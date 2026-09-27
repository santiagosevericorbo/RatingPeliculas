import pandas as pd
import os


class ProviderRepository:

    def __init__(self, path):
        self.path = path

    def load_existing_ids(self):

        if not os.path.exists(self.path):
            return set()

        df = pd.read_parquet(self.path)
        return set(df["tmdb_id"].unique())

    def save(self, providers):

        df = pd.DataFrame([p.__dict__ for p in providers])

        if os.path.exists(self.path):
            existing = pd.read_parquet(self.path)
            df = pd.concat([existing, df], ignore_index=True)

        df.to_parquet(self.path, index=False)
