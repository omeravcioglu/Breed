"""Kit family: NATURE & YARD (trees, plants, fences, yard props). See docs/KIT_SPEC.md.

Conventions (KIT_SPEC): origin at ground level, bottom centre of the footprint, front faces -Y,
nothing below z = 0. Trees keep the origin at the trunk base (the palm's crown leans toward +X).
All crowns / bushes use the recolor placeholder ``M_Foliage`` (role "foliage"), so one tree can be
green, dark (pines), light, autumn or blossom per instance.

Pieces
  Trees  ("Trees")  : KIT_Tree_Round_A (6.45 m lollipop), KIT_Tree_Round_B (8 m, 7.3 m wide crown),
                      KIT_Tree_Cone (8 m pine, 4 wavy tiers), KIT_Tree_Small (4.2 m young street
                      tree with stakes + mulch ring), KIT_Tree_Palm (6.4 m zoo exotic, 10 fronds)
  Plants ("Plants") : KIT_Bush_A (1.2 m), KIT_Bush_B (2.0 m wide), KIT_Hedge_3m (3 x 0.9 x 1.1,
                      M_Hedge, tiles along X), KIT_Flowerbed_2m (2 x 1 timber bed, flowers),
                      KIT_Rock_A, KIT_Rock_B (natural scatter, filed under Plants)
  Fences ("Fences") : KIT_Fence_Picket_3m (1.0), KIT_Fence_Wood_3m (1.8 privacy, dog-ear boards),
                      KIT_Fence_Chain_3m (2.0, coarse closed lattice), KIT_Fence_Iron_3m (1.6 spear
                      bars on a 0.22 curb),
                      KIT_Gate_Picket (1.2 m, arched leaf, Z brace, hinges + latch)
  Yard   ("Yard")   : KIT_Lamp_Park (3.5 m lantern post, glow M_Light_Emit), KIT_PicnicTable,
                      KIT_Planter, KIT_Doghouse, KIT_Birdbath, KIT_Mailbox_House, KIT_Swing
  No extra pieces.

Fences, gate and hedge run along X with the thickness centred on y = 0 and span exactly
x in [-L/2, L/2]. Fences carry HALF a post at each end, cut flat on x = +-L/2: two neighbouring
pieces merge into one full post, so runs tile seamlessly on the 3 m grid and the 1.2 m picket
gate slots into a picket run the same way (its posts match the picket posts exactly). Rails stop
on the post cut planes (no end caps there), so an exposed run end shows a clean flat half post.
The chain-link diamond lattice and the hedge lumps are periodic, so they also continue across
seams. The chain-link lattice is coarse on purpose (1/3 m diamonds of closed 0.05 m square wires)
so it does not shimmer / moire at 20-60 m in Unity; the wire ends hide inside the rails and posts.

Backface-culling safe: every piece is closed or ends inside another closed part (polish pass:
closed chain-link wires, closed palm fronds, mailbox flag + door rim, capped Round_B trunk,
iron bars ending inside the spear heads).

Recolor roles used here: foliage (all crowns / bushes / flowerbed + planter greenery), trim
(planter rim + feet, mailbox post, doghouse trim), wall + roof + sign (doghouse body, roof,
name plate), awning (swing-set frame).

Shading: foliage, hedge, bark, rocks and the round lathe props are smooth shaded with angle-based sharp
edges (soft, rounded stylized read without extra geometry; rocks use a low 30 deg crease angle so
they stay chunky and faceted); boards, posts, fences and slabs stay flat shaded.
Meta on every piece: height (top z) and radius (max plan distance from the origin), measured from
the mesh; trees add crown_base (lowest foliage z = walk-under clearance), tiling pieces add tile
(run length along X), the park lamp adds light_z (centre of the glowing lantern).
"""
import math
import random

from mathutils import Matrix, Vector, geometry

from .. import facade as F
from ..geom2d import ensure_ccw
from ..meshutil import MeshBuilder

FAM = "nature"
TAU = 2.0 * math.pi
SQ2 = math.sqrt(2.0)

FOLIAGE = "M_Foliage"      # recolor: foliage
TRIM = "M_Trim_White"      # recolor: trim
WALL = "M_Wall_Cream"      # recolor: wall
ROOF = "M_Roof_Slate"      # recolor: roof
SIGN = "M_Sign_Accent"     # recolor: sign
AWNING = "M_Awning_Red"    # recolor: awning
BARK = "M_Bark"
HEDGE = "M_Hedge"


# =============================================================================== geometry helpers
def _v(x, y, z):
    return Vector((float(x), float(y), float(z)))


def _poly(mb, pts, mat, eps=1e-6):
    """mb.face() that drops repeated consecutive points (collapsed quads become triangles)."""
    out = []
    for p in pts:
        p = Vector(p)
        if not out or (p - out[-1]).length > eps:
            out.append(p)
    while len(out) > 1 and (out[0] - out[-1]).length <= eps:
        out.pop()
    if len(out) >= 3:
        mb.face(out, mat)


def lathe(mb, prof, mat, seg=8, cx=0.0, cy=0.0, phase=0.0, mats=None, wave=None):
    """Surface of revolution around a vertical axis.

    prof: [(r, z) | (r, z, ox, oy)] walked from the bottom/outside up and over to the top/inside;
    that order yields outward normals. r == 0 collapses onto the axis (caps / apexes).
    mats: optional per-band material list. wave: {ring_index: (dr_frac, dz)} alternating +/- per
    vertex (use an even seg) for wavy rims.
    """
    rings = []
    for i, p in enumerate(prof):
        r, z = p[0], p[1]
        ox, oy = (p[2], p[3]) if len(p) > 2 else (0.0, 0.0)
        row = []
        for j in range(seg):
            a = phase + TAU * j / seg
            rr, zz = r, z
            if wave and i in wave:
                s = 1.0 if j % 2 == 0 else -1.0
                rr, zz = r * (1.0 + wave[i][0] * s), z + wave[i][1] * s
            row.append(_v(cx + ox + rr * math.cos(a), cy + oy + rr * math.sin(a), zz))
        rings.append(row)
    for i in range(len(prof) - 1):
        m = mats[i] if mats else mat
        for j in range(seg):
            k = (j + 1) % seg
            _poly(mb, [rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]], m)


def blob(mb, c, r, mat, seg=10, rings=6, sz=1.0, sz_bot=None, jit=0.0, seed=0, floor=None,
         sx=1.0, sy=1.0):
    """Organic low-poly blob: UV sphere with seeded radial jitter, optional flatter underside
    (sz_bot) and an optional floor clamp (flat bottom at z = floor)."""
    rnd = random.Random(seed)
    ph0 = rnd.uniform(0.0, TAU)
    cx, cy, cz = c
    zb = sz if sz_bot is None else sz_bot
    rows = []
    for i in range(rings + 1):
        th = math.pi * i / rings
        st, ct = math.sin(th), math.cos(th)
        row = []
        for j in range(seg):
            ph = ph0 + TAU * j / seg
            k = 1.0 + (rnd.uniform(-jit, jit) if 0 < i < rings else 0.0)
            z = cz + r * (sz if ct >= 0 else zb) * ct * k
            if floor is not None:
                z = max(z, floor)
            row.append(_v(cx + r * sx * st * math.cos(ph) * k, cy + r * sy * st * math.sin(ph) * k, z))
        rows.append(row)
    for i in range(rings):
        for j in range(seg):
            k2 = (j + 1) % seg
            _poly(mb, [rows[i][j], rows[i + 1][j], rows[i + 1][k2], rows[i][k2]], mat)


