from transformers import pipeline
from wiki.processors.text.summarizers.summarizer import TextSummarizer


class BartSummarizer(TextSummarizer):
    """Summarizer using a pretrained transformer model."""

    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn"
        )

    def summarize(self, texts: str, max_length: int = 130, min_length: int = 30) -> str:
        """Generate summary using transformer model with optional length control."""
        input_text = texts.strip()

        if not input_text:
            return ""

        max_input_length = 1024
        input_text = input_text[:max_input_length]

        result = self.summarizer(
            input_text,
            max_length=max_length,
            min_length=min(min_length, max_length - 1),
            do_sample=False
        )

        summary = result[0]['summary_text'].strip().capitalize()
        return summary
