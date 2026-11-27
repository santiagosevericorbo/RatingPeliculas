"""Clasificación por reglas JSON y excepciones manuales JSON."""


class CategoryClassifier:
    def __init__(self, months: list[dict], rules: dict):
        self.month_by_number = {int(month["number"]): month for month in months}
        self.genre_rules = rules["genre_to_month"]
        self.overrides = {self._key(row["title"]): row for row in rules.get("overrides", [])}
        self.default = rules.get("default", {"number": None, "category": "Sin categoría"})

    @staticmethod
    def _key(title: str) -> str:
        return " ".join(str(title).casefold().split())

    def classify(self, title: str, genres: str | None) -> dict:
        override = self.overrides.get(self._key(title))
        if override:
            return self._result(int(override["month_number"]), override.get("category"))
        movie_genres = {genre.strip() for genre in str(genres or "").split(",")}
        # El orden del JSON permite decidir cuál tema gana si hay varios géneros.
        for genre, month_number in self.genre_rules.items():
            if genre in movie_genres:
                return self._result(int(month_number))
        return {"month_number": None, "month": None, "category": self.default["category"]}

    def _result(self, number: int, category: str | None = None) -> dict:
        month = self.month_by_number[number]
        return {"month_number": number, "month": month["name"],
                "category": category or month["theme"]}
