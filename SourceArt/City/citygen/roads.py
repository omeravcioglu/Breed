"""Phase 1: road network -> asphalt ribbons, intersection patches, sidewalks, markings, bridges.

Graph model
-----------
layout.NODES  : {node_id: (x, y)  or  dict(pos=(x, y), culdesac=True, exit=True)}
layout.ROADS  : list of dict(id, name, cls, path=[node_id | (x, y), ...], width?, sidewalk?)
    * A road's centerline is a centripetal Catmull-Rom spline through every path point.
    * Roads are split into edges at nodes shared by 2+ roads (intersections) and at path ends.
    * A node used by a single road in its interior is just a named control point.

Intersections are built CityEngine-style: each incident road is trimmed back, corner fillets
are computed from the curb lines, and the junction is filled with one star-shaped patch.
"""
import math
from collections import defaultdict

from mathutils import Vector

from . import config as C
from . import geom2d as G
from .meshutil import MeshBuilder
from . import scene


class Edge:
    def __init__(self, eid, road, poly, a, b):
        self.id = eid
        self.road = road
        cls = C.ROAD_CLASSES[road["cls"]]
        self.cls = road["cls"]
        self.hw = road.get("width", cls["lanes_w"]) * 0.5
        self.sw = road.get("sidewalk", cls["sidewalk"])
        self.R = road.get("curb_r", cls["curb_r"])
        self.poly = poly
        self.a, self.b = a, b
        self.ta = 0.0
        self.tb = 0.0

    @property
    def s0(self):
        return self.ta

    @property
    def s1(self):
        return self.poly.length - self.tb


class End:
    """One edge end at a node. dir points AWAY from the node along the edge."""

    def __init__(self, edge, at_start):
        self.edge = edge
        self.start = at_start
        L = edge.poly.length
        look = min(5.0, L * 0.3)
        if at_start:
            self.dir = (edge.poly.pos(look) - edge.poly.pts[0]).normalized()
        else:
            self.dir = (edge.poly.pos(L - look) - edge.poly.pts[-1]).normalized()
        self.hw, self.sw, self.R = edge.hw, edge.sw, edge.R

    @property
    def trim(self):
        return self.edge.ta if self.start else self.edge.tb

    @trim.setter
    def trim(self, v):
        if self.start:
            self.edge.ta = max(self.edge.ta, v)
        else:
            self.edge.tb = max(self.edge.tb, v)

    def section(self, off=0.0):
        """Actual ribbon cross-section at the trim. Returns (p, t_out, nL, nR) in outward frame."""
        e = self.edge
        s = e.ta + off if self.start else e.poly.length - e.tb - off
        p = e.poly.pos(s)
        t = e.poly.tangent(s)
        if not self.start:
            t = -t
        return p, t, G.left_normal(t), G.right_normal(t)

    def corners(self, off=0.0):
        p, t, nL, nR = self.section(off)
        return dict(L=p + nL * self.hw, R=p + nR * self.hw,
                    Lo=p + nL * (self.hw + self.sw), Ro=p + nR * (self.hw + self.sw), p=p, t=t)


