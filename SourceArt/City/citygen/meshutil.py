"""MeshBuilder: accumulate faces with palette material names, then emit one Blender mesh.

Winding convention: faces are CCW when viewed from the side their normal points to.
Horizontal tops are CCW seen from +Z. All builders below respect this, so meshes come
out with correct outward normals for Unity (backface culling on).
"""
import math
import bmesh
import bpy
from mathutils import Vector, Matrix, geometry

from . import palette


def V3(p, z=None):
    if z is None:
        return Vector((float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0))
    return Vector((float(p[0]), float(p[1]), float(z)))


class MeshBuilder:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.fmat = []
        self.mats = []

    # ------------------------------------------------------------------ basics
    def _mi(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def face(self, pts, mat):
        """Add a polygon from 3D points (CCW seen from the normal side)."""
        if len(pts) < 3:
            return
        base = len(self.verts)
        self.verts.extend(V3(p) for p in pts)
        self.faces.append(tuple(range(base, base + len(pts))))
        self.fmat.append(self._mi(mat))

    def tri_fill(self, loops2d, z, mat, up=True):
        """Fill (possibly concave, with holes) 2D polylines at height z via scanfill.

        loops2d: list of polylines; the first is the outer boundary, others are holes.
        """
        loops = [[Vector((p[0], p[1], z)) for p in loop] for loop in loops2d if len(loop) >= 3]
        if not loops:
            return
        tris = geometry.tessellate_polygon(loops)
        flat = [p for loop in loops for p in loop]
        for t in tris:
            a, b, c = flat[t[0]], flat[t[1]], flat[t[2]]
            n = (b - a).cross(c - a)
            if (n.z >= 0) == up:
                self.face([a, b, c], mat)
            else:
                self.face([a, c, b], mat)

    def fan(self, center2d, ring2d, z, mat):
        """Fan-triangulate a star-shaped ring (CCW) around center at height z (normal up)."""
        c = V3(center2d, z)
        n = len(ring2d)
        for i in range(n):
            a = V3(ring2d[i], z)
            b = V3(ring2d[(i + 1) % n], z)
            if (a - b).length < 1e-6:
                continue
            nrm = (a - c).cross(b - c)
            if nrm.z >= 0:
                self.face([c, a, b], mat)
            else:
                self.face([c, b, a], mat)

    def strip(self, left, right, mat, z=None):
        """Quad strip between two equal-length point lists (left/right of travel), normal up."""
        for i in range(len(left) - 1):
            l0, l1 = V3(left[i], z), V3(left[i + 1], z)
            r0, r1 = V3(right[i], z), V3(right[i + 1], z)
            # travel direction along index; left is CCW side -> r0, r1, l1, l0 is CCW from above
            self.face([r0, r1, l1, l0], mat)

    def wall(self, pts2d, z0, z1, mat, closed=False, outward_left=False):
        """Vertical wall along a 2D polyline. Normal faces RIGHT of travel unless outward_left."""
        n = len(pts2d)
        rng = range(n if closed else n - 1)
        for i in rng:
            a = pts2d[i]
            b = pts2d[(i + 1) % n]
            if outward_left:
                a, b = b, a
            A0, B0 = V3(a, z0), V3(b, z0)
            A1, B1 = V3(a, z1), V3(b, z1)
            # walking a->b, normal to the right: CCW seen from the right = A0,B0,B1,A1 reversed?
            # Right-of-travel normal r = (t.y, -t.x). Face (A0, A1, B1, B0) has normal = (A1-A0)x(B0-A0)
            # = z x t = (-t.y, t.x) = left. So use (A0, B0, B1, A1) for a right-facing normal.
            self.face([A0, B0, B1, A1], mat)

    def wall_var(self, pts2d, z0s, z1s, mat, outward_left=False):
        """Vertical wall with per-vertex bottom/top heights (normal RIGHT of travel)."""
        P, Z0, Z1 = list(pts2d), list(z0s), list(z1s)
        if outward_left:
            P, Z0, Z1 = P[::-1], Z0[::-1], Z1[::-1]
        for i in range(len(P) - 1):
            self.face([V3(P[i], Z0[i]), V3(P[i + 1], Z0[i + 1]), V3(P[i + 1], Z1[i + 1]), V3(P[i], Z1[i])], mat)

    def box(self, x0, y0, z0, x1, y1, z1, mat, skip=()):
        """Axis aligned box. skip: subset of {'-x','+x','-y','+y','-z','+z'}."""
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        if z0 > z1: z0, z1 = z1, z0
        c = [Vector(v) for v in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
        faces = {
            "-z": [c[0], c[3], c[2], c[1]], "+z": [c[4], c[5], c[6], c[7]],
            "-y": [c[0], c[1], c[5], c[4]], "+y": [c[2], c[3], c[7], c[6]],
            "-x": [c[3], c[0], c[4], c[7]], "+x": [c[1], c[2], c[6], c[5]],
        }
        for k, f in faces.items():
            if k not in skip:
                self.face(f, mat)

    def obox(self, center, fwd, width, depth, z0, z1, mat, skip_bottom=True):
        """Oriented box (2D rectangle footprint) - width across, depth along fwd."""
        from .geom2d import rect_corners
        pts = rect_corners(center, fwd, width, depth)
        self.prism(pts, z0, z1, mat, mat, bottom=None if skip_bottom else mat)

    def prism(self, poly2d, z0, z1, mat_top, mat_side, bottom=None):
        """Extrude a simple polygon (any winding) between z0 and z1."""
        from .geom2d import ensure_ccw
        P = ensure_ccw([(p[0], p[1]) for p in poly2d])
        self.tri_fill([P], z1, mat_top, up=True)
        if bottom:
            self.tri_fill([P], z0, bottom, up=False)
        # CCW outer boundary -> outward normal is to the RIGHT of travel
        self.wall(P, z0, z1, mat_side, closed=True)

    def cylinder(self, cx, cy, z0, z1, r, mat, seg=8, cap_top=True, cap_bottom=False, mat_cap=None, r_top=None):
        rt = r if r_top is None else r_top
        ring0 = [(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
        ring1 = [(cx + rt * math.cos(2 * math.pi * i / seg), cy + rt * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
        for i in range(seg):
            j = (i + 1) % seg
            self.face([V3(ring0[i], z0), V3(ring0[j], z0), V3(ring1[j], z1), V3(ring1[i], z1)], mat)
        if cap_top and rt > 1e-4:
            self.face([V3(p, z1) for p in ring1], mat_cap or mat)
        if cap_bottom:
            self.face([V3(p, z0) for p in reversed(ring0)], mat_cap or mat)

    def sphere(self, cx, cy, cz, r, mat, seg=8, rings=5, sz=1.0):
        """Low-poly UV sphere (sz squashes vertically)."""
        pts = []
        for i in range(rings + 1):
            th = math.pi * i / rings
            row = []
            for j in range(seg):
                ph = 2 * math.pi * j / seg
                row.append(Vector((cx + r * math.sin(th) * math.cos(ph), cy + r * math.sin(th) * math.sin(ph),
                                   cz + r * sz * math.cos(th))))
            pts.append(row)
        for i in range(rings):
            for j in range(seg):
                k = (j + 1) % seg
                a, b, c, d = pts[i][j], pts[i][k], pts[i + 1][k], pts[i + 1][j]
                if i == 0:
                    self.face([a, d, c], mat)
                elif i == rings - 1:
                    self.face([a, d, b], mat)
                else:
                    self.face([a, d, c, b], mat)

    def extend(self, other, matrix=None):
        M = matrix or Matrix.Identity(4)
        base = len(self.verts)
        self.verts.extend(M @ v for v in other.verts)
        for f, mi in zip(other.faces, other.fmat):
            self.faces.append(tuple(base + i for i in f))
            self.fmat.append(self._mi(other.mats[mi]))

    def transform(self, M):
        self.verts = [M @ v for v in self.verts]

    # ------------------------------------------------------------------ output
    def build(self, name, weld=True, weld_dist=1e-4, uv_scale=0.25, bevel=0.0, bevel_angle=40.0):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        for mname in self.mats:
            me.materials.append(palette.get(mname))
        for poly, mi in zip(me.polygons, self.fmat):
            poly.material_index = mi
        me.update()
        bm = bmesh.new()
        bm.from_mesh(me)
        if weld:
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld_dist)
        if bevel > 0:
            edges = [e for e in bm.edges if e.is_manifold and len(e.link_faces) == 2 and
                     math.degrees(e.calc_face_angle(0.0)) > bevel_angle]
            if edges:
                bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=1, profile=0.5,
                                affect="EDGES", clamp_overlap=True)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
        _box_uv(bm, uv_scale)
        bm.to_mesh(me)
        bm.free()
        me.update()
        return me


def _box_uv(bm, scale):
    """World-space box-projection UVs (1 UV unit = 1/scale meters) for tiling textures later."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            co = l.vert.co
            if ax == 2:
                l[uv].uv = (co.x * scale, co.y * scale)
            elif ax == 1:
                l[uv].uv = (co.x * scale, co.z * scale)
            else:
                l[uv].uv = (co.y * scale, co.z * scale)
