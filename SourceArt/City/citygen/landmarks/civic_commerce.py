"""Phase 4 landmarks: CIVIC COMMERCE - Gas Station, Supermarket, Diner (lead densification pass).

Three commercial anchors on the south side (Main St / Southside Pkwy) that make Willowbrook read as a
working town rather than a village. All three are layout LANDMARKS with module="civic_commerce";
build(S) dispatches on S.id. Plans are written in the SITE FRAME (lmkit.Site: origin = site centre,
local -Y = toward the street). The polygons are near-rectangles fitted by _tmp/site_finder.py;
_T measures their inner box (x0..x1, y0..y1) in the site frame so the plans follow if the lead nudges
a polygon. Levels: paved aprons / lots PAVE_Z = 0.03 (same as the generic parking lots), store walks
and building plinths 0.15 (sidewalk level), grass -0.05.

GAS STATION  (Main St, ~34 x 28 m, Main St along the front, intersection at the local -X end)
  - Concrete apron over the whole polygon + two driveway cuts across the grass strip to the kerb.
  - CANOPY (custom, 19 x 9 m, underside 4.6 m): rounded flat roof with a raised white lip and two
    vent boxes, yellow / red / white striped fascia, "GAS" lettering + yellow stars front and back and
    a star on each end, 12 glowing light panels underneath, six red-and-white columns standing on three
    raised pump islands (yellow bollards at the island noses).
  - 6 PUMPS (custom, linked duplicates): white body, red brand header, dark display with a glowing
    price strip, nozzle holsters + hoses on both faces (cars fill up on either side of an island).
  - PRICE PYLON (custom, 8.3 m) in a raised planter at the intersection corner, turned to face both
    Main St and the cross street: brick plinth, two legs, red "GAS" header, three price rows (grade
    colour tab + dark LED panel with glowing 7-segment prices), double sided.
  - MART (kit shop 4x3, H4, flat roof, red trim / flat red awnings) at the back right on a raised
    walk with bollards, bench, bin and an ICE chest (custom); custom "MART" sign box standing on the
    cornice; PROPANE exchange cage (custom) on its side wall; two nose-in stalls at the store front.
    Back left: 4 striped stalls, AIR pump (custom), dumpster, lot lights. Front right: landscaped
    corner island with the lot light; painted lane arrows (custom) at the two curb cuts.
  - 3 cars at the pumps (+3 parked).

SUPERMARKET  (Southside Pkwy x Main St corner, ~52 x 42 m; Main St runs along the local -X edge)
  - Asphalt lot over the polygon; a striped double row of stalls (KIT_ParkingLine) with ~70 % parked
    cars, a fire lane with a zebra to the entrance, a landscaped front strip (trees, lot lights) cut by
    the main entrance from Southside Pkwy, a second entrance from Main St into the aisle.
  - STORE: kit "commercial" 11x5 modules (33 x 15 m), 2 floors (H4 shop floor + clerestory floor),
    storefront glass, kit flat green awnings on the modules outside the portal span (the assembler's
    own awnings would cut through the portal piers), rooftop AC units, a green "MARKET" WALL SIGN
    (custom) on the Main St side wall.
  - ENTRANCE PORTAL (custom): two brick piers rising to 10.4 m, a green sign box with big white
    "MARKET" block letters above the parapet, a flat entrance canopy with lights on slim columns.
  - CART CORRALS (custom, x3) holding nested SHOPPING CARTS (custom, linked duplicates), a nested
    cart row at the door and a few strays in the lot; benches, planters, bins, bike rack, ICE chest.
  - POLE SIGN (custom, ~7 m) at the Southside Pkwy x Main St corner: MARKET panel + OPEN 24 HRS.
  - SERVICE YARD (Main St side, chain-link fence to the lot): raised loading DOCK with a roller door,
    dock seals and bumpers on the store's side wall, the box DELIVERY TRUCK backed up to it, trash
    compactor, dumpsters, pallets, crates, yard light; driveway cut to Main St.

DINER  (Main St, ~22 x 18 m)
  - Asphalt over the polygon, 6 nose-in stalls along the street with wheel stops, driveway apron.
  - DINER BODY (custom, 15 x 5.6 m rounded "streamline" shell): chrome skirt, red stripe, wrap-around
    window band with chrome mullions, mint fascia with a chrome pinstripe and red "DINER" letters,
    white overhanging roof slab, red entrance vestibule with a glass door; kit AC units on the roof;
    kit shed (6 x 3 m, roof vent + AC) as the kitchen annex at the back, dumpster + grease barrels.
  - NEON ROADSIDE SIGN (custom, ~8.5 m): teal stadium panel with glowing "DINER" letters and neon
    border, a yellow starburst on top, a red "EAT" arrow with chase bulbs, double sided.
  - PICNIC PATIO on the north side: picnic tables, a parasol table, string lights on four poles,
    white picket fence; bench, bin, planters at the door.

Custom geometry: every solid is closed (or sits on / inside another closed part) and faces are
oriented outward from each part (face_dir / fo), so the sites survive backface culling (Unity);
checked with _tmp/civic_commerce_cull.py (culled vs unculled close-ups + per-part signed volume).
Driveway aprons (driveway()) are the only geometry outside the polygons: they pave the 1-2 m grass
strip between a polygon edge and the sidewalk at the curb cuts, tucked under the kerb.
Repeated pieces (pumps, carts, corrals, ice chests) are linked duplicates of one mesh.
Budgets (custom tris incl. duplicates) are reported by build(S) in the JSON report.
"""
import math

import bpy
from mathutils import Matrix, Vector

from .. import config as C
from .. import facade as F
from .. import geom2d as G
from .. import scene
from ..assembler import BuildingSpec, H4
from ..meshutil import MeshBuilder

TAU = 2 * math.pi
R90 = math.pi / 2
PAVE_Z = C.ROAD_Z + 0.03      # apron / parking lot top (same as the generic lots in placement.py)
WALK_Z = C.LOT_Z              # store walks, plinths, building bases (= sidewalk level)
RX90 = Matrix.Rotation(math.pi / 2, 4, "X")
RZ180 = Matrix.Rotation(math.pi, 4, "Z")
CAR_COLORS = ["M_Awning_Red", "M_Awning_Green", "M_Awning_Blue", "M_Awning_Yellow", "M_Awning_Teal",
              "M_Wall_White", "M_Wall_Slate", "M_Trim_Dark", "M_Wall_Sky", "M_Wall_Coral"]


# =============================================================================== geometry helpers
def newell(P):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def face_dir(mb, pts, d, mat):
    """Polygon oriented so that its normal points along *d*."""
    P = [Vector(p) for p in pts]
    if len(P) < 3:
        return
    if newell(P).dot(Vector(d)) < 0:
        P.reverse()
    mb.face(P, mat)


def fo(mb, pts, inside, mat):
    """Polygon whose normal points away from *inside*."""
    P = [Vector(p) for p in pts]
    c = sum(P, Vector((0.0, 0.0, 0.0))) / len(P)
    face_dir(mb, P, c - Vector(inside), mat)


def bx(mb, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, skip=()):
    s = MeshBuilder()
    s.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
    if bevel > 0:
        s = F.bevelled(s, bevel)
    mb.extend(s)


def xf(mb, sub, loc=(0, 0, 0), rz=0.0):
    mb.extend(sub, matrix=Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rz, 4, "Z"))


def cyl(mb, center, axis, r, length, mat, seg=8, cap_mat=None, r2=None, caps=(True, True)):
    s = MeshBuilder()
    s.cylinder(0, 0, -length / 2, length / 2, r, mat, seg=seg, cap_top=caps[1], cap_bottom=caps[0],
               mat_cap=cap_mat, r_top=r2)
    rot = {"x": Matrix.Rotation(math.pi / 2, 4, "Y"), "y": Matrix.Rotation(-math.pi / 2, 4, "X"),
           "z": Matrix.Identity(4)}[axis]
    mb.extend(s, matrix=Matrix.Translation(Vector(center)) @ rot)


def strut(mb, a, b, w, d, mat):
    """Square-section bar from 3D point a to b."""
    a, b = Vector(a), Vector(b)
    ax = b - a
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


def xz_prism(mb, pts, yf, depth, mat_front, mat_side, back=None, loc=(0, 0, 0)):
    """Prism of an outline drawn in the XZ plane (pairs (x, z)): front face on y = yf facing -Y,
    extruded to y = yf + depth (back face only when *back* is a material)."""
    s = MeshBuilder()
    s.prism(pts, -(yf + depth), -yf, mat_front, mat_side, bottom=back)
    mb.extend(s, matrix=Matrix.Translation(Vector(loc)) @ RX90)


