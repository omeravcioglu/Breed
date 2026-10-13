"""MAPLE GREEN - the village green in front of the Pet Shop (LANDMARKS["MapleGreen"]).

PLAN (world coords; the site has no facing, so the site frame is axis aligned)
-----------------------------------------------------------------------------
Starter / tutorial capture zone (rabbits, guinea pigs, peacocks) in full view of the shop door. The shop
(-50, -47) looks north up the GREEN WALK (layout path, x ~ -50) across the green, the canal and on to the
Town Square clock tower; that axis is kept clear (only a low flower roundel on it; the entrance lamp pair
stands ~5 m either side of the walk so it frames the spawn view instead of blocking it).

  LAWN        mowed stripes (aligned with the Green Walk axis) + a low stone edging around the green.
  CROSS WALK  east-west path: Swan Lane side (west) -> bandstand ring -> Green Walk roundel -> the
              bridgehead corner (east). A south spur from the ring reaches Maple Street near Collar St.
  ROUNDEL     paved circle where the cross walk meets the Green Walk: round flower bed, benches facing
              the lawn (the flagpole moved to the bandstand: it competed with the clock tower in the spawn vista).
  BANDSTAND   hero element (custom): octagonal white bandstand with a striped bell roof on a raised deck,
              steps toward the Green Walk, railings, picket skirt with ONE OPEN BAY on the north side =
              crawl-space hiding spot under the deck. Ringed by a path, benches and lamps; the 8.5 m flagpole
              stands on the ring's south-west rim beside the south entrance.
  EDGES       low hedge runs along Maple Street in short segments (lots of gaps = entrances + rabbit
              cover), a matching pair of flower beds at every path mouth (Green Walk, west, south, east), a
              two-sided "MAPLE / GREEN" welcome board (mesh lettering on both faces).
  CONNECTORS  (deliberate small extensions beyond the polygon, connectors only) the west, south and east
              paths and the layout Green Walk (from its 7 m-short start at (-50, -18)) run on to the kerb and
              end 0.35 m under the 0.15 sidewalk edge; the Green Walk link lands at x = -50 opposite the shop
              apron (a Maple St crosswalk there is requested from the lead).
  TREES       big shade trees in the west end (picnic tables under them) and a few along the north edge
              and the east wedge; the middle lawn (between the bandstand and the Green Walk) and the east
              wedge stay OPEN for chases. Bush clumps in the east wedge = more hiding cover.
NOTE (framework workaround): citygen.scene.coll() resolves every path part with a GLOBAL
bpy.data.collections.get(name), so generic sub-collection names ("Ground", "Paths", "Trees", ...) collide
between sites and even with kit category collections (KIT_Library/nature/Trees). Every sub= used by my
three modules is therefore prefixed (PS_ / MG_ / OL_) and passed explicitly (also to S.paving / path_ribbon).
"""
import math

from mathutils import Matrix, Vector

from .. import geom2d as G
from ..meshutil import MeshBuilder
from .petshop import (TAU, bev_box, emit, ellipse, face_rot, front_matrix, kerb_hit, seg_box, sign_board,
                      star_shape, stripes, text_mb, tri_count, xf)

BANDSTAND = Vector((-82.0, 1.0))
RING_R = 7.6
ROUNDEL = Vector((-50.2, 1.0))
PATH_W = 2.4
FLOWERS = ["M_Foliage_Blossom", "M_Awning_Yellow", "M_Trim_White", "M_Wall_Lavender", "M_Foliage_Blossom",
           "M_Awning_Red"]


# =============================================================================== helpers
def ring_wall(mb, cx, cy, r, z0, z1, mat, seg=16, inward=False):
    for i in range(seg):
        a0, a1 = TAU * i / seg, TAU * (i + 1) / seg
        p0 = Vector((cx + r * math.cos(a0), cy + r * math.sin(a0)))
        p1 = Vector((cx + r * math.cos(a1), cy + r * math.sin(a1)))
        if inward:
            mb.face([(p1.x, p1.y, z0), (p0.x, p0.y, z0), (p0.x, p0.y, z1), (p1.x, p1.y, z1)], mat)
        else:
            mb.face([(p0.x, p0.y, z0), (p1.x, p1.y, z0), (p1.x, p1.y, z1), (p0.x, p0.y, z1)], mat)


