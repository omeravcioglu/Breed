"""Kit family: PROPS - street furniture, utility clutter and stylized vehicles.

Spec: docs/KIT_SPEC.md ("props.py"). Categories: "Street", "Utility", "Vehicles".

Conventions used here
---------------------
* Origin = ground level (z = 0) at the bottom centre of the footprint; the piece front faces -Y.
* Pole pieces (StreetLight, TrafficLight, StreetSign, StopSign, ParkingMeter, UtilityPole):
  origin at the centre of the pole base.
  - StreetLight: arm + lamp head reach toward -Y (over the road). meta 'light_local' = lamp lens.
  - TrafficLight: mast arm reaches toward -X across the lanes, the 3-light head faces -Y.
    Stand it on the right-hand curb of the approach (approaching drivers look toward +Y).
* Vehicles (Car_Sedan, Car_Van, Truck_Box): the NOSE points to -Y (driving direction = piece
  front), length along Y, width along X, tyres touch z = 0.
  Car_Sedan 1.8 x 4.3 x 1.5, Car_Van 2.0 x 5.0 x 2.2, Truck_Box 2.3 x 6.5 x 3.2  (x * y * z).
* Container_6m lies along X: 6.1 (x) x 2.44 (y) x 2.6 (z), long side faces -Y, doors on +X.
* Recolour placeholders (citygen/kit RECOLOR_SLOTS):
  - M_Awning_Red: vehicle body, container body, cafe umbrella + kiosk awning stripes
    (alternating with the fixed M_Awning_Cream).
  - M_Sign_Accent: sign / poster faces (traffic cone shell, bus shelter poster, kiosk sign,
    truck cargo-box band).
  Everything else uses fixed palette colours.
* Round parts (lathes, tubes, wheels) are shaded smooth; edges sharper than 40 deg stay hard,
  so boxes and bevel chamfers stay crisp while poles / drums / tyres read round.
* Backface culling (Unity): pieces are closed or end inside closed parts. Decals that could show
  their rim at grazing angles are closed plates (plate_decal / side_plate: sedan side windows,
  trash-bin flaps) or flush split faces (inset_panels: CrateStack panels).
* Draw calls: <= 8 materials per piece (NewsStand and Truck_Box merged in the polish pass).

Extra pieces (not required by the spec, same conventions):
  KIT_StopSign (octagonal stop sign on a post), KIT_ParkingMeter, KIT_UtilityPole (9 m wooden
  power pole, crossarm along X, insulators + transformer can).
"""
import math

from mathutils import Euler, Matrix, Vector

from .. import facade as F
from ..geom2d import ensure_ccw
from ..meshutil import MeshBuilder

FAM = "props"
SMOOTH_DEG = 40.0

# ---------------------------------------------------------------- palette shortcuts
BODY = "M_Awning_Red"      # recolourable body (vehicles, container, umbrella stripes)
CREAM = "M_Awning_Cream"
SIGN = "M_Sign_Accent"     # recolourable sign / poster face
TIRE = "M_Hazard_Dark"
HUB = "M_Metal"
GLASS = "M_Glass"
GLASS_L = "M_Glass_Shop"
DARK = "M_Trim_Dark"
METAL = "M_Metal"
METAL_D = "M_Metal_Dark"
LIGHT = "M_Light_Emit"
TAIL = "M_Door_Red"
WOOD = "M_Wood_Light"
WOOD_D = "M_Fence_Wood"
WHITE = "M_Sign_Face"
HAZ = "M_Hazard"
HAZ_D = "M_Hazard_Dark"
GREEN_SIGN = "M_Awning_Green"


# ============================================================================ helpers
def _M(loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0)):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, "XYZ").to_matrix().to_4x4()


def put(mb, sub, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), bevel=0.0, angle=40.0):
    """Append *sub* (optionally chamfered) to *mb*, rotated (Euler XYZ) then moved to *loc*."""
    if bevel > 0:
        sub = F.bevelled(sub, bevel, angle)
    mb.extend(sub, matrix=_M(loc, rot))


def box(mb, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, skip=(), angle=40.0):
    s = MeshBuilder()
    s.box(x0, y0, z0, x1, y1, z1, mat, skip=skip)
    put(mb, s, bevel=bevel, angle=angle)


