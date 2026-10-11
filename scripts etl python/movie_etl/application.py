"""Casos de uso de aplicación, ensamblados por la capa CLI/notebook."""
from .category_classifier import CategoryClassifier
from .database import DuckDBConnectionFactory
from .director_repository import DirectorRepository
from .json_plan_writer import JsonPlanWriter
from .letterboxd_history_repository import LetterboxdHistoryRepository
from .letterboxd_history_service import LetterboxdHistoryService
from .movie_repository import MovieRepository
from .monthly_plan_service import MonthlyPlanService
from .pipeline import SqlPipelineRunner
from .settings import Settings


class MovieEtlApplication:
    def __init__(self, settings: Settings):
        self.settings = settings
        db = settings.project_path(settings.config["database"])
        connections = DuckDBConnectionFactory(db)
        self.pipeline = SqlPipelineRunner(settings, connections)
        classifier = CategoryClassifier(settings.months, settings.category_rules)
        repository = MovieRepository(connections)
        self.plan_service = MonthlyPlanService(repository, classifier)
        lb_root = settings.project_path(settings.config["letterboxd_user_data_directory"])
        user_folders = sorted(lb_root.glob("user-*"))
        ratings_path = (user_folders[-1] / "ratings.csv") if user_folders else (lb_root / "ratings.csv")
        history_repository = LetterboxdHistoryRepository(connections, ratings_path)
        director_repository = DirectorRepository(
            connections,
            settings.project_path(settings.config["imdb_crew_path"]),
            settings.project_path(settings.config["imdb_names_path"]),
        )
        self.history_service = LetterboxdHistoryService(history_repository, director_repository, classifier)
        self.plan_writer = JsonPlanWriter()

    def run_pipeline(self, steps: list[int] | None = None):
        self.pipeline.run(steps)

    def build_plan(self) -> list[dict]:
        return self.plan_service.build()

    def build_history(self) -> list[dict]:
        return self.history_service.build()

    @property
    def director_data_available(self) -> bool:
        return self.history_service.director_data_available

    def publish_plan(self, plan: list[dict] | None = None) -> list[dict]:
        result = plan if plan is not None else self.build_plan()
        output = self.settings.project_path(self.settings.config["plan_json"])
        self.plan_writer.write(result, output)
        return result

    def publish_history(self, history: list[dict] | None = None) -> list[dict]:
        result = history if history is not None else self.build_history()
        output = self.settings.project_path(self.settings.config["history_json"])
        self.plan_writer.write({
            "director_data_available": self.director_data_available,
            "movies": result,
        }, output)
        return result
