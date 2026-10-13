"""Phase 1 terrain: ground (split by the canal, holes for ponds), canal walls/water, ponds,
hills, zoning blockout plates and map labels.

Layout data used:
    RIVER  = dict(name, path=[(x,y),...], width)       # boundary-to-boundary canal (optional)
    PONDS  = [dict(id, center, radii=[...], rot=0)]     # star-shaped blobs (holes in ground)
    HILLS  = [dict(id, center, radius, height, squash=(sx, sy), rot=0)]
    DISTRICTS = [dict(id, name, kind, poly=[...], ground=None|'paved'|'gravel'|'park')]
"""
import math

import bpy
from mathutils import Vector

from . import config as C
from . import geom2d as G
from .meshutil import MeshBuilder
from . import scene

KIND_MAT = {
    "downtown": "M_Zone_Downtown", "residential": "M_Zone_Residential", "suburb": "M_Zone_Suburb",
    "park": "M_Zone_Park", "petshop": "M_Zone_PetShop", "zoo": "M_Zone_Zoo", "service": "M_Zone_Service",
    "riverside": "M_Zone_Riverside", "market": "M_Zone_Market",
}
GROUND_MAT = {"paved": "M_Concrete", "gravel": "M_Gravel", "plaza": "M_Plaza", "park": "M_Grass_Park",
              "dirt": "M_Dirt", "sand": "M_Sand"}


class River:
    def __init__(self, data):
        self.data = data
        self.name = data.get("name", "River")
        self.hw = data["width"] * 0.5
        pts = [G.V(p) for p in data["path"]]
        # extend both ends well beyond the ground so the ground split is always clean
        for end in (0, -1):
            p = pts[end]
            q = pts[1] if end == 0 else pts[-2]
            d = (p - q).normalized()
            far = p + d * 200.0
            if end == 0:
                pts.insert(0, far)
            else:
                pts.append(far)
        samples, _ = G.catmull_rom(pts, step=2.0)
        self.poly = G.Polyline(samples)
        st = self.poly.stations(0.0, self.poly.length, 2.0)
        self.center = [self.poly.pos(s) for s in st]
        nl = [G.left_normal(self.poly.tangent(s)) for s in st]
        self.left = [p + n * self.hw for p, n in zip(self.center, nl)]
        self.right = [p - n * self.hw for p, n in zip(self.center, nl)]
        self.normals = nl

    def hash(self, extra=0.0):
        h = G.SegmentHash(cell=16.0)
        h.add_polyline(self.center, self.hw + extra, payload="river")
        return h


# ----------------------------------------------------------------------------- square helpers
def _inside(p, h):
    return abs(p.x) <= h and abs(p.y) <= h


def _boundary_hit(a, b, h):
    lo, hi = 0.0, 1.0  # a inside, b outside (or vice versa handled by caller)
    ina = _inside(a, h)
    for _ in range(40):
        m = (lo + hi) * 0.5
        if _inside(a.lerp(b, m), h) == ina:
            lo = m
        else:
            hi = m
    p = a.lerp(b, (lo + hi) * 0.5)
    # snap to the boundary exactly
    if abs(abs(p.x) - h) < abs(abs(p.y) - h):
        p.x = math.copysign(h, p.x)
    else:
        p.y = math.copysign(h, p.y)
    return p


def _clip(pts, h):
    ins = [_inside(p, h) for p in pts]
    if True not in ins:
        return None
    i0 = ins.index(True)
    i1 = len(ins) - 1 - ins[::-1].index(True)
    out = []
    if i0 > 0:
        out.append(_boundary_hit(pts[i0], pts[i0 - 1], h))
    out += [p.copy() for p in pts[i0:i1 + 1]]
    if i1 < len(pts) - 1:
        out.append(_boundary_hit(pts[i1], pts[i1 + 1], h))
    return out


def _u(p, h):
    x, y = p.x, p.y
    if abs(y + h) < 1e-3:
        return x + h
    if abs(x - h) < 1e-3:
        return 2 * h + (y + h)
    if abs(y - h) < 1e-3:
        return 4 * h + (h - x)
    return 6 * h + (h - y)


def _walk_ccw(p_from, p_to, h):
    corners = [(Vector((-h, -h)), 0.0), (Vector((h, -h)), 2 * h), (Vector((h, h)), 4 * h), (Vector((-h, h)), 6 * h)]
    u0, u1 = _u(p_from, h), _u(p_to, h)
    if u1 <= u0:
        u1 += 8 * h
    out = []
    for k in range(2):
        for c, uc in corners:
            uu = uc + 8 * h * k
            if u0 < uu < u1:
                out.append((uu, c.copy()))
    out.sort(key=lambda t: t[0])
    return [c for _, c in out]