def cbox(mb, center, size, mat, rot=(0.0, 0.0, 0.0), bevel=0.0, skip=()):
    """Box of *size* centred at *center*, rotated (Euler XYZ, radians) about its own centre."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    s = MeshBuilder()
    s.box(-hx, -hy, -hz, hx, hy, hz, mat, skip=skip)
    put(mb, s, center, rot, bevel)


def newell(P):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def face_n(mb, pts, n, mat):
    """Planar polygon whose winding is fixed so its normal points along *n*."""
    P = [Vector(p) for p in pts]
    if newell(P).dot(Vector(n)) < 0:
        P.reverse()
    mb.face(P, mat)


def extrude(poly2d, c0, c1, cap_mat, side_mat, cap0=True, cap1=True):
    """Local prism: 2D polygon (a, b) extruded along c in [c0, c1].

    side_mat may be a callable (a2d, b2d) -> material, evaluated per outline edge.
    """
    s = MeshBuilder()
    P = ensure_ccw([(float(p[0]), float(p[1])) for p in poly2d])
    if cap1:
        s.tri_fill([P], c1, cap_mat, up=True)
    if cap0:
        s.tri_fill([P], c0, cap_mat, up=False)
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        m = side_mat(a, b) if callable(side_mat) else side_mat
        s.wall([a, b], c0, c1, m)
    return s


# (a, b, c) -> (x = c, y = a, z = b): profile drawn in the YZ plane, extruded along X
MX = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
# (a, b, c) -> (x = a, y = -c, z = b): profile drawn in the XZ plane, extruded along Y
MY = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def xprism(mb, prof_yz, x0, x1, cap_mat, side_mat=None, bevel=0.0, angle=40.0, loc=(0, 0, 0)):
    s = extrude(prof_yz, x0, x1, cap_mat, side_mat or cap_mat)
    if bevel > 0:
        s = F.bevelled(s, bevel, angle)
    mb.extend(s, matrix=Matrix.Translation(Vector(loc)) @ MX)


def yprism(mb, prof_xz, y0, y1, cap_mat, side_mat=None, bevel=0.0, angle=40.0, loc=(0, 0, 0)):
    s = extrude(prof_xz, -y1, -y0, cap_mat, side_mat or cap_mat)
    if bevel > 0:
        s = F.bevelled(s, bevel, angle)
    mb.extend(s, matrix=Matrix.Translation(Vector(loc)) @ MY)


def lathe(mb, prof, seg=10, center=(0.0, 0.0), mat=METAL, cap_top=True, cap_bottom=False,
          cap_mat=None, phase=0.0, matrix=None):
    """Surface of revolution about a vertical axis.

    prof: [(r, z) | (r, z, mat)] listed bottom -> top with the solid on the left of travel;
    each segment takes the material of its upper point.
    """
    cx, cy = center
    pts = [(float(p[0]), float(p[1]), p[2] if len(p) > 2 else mat) for p in prof]
    ang = [phase + 2 * math.pi * j / seg for j in range(seg)]
    rings = [[Vector((cx + r * math.cos(a), cy + r * math.sin(a), z)) for a in ang] for (r, z, _) in pts]
    s = MeshBuilder()
    E = 1e-6
    for i in range(len(pts) - 1):
        r0, r1, m = pts[i][0], pts[i + 1][0], pts[i + 1][2]
        if r0 < E and r1 < E:
            continue
        for j in range(seg):
            k = (j + 1) % seg
            A, B, C, D = rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]
            if r1 < E:
                s.face([A, B, D], m)
            elif r0 < E:
                s.face([A, C, D], m)
            else:
                s.face([A, B, C, D], m)
    if cap_top and pts[-1][0] > E:
        s.face(rings[-1], cap_mat or pts[-1][2])
    if cap_bottom and pts[0][0] > E:
        s.face(list(reversed(rings[0])), pts[0][2])
    mb.extend(s, matrix=matrix)
    return rings


def tube(mb, path, radii, mat, seg=6, cap0=False, cap1=False, phase=0.0):
    """Swept round tube along a 3D polyline (parallel-transport frames, mitred joints)."""
    P = [Vector(p) for p in path]
    n = len(P)
    R = list(radii) if isinstance(radii, (list, tuple)) else [radii] * n
    T = []
    for i in range(n):
        if i == 0:
            t = P[1] - P[0]
        elif i == n - 1:
            t = P[-1] - P[-2]
        else:
            t = (P[i] - P[i - 1]).normalized() + (P[i + 1] - P[i]).normalized()
        T.append(t.normalized())
    ref = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = (ref - ref.dot(T[0]) * T[0]).normalized()
    rings = []
    for i in range(n):
        N = (N - N.dot(T[i]) * T[i]).normalized()
        B = T[i].cross(N)
        k, sc = None, 1.0
        if 0 < i < n - 1:
            d0 = (P[i] - P[i - 1]).normalized()
            d1 = (P[i + 1] - P[i]).normalized()
            sc = 1.0 / max(d1.dot(T[i]), 0.35)
            kv = d1 - d0
            kv = kv - kv.dot(T[i]) * T[i]
            if kv.length > 1e-6:
                k = kv.normalized()
        ring = []
        for j in range(seg):
            a = phase + 2 * math.pi * j / seg
            o = (math.cos(a) * N + math.sin(a) * B) * R[i]
            if k is not None:
                o = o + (sc - 1.0) * o.dot(k) * k
            ring.append(P[i] + o)
        rings.append(ring)
    for i in range(n - 1):
        for j in range(seg):
            jj = (j + 1) % seg
            mb.face([rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]], mat)
    if cap1:
        mb.face(rings[-1], mat)
    if cap0:
        mb.face(list(reversed(rings[0])), mat)


def cyl_y(mb, cx, cz, y0, y1, r, mat, seg=8, cap_front=True, cap_back=False, cap_mat=None, phase=0.0):
    """Cylinder along Y from y0 (front, more negative) to y1. Front cap faces -Y."""
    s = MeshBuilder()
    s.cylinder(0.0, 0.0, 0.0, y1 - y0, r, mat, seg=seg, cap_top=cap_front, cap_bottom=cap_back, mat_cap=cap_mat)
    # Rx(+90) maps +z -> -y: local z in [0, L] -> y in [y1 - L, y1]
    mb.extend(s, matrix=Matrix.Translation((cx, y1, cz)) @ Matrix.Rotation(math.pi / 2, 4, "X")
              @ Matrix.Rotation(phase, 4, "Z"))


def cyl_x(mb, cy, cz, x0, x1, r, mat, seg=8, cap_out=True, cap_in=False, cap_mat=None):
    """Cylinder along X between x0 and x1 (|x1| > |x0|); the 'out' cap is at x1."""
    s = MeshBuilder()
    L = abs(x1 - x0)
    s.cylinder(0.0, 0.0, 0.0, L, r, mat, seg=seg, cap_top=cap_out, cap_bottom=cap_in, mat_cap=cap_mat)
    sgn = 1.0 if x1 >= x0 else -1.0
    mb.extend(s, matrix=Matrix.Translation((x0, cy, cz)) @ Matrix.Rotation(sgn * math.pi / 2, 4, "Y"))


def slant_decal(mb, p, q, x0, x1, t0, t1, inside, mat, d=0.008, depth=0.0):
    """Quad lying on the face of an X-extruded prism through the profile edge p->q (y, z).
    depth > 0 closes it into a plate sunk *depth* below the face (no rim sliver when culled)."""
    P, Q = Vector((0.0, p[0], p[1])), Vector((0.0, q[0], q[1]))
    e = Q - P
    n = Vector((0.0, -e.z, e.y)).normalized()
    if ((P + Q) / 2 - Vector((0.0, inside[0], inside[1]))).dot(n) < 0:
        n = -n
    a = P + e * t0 + n * d
    b = P + e * t1 + n * d
    pts = [(x0, a.y, a.z), (x1, a.y, a.z), (x1, b.y, b.z), (x0, b.y, b.z)]
    if depth > 0:
        plate_decal(mb, pts, n, d + depth, mat)
    else:
        face_n(mb, pts, n, mat)


def side_decal(mb, poly_yz, x, mat):
    """Flat polygon on the plane x (normal +X if x > 0 else -X)."""
    face_n(mb, [(x, p[0], p[1]) for p in poly_yz], (1.0 if x > 0 else -1.0, 0.0, 0.0), mat)


def facet_decal(mb, quad, mat, shrink=0.75, off=0.006, depth=0.0):
    """Decal on a planar facet. depth > 0 closes it into a plate sunk *depth* into the surface."""
    P = [Vector(p) for p in quad]
    c = sum(P, Vector()) / len(P)
    n = newell(P).normalized()
    pts = [c + (p - c) * shrink + n * off for p in P]
    if depth > 0:
        plate_decal(mb, pts, n, off + depth, mat)
    else:
        mb.face(pts, mat)


def plate_decal(mb, pts, n, depth, mat, side_mat=None):
    """Closed decal: the planar polygon *pts* (already standing proud of a surface, outward normal
    *n*) plus side faces running *depth* back along -n into the surface it sits on. Replaces a
    floating one-sided decal whose rim shows as a 1-2 px sliver / crack with backface culling."""
    P = [Vector(p) for p in pts]
    n = Vector(n).normalized()
    face_n(mb, P, n, mat)
    c = sum(P, Vector()) / len(P)
    back = -n * depth
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        if (b - a).length < 1e-7:
            continue
        s = (b - a).cross(n)
        if s.dot((a + b) / 2 - c) < 0:
            s = -s
        face_n(mb, [a, b, b + back, a + back], s, side_mat or mat)


def side_plate(mb, poly_yz, x, depth, mat):
    """side_decal() closed into a plate: outer face on the plane x, sides sunk *depth* toward x=0."""
    plate_decal(mb, [(x, p[0], p[1]) for p in poly_yz], (1.0 if x > 0 else -1.0, 0.0, 0.0), depth, mat)


def inset_panels(src, plane, half, keys, mat):
    """Copy MeshBuilder *src* (an axis-aligned, bevelled box centred on the origin) and split each
    flat face lying on +-plane whose key ('-y', '+x', ...) is in *keys* into a frame ring (keeps
    its material) around a FLUSH centre panel [-half, half]^2 in *mat* (no floating decal)."""
    out = MeshBuilder()
    for f, mi in zip(src.faces, src.fmat):
        Q = [src.verts[i].copy() for i in f]
        m = src.mats[mi]
        nrm = newell(Q)
        key = None
        if nrm.length > 1e-9:
            nrm.normalize()
            ax = max(range(3), key=lambda i: abs(nrm[i]))
            sg = 1.0 if nrm[ax] > 0 else -1.0
            if abs(abs(nrm[ax]) - 1.0) < 1e-4 and all(abs(q[ax] - sg * plane) < 1e-5 for q in Q):
                key = ("+" if sg > 0 else "-") + "xyz"[ax]
        if key is None or key not in keys:
            out.face(Q, m)
            continue

        def pc(q):
            p = q.copy()
            for i in range(3):
                if i != ax:
                    p[i] = half if q[i] > 0 else -half
            return p
        P = [pc(q) for q in Q]
        for i in range(len(Q)):
            j = (i + 1) % len(Q)
            if (P[i] - P[j]).length < 1e-7:
                face_n(out, [Q[i], Q[j], P[i]], nrm, m)
            else:
                face_n(out, [Q[i], Q[j], P[j], P[i]], nrm, m)
        C = []
        for p in P:
            if not C or (p - C[-1]).length > 1e-7:
                C.append(p)
        if len(C) > 1 and (C[0] - C[-1]).length < 1e-7:
            C.pop()
        face_n(out, C, nrm, mat)
    return out


def clip_half(poly, f):
    """Sutherland-Hodgman: keep the part of 2D polygon where f(p) >= 0 (f linear)."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def arch_pts(cy, cz, R, zb, n=6):
    """Wheel-arch arc (y, z) from its -Y foot over the top to its +Y foot, feet at height zb."""
    s = math.asin(max(-1.0, min(1.0, (zb - cz) / R)))
    t0, t1 = math.pi - s, s
    return [(cy + R * math.cos(t0 + (t1 - t0) * k / n), cz + R * math.sin(t0 + (t1 - t0) * k / n))
            for k in range(n + 1)]


def arch_side_mat(arches, zb, body=BODY, well=DARK):
    """Outline-edge material: dark wheel wells, body colour elsewhere."""
    def f(a, b):
        my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if mz > zb + 1e-3:
            for (cy, cz, R) in arches:
                if abs(math.hypot(my - cy, mz - cz) - R) < 0.06 * R:
                    return well
        return body
    return f


def wheel(mb, x_out, y, r, w, side, seg=10, hub=HUB, tire=TIRE):
    """Chunky tyre + hub disc, axis along X; outer face at |x| = x_out on the given side."""
    s = MeshBuilder()
    ch = min(0.05, w * 0.25)
    lathe(s, [(r, 0.0, tire), (r, w - ch, tire), (r - ch, w, tire), (r * 0.6, w, tire)],
          seg=seg, cap_top=True, cap_bottom=True, cap_mat=hub)
    x_in = x_out - w
    if side > 0:
        M = Matrix.Translation((x_in, y, r)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    else:
        M = Matrix.Translation((-x_in, y, r)) @ Matrix.Rotation(-math.pi / 2, 4, "Y")
    mb.extend(s, matrix=M)


def _recenter(mb):
    """Shift *mb* so its XY footprint is centred on the origin (z untouched)."""
    xs = [v.x for v in mb.verts]
    ys = [v.y for v in mb.verts]
    dx, dy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    mb.transform(Matrix.Translation((-dx, -dy, 0.0)))


def _add(K, name, mb, cat, meta=None, smooth=True):
    meta = dict(meta or {})
    meta.setdefault("forward", "-Y")
    o = K.add(name, mb, FAM, cat, meta=meta)
    if smooth:
        me = o.data
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(SMOOTH_DEG))
    return o


