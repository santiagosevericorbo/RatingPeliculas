from pathlib import Path
import subprocess
import sys
import time


class PythonRunner:

    def __init__(self, root: Path):
        self.root = root

    def run(self, script: str):

        module = Path(script).with_suffix("").as_posix().replace("/", ".")

        print(f"\n▶ Ejecutando {module}")

        t0 = time.time()

        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=self.root,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Falló {module}")

        print(f"   ✔ {time.time()-t0:.1f}s")
