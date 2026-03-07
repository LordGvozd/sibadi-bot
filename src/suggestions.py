import asyncio
from collections.abc import Sequence

import rapidfuzz


def get_suggestions_sync(
    target: str, collection: Sequence[str], limit: int = 5
) -> list[str]:
    results = rapidfuzz.process.extract(
        target, collection, scorer=rapidfuzz.fuzz.WRatio, limit=limit
    )
    return [result[0] for result in results]


async def get_suggestions_async(
    target: str, collection: Sequence[str], limit: int = 5
) -> list[str]:
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(
        None, get_suggestions_sync, target, collection, limit
    )
