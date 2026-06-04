import asyncio
from functools import partial, lru_cache
from typing import Union

import numpy as np
from sentence_transformers import SentenceTransformer

from src.service.model_manager_service import model_manager as model_manager_service, ModelManager


class EmbeddingModelService:

    def __init__(self,
                 model_name : str = "BAAI/bge-m3",
                 device : str = "cpu",
                 model_manager : ModelManager = model_manager_service,
                 ):

        self.model_name = model_name
        self.model_manager = model_manager
        self.model = self.model_manager.get_bge_model()
        if self.model:
            self.embedding_dim = self.model.get_embedding_dimension()

        else:
            self.embedding_dim = 1024
        # self.model = SentenceTransformer(
        #     self.model_name,
        #     device = device,
        #     model_kwargs = {
        #         "torch_dtype": "float32",
        #         "use_memory_efficient_attention": True
        #         },
        # )



    def encode(self,
               texts : Union[str, list[str]],
               normalize : bool = True,
               batch_size : int = 8,
               ) -> np.ndarray:

        single_input : bool
        if isinstance(texts, str):
            texts = [texts]
            single_input = True

        else:
            single_input = False

        embeddings = self.model.encode(
            texts,
            batch_size = batch_size,
            normalize_embeddings = normalize,
            show_progress_bar = False,
            convert_to_numpy = True,
            )

        if single_input:
            return embeddings[0]

        return embeddings

    async def encode_async(
            self,
            texts: Union[str, list[str]],
            normalize: bool = True,
            batch_size: int = 8
            ) -> np.ndarray:

        loop = asyncio.get_event_loop()

        func = partial(self.encode, texts, normalize = normalize, batch_size = batch_size)
        return await loop.run_in_executor(None, func)

    def get_embedding_dim(self) -> int | None:
        return self.embedding_dim


@lru_cache()
def get_embedding_model() -> EmbeddingModelService:
    """Фабрика для получения единственного экземпляра модели"""
    return EmbeddingModelService()



embedding_service = get_embedding_model()




