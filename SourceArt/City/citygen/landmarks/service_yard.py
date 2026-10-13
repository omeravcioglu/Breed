"""Phase 4 landmark: CONTAINER YARD (ServiceYard, Dock Yard loop) + NET YARD (NetYard, Wharf quay).

Both sites are built here; the shared custom-geometry helpers at the top are also used by
hiding_spots.py (tarp piles, logs, scoped sub-collections, linked duplicates).

CONTAINER YARD  (LANDMARKS["ServiceYard"], centre (314, -58), ~24 x 48 m, inside the gravel Dock Yard
loop: Dock Bridge Rd west, Canal St north, Cannery Row east + south)
---------------------------------------------------------------------------------------------------
The site has no facing, so the site frame is world-aligned (local = world - centre). The long axis
runs north-south. Plan, south (street / gate) to north:

  y -26..-12  APRON (concrete): truck GATE in the south fence toward Cannery Row (7.5 m opening;
              its x is picked so the approach is free of the generic Dock Yard sheds), overhead
              "container yard" sign gantry (4.2 m clearance bar) whose posts are the gate posts,
              raised boom barrier, telescopic sliding leaves parked open inside the fence;
              SITE OFFICE (kit shed 2x2 via the assembler) in the SW corner, door + canopy facing
              the apron, bench / bin / dumpster / tyre stack / guard-dog doghouse - the 1 m gap
              behind it along the fence is a squeeze hiding spot; LOADING BAY on the east fence
              (raised concrete dock, bumpers, leveller, steps, rail) with the box TRUCK backed up to
              it; FORKLIFT (custom) crossing the apron with a pallet of crates on its forks.
  y -12..+17  THE MAZE: two double rows of KIT_Container_6m (recoloured, stacks 1-3 high, slight
              jitter) running north-south, a 5 m MAIN LANE between them (yellow lane lines) and
              3-5 m perimeter lanes outside. Cross passages are staggered (west row at y ~1, east
              row at y ~-5 and ~10) so chases zig-zag; stack heights step 1-2-3 so climbing animals
              get a parkour route. One OPEN CONTAINER (custom, doors swung into the east cross
              passage, timber floor, dark interior) is the signature hiding hole. Every upper-tier
              box gets a dark bottom-rail plate (linked duplicates of one mesh) because the kit
              container has no bottom face: without it a jittered box that overhangs the one below
              is see-through from the lanes once backfaces are culled (Unity).
  y ~8        GANTRY CRANE (custom RTG, girders at 13 m, beacon at ~15.5 m, yellow): legs in the
              outer lanes straddling both rows and the main lane, an orange container hanging from
              the spreader 5 m over the main lane (underside plate so it is not see-through from
              below), operator cab, engine house on the east sill, name boards on the girders.
              Signature silhouette of the docks, readable from across the canal and the far corners
              of the map. Small animals slip under the sill beams, players go round.
  y 17..23    NORTH LANE: cross-stacked container + crate / pallet / barrel / tyre clutter in the
              corners, and the BROKEN GAP: one fence panel missing, pushed in flat onto the yard
              ("something broke in here").
  Perimeter   KIT_Fence_Chain_3m on the polygon inset 0.5 m with three openings: truck gate (S),
              pedestrian gap with posts (W side preferred, else E; the first candidate whose outside
              approach is free of World lots - currently y ~-9 because a warehouse hugs the west
              fence further north) and the broken gap (N). Four custom FLOODLIGHT masts (10 m,
              linked duplicates) aimed into the yard.
Ground: asphalt slab over the stacking area, concrete apron in the south (slab top PAVE_Z = 0.03).
Everything stands on the slab top, so nothing sinks into or floats over the gravel.

NET YARD  (NO_BUILD "NetYard", ~28 x 13 m parallelogram on the Wharf quay between Riverside Drive
and the canal, a warehouse 1-3 m to the east)
---------------------------------------------------------------------------------------------------
Frame rotated so local X runs along the long edge and local -Y faces Riverside Drive (the entrance
side); +Y looks to the canal. Packed-dirt pad with a soft hand-made edge.
  east end    NET SHED (kit shed 2x2, gable roof, barn red, teal door) on a plank deck with a bench,
              rope coil, lamp post and a life ring by the door; a string of fishing BUOYS on its
              west gable wall; the strip behind it (canal side, half screened by crates) and the
              gap to the warehouse are hiding gaps.
  middle      two NET RACKS (timber rails, pleated nets with cork lines + lead-line floats) and four
              lumpy NET PILES with float lines: soft cover for otters / crabs.
  west end    LOBSTER-POT towers (one custom pot, linked duplicates, recoloured), an UPTURNED
              DINGHY on trestles (crawl-under hiding spot), crate stacks, barrels, pallets and the
              timber YARD SIGN with a fish pictogram facing the street.
The street side stays open (it is an open yard reached from Riverside Drive).

Hiding spots: DockYardContainers and NetYard lie inside these sites, so hiding_spots.py skips them
(the open container, the office gap, the sill beams, the dinghy and the shed strip are the hides).
register_hide() publishes the main designed-in hide points (OpenContainer; NetPilePocket, UnderDinghy) in
ctx["lm_hides"]; hiding_spots reports the nearest one as that spot's machine-readable anchor.

Budgets: custom tris ~3.9k (Container Yard; gantry 1.3k, forklift 0.6k, gate sign 0.5k) and ~5.7k
(Net Yard; racks 0.75k each, piles 0.5k each, buoys 0.56k). Repeated pieces (floodlights, gate posts,
lobster pots, tyre stacks, tarp piles) are linked duplicates of one mesh. Every custom solid is closed
or ends inside another closed part and faces are oriented outward from each part's centre (checked with
backface culling on: no holes, no inside-out islands).

WORKAROUND (framework): scene.coll() resolves each path segment by its global collection name, so a
plain sub like "Ground" / "Gate" / "Clutter" is shared between sites (objects land in whichever site
created it first). scoped(S) prefixes every sub with the site id.
"""
import math
import random

import bpy
from mathutils import Euler, Matrix, Vector

from .. import facade as F
from .. import geom2d as G
from .. import palette
from .. import scene
from ..assembler import BuildingSpec, H3
from ..meshutil import MeshBuilder

TAU = 2 * math.pi


# =============================================================================== geometry helpers
def newell(P):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def fo(mb, pts, inside, mat, inward=False):
    """Polygon whose normal points away from *inside* (or toward it when inward=True)."""
    P = [Vector(p) for p in pts]
    if len(P) < 3:
        return
    c = sum(P, Vector((0.0, 0.0, 0.0))) / len(P)
    d = newell(P).dot(c - Vector(inside))
    if (d < 0) != inward:
        P.reverse()
    mb.face(P, mat)


def bx(mb, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, skip=()):
    s = MeshBuilder()
    s.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
    if bevel > 0:
        s = F.bevelled(s, bevel)
    mb.extend(s)


def xf(mb, sub, loc=(0, 0, 0), rot=(0, 0, 0)):
    mb.extend(sub, matrix=Matrix.Translation(Vector(loc)) @ Euler(rot, "XYZ").to_matrix().to_4x4())


def strut(mb, a, b, w, d, mat):
    """Square-section bar from 3D point a to b (w across, d in the second direction)."""
    a, b = Vector(a), Vector(b)
    ax = (b - a)
    if ax.length < 1e-6:
        return
    ax.normalize()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.95 else Vector((0, 1, 0))
    u = ax.cross(up).normalized()
    v = u.cross(ax).normalized()
    ring = lambda p: [p + u * w / 2 + v * d / 2, p - u * w / 2 + v * d / 2, p - u * w / 2 - v * d / 2,
                      p + u * w / 2 - v * d / 2]
    A, B = ring(a), ring(b)
    c = (a + b) / 2
    for i in range(4):
        j = (i + 1) % 4
        fo(mb, [A[i], A[j], B[j], B[i]], c, mat)
    fo(mb, A, c, mat)
    fo(mb, B, c, mat)


def cyl(mb, center, axis, r, length, mat, seg=8, cap_mat=None, r2=None, caps=(True, True)):
    """Cylinder centred at *center* along 'x' | 'y' | 'z'."""
    s = MeshBuilder()
    s.cylinder(0, 0, -length / 2, length / 2, r, mat, seg=seg, cap_top=caps[1], cap_bottom=caps[0],
               mat_cap=cap_mat, r_top=r2)
    rot = {"x": (0, math.pi / 2, 0), "y": (-math.pi / 2, 0, 0), "z": (0, 0, 0)}[axis]
    xf(mb, s, center, rot)


def ball(mb, c, r, mat, seg=8, rings=5, sz=1.0):
    mb.sphere(c[0], c[1], c[2], r, mat, seg=seg, rings=rings, sz=sz)


def obox(mb, center, fwd, length, width, z0, z1, mat):
    """Box with a 2D footprint: *length* along fwd, *width* across (closed, bottom included)."""
    f = Vector(fwd).normalized()
    r = Vector((f.y, -f.x))
    c = Vector(center)
    P = [c + f * length / 2 + r * width / 2, c - f * length / 2 + r * width / 2,
         c - f * length / 2 - r * width / 2, c + f * length / 2 - r * width / 2]
    mb.prism([(p.x, p.y) for p in P], z0, z1, mat, mat, bottom=mat)


