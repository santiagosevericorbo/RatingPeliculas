import { useEffect, useState } from 'react';

const DATA_BASE = `${import.meta.env.BASE_URL}data`;

export default function usePlanData() {
  const [state, setState] = useState({ movies: [], months: [], loading: true, error: '' });

  useEffect(() => {
    const files = ['monthly_movie_plan.json', 'months.json', 'letterboxd_history.json'];
    Promise.all(files.map(async (file) => {
      const response = await fetch(`${DATA_BASE}/${file}`);
      if (!response.ok) throw new Error(`No se pudo cargar ${file} (${response.status}).`);
      return response.json();
    }))
      .then(([movies, months, historyData]) => setState({
        movies,
        months,
        history: historyData.movies,
        directorsAvailable: historyData.director_data_available,
        loading: false,
        error: '',
      }))
      .catch((error) => setState((current) => ({ ...current, loading: false, error: error.message })));
  }, []);

  return state;
}
