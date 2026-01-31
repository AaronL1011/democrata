from pathlib import Path

import aiofiles
import aiofiles.os


class LocalBlobStore:
    def __init__(self, base_path: str = "./data/blobs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)

        return key

    async def get(self, key: str) -> bytes:
        file_path = self.base_path / key
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        file_path = self.base_path / key
        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)

    async def exists(self, key: str) -> bool:
        file_path = self.base_path / key
        return await aiofiles.os.path.exists(file_path)
