"""NO_BUILD areas: LANTERN COURT, COBBLER YARD and BOATHOUSE SLIP (build_area dispatches on S.id).

LANTERN COURT  (22 x 14 m off Lantern Alley, behind the Union Street shops; frame = world axes)
    A hidden brick-paved courtyard. Brick walls with a cream coping close the alley side (south) and
    the boulevard side (west); the only ways in are an arched gateway from the alley (hanging lantern,
    little sign) and a narrow gap in the west wall - two exits, so chases flow through. The north side
    stays open to the back doors of the Union Street shops: a back-door cafe table + chairs, potted
    plants and a chalkboard. A fig tree in a brick bed, bins / dumpster / crates on the east fence,
    a rain barrel, and festoon string lights zig-zagging over the court from timber poles to the
    south wall coping (the court's namesake, it glows at dusk). Gameplay: raccoons and red pandas
    raid the bins; the centre (hiding spot) stays open, hidden nooks behind the dumpster and the fig.

COBBLER YARD   (20 x 18 m inside the Cobbler Alley dog-leg; frame = world axes)
    A cobbler's back yard enclosed by sheds and shop backs. Timber privacy fences close the gaps but
    leave the entrance at the south-west corner (straight off the alley bend) and a slot in the east
    fence. Along the north side an open lean-to workshop (custom) with a long workbench, lasts, leather
    rolls and a hanging boot sign; a leather drying rack, a hand cart, stacked / scattered pallets,
    crates and barrels; a bench under a young tree by the entrance. In the middle a tarp-covered pallet
    den = the hiding spot (small animals hide under the tarp).

BOATHOUSE SLIP (30 x 16 m on the west quay; local +X downstream along the quay, -Y toward the water)
    A red corrugated boathouse (kit warehouse, gable to the water) with a roller door opening onto a
    timber-sleepered SLIPWAY with launch rails that runs down to the riverwalk at the quay edge (the
    NO_BUILD polygon stops ~2 m short of the water, so the slip ends at the promenade). A kayak trolley
    on the rails, a 6-kayak rack (custom kayaks) west of the slip, a winch post. East of the slip a
    raised boat-club DECK (0.85 m, picket railing, steps from the slip and the riverwalk) with picnic
    tables and a pennant; its lattice skirt has two broken panels -> crawl space UNDER THE DECK (the
    hiding spot). Upside-down kayaks and paddles on the grass.
"""
import math

from mathutils import Matrix, Vector

from .. import config as C
from .. import geom2d as G
from ..assembler import BuildingSpec, H4
from ..meshutil import MeshBuilder
from .town_square import (AWN, CREAM, Counter, bbox, beam, extrude_xz, face_n, flagpole_mb, gem, kit, lantern_mb,
                          lathe, place, put_mb, rbox, shared_mesh, string_lights, tube, v3)
from .marina import kayak_mb, lifering_stand_mb

GZ = C.GROUND_Z
TAU = 2.0 * math.pi


# =============================================================================== shared bits
def paving_mb(P, z, mat, joint_mat=None, joint=1.5, jw=0.06, skirt=0.2):
    """Flat paved slab over polygon P (local), optional joint grid (thin inlays)."""
    from .town_square import clip_convex
    mb = MeshBuilder()
    Pc = G.ensure_ccw([G.V(p) for p in P])
    mb.prism(Pc, z - skirt, z, mat, "M_Curb")
    if joint_mat:
        xs = [p.x for p in Pc]
        ys = [p.y for p in Pc]
        for axis in ("x", "y"):
            lo, hi = (min(xs), max(xs)) if axis == "x" else (min(ys), max(ys))
            c = math.ceil(lo / joint) * joint
            while c < hi:
                if axis == "x":
                    q = [Vector((c - jw / 2, -99)), Vector((c + jw / 2, -99)), Vector((c + jw / 2, 99)),
                         Vector((c - jw / 2, 99))]
                else:
                    q = [Vector((-99, c - jw / 2)), Vector((99, c - jw / 2)), Vector((99, c + jw / 2)),
                         Vector((-99, c + jw / 2))]
                q = clip_convex(q, Pc)
                if len(q) >= 3:
                    mb.tri_fill([G.ensure_ccw(q)], z + 0.008, joint_mat)
                c += joint
    return mb


