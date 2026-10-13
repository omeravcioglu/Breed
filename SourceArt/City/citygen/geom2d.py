"""2D geometry helpers: splines, polylines, polygons, spatial hashing.

Pure-python + mathutils so it runs inside Blender with no extra dependencies.
"""
import math
from mathutils import Vector


def V(p):
    return Vector((float(p[0]), float(p[1])))


# ----------------------------------------------------------------------------- splines
def catmull_rom(points, step=1.0, alpha=0.5, closed=False):
    """Centripetal Catmull-Rom spline through *points*.

    Returns (samples, ctrl_idx) where ctrl_idx[i] is the sample index of control point i.
    The curve passes exactly through every control point.
    """
    P = [V(p) for p in points]
    n = len(P)
    if n == 1:
        return [P[0].copy()], [0]
    if closed:
        ext = [P[-1]] + P + [P[0], P[1]]
        segs = n
    else:
        ext = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
        segs = n - 1
    out, idx = [], []
    for i in range(segs):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        idx.append(len(out))
        seglen = (p2 - p1).length
        m = max(1, int(math.ceil(seglen / step)))
        t0 = 0.0
        t1 = t0 + max((p1 - p0).length, 1e-4) ** alpha
        t2 = t1 + max((p2 - p1).length, 1e-4) ** alpha
        t3 = t2 + max((p3 - p2).length, 1e-4) ** alpha
        for k in range(m):
            t = t1 + (t2 - t1) * k / m
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    if not closed:
        idx.append(len(out))
        out.append(P[-1].copy())
    return out, idx


# ----------------------------------------------------------------------------- polylines
class Polyline:
    """Arc-length parameterised 2D polyline."""

    def __init__(self, pts):
        clean = []
        for p in pts:
            v = V(p)
            if not clean or (v - clean[-1]).length > 1e-5:
                clean.append(v)
        self.pts = clean
        self.cum = [0.0]
        for i in range(1, len(clean)):
            self.cum.append(self.cum[-1] + (clean[i] - clean[i - 1]).length)
        self.length = self.cum[-1]

    def _seg(self, s):
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        return lo

    def pos(self, s):
        if len(self.pts) == 1:
            return self.pts[0].copy()
        s = min(max(s, 0.0), self.length)
        i = self._seg(s)
        i = min(i, len(self.pts) - 2)
        seg = self.cum[i + 1] - self.cum[i]
        t = 0.0 if seg < 1e-9 else (s - self.cum[i]) / seg
        return self.pts[i].lerp(self.pts[i + 1], t)

    def tangent(self, s, h=1.0):
        a = self.pos(max(0.0, s - h))
        b = self.pos(min(self.length, s + h))
        d = b - a
        if d.length < 1e-9:
            return Vector((1.0, 0.0))
        return d.normalized()

    def stations(self, s0, s1, step):
        """Evenly spaced arc-length stations between s0 and s1 (inclusive)."""
        if s1 <= s0:
            return [s0]
        n = max(1, int(math.ceil((s1 - s0) / step)))
        return [s0 + (s1 - s0) * k / n for k in range(n + 1)]

    def reversed(self):
        return Polyline(list(reversed(self.pts)))

    def offset(self, d, s0=0.0, s1=None, step=2.0):
        """Points offset to the LEFT by d (negative = right)."""
        s1 = self.length if s1 is None else s1
        out = []
        for s in self.stations(s0, s1, step):
            p = self.pos(s)
            t = self.tangent(s)
            out.append(p + left_normal(t) * d)
        return out


def left_normal(t):
    return Vector((-t.y, t.x))


def right_normal(t):
    return Vector((t.y, -t.x))


# ----------------------------------------------------------------------------- lines / segments
def line_intersect(p, d, q, e):
    """Intersect lines p + d*s and q + e*u. Returns (s, u) or None if parallel."""
    den = d.x * e.y - d.y * e.x
    if abs(den) < 1e-9:
        return None
    w = q - p
    s = (w.x * e.y - w.y * e.x) / den
    u = (w.x * d.y - w.y * d.x) / den
    return s, u


