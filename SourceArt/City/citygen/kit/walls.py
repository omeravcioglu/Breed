"""Kit family: WALLS & OPENINGS (facade modules and corners). See docs/KIT_SPEC.md.

Conventions (KIT_SPEC): front faces -Y, origin bottom-center on the facade plane y = 0, wall body
in y [0, 0.3], everything that sticks out of the facade goes to y < 0. Full modules span
x [-1.5, 1.5], half modules x [-0.75, 0.75]. Corners: origin on the outer building corner, authored
for the front-right corner (building at x <= 0, y >= 0).

Pieces (category "Walls"):
    KIT_Wall_Plain_H3 / _H4, KIT_Wall_Half_H3 / _H4, KIT_Wall_Window_H3, KIT_Wall_WindowPair_H3,
    KIT_Wall_WindowWide_H3, KIT_Wall_WindowShutter_H3, KIT_Wall_BalconyDoor_H3, KIT_Wall_Door_H3,
    KIT_Wall_DoorGlass_H3, KIT_Wall_Garage_H3, KIT_Wall_Window_H4, KIT_Wall_Door_H4,
    KIT_Wall_Storefront_H4, KIT_Wall_StorefrontDoor_H4, KIT_Wall_RollerDoor_H4,
    KIT_Wall_Industrial_H3 / _H4, KIT_Wall_IndustrialWindow_H3
Pieces (category "Corners"):
    KIT_Corner_H3 / _H4, KIT_Corner_Industrial_H3 / _H4
Extra pieces (not in the spec list):
    KIT_Wall_StorefrontDoorL_H4 - mirror of KIT_Wall_StorefrontDoor_H4 with the door on the LEFT
        (-X) side. Placing ...StorefrontDoor_H4 then ...StorefrontDoorL_H4 side by side gives a
        centred double shop entrance flanked by display windows.
    KIT_Wall_StorefrontCorner_H4 / KIT_Wall_StorefrontCornerL_H4 - display window for the module
        next to a building corner: glass x [-1.3, 1.0] plus a solid 0.5 m wall pier toward +X
        (L: mirrored, pier toward -X), so the KIT_Corner pilaster (|x| >= 1.28) hides no post.
        meta corner_side = "+x" / "-x" says which end may touch the corner.
    KIT_Wall_IndustrialDoor_H4 - the KIT_Wall_Door_H4 service door (frames in M_Trim_Dark) set into
        the ribbed industrial cladding, so warehouses keep a continuous corrugated facade.
    KIT_Wall_IndustrialDoor_H3 - same 1.0 x 2.3 service door (no transom) in an H3 industrial wall.
    KIT_Wall_IndustrialWindow_H4 - the H3 ribbon window (2.8 x 1.1, 3 mullions, dark frames,
        continuous sill) raised to z 2.4 .. 3.5 in a 4 m industrial wall; tiles into a ribbon.
    KIT_Wall_IndustrialWindowEnd_H3 / _H4 - ribbon window whose continuous sill runs 0.14 m past
        +X (meta corner_end = "+x"). Use it for the module whose +X end is at an outer corner: the
        sill return fills the 0.14 x 0.14 notch where the front and side ribbon sills meet.
    KIT_Wall_GarageGrade_H3 - garage module for houses raised 0.35 above the lot: wall body and the
        2.6 x 2.65 door run down to z = -0.35 (meta grade_drop = 0.35), head stays at the H3 datum.

Shared vertical datums so modules line up along one facade (all published in meta, see below):
    residential window heads z 2.45 (frame top 2.54) (H3); storefront glass z 0.45 .. 3.05 with the
    transom bar at z 2.60 .. 2.68 (H4, all storefront modules); door transoms sit on the door head.

Meta (every piece): height, module (width), kind (plain / window / door / garage / storefront /
industrial / corner / corner_industrial). Opening modules also publish numeric snap datums:
    opening       (x0, z0, x1, z1) of the main opening (door leaf + transom for doors, glass for
                  storefronts / windows)          openings  flat tuple, 4 floats per opening
    opening_kind  window / door / glass / garage / roller
    head_top_z    top of the head frame (canopies / awnings / signs snap above this)
    sill_top_z, sill_bottom_z    window sills
    threshold_z   top of the door threshold slab (door modules)
    trim_x        max |x| reached by frames / posts / jambs / housings standing proud of the facade
    corner_ok     True if the module may sit next to a KIT_Corner pilaster (trim_x <= 1.28)
    corner_ok_industrial    same against KIT_Corner_Industrial flashing (clear of |x| >= 1.37, or the
                  trim is shallower than the 0.085 flashing and tucks under it)
    corner_side   asymmetric corner variants only: the one end ("+x" / "-x") that may touch the
                  corner; trim_x / corner_ok then describe that end (far_trim_x the other one)
    storefronts: kick_z 0.35 (bulkhead top), ledge_z 0.45 (display ledge top = glass bottom)
    roller door: housing_z (3.38, 3.95), housing_x 1.40
Door modules carry a 0.03 m threshold slab from the frame face to the leaf (no see-through floor
gap inside the reveal).
"""
import math

from mathutils import Matrix, Vector

from .. import config as C
from .. import facade as F
from ..meshutil import MeshBuilder

W = C.MODULE_W
H3 = C.FLOOR_H
H4 = C.SHOP_FLOOR_H
FAM = "walls"

WALL = "M_Wall_Cream"      # recolor: wall
TRIM = "M_Trim_White"      # recolor: trim
DOOR = "M_Door_Wood"       # recolor: door
GLASS = "M_Glass"
SHOP_GLASS = "M_Glass_Shop"
DARK = "M_Trim_Dark"
METAL = "M_Metal"
METAL_DK = "M_Metal_Dark"
ROLLER = "M_RollerDoor"
CONC = "M_Concrete"

CORNER_CLEAR = W / 2 - 0.22        # KIT_Corner pilaster reaches |x| >= 1.28 on a corner module
IND_CLEAR = W / 2 - 0.13           # KIT_Corner_Industrial flashing legs reach |x| >= 1.37
IND_FLASH_D = 0.085                # ... standing 0.085 proud
THRESH_T = 0.03                    # door threshold slab thickness