def annulus(mb, cx, cy, r0, r1, z, mat, seg=16):
    for i in range(seg):
        a0, a1 = TAU * i / seg, TAU * (i + 1) / seg
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        mb.face([(cx + r0 * c0, cy + r0 * s0, z), (cx + r1 * c0, cy + r1 * s0, z), (cx + r1 * c1, cy + r1 * s1, z),
                 (cx + r0 * c1, cy + r0 * s1, z)], mat)


def round_bed(mb, cx, cy, r, z0, rng, n_flowers=12, bush=True, seg=16):
    """Stone-rimmed round flower bed with flower clumps (and a centre bush)."""
    zr = z0 + 0.32
    zs = z0 + 0.22
    ring_wall(mb, cx, cy, r, z0 - 0.05, zr, "M_CanalStone", seg)
    annulus(mb, cx, cy, r - 0.22, r, zr, "M_CanalStone", seg)
    ring_wall(mb, cx, cy, r - 0.22, zs, zr, "M_CanalStone", seg, inward=True)
    mb.fan((cx, cy), [(cx + (r - 0.22) * math.cos(TAU * i / seg), cy + (r - 0.22) * math.sin(TAU * i / seg))
                      for i in range(seg)], zs, "M_Dirt")
    for k in range(n_flowers):
        a = TAU * k / n_flowers + rng.uniform(-0.2, 0.2)
        rr = (r - 0.55) * (0.55 + 0.45 * ((k % 2) * 0.6 + 0.4)) if r > 1.0 else r * 0.4
        fr = rng.uniform(0.2, 0.3)
        mb.sphere(cx + rr * math.cos(a), cy + rr * math.sin(a), zs + fr * 0.45, fr, FLOWERS[k % len(FLOWERS)],
                  seg=7, rings=4, sz=0.75)
    if bush:
        mb.sphere(cx, cy, zs + 0.35, min(0.6, r * 0.38), "M_Foliage", seg=9, rings=5, sz=0.85)


def _ribbon_poly(pts, w):
    """Rectangle around the segment pts[0]->pts[1] (w wide), for register_lot."""
    a, b = Vector(pts[0]), Vector(pts[1])
    t = (b - a).normalized()
    n = Vector((-t.y, t.x)) * (w / 2)
    return [a - n, b - n, b + n, a + n]


def offset_line(pts, d):
    """Offset an open polyline to the LEFT by d (mitred)."""
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P)):
        t0 = (P[i] - P[i - 1]).normalized() if i > 0 else (P[1] - P[0]).normalized()
        t1 = (P[i + 1] - P[i]).normalized() if i < len(P) - 1 else t0
        n0, n1 = Vector((-t0.y, t0.x)), Vector((-t1.y, t1.x))
        m = (n0 + n1)
        m = m.normalized() if m.length > 1e-6 else n0
        k = d / max(m.dot(n0), 0.35)
        out.append(P[i] + m * k)
    return out