def dome(mb, cx, cy, rx, ry, h, mat, rng, seg=10, noise=0.12, z0=0.0, profile=None):
    """Lumpy closed mound (bottom cap included) - net piles, bushes of stuff, tarp heaps."""
    prof = profile or [(1.0, 0.0), (0.97, 0.22), (0.82, 0.55), (0.52, 0.86), (0.0, 1.0)]
    nz = [rng.uniform(1 - noise, 1 + noise) for _ in range(seg)]
    rings = []
    for k, (rs, zs) in enumerate(prof[:-1]):
        row = []
        for i in range(seg):
            a = TAU * i / seg
            jit = nz[i] * rng.uniform(1 - noise * 0.5, 1 + noise * 0.5) if k else nz[i]
            row.append(Vector((cx + math.cos(a) * rx * rs * jit, cy + math.sin(a) * ry * rs * jit,
                               z0 + h * zs * (rng.uniform(0.9, 1.1) if k else 1.0))))
        rings.append(row)
    top = Vector((cx, cy, z0 + h * prof[-1][1]))
    inside = Vector((cx, cy, z0 + h * 0.3))
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            fo(mb, [rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]], inside, mat)
    for i in range(seg):
        j = (i + 1) % seg
        fo(mb, [rings[-1][i], rings[-1][j], top], inside, mat)
    fo(mb, rings[0], inside, mat)


def inset_poly(P, d):
    """Mitred inset of a simple polygon by d (any winding)."""
    P = [G.V(p) for p in P]
    n = len(P)
    sgn = 1.0 if G.poly_area(P) > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % n]
        a, b = (p1 - p0).normalized(), (p2 - p1).normalized()
        na = Vector((-a.y, a.x)) * sgn
        nb = Vector((-b.y, b.x)) * sgn
        m = na + nb
        m = m.normalized() if m.length > 1e-6 else na
        k = d / max(m.dot(na), 0.35)
        out.append(p1 + m * k)
    return out


# =============================================================================== instancing
def _sub(S, sub):
    """Site-unique sub-collection name. WORKAROUND: scene.coll() resolves every path segment by its
    GLOBAL collection name, so a plain sub like "Ground" / "Gate" / "Clutter" is shared with the first
    site that created it and our objects would land in that site's hierarchy."""
    if not sub:
        return sub
    return sub if sub.startswith(S.id + "_") else f"{S.id}_{sub}"


def scoped(S):
    """Patch S.put / S.mesh (and thereby S.paving, S.fence_along, S.scatter) to use site-unique subs."""
    if getattr(S, "_scoped", False):
        return S
    put, mesh = S.put, S.mesh
    S.put = lambda *a, sub=None, **k: put(*a, sub=_sub(S, sub), **k)
    S.mesh = lambda name, mb, sub=None, **k: mesh(name, mb, sub=_sub(S, sub), **k)
    S._scoped = True
    return S


def dup(S, src, name, x, y, z, rot=0.0, sub=None, recolor=None, local=False, scale=None):
    """Linked duplicate of one of our custom mesh objects (shares mesh data like kit instances).

    recolor: palette material replacing the M_Awning_Red placeholder slot (object-level link).
    """
    if local:
        p = S.to_world(x, y)
        x, y, rot = p.x, p.y, rot + S.rot
    S.n += 1
    o = bpy.data.objects.new(f"LM_{S.id}_{name}_{S.n:03d}"[:63], src.data)
    sub = _sub(S, sub)
    scene.coll(S.coll + (f"/{sub}" if sub else "")).objects.link(o)
    o.location = (x, y, z)
    o.rotation_euler = (0.0, 0.0, rot)
    if scale:
        o.scale = scale
    if recolor:
        for i, slot in enumerate(o.material_slots):
            m = src.data.materials[i]
            if m is not None and m.name == "M_Awning_Red":
                slot.link = "OBJECT"
                slot.material = palette.get(recolor)
    return o


def place(S, name, mb, x, y, z, rot=0.0, sub=None, local=True):
    """Custom mesh with its own local origin, placed at site-local (x, y) and rotated."""
    if local:
        p = S.to_world(x, y)
        x, y, rot = p.x, p.y, rot + S.rot
    full = f"LM_{S.id}_{name}"
    if bpy.data.objects.get(full[:63]) is not None:
        S.n += 1
        name = f"{name}_{S.n:03d}"
    o = S.mesh(name, mb, sub=sub, loc=(x, y, z))
    o.rotation_euler = (0.0, 0.0, rot)
    return o


# =============================================================================== custom pieces
YEL, YEL_D, DARK, TIRE = "M_Hazard", "M_Hazard_Dark", "M_Trim_Dark", "M_Hazard_Dark"
METAL, METAL_D, WHITE, GLASS = "M_Metal", "M_Metal_Dark", "M_Wall_White", "M_Glass"
PLACE = "M_Awning_Red"     # recolour placeholder for our duplicated pieces


def gantry_mb(span=20.6, base=7.6, h=13.0, tx=0.0):
    """Rubber-tyred gantry crane. Origin = ground centre; span along X, travel along Y.

    tx: trolley position along X. The spreader hangs at z 7.6..7.9 (a container goes below it).
    """
    mb = MeshBuilder()
    lx, ly = span / 2, base / 2
    for sx in (-1, 1):
        x = sx * lx
        bx(mb, x - 0.42, -ly - 0.95, 0.85, x + 0.42, ly + 0.95, 1.55, YEL, bevel=0.06)      # sill beam
        for sy in (-1, 1):
            yc = sy * (ly + 0.25)
            bx(mb, x - 0.33, yc - 1.0, 0.5, x + 0.33, yc + 1.0, 0.86, METAL_D)                # bogie
            for k in (-1, 1):
                cyl(mb, (x, yc + k * 0.52, 0.5), "x", 0.5, 0.52, TIRE, seg=10, cap_mat=METAL_D)
            strut(mb, (x, sy * ly, 1.5), (x, sy * (ly - 0.1), h - 1.1), 0.72, 0.72, YEL)       # leg
            for zb in (1.75, 2.45):                                                          # hazard bands
                bx(mb, x - 0.4, sy * ly - 0.4, zb, x + 0.4, sy * ly + 0.4, zb + 0.35, YEL_D)
        bx(mb, x - 0.28, -ly, 7.6, x + 0.28, ly, 8.15, YEL)                                  # mid tie
        strut(mb, (x, -ly + 0.3, 1.6), (x, ly - 0.3, 7.6), 0.22, 0.22, YEL)                  # diagonal
        bx(mb, x - 0.5, -ly - 0.55, h - 1.25, x + 0.5, ly + 0.55, h - 0.1, YEL, bevel=0.06)  # end tie
    for sy in (-1, 1):
        y = sy * ly
        bx(mb, -lx - 0.75, y - 0.42, h - 1.15, lx + 0.75, y + 0.42, h, YEL, bevel=0.06)      # girder
        bx(mb, -lx + 0.3, y - 0.09, h, lx - 0.3, y + 0.09, h + 0.12, METAL_D)                # rail
        # name board on the outer face of each girder (white panel + dark word bars)
        yo = y + sy * 0.42
        bx(mb, -5.2, min(yo, yo + sy * 0.06), h - 1.0, 5.2, max(yo, yo + sy * 0.06), h - 0.15, "M_Sign_Face")
        yl = yo + sy * 0.06
        for x0, x1 in ((-4.6, -2.2), (-1.8, 0.6), (1.0, 4.6)):
            bx(mb, x0, min(yl, yl + sy * 0.04), h - 0.75, x1, max(yl, yl + sy * 0.04), h - 0.4, "M_Sign_Board")
    # trolley + machinery house + beacon
    bx(mb, tx - 1.7, -ly - 0.6, h + 0.12, tx + 1.7, ly + 0.6, h + 1.3, YEL, bevel=0.07)
    bx(mb, tx - 1.25, -2.5, h + 1.3, tx + 1.25, 2.5, h + 2.15, WHITE, bevel=0.06)
    bx(mb, tx - 1.28, -1.6, h + 1.45, tx + 1.28, 1.6, h + 1.95, DARK)                         # vent band
    bx(mb, tx - 0.16, -0.16, h + 2.15, tx + 0.16, 0.16, h + 2.45, "M_Hazard_Orange")
    # operator cab hanging off the trolley (+X side), between the girders
    bx(mb, tx + 1.3, -0.5, h - 0.4, tx + 1.9, 0.5, h + 0.2, YEL)                              # hanger
    bx(mb, tx + 1.7, -1.0, h - 2.5, tx + 3.6, 1.0, h - 0.35, WHITE, bevel=0.06)
    bx(mb, tx + 1.62, -1.05, h - 2.0, tx + 3.68, 1.05, h - 0.9, GLASS)                         # glass band
    bx(mb, tx + 1.6, -1.1, h - 0.4, tx + 3.7, 1.1, h - 0.25, YEL)                             # cab roof
    # underside plate for the hanging kit container (its open bottom is visible from below): 1.5 cm
    # proud of its walls (container 2.44 x 6.1, rotated onto Y) so no slit is left and no face is coplanar
    bx(mb, tx - 1.235, -3.065, 4.985, tx + 1.235, 3.065, 5.025, METAL_D)
    # spreader + cables
    bx(mb, tx - 1.3, -3.15, 7.6, tx + 1.3, 3.15, 7.95, YEL, bevel=0.04)
    bx(mb, tx - 0.5, -1.2, 7.95, tx + 0.5, 1.2, 8.35, YEL_D)
    for cxx in (-1.0, 1.0):
        for cyy in (-2.7, 2.7):
            strut(mb, (tx + cxx * 0.85, cyy * 0.95, 7.9), (tx + cxx * 1.0, cyy, h + 0.15), 0.08, 0.08, METAL_D)
    # engine house on the +X sill
    bx(mb, lx - 0.75, -2.0, 1.5, lx + 0.75, 2.0, 3.5, WHITE, bevel=0.07)
    bx(mb, lx + 0.72, -1.4, 2.0, lx + 0.8, 1.4, 3.0, DARK)                                    # grille
    bx(mb, lx - 0.3, -1.4, 3.5, lx + 0.3, -0.9, 3.65, YEL)
    cyl(mb, (lx + 0.3, 1.4, 4.1), "z", 0.1, 1.2, METAL_D, seg=6)
    return mb