# =============================================================================== local helpers
def _newell(P):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def _poly(mb, pts, mat, n):
    """Planar polygon; winding is fixed so the face normal points along *n* (safe for Unity)."""
    P = [Vector(p) for p in pts]
    if _newell(P).dot(Vector(n)) < 0:
        P.reverse()
    mb.face(P, mat)


def _front(mb, x0, x1, z0, z1, y, mat):
    """Single quad at depth y facing -Y (x0 < x1, z0 < z1)."""
    mb.face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], mat)


def _frame_at(mb, hole, y, mat, w=F.FRAME_W, d=F.FRAME_D, bottom=True, on_sill=False):
    """Picture frame around *hole* standing proud of plane y by d (hidden faces skipped).

    on_sill: the jamb feet rest on a sill / the ground, so their bottom faces are dropped.
    """
    x0, z0, x1, z1 = hole
    zb = z0 - (w if bottom else 0.0)
    jskip = ("+y", "+z") + (("-z",) if on_sill or (not bottom and z0 < 1e-4) else ())
    mb.box(x0 - w, y - d, z1, x1 + w, y, z1 + w, mat, skip=("+y",))
    mb.box(x0 - w, y - d, zb, x0, y, z1, mat, skip=jskip)
    mb.box(x1, y - d, zb, x1 + w, y, z1, mat, skip=jskip)
    if bottom:
        mb.box(x0, y - d, z0 - w, x1, y, z0, mat, skip=("+y", "-x", "+x"))


def _raised(mb, x0, x1, z0, z1, y, h, inset, mat):
    """Raised panel (frustum) on plane y: chamfered sides give a soft moulded edge for 10 tris."""
    i = inset
    B = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    Fr = [(x0 + i, y - h, z0 + i), (x1 - i, y - h, z0 + i), (x1 - i, y - h, z1 - i), (x0 + i, y - h, z1 - i)]
    _poly(mb, Fr, mat, (0, -1, 0))
    _poly(mb, [B[0], B[1], Fr[1], Fr[0]], mat, (0, -1, -1))
    _poly(mb, [B[1], B[2], Fr[2], Fr[1]], mat, (1, -1, 0))
    _poly(mb, [B[2], B[3], Fr[3], Fr[2]], mat, (0, -1, 1))
    _poly(mb, [B[3], B[0], Fr[0], Fr[3]], mat, (-1, -1, 0))


def _glaze(mb, hole, y, mat=GLASS, xs=(), zs=(), bar=TRIM, bw=0.06, bd=0.035, pad=0.0):
    """Glass pane at depth y with mullions at explicit x / transoms at explicit z positions.

    pad > 0 enlarges the pane so it can sit hidden behind a door leaf / panel with a hole.
    """
    x0, z0, x1, z1 = hole
    _front(mb, x0 - pad, x1 + pad, z0 - pad, z1 + pad, y, mat)
    for x in xs:
        mb.box(x - bw / 2, y - bd, z0, x + bw / 2, y, z1, bar, skip=("+y", "-z", "+z"))
    for z in zs:
        mb.box(x0, y - bd, z - bw / 2, x1, y, z + bw / 2, bar, skip=("+y", "-x", "+x"))


def _win(mb, hole, xs=(), zs=(), glass=GLASS, fr=TRIM, wall=WALL, sill=True, depth=F.REVEAL, bw=0.06):
    """Recessed window like facade.window() but with explicit mullion / transom positions."""
    F.reveal(mb, hole, depth, wall)
    _glaze(mb, hole, depth, glass, xs, zs, fr, bw=bw)
    _frame_at(mb, hole, 0.0, fr, on_sill=sill)
    if sill:
        F.sill(mb, hole, fr)


def _threshold(mb, x0, x1, y0, y1, mat, z0=0.0, t=THRESH_T):
    """Door threshold slab in the opening, from the frame face (y0 < 0) back to the leaf plane y1.

    Only the top and the front are visible: the ends hide against the jambs / reveal, the bottom
    on the ground and the back behind the door leaf (4 tris).
    """
    mb.box(x0, y0, z0, x1, y1, z0 + t, mat, skip=("-z", "+y", "-x", "+x"))


def _vrib(mb, x, z0, z1, mat, wb=0.2, wt=0.085, d=0.07, top=True, bottom=False):
    """Vertical trapezoid cladding rib on the facade (x centre), z0..z1."""
    prof = [(x - wb / 2, 0.0), (x - wt / 2, -d), (x + wt / 2, -d), (x + wb / 2, 0.0)]
    mb.wall(prof, z0, z1, mat)          # normals right of travel = outward
    if top:
        _poly(mb, [(p[0], p[1], z1) for p in prof], mat, (0, 0, 1))
    if bottom:
        _poly(mb, [(p[0], p[1], z0) for p in prof], mat, (0, 0, -1))


def _hrib(mb, x0, x1, zc, y, mat, hb=0.045, ht=0.022, d=0.03):
    """Horizontal trapezoid rib on plane y (roller door slats). Ends are hidden by guides."""
    yf = y - d
    _poly(mb, [(x0, yf, zc - ht), (x1, yf, zc - ht), (x1, yf, zc + ht), (x0, yf, zc + ht)], mat, (0, -1, 0))
    _poly(mb, [(x0, yf, zc + ht), (x1, yf, zc + ht), (x1, y, zc + hb), (x0, y, zc + hb)], mat, (0, -1, 1))
    _poly(mb, [(x0, y, zc - hb), (x1, y, zc - hb), (x1, yf, zc - ht), (x0, yf, zc - ht)], mat, (0, -1, -1))


def _louvers(mb, x0, x1, z0, z1, mat, yb=-0.015, ys=-0.05, pitch=0.085):
    """Saw-tooth shutter slats between z0 and z1: lit sloped face + dark underside per slat."""
    n = max(1, round((z1 - z0) / pitch))
    p = (z1 - z0) / n
    for i in range(n):
        zt = z1 - i * p
        zb = zt - p
        _poly(mb, [(x0, ys, zb), (x1, ys, zb), (x1, yb, zt), (x0, yb, zt)], mat, (0, -1, 0.4))
        if i < n - 1:   # the last underside would lie on the rail top
            _poly(mb, [(x0, ys, zb), (x1, ys, zb), (x1, yb, zb), (x0, yb, zb)], mat, (0, 0, -1))


