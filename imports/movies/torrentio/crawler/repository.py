from utils.sql_loader import load_sql


class TorrentRepository:

    def __init__(self, conn):
        self.conn = conn
        self.insert_query = load_sql("insert_torrent_availability.sql")

    def save(self, rows):

        self.conn.executemany(self.insert_query, rows)
