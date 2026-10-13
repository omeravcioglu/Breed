"""Helpers for Phase 4 landmark builders (citygen/landmarks/<site>.py).

    def build(S):            # S is a Site for one LANDMARKS entry
        S.put("Bench", x, y, rot=..)                     # kit instance (world coords)
        S.put("Bench", lx, ly, rot=.., local=True)       # coords in the site frame (see below)
        S.mesh("Plaza", mb)                              # custom MeshBuilder geometry
        S.building(spec, origin, rot)                    # modular building from the kit (assembler)

Site frame: origin = site center; local -Y points along the site's "facing" (toward its street /
entrance) when the site has one, so "front" is -Y exactly like kit pieces and buildings.
Everything lands in the collection 05_Landmarks/LM_<SiteId>/... Ground level is C.GROUND_Z
(-0.05); sidewalk / plinth level is 0.15; hills raise the ground (use S.ground_z(x, y)).
"""
import math
import random

from mathutils import Vector

from . import config as C
from . import geom2d as G
from . import kit as K
from . import scene
from .meshutil import MeshBuilder


class Site:
    def __init__(self, ctx, site_id, data=None):
        """site_id: a LANDMARKS key, or any id when *data* (NO_BUILD / DISTRICTS entry) is given."""
        self.ctx = ctx
        self.id = site_id
        self.layout = ctx["layout"]
        self.data = data if data is not None else self.layout.LANDMARKS.get(site_id, {})
        self.poly = [G.V(p) for p in self.data.get("poly", [])]
        c = self.data.get("center")
        self.center = G.V(c) if c else (G.centroid(self.poly) if self.poly else Vector((0, 0)))
        f = self.data.get("facing") or self.data.get("entrance_facing")
        self.facing = G.V(f).normalized() if f else Vector((0.0, -1.0))
        # local +Y = away from the street: rot so that local (0,1) -> -facing
        self.rot = math.atan2(-self.facing.y, -self.facing.x) - math.pi / 2
        self.coll = f"05_Landmarks/LM_{site_id}"
        self.net = ctx["net"]
        self.world = ctx.get("world")
        self.rng = random.Random("site:" + site_id)
        self.n = 0
        self.road_hash = self.net.clearance_hash(extra=0.0)
        river = ctx.get("river")
        self.river_hash = river.hash(extra=0.5) if river else None

    # ------------------------------------------------------------------ frames
    def to_world(self, lx, ly):
        c, s = math.cos(self.rot), math.sin(self.rot)
        return Vector((self.center.x + lx * c - ly * s, self.center.y + lx * s + ly * c))

    def to_local(self, p):
        d = G.V(p) - self.center
        c, s = math.cos(-self.rot), math.sin(-self.rot)
        return Vector((d.x * c - d.y * s, d.x * s + d.y * c))

    def ground_z(self, x, y):
        from . import terrain
        z = C.GROUND_Z
        for hd in getattr(self.layout, "HILLS", []):
            z = max(z, C.GROUND_Z + terrain.hill_height(hd, x, y))
        return z

    def inside(self, p, poly=None):
        return G.point_in_poly(G.V(p), poly or self.poly)

    def clear_of_roads(self, p, extra=0.3):
        p = G.V(p)
        if self.road_hash.blocked(p, extra=extra):
            return False
        if self.river_hash is not None and self.river_hash.blocked(p):
            return False
        return True

    # ------------------------------------------------------------------ placement
    def put(self, piece, x, y, z=None, rot=0.0, recolor=None, scale=None, local=False, sub=None, name=None):
        nm = piece if piece.startswith("KIT_") else "KIT_" + piece
        if not K.has(nm):
            return None
        if local:
            p = self.to_world(x, y)
            x, y = p.x, p.y
            rot = rot + self.rot
        if z is None:
            z = self.ground_z(x, y)
        self.n += 1
        path = self.coll + (f"/{sub}" if sub else "")
        return K.instance(nm, path, (x, y, z), rot, recolor=recolor, scale=scale,
                          inst_name=(name or f"LM_{self.id}_{nm[4:]}_{self.n:03d}")[:63])

    def mesh(self, name, mb, sub=None, weld=True, loc=(0, 0, 0), rot=0.0):
        full = f"LM_{self.id}_{name}"[:63]
        return scene.obj(full, mb.build(full, weld=weld), self.coll + (f"/{sub}" if sub else ""), loc, rot_z=rot)

    def building(self, spec, origin, rot, name=None, register=True, base_z=C.LOT_Z):
        from .assembler import assemble
        self.n += 1
        nm = (name or f"LM_{self.id}_Bldg_{self.n:02d}")[:63]
        root, cnt = assemble(spec, nm, G.V(origin), rot, self.coll, base_z=base_z)
        if register and self.world is not None:
            X = Vector((math.cos(rot), math.sin(rot)))
            Y = Vector((-math.sin(rot), math.cos(rot)))
            o = G.V(origin)
            self.world.add_lot([o - X * spec.W / 2, o + X * spec.W / 2, o + X * spec.W / 2 + Y * spec.D,
                                o - X * spec.W / 2 + Y * spec.D])
        return root

    def register_lot(self, poly):
        if self.world is not None:
            self.world.add_lot([G.V(p) for p in poly])

    def fence_along(self, pts, piece="Fence_Iron_3m", closed=False, gaps=(), z=None, sub="Fences", recolor=None):
        """3 m fence pieces along a polyline (scaled to fit each segment). gaps: [(point, width)]."""
        P = [G.V(p) for p in pts]
        if closed:
            P = P + [P[0]]
        placed = 0
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            L = (b - a).length
            if L < 0.5:
                continue
            n = max(1, round(L / 3.0))
            sx = L / (3.0 * n)
            d = (b - a) / L
            rot = math.atan2(d.y, d.x)
            for k in range(n):
                m = a + d * (L * (k + 0.5) / n)
                if any((m - G.V(g)).length < w / 2 + 1.5 for g, w in gaps):
                    continue
                if self.put(piece, m.x, m.y, z, rot, scale=(sx, 1, 1), sub=sub, recolor=recolor):
                    placed += 1
        return placed

    def scatter(self, pieces, count, poly=None, min_dist=3.0, z=None, sub="Scatter", recolor_fn=None,
                avoid=(), rot_random=True, scale_range=(1.0, 1.0), tries=40):
        """Random non-overlapping placement inside a polygon (default: the site polygon)."""
        poly = [G.V(p) for p in (poly or self.poly)]
        x0, y0, x1, y1 = G.bbox(poly)
        out = []
        for _ in range(count):
            for _t in range(tries):
                p = Vector((self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)))
                if not G.point_in_poly(p, poly):
                    continue
                if any(G.point_in_poly(p, [G.V(q) for q in a]) for a in avoid):
                    continue
                if not self.clear_of_roads(p, extra=1.0):
                    continue
                if any((p - q).length < min_dist for q in out):
                    continue
                piece = self.rng.choice(pieces) if isinstance(pieces, (list, tuple)) else pieces
                s = self.rng.uniform(*scale_range)
                self.put(piece, p.x, p.y, z, self.rng.uniform(0, 6.28) if rot_random else 0.0,
                         recolor=recolor_fn(self.rng) if recolor_fn else None, scale=(s, s, s), sub=sub)
                out.append(p)
                break
        return out

    # ------------------------------------------------------------------ surfaces
    def paving(self, name, poly, mat="M_Plaza", z=0.0, skirt=0.25, sub="Ground"):
        """Flat paved polygon with a short skirt (z = top)."""
        mb = MeshBuilder()
        P = G.ensure_ccw([G.V(p) for p in poly])
        mb.prism(P, z - skirt, z, mat, mat)
        return self.mesh(name, mb, sub=sub)

    def path_ribbon(self, name, pts, width=3.0, mat="M_Path", lift=0.035, step=1.5, sub="Paths", clip=True):
        """Footpath ribbon following the ground (and hills).

        clip: drop segments that run deep under a road/sidewalk corridor or out over the canal
        (paths may meet sidewalks - a short overlap is kept so the joint has no gap).
        """
        spl, _ = G.catmull_rom([G.V(p) for p in pts], step=step)
        pl = G.Polyline(spl)
        st = pl.stations(0.0, pl.length, step)
        L, R, C2 = [], [], []
        for s in st:
            p = pl.pos(s)
            n = G.left_normal(pl.tangent(s))
            C2.append(p)
            for side, lst in ((1, L), (-1, R)):
                q = p + n * (width / 2 * side)
                lst.append(Vector((q.x, q.y, self.ground_z(q.x, q.y) + lift)))
        river = self.ctx.get("river")
        water = river.hash(extra=0.0) if (clip and river is not None) else None
        mb = MeshBuilder()
        for i in range(len(L) - 1):
            if clip:
                m = (C2[i] + C2[i + 1]) * 0.5
                if self.road_hash.blocked(m, extra=-0.9):
                    continue
                if water is not None and water.blocked(m):
                    continue
            mb.strip(L[i:i + 2], R[i:i + 2], mat)
        if not mb.faces:
            return None
        return self.mesh(name, mb, sub=sub)

    def pool(self, name, outline, water_z=-0.45, bed_z=-1.2, rim_mat="M_CanalStone", rim_w=0.5, rim_h=0.25,
             sub="Water"):
        """Raised-rim pool / pond with water surface (outline is any simple polygon)."""
        P = G.ensure_ccw([G.V(p) for p in outline])
        c = G.centroid(P)
        inner = G.offset_polygon_radial(P, c, rim_w)
        mb = MeshBuilder()
        # rim top ring
        n = len(P)
        for i in range(n):
            j = (i + 1) % n
            a0, a1 = Vector((*P[i], C.GROUND_Z + rim_h)), Vector((*P[j], C.GROUND_Z + rim_h))
            b0, b1 = Vector((*inner[i], C.GROUND_Z + rim_h)), Vector((*inner[j], C.GROUND_Z + rim_h))
            mb.face([a0, a1, b1, b0], rim_mat)
        mb.wall(P, C.GROUND_Z - 0.1, C.GROUND_Z + rim_h, rim_mat, closed=True)
        mb.wall(inner, bed_z, C.GROUND_Z + rim_h, rim_mat, closed=True, outward_left=True)
        mb.tri_fill([inner], bed_z, "M_RiverBed")
        w = MeshBuilder()
        w.tri_fill([inner], water_z, "M_Water")
        self.mesh(name + "_Rim", mb, sub=sub)
        return self.mesh(name + "_Water", w, sub=sub)