class Network:
    def __init__(self, layout):
        self.layout = layout
        self.nodes = {}
        self.edges = []
        self.ends_at = defaultdict(list)
        self.corners = {}           # node -> list of corner dicts
        self.warnings = []
        self.bridges = []           # (edge, s0, s1)
        self._build_graph()
        self._compute_trims()

    # ------------------------------------------------------------------ graph
    def _build_graph(self):
        for k, v in self.layout.NODES.items():
            if isinstance(v, dict):
                d = dict(v)
                d["pos"] = G.V(v["pos"])
            else:
                d = dict(pos=G.V(v))
            self.nodes[k] = d
        roads = []
        for r in self.layout.ROADS:
            r = dict(r)
            path = list(r["path"])
            for idx in (0, -1):
                if not isinstance(path[idx], str):
                    nid = f"{r['id']}__{'start' if idx == 0 else 'end'}"
                    self.nodes[nid] = dict(pos=G.V(path[idx]))
                    path[idx] = nid
            r["path"] = path
            roads.append(r)
        self.roads = roads
        usage = defaultdict(int)
        for r in roads:
            for p in r["path"]:
                if isinstance(p, str):
                    if p not in self.nodes:
                        raise KeyError(f"Road {r['id']} references unknown node {p!r}")
                    usage[p] += 1
        self.usage = usage
        for r in roads:
            path = r["path"]
            pts = [self.nodes[p]["pos"] if isinstance(p, str) else G.V(p) for p in path]
            samples, idx = G.catmull_rom(pts, step=C.SPLINE_STEP)
            r["_samples"] = samples
            splits = [k for k, p in enumerate(path)
                      if isinstance(p, str) and (usage[p] >= 2 or k in (0, len(path) - 1))]
            for i in range(len(splits) - 1):
                k0, k1 = splits[i], splits[i + 1]
                poly = G.Polyline(samples[idx[k0]: idx[k1] + 1])
                e = Edge(f"{r['id']}_{i:02d}", r, poly, path[k0], path[k1])
                self.edges.append(e)
        for e in self.edges:
            self.ends_at[e.a].append(End(e, True))
            self.ends_at[e.b].append(End(e, False))

    # ------------------------------------------------------------------ trims & corners
    def _compute_trims(self):
        for nid, ends in self.ends_at.items():
            N = self.nodes[nid]["pos"]
            ends.sort(key=lambda en: G.angle_of(en.dir))
            k = len(ends)
            corners = []
            if k == 1:
                en = ends[0]
                if self.nodes[nid].get("culdesac"):
                    # trim where the sidewalk's outer edge meets the outer bulb circle
                    Rb = max(C.CULDESAC_R, en.hw + 2.0)
                    w = en.hw + en.sw
                    en.trim = math.sqrt(max((Rb + en.sw) ** 2 - w * w, 0.0)) + 0.01
                self.corners[nid] = corners
                continue
            for i in range(k):
                a, b = ends[i], ends[(i + 1) % k]
                th = G.ccw_angle(a.dir, b.dir)
                c = dict(a=a, b=b, th=th, fillet=False)
                if th < math.radians(150):
                    da, db = a.dir, b.dir
                    pa = N + G.left_normal(da) * a.hw
                    pb = N + G.right_normal(db) * b.hw
                    res = G.line_intersect(pa, da, pb, db)
                    if res is not None:
                        Cp = pa + da * res[0]
                        R = min(a.R, b.R)
                        kt = R / math.tan(th / 2)
                        Ta, Tb = Cp + da * kt, Cp + db * kt
                        bis = (da + db).normalized()
                        O = Cp + bis * (R / math.sin(th / 2))
                        # outer (property) lines
                        qa = N + G.left_normal(da) * (a.hw + a.sw)
                        qb = N + G.right_normal(db) * (b.hw + b.sw)
                        res2 = G.line_intersect(qa, da, qb, db)
                        P = qa + da * res2[0] if res2 else Cp
                        Ro = R - max(a.sw, b.sw)
                        if Ro >= 1.0:
                            kto = Ro / math.tan(th / 2)
                            Toa, Tob = P + da * kto, P + db * kto
                            Oo = P + bis * (Ro / math.sin(th / 2))
                        else:
                            Toa = Tob = P
                            Oo = None
                        sa = max((Ta - N).dot(da), (Toa - N).dot(da), (P - N).dot(da))
                        sb = max((Tb - N).dot(db), (Tob - N).dot(db), (P - N).dot(db))
                        if -30 <= sa < 60 and -30 <= sb < 60:
                            c.update(fillet=True, C=Cp, Ta=Ta, Tb=Tb, O=O, R=R, P=P, Ro=Ro,
                                     Toa=Toa, Tob=Tob, Oo=Oo)
                            a.trim = max(sa, 0.0) + 0.6
                            b.trim = max(sb, 0.0) + 0.6
                        else:
                            self.warnings.append(f"node {nid}: degenerate corner ({math.degrees(th):.0f} deg)")
                    if th < math.radians(35):
                        self.warnings.append(f"node {nid}: very acute angle {math.degrees(th):.0f} deg")
                corners.append(c)
            # straight-through / reflex corners still need the ribbons to clear each other
            for en in ends:
                if en.trim < 0.5:
                    en.trim = max(o.hw + o.sw for o in ends if o is not en) * 0.6
            self.corners[nid] = corners
        for e in self.edges:
            if e.s1 - e.s0 < 3.0:
                self.warnings.append(f"edge {e.id}: too short after trimming ({e.s1 - e.s0:.1f}m)")

    # ------------------------------------------------------------------ queries
    def clearance_hash(self, extra=0.0, include_sidewalk=True):
        """SegmentHash of every road centerline with radius = half width (+ sidewalk) + extra."""
        h = G.SegmentHash(cell=16.0)
        for e in self.edges:
            r = e.hw + (e.sw if include_sidewalk else 0.0) + extra
            pts = e.poly.pts[::2] + [e.poly.pts[-1]]
            h.add_polyline(pts, r, payload=e)
        # cul-de-sac turning bulbs are wider than the street corridor
        for nid, ends in self.ends_at.items():
            if len(ends) == 1 and self.nodes[nid].get("culdesac"):
                en = ends[0]
                Rb = max(C.CULDESAC_R, en.hw + 2.0)
                p = self.nodes[nid]["pos"]
                h.add(p, p, Rb + (en.sw if include_sidewalk else 0.0) + extra, payload=en.edge)
        return h