# ============================================================================ STREET
def street_light(K):
    mb = MeshBuilder()
    lathe(mb, [(0.2, 0.0), (0.2, 0.1), (0.15, 0.17), (0.12, 0.5), (0.09, 0.56)], seg=8, mat=METAL_D)
    arm_z = 5.88
    path = [(0, 0, 0.5), (0, 0, arm_z - 0.5), (0, -0.067, arm_z - 0.25), (0, -0.25, arm_z - 0.067),
            (0, -0.5, arm_z), (0, -1.45, arm_z)]
    tube(mb, path, [0.085, 0.07, 0.066, 0.063, 0.06, 0.055], METAL_D, seg=8)
    # decorative collar
    lathe(mb, [(0.078, 2.45, METAL_D), (0.105, 2.55), (0.078, 2.65)], seg=8, mat=METAL_D, cap_top=False)
    # cobra-head lamp housing + glowing lens
    head = [(-1.30, arm_z - 0.04), (-1.42, arm_z + 0.08), (-1.82, arm_z + 0.12), (-2.02, arm_z + 0.06),
            (-2.0, arm_z - 0.04), (-1.38, arm_z - 0.06)]
    xprism(mb, head, -0.19, 0.19, METAL_D, bevel=0.03)
    box(mb, -0.13, -1.92, arm_z - 0.105, 0.13, -1.45, arm_z - 0.045, LIGHT, skip=("+z",))
    _add(K, "KIT_StreetLight", mb, "Street",
         meta=dict(height=6.0, light_local=[0.0, -1.68, round(arm_z - 0.11, 3)]))


def traffic_light(K):
    mb = MeshBuilder()
    lathe(mb, [(0.22, 0.0), (0.22, 0.1), (0.13, 0.22), (0.105, 0.56)], seg=8, mat=METAL_D)
    tube(mb, [(0, 0, 0.5), (0, 0, 5.6)], [0.1, 0.085], METAL_D, seg=8)
    lathe(mb, [(0.095, 5.58), (0.0, 5.7)], seg=8, mat=METAL_D)
    # mast arm toward -X
    tube(mb, [(0.0, 0, 5.15), (-4.3, 0, 5.4)], [0.075, 0.05], METAL_D, seg=8, cap1=True)
    # signal head at x = -3.0
    hx = -3.0
    box(mb, hx - 0.035, -0.035, 5.08, hx + 0.035, 0.035, 5.32, METAL_D, skip=("-z", "+z"))
    box(mb, hx - 0.19, -0.14, 4.0, hx + 0.19, 0.14, 5.1, HAZ_D, bevel=0.03)
    box(mb, hx - 0.3, 0.14, 3.9, hx + 0.3, 0.18, 5.2, HAZ, bevel=0.012)
    for zc, m in ((4.83, TAIL), (4.55, "M_Foliage_Autumn"), (4.27, GREEN_SIGN)):
        cyl_y(mb, hx, zc, -0.17, -0.13, 0.1, m, seg=8, phase=math.pi / 8)
        box(mb, hx - 0.13, -0.36, zc + 0.1, hx + 0.13, -0.14, zc + 0.14, HAZ_D, skip=("+y",))
    # pedestrian push-button box
    box(mb, -0.07, -0.19, 1.0, 0.07, -0.08, 1.22, HAZ, skip=("+y",))
    # street-name blade on the arm
    sub = MeshBuilder()
    sub.box(-0.5, -0.02, -0.12, 0.5, 0.02, 0.12, GREEN_SIGN)
    for sg in (-1, 1):
        y = sg * 0.024
        for (a, b) in ((-0.38, -0.2), (-0.15, 0.08), (0.13, 0.36)):
            face_n(sub, [(a, y, -0.035), (b, y, -0.035), (b, y, 0.04), (a, y, 0.04)], (0, sg, 0), WHITE)
    put(mb, sub, (-1.75, 0.0, 5.1))
    _add(K, "KIT_TrafficLight", mb, "Street", meta=dict(height=5.72, arm_reach=4.3, head_x=hx))


def _street_blade(zc, L=0.94, Hh=0.22, T=0.04):
    sub = MeshBuilder()
    sub.box(-L / 2, -T / 2, zc - Hh / 2, L / 2, T / 2, zc + Hh / 2, WHITE)
    for sg in (-1, 1):
        y = sg * (T / 2 + 0.003)
        face_n(sub, [(-L / 2 + 0.03, y, zc - Hh / 2 + 0.025), (L / 2 - 0.03, y, zc - Hh / 2 + 0.025),
                     (L / 2 - 0.03, y, zc + Hh / 2 - 0.025), (-L / 2 + 0.03, y, zc + Hh / 2 - 0.025)],
               (0, sg, 0), GREEN_SIGN)
        yt = sg * (T / 2 + 0.006)
        for (a, b) in ((-0.36, -0.25), (-0.21, -0.03), (0.01, 0.11), (0.15, 0.36)):
            face_n(sub, [(a, yt, zc - 0.035), (b, yt, zc - 0.035), (b, yt, zc + 0.04), (a, yt, zc + 0.04)],
                   (0, sg, 0), WHITE)
    return sub


def street_sign(K):
    mb = MeshBuilder()
    box(mb, -0.035, -0.035, 0.0, 0.035, 0.035, 3.06, METAL, bevel=0.01, skip=("-z",))
    box(mb, -0.05, -0.05, 3.06, 0.05, 0.05, 3.1, METAL_D)       # closed cap (its underside shows from below)
    put(mb, _street_blade(2.68))
    put(mb, _street_blade(2.92), rot=(0, 0, math.pi / 2))
    _add(K, "KIT_StreetSign", mb, "Street", meta=dict(height=3.1))


def stop_sign(K):
    mb = MeshBuilder()
    box(mb, -0.035, -0.035, 0.0, 0.035, 0.035, 2.3, METAL, bevel=0.01, skip=("-z",))
    zc, r = 2.3, 0.38
    ph = math.pi / 8
    cyl_y(mb, 0.0, zc, -0.065, -0.035, r, TAIL, seg=8, cap_front=True, cap_back=False, phase=ph)
    face_n(mb, [(r * math.cos(ph + 2 * math.pi * i / 8), -0.035, zc + r * math.sin(ph + 2 * math.pi * i / 8))
                for i in range(8)], (0, 1, 0), METAL)   # bare metal back
    # white border ring + text bar on the front
    y = -0.068
    for i in range(8):
        a0, a1 = ph + 2 * math.pi * i / 8, ph + 2 * math.pi * (i + 1) / 8
        ro, ri = r - 0.025, r - 0.07
        pts = [(ro * math.cos(a0), y, zc + ro * math.sin(a0)), (ro * math.cos(a1), y, zc + ro * math.sin(a1)),
               (ri * math.cos(a1), y, zc + ri * math.sin(a1)), (ri * math.cos(a0), y, zc + ri * math.sin(a0))]
        face_n(mb, pts, (0, -1, 0), WHITE)
    for (a, b) in ((-0.2, -0.11), (-0.08, 0.0), (0.03, 0.11), (0.14, 0.21)):
        face_n(mb, [(a, y, zc - 0.07), (b, y, zc - 0.07), (b, y, zc + 0.07), (a, y, zc + 0.07)], (0, -1, 0), WHITE)
    _add(K, "KIT_StopSign", mb, "Street", meta=dict(height=2.68, extra=True))


def bench(K):
    mb = MeshBuilder()
    frame = [(-0.30, 0.0), (-0.21, 0.0), (-0.19, 0.36), (0.12, 0.36), (0.16, 0.0), (0.25, 0.0), (0.22, 0.40),
             (0.30, 0.86), (0.22, 0.87), (0.14, 0.45), (-0.18, 0.45), (-0.20, 0.62), (-0.29, 0.62)]
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.74, sx * 0.81))
        xprism(mb, frame, xa, xb, METAL_D)
        xa, xb = sorted((sx * 0.725, sx * 0.825))
        box(mb, xa, -0.34, 0.62, xb, 0.19, 0.675, WOOD)
    for (y0, y1) in ((-0.31, -0.20), (-0.165, -0.055), (-0.02, 0.09)):
        box(mb, -0.9, y0, 0.45, 0.9, y1, 0.5, WOOD, bevel=0.015, skip=("-z",))
    tilt = -math.atan2(0.08, 0.42)
    for zc in (0.58, 0.76):
        yc = 0.14 + 0.08 * (zc - 0.45) / 0.42 - 0.027
        cbox(mb, (0.0, yc, zc), (1.8, 0.04, 0.12), WOOD, rot=(tilt, 0, 0), bevel=0.015)
    _add(K, "KIT_Bench", mb, "Street", meta=dict(seat_h=0.5, length=1.8))