# =============================================================================== bandstand (hero)
def bandstand(R=4.3, deck=0.95, post_h=2.6, rng=None):
    """Octagonal bandstand, origin = ground centre, steps toward +X (east), open skirt bay toward +Y."""
    mb = MeshBuilder()
    n = 8
    off = math.pi / 8
    V = [Vector((R * math.cos(off + TAU * i / n), R * math.sin(off + TAU * i / n))) for i in range(n)]
    # deck slab (with underside for the crawl space)
    mb.prism(V, deck - 0.2, deck, "M_Wood_Light", "M_Trim_White", bottom="M_Trim_Wood")
    # brick piers at the corners + picket skirt between them (side 7 = east steps, side 2 = north open bay)
    sides_skirt = [i for i in range(n) if i not in (7, 1)]
    for i in range(n):
        p = V[i] * ((R - 0.22) / R)
        mb.extend(bev_box(p.x - 0.24, p.y - 0.24, -0.05, p.x + 0.24, p.y + 0.24, deck - 0.2, "M_CanalStone", bev=0.03))
    for i in sides_skirt:
        a, b = V[i] * ((R - 0.3) / R), V[(i + 1) % n] * ((R - 0.3) / R)
        d = (b - a)
        L = d.length
        t = d / L
        nrm = Vector((t.y, -t.x))   # outward (CCW polygon)
        k = int(L / 0.2)
        for j in range(1, k):
            if j % 2:
                continue
            c = a + t * (L * j / k)
            q0, q1 = c - t * 0.06, c + t * 0.06
            sub = MeshBuilder()
            pts = [q0 - nrm * 0.03, q1 - nrm * 0.03, q1 + nrm * 0.03, q0 + nrm * 0.03]
            sub.prism(pts, 0.0, deck - 0.24, "M_Trim_White", "M_Trim_White")
            mb.extend(sub)
        for z in (0.08, deck - 0.34):
            seg_box(mb, (a.x, a.y, z), (b.x, b.y, z), 0.07, 0.08, "M_Trim_White")
    # posts
    for i in range(n):
        p = V[i] * ((R - 0.3) / R)
        mb.extend(bev_box(p.x - 0.11, p.y - 0.11, deck, p.x + 0.11, p.y + 0.11, deck + post_h, "M_Trim_White", bev=0.03))
    # railings (all sides but the steps) and the frieze band under the roof
    for i in range(n):
        a, b = V[i] * ((R - 0.3) / R), V[(i + 1) % n] * ((R - 0.3) / R)
        t = (b - a).normalized()
        a2, b2 = a + t * 0.11, b - t * 0.11
        zf = deck + post_h - 0.32
        seg_box(mb, (a2.x, a2.y, zf + 0.12), (b2.x, b2.y, zf + 0.12), 0.1, 0.22, "M_Trim_White")
        # little arch brackets under the frieze
        for (p, s) in ((a2, 1), (b2, -1)):
            q = p + t * s * 0.45
            seg_box(mb, (p.x, p.y, zf - 0.35), (q.x, q.y, zf), 0.06, 0.06, "M_Trim_White")
        if i == 7:
            continue
        seg_box(mb, (a2.x, a2.y, deck + 0.9), (b2.x, b2.y, deck + 0.9), 0.12, 0.08, "M_Trim_White")
        seg_box(mb, (a2.x, a2.y, deck + 0.12), (b2.x, b2.y, deck + 0.12), 0.08, 0.06, "M_Trim_White")
        L = (b2 - a2).length
        k = int(L / 0.32)
        for j in range(1, k):
            c = a2 + t * (L * j / k)
            mb.box(c.x - 0.03, c.y - 0.03, deck + 0.15, c.x + 0.03, c.y + 0.03, deck + 0.86, "M_Trim_White",
                   skip=("-z", "+z"))
    # steps (east, side 7 spans angles -22.5..22.5 deg)
    xe = R * math.cos(off)
    ns = 4
    rise = deck / ns
    for s in range(ns):
        x0 = xe - 0.05 + (ns - 1 - s) * 0.36
        mb.box(x0, -1.2, -0.05, x0 + 0.38, 1.2, rise * (s + 1), "M_Wood_Light", skip=("-z",))
    # roof: striped bell (lower flare + upper cone), soffit, fascia, finial
    zt = deck + post_h
    Re = R + 0.55
    E = [Vector((Re * math.cos(off + TAU * i / n), Re * math.sin(off + TAU * i / n), zt + 0.18)) for i in range(n)]
    M_ = [Vector((0.56 * Re * math.cos(off + TAU * i / n), 0.56 * Re * math.sin(off + TAU * i / n), zt + 0.78))
          for i in range(n)]
    apex = Vector((0, 0, zt + 2.95))
    for i in range(n):
        j = (i + 1) % n
        col = "M_Roof_Terracotta"
        mb.face([E[i], E[j], M_[j], M_[i]], col)
        mb.face([M_[i], M_[j], apex], col)
        # cream hip ribs
        seg_box(mb, E[i] + Vector((0, 0, 0.05)), M_[i] + Vector((0, 0, 0.05)), 0.12, 0.1, "M_Trim_White")
        seg_box(mb, M_[i] + Vector((0, 0, 0.05)), apex + Vector((0, 0, 0.05)), 0.12, 0.1, "M_Trim_White")
    # fascia band + soffit
    for i in range(n):
        j = (i + 1) % n
        a0, a1 = E[i] - Vector((0, 0, 0.22)), E[j] - Vector((0, 0, 0.22))
        mb.face([a0, a1, E[j], E[i]], "M_Trim_White")
    mb.face([E[i] - Vector((0, 0, 0.22)) for i in reversed(range(n))], "M_Trim_White")
    # scalloped valance under the eave
    for i in range(n):
        j = (i + 1) % n
        a0, a1 = E[i] - Vector((0, 0, 0.22)), E[j] - Vector((0, 0, 0.22))
        for k in range(3):
            p0, p1 = a0.lerp(a1, k / 3), a0.lerp(a1, (k + 1) / 3)
            tip = p0.lerp(p1, 0.5) - Vector((0, 0, 0.22))
            mb.face([p0, tip, p1], "M_Roof_Terracotta")
            # back side (seen from inside the bandstand)
            c = Vector((0, 0, p0.z))
            inn = (p0.lerp(p1, 0.5) - c)
            inn.z = 0
            o = -inn.normalized() * 0.01
            mb.face([p1 + o, tip + o, p0 + o], "M_Roof_Terracotta")
    mb.cylinder(0, 0, apex.z - 0.1, apex.z + 0.55, 0.07, "M_Trim_White", seg=8)
    mb.sphere(0, 0, apex.z + 0.68, 0.17, "M_Awning_Yellow", seg=10, rings=6)
    # hanging lantern
    mb.cylinder(0, 0, zt - 0.6, zt + 0.18, 0.03 + 0.02, "M_Metal_Dark", seg=6)
    mb.cylinder(0, 0, zt - 0.95, zt - 0.6, 0.2, "M_Light_Emit", seg=8, cap_top=True, cap_bottom=True)
    return mb


