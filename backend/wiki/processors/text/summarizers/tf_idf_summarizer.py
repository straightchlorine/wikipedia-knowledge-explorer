import re
from sklearn.feature_extraction.text import TfidfVectorizer
from wiki.processors.text.summarizers.summarizer import TextSummarizer

class BasicSummarizer(TextSummarizer):
    """Summarizer based on TF-IDF scoring of sentences."""

    def summarize(self, texts: str) -> str:
        sentences = re.split(r'(?<=[.!?]) +', texts.strip())
        if not sentences:
            return texts

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(sentences)
        scores = X.sum(axis=1)
        ranked_sentences = sorted(zip(scores, sentences), key=lambda x: -x[0])
        top_n = [sent for _, sent in ranked_sentences[:3]]
        return ' '.join(top_n)