# =============================================================================== geometry
def _ribbon_stations(e):
    return e.poly.stations(e.s0, e.s1, C.RIBBON_STEP)


def build(layout, river_hash=None):
    """Build all road geometry. Returns the Network for later phases."""
    net = Network(layout)
    for w in net.warnings:
        print("[roads] WARN", w)

    road_meshes = {}
    for e in net.edges:
        key = e.road["id"]
        if key not in road_meshes:
            road_meshes[key] = dict(asph=MeshBuilder(), sw=MeshBuilder(), mk=MeshBuilder(), road=e.road)
        rm = road_meshes[key]
        if e.s1 - e.s0 < 0.5:
            continue
        st = _ribbon_stations(e)
        P = [e.poly.pos(s) for s in st]
        T = [e.poly.tangent(s) for s in st]
        NL = [G.left_normal(t) for t in T]
        left = [p + n * e.hw for p, n in zip(P, NL)]
        right = [p - n * e.hw for p, n in zip(P, NL)]
        mat = "M_Asphalt_Alley" if e.cls == "alley" else "M_Asphalt"
        rm["asph"].strip(left, right, mat, z=C.ROAD_Z)
        if e.sw > 0:
            lo = [p + n * (e.hw + e.sw) for p, n in zip(P, NL)]
            ro = [p - n * (e.hw + e.sw) for p, n in zip(P, NL)]
            b = rm["sw"]
            b.strip(lo, left, "M_Sidewalk", z=C.SIDEWALK_Z)
            b.wall(left, C.ROAD_Z, C.SIDEWALK_Z, "M_Curb")                       # faces road (right)
            b.wall(lo, C.SKIRT_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
            b.strip(right, ro, "M_Sidewalk", z=C.SIDEWALK_Z)
            b.wall(right, C.ROAD_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
            b.wall(ro, C.SKIRT_Z, C.SIDEWALK_Z, "M_Curb")
        else:
            rm["asph"].wall(left, C.SKIRT_Z, C.ROAD_Z, "M_Curb", outward_left=True)
            rm["asph"].wall(right, C.SKIRT_Z, C.ROAD_Z, "M_Curb")
        _markings(e, rm["mk"])

    # ---- intersections
    ix = MeshBuilder()
    ixsw = MeshBuilder()
    for nid, ends in net.ends_at.items():
        N = net.nodes[nid]["pos"]
        if len(ends) == 1:
            _dead_end(net, nid, ends[0], ix, ixsw)
            continue
        ring = []
        for c in net.corners[nid]:
            a, b = c["a"], c["b"]
            ca = a.corners()
            cb = b.corners()
            if not ring:
                pass
            ring += [ca["R"], ca["L"]]
            if c["fillet"]:
                arc = _fillet_arc(c["O"], c["Ta"], c["Tb"], c["R"])
                ring += arc
                inner = [ca["L"]] + arc + [cb["R"]]
                if c["Oo"] is not None:
                    outer = [cb["Ro"]] + _fillet_arc(c["Oo"], c["Tob"], c["Toa"], c["Ro"]) + [ca["Lo"]]
                else:
                    outer = [cb["Ro"], c["P"], ca["Lo"]]
            else:
                inner = [ca["L"], cb["R"]]
                outer = [cb["Ro"], ca["Lo"]]
            if a.sw > 0 or b.sw > 0:
                poly = _dedupe(inner + outer)
                if len(poly) >= 3:
                    ixsw.tri_fill([poly], C.SIDEWALK_Z, "M_Sidewalk")
                    ixsw.wall(_dedupe(inner), C.ROAD_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
                    ixsw.wall(_dedupe(outer), C.SKIRT_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
            else:
                # no sidewalks: asphalt edge skirt faces away from the road (toward the ground)
                ix.wall(_dedupe(inner), C.SKIRT_Z, C.ROAD_Z, "M_Curb")
        ring = _dedupe(ring)
        mat = "M_Asphalt_Alley" if all(en.edge.cls == "alley" for en in ends) else "M_Asphalt"
        ix.fan(N, ring, C.ROAD_Z, mat)
        _crosswalks(net, nid, ends, road_meshes)

    # ---- mid-block crosswalks (layout.CROSSWALKS = [dict(road=<road id>, at=(x, y))])
    for cw in getattr(layout, "CROSSWALKS", []):
        best = None
        q = G.V(cw["at"])
        for e in net.edges:
            if e.road["id"] != cw["road"]:
                continue
            for s in e.poly.stations(e.s0 + 4.0, max(e.s0 + 4.0, e.s1 - 4.0), 1.0):
                d = (e.poly.pos(s) - q).length
                if best is None or d < best[0]:
                    best = (d, e, s)
        if best is None or best[0] > 25.0:
            print(f"[roads] WARN crosswalk {cw} not near road {cw['road']}")
            continue
        _, e, s = best
        _zebra(road_meshes[e.road["id"]]["mk"], e.poly.pos(s - 1.5), e.poly.tangent(s), e.hw)

    # ---- emit objects
    for rid, rm in road_meshes.items():
        nm = rm["road"].get("name", rid).replace(" ", "")
        if rm["asph"].faces:
            o = scene.obj(f"{C.PREFIX['road']}{rid}", rm["asph"].build(f"{C.PREFIX['road']}{rid}"), "02_Roads/Roads_Surface")
            o["road_class"] = rm["road"]["cls"]
            o["road_name"] = rm["road"].get("name", rid)
        if rm["sw"].faces:
            scene.obj(f"{C.PREFIX['sidewalk']}{rid}", rm["sw"].build(f"{C.PREFIX['sidewalk']}{rid}"), "02_Roads/Roads_Sidewalks")
        if rm["mk"].faces:
            scene.obj(f"{C.PREFIX['marking']}{rid}", rm["mk"].build(f"{C.PREFIX['marking']}{rid}", weld=False), "02_Roads/Roads_Markings")
    if ix.faces:
        scene.obj(f"{C.PREFIX['intersection']}Asphalt", ix.build("IX_Asphalt"), "02_Roads/Roads_Intersections")
    if ixsw.faces:
        scene.obj(f"{C.PREFIX['intersection']}Sidewalks", ixsw.build("IX_Sidewalks"), "02_Roads/Roads_Intersections")
    return net


def _dedupe(pts, eps=0.05):
    out = []
    for p in pts:
        if not out or (p - out[-1]).length > eps:
            out.append(p)
    if len(out) > 2 and (out[0] - out[-1]).length < eps:
        out.pop()
    return out


def _fillet_arc(O, T0, T1, R, seg_len=0.8):
    a0 = G.angle_of(T0 - O)
    a1 = G.angle_of(T1 - O)
    d = a1 - a0
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    n = max(2, int(math.ceil(abs(d) * R / seg_len)))
    return [O + Vector((math.cos(a0 + d * k / n), math.sin(a0 + d * k / n))) * R for k in range(n + 1)]


def _dead_end(net, nid, en, ix, ixsw):
    nd = net.nodes[nid]
    N = nd["pos"]
    c = en.corners()
    if nd.get("culdesac"):
        Rb = max(C.CULDESAC_R, en.hw + 2.0)
        t_out = c["t"]
        nL, nR = G.left_normal(t_out), G.right_normal(t_out)
        s_in = math.sqrt(max(Rb * Rb - en.hw * en.hw, 0.0))
        Lc = N + t_out * s_in + nL * en.hw     # where the curbs meet the bulb circle
        Rc = N + t_out * s_in + nR * en.hw
        # bulb goes the long way round, from the left curb (CCW) back to the right curb
        arc = G.arc_points(N, Rb, G.angle_of(Lc - N), G.angle_of(Rc - N), ccw=True, seg_len=1.0)
        inner = _dedupe([c["L"], Lc] + arc + [Rc, c["R"]])
        ix.fan(N, inner, C.ROAD_Z, "M_Asphalt")
        if en.sw > 0:
            Ro = Rb + en.sw
            outer = [c["Ro"]] + G.arc_points(N, Ro, G.angle_of(c["Ro"] - N), G.angle_of(c["Lo"] - N),
                                             ccw=False, seg_len=1.0) + [c["Lo"]]
            ixsw.tri_fill([_dedupe(inner + outer)], C.SIDEWALK_Z, "M_Sidewalk")
            ixsw.wall(inner, C.ROAD_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
            ixsw.wall(_dedupe(outer), C.SKIRT_Z, C.SIDEWALK_Z, "M_Curb", outward_left=True)
        else:
            ix.wall(inner, C.SKIRT_Z, C.ROAD_Z, "M_Curb")
        return
    if nd.get("exit") or max(abs(N.x), abs(N.y)) > C.CITY_HALF - 1:
        return
    # plain dead end: curb cap across the end
    p, t = c["p"], c["t"]
    back = -t
    if en.sw > 0:
        w = en.hw + en.sw
        nL = G.left_normal(t)
        cap = [p + nL * w, p + nL * w + back * en.sw, p - nL * w + back * en.sw, p - nL * w]
        ixsw.prism(cap, C.SKIRT_Z, C.SIDEWALK_Z, "M_Sidewalk", "M_Curb")
    else:
        ix.wall([c["R"], c["L"]], C.SKIRT_Z, C.ROAD_Z, "M_Curb", outward_left=True)


def _markings(e, mk):
    cls = C.ROAD_CLASSES[e.cls]
    style = e.road.get("marking", cls["marking"])
    if not style:
        return
    s0, s1 = e.s0 + 5.0, e.s1 - 5.0
    if s1 - s0 < 2:
        return
    if style == "double_yellow":
        for off in (0.17, -0.17):
            pts = e.poly.offset(off, s0, s1, step=C.RIBBON_STEP)
            pts2 = e.poly.offset(off - 0.12, s0, s1, step=C.RIBBON_STEP)
            mk.strip(pts, pts2, "M_RoadLine_Yellow", z=C.MARK_Z)
    elif style == "dashed_white":
        s = s0
        while s + 3.0 <= s1:
            a = e.poly.offset(0.08, s, s + 3.0, step=1.5)
            b = e.poly.offset(-0.08, s, s + 3.0, step=1.5)
            mk.strip(a, b, "M_RoadLine_White", z=C.MARK_Z)
            s += 7.0


def _zebra(mk, p, t, hw, depth=3.0):
    """Zebra stripes across a road: stripes run along t from p for *depth* meters."""
    nL = G.left_normal(t)
    w = hw - 0.4
    n = int((2 * w) / 1.1)
    for i in range(n + 1):
        o = -w + i * (2 * w / max(n, 1))
        c0, c1 = p + nL * (o - 0.3), p + nL * (o + 0.3)
        quad3 = [Vector((v.x, v.y, C.MARK_Z)) for v in (c0, c0 + t * depth, c1 + t * depth, c1)]
        nrm = (quad3[1] - quad3[0]).cross(quad3[2] - quad3[1])
        mk.face(quad3 if nrm.z > 0 else quad3[::-1], "M_RoadLine_White")


def _crosswalks(net, nid, ends, road_meshes):
    if len(ends) < 3:
        return
    for en in ends:
        cls = C.ROAD_CLASSES[en.edge.cls]
        if not cls["crosswalk"]:
            continue
        mk = road_meshes[en.edge.road["id"]]["mk"]
        p, t, nL, nR = en.section(1.0)
        depth = 3.0
        w = en.hw - 0.4
        n = int((2 * w) / 1.1)
        for i in range(n + 1):
            o = -w + i * (2 * w / max(n, 1))
            c0 = p + nL * (o - 0.3)
            c1 = p + nL * (o + 0.3)
            quad = [c0, c0 + t * depth, c1 + t * depth, c1]
            quad3 = [Vector((q.x, q.y, C.MARK_Z)) for q in quad]
            nrm = (quad3[1] - quad3[0]).cross(quad3[2] - quad3[1])
            mk.face(quad3 if nrm.z > 0 else quad3[::-1], "M_RoadLine_White")
        # stop line across the inbound (right-hand) half
        sp, st, snL, snR = en.section(depth + 1.5)
        a0, a1 = sp, sp + snR * (en.hw - 0.3)
        quad = [a0, a1, a1 + st * 0.4, a0 + st * 0.4]
        quad3 = [Vector((q.x, q.y, C.MARK_Z)) for q in quad]
        nrm = (quad3[1] - quad3[0]).cross(quad3[2] - quad3[1])
        mk.face(quad3 if nrm.z > 0 else quad3[::-1], "M_RoadLine_White")


# =============================================================================== bridges
def build_bridges(net, river_poly, river_hw):
    """Deck fascia, underside and railings wherever a road crosses the river corridor."""
    if river_poly is None:
        return
    rh = G.SegmentHash(cell=16.0)
    rh.add_polyline(river_poly.pts[::2] + [river_poly.pts[-1]], river_hw + 1.0, payload="river")
    count = 0
    for e in net.edges:
        st = e.poly.stations(0.0, e.poly.length, 1.0)
        inside = [rh.blocked(e.poly.pos(s)) for s in st]
        ranges, cur = [], None
        for s, f in zip(st, inside):
            if f and cur is None:
                cur = [s, s]
            elif f:
                cur[1] = s
            elif cur is not None:
                ranges.append(cur)
                cur = None
        if cur is not None:
            ranges.append(cur)
        for s0, s1 in ranges:
            s0, s1 = max(0.0, s0 - 2.5), min(e.poly.length, s1 + 2.5)
            b = MeshBuilder()
            w = e.hw + e.sw
            stations = e.poly.stations(s0, s1, 1.0)
            P = [e.poly.pos(s) for s in stations]
            NL = [G.left_normal(e.poly.tangent(s)) for s in stations]
            lo = [p + n * w for p, n in zip(P, NL)]
            ro = [p - n * w for p, n in zip(P, NL)]
            deck_bot = -0.95
            b.wall(lo, deck_bot, C.SIDEWALK_Z, "M_CanalStone", outward_left=True)
            b.wall(ro, deck_bot, C.SIDEWALK_Z, "M_CanalStone")
            b.strip(ro, lo, "M_CanalStone", z=deck_bot)  # underside, normal down
            # railings: posts + a flat top rail 0.08..0.22m in from each deck edge
            for line, sgn in ((lo, -1.0), (ro, 1.0)):
                for i, (p, n) in enumerate(zip(line, NL)):
                    if i % 2 == 0:
                        q = p + n * sgn * 0.15
                        b.box(q.x - 0.1, q.y - 0.1, C.SIDEWALK_Z, q.x + 0.1, q.y + 0.1, C.SIDEWALK_Z + 1.0, "M_Metal_Dark")
                edge_side = [p + n * sgn * 0.08 for p, n in zip(line, NL)]
                road_side = [p + n * sgn * 0.22 for p, n in zip(line, NL)]
                top = C.SIDEWALK_Z + 1.0
                if sgn < 0:   # left railing: edge_side is further left
                    b.strip(edge_side, road_side, "M_Metal_Dark", z=top + 0.08)
                else:
                    b.strip(road_side, edge_side, "M_Metal_Dark", z=top + 0.08)
                b.wall(edge_side, top, top + 0.08, "M_Metal_Dark", outward_left=(sgn < 0))
                b.wall(road_side, top, top + 0.08, "M_Metal_Dark", outward_left=(sgn > 0))
            name = f"{C.PREFIX['bridge']}{e.road['id']}_{count:02d}"
            scene.obj(name, b.build(name, weld=False), "02_Roads/Roads_Bridges")
            net.bridges.append((e, s0, s1))
            count += 1
