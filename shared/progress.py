# shared/progress.py
from tqdm import tqdm


def make_progress(iterable, desc: str, total: int = None):
    return tqdm(
        iterable,
        desc=f"  → {desc}",
        total=total,
        unit=" items",
        colour="cyan",
        dynamic_ncols=True,
    )
