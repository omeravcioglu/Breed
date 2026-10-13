"""Kit family: ROOFS, TRIMS & ROOFTOP pieces. See docs/KIT_SPEC.md ("roofs.py").

Pieces (all required names, nothing renamed):
  Roofs   KIT_Roof_Flat_1x1
          KIT_Roof_Gable_S{6,9,12}_Mid / _EndL / _EndR, KIT_Gable_S{6,9,12}
  Trims   KIT_Parapet_3m, KIT_Parapet_Corner, KIT_Cornice_3m, KIT_Cornice_Corner,
          KIT_FloorBand_3m, KIT_FloorBand_Corner, KIT_Plinth_3m, KIT_Plinth_Corner
  Rooftop KIT_Roof_AC_Unit, KIT_Roof_WaterTank, KIT_Roof_Vent, KIT_Roof_Skylight,
          KIT_Roof_Access, KIT_Chimney
Extra pieces (not in the spec list):
  Trims   KIT_Plinth_Door_3m - plinth for a door module: centred 1.30 m gap (meta gap) with return
            caps, so the base course runs right up to the door frame (1.0 / 1.1 m doors).
          KIT_Plinth_Half - 1.5 m plinth (x in [-0.75, 0.75]) for the KIT_Wall_Half_* fillers.

Gable roof convention (ridge along X):
  * origin = top of the front wall on the facade plane: the roof UNDERSIDE passes through
    (y=0, z=0) and rises with the pitch, so it sits exactly on the outer edge of the wall top.
  * y in [-0.45, S+0.45] (0.45 eaves front & back), apex of the underside at y=S/2,
    z = S/2*tan(pitch)  (meta "ridge_under_z"; KIT_Gable_S* peaks at exactly this height).
  * Mid segments are 3 m (x in [-1.5, 1.5]), open at both ends (no hidden end caps) and tile
    seamlessly along X. EndL (x in [-0.45, 0]) / EndR (x in [0, 0.45]) close the -X / +X ends:
    they continue the same cross-section as the 0.45 m gable overhang, cap it, and carry the
    barge boards. Place EndL with its origin at the building's -X outer face and EndR at the
    +X outer face (same y/z as the Mid segments).
  * S6 / S9 (35 deg, houses): shingle courses (stepped butt lines every ~0.5 m along the slope).
    S12 (18 deg, warehouses): smooth slab with standing-seam ribs every 0.6 m (ribs sit at
    0.3 m + k*0.6 m from the building end, so they stay evenly spaced across Mid/End seams).
  * Fascia / barge boards are 0.18 m deep (BOARD_H): on S6 / S9 the eave fascia bottom stays
    above the H3 window-head frames of the floor below.
  * Top surfaces + ridge cap + slab edges M_Roof_Slate (recolor "roof"); fascia boards,
    barge boards and the soffit/ceiling underside M_Trim_White (recolor "trim").
  * KIT_Gable_S*: WALL convention (outer face y=0, x in [-S/2, S/2], thickness 0.3 into +Y),
    triangle from z=0 to the underside apex, so its sloped tops lie flush under the roof.
    Placed on top of the end walls, rotated -90 deg (at the -X end) / +90 deg (at the +X end).
    KIT_Gable_S12 (warehouse-only) carries the same box-profile cladding as the industrial walls
    (walls._cladding): major ribs at x = -5.75 + 0.5k, minor ribs at x = -6 + 0.5k, so they line up
    with the 3 m KIT_Wall_Industrial_* modules below. An M_Metal_Dark flashing (0.10 deep x 0.12)
    along the base caps the wall rib tops; a surface-mounted louvre vent replaces the recessed one.
    Rib tops are sunk 0.02 above the rake into the roof slab (open by design, hidden by the
    gable overhang / barge board in assembly).

Trim corners follow the corner convention (front-right corner, building at x<=0, y>=0) and are
mitred solids that fill the square between the two straight runs.
Chimney: z = 0 is the roof surface reference; the brick shaft continues 1 m below (z = -1) so it
can be sunk into sloped roofs.
"""
import math

from mathutils import Matrix, Vector, geometry

from .. import config as C
from .. import facade as F
from ..meshutil import MeshBuilder

FAM = "roofs"
W = C.MODULE_W
T = C.WALL_T

WALL = "M_Wall_Cream"
TRIM = "M_Trim_White"
ROOF = "M_Roof_Slate"

# gable roof parameters
EAVE = 0.45          # eave / gable overhang
SLAB_T = 0.16        # slab thickness (perpendicular to the slope), ~0.18 incl. shingle butts
STEP = 0.05          # vertical shingle butt step
COURSE = 0.5         # shingle course length along the slope
LIP = 0.04           # how far the roof slab overhangs the fascia / barge boards
BOARD_T = 0.08       # fascia / barge board thickness
BOARD_H = 0.18       # fascia / barge board height (vertical)
RIDGE_W = 0.17       # ridge cap half width
RIB_PITCH = 0.6      # standing seam spacing (S12)
GABLES = [(6.0, 35.0), (9.0, 35.0), (12.0, 18.0)]


# =============================================================================== helpers
def _newell(pts):
    n = Vector((0.0, 0.0, 0.0))
    k = len(pts)
    for i in range(k):
        a, b = pts[i], pts[(i + 1) % k]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def _dedup(pts):
    out = []
    for p in pts:
        p = Vector(p)
        if not out or (p - out[-1]).length > 1e-6:
            out.append(p)
    while len(out) > 1 and (out[0] - out[-1]).length < 1e-6:
        out.pop()
    return out


