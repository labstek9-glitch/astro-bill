from __future__ import annotations

import argparse
import asyncio
import signal

from astrobill.config import Settings
from astrobill.display import console, render
from astrobill.engine import Engine, persist


async def run(settings: Settings, once: bool) -> None:
    engine = Engine(settings)
    stop = asyncio.Event()

    def _stop(*_args: object) -> None:
        stop.set()

    try:
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)
    except ValueError:
        pass

    try:
        series = await engine.resolve_series()
        console.print(f"watching {len(series)} series: {', '.join(series)}")
        cycle = 0
        while not stop.is_set():
            cycle += 1
            try:
                rows = await engine.scan_once()
                persist(rows, settings)
                render(rows, cycle)
            except Exception as exc:
                console.print(f"[red]scan error:[/red] {exc}")
            if once:
                break
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.poll_seconds)
            except TimeoutError:
                continue
    finally:
        await engine.close()


def main() -> None:
    p = argparse.ArgumentParser(prog="astrobill", description="Astro Bill Kalshi 15m scanner")
    p.add_argument("--config", default=None)
    p.add_argument("--once", action="store_true", help="single scan then exit")
    p.add_argument("--poll", type=float, default=None, help="override poll seconds")
    args = p.parse_args()
    settings = Settings.load(args.config)
    if args.poll:
        settings.poll_seconds = args.poll
    asyncio.run(run(settings, once=args.once))


if __name__ == "__main__":
    main()