def seg_intersect(a, b, c, d):
    """True if segments ab and cd properly intersect (2D)."""
    def orient(p, q, r):
        return (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x)
    o1, o2 = orient(a, b, c), orient(a, b, d)
    o3, o4 = orient(c, d, a), orient(c, d, b)
    return (o1 * o2 < 0) and (o3 * o4 < 0)


def dist_point_seg(p, a, b):
    ab = b - a
    L2 = ab.length_squared
    if L2 < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


def angle_of(v):
    return math.atan2(v.y, v.x)


def ccw_angle(a, b):
    """CCW angle from direction a to direction b, in (0, 2pi]."""
    d = angle_of(b) - angle_of(a)
    while d <= 1e-9:
        d += 2 * math.pi
    while d > 2 * math.pi:
        d -= 2 * math.pi
    return d


def arc_points(center, r, a0, a1, ccw=True, seg_len=1.0):
    """Points on a circular arc from angle a0 to a1 (inclusive)."""
    if ccw:
        while a1 < a0:
            a1 += 2 * math.pi
    else:
        while a1 > a0:
            a1 -= 2 * math.pi
    sweep = abs(a1 - a0)
    n = max(2, int(math.ceil(sweep * r / seg_len)))
    return [center + Vector((math.cos(a0 + (a1 - a0) * k / n), math.sin(a0 + (a1 - a0) * k / n))) * r
            for k in range(n + 1)]


# ----------------------------------------------------------------------------- polygons
def poly_area(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        a += p[0] * q[1] - q[0] * p[1]
    return 0.5 * a


def ensure_ccw(poly):
    return poly if poly_area(poly) >= 0 else list(reversed(poly))


def point_in_poly(p, poly):
    x, y = p[0], p[1]
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i][0], poly[i][1]
        xj, yj = poly[j][0], poly[j][1]
        if (yi > y) != (yj > y):
            xint = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xint:
                inside = not inside
        j = i
    return inside


def polys_overlap(a, b):
    """General simple-polygon overlap test (edge crossing or containment)."""
    A = [V(p) for p in a]
    B = [V(p) for p in b]
    if not bbox_overlap(bbox(A), bbox(B)):
        return False
    for i in range(len(A)):
        a0, a1 = A[i], A[(i + 1) % len(A)]
        for j in range(len(B)):
            if seg_intersect(a0, a1, B[j], B[(j + 1) % len(B)]):
                return True
    return point_in_poly(A[0], B) or point_in_poly(B[0], A)


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_overlap(a, b, pad=0.0):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def centroid(poly):
    a = poly_area(poly)
    if abs(a) < 1e-9:
        n = len(poly)
        return Vector((sum(p[0] for p in poly) / n, sum(p[1] for p in poly) / n))
    cx = cy = 0.0
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        c = p[0] * q[1] - q[0] * p[1]
        cx += (p[0] + q[0]) * c
        cy += (p[1] + q[1]) * c
    return Vector((cx / (6 * a), cy / (6 * a)))


def rect_corners(center, fwd, width, depth, front_at_center=False):
    """Oriented rectangle. *fwd* is the unit direction the front faces.

    If front_at_center, *center* is the midpoint of the front edge and the rect extends
    backwards (opposite fwd) by depth.
    """
    f = V(fwd).normalized()
    r = Vector((f.y, -f.x))  # right of facing direction
    c = V(center)
    if front_at_center:
        c = c - f * (depth * 0.5)
    hw, hd = width * 0.5, depth * 0.5
    return [c + r * hw + f * hd, c - r * hw + f * hd, c - r * hw - f * hd, c + r * hw - f * hd]


def blob_polygon(center, radii, seg_len=2.0, rot=0.0):
    """Smooth closed blob: radii sampled evenly around the circle, interpolated periodically."""
    c = V(center)
    n = len(radii)
    ctrl = []
    for i, r in enumerate(radii):
        a = rot + 2 * math.pi * i / n
        ctrl.append(c + Vector((math.cos(a), math.sin(a))) * r)
    pts, _ = catmull_rom(ctrl, step=seg_len, closed=True)
    return pts