# ----------------------------------------------------------------------------- builders
def build_ground(layout, river):
    h = C.GROUND_HALF
    holes = []
    for pd in getattr(layout, "PONDS", []):
        holes.append(G.blob_polygon(pd["center"], pd["radii"], seg_len=2.0, rot=pd.get("rot", 0.0)))
    regions = []
    if river is not None:
        lb = _clip(river.left, h)
        rb = _clip(river.right, h)
        left_region = lb + _walk_ccw(lb[-1], lb[0], h)
        rrev = rb[::-1]
        right_region = rrev + _walk_ccw(rrev[-1], rrev[0], h)
        regions = [("North", left_region), ("South", right_region)]
    else:
        sq = [Vector((-h, -h)), Vector((h, -h)), Vector((h, h)), Vector((-h, h))]
        regions = [("All", sq)]
    for name, reg in regions:
        reg = G.ensure_ccw(reg)
        my_holes = [hp for hp in holes if G.point_in_poly(G.centroid(hp), reg)]
        b = MeshBuilder()
        b.tri_fill([reg] + my_holes, C.GROUND_Z, "M_Grass")
        scene.obj(f"{C.PREFIX['terrain']}Ground_{name}", b.build(f"TRN_Ground_{name}"), "01_Terrain")


def build_canal(river, road_hash):
    if river is None:
        return
    h = C.GROUND_HALF
    walls = MeshBuilder()
    water = MeshBuilder()
    bed = MeshBuilder()
    idx = [i for i, p in enumerate(river.center) if _inside(p, h + 4.0)]
    if not idx:
        return
    i0, i1 = idx[0], idx[-1]
    L = river.left[i0:i1 + 1]
    R = river.right[i0:i1 + 1]
    NL = river.normals[i0:i1 + 1]
    water.strip(L, R, "M_Water", z=C.CANAL_WATER_Z)
    bed.strip(L, R, "M_RiverBed", z=C.CANAL_BED_Z)
    for line, sgn in ((L, 1.0), (R, -1.0)):
        for i in range(len(line) - 1):
            a, b = line[i], line[i + 1]
            under_bridge = road_hash.blocked(a) and road_hash.blocked(b)
            top = -0.95 if under_bridge else C.CANAL_COPING_Z
            seg = [a, b]
            walls.wall(seg, C.CANAL_BED_Z, top, "M_CanalStone", outward_left=(sgn < 0))
            if not under_bridge:
                ao, bo = a + NL[i] * sgn * 0.7, b + NL[i + 1] * sgn * 0.7
                if sgn > 0:
                    walls.strip([ao, bo], [a, b], "M_CanalStone", z=C.CANAL_COPING_Z)
                    walls.wall([ao, bo], C.GROUND_Z - 0.05, C.CANAL_COPING_Z, "M_CanalStone", outward_left=True)
                else:
                    walls.strip([a, b], [ao, bo], "M_CanalStone", z=C.CANAL_COPING_Z)
                    walls.wall([ao, bo], C.GROUND_Z - 0.05, C.CANAL_COPING_Z, "M_CanalStone")
    nm = river.name.replace(" ", "")
    scene.obj(f"{C.PREFIX['water']}{nm}", water.build(f"WTR_{nm}"), "01_Terrain")
    scene.obj(f"{C.PREFIX['terrain']}{nm}_Bed", bed.build(f"TRN_{nm}_Bed"), "01_Terrain")
    scene.obj(f"{C.PREFIX['terrain']}{nm}_Walls", walls.build(f"TRN_{nm}_Walls"), "01_Terrain")


def build_ponds(layout):
    for pd in getattr(layout, "PONDS", []):
        c = G.V(pd["center"])
        outline = G.blob_polygon(c, pd["radii"], seg_len=2.0, rot=pd.get("rot", 0.0))
        outline = G.ensure_ccw(outline)
        inset = G.offset_polygon_radial(outline, c, pd.get("bank", 3.0))
        water_ring = G.offset_polygon_radial(outline, c, pd.get("bank", 3.0) * 0.45)
        b = MeshBuilder()
        bz = -0.95
        n = len(outline)
        for i in range(n):
            j = (i + 1) % n
            a0, a1 = Vector((*outline[i], C.GROUND_Z)), Vector((*outline[j], C.GROUND_Z))
            b0, b1 = Vector((*inset[i], bz)), Vector((*inset[j], bz))
            # outline CCW: inner side is on the left; slope faces up/inward
            b.face([a0, a1, b1, b0], "M_Sand")
        b.fan(c, inset, bz, "M_RiverBed")
        w = MeshBuilder()
        w.fan(c, water_ring, -0.4, "M_Water")
        scene.obj(f"{C.PREFIX['terrain']}{pd['id']}_Bank", b.build(f"TRN_{pd['id']}_Bank"), "01_Terrain")
        scene.obj(f"{C.PREFIX['water']}{pd['id']}", w.build(f"WTR_{pd['id']}"), "01_Terrain")