def _poly(mb, pts, n_des, mat):
    """Add a planar polygon, auto-wound so its normal agrees with n_des."""
    pts = _dedup(pts)
    if len(pts) < 3:
        return
    n = _newell(pts)
    if n.length < 1e-9:
        return
    if n.dot(Vector(n_des)) < 0:
        pts = pts[::-1]
    mb.face(pts, mat)


def _area2(loop):
    n = len(loop)
    return sum(loop[i][0] * loop[(i + 1) % n][1] - loop[(i + 1) % n][0] * loop[i][1] for i in range(n)) * 0.5


def _clean2(loop):
    out = []
    for p in loop:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-7:
            out.append((float(p[0]), float(p[1])))
    while len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def _fill(mb, loops2d, to3d, n_des, mat):
    """Triangulate planar 2D loops (first = outline, rest = holes) and map them to 3D."""
    loops = [[Vector((p[0], p[1], 0.0)) for p in _clean2(l)] for l in loops2d]
    loops = [l for l in loops if len(l) >= 3]
    if not loops:
        return
    tris = geometry.tessellate_polygon(loops)
    flat = [p for l in loops for p in l]
    for t in tris:
        _poly(mb, [to3d(flat[i]) for i in t], n_des, mat)


def _edge_mat(mats, i):
    return mats[i] if isinstance(mats, (list, tuple)) else mats


def _extrude_x(mb, loop, mats, x0, x1, cap0=None, cap1=None):
    """Extrude a closed (y, z) loop along X. mats: one material or one per edge (None = skip)."""
    loop = _clean2(loop)
    n = len(loop)
    ccw = _area2(loop) > 0
    for i in range(n):
        m = _edge_mat(mats, i)
        if m is None:
            continue
        (ya, za), (yb, zb) = loop[i], loop[(i + 1) % n]
        dy, dz = yb - ya, zb - za
        ny, nz = (dz, -dy) if ccw else (-dz, dy)
        _poly(mb, [(x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)], (0.0, ny, nz), m)
    if cap0:
        _fill(mb, [loop], lambda p: Vector((x0, p.x, p.y)), (-1, 0, 0), cap0)
    if cap1:
        _fill(mb, [loop], lambda p: Vector((x1, p.x, p.y)), (1, 0, 0), cap1)


def _extrude_y(mb, loop, mats, y0, y1, inward=False):
    """Extrude a closed (x, z) loop along Y between y0 and y1 (sides only)."""
    loop = _clean2(loop)
    n = len(loop)
    ccw = _area2(loop) > 0
    s = -1.0 if inward else 1.0
    for i in range(n):
        m = _edge_mat(mats, i)
        if m is None:
            continue
        (xa, za), (xb, zb) = loop[i], loop[(i + 1) % n]
        dx, dz = xb - xa, zb - za
        nx, nz = (dz, -dx) if ccw else (-dz, dx)
        _poly(mb, [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], (s * nx, 0.0, s * nz), m)


def _lathe(mb, prof, mats, cx=0.0, cy=0.0, seg=12, phase=None):
    """Revolve an (r, z) polyline around a vertical axis. The visible side is RIGHT of travel
    in the (r, z) plane (r to the right, z up): go up the outside, inward across tops.
    mats: one material, or a list with one entry per edge (None = skip); an entry may be a
    tuple of materials to alternate around the axis (e.g. turbine vanes)."""
    if phase is None:
        phase = math.pi / seg
    for k in range(len(prof) - 1):
        m = _edge_mat(mats, k)
        if m is None:
            continue
        (ra, za), (rb, zb) = prof[k], prof[k + 1]
        nr, nz = zb - za, -(rb - ra)
        for i in range(seg):
            a0 = phase + 2 * math.pi * i / seg
            a1 = phase + 2 * math.pi * (i + 1) / seg
            am = (a0 + a1) * 0.5

            def P(r, a, z):
                return Vector((cx + r * math.cos(a), cy + r * math.sin(a), z))

            mi = m[i % len(m)] if isinstance(m, tuple) else m
            _poly(mb, [P(ra, a0, za), P(ra, a1, za), P(rb, a1, zb), P(rb, a0, zb)],
                  (nr * math.cos(am), nr * math.sin(am), nz), mi)


def _bar(mb, p0, p1, w, d, mat, up=(0, 0, 1), ends=False):
    """Square-ish beam between two points (w across, d along the 'up' side)."""
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    side = ax.cross(Vector(up))
    if side.length < 1e-6:
        side = ax.cross(Vector((1, 0, 0)))
    side.normalize()
    nrm = side.cross(ax).normalized()
    hw, hd = w * 0.5, d * 0.5

    def ring(p):
        return [p + side * hw + nrm * hd, p - side * hw + nrm * hd, p - side * hw - nrm * hd, p + side * hw - nrm * hd]

    a, b = ring(p0), ring(p1)
    for i in range(4):
        j = (i + 1) % 4
        out = (a[i] + a[j]) * 0.5 - p0
        _poly(mb, [a[i], a[j], b[j], b[i]], out, mat)
    if ends:
        _poly(mb, a, -ax, mat)
        _poly(mb, b, ax, mat)


def _mirror(mb, axis=0, about=0.0):
    """Mirrored copy of a MeshBuilder (winding reversed so normals stay outward)."""
    out = MeshBuilder()
    for v in mb.verts:
        v = v.copy()
        v[axis] = 2 * about - v[axis]
        out.verts.append(v)
    out.faces = [tuple(reversed(f)) for f in mb.faces]
    out.fmat = list(mb.fmat)
    out.mats = list(mb.mats)
    return out


