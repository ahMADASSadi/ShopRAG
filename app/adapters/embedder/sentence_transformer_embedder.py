from typing import List

from loguru import logger

from app.core.ports.embedder import EmbedderPort


class SentenceTransformerEmbedder(EmbedderPort):
    def __init__(self, model_name: str) -> None:
        logger.info(f"Loading embedding model: {model_name}")
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        logger.success(f"Embedding model '{model_name}' loaded")

    def embed(self, text: str) -> List[float]:
        return self._model.encode(text).tolist()
