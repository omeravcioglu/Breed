"""Phase 4: landmark / special-area builders.

Modules in this package build the hand-placed special areas. A module may expose:
    build(S)            for a LANDMARKS site          (S = lmkit.Site of that site)
    build_area(S)       for a NO_BUILD area           (S.data = the NO_BUILD entry)
    build_district(S)   for a whole district          (S.data = the DISTRICTS entry)
    build_all(ctx)      a global pass (e.g. hiding-spot dressing)
The maps below route every layout id to its module. Footpaths (layout.PATHS) are drawn first.
"""
import importlib
import traceback

from .. import lmkit

SITE_MODULES = {
    "PetShop": "petshop", "MapleGreen": "maple_green", "OpenLot": "open_lot",
    "Zoo": "zoo",
    "CentralPark": "park", "Lookout": "lookout",
    "TownSquare": "town_square", "Marina": "marina",
    "ServiceYard": "service_yard",
    # civic anchors (densification pass)
    "PoliceStation": "civic_services", "FireStation": "civic_services", "School": "civic_services",
    "Church": "civic_services", "VetClinic": "civic_services",
    "GasStation": "civic_commerce", "Supermarket": "civic_commerce", "Diner": "civic_commerce",
}
AREA_MODULES = {
    "ZooLanding": "zoo", "ZooForecourt": "zoo", "ZooParking": "zoo", "ZooBackLot": "zoo",
    "CrescentCommons": "park", "RiverwalkGardens": "park",
    "LanternCourt": "courts", "CobblerYard": "courts", "BoathouseSlip": "courts",
    "NetYard": "service_yard",
}
DISTRICT_MODULES = {"park": "park"}          # district kind -> module with build_district(S)
GLOBAL_MODULES = ["hiding_spots"]            # modules with build_all(ctx), run last
PATH_MATS = {"park": "M_Path", "riverwalk": "M_Plaza", "trail": "M_Dirt", "plaza": "M_Plaza"}


def build_paths(ctx):
    layout = ctx["layout"]
    S = lmkit.Site(ctx, "Paths", data={})
    n = 0
    for p in getattr(layout, "PATHS", []):
        pts = _snap_ends(p["path"], S.road_hash)
        S.path_ribbon(p["id"], pts, width=p.get("width", 3.0),
                      mat=PATH_MATS.get(p.get("kind", "park"), "M_Path"), sub=None)
        n += 1
        if p.get("kind") == "riverwalk":
            _dress_promenade(S, dict(p, path=pts), ctx)
    return n


def _snap_ends(pts, road_hash, max_gap=12.0):
    """Extend a footpath's loose ends to the nearest sidewalk edge (if one is within max_gap),
    so entrances never stop on a strip of grass."""
    from .. import geom2d as G
    P = [G.V(q) for q in pts]
    if len(P) < 2:
        return P
    for end in (0, -1):
        p = P[end]
        if road_hash.blocked(p):
            continue
        out = (p - P[1 if end == 0 else -2]).normalized()
        dirs = [out]
        # fall back to heading for the nearest corridor
        dist, e = road_hash.nearest(p, max_d=max_gap + 20.0)
        if e is not None and dist < max_gap:
            st = e.poly.stations(0.0, e.poly.length, 1.0)
            c = min((e.poly.pos(s) for s in st), key=lambda q: (q - p).length)
            dirs.append((c - p).normalized())
        hit = None
        for d in dirs:
            for k in range(1, int(max_gap / 0.5) + 1):
                q = p + d * (0.5 * k)
                if road_hash.blocked(q):
                    hit = q + d * 0.5      # tuck under the sidewalk edge (no visible seam)
                    break
            if hit is not None:
                break
        if hit is not None:
            if end == 0:
                P.insert(0, hit)
            else:
                P.append(hit)
    return P


def _dress_promenade(S, p, ctx):
    """Lamps + benches facing the water along riverwalk promenades."""
    import math
    from .. import geom2d as G
    river = ctx.get("river")
    spl, _ = G.catmull_rom([G.V(q) for q in p["path"]], step=1.0)
    pl = G.Polyline(spl)
    w = p.get("width", 3.0)
    s, k = 6.0, 0
    while s < pl.length - 6.0:
        q = pl.pos(s)
        nL = G.left_normal(pl.tangent(s))
        # which side is the water?
        wside = 1.0
        if river is not None:
            dl, _ = river.hash().nearest(q + nL * 6.0, max_d=60.0)
            dr, _ = river.hash().nearest(q - nL * 6.0, max_d=60.0)
            wside = 1.0 if dl < dr else -1.0
        land = q - nL * wside * (w / 2 + 0.6)
        water = q + nL * wside * (w / 2 + 0.5)
        face_water = math.atan2(-nL.y * wside, -nL.x * wside) - math.pi / 2   # local -Y toward the water
        if k % 2 == 0:
            if S.clear_of_roads(land, extra=0.6):
                S.put("Lamp_Park", land.x, land.y, None, face_water, sub="Promenade")
        elif S.clear_of_roads(water, extra=0.6) and S.clear_of_roads(q, extra=0.6):
            S.put("Bench", water.x, water.y, None, face_water, sub="Promenade")   # seat faces -Y = the water
        k += 1
        s += 11.0


def _mod(name, out, key):
    try:
        return importlib.import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as e:
        if name in str(e):
            out["missing"].append(f"{key}->{name}")
        else:
            out["errors"][key] = traceback.format_exc()
    except Exception:
        out["errors"][key] = traceback.format_exc()
    return None


def _run(out, key, fn, *a):
    try:
        res = fn(*a)
        out["built"][key] = res if res is not None else "ok"
    except Exception:
        out["errors"][key] = traceback.format_exc()
        print(f"[landmarks] {key} FAILED\n{out['errors'][key]}")


def build_all(ctx, only=None):
    """only: optional set of module names to build (fast iteration)."""
    layout = ctx["layout"]
    out = dict(paths=0, built={}, missing=[], errors={})
    want = (lambda m: only is None or m in only)
    try:
        out["paths"] = build_paths(ctx)
    except Exception:
        out["errors"]["paths"] = traceback.format_exc()
    for sid, site in getattr(layout, "LANDMARKS", {}).items():
        mname = SITE_MODULES.get(sid) or site.get("module") or "generic"
        if not want(mname):
            continue
        mod = _mod(mname, out, sid)
        if mod is not None and hasattr(mod, "build"):
            _run(out, sid, mod.build, lmkit.Site(ctx, sid))
    for nb in getattr(layout, "NO_BUILD", []):
        mname = AREA_MODULES.get(nb["id"])
        if not mname or not want(mname):
            continue
        mod = _mod(mname, out, nb["id"])
        if mod is not None and hasattr(mod, "build_area"):
            _run(out, nb["id"], mod.build_area, lmkit.Site(ctx, nb["id"], data=nb))
    for d in layout.DISTRICTS:
        mname = DISTRICT_MODULES.get(d["kind"])
        if not mname or not want(mname):
            continue
        mod = _mod(mname, out, "district:" + d["id"])
        if mod is not None and hasattr(mod, "build_district"):
            _run(out, "district:" + d["id"], mod.build_district, lmkit.Site(ctx, "D_" + d["id"], data=d))
    for mname in GLOBAL_MODULES:
        if not want(mname):
            continue
        mod = _mod(mname, out, mname)
        if mod is not None and hasattr(mod, "build_all"):
            _run(out, mname, mod.build_all, ctx)
    return out