def forklift_mb():
    """Chunky counterbalance forklift. Origin bottom centre, forks point to -Y."""
    B, CW = "M_Hazard_Orange", DARK
    mb = MeshBuilder()
    bx(mb, -0.56, -0.85, 0.3, 0.56, 0.95, 1.0, B, bevel=0.07)                 # body
    bx(mb, -0.6, 0.8, 0.28, 0.6, 1.38, 1.25, CW, bevel=0.12)                  # counterweight
    bx(mb, -0.5, -0.92, 0.95, 0.5, -0.5, 1.3, B, bevel=0.05)                  # cowl / dash
    bx(mb, -0.27, 0.22, 1.0, 0.27, 0.62, 1.2, CW, bevel=0.04)                 # seat
    bx(mb, -0.27, 0.6, 1.0, 0.27, 0.74, 1.68, CW, bevel=0.03)                 # back rest
    strut(mb, (0.0, -0.62, 1.3), (0.0, -0.4, 1.55), 0.05, 0.05, CW)            # steering column
    cyl(mb, (0.0, -0.38, 1.58), "z", 0.17, 0.05, CW, seg=8)
    for x in (-0.5, 0.5):                                                    # overhead guard
        strut(mb, (x, -0.62, 1.2), (x, -0.5, 2.18), 0.08, 0.08, CW)
        strut(mb, (x, 1.0, 1.15), (x, 1.0, 2.18), 0.08, 0.08, CW)
    bx(mb, -0.58, -0.62, 2.14, 0.58, 1.08, 2.22, CW)
    for y in (-0.25, 0.15, 0.55):
        bx(mb, -0.5, y - 0.05, 2.22, 0.5, y + 0.05, 2.26, CW)
    bx(mb, -0.08, 0.75, 2.22, 0.08, 0.91, 2.38, "M_Hazard")                    # beacon
    for x in (-0.36, 0.36):                                                  # mast
        bx(mb, x - 0.06, -1.12, 0.15, x + 0.06, -0.98, 2.4, METAL_D)
    bx(mb, -0.42, -1.12, 2.25, 0.42, -0.98, 2.37, METAL_D)
    bx(mb, -0.52, -1.24, 0.5, 0.52, -1.12, 1.15, METAL_D)                     # carriage
    for x in (-0.3, 0.3):                                                    # forks
        bx(mb, x - 0.06, -2.3, 0.45, x + 0.06, -1.12, 0.52, METAL)
        bx(mb, x - 0.06, -1.25, 0.45, x + 0.06, -1.12, 1.1, METAL)
    for x in (-0.56, 0.56):
        cyl(mb, (x, -0.55, 0.33), "x", 0.33, 0.28, TIRE, seg=10, cap_mat=METAL)
    for x in (-0.5, 0.5):
        cyl(mb, (x, 1.0, 0.27), "x", 0.27, 0.24, TIRE, seg=10, cap_mat=METAL)
    return mb


def flood_mast_mb(h=10.0):
    """Floodlight mast: concrete footing, tapered pole, crossbar with 3 lamps aimed down toward -Y."""
    mb = MeshBuilder()
    bx(mb, -0.38, -0.38, -0.25, 0.38, 0.38, 0.4, "M_Concrete", bevel=0.05)
    mb.cylinder(0, 0, 0.4, h, 0.16, METAL, seg=8, r_top=0.1)
    bx(mb, -0.95, -0.1, h - 0.05, 0.95, 0.1, h + 0.12, METAL_D)
    bx(mb, -0.08, -0.22, h - 0.5, 0.08, 0.05, h - 0.05, METAL_D)
    for x in (-0.65, 0.0, 0.65):
        s = MeshBuilder()
        bx(s, -0.26, -0.18, -0.2, 0.26, 0.2, 0.2, DARK, bevel=0.03)
        bx(s, -0.21, -0.22, -0.15, 0.21, -0.17, 0.15, "M_Light_Emit")
        xf(mb, s, (x, -0.3, h + 0.25), (math.radians(38), 0, 0))
    return mb


def dock_mb(L=8.0, D=2.8, H=1.2):
    """Raised loading dock. Front (truck side) faces -Y; x in [-L/2, L/2], y in [0, D]; steps at +X."""
    mb = MeshBuilder()
    bx(mb, -L / 2, 0.0, -0.15, L / 2, D, H, "M_Concrete", bevel=0.04)
    n = 10
    for i in range(n):                                        # hazard edge band on the front face
        x0 = -L / 2 + 0.1 + (L - 0.2) * i / n
        x1 = -L / 2 + 0.1 + (L - 0.2) * (i + 1) / n
        bx(mb, x0, -0.03, H - 0.2, x1, 0.0, H - 0.03, YEL if i % 2 == 0 else YEL_D, skip=("+y",))
    for x in (-L / 2 + 1.2, -0.9, 0.9, L / 2 - 1.2):           # rubber bumpers
        bx(mb, x - 0.2, -0.2, 0.45, x + 0.2, 0.0, 1.0, YEL_D, bevel=0.03, skip=("+y",))
    bx(mb, -1.0, 0.0, H, 1.0, 1.7, H + 0.04, METAL)            # dock leveller
    for k in range(4):                                        # steps up the +X end
        hgt = H * (k + 1) / 4.0
        bx(mb, L / 2 - 0.02, D - 1.4, -0.1, L / 2 + 0.32 * (4 - k), D - 0.15, hgt, "M_Concrete")
    for x in (-L / 2 + 0.25, L / 2 - 0.25):                    # safety rail posts at the back corners
        bx(mb, x - 0.05, D - 0.3, H, x + 0.05, D - 0.2, H + 1.0, YEL)
    bx(mb, -L / 2 + 0.2, D - 0.3, H + 0.92, L / 2 - 0.2, D - 0.2, H + 1.02, YEL)
    return mb


