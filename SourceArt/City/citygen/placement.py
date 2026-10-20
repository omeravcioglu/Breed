"""Phase 3: populate road frontage with modular buildings, district by district.

Buildings face their road and sit behind the sidewalk. Each district kind has a rule set
(archetype mix, setbacks, gaps, skip chance, yard style). Placement is deterministic and
collision checked against road corridors, the canal, reserved landmark sites, NO_BUILD areas,
parks / the zoo, and every previously placed lot.
"""
import math
import random
import zlib

from mathutils import Vector

from . import config as C
from . import geom2d as G
from . import palette as P
from . import kit as K
from . import scene
from .assembler import BuildingSpec, assemble, H3, H4, MW

RULES = {
    # pave: concrete from the sidewalk to the facade (no grass strips) ; yard: houses keep small yards
    "downtown":    dict(mix=[("mixed", 6), ("apartment", 4), ("commercial", 2), ("shop", 1)],
                        setback=(0.2, 0.5), gap=(0.0, 0.2), skip=0.0, yard=False, pave=True,
                        walls=P.WALL_COLORS_DOWNTOWN, max_floors=6),
    "market":      dict(mix=[("mixed", 4), ("shop", 4), ("cafe", 1), ("apartment", 1)],
                        setback=(0.2, 0.6), gap=(0.0, 0.3), skip=0.0, yard=False, pave=True,
                        walls=P.WALL_COLORS_WARM + P.WALL_COLORS_COOL, max_floors=4),
    "petshop":     dict(mix=[("mixed", 3), ("shop", 3), ("townhouse", 3), ("apartment", 1)],
                        setback=(0.3, 1.5), gap=(0.0, 0.6), skip=0.0, yard=False, pave=True,
                        walls=P.WALL_COLORS_WARM + P.WALL_COLORS_COOL, max_floors=4),
    "residential": dict(mix=[("townhouse", 6), ("apartment", 2), ("house", 2), ("mixed", 1)],
                        setback=(1.2, 2.5), gap=(0.0, 0.5), skip=0.0, yard="small", pave=True,
                        walls=P.WALL_COLORS_RESIDENTIAL, max_floors=4),
    "suburb":      dict(mix=[("house", 5), ("townhouse", 3), ("apartment", 1)],
                        setback=(2.0, 3.0), gap=(0.6, 1.4), skip=0.0, yard=True, pave=False,
                        walls=["M_Wall_White", "M_Wall_Cream", "M_Wall_Sage", "M_Wall_Sky", "M_Wall_Butter",
                               "M_Wall_Lavender", "M_Wall_Mint", "M_Wall_Peach", "M_Wall_Brick"], max_floors=3),
    "service":     dict(mix=[("warehouse", 6), ("commercial", 2), ("shed", 1)],
                        setback=(1.5, 4.0), gap=(0.5, 2.5), skip=0.0, yard=False, pave=True,
                        walls=P.WALL_COLORS_INDUSTRIAL, max_floors=2),
    "riverside":   dict(mix=[("mixed", 3), ("cafe", 2), ("shop", 2), ("apartment", 2)],
                        setback=(0.3, 1.5), gap=(0.0, 1.0), skip=0.0, yard=False, pave=True,
                        walls=P.WALL_COLORS_COOL + ["M_Wall_Cream", "M_Wall_Butter", "M_Wall_Brick"], max_floors=4),
}
HOUSE_GAP = (1.2, 2.0)
PASSAGE_P = {"downtown": 0.15, "market": 0.3, "riverside": 0.35, "petshop": 0.25, "residential": 0.25,
             "service": 0.4}        # detached houses always keep a side gap (side windows / driveways)
NO_BUILD_KINDS = ("park", "zoo")
CLASS_ORDER = {"main": 0, "secondary": 1, "side": 2, "alley": 3}


# ----------------------------------------------------------------------------- specs
def _weighted(rng, items):
    tot = sum(w for _, w in items)
    r = rng.uniform(0, tot)
    for it, w in items:
        r -= w
        if r <= 0:
            return it
    return items[-1][0]


