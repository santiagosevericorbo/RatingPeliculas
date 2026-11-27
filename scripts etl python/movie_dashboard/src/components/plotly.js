import Plotly from 'plotly.js/lib/core';
import bar from 'plotly.js/lib/bar';
import pie from 'plotly.js/lib/pie';
import scattergl from 'plotly.js/lib/scattergl';
import createPlotlyComponent from 'react-plotly.js/factory';

Plotly.register([bar, pie, scattergl]);

export default createPlotlyComponent(Plotly);
