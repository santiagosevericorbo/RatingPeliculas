from pathlib import Path
import time


class SQLRunner:

    def __init__(self, con):
        self.con = con

    def run(self, sql_file: Path):

        print(f"▶ {sql_file.name}")

        sql = sql_file.read_text(encoding="utf8")

        t0 = time.time()

        self.con.execute(sql)

        print(f"   ✔ {time.time()-t0:.1f}s")
