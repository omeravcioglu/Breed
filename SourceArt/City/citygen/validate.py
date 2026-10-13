"""Layout validator: catches road/district/water problems before geometry is trusted.

Returns a dict(errors=[...], warnings=[...], stats={...}). Errors mean the layout must be fixed.
"""
import math

from . import config as C
from . import geom2d as G


def _dist_boundary(p, poly):
    n = len(poly)
    return min(G.dist_point_seg(p, poly[i], poly[(i + 1) % n]) for i in range(n))


def validate(layout, net, river=None):
    errors, warns = [], list(net.warnings)
    H = C.CITY_HALF

    # -- road edges crossing each other without a shared node
    segs = []
    for e in net.edges:
        pts = e.poly.pts[::3] + [e.poly.pts[-1]]
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1], e))
    grid = {}
    cell = 20.0
    for k, (a, b, e) in enumerate(segs):
        for gx in range(int(math.floor(min(a.x, b.x) / cell)), int(math.floor(max(a.x, b.x) / cell)) + 1):
            for gy in range(int(math.floor(min(a.y, b.y) / cell)), int(math.floor(max(a.y, b.y) / cell)) + 1):
                grid.setdefault((gx, gy), []).append(k)
    reported = set()
    for cellk, ids in grid.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a0, a1, ea = segs[ids[i]]
                b0, b1, eb = segs[ids[j]]
                if ea is eb:
                    continue
                if {ea.a, ea.b} & {eb.a, eb.b}:
                    continue
                if G.seg_intersect(a0, a1, b0, b1):
                    key = tuple(sorted((ea.id, eb.id)))
                    if key not in reported:
                        reported.add(key)
                        errors.append(f"roads cross without an intersection node: {ea.id} x {eb.id} near "
                                      f"({a0.x:.0f},{a0.y:.0f})")

    # -- parallel roads too close (ribbons overlapping) - sample check
    h = net.clearance_hash(extra=0.0)
    close = set()
    for e in net.edges:
        for s in e.poly.stations(e.s0 + 2, max(e.s0 + 2, e.s1 - 2), 6.0):
            p = e.poly.pos(s)
            for other in h.hits(p, extra=e.hw + e.sw - 0.5):
                if other is e or other.road is e.road:
                    continue
                if {other.a, other.b} & {e.a, e.b}:
                    # near a shared node this is expected
                    na = net.nodes[e.a]["pos"]
                    nb = net.nodes[e.b]["pos"]
                    if min((p - na).length, (p - nb).length) < 45:
                        continue
                key = tuple(sorted((e.id, other.id)))
                if key not in close:
                    close.add(key)
                    warns.append(f"roads overlap/too close: {e.id} ~ {other.id} near ({p.x:.0f},{p.y:.0f})")

    # -- tight curves
    for e in net.edges:
        L = e.poly.length
        for s in e.poly.stations(e.s0, e.s1, 4.0):
            t0 = e.poly.tangent(max(0, s - 4))
            t1 = e.poly.tangent(min(L, s + 4))
            ang = math.acos(max(-1.0, min(1.0, t0.dot(t1))))
            if ang > 1e-3:
                radius = 8.0 / ang
                if radius < e.hw + e.sw + 1.0:
                    p = e.poly.pos(s)
                    warns.append(f"curve too tight on {e.id} (r~{radius:.1f}m) near ({p.x:.0f},{p.y:.0f})")
                    break

    # -- nodes out of bounds
    for nid, nd in net.nodes.items():
        p = nd["pos"]
        if max(abs(p.x), abs(p.y)) > C.GROUND_HALF:
            errors.append(f"node {nid} outside ground ({p.x:.0f},{p.y:.0f})")

    # -- district polygons
    dists = layout.DISTRICTS
    for d in dists:
        P = [G.V(p) for p in d["poly"]]
        if len(P) < 3:
            errors.append(f"district {d['id']} has < 3 points")
            continue
        if any(max(abs(p.x), abs(p.y)) > C.GROUND_HALF for p in P):
            warns.append(f"district {d['id']} extends beyond the ground")
        # self intersection
        n = len(P)
        for i in range(n):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                if G.seg_intersect(P[i], P[(i + 1) % n], P[j], P[(j + 1) % n]):
                    errors.append(f"district {d['id']} polygon self-intersects")
                    break
        if river is not None:
            rh = river.hash()
            hit = [p for p in G.sample_poly_points(P, step=4.0, interior=True) if rh.blocked(p)]
            if hit and d.get("ground"):
                errors.append(f"district {d['id']} (ground={d['ground']}) overlaps the river at "
                              f"({hit[0].x:.0f},{hit[0].y:.0f}) - its ground plate would cover water")
            elif hit:
                warns.append(f"district {d['id']} overlaps the river ({len(hit)} samples)")
    for i in range(len(dists)):
        for j in range(i + 1, len(dists)):
            A = [G.V(p) for p in dists[i]["poly"]]
            B = [G.V(p) for p in dists[j]["poly"]]
            if not G.bbox_overlap(G.bbox(A), G.bbox(B)):
                continue
            # ignore samples on/near B's boundary so districts may share an edge exactly
            pa = [p for p in G.sample_poly_points(A, step=5.0, interior=True)
                  if G.point_in_poly(p, B) and _dist_boundary(p, B) > 1.0]
            if len(pa) > 6:
                warns.append(f"districts overlap: {dists[i]['id']} & {dists[j]['id']} (~{len(pa) * 25} m2)")

    # -- reserved sites vs roads / river
    road_h = net.clearance_hash(extra=0.0)
    areas = []
    for sid, site in getattr(layout, "LANDMARKS", {}).items():
        if site.get("expansion_poly"):
            areas.append((f"{sid}.expansion_poly", site["expansion_poly"]))
    for nb in getattr(layout, "NO_BUILD", []):
        areas.append((f"NO_BUILD {nb['id']}", nb["poly"]))
    for aid, poly in areas:
        pts = G.sample_poly_points([G.V(p) for p in poly], step=2.0, interior=True)
        bad = [p for p in pts if road_h.blocked(p)]
        if bad:
            warns.append(f"{aid} overlaps road/sidewalk at ({bad[0].x:.0f},{bad[0].y:.0f}) ({len(bad)} samples)")
    for sid, site in getattr(layout, "LANDMARKS", {}).items():
        poly = site.get("poly")
        if not poly:
            continue
        pts = G.sample_poly_points([G.V(p) for p in poly], step=2.0, interior=True)
        bad = [p for p in pts if road_h.blocked(p)]
        if bad:
            warns.append(f"landmark site {sid} overlaps road/sidewalk at ({bad[0].x:.0f},{bad[0].y:.0f}) "
                         f"({len(bad)} samples)")
        if river is not None:
            rb = [p for p in pts if river.hash().blocked(p)]
            if rb and not site.get("allow_water"):
                warns.append(f"landmark site {sid} overlaps the river")
    for hd in getattr(layout, "HILLS", []):
        c = G.V(hd["center"])
        r = hd["radius"] * max(hd.get("squash", (1, 1)))
        pts = [c + G.V((math.cos(a) * r * 0.85, math.sin(a) * r * 0.85)) for a in [i * math.pi / 12 for i in range(24)]] + [c]
        bad = [p for p in pts if road_h.blocked(p)]
        if bad:
            errors.append(f"hill {hd['id']} overlaps a road near ({bad[0].x:.0f},{bad[0].y:.0f})")
    for pd in getattr(layout, "PONDS", []):
        poly = G.blob_polygon(pd["center"], pd["radii"], rot=pd.get("rot", 0.0))
        bad = [p for p in G.sample_poly_points(poly, step=3.0) if road_h.blocked(p)]
        if bad:
            errors.append(f"pond {pd['id']} overlaps a road near ({bad[0].x:.0f},{bad[0].y:.0f})")

    # -- stats
    total = {}
    for e in net.edges:
        total[e.cls] = total.get(e.cls, 0.0) + e.poly.length
    deg = {}
    for nid, ends in net.ends_at.items():
        deg[len(ends)] = deg.get(len(ends), 0) + 1
    stats = dict(road_length_m={k: round(v) for k, v in total.items()}, node_degree_hist=deg,
                 edges=len(net.edges), roads=len(net.roads), districts=len(dists),
                 bridges=len(getattr(net, "bridges", [])))
    return dict(errors=errors, warnings=warns, stats=stats)
