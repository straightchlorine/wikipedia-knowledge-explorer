import re
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from wiki.processors.text.summarizers.summarizer import TextSummarizer


class TFIDFSummarizer(TextSummarizer):
    """Summarizer based on TF-IDF scoring of sentences."""

    def summarize(self, texts: str, ratio: float = 0.3) -> str:
        input_text = texts.strip()

        if not input_text:
            return ""

        # Podział na zdania
        sentences = re.split(r'(?<=[.!?]) +', input_text)
        if not sentences:
            return ""

        # Liczba zdań do zwrócenia
        num_sentences = max(1, math.ceil(len(sentences) * ratio))

        # TF-IDF scoring
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(sentences)
        scores = X.sum(axis=1).A1  # Zamień na jednowymiarowy array

        # Posortuj zdania według sumy TF-IDF
        ranked_sentences = [sentence for _, sentence in sorted(
            zip(scores, sentences), key=lambda x: -x[0]
        )]

        # Zwróć top N
        return ' '.join(ranked_sentences[:num_sentences])