def flagpole(h=8.5):
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0.0, 0.3, 0.28, "M_CanalStone", seg=10, cap_top=True, r_top=0.22)
    mb.cylinder(0, 0, 0.3, h, 0.075, "M_Trim_White", seg=8, r_top=0.055)
    mb.sphere(0, 0, h + 0.12, 0.13, "M_Awning_Yellow", seg=8, rings=5)
    # flag: 4 wavy strips, double sided, blue field + white star (both sides)
    fw, fh, nseg = 1.9, 1.15, 4
    z1 = h - 0.15
    z0 = z1 - fh
    cols = []
    for i in range(nseg + 1):
        x = 0.08 + fw * i / nseg
        y = 0.0 if i <= 1 else 0.13 * math.sin(i * 1.7)
        cols.append((x, y))
    for i in range(nseg):
        (xa, ya), (xb, yb) = cols[i], cols[i + 1]
        o = 0.012
        mb.face([(xa, ya - o, z0), (xb, yb - o, z0), (xb, yb - o, z1), (xa, ya - o, z1)], "M_Awning_Blue")
        mb.face([(xb, yb + o, z0), (xa, ya + o, z0), (xa, ya + o, z1), (xb, yb + o, z1)], "M_Awning_Blue")
    st = star_shape(0.2, 0.085)
    for sgn in (-1, 1):
        sub = MeshBuilder()
        sub.prism(st, 0.0, 0.015, "M_Trim_White", "M_Trim_White")
        # plane facing -Y (front) at y = -0.012 on strip 0..1 (nearly flat), or +Y for the back
        cx = 0.08 + fw * 0.13
        cy = 0.0
        if sgn < 0:
            M = front_matrix(cx, cy - 0.013, (z0 + z1) / 2)
        else:
            M = Matrix.Translation((cx, cy + 0.013, (z0 + z1) / 2)) @ Matrix.Rotation(math.pi, 4, "Z") @ \
                front_matrix()
        mb.extend(sub, M)
    for z in (z1, z0 + 0.1):     # halyard clips
        mb.box(0.05, -0.03, z - 0.05, 0.1, 0.03, z, "M_Metal", skip=())
    return mb


