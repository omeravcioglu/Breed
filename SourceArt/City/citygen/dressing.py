"""Phase 3b: street dressing — lights, street trees, furniture, alley clutter, parked cars,
traffic lights, bus stops and the map-edge tree belt. Everything is a linked kit instance in
06_Props/<Category>, placed deterministically from the road network and district rules.
"""
import math
import random

from mathutils import Vector

from . import config as C
from . import geom2d as G
from . import kit as K
from . import palette as P

Z_SW = C.SIDEWALK_Z
Z_ROAD = C.ROAD_Z
Z_GROUND = C.GROUND_Z


class Dresser:
    def __init__(self, ctx):
        self.ctx = ctx
        self.net = ctx["net"]
        self.world = ctx.get("world")
        self.count = {}
        self.taken = G.SegmentHash(cell=12.0)   # point obstacles (props already placed, doors)
        for b in ctx.get("placed", []):
            for d in b.get("doors", []):
                self.taken.add(d, d, 2.2, payload="door")
        # landmark sites keep a clear frontage (no street trees / planters / parked cars in front)
        self.sites = []
        for sid, site in getattr(ctx["layout"], "LANDMARKS", {}).items():
            for key in ("poly", "expansion_poly"):
                if site.get(key):
                    poly = [G.V(q) for q in site[key]]
                    self.sites.append((poly, G.bbox(poly)))

    def near_site(self, p, margin=4.0):
        for poly, bb in self.sites:
            if bb[0] - margin <= p.x <= bb[2] + margin and bb[1] - margin <= p.y <= bb[3] + margin:
                if G.point_in_poly(p, poly):
                    return True
                n = len(poly)
                if min(G.dist_point_seg(p, poly[i], poly[(i + 1) % n]) for i in range(n)) < margin:
                    return True
        return False

    def put(self, piece, cat, pos, rot, z, recolor=None, scale=None, radius=0.8):
        name = "KIT_" + piece
        if not K.has(name):
            return None
        p2 = Vector((pos[0], pos[1]))
        if radius > 0 and self.taken.blocked(p2, extra=radius):
            return None
        if cat in ("StreetTrees", "StreetFurniture", "ParkedCars") and self.near_site(p2):
            return None
        if radius > 0:
            self.taken.add(p2, p2, radius, payload=piece)
        k = self.count.get(cat, 0) + 1
        self.count[cat] = k
        return K.instance(name, f"06_Props/{cat}", (pos[0], pos[1], z), rot, recolor=recolor, scale=scale,
                          inst_name=f"PROP_{cat}_{piece}_{k:04d}"[:63])

    def lot_clear(self, poly):
        return self.world is None or self.world.lot_free(poly)


def _rot_facing(n):
    """Rotation so the piece's local +Y points along n (its front, -Y, faces -n)."""
    return math.atan2(n.y, n.x) - math.pi / 2


def _district(world, p):
    if world is None:
        return None
    d = world.district_at(p)
    return d["kind"] if d else None


def street_lights_and_trees(D):
    net, world = D.net, D.world
    for e in net.edges:
        cls = C.ROAD_CLASSES[e.cls]
        spacing = cls["lights"]
        if e.cls == "alley" or e.s1 - e.s0 < 14:
            continue
        rng = random.Random("lights:" + e.id)
        L0, L1 = e.s0 + 7.0, e.s1 - 7.0
        s = L0 + rng.uniform(0, spacing * 0.5)
        side = 1
        while s < L1:
            p = e.poly.pos(s)
            t = e.poly.tangent(s)
            n = G.left_normal(t) * side
            pos = p + n * (e.hw + 0.55)
            D.put("StreetLight", "StreetLights", pos, _rot_facing(n), Z_SW, radius=1.2)
            s += spacing
            side = -side
        # street trees on sidewalks wide enough, in leafy districts
        s = L0 + spacing * 0.5
        while s < L1:
            for side in (1, -1):
                p = e.poly.pos(s)
                n = G.left_normal(e.poly.tangent(s)) * side
                kind = _district(world, p + n * (e.hw + e.sw + 6))
                if kind in ("residential", "suburb", "petshop", "riverside") and e.sw >= 2.0 and rng.random() < 0.8:
                    pos = p + n * (e.hw + e.sw * 0.55)
                    tree = rng.choice(["Tree_Small", "Tree_Round_A", "Tree_Small"])
                    D.put(tree, "StreetTrees", pos, rng.uniform(0, 6.28), Z_SW,
                          recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Light", "M_Foliage", "M_Foliage_Autumn"])},
                          radius=2.0)
                elif kind in ("downtown", "market") and e.sw >= 3.0 and rng.random() < 0.55:
                    pos = p + n * (e.hw + 0.9)
                    D.put("Planter", "StreetFurniture", pos, _rot_facing(n), Z_SW, radius=1.4)
            s += 13.0 if e.cls != "main" else 17.0