def trash_bin(K):
    mb = MeshBuilder()
    BIN = "M_Dumpster"
    ph = math.radians(15)
    prof = [(0.25, 0.0, BIN), (0.28, 0.05, BIN), (0.28, 0.80, BIN), (0.305, 0.82, METAL_D),
            (0.305, 0.88, METAL_D), (0.27, 0.90, METAL_D), (0.2, 0.98, METAL_D), (0.1, 1.02, METAL_D),
            (0.0, 1.03, METAL_D)]
    lathe(mb, prof, seg=12, phase=ph)
    # vertical rib bands on the body
    for k in range(6):
        a = ph + math.pi / 6 + k * math.pi / 3
        c = Vector((math.cos(a), math.sin(a), 0.0))
        cbox(mb, (c.x * 0.285, c.y * 0.285, 0.43), (0.022, 0.07, 0.7), METAL_D, rot=(0, 0, a),
             skip=("-x", "-z"))
    # push-flap openings front (-Y) and back (+Y) on the dome
    for (ja, jb) in ((8, 9), (2, 3)):
        a0, a1 = ph + ja * math.pi / 6, ph + jb * math.pi / 6
        quad = [(0.27 * math.cos(a0), 0.27 * math.sin(a0), 0.9), (0.27 * math.cos(a1), 0.27 * math.sin(a1), 0.9),
                (0.2 * math.cos(a1), 0.2 * math.sin(a1), 0.98), (0.2 * math.cos(a0), 0.2 * math.sin(a0), 0.98)]
        facet_decal(mb, quad, HAZ_D, shrink=0.8, off=0.004, depth=0.01)
    _add(K, "KIT_TrashBin", mb, "Street", meta=dict(height=1.03))


def hydrant(K):
    mb = MeshBuilder()
    R = TAIL
    prof = [(0.17, 0.0, R), (0.17, 0.06, R), (0.125, 0.085, R), (0.115, 0.5, R), (0.15, 0.53, R),
            (0.15, 0.58, R), (0.115, 0.6, R), (0.09, 0.68, R), (0.045, 0.72, R)]
    lathe(mb, prof, seg=10, cap_top=True, cap_mat=METAL)
    s = MeshBuilder()
    s.cylinder(0, 0, 0.71, 0.79, 0.04, METAL, seg=5)
    put(mb, s)
    # nozzle caps closed on the inner side too (the 8-gon nozzle does not fill the 6-gon cap rim)
    for sg in (-1, 1):
        cyl_x(mb, 0.0, 0.42, sg * 0.09, sg * 0.19, 0.045, R, seg=8, cap_out=False)
        cyl_x(mb, 0.0, 0.42, sg * 0.185, sg * 0.225, 0.052, METAL, seg=6, cap_in=True)
    cyl_y(mb, 0.0, 0.4, -0.2, -0.08, 0.065, R, seg=8, cap_front=False)
    cyl_y(mb, 0.0, 0.4, -0.245, -0.195, 0.072, METAL, seg=6, cap_back=True)
    _add(K, "KIT_Hydrant", mb, "Street", meta=dict(height=0.79))


def mailbox(K):
    mb = MeshBuilder()
    BLUE = "M_Awning_Blue"
    prof = [(-0.27, 0.22), (0.27, 0.22)]
    for i in range(9):
        t = math.pi * i / 8
        prof.append((0.27 * math.cos(t), 0.95 + 0.27 * math.sin(t)))
    yprism(mb, prof, -0.24, 0.24, BLUE, bevel=0.025)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(mb, sx * 0.2 - 0.03, sy * 0.17 - 0.03, 0.0, sx * 0.2 + 0.03, sy * 0.17 + 0.03, 0.24, METAL_D,
                skip=("-z", "+z"))
    # pull-down chute + handle, info plate
    cbox(mb, (0.0, -0.255, 1.0), (0.36, 0.04, 0.17), BLUE, rot=(math.radians(14), 0, 0), bevel=0.012)
    cbox(mb, (0.0, -0.29, 1.07), (0.18, 0.035, 0.035), METAL, rot=(math.radians(14), 0, 0))
    face_n(mb, [(-0.12, -0.2455, 0.5), (0.12, -0.2455, 0.5), (0.12, -0.2455, 0.68), (-0.12, -0.2455, 0.68)],
           (0, -1, 0), WHITE)
    _add(K, "KIT_Mailbox", mb, "Street", meta=dict(height=1.22))


def bollard(K):
    mb = MeshBuilder()
    M = METAL_D
    prof = [(0.12, 0.0, M), (0.12, 0.04, M), (0.1, 0.06, M), (0.1, 0.66, M), (0.1, 0.78, HAZ), (0.1, 0.86, M),
            (0.07, 0.93, M), (0.0, 0.95, M)]
    lathe(mb, prof, seg=8)
    _add(K, "KIT_Bollard", mb, "Street", meta=dict(height=0.95))


def bus_stop(K):
    mb = MeshBuilder()
    box(mb, -1.75, -0.85, 0.0, 1.75, 0.75, 0.06, "M_Concrete", bevel=0.02, skip=("-z",))
    for (x, y, ztop) in ((-1.6, 0.62, 2.40), (1.6, 0.62, 2.40), (-1.6, -0.55, 2.46), (1.6, -0.55, 2.46)):
        box(mb, x - 0.04, y - 0.04, 0.06, x + 0.04, y + 0.04, ztop, METAL_D, skip=("-z", "+z"))
    # back glass wall + rails
    box(mb, -1.56, 0.6, 0.32, 1.56, 0.64, 2.12, GLASS_L)
    for (z0, z1) in ((0.26, 0.32), (2.12, 2.18)):
        box(mb, -1.6, 0.585, z0, 1.6, 0.655, z1, METAL_D)
    # left glass side
    box(mb, -1.62, -0.51, 0.32, -1.58, 0.58, 2.12, GLASS_L)
    for (z0, z1) in ((0.26, 0.32), (2.12, 2.18)):
        box(mb, -1.635, -0.55, z0, -1.565, 0.62, z1, METAL_D, skip=("-y", "+y"))
    # right side advertising panel (poster faces recolourable via 'sign')
    box(mb, 1.55, -0.48, 0.28, 1.67, 0.56, 2.1, METAL_D)
    side_decal(mb, [(-0.42, 0.38), (0.5, 0.38), (0.5, 2.0), (-0.42, 2.0)], 1.674, SIGN)
    face_n(mb, [(1.546, y, z) for (y, z) in ((-0.42, 0.38), (0.5, 0.38), (0.5, 2.0), (-0.42, 2.0))], (-1, 0, 0), SIGN)
    # gently curved roof
    ys = [-0.98, -0.53, -0.08, 0.37, 0.82]
    top = [(y, 2.56 - 0.16 * ((y + 0.08) / 0.9) ** 2) for y in ys]
    prof = top + [(y, z - 0.07) for (y, z) in reversed(top)]
    xprism(mb, prof, -1.75, 1.75, METAL_D, bevel=0.025)
    # bench
    box(mb, -1.1, 0.22, 0.42, 1.1, 0.56, 0.48, WOOD, bevel=0.02, skip=("-z",))
    for x in (-0.88, 0.88):
        box(mb, x - 0.035, 0.3, 0.06, x + 0.035, 0.5, 0.42, METAL_D, skip=("-z", "+z"))
    # bus-stop roundel on a short mast above the roof
    box(mb, -1.535, -0.585, 2.45, -1.465, -0.515, 2.85, METAL_D, skip=("-z",))
    cyl_y(mb, -1.5, 3.0, -0.57, -0.53, 0.2, "M_Awning_Blue", seg=10, cap_front=True, cap_back=True)
    for (y, sg) in ((-0.574, -1), (-0.526, 1)):
        pts = [(-1.5 + 0.12 * math.cos(2 * math.pi * i / 10), y, 3.0 + 0.12 * math.sin(2 * math.pi * i / 10))
               for i in range(10)]
        face_n(mb, pts, (0, sg, 0), WHITE)
    _add(K, "KIT_BusStop", mb, "Street", meta=dict(width=3.5, open_side="-Y"))


def bike_rack(K):
    mb = MeshBuilder()
    RACK = "M_Door_Teal"
    for x in (-0.75, 0.0, 0.75):
        r = 0.35
        path = [(x, -r, 0.0), (x, -r, 0.6)]
        for deg in (150, 120, 90, 60, 30):
            a = math.radians(deg)
            path.append((x, r * math.cos(a), 0.6 + r * math.sin(a)))
        path += [(x, r, 0.6), (x, r, 0.0)]
        tube(mb, path, 0.035, RACK, seg=6)
    for y in (-0.35, 0.35):
        box(mb, -1.0, y - 0.035, 0.0, 1.0, y + 0.035, 0.03, METAL_D, skip=("-z",))
    _add(K, "KIT_BikeRack", mb, "Street", meta=dict(slots=4))


def _bistro_chair():
    s = MeshBuilder()
    s.box(-0.2, -0.2, 0.44, 0.2, 0.2, 0.49, WOOD)
    for sx in (-1, 1):
        s.box(sx * 0.17 - 0.0175, -0.1875, 0.0, sx * 0.17 + 0.0175, -0.1525, 0.44, METAL_D, skip=("-z", "+z"))
        s.box(sx * 0.17 - 0.0175, 0.1525, 0.0, sx * 0.17 + 0.0175, 0.1875, 0.88, METAL_D, skip=("-z",))
    s.box(-0.2, 0.15, 0.62, 0.2, 0.19, 0.86, WOOD)
    return s


