"""Phase 4 global pass: contextual dressing for every layout.HIDING_SPOTS entry.

build_all(ctx) runs after every site / area / district builder. For each hiding spot
(id, at, notes) it adds one small cluster of 2-5 props that reads as a place where an escaped
animal could hide (a nook behind bushes, a gap behind a dumpster, a tarp heap with a dark
crawl-space, a fallen log ...). GP markers are NOT created here (markers.py already does that).

How a spot is dressed
1. SKIP if the spot lies inside another landmark site / NO_BUILD area whose builder already dressed it
   (its LM_<id> collection has objects) - e.g. the Container Yard and Net Yard (service_yard.py) have
   their hiding pockets designed in, the zoo / park / courts modules dress theirs.
2. RECIPE from the notes text (bridge, reeds, thicket, hedge, crates, alley / bins, warehouses,
   allotments, court end, fallen log ...) with the district kind at that point as the fallback.
3. ANCHOR: the spot itself or the nearest free ground within ~22 m (rings of candidates). Under-bridge
   spots sit in the canal, cul-de-sac spots on the bulb asphalt, alley spots on the alley, so they move
   to the closest dry, free patch (the bridge abutment bank, the verge behind the bulb, the gap next
   to the alley). A position is free when it is clear of road corridors incl. sidewalks, turning bulbs,
   the canal + coping, ponds, footpaths, building lots (World), doors and facade fronts (setback strip /
   loading apron of every placed building), the polygons of dressed sites and the objects other landmark
   builders already placed. Among the candidates in the first rings that fit, clutter recipes prefer
   one with a wall / fence / lot edge right behind it (something to hide against).
4. ORIENTATION: the cluster's front (-Y) faces the nearest road / water / path, so the props screen a
   pocket behind them from the street; nothing is placed on roads, sidewalks or in front of doors.
5. Each cluster registers a lot so the later street dressing keeps out of it.

Custom pieces (linked duplicates of one mesh each, from service_yard.py): TarpPile (tarp-covered heap,
recoloured per recipe) and Log (fallen log for the woods). Everything else is kit.
Objects: 05_Landmarks/LM_HidingSpots/HidingSpots_<spot id>/LM_HidingSpots_<Piece>_NNN.

Report (machine-readable; markers.py / Unity tooling can consume it instead of hand-copying positions)
landmarks.built.hiding_spots[<spot id>] is a dict for EVERY layout spot (also published in this run as
ctx["hiding_anchors"]):
  status       "dressed"  cluster built by this pass (anchor = cluster origin, may be moved off the layout point)
               "site"     inside a landmark site / NO_BUILD area its own builder dressed; anchor = the nearest
                          hide point that builder published in ctx["lm_hides"][site] (e.g. the open container,
                          the upturned dinghy - see service_yard.register_hide), else the layout point
               "unplaced" no free ground found; anchor = the layout point
  at           [x, y]  layout point          anchor  [x, y]  where the hide actually is (world metres)
  z            ground / floor height at the anchor          offset_m  |anchor - at|
  heading_deg  direction the hide faces (toward the street / water it is screened from), degrees CCW from
               +X like PLAYER_SPAWN.heading_deg (a GP empty facing local -Y uses rot = heading + 90 deg);
               None when there is no preferred side
  dressed rows also carry recipe, props, front [x, y] (unit vector of heading_deg) and collection;
  site / unplaced rows carry reason (+ site, hide).
"""
import math
import random

import bpy
from mathutils import Vector

from .. import config as C
from .. import geom2d as G
from .. import lmkit
from .service_yard import _recolor_obj, dup, log_mb, place, scoped, tarp_pile_mb