def _shutter(mb, xa, xb, z0, z1, mat=DOOR, d=0.06, st=0.075, rl=0.09):
    """Louvred house shutter flat on the facade: 2 stiles, 3 rails, 2 slatted panels."""
    zm = (z0 + z1) / 2
    mb.box(xa, -d, z0, xa + st, 0.0, z1, mat, skip=("+y",))
    mb.box(xb - st, -d, z0, xb, 0.0, z1, mat, skip=("+y",))
    ia, ib = xa + st, xb - st
    for r0, r1 in ((z0, z0 + rl), (zm - rl / 2, zm + rl / 2), (z1 - rl, z1)):
        mb.box(ia, -d, r0, ib, 0.0, r1, mat, skip=("+y", "-x", "+x"))
    _louvers(mb, ia, ib, z0 + rl, zm - rl / 2, mat)
    _louvers(mb, ia, ib, zm + rl / 2, z1 - rl, mat)


def _soft(mb, sub, w=0.025):
    """Append *sub* with its sharp edges chamfered (chunky free-standing parts only)."""
    mb.extend(F.bevelled(sub, w))


def _sill_bar(mb, x0, x1, z0, z1, d, mat, bev=0.02, back=None):
    """Long sill bar x0..x1 with chamfered front edges and FLAT end caps (flush module seams).

    back: optional (xa, xb) range that also gets a +Y back face (part of the bar beyond the wall).
    """
    sub = MeshBuilder()
    sub.box(x0, -d, z0, x1, 0.0, z1, mat, skip=("+y", "-x", "+x"))
    sb = F.bevelled(sub, bev)
    mb.extend(sb)
    for xe, s in ((x0, -1.0), (x1, 1.0)):
        pts = []
        for v in sb.verts:
            if abs(v.x - xe) < 1e-5 and not any((v - p).length < 1e-6 for p in pts):
                pts.append(v.copy())
        cy = sum(p.y for p in pts) / len(pts)
        cz = sum(p.z for p in pts) / len(pts)
        pts.sort(key=lambda p: math.atan2(p.z - cz, p.y - cy))
        _poly(mb, pts, mat, (s, 0, 0))
    if back:
        xa, xb = back
        _poly(mb, [(xa, 0.0, z0), (xb, 0.0, z0), (xb, 0.0, z1), (xa, 0.0, z1)], mat, (0, 1, 0))


def _mirror_x(mb):
    """Mirrored copy (x -> -x) with face winding flipped so normals stay outward."""
    out = MeshBuilder()
    out.verts = [Vector((-v.x, v.y, v.z)) for v in mb.verts]
    out.faces = [tuple(reversed(f)) for f in mb.faces]
    out.fmat = list(mb.fmat)
    out.mats = list(mb.mats)
    return out


def _wall(h, holes=(), w=W):
    mb = MeshBuilder()
    F.wall_module(mb, w, h, holes=list(holes))
    return mb


def _r(v):
    return round(float(v), 4)


def _om(kind, opening=None, openings=None, head=None, sill=None, trim_x=0.0, ind_ok=None, **extra):
    """Opening / snap-datum meta (see the module docstring)."""
    m = {}
    if opening is not None:
        m["opening"] = tuple(_r(v) for v in opening)
        m["openings"] = tuple(_r(v) for o in (openings or [opening]) for v in o)
        m["opening_kind"] = kind
    if head is not None:
        m["head_top_z"] = _r(head)
    if sill is not None:
        m["sill_bottom_z"], m["sill_top_z"] = _r(sill[0]), _r(sill[1])
    m["trim_x"] = _r(trim_x)
    m["corner_ok"] = bool(trim_x <= CORNER_CLEAR + 1e-6)
    m["corner_ok_industrial"] = bool(trim_x <= IND_CLEAR + 1e-6) if ind_ok is None else bool(ind_ok)
    m.update(extra)
    return m


def _sill_z(hole):
    """(bottom, top) of the facade.sill() under *hole*."""
    return hole[1] - F.FRAME_W - F.SILL_H, hole[1] - F.FRAME_W


def _add(K, name, mb, h, kind, w=W, cat="Walls", **extra):
    K.add(name, mb, FAM, cat, meta=dict(height=h, module=w, kind=kind, **extra))


# =============================================================================== lead reference pieces
def _plain(K, name, h):
    mb = MeshBuilder()
    F.wall_module(mb, W, h)
    K.add(name, mb, FAM, "Walls", meta=dict(height=h, module=W, kind="plain", **_om("plain")))


def _window(K, name, h, hole, mullions=(1, 1)):
    mb = MeshBuilder()
    F.wall_module(mb, W, h, holes=[hole])
    F.window(mb, hole, mullions=mullions)
    meta = _om("window", hole, head=hole[3] + F.FRAME_W, sill=_sill_z(hole), trim_x=hole[2] + F.FRAME_W)
    K.add(name, mb, FAM, "Walls", meta=dict(height=h, module=W, kind="window", **meta))


def _door(K, name, h, hole, glass=None):
    mb = MeshBuilder()
    F.wall_module(mb, W, h, holes=[hole])
    F.door(mb, hole, glass_mat=glass)
    _threshold(mb, hole[0], hole[2], -F.FRAME_D, F.REVEAL + 0.03, TRIM)
    meta = _om("door", hole, head=hole[3] + F.FRAME_W, trim_x=hole[2] + F.FRAME_W, threshold_z=THRESH_T)
    K.add(name, mb, FAM, "Walls", meta=dict(height=h, module=W, kind="door", **meta))


