"""Phase 4 landmark builder "parks": Central Park, the park districts, Crescent Commons, Riverwalk Gardens.

Routing (citygen/landmarks/__init__.py)
  build(S)           LANDMARKS["CentralPark"]                         -> _central_park
  build_area(S)      NO_BUILD CrescentCommons / RiverwalkGardens       -> _commons / _gardens
  build_district(S)  DISTRICTS of kind park: CentralPark (fringe only), LookoutPark, WillowWoods
  Lookout Point (the deck on Lookout Hill) lives in lookout.py and reuses the helpers below.

PLAN (world metres, x = east, y = north)
----------------------------------------
CENTRAL PARK site (Swan Pond, Picnic Hill, ParkLoop) - "the town's back garden", the first place the
animals reach over the Zoo Bridge (ANIMAL_ZONES ParkCanopy + SwanPond).
  * Fountain Plaza (-142.5, -27.5): round paved plaza with a tiered stone fountain at the SE corner of the
    ParkLoop. It hides the loop's closing kink and is the park's FRONT DOOR from the pet shop side (Maple St /
    Swan Ln corner, entrance E1 with brick gate pillars). Benches, lamps and flower beds sit between the path
    mouths, so the plaza stays a clear crossroads.
  * Entrances = short connector paths from the loop to the sidewalks, each with brick gate pillars + iron fence
    wings: E1 plaza -> Maple St / Swan Ln corner, E2 east loop -> Swan Lane (towards the Mill Bridge),
    E3 south-west loop -> Park Lane, E5 north loop -> the canal Riverwalk (no gate, it is a park path).
  * Swan Pond edge: reed beds on the shady west / south-west shore (otter + flamingo cover), shore rocks, a
    small timber pier on the east shore reached by a dirt spur from the loop, and a swan pedal boat moored at
    the pier (the pond's name in one readable silhouette).
  * Picnic Hill (-225, 45, +6 m): picnic tables in a loose ring round the summit under one big shade tree,
    the open east flank kept as a lawn to run / roll down. The west flank and the hill foot carry the dense
    mixed tree clumps of the ParkCanopy zone (monkeys / lemurs / sloth) - crowns overlap into a canopy.
    PicnicHillThicket (hiding spot) is dressed HERE (hiding_spots.py skips spots inside dressed sites): a
    horseshoe of dark bushes round a crawl-in hollow that opens to the far (west) side, a boulder, two trees.
  * Playground on the flat strip between the loop and the canal Riverwalk (-195, 64): soft-fall sand pad
    with a timber edge, play tower with slide + ladder, climbing arch, seesaw, two kit swings, parent benches.
  * Open lawns: the centre of the north lawn inside the loop and the east lawn by the pier stay open on
    purpose - sight lines across the pond and chase space for multiplayer round-ups; small tree groups only
    along the inside of the loop (shade over the path) and lily pads / reeds break up the pond.
  * Lamp_Park + benches along ParkLoop / PicnicHillPath (benches on the outer side looking across the path
    to the water), trash bins next to benches, flower beds at the plaza, gates and playground.
CENTRAL PARK district fringe (build_district): only the land OUTSIDE the site polygon and WEST of Swan Lane
  (the east part of the district is Maple Green + the Riverwalk promenade, owned by other builders): tree rows
  along Willow Rd / Park Ln / Maple St and bushes - a soft green edge that frames the park from the streets.
LOOKOUT PARK district: grassy Lookout Hill for goats / llamas. The upper hill (r < 18 m) stays open grass;
  trees are scattered over the lower slopes and the district edges, boulders everywhere (a "goat rocks"
  outcrop on the east flank to climb), a summit cairn with a pennant flagpole and two benches facing the
  town, blue-banded trail markers along LookoutTrail (outside the Lookout site, which lookout.py builds).
WILLOW WOODS district: the wild south-west corner (bear / moose / wolves). Dense mixed woodland (cones +
  round trees, dark foliage) with an understory of bushes, rocks, fallen logs and stumps, but trunks >= 5 m
  apart so big animals and players can weave through. Four small clearings (pond meadow, a north "bear"
  clearing with boulders, an east picnic clearing, a south glade). Beaver Pond: reeds, a beaver lodge mound
  half in the water, chewed stumps, a log reaching into the water. Woods End trailhead: ranger notice board,
  bench, bin, trailhead post; yellow-banded markers along WoodsTrail. WoodsHollow (district land, not a site)
  is dressed by the global hiding pass - this builder keeps a 4 m pocket free round it (same for LookoutBushes).
CRESCENT COMMONS (NO_BUILD, 30 x 38 m): a 5 x 5 cell hedge maze (Hedge_3m on a 3 m grid, corridors ~2.1 m)
  entered from CommonsWalk on the east, exit north to the swing lawn; its centre cell holds the CrescentHedge
  hiding spot (dressed here: birdbath + blossom bush). North lawn: two swings on a sand pad, benches, picnic table;
  blossom trees in the corners, flower beds at the maze mouth, park lamps on the walk.
RIVERWALK GARDENS (NO_BUILD on the north quay): community allotments facing the canal promenade. Picket
  fence with a rose-arch gate on the Riverwalk, a gravel cross of paths, 15+ custom raised beds (lettuce,
  cabbages, tomatoes, pumpkins, carrots), two dense bean rows with a crawl gap on a freshly dug plot (the
  RiverwalkGardens hiding spot, dressed here) plus bean teepees, a sage corrugated tool shed and a small butter
  potting shed (assembler 'shed'), compost crates, water butt, bench, a scarecrow and a sunflower border along
  the promenade fence.

CONVENTIONS / WORKAROUNDS
  * Sub-collections are named f"{S.id}_<Thing>" (see subc): scene.coll() resolves collections by GLOBAL
    name, so a bare sub="Trees" / "Fences" / "Plants" would put objects into KIT_Library/nature/... (or into
    another site's collection). Framework bug, reported.
  * S.clear_of_roads() does not cover cul-de-sac bulbs (the road hash only holds edge half-width + sidewalk);
    Planner adds the bulbs (CULDESAC_R + sidewalk) itself. Framework gap, reported.
  * The site builder hands its connector paths + occupancy to the district fringe builder through _SHARED
    (same Blender process; the fringe falls back to its own checks when the site did not run).
  * Land decides ownership: the Central Park site builder lays out the whole park (entrances need the loop),
    then build_district(CentralPark) first ADOPTS every site piece whose footprint stands > 0.9 m outside the
    site polygon (_rehome: gate pillars, connector paths, fence wings, edge trees, loop furniture) - renamed
    LM_D_CentralPark_..., moved to the district's sub-collections and so into the district's FBX.
  * Gate pillars step back until both footings clear the sidewalk corridor (gate_footing_clear); E1 at the
    curved Maple St / Swan Ln corner kerb is pulled a further 0.6 m back.
  * Reeds are 2-3 crossed double-sided blade cards per clump (+ a cattail); repeated garden pieces (beds per
    crop, bean rows, teepees, sunflowers) share one mesh each (shared_obj) - unique tris count once.
  * Willow Woods gets a contoured forest floor (_forest_floor: moss + deep-shade layers from the tree density,
    lighter meadows in the clearings, a light verge along the trail) and a dense understory (bush clusters,
    logs and stumps inside the groves; tree occupancy shrinks to the trunks for that pass).
  * Custom meshes: LM_<Site>_<Thing>, palette materials only, outward normals (MeshBuilder / kit.nature
    helpers); organic parts smooth-shaded with kit.nature._shade. Everything sits on S.ground_z (hills) or on
    the pond bank profile (pond_bank_z).
"""
import math
import random

from mathutils import Matrix, Vector

from .. import config as C
from .. import geom2d as G
from .. import scene
from ..kit import nature as NK
from ..meshutil import MeshBuilder

TAU = 2.0 * math.pi
GZ = C.GROUND_Z
_SHARED = {}        # Central Park site -> district fringe (connector paths + occupancy), same process
WOOD, WOOD_D, BARK = "M_Wood_Light", "M_Trim_Wood", "M_Bark"
STONE = "M_CanalStone"


# =============================================================================== small helpers
def subc(S, name):
    """Unique sub-collection name. scene.coll() looks collections up by GLOBAL name, so a bare 'Trees'
    would land in KIT_Library/nature/Trees - always prefix with the site id."""
    return f"{S.id}_{name}"


def face_rot(f):
    """Z rotation that turns a kit piece's front (-Y) toward direction f."""
    return math.atan2(f[0], -f[1])


def wchoice(rng, items):
    tot = sum(w for _, w in items)
    r = rng.uniform(0, tot)
    for it, w in items:
        r -= w
        if r <= 0:
            return it
    return items[-1][0]


def V2(x, y=None):
    if y is None:
        return Vector((float(x[0]), float(x[1])))
    return Vector((float(x), float(y)))


def zmin(S, p, r=0.4, n=6):
    """Lowest ground under a small footprint (so nothing floats on slopes)."""
    z = S.ground_z(p[0], p[1])
    for k in range(n):
        a = TAU * k / n
        z = min(z, S.ground_z(p[0] + r * math.cos(a), p[1] + r * math.sin(a)))
    return z


