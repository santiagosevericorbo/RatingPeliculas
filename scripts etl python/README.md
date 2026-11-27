# ETL de películas y tablero React

La solución separa el runner en componentes Python, guarda rutas, etapas, temas y reglas en JSON y publica los datos de películas y actividad personal como JSON. El tablero React carga esos JSON al abrirse: el HTML solo monta la aplicación.

## Estructura

- `movie_etl/`: aplicación y módulos separados para configuración, conexión DuckDB, ejecución SQL, consultas, clasificación, armado del plan y exportación JSON.
- `config/etl.json`: base, fuentes, destino del JSON y secuencia de etapas 0–9.
- `movie_dashboard/public/data/months.json`: plan temático mensual.
- `movie_dashboard/public/data/category_rules.json`: reglas automáticas por género y excepciones manuales por película.
- `movie_dashboard/public/data/monthly_movie_plan.json`: películas con indicadores de vistas y watchlist.
- `movie_dashboard/public/data/letterboxd_history.json`: vistas, calificación Letterboxd y puntaje ponderado.
- `movie_dashboard/src/`: página, hook de carga JSON, componentes React y hojas CSS por componente.
- `movie_etl_jupyter.ipynb`: ejecución/consulta en Jupyter y gráfico Plotly para análisis.

## Preparar y ejecutar el ETL

Desde la raíz del repositorio:

```powershell
python -m pip install -r "scripts etl python/requirements.txt"
cd "scripts etl python"
python -m movie_etl.cli
```

El plan y el historial se escriben en `movie_dashboard/public/data/`. Para generar los JSON con las tablas DuckDB existentes, omití el pipeline:

```powershell
python -m movie_etl.cli --skip-etl
```

Se pueden seleccionar etapas, por ejemplo `--steps 8 9`. El runner ejecuta el SQL existente; la conversión de Letterboxd de la etapa 0 se hace en Python porque el antiguo SQL apunta a una ruta de datos obsoleta. Las llamadas externas a APIs, las importaciones propias de Letterboxd y la exportación a SQL Server no forman parte de este runner.

## Clasificar películas

IMDb ya contiene `genres` y `runtimeMinutes`; el plan consulta ambos. `category_rules.json` relaciona géneros con meses y admite excepciones manuales con esta forma:

```json
{
  "title": "Título de película (2020)",
  "month_number": 4,
  "category": "Religión"
}
```

La categoría se propone automáticamente cuando hay un género con regla. Para temas como verano, religión, primavera o Navidad, que no se deducen bien del género IMDb, completá excepciones manuales. Los datos mensuales editables viven en `months.json`.

La lista **Por ver** excluye las películas vistas o calificadas en la actividad del usuario y separa primero las pendientes del watchlist (Letterboxd o IMDb); el resto queda ordenado por puntaje ponderado. La vista **Vistas** usa la actividad de Letterboxd y el export `ratings.csv` más reciente para comparar tu calificación con el puntaje ponderado.

La base actual no tiene créditos de dirección. Para activar el gráfico de directores, colocá los archivos oficiales de IMDb `title.crew.tsv.gz` y `name.basics.tsv.gz` dentro de `data/movies/imdb/`, y regenerá los JSON con `--skip-etl`. El tablero indica cuando esa fuente falta.

## Abrir la página React

```powershell
cd "scripts etl python/movie_dashboard"
npm install
npm run dev
```

Vite escucha solo en `127.0.0.1` (loopback; no publica el tablero en la red local). Abrí en tu propio navegador la dirección que indique Vite. La página carga el plan, los meses y el historial JSON con `fetch`. Incluye navegación entre **Por ver** y **Vistas**, búsqueda, filtros por mes/categoría, watchlist priorizada, recomendaciones ordenadas por puntaje, gráficos Plotly y tablas paginadas.

Para una compilación de despliegue: `npm run build`. El resultado se guarda en `movie_dashboard/dist`.
