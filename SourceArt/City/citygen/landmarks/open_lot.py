"""FAIRGROUND LOT (LANDMARKS["OpenLot"]) - open lot for tutorial / multiplayer round-ups.

PLAN (world coords, axis-aligned site frame; Main Street runs along the west edge, Riverside Drive the north)
---------------------------------------------------------------------------------------------------------
Mostly OPEN: a gravel lot with a big dirt ARENA oval in the middle (~30 x 26 m) where ostriches / emus are
chased and herded. A temporary fair is packed around the edges so the centre stays clear:

  WEST (Main St, toward the pet shop)  candy-striped ENTRANCE ARCH with a banner + ticket kiosk + barriers;
                                       a gravel ARCH LINK (deliberate small extension, connector only) runs
                                       from the entry pad through the arch to the Main St kerb.
  NORTH edge (Riverside Dr)            three striped market STALLS (red / blue / yellow) facing the arena,
                                       each with a pennant finial; stall 1's finial anchors the arch bunting.
  NE corner                            a bigger striped show TENT (open sides - animals can run through).
  EAST                                 a round-up CORRAL of portable livestock panels, mouth toward the
                                       arena = the goal for group chases; hay bale stacks + crates.
  SE corner                            small STAGE with a starry backdrop facing the arena; the gap behind
                                       it is the "FairgroundCorner" hiding spot.
  SW corner                            FOOD TRUCK with cafe tables, crates and barrels.
  ARENA rim                            7 short segments on the oval edge, alternating hay-bale rows and
                                       white/red rails, with 7 openings of 4.8-7.5 m (corral mouth, arch,
                                       bleachers, tent, stalls, food court, stage); the two segments by the
                                       corral act as funnel wings. Six bunting poles with pennant strings;
                                       every pennant tip >= 3.3 m over walkable ground.
NOTE (framework workaround): citygen.scene.coll() resolves every path part with a GLOBAL
bpy.data.collections.get(name), so generic sub-collection names ("Ground", "Paths", "Trees", ...) collide
between sites and even with kit category collections (KIT_Library/nature/Trees). Every sub= used by my
three modules is therefore prefixed (PS_ / MG_ / OL_) and passed explicitly (also to S.paving / path_ribbon).
"""
import math

from mathutils import Matrix, Vector

from .. import geom2d as G
from ..meshutil import MeshBuilder
from .petshop import (TAU, bev_box, bunting, connector_poly, ellipse, emit, face_rot, front_matrix, hay_bale, rz,
                      seg_box, star_shape, tent, tri_count, xf)

ARENA = Vector((52.0, -67.5))
ARENA_R = (15.5, 13.0)
GZ = -0.03                       # gravel top
STALL_FINIAL = 0.85              # pennant finial above the stall apexes (3.9 m) = bunting anchor
# arena rim segments (ellipse parameter angles in degrees on the oval + 1.1 m) and their kind; the gaps are
# the openings: corral mouth (-20..8), tent (30..49), stalls (91..110), arch (140..170), food (212..231),
# bleachers (257..283), stage (306..324)
RIM = [(8, 30, "hay"), (49, 91, "rail"), (110, 140, "hay"), (170, 212, "rail"), (231, 257, "hay"),
       (283, 306, "rail"), (324, 340, "hay")]
RIM_OFF = 1.1