def _corner(K, name, h):
    """Corner pilaster centred on the building corner (refined: chamfered vertical edges).

    Same outer bounds as the original box (x, y in [-0.22, 0.22]); top/bottom stay flat so
    pilasters stack seamlessly floor over floor.
    """
    mb = MeshBuilder()
    s, c = 0.22, 0.045
    oct8 = [(-s + c, -s), (s - c, -s), (s, -s + c), (s, s - c), (s - c, s), (-s + c, s), (-s, s - c), (-s, -s + c)]
    mb.prism(oct8, 0.0, h, TRIM, TRIM)
    K.add(name, mb, FAM, "Corners", meta=dict(height=h, kind="corner", reach=s))


# =============================================================================== new pieces
def _half(K, name, h):
    mb = _wall(h, w=W / 2)
    _add(K, name, mb, h, "plain", w=W / 2, **_om("plain"))


def _window_pair(K):
    holes = [(-1.15, 0.95, -0.35, 2.45), (0.35, 0.95, 1.15, 2.45)]
    mb = _wall(H3, holes)
    for hole in holes:
        F.window(mb, hole, mullions=(1, 1))
    bb = (holes[0][0], holes[0][1], holes[1][2], holes[1][3])
    _add(K, "KIT_Wall_WindowPair_H3", mb, H3, "window",
         **_om("window", bb, holes, head=2.45 + F.FRAME_W, sill=_sill_z(holes[0]), trim_x=1.15 + F.FRAME_W))


def _window_wide(K):
    hole = (-1.1, 1.05, 1.1, 2.45)          # head aligned with the standard window head (2.45)
    mb = _wall(H3, [hole])
    _win(mb, hole, xs=(-1.1 + 2.2 / 3, -1.1 + 4.4 / 3))
    _add(K, "KIT_Wall_WindowWide_H3", mb, H3, "window",
         **_om("window", hole, head=hole[3] + F.FRAME_W, sill=_sill_z(hole), trim_x=hole[2] + F.FRAME_W))


def _window_shutter(K):
    hole = (-0.55, 0.95, 0.55, 2.45)        # identical opening to KIT_Wall_Window_H3
    mb = _wall(H3, [hole])
    F.window(mb, hole, mullions=(1, 1))
    z0, z1 = hole[1] - 0.07, hole[3] + 0.07
    _shutter(mb, -1.23, -0.68, z0, z1)
    _shutter(mb, 0.68, 1.23, z0, z1)
    _add(K, "KIT_Wall_WindowShutter_H3", mb, H3, "window",
         **_om("window", hole, head=hole[3] + F.FRAME_W, sill=_sill_z(hole), trim_x=1.23,
               shutter_x=(0.68, 1.23)))


def _balcony_door(K):
    """Glazed French door 1.3 x 2.4 to floor level (pairs with KIT_Balcony_3m)."""
    hole = (-0.65, 0.0, 0.65, 2.4)
    yd = 0.15
    mb = _wall(H3, [hole])
    F.reveal(mb, hole, yd, WALL, bottom=False)
    _frame_at(mb, hole, 0.0, TRIM, bottom=False)
    # threshold
    mb.box(-0.65, -0.05, 0.0, 0.65, yd, 0.04, TRIM, skip=("-z", "+y", "-x", "+x"))
    zk, zt = 0.46, 2.29          # top of kick rail, bottom of top rail
    _front(mb, -0.55, 0.55, zk, zt, yd, GLASS)
    ys = yd - 0.06
    mb.box(-0.65, ys, 0.04, -0.55, yd, 2.4, TRIM, skip=("+y", "-x", "-z", "+z"))     # outer stiles
    mb.box(0.55, ys, 0.04, 0.65, yd, 2.4, TRIM, skip=("+y", "+x", "-z", "+z"))
    mb.box(-0.55, ys, zt, 0.55, yd, 2.4, TRIM, skip=("+y", "-x", "+x", "+z"))         # top rail
    mb.box(-0.55, ys, 0.04, 0.55, yd, zk, TRIM, skip=("+y", "-x", "+x", "-z"))        # kick rail
    mb.box(-0.065, yd - 0.08, 0.04, 0.065, yd, 2.4, TRIM, skip=("+y", "-z", "+z"))    # meeting stiles
    for z in (zk + (zt - zk) / 3, zk + 2 * (zt - zk) / 3):                            # muntins
        for xa, xb in ((-0.55, -0.065), (0.065, 0.55)):
            mb.box(xa, yd - 0.04, z - 0.022, xb, yd, z + 0.022, TRIM, skip=("+y", "-x", "+x"))
    for xa, xb in ((-0.47, -0.14), (0.14, 0.47)):                                     # kick panels
        _raised(mb, xa, xb, 0.12, zk - 0.08, ys, 0.025, 0.025, TRIM)
    for s in (-1, 1):                                                                 # lever handles
        x = s * 0.115
        mb.box(x - 0.02, yd - 0.12, 1.02, x + 0.02, yd - 0.08, 1.1, METAL, skip=("+y",))
    _add(K, "KIT_Wall_BalconyDoor_H3", mb, H3, "door",
         **_om("door", hole, head=hole[3] + F.FRAME_W, trim_x=hole[2] + F.FRAME_W, threshold_z=0.04))


def _door_glass(K):
    """Apartment lobby door: glazed upper half, raised panel below, small 3-light transom."""
    O = (-0.55, 0.0, 0.55, 2.65)
    zd = 2.2                                # door head / transom bar bottom
    yd = 0.15
    mb = _wall(H3, [O])
    F.reveal(mb, O, yd, WALL, bottom=False)
    _frame_at(mb, O, 0.0, TRIM, bottom=False)
    mb.box(-0.55, -F.FRAME_D, zd, 0.55, yd, zd + 0.1, TRIM, skip=("+y", "-x", "+x"))  # transom bar
    _glaze(mb, (-0.55, zd + 0.1, 0.55, 2.65), yd - 0.03, GLASS, xs=(-0.185, 0.185), bw=0.05)
    gd = (-0.36, 1.02, 0.36, 2.02)
    F.panel(mb, -0.55, 0.55, 0.0, zd, [gd], DOOR, y=yd)
    _front(mb, gd[0] - 0.03, gd[2] + 0.03, gd[1] - 0.03, gd[3] + 0.03, yd + 0.025, GLASS)
    _frame_at(mb, gd, yd + 0.025, DOOR, w=0.04, d=0.045)    # glazing bead, runs back to the glass
    _raised(mb, -0.36, 0.36, 0.2, 0.84, yd, 0.03, 0.03, DOOR)
    mb.box(0.36, yd - 0.07, 1.0, 0.42, yd, 1.08, METAL, skip=("+y",))                # knob
    _threshold(mb, -0.55, 0.55, -F.FRAME_D, yd, TRIM)
    _add(K, "KIT_Wall_DoorGlass_H3", mb, H3, "door",
         **_om("door", O, head=O[3] + F.FRAME_W, trim_x=O[2] + F.FRAME_W, threshold_z=THRESH_T,
               leaf_top_z=zd))


