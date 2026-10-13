"""Landmark: TOWN SQUARE (north bridgehead, end of the Zoo Boulevard axis) - the town's postcard.

PLAN (site frame = world axes, origin = site center (-53, 73) = the clock tower; +x east, +y north)
--------------------------------------------------------------------------------------------------
Site polygon (local): SW (-25,-11), SE (25,-21), NE (25,17), NW (-25,17). Canal Street runs ~5 m north
of the north edge, the canal quay ~8 m south of the south edge, the backs of the Main Street block
~8 m east of the east edge. The pet shop sits 120 m due south across the canal on the same x.

* PAVING (z = 0.15, sidewalk level): warm M_Plaza field with an M_Plaza_Accent pattern that reads from
  the gameplay camera and from above: a 1 m border band, a 16-ray sunburst + ring around the tower,
  and two pairs of accent stripes marking the two AXES:
    - NW axis  -> Zoo Boulevard (direction (-0.4908, 0.8713)); the boulevard vista ends on the tower.
    - S axis   -> Green Walk / Maple Green / the pet shop door across the canal.
  Both axis corridors (5 m) stay free of furniture; the SE corner stays open toward the quay
  promenade and the Central Bridge.
  RAMPS: the slab sits 0.19 m above the surrounding concrete / grass, so the edge band is ramped (2.5 m,
  ~6 %, side flares) on the open approaches: the S axis, the SE corner (hip-joined across the corner)
  and the NW boulevard mouth. The pattern inlays follow the ramp planes. Nothing stands on a ramp
  (checked at build time -> report 'ramp_conflicts').
* CLOCK TOWER (hero, custom ~17.5 m): stepped stone plinth, cream base course, brick shaft with
  cream quoins, a string course and arched windows, a cream clock stage with four big clock faces
  (south face looks straight at the pet shop), an open brick belfry with a brass bell, and a
  bell-cast copper (M_Roof_Green) spire with a gilded ball and weathervane. Door on the north face.
* FOUNTAIN (custom) in the west field: octagonal basin, two tiers, falling water sheets; benches.
* MARKET (custom stalls with striped canopies in three alternating colours red / teal / yellow, 5 stalls:
  fruit / flowers / veg / bakery / pet treats)
  along the north edge east of the NW axis, facing south into the square; their backs screen Canal
  Street traffic. Festoon lights zig-zag over the canopies on slim poles.
* CAFE: a teal coffee kiosk (custom) on the west edge with kit cafe tables between it, the fountain
  and the quay - the sunny water-side terrace.
* EDGES: flag poles (custom) flanking both axis gateways, kit park lamps around the tower ring and
  on the edges, trees in round seat-wall planters (custom), hedges + benches screening the backs of
  the Main Street block, bike racks at the north-east entrance, bins next to the benches.
GAMEPLAY: two big open fields (east field + fountain field) for round-ups, clear entrances from all
sides (boulevard corner, Canal Street, the quay, the bridge side), a 2.5 m walk behind the market,
pockets behind the east hedges for small animals, perches for parrots on canopies / the belfry.
Custom tris ~11k (tower ~4.1k); everything else is kit (lamps, benches, bins, cafe tables, planters,
trees, hedges, bike racks, mailbox).

Shared geometry helpers for the downtown landmark builder live here too (marina.py / courts.py
import them): shared-mesh instancing with recolor, lathe / tube / box helpers, XZ extrusion,
convex clipping, string lights and striped canopies.
"""
import math

import bpy
from mathutils import Matrix, Vector

from .. import config as C
from .. import facade as F
from .. import geom2d as G
from .. import palette
from .. import scene
from ..meshutil import MeshBuilder

TAU = 2.0 * math.pi
PZ = C.SIDEWALK_Z           # plaza top (sidewalk level)
AXIS_NW = Vector((-0.4908, 0.8713))

AWN = "M_Awning_Red"        # recolorable placeholder (stall canopies, flags)
CREAM = "M_Awning_Cream"


# =============================================================================== generic helpers
def v3(x, y, z):
    return Vector((float(x), float(y), float(z)))


def face_rot(dx, dy):
    """Z rotation that turns a piece's front (-Y) toward direction (dx, dy)."""
    return math.atan2(dx, -dy)


def poly(mb, pts, mat, eps=1e-6):
    """mb.face() dropping repeated points (collapsed quads -> triangles)."""
    out = []
    for p in pts:
        p = Vector(p)
        if not out or (p - out[-1]).length > eps:
            out.append(p)
    while len(out) > 1 and (out[0] - out[-1]).length <= eps:
        out.pop()
    if len(out) >= 3:
        mb.face(out, mat)


def face_n(mb, pts, mat, want):
    """Planar polygon whose normal points along *want* (winding fixed automatically)."""
    Q = [Vector(p) for p in pts]
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    if n.dot(Vector(want)) < 0:
        Q.reverse()
    poly(mb, Q, mat)


def lathe(mb, prof, mat, seg=8, cx=0.0, cy=0.0, phase=0.0, mats=None):
    """Surface of revolution around a vertical axis. prof [(r, z)] walked from the bottom/outside up
    and over to the top/inside gives outward normals; r == 0 collapses onto the axis."""
    rings = []
    for r, z in prof:
        rings.append([v3(cx + r * math.cos(phase + TAU * j / seg), cy + r * math.sin(phase + TAU * j / seg), z)
                      for j in range(seg)])
    for i in range(len(prof) - 1):
        m = mats[i] if mats else mat
        for j in range(seg):
            k = (j + 1) % seg
            poly(mb, [rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]], m)


