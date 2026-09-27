from pathlib import Path
from typing import Iterable


class FolderRunner:
    """
    Descubre automáticamente todos los .sql de una carpeta.

    Ejemplo:

        scripts/
            1_load/
                movies/
                    imdb.sql
                    tmdb.sql
            2_clean/
                movies/
                    ...

    devuelve

        1_load/movies/imdb.sql
        1_load/movies/tmdb.sql
        2_clean/movies/...
    """

    def __init__(self, scripts_root: Path):
        self.scripts_root = scripts_root

    def folders(self) -> list[Path]:
        """
        Devuelve únicamente las carpetas de primer nivel
        ordenadas alfabéticamente.

        1_load
        2_clean
        2.5_map
        ...
        99_exports
        """

        return sorted(
            [p for p in self.scripts_root.iterdir() if p.is_dir()],
            key=lambda p: p.name,
        )

    def sql_files(self, folder: Path) -> Iterable[Path]:
        """
        Busca todos los SQL de manera recursiva.

        scripts/
            1_load/
                movies/
                books/

        devuelve ambos.
        """

        return sorted(
            folder.rglob("*.sql"),
            key=lambda p: str(p.relative_to(folder)),
        )

    def pipeline(self):

        for folder in self.folders():

            yield folder, list(self.sql_files(folder))

    def sql_files_from(self, relative_folder: str):

        folder = self.scripts_root / relative_folder

        if not folder.exists():
            raise FileNotFoundError(folder)

        return sorted(
            folder.rglob("*.sql"),
            key=lambda p: str(p.relative_to(folder)),
        )
