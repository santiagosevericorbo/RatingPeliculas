from pathlib import Path
import subprocess
import sys
from datetime import datetime
import sys

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from utils.config import STEPS

# carpeta donde vive pipeline.py
BASE_DIR = Path(__file__).resolve().parent


def run_step(name, script_path):

    print(f"\n[{datetime.now()}] RUNNING STEP: {name}")
    print(f"Script → {script_path}")

    if not script_path.exists():
        print(f"ERROR: Script not found {script_path}")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, str(script_path)], cwd=BASE_DIR  # MUY IMPORTANTE
    )

    if result.returncode != 0:
        print(f"ERROR in {name}")
        sys.exit(1)

    print(f"[OK] {name}")


def main():

    # ejecutar solo un paso
    if len(sys.argv) > 1:
        step_name = sys.argv[1]

        for name, script in STEPS:
            if name == step_name:
                run_step(name, script)
                return

        print("Step not found")
        sys.exit(1)

    # pipeline completo
    for name, script in STEPS:
        run_step(name, script)

    print("\nPIPELINE COMPLETED")


if __name__ == "__main__":
    main()
