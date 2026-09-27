import asyncio
import aiohttp
from tqdm import tqdm


class ProviderCrawler:

    def __init__(
        self,
        client,
        repository,
        service,
        workers=40,
        save_every=1000,
    ):
        self.client = client
        self.repository = repository
        self.service = service

        self.workers = workers
        self.save_every = save_every

        self.queue = asyncio.Queue()
        self.buffer = []

        # evita race conditions
        self.buffer_lock = asyncio.Lock()
        self.progress_lock = asyncio.Lock()

    # --------------------------------------------------
    # WORKER
    # --------------------------------------------------
    async def worker(self, session, progress):

        while True:

            tmdb_id = await self.queue.get()

            try:
                data = await self.client.fetch_watch_providers(
                    session,
                    tmdb_id,
                )

                if data:
                    providers = self.service.parse_uy_providers(
                        tmdb_id,
                        data,
                    )

                    # ---- BUFFER SAFE ----
                    async with self.buffer_lock:

                        self.buffer.extend(providers)

                        if len(self.buffer) >= self.save_every:
                            self.repository.save(self.buffer)
                            self.buffer.clear()

                # ---- PROGRESS SAFE ----
                async with self.progress_lock:
                    progress.update(1)

            finally:
                self.queue.task_done()

    # --------------------------------------------------
    # RUN
    # --------------------------------------------------
    async def run(self, movie_ids):

        # cargar queue
        for m in movie_ids:
            await self.queue.put(m)

        progress = tqdm(
            total=len(movie_ids),
            desc="Fetching UY providers",
        )

        async with aiohttp.ClientSession() as session:

            workers = [
                asyncio.create_task(self.worker(session, progress))
                for _ in range(self.workers)
            ]

            await self.queue.join()

            # cancelar workers
            for w in workers:
                w.cancel()

            await asyncio.gather(*workers, return_exceptions=True)

        progress.close()

        # guardado final
        if self.buffer:
            self.repository.save(self.buffer)
            self.buffer.clear()