def gate_sign_mb(width=9.0, h=5.7):
    """Overhead yard sign over the truck gate. X along the fence, the lettered face looks -Y."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        x = sx * width / 2
        bx(mb, x - 0.3, -0.3, -0.2, x + 0.3, 0.3, 0.25, "M_Concrete", bevel=0.04)
        bx(mb, x - 0.17, -0.17, 0.25, x + 0.17, 0.17, h + 0.15, DARK, bevel=0.03)
        bx(mb, x - 0.2, -0.2, h + 0.15, x + 0.2, 0.2, h + 0.27, YEL)
    W = width / 2 - 0.17
    bx(mb, -W, -0.14, h - 1.2, W, 0.14, h, "M_Sign_Board", bevel=0.03)          # board frame
    for sy in (-1, 1):                                                          # both faces
        y0 = sy * 0.14
        bx(mb, -W + 0.25, min(y0, y0 + sy * 0.03), h - 1.05, W - 0.25, max(y0, y0 + sy * 0.03), h - 0.15,
           "M_Sign_Face")
    yl = -0.17
    for x0, x1, z0, z1 in ((-2.6, -0.4, h - 0.62, h - 0.32), (-0.1, 1.6, h - 0.62, h - 0.32),
                           (1.9, 2.9, h - 0.62, h - 0.32), (-2.0, 2.2, h - 0.92, h - 0.78)):
        bx(mb, x0, yl - 0.03, z0, x1, yl, z1, "M_Sign_Board", skip=("+y",))
    for x, mat in ((-W + 0.85, "M_Awning_Red"), (W - 0.85, "M_Awning_Blue")):   # container pictograms
        bx(mb, x - 0.45, yl - 0.04, h - 0.85, x + 0.45, yl, h - 0.33, mat, skip=("+y",))
        for k in range(3):
            xr = x - 0.3 + 0.3 * k
            bx(mb, xr - 0.04, yl - 0.07, h - 0.8, xr + 0.04, yl - 0.04, h - 0.38, mat, skip=("+y",))
    n = 12
    for i in range(n):                                                          # clearance bar
        x0 = -W + 2 * W * i / n
        x1 = -W + 2 * W * (i + 1) / n
        bx(mb, x0, -0.1, h - 1.5, x1, 0.1, h - 1.25, YEL if i % 2 == 0 else YEL_D)
    return mb


def boom_mb(angle=78.0, L=4.2):
    """Boom barrier: post box at the origin, arm hinged at z 1.0 toward +X, raised by *angle*."""
    mb = MeshBuilder()
    bx(mb, -0.25, -0.25, 0.0, 0.25, 0.25, 1.1, WHITE, bevel=0.04)
    bx(mb, -0.27, -0.27, 0.85, 0.27, 0.27, 0.95, "M_Door_Red")
    a = math.radians(angle)
    d = Vector((math.cos(a), 0.0, math.sin(a)))
    p0 = Vector((0.15, -0.32, 1.0))
    n = 6
    for i in range(n):
        strut(mb, p0 + d * (L * i / n), p0 + d * (L * (i + 1) / n), 0.12, 0.09,
              "M_Door_Red" if i % 2 == 0 else "M_Sign_Face")
    bx(mb, 0.05, -0.38, 0.85, 0.3, -0.25, 1.15, DARK)
    return mb


def open_container_mb(L=6.1, D=2.44, H=2.6, door_deg=112.0):
    """Container with its +X doors swung open (walk-in hiding hole). Body uses the PLACE colour."""
    mb = MeshBuilder()
    hx, hy, t = L / 2, D / 2, 0.08
    # outer shell (open at +X)
    mb.box(-hx, -hy, 0.0, hx, hy, H, PLACE, skip=("+x", "-z"))
    # inner shell, normals toward the inside
    xi0, xi1, yi0, yi1, zi0, zi1 = -hx + t, hx, -hy + t, hy - t, 0.1, H - t
    I = [Vector(v) for v in [(xi0, yi0, zi0), (xi1, yi0, zi0), (xi1, yi1, zi0), (xi0, yi1, zi0),
                             (xi0, yi0, zi1), (xi1, yi0, zi1), (xi1, yi1, zi1), (xi0, yi1, zi1)]]
    ci = Vector(((xi0 + xi1) / 2, 0, (zi0 + zi1) / 2))
    fo(mb, [I[0], I[1], I[2], I[3]], ci, "M_Door_Wood", inward=True)       # timber floor
    fo(mb, [I[4], I[5], I[6], I[7]], ci, METAL_D, inward=True)
    fo(mb, [I[0], I[1], I[5], I[4]], ci, METAL_D, inward=True)
    fo(mb, [I[3], I[2], I[6], I[7]], ci, METAL_D, inward=True)
    fo(mb, [I[0], I[3], I[7], I[4]], ci, METAL_D, inward=True)
    # door-end rim joining the two shells (faces +X)
    O = [Vector((hx, -hy, 0.0)), Vector((hx, hy, 0.0)), Vector((hx, hy, H)), Vector((hx, -hy, H))]
    Ii = [Vector((hx, yi0, 0.0)), Vector((hx, yi1, 0.0)), Vector((hx, yi1, zi1)), Vector((hx, yi0, zi1))]
    ref = Vector((hx - 1.0, 0, H / 2))
    fo(mb, [O[0], Ii[0], Ii[3], O[3]], ref, PLACE)
    fo(mb, [Ii[1], O[1], O[2], Ii[2]], ref, PLACE)
    fo(mb, [Ii[3], Ii[2], O[2], O[3]], ref, PLACE)
    fo(mb, [Vector((hx, yi0, 0.0)), Vector((hx, yi1, 0.0)), Vector((hx, yi1, zi0)), Vector((hx, yi0, zi0))],
       ref, "M_Door_Wood")
    # floor sill under the rim
    # ribs on the long sides + corner posts
    for i in range(8):
        x = -hx + 0.45 + (L - 0.9) * i / 7
        for sy in (-1, 1):
            y0 = sy * hy
            bx(mb, x - 0.09, min(y0, y0 + sy * 0.05), 0.12, x + 0.09, max(y0, y0 + sy * 0.05), H - 0.12, PLACE,
               skip=("+y",) if sy < 0 else ("-y",))
    for x in (-hx, hx - 0.16):
        for sy in (-1, 1):
            bx(mb, x - 0.02, sy * hy - 0.08 - 0.02 * sy, -0.0, x + 0.18, sy * hy + 0.08 - 0.02 * sy, H + 0.02, DARK)
    # door leaves hinged at (hx, +-hy), swung outward
    a = math.radians(door_deg)
    for sy in (-1, 1):
        hinge = Vector((hx + 0.04, sy * (hy - 0.02)))
        d = Vector((math.sin(a), -sy * math.cos(a)))
        cen = hinge + d * (hy - 0.06) / 2
        obox(mb, cen, d, hy - 0.06, 0.07, 0.06, H - 0.06, PLACE)
        for k in (0.25, 0.75):                                               # locking bars
            p = hinge + d * (hy - 0.06) * k
            nrm = Vector((-d.y, d.x)) * (1 if sy > 0 else -1)
            obox(mb, p + nrm * 0.06, d, 0.06, 0.05, 0.15, H - 0.15, METAL)
    return mb


def net_rack_mb(rng, L=5.0, H=2.0, mats=("M_Door_Teal", "M_Door_Navy")):
    """Timber net-drying rack along X with nets draped over the top rail. Origin bottom centre.

    Each net is a closed fold-pleated prism over the rail (accordion folds catch the light), with a
    scalloped hem, a cork line of floats along the rail and white lead-line floats on the hem."""
    mb = MeshBuilder()
    W = "M_Fence_Wood"
    for x in (-L / 2, 0.0, L / 2):
        strut(mb, (x, 0, 0.0), (x, 0, H + 0.1), 0.14, 0.14, W)
        for sy in (-1, 1):
            strut(mb, (x, sy * 0.55, 0.0), (x, sy * 0.05, H * 0.55), 0.09, 0.09, W)
    bx(mb, -L / 2 - 0.25, -0.07, H - 0.02, L / 2 + 0.25, 0.07, H + 0.12, W)
    spans = [(-L / 2 + 0.15, -0.15, mats[0]), (0.15, L / 2 - 0.4, mats[1])]
    for x0, x1, mat in spans:
        n = max(4, int((x1 - x0) / 0.28))
        ph = rng.uniform(0, 3)
        apex, Lft, Rgt = [], [], []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            zh = 0.3 + 0.32 * abs(math.sin(i * 0.8 + ph)) + rng.uniform(-0.06, 0.06)
            fold = 0.09 + (0.2 if i % 2 else 0.0) * rng.uniform(0.8, 1.2)
            apex.append(Vector((x, 0.0, H + 0.17)))
            Lft.append(Vector((x, -fold - 0.06, zh)))
            Rgt.append(Vector((x, fold + 0.06, zh + rng.uniform(-0.1, 0.1))))
        for i in range(n):
            ins = Vector(((apex[i].x + apex[i + 1].x) / 2, 0.0, (H + 0.17 + Lft[i].z) / 2))
            fo(mb, [apex[i], apex[i + 1], Lft[i + 1], Lft[i]], ins, mat)
            fo(mb, [apex[i], apex[i + 1], Rgt[i + 1], Rgt[i]], ins, mat)
            fo(mb, [Lft[i], Lft[i + 1], Rgt[i + 1], Rgt[i]], ins, mat)
        for k in (0, n):
            fo(mb, [apex[k], Lft[k], Rgt[k]], Vector((apex[k].x + (0.1 if k == 0 else -0.1), 0, H * 0.7)), mat)
        for i in range(0, n + 1, 2):                                  # cork line along the rail
            ball(mb, (apex[i].x, 0.0, H + 0.2), 0.075, "M_Hazard_Orange" if i % 4 == 0 else "M_Awning_Yellow",
                 seg=6, rings=4)
        for i in range(1, n, 3):                                      # lead-line floats on the hem
            for side in (Lft, Rgt):
                p = side[i]
                ball(mb, (p.x, p.y * 1.1, p.z - 0.02), 0.08, "M_Awning_Cream", seg=6, rings=4)
    return mb


def net_pile_mb(rng, rx=1.2, ry=0.9, h=0.6, mat="M_Door_Teal"):
    """Heap of net: a low lumpy mound with side lobes and a cork line snaking over it."""
    mb = MeshBuilder()
    prof = [(1.0, 0.0), (0.93, 0.25), (0.72, 0.55), (0.42, 0.85), (0.0, 1.0)]
    dome(mb, 0.0, 0.0, rx, ry, h, mat, rng, seg=12, noise=0.2, profile=prof)
    for k in range(3):
        a = rng.uniform(0, TAU)
        dome(mb, math.cos(a) * rx * 0.62, math.sin(a) * ry * 0.62, rx * 0.42, ry * 0.42, h * 0.58, mat, rng,
             seg=8, noise=0.2, profile=prof)
    for i in range(7):
        t = -0.85 + 1.7 * i / 6
        x, y = t * rx, math.sin(t * 2.6 + 0.5) * ry * 0.35
        rho = min(0.98, math.hypot(x / rx, y / ry))
        z = h * (1 - rho * rho) ** 0.75 + 0.02
        ball(mb, (x, y, z), 0.085, "M_Hazard_Orange" if i % 2 == 0 else "M_Awning_Yellow", seg=6, rings=4)
    return mb


def lobster_pot_mb():
    """Wire lobster trap 0.9 x 0.6 x 0.48 (body = PLACE colour, dark frame bands, timber runners)."""
    mb = MeshBuilder()
    bx(mb, -0.45, -0.3, 0.04, 0.45, 0.3, 0.46, PLACE, bevel=0.035)
    for x in (-0.44, 0.0, 0.44):
        bx(mb, x - 0.03, -0.315, 0.03, x + 0.03, 0.315, 0.475, DARK)
    bx(mb, -0.46, -0.315, 0.2, 0.46, 0.315, 0.25, DARK)
    for y in (-0.22, 0.22):
        bx(mb, -0.47, y - 0.03, 0.0, 0.47, y + 0.03, 0.06, "M_Door_Wood")
    return mb


def dinghy_mb(L=3.3, B=1.3, Dp=0.5, lift=0.45):
    """Upturned rowboat on two trestles (crawl-under gap). Hull = PLACE colour, white sheer strake."""
    mb = MeshBuilder()
    W = "M_Fence_Wood"
    for x in (-L * 0.28, L * 0.28):                       # trestles
        bx(mb, x - 0.08, -0.6, lift - 0.12, x + 0.08, 0.6, lift, W)
        for sy in (-1, 1):
            strut(mb, (x, sy * 0.5, lift - 0.12), (x, sy * 0.65, 0.0), 0.07, 0.07, W)
    ns, nj = 9, 6
    secs = []
    for i in range(ns):
        t = i / (ns - 1)                                  # 0 transom -> 1 bow
        x = -L / 2 + L * t
        b = B / 2 * (0.8 + 0.2 * math.sin(math.pi * min(1.0, t * 1.3))) * (1 - t ** 3) + 0.03
        d = Dp * (0.88 + 0.12 * math.sin(math.pi * t)) * (1 - 0.35 * t ** 4)
        row = []
        for j in range(nj + 1):
            th = math.pi * j / nj
            s = math.sin(th)
            row.append(Vector((x, b * math.cos(th), lift + d * (s ** 0.55))))
        secs.append(row)
    axis_in = lambda x: Vector((x, 0.0, lift + Dp * 0.3))
    for i in range(ns - 1):
        for j in range(nj):
            mat = "M_Sign_Face" if j in (0, nj - 1) else PLACE
            fo(mb, [secs[i][j], secs[i][j + 1], secs[i + 1][j + 1], secs[i + 1][j]],
               axis_in((secs[i][0].x + secs[i + 1][0].x) / 2), mat)
    fo(mb, secs[0], axis_in(-L / 2 + 0.3), PLACE)                               # transom
    fo(mb, secs[-1], axis_in(L / 2 - 0.3), PLACE)                               # bow
    for i in range(ns - 1):                                                     # underside (gunwales)
        q = [secs[i][0], secs[i + 1][0], secs[i + 1][nj], secs[i][nj]]
        fo(mb, q, Vector(((q[0].x + q[1].x) / 2, 0, lift + 0.3)), DARK)
    top = [r[nj // 2] for r in secs]                                            # keel strip
    for i in range(ns - 1):
        strut(mb, top[i] + Vector((0, 0, 0.02)), top[i + 1] + Vector((0, 0, 0.02)), 0.1, 0.06, "M_Door_Wood")
    return mb


def buoys_mb(width=3.2, z=2.3, rng=None):
    """String of fishing buoys for a wall: origin on the wall plane (y=0), buoys hang toward -Y."""
    rng = rng or random.Random(3)
    mb = MeshBuilder()
    bx(mb, -width / 2, -0.12, z - 0.04, width / 2, -0.04, z + 0.04, "M_Fence_Wood")
    for x in (-width / 2, width / 2):
        bx(mb, x - 0.06, -0.06, z - 0.08, x + 0.06, 0.0, z + 0.08, METAL_D)
    cols = [("M_Hazard_Orange", "M_Sign_Face"), ("M_Awning_Yellow", "M_Door_Red"), ("M_Sign_Face", "M_Awning_Teal"),
            ("M_Door_Red", "M_Sign_Face"), ("M_Awning_Teal", "M_Awning_Yellow"), ("M_Hazard_Orange", "M_Door_Navy")]
    n = 6
    for i in range(n):
        x = -width / 2 + 0.3 + (width - 0.6) * i / (n - 1)
        drop = rng.uniform(0.35, 0.8)
        cz = z - drop - 0.3
        strut(mb, (x, -0.08, z - 0.03), (x, -0.12, cz + 0.3), 0.04, 0.04, "M_Fence_Wood")
        a, b = cols[i % len(cols)]
        ball(mb, (x, -0.2, cz + 0.08), 0.17, a, seg=8, rings=4, sz=1.25)
        cyl(mb, (x, -0.2, cz - 0.12), "z", 0.13, 0.12, b, seg=8)
    return mb


def tarp_pile_mb(rng, L=1.9, W=1.3, H=0.95, tyre=True):
    """Tarp-covered heap (PLACE colour = tarp) with a tyre / bricks weighing it down."""
    mb = MeshBuilder()
    seg = 14
    levels = [(1.07, 0.0), (1.0, 0.1), (0.98, 0.5), (0.9, 0.8), (0.62, 0.97), (0.0, 1.03)]
    rings = []
    for k, (s, zf) in enumerate(levels[:-1]):
        row = []
        for i in range(seg):
            a = TAU * i / seg
            ca, sa = math.cos(a), math.sin(a)
            e = 0.28                                         # superellipse (boxy, soft corners)
            px = math.copysign(abs(ca) ** e, ca) * L / 2 * s
            py = math.copysign(abs(sa) ** e, sa) * W / 2 * s
            j = rng.uniform(0.95, 1.05) if k else 1.0
            row.append(Vector((px * j, py * j, H * zf + (rng.uniform(-0.07, 0.05) if k >= 2 else 0.0))))
        rings.append(row)
    top = Vector((rng.uniform(-0.1, 0.1), 0.0, H * levels[-1][1]))
    ins = Vector((0, 0, H * 0.4))
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            fo(mb, [rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]], ins, PLACE)
    for i in range(seg):
        fo(mb, [rings[-1][i], rings[-1][(i + 1) % seg], top], ins, PLACE)
    fo(mb, rings[0], ins, PLACE)
    # rope ties over the heap
    for xr in (-0.28, 0.3):
        x = xr * L
        prev = None
        for k in range(7):
            a = math.pi * k / 6
            y = math.cos(a) * W / 2 * 1.02
            z = 0.05 + math.sin(a) * (H * 0.97)
            p = Vector((x, y, z))
            if prev is not None:
                strut(mb, prev, p, 0.075, 0.075, "M_Trim_Wood")
            prev = p
    if tyre:
        cyl(mb, (L * 0.12, 0.05, H * 1.0 + 0.06), "z", 0.33, 0.2, TIRE, seg=10, cap_mat=DARK)
    for k, (bxx, byy, rz) in enumerate(((-L * 0.36, -0.05, 0.0), (-L * 0.36 + 0.06, 0.12, 0.35))):
        s = MeshBuilder()
        bx(s, -0.16, -0.075, 0.0, 0.16, 0.075, 0.1, "M_Wall_Brick")
        xf(mb, s, (bxx, byy, H * 0.93 + 0.1 * k), (0, 0, rz))
    return mb


def tyre_stack_mb(n=4, rng=None):
    """Stack of old tyres (slightly offset): outer tread, top sidewall ring, inward-facing bore, dark floor."""
    rng = rng or random.Random(5)
    mb = MeshBuilder()
    seg, ro, ri, h = 12, 0.42, 0.22, 0.25
    for k in range(n):
        ox, oy = rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06)
        z0, z1 = k * (h + 0.01), k * (h + 0.01) + h
        O = [(ox + ro * math.cos(TAU * i / seg), oy + ro * math.sin(TAU * i / seg)) for i in range(seg)]
        I = [(ox + ri * math.cos(TAU * i / seg), oy + ri * math.sin(TAU * i / seg)) for i in range(seg)]
        for i in range(seg):
            j = (i + 1) % seg
            mid = Vector((ox, oy, (z0 + z1) / 2))
            fo(mb, [Vector((*O[i], z0)), Vector((*O[j], z0)), Vector((*O[j], z1)), Vector((*O[i], z1))], mid, TIRE)
            fo(mb, [Vector((*O[i], z1)), Vector((*O[j], z1)), Vector((*I[j], z1)), Vector((*I[i], z1))],
               Vector((ox, oy, z0)), TIRE)
            fo(mb, [Vector((*I[i], z0 + 0.05)), Vector((*I[j], z0 + 0.05)), Vector((*I[j], z1)), Vector((*I[i], z1))],
               mid, DARK, inward=True)
        fo(mb, [Vector((*I[i], z0 + 0.05)) for i in range(seg)], Vector((ox, oy, z0 - 1.0)), DARK)
    return mb


def log_mb(L=3.0, r=0.3):
    """Fallen log along X with a root flare, a broken branch and a moss cushion."""
    mb = MeshBuilder()
    cz = r * 0.9
    cyl(mb, (0.15, 0.0, cz), "x", r, L - 0.3, "M_Bark", seg=9, cap_mat="M_Wood_Light")
    cyl(mb, (-L / 2 + 0.1, 0.0, cz * 1.05), "x", r * 1.25, 0.5, "M_Bark", seg=9, r2=r * 1.0, cap_mat="M_Bark")
    strut(mb, (0.4, 0.1, cz + r * 0.7), (0.75, 0.55, cz + r * 2.1), 0.13, 0.13, "M_Bark")
    rng = random.Random(7)
    dome(mb, -0.35, 0.0, 0.5, 0.28, 0.16, "M_Foliage_Dark", rng, seg=8, noise=0.1, z0=cz + r * 0.82)
    return mb


# =============================================================================== container yard
PAVE_Z = 0.03
CW, CL, CH = 2.44, 6.1, 2.6
CONTAINER_COLORS = ["M_Awning_Red", "M_Awning_Blue", "M_Awning_Green", "M_Hazard_Orange", "M_Awning_Teal",
                    "M_Wall_Slate", "M_Door_Navy", "M_Wall_Brick", "M_Awning_Yellow", "M_Awning_Blue",
                    "M_Awning_Red", "M_Awning_Green"]
COLS = {"A": -6.40, "B": -3.96, "C": 3.52, "D": 5.96}
# (column, y-centre, stack height)   containers lie along Y (doors face north / south alternately)
STACKS = [
    ("A", -9.30, 2), ("B", -9.30, 1),
    ("A", -3.05, 3), ("B", -3.05, 2),
    ("A", 5.65, 1), ("B", 5.65, 2),
    ("A", 11.95, 2), ("B", 11.95, 3),
    ("C", -9.00, 1), ("D", -9.00, 3),
    ("D", -0.55, 2),                    # C at -0.55 is the open container
    ("C", 5.70, 3), ("D", 5.70, 1),
    ("C", 14.25, 1), ("D", 14.25, 2),
]
GANTRY_Y = 8.0
GANTRY_TX = -0.22                       # trolley over the main lane


def _fence_runs(S, poly, gaps, piece="Fence_Chain_3m", z=PAVE_Z, sub="Fence"):
    """Closed fence along a local polygon with exact openings. gaps: [(local point, width)].

    Returns the list of opening end points (for gate posts)."""
    P = [G.V(p) for p in poly]
    ends = []
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        L = (b - a).length
        d = (b - a) / L
        cuts = []
        for g, w in gaps:
            g = G.V(g)
            s = (g - a).dot(d)
            off = abs((g - a).x * d.y - (g - a).y * d.x)
            if -w / 2 < s < L + w / 2 and off < 1.5:
                cuts.append((max(0.0, s - w / 2), min(L, s + w / 2)))
                ends += [a + d * max(0.0, s - w / 2), a + d * min(L, s + w / 2)]
        cuts.sort()
        runs, s0 = [], 0.0
        for c0, c1 in cuts:
            if c0 > s0 + 0.3:
                runs.append((s0, c0))
            s0 = max(s0, c1)
        if L > s0 + 0.3:
            runs.append((s0, L))
        rot = math.atan2(d.y, d.x)
        for r0, r1 in runs:
            n = max(1, round((r1 - r0) / 3.0))
            sx = (r1 - r0) / (3.0 * n)
            for k in range(n):
                m = a + d * (r0 + (r1 - r0) * (k + 0.5) / n)
                S.put(piece, m.x, m.y, z, rot, scale=(sx, 1, 1), local=True, sub=sub)
    return ends


def container_base_mb(L=CL, D=CW, lip=0.015):
    """Closed underside plate for an upper-tier KIT_Container_6m (kit frame: long side along X).

    WORKAROUND (kit): the kit container has no bottom face and single-sided walls, so wherever a
    jittered upper box overhangs the one below, the lane camera looks up into its interior and (with
    backface culling, as in Unity) straight through the walls. This dark bottom rail covers the whole
    footprint, 1.5 cm proud of the walls (no slit, no coplanar faces) and 2 mm above the box below; it
    reads as the shadow seam between stacked boxes."""
    mb = MeshBuilder()
    mb.box(-L / 2 - lip, -D / 2 - lip, 0.002, L / 2 + lip, D / 2 + lip, 0.035, METAL_D)
    return mb


def _container(S, x, y, level, rot, color, sub="Containers", rng=None):
    # rng call order (x jitter, rotation, y jitter) is kept so the stack layout stays unchanged
    j = rng.uniform(-0.06, 0.06) if rng else 0.0
    r = rot + (math.radians(rng.uniform(-1.6, 1.6)) if (rng and level > 0) else 0.0)
    jy = rng.uniform(-0.08, 0.08) if rng else 0.0
    z = PAVE_Z + CH * level
    o = S.put("Container_6m", x + j, y + jy, z, r, recolor={"awning": color}, local=True, sub=sub)
    if o is not None and level > 0:
        src = getattr(S, "_container_base", None)
        if src is None:
            S._container_base = place(S, "ContainerBase", container_base_mb(), x + j, y + jy, z, r, sub=sub)
        else:
            dup(S, src, "ContainerBase", x + j, y + jy, z, r, sub=sub, local=True)
    return o


def _edge_x_at(P, i, y):
    """x where edge P[i] -> P[i+1] crosses height y (local)."""
    a, b = P[i], P[(i + 1) % len(P)]
    t = (y - a.y) / (b.y - a.y)
    return a.x + (b.x - a.x) * t


def _aim(px, py, tx, ty):
    """Rotation that points a piece's local -Y from (px, py) toward (tx, ty)."""
    return math.atan2(tx - px, -(ty - py))


