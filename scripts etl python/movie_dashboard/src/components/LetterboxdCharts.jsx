import Plot from './plotly.js';
import './LetterboxdCharts.css';

const COLORS = ['#b6ee68', '#82c7c0', '#e9ce79', '#c4a7e7', '#ee857d', '#82a9dd', '#d795c6', '#8dc68b', '#f08f51', '#70c9d1'];
const layoutBase = { autosize: true, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#dfe3d9', family: 'Inter, system-ui, sans-serif' }, margin: { l: 48, r: 16, t: 18, b: 48 } };

function groupCounts(items, key) {
  const counts = new Map();
  for (const item of items) {
    const value = key(item);
    if (!value) continue;
    counts.set(value, (counts.get(value) || 0) + 1);
  }
  return [...counts].sort((a, b) => b[1] - a[1]);
}

export default function LetterboxdCharts({ movies, directorsAvailable }) {
  const categories = groupCounts(movies, (movie) => movie.category || 'Sin categoría');
  const directors = groupCounts(movies.flatMap((movie) => movie.directors || []), (name) => name).slice(0, 12);
  const rated = movies.filter((movie) => movie.personal_rating != null && movie.weighted_score != null);
  const chartRated = rated.length > 4000 ? rated.filter((_, index) => index % Math.ceil(rated.length / 4000) === 0) : rated;

  return (
    <section className="analytics-grid">
      <article className="panel analytics-panel category-chart"><div className="panel-heading"><div><span className="eyebrow">MI HISTORIAL</span><h2>Vistas por categoría</h2></div></div>
        {categories.length ? <Plot data={[{ type: 'pie', hole: .55, labels: categories.map(([name]) => name), values: categories.map(([, count]) => count), marker: { colors: categories.map((_, index) => COLORS[index % COLORS.length]), line: { color: '#191c17', width: 2 } }, textinfo: 'label+percent', hovertemplate: '%{label}<br>%{value} películas · %{percent}<extra></extra>' }]} layout={{ ...layoutBase, height: 360, showlegend: false }} config={{ responsive: true, displaylogo: false }} style={{ width: '100%' }} useResizeHandler /> : <p className="chart-notice">Todavía no hay categorías para mostrar.</p>}
      </article>

      <article className="panel analytics-panel director-chart"><div className="panel-heading"><div><span className="eyebrow">CRÉDITOS</span><h2>Directores más frecuentes</h2></div></div>
        {directorsAvailable && directors.length ? <Plot data={[{ type: 'bar', orientation: 'h', x: directors.map(([, count]) => count).reverse(), y: directors.map(([name]) => name).reverse(), marker: { color: '#b6ee68', opacity: .85 }, hovertemplate: '%{y}<br>%{x} películas<extra></extra>' }]} layout={{ ...layoutBase, height: Math.max(320, directors.length * 36), margin: { l: 130, r: 20, t: 10, b: 38 }, xaxis: { title: 'Películas', gridcolor: '#292d26' }, yaxis: { automargin: true } }} config={{ responsive: true, displaylogo: false }} style={{ width: '100%' }} useResizeHandler /> : <div className="chart-notice"><strong>Falta la fuente de créditos.</strong><p>Guardá <code>title.crew.tsv.gz</code> y <code>name.basics.tsv.gz</code> en <code>data/movies/imdb/</code> y volvé a generar los JSON. Esos archivos no están en este repositorio.</p></div>}
      </article>

      <article className="panel analytics-panel rating-chart"><div className="panel-heading"><div><span className="eyebrow">COMPARACIÓN</span><h2>Mi puntaje y el ponderado</h2></div><span className="panel-hint">{rated.length} películas con ambos puntajes</span></div>
        {chartRated.length ? <Plot data={[
          { type: 'scattergl', mode: 'markers', x: chartRated.map((movie) => movie.personal_rating), y: chartRated.map((movie) => movie.weighted_score), customdata: chartRated.map((movie) => [movie.title, movie.category]), marker: { size: 9, color: '#82c7c0', opacity: .78 }, hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Mi puntaje: %{x:.1f}<br>Ponderado: %{y:.2f}<extra></extra>' },
          { type: 'scattergl', mode: 'lines', x: [0, 10], y: [0, 10], line: { color: '#777d70', dash: 'dash', width: 1 }, hoverinfo: 'skip', showlegend: false },
        ]} layout={{ ...layoutBase, height: 390, xaxis: { title: 'Mi puntaje Letterboxd (0–10)', range: [0, 10], gridcolor: '#292d26' }, yaxis: { title: 'Puntaje ponderado (0–10)', range: [0, 10], gridcolor: '#292d26' }, showlegend: false }} config={{ responsive: true, displaylogo: false }} style={{ width: '100%' }} useResizeHandler /> : <p className="chart-notice">No hay películas con ambos puntajes. Se comparan solo las películas calificadas en tu exportación de Letterboxd.</p>}
      </article>
    </section>
  );
}