def xz_prism(mb, pts, y0, y1, mat, side_mat=None, front=True, back=True, open_bottom=False):
    """Extrude an (x, z) profile along +Y from y0 (front face, looks -Y) to y1 (back, looks +Y)."""
    P = ensure_ccw([(float(p[0]), float(p[1])) for p in pts])
    if front or back:
        for t in geometry.tessellate_polygon([[Vector((x, z, 0.0)) for x, z in P]]):
            a, b, c = P[t[0]], P[t[1]], P[t[2]]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0:
                b, c = c, b
            if front:
                mb.face([_v(a[0], y0, a[1]), _v(b[0], y0, b[1]), _v(c[0], y0, c[1])], mat)
            if back:
                mb.face([_v(a[0], y1, a[1]), _v(c[0], y1, c[1]), _v(b[0], y1, b[1])], mat)
    zmin = min(p[1] for p in P)
    n = len(P)
    for i in range(n):
        p, q = P[i], P[(i + 1) % n]
        if open_bottom and abs(p[1] - zmin) < 1e-6 and abs(q[1] - zmin) < 1e-6:
            continue
        mb.face([_v(p[0], y0, p[1]), _v(p[0], y1, p[1]), _v(q[0], y1, q[1]), _v(q[0], y0, q[1])],
                side_mat or mat)


def x_loft(mb, sections, mat, cap0=True, cap1=True, open_bottom=True):
    """Loft (y, z) profiles along +X. sections: [(x, [(y, z), ...]), ...], x increasing, equal
    point counts, profiles CCW in (y, z) (= seen from +X)."""
    for (xa, A), (xb, B) in zip(sections, sections[1:]):
        n = len(A)
        for i in range(n):
            j = (i + 1) % n
            if open_bottom and A[i][1] < 1e-6 and A[j][1] < 1e-6:
                continue
            mb.face([_v(xa, *A[i]), _v(xa, *A[j]), _v(xb, *B[j]), _v(xb, *B[i])], mat)
    if cap1:
        x, S = sections[-1]
        mb.face([_v(x, y, z) for y, z in S], mat)
    if cap0:
        x, S = sections[0]
        mb.face([_v(x, y, z) for y, z in reversed(S)], mat)


def chamfer_rect(cx, cy, w, d, c=0.0):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    if c <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
            (x0, y1 - c), (x0, y0 + c)]


def circle(cx, cy, r, seg, phase=0.0):
    return [(cx + r * math.cos(phase + TAU * i / seg), cy + r * math.sin(phase + TAU * i / seg))
            for i in range(seg)]


def clip_half(poly, axis, c, keep):
    """Sutherland-Hodgman clip of a 2D polygon against coord[axis] >= c (keep=+1) / <= c (-1)."""
    if keep is None:
        return list(poly)
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp, dq = keep * (p[axis] - c), keep * (q[axis] - c)
        if dp >= -1e-9:
            out.append((p[0], p[1]))
        if (dp > 1e-9 and dq < -1e-9) or (dp < -1e-9 and dq > 1e-9):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    res = []
    for p in out:
        if not res or abs(p[0] - res[-1][0]) + abs(p[1] - res[-1][1]) > 1e-7:
            res.append(p)
    while len(res) > 1 and abs(res[0][0] - res[-1][0]) + abs(res[0][1] - res[-1][1]) <= 1e-7:
        res.pop()
    return res


def post(mb, poly, z0, z1, mat, apex=None, cap_h=0.0, top=True, cap_mat=None):
    """Vertical prism from a 2D footprint (no bottom) with a flat top or a pyramid cap whose apex
    sits at *apex* (x, y). A footprint clipped on the apex line gives a valid HALF post: the cap
    triangles over the cut edge close the cut face."""
    P = ensure_ccw(list(poly))
    mb.wall(P, z0, z1, mat, closed=True)
    if cap_h > 0:
        A = _v(apex[0], apex[1], z1 + cap_h)
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            _poly(mb, [_v(a[0], a[1], z1), _v(b[0], b[1], z1), A], cap_mat or mat)
    elif top:
        mb.tri_fill([P], z1, cap_mat or mat, up=True)


def plate(mb, poly, z0, z1, mat):
    """Closed flat slab from a 2D footprint (top, bottom, sides)."""
    P = ensure_ccw(list(poly))
    mb.wall(P, z0, z1, mat, closed=True)
    mb.tri_fill([P], z1, mat, up=True)
    mb.tri_fill([P], z0, mat, up=False)


def fence_post(mb, x, w, z1, mat, cap_h, chamfer=0.012, keep=None, plate_w=0.0, plate_h=0.0, z0=0.0):
    """Square fence post centred on (x, 0); keep=+1/-1 builds only the half with x >= / <= x."""
    body = clip_half(chamfer_rect(x, 0.0, w, w, chamfer), 0, x, keep)
    if plate_w <= 0:
        post(mb, body, z0, z1, mat, apex=(x, 0.0), cap_h=cap_h)
        return
    # post body, then a wider cap plate, then the pyramid on the plate
    post(mb, body, z0, z1, mat, top=False)
    pl = clip_half(chamfer_rect(x, 0.0, plate_w, plate_w, chamfer), 0, x, keep)
    mb.tri_fill([ensure_ccw(pl)], z1, mat, up=False)
    post(mb, pl, z1, z1 + plate_h, mat, apex=(x, 0.0), cap_h=cap_h)