def cafe_table(K):
    mb = MeshBuilder()
    prof = [(0.24, 0.0, METAL_D), (0.24, 0.03, METAL_D), (0.05, 0.07, METAL_D), (0.04, 0.71, METAL_D),
            (0.38, 0.72, WOOD), (0.38, 0.76, WOOD)]
    lathe(mb, prof, seg=10)
    s = MeshBuilder()
    s.cylinder(0, 0, 0.76, 2.46, 0.025, METAL_D, seg=6, cap_top=False)
    put(mb, s)
    # umbrella: 8 gores alternating red (recolour) / cream, double sided, with valance
    n, R, Ru, zr, za = 8, 1.08, 1.065, 2.12, 2.48
    zv = 1.99
    apex, apex_u = Vector((0, 0, za)), Vector((0, 0, za - 0.03))
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        m = BODY if i % 2 == 0 else CREAM
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        o0, o1 = Vector((R * c0, R * s0, zr)), Vector((R * c1, R * s1, zr))
        u0, u1 = Vector((Ru * c0, Ru * s0, zr - 0.025)), Vector((Ru * c1, Ru * s1, zr - 0.025))
        mb.face([apex, o0, o1], m)
        mb.face([apex_u, u1, u0], m)
        b0, b1 = Vector((R * c0, R * s0, zv)), Vector((R * c1, R * s1, zv))
        bi0, bi1 = Vector((Ru * c0, Ru * s0, zv)), Vector((Ru * c1, Ru * s1, zv))
        mb.face([b0, b1, o1, o0], m)          # valance outside
        mb.face([bi1, bi0, u0, u1], m)        # valance inside
        mb.face([bi0, bi1, b1, b0], m)        # valance hem (faces down)
    s = MeshBuilder()
    s.cylinder(0, 0, za - 0.02, za + 0.08, 0.035, METAL_D, seg=6)
    put(mb, s)
    put(mb, _bistro_chair(), (0.68, 0.0, 0.0), (0, 0, -math.pi / 2))
    put(mb, _bistro_chair(), (-0.68, 0.0, 0.0), (0, 0, math.pi / 2))
    _add(K, "KIT_CafeTable", mb, "Street", meta=dict(umbrella_d=2.16))


def news_stand(K):
    """Kiosk. Draw-call budget (polish pass): 8 materials = body teal, dark trim (base, sign board,
    service door, interior), cream (roof, awning stripes, sign letters, papers), wood counter,
    awning red (recolour; also some magazines), sign accent (recolour), magazine yellow + blue."""
    mb = MeshBuilder()
    BODYK = "M_Door_Teal"
    MAG_Y, MAG_B = "M_Awning_Yellow", "M_Awning_Blue"
    x0, x1, yf, yb, zb, zt = -0.95, 0.95, -0.6, 0.65, 0.15, 2.35
    hole = (-0.72, 1.05, 0.72, 2.0)
    shell = MeshBuilder()
    F.panel(shell, x0, x1, zb, zt, [hole], BODYK, y=yf, facing=-1)
    side = [(yf, zb), (yb, zb), (yb, zt), (yf, zt), (yf, hole[3]), (yf, hole[1])]
    side_decal(shell, side, x1, BODYK)
    side_decal(shell, side, x0, BODYK)
    face_n(shell, [(x0, yb, zb), (x1, yb, zb), (x1, yb, zt), (x0, yb, zt)], (0, 1, 0), BODYK)
    mb.extend(F.bevelled(shell, 0.03))
    # service door on the back (dark panel + brass handle)
    face_n(mb, [(0.15, yb + 0.004, zb), (0.75, yb + 0.004, zb), (0.75, yb + 0.004, 2.1), (0.15, yb + 0.004, 2.1)],
           (0, 1, 0), DARK)
    box(mb, 0.24, yb, 1.0, 0.3, yb + 0.05, 1.06, MAG_Y, skip=("-y",))
    # base skirt: closed on top (the 2 cm ledge around the shell was open -> crack from above)
    box(mb, -0.97, -0.62, 0.0, 0.97, 0.67, zb, DARK, skip=("-z",))
    # window interior
    d = 0.32
    F.reveal(mb, hole, d, BODYK, y=yf)
    yi = yf + d
    face_n(mb, [(hole[0], yi, hole[1]), (hole[2], yi, hole[1]), (hole[2], yi, hole[3]), (hole[0], yi, hole[3])],
           (0, -1, 0), DARK)
    mags = [MAG_Y, MAG_B, BODY, MAG_B, CREAM, MAG_Y]
    for row, zc in enumerate((1.3, 1.68)):
        for i in range(3):
            xc = -0.42 + 0.42 * i + (0.06 if row else 0.0)
            m = mags[(i + 3 * row) % len(mags)]
            face_n(mb, [(xc - 0.13, yi - 0.004, zc - 0.15), (xc + 0.13, yi - 0.004, zc - 0.15),
                        (xc + 0.13, yi - 0.004, zc + 0.15), (xc - 0.13, yi - 0.004, zc + 0.15)], (0, -1, 0), m)
    # counter
    box(mb, -0.82, -0.82, 1.0, 0.82, -0.32, 1.07, WOOD, bevel=0.02)
    # newspaper rack under the counter
    for zc, yc in ((0.42, -0.69), (0.72, -0.69)):
        cbox(mb, (0.0, yc, zc), (1.5, 0.16, 0.05), WOOD, rot=(math.radians(-20), 0, 0))
        for i, m in enumerate((CREAM, MAG_Y, MAG_B)):
            xc = -0.45 + 0.45 * i
            cbox(mb, (xc, yc - 0.01, zc + 0.11), (0.3, 0.025, 0.2), m, rot=(math.radians(-20), 0, 0),
                 skip=("+y", "-z"))
    # roof + roof sign (sign face recolourable)
    box(mb, -1.05, -0.74, zt, 1.05, 0.77, zt + 0.13, CREAM, bevel=0.03)
    box(mb, -0.85, -0.6, zt + 0.13, 0.85, -0.48, zt + 0.5, DARK, bevel=0.02, skip=("-z",))
    for (y, sg) in ((-0.606, -1), (-0.474, 1)):
        face_n(mb, [(-0.78, y, zt + 0.19), (0.78, y, zt + 0.19), (0.78, y, zt + 0.44), (-0.78, y, zt + 0.44)],
               (0, sg, 0), SIGN)
        for (a, b) in (((-0.55, -0.3), (-0.24, 0.1), (0.16, 0.55)) if sg < 0 else ()):
            face_n(mb, [(a, y + sg * 0.003, zt + 0.27), (b, y + sg * 0.003, zt + 0.27),
                        (b, y + sg * 0.003, zt + 0.36), (a, y + sg * 0.003, zt + 0.36)], (0, sg, 0), CREAM)
    # striped awning over the service window
    ya, za, yo, zo, zv = yf, 2.33, -1.02, 2.05, 1.93
    xs = [-0.86 + 1.72 * i / 6 for i in range(7)]
    nrm = Vector((0, -(za - zo), (ya - yo))).normalized()   # up/out
    for i in range(6):
        m = BODY if i % 2 == 0 else CREAM
        a, b = xs[i], xs[i + 1]
        face_n(mb, [(a, ya, za), (b, ya, za), (b, yo, zo), (a, yo, zo)], nrm, m)
        face_n(mb, [(a, ya, za - 0.025), (b, ya, za - 0.025), (b, yo + 0.02, zo - 0.025), (a, yo + 0.02, zo - 0.025)],
               -nrm, m)
        face_n(mb, [(a, yo, zv), (b, yo, zv), (b, yo, zo), (a, yo, zo)], (0, -1, 0), m)
        face_n(mb, [(a, yo + 0.02, zv), (b, yo + 0.02, zv), (b, yo + 0.02, zo - 0.025), (a, yo + 0.02, zo - 0.025)],
               (0, 1, 0), m)
        face_n(mb, [(a, yo, zv), (b, yo, zv), (b, yo + 0.02, zv), (a, yo + 0.02, zv)], (0, 0, -1), m)
    for x, sg in ((xs[0], -1), (xs[-1], 1)):
        cheek = [(x, ya, za), (x, yo, zo), (x, yo, zv), (x, ya, za - 0.12)]
        face_n(mb, cheek, (sg, 0, 0), BODY)
        face_n(mb, cheek, (-sg, 0, 0), BODY)
    _add(K, "KIT_NewsStand", mb, "Street", meta=dict(height=2.98))


def parking_meter(K):
    mb = MeshBuilder()
    box(mb, -0.04, -0.04, 0.0, 0.04, 0.04, 1.05, METAL_D, bevel=0.01, skip=("-z",))
    box(mb, -0.12, -0.1, 1.0, 0.12, 0.1, 1.38, METAL, bevel=0.025)
    # dome: closed underneath and sunk 2 cm into the bevelled head (no crack at the head's chamfer)
    lathe(mb, [(0.12, 1.36, METAL), (0.12, 1.385, METAL), (0.1, 1.45, METAL), (0.0, 1.48, METAL)], seg=8,
          phase=math.pi / 8, cap_bottom=True)
    # display window + coin plate: closed 4 mm plates (their rim is seen edge-on from the side)
    plate_decal(mb, [(-0.08, -0.104, 1.2), (0.08, -0.104, 1.2), (0.08, -0.104, 1.33), (-0.08, -0.104, 1.33)],
                (0, -1, 0), 0.012, GLASS_L)
    plate_decal(mb, [(-0.05, -0.104, 1.06), (0.05, -0.104, 1.06), (0.05, -0.104, 1.14), (-0.05, -0.104, 1.14)],
                (0, -1, 0), 0.012, HAZ)
    _add(K, "KIT_ParkingMeter", mb, "Street", meta=dict(height=1.48, extra=True))