GARAGE_FW = 0.1          # garage frame width


def _garage_mb(drop=0.0):
    """Sectional garage door 2.6 wide, head at z 2.3; raised panels, glazed top section.

    drop > 0: the wall body and the door run down to z = -drop (house raised above the driveway);
    the door then gets one more section so the sections keep their proportions.
    """
    Hd = 2.3 + drop                      # door height (local frame: door bottom at z = 0)
    G = (-1.3, 0.0, 1.3, Hd)
    yd = 0.15
    mb = _wall(H3 + drop, [G])
    F.reveal(mb, G, yd, WALL, bottom=False)
    _frame_at(mb, G, 0.0, TRIM, w=GARAGE_FW, bottom=False)
    _front(mb, -1.3, 1.3, 0.0, Hd, yd, TRIM)          # backing plane, seen in the grooves
    ns, g, yf = (4 if drop < 0.2 else 5), 0.04, yd - 0.04
    hs = Hd / ns
    sw = 0.12
    pw = (2.6 - 5 * sw) / 4
    cols = [(-1.3 + sw + i * (pw + sw), -1.3 + sw + i * (pw + sw) + pw) for i in range(4)]
    for k in range(ns):
        a = k * hs + (g / 2 if k > 0 else 0.0)
        b = (k + 1) * hs - (g / 2 if k < ns - 1 else 0.0)
        if k < ns - 1:
            skip = ("+y", "-x", "+x") + (("-z",) if k == 0 else ())
            mb.box(-1.3, yf, a, 1.3, yd, b, TRIM, skip=skip)
            for xa, xb in cols:
                _raised(mb, xa, xb, a + 0.09, b - 0.09, yf, 0.03, 0.035, TRIM)
        else:
            wins = [(xa, a + 0.1, xb, b - 0.1) for xa, xb in cols]
            F.panel(mb, -1.3, 1.3, a, b, wins, TRIM, y=yf)
            _poly(mb, [(-1.3, yf, a), (1.3, yf, a), (1.3, yd, a), (-1.3, yd, a)], TRIM, (0, 0, -1))
            _front(mb, -1.3, 1.3, a, b, yf + 0.025, GLASS)      # glass behind the 4 lights
    mb.box(-0.14, yf - 0.035, 0.32, 0.14, yf, 0.38, METAL, skip=("+y",))     # lift handle
    _threshold(mb, -1.3, 1.3, -F.FRAME_D, yf, CONC)
    if drop:
        mb.transform(Matrix.Translation((0.0, 0.0, -drop)))
    return mb, (-1.3, -drop if drop else 0.0, 1.3, 2.3)


def _garage(K):
    mb, G = _garage_mb()
    _add(K, "KIT_Wall_Garage_H3", mb, H3, "garage",
         **_om("garage", G, head=G[3] + GARAGE_FW, trim_x=G[2] + GARAGE_FW, threshold_z=THRESH_T))


def _garage_grade(K, drop=0.35):
    """EXTRA: garage for a house raised *drop* above the lot (door reaches the driveway)."""
    mb, G = _garage_mb(drop)
    _add(K, "KIT_Wall_GarageGrade_H3", mb, H3, "garage",
         **_om("garage", G, head=G[3] + GARAGE_FW, trim_x=G[2] + GARAGE_FW, threshold_z=_r(-drop + THRESH_T),
               grade_drop=drop))


def _window_h4(K):
    hole = (-0.6, 1.2, 0.6, 3.2)
    mb = _wall(H4, [hole])
    _win(mb, hole, xs=(0.0,), zs=(2.6,))
    _add(K, "KIT_Wall_Window_H4", mb, H4, "window",
         **_om("window", hole, head=hole[3] + F.FRAME_W, sill=_sill_z(hole), trim_x=hole[2] + F.FRAME_W))


SD_O = (-0.5, 0.0, 0.5, 2.95)     # service door opening: door 0..2.3, transom bar, transom light
SD_ZD = 2.3


def _service_door_mb(fr=TRIM, fd=F.FRAME_D, h=H4, transom=True):
    """Service door 1.0 x 2.3 with a narrow vision light, kick plate, lever (+ transom above)."""
    O = SD_O if transom else (-0.5, 0.0, 0.5, SD_ZD)
    zd = SD_ZD
    yd = 0.15
    mb = _wall(h, [O])
    F.reveal(mb, O, yd, WALL, bottom=False)
    _frame_at(mb, O, 0.0, fr, d=fd, bottom=False)
    if transom:
        mb.box(-0.5, -fd, zd, 0.5, yd, zd + 0.1, fr, skip=("+y", "-x", "+x"))        # transom bar
        _glaze(mb, (-0.5, zd + 0.1, 0.5, O[3]), yd - 0.03, GLASS, xs=(0.0,), bar=fr, bw=0.05)
    vl = (-0.11, 1.3, 0.11, 2.0)
    F.panel(mb, -0.5, 0.5, 0.0, zd, [vl], DOOR, y=yd)
    _front(mb, vl[0] - 0.03, vl[2] + 0.03, vl[1] - 0.03, vl[3] + 0.03, yd + 0.02, GLASS)
    _frame_at(mb, vl, yd + 0.02, DOOR, w=0.04, d=0.04)      # bead runs back to the glass (no crack)
    mb.box(-0.44, yd - 0.015, 0.05, 0.44, yd, 0.3, METAL, skip=("+y",))              # kick plate
    mb.box(0.3, yd - 0.025, 0.97, 0.37, yd, 1.13, METAL, skip=("+y",))               # lever rose
    mb.box(0.15, yd - 0.075, 1.03, 0.37, yd - 0.025, 1.075, METAL, skip=("+y",))     # lever
    _threshold(mb, -0.5, 0.5, -fd, yd, CONC)
    return mb, O