def brick_wall_mb(a, b, h=2.4, t=0.4, gaps=(), arch=None):
    """Free-standing brick wall from a to b (2D, local), cream coping; gaps = [(s0, s1)] along the wall;
    arch = (s_center, width, height) cuts an arched gateway with a cream surround."""
    mb = MeshBuilder()
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    d = (b - a) / L
    segs = [(0.0, L)]
    cuts = list(gaps)
    if arch:
        sc, w, _ = arch
        cuts.append((sc - w / 2, sc + w / 2))
    for (c0, c1) in cuts:
        nxt = []
        for (s0, s1) in segs:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 > s0:
                nxt.append((s0, c0))
            if c1 < s1:
                nxt.append((c1, s1))
        segs = nxt
    R = Matrix.Rotation(math.atan2(d.y, d.x), 4, "Z")
    T = Matrix.Translation((a.x, a.y, 0.0))
    sub = MeshBuilder()
    for (s0, s1) in segs:
        if s1 - s0 < 0.05:
            continue
        sub.box(s0, -t / 2, GZ - 0.1, s1, t / 2, h, "M_Wall_Brick", skip=("-z",))
        sub.box(s0 - 0.04, -t / 2 - 0.06, h, s1 + 0.04, t / 2 + 0.06, h + 0.14, "M_Trim_White")
        # brick piers every ~3 m
        s = s0
        while s <= s1 + 1e-6:
            sp = min(max(s, s0 + 0.25), s1 - 0.25)
            sub.box(sp - 0.25, -t / 2 - 0.08, GZ - 0.1, sp + 0.25, t / 2 + 0.08, h + 0.08, "M_Wall_Brick",
                    skip=("-z",))
            sub.box(sp - 0.3, -t / 2 - 0.13, h + 0.08, sp + 0.3, t / 2 + 0.13, h + 0.24, "M_Trim_White")
            s += 3.0
    if arch:
        sc, w, ah = arch
        r = w / 2
        zs = ah - r
        # piers + arch over the opening (extruded in the wall plane)
        for side in (-1, 1):
            sub.box(sc + side * r - (0.35 if side < 0 else 0.0), -t / 2 - 0.1, GZ - 0.1,
                    sc + side * r + (0.35 if side > 0 else 0.0), t / 2 + 0.1, h + 0.5, "M_Wall_Brick", skip=("-z",))
        top = h + 0.75
        outer = [(sc - r - 0.35, zs), (sc - r - 0.35, top), (sc + r + 0.35, top), (sc + r + 0.35, zs)]
        pts = [(sc + r, zs)] + [(sc + r * math.cos(math.pi * i / 10), zs + r * math.sin(math.pi * i / 10))
                                 for i in range(1, 10)] + [(sc - r, zs)]
        shape = outer[:1] + outer[1:3] + outer[3:] + pts
        arch_sub = MeshBuilder()
        extrude_xz(arch_sub, G.ensure_ccw([G.V(p) for p in shape]), -t / 2 - 0.1, t / 2 + 0.1, "M_Wall_Brick")
        sub.extend(arch_sub)
        # cream arch surround (key ring) on both faces
        for yf, s in ((-t / 2 - 0.1, -1), (t / 2 + 0.1, 1)):
            ring = MeshBuilder()
            ro, ri = r + 0.22, r
            for i in range(10):
                a0, a1 = math.pi * i / 10, math.pi * (i + 1) / 10
                q = [(sc + ro * math.cos(a0), zs + ro * math.sin(a0)), (sc + ro * math.cos(a1), zs + ro * math.sin(a1)),
                     (sc + ri * math.cos(a1), zs + ri * math.sin(a1)), (sc + ri * math.cos(a0), zs + ri * math.sin(a0))]
                extrude_xz(ring, G.ensure_ccw([G.V(p) for p in q]), yf - 0.05 if s < 0 else yf,
                           yf if s < 0 else yf + 0.05, "M_Trim_White")
            sub.extend(ring)
        sub.box(sc - r - 0.45, -t / 2 - 0.16, top, sc + r + 0.45, t / 2 + 0.16, top + 0.16, "M_Trim_White")
    mb.extend(sub, T @ R)
    return mb


def post_mb(h=4.2):
    """Timber pole for string lights with a little cross arm."""
    mb = MeshBuilder()
    bbox(mb, -0.09, -0.09, GZ - 0.2, 0.09, 0.09, h, "M_Trim_Wood", bevel=0.02)
    bbox(mb, -0.25, -0.05, h - 0.35, 0.25, 0.05, h - 0.25, "M_Trim_Wood")
    bbox(mb, -0.2, -0.2, GZ - 0.05, 0.2, 0.2, 0.25, "M_Wall_Concrete")
    return mb


def aframe_mb():
    """Chalkboard A-frame sign (front -Y)."""
    mb = MeshBuilder()
    for s in (-1, 1):
        rot = Matrix.Rotation(s * 0.2, 4, "X")
        sub = MeshBuilder()
        bbox(sub, -0.32, -0.025, 0.0, 0.32, 0.025, 0.95, "M_Trim_Wood")
        bbox(sub, -0.26, -0.035 if s < 0 else 0.025, 0.12, 0.26, -0.025 if s < 0 else 0.035, 0.85, "M_Sign_Board")
        for k, z in enumerate((0.7, 0.55, 0.4)):
            bbox(sub, -0.18, -0.04 if s < 0 else 0.035, z, 0.1 + 0.05 * k, -0.035 if s < 0 else 0.04, z + 0.05,
                 "M_Wall_White")
        mb.extend(sub, Matrix.Translation((0, s * 0.16, 0)) @ rot)
    return mb