# ============================================================================ UTILITY
def dumpster(K):
    mb = MeshBuilder()
    G = "M_Dumpster"
    body = [(-0.42, 0.14), (0.52, 0.14), (0.52, 1.12), (-0.56, 1.12)]
    xprism(mb, body, -0.92, 0.92, G, bevel=0.03)
    box(mb, -0.95, -0.6, 1.04, 0.95, 0.56, 1.14, G, bevel=0.025)
    lid = [(-0.6, 1.14), (0.56, 1.14), (0.56, 1.302), (-0.6, 1.20)]
    xprism(mb, lid, -0.93, -0.015, HAZ_D, bevel=0.02)
    xprism(mb, lid, 0.015, 0.93, HAZ_D, bevel=0.02)
    box(mb, -0.93, 0.54, 1.1, 0.93, 0.6, 1.18, METAL_D)
    for sg in (-1, 1):
        xa, xb = sorted((sg * 0.9, sg * 1.0))
        box(mb, xa, -0.4, 0.6, xb, 0.42, 0.78, G, bevel=0.02, skip=("-x" if sg > 0 else "+x",))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(mb, sx * 0.78 - 0.06, sy * 0.33 - 0.06, 0.0, sx * 0.78 + 0.06, sy * 0.33 + 0.06, 0.14, METAL_D,
                skip=("+z",))
    slant_decal(mb, (-0.42, 0.14), (-0.56, 1.12), -0.32, 0.32, 0.5, 0.75, (0.0, 0.6), WHITE, d=0.004)
    _add(K, "KIT_Dumpster", mb, "Utility", meta=dict(size=[2.0, 1.2, 1.3]))


def _crate(s, style="framed", faces=("-y", "+x", "+y", "-x", "+z"), bottom=True):
    """Crate of edge *s*: local origin at its bottom centre."""
    h = s / 2
    m = 0.12 * s
    FR, PN = "M_Crate", WOOD_D
    rots = {"-y": (0, 0, 0), "+x": (0, 0, math.pi / 2), "+y": (0, 0, math.pi), "-x": (0, 0, -math.pi / 2),
            "+z": (-math.pi / 2, 0, 0), "-z": (math.pi / 2, 0, 0)}
    a = s - 2 * m
    wb = m * 0.85
    Lb = a * math.sqrt(2) - wb * 1.05
    out = MeshBuilder()
    if style == "framed":
        d = 0.045 * s
        hole = (-h + m, -h + m, h - m, h - m)
        shell = MeshBuilder()
        det = MeshBuilder()
        for k, key in enumerate(("-y", "+x", "+y", "-x", "+z")):
            f = MeshBuilder()
            F.panel(f, -h, h, -h, h, [hole], FR, y=-h, facing=-1)
            shell.extend(f, matrix=_M(rot=rots[key]))
            g = MeshBuilder()
            F.reveal(g, hole, d, FR, y=-h)
            yi = -h + d
            g.face([(hole[0], yi, hole[1]), (hole[2], yi, hole[1]), (hole[2], yi, hole[3]), (hole[0], yi, hole[3])], PN)
            tb = d - 0.008
            cbox(g, (0.0, yi - tb / 2, 0.0), (Lb, tb, wb), FR, rot=(0, (1 if k % 2 else -1) * math.pi / 4, 0),
                 skip=("+y",))
            det.extend(g, matrix=_M(rot=rots[key]))
        if bottom:
            pts = [(-h, -h), (-h + m, -h), (h - m, -h), (h, -h), (h, -h + m), (h, h - m), (h, h), (h - m, h),
                   (-h + m, h), (-h, h), (-h, h - m), (-h, -h + m)]
            f = MeshBuilder()
            face_n(f, [(x, -h, z) for (x, z) in pts], (0, -1, 0), FR)
            shell.extend(f, matrix=_M(rot=rots["-z"]))
        out.extend(F.bevelled(shell, 0.025 * s))
        out.extend(det)
    else:   # "lite": bevelled cube with FLUSH darker panels (split faces, no floating decals,
        #     so no rim slivers with backface culling) + raised diagonal braces
        b = MeshBuilder()
        b.box(-h, -h, -h, h, h, h, FR, skip=() if bottom else ("-z",))
        out.extend(inset_panels(F.bevelled(b, 0.03 * s), h, h - m, set(faces), PN))
        for k, key in enumerate(faces):
            g = MeshBuilder()
            tb = 0.03 * s
            cbox(g, (0.0, -h - tb / 2, 0.0), (Lb, tb, wb), FR, rot=(0, (1 if k % 2 else -1) * math.pi / 4, 0),
                 skip=("+y",))
            out.extend(g, matrix=_M(rot=rots[key]))
    out.transform(Matrix.Translation((0, 0, h)))
    return out


def crate(K):
    mb = MeshBuilder()
    mb.extend(_crate(1.0, "framed"))
    _add(K, "KIT_Crate", mb, "Utility", meta=dict(size=1.0))


def crate_stack(K):
    mb = MeshBuilder()
    # the big crate's top carries the small crate: plain lid there (no panel / brace under it)
    put(mb, _crate(1.0, "lite", faces=("-y", "+x", "+y", "-x"), bottom=False), (-0.5, 0.04, 0.0), (0, 0, 0))
    put(mb, _crate(0.82, "lite", bottom=False), (0.47, -0.06, 0.0), (0, 0, math.radians(9)))
    put(mb, _crate(0.72, "lite", bottom=False), (-0.46, 0.06, 1.0), (0, 0, math.radians(-13)))
    _recenter(mb)
    _add(K, "KIT_CrateStack", mb, "Utility", meta=dict(crates=3))


def pallet(K):
    mb = MeshBuilder()
    for x in (-0.53, 0.0, 0.53):
        box(mb, x - 0.07, -0.5, 0.0, x + 0.07, 0.5, 0.022, WOOD)
    a, b = 0.022, 0.122
    prof = [(-0.6, a), (-0.4, a), (-0.37, a + 0.04), (-0.16, a + 0.04), (-0.13, a), (0.13, a), (0.16, a + 0.04),
            (0.37, a + 0.04), (0.4, a), (0.6, a), (0.6, b), (-0.6, b)]
    for y in (-0.46, 0.0, 0.46):
        yprism(mb, prof, y - 0.025, y + 0.025, WOOD_D)
    for i in range(6):
        x = -0.535 + 1.07 * i / 5
        box(mb, x - 0.065, -0.5, b, x + 0.065, 0.5, b + 0.025, WOOD)
    _add(K, "KIT_Pallet", mb, "Utility", meta=dict(size=[1.2, 1.0, 0.147]))


def barrel(K):
    mb = MeshBuilder()
    Bc = "M_Awning_Blue"
    prof = [(0.27, 0.0, Bc), (0.29, 0.03, Bc), (0.29, 0.25, Bc), (0.305, 0.28, Bc), (0.29, 0.31, Bc),
            (0.29, 0.57, Bc), (0.305, 0.60, Bc), (0.29, 0.63, Bc), (0.29, 0.86, Bc), (0.3, 0.88, Bc),
            (0.275, 0.885, Bc), (0.265, 0.865, METAL_D)]
    lathe(mb, prof, seg=12, cap_top=True, cap_bottom=True, cap_mat=METAL_D)   # closed: barrels get tipped over
    s = MeshBuilder()
    s.cylinder(0.14, 0.08, 0.86, 0.885, 0.04, METAL, seg=6)
    put(mb, s)
    _add(K, "KIT_Barrel", mb, "Utility", meta=dict(height=0.885))