def _door_meta(O, **kw):
    return _om("door", O, head=O[3] + F.FRAME_W, trim_x=O[2] + F.FRAME_W, threshold_z=THRESH_T,
               leaf_top_z=SD_ZD, **kw)


def _door_h4(K):
    mb, O = _service_door_mb()
    _add(K, "KIT_Wall_Door_H4", mb, H4, "door", **_door_meta(O))


# ---- storefront system (H4): glass 0.45 .. 3.05, transom bar 2.60 .. 2.68, posts 0.1 wide
SF_X0, SF_X1 = -1.3, 1.3
SF_ZK, SF_ZH = 0.45, 3.05
SF_ZT0, SF_ZT1 = 2.6, 2.68
SF_PW, SF_PD = 0.1, 0.06
SF_YG = 0.1
SF_HEAD = SF_ZH + 0.13            # top of the head beam
SF_PIER = 0.5                     # solid pier next to a building corner (StorefrontCorner)


def _sf_posts_head(mb, posts, hx0=SF_X0 - SF_PW, hx1=SF_X1 + SF_PW):
    for xa, xb in posts:
        mb.box(xa, -SF_PD, 0.0, xb, 0.0, SF_ZH, TRIM, skip=("+y", "-z", "+z"))
    head = MeshBuilder()
    head.box(hx0, -SF_PD - 0.01, SF_ZH, hx1, 0.0, SF_HEAD, TRIM, skip=("+y",))
    _soft(mb, head, 0.02)


def _sf_bulkhead(mb, xa, xb):
    """Display ledge + kick plate with raised panels below one display window x [xa, xb]."""
    ledge = MeshBuilder()
    ledge.box(xa - SF_PW, -0.12, SF_ZK - 0.1, xb + SF_PW, 0.0, SF_ZK, TRIM, skip=("+y",))
    _soft(mb, ledge, 0.025)
    zk = SF_ZK - 0.1
    _front(mb, xa, xb, 0.0, zk, -0.025, TRIM)
    span = xb - xa
    if span > 2.0:
        parts = [(xa + 0.1, (xa + xb) / 2 - 0.08), ((xa + xb) / 2 + 0.08, xb - 0.1)]
    else:
        parts = [(xa + 0.1, xb - 0.1)]
    for pa, pb in parts:
        _raised(mb, pa, pb, 0.08, zk - 0.07, -0.025, 0.025, 0.025, TRIM)


def _sf_meta(G, openings=None, kind="glass", trim_x=SF_X1 + SF_PW, glass=None, **kw):
    return _om(kind, G, openings, head=SF_HEAD, trim_x=trim_x, kick_z=_r(SF_ZK - 0.1), ledge_z=SF_ZK,
               glass=tuple(_r(v) for v in (glass or G)), **kw)


def _storefront_mb(xa=SF_X0, xb=SF_X1):
    """Display window: glass x [xa, xb] from the ledge to the head, centred mullion + transom."""
    G = (xa, SF_ZK, xb, SF_ZH)
    mb = _wall(H4, [G])
    F.reveal(mb, G, SF_YG, WALL)
    _glaze(mb, G, SF_YG, SHOP_GLASS, xs=((xa + xb) / 2,), zs=((SF_ZT0 + SF_ZT1) / 2,), bw=0.08, bd=0.06)
    _sf_posts_head(mb, [(xa - SF_PW, xa), (xb, xb + SF_PW)], xa - SF_PW, xb + SF_PW)
    _sf_bulkhead(mb, xa, xb)
    return mb, G


def _storefront(K):
    mb, G = _storefront_mb()
    _add(K, "KIT_Wall_Storefront_H4", mb, H4, "storefront", **_sf_meta(G))


def _storefront_corner(K):
    """EXTRA: display window for the module at a building corner (solid pier toward +X / -X)."""
    xb = W / 2 - SF_PIER                              # glass ends at x = 1.0, post 1.0 .. 1.1
    mb, G = _storefront_mb(SF_X0, xb)
    # trim_x / corner_ok refer to the corner end (corner_side); the far end keeps the regular post
    # (far_trim_x) and butts against the neighbouring storefront module.
    kw = dict(trim_x=xb + SF_PW, pier=SF_PIER, far_trim_x=_r(abs(SF_X0) + SF_PW))
    _add(K, "KIT_Wall_StorefrontCorner_H4", mb, H4, "storefront", **_sf_meta(G, corner_side="+x", **kw))
    Gl = (-G[2], G[1], -G[0], G[3])
    _add(K, "KIT_Wall_StorefrontCornerL_H4", _mirror_x(mb), H4, "storefront",
         **_sf_meta(Gl, corner_side="-x", **kw))


