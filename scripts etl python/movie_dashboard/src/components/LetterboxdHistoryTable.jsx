import { useEffect, useState } from 'react';
import './LetterboxdHistoryTable.css';

const formatScore = (score) => score == null ? '—' : Number(score).toFixed(2);

export default function LetterboxdHistoryTable({ movies }) {
  const [page, setPage] = useState(1);
  const pageSize = 40;
  const pageCount = Math.max(1, Math.ceil(movies.length / pageSize));
  useEffect(() => setPage(1), [movies]);
  const pageMovies = movies.slice((page - 1) * pageSize, page * pageSize);

  return (
    <>
      <div className="table-scroll"><table className="history-table"><thead><tr><th>Película</th><th>Categoría</th><th>Géneros</th><th>Mi puntaje</th><th>Ponderado</th><th>Director</th></tr></thead>
        <tbody>{pageMovies.map((movie) => <tr key={movie.id}><td><strong>{movie.title}</strong><small>{movie.year || 'Año desconocido'}</small></td><td>{movie.category}</td><td>{movie.genres || '—'}</td><td className="personal-score">{formatScore(movie.personal_rating)}</td><td>{formatScore(movie.weighted_score)}</td><td>{movie.directors?.join(', ') || '—'}</td></tr>)}
          {!pageMovies.length && <tr><td className="empty-row" colSpan="6">No hay películas que coincidan con los filtros.</td></tr>}
        </tbody></table></div>
      <div className="pagination"><span>{movies.length ? `${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, movies.length)} de ${movies.length}` : '0 resultados'}</span><div><button disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Anterior</button><span>Página {page} / {pageCount}</span><button disabled={page >= pageCount} onClick={() => setPage((current) => current + 1)}>Siguiente</button></div></div>
    </>
  );
}