def container(K):
    mb = MeshBuilder()
    L, D, H = 6.1, 2.44, 2.6
    hx, hy = L / 2, D / 2
    m, d = 0.14, 0.07
    shell = MeshBuilder()
    sides = [(hx, hy, (0, 0, 0), "long"), (hx, hy, (0, 0, math.pi), "long"),
             (hy, hx, (0, 0, -math.pi / 2), "end"), (hy, hx, (0, 0, math.pi / 2), "doors")]
    for (w, e, rot, kind) in sides:
        hole = (-w + m, m, w - m, H - m)
        f = MeshBuilder()
        F.panel(f, -w, w, 0.0, H, [hole], BODY, y=-e, facing=-1)
        shell.extend(f, matrix=_M(rot=rot))
        g = MeshBuilder()
        F.reveal(g, hole, d, BODY, y=-e)
        yp = -e + d
        g.face([(hole[0], yp, hole[1]), (hole[2], yp, hole[1]), (hole[2], yp, hole[3]), (hole[0], yp, hole[3])], BODY)
        if kind in ("long", "end"):
            n = 9 if kind == "long" else 3
            pitch = (hole[2] - hole[0]) / n
            bw, tw, hr = 0.56 * pitch, 0.34 * pitch, 0.045
            yo = yp - hr
            z0, z1 = hole[1], hole[3]
            for k in range(n):
                c = hole[0] + pitch * (k + 0.5)
                xl0, xl1, xr1, xr0 = c - bw / 2, c - tw / 2, c + tw / 2, c + bw / 2
                face_n(g, [(xl1, yo, z0), (xr1, yo, z0), (xr1, yo, z1), (xl1, yo, z1)], (0, -1, 0), BODY)
                face_n(g, [(xl0, yp, z0), (xl1, yo, z0), (xl1, yo, z1), (xl0, yp, z1)], (-1, -1, 0), BODY)
                face_n(g, [(xr1, yo, z0), (xr0, yp, z0), (xr0, yp, z1), (xr1, yo, z1)], (1, -1, 0), BODY)
        else:
            box(g, -0.012, yp - 0.015, hole[1], 0.012, yp, hole[3], DARK, skip=("+y",))
            for xb in (-0.8, -0.28, 0.28, 0.8):
                box(g, xb - 0.025, yp - 0.06, hole[1] + 0.08, xb + 0.025, yp, hole[3] - 0.08, METAL, skip=("+y",))
            face_n(g, [(0.45, yp - 0.002, 2.0), (0.95, yp - 0.002, 2.0), (0.95, yp - 0.002, 2.25),
                       (0.45, yp - 0.002, 2.25)], (0, -1, 0), WHITE)
        mb.extend(g, matrix=_M(rot=rot))
    ring = [(-hx, -hy), (-hx + m, -hy), (hx - m, -hy), (hx, -hy), (hx, -hy + m), (hx, hy - m), (hx, hy),
            (hx - m, hy), (-hx + m, hy), (-hx, hy), (-hx, hy - m), (-hx, -hy + m)]
    face_n(shell, [(x, y, H) for (x, y) in ring], (0, 0, 1), BODY)
    face_n(shell, [(x, y, 0.0) for (x, y) in ring], (0, 0, -1), BODY)   # closed bottom: stacked/hung/tipped
    mb.extend(F.bevelled(shell, 0.04))
    _add(K, "KIT_Container_6m", mb, "Utility", meta=dict(size=[6.1, 2.44, 2.6], doors="+X"))


def traffic_cone(K):
    mb = MeshBuilder()
    box(mb, -0.19, -0.19, 0.0, 0.19, 0.19, 0.04, HAZ_D, bevel=0.015, skip=("-z",))
    O, W = SIGN, WHITE
    prof = [(0.15, 0.035, O), (0.12, 0.2, O), (0.105, 0.28, W), (0.085, 0.38, O), (0.072, 0.45, W), (0.04, 0.66, O),
            (0.03, 0.70, O)]
    lathe(mb, prof, seg=10)
    _add(K, "KIT_TrafficCone", mb, "Utility", meta=dict(height=0.7))


def _stripe_board(mb, x0, x1, z0, z1, y0, y1, w=0.24, mats=(HAZ, HAZ_D)):
    """Board with 45-degree alternating stripes on front/back and matching edge faces."""
    h = z1 - z0
    rect = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    k0 = int(math.floor((x0 - h) / w)) - 1
    k1 = int(math.ceil(x1 / w)) + 1
    E = 1e-6
    for k in range(k0, k1):
        c = k * w
        poly = clip_half(rect, lambda p, c=c: (p[0] - (p[1] - z0)) - c)
        poly = clip_half(poly, lambda p, c=c: c + w - (p[0] - (p[1] - z0)))
        if len(poly) < 3:
            continue
        area = 0.0
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            area += a[0] * b[1] - b[0] * a[1]
        if abs(area) < 1e-6:
            continue
        m = mats[k % 2]
        face_n(mb, [(p[0], y0, p[1]) for p in poly], (0, -1, 0), m)
        face_n(mb, [(p[0], y1, p[1]) for p in poly], (0, 1, 0), m)
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            for (val, idx, n) in ((z1, 1, (0, 0, 1)), (z0, 1, (0, 0, -1)), (x0, 0, (-1, 0, 0)), (x1, 0, (1, 0, 0))):
                if abs(a[idx] - val) < E and abs(b[idx] - val) < E and (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 > E:
                    face_n(mb, [(a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1]), (a[0], y1, a[1])], n, m)


def barrier(K):
    mb = MeshBuilder()
    for x in (-0.8, 0.8):
        box(mb, x - 0.035, -0.035, 0.0, x + 0.035, 0.035, 1.2, METAL, bevel=0.01, skip=("-z",))
        box(mb, x - 0.05, -0.35, 0.0, x + 0.05, 0.35, 0.07, HAZ_D, bevel=0.015, skip=("-z",))
    for (z0, z1) in ((0.62, 0.82), (0.92, 1.12)):
        _stripe_board(mb, -1.0, 1.0, z0, z1, -0.075, -0.035)
    # amber warning lamp on the right post
    box(mb, 0.74, -0.06, 1.2, 0.86, 0.06, 1.26, HAZ_D, skip=("-z",))
    s = MeshBuilder()
    s.cylinder(0.8, 0.0, 1.26, 1.36, 0.055, LIGHT, seg=8)
    put(mb, s)
    _add(K, "KIT_Barrier", mb, "Utility", meta=dict(width=2.0))


def utility_pole(K):
    mb = MeshBuilder()
    PW = "M_Trim_Wood"
    tube(mb, [(0, 0, 0.0), (0, 0, 9.0)], [0.15, 0.11], PW, seg=8, cap1=True)
    box(mb, -1.2, -0.06, 8.35, 1.2, 0.06, 8.5, PW, bevel=0.02)
    for sx in (-1, 1):
        tube(mb, [(sx * 0.05, -0.08, 7.75), (sx * 0.75, -0.08, 8.36)], 0.025, METAL_D, seg=4)
    for x in (-1.0, 0.0, 1.0):
        lathe(mb, [(0.05, 8.5), (0.06, 8.56), (0.035, 8.62), (0.045, 8.66), (0.0, 8.7)],
              seg=6, center=(x, 0.0), mat=GLASS_L, cap_top=False)
    # transformer can on the -Y side
    lathe(mb, [(0.26, 6.55, METAL), (0.27, 6.6), (0.27, 7.35), (0.24, 7.42), (0.0, 7.45)],
          seg=10, center=(0.0, -0.4), mat=METAL, cap_top=False, cap_bottom=True)
    box(mb, -0.08, -0.2, 6.75, 0.08, -0.1, 7.2, METAL_D, skip=("+y",))
    _add(K, "KIT_UtilityPole", mb, "Utility", meta=dict(height=9.0, extra=True, wire_z=8.66))


# ============================================================================ VEHICLES
def car_sedan(K):
    mb = MeshBuilder()
    zb, wr, wy, R = 0.22, 0.35, 1.35, 0.45
    prof = ([(-1.98, zb)] + arch_pts(-wy, wr, R, zb) + arch_pts(wy, wr, R, zb) +
            [(1.98, zb), (2.08, 0.33), (2.08, 0.8), (2.0, 0.92), (1.35, 0.95), (-0.98, 0.95), (-1.95, 0.84),
             (-2.08, 0.72), (-2.08, 0.33)])
    xprism(mb, prof, -0.9, 0.9, BODY, side_mat=arch_side_mat([(-wy, wr, R), (wy, wr, R)], zb), bevel=0.06)
    cab = [(-0.98, 0.9), (1.42, 0.9), (0.98, 1.46), (0.85, 1.5), (-0.18, 1.5), (-0.3, 1.46)]
    xprism(mb, cab, -0.74, 0.74, BODY, bevel=0.05)
    box(mb, -0.6, -1.82, 0.17, 0.6, 1.82, 0.8, DARK, skip=("+z",))
    # glazing
    slant_decal(mb, (-0.98, 0.9), (-0.3, 1.46), -0.6, 0.6, 0.17, 0.9, (0.3, 1.2), GLASS, depth=0.01)
    slant_decal(mb, (1.42, 0.9), (0.98, 1.46), -0.58, 0.58, 0.15, 0.88, (0.3, 1.2), GLASS, depth=0.01)
    # side windows: closed 8 mm plates sunk into the cab side (x = +-0.74), so their rim does not
    # show as a sliver / crack from above or from the front with backface culling
    for x in (0.748, -0.748):
        side_plate(mb, [(-0.749, 1.0), (0.2, 1.0), (0.2, 1.42), (-0.239, 1.42)], x, 0.018, GLASS)
        side_plate(mb, [(0.3, 1.0), (1.252, 1.0), (0.922, 1.42), (0.3, 1.42)], x, 0.018, GLASS)
    # lights, grille, bumpers, plate, mirrors
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.5, sx * 0.8))
        box(mb, xa, -2.11, 0.56, xb, -2.05, 0.68, LIGHT, skip=("+y",))
        xa, xb = sorted((sx * 0.55, sx * 0.82))
        box(mb, xa, 2.05, 0.6, xb, 2.11, 0.74, TAIL, skip=("-y",))
        xa, xb = sorted((sx * 0.75, sx * 0.9))
        box(mb, xa, -0.86, 0.97, xb, -0.72, 1.1, BODY, bevel=0.015, skip=("-z",))
    box(mb, -0.38, -2.1, 0.42, 0.38, -2.05, 0.6, DARK, skip=("+y",))
    box(mb, -0.87, -2.15, 0.24, 0.87, -1.97, 0.44, DARK, bevel=0.04)
    box(mb, -0.87, 1.97, 0.24, 0.87, 2.15, 0.44, DARK, bevel=0.04)
    face_n(mb, [(-0.18, 2.086, 0.47), (0.18, 2.086, 0.47), (0.18, 2.086, 0.59), (-0.18, 2.086, 0.59)], (0, 1, 0), WHITE)
    for sx in (-1, 1):
        for y in (-wy, wy):
            wheel(mb, 0.86, y, wr, 0.24, sx)
    _add(K, "KIT_Car_Sedan", mb, "Vehicles",
         meta=dict(size=[1.8, 4.3, 1.5], nose="-Y", wheelbase=2 * wy, wheel_r=wr, recolor="awning"))