def _storefront_door_mb():
    """Door on the +X side (x 0.2 .. 1.3), display glass on the -X side."""
    xd0, xd1 = 0.2, SF_X1
    S = (SF_X0, SF_ZK, 0.1, SF_ZH)
    D = (xd0, 0.0, xd1, SF_ZH)
    yd = 0.12
    mb = _wall(H4, [S, D])
    F.reveal(mb, S, SF_YG, WALL)
    F.reveal(mb, D, 0.14, WALL, bottom=False)
    # side display glass + transom
    _glaze(mb, S, SF_YG, SHOP_GLASS, zs=((SF_ZT0 + SF_ZT1) / 2,), bw=0.08, bd=0.06)
    # door transom bar + transom glass
    mb.box(xd0, SF_YG - 0.06, SF_ZT0, xd1, 0.14, SF_ZT1, TRIM, skip=("+y", "-x", "+x"))
    _front(mb, xd0, xd1, SF_ZT1, SF_ZH, SF_YG, SHOP_GLASS)
    # glazed door leaf
    gd = (xd0 + 0.13, 0.32, xd1 - 0.13, SF_ZT0 - 0.13)
    F.panel(mb, xd0, xd1, 0.0, SF_ZT0, [gd], DOOR, y=yd)
    _front(mb, gd[0] - 0.03, gd[2] + 0.03, gd[1] - 0.03, gd[3] + 0.03, yd + 0.015, SHOP_GLASS)
    F.reveal(mb, gd, 0.015, DOOR, y=yd)                     # leaf edge around the glass (no crack)
    mb.box(xd0 + 0.06, yd - 0.012, 0.05, xd1 - 0.06, yd, 0.27, METAL, skip=("+y",))   # kick plate
    hx = xd0 + 0.065                                                                 # pull handle
    mb.box(hx - 0.02, yd - 0.09, 0.85, hx + 0.02, yd - 0.06, 1.6, METAL, skip=())
    for z in (0.92, 1.53):
        mb.box(hx - 0.02, yd - 0.06, z - 0.02, hx + 0.02, yd, z + 0.02, METAL, skip=("+y", "-y"))
    _sf_posts_head(mb, [(SF_X0 - SF_PW, SF_X0), (0.1, xd0), (SF_X1, SF_X1 + SF_PW)])
    _sf_bulkhead(mb, SF_X0, 0.1)
    _threshold(mb, xd0, xd1, -SF_PD, yd, CONC)
    return mb, S, D


def _storefront_door(K):
    mb, S, D = _storefront_door_mb()
    meta = _sf_meta(D, [D, S], kind="door", glass=S, threshold_z=THRESH_T, leaf_top_z=SF_ZT0)
    _add(K, "KIT_Wall_StorefrontDoor_H4", mb, H4, "storefront", door_side="right", **meta)
    Dl, Sl = (-D[2], D[1], -D[0], D[3]), (-S[2], S[1], -S[0], S[3])
    meta = _sf_meta(Dl, [Dl, Sl], kind="door", glass=Sl, threshold_z=THRESH_T, leaf_top_z=SF_ZT0)
    _add(K, "KIT_Wall_StorefrontDoorL_H4", _mirror_x(mb), H4, "storefront", door_side="left", **meta)


RD_HOUSING_X = 1.40                  # coil housing half width (clears the industrial corner flashing)
RD_HOUSING_Z = (3.38, 3.95)


def _roller_door(K):
    """Warehouse roller door 2.7 x 3.4 (ribbed M_RollerDoor curtain) + coil housing above."""
    R = (-1.35, 0.0, 1.35, 3.4)
    yc = 0.22            # curtain plane
    gx = 1.28            # inner face of the guide rails
    mb = _wall(H4, [R])
    F.reveal(mb, R, yc, WALL, bottom=False)
    # steel angle jambs on the facade (tops capped: they reach past the narrowed housing)
    for xa, xb in ((-1.44, -1.35), (1.35, 1.44)):
        mb.box(xa, -0.04, 0.0, xb, 0.0, 3.4, METAL_DK, skip=("+y", "-z"))
    # guide rails inside the reveal
    mb.box(-1.35, 0.13, 0.0, -gx, yc, 3.4, METAL_DK, skip=("+y", "-x", "-z", "+z"))
    mb.box(gx, 0.13, 0.0, 1.35, yc, 3.4, METAL_DK, skip=("+y", "+x", "-z", "+z"))
    # curtain
    _front(mb, -gx, gx, 0.0, 3.4, yc, ROLLER)
    zb = 0.13
    n = 20
    p = (3.4 - zb) / n
    for i in range(n):
        _hrib(mb, -gx, gx, zb + (i + 0.5) * p, yc, ROLLER)
    mb.box(-gx, yc - 0.06, 0.0, gx, yc, zb, METAL_DK, skip=("+y", "-x", "+x", "-z"))   # bottom bar
    mb.box(-0.16, yc - 0.1, 0.17, 0.16, yc - 0.03, 0.23, METAL_DK, skip=("+y",))      # grab handle
    _threshold(mb, -1.35, 1.35, -0.04, yc - 0.06, CONC)
    # coil housing (x +-1.40: stays 0.05 past the opening, keeps the corner flashing continuous)
    hb = MeshBuilder()
    hb.box(-RD_HOUSING_X, -0.36, RD_HOUSING_Z[0], RD_HOUSING_X, 0.0, RD_HOUSING_Z[1], METAL_DK, skip=("+y",))
    _soft(mb, hb, 0.04)
    _add(K, "KIT_Wall_RollerDoor_H4", mb, H4, "door",
         **_om("roller", R, head=RD_HOUSING_Z[1], trim_x=1.44, ind_ok=True, threshold_z=THRESH_T,
               housing_z=RD_HOUSING_Z, housing_x=RD_HOUSING_X))


RIB_X = [-1.25 + 0.5 * k for k in range(6)]     # major ribs every 0.5 m, 0.25 from the module edges
MINOR_X = [-1.0 + 0.5 * k for k in range(5)]    # minor ribs half way between (+ halves on the edges)
MINOR = dict(wb=0.07, wt=0.04, d=0.022)


def _cladding(mb, z0, z1, top=True, bottom=False, only=None, avoid=None):
    """Box-profile cladding on the facade between z0 and z1: major + minor ribs; seamless tiling.

    only / avoid: optional (xa, xb) ranges - keep only the ribs overlapping *only*, drop the ribs
    overlapping *avoid* (used to run the cladding around a door opening).
    """
    def keep(xa, xb):
        if only and (xb <= only[0] or xa >= only[1]):
            return False
        if avoid and not (xb <= avoid[0] or xa >= avoid[1]):
            return False
        return True
    for x in RIB_X:
        if keep(x - 0.1, x + 0.1):
            _vrib(mb, x, z0, z1, WALL, top=top, bottom=bottom)
    for x in MINOR_X:
        if keep(x - MINOR["wb"] / 2, x + MINOR["wb"] / 2):
            _vrib(mb, x, z0, z1, WALL, top=top, bottom=bottom, **MINOR)
    # half minor ribs on both module edges (the neighbour module completes them)
    wb, wt, d = MINOR["wb"], MINOR["wt"], MINOR["d"]
    for s in (-1, 1):
        e = 1.5 * s
        if not keep(min(e, e - s * wb / 2), max(e, e - s * wb / 2)):
            continue
        prof = [(e - s * wb / 2, 0.0), (e - s * wt / 2, -d), (e, -d), (e, 0.0)]
        if s < 0:
            prof = prof[::-1]
        mb.wall(prof[:3] if s > 0 else prof[1:], z0, z1, WALL)
        # end cap on the module edge (hidden against the neighbour, closes the rib when alone)
        _poly(mb, [(e, -d, z0), (e, 0.0, z0), (e, 0.0, z1), (e, -d, z1)], WALL, (s, 0, 0))
        if top:
            _poly(mb, [(p[0], p[1], z1) for p in prof], WALL, (0, 0, 1))
        if bottom:
            _poly(mb, [(p[0], p[1], z0) for p in prof], WALL, (0, 0, -1))


