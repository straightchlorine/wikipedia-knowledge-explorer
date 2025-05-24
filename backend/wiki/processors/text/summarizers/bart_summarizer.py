from transformers import pipeline
from wiki.processors.text.summarizers.summarizer import TextSummarizer


class BartSummarizer(TextSummarizer):
    """Summarizer using a pretrained transformer model."""

    def __init__(self):
        # Inicjalizacja pipeline'u do podsumowania z wykorzystaniem modelu BART
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn"
        )

    def summarize(self, texts: str) -> str:
        """Generate summary using transformer model"""
        # Obcięcie jeśli tekst jest zbyt długi
        max_input_length = 1024  # limit BART
        input_text = texts.strip()[:max_input_length]

        # Wygeneruj streszczenie
        result = self.summarizer(
            input_text,
            max_length=130,
            min_length=30,
            do_sample=False
        )
        return result[0]['summary_text']