# =============================================================================== trims
# Trim profiles: (u, z) with u = outward distance from the facade (y = -u), traversed from the
# back (u = 0) outwards, up, and back to u = 0 - i.e. CCW, outward side right of travel.
CORNICE_PROF = [(0.0, 0.0), (0.07, 0.0), (0.07, 0.09), (0.15, 0.13), (0.15, 0.2), (0.32, 0.25),
                (0.32, 0.35), (0.28, 0.4), (0.0, 0.4)]
BAND_PROF = [(0.0, 0.0), (0.07, 0.0), (0.1, 0.03), (0.1, 0.14), (0.06, 0.18), (0.0, 0.18)]
PLINTH_PROF = [(0.0, 0.0), (0.07, 0.0), (0.07, 0.41), (0.03, 0.45), (0.0, 0.45)]
PLINTH_DOOR_GAP = 1.30     # fits the 1.0 / 1.1 m door frames (outer |x| 0.59 / 0.64)


def _trim_straight(mb, prof, mat, x0=-W / 2, x1=W / 2, skip_bottom=False, caps=True):
    loop = [(-u, z) for (u, z) in prof]
    n = len(loop)
    mats = [mat] * (n - 1) + [None]          # closing edge = back face against the wall
    if skip_bottom:
        mats[0] = None
    _extrude_x(mb, loop, mats, x0, x1, cap0=mat if caps else None, cap1=mat if caps else None)


def _trim_corner(mb, prof, mat, skip_bottom=False):
    """Mitred outer-corner fill: at every height z the solid is the square [0,u]x[-u,0]."""
    for i in range(len(prof) - 1):
        if skip_bottom and i == 0:
            continue
        (ua, za), (ub, zb) = prof[i], prof[i + 1]
        nu, nz = zb - za, -(ub - ua)
        _poly(mb, [(0, -ua, za), (ua, -ua, za), (ub, -ub, zb), (0, -ub, zb)], (0, -nu, nz), mat)
        _poly(mb, [(ua, 0, za), (ua, -ua, za), (ub, -ub, zb), (ub, 0, zb)], (nu, 0, nz), mat)


def _build_trims(K):
    # ---- flat roof unit slab (scaled by the assembler)
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, 0.0, 0.5, 0.5, 0.2, "M_Roof_Flat")
    K.add("KIT_Roof_Flat_1x1", mb, FAM, "Roofs", meta=dict(unit=1.0, thickness=0.2))

    # ---- parapet: body + chamfered coping
    mb = MeshBuilder()
    mb.box(-W / 2, 0.0, 0.0, W / 2, T, 0.7, WALL, skip=("-z", "+z"))
    cap = [(-0.06, 0.7), (0.36, 0.7), (0.36, 0.77), (0.33, 0.8), (-0.03, 0.8), (-0.06, 0.77)]
    _extrude_x(mb, cap, TRIM, -W / 2, W / 2, cap0=TRIM, cap1=TRIM)
    K.add("KIT_Parapet_3m", mb, FAM, "Trims", meta=dict(height=0.8, module=W))

    # ---- parapet corner post (centred on the 0.3 x 0.3 wall corner block)
    mb = MeshBuilder()
    cx, cy = -T / 2, T / 2
    s = 0.23
    mb.box(cx - s, cy - s, 0.0, cx + s, cy + s, 0.74, WALL, skip=("-z", "+z"))
    capm = MeshBuilder()
    capm.box(cx - s - 0.04, cy - s - 0.04, 0.74, cx + s + 0.04, cy + s + 0.04, 0.84, TRIM)
    mb.extend(F.bevelled(capm, 0.025))
    top = MeshBuilder()
    top.box(cx - s + 0.05, cy - s + 0.05, 0.84, cx + s - 0.05, cy + s - 0.05, 0.88, TRIM, skip=("-z",))
    mb.extend(F.bevelled(top, 0.015))
    K.add("KIT_Parapet_Corner", mb, FAM, "Trims", meta=dict(height=0.88))

    # ---- cornice, floor band, plinth (+ mitred corners)
    for name, prof, mat, skip in (("Cornice", CORNICE_PROF, TRIM, False),
                                  ("FloorBand", BAND_PROF, TRIM, False),
                                  ("Plinth", PLINTH_PROF, "M_Wall_Concrete", True)):
        mb = MeshBuilder()
        _trim_straight(mb, prof, mat, skip_bottom=skip)
        K.add(f"KIT_{name}_3m", mb, FAM, "Trims", meta=dict(module=W, height=prof[-1][1]))
        mb = MeshBuilder()
        _trim_corner(mb, prof, mat, skip_bottom=skip)
        K.add(f"KIT_{name}_Corner", mb, FAM, "Trims", meta=dict(height=prof[-1][1]))

    # ---- plinth extras: door module (centred gap with return caps) and half module
    ph = PLINTH_PROF[-1][1]
    mb = MeshBuilder()
    g = PLINTH_DOOR_GAP / 2
    _trim_straight(mb, PLINTH_PROF, "M_Wall_Concrete", x0=-W / 2, x1=-g, skip_bottom=True)
    _trim_straight(mb, PLINTH_PROF, "M_Wall_Concrete", x0=g, x1=W / 2, skip_bottom=True)
    K.add("KIT_Plinth_Door_3m", mb, FAM, "Trims", meta=dict(module=W, height=ph, gap=PLINTH_DOOR_GAP))
    mb = MeshBuilder()
    _trim_straight(mb, PLINTH_PROF, "M_Wall_Concrete", x0=-W / 4, x1=W / 4, skip_bottom=True)
    K.add("KIT_Plinth_Half", mb, FAM, "Trims", meta=dict(module=W / 2, height=ph))


