"""PET SHOP - the player's home base (LANDMARKS["PetShop"]) + its reserved expansion plot.

PLAN (site frame: origin = lot centre, local -Y = north toward Maple Street / Maple Green, local +X = west)
-------------------------------------------------------------------------------------------------------
The 24 x 20 m lot (x -12..12, y -10..10) sits on the south side of Maple Street. The shop door looks north
over Maple Green, the canal and the Town Square clock tower (Green Walk axis); the player spawn is on the
sidewalk right in front of the door (local 0, -13.4).

  y -10 .. -6.5  FORECOURT (paved, sidewalk level): planters, bench under the awning, chalkboard A-frame,
                 water bowl by the door, gate apron for the play yard. The spawn / door axis stays clear.
  y < -10        CONNECTORS (deliberate small extensions beyond the lot, connectors only): a 4.9 m M_Plaza
                 FRONT APRON on the door axis and the DRIVEWAY MOUTH (M_Concrete) cross the 1.8-2.7 m grass verge
                 to the Maple St sidewalk; top 0.14, they start under the forecourt / driveway and end 0.35 m
                 under the 0.15 kerb (no z-fighting). The spawn -> door walk never touches grass.
  BUILDING       kit shop (assembler): 3 x 3 modules (9 x 9 m), 2 floors (H4 storefront + H3), FRONT GABLE
                 roof (cottage silhouette that stands apart from the flat-roofed shop rows). Door in the
                 centre module, striped teal awnings over the two display windows, orange fascia sign with
                 cream "PET SHOP" mesh lettering (built-in font -> mesh, an orange plate in the kit board's
                 recess hides its placeholder bars; reads at 5-20 m),
                 paw blade sign on the east corner, window boxes + window awnings upstairs, display windows
                 on the east side looking into the play yard.  Signature palette: cream walls, teal
                 (M_PetShop_Second) roof / awnings / door, orange (M_PetShop_Primary) signs.
  HERO SIGN      custom 3.8 m paw-print medallion (orange rim, teal face, cream paw) on the front gable,
                 popping above the ridge: reads from the green, the bridge and the Town Square (60-130 m).
                 A small twin on the back gable marks the shop from the expansion plot / Kennel Lane.
  PLAY YARD (east, x -11.7..-4.85, y -8..9.5)  white picket pen with a front gate (from the forecourt) and
                 a back gate (to the back yard): sand patch, agility hurdles / tunnel / A-frame, doghouses,
                 water, hay bales, a shade tree and bushes (hiding spots for small animals). Visible from the
                 Main Street approach and from the green.
  DELIVERY (west, x 5..11.8)  concrete driveway from Maple Street along the shop: branded orange van (paw
                 disc on the cargo panel + "PET SHOP" lettering under the belt line, both sides), painted
                 loading bay at the back, pallets / crates / feed sacks by the back door.
  BACK YARD (x -4.85..5, y 2.5..10)  gravel service yard, bins; opens straight into the expansion plot.

EXPANSION PLOT (data['expansion_poly'], ~58 x 33 m behind the shop, reaching Kennel Lane)
  Readable growth plan without building it - a CONSTRUCTION SITE, not a sports field: chain-link
  construction fence (open toward the shop yard, a wide gate toward Kennel Lane), plain dry grass inside,
  a gravel service drive from the shop yard through the gate on to the Kennel Lane asphalt (connector),
  three marked future plots with pictogram boards: KENNELS (dug-out dirt pad, timber formwork, a poured
  footing strip carrying the kennel-run posts), BREEDING ROOMS (scraped irregular dirt patch, orange survey
  strings on stakes, gravel + sand heaps), AVIARY (dirt disc, staked orange ring, centre pole); a spoil
  heap; a gravel parking strip; a teal site container with a portable toilet, a strapped timber stack and a
  survey tripod (vertical cues), pallet / crate stacks, barriers, cones and a big two-sided "coming soon"
  board (paw + house, readable from the shop and from the Kennel Lane gate). Open and walkable everywhere
  (animals can be chased around the container, heaps and crate stacks).

Shared geometry helpers (paw shapes, plane matrices, hay bales, tents, bunting, emit, text_mb block lettering,
kerb_hit / connector_poly for kerb connectors, two-sided sign boards) live here and are reused by
maple_green.py and open_lot.py.
NOTE (request to the lead): Maple St (a "side" road) has no crosswalks; the spawn (-51.5, -33.9) -> front
apron -> Green Walk link crossing wants one at x ~ -50.5 (the apron and the Green Walk link both land there).
NOTE (framework workaround): citygen.scene.coll() resolves every path part with a GLOBAL
bpy.data.collections.get(name), so generic sub-collection names ("Ground", "Paths", "Trees", ...) collide
between sites and even with kit category collections (KIT_Library/nature/Trees). Every sub= used by my
three modules is therefore prefixed (PS_ / MG_ / OL_) and passed explicitly (also to S.paving / path_ribbon).
"""
import math

from mathutils import Matrix, Vector

from .. import config as C
from .. import facade as F
from .. import geom2d as G
from .. import kit as K
from ..assembler import BuildingSpec, H4
from ..meshutil import MeshBuilder

PRI, SEC = "M_PetShop_Primary", "M_PetShop_Second"
Z_LOT = C.LOT_Z            # 0.15: sidewalk / plinth level
TAU = 2.0 * math.pi


