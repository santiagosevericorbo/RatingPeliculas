"""Arma el análisis de vistas con categoría y director, cuando está disponible."""


class LetterboxdHistoryService:
    def __init__(self, history_repository, director_repository, classifier):
        self.history_repository = history_repository
        self.director_repository = director_repository
        self.classifier = classifier

    @property
    def director_data_available(self):
        return self.director_repository.available

    def build(self) -> list[dict]:
        movies = self.history_repository.watched_movies()
        directors = self.director_repository.for_imdb_ids(
            [movie["imdb_id"] for movie in movies if movie["imdb_id"]]
        )
        result = []
        for movie in movies:
            assignment = self.classifier.classify(movie["title"], movie["genres"])
            result.append({
                "id": movie["id"],
                "title": movie["title"],
                "year": movie["year"],
                "genres": movie["genres"],
                "category": assignment["category"],
                "month_number": assignment["month_number"],
                "month": assignment["month"],
                "weighted_score": movie["weighted_score"],
                "personal_rating": movie["personal_rating"],
                "directors": directors.get(movie["imdb_id"], []),
            })
        return result
