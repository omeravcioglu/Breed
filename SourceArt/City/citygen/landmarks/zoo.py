"""Willowbrook Zoo - the story's incident origin (Phase 4 landmark module, owner: "zoo").

Routing: ``build(S)`` for the LANDMARKS site "Zoo"; ``build_area(S)`` for the NO_BUILD pockets
ZooForecourt, ZooParking, ZooBackLot and ZooLanding (dispatch on S.id).

PLAN (world coordinates, metres; the site is ~193 x 152 m, gate on the chamfered SE edge)
------------------------------------------------------------------------------------------
Reading order from the street: the Zoo Boulevard vista (clock tower -> gate, axis (-0.49, 0.87))
ends on the HERO GATE; straight through the arch the eye lands on the entrance plaza palms and the
AVIARY DOME, which sits on the same axis 46 m inside. Everything else rings a single looping
visitor path so the zoo reads as "loop + themed pockets" from above.

  * PERIMETER   kit iron fence 2 m inside the site polygon (leaves a planting strip), brick pillars
                with stone caps + zoo-green pyramids every ~15 m and at every corner, bushes and a
                band of shade trees inside. Gaps: main gate (12.3 m), the incident breach on the
                south fence (15 m), a keeper gate on the east fence to the back lot (left open).
  * HERO GATE   (-143.3, 232.3) facing (0.49, -0.87): two brick towers with stone plinths, pyramid
                roofs (M_Zoo_Primary) and yellow finials, paw-print medallions, hanging banners;
                a green arch carrying an arched sign board ("WILLOWBROOK" + big yellow "ZOO" from
                the built-in font, "ZOO" on both faces) with a giraffe cut-out peeking over it;
                turnstile lanes left and right, the wide centre exit gate swung open (the crowd
                fled), two hazard barriers in front ("closed after the incident", centre passable).
  * ENTRANCE    round plaza (r 11) behind the gate: palm planter, benches, lamps, gift shop (kit
                'shop'); a short walk on the axis leads to the aviary door.
  * LOOP PATH   4 m M_Path loop: plaza -> south lawn -> west (penguins / big cats) -> north
                (elephants / savanna) -> east (reptile house) -> plaza; a 3 m cross path through the
                central Commons; spurs to the aviary and the big-cat terrace; a dirt keeper track
                along the inside of the south fence (the truck's route); lamps / benches / bins.
  * ENCLOSURES  (each a distinct ground colour / silhouette so they read from 100 m up)
      1 SAVANNA      N/NE, sand + dry-grass ground, 9 flat-crowned acacias (custom), rock kopje,
                     termite mound, watering hole, giraffe hay feeders on poles, zebra boma, rail
                     fence, GIRAFFE HOUSE (2-storey kit warehouse) and a raised giraffe-feeding
                     platform on the loop (hero vantage point, hide-under). Its east service gate
                     stands OPEN; hoof prints run down the service lane to the open back gate.
      2 ELEPHANTS    NW, dirt paddock with sand patches, a sand-banked pool with "hippo" rocks,
                     logs, hay, elephant house (5x4 kit warehouse, S12 roof), viewing deck.
      3 BIG CATS     W, raised dry-grass island with a stacked "lion rock" + den (custom) ringed by
                     a water moat and a visitor parapet; viewing terrace with benches on a spur.
                     (Intact: the lions did NOT get out.)
      4 MONKEY ISL.  centre-west, moat pool with a grassy island, palms, climbing frame and a
                     toppled palm log bridging the moat (how the monkeys got out).
      5 PENGUINS     SW, rock-and-ice pool with floes, igloo, glass viewing wall; its keeper gate
                     (south, toward the breach) stands OPEN with a beach ramp, buckets tipped.
      6 AVIARY       custom geodesic lattice dome on the boulevard axis, trees + pond inside,
                     vestibule with an "AVIARY" sign, escaped parrots perched on the cupola.
      7 PETTING ZOO  S, red kit barn + white picket paddock (gate OPEN), hutches, hay, trough,
                     goat hill.
      + REPTILE HOUSE (kit 'commercial', glass front, a big custom snake lying on the parapet) on
        the east path; food kiosks + cafe tables; keeper kiosks (kit sheds in zoo green);
        signposts (custom) at the junctions; keeper service yard inside the back gate.
  * THE INCIDENT (-235, 192), south fence facing Canal Street / Zoo Bridge: 15 m of fence gone,
    panels blown flat outward, one leaning, a pillar knocked over + a broken stump, a radial scorch
    star (M_Incident) with soot splashes and a dirt crater lip, a ~8 m stylized SMOKE COLUMN rising
    out of the crater (charcoal -> slate -> light grey puffs drifting east: the eye-level cue), a
    charred bare tree, a park lamp bent over by the blast, rubble fan, the zoo keeper truck on its
    side in zoo livery (green box, yellow cab, big yellow paws on the roof - which faces the street -
    and on the up-facing side panel), spilled crates / barrels, only ONE knocked-over barrier and ONE
    tipped cone (first responders just arrived - rows of barriers read as roadworks), stray cargo in
    the verge strip, trails of tipped props + paw / hoof prints from the open penguin and petting-zoo
    gates converging on the hole, and three ESCAPE TRAILS out of the hole across the grass verge to
    the Canal St sidewalk: sooty paws (toward the Zoo Bridge), a small herd's hooves (toward Zoo
    Corner) and webbed feet (toward the Zoo Landing reeds). Reads instantly: "something blew up here
    and the animals got out".
  * GAMEPLAY    the loop + commons + plaza + south lawn are wide open walkable space; hiding spots
    under the feeding platform, behind the barn, lion rock and kopje, in the aviary, between the
    back-lot sheds / hay and in the landing reeds; three ways in/out (gate, breach, back gate).

NO_BUILD pockets (build_area):
  * ZooForecourt  plaza paving with an accent carpet on the boulevard axis, ticket booths (kit
                  NewsStand in zoo colours), flag banners, planters, benches, the big map board.
  * ZooParking    lot paving with curbs, painted stalls, a few cars + the zoo shuttle van, lamps,
                  a "P" sign, parking meter, tree islands at the row ends.
  * ZooBackLot    feed shed (kit shed) + hay barn (kit warehouse, zoo green), round + square hay
                  bales (custom), the second keeper truck, crates / pallets / barrels / dumpster.
                  The bales between the barn and the truck are the ZooBackLot hiding spot.
  * ZooLanding    reedy meadow between Canal St and the water: dry-grass patches, ~65 reed tufts
                  (custom, 3 colours; full tufts in the hiding pocket, lean 6-blade tufts in tight
                  clumps elsewhere), wildflower tufts, a marsh pool with a small wooden dock,
                  rocks, willows, lifebuoy stands, benches, flamingo feathers, a tipped fish bucket
                  and a spilled zoo crate near the bridge head - where penguins and flamingos hide
                  (the ZooLandingReeds hiding spot sits in the densest reeds by the trail).

DELIBERATE SMALL EXTENSIONS beyond the polygons (connectors only, nothing on roads / sidewalks):
  * a 2.4 m paved strip between the ZooForecourt polygon and the gate threshold (the two polygons
    do not touch) and a 5 m accent walk from the forecourt down to the Zoo Boulevard sidewalk;
  * the parking driveway across the grass verge to the Zoo Parkway sidewalk (the lot polygon has
    no road frontage). Both stop at the sidewalk edge (their ends tuck under the 0.15 kerb).
  * the incident ESCAPE TRAILS: flat print decals (no geometry above 3 cm) across the ~10 m grass
    verge between the breach and the Canal St sidewalk; each trail stops 0.45 m short of the sidewalk
    edge (kerb_gap: exact distance to the road centerlines' hw + sidewalk).

FRAMEWORK NOTES / WORKAROUNDS
  * scene.coll() resolves every collection path part by its GLOBAL name, so a bare sub such as
    'Ground' / 'Furniture' landed in the first site that created it (LM_ZooLanding) and 'Trees' /
    'Vehicles' inside KIT_Library. _Ctx.sub() prefixes every sub collection with the site id
    (Zoo_Gate, ZooForecourt_Ground, ZooLanding_Trees, ...); every put / inst / tilted / mesh / path /
    patch goes through it.
  * Site.clear_of_roads samples every 2nd centerline point (chords on curves); the escape trails use
    kerb_gap(), the exact distance to the sidewalk outer edge, so they end a fixed 0.45 m short of it.
  * export_unity.py writes kit instances with rot_z only, so tilted kit pieces (fallen fence
    panels, the overturned truck, tipped barrels / crates / cones / lamp) are emitted as LM_ mesh
    COPIES (see _Ctx.tilted, one shared copy per piece + recolour) which export with their full
    transform in Env/Landmarks; their open kit bottoms / cut ends are capped (cap_holes).
  * The terrain is one flat grass plane at z = -0.05 without holes, so every water surface here
    sits above it (raised rims / banks) instead of using Site.pool() (whose water is at -0.45,
    i.e. under the grass).
  * Site.clear_of_roads (Network.clearance_hash) does not cover cul-de-sac bulbs: the back lot keeps 10.5 m off
    the Keeper's Lane bulb centre by hand.
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

from .. import config as C
from .. import facade as F
from .. import geom2d as G
from .. import kit as K
from .. import palette
from .. import scene
from ..assembler import BuildingSpec, H3, H4
from ..kit import nature as N
from ..meshutil import MeshBuilder

TAU = 2.0 * math.pi
GZ = C.GROUND_Z

# ------------------------------------------------------------------------------------ key points
GATE = Vector((-143.3, 232.3))
TAN = Vector((0.8713, 0.4908))      # along the gate fence (local +X of the site frame)
INW = Vector((-0.4908, 0.8713))     # into the zoo (local +Y)
FACE = -INW                         # out to Zoo Boulevard
PLAZA = GATE + INW * 16.0           # (-151.2, 246.2)
AVIARY = GATE + INW * 46.0          # (-165.9, 272.4)
MONKEY = Vector((-229.0, 268.0))
PENGUIN = Vector((-256.0, 227.0))
CATS = Vector((-294.0, 252.0))
BREACH = Vector((-235.0, 192.0))
BR_ALONG = Vector((0.9078, -0.4191))   # south fence direction at the breach (west -> east)
BR_IN = Vector((0.4191, 0.9078))       # into the zoo at the breach
SCORCH = BREACH + BR_IN * 4.0

ZOO_GREEN, ZOO_YELLOW = "M_Zoo_Primary", "M_Zoo_Accent"


def V2(x, y=None):
    if y is None:
        return Vector((float(x[0]), float(x[1])))
    return Vector((float(x), float(y)))


def gw(u, v):
    """Gate frame -> world (u along the fence, v into the zoo)."""
    return GATE + TAN * u + INW * v


def rot_front(d):
    """Z rotation so a kit piece's front (-Y) faces direction d."""
    return math.atan2(d[0], -d[1])


def rot_along(d):
    """Z rotation so a piece's local +X runs along d."""
    return math.atan2(d[1], d[0])