# =============================================================================== gable roofs
class _Gable:
    def __init__(self, S, pitch):
        self.S = float(S)
        self.c = self.S / 2
        self.pitch = pitch
        p = math.radians(pitch)
        self.p = p
        self.tp = math.tan(p)
        self.cp = math.cos(p)
        self.tv = SLAB_T / self.cp           # vertical slab thickness
        self.shingles = S < 10.0
        self.dv = STEP if self.shingles else 0.0
        self.h = self.c * self.tp            # underside apex height (= gable wall peak)

    def zu(self, y):                         # underside
        return self.tp * (y if y <= self.c else self.S - y)

    def zt(self, y):                         # top surface (bottom of each shingle course)
        return self.zu(y) + self.tv

    # ---- cross sections (y, z)
    def top_path(self):
        e, c = EAVE, self.c
        if self.shingles:
            n = max(3, int(round((c + e) / self.cp / COURSE)))
            ys = [-e + (c + e) * k / n for k in range(n + 1)]
            front = []
            for k in range(n):
                front.append((ys[k], self.zt(ys[k]) + self.dv))
                front.append((ys[k + 1], self.zt(ys[k + 1])))
        else:
            front = [(-e, self.zt(-e)), (c, self.zt(c))]
        back = [(self.S - y, z) for (y, z) in reversed(front)][1:]
        return front + back

    def slab(self):
        e, S, c = EAVE, self.S, self.c
        under = [(-e, self.zu(-e)), (-e + LIP, self.zu(-e + LIP)), (c, self.zu(c)),
                 (S + e - LIP, self.zu(S + e - LIP)), (S + e, self.zu(S + e))]
        top = list(reversed(self.top_path()))
        loop = under + top
        mats = [ROOF, TRIM, TRIM, ROOF] + [ROOF] * (len(top) + 1)
        return loop, mats

    def fascia(self, back=False):
        ya, yb = -EAVE + LIP, -EAVE + LIP + BOARD_T
        zb = self.zu(ya) - BOARD_H
        loop = [(ya, zb), (yb, zb), (yb, self.zu(yb)), (ya, self.zu(ya))]
        mats = [TRIM, TRIM, None, TRIM]       # bottom, back, (top hidden), front
        if back:
            loop = [(self.S - y, z) for (y, z) in loop]
        return loop, mats

    def ridge(self):
        c, w = self.c, RIDGE_W
        za = self.zt(c)
        zb = za - w * self.tp - 0.03
        z1 = self.zt(c - w) + self.dv + 0.06
        z2 = za + 0.1
        z3 = za + 0.13
        loop = [(c - w, zb), (c + w, zb), (c + w, z1), (c + w * 0.5, z2), (c, z3), (c - w * 0.5, z2), (c - w, z1)]
        mats = [None] + [ROOF] * 6
        return loop, mats

    def barge(self):
        ya, yb, c, H = -EAVE + LIP, self.S + EAVE - LIP, self.c, BOARD_H
        loop = [(ya, self.zu(ya)), (c, self.zu(c)), (yb, self.zu(yb)),
                (yb, self.zu(yb) - H), (c, self.zu(c) - H), (ya, self.zu(ya) - H)]
        mats = [None, None, None, TRIM, TRIM, None]
        return loop, mats

    def ribs(self, xs):
        """Standing-seam ribs on both slopes at the given x centres (S12 only)."""
        mb = MeshBuilder()
        if self.shingles:
            return mb
        e, c = EAVE, self.c
        s0 = 0.03
        s1 = (c - RIDGE_W + 0.06 + e) / self.cp
        rot = Matrix.Rotation(self.p, 4, "X")
        M = Matrix.Translation((0.0, -e, self.zt(-e))) @ rot
        loc = MeshBuilder()
        for x in xs:
            loc.box(x - 0.03, s0, 0.0, x + 0.03, s1, 0.05, ROOF, skip=("-z", "+y"))
        mb.extend(loc, M)
        mb.extend(_mirror(mb, axis=1, about=c))
        return mb

    def ridge_top(self):
        return self.zt(self.c) + 0.13


def _gable_mid(g):
    mb = MeshBuilder()
    x0, x1 = -W / 2, W / 2
    loop, mats = g.slab()
    _extrude_x(mb, loop, mats, x0, x1)
    for back in (False, True):
        l, m = g.fascia(back)
        _extrude_x(mb, l, m, x0, x1)
    l, m = g.ridge()
    _extrude_x(mb, l, m, x0, x1)
    n = int(round(W / RIB_PITCH))
    mb.extend(g.ribs([x0 + RIB_PITCH * (k + 0.5) for k in range(n)]))
    return mb


def _gable_endL(g):
    """-X end: overhang x in [-EAVE, 0] with capped slab, ridge and barge boards."""
    mb = MeshBuilder()
    x0, x1 = -EAVE, 0.0
    xb0, xb1 = -EAVE + LIP, -EAVE + LIP + BOARD_T
    loop, mats = g.slab()
    _extrude_x(mb, loop, mats, x0, x1, cap0=ROOF)
    for back in (False, True):
        l, m = g.fascia(back)
        _extrude_x(mb, l, m, xb0, x1, cap0=TRIM)
    l, m = g.ridge()
    _extrude_x(mb, l, m, x0, x1, cap0=ROOF)
    l, m = g.barge()
    barge = MeshBuilder()
    _extrude_x(barge, l, m, xb0, xb1, cap0=TRIM, cap1=TRIM)
    mb.extend(barge)
    mb.extend(g.ribs([-RIB_PITCH / 2]))
    return mb


