import './MovieTable.css';

const score = (value) => value == null ? '—' : Number(value).toFixed(2);
const duration = (value) => value == null ? '—' : `${value} min`;

export default function MovieTable({ movies, onSelectMovie }) {
  return (
    <div className="table-scroll">
      <table className="movie-table">
        <thead><tr><th>Película</th><th>Puntaje</th><th>Categoría</th><th>Mes</th><th>Duración</th></tr></thead>
        <tbody>
          {movies.map((movie) => <tr key={movie.id} onClick={() => onSelectMovie(movie.title)}>
            <td><strong>{movie.title}</strong><small>{movie.genres || 'Géneros no disponibles'}</small></td>
            <td className="score-cell">{score(movie.weighted_score)}</td>
            <td><span className="category-pill">{movie.category}</span></td>
            <td>{movie.month || 'Sin asignar'}</td>
            <td>{duration(movie.duration_minutes)}</td>
          </tr>)}
          {!movies.length && <tr><td className="empty-row" colSpan="5">No hay películas que coincidan con estos filtros.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
