import './MonthCards.css';

export default function MonthCards({ months, movies, selectedMonth, onSelect }) {
  return (
    <section className="month-grid" aria-label="Plan temático por mes">
      {months.map((month) => {
        const count = movies.filter((movie) => movie.month_number === month.number).length;
        const active = String(selectedMonth) === String(month.number);
        return (
          <button key={month.number} className={`month-card${active ? ' is-active' : ''}`} onClick={() => onSelect(active ? 'all' : String(month.number))}>
            <span className="month-card__top"><span className="month-card__emoji">{month.emoji}</span><span className="month-card__count">{count} títulos</span></span>
            <span className="month-card__name">{month.name}</span>
            <span className="month-card__theme">{month.theme}</span>
          </button>
        );
      })}
    </section>
  );
}