# =============================================================================== LANTERN COURT
def lantern_court(S, cnt):
    P = [S.to_local(p) for p in S.poly]
    x0, y0, x1, y1 = G.bbox(P)
    ZP = 0.06
    put_mb(S, "Paving", paving_mb(P, ZP, "M_Plaza_Accent", "M_Plaza", joint=1.2, jw=0.07), 0, 0, 0,
           sub="Ground", counter=cnt)
    # walls: south (alley side) with the arched gateway, west with a narrow gap
    ws = brick_wall_mb((x0 + 0.3, y0 + 0.3), (x1 - 0.3, y0 + 0.3), h=2.5, arch=(8.5, 2.2, 3.0))
    put_mb(S, "Wall_South", ws, 0, 0, 0, sub="Walls", counter=cnt)
    ww = brick_wall_mb((x0 + 0.3, y1 - 0.3), (x0 + 0.3, y0 + 0.3), h=2.5, gaps=[(3.2, 4.6)])
    put_mb(S, "Wall_West", ww, 0, 0, 0, sub="Walls", counter=cnt)
    gate_x = x0 + 0.3 + 8.5
    # sign over the gateway + lanterns
    sg = MeshBuilder()
    bbox(sg, -1.0, -0.08, 0.0, 1.0, 0.0, 0.42, "M_Sign_Board", bevel=0.02)
    bbox(sg, -0.9, -0.1, 0.06, 0.9, -0.08, 0.36, "M_Sign_Face")
    for k in range(5):
        bbox(sg, -0.7 + 0.3 * k, -0.12, 0.15, -0.5 + 0.3 * k, -0.1, 0.27, "M_Trim_Dark")
    put_mb(S, "GateSign", sg, gate_x, y0 + 0.3 - 0.36, 3.42, 0.0, sub="Walls", counter=cnt)
    lan = shared_mesh("CT_WallLantern", lantern_mb)
    for (x, y, r) in ((gate_x - 1.75, y0 + 0.08, 0.0), (gate_x + 1.75, y0 + 0.08, 0.0),
                      (gate_x - 1.75, y0 + 0.52, math.pi), (x0 + 0.52, 1.0, math.pi / 2),
                      (x0 + 0.52, -4.5, math.pi / 2)):
        place(S, lan, "WallLantern", x, y, 2.15, r, sub="Lights", counter=cnt)
    # fig tree in a brick bed
    fx, fy = -6.0, 1.4
    bed = MeshBuilder()
    bbox(bed, -1.25, -1.25, GZ - 0.1, 1.25, 1.25, 0.5, "M_Wall_Brick")
    bbox(bed, -1.35, -1.35, 0.5, 1.35, 1.35, 0.6, "M_Trim_White")
    bbox(bed, -1.0, -1.0, 0.6, 1.0, 1.0, 0.62, "M_Dirt")
    put_mb(S, "FigBed", bed, fx, fy, 0.0, sub="Fig", counter=cnt)
    kit(S, "Tree_Round_A", fx, fy, 0.55, 0.6, recolor={"foliage": "M_Foliage_Dark"}, sub="Fig",
        scale=(1.15, 1.15, 1.05))
    # string lights: poles along the north edge, anchors on the south wall coping
    po = shared_mesh("CT_LightPost", post_mb)
    poles = [Vector((x, y1 - 0.6)) for x in (-8.6, -0.4, 7.8)]
    for i, p in enumerate(poles):
        place(S, po, f"LightPost_{i + 1}", p.x, p.y, 0.0, 0.0, sub="Lights", counter=cnt)
    sl = MeshBuilder()
    south = [Vector((x, y0 + 0.3, 2.62)) for x in (-10.0, -4.5, 1.0, 6.0, 10.2)]
    tops = [Vector((p.x, p.y, 4.0)) for p in poles]
    for (a, b) in ((tops[0], south[0]), (tops[0], south[1]), (tops[1], south[1]), (tops[1], south[2]),
                   (tops[1], south[3]), (tops[2], south[3]), (tops[2], south[4]), (tops[0], tops[1]),
                   (tops[1], tops[2])):
        string_lights(sl, a, b, sag=0.5, step=1.15, r=0.07, seg_len=2.6)     # lean: <= 800 tris in all
    put_mb(S, "StringLights", sl, 0, 0, 0, sub="Lights", counter=cnt)
    # back-door cafe corner (north side, shop back doors)
    kit(S, "CafeTable", -1.6, 3.6, ZP, 0.3, recolor={"awning": "M_Awning_Green"}, sub="Cafe")
    kit(S, "CafeTable", 2.4, 4.3, ZP, 1.1, recolor={"awning": "M_Awning_Yellow"}, sub="Cafe")
    for (x, y) in ((-3.8, 5.9), (4.6, 6.0), (0.4, 6.2)):
        kit(S, "Planter", x, y, ZP, 0.0, sub="Cafe")
    af = shared_mesh("CT_AFrame", aframe_mb)
    place(S, af, "Chalkboard", gate_x - 0.6, y0 + 2.0, ZP, math.radians(160), sub="Cafe", counter=cnt)
    # bins / dumpster / crates along the east side
    kit(S, "Dumpster", x1 - 1.1, -2.8, ZP, -math.pi / 2, recolor=None, sub="Bins")
    kit(S, "TrashBin", x1 - 0.7, -0.8, ZP, 0.4, sub="Bins")
    kit(S, "TrashBin", x1 - 0.75, -0.1, ZP, 1.2, sub="Bins")
    kit(S, "CrateStack", x1 - 1.0, 3.2, ZP, -math.pi / 2, sub="Bins")
    kit(S, "Crate", x1 - 2.3, 4.6, ZP, 0.35, sub="Bins")
    kit(S, "Crate", x1 - 1.3, 5.6, ZP, 0.8, sub="Bins")
    kit(S, "Pallet", x1 - 2.6, -5.6, ZP, 0.2, sub="Bins")
    kit(S, "Barrel", x0 + 0.95, 5.8, ZP, 0.0, sub="Bins")
    kit(S, "Barrel", x0 + 1.0, -2.6, ZP, 0.0, sub="Bins")
    kit(S, "Bench", -9.9, -1.2, ZP, -math.pi / 2, sub="Cafe")
    # east fence (timber) leaving a slot to the alley bend
    for y in (-5.3, -2.3, 3.7):
        kit(S, "Fence_Wood_3m", x1 - 0.25, y, ZP, math.pi / 2, sub="Walls")
    S.register_lot(S.poly)


