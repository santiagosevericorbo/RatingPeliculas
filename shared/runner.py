# shared/runner.py
import sys


class Runner:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is KeyboardInterrupt:
            print("\n\n  Proceso interrumpido por el usuario.")
            sys.exit(0)
        return False