def _gable_wall(g):
    S, h, tp = g.S, g.h, g.tp
    mb = MeshBuilder()
    # attic vent (pentagon: rectangle with a peaked head following the roof pitch)
    if S < 7:
        vw, vh, vz, nl = 0.62, 0.42, 0.62, 3
    elif S < 10:
        vw, vh, vz, nl = 0.8, 0.56, 0.95, 4
    else:
        vw, vh, vz, nl = 1.3, 0.42, 0.55, 3
    peak = vz + vh + vw / 2 * tp
    hole = [(-vw / 2, vz), (vw / 2, vz), (vw / 2, vz + vh), (0.0, peak), (-vw / 2, vz + vh)]
    tri = [(-S / 2, 0.0), (S / 2, 0.0), (0.0, h)]
    # wall body (outer face with the vent hole, inner face, sloped tops, bottom)
    _fill(mb, [tri, hole], lambda p: Vector((p.x, 0.0, p.y)), (0, -1, 0), WALL)
    _fill(mb, [tri], lambda p: Vector((p.x, T, p.y)), (0, 1, 0), WALL)
    sp, cp = math.sin(g.p), math.cos(g.p)
    _poly(mb, [(-S / 2, 0, 0), (0, 0, h), (0, T, h), (-S / 2, T, 0)], (-sp, 0, cp), WALL)
    _poly(mb, [(S / 2, 0, 0), (S / 2, T, 0), (0, T, h), (0, 0, h)], (sp, 0, cp), WALL)
    _poly(mb, [(-S / 2, 0, 0), (S / 2, 0, 0), (S / 2, T, 0), (-S / 2, T, 0)], (0, 0, -1), WALL)
    # vent frame (stands proud by FD), dark recess, thin louvers, sill
    FW, FD, VD = 0.08, 0.05, 0.16
    d = FW * (1.0 / g.cp - g.tp)
    outer = [(-vw / 2 - FW, vz - FW), (vw / 2 + FW, vz - FW), (vw / 2 + FW, vz + vh + d),
             (0.0, peak + FW / g.cp), (-vw / 2 - FW, vz + vh + d)]
    _fill(mb, [outer, hole], lambda p: Vector((p.x, -FD, p.y)), (0, -1, 0), TRIM)
    _extrude_y(mb, outer, TRIM, -FD, 0.0)
    _extrude_y(mb, hole, TRIM, -FD, 0.0, inward=True)
    _extrude_y(mb, hole, "M_Trim_Dark", 0.0, VD, inward=True)
    _fill(mb, [hole], lambda p: Vector((p.x, VD, p.y)), (0, -1, 0), "M_Trim_Dark")
    lou = MeshBuilder()
    gap = vh / nl
    for i in range(nl):
        zl = vz + gap * (i + 0.3)
        prof = [(0.0, zl), (0.07, zl + 0.045), (0.07, zl + 0.08), (0.0, zl + 0.035)]
        _extrude_x(lou, prof, [TRIM, None, TRIM, TRIM], -vw / 2, vw / 2)
    mb.extend(lou)
    mb.box(-vw / 2 - FW - 0.05, -0.12, vz - FW - 0.07, vw / 2 + FW + 0.05, 0.0, vz - FW, TRIM, skip=("+y",))
    # frieze band along the base of the gable (separates it from the floor below); its ends are
    # cut along the pitch so they tuck flush under the roof soffit at the building corners.
    hb, bd = 0.15, 0.06
    xb = S / 2 - hb / tp
    band = [(-S / 2, 0.0), (S / 2, 0.0), (xb, hb), (-xb, hb)]
    _fill(mb, [band], lambda p: Vector((p.x, -bd, p.y)), (0, -1, 0), TRIM)
    _extrude_y(mb, band, [TRIM, TRIM, TRIM, TRIM], -bd, 0.0)
    return mb


# ---- ribbed (industrial) gable infill: matches walls._cladding exactly
CLAD_MAJOR = dict(wb=0.2, wt=0.085, d=0.07)      # = walls._vrib defaults
CLAD_MINOR = dict(wb=0.07, wt=0.0, d=0.022)       # walls MINOR is 0.07/0.04/0.022; a V profile
                                                  # reads the same above the flashing for 2 tris less
FLASH_H, FLASH_D = 0.12, 0.10                     # base flashing over the wall rib tops
RIB_SINK = 0.02                                   # rib tops end this far above the rake (in the slab)