class Occ:
    """Circle occupancy grid (my own placements: trees, benches, props...)."""

    def __init__(self, cell=8.0):
        self.cell = cell
        self.g = {}

    def _k(self, x, y):
        return (int(math.floor(x / self.cell)), int(math.floor(y / self.cell)))

    def free(self, p, r):
        i, j = self._k(p[0], p[1])
        span = 1 + int(r // self.cell)
        for di in range(-span, span + 1):
            for dj in range(-span, span + 1):
                for (q, rq) in self.g.get((i + di, j + dj), ()):
                    if (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 < (r + rq) ** 2:
                        return False
        return True

    def add(self, p, r):
        self.g.setdefault(self._k(p[0], p[1]), []).append(((float(p[0]), float(p[1])), r))


def path_polyline(path_entry, step=1.0):
    spl, _ = G.catmull_rom([G.V(q) for q in path_entry["path"]], step=step)
    return G.Polyline(spl)


def paths_hash(layout, extra_paths=()):
    """SegmentHash of every footpath (layout.PATHS + my connectors) with radius = half width."""
    h = G.SegmentHash(cell=12.0)
    for p in list(getattr(layout, "PATHS", [])) + list(extra_paths):
        pl = path_polyline(p, step=1.5)
        h.add_polyline(pl.pts, p.get("width", 3.0) / 2.0, payload=p["id"])
    return h


class Pond:
    def __init__(self, pd):
        self.id = pd["id"]
        self.c = G.V(pd["center"])
        self.bank = pd.get("bank", 3.0)
        self.outline = G.ensure_ccw(G.blob_polygon(self.c, pd["radii"], seg_len=2.0, rot=pd.get("rot", 0.0)))
        ang = []
        for p in self.outline:
            d = p - self.c
            ang.append((math.atan2(d.y, d.x) % TAU, d.length))
        ang.sort()
        self._ang = ang

    def R(self, a):
        a = a % TAU
        A = self._ang
        for i in range(len(A)):
            a0, r0 = A[i - 1]
            a1, r1 = A[i]
            if i == 0:
                a0 -= TAU
            if a0 <= a <= a1:
                t = 0.0 if a1 - a0 < 1e-9 else (a - a0) / (a1 - a0)
                return r0 + (r1 - r0) * t
        return A[0][1]

    def depth_in(self, p):
        """Signed distance inside the outline along the radius (> 0 = inside the bank)."""
        d = G.V(p) - self.c
        return self.R(math.atan2(d.y, d.x)) - d.length

    def bank_z(self, p):
        din = self.depth_in(p)
        if din <= 0:
            return GZ
        return GZ - 0.9 * min(1.0, din / self.bank)

    def at(self, a, inset):
        """Point at angle a, *inset* metres inside the outline (negative = outside)."""
        r = self.R(a) - inset
        return self.c + Vector((math.cos(a), math.sin(a))) * r

    def water_inset(self):
        return self.bank * 0.45


def pond_by_id(layout, pid):
    for pd in getattr(layout, "PONDS", []):
        if pd["id"] == pid:
            return Pond(pd)
    return None


def obj_at(S, name, mb, x, y, z, rot=0.0, sub=None, smooth=None, angle=50.0):
    """Custom mesh built in local coords, placed + rotated in the world."""
    o = S.mesh(name, mb, sub=sub, loc=(x, y, z))
    o.rotation_euler = (0.0, 0.0, rot)
    if smooth:
        NK._shade(o, set(smooth), angle)
    return o


def xform(x, y, z, rot):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z")


def sidewalk_hit(S, p, d, max_len=45.0, step=0.2):
    """March from p along d until the road/sidewalk clearance (or canal) is hit. Returns the point."""
    p, d = V2(p), V2(d).normalized()
    n = int(max_len / step)
    for i in range(n):
        q = p + d * (i * step)
        if not S.clear_of_roads(q, extra=0.0):
            return q
    return None


def tri_count(objs):
    """Unique custom tris: a mesh shared by several objects (shared_obj) counts once, like kit pieces."""
    n = 0
    seen = set()
    for o in objs:
        if o is not None and o.type == "MESH" and o.data.name not in seen:
            seen.add(o.data.name)
            n += sum(len(pp.vertices) - 2 for pp in o.data.polygons)
    return n


def shared_obj(S, cache, key, name, make_mb, x, y, z, rot=0.0, sub=None, smooth=None, angle=50.0):
    """Linked duplicate of a custom mesh. The first call with *key* builds it (mesh data LM_<site>_<key>), later
    calls reuse that mesh data - repeated garden beds, sunflowers, bean rows cost their tris once (the FBX
    export shares the geometry, exactly like kit instances)."""
    data = cache.get(key)
    if data is None:
        o = obj_at(S, name, make_mb(), x, y, z, rot, sub=sub, smooth=smooth, angle=angle)
        o.data.name = f"LM_{S.id}_{key}"[:63]
        cache[key] = o.data
        return o
    return scene.obj(f"LM_{S.id}_{name}"[:63], data, S.coll + (f"/{sub}" if sub else ""), (x, y, z), rot)


# =============================================================================== custom geometry
def fountain_mb():
    """Tiered stone fountain, basin radius 2.9 m, ~3 m tall. Origin = basin centre on the plaza."""
    mb = MeshBuilder()
    R = 2.9
    wat = "M_Water"
    prof = [(R, -0.15), (R, 0.38), (R + 0.14, 0.43), (R + 0.17, 0.55), (R + 0.07, 0.64), (R - 0.3, 0.64),
            (R - 0.37, 0.57), (R - 0.37, 0.34), (0.0, 0.34)]
    NK.lathe(mb, prof, STONE, seg=28, mats=[STONE, "M_Plaza_Accent", STONE, STONE, STONE, STONE, STONE, wat])
    ped = [(0.66, 0.3), (0.66, 0.44), (0.48, 0.56), (0.3, 0.74), (0.25, 1.12), (0.38, 1.24), (1.02, 1.42),
           (1.16, 1.5), (1.12, 1.6), (0.98, 1.56), (0.96, 1.52), (0.24, 1.52), (0.19, 2.05), (0.3, 2.16),
           (0.52, 2.28), (0.5, 2.36), (0.42, 2.34), (0.12, 2.34), (0.16, 2.55), (0.09, 2.85), (0.0, 2.98)]
    mats = [STONE] * 10 + [wat] + [STONE] * 5 + [wat] + [wat, wat, wat]
    NK.lathe(mb, ped, STONE, seg=20, mats=mats)
    # arcing water jets (quadratic bezier arcs): 8 from the middle bowl lip into the basin, 4 from the top
    def arc(p0, p1, p2, r0, r1, n=9):
        pts, rad = [], []
        for i in range(n):
            t = i / (n - 1)
            pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
            rad.append(r0 + (r1 - r0) * t)
        return pts, rad

    for (n, ph, p0, p1, p2, r0, r1) in ((8, TAU / 16, (1.1, 1.55), (1.75, 2.15), (2.12, 0.34), 0.035, 0.045),
                                        (4, 0.0, (0.2, 2.98), (0.72, 3.45), (0.9, 1.54), 0.028, 0.036)):
        prof, rad = arc(p0, p1, p2, r0, r1)
        for k in range(n):
            a = TAU * k / n + ph
            ca, sa = math.cos(a), math.sin(a)
            sweep(mb, [(r * ca, r * sa, z) for r, z in prof], rad, wat, seg=5, cap0=True, cap1=True)
    return mb


def pier_mb(L=9.0, W=2.0, head_w=3.6, head_d=2.4, dz=0.0, post_bot=-1.3):
    """Timber pier along +Y from y=0 (shore) to y=L (+ T head). Deck top at z=dz."""
    mb = MeshBuilder()
    t = 0.09
    y = 0.0
    k = 0
    while y < L - 0.05:
        y1 = min(L, y + 0.3)
        NK.bbox(mb, -W / 2, y + 0.02, dz - t, W / 2, y1 - 0.02, dz, WOOD if k % 3 else "M_Fence_Wood")
        y = y1 + 0.03
        k += 1
    # T head
    y = L
    while y < L + head_d - 0.05:
        y1 = min(L + head_d, y + 0.3)
        NK.bbox(mb, -head_w / 2, y + 0.02, dz - t, head_w / 2, y1 - 0.02, dz, WOOD if k % 3 else "M_Fence_Wood")
        y = y1 + 0.03
        k += 1
    for sx in (-1, 1):
        NK.bbox(mb, sx * (W / 2 - 0.25) - 0.1, -0.2, dz - 0.32, sx * (W / 2 - 0.25) + 0.1, L + head_d - 0.1,
                dz - t, WOOD_D)
    NK.bbox(mb, -head_w / 2 + 0.1, L + 0.2, dz - 0.32, head_w / 2 - 0.1, L + 0.45, dz - t, WOOD_D)
    NK.bbox(mb, -head_w / 2 + 0.1, L + head_d - 0.45, dz - 0.32, head_w / 2 - 0.1, L + head_d - 0.2, dz - t, WOOD_D)
    # posts (under water) + mooring bollards at the head corners
    ys = [y0 for y0 in (2.0, 4.6, 7.2) if y0 < L - 0.5] + [L + 0.3]
    for yy in ys:
        for sx in (-1, 1):
            NK.lathe(mb, [(0.13, post_bot), (0.13, dz - 0.1), (0.0, dz - 0.1)], WOOD_D, seg=6,
                     cx=sx * (W / 2 - 0.05), cy=yy)
    for sx in (-1, 1):
        x = sx * (head_w / 2 - 0.15)
        NK.lathe(mb, [(0.14, post_bot), (0.14, dz + 0.55), (0.17, dz + 0.6), (0.0, dz + 0.66)], WOOD_D, seg=6,
                 cx=x, cy=L + head_d - 0.18)
        NK.lathe(mb, [(0.13, post_bot), (0.13, dz - 0.1), (0.0, dz - 0.1)], WOOD_D, seg=6, cx=x, cy=L + 0.3)
    # end rail between the head bollards
    NK.bbox(mb, -head_w / 2 + 0.15, L + head_d - 0.24, dz + 0.42, head_w / 2 - 0.15, L + head_d - 0.12, dz + 0.5,
            WOOD_D)
    return mb


def sweep(mb, pts, radii, mat, seg=8, cap0=False, cap1=True):
    """Tube swept along a 3D polyline (parallel-transport frames) - smooth necks, branches..."""
    P = [Vector(p) for p in pts]
    n = len(P)
    T = []
    for i in range(n):
        a = P[max(0, i - 1)]
        b = P[min(n - 1, i + 1)]
        T.append((b - a).normalized())
    ref = Vector((1.0, 0.0, 0.0)) if abs(T[0].x) < 0.9 else Vector((0.0, 1.0, 0.0))
    X = (ref - T[0] * ref.dot(T[0])).normalized()
    rings = []
    for i in range(n):
        if i > 0:
            X = (X - T[i] * X.dot(T[i])).normalized()
        Y = T[i].cross(X)
        r = radii[i]
        rings.append([P[i] + (X * math.cos(TAU * k / seg) + Y * math.sin(TAU * k / seg)) * r for k in range(seg)])
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            mb.face([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]], mat)
    if cap1:
        mb.face(rings[-1], mat)
    if cap0:
        mb.face(list(reversed(rings[0])), mat)


def swan_boat_mb():
    """Swan pedal boat, ~1.6 x 2.8 m, head toward -Y. Origin = waterline centre."""
    mb = MeshBuilder()
    W_ = "M_Trim_White"
    NK.blob(mb, (0.0, 0.15, 0.25), 0.95, W_, seg=12, rings=6, sz=0.5, sz_bot=0.42, sx=0.82, sy=1.4, jit=0.0, seed=3)
    for sx in (-1, 1):
        NK.blob(mb, (sx * 0.62, 0.35, 0.62), 0.55, W_, seg=8, rings=5, sz=0.55, sx=0.42, sy=1.3, jit=0.0, seed=4)
    NK.blob(mb, (0.0, 1.35, 0.78), 0.32, W_, seg=8, rings=5, sz=0.8, sx=0.9, sy=0.8, jit=0.0, seed=5)
    NK.bbox(mb, -0.48, 0.1, 0.5, 0.48, 0.7, 0.72, "M_Awning_Teal", bevel=0.05)
    NK.beam(mb, (0.0, 0.62, 0.62), (0.0, 0.78, 1.12), 0.96, 0.14, "M_Awning_Teal", up=(0.0, -1.0, 0.3), bevel=0.04)
    neck = [(0.0, -0.7, 0.45), (0.0, -1.02, 0.72), (0.0, -1.2, 1.05), (0.0, -1.2, 1.4), (0.0, -1.1, 1.72),
            (0.0, -1.1, 1.95), (0.0, -1.22, 2.1)]
    sweep(mb, neck, [0.24, 0.2, 0.16, 0.14, 0.13, 0.135, 0.13], W_, seg=8, cap1=False)
    NK.blob(mb, (0.0, -1.3, 2.12), 0.2, W_, seg=8, rings=5, sz=0.85, sy=1.35, jit=0.0, seed=6)
    NK.tube(mb, (0.0, -1.5, 2.1), (0.0, -1.8, 2.03), 0.085, "M_Hazard_Orange", seg=6, cap0=True, r1=0.015)
    NK.tube(mb, (0.0, -1.47, 2.1), (0.0, -1.53, 2.1), 0.1, "M_Trim_Dark", seg=6, cap0=True, cap1=True)
    for sx in (-1, 1):
        NK.blob(mb, (sx * 0.15, -1.38, 2.18), 0.035, "M_Trim_Dark", seg=6, rings=3)
    return mb


def gate_pair_mb(gap=3.4, slim=False):
    """Two brick gate pillars with stone caps + lanterns, centred on x = +-(gap/2 + 0.35). Origin = gate
    centre on the ground."""
    mb = MeshBuilder()
    k = 0.62 if slim else 1.0
    H = 1.7 if slim else 1.95
    for sx in (-1, 1):
        x = sx * (gap / 2 + 0.42 * k)
        NK.bbox(mb, x - 0.42 * k, -0.42 * k, -0.25, x + 0.42 * k, 0.42 * k, 0.28, STONE, bevel=0.03)
        NK.bbox(mb, x - 0.33 * k, -0.33 * k, 0.28, x + 0.33 * k, 0.33 * k, H, "M_Wall_Brick", bevel=0.02,
                skip=("-z",))
        NK.bbox(mb, x - 0.43 * k, -0.43 * k, H, x + 0.43 * k, 0.43 * k, H + 0.17, STONE, bevel=0.03)
        if slim:
            NK.lathe(mb, [(0.0, H + 0.17), (0.12, H + 0.17), (0.17, H + 0.3), (0.12, H + 0.42), (0.0, H + 0.46)],
                     STONE, seg=8, cx=x)
            continue
        NK.bbox(mb, x - 0.2, -0.2, H + 0.17, x + 0.2, 0.2, H + 0.25, "M_Metal_Dark")
        NK.bbox(mb, x - 0.14, -0.14, H + 0.25, x + 0.14, 0.14, H + 0.55, "M_Light_Emit", skip=("-z", "+z"))
        for cx in (-0.14, 0.14):
            for cy in (-0.14, 0.14):
                NK.bbox(mb, x + cx - 0.025, cy - 0.025, H + 0.25, x + cx + 0.025, cy + 0.025, H + 0.55,
                        "M_Metal_Dark", skip=("-z", "+z"))
        NK.lathe(mb, [(0.0, H + 0.55), (NK.sq(0.17), H + 0.55), (NK.sq(0.19), H + 0.59), (0.0, H + 0.75)],
                 "M_Metal_Dark", seg=4, cx=x, phase=math.pi / 4)
    return mb


def marker_post_mb(band="M_Awning_Blue", h=1.05):
    """Trail marker: chunky timber post with a coloured band and a pyramid cap (origin at ground)."""
    mb = MeshBuilder()
    NK.bbox(mb, -0.08, -0.08, -0.35, 0.08, 0.08, h, WOOD_D, skip=("-z",), bevel=0.015)
    NK.bbox(mb, -0.095, -0.095, h - 0.32, 0.095, 0.095, h - 0.16, band)
    NK.lathe(mb, [(NK.sq(0.1), h), (NK.sq(0.1), h + 0.03), (0.0, h + 0.14)], WOOD_D, seg=4, phase=math.pi / 4)
    # little arrow plate on the front
    NK.xz_prism(mb, [(-0.06, h - 0.55), (0.03, h - 0.55), (0.03, h - 0.6), (0.09, h - 0.5), (0.03, h - 0.4),
                     (0.03, h - 0.45), (-0.06, h - 0.45)], -0.1, -0.08, band)
    return mb


def notice_board_mb(face_notes=("M_Sign_Face", "M_Awning_Yellow", "M_Wall_Sky", "M_Wall_Rose"),
                    roof="M_Roof_Green", w=1.8):
    """Roofed timber notice board facing -Y (origin at the ground, centre)."""
    mb = MeshBuilder()
    hw = w / 2
    for sx in (-1, 1):
        NK.bbox(mb, sx * hw - 0.08, -0.08, -0.3, sx * hw + 0.08, 0.08, 2.35, WOOD_D, skip=("-z",), bevel=0.015)
    NK.bbox(mb, -hw + 0.08, -0.05, 0.85, hw - 0.08, 0.05, 1.95, "M_Crate")
    NK.bbox(mb, -hw + 0.08, -0.09, 0.8, hw - 0.08, 0.06, 0.88, WOOD_D)
    NK.bbox(mb, -hw + 0.08, -0.09, 1.92, hw - 0.08, 0.06, 2.0, WOOD_D)
    rnd = random.Random(7)
    x = -hw + 0.25
    for i, m in enumerate(face_notes):
        ww = rnd.uniform(0.28, 0.4)
        hh = rnd.uniform(0.3, 0.45)
        z0 = rnd.uniform(1.0, 1.85 - hh)
        NK.bbox(mb, x, -0.075, z0, x + ww, -0.05, z0 + hh, m)
        x += ww + 0.1
    # roof: two slabs + ridge
    for s in (-1, 1):
        a = Vector((0.0, 0.0, 2.62))
        b = Vector((0.0, s * 0.66, 2.26))
        nrm = Vector((0.0, s * 0.36, 0.66)).normalized()
        NK.beam(mb, a + nrm * 0.035, b + nrm * 0.035, w + 0.5, 0.07, roof, up=tuple(nrm))
    NK.bbox(mb, -hw - 0.25, -0.06, 2.6, hw + 0.25, 0.06, 2.68, WOOD_D)
    return mb


def coin_telescope_mb(body="M_Awning_Teal"):
    """Coin-operated telescope looking toward -Y, eyepiece at +Y (origin at the floor)."""
    mb = MeshBuilder()
    md = "M_Metal_Dark"
    NK.lathe(mb, [(0.22, 0.0), (0.22, 0.05), (0.1, 0.12), (0.06, 0.2), (0.06, 0.95), (0.09, 1.0), (0.0, 1.0)],
             md, seg=8)
    NK.bbox(mb, -0.13, -0.08, 0.98, 0.13, 0.08, 1.1, md)
    for sx in (-1, 1):
        NK.bbox(mb, sx * 0.13 - 0.03, -0.05, 1.05, sx * 0.13 + 0.03, 0.05, 1.32, md)
    tilt = math.radians(8)
    a = Vector((0.0, 0.28, 1.22 - 0.28 * math.tan(tilt)))
    b = Vector((0.0, -0.36, 1.22 + 0.36 * math.tan(tilt)))
    NK.tube(mb, a, b, 0.105, body, seg=10, cap0=True, cap1=True, r1=0.125)
    NK.tube(mb, b, b + (b - a).normalized() * 0.06, 0.135, md, seg=10, cap0=True, cap1=True)
    for sx in (-1, 1):
        e0 = a + Vector((sx * 0.05, 0.0, 0.0))
        NK.tube(mb, e0, e0 + Vector((0.0, 0.1, -0.01)), 0.035, md, seg=6, cap0=False, cap1=True)
    NK.bbox(mb, -0.07, 0.06, 0.62, 0.07, 0.16, 0.86, "M_Zoo_Accent")
    return mb


def flagpole_mb(h=5.0, flag="M_Awning_Yellow"):
    mb = MeshBuilder()
    NK.lathe(mb, [(0.06, -0.3), (0.06, h), (0.09, h + 0.04), (0.0, h + 0.14)], "M_Metal", seg=8)
    # pennant (closed thin wedge) toward +X
    pts = [(0.06, h - 1.0), (1.4, h - 0.72), (0.06, h - 0.38)]
    NK.xz_prism(mb, pts, -0.02, 0.02, flag)
    return mb


# ------------------------------------------------------------------------------ nature bits (world, merged)
def reed_clump(mb, x, y, z, rng, h=1.6, n=8, spread=0.38, cattail=0.6):
    """Reed clump = 2-3 crossed blade CARDS (n >= 8 -> 3 cards) through the clump centre. Each card is a comb of
    broad blade triangles fanning outward, built double-sided (front + back face 12 mm apart, each facing its
    own side) so it survives Unity's backface culling. ~20-26 tris + an optional cattail (stem + seed head,
    14 tris); the old 3-sided spikes cost ~100 tris per clump and were thin enough to shimmer without TAA."""
    mats = ("M_Foliage_Dark", "M_Foliage_Dark", "M_Foliage", "M_Grass_Dry")
    ncard = 3 if n >= 8 else 2
    nb = max(3, min(4, int(round(n / ncard))))
    ph = rng.uniform(0, math.pi)
    for c in range(ncard):
        a = ph + math.pi * c / ncard + rng.uniform(-0.15, 0.15)
        u = Vector((math.cos(a), math.sin(a), 0.0))            # along the card
        nrm = Vector((-u.y, u.x, 0.0))                          # card normal
        off = nrm * rng.uniform(-0.07, 0.07) + u * rng.uniform(-0.06, 0.06)
        half = spread * rng.uniform(0.85, 1.1)
        e = nrm * 0.006
        for b in range(nb):
            t = -1.0 + 2.0 * (b + 0.5) / nb                     # -1..1 along the card
            cx = t * half * 0.7
            w = rng.uniform(0.15, 0.21)
            hh = h * rng.uniform(0.6, 1.05)
            lean = t * hh * rng.uniform(0.14, 0.26) + rng.uniform(-0.05, 0.05)
            base = Vector((x, y, z - 0.15)) + off
            p0 = base + u * (cx - w / 2)
            p1 = base + u * (cx + w / 2)
            tip = Vector((x, y, z + hh)) + off + u * (cx + lean) + nrm * rng.uniform(-0.12, 0.12)
            m = rng.choice(mats)
            mb.face([p0 - e, p1 - e, tip - e], m)               # faces -nrm
            mb.face([p1 + e, p0 + e, tip + e], m)               # faces +nrm
    if rng.random() < cattail:
        bx, by = x + rng.uniform(-0.12, 0.12), y + rng.uniform(-0.12, 0.12)
        hh = h * rng.uniform(0.95, 1.15)
        top = Vector((bx + rng.uniform(-0.1, 0.1), by + rng.uniform(-0.1, 0.1), z + hh))
        NK.tube(mb, (bx, by, z - 0.15), top, 0.024, "M_Foliage_Dark", seg=3, cap1=False)
        NK.gem(mb, (top.x, top.y, top.z + 0.12), 0.065, 0.2, "M_Bark", seg=4, phase=rng.uniform(0, 1.5))


def log_mb(mb, a, b, r, rng, stubs=True):
    """Fallen log from a to b (3D), bark sides, light cut ends, a couple of branch stubs."""
    a, b = Vector(a), Vector(b)
    d = b - a
    sub = MeshBuilder()
    sub.cylinder(0.0, 0.0, 0.0, d.length, r, BARK, seg=8, cap_top=True, cap_bottom=True, mat_cap=WOOD,
                 r_top=r * 0.88)
    M = Matrix.Translation(a) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    mb.extend(sub, M)
    if stubs:
        u = d.normalized()
        side = u.cross(Vector((0.0, 0.0, 1.0)))
        if side.length < 1e-6:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        for t, s in ((0.35, 1), (0.7, -1)):
            p0 = a + d * t
            q = p0 + side * s * (r + 0.35) + Vector((0, 0, r * 0.6)) + u * 0.2
            NK.tube(mb, p0, q, r * 0.32, BARK, seg=5, cap0=False, cap1=True, r1=r * 0.22)


def stump_mb(mb, x, y, z, r=0.35, h=0.55, chewed=False):
    if chewed:
        prof = [(r * 1.35, z - 0.08), (r, z + 0.12), (r * 0.95, z + 0.3), (r * 0.45, z + 0.46), (r * 0.42, z + 0.5),
                (r * 0.85, z + 0.62), (r * 0.5, z + 0.8), (0.0, z + 0.9)]
        mats = [BARK, BARK, WOOD, WOOD, WOOD, WOOD, WOOD]
    else:
        prof = [(r * 1.4, z - 0.08), (r, z + 0.14), (r * 0.95, z + h), (r * 0.82, z + h + 0.03), (0.0, z + h + 0.03)]
        mats = [BARK, BARK, WOOD, WOOD]
    NK.lathe(mb, prof, BARK, seg=8, cx=x, cy=y, mats=mats)


def beaver_lodge_mb(rng, R=2.4, H=1.5):
    """Dome of mud + sticks. Origin = centre at the waterline."""
    mb = MeshBuilder()
    NK.blob(mb, (0.0, 0.0, -0.4), R, "M_Bark", seg=12, rings=6, sz=(H + 0.4) / R, sz_bot=0.2, jit=0.08, seed=11)
    NK.blob(mb, (0.7, -0.5, -0.2), R * 0.55, "M_Dirt", seg=8, rings=5, sz=0.7, jit=0.1, seed=12)
    NK.blob(mb, (-0.8, 0.6, -0.3), R * 0.62, "M_Bark", seg=8, rings=5, sz=0.95, jit=0.1, seed=13)
    for k in range(44):
        a = rng.uniform(0, TAU)
        el = rng.uniform(0.15, 1.2)
        rr = R * math.cos(el) * 0.92
        zz = -0.4 + (H + 0.4) * math.sin(el) * 0.92
        p = Vector((rr * math.cos(a), rr * math.sin(a), zz))
        t = Vector((-math.sin(a), math.cos(a), rng.uniform(-0.6, 0.6))).normalized()
        L = rng.uniform(0.9, 1.8)
        NK.beam(mb, p - t * L / 2, p + t * L / 2, 0.09, 0.09, rng.choice([WOOD_D, BARK, "M_Fence_Wood"]))
    NK.floor_clamp(mb, -0.45)
    return mb


# ------------------------------------------------------------------------------ playground
def play_tower_mb():
    """Play tower: 2 x 2 m platform at 1.5 m, pyramid roof, slide toward -Y, ladder at +Y."""
    mb = MeshBuilder()
    P, top = 1.0, 1.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            NK.bbox(mb, sx * P - 0.08, sy * P - 0.08, -0.2, sx * P + 0.08, sy * P + 0.08, 2.7, WOOD, bevel=0.02,
                    skip=("-z",))
    NK.bbox(mb, -P, -P, top - 0.12, P, P, top, WOOD_D, bevel=0.02)
    # side panels (+X / -X) and half panels at the back
    for sx in (-1, 1):
        NK.bbox(mb, sx * P - 0.03, -P + 0.1, top + 0.15, sx * P + 0.03, P - 0.1, top + 0.85, "M_Awning_Blue",
                bevel=0.015)
    for sx in (-1, 1):
        NK.bbox(mb, sx * 0.62 - 0.32, P - 0.03, top + 0.15, sx * 0.62 + 0.32, P + 0.03, top + 0.85, "M_Awning_Blue",
                bevel=0.015)
    NK.bbox(mb, -P, -P - 0.04, top + 0.82, P, -P + 0.04, top + 0.92, WOOD)
    # roof
    NK.lathe(mb, [(0.0, 2.62), (NK.sq(1.25), 2.62), (NK.sq(1.28), 2.7), (0.0, 3.45)], "M_Awning_Red", seg=4,
             phase=math.pi / 4)
    NK.blob(mb, (0.0, 0.0, 3.5), 0.12, "M_Awning_Yellow", seg=8, rings=4)
    # slide toward -Y: inclined chute (bottom + 2 cheeks) + run-out
    y0, y1, y2 = -P, -P - 2.6, -P - 3.3
    z0, z1 = top, 0.32
    sl = "M_Awning_Yellow"
    for (ya, za, yb, zb) in ((y0, z0, y1, z1), (y1, z1, y2, z1 - 0.02)):
        NK.beam(mb, (0.0, ya, za - 0.05), (0.0, yb, zb - 0.05), 0.62, 0.06, sl)
        for sx in (-1, 1):
            NK.beam(mb, (sx * 0.33, ya, za + 0.08), (sx * 0.33, yb, zb + 0.08), 0.06, 0.3, sl)
    for sx in (-1, 1):
        NK.bbox(mb, sx * 0.3 - 0.05, y2 + 0.1, 0.0, sx * 0.3 + 0.05, y2 + 0.2, z1 - 0.05, "M_Metal")
    # ladder at +Y
    for sx in (-1, 1):
        NK.beam(mb, (sx * 0.35, P + 0.75, 0.0), (sx * 0.35, P + 0.02, top + 0.9), 0.07, 0.07, WOOD,
                up=(1.0, 0.0, 0.0))
    for k in range(1, 6):
        t = k / 6.0
        yy = P + 0.75 - 0.73 * t * (top + 0.9) / (top + 0.9)
        zz = (top + 0.9) * t
        if zz > top + 0.1:
            break
        NK.bbox(mb, -0.35, yy - 0.04, zz - 0.03, 0.35, yy + 0.04, zz + 0.03, "M_Metal")
    NK.floor_clamp(mb, -0.2)
    return mb


def climb_arch_mb(r=1.25, gap=1.0, mat="M_Awning_Green"):
    """Arched climbing ladder (monkey-bar arch) spanning X, rungs along Y."""
    mb = MeshBuilder()
    n = 8
    pts = [Vector((-r * math.cos(math.pi * k / n), 0.0, r * 0.95 * math.sin(math.pi * k / n))) for k in range(n + 1)]
    for sy in (-gap / 2, gap / 2):
        off = Vector((0.0, sy, 0.0))
        for a, b in zip(pts, pts[1:]):
            NK.tube(mb, a + off, b + off, 0.05, mat, seg=6, cap0=False, cap1=True)
        for p in (pts[0], pts[-1]):
            NK.lathe(mb, [(0.09, -0.1), (0.09, 0.08), (0.0, 0.08)], "M_Metal_Dark", seg=6, cx=p.x, cy=sy)
    for k in range(1, n):
        p = pts[k]
        NK.tube(mb, (p.x, -gap / 2, p.z), (p.x, gap / 2, p.z), 0.035, "M_Metal", seg=6, cap0=True, cap1=True)
    return mb


def seesaw_mb():
    mb = MeshBuilder()
    NK.xz_prism(mb, [(-0.25, 0.0), (0.25, 0.0), (0.08, 0.42), (-0.08, 0.42)], -0.25, 0.25, "M_Metal_Dark")
    tilt = math.radians(11)
    L = 3.0
    a = Vector((-L / 2 * math.cos(tilt), 0.0, 0.5 - L / 2 * math.sin(tilt)))
    b = Vector((L / 2 * math.cos(tilt), 0.0, 0.5 + L / 2 * math.sin(tilt)))
    NK.beam(mb, a, b, 0.3, 0.08, "M_Hazard_Orange", up=(0.0, 0.0, 1.0), bevel=0.015)
    for s, p in ((-1, a), (1, b)):
        q = p + (b - a).normalized() * (-s * 0.35)
        NK.tube(mb, q, q + Vector((0, 0, 0.32)), 0.03, "M_Metal", seg=6, cap1=False)
        NK.tube(mb, q + Vector((0, -0.14, 0.32)), q + Vector((0, 0.14, 0.32)), 0.03, "M_Awning_Blue", seg=6,
                cap0=True)
    NK.floor_clamp(mb, 0.0)
    return mb


# ------------------------------------------------------------------------------ allotments
def raised_bed_mb(crop, rng, L=3.0, D=1.2, H=0.38):
    """Timber raised bed (long axis X) with a crop. Origin = bottom centre. Lean (polish pass): ~150-250 tris,
    and _gardens shares one mesh per crop between the beds (shared_obj)."""
    mb = MeshBuilder()
    t = 0.08
    hx, hy = L / 2, D / 2
    # frame boards (4 closed boxes, chunky dark top rim) + soil
    sk = ("-z",)
    NK.bbox(mb, -hx, -hy, -0.05, hx, -hy + t, H, WOOD, skip=sk)
    NK.bbox(mb, -hx, hy - t, -0.05, hx, hy, H, WOOD, skip=sk)
    NK.bbox(mb, -hx, -hy + t, -0.05, -hx + t, hy - t, H, WOOD_D, skip=sk)
    NK.bbox(mb, hx - t, -hy + t, -0.05, hx, hy - t, H, WOOD_D, skip=sk)
    zs = H - 0.07
    mb.face([(-hx + t, -hy + t, zs), (hx - t, -hy + t, zs), (hx - t, hy - t, zs), (-hx + t, hy - t, zs)], "M_Dirt")
    xs = [-hx + 0.4 + i * (L - 0.8) / 3 for i in range(4)]
    if crop == "lettuce":
        for row in (-0.25, 0.25):
            for x in xs:
                NK.blob(mb, (x + row * 0.3, row, zs + 0.06), 0.2, rng.choice(["M_Foliage_Light", "M_Foliage"]), seg=5,
                        rings=3, sz=0.7, jit=0.12, seed=rng.randint(0, 999), floor=zs)
    elif crop == "cabbage":
        for row in (-0.24, 0.24):
            for x in (-0.85, 0.05, 0.95):
                NK.blob(mb, (x + row * 0.4, row, zs + 0.12), 0.26, "M_Foliage_Dark", seg=6, rings=3, sz=0.8, jit=0.1,
                        seed=rng.randint(0, 999), floor=zs)
                NK.gem(mb, (x + row * 0.4, row, zs + 0.3), 0.13, 0.07, "M_Foliage_Light", seg=4)
    elif crop == "tomato":
        for x in (-0.9, 0.0, 0.9):
            NK.bbox(mb, x - 0.025, -0.025, zs, x + 0.025, 0.025, zs + 1.25, WOOD, skip=sk)
            NK.blob(mb, (x, 0.0, zs + 0.6), 0.3, "M_Foliage_Dark", seg=6, rings=4, sz=1.5, jit=0.12,
                    seed=rng.randint(0, 999), floor=zs)
            for k in range(3):
                a = rng.uniform(0, TAU)
                NK.gem(mb, (x + 0.25 * math.cos(a), 0.25 * math.sin(a), zs + rng.uniform(0.35, 0.9)), 0.08, 0.075,
                       "M_Door_Red", seg=4)
    elif crop == "pumpkin":
        NK.blob(mb, (0.0, 0.0, zs + 0.05), 0.55, "M_Foliage", seg=7, rings=3, sz=0.25, sx=2.2, sy=0.8, jit=0.15,
                seed=rng.randint(0, 999), floor=zs)
        for x in (-0.95, -0.15, 0.7):
            NK.blob(mb, (x, rng.uniform(-0.2, 0.2), zs + 0.2), 0.24, "M_Hazard_Orange", seg=7, rings=4, sz=0.75,
                    jit=0.04, seed=rng.randint(0, 999), floor=zs)
            NK.tube(mb, (x, 0.0, zs + 0.36), (x + 0.03, 0.0, zs + 0.46), 0.03, "M_Bark", seg=4)
    else:  # carrots / onions: rows of feathery tufts
        for row in (-0.3, 0.0, 0.3):
            for x in [-hx + 0.3 + i * 0.4 for i in range(int((L - 0.6) / 0.4) + 1)]:
                NK.gem(mb, (x + row * 0.3, row, zs + 0.12), 0.09, 0.14, "M_Foliage_Light", seg=4,
                       phase=rng.uniform(0, 3))
    return mb


def bean_row_mb(rng, L=3.2, h=1.85):
    """Bean row: poles + top rail along X with climbing foliage (a screen animals hide behind). Polish pass: the
    23 small leaf blobs are merged into two lumpy leaf clusters per pole span + a spill-over cap (~500 tris)."""
    mb = MeshBuilder()
    n = 5
    for i in range(n):
        x = -L / 2 + L * i / (n - 1)
        NK.bbox(mb, x - 0.03, -0.03, -0.1, x + 0.03, 0.03, h, WOOD, skip=("-z",))
    NK.bbox(mb, -L / 2 - 0.05, -0.03, h - 0.06, L / 2 + 0.05, 0.03, h, WOOD)
    for i in range(n - 1):
        x = -L / 2 + L * (i + 0.5) / (n - 1)
        sh = 0.12 if i % 2 else -0.12
        NK.blob(mb, (x + sh, 0.0, 0.55), 0.43, "M_Foliage_Dark", seg=6, rings=4, sz=1.15, sx=1.0, sy=0.56, jit=0.2,
                seed=rng.randint(0, 999), floor=0.0)
        NK.blob(mb, (x - sh, 0.0, 1.22), 0.4, "M_Foliage", seg=6, rings=4, sz=1.05, sx=1.05, sy=0.56, jit=0.2,
                seed=rng.randint(0, 999))
        NK.blob(mb, (x + rng.uniform(-0.1, 0.1), 0.0, h - 0.08), 0.28, "M_Foliage", seg=6, rings=3, sz=0.75, sx=1.35,
                sy=0.95, jit=0.15, seed=rng.randint(0, 999))
        for k in range(2):
            NK.gem(mb, (x + rng.uniform(-0.25, 0.25), rng.choice([-0.24, 0.24]), rng.uniform(0.6, 1.5)), 0.05, 0.12,
                   "M_Foliage_Light", seg=4)
    return mb


def lily_pads(mb, pond, rng, n=18, clusters=((300, 3.5), (40, 4.5), (250, 5.0))):
    """Flat lily pads (+ a few pink flowers) floating on the pond water, in loose clusters."""
    wz = -0.4 + 0.012
    for (a_deg, inset) in clusters:
        for k in range(n // len(clusters)):
            a = math.radians(a_deg + rng.uniform(-9, 9))
            p = pond.at(a, inset + rng.uniform(-1.2, 1.6)) - pond.c
            r = rng.uniform(0.28, 0.5)
            notch = rng.uniform(0, TAU)
            ring = []
            for j in range(9):
                t = notch + 0.5 + (TAU - 1.0) * j / 8
                ring.append(Vector((p.x + r * math.cos(t), p.y + r * math.sin(t), wz)))
            c = Vector((p.x, p.y, wz))
            for j in range(8):
                mb.face([c, ring[j], ring[j + 1]], "M_Foliage_Light" if k % 3 else "M_Foliage")
            if rng.random() < 0.35:
                NK.gem(mb, (p.x + 0.05, p.y, wz + 0.07), 0.11, 0.07, "M_Foliage_Blossom", seg=5,
                       phase=rng.uniform(0, 3))


def bean_teepee_mb(rng, r=0.55, h=2.1):
    """Bean teepee: 4 poles, two merged leaf clusters per pole (~230 tris)."""
    mb = MeshBuilder()
    for k in range(4):
        a = TAU * k / 4 + 0.4
        p = (r * math.cos(a), r * math.sin(a), 0.0)
        NK.tube(mb, p, (0.0, 0.0, h), 0.025, WOOD, seg=4, cap1=False)
        for t, rr in ((0.33, 0.27), (0.68, 0.21)):
            q = Vector(p).lerp(Vector((0.0, 0.0, h)), t)
            NK.blob(mb, tuple(q), rr, "M_Foliage" if k % 2 else "M_Foliage_Dark", seg=6, rings=3, sz=1.5, jit=0.15,
                    seed=rng.randint(0, 999))
    return mb


def scarecrow_mb():
    mb = MeshBuilder()
    NK.bbox(mb, -0.05, -0.05, -0.3, 0.05, 0.05, 1.95, WOOD_D)
    NK.bbox(mb, -0.85, -0.04, 1.42, 0.85, 0.04, 1.5, WOOD_D)
    NK.rbox(mb, (0.0, 0.0, 1.25), (0.62, 0.3, 0.62), "M_Awning_Blue", bevel=0.04)
    for sx in (-1, 1):
        NK.rbox(mb, (sx * 0.52, 0.0, 1.43), (0.48, 0.22, 0.22), "M_Awning_Red", bevel=0.03)
        NK.gem(mb, (sx * 0.85, 0.0, 1.43), 0.12, 0.1, "M_Awning_Yellow", seg=5)
    NK.rbox(mb, (0.0, 0.0, 0.88), (0.5, 0.26, 0.2), "M_Door_Navy", bevel=0.03)
    NK.blob(mb, (0.0, 0.0, 1.78), 0.2, "M_Sand", seg=8, rings=5, sz=1.05)
    NK.lathe(mb, [(0.42, 1.9), (0.42, 1.93), (0.2, 1.95), (0.17, 2.12), (0.0, 2.15)], "M_Wall_Butter", seg=10)
    for sx in (-1, 1):
        NK.bbox(mb, sx * 0.07 - 0.025, -0.2, 1.8, sx * 0.07 + 0.025, -0.17, 1.84, "M_Trim_Dark")
    return mb


def sunflower_mb(rng, h=1.7):
    mb = MeshBuilder()
    lean = (rng.uniform(-0.08, 0.08), rng.uniform(-0.15, 0.0))
    top = Vector((lean[0], lean[1], h))
    NK.tube(mb, (0.0, 0.0, -0.05), top, 0.03, "M_Foliage_Dark", seg=4, cap1=False)
    NK.blob(mb, (0.14, 0.0, 0.7), 0.13, "M_Foliage", seg=5, rings=3, sz=0.35, sx=1.5)
    n = Vector((0.0, -1.0, 0.35)).normalized()
    M = Matrix.Translation(top) @ n.to_track_quat("Z", "Y").to_matrix().to_4x4()
    head = MeshBuilder()
    NK.lathe(head, [(0.0, -0.04), (0.3, -0.02), (0.31, 0.02), (0.12, 0.05), (0.0, 0.06)], "M_Awning_Yellow", seg=8,
             mats=["M_Awning_Yellow", "M_Awning_Yellow", "M_Awning_Yellow", "M_Bark"], wave={2: (0.12, 0.0)})
    mb.extend(head, M)
    return mb


def rose_arch_mb(w=2.0, h=2.4):
    """Garden gate arch with climbing roses, spanning X (opening along Y). Polish pass: 4-segment arch, 7 merged
    rose clusters (~500 tris)."""
    mb = MeshBuilder()
    hw = w / 2
    for sx in (-1, 1):
        for sy in (-0.25, 0.25):
            NK.bbox(mb, sx * hw - 0.05, sy - 0.05, -0.3, sx * hw + 0.05, sy + 0.05, h, "M_Trim_White", skip=("-z",))
    n = 4
    pts = [Vector((-hw * math.cos(math.pi * k / n), 0.0, h + 0.55 * math.sin(math.pi * k / n))) for k in range(n + 1)]
    for sy in (-0.25, 0.25):
        for a, b in zip(pts, pts[1:]):
            NK.beam(mb, a + Vector((0, sy, 0)), b + Vector((0, sy, 0)), 0.07, 0.07, "M_Trim_White")
    rnd = random.Random(31)
    spots = [Vector((-hw, 0.0, 0.85)), Vector((-hw, 0.0, 1.75)), pts[1], pts[2], pts[3], Vector((hw, 0.0, 1.65)),
             Vector((hw, 0.0, 0.7))]
    for k, p in enumerate(spots):
        lens = 1.35 if k in (0, 1, 5, 6) else 1.0         # posts: taller clusters climbing the post
        NK.blob(mb, (p.x, rnd.uniform(-0.08, 0.08), p.z), rnd.uniform(0.33, 0.42), "M_Foliage_Dark", seg=6, rings=4,
                sz=lens, jit=0.1, seed=rnd.randint(0, 999))
        for j in range(2):
            a = rnd.uniform(0, TAU)
            NK.gem(mb, (p.x + 0.34 * math.cos(a), 0.34 * math.sin(a), p.z + rnd.uniform(-0.1, 0.2)), 0.09, 0.07,
                   rnd.choice(["M_Foliage_Blossom", "M_Wall_Rose", "M_Door_Red"]), seg=4)
    return mb


# =============================================================================== placement helpers
def soft_pad(S, name, c, u, W, D, sub, cs=1.2, edge=0.22, lift=0.1, top="M_Sand", rim=WOOD):
    """Rounded soft-fall pad (sand) with a timber edge, levelled at the highest ground + lift.
    Returns (z of the sand surface, object)."""
    c, u = V2(c), V2(u).normalized()
    n = Vector((-u.y, u.x))
    corners = [c + u * (a * W / 2) + n * (b * D / 2) for a in (-1, 1) for b in (-1, 1)]
    zpad = max(S.ground_z(q.x, q.y) for q in corners + [c]) + lift
    rr = []
    for (cu, cv, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        cc = u * (cu * (W / 2 - cs)) + n * (cv * (D / 2 - cs))
        for k in range(5):
            a = math.radians(a0 + 90 * k / 4)
            rr.append(cc + u * (cs * math.cos(a)) + n * (cs * math.sin(a)))
    P = G.ensure_ccw(rr)
    inner = [p * ((p.length - edge) / p.length) for p in P]
    Pc = [(p.x, p.y) for p in P]
    Ic = [(p.x, p.y) for p in inner]
    pad = MeshBuilder()
    pad.tri_fill([Ic], zpad - 0.03, top)
    pad.wall(Pc, GZ - 0.25, zpad, rim, closed=True)
    pad.tri_fill([Pc, Ic], zpad, rim)
    pad.wall(list(reversed(Ic)), zpad - 0.03, zpad, rim, closed=True)
    o = S.mesh(name, pad, sub=sub, loc=(c.x, c.y, 0.0))
    return zpad - 0.03, o


class Planner:
    """Per-area placement context: occupancy, footpaths, ponds, keep-in / keep-out polygons."""

    def __init__(self, S, keep_in=None, avoid_polys=(), extra_paths=(), avoid_pts=()):
        self.S = S
        self.rng = S.rng
        self.occ = Occ()
        self.paths = paths_hash(S.layout, extra_paths)
        self.keep_in = [G.V(p) for p in keep_in] if keep_in else None
        self.avoid_polys = [[G.V(p) for p in poly] for poly in avoid_polys]
        self.ponds = [Pond(pd) for pd in getattr(S.layout, "PONDS", [])]
        self.avoid_pts = list(avoid_pts)        # [(point, radius)]
        for (q, r) in self.avoid_pts:
            self.occ.add(q, r)
        # cul-de-sac bulbs are NOT covered by S.clear_of_roads (edge hash = half width + sidewalk only)
        self.bulbs = [(G.V(nd["pos"]), C.CULDESAC_R + 2.6) for nd in S.layout.NODES.values()
                      if isinstance(nd, dict) and nd.get("culdesac")]
        self.world = getattr(S, "world", None)
        self.trees = []                         # trunk positions of every plan.tree() (forest floor, understory)
        self._foreign_obstacles()

    def _foreign_obstacles(self):
        """Objects other landmark builders already placed (riverwalk promenade lamps, neighbours' props...)
        become occupancy circles, so trees / benches never stand inside them."""
        import bpy
        root = bpy.data.collections.get("05_Landmarks")
        if root is None:
            return
        own = bpy.data.collections.get(self.S.coll.split("/")[-1])
        own_objs = set(own.all_objects) if own else set()
        x0, y0, x1, y1 = G.bbox(self.keep_in) if self.keep_in else G.bbox(self.S.poly or [Vector((0, 0))])
        pad = 30.0
        for o in root.all_objects:
            if o in own_objs or o.type != "MESH":
                continue
            m = o.matrix_world.translation
            if not (x0 - pad < m.x < x1 + pad and y0 - pad < m.y < y1 + pad):
                continue
            dims = o.dimensions
            ext = max(dims.x, dims.y)
            if dims.z < 0.25 or ext > 14.0:
                continue           # paving, paths, merged ground pieces
            self.occ.add((m.x, m.y), max(0.4, 0.45 * ext))

    def road_ok(self, p, extra=0.3):
        p = V2(p)
        return self.S.clear_of_roads(p, extra=extra) and not any((p - c).length < rb + extra for c, rb in self.bulbs)

    def ok(self, p, r=0.5, road=1.0, path=0.6, pond=1.0, keep_in=True):
        p = V2(p)
        if keep_in and self.keep_in is not None and not G.point_in_poly(p, self.keep_in):
            return False
        if any(G.point_in_poly(p, poly) for poly in self.avoid_polys):
            return False
        if road is not None and not self.S.clear_of_roads(p, extra=road):
            return False
        if road is not None and any((p - c).length < rb + road for c, rb in self.bulbs):
            return False
        if self.world is not None:
            h = 2 * min(r, 1.5) + 0.4          # trunk + lower crown must stay out of building lots / yards
            if not self.world.lot_free(G.rect_corners(p, (0, -1), h, h)):
                return False
        if path is not None and self.paths.blocked(p, extra=path + r * 0.5):
            return False
        if pond is not None:
            for pd in self.ponds:
                if pd.depth_in(p) > -pond - r * 0.3:
                    return False
        return self.occ.free(p, r)

    def tree(self, p, piece=None, foliage=None, scale=None, sub="Trees", r=2.2, mix=None, fol_mix=None):
        S, rng = self.S, self.rng
        piece = piece or wchoice(rng, mix or [("Tree_Round_A", 4), ("Tree_Round_B", 3), ("Tree_Cone", 2)])
        foliage = foliage or wchoice(rng, fol_mix or [("M_Foliage", 5), ("M_Foliage_Dark", 2),
                                                       ("M_Foliage_Light", 2)])
        if piece == "Tree_Cone" and foliage in ("M_Foliage_Autumn", "M_Foliage_Blossom"):
            foliage = "M_Foliage_Dark"
        s = scale or rng.uniform(0.9, 1.25)
        z = zmin(S, p, 0.35) - 0.04
        self.occ.add(p, r * 0.5)
        self.trees.append((float(p[0]), float(p[1])))
        return S.put(piece, p[0], p[1], z, rng.uniform(0, TAU), recolor={"foliage": foliage}, scale=(s, s, s),
                     sub=subc(S, sub))

    def cluster(self, c, radius, n, min_d=4.0, tries=30, **kw):
        out = []
        c = V2(c)
        for _ in range(n):
            for _t in range(tries):
                a = self.rng.uniform(0, TAU)
                rr = radius * math.sqrt(self.rng.random())
                p = c + Vector((math.cos(a), math.sin(a))) * rr
                if not self.ok(p, r=min_d / 2, road=1.5, path=1.4):
                    continue
                self.tree(p, r=min_d, **kw)
                out.append(p)
                break
        return out

    def prop(self, piece, p, rot=0.0, r=0.8, z=None, sub="Props", recolor=None, scale=None, force=False,
             road=0.3, path=None):
        p = V2(p)
        if not force and not self.ok(p, r=r, road=road, path=path, pond=0.3):
            return None
        self.occ.add(p, r)
        zz = zmin(self.S, p, min(r, 0.9)) - 0.02 if z is None else z
        return self.S.put(piece, p.x, p.y, zz, rot, recolor=recolor, scale=scale, sub=subc(self.S, sub))

    def scatter(self, pieces, n, poly, r=1.0, sub="Scatter", scale=(0.9, 1.2), recolor_fn=None, sink=0.04,
                road=1.0, path=0.8, extra_ok=None, tries=40):
        poly = [G.V(q) for q in poly]
        x0, y0, x1, y1 = G.bbox(poly)
        out = []
        for _ in range(n):
            for _t in range(tries):
                p = Vector((self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)))
                if not G.point_in_poly(p, poly):
                    continue
                if extra_ok and not extra_ok(p):
                    continue
                if not self.ok(p, r=r, road=road, path=path):
                    continue
                piece = wchoice(self.rng, pieces) if isinstance(pieces, list) else pieces
                s = self.rng.uniform(*scale)
                z = zmin(self.S, p, 0.5 * s) - sink
                self.occ.add(p, r)
                self.S.put(piece, p.x, p.y, z, self.rng.uniform(0, TAU),
                           recolor=recolor_fn(self.rng) if recolor_fn else None, scale=(s, s, s), sub=subc(self.S, sub))
                out.append(p)
                break
        return out

    def along(self, pl, spacing, offset, fn, s0=4.0, s1=None, side=1, alternate=False):
        """Call fn(point, outward_normal, s) at stations along polyline pl, offset to one side."""
        s1 = pl.length - 4.0 if s1 is None else s1
        s = s0
        k = 0
        while s <= s1:
            t = pl.tangent(s)
            sd = side * (-1 if (alternate and k % 2) else 1)
            n = G.left_normal(t) * sd
            fn(pl.pos(s) + n * offset, n, s)
            s += spacing
            k += 1


def gate_footing_clear(S, c, d, gap, k, extra=0.2):
    """True when both pillar footings (0.84k m square, centred +-(gap/2 + 0.42k) across the path) stand clear
    of the road + sidewalk corridor by *extra* metres (corner kerbs curve in toward the park)."""
    r = Vector((d.y, -d.x))
    for sx in (-1, 1):
        pc = c + r * sx * (gap / 2 + 0.42 * k)
        for a in (-1, 1):
            for b in (-1, 1):
                if not S.clear_of_roads(pc + r * (a * 0.43 * k) + d * (b * 0.43 * k), extra=extra):
                    return False
    return True


def gate_entrance(S, plan, hit, d, sub="Gates", gap=3.4, wings=1, name="Gate", slim=False, extra_back=0.0):
    """Brick gate pillars where a park path meets a sidewalk. hit = sidewalk edge point, d = path direction
    (from the park toward the sidewalk). slim: narrow posts on the thin strip between a path that runs along
    the street and the sidewalk; wings = number of iron fence pieces on each side (following the curb).
    extra_back pulls the pillars further back along the path; on top of that the pair steps back until both
    footings clear the sidewalk corridor (a curved corner kerb otherwise catches the outer pillar)."""
    d = V2(d).normalized()
    k = 0.62 if slim else 1.0
    set_back = ((0.42 * k + 0.12) if slim else 0.95) + extra_back
    c = hit - d * set_back
    for _ in range(25):
        if gate_footing_clear(S, c, d, gap, k, extra=0.1 if slim else 0.2):
            break
        c = c - d * 0.1
        set_back += 0.1
    rot = face_rot(d)
    z = zmin(S, c, gap / 2 + 0.5) - 0.02
    o = obj_at(S, name, gate_pair_mb(gap, slim=slim), c.x, c.y, z, rot, sub=subc(S, sub))
    r = Vector((d.y, -d.x))
    for sx in (-1, 1):
        plan.occ.add(c + r * sx * (gap / 2 + 0.42 * k), 0.7 * k)
    for sx in (-1, 1):
        a = c + r * sx * (gap / 2 + 0.84 * k)
        for i in range(wings):
            # follow the curb: re-project each piece end onto the set-back line from the sidewalk edge
            b = a + r * sx * 3.0
            hb = sidewalk_hit(S, b - d * 3.0, d, max_len=8.0)
            if hb is not None:
                b = hb - d * set_back
            m = (a + b) / 2
            seg = b - a
            ok = seg.length > 2.0 and all(S.clear_of_roads(q, extra=0.12) for q in (a, b, m)) and \
                not plan.paths.blocked(m, extra=0.15)
            if not ok:
                break
            S.put("Fence_Iron_3m", m.x, m.y, zmin(S, m, 1.5) - 0.02, math.atan2(seg.y, seg.x),
                  scale=(seg.length / 3.0, 1.0, 1.0), sub=subc(S, sub))
            plan.occ.add(m, 0.4)
            a = b
    return o


def connector(S, plan, name, start, d, width=3.0, mat="M_Path", sub="Paths", extend=0.6, min_len=1.0):
    """Short path from *start* along d to the sidewalk edge. Returns (hit, length) or (None, 0)."""
    hit = sidewalk_hit(S, start, d)
    if hit is None:
        return None, 0.0
    L = (hit - V2(start)).length
    if L < min_len:
        return hit, L
    end = hit + V2(d).normalized() * extend
    mid = V2(start).lerp(end, 0.5)
    S.path_ribbon(name, [V2(start), mid, end], width=width, mat=mat, sub=subc(S, sub))
    plan.paths.add(V2(start), end, width / 2, payload=name)
    return hit, L


# =============================================================================== CENTRAL PARK (site)
def build(S):
    if S.id == "CentralPark":
        return _central_park(S)
    return "skipped"


def _loop(S):
    for p in S.layout.PATHS:
        if p["id"] == "ParkLoop":
            return p, path_polyline(p, step=0.5)
    return None, None


def _closest_s(pl, q):
    best, bs = 1e9, 0.0
    s = 0.0
    while s <= pl.length:
        d = (pl.pos(s) - q).length
        if d < best:
            best, bs = d, s
        s += 0.5
    return bs, best


def _central_park(S):
    rng = S.rng
    lay = S.layout
    pond = pond_by_id(lay, "SwanPond")
    hill = next((h for h in getattr(lay, "HILLS", []) if h["id"] == "PicnicHill"), None)
    loop_e, loop = _loop(S)
    hide = [(G.V(h["at"]), 2.6) for h in lay.HIDING_SPOTS if G.point_in_poly(G.V(h["at"]), S.poly)]
    plan = Planner(S, avoid_pts=hide)
    report = {}
    objs = []
    # ---------------------------------------------------------------- PicnicHillThicket (hiding spot, ours)
    # hiding_spots.py skips spots inside a dressed site, so the thicket is built here: a horseshoe of dense
    # bushes round a hollow that opens toward the far (west) side, a boulder and two trees on top.
    for (hp, _r) in hide:
        open_dir = Vector((-1.0, 0.15)).normalized()
        k = 0
        for da in (40, 75, 110, 145, 180, 215, 250, 285, 320):
            a = math.atan2(open_dir.y, open_dir.x) + math.radians(da)
            q = hp + Vector((math.cos(a), math.sin(a))) * rng.uniform(1.6, 2.1)
            s_ = rng.uniform(1.0, 1.3)
            S.put("Bush_B" if k % 2 == 0 else "Bush_A", q.x, q.y, zmin(S, q, 0.9) - 0.05, rng.uniform(0, TAU),
                  recolor={"foliage": rng.choice(["M_Foliage_Dark", "M_Foliage_Dark", "M_Hedge"])},
                  scale=(s_, s_, s_), sub=subc(S, "Thicket"))
            k += 1
        q = hp - open_dir * 2.4 + Vector((0.6, 1.2))
        S.put("Rock_B", q.x, q.y, zmin(S, q, 1.0) - 0.15, 0.7, scale=(1.1, 1.1, 1.0), sub=subc(S, "Thicket"))
        for off, pc in (((1.6, -3.4), "Tree_Round_A"), ((2.2, 3.0), "Tree_Cone")):
            q = hp + Vector(off)
            plan.tree(q, piece=pc, foliage="M_Foliage_Dark", scale=1.15, r=3.0)

    # ---------------------------------------------------------------- fountain plaza (SE corner, loop kink)
    FP = Vector((-142.5, -27.5))
    PR = 6.5
    pz = GZ + 0.085
    mb = MeshBuilder()
    seg = 40
    rings = [(0.0, 3.6, "M_Plaza"), (3.6, 4.3, "M_Plaza_Accent"), (4.3, PR - 0.25, "M_Plaza")]
    for r0, r1, m in rings:
        for k in range(seg):
            a0, a1 = TAU * k / seg, TAU * (k + 1) / seg
            c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
            if r0 < 1e-6:
                mb.face([(0, 0, pz), (r1 * c0, r1 * s0, pz), (r1 * c1, r1 * s1, pz)], m)
            else:
                mb.face([(r0 * c0, r0 * s0, pz), (r1 * c0, r1 * s0, pz), (r1 * c1, r1 * s1, pz),
                         (r0 * c1, r0 * s1, pz)], m)
    # curb ring (slightly raised) + skirt
    NK.lathe(mb, [(PR, GZ - 0.2), (PR, pz + 0.05), (PR - 0.25, pz + 0.05), (PR - 0.25, pz)], "M_Curb", seg=seg)
    objs.append(S.mesh("FountainPlaza", mb, sub=subc(S, "Plaza"), loc=(FP.x, FP.y, 0.0)))
    objs[-1].location = (FP.x, FP.y, 0.0)
    objs.append(obj_at(S, "Fountain", fountain_mb(), FP.x, FP.y, pz, 0.0, sub=subc(S, "Plaza"),
                       smooth=(STONE, "M_Plaza_Accent"), angle=40))
    plan.occ.add(FP, PR)
    # path mouths on the plaza rim -> free angular slots for furniture
    mouths = []
    if loop is not None:
        prev = None
        s = 0.0
        while s <= loop.length:
            inside = (loop.pos(s) - FP).length < PR
            if prev is not None and inside != prev:
                d = loop.pos(s) - FP
                mouths.append(math.atan2(d.y, d.x))
            prev = inside
            s += 0.25
    e1_dir = Vector((0.62, -0.785)).normalized()
    mouths.append(math.atan2(e1_dir.y, e1_dir.x))
    report["plaza_mouths_deg"] = [round(math.degrees(a) % 360) for a in mouths]

    def ang_free(a, margin):
        return all(abs((a - m + math.pi) % TAU - math.pi) > margin for m in mouths)

    furn = [("Bench", 5.35, True), ("Lamp_Park", 6.05, False), ("Bench", 5.35, True), ("Flowerbed_2m", 5.2, True),
            ("Bench", 5.35, True), ("Lamp_Park", 6.05, False), ("TrashBin", 5.6, False), ("Bench", 5.35, True),
            ("Flowerbed_2m", 5.2, True), ("Lamp_Park", 6.05, False)]
    slots = [a for a in [math.radians(d) for d in range(0, 360, 6)] if ang_free(a, math.radians(26))]
    # spread the furniture evenly over the free slots
    if slots:
        step = max(1, len(slots) // len(furn))
        for i, (piece, rr, facing) in enumerate(furn):
            idx = (i * step + step // 2) % len(slots)
            a = slots[idx]
            p = FP + Vector((math.cos(a), math.sin(a))) * rr
            inward = (FP - p).normalized()
            rot = face_rot(inward) if facing else face_rot(-inward)
            if piece == "Flowerbed_2m":
                rot = face_rot(inward)
            S.put(piece, p.x, p.y, pz, rot, sub=subc(S, "Plaza"))

    # ---------------------------------------------------------------- entrances
    gates = {}
    # E1: plaza -> Maple St / Swan Ln corner
    st = FP + e1_dir * (PR - 0.3)
    hit, L = connector(S, plan, "Path_E1", st, e1_dir)
    if hit is not None:
        gates["E1"] = round(L, 1)
        # the Maple St / Swan Ln corner kerb curves toward the park: pull the pillar pair 0.6 m back onto the
        # grass (gate_entrance then also checks both footings against the sidewalk corridor)
        gate_entrance(S, plan, hit, e1_dir, name="Gate_E1", wings=2, extra_back=0.6)
        for sx in (-1, 1):
            q = hit - e1_dir * 3.2 + Vector((e1_dir.y, -e1_dir.x)) * sx * 3.1
            plan.prop("Flowerbed_2m", q, face_rot(-e1_dir), r=1.0, sub="Gates", path=0.2)
    # E2: east loop -> Swan Lane (toward the Mill Bridge)
    if loop is not None:
        s2, _ = _closest_s(loop, Vector((-135.0, 22.0)))
        p2 = loop.pos(s2)
        d2 = Vector((1.0, 0.04)).normalized()
        hit, L = connector(S, plan, "Path_E2", p2, d2)
        if hit is not None:
            gates["E2"] = round(L, 1)
            gate_entrance(S, plan, hit, d2, name="Gate_E2", wings=3, slim=L < 4.5, gap=3.2)
        # E3: south-west loop -> Park Lane
        s3, _ = _closest_s(loop, Vector((-199.0, -22.0)))
        p3 = loop.pos(s3)
        d3 = Vector((-0.606, -0.795)).normalized()
        hit, L = connector(S, plan, "Path_E3", p3, d3)
        if hit is not None:
            gates["E3"] = round(L, 1)
            gate_entrance(S, plan, hit, d3, name="Gate_E3", wings=3, slim=L < 4.5, gap=3.2)
            for sx in (-1, 1):
                q = hit - d3 * 3.4 + Vector((d3.y, -d3.x)) * sx * 3.0
                plan.prop("Flowerbed_2m", q, face_rot(-d3), r=1.0, sub="Gates", path=0.2)
        # E5: north loop -> canal riverwalk
        s5, _ = _closest_s(loop, Vector((-178.0, 56.0)))
        p5 = loop.pos(s5)
        rw = next((p for p in lay.PATHS if p["id"] == "RiverwalkS"), None)
        if rw is not None:
            rpl = path_polyline(rw)
            sr, dr = _closest_s(rpl, p5)
            q5 = rpl.pos(sr)
            S.path_ribbon("Path_E5", [p5, p5.lerp(q5, 0.5), q5], width=2.6, mat="M_Path", sub=subc(S, "Paths"))
            gates["E5"] = round((q5 - p5).length, 1)
            plan.paths.add(p5, q5, 1.3, payload="E5")
    report["entrances"] = gates

    # ---------------------------------------------------------------- Swan Pond: pier, boat, reeds, rocks
    if pond is not None:
        wi = pond.water_inset()
        a_p = math.radians(2.0)
        shore = pond.at(a_p, -1.6)
        dirp = (pond.c - shore).normalized()
        Lp = (pond.R(a_p) + 1.6) - (pond.R(a_p) - 6.8)     # from 1.6 m outside to 6.8 m inside the outline
        deck = GZ + 0.32
        o = obj_at(S, "Pier", pier_mb(L=Lp - 2.4, W=2.0, dz=0.0, post_bot=-1.4), shore.x, shore.y, deck,
                   face_rot(-dirp), sub=subc(S, "Pond"))
        objs.append(o)
        plan.occ.add(shore + dirp * 2.0, 2.0)
        head = shore + dirp * (Lp - 1.2)
        side = Vector((dirp.y, -dirp.x))
        boat = head + side * 2.9 - dirp * 0.6
        objs.append(obj_at(S, "SwanBoat", swan_boat_mb(), boat.x, boat.y, -0.48, face_rot(dirp) + 0.12,
                           sub=subc(S, "Pond"), smooth=("M_Trim_White", "M_Awning_Teal"), angle=55))
        S.put("Lamp_Park", (shore + side * 1.6).x, (shore + side * 1.6).y, GZ - 0.02, face_rot(dirp),
              sub=subc(S, "Pond"))
        S.put("Bench", (head - side * 0.0 + dirp * 0.55).x, (head + dirp * 0.55).y, deck,
              face_rot(dirp), sub=subc(S, "Pond"))
        # dirt spur from the loop to the pier
        if loop is not None:
            sl, _ = _closest_s(loop, shore - dirp * 8.0)
            a0 = loop.pos(sl)
            S.path_ribbon("Path_Pier", [a0, a0.lerp(shore, 0.5), shore + dirp * 0.6], width=2.0, mat="M_Path",
                          sub=subc(S, "Paths"))
            plan.paths.add(a0, shore, 1.0, payload="pier")
        # reeds: shady west / south-west / north-west shore, in clumps
        rmb = MeshBuilder()
        rr = random.Random("cp-reeds")    # own stream: reed tweaks never reshuffle the rest of the layout
        nclumps = 0
        for (a_deg, span, n) in ((150, 44, 13), (195, 30, 10), (232, 26, 9), (110, 18, 5), (282, 16, 5), (322, 12, 4)):
            for k in range(n):
                a = math.radians(a_deg + rr.uniform(-span / 2, span / 2))
                inset = rr.uniform(wi - 0.5, wi + 1.6)
                p = pond.at(a, inset)
                z = pond.bank_z(p)
                reed_clump(rmb, p.x - pond.c.x, p.y - pond.c.y, z, rr, h=rr.uniform(1.5, 2.2), n=rr.randint(8, 12),
                           spread=0.5)
                nclumps += 1
        objs.append(obj_at(S, "Reeds", rmb, pond.c.x, pond.c.y, 0.0, 0.0, sub=subc(S, "Pond")))
        report["reed_clumps"] = nclumps
        lmb = MeshBuilder()
        lily_pads(lmb, pond, rng, n=21, clusters=((300, 4.0), (60, 4.5), (238, 5.5)))
        objs.append(obj_at(S, "LilyPads", lmb, pond.c.x, pond.c.y, 0.0, 0.0, sub=subc(S, "Pond")))
        # shore rocks (half in the sand)
        for a_deg in (40, 75, 128, 170, 214, 258, 300, 340):
            a = math.radians(a_deg + rng.uniform(-8, 8))
            p = pond.at(a, rng.uniform(-0.3, 1.2))
            s = rng.uniform(0.9, 1.7)
            S.put(rng.choice(["Rock_A", "Rock_B"]), p.x, p.y, pond.bank_z(p) - 0.12 * s, rng.uniform(0, TAU),
                  scale=(s, s, s * 0.9), sub=subc(S, "Pond"))
            if rng.random() < 0.6:
                q = pond.at(a + 0.05, -0.8)
                S.put("Rock_A", q.x, q.y, GZ - 0.08, rng.uniform(0, TAU), scale=(0.6, 0.6, 0.6),
                      sub=subc(S, "Pond"))

    # ---------------------------------------------------------------- playground (between loop and riverwalk)
    rw = next((p for p in lay.PATHS if p["id"] == "RiverwalkS"), None)
    pg_report = {}
    if rw is not None and loop is not None:
        rpl = path_polyline(rw)
        sr, _ = _closest_s(rpl, Vector((-196.0, 76.0)))
        q = rpl.pos(sr)
        t = rpl.tangent(sr)
        if t.x < 0:
            t = -t
        n = Vector((t.y, -t.x))               # toward the park (south-ish)
        if n.y > 0:
            n = -n
        q_edge = q + n * (rw.get("width", 4.0) / 2)
        # distance to the loop along n
        gap = 0.0
        while gap < 40 and not plan.paths.blocked(q_edge + n * (gap + 0.5), extra=0.0) or gap < 1.0:
            gap += 0.25
        depth = min(12.0, gap - 3.0)
        PG = q_edge + n * (1.5 + depth / 2)
        W = 15.0
        pg_report = dict(center=(round(PG.x, 1), round(PG.y, 1)), gap=round(gap, 1), depth=round(depth, 1))
        u = t
        zpad, o = soft_pad(S, "PlaygroundPad", PG, u, W, depth, sub=subc(S, "Playground"))
        objs.append(o)
        for k in (-1, 0, 1):
            plan.occ.add(PG + u * (k * (W / 2 - depth / 2)), depth / 2 + 0.5)

        def L2W(lu, lv):
            return PG + u * lu + n * lv

        rot_u = math.atan2(u.y, u.x)
        zp = zpad
        tw = L2W(-4.8, -2.0)
        objs.append(obj_at(S, "PlayTower", play_tower_mb(), tw.x, tw.y, zp, rot_u + math.pi / 2,
                           sub=subc(S, "Playground"), smooth=("M_Awning_Yellow",), angle=40))
        ca = L2W(-4.0, 3.5)
        objs.append(obj_at(S, "ClimbArch", climb_arch_mb(), ca.x, ca.y, zp, rot_u, sub=subc(S, "Playground"),
                           smooth=("M_Awning_Green", "M_Metal"), angle=50))
        ss = L2W(4.0, -3.7)
        objs.append(obj_at(S, "Seesaw", seesaw_mb(), ss.x, ss.y, zp, rot_u, sub=subc(S, "Playground")))
        for lu in (1.4, 4.7):
            p = L2W(lu, 2.9)
            S.put("Swing", p.x, p.y, zp, rot_u, recolor={"awning": "M_Awning_Teal" if lu > 4 else "M_Awning_Red"},
                  sub=subc(S, "Playground"))
        for lu, lv, piece in ((-2.0, depth / 2 + 1.0, "Bench"), (3.0, depth / 2 + 1.0, "Bench")):
            p = L2W(lu, lv)
            S.put(piece, p.x, p.y, zmin(S, p, 0.9) - 0.02, face_rot(-n), sub=subc(S, "Playground"))
        p = L2W(0.5, depth / 2 + 1.0)
        S.put("TrashBin", p.x, p.y, zmin(S, p, 0.4) - 0.02, face_rot(-n), sub=subc(S, "Playground"))
        for lu in (-W / 2 - 1.4, W / 2 + 1.4):
            p = L2W(lu, -depth / 2 + 1.5)
            plan.prop("Flowerbed_2m", p, face_rot(u), r=1.0, sub="Playground")
    report["playground"] = pg_report

    # ---------------------------------------------------------------- Picnic Hill
    if hill is not None:
        HT = G.V(hill["center"])
        ang_path = math.atan2(40 - HT.y, -212 - HT.x)
        tree_a = ang_path + math.radians(150)
        big = HT + Vector((math.cos(tree_a), math.sin(tree_a))) * 7.0
        plan.tree(big, piece="Tree_Round_B", foliage="M_Foliage", scale=1.4, r=6.0)
        for k, da in enumerate((60, 110, 205, 255, 300)):
            a = ang_path + math.radians(da)
            p = HT + Vector((math.cos(a), math.sin(a))) * (4.6 if k % 2 else 5.4)
            tang = Vector((-math.sin(a), math.cos(a)))
            if plan.ok(p, r=1.3, road=2.0, path=0.6):
                plan.occ.add(p, 1.3)
                S.put("PicnicTable", p.x, p.y, zmin(S, p, 0.9) - 0.02, math.atan2(tang.y, tang.x),
                      sub=subc(S, "PicnicHill"))
        p = HT + Vector((math.cos(ang_path), math.sin(ang_path))) * 3.2 + \
            Vector((-math.sin(ang_path), math.cos(ang_path))) * 2.4
        plan.prop("TrashBin", p, 0.0, r=0.5, sub="PicnicHill")
        jp = Vector((-212.0, 40.0))
        for off in (Vector((-2.3, -2.3)),):
            q = jp + off
            if plan.ok(q, r=0.4, path=0.2):
                plan.occ.add(q, 0.5)
                S.put("Lamp_Park", q.x, q.y, zmin(S, q, 0.3) - 0.02, 0.0, sub=subc(S, "Furniture"))

    # ---------------------------------------------------------------- loop furniture (lamps + benches)
    if loop is not None:
        # outside of the loop = away from the pond
        def outer_n(s):
            p = loop.pos(s)
            nl = G.left_normal(loop.tangent(s))
            return nl if (p + nl - pond.c).length > (p - pond.c).length else -nl

        s = 9.0
        k = 0
        while s < loop.length - 9.0:
            p = loop.pos(s)
            no = outer_n(s)
            if (p - FP).length > PR + 4.0:
                if k % 2 == 0:
                    q = p + no * 2.0
                    if plan.ok(q, r=0.4, road=0.6, path=0.1):
                        plan.occ.add(q, 0.6)
                        S.put("Lamp_Park", q.x, q.y, zmin(S, q, 0.3) - 0.02, face_rot(-no), sub=subc(S, "Furniture"))
                else:
                    q = p + no * 2.25
                    if plan.ok(q, r=1.0, road=0.6, path=0.1):
                        plan.occ.add(q, 1.1)
                        S.put("Bench", q.x, q.y, zmin(S, q, 0.9) - 0.02, face_rot(-no), sub=subc(S, "Furniture"))
                        b2 = q + loop.tangent(s) * 1.6
                        if k % 4 == 1 and plan.ok(b2, r=0.35, road=0.6, path=0.1):
                            plan.occ.add(b2, 0.4)
                            S.put("TrashBin", b2.x, b2.y, zmin(S, b2, 0.3) - 0.02, face_rot(-no),
                                  sub=subc(S, "Furniture"))
            s += 12.5
            k += 1

    # ---------------------------------------------------------------- trees: canopy clumps + specimens
    canopy_fol = [("M_Foliage", 4), ("M_Foliage_Dark", 3), ("M_Foliage_Light", 2)]
    clumps = [((-244, 36), 11, 9), ((-236, 70), 9, 6), ((-226, 14), 9, 8), ((-247, 14), 7, 4),
              ((-212, 72), 6, 3), ((-252, 54), 6, 3), ((-205, -12), 5, 2), ((-158, -42), 6, 3)]
    clumps += [((-130.5, 2), 4, 2), ((-147, 47), 5, 2), ((-176, -45), 6, 3), ((-205, -32), 5, 2),
               ((-221, -12), 5, 2), ((-152, 22), 4, 2),
               # loose groups along the inside of the loop: shade over the path, the lawn centre stays open
               ((-184, 45), 5, 3), ((-150, 13), 4, 2), ((-166, -29), 4, 2), ((-206, 6), 4, 2),
               ((-207, 33), 4, 2), ((-160, 55), 4, 2)]
    for c, rad, n in clumps:
        plan.cluster(c, rad, n, min_d=4.6, fol_mix=canopy_fol)
    # accent / specimen trees on the lawns (keep the north + east lawns open in the middle)
    specimens = [((-199, 30), "Tree_Round_B", "M_Foliage_Blossom", 1.15), ((-150, 30), "Tree_Round_A", "M_Foliage_Autumn", 1.2),
                 ((-160, -41), "Tree_Round_A", "M_Foliage_Blossom", 1.1), ((-198, -12), "Tree_Cone", "M_Foliage_Dark", 1.2),
                 ((-214, 52), "Tree_Round_A", "M_Foliage_Autumn", 1.15), ((-163, 56), "Tree_Round_B", "M_Foliage", 1.1)]
    for (p, pc, fol, sc) in specimens:
        p = V2(p)
        if plan.ok(p, r=2.0, road=1.5, path=1.4):
            plan.tree(p, piece=pc, foliage=fol, scale=sc, r=4.0)
    # bushes along the hill foot / clumps (understory for hiding)
    plan.scatter([("Bush_B", 2), ("Bush_A", 3)], 22, [(-262, 0), (-236, 0), (-226, 30), (-232, 82), (-252, 86),
                                                     (-262, 50)], r=1.2, sub="Bushes",
                 recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage", "M_Foliage_Dark", "M_Hedge"])})
    plan.scatter([("Bush_A", 3), ("Bush_B", 1)], 6, S.poly, r=1.0, sub="Bushes",
                 recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage", "M_Foliage_Dark"])},
                 extra_ok=lambda p: p.x > -170 and p.y < -25)

    report["custom_tris"] = tri_count(objs)
    _SHARED["occ"] = plan.occ
    _SHARED["paths"] = plan.paths
    return report


# =============================================================================== NO_BUILD areas
def build_area(S):
    if S.id == "CrescentCommons":
        return _commons(S)
    if S.id == "RiverwalkGardens":
        return _gardens(S)
    return "skipped"


def _maze(rng, nx, ny, start):
    """Perfect maze by randomized DFS. Returns the set of open passages {((i,j),(k,l))}."""
    seen = {start}
    stack = [start]
    open_ = set()
    while stack:
        c = stack[-1]
        i, j = c
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= i + di < nx and 0 <= j + dj < ny and (i + di, j + dj) not in seen]
        if not nb:
            stack.pop()
            continue
        n = rng.choice(nb)
        open_.add(frozenset((c, n)))
        seen.add(n)
        stack.append(n)
    return open_


def _commons(S):
    rng = random.Random("commons-maze-3")
    x0p, y0p, x1p, y1p = G.bbox(S.poly)
    plan = Planner(S, keep_in=S.poly)
    sub = "Maze"
    # ---------------------------------------------------------------- hedge maze 5 x 5 cells of 3 m
    N, CS = 5, 3.0
    X0, Y0 = -106.5, -258.0
    open_ = _maze(rng, N, N, (2, 2))
    ent = (4, 3)            # east wall of cell (4,3) -> CommonsWalk
    ext = (2, 4)            # north wall of cell (2,4) -> swing lawn
    walls_x, walls_y = set(), set()     # walls along X: (i, j) = edge from node (i,j) to (i+1,j)
    for i in range(N):
        for j in range(N + 1):
            if j in (0, N):
                if (j == N and (i, N - 1) == ext):
                    continue
                walls_x.add((i, j))
            elif frozenset(((i, j - 1), (i, j))) not in open_:
                walls_x.add((i, j))
    for i in range(N + 1):
        for j in range(N):
            if i in (0, N):
                if i == N and (N - 1, j) == ent:
                    continue
                walls_y.add((i, j))
            elif frozenset(((i - 1, j), (i, j))) not in open_:
                walls_y.add((i, j))

    def node_has_y(a, b):
        return (a, b - 1) in walls_y or (a, b) in walls_y

    zg = GZ - 0.02
    n_h = 0
    for (i, j) in sorted(walls_x):
        el = 0.45 if (node_has_y(i, j) or (i - 1, j) not in walls_x) else 0.0
        er = 0.45 if (node_has_y(i + 1, j) or (i + 1, j) not in walls_x) else 0.0
        L = CS + el + er
        cx = X0 + CS * i + CS / 2 + (er - el) / 2
        S.put("Hedge_3m", cx, Y0 + CS * j, zg, 0.0, scale=(L / 3.0, 1.0, 1.0), sub=subc(S, sub))
        n_h += 1
    for (i, j) in sorted(walls_y):
        S.put("Hedge_3m", X0 + CS * i, Y0 + CS * j + CS / 2, zg, math.pi / 2, sub=subc(S, sub))
        n_h += 1
    mz = [(X0 - 0.6, Y0 - 0.6), (X0 + N * CS + 0.6, Y0 - 0.6), (X0 + N * CS + 0.6, Y0 + N * CS + 0.6),
          (X0 - 0.6, Y0 + N * CS + 0.6)]
    plan.avoid_polys.append([G.V(p) for p in mz])
    # gravel floor in the corridors would be nice but grass reads better for kangaroos - keep grass
    # maze mouths: lamps + flower beds
    ey = Y0 + CS * ent[1] + CS / 2
    exx = X0 + CS * ext[0] + CS / 2
    walk = next((p for p in S.layout.PATHS if p["id"] == "CommonsWalk"), None)
    if walk is not None:
        a = Vector((x1p - 0.4, -247.0))
        b = Vector((X0 + N * CS + 0.2, -247.0))
        S.path_ribbon("Path_MazeEast", [a, a.lerp(b, 0.5), b], width=2.5, mat="M_Path", sub=subc(S, "Paths"))
        plan.paths.add(a, b, 1.1)
    b0 = Vector((exx, Y0 + N * CS - 0.2))
    b1 = Vector((exx, Y0 + N * CS + 3.4))
    S.path_ribbon("Path_MazeNorth", [b0, b0.lerp(b1, 0.5), b1], width=2.0, mat="M_Path", sub=subc(S, "Paths"))
    plan.paths.add(b0, b1, 1.0)
    for sy in (-1, 1):
        plan.prop("Flowerbed_2m", (X0 + N * CS + 2.2, ey + sy * 2.6), math.pi / 2, r=1.0, sub="Garden", path=0.1)
        plan.prop("Bush_A", (exx + sy * 2.4, Y0 + N * CS + 1.2), 0.0, r=0.6, sub="Garden", path=0.1,
                  recolor={"foliage": "M_Hedge"})
    plan.prop("Lamp_Park", (x1p - 1.4, ey + 2.4), 0.0, r=0.4, sub="Garden", path=0.1)
    plan.prop("Lamp_Park", (x1p - 1.4, ey - 2.6), 0.0, r=0.4, sub="Garden", path=0.1)
    # ---------------------------------------------------------------- swing lawn (north)
    sp = Vector((-103.5, -233.6))
    zsp, _o = soft_pad(S, "SwingPad", sp, (1.0, 0.0), 12.0, 6.0, sub=subc(S, "Swings"), lift=0.08)
    plan.occ.add(sp, 4.5)
    for dx, col in ((-3.0, "M_Awning_Blue"), (3.0, "M_Awning_Yellow")):
        S.put("Swing", sp.x + dx, sp.y, zsp, 0.0, recolor={"awning": col}, sub=subc(S, "Swings"))
    plan.prop("Bench", (sp.x - 8.0, sp.y), face_rot((1, 0)), r=1.0, sub="Swings", force=True)
    plan.prop("Bench", (sp.x + 2.0, y1p - 1.3), face_rot((0, -1)), r=1.0, sub="Swings", force=True)
    plan.prop("PicnicTable", (-89.5, -232.5), 0.2, r=1.4, sub="Swings")
    plan.prop("TrashBin", (sp.x - 8.0, sp.y + 1.6), 0.0, r=0.4, sub="Swings", force=True)
    plan.prop("Birdbath", (-111.0, -246.0), 0.0, r=0.5, sub="Garden")
    # maze centre (CrescentHedge hiding spot): a birdbath in the middle cell and a bush in its corner
    mc = Vector((X0 + CS * 2.5, Y0 + CS * 2.5))
    S.put("Birdbath", mc.x - 0.35, mc.y + 0.3, zg, 0.0, sub=subc(S, sub))
    S.put("Bush_A", mc.x + 0.55, mc.y - 0.55, zg, 1.0, recolor={"foliage": "M_Foliage_Blossom"},
          scale=(0.9, 0.9, 0.9), sub=subc(S, sub))
    # ---------------------------------------------------------------- trees + bushes round the edges
    for p, fol, pc in (((-111.5, -230.5), "M_Foliage_Blossom", "Tree_Round_A"),
                       ((-86.5, -229.8), "M_Foliage", "Tree_Round_B"),
                       ((-111.6, -263.4), "M_Foliage_Autumn", "Tree_Round_A"),
                       ((-86.4, -263.6), "M_Foliage_Blossom", "Tree_Round_A"),
                       ((-111.8, -253.0), "M_Foliage_Dark", "Tree_Cone"),
                       ((-99.0, -263.6), "M_Foliage", "Tree_Small")):
        if plan.ok(p, r=1.0, road=1.0, path=0.6):
            plan.tree(V2(p), piece=pc, foliage=fol, scale=1.0 if pc != "Tree_Small" else 1.2, r=2.4)
    plan.prop("Bench", (-99.0, -260.6), face_rot((0, 1)), r=1.0, sub="Garden")
    plan.prop("Lamp_Park", (-104.0, -261.0), 0.0, r=0.4, sub="Garden")
    plan.scatter([("Bush_A", 2), ("Bush_B", 1)], 7, S.poly, r=0.9, sub="Garden",
                 recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage", "M_Hedge", "M_Foliage_Dark"])},
                 extra_ok=lambda p: (p.x < -108.5 or p.x > -89.5 or p.y < -260.0) and not
                 (-237.5 < p.y < -229.5 and -111 < p.x < -96))
    return dict(hedges=n_h, maze_entrance=(round(X0 + N * CS, 1), round(ey, 1)), maze_exit=(round(exx, 1),
                round(Y0 + N * CS, 1)))


def _gardens(S):
    rng = random.Random("gardens")
    plan = Planner(S, keep_in=S.poly)
    O = Vector((111.0, 37.0))
    u = Vector((0.9428, -0.3333)).normalized()
    v = Vector((-u.y, u.x))
    rot_u = math.atan2(u.y, u.x)

    def W(lu, lv):
        return O + u * lu + v * lv

    zg = GZ
    U0, U1, V0, V1 = -16.5, 16.5, -5.0, 8.0
    # find the real southern limit: riverwalk north edge + margin
    vmin = V0
    for lu in (U0, 0.0, U1):
        lv = V0
        while plan.paths.blocked(W(lu, lv), extra=0.7) and lv < 0:
            lv += 0.1
        vmin = max(vmin, lv)
    V0 = vmin
    gate_u = 3.0
    # ---------------------------------------------------------------- picket fence + rose arch gate
    corners = [W(U0, V0), W(U1, V0), W(U1, V1), W(U0, V1)]
    gate_pt = W(gate_u, V0)
    S.fence_along(corners, piece="Fence_Picket_3m", closed=True, gaps=[(gate_pt, 1.0)], z=zg - 0.02,
                  sub=subc(S, "Fence"))
    objs = []
    objs.append(obj_at(S, "RoseArch", rose_arch_mb(w=2.8), gate_pt.x, gate_pt.y, zg - 0.02, rot_u,
                       sub=subc(S, "Fence"), smooth=("M_Foliage_Dark",), angle=60))
    # ---------------------------------------------------------------- gravel paths (cross)
    pm = MeshBuilder()

    def strip(a, b, w):
        d = (b - a).normalized()
        nn = Vector((-d.y, d.x)) * w / 2
        pts = [a - nn, b - nn, b + nn, a + nn]
        pm.prism([(p.x - O.x, p.y - O.y) for p in pts], zg - 0.15, zg + 0.03, "M_Gravel", "M_Gravel")
    strip(W(gate_u, V0 - 0.2), W(gate_u, V1 - 0.3), 1.6)
    strip(W(U0 + 0.4, 3.1), W(gate_u - 0.8, 3.1), 1.3)
    strip(W(gate_u + 0.8, 3.1), W(U1 - 0.4, 3.1), 1.3)
    objs.append(S.mesh("GravelPaths", pm, sub=subc(S, "Beds"), loc=(O.x, O.y, 0.0)))
    # hiding spot (bean rows): leave a freshly dug plot free, ring it with bean teepees
    hs = next((G.V(h["at"]) for h in S.layout.HIDING_SPOTS if h["id"] == "RiverwalkGardens"), None)
    dug_u, dug_v = -0.6, -1.3
    if hs is not None:
        d = hs - O
        dug_u, dug_v = d.dot(u), d.dot(v)
    dm = MeshBuilder()
    dug = [W(dug_u - 2.0, dug_v - 1.6), W(dug_u + 1.8, dug_v - 1.6), W(dug_u + 1.8, dug_v + 1.6),
           W(dug_u - 2.0, dug_v + 1.6)]
    dm.prism([(p.x - O.x, p.y - O.y) for p in dug], zg - 0.15, zg + 0.04, "M_Dirt", "M_Dirt")
    objs.append(S.mesh("DugPlot", dm, sub=subc(S, "Beds"), loc=(O.x, O.y, 0.0)))
    cache = {}           # shared custom meshes (one per crop / piece), see shared_obj
    for i, lv in enumerate((dug_v - 1.0, dug_v + 0.9)):
        p = W(dug_u - 2.9, lv)
        objs.append(shared_obj(S, cache, "BeanTeepee_mesh", f"BeanTeepee_{i}", lambda: bean_teepee_mb(rng), p.x, p.y,
                               zg, rng.uniform(0, TAU), sub=subc(S, "Beds"), smooth=("M_Foliage", "M_Foliage_Dark"),
                               angle=60))
    # the hiding spot itself: two bean rows with a crawl gap between them (one mesh, the 2nd turned 180 deg)
    for i, lv in enumerate((dug_v - 0.75, dug_v + 0.75)):
        p = W(dug_u, lv)
        objs.append(shared_obj(S, cache, "BeanRow_mesh", f"BeanRow_{i}", lambda: bean_row_mb(rng), p.x, p.y,
                               zg + 0.04, rot_u + math.pi * i, sub=subc(S, "Beds"),
                               smooth=("M_Foliage", "M_Foliage_Dark"), angle=60))
    # ---------------------------------------------------------------- raised beds
    crops = ["lettuce", "cabbage", "tomato", "pumpkin", "carrot"]
    beds = []
    for lv in (-2.3, 1.2 - 0.25):
        for lu in (-14.3, -10.3, -6.3, 7.0, 11.0, 15.0 - 0.3):
            beds.append((lu, lv))
    for lu in (-6.3, -1.4, 7.0, 10.8):
        beds.append((lu, 5.0))
    nb = 0
    for k, (lu, lv) in enumerate(beds):
        if lv < V0 + 0.9:
            continue
        if abs(lu - dug_u) < 3.2 and abs(lv - dug_v) < 2.4:
            continue
        p = W(lu, lv)
        crop = crops[(k * 3 + 1) % len(crops)]
        # one mesh per crop; every other bed of a crop is turned 180 deg so the repeats do not read as copies
        objs.append(shared_obj(S, cache, f"RaisedBed_{crop}", f"RaisedBed_{nb:02d}",
                               lambda c=crop: raised_bed_mb(c, rng), p.x, p.y, zg, rot_u + math.pi * (nb % 2),
                               sub=subc(S, "Beds"),
                               smooth=("M_Foliage", "M_Foliage_Light", "M_Foliage_Dark", "M_Hazard_Orange"), angle=60))
        nb += 1
    # ---------------------------------------------------------------- sunflower border along the promenade fence
    lu = U0 + 0.8
    ns = 0
    while lu < U1 - 0.6:
        if abs(lu - gate_u) > 1.6:
            p = W(lu + rng.uniform(-0.15, 0.15), V0 + 0.55 + rng.uniform(-0.1, 0.1))
            hv = ns % 3                                  # three shared sunflower heights
            objs.append(shared_obj(S, cache, f"Sunflower_h{hv}", f"Sunflower_{ns:02d}",
                                   lambda hv=hv: sunflower_mb(rng, h=(1.55, 1.8, 2.05)[hv]), p.x, p.y, zg,
                                   rot_u + rng.uniform(-0.3, 0.3), sub=subc(S, "Beds"), smooth=("M_Foliage",),
                                   angle=60))
            ns += 1
        lu += rng.uniform(1.2, 1.7)
    # ---------------------------------------------------------------- shed, scarecrow, compost, water butt, bench
    from ..assembler import BuildingSpec, H3
    shed_o = W(-12.6, 4.4)
    spec = BuildingSpec("shed", 2, 1, 1, dict(wall="M_Wall_Sage", trim="M_Trim_White", door="M_Door_Teal",
                                              roof="M_Roof_Green", awning="M_Awning_Green", sign="M_Sign_Accent"),
                        roof="flat", ground_h=H3, seed=17, district="Riverwalk")
    S.building(spec, shed_o, rot_u, name="LM_RiverwalkGardens_ToolShed")
    sc = W(-3.9, 5.0)
    objs.append(obj_at(S, "Scarecrow", scarecrow_mb(), sc.x, sc.y, zg, rot_u + math.pi + 0.25, sub=subc(S, "Beds"),
                       smooth=("M_Sand",), angle=50))
    for i, lu2 in enumerate((-8.4, -7.3)):
        p = W(lu2, 7.1)
        S.put("Crate", p.x, p.y, zg, rot_u + rng.uniform(-0.1, 0.1), sub=subc(S, "Props"))
    p = W(-9.1, 5.0)
    S.put("Barrel", p.x, p.y, zg, 0.0, sub=subc(S, "Props"))
    p = W(9.0, 7.2)
    S.put("Bench", p.x, p.y, zg, rot_u, sub=subc(S, "Props"))
    spec2 = BuildingSpec("shed", 1, 1, 1, dict(wall="M_Wall_Butter", trim="M_Trim_White", door="M_Door_Teal",
                                               roof="M_Roof_Green", awning="M_Awning_Green", sign="M_Sign_Accent"),
                         roof="flat", ground_h=H3, seed=23, district="Riverwalk", feats=dict(door_i=0))
    S.building(spec2, W(14.75, 4.7), rot_u, name="LM_RiverwalkGardens_PottingShed")
    p = W(12.9, 7.2)
    S.put("Planter", p.x, p.y, zg, 0.0, recolor={"foliage": "M_Foliage_Blossom"}, sub=subc(S, "Props"))
    p = W(5.0, 7.1)
    S.put("Pallet", p.x, p.y, zg, rot_u, sub=subc(S, "Props"))
    p = W(5.2, 7.1)
    S.put("CrateStack", p.x, p.y, zg + 0.15, rot_u, sub=subc(S, "Props"))
    return dict(beds=nb, custom_tris=tri_count(objs), band=(round(V0, 2), V1))


# =============================================================================== DISTRICTS (kind park)
def build_district(S):
    did = S.data.get("id")
    if did == "CentralPark":
        return _cp_fringe(S)
    if did == "LookoutPark":
        return _lookout_park(S)
    if did == "WillowWoods":
        return _willow_woods(S)
    return "skipped"


def _site_polys(S, pad=0.0):
    out = []
    for k, v in S.layout.LANDMARKS.items():
        P = [G.V(p) for p in v.get("poly", [])]
        if pad:
            c = G.centroid(P)
            P = G.offset_polygon_radial(P, c, -pad)
        out.append(P)
    for nb in S.layout.NO_BUILD:
        P = [G.V(p) for p in nb["poly"]]
        if pad:
            c = G.centroid(P)
            P = G.offset_polygon_radial(P, c, -pad)
        out.append(P)
    return out


_XY_BOUNDS = {}


def _dist_poly(p, P):
    """0 inside the polygon, else the distance to its boundary."""
    if G.point_in_poly(p, P):
        return 0.0
    return min(G.dist_point_seg(p, P[i], P[(i + 1) % len(P)]) for i in range(len(P)))


def _footprint(o):
    """World XY sample points of an object's ground footprint (same sampling as the landmark review audit):
    kit instance -> the 4 corners of its XY bounds + the origin; custom mesh -> up to ~400 of its vertices.
    Uses matrix_basis (no depsgraph update needed; these objects have no parent)."""
    M = o.matrix_basis
    me = o.data
    if me.name.startswith("KIT_"):
        b = _XY_BOUNDS.get(me.name)
        if b is None:
            xs = [v.co.x for v in me.vertices] or [0.0]
            ys = [v.co.y for v in me.vertices] or [0.0]
            b = _XY_BOUNDS[me.name] = (min(xs), min(ys), max(xs), max(ys))
        pts = [M @ Vector((x, y, 0.0)) for x in (b[0], b[2]) for y in (b[1], b[3])] + [M.translation]
    else:
        vs = me.vertices
        step = max(1, len(vs) // 400)
        pts = [M @ vs[i].co for i in range(0, len(vs), step)]
    return [Vector((q.x, q.y)) for q in pts]


def _rehome(DS, site_id, tol=0.9):
    """Hand the objects the *site_id* builder placed on THIS district's land over to the district: everything
    whose footprint stands more than *tol* m outside the site polygon (connector paths + gates at the sidewalks,
    their fence wings and flower beds, loop furniture where the loop hugs the site edge, edge trees) is renamed
    LM_<district>_..., relinked into the district's sub-collections (CentralPark_Gates -> D_CentralPark_Gates)
    and so lands in the district's per-site FBX - names, collections and export match the land it stands on.
    Runs first in build_district (sites are built before districts), so the district numbering continues
    after the adopted pieces. Returns {new name: metres outside the site}."""
    import bpy
    sp = [G.V(p) for p in DS.layout.LANDMARKS.get(site_id, {}).get("poly", [])]
    root = bpy.data.collections.get(f"LM_{site_id}")
    if root is None or not sp:
        return {}
    pre = f"LM_{site_id}_"
    moved = {}
    for o in sorted(root.all_objects, key=lambda ob: ob.name):
        if o.type != "MESH" or o.parent is not None or not o.name.startswith(pre):
            continue
        pts = _footprint(o)
        out_site = max(_dist_poly(p, sp) for p in pts)
        if out_site <= tol or max(_dist_poly(p, DS.poly) for p in pts) >= out_site:
            continue
        me = o.data
        if me.name.startswith("KIT_"):
            DS.n += 1
            new = f"LM_{DS.id}_{me.name[4:]}_{DS.n:03d}"[:63]
        else:
            new = f"LM_{DS.id}_{o.name[len(pre):]}"[:63]
            if me.users == 1:
                me.name = new
        cols = list(o.users_collection)
        sub = None
        for c in cols:
            if c.name.startswith(site_id + "_"):
                sub = c.name[len(site_id) + 1:]
            c.objects.unlink(o)
        o.name = new
        scene.coll(DS.coll + (f"/{subc(DS, sub)}" if sub else "")).objects.link(o)
        moved[o.name] = round(out_site, 1)
    return moved


def _cp_fringe(S):
    """Central Park district land OUTSIDE the park site and west of Swan Lane: soft tree rows + bushes. First
    adopts the site builder's pieces that stand on district land (_rehome)."""
    moved = _rehome(S, "CentralPark")
    plan = Planner(S, keep_in=S.poly, avoid_polys=_site_polys(S, pad=3.0))
    if "occ" in _SHARED:              # the site builder's connectors, gates and trees near its edge
        plan.occ = _SHARED["occ"]
        plan.paths = _SHARED["paths"]
    rng = S.rng
    west = lambda p: p.x < -131.0
    trees = 0
    for _ in range(60):
        for _t in range(40):
            x0, y0, x1, y1 = G.bbox(S.poly)
            p = Vector((rng.uniform(x0, -128.0), rng.uniform(y0, y1)))
            if not west(p):
                continue
            if not plan.ok(p, r=3.2, road=1.4, path=1.4):
                continue
            plan.tree(p, r=6.4, mix=[("Tree_Round_A", 4), ("Tree_Round_B", 2), ("Tree_Cone", 2)],
                      fol_mix=[("M_Foliage", 4), ("M_Foliage_Dark", 2), ("M_Foliage_Light", 2),
                               ("M_Foliage_Autumn", 1)])
            trees += 1
            break
    b = plan.scatter([("Bush_A", 2), ("Bush_B", 2)], 18, S.poly, r=1.2, sub="Bushes", extra_ok=west, road=0.8,
                     recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage", "M_Foliage_Dark", "M_Hedge"])})
    return dict(trees=trees, bushes=len(b), adopted_from_site=len(moved), adopted=moved)


# ------------------------------------------------------------------------------ Lookout Park
def _lookout_park(S):
    rng = S.rng
    lay = S.layout
    hill = next((h for h in lay.HILLS if h["id"] == "LookoutHill"), None)
    HC = G.V(hill["center"]) if hill else G.centroid(S.poly)
    lk = lay.LANDMARKS.get("Lookout", {})
    lk_poly = [G.V(p) for p in lk.get("poly", [])]
    hide = [(G.V(h["at"]), 4.0) for h in lay.HIDING_SPOTS if G.point_in_poly(G.V(h["at"]), S.poly)]
    plan = Planner(S, keep_in=S.poly, avoid_polys=[G.offset_polygon_radial(lk_poly, G.centroid(lk_poly), -2.5)]
                   if lk_poly else (), avoid_pts=hide)
    trail = next((p for p in lay.PATHS if p["id"] == "LookoutTrail"), None)
    tpl = path_polyline(trail) if trail else None
    objs = []
    rep = {}

    def hill_r(p):
        if hill is None:
            return 99.0
        d = V2(p) - HC
        rot = hill.get("rot", 0.0)
        cr, sr = math.cos(-rot), math.sin(-rot)
        lx, ly = d.x * cr - d.y * sr, d.x * sr + d.y * cr
        sx, sy = hill.get("squash", (1.0, 1.0))
        return math.hypot(lx / sx, ly / sy)

    # ---------------------------------------------------------------- summit: cairn, flagpole, benches
    top = HC
    zt = S.ground_z(top.x, top.y)
    if tpl is not None:
        st, dtop = _closest_s(tpl, top)
        tp = tpl.pos(st)
        away = (top - tp).normalized() if (top - tp).length > 0.1 else Vector((1.0, 0.0))
        cairn = tp + away * max(4.5, (top - tp).length)
    else:
        cairn = top
    zc = zmin(S, cairn, 1.2)
    S.put("Rock_B", cairn.x, cairn.y, zc - 0.15, 0.4, scale=(1.5, 1.5, 1.3), sub=subc(S, "Summit"))
    S.put("Rock_A", cairn.x + 0.2, cairn.y - 0.1, zc + 0.55, 1.3, scale=(1.0, 1.0, 1.0), sub=subc(S, "Summit"))
    S.put("Rock_A", cairn.x - 0.1, cairn.y + 0.05, zc + 0.95, 2.2, scale=(0.6, 0.6, 0.7), sub=subc(S, "Summit"))
    fp = cairn + Vector((1.6, 1.0))
    town = (Vector((0.0, 30.0)) - top).normalized()
    objs.append(obj_at(S, "SummitFlag", flagpole_mb(5.2, "M_Awning_Yellow"), fp.x, fp.y, zmin(S, fp, 0.2) - 0.02,
                       face_rot(town), sub=subc(S, "Summit")))
    plan.occ.add(cairn, 2.0)
    nb_ = 0
    for k in range(40):
        if nb_ >= 2:
            break
        a = math.atan2(town.y, town.x) + math.radians((-1) ** k * (k // 2) * 9.0)
        b = cairn + Vector((math.cos(a), math.sin(a))) * 3.4
        if tpl is not None and (tpl.pos(_closest_s(tpl, b)[0]) - b).length < 3.0:
            continue
        if not plan.occ.free(b, 1.0) and nb_ > 0:
            continue
        plan.occ.add(b, 1.4)
        S.put("Bench", b.x, b.y, zmin(S, b, 0.9) - 0.03, face_rot(town), sub=subc(S, "Summit"))
        nb_ += 1
    rep["summit"] = (round(top.x, 1), round(top.y, 1), round(zt, 1))

    # ---------------------------------------------------------------- goat rocks (east flank outcrop)
    gr = HC + Vector((24.0, -4.0))
    for k in range(9):
        a = rng.uniform(0, TAU)
        rr = 4.5 * math.sqrt(rng.random())
        p = gr + Vector((math.cos(a), math.sin(a))) * rr
        if not plan.ok(p, r=0.8, road=2.0, path=1.5):
            continue
        s = rng.uniform(1.4, 2.8)
        plan.occ.add(p, 0.8 * s)
        S.put(rng.choice(["Rock_A", "Rock_B"]), p.x, p.y, zmin(S, p, 0.45 * s) - 0.12 * s, rng.uniform(0, TAU),
              scale=(s, s, s * rng.uniform(0.8, 1.2)), sub=subc(S, "Rocks"))

    # ---------------------------------------------------------------- trees: lower slopes + edges, hilltop open
    fol = [("M_Foliage", 5), ("M_Foliage_Dark", 3), ("M_Foliage_Light", 2), ("M_Foliage_Autumn", 0.6)]
    mix = [("Tree_Round_A", 3), ("Tree_Round_B", 3), ("Tree_Cone", 3)]
    x0, y0, x1, y1 = G.bbox(S.poly)
    nt = 0
    # a few clumps (shade / hiding) on the meadows round the hill, then sparse singles
    for c, rad, n in (((262, 322), 8.0, 6), ((322, 305), 7.0, 5), ((333, 196), 7.0, 5), ((252, 262), 6.0, 3),
                      ((318, 172), 6.0, 3), ((290, 330), 6.0, 4)):
        nt += len(plan.cluster(c, rad, n, min_d=4.6, fol_mix=fol, mix=mix))
    for _ in range(26):
        for _t in range(40):
            p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
            if hill_r(p) < 27.0:
                continue
            if max(abs(p.x), abs(p.y)) > 338.0:
                continue
            if not plan.ok(p, r=6.5, road=1.5, path=1.6):
                continue
            plan.tree(p, r=13.0, mix=mix, fol_mix=fol)
            nt += 1
            break
    rep["trees"] = nt
    # rocks + bushes everywhere (boulders for goats to hop on)
    rocks = plan.scatter([("Rock_A", 2), ("Rock_B", 2)], 30, S.poly, r=1.0, sub="Rocks", scale=(0.8, 2.4),
                         sink=0.15, road=1.0, path=0.8)
    bushes = plan.scatter([("Bush_A", 2), ("Bush_B", 2)], 22, S.poly, r=1.0, sub="Bushes",
                          recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage_Light"])},
                          extra_ok=lambda p: hill_r(p) > 12.0)
    rep["rocks"], rep["bushes"] = len(rocks), len(bushes)

    # ---------------------------------------------------------------- trail markers (outside the Lookout site)
    if tpl is not None:
        mmb = MeshBuilder()
        post = marker_post_mb("M_Awning_Blue")
        nm = 0
        s = 3.0
        k = 0
        while s < tpl.length - 1.0:
            p = tpl.pos(s)
            t = tpl.tangent(s)
            n = G.left_normal(t) * (1 if k % 2 == 0 else -1)
            q = p + n * 1.65
            if not (lk_poly and G.point_in_poly(q, G.offset_polygon_radial(lk_poly, G.centroid(lk_poly), -1.0))) \
                    and plan.road_ok(q, extra=0.3) and G.point_in_poly(q, S.poly):
                mmb.extend(post, xform(q.x - HC.x, q.y - HC.y, zmin(S, q, 0.15) - 0.01, face_rot(-n)))
                nm += 1
            s += 21.0
            k += 1
        end = tpl.pos(tpl.length - 1.2)
        tn = G.left_normal(tpl.tangent(tpl.length - 1.2))
        q = end + tn * 1.7
        mmb.extend(post, xform(q.x - HC.x, q.y - HC.y, zmin(S, q, 0.15) - 0.01, face_rot(-tn)))
        objs.append(S.mesh("TrailMarkers", mmb, sub=subc(S, "Trail"), loc=(HC.x, HC.y, 0.0)))
        rep["markers"] = nm + 1
    rep["custom_tris"] = tri_count(objs)
    return rep


# ------------------------------------------------------------------------------ Willow Woods
def _hash01(i, j, s=0):
    n = (i * 374761393 + j * 668265263 + s * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def _vnoise(x, y, s=0):
    """Smooth value noise in [0, 1] (unit lattice)."""
    i, j = math.floor(x), math.floor(y)
    fx, fy = x - i, y - j
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _hash01(i, j, s) + (_hash01(i + 1, j, s) - _hash01(i, j, s)) * fx
    b = _hash01(i, j + 1, s) + (_hash01(i + 1, j + 1, s) - _hash01(i, j + 1, s)) * fx
    return a + (b - a) * fy


def iso_fill(mb, x0, y0, cell, V, thr, zf, mat):
    """Marching-squares fill of the region V > thr on a regular grid (V[j][i] sampled at (x0 + i*cell,
    y0 + j*cell)). Each cell emits the convex clip of its square (CCW seen from +Z, normals up): full cells are
    plain quads, edge cells 3-6-gons with linearly interpolated corners (shared edge points weld)."""
    ny, nx = len(V) - 1, len(V[0]) - 1
    for j in range(ny):
        for i in range(nx):
            cs = ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))
            vals = [V[b][a] for a, b in cs]
            ins = [v > thr for v in vals]
            if not any(ins):
                continue
            pts = []
            for k in range(4):
                a, b = cs[k]
                a2, b2 = cs[(k + 1) % 4]
                p0 = (x0 + a * cell, y0 + b * cell)
                if ins[k]:
                    pts.append(p0)
                if ins[k] != ins[(k + 1) % 4]:
                    t = (thr - vals[k]) / (vals[(k + 1) % 4] - vals[k])
                    p1 = (x0 + a2 * cell, y0 + b2 * cell)
                    pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))
            NK._poly(mb, [(x, y, zf(x, y)) for x, y in pts], mat)


T_MOSS, T_DEEP = 0.75, 1.9          # forest-floor density thresholds (moss layer / deep-shade layer)


def _forest_floor(S, plan, clearings, tpl, trail_w, pond, cell=4.0):
    """Forest-floor ground read for Willow Woods (polish pass): the woods stood on the same bright lawn as the
    town. Tree density (gaussian splat of every trunk, sigma 4 m, broken up by value noise) is contoured
    (marching squares, 4 m cells) into two flat layers just above the grass:
      M_Hedge       'moss' under the woods          (z + 0.012)
      M_Foliage_Dark deep shade in the dense groves (z + 0.022)
    and the clearings get a lighter M_Grass meadow (z + 0.012) so they pop. The dark layers keep ~2-3 m off the
    WoodsTrail (a light verge either side), the clearings, the pond bank, roads / sidewalks / bulbs and the
    district edge; paths (z + 0.035) still draw on top. Returns (density fn, objs, report)."""
    x0, y0, x1, y1 = G.bbox(S.poly)
    P = S.poly
    sig2 = 2.0 * 4.0 ** 2
    buck = {}
    for t in plan.trees:
        buck.setdefault((int(math.floor(t[0] / 8.0)), int(math.floor(t[1] / 8.0))), []).append(t)

    def dens(p):
        i, j = int(math.floor(p[0] / 8.0)), int(math.floor(p[1] / 8.0))
        s = 0.0
        for di in (-2, -1, 0, 1, 2):
            for dj in (-2, -1, 0, 1, 2):
                for t in buck.get((i + di, j + dj), ()):
                    d2 = (t[0] - p[0]) ** 2 + (t[1] - p[1]) ** 2
                    if d2 < 144.0:
                        s += math.exp(-d2 / sig2)
        return s

    th = G.SegmentHash(cell=12.0)
    if tpl is not None:
        th.add_polyline(tpl.pts, trail_w / 2.0)
    river = S.river_hash

    def blockers(p, road_m, edge_m):
        """Penalty from hard limits (district edge, roads/sidewalks, bulbs, canal): linear ramps so the contour
        runs parallel to them instead of stair-stepping along the sample grid."""
        if not G.point_in_poly(p, P):
            return 50.0
        de = min(G.dist_point_seg(p, P[i], P[(i + 1) % len(P)]) for i in range(len(P)))
        pen = max(0.0, edge_m - de) * 3.0
        dr, _ = S.road_hash.nearest(p, max_d=12.0)
        pen += max(0.0, road_m - dr) * 3.0
        for c, rb in plan.bulbs:
            pen += max(0.0, road_m - ((p - c).length - rb)) * 3.0
        if river is not None:
            dw, _ = river.nearest(p, max_d=12.0)
            pen += max(0.0, road_m - dw) * 3.0
        return pen

    nx = int(math.ceil((x1 - x0) / cell))
    ny = int(math.ceil((y1 - y0) / cell))
    VD, VM, raw = [], [], []
    for j in range(ny + 1):
        rd, rm = [], []
        for i in range(nx + 1):
            p = Vector((x0 + i * cell, y0 + j * cell))
            hard = blockers(p, 2.5, 2.0)
            dp = dens(p)
            if hard < 50.0:
                raw.append(dp)
            v = dp * (0.7 + 0.6 * _vnoise(p.x / 13.0, p.y / 13.0, 3)) - hard
            dt = th.nearest(p, max_d=12.0)[0] if tpl is not None else 99.0
            v -= max(0.0, 2.6 - dt) * 2.5
            m = -9.0
            for c, r in clearings:
                d = (p - V2(c)).length
                v -= max(0.0, r + 2.5 - d) * 1.5
                m = max(m, r + 1.0 - d + 2.4 * (_vnoise(p.x / 5.0, p.y / 5.0, 7) - 0.5))
            if pond is not None:
                din = pond.depth_in(p)
                v -= max(0.0, din + 3.5) * 2.0
                m -= max(0.0, din + 1.6) * 3.0
            rd.append(v)
            rm.append(m - blockers(p, 1.0, 1.0) if m > -9.0 else m)
        VD.append(rd)
        VM.append(rm)
    zf = lambda lift: (lambda x, y: S.ground_z(x, y) + lift)
    mb = MeshBuilder()
    iso_fill(mb, x0, y0, cell, VD, T_MOSS, zf(0.012), "M_Hedge")
    iso_fill(mb, x0, y0, cell, VD, T_DEEP, zf(0.022), "M_Foliage_Dark")
    iso_fill(mb, x0, y0, cell, VM, 0.0, zf(0.012), "M_Grass")
    objs = [S.mesh("ForestFloor", mb, sub=subc(S, "Ground"))] if mb.faces else []
    raw.sort()
    flat = [v for row in VD for v in row]
    q = lambda f: round(raw[int(f * (len(raw) - 1))], 2) if raw else 0.0
    return dens, objs, dict(floor_tris=tri_count(objs), floor_dens_q=(q(0.25), q(0.5), q(0.75), q(0.9)),
                            floor_cover=(round(sum(v > T_MOSS for v in flat) / max(1, len(raw)), 2),
                                         round(sum(v > T_DEEP for v in flat) / max(1, len(raw)), 2)))


def _trunk_occ(plan, r_trunk=0.6):
    """Copy of the occupancy with every tree shrunk to its trunk, so understory (bushes, logs, stumps) can sit
    INSIDE the groves instead of only in the gaps between crowns."""
    tset = {(round(t[0], 3), round(t[1], 3)) for t in plan.trees}
    occ = Occ(plan.occ.cell)
    for lst in plan.occ.g.values():
        for (q, r) in lst:
            occ.add(q, r_trunk if (round(q[0], 3), round(q[1], 3)) in tset else r)
    return occ


def _willow_woods(S):
    rng = S.rng
    lay = S.layout
    pond = pond_by_id(lay, "BeaverPond")
    trail = next((p for p in lay.PATHS if p["id"] == "WoodsTrail"), None)
    tpl = path_polyline(trail) if trail else None
    hide = [(G.V(h["at"]), 4.0) for h in lay.HIDING_SPOTS if G.point_in_poly(G.V(h["at"]), S.poly)]
    head = tpl.pos(0.0) if tpl else Vector((-264.0, -224.0))
    clearings = [((-262.0, -283.0), 12.0), ((-318.0, -197.0), 10.0), ((-229.0, -252.0), 9.0),
                 ((-246.0, -328.0), 8.0), (tuple(head + Vector((0.0, -4.0))), 8.0)]
    plan = Planner(S, keep_in=S.poly, avoid_pts=hide)
    objs = []
    rep = {}

    def in_clearing(p):
        return any((V2(p) - V2(c)).length < r for c, r in clearings)

    # ---------------------------------------------------------------- trailhead: ranger board, bench, bin, post
    if tpl is not None:
        t0 = tpl.tangent(0.0)
        n0 = G.left_normal(t0)
        bp = head + t0 * 3.2 + n0 * 3.0
        objs.append(obj_at(S, "RangerBoard", notice_board_mb(roof="M_Roof_Green"), bp.x, bp.y, zmin(S, bp, 1.0) - 0.02,
                           face_rot(-n0), sub=subc(S, "Trailhead")))
        plan.occ.add(bp, 1.4)
        bb = head + t0 * 3.6 - n0 * 2.8
        plan.prop("Bench", bb, face_rot(n0), r=1.0, sub="Trailhead", force=True)
        plan.prop("TrashBin", bb + t0 * 1.5, face_rot(n0), r=0.4, sub="Trailhead", force=True)
        plan.prop("Lamp_Park", head + t0 * 0.6 + n0 * 2.0, 0.0, r=0.4, sub="Trailhead", force=True)

    # ---------------------------------------------------------------- Beaver Pond: lodge, reeds, rocks, stumps
    nmb = MeshBuilder()           # merged nature bits (logs + stumps), origin at the pond centre
    oc = pond.c if pond else G.centroid(S.poly)
    if pond is not None:
        wi = pond.water_inset()
        a_l = math.radians(-20.0)
        lp = pond.at(a_l, wi + 0.4)
        objs.append(obj_at(S, "BeaverLodge", beaver_lodge_mb(rng), lp.x, lp.y, -0.42, rng.uniform(0, TAU),
                           sub=subc(S, "Pond"), smooth=("M_Bark", "M_Dirt"), angle=55))
        plan.occ.add(lp, 3.0)
        rmb = MeshBuilder()
        rr = random.Random("woods-reeds")    # own stream: reed tweaks never reshuffle the rest of the layout
        nr = 0
        for (a_deg, span, n) in ((60, 40, 7), (120, 30, 6), (175, 40, 8), (240, 30, 5), (300, 20, 3)):
            for k in range(n):
                a = math.radians(a_deg + rr.uniform(-span / 2, span / 2))
                p = pond.at(a, rr.uniform(wi - 0.5, wi + 1.2))
                reed_clump(rmb, p.x - oc.x, p.y - oc.y, pond.bank_z(p), rr, h=rr.uniform(1.2, 1.8),
                           n=rr.randint(6, 9))
                nr += 1
        objs.append(obj_at(S, "Reeds", rmb, oc.x, oc.y, 0.0, 0.0, sub=subc(S, "Pond")))
        rep["reed_clumps"] = nr
        for a_deg in (40, 95, 150, 205, 265, 300):
            a = math.radians(a_deg + rng.uniform(-10, 10))
            p = pond.at(a, rng.uniform(-0.5, 1.0))
            s = rng.uniform(0.9, 1.8)
            S.put(rng.choice(["Rock_A", "Rock_B"]), p.x, p.y, pond.bank_z(p) - 0.12 * s, rng.uniform(0, TAU),
                  scale=(s, s, s * 0.85), sub=subc(S, "Pond"))
        # chewed stumps + a felled log reaching into the water (beaver work) near the lodge
        for da in (-28, -8, 14):
            a = a_l + math.radians(da)
            p = pond.at(a, -2.6 - rng.uniform(0, 1.5))
            stump_mb(nmb, p.x - oc.x, p.y - oc.y, zmin(S, p, 0.4), r=rng.uniform(0.22, 0.32), chewed=True)
            plan.occ.add(p, 0.8)
        a = a_l + math.radians(28)
        p_in = pond.at(a, wi + 1.2)
        p_out = pond.at(a + 0.08, -4.5)
        log_mb(nmb, (p_out.x - oc.x, p_out.y - oc.y, GZ + 0.18), (p_in.x - oc.x, p_in.y - oc.y, -0.45), 0.26, rng)
        plan.occ.add(p_out.lerp(p_in, 0.5), 2.0)

    # ---------------------------------------------------------------- boulders in the north "bear" clearing
    bc = V2(clearings[1][0])
    for k in range(5):
        a = TAU * k / 5 + rng.uniform(-0.3, 0.3)
        p = bc + Vector((math.cos(a), math.sin(a))) * rng.uniform(5.5, 8.0)
        s = rng.uniform(1.6, 2.6)
        if plan.ok(p, r=1.0, road=1.0, path=1.0):
            plan.occ.add(p, 0.9 * s)
            S.put(rng.choice(["Rock_A", "Rock_B"]), p.x, p.y, zmin(S, p, s * 0.6) - 0.2 * s, rng.uniform(0, TAU),
                  scale=(s, s, s * 0.9), sub=subc(S, "Rocks"))
    # picnic table in the east clearing
    plan.prop("PicnicTable", V2(clearings[2][0]) + Vector((1.0, 0.5)), 0.6, r=1.4, sub="Trailhead")

    # ---------------------------------------------------------------- the woods (dense, clustered, walkable)
    x0, y0, x1, y1 = G.bbox(S.poly)
    mix = [("Tree_Cone", 5), ("Tree_Round_B", 3), ("Tree_Round_A", 2)]
    fol = [("M_Foliage_Dark", 6), ("M_Foliage", 3), ("M_Foliage_Light", 1), ("M_Foliage_Autumn", 0.5)]
    edge_ok = lambda p: max(abs(p.x), abs(p.y)) <= 338.0
    nt = 0
    # clearing rims first: a ring of big round trees makes each clearing read as a "room"
    for c, r in clearings[:4]:
        c = V2(c)
        for k in range(7):
            a = TAU * k / 7 + rng.uniform(-0.25, 0.25)
            p = c + Vector((math.cos(a), math.sin(a))) * (r + rng.uniform(1.0, 2.5))
            if edge_ok(p) and plan.ok(p, r=2.4, road=2.0, path=1.6, pond=3.5):
                plan.tree(p, r=4.8, piece=rng.choice(["Tree_Round_B", "Tree_Round_B", "Tree_Round_A"]),
                          fol_mix=fol, scale=rng.uniform(1.1, 1.4))
                nt += 1
    # density field: seeded groves are denser, the spaces between them airier
    groves = [Vector(g) for g in ((-330, -230), (-300, -215), (-245, -195), (-215, -290), (-280, -330),
                                  (-330, -290), (-240, -282), (-315, -322))]

    def min_d(p):
        g = min((p - q).length for q in groves)
        return 4.1 if g < 14 else (5.6 if g < 26 else 7.4)

    for _ in range(900):
        for _t in range(12):
            p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
            if not edge_ok(p) or in_clearing(p):
                continue
            md = min_d(p)
            if not plan.ok(p, r=md / 2, road=2.0, path=1.6, pond=3.5):
                continue
            plan.tree(p, r=md, mix=mix, fol_mix=fol, scale=rng.uniform(0.9, 1.45))
            nt += 1
            break
    rep["trees"] = nt
    # clearing edges: a ring of round trees reads as a "room"
    under = plan.scatter([("Bush_A", 3), ("Bush_B", 3)], 80, S.poly, r=1.1, sub="Understory",
                         recolor_fn=lambda r: {"foliage": r.choice(["M_Foliage_Dark", "M_Foliage", "M_Hedge"])},
                         extra_ok=lambda p: not in_clearing(p) and max(abs(p.x), abs(p.y)) < 340)
    rocks = plan.scatter([("Rock_A", 3), ("Rock_B", 2)], 40, S.poly, r=0.9, sub="Rocks", scale=(0.7, 1.9), sink=0.15,
                         extra_ok=lambda p: max(abs(p.x), abs(p.y)) < 340)
    rep["bushes"], rep["rocks"] = len(under), len(rocks)
    # ---------------------------------------------------------------- forest floor + dense understory (polish)
    dens, fobjs, frep = _forest_floor(S, plan, clearings, tpl, trail["width"] if trail else 2.0, pond)
    objs += fobjs
    rep.update(frep)
    plan.occ = _trunk_occ(plan)          # trees shrink to their trunks: understory may now sit inside the groves

    def deep(p, lo=1.4):
        """Mostly inside the woods proper (with a little spill so it does not look masked)."""
        return dens(p) >= lo or rng.random() < 0.15

    ncl = nbu = 0
    for _ in range(220):
        if ncl >= 28:
            break
        p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
        if not edge_ok(p) or in_clearing(p) or dens(p) < 2.2:
            continue
        if not plan.ok(p, r=1.0, road=2.0, path=1.8, pond=2.5):
            continue
        k = 0
        for j in range(rng.randint(3, 5)):
            a = rng.uniform(0, TAU)
            q = p + Vector((math.cos(a), math.sin(a))) * (rng.uniform(0.9, 1.9) if j else 0.0)
            s_ = rng.uniform(0.75, 1.3)
            if not plan.ok(q, r=0.5 * s_, road=2.0, path=1.6, pond=2.5):
                continue
            plan.occ.add(q, 0.5 * s_)
            S.put(rng.choice(["Bush_A", "Bush_B", "Bush_B"]), q.x, q.y, zmin(S, q, 0.5 * s_) - 0.05, rng.uniform(0, TAU),
                  recolor={"foliage": rng.choice(["M_Foliage_Dark", "M_Foliage_Dark", "M_Hedge", "M_Foliage"])},
                  scale=(s_, s_, s_ * rng.uniform(0.85, 1.1)), sub=subc(S, "Understory"))
            k += 1
        if k:
            ncl += 1
            nbu += k
    rep["bush_clusters"], rep["cluster_bushes"] = ncl, nbu
    # fallen logs + stumps (mostly inside the groves)
    nl = ns = 0
    for _ in range(27):
        for _t in range(40):
            p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
            if in_clearing(p) or not deep(p):
                continue
            a = rng.uniform(0, TAU)
            L = rng.uniform(3.0, 5.5)
            d = Vector((math.cos(a), math.sin(a)))
            pa, pb = p - d * L / 2, p + d * L / 2
            if not all(plan.ok(q, r=0.6, road=1.5, path=1.0, pond=1.0) for q in (pa, p, pb)):
                continue
            if max(abs(p.x), abs(p.y)) > 336:
                continue
            r = rng.uniform(0.22, 0.36)
            log_mb(nmb, (pa.x - oc.x, pa.y - oc.y, S.ground_z(pa.x, pa.y) + r * 0.75),
                   (pb.x - oc.x, pb.y - oc.y, S.ground_z(pb.x, pb.y) + r * 0.7), r, rng)
            for q in (pa, p, pb):
                plan.occ.add(q, 0.8)
            nl += 1
            break
    for _ in range(30):
        for _t in range(30):
            p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
            if not deep(p, 1.0):
                continue
            if not plan.ok(p, r=0.6, road=1.5, path=0.8, pond=0.8) or max(abs(p.x), abs(p.y)) > 336:
                continue
            stump_mb(nmb, p.x - oc.x, p.y - oc.y, zmin(S, p, 0.45), r=rng.uniform(0.28, 0.45),
                     h=rng.uniform(0.35, 0.7))
            plan.occ.add(p, 0.7)
            ns += 1
            break
    objs.append(obj_at(S, "LogsStumps", nmb, oc.x, oc.y, 0.0, 0.0, sub=subc(S, "Logs"), smooth=(BARK,), angle=50))
    rep["logs"], rep["stumps"] = nl, ns

    # ---------------------------------------------------------------- trail markers (yellow band)
    if tpl is not None:
        mmb = MeshBuilder()
        post = marker_post_mb("M_Awning_Yellow")
        nm = 0
        s = 1.6
        k = 0
        while s < tpl.length - 0.5:
            p = tpl.pos(s)
            n = G.left_normal(tpl.tangent(s)) * (1 if k % 2 == 0 else -1)
            q = p + n * 1.5
            if plan.road_ok(q, extra=0.3):
                mmb.extend(post, xform(q.x - oc.x, q.y - oc.y, zmin(S, q, 0.15) - 0.01, face_rot(-n)))
                nm += 1
            s += 20.0 if s > 2 else 18.4
            k += 1
        q = tpl.pos(tpl.length - 0.4) + G.left_normal(tpl.tangent(tpl.length - 0.4)) * 1.5
        mmb.extend(post, xform(q.x - oc.x, q.y - oc.y, zmin(S, q, 0.15) - 0.01, 0.0))
        objs.append(S.mesh("TrailMarkers", mmb, sub=subc(S, "Trail"), loc=(oc.x, oc.y, 0.0)))
        rep["markers"] = nm + 1
    rep["custom_tris"] = tri_count(objs)
    return rep
