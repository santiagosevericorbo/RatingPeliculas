from utils.config import SQL_DIR


def load_sql(name):
    return (SQL_DIR / name).read_text()
