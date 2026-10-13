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
    "downtown":    dict(mix=[("mixed", 7), ("shop", 2), ("apartment", 3), ("commercial", 1)],
                        setback=(0.3, 0.7), gap=(0.0, 0.4), skip=0.03, yard=False,
                        walls=P.WALL_COLORS_DOWNTOWN, max_floors=5),
    "market":      dict(mix=[("shop", 5), ("cafe", 2), ("mixed", 2)],
                        setback=(0.3, 1.0), gap=(0.0, 1.5), skip=0.05, yard=False,
                        walls=P.WALL_COLORS_WARM + P.WALL_COLORS_COOL, max_floors=3),
    "petshop":     dict(mix=[("shop", 3), ("house", 3), ("townhouse", 2), ("cafe", 1)],
                        setback=(0.5, 3.5), gap=(1.5, 4.0), skip=0.08, yard=True,
                        walls=P.WALL_COLORS_WARM + P.WALL_COLORS_COOL, max_floors=3),
    "residential": dict(mix=[("house", 5), ("townhouse", 3), ("apartment", 1)],
                        setback=(3.0, 5.5), gap=(2.5, 6.0), skip=0.10, yard=True,
                        walls=P.WALL_COLORS_WARM + P.WALL_COLORS_COOL, max_floors=4),
    "suburb":      dict(mix=[("house", 1)],
                        setback=(6.0, 8.5), gap=(5.0, 10.0), skip=0.12, yard=True,
                        walls=["M_Wall_White", "M_Wall_Cream", "M_Wall_Sage", "M_Wall_Sky", "M_Wall_Butter",
                               "M_Wall_Lavender", "M_Wall_Mint", "M_Wall_Peach"], max_floors=2),
    "service":     dict(mix=[("warehouse", 7), ("shed", 2), ("commercial", 1)],
                        setback=(2.5, 6.0), gap=(2.0, 6.0), skip=0.08, yard=False,
                        walls=P.WALL_COLORS_INDUSTRIAL, max_floors=2),
    "riverside":   dict(mix=[("cafe", 3), ("shop", 2), ("townhouse", 1), ("mixed", 1)],
                        setback=(1.0, 3.0), gap=(2.0, 6.0), skip=0.12, yard=False,
                        walls=P.WALL_COLORS_COOL + ["M_Wall_Cream", "M_Wall_Butter"], max_floors=2),
}
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


