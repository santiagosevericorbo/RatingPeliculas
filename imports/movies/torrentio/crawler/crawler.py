import asyncio
import aiohttp
from tqdm import tqdm
import time


class TorrentioCrawler:

    def __init__(
        self,
        client,
        service,
        repository,
        workers=4,
        save_every=100,
        save_interval=30,
    ):
        self.client = client
        self.service = service
        self.repository = repository

        self.workers = workers
        self.save_every = save_every
        self.save_interval = save_interval

        self.queue = asyncio.Queue()
        self.progress_queue = asyncio.Queue()

        self.buffer = []

        self.last_save = None

        # control global simple (extra seguridad)
        self.semaphore = asyncio.Semaphore(3)

    # -----------------------------
    # WORKER
    # -----------------------------
    async def worker(self, session):

        while True:

            movie = await self.queue.get()

            imdb_id = movie["imdb_id"]
            canonical_id = movie["canonical_movie_id"]

            try:
                async with self.semaphore:
                    data = await self.client.fetch_streams(session, imdb_id)

                if not data:
                    await self.progress_queue.put(1)
                    continue

                result = self.service.extract_best_torrent(imdb_id, data)

                if result:
                    self.buffer.append(
                        (
                            canonical_id,
                            imdb_id,
                            result["best_seeders"],
                            result["quality"],
                        )
                    )

                # flush seguro por tamaño o tiempo
                now = time.time()

                if self.last_save is None:
                    self.last_save = now

                if (
                    len(self.buffer) >= self.save_every
                    or (now - self.last_save) >= self.save_interval
                ):
                    self.repository.save(self.buffer)
                    self.buffer.clear()
                    self.last_save = now

                await self.progress_queue.put(1)

            except Exception as e:
                print(f"[WORKER ERROR] {imdb_id} | {e}")
                await self.progress_queue.put(1)

            finally:
                self.queue.task_done()

    # -----------------------------
    # PROGRESS
    # -----------------------------
    async def progress_worker(self, total):

        with tqdm(total=total, desc="Fetching Torrent Availability") as pbar:

            completed = 0

            while completed < total:
                await self.progress_queue.get()
                completed += 1
                pbar.update(1)

    # -----------------------------
    # RUN
    # -----------------------------
    async def run(self, movies):

        total = len(movies)

        for m in movies:
            await self.queue.put(m)

        async with aiohttp.ClientSession() as session:

            workers = [
                asyncio.create_task(self.worker(session)) for _ in range(self.workers)
            ]

            progress_task = asyncio.create_task(self.progress_worker(total))

            await self.queue.join()

            # flush final obligatorio
            if self.buffer:
                self.repository.save(self.buffer)
                self.buffer.clear()

            for w in workers:
                w.cancel()

            await asyncio.gather(*workers, return_exceptions=True)

            await progress_task