# =============================================================================== hero pieces
def entrance_arch(span=6.4, h=5.0):
    """Two candy-striped posts + arched banner. Origin ground centre, front -Y, span along X."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        x = sx * span / 2
        mb.cylinder(x, 0, -0.05, 0.35, 0.36, "M_CanalStone", seg=10, cap_top=True, r_top=0.3)
        nseg = 9
        for k in range(nseg):
            z0 = 0.35 + (h - 0.35) * k / nseg
            z1 = 0.35 + (h - 0.35) * (k + 1) / nseg
            mb.cylinder(x, 0, z0, z1, 0.2, "M_Awning_Red" if k % 2 == 0 else "M_Trim_White", seg=10,
                        cap_top=(k == nseg - 1))
        mb.sphere(x, 0, h + 0.25, 0.3, "M_Awning_Yellow", seg=10, rings=6)
    # arched banner: board following an arc from post to post
    n = 10
    zb0, rise, bh, t = h - 1.35, 0.55, 0.95, 0.14
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        x = -span / 2 + 0.2 + (span - 0.4) * u
        z = zb0 + rise * math.sin(math.pi * u)
        bot.append(Vector((x, 0, z)))
        top.append(Vector((x, 0, z + bh)))
    y0, y1 = -t / 2, t / 2
    for i in range(n):
        b0, b1, t0, t1 = bot[i], bot[i + 1], top[i], top[i + 1]
        V = lambda p, y: Vector((p.x, y, p.z))
        mb.face([V(b0, y0), V(b1, y0), V(t1, y0), V(t0, y0)], "M_Awning_Yellow")       # front
        mb.face([V(b1, y1), V(b0, y1), V(t0, y1), V(t1, y1)], "M_Awning_Yellow")       # back
        mb.face([V(t0, y0), V(t1, y0), V(t1, y1), V(t0, y1)], "M_Awning_Red")          # top
        mb.face([V(b1, y0), V(b0, y0), V(b0, y1), V(b1, y1)], "M_Awning_Red")          # bottom
        # red border bands front + back
        for (yy, sgn) in ((y0, -1), (y1, 1)):
            for (zlo, zhi) in ((0.0, 0.1), (bh - 0.1, bh)):
                a0 = Vector((b0.x, yy + sgn * 0.015, b0.z + zlo))
                a1 = Vector((b1.x, yy + sgn * 0.015, b1.z + zlo))
                c1 = Vector((b1.x, yy + sgn * 0.015, b1.z + zhi))
                c0 = Vector((b0.x, yy + sgn * 0.015, b0.z + zhi))
                mb.face([a0, a1, c1, c0] if sgn < 0 else [a1, a0, c0, c1], "M_Awning_Red")
    # end caps
    for (b, tp, sgn) in ((bot[0], top[0], -1), (bot[-1], top[-1], 1)):
        q = [Vector((b.x, y0, b.z)), Vector((b.x, y1, b.z)), Vector((tp.x, y1, tp.z)), Vector((tp.x, y0, tp.z))]
        mb.face(list(reversed(q)) if sgn < 0 else q, "M_Awning_Red")
    # "lettering" + stars on the front and back faces
    for side in (-1, 1):
        for k in range(5):
            u = 0.22 + 0.14 * k
            x = -span / 2 + 0.2 + (span - 0.4) * u
            z = zb0 + rise * math.sin(math.pi * u) + bh * 0.5
            sub = MeshBuilder()
            sub.box(-0.22, 0.0, -0.17, 0.22, 0.03, 0.17, "M_Awning_Red", skip=("+y",))
            M = Matrix.Translation((x, -t / 2 - 0.03, z))
            if side > 0:
                M = Matrix.Translation((x, t / 2 + 0.03, z)) @ Matrix.Rotation(math.pi, 4, "Z")
            mb.extend(sub, M)
        for u in (0.08, 0.92):
            x = -span / 2 + 0.2 + (span - 0.4) * u
            z = zb0 + rise * math.sin(math.pi * u) + bh * 0.5
            st = MeshBuilder()
            st.prism(star_shape(0.24, 0.1), 0.0, 0.04, "M_Awning_Red", "M_Awning_Red")
            if side < 0:
                mb.extend(st, front_matrix(x, -t / 2, z))
            else:
                mb.extend(st, Matrix.Translation((x, t / 2, z)) @ Matrix.Rotation(math.pi, 4, "Z") @ front_matrix())
    return mb


def stage(w=8.0, d=5.0, h=1.0):
    """Small open stage, origin ground centre, front -Y."""
    mb = MeshBuilder()
    mb.box(-w / 2, -d / 2, -0.05, w / 2, d / 2, h, "M_Wood_Light", skip=("-z",))
    # striped skirt on front + sides
    k = 10
    for i in range(k):
        x0, x1 = -w / 2 + w * i / k, -w / 2 + w * (i + 1) / k
        col = "M_Awning_Red" if i % 2 == 0 else "M_Awning_Cream"
        mb.box(x0, -d / 2 - 0.04, 0.0, x1, -d / 2, h - 0.12, col, skip=("+y", "-z"))
    for sx in (-1, 1):
        for i in range(6):
            y0, y1 = -d / 2 + d * i / 6, -d / 2 + d * (i + 1) / 6
            col = "M_Awning_Red" if i % 2 == 0 else "M_Awning_Cream"
            if sx > 0:
                mb.box(w / 2, y0, 0.0, w / 2 + 0.04, y1, h - 0.12, col, skip=("-x", "-z"))
            else:
                mb.box(-w / 2 - 0.04, y0, 0.0, -w / 2, y1, h - 0.12, col, skip=("+x", "-z"))
    e = 0.06
    for (x0, y0, x1, y1) in ((-w / 2 - e, -d / 2 - e, w / 2 + e, -d / 2 + 0.12), (-w / 2 - e, d / 2 - 0.12, w / 2 + e, d / 2 + e),
                             (-w / 2 - e, -d / 2 + 0.12, -w / 2 + 0.12, d / 2 - 0.12), (w / 2 - 0.12, -d / 2 + 0.12, w / 2 + e, d / 2 - 0.12)):
        mb.box(x0, y0, h - 0.12, x1, y1, h + 0.02, "M_Trim_White", skip=("-z",))
    # side steps (front corners)
    for sx in (-1, 1):
        for s in range(3):
            x0 = sx * (w / 2 + 0.06 + (2 - s) * 0.35)
            mb.box(min(x0, x0 + sx * 0.36), -d / 2 + 0.2, -0.05, max(x0, x0 + sx * 0.36), -d / 2 + 1.6,
                   h * (s + 1) / 3, "M_Wood_Light", skip=("-z",))
    # backdrop frame + panel + star
    for sx in (-1, 0, 1):
        x = sx * (w / 2 - 0.15)
        mb.extend(bev_box(x - 0.12, d / 2 - 0.4, h, x + 0.12, d / 2 - 0.16, h + 3.6, "M_Trim_White", bev=0.02))
    mb.box(-w / 2 + 0.05, d / 2 - 0.36, h + 0.05, w / 2 - 0.05, d / 2 - 0.2, h + 3.0, "M_Awning_Blue", skip=())
    mb.extend(bev_box(-w / 2 - 0.1, d / 2 - 0.45, h + 3.6, w / 2 + 0.1, d / 2 - 0.1, h + 3.9, "M_Trim_White", bev=0.03,
                      skip_bottom=False))
    st = MeshBuilder()
    st.prism(star_shape(1.0, 0.42), 0.0, 0.06, "M_Awning_Yellow", "M_Awning_Yellow")
    mb.extend(st, front_matrix(0.0, d / 2 - 0.36, h + 1.6))
    for x in (-2.6, 2.6):
        sm = MeshBuilder()
        sm.prism(star_shape(0.42, 0.18), 0.0, 0.05, "M_Trim_White", "M_Trim_White")
        mb.extend(sm, front_matrix(x, d / 2 - 0.36, h + 2.1))
    # valance under the header + spotlights
    for i in range(12):
        x0, x1 = -w / 2 + w * i / 12, -w / 2 + w * (i + 1) / 12
        tip = Vector(((x0 + x1) / 2, d / 2 - 0.47, h + 3.25))
        a, b = Vector((x0, d / 2 - 0.47, h + 3.6)), Vector((x1, d / 2 - 0.47, h + 3.6))
        col = "M_Awning_Red" if i % 2 == 0 else "M_Awning_Yellow"
        mb.face([a, tip, b], col)
        mb.face([b + Vector((0, 0.02, 0)), tip + Vector((0, 0.02, 0)), a + Vector((0, 0.02, 0))], col)
    for x in (-2.9, -1.0, 1.0, 2.9):
        mb.box(x - 0.18, d / 2 - 0.85, h + 3.35, x + 0.18, d / 2 - 0.45, h + 3.65, "M_Trim_Dark", skip=())
        mb.box(x - 0.13, d / 2 - 0.87, h + 3.4, x + 0.13, d / 2 - 0.85, h + 3.6, "M_Light_Emit", skip=("+y",))
    # speakers
    for sx in (-1, 1):
        x = sx * (w / 2 - 0.55)
        mb.extend(bev_box(x - 0.32, -d / 2 + 0.3, h, x + 0.32, -d / 2 + 0.8, h + 1.1, "M_Hazard_Dark", bev=0.03))
        sp = MeshBuilder()
        sp.cylinder(0, 0, 0.0, 0.03, 0.2, "M_Metal_Dark", seg=10, cap_top=True)
        mb.extend(sp, front_matrix(x, -d / 2 + 0.3, h + 0.45))
        sp2 = MeshBuilder()
        sp2.cylinder(0, 0, 0.0, 0.03, 0.11, "M_Metal_Dark", seg=8, cap_top=True)
        mb.extend(sp2, front_matrix(x, -d / 2 + 0.3, h + 0.85))
    return mb


def corral_panel(L=3.0, H=1.3):
    """Portable livestock panel along X, origin ground centre."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.05)
        mb.box(x - 0.06, -0.06, 0.0, x + 0.06, 0.06, H + 0.05, "M_Trim_White", skip=("-z",))
        mb.box(x - 0.09, -0.3, 0.0, x + 0.09, 0.3, 0.06, "M_Trim_White", skip=("-z",))
    for z in (0.3, 0.6, 0.9, 1.2):
        mb.box(-L / 2 + 0.1, -0.045, z - 0.045, L / 2 - 0.1, 0.045, z + 0.045, "M_Door_Red", skip=("-x", "+x"))
    return mb