# =============================================================================== shared helpers
def ellipse(cx, cy, a, b, n=12, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        t = TAU * i / n
        x, y = a * math.cos(t), b * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def paw_shapes(s):
    """Paw print outlines (2D, CCW) about the origin, overall height ~ s."""
    pad = []
    n = 20
    for i in range(n):
        t = TAU * i / n
        x, y = 0.34 * s * math.cos(t), 0.25 * s * math.sin(t)
        if y > 0:
            x *= 1.0 - 0.22 * (y / (0.25 * s))      # heel pad narrows toward the toes
        else:
            y *= 1.0 - 0.18 * abs(math.cos(t)) ** 6  # slightly flat bottom
        pad.append((x, y - 0.2 * s))
    toes = [ellipse(-0.37 * s, 0.11 * s, 0.105 * s, 0.135 * s, 12, 0.45),
            ellipse(-0.135 * s, 0.30 * s, 0.11 * s, 0.145 * s, 12, 0.12),
            ellipse(0.135 * s, 0.30 * s, 0.11 * s, 0.145 * s, 12, -0.12),
            ellipse(0.37 * s, 0.11 * s, 0.105 * s, 0.135 * s, 12, -0.45)]
    return [pad] + toes


def heart_shape(s, n=24):
    out = []
    for i in range(n):
        t = TAU * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        out.append((x * s / 34.0, y * s / 34.0 + 0.05 * s))
    return G.ensure_ccw([Vector(p) for p in out])


def star_shape(r_out, r_in, n=5, rot=math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + math.pi * i / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def plane_matrix(origin, right, up):
    """(u, v, w) plane coords -> world: origin + u*right + v*up + w*(right x up). Proper rotation."""
    r = Vector(right).normalized()
    u = Vector(up).normalized()
    n = r.cross(u)
    o = Vector(origin)
    return Matrix(((r.x, u.x, n.x, o.x), (r.y, u.y, n.y, o.y), (r.z, u.z, n.z, o.z), (0, 0, 0, 1)))


def front_matrix(x=0.0, y=0.0, z=0.0):
    """Plane coords -> a vertical plane facing -Y (u = +X, v = +Z, w = toward the viewer = -Y)."""
    return plane_matrix((x, y, z), (1, 0, 0), (0, 0, 1))


def xf(mb, M):
    """Extend a new MeshBuilder with mb transformed by M."""
    out = MeshBuilder()
    out.extend(mb, M)
    return out


def bev_box(x0, y0, z0, x1, y1, z1, mat, bev=0.03, skip_bottom=True):
    sub = MeshBuilder()
    sub.box(x0, y0, z0, x1, y1, z1, mat, skip=("-z",) if skip_bottom else ())
    return F.bevelled(sub, bev) if bev > 0 else sub


def seg_box(mb, a, b, w, h, mat, z_mid=None):
    """Rectangular bar between 3D points a and b (cross-section w x h)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    if L < 1e-4:
        return
    sub = MeshBuilder()
    sub.box(0, -w / 2, -h / 2, L, w / 2, h / 2, mat)
    xa = d.normalized()
    up = Vector((0, 0, 1))
    if abs(xa.dot(up)) > 0.99:
        up = Vector((0, 1, 0))
    ya = up.cross(xa).normalized()
    za = xa.cross(ya)
    M = Matrix(((xa.x, ya.x, za.x, a.x), (xa.y, ya.y, za.y, a.y), (xa.z, ya.z, za.z, a.z), (0, 0, 0, 1)))
    mb.extend(sub, M)


def rz(mb, rot, x=0.0, y=0.0, z=0.0):
    return xf(mb, Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z"))


def emit(S, name, mb, lx=0.0, ly=0.0, z=0.0, rot=0.0, sub=None, local=True):
    """Custom mesh object with its pivot at (lx, ly, z) (site frame if local) rotated by rot."""
    o = S.mesh(name, mb, sub=sub)
    if local:
        p = S.to_world(lx, ly)
        o.location = (p.x, p.y, z)
        o.rotation_euler = (0.0, 0.0, S.rot + rot)
    else:
        o.location = (lx, ly, z)
        o.rotation_euler = (0.0, 0.0, rot)
    return o


def face_rot(dx, dy):
    """Rotation that turns a piece's front (-Y) toward the direction (dx, dy)."""
    return math.atan2(dx, -dy)


def hay_bale(L=1.15, W=0.6, H=0.48):
    mb = bev_box(-L / 2, -W / 2, 0.0, L / 2, W / 2, H, "M_Awning_Yellow", bev=0.07)
    for t in (-0.27, 0.27):
        x = t * L
        mb.box(x - 0.03, -W / 2 - 0.012, 0.0, x + 0.03, W / 2 + 0.012, H + 0.012, "M_Trim_Wood", skip=("-z",))
    return mb


def paw_medallion(R=1.9, depth=0.40, rim=PRI, face=SEC, paw="M_Sign_Face", seg=32):
    """Round paw sign in plane coords facing -Y; origin = centre of the disc BACK face (y = 0)."""
    mb = MeshBuilder()
    d0 = depth * 0.55
    mb.cylinder(0, 0, 0.0, d0, R, rim, seg=seg, cap_top=True, cap_bottom=True)
    mb.cylinder(0, 0, d0, d0 + 0.08, R - 0.26, face, seg=seg, cap_top=True)
    for shp in paw_shapes(2.0 * (R - 0.26) * 0.78):
        mb.prism(shp, d0 + 0.08, depth, paw, paw)
    return xf(mb, front_matrix())


def sign_board(w, h, face, frame="M_Sign_Board", depth=0.12, post_h=None, post_mat="M_Trim_Wood",
               pictos=(), picto_mat="M_Sign_Face", z0=0.0, two_sided=False, extra=()):
    """Free-standing board on two posts (front -Y). pictos: list of (shapes, du, dv) in face coords.
    extra: list of (MeshBuilder facing -Y centred on its origin, du, dv) mounted on the face (e.g. text_mb).
    two_sided: the face panel, pictos and extras are repeated on the back (rotated 180 deg so they read
    correctly from behind) and the posts move into the board's middle plane."""
    mb = MeshBuilder()
    zb = z0 + (post_h if post_h is not None else 0.0)
    mb.extend(bev_box(-w / 2, -depth / 2, zb, w / 2, depth / 2, zb + h, frame, bev=0.03, skip_bottom=False))
    face_mb = MeshBuilder()
    inner = MeshBuilder()
    inner.box(-w / 2 + 0.1, 0, 0, w / 2 - 0.1, 0.02, h - 0.2, face, skip=("+y",))
    face_mb.extend(inner, Matrix.Translation((0, -depth / 2 - 0.02 + 0.0, zb + 0.1)))
    for shapes, du, dv in pictos:
        p = MeshBuilder()
        for shp in shapes:
            p.prism(shp, 0.0, 0.05, picto_mat, picto_mat)
        face_mb.extend(p, front_matrix(du, -depth / 2 - 0.02, zb + dv))
    for sub, du, dv in extra:
        face_mb.extend(sub, Matrix.Translation((du, -depth / 2 - 0.02, zb + dv)))
    mb.extend(face_mb)
    if two_sided:
        mb.extend(face_mb, Matrix.Rotation(math.pi, 4, "Z"))
    if post_h:
        for sx in (-1, 1):
            x = sx * (w / 2 - 0.25)
            y0, y1 = (-0.07, 0.07) if two_sided else (0.04, 0.18)
            mb.extend(bev_box(x - 0.07, y0, 0.0, x + 0.07, y1, zb + h * 0.8, post_mat, bev=0.02))
    return mb


def text_mb(text, height, depth, mat, max_w=None, offset=0.012, res=2, back=False):
    """Extruded block lettering from Blender's built-in font: XZ plane, front toward -Y, centred on the
    origin; y spans [-depth/2, depth/2]. The glyph box is *height* tall (scaled down to *max_w* when wider).
    back=False drops the back faces (lettering mounted flat on a board) to save triangles."""
    import bpy
    cu = bpy.data.curves.new("__ps_txt", "FONT")
    cu.body = text
    cu.size = 1.0
    cu.extrude = 0.5
    cu.offset = offset
    cu.resolution_u = res
    cu.align_x = "CENTER"
    cu.fill_mode = "BOTH"
    ob = bpy.data.objects.new("__ps_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    mb = MeshBuilder()
    if me.vertices:
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        s = height / max(y1 - y0, 1e-6)
        if max_w and (x1 - x0) * s > max_w:
            s = max_w / (x1 - x0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for poly in me.polygons:
            if not back and poly.normal.z < -0.9:
                continue
            # curve XY (front +Z) -> XZ plane facing -Y: (x, y, z) -> (x, -z, y) is a proper rotation
            mb.face([Vector(((me.vertices[i].co.x - cx) * s, -me.vertices[i].co.z * depth,
                             (me.vertices[i].co.y - cy) * s)) for i in poly.vertices], mat)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bpy.data.meshes.remove(me)
    return mb


def kerb_hit(S, p, d, max_len=30.0, step=0.05):
    """March from world point p along d until the road + sidewalk corridor (or the canal) begins.
    Returns the world point (Vector) or None."""
    p, d = Vector((p[0], p[1])), Vector((d[0], d[1])).normalized()
    for i in range(int(max_len / step)):
        q = p + d * (i * step)
        if not S.clear_of_roads(q, extra=0.0):
            return q
    return None


def connector_poly(S, a, b, d, n=4, tuck=0.35):
    """Paving polygon from the world edge a->b out along d to the kerb, sampled at n+1 points across and
    pushed *tuck* m past the corridor edge so its end hides under the 0.15 kerb / asphalt edge."""
    a, b, d = Vector(a), Vector(b), Vector(d).normalized()
    far = []
    for i in range(n + 1):
        p = a.lerp(b, i / n)
        q = kerb_hit(S, p, d)
        if q is None:
            return None
        far.append(q + d * tuck)
    return [a, b] + list(reversed(far))


def bunting(mb, a, b, n, colors, sag=0.5, flag=0.36):
    """String of pennants from 3D point a to b (sagging); double-sided flags + a 0.04 line."""
    a, b = Vector(a), Vector(b)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for i in range(n):
        seg_box(mb, pts[i], pts[i + 1], 0.04, 0.04, "M_Trim_Dark")
    d = (b - a)
    d.z = 0
    d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
    nrm = Vector((-d.y, d.x, 0))
    for i in range(n):
        p0, p1 = pts[i], pts[i + 1]
        m0 = p0.lerp(p1, 0.2)
        m1 = p0.lerp(p1, 0.8)
        tip = p0.lerp(p1, 0.5) + Vector((0, 0, -flag))
        col = colors[i % len(colors)]
        off = nrm * 0.012
        # front and back faces (single-sided safe)
        f = [m0 + off, m1 + off, tip + off]
        bk = [m1 - off, m0 - off, tip - off]
        if (f[1] - f[0]).cross(f[2] - f[0]).dot(nrm) < 0:
            f = [f[1], f[0], f[2]]
            bk = [bk[1], bk[0], bk[2]]
        mb.face(f, col)
        mb.face(bk, col)


def tent(w, d, h_eave, h_peak, c1, c2, stripes=3, counter=None, valance=0.38, post_mat="M_Trim_White",
         finial=0.0, pennant_mat="M_Awning_Yellow"):
    """Striped pyramid-roof pavilion / stall, origin at ground centre, front -Y.
    finial > 0: a white pole of that height above the apex with a small pennant (bunting attach point)."""
    mb = MeshBuilder()
    if finial > 0:
        mb.cylinder(0, 0, h_peak - 0.15, h_peak + finial, 0.045, "M_Trim_White", seg=6)
        mb.sphere(0, 0, h_peak + finial + 0.04, 0.08, pennant_mat, seg=6, rings=4)
        pts = [Vector((0.05, 0, h_peak + finial - 0.05)), Vector((0.62, 0, h_peak + finial - 0.2)),
               Vector((0.05, 0, h_peak + finial - 0.36))]
        o = Vector((0, 0.01, 0))
        mb.face([pts[2] - o, pts[1] - o, pts[0] - o], pennant_mat)
        mb.face([pts[0] + o, pts[1] + o, pts[2] + o], pennant_mat)
    hw, hd = w / 2, d / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (hw - 0.08), sy * (hd - 0.08)
            mb.extend(bev_box(x - 0.06, y - 0.06, 0.0, x + 0.06, y + 0.06, h_eave + 0.05, post_mat, bev=0.015))
    ov = 0.18
    E = [Vector((-hw - ov, -hd - ov, h_eave)), Vector((hw + ov, -hd - ov, h_eave)),
         Vector((hw + ov, hd + ov, h_eave)), Vector((-hw - ov, hd + ov, h_eave))]
    apex = Vector((0, 0, h_peak))
    k = 0
    for i in range(4):
        A, B = E[i], E[(i + 1) % 4]
        for j in range(stripes):
            p0 = A.lerp(B, j / stripes)
            p1 = A.lerp(B, (j + 1) / stripes)
            col = c1 if k % 2 == 0 else c2
            mb.face([p0, p1, apex], col)
            # underside (slightly lower), seen from below
            dz = Vector((0, 0, -0.03))
            mb.face([p1 + dz, p0 + dz, apex + dz * 1.5], "M_Awning_Cream")
            k += 1
    # scalloped valance (double-sided) around the eave
    for i in range(4):
        A, B = E[i], E[(i + 1) % 4]
        L = (B - A).length
        n = max(2, round(L / 0.75))
        out = (B - A).normalized().cross(Vector((0, 0, 1)))
        for j in range(n):
            p0, p1 = A.lerp(B, j / n), A.lerp(B, (j + 1) / n)
            pm = p0.lerp(p1, 0.5)
            col = c1 if j % 2 == 0 else c2
            q = [p0, p1, p1 + Vector((0, 0, -valance * 0.7)), pm + Vector((0, 0, -valance)),
                 p0 + Vector((0, 0, -valance * 0.7))]
            o = out * 0.01
            fr = [v + o for v in q]
            # CCW seen from outside (out direction): order p0->p1 along CCW edge is clockwise from outside
            mb.face(list(reversed(fr)), col)
            bk = [v - o for v in q]
            mb.face(bk, col)
    if counter:
        cw, ch, cd = counter
        mb.extend(bev_box(-cw / 2, -hd + 0.05, 0.0, cw / 2, -hd + 0.05 + cd, ch, "M_Wood_Light", bev=0.03))
        mb.box(-cw / 2 - 0.03, -hd + 0.02, ch, cw / 2 + 0.03, -hd + 0.08 + cd, ch + 0.06, "M_Trim_White",
               skip=("-z",))
    return mb


def tri_count(objs):
    n = 0
    for o in objs:
        if o.type == "MESH":
            n += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return n


class Fence:
    """Fence runs in the SITE frame with exact gate openings (kit pieces scaled to fit)."""

    def __init__(self, S, piece, sub="PS_Fences", z=None, recolor=None):
        self.S, self.piece, self.sub, self.z, self.recolor = S, piece, sub, z, recolor
        self.placed = 0

    def run(self, a, b, piece=None, local=True, tile=3.0):
        S = self.S
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        if L < 0.3:
            return
        n = max(1, round(L / tile))
        d = (b - a) / L
        rot = math.atan2(d.y, d.x)
        for k in range(n):
            m = a + d * (L * (k + 0.5) / n)
            w = S.to_world(m.x, m.y) if local else m
            if not S.clear_of_roads(w, extra=0.2):
                continue
            if S.put(piece or self.piece, m.x, m.y, self.z, rot, scale=(L / (tile * n), 1, 1), local=local,
                     sub=self.sub, recolor=self.recolor):
                self.placed += 1

    def gate(self, a, b, piece="Gate_Picket", width=1.2, local=True, open_deg=0.0):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        d = (b - a) / L
        rot = math.atan2(d.y, d.x)
        m = (a + b) / 2
        if open_deg:
            hinge = a
            r2 = rot + math.radians(open_deg)
            m = hinge + Vector((math.cos(r2), math.sin(r2))) * (L / 2)
            rot = r2
        self.S.put(piece, m.x, m.y, self.z, rot, scale=(L / width, 1, 1), local=local, sub=self.sub)

    def line(self, pts, gates=(), piece=None, local=True, tile=3.0, gate_piece="Gate_Picket", gate_w=1.2,
             open_deg=0.0):
        """Polyline with gates = [(seg_index, t_center, width[, open_width])] (width None -> empty opening)."""
        P = [Vector(p) for p in pts]
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            L = (b - a).length
            cuts = sorted([(g[1], g[2], g[3] if len(g) > 3 else 3.0) for g in gates if g[0] == i])
            cur = a
            for t, w, ow in cuts:
                ww = w if w else ow
                g0 = a + (b - a) * (t - ww / 2 / L)
                g1 = a + (b - a) * (t + ww / 2 / L)
                self.run(cur, g0, piece, local, tile)
                if w:
                    self.gate(g0, g1, gate_piece, gate_w, local, open_deg)
                cur = g1
            self.run(cur, b, piece, local, tile)


def local_poly(S, pts):
    return [S.to_world(p[0], p[1]) for p in pts]


def clip_convex(poly, clip):
    """Sutherland-Hodgman: clip polygon *poly* by the convex CCW polygon *clip*."""
    out = [Vector(p) for p in poly]
    C_ = G.ensure_ccw([Vector(p) for p in clip])
    for i in range(len(C_)):
        a, b = C_[i], C_[(i + 1) % len(C_)]
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x) >= 0

        def inter(p, q):
            r = G.line_intersect(p, q - p, a, b - a)
            return p + (q - p) * r[0] if r is not None else p
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            if inside(q):
                if not inside(p):
                    out.append(inter(p, q))
                out.append(q)
            elif inside(p):
                out.append(inter(p, q))
    return out


def stripes(poly, angle, width, gap, z, mat, mb):
    """Parallel stripes (mowing pattern) clipped to a convex polygon."""
    d = Vector((math.cos(angle), math.sin(angle)))
    nrm = Vector((-d.y, d.x))
    P = [Vector(p) for p in poly]
    c = G.centroid(P)
    R = max((p - c).length for p in P) + 2
    k = -R
    while k < R:
        s0, s1 = c + nrm * k, c + nrm * (k + width)
        rect = [s0 - d * R, s0 + d * R, s1 + d * R, s1 - d * R]
        piece = clip_convex(rect, P)
        if len(piece) >= 3:
            mb.tri_fill([G.ensure_ccw(piece)], z, mat)
        k += width + gap


# =============================================================================== the shop
BF = -6.5          # building front line (site local y)
NW, ND, FLOORS = 3, 3, 2
SHOP_COLORS = dict(wall="M_Wall_Cream", trim="M_Trim_White", door=SEC, awning=SEC, roof=SEC, sign=PRI)


def _shop(S, out):
    spec = BuildingSpec("shop", NW, ND, FLOORS, dict(SHOP_COLORS), roof="gable_front", ground_h=H4,
                        feats=dict(awning=True, door_i=1, style="single", window_awnings=True),
                        seed=4242, exposed={"left": True}, district="petshop")
    o = S.to_world(0.0, BF)
    S.building(spec, o, S.rot, name="LM_PetShop_Shop")
    W, D = spec.W, spec.D
    top = Z_LOT + spec.wall_top()
    # window boxes under the three upstairs front windows
    sill_b = 0.79
    r = K.REG.get("KIT_Wall_Window_H3")
    if r:
        sill_b = r["meta"].get("sill_bottom_z", sill_b)
    for i in range(NW):
        x = -W / 2 + 1.5 + 3.0 * i
        S.put("WindowBox", x, BF, Z_LOT + H4 + sill_b - 0.27, recolor={"door": SEC}, local=True, sub="PS_Shop")
    # paw blade sign on the east corner + gooseneck lamps over the fascia sign
    S.put("Sign_Blade_Paw", -W / 2 + 0.55, BF, Z_LOT + H4 + 0.45, recolor={"sign": PRI, "trim": "M_Trim_White"},
          local=True, sub="PS_Shop")
    for dx in (-0.85, 0.85):
        S.put("Sign_Lamp", dx, BF, Z_LOT + 3.95, local=True, sub="PS_Shop")
    # HERO paw medallion on the front gable (pops above the ridge), twin on the back gable
    R = 1.95
    med = paw_medallion(R=R)
    for bx in (-0.9, 0.9):     # brackets back into the gable wall
        med.extend(bev_box(bx - 0.09, 0.0, -R * 0.55 - 0.09, bx + 0.09, 0.62, -R * 0.55 + 0.09, "M_Metal_Dark",
                           bev=0.02, skip_bottom=False))
    zc = top + 0.18 + R
    emit(S, "HeroSign_Paw", med, 0.0, BF - 0.55, zc, sub="PS_Shop")
    out["hero_top_z"] = round(zc + R, 2)
    rb = 1.05
    med2 = paw_medallion(R=rb, depth=0.3)
    for bx in (-0.45, 0.45):
        med2.extend(bev_box(bx - 0.06, 0.0, -0.06, bx + 0.06, 0.5, 0.06, "M_Metal_Dark", bev=0.015,
                            skip_bottom=False))
    emit(S, "BackSign_Paw", med2, 0.0, BF + D + 0.5, top + 0.35 + rb, rot=math.pi, sub="PS_Shop")
    # black-cat weathervane on the back end of the ridge (playful silhouette seen from the green)
    ridge = 3.476
    r = K.REG.get("KIT_Roof_Gable_S9_Mid")
    if r:
        ridge = r["dims"]["z"][1]
    emit(S, "CatWeathervane", cat_weathervane(), 0.0, BF + D - 1.4, top + ridge - 0.12, sub="PS_Shop")
    # FASCIA LETTERING: the assembler hangs a kit Sign_Board_3m (2.8 x 0.7, front at y = -0.12, recessed
    # face at -0.085 with raised placeholder bars to -0.097) on the door module at z 3.2. An orange plate in
    # the recess hides the bars and carries cream "PET SHOP" block letters (reads at 5-20 m).
    fx = -W / 2 + 1.5 + 3.0 * spec.feats.get("door_i", 0)
    fl = MeshBuilder()
    fl.box(-1.235, -0.1045, 0.165, 1.235, -0.0975, 0.535, PRI, skip=("+y",))
    fl.extend(text_mb("PET SHOP", 0.27, 0.022, "M_Sign_Face", max_w=2.2, offset=0.02, res=3),
              Matrix.Translation((0.0, -0.1155, 0.35)))
    emit(S, "Shop_FasciaLettering", fl, fx, BF, Z_LOT + 3.2, sub="PS_Shop")
    return spec


CAT = [(-0.05, 0.0), (0.40, 0.0), (0.42, 0.06), (0.36, 0.10), (0.38, 0.30), (0.34, 0.45), (0.40, 0.52),
       (0.42, 0.60), (0.38, 0.68), (0.40, 0.80), (0.31, 0.73), (0.24, 0.73), (0.20, 0.82), (0.18, 0.66),
       (0.16, 0.50), (0.08, 0.36), (0.02, 0.20), (-0.02, 0.10), (-0.15, 0.12), (-0.24, 0.20), (-0.26, 0.31),
       (-0.31, 0.27), (-0.28, 0.14), (-0.16, 0.04)]


def cat_weathervane(s=1.35):
    """Rod + compass arms + sitting-cat silhouette (faces the street). Origin at the rod base."""
    mb = MeshBuilder()
    mb.extend(bev_box(-0.12, -0.12, 0.0, 0.12, 0.12, 0.22, "M_Trim_Dark", bev=0.03))
    mb.box(-0.03, -0.03, 0.22, 0.03, 0.03, 1.35, "M_Trim_Dark", skip=("-z",))
    for (dx, dy) in ((1, 0), (0, 1)):
        mb.box(-0.42 * dx - 0.025, -0.42 * dy - 0.025, 0.72, 0.42 * dx + 0.025, 0.42 * dy + 0.025, 0.77, "M_Trim_Dark")
    mb.sphere(0, 0, 0.745, 0.06, "M_Awning_Yellow", seg=8, rings=4)
    cat = MeshBuilder()
    pts = [(x * s - 0.1 * s, y * s) for x, y in CAT]
    cat.prism(pts, -0.03, 0.03, "M_Trim_Dark", "M_Trim_Dark", bottom="M_Trim_Dark")
    mb.extend(cat, front_matrix(0.0, 0.0, 1.3))
    return mb


# =============================================================================== small pet props
def _agility():
    """Hurdles, tunnel and A-frame (play-yard agility set) as separate builders, origin at ground."""
    hurdle = MeshBuilder()
    for sx in (-1, 1):
        hurdle.extend(bev_box(sx * 0.62 - 0.06, -0.06, 0.0, sx * 0.62 + 0.06, 0.06, 0.95, "M_Trim_White", bev=0.02))
        hurdle.extend(bev_box(sx * 0.62 - 0.18, -0.25, 0.0, sx * 0.62 + 0.18, 0.25, 0.06, "M_Trim_White", bev=0.015))
    for j, z in enumerate((0.42, 0.72)):
        for k in range(4):
            x0 = -0.56 + k * 0.28
            hurdle.box(x0, -0.045, z - 0.045, x0 + 0.28, 0.045, z + 0.045, PRI if (k + j) % 2 == 0 else "M_Trim_White")

    tunnel = MeshBuilder()
    seg, r0, r1, L = 12, 0.5, 0.42, 2.6
    for i in range(seg):
        a0, a1 = math.pi * i / seg, math.pi * (i + 1) / seg
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        col = SEC if (i // 2) % 2 == 0 else "M_Awning_Cream"
        # outer (normal outward)
        tunnel.face([(r0 * c1, -L / 2, r0 * s1), (r0 * c0, -L / 2, r0 * s0), (r0 * c0, L / 2, r0 * s0),
                     (r0 * c1, L / 2, r0 * s1)], col)
        # inner (normal inward)
        tunnel.face([(r1 * c0, -L / 2, r1 * s0), (r1 * c1, -L / 2, r1 * s1), (r1 * c1, L / 2, r1 * s1),
                     (r1 * c0, L / 2, r1 * s0)], SEC)
        # end rings
        tunnel.face([(r1 * c0, -L / 2, r1 * s0), (r0 * c0, -L / 2, r0 * s0), (r0 * c1, -L / 2, r0 * s1),
                     (r1 * c1, -L / 2, r1 * s1)], "M_Trim_White")
        tunnel.face([(r0 * c0, L / 2, r0 * s0), (r1 * c0, L / 2, r1 * s0), (r1 * c1, L / 2, r1 * s1),
                     (r0 * c1, L / 2, r0 * s1)], "M_Trim_White")
    # bottom of the arch legs (closed)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * r1, sx * r0))
        tunnel.face([(x0, -L / 2, 0.0), (x0, L / 2, 0.0), (x1, L / 2, 0.0), (x1, -L / 2, 0.0)], SEC)

    aframe = MeshBuilder()
    Wd, Lh, H = 0.9, 1.25, 0.95
    prof = [(-Lh, 0.0), (Lh, 0.0), (0.0, H)]
    sub = MeshBuilder()
    # triangular prism along X (width) -> build in (y,z) profile, extrude along x
    A = [Vector((-Wd / 2, p[0], p[1])) for p in prof]
    B = [Vector((Wd / 2, p[0], p[1])) for p in prof]
    sub.face([A[0], A[2], A[1]], "M_Wood_Light")
    sub.face([B[0], B[1], B[2]], "M_Wood_Light")
    sub.face([A[0], A[1], B[1], B[0]], "M_Wood_Light")
    sub.face([A[1], A[2], B[2], B[1]], PRI)
    sub.face([A[2], A[0], B[0], B[2]], PRI)
    aframe.extend(F.bevelled(sub, 0.03))
    for t in (0.33, 0.66):   # contact-zone stripes / cleats
        for side in (-1, 1):
            p = Vector((0, side * Lh * (1 - t), H * t))
            aframe.box(-Wd / 2 - 0.01, p.y - 0.05, p.z - 0.03, Wd / 2 + 0.01, p.y + 0.05, p.z + 0.03, "M_Trim_White")
    return hurdle, tunnel, aframe


def _ball(mb, x, y, r, mat, z=0.0):
    mb.sphere(x, y, z + r, r, mat, seg=8, rings=5)


def _sack(mb, x, y, z, rot, mat=PRI):
    sub = bev_box(-0.32, -0.2, 0.0, 0.32, 0.2, 0.22, "M_Awning_Cream", bev=0.07)
    sub.box(-0.15, -0.205, 0.05, 0.15, 0.0, 0.17, mat, skip=("+y", "-z"))
    mb.extend(sub, Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z"))


def _aframe_sign():
    mb = MeshBuilder()
    w, h, sp = 0.6, 0.95, 0.24
    for sgn in (-1, 1):
        # one leaf, leaning
        top = Vector((0, 0, h))
        foot = Vector((0, sgn * sp, 0))
        leaf = MeshBuilder()
        leaf.box(-w / 2, -0.02, 0.0, w / 2, 0.02, (top - foot).length, "M_Trim_Wood")
        leaf.box(-w / 2 + 0.05, -0.035, 0.08, w / 2 - 0.05, -0.02, (top - foot).length - 0.06, "M_Sign_Board",
                 skip=("+y",))
        for i, (zz, ww) in enumerate(((0.62, 0.36), (0.5, 0.28), (0.38, 0.32))):
            leaf.box(-ww / 2, -0.045, zz, ww / 2, -0.035, zz + 0.05, "M_Sign_Face" if i else PRI, skip=("+y",))
        ang = math.atan2(sp, h) * sgn
        M = Matrix.Translation(foot) @ Matrix.Rotation(ang, 4, "X")
        if sgn > 0:
            M = M @ Matrix.Rotation(math.pi, 4, "Z")
        mb.extend(leaf, M)
    return mb


def _bowl(mb, x, y, z, r=0.2, mat=PRI):
    mb.cylinder(x, y, z, z + 0.1, r, mat, seg=12, cap_top=True, r_top=r * 1.15)
    mb.cylinder(x, y, z + 0.1, z + 0.105, r * 0.95, "M_Water", seg=12, cap_top=True)


# =============================================================================== construction cues
def portable_toilet():
    """Site portable toilet (1.15 x 1.15 x 2.35), door toward -Y. Origin at ground centre."""
    mb = MeshBuilder()
    mb.extend(bev_box(-0.6, -0.6, -0.05, 0.6, 0.6, 0.1, "M_Trim_White", bev=0.02))
    mb.extend(bev_box(-0.55, -0.55, 0.1, 0.55, 0.55, 2.15, "M_Awning_Blue", bev=0.04))
    roof = MeshBuilder()
    roof.cylinder(0, 0, 2.1, 2.32, 0.66, "M_Trim_White", seg=12, cap_top=True, r_top=0.5)
    mb.extend(roof)
    mb.box(-0.42, -0.585, 0.16, 0.42, -0.55, 1.98, "M_Awning_Teal", skip=("+y",))           # door
    mb.box(0.26, -0.62, 1.0, 0.34, -0.585, 1.12, "M_Trim_Dark", skip=("+y",))               # latch
    mb.box(-0.3, -0.6, 1.62, 0.3, -0.585, 1.72, "M_Trim_White", skip=("+y",))               # vent slot
    mb.box(-0.18, -0.6, 1.3, 0.18, -0.585, 1.5, "M_Awning_Red", skip=("+y",))               # occupied tag
    return mb


def timber_stack(L=3.0, W=1.15):
    """Stacked sawn timber on three bearers with two loose planks leaning on it. Origin ground centre."""
    mb = MeshBuilder()
    for x in (-L / 2 + 0.3, 0.0, L / 2 - 0.3):
        mb.box(x - 0.08, -W / 2 - 0.05, -0.05, x + 0.08, W / 2 + 0.05, 0.12, "M_Trim_Wood", skip=("-z",))
    z = 0.12
    for layer in range(5):
        n = 5 if layer % 2 == 0 else 4
        pw = W / 5.0
        off = 0.0 if layer % 2 == 0 else pw / 2
        for k in range(n):
            y0 = -W / 2 + off + k * pw + 0.012
            mb.box(-L / 2 + 0.03 * (k % 2), y0, z, L / 2 - 0.04 * ((k + layer) % 2), y0 + pw - 0.024, z + 0.14,
                   "M_Wood_Light", skip=("-z",))
        z += 0.15
        if layer in (1, 3):     # spacer sticks
            for x in (-L / 2 + 0.3, 0.0, L / 2 - 0.3):
                mb.box(x - 0.03, -W / 2, z, x + 0.03, W / 2, z + 0.04, "M_Trim_Wood", skip=("-z",))
            z += 0.04
    for (y, dy) in ((-0.28, 0.06), (0.22, -0.04)):        # two planks leaning on the stack end
        seg_box(mb, (L / 2 + 1.05, y, 0.0), (L / 2 - 0.1, y + dy, z + 0.02), 0.2, 0.05, "M_Wood_Light")
    # orange strap round the bundle
    mb.box(L / 2 - 0.62, -W / 2 - 0.01, 0.12, L / 2 - 0.55, W / 2 + 0.01, z + 0.01, "M_Hazard_Orange", skip=("-z",))
    return mb


def heap(r, h, mat, seed=0, seg=9):
    """Low-poly material heap (spoil / gravel / sand), origin at ground centre; base sinks to z -0.06."""
    import random
    rnd = random.Random(seed)
    mb = MeshBuilder()
    j = [rnd.uniform(0.85, 1.15) for _ in range(seg)]
    r0 = [Vector((r * j[i] * math.cos(TAU * i / seg), r * j[i] * math.sin(TAU * i / seg), -0.06)) for i in range(seg)]
    r1 = [Vector((0.55 * r * j[i] * math.cos(TAU * (i + 0.5) / seg), 0.55 * r * j[i] * math.sin(TAU * (i + 0.5) / seg),
                  h * rnd.uniform(0.55, 0.7))) for i in range(seg)]
    top = Vector((rnd.uniform(-0.1, 0.1) * r, rnd.uniform(-0.1, 0.1) * r, h))
    for i in range(seg):
        k = (i + 1) % seg
        mb.face([r0[i], r0[k], r1[i]], mat)
        mb.face([r1[i], r0[k], r1[k]], mat)
        mb.face([r1[i], r1[k], top], mat)
    return mb


def survey_tripod():
    """Surveyor's level on a yellow tripod (~1.55 m), sighting toward -Y. Origin at ground centre."""
    mb = MeshBuilder()
    top = Vector((0, 0, 1.3))
    for k in range(3):
        a = TAU * k / 3 + math.pi / 6
        foot = Vector((0.52 * math.cos(a), 0.52 * math.sin(a), -0.03))
        seg_box(mb, foot, top, 0.05, 0.05, "M_Awning_Yellow")
        mb.box(foot.x - 0.04, foot.y - 0.04, -0.05, foot.x + 0.04, foot.y + 0.04, 0.06, "M_Metal_Dark", skip=("-z",))
    mb.cylinder(0, 0, 1.26, 1.34, 0.13, "M_Metal_Dark", seg=8, cap_top=True, cap_bottom=True)
    mb.extend(bev_box(-0.11, -0.2, 1.34, 0.11, 0.18, 1.52, "M_Awning_Yellow", bev=0.025, skip_bottom=False))
    eye = MeshBuilder()
    eye.cylinder(0, 0, 0.0, 0.06, 0.055, "M_Trim_Dark", seg=8, cap_top=True)
    mb.extend(eye, front_matrix(0.0, -0.2, 1.44))
    mb.box(-0.025, 0.18, 1.4, 0.025, 0.24, 1.48, "M_Trim_Dark")
    return mb


# =============================================================================== lot layout
def _lot(S, spec, out):
    Wb = spec.W
    # ---- surfaces
    S.paving("Forecourt", local_poly(S, [(-4.85, -9.95), (5.0, -9.95), (5.0, BF), (-4.85, BF)]),
             "M_Plaza", z=Z_LOT, sub="PS_Ground")
    S.paving("GateApron", local_poly(S, [(-7.3, -9.95), (-4.85, -9.95), (-4.85, -8.15), (-7.3, -8.15)]),
             "M_Plaza", z=Z_LOT, sub="PS_Ground")
    S.paving("Doormat", local_poly(S, [(-0.2, -9.95), (1.7, -9.95), (1.7, BF - 0.15), (-0.2, BF - 0.15)]),
             "M_Plaza_Accent", z=Z_LOT + 0.012, skirt=0.05, sub="PS_Ground")
    S.paving("Driveway", local_poly(S, [(5.0, -9.95), (11.85, -9.95), (11.85, 9.95), (5.0, 9.95)]),
             "M_Concrete", z=Z_LOT, sub="PS_Ground")
    S.paving("BackYard", local_poly(S, [(-4.85, BF + spec.D), (5.0, BF + spec.D), (5.0, 9.95), (-4.85, 9.95)]),
             "M_Gravel", z=-0.02, skirt=0.1, sub="PS_Ground")
    # CONNECTORS across the 1.8-2.7 m grass verge to the Maple St sidewalk (deliberate small extensions
    # beyond the lot, connectors only): a 4.9 m M_Plaza apron on the door axis (spawn -> door) and the
    # driveway mouth. Both start under the forecourt / driveway edge and end 0.35 m under the 0.15 kerb
    # (top 0.14, so nothing z-fights with the sidewalk or the forecourt).
    fwd = Vector(S.facing)
    for nm, x0, x1, mat in (("FrontApron", -2.0, 2.9, "M_Plaza"), ("DrivewayMouth", 5.0, 11.85, "M_Concrete")):
        cp = connector_poly(S, S.to_world(x0, -9.7), S.to_world(x1, -9.7), fwd, n=3)
        if cp:
            S.paving(nm, cp, mat, z=Z_LOT - 0.01, skirt=0.25, sub="PS_Ground")
            S.register_lot(cp)
            out.setdefault("connectors", {})[nm] = round(max((p - S.to_world((x0 + x1) / 2, -9.7)).length
                                                         for p in cp), 2)
    g = MeshBuilder()
    sand = ellipse(-8.0, 0.2, 2.3, 4.2, 18)
    g.tri_fill([G.ensure_ccw([Vector(S.to_world(*p)) for p in sand])], -0.03, "M_Sand")
    S.mesh("PlayYard_Sand", g, sub="PS_PlayYard")
    # painted loading bay + van bay lines on the driveway
    pl = MeshBuilder()

    def line(a, b, w=0.12, mat="M_RoadLine_Yellow"):
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        n = Vector((-d.y, d.x)) * (w / 2)
        q = [a - n, b - n, b + n, a + n]
        pl.tri_fill([G.ensure_ccw([Vector(S.to_world(p.x, p.y)) for p in q])], Z_LOT + 0.008, mat)
    for (a, b) in (((6.4, 4.0), (10.6, 4.0)), ((10.6, 4.0), (10.6, 9.6)), ((6.4, 4.0), (6.4, 9.6))):
        line(a, b)
    for k in range(6):      # hatching inside the loading box
        y = 4.6 + k * 0.9
        line((6.6, y), (7.4, y + 0.6), 0.1)
    S.mesh("Driveway_Paint", pl, sub="PS_Delivery")

    # ---- play yard fence (white pickets, front gate from the forecourt, back gate to the yard)
    fz = None
    pick = Fence(S, "Fence_Picket_3m", sub="PS_PlayYard", z=fz)
    x_e, x_w = -11.7, -4.85
    yf, yb = -8.1, 9.6
    pick.line([(x_w, BF - 0.2), (x_w, yf), (x_e, yf), (x_e, yb), (x_w, yb), (x_w, BF + spec.D + 0.25)],
              gates=[(1, (6.05 - 4.85) / 6.85, 1.2), (3, 0.62, 1.2)])
    # ---- west boundary privacy fence (beside the driveway) and short return at the back corner
    Fence(S, "Fence_Wood_3m", sub="PS_Delivery").line([(11.85, -2.0), (11.85, 9.9)])

    # ---- play yard contents
    hurdle, tunnel, aframe = _agility()
    emit(S, "PlayYard_Hurdle_A", hurdle, -8.3, -3.9, 0.0 + S.ground_z(*S.to_world(-8.3, -3.9)), sub="PS_PlayYard")
    emit(S, "PlayYard_Hurdle_B", hurdle, -7.6, -1.4, S.ground_z(*S.to_world(-7.6, -1.4)), rot=0.25, sub="PS_PlayYard")
    emit(S, "PlayYard_Tunnel", tunnel, -8.3, 2.9, S.ground_z(*S.to_world(-8.3, 2.9)), rot=0.15, sub="PS_PlayYard")
    emit(S, "PlayYard_AFrame", aframe, -10.15, -0.7, S.ground_z(*S.to_world(-10.15, -0.7)), rot=0.08,
         sub="PS_PlayYard")
    S.put("Doghouse", -10.5, 7.9, recolor={"wall": PRI, "roof": SEC, "trim": "M_Trim_White", "sign": SEC},
          rot=0.1, local=True, sub="PS_PlayYard")
    S.put("Doghouse", -8.2, 8.3, recolor={"wall": SEC, "roof": PRI, "trim": "M_Trim_White", "sign": PRI},
          rot=-0.2, local=True, sub="PS_PlayYard")
    S.put("Birdbath", -5.9, 6.4, local=True, sub="PS_PlayYard")
    S.put("Tree_Small", -10.9, 4.6, recolor={"foliage": "M_Foliage"}, local=True, sub="PS_PlayYard")
    S.put("Bush_B", -10.8, -6.9, rot=0.4, local=True, sub="PS_PlayYard")
    S.put("Bush_A", -5.7, -7.3, rot=1.3, local=True, sub="PS_PlayYard")
    S.put("Bush_A", -11.0, 1.9, rot=2.3, local=True, sub="PS_PlayYard")
    toys = MeshBuilder()
    for (x, y, r, m) in ((-6.6, -4.9, 0.17, PRI), (-9.3, 5.4, 0.15, SEC), (-6.2, 2.2, 0.13, "M_Awning_Yellow")):
        p = S.to_world(x, y)
        _ball(toys, p.x, p.y, r, m, z=S.ground_z(p.x, p.y))
    for (x, y) in ((-5.6, 7.6), (-7.0, 8.4)):
        p = S.to_world(x, y)
        _bowl(toys, p.x, p.y, S.ground_z(p.x, p.y), 0.19, PRI if x < -6 else SEC)
    S.mesh("PlayYard_Toys", toys, sub="PS_PlayYard")
    hb = hay_bale()
    hbs = MeshBuilder()
    for (x, y, z, r) in ((-11.0, -3.4, 0.0, 1.57), (-11.0, -4.6, 0.0, 1.57), (-11.0, -4.0, 0.48, 1.62)):
        hbs.extend(rz(hb, S.rot + r, *S.to_world(x, y), z + S.ground_z(*S.to_world(x, y))))
    S.mesh("PlayYard_HayBales", hbs, sub="PS_PlayYard")

    # ---- front planting strip outside the pen + forecourt furniture
    S.put("Flowerbed_2m", -10.3, -9.1, local=True, sub="PS_Forecourt")
    S.put("Flowerbed_2m", -8.3, -9.1, local=True, sub="PS_Forecourt", recolor={"foliage": "M_Foliage_Light"})
    S.put("Planter", -4.15, -7.0, z=Z_LOT, recolor={"trim": PRI}, local=True, sub="PS_Forecourt")
    S.put("Planter", 4.15, -7.0, z=Z_LOT, recolor={"trim": PRI}, local=True, sub="PS_Forecourt")
    S.put("Bench", -2.55, -7.25, z=Z_LOT, local=True, sub="PS_Forecourt")
    S.put("TrashBin", -3.75, -8.6, z=Z_LOT, local=True, sub="PS_Forecourt")
    S.put("BikeRack", 3.75, -9.35, z=Z_LOT, local=True, sub="PS_Forecourt")
    fc = MeshBuilder()
    fc.extend(_aframe_sign())
    emit(S, "Forecourt_Chalkboard", fc, -0.85, -9.1, Z_LOT, rot=-0.3, sub="PS_Forecourt")
    bw = MeshBuilder()
    p = S.to_world(1.75, -6.85)
    _bowl(bw, p.x, p.y, Z_LOT, 0.2, SEC)
    S.mesh("Forecourt_WaterBowl", bw, sub="PS_Forecourt")

    # ---- delivery: branded van, loading clutter by the back door
    S.put("Car_Van", 8.45, -1.6, z=Z_LOT, recolor={"awning": PRI, "sign": SEC}, local=True, sub="PS_Delivery",
          name="LM_PetShop_DeliveryVan")
    # van livery: paw disc on the windowless cargo panel (y 0.6..2.4, z 1.04..2.2) and cream "PET SHOP"
    # lettering under the belt stripe between the wheel arches (y -1.1..1.15, z 0.27..0.9), both sides
    decal = MeshBuilder()
    vtxt = text_mb("PET SHOP", 0.27, 0.02, "M_Sign_Face", max_w=1.95)
    for sx in (-1, 1):
        sub = MeshBuilder()
        for shp in paw_shapes(0.7):
            sub.prism(shp, 0.0, 0.025, SEC, SEC)
        sub.cylinder(0, 0, -0.012, 0.0, 0.5, "M_Awning_Cream", seg=20, cap_top=True)
        # van side at |x| = 1.0 ; plane faces +-X; u along +-Y
        right = (0, sx, 0)
        M = plane_matrix((sx * 1.0, 1.5, 1.6), right, (0, 0, 1))
        decal.extend(sub, M)
        # text faces -Y in its own frame: Rz(+90) turns it toward +X (reads left->right = +Y), Rz(-90) to -X
        decal.extend(vtxt, Matrix.Translation((sx * 1.003, 0.05, 0.6)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Z"))
    emit(S, "DeliveryVan_Livery", decal, 8.45, -1.6, Z_LOT, sub="PS_Delivery")
    S.put("Pallet", 4.2, 5.2, z=-0.02, rot=0.1, local=True, sub="PS_Delivery")
    S.put("Pallet", 4.2, 5.2, z=0.127, rot=0.15, local=True, sub="PS_Delivery")
    S.put("CrateStack", 3.9, 7.4, z=-0.02, rot=1.57, local=True, sub="PS_Delivery")
    S.put("Crate", 2.3, 6.2, z=-0.02, rot=0.4, local=True, sub="PS_Delivery")
    S.put("Barrel", 1.1, 3.4, z=-0.02, local=True, sub="PS_Delivery")
    S.put("TrashBin", -0.2, 3.3, z=-0.02, local=True, sub="PS_Delivery")
    S.put("TrashBin", -1.0, 3.3, z=-0.02, local=True, sub="PS_Delivery")
    S.put("Dumpster", -3.2, 3.6, z=-0.02, local=True, sub="PS_Delivery")
    sacks = MeshBuilder()
    for (x, y, z, r, m) in ((4.0, 5.0, 0.274, 0.1, PRI), (4.45, 5.4, 0.274, 0.2, SEC), (4.1, 5.5, 0.494, 0.05, PRI),
                            (5.6, 2.9, Z_LOT, 1.4, SEC)):
        p = S.to_world(x, y)
        _sack(sacks, p.x, p.y, z, S.rot + r, m)
    S.mesh("Delivery_FeedSacks", sacks, sub="PS_Delivery")


# =============================================================================== expansion plot
def _expansion(S, out):
    E = [S.to_local(p) for p in S.data.get("expansion_poly", [])]
    if len(E) < 3:
        return
    Ew = [Vector(p) for p in S.data["expansion_poly"]]
    # ---- plain, slightly dry grass inside the fence (unused land, NOT a mowed sports lawn) + gravel drive
    inner = G.offset_polygon_radial(G.ensure_ccw(Ew), G.centroid(Ew), 0.6)
    S.paving("Expansion_DryGrass", inner, "M_Grass_Dry", z=-0.036, skirt=0.04, sub="PS_Expansion")
    drive = [(5.6, 10.6), (11.6, 10.6), (13.6, 42.6), (7.6, 43.3)]
    S.paving("Expansion_Drive", local_poly(S, drive), "M_Gravel", z=-0.012, skirt=0.08, sub="PS_Expansion")
    park = [(13.6, 31.0), (33.5, 28.8), (34.6, 37.3), (14.6, 39.9)]
    S.paving("Expansion_Parking", local_poly(S, park), "M_Gravel", z=-0.014, skirt=0.08, sub="PS_Expansion")
    pm = MeshBuilder()
    for k in range(6):      # parking stall lines
        x = 16.2 + k * 3.2
        a = Vector((x, 31.0 - (x - 13.6) * 0.1106 + 0.4))
        b = Vector((x + 0.9, 39.9 - (x + 0.9 - 14.6) * 0.13 - 0.5))
        d = (b - a).normalized()
        n = Vector((-d.y, d.x)) * 0.06
        q = [S.to_world(*(a - n)), S.to_world(*(b - n)), S.to_world(*(b + n)), S.to_world(*(a + n))]
        pm.tri_fill([G.ensure_ccw(q)], 0.0, "M_RoadLine_White")
    S.mesh("Expansion_ParkingLines", pm, sub="PS_Expansion")

    # ---- future plots = construction footprints: KENNELS dug-out dirt pad with timber formwork and a poured
    # footing strip carrying the run posts, BREEDING ROOMS levelled gravel pad + survey strings, AVIARY dirt disc
    ken = [(-17.5, 16.0), (-3.0, 16.0), (-3.0, 23.0), (-17.5, 23.0)]
    S.paving("Plot_Kennels_Dirt", local_poly(S, ken), "M_Dirt", z=-0.02, skirt=0.06, sub="PS_Expansion")
    S.paving("Plot_Kennels_Footing", local_poly(S, [(-17.5, 21.9), (-3.0, 21.9), (-3.0, 23.0), (-17.5, 23.0)]),
             "M_Concrete", z=0.1, skirt=0.15, sub="PS_Expansion")
    # breeding rooms: scraped, irregular dirt patch a little larger than the staked outline (reads as ground
    # works, not as a court), a gravel heap and a sand heap waiting on it
    brd = [(14.3, 13.0), (19.0, 12.6), (24.5, 12.9), (31.6, 12.7), (31.9, 17.5), (31.5, 24.4), (26.0, 24.9),
           (20.5, 24.5), (14.6, 24.8), (14.1, 19.2)]
    S.paving("Plot_Breeding_Dirt", local_poly(S, brd), "M_Dirt", z=-0.018, skirt=0.06, sub="PS_Expansion")
    for nm, (x, y), r, h, mat, sd in (("GravelHeap", (28.6, 16.2), 1.5, 1.05, "M_Gravel", 3),
                                      ("SandHeap", (26.3, 21.4), 1.2, 0.8, "M_Sand", 5),
                                      ("SpoilHeap", (-5.6, 25.8), 1.7, 1.15, "M_Dirt", 7)):
        emit(S, f"Expansion_{nm}", heap(r, h, mat, sd), x, y, S.ground_z(*S.to_world(x, y)), sub="PS_Expansion")
    fw = MeshBuilder()

    def formwork(pts):
        """Low timber shuttering boards (0.06 x 0.22) along a local polyline + pegs."""
        W = [Vector((*S.to_world(*p), 0.0)) for p in pts]
        for i in range(len(W) - 1):
            a, b = W[i], W[i + 1]
            seg_box(fw, a + Vector((0, 0, 0.06)), b + Vector((0, 0, 0.06)), 0.06, 0.22, "M_Wood_Light")
            L = (b - a).length
            for k in range(int(L / 2.4) + 1):
                q = a.lerp(b, min(1.0, k * 2.4 / L)) if L > 1e-6 else a
                fw.box(q.x - 0.04, q.y - 0.04, -0.05, q.x + 0.04, q.y + 0.04, 0.32, "M_Trim_Wood", skip=("-z",))
    formwork([(-3.0, 21.9), (-3.0, 16.0), (-17.5, 16.0), (-17.5, 21.9)])
    formwork([(15.0, 19.0), (15.0, 13.5), (23.0, 13.5)])
    S.mesh("Plots_Formwork", fw, sub="PS_Expansion")
    stk = MeshBuilder()

    def stake(x, y, h=0.75):
        p = S.to_world(x, y)
        z = S.ground_z(p.x, p.y)
        stk.box(p.x - 0.05, p.y - 0.05, z, p.x + 0.05, p.y + 0.05, z + h, "M_Wood_Light", skip=("-z",))
        stk.box(p.x - 0.055, p.y - 0.055, z + h - 0.16, p.x + 0.055, p.y + 0.055, z + h - 0.04, "M_Hazard_Orange",
                skip=("-z", "+z"))
        return Vector((p.x, p.y, z + h - 0.1))

    def string_line(pts, closed=True):
        tops = [stake(x, y) for x, y in pts]
        n = len(tops)
        for i in range(n if closed else n - 1):
            seg_box(stk, tops[i], tops[(i + 1) % n], 0.04, 0.04, "M_Hazard_Orange")
    # breeding rooms: orange survey string around the pad + the room divider
    string_line([(15.0, 13.5), (31.0, 13.5), (31.0, 24.0), (15.0, 24.0)])
    string_line([(23.0, 13.5), (23.0, 24.0)], closed=False)
    # kennel runs: posts along the slab back edge marking 5 runs
    for k in range(6):
        x = -17.0 + k * 2.75
        p = S.to_world(x, 22.6)
        stk.extend(bev_box(p.x - 0.07, p.y - 0.07, 0.1, p.x + 0.07, p.y + 0.07, 1.6, "M_Metal", bev=0.02))
    # aviary: staked circle + centre pole
    av_c = Vector((-9.0, 34.0))
    av_r = 5.2
    ring = [(av_c.x + av_r * math.cos(TAU * i / 10), av_c.y + av_r * math.sin(TAU * i / 10)) for i in range(10)]
    string_line(ring)
    pc = S.to_world(av_c.x, av_c.y)
    stk.cylinder(pc.x, pc.y, -0.05, 3.2, 0.09, "M_Wood_Light", seg=8)
    stk.cylinder(pc.x, pc.y, 2.9, 3.25, 0.12, "M_Hazard_Orange", seg=8)
    S.mesh("Expansion_StakesStrings", stk, sub="PS_Expansion")
    S.paving("Plot_Aviary_Dirt", [Vector(S.to_world(*p)) for p in ellipse(av_c.x, av_c.y, av_r + 0.6, av_r + 0.6, 24)],
             "M_Dirt", z=-0.02, skirt=0.06, sub="PS_Expansion")

    # ---- plot marker boards with pictograms (orange boards, cream pictos)
    house = [(-0.32, -0.28), (0.32, -0.28), (0.32, 0.08), (0.0, 0.34), (-0.32, 0.08)]
    door = [(-0.1, -0.28), (0.1, -0.28), (0.1, -0.02), (-0.1, -0.02)]
    bird = ellipse(0.0, 0.0, 0.3, 0.18, 14)
    dome = [(-0.34, -0.25), (0.34, -0.25)] + [(0.34 * math.cos(a), -0.05 + 0.34 * math.sin(a))
                                                 for a in [math.pi * k / 10 for k in range(0, 11)]]
    dome = [dome[0], dome[1]] + dome[2:]
    markers = [("Kennels", (-10.5, 14.6), [([house], 0.0, 0.55)]),
               ("Breeding", (19.0, 12.2), [([heart_shape(0.62)], 0.0, 0.5)]),
               ("Aviary", (-9.0, 27.6), [([G.ensure_ccw([Vector(p) for p in dome])], 0.0, 0.5)])]
    for nm, (x, y), pict in markers:
        b = sign_board(1.3, 1.05, PRI, frame="M_Trim_White", post_h=0.85, pictos=pict)
        emit(S, f"Plot_{nm}_Marker", b, x, y, S.ground_z(*S.to_world(x, y)), sub="PS_Expansion")

    # ---- big "coming soon" board facing the shop yard; two-sided so the Kennel Lane gate side reads too
    # (paw + orange "+" + house = the shop will grow here)
    plus = MeshBuilder()
    plus.box(-0.25, -0.06, -0.07, 0.25, 0.0, 0.07, PRI, skip=("+y",))
    plus.box(-0.07, -0.06, -0.25, 0.07, 0.0, 0.25, PRI, skip=("+y",))
    big = sign_board(4.2, 2.1, SEC, frame="M_Trim_White", post_h=1.2, depth=0.16, two_sided=True,
                     pictos=[(paw_shapes(1.25), -1.2, 1.05), ([house], 0.95, 1.0)], picto_mat="M_Sign_Face",
                     extra=[(plus, -0.05, 1.05)])
    emit(S, "Expansion_ComingSoonBoard", big, 1.5, 14.2, S.ground_z(*S.to_world(1.5, 14.2)), sub="PS_Expansion")

    # ---- construction clutter: container, pallets, crates, barriers, cones
    S.put("Container_6m", 35.0, 27.5, rot=math.radians(82.4), recolor={"awning": SEC}, local=True, sub="PS_Expansion",
          name="LM_PetShop_SiteContainer")
    # vertical construction cues by the site container: portable toilet, timber stack, survey tripod
    emit(S, "Expansion_PortableToilet", portable_toilet(), 36.0, 33.3, S.ground_z(*S.to_world(36.0, 33.3)),
         rot=face_rot(-1.0, -0.3), sub="PS_Expansion")
    emit(S, "Expansion_TimberStack", timber_stack(), 31.4, 25.8, S.ground_z(*S.to_world(31.4, 25.8)),
         rot=math.pi + 0.04, sub="PS_Expansion")
    emit(S, "Expansion_SurveyTripod", survey_tripod(), 24.6, 25.1, S.ground_z(*S.to_world(24.6, 25.1)),
         rot=face_rot(-0.25, -1.0), sub="PS_Expansion")
    for (x, y, r, n) in ((1.0, 26.4, 0.2, 4), (3.0, 26.8, 0.05, 2)):
        for k in range(n):
            S.put("Pallet", x, y, z=-0.05 + k * 0.147, rot=r + 0.05 * k, local=True, sub="PS_Expansion")
    S.put("CrateStack", 0.2, 29.2, rot=0.6, local=True, sub="PS_Expansion")
    S.put("Crate", 2.5, 29.5, rot=0.2, local=True, sub="PS_Expansion")
    S.put("Barrel", 4.3, 28.0, local=True, sub="PS_Expansion")
    S.put("Barrel", 4.6, 28.8, local=True, sub="PS_Expansion")
    for (x, y, r) in ((-18.0, 25.5, 0.0), (-15.6, 25.5, 0.0), (32.0, 23.0, 1.57), (32.0, 20.6, 1.57)):
        S.put("Barrier", x, y, rot=r, local=True, sub="PS_Expansion")
    for (x, y) in ((-3.0, 15.4), (-17.5, 15.4), (23.0, 12.8), (31.6, 12.8), (14.4, 13.0), (-3.6, 23.6)):
        S.put("TrafficCone", x, y, local=True, sub="PS_Expansion")
    hb = hay_bale()
    hbs = MeshBuilder()
    for (x, y, z, r) in ((26.0, 26.4, 0.0, 0.1), (27.2, 26.4, 0.0, 0.1), (26.6, 26.5, 0.48, 0.15)):
        hbs.extend(rz(hb, S.rot + r, *S.to_world(x, y), z + S.ground_z(*S.to_world(x, y))))
    S.mesh("Expansion_HayBales", hbs, sub="PS_Expansion")
    S.put("Tree_Round_A", 34.0, 13.8, local=True, sub="PS_Expansion", recolor={"foliage": "M_Foliage"})
    S.put("Tree_Round_B", -14.5, 39.5, local=True, sub="PS_Expansion", recolor={"foliage": "M_Foliage_Dark"})

    # ---- chain-link construction fence (open toward the shop lot; wide gate to Kennel Lane)
    fence = Fence(S, "Fence_Chain_3m", sub="PS_ExpansionFence")
    P = [Vector(p) for p in E]           # (12.09,10.5) (-11.92,10.47) (-22.15,13.24) (-17.58,47.54) (39.91,39.88) (36.01,10.54)
    c = G.centroid(P)
    Pi = [c + (p - c) * ((p - c).length - 0.7) / (p - c).length for p in P]
    a, b = Pi[3], Pi[4]
    L = (b - a).length
    tg = (Vector((10.5, 0)) - a).x / (b - a).x if abs((b - a).x) > 1e-6 else 0.5
    GW = 4.6
    fence.line([Pi[1], Pi[2], Pi[3], Pi[4], Pi[5], Pi[0]], gates=[(2, tg, None, GW)])
    # gate leaves standing open in the Kennel Lane opening
    g0 = a + (b - a) * (tg - GW / 2 / L)
    g1 = a + (b - a) * (tg + GW / 2 / L)
    d = (b - a).normalized()
    for gp_, sgn in ((g0, -1), (g1, 1)):
        ang = math.atan2(d.y, d.x) + (math.radians(-110) if sgn < 0 else math.radians(290))   # both swing inward
        m = gp_ + Vector((math.cos(ang), math.sin(ang))) * 0.75
        S.put("Fence_Chain_3m", m.x, m.y, rot=ang, scale=(0.5, 1, 1), local=True, sub="PS_ExpansionFence")
        S.put("TrafficCone", (gp_ - d * sgn * 0.6).x, (gp_ - d * sgn * 0.6).y + 0.0, local=True, sub="PS_ExpansionFence")
    # gravel connector from the drive end through the gate to the Kennel Lane asphalt edge (deliberate small
    # extension beyond the plot; ends 0.35 m under the asphalt edge, top below ROAD_Z)
    cp = connector_poly(S, S.to_world(13.6, 42.6), S.to_world(7.6, 43.3), -Vector(S.facing), n=3)
    if cp:
        S.paving("Expansion_GateDrive", cp, "M_Gravel", z=-0.014, skirt=0.08, sub="PS_Expansion")
        S.register_lot(cp)
        out.setdefault("connectors", {})["GateDrive"] = round(max((p - S.to_world(10.6, 42.6)).length for p in cp), 2)
    S.register_lot(Ew)


# =============================================================================== entry point
def build(S):
    out = {}
    import bpy
    before = set(o.name for o in bpy.data.objects)
    spec = _shop(S, out)
    _lot(S, spec, out)
    _expansion(S, out)
    S.register_lot(S.poly)
    new = [o for o in bpy.data.objects if o.name not in before]
    custom = [o for o in new if o.type == "MESH" and o.data.users == 1 and o.name.startswith("LM_PetShop_")]
    out["custom_tris"] = tri_count(custom)
    out["instances"] = S.n
    out["objects"] = len(new)
    return out
