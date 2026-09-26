"""MapkAnimation — the MAPK BRS cell-cartoon animation, embedded as a GIF.

The same smooth cell-cartoon animation the mapk-brs-basics study ships, made
available on the composite itself. It regenerates deterministically (seed 42),
subsampled to a handful of keyframes so it renders responsively, and embeds the
result as a base64 GIF so the viewer needs no server-side state.

``config`` overrides: ``total_time`` (default 60), ``seed`` (default 42),
``n_keyframes`` (default 12), ``n_intermediate`` (default 4), ``fps`` (default 8).
"""
from __future__ import annotations
import base64
import os
import tempfile
from process_bigraph.visualization import Visualization


class MapkAnimation(Visualization):
    """Regenerate the MAPK cell-cartoon animation and embed it as a GIF."""

    def inputs(self):
        # A single list input keeps the renderer on the one-shot path (not the
        # synthetic-streaming path); the animation is regenerated internally.
        return {'time': 'list[float]'}

    @classmethod
    def demo(cls):
        return {'time': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]}

    def update(self, state):
        from process_bigraph import Composite, gather_emitter_results
        from process_bigraph.emitter import emitter_from_wires
        from pbg_reactive_system.core import build_core
        from pbg_reactive_system.composites import mapk_brs
        from pbg_reactive_system.mapk_plots import (
            _make_smooth_animation, _iter_compartments)

        cfg = getattr(self, 'config', None) or {}
        total_time = float(cfg.get('total_time', 60.0))
        seed = int(cfg.get('seed', 42))
        n_keyframes = int(cfg.get('n_keyframes', 12))
        n_intermediate = int(cfg.get('n_intermediate', 4))
        fps = int(cfg.get('fps', 8))

        core = build_core()
        doc = mapk_brs(core=core, seed=seed)
        st = dict(doc['state'])
        st['emitter'] = emitter_from_wires(
            {'global_time': ['global_time'], 'cell': ['cell']})
        sim = Composite({'state': st, 'composition': doc['schema']}, core=core)
        sim.run(total_time)
        series = next(iter(gather_emitter_results(sim).values()))
        states = [s['cell'] for s in series]
        times = [s['global_time'] for s in series]

        # Subsample to evenly-spaced keyframes so the GIF stays light + fast.
        if len(states) > n_keyframes:
            idx = [round(i * (len(states) - 1) / (n_keyframes - 1))
                   for i in range(n_keyframes)]
            states = [states[i] for i in idx]
            times = [times[i] for i in idx]

        compartment_names = []
        for s in states:
            for name, _ in _iter_compartments(s):
                if name not in compartment_names:
                    compartment_names.append(name)

        with tempfile.TemporaryDirectory() as tmp:
            _make_smooth_animation(
                'mapk_brs', tmp, states, times, compartment_names, firings=[],
                n_intermediate=n_intermediate, fps=fps)
            gif_path = os.path.join(tmp, 'mapk_brs_animation.gif')
            if not os.path.exists(gif_path):
                return {'html': '<p>animation could not be generated</p>'}
            uri = ('data:image/gif;base64,'
                   + base64.b64encode(open(gif_path, 'rb').read()).decode())

        return {'html': (
            '<figure style="margin:0;text-align:center">'
            f'<img src="{uri}" alt="MAPK BRS animation" '
            'style="max-width:100%;height:auto;border-radius:8px">'
            '<figcaption style="font-size:13px;color:#5f6b7a;margin-top:8px">'
            'MAPK BRS under Gillespie SSA (seed 42) — MEK·ERK complexes form in '
            'the cytoplasm and phospho-ERK translocates into the nucleus.'
            '</figcaption></figure>'
        )}