def rrect(cx, cy, w, d, r, seg=3):
    """Rounded rectangle (CCW). Offsetting = rrect(cx, cy, w + 2o, d + 2o, r + o) keeps vertex order."""
    r = max(0.0, min(r, w / 2 - 1e-3, d / 2 - 1e-3))
    if r < 1e-3:
        return [(cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2), (cx - w / 2, cy + d / 2), (cx - w / 2, cy - d / 2)]
    pts = []
    for qx, qy, a0 in ((cx + w / 2 - r, cy - d / 2 + r, -90), (cx + w / 2 - r, cy + d / 2 - r, 0),
                       (cx - w / 2 + r, cy + d / 2 - r, 90), (cx - w / 2 + r, cy - d / 2 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
    return pts


def ring_band(mb, P, Q, z0, z1, mat, top=True, bottom=True):
    """Proud band between outline P and its outward offset Q (same vertex count): outer wall on Q,
    top / bottom annuli."""
    mb.wall(Q, z0, z1, mat, closed=True)
    n = len(P)
    for i in range(n):
        j = (i + 1) % n
        if top:
            face_dir(mb, [(*P[i], z1), (*P[j], z1), (*Q[j], z1), (*Q[i], z1)], (0, 0, 1), mat)
        if bottom:
            face_dir(mb, [(*P[i], z0), (*P[j], z0), (*Q[j], z0), (*Q[i], z0)], (0, 0, -1), mat)


def star_pts(cx, cz, r, n=5, inner=0.45, rot=math.pi / 2):
    return [(cx + (r if k % 2 == 0 else r * inner) * math.cos(rot + math.pi * k / n),
             cz + (r if k % 2 == 0 else r * inner) * math.sin(rot + math.pi * k / n)) for k in range(2 * n)]


def both_sides(mb, sub):
    """Add *sub* (decoration built on the -Y face) and its 180 deg copy (the +Y face)."""
    mb.extend(sub)
    mb.extend(sub, matrix=RZ180)


# =============================================================================== block lettering
# Stroke font: centrelines on a 4 x 6 grid (digits 3 x 6, seven-segment style). Strokes are mitred
# thick polylines with square caps, extruded toward +Y (the board they are mounted on).
_GL = {
    "A": [[(0, 0), (0, 4.5), (1.5, 6), (2.5, 6), (4, 4.5), (4, 0)], [(0, 2.6), (4, 2.6)]],
    "B": [[(0, 0), (0, 6), (2.8, 6), (3.7, 5.1), (3.7, 3.9), (2.8, 3), (0, 3)],
          [(2.8, 3), (4, 1.9), (4, 1.1), (2.9, 0), (0, 0)]],
    "C": [[(4, 6), (1.2, 6), (0, 4.8), (0, 1.2), (1.2, 0), (4, 0)]],
    "D": [[(0, 0), (0, 6), (2.6, 6), (4, 4.6), (4, 1.4), (2.6, 0), (0, 0)]],
    "E": [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3.2, 3)]],
    "F": [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3.2, 3)]],
    "G": [[(4, 4.7), (4, 6), (1.2, 6), (0, 4.8), (0, 1.2), (1.2, 0), (4, 0), (4, 2.8), (2.3, 2.8)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(1.2, 0), (1.2, 6)], [(0, 6), (2.4, 6)], [(0, 0), (2.4, 0)]],
    "K": [[(0, 0), (0, 6)], [(0.3, 2.7), (4, 6)], [(1.5, 3.6), (4, 0)]],
    "L": [[(0, 6), (0, 0), (4, 0)]],
    "M": [[(0, 0), (0, 6), (2, 3.4), (4, 6), (4, 0)]],
    "N": [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    "O": [[(1.2, 0), (0, 1.2), (0, 4.8), (1.2, 6), (2.8, 6), (4, 4.8), (4, 1.2), (2.8, 0), (1.2, 0)]],
    "P": [[(0, 0), (0, 6), (2.8, 6), (4, 4.8), (4, 4.2), (2.8, 3), (0, 3)]],
    "R": [[(0, 0), (0, 6), (2.8, 6), (4, 4.8), (4, 4.2), (2.8, 3), (0, 3)], [(1.8, 3), (4, 0)]],
    "S": [[(4, 6), (1.2, 6), (0, 4.8), (0, 4.2), (1.2, 3), (2.8, 3), (4, 1.8), (4, 1.2), (2.8, 0), (0, 0)]],
    "T": [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    "U": [[(0, 6), (0, 1.2), (1.2, 0), (2.8, 0), (4, 1.2), (4, 6)]],
    "V": [[(0, 6), (2, 0), (4, 6)]],
    "W": [[(0, 6), (0, 0), (2, 2.6), (4, 0), (4, 6)]],
    "Y": [[(0, 6), (2, 3.2), (4, 6)], [(2, 3.2), (2, 0)]],
    "0": [[(0, 0), (0, 6), (3, 6), (3, 0), (0, 0)]],
    "1": [[(3, 0), (3, 6)]],
    "2": [[(0, 6), (3, 6), (3, 3), (0, 3), (0, 0), (3, 0)]],
    "3": [[(0, 6), (3, 6), (3, 0), (0, 0)], [(0, 3), (3, 3)]],
    "4": [[(0, 6), (0, 3), (3, 3)], [(3, 6), (3, 0)]],
    "5": [[(3, 6), (0, 6), (0, 3), (3, 3), (3, 0), (0, 0)]],
    "6": [[(3, 6), (0, 6), (0, 0), (3, 0), (3, 3), (0, 3)]],
    "7": [[(0, 6), (3, 6), (3, 0)]],
    "8": [[(0, 0), (0, 6), (3, 6), (3, 0), (0, 0)], [(0, 3), (3, 3)]],
    "9": [[(3, 3), (0, 3), (0, 6), (3, 6), (3, 0), (0, 0)]],
    ".": [[(0, 0)]],
    "-": [[(0, 3), (3, 3)]],
}
_GW = {"I": 2.4, ".": 0.0, " ": 2.2, "-": 3.0}
for _d in "0123456789":
    _GW[_d] = 3.0


def _stroke(mb, pts, h, yf, y1, mat, back=False):
    """Thick mitred polyline in the XZ plane (pairs (x, z), metres), half width h, from y = yf (front,
    facing -Y) to y = y1. Closed when the first and last points coincide."""
    P = [Vector((float(p[0]), float(p[1]))) for p in pts]
    if len(P) == 1 or (len(P) == 2 and (P[0] - P[1]).length < 1e-6):
        c = P[0]
        bx(mb, c.x - h, yf, c.y - h, c.x + h, y1, c.y + h, mat, skip=() if back else ("+y",))
        return
    closed = len(P) > 2 and (P[0] - P[-1]).length < 1e-6
    if closed:
        P = P[:-1]
    n = len(P)
    segs = n if closed else n - 1
    D = [(P[(i + 1) % n] - P[i]).normalized() for i in range(segs)]
    if not closed:
        P[0] = P[0] - D[0] * h
        P[-1] = P[-1] + D[-1] * h
    L, R = [], []
    for i in range(n):
        if closed:
            d0, d1 = D[i - 1], D[i % segs]
        else:
            d0, d1 = D[max(i - 1, 0)], D[min(i, segs - 1)]
        n0, n1 = Vector((-d0.y, d0.x)), Vector((-d1.y, d1.x))
        m = n0 + n1
        m = m.normalized() if m.length > 1e-6 else n0
        k = h / max(m.dot(n0), 0.5)
        L.append(P[i] + m * k)
        R.append(P[i] - m * k)
    v3 = lambda p, y: Vector((p.x, y, p.y))
    for i in range(segs):
        a, b = i, (i + 1) % n
        nr = Vector((-D[i].y, D[i].x))
        face_dir(mb, [v3(L[a], yf), v3(L[b], yf), v3(R[b], yf), v3(R[a], yf)], (0, -1, 0), mat)
        if back:
            face_dir(mb, [v3(L[a], y1), v3(L[b], y1), v3(R[b], y1), v3(R[a], y1)], (0, 1, 0), mat)
        face_dir(mb, [v3(L[a], yf), v3(L[b], yf), v3(L[b], y1), v3(L[a], y1)], (nr.x, 0, nr.y), mat)
        face_dir(mb, [v3(R[a], yf), v3(R[b], yf), v3(R[b], y1), v3(R[a], y1)], (-nr.x, 0, -nr.y), mat)
    if not closed:
        face_dir(mb, [v3(L[0], yf), v3(R[0], yf), v3(R[0], y1), v3(L[0], y1)], (-D[0].x, 0, -D[0].y), mat)
        face_dir(mb, [v3(L[-1], yf), v3(R[-1], yf), v3(R[-1], y1), v3(L[-1], y1)], (D[-1].x, 0, D[-1].y), mat)


def text(mb, s, cx, zc, height, yf, depth, mat, t=1.3, track=1.25, max_w=None, back=False):
    """Block letters centred on (cx, zc) in the XZ plane; front on y = yf (facing -Y), extruded
    *depth* toward +Y. Returns (width, height)."""
    u = height / (6.0 + t)
    widths = [_GW.get(ch, 4.0) + t for ch in s]
    total = (sum(widths) + track * (len(s) - 1)) * u
    if max_w and total > max_w:
        u *= max_w / total
        total = max_w
    h = t * u / 2
    z0 = zc - (6.0 + t) * u / 2
    x = cx - total / 2
    for ch, w in zip(s, widths):
        for pl in _GL.get(ch, []):
            _stroke(mb, [(x + h + px * u, z0 + h + pz * u) for px, pz in pl], h, yf, yf + depth, mat, back)
        x += (w + track) * u
    return total, (6.0 + t) * u


# =============================================================================== site bookkeeping
class _T:
    """Per-site tracker: inner box of the polygon in the site frame, custom tri budget, containment."""

    def __init__(self, S):
        self.S = S
        P = [S.to_local(p) for p in S.poly]
        xs, ys = sorted(p.x for p in P), sorted(p.y for p in P)
        self.x0, self.x1 = xs[1], xs[-2]
        self.y0, self.y1 = ys[1], ys[-2]
        self.tris = 0
        self.custom = 0
        self.kit = 0
        self.outside = []

    def check(self, lx, ly, what):
        p = self.S.to_world(lx, ly)
        if not self.S.inside(p):
            self.outside.append(f"{what}@({lx:.1f},{ly:.1f})")

    def add(self, o, lx, ly):
        self.custom += 1
        self.tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
        self.check(lx, ly, o.name)

    def report(self):
        return dict(custom_objects=self.custom, custom_tris=self.tris, kit_instances=self.kit,
                    outside=self.outside[:20])


def _sub(S, g):
    return f"{S.id}_{g}" if g else None


def place(S, T, name, mb, lx, ly, z=0.0, rot=0.0, group=None):
    """Custom mesh with its own origin at site-local (lx, ly), rotated by rot in the site frame."""
    p = S.to_world(lx, ly)
    o = S.mesh(name, mb, sub=_sub(S, group), loc=(p.x, p.y, z), rot=rot + S.rot)
    T.add(o, lx, ly)
    return o


def shared(name, fn):
    """Mesh datablock shared by every duplicate (built once per run)."""
    me = bpy.data.meshes.get(name)
    if me is None:
        me = fn().build(name)
    return me


def inst(S, T, me, name, lx, ly, z=0.0, rot=0.0, group=None):
    """Linked duplicate of a shared custom mesh at site-local (lx, ly)."""
    p = S.to_world(lx, ly)
    S.n += 1
    o = bpy.data.objects.new(f"LM_{S.id}_{name}_{S.n:03d}"[:63], me)
    scene.coll(S.coll + "/" + _sub(S, group)).objects.link(o)
    o.location = (p.x, p.y, z)
    o.rotation_euler = (0.0, 0.0, rot + S.rot)
    T.add(o, lx, ly)
    return o


def put(S, T, piece, lx, ly, z=PAVE_Z, rot=0.0, group=None, recolor=None, scale=None):
    o = S.put(piece, lx, ly, z, rot, recolor=recolor, scale=scale, local=True, sub=_sub(S, group))
    if o is not None:
        T.kit += 1
        T.check(lx, ly, piece)
    return o


def car(S, T, lx, ly, rot, group="Vehicles", van=False):
    piece = "Car_Van" if van else "Car_Sedan"
    return put(S, T, piece, lx, ly, PAVE_Z, rot + S.rng.uniform(-0.04, 0.04), group=group,
               recolor={"awning": S.rng.choice(CAR_COLORS)})


def lpoly(S, pts):
    return [S.to_world(x, y) for x, y in pts]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def pave(S, T, name, pts, mat, z=PAVE_Z, skirt=0.25, group="Ground"):
    o = S.paving(name, lpoly(S, pts), mat=mat, z=z, skirt=skirt, sub=_sub(S, group))
    T.custom += 1
    T.tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return o


def slab_mb(pts, z0, z1, top, side):
    mb = MeshBuilder()
    mb.prism(pts, z0, z1, top, side)
    return mb


def kerb_hit(S, p, d, max_len=10.0, step=0.1):
    for i in range(int(max_len / step)):
        q = p + d * (i * step)
        if not S.clear_of_roads(q, extra=0.0):
            return q
    return None


def driveway(S, T, a, b, out, name, mat, n=6, tuck=0.35):
    """Paved apron from the site edge a->b (site-local) straight out (site-local direction *out*) to
    the sidewalk, tucked under its kerb. Covers only the grass strip between the polygon and the
    sidewalk (curb cut for the cars); returns None when the edge already touches the sidewalk."""
    A, B = Vector(a), Vector(b)
    o = Vector(out).normalized()
    wd = S.to_world(o.x, o.y) - S.center
    near, far = [], []
    for k in range(n + 1):
        q = A.lerp(B, k / n)
        pin = S.to_world(q.x - o.x * 0.3, q.y - o.y * 0.3)
        hit = kerb_hit(S, pin, wd)
        if hit is None:
            return None
        near.append(pin)
        far.append(hit + wd * tuck)
    if max((f - p).length for f, p in zip(far, near)) < 0.8:
        return None
    mb = MeshBuilder()
    mb.prism([(p.x, p.y) for p in near + far[::-1]], PAVE_Z - 0.25, PAVE_Z, mat, mat)
    o_ = S.mesh(name, mb, sub=_sub(S, "Ground"))
    T.custom += 1
    T.tris += sum(len(p.vertices) - 2 for p in o_.data.polygons)
    return o_


def stalls(S, T, x0, n, w, yc, skip=(), group="Parking"):
    """Stripes for a row of n stalls (w wide, 5 m deep along Y, centred on yc) starting at x0.
    skip: [(lo, hi)] x ranges left open (entrances). Returns the x centres of the stalls kept."""
    out = []
    for i in range(n + 1):
        x = x0 + i * w
        if any(lo <= x - w / 2 <= hi and lo <= x + w / 2 <= hi for lo, hi in skip):
            continue
        put(S, T, "ParkingLine", x, yc, PAVE_Z + 0.002, 0.0, group=group)
    for i in range(n):
        x = x0 + (i + 0.5) * w
        if any(lo <= x <= hi for lo, hi in skip):
            continue
        out.append(x)
    return out


# =============================================================================== shared hero meshes
def mb_pump():
    """Fuel pump on an island top (origin z = island top); displays face +-X (cars on both sides)."""
    mb = MeshBuilder()
    bx(mb, -0.34, -0.48, 0.0, 0.34, 0.48, 0.12, "M_Metal_Dark", skip=("-z",))
    bx(mb, -0.27, -0.42, 0.12, 0.27, 0.42, 1.78, "M_Trim_White", bevel=0.04)
    bx(mb, -0.31, -0.46, 1.78, 0.31, 0.46, 2.12, "M_Awning_Red", bevel=0.04)
    bx(mb, -0.24, -0.4, 2.12, 0.24, 0.4, 2.18, "M_Trim_White", skip=("-z",))
    for sx in (-1, 1):
        x = sx * 0.27
        bx(mb, x, -0.27, 1.2, x + sx * 0.035, 0.27, 1.62, "M_Sign_Board")
        bx(mb, x + sx * 0.035, -0.2, 1.44, x + sx * 0.055, 0.2, 1.54, "M_Light_Emit")
        for k, col in enumerate(("M_Awning_Green", "M_Awning_Yellow", "M_Awning_Blue")):
            yy = -0.18 + 0.18 * k
            bx(mb, x, yy - 0.05, 1.27, x + sx * 0.05, yy + 0.05, 1.35, col)
        bx(mb, x, 0.12, 0.72, x + sx * 0.13, 0.34, 1.08, "M_Metal_Dark")                 # holster
        bx(mb, x + sx * 0.02, 0.17, 0.9, x + sx * 0.17, 0.29, 1.14, "M_Hazard_Dark")     # nozzle grip
        strut(mb, (x + sx * 0.09, 0.23, 0.74), (x + sx * 0.2, 0.08, 0.2), 0.06, 0.06, "M_Hazard_Dark")
        strut(mb, (x + sx * 0.2, 0.08, 0.2), (x + sx * 0.03, -0.24, 0.95), 0.06, 0.06, "M_Hazard_Dark")
    return mb


def mb_cart():
    """Shopping cart (~0.6 x 0.95 x 1.0 m), front -Y, handle at +Y. Nests along Y every ~0.3 m."""
    mb = MeshBuilder()
    b0 = [(-0.24, -0.36), (0.24, -0.36), (0.24, 0.3), (-0.24, 0.3)]
    b1 = [(-0.29, -0.46), (0.29, -0.46), (0.29, 0.4), (-0.29, 0.4)]
    z0, z1 = 0.46, 0.98
    c = Vector((0, -0.03, (z0 + z1) / 2))
    for i in range(4):
        j = (i + 1) % 4
        fo(mb, [(*b0[i], z0), (*b0[j], z0), (*b1[j], z1), (*b1[i], z1)], c, "M_Metal")
    face_dir(mb, [(*p, z1) for p in b1], (0, 0, 1), "M_Metal_Dark")       # reads as the hollow basket
    face_dir(mb, [(*p, z0) for p in b0], (0, 0, -1), "M_Metal")
    bx(mb, -0.29, 0.43, 0.97, 0.29, 0.5, 1.04, "M_Awning_Red")              # handle grip
    for sx in (-1, 1):
        strut(mb, (sx * 0.26, 0.38, 0.9), (sx * 0.27, 0.47, 1.0), 0.04, 0.04, "M_Metal")
        strut(mb, (sx * 0.22, -0.32, 0.47), (sx * 0.22, -0.3, 0.1), 0.04, 0.04, "M_Metal")
        strut(mb, (sx * 0.22, 0.27, 0.47), (sx * 0.22, 0.3, 0.1), 0.04, 0.04, "M_Metal")
    bx(mb, -0.22, -0.3, 0.17, 0.22, 0.3, 0.21, "M_Metal")                  # bottom tray
    for sx in (-1, 1):
        for yy in (-0.3, 0.3):
            bx(mb, sx * 0.22 - 0.03, yy - 0.06, 0.0, sx * 0.22 + 0.03, yy + 0.06, 0.11, "M_Hazard_Dark")
    return mb


def mb_corral():
    """Cart corral, 1.5 x 4.6 m along Y (one parking stall), open toward -Y, green sign at +Y."""
    mb = MeshBuilder()
    L, W = 4.6, 1.5
    for sx in (-1, 1):
        x = sx * W / 2
        for yy in (-L / 2, 0.0, L / 2):
            bx(mb, x - 0.05, yy - 0.05, 0.0, x + 0.05, yy + 0.05, 1.0, "M_Metal_Dark")
        bx(mb, x - 0.04, -L / 2, 0.92, x + 0.04, L / 2, 1.0, "M_Metal")
        bx(mb, x - 0.04, -L / 2, 0.45, x + 0.04, L / 2, 0.52, "M_Metal")
        bx(mb, x - 0.1, -L / 2, 0.0, x + 0.1, L / 2, 0.12, "M_Hazard")            # yellow curb rail
    bx(mb, -W / 2, L / 2 - 0.04, 0.92, W / 2, L / 2 + 0.04, 1.0, "M_Metal")
    bx(mb, -W / 2, L / 2 - 0.04, 0.45, W / 2, L / 2 + 0.04, 0.52, "M_Metal")
    for sx in (-1, 1):
        bx(mb, sx * 0.4 - 0.04, L / 2 - 0.04, 1.0, sx * 0.4 + 0.04, L / 2 + 0.04, 1.55, "M_Metal_Dark")
    bx(mb, -0.6, L / 2 - 0.05, 1.55, 0.6, L / 2 + 0.05, 2.1, "M_Awning_Green", bevel=0.03)
    sub = MeshBuilder()
    for sx in (-0.3, 0.0, 0.3):            # little cart pictogram bars
        bx(sub, sx - 0.08, -0.07, 1.68, sx + 0.08, -0.05, 1.97, "M_Trim_White", skip=("+y",))
    xf(mb, sub, (0, L / 2, 0))
    xf(mb, sub, (0, L / 2, 0), math.pi)
    return mb


def mb_ice_chest():
    mb = MeshBuilder()
    bx(mb, -0.85, -0.38, 0.0, 0.85, 0.38, 0.1, "M_Metal_Dark", skip=("-z",))
    bx(mb, -0.8, -0.36, 0.1, 0.8, 0.36, 1.25, "M_Wall_White", bevel=0.04)
    bx(mb, -0.72, -0.39, 0.3, 0.72, -0.36, 1.0, "M_Awning_Blue")
    text(mb, "ICE", 0.0, 0.65, 0.42, -0.43, 0.04, "M_Trim_White")
    bx(mb, -0.82, -0.38, 1.12, 0.82, 0.38, 1.16, "M_Metal")
    return mb


# =============================================================================== GAS STATION
def mb_canopy(W, D, islands, isl_len, col_y):
    mb = MeshBuilder()
    zu, zt = 4.6, 5.85
    P = rrect(0.0, 0.0, W, D, 0.7, seg=3)
    mb.wall(P, zu, zu + 0.24, "M_Awning_Yellow", closed=True)
    mb.wall(P, zu + 0.24, zt - 0.2, "M_Awning_Red", closed=True)
    mb.wall(P, zt - 0.2, zt + 0.16, "M_Trim_White", closed=True)
    Pi = rrect(0.0, 0.0, W - 0.6, D - 0.6, 0.4, seg=3)                   # raised white lip around the roof
    mb.wall(Pi, zt, zt + 0.16, "M_Trim_White", closed=True, outward_left=True)
    for i in range(len(P)):
        j = (i + 1) % len(P)
        face_dir(mb, [(*P[i], zt + 0.16), (*P[j], zt + 0.16), (*Pi[j], zt + 0.16), (*Pi[i], zt + 0.16)], (0, 0, 1),
                 "M_Trim_White")
    mb.tri_fill([Pi], zt, "M_Roof_Flat", up=True)
    for x in (-W / 4, W / 4):                                            # rooftop vent boxes
        bx(mb, x - 0.6, -0.45, zt, x + 0.6, 0.45, zt + 0.45, "M_Metal", bevel=0.03)
    mb.tri_fill([P], zu, "M_Trim_White", up=False)
    gaps = [(islands[i] + islands[i + 1]) / 2 for i in range(len(islands) - 1)]
    lx = [islands[0] - 2.4] + gaps + [islands[-1] + 2.4]
    for x in lx:
        for y in (-D / 2 + 1.6, 0.0, D / 2 - 1.6):
            bx(mb, x - 0.75, y - 0.32, zu - 0.06, x + 0.75, y + 0.32, zu, "M_Light_Emit", skip=("+z",))
    for ix in islands:
        isl = rrect(ix, 0.0, 1.3, isl_len, 0.62, seg=3)
        mb.prism(isl, -0.15, 0.25, "M_Concrete", "M_Curb")
        for sy in (-1, 1):
            cyl(mb, (ix, sy * (isl_len / 2 - 0.28), 0.25 + 0.45), "z", 0.13, 0.9, "M_Hazard", seg=8)
            y = sy * col_y
            bx(mb, ix - 0.27, y - 0.27, 0.25, ix + 0.27, y + 0.27, 1.35, "M_Awning_Red", bevel=0.03)
            bx(mb, ix - 0.22, y - 0.22, 1.35, ix + 0.22, y + 0.22, zu, "M_Trim_White")
    deco = MeshBuilder()
    zc = (zu + 0.24 + zt - 0.2) / 2
    text(deco, "GAS", 0.0, zc, 0.62, -D / 2 - 0.07, 0.07, "M_Trim_White", t=1.4)
    for sx in (-1, 1):
        xz_prism(deco, star_pts(sx * 2.3, zc, 0.36), -D / 2 - 0.06, 0.06, "M_Awning_Yellow", "M_Awning_Yellow")
    both_sides(mb, deco)
    end = MeshBuilder()
    xz_prism(end, star_pts(0.0, zc, 0.4), -W / 2 - 0.06, 0.06, "M_Awning_Yellow", "M_Awning_Yellow")
    mb.extend(end, matrix=Matrix.Rotation(-R90, 4, "Z"))
    mb.extend(end, matrix=Matrix.Rotation(R90, 4, "Z"))
    return mb


def mb_pylon(prices):
    mb = MeshBuilder()
    bx(mb, -1.55, -0.55, -0.1, 1.55, 0.55, 0.75, "M_Wall_Brick", bevel=0.04)
    bx(mb, -1.63, -0.63, 0.75, 1.63, 0.63, 0.87, "M_Trim_White", skip=("-z",))
    for sx in (-1, 1):
        bx(mb, sx * 0.95 - 0.16, -0.16, 0.87, sx * 0.95 + 0.16, 0.16, 3.0, "M_Metal_Dark", skip=("-z",))
    W2, T2 = 1.35, 0.28
    bx(mb, -W2, -T2, 3.0, W2, T2, 6.3, "M_Sign_Face")
    bx(mb, -W2 - 0.06, -T2 - 0.06, 6.3, W2 + 0.06, T2 + 0.06, 6.5, "M_Awning_Yellow")
    bx(mb, -W2 - 0.04, -T2 - 0.04, 6.5, W2 + 0.04, T2 + 0.04, 8.1, "M_Awning_Red")
    bx(mb, -W2 - 0.08, -T2 - 0.08, 8.1, W2 + 0.08, T2 + 0.08, 8.28, "M_Trim_White")
    bx(mb, -W2 - 0.06, -T2 - 0.06, 2.88, W2 + 0.06, T2 + 0.06, 3.0, "M_Trim_White")
    deco = MeshBuilder()
    text(deco, "GAS", 0.0, 7.3, 1.05, -T2 - 0.04 - 0.09, 0.09, "M_Trim_White", t=1.45)
    tabs = ("M_Awning_Green", "M_Awning_Yellow", "M_Awning_Blue")
    for k, price in enumerate(prices):
        zc = 5.65 - k * 0.98
        bx(deco, -1.22, -T2 - 0.04, zc - 0.4, -0.55, -T2, zc + 0.4, tabs[k % 3], skip=("+y",))
        bx(deco, -0.45, -T2 - 0.04, zc - 0.4, 1.22, -T2, zc + 0.4, "M_Sign_Board", skip=("+y",))
        text(deco, price, 0.39, zc, 0.56, -T2 - 0.04 - 0.03, 0.03, "M_Light_Emit", t=1.0, track=1.2)
    both_sides(mb, deco)
    return mb


def mb_mart_sign(w):
    mb = MeshBuilder()
    bx(mb, -w / 2, -0.42, 0.0, w / 2, -0.04, 1.42, "M_Awning_Red", skip=("-z",))
    bx(mb, -w / 2 - 0.05, -0.47, 0.0, w / 2 + 0.05, -0.04, 0.18, "M_Awning_Yellow")
    bx(mb, -w / 2 - 0.05, -0.47, 1.3, w / 2 + 0.05, -0.04, 1.48, "M_Trim_White")
    text(mb, "MART", 0.0, 0.74, 0.86, -0.42 - 0.1, 0.1, "M_Trim_White", t=1.4)
    return mb


def mb_air_pump():
    mb = MeshBuilder()
    bx(mb, -0.6, -0.5, -0.1, 0.6, 0.5, 0.12, "M_Concrete")
    bx(mb, -0.12, -0.12, 0.12, 0.12, 0.12, 1.0, "M_Metal_Dark")
    bx(mb, -0.3, -0.24, 1.0, 0.3, 0.24, 1.62, "M_Awning_Red", bevel=0.04)
    text(mb, "AIR", 0.0, 1.35, 0.26, -0.24 - 0.04, 0.04, "M_Trim_White", t=1.4)
    strut(mb, (0.3, -0.05, 1.2), (0.45, -0.25, 0.55), 0.05, 0.05, "M_Hazard_Dark")
    strut(mb, (0.45, -0.25, 0.55), (0.2, -0.35, 0.3), 0.05, 0.05, "M_Hazard_Dark")
    strut(mb, (0.2, -0.35, 0.3), (0.1, -0.15, 0.9), 0.05, 0.05, "M_Hazard_Dark")
    return mb


def mb_arrow(L=3.0, W=1.1):
    """Painted lane arrow on the apron (points +Y), 6 mm proud."""
    mb = MeshBuilder()
    pts = [(-0.18, -L / 2), (0.18, -L / 2), (0.18, L / 2 - 1.1), (W / 2, L / 2 - 1.1), (0.0, L / 2),
           (-W / 2, L / 2 - 1.1), (-0.18, L / 2 - 1.1)]
    mb.prism(pts, -0.01, 0.006, "M_RoadLine_White", "M_RoadLine_White")
    return mb


def mb_propane_cage(W=1.8, D=0.85, H=1.7):
    """Propane exchange cage: white frame, dark back, blue tanks behind bars (front -Y)."""
    mb = MeshBuilder()
    bx(mb, -W / 2, -D / 2, 0.0, W / 2, D / 2, 0.12, "M_Trim_White", skip=("-z",))
    bx(mb, -W / 2, D / 2 - 0.06, 0.12, W / 2, D / 2, H, "M_Trim_Dark")
    for sx in (-1, 1):
        bx(mb, sx * W / 2, -D / 2, 0.12, sx * (W / 2 - 0.06), D / 2 - 0.06, H, "M_Trim_White")
    bx(mb, -W / 2 - 0.04, -D / 2 - 0.04, H, W / 2 + 0.04, D / 2 + 0.04, H + 0.12, "M_Trim_White")
    for k in range(3):
        x = -W / 2 + W * (k + 0.5) / 3
        cyl(mb, (x, 0.02, 0.12 + 0.36), "z", 0.19, 0.72, "M_Awning_Blue", seg=8)
        cyl(mb, (x, 0.02, 0.84 + 0.06), "z", 0.12, 0.12, "M_Metal", seg=8)
        cyl(mb, (x, 0.02, 0.98 + 0.33), "z", 0.19, 0.66, "M_Awning_Blue", seg=8)
    for k in range(1, 7):
        x = -W / 2 + W * k / 7
        bx(mb, x - 0.02, -D / 2 - 0.02, 0.12, x + 0.02, -D / 2 + 0.02, H, "M_Trim_White")
    for z in (0.6, 1.15):
        bx(mb, -W / 2, -D / 2 - 0.03, z - 0.025, W / 2, -D / 2 + 0.02, z + 0.025, "M_Trim_White")
    bx(mb, -0.5, -D / 2 - 0.06, H - 0.36, 0.5, -D / 2 - 0.02, H - 0.08, "M_Awning_Blue")
    return mb


def build_gas(S, T):
    X0, X1, Y0, Y1 = T.x0, T.x1, T.y0, T.y1
    pave(S, T, "Apron", [(p.x, p.y) for p in (S.to_local(q) for q in S.poly)], "M_Concrete")
    S.register_lot(S.poly)
    # curb cuts to Main St
    driveway(S, T, (X0 + 4.5, Y0), (X0 + 11.5, Y0), (0, -1), "DriveIn", "M_Concrete")
    driveway(S, T, (X0 + 18.0, Y0), (X0 + 25.0, Y0), (0, -1), "DriveOut", "M_Concrete")

    # ---- canopy + pump islands + pumps
    ccx, ccy = X0 + 14.5, Y0 + 7.5
    islands = [-6.2, 0.0, 6.2]
    place(S, T, "Canopy", mb_canopy(19.0, 9.0, islands, 6.0, 2.2), ccx, ccy, PAVE_Z, 0.0, group="Canopy")
    pump = shared("LM_CC_Pump", mb_pump)
    for ix in islands:
        for py in (-0.95, 0.95):
            inst(S, T, pump, "Pump", ccx + ix, ccy + py, PAVE_Z + 0.25, 0.0, group="Canopy")
    # cars filling up (nose toward the store = +Y)
    car(S, T, ccx - 3.1, ccy + 0.4, math.pi)
    car(S, T, ccx + 8.2, ccy - 0.3, math.pi, van=True)
    car(S, T, ccx - 8.2, ccy + 0.8, math.pi)

    # ---- MART convenience store (kit) on a raised walk
    ox, oy = X1 - 7.5, Y1 - 11.0
    spec = BuildingSpec("shop", 4, 3, 1,
                        dict(wall="M_Wall_White", trim="M_Awning_Red", door="M_Door_Red", awning="M_Awning_Red",
                             roof="M_Roof_Slate", sign="M_Awning_Yellow"),
                        roof="flat", ground_h=H4, feats=dict(door_i=1, awning="flat", ac_units=2), seed=4101,
                        district="civic")
    S.building(spec, S.to_world(ox, oy), S.rot, name=f"LM_{S.id}_Mart")
    place(S, T, "MartWalk", slab_mb(rect(-6.3, -1.6, 6.3, 0.05), PAVE_Z - 0.1, WALK_Z, "M_Sidewalk", "M_Curb"),
          ox, oy, 0.0, 0.0, group="Store")
    place(S, T, "MartSign", mb_mart_sign(8.2), ox, oy, WALK_Z + H4, 0.0, group="Store")
    for bxx in (-5.2, -3.2, 1.2, 3.2, 5.2):
        put(S, T, "Bollard", ox + bxx, oy - 1.35, WALK_Z, 0.0, group="Store", recolor={"awning": "M_Awning_Yellow"})
    put(S, T, "Bench", ox - 4.2, oy - 0.65, WALK_Z, 0.0, group="Store")
    put(S, T, "TrashBin", ox + 0.3, oy - 0.7, WALK_Z, 0.0, group="Store")
    inst(S, T, shared("LM_CC_IceChest", mb_ice_chest), "IceChest", ox + 4.2, oy - 0.62, WALK_Z, 0.0, group="Store")
    fc = stalls(S, T, ox + 0.6, 2, 2.6, oy - 1.6 - 2.5)              # two nose-in stalls at the store
    car(S, T, fc[1], oy - 1.6 - 2.6, math.pi, group="Parking")

    # ---- price pylon in a raised planter at the corner (faces Main St and the cross street)
    px, py = X0 + 2.6, Y0 + 2.4
    bed = MeshBuilder()
    bed.prism(rrect(0, 0, 3.8, 2.1, 0.9, seg=3), PAVE_Z - 0.1, 0.38, "M_Grass", "M_Curb")
    place(S, T, "PylonBed", bed, px, py, 0.0, -0.87, group="Signs")
    place(S, T, "PricePylon", mb_pylon(["3.49", "3.79", "4.09"]), px, py, 0.38, -0.87, group="Signs")
    for dx, dy in ((-1.2, 0.7), (1.25, -0.75)):
        put(S, T, "Bush_A", px + dx, py + dy, 0.38, S.rng.uniform(0, TAU), group="Signs")

    # ---- back left: stalls, air pump, dumpster, lights
    sx0 = X0 + 1.4
    centres = stalls(S, T, sx0, 4, 2.6, Y1 - 2.7)
    for k, x in enumerate(centres):
        if k in (0, 2):
            car(S, T, x, Y1 - 2.9, math.pi, group="Parking")
    inst(S, T, shared("LM_CC_AirPump", mb_air_pump), "AirPump", X0 + 13.9, Y1 - 1.3, PAVE_Z, 0.0, group="Props")
    put(S, T, "TrashBin", X0 + 15.0, Y1 - 1.0, PAVE_Z, 0.0, group="Props")
    put(S, T, "Dumpster", ox - 7.6, Y1 - 1.0, PAVE_Z, 0.0, group="Props")
    put(S, T, "StreetLight", X0 + 0.5, Y1 - 6.0, PAVE_Z, R90, group="Props")
    # landscaped corner island (lamp + bushes) and painted lane arrows at the curb cuts
    isl = MeshBuilder()
    isl.prism(rrect(0, 0, 3.0, 2.4, 0.9, seg=3), PAVE_Z - 0.1, 0.2, "M_Grass", "M_Curb")
    place(S, T, "CornerIsland", isl, X1 - 1.9, Y0 + 1.7, 0.0, 0.0, group="Props")
    put(S, T, "StreetLight", X1 - 1.4, Y0 + 1.6, 0.2, -R90, group="Props")
    put(S, T, "Bush_B", X1 - 2.5, Y0 + 1.9, 0.2, 0.6, group="Props")
    arrow = shared("LM_CC_LaneArrow", mb_arrow)
    inst(S, T, arrow, "LaneArrow", X0 + 8.0, Y0 + 2.2, PAVE_Z, 0.0, group="Ground")
    inst(S, T, arrow, "LaneArrow", X0 + 21.5, Y0 + 2.2, PAVE_Z, math.pi, group="Ground")
    # propane exchange cage against the store's side wall
    place(S, T, "PropaneCage", mb_propane_cage(), ox + 6.0 + 0.55, oy + 3.0, PAVE_Z, R90, group="Store")
    return T.report()


# =============================================================================== SUPERMARKET
def mb_portal(depth_canopy=3.0):
    """Entrance portal on the store front (origin = facade centre at walk level, front -Y)."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 5.9, sx * 7.3))
        bx(mb, x0, -1.7, -0.05, x1, -0.02, 10.2, "M_Wall_Brick", bevel=0.05)
        bx(mb, x0 - 0.1, -1.8, 10.2, x1 + 0.1, 0.0, 10.45, "M_Trim_White", bevel=0.03)
        bx(mb, x0 - 0.06, -1.76, -0.05, x1 + 0.06, 0.04, 0.55, "M_Wall_Concrete")
    bx(mb, -5.9, -1.4, 7.1, 5.9, -0.02, 9.95, "M_Awning_Green", skip=("-x", "+x"))
    bx(mb, -5.9, -1.5, 6.92, 5.9, -0.02, 7.1, "M_Trim_White", skip=("-x", "+x"))
    bx(mb, -5.9, -1.5, 9.95, 5.9, -0.02, 10.12, "M_Trim_White", skip=("-x", "+x"))
    text(mb, "MARKET", 0.0, 8.52, 1.85, -1.4 - 0.14, 0.14, "M_Trim_White", t=1.35, max_w=10.9)
    # entrance canopy between the piers on two slim columns
    zc0, zc1, dc = 4.45, 4.85, depth_canopy
    bx(mb, -5.9, -dc, zc0, 5.9, -0.02, zc0 + 0.12, "M_Trim_White")        # closed: it projects past the piers
    bx(mb, -5.9, -dc, zc0 + 0.12, 5.9, -0.02, zc1, "M_Awning_Green")
    for x in (-3.6, -1.2, 1.2, 3.6):
        bx(mb, x - 0.5, -dc * 0.55 - 0.25, zc0 - 0.04, x + 0.5, -dc * 0.55 + 0.25, zc0, "M_Light_Emit", skip=("+z",))
    for sx in (-1, 1):
        bx(mb, sx * 5.5 - 0.1, -dc + 0.2, -0.05, sx * 5.5 + 0.1, -dc + 0.4, zc0, "M_Metal_Dark")
    return mb


def mb_dock(L=7.0, H=1.15):
    """Loading dock against a wall at local x = 0 (wall faces -X), centred on y = 0."""
    mb = MeshBuilder()
    mb.prism(rect(-2.2, -L / 2, 0.02, L / 2), -0.1, H, "M_Concrete", "M_Wall_Concrete")
    bx(mb, -2.26, -L / 2, H - 0.12, -2.2, L / 2, H, "M_Hazard")                         # edge stripe
    for yy in (-1.4, 1.4):
        bx(mb, -2.42, yy - 0.3, 0.35, -2.2, yy + 0.3, 0.95, "M_Hazard_Dark")             # bumpers
    for k in range(3):                                                                 # steps (y = -L/2 end)
        z = H * (k + 1) / 4
        bx(mb, -1.6, -L / 2 - 0.9 + k * 0.3, -0.1, -0.4, -L / 2, z, "M_Concrete", skip=("-z",))
    # roller door + dock seal on the wall above the platform
    bx(mb, -0.12, -1.5, H, -0.04, 1.5, H + 3.1, "M_RollerDoor", skip=("+x",))
    for k in range(1, 9):
        z = H + k * 3.1 / 9
        bx(mb, -0.15, -1.5, z - 0.03, -0.12, 1.5, z + 0.03, "M_Metal")
    for yy in (-1.85, 1.5):
        bx(mb, -0.42, yy, H, -0.04, yy + 0.35, H + 3.25, "M_Hazard_Dark", skip=("+x",))
    bx(mb, -0.42, -1.85, H + 3.1, -0.04, 1.85, H + 3.55, "M_Hazard_Dark", skip=("+x",))
    bx(mb, -0.3, -0.4, H + 3.6, -0.04, 0.4, H + 3.8, "M_Light_Emit", skip=("+x",))    # dock light
    return mb


def mb_compactor():
    mb = MeshBuilder()
    bx(mb, -0.95, -1.5, 0.0, 0.95, 1.5, 1.7, "M_Awning_Green", bevel=0.05)
    bx(mb, -0.6, -1.0, 1.7, 0.6, 1.0, 1.9, "M_Metal_Dark", skip=("-z",))
    bx(mb, 0.95, -0.7, 0.9, 1.25, 0.7, 2.6, "M_Metal", skip=("-z",))                   # chute into the wall
    bx(mb, -0.98, -1.2, 0.3, -0.95, 1.2, 0.5, "M_Hazard")
    return mb


def mb_zebra(n, w, L):
    mb = MeshBuilder()
    for k in range(n):
        x = -(n - 1) * 0.5 * (w * 2) + k * w * 2
        bx(mb, x - w / 2, -L / 2, 0.0, x + w / 2, L / 2, 0.012, "M_RoadLine_White", skip=("-z",))
    return mb


def mb_pole_sign():
    """Tall corner pole sign (double sided): MARKET panel + OPEN 24 HRS reader board."""
    mb = MeshBuilder()
    bx(mb, -0.75, -0.55, -0.1, 0.75, 0.55, 0.6, "M_Wall_Brick", bevel=0.04)
    bx(mb, -0.83, -0.63, 0.6, 0.83, 0.63, 0.72, "M_Trim_White", skip=("-z",))
    bx(mb, -0.2, -0.2, 0.72, 0.2, 0.2, 4.3, "M_Metal_Dark", skip=("-z",))
    W2, T2 = 2.0, 0.26
    bx(mb, -W2 - 0.08, -T2 - 0.08, 4.3, W2 + 0.08, T2 + 0.08, 4.42, "M_Trim_White")
    bx(mb, -W2, -T2, 4.42, W2, T2, 5.2, "M_Sign_Face")
    bx(mb, -W2 - 0.08, -T2 - 0.08, 5.2, W2 + 0.08, T2 + 0.08, 5.32, "M_Trim_White")
    bx(mb, -W2, -T2, 5.32, W2, T2, 7.0, "M_Awning_Green")
    bx(mb, -W2 - 0.08, -T2 - 0.08, 7.0, W2 + 0.08, T2 + 0.08, 7.16, "M_Trim_White")
    deco = MeshBuilder()
    text(deco, "MARKET", 0.0, 6.16, 1.0, -T2 - 0.08, 0.08, "M_Trim_White", t=1.4, max_w=3.6)
    text(deco, "OPEN 24 HRS", 0.0, 4.81, 0.42, -T2 - 0.05, 0.05, "M_Awning_Red", t=1.4, max_w=3.6)
    both_sides(mb, deco)
    return mb


def mb_wall_sign(w=5.8, h=1.5):
    """Flat wall sign (origin = wall plane, bottom centre; front -Y)."""
    mb = MeshBuilder()
    bx(mb, -w / 2, -0.24, 0.0, w / 2, -0.04, h, "M_Awning_Green", bevel=0.03)
    bx(mb, -w / 2 - 0.06, -0.28, -0.1, w / 2 + 0.06, -0.04, 0.0, "M_Trim_White")
    bx(mb, -w / 2 - 0.06, -0.28, h, w / 2 + 0.06, -0.04, h + 0.1, "M_Trim_White")
    text(mb, "MARKET", 0.0, h / 2, h * 0.66, -0.24 - 0.1, 0.1, "M_Trim_White", t=1.35, max_w=w - 0.5)
    return mb


def build_supermarket(S, T):
    X0, X1, Y0, Y1 = T.x0, T.x1, T.y0, T.y1
    pave(S, T, "Lot", [(p.x, p.y) for p in (S.to_local(q) for q in S.poly)], "M_Asphalt")
    S.register_lot(S.poly)

    # ---- store (kit commercial) + entrance portal
    W, D = 33.0, 15.0
    ox, oy = X1 - 3.5 - W / 2, Y1 - 1.0 - D
    spec = BuildingSpec("commercial", 11, 5, 2,
                        dict(wall="M_Wall_Cream", trim="M_Trim_White", door="M_Door_Teal", awning="M_Awning_Green",
                             roof="M_Roof_Slate", sign="M_Awning_Green"),
                        roof="flat", ground_h=H4,
                        feats=dict(door_i=5, awning=None, style="wide", ac_units=10, roof_access=True), seed=4202,
                        district="civic")
    S.building(spec, S.to_world(ox, oy), S.rot, name=f"LM_{S.id}_Store")
    place(S, T, "Walk", slab_mb(rect(-W / 2 - 0.3, -3.2, W / 2 + 0.3, 0.05), PAVE_Z - 0.1, WALK_Z, "M_Sidewalk", "M_Curb"),
          ox, oy, 0.0, 0.0, group="Store")
    place(S, T, "Portal", mb_portal(3.0), ox, oy, WALK_Z, 0.0, group="Store")
    for i in range(11):                                        # flat awnings outside the portal span
        mx = -W / 2 + 1.5 + 3.0 * i
        if abs(mx) < 8.0:
            continue
        put(S, T, "Awning_Flat_3m", ox + mx, oy, WALK_Z + 3.25, 0.0, group="Store",
            recolor={"awning": "M_Awning_Green", "trim": "M_Trim_White"})
    put(S, T, "TrashBin", ox - 7.4, oy - 2.4, WALK_Z, 0.0, group="Store")
    put(S, T, "TrashBin", ox + 7.4, oy - 2.4, WALK_Z, 0.0, group="Store")
    put(S, T, "Bench", ox + 10.5, oy - 1.4, WALK_Z, 0.0, group="Store")
    put(S, T, "Bench", ox - 10.5, oy - 1.4, WALK_Z, 0.0, group="Store")
    put(S, T, "BikeRack", ox + 15.6, oy - 1.2, WALK_Z, 0.0, group="Store")
    for x in (ox - 13.5, ox - 8.6, ox + 8.6, ox + 13.5):
        put(S, T, "Planter", x, oy - 2.6, WALK_Z, 0.0, group="Store")
    inst(S, T, shared("LM_CC_IceChest", mb_ice_chest), "IceChest", ox - 14.2, oy - 0.7, WALK_Z, 0.0, group="Store")
    cart = shared("LM_CC_Cart", mb_cart)
    for k in range(5):                                         # nested cart row at the door
        inst(S, T, cart, "Cart", ox - 4.7 + k * 0.32, oy - 1.0, WALK_Z, -R90, group="Carts")

    # ---- parking: fire lane zebra, two stall rows facing across the aisle, landscaped front strip
    place(S, T, "Zebra", mb_zebra(5, 0.5, 3.0), ox, oy - 3.2 - 1.5, PAVE_Z, 0.0, group="Parking")
    yA = oy - 3.2 - 3.0 - 2.5                  # row A centre (cars nose to the store)
    yB = yA - 2.5 - 6.8 - 2.5                  # row B centre (cars nose to the street)
    sw = 2.6
    n = int((X1 - X0 - 5.2) // sw)
    x0 = (X0 + X1) / 2 - n * sw / 2
    ent = (ox - 3.8, ox + 3.8)
    rowA = stalls(S, T, x0, n, sw, yA)
    rowB = stalls(S, T, x0, n, sw, yB, skip=[ent])
    corral = shared("LM_CC_Corral", mb_corral)
    corr_A = sorted(rowA, key=lambda x: abs(x - (ox - 13.0)))[0], sorted(rowA, key=lambda x: abs(x - (ox + 12.0)))[0]
    corr_B = sorted(rowB, key=lambda x: abs(x - (ox - 20.0)))[0]
    for x, yc, rot in ((corr_A[0], yA, 0.0), (corr_A[1], yA, 0.0), (corr_B, yB, math.pi)):
        inst(S, T, corral, "CartCorral", x, yc, PAVE_Z, rot, group="Carts")
        for k in range(S.rng.randint(2, 4)):
            inst(S, T, cart, "Cart", x, yc + (1.6 - k * 0.34) * (1 if rot == 0 else -1), PAVE_Z, rot + math.pi,
                 group="Carts")
    for x in rowA:
        if x in corr_A or S.rng.random() > 0.74:
            continue
        car(S, T, x, yA + 0.1, math.pi, group="Parking", van=S.rng.random() < 0.15)
    for x in rowB:
        if x == corr_B or S.rng.random() > 0.7:
            continue
        car(S, T, x, yB - 0.1, 0.0, group="Parking", van=S.rng.random() < 0.15)
    for (dx, dy, r) in ((-2.0, 0.6, 0.8), (5.5, -1.2, -2.3), (13.0, 0.3, 2.9)):
        inst(S, T, cart, "Cart", ox + dx, (yA + yB) / 2 + dy, PAVE_Z, r, group="Carts")
    # front landscape strip (cut by the entrance) with trees and lot lights
    yb0, yb1 = Y0 + 0.1, yB - 2.5 - 0.3
    for a, b in ((X0 + 0.2, ent[0] - 0.4), (ent[1] + 0.4, X1 - 0.2)):
        place(S, T, "FrontBed", slab_mb(rect(a, yb0, b, yb1), PAVE_Z - 0.1, 0.2, "M_Grass", "M_Curb"),
              0.0, 0.0, 0.0, 0.0, group="Landscape")
        k = 0
        x = a + (6.5 if a < ent[0] else 2.5)
        while x < b - 1.5:
            if k % 3 == 1:
                put(S, T, "StreetLight", x, (yb0 + yb1) / 2, 0.2, math.pi, group="Landscape")
            else:
                put(S, T, "Tree_Small" if k % 2 else "Tree_Round_A", x, (yb0 + yb1) / 2, 0.2,
                    S.rng.uniform(0, TAU), group="Landscape")
            x += 6.5
            k += 1
    # west strip (beside the end of the rows and the store) with trees
    place(S, T, "WestBed", slab_mb(rect(x0 + n * sw + 0.4, yb1, X1 - 0.15, oy - 3.4), PAVE_Z - 0.1, 0.2, "M_Grass", "M_Curb"),
          0.0, 0.0, 0.0, 0.0, group="Landscape")
    place(S, T, "WestBed2", slab_mb(rect(ox + W / 2 + 0.4, oy - 3.0, X1 - 0.15, Y1 - 0.15), PAVE_Z - 0.1, 0.2, "M_Grass", "M_Curb"),
          0.0, 0.0, 0.0, 0.0, group="Landscape")
    for yy in (yb1 + 4.0, oy - 6.0, oy + 3.0, oy + 10.5):
        xx = (x0 + n * sw + 0.4 + X1) / 2 if yy < oy else (ox + W / 2 + X1) / 2
        put(S, T, "Tree_Round_B" if yy > oy else "Tree_Round_A", xx, yy, 0.2, S.rng.uniform(0, TAU), group="Landscape")
    # pole sign at the Southside Pkwy x Main St corner, turned to the intersection
    place(S, T, "PoleSign", mb_pole_sign(), X0 + 2.8, (yb0 + yb1) / 2, 0.2, -0.5, group="Landscape")
    # entrances: from Southside Pkwy (front) and from Main St (-X edge, into the aisle)
    driveway(S, T, (ent[0], Y0), (ent[1], Y0), (0, -1), "DriveMain", "M_Asphalt")
    driveway(S, T, (X0, yB + 2.6), (X0, yA - 2.6), (-1, 0), "DriveSide", "M_Asphalt")

    # ---- service yard on the Main St side: dock, truck, compactor, dumpsters, pallets
    wx = ox - W / 2                                           # store side wall (faces -X)
    place(S, T, "Dock", mb_dock(7.0), wx, oy + 10.5, PAVE_Z, 0.0, group="Service")
    put(S, T, "Truck_Box", wx - 2.45 - 3.3, oy + 10.5, PAVE_Z, -R90, group="Service",
        recolor={"awning": "M_Awning_Green"})
    place(S, T, "Compactor", mb_compactor(), wx - 1.0, oy + 4.3, PAVE_Z, 0.0, group="Service")
    place(S, T, "SideSign", mb_wall_sign(), wx, oy + 3.0, WALK_Z + H4 + 0.75, -R90, group="Store")   # reads from Main St
    for k, x in enumerate((X0 + 2.0, X0 + 4.4)):
        put(S, T, "Dumpster", x, Y1 - 1.0, PAVE_Z, 0.0, group="Service")
    for k in range(3):
        put(S, T, "Pallet", X0 + 1.4, oy + 0.6, PAVE_Z + k * 0.15, 0.1 * k, group="Service")
        put(S, T, "Pallet", X0 + 2.8, oy + 0.6, PAVE_Z + k * 0.15, -0.08 * k, group="Service")
    put(S, T, "CrateStack", X0 + 4.6, oy + 0.7, PAVE_Z, 0.3, group="Service")
    put(S, T, "StreetLight", X0 + 0.5, oy + 5.0, PAVE_Z, R90, group="Service")
    fy = oy - 1.6
    S.fence_along([S.to_world(X0 + 0.4, fy), S.to_world(wx - 1.6, fy)], piece="Fence_Chain_3m",
                  z=PAVE_Z, sub=_sub(S, "Service"))
    driveway(S, T, (X0, oy + 6.5), (X0, oy + 14.5), (-1, 0), "DriveService", "M_Asphalt")
    return T.report()


# =============================================================================== DINER
def mb_diner_body(L=15.0, Dp=5.6, r=1.7):
    """Streamline diner shell, origin = body centre at walk level, front -Y."""
    mb = MeshBuilder()
    seg = 4
    P = rrect(0, 0, L, Dp, r, seg)
    Q = lambda o: rrect(0, 0, L + 2 * o, Dp + 2 * o, r + o, seg)
    mb.wall(P, -0.05, 0.85, "M_Metal", closed=True)                        # chrome skirt
    ring_band(mb, P, Q(0.06), 0.85, 1.02, "M_Awning_Red")                  # red stripe
    mb.wall(P, 1.02, 2.36, "M_Glass_Shop", closed=True)                    # wrap-around windows
    ring_band(mb, P, Q(0.05), 2.36, 2.5, "M_Metal")                        # chrome head
    mb.wall(P, 2.5, 3.32, "M_Wall_Mint", closed=True)                      # pastel fascia
    ring_band(mb, P, Q(0.04), 2.56, 2.63, "M_Metal")                       # pinstripe
    Qr = Q(0.38)
    mb.wall(Qr, 3.32, 3.6, "M_Trim_White", closed=True)                    # roof slab
    mb.tri_fill([Qr], 3.6, "M_Roof_Flat", up=True)
    n = len(P)
    for i in range(n):
        j = (i + 1) % n
        face_dir(mb, [(*P[i], 3.32), (*P[j], 3.32), (*Qr[j], 3.32), (*Qr[i], 3.32)], (0, 0, -1), "M_Trim_White")
    # chrome mullions every ~1.25 m around the perimeter (not behind the vestibule)
    pl = G.Polyline([Vector(p) for p in P + [P[0]]])
    k = int(pl.length / 1.25)
    for i in range(k):
        s = pl.length * i / k
        p, t = pl.pos(s), pl.tangent(s)
        if p.y < 0 and abs(p.x) < 2.0:
            continue
        nrm = Vector((t.y, -t.x))          # outward (CCW outline -> right of travel)
        c = p + nrm * 0.02
        q = [c + t * 0.05 + nrm * 0.05, c - t * 0.05 + nrm * 0.05, c - t * 0.05 - nrm * 0.04, c + t * 0.05 - nrm * 0.04]
        mb.prism([(v.x, v.y) for v in q], 1.02, 2.36, "M_Metal", "M_Metal")
    # vestibule with a glass door
    y0 = -Dp / 2 - 1.15
    bx(mb, -1.6, y0, -0.05, 1.6, -Dp / 2 + 0.3, 2.5, "M_Awning_Red", skip=("+y",))
    bx(mb, -1.75, y0 - 0.15, 2.5, 1.75, -Dp / 2 + 0.3, 2.68, "M_Trim_White")
    bx(mb, -0.62, y0 - 0.04, 0.0, 0.62, y0, 2.2, "M_Metal", skip=("+y",))
    bx(mb, -0.52, y0 - 0.06, 0.08, 0.52, y0 - 0.04, 2.1, "M_Glass_Shop", skip=("+y",))
    bx(mb, -0.3, y0 - 0.1, 1.0, 0.3, y0 - 0.06, 1.08, "M_Metal", skip=("+y",))         # push bar
    for sx in (-1, 1):
        bx(mb, sx * 1.6, y0 + 0.25, 0.9, sx * 1.64, y0 + 0.95, 2.2, "M_Glass_Shop")
    text(mb, "DINER", 0.0, 3.0, 0.56, -Dp / 2 - 0.1, 0.1, "M_Awning_Red", t=1.4, track=1.5)
    return mb


def mb_neon_sign():
    """Roadside neon sign, origin ground centre, faces -Y (double sided)."""
    mb = MeshBuilder()
    bx(mb, -1.4, -0.5, -0.1, 1.4, 0.5, 0.45, "M_Wall_Concrete", bevel=0.04)
    for sx in (-1, 1):
        bx(mb, sx * 0.95 - 0.13, -0.13, 0.45, sx * 0.95 + 0.13, 0.13, 4.75, "M_Metal", skip=("-z",))
    zc, Wp, Hp, T2 = 5.65, 5.2, 1.9, 0.22
    panel = rrect(0.0, zc, Wp, Hp, Hp / 2, seg=5)
    xz_prism(mb, panel, -T2, 2 * T2, "M_Awning_Teal", "M_Trim_White", back="M_Awning_Teal")
    rim = rrect(0.0, zc, Wp - 0.36, Hp - 0.36, Hp / 2 - 0.18, seg=5)
    deco = MeshBuilder()
    _stroke(deco, rim + [rim[0]], 0.045, -T2 - 0.05, -T2, "M_Light_Emit")
    text(deco, "DINER", 0.0, zc, 0.95, -T2 - 0.07, 0.07, "M_Light_Emit", t=1.3, track=1.4)
    # EAT arrow (red, bulbs), points +X
    arrow = [(-1.7, 2.9), (0.8, 2.9), (0.8, 2.55), (1.95, 3.3), (0.8, 4.05), (0.8, 3.7), (-1.7, 3.7)]
    text(deco, "EAT", -0.45, 3.3, 0.42, -0.17 - 0.05, 0.05, "M_Trim_White", t=1.4)
    pl = G.Polyline([Vector(p) for p in arrow + [arrow[0]]])
    k = int(pl.length / 0.38)
    for i in range(k):
        p = pl.pos(pl.length * i / k)
        c = Vector((sum(q[0] for q in arrow) / 7, sum(q[1] for q in arrow) / 7))
        p = p + (c - p).normalized() * 0.11
        bx(deco, p.x - 0.055, -0.17 - 0.06, p.y - 0.055, p.x + 0.055, -0.17 + 0.02, p.y + 0.055, "M_Light_Emit")
    both_sides(mb, deco)
    xz_prism(mb, arrow, -0.17, 0.34, "M_Awning_Red", "M_Awning_Red", back="M_Awning_Red")
    # starburst on a short mast
    bx(mb, -0.08, -0.08, zc + Hp / 2 - 0.05, 0.08, 0.08, zc + Hp / 2 + 0.6, "M_Metal")
    sz = zc + Hp / 2 + 1.25
    xz_prism(mb, star_pts(0.0, sz, 0.95, n=8, inner=0.38), -0.08, 0.16, "M_Awning_Yellow", "M_Awning_Yellow",
             back="M_Awning_Yellow")
    mb.sphere(0.0, 0.0, sz, 0.26, "M_Light_Emit", seg=8, rings=5)
    return mb


def mb_string_lights(pts, z_top=3.2, sag=0.45, bulb_every=0.75):
    """Poles at pts (local XY) with sagging wires + bulbs between consecutive poles."""
    mb = MeshBuilder()
    for x, y in pts:
        bx(mb, x - 0.07, y - 0.07, -0.1, x + 0.07, y + 0.07, z_top + 0.15, "M_Trim_Wood", skip=("-z",))
    for (ax, ay), (bxx, byy) in zip(pts, pts[1:]):
        a, b = Vector((ax, ay, z_top)), Vector((bxx, byy, z_top))
        nseg = 6
        P = []
        for k in range(nseg + 1):
            t = k / nseg
            q = a.lerp(b, t)
            q.z -= sag * 4 * t * (1 - t)
            P.append(q)
        for p, q in zip(P, P[1:]):
            strut(mb, p, q, 0.03, 0.03, "M_Hazard_Dark")
        L = (b - a).length
        nb = int(L / bulb_every)
        for k in range(1, nb):
            t = k / nb
            q = a.lerp(b, t)
            q.z -= sag * 4 * t * (1 - t) + 0.1
            bx(mb, q.x - 0.06, q.y - 0.06, q.z - 0.08, q.x + 0.06, q.y + 0.06, q.z + 0.06, "M_Light_Emit")
    return mb


def mb_wheel_stops(xs, y):
    mb = MeshBuilder()
    for x in xs:
        bx(mb, x - 0.8, y - 0.1, -0.02, x + 0.8, y + 0.1, 0.12, "M_Concrete", bevel=0.02)
    return mb


def build_diner(S, T):
    X0, X1, Y0, Y1 = T.x0, T.x1, T.y0, T.y1
    pave(S, T, "Lot", [(p.x, p.y) for p in (S.to_local(q) for q in S.poly)], "M_Asphalt")
    S.register_lot(S.poly)
    # plinth / walk around the diner body
    bcx, bcy, BL, BD = X1 - 0.9 - 7.5, Y0 + 9.6, 15.0, 5.6
    walk = rect(bcx - BL / 2 - 0.9, Y0 + 5.05, X1 - 0.1, bcy + BD / 2 + 0.6)
    place(S, T, "Walk", slab_mb(walk, PAVE_Z - 0.1, WALK_Z, "M_Sidewalk", "M_Curb"), 0.0, 0.0, 0.0, 0.0, group="Diner")
    place(S, T, "Body", mb_diner_body(BL, BD), bcx, bcy, WALK_Z, 0.0, group="Diner")
    for dx in (-4.0, 0.0, 4.0):
        put(S, T, "Roof_AC_Unit" if dx else "Roof_Vent", bcx + dx, bcy + 0.9, WALK_Z + 3.6, 0.0, group="Diner")
    # kitchen annex (kit shed, faces the back) + back-of-house clutter
    ax = bcx + 3.2
    spec = BuildingSpec("shed", 2, 1, 1,
                        dict(wall="M_Wall_White", trim="M_Trim_Dark", door="M_Door_Red", awning="M_Awning_Red",
                             roof="M_Roof_Charcoal", sign="M_Awning_Red"),
                        roof="flat", feats=dict(door_i=1), seed=4303, district="civic")
    S.building(spec, S.to_world(ax, bcy + BD / 2 + 2.7), S.rot + math.pi, name=f"LM_{S.id}_Kitchen")
    put(S, T, "Roof_Vent", ax + 1.4, bcy + BD / 2 + 1.2, WALK_Z + 3.0 + 0.2, 0.0, group="Diner")
    put(S, T, "Roof_AC_Unit", ax - 1.2, bcy + BD / 2 + 1.3, WALK_Z + 3.0 + 0.2, R90, group="Diner")
    put(S, T, "Dumpster", X1 - 1.4, Y1 - 1.0, PAVE_Z, 0.0, group="Props")
    put(S, T, "Barrel", ax - 4.4, Y1 - 0.8, PAVE_Z, 0.0, group="Props")
    put(S, T, "Barrel", ax - 3.7, Y1 - 0.9, PAVE_Z, 1.0, group="Props")
    put(S, T, "CrateStack", ax - 5.6, Y1 - 1.0, PAVE_Z, 0.4, group="Props")
    # entrance furniture on the walk
    wy = Y0 + 5.05
    put(S, T, "Bench", bcx + 3.6, wy + 0.55, WALK_Z, 0.0, group="Props")
    put(S, T, "TrashBin", bcx - 2.5, wy + 0.45, WALK_Z, 0.0, group="Props")
    put(S, T, "Planter", bcx - 6.4, wy + 0.5, WALK_Z, 0.0, group="Props")
    put(S, T, "Planter", bcx + 6.6, wy + 0.5, WALK_Z, 0.0, group="Props")
    # parking strip along the street: nose-in stalls with wheel stops
    sw = 2.6
    x0 = bcx - BL / 2 - 0.1
    n = int((X1 - x0 - 0.2) // sw)
    cs = stalls(S, T, x0, n, sw, Y0 + 2.5)
    place(S, T, "WheelStops", mb_wheel_stops([x - x0 for x in cs], 0.0), x0, wy - 0.45, PAVE_Z, 0.0, group="Parking")
    for k, x in enumerate(cs):
        if k in (0, 2, 3, 5):
            car(S, T, x, Y0 + 2.4, math.pi, group="Parking", van=(k == 3))
    driveway(S, T, (x0, Y0), (X1, Y0), (0, -1), "Drive", "M_Asphalt")
    # neon roadside sign at the north-front corner, angled to Main St and the northbound traffic
    sx, sy = X0 + 2.6, Y0 + 2.6
    place(S, T, "NeonSign", mb_neon_sign(), sx, sy, PAVE_Z, -0.7, group="Sign")
    # picnic patio on the north side with string lights and a picket fence
    px0, px1, py0, py1 = X0 + 0.4, bcx - BL / 2 - 1.2, wy + 1.4, Y1 - 0.4
    place(S, T, "Patio", slab_mb(rect(px0, py0, px1, py1), PAVE_Z - 0.1, WALK_Z, "M_Plaza", "M_Curb"),
          0.0, 0.0, 0.0, 0.0, group="Patio")
    pcx = (px0 + px1) / 2
    put(S, T, "PicnicTable", pcx, py0 + 2.0, WALK_Z, R90, group="Patio")
    put(S, T, "CafeTable", pcx, py0 + 5.4, WALK_Z, 0.3, group="Patio")
    put(S, T, "PicnicTable", pcx, py0 + 8.8, WALK_Z, R90, group="Patio")
    lp = [(px0 + 0.2, py0 + 0.2), (px0 + 0.2, py1 - 0.2), (px1 - 0.2, py1 - 0.2), (px1 - 0.2, py0 + 0.2)]
    place(S, T, "StringLights", mb_string_lights(lp), 0.0, 0.0, WALK_Z, 0.0, group="Patio")
    S.fence_along([S.to_world(px0 + 0.1, py0 + 1.0), S.to_world(px0 + 0.1, py1 - 0.1),
                   S.to_world(px1 - 1.0, py1 - 0.1)], piece="Fence_Picket_3m", z=WALK_Z, sub=_sub(S, "Patio"))
    return T.report()


# =============================================================================== entry point
BUILDERS = {"GasStation": build_gas, "Supermarket": build_supermarket, "Diner": build_diner}


def build(S):
    fn = BUILDERS.get(S.id)
    if fn is None:
        return dict(skipped=S.id)
    T = _T(S)
    return fn(S, T)