def register_hide(S, name, lx, ly, z, face_local):
    """Publish a designed-in hide point of this site (site-local x, y; *face_local* = the local angle the
    hide opens toward) in ctx["lm_hides"][site id]. hiding_spots.build_all uses the nearest one as the
    machine-readable anchor of a layout HIDING_SPOT that falls inside this (already dressed) site."""
    p = S.to_world(lx, ly)
    a = face_local + S.rot
    S.ctx.setdefault("lm_hides", {}).setdefault(S.id, []).append(
        dict(name=name, x=round(p.x, 2), y=round(p.y, 2), z=round(z, 3),
             heading_deg=round(math.degrees(math.atan2(math.sin(a), math.cos(a))), 1)))


def _recolor_obj(o, mat):
    if o is None:
        return
    for i, slot in enumerate(o.material_slots):
        m = o.data.materials[i]
        if m is not None and m.name == PLACE:
            slot.link = "OBJECT"
            slot.material = palette.get(mat)


def build(S):
    """ServiceYard -> the Container Yard (see module docstring)."""
    scoped(S)
    rng = random.Random("ServiceYard")
    P = [S.to_local(p) for p in S.poly]               # site frame = world axes (no facing)
    fence = inset_poly(P, 0.5)
    W = lambda x, y: S.to_world(x, y)

    # ---------------------------------------------------------------- ground: asphalt + concrete apron
    slab = inset_poly(P, 0.1)
    S.paving("Ground_Slab", [W(p.x, p.y) for p in slab], "M_Asphalt_Alley", z=PAVE_Z)
    ya = -12.6
    ap_poly = [slab[3], slab[2], Vector((_edge_x_at(slab, 1, ya), ya)), Vector((_edge_x_at(slab, 3, ya), ya))]
    S.paving("Ground_Apron", [W(p.x, p.y) for p in ap_poly], "M_Concrete", z=PAVE_Z + 0.012, skirt=0.05)
    mk = MeshBuilder()
    zl = PAVE_Z + 0.02

    def line(x0, y0, x1, y1, w=0.16, mat="M_RoadLine_Yellow", z=zl):
        d = Vector((x1 - x0, y1 - y0)).normalized()
        n = Vector((-d.y, d.x)) * w / 2
        q = [W(x0 - n.x, y0 - n.y), W(x1 - n.x, y1 - n.y), W(x1 + n.x, y1 + n.y), W(x0 + n.x, y0 + n.y)]
        fo(mk, [(p.x, p.y, z) for p in q], (q[0].x, q[0].y, z - 1.0), mat)

    for x in (-2.55, 2.1):
        line(x, -12.2, x, 18.5)
    line(_edge_x_at(slab, 3, ya) + 0.3, ya + 0.15, _edge_x_at(slab, 1, ya) - 0.3, ya + 0.15, w=0.22, z=zl + 0.012)
    for k in range(5):                                   # keep-clear hatch north of the loading dock
        y = -15.4 + k * 0.55
        line(9.3, y, 11.6, y + 1.0, w=0.18, z=zl + 0.012)
    S.mesh("Ground_Lines", mk, sub="Ground")

    # ---------------------------------------------------------------- fence + openings
    # The truck gate is fixed (south, toward Cannery Row). The side gap and the broken gap pick the first
    # candidate whose outside approach (4 m) is free of the generic Dock Yard buildings (World lots), so
    # no opening ends up against a warehouse wall: west side preferred (toward Dock Bridge Rd), else east.
    gate_w = 7.5

    def edge_point(i, t):
        a, b = fence[i], fence[(i + 1) % len(fence)]
        return a.lerp(b, t), (b - a).normalized()

    def outside_free(p, d, w, depth=4.0):
        if S.world is None:
            return True
        o = Vector((d.y, -d.x))
        if o.dot(p) < 0:                                 # outward = away from the site centre
            o = -o
        c = p + o * (depth / 2 + 0.25)
        rect = [c + d * w / 2 + o * depth / 2, c - d * w / 2 + o * depth / 2, c - d * w / 2 - o * depth / 2,
                c + d * w / 2 - o * depth / 2]
        return S.world.lot_free([W(q.x, q.y) for q in rect])

    def pick(i, coord, cands, w):
        a, b = fence[i], fence[(i + 1) % len(fence)]
        for v in cands:
            t = (v - getattr(a, coord)) / (getattr(b, coord) - getattr(a, coord))
            if not 0.05 < t < 0.95:
                continue
            p, d = edge_point(i, t)
            if outside_free(p, d, w + 1.0):
                return p
        return None

    side_w, north_w = 2.2, 3.2
    gate_c = None
    for gx in (5.6, 6.2, 4.6, 3.6):                     # truck gate: the central 6 m must be approachable
        p, d = edge_point(2, (gx - fence[2].x) / (fence[3].x - fence[2].x))
        if outside_free(p, d, gate_w - 1.5, depth=3.0):
            gate_c = p
            break
    if gate_c is None:
        gate_c = edge_point(2, (5.6 - fence[2].x) / (fence[3].x - fence[2].x))[0]
    side_c = pick(3, "y", [1.35, 0.4, -0.8, -2.2, -3.4, -9.4, -10.6], side_w)          # west fence
    if side_c is None:
        side_c = pick(1, "y", [-4.75, -3.6, -5.9, 0.0, 9.9], side_w)                    # east fence
    north_c = pick(0, "x", [1.6, -0.4, 3.6, -2.6, 5.6, -4.6], north_w)
    gaps = [(gate_c, gate_w)] + [(g, w) for g, w in ((side_c, side_w), (north_c, north_w)) if g is not None]
    ends = _fence_runs(S, fence, gaps)
    post = MeshBuilder()
    bx(post, -0.2, -0.2, 0.0, 0.2, 0.2, 2.35, DARK, bevel=0.03)
    bx(post, -0.24, -0.24, 2.35, 0.24, 0.24, 2.5, YEL)
    post_obj = None
    for e in ends:
        if (north_c is not None and (e - north_c).length < 4) or (e - gate_c).length < gate_w / 2 + 1.0:
            continue                                     # broken gap: no posts; truck gate: the sign posts
        if post_obj is None:
            post_obj = place(S, "GatePost", post, e.x, e.y, PAVE_Z, 0.0, sub="Gate")
        else:
            dup(S, post_obj, "GatePost", e.x, e.y, PAVE_Z, 0.0, sub="Gate", local=True)
    # telescopic sliding gate: both leaves parked open on the west side, on two tracks inside the fence
    fy = gate_c.y + 0.55
    S.put("Fence_Chain_3m", gate_c.x - gate_w / 2 - 1.5, fy + 0.3, PAVE_Z, 0.0, local=True, sub="Gate")
    S.put("Fence_Chain_3m", gate_c.x - gate_w / 2 - 4.4, fy, PAVE_Z, 0.0, local=True, sub="Gate")
    # the broken gap: one panel pushed in, lying against the yard side (story: something broke in here)
    if north_c is not None:
        _, d = edge_point(0, 0.5)
        o = S.put("Fence_Chain_3m", north_c.x + 0.25, north_c.y - 0.25, PAVE_Z, math.atan2(d.y, d.x) + 0.12,
                  local=True, sub="Fence")
        if o:
            o.rotation_euler[0] = math.radians(78)
    place(S, "GateSign", gate_sign_mb(width=gate_w + 0.1), gate_c.x, gate_c.y, PAVE_Z, 0.0, sub="Gate")
    place(S, "BoomBarrier", boom_mb(), gate_c.x - gate_w / 2 + 0.75, gate_c.y + 1.3, PAVE_Z, 0.0, sub="Gate")

    # ---------------------------------------------------------------- site office (kit shed) + bits
    spec = BuildingSpec("shed", 2, 2, 1,
                        dict(wall="M_Wall_Sky", trim="M_Trim_White", door="M_Door_Navy", awning="M_Awning_Blue",
                             roof="M_Roof_Charcoal", sign="M_Sign_Accent"),
                        roof="flat", ground_h=H3, feats=dict(door_i=0), seed=41, district="service")
    S.building(spec, W(-3.0, -21.6), S.rot + math.pi / 2, name="LM_ServiceYard_SiteOffice")
    S.put("Canopy_Door", -3.0, -23.1, 0.15 + 2.42, math.pi / 2, local=True, sub="Office")
    S.put("Bench", -2.35, -20.9, PAVE_Z + 0.012, math.pi / 2, local=True, sub="Office")
    S.put("TrashBin", -2.45, -19.3, PAVE_Z + 0.012, 0.3, local=True, sub="Office")
    S.put("Doghouse", -1.9, -17.2, PAVE_Z + 0.012, math.pi / 2 + 0.45, local=True, sub="Office",
          recolor={"wall": "M_Wall_Butter", "roof": "M_Roof_Terracotta"})
    S.put("Dumpster", -6.2, -17.25, PAVE_Z + 0.012, math.pi, local=True, sub="Office")
    S.put("Pallet", -4.4, -16.9, PAVE_Z + 0.012, 0.1, local=True, sub="Clutter")
    S.put("Pallet", -4.4, -16.9, PAVE_Z + 0.16, -0.05, local=True, sub="Clutter")

    # ---------------------------------------------------------------- loading bay + truck + forklift
    dock_front = _edge_x_at(fence, 1, -19.5) - 0.12 - 2.6
    place(S, "LoadingDock", dock_mb(L=8.0, D=2.6, H=1.2), dock_front, -19.5, PAVE_Z, -math.pi / 2, sub="LoadingBay")
    zd = PAVE_Z + 1.2
    S.put("Pallet", dock_front + 1.0, -22.2, zd, 0.05, local=True, sub="LoadingBay")
    S.put("CrateStack", dock_front + 1.0, -22.2, zd + 0.15, 0.3, local=True, sub="LoadingBay")
    S.put("Pallet", dock_front + 1.1, -16.6, zd, -0.1, local=True, sub="LoadingBay")
    S.put("Crate", dock_front + 1.15, -16.6, zd + 0.15, -0.2, local=True, sub="LoadingBay")
    S.put("Truck_Box", dock_front - 0.3 - 3.25, -19.5, PAVE_Z + 0.012, -math.pi / 2, local=True, sub="LoadingBay",
          recolor={"awning": "M_Awning_Teal", "sign": "M_Hazard_Orange"})
    a = math.pi / 2 + 0.3
    fpos = Vector((1.4, -15.2))
    place(S, "Forklift", forklift_mb(), fpos.x, fpos.y, PAVE_Z + 0.012, a, sub="LoadingBay")
    fwd = Vector((math.sin(a), -math.cos(a)))
    fp = fpos + fwd * 1.72
    S.put("Pallet", fp.x, fp.y, PAVE_Z + 0.012 + 0.52, a, local=True, sub="LoadingBay")
    S.put("CrateStack", fp.x, fp.y, PAVE_Z + 0.012 + 0.67, a, local=True, sub="LoadingBay")

    # ---------------------------------------------------------------- container maze
    cols = list(CONTAINER_COLORS)
    rng.shuffle(cols)
    ci = 0
    for col, y, h in STACKS:
        x = COLS[col]
        for lv in range(h):
            rot = math.pi / 2 if (ci % 2 == 0) else -math.pi / 2
            _container(S, x, y, lv, rot, cols[ci % len(cols)], rng=rng)
            ci += 1
    oc = place(S, "OpenContainer", open_container_mb(), COLS["C"], -0.55, PAVE_Z, -math.pi / 2, sub="Containers")
    _recolor_obj(oc, "M_Awning_Green")
    # hide point: 1.5 m inside the open doors (doors = mesh +X -> site -Y after the -90 deg turn)
    register_hide(S, "OpenContainer", COLS["C"], -0.55 - CL / 2 + 1.5, PAVE_Z + 0.1, -math.pi / 2)
    S.put("Pallet", 2.6, -4.75, PAVE_Z, 0.2, local=True, sub="Clutter")
    S.put("Crate", 2.65, -4.7, PAVE_Z + 0.15, 0.35, local=True, sub="Clutter")
    _container(S, -7.3, 18.6, 0, 0.04, "M_Wall_Slate", rng=None)
    S.put("CrateStack", -11.0, 16.2, PAVE_Z, 0.4, local=True, sub="Clutter")
    S.put("Crate", -10.4, 14.4, PAVE_Z, 0.1, local=True, sub="Clutter")
    S.put("Pallet", -2.0, 19.4, PAVE_Z, 0.0, local=True, sub="Clutter")
    for k in range(4):
        S.put("Pallet", -9.2, -14.3, PAVE_Z + 0.012 + 0.147 * k, 0.05 * (k % 2) - 0.02, local=True, sub="Clutter")
    for (x, y) in ((8.3, 17.7), (9.0, 17.9), (8.6, 18.6), (9.4, 18.6), (8.0, 19.3)):
        S.put("Barrel", x, y, PAVE_Z, rng.uniform(0, TAU), local=True, sub="Clutter")
    ty = tyre_stack_mb(4, rng)
    t0 = place(S, "TyreStack", ty, -8.3, -16.9, PAVE_Z + 0.012, 0.0, sub="Clutter")
    dup(S, t0, "TyreStack", 10.4, 16.1, PAVE_Z, 0.7, sub="Clutter", local=True, scale=(1, 1, 0.75))
    S.put("TrafficCone", 0.9, -11.6, PAVE_Z, 0.0, local=True, sub="Clutter")
    S.put("TrafficCone", -1.4, -11.7, PAVE_Z, 0.0, local=True, sub="Clutter")

    # ---------------------------------------------------------------- gantry crane + hanging container
    place(S, "GantryCrane", gantry_mb(tx=GANTRY_TX), 0.0, GANTRY_Y, PAVE_Z, 0.0, sub="Crane")
    S.put("Container_6m", GANTRY_TX, GANTRY_Y, PAVE_Z + 5.0, math.pi / 2, recolor={"awning": "M_Hazard_Orange"},
          local=True, sub="Crane", name="LM_ServiceYard_HangingContainer")

    # ---------------------------------------------------------------- floodlights (aimed into the yard)
    fm = flood_mast_mb()
    masts = [(11.4, -12.0), (-10.4, -6.0), (-12.5, 21.9), (10.8, 18.9)]
    src = None
    for x, y in masts:
        r = _aim(x, y, 0.0, 0.0)
        if src is None:
            src = place(S, "Floodlight", fm, x, y, PAVE_Z, r, sub="Lights")
        else:
            dup(S, src, "Floodlight", x, y, PAVE_Z, r, sub="Lights", local=True)

    S.register_lot([W(p.x, p.y) for p in P])
    return dict(containers=ci + 1, side_gap=[round(side_c.x, 1), round(side_c.y, 1)] if side_c else None,
                north_gap=[round(north_c.x, 1), round(north_c.y, 1)] if north_c else None)


