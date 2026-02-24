from transformers import pipeline

summarizer = pipeline("summarization", model="t5-small")

def simplify_text(text):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    simplified = ""
    for chunk in chunks:
        summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        simplified += summary[0]['summary_text'] + "\n"
    return simplified