def bleachers(L=7.0, tiers=3):
    """Small wooden bleachers, origin ground centre of the front edge, seats face -Y."""
    mb = MeshBuilder()
    for k in range(tiers):
        y0 = 0.15 + k * 0.72
        z = 0.42 + k * 0.42
        # seat plank (chunky) + painted riser under its front edge + footboard in front
        mb.extend(bev_box(-L / 2, y0, z - 0.12, L / 2, y0 + 0.5, z, "M_Wood_Light", bev=0.03, skip_bottom=False))
        mb.box(-L / 2 + 0.05, y0 + 0.08, z - 0.42, L / 2 - 0.05, y0 + 0.14, z - 0.12, "M_Door_Red", skip=("-z", "+z"))
        mb.box(-L / 2, y0 - 0.3, z - 0.42 + 0.0, L / 2, y0 + 0.08, z - 0.42 + 0.1, "M_Trim_Wood", skip=("-z",))
    for x in (-L / 2 + 0.2, 0.0, L / 2 - 0.2):
        seg_box(mb, (x, 0.0, 0.0), (x, 0.15 + tiers * 0.72, 0.42 * tiers), 0.1, 0.12, "M_Door_Red")
        mb.box(x - 0.05, 0.15 + (tiers - 1) * 0.72 + 0.1, 0.0, x + 0.05, 0.15 + (tiers - 1) * 0.72 + 0.2,
               0.42 * tiers, "M_Door_Red", skip=("-z",))
    return mb


