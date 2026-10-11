import Plot from './plotly.js';
import './ScoreDurationChart.css';

const MONTH_COLORS = ['#b6ee68', '#ed9b75', '#82c7c0', '#c4a7e7', '#e9ce79', '#82a9dd', '#ee857d', '#d795c6', '#8dc68b', '#f08f51', '#b2a2d8', '#70c9d1'];

export default function ScoreDurationChart({ movies, onSelectMovie }) {
  const points = movies.filter((movie) => movie.duration_minutes != null && movie.weighted_score != null);
  const stride = Math.max(1, Math.ceil(points.length / 4000));
  const chartPoints = points.filter((_, index) => index % stride === 0);
  return (
    <div className="chart-shell">
      {chartPoints.length ? <Plot
        data={[{
          type: 'scattergl', mode: 'markers',
          x: chartPoints.map((movie) => movie.duration_minutes),
          y: chartPoints.map((movie) => movie.weighted_score),
          customdata: chartPoints.map((movie) => [movie.title, movie.month || 'Sin asignar', movie.category, movie.genres || 'Sin género']),
          marker: { size: 10, opacity: .78, color: chartPoints.map((movie) => movie.month_number ? MONTH_COLORS[(movie.month_number - 1) % MONTH_COLORS.length] : '#84877f'), line: { color: '#11140f', width: 1 } },
          hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}<br>%{customdata[3]}<br>Duración: %{x} min<br>Puntaje: %{y:.2f}<extra></extra>',
        }]}
        layout={{ autosize: true, height: 390, margin: { l: 55, r: 20, t: 20, b: 55 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#dfe3d9', family: 'Inter, system-ui, sans-serif' }, xaxis: { title: 'Duración (minutos)', gridcolor: '#292d26', zerolinecolor: '#292d26' }, yaxis: { title: 'Puntaje ponderado', gridcolor: '#292d26', zerolinecolor: '#292d26' }, showlegend: false }}
        config={{ responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] }}
        onClick={(event) => { const point = event.points?.[0]; if (point) onSelectMovie(point.customdata[0]); }}
        style={{ width: '100%' }} useResizeHandler
      /> : <div className="chart-empty">No hay películas con puntaje y duración para graficar en esta selección.</div>}
    </div>
  );
}