# (piece, x, y, rot, scale, recolor)   cluster frame: front (-Y) faces the street / water
R = math.pi / 2
M = 3.0          # spatial-hash registration margin (see _Env)
RECIPES = {
    "bank": [("Bush_B", -1.2, 0.2, 0.3, 1.15, "M_Foliage_Dark"), ("Bush_A", 0.5, -0.35, 1.1, 1.1, "M_Foliage"),
             ("Bush_A", 1.55, 0.45, 2.0, 0.95, "M_Foliage_Light"), ("Rock_A", -0.1, 1.25, 0.6, 1.0, None),
             ("Bush_B", 0.6, 1.55, 2.6, 0.9, "M_Foliage_Dark")],
    "reeds": [("Bush_A", -1.0, 0.0, 0.2, 1.2, "M_Foliage_Light"), ("Bush_A", 0.3, -0.4, 1.4, 1.05, "M_Grass_Dry"),
              ("Bush_A", 1.3, 0.3, 2.5, 1.15, "M_Foliage_Light"), ("Bush_B", 0.1, 1.2, 0.8, 1.0, "M_Foliage"),
              ("Rock_A", -1.6, 1.2, 0.3, 0.8, None)],
    "thicket": [("Bush_B", -1.15, 0.25, 0.4, 1.15, "M_Foliage_Dark"), ("Bush_B", 1.05, 0.55, 2.1, 1.0, "M_Foliage"),
                ("Bush_A", 0.05, -0.75, 1.0, 1.0, "M_Foliage_Light"), ("Rock_B", -0.2, 1.55, 0.7, 0.9, None)],
    "hedge": [("Hedge_3m", 0.0, 1.0, 0.0, 1.0, None), ("Hedge_3m", -1.95, -0.45, R, 1.0, None),
              ("Bush_A", 1.35, 0.0, 0.7, 1.0, "M_Foliage"), ("TrashBin", 0.9, -0.9, 0.4, 1.0, None)],
    "court_end": [("Hedge_3m", 0.0, 1.2, 0.0, 1.0, None), ("Bush_B", -1.75, 0.3, 0.5, 1.05, "M_Foliage_Dark"),
                  ("TarpPile", 0.35, 0.15, 0.05, 1.0, "M_Awning_Blue"), ("Bush_A", 1.85, 0.5, 2.2, 1.0, "M_Foliage")],
    "hollow": [("Log", 0.0, 0.25, 0.25, 1.0, None), ("Bush_B", -1.8, 0.9, 0.4, 1.1, "M_Foliage_Dark"),
               ("Rock_B", 1.7, 1.0, 1.2, 1.0, None), ("Rock_A", 1.3, -0.55, 0.3, 0.9, None),
               ("Bush_A", -0.4, 1.6, 2.0, 1.0, "M_Foliage")],
    "urban": [("Dumpster", 0.0, 0.7, 0.0, 1.0, None), ("TrashBin", 1.55, 0.45, 0.5, 1.0, None),
              ("CrateStack", -1.7, 0.5, 0.25, 1.0, None), ("Pallet", -0.3, -0.55, 1.4, 1.0, None)],
    "crates": [("CrateStack", -1.0, 0.35, 0.2, 1.0, None), ("CrateStack", 0.95, 0.75, 1.3, 1.0, None),
               ("Crate", 0.05, -0.45, 0.6, 1.0, None), ("Pallet", 0.0, 1.6, 0.1, 1.0, None),
               ("Barrel", 1.9, -0.2, 0.0, 1.0, None)],
    "yard": [("TarpPile", 0.0, 0.5, 0.0, 1.0, "M_Awning_Blue"), ("Pallet", -1.75, 0.1, 0.15, 1.0, None),
             ("Barrel", 1.45, -0.1, 0.0, 1.0, None), ("Barrel", 1.85, 0.6, 1.0, 1.0, None),
             ("CrateStack", 1.6, 1.65, 0.4, 1.0, None)],
    "garden": [("Flowerbed_2m", -1.2, -0.3, 0.0, 1.0, None), ("Flowerbed_2m", 1.2, -0.3, 0.0, 1.0, None),
               ("TarpPile", 0.0, 1.2, 0.0, 0.85, "M_Awning_Green"), ("Bush_A", 2.3, 0.9, 1.0, 1.0, "M_Foliage")],
    "bank_paved": [("TarpPile", 0.0, 0.45, 0.1, 1.0, "M_Awning_Blue"), ("Planter", -1.6, 0.0, 0.0, 1.0, "M_Foliage"),
                   ("Planter", 1.55, 0.25, 0.0, 1.0, "M_Foliage_Dark"), ("Crate", 0.9, 1.5, 0.4, 1.0, None),
                   ("Barrel", -1.1, 1.4, 0.0, 1.0, None)],
    "stage": [("CrateStack", -1.3, 0.6, 0.3, 1.0, None), ("TarpPile", 0.6, 0.6, 0.1, 1.0, "M_Awning_Red"),
              ("Barrel", -0.4, -0.5, 0.0, 1.0, None), ("Barrel", 0.3, -0.75, 0.0, 1.0, None),
              ("Barrier", 1.9, -0.6, 0.4, 1.0, None)],
}
# extra pieces stacked on top of the base piece: piece -> (piece, dz)
STACK_ON = {"Pallet": ("Pallet", 0.147)}


