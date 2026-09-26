"""MapkSpeciesTimeseries — interactive Plotly time series of MAPK species counts.

An interactive population time series of the per-compartment substrate counts the
``SubstrateCensus`` step emits (cytoplasm ERK / pERK, nuclear pERK, MEK·substrate
complexes, and the running total). Click a trace in the legend to isolate it;
hover for exact counts. Ships with the ``mapk_brs`` composite.
"""
from __future__ import annotations
import json
from process_bigraph.visualization import Visualization

# One consistent, distinguishable colour per species, reused everywhere.
_SERIES = [
    ('nucleus_pERK', 'nuclear pERK', '#1b9e77'),
    ('cytoplasm_pERK', 'cytoplasmic pERK', '#d95f02'),
    ('cytoplasm_ERK', 'cytoplasmic ERK', '#7570b3'),
    ('complexes', 'MEK·substrate complexes', '#e7298a'),
    ('total_substrate', 'total substrate', '#666666'),
]


class MapkSpeciesTimeseries(Visualization):
    """Interactive line chart of MAPK substrate populations over time."""

    def inputs(self):
        return {
            'time': 'list[float]',
            'nucleus_pERK': 'list[float]',
            'cytoplasm_pERK': 'list[float]',
            'cytoplasm_ERK': 'list[float]',
            'complexes': 'list[float]',
            'total_substrate': 'list[float]',
        }

    @classmethod
    def demo(cls):
        return {
            'time': [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120],
            'nucleus_pERK': [0, 4, 12, 26, 42, 60, 79, 97, 114, 130, 144],
            'cytoplasm_pERK': [1, 3, 6, 10, 14, 19, 23, 27, 31, 34, 37],
            'cytoplasm_ERK': [2, 6, 12, 19, 27, 36, 45, 53, 60, 66, 71],
            'complexes': [0, 3, 8, 14, 21, 29, 37, 44, 50, 55, 59],
            'total_substrate': [4, 20, 48, 88, 140, 200, 268, 340, 400, 424, 428],
        }

    def update(self, state):
        time = list(state.get('time') or [])
        traces = []
        for key, label, color in _SERIES:
            y = list(state.get(key) or [])
            x = time if len(time) == len(y) else list(range(len(y)))
            traces.append({
                'x': x, 'y': y,
                'type': 'scatter', 'mode': 'lines',
                'name': label,
                'line': {'color': color, 'width': 2.4,
                         'dash': 'dot' if key == 'total_substrate' else 'solid'},
                'hovertemplate': f'{label}: %{{y}}<extra></extra>',
            })
        layout = {
            'title': {'text': 'MAPK substrate populations under Gillespie SSA'},
            'hovermode': 'x unified',
            'legend': {'orientation': 'h', 'y': -0.22},
            'margin': {'l': 60, 'r': 20, 't': 48, 'b': 60},
            'xaxis': {'title': {'text': 'time (ticks)'}},
            'yaxis': {'title': {'text': 'count (molecules)'}},
            'template': 'plotly_white',
        }
        return {'html': (
            '<div id="viz" style="height:400px"></div>'
            '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
            '<script>Plotly.newPlot("viz",'
            + json.dumps(traces) + ',' + json.dumps(layout)
            + ', {responsive:true, displayModeBar:false});</script>'
        )}
