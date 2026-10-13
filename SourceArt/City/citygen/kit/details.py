"""Kit family: DETAILS - awnings, signs and facade add-ons. See docs/KIT_SPEC.md.

Conventions (spec): meters, Z up, every piece's front faces -Y.
Facade-attached pieces have their origin on the facade plane y = 0, centred in x; everything that
sticks out of the facade lives at y < 0. KIT_Sign_Rooftop is free-standing (origin = bottom centre
of its footprint).

Required pieces (exact spec names)
    Awnings : KIT_Awning_3m, KIT_Awning_Flat_3m, KIT_Awning_Window
    Signs   : KIT_Sign_Board_3m, KIT_Sign_Blade, KIT_Sign_Rooftop
    Facade  : KIT_Porch_3m, KIT_Steps_2, KIT_Canopy_Door, KIT_Balcony_3m, KIT_WindowBox,
              KIT_FireEscape_3m, KIT_DownPipe_H3

Extra pieces (not in the spec; optional set dressing, meta kit_extra = True)
    KIT_Sign_Lamp      (Signs)  gooseneck lamp for fascia signs. Facade-attached, z = 0 = wall plate
                                bottom; mount ~0.1 m above a KIT_Sign_Board_3m, one or two per board.
    KIT_Sign_Blade_Paw (Signs)  pet-shop variant of KIT_Sign_Blade (identical bracket, origin and dims)
                                with a raised paw-print pictogram instead of the lettering bars.
    KIT_DownPipe_Shoe  (Facade) 0.6 m kick-out that ends a downpipe stack at ground level (same pipe
                                axis x = 0, y = -0.1 as KIT_DownPipe_H3), z = 0 = ground.
    KIT_DownPipe_Head  (Facade) rain-head hopper on top of a downpipe stack under the eave,
                                z = 0 = top of the pipe below.

Placement notes
    KIT_Awning_3m      z = 0 is the fabric top at the facade (~3.3 on an H4 storefront).
    KIT_Awning_Window  z = 0 is the fabric top at the facade (~2.75 above a KIT_Wall_Window_H3 floor).
    KIT_WindowBox      top meets the window sill: z ~ floor + 0.52 for KIT_Wall_Window_H3.
    KIT_Canopy_Door    z = 0 is the canopy underside (door head ~2.36-2.45).
    KIT_Porch_3m       deck top at 0.35 (pairs with a ground floor raised 0.35); roof meets the wall
                       at 3.35; steps protrude to y = -2.8.
    KIT_Steps_2        risers 2 x 0.175: top tread at 0.35 = porch deck = raised ground floor datum.
                       (Intentional deviation from the spec's "x 0.3" after the kit review: a 0.3 stair
                       left a 0.05 lip under raised doors.)
    KIT_FireEscape_3m  z = 0 = platform top = floor level; its stair lands on the instance 3 m below.

Sign faces
    KIT_Sign_Board_3m / KIT_Sign_Blade / KIT_Sign_Rooftop carry a raised M_Sign_Face lettering
    suggestion (word bars; 0.12 tall on the board, 0.08-0.11 on the blade, 0.16-0.34 on the billboard).
    For Unity decals / text the inner face field is published as meta:
        kit_decal_rect  = [u0, z0, u1, z1] in piece space (u = x; for the blade signs u = y)
        kit_decal_plane = "y=<face plane>" (normal -Y) or, for the two-sided blades, "abs(x)=<plane>".

Recolour placeholders used
    M_Awning_Red  : awning stripes / cheeks (alternating with M_Awning_Cream), flat canopy fascia
    M_Trim_White  : posts, rails, fascia, soffits, brackets, tie rods, step risers
    M_Sign_Accent : sign faces (inside an M_Sign_Board frame, with an M_Sign_Face pinstripe)
    M_Roof_Slate  : porch roof and door-canopy roofing
    M_Door_Wood   : window box (matches shutters / doors)
    M_Foliage     : window box greenery (one cushion incl. the trailing fringe; no M_Foliage_Dark)

Every hand-made polygon goes through poly(), which orients it against an explicit outward
direction, so all faces are single-sided-safe (Unity backface culling).
"""
import math
import traceback

from mathutils import Matrix, Vector

from .. import facade as F
from ..meshutil import MeshBuilder

FAM = "details"

RED = "M_Awning_Red"
CREAM = "M_Awning_Cream"
TRIM = "M_Trim_White"
METAL = "M_Metal"
METAL_D = "M_Metal_Dark"
BOARD = "M_Sign_Board"
ACCENT = "M_Sign_Accent"
SIGN_FACE = "M_Sign_Face"
ROOF = "M_Roof_Slate"
WOOD = "M_Wood_Light"
CONC = "M_Concrete"
EMIT = "M_Light_Emit"


# ============================================================================ geometry helpers
def _newell(P):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def poly(mb, pts, mat, want):
    """Add a planar polygon whose normal points along *want* (winding fixed automatically)."""
    Q = []
    for p in pts:
        v = Vector(p)
        if not Q or (v - Q[-1]).length > 1e-7:
            Q.append(v)
    if len(Q) > 1 and (Q[0] - Q[-1]).length < 1e-7:
        Q.pop()
    if len(Q) < 3:
        return
    if _newell(Q).dot(Vector(want)) < 0:
        Q.reverse()
    mb.face(Q, mat)


def box(mb, x0, y0, z0, x1, y1, z1, mat, skip=(), mats=None):
    """Axis aligned box; mats = {'+z': 'M_..', ...} overrides the material per face."""
    if not mats:
        mb.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
        return
    keys = ("-x", "+x", "-y", "+y", "-z", "+z")
    for k in keys:
        if k in skip:
            continue
        mb.box(x0, y0, z0, x1, y1, z1, mats.get(k, mat), skip=tuple(q for q in keys if q != k))


