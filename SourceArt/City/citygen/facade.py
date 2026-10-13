"""Shared facade construction helpers for kit pieces (consistent openings across the kit).

Local piece frame (see docs/KIT_SPEC.md):
    x = across the facade, y = depth INTO the building (+Y), z = up.
    The outer facade plane is y = 0 and faces -Y. Wall body occupies y in [0, WALL_T].
    Things that stick out of the facade (frames, sills, awnings, signs) go to y < 0.

All functions append to a MeshBuilder. Hole = (x0, z0, x1, z1) rectangle on the facade.
"""
from mathutils import Vector

from . import config as C
from .meshutil import MeshBuilder

FRAME_W = 0.09     # window/door frame width
FRAME_D = 0.05     # how far frames stand proud of the facade
REVEAL = 0.12      # glass / door recess depth
SILL_D = 0.14      # sill projection
SILL_H = 0.07


def _q(mb, a, b, c, d, mat):
    mb.face([Vector(a), Vector(b), Vector(c), Vector(d)], mat)


def panel(mb, x0, x1, z0, z1, holes, mat, y=0.0, facing=-1):
    """Rectangle (x0..x1, z0..z1) at plane y with rectangular holes. facing=-1 -> normal -Y."""
    xs = sorted({x0, x1, *[h[0] for h in holes], *[h[2] for h in holes]})
    zs = sorted({z0, z1, *[h[1] for h in holes], *[h[3] for h in holes]})
    xs = [x for x in xs if x0 - 1e-6 <= x <= x1 + 1e-6]
    zs = [z for z in zs if z0 - 1e-6 <= z <= z1 + 1e-6]
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            cx, cz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            if any(h[0] < cx < h[2] and h[1] < cz < h[3] for h in holes):
                continue
            a, b = xs[i], xs[i + 1]
            c, d = zs[j], zs[j + 1]
            if facing < 0:   # normal -Y: CCW seen from -Y means x increasing, z increasing
                _q(mb, (a, y, c), (b, y, c), (b, y, d), (a, y, d), mat)
            else:
                _q(mb, (b, y, c), (a, y, c), (a, y, d), (b, y, d), mat)


def reveal(mb, hole, depth, mat, y=0.0, bottom=True):
    """Inner side faces of an opening from the facade (y) back to y+depth."""
    x0, z0, x1, z1 = hole
    y1 = y + depth
    # left jamb (faces +x), right jamb (faces -x), head (faces -z), sill (faces +z)
    _q(mb, (x0, y, z0), (x0, y1, z0), (x0, y1, z1), (x0, y, z1), mat)
    _q(mb, (x1, y, z0), (x1, y, z1), (x1, y1, z1), (x1, y1, z0), mat)
    _q(mb, (x0, y, z1), (x0, y1, z1), (x1, y1, z1), (x1, y, z1), mat)
    if bottom:
        _q(mb, (x0, y, z0), (x1, y, z0), (x1, y1, z0), (x0, y1, z0), mat)


def frame(mb, hole, mat="M_Trim_White", w=FRAME_W, d=FRAME_D, bottom=True):
    """Picture frame around a hole, standing proud of the facade by d."""
    x0, z0, x1, z1 = hole
    y0 = -d
    bars = [(x0 - w, z1, x1 + w, z1 + w),          # head
            (x0 - w, z0 - (w if bottom else 0), x0, z1),   # left
            (x1, z0 - (w if bottom else 0), x1 + w, z1)]   # right
    if bottom:
        bars.append((x0 - w, z0 - w, x1 + w, z0))
    for bx0, bz0, bx1, bz1 in bars:
        mb.box(bx0, y0, bz0, bx1, 0.0, bz1, mat, skip=("+y",))


def sill(mb, hole, mat="M_Trim_White"):
    x0, z0, x1, z1 = hole
    mb.box(x0 - FRAME_W - 0.06, -SILL_D, z0 - FRAME_W - SILL_H, x1 + FRAME_W + 0.06, 0.0, z0 - FRAME_W, mat, skip=("+y",))