def make_spec(arch, rng, kind, rules, seed, cap=None):
    feats = {}
    tall = kind in ("downtown",)
    if arch == "mixed":
        nw, nd = rng.choice([2, 3, 3, 4, 4]), rng.choice([4, 4, 5])
        fl, gh = rng.choice([4, 4, 5, 5, 6] if tall else [2, 3, 3, 4]), H4
    elif arch == "shop":
        nw, nd, fl, gh = rng.choice([2, 2, 3]), rng.choice([3, 4]), rng.choice([2, 2, 3]), H4
    elif arch == "apartment":
        nw, nd = rng.choice([3, 4, 4, 5, 6]), rng.choice([4, 4, 5])
        fl, gh = rng.choice([5, 5, 6] if tall else [3, 3, 4]), H3
    elif arch == "commercial":
        nw, nd, fl, gh = rng.choice([3, 4, 5, 6]), rng.choice([4, 5, 6]), rng.choice([1, 2, 2]), H4
    elif arch == "cafe":
        nw, nd, fl, gh = rng.choice([2, 3]), rng.choice([3, 4]), rng.choice([1, 2]), H4
    elif arch == "townhouse":
        nw, nd, fl, gh = rng.choice([2, 3, 3, 4]), rng.choice([3, 4]), rng.choice([2, 3, 3]), H3
    elif arch == "house":
        nw, nd, fl, gh = rng.choice([3, 3, 4]), 3, rng.choice([2, 2, 1]), H3
    elif arch == "warehouse":
        nw, nd, fl, gh = rng.choice([5, 6, 7, 8]), rng.choice([4, 5, 6, 7]), 2, H4
    else:  # shed
        arch = "shed"
        nw, nd, fl, gh = rng.choice([2, 3]), rng.choice([2, 3]), 1, H3
    fl = min(fl, cap if cap is not None else rules["max_floors"])
    # roof
    if arch == "house":
        roof = rng.choice(["gable_side", "gable_side", "gable_front"]) if nw in (2, 3) else "gable_side"
        if roof == "gable_side" and nd not in (2, 3):
            nd = 3
    elif arch == "townhouse":
        roof = "gable_front" if (nw in (2, 3) and rng.random() < 0.7) else "flat"
    elif arch == "warehouse":
        roof = "gable_low" if nd == 4 else "flat"
    else:
        roof = "flat"
    # colors
    wall = rng.choice(rules["walls"])
    dark_trim = wall in ("M_Wall_Slate", "M_Wall_Corrugated") or rng.random() < 0.45
    colors = dict(wall=wall, trim="M_Trim_Dark" if dark_trim and wall not in ("M_Wall_Brick", "M_Wall_BrickDark") else "M_Trim_White",
                  door=rng.choice(P.DOOR_COLORS), awning=rng.choice(P.AWNING_COLORS),
                  roof=rng.choice(P.ROOF_COLORS),
                  sign=rng.choice(["M_Sign_Accent", "M_Awning_Teal", "M_Awning_Yellow", "M_Awning_Green", "M_Awning_Blue"]),
                  flatroof=rng.choice(P.FLAT_ROOF_COLORS))
    if arch in ("warehouse", "shed"):
        colors["trim"] = "M_Trim_Dark" if rng.random() < 0.6 else "M_Trim_White"
        colors["roof"] = rng.choice(["M_Roof_Charcoal", "M_Roof_Slate"])
    # features
    if arch in ("shop", "cafe"):
        feats["awning"] = "fabric" if rng.random() < 0.8 else "flat"
    elif arch == "mixed":
        feats["awning"] = rng.choice(["fabric", "fabric", "flat", None])
        feats["blade_sign"] = rng.random() < 0.7
        feats["window_awnings"] = rng.random() < 0.25
        core = kind in ("downtown", "market")
        feats["water_tank"] = fl >= 3 and rng.random() < (0.5 if core and fl >= 5 else 0.3 if core else 0.08)
        feats["fire_escape"] = fl >= 3 and rng.random() < (0.5 if core else 0.2)
    elif arch == "commercial":
        feats["awning"] = rng.choice(["flat", "fabric", None])
        feats["billboard"] = kind == "downtown" and rng.random() < 0.3
    elif arch == "apartment":
        core = kind in ("downtown", "market")
        feats["water_tank"] = rng.random() < (0.5 if core else 0.08)
        feats["roof_access"] = rng.random() < (0.5 if core else 0.15)
        feats["fire_escape"] = rng.random() < (0.6 if core else 0.2)
        feats["fire_escape_side"] = rng.choice(["back", "left", "right"])
    elif arch in ("house", "townhouse"):
        feats["porch"] = arch == "house" and rng.random() < 0.55
        feats["chimney"] = rng.random() < 0.6
        feats["windowboxes"] = rng.random() < 0.3
        feats["window_awnings"] = fl >= 2 and rng.random() < 0.15
        if arch == "house" and nw >= 3 and rng.random() < 0.55:
            feats["garage"] = True
    return BuildingSpec(arch, nw, nd, fl, colors, roof=roof, ground_h=gh, feats=feats, seed=seed, district=kind)


