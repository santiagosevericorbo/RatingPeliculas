import './Filters.css';

export default function Filters({ months, categories, selectedMonth, selectedCategory, search, onMonthChange, onCategoryChange, onSearchChange, onReset }) {
  return (
    <section className="filters" aria-label="Filtros del plan">
      <label className="filter-search">
        <span>Buscar película</span>
        <input value={search} onChange={(event) => onSearchChange(event.target.value)} placeholder="Título o género" />
      </label>
      <label>
        <span>Mes</span>
        <select value={selectedMonth} onChange={(event) => onMonthChange(event.target.value)}>
          <option value="all">Todos los meses</option>
          {months.map((month) => <option key={month.number} value={month.number}>{month.name} · {month.theme}</option>)}
          <option value="unassigned">Sin asignar</option>
        </select>
      </label>
      <label>
        <span>Categoría</span>
        <select value={selectedCategory} onChange={(event) => onCategoryChange(event.target.value)}>
          <option value="all">Todas las categorías</option>
          {categories.map((category) => <option key={category} value={category}>{category}</option>)}
        </select>
      </label>
      <button className="reset-button" onClick={onReset}>Limpiar filtros</button>
    </section>
  );
}