def _gable_wall_ribbed(g):
    """KIT_Gable_S12: triangular infill with box-profile cladding, base flashing, louvre vent."""
    S, h, tp = g.S, g.h, g.tp
    hs = S / 2
    mb = MeshBuilder()
    MD = "M_Metal_Dark"
    tri = [(-hs, 0.0), (hs, 0.0), (0.0, h)]
    _fill(mb, [tri], lambda p: Vector((p.x, 0.0, p.y)), (0, -1, 0), WALL)
    _fill(mb, [tri], lambda p: Vector((p.x, T, p.y)), (0, 1, 0), WALL)
    sp, cp = math.sin(g.p), math.cos(g.p)
    _poly(mb, [(-hs, 0, 0), (0, 0, h), (0, T, h), (-hs, T, 0)], (-sp, 0, cp), WALL)
    _poly(mb, [(hs, 0, 0), (hs, T, 0), (0, T, h), (0, 0, h)], (sp, 0, cp), WALL)
    _poly(mb, [(-hs, 0, 0), (hs, 0, 0), (hs, T, 0), (-hs, T, 0)], (0, 0, -1), WALL)

    # base flashing: ends cut along the pitch so they tuck flush under the gable soffit
    xb = hs - FLASH_H / tp
    band = [(-hs, 0.0), (hs, 0.0), (xb, FLASH_H), (-xb, FLASH_H)]
    _fill(mb, [band], lambda p: Vector((p.x, -FLASH_D, p.y)), (0, -1, 0), MD)
    _extrude_y(mb, band, MD, -FLASH_D, 0.0)

    def rake(x):
        return (hs - abs(x)) * tp

    def rib(xc, wb, wt, d):
        if wt > 0:
            prof = [(xc - wb / 2, 0.0), (xc - wt / 2, -d), (xc + wt / 2, -d), (xc + wb / 2, 0.0)]
        else:
            prof = [(xc - wb / 2, 0.0), (xc, -d), (xc + wb / 2, 0.0)]
        z0 = [min(FLASH_H, rake(p[0])) for p in prof]
        z1 = [min(rake(p[0]) + RIB_SINK, h) for p in prof]     # piece stays within z [0, ridge]
        if min(b - a for a, b in zip(z0, z1)) < RIB_SINK + 0.03:
            return 0
        mb.wall_var(prof, z0, z1, WALL)      # normals right of travel = outward; ends hidden
        return 1

    nmaj = sum(rib(-hs + 0.25 + 0.5 * k, **CLAD_MAJOR) for k in range(int(round(S / 0.5))))
    nmin = sum(rib(-hs + 0.5 * k, **CLAD_MINOR) for k in range(int(round(S / 0.5)) + 1))

    # surface-mounted louvre vent (stands proud of the ribs, so they simply run behind it)
    vx, vz0, vz1, vd, fw, yb = 0.5, 0.55, 1.15, 0.14, 0.08, -0.08
    o = [(-vx, vz0), (vx, vz0), (vx, vz1), (-vx, vz1)]
    i = [(-vx + fw, vz0 + fw), (vx - fw, vz0 + fw), (vx - fw, vz1 - fw), (-vx + fw, vz1 - fw)]
    for k in range(4):
        a, b = o[k], o[(k + 1) % 4]
        c, d = i[(k + 1) % 4], i[k]
        _poly(mb, [(a[0], -vd, a[1]), (b[0], -vd, b[1]), (c[0], -vd, c[1]), (d[0], -vd, d[1])], (0, -1, 0), TRIM)
    _extrude_y(mb, o, TRIM, -vd, 0.0)
    _extrude_y(mb, i, "M_Trim_Dark", -vd, yb, inward=True)
    ix0, iz0, ix1, iz1 = i[0][0], i[0][1], i[2][0], i[2][1]
    _poly(mb, [(ix0, yb, iz0), (ix1, yb, iz0), (ix1, yb, iz1), (ix0, yb, iz1)], (0, -1, 0), "M_Trim_Dark")
    nl = 3
    p = (iz1 - iz0) / nl
    ys = -vd + 0.015
    for k in range(nl):
        zt = iz1 - k * p - 0.02
        zb = zt - p + 0.04
        _poly(mb, [(ix0, ys, zb), (ix1, ys, zb), (ix1, yb, zt), (ix0, yb, zt)], (0, -1, 0.6), TRIM)
        _poly(mb, [(ix0, ys, zb), (ix1, ys, zb), (ix1, yb, zb), (ix0, yb, zb)], (0, 0, -1), TRIM)
    return mb, nmaj, nmin


def _build_gables(K):
    for S, pitch in GABLES:
        g = _Gable(S, pitch)
        tag = f"S{int(S)}"
        meta = dict(span=S, pitch_deg=pitch, eave=EAVE, ridge_under_z=round(g.h, 4),
                    ridge_top_z=round(g.ridge_top(), 4), module=W, board_h=BOARD_H)
        K.add(f"KIT_Roof_Gable_{tag}_Mid", _gable_mid(g), FAM, "Roofs", meta=dict(meta, part="mid"))
        endl = _gable_endL(g)
        K.add(f"KIT_Roof_Gable_{tag}_EndL", endl, FAM, "Roofs", meta=dict(meta, part="endL"))
        K.add(f"KIT_Roof_Gable_{tag}_EndR", _mirror(endl, axis=0, about=0.0), FAM, "Roofs",
              meta=dict(meta, part="endR"))
        gm = dict(span=S, pitch_deg=pitch, height=round(g.h, 4), thickness=T)
        if g.shingles:
            K.add(f"KIT_Gable_{tag}", _gable_wall(g), FAM, "Roofs", meta=dict(gm, cladding="smooth"))
        else:
            mb, nmaj, nmin = _gable_wall_ribbed(g)
            K.add(f"KIT_Gable_{tag}", mb, FAM, "Roofs",
                  meta=dict(gm, cladding="ribbed", rib_pitch=0.5, rib_x0=round(-S / 2 + 0.25, 3),
                            flashing_h=FLASH_H, flashing_d=FLASH_D))


# =============================================================================== rooftop
def _ac_unit():
    mb = MeshBuilder()
    for y in (-0.3, 0.3):
        mb.box(-0.58, y - 0.05, 0.0, 0.58, y + 0.05, 0.08, "M_Metal_Dark", skip=("-z",))
    body = MeshBuilder()
    body.box(-0.6, -0.42, 0.08, 0.6, 0.45, 0.7, "M_Metal")
    mb.extend(F.bevelled(body, 0.035))
    # fan shroud + grill on top
    fx, r0, r1 = 0.22, 0.33, 0.28
    _lathe(mb, [(r0, 0.69), (r0, 0.8), (r1, 0.8), (r1, 0.74), (0.0, 0.74)],
           ["M_Metal_Dark", "M_Metal_Dark", "M_Metal_Dark", "M_Trim_Dark"], cx=fx, seg=14)
    for a in (0.0, math.pi / 2):
        dx, dy = math.cos(a) * r1, math.sin(a) * r1
        _bar(mb, (fx - dx, -dy, 0.775), (fx + dx, dy, 0.775), 0.04, 0.04, "M_Metal")
    _lathe(mb, [(0.07, 0.74), (0.07, 0.79), (0.0, 0.79)], "M_Metal", cx=fx, seg=8)
    # front louvre slats + side service panel
    for i in range(5):
        z = 0.2 + i * 0.09
        mb.box(-0.5, -0.45, z, -0.02, -0.42, z + 0.04, "M_Metal_Dark", skip=("+y",))
    mb.box(0.42, -0.45, 0.36, 0.46, -0.42, 0.46, "M_Metal_Dark", skip=("+y",))
    mb.box(0.12, -0.44, 0.22, 0.5, -0.42, 0.58, "M_Metal", skip=("+y",))
    return mb