# =============================================================================== COBBLER YARD
def lean_to_mb(w=8.0, d=3.4, hb=3.1, hf=2.45):
    """Open lean-to workshop (front -Y, origin = front centre at ground): timber frame, board back
    wall, corrugated mono-pitch roof, long workbench with lasts, tools and leather rolls."""
    mb = MeshBuilder()
    hw = w / 2
    for x in (-hw + 0.1, -hw / 3, hw / 3, hw - 0.1):
        bbox(mb, x - 0.08, -0.08, GZ, x + 0.08, 0.08, hf, "M_Trim_Wood")
        bbox(mb, x - 0.08, d - 0.08, GZ, x + 0.08, d + 0.08, hb, "M_Trim_Wood")
    bbox(mb, -hw, -0.1, hf - 0.18, hw, 0.1, hf, "M_Trim_Wood")
    bbox(mb, -hw, d - 0.1, hb - 0.18, hw, d + 0.1, hb, "M_Trim_Wood")
    # back wall boards + half side walls
    bbox(mb, -hw, d - 0.02, GZ, hw, d + 0.06, hb - 0.18, "M_Fence_Wood")
    for x in range(int(w / 0.5)):
        xx = -hw + 0.25 + 0.5 * x
        bbox(mb, xx - 0.02, d - 0.05, GZ + 0.1, xx + 0.02, d - 0.02, hb - 0.25, "M_Trim_Wood")
    for s in (-1, 1):
        bbox(mb, s * hw - 0.04, 0.3, GZ, s * hw + 0.04, d, 1.4, "M_Fence_Wood")
    # roof (sloped slab, corrugated metal) with overhang
    a = Vector((-hw - 0.35, -0.55, hf + 0.02))
    roof = MeshBuilder()
    L = d + 0.9
    rise = hb - hf
    ang = math.atan2(rise, d)
    roof.box(-hw - 0.35, 0.0, 0.0, hw + 0.35, L / math.cos(ang), 0.1, "M_Wall_Corrugated")
    for k in range(int((w + 0.7) / 0.35)):
        xx = -hw - 0.2 + 0.35 * k
        roof.box(xx - 0.04, 0.0, 0.1, xx + 0.04, L / math.cos(ang), 0.15, "M_Wall_Corrugated")
    mb.extend(roof, Matrix.Translation((0.0, -0.55, hf - 0.04 - 0.55 * math.tan(ang))) @ Matrix.Rotation(ang, 4, "X"))
    # workbench + goods
    bbox(mb, -hw + 0.5, d - 1.0, 0.85, hw - 0.5, d - 0.25, 0.95, "M_Trim_Wood", bevel=0.02)
    for x in (-hw + 0.7, -0.2, hw - 0.7):
        bbox(mb, x - 0.06, d - 0.95, GZ, x + 0.06, d - 0.3, 0.85, "M_Trim_Wood")
    bbox(mb, -hw + 0.5, d - 0.95, 0.25, hw - 0.5, d - 0.3, 0.3, "M_Trim_Wood")          # lower shelf
    for i in range(6):                                                                  # shoe lasts
        x = -hw + 1.0 + i * 0.45
        rbox(mb, (x, d - 0.62, 1.02), (0.12, 0.28, 0.13), "M_Door_Wood" if i % 2 else "M_Trim_Dark", rot_z=0.15 * i)
    for i, m in enumerate(("M_Door_Red", "M_Door_Wood", "M_Awning_Cream")):            # leather rolls
        x = 0.8 + i * 0.5
        sub = MeshBuilder()
        sub.cylinder(0, 0, -0.35, 0.35, 0.15, m, seg=8, cap_bottom=True)
        mb.extend(sub, Matrix.Translation((x, d - 0.6, 1.1)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    for i in range(5):                                                                  # tools on the wall
        x = -hw + 1.2 + i * 0.4
        bbox(mb, x - 0.03, d - 0.07, 1.4, x + 0.03, d - 0.03, 1.9 - 0.08 * (i % 3), "M_Metal_Dark")
    bbox(mb, hw - 2.3, d - 0.1, 1.35, hw - 0.9, d - 0.04, 1.75, "M_Metal")             # sharpening board
    # pairs of boots on the lower shelf
    for i in range(4):
        x = -hw + 1.2 + i * 0.5
        bbox(mb, x - 0.08, d - 0.8, 0.3, x + 0.08, d - 0.5, 0.42, "M_Door_Wood")
        bbox(mb, x - 0.08, d - 0.55, 0.3, x + 0.08, d - 0.45, 0.62, "M_Door_Wood")
    return mb


def boot_sign_mb():
    """Hanging boot sign on a wall bracket (bracket base at x = 0 pointing +X)."""
    mb = MeshBuilder()
    beam(mb, (0.0, 0.0, 0.0), (1.05, 0.0, 0.0), 0.06, 0.06, "M_Metal_Dark")
    beam(mb, (0.0, 0.0, -0.35), (0.6, 0.0, 0.0), 0.04, 0.04, "M_Metal_Dark")
    for x in (0.35, 0.95):
        bbox(mb, x - 0.012 - 0.01, -0.012 - 0.01, -0.3, x + 0.022, 0.022, 0.0, "M_Metal_Dark")
    boot = [(0.25, -1.15), (1.1, -1.15), (1.15, -1.0), (1.0, -0.88), (0.62, -0.8), (0.58, -0.3), (0.22, -0.3)]
    extrude_xz(mb, G.ensure_ccw([G.V(p) for p in boot]), -0.07, 0.07, "M_Sign_Accent", side="M_Door_Wood")
    sole = [(0.22, -1.22), (1.15, -1.22), (1.15, -1.13), (0.22, -1.13)]
    extrude_xz(mb, G.ensure_ccw([G.V(p) for p in sole]), -0.08, 0.08, "M_Trim_Dark")
    return mb


def drying_rack_mb():
    """A-frame rack with three leather hides draped over the top bar."""
    mb = MeshBuilder()
    for x in (-1.2, 1.2):
        beam(mb, (x, -0.6, GZ), (x, 0.0, 1.7), 0.08, 0.08, "M_Trim_Wood")
        beam(mb, (x, 0.6, GZ), (x, 0.0, 1.7), 0.08, 0.08, "M_Trim_Wood")
    tube(mb, (-1.35, 0.0, 1.62), (1.35, 0.0, 1.62), 0.05, "M_Trim_Wood", seg=6, cap0=True)
    for i, (x, m) in enumerate(((-0.75, "M_Door_Wood"), (0.0, "M_Crate"), (0.75, "M_Door_Red"))):
        for s in (-1, 1):
            q0 = Vector((x - 0.32, 0.0, 1.66))
            face_n(mb, [v3(x - 0.32, 0.0, 1.66), v3(x + 0.32, 0.0, 1.66), v3(x + 0.28, s * 0.32, 0.75 + 0.1 * i),
                        v3(x - 0.3, s * 0.3, 0.8)], m, (0, s, 0.3))
            face_n(mb, [v3(x - 0.32, 0.0, 1.66), v3(x + 0.32, 0.0, 1.66), v3(x + 0.28, s * 0.32, 0.75 + 0.1 * i),
                        v3(x - 0.3, s * 0.3, 0.8)], m, (0, -s, -0.3))
    return mb


def hand_cart_mb():
    """Two-wheeled hand cart (front -Y) with a couple of boxes."""
    mb = MeshBuilder()
    bbox(mb, -0.55, -0.75, 0.42, 0.55, 0.75, 0.5, "M_Wood_Light")
    for s in (-1, 1):
        bbox(mb, s * 0.55 - 0.03, -0.75, 0.5, s * 0.55 + 0.03, 0.75, 0.75, "M_Wood_Light")
        sub = MeshBuilder()
        sub.cylinder(0, 0, -0.04, 0.04, 0.38, "M_Trim_Dark", seg=10, cap_bottom=True)
        mb.extend(sub, Matrix.Translation((s * 0.62, 0.15, 0.38)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        beam(mb, (s * 0.45, 0.75, 0.48), (s * 0.4, 1.7, 0.9), 0.05, 0.05, "M_Trim_Wood")
    bbox(mb, -0.08, -0.7, GZ, 0.08, -0.6, 0.42, "M_Trim_Wood")
    bbox(mb, -0.45, -0.6, 0.5, 0.05, -0.05, 0.85, "M_Crate")
    bbox(mb, 0.0, 0.0, 0.5, 0.42, 0.55, 0.72, "M_Door_Wood")
    return mb


def tarp_den_mb():
    """Two pallet stacks with a tarp draped over a ridge pole between them (hidey hole)."""
    mb = MeshBuilder()
    for x in (-1.15, 1.15):
        for k in range(5):
            z = GZ + 0.03 + 0.15 * k
            bbox(mb, x - 0.5, -0.6, z, x + 0.5, 0.6, z + 0.12, "M_Wood_Light")
    tube(mb, (-1.5, 0.0, 1.15), (1.5, 0.0, 1.15), 0.04, "M_Trim_Wood", seg=4, cap0=True)
    # tarp: two sloped panels (double sided) with a sagging middle
    for s in (-1, 1):
        pts = [v3(-1.75, 0.0, 1.2), v3(1.75, 0.0, 1.2), v3(1.8, s * 0.95, 0.35), v3(0.0, s * 1.0, 0.55),
               v3(-1.8, s * 0.95, 0.35)]
        face_n(mb, pts, "M_Awning_Blue", (0, s, 1))
        face_n(mb, pts, "M_Awning_Blue", (0, -s, -1))
    return mb


def cobbler_yard(S, cnt):
    P = [S.to_local(p) for p in S.poly]
    x0, y0, x1, y1 = G.bbox(P)
    ZP = 0.03
    put_mb(S, "Ground", paving_mb(P, ZP, "M_Path"), 0, 0, 0, sub="Ground", counter=cnt)
    # dirt patches (inlays)
    dm = MeshBuilder()
    for (cx, cy, r) in ((-1.0, 0.5, 2.6), (4.5, -4.0, 1.6), (-6.0, 4.2, 1.8), (6.5, 3.0, 1.5), (-7.0, -6.0, 1.4)):
        ring = [(cx + r * math.cos(TAU * i / 10) * (1.0 + 0.12 * math.sin(3 * i)),
                 cy + r * 0.75 * math.sin(TAU * i / 10)) for i in range(10)]
        dm.tri_fill([G.ensure_ccw([G.V(p) for p in ring])], ZP + 0.008, "M_Dirt")
    put_mb(S, "DirtPatches", dm, 0, 0, 0, sub="Ground", counter=cnt)
    # fences: south (leave SW entrance), west (leave SW), east with a slot
    for x in (-3.5 + 3.0 * k for k in range(5)):
        kit(S, "Fence_Wood_3m", x, y0 + 0.2, ZP, 0.0, sub="Fences")
    for y in (-2.5 + 3.0 * k for k in range(4)):
        kit(S, "Fence_Wood_3m", x0 + 0.2, y, ZP, math.pi / 2, sub="Fences")
    for y in (-7.5, -4.5, 2.5, 5.5):
        kit(S, "Fence_Wood_3m", x1 - 0.2, y, ZP, math.pi / 2, sub="Fences")
    # lean-to workshop along the north side
    lt = lean_to_mb()
    put_mb(S, "Workshop", lt, -3.0, y1 - 4.2, ZP - GZ, 0.0, sub="Workshop", counter=cnt)
    put_mb(S, "BootSign", boot_sign_mb(), 1.0, y1 - 4.25, 2.35, 0.0, sub="Workshop", counter=cnt)
    put_mb(S, "DryingRack", drying_rack_mb(), 5.2, 4.6, ZP - GZ, 0.25, sub="Workshop", counter=cnt)
    # pallets: stacks and scatter
    for (x, y, n, r) in ((7.6, -6.6, 5, 0.1), (8.4, -4.3, 3, -0.3), (5.9, -7.4, 2, 0.6), (-8.4, 3.0, 4, 0.0),
                         (-8.5, 4.4, 2, 0.15)):
        for k in range(n):
            kit(S, "Pallet", x, y, ZP + 0.147 * k, r + 0.06 * (k % 2) - 0.03, sub="Clutter")
    put_mb(S, "TarpDen", tarp_den_mb(), 0.2, -0.6, ZP - GZ, 0.12, sub="Clutter", counter=cnt)
    kit(S, "CrateStack", 3.3, 7.6, ZP, 0.0, sub="Clutter")
    kit(S, "Crate", 4.6, 7.4, ZP, 0.4, sub="Clutter")
    kit(S, "Barrel", 8.3, 7.4, ZP, 0.0, sub="Clutter")
    kit(S, "Barrel", 8.9, 6.6, ZP, 0.0, sub="Clutter")
    kit(S, "Barrel", 8.4, 1.0, ZP, 0.0, sub="Clutter")
    kit(S, "TrashBin", 8.8, 3.8, ZP, 0.0, sub="Clutter")
    put_mb(S, "HandCart", hand_cart_mb(), 3.4, -2.6, ZP - GZ, math.radians(-35), sub="Clutter", counter=cnt)
    # bench under a young tree by the entrance
    kit(S, "Tree_Small", -6.8, -3.8, ZP, 0.3, recolor={"foliage": "M_Foliage_Autumn"}, sub="Clutter")
    kit(S, "Bench", -4.6, -5.6, ZP, math.radians(160), sub="Clutter")
    kit(S, "Planter", -8.8, -1.4, ZP, 0.0, sub="Clutter")
    S.register_lot(S.poly)


# =============================================================================== BOATHOUSE SLIP
def kayak_rack_mb(n_cols=2, n_rows=3):
    """Freestanding kayak rack (kayaks along X): two timber frames with cross arms."""
    mb = MeshBuilder()
    for x in (-1.0, 1.0):
        for y in (-0.55 - 0.45 * (n_cols - 1), 0.55 + 0.45 * (n_cols - 1)):
            bbox(mb, x - 0.07, y - 0.07, GZ - 0.1, x + 0.07, y + 0.07, 0.35 + 0.5 * n_rows, "M_Trim_Wood")
        for r in range(n_rows):
            z = 0.3 + 0.5 * r
            bbox(mb, x - 0.08, -1.0 - 0.45 * (n_cols - 1), z, x + 0.08, 1.0 + 0.45 * (n_cols - 1), z + 0.08,
                 "M_Trim_Wood")
        bbox(mb, x - 0.09, -1.05 - 0.45 * (n_cols - 1), 0.35 + 0.5 * n_rows, x + 0.09, 1.05 + 0.45 * (n_cols - 1),
             0.45 + 0.5 * n_rows, "M_Trim_Wood")
    return mb


def slipway_mb(L, W, z_top, z_end):
    """Concrete slipway with timber sleepers and two steel launch rails, from y=0 (top) to y=-L."""
    def zat(y):
        return z_top + (z_top - z_end) * (y / L)
    mb = MeshBuilder()
    pts_top = [v3(-W / 2, -L, z_end), v3(W / 2, -L, z_end), v3(W / 2, 0.0, z_top), v3(-W / 2, 0.0, z_top)]
    face_n(mb, pts_top, "M_Concrete", (0, 0, 1))
    for s in (-1, 1):
        face_n(mb, [v3(s * W / 2, -L, GZ - 0.25), v3(s * W / 2, 0.0, GZ - 0.25), v3(s * W / 2, 0.0, z_top),
                    v3(s * W / 2, -L, z_end)], "M_Curb", (s, 0, 0))
    face_n(mb, [v3(-W / 2, -L, GZ - 0.25), v3(W / 2, -L, GZ - 0.25), v3(W / 2, -L, z_end), v3(-W / 2, -L, z_end)],
           "M_Curb", (0, -1, 0))
    face_n(mb, [v3(-W / 2, 0.0, GZ - 0.25), v3(W / 2, 0.0, GZ - 0.25), v3(W / 2, 0.0, z_top), v3(-W / 2, 0.0, z_top)],
           "M_Curb", (0, 1, 0))
    y = -0.6
    while y > -L + 0.3:
        z = zat(y)
        bbox(mb, -W / 2 + 0.15, y - 0.14, z - 0.02, W / 2 - 0.15, y + 0.14, z + 0.07, "M_Trim_Wood")
        y -= 0.9
    for x in (-0.55, 0.55):
        q = MeshBuilder()
        q.box(x - 0.06, -L + 0.1, 0.0, x + 0.06, -0.1, 0.12, "M_Metal_Dark")
        sh = Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, (z_top - z_end) / L, 1, z_top + 0.03), (0, 0, 0, 1)))
        mb.extend(q, sh)
    return mb


def deck_mb(x0, x1, y0, y1, h, skirt_gaps=()):
    """Raised timber deck (top at h) on posts, joists, lattice skirt panels with gaps (crawl holes)."""
    mb = MeshBuilder()
    bbox(mb, x0, y0, h - 0.12, x1, y1, h, "M_Wood_Light")
    x = x0 + 0.6
    while x < x1 - 0.2:
        bbox(mb, x - 0.025, y0 + 0.03, h, x + 0.025, y1 - 0.03, h + 0.008, "M_Trim_Wood")
        x += 0.6
    bbox(mb, x0 - 0.04, y0 - 0.04, h - 0.3, x1 + 0.04, y0 + 0.06, h - 0.02, "M_Trim_Wood")    # fascia
    bbox(mb, x0 - 0.04, y1 - 0.06, h - 0.3, x1 + 0.04, y1 + 0.04, h - 0.02, "M_Trim_Wood")
    bbox(mb, x0 - 0.04, y0, h - 0.3, x0 + 0.06, y1, h - 0.02, "M_Trim_Wood")
    bbox(mb, x1 - 0.06, y0, h - 0.3, x1 + 0.04, y1, h - 0.02, "M_Trim_Wood")
    for x in (x0 + 0.2, (x0 + x1) / 2, x1 - 0.2):
        for y in (y0 + 0.2, (y0 + y1) / 2, y1 - 0.2):
            bbox(mb, x - 0.1, y - 0.1, GZ - 0.1, x + 0.1, y + 0.1, h - 0.12, "M_Trim_Wood")
    # board skirt: panels of three horizontal boards between the posts, some missing (crawl holes)
    sides = [((x0, y0), (x1, y0), (0, -1)), ((x1, y0), (x1, y1), (1, 0)), ((x1, y1), (x0, y1), (0, 1)),
             ((x0, y1), (x0, y0), (-1, 0))]
    for si, (a, b, n) in enumerate(sides):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        d = (b - a) / L
        npan = max(1, round(L / 1.5))
        nv = Vector(n)
        for k in range(npan):
            pa = a + d * (L * k / npan) + nv * 0.03
            pb = a + d * (L * (k + 1) / npan) + nv * 0.03
            broken = (si, k) in skirt_gaps
            for j, (z0, z1) in enumerate(((GZ + 0.02, 0.17), (0.25, 0.41), (0.49, h - 0.3))):
                if broken and j < 2:
                    continue        # bottom boards missing: crawl hole
                bbox(mb, min(pa.x, pb.x) - 0.02 * abs(nv.x) - 0.01, min(pa.y, pb.y) - 0.02 * abs(nv.y) - 0.01, z0,
                     max(pa.x, pb.x) + 0.02 * abs(nv.x) + 0.01, max(pa.y, pb.y) + 0.02 * abs(nv.y) + 0.01, z1,
                     "M_Fence_Wood")
            if broken:              # one board hanging askew
                c = (pa + pb) / 2
                beam(mb, (c.x - d.x * 0.6, c.y - d.y * 0.6, 0.47), (c.x + d.x * 0.5, c.y + d.y * 0.5, 0.05),
                     0.04, 0.15, "M_Fence_Wood", up=(nv.x, nv.y, 0.0))
    return mb


def steps_mb(w, n, rise, run):
    """Timber steps going DOWN toward -Y from y=0 (top step top at n*rise)."""
    mb = MeshBuilder()
    for k in range(n):
        z = rise * (n - k)
        bbox(mb, -w / 2, -run * (k + 1), GZ - 0.05, w / 2, -run * k, z, "M_Wood_Light")
    return mb


def boathouse_slip(S, cnt):
    d = S.poly[1] - S.poly[2]
    S.rot = math.atan2(d.y, d.x)                  # local +X downstream along the quay, -Y to the water
    P = [S.to_local(p) for p in S.poly]
    x0, y0, x1, y1 = G.bbox(P)
    # gravel apron in front of the boathouse
    apron = [Vector((x0 + 0.2, y0 + 1.2)), Vector((-1.8, y0 + 1.2)), Vector((-1.8, -1.2)), Vector((x0 + 0.2, -1.2))]
    put_mb(S, "Apron", paving_mb(apron, 0.02, "M_Gravel", skirt=0.15), 0, 0, 0, sub="Ground", counter=cnt)
    # boathouse (kit warehouse, gable + roller door to the water)
    bx, by = -7.0, -1.2
    spec = BuildingSpec("warehouse", 3, 3, 1, dict(wall="M_Wall_Brick", trim="M_Trim_White", door="M_Door_Wood",
                                                    awning="M_Awning_Red", roof="M_Roof_Charcoal",
                                                    sign="M_Awning_Red"),
                        roof="gable_front", ground_h=H4, feats={"rollers": [1]}, seed=2718)
    S.building(spec, S.to_world(bx, by), S.rot, name=f"LM_{S.id}_Boathouse")
    sg = MeshBuilder()
    bbox(sg, -1.6, -0.1, 0.0, 1.6, 0.0, 0.6, "M_Sign_Board", bevel=0.02)
    bbox(sg, -1.5, -0.13, 0.07, 1.5, -0.1, 0.53, "M_Sign_Face")
    for k in range(6):
        bbox(sg, -1.2 + 0.42 * k, -0.15, 0.2, -0.92 + 0.42 * k, -0.13, 0.4, "M_Door_Red" if k % 2 else "M_Trim_Dark")
    put_mb(S, "ClubSign", sg, bx, by - 0.02, C.LOT_Z + H4 + 0.35, 0.0, sub="Boathouse", counter=cnt)
    lr = shared_mesh("MA_LifeRingStand", lifering_stand_mb)
    # slipway from the roller door to the riverwalk
    sl_len = (by - 0.05) - (y0 + 0.05)
    put_mb(S, "Slipway", slipway_mb(sl_len, 3.4, C.LOT_Z, GZ + 0.02), bx, by - 0.05, 0.0, sub="Slipway",
           counter=cnt)
    # winch post by the door
    wm = MeshBuilder()
    bbox(wm, -0.15, -0.15, GZ, 0.15, 0.15, 1.0, "M_Hazard", bevel=0.02)
    sub = MeshBuilder()
    sub.cylinder(0, 0, -0.25, 0.25, 0.18, "M_Metal_Dark", seg=8, cap_bottom=True)
    wm.extend(sub, Matrix.Translation((0, -0.2, 0.85)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    put_mb(S, "Winch", wm, bx + 2.3, by - 0.6, 0.0, 0.0, sub="Slipway", counter=cnt)
    # kayaks: one on a trolley on the slip, six on the rack, two upside down on the grass
    ky = shared_mesh("CT_Kayak", kayak_mb)
    cols = ["M_Awning_Yellow", "M_Hazard_Orange", "M_Awning_Red", "M_Awning_Teal", "M_Awning_Green",
            "M_Awning_Blue", "M_Awning_Yellow", "M_Awning_Red", "M_Awning_Teal"]
    tr = MeshBuilder()
    bbox(tr, -0.35, -0.9, 0.35, 0.35, 0.9, 0.42, "M_Metal_Dark")
    for s in (-1, 1):
        w = MeshBuilder()
        w.cylinder(0, 0, -0.05, 0.05, 0.2, "M_Trim_Dark", seg=8, cap_bottom=True)
        tr.extend(w, Matrix.Translation((s * 0.45, 0.0, 0.2)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        bbox(tr, s * 0.38 - 0.03, -0.03, 0.2, s * 0.38 + 0.03, 0.03, 0.42, "M_Metal_Dark")
    ty = by - 3.6
    tz = C.LOT_Z + (C.LOT_Z - GZ - 0.02) * ((ty - by) / sl_len) + 0.03
    put_mb(S, "KayakTrolley", tr, bx + 0.0, ty, tz, 0.0, sub="Kayaks", counter=cnt)
    place(S, ky, "Kayak_Trolley", bx, ty, tz + 0.42, math.pi / 2, recolor={AWN: cols[0]}, sub="Kayaks",
          counter=cnt)
    rk = MeshBuilder()
    rk.extend(kayak_rack_mb())
    rx, ry = x0 + 3.0, y0 + 3.3
    put_mb(S, "KayakRack", rk, rx, ry, 0.0, 0.0, sub="Kayaks", counter=cnt)
    for r in range(3):
        for c, yy in enumerate((-0.5, 0.5)):
            if r == 2 and c == 1:
                continue
            place(S, ky, f"Kayak_Rack_{r}{c}", rx, ry + yy, 0.38 + 0.5 * r, 0.0, recolor={AWN: cols[1 + r * 2 + c]},
                  sub="Kayaks", counter=cnt)
    # club deck (raised) with the crawl space under it (hiding spot)
    dx0, dx1, dy0, dy1 = -1.2, 11.8, y0 + 1.4, 2.6
    H = 0.85
    dk = deck_mb(dx0, dx1, dy0, dy1, H, skirt_gaps={(0, 2), (0, 3), (1, 1)})
    put_mb(S, "ClubDeck", dk, 0.0, 0.0, 0.0, sub="Deck", counter=cnt)
    st = steps_mb(1.6, 4, H / 4.0, 0.32)
    put_mb(S, "DeckSteps_S", st, 8.6, dy0, 0.0, 0.0, sub="Deck", counter=cnt)
    put_mb(S, "DeckSteps_W", steps_mb(1.6, 4, H / 4.0, 0.32), dx0, -4.4, 0.0, -math.pi / 2, sub="Deck", counter=cnt)
    # picket railing on the deck edge (gaps at the steps)
    for (x, y, r) in ((dx0 + 1.5, dy0 + 0.05, 0.0), (dx0 + 4.5, dy0 + 0.05, 0.0), (dx0 + 7.5, dy0 + 0.05, 0.0),
                      (dx1 - 1.5, dy1 - 0.05, 0.0), (dx1 - 4.5, dy1 - 0.05, 0.0), (dx1 - 7.5, dy1 - 0.05, 0.0),
                      (dx1 - 10.5, dy1 - 0.05, 0.0),
                      (dx1 - 0.05, dy0 + 1.5, math.pi / 2), (dx1 - 0.05, dy0 + 4.5, math.pi / 2),
                      (dx1 - 0.05, dy0 + 7.5, math.pi / 2),
                      (dx0 + 0.05, dy1 - 1.4, math.pi / 2), (dx0 + 0.05, dy1 - 4.2, math.pi / 2)):
        kit(S, "Fence_Picket_3m", x, y, H, r, sub="Deck")
    kit(S, "PicnicTable", 2.6, -1.4, H, 0.0, sub="Deck")
    kit(S, "PicnicTable", 6.4, -1.0, H, 0.12, sub="Deck")
    kit(S, "Bench", 4.6, dy0 + 0.75, H, math.pi, sub="Deck")
    kit(S, "Lamp_Park", dx1 - 0.6, dy0 + 0.6, H, 0.0, sub="Deck")
    kit(S, "Lamp_Park", dx0 + 0.6, dy1 - 0.6, H, 0.0, sub="Deck")
    place(S, lr, "LifeRing", dx1 - 2.6, dy0 + 0.45, H, 0.0, sub="Deck", counter=cnt)
    fp = shared_mesh("TS_FlagPole", flagpole_mb, smooth=("M_Awning_Yellow", "M_Metal"))
    place(S, fp, "ClubPennant", dx1 + 1.4, 1.2, GZ, 0.0, recolor={AWN: "M_Awning_Red"}, sub="Deck",
          scale=(0.85, 0.85, 0.85), counter=cnt)
    # upside-down kayaks + paddles on the grass, crates by the boathouse
    for i, (x, y, r) in enumerate(((12.9, -4.3, 0.2), (14.15, -3.5, -0.1))):
        o = place(S, ky, f"Kayak_Grass_{i}", x, y, GZ + 0.39, math.pi / 2 + r, recolor={AWN: cols[6 + i]},
                  sub="Kayaks", counter=cnt)
        o.rotation_euler[0] = math.pi            # upside down (rotation, no negative scale)
    pd = MeshBuilder()
    for i in range(3):
        beam(pd, (-0.9 + 0.25 * i, 0.0, 0.02), (0.9 + 0.25 * i, 0.12, 0.05), 0.06, 0.04, "M_Trim_Wood")
        for s in (-1, 1):
            rbox(pd, (s * 1.0 + 0.25 * i, 0.06 * (s + 1), 0.04), (0.42, 0.18, 0.03), "M_Awning_Yellow")
    put_mb(S, "Paddles", pd, 12.0, -6.2, GZ, 0.3, sub="Kayaks", counter=cnt)
    kit(S, "CrateStack", x0 + 1.4, 5.2, GZ, math.pi / 2, sub="Clutter")
    kit(S, "Barrel", x0 + 1.0, 3.2, GZ, 0.0, sub="Clutter")
    kit(S, "Barrel", x0 + 1.6, 2.6, GZ, 0.0, sub="Clutter")
    S.register_lot(S.poly)


# =============================================================================== dispatch
def build_area(S):
    cnt = Counter()
    if S.id == "LanternCourt":
        lantern_court(S, cnt)
    elif S.id == "CobblerYard":
        cobbler_yard(S, cnt)
    elif S.id == "BoathouseSlip":
        boathouse_slip(S, cnt)
    else:
        return dict(skipped=S.id)
    return cnt.report(S.n, S)