def tube(mb, p0, p1, r, mat, seg=6, cap0=False, cap1=True, r1=None):
    """Cylinder between two 3D points."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    sub = MeshBuilder()
    sub.cylinder(0.0, 0.0, 0.0, d.length, r, mat, seg=seg, cap_top=cap1, cap_bottom=cap0, r_top=r1)
    M = Matrix.Translation(p0) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    mb.extend(sub, M)


def bbox(mb, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, skip=()):
    """Axis-aligned box, optionally chamfered (soft stylized edge)."""
    sub = MeshBuilder()
    sub.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
    if bevel > 0:
        sub = F.bevelled(sub, bevel)
    mb.extend(sub)


def rbox(mb, center, size, mat, rot_z=0.0, bevel=0.0, skip=(), rot=None):
    """Box of *size* centred at *center*, rotated about Z (or by a full matrix *rot*)."""
    sx, sy, sz = size
    sub = MeshBuilder()
    sub.box(-sx / 2, -sy / 2, -sz / 2, sx / 2, sy / 2, sz / 2, mat, skip=skip)
    if bevel > 0:
        sub = F.bevelled(sub, bevel)
    R = rot.to_4x4() if rot is not None else Matrix.Rotation(rot_z, 4, "Z")
    mb.extend(sub, Matrix.Translation(Vector(center)) @ R)


def beam(mb, a, b, w, t, mat, up=(0.0, 0.0, 1.0), bevel=0.0):
    """Rectangular beam from point a to b: width w across, thickness t along 'up'."""
    a, b = Vector(a), Vector(b)
    d = b - a
    x = d.normalized()
    u = Vector(up)
    y = u.cross(x)
    if y.length < 1e-6:
        y = Vector((0.0, 1.0, 0.0)).cross(x)
    y.normalize()
    z = x.cross(y)
    R = Matrix((x, y, z)).transposed()
    rbox(mb, (a + b) / 2, (d.length, w, t), mat, rot=R, bevel=bevel)


def gem(mb, c, r, h, mat, seg=5, phase=0.0):
    """Small bipyramid (fruit / flower head / bulb)."""
    lathe(mb, [(0.0, c[2] - h), (r, c[2]), (0.0, c[2] + h)], mat, seg=seg, cx=c[0], cy=c[1], phase=phase)


def M_front(y0):
    """Map a 'facade frame' (u = x, v = z, h = out of the facade toward -Y) onto the plane y = y0."""
    return Matrix(((1, 0, 0, 0), (0, 0, -1, y0), (0, 1, 0, 0), (0, 0, 0, 1)))


def extrude_xz(mb, pts, y0, y1, mat, side=None, back=True):
    """Prism of a simple (possibly concave) 2D polygon in the XZ plane, front face at y0 (normal -Y),
    back face at y1 > y0 (normal +Y)."""
    sub = MeshBuilder()
    sub.prism([(p[0], p[1]) for p in pts], -(y1 - y0), 0.0, mat, side or mat, bottom=mat if back else None)
    mb.extend(sub, M_front(y0))


def disc_front(mb, cx, cz, r, y0, depth, mat, seg=16, side=None):
    """Round plate on a facade: front face at y0 - depth (normal -Y), side wall back to y0."""
    sub = MeshBuilder()
    sub.cylinder(cx, cz, 0.0, depth, r, side or mat, seg=seg, cap_top=False)
    sub.face([v3(cx + r * math.cos(TAU * i / seg), cz + r * math.sin(TAU * i / seg), depth) for i in range(seg)], mat)
    mb.extend(sub, M_front(y0))


def ring_front(mb, cx, cz, r0, r1, y0, depth, mat, seg=16):
    """Flat annulus (bezel) standing proud of a facade by *depth*."""
    sub = MeshBuilder()
    for i in range(seg):
        a0, a1 = TAU * i / seg, TAU * (i + 1) / seg
        o0, o1 = (cx + r1 * math.cos(a0), cz + r1 * math.sin(a0)), (cx + r1 * math.cos(a1), cz + r1 * math.sin(a1))
        i0, i1 = (cx + r0 * math.cos(a0), cz + r0 * math.sin(a0)), (cx + r0 * math.cos(a1), cz + r0 * math.sin(a1))
        sub.face([v3(*o0, depth), v3(*o1, depth), v3(*i1, depth), v3(*i0, depth)], mat)
        sub.face([v3(*o0, 0), v3(*o1, 0), v3(*o1, depth), v3(*o0, depth)], mat)     # outer rim
        sub.face([v3(*i1, 0), v3(*i0, 0), v3(*i0, depth), v3(*i1, depth)], mat)     # inner rim
    mb.extend(sub, M_front(y0))


def clip_convex(subject, clip):
    """Sutherland-Hodgman: clip polygon *subject* by the CONVEX polygon *clip* (both 2D, CCW clip)."""
    clip = G.ensure_ccw([G.V(p) for p in clip])
    out = [G.V(p) for p in subject]
    n = len(clip)
    for i in range(n):
        a, b = clip[i], clip[(i + 1) % n]
        e = b - a
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return e.x * (p.y - a.y) - e.y * (p.x - a.x) >= -1e-9

        def cut(p, q):
            d = q - p
            den = e.x * d.y - e.y * d.x
            if abs(den) < 1e-12:
                return q
            t = (e.x * (a.y - p.y) - e.y * (a.x - p.x)) / den
            return p + d * t
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q):
                if not inside(p):
                    out.append(cut(p, q))
                out.append(q)
            elif inside(p):
                out.append(cut(p, q))
    return out


def inset_convex(P, d):
    """Offset a CCW convex polygon inward by d (mitred)."""
    P = G.ensure_ccw([G.V(p) for p in P])
    n = len(P)
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        t = (b - a).normalized()
        lines.append((a + G.left_normal(t) * d, t))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        r = G.line_intersect(p1, d1, p2, d2)
        out.append(p1 + d1 * r[0] if r else p2)
    return out


def _clean(pts, eps=1e-4):
    out = []
    for p in pts:
        if not out or (p - out[-1]).length > eps:
            out.append(p)
    while len(out) > 1 and (out[0] - out[-1]).length <= eps:
        out.pop()
    return out


def clip_half(poly_, a, e, keep_left=True):
    """Clip a polygon by the half-plane left (keep_left) or right of the line through a along e."""
    a, e = G.V(a), G.V(e)
    sg = 1.0 if keep_left else -1.0

    def side(p):
        return sg * (e.x * (p.y - a.y) - e.y * (p.x - a.x))
    out = []
    P = [G.V(p) for p in poly_]
    for j in range(len(P)):
        p, q = P[j - 1], P[j]
        sp, sq = side(p), side(q)
        if sq >= -1e-9:
            if sp < -1e-9:
                out.append(p + (q - p) * (sp / (sp - sq)))
            out.append(q)
        elif sp >= -1e-9:
            out.append(p + (q - p) * (sp / (sp - sq)))
    return _clean(out)


def subtract_convex(subject, R):
    """subject minus the CONVEX polygon R -> list of polygons (convex when subject is convex)."""
    R = G.ensure_ccw([G.V(p) for p in R])
    rest = [G.V(p) for p in subject]
    out = []
    for i in range(len(R)):
        a, b = R[i], R[(i + 1) % len(R)]
        o = clip_half(rest, a, b - a, keep_left=False)
        if len(o) >= 3 and abs(G.poly_area(o)) > 1e-4:
            out.append(o)
        rest = clip_half(rest, a, b - a, keep_left=True)
        if len(rest) < 3 or abs(G.poly_area(rest)) <= 1e-4:
            break
    return out


class RampPiece:
    """Planar convex piece of a plaza edge ramp: 2D outline (CCW) + plane z = A x + B y + C."""
    def __init__(self, pts3):
        self.poly = G.ensure_ccw([Vector((p[0], p[1])) for p in pts3])
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [tuple(p) for p in pts3[:3]]
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        self.A = ((z1 - z0) * (y2 - y0) - (z2 - z0) * (y1 - y0)) / det
        self.B = ((x1 - x0) * (z2 - z0) - (x2 - x0) * (z1 - z0)) / det
        self.C = z0 - self.A * x0 - self.B * y0

    def z(self, p):
        return self.A * p.x + self.B * p.y + self.C

    def near(self, p, m=0.0):
        """Point inside the piece, or within m of its outline."""
        if G.point_in_poly(p, self.poly):
            return True
        return m > 0 and any(G.dist_point_seg(p, self.poly[i - 1], self.poly[i]) < m for i in range(len(self.poly)))


def edge_ramps(P, specs, z_top, z_low, depth, flare):
    """Ramps that bring a raised slab (top z_top) down to z_low at its CONVEX polygon edge P (CCW).
    specs: [(edge_index, s0, s1, end0, end1[, foot_z])], s measured along the edge from P[i] (foot_z overrides
    z_low for that ramp; hip-joined corner ramps must share it); an end is 'flare'
    (triangular side flare of length *flare*) or 'corner' (the ramp runs into the polygon corner and meets
    the adjacent edge's ramp on the corner bisector - that edge needs a matching 'corner' end).
    Returns (pieces, profiles): planar RampPiece list + per-edge [(s, z_top_of_curb)] profiles."""
    n = len(P)
    pieces = []
    prof = {i: [] for i in range(n)}

    def frame(i):
        a, b = P[i], P[(i + 1) % n]
        L = (b - a).length
        t = (b - a) / L
        return a, t, G.left_normal(t), L

    def half_tan(k):
        u = (P[k - 1] - P[k]).normalized()
        w = (P[(k + 1) % n] - P[k]).normalized()
        return math.tan(math.acos(max(-1.0, min(1.0, u.dot(w)))) / 2.0)

    for spec in specs:
        i, s0, s1, e0, e1 = spec[:5]
        zl = spec[5] if len(spec) > 5 else z_low
        a, t, nrm, L = frame(i)

        def W(s, d, z):
            p = a + t * s + nrm * d
            return (p.x, p.y, z)
        c0 = 0.0 if e0 == "corner" else s0
        c1 = L if e1 == "corner" else s1
        i0 = depth / half_tan(i) if e0 == "corner" else c0
        i1 = L - depth / half_tan((i + 1) % n) if e1 == "corner" else c1
        pieces.append(RampPiece([W(c0, 0, zl), W(c1, 0, zl), W(i1, depth, z_top), W(i0, depth, z_top)]))
        if e0 == "flare":
            pieces.append(RampPiece([W(c0 - flare, 0, z_top), W(c0, 0, zl), W(c0, depth, z_top)]))
            prof[i] += [(c0 - flare, z_top), (c0, zl)]
        else:
            prof[i] += [(0.0, zl)]
        if e1 == "flare":
            pieces.append(RampPiece([W(c1, 0, zl), W(c1 + flare, 0, z_top), W(c1, depth, z_top)]))
            prof[i] += [(c1, zl), (c1 + flare, z_top)]
        else:
            prof[i] += [(L, zl)]
    out = {}
    for i in range(n):
        L = frame(i)[3]
        pts = sorted(prof[i], key=lambda q: q[0])
        if not pts or pts[0][0] > 1e-6:
            pts.insert(0, (0.0, z_top))
        if pts[-1][0] < L - 1e-6:
            pts.append((L, z_top))
        out[i] = pts
    return pieces, out


def shade(me, smooth_mats, angle=50.0):
    """Smooth-shade faces using *smooth_mats*; edges sharper than *angle* stay crisp."""
    names = [m.name for m in me.materials]
    flags = [names[p.material_index] in smooth_mats for p in me.polygons]
    if not any(flags):
        return
    me.set_sharp_from_angle(angle=math.radians(angle))
    me.polygons.foreach_set("use_smooth", flags)
    me.update()


def shared_mesh(key, build_fn, smooth=(), angle=50.0):
    """Mesh datablock built once per run and shared by every instance (linked duplicates)."""
    nm = "LMX_" + key
    me = bpy.data.meshes.get(nm)
    if me is None:
        mb = build_fn()
        me = mb.build(nm)
        if smooth:
            shade(me, set(smooth), angle)
    return me


def tris_of(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


class Counter:
    """Custom-geometry triangle budget per site (instances of a shared mesh counted once)."""
    def __init__(self):
        self.tris = 0
        self.seen = {}

    def add(self, me):
        if me.name not in self.seen:
            t = tris_of(me)
            self.seen[me.name] = t
            self.tris += t

    def report(self, objects, S=None):
        top = sorted(self.seen.items(), key=lambda kv: -kv[1])[:8]
        out = dict(custom_tris=self.tris, objects=objects, heaviest={k: v for k, v in top})
        if S is not None:
            # everything here is authored on flat ground (no layout hill reaches these sites); flag it if
            # a hill ever moves under the site so the fixed z levels get revisited
            pts = list(S.poly) + [S.center]
            dev = max(S.ground_z(p.x, p.y) for p in pts) - C.GROUND_Z
            out["ground_dev"] = round(dev, 3)
            if dev > 0.02:
                out["WARNING"] = "a hill raises the ground under this site - fixed z levels need review"
        return out


def sub_path(S, sub):
    # NOTE (framework workaround): scene.coll() resolves collection names globally, so a sub name such
    # as "Ground" shared by two sites would put the second site's objects into the first site's
    # collection. Every sub collection here is therefore prefixed with the site id.
    return S.coll + (f"/{S.id}_{sub}" if sub else "")


def place(S, me, name, x, y, z, rot=0.0, recolor=None, sub=None, scale=None, local=True, counter=None):
    """Object using shared mesh *me* in the site frame (or world when local=False).
    recolor: {material_name: new_material_name} applied as object-level material links."""
    if local:
        p = S.to_world(x, y)
        x, y = p.x, p.y
        rot = rot + S.rot
    S.n += 1
    o = scene.obj(f"LM_{S.id}_{name}"[:63], me, sub_path(S, sub), (x, y, z), rot)
    if scale is not None:
        o.scale = scale
    if recolor:
        for i, slot in enumerate(o.material_slots):
            m = me.materials[i] if i < len(me.materials) else None
            if m is not None and m.name in recolor and recolor[m.name] != m.name:
                slot.link = "OBJECT"
                slot.material = palette.get(recolor[m.name])
    if counter is not None:
        counter.add(me)
    return o


def put_mb(S, name, mb, x, y, z, rot=0.0, sub=None, smooth=(), angle=50.0, local=True, counter=None):
    """Unique custom mesh placed in the site frame (origin at (x, y, z))."""
    full = f"LM_{S.id}_{name}"[:63]
    me = mb.build(full)
    if smooth:
        shade(me, set(smooth), angle)
    return place(S, me, name, x, y, z, rot, sub=sub, local=local, counter=counter)


def kit(S, piece, x, y, z, rot=0.0, recolor=None, sub=None, scale=None):
    """Kit instance in the site frame with an explicit z (plaza / deck level)."""
    nm = piece if piece.startswith("KIT_") else "KIT_" + piece
    from .. import kit as K
    if not K.has(nm):
        return None
    p = S.to_world(x, y)
    S.n += 1
    return K.instance(nm, sub_path(S, sub), (p.x, p.y, z), rot + S.rot, recolor=recolor, scale=scale,
                      inst_name=f"LM_{S.id}_{nm[4:]}_{S.n:03d}"[:63])


# ------------------------------------------------------------------------------- shared props
def stripe_canopy(mb, x0, x1, y0, y1, z_eave, z_ridge, mats, band=0.5, th=0.06, valance=0.26,
                  val_front=True, val_back=True):
    """Gable canopy (ridge along X at y=(y0+y1)/2) made of stripe bands across X alternating *mats*;
    closed thin slab (visible from above and below) + scalloped valances on the eaves."""
    n = max(1, int(round((x1 - x0) / band)))
    bw = (x1 - x0) / n
    ym = (y0 + y1) / 2
    for i in range(n):
        xa, xb = x0 + bw * i, x0 + bw * (i + 1)
        m = mats[i % len(mats)]
        for (ya, yb) in ((y0, ym), (ym, y1)):
            za = z_eave if ya in (y0, y1) else z_ridge
            zb = z_eave if yb in (y0, y1) else z_ridge
            top = [v3(xa, ya, za + th), v3(xb, ya, za + th), v3(xb, yb, zb + th), v3(xa, yb, zb + th)]
            bot = [v3(xa, ya, za), v3(xb, ya, za), v3(xb, yb, zb), v3(xa, yb, zb)]
            face_n(mb, top, m, (0, 0, 1))
            face_n(mb, bot, m, (0, 0, -1))
        # eave edges
        for (ye, s) in ((y0, -1), (y1, 1)):
            face_n(mb, [v3(xa, ye, z_eave), v3(xb, ye, z_eave), v3(xb, ye, z_eave + th), v3(xa, ye, z_eave + th)],
                   m, (0, s, 0))
        # gable-end edges
        if i in (0, n - 1):
            xe, s = (xa, -1) if i == 0 else (xb, 1)
            for (ya, yb) in ((y0, ym), (ym, y1)):
                za = z_eave if ya in (y0, y1) else z_ridge
                zb = z_eave if yb in (y0, y1) else z_ridge
                face_n(mb, [v3(xe, ya, za), v3(xe, yb, zb), v3(xe, yb, zb + th), v3(xe, ya, za + th)], m, (s, 0, 0))
        # scalloped valance flaps (thin closed slabs) under the eaves
        for (ye, s, on) in ((y0, -1, val_front), (y1, 1, val_back)):
            if not on:
                continue
            t = 0.04
            yo, yi = ye + s * 0.0, ye - s * t
            prof = [(xa, z_eave), (xb, z_eave), (xb, z_eave - valance * 0.6), ((xa + xb) / 2, z_eave - valance),
                    (xa, z_eave - valance * 0.6)]
            face_n(mb, [v3(px, yo, pz) for px, pz in prof], m, (0, s, 0))
            face_n(mb, [v3(px, yi, pz) for px, pz in prof], m, (0, -s, 0))
            for k in range(len(prof)):
                (ax, az), (bx, bz) = prof[k], prof[(k + 1) % len(prof)]
                if k == 0:
                    continue   # top edge hidden under the canopy slab
                nrm = Vector((-(bz - az), 0.0, bx - ax))     # profile is CW in (x, z): outward = left
                face_n(mb, [v3(ax, yo, az), v3(bx, yo, bz), v3(bx, yi, bz), v3(ax, yi, az)], m,
                       (nrm.x, 0, nrm.z) if nrm.length > 1e-9 else (0, 0, -1))


def rope(mb, pts, r, mat, sides=3):
    """Thin continuous tube through 3D points (triangular section, shared rings, no end caps):
    6 tris per segment - for cables, festoon strings and bunting lines."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        u = t.cross(Vector((0.0, 0.0, 1.0)))
        if u.length < 1e-6:
            u = Vector((1.0, 0.0, 0.0))
        u.normalize()
        w = u.cross(t)
        rings.append([p + (u * math.cos(a) + w * math.sin(a)) * r
                      for a in (math.pi / 2 + TAU * k / sides for k in range(sides))])
    for i in range(n - 1):
        ax = (pts[i] + pts[i + 1]) / 2
        for k in range(sides):
            k2 = (k + 1) % sides
            q = [rings[i][k], rings[i + 1][k], rings[i + 1][k2], rings[i][k2]]
            face_n(mb, q, mat, sum(q, Vector()) / 4 - ax)


def sag_point(a, b, t, sag):
    p = Vector(a).lerp(Vector(b), t)
    p.z -= sag * 4.0 * t * (1.0 - t)
    return p


def string_lights(mb, a, b, sag=0.45, step=0.75, cable="M_Trim_Dark", bulb="M_Light_Emit", r=0.06, seg_len=2.4):
    """Festoon string between 3D points a and b: sagging triangular-section cable (one segment per
    *seg_len* m) + diamond bulbs (6 tris) every *step* m hanging just below it."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    n = max(3, int(round(L / seg_len)))
    rope(mb, [sag_point(a, b, i / n, sag) for i in range(n + 1)], 0.022, cable)
    m = max(1, int(L / step))
    for i in range(1, m):
        p = sag_point(a, b, i / m, sag)
        p.z -= 0.09
        gem(mb, (p.x, p.y, p.z), r, r * 1.35, bulb, seg=3, phase=0.5 * i)


def flagpole_mb(height=8.4, flag_w=1.9, flag_h=1.15):
    """Flag pole on a concrete base; flag streams toward +X in three waves (AWN / cream / AWN)."""
    mb = MeshBuilder()
    bbox(mb, -0.38, -0.38, 0.0, 0.38, 0.38, 0.32, "M_Wall_Concrete", bevel=0.05)
    bbox(mb, -0.24, -0.24, 0.32, 0.24, 0.24, 0.5, "M_Wall_Concrete", bevel=0.03)
    mb.cylinder(0, 0, 0.5, height, 0.075, "M_Metal", seg=8, r_top=0.05)
    lathe(mb, [(0.0, height - 0.02), (0.1, height + 0.03), (0.15, height + 0.15), (0.1, height + 0.27),
               (0.0, height + 0.31)], "M_Awning_Yellow", seg=8)
    # flag: 3 horizontal stripes, waving columns
    z0, z1 = height - 0.25 - flag_h, height - 0.25
    xs = [0.07 + flag_w * k / 4 for k in range(5)]
    wave = [0.0, 0.14, -0.04, 0.12, -0.02]
    zs = [z0, z0 + flag_h / 3, z0 + 2 * flag_h / 3, z1]
    mats = [AWN, CREAM, AWN]
    t = 0.04
    for j in range(3):
        for k in range(4):
            xa, xb = xs[k], xs[k + 1]
            ya, yb = wave[k], wave[k + 1]
            za, zb = zs[j], zs[j + 1]
            droop_a, droop_b = 0.06 * k / 4, 0.06 * (k + 1) / 4
            f = [v3(xa, ya - t / 2, za - droop_a), v3(xb, yb - t / 2, za - droop_b),
                 v3(xb, yb - t / 2, zb - droop_b), v3(xa, ya - t / 2, zb - droop_a)]
            bk = [v3(p.x, p.y + t, p.z) for p in f]
            face_n(mb, f, mats[j], ((yb - ya), -(xb - xa), 0))
            face_n(mb, bk, mats[j], (-(yb - ya), (xb - xa), 0))
            if j == 0:
                face_n(mb, [f[0], f[1], bk[1], bk[0]], mats[j], (0, 0, -1))
            if j == 2:
                face_n(mb, [f[3], f[2], bk[2], bk[3]], mats[j], (0, 0, 1))
            if k == 3:
                face_n(mb, [f[1], f[2], bk[2], bk[1]], mats[j], (1, 0, 0))
    return mb


def lantern_mb(arm=0.45):
    """Wall lantern on a bracket (bracket at y = 0 into -Y), glowing panes."""
    mb = MeshBuilder()
    bbox(mb, -0.08, -0.03, -0.14, 0.08, 0.0, 0.14, "M_Metal_Dark")
    beam(mb, (0.0, 0.0, 0.08), (0.0, -arm, 0.08), 0.05, 0.05, "M_Metal_Dark")
    bbox(mb, -0.14, -arm - 0.14, -0.38, 0.14, -arm + 0.14, -0.33, "M_Metal_Dark")
    bbox(mb, -0.11, -arm - 0.11, -0.33, 0.11, -arm + 0.11, 0.0, "M_Light_Emit")
    lathe(mb, [(0.0, -0.02), (0.2, -0.02), (0.2, 0.02), (0.0, 0.14)], "M_Metal_Dark", seg=4, cx=0.0, cy=-arm,
          phase=math.pi / 4)
    bbox(mb, -0.02, -arm - 0.02, 0.0, 0.02, -arm + 0.02, 0.1, "M_Metal_Dark")
    return mb


def market_pole_mb(h=3.7):
    """Slim dark pole with a little finial for festoon lights (origin = ground)."""
    mb = MeshBuilder()
    bbox(mb, -0.16, -0.16, 0.0, 0.16, 0.16, 0.12, "M_Wall_Concrete", bevel=0.03)
    mb.cylinder(0, 0, 0.12, h, 0.05, "M_Metal_Dark", seg=6)
    lathe(mb, [(0.0, h - 0.02), (0.08, h + 0.02), (0.08, h + 0.08), (0.0, h + 0.16)], "M_Metal_Dark", seg=6)
    return mb


def notice_board_mb():
    """Town notice board ('lost pets' & market notices): two posts, little roof, pinned papers (front -Y)."""
    mb = MeshBuilder()
    for x in (-0.95, 0.95):
        bbox(mb, x - 0.07, -0.07, 0.0, x + 0.07, 0.07, 2.2, "M_Trim_Wood", bevel=0.02)
    bbox(mb, -0.9, -0.05, 0.7, 0.9, 0.05, 1.9, "M_Sign_Board")
    bbox(mb, -0.82, -0.08, 0.78, 0.82, -0.05, 1.82, "M_Wood_Light")
    papers = [(-0.6, 1.5, "M_Wall_White"), (-0.15, 1.55, "M_Awning_Yellow"), (0.42, 1.48, "M_Wall_White"),
              (-0.5, 1.05, "M_Wall_Rose"), (0.05, 1.0, "M_Wall_White"), (0.55, 1.08, "M_Wall_Mint")]
    for (x, z, m) in papers:
        bbox(mb, x - 0.17, -0.1, z - 0.2, x + 0.17, -0.08, z + 0.2, m)
        bbox(mb, x - 0.03, -0.115, z + 0.12, x + 0.03, -0.1, z + 0.17, "M_Door_Red")
    face_n(mb, [v3(-1.15, -0.45, 2.05), v3(1.15, -0.45, 2.05), v3(1.15, 0.0, 2.45), v3(-1.15, 0.0, 2.45)],
           "M_Roof_Green", (0, -1, 1))
    face_n(mb, [v3(-1.15, 0.45, 2.05), v3(1.15, 0.45, 2.05), v3(1.15, 0.0, 2.45), v3(-1.15, 0.0, 2.45)],
           "M_Roof_Green", (0, 1, 1))
    face_n(mb, [v3(-1.15, -0.45, 2.05), v3(1.15, -0.45, 2.05), v3(1.15, 0.45, 2.05), v3(-1.15, 0.45, 2.05)],
           "M_Trim_Wood", (0, 0, -1))
    for s_ in (-1, 1):
        face_n(mb, [v3(s_ * 1.15, -0.45, 2.05), v3(s_ * 1.15, 0.45, 2.05), v3(s_ * 1.15, 0.0, 2.45)],
               "M_Trim_Wood", (s_, 0, 0))
    return mb


def tree_bed_mb(r=1.5, h=0.5):
    """Round seat-wall tree planter: concrete wall, white seat ledge, soil at h - 0.08."""
    mb = MeshBuilder()
    lathe(mb, [(r, -0.12), (r, h - 0.06), (r + 0.08, h - 0.06), (r + 0.08, h), (r - 0.3, h), (r - 0.3, h - 0.1),
               (r - 0.36, h - 0.1), (0.0, h - 0.1)],
          "M_Wall_Concrete", seg=14,
          mats=["M_Wall_Concrete", "M_Trim_White", "M_Trim_White", "M_Trim_White", "M_Trim_White", "M_Dirt", "M_Dirt"])
    return mb


def arch_outline(r, z0, zt, seg=8):
    """Round-arched opening outline in (x, z): sill at z0, springing at zt, crown at zt + r (CCW)."""
    pts = [(-r, z0), (r, z0)]
    for i in range(seg + 1):
        a = math.pi * i / seg
        pts.append((r * math.cos(a), zt + r * math.sin(a)))
    return pts


def framed_opening(mb, outer, inner, yw, depth, frame_mat, leaf_mat, leaf_h=0.02, reveal_from=None):
    """Facade frame plate (outer outline minus the inner opening) standing *depth* proud of the wall
    plane y = yw (outward = -Y), with a leaf (glass / door) filling the opening at height leaf_h."""
    O = G.ensure_ccw([G.V(p) for p in outer])
    I = G.ensure_ccw([G.V(p) for p in inner])
    sub = MeshBuilder()
    sub.tri_fill([O, I], depth, frame_mat, up=True)
    sub.wall(O, 0.0, depth, frame_mat, closed=True)
    sub.wall(I, leaf_h if reveal_from is None else reveal_from, depth, frame_mat, closed=True, outward_left=True)
    sub.tri_fill([I], leaf_h, leaf_mat, up=True)
    mb.extend(sub, M_front(yw))


# =============================================================================== the clock tower
def clock_tower_mb():
    """Hero clock tower, origin at the base centre on the plaza (z = 0 = plaza top), faces +-X / +-Y."""
    mb = MeshBuilder()
    BR, CR, TW, TD = "M_Wall_Brick", "M_Wall_Cream", "M_Trim_White", "M_Trim_Dark"
    # plinth steps (stone)
    bbox(mb, -3.7, -3.7, -0.15, 3.7, 3.7, 0.18, "M_Wall_Concrete", bevel=0.05)
    bbox(mb, -3.25, -3.25, 0.18, 3.25, 3.25, 0.36, "M_Wall_Concrete", bevel=0.04)
    # base course + cap
    bbox(mb, -2.5, -2.5, 0.36, 2.5, 2.5, 1.5, CR)
    bbox(mb, -2.64, -2.64, 1.5, 2.64, 2.64, 1.72, TW, bevel=0.04)
    # brick shaft
    H0, H1 = 1.72, 8.4
    hw = 2.2
    mb.box(-hw, -hw, H0, hw, hw, H1, BR, skip=("-z", "+z"))
    # quoins (alternating long / short blocks on every corner)
    k = 0
    z = H0 + 0.12
    while z + 0.5 < H1 - 0.15:
        for sx in (-1, 1):
            for sy in (-1, 1):
                la, lb = (0.8, 0.45) if k % 2 == 0 else (0.45, 0.8)
                xa, xb = sorted((sx * (hw - la), sx * (hw + 0.06)))
                ya, yb = sorted((sy * (hw - lb), sy * (hw + 0.06)))
                bbox(mb, xa, ya, z, xb, yb, z + 0.5, CR)
        z += 0.82
        k += 1
    # string course
    bbox(mb, -2.32, -2.32, 4.45, 2.32, 2.32, 4.71, TW, bevel=0.03)
    # clock stage
    bbox(mb, -2.42, -2.42, H1, 2.42, 2.42, H1 + 0.32, TW, bevel=0.04)
    C0, C1 = H1 + 0.32, H1 + 3.1
    cw = 2.3
    mb.box(-cw, -cw, C0, cw, cw, C1, CR, skip=("-z",))
    for sx in (-1, 1):            # white corner pilasters
        for sy in (-1, 1):
            xa, xb = sorted((sx * (cw - 0.42), sx * (cw + 0.07)))
            ya, yb = sorted((sy * (cw - 0.42), sy * (cw + 0.07)))
            bbox(mb, xa, ya, C0, xb, yb, C1, TW)
    bbox(mb, -2.55, -2.55, C1, 2.55, 2.55, C1 + 0.22, TW, bevel=0.03)
    bbox(mb, -2.68, -2.68, C1 + 0.22, 2.68, 2.68, C1 + 0.42, TW, bevel=0.04)
    top_clock = C1 + 0.42
    # belfry: 4 brick corner piers + arched openings + cream lintel band
    B0, B1 = top_clock, top_clock + 2.25
    bw = 2.05
    pier = 0.72
    mb.box(-1.4, -1.4, B0 - 0.02, 1.4, 1.4, B0 + 0.08, "M_Roof_Flat", skip=("-z",))     # belfry floor
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * (bw - pier), sx * bw))
            ya, yb = sorted((sy * (bw - pier), sy * bw))
            mb.box(xa, ya, B0, xb, yb, B1, BR, skip=("-z",))
    # arch spandrels in each opening (rounded arch tops) + sill rails
    ow = bw - pier                       # half opening width
    zs = B1 - ow
    for rot in range(4):
        R = Matrix.Rotation(rot * math.pi / 2, 4, "Z")
        sub = MeshBuilder()
        for side in (-1, 1):
            pts = [(side * ow, B1)] + [(side * ow * math.cos(math.pi / 2 * i / 6), zs + ow * math.sin(math.pi / 2 * i / 6))
                                       for i in range(7)]
            extrude_xz(sub, G.ensure_ccw([G.V(q) for q in pts]), -bw, -bw + pier, CR)
        # low balustrade rail across the opening
        bbox(sub, -ow, -bw + 0.12, B0 + 0.08, ow, -bw + 0.42, B0 + 0.62, CR)
        bbox(sub, -ow - 0.02, -bw + 0.08, B0 + 0.62, ow + 0.02, -bw + 0.46, B0 + 0.72, TW)
        mb.extend(sub, R)
    # lintel band + cornice
    bbox(mb, -2.12, -2.12, B1, 2.12, 2.12, B1 + 0.42, CR)
    bbox(mb, -2.3, -2.3, B1 + 0.42, 2.3, 2.3, B1 + 0.62, TW, bevel=0.04)
    # bell on a beam
    zb = B1 - 0.35
    bbox(mb, -1.36, -0.1, zb, 1.36, 0.1, zb + 0.2, "M_Trim_Wood")
    lathe(mb, [(0.0, zb - 1.05), (0.62, zb - 1.05), (0.6, zb - 0.95), (0.42, zb - 0.6), (0.33, zb - 0.2),
               (0.18, zb), (0.0, zb + 0.02)], "M_Awning_Yellow", seg=10)
    # corner finials on the clock-stage cornice (outside the belfry piers)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * 2.42, sy * 2.42
            bbox(mb, cx - 0.2, cy - 0.2, top_clock, cx + 0.2, cy + 0.2, top_clock + 0.32, TW, bevel=0.03)
            lathe(mb, [(0.0, top_clock + 0.32), (0.16, top_clock + 0.34), (0.2, top_clock + 0.5),
                       (0.1, top_clock + 0.66), (0.13, top_clock + 0.74), (0.0, top_clock + 0.86)],
                  TW, seg=8, cx=cx, cy=cy)
    # bell-cast copper spire (square, seg=4 at 45 deg)
    R0 = B1 + 0.62
    s2 = math.sqrt(2.0)
    prof = [(1.9 * s2, R0), (2.44 * s2, R0), (2.38 * s2, R0 + 0.16), (2.0 * s2, R0 + 0.4), (1.5 * s2, R0 + 0.92),
            (1.05 * s2, R0 + 1.7), (0.7 * s2, R0 + 2.55), (0.4 * s2, R0 + 3.3), (0.16 * s2, R0 + 3.78),
            (0.0, R0 + 3.9)]
    lathe(mb, prof, "M_Roof_Green", seg=4, phase=math.pi / 4)
    top = R0 + 3.9
    # finial: gilded ball, rod, weathervane
    lathe(mb, [(0.0, top - 0.05), (0.16, top + 0.02), (0.24, top + 0.2), (0.16, top + 0.38), (0.0, top + 0.44)],
          "M_Awning_Yellow", seg=8)
    mb.cylinder(0, 0, top + 0.4, top + 1.45, 0.045, "M_Metal_Dark", seg=6)
    zv = top + 1.05
    bbox(mb, -0.75, -0.035, zv - 0.035, 0.6, 0.035, zv + 0.035, "M_Metal_Dark")           # arrow shaft
    face_n(mb, [v3(0.6, 0, zv - 0.16), v3(0.95, 0, zv), v3(0.6, 0, zv + 0.16)], "M_Metal_Dark", (0, -1, 0))
    face_n(mb, [v3(0.6, 0.0, zv - 0.16), v3(0.95, 0.0, zv), v3(0.6, 0.0, zv + 0.16)], "M_Metal_Dark", (0, 1, 0))
    face_n(mb, [v3(-0.75, 0, zv), v3(-0.45, 0, zv), v3(-0.6, 0, zv + 0.3), v3(-0.9, 0, zv + 0.3)],
           "M_Metal_Dark", (0, -1, 0))
    face_n(mb, [v3(-0.75, 0, zv), v3(-0.45, 0, zv), v3(-0.6, 0, zv + 0.3), v3(-0.9, 0, zv + 0.3)],
           "M_Metal_Dark", (0, 1, 0))
    zc = top + 0.7
    bbox(mb, -0.45, -0.03, zc - 0.03, 0.45, 0.03, zc + 0.03, "M_Metal_Dark")
    bbox(mb, -0.03, -0.45, zc - 0.03, 0.03, 0.45, zc + 0.03, "M_Metal_Dark")

    # ---- per-face details (built on the south face y = -hw, rotated for the others)
    for rot in range(4):
        R = Matrix.Rotation(rot * math.pi / 2, 4, "Z")
        sub = MeshBuilder()
        # clock face
        zc = (C0 + C1) / 2
        yf = -cw
        ring_front(sub, 0.0, zc, 1.06, 1.24, yf, 0.1, TD, seg=20)
        disc_front(sub, 0.0, zc, 1.06, yf, 0.05, "M_Sign_Face", seg=20, side=TD)
        for i in range(12):
            a = TAU * i / 12
            big = i % 3 == 0
            w, l = (0.09, 0.26) if big else (0.06, 0.15)
            rr = 0.86 if big else 0.9
            cx, cz = rr * math.sin(a), zc + rr * math.cos(a)
            tick = MeshBuilder()
            tick.box(-w / 2, -l / 2, 0.0, w / 2, l / 2, 0.03, TD, skip=("-z",))
            sub.extend(tick, M_front(yf - 0.05) @ Matrix.Translation((cx, cz, 0)) @ Matrix.Rotation(-a, 4, "Z"))
        for (ang, ln, wd) in ((math.radians(-58), 0.5, 0.11), (math.radians(48), 0.78, 0.07)):   # ~10:08
            hand = MeshBuilder()
            hand.box(-wd / 2, -0.12, 0.0, wd / 2, ln, 0.04, TD, skip=("-z",))
            sub.extend(hand, M_front(yf - 0.08) @ Matrix.Translation((0, zc, 0)) @ Matrix.Rotation(-ang, 4, "Z"))
        disc_front(sub, 0.0, zc, 0.1, yf - 0.12, 0.04, "M_Awning_Yellow", seg=8)
        # arched windows on the shaft (tall upper + small lower); frame ring + recessed glass
        for (z0, z1, ww) in ((5.55, 7.0, 0.86), (2.35, 3.35, 0.62)):
            if rot == 2 and z0 < 4:
                continue      # the door takes the lower slot on the north face
            r = ww / 2
            outer = arch_outline(r + 0.15, z0 - 0.12, z1)
            inner = arch_outline(r, z0, z1)
            framed_opening(sub, outer, inner, -hw, 0.09, CR, "M_Glass", leaf_h=0.015)
            bbox(sub, -r - 0.26, -hw - 0.17, z0 - 0.24, r + 0.26, -hw + 0.01, z0 - 0.1, TW)         # sill
        if rot == 2:
            # north door: deep cream portal (frontispiece) with an arched wooden double door
            dw, dh = 0.72, 2.2
            z0 = 0.36
            outer = [(-dw - 0.5, z0), (dw + 0.5, z0), (dw + 0.5, z0 + dh + dw + 0.45), (-dw - 0.5, z0 + dh + dw + 0.45)]
            inner = arch_outline(dw, z0, z0 + dh)
            framed_opening(sub, outer, inner, -hw, 0.78, CR, "M_Door_Wood", leaf_h=0.56, reveal_from=0.5)
            zt = z0 + dh + dw + 0.45
            bbox(sub, -dw - 0.66, -hw - 0.92, zt, dw + 0.66, -hw, zt + 0.22, TW, bevel=0.03)        # cornice
            bbox(sub, -0.03, -hw - 0.6, z0, 0.03, -hw - 0.54, z0 + dh + 0.6, "M_Trim_Wood")      # leaf split
            for sx in (-1, 1):
                bbox(sub, sx * 0.16 - 0.04, -hw - 0.64, z0 + 1.0, sx * 0.16 + 0.04, -hw - 0.56, z0 + 1.12, "M_Metal")
            bbox(sub, -dw - 0.62, -hw - 0.86, z0 - 0.02, dw + 0.62, -hw, z0 + 0.06, "M_Wall_Concrete")  # threshold
            yp = -hw - 0.78
            bbox(sub, -0.17, yp - 0.07, z0 + dh + dw - 0.22, 0.17, yp + 0.01, z0 + dh + dw + 0.24, TW)   # keystone
            for sx in (-1, 1):                                                                       # pilasters
                xa, xb = sorted((sx * (dw + 0.27), sx * (dw + 0.47)))
                bbox(sub, xa, yp - 0.05, z0, xb, yp + 0.01, zt, TW)
                xa, xb = sorted((sx * dw, sx * (dw + 0.27)))
                bbox(sub, xa, yp - 0.04, z0 + dh - 0.08, xb, yp + 0.01, z0 + dh + 0.04, TW)          # impost
        mb.extend(sub, R @ Matrix.Rotation(0.0, 4, "Z"))
    return mb


# =============================================================================== fountain
def fountain_mb():
    """Octagonal two-tier fountain (origin = centre, z = 0 = plaza top)."""
    mb = MeshBuilder()
    st, cr, tw = "M_Wall_Concrete", "M_Wall_Cream", "M_Trim_White"
    R = 3.3
    seg = 8
    ph = math.pi / 8
    # basin: outer wall, chunky rim, inner wall, floor
    lathe(mb, [(R, -0.1), (R, 0.42), (R + 0.12, 0.42), (R + 0.12, 0.6), (R - 0.45, 0.6), (R - 0.45, 0.3)],
          st, seg=seg, phase=ph, mats=[cr, tw, tw, tw, cr])
    lathe(mb, [(R - 0.45, 0.3), (0.0, 0.3)], "M_RiverBed", seg=seg, phase=ph)
    lathe(mb, [(R - 0.45, 0.46), (0.0, 0.46)], "M_Water", seg=seg, phase=ph)
    # central pedestal + lower bowl
    lathe(mb, [(0.55, 0.3), (0.55, 0.62), (0.4, 0.75), (0.32, 1.25), (0.5, 1.35)], cr, seg=8, phase=ph)
    lathe(mb, [(0.5, 1.35), (1.25, 1.5), (1.58, 1.72), (1.6, 1.86), (1.45, 1.86), (1.45, 1.8)], tw, seg=12)
    lathe(mb, [(1.45, 1.8), (0.0, 1.8)], "M_Water", seg=12)
    # water sheet falling from the lower bowl into the basin
    lathe(mb, [(1.75, 0.46), (1.68, 1.0), (1.62, 1.5), (1.62, 1.78)], "M_Water", seg=12)
    # upper pedestal + small bowl
    lathe(mb, [(0.25, 1.8), (0.2, 2.35), (0.3, 2.42)], cr, seg=8, phase=ph)
    lathe(mb, [(0.3, 2.42), (0.75, 2.55), (0.82, 2.68), (0.72, 2.68), (0.72, 2.64)], tw, seg=10)
    lathe(mb, [(0.72, 2.64), (0.0, 2.64)], "M_Water", seg=10)
    lathe(mb, [(0.95, 1.8), (0.9, 2.2), (0.86, 2.5), (0.86, 2.66)], "M_Water", seg=10)
    # top: gilded fish-ball finial + jet
    lathe(mb, [(0.0, 2.6), (0.16, 2.68), (0.18, 2.82), (0.1, 2.95), (0.0, 2.98)], "M_Awning_Yellow", seg=8)
    lathe(mb, [(0.07, 2.95), (0.12, 3.25), (0.17, 3.4), (0.0, 3.48)], "M_Water", seg=6)
    # four little spouting frogs on the rim (playful), water arcs into the basin
    for i in range(4):
        a = ph * 0 + TAU * i / 4 + math.pi / 4
        cx, cy = (R - 0.2) * math.cos(a), (R - 0.2) * math.sin(a)
        sub = MeshBuilder()
        lathe(sub, [(0.0, 0.6), (0.24, 0.62), (0.26, 0.78), (0.16, 0.92), (0.0, 0.95)], "M_Zoo_Primary", seg=6)
        gem(sub, (-0.1, -0.1, 0.92), 0.07, 0.07, "M_Wall_White", seg=4)
        gem(sub, (0.1, -0.1, 0.92), 0.07, 0.07, "M_Wall_White", seg=4)
        rot = Matrix.Rotation(a - math.pi / 2, 4, "Z")      # frog front (-Y) looks at the centre
        mb.extend(sub, Matrix.Translation((cx, cy, 0)) @ rot)
        # arc of water toward the centre
        p0 = Vector((cx, cy, 0.86)) * 1.0
        d = -Vector((math.cos(a), math.sin(a), 0.0))
        pts = [p0 + d * (0.2 + 0.25 * k) + Vector((0, 0, 0.35 * math.sin(math.pi * k / 4) - 0.1 * k)) for k in range(5)]
        for k in range(4):
            tube(mb, pts[k], pts[k + 1], 0.05, "M_Water", seg=4, cap1=False)
    return mb


# =============================================================================== market stall
GOODS = {
    "fruit": ["M_Door_Red", "M_Hazard_Orange", "M_Hazard"],
    "flowers": ["M_Foliage_Blossom", "M_Awning_Yellow", "M_Wall_Lavender"],
    "veg": ["M_Foliage_Light", "M_Hazard_Orange", "M_Foliage_Dark"],
    "bakery": ["M_Wood_Light", "M_Crate", "M_Wall_Butter"],
    "pets": ["M_PetShop_Primary", "M_PetShop_Second", "M_Wood_Light"],
}


def stall_mb(goods="fruit"):
    """Market stall 3 x 2 m (front -Y, origin bottom centre), gable canopy striped AWN / cream."""
    mb = MeshBuilder()
    W = 1.5
    # counter + top board + coloured front panel
    bbox(mb, -1.35, -0.92, 0.0, 1.35, -0.4, 0.92, "M_Wood_Light", bevel=0.025)
    bbox(mb, -1.45, -1.02, 0.92, 1.45, -0.32, 1.0, "M_Trim_Wood", bevel=0.02)
    bbox(mb, -1.1, -0.96, 0.25, 1.1, -0.9, 0.75, AWN)
    bbox(mb, -0.9, -0.99, 0.38, 0.9, -0.96, 0.62, CREAM)
    # back shelf
    bbox(mb, -1.35, 0.45, 0.0, 1.35, 0.9, 1.2, "M_Trim_Wood", bevel=0.025)
    # posts
    for sx in (-1, 1):
        for y in (-0.97, 0.92):
            bbox(mb, sx * 1.42 - 0.05, y - 0.05, 0.0, sx * 1.42 + 0.05, y + 0.05, 2.36, "M_Trim_White")
    # canopy
    stripe_canopy(mb, -W, W, -1.3, 1.3, 2.32, 2.92, [AWN, CREAM], band=0.5)
    # goods: crates with piles
    cols = GOODS.get(goods, GOODS["fruit"])
    for i, x in enumerate((-0.85, 0.0, 0.85)):
        bbox(mb, x - 0.33, -0.86, 1.0, x + 0.33, -0.44, 1.2, "M_Crate")
        m = cols[i % len(cols)]
        for (dx, dy, dz) in ((-0.16, -0.08, 0), (0.0, -0.1, 0), (0.16, -0.06, 0), (-0.08, 0.06, 0.02),
                             (0.09, 0.07, 0.02), (0.0, -0.01, 0.1)):
            if goods == "bakery":
                rbox(mb, (x + dx, -0.65 + dy, 1.27 + dz), (0.24, 0.13, 0.1), m, rot_z=0.3 * dx * 10)
            else:
                gem(mb, (x + dx, -0.65 + dy, 1.27 + dz), 0.09, 0.08, m, seg=5, phase=dx * 7)
    # back shelf goods (jars / boxes)
    for i, x in enumerate((-1.0, -0.55, -0.1, 0.35, 0.8, 1.1)):
        m = cols[(i + 1) % len(cols)]
        bbox(mb, x - 0.12, 0.55, 1.2, x + 0.12, 0.8, 1.48 + 0.06 * (i % 2), m)
    # small hanging price sign on the front eave centre
    bbox(mb, -0.42, -1.33, 1.95, 0.42, -1.28, 2.26, "M_Sign_Board")
    bbox(mb, -0.34, -1.35, 2.01, 0.34, -1.32, 2.2, "M_Sign_Face")
    return mb


def kiosk_mb():
    """Coffee kiosk 2.6 x 2.0 (front -Y): teal booth, serving window, striped awning, roof sign."""
    mb = MeshBuilder()
    body, trim = "M_Door_Teal", "M_Trim_White"
    w, d, h = 1.3, 1.0, 2.5
    bbox(mb, -w, -d, 0.0, w, d, 0.18, "M_Wall_Concrete")
    mb.box(-w + 0.05, -d + 0.05, 0.18, w - 0.05, d - 0.05, h, body, skip=("-z",))
    # serving window (dark glass inset) + counter ledge
    bbox(mb, -0.95, -d - 0.0, 1.05, 0.95, -d + 0.07, 2.05, "M_Glass")
    for x in (-0.98, 0.98):
        bbox(mb, x - 0.05, -d - 0.04, 1.0, x + 0.05, -d + 0.06, 2.1, trim)
    bbox(mb, -1.0, -d - 0.04, 2.05, 1.0, -d + 0.06, 2.13, trim)
    bbox(mb, -1.05, -d - 0.32, 0.98, 1.05, -d + 0.06, 1.06, "M_Trim_Wood")
    # cups on the counter
    for x in (-0.7, -0.5, 0.55):
        lathe(mb, [(0.0, 1.06), (0.05, 1.06), (0.065, 1.2), (0.0, 1.2)], "M_Wall_White", seg=6, cx=x, cy=-d - 0.15)
    # trim corners + roof slab
    for sx in (-1, 1):
        for sy in (-1, 1):
            bbox(mb, sx * w - 0.08, sy * d - 0.08, 0.18, sx * w + 0.08, sy * d + 0.08, h, trim)
    bbox(mb, -w - 0.2, -d - 0.2, h, w + 0.2, d + 0.2, h + 0.18, trim, bevel=0.04)
    # striped flat-ish awning over the window
    stripe_canopy(mb, -1.15, 1.15, -d - 0.85, -d - 0.05, 2.2, 2.38, [AWN, CREAM], band=0.46, val_back=False)
    # roof sign: board with a cup pictogram
    bbox(mb, -0.85, -0.1, h + 0.18, 0.85, 0.1, h + 0.85, "M_Sign_Board", bevel=0.03)
    bbox(mb, -0.75, -0.13, h + 0.26, 0.75, -0.1, h + 0.77, "M_Sign_Face")
    lathe(mb, [(0.0, h + 0.36), (0.13, h + 0.36), (0.17, h + 0.64), (0.0, h + 0.64)], "M_Door_Wood", seg=6,
          cx=0.0, cy=-0.2)
    bbox(mb, 0.16, -0.24, h + 0.44, 0.27, -0.16, h + 0.56, "M_Door_Wood")
    # side menu board
    bbox(mb, w + 0.0, -0.6, 0.9, w + 0.06, 0.6, 1.9, "M_Sign_Board")
    return mb


# =============================================================================== paving
RAMP_DEPTH = 2.5      # edge ramps: run inward from the plaza edge (0.15 m drop -> ~6 % slope)
RAMP_FLARE = 1.6      # side flares along the edge
RAMP_FOOT = -0.03     # ramp foot: 8 mm above the downtown concrete (-0.038) -> no lip
RAMP_FOOT_PATH = -0.004   # NW mouth: the SquareAxis path ribbon (-0.015) runs under the ramp - stay above it


def plaza_ramp_specs(Pc):
    """Edge ramps on the kept-open approaches (Pc = CCW local polygon SW, SE, NE, NW):
    S axis (Green Walk / pet shop) and the SE corner (quay promenade -> Central Bridge) on the south edge,
    the SE corner on the east edge, the NW boulevard mouth (Canal St sidewalk / Zoo Blvd) on the north edge."""
    def s_at(i, p):
        a, b = Pc[i], Pc[(i + 1) % len(Pc)]
        return (G.V(p) - a).dot((b - a).normalized())

    def cross_edge(i, d):
        """Point where the axis ray from the tower (origin) along d leaves through edge i."""
        a, b = Pc[i], Pc[(i + 1) % len(Pc)]
        r = G.line_intersect(Vector((0.0, 0.0)), d, a, b - a)
        return d * r[0]
    L0 = (Pc[1] - Pc[0]).length
    s_s = s_at(0, cross_edge(0, Vector((0.0, -1.0))))
    s_nw = s_at(2, cross_edge(2, AXIS_NW))
    return [(0, s_s - 3.5, s_s + 3.5, "flare", "flare"),                     # S axis
            (0, L0 - 6.5, None, "flare", "corner"),                         # SE corner (south edge)
            (1, None, 4.0, "corner", "flare"),                              # SE corner (east edge)
            (2, s_nw - 3.4, s_nw + 3.4, "flare", "flare", RAMP_FOOT_PATH)]   # NW boulevard mouth


def plaza_paving(S, P):
    """Base slab + flush accent inlays (two-tone pattern), with ramped edge bands on the open approaches.
    Returns (MeshBuilder in the local frame, ramp pieces)."""
    mb = MeshBuilder()
    Pc = G.ensure_ccw([G.V(p) for p in P])
    ramps, profiles = edge_ramps(Pc, plaza_ramp_specs(Pc), PZ, RAMP_FOOT, RAMP_DEPTH, RAMP_FLARE)
    # base slab: flat pieces (polygon minus the ramp pieces) + the sloped ramp pieces
    flat = [Pc]
    for r in ramps:
        nxt = []
        for f in flat:
            nxt += subtract_convex(f, r.poly)
        flat = nxt
    for f in flat:                                  # convex pieces -> single n-gons (no scanfill slivers)
        face_n(mb, [v3(p.x, p.y, PZ) for p in f], "M_Plaza", (0, 0, 1))
    for r in ramps:
        face_n(mb, [v3(p.x, p.y, r.z(p)) for p in r.poly], "M_Plaza", (0, 0, 1))
    # curb walls (top follows the ramps along the edge)
    for i in range(len(Pc)):
        a, b = Pc[i], Pc[(i + 1) % len(Pc)]
        t = (b - a).normalized()
        out_n = -G.left_normal(t)
        pr = profiles[i]
        for (sa, za), (sb, zb) in zip(pr, pr[1:]):
            if sb - sa < 1e-4:
                continue
            pa, pb = a + t * sa, a + t * sb
            face_n(mb, [v3(pa.x, pa.y, C.GROUND_Z - 0.06), v3(pb.x, pb.y, C.GROUND_Z - 0.06), v3(pb.x, pb.y, zb),
                        v3(pa.x, pa.y, za)], "M_Curb", (out_n.x, out_n.y, 0))

    def emit(q, dz, mat):
        """Flush inlay polygon (convex): flat parts at PZ + dz, parts on a ramp follow its plane."""
        rest = [[G.V(p) for p in q]]
        for r in ramps:
            nxt = []
            for f in rest:
                on = _clean(clip_convex(f, r.poly))
                if len(on) >= 3 and abs(G.poly_area(on)) > 1e-4:
                    face_n(mb, [v3(p.x, p.y, r.z(p) + dz) for p in on], mat, (0, 0, 1))
                nxt += subtract_convex(f, r.poly)
            rest = nxt
        for f in rest:
            face_n(mb, [v3(p.x, p.y, PZ + dz) for p in f], mat, (0, 0, 1))
    zi = PZ + 0.012
    acc = "M_Plaza_Accent"
    inner = inset_convex(Pc, 1.0)
    for i in range(len(Pc)):                       # 1 m border band, one trapezoid per edge
        j = (i + 1) % len(Pc)
        emit([Pc[i], Pc[j], inner[j], inner[i]], 0.012, acc)
    field = inset_convex(Pc, 1.0)
    # sunburst + ring around the tower
    n = 32
    for i in range(n):
        a0, a1 = TAU * i / n, TAU * (i + 1) / n
        for (r0, r1, on) in ((6.0, 7.0, True), (3.95, 6.0, (i // 2) % 2 == 0)):
            if not on:
                continue
            q = [Vector((r1 * math.cos(a0), r1 * math.sin(a0))), Vector((r1 * math.cos(a1), r1 * math.sin(a1))),
                 Vector((r0 * math.cos(a1), r0 * math.sin(a1))), Vector((r0 * math.cos(a0), r0 * math.sin(a0)))]
            emit(G.ensure_ccw(q), 0.012, acc)
    # axis stripe pairs (NW -> Zoo Boulevard, S -> Green Walk / pet shop) with diamond inlays
    axes = (AXIS_NW, Vector((0.0, -1.0)))
    for d in axes:
        nrm = G.left_normal(d)
        for off in (-2.6, 2.6):
            c0 = d * 7.0 + nrm * off
            c1 = d * 40.0 + nrm * off
            q = [c0 - nrm * 0.28, c1 - nrm * 0.28, c1 + nrm * 0.28, c0 + nrm * 0.28]
            q = clip_convex(q, field)
            if len(q) >= 3:
                emit(G.ensure_ccw(q), 0.012, acc)
        s = 9.6
        while s < 40.0:
            c = d * s
            q = [c - d * 0.85, c + nrm * 0.85, c + d * 0.85, c - nrm * 0.85]
            if all(G.point_in_poly(p, field) for p in q):
                emit(G.ensure_ccw(q), 0.012, acc)
            s += 3.6
    # slab grid in the open fields (thin joints every 4 m), kept out of the tower ring and axis bands
    jw, step, Rr = 0.16, 4.0, 7.35
    xs = [p.x for p in field]
    ys = [p.y for p in field]

    def free_intervals(p0, dirv, t0, t1):
        cuts = []
        # circle around the tower
        b_ = p0.dot(dirv)
        c_ = p0.dot(p0) - Rr * Rr
        disc = b_ * b_ - c_
        if disc > 0:
            cuts.append((-b_ - math.sqrt(disc), -b_ + math.sqrt(disc)))
        for d in axes:            # axis bands |p.nrm| < 3.0, p.d > 0
            nrm = G.left_normal(d)
            a0, a1 = p0.dot(nrm), dirv.dot(nrm)
            lo, hi = -1e9, 1e9
            if abs(a1) < 1e-9:
                if abs(a0) >= 3.0:
                    continue
            else:
                u0, u1 = sorted(((-3.0 - a0) / a1, (3.0 - a0) / a1))
                lo, hi = max(lo, u0), min(hi, u1)
            b0, b1 = p0.dot(d), dirv.dot(d)
            if abs(b1) < 1e-9:
                if b0 <= 0:
                    continue
            else:
                u = -b0 / b1
                if b1 > 0:
                    lo = max(lo, u)
                else:
                    hi = min(hi, u)
            if lo < hi:
                cuts.append((lo, hi))
        segs = [(t0, t1)]
        for (c0, c1) in cuts:
            nxt = []
            for (a, b) in segs:
                if c1 <= a or c0 >= b:
                    nxt.append((a, b))
                    continue
                if c0 > a:
                    nxt.append((a, c0))
                if c1 < b:
                    nxt.append((c1, b))
            segs = nxt
        return [(a, b) for (a, b) in segs if b - a > 0.6]

    for axis in ("x", "y"):
        lo, hi = (min(xs), max(xs)) if axis == "x" else (min(ys), max(ys))
        k = math.ceil(lo / step)
        while k * step < hi:
            c = k * step
            k += 1
            if axis == "x":
                p0, dirv, big = Vector((c, -100.0)), Vector((0.0, 1.0)), 200.0
            else:
                p0, dirv, big = Vector((-100.0, c)), Vector((1.0, 0.0)), 200.0
            nrm = G.left_normal(dirv)
            q = [p0 - nrm * jw / 2, p0 + dirv * big - nrm * jw / 2, p0 + dirv * big + nrm * jw / 2, p0 + nrm * jw / 2]
            q = clip_convex(q, field)
            if len(q) < 3:
                continue
            ts = [(p - p0).dot(dirv) for p in q]
            for (a, b) in free_intervals(p0, dirv, min(ts), max(ts)):
                pa, pb = p0 + dirv * a, p0 + dirv * b
                quad = [pa - nrm * jw / 2, pb - nrm * jw / 2, pb + nrm * jw / 2, pa + nrm * jw / 2]
                emit(G.ensure_ccw(quad), 0.008, acc)
    return mb, ramps


# =============================================================================== build
def build(S):
    cnt = Counter()
    P = [S.to_local(p) for p in S.poly]

    # ---- ground (two-tone paving; ramped edge bands on the S axis, the SE corner and the NW mouth)
    pav, ramps = plaza_paving(S, P)
    put_mb(S, "Plaza", pav, 0.0, 0.0, 0.0, sub="Ground", counter=cnt)

    # ---- clock tower (hero)
    tower = shared_mesh("TS_ClockTower", clock_tower_mb, smooth=("M_Awning_Yellow",), angle=50)
    place(S, tower, "ClockTower", 0.0, 0.0, PZ, 0.0, sub="Tower", counter=cnt)
    lan = shared_mesh("CT_WallLantern", lantern_mb)
    for x in (-1.15, 1.15):                       # lanterns on the north door portal pilasters
        place(S, lan, "TowerLantern", x, 3.03, PZ + 2.75, math.pi, sub="Tower", counter=cnt)

    # ---- fountain
    fc = Vector((-13.5, -2.5))
    fnt = shared_mesh("TS_Fountain", fountain_mb, smooth=("M_Water", "M_Awning_Yellow", "M_Zoo_Primary"), angle=55)
    place(S, fnt, "Fountain", fc.x, fc.y, PZ, 0.0, sub="Fountain", counter=cnt)

    # ---- market stalls along the north edge (fronts face south into the square)
    # one market, three canopy colours alternating (red / teal / yellow - shared with the kiosk + umbrellas)
    variants = [("fruit", "M_Awning_Red"), ("flowers", "M_Awning_Teal"), ("veg", "M_Awning_Yellow"),
                ("bakery", "M_Awning_Red"), ("pets", "M_Awning_Teal")]
    for i, (g, col) in enumerate(variants):
        me = shared_mesh("TS_Stall_" + g, lambda g=g: stall_mb(g))
        x = -0.5 + 5.0 * i
        place(S, me, f"Stall_{i + 1:02d}_{g}", x, 13.2, PZ, 0.0, recolor={AWN: col}, sub="Market", counter=cnt)
    for x in (2.0, 12.0):
        kit(S, "Planter", x, 12.7, PZ, 0.0, sub="Market")
    # festoon lights on slim poles above the market canopies (zig-zag front / back between the poles)
    mp = shared_mesh("TS_MarketPole", market_pole_mb)
    fl = MeshBuilder()
    poles = []
    for i, (x, y) in enumerate(((-3.1, 11.7), (2.0, 14.6), (7.0, 11.7), (12.0, 14.6), (17.0, 11.7), (22.1, 12.0))):
        poles.append(Vector((x, y, 3.55)))
        place(S, mp, f"MarketPole_{i + 1}", x, y, PZ, 0.0, sub="Market", counter=cnt)
    for a, b in zip(poles, poles[1:]):
        string_lights(fl, a, b, sag=0.3, step=0.6)
    put_mb(S, "MarketLights", fl, 0.0, 0.0, PZ, sub="Market", counter=cnt)

    # ---- coffee kiosk + cafe terrace (west / quay side)
    ko = shared_mesh("TS_Kiosk", kiosk_mb, smooth=("M_Wall_White", "M_Door_Wood"))
    place(S, ko, "CoffeeKiosk", -22.4, -4.0, PZ, face_rot(1, 0), recolor={AWN: "M_Awning_Teal"},
          sub="Cafe", counter=cnt)
    umb = ["M_Awning_Teal", "M_Awning_Yellow", "M_Awning_Teal", "M_Awning_Red", "M_Awning_Yellow"]
    for i, (x, y) in enumerate(((-20.3, -8.3), (-16.0, -10.0), (-11.4, -11.6), (-19.6, 1.6))):
        kit(S, "CafeTable", x, y, PZ, 0.35 * i, recolor={"awning": umb[i]}, sub="Cafe")
    kit(S, "TrashBin", -22.6, -0.6, PZ, 0.0, sub="Cafe")
    kit(S, "Planter", -22.6, -7.2, PZ, face_rot(1, 0), sub="Cafe")

    # ---- flag poles flanking both axis gateways
    fp = shared_mesh("TS_FlagPole", flagpole_mb, smooth=("M_Awning_Yellow", "M_Metal"))
    nrm = G.left_normal(AXIS_NW)
    g_nw = AXIS_NW * 14.0 / AXIS_NW.y
    flags = [(-4.6, -12.9, "M_Awning_Blue"), (4.6, -14.7, "M_Awning_Red"),
             (*(g_nw + nrm * 3.9), "M_Awning_Red"), (*(g_nw - nrm * 3.9), "M_Awning_Blue")]
    for i, (x, y, col) in enumerate(flags):
        place(S, fp, f"FlagPole_{i + 1}", x, y, PZ, 0.0, recolor={AWN: col}, sub="Flags", counter=cnt)

    # ---- lamps: ring around the tower + edges
    for ang in (30, 158, 214, 326):
        a = math.radians(ang)
        kit(S, "Lamp_Park", 8.3 * math.cos(a), 8.3 * math.sin(a), PZ, 0.0, sub="Lamps")
    # (the SE corner lamp stands beside the corner ramp head, clear of the ramp)
    for (x, y) in ((-23.6, 9.0), (-23.6, -9.8), (11.5, -16.9), (23.5, -14.3), (23.5, 14.5), (-14.5, 15.8)):
        kit(S, "Lamp_Park", x, y, PZ, 0.0, sub="Lamps")

    # ---- trees in seat-wall planters
    bed = shared_mesh("TS_TreeBed", tree_bed_mb)
    for i, (x, y, tree, fol) in enumerate(((-20.4, 11.0, "Tree_Round_A", "M_Foliage"),
                                           (18.6, -13.2, "Tree_Round_A", "M_Foliage_Light"),
                                           (20.6, 4.2, "Tree_Round_A", "M_Foliage"))):
        place(S, bed, f"TreeBed_{i + 1}", x, y, PZ, 0.0, sub="Trees", counter=cnt)
        kit(S, tree, x, y, PZ + 0.38, 0.7 * i, recolor={"foliage": fol}, sub="Trees", scale=(0.95, 0.95, 0.95))

    # ---- benches + bins
    def bench_at(x, y, tx, ty, bin_side=1):
        r = face_rot(tx - x, ty - y)
        kit(S, "Bench", x, y, PZ, r, sub="Benches")
        if bin_side:
            ox, oy = math.cos(r) * 1.35 * bin_side, math.sin(r) * 1.35 * bin_side
            kit(S, "TrashBin", x + ox, y + oy, PZ, r, sub="Benches")
    for ang, bs in ((80, 1), (12, 0), (150, 0)):
        a = math.radians(ang)
        bench_at(fc.x + 5.2 * math.cos(a), fc.y + 5.2 * math.sin(a), fc.x, fc.y, bs)
    for ang in (0, 250 + 40, 200):
        a = math.radians(ang)
        bench_at(9.4 * math.cos(a), 9.4 * math.sin(a), 0.0, 0.0, 1 if ang == 0 else 0)
    # east edge: hedges screening the Main Street backs, benches in front
    for y in (-10.5, -1.5, 1.5, 7.5, 10.5):
        kit(S, "Hedge_3m", 23.9, y, PZ, math.pi / 2, sub="Edges")
    bench_at(22.4, -6.0, 0.0, -6.0, 0)
    # bike racks + mailbox at the north-east entrance (Canal St / Main St side)
    for y in (9.6, 12.2):
        kit(S, "BikeRack", 23.3, y + 3.5, PZ, math.pi / 2, sub="Edges")
    kit(S, "Mailbox", 24.0, -12.9, PZ, face_rot(-1, 0), sub="Edges")
    # notice board at the boulevard corner + benches looking out over the canal on the quay edge
    nb = shared_mesh("TS_NoticeBoard", notice_board_mb)
    place(S, nb, "NoticeBoard", -19.2, 14.6, PZ, face_rot(0.35, -1.0), sub="Edges", counter=cnt)
    for (x, t) in ((-7.6, 0.0), (9.0, 0.0), (15.5, 0.0)):
        y = -11.0 - (x + 25.0) / 50.0 * 10.0 + 1.6
        kit(S, "Bench", x, y, PZ, math.atan2(-10.0, 50.0), sub="Benches")     # facing the canal

    # nothing may stand on the ramps (all furniture is placed at plaza level)
    conflicts = []
    lmc = bpy.data.collections.get(f"LM_{S.id}")
    for o in (lmc.all_objects if lmc else []):
        if o.name.endswith("_Plaza"):
            continue
        q = S.to_local(o.location)
        if any(r.near(q, 0.3) for r in ramps):
            conflicts.append(o.name)
    S.register_lot(S.poly)
    out = cnt.report(S.n, S)
    out["ramps"] = len(ramps)
    out["ramp_conflicts"] = conflicts
    return out
