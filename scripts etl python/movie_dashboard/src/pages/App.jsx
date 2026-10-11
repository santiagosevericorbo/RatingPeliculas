import { useMemo, useState } from 'react';
import Filters from '../components/Filters.jsx';
import LetterboxdPage from './LetterboxdPage.jsx';
import MonthCards from '../components/MonthCards.jsx';
import MovieListSection from '../components/MovieListSection.jsx';
import Navbar from '../components/Navbar.jsx';
import ScoreDurationChart from '../components/ScoreDurationChart.jsx';
import usePlanData from '../hooks/usePlanData.js';
import './App.css';

function byWeightedScore(left, right) {
  const score = (movie) => movie.weighted_score == null ? -Infinity : Number(movie.weighted_score);
  return score(right) - score(left);
}

export default function App() {
  const { movies, months, history, directorsAvailable, loading, error } = usePlanData();
  const [activeView, setActiveView] = useState('plan');
  const [month, setMonth] = useState('all');
  const [category, setCategory] = useState('all');
  const [search, setSearch] = useState('');

  const toWatchMovies = useMemo(() => movies.filter((movie) => !movie.is_watched), [movies]);
  const categories = useMemo(() => [...new Set(toWatchMovies.map((movie) => movie.category).filter(Boolean))].sort(), [toWatchMovies]);
  const visibleMovies = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('es');
    return toWatchMovies.filter((movie) => {
      const monthMatch = month === 'all' || (month === 'unassigned' ? movie.month_number == null : String(movie.month_number) === month);
      const categoryMatch = category === 'all' || movie.category === category;
      const textMatch = !query || `${movie.title} ${movie.genres || ''} ${movie.category || ''}`.toLocaleLowerCase('es').includes(query);
      return monthMatch && categoryMatch && textMatch;
    });
  }, [toWatchMovies, month, category, search]);
  const watchlistMovies = useMemo(() => visibleMovies.filter((movie) => movie.in_watchlist).sort(byWeightedScore), [visibleMovies]);
  const recommendations = useMemo(() => visibleMovies.filter((movie) => !movie.in_watchlist).sort(byWeightedScore), [visibleMovies]);
  const rated = visibleMovies.filter((movie) => movie.weighted_score != null);
  const average = rated.length ? rated.reduce((total, movie) => total + movie.weighted_score, 0) / rated.length : 0;
  const reset = () => { setMonth('all'); setCategory('all'); setSearch(''); };

  if (loading) return <main className="state-screen"><span className="loader" /><p>Cargando listas y análisis desde JSON…</p></main>;
  if (error) return <main className="state-screen"><div className="error-card"><span className="eyebrow">DATOS NO DISPONIBLES</span><h1>No pude cargar el tablero</h1><p>{error}</p><p>Generá los JSON con el comando Python del README y volvé a cargar.</p></div></main>;

  return (
    <main className="dashboard">
      <Navbar activeView={activeView} onNavigate={setActiveView} toWatchCount={toWatchMovies.length} watchedCount={history.length} />
      {activeView === 'history' ? <LetterboxdPage history={history} directorsAvailable={directorsAvailable} /> : <>
        <header className="hero"><div className="hero-copy"><span className="eyebrow">CINE · PLANIFICACIÓN ANUAL</span><h1>Tu año en <em>películas</em></h1><p>Ocultamos las ya vistas. Tu watchlist va primero; las demás quedan ordenadas por puntaje.</p></div><div className="hero-note"><span>01 — 12</span><p>Elegí una temporada.<br />Encontrá tu próxima película.</p></div></header>

        <section className="kpis" aria-label="Resumen de películas por ver"><article><span>PELÍCULAS POR VER</span><strong>{toWatchMovies.length.toLocaleString('es')}</strong></article><article><span>EN MI WATCHLIST</span><strong>{toWatchMovies.filter((movie) => movie.in_watchlist).length.toLocaleString('es')}</strong></article><article><span>PUNTAJE PROMEDIO</span><strong>{average.toFixed(2)}<small> / 10</small></strong></article></section>

        <section className="section-block"><div className="section-heading"><div><span className="eyebrow">CALENDARIO</span><h2>Doce meses, doce temas</h2></div><span className="section-caption">Seleccioná un mes para filtrar las películas por ver</span></div><MonthCards months={months} movies={toWatchMovies} selectedMonth={month} onSelect={setMonth} /></section>

        <Filters months={months} categories={categories} selectedMonth={month} selectedCategory={category} search={search} onMonthChange={setMonth} onCategoryChange={setCategory} onSearchChange={setSearch} onReset={reset} />

        <section className="section-block analysis-grid"><article className="panel chart-panel"><div className="panel-heading"><div><span className="eyebrow">EXPLORAR</span><h2>Puntaje y duración</h2></div><span className="panel-hint">Clic en un punto para buscar la película</span></div><ScoreDurationChart movies={visibleMovies} onSelectMovie={setSearch} /></article><aside className="panel insight-panel"><span className="eyebrow">FILTRADAS</span><strong>{visibleMovies.length.toLocaleString('es')}</strong><p>películas no vistas coinciden con los filtros.</p><div className="insight-divider" /><p>Las listas se vuelven a ordenar por puntaje ponderado después de aplicar los filtros.</p></aside></section>

        <MovieListSection eyebrow="WATCHLIST · PRIORIDAD" title="En mi watchlist" description="No vistas y guardadas en Letterboxd o IMDb, ordenadas por puntaje ponderado." movies={watchlistMovies} onSelectMovie={setSearch} />
        <MovieListSection eyebrow="RECOMENDACIONES" title="Fuera del watchlist" description="Otras películas que no viste, ordenadas por puntaje ponderado." movies={recommendations} onSelectMovie={setSearch} />
      </>}
      <footer className="footer"><span>PLAN DE CINE</span><span>Géneros y duración: IMDb · Puntaje: modelo ponderado del proyecto</span></footer>
    </main>
  );
}