# ----------------------------------------------------------------------------- collision world
class World:
    def __init__(self, ctx):
        layout, net, river = ctx["layout"], ctx["net"], ctx.get("river")
        self.layout, self.net = layout, net
        self.road = net.clearance_hash(extra=0.0)
        self.river = river.hash(extra=4.5) if river is not None else None
        self.river_edge = river.hash(extra=0.0) if river is not None else G.SegmentHash()
        self.blockers = []   # (poly, bbox)
        for sid, site in getattr(layout, "LANDMARKS", {}).items():
            for key in ("poly", "expansion_poly"):
                if site.get(key):
                    self._block([G.V(p) for p in site[key]])
        for nb in getattr(layout, "NO_BUILD", []):
            self._block([G.V(p) for p in nb["poly"]])
        for d in layout.DISTRICTS:
            if d["kind"] in NO_BUILD_KINDS:
                self._block([G.V(p) for p in d["poly"]])
        for pd in getattr(layout, "PONDS", []):
            self._block(G.blob_polygon(pd["center"], [r + 4 for r in pd["radii"]], rot=pd.get("rot", 0.0)))
        for hd in getattr(layout, "HILLS", []):
            sx, sy = hd.get("squash", (1, 1))
            r = hd["radius"]
            self._block(G.blob_polygon(hd["center"], [r * max(sx, sy) + 3] * 8))
        self.paths = G.SegmentHash(cell=16.0)
        for pth in getattr(layout, "PATHS", []):
            spl, _ = G.catmull_rom([G.V(q) for q in pth["path"]], step=2.0)
            self.paths.add_polyline(spl, pth.get("width", 3.0) / 2 + 0.8, payload=pth["id"])
        ts = getattr(layout, "LANDMARKS", {}).get("TownSquare")
        self.square = G.V(ts["center"]) if ts and ts.get("center") else None
        self.curb_cuts = []           # kerb points where lots / driveways meet the street
        self.hard = {}
        self.lots = {}
        self.cell = 20.0
        self.districts = [(d, [G.V(p) for p in d["poly"]]) for d in layout.DISTRICTS]

    def _block(self, poly):
        self.blockers.append((poly, G.bbox(poly)))

    def district_at(self, p):
        for d, poly in self.districts:
            if G.point_in_poly(p, poly):
                return d
        return None

    def _cells(self, bb):
        c = self.cell
        for i in range(int(math.floor(bb[0] / c)), int(math.floor(bb[2] / c)) + 1):
            for j in range(int(math.floor(bb[1] / c)), int(math.floor(bb[3] / c)) + 1):
                yield (i, j)

    def lot_free(self, poly):
        bb = G.bbox(poly)
        seen = set()
        for key in self._cells(bb):
            for k in self.lots.get(key, ()):
                if k in seen:
                    continue
                seen.add(k)
                op, obb = self._lot_list[k]
                if G.bbox_overlap(bb, obb) and G.polys_overlap(poly, op):
                    return False
        return True

    def add_lot(self, poly, soft=False):
        """Register an occupied area. soft=True: yards (trees may grow there, buildings may not)."""
        if not hasattr(self, "_lot_list"):
            self._lot_list = []
        k = len(self._lot_list)
        bb = G.bbox(poly)
        self._lot_list.append((poly, bb))
        for key in self._cells(bb):
            self.lots.setdefault(key, []).append(k)
            if not soft:
                self.hard.setdefault(key, []).append(k)

    def hard_free(self, poly):
        """Like lot_free, but ignores soft yard lots (footprints, pads, parking, sites only)."""
        bb = G.bbox(poly)
        seen = set()
        for key in self._cells(bb):
            for k in self.hard.get(key, ()):
                if k in seen:
                    continue
                seen.add(k)
                op, obb = self._lot_list[k]
                if G.bbox_overlap(bb, obb) and G.polys_overlap(poly, op):
                    return False
        return True

    def site_free(self, poly):
        bb = G.bbox(poly)
        for bp, bbb in self.blockers:
            if G.bbox_overlap(bb, bbb) and G.polys_overlap(poly, bp):
                return False
        return True

    def ground_free(self, footprint):
        for p in G.sample_poly_points(footprint, step=1.5, interior=True):
            if max(abs(p.x), abs(p.y)) > C.CITY_HALF - 3:
                return False
            if self.road.blocked(p, extra=0.35):
                return False
            if self.river is not None and self.river.blocked(p):
                return False
            if self.paths.blocked(p):
                return False
        return True


def _rect(origin, n, W, y0, y1, xpad=0.0):
    """Polygon in building frame: x in [-W/2-xpad, W/2+xpad], y in [y0, y1] (y along n)."""
    X = Vector((n.y, -n.x))
    hw = W / 2 + xpad
    return [origin + X * (-hw) + n * y0, origin + X * hw + n * y0, origin + X * hw + n * y1, origin + X * (-hw) + n * y1]


# ----------------------------------------------------------------------------- yards
ZG = C.GROUND_Z - C.LOT_Z   # ground level in building-local z (buildings sit on a plinth at LOT_Z)


def _fence_line(A_put, x0, y0, x1, y1, piece, rot):
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.8 or not K.has("KIT_" + piece):
        return
    n = max(1, round(L / 3.0))
    sx = L / (3.0 * n)
    for k in range(n):
        t = (k + 0.5) / n
        A_put(piece, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ZG, rot, scale=(sx, 1.0, 1.0))