def hill_height(hd, x, y):
    """Height of hill *hd* at world (x, y), or 0 outside."""
    c = G.V(hd["center"])
    sx, sy = hd.get("squash", (1.0, 1.0))
    rot = hd.get("rot", 0.0)
    d = Vector((x, y)) - c
    cr, sr = math.cos(-rot), math.sin(-rot)
    lx, ly = d.x * cr - d.y * sr, d.x * sr + d.y * cr
    r = math.hypot(lx / sx, ly / sy)
    R = hd["radius"]
    if r >= R:
        return 0.0
    t = r / R
    return hd["height"] * 0.5 * (1 + math.cos(math.pi * t))


def build_hills(layout):
    for hd in getattr(layout, "HILLS", []):
        c = G.V(hd["center"])
        R = hd["radius"]
        sx, sy = hd.get("squash", (1.0, 1.0))
        rot = hd.get("rot", 0.0)
        K, S = 14, 56
        rings = []
        for k in range(K + 1):
            rr = R * k / K
            row = []
            for s in range(S):
                a = 2 * math.pi * s / S
                lx, ly = rr * math.cos(a) * sx, rr * math.sin(a) * sy
                x = c.x + lx * math.cos(rot) - ly * math.sin(rot)
                y = c.y + lx * math.sin(rot) + ly * math.cos(rot)
                z = hill_height(hd, x, y) + (C.GROUND_Z - 0.03 if k == K else C.GROUND_Z)
                row.append(Vector((x, y, z)))
            rings.append(row)
        b = MeshBuilder()
        top = Vector((c.x, c.y, hd["height"] + C.GROUND_Z))
        for s in range(S):
            t = (s + 1) % S
            b.face([top, rings[1][s], rings[1][t]], "M_Grass_Park")
        for k in range(1, K):
            for s in range(S):
                t = (s + 1) % S
                b.face([rings[k][s], rings[k + 1][s], rings[k + 1][t], rings[k][t]], "M_Grass_Park")
        scene.obj(f"{C.PREFIX['terrain']}{hd['id']}", b.build(f"TRN_{hd['id']}"), "01_Terrain")


def build_district_grounds(layout):
    for d in layout.DISTRICTS:
        g = d.get("ground")
        if not g:
            continue
        b = MeshBuilder()
        b.tri_fill([G.ensure_ccw([G.V(p) for p in d["poly"]])], C.GROUND_Z + 0.012, GROUND_MAT[g])
        scene.obj(f"{C.PREFIX['terrain']}Ground_{d['id']}", b.build(f"TRN_Ground_{d['id']}"), "01_Terrain")


def build_zoning(layout):
    for d in layout.DISTRICTS:
        b = MeshBuilder()
        b.tri_fill([G.ensure_ccw([G.V(p) for p in d["poly"]])], C.GROUND_Z + 0.03, KIND_MAT.get(d["kind"], "M_Zone_Residential"))
        o = scene.obj(f"{C.PREFIX['zone']}{d['id']}", b.build(f"ZN_{d['id']}"), "03_Zoning_Blockout")
        o["district_kind"] = d["kind"]
        o["district_name"] = d.get("name", d["id"])


def build_labels(layout, net=None):
    from . import palette
    def label(text, x, y, size, z=3.0):
        for hd in getattr(layout, "HILLS", []):          # keep labels above hills
            z = max(z, C.GROUND_Z + hill_height(hd, x, y) + 2.0)
        cu = bpy.data.curves.new(f"LBL_{text}", "FONT")
        cu.body = text
        cu.size = size
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.materials.append(palette.get("M_Label"))
        o = scene.obj(f"{C.PREFIX['label']}{text.replace(' ', '_')}", cu, "99_Annotations", (x, y, z))
        return o
    for d in layout.DISTRICTS:
        c = G.centroid([G.V(p) for p in d["poly"]])
        if "label_at" in d:
            c = G.V(d["label_at"])
        label(d.get("name", d["id"]).upper(), c.x, c.y, d.get("label_size", 9.0))
    for lm_id, lm in getattr(layout, "LANDMARKS", {}).items():
        if "center" in lm:
            label(lm.get("name", lm_id), lm["center"][0], lm["center"][1] - 6, 6.0, z=3.5)
    if net is not None:
        seen = set()
        for e in net.edges:
            nm = e.road.get("name")
            if not nm or nm in seen or e.cls not in ("main", "secondary"):
                continue
            seen.add(nm)
            p = e.poly.pos(e.poly.length * 0.5)
            t = e.poly.tangent(e.poly.length * 0.5)
            o = label(nm, p.x, p.y, 4.0, z=3.2)
            ang = math.atan2(t.y, t.x)
            if ang > math.pi / 2:
                ang -= math.pi
            if ang < -math.pi / 2:
                ang += math.pi
            o.rotation_euler[2] = ang
