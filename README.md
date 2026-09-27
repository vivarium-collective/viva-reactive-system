# viva-reactive-system

<!-- BEGIN dashboard -->
> ## 📊 [**Live dashboard →**](https://vivarium-collective.github.io/viva-reactive-system/dashboard/)
> Browse every investigation & study interactively, or read the [published investigation reports](https://vivarium-collective.github.io/viva-reactive-system/). Auto-published from `main` on every merge.
<!-- END dashboard -->

A **process-bigraph research workspace** for **Milner-style Bigraphical
Reactive Systems (BRS)**, driven through the interactive
[**vivarium-workbench**](https://github.com/vivarium-collective/vivarium-workbench)
dashboard. The running example is a **MAPK signalling cycle** modelled as a
bigraph and simulated under Gillespie SSA.

> The core engine lives in the Python package `pbg_reactive_system`; the
> workspace layer (`workspace.yaml`, studies, investigations, reports) turns it
> into a workbench you can run, inspect, and report from.

---

## What's inside

- **A generic BRS engine** — `BigraphicalReactiveSystem`, a `process-bigraph`
  Process that fires Milner-style redex → reactum rewrite rules on a
  time-stepped schedule, in three modes: `deterministic`, `stochastic`, and
  Gillespie `gillespie` SSA.
- **A worked MAPK example** — seven rules (`phosphorylate`, `dissociate`,
  `dephosphorylate`, `translocate_erk_in/out`, `translocate_perk_in/out`) over
  a nested cell bigraph (`Cell ⊃ Cytoplasm ⊃ {Nucleus, ERLumen}`), with
  MEK·pERK complexes carried on the link graph.
- **A workbench composite** — `pbg_reactive_system.composites.mapk_brs`, a
  `@composite_generator` the dashboard discovers, runs, and charts.
- **A demo study** — `mapk-brs-basics`, grouped under the `mapk-signalling`
  investigation, which reproduces the prior live demo's basic systems as
  workbench visualizations (see below).

## The MAPK BRS demo, in the workbench

The `mapk-brs-basics` study reproduces the original live demo inside the
workbench: it runs the MAPK cycle under Gillespie SSA and surfaces its **basic
systems** as five figures —

| Figure | What it shows |
|---|---|
| **Initial bigraph** | Place graph (nested compartments) + link graph (MEK·substrate bonds). |
| **Population time series** | Per-compartment substrate counts under Gillespie SSA. |
| **Structural snapshots** | Cell cartoons through the run — ERK/pERK across compartments. |
| **Rule catalog** | Each rule's redex → reactum beside a real before/after state. |
| **Animation** | Smooth interpolation across rule firings; pERK entering the nucleus. |

On a seeded 120-tick run the cycle behaves as expected: MEK·substrate complexes
form in the cytoplasm and phospho-ERK accumulates in the nucleus (0 → 144), and
all five behavior tests pass. See `workspace/studies/mapk-brs-basics/study.yaml`.

## Open the workbench

```bash
# 1. install (editable) into a workspace venv
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. start the dashboard (serves the workspace, studies, and reports)
vivarium-workbench serve --workspace . --port 8765
#    → open http://localhost:8765, pick the mapk-signalling investigation,
#      open the mapk-brs-basics study, and browse its five figures.
```

With the [viva-superpowers](https://github.com/vivarium-collective/viva-superpowers)
plugin installed you can instead drive it with the skills — `/viva-workbench
start`, `/viva-study open mapk-brs-basics`, `/viva-report`.

**Regenerate the demo figures** (deterministic, seed 42):

```bash
cd workspace/studies/mapk-brs-basics && python render_panels.py
```

## Quick start — drive the engine directly

```python
from process_bigraph import Composite, gather_emitter_results
from process_bigraph.emitter import emitter_from_wires
from pbg_reactive_system.core import build_core
from pbg_reactive_system.composites import mapk_brs

core = build_core()                       # registers the MAPK bigraph signature
doc = mapk_brs(core=core, seed=42)        # the workbench composite
state = dict(doc["state"])
state["emitter"] = emitter_from_wires(
    {"global_time": ["global_time"], "nucleus_pERK": ["nucleus_pERK"]})

sim = Composite({"state": state, "composition": doc["schema"]}, core=core)
sim.run(120.0)

series = next(iter(gather_emitter_results(sim).values()))
print("nuclear pERK:", series[0]["nucleus_pERK"], "→", series[-1]["nucleus_pERK"])
```

To fire your own rules on your own bigraph, use `BigraphicalReactiveSystem`
directly with a list of `bigraph_schema.assembly.ReactionRule`s — see the engine
docstring in `pbg_reactive_system/processes.py`.

## Workspace layout

```
workspace.yaml                     # workspace manifest (name, package, layout)
pbg_reactive_system/               # the Python package (engine + example)
  processes.py                     #   BigraphicalReactiveSystem + SubstrateCensus
  composites.py                    #   mapk_brs composite generator + rules
  types.py                         #   the MAPK bigraph signature
  core.py                          #   build_core() the workbench builds against
  mapk_plots.py                    #   cell cartoons / snapshots / animation
workspace/
  investigations/mapk-signalling/  # the investigation grouping the demo study
  studies/mapk-brs-basics/         # the demo study: study.yaml, tests/, charts/
  reports/                         # rendered workbench report (index.html)
demo/                              # the original standalone HTML demo report
references/brs_mapk.md             # the formalism + biology citations
```

## Tests

```bash
uv pip install -e ".[dev]"
pytest                                        # engine + composite unit/integration tests
pytest workspace/studies/mapk-brs-basics/tests # the study's behavior tests
```

## API

| Symbol | What it is |
|---|---|
| `BigraphicalReactiveSystem` | `process_bigraph.Process`; fires rules on each tick. |
| `SubstrateCensus` | `Step` emitting scalar per-compartment substrate counts. |
| `mapk_brs(core=None, *, mode, seed, interval, max_per_tick)` | The workbench composite generator. |
| `build_core()` | Allocate a core with the MAPK signature registered. |
| `register_mapk_types(core)` | Register the `Cell` / `Compartment` / `MEK` / `ERK` / `pERK` / `NPC` / … sorts. |
| `mapk_rules()` | The seven MAPK rules as `ReactionRule`s. |
| `initial_mapk_state(seed=0)` | The seeded nested cell bigraph. |
| `get_brs_mapk_doc(core=None, config=None)` | Legacy composite document builder (emitter baked in). |
| `plot_brs_mapk(results, state, config)` | Five-panel summary: bigraph, time series, snapshots, rule catalog, animation. |

## Limitations

- The matcher operates on `_type` string equality on registered schema types;
  encode value-based states as distinct sorts (`Red` vs `Blue`, not a `color`
  field).
- The MAPK example is an illustrative BRS-engine demonstration, not a calibrated
  kinetic model — rule rates are nominal and the rewrite rules are not
  mass-conserving, so substrate copies grow over a run.

## License

MIT.
