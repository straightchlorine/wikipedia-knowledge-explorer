import re
from wiki.processors.text.summarizers.summarizer import TextSummarizer

class BasicSummarizer(TextSummarizer):
    """Summarizer that returns top 3 longest sentences."""

    def summarize(self, texts: str) -> str:
        sentences = re.split(r'(?<=[.!?]) +', texts.strip())
        top_sentences = sorted(sentences, key=len, reverse=True)[:3]
        return ' '.join(top_sentences)
