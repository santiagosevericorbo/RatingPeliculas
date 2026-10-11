import { useMemo, useState } from 'react';
import LetterboxdCharts from '../components/LetterboxdCharts.jsx';
import LetterboxdHistoryTable from '../components/LetterboxdHistoryTable.jsx';
import './LetterboxdPage.css';

export default function LetterboxdPage({ history, directorsAvailable }) {
  const [category, setCategory] = useState('all');
  const [search, setSearch] = useState('');
  const categories = useMemo(() => [...new Set(history.map((movie) => movie.category).filter(Boolean))].sort(), [history]);
  const visible = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('es');
    return history.filter((movie) => {
      const categoryMatch = category === 'all' || movie.category === category;
      const searchMatch = !query || `${movie.title} ${movie.genres || ''} ${(movie.directors || []).join(' ')}`.toLocaleLowerCase('es').includes(query);
      return categoryMatch && searchMatch;
    });
  }, [history, category, search]);
  const ratings = visible.filter((movie) => movie.personal_rating != null);
  const mean = ratings.length ? ratings.reduce((sum, movie) => sum + movie.personal_rating, 0) / ratings.length : null;

  return (
    <>
      <header className="hero history-hero"><div className="hero-copy"><span className="eyebrow">LETTERBOXD · HISTORIAL PERSONAL</span><h1>Lo que ya <em>viste</em></h1><p>Tu recorrido de películas, categorías y calificaciones frente al puntaje ponderado.</p></div><div className="hero-note"><span>VISTAS</span><p>Tu diario y calificaciones<br />de Letterboxd.</p></div></header>
      <section className="kpis" aria-label="Resumen de Letterboxd">
        <article><span>PELÍCULAS VISTAS</span><strong>{history.length.toLocaleString('es')}</strong></article>
        <article><span>PELÍCULAS CALIFICADAS</span><strong>{ratings.length.toLocaleString('es')}</strong></article>
        <article><span>PUNTAJE PERSONAL PROMEDIO</span><strong>{mean == null ? '—' : mean.toFixed(2)}<small> / 10</small></strong></article>
      </section>
      <LetterboxdCharts movies={visible} directorsAvailable={directorsAvailable} />
      <section className="section-block panel list-panel history-list">
        <div className="panel-heading list-section-heading"><div><span className="eyebrow">HISTORIAL</span><h2>Películas que registraste como vistas</h2><p>Las calificaciones personales se convierten a escala 0–10 para compararlas con el puntaje ponderado.</p></div><span className="result-count">{visible.length} resultados</span></div>
        <div className="history-filters"><label><span>Buscar título, género o director</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Escribí para filtrar" /></label><label><span>Categoría</span><select value={category} onChange={(event) => setCategory(event.target.value)}><option value="all">Todas</option>{categories.map((item) => <option key={item}>{item}</option>)}</select></label></div>
        <LetterboxdHistoryTable movies={visible} />
      </section>
    </>
  );
}
