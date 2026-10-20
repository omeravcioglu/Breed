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
        # kerb lane: cars only collide with cars, crosswalks, curb cuts, hydrants and bus stops
        self.lane = G.SegmentHash(cell=12.0)
        # mid-block crosswalks stay clear of parked cars / props
        for cw in getattr(ctx["layout"], "CROSSWALKS", []):
            q = G.V(cw["at"])
            self.taken.add(q, q, 6.0, payload="crosswalk")
            self.lane.add(q, q, 6.0, payload="crosswalk")
        # intersection crosswalk landings (zebra band + the sidewalk corners it lands on)
        for nid, ends in self.net.ends_at.items():
            if len(ends) < 3:
                continue
            for en in ends:
                if not C.ROAD_CLASSES[en.edge.cls]["crosswalk"]:
                    continue
                a = en.section(0.5)[0]
                b = en.section(4.5)[0]
                self.taken.add(a, b, en.hw + en.sw, payload="crosswalk")
                self.lane.add(a, b, en.hw, payload="crosswalk")
        # driveways / lot aisles meeting the kerb
        world = ctx.get("world")
        for q in (world.curb_cuts if world is not None else []):
            self.taken.add(q, q, 3.2, payload="curbcut")
            self.lane.add(q, q, 3.2, payload="curbcut")
        # doors projected onto the kerb (keep the walk line from the door to the street open)
        for b in ctx.get("placed", []):
            nrm = b.get("normal")
            if not nrm or not b.get("doors"):
                continue
            n = Vector(nrm)
            for i, d in enumerate(b["doors"]):
                q = Vector(d) - n * (b.get("setback", 0.0) + 0.8)
                r = 2.4 if i > 0 else 1.0          # second entry is a garage
                self.taken.add(q, q, r, payload="doorline")
                if i > 0:
                    self.lane.add(q, q, 2.6, payload="driveway")
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
        if radius > 0:
            if cat == "TrafficControl":
                # signals / street-name signs belong at the corners: ignore crosswalk + door-line zones
                if any(pl not in ("crosswalk", "doorline") for pl in self.taken.hits(p2, extra=radius)):
                    return None
            elif self.taken.blocked(p2, extra=radius):
                return None
        if cat in ("StreetTrees", "StreetFurniture") and self.near_site(p2):
            return None
        if cat in ("StreetLights", "PowerLines") and self.near_site(p2, margin=4.5):
            return None
        if cat in ("ParkedCars", "Traffic") and self.near_site(p2, margin=7.0):
            return None
        if radius > 0:
            self.taken.add(p2, p2, radius, payload=piece)
        if piece in ("Hydrant", "BusStop"):
            self.lane.add(p2, p2, 2.5 if piece == "Hydrant" else 4.0, payload=piece)
        k = self.count.get(cat, 0) + 1
        self.count[cat] = k
        return K.instance(name, f"06_Props/{cat}", (pos[0], pos[1], z), rot, recolor=recolor, scale=scale,
                          inst_name=f"PROP_{cat}_{piece}_{k:04d}"[:63])

    def put_car(self, piece, cat, pos, heading, z, recolor=None):
        """Car on the road: tested as a 3.6 m body segment against the kerb-lane hash only."""
        if not K.has("KIT_" + piece):
            return None
        p2 = Vector((pos[0], pos[1]))
        h = heading.normalized()
        pts = [p2 - h * 1.8, p2, p2 + h * 1.8]
        if any(self.lane.blocked(q, extra=1.0) for q in pts):
            return None
        if self.near_site(p2, margin=7.0):
            return None
        self.lane.add(pts[0], pts[-1], 0.95, payload=piece)
        k = self.count.get(cat, 0) + 1
        self.count[cat] = k
        return K.instance("KIT_" + piece, f"06_Props/{cat}", (p2.x, p2.y, z), _rot_facing(-h), recolor=recolor,
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
            if not (D.world is not None and D.world.paths.blocked(pos, extra=1.0)):
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
                elif kind in ("downtown", "market") and e.cls in ("main", "secondary") and rng.random() < 0.6:
                    # tree pits along the downtown kerbs
                    pos = p + n * (e.hw + 1.0)
                    D.put("Tree_Small", "StreetTrees", pos, rng.uniform(0, 6.28), Z_SW,
                          recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Light", "M_Foliage_Dark"])},
                          radius=1.6)
                elif kind in ("downtown", "market") and e.sw >= 3.0 and rng.random() < 0.4:
                    pos = p + n * (e.hw + 0.9)
                    D.put("Planter", "StreetFurniture", pos, _rot_facing(n), Z_SW, radius=1.4)
            s += 13.0 if e.cls != "main" else 14.0


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
                    if r < 0.5:
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
        if placed >= 8:
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


PARK_PROB = {"downtown": 0.95, "market": 0.9, "petshop": 0.65, "residential": 0.7, "suburb": 0.45,
             "service": 0.55, "riverside": 0.55}
CAR_COLORS = P.AWNING_COLORS + ["M_Wall_White", "M_Wall_Slate", "M_Trim_Dark", "M_Wall_Sky", "M_Wall_Butter"]


def _car_piece(rng, kind):
    r = rng.random()
    if kind == "service" and r < 0.3:
        return "Truck_Box"
    return "Car_Sedan" if r < 0.78 else "Car_Van"


def parked_cars(D):
    """Kerb-side parking: both kerbs on wide streets, one kerb on 6 m side streets."""
    net, world = D.net, D.world
    for e in net.edges:
        if e.cls == "alley" or e.s1 - e.s0 < 28:
            continue
        sides = (1, -1) if e.cls != "side" else ((1,) if zlib_hash(e.id) % 2 else (-1,))
        for side in sides:
            rng = random.Random(f"cars:{e.id}:{side}")
            s = e.s0 + 10.0 + rng.uniform(0, 3)
            while s < e.s1 - 10.0:
                p = e.poly.pos(s)
                t = e.poly.tangent(s)
                n = G.left_normal(t) * side
                kind = _district(world, p + n * (e.hw + e.sw + 6))
                if rng.random() < PARK_PROB.get(kind, 0.0):
                    heading = t if side < 0 else -t       # drive on the right
                    if D.put_car(_car_piece(rng, kind), "ParkedCars", p + n * (e.hw - 1.15), heading, Z_ROAD,
                                 recolor={"awning": rng.choice(CAR_COLORS)}):
                        s += rng.uniform(5.8, 7.2)
                    else:
                        s += 1.5                          # retry just past the obstacle
                else:
                    s += rng.uniform(6.0, 12.0)


def traffic(D):
    """Static traffic in the driving lanes of main / secondary roads (placeholders for a traffic system)."""
    net = D.net
    for e in net.edges:
        if e.cls not in ("main", "secondary") or e.s1 - e.s0 < 30:
            continue
        rng = random.Random("traffic:" + e.id)
        s = e.s0 + 8.0 + rng.uniform(0, 6)
        while s < e.s1 - 8.0:
            if rng.random() < 0.8:
                side = rng.choice([1, -1])
                p = e.poly.pos(s)
                t = e.poly.tangent(s)
                n = G.left_normal(t) * side
                heading = t if side < 0 else -t
                piece = rng.choice(["Car_Sedan", "Car_Sedan", "Car_Sedan", "Car_Van", "Truck_Box"])
                D.put_car(piece, "Traffic", p + n * (e.hw * 0.36), heading, Z_ROAD,
                          recolor={"awning": rng.choice(CAR_COLORS)})
            s += rng.uniform(12.0, 28.0)


POLE_KINDS = ("residential", "suburb", "service", "petshop", "riverside", "market")


def power_lines(D):
    """Wooden utility poles on one kerb of side / secondary streets, with sagging wires between them."""
    from .meshutil import MeshBuilder
    from . import scene
    net = D.net
    WZ = 8.66                     # KIT_UtilityPole meta wire_z (insulator tops)
    for e in net.edges:
        if e.cls not in ("side", "secondary") or e.s1 - e.s0 < 30 or not K.has("KIT_UtilityPole"):
            continue
        if e.road["id"] in NO_POLE_ROADS or _near_hero(D, e):
            continue
        rng = random.Random("poles:" + e.id)
        side = 1 if (zlib_hash(e.id) % 2) else -1
        poles = []
        s = e.s0 + 7.0
        while s < e.s1 - 7.0:
            p = e.poly.pos(s)
            t = e.poly.tangent(s)
            n = G.left_normal(t) * side
            kind = _district(D.world, p + n * (e.hw + e.sw + 6))
            if kind in POLE_KINDS:
                pos = p + n * (e.hw + 0.45)
                if D.put("UtilityPole", "PowerLines", pos, math.atan2(n.y, n.x), Z_SW, radius=1.4) is not None:
                    poles.append((pos, n))
                else:
                    s += 3.0
                    continue
            else:
                if len(poles) >= 2:
                    _wires(poles, e.id + f"_{len(poles)}", D)
                poles = []
            s += rng.uniform(28.0, 34.0)
        if len(poles) >= 2:
            _wires(poles, e.id, D)


NO_POLE_ROADS = ("MapleSt",)
HERO_SITES = ("PetShop", "MapleGreen", "TownSquare")


def _near_hero(D, e, dist=30.0):
    for sid in HERO_SITES:
        site = getattr(D.ctx["layout"], "LANDMARKS", {}).get(sid)
        if not site or not site.get("center"):
            continue
        c = G.V(site["center"])
        if any((e.poly.pos(s) - c).length < dist for s in e.poly.stations(e.s0, e.s1, 6.0)):
            return True
    return False


def zlib_hash(text):
    import zlib
    return zlib.crc32(text.encode())


def _wires(poles, tag, D):
    from .meshutil import MeshBuilder
    from . import scene
    mb = MeshBuilder()
    z0 = Z_SW + 8.66
    r = 0.028
    for (a, na), (b, nb) in zip(poles, poles[1:]):
        if (b - a).length > 45.0:
            continue
        for off in (-1.0, 0.0, 1.0):
            A = a + na * off
            B = b + nb * off
            pts = []
            for k in range(9):
                u = k / 8
                q = A.lerp(B, u)
                sag = 0.55 * 4 * u * (1 - u)
                pts.append(Vector((q.x, q.y, z0 - sag)))
            # thin triangular tube along the wire
            d = (B - A).normalized()
            side = Vector((-d.y, d.x, 0.0)) * r
            up = Vector((0, 0, r * 1.2))
            rings = [[p + up, p - side - up * 0.5, p + side - up * 0.5] for p in pts]
            for i in range(len(rings) - 1):
                for j in range(3):
                    j2 = (j + 1) % 3
                    mb.face([rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]], "M_Metal_Dark")
    if mb.faces:
        name = f"PROP_PowerLines_{tag}"[:63]
        scene.obj(name, mb.build(name, weld=False), "06_Props/PowerLines")