def furniture(D):
    net, world = D.net, D.world
    for e in net.edges:
        if e.cls == "alley" or e.s1 - e.s0 < 20:
            continue
        rng = random.Random("furn:" + e.id)
        s = e.s0 + 10.0
        while s < e.s1 - 10.0:
            for side in (1, -1):
                p = e.poly.pos(s)
                n = G.left_normal(e.poly.tangent(s)) * side
                kind = _district(world, p + n * (e.hw + e.sw + 6))
                rot = _rot_facing(n)
                if kind in ("downtown", "market", "petshop") and e.sw >= 2.5:
                    r = rng.random()
                    if r < 0.35:
                        t = e.poly.tangent(s)
                        base = p + n * (e.hw + 1.0)
                        D.put("Bench", "StreetFurniture", base, rot, Z_SW, radius=1.3)
                        D.put("TrashBin", "StreetFurniture", base + t * 1.6, rot, Z_SW, radius=0.5)
                    elif r < 0.45:
                        D.put("Hydrant", "StreetFurniture", p + n * (e.hw + 0.5), rot, Z_SW, radius=0.6)
                    elif r < 0.52:
                        D.put("Mailbox", "StreetFurniture", p + n * (e.hw + 0.6), rot, Z_SW, radius=0.7)
                    elif r < 0.58:
                        D.put("BikeRack", "StreetFurniture", p + n * (e.hw + 0.9), rot, Z_SW, radius=1.2)
                elif kind in ("residential", "suburb") and rng.random() < 0.12:
                    D.put("Hydrant", "StreetFurniture", p + n * (e.hw + 0.45), rot, Z_SW, radius=0.6)
            s += rng.uniform(14.0, 24.0)


def bus_stops(D):
    mains = [e for e in D.net.edges if e.cls == "main" and e.s1 - e.s0 > 60]
    mains.sort(key=lambda e: -(e.s1 - e.s0))
    placed = 0
    for e in mains:
        if placed >= 4:
            break
        s = (e.s0 + e.s1) / 2
        p = e.poly.pos(s)
        n = G.left_normal(e.poly.tangent(s)) * (1 if placed % 2 == 0 else -1)
        pos = p + n * (e.hw + e.sw - 0.9)
        if D.put("BusStop", "StreetFurniture", pos, _rot_facing(n), Z_SW, radius=2.5):
            placed += 1


def traffic_control(D):
    net = D.net
    for nid, ends in net.ends_at.items():
        if len(ends) < 3:
            continue
        classes = sorted(C.ROAD_CLASSES[en.edge.cls]["lanes_w"] for en in ends)
        big = [en for en in ends if en.edge.cls in ("main", "secondary")]
        rng = random.Random("tl:" + nid)
        if len(big) >= 3 or (len(big) >= 2 and any(en.edge.cls == "main" for en in big)):
            for en in big:
                c = en.corners(off=1.5)
                pos = c["R"] + (c["Ro"] - c["R"]).normalized() * 0.6 if en.sw > 0 else c["R"]
                # pole on the right corner, arm reaching over the inbound lanes (toward -nR)
                nR = (c["Ro"] - c["R"]).normalized() if en.sw > 0 else G.right_normal(c["t"])
                D.put("TrafficLight", "TrafficControl", pos, _rot_facing(nR), Z_SW if en.sw > 0 else Z_GROUND, radius=1.0)
        # one street-name sign per junction
        en = ends[rng.randrange(len(ends))]
        if en.sw > 0:
            c = en.corners(off=0.5)
            q = c["L"] + (c["Lo"] - c["L"]).normalized() * 0.8
            D.put("StreetSign", "TrafficControl", q, rng.uniform(0, 6.28), Z_SW, radius=0.8)


