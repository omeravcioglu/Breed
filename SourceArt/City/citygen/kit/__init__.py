"""Modular building kit: registry, shelf layout, instancing and the kit sheet render.

Families live in sibling modules (walls.py, roofs.py, details.py, props.py). Each exposes
    build(K)   where K is this module; it calls K.add(...) once per piece.
See docs/KIT_SPEC.md for the exact piece list, dimensions and origin conventions.

Pieces are real mesh objects in the KIT_Library collection, parked on a "shelf" south of the
map. Buildings use linked duplicates (shared mesh data) so editing a kit mesh updates the city.
"""
import importlib
import math
import os
import sys
import traceback

import bpy
from mathutils import Vector

from .. import config as C
from .. import scene
from ..meshutil import MeshBuilder  # re-exported for family modules  # noqa: F401

KIT_ROOT = "KIT_Library"
FAMILIES = ["walls", "roofs", "details", "props", "nature"]
SHELF_Y0 = -560.0
SHELF_FAMILY = 70.0     # y spacing between family blocks
SHELF_SUBROW = 13.0     # y spacing between wrapped rows inside a family
SHELF_WRAP = 64.0       # wrap a row after this many meters

# Recolorable placeholder materials: assemblers swap these per instance (object-level link).
RECOLOR_SLOTS = {
    "M_Wall_Cream": "wall",
    "M_Trim_White": "trim",
    "M_Door_Wood": "door",
    "M_Awning_Red": "awning",
    "M_Roof_Slate": "roof",
    "M_Sign_Accent": "sign",
    "M_Foliage": "foliage",
}

REG = {}          # name -> dict(obj, family, category, dims, meta)
ERRORS = {}       # family -> traceback text
_cursor = {}      # family -> next shelf x


def add(name, mb, family, category="Misc", bevel=0.0, meta=None, weld=True):
    """Register a kit piece built with MeshBuilder *mb*. Returns the object."""
    if not name.startswith("KIT_"):
        name = "KIT_" + name
    if name in REG:
        raise ValueError(f"duplicate kit piece {name}")
    me = mb.build(name, weld=weld, bevel=bevel)
    o = bpy.data.objects.new(name, me)
    scene.coll(f"{family}/{category}", root=KIT_ROOT).objects.link(o)
    # dims from local bounds
    xs = [v.co.x for v in me.vertices] or [0]
    ys = [v.co.y for v in me.vertices] or [0]
    zs = [v.co.z for v in me.vertices] or [0]
    dims = dict(x=(round(min(xs), 3), round(max(xs), 3)), y=(round(min(ys), 3), round(max(ys), 3)),
                z=(round(min(zs), 3), round(max(zs), 3)))
    # shelf placement
    row = FAMILIES.index(family) if family in FAMILIES else -1   # "core" sits on its own row north of the shelf
    x, sub = _cursor.get(family, (0.0, 0))
    width = dims["x"][1] - dims["x"][0]
    if x > 0 and x + width > SHELF_WRAP:
        x, sub = 0.0, sub + 1
    # pieces hanging below their attach line (awnings, fire escapes...) are lifted onto the shelf
    o.location = (x - dims["x"][0], SHELF_Y0 - row * SHELF_FAMILY - sub * SHELF_SUBROW, max(0.0, -dims["z"][0]))
    _cursor[family] = (x + width + 2.0, sub)
    o["kit_family"] = family
    o["kit_category"] = category
    for k, v in (meta or {}).items():
        o[f"kit_{k}"] = v
    REG[name] = dict(obj=o, family=family, category=category, dims=dims, meta=meta or {},
                     tris=sum(len(p.vertices) - 2 for p in me.polygons))
    return o


def build_kit(families=None):
    REG.clear()
    ERRORS.clear()
    _cursor.clear()
    for fam in (families or (["core"] + FAMILIES)):
        try:
            mod = importlib.import_module(f"{__name__}.{fam}")
            mod.build(sys.modules[__name__])
        except ModuleNotFoundError as e:
            if fam in str(e):
                ERRORS[fam] = f"family module {fam}.py not present yet"
            else:
                ERRORS[fam] = traceback.format_exc()
        except Exception:
            ERRORS[fam] = traceback.format_exc()
            print(f"[kit] family {fam} FAILED\n{ERRORS[fam]}")
    return REG


def get(name):
    if not name.startswith("KIT_"):
        name = "KIT_" + name
    r = REG.get(name)
    if r is None:
        o = bpy.data.objects.get(name)
        if o is None:
            raise KeyError(f"kit piece {name} missing")
        return o
    return r["obj"]


def has(name):
    if not name.startswith("KIT_"):
        name = "KIT_" + name
    return name in REG


def instance(name, path, loc=(0, 0, 0), rot_z=0.0, parent=None, recolor=None, scale=None, inst_name=None, root=scene.ROOT):
    """Linked duplicate of kit piece *name*. recolor: {'wall': 'M_Wall_Sky', ...}."""
    src = get(name)
    o = bpy.data.objects.new(inst_name or src.name.replace("KIT_", "", 1), src.data)
    scene.coll(path, root=root).objects.link(o)
    if parent is not None:
        o.parent = parent
    o.location = Vector(loc)
    o.rotation_euler = (0.0, 0.0, rot_z)
    if scale is not None:
        o.scale = scale
    if recolor:
        from .. import palette
        for i, slot in enumerate(o.material_slots):
            m = src.data.materials[i] if i < len(src.data.materials) else None
            if m is None:
                continue
            role = RECOLOR_SLOTS.get(m.name)
            if role and role in recolor and recolor[role] != m.name:
                slot.link = "OBJECT"
                slot.material = palette.get(recolor[role])
    return o


def manifest():
    return {n: dict(family=r["family"], category=r["category"], dims=r["dims"], tris=r["tris"])
            for n, r in sorted(REG.items())}


def render_sheet(path, family=None):
    """Render the kit shelf (all families, or one) with EEVEE from a 3/4 front view."""
    from .. import render as R
    bpy.context.view_layer.update()
    objs = [r["obj"] for r in REG.values() if family in (None, r["family"])]
    if not objs:
        return None
    pts = []
    for o in objs:
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z1 = max(p.z for p in pts)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    span = max(x1 - x0, (y1 - y0) * 1.6, 12.0)
    # ground plane under the shelf
    gname = "KIT_ShelfGround"
    if bpy.data.objects.get(gname) is None:
        mb = MeshBuilder()
        y_lo = SHELF_Y0 - (len(FAMILIES) + 1) * SHELF_FAMILY - 100
        y_hi = SHELF_Y0 + SHELF_FAMILY + 40
        mb.face([(-500, y_lo, -0.01), (700, y_lo, -0.01), (700, y_hi, -0.01), (-500, y_hi, -0.01)], "M_Concrete")
        g = bpy.data.objects.new(gname, mb.build(gname))
        scene.coll("Shelf", root=KIT_ROOT).objects.link(g)
    dist = span * 0.95
    loc = (cx, cy - dist, max(z1, 4.0) * 0.6 + dist * 0.5)
    tgt = (cx, cy, max(z1, 3.0) * 0.3)
    res = (2400, 1100) if family is None else (2200, 1100)
    return R.view(path, loc, tgt, lens=35, res=res, name="CAM_KitSheet", hide=(), show=())