# =============================================================================== build
def build(S):
    import bpy
    before = set(o.name for o in bpy.data.objects)
    rng = S.rng
    P = [Vector(p) for p in S.poly]
    Pc = G.ensure_ccw(P)
    cen = G.centroid(Pc)
    out = {}

    # ---- lawn: mowing stripes along the Green Walk axis + stone edging
    inner = G.offset_polygon_radial(Pc, cen, 0.9)
    mb = MeshBuilder()
    axis = math.atan2(0.991, -0.132)
    stripes(inner, axis, 3.0, 3.0, -0.035, "M_Grass_Park", mb)
    S.mesh("Lawn_Stripes", mb, sub="MG_Ground")

    # ---- paths (inside the polygon) + CONNECTORS from each path end to the kerb (deliberate small extensions
    # beyond the polygon, connectors only: they stop 0.35 m under the 0.15 sidewalk edge)
    west = [Vector((-115.0, -0.6)), Vector((-104.0, 0.2)), BANDSTAND + Vector((-RING_R, 0.0))]
    east_link = [BANDSTAND + Vector((RING_R, 0.0)), Vector((-63.0, 1.3)), ROUNDEL + Vector((-3.6, 0.0))]
    east = [ROUNDEL + Vector((3.4, -0.6)), Vector((-36.0, -2.2)), Vector((-24.0, -3.4)), Vector((-15.2, -4.0))]
    south = [BANDSTAND + Vector((0.6, -RING_R)), Vector((-82.0, -15.0)), Vector((-82.6, -24.2))]
    mouths = {}          # entrance -> (point where the path leaves the lawn, outward direction)
    conn = {}
    for nm, pl, rev in (("West", west, True), ("East", east, False), ("South", south, False)):
        end, prev = (pl[0], pl[1]) if rev else (pl[-1], pl[-2])
        d = (end - prev).normalized()
        hit = kerb_hit(S, end, d)
        mouths[nm] = (end, d)
        if hit is not None and (hit - end).length < 14.0:
            tip = hit + d * 0.35
            mid = end.lerp(tip, 0.5)
            if rev:
                pl[:0] = [tip, mid]
            else:
                pl += [mid, tip]
            conn[nm] = round((hit - end).length, 2)
            S.register_lot(_ribbon_poly([end, tip], PATH_W))
    S.path_ribbon("Path_West", west, width=PATH_W, mat="M_Path", sub="MG_Paths")
    S.path_ribbon("Path_EastLink", east_link, width=PATH_W, mat="M_Path", sub="MG_Paths")
    S.path_ribbon("Path_East", east, width=PATH_W, mat="M_Path", sub="MG_Paths")
    S.path_ribbon("Path_South", south, width=PATH_W, mat="M_Path", sub="MG_Paths")
    # the layout's Green Walk (3 m, drawn by the paths pass) starts 7 m short of Maple St: carry it straight
    # on to the kerb at x = -50, on the spawn / shop-door crossing (Maple St crosswalk requested from the lead)
    gw0 = Vector((-50.0, -17.97))
    hit = kerb_hit(S, gw0, (0.0, -1.0))
    if hit is not None:
        tip = hit + Vector((0.0, -0.35))
        S.path_ribbon("Path_GreenWalkLink", [gw0, gw0.lerp(tip, 0.5), tip], width=3.0, mat="M_Path", lift=0.03,
                      sub="MG_Paths")
        conn["GreenWalk"] = round((hit - gw0).length, 2)
        S.register_lot(_ribbon_poly([gw0, tip], 3.0))
    out["connectors"] = conn
    ring = [BANDSTAND + Vector((RING_R * math.cos(a), RING_R * math.sin(a))) for a in
            [TAU * k / 28 for k in range(28)]]
    S.path_ribbon("Path_BandstandRing", ring + ring[:3], width=PATH_W, mat="M_Path", sub="MG_Paths", step=1.0)
    # roundel plaza on the Green Walk
    rp = MeshBuilder()
    circ = ellipse(ROUNDEL.x, ROUNDEL.y, 4.6, 4.6, 28)
    rp.prism(circ, -0.06, -0.008, "M_Path", "M_Path")
    annulus(rp, ROUNDEL.x, ROUNDEL.y, 4.45, 4.75, 0.0, "M_CanalStone", 28)
    ring_wall(rp, ROUNDEL.x, ROUNDEL.y, 4.75, -0.06, 0.0, "M_CanalStone", 28)
    S.mesh("Roundel_Paving", rp, sub="MG_Paths")
    rb = MeshBuilder()
    round_bed(rb, ROUNDEL.x, ROUNDEL.y, 1.9, -0.008, rng, n_flowers=14, bush=True, seg=20)
    S.mesh("Roundel_FlowerBed", rb, sub="MG_Beds")
    # flagpole on the bandstand ring's south-west rim, beside the south entrance: out of the spawn -> Green
    # Walk -> clock tower vista (it used to stand on the roundel and competed with the tower), flag flying west
    a = math.radians(250)
    fp = BANDSTAND + Vector((math.cos(a), math.sin(a))) * (RING_R + PATH_W / 2 + 0.75)
    emit(S, "Bandstand_Flagpole", flagpole(), fp.x, fp.y, S.ground_z(*fp), rot=math.radians(172), local=False,
         sub="MG_Bandstand")

    # ---- stone edging around the lawn, broken where paths leave the green
    exits = [Vector((-50.0, -20.6)), Vector((-52.2, 16.6))]
    for e, d in mouths.values():
        exits += [e, e + d * 1.5]
    edge = MeshBuilder()
    ring_pts = G.offset_polygon_radial(Pc, cen, 0.45)
    for i in range(len(ring_pts)):
        a, b = ring_pts[i], ring_pts[(i + 1) % len(ring_pts)]
        L = (b - a).length
        k = max(1, int(L / 1.5))
        for j in range(k):
            p0, p1 = a.lerp(b, j / k), a.lerp(b, (j + 1) / k)
            m = (p0 + p1) / 2
            if any((m - e).length < 2.6 for e in exits):
                continue
            seg_box(edge, (p0.x, p0.y, -0.02), (p1.x, p1.y, -0.02), 0.28, 0.12, "M_Curb")
    S.mesh("Lawn_Edging", edge, sub="MG_Ground")

    # ---- the bandstand (hero) + benches / lamps around the ring
    emit(S, "Bandstand", bandstand(), BANDSTAND.x, BANDSTAND.y, S.ground_z(*BANDSTAND), rot=0.0, local=False,
         sub="MG_Bandstand")
    for ang in (50, 130, 230, 310):
        a = math.radians(ang)
        p = BANDSTAND + Vector((math.cos(a), math.sin(a))) * (RING_R + PATH_W / 2 + 0.55)
        d = BANDSTAND - p
        S.put("Bench", p.x, p.y, rot=face_rot(d.x, d.y), sub="MG_Furniture")
    for ang in (10, 170, 270 + 25):
        a = math.radians(ang)
        p = BANDSTAND + Vector((math.cos(a), math.sin(a))) * (RING_R + PATH_W / 2 + 0.5)
        S.put("Lamp_Park", p.x, p.y, sub="MG_Lamps")
    bb = MeshBuilder()
    for dy in (-2.3, 2.3):       # little beds flanking the steps
        round_bed(bb, BANDSTAND.x + 4.9, BANDSTAND.y + dy, 0.72, -0.05, rng, n_flowers=6, seg=12)
    S.mesh("Bandstand_FlowerBeds", bb, sub="MG_Beds")

    # ---- Green Walk furniture: benches facing the lawn, lamps, entrance beds + welcome board
    for (x, y, dx, dy) in ((-53.6, -9.5, -1, 0), (-46.6, -10.5, 1, 0), (-54.2, 8.5, -1, 0), (-46.2, 9.0, 1, 0)):
        S.put("Bench", x, y, rot=face_rot(dx, dy), sub="MG_Furniture")
        S.put("TrashBin", x, y + 1.5, sub="MG_Furniture")
    # lamps: the Green Walk entrance pair stands ~5 m either side of the walk axis (x = -50) so they frame the
    # spawn view up the walk (>= 8 deg off the clock tower) and stay off the green -> shop-door sightline
    for (x, y) in ((-55.2, -13.2), (-45.0, -13.4), (-47.6, -4.6), (-52.6, 6.0), (-47.6, 13.0), (-63.5, 3.0),
                   (-104.0, 2.4), (-33.0, -0.4), (-80.2, -18.5)):
        S.put("Lamp_Park", x, y, sub="MG_Lamps")
    S.put("Flowerbed_2m", -53.6, -18.6, rot=math.radians(97), sub="MG_Beds")
    S.put("Flowerbed_2m", -46.6, -18.1, rot=math.radians(97), sub="MG_Beds",
          recolor={"foliage": "M_Foliage_Light"})
    # the other three path mouths get the same matching pair of flower beds, flanking the path where it
    # leaves the lawn, so every entrance reads from the street
    for nm, (e, d) in sorted(mouths.items()):
        nrm = Vector((-d.y, d.x))
        rot = math.atan2(d.y, d.x)
        for j, s in enumerate((-1, 1)):
            p = e - d * 0.9 + nrm * s * (PATH_W / 2 + 1.0)
            if S.inside(p) and S.clear_of_roads(p, extra=0.6):
                S.put("Flowerbed_2m", p.x, p.y, rot=rot, sub="MG_Beds",
                      recolor={"foliage": "M_Foliage_Light"} if j else None)
    # welcome board: two-sided (the green sees the same face), block lettering MAPLE / GREEN on both faces
    lt = [(text_mb("MAPLE", 0.27, 0.03, "M_Sign_Face", max_w=1.9), 0.0, 0.66),
          (text_mb("GREEN", 0.27, 0.03, "M_Sign_Face", max_w=1.9), 0.0, 0.29)]
    board = sign_board(2.4, 0.95, "M_Roof_Green", frame="M_Trim_White", post_h=0.7, post_mat="M_Trim_White",
                       two_sided=True, extra=lt,
                       pictos=[([ellipse(0, 0, 0.09, 0.09, 10)], -1.0, 0.475),
                               ([ellipse(0, 0, 0.09, 0.09, 10)], 1.0, 0.475)])
    emit(S, "WelcomeBoard", board, -55.6, -17.0, S.ground_z(-55.6, -17.0), rot=face_rot(0.25, -1.0), local=False,
         sub="MG_Furniture")

    # ---- low hedges along Maple Street (short runs with gaps) + entrance gaps for the paths
    south_edge = [Vector((-111.0, -28.3)), Vector((-80.0, -23.3)), Vector((-35.0, -17.3)), Vector((-17.0, -9.6))]
    hedge_line = offset_line(south_edge, 0.7)
    gaps = [Vector((-82.6, -24.0)), Vector((-50.0, -20.0))]
    for i in range(len(hedge_line) - 1):
        a, b = hedge_line[i], hedge_line[i + 1]
        L = (b - a).length
        t = (b - a) / L
        rot = math.atan2(t.y, t.x)
        s = 1.8
        run = 0
        while s < L - 1.6:
            m = a + t * s
            if any((m - g).length < 5.2 for g in gaps):
                s += 1.0
                continue
            if S.clear_of_roads(m, extra=0.6):
                S.put("Hedge_3m", m.x, m.y, rot=rot, sub="MG_Hedges")
            run += 1
            if run % 3 == 0:
                s += 3.0 + 2.6   # gap after three pieces
            else:
                s += 3.0
    # hedge corner around the west entrance
    for (x, y, r) in ((-112.6, 6.5, 1.66), (-112.0, 10.5, 1.75), (-113.0, -7.6, 1.5)):
        S.put("Hedge_3m", x, y, rot=r, sub="MG_Hedges")

    # ---- trees: west grove (+ picnic tables), north edge, east wedge
    trees = [("Tree_Round_B", -104.0, 14.5, "M_Foliage"), ("Tree_Round_A", -107.5, 7.0, "M_Foliage_Light"),
             ("Tree_Cone", -99.0, 21.5, "M_Foliage_Dark"), ("Tree_Round_B", -103.0, -16.5, "M_Foliage"),
             ("Tree_Round_A", -95.0, -21.0, "M_Foliage_Autumn"), ("Tree_Round_A", -92.5, 14.0, "M_Foliage"),
             ("Tree_Round_B", -66.0, 15.5, "M_Foliage"), ("Tree_Round_A", -71.0, -12.5, "M_Foliage_Light"),
             ("Tree_Round_B", -27.0, 5.0, "M_Foliage_Autumn"), ("Tree_Round_A", -36.0, 10.0, "M_Foliage"),
             ("Tree_Small", -20.0, -1.0, "M_Foliage_Blossom"), ("Tree_Small", -60.0, -17.5, "M_Foliage_Blossom")]
    for piece, x, y, col in trees:
        if S.inside((x, y)) and S.clear_of_roads((x, y), extra=1.0):
            S.put(piece, x, y, rot=rng.uniform(0, TAU), recolor={"foliage": col}, sub="MG_Trees")
    for (x, y, r) in ((-99.5, 8.0, 0.3), (-97.5, -11.5, -0.4)):
        S.put("PicnicTable", x, y, rot=r, sub="MG_Furniture")
    for (pc, x, y) in (("Bush_B", -24.5, 7.0), ("Bush_A", -22.6, 6.2), ("Bush_A", -26.3, 8.3),
                       ("Bush_B", -31.5, -11.8), ("Bush_A", -29.8, -12.6), ("Bush_B", -108.5, 18.5),
                       ("Bush_A", -75.5, 14.8), ("Bush_B", -88.0, -16.0)):
        S.put(pc, x, y, rot=rng.uniform(0, TAU), sub="MG_Bushes")
    S.put("Birdbath", -70.0, -6.0, sub="MG_Furniture")
    S.register_lot(S.poly)

    new = [o for o in bpy.data.objects if o.name not in before]
    custom = [o for o in new if o.type == "MESH" and o.data.users == 1]
    out["custom_tris"] = tri_count(custom)
    out["instances"] = S.n
    return out
