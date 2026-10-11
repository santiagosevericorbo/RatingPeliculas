import './Navbar.css';

export default function Navbar({ activeView, onNavigate, toWatchCount, watchedCount }) {
  return (
    <nav className="main-nav" aria-label="Secciones">
      <span className="main-nav__brand"><span className="brand-mark">◉</span> CINE / PLAN</span>
      <div className="main-nav__links">
        <button className={activeView === 'plan' ? 'is-active' : ''} onClick={() => onNavigate('plan')}>Por ver <span>{toWatchCount}</span></button>
        <button className={activeView === 'history' ? 'is-active' : ''} onClick={() => onNavigate('history')}>Vistas <span>{watchedCount}</span></button>
      </div>
    </nav>
  );
}
