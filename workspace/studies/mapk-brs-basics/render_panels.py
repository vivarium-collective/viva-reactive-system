"""Render the MAPK BRS demo panels for the mapk-brs-basics study.

Reproduces the prior live demo's basic systems as workbench charts:

    charts/mapk_brs_viz.png         — initial bigraph (place + link graph)
    charts/mapk_brs_timeseries.png  — per-compartment substrate populations
    charts/mapk_brs_snapshots.png   — structural cell cartoons through the run
    charts/mapk_brs_trace.png       — rule catalog (redex→reactum + before/after)
    charts/mapk_brs_animation.gif   — smooth animation across rule firings

One seeded run (seed 42, 120 ticks) drives all five, matching the study's
baseline run. Invoked by each `visualizations[].render` entry (cwd = this study
dir), so `charts/` resolves here; a single invocation writes every panel.
"""
import os
import shutil
import tempfile

from process_bigraph import Composite, gather_emitter_results
from process_bigraph.emitter import emitter_from_wires

from pbg_reactive_system.core import build_core
from pbg_reactive_system.composites import mapk_brs
from pbg_reactive_system.mapk_plots import plot_brs_mapk

HERE = os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(HERE, 'charts')
SEED = 42
TOTAL_TIME = 120.0

# The five final panels we keep — plot_brs_mapk also drops ~30 intermediate
# redex/reactum tiles + a graphviz dump + overview.md/state.json, which we
# render into a temp dir and discard so the study's charts/ auto-discovers
# only these.
PANELS = [
    'mapk_brs_viz.png',         # initial bigraph (place + link graph)
    'mapk_brs_timeseries.png',  # per-compartment substrate populations
    'mapk_brs_snapshots.png',   # structural cell cartoons through the run
    'mapk_brs_trace.png',       # rule catalog (redex→reactum + before/after)
    'mapk_brs_animation.gif',   # smooth animation across rule firings
]


def main():
    core = build_core()
    doc = mapk_brs(core=core, seed=SEED)
    initial_cell = doc['state']['cell']
    state = dict(doc['state'])
    state['emitter'] = emitter_from_wires(
        {'global_time': ['global_time'], 'cell': ['cell']})
    sim = Composite({'state': state, 'composition': doc['schema']}, core=core)
    sim.run(TOTAL_TIME)
    results = next(iter(gather_emitter_results(sim).values()))

    os.makedirs(CHARTS, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        plot_brs_mapk(
            results,
            state=initial_cell,
            config={'filename': 'mapk_brs', 'out_dir': tmp, 'n_snapshots': 6})
        for panel in PANELS:
            src = os.path.join(tmp, panel)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(CHARTS, panel))
    print(f'wrote {len(PANELS)} panels to {CHARTS}')


if __name__ == '__main__':
    main()