def tube(mb, p0, p1, r, mat, seg=8, cap0=False, cap1=True, r1=None, phase=0.0):
    """Cylinder between two 3D points."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    sub = MeshBuilder()
    sub.cylinder(0.0, 0.0, 0.0, d.length, r, mat, seg=seg, cap_top=cap1, cap_bottom=cap0, r_top=r1)
    if phase:
        sub.transform(Matrix.Rotation(phase, 4, "Z"))
    M = Matrix.Translation(p0) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    mb.extend(sub, M)


def rbox(mb, center, size, mat, rot=None, skip=(), bevel=0.0):
    """Box of *size* centred at *center*, optionally rotated (3x3 / 4x4 matrix) and chamfered."""
    sx, sy, sz = size
    sub = MeshBuilder()
    sub.box(-sx / 2, -sy / 2, -sz / 2, sx / 2, sy / 2, sz / 2, mat, skip=skip)
    if bevel > 0:
        sub = F.bevelled(sub, bevel)
    M = Matrix.Translation(Vector(center))
    if rot is not None:
        M = M @ (rot.to_4x4() if len(rot) == 3 else rot)
    mb.extend(sub, M)


def bbox(mb, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, skip=()):
    """Axis-aligned box, optionally chamfered (soft stylized edge)."""
    sub = MeshBuilder()
    sub.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
    if bevel > 0:
        sub = F.bevelled(sub, bevel)
    mb.extend(sub)


def beam(mb, a, b, w, t, mat, up=(0.0, 0.0, 1.0), bevel=0.0, skip=()):
    """Rectangular beam from point a to b: width w across, thickness t along the 'up' side."""
    a, b = Vector(a), Vector(b)
    d = (b - a)
    L = d.length
    x = d.normalized()
    u = Vector(up)
    y = u.cross(x)
    if y.length < 1e-6:
        y = Vector((0.0, 1.0, 0.0)).cross(x)
    y.normalize()
    z = x.cross(y)
    R = Matrix((x, y, z)).transposed()
    rbox(mb, (a + b) / 2, (L, w, t), mat, rot=R, skip=skip, bevel=bevel)


def gem(mb, c, r, h, mat, seg=5, phase=0.0):
    """Small bipyramid (flower head / berry): 2*seg triangles."""
    lathe(mb, [(0.0, c[2] - h), (r, c[2]), (0.0, c[2] + h)], mat, seg=seg, cx=c[0], cy=c[1], phase=phase)


def floor_clamp(mb, z=0.0):
    """Clamp every vertex to z >= z (keeps slanted legs from poking under the ground)."""
    for v in mb.verts:
        if v.z < z:
            v.z = z


def _center_y(mb):
    """Translate the builder so its footprint is centred on y = 0."""
    ys = [v.y for v in mb.verts]
    dy = -(min(ys) + max(ys)) / 2.0
    mb.transform(Matrix.Translation((0.0, dy, 0.0)))


def sq(a):
    """Lathe radius of a square (seg=4, phase 45 deg) with half-width a."""
    return a * SQ2


# =============================================================================== registration
def _shade(o, smooth_mats, angle=48.0):
    """Smooth-shade faces using *smooth_mats*; edges sharper than *angle* stay crisp."""
    me = o.data
    names = [m.name for m in me.materials]
    flags = [names[p.material_index] in smooth_mats for p in me.polygons]
    if not any(flags):
        return
    me.set_sharp_from_angle(angle=math.radians(angle))   # note: also marks every face smooth
    me.polygons.foreach_set("use_smooth", flags)          # so restore flat faces afterwards
    me.update()


def _add(K, name, mb, cat, meta=None, smooth=(), angle=48.0):
    """Register a piece; meta gets measured height (top z) and radius (max distance from the
    origin in plan) so placers can space / collide pieces without reading the mesh."""
    m = dict(meta or {})
    m["height"] = round(max(v.z for v in mb.verts), 2)
    m["radius"] = round(max(math.hypot(v.x, v.y) for v in mb.verts), 2)
    if cat == "Trees":      # lowest foliage point = clearance under the crown
        fi = mb.mats.index(FOLIAGE)
        m["crown_base"] = round(min(mb.verts[i].z for f, mi in zip(mb.faces, mb.fmat) if mi == fi for i in f), 2)
    o = K.add(name, mb, FAM, cat, meta=m)
    if smooth:
        _shade(o, set(smooth), angle)
    return o


# =============================================================================== trees
def _trunk(mb, h, r0, r1, seg=8, flare=1.4, lean=(0.0, 0.0), phase=0.0, cap=False):
    """Tapered trunk with a root flare; top left open when it ends inside the crown, capped with a
    low cone when *cap* (the top shows under a high crown)."""
    lx, ly = lean
    prof = [(r0 * flare, 0.0, 0.0, 0.0), (r0, 0.32, 0.0, 0.0),
            (r0 * 0.6 + r1 * 0.4, h * 0.55, lx * 0.4, ly * 0.4), (r1, h, lx, ly)]
    if cap:
        prof.append((0.0, h + r1 * 0.5, lx, ly))
    lathe(mb, prof, BARK, seg=seg, phase=phase)


def tree_round_a(K):
    mb = MeshBuilder()
    _trunk(mb, 3.6, 0.19, 0.12, seg=8)
    tube(mb, (0.0, 0.0, 2.4), (0.9, -0.3, 3.5), 0.075, BARK, seg=6, r1=0.05)
    tube(mb, (0.0, 0.0, 2.7), (-0.85, 0.4, 3.7), 0.07, BARK, seg=6, r1=0.05)
    blob(mb, (0.0, 0.0, 4.35), 1.75, FOLIAGE, seg=10, rings=6, sz=0.9, sz_bot=0.72, jit=0.05, seed=11)
    blob(mb, (-0.2, 0.2, 5.45), 1.05, FOLIAGE, seg=10, rings=6, sz=0.95, sz_bot=0.8, jit=0.05, seed=12)
    blob(mb, (1.2, -0.35, 3.8), 0.95, FOLIAGE, seg=9, rings=6, sz=0.9, sz_bot=0.75, jit=0.05, seed=13)
    blob(mb, (-1.15, 0.4, 3.95), 0.9, FOLIAGE, seg=9, rings=6, sz=0.9, sz_bot=0.75, jit=0.05, seed=14)
    _add(K, "KIT_Tree_Round_A", mb, "Trees", None,
         smooth=(FOLIAGE, BARK), angle=50)


def tree_round_b(K):
    mb = MeshBuilder()
    _trunk(mb, 3.4, 0.28, 0.19, seg=9, flare=1.45, cap=True)   # top shows below the 3.98 m crown base
    tube(mb, (0.0, 0.0, 2.5), (1.6, 0.27, 4.75), 0.13, BARK, seg=7, r1=0.08)
    tube(mb, (0.0, 0.0, 2.7), (-1.55, -0.3, 4.55), 0.12, BARK, seg=7, r1=0.08)
    tube(mb, (0.0, 0.0, 3.0), (0.2, 0.75, 5.1), 0.11, BARK, seg=7, r1=0.07)
    blob(mb, (0.0, 0.15, 5.55), 2.25, FOLIAGE, seg=10, rings=6, sz=0.85, sz_bot=0.7, jit=0.05, seed=21)
    blob(mb, (-2.0, -0.2, 4.75), 1.6, FOLIAGE, seg=10, rings=6, sz=0.88, sz_bot=0.72, jit=0.05, seed=22)
    blob(mb, (2.05, 0.3, 4.9), 1.65, FOLIAGE, seg=10, rings=6, sz=0.88, sz_bot=0.72, jit=0.05, seed=23)
    blob(mb, (0.45, -1.35, 4.5), 1.35, FOLIAGE, seg=9, rings=6, sz=0.88, sz_bot=0.72, jit=0.05, seed=24)
    blob(mb, (0.35, 0.25, 7.05), 1.05, FOLIAGE, seg=9, rings=6, sz=0.9, sz_bot=0.8, jit=0.05, seed=25)
    _add(K, "KIT_Tree_Round_B", mb, "Trees", None,
         smooth=(FOLIAGE, BARK), angle=50)


def tree_cone(K):
    mb = MeshBuilder()
    _trunk(mb, 1.9, 0.2, 0.14, seg=8, flare=1.35)
    tiers = [(0.85, 2.05, 3.1), (2.35, 1.7, 2.9), (3.85, 1.3, 2.7), (5.3, 0.88, 2.7)]
    for i, (z0, R, h) in enumerate(tiers):
        prof = [(0.0, z0 + 0.42), (R, z0), (R * 0.6, z0 + h * 0.36), (R * 0.24, z0 + h * 0.74), (0.0, z0 + h)]
        lathe(mb, prof, FOLIAGE, seg=12, phase=i * 0.37, wave={1: (0.06, 0.07)})
    _add(K, "KIT_Tree_Cone", mb, "Trees", None,
         smooth=(FOLIAGE, BARK), angle=55)


def tree_small(K):
    mb = MeshBuilder()
    # mulch ring (reads as a tree pit on pavement, mulch on grass)
    lathe(mb, [(0.55, 0.0), (0.5, 0.045), (0.0, 0.045)], "M_Dirt", seg=10)
    _trunk(mb, 2.5, 0.085, 0.065, seg=7, flare=1.3)
    blob(mb, (0.0, 0.0, 2.8), 0.95, FOLIAGE, seg=10, rings=6, sz=0.95, sz_bot=0.78, jit=0.05, seed=31)
    blob(mb, (0.18, -0.08, 3.62), 0.58, FOLIAGE, seg=9, rings=5, sz=0.95, sz_bot=0.8, jit=0.05, seed=32)
    # two support stakes with a strap
    for sx in (-0.3, 0.3):
        bbox(mb, sx - 0.03, -0.03, 0.0, sx + 0.03, 0.03, 1.55, "M_Wood_Light", skip=("-z",))
    bbox(mb, -0.33, -0.025, 1.22, 0.33, 0.025, 1.3, "M_Trim_Dark")
    _add(K, "KIT_Tree_Small", mb, "Trees", None,
         smooth=(FOLIAGE, BARK), angle=50)


def _frond(mb, top, a, L, W, lift, droop, n=5):
    """Palm frond: arched spine rising then drooping, edges lower than the spine. Closed thin lens:
    the top and under surfaces share the leaf edges and only the under spine sits 3 cm lower, so
    the leaf is watertight (no open rim at grazing angles with backface culling), same tri count."""
    up = Vector((0.0, 0.0, 1.0))
    d = Vector((math.cos(a), math.sin(a), 0.0))
    left = up.cross(d)
    S, Lf, Rt = [], [], []
    for k in range(n + 1):
        t = k / n
        p = top + d * (L * t + 0.05) + up * (L * (lift * t - droop * t * t) + 0.12)
        w = W * math.sin(math.pi * min(1.0, t ** 0.75))
        S.append(p)
        Lf.append(p + left * w - up * 0.4 * w)
        Rt.append(p - left * w - up * 0.4 * w)
    dn = up * -0.03
    for k in range(n):
        _poly(mb, [S[k], S[k + 1], Lf[k + 1], Lf[k]], FOLIAGE)
        _poly(mb, [Rt[k], Rt[k + 1], S[k + 1], S[k]], FOLIAGE)
        _poly(mb, [Lf[k], Lf[k + 1], S[k + 1] + dn, S[k] + dn], FOLIAGE)
        _poly(mb, [S[k] + dn, S[k + 1] + dn, Rt[k + 1], Rt[k]], FOLIAGE)


def tree_palm(K):
    mb = MeshBuilder()
    H = 5.6
    # stacked-segment trunk, curving gently toward +X
    nseg = 6
    prof = []
    for k in range(nseg):
        t0, t1 = k / nseg, (k + 1) / nseg
        z0, z1 = H * t0, H * t1
        rb = 0.2 - 0.07 * t0
        rt = 0.2 - 0.07 * t1
        o0 = 0.9 * t0 ** 2
        if k == 0:
            prof.append((rb * 1.35, 0.0, 0.0, 0.0))
        else:
            prof.append((rb * 0.92, z0 + 0.02, o0, 0.0))
        prof.append((rt * 1.18, z1 - 0.07, 0.9 * ((z1 - 0.07) / H) ** 2, 0.0))
    prof.append((0.0, H, 0.9, 0.0))
    lathe(mb, prof, BARK, seg=7)
    top = Vector((0.9, 0.0, H))
    blob(mb, (top.x, top.y, top.z + 0.05), 0.28, FOLIAGE, seg=7, rings=4, sz=0.9, seed=41)
    # coconuts
    for i, a in enumerate((0.4, 2.5, 4.4)):
        blob(mb, (top.x + 0.22 * math.cos(a), top.y + 0.22 * math.sin(a), top.z - 0.22), 0.13,
             "M_Trim_Wood", seg=6, rings=4, seed=45 + i)
    # fronds: arched, drooping, double-sided leaves with a raised spine
    rnd = random.Random(7)
    for f in range(6):          # lower ring: long, drooping
        a = TAU * f / 6 + rnd.uniform(-0.15, 0.15)
        _frond(mb, top, a, rnd.uniform(2.4, 2.8), 0.46, rnd.uniform(0.35, 0.5), 0.85)
    for f in range(4):          # upper ring: shorter, rising (fuller, livelier crown)
        a = TAU * f / 4 + 0.5 + rnd.uniform(-0.15, 0.15)
        _frond(mb, top + Vector((0.0, 0.0, 0.05)), a, rnd.uniform(1.8, 2.1), 0.4, rnd.uniform(0.95, 1.1), 0.9)
    _add(K, "KIT_Tree_Palm", mb, "Trees", None,
         smooth=(FOLIAGE, BARK, "M_Trim_Wood"), angle=50)


# =============================================================================== plants
def bush_a(K):
    mb = MeshBuilder()
    blob(mb, (0.0, 0.05, 0.5), 0.55, FOLIAGE, seg=9, rings=5, sz=0.95, jit=0.06, seed=51, floor=0.0)
    blob(mb, (0.26, -0.12, 0.33), 0.37, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=52, floor=0.0)
    blob(mb, (-0.24, -0.06, 0.35), 0.38, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=53, floor=0.0)
    _add(K, "KIT_Bush_A", mb, "Plants", None, smooth=(FOLIAGE,), angle=55)


def bush_b(K):
    mb = MeshBuilder()
    blob(mb, (0.0, 0.1, 0.62), 0.7, FOLIAGE, seg=9, rings=5, sz=0.92, jit=0.06, seed=61, floor=0.0)
    blob(mb, (-0.52, -0.05, 0.45), 0.5, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=62, floor=0.0)
    blob(mb, (0.5, 0.12, 0.48), 0.48, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=63, floor=0.0)
    blob(mb, (0.22, -0.42, 0.34), 0.42, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=64, floor=0.0)
    blob(mb, (-0.25, 0.48, 0.4), 0.42, FOLIAGE, seg=8, rings=5, sz=0.95, jit=0.06, seed=65, floor=0.0)
    _add(K, "KIT_Bush_B", mb, "Plants", None, smooth=(FOLIAGE,), angle=55)


def hedge_3m(K):
    """3 x 0.9 x 1.1 box hedge lofted along X with gentle lumps; end profiles are identical so
    runs tile seamlessly."""
    mb = MeshBuilder()

    def prof(s, h):
        hw = 0.45 * s
        return [(-hw, 0.0), (hw, 0.0), (hw, h - 0.24), (hw - 0.07, h - 0.07), (hw - 0.2, h),
                (-hw + 0.2, h), (-hw + 0.07, h - 0.07), (-hw, h - 0.24)]
    secs = [(-1.5, prof(0.94, 1.06))]
    n = 12
    for i in range(n + 1):
        x = -1.44 + 2.88 * i / n
        bump = 0.5 - 0.5 * math.cos(TAU * 3.0 * i / n)     # 3 soft lumps, 0 at both ends
        secs.append((x, prof(0.94 + 0.06 * bump, 1.06 + 0.04 * bump)))
    secs.append((1.5, prof(0.94, 1.06)))
    x_loft(mb, secs, HEDGE)
    _add(K, "KIT_Hedge_3m", mb, "Plants", dict(tile=3.0), smooth=(HEDGE,), angle=50)


def flowerbed_2m(K):
    mb = MeshBuilder()
    outer = chamfer_rect(0.0, 0.0, 2.0, 1.0, 0.14)
    inner = chamfer_rect(0.0, 0.0, 1.78, 0.78, 0.08)
    # timber edging ring
    O, I = ensure_ccw(outer), ensure_ccw(inner)
    mb.wall(O, 0.0, 0.2, "M_Wood_Light", closed=True)
    mb.wall(list(reversed(I)), 0.14, 0.2, "M_Wood_Light", closed=True)
    mb.tri_fill([O, I], 0.2, "M_Wood_Light", up=True)
    mb.tri_fill([I], 0.14, "M_Dirt", up=True)
    rnd = random.Random(77)
    clumps = [(-0.62, -0.12, 0.25), (-0.18, 0.15, 0.27), (0.28, -0.1, 0.26), (0.62, 0.12, 0.24),
              (-0.45, 0.2, 0.2), (0.05, -0.18, 0.2), (0.48, 0.2, 0.19)]
    colors = ["M_Foliage_Blossom", "M_Awning_Yellow", "M_Foliage_Blossom", "M_Wall_Lavender",
              "M_Awning_Yellow", "M_Foliage_Blossom", "M_Wall_Lavender"]
    for i, (x, y, r) in enumerate(clumps):
        blob(mb, (x, y, 0.14 + r * 0.45), r, FOLIAGE, seg=6, rings=4, sz=0.85, jit=0.07, seed=80 + i,
             floor=0.14)
        for k in range(2):
            a = rnd.uniform(0, TAU)
            rr = r * rnd.uniform(0.25, 0.55)
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            dz = math.sqrt(max(0.0, r * r - rr * rr)) * 0.85
            gem(mb, (px, py, 0.14 + r * 0.45 + dz + 0.02), 0.075, 0.05, colors[(i + k) % len(colors)],
                seg=4, phase=a)
    _add(K, "KIT_Flowerbed_2m", mb, "Plants", None, smooth=(FOLIAGE,), angle=75)


def _rock(mb, c, r, seed, sx=1.0, sy=0.85, sz=0.7):
    blob(mb, c, r, "M_Rock", seg=7, rings=5, sz=sz, jit=0.14, seed=seed, floor=0.0, sx=sx, sy=sy)


def rock_a(K):
    mb = MeshBuilder()
    _rock(mb, (0.0, 0.0, 0.2), 0.55, 91, sx=1.0, sy=0.82, sz=0.75)
    _add(K, "KIT_Rock_A", mb, "Plants", None, smooth=("M_Rock",), angle=30)


def rock_b(K):
    mb = MeshBuilder()
    _rock(mb, (-0.2, 0.08, 0.32), 0.82, 95, sx=1.0, sy=0.85, sz=0.72)
    _rock(mb, (0.78, -0.3, 0.12), 0.42, 96, sx=1.1, sy=0.9, sz=0.75)
    _add(K, "KIT_Rock_B", mb, "Plants", None, smooth=("M_Rock",), angle=30)


# =============================================================================== fences
def _end_posts(mb, half_len, w, z1, mat, cap_h, chamfer=0.012, **kw):
    fence_post(mb, -half_len, w, z1, mat, cap_h, chamfer, keep=+1, **kw)
    fence_post(mb, half_len, w, z1, mat, cap_h, chamfer, keep=-1, **kw)


def _pickets(mb, x0, x1, n, w, ztop_fn, mat, y0=-0.045, y1=0.0, zb=0.07, tip=0.09):
    pitch = (x1 - x0) / n
    for i in range(n):
        xc = x0 + pitch * (i + 0.5)
        zs = ztop_fn(xc)
        a, b = xc - w / 2, xc + w / 2
        xz_prism(mb, [(a, zb), (b, zb), (b, zs), (xc, zs + tip), (a, zs)], y0, y1, mat, open_bottom=True)


def fence_picket(K):
    mb = MeshBuilder()
    L, PW = 3.0, 0.1
    m = "M_Fence_White"
    _end_posts(mb, L / 2, PW, 0.92, m, 0.08)
    for z0, z1 in ((0.2, 0.28), (0.66, 0.74)):
        bbox(mb, -L / 2, 0.0, z0, L / 2, 0.045, z1, m, skip=("-x", "+x"))
    _pickets(mb, -L / 2 + PW / 2, L / 2 - PW / 2, 16, 0.085, lambda x: 0.84, m)
    _add(K, "KIT_Fence_Picket_3m", mb, "Fences", dict(tile=3.0))


def gate_picket(K):
    mb = MeshBuilder()
    L, PW = 1.2, 0.1
    m = "M_Fence_White"
    _end_posts(mb, L / 2, PW, 0.92, m, 0.08)
    lx0, lx1 = -L / 2 + PW / 2 + 0.025, L / 2 - PW / 2 - 0.025
    for z0, z1 in ((0.2, 0.28), (0.66, 0.74)):
        bbox(mb, lx0, 0.0, z0, lx1, 0.045, z1, m)
    # Z brace between the rails (hinge side low -> latch side high)
    beam(mb, (lx0 + 0.07, 0.0225, 0.27), (lx1 - 0.07, 0.0225, 0.67), 0.075, 0.04, m, up=(0.0, -1.0, 0.0))
    span = (lx1 - lx0) / 2
    _pickets(mb, lx0, lx1, 6, 0.085, lambda x: 0.78 + 0.08 * (1.0 - (x / span) ** 2), m)
    # hinges + latch
    for z in (0.24, 0.7):
        bbox(mb, -L / 2 + 0.03, -0.01, z - 0.03, lx0 + 0.06, 0.055, z + 0.03, "M_Metal_Dark")
    bbox(mb, lx1 - 0.05, -0.085, 0.56, lx1 + 0.02, -0.045, 0.6, "M_Metal_Dark")
    _add(K, "KIT_Gate_Picket", mb, "Fences", dict(tile=1.2))


def fence_wood(K):
    mb = MeshBuilder()
    L, PW = 3.0, 0.12
    m = "M_Fence_Wood"
    _end_posts(mb, L / 2, PW, 1.72, m, 0.08, chamfer=0.015)
    for z0, z1 in ((0.28, 0.38), (1.3, 1.4)):
        bbox(mb, -L / 2, -0.01, z0, L / 2, 0.05, z1, m, skip=("-x", "+x"))
    x0, x1 = -L / 2 + PW / 2, L / 2 - PW / 2
    n = 14
    pitch = (x1 - x0) / n
    w, e = pitch - 0.016, 0.05
    for i in range(n):
        a = x0 + pitch * i + 0.008
        b = a + w
        top = 1.7 - (0.02 if i % 2 else 0.0)
        xz_prism(mb, [(a, 0.05), (b, 0.05), (b, top - e), (b - e, top), (a + e, top), (a, top - e)],
                 -0.05, -0.01, m, open_bottom=True)
    _add(K, "KIT_Fence_Wood_3m", mb, "Fences", dict(tile=3.0))


def _lattice(mb, x0, x1, z0, z1, pitch, wire, mat, layers, phases=(0.25, 0.7), min_area=2e-4):
    """Chain-link lattice of CLOSED square-section wires: two families of 45 deg bars (+ rising to
    +X in the front layer, - falling in the back layer), periodic in x with *pitch* (anchored at
    x0, pitch divides the tile) so the diamonds continue across tiled pieces.

    Each bar = front face + back face + its two long side faces. The cut ends are left open on
    purpose: the bars stop on the rail centre lines (z0 / z1) inside the closed rails and on the
    half-post cut planes (x0 / x1), which cover them. *layers* = ((ya, yb) front, (ya, yb) back).
    *phases* keep every bar clear of the panel corners (no slivers / pentagons)."""
    E = 1e-7
    hw = wire / 2 * SQ2          # horizontal half-width of a 45 deg bar
    H = z1 - z0

    def border(p, q):
        return any(abs(p[a] - c) < 1e-6 and abs(q[a] - c) < 1e-6 for a, c in ((0, x0), (0, x1), (1, z0), (1, z1)))

    for fam, (ya, yb), ph in ((+1, layers[0], phases[0]), (-1, layers[1], phases[1])):
        k0 = int(math.floor(-H / pitch)) - 2
        k1 = int(math.ceil((x1 - x0 + H) / pitch)) + 2
        for k in range(k0, k1 + 1):
            c = x0 + (k + ph) * pitch
            zA, zB = z0 - 1.0, z1 + 1.0          # bar around the line x = c + fam * (z - z0)
            xa, xb = c + fam * (zA - z0), c + fam * (zB - z0)
            poly = [(xa - hw, zA), (xa + hw, zA), (xb + hw, zB), (xb - hw, zB)]
            for axis, cc, keep in ((0, x0, +1), (0, x1, -1), (1, z0, +1), (1, z1, -1)):
                poly = clip_half(poly, axis, cc, keep)
                if len(poly) < 3:
                    break
            if len(poly) < 3:
                continue
            area = 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                                 for i in range(len(poly))))
            if area < min_area:
                continue
            P = ensure_ccw(poly)
            mb.face([_v(x, ya, z) for x, z in P], mat)                 # front (-Y)
            mb.face([_v(x, yb, z) for x, z in reversed(P)], mat)       # back (+Y)
            n = len(P)
            for i in range(n):
                p, q = P[i], P[(i + 1) % n]
                if border(p, q) or (abs(p[0] - q[0]) + abs(p[1] - q[1])) < E:
                    continue
                mb.face([_v(p[0], ya, p[1]), _v(p[0], yb, p[1]), _v(q[0], yb, q[1]), _v(q[0], ya, q[1])], mat)


def _hex_rail(mb, x0, x1, zc, r, mat):
    """Closed-section hexagonal rail along X (open ends sit on the half-post cut planes).
    Vertices point to +-Y so the rail is r wide at its centre line (hides the lattice bar ends)."""
    prof = [(r * math.cos(TAU * i / 6), zc + r * math.sin(TAU * i / 6)) for i in range(6)]
    x_loft(mb, [(x0, prof), (x1, prof)], mat, cap0=False, cap1=False, open_bottom=False)


def fence_chain(K):
    """2.0 m chain-link. Coarse closed lattice (polish pass): 1/3 m diamonds of 0.05 m square
    wires (front family y -0.035..0.015, back family -0.015..0.035), between hexagonal rails
    (r 0.042) on R 0.05 half posts. Reads as mesh at 20-60 m without moire; ~284 tris."""
    mb = MeshBuilder()
    L, R = 3.0, 0.05
    m = "M_Metal"
    zb, zt = 0.08, 1.88                          # rail centre lines = lattice bar ends
    for x, keep in ((-L / 2, +1), (L / 2, -1)):
        half = clip_half(circle(x, 0.0, R, 8, phase=math.pi / 8), 0, x, keep)
        post(mb, half, 0.0, 1.95, m, apex=(x, 0.0), cap_h=0.05)
    _hex_rail(mb, -L / 2, L / 2, zt, 0.042, m)
    _hex_rail(mb, -L / 2, L / 2, zb, 0.042, m)
    _lattice(mb, -L / 2, L / 2, zb, zt, L / 9, 0.05, m, ((-0.035, 0.015), (-0.015, 0.035)))
    _add(K, "KIT_Fence_Chain_3m", mb, "Fences", dict(tile=3.0))


def fence_iron(K):
    mb = MeshBuilder()
    L, PW = 3.0, 0.12
    m = "M_Metal_Dark"
    # low concrete curb, chamfered, lofted so the cut ends tile flush
    curb = [(-0.13, 0.0), (0.13, 0.0), (0.13, 0.17), (0.095, 0.22), (-0.095, 0.22), (-0.13, 0.17)]
    x_loft(mb, [(-L / 2, curb), (L / 2, curb)], "M_Wall_Concrete")
    _end_posts(mb, L / 2, PW, 1.44, m, 0.12, chamfer=0.012, plate_w=0.16, plate_h=0.04, z0=0.22)
    for z0, z1 in ((0.3, 0.36), (1.1, 1.15), (1.26, 1.31)):
        bbox(mb, -L / 2, -0.025, z0, L / 2, 0.025, z1, m, skip=("-x", "+x"))
    x0, x1 = -L / 2 + PW / 2, L / 2 - PW / 2
    n = 18
    pitch = (x1 - x0) / n
    for i in range(n):
        xc = x0 + pitch * (i + 0.5)
        # open-ended bar: its top must end where the spear is wider than the bar (z >= 1.41)
        bbox(mb, xc - 0.02, -0.02, 0.22, xc + 0.02, 0.02, 1.43, m, skip=("-z", "+z"))
        lathe(mb, [(0.0, 1.37), (sq(0.042), 1.45), (0.0, 1.56)], m, seg=4, cx=xc, phase=math.pi / 4)
    _add(K, "KIT_Fence_Iron_3m", mb, "Fences", dict(tile=3.0))


# =============================================================================== yard
def lamp_park(K):
    mb = MeshBuilder()
    m = "M_Metal_Dark"
    lathe(mb, [(0.17, 0.0), (0.17, 0.2), (0.13, 0.26), (0.075, 0.34), (0.055, 0.44), (0.05, 2.7),
               (0.085, 2.74), (0.085, 2.82), (0.12, 2.86), (0.0, 2.86)], m, seg=8, phase=math.pi / 8)
    # lantern: tray, glowing body, corner posts, pyramid roof, finial
    plate(mb, chamfer_rect(0.0, 0.0, 0.32, 0.32, 0.02), 2.86, 2.9, m)
    bbox(mb, -0.12, -0.12, 2.9, 0.12, 0.12, 3.22, "M_Light_Emit", skip=("-z", "+z"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            bbox(mb, sx * 0.12 - 0.025, sy * 0.12 - 0.025, 2.9, sx * 0.12 + 0.025, sy * 0.12 + 0.025, 3.22, m,
                 skip=("-z", "+z"))
    lathe(mb, [(0.0, 3.22), (sq(0.15), 3.22), (sq(0.2), 3.26), (sq(0.2), 3.3), (sq(0.05), 3.43), (0.0, 3.43)], m,
          seg=4, phase=math.pi / 4)
    blob(mb, (0.0, 0.0, 3.46), 0.045, m, seg=6, rings=4)
    _add(K, "KIT_Lamp_Park", mb, "Yard", dict(light_z=3.06), smooth=(m,), angle=50)


def picnic_table(K):
    mb = MeshBuilder()
    top, frame = "M_Wood_Light", "M_Fence_Wood"
    for y in (-0.26, 0.0, 0.26):
        bbox(mb, -0.9, y - 0.12, 0.72, 0.9, y + 0.12, 0.77, top, bevel=0.015)
    for y in (-0.68, 0.68):
        bbox(mb, -0.85, y - 0.13, 0.42, 0.85, y + 0.13, 0.47, top, bevel=0.015)
    legs = MeshBuilder()
    for x in (-0.62, 0.62):
        for s in (-1, 1):
            beam(legs, (x, s * 0.6, -0.05), (x, s * 0.2, 0.74), 0.1, 0.07, frame, up=(1.0, 0.0, 0.0))
        bbox(legs, x - 0.035, -0.82, 0.35, x + 0.035, 0.82, 0.42, frame)
        bbox(legs, x - 0.035, -0.36, 0.65, x + 0.035, 0.36, 0.72, frame)
    floor_clamp(legs, 0.0)
    mb.extend(legs)
    _add(K, "KIT_PicnicTable", mb, "Yard")


def planter(K):
    mb = MeshBuilder()
    wood = "M_Fence_Wood"
    lathe(mb, [(0.0, 0.05), (sq(0.34), 0.05), (sq(0.38), 0.46), (sq(0.33), 0.46), (sq(0.325), 0.4), (0.0, 0.4)],
          wood, seg=4, phase=math.pi / 4, mats=[wood, wood, wood, wood, "M_Dirt"])
    # chunky rim cap (recolor: trim)
    lathe(mb, [(sq(0.36), 0.43), (sq(0.42), 0.43), (sq(0.42), 0.5), (sq(0.31), 0.5), (sq(0.31), 0.45)],
          TRIM, seg=4, phase=math.pi / 4)
    # little feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            bbox(mb, sx * 0.3 - 0.06, sy * 0.3 - 0.06, 0.0, sx * 0.3 + 0.06, sy * 0.3 + 0.06, 0.05, TRIM,
                 skip=("-z",))
    blob(mb, (0.0, 0.02, 0.78), 0.42, FOLIAGE, seg=9, rings=5, sz=0.95, sz_bot=0.8, jit=0.06, seed=101)
    blob(mb, (0.2, -0.15, 0.65), 0.3, FOLIAGE, seg=8, rings=5, jit=0.06, seed=102)
    blob(mb, (-0.22, -0.1, 0.66), 0.3, FOLIAGE, seg=8, rings=5, jit=0.06, seed=103)
    _add(K, "KIT_Planter", mb, "Yard", None, smooth=(FOLIAGE,), angle=55)


def doghouse(K):
    mb = MeshBuilder()
    W, D, Z0, ZE, ZR = 0.9, 1.1, 0.08, 0.68, 1.04
    hx, hy = W / 2, D / 2
    # base deck
    bbox(mb, -hx - 0.06, -hy - 0.06, 0.0, hx + 0.06, hy + 0.06, Z0, "M_Trim_Wood", bevel=0.015)
    # body: front gable with arched door, back gable, side walls
    house = [(-hx, Z0), (hx, Z0), (hx, ZE), (0.0, ZR), (-hx, ZE)]
    dr, dz0, dzs = 0.2, 0.11, 0.42
    hole = ensure_ccw([(-dr, dz0), (dr, dz0)] + [(dr * math.cos(math.pi * k / 6), dzs + dr * math.sin(math.pi * k / 6))
                                                 for k in range(0, 7)])
    # front face with hole (normal -Y)
    loops = [[Vector((x, z, 0.0)) for x, z in house], [Vector((x, z, 0.0)) for x, z in hole]]
    flat = [p for lp in loops for p in lp]
    for t in geometry.tessellate_polygon(loops):
        a, b, c = flat[t[0]], flat[t[1]], flat[t[2]]
        if (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) < 0:
            b, c = c, b
        mb.face([_v(a.x, -hy, a.y), _v(b.x, -hy, b.y), _v(c.x, -hy, c.y)], WALL)
    # back gable (normal +Y) and side walls
    xz_prism(mb, house, -hy, hy, WALL, front=False, back=True, open_bottom=True)
    # door tunnel + dark inside
    yd = -hy + 0.09
    H = ensure_ccw(hole)
    Hr = list(reversed(H))
    for i in range(len(Hr)):
        p, q = Hr[i], Hr[(i + 1) % len(Hr)]
        mb.face([_v(p[0], -hy, p[1]), _v(p[0], yd, p[1]), _v(q[0], yd, q[1]), _v(q[0], -hy, q[1])], WALL)
    mb.face([_v(x, yd, z) for x, z in H], "M_Trim_Dark")
    # door surround trim
    ring_o = [(-dr - 0.05, dz0 - 0.03), (dr + 0.05, dz0 - 0.03)] + [
        ((dr + 0.05) * math.cos(math.pi * k / 6), dzs + (dr + 0.05) * math.sin(math.pi * k / 6)) for k in range(0, 7)]
    tr = MeshBuilder()
    Ro = ensure_ccw(ring_o)
    loops2 = [[Vector((x, z, 0.0)) for x, z in Ro], [Vector((x, z, 0.0)) for x, z in H]]
    flat2 = [p for lp in loops2 for p in lp]
    yt = -hy - 0.04
    for t in geometry.tessellate_polygon(loops2):
        a, b, c = flat2[t[0]], flat2[t[1]], flat2[t[2]]
        if (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) < 0:
            b, c = c, b
        tr.face([_v(a.x, yt, a.y), _v(b.x, yt, b.y), _v(c.x, yt, c.y)], TRIM)
    for i in range(len(Ro)):
        p, q = Ro[i], Ro[(i + 1) % len(Ro)]
        tr.face([_v(p[0], yt, p[1]), _v(p[0], -hy, p[1]), _v(q[0], -hy, q[1]), _v(q[0], yt, q[1])], TRIM)
    Hh = list(reversed(H))
    for i in range(len(Hh)):
        p, q = Hh[i], Hh[(i + 1) % len(Hh)]
        tr.face([_v(p[0], yt, p[1]), _v(p[0], -hy, p[1]), _v(q[0], -hy, q[1]), _v(q[0], yt, q[1])], TRIM)
    mb.extend(tr)
    # corner boards
    for sx in (-1, 1):
        for sy in (-1, 1):
            bbox(mb, sx * hx - 0.035, sy * hy - 0.035, Z0, sx * hx + 0.035, sy * hy + 0.035, ZE, TRIM,
                 skip=("-z",))
    # roof: two chunky slabs + ridge cap
    pitch = math.atan2(ZR - ZE, hx)
    over, t = 0.12, 0.07
    slope_len = math.hypot(hx, ZR - ZE) + over
    for s in (-1, 1):
        u = Vector((s * math.cos(pitch), 0.0, -math.sin(pitch)))
        nrm = Vector((s * math.sin(pitch), 0.0, math.cos(pitch)))
        ridge = Vector((0.0, 0.0, ZR))
        c = ridge + u * (slope_len / 2) + nrm * (t / 2)
        R = Matrix.Rotation(s * pitch, 3, "Y")
        rbox(mb, c, (slope_len, D + 2 * 0.1, t), ROOF, rot=R, bevel=0.02)
    # ridge cap hugging both roof planes (pentagon section)
    def zt(x):
        return ZR + t / math.cos(pitch) - abs(x) * math.tan(pitch)
    rw = 0.065
    xz_prism(mb, [(-rw, zt(rw) - 0.015), (rw, zt(rw) - 0.015), (rw, zt(rw) + 0.022), (0.0, zt(0.0) + 0.03),
                  (-rw, zt(rw) + 0.022)], -hy - 0.11, hy + 0.11, ROOF)
    # name plate (recolor: sign) above the door
    bbox(mb, -0.15, -hy - 0.04, 0.72, 0.15, -hy, 0.83, SIGN, bevel=0.012, skip=("+y",))
    # food bowl
    lathe(mb, [(0.11, 0.0), (0.15, 0.075), (0.125, 0.075), (0.0, 0.05)], "M_Door_Red", seg=10,
          cx=0.3, cy=-hy - 0.28, mats=["M_Door_Red", "M_Door_Red", "M_Crate"])
    _center_y(mb)       # the bowl sits in front: re-centre the whole footprint on the origin
    _add(K, "KIT_Doghouse", mb, "Yard", None, smooth=("M_Door_Red", "M_Crate"), angle=50)


def birdbath(K):
    mb = MeshBuilder()
    m = "M_Concrete"
    prof = [(0.26, 0.0), (0.26, 0.06), (0.2, 0.1), (0.1, 0.16), (0.075, 0.3), (0.075, 0.46), (0.1, 0.58),
            (0.18, 0.66), (0.4, 0.73), (0.43, 0.79), (0.38, 0.8), (0.33, 0.75), (0.0, 0.75)]
    mats = [m] * (len(prof) - 2) + ["M_Water"]
    lathe(mb, prof, m, seg=12, mats=mats)
    _add(K, "KIT_Birdbath", mb, "Yard", None, smooth=(m,), angle=50)


def mailbox_house(K):
    mb = MeshBuilder()
    bbox(mb, -0.045, -0.045, 0.0, 0.045, 0.045, 1.0, TRIM, bevel=0.012, skip=("-z",))
    bbox(mb, -0.08, -0.3, 1.0, 0.08, 0.2, 1.04, TRIM, bevel=0.01)
    # classic arched mailbox body, door facing the street (-Y)
    r, zb, zs = 0.1, 1.04, 1.16
    arch = [(-r, zb), (r, zb)] + [(r * math.cos(math.pi * k / 6), zs + r * math.sin(math.pi * k / 6))
                                  for k in range(0, 7)]
    # body front left open: the door slab below is CLOSED (its back face caps the body), so the
    # door rim that overhangs the body is solid from behind too (backface-culling safe)
    xz_prism(mb, arch, -0.3, 0.22, "M_Metal_Dark", front=False)
    door = [(x * 1.07, zb + (z - zb) * 1.05) for x, z in arch]
    xz_prism(mb, door, -0.33, -0.3, "M_Metal_Dark")
    bbox(mb, -0.03, -0.36, 1.2, 0.03, -0.33, 1.23, "M_Metal")
    # red flag (raised) on the +X side: one closed 0.03 m thick L-shaped slab (arm + flag)
    flag = [(-0.08, 1.24), (0.06, 1.24), (0.06, 1.08), (0.1, 1.08), (0.1, 1.33), (-0.08, 1.33)]   # (y, z)
    fl = MeshBuilder()
    # extrude (-y, z) along Y over [0.1, 0.13], then rotate -90 deg about Z: (a, c, z) -> (c, -a, z)
    xz_prism(fl, [(-y, z) for y, z in flag], 0.1, 0.13, "M_Door_Red")
    fl.transform(Matrix.Rotation(-math.pi / 2, 4, "Z"))
    mb.extend(fl)
    _add(K, "KIT_Mailbox_House", mb, "Yard", None, smooth=("M_Metal_Dark",), angle=40)


def swing(K):
    mb = MeshBuilder()
    fr = MeshBuilder()
    hx, ty, H = 1.2, 0.85, 2.15
    for x in (-hx, hx):
        for s in (-1, 1):
            tube(fr, (x, s * ty, -0.03), (x, 0.0, H), 0.045, AWNING, seg=8, cap1=False)
        yb = ty * (1 - 0.9 / H)
        tube(fr, (x, -yb, 0.9), (x, yb, 0.9), 0.03, AWNING, seg=6, cap1=False)
    floor_clamp(fr, 0.0)
    mb.extend(fr)
    tube(mb, (-hx - 0.12, 0.0, H), (hx + 0.12, 0.0, H), 0.055, AWNING, seg=8, cap0=True, cap1=True)
    for sx in (-0.55, 0.55):
        for cx in (sx - 0.22, sx + 0.22):
            bbox(mb, cx - 0.02, -0.02, 0.5, cx + 0.02, 0.02, H - 0.04, "M_Metal", skip=("-z", "+z"))
        bbox(mb, sx - 0.27, -0.11, 0.45, sx + 0.27, 0.11, 0.51, "M_Wood_Light", bevel=0.018)
    _add(K, "KIT_Swing", mb, "Yard", None, smooth=(AWNING,), angle=50)


# =============================================================================== entry
def build(K):
    tree_round_a(K)
    tree_round_b(K)
    tree_cone(K)
    tree_small(K)
    tree_palm(K)
    bush_a(K)
    bush_b(K)
    hedge_3m(K)
    flowerbed_2m(K)
    rock_a(K)
    rock_b(K)
    fence_picket(K)
    fence_wood(K)
    fence_chain(K)
    fence_iron(K)
    gate_picket(K)
    lamp_park(K)
    picnic_table(K)
    planter(K)
    doghouse(K)
    birdbath(K)
    mailbox_house(K)
    swing(K)