def make_spec(arch, rng, kind, rules, seed):
    feats = {}
    if arch == "mixed":
        nw, nd, fl, gh = rng.choice([2, 3, 3, 4]), rng.choice([3, 4, 4, 5]), rng.choice([2, 3, 3, 4]), H4
    elif arch == "shop":
        nw, nd, fl, gh = rng.choice([1, 2, 2, 3]), rng.choice([3, 4]), rng.choice([1, 2, 2]), H4
    elif arch == "apartment":
        nw, nd, fl, gh = rng.choice([3, 4, 4, 5]), rng.choice([3, 4, 5]), rng.choice([3, 4, 4, 5]), H3
    elif arch == "commercial":
        nw, nd, fl, gh = rng.choice([3, 4, 5, 6]), rng.choice([4, 5, 6]), 1, H4
    elif arch == "cafe":
        nw, nd, fl, gh = rng.choice([2, 3]), rng.choice([3, 4]), 1, H4
    elif arch == "townhouse":
        nw, nd, fl, gh = 2, rng.choice([3, 4]), rng.choice([2, 2, 3]), H3
    elif arch == "house":
        nw, nd, fl, gh = rng.choice([2, 3, 3, 4]), rng.choice([2, 3, 3]), rng.choice([1, 2, 2, 2]), H3
    elif arch == "warehouse":
        nw, nd, fl, gh = rng.choice([4, 5, 6, 7]), rng.choice([4, 4, 5, 6]), 2, H4
    else:  # shed
        arch = "shed"
        nw, nd, fl, gh = rng.choice([2, 3]), rng.choice([2, 3]), 1, H3
    fl = min(fl, rules["max_floors"])
    # roof
    if arch == "house":
        roof = rng.choice(["gable_side", "gable_side", "gable_front"]) if nw in (2, 3) else "gable_side"
        if roof == "gable_side" and nd not in (2, 3):
            nd = 3
    elif arch == "townhouse":
        roof = "gable_front" if rng.random() < 0.6 else "flat"
    elif arch == "warehouse":
        roof = "gable_low" if nd == 4 else "flat"
    else:
        roof = "flat"
    # colors
    wall = rng.choice(rules["walls"])
    dark_trim = wall in ("M_Wall_Slate", "M_Wall_Corrugated") or rng.random() < 0.18
    colors = dict(wall=wall, trim="M_Trim_Dark" if dark_trim and wall not in ("M_Wall_Brick",) else "M_Trim_White",
                  door=rng.choice(P.DOOR_COLORS), awning=rng.choice(P.AWNING_COLORS),
                  roof=rng.choice(P.ROOF_COLORS),
                  sign=rng.choice(["M_Sign_Accent", "M_Awning_Teal", "M_Awning_Yellow", "M_Awning_Green", "M_Awning_Blue"]))
    if arch in ("warehouse", "shed"):
        colors["trim"] = "M_Trim_Dark" if rng.random() < 0.6 else "M_Trim_White"
        colors["roof"] = rng.choice(["M_Roof_Charcoal", "M_Roof_Slate"])
    # features
    if arch in ("shop", "cafe"):
        feats["awning"] = "fabric" if rng.random() < 0.8 else "flat"
    elif arch == "mixed":
        feats["awning"] = rng.choice(["fabric", "fabric", "flat", None])
        feats["blade_sign"] = rng.random() < 0.35
        feats["window_awnings"] = rng.random() < 0.25
        feats["water_tank"] = fl >= 3 and rng.random() < 0.35
        feats["fire_escape"] = fl >= 3 and rng.random() < 0.5
    elif arch == "commercial":
        feats["awning"] = rng.choice(["flat", "fabric", None])
        feats["billboard"] = kind == "downtown" and rng.random() < 0.3
    elif arch == "apartment":
        feats["water_tank"] = rng.random() < 0.45
        feats["roof_access"] = rng.random() < 0.5
        feats["fire_escape"] = rng.random() < 0.6
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

    def add_lot(self, poly):
        if not hasattr(self, "_lot_list"):
            self._lot_list = []
        k = len(self._lot_list)
        bb = G.bbox(poly)
        self._lot_list.append((poly, bb))
        for key in self._cells(bb):
            self.lots.setdefault(key, []).append(k)

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
    style = rng.choice(["picket", "picket", "hedge", "none"])
    if style != "none" and setback > 2.0:
        piece = "Fence_Picket_3m" if style == "picket" else "Hedge_3m"
        g0, g1 = door_x - 0.9, door_x + 0.9
        _fence_line(put, -hx, yf, g0, yf, piece, 0.0)
        _fence_line(put, g1, yf, hx, yf, piece, 0.0)
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
        if rng.random() < 0.5:
            put("Car_Sedan", gx, -min(L - 2.5, 3.0), -0.01, math.pi / 2, recolor={"awning": rng.choice(P.AWNING_COLORS)})
    if setback > 2.5:
        mx = hx - 0.8 if door_x < 0 else -hx + 0.8
        put("Mailbox_House", mx, yf + 0.4, ZG, 0.0)
        if rng.random() < 0.6:
            tx = -door_x * 0.9 if abs(door_x) > 1 else rng.choice([-1, 1]) * (W / 2 - 1.0)
            tree = rng.choice(["Tree_Round_A", "Tree_Small", "Tree_Round_B"])
            put(tree, tx, yf + setback * 0.45, ZG, rng.uniform(0, 6.28),
                recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage", "M_Foliage_Light", "M_Foliage_Dark",
                                                "M_Foliage_Autumn", "M_Foliage_Blossom"])})
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
                arch = "shed" if e.cls == "alley" else _weighted(rng, rules["mix"])
                seed = zlib.crc32(f"{e.id}:{side}:{s:.1f}".encode()) % 100000
                spec = make_spec(arch, rng, kind, rules, seed)
                ok = None
                setback = rng.uniform(*rules["setback"])
                if spec.feats.get("porch"):
                    setback = max(setback, 3.0)
                gap = rng.uniform(*rules["gap"])
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
                        side_pad = gap / 2 + (1.0 if rules["yard"] else 0.0)
                        back_extra = rng.uniform(5.0, 10.0) if rules["yard"] else 0.6
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
                if kind == "service" and K.has("KIT_Pad_1x1"):
                    # concrete loading apron between the sidewalk and the facade (+ side margins)
                    K.instance("KIT_Pad_1x1", path, (0.0, -setback / 2 - 0.05, -0.02), 0.0, parent=root,
                               scale=(Wm + 4.0, setback + 0.1, 1.0), inst_name=f"{name}.Apron"[:63])
                world.add_lot(lot if rules["yard"] else _rect(origin, n, Wm, 0.3, Dm))
                doors = [origin + X * (-Wm / 2 + 1.5 + MW * spec.feats.get("door_i", 0))]
                if spec.feats.get("garage"):
                    doors.append(origin + X * (-Wm / 2 + 1.5 + MW * spec.feats.get("garage_i", 0)))
                placed.append(dict(name=name, district=d["id"], kind=kind, archetype=spec.archetype,
                                   origin=(round(origin.x, 2), round(origin.y, 2)), normal=(n.x, n.y),
                                   W=Wm, D=Dm, floors=spec.floors, road=e.road["id"], edge=e.id, side=side,
                                   setback=setback, doors=[(round(q.x, 2), round(q.y, 2)) for q in doors],
                                   height=round(spec.wall_top() + spec.roof_height(), 1)))
                s = sc + Wm / 2 + gap / 2
    ctx["placed"] = placed
    by_arch = {}
    for b in placed:
        by_arch[b["archetype"]] = by_arch.get(b["archetype"], 0) + 1
    return dict(buildings=len(placed), pieces=pieces, by_district=counts, by_archetype=by_arch)
