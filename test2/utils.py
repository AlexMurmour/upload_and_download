import aiofiles
from aiohttp.multipart import BodyPartReader


async def upload_file(field: BodyPartReader, path: str) -> int:
    size = 0
    async with aiofiles.open(path, mode='w+b') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            await f.write(chunk)
    return size


async def download_file(path_from: str, path_to: str) -> None:
    async with aiofiles.open(path_from, mode="r+b") as f:
        async with aiofiles.open(path_to, 'wb') as dl:
            index_contents = await f.read()
            await dl.write(index_contents)