def sweep(mb, p0, p1, ring0, mat, ring1=None, up=(0, 0, 1), caps=(True, True), cap_mats=(None, None)):
    """Prism / frustum along p0->p1. ring0/ring1: convex 2D cross sections (u, v) at each end."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    u = d.cross(Vector(up))
    if u.length < 1e-6:
        u = d.cross(Vector((0.0, 1.0, 0.0)))
    u.normalize()
    v = u.cross(d).normalized()
    ring1 = ring1 or ring0
    r0 = [p0 + u * a + v * b for a, b in ring0]
    r1 = [p1 + u * a + v * b for a, b in ring1]
    n = len(r0)
    for i in range(n):
        j = (i + 1) % n
        q = [r0[i], r0[j], r1[j], r1[i]]
        fc = (q[0] + q[1] + q[2] + q[3]) / 4.0
        axis_pt = p0 + d * (fc - p0).dot(d)
        poly(mb, q, mat, fc - axis_pt)
    if caps[0]:
        poly(mb, r0, cap_mats[0] or mat, -d)
    if caps[1]:
        poly(mb, r1, cap_mats[1] or mat, d)


def beam(mb, p0, p1, w, h, mat, up=(0, 0, 1), caps=(True, True)):
    """Rectangular bar from p0 to p1; w across (d x up), h in the (d, up) plane."""
    hw, hh = w / 2.0, h / 2.0
    sweep(mb, p0, p1, [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)], mat, up=up, caps=caps)


def circle(r, seg, rot=0.0):
    return [(r * math.cos(rot + 2 * math.pi * i / seg), r * math.sin(rot + 2 * math.pi * i / seg)) for i in range(seg)]


def rod(mb, p0, p1, r, mat, seg=6, caps=(True, True), r1=None, cap_mats=(None, None)):
    sweep(mb, p0, p1, circle(r, seg, math.pi / seg), mat,
          ring1=circle(r if r1 is None else r1, seg, math.pi / seg), caps=caps, cap_mats=cap_mats)


def extrude_x(mb, prof, x0, x1, mat, edge_mats=None, skip_edges=(), caps=(True, True), cap_mat=None):
    """Extrude a CONVEX (y, z) profile along X from x0 to x1 (outward normals)."""
    n = len(prof)
    cy = sum(p[0] for p in prof) / n
    cz = sum(p[1] for p in prof) / n
    for i in range(n):
        if i in skip_edges:
            continue
        (ya, za), (yb, zb) = prof[i], prof[(i + 1) % n]
        m = (edge_mats or {}).get(i, mat)
        poly(mb, [(x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)], m,
             (0.0, (ya + yb) / 2 - cy, (za + zb) / 2 - cz))
    if caps[0]:
        poly(mb, [(x0, y, z) for y, z in prof], cap_mat or mat, (-1, 0, 0))
    if caps[1]:
        poly(mb, [(x1, y, z) for y, z in prof], cap_mat or mat, (1, 0, 0))


def blob(mb, c, rx, ry, rz, mat, seg=6, rings=3):
    """Closed low-poly ellipsoid."""
    cx, cy, cz = c
    C = Vector(c)
    rows = []
    for i in range(1, rings):
        th = math.pi * i / rings
        rows.append([Vector((cx + rx * math.sin(th) * math.cos(2 * math.pi * j / seg),
                             cy + ry * math.sin(th) * math.sin(2 * math.pi * j / seg),
                             cz + rz * math.cos(th))) for j in range(seg)])
    top, bot = Vector((cx, cy, cz + rz)), Vector((cx, cy, cz - rz))
    for j in range(seg):
        k = (j + 1) % seg
        t = [top, rows[0][j], rows[0][k]]
        poly(mb, t, mat, (t[0] + t[1] + t[2]) / 3 - C)
        t = [bot, rows[-1][j], rows[-1][k]]
        poly(mb, t, mat, (t[0] + t[1] + t[2]) / 3 - C)
        for i in range(len(rows) - 1):
            q = [rows[i][j], rows[i][k], rows[i + 1][k], rows[i + 1][j]]
            poly(mb, q, mat, (q[0] + q[1] + q[2] + q[3]) / 4 - C)


def dome(mb, c, rx, ry, rz, mat, seg=7, rings=3):
    """Upper half ellipsoid with an open bottom (sits on / in something)."""
    cx, cy, cz = c
    C = Vector(c)
    rows = []
    for i in range(rings):
        ph = (math.pi / 2) * i / rings
        rows.append([Vector((cx + rx * math.cos(ph) * math.cos(2 * math.pi * j / seg),
                             cy + ry * math.cos(ph) * math.sin(2 * math.pi * j / seg),
                             cz + rz * math.sin(ph))) for j in range(seg)])
    pole = Vector((cx, cy, cz + rz))
    for j in range(seg):
        k = (j + 1) % seg
        for i in range(rings - 1):
            q = [rows[i][j], rows[i][k], rows[i + 1][k], rows[i + 1][j]]
            poly(mb, q, mat, (q[0] + q[1] + q[2] + q[3]) / 4 - C)
        t = [rows[-1][j], rows[-1][k], pole]
        poly(mb, t, mat, (t[0] + t[1] + t[2]) / 3 - C)


def ring(mb, outer, inner, to3d, mat, want):
    """Mitred rectangular frame between rect outer and rect inner ((u0, v0, u1, v1)), no T-junctions."""
    O = [(outer[0], outer[1]), (outer[2], outer[1]), (outer[2], outer[3]), (outer[0], outer[3])]
    I = [(inner[0], inner[1]), (inner[2], inner[1]), (inner[2], inner[3]), (inner[0], inner[3])]
    for i in range(4):
        j = (i + 1) % 4
        poly(mb, [to3d(*O[i]), to3d(*O[j]), to3d(*I[j]), to3d(*I[i])], mat, want)


def rect(mb, r, to3d, mat, want):
    poly(mb, [to3d(r[0], r[1]), to3d(r[2], r[1]), to3d(r[2], r[3]), to3d(r[0], r[3])], mat, want)


def inset(r, d):
    return (r[0] + d, r[1] + d, r[2] - d, r[3] - d)


def hgrid(mb, x0, y0, x1, y1, z, holes, mat, up, hole_mat=None):
    """Horizontal rectangle at height z split (conforming grid) around rectangular holes.
    hole_mat fills the holes flush with another material; otherwise they stay open."""
    xs = sorted({x0, x1, *[h[0] for h in holes], *[h[2] for h in holes]})
    ys = sorted({y0, y1, *[h[1] for h in holes], *[h[3] for h in holes]})
    want = (0, 0, 1 if up else -1)
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            a, b, c, d = xs[i], xs[i + 1], ys[j], ys[j + 1]
            cx, cy = (a + b) / 2, (c + d) / 2
            inside = any(h[0] < cx < h[2] and h[1] < cy < h[3] for h in holes)
            if inside and not hole_mat:
                continue
            poly(mb, [(a, c, z), (b, c, z), (b, d, z), (a, d, z)], hole_mat if inside else mat, want)


def reveal_y(mb, hole, ya, yb, mat):
    """Jamb faces of an xz-plane opening between the planes y = ya and y = yb (facing inward)."""
    x0, z0, x1, z1 = hole
    poly(mb, [(x0, ya, z0), (x0, yb, z0), (x0, yb, z1), (x0, ya, z1)], mat, (1, 0, 0))
    poly(mb, [(x1, ya, z0), (x1, yb, z0), (x1, yb, z1), (x1, ya, z1)], mat, (-1, 0, 0))
    poly(mb, [(x0, ya, z1), (x1, ya, z1), (x1, yb, z1), (x0, yb, z1)], mat, (0, 0, -1))
    poly(mb, [(x0, ya, z0), (x1, ya, z0), (x1, yb, z0), (x0, yb, z0)], mat, (0, 0, 1))


def oct_prism(mb, cx, cy, a, c, z0, z1, mat):
    """Square post with chamfered vertical edges (half size a, chamfer c), open ends."""
    b = a - c
    pts = [(a, -b), (a, b), (b, a), (-b, a), (-a, b), (-a, -b), (-b, -a), (b, -a)]
    for i in range(8):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 8]
        poly(mb, [(cx + x0, cy + y0, z0), (cx + x1, cy + y1, z0), (cx + x1, cy + y1, z1), (cx + x0, cy + y0, z1)],
             mat, ((x0 + x1) / 2, (y0 + y1) / 2, 0.0))


def knee_bracket(mb, xc, t, depth, height, z_top, mat, seg=4, foot=0.06):
    """Concave (scroll-like) knee bracket against the wall (y = 0) under a ledge at z_top."""
    yo, zb = -depth, z_top - height
    pts = [(0.0, z_top), (yo, z_top), (yo, z_top - foot)]
    ry, rz = depth - foot, height - foot          # arc centre at the outer-bottom corner
    for i in range(1, seg):
        th = (math.pi / 2) * i / seg
        pts.append((yo + ry * math.sin(th), zb + rz * math.cos(th)))
    pts += [(-foot, zb), (0.0, zb)]
    xa, xb = xc - t / 2, xc + t / 2
    c0 = pts[0]
    for k in range(1, len(pts) - 1):            # fan from the wall/top corner (star-shaped)
        for xx, s in ((xa, -1), (xb, 1)):
            poly(mb, [(xx, c0[0], c0[1]), (xx, pts[k][0], pts[k][1]), (xx, pts[k + 1][0], pts[k + 1][1])], mat, (s, 0, 0))
    for k in range(1, len(pts) - 1):            # rim (skip the top and wall edges)
        (y0, z0), (y1, z1) = pts[k], pts[k + 1]
        poly(mb, [(xa, y0, z0), (xb, y0, z0), (xb, y1, z1), (xa, y1, z1)], mat, (0, z1 - z0, -(y1 - y0)))


def _safe_bevel(sub, width):
    return F.bevelled(sub, width)


# ============================================================================ awnings
def awning_shell(mb, W, top, under, zb, dip, n, seg=4, th_v=0.04, cheek_t=0.04, mats=(RED, CREAM), cheek_mat=RED):
    """Striped fabric awning across x in [-W/2, W/2].

    top   : (y, z) polyline of the fabric top from the wall (y = 0) to the valance top front edge.
    under : (y, z) polyline of the fabric underside, ending on the valance back plane.
    zb    : valance bottom at the stripe seams, dip = extra scallop depth mid-stripe.
    n     : number of stripes (odd -> both edge stripes use mats[0]).
    """
    yf, zt = top[-1]
    yb, zu = under[-1]
    xs = [-W / 2 + W * i / n for i in range(n + 1)]
    for i in range(n):
        xa, xb = xs[i], xs[i + 1]
        m = mats[i % 2]
        for k in range(len(top) - 1):
            (y0, z0), (y1, z1) = top[k], top[k + 1]
            poly(mb, [(xa, y0, z0), (xb, y0, z0), (xb, y1, z1), (xa, y1, z1)], m, (0, z1 - z0, -(y1 - y0)))
        for k in range(len(under) - 1):
            (y0, z0), (y1, z1) = under[k], under[k + 1]
            poly(mb, [(xa, y0, z0), (xb, y0, z0), (xb, y1, z1), (xa, y1, z1)], m, (0, -(z1 - z0), y1 - y0))
        sc = [(xa + (xb - xa) * s / seg, zb - dip * math.sin(math.pi * s / seg)) for s in range(seg + 1)]
        poly(mb, [(xa, yf, zt)] + [(x, yf, z) for x, z in sc] + [(xb, yf, zt)], m, (0, -1, 0))
        poly(mb, [(xa, yb, zu)] + [(x, yb, z) for x, z in sc] + [(xb, yb, zu)], m, (0, 1, 0))
        for s in range(seg):
            (x0, z0), (x1, z1) = sc[s], sc[s + 1]
            poly(mb, [(x0, yf, z0), (x1, yf, z1), (x1, yb, z1), (x0, yb, z0)], m, (0, 0, -1))
    # side cheeks (closed triangular sides) + valance end caps
    zcb = min(zt, zu)
    cheek = list(top) + ([(yf, zcb)] if zcb < zt - 1e-6 else []) + [(0.0, zcb)]
    for s in (-1, 1):
        xo, xi = s * W / 2, s * (W / 2 - cheek_t)
        poly(mb, [(xo, y, z) for y, z in cheek], cheek_mat, (s, 0, 0))
        poly(mb, [(xi, y, z) for y, z in cheek], cheek_mat, (-s, 0, 0))
        poly(mb, [(xi, yb, zcb), (xo, yb, zcb), (xo, 0.0, zcb), (xi, 0.0, zcb)], cheek_mat, (0, 0, -1))
        end_mat = mats[0] if s < 0 else mats[(n - 1) % 2]
        poly(mb, [(xo, yf, zcb), (xo, yf, zb), (xo, yb, zb), (xo, yb, zcb)], end_mat, (s, 0, 0))


def _bezier2(a, c, b, n):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0],
                    (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]))
    return out


def _awning_3m(K):
    """Classic striped shop awning: slopes out to y=-1.5 and down 0.9, cheeks, scalloped 0.25 valance."""
    mb = MeshBuilder()
    W, proj, drop, th = 2.9, 1.5, 0.9, 0.04
    A, B = (0.0, 0.0), (-proj, -drop)
    L = math.hypot(proj, drop)
    nrm = (-drop / L, proj / L)                       # up/out normal of the chord
    bulge = 0.055                                      # gentle convex belly
    ctrl = ((A[0] + B[0]) / 2 + 2 * bulge * nrm[0], (A[1] + B[1]) / 2 + 2 * bulge * nrm[1])
    top = _bezier2(A, ctrl, B, 3)
    under = [(y, z - th) for y, z in top]
    yb = B[0] + th
    (y2, z2), (y3, z3) = under[-2], under[-1]
    t = (yb - y2) / (y3 - y2)
    under[-1] = (yb, z2 + t * (z3 - z2))
    awning_shell(mb, W, top, under, zb=-drop - 0.17, dip=0.08, n=9)
    # slim mounting rail along the top edge (same width as the fabric)
    box(mb, -W / 2, -0.08, -0.11, W / 2, 0.0, 0.0, METAL_D, skip=("+y",))
    K.add("KIT_Awning_3m", mb, FAM, "Awnings",
          meta=dict(attach="facade", z0="fabric top at facade", width=W, place_z_on_H4=3.3))


def _awning_window(K):
    """Small dome awning for a 1.1 m window: quarter-round profile, 5 stripes, short scalloped valance."""
    mb = MeshBuilder()
    W, proj, drop, th = 1.5, 0.7, 0.55, 0.04
    a0 = math.radians(70.0)
    ry, rz = proj / (1 - math.cos(a0)), drop / math.sin(a0)
    cy, cz = ry * math.cos(a0), -rz * math.sin(a0)
    n = 5
    angs = [a0 * (1 - i / n) for i in range(n + 1)]
    top = [(cy - ry * math.cos(a), cz + rz * math.sin(a)) for a in angs]
    top[0] = (0.0, 0.0)
    under = [(cy - (ry - th) * math.cos(a), cz + (rz - th) * math.sin(a)) for a in angs]
    under[0] = (0.0, under[0][1])
    awning_shell(mb, W, top, under, zb=cz - 0.065, dip=0.05, n=5)
    K.add("KIT_Awning_Window", mb, FAM, "Awnings",
          meta=dict(attach="facade", z0="fabric top at facade", width=W, place_z_on_H3=2.75))


def _awning_flat(K):
    """Modern flat canopy 3.0 x 1.2 x 0.15 with two tie rods; z = 0 is the canopy underside."""
    mb = MeshBuilder()
    D, H, c = 1.2, 0.15, 0.03
    prof = [(0.0, 0.0), (0.0, H), (-D + c, H), (-D, H - c), (-D, c), (-D + c, 0.0)]
    # edges: 0 wall (skip), 1 top, 2 chamfer, 3 fascia, 4 chamfer, 5 underside (custom)
    extrude_x(mb, prof, -1.5, 1.5, RED, edge_mats={1: METAL_D}, skip_edges=(0, 5))
    # underside with two flush downlights
    s = 0.1
    lights = [(-0.8, -0.62), (0.8, -0.62)]
    holes = [(lx - s, ly - s, lx + s, ly + s) for lx, ly in lights]
    hgrid(mb, -1.5, -D + c, 1.5, 0.0, 0.0, holes, TRIM, up=False, hole_mat=EMIT)
    # tie rods (wall plate -> lug on the canopy top)
    for sx in (-1, 1):
        x = sx * 1.1
        plate = MeshBuilder()
        box(plate, x - 0.08, -0.035, 0.92, x + 0.08, 0.0, 1.14, TRIM, skip=("+y",))
        mb.extend(_safe_bevel(plate, 0.012))
        box(mb, x - 0.04, -1.02, H, x + 0.04, -0.9, H + 0.07, TRIM, skip=("-z",))
        rod(mb, (x, -0.96, H + 0.04), (x, -0.025, 1.03), 0.027, TRIM, seg=6)
    K.add("KIT_Awning_Flat_3m", mb, FAM, "Awnings", meta=dict(attach="facade", z0="canopy underside"))


# ============================================================================ signs
def sign_face(mb, r, to3d, want, ins=0.05, stripe=0.04):
    """Accent sign face with a cream pinstripe border (coplanar partition, no z-fight)."""
    r1 = inset(r, ins)
    r2 = inset(r1, stripe)
    ring(mb, r, r1, to3d, ACCENT, want)
    ring(mb, r1, r2, to3d, SIGN_FACE, want)
    rect(mb, r2, to3d, ACCENT, want)


def raised(mb, outline, frame, mat, d):
    """Convex outline [(u, v), ...] raised d proud of a face: front cap + side walls, open back.

    frame = (O, U, V, N): face origin, in-plane axes and outward normal (Vectors)."""
    O, U, V, N = frame
    P = lambda u, v, w: O + U * u + V * v + N * w      # noqa: E731
    n = len(outline)
    cu = sum(p[0] for p in outline) / n
    cv = sum(p[1] for p in outline) / n
    poly(mb, [P(u, v, d) for u, v in outline], mat, N)
    for i in range(n):
        (u0, v0), (u1, v1) = outline[i], outline[(i + 1) % n]
        poly(mb, [P(u0, v0, 0.0), P(u1, v1, 0.0), P(u1, v1, d), P(u0, v0, d)], mat,
             U * ((u0 + u1) / 2 - cu) + V * ((v0 + v1) / 2 - cv))


def rect_outline(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def text_line(words, h, v, gap):
    """Centred row of 'word' bars (lettering suggestion): widths -> outlines at height v (centre)."""
    total = sum(words) + gap * (len(words) - 1)
    u, out = -total / 2, []
    for wd in words:
        out.append(rect_outline(u, v - h / 2, u + wd, v + h / 2))
        u += wd + gap
    return out


def ellipse_outline(cu, cv, ru, rv, seg, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg + math.pi / 2
        x, y = ru * math.cos(a), rv * math.sin(a)
        pts.append((cu + x * c - y * s, cv + x * s + y * c))
    return pts


def face_field(w, h, fw, ins, stripe):
    """Inner accent field (inside the pinstripe) of a framed panel, panel-local (u0, v0, u1, v1)."""
    return inset(inset((-w / 2 + fw, fw, w / 2 - fw, h - fw), ins), stripe)


def framed_panel(w, h, t, fw=0.07, rec=0.035, two_sided=False, back_mat=None, bevel=0.018,
                 ins=0.05, stripe=0.04, art=(), art_d=0.012):
    """Sign panel in the xz plane: x in [-w/2, w/2], z in [0, h].

    Single-sided: y in [-t, 0], face toward -Y (back open unless back_mat).
    Two-sided   : y in [-t/2, t/2], framed faces on both sides.
    art         : convex outlines (u, v) relative to the face centre, raised art_d in M_Sign_Face
                  (lettering bars / pictograms). On the +Y side u is mirrored so it reads correctly.
    """
    fr, out = MeshBuilder(), MeshBuilder()
    x0, x1 = -w / 2, w / 2
    y0, y1 = (-t / 2, t / 2) if two_sided else (-t, 0.0)
    hole = (x0 + fw, fw, x1 - fw, h - fw)
    sides = [(y0, -1)] + ([(y1, 1)] if two_sided else [])
    for yy, s in sides:
        ring(fr, (x0, 0.0, x1, h), hole, (lambda u, v, yy=yy: (u, yy, v)), BOARD, (0, s, 0))
        yr = yy - s * rec
        reveal_y(out, hole, yy, yr, BOARD)
        sign_face(out, hole, (lambda u, v, yr=yr: (u, yr, v)), (0, s, 0), ins, stripe)
        frame = (Vector((0.0, yr, h / 2)), Vector((-float(s), 0.0, 0.0)), Vector((0.0, 0.0, 1.0)),
                 Vector((0.0, float(s), 0.0)))
        for o in art:
            raised(out, o, frame, SIGN_FACE, art_d)
    poly(fr, [(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)], BOARD, (0, 0, 1))
    poly(fr, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], BOARD, (0, 0, -1))
    poly(fr, [(x0, y0, 0), (x0, y1, 0), (x0, y1, h), (x0, y0, h)], BOARD, (-1, 0, 0))
    poly(fr, [(x1, y0, 0), (x1, y1, 0), (x1, y1, h), (x1, y0, h)], BOARD, (1, 0, 0))
    if back_mat and not two_sided:
        poly(fr, [(x0, 0, 0), (x1, 0, 0), (x1, 0, h), (x0, 0, h)], back_mat, (0, 1, 0))
    res = _safe_bevel(fr, bevel) if bevel else fr
    res.extend(out)
    return res


def _decal(rect_uv, plane, axis="y", offset=(0.0, 0.0)):
    """meta for a Unity decal / text overlay: rect in piece space + the face plane coordinate."""
    u0, v0, u1, v1 = rect_uv
    ou, oz = offset
    return dict(decal_rect=[round(u0 + ou, 4), round(v0 + oz, 4), round(u1 + ou, 4), round(v1 + oz, 4)],
                decal_plane=f"{axis}={plane:+.4f}")


BOARD_TEXT = text_line([0.42, 0.22, 0.58, 0.34], 0.12, 0.0, 0.12)     # e.g. "BOB'S  PET  SUPPLY  CO"


def _sign_board(K):
    """Fascia sign 2.8 x 0.7 x 0.12: dark board frame, recessed accent face with pinstripe and a
    raised M_Sign_Face lettering suggestion (4 word bars, 0.12 tall)."""
    mb = MeshBuilder()
    W, H, T, FW, REC, INS, ST = 2.8, 0.7, 0.12, 0.075, 0.035, 0.05, 0.04
    mb.extend(framed_panel(W, H, T, fw=FW, rec=REC, ins=INS, stripe=ST, art=BOARD_TEXT))
    meta = dict(attach="facade", z0="board bottom", lettering="raised 0.012 M_Sign_Face bars")
    meta.update(_decal(face_field(W, H, FW, INS, ST), -T + REC, "y"))           # face normal -Y
    K.add("KIT_Sign_Board_3m", mb, FAM, "Signs", meta=meta)


BLADE_TEXT = (text_line([0.46], 0.11, 0.13, 0.0) + text_line([0.2, 0.17], 0.08, -0.03, 0.06)
              + text_line([0.34], 0.08, -0.16, 0.0))


def _paw_art(s=1.0, dv=0.0):
    """Pet-shop pictogram: main pad (rounded triangle) + 4 toe beans, convex outlines (u, v)."""
    pad = [(-0.14, -0.075), (-0.085, -0.125), (0.0, -0.135), (0.085, -0.125), (0.14, -0.075),
           (0.115, 0.0), (0.05, 0.06), (-0.05, 0.06), (-0.115, 0.0)]
    art = [[(u * s, (v - 0.07) * s + dv) for u, v in pad]]
    for cu, cv, rot in ((-0.175, 0.075, 0.42), (-0.068, 0.155, 0.12), (0.068, 0.155, -0.12), (0.175, 0.075, -0.42)):
        art.append(ellipse_outline(cu * s, cv * s + dv, 0.05 * s, 0.066 * s, 7, rot))
    return art


def _blade(K, name, art, extra=False):
    """Projecting blade sign: wall plate + arm + brace, 0.9 x 0.9 two-sided panel out to y = -1.2."""
    mb = MeshBuilder()
    W, T, FW, REC, INS, ST = 0.9, 0.1, 0.065, 0.025, 0.04, 0.04
    panel = framed_panel(W, W, T, fw=FW, rec=REC, two_sided=True, ins=INS, stripe=ST, art=art)
    M = Matrix.Translation((0.0, -0.75, 0.12)) @ Matrix.Rotation(math.radians(90.0), 4, "Z")
    mb.extend(panel, M)                               # panel: y in [-1.2, -0.3], z in [0.12, 1.02]
    hw = MeshBuilder()
    box(hw, -0.075, -0.045, 0.0, 0.075, 0.0, 1.45, METAL_D, skip=("+y",))        # wall plate
    box(hw, -0.045, -1.2, 1.085, 0.045, -1.12, 1.185, METAL_D)                    # arm end cap
    mb.extend(_safe_bevel(hw, 0.015))
    box(mb, -0.03, -1.12, 1.105, 0.03, -0.045, 1.165, METAL_D, skip=("+y", "-y"))  # arm
    beam(mb, (0.0, -0.02, 1.4), (0.0, -0.66, 1.15), 0.045, 0.045, METAL_D)          # diagonal brace
    for y in (-0.42, -1.08):                                                       # hangers
        box(mb, -0.022, y - 0.022, 1.02, 0.022, y + 0.022, 1.105, METAL_D, skip=("-z", "+z"))
    meta = dict(attach="facade", z0="bracket bottom",
                lettering="raised 0.012 M_Sign_Face " + ("paw pictogram" if extra else "bars"))
    if extra:
        meta["extra"] = True
    # panel-local face field (u, v) -> piece space: u -> y (offset -0.75), v -> z (offset +0.12);
    # two faces at x = +/-(T/2 - REC), normals +/-X
    meta.update(_decal(face_field(W, W, FW, INS, ST), T / 2 - REC, "abs(x)", offset=(-0.75, 0.12)))
    K.add(name, mb, FAM, "Signs", meta=meta)


def _sign_blade(K):
    """Generic blade sign with a 3-line lettering suggestion on both faces."""
    _blade(K, "KIT_Sign_Blade", BLADE_TEXT)


def _sign_blade_paw(K):
    """EXTRA: pet-shop blade sign variant with a raised paw-print pictogram on both faces."""
    _blade(K, "KIT_Sign_Blade_Paw", _paw_art(1.12, -0.005), extra=True)


def _sign_rooftop(K):
    """Rooftop billboard 6 x 2.5 on two posts with catwalk, railing, kickers and 3 lamps."""
    mb = MeshBuilder()
    PZ, PH, PW, PT, FW, REC, INS, ST = 1.75, 2.5, 6.0, 0.2, 0.14, 0.05, 0.12, 0.07
    art = text_line([1.3, 0.8, 1.5], 0.34, 0.2, 0.26) + text_line([1.5, 1.0], 0.16, -0.3, 0.2)
    panel = framed_panel(PW, PH, PT, fw=FW, rec=REC, back_mat=BOARD, bevel=0.03, ins=INS, stripe=ST,
                         art=art, art_d=0.02)
    mb.extend(panel, Matrix.Translation((0.0, -0.11, PZ)))   # y in [-0.31, -0.11]
    for px in (-1.9, 1.9):
        box(mb, px - 0.11, -0.11, 0.0, px + 0.11, 0.11, PZ + PH - 0.15, METAL_D, skip=("-z",))
        box(mb, px - 0.045, -1.0, 0.82, px + 0.045, -0.11, 0.92, METAL_D, skip=("+y", "+z"))  # catwalk arm
        beam(mb, (px, -0.09, 0.3), (px, -0.84, 0.84), 0.06, 0.06, METAL_D)                   # arm brace
        beam(mb, (px, 0.08, 2.3), (px, 0.98, 0.06), 0.08, 0.08, METAL_D)                     # kicker
        box(mb, px - 0.12, 0.86, 0.0, px + 0.12, 1.1, 0.05, METAL_D, skip=("-z",))           # foot
    for a, b in (((-1.9, 0.3), (1.9, 1.55)), ((-1.9, 1.55), (1.9, 0.3))):                   # X brace
        beam(mb, (a[0], 0.13, a[1]), (b[0], 0.13, b[1]), 0.05, 0.06, METAL_D)
    # catwalk deck + railing
    box(mb, -3.1, -1.0, 0.92, 3.1, -0.11, 1.0, METAL_D)
    for x in (-3.05, -1.525, 0.0, 1.525, 3.05):
        box(mb, x - 0.03, -1.0, 1.0, x + 0.03, -0.94, 1.95, METAL_D, skip=("-z", "+z"))
    box(mb, -3.08, -1.0, 1.95, 3.08, -0.94, 2.0, METAL_D)
    box(mb, -3.02, -0.99, 1.46, 3.02, -0.95, 1.5, METAL_D, skip=("-x", "+x"))
    for sx in (-1, 1):
        box(mb, sx * 3.05 - 0.03, -0.94, 1.95, sx * 3.05 + 0.03, -0.11, 2.0, METAL_D, skip=("-y",))
    # gooseneck lamps over the panel
    top = PZ + PH
    for lx in (-2.0, 0.0, 2.0):
        a = Vector((lx, -0.21, top - 0.04))            # starts inside the frame's top rail
        b = Vector((lx, -0.82, top + 0.22))            # ends inside the shade
        rod(mb, a, b, 0.028, METAL_D, seg=6, caps=(False, False))
        d = Vector((0.0, 0.42, -1.0)).normalized()
        rod(mb, b - d * 0.04, b + d * 0.2, 0.06, METAL_D, seg=6, r1=0.13, cap_mats=(None, EMIT))
    meta = dict(attach="free", z0="ground", lettering="raised 0.02 M_Sign_Face bars")
    meta.update(_decal(face_field(PW, PH, FW, INS, ST), -0.11 - PT + REC, "y", offset=(0.0, PZ)))
    K.add("KIT_Sign_Rooftop", mb, FAM, "Signs", meta=meta)


# ============================================================================ facade add-ons
def _porch(K):
    """Wood porch deck 3.0 x 2.2 x 0.35, two posts, railings, 15 deg roof (eave ~2.55-2.7, 3.35 at the
    wall) with fascia, and 2 integrated front steps (y down to -2.8)."""
    mb = MeshBuilder()
    D, H = 2.2, 0.35
    deck = MeshBuilder()
    box(deck, -1.5, -D, H - 0.08, 1.5, 0.0, H, WOOD, skip=("+y",))                     # deck slab
    mb.extend(_safe_bevel(deck, 0.02))
    box(mb, -1.46, -D + 0.04, 0.0, 1.46, 0.0, H - 0.08, TRIM, skip=("+y", "-z", "+z"))  # skirt
    sw, r = 0.6, H / 3.0                                                                # steps
    box(mb, -sw, -D - 0.6, 0.0, sw, -D + 0.04, r, TRIM, skip=("+y", "-z"), mats={"+z": WOOD})
    box(mb, -sw, -D - 0.3, r, sw, -D + 0.04, 2 * r, TRIM, skip=("+y", "-z"), mats={"+z": WOOD})
    # roof
    S, ZW, TV, YE = math.tan(math.radians(15.0)), 3.35, 0.145, -2.45
    zt = lambda y: ZW + S * y          # noqa: E731
    zu = lambda y: zt(y) - TV          # noqa: E731
    poly(mb, [(-1.5, 0, zt(0)), (1.5, 0, zt(0)), (1.5, YE, zt(YE)), (-1.5, YE, zt(YE))], ROOF, (0, -S, 1))
    poly(mb, [(-1.5, 0, zu(0)), (1.5, 0, zu(0)), (1.5, YE, zu(YE)), (-1.5, YE, zu(YE))], TRIM, (0, S, -1))
    for sx in (-1, 1):
        poly(mb, [(sx * 1.5, 0, zt(0)), (sx * 1.5, YE, zt(YE)), (sx * 1.5, YE, zu(YE)), (sx * 1.5, 0, zu(0))],
             TRIM, (sx, 0, 0))
    box(mb, -1.5, YE - 0.05, zu(YE) - 0.05, 1.5, YE, zt(YE) + 0.05, TRIM)               # fascia
    # header beam (top follows the roof underside; that face is hidden so it is skipped)
    by0, by1, bz = -2.15, -1.89, 2.4
    extrude_x(mb, [(by0, bz), (by1, bz), (by1, zu(by1)), (by0, zu(by0))], -1.5, 1.5, TRIM, skip_edges=(2,))
    # posts
    PX, PY = 1.32, -2.02
    for sx in (-1, 1):
        cx = sx * PX
        box(mb, cx - 0.13, PY - 0.13, H, cx + 0.13, PY + 0.13, H + 0.2, TRIM, skip=("-z",))       # base
        oct_prism(mb, cx, PY, 0.085, 0.028, H + 0.2, bz - 0.13, TRIM)                            # shaft
        box(mb, cx - 0.12, PY - 0.12, bz - 0.13, cx + 0.12, PY + 0.12, bz, TRIM, skip=("+z",))   # capital
    # railings: sides (post -> wall) and front (post -> stair newel)
    RT0, RT1, RB0, RB1 = H + 0.85, H + 0.92, H + 0.08, H + 0.14
    for sx in (-1, 1):
        cx = sx * PX
        box(mb, cx - 0.045, PY + 0.085, RT0, cx + 0.045, 0.0, RT1, TRIM, skip=("+y", "-y"))
        box(mb, cx - 0.035, PY + 0.085, RB0, cx + 0.035, 0.0, RB1, TRIM, skip=("+y", "-y"))
        n = 5
        for i in range(1, n + 1):
            y = PY + 0.085 + (-(PY + 0.085)) * i / (n + 1)
            box(mb, cx - 0.024, y - 0.024, RB1, cx + 0.024, y + 0.024, RT0, TRIM, skip=("-z", "+z"))
        # front
        nx = sx * (sw + 0.05)                     # stair newel post
        box(mb, nx - 0.05, PY - 0.05, H, nx + 0.05, PY + 0.05, RT1 + 0.08, TRIM, skip=("-z",))
        xa, xb = sorted((nx + sx * 0.05, cx - sx * 0.085))
        box(mb, xa, PY - 0.045, RT0, xb, PY + 0.045, RT1, TRIM, skip=("-x", "+x"))
        box(mb, xa, PY - 0.035, RB0, xb, PY + 0.035, RB1, TRIM, skip=("-x", "+x"))
        for f in (1 / 3, 2 / 3):
            x = xa + (xb - xa) * f
            box(mb, x - 0.024, PY - 0.024, RB1, x + 0.024, PY + 0.024, RT0, TRIM, skip=("-z", "+z"))
    K.add("KIT_Porch_3m", mb, FAM, "Facade", meta=dict(attach="facade", z0="ground", deck_h=H))


STEP_R = 0.175     # riser: 2 x 0.175 = 0.35 = KIT_Porch_3m deck = raised-ground-floor datum


def _steps(K):
    """Two chunky concrete steps 1.4 x 0.6, risers 2 x 0.175 = 0.35 (y in [-0.6, 0]); the top tread is
    flush with a ground floor raised 0.35 (same datum as the KIT_Porch_3m deck)."""
    mb = MeshBuilder()
    a = MeshBuilder()
    box(a, -0.7, -0.6, 0.0, 0.7, 0.0, STEP_R, CONC, skip=("+y",))
    mb.extend(_safe_bevel(a, 0.02))
    b = MeshBuilder()
    box(b, -0.7, -0.3, STEP_R, 0.7, 0.0, 2 * STEP_R, CONC, skip=("+y", "-z"))
    mb.extend(_safe_bevel(b, 0.02))
    K.add("KIT_Steps_2", mb, FAM, "Facade",
          meta=dict(attach="facade", z0="ground", riser=STEP_R, top=2 * STEP_R))


def _canopy_door(K):
    """Small gabled door hood 1.6 x 0.8 on two scroll brackets; z = 0 is the canopy underside."""
    mb = MeshBuilder()
    base = MeshBuilder()
    box(base, -0.74, -0.74, 0.0, 0.74, 0.0, 0.12, TRIM, skip=("+y",))
    mb.extend(_safe_bevel(base, 0.02))
    hw, yfr, zr, ze, tr = 0.8, -0.8, 0.52, 0.12, 0.06
    for s in (-1, 1):
        poly(mb, [(0, yfr, zr), (s * hw, yfr, ze), (s * hw, 0, ze), (0, 0, zr)], ROOF, (s * (zr - ze), 0, hw))
        poly(mb, [(0, yfr, zr - tr), (s * hw, yfr, ze - tr), (s * hw, 0, ze - tr), (0, 0, zr - tr)], TRIM,
             (-s * (zr - ze), 0, -hw))
        poly(mb, [(0, yfr, zr), (s * hw, yfr, ze), (s * hw, yfr, ze - tr), (0, yfr, zr - tr)], TRIM, (0, -1, 0))
        poly(mb, [(s * hw, yfr, ze), (s * hw, 0, ze), (s * hw, 0, ze - tr), (s * hw, yfr, ze - tr)], TRIM, (s, 0, 0))
    k = (zr - tr - 0.12) * hw / (zr - ze)
    poly(mb, [(-k, -0.74, 0.12), (k, -0.74, 0.12), (0, -0.74, zr - tr)], TRIM, (0, -1, 0))   # pediment
    for sx in (-1, 1):
        knee_bracket(mb, sx * 0.66, 0.08, 0.58, 0.42, 0.0, TRIM)
    K.add("KIT_Canopy_Door", mb, FAM, "Facade", meta=dict(attach="facade", z0="canopy underside", place_z=2.45))


def _balcony(K):
    """Balcony slab 2.6 x 1.1 x 0.15 + 1.0 m metal railing with pickets; z = 0 is the slab top."""
    mb = MeshBuilder()
    slab = MeshBuilder()
    box(slab, -1.3, -1.1, -0.15, 1.3, 0.0, 0.0, TRIM, skip=("+y",), mats={"+z": CONC})
    mb.extend(_safe_bevel(slab, 0.025))
    XR, YR = 1.25, -1.05
    for x in (-XR, 0.0, XR):                                                           # posts
        box(mb, x - 0.032, YR - 0.032, 0.0, x + 0.032, YR + 0.032, 0.95, METAL_D, skip=("-z", "+z"))
    box(mb, -XR - 0.04, YR - 0.04, 0.95, XR + 0.04, YR + 0.04, 1.0, METAL_D)            # top rail front
    box(mb, -XR - 0.025, YR - 0.025, 0.08, XR + 0.025, YR + 0.025, 0.12, METAL_D)       # bottom rail front
    for sx in (-1, 1):
        x = sx * XR
        box(mb, x - 0.04, YR + 0.04, 0.95, x + 0.04, 0.0, 1.0, METAL_D, skip=("-y", "+y"))
        box(mb, x - 0.025, YR + 0.025, 0.08, x + 0.025, 0.0, 0.12, METAL_D, skip=("-y", "+y"))
        for i in range(1, 7):
            y = YR + (0.0 - YR) * i / 7.0
            box(mb, x - 0.02, y - 0.02, 0.12, x + 0.02, y + 0.02, 0.95, METAL_D, skip=("-z", "+z"))
    n = 16
    for i in range(1, n):
        x = -XR + 2 * XR * i / n
        if abs(x) < 0.05:
            continue
        box(mb, x - 0.02, YR - 0.02, 0.12, x + 0.02, YR + 0.02, 0.95, METAL_D, skip=("-z", "+z"))
    for sx in (-1, 1):
        knee_bracket(mb, sx * 0.98, 0.09, 0.62, 0.38, -0.15, TRIM)
    K.add("KIT_Balcony_3m", mb, FAM, "Facade", meta=dict(attach="facade", z0="slab top (floor level)"))


def _window_box(K):
    """Window planter 1.2 x 0.3 x 0.25 (M_Door_Wood) with foliage mounds and blossoms; z = 0 box bottom."""
    mb = MeshBuilder()
    BX = "M_Door_Wood"
    bx, by = 0.55, -0.26           # bottom half-width / front
    tx, ty = 0.585, -0.285         # under the rim
    zr0, zr1, zs = 0.2, 0.25, 0.21
    poly(mb, [(-bx, by, 0), (bx, by, 0), (tx, ty, zr0), (-tx, ty, zr0)], BX, (0, -1, 0.15))
    for s in (-1, 1):
        poly(mb, [(s * bx, by, 0), (s * bx, 0, 0), (s * tx, 0, zr0), (s * tx, ty, zr0)], BX, (s, 0, 0.15))
    poly(mb, [(-bx, by, 0), (bx, by, 0), (bx, 0, 0), (-bx, 0, 0)], BX, (0, 0, -1))
    box(mb, -0.6, -0.3, zr0, 0.6, 0.0, zr1, BX, skip=("+y", "+z"))                       # rim band
    inner = (-0.555, -0.258, 0.555, -0.04)
    ring(mb, (-0.6, -0.3, 0.6, 0.0), inner, (lambda u, v: (u, v, zr1)), BX, (0, 0, 1))
    ix0, iy0, ix1, iy1 = inner
    # inner walls (back + ends; the front one is hidden under the foliage roll). The foliage boundary
    # cuts through their middle (z = ZB), so a raster crack there shows wall, never the void.
    poly(mb, [(ix0, iy1, zs), (ix1, iy1, zs), (ix1, iy1, zr1), (ix0, iy1, zr1)], BX, (0, -1, 0))
    poly(mb, [(ix0, iy0, zs), (ix0, iy1, zs), (ix0, iy1, zr1), (ix0, iy0, zr1)], BX, (1, 0, 0))
    poly(mb, [(ix1, iy0, zs), (ix1, iy1, zs), (ix1, iy1, zr1), (ix1, iy0, zr1)], BX, (-1, 0, 0))

    # greenery: ONE continuous M_Foliage cushion (3 lumps) that rolls over the front lip as a hanging
    # fringe (this replaces the old 3 domes + 2 separate ivy blobs). Grid columns x, rows back -> front:
    #   0 back edge (tucked under the rim) . 1 . 2 crown . 3 lip (over the rim) . 4 fringe hem
    #   5 hem return (back into the box body)  => rows 4-5 close the underside of the fringe.
    ZB = 0.23
    lumps = [(-0.33, -0.15, 0.25, 0.165, 0.15), (0.0, -0.16, 0.27, 0.175, 0.185), (0.33, -0.15, 0.25, 0.165, 0.15)]

    def crown(x, y):
        z = ZB + 0.02
        for mx, my, rx, ry, rz in lumps:
            q = 1 - ((x - mx) / rx) ** 2 - ((y - my) / ry) ** 2
            if q > 0:
                z = max(z, ZB + rz * math.sqrt(q))
        return z
    XS = [-0.57, -0.45, -0.33, -0.165, 0.0, 0.165, 0.33, 0.45, 0.57]
    HEM = [None, 0.17, 0.12, 0.18, 0.14, 0.175, 0.115, 0.17, None]     # fringe hem height per column
    YR = [-0.03, -0.12, -0.215, -0.318]                                  # crown rows (back -> lip)
    G = []
    for i, x in enumerate(XS):
        if HEM[i] is None:                                  # end columns: buried in the rim band
            col = [(x, YR[0], ZB), (x, YR[1], ZB), (x, YR[2], ZB)] + [(x, -0.285, ZB)] * 3
        else:                                               # hem return y = -0.265 is inside the box body
            col = [(x, YR[0], ZB), (x, YR[1], crown(x, YR[1])), (x, YR[2], crown(x, YR[2])),
                   (x, YR[3], max(crown(x, -0.29) - 0.03, 0.272)), (x, -0.336, HEM[i]), (x, -0.265, HEM[i])]
        G.append(col)
    for i in range(len(XS) - 1):
        for j in range(5):
            want = (0, 0, 1) if j < 3 else ((0, -1, 0.25) if j == 3 else (0, 0, -1))
            poly(mb, [G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1]], "M_Foliage", want)

    def surf(x, y):                                         # height of the faceted crown (rows 0-3)
        i = max(k for k in range(len(XS) - 1) if XS[k] <= x)
        tx = (x - XS[i]) / (XS[i + 1] - XS[i])
        j = max(k for k in range(len(YR) - 1) if YR[k] >= y)
        ty = (y - YR[j]) / (YR[j + 1] - YR[j])
        z = lambda a, b: G[a][b][2]                         # noqa: E731
        return ((1 - tx) * ((1 - ty) * z(i, j) + ty * z(i, j + 1)) +
                tx * ((1 - ty) * z(i + 1, j) + ty * z(i + 1, j + 1)))
    # 4 flower clusters (squashed 5-sided blobs, each turned differently); two sit on the front roll so
    # they read from the street below
    for x, y, r, m, rot in ((-0.4, -0.25, 0.082, "M_Foliage_Blossom", 0.3), (-0.12, -0.16, 0.086, "M_Foliage_Autumn", 1.1),
                            (0.15, -0.26, 0.084, "M_Foliage_Blossom", 2.0), (0.41, -0.17, 0.08, "M_Foliage_Autumn", 0.7)):
        fl = MeshBuilder()
        blob(fl, (0.0, 0.0, 0.0), r, r, r * 0.62, m, seg=5, rings=3)
        mb.extend(fl, Matrix.Translation((x, y, surf(x, y) + 0.012)) @ Matrix.Rotation(rot, 4, "Z"))
    K.add("KIT_WindowBox", mb, FAM, "Facade", meta=dict(attach="facade", z0="box bottom"))


def _fire_escape(K):
    """Fire escape platform 2.8 x 1.2 + picket railing + diagonal stair down 3.0 m; z = 0 platform top."""
    mb = MeshBuilder()
    X0, X1, D, T = -1.4, 1.4, 1.2, 0.08
    xt, run, drop, n = 1.2, 2.1, 3.0, 10       # stair head x, horizontal run, drop, risers
    sy0, sy1 = -1.1, -0.5                      # stair outer faces (stringers)
    hole = (-0.25, -1.12, 1.27, -0.48)
    # deck with stair hatch
    hgrid(mb, X0, -D, X1, 0.0, 0.0, [hole], METAL_D, up=True)
    hgrid(mb, X0, -D, X1, 0.0, -T, [hole], METAL_D, up=False)
    poly(mb, [(X0, -D, -T), (X1, -D, -T), (X1, -D, 0), (X0, -D, 0)], METAL_D, (0, -1, 0))
    poly(mb, [(X0, -D, -T), (X0, 0, -T), (X0, 0, 0), (X0, -D, 0)], METAL_D, (-1, 0, 0))
    poly(mb, [(X1, -D, -T), (X1, 0, -T), (X1, 0, 0), (X1, -D, 0)], METAL_D, (1, 0, 0))
    hx0, hy0, hx1, hy1 = hole
    poly(mb, [(hx0, hy0, -T), (hx0, hy1, -T), (hx0, hy1, 0), (hx0, hy0, 0)], METAL_D, (1, 0, 0))
    poly(mb, [(hx1, hy0, -T), (hx1, hy1, -T), (hx1, hy1, 0), (hx1, hy0, 0)], METAL_D, (-1, 0, 0))
    poly(mb, [(hx0, hy0, -T), (hx1, hy0, -T), (hx1, hy0, 0), (hx0, hy0, 0)], METAL_D, (0, 1, 0))
    poly(mb, [(hx0, hy1, -T), (hx1, hy1, -T), (hx1, hy1, 0), (hx0, hy1, 0)], METAL_D, (0, -1, 0))
    # stair: stringers, treads, handrail
    zl = lambda x: -drop * (xt - x) / run      # noqa: E731  tread line
    for ys in (sy0 + 0.025, sy1 - 0.025):
        xa, xb = xt + 0.02, xt - run * 0.93
        beam(mb, (xa, ys, zl(xa) - 0.12), (xb, ys, zl(xb) - 0.12), 0.05, 0.18, METAL_D)
    # treads: open ends are buried 1 cm in the stringers, and the x extent [x - 0.015, x + 0.15] keeps
    # the whole end inside the 0.18 stringer profile (the old [x - 0.13, x + 0.10] poked out above it)
    for k in range(1, n):
        x, z = xt - run * k / n, -drop * k / n
        box(mb, x - 0.015, sy0 + 0.04, z - 0.05, x + 0.15, sy1 - 0.04, z, METAL_D, skip=("-y", "+y"))
    xr0, xr1 = xt - 0.05, xt - run + 0.03
    beam(mb, (xr0, sy0 + 0.025, zl(xr0) + 0.9), (xr1, sy0 + 0.025, zl(xr1) + 0.9), 0.045, 0.05, METAL_D)
    box(mb, xr1 - 0.025, sy0, -drop, xr1 + 0.025, sy0 + 0.05, zl(xr1) + 0.92, METAL_D, skip=("-z",))
    # platform railing
    YF, XS = -1.17, 1.37
    box(mb, X0, YF - 0.03, 0.95, X1, YF + 0.03, 1.0, METAL_D)
    box(mb, X0 + 0.03, YF - 0.02, 0.06, X1 - 0.03, YF + 0.02, 0.1, METAL_D, skip=("-x", "+x"))
    for sx in (-1, 1):
        x = sx * XS
        box(mb, x - 0.03, YF - 0.03, 0.0, x + 0.03, YF + 0.03, 0.95, METAL_D, skip=("-z", "+z"))    # corner post
        box(mb, x - 0.03, YF + 0.03, 0.95, x + 0.03, 0.0, 1.0, METAL_D, skip=("-y", "+y"))
        box(mb, x - 0.02, YF + 0.03, 0.06, x + 0.02, 0.0, 0.1, METAL_D, skip=("-y", "+y"))
        for i in range(1, 4):
            y = YF + (0.0 - YF) * i / 4.0
            box(mb, x - 0.02, y - 0.02, 0.1, x + 0.02, y + 0.02, 0.95, METAL_D, skip=("-z", "+z"))
        # triangular wall bracket: horizontal arm under the deck + diagonal strut
        box(mb, sx * 1.34 - 0.025, -1.16, -T - 0.07, sx * 1.34 + 0.025, 0.0, -T, METAL_D, skip=("+y", "+z"))
        beam(mb, (sx * 1.34, -1.04, -T - 0.05), (sx * 1.34, -0.03, -0.85), 0.05, 0.06, METAL_D)
    for i in range(1, 10):
        x = X0 + (X1 - X0) * i / 10.0
        box(mb, x - 0.02, YF - 0.02, 0.1, x + 0.02, YF + 0.02, 0.95, METAL_D, skip=("-z", "+z"))
    K.add("KIT_FireEscape_3m", mb, FAM, "Facade", meta=dict(attach="facade", z0="platform top", stair_drop=drop))


def _downpipe(K):
    """Gutter downpipe 3 m at x = 0 (stackable) with two wall clamps."""
    mb = MeshBuilder()
    yc, r = -0.1, 0.055
    rod(mb, (0.0, yc, 0.0), (0.0, yc, 3.0), r, METAL, seg=8)
    for zc in (0.6, 2.4):
        box(mb, -0.075, yc - 0.075, zc - 0.035, 0.075, yc + 0.075, zc + 0.035, METAL)
        box(mb, -0.03, yc + 0.075, zc - 0.03, 0.03, 0.0, zc + 0.03, METAL, skip=("+y", "-y"))
    K.add("KIT_DownPipe_H3", mb, FAM, "Facade", meta=dict(attach="facade", z0="pipe bottom", height=3.0))


# ============================================================================ extras (not in the spec)
def _sign_lamp(K):
    """EXTRA: gooseneck lamp to light a fascia sign below it; z = 0 is the wall plate bottom."""
    mb = MeshBuilder()
    plate = MeshBuilder()
    box(plate, -0.07, -0.04, 0.0, 0.07, 0.0, 0.16, METAL_D, skip=("+y",))
    mb.extend(_safe_bevel(plate, 0.012))
    p0, p1, p2 = Vector((0.0, -0.02, 0.08)), Vector((0.0, -0.24, 0.3)), Vector((0.0, -0.55, 0.36))
    rod(mb, p0, p1, 0.022, METAL_D, seg=6)
    rod(mb, p1, p2, 0.022, METAL_D, seg=6)
    blob(mb, tuple(p1), 0.028, 0.028, 0.028, METAL_D, seg=6, rings=3)          # elbow knuckle
    d = Vector((0.0, 0.45, -1.0)).normalized()
    rod(mb, p2 - d * 0.04, p2 + d * 0.16, 0.05, METAL_D, seg=8, r1=0.11, cap_mats=(None, EMIT))
    K.add("KIT_Sign_Lamp", mb, FAM, "Signs", meta=dict(attach="facade", z0="plate bottom", extra=True))


def _downpipe_shoe(K):
    """EXTRA: kick-out shoe that ends a downpipe stack at the ground (0.6 m, same pipe axis as H3)."""
    mb = MeshBuilder()
    yc, r = -0.1, 0.055
    knee = Vector((0.0, yc, 0.24))
    rod(mb, (0.0, yc, 0.6), knee, r, METAL, seg=8, caps=(True, False))
    blob(mb, tuple(knee), r * 1.06, r * 1.06, r * 1.06, METAL, seg=8, rings=4)
    rod(mb, knee, (0.0, yc - 0.2, 0.06), r, METAL, seg=8, caps=(False, True))
    box(mb, -0.075, yc - 0.075, 0.43, 0.075, yc + 0.075, 0.5, METAL)
    box(mb, -0.03, yc + 0.075, 0.435, 0.03, 0.0, 0.495, METAL, skip=("+y", "-y"))
    K.add("KIT_DownPipe_Shoe", mb, FAM, "Facade", meta=dict(attach="facade", z0="ground", height=0.6, extra=True))


def _downpipe_head(K):
    """EXTRA: rain head (hopper) that tops a downpipe stack under the eave; z = 0 joins the pipe top."""
    mb = MeshBuilder()
    yc, r = -0.1, 0.055
    rod(mb, (0.0, yc, 0.0), (0.0, yc, 0.22), r, METAL, seg=8, caps=(True, False))
    bx, by, tx, ty, z0, z1, z2 = 0.09, -0.18, 0.17, -0.24, 0.2, 0.42, 0.5
    poly(mb, [(-bx, by, z0), (bx, by, z0), (tx, ty, z1), (-tx, ty, z1)], METAL, (0, -1, 0.3))
    for s in (-1, 1):
        poly(mb, [(s * bx, by, z0), (s * bx, 0, z0), (s * tx, 0, z1), (s * tx, ty, z1)], METAL, (s, 0, 0.3))
    poly(mb, [(-bx, by, z0), (bx, by, z0), (bx, 0, z0), (-bx, 0, z0)], METAL, (0, 0, -1))
    box(mb, -tx, ty, z1, tx, 0.0, z2, METAL, skip=("+y", "+z", "-z"))
    inner = (-tx + 0.035, ty + 0.035, tx - 0.035, -0.03)
    ring(mb, (-tx, ty, tx, 0.0), inner, (lambda u, v: (u, v, z2)), METAL, (0, 0, 1))
    rect(mb, inner, (lambda u, v: (u, v, z2)), METAL_D, (0, 0, 1))
    K.add("KIT_DownPipe_Head", mb, FAM, "Facade", meta=dict(attach="facade", z0="pipe top", height=0.5, extra=True))


PIECES = [_awning_3m, _awning_flat, _awning_window, _sign_board, _sign_blade, _sign_rooftop,
          _porch, _steps, _canopy_door, _balcony, _window_box, _fire_escape, _downpipe,
          _sign_lamp, _sign_blade_paw, _downpipe_shoe, _downpipe_head]


def build(K):
    for fn in PIECES:
        try:
            fn(K)
        except Exception:
            K.ERRORS[f"{FAM}:{fn.__name__}"] = traceback.format_exc()
            print(f"[kit] details piece {fn.__name__} FAILED\n{K.ERRORS[f'{FAM}:{fn.__name__}']}")
