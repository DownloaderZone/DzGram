"""Run in an environment containing either DzGram or WzGram.

Credentials: DZGRAM_API_ID, DZGRAM_API_HASH, DZGRAM_BOT_TOKEN.
Example: python benchmark_transfer.py --chat -1001234567890 --message 42
Upload-only: python benchmark_transfer.py --upload /path/to/file
"""
import argparse
import asyncio
import importlib.metadata
import json
import logging
import os
import tempfile
import time
from pathlib import Path

from pyrogram import Client, __version__


async def measure(label, operation):
    start = time.monotonic()
    first = None
    completed = 0
    first_bytes = 0

    def progress(current, total):
        nonlocal first, completed, first_bytes
        completed = current
        if current > 0 and first is None:
            first = time.monotonic()
            first_bytes = current

    result = await operation(progress)
    end = time.monotonic()
    if result is None:
        raise RuntimeError(f"{label} failed; see logs")
    duration = end - start
    steady_time = end - first if first is not None else 0
    print(json.dumps({
        "operation": label,
        "bytes": completed,
        "first_progress_seconds": round(first - start, 3) if first is not None else None,
        "total_seconds": round(duration, 3),
        "average_MiB_s": round(completed / duration / 1048576, 3),
        "after_first_progress_MiB_s": round((completed - first_bytes) / steady_time / 1048576, 3) if steady_time else None,
    }), flush=True)


async def main(args):
    if not args.upload and (args.chat is None or args.message is None):
        raise ValueError("Provide --upload, or both --chat and --message")
    versions = {"pyrogram": __version__}
    for package in ("dzgram", "wzgram", "warpcrypto"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    print(json.dumps({"versions": versions}), flush=True)
    with tempfile.TemporaryDirectory(prefix="transfer_bench_") as workdir:
        async with Client(
            "benchmark", api_id=int(os.environ["DZGRAM_API_ID"]),
            api_hash=os.environ["DZGRAM_API_HASH"],
            bot_token=os.environ["DZGRAM_BOT_TOKEN"],
            in_memory=True, no_updates=True,
        ) as client:
            print(json.dumps({"bot": client.me.is_bot, "dc": await client.storage.dc_id()}), flush=True)
            if args.chat is not None and args.message is not None:
                chat = int(args.chat) if args.chat.lstrip("-").isdigit() else args.chat
                message = await client.get_messages(chat, args.message)
                for run in range(args.runs):
                    destination = str(Path(workdir) / f"download_{run}.bin")
                    await measure(f"download_{run + 1}", lambda progress: client.download_media(
                        message, file_name=destination, progress=progress
                    ))
                    Path(destination).unlink()
            if args.upload:
                for run in range(args.runs):
                    await measure(f"upload_{run + 1}", lambda progress: client.save_file(
                        args.upload, progress=progress
                    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chat")
    parser.add_argument("--message", type=int)
    parser.add_argument("--upload", help="Upload parts only; does not post a message")
    parser.add_argument("--runs", type=int, default=2, help="Compare cold and warm transfers")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(args))
