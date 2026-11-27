"""Construye registros de plan con un esquema serializable a JSON."""


class MonthlyPlanService:
    def __init__(self, movie_repository, classifier):
        self.movie_repository = movie_repository
        self.classifier = classifier

    def build(self) -> list[dict]:
        plan = []
        for movie in self.movie_repository.all_movies():
            assignment = self.classifier.classify(movie["title"], movie["genres"])
            plan.append({
                "id": movie["canonical_movie_id"],
                "title": movie["title"],
                "weighted_score": movie["weighted_score"],
                "genres": movie["genres"],
                "category": assignment["category"],
                "month_number": assignment["month_number"],
                "month": assignment["month"],
                "duration_minutes": movie["duration_minutes"],
                "in_watchlist": movie["in_watchlist"],
                "watchlist_sources": movie["watchlist_sources"],
                "is_watched": movie["is_watched"],
            })
        return plan