def _bar3(mb, p0, p1, w, mat, out):
    """Triangular-section strut (side w) between two points; one flat face looks along *out*."""
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    o = Vector(out)
    o = (o - ax * o.dot(ax)).normalized()
    side = ax.cross(o).normalized()
    r = w / math.sqrt(3.0)

    def ring(p):
        return [p + o * (r / 2) + side * (w / 2), p + o * (r / 2) - side * (w / 2), p - o * r]

    a, b = ring(p0), ring(p1)
    for i in range(3):
        j = (i + 1) % 3
        _poly(mb, [a[i], a[j], b[j], b[i]], (a[i] + a[j]) * 0.5 - (a[0] + a[1] + a[2]) / 3, mat)


def _water_tank():
    """Classic wooden water tower: 4 steel legs with X bracing, closed deck, hooped tank, cone cap.

    <= 450 tris: triangular-section braces, 4 ladder rungs, single n-gon tank bottom. The deck keeps
    its top face so the corners outside the round tank are closed when seen from above.
    """
    mb = MeshBuilder()
    MD = "M_Metal_Dark"
    L = 0.72                 # leg half spacing
    zt = 1.5                 # tank bottom
    # legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box(sx * L - 0.07, sy * L - 0.07, 0.0, sx * L + 0.07, sy * L + 0.07, zt - 0.1, MD,
                   skip=("-z", "+z"))
    # cross bracing on all four sides (flat face outward)
    zb0, zb1 = 0.2, zt - 0.2
    for (ax, ay, bx, by) in ((-L, -L, L, -L), (L, -L, L, L), (L, L, -L, L), (-L, L, -L, -L)):
        out = ((ax + bx) * 0.5, (ay + by) * 0.5, 0.0)
        _bar3(mb, (ax, ay, zb0), (bx, by, zb1), 0.06, MD, out)
        _bar3(mb, (ax, ay, zb1), (bx, by, zb0), 0.06, MD, out)
    # deck (closed top: its corners stick out past the round tank)
    mb.box(-L - 0.2, -L - 0.2, zt - 0.1, L + 0.2, L + 0.2, zt, MD)
    # wooden tank with steel hoops, conical cap, finial
    R, Rh = 1.1, 1.15
    seg = 12
    wood, hoop, capm = "M_Fence_Wood", MD, "M_Trim_Wood"
    prof = [(R, zt), (R, zt + 0.3), (Rh, zt + 0.33), (Rh, zt + 0.4), (R, zt + 0.43),
            (R, zt + 1.15), (Rh, zt + 1.18), (Rh, zt + 1.25), (R, zt + 1.28), (R, zt + 1.85),
            (R + 0.14, zt + 1.85), (R + 0.14, zt + 1.93), (0.0, zt + 2.6)]
    mats = [wood, hoop, hoop, hoop, wood, hoop, hoop, hoop, wood, capm, capm, capm]
    _lathe(mb, prof, mats, seg=seg)
    ph = math.pi / seg
    ring = [Vector((R * math.cos(ph + 2 * math.pi * k / seg), R * math.sin(ph + 2 * math.pi * k / seg), zt))
            for k in range(seg)]
    _poly(mb, ring, (0, 0, -1), wood)                      # tank bottom (one n-gon)
    _lathe(mb, [(0.07, zt + 2.5), (0.07, zt + 2.66), (0.0, zt + 2.74)], MD, seg=6)
    # small access ladder on the front
    lx = 0.32
    for x in (-lx / 2, lx / 2):
        mb.box(x - 0.025, -R - 0.12, zt + 0.1, x + 0.025, -R - 0.07, zt + 1.85, MD, skip=("-z",))
    for i in range(4):
        z = zt + 0.4 + i * 0.4
        mb.box(-lx / 2, -R - 0.11, z, lx / 2, -R - 0.08, z + 0.03, MD, skip=("-x", "+x"))
    return mb


def _roof_vent():
    mb = MeshBuilder()
    base = MeshBuilder()
    base.box(-0.28, -0.28, 0.0, 0.28, 0.28, 0.05, "M_Metal_Dark", skip=("-z",))
    mb.extend(F.bevelled(base, 0.015))
    m, vane = "M_Metal", ("M_Metal", "M_RollerDoor")
    # neck, flared collar, turbine globe with alternating vanes, top cap
    _lathe(mb, [(0.13, 0.05), (0.13, 0.33), (0.21, 0.38), (0.21, 0.41)], m, seg=10)
    _lathe(mb, [(0.21, 0.41), (0.25, 0.47), (0.27, 0.55), (0.25, 0.63), (0.19, 0.7), (0.1, 0.735)],
           [vane, vane, vane, vane, vane], seg=10)
    _lathe(mb, [(0.1, 0.735), (0.1, 0.75), (0.0, 0.76)], "M_Metal_Dark", seg=10)
    _lathe(mb, [(0.04, 0.745), (0.04, 0.8), (0.0, 0.81)], "M_Metal_Dark", seg=6)   # foot sunk into the cap
    return mb