def _recipe(notes, kind):
    t = (notes or "").lower()
    if "bridge" in t:
        return "bank"
    if "reed" in t:
        return "reeds"
    if "hollow" in t or "log" in t:
        return "hollow"
    if "end of" in t or "bulb" in t:
        return "hollow" if "wood" in t else "court_end"
    if "hedge" in t:
        return "hedge"
    if "thicket" in t or "bush" in t:
        return "thicket"
    if "allotment" in t or "bean" in t or "garden" in t and "alley" not in t:
        return "garden"
    if "stage" in t:
        return "stage"
    if "crate" in t:
        return "crates"
    if any(k in t for k in ("warehouse", "shed", "boathouse", "container", " net")):
        return "yard"
    if any(k in t for k in ("courtyard", "alley", "bins", "kennel", "behind the pet shop")):
        return "urban"
    return {"park": "thicket", "suburb": "thicket", "residential": "hedge", "downtown": "urban",
            "market": "crates", "service": "yard", "zoo": "yard", "petshop": "urban",
            "riverside": "bank"}.get(kind, "thicket")


def _site_dressed(sid):
    c = bpy.data.collections.get(f"LM_{sid}")
    return c is not None and len(c.all_objects) > 0


class _Env:
    """Everything a candidate position must stay clear of."""

    def __init__(self, ctx, S):
        layout = ctx["layout"]
        self.ctx, self.S, self.layout = ctx, S, layout
        self.world = ctx.get("world")
        # SegmentHash.blocked() only looks in the query point's cell, so segments are registered with a
        # margin (M) and queried with extra - M: a positive extra alone can miss a segment in the next cell.
        self.road = ctx["net"].clearance_hash(extra=M)
        river = ctx.get("river")
        self.river = river.hash(extra=M) if river else None
        self.bulbs = []
        for nid, nd in getattr(layout, "NODES", {}).items():
            if isinstance(nd, dict) and nd.get("culdesac"):
                self.bulbs.append((G.V(nd["pos"]), C.CULDESAC_R + 2.0))
        self.paths = G.SegmentHash(cell=16.0)
        for p in getattr(layout, "PATHS", []):
            spl, _ = G.catmull_rom([G.V(q) for q in p["path"]], step=1.5)
            self.paths.add_polyline(spl, p.get("width", 3.0) / 2 + 0.3 + M, payload=p["id"])
        self.ponds = [G.blob_polygon(pd["center"], [r + pd.get("bank", 2.0) + 0.5 for r in pd["radii"]],
                                     rot=pd.get("rot", 0.0)) for pd in getattr(layout, "PONDS", [])]
        # sites: (id, poly, dressed)
        self.sites = []
        for sid, site in getattr(layout, "LANDMARKS", {}).items():
            for key in ("poly", "expansion_poly"):
                if site.get(key):
                    self.sites.append((sid, [G.V(q) for q in site[key]], _site_dressed(sid)))
        for nb in getattr(layout, "NO_BUILD", []):
            self.sites.append((nb["id"], [G.V(q) for q in nb["poly"]], _site_dressed(nb["id"])))
        self.doors = [G.V(d) for b in ctx.get("placed", []) for d in b.get("doors", [])]
        # facade fronts (the setback strip / loading apron between sidewalk and facade) stay clear
        self.fronts, self.front_grid = [], {}
        for b in ctx.get("placed", []):
            o, n, W = G.V(b["origin"]), G.V(b["normal"]).normalized(), b["W"]
            sb = max(1.5, float(b.get("setback", 2.0))) + 0.5
            X = Vector((n.y, -n.x))
            poly = [o - X * (W / 2 + 0.5) - n * sb, o + X * (W / 2 + 0.5) - n * sb, o + X * (W / 2 + 0.5),
                    o - X * (W / 2 + 0.5)]
            k = len(self.fronts)
            self.fronts.append(poly)
            x0, y0, x1, y1 = G.bbox(poly)
            for i in range(int(math.floor(x0 / 20)), int(math.floor(x1 / 20)) + 1):
                for j in range(int(math.floor(y0 / 20)), int(math.floor(y1 / 20)) + 1):
                    self.front_grid.setdefault((i, j), []).append(k)
        self.obst = self._landmark_obstacles()
        self.mine = []            # (center, radius) of props placed by this pass

    def _landmark_obstacles(self):
        root = bpy.data.collections.get("05_Landmarks")
        if root is None:
            return G.SegmentHash(cell=12.0)
        bpy.context.view_layer.update()
        h = G.SegmentHash(cell=12.0)
        skip = bpy.data.collections.get("LM_HidingSpots")
        skip_objs = set(skip.all_objects) if skip else set()
        for o in root.all_objects:
            if o in skip_objs or o.type not in ("MESH",):
                continue
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
            y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
            z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
            if z1 - z0 < 0.2 or max(x1 - x0, y1 - y0) > 14.0:
                continue          # paving / path ribbons / big ground pieces are not obstacles
            c = Vector(((x0 + x1) / 2, (y0 + y1) / 2))
            r = 0.5 * math.hypot(x1 - x0, y1 - y0) * 0.8
            h.add(c, c, r + M, payload=o.name)
        return h

    def district(self, p):
        if self.world is not None:
            return self.world.district_at(p)
        for d in self.layout.DISTRICTS:
            if G.point_in_poly(p, [G.V(q) for q in d["poly"]]):
                return d
        return None

    def ground_z(self, p):
        z = self.S.ground_z(p.x, p.y)
        d = self.district(p)
        if d and d.get("ground"):
            z = max(z, C.GROUND_Z + 0.012)
        return z

    def free(self, p, r, own_site=None):
        p = G.V(p)
        if max(abs(p.x), abs(p.y)) > C.CITY_HALF - 2.0 - r:
            return False
        if self.road.blocked(p, extra=r + 0.4 - M):
            return False
        if self.river is not None and self.river.blocked(p, extra=r + 1.0 - M):
            return False
        if any((p - c).length < br + r + 0.4 for c, br in self.bulbs):
            return False
        if self.paths.blocked(p, extra=r - M):
            return False
        if any(G.point_in_poly(p, poly) for poly in self.ponds):
            return False
        ring = [p] + [p + Vector((math.cos(a), math.sin(a))) * r for a in (0, R, math.pi, -R)]
        for sid, poly, dressed in self.sites:
            if sid == own_site and not dressed:
                continue
            if any(G.point_in_poly(q, poly) for q in ring):
                return False
        if self.obst.blocked(p, extra=r - M):
            return False
        if any((p - c).length < cr + r for c, cr in self.mine):
            return False
        if any((p - d).length < 2.6 + r for d in self.doors):
            return False
        for q in ring:
            for k in self.front_grid.get((int(math.floor(q.x / 20)), int(math.floor(q.y / 20))), ()):
                if G.point_in_poly(q, self.fronts[k]):
                    return False
        if self.world is not None and not self.world.lot_free(G.rect_corners(p, (0, -1), 2 * r, 2 * r)):
            return False
        return True

    def open_dir(self, p):
        """Direction toward the nearest road / water / path (the side people look from)."""
        best, bd = None, 1e9
        for k in range(12):
            a = 2 * math.pi * k / 12
            d = Vector((math.cos(a), math.sin(a)))
            for s in range(1, 11):
                q = p + d * (s * 1.5)
                if self.road.blocked(q, extra=-M) or (self.river is not None and self.river.blocked(q, extra=-M)) \
                        or self.paths.blocked(q, extra=-M) or any((q - c).length < br for c, br in self.bulbs):
                    if s < bd:
                        best, bd = d, s
                    break
        return best


