"""Kit family: CORE (lead-owned) — tiny structural helpers used by the assembler."""
from ..meshutil import MeshBuilder

FAM = "core"


def build(K):
    # Unit foundation block, top face at z=0. The assembler scales it to the building footprint
    # (x, y) and to the depth between the ground and the building base (z).
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -1.0, 0.5, 0.5, 0.0, "M_Wall_Concrete", skip=("-z",))
    K.add("KIT_Foundation_1x1", mb, FAM, "Structure", meta=dict(scalable=True))

    # Unit flat pad (walkways, driveways, slabs): 1 x 1 m, top at z=0, 0.3 deep so it never floats.
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -0.3, 0.5, 0.5, 0.0, "M_Concrete", skip=("-z",))
    K.add("KIT_Pad_1x1", mb, FAM, "Structure", meta=dict(scalable=True))
