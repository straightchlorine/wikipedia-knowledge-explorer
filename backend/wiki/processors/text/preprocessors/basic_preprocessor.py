import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from wiki.processors.text.preprocessors.preprocessor import TextPreprocessor
from wiki.processors.text.summarizers.bart_summarizer import BartSummarizer


class BasicPreprocessor(TextPreprocessor):
    """Basic text preprocessing with NLTK."""

    def __init__(self):
        nltk.download("punkt_tab", quiet=True)
        nltk.download("stopwords", quiet=True)
        nltk.download("wordnet", quiet=True)
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

        # pass an object to act as an summariser
        self.summarizer = BartSummarizer()

    def preprocess(self, texts: list[str]) -> list[str]:
        """Preprocess texts using basic NLP techniques."""
        processed_texts = []

        for text in texts:
            # remove text and symbols not useful for clustering:
            # - HTML tags
            # - citations and references
            # - special characters
            # - digits
            # - whitespaces
            text = re.sub(r"<.*?>", "", text)
            text = re.sub(r"\[\d+\]", "", text)
            text = re.sub(r"[^\w\s]", " ", text)
            text = re.sub(r"\d+", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            text = text.lower()

            # break down into tokens and lemmatize
            tokens = word_tokenize(text)
            lemmatized = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words
            ]
            processed_text = " ".join(lemmatized)

            if self.summarizer:
                processed_text = self.summarizer.summarize(processed_text)

            processed_texts.append(processed_text)

        return processed_texts
