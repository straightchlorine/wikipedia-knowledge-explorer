import re

from wiki.processors.text.preprocessors.preprocessor import TextPreprocessor


class BasicPreprocessor(TextPreprocessor):
    """Light text preprocessing for embedding-based clustering.

    SentenceTransformer works best on natural text, so this preprocessor
    only removes noise (HTML, citations, excess whitespace) without
    lemmatization or stopword removal.
    """

    def preprocess(self, texts: list[str]) -> list[str]:
        """Preprocess texts with light cleaning."""
        processed_texts = []

        for text in texts:
            text = re.sub(r"<.*?>", "", text)
            text = re.sub(r"\[\d+\]", "", text)
            text = re.sub(r"\s+", " ", text).strip()

            processed_texts.append(text)

        return processed_texts