def _industrial(K, name, h):
    mb = _wall(h)
    _cladding(mb, 0.0, h)
    _add(K, name, mb, h, "industrial", **_om("industrial"))


IW_FW = 0.09                 # ribbon window frame width
IW_SILL_D = 0.14             # continuous sill depth
IW_RETURN = 0.14             # sill return past +X on the corner-end variant


def _industrial_window_mb(h, z0, end=False):
    """Ribbon window 2.8 x 1.1 at z0, 3 mullions, dark frames, continuous sill, ribbed cladding.

    end: the sill runs IW_RETURN past +X (outer corner) so it meets the side ribbon's sill.
    """
    hole = (-1.4, z0, 1.4, z0 + 1.1)
    fw = IW_FW
    mb = _wall(h, [hole])
    F.reveal(mb, hole, 0.1, WALL)
    _glaze(mb, hole, 0.1, GLASS, xs=(-0.7, 0.0, 0.7), bar=DARK, bw=0.06, bd=0.04)
    _frame_at(mb, hole, 0.0, DARK, w=fw, d=0.075, on_sill=True)
    zs0, zs1 = hole[1] - fw - 0.08, hole[1] - fw            # continuous metal sill under the frame
    x1 = W / 2 + (IW_RETURN if end else 0.0)
    _sill_bar(mb, -W / 2, x1, zs0, zs1, IW_SILL_D, DARK, back=(W / 2, x1) if end else None)
    _cladding(mb, 0.0, zs0, top=False)
    _cladding(mb, hole[3] + fw, h, top=True)
    return mb, hole, (zs0, zs1)


def _industrial_window(K):
    for h, z0, tag in ((H3, 1.2, "H3"), (H4, 2.4, "H4")):
        for end in (False, True):
            mb, hole, sill = _industrial_window_mb(h, z0, end)
            name = f"KIT_Wall_IndustrialWindow{'End' if end else ''}_{tag}"
            extra = dict(corner_end="+x", corner_side="+x", sill_return=IW_RETURN) if end else {}
            _add(K, name, mb, h, "industrial",
                 **_om("window", hole, head=hole[3] + IW_FW, sill=sill, trim_x=hole[2] + IW_FW,
                       ind_ok=True, **extra))


def _industrial_door(K):
    """EXTRA: the service door (dark frame) set into ribbed industrial cladding (H4 + H3)."""
    for h, transom, tag in ((H4, True, "H4"), (H3, False, "H3")):
        mb, O = _service_door_mb(fr=DARK, fd=0.075, h=h, transom=transom)
        span = (O[0] - F.FRAME_W - 0.01, O[2] + F.FRAME_W + 0.01)
        _cladding(mb, 0.0, h, avoid=span)
        _cladding(mb, O[3] + F.FRAME_W, h, bottom=True, only=span)
        _add(K, f"KIT_Wall_IndustrialDoor_{tag}", mb, h, "industrial", **_door_meta(O))


def _corner_industrial(K, name, h):
    """Folded corner flashing (L angle) in dark metal, wraps the outer corner of ribbed cladding.

    Legs 0.13 m along each facade (clears the first major cladding rib at 0.25 m), 0.085 m proud so
    it covers the 0.07 m ribs; chamfered vertical edges, flat top/bottom for stacking.
    """
    a, d, c = 0.13, IND_FLASH_D, 0.022
    L = [(-a, 0.0), (-a, -d + c), (-a + c, -d), (d - c, -d), (d, -d + c), (d, a - c), (d - c, a), (0.0, a), (0.0, 0.0)]
    mb = MeshBuilder()
    mb.prism(L, 0.0, h, METAL_DK, METAL_DK)
    K.add(name, mb, FAM, "Corners", meta=dict(height=h, kind="corner_industrial", reach=a, proud=d))


# =============================================================================== build
def build(K):
    # plain & fillers
    _plain(K, "KIT_Wall_Plain_H3", H3)
    _plain(K, "KIT_Wall_Plain_H4", H4)
    _half(K, "KIT_Wall_Half_H3", H3)
    _half(K, "KIT_Wall_Half_H4", H4)
    # H3 windows
    _window(K, "KIT_Wall_Window_H3", H3, (-0.55, 0.95, 0.55, 2.45))
    _window_pair(K)
    _window_wide(K)
    _window_shutter(K)
    # H3 doors
    _balcony_door(K)
    _door(K, "KIT_Wall_Door_H3", H3, (-0.5, 0.0, 0.5, 2.25))
    _door_glass(K)
    _garage(K)
    _garage_grade(K)
    # H4 shop / service floor
    _window_h4(K)
    _door_h4(K)
    _storefront(K)
    _storefront_corner(K)
    _storefront_door(K)
    _roller_door(K)
    # industrial
    _industrial(K, "KIT_Wall_Industrial_H3", H3)
    _industrial(K, "KIT_Wall_Industrial_H4", H4)
    _industrial_window(K)
    _industrial_door(K)
    # corners
    _corner(K, "KIT_Corner_H3", H3)
    _corner(K, "KIT_Corner_H4", H4)
    _corner_industrial(K, "KIT_Corner_Industrial_H3", H3)
    _corner_industrial(K, "KIT_Corner_Industrial_H4", H4)
