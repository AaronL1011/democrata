from openai import AsyncOpenAI


class OpenAIEmbedder:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "text-embedding-3-small",
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def embed_single(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0] if embeddings else []
