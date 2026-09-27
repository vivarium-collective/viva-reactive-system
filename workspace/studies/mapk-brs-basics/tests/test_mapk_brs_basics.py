"""Behavior tests for the mapk-brs-basics study.

Self-contained: each test builds the MAPK BRS composite and runs it in-process
under Gillespie SSA with the study's seed, then asserts on the per-compartment
substrate census. This reproduces the qualitative behaviour of the prior live
demo without depending on the dashboard run store, so the tests pass in any
workspace venv.
"""
import pytest

from process_bigraph import Composite, gather_emitter_results
from process_bigraph.emitter import emitter_from_wires

from pbg_reactive_system.core import build_core
from pbg_reactive_system.composites import mapk_brs

SEED = 42
TOTAL_TIME = 120.0
PATHS = [
    'global_time', 'cytoplasm_ERK', 'cytoplasm_pERK',
    'nucleus_pERK', 'complexes', 'total_substrate',
]


@pytest.fixture(scope='module')
def series():
    """One seeded 120-tick run of the MAPK BRS, as an emitted time series."""
    core = build_core()
    doc = mapk_brs(core=core, seed=SEED)
    state = dict(doc['state'])
    state['emitter'] = emitter_from_wires({p: [p] for p in PATHS})
    sim = Composite({'state': state, 'composition': doc['schema']}, core=core)
    sim.run(TOTAL_TIME)
    return next(iter(gather_emitter_results(sim).values()))


def test_nucleus_accumulates_perk(series):
    """primary — phospho-ERK translocates into the nucleus over the run."""
    assert series[-1]['nucleus_pERK'] >= 1


def test_nucleus_starts_empty(series):
    """diagnostic — accumulation is dynamics, not an initial condition."""
    assert series[0]['nucleus_pERK'] == 0


def test_complexes_form(series):
    """supporting — MEK·substrate complexes form during the run."""
    assert max(s['complexes'] for s in series) >= 1


def test_population_grows(series):
    """supporting — the substrate population evolves into a non-trivial series."""
    assert series[-1]['total_substrate'] >= 5
    assert series[-1]['total_substrate'] > series[0]['total_substrate']


def test_run_length(series):
    """the run emits one snapshot per tick plus t=0."""
    assert len(series) == int(TOTAL_TIME) + 1
    assert series[-1]['global_time'] == TOTAL_TIME