def alleys_and_backs(D):
    net, world = D.net, D.world
    for e in net.edges:
        if e.cls != "alley":
            continue
        rng = random.Random("alley:" + e.id)
        s = e.s0 + 4.0
        while s < e.s1 - 4.0:
            side = rng.choice([1, -1])
            p = e.poly.pos(s)
            t = e.poly.tangent(s)
            n = G.left_normal(t) * side
            pos = p + n * (e.hw + 1.0)
            kind = _district(world, pos)
            rect = G.rect_corners(pos, -n, 2.4, 1.6)
            if D.lot_clear(rect):
                r = rng.random()
                if r < 0.45:
                    D.put("Dumpster", "AlleyClutter", pos, _rot_facing(n), Z_GROUND, radius=1.6)
                    if rng.random() < 0.5:
                        D.put("TrashBin", "AlleyClutter", pos + t * 1.9, rng.uniform(0, 6.28), Z_GROUND, radius=0.6)
                elif r < 0.75:
                    D.put(rng.choice(["CrateStack", "Crate", "Barrel", "Pallet"]), "AlleyClutter", pos,
                          rng.uniform(0, 6.28), Z_GROUND, radius=1.2)
            s += rng.uniform(7.0, 14.0)


def parked_cars(D):
    net, world = D.net, D.world
    for e in net.edges:
        if e.cls not in ("side", "secondary") or e.s1 - e.s0 < 30:
            continue
        rng = random.Random("cars:" + e.id)
        s = e.s0 + 9.0
        while s < e.s1 - 9.0:
            side = rng.choice([1, -1])
            p = e.poly.pos(s)
            t = e.poly.tangent(s)
            n = G.left_normal(t) * side
            kind = _district(world, p + n * (e.hw + e.sw + 6))
            prob = {"residential": 0.35, "suburb": 0.2, "downtown": 0.4, "petshop": 0.3, "market": 0.35,
                    "service": 0.3}.get(kind, 0.0)
            if rng.random() < prob:
                pos = p + n * (e.hw - 1.15)
                piece = "Car_Sedan" if rng.random() < 0.75 else ("Car_Van" if kind != "service" else "Truck_Box")
                # cars drive on the right: parked heading follows the lane on that side
                heading = t if side < 0 else -t
                rot = _rot_facing(-heading)   # car front (-Y) points along its heading
                D.put(piece, "ParkedCars", pos, rot, Z_ROAD,
                      recolor={"awning": rng.choice(P.AWNING_COLORS + ["M_Wall_White", "M_Wall_Slate"])}, radius=3.0)
            s += rng.uniform(9.0, 18.0)


def edge_forest(D):
    """Dense tree belt between the city footprint and the ground edge (keeps road exits open)."""
    rng = random.Random("forest")
    net, world = D.net, D.world
    road = net.clearance_hash(extra=3.0)
    river = D.ctx.get("river")
    rh = river.hash(extra=3.0) if river else None
    H0, H1 = C.CITY_HALF - 8, C.GROUND_HALF - 4
    step = 9.0
    y = -H1
    while y <= H1:
        x = -H1
        while x <= H1:
            if max(abs(x), abs(y)) >= H0:
                px, py = x + rng.uniform(-3.5, 3.5), y + rng.uniform(-3.5, 3.5)
                q = Vector((px, py))
                foot = G.rect_corners(q, (0, -1), 4.0, 4.0)
                if not road.blocked(q) and not (rh and rh.blocked(q)) and                         (world is None or (world.site_free(foot) and world.lot_free(foot))):
                    tree = rng.choice(["Tree_Cone", "Tree_Cone", "Tree_Round_B", "Tree_Round_A"])
                    s = rng.uniform(0.85, 1.35)
                    D.put(tree, "EdgeForest", q, rng.uniform(0, 6.28), Z_GROUND,
                          recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage_Dark", "M_Foliage_Light"])},
                          scale=(s, s, s), radius=2.5)
            x += step
        y += step


def populate(ctx):
    D = Dresser(ctx)
    street_lights_and_trees(D)
    furniture(D)
    bus_stops(D)
    traffic_control(D)
    alleys_and_backs(D)
    parked_cars(D)
    edge_forest(D)
    return dict(D.count)