def offset_polygon_radial(poly, center, d):
    """Cheap inset for star-shaped blobs: move each vertex toward center by d."""
    c = V(center)
    out = []
    for p in poly:
        v = V(p) - c
        L = v.length
        out.append(c + v * max(0.05, (L - d)) / max(L, 1e-6))
    return out


# ----------------------------------------------------------------------------- spatial hash
class SegmentHash:
    """Spatial hash of 2D segments, each with a clearance radius and payload."""

    def __init__(self, cell=16.0):
        self.cell = cell
        self.grid = {}
        self.items = []

    def _cells(self, x0, y0, x1, y1):
        c = self.cell
        for i in range(int(math.floor(x0 / c)), int(math.floor(x1 / c)) + 1):
            for j in range(int(math.floor(y0 / c)), int(math.floor(y1 / c)) + 1):
                yield (i, j)

    def add(self, a, b, radius, payload=None):
        a, b = V(a), V(b)
        k = len(self.items)
        self.items.append((a, b, radius, payload))
        r = radius
        for key in self._cells(min(a.x, b.x) - r, min(a.y, b.y) - r, max(a.x, b.x) + r, max(a.y, b.y) + r):
            self.grid.setdefault(key, []).append(k)

    def add_polyline(self, pts, radius, payload=None):
        for i in range(len(pts) - 1):
            self.add(pts[i], pts[i + 1], radius, payload)

    def _candidates(self, p, extra):
        """Segment ids near p. Segments are registered in every cell their radius touches, so a
        positive *extra* margin must also scan the neighbouring cells it can reach."""
        c = self.cell
        if extra <= 0:
            return self.grid.get((int(math.floor(p.x / c)), int(math.floor(p.y / c))), ())
        i0, i1 = int(math.floor((p.x - extra) / c)), int(math.floor((p.x + extra) / c))
        j0, j1 = int(math.floor((p.y - extra) / c)), int(math.floor((p.y + extra) / c))
        if i0 == i1 and j0 == j1:
            return self.grid.get((i0, j0), ())
        seen = set()
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                seen.update(self.grid.get((i, j), ()))
        return seen

    def hits(self, p, extra=0.0):
        """Payloads of segments whose clearance (radius + extra) contains point p."""
        p = V(p)
        res = []
        for k in self._candidates(p, extra):
            a, b, r, pl = self.items[k]
            if dist_point_seg(p, a, b) < r + extra:
                res.append(pl)
        return res

    def blocked(self, p, extra=0.0):
        p = V(p)
        for k in self._candidates(p, extra):
            a, b, r, _ = self.items[k]
            if dist_point_seg(p, a, b) < r + extra:
                return True
        return False

    def nearest(self, p, max_d=1e9):
        p = V(p)
        best, bpl = max_d, None
        c = self.cell
        span = int(math.ceil(max_d / c)) if max_d < 1e8 else 3
        ci, cj = int(math.floor(p.x / c)), int(math.floor(p.y / c))
        seen = set()
        for i in range(ci - span, ci + span + 1):
            for j in range(cj - span, cj + span + 1):
                for k in self.grid.get((i, j), ()):
                    if k in seen:
                        continue
                    seen.add(k)
                    a, b, r, pl = self.items[k]
                    d = dist_point_seg(p, a, b) - r
                    if d < best:
                        best, bpl = d, pl
        return best, bpl


def sample_poly_points(poly, step=1.5, interior=True):
    """Boundary (and optional interior grid) sample points of a polygon for collision tests."""
    P = [V(p) for p in poly]
    pts = []
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n = max(1, int(math.ceil((b - a).length / step)))
        for k in range(n):
            pts.append(a.lerp(b, k / n))
    if interior:
        x0, y0, x1, y1 = bbox(P)
        y = y0 + step * 0.5
        while y < y1:
            x = x0 + step * 0.5
            while x < x1:
                q = Vector((x, y))
                if point_in_poly(q, P):
                    pts.append(q)
                x += step
            y += step
    return pts


def poly_length(pts, closed=False):
    L = 0.0
    for i in range(len(pts) - 1):
        L += (V(pts[i + 1]) - V(pts[i])).length
    if closed and len(pts) > 2:
        L += (V(pts[0]) - V(pts[-1])).length
    return L
