from imports.movies.lb.lb_resolver import process_csv
from imports.movies.lb.configs import DATASETS

for dataset in DATASETS:
    process_csv(
        dataset["input"],
        dataset["output"],
        dataset["uri_column"],
    )
