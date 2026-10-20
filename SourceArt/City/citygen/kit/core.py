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

    # Unit asphalt pad for parking lots (top at z=0, 0.3 deep), scaled by the placement code.
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -0.3, 0.5, 0.5, 0.0, "M_Asphalt", skip=("-z",))
    K.add("KIT_LotAsphalt_1x1", mb, FAM, "Structure", meta=dict(scalable=True))

    # Parking stall line: 0.12 x 5.0 m paint strip along local Y, origin at its center, 1 cm proud.
    mb = MeshBuilder()
    mb.box(-0.06, -2.5, 0.0, 0.06, 2.5, 0.012, "M_RoadLine_White", skip=("-z",))
    K.add("KIT_ParkingLine", mb, FAM, "Structure")

    # Unit gravel pad (industrial yards), same convention as KIT_Pad_1x1.
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -0.3, 0.5, 0.5, 0.0, "M_Gravel", skip=("-z",))
    K.add("KIT_PadGravel_1x1", mb, FAM, "Structure", meta=dict(scalable=True))
