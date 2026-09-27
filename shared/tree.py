from pathlib import Path


def mostrar_estructura(ruta=".", prefijo=""):
    ruta = Path(ruta)

    elementos = sorted(ruta.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

    for i, elemento in enumerate(elementos):
        ultimo = i == len(elementos) - 1

        conector = "└── " if ultimo else "├── "
        print(prefijo + conector + elemento.name)

        if elemento.is_dir():
            extension = "    " if ultimo else "│   "
            mostrar_estructura(elemento, prefijo + extension)


# Carpeta actual
raiz = Path.cwd()

print(raiz)
mostrar_estructura(raiz)