def tris_of(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def shade(me, smooth_mats, angle=45.0):
    names = [m.name for m in me.materials]
    flags = [names[p.material_index] in smooth_mats for p in me.polygons]
    if not any(flags):
        return
    me.set_sharp_from_angle(angle=math.radians(angle))
    me.polygons.foreach_set("use_smooth", flags)
    me.update()


def cap_holes(me):
    """Fill open boundary loops of a mesh copy (kit pieces omit hidden bottoms / cut ends) and orient
    each new face away from the mesh centre, so a tipped-over piece has no see-through holes."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    old = set(bm.faces)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    c = Vector((0.0, 0.0, 0.0))
    for v in bm.verts:
        c += v.co
    c /= max(1, len(bm.verts))
    for f in bm.faces:
        if f in old:
            continue
        f.normal_update()
        if (f.calc_center_median() - c).dot(f.normal) < 0:
            f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    me.update()


def merge_dup_slots(me):
    """Collapse material slots that ended up with the same material after a recolour / swap (one
    draw call per material in Unity)."""
    names = [m.name if m else "" for m in me.materials]
    first, remap = {}, []
    for i, n in enumerate(names):
        first.setdefault(n, i)
        remap.append(first[n])
    if all(r == i for i, r in enumerate(remap)):
        return
    keep = sorted(set(remap))
    newpos = {old: k for k, old in enumerate(keep)}
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)
    idx = [newpos[remap[i]] for i in idx]
    mats = [me.materials[i] for i in keep]
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", idx)
    me.update()


def decal(mb, pts2d, z, mat):
    """Flat polygon at height z with its normal up (any input winding)."""
    P = G.ensure_ccw([(p[0], p[1]) for p in pts2d])
    mb.face([Vector((p[0], p[1], z)) for p in P], mat)


def paw_shapes(c, d, s):
    """Paw print outlines at c pointing along unit d, ~0.84 s wide x 0.8 s long: pad + 4 toes."""
    d = V2(d).normalized()
    n = Vector((d.y, -d.x))
    r = rot_along(n)
    out = [blob_pts(c - d * (0.12 * s), 0.30 * s, 0.24 * s, seg=7, rot=r)]
    for ox, oy in ((-0.33, 0.16), (-0.12, 0.33), (0.12, 0.33), (0.33, 0.16)):
        out.append(blob_pts(c + n * (ox * s) + d * (oy * s), 0.09 * s, 0.115 * s, seg=5, rot=r))
    return out


def hoof_shapes(c, d, s):
    """Cloven hoof print: two narrow ovals side by side."""
    d = V2(d).normalized()
    n = Vector((d.y, -d.x))
    return [blob_pts(c + n * (side * 0.085 * s), 0.065 * s, 0.15 * s, seg=6, rot=rot_along(n)) for side in (-1, 1)]


def web_shapes(c, d, s):
    """Webbed (penguin / flamingo) foot: three toe triangles fanning from the heel."""
    d = V2(d).normalized()
    n = Vector((d.y, -d.x))
    heel = c - d * (0.12 * s)
    out = []
    for a in (-0.6, 0.0, 0.6):
        t = d * math.cos(a) + n * math.sin(a)
        tn = Vector((t.y, -t.x))
        tip = heel + t * (0.32 * s)
        out.append([heel + tn * (0.035 * s), tip, heel - tn * (0.035 * s)])
    return out


def kerb_gap(S, p, _cache={}):
    """Exact distance (m) from p to the nearest sidewalk outer edge, from the full road centerlines
    (hw + sidewalk); negative = on the sidewalk / road. (Site.clear_of_roads only answers yes / no
    against chords over every 2nd centerline point.)"""
    key = id(S.net)
    segs = _cache.get(key)
    if segs is None:
        segs = []
        for e in S.net.edges:
            pts = e.poly.pts
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                segs.append((a, b, e.hw + e.sw, min(a.x, b.x), max(a.x, b.x), min(a.y, b.y), max(a.y, b.y)))
        _cache.clear()
        _cache[key] = segs
    p = V2(p)
    best = 1e9
    for a, b, r, x0, x1, y0, y1 in segs:
        if p.x < x0 - r - 30 or p.x > x1 + r + 30 or p.y < y0 - r - 30 or p.y > y1 + r + 30:
            continue
        best = min(best, G.dist_point_seg(p, a, b) - r)
    return best


def plane_decal(mb, polys2d, origin, right, up, mat):
    """Flat polygons on an arbitrary plane: 2D (right, up) coords -> origin + right*x + up*y. The face
    normal is right x up (the side a viewer sees 'right' to the right and 'up' up)."""
    for poly in polys2d:
        P = G.ensure_ccw([(p[0], p[1]) for p in poly])
        mb.face([origin + right * p[0] + up * p[1] for p in P], mat)


# smoke greys per level (main puff / side puff): the side puffs blend each colour step into the next
SMOKE_MATS = ["M_Incident", "M_Incident", "M_Wall_Slate", "M_Wall_Slate", "M_Wall_Slate", "M_Wall_Concrete",
              "M_Wall_Concrete", "M_Wall_Concrete"]
SMOKE_SIDE = ["M_Incident", "M_Wall_Slate", "M_Incident", "M_Wall_Slate", "M_Wall_Concrete", "M_Wall_Slate",
              "M_Wall_Concrete", "M_Wall_Concrete"]


def mb_smoke(seed=5, height=7.6, drift=(0.42, 0.12)):
    """Stylized low-poly smoke column rising from z = 0: clumped puffs that grow and drift with the
    wind, charcoal at the base -> slate -> light grey on top (palette greys). ~0.9k tris."""
    rnd = random.Random(seed)
    mb = MeshBuilder()
    dx, dy = drift
    levels = 8
    for k in range(levels):
        t = k / (levels - 1)
        z = 0.55 + t * (height - 1.9)
        r = 0.7 + 1.05 * t ** 0.8
        cx, cy = dx * z + rnd.uniform(-0.15, 0.15), dy * z + rnd.uniform(-0.15, 0.15)
        mat = SMOKE_MATS[k]
        N.blob(mb, (cx, cy, z), r, mat, seg=8, rings=4, sz=0.78, jit=0.12, seed=seed * 20 + k)
        if k % 2 == 1 or k == levels - 1:     # side puff for a clumpy silhouette
            a = rnd.uniform(0, TAU)
            off = r * 0.75
            N.blob(mb, (cx + math.cos(a) * off, cy + math.sin(a) * off, z + r * 0.25), r * 0.62, SMOKE_SIDE[k], seg=7,
                   rings=4, sz=0.8, jit=0.12, seed=seed * 20 + 50 + k)
    # a last thin wisp blown downwind off the top
    zt = 0.55 + height - 1.9
    N.blob(mb, (dx * zt + 1.9, dy * zt + 0.5, zt + 1.0), 0.9, "M_Wall_Concrete", seg=7, rings=4, sz=0.6, sx=1.5,
           jit=0.1, seed=seed * 20 + 99)
    return mb


def blob_pts(c, rx, ry, seg=24, jit=0.0, seed=0, rot=0.0):
    """Smooth organic closed outline (low-frequency radial wobble), CCW."""
    rnd = random.Random(seed)
    p1, p2, p3 = rnd.uniform(0, TAU), rnd.uniform(0, TAU), rnd.uniform(0, TAU)
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for i in range(seg):
        a = TAU * i / seg
        k = 1.0 + jit * (0.55 * math.sin(2 * a + p1) + 0.3 * math.sin(3 * a + p2) + 0.15 * math.sin(5 * a + p3))
        x, y = rx * math.cos(a) * k, ry * math.sin(a) * k
        out.append(Vector((c[0] + x * cr - y * sr, c[1] + x * sr + y * cr)))
    return out


def inset_poly(poly, d):
    """Mitred inward offset by d (positive = inward) of a simple polygon."""
    P = G.ensure_ccw([V2(p) for p in poly])
    n = len(P)
    out = []
    for i in range(n):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % n]
        a = (p1 - p0).normalized()
        b = (p2 - p1).normalized()
        na = Vector((-a.y, a.x))
        nb = Vector((-b.y, b.x))
        m = na + nb
        if m.length < 1e-6:
            m = na
        m.normalize()
        k = d / max(m.dot(na), 0.35)
        out.append(p1 + m * k)
    return out


def box_rot(mb, c, sx, sy, z0, z1, mat, rz=0.0, skip=("-z",)):
    sub = MeshBuilder()
    sub.box(-sx / 2, -sy / 2, z0, sx / 2, sy / 2, z1, mat, skip=skip)
    mb.extend(sub, Matrix.Translation((c[0], c[1], 0.0)) @ Matrix.Rotation(rz, 4, "Z"))


def pyramid(mb, cx, cy, z0, half, h, mat, rz=0.0, bottom=True):
    cr, sr = math.cos(rz), math.sin(rz)
    pts = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, y = sx * half, sy * half
        pts.append(Vector((cx + x * cr - y * sr, cy + x * sr + y * cr, z0)))
    apex = Vector((cx, cy, z0 + h))
    for i in range(4):
        mb.face([pts[i], pts[(i + 1) % 4], apex], mat)
    if bottom:
        mb.face(list(reversed(pts)), mat)


def disc_front(mb, cx, cz, r, y, depth, mat, seg=12):
    """Disc on a -Y facing facade: centre (cx, cz) at plane y, protruding toward -Y by depth."""
    sub = MeshBuilder()
    sub.cylinder(0.0, 0.0, 0.0, depth, r, mat, seg=seg, cap_top=True)
    mb.extend(sub, Matrix.Translation((cx, y, cz)) @ Matrix.Rotation(math.pi / 2, 4, "X"))


def ring_wall(mb, outer, inner, z0, z1, top_mat, out_mat, in_mat=None, in_z0=None, gap=None):
    """Closed ring wall between two equal-count CCW outlines. gap = set of segment indices to skip."""
    n = len(outer)
    in_mat = in_mat or out_mat
    iz0 = z0 if in_z0 is None else in_z0
    gap = gap or set()
    for i in range(n):
        if i in gap:
            continue
        j = (i + 1) % n
        a0, a1 = outer[i], outer[j]
        b0, b1 = inner[i], inner[j]
        mb.face([Vector((*a0, z1)), Vector((*a1, z1)), Vector((*b1, z1)), Vector((*b0, z1))], top_mat)
        mb.face([Vector((*a0, z0)), Vector((*a1, z0)), Vector((*a1, z1)), Vector((*a0, z1))], out_mat)
        mb.face([Vector((*b1, iz0)), Vector((*b0, iz0)), Vector((*b0, z1)), Vector((*b1, z1))], in_mat)
    if gap:
        for i in sorted(gap):   # end caps where the ring opens
            for k, sgn in ((i, 1), ((i + 1) % n, -1)):
                if (k - 1) % n in gap and sgn == 1:
                    continue
                if k in gap and sgn == -1:
                    continue
                a, b = outer[k], inner[k]
                quad = [Vector((*a, z0)), Vector((*b, iz0)), Vector((*b, z1)), Vector((*a, z1))]
                if sgn < 0:
                    quad = list(reversed(quad))
                mb.face(quad, out_mat)


# ================================================================================ shared context
class _Ctx:
    """Per-site helper: prototypes (shared custom meshes), tilted kit copies, keep-out bookkeeping."""

    def __init__(self, S):
        self.S = S
        self.protos = {}
        self.tilts = {}
        self.unique_tris = 0
        self.mesh_tris = 0
        self.heavy = {}
        self.by_key = {}
        self.inst_tris = 0
        self.inst_n = 0
        self.kit_n = 0
        self.blocks = []        # keep-out circles (center, r)
        self.polys = []         # keep-out polygons
        self.paths = []         # (sample points, half width)
        self.k = 0

    # ---------------------------------------------------------------- objects
    def sub(self, name):
        """Site-unique sub-collection name. FRAMEWORK WORKAROUND: scene.coll() resolves every path part
        by its GLOBAL collection name, so a bare 'Ground' / 'Furniture' would land in whichever site made
        it first (LM_ZooLanding) and 'Trees' / 'Vehicles' inside KIT_Library. Every sub is therefore
        prefixed with the site id (same idea as park.subc / service_yard.scoped / town_square.sub_path)."""
        if not name:
            return None
        pre = self.S.id + "_"
        return name if name.startswith(pre) else pre + name

    def mesh(self, name, mb, sub, smooth=None, angle=45.0, loc=(0.0, 0.0, 0.0), rot=0.0, weld=True):
        o = self.S.mesh(name, mb, sub=self.sub(sub), weld=weld, loc=loc)
        o.rotation_euler = (0.0, 0.0, rot)
        if smooth:
            shade(o.data, set(smooth), angle)
        t = tris_of(o.data)
        self.unique_tris += t
        self.mesh_tris += t
        self.heavy[name] = t
        return o

    def proto(self, key, fn, smooth=None, angle=45.0):
        me = self.protos.get(key)
        if me is None:
            mb = fn()
            me = mb.build(f"LM_{self.S.id}_P_{key}"[:63])
            if smooth:
                shade(me, set(smooth), angle)
            self.protos[key] = me
            self.unique_tris += tris_of(me)
            self.heavy["P_" + key] = tris_of(me)
        return me

    def inst(self, key, x, y, z=None, rot=0.0, sub="Props", scale=None, tilt=None, name=None):
        me = self.protos[key]
        if z is None:
            z = self.S.ground_z(x, y)
        self.k += 1
        nm = (name or f"LM_{self.S.id}_{key}_{self.k:03d}")[:63]
        o = scene.obj(nm, me, self.S.coll + "/" + self.sub(sub), (x, y, z), rot)
        if tilt:
            o.rotation_euler = (tilt[0], tilt[1], rot)
        if scale:
            o.scale = scale if hasattr(scale, "__len__") else (scale, scale, scale)
        self.inst_tris += tris_of(me)
        self.inst_n += 1
        self.by_key[key] = self.by_key.get(key, 0) + tris_of(me)
        return o

    def put(self, piece, x, y, z=None, rot=0.0, recolor=None, scale=None, sub="Props"):
        o = self.S.put(piece, x, y, z, rot, recolor=recolor, scale=scale, sub=self.sub(sub))
        if o is not None:
            self.kit_n += 1
        return o

    def tilted(self, piece, x, y, z, rx, ry, rz, recolor=None, sub="Incident", name=None, swap=None):
        """Kit piece with X/Y rotation as an LM_ mesh copy (instances.json only keeps rot_z).
        swap: {fixed kit material: palette material} for slots that are not recolour roles."""
        nm = piece if piece.startswith("KIT_") else "KIT_" + piece
        if not K.has(nm):
            return None
        key = nm[4:] + ("_" + "_".join(v[2:] for _, v in sorted(recolor.items())) if recolor else "")
        if swap:
            key += "_S" + "_".join(v[2:] for _, v in sorted(swap.items()))
        me = self.tilts.get(key)
        if me is None:
            src = K.get(nm).data
            me = src.copy()
            me.name = f"LM_{self.S.id}_Tilt_{key}"[:63]
            for i, m in enumerate(me.materials):
                mn = m.name if m else ""
                role = K.RECOLOR_SLOTS.get(mn)
                if recolor and role and role in recolor:
                    me.materials[i] = palette.get(recolor[role])
                elif swap and mn in swap:
                    me.materials[i] = palette.get(swap[mn])
            if recolor or swap:
                merge_dup_slots(me)
            if nm != "KIT_Truck_Box":
                cap_holes(me)
            self.tilts[key] = me
            self.unique_tris += tris_of(me)
            self.heavy["Tilt_" + key] = tris_of(me)
        self.k += 1
        o = scene.obj((name or f"LM_{self.S.id}_Tilted_{key}_{self.k:03d}")[:63], me,
                      self.S.coll + "/" + self.sub(sub), (x, y, z))
        o.rotation_euler = (rx, ry, rz)
        self.inst_tris += tris_of(me)
        self.by_key["Tilt_" + key] = self.by_key.get("Tilt_" + key, 0) + tris_of(me)
        return o

    # ---------------------------------------------------------------- keep-outs
    def block(self, c, r):
        self.blocks.append((V2(c), r))

    def block_poly(self, poly):
        self.polys.append([V2(p) for p in poly])

    def add_path(self, pts, width):
        spl, _ = G.catmull_rom([V2(p) for p in pts], step=2.0)
        self.paths.append((spl, width / 2))

    def free(self, p, r=1.0, path_pad=0.6):
        p = V2(p)
        for c, rr in self.blocks:
            if (p - c).length < rr + r:
                return False
        for poly in self.polys:
            if G.point_in_poly(p, poly):
                return False
            # distance to polygon edges
            for i in range(len(poly)):
                if G.dist_point_seg(p, poly[i], poly[(i + 1) % len(poly)]) < r:
                    return False
        for spl, hw in self.paths:
            for i in range(len(spl) - 1):
                if G.dist_point_seg(p, spl[i], spl[i + 1]) < hw + r + path_pad:
                    return False
        return True

    def path(self, name, pts, width, mat="M_Path", sub="Paths", keep=True):
        o = self.S.path_ribbon(name, pts, width=width, mat=mat, sub=self.sub(sub))
        self.unique_tris += tris_of(o.data)
        self.mesh_tris += tris_of(o.data)
        if keep:
            self.add_path(pts, width)
        return o

    def patch(self, name, poly, mat, z, sub="Ground", skirt=0.06):
        mb = MeshBuilder()
        P = G.ensure_ccw([V2(p) for p in poly])
        mb.prism(P, z - skirt, z, mat, mat)
        return self.mesh(name, mb, sub)

    def stats(self, extra=None):
        top = sorted(self.heavy.items(), key=lambda kv: -kv[1])[:8]
        d = dict(custom_tris_unique=self.unique_tris, custom_tris_rendered=self.mesh_tris + self.inst_tris,
                 proto_instances=self.inst_n, kit_instances=self.kit_n, heaviest=top,
                 instanced=sorted(self.by_key.items(), key=lambda kv: -kv[1])[:6])
        if extra:
            d.update(extra)
        return d


# ================================================================================ prototypes
def mb_pillar(h=2.3):
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -0.12, 0.5, 0.5, 0.42, "M_CanalStone", skip=())
    mb.box(-0.4, -0.4, 0.42, 0.4, 0.4, h, "M_Wall_Brick", skip=("-z", "+z"))
    mb.box(-0.53, -0.53, h, 0.53, 0.53, h + 0.22, "M_CanalStone", skip=())
    pyramid(mb, 0.0, 0.0, h + 0.22, 0.38, 0.44, ZOO_GREEN, bottom=False)
    return mb


def mb_pillar_stump():
    """Broken pillar: base + brick stub with a jagged, tilted break."""
    mb = MeshBuilder()
    mb.box(-0.5, -0.5, -0.12, 0.5, 0.5, 0.42, "M_CanalStone", skip=("-z",))
    tops = [(-0.4, -0.4, 1.35), (0.4, -0.4, 0.95), (0.4, 0.4, 1.55), (-0.4, 0.4, 1.15)]
    P = [Vector((x, y, 0.42)) for x, y, _ in tops]
    T = [Vector((x, y, z)) for x, y, z in tops]
    for i in range(4):
        j = (i + 1) % 4
        mb.face([P[i], P[j], T[j], T[i]], "M_Wall_Brick")
    mid = Vector((0.05, 0.0, 1.05))
    for i in range(4):
        mb.face([T[i], T[(i + 1) % 4], mid], "M_Incident" if i % 2 else "M_Wall_Brick")
    return mb


def mb_railpost():
    mb = MeshBuilder()
    mb.box(-0.09, -0.09, 0.0, 0.09, 0.09, 1.25, "M_Trim_Wood", skip=("-z", "+z"))
    pyramid(mb, 0.0, 0.0, 1.25, 0.09, 0.12, "M_Trim_Wood", bottom=False)
    return mb


def mb_railfence(L=3.0):
    """L m log-rail enclosure fence along X (post at -X end; a run end needs a RailPost). The long
    runs use L = 6 (one post + two open-ended rails per 6 m: half the tris of the 3 m module)."""
    mb = mb_railpost()
    mb.transform(Matrix.Translation((-L / 2, 0.0, 0.0)))
    for z0 in (0.5, 0.95):
        mb.box(-L / 2 + 0.09, -0.05, z0, L / 2 - 0.09, 0.05, z0 + 0.12, "M_Fence_Wood", skip=("-x", "+x"))
    return mb


def mb_acacia(seed):
    rnd = random.Random(seed)
    mb = MeshBuilder()
    lean = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4))
    N.lathe(mb, [(0.34, 0.0), (0.24, 0.4, 0, 0), (0.17, 2.4, lean[0] * 0.6, lean[1] * 0.6),
                 (0.12, 3.3, lean[0], lean[1])], "M_Bark", seg=6)
    top = Vector((lean[0], lean[1], 3.3))
    crowns = []
    for k in range(3):
        a = rnd.uniform(0, TAU) + k * TAU / 3
        L = rnd.uniform(1.3, 2.0)
        end = top + Vector((math.cos(a) * L, math.sin(a) * L, rnd.uniform(0.5, 1.1)))
        N.tube(mb, top - Vector((0, 0, 0.6)), end, 0.11, "M_Bark", seg=5, r1=0.07)
        crowns.append(end)
    for i, c in enumerate(crowns):
        N.blob(mb, (c.x, c.y, c.z + 0.25), rnd.uniform(1.6, 2.1), "M_Foliage", seg=8, rings=3, sz=0.3,
               jit=0.08, seed=seed * 10 + i)
    N.blob(mb, (top.x, top.y, top.z + 1.25), 2.3, "M_Foliage", seg=10, rings=4, sz=0.26, jit=0.06,
           seed=seed * 10 + 7)
    return mb


def mb_giraffe_feeder():
    """Tall hay basket on a pole (giraffes eat at ~4.5 m)."""
    mb = MeshBuilder()
    mb.cylinder(0.0, 0.0, 0.0, 4.6, 0.12, "M_Trim_Wood", seg=6, cap_top=True)
    N.lathe(mb, [(0.15, 4.0), (0.75, 4.35), (0.8, 4.95), (0.68, 4.95), (0.62, 4.45), (0.0, 4.2)], "M_Metal_Dark",
            seg=8)
    N.blob(mb, (0.0, 0.0, 4.95), 0.68, "M_Wall_Butter", seg=8, rings=4, sz=0.55, jit=0.12, seed=4)
    pyramid(mb, 0.0, 0.0, 5.55, 0.95, 0.55, ZOO_GREEN, rz=0.4)
    mb.cylinder(0.0, 0.0, 4.6, 5.56, 0.05, "M_Trim_Wood", seg=4, cap_top=False)
    return mb


def mb_flowers(seed):
    """Wildflower tuft: one leafy cushion + four little blossoms (lean: ~40 tris)."""
    rnd = random.Random(seed)
    mb = MeshBuilder()
    cols = ["M_Foliage_Blossom", "M_Awning_Yellow", "M_Wall_Lavender", "M_Trim_White"]
    N.blob(mb, (0.0, 0.0, 0.0), 0.42, "M_Foliage", seg=6, rings=2, sz=0.55, floor=0.0, jit=0.1, seed=seed)
    for k in range(4):
        a = TAU * k / 4 + rnd.uniform(-0.4, 0.4)
        x, y = 0.28 * math.cos(a), 0.28 * math.sin(a)
        z = rnd.uniform(0.22, 0.36)
        pyramid(mb, x, y, z, 0.07, 0.09, cols[(seed + k) % 4], rz=a, bottom=True)
    return mb


def mb_lifering():
    """Canal-side lifebuoy stand: post + backboard + orange/white ring facing -Y."""
    mb = MeshBuilder()
    mb.box(-0.06, -0.06, 0.0, 0.06, 0.06, 1.75, "M_Trim_Wood", skip=("-z",))
    mb.box(-0.42, -0.02, 0.7, 0.42, 0.06, 1.62, ZOO_GREEN, skip=())
    ring = []
    for i in range(10):
        a = TAU * i / 10
        ring.append(Vector((0.3 * math.cos(a), -0.1, 1.16 + 0.3 * math.sin(a))))
    for i in range(10):
        N.tube(mb, ring[i], ring[(i + 1) % 10], 0.075, "M_Hazard_Orange" if i % 5 < 3 else "M_Trim_White", seg=5,
               cap0=False, cap1=False)
    return mb


def mb_haybale():
    mb = MeshBuilder()
    sub = MeshBuilder()
    sub.cylinder(0.0, 0.0, -0.6, 0.6, 0.62, "M_Wall_Butter", seg=10, cap_top=True, cap_bottom=True,
                 mat_cap="M_Wood_Light")
    mb.extend(sub, Matrix.Translation((0, 0, 0.62)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    return mb


def mb_haysquare():
    mb = MeshBuilder()
    sub = MeshBuilder()
    sub.box(-0.55, -0.3, 0.0, 0.55, 0.3, 0.42, "M_Wall_Butter", skip=())     # closed: some lie tipped over
    mb.extend(F.bevelled(sub, 0.05))
    for x in (-0.25, 0.25):
        mb.box(x - 0.03, -0.31, 0.0, x + 0.03, 0.31, 0.43, "M_Trim_Wood", skip=("-z", "-x", "+x"))
    return mb


def mb_signpost():
    mb = MeshBuilder()
    mb.box(-0.07, -0.07, 0.0, 0.07, 0.07, 2.7, "M_Trim_Wood", skip=("-z",))
    pyramid(mb, 0.0, 0.0, 2.7, 0.1, 0.16, ZOO_GREEN, bottom=True)
    for i, (z, ang, L) in enumerate(((2.35, 0.3, 1.0), (1.95, 2.4, 0.95), (1.55, -1.2, 1.05))):
        sub = MeshBuilder()
        pts = [(0.05, -0.17), (L - 0.12, -0.17), (L, 0.0), (L - 0.12, 0.17), (0.05, 0.17)]
        N.xz_prism(sub, pts, -0.035, 0.035, ZOO_GREEN if i % 2 == 0 else ZOO_YELLOW)
        bar = MeshBuilder()
        bar.box(0.25, -0.04, -0.035, L - 0.25, 0.04, 0.035, "M_Sign_Face", skip=())
        sub.extend(bar, Matrix.Translation((0, -0.01, 0)) @ Matrix.Scale(1.0, 4))
        mb.extend(sub, Matrix.Translation((0, 0, z)) @ Matrix.Rotation(ang, 4, "Z"))
    return mb


def mb_flagpole(mat):
    mb = MeshBuilder()
    mb.cylinder(0.0, 0.0, 0.0, 6.6, 0.07, "M_Metal", seg=6, cap_top=True)
    mb.cylinder(0.0, 0.0, -0.05, 0.25, 0.16, "M_Metal_Dark", seg=6, cap_top=True)
    mb.sphere(0.0, 0.0, 6.75, 0.16, ZOO_YELLOW, seg=8, rings=4)
    mb.box(-0.03, -0.03, 6.25, 1.05, 0.03, 6.31, "M_Metal", skip=())
    pts = [(0.08, 6.25), (1.0, 6.25), (1.0, 3.6), (0.54, 3.95), (0.08, 3.6)]
    N.xz_prism(mb, pts, -0.03, 0.03, mat)
    stripe = [(0.08, 5.55), (1.0, 5.55), (1.0, 5.35), (0.08, 5.35)]
    other = ZOO_YELLOW if mat == ZOO_GREEN else ZOO_GREEN
    N.xz_prism(mb, stripe, -0.045, 0.045, other)
    return mb


def mb_turnstile():
    mb = MeshBuilder()
    body = MeshBuilder()
    body.box(-0.16, -0.5, 0.0, 0.16, 0.5, 1.0, "M_Metal_Dark", skip=("-z",))
    mb.extend(F.bevelled(body, 0.03))
    mb.box(-0.17, -0.52, 1.0, 0.17, 0.52, 1.06, ZOO_GREEN, skip=("-z",))
    hub = Vector((0.16, 0.0, 0.88))
    for a in (0.0, TAU / 3, 2 * TAU / 3):
        d = Vector((math.cos(math.radians(35)), math.cos(a) * 0.82, math.sin(a) * 0.82))
        N.tube(mb, hub, hub + d * 0.55, 0.025, "M_Metal", seg=4)
    return mb


def mb_lamp_post_sign():
    """Small 'P' parking sign on a post."""
    mb = MeshBuilder()
    mb.box(-0.05, -0.05, 0.0, 0.05, 0.05, 2.6, "M_Metal", skip=("-z",))
    mb.box(-0.45, -0.1, 2.0, 0.45, -0.05, 2.9, "M_Awning_Blue", skip=())
    # letter P (raised, white)
    P = [(-0.2, 2.15), (-0.08, 2.15), (-0.08, 2.4), (0.12, 2.4), (0.2, 2.5), (0.2, 2.65), (0.12, 2.75),
         (-0.2, 2.75)]
    N.xz_prism(mb, P, -0.13, -0.1, "M_Sign_Face")
    return mb


def mb_reed(seed, mat, blades=None, heads=2):
    """Reed tuft: 3-sided blades + cattail heads. Full tuft ~54 tris; lite (6 blades, 1 head) ~30."""
    rnd = random.Random(seed)
    mb = MeshBuilder()
    n = rnd.randint(9, 11)
    if blades:
        n = blades
    for i in range(n):
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(0.0, 0.35)
        bx, by = r * math.cos(a), r * math.sin(a)
        h = rnd.uniform(0.9, 1.75)
        lx, ly = math.cos(a) * rnd.uniform(0.1, 0.45), math.sin(a) * rnd.uniform(0.1, 0.45)
        w = 0.085
        base = [Vector((bx + w * math.cos(k * TAU / 3 + a), by + w * math.sin(k * TAU / 3 + a), 0.0))
                for k in range(3)]
        apex = Vector((bx + lx, by + ly, h))
        for k in range(3):
            mb.face([base[k], base[(k + 1) % 3], apex], mat)
        if i < heads:   # cattail head
            c = Vector((bx + lx * 0.85, by + ly * 0.85, h * 0.85))
            mb.cylinder(c.x, c.y, c.z - 0.16, c.z + 0.16, 0.06, "M_Bark", seg=4, cap_top=True,
                        cap_bottom=True)
    return mb


def mb_feather():
    mb = MeshBuilder()
    N.blob(mb, (0.0, 0.0, 0.05), 0.16, "M_Foliage_Blossom", seg=6, rings=3, sz=0.35, sx=1.8, seed=3)
    return mb


def mb_bucket():
    mb = MeshBuilder()
    N.lathe(mb, [(0.0, 0.0), (0.2, 0.0), (0.26, 0.45), (0.22, 0.45), (0.17, 0.05), (0.0, 0.05)],
            "M_Awning_Blue", seg=8)
    return mb


def mb_trough():
    mb = MeshBuilder()
    mb.box(-0.9, -0.3, 0.0, 0.9, 0.3, 0.45, "M_Fence_Wood", skip=("-z",))
    mb.box(-0.8, -0.2, 0.3, 0.8, 0.2, 0.455, "M_Water", skip=("-z", "-x", "+x", "-y", "+y"))
    return mb


def mb_bench_round(r_in, r_out, seg=12, z=0.45):
    """Ring bench around a planter (custom: circular)."""
    mb = MeshBuilder()
    outer = [(r_out * math.cos(TAU * i / seg), r_out * math.sin(TAU * i / seg)) for i in range(seg)]
    inner = [(r_in * math.cos(TAU * i / seg), r_in * math.sin(TAU * i / seg)) for i in range(seg)]
    ring_wall(mb, outer, inner, 0.0, z, "M_Wood_Light", "M_CanalStone")
    return mb


# ================================================================================ hero meshes
def _text_mb(text, height, depth, mat, offset=0.02):
    """Extruded block text from the built-in font, in the XZ plane facing -Y, centred at the origin,
    scaled so the glyph box is *height* tall."""
    cu = bpy.data.curves.new("__zoo_txt", "FONT")
    cu.body = text
    cu.size = 1.0
    cu.extrude = depth / 2
    cu.offset = offset
    cu.resolution_u = 3
    cu.align_x = "CENTER"
    cu.fill_mode = "BOTH"
    ob = bpy.data.objects.new("__zoo_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    pts = [v.co.copy() for v in me.vertices]
    mb = MeshBuilder()
    if pts:
        x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
        y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
        s = height / max(y1 - y0, 1e-6)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for poly in me.polygons:
            vs = []
            for i in poly.vertices:
                p = me.vertices[i].co
                # XY text (front +Z) -> XZ plane facing -Y
                vs.append(Vector(((p.x - cx) * s, -p.z * (depth / (2 * cu.extrude)), (p.y - cy) * s)))
            mb.face(vs, mat)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bpy.data.meshes.remove(me)
    return mb


GIRAFFE = [(0.10, 0.0), (0.27, 0.0), (0.30, 1.25), (1.22, 1.25), (1.28, 0.0), (1.45, 0.0), (1.50, 1.35),
           (1.72, 1.55), (1.98, 1.28), (2.06, 1.33), (1.80, 1.76), (1.56, 1.86), (0.48, 1.95), (0.14, 3.02),
           (0.16, 3.28), (0.08, 3.44), (0.02, 3.30), (-0.06, 3.40), (-0.13, 3.29), (-0.24, 3.24),
           (-0.70, 3.02), (-0.72, 2.92), (-0.30, 2.86), (-0.12, 2.73), (0.04, 1.66), (0.10, 1.40)]
GIRAFFE_SPOTS = [(0.55, 1.55, 0.18), (0.95, 1.6, 0.2), (1.3, 1.55, 0.16), (0.75, 1.35, 0.13),
                 (1.1, 1.38, 0.12), (0.22, 2.2, 0.1), (0.13, 2.65, 0.09), (0.32, 1.85, 0.1)]


def mb_giraffe(scale=1.45, thick=0.22):
    mb = MeshBuilder()
    pts = [(x * scale, z * scale) for x, z in GIRAFFE]
    N.xz_prism(mb, pts, -thick / 2, thick / 2, ZOO_YELLOW)
    for x, z, r in GIRAFFE_SPOTS:
        for side in (-1, 1):
            q = [(x * scale + r * scale * math.cos(TAU * k / 6 + 0.3) * 1.2,
                  z * scale + r * scale * math.sin(TAU * k / 6 + 0.3)) for k in range(6)]
            y = side * (thick / 2 + 0.012)
            vs = [Vector((qx, y, qz)) for qx, qz in q]
            if side < 0:
                mb.face(vs, "M_Bark")          # CCW in XZ seen from -Y
            else:
                mb.face(list(reversed(vs)), "M_Bark")
    return mb


def build_gate_mesh(Z):
    """Hero entrance (gate frame: x = u along the fence, y = v into the zoo, z up)."""
    S = Z.S
    st = MeshBuilder()
    for uc in (-5.0, 5.0):
        vc = 1.2
        blk = MeshBuilder()
        blk.box(uc - 1.4, vc - 1.4, -0.12, uc + 1.4, vc + 1.4, 0.95, "M_CanalStone", skip=("-z",))
        blk.box(uc - 1.28, vc - 1.28, 4.0, uc + 1.28, vc + 1.28, 4.32, "M_CanalStone", skip=())
        blk.box(uc - 1.45, vc - 1.45, 6.8, uc + 1.45, vc + 1.45, 7.22, "M_CanalStone", skip=())
        st.extend(F.bevelled(blk, 0.05))
        st.box(uc - 1.15, vc - 1.15, 0.95, uc + 1.15, vc + 1.15, 6.8, "M_Wall_Brick", skip=("-z", "+z"))
        pyramid(st, uc, vc, 7.22, 1.55, 1.75, ZOO_GREEN)
        st.cylinder(uc, vc, 8.85, 9.15, 0.07, "M_Metal", seg=6, cap_top=False)
        st.sphere(uc, vc, 9.35, 0.3, ZOO_YELLOW, seg=10, rings=6)
        # paw-print medallions, front (-y) and back (+y)
        for face_y, sgn in ((vc - 1.15, 1), (vc + 1.15, -1)):
            m = MeshBuilder()
            disc_front(m, 0.0, 0.0, 0.78, 0.0, 0.08, ZOO_YELLOW, seg=14)
            disc_front(m, 0.0, -0.12, 0.27, -0.08, 0.05, ZOO_GREEN, seg=10)
            for tx, tz in ((-0.3, 0.2), (-0.11, 0.36), (0.11, 0.36), (0.3, 0.2)):
                disc_front(m, tx, tz, 0.1, -0.08, 0.05, ZOO_GREEN, seg=8)
            M = Matrix.Translation((uc, face_y, 5.45))
            if sgn < 0:
                M = M @ Matrix.Rotation(math.pi, 4, "Z")
            st.extend(m, M)
        # hanging banners on the tower fronts (street side)
        for side in (-1, 1):
            bx = uc + side * 0.55
            ban = [(bx - 0.36, 6.55), (bx + 0.36, 6.55), (bx + 0.36, 3.3), (bx, 3.0), (bx - 0.36, 3.3)]
            N.xz_prism(st, ban, vc - 1.15 - 0.07, vc - 1.15, ZOO_GREEN if side < 0 else ZOO_YELLOW)
    # arch beam
    def z_top(u):
        return 5.15 + 1.1 * math.cos(math.pi / 2 * max(-1.0, min(1.0, u / 3.85)))
    us = [-3.85 + 7.7 * i / 12 for i in range(13)]
    prof = [(u, z_top(u) - 0.75) for u in us] + [(u, z_top(u)) for u in reversed(us)]
    N.xz_prism(st, prof, 0.55, 1.85, ZOO_GREEN)
    trim = [(u, z_top(u) - 0.78) for u in us] + [(u, z_top(u) - 0.6) for u in reversed(us)]
    N.xz_prism(st, trim, 0.5, 1.9, ZOO_YELLOW, front=True, back=True)
    # threshold slab
    st.box(-3.85, -2.4, -0.1, 3.85, 2.6, 0.15, "M_Plaza_Accent", skip=("-z",))
    gate = Z.mesh("Gate", st, "Gate", loc=(GATE.x, GATE.y, GZ), rot=S.rot)

    # ---- sign board + lettering + giraffe
    sg = MeshBuilder()
    W2 = 3.7
    usb = [-W2 + 2 * W2 * i / 14 for i in range(15)]
    board = [(u, z_top(u) - 0.1) for u in usb] + [(u, 8.7 + 0.6 * math.cos(math.pi / 2 * u / W2))
                                                   for u in reversed(usb)]
    N.xz_prism(sg, board, 1.0, 1.4, ZOO_GREEN)
    W3 = 3.86
    usb3 = [-W3 + 2 * W3 * i / 14 for i in range(15)]
    back = [(u, z_top(u) - 0.2) for u in usb3] + [(u, 8.92 + 0.62 * math.cos(math.pi / 2 * u / W3))
                                                  for u in reversed(usb3)]
    N.xz_prism(sg, back, 1.05, 1.35, ZOO_YELLOW)
    for side in (-1, 1):
        y_face = 1.0 if side < 0 else 1.4
        zoo = _text_mb("ZOO", 1.62, 0.2, ZOO_YELLOW, offset=0.035)
        items = [(zoo, 7.15)]
        if side < 0:
            items.append((_text_mb("WILLOWBROOK", 0.46, 0.12, "M_Sign_Face", offset=0.012), 8.47))
        for mbt, zc in items:
            if side < 0:
                M = Matrix.Translation((0.0, y_face - 0.1, zc))
            else:
                M = Matrix.Translation((0.0, y_face + 0.1, zc)) @ Matrix.Rotation(math.pi, 4, "Z")
            sg.extend(mbt, M)
    gir = mb_giraffe(scale=1.75)
    sg.extend(gir, Matrix.Translation((0.05, 1.56, 5.85)))
    Z.mesh("GateSign", sg, "Gate", loc=(GATE.x, GATE.y, GZ), rot=S.rot)

    # ---- "closed" barriers placed after the incident (angled, centre lane stays passable)
    for u, a in ((-2.9, 0.25), (2.9, -0.25)):
        p = gw(u, -3.4)
        Z.put("Barrier", p.x, p.y, 0.11, S.rot + a, sub="Gate")
    # ---- turnstiles + open exit gate leaves
    Z.proto("Turnstile", mb_turnstile)
    for u in (-3.05, -1.95, 1.95, 3.05):
        p = gw(u, 1.2)
        Z.inst("Turnstile", p.x, p.y, 0.1, S.rot, sub="Gate")
    for side in (-1, 1):
        hinge = gw(side * 1.74, 1.9)
        ang = S.rot + (math.radians(-80) if side < 0 else math.radians(80) + math.pi)
        Z.put("Fence_Iron_3m", hinge.x + math.cos(ang) * 0.85, hinge.y + math.sin(ang) * 0.85, 0.1, ang,
              scale=(0.57, 1.0, 0.95), sub="Gate")
    return gate


def build_aviary(Z, c, R=11.0):
    mb = MeshBuilder()
    seg = 16
    ring0 = [(c.x + R * math.cos(TAU * i / seg), c.y + R * math.sin(TAU * i / seg)) for i in range(seg)]
    ringi = [(c.x + (R - 0.6) * math.cos(TAU * i / seg), c.y + (R - 0.6) * math.sin(TAU * i / seg))
             for i in range(seg)]
    ring_wall(mb, ring0, ringi, GZ, 0.65, "M_CanalStone", "M_CanalStone")
    z0 = 0.65
    elev = [0.0, 22.0, 44.0, 64.0, 80.0]
    rings = []
    for k, e in enumerate(elev):
        er = math.radians(e)
        rr = (R - 0.3) * math.cos(er)
        zz = z0 + (R - 0.3) * math.sin(er) * 1.02
        off = (k % 2) * 0.5
        rings.append([Vector((c.x + rr * math.cos(TAU * (i + off) / seg), c.y + rr * math.sin(TAU * (i + off) / seg),
                              zz)) for i in range(seg)])
    lat = MeshBuilder()
    r = 0.075
    for k, ring in enumerate(rings):
        if k > 0:
            for i in range(seg):
                N.tube(lat, ring[i], ring[(i + 1) % seg], r, "M_Zoo_Fence", seg=4, cap1=False)
        if k + 1 < len(rings):
            nxt = rings[k + 1]
            for i in range(seg):
                N.tube(lat, ring[i], nxt[i], r, "M_Zoo_Fence", seg=4, cap1=False)
                j = (i - 1) % seg if k % 2 == 0 else (i + 1) % seg
                N.tube(lat, ring[i], nxt[j], r, "M_Zoo_Fence", seg=4, cap1=False)
    top = rings[-1]
    topz = top[0].z
    for i in range(seg):
        N.tube(lat, top[i], Vector((c.x, c.y, z0 + (R - 0.3) * 1.02)), r, "M_Zoo_Fence", seg=4, cap1=False)
    mb.extend(lat)
    # cupola + finial
    capz = z0 + (R - 0.3) * 1.02
    N.lathe(mb, [(1.3, capz - 0.35), (1.25, capz + 0.1), (0.9, capz + 0.55), (0.0, capz + 0.75)], ZOO_GREEN,
            seg=10, cx=c.x, cy=c.y)
    mb.cylinder(c.x, c.y, capz - 0.4, capz - 0.34, 1.32, ZOO_GREEN, seg=10, cap_top=False, cap_bottom=True)
    mb.sphere(c.x, c.y, capz + 1.0, 0.32, ZOO_YELLOW, seg=10, rings=6)
    # entry vestibule toward the plaza (facing FACE)
    d = FACE
    ent = c + d * (R + 0.6)
    ves = MeshBuilder()
    ves.box(-1.7, -1.6, GZ, 1.7, 1.6, 3.1, ZOO_GREEN, skip=("-z",))
    ves.box(-1.9, -1.8, 3.1, 1.9, 1.8, 3.35, ZOO_YELLOW, skip=())
    ves.box(-0.8, -1.65, 0.05, 0.8, -1.6, 2.45, "M_Glass", skip=("+y",))
    ves.box(-1.45, -1.72, 2.55, 1.45, -1.6, 3.05, ZOO_YELLOW, skip=("+y",))
    txt = _text_mb("AVIARY", 0.32, 0.06, ZOO_GREEN, offset=0.01)
    ves.extend(txt, Matrix.Translation((0.0, -1.75, 2.8)))
    mb.extend(ves, Matrix.Translation((ent.x, ent.y, 0.0)) @ Matrix.Rotation(rot_front(d), 4, "Z"))
    o = Z.mesh("Aviary_Dome", mb, "Aviary", smooth={ZOO_YELLOW}, angle=60)
    # inside ground
    Z.patch("Aviary_Ground", blob_pts(c, R - 0.6, R - 0.6, seg=16), "M_Grass_Park", GZ + 0.02, sub="Aviary")
    return o


def build_lion_rock(Z, c):
    """Stacked, slightly tapered rock slabs (custom 'pride rock')."""
    mb = MeshBuilder()
    rnd = random.Random(77)
    tiers = [(Vector((0.0, 0.0)), 6.8, 5.4, 0.0, 3.0, 0.3), (Vector((-1.4, 1.2)), 4.8, 3.9, 3.0, 5.6, 1.1),
             (Vector((0.6, -0.2)), 3.8, 2.6, 5.6, 7.0, 2.2), (Vector((2.6, -1.4)), 3.0, 1.7, 7.0, 7.7, 0.6)]
    base_z = 0.9
    base_outline = None
    for k, (off, rx, ry, z0, z1, rot) in enumerate(tiers):
        out = blob_pts(c + off, rx, ry, seg=11, jit=0.18, seed=40 + k, rot=rot)
        top = blob_pts(c + off + Vector((0.3, -0.2)), rx * 0.86, ry * 0.86, seg=11, jit=0.18, seed=40 + k,
                       rot=rot)
        P = G.ensure_ccw(out)
        T = G.ensure_ccw(top)
        if k == 0:
            base_outline = P
        zt = [base_z + z1 + rnd.uniform(-0.15, 0.15) for _ in T]
        for i in range(len(P)):
            j = (i + 1) % len(P)
            mb.face([Vector((*P[i], base_z + z0 - 0.3)), Vector((*P[j], base_z + z0 - 0.3)),
                     Vector((*T[j], zt[j])), Vector((*T[i], zt[i]))], "M_Rock")
        ctr = G.centroid(T)
        zc = sum(zt) / len(zt) + 0.1
        for i in range(len(T)):
            j = (i + 1) % len(T)
            mb.face([Vector((*T[i], zt[i])), Vector((*T[j], zt[j])), Vector((ctr.x, ctr.y, zc))],
                    "M_Grass_Dry" if k == 0 else "M_Rock")
    # den opening (dark) on the east face
    dy = c.y - 1.0
    xs = []
    for i in range(len(base_outline)):
        a, b = base_outline[i], base_outline[(i + 1) % len(base_outline)]
        if (a.y - dy) * (b.y - dy) <= 0 and abs(b.y - a.y) > 1e-6:
            xs.append(a.x + (dy - a.y) / (b.y - a.y) * (b.x - a.x))
    den = Vector((max(xs) if xs else c.x + 6.0, dy))
    mb.face([Vector((den.x + 0.05, den.y - 1.2, base_z)), Vector((den.x + 0.05, den.y + 1.2, base_z)),
             Vector((den.x - 0.25, den.y + 0.7, base_z + 1.8)), Vector((den.x - 0.25, den.y - 0.7, base_z + 1.8))],
            "M_Incident")
    return Z.mesh("BigCats_LionRock", mb, "BigCats", smooth={"M_Rock"}, angle=35)


# ================================================================================ zoo builders
class Zoo(_Ctx):
    def __init__(self, S):
        super().__init__(S)
        self.fence_line = inset_poly(S.poly, 2.0)

    # ------------------------------------------------------------------ perimeter
    def perimeter(self):
        S = self.S
        P = self.fence_line + [self.fence_line[0]]
        pl = G.Polyline(P)
        self.pl = pl

        def proj(pt):
            best, bs = 1e9, 0.0
            for i in range(len(P) - 1):
                a, b = P[i], P[i + 1]
                ab = b - a
                t = max(0.0, min(1.0, (pt - a).dot(ab) / max(ab.length_squared, 1e-9)))
                q = a + ab * t
                d = (pt - q).length
                if d < best:
                    best, bs = d, pl.cum[i] + ab.length * t
            return bs

        sg = proj(gw(0, 2.0))
        sb = proj(BREACH + BR_IN * 2.0)
        sk = proj(V2(-127.6, 300.5))
        self.s_breach = sb
        cuts = [(sg - 6.15, sg + 6.15, "gate"), (sb - 7.5, sb + 7.5, "breach"), (sk - 2.7, sk + 2.7, "back")]
        cuts.sort()
        keep, s = [], 0.0
        for a, b, _ in cuts:
            keep.append((s, a))
            s = b
        keep.append((s, pl.length))
        self.fence_keep = keep
        Z = self
        Z.proto("Pillar", mb_pillar)
        Z.proto("PillarStump", mb_pillar_stump)
        n = 0
        for a, b in keep:
            n += self._fence_span(pl, a, b, "Fence_Iron_3m", "Perimeter")
        # pillars: corners + every ~15 m + run ends (except the gate towers / breach specials)
        spots = []
        for a, b in keep:
            L = b - a
            k = max(1, round(L / 15.0))
            for i in range(k + 1):
                spots.append(a + L * i / k)
        for i in range(1, len(P) - 1):
            spots.append(pl.cum[i])
        spots.sort()
        placed = []
        for s_ in spots:
            if any(abs(s_ - q) < 4.0 for q in placed):
                continue
            if abs(s_ - sg) < 8.0 or abs(s_ - sb) < 11.5:
                continue
            if any(a + 0.01 < s_ < b - 0.01 for a, b, _ in cuts):
                continue
            p = pl.pos(s_)
            t = pl.tangent(s_)
            placed.append(s_)
            self.inst("Pillar", p.x, p.y, GZ, rot_along(t), sub="Perimeter")
        # back (keeper) gate: chain-link leaves swung open into the zoo
        for side in (-1, 1):
            hs = sk + side * 2.6
            h = pl.pos(hs)
            t = pl.tangent(sk)
            self.inst("Pillar", h.x, h.y, GZ, rot_along(t), sub="Perimeter")
            inward = Vector((-t.y, t.x))
            ang = rot_along(inward)
            q = h + inward * 1.25 - t * side * 0.15
            self.put("Fence_Chain_3m", q.x, q.y, GZ, ang, scale=(0.82, 1.0, 1.0), sub="Perimeter")
        return n

    def _fence_span(self, pl, a, b, piece, sub, proto=None, unit=3.0):
        if b - a < 0.4:
            return 0
        # split at polyline vertices
        cuts = [a] + [c for c in pl.cum if a < c < b] + [b]
        n = 0
        for i in range(len(cuts) - 1):
            s0, s1 = cuts[i], cuts[i + 1]
            L = s1 - s0
            if L < 0.4:
                continue
            k = max(1, round(L / unit))
            p0, p1 = pl.pos(s0), pl.pos(s1)
            d = (p1 - p0).normalized()
            for j in range(k):
                m = p0 + (p1 - p0) * ((j + 0.5) / k)
                if proto:
                    self.inst(proto, m.x, m.y, GZ, rot_along(d), sub=sub, scale=(L / (unit * k), 1.0, 1.0))
                else:
                    self.put(piece, m.x, m.y, GZ, rot_along(d), scale=(L / (3.0 * k), 1.0, 1.0), sub=sub)
                n += 1
        return n

    def rail_fence(self, pts, sub, closed=False, gaps=()):
        """Custom log-rail fence along a polyline; gaps = [(s0, s1)] arc-length intervals.
        Lean 6 m modules (posts every ~6 m); a stub shorter than 4 m still gets one module."""
        self.proto("RailFence6", lambda: mb_railfence(6.0))
        self.proto("RailPost", mb_railpost)
        P = [V2(p) for p in pts] + ([V2(pts[0])] if closed else [])
        pl = G.Polyline(P)
        keep, s = [], 0.0
        for a, b in sorted(gaps):
            keep.append((s, a))
            s = b
        keep.append((s, pl.length))
        for a, b in keep:
            if b - a < 0.5:
                continue
            self._fence_span(pl, a, b, None, sub, proto="RailFence6", unit=6.0)
            e = pl.pos(b)
            self.inst("RailPost", e.x, e.y, GZ, 0.0, sub=sub)
        return pl

    # ------------------------------------------------------------------ gate + plaza
    def gate(self):
        build_gate_mesh(self)
        self.block(gw(-5.0, 1.2), 2.6)
        self.block(gw(5.0, 1.2), 2.6)

    def plaza(self):
        S = self.S
        c = PLAZA
        mb = MeshBuilder()
        disc = blob_pts(c, 11.0, 11.0, seg=28)
        mb.prism(disc, GZ - 0.05, 0.06, "M_Plaza", "M_Plaza_Accent")
        ring_o = blob_pts(c, 9.6, 9.6, seg=28)
        ring_i = blob_pts(c, 8.9, 8.9, seg=28)
        mb.tri_fill([ring_o, ring_i], 0.068, "M_Plaza_Accent")
        # connector from the gate threshold to the plaza
        rect = [gw(-3.85, 2.5), gw(3.85, 2.5), gw(3.85, 7.0), gw(-3.85, 7.0)]
        mb.prism(rect, GZ - 0.05, 0.059, "M_Plaza", "M_Plaza")
        self.mesh("Plaza", mb, "Plaza")
        # central palm planter
        pm = MeshBuilder()
        po = blob_pts(c, 3.4, 3.4, seg=16)
        pi_ = blob_pts(c, 2.95, 2.95, seg=16)
        ring_wall(pm, po, pi_, 0.0, 0.62, "M_CanalStone", "M_CanalStone", in_z0=0.45)
        pm.tri_fill([pi_], 0.48, "M_Dirt")
        self.mesh("Plaza_Planter", pm, "Plaza")
        for k, (dx, dy, a) in enumerate(((-0.9, 0.6, 0.5), (1.0, 0.4, 2.6), (0.0, -1.0, 4.4))):
            self.put("Tree_Palm", c.x + dx, c.y + dy, 0.48, a, recolor={"foliage": "M_Foliage"}, sub="Plaza",
                     scale=(1.0 + 0.12 * k,) * 3)
        for k in range(5):
            a = TAU * k / 5 + 0.3
            self.put("Bush_A", c.x + 2.2 * math.cos(a), c.y + 2.2 * math.sin(a), 0.48, a,
                     recolor={"foliage": "M_Foliage_Blossom" if k % 2 else "M_Foliage_Light"}, sub="Plaza")
        # benches facing the planter + lamps
        for k in range(6):
            a = TAU * k / 6 + 0.25
            p = c + Vector((math.cos(a), math.sin(a))) * 6.3
            if (p - gw(0, 7)).length < 3.5:
                continue
            self.put("Bench", p.x, p.y, 0.06, rot_front(-(p - c)) + math.pi, sub="Plaza")
        for k in range(4):
            a = TAU * k / 4 + 0.78
            p = c + Vector((math.cos(a), math.sin(a))) * 10.2
            self.put("Lamp_Park", p.x, p.y, 0.06, 0.0, sub="Plaza")
        self.block(c, 11.5)
        # gift shop on the east side of the plaza
        spec = BuildingSpec("shop", 3, 2, 1, dict(wall="M_Wall_Butter", trim="M_Trim_White", door="M_Door_Teal",
                                                 awning=ZOO_GREEN, roof="M_Roof_Green", sign=ZOO_YELLOW),
                            roof="flat", ground_h=H4, feats=dict(awning=True, door_i=1), seed=11, district="zoo")
        S.building(spec, (-138.3, 252.0), rot_front((-1.0, 0.0)), name="LM_Zoo_GiftShop")
        self.block_poly([(-139.5, 246.5), (-131.5, 246.5), (-131.5, 257.5), (-139.5, 257.5)])

    # ------------------------------------------------------------------ paths
    def walkways(self):
        E = PLAZA
        loop = [E, (-166, 243.5), (-185, 242.0), (-205, 243.0), (-228, 245.0), (-247, 247.5), (-260, 256.0),
                (-264, 270.0), (-259.5, 283.5), (-246, 290.0), (-222, 290.0), (-197, 289.0), (-172, 289.0),
                (-155, 286.5), (-147.5, 276.0), (-146.5, 263.0), E]
        self.path("Loop", loop, 4.0)
        self.path("CommonsWalk", [(-185, 242.0), (-189, 256), (-193.5, 272), (-197, 289.0)], 3.0)
        door = AVIARY + FACE * 12.6
        self.path("AviaryWalk", [E, E + INW * 6.0, door], 3.0)
        self.path("CatsSpur", [(-261.0, 259.5), (-266.0, 259.0), (-271.0, 258.5)], 3.0)
        # keeper track (dirt) along the south fence, through the breach
        self.track = [(-300, 222.5), (-281, 215.5), (-262, 210.0), (-246, 204.5), (-233.5, 199.0),
                      (-222, 197.5), (-211, 203.0), (-203, 205.8), (-190, 207.0)]
        self.path("KeeperTrack", self.track, 3.4, mat="M_Dirt")
        self.path("PenguinGateWalk", [(-252, 214.0), (-250, 209.0)], 2.2, mat="M_Dirt", keep=False)

    # ------------------------------------------------------------------ enclosures
    def aviary(self):
        build_aviary(self, AVIARY)
        self.block(AVIARY, 12.5)
        c = AVIARY
        self.put("Tree_Round_A", c.x - 3.5, c.y + 2.0, None, 0.4, recolor={"foliage": "M_Foliage_Dark"},
                 sub="Aviary", scale=(1.1, 1.1, 1.05))
        self.put("Tree_Palm", c.x + 3.0, c.y + 3.5, None, 3.9, sub="Aviary")
        self.put("Tree_Round_A", c.x + 1.5, c.y - 4.5, None, 2.0, recolor={"foliage": "M_Foliage_Light"},
                 sub="Aviary", scale=(0.85, 0.85, 0.8))
        self.put("Bush_B", c.x - 5.5, c.y - 3.0, None, 1.0, recolor={"foliage": "M_Foliage_Blossom"}, sub="Aviary")
        self.put("Bush_A", c.x + 6.0, c.y - 0.5, None, 2.0, sub="Aviary")
        pond = MeshBuilder()
        pp = blob_pts(c + Vector((-1.5, -3.5)), 2.6, 1.8, seg=12, jit=0.15, seed=5)
        pond.prism(pp, GZ, 0.04, "M_Water", "M_CanalStone")
        self.mesh("Aviary_Pond", pond, "Aviary")
        # escaped parrots perched on top of the dome
        mb = MeshBuilder()
        top = 0.65 + 10.7 * 1.02
        for k, (ang, rr, mat) in enumerate(((0.3, 1.6, "M_Awning_Red"), (2.2, 2.3, "M_Awning_Blue"),
                                             (4.0, 1.9, ZOO_YELLOW), (5.3, 2.6, "M_Awning_Red"))):
            x, y = c.x + rr * math.cos(ang), c.y + rr * math.sin(ang)
            z = 0.65 + math.sqrt(max(0.0, 10.7 ** 2 - rr ** 2)) * 1.02 + 0.22
            N.blob(mb, (x, y, z), 0.24, mat, seg=7, rings=4, sz=1.25, seed=k)
            N.blob(mb, (x, y, z + 0.32), 0.15, mat, seg=6, rings=4, seed=k + 9)
            mb.box(x - 0.04, y - 0.18, z + 0.28, x + 0.04, y - 0.1, z + 0.35, ZOO_YELLOW, skip=())
        self.mesh("Aviary_Parrots", mb, "Aviary", smooth={"M_Awning_Red", "M_Awning_Blue", ZOO_YELLOW})

    def monkey_island(self):
        c = MONKEY
        out = G.ensure_ccw(blob_pts(c, 15.0, 13.0, seg=30, jit=0.06, seed=3))
        inn = G.ensure_ccw(blob_pts(c, 14.3, 12.3, seg=30, jit=0.06, seed=3))
        mb = MeshBuilder()
        ring_wall(mb, out, inn, GZ - 0.05, 0.85, "M_CanalStone", "M_CanalStone", in_z0=0.2)
        mb.tri_fill([inn], 0.22, "M_Water")
        # island mound
        ic = c + Vector((0.8, 0.6))
        prof = [(7.2, 0.1, "M_Sand"), (6.3, 0.42, "M_Sand"), (5.3, 0.62, "M_Grass_Park"),
                (3.6, 1.45, "M_Grass_Park"), (1.8, 2.05, "M_Grass_Park")]
        seg = 16
        rings = []
        for r_, z_, _ in prof:
            pts = blob_pts(ic, r_, r_ * 0.9, seg=seg, jit=0.1, seed=8)
            rings.append([Vector((p.x, p.y, z_)) for p in pts])
        for k in range(len(rings) - 1):
            for i in range(seg):
                j = (i + 1) % seg
                mb.face([rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]], prof[k][2])
        mb.fan(ic, [Vector((p.x, p.y)) for p in rings[-1]], 2.2, "M_Grass_Park")
        # climbing frame: 3 log posts, platform, rope
        fc = ic + Vector((-1.2, 0.8))
        posts = [fc + Vector((math.cos(a), math.sin(a))) * 1.3 for a in (0.3, 2.4, 4.4)]
        for p in posts:
            mb.cylinder(p.x, p.y, 1.2, 5.6, 0.14, "M_Trim_Wood", seg=6, cap_top=True)
        tri = [Vector((p.x, p.y)) for p in posts]
        plat = MeshBuilder()
        plat.prism(tri, 4.0, 4.18, "M_Wood_Light", "M_Wood_Light", bottom="M_Wood_Light")
        mb.extend(plat)
        far = ic + Vector((4.2, -2.6))
        N.tube(mb, Vector((posts[0].x, posts[0].y, 4.9)), Vector((far.x, far.y, 0.8)), 0.05, "M_Wood_Light",
               seg=4)
        N.tube(mb, Vector((posts[1].x, posts[1].y, 5.2)), Vector((posts[2].x, posts[2].y, 5.2)), 0.05,
               "M_Wood_Light", seg=4)
        # a toppled palm log bridging the moat toward the south lawn: how the monkeys got out
        dv = (V2(-226.0, 245.0) - c).normalized()
        rim = max((p for p in out), key=lambda p: (p - c).normalized().dot(dv))
        a0 = ic + dv * 4.2
        a1 = rim + dv * 0.6
        N.tube(mb, Vector((a0.x, a0.y, 1.05)), Vector((a1.x, a1.y, 0.98)), 0.24, "M_Bark", seg=6, cap0=True,
               cap1=True)
        for k in range(3):
            fa = rot_along(dv) + math.pi + (k - 1) * 0.7
            tip = Vector((a0.x + math.cos(fa) * 1.6, a0.y + math.sin(fa) * 1.6, 0.75))
            N.tube(mb, Vector((a0.x, a0.y, 1.1)), tip, 0.12, "M_Foliage_Dark", seg=4, r1=0.03)
        self.mesh("MonkeyIsland", mb, "MonkeyIsland", smooth={"M_Grass_Park", "M_Sand", "M_Bark"}, angle=50)
        def mound_z(dx, dy):
            r = math.hypot(dx, dy / 0.9)
            pr = [(0.0, 2.2)] + [(r_, z_) for r_, z_, _ in reversed(prof)]
            for (r0, z0), (r1, z1) in zip(pr, pr[1:]):
                if r0 <= r <= r1:
                    return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
            return 0.1

        for k, (dx, dy, s) in enumerate(((2.2, 1.6, 1.15), (-2.6, -1.8, 1.0), (1.6, -2.9, 0.9))):
            self.put("Tree_Palm", ic.x + dx, ic.y + dy, mound_z(dx, dy) - 0.15, 1.3 + k * 2.1, sub="MonkeyIsland",
                     scale=(s, s, s), recolor={"foliage": "M_Foliage" if k != 1 else "M_Foliage_Light"})
        self.put("Rock_B", ic.x + 4.0, ic.y + 1.5, mound_z(4.0, 1.5) - 0.2, 0.7, sub="MonkeyIsland",
                 scale=(1.2, 1.2, 1.0))
        self.put("Rock_A", ic.x - 4.8, ic.y + 0.4, mound_z(-4.8, 0.4) - 0.15, 2.0, sub="MonkeyIsland")
        self.block_poly(blob_pts(c, 16.0, 14.0, seg=16, jit=0.06, seed=3))
        # visitor benches facing the pool
        for a in (3.6, 4.4, 5.2):
            p = c + Vector((math.cos(a) * 17.5, math.sin(a) * 15.5))
            self.put("Bench", p.x, p.y, None, rot_front(c - p), sub="MonkeyIsland")

    def penguins(self):
        c = PENGUIN
        n = 26
        out = G.ensure_ccw(blob_pts(c, 11.0, 8.5, seg=n, jit=0.07, seed=21))
        inn = G.ensure_ccw(blob_pts(c, 10.4, 7.9, seg=n, jit=0.07, seed=21))
        # keeper gate gap on the south side (toward the breach)
        gi = min(range(n), key=lambda i: (out[i] - (c + Vector((3.5, -9.0)))).length)
        gap = {gi, (gi + 1) % n}
        self.pg_gate = (out[gi] + out[(gi + 2) % n]) / 2
        mb = MeshBuilder()
        ring_wall(mb, out, inn, GZ - 0.05, 0.75, "M_Wall_White", "M_CanalStone", in_mat="M_Wall_White",
                  in_z0=0.25, gap=gap)
        mb.tri_fill([inn], 0.27, "M_Water")
        # pebble beach + ramp to the open gate
        beach = [inn[(gi + k) % n] for k in range(-3, 6)]
        bc = G.centroid(beach + [c + Vector((3.0, -3.5))])
        beach_poly = beach + [c + Vector((5.5, -3.2)), c + Vector((1.5, -3.6))]
        mb.prism(G.ensure_ccw(beach_poly), 0.1, 0.36, "M_Sand", "M_Sand")
        a, b = out[gi], out[(gi + 2) % n]
        dirv = (self.pg_gate - c).normalized()
        mb.face([Vector((*b, 0.36)), Vector((*a, 0.36)), Vector((*(a + dirv * 1.6), GZ + 0.02)),
                 Vector((*(b + dirv * 1.6), GZ + 0.02))], "M_Sand")
        # rocks / ice floes
        rk = MeshBuilder()
        for k, (dx, dy, r, h) in enumerate(((-4.0, 1.5, 2.2, 1.6), (-1.0, 3.2, 1.5, 1.1), (3.0, 2.0, 1.8, 1.3),
                                            (-6.5, -1.5, 1.4, 0.9))):
            N.blob(rk, (c.x + dx, c.y + dy, 0.2), r, "M_Rock", seg=8, rings=4, sz=h / r, jit=0.15, seed=30 + k,
                   floor=0.2)
            N.blob(rk, (c.x + dx - 0.2, c.y + dy + 0.1, 0.2 + h * 0.75), r * 0.55, "M_Wall_White", seg=7, rings=3,
                   sz=0.45, jit=0.1, seed=50 + k)
        for k, (dx, dy, r) in enumerate(((1.0, -0.8, 1.3), (5.5, 0.5, 1.0), (-2.5, -2.8, 0.9))):
            fl = blob_pts(c + Vector((dx, dy)), r * 1.3, r, seg=7, jit=0.2, seed=60 + k)
            rk.prism(fl, 0.15, 0.36, "M_Wall_White", "M_Wall_Sky")
        mb.extend(rk)
        ig = c + Vector((-1.2, -4.6))
        N.lathe(mb, [(1.7, 0.3), (1.6, 0.8), (1.25, 1.45), (0.65, 1.85), (0.0, 1.98)], "M_Wall_White", seg=10,
                cx=ig.x, cy=ig.y)
        dv = Vector((0.35, -1.0)).normalized()
        dp = ig + dv * 1.62
        nv = Vector((dv.y, -dv.x))
        q = [dp - nv * 0.45, dp + nv * 0.45]
        mb.face([Vector((*q[1], 0.32)), Vector((*q[0], 0.32)), Vector((*(dp - nv * 0.3 - dv * 0.25), 1.05)),
                 Vector((*(dp + nv * 0.3 - dv * 0.25), 1.05))], "M_Trim_Dark")
        # glass viewing wall on the visitor (north) side
        gl = MeshBuilder()
        for i in range(n):
            j = (i + 1) % n
            mid = (out[i] + out[j]) / 2
            if mid.y < c.y + 3.0 or i in gap:
                continue
            p0 = (out[i] + inn[i]) / 2
            p1 = (out[j] + inn[j]) / 2
            d = (p1 - p0)
            nrm = Vector((d.y, -d.x)).normalized() * 0.04
            q = [p0 - nrm, p1 - nrm, p1 + nrm, p0 + nrm]
            gl.prism(q, 0.75, 1.75, "M_Glass", "M_Glass")
            gl.cylinder(p0.x, p0.y, 0.75, 1.82, 0.06, "M_Metal_Dark", seg=4)
        mb.extend(gl)
        self.mesh("PenguinPool", mb, "Penguins", smooth={"M_Rock"}, angle=35)
        # open keeper gate leaf
        t = (b - a).normalized()
        hinge = a
        ang = rot_along(t) - math.radians(105)
        self.put("Fence_Iron_3m", hinge.x + math.cos(ang) * 0.85, hinge.y + math.sin(ang) * 0.85, GZ, ang,
                 scale=(0.57, 1.0, 0.75), sub="Penguins")
        self.block_poly(blob_pts(c, 12.0, 9.5, seg=16, jit=0.07, seed=21))
        # sign + bucket of fish knocked over at the gate
        self.proto("Bucket", mb_bucket)
        g = self.pg_gate + dirv * 2.5
        self.inst("Bucket", g.x, g.y, GZ + 0.26, 0.4, sub="Penguins", tilt=(math.pi / 2, 0.0))
        self.inst("Bucket", g.x + 1.7, g.y - 1.4, GZ, 1.4, sub="Penguins")

    def big_cats(self):
        c = CATS
        n = 30
        out = G.ensure_ccw(blob_pts(c, 19.0, 26.0, seg=n, jit=0.05, seed=12))
        out_i = G.ensure_ccw(blob_pts(c, 18.4, 25.4, seg=n, jit=0.05, seed=12))
        isl = G.ensure_ccw(blob_pts(c, 15.4, 22.4, seg=n, jit=0.05, seed=12))
        mb = MeshBuilder()
        ring_wall(mb, out, out_i, GZ - 0.05, 1.05, "M_CanalStone", "M_CanalStone", in_z0=0.02)
        mb.tri_fill([out_i, isl], 0.05, "M_Water_Deep")
        # island raised 0.9 with a rocky edge
        mb.wall(isl, 0.0, 0.9, "M_Rock", closed=True)
        mb.tri_fill([isl], 0.9, "M_Grass_Dry")
        self.mesh("BigCats_Moat", mb, "BigCats")
        build_lion_rock(self, c + Vector((-2.5, 3.0)))
        # island dressing
        for k, (dx, dy, piece, s, rot) in enumerate((
                (6.0, -10.0, "Rock_B", 1.8, 0.5), (-7.0, -12.0, "Rock_B", 1.4, 2.0), (8.0, 9.0, "Rock_B", 1.6, 4.0),
                (-9.0, 12.0, "Rock_A", 2.2, 1.0), (3.0, 15.0, "Rock_A", 1.8, 2.5), (9.5, -2.0, "Rock_A", 1.5, 5.0))):
            self.put(piece, c.x + dx, c.y + dy, 0.9, rot, scale=(s, s, s * 0.9), sub="BigCats")
        for dx, dy, piece, fol in ((-8.0, -6.0, "Tree_Round_B", "M_Foliage_Autumn"),
                                   (-6.0, 15.0, "Tree_Round_A", "M_Foliage_Light"),
                                   (4.0, -16.0, "Tree_Round_A", "M_Foliage")):
            self.put(piece, c.x + dx, c.y + dy, 0.9, dx, recolor={"foliage": fol}, sub="BigCats")
        log = MeshBuilder()
        N.tube(log, Vector((c.x + 2.0, c.y + 6.5, 1.15)), Vector((c.x + 7.5, c.y + 4.0, 1.05)), 0.32, "M_Bark",
               seg=7, cap0=True, cap1=True)
        N.tube(log, Vector((c.x + 5.0, c.y + 5.2, 1.3)), Vector((c.x + 6.0, c.y + 6.8, 2.2)), 0.12, "M_Bark",
               seg=5)
        self.mesh("BigCats_Log", log, "BigCats", smooth={"M_Bark"}, angle=50)
        self.block_poly(blob_pts(c, 20.0, 27.0, seg=16, jit=0.05, seed=12))
        # viewing terrace on the loop (east side of the moat)
        tc = c + Vector((20.5, 4.0))
        terr = [tc + Vector(v) for v in ((-1.8, -6.0), (4.0, -5.0), (5.0, 6.5), (-1.8, 7.0))]
        self.patch("BigCats_Terrace", terr, "M_Plaza", 0.0, sub="BigCats")
        for dy in (-3.0, 3.5):
            self.put("Bench", tc.x + 1.2, tc.y + dy, 0.0, rot_front((-1.0, 0.0)) + math.pi, sub="BigCats")
        self.put("Lamp_Park", tc.x + 3.6, tc.y - 4.0, 0.0, 0.0, sub="BigCats")

    def elephants(self):
        x0, x1, y0, y1 = -315.0, -248.0, 293.0, 335.0
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.patch("Elephants_Ground", poly, "M_Dirt", GZ + 0.02, sub="Elephants")
        for k, (cx, cy, rx, ry) in enumerate(((-292, 300, 9, 4), (-258, 326, 7, 5), (-300, 330, 8, 3.5))):
            self.patch(f"Elephants_Sand{k}", blob_pts((cx, cy), rx, ry, seg=14, jit=0.15, seed=70 + k), "M_Sand",
                       GZ + 0.03, sub="Elephants")
        pc = Vector((-268.0, 313.0))
        bank = G.ensure_ccw(blob_pts(pc, 10.5, 8.0, seg=22, jit=0.1, seed=33))
        water = G.ensure_ccw(blob_pts(pc, 8.8, 6.4, seg=22, jit=0.1, seed=33))
        mb = MeshBuilder()
        mb.tri_fill([bank, water], 0.06, "M_Sand")
        mb.wall(bank, GZ, 0.06, "M_Sand", closed=True)
        mb.tri_fill([water], 0.045, "M_Water")
        self.mesh("Elephants_Pool", mb, "Elephants")
        for dx, dy, s in ((3.0, 1.5, 1.4), (-2.5, -1.0, 1.1)):
            self.put("Rock_B", pc.x + dx, pc.y + dy, -0.25, dx, scale=(s, s, s * 0.7), sub="Elephants")
        spec = BuildingSpec("warehouse", 5, 4, 1, dict(wall="M_Wall_Peach", trim="M_Trim_White", door="M_Door_Wood",
                                                      awning="M_Awning_Red", roof="M_Roof_Terracotta",
                                                      sign=ZOO_YELLOW),
                            roof="gable_side", ground_h=H4, seed=21, district="zoo")
        self.S.building(spec, (-302.0, 316.0), rot_front((1.0, 0.0)), name="LM_Zoo_ElephantHouse")
        log = MeshBuilder()
        for (ax, ay, bx, by, r) in ((-285, 322, -279, 325, 0.38), (-290, 305, -287, 299, 0.32),
                                    (-252.5, 304, -253, 298, 0.3)):
            N.tube(log, Vector((ax, ay, GZ + r)), Vector((bx, by, GZ + r)), r, "M_Bark", seg=7, cap0=True,
                   cap1=True)
        self.mesh("Elephants_Logs", log, "Elephants", smooth={"M_Bark"}, angle=50)
        for (x, y, piece, s) in ((-280, 300.5, "Tree_Round_B", 1.15), (-256, 331, "Tree_Round_B", 1.0),
                                 (-308, 300, "Tree_Round_A", 1.1)):
            self.put(piece, x, y, None, x, recolor={"foliage": "M_Foliage"}, scale=(s, s, s), sub="Elephants")
        self.proto("HayBale", mb_haybale, smooth={"M_Wall_Butter"}, angle=50)
        for (x, y, r) in ((-296.5, 324.5, 0.2), (-296.0, 309.0, 1.4), (-294.5, 311.0, 1.1)):
            self.inst("HayBale", x, y, GZ, r, sub="Elephants")
        self.rail_fence([(x0 - 1.0, y0), (x1, y0), (x1, y1 + 1.0)], "Elephants")
        self.block_poly([(x0 - 1, y0 - 0.5), (x1 + 0.5, y0 - 0.5), (x1 + 0.5, y1 + 1), (x0 - 1, y1 + 1)])
        # viewing deck at the loop corner
        dc = Vector((-262.0, 290.6))
        self.patch("Elephants_Deck", [dc + Vector(v) for v in ((-6.0, -1.3), (6.0, -1.3), (6.0, 1.6), (-6.0, 1.6))],
                   "M_Wood_Light", 0.12, sub="Elephants")

    def savanna(self):
        S = self.S
        x0, x1, y0, y1 = -236.0, -143.5, 294.0, 335.5
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.patch("Savanna_Ground", poly, "M_Sand", GZ + 0.02, sub="Savanna")
        for k, (cx, cy, rx, ry, rot) in enumerate(((-215, 318, 16, 9, 0.3), (-178, 308, 14, 7, -0.2),
                                                   (-160, 326, 10, 6, 0.6), (-200, 301, 9, 4, 0.0),
                                                   (-226, 302, 7, 5, 0.9))):
            self.patch(f"Savanna_Grass{k}", blob_pts((cx, cy), rx, ry, seg=16, jit=0.2, seed=90 + k, rot=rot),
                       "M_Grass_Dry", GZ + 0.03, sub="Savanna")
        # watering hole
        wc = Vector((-196.0, 322.0))
        mb = MeshBuilder()
        bank = G.ensure_ccw(blob_pts(wc, 6.5, 4.6, seg=18, jit=0.12, seed=44))
        water = G.ensure_ccw(blob_pts(wc, 5.0, 3.3, seg=18, jit=0.12, seed=44))
        mb.tri_fill([bank, water], 0.07, "M_Dirt")
        mb.wall(bank, GZ, 0.07, "M_Dirt", closed=True)
        mb.tri_fill([water], 0.055, "M_Water")
        # termite mound
        N.lathe(mb, [(1.3, GZ), (1.0, 0.9), (0.55, 2.1), (0.25, 2.9), (0.0, 3.2)], "M_Dirt", seg=7,
                cx=-169.0, cy=318.0)
        N.lathe(mb, [(0.6, GZ), (0.4, 0.9), (0.0, 1.5)], "M_Dirt", seg=6, cx=-167.6, cy=318.9)
        self.mesh("Savanna_Features", mb, "Savanna", smooth={"M_Dirt"}, angle=60)
        # acacias
        for k in range(2):
            self.proto(f"Acacia{k}", lambda k=k: mb_acacia(5 + k * 3), smooth={"M_Foliage", "M_Bark"}, angle=55)
        for k, (x, y, s) in enumerate(((-226, 326, 1.45), (-206, 309, 1.3), (-183, 330, 1.55), (-160, 312, 1.25),
                                       (-151, 300, 1.05), (-215, 300, 1.0), (-172, 301, 1.15), (-139.5 - 9, 327, 1.3),
                                       (-232, 307, 1.1))):
            self.inst(f"Acacia{k % 2}", x, y, GZ, k * 1.7, sub="Savanna", scale=(s, s, s * 0.95))
        kop = MeshBuilder()
        for k, (dx, dy, r, h) in enumerate(((0.0, 0.0, 3.2, 2.6), (2.8, 1.2, 2.2, 1.8), (-2.4, 1.6, 2.0, 1.5),
                                            (0.9, -2.3, 1.7, 1.1), (4.6, -0.6, 1.2, 0.8))):
            N.blob(kop, (-165.0 + dx, 325.0 + dy, GZ), r, "M_Rock", seg=8, rings=4, sz=h / r, jit=0.16,
                   seed=120 + k, floor=GZ, sx=1.15)
        self.mesh("Savanna_Kopje", kop, "Savanna", smooth={"M_Rock"}, angle=32)
        self.proto("GiraffeFeeder", mb_giraffe_feeder, smooth={"M_Wall_Butter"}, angle=60)
        for (x, y, r) in ((-200.0, 312.0, 0.3), (-155.0, 320.0, 1.1)):
            self.inst("GiraffeFeeder", x, y, GZ, r, sub="Savanna")
        for k, (x, y, s) in enumerate(((-232, 331, 1.6), (-229, 333, 1.1), (-188, 313, 1.4), (-147, 330, 1.8))):
            self.put("Rock_B", x, y, None, k * 1.3, scale=(s, s, s), sub="Savanna")
        # zebra boma (open thatched shelter) - custom
        bc = Vector((-225.0, 314.0))
        bm = MeshBuilder()
        for dx, dy in ((-2.4, -1.8), (2.4, -1.8), (2.4, 1.8), (-2.4, 1.8)):
            bm.cylinder(bc.x + dx, bc.y + dy, GZ, 2.5, 0.12, "M_Trim_Wood", seg=6)
        pyramid(bm, bc.x, bc.y, 2.45, 3.4, 1.9, "M_Wall_Butter", rz=0.0)
        self.mesh("Savanna_Boma", bm, "Savanna")
        # giraffe house (tall kit warehouse) on the east side
        spec = BuildingSpec("warehouse", 4, 3, 2, dict(wall="M_Wall_Butter", trim="M_Trim_White", door="M_Door_Wood",
                                                      awning="M_Awning_Yellow", roof="M_Roof_Green", sign=ZOO_YELLOW),
                            roof="gable_side", ground_h=H4, seed=31, district="zoo")
        S.building(spec, (-142.0, 312.0), rot_front((-1.0, 0.0)), name="LM_Zoo_GiraffeHouse")
        # rail fence: south + west sides (feeding platform crosses the south side)
        pl = self.rail_fence([(x0, y1 + 0.5), (x0, y0), (x1, y0), (x1, 305.5)], "Savanna",
                             gaps=[(41.5 + 39.0, 41.5 + 46.0)])
        self.rail_fence([(x1, 318.5), (x1, y1 + 0.5)], "Savanna", gaps=[(3.0, 7.5)])
        hinge, dleaf = V2(x1, 321.5), V2(0.866, 0.5)     # gate leaf swung open toward the service lane
        cl = hinge + dleaf * 2.05
        self.proto("RailFence", mb_railfence)
        self.inst("RailFence", cl.x, cl.y, GZ, rot_along(dleaf), sub="Savanna", scale=(1.37, 1.0, 1.0))
        self.block_poly([(x0 - 0.5, y0 - 0.5), (x1 + 0.5, y0 - 0.5), (x1 + 0.5, y1 + 1), (x0 - 0.5, y1 + 1)])
        self.feeding_platform(Vector((-193.5, 293.6)))

    def feeding_platform(self, c):
        """Raised giraffe-feeding deck straddling the savanna fence (stairs down to the loop)."""
        mb = MeshBuilder()
        w, d, h = 7.0, 4.2, 3.6
        x0, x1, y0, y1 = c.x - w / 2, c.x + w / 2, c.y - 1.0, c.y + d - 1.0
        deck = MeshBuilder()
        deck.box(x0, y0, h - 0.25, x1, y1, h, "M_Wood_Light", skip=())
        mb.extend(F.bevelled(deck, 0.03))
        for px in (x0 + 0.25, c.x, x1 - 0.25):
            for py in (y0 + 0.25, y1 - 0.25):
                mb.box(px - 0.13, py - 0.13, GZ, px + 0.13, py + 0.13, h - 0.25, "M_Trim_Wood", skip=("-z", "+z"))
                mb.box(px - 0.08, py - 0.08, h, px + 0.08, py + 0.08, 6.4, "M_Trim_Wood", skip=("-z",))
        # railing (top rail + mid rail) on 3 sides (open where the stairs arrive, -y side, left part)
        for (ax, ay, bx, by) in ((x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1), (x0 + 2.2, y0, x1, y0)):
            for z in (h + 0.55, h + 1.05):
                N.tube(mb, Vector((ax, ay, z)), Vector((bx, by, z)), 0.05, "M_Trim_Wood", seg=4, cap0=True)
        # roof
        rf = MeshBuilder()
        rf.box(x0 - 0.6, y0 - 0.6, 6.4, x1 + 0.6, y1 + 0.6, 6.62, ZOO_YELLOW, skip=())
        mb.extend(F.bevelled(rf, 0.04))
        roof = [Vector((x0 - 0.6, y0 - 0.6, 6.62)), Vector((x1 + 0.6, y0 - 0.6, 6.62)),
                Vector((x1 + 0.6, y1 + 0.6, 6.62)), Vector((x0 - 0.6, y1 + 0.6, 6.62))]
        ridge_a = Vector((x0 + 1.2, (y0 + y1) / 2, 7.9))
        ridge_b = Vector((x1 - 1.2, (y0 + y1) / 2, 7.9))
        mb.face([roof[0], roof[1], ridge_b, ridge_a], ZOO_GREEN)
        mb.face([roof[2], roof[3], ridge_a, ridge_b], ZOO_GREEN)
        mb.face([roof[1], roof[2], ridge_b], ZOO_GREEN)
        mb.face([roof[3], roof[0], ridge_a], ZOO_GREEN)
        # straight stair flight running down from the deck edge toward -y (the loop path)
        steps = 9
        run = 4.2
        for i in range(steps):
            z = h - (i + 1) * h / steps
            yy0 = y0 - (i + 1) * run / steps
            mb.box(x0 + 0.2, yy0, z, x0 + 2.0, yy0 + run / steps + 0.02, z + 0.1, "M_Wood_Light", skip=())
        N.tube(mb, Vector((x0 + 0.2, y0, h + 0.9)), Vector((x0 + 0.2, y0 - run, 0.9)), 0.05, "M_Trim_Wood", seg=4,
               cap0=True)
        N.tube(mb, Vector((x0 + 2.0, y0, h + 0.9)), Vector((x0 + 2.0, y0 - run, 0.9)), 0.05, "M_Trim_Wood", seg=4,
               cap0=True)
        for sx in (x0 + 0.2, x0 + 2.0):
            mb.box(sx - 0.05, y0 - run - 0.05, GZ, sx + 0.05, y0 - run + 0.05, 0.95, "M_Trim_Wood", skip=("-z",))
        # sign on the roof edge
        mb.box(c.x - 1.6, y0 - 0.66, 5.7, c.x + 1.6, y0 - 0.6, 6.35, ZOO_GREEN, skip=("+y",))
        self.mesh("Savanna_FeedingDeck", mb, "Savanna")
        self.block_poly([(x0 - 0.5, y0 - run - 0.5), (x1 + 0.5, y0 - run - 0.5), (x1 + 0.5, y1 + 0.5),
                         (x0 - 0.5, y1 + 0.5)])

    def petting_zoo(self):
        S = self.S
        spec = BuildingSpec("warehouse", 3, 3, 1, dict(wall="M_Door_Red", trim="M_Trim_White", door="M_Door_Wood",
                                                      awning="M_Awning_Red", roof="M_Roof_Charcoal",
                                                      sign=ZOO_YELLOW),
                            roof="gable_front", ground_h=H4, seed=41, district="zoo")
        S.building(spec, (-200.0, 219.0), rot_front((0.0, 1.0)), name="LM_Zoo_PettingBarn")
        self.block_poly([(-205, 209.5), (-195, 209.5), (-195, 219.5), (-205, 219.5)])
        x0, x1, y0, y1 = -214.0, -182.0, 219.0, 236.0
        self.patch("Petting_Ground", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "M_Dirt", GZ + 0.02, sub="PettingZoo")
        self.patch("Petting_Straw", blob_pts((-200, 223.5), 4.2, 2.2, seg=12, jit=0.1, seed=4), "M_Grass_Dry",
                   GZ + 0.03, sub="PettingZoo")
        pts = [(-204.5, y0), (x0, y0), (x0, y1), (x1, y1), (x1, y0), (-195.5, y0)]
        pl = G.Polyline([V2(p) for p in pts])
        gate_s = 9.5 + 17.0 + 15.0   # north side, near x = -198
        keep = [(0.0, gate_s - 0.6), (gate_s + 0.6, pl.length)]
        for a, b in keep:
            self._fence_span(pl, a, b, "Fence_Picket_3m", "PettingZoo")
        g = pl.pos(gate_s - 0.6)
        self.put("Gate_Picket", g.x - 0.45, g.y - 0.55, GZ, math.radians(-75), sub="PettingZoo")   # swung open
        self.pz_gate = pl.pos(gate_s)
        # inside: hutches, hay, trough, goat mound
        self.proto("HayBale", mb_haybale, smooth={"M_Wall_Butter"}, angle=50)
        self.proto("HaySquare", mb_haysquare)
        self.proto("Trough", mb_trough)
        for (x, y, r) in ((-210.5, 222.0, 0.3), (-188.5, 221.5, 1.2)):
            self.inst("HayBale", x, y, GZ, r, sub="PettingZoo")
        for (x, y, r, z) in ((-207.5, 233.0, 0.1, GZ), (-206.6, 233.4, 0.2, GZ + 0.42), (-186.5, 233.5, 1.0, GZ)):
            self.inst("HaySquare", x, y, z, r, sub="PettingZoo")
        self.inst("Trough", -192.0, 227.5, GZ, 0.0, sub="PettingZoo")
        for (x, y, r) in ((-211.0, 229.0, 1.57), (-211.0, 226.5, 1.57)):
            self.put("Doghouse", x, y, None, r, recolor={"wall": "M_Wall_Cream", "roof": "M_Roof_Terracotta",
                                                         "trim": "M_Trim_White", "sign": ZOO_YELLOW}, sub="PettingZoo")
        mound = MeshBuilder()
        N.lathe(mound, [(2.4, GZ), (2.0, 0.55), (1.2, 1.1), (0.0, 1.3)], "M_Grass_Park", seg=10,
                cx=-188.0, cy=230.0)
        mound.box(-190.6, 229.6, 0.2, -186.0, 230.4, 0.32, "M_Wood_Light", skip=())
        self.mesh("Petting_GoatHill", mound, "PettingZoo", smooth={"M_Grass_Park"}, angle=60)
        self.put("Pallet", -196.5, 233.0, None, 0.2, sub="PettingZoo")
        self.block_poly([(x0 - 0.5, y0 - 0.5), (x1 + 0.5, y0 - 0.5), (x1 + 0.5, y1 + 0.5), (x0 - 0.5, y1 + 0.5)])

    def reptile_house(self):
        spec = BuildingSpec("commercial", 5, 3, 1, dict(wall="M_Wall_Sage", trim="M_Trim_White", door="M_Door_Teal",
                                                       awning="M_Awning_Teal", roof="M_Roof_Green",
                                                       sign=ZOO_YELLOW),
                            roof="flat", ground_h=H4, feats=dict(awning="flat", door_i=2), seed=51, district="zoo")
        self.S.building(spec, (-140.0, 273.5), rot_front((-1.0, 0.0)), name="LM_Zoo_ReptileHouse")
        self.block_poly([(-141.5, 265.5), (-130.5, 265.5), (-130.5, 281.5), (-141.5, 281.5)])
        # snake sign on the parapet (custom: wavy body + head)
        # a big snake lying along the parapet cap: tail hanging over the front, head rearing at the end
        mb = MeshBuilder()
        pts = [Vector((-140.62, 267.6, 4.35)), Vector((-140.55, 268.2, 4.8)), Vector((-140.25, 268.9, 5.12))]
        for i in range(12):
            t = i / 11
            pts.append(Vector((-140.0 - 0.28 * math.sin(t * TAU * 1.5), 269.8 + 8.4 * t, 5.17)))
        pts += [Vector((-140.2, 278.9, 5.35)), Vector((-140.4, 279.4, 5.75))]
        n_ = len(pts)
        for i in range(n_ - 1):
            r0 = 0.1 + 0.14 * min(1.0, i / 4.0)
            N.tube(mb, pts[i], pts[i + 1], r0, "M_Awning_Green", seg=6, cap0=True, cap1=True,
                   r1=0.1 + 0.14 * min(1.0, (i + 1) / 4.0))
        N.blob(mb, (pts[-1].x, pts[-1].y + 0.25, pts[-1].z + 0.05), 0.38, "M_Awning_Green", seg=8, rings=5, sx=0.8,
               sy=1.3, sz=0.75, seed=2)
        for side in (-1, 1):
            N.blob(mb, (pts[-1].x - 0.28, pts[-1].y + 0.32 + side * 0.17, pts[-1].z + 0.2), 0.08, ZOO_YELLOW, seg=6,
                   rings=4, seed=3)
        self.mesh("Reptile_SnakeSign", mb, "ReptileHouse", smooth={"M_Awning_Green"}, angle=70)

    def commons(self):
        """Central lawn: food kiosk, picnic tables, keeper kiosk, benches, signposts, lamps."""
        S = self.S
        self.put("NewsStand", -181.0, 263.0, None, rot_front((1.0, 0.0)),
                 recolor={"awning": ZOO_GREEN, "sign": ZOO_YELLOW}, sub="Commons")
        self.block((-181.0, 263.0), 2.5)
        for k, (x, y) in enumerate(((-205.5, 258.0), (-209.0, 262.5), (-204.0, 265.5), (-200.0, 279.0))):
            self.put("PicnicTable", x, y, None, 0.4 * k, sub="Commons")
            self.block((x, y), 1.5)
        for k, (x, y) in enumerate(((-176.0, 268.5), (-175.0, 259.5))):
            self.put("CafeTable", x, y, None, k, recolor={"awning": ZOO_GREEN}, sub="Commons")
            self.block((x, y), 1.5)
        # keeper kiosk (tiny kit shed in zoo colours)
        spec = BuildingSpec("shed", 1, 1, 1, dict(wall=ZOO_GREEN, trim=ZOO_YELLOW, door="M_Door_Wood",
                                                 awning="M_Awning_Green", roof="M_Roof_Green", sign=ZOO_YELLOW),
                            roof="flat", ground_h=H3, feats=dict(door_i=0), seed=61, district="zoo")
        S.building(spec, (-252.5, 263.0), rot_front((1.0, 0.0)), name="LM_Zoo_KeeperKiosk_W")
        self.block_poly([(-256.5, 260.5), (-252.0, 260.5), (-252.0, 265.5), (-256.5, 265.5)])
        spec2 = BuildingSpec("shed", 1, 1, 1, dict(wall=ZOO_GREEN, trim=ZOO_YELLOW, door="M_Door_Wood",
                                                  awning="M_Awning_Green", roof="M_Roof_Green", sign=ZOO_YELLOW),
                             roof="flat", ground_h=H3, feats=dict(door_i=0), seed=62, district="zoo")
        S.building(spec2, (-213.0, 284.0), rot_front((0.0, -1.0)), name="LM_Zoo_KeeperKiosk_N")
        self.block_poly([(-215.0, 283.5), (-211.0, 283.5), (-211.0, 287.5), (-215.0, 287.5)])
        # signposts at the main junctions
        self.proto("Signpost", mb_signpost)
        for (x, y, r) in ((-185.0, 239.0, 0.3), (-249.5, 251.5, 1.2), (-197.5, 292.6, 2.4), (-150.0, 283.5, 4.0),
                          (-160.5, 252.8, 5.2)):
            self.inst("Signpost", x, y, GZ, r, sub="Commons")
            self.block((x, y), 0.8)

    def path_dressing(self):
        """Park lamps, benches and bins along the loop."""
        spl, hw = self.paths[0]
        pl = G.Polyline(spl)
        s, k = 14.0, 0
        while s < pl.length - 12.0:
            p = pl.pos(s)
            nrm = G.left_normal(pl.tangent(s))
            for side in (1, -1):
                q = p + nrm * side * (hw + 0.9)
                if (q - PLAZA).length < 13.0:
                    continue
                if k % 3 == 0 and side == 1 and self.free(q, 0.4, path_pad=-0.6):
                    self.put("Lamp_Park", q.x, q.y, None, 0.0, sub="PathDressing")
                    self.block(q, 0.6)
                elif k % 3 == 1 and side == -1 and self.free(q, 0.9, path_pad=-0.6):
                    self.put("Bench", q.x, q.y, None, rot_front(nrm * -side), sub="PathDressing")
                    self.block(q, 1.0)
                    b = q + pl.tangent(s) * 1.5
                    self.put("TrashBin", b.x, b.y, None, 0.0, sub="PathDressing")
            s += 13.0
            k += 1

    def cafe(self):
        c = Vector((-171.0, 231.5))
        pat = blob_pts(c, 7.0, 4.8, seg=14, jit=0.05, seed=9, rot=0.55)
        self.patch("Cafe_Patio", pat, "M_Plaza", 0.0, sub="Cafe")
        self.put("NewsStand", c.x + 2.8, c.y - 2.2, 0.0, rot_front((-0.4, 1.0)),
                 recolor={"awning": "M_Awning_Yellow", "sign": ZOO_GREEN}, sub="Cafe")
        for k, (dx, dy) in enumerate(((-3.2, 0.8), (0.2, 1.8), (-2.0, -2.0), (3.6, 1.6))):
            self.put("CafeTable", c.x + dx, c.y + dy, 0.0, k * 0.7,
                     recolor={"awning": ZOO_GREEN if k % 2 else ZOO_YELLOW}, sub="Cafe")
        self.block_poly(pat)

    def service_yard(self):
        """Keeper yard inside the back gate (east): hay, cart, crates."""
        self.proto("HayBale", mb_haybale, smooth={"M_Wall_Butter"}, angle=50)
        self.proto("HaySquare", mb_haysquare)
        for (x, y, r) in ((-137.0, 292.0, 0.4), (-134.5, 291.0, 0.2)):
            self.inst("HayBale", x, y, GZ, r, sub="ServiceYard")
        for (x, y, z, r) in ((-131.5, 289.5, GZ, 0.0), (-131.4, 290.4, GZ, 0.05), (-131.5, 289.9, GZ + 0.42, 1.5)):
            self.inst("HaySquare", x, y, z, r, sub="ServiceYard")
        self.put("CrateStack", -135.0, 296.5, None, 1.6, sub="ServiceYard")
        self.put("Barrel", -137.6, 296.8, None, 0.0, sub="ServiceYard")
        self.patch("ServiceYard_Gravel", [(-140.5, 287.0), (-129.0, 287.0), (-128.5, 303.5), (-140.5, 303.5)],
                   "M_Gravel", GZ + 0.02, sub="ServiceYard")
        self.block_poly([(-141.0, 286.5), (-128.0, 286.5), (-128.0, 304.0), (-141.0, 304.0)])

    # ------------------------------------------------------------------ the incident
    def incident(self):
        S = self.S
        sub = "Incident"
        rnd = random.Random(1337)
        A, I = BR_ALONG, BR_IN
        fl = BREACH + I * 2.0                     # fence line at the breach
        site = [V2(p) for p in S.poly]

        def inside(p, margin=0.35):
            if not G.point_in_poly(p, site):
                return False
            for i in range(len(site)):
                if G.dist_point_seg(p, site[i], site[(i + 1) % len(site)]) < margin:
                    return False
            return True

        # scorch star + crater lip
        mb = MeshBuilder()
        pts = []
        for i in range(26):
            a = TAU * i / 26
            r = (12.0 if i % 2 == 0 else 4.8) * rnd.uniform(0.7, 1.15)
            d = Vector((math.cos(a), math.sin(a)))
            # squash toward the street (blast vented outward through the fence)
            if d.dot(-I) > 0:
                r *= 0.55
            pts.append(SCORCH + d * r)
        pts = [p if inside(p, 0.2) else SCORCH + (p - SCORCH) * 0.5 for p in pts]
        mb.fan(SCORCH, pts, GZ + 0.055, "M_Incident")
        lip_o = G.ensure_ccw(blob_pts(SCORCH, 3.4, 3.0, seg=14, jit=0.15, seed=7))
        lip_i = G.ensure_ccw(blob_pts(SCORCH, 2.2, 1.9, seg=14, jit=0.15, seed=7))
        for i in range(len(lip_o)):
            j = (i + 1) % len(lip_o)
            mid = (lip_o[i] + lip_i[i]) / 2
            mb.face([Vector((*lip_o[i], GZ + 0.04)), Vector((*lip_o[j], GZ + 0.04)),
                     Vector((*((lip_o[j] + lip_i[j]) / 2), GZ + 0.3)), Vector((*mid, GZ + 0.3))], "M_Dirt")
            mb.face([Vector((*mid, GZ + 0.3)), Vector((*((lip_o[j] + lip_i[j]) / 2), GZ + 0.3)),
                     Vector((*lip_i[j], GZ + 0.08)), Vector((*lip_i[i], GZ + 0.08))], "M_Dirt")
        mb.tri_fill([lip_i], GZ + 0.08, "M_Incident")
        # soot splashes around the star
        for k in range(14):
            a = rnd.uniform(0, TAU)
            d = Vector((math.cos(a), math.sin(a)))
            if d.dot(-I) > 0.3:
                continue
            q = SCORCH + d * rnd.uniform(6.0, 13.0)
            if not inside(q, 0.4):
                continue
            decal(mb, blob_pts(q, rnd.uniform(0.4, 1.1), rnd.uniform(0.3, 0.7), seg=5, rot=a), GZ + 0.05, "M_Incident")
        self.mesh("Incident_Scorch", mb, sub)
        # charred tree at the edge of the blast (bare black trunk + snapped branches): reads at eye level
        ct = SCORCH + A * 7.0 + I * 2.4
        tm = MeshBuilder()
        N.lathe(tm, [(0.42, GZ), (0.3, 0.5), (0.22, 2.6, 0.15, 0.1), (0.14, 4.1, 0.35, 0.2), (0.0, 4.5, 0.4, 0.2)],
                "M_Incident", seg=7, cx=ct.x, cy=ct.y)
        for k, (a, L, z0, up) in enumerate(((0.4, 2.2, 2.4, 1.3), (2.3, 1.8, 2.9, 1.0), (4.0, 1.6, 3.4, 0.9),
                                            (5.4, 1.2, 1.7, 0.5))):
            b0 = Vector((ct.x + 0.15, ct.y + 0.1, z0))
            b1 = b0 + Vector((math.cos(a) * L, math.sin(a) * L, up))
            N.tube(tm, b0, b1, 0.11, "M_Incident", seg=5, r1=0.04, cap0=True)
            N.tube(tm, b1, b1 + Vector((math.cos(a + 0.7) * 0.6, math.sin(a + 0.7) * 0.6, 0.45)), 0.04,
                   "M_Incident", seg=4, r1=0.02)
        N.blob(tm, (ct.x - 0.7, ct.y + 0.9, GZ), 0.75, "M_Incident", seg=6, rings=3, sz=0.5, floor=GZ, seed=9)
        self.mesh("Incident_CharredTree", tm, sub, smooth={"M_Incident"}, angle=60)
        self.block(ct, 4.5)

        # rubble fan (brick, stone, concrete chunks; mostly blown outward)
        rb = MeshBuilder()
        mats = ["M_Wall_Brick", "M_Wall_Brick", "M_CanalStone", "M_Wall_Concrete", "M_Wall_Brick"]
        n = 0
        tries = 0
        while n < 34 and tries < 400:
            tries += 1
            ang = rnd.uniform(-1.45, 1.45)
            out = rnd.random() < 0.7
            base = -I if out else I
            d = Vector((base.x * math.cos(ang) - base.y * math.sin(ang), base.x * math.sin(ang) + base.y * math.cos(ang)))
            r = rnd.uniform(0.8, 7.5 if not out else 4.5)
            p = fl + d * r + A * rnd.uniform(-5.5, 5.5)
            if not inside(p, 0.45):
                continue
            s = rnd.uniform(0.2, 0.55) * (1.15 if r < 3 else 0.85)
            sub_ = MeshBuilder()
            sub_.box(-s, -s * 0.7, 0.0, s, s * 0.7, s * rnd.uniform(0.6, 1.1), rnd.choice(mats), skip=("-z",))
            rb.extend(sub_, Matrix.Translation((p.x, p.y, GZ - 0.05)) @ Matrix.Rotation(rnd.uniform(0, TAU), 4, "Z")
                      @ Matrix.Rotation(rnd.uniform(-0.35, 0.35), 4, "X"))
            n += 1
        self.mesh("Incident_Rubble", rb, sub)

        # fence panels: blown flat outward, one twisted, one leaning
        fz = GZ
        rz = rot_along(A)
        for (u, dz_rot, tilt, outw) in ((-3.6, 0.0, 84.0, 0.1), (2.2, 0.32, 88.0, 0.25), (5.9, 0.0, 34.0, 0.0)):
            p = fl + A * u - I * outw
            self.tilted("Fence_Iron_3m", p.x, p.y, fz + (0.12 if tilt > 80 else 0.0), math.radians(tilt), 0.0,
                        rz + dz_rot, sub=sub)
        # breach pillars: west one knocked over (lying outward), east one broken stump
        pw = fl - A * 7.6
        o = self.inst("Pillar", pw.x - I.x * 0.2, pw.y - I.y * 0.2, GZ + 0.5, rz, sub=sub,
                      tilt=(math.radians(-78), math.radians(6)))
        pe = fl + A * 7.6
        self.inst("PillarStump", pe.x, pe.y, GZ, rz + 0.2, sub=sub)
        self.inst("Pillar", (fl - A * 10.0).x, (fl - A * 10.0).y, GZ, rz, sub=sub, tilt=(math.radians(-8), 0.0))

        # overturned keeper truck (zoo livery: green box, yellow cab, big yellow paws), lying on its side
        # across the keeper track west of the crater. Its ROOF faces the street (due south) so the roof
        # paw reads from the Canal St sidewalk / Zoo Bridge at eye level; the up-facing side panel
        # carries the second paw for the mid / top views. Local frame of the kit truck: nose -Y,
        # roof +Z; ry = +90 deg puts local -X up and local +Z (roof) along the nose's right.
        roof_dir = Vector((0.0, -1.0))
        nose_dir = Vector((roof_dir.y, -roof_dir.x))           # (-1, 0): cab points west along the track
        t_ctr = V2(-238.6, 200.6)                             # footprint centre (clear of the crater lip)
        tp = t_ctr - roof_dir * 1.6                           # kit origin = belly line
        rz_t = rot_front(nose_dir)
        ry_t = math.radians(90)
        truck = self.tilted("Truck_Box", tp.x, tp.y, GZ + 1.15, 0.0, ry_t, rz_t,
                            recolor={"awning": ZOO_YELLOW, "sign": ZOO_GREEN}, swap={"M_Wall_White": ZOO_GREEN},
                            sub=sub, name="LM_Zoo_KeeperTruck_Overturned")
        lv = MeshBuilder()
        X, Y, Zv = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
        # side panel (local -X, faces the sky): paw toes toward the roof (+Z)
        s1 = 2.2
        plane_decal(lv, paw_shapes(Vector((0, 0)), (0, 1), s1), Vector((-1.145, 0.99, 2.09 - 0.04 * s1)),
                    Zv.cross(-X), Zv, ZOO_YELLOW)
        # roof (local +Z, faces the street): paw upright in the world (local -X is up)
        s2 = 2.25
        plane_decal(lv, paw_shapes(Vector((0, 0)), (0, 1), s2), Vector((0.04 * s2, 1.05, 3.215)),
                    (-X).cross(Zv), -X, ZOO_YELLOW)
        o = self.mesh("Incident_TruckLivery", lv, sub, loc=(tp.x, tp.y, GZ + 1.15))
        o.rotation_euler = (0.0, ry_t, rz_t)

        # spilled cargo: crates, barrels, pallets (some tipped) - kept off the truck's footprint and out of
        # the sightline to its roof paw
        cargo = [("Crate", -11.2, 1.6, 0.0, 0.3, 0.0), ("Crate", -7.8, 5.2, 0.0, 0.0, 0.0),
                 ("Crate", -5.2, 6.4, math.radians(28), 0.0, 0.5), ("Barrel", -12.0, 4.4, math.radians(90), 0.0, 0.9),
                 ("Barrel", 1.8, 7.8, math.radians(90), 0.0, 2.4), ("Barrel", -3.0, 8.2, 0.0, 0.0, 0.0),
                 ("Pallet", -8.6, 6.6, math.radians(12), 0.0, 0.7), ("CrateStack", -10.5, 7.5, 0.0, 0.0, 0.3),
                 ("Crate", 3.9, -0.6, math.radians(-22), math.radians(12), 0.2),
                 ("Barrel", 6.6, 1.8, math.radians(90), 0.0, -0.6)]
        for piece, au, iv, rx, ry, rr in cargo:
            p = SCORCH + A * au + I * iv
            if not inside(p, 0.6):
                continue
            if rx or ry:
                zz = GZ + (0.3 if piece == "Barrel" else 0.12)
                self.tilted(piece, p.x, p.y, zz, rx, ry, rr + rz, sub=sub)
            else:
                self.put(piece, p.x, p.y, None, rr + rz, sub=sub)
        # park lamp bent over by the blast: leans ~34 deg away from the crater (eye-level diagonal) +
        # toppled bin
        lp = SCORCH + A * 4.5 + I * 6.0
        away = (lp - SCORCH).normalized()
        self.tilted("Lamp_Park", lp.x, lp.y, GZ + 0.04, math.radians(34), 0.0, rot_front(away), sub=sub,
                    name="LM_Zoo_Incident_BentLamp")
        bp = SCORCH + A * 9.0 + I * 4.5
        self.tilted("TrashBin", bp.x, bp.y, GZ + 0.3, math.radians(90), 0.0, rz + 1.0, sub=sub)
        # SMOKE COLUMN rising out of the crater (the tall vertical cue that reads at eye level from the
        # street; static stylized mesh - no collider in Unity, swap for a particle system if wanted)
        sm = mb_smoke(seed=5, height=7.6, drift=(0.42, 0.12))
        self.mesh("Incident_Smoke", sm, sub, loc=(SCORCH.x - 0.3, SCORCH.y + 0.4, GZ + 0.1),
                  smooth={"M_Incident", "M_Wall_Slate", "M_Wall_Concrete"}, angle=80)
        # first responders only just arrived: ONE barrier knocked flat and ONE tipped cone (a full row of
        # barriers / cones read as tidy after-the-fact roadworks)
        p = fl + A * 8.9 - I * 1.2
        if inside(p, 0.4):
            self.tilted("Barrier", p.x, p.y, GZ + 0.14, math.radians(82), 0.0, rz + 0.35, sub=sub)
        p = fl + A * -2.2 - I * 1.45
        if inside(p, 0.3):
            self.tilted("TrafficCone", p.x, p.y, GZ + 0.19, math.radians(90), 0.0, rz + 0.6, sub=sub)
        # stray cargo blown out into the verge strip, leading toward Zoo Corner / the Zoo Bridge
        for au, iv, piece, rx, rr in ((9.6, -1.0, "Barrel", 90.0, 0.4), (12.4, -1.05, "Crate", 18.0, 0.9),
                                      (11.0, -0.6, "Pallet", 0.0, 0.3), (-9.6, -1.1, "Crate", 0.0, 0.2)):
            p = fl + A * au + I * iv
            if not inside(p, 0.45):
                continue
            if rx:
                self.tilted(piece, p.x, p.y, GZ + (0.3 if piece == "Barrel" else 0.15), math.radians(rx), 0.0,
                            rz + rr, sub=sub)
            else:
                self.put(piece, p.x, p.y, None, rz + rr, sub=sub)

        # trails of tipped props + prints from the open enclosure gates to the hole
        self.proto("HaySquare", mb_haysquare)
        self.proto("Bucket", mb_bucket)
        trail = [(-250.5, 212.0, "Bucket", 1.0), (-246.0, 206.0, "Bucket", 2.2)]
        for x, y, key, r in trail:
            self.inst(key, x, y, GZ + 0.26, r, sub=sub, tilt=(math.pi / 2, 0.0))
        for x, y, r, tilt in ((-205.0, 238.5, 0.4, 0.0), (-213.5, 214.0, 1.1, 0.35), (-221.0, 205.0, 2.0, 1.4)):
            self.inst("HaySquare", x, y, GZ, r, sub=sub, tilt=(tilt, 0.0) if tilt else None)
        self.tilted("Crate", -226.5, 203.5, GZ + 0.15, math.radians(25), math.radians(10), 0.9, sub=sub)
        prints = MeshBuilder()

        def prints_along(pts, mat, size, spacing, pair):
            pl = G.Polyline([V2(p) for p in pts])
            s = 0.5
            k = 0
            while s < pl.length:
                p = pl.pos(s)
                t = pl.tangent(s)
                nrm = G.left_normal(t)
                q = p + nrm * (pair if k % 2 == 0 else -pair) + nrm * rnd.uniform(-0.15, 0.15)
                ring = blob_pts(q, size, size * 0.75, seg=4, rot=rot_along(t))
                prints.face([Vector((p_.x, p_.y, GZ + 0.045)) for p_ in ring], mat)
                s += spacing
                k += 1

        prints_along([self.pg_gate + (self.pg_gate - PENGUIN).normalized() * 1.6, (-248, 207.5), (-243.2, 202.8),
                      (-239.2, 197.4)], "M_Incident", 0.11, 0.55, 0.13)
        prints_along([self.pz_gate + Vector((0, 1.5)), (-201, 240.0), (-212, 238.0), (-220, 228.0), (-224, 214.0),
                      SCORCH + A * 3.0 + I * 2.0], "M_Dirt", 0.14, 0.75, 0.22)
        prints_along([(-150.0, 324.0), (-140.0, 325.0), (-131.3, 320.5), (-131.0, 309.0), (-129.5, 302.5),
                      (-126.5, 300.5)], "M_Dirt", 0.22, 1.2, 0.35)
        self.mesh("Incident_Prints", prints, sub)

        # ESCAPE TRAILS out of the hole, across the grass verge to the Canal St kerb (deliberate small
        # extension beyond the polygon: flat decals only, each trail stops before the sidewalk):
        # sooty paws -> south to the kerb facing the Zoo Bridge, a small herd's hooves -> Zoo Corner,
        # penguin / flamingo webbed feet -> south-west toward the Zoo Landing reeds.
        vg = MeshBuilder()
        self.verge_stop = []

        def trail(pts, shape_fn, mat, size, spacing, pair, lateral=0.0, phase=0.0):
            spl, _ = G.catmull_rom([V2(p) for p in pts], step=0.5)
            pl = G.Polyline(spl)
            s, k = phase, 0
            while s < pl.length:
                p = pl.pos(s)
                t = pl.tangent(s)
                nrm = G.left_normal(t)
                q = p + nrm * (lateral + (pair if k % 2 == 0 else -pair) + rnd.uniform(-0.06, 0.06))
                if kerb_gap(S, q) < 0.45:
                    self.verge_stop.append((round(q.x, 1), round(q.y, 1)))
                    break
                z = GZ + (0.065 if (q - SCORCH).length < 12.8 else 0.03)
                yaw = rnd.uniform(-0.18, 0.18)
                d = Vector((t.x * math.cos(yaw) - t.y * math.sin(yaw), t.x * math.sin(yaw) + t.y * math.cos(yaw)))
                for sh in shape_fn(q, d, size):
                    decal(vg, sh, z, mat)
                s += spacing
                k += 1

        paws = [fl + A * -3.4 - I * 0.4, (-236.4, 188.5), (-234.4, 182.5), (-232.6, 177.0), (-231.6, 171.0)]
        trail(paws, paw_shapes, "M_Incident", 0.42, 0.85, 0.17)
        hooves = [SCORCH + A * 3.6 - I * 2.2, (-229.0, 187.0), (-226.4, 181.5), (-223.4, 176.5), (-221.0, 171.0)]
        trail(hooves, hoof_shapes, "M_Dirt", 1.0, 0.95, 0.2, lateral=0.5)
        trail(hooves, hoof_shapes, "M_Dirt", 0.9, 0.9, 0.18, lateral=-0.55, phase=0.45)
        webs = [(-238.9, 195.5), (-241.5, 190.5), (-245.0, 185.5), (-247.5, 181.0), (-249.5, 176.0)]
        trail(webs, web_shapes, "M_Incident", 1.05, 0.7, 0.14)
        self.mesh("Incident_EscapeTrails", vg, sub)
        self.block(SCORCH, 9.0)
        self.block(t_ctr, 4.6)

    # ------------------------------------------------------------------ planting
    def planting(self):
        S = self.S
        rnd = random.Random(99)
        inner = inset_poly(S.poly, 5.2)
        bx0, by0, bx1, by1 = G.bbox(inner)
        trees, bushes = [], []
        # perimeter band trees (inside the fence)
        pl = G.Polyline(inner + [inner[0]])
        s = 3.0
        while s < pl.length:
            p = pl.pos(s) + V2(rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2))
            if self.free(p, 2.6) and all((p - q).length > 6.5 for q in trees):
                piece = rnd.choice(["Tree_Round_A", "Tree_Round_B", "Tree_Round_A", "Tree_Cone"])
                fol = rnd.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage", "M_Foliage_Light"])
                if piece == "Tree_Cone":
                    fol = "M_Foliage_Dark"
                sc = rnd.uniform(0.9, 1.2)
                self.put(piece, p.x, p.y, None, rnd.uniform(0, TAU), recolor={"foliage": fol}, scale=(sc, sc, sc),
                         sub="Planting")
                trees.append(p)
            s += rnd.uniform(7.0, 11.0)
        # bushes along the fence
        pl2 = G.Polyline(inset_poly(S.poly, 3.0) + [inset_poly(S.poly, 3.0)[0]])
        s = 1.0
        while s < pl2.length:
            p = pl2.pos(s)
            if self.free(p, 1.0) and all((p - q).length > 2.5 for q in trees):
                self.put(rnd.choice(["Bush_A", "Bush_B"]), p.x, p.y, None, rnd.uniform(0, TAU),
                         recolor={"foliage": rnd.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage_Light"])},
                         sub="Planting")
                bushes.append(p)
            s += rnd.uniform(3.5, 7.0)
        # interior shade trees on the lawns
        n = 0
        for _ in range(500):
            if n >= 26:
                break
            p = V2(rnd.uniform(bx0, bx1), rnd.uniform(by0, by1))
            if not G.point_in_poly(p, inner) or not self.free(p, 3.0):
                continue
            if any((p - q).length < 8.0 for q in trees):
                continue
            piece = rnd.choice(["Tree_Round_A", "Tree_Round_B", "Tree_Palm", "Tree_Round_A"])
            fol = rnd.choice(["M_Foliage", "M_Foliage_Light", "M_Foliage_Dark"])
            self.put(piece, p.x, p.y, None, rnd.uniform(0, TAU), recolor={"foliage": fol}, sub="Planting")
            trees.append(p)
            n += 1
            for k in range(rnd.randint(1, 3)):
                q = p + V2(rnd.uniform(-3.5, 3.5), rnd.uniform(-3.5, 3.5))
                if self.free(q, 1.0) and G.point_in_poly(q, inner):
                    self.put(rnd.choice(["Bush_A", "Bush_B"]), q.x, q.y, None, rnd.uniform(0, TAU),
                             recolor={"foliage": rnd.choice(["M_Foliage", "M_Foliage_Blossom", "M_Foliage_Light"])},
                             sub="Planting")
        # flowerbeds flanking the plaza / loop
        for (x, y, r) in ((-163.0, 251.5, 0.55), (-158.0, 238.5, 0.55), (-144.5, 258.5, 1.57)):
            if self.free((x, y), 1.0):
                self.put("Flowerbed_2m", x, y, None, r, recolor={"foliage": "M_Foliage"}, sub="Planting")
        return len(trees)


# ================================================================================ entry points
def build(S):
    if S.id != "Zoo":
        return "unknown site"
    Z = Zoo(S)
    Z.gate()
    Z.walkways()
    Z.plaza()
    Z.aviary()
    Z.monkey_island()
    Z.penguins()
    Z.big_cats()
    Z.elephants()
    Z.savanna()
    Z.petting_zoo()
    Z.reptile_house()
    Z.cafe()
    Z.commons()
    Z.service_yard()
    Z.perimeter()
    Z.incident()
    Z.path_dressing()
    nt = Z.planting()
    S.register_lot(S.poly)
    return Z.stats(dict(trees=nt, verge_trail_ends=Z.verge_stop))


def build_area(S):
    fn = {"ZooForecourt": _forecourt, "ZooParking": _parking, "ZooBackLot": _backlot,
          "ZooLanding": _landing}.get(S.id)
    if fn is None:
        return "no builder"
    Z = _Ctx(S)
    fn(Z)
    S.register_lot(S.poly)
    return Z.stats(dict(reeds=Z.reeds_n) if hasattr(Z, "reeds_n") else None)


# -------------------------------------------------------------------------------- forecourt
def _forecourt(Z):
    S = Z.S
    poly = [V2(p) for p in S.poly]
    mb = MeshBuilder()
    P = G.ensure_ccw(poly)
    mb.prism(P, GZ - 0.1, 0.1, "M_Plaza", "M_Curb")
    # gate strip between the forecourt and the gate threshold (connects the two polygons)
    strip = [gw(-4.6, -2.75), gw(4.6, -2.35), gw(4.6, 0.05), gw(-4.6, 0.05)]
    mb.prism(G.ensure_ccw(strip), GZ - 0.1, 0.1, "M_Plaza", "M_Plaza")
    # accent carpet on the boulevard axis + crosswise bands
    car = [gw(-2.6, -12.0), gw(2.6, -10.0), gw(2.6, -2.4), gw(-2.6, -2.4)]
    mb.prism(G.ensure_ccw(car), 0.05, 0.112, "M_Plaza_Accent", "M_Plaza_Accent")
    mb.prism(G.ensure_ccw([gw(-4.6, -2.75), gw(4.6, -2.35), gw(4.6, 0.05), gw(-4.6, 0.05)]), 0.05, 0.112,
             "M_Plaza_Accent", "M_Plaza_Accent")
    v = -10.0
    while v > -24.0 and S.clear_of_roads(gw(0.0, v - 0.5), extra=0.0):
        v -= 0.5
    if v > -24.0:
        con = [gw(-2.6, -9.0), gw(2.6, -9.0), gw(2.6, v - 0.3), gw(-2.6, v - 0.3)]
        mb.prism(G.ensure_ccw(con), GZ - 0.1, 0.112, "M_Plaza_Accent", "M_Plaza_Accent")
    Z.mesh("Paving", mb, "Ground")
    rot = Z.S.rot
    # ticket booths flanking the gate
    for u in (-8.0, 8.0):
        p = gw(u, -3.6)
        Z.put("NewsStand", p.x, p.y, 0.1, rot, recolor={"awning": ZOO_GREEN, "sign": ZOO_YELLOW}, sub="Booths")
    # flag banners
    Z.proto("FlagGreen", lambda: mb_flagpole(ZOO_GREEN))
    Z.proto("FlagYellow", lambda: mb_flagpole(ZOO_YELLOW))
    for k, (u, v) in enumerate(((-14.5, -3.2), (-11.5, -6.6), (11.5, -3.0), (9.0, -6.4))):
        p = gw(u, v)
        if G.point_in_poly(p, poly):
            Z.inst("FlagGreen" if k % 2 == 0 else "FlagYellow", p.x, p.y, 0.1, rot, sub="Flags")
    # planters + benches
    for (u, v) in ((-5.2, -5.2), (5.2, -5.0), (-8.0, -8.6)):
        p = gw(u, v)
        if G.point_in_poly(p, poly):
            Z.put("Planter", p.x, p.y, 0.1, rot, recolor={"foliage": "M_Foliage_Blossom"}, sub="Furniture")
    for (u, v, r) in ((-4.0, -8.6, math.pi / 2), (4.2, -7.8, -math.pi / 2)):
        p = gw(u, v)
        if G.point_in_poly(p, poly):
            Z.put("Bench", p.x, p.y, 0.1, rot + r, sub="Furniture")
    # big map board
    mb2 = MeshBuilder()
    for x in (-1.5, 1.5):
        mb2.box(x - 0.1, -0.1, 0.0, x + 0.1, 0.1, 3.0, "M_Trim_Wood", skip=("-z",))
    mb2.box(-1.8, -0.12, 0.9, 1.8, 0.12, 3.25, ZOO_GREEN, skip=())
    mb2.box(-1.95, -0.16, 3.25, 1.95, 0.16, 3.45, ZOO_YELLOW, skip=())
    face = MeshBuilder()
    face.box(-1.6, -0.15, 1.05, 1.6, -0.12, 3.1, "M_Grass_Park", skip=("+y",))
    # map features (raised a hair in front of the face)
    def feat(pts, mat, y):
        q = [Vector((x, y, z)) for x, z in pts]
        face.face(q, mat)
    feat([(-1.4, 2.6), (-0.6, 2.6), (-0.6, 2.95), (-1.4, 2.95)], "M_Dirt", -0.155)          # elephants
    feat([(-0.4, 2.55), (1.4, 2.55), (1.4, 2.95), (-0.4, 2.95)], "M_Sand", -0.155)          # savanna
    feat([(-1.4, 1.7), (-0.8, 1.7), (-0.8, 2.35), (-1.4, 2.35)], "M_Grass_Dry", -0.155)     # big cats
    for cx, cz, r, mat in ((-0.35, 2.05, 0.28, "M_Water"), (-1.05, 1.3, 0.2, "M_Water"), (0.45, 2.15, 0.27,
                                                                                          "M_Metal_Dark")):
        ring = [(cx + r * math.cos(TAU * i / 10), cz + r * math.sin(TAU * i / 10)) for i in range(10)]
        feat(ring, mat, -0.155)
    loop = [(-1.2, 1.25), (0.9, 1.25), (1.2, 1.6), (1.2, 2.4), (-1.25, 2.45), (-1.25, 1.3)]
    for i in range(len(loop)):
        a, b = loop[i], loop[(i + 1) % len(loop)]
        d = Vector((b[0] - a[0], b[1] - a[1])).normalized() * 0.0
        nx, nz = -(b[1] - a[1]), (b[0] - a[0])
        L = math.hypot(nx, nz) or 1.0
        nx, nz = nx / L * 0.04, nz / L * 0.04
        feat([(a[0] - nx, a[1] - nz), (b[0] - nx, b[1] - nz), (b[0] + nx, b[1] + nz), (a[0] + nx, a[1] + nz)],
             "M_Path", -0.16)
    star = [(0.95 + 0.11 * math.cos(TAU * i / 8), 1.25 + 0.11 * math.sin(TAU * i / 8)) for i in range(8)]
    feat(star, "M_Awning_Red", -0.165)
    mb2.extend(face)
    p = gw(-12.3, -5.6)
    o = Z.mesh("MapBoard", mb2, "Furniture", loc=(p.x, p.y, 0.1), rot=rot + 0.35)
    Z.k += 1
    return o


# -------------------------------------------------------------------------------- parking
def _parking(Z):
    S = Z.S
    poly = G.ensure_ccw([V2(p) for p in S.poly])
    wa, wb = V2(-110, 201), V2(-100, 233)
    mid = wa + (wb - wa) * 0.5
    t = (wb - wa).normalized()
    ia = next(i for i, p in enumerate(poly) if (p - wb).length < 0.01)
    if (poly[(ia + 1) % len(poly)] - wa).length < 0.01:      # edge wb -> wa: insert the curb gap there
        poly = poly[:ia + 1] + [mid + t * 3.3, mid - t * 3.3] + poly[ia + 1:]
        gap = {ia + 1}
    else:
        gap = set()
    inner = inset_poly(poly, 0.35)
    mb = MeshBuilder()
    ring_wall(mb, poly, inner, GZ - 0.05, 0.15, "M_Curb", "M_Curb", in_z0=0.0, gap=gap)
    mb.tri_fill([inner], 0.02, "M_Asphalt_Alley")
    mb.wall(inner, -0.1, 0.02, "M_Asphalt_Alley", closed=True)
    # aisle axis: along the lot's long direction
    a0 = (V2(-110, 201) + V2(-90, 192)) / 2
    a1 = (V2(-86, 228) + V2(-100, 233)) / 2
    ax = (a1 - a0).normalized()
    side = Vector((ax.y, -ax.x))      # to the east
    L = (a1 - a0).length
    lines = MeshBuilder()
    cars = []
    k = 0
    wmid = V2(-105.0, 217.0)
    for sgn in (-1, 1):
        n = int((L - 6.0) / 2.7)
        for i in range(n + 1):
            t = 3.0 + i * 2.7
            c = a0 + ax * t + side * sgn * 3.0
            e = c + side * sgn * 5.0
            q0 = c - ax * 0.06
            q1 = c + ax * 0.06
            q2 = e + ax * 0.06
            q3 = e - ax * 0.06
            if not all(G.point_in_poly(q, inner) for q in (q0, q2)):
                continue
            if side.x * sgn < 0 and abs((c - wmid).dot(ax)) < 3.4:
                continue
            decal(lines, [q0, q1, q2, q3], 0.03, "M_RoadLine_White")
            if i < n:
                cc = a0 + ax * (t + 1.35) + side * sgn * 5.5
                if not (side.x * sgn < 0 and abs((cc - wmid).dot(ax)) < 4.6):
                    cars.append((cc, sgn))
    mb.extend(lines)
    Z.mesh("Lot", mb, "Ground")
    rnd = random.Random(5)
    picks = [1, 3, 4, 7, 9, 12, 14, 16]
    cols = ["M_Awning_Blue", "M_Wall_White", "M_Awning_Yellow", "M_Wall_Slate", "M_Awning_Teal", "M_Awning_Red"]
    for j, idx in enumerate(picks):
        if idx >= len(cars):
            continue
        c, sgn = cars[idx]
        if not G.point_in_poly(c + side * sgn * 2.4, inner):
            continue
        piece = "Car_Van" if j == 2 else "Car_Sedan"
        rec = {"awning": ZOO_GREEN} if j == 2 else {"awning": cols[j % len(cols)]}
        Z.put(piece, c.x, c.y, 0.02, rot_front(side * sgn) + rnd.uniform(-0.04, 0.04), recolor=rec, sub="Cars")
    # lamps, P sign, tree islands at both ends
    for t in (4.0, L - 4.0):
        p = a0 + ax * t
        Z.put("Lamp_Park", p.x, p.y, 0.02, 0.0, sub="Furniture")
    Z.proto("ParkSign", mb_lamp_post_sign)
    ps = V2(-99.6, 230.6)
    Z.inst("ParkSign", ps.x, ps.y, 0.15, rot_front((-1.0, 0.2)), sub="Furniture")
    # driveway: from the middle of the west side across the grass verge to the Zoo Parkway sidewalk
    wa, wb = V2(-110, 201), V2(-100, 233)
    mid = wa + (wb - wa) * 0.5
    dw = Vector((-(wb - wa).y, (wb - wa).x)).normalized()      # outward (west)
    if dw.x > 0:
        dw = -dw
    t = (wb - wa).normalized()
    reach = 0.0
    while reach < 25.0 and S.clear_of_roads(mid + dw * (reach + 0.5), extra=0.0):
        reach += 0.5
    if 0.5 < reach < 25.0:
        q = [mid - t * 3.3 - dw * 0.5, mid + t * 3.3 - dw * 0.5, mid + t * 3.6 + dw * (reach + 0.2),
             mid - t * 3.6 + dw * (reach + 0.2)]
        dmb = MeshBuilder()
        dmb.prism(G.ensure_ccw(q), GZ - 0.1, 0.03, "M_Asphalt_Alley", "M_Curb")
        Z.mesh("Driveway", dmb, "Ground")
    Z.drive_mid, Z.drive_t = mid, t
    # tree planters at the row ends (never on a stall)
    stall_pts = [c for c, _ in cars]
    for sgn in (-1, 1):
        for q in (a0 + ax * 1.2 + side * sgn * 5.6, a1 - ax * 1.4 + side * sgn * 5.6):
            if not G.point_in_poly(q, inset_poly(poly, 1.2)) or any((q - c).length < 2.6 for c in stall_pts):
                continue
            pm = MeshBuilder()
            pm.prism(blob_pts(q, 1.1, 1.1, seg=8), 0.0, 0.2, "M_Dirt", "M_Curb")
            Z.mesh(f"TreeIsland_{len(Z.heavy)}", pm, "Furniture")
            Z.put("Tree_Small", q.x, q.y, 0.2, q.x, recolor={"foliage": "M_Foliage_Light"}, sub="Furniture")
    Z.put("ParkingMeter", -98.6, 229.0, 0.02, rot_front((-1, 0)), sub="Furniture")


# -------------------------------------------------------------------------------- back lot
def _backlot(Z):
    S = Z.S
    poly = G.ensure_ccw([V2(p) for p in S.poly])
    bulb = V2(-110.0, 330.0)

    def ok(p, r=1.0):
        p = V2(p)
        return G.point_in_poly(p, poly) and (p - bulb).length > 10.5 + r and S.clear_of_roads(p, extra=r)

    gravel = [p for p in poly]
    Z.patch("Gravel", gravel, "M_Gravel", GZ + 0.03, sub="Ground")
    sp = BuildingSpec("shed", 2, 2, 1, dict(wall="M_Wall_Corrugated", trim="M_Trim_White", door="M_Door_Wood",
                                           awning=ZOO_GREEN, roof="M_Roof_Green", sign=ZOO_YELLOW),
                      roof="flat", ground_h=H3, feats=dict(door_i=1), seed=71, district="zoo")
    S.building(sp, (-116.8, 302.0), rot_front((1.0, 0.0)), name="LM_ZooBackLot_FeedShed")
    sp2 = BuildingSpec("warehouse", 3, 2, 1, dict(wall=ZOO_GREEN, trim=ZOO_YELLOW, door="M_Door_Wood",
                                                 awning=ZOO_GREEN, roof="M_Roof_Charcoal", sign=ZOO_YELLOW),
                       roof="gable_side", ground_h=H4, seed=72, district="zoo")
    S.building(sp2, (-117.9, 312.0), rot_front((1.0, 0.0)), name="LM_ZooBackLot_HayBarn")
    Z.proto("HayBale", mb_haybale, smooth={"M_Wall_Butter"}, angle=50)
    Z.proto("HaySquare", mb_haysquare)
    for (x, y, z, r) in ((-121.6, 297.6, GZ, 0.1), (-120.2, 297.7, GZ, 0.0), (-120.9, 297.6, GZ + 0.42, 0.05),
                         (-116.2, 297.3, GZ, 1.5)):
        if ok((x, y), 0.5):
            Z.inst("HaySquare", x, y, z, r, sub="Hay")
    for (x, y, r) in ((-122.3, 319.5, 0.0), (-122.0, 321.0, 0.0)):
        if ok((x, y), 0.6):
            Z.inst("HayBale", x, y, GZ, r + 1.57, sub="Hay")
    tp = V2(-122.0, 326.5)
    if ok(tp, 0.2):
        Z.put("Truck_Box", tp.x, tp.y, None, rot_front((0.1, 1.0)), recolor={"awning": ZOO_GREEN, "sign": ZOO_YELLOW},
              sub="Vehicles")
    for (piece, x, y, r) in (("CrateStack", -116.2, 306.8, 0.2), ("Pallet", -115.6, 318.5, 0.4),
                             ("Barrel", -121.5, 316.6, 0.0), ("Barrel", -120.6, 317.1, 0.0),
                             ("Dumpster", -124.2, 333.5, 1.6), ("Crate", -118.0, 305.5, 0.7)):
        if ok((x, y), 0.5):
            Z.put(piece, x, y, None, r, sub="Props", recolor={"awning": ZOO_GREEN} if piece == "Dumpster" else None)


# -------------------------------------------------------------------------------- landing
def _landing(Z):
    S = Z.S
    poly = G.ensure_ccw([V2(p) for p in S.poly])
    inner = inset_poly(poly, 0.8)
    rnd = random.Random(808)
    trail = [V2(p) for p in ((-345, 172), (-296, 161), (-250, 141))]
    tspl, _ = G.catmull_rom(trail, step=1.5)

    def off_trail(p, pad):
        return all(G.dist_point_seg(p, tspl[i], tspl[i + 1]) > 1.25 + pad for i in range(len(tspl) - 1))

    def ok(p, pad=0.6):
        p = V2(p)
        return G.point_in_poly(p, inner) and off_trail(p, pad) and S.clear_of_roads(p, extra=pad)

    # meadow patches
    for k, (cx, cy, rx, ry, r) in enumerate(((-330, 177, 12, 5, 0.2), (-300, 172, 10, 4.5, 0.25),
                                             (-268, 160, 9, 4, 0.45))):
        pts = [p for p in blob_pts((cx, cy), rx, ry, seg=16, jit=0.2, seed=k + 1, rot=r)]
        pts = [p if G.point_in_poly(p, inner) else G.V(p) for p in pts]
        Z.patch(f"Meadow{k}", [p for p in pts], "M_Grass_Dry", GZ + 0.02, sub="Ground")
    # marsh pool with a small dock
    mc = V2(-317.0, 176.3)
    bank = G.ensure_ccw(blob_pts(mc, 7.6, 4.4, seg=18, jit=0.12, seed=4, rot=0.2))
    water = G.ensure_ccw(blob_pts(mc, 6.3, 3.3, seg=18, jit=0.12, seed=4, rot=0.2))
    mb = MeshBuilder()
    mb.tri_fill([bank, water], 0.05, "M_Dirt")
    mb.wall(bank, GZ, 0.05, "M_Dirt", closed=True)
    mb.tri_fill([water], 0.035, "M_Water")
    # dock: planks on posts reaching into the pool from the north-east bank
    d0 = mc + V2(3.6, 4.4)
    d1 = mc + V2(0.4, 0.2)
    dv = (d1 - d0).normalized()
    nv = Vector((dv.y, -dv.x))
    deck = MeshBuilder()
    Lk = (d1 - d0).length
    nplank = 8
    for i in range(nplank):
        a = d0 + dv * (Lk * i / nplank)
        b = d0 + dv * (Lk * (i + 1) / nplank - 0.05)
        q = [a - nv * 0.75, b - nv * 0.75, b + nv * 0.75, a + nv * 0.75]
        deck.prism(G.ensure_ccw(q), 0.18, 0.28, "M_Wood_Light", "M_Fence_Wood")
    for t in (0.0, 1.0):
        for sgn in (-1, 1):
            p = d0 + dv * (Lk * t) + nv * sgn * 0.7
            deck.cylinder(p.x, p.y, GZ, 0.55 if t > 0.5 else 0.3, 0.09, "M_Trim_Wood", seg=6)
    mb.extend(deck)
    Z.mesh("MarshPool", mb, "Marsh")
    # reed clumps (custom tufts, 3 colour variants). Budget pass: full tufts only in the dense
    # ZooLandingReeds hiding pocket (layout HIDING_SPOTS, by the trail at the west end); elsewhere fewer,
    # lite tufts (6 blades + 1 cattail, ~30 tris) - about 60-65 tufts in all instead of ~100.
    for k, mat in enumerate(("M_Foliage_Light", "M_Grass_Dry", "M_Hedge")):
        Z.proto(f"Reed{k}", lambda k=k, mat=mat: mb_reed(11 + k, mat))
        Z.proto(f"ReedLite{k}", lambda k=k, mat=mat: mb_reed(21 + k, mat, blades=6, heads=1))
    pocket = V2(-330.0, 169.0)
    for hs in getattr(S.layout, "HIDING_SPOTS", []):
        if hs.get("id") == "ZooLandingReeds" and hs.get("at"):
            pocket = V2(hs["at"])
    reeds = []
    centers = [(-333, 171.5, 26), (-325, 174, 18), (-308, 167.5, 8), (-292, 165, 7), (-276, 157, 6),
               (-262, 151.5, 5), (-338, 181, 5), (-312, 182, 4), (-280, 168.5, 4), (-317, 177, 11),
               (-300, 166, 4), (-268, 156, 4), (-250, 147, 3), (-344, 176, 5)]
    for cx, cy, cnt in centers:
        near = (V2(cx, cy) - pocket).length < 9.5
        jx, jy = (4.5, 2.2) if near else (2.8, 1.4)        # lite tufts clump into tighter clusters
        for _ in range(cnt):
            p = V2(cx + rnd.uniform(-jx, jx), cy + rnd.uniform(-jy, jy))
            if not ok(p, 0.3):
                continue
            if G.point_in_poly(p, water) and (p - mc).length < 4.0:
                continue
            if G.dist_point_seg(p, d0, d1) < 1.2:
                continue
            if any((p - q).length < 0.9 for q in reeds):
                continue
            dense = (p - pocket).length < 9.5
            s = rnd.uniform(0.85, 1.35) if dense else rnd.uniform(1.0, 1.4)
            key = ("Reed" if dense else "ReedLite") + str(rnd.randrange(3))
            Z.inst(key, p.x, p.y, GZ, rnd.uniform(0, TAU), sub="Reeds", scale=(s, s, s))
            reeds.append(p)
    Z.reeds_n = len(reeds)
    for k in range(2):
        Z.proto(f"Flowers{k}", lambda k=k: mb_flowers(3 + k * 5), smooth={"M_Foliage"}, angle=70)
    fl_pts = []
    for _ in range(140):
        if len(fl_pts) >= 26:
            break
        p = V2(rnd.uniform(-344, -250), rnd.uniform(150, 187))
        if not ok(p, 0.4) or any((p - q).length < 2.2 for q in fl_pts + reeds):
            continue
        if G.point_in_poly(p, bank):
            continue
        Z.inst(f"Flowers{len(fl_pts) % 2}", p.x, p.y, GZ, rnd.uniform(0, TAU), sub="Flowers",
               scale=rnd.uniform(1.4, 1.9))
        fl_pts.append(p)
    # rocks, willows, bushes
    for (x, y, piece, s) in ((-341, 182.5, "Rock_B", 1.4), (-298, 169.5, "Rock_B", 1.2), (-271, 163.5, "Rock_A", 1.5),
                             (-326, 183.0, "Rock_A", 1.1), (-255, 152.0, "Rock_B", 1.0)):
        if ok((x, y), 0.8):
            Z.put(piece, x, y, None, x, scale=(s, s, s * 0.85), sub="Rocks")
    for (x, y, s) in ((-337, 182.0, 1.0), (-288, 173.5, 0.95), (-263, 158.0, 0.85)):
        if ok((x, y), 2.0):
            Z.put("Tree_Round_B", x, y, None, x, recolor={"foliage": "M_Foliage_Light"}, scale=(s, s, s * 1.05),
                  sub="Trees")
    for (x, y) in ((-304, 175.0), (-318, 183.5), (-276, 166.0), (-345 + 6, 176.0)):
        if ok((x, y), 1.0):
            Z.put("Bush_B", x, y, None, x, recolor={"foliage": "M_Foliage_Dark"}, sub="Trees")
    # escape clues: flamingo feathers, a spilled zoo crate, a tipped fish bucket
    Z.proto("Feather", mb_feather)
    for k in range(9):
        p = V2(-322 + rnd.uniform(-9, 9), 175 + rnd.uniform(-3, 4))
        if ok(p, 0.2):
            Z.inst("Feather", p.x, p.y, GZ + 0.02, rnd.uniform(0, TAU), sub="Clues")
    Z.proto("Bucket", mb_bucket)
    for (x, y, tilt) in ((-258.5, 154.5, True), (-284.0, 170.0, True)):
        if ok((x, y), 0.3):
            Z.inst("Bucket", x, y, GZ + 0.26, x, sub="Clues", tilt=(math.pi / 2, 0.0))
    if ok((-252.5, 149.5), 0.5):
        Z.tilted("Crate", -252.5, 149.5, GZ + 0.12, math.radians(18), math.radians(-8), 0.7, sub="Clues")
    for (x, y, r) in ((-296.0, 171.0, rot_front((0.2, -1.0))), (-330.0, 177.5, rot_front((0.1, -1.0)))):
        if ok((x, y), 0.8):
            Z.put("Bench", x, y, None, r, sub="Furniture")
    Z.proto("LifeRing", mb_lifering)
    for (x, y) in ((-305.5, 165.2), (-265.0, 155.6)):
        if ok((x, y), 0.2):
            Z.inst("LifeRing", x, y, GZ, rot_front((0.2, -1.0)), sub="Furniture")
