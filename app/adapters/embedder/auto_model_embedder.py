import torch
from loguru import logger

from app.core.ports.embedder import EmbedderPort


class AutoModelEmbedder(EmbedderPort):
    """Embedder backed by HuggingFace ``transformers.AutoModel`` and ``AutoTokenizer``.

    Uses mean-pooling over the last hidden state to produce a fixed-size
    embedding vector for any encoder model available on the HuggingFace Hub.
    """

    def __init__(self, model_name: str) -> None:
        logger.info(f"Loading AutoModel embedder: {model_name}")
        from transformers import AutoModel, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModel.from_pretrained(model_name)
        self._model.eval()
        logger.success(f"AutoModel '{model_name}' loaded")

    def embed(self, text: str) -> list[float]:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        with torch.no_grad():
            outputs = self._model(**inputs)
        # Mean-pool the token embeddings (ignore padding via attention mask)
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state  # (1, seq_len, hidden)
        mask_expanded = attention_mask.unsqueeze(-1).float()
        sum_embeddings = (token_embeddings * mask_expanded).sum(dim=1)
        sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
        embedding = (sum_embeddings / sum_mask).squeeze(0)
        return embedding.tolist()