PIECE_R = {"Bush_A": 0.75, "Bush_B": 1.15, "Hedge_3m": 1.3, "Rock_A": 0.6, "Rock_B": 0.9, "Dumpster": 1.15,
           "TrashBin": 0.45, "CrateStack": 1.0, "Crate": 0.65, "Pallet": 0.75, "Barrel": 0.4, "Flowerbed_2m": 1.05,
           "TarpPile": 1.1, "Log": 0.95, "Barrier": 1.0, "Planter": 0.7}


def _site_of(env, p):
    for sid, poly, dressed in env.sites:
        if G.point_in_poly(p, poly):
            return sid, dressed
    return None, False


def _fit(env, anchor, front, items, own):
    """Positions for the recipe items around anchor (front = -Y of the cluster). Returns placed list."""
    f = front.normalized()
    # cluster frame: local -Y -> f  =>  local +Y -> -f ; local +X -> perpendicular (right-handed)
    Yax = -f
    Xax = Vector((Yax.y, -Yax.x))
    rot0 = math.atan2(Yax.y, Yax.x) - math.pi / 2
    out = []
    taken = []
    for piece, lx, ly, lr, sc, rc in items:
        q = anchor + Xax * lx + Yax * ly
        r = PIECE_R.get(piece, 0.8) * sc * 0.85
        if not env.free(q, r, own) or any((q - c).length < (cr + r) * 0.55 for c, cr in taken):
            continue
        taken.append((q, r))
        out.append((piece, q, rot0 + lr, sc, rc, r))
    return out