def _skylight():
    mb = MeshBuilder()
    curb = MeshBuilder()
    curb.box(-0.75, -0.75, 0.0, 0.75, 0.75, 0.24, TRIM, skip=("-z",))
    mb.extend(F.bevelled(curb, 0.03))
    a, b, z0, z1 = 0.66, 0.3, 0.24, 0.5
    g = "M_Glass"
    P = lambda x, y, z: Vector((x, y, z))
    _poly(mb, [P(-a, -a, z0), P(a, -a, z0), P(b, -b, z1), P(-b, -b, z1)], (0, -1, 1), g)
    _poly(mb, [P(a, -a, z0), P(a, a, z0), P(b, b, z1), P(b, -b, z1)], (1, 0, 1), g)
    _poly(mb, [P(a, a, z0), P(-a, a, z0), P(-b, b, z1), P(b, b, z1)], (0, 1, 1), g)
    _poly(mb, [P(-a, a, z0), P(-a, -a, z0), P(-b, -b, z1), P(-b, b, z1)], (-1, 0, 1), g)
    _poly(mb, [P(-b, -b, z1), P(b, -b, z1), P(b, b, z1), P(-b, b, z1)], (0, 0, 1), g)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        _bar(mb, (sx * a, sy * a, z0), (sx * b, sy * b, z1 + 0.01), 0.06, 0.05, TRIM,
             up=(sx, sy, 1.5))
    top = MeshBuilder()
    top.box(-b - 0.03, -b - 0.03, z1 - 0.01, b + 0.03, b + 0.03, z1 + 0.04, TRIM, skip=("-z",))
    mb.extend(F.bevelled(top, 0.015))
    return mb


def _roof_access():
    mb = MeshBuilder()
    s, H = 1.14, 2.32
    hole = (-0.45, 0.0, 0.45, 2.05)
    front = MeshBuilder()
    F.panel(front, -s, s, 0.0, H, [hole], WALL, y=0.0, facing=-1)
    F.door(front, hole)
    mb.extend(front, Matrix.Translation((0.0, -s, 0.0)))
    # remaining walls
    _poly(mb, [(s, -s, 0), (s, s, 0), (s, s, H), (s, -s, H)], (1, 0, 0), WALL)
    _poly(mb, [(-s, s, 0), (-s, -s, 0), (-s, -s, H), (-s, s, H)], (-1, 0, 0), WALL)
    _poly(mb, [(s, s, 0), (-s, s, 0), (-s, s, H), (s, s, H)], (0, 1, 0), WALL)
    # coping slab + inset roof pad
    cap = MeshBuilder()
    cap.box(-1.2, -1.2, H, 1.2, 1.2, 2.44, TRIM)
    mb.extend(F.bevelled(cap, 0.03))
    pad = MeshBuilder()
    pad.box(-1.08, -1.08, 2.44, 1.08, 1.08, 2.5, "M_Roof_Flat", skip=("-z",))
    mb.extend(F.bevelled(pad, 0.02))
    # wall lamp above the door + side vent grille
    mb.box(-0.12, -s - 0.12, 2.12, 0.12, -s, 2.2, "M_Metal_Dark", skip=("+y",))
    mb.box(-0.08, -s - 0.1, 2.06, 0.08, -s - 0.02, 2.12, "M_Light_Emit", skip=("+y", "+z"))
    for i in range(4):
        z = 1.55 + i * 0.12
        mb.box(s, -0.4, z, s + 0.04, 0.4, z + 0.05, "M_Metal_Dark", skip=("-x",))
    return mb


def _chimney():
    mb = MeshBuilder()
    shaft = MeshBuilder()
    shaft.box(-0.4, -0.4, -1.0, 0.4, 0.4, 2.0, "M_Wall_Brick", skip=("-z", "+z"))
    mb.extend(F.bevelled(shaft, 0.025))
    band = MeshBuilder()
    band.box(-0.46, -0.46, 1.86, 0.46, 0.46, 2.02, "M_Wall_Brick")
    mb.extend(F.bevelled(band, 0.02))
    mb.box(-0.4, -0.4, 2.02, 0.4, 0.4, 2.12, "M_Wall_Brick", skip=("-z", "+z"))
    cap = MeshBuilder()
    cap.box(-0.48, -0.48, 2.12, 0.48, 0.48, 2.24, "M_Wall_Concrete")
    mb.extend(F.bevelled(cap, 0.025))
    for x in (-0.17, 0.17):
        _lathe(mb, [(0.12, 2.24), (0.1, 2.4), (0.07, 2.4), (0.07, 2.33)], "M_Roof_Terracotta", cx=x, seg=8)
        _lathe(mb, [(0.07, 2.33), (0.0, 2.33)], "M_Trim_Dark", cx=x, seg=8)
    return mb


def _build_rooftop(K):
    K.add("KIT_Roof_AC_Unit", _ac_unit(), FAM, "Rooftop", meta=dict(size="1.2x0.9x0.8"))
    K.add("KIT_Roof_WaterTank", _water_tank(), FAM, "Rooftop", meta=dict(diameter=2.2))
    K.add("KIT_Roof_Vent", _roof_vent(), FAM, "Rooftop")
    K.add("KIT_Roof_Skylight", _skylight(), FAM, "Rooftop", meta=dict(size="1.5x1.5"))
    K.add("KIT_Roof_Access", _roof_access(), FAM, "Rooftop", meta=dict(size="2.4x2.4x2.5"))
    K.add("KIT_Chimney", _chimney(), FAM, "Rooftop", meta=dict(below=1.0, height=2.4))


def build(K):
    _build_trims(K)
    _build_gables(K)
    _build_rooftop(K)