def glass(mb, hole, y, mat="M_Glass", mullions=(0, 0), mullion_mat="M_Trim_White", mw=0.06):
    """Glass pane at depth y with optional mullions (vertical count, horizontal count)."""
    x0, z0, x1, z1 = hole
    _q(mb, (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), mat)
    nv, nh = mullions
    for i in range(1, nv + 1):
        x = x0 + (x1 - x0) * i / (nv + 1)
        mb.box(x - mw / 2, y - 0.03, z0, x + mw / 2, y, z1, mullion_mat, skip=("+y",))
    for j in range(1, nh + 1):
        z = z0 + (z1 - z0) * j / (nh + 1)
        mb.box(x0, y - 0.03, z - mw / 2, x1, y, z + mw / 2, mullion_mat, skip=("+y",))


def window(mb, hole, wall_mat="M_Wall_Cream", glass_mat="M_Glass", frame_mat="M_Trim_White",
           mullions=(1, 1), with_sill=True):
    """Standard recessed window: reveal + glass + frame + sill."""
    reveal(mb, hole, REVEAL, wall_mat)
    glass(mb, hole, REVEAL, glass_mat, mullions=mullions, mullion_mat=frame_mat)
    frame(mb, hole, frame_mat)
    if with_sill:
        sill(mb, hole, frame_mat)


def door(mb, hole, wall_mat="M_Wall_Cream", door_mat="M_Door_Wood", frame_mat="M_Trim_White",
         glass_mat=None, panels=True):
    """Recessed door to floor level. If glass_mat, the upper part is glazed."""
    x0, z0, x1, z1 = hole
    reveal(mb, hole, REVEAL + 0.03, wall_mat, bottom=False)
    y = REVEAL + 0.03
    if glass_mat:
        zg = z0 + (z1 - z0) * 0.38
        _q(mb, (x0, y, z0), (x1, y, z0), (x1, y, zg), (x0, y, zg), door_mat)
        _q(mb, (x0, y, zg), (x1, y, zg), (x1, y, z1), (x0, y, z1), glass_mat)
        mb.box(x0, y - 0.04, zg - 0.04, x1, y, zg + 0.04, frame_mat, skip=("+y",))
    else:
        _q(mb, (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), door_mat)
        if panels:
            pw = (x1 - x0)
            for (a, b) in ((0.12, 0.45), (0.55, 0.88)):
                mb.box(x0 + pw * 0.15, y - 0.025, z0 + (z1 - z0) * a, x1 - pw * 0.15, y, z0 + (z1 - z0) * b,
                       door_mat, skip=("+y",))
    # knob
    kx = x1 - 0.14 if (x1 - x0) > 0.7 else (x0 + x1) / 2
    mb.box(kx - 0.03, y - 0.07, z0 + 1.0, kx + 0.03, y, z0 + 1.08, "M_Metal", skip=("+y",))
    frame(mb, hole, frame_mat, bottom=False)


def wall_module(mb, w=3.0, h=3.0, holes=(), mat="M_Wall_Cream", t=C.WALL_T, back=True, caps=True):
    """Wall body for one module: outer face (with holes) at y=0, inner face at y=t, end caps.

    Spans x in [-w/2, w/2], z in [0, h].
    """
    x0, x1 = -w / 2, w / 2
    panel(mb, x0, x1, 0.0, h, list(holes), mat, y=0.0, facing=-1)
    if back:
        panel(mb, x0, x1, 0.0, h, [], mat, y=t, facing=+1)
    if caps:
        # top & bottom caps, side caps
        _q(mb, (x0, 0, h), (x1, 0, h), (x1, t, h), (x0, t, h), mat)
        _q(mb, (x0, 0, 0), (x0, t, 0), (x1, t, 0), (x1, 0, 0), mat)
        _q(mb, (x0, 0, 0), (x0, 0, h), (x0, t, h), (x0, t, 0), mat)
        _q(mb, (x1, 0, 0), (x1, t, 0), (x1, t, h), (x1, 0, h), mat)


def bevelled(mb, width=0.03, angle=40.0):
    """Return a NEW MeshBuilder holding mb's geometry with sharp edges chamfered."""
    import bmesh
    import bpy
    tmp = mb.build("__tmp_bevel", weld=True, bevel=width, bevel_angle=angle)
    out = MeshBuilder()
    for poly in tmp.polygons:
        out.face([tmp.vertices[i].co.copy() for i in poly.vertices], tmp.materials[poly.material_index].name)
    bpy.data.meshes.remove(tmp)
    return out
