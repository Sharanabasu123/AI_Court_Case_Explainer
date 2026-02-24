from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import docx
import pdfplumber
import re
import io

# ---------------------------------------------------------
# Flask setup
# ---------------------------------------------------------
app = Flask(
    __name__,
    template_folder='../Frontend/templates',
    static_folder='../Frontend/static'
)

# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
legal_glossary = {
    "plaintiff": "The person or party who brings a case against another in a court of law.",
    "defendant": "The person or party against whom a lawsuit is filed.",
    "affidavit": "A written statement confirmed by oath or affirmation, used as evidence in court.",
    "injunction": "A court order requiring a person to do or cease doing a specific action.",
    "jurisdiction": "The authority given to a legal body to administer justice within a defined field of responsibility.",
    "summons": "An official notice to a person that a lawsuit has been filed against them.",
    "bail": "Temporary release of an accused person awaiting trial, sometimes on monetary conditions.",
    "deposition": "The process of giving sworn evidence outside of court.",
    "subpoena": "A legal document ordering someone to attend court or produce documents.",
    "verdict": "The formal decision or finding made by a jury or judge in a court case.",
    "appeal": "A request made to a higher court to review the decision of a lower court.",
    "prosecution": "The legal party responsible for presenting the case against an individual in a criminal trial.",
    "acquittal": "A legal judgment that officially and formally clears a defendant of criminal charges.",
    "testimony": "A formal written or spoken statement given in a court of law.",
    "litigation": "The process of taking legal action; the process of suing someone or being sued."
}

court_updates = [
    "Judge entered the courtroom.",
    "Hearing started at 10:00 AM.",
    "Plaintiff presented opening statement.",
    "Defendant's lawyer requested a recess."
]

# ---- Pre-planned summaries for laws / cases ----
preplanned_summaries = {
    "right to equality": (
        "📌 Right to Equality (Articles 14–18): "
        "Ensures every person is equal before the law and entitled to equal protection. "
        "It forbids discrimination based on religion, race, caste, sex, or birthplace, "
        "and abolishes untouchability and titles."
    ),
    "freedom of speech": (
        "📌 Freedom of Speech & Expression (Article 19(1)(a)): "
        "Allows citizens to express opinions freely, with reasonable limits for public order, "
        "defamation, and security of the state."
    ),
    "habeas corpus": (
        "📌 Habeas Corpus: "
        "A writ protecting personal liberty. Courts can order authorities to present "
        "a detained person and justify the detention."
    ),
    "ipc section 302": (
        "🔍 IPC Section 302 – Punishment for Murder:\n"
        "Whoever commits murder shall be punished with death or life imprisonment, and may also be fined. "
        "This is a non-bailable, cognizable offence triable by the Court of Session. "
        "To prove murder under this section, intent (mens rea) and causation must be established."
    ),
    "ipc section 376": (
        "🔍 IPC Section 376 – Punishment for Rape:\n"
        "Prescribes rigorous imprisonment of not less than 10 years, which may extend to life, and a fine. "
        "Aggravated cases (custodial rape, gang rape, rape of minors) attract stricter penalties. "
        "This section ensures justice for victims and reflects evolving legal reforms post-Nirbhaya case."
    ),
    "ipc section 420": (
        "🔍 IPC Section 420 – Cheating and Dishonest Inducement:\n"
        "Deals with cheating and dishonestly inducing delivery of property. "
        "Punishment includes up to 7 years imprisonment and fine. "
        "Requires proof of fraudulent intent at the time of inducement."
    ),
    "ipc section 498a": (
        "🔍 IPC Section 498A – Cruelty by Husband or Relatives:\n"
        "Protects married women from cruelty by husband or his relatives. "
        "Cruelty includes physical or mental harm, harassment for dowry, or threats. "
        "Punishable with imprisonment up to 3 years and fine. It is a cognizable, non-bailable offence."
    )
}

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def extract_text(file):
    """Read text from txt / docx / pdf files."""
    filename = secure_filename(file.filename)
    if filename.endswith('.txt'):
        return file.read().decode('utf-8', errors='ignore')
    elif filename.endswith('.docx'):
        file.seek(0)
        doc = docx.Document(io.BytesIO(file.read()))
        return '\n'.join([p.text for p in doc.paragraphs])
    elif filename.endswith('.pdf'):
        file.seek(0)
        text = ''
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    return "Unsupported file type."


def simple_simplify(text):
    """Return first few sentences from text."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return ' '.join(sentences[:3]) if sentences else text


def ai_summarize_chat(user_text):
    """Return pre-planned summary if known, else simple summary."""
    if not user_text.strip():
        return "Please enter a legal topic or question."

    lower = user_text.lower()
    for key, summary in preplanned_summaries.items():
        if key in lower:
            return summary

    return f"AI Summary: {simple_simplify(user_text)}"

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/glossary', methods=['GET', 'POST'])
def glossary():
    glossary_term = glossary_def = None
    if request.method == 'POST':
        legal_term = request.form.get('legal_term', '').strip().lower()
        if legal_term:
            glossary_term = legal_term
            glossary_def = legal_glossary.get(legal_term)
    return render_template(
        'glossary.html',
        glossary_term=glossary_term,
        glossary_def=glossary_def
    )


@app.route('/document', methods=['GET', 'POST'])
def document():
    result = {}
    if request.method == 'POST':
        raw_text = ""
        file = request.files.get('document')
        if file and file.filename:
            raw_text = extract_text(file)
        else:
            raw_text = request.form.get('plain_text', '').strip()

        if raw_text:
            result = {
                "original": raw_text,
                "simplified": simple_simplify(raw_text)
            }
    return render_template('document.html', result=result)


@app.route('/live')
def live():
    return render_template('live.html')


@app.route('/court_updates')
def get_court_updates():
    return jsonify(court_updates)


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    chat_response = None
    if request.method == 'POST':
        query = request.form.get('chat_input', '').strip()
        if query:
            chat_response = ai_summarize_chat(query)
    return render_template('chatbot.html', chat_response=chat_response)


@app.route('/nextpage')
def nextpage():
    return render_template('nextpage.html')


if __name__ == '__main__':
    app.run(debug=True)