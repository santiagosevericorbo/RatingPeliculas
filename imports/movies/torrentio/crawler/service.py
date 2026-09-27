import re


class TorrentioService:

    def extract_best_torrent(self, imdb_id, data):
        streams = data.get("streams", [])
        best = None
        max_seeders = -1

        for s in streams:
            title = s.get("title", "")

            match = re.search(r"👤\s*(\d+)", title)
            if not match:
                continue

            seeders = int(match.group(1))

            if seeders < 50:  # ← skip directo
                continue

            if seeders > max_seeders:
                max_seeders = seeders
                best = {
                    "best_seeders": seeders,
                    "quality": title.split("\n")[0] if title else "unknown",
                }

        return best