def _rim_pt(deg):
    a = math.radians(deg)
    return ARENA + Vector((math.cos(a) * (ARENA_R[0] + RIM_OFF), math.sin(a) * (ARENA_R[1] + RIM_OFF)))


def _arc(a0, a1, step=0.25):
    """Points along the rim ellipse from a0 to a1 (deg) and their cumulative arc lengths."""
    n = max(2, int(abs(a1 - a0) / step))
    pts = [_rim_pt(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    acc = [0.0]
    for i in range(1, len(pts)):
        acc.append(acc[-1] + (pts[i] - pts[i - 1]).length)
    return pts, acc


def _at(pts, acc, s):
    for i in range(1, len(acc)):
        if acc[i] >= s:
            t = (s - acc[i - 1]) / max(acc[i] - acc[i - 1], 1e-9)
            p = pts[i - 1].lerp(pts[i], t)
            d = (pts[i] - pts[i - 1]).normalized()
            return p, d
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def arena_rim(S, out):
    hb = hay_bale()
    mb = MeshBuilder()
    gaps = []
    for k, (a0, a1, kind) in enumerate(RIM):
        pts, acc = _arc(a0, a1)
        L = acc[-1]
        if kind == "hay":
            n = max(2, int(L / 1.22))
            pitch = L / n
            for i in range(n):
                p, d = _at(pts, acc, pitch * (i + 0.5))
                r = math.atan2(d.y, d.x) + (0.05 if i % 2 else -0.04)
                mb.extend(rz(hb, r, p.x, p.y, S.ground_z(p.x, p.y)))
                if i in (1, n - 2) and n >= 4:          # a stacked bale near each end of the row
                    mb.extend(rz(hb, r + 0.12, p.x, p.y, S.ground_z(p.x, p.y) + 0.48))
        else:
            n = max(1, math.ceil(L / 2.6))
            posts = [_at(pts, acc, L * i / n)[0] for i in range(n + 1)]
            for i, p in enumerate(posts):
                z = S.ground_z(p.x, p.y)
                mb.extend(bev_box(p.x - 0.075, p.y - 0.075, z - 0.05, p.x + 0.075, p.y + 0.075, z + 1.1,
                                  "M_Trim_White", bev=0.02))
                mb.cylinder(p.x, p.y, z + 1.1, z + 1.16, 0.1, "M_Awning_Red", seg=8, cap_top=True)
                if i:
                    q = posts[i - 1]
                    for zz in (0.45, 0.9):
                        seg_box(mb, (q.x, q.y, z + zz), (p.x, p.y, z + zz), 0.07, 0.11, "M_Door_Red")
        gaps.append(round((_rim_pt(RIM[(k + 1) % len(RIM)][0]) - _rim_pt(a1)).length, 1))
    S.mesh("Arena_Rim", mb, sub="OL_Arena")
    out["rim_openings_m"] = gaps


def bunting_pole(h=4.6):
    mb = MeshBuilder()
    mb.cylinder(0, 0, -0.05, 0.2, 0.18, "M_CanalStone", seg=8, cap_top=True)
    mb.cylinder(0, 0, 0.2, h, 0.06, "M_Trim_White", seg=8)
    mb.sphere(0, 0, h + 0.1, 0.12, "M_Awning_Red", seg=8, rings=5)
    return mb


# =============================================================================== build
def build(S):
    import bpy
    before = set(o.name for o in bpy.data.objects)
    rng = S.rng
    P = G.ensure_ccw([Vector(p) for p in S.poly])
    cen = G.centroid(P)
    out = {}

    # ---- ground: gravel lot + dirt arena oval + a worn track to the arch
    inner = G.offset_polygon_radial(P, cen, 1.8)
    S.paving("TrampledGrass", inner, "M_Grass_Dry", z=GZ - 0.006, skirt=0.1, sub="OL_Ground")
    for nm, pts in (("Gravel_North", [(26.0, -40.0), (63.0, -46.4), (63.6, -50.6), (26.4, -44.2)]),
                    ("Gravel_FoodCourt", [(26.0, -75.5), (40.0, -75.5), (40.4, -91.0), (26.4, -91.6)]),
                    ("Gravel_Stage", [(64.0, -77.0), (79.6, -73.0), (80.0, -90.2), (63.0, -90.6)]),
                    ("Gravel_Entry", [(24.6, -49.0), (31.0, -49.0), (31.0, -63.0), (24.6, -63.0)])):
        S.paving(nm, [Vector(p) for p in pts], "M_Gravel", z=GZ, skirt=0.08, sub="OL_Ground")
    ar = MeshBuilder()
    oval = ellipse(ARENA.x, ARENA.y, ARENA_R[0], ARENA_R[1], 40)
    ar.tri_fill([G.ensure_ccw([Vector(p) for p in oval])], GZ + 0.012, "M_Dirt")
    S.mesh("Arena_Dirt", ar, sub="OL_Ground")
    # ---- entrance arch (west edge, toward Main St / the pet shop) + kiosk + barriers
    arch_c = Vector((25.6, -56.0))
    emit(S, "EntranceArch", entrance_arch(), arch_c.x, arch_c.y, S.ground_z(*arch_c), rot=face_rot(-1, 0),
         local=False, sub="OL_Entrance")
    S.put("NewsStand", 28.4, -50.6, rot=face_rot(-1, 0.15), recolor={"awning": "M_Awning_Yellow",
                                                                     "sign": "M_Awning_Red"}, sub="OL_Entrance",
          name="LM_OpenLot_TicketKiosk")
    for (x, y) in ((25.5, -46.0), (25.6, -49.5), (25.8, -62.5), (26.0, -66.0)):
        S.put("Barrier", x, y, rot=math.pi / 2, sub="OL_Entrance")
    for (x, y) in ((24.6, -59.8), (24.6, -52.2)):
        S.put("TrafficCone", x, y, sub="OL_Entrance")
    # gravel connector from the entry pad through the arch to the Main St sidewalk (deliberate small extension
    # beyond the lot, connector only; it ends 0.35 m under the 0.15 kerb)
    cp = connector_poly(S, Vector((24.6, -52.2)), Vector((24.6, -59.8)), Vector((-1.0, 0.0)), n=4)
    if cp:
        S.paving("Gravel_ArchLink", cp, "M_Gravel", z=GZ, skirt=0.08, sub="OL_Ground")
        S.register_lot(cp)
        out["connectors"] = {"ArchLink": round(max(24.6 - p.x for p in cp), 2)}

    # ---- market stalls along the north edge + big show tent NE
    stalls = [((35.0, -43.0), "M_Awning_Red"), ((46.0, -45.0), "M_Awning_Blue"), ((57.0, -46.9), "M_Awning_Yellow")]
    for i, ((x, y), col) in enumerate(stalls):
        # every stall gets a pennant finial; stall 1's finial top (z 4.75) anchors the bunting from the arch
        t = tent(3.8, 3.4, 2.35, 3.9, col, "M_Awning_Cream", stripes=3, counter=(3.0, 1.0, 0.6), finial=STALL_FINIAL,
                 pennant_mat="M_Awning_Yellow" if col != "M_Awning_Yellow" else "M_Awning_Red")
        emit(S, f"Stall_{i + 1}", t, x, y, S.ground_z(x, y), rot=0.0 + 0.04 * (i - 1), local=False, sub="OL_Stalls")
        S.put("CrateStack", x + 1.5, y + 2.4, rot=0.1 * i, sub="OL_Stalls")
    S.put("Crate", 40.7, -46.0, rot=0.4, sub="OL_Stalls")
    S.put("Barrel", 51.6, -48.0, sub="OL_Stalls")
    big = tent(6.4, 6.4, 2.7, 5.6, "M_Awning_Red", "M_Awning_Cream", stripes=4, valance=0.5)
    big.cylinder(0, 0, 5.5, 6.3, 0.05, "M_Trim_White", seg=6)
    big.extend(xf(_pennant(), Matrix.Translation((0, 0, 6.3))))
    emit(S, "ShowTent", big, 72.5, -53.5, S.ground_z(72.5, -53.5), rot=face_rot(-1, -0.8), local=False, sub="OL_Stalls")
    for (x, y, r) in ((68.0, -50.0, 0.3), (76.8, -57.4, 1.2)):
        S.put("Bench", x, y, rot=r + math.pi, sub="OL_Stalls")

    # ---- stage SE (back to the FairgroundCorner hiding spot)
    st_c = Vector((72.6, -84.0))
    emit(S, "Stage", stage(), st_c.x, st_c.y, S.ground_z(*st_c), rot=face_rot(ARENA.x - st_c.x, ARENA.y - st_c.y),
         local=False, sub="OL_Stage")
    for (pc, x, y, r) in (("CrateStack", 78.8, -88.5, 0.7), ("Crate", 77.2, -90.0, 0.2), ("Barrel", 66.0, -89.6, 0.0),
                          ("Barrel", 66.7, -90.3, 0.0), ("Pallet", 79.6, -82.0, 0.9)):
        S.put(pc, x, y, rot=r, sub="OL_Stage")

    # ---- food truck SW + cafe tables
    S.put("Truck_Box", 30.4, -84.2, rot=math.pi + 0.06, recolor={"awning": "M_Awning_Yellow", "sign": "M_Awning_Red"},
          sub="OL_FoodCourt", name="LM_OpenLot_FoodTruck")
    for (x, y) in ((35.5, -78.5), (37.4, -83.6), (35.2, -88.0)):
        S.put("CafeTable", x, y, rot=rng.uniform(0, TAU), sub="OL_FoodCourt")
    for (pc, x, y, r) in (("CrateStack", 27.2, -90.4, 0.1), ("Barrel", 28.8, -78.4, 0.0), ("TrashBin", 33.4, -76.6, 0.0),
                          ("Crate", 26.4, -88.6, 0.5)):
        S.put(pc, x, y, rot=r, sub="OL_FoodCourt")

    # ---- round-up corral (east), mouth toward the arena
    cc = Vector((72.8, -70.0))
    cr = 4.4
    mouth = math.atan2(ARENA.y - cc.y, ARENA.x - cc.x)
    k_tot = 8
    for k in range(k_tot):
        a = mouth + math.radians(45) + (TAU - math.radians(90)) * (k + 0.5) / k_tot
        p = cc + Vector((math.cos(a), math.sin(a))) * cr
        chord = 2 * cr * math.sin((TAU - math.radians(90)) / k_tot / 2)
        emit(S, f"Corral_Panel_{k + 1:02d}", corral_panel(L=chord + 0.1), p.x, p.y, S.ground_z(*p), rot=a + math.pi / 2,
             local=False, sub="OL_Corral")
    hb = hay_bale()
    bales = MeshBuilder()
    for (x, y, z, r) in ((76.4, -63.6, 0, 0.2), (77.5, -63.8, 0, 0.25), (76.9, -63.7, 0.48, 0.3),
                         (77.6, -76.8, 0, 1.4), (77.7, -75.6, 0, 1.45)):
        bales.extend(rz(hb, r, x, y, S.ground_z(x, y) + z))
    S.mesh("HayBales", bales, sub="OL_Arena")
    # ---- ARENA RIM: 7 short segments on the oval edge (+1.1 m), alternating hay-bale rows and white/red
    # rails, with 7 openings (corral mouth 7.5 m, arch 8 m, bleachers 7 m, tent / stalls / food / stage
    # 4.3-5 m) - defines the round-up space without blocking runs; the corral wings funnel into the corral.
    arena_rim(S, out)

    # ---- bunting poles around the arena + pennant strings
    poles = []
    for ang in (75, 135, 195, 255, 315, 15):
        a = math.radians(ang)
        p = ARENA + Vector((math.cos(a) * (ARENA_R[0] + 3.4), math.sin(a) * (ARENA_R[1] + 3.4)))
        poles.append(p)
        emit(S, f"BuntingPole_{len(poles)}", bunting_pole(), p.x, p.y, S.ground_z(*p), local=False, sub="OL_Bunting")
    bt = MeshBuilder()
    cols = ["M_Awning_Red", "M_Awning_Yellow", "M_Awning_Blue", "M_Awning_Cream", "M_Awning_Green"]
    for i in range(len(poles)):
        a, b = poles[i], poles[(i + 1) % len(poles)]
        if i == 1:      # leave the side facing the arch un-strung (clear view in)
            continue
        za, zb = S.ground_z(*a) + 4.45, S.ground_z(*b) + 4.45
        n = max(6, int((b - a).length / 1.1))
        bunting(bt, (a.x, a.y, za), (b.x, b.y, zb), n, cols, sag=0.75)
    # arch -> first stall string, tied to the stall's finial (every pennant tip stays >= 4 m; it used to dip
    # to 2.1 m over the walkable stall pad when it was tied to the stall eave)
    bunting(bt, (arch_c.x, arch_c.y + 3.2, 4.9), (stalls[0][0][0], stalls[0][0][1], 3.9 + STALL_FINIAL - 0.06), 9,
            cols, sag=0.35)
    S.mesh("Bunting", bt, sub="OL_Bunting")

    # ---- spectator bleachers on the south side of the arena (crawl space underneath)
    emit(S, "Bleachers", bleachers(), 52.5, -85.0, S.ground_z(52.5, -85.0), rot=math.pi, local=False, sub="OL_Arena")
    # ---- flood lights on the edges
    for (x, y, tx, ty) in ((27.0, -91.5, 1, 0.6), (79.0, -47.5, -1, -0.3), (79.5, -77.0, -1, 0.2)):
        S.put("StreetLight", x, y, rot=face_rot(tx, ty), sub="OL_Lights")
    S.register_lot(S.poly)

    new = [o for o in bpy.data.objects if o.name not in before]
    custom = [o for o in new if o.type == "MESH" and o.data.users == 1]
    out["custom_tris"] = tri_count(custom)
    out["instances"] = S.n
    return out


def _pennant():
    mb = MeshBuilder()
    pts = [Vector((0.06, 0, 0)), Vector((0.9, 0, -0.22)), Vector((0.06, 0, -0.45))]
    o = Vector((0, 0.012, 0))
    mb.face([pts[2] - o, pts[1] - o, pts[0] - o], "M_Awning_Yellow")
    mb.face([pts[0] + o, pts[1] + o, pts[2] + o], "M_Awning_Yellow")
    return mb