def _solid(env, p):
    """Something you could hide against: a building / yard lot or an object another builder placed."""
    if env.obst.blocked(p, extra=0.2 - M):
        return True
    return env.world is not None and not env.world.lot_free(G.rect_corners(p, (0, -1), 0.6, 0.6))


def _backing(env, anchor, front):
    """1.0 when a wall / fence / lot edge stands 1.5-4 m behind the cluster (its back = -front)."""
    b = -front.normalized()
    side = Vector((b.y, -b.x))
    for dist in (1.8, 2.6, 3.4):
        for s in (-1.0, 0.0, 1.0):
            if _solid(env, anchor + b * dist + side * s):
                return 1.0
    return 0.0


# backing preference per recipe (urban clutter wants a wall behind it, nature clusters stay near the spot)
BACK_W = {"urban": 3.0, "crates": 3.0, "yard": 2.5, "stage": 2.5, "court_end": 2.0, "hedge": 2.0,
          "garden": 1.0, "bank_paved": 2.0}


def _ground_z(env, q, r):
    """Lowest ground under the footprint (hill slopes: the uphill side sinks in, nothing floats)."""
    zs = [env.ground_z(q)] + [env.ground_z(q + Vector((math.cos(a), math.sin(a))) * r * 0.7)
                              for a in (0.0, R, math.pi, -R)]
    return min(zs) - (0.03 if max(zs) - min(zs) > 0.02 else 0.0)


def _heading(v):
    return round(math.degrees(math.atan2(v.y, v.x)), 1)


def _entry(h, status, anchor, z, heading=None, **kw):
    """One machine-readable report row (see the module docstring, "Report")."""
    at = G.V(h["at"])
    e = dict(status=status, at=[round(at.x, 2), round(at.y, 2)], anchor=[round(anchor.x, 2), round(anchor.y, 2)],
             z=round(z, 3), offset_m=round((anchor - at).length, 1), heading_deg=heading)
    e.update(kw)
    return e


