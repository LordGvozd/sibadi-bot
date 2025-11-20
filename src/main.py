import asyncio

from src.telegram.bot import run_bot


if __name__ == "__main__":
    print("Called main")
    asyncio.run(run_bot())