def gap_trees(D):
    """Trees in the leftover gaps between buildings (backyards, block corners), city-wide."""
    world = D.world
    if world is None:
        return
    prob = {"residential": 0.6, "suburb": 0.6, "petshop": 0.3, "riverside": 0.35, "market": 0.2,
            "downtown": 0.12, "service": 0.18}
    road = D.net.clearance_hash(extra=1.5)
    for d, poly in world.districts:
        pk = prob.get(d["kind"])
        if pk is None:
            continue
        rng = random.Random("gaptrees:" + d["id"])
        x0, y0, x1, y1 = G.bbox(poly)
        yardy = d["kind"] in ("residential", "suburb")
        step = 6.0 if yardy else 7.0
        y = y0 + step / 2
        while y < y1:
            x = x0 + step / 2
            while x < x1:
                q = Vector((x + rng.uniform(-1.8, 1.8), y + rng.uniform(-1.8, 1.8)))
                x += step
                if not G.point_in_poly(q, poly) or rng.random() > pk:
                    continue
                if road.blocked(q) or world.paths.blocked(q):
                    continue
                if world.river is not None and world.river_edge.blocked(q, extra=2.0):
                    continue
                if yardy:
                    # yards are fine; keep 2.2 m from buildings, pads, parking and sites
                    ok = world.hard_free(G.rect_corners(q, (0, -1), 4.4, 4.4))
                else:
                    ok = world.lot_free(G.rect_corners(q, (0, -1), 3.0, 3.0))
                if not ok or not world.site_free(G.rect_corners(q, (0, -1), 3.0, 3.0)):
                    continue
                tree = rng.choice(["Tree_Cone", "Tree_Cone", "Tree_Cone", "Tree_Round_A", "Tree_Round_B", "Tree_Small"])
                sc = rng.uniform(0.85, 1.25)
                D.put(tree, "GapTrees", q, rng.uniform(0, 6.28), Z_GROUND,
                      recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Dark", "M_Foliage_Light",
                                                      "M_Foliage", "M_Foliage_Autumn"])},
                      scale=(sc, sc, sc), radius=2.2)
            y += step


