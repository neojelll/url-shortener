import asyncio
from .bot import main

def run() -> None:
	asyncio.run(main())

if __name__ == '__main__':
	run()