def add_yard(root, spec, setback, side_pad, back_y, rng, path):
    """Front fence / hedges / paths / mailbox / tree for houses (children of the building root)."""
    W, D = spec.W, spec.D
    k = [0]

    def put(piece, x, y, z, rot, scale=None, recolor=None):
        name = "KIT_" + piece
        if not K.has(name):
            return None
        k[0] += 1
        return K.instance(name, path, (x, y, z), rot, parent=root, recolor=recolor, scale=scale,
                          inst_name=f"{root.name}.Y.{piece}.{k[0]}"[:63])

    hx = W / 2 + side_pad
    yf = -setback + 0.7          # front fence line, just behind the sidewalk
    di = spec.feats.get("door_i", 0)
    door_x = -W / 2 + 1.5 + MW * di
    gx = -W / 2 + 1.5 + MW * spec.feats.get("garage_i", 0) if spec.feats.get("garage") else None
    style = rng.choice(["picket", "picket", "hedge", "none"])
    if style != "none" and setback > 2.0:
        piece = "Fence_Picket_3m" if style == "picket" else "Hedge_3m"
        # openings: the front gate and (if any) the driveway
        cuts = sorted([(door_x - 0.9, door_x + 0.9)] + ([(gx - 1.6, gx + 1.6)] if gx is not None else []))
        x = -hx
        for c0, c1 in cuts:
            if c0 > x:
                _fence_line(put, x, yf, c0, yf, piece, 0.0)
            x = max(x, c1)
        if x < hx:
            _fence_line(put, x, yf, hx, yf, piece, 0.0)
        if style == "picket":
            put("Gate_Picket", door_x, yf, ZG, 0.0)
    # side + back privacy fences
    side_piece = rng.choice(["Fence_Wood_3m", "Hedge_3m", "Fence_Picket_3m"])
    if side_pad > 0.6:
        _fence_line(put, hx, max(yf, 0.5), hx, back_y, side_piece, math.pi / 2)
        _fence_line(put, -hx, max(yf, 0.5), -hx, back_y, side_piece, math.pi / 2)
        _fence_line(put, -hx, back_y, hx, back_y, "Fence_Wood_3m", 0.0)
    # walkway to the door, driveway to the garage
    if setback > 0.8:
        L = setback + 0.1
        put("Pad_1x1", door_x, -L / 2, 0.0, 0.0, scale=(1.4, L, 1.0))
    if spec.feats.get("garage"):
        gx = -W / 2 + 1.5 + MW * spec.feats.get("garage_i", 0)
        L = setback + 0.1
        put("Pad_1x1", gx, -L / 2, -0.01, 0.0, scale=(2.9, L, 1.0))
        if setback >= 5.0 and rng.random() < 0.5:     # only when the driveway is long enough
            put("Car_Sedan", gx, -(2.15 + 0.4), -0.01, 0.0, recolor={"awning": rng.choice(P.AWNING_COLORS)})
    if setback > 2.5:
        mx = hx - 0.8 if door_x < 0 else -hx + 0.8
        put("Mailbox_House", mx, yf + 0.4, ZG, 0.0)
        tx = -door_x * 0.9 if abs(door_x) > 1 else rng.choice([-1, 1]) * (W / 2 - 1.0)
        if rng.random() < 0.6 and (gx is None or abs(tx - gx) > 2.5) and setback >= 3.0:
            # small species only: a front-yard crown must stay clear of the facade
            tree = "Tree_Small" if setback < 4.5 else "Tree_Round_A"
            put(tree, tx, -(setback * 0.5), ZG, rng.uniform(0, 6.28),
                recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage", "M_Foliage_Light", "M_Foliage_Dark",
                                                "M_Foliage_Autumn", "M_Foliage_Blossom"])})
    if back_y - D > 3.5 and rng.random() < 0.7:
        deep = back_y - D
        tree = "Tree_Small" if deep < 5.0 else rng.choice(["Tree_Round_A", "Tree_Cone"])
        put(tree, rng.uniform(-W / 2.5, W / 2.5), D + min(deep * 0.6, 2.0 if deep < 5.0 else 3.2), ZG,
            rng.uniform(0, 6.28),
            recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage_Light", "M_Foliage_Autumn"])})
    # backyard flavor
    if back_y - D > 5 and rng.random() < 0.35:
        put(rng.choice(["Doghouse", "Swing", "Birdbath", "PicnicTable"]), rng.uniform(-W / 3, W / 3),
            D + (back_y - D) * 0.55, ZG, rng.uniform(-0.6, 0.6))


def _terrace(root, spec, origin, n, Wm, Dm, world, rng, path, name):
    """Cafe terrace on the quay behind a waterfront building (children of the building root)."""
    X = Vector((n.y, -n.x))
    k = 0
    depth = 0.0
    for d in (6.0, 5.0, 4.0, 3.0):          # deepest terrace that stays clear of the canal edge
        if not world.river_edge.blocked(origin + n * (Dm + d + 0.8)):
            depth = d
            break
    if depth < 3.0:
        return
    K.instance("KIT_Pad_1x1", path, (0.0, Dm + depth / 2, -0.01), 0.0, parent=root,
               scale=(Wm, depth, 1.0), inst_name=f"{name}.Terrace"[:63])
    for i in range(spec.nw):
        x = -Wm / 2 + 1.5 + MW * i
        if rng.random() < 0.75 and K.has("KIT_CafeTable"):
            k += 1
            K.instance("KIT_CafeTable", path, (x + rng.uniform(-0.3, 0.3), Dm + depth * 0.55, 0.0),
                       rng.uniform(-0.3, 0.3), parent=root, inst_name=f"{name}.Cafe{k}"[:63])
    if K.has("KIT_Planter"):
        for x in (-Wm / 2 + 0.5, Wm / 2 - 0.5):
            K.instance("KIT_Planter", path, (x, Dm + depth - 0.4, 0.0), 0.0, parent=root,
                       inst_name=f"{name}.Planter{x:+.0f}"[:63])


LOT_BACK = {"service": 12.0, "downtown": 4.0, "market": 4.0, "petshop": 3.0, "riverside": 2.0, "residential": 4.0}


def _lot_pad(root, path, name, kind, Wm, Dm, gap, setback, rules, world=None, origin=None, n=None):
    """Urban lot paving: one pad from the sidewalk edge, under the building, into the back lot.

    Neighbouring pads may overlap slightly on curves; they share material and height so the
    overlap is invisible. Residential districts only pave the frontage (backyards stay green).
    """
    piece = "KIT_PadGravel_1x1" if kind == "service" and K.has("KIT_PadGravel_1x1") else "KIT_Pad_1x1"
    back = LOT_BACK.get(kind, 0.0)
    if back > 0 and world is not None:
        # shrink the back lot until it stays clear of the canal, roads and reserved sites
        W2 = Wm + gap
        while back > 0.5:
            rect = _rect(origin, n, W2, Dm, Dm + back)
            pts = G.sample_poly_points(rect, step=2.0, interior=True)
            if all(not world.river_edge.blocked(q, extra=1.0) and not world.road.blocked(q, extra=0.2)
                   for q in pts) and world.site_free(rect):
                break
            back -= 1.0
        if back <= 0.5:
            back = 0.0
    y0 = -max(setback, 0.0) + 0.05
    y1 = (Dm + back) if back > 0 else 0.1
    if y1 - y0 < 0.2:
        return
    K.instance(piece, path, (0.0, (y0 + y1) / 2, 0.0), 0.0, parent=root,
               scale=(Wm + gap - 0.04, y1 - y0, 1.0), inst_name=f"{name}.LotPad"[:63])
    if world is not None and back > 0:
        world.add_lot(_rect(origin, n, Wm + gap, Dm, Dm + back))


# ----------------------------------------------------------------------------- main
def populate(ctx):
    net = ctx["net"]
    world = World(ctx)
    ctx["world"] = world
    edges = sorted(net.edges, key=lambda e: (CLASS_ORDER[e.cls], -e.poly.length))
    placed = []
    counts = {}
    pieces = 0
    for e in edges:
        for side in (1, -1):
            rng = random.Random(f"{e.id}:{side}")
            s, end = e.s0 + 2.0, e.s1 - 2.0
            guard = 0
            while s < end - 3.0 and guard < 400:
                guard += 1
                p0 = e.poly.pos(s + 4.0)
                t0 = e.poly.tangent(s + 4.0)
                n0 = G.left_normal(t0) * side
                probe = p0 + n0 * (e.hw + e.sw + 9.0)
                d = world.district_at(probe)
                if d is None or d["kind"] not in RULES:
                    s += 4.0
                    continue
                kind = d["kind"]
                rules = RULES[kind]
                if e.cls == "alley" and kind not in ("service", "downtown", "market"):
                    break
                if rng.random() < (rules["skip"] if e.cls != "alley" else 0.55):
                    s += rng.uniform(6.0, 14.0)
                    continue
                cap = None
                near_end = (s - e.s0) < 14.0 or (e.s1 - s) < 18.0
                if e.cls == "alley":
                    # downtown / market back lanes get small 2-storey commercial backs, elsewhere sheds
                    arch = "commercial" if kind in ("downtown", "market") else "shed"
                    cap = 2
                elif kind in ("residential", "petshop") and e.cls in ("main", "secondary"):
                    # corridor spines: shops below, flats above
                    arch = _weighted(rng, [("mixed", 4), ("shop", 2), ("apartment", 3), ("townhouse", 2)])
                    cap = 5
                elif kind in ("residential", "petshop", "market") and near_end and rng.random() < 0.6:
                    arch = rng.choice(["mixed", "shop"])          # corner stores
                else:
                    arch = _weighted(rng, rules["mix"])
                if e.cls == "side" and kind in ("residential", "petshop", "suburb"):
                    cap = min(cap or 3, 3)
                if world.square is not None and (p0 - world.square).length < 60.0:
                    cap = min(cap or 4, 4)                           # keep the clock tower on top
                seed = zlib.crc32(f"{e.id}:{side}:{s:.1f}".encode()) % 100000
                spec = make_spec(arch, rng, kind, rules, seed, cap=cap)
                ok = None
                setback = rng.uniform(*rules["setback"])
                if spec.feats.get("porch"):
                    setback = max(setback, 3.0)
                if spec.archetype == "house":
                    gap = rng.uniform(*HOUSE_GAP)
                elif rules["yard"] is True:
                    gap = rng.uniform(*rules["gap"])
                else:
                    # attached city fabric: flush party walls, with a walkable passage every few lots
                    gap = rng.uniform(2.6, 3.6) if rng.random() < PASSAGE_P.get(kind, 0.25) else 0.0
                nd_opts = sorted({spec.nd, max(2, spec.nd - 1), max(2, spec.nd - 2)}, reverse=True)
                nw_min = 3 if spec.archetype in ("warehouse", "commercial") else 1
                nw_opts = sorted({spec.nw, max(nw_min, spec.nw - 1), max(nw_min, spec.nw - 2)}, reverse=True)
                if spec.roof == "gable_low":          # low-pitch roofs need exactly 4 modules of depth;
                    nd_opts = sorted(set(nd_opts) | {4}, reverse=True)   # other depths fall back to flat
                for nw in nw_opts:
                    for nd in nd_opts:
                        if spec.roof == "gable_side" and nd not in (2, 3):
                            continue
                        if spec.roof == "gable_front" and nw not in (2, 3):
                            continue

                        Wm, Dm = nw * MW, nd * MW
                        sc = s + Wm / 2 + gap / 2
                        if sc + Wm / 2 > end:
                            continue
                        pc = e.poly.pos(sc)
                        tc = e.poly.tangent(sc, h=Wm / 2)
                        n = G.left_normal(tc) * side
                        origin = pc + n * (e.hw + e.sw + setback)
                        foot = _rect(origin, n, Wm, 0.3, Dm)
                        yard = rules["yard"]
                        side_pad = gap / 2 + (0.5 if yard is True else 0.2 if yard else 0.0)
                        back_extra = rng.uniform(4.0, 7.0) if yard is True else rng.uniform(2.5, 4.5) if yard else 0.6
                        lot = _rect(origin, n, Wm, -setback + 0.6, Dm + back_extra, xpad=max(side_pad, 0.05))
                        if not world.ground_free(foot):
                            continue
                        if not world.site_free(lot if rules["yard"] else foot):
                            continue
                        test_lot = lot if rules["yard"] else _rect(origin, n, Wm - 0.1, 0.35, Dm - 0.1)
                        if not world.lot_free(test_lot):
                            continue
                        ok = (nw, nd, Wm, Dm, origin, n, lot, side_pad, back_extra, setback)
                        break
                    if ok:
                        break
                if not ok:
                    s += 2.5
                    continue
                nw, nd, Wm, Dm, origin, n, lot, side_pad, back_extra, setback = ok
                spec.nw, spec.nd = nw, nd
                if spec.roof == "gable_low" and nd != 4:
                    spec.roof = "flat"
                if spec.feats.get("garage"):
                    di = spec.feats.setdefault("door_i", 1 if nw >= 3 else 0)
                    spec.feats["garage_i"] = 0 if di != 0 else nw - 1
                    if spec.feats["garage_i"] == di:
                        spec.feats["garage"] = False
                # exposed sides (corner buildings get dressed side facades)
                X = Vector((n.y, -n.x))
                for sname, mid, outward in (("right", origin + X * (Wm / 2) + n * (Dm / 2), X),
                                            ("left", origin - X * (Wm / 2) + n * (Dm / 2), -X),
                                            ("back", origin + n * Dm, n)):
                    spec.exposed[sname] = world.road.blocked(mid + outward * 9.0, extra=3.0)
                # waterfront: the back faces the canal -> shopfronts + a cafe terrace on the quay
                if world.river is not None and spec.archetype in ("shop", "cafe", "mixed", "commercial") and                         any(world.river.blocked(origin + n * (Dm + dd)) for dd in (6.0, 11.0, 16.0, 21.0, 26.0, 31.0, 36.0)):
                    spec.feats["waterfront"] = True
                    spec.exposed["back"] = True
                rot = math.atan2(n.y, n.x) - math.pi / 2
                path = f"04_Buildings/BLD_{d['id']}"
                idx = counts.get(d["id"], 0) + 1
                counts[d["id"]] = idx
                name = f"BLD_{d['id']}_{idx:03d}_{spec.archetype}"
                root, cnt = assemble(spec, name, origin, rot, path)
                pieces += cnt
                if rules["yard"] and spec.archetype in ("house", "townhouse"):
                    add_yard(root, spec, setback, side_pad, Dm + back_extra, rng, path)
                if spec.feats.get("waterfront"):
                    _terrace(root, spec, origin, n, Wm, Dm, world, rng, path, name)
                if rules.get("pave") and spec.archetype != "house":
                    _lot_pad(root, path, name, kind, Wm, Dm, gap, setback, rules, world, origin, n)
                if rules["yard"]:
                    world.add_lot(lot, soft=True)
                world.add_lot(_rect(origin, n, Wm, 0.3, Dm))
                doors = [origin + X * (-Wm / 2 + 1.5 + MW * spec.feats.get("door_i", 0))]
                if spec.feats.get("garage"):
                    doors.append(origin + X * (-Wm / 2 + 1.5 + MW * spec.feats.get("garage_i", 0)))
                placed.append(dict(name=name, district=d["id"], kind=kind, archetype=spec.archetype,
                                   origin=(round(origin.x, 2), round(origin.y, 2)), normal=(n.x, n.y),
                                   W=Wm, D=Dm, floors=spec.floors, road=e.road["id"], edge=e.id, side=side,
                                   setback=setback, doors=[(round(q.x, 2), round(q.y, 2)) for q in doors],
                                   height=round(spec.wall_top() + spec.roof_height(), 1)))
                s = sc + Wm / 2 + gap / 2
    n_front = len(placed)
    infill(ctx, world, placed, counts)
    ctx["placed"] = placed
    by_arch = {}
    for b in placed:
        by_arch[b["archetype"]] = by_arch.get(b["archetype"], 0) + 1
    return dict(buildings=len(placed), frontage=n_front, infill=len(placed) - n_front, pieces=pieces,
                by_district=counts, by_archetype=by_arch)


# ----------------------------------------------------------------------------- block interiors
# Second-row buildings, garages, warehouses and parking lots fill what the frontage pass left
# empty inside each block, so blocks read as a busy city instead of buildings floating in lawns.
INFILL = {
    "downtown":    [("commercial", 3), ("mixed", 2), ("parking", 3)],
    "market":      [("shop", 2), ("commercial", 2), ("parking", 3), ("shed", 1)],
    "petshop":     [("townhouse", 2), ("shed", 2), ("parking", 2), ("commercial", 1)],
    "residential": [("apartment", 2), ("townhouse", 3), ("shed", 1), ("parking", 2)],
    "suburb":      [("house", 2), ("shed", 4), ("parking", 1)],
    "service":     [("warehouse", 4), ("shed", 2), ("parking", 3)],
    "riverside":   [("shed", 2), ("parking", 2), ("townhouse", 1)],
}
INFILL_STEP = 5.5
INFILL_MAX_KERB = 28.0        # infill only within this distance of a street corridor


def _closest_on_edge(e, p):
    best_s, best_d = 0.0, 1e9
    for s in e.poly.stations(0.0, e.poly.length, 2.0):
        d = (e.poly.pos(s) - p).length
        if d < best_d:
            best_s, best_d = s, d
    for k in range(-8, 9):
        s = min(max(best_s + k * 0.25, 0.0), e.poly.length)
        d = (e.poly.pos(s) - p).length
        if d < best_d:
            best_s, best_d = s, d
    return e.poly.pos(best_s)


def _parking(world, origin, n, W, D, name, path, rng):
    """Asphalt lot with stall lines and parked cars. Stalls 2.6 x 5 m along the back (and front if deep)."""
    rot = math.atan2(n.y, n.x) - math.pi / 2
    root = scene.empty(name, path, (origin.x, origin.y, C.ROAD_Z + 0.03), rot, display="PLAIN_AXES", size=1.5,
                       props=dict(lot_kind="parking", lot_w=W, lot_d=D))
    K.instance("KIT_LotAsphalt_1x1", path, (0.0, D / 2, 0.0), 0.0, parent=root, scale=(W, D, 1.0),
               inst_name=f"{name}.Asphalt"[:63])
    rows = [(D - 5.0, math.pi)] + ([(0.0, 0.0)] if D >= 15.0 else [])
    n_st = max(1, int((W - 1.0) // 2.6))
    x0 = -n_st * 2.6 / 2
    k = 0
    for (y0, crot) in rows:
        for i in range(n_st + 1):
            K.instance("KIT_ParkingLine", path, (x0 + i * 2.6, y0 + 2.5, 0.0), 0.0, parent=root,
                       inst_name=f"{name}.Line{k}"[:63])
            k += 1
        for i in range(n_st):
            if rng.random() < 0.7:
                piece = "Car_Sedan" if rng.random() < 0.8 else "Car_Van"
                K.instance("KIT_" + piece, path, (x0 + (i + 0.5) * 2.6, y0 + 2.5, 0.0),
                           crot + rng.uniform(-0.05, 0.05), parent=root,
                           recolor={"awning": rng.choice(P.AWNING_COLORS + ["M_Wall_White", "M_Wall_Slate", "M_Trim_Dark"])},
                           inst_name=f"{name}.Car{i}_{k}"[:63])
    if K.has("KIT_StreetLight") and W >= 12:
        K.instance("KIT_StreetLight", path, (-W / 2 + 0.6, D / 2, 0.0), -math.pi / 2, parent=root,
                   inst_name=f"{name}.Light"[:63])
    return root


def _orientations(n):
    """Facing candidates: toward the nearest street first, then the two side streets, then away."""
    return [n, Vector((-n.y, n.x)), Vector((n.y, -n.x)), -n]


def _aisle(world, origin, n, max_len=INFILL_MAX_KERB + 4.0):
    """Length of a straight 5 m driveway from a lot front (origin, facing -n) to the kerb, or None."""
    X = Vector((n.y, -n.x))
    L = 0.0
    while L < max_len:
        L += 0.5
        q = origin - n * L
        if world.road.blocked(q) or world.road.blocked(q + X * 2.0) or world.road.blocked(q - X * 2.0):
            break
    else:
        return None
    if L < 1.0:
        return None
    L += 0.35                                   # tuck under the sidewalk
    strip = _rect(origin, n, 5.0, -(L - 0.9), -0.2)
    if not world.lot_free(strip) or not world.site_free(strip):
        return None
    if any(world.river is not None and world.river.blocked(q) for q in G.sample_poly_points(strip, 2.0)):
        return None
    if any(world.paths.blocked(q) for q in G.sample_poly_points(strip, 2.0)):
        return None
    return L


def infill(ctx, world, placed, counts):
    road = world.road
    for d, poly in world.districts:
        kind = d["kind"]
        if kind not in INFILL:
            continue
        rules = RULES[kind]
        rng = random.Random("infill:" + d["id"])
        x0, y0, x1, y1 = G.bbox(poly)
        pts = []
        y = y0 + INFILL_STEP / 2
        while y < y1:
            x = x0 + INFILL_STEP / 2
            while x < x1:
                q = Vector((x + rng.uniform(-1.5, 1.5), y + rng.uniform(-1.5, 1.5)))
                if G.point_in_poly(q, poly):
                    pts.append(q)
                x += INFILL_STEP
            y += INFILL_STEP
        rng.shuffle(pts)
        for p in pts:
            if road.blocked(p, extra=4.0):
                continue
            probe = G.rect_corners(p, (0, 1), 4.0, 4.0)
            if not world.lot_free(probe) or not world.site_free(probe):
                continue
            dist, e = road.nearest(p, max_d=150.0)
            if e is None or dist > INFILL_MAX_KERB:
                continue
            q = _closest_on_edge(e, p)
            if (p - q).length < 1e-3:
                continue
            n = (p - q).normalized()
            arch = _weighted(rng, INFILL[kind])
            spec = None
            if arch == "parking":
                sizes = [(18.2, 15.0), (15.6, 15.0), (13.0, 12.0), (10.4, 10.0)]
            else:
                seed = zlib.crc32(f"infill:{d['id']}:{p.x:.1f}:{p.y:.1f}".encode()) % 100000
                spec = make_spec(arch, rng, kind, rules, seed)
                if spec.roof == "gable_low":
                    spec.roof = "flat"
                cand = [(spec.nw, spec.nd), (max(2, spec.nw - 1), spec.nd), (max(2, spec.nw - 1), max(2, spec.nd - 1)),
                        (2, 2)]
                if spec.roof == "gable_front":
                    cand = [(w, dd) for (w, dd) in cand if w in (2, 3)] or [(2, 2)]
                sizes = [(w * MW, dd * MW) for (w, dd) in cand]
            done = False
            for (Wm, Dm) in sizes:
                for nn in _orientations(n):
                    origin = p - nn * (Dm / 2)
                    foot = _rect(origin, nn, Wm, 0.0, Dm)
                    lot = _rect(origin, nn, Wm, -0.9, Dm + 0.9, xpad=0.9)
                    if not all(G.point_in_poly(c, poly) for c in foot):
                        continue
                    if not world.ground_free(lot) or not world.site_free(lot) or not world.lot_free(lot):
                        continue
                    aisle = None
                    if spec is None:
                        aisle = _aisle(world, origin, nn)
                        if aisle is None:
                            continue
                    else:
                        apron = _rect(origin, nn, Wm, -2.4, -0.9)
                        if not world.lot_free(apron) or not world.site_free(apron) or not world.ground_free(apron):
                            continue
                    n = nn
                    done = True
                    break
                if done:
                    break
            if done:
                idx = counts.get(d["id"], 0) + 1
                counts[d["id"]] = idx
                path = f"04_Buildings/BLD_{d['id']}"
                if spec is None:
                    name = f"LOT_{d['id']}_{idx:03d}_parking"
                    root = _parking(world, origin, n, Wm, Dm, name, path, rng)
                    L = aisle
                    K.instance("KIT_LotAsphalt_1x1", path, (0.0, -L / 2 + 0.2, 0.0), 0.0, parent=root,
                               scale=(5.0, L + 0.4, 1.0), inst_name=f"{name}.Aisle"[:63])
                    world.add_lot(_rect(origin, n, 5.0, -L, 0.0))
                    world.curb_cuts.append(origin - n * (L - 0.3))
                    placed_arch, floors = "parking", 0
                else:
                    spec.nw, spec.nd = int(round(Wm / MW)), int(round(Dm / MW))
                    if spec.roof == "gable_side" and spec.nd not in (2, 3):
                        spec.roof = "flat"
                    spec.feats.pop("garage", None)
                    if spec.archetype != "house":
                        spec.feats.pop("porch", None)
                    name = f"BLD_{d['id']}_{idx:03d}_{spec.archetype}"
                    rot = math.atan2(n.y, n.x) - math.pi / 2
                    root, _ = assemble(spec, name, origin, rot, path)
                    if rules.get("pave") and kind != "residential":
                        piece = "KIT_PadGravel_1x1" if kind == "service" and K.has("KIT_PadGravel_1x1") else "KIT_Pad_1x1"
                        K.instance(piece, path, (0.0, Dm / 2, 0.0), 0.0, parent=root,
                                   scale=(Wm + 2.4, Dm + 2.4, 1.0), inst_name=f"{name}.LotPad"[:63])
                    placed_arch, floors = spec.archetype, spec.floors
                world.add_lot(_rect(origin, n, Wm, -0.6, Dm + 0.6, xpad=0.6))
                if spec is not None:
                    world.add_lot(_rect(origin, n, Wm, -2.4, -0.6))        # keep the doorstep apron open
                placed.append(dict(name=name, district=d["id"], kind=kind, archetype=placed_arch,
                                   origin=(round(origin.x, 2), round(origin.y, 2)), normal=(n.x, n.y),
                                   W=Wm, D=Dm, floors=floors, road=None, edge=None, side=0, setback=0.0,
                                   doors=[], infill=True))