def edge_forest(D):
    """Dense tree belt between the city footprint and the ground edge (keeps road exits open)."""
    rng = random.Random("forest")
    net, world = D.net, D.world
    road = net.clearance_hash(extra=3.0)
    river = D.ctx.get("river")
    rh = river.hash(extra=3.0) if river else None
    H0, H1 = C.CITY_HALF - 8, C.GROUND_HALF - 4
    step = 6.5
    y = -H1
    while y <= H1:
        x = -H1
        while x <= H1:
            px, py = x + rng.uniform(-3.5, 3.5), y + rng.uniform(-3.5, 3.5)
            q = Vector((px, py))
            # map edge belt + every bit of unzoned land inside the map (no bare lawns around the town)
            if max(abs(x), abs(y)) >= H0 or (world is not None and world.district_at(q) is None):
                foot = G.rect_corners(q, (0, -1), 4.0, 4.0)
                if not road.blocked(q) and not (rh and rh.blocked(q)) and \
                        not (world is not None and world.paths.blocked(q, extra=2.5)) and                         (world is None or (world.site_free(foot) and world.lot_free(foot))):
                    tree = rng.choice(["Tree_Cone", "Tree_Cone", "Tree_Cone", "Tree_Round_B"])
                    s = rng.uniform(1.1, 1.9)
                    D.put(tree, "EdgeForest", q, rng.uniform(0, 6.28), Z_GROUND,
                          recolor={"foliage": rng.choice(["M_Foliage_Dark", "M_Foliage_Dark", "M_Foliage", "M_Foliage_Dark", "M_Foliage_Light"])},
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
    traffic(D)
    power_lines(D)
    gap_trees(D)
    edge_forest(D)
    return dict(D.count)