def build_all(ctx):
    layout = ctx["layout"]
    S = scoped(lmkit.Site(ctx, "HidingSpots", data={}))
    env = _Env(ctx, S)
    masters = {}
    report = {}
    ctx["hiding_anchors"] = report          # same rows, for later phases of this run (markers)
    for h in getattr(layout, "HIDING_SPOTS", []):
        hid = h["id"]
        at = G.V(h["at"])
        sid, dressed = _site_of(env, at)
        if sid is not None and dressed:
            hides = ctx.get("lm_hides", {}).get(sid, [])
            if hides:                               # the site builder published designed-in hide points
                hp = min(hides, key=lambda d: (G.V((d["x"], d["y"])) - at).length)
                report[hid] = _entry(h, "site", G.V((hp["x"], hp["y"])), hp["z"], hp.get("heading_deg"),
                                     site=sid, hide=hp["name"],
                                     reason=f"inside {sid} (dressed by its site builder)")
            else:
                report[hid] = _entry(h, "site", at, env.ground_z(at), None, site=sid,
                                     reason=f"inside {sid} (dressed by its site builder)")
            continue
        rname = _recipe(h.get("notes", ""), (env.district(at) or {}).get("kind"))
        rng = random.Random("hide:" + hid)
        cands, first = [], None
        for ring in range(0, 15):
            if first is not None and ring > first + (5 if BACK_W.get(rname, 0.5) >= 2.5 else 3):
                break                               # keep searching 4.5-7.5 m past the first fit for a backing
            rr = ring * 1.5
            n = 1 if ring == 0 else max(8, int(2 * math.pi * rr / 1.5))
            for k in range(n):
                a = 2 * math.pi * (k + rng.random() * 0.3) / n
                c = at + Vector((math.cos(a), math.sin(a))) * rr
                if not env.free(c, 0.6, sid):
                    continue
                d = env.district(c)
                rn = rname
                if rn in ("bank", "thicket", "reeds") and d and d.get("ground") == "paved":
                    rn = "bank_paved"                # no bushes on pavement: planters + tarp heap instead
                items = RECIPES[rn]
                front = env.open_dir(c)
                if front is None:
                    front = (at - c).normalized() if rr > 0 else Vector((math.cos(rng.uniform(0, 6.28)),
                                                                          math.sin(rng.uniform(0, 6.28))))
                placed = _fit(env, c, front, items, sid)
                if len(placed) >= min(3, len(items)) and placed[0][0] == items[0][0]:
                    score = len(placed) + BACK_W.get(rn, 0.5) * _backing(env, c, front) - 0.12 * rr
                    cands.append((score, c, placed, rn, front))
                    if first is None:
                        first = ring
        if not cands:
            report[hid] = _entry(h, "unplaced", at, env.ground_z(at), None, recipe=rname,
                                 reason=f"no free ground within 21 m ({rname})")
            continue
        cands.sort(key=lambda t: -t[0])
        _, anchor, placed, rname, front = cands[0]
        n = 0
        for piece, q, rot, sc, rc, r in placed:
            z = _ground_z(env, q, r)
            if piece in ("TarpPile", "Log"):
                if piece not in masters:
                    mb = tarp_pile_mb(random.Random(piece)) if piece == "TarpPile" else log_mb()
                    o = place(S, piece, mb, q.x, q.y, z, rot, sub=hid, local=False)
                    masters[piece] = o
                    if rc:
                        _recolor_obj(o, rc)
                    o.scale = (sc, sc, sc)
                else:
                    dup(S, masters[piece], piece, q.x, q.y, z, rot, sub=hid, recolor=rc, scale=(sc, sc, sc))
            else:
                recolor = {"foliage": rc} if rc and piece.startswith(("Bush", "Hedge", "Planter")) else None
                sy = sc * (1.25 if (rname == "reeds" and piece == "Bush_A") else 1.0)
                S.put(piece, q.x, q.y, z, rot, recolor=recolor, scale=(sc, sc, sy), sub=hid)
                if piece in STACK_ON:
                    p2, dz = STACK_ON[piece]
                    S.put(p2, q.x, q.y, z + dz, rot + 0.08, sub=hid)
            env.mine.append((q, r))
            n += 1
        xs = [q.x for _, q, *_ in placed]
        ys = [q.y for _, q, *_ in placed]
        S.register_lot([Vector((min(xs) - 1.2, min(ys) - 1.2)), Vector((max(xs) + 1.2, min(ys) - 1.2)),
                        Vector((max(xs) + 1.2, max(ys) + 1.2)), Vector((min(xs) - 1.2, max(ys) + 1.2))])
        f = front.normalized()
        report[hid] = _entry(h, "dressed", anchor, _ground_z(env, anchor, 0.6), _heading(f), recipe=rname, props=n,
                             front=[round(f.x, 3), round(f.y, 3)], collection=f"HidingSpots_{hid}")
    return report
