import { useEffect, useState } from 'react';
import MovieTable from './MovieTable.jsx';

export default function MovieListSection({ eyebrow, title, description, movies, onSelectMovie }) {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const pageCount = Math.max(1, Math.ceil(movies.length / pageSize));
  useEffect(() => setPage(1), [movies]);
  const pageMovies = movies.slice((page - 1) * pageSize, page * pageSize);

  return (
    <section className="section-block panel list-panel">
      <div className="panel-heading list-section-heading"><div><span className="eyebrow">{eyebrow}</span><h2>{title}</h2>{description && <p>{description}</p>}</div><span className="result-count">{movies.length.toLocaleString('es')} resultados</span></div>
      <MovieTable movies={pageMovies} onSelectMovie={onSelectMovie} />
      <div className="pagination"><span>{movies.length ? `${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, movies.length)} de ${movies.length}` : '0 resultados'}</span><div><button disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Anterior</button><span>Página {page} / {pageCount}</span><button disabled={page >= pageCount} onClick={() => setPage((current) => current + 1)}>Siguiente</button></div></div>
    </section>
  );
}