def car_van(K):
    mb = MeshBuilder()
    zb, wr = 0.27, 0.38
    fy, ry, R = -1.6, 1.65, 0.48
    prof = ([(-2.34, zb)] + arch_pts(fy, wr, R, zb) + arch_pts(ry, wr, R, zb) +
            [(2.34, zb), (2.44, 0.38), (2.44, 2.06), (2.36, 2.2), (-1.0, 2.2), (-1.18, 2.14), (-1.82, 1.22),
             (-2.36, 1.09), (-2.44, 0.99), (-2.44, 0.38)])
    xprism(mb, prof, -0.995, 0.995, BODY, side_mat=arch_side_mat([(fy, wr, R), (ry, wr, R)], zb), bevel=0.06)
    box(mb, -0.68, -2.1, 0.2, 0.68, 2.15, 0.9, DARK, skip=("+z",))
    # glazing
    slant_decal(mb, (-1.82, 1.22), (-1.18, 2.14), -0.86, 0.86, 0.08, 0.9, (0.0, 1.2), GLASS, depth=0.01)
    for x in (0.9965, -0.9965):
        side_decal(mb, [(-1.609, 1.38), (-0.8, 1.38), (-0.8, 1.98), (-1.191, 1.98)], x, GLASS)
        side_decal(mb, [(-0.62, 1.38), (0.55, 1.38), (0.55, 1.98), (-0.62, 1.98)], x, GLASS)
        # cream belt stripe
        side_decal(mb, [(-2.25, 0.9), (2.3, 0.9), (2.3, 1.04), (-2.25, 1.04)], x, CREAM)
    for (a, b) in ((-0.86, -0.07), (0.07, 0.86)):
        face_n(mb, [(a, 2.441, 1.45), (b, 2.441, 1.45), (b, 2.441, 1.98), (a, 2.441, 1.98)], (0, 1, 0), GLASS)
    face_n(mb, [(-0.012, 2.442, 0.45), (0.012, 2.442, 0.45), (0.012, 2.442, 2.05), (-0.012, 2.442, 2.05)], (0, 1, 0),
           DARK)
    # lights, grille, bumpers, mirrors
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.55, sx * 0.86))
        box(mb, xa, -2.47, 0.78, xb, -2.41, 0.92, LIGHT, skip=("+y",))
        xa, xb = sorted((sx * 0.8, sx * 0.93))
        box(mb, xa, 2.41, 0.62, xb, 2.47, 1.2, TAIL, skip=("-y",))
        xa, xb = sorted((sx * 0.88, sx * 0.995))
        box(mb, xa, -1.72, 1.42, xb, -1.58, 1.62, DARK, bevel=0.02)
    box(mb, -0.42, -2.47, 0.6, 0.42, -2.41, 0.86, DARK, skip=("+y",))
    box(mb, -0.97, -2.5, 0.3, 0.97, -2.32, 0.52, DARK, bevel=0.04)
    box(mb, -0.97, 2.32, 0.3, 0.97, 2.5, 0.52, DARK, bevel=0.04)
    for sx in (-1, 1):
        for y in (fy, ry):
            wheel(mb, 0.95, y, wr, 0.26, sx)
    _add(K, "KIT_Car_Van", mb, "Vehicles",
         meta=dict(size=[2.0, 5.0, 2.2], nose="-Y", wheelbase=ry - fy, wheel_r=wr, recolor="awning"))


def truck_box(K):
    """Box truck. Draw-call budget (polish pass): 8 materials = body (recolour), sign band
    (recolour), white box, one near-black for tyres + every dark part (chassis, wells, bumpers,
    grille, mirrors, box sill, door seams), metal (hubs, tank, roll-up door), glass, headlight /
    cab marker glow (M_Light_Emit), tail lights."""
    mb = MeshBuilder()
    DK = TIRE        # single dark material for the truck (merged Trim_Dark / Metal_Dark / tyres)
    zb, wr, fy, ry, R = 0.4, 0.45, -2.3, 1.95, 0.56
    cab = ([(-3.08, zb)] + arch_pts(fy, wr, R, zb) +
           [(-1.3, zb), (-1.3, 2.62), (-1.42, 2.75), (-2.25, 2.75), (-2.4, 2.66), (-2.72, 1.72), (-3.1, 1.6),
            (-3.16, 1.5), (-3.16, 0.5)])
    xprism(mb, cab, -1.0, 1.0, BODY, side_mat=arch_side_mat([(fy, wr, R)], zb, well=DK), bevel=0.06)
    box(mb, -0.72, -3.0, 0.3, 0.72, -1.35, 1.2, DK, skip=("+z",))
    # cargo box (fixed white, recolourable sign band)
    BOX = "M_Wall_White"
    box(mb, -1.13, -1.2, 0.98, 1.13, 3.18, 3.2, BOX, bevel=0.04)
    box(mb, -1.15, -1.22, 0.92, 1.15, 3.2, 1.0, DK)
    for x in (1.131, -1.131):
        side_decal(mb, [(-0.9, 1.75), (2.9, 1.75), (2.9, 2.75), (-0.9, 2.75)], x, SIGN)
    face_n(mb, [(-0.92, 3.181, 1.08), (0.92, 3.181, 1.08), (0.92, 3.181, 3.05), (-0.92, 3.181, 3.05)], (0, 1, 0),
           METAL)
    for z in (1.55, 2.05, 2.55):
        box(mb, -0.92, 3.18, z - 0.025, 0.92, 3.2, z + 0.025, BOX, skip=("-y",))
    # chassis, tank, mud flaps, bumpers
    box(mb, -0.45, -2.9, 0.55, 0.45, 3.0, 0.98, DK, skip=("+z",))
    cyl_y(mb, -0.72, 0.68, -1.25, -0.55, 0.2, METAL, seg=8, cap_front=True, cap_back=True)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.72, sx * 1.08))
        box(mb, xa, 2.5, 0.2, xb, 2.53, 0.92, DK)
    box(mb, -1.08, -3.25, 0.38, 1.08, -3.1, 0.66, DK, bevel=0.035)
    box(mb, -1.0, 3.0, 0.5, 1.0, 3.25, 0.68, DK)
    # cab glazing, lights, grille, marker lights, mirrors
    slant_decal(mb, (-2.4, 2.66), (-2.72, 1.72), -0.86, 0.86, 0.08, 0.9, (-1.8, 1.6), GLASS)
    for x in (1.001, -1.001):
        side_decal(mb, [(-2.593, 1.8), (-1.5, 1.8), (-1.5, 2.45), (-2.3715, 2.45)], x, GLASS)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.6, sx * 0.9))
        box(mb, xa, -3.19, 1.0, xb, -3.13, 1.2, LIGHT, skip=("+y",))
        xa, xb = sorted((sx * 0.92, sx * 1.1))
        box(mb, xa, 3.18, 1.06, xb, 3.22, 1.3, TAIL, skip=("-y",))
        xa, xb = sorted((sx * 1.0, sx * 1.13))
        box(mb, xa, -2.62, 1.75, xb, -2.5, 2.15, DK, bevel=0.02)
    box(mb, -0.5, -3.19, 0.72, 0.5, -3.13, 1.45, DK, skip=("+y",))
    for x in (-0.3, 0.0, 0.3):     # cab roof clearance markers (glow, merged with the headlights)
        box(mb, x - 0.06, -2.2, 2.74, x + 0.06, -2.1, 2.8, LIGHT, skip=("-z",))
    for sx in (-1, 1):
        wheel(mb, 0.98, fy, wr, 0.28, sx, tire=DK)
        wheel(mb, 1.1, ry, wr, 0.38, sx, tire=DK)
    _add(K, "KIT_Truck_Box", mb, "Vehicles",
         meta=dict(size=[2.3, 6.5, 3.2], nose="-Y", wheelbase=ry - fy, wheel_r=wr, recolor="awning,sign"))


# ============================================================================ build
def build(K):
    # Street
    street_light(K)
    traffic_light(K)
    street_sign(K)
    bench(K)
    trash_bin(K)
    hydrant(K)
    mailbox(K)
    bollard(K)
    bus_stop(K)
    bike_rack(K)
    cafe_table(K)
    news_stand(K)
    # Utility
    dumpster(K)
    crate(K)
    crate_stack(K)
    pallet(K)
    barrel(K)
    container(K)
    traffic_cone(K)
    barrier(K)
    # Vehicles
    car_sedan(K)
    car_van(K)
    truck_box(K)
    # Extras
    stop_sign(K)
    parking_meter(K)
    utility_pole(K)
