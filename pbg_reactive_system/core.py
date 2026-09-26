"""``build_core()`` — the workspace core the vivarium-workbench builds against.

The workbench's env worker imports ``pbg_reactive_system.core.build_core`` and
calls it to obtain a ``process_bigraph`` core with this workspace's types and
processes registered, before resolving/running any composite. For the MAPK BRS
that means registering the bigraph signature (``Cell``, ``Compartment``,
``MEK``, ``ERK``, ``pERK``, ``NPC``, ``Cytoplasm``, ``Nucleus``, ``ERLumen``)
so the nested-cell state validates, and importing ``processes`` so the
``BigraphicalReactiveSystem`` process class is defined for address resolution.
"""
from process_bigraph import allocate_core

from .types import register_mapk_types
from .processes import BigraphicalReactiveSystem, SubstrateCensus
from .visualizations import MapkSpeciesTimeseries, MapkAnimation


def build_core():
    """Allocate a core with the MAPK BRS signature, processes, and viz registered.

    Registering under bare ``local:<Name>`` links lets composites address them as
    ``local:BigraphicalReactiveSystem`` / ``local:SubstrateCensus`` /
    ``local:MapkSpeciesTimeseries`` / ``local:MapkAnimation`` (the fully-qualified
    ``local:!pbg_reactive_system...`` form also resolves).
    """
    core = allocate_core()
    register_mapk_types(core)
    core.register_link('BigraphicalReactiveSystem', BigraphicalReactiveSystem)
    core.register_link('SubstrateCensus', SubstrateCensus)
    core.register_link('MapkSpeciesTimeseries', MapkSpeciesTimeseries)
    core.register_link('MapkAnimation', MapkAnimation)
    return core