# =============================================================================== net yard
def torus(mb, center, R, r, mats, axis="z", seg=12, tseg=6):
    """Torus ring; mats = one material or a list cycled per quarter (life-ring stripes)."""
    c = Vector(center)
    if axis == "z":
        U, V, A = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    else:                                   # ring standing in the XZ plane, facing -Y
        U, V, A = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0))
    ml = mats if isinstance(mats, (list, tuple)) else [mats]
    for i in range(seg):
        a0, a1 = TAU * i / seg, TAU * (i + 1) / seg
        d0, d1 = U * math.cos(a0) + V * math.sin(a0), U * math.cos(a1) + V * math.sin(a1)
        am = (a0 + a1) / 2
        mid = c + (U * math.cos(am) + V * math.sin(am)) * R
        mat = ml[(i * len(ml)) // seg]
        for j in range(tseg):
            b0, b1 = TAU * j / tseg, TAU * (j + 1) / tseg
            q = [c + d0 * (R + r * math.cos(b0)) + A * r * math.sin(b0),
                 c + d1 * (R + r * math.cos(b0)) + A * r * math.sin(b0),
                 c + d1 * (R + r * math.cos(b1)) + A * r * math.sin(b1),
                 c + d0 * (R + r * math.cos(b1)) + A * r * math.sin(b1)]
            fo(mb, q, mid, mat)


def life_ring_mb():
    """Life ring on a wall hook. Origin on the wall plane (y = 0), ring stands proud toward -Y."""
    mb = MeshBuilder()
    bx(mb, -0.05, -0.12, 0.62, 0.05, 0.0, 0.74, METAL_D)
    torus(mb, (0, -0.1, 0.36), 0.3, 0.075, ["M_Sign_Face", "M_Door_Red", "M_Sign_Face", "M_Door_Red"], axis="y",
          seg=16, tseg=6)
    return mb


def rope_coil_mb():
    mb = MeshBuilder()
    for k, (R, z) in enumerate(((0.36, 0.06), (0.33, 0.17), (0.3, 0.28))):
        torus(mb, (0.0, 0.0, z), R, 0.06, "M_Wood_Light", seg=12, tseg=5)
    return mb


def _slab_xz(mb, poly, y0, y1, mat):
    """Convex 2D outline in the XZ plane extruded from y0 to y1 (closed, outward faces)."""
    c = Vector((sum(p[0] for p in poly) / len(poly), (y0 + y1) / 2, sum(p[1] for p in poly) / len(poly)))
    A = [Vector((p[0], y0, p[1])) for p in poly]
    B = [Vector((p[0], y1, p[1])) for p in poly]
    fo(mb, A, c, mat)
    fo(mb, B, c, mat)
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        fo(mb, [A[i], A[j], B[j], B[i]], c, mat)


def yard_sign_mb(w=2.4, h=2.5):
    """Timber post sign with a fish pictogram on both faces. X along the board."""
    mb = MeshBuilder()
    W = "M_Fence_Wood"
    for sx in (-1, 1):
        bx(mb, sx * w / 2 - 0.08, -0.08, 0.0, sx * w / 2 + 0.08, 0.08, h, W, bevel=0.02)
        bx(mb, sx * w / 2 - 0.1, -0.1, h, sx * w / 2 + 0.1, 0.1, h + 0.06, "M_Trim_Wood")
    z0, z1 = h - 0.85, h - 0.15
    bx(mb, -w / 2 + 0.08, -0.06, z0, w / 2 - 0.08, 0.06, z1, "M_Wood_Light", bevel=0.02)
    cx, cz = -0.68, (z0 + z1) / 2
    body = [(cx + 0.28 * math.cos(a), cz + 0.15 * math.sin(a)) for a in [TAU * k / 10 for k in range(10)]]
    tail = [(cx - 0.2, cz), (cx - 0.46, cz + 0.17), (cx - 0.46, cz - 0.17)]
    for sy in (-1, 1):
        y = sy * 0.06
        for x0, x1, zz0, zz1 in ((-0.25, 0.25, z1 - 0.28, z1 - 0.15), (-0.25, 0.95, z0 + 0.14, z0 + 0.26),
                                 (0.4, 0.95, z1 - 0.28, z1 - 0.15)):
            bx(mb, x0, min(y, y + sy * 0.03), zz0, x1, max(y, y + sy * 0.03), zz1, "M_Sign_Board")
        _slab_xz(mb, body, y, y + sy * 0.04, "M_Awning_Teal")
        _slab_xz(mb, tail, y, y + sy * 0.04, "M_Awning_Teal")
        ball(mb, (cx + 0.15, y + sy * 0.045, cz + 0.04), 0.035, "M_Sign_Face", seg=6, rings=3)
    return mb


def _organic(P, rng, step=2.2, inward=0.9):
    """Subdivide a polygon and pull the new points inward by a random amount (soft, hand-made edge)."""
    P = [G.V(p) for p in P]
    c = G.centroid(P)
    out = []
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        out.append(a)
        n = max(1, int((b - a).length / step))
        for k in range(1, n):
            q = a.lerp(b, k / n)
            out.append(q + (c - q).normalized() * rng.uniform(0.1, inward))
    return out


def build_area(S):
    """NO_BUILD NetYard -> open crate and net yard on the Wharf quay (see module docstring)."""
    if S.id != "NetYard":
        return None
    scoped(S)
    rng = random.Random("NetYard")
    P = [G.V(p) for p in S.poly]
    S.rot = math.atan2(P[1].y - P[0].y, P[1].x - P[0].x)      # local X along the long (canal-side) edge
    L = [S.to_local(p) for p in P]
    Z = 0.02
    pad = _organic(inset_poly(L, 0.3), rng, step=3.0, inward=0.55)
    S.paving("Ground_Yard", [S.to_world(p.x, p.y) for p in pad], "M_Dirt", z=Z, skirt=0.15)

    # ---------------------------------------------------------------- net shed (east end, door to the street)
    spec = BuildingSpec("shed", 2, 2, 1,
                        dict(wall="M_Wall_Brick", trim="M_Trim_White", door="M_Door_Teal", awning="M_Awning_Teal",
                             roof="M_Roof_Charcoal", sign="M_Sign_Accent"),
                        roof="gable_side", ground_h=H3, feats=dict(door_i=1), seed=17, district="service")
    sx, sy = 8.2, -2.4
    S.building(spec, S.to_world(sx, sy), S.rot, name="LM_NetYard_NetShed")
    deck = MeshBuilder()                                    # plank deck along the front
    for i in range(9):
        x0 = sx - 3.6 + i * 0.82
        bx(deck, x0, -2.3, 0.0, x0 + 0.78, 0.0, 0.15, "M_Wood_Light" if i % 3 else "M_Fence_Wood")
    bx(deck, sx - 3.6, -2.38, -0.1, sx - 3.6 + 9 * 0.82 - 0.04, -2.3, 0.13, "M_Fence_Wood")
    place(S, "Deck", deck, 0.0, sy, Z, 0.0, sub="Shed")
    place(S, "Buoys", buoys_mb(width=3.8, z=2.45, rng=rng), sx - 3.0 - 0.02, sy + 3.0, Z + 0.13, -math.pi / 2,
          sub="Shed")
    place(S, "LifeRing", life_ring_mb(), sx + 2.55, sy - 0.02, 0.15 + 1.25, 0.0, sub="Shed")
    place(S, "RopeCoil", rope_coil_mb(), sx - 3.0, sy - 1.0, Z + 0.15, 0.0, sub="Shed")
    S.put("Bench", sx - 1.2, sy - 1.55, Z + 0.15, 0.0, local=True, sub="Shed")
    S.put("Lamp_Park", sx - 3.9, sy - 2.9, Z, 0.0, local=True, sub="Shed")
    S.put("Barrel", sx + 3.55, sy - 0.7, Z, 0.4, local=True, sub="Clutter")
    place(S, "YardSign", yard_sign_mb(), -8.6, -6.9, Z, 0.13, sub="Shed")
    S.put("Barrel", sx + 3.35, sy - 1.45, Z, 1.2, local=True, sub="Clutter")
    S.put("CrateStack", sx + 1.2, sy + 7.2, Z, 0.15, local=True, sub="Clutter")

    # ---------------------------------------------------------------- net racks + piles (middle)
    place(S, "NetRack_A", net_rack_mb(rng, L=5.0, mats=("M_Door_Teal", "M_Door_Navy")), -3.4, 2.7, Z, 0.0,
          sub="Nets")
    place(S, "NetRack_B", net_rack_mb(rng, L=4.2, mats=("M_Awning_Green", "M_Door_Teal")), -2.6, -2.2, Z, 0.06,
          sub="Nets")
    for (x, y, rx, ry, h, mat) in ((1.5, 0.4, 1.3, 1.0, 0.6, "M_Door_Navy"),
                                   (-7.6, 0.2, 1.15, 0.9, 0.5, "M_Hazard_Orange"),
                                   (2.4, 4.7, 1.0, 0.8, 0.45, "M_Awning_Green"),
                                   (-6.2, -3.6, 0.9, 0.7, 0.42, "M_Door_Teal")):
        place(S, "NetPile", net_pile_mb(rng, rx, ry, h, mat), x, y, Z, rng.uniform(0, TAU), sub="Nets")
    # hide point: the pocket between the two net racks and the big net pile (screened from the street)
    register_hide(S, "NetPilePocket", -0.4, 0.5, Z, -math.pi / 2)

    # ---------------------------------------------------------------- lobster pots (west end)
    pot = None
    pot_cols = ["M_Awning_Yellow", "M_Awning_Green", "M_Hazard_Orange", "M_Awning_Yellow", "M_Awning_Blue",
                "M_Awning_Green"]
    towers = [(-11.2, 4.0, 4, 0.1), (-10.15, 4.1, 3, -0.05), (-12.1, 2.8, 2, 0.08), (-6.1, 5.4, 2, 0.3),
              (-11.0, 1.6, 1, 0.5), (-5.2, 5.6, 1, -0.2), (0.6, 6.0, 3, 0.05)]
    k = 0
    for (x, y, n, r) in towers:
        for lv in range(n):
            z = Z + lv * 0.475
            rr = r + rng.uniform(-0.12, 0.12)
            xx, yy = x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.04, 0.04)
            if pot is None:
                pot = place(S, "LobsterPot", lobster_pot_mb(), xx, yy, z, rr, sub="Pots")
                _recolor_obj(pot, pot_cols[0])
            else:
                dup(S, pot, "LobsterPot", xx, yy, z, rr, sub="Pots", recolor=pot_cols[k % len(pot_cols)], local=True)
            k += 1

    # ---------------------------------------------------------------- upturned dinghy, crates, pallets, barrels
    dg = place(S, "Dinghy", dinghy_mb(), -9.4, -3.7, Z, 0.12, sub="Boat")
    _recolor_obj(dg, "M_Awning_Teal")
    register_hide(S, "UnderDinghy", -9.4, -3.7, Z, 0.12 - math.pi / 2)     # crawl gap, opens to the street side
    S.put("CrateStack", -11.3, -0.9, Z, 0.2, local=True, sub="Clutter")
    S.put("Crate", 4.4, 5.7, Z, 0.5, local=True, sub="Clutter")
    S.put("Crate", 4.95, 5.5, Z + 1.0, 0.3, local=True, sub="Clutter")
    S.put("Crate", 5.4, 5.5, Z, 0.1, local=True, sub="Clutter")
    S.put("Pallet", 0.2, -5.5, Z, 0.1, local=True, sub="Clutter")
    S.put("Pallet", 0.25, -5.5, Z + 0.147, 0.0, local=True, sub="Clutter")
    S.put("Crate", 0.3, -5.5, Z + 0.294, 0.25, local=True, sub="Clutter")
    for (x, y) in ((-5.6, -5.5), (-5.0, -6.1), (-4.4, -5.4)):
        S.put("Barrel", x, y, Z, rng.uniform(0, TAU), local=True, sub="Clutter")
    S.register_lot(S.poly)
    return dict(pots=k)
