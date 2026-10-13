"""Landmark: MARINA - boat slips on the north quay below the Dock Yard (site has allow_water).

PLAN (site frame: local +X runs DOWNSTREAM along the canal, local -Y faces the water; origin = site
center (318, -138); S.rot is fitted to the canal edge inside the polygon, ~ -38 deg)
--------------------------------------------------------------------------------------------------
The site polygon reaches the water only along a ~26 m stretch of quay (x ~ -18 .. 8) and only covers
a thin sliver of the canal (max ~4.9 m from the wall at the west vertex). Everything on the water
stays inside that sliver:
* QUAY DECK: timber boardwalk (4 m) along the water frontage, covering the stone coping, with timber
  fender posts down the quay wall, cast-iron mooring bollards and life-ring stands. Both ends are cut
  square where the full deck section still fits the polygon (no thin wedges along the oblique edges).
* FLOATING PONTOONS (custom) in the sliver along the wall (x -15 .. -1): two 1.8 m wide sections joined
  by a hinge plate, deck 0.4 m above the water on white floats, reached by a gangway ramp from a small
  landing at quay level at the east end.
  Moored at it: a small motor launch and a canoe; two timber mooring piles (pelican perches).
* JIB CRANE (custom) at the west end of the quay lifting a dinghy off the pontoon, dressed with red /
  white / blue pennant bunting under the jib and beside the tie rod.
* HARBOR OFFICE: a kit shed (S.building, gable to the water) behind the deck, with a sign board,
  life rings and a pennant pole; crates / barrels / pallets around it.
* BOATYARD (concrete hardstanding) east of the office: a sailboat on a cradle and a red day-sailer
  sloop on a road trailer - two masts of different heights = the marina's silhouette from the bridges
  and the south bank.
  => 5 boats: launch + canoe (water), dinghy (crane), sailboat (cradle), sloop (trailer).
* A chain-link fence closes the inland (warehouse) sides of the yard with a gate toward the passage
  between the Canal Works sheds; the quay ends stay open. Storage container, barrels, two trees.
GAMEPLAY: sea lions lounge on the pontoon and deck, pelicans on the piles / crane; the boatyard is an
open chase space between hulls (hiding under the cradle / trailer); the deck is the quay promenade.

Exported builders reused by courts.py (BoathouseSlip): kayak_mb, lifering_stand_mb, bollard_mb,
hull_mb.
"""
import math

from mathutils import Matrix, Vector

from .. import config as C
from .. import geom2d as G
from ..assembler import BuildingSpec, H3
from ..meshutil import MeshBuilder
from .town_square import (AWN, CREAM, Counter, bbox, beam, clip_convex, face_n, gem, kit, lathe, place,
                          put_mb, rbox, rope, sag_point, shared_mesh, tube, v3, flagpole_mb)

TAU = 2.0 * math.pi
WATER_Z = C.CANAL_WATER_Z
COPING_Z = C.CANAL_COPING_Z
DECK_Z = 0.24


# =============================================================================== boats
def hull_mb(L, B, H, hull_mat, in_mat="M_Wood_Light", rim_mat="M_Trim_White", open_top=True, n=10,
            rocker=0.12, sheer_rise=0.14, transom=True, keel=0.0, thick=0.07, floor_h=0.16, seats=2,
            bow_pow=1.6, stripe=None):
    """Stylized boat hull along X (bow at +X, origin at the keel bottom amidships, z up).
    open_top: inner skin + gunwale rim + floor + thwarts; else a flat deck at the sheer (in_mat)."""
    mb = MeshBuilder()
    secs = []          # list of (x, [(y, z) port side from sheer to keel])
    for i in range(n + 1):
        t = -1.0 + 2.0 * i / n
        x = t * L / 2
        if t >= 0:
            bw = (B / 2) * max(0.0, 1.0 - t ** bow_pow) ** 0.75
        else:
            bw = (B / 2) * (1.0 - (0.5 if not transom else 0.3) * (-t) ** 2.4)
        if not transom and t < 0:
            bw = (B / 2) * max(0.0, 1.0 - (-t) ** bow_pow) ** 0.75
        kz = rocker * (max(0.0, t) ** 2) + (0.0 if transom else rocker * (max(0.0, -t) ** 2))
        sz = H + sheer_rise * (max(0.0, t) ** 2) + 0.04 * (max(0.0, -t) ** 2)
        prof = [(bw, sz), (bw * 0.99, kz + (sz - kz) * 0.62), (bw * 0.86, kz + (sz - kz) * 0.25),
                (bw * 0.5, kz + 0.035), (0.0, kz)]
        secs.append((x, prof, bw, sz, kz))
    # outer skin (port + starboard)
    for i in range(n):
        xa, pa, bwa, _, _ = secs[i]
        xb, pb, bwb, _, _ = secs[i + 1]
        for side in (1, -1):
            for k in range(len(pa) - 1):
                q = [v3(xa, side * pa[k][0], pa[k][1]), v3(xb, side * pb[k][0], pb[k][1]),
                     v3(xb, side * pb[k + 1][0], pb[k + 1][1]), v3(xa, side * pa[k + 1][0], pa[k + 1][1])]
                mid = sum(q, Vector()) / 4
                m = hull_mat
                if stripe and k == 0:
                    m = stripe
                face_n(mb, q, m, (0.0, side * 1.0, -0.35 if k >= 2 else 0.0) if abs(mid.y) > 1e-4 else (0, 0, -1))
    # transom
    x0, p0, bw0, sz0, kz0 = secs[0]
    if transom and bw0 > 0.05:
        pts = [v3(x0, y, z) for (y, z) in p0] + [v3(x0, -y, z) for (y, z) in reversed(p0[:-1])]
        face_n(mb, pts, hull_mat, (-1, 0, 0))
    if keel > 0:
        bbox(mb, -L * 0.18, -0.06, -keel, L * 0.12, 0.06, 0.05, hull_mat)
        bbox(mb, -L * 0.14, -0.14, -keel - 0.12, L * 0.06, 0.14, -keel + 0.08, "M_Metal_Dark")
    if open_top:
        # gunwale rim + inner skin + floor
        inner = []
        for (x, prof, bw, sz, kz) in secs:
            bi = max(0.0, bw - thick)
            fz = kz + floor_h
            inner.append((x, bi, sz, fz, bw))
        for i in range(n):
            xa, bia, sza, fza, bwa = inner[i]
            xb, bib, szb, fzb, bwb = inner[i + 1]
            for side in (1, -1):
                face_n(mb, [v3(xa, side * bwa, sza), v3(xb, side * bwb, szb), v3(xb, side * bib, szb),
                            v3(xa, side * bia, sza)], rim_mat, (0, 0, 1))
                face_n(mb, [v3(xa, side * bia, sza), v3(xb, side * bib, szb), v3(xb, side * bib * 0.85, fzb),
                            v3(xa, side * bia * 0.85, fza)], in_mat, (0, -side, 0.3))
            face_n(mb, [v3(xa, bia * 0.85, fza), v3(xb, bib * 0.85, fzb), v3(xb, -bib * 0.85, fzb),
                        v3(xa, -bia * 0.85, fza)], in_mat, (0, 0, 1))
        if transom and bw0 > 0.05:
            xa, bia, sza, fza, bwa = inner[0]
            face_n(mb, [v3(xa + 0.001, bia, sza), v3(xa + 0.001, -bia, sza), v3(xa + 0.001, -bia * 0.85, fza),
                        v3(xa + 0.001, bia * 0.85, fza)], in_mat, (1, 0, 0))
            face_n(mb, [v3(xa, bwa, sza), v3(xa, -bwa, sza), v3(xa, -bia, sza), v3(xa, bia, sza)], rim_mat, (0, 0, 1))
        for k in range(seats):
            xs = -L * 0.25 + (L * 0.45) * (k / max(1, seats - 1)) if seats > 1 else 0.0
            j = min(range(len(secs)), key=lambda i: abs(secs[i][0] - xs))
            bw = secs[j][2] - thick - 0.02
            zt = secs[j][3] - 0.16
            bbox(mb, xs - 0.13, -bw, zt - 0.05, xs + 0.13, bw, zt, rim_mat)
    else:
        for i in range(n):
            xa, pa, bwa, sza, _ = secs[i]
            xb, pb, bwb, szb, _ = secs[i + 1]
            face_n(mb, [v3(xa, bwa, sza), v3(xb, bwb, szb), v3(xb, -bwb, szb), v3(xa, -bwa, sza)], in_mat, (0, 0, 1))
    return mb, secs


def launch_mb():
    """Small motor launch (4.6 m): open hull, little console with windscreen, outboard motor."""
    mb, secs = hull_mb(4.6, 1.65, 0.78, "M_Wall_White", in_mat="M_Wood_Light", rim_mat="M_Trim_Wood",
                       stripe="M_Awning_Blue", seats=2)
    bbox(mb, 0.15, -0.35, 0.22, 0.75, 0.35, 0.95, "M_Wall_White", bevel=0.04)          # console
    face_n(mb, [v3(0.75, -0.36, 0.95), v3(0.75, 0.36, 0.95), v3(0.95, 0.3, 1.3), v3(0.95, -0.3, 1.3)],
           "M_Glass", (1, 0, 0.6))
    face_n(mb, [v3(0.75, -0.36, 0.95), v3(0.75, 0.36, 0.95), v3(0.95, 0.3, 1.3), v3(0.95, -0.3, 1.3)],
           "M_Glass", (-1, 0, -0.6))
    bbox(mb, 0.3, -0.12, 0.95, 0.45, 0.12, 1.02, "M_Trim_Dark")                         # wheel
    # outboard motor on the transom
    x0 = -2.3
    bbox(mb, x0 - 0.42, -0.2, 0.55, x0 - 0.02, 0.2, 1.0, "M_Trim_Dark", bevel=0.05)
    bbox(mb, x0 - 0.3, -0.07, -0.25, x0 - 0.16, 0.07, 0.56, "M_Metal_Dark")
    return mb


def canoe_mb():
    """Open canoe 3.6 m (pointed both ends), recolorable AWN hull."""
    mb, _ = hull_mb(3.6, 0.82, 0.4, AWN, in_mat="M_Wood_Light", rim_mat="M_Trim_Wood", transom=False, n=10,
                    rocker=0.08, sheer_rise=0.12, thick=0.05, floor_h=0.06, seats=2, bow_pow=1.4)
    # sheer rises at both ends: mirror rise toward the stern by a second pass is skipped (keeps it lean)
    beam(mb, (-0.4, 0.0, 0.42), (0.5, 0.0, 0.62), 0.07, 0.04, "M_Trim_Wood")             # paddle shaft
    rbox(mb, (0.75, 0.0, 0.66), (0.4, 0.17, 0.04), "M_Trim_Wood", rot=Matrix.Rotation(0.22, 3, "Y"))
    return mb


def dinghy_mb():
    """Little 2.4 m rowing dinghy (white / teal), hung from the crane."""
    mb, _ = hull_mb(2.4, 1.15, 0.5, "M_Wall_White", in_mat="M_Wood_Light", rim_mat="M_Trim_Wood", n=8,
                    rocker=0.1, sheer_rise=0.08, thick=0.06, floor_h=0.1, seats=2, stripe="M_Awning_Teal",
                    bow_pow=1.3)
    return mb


def sailboat_mb():
    """6.6 m sailboat on a timber cradle (origin = ground), mast ~8.6 m, boom with furled sail."""
    mb = MeshBuilder()
    hb, secs = hull_mb(6.6, 2.2, 1.3, "M_Wall_White", in_mat="M_Wood_Light", open_top=False, n=12,
                       rocker=0.25, sheer_rise=0.22, keel=0.85, stripe="M_Door_Navy", bow_pow=1.5)
    lift = 1.05
    mb.extend(hb, Matrix.Translation((0, 0, lift)))
    # cabin + windows
    zt = lift + 1.3
    bbox(mb, -1.6, -0.72, zt - 0.05, 0.9, 0.72, zt + 0.55, "M_Wall_White", bevel=0.06)
    bbox(mb, -1.55, -0.72, zt + 0.55, 0.85, 0.72, zt + 0.62, "M_Wood_Light")
    for y, s in ((-0.73, -1), (0.73, 1)):
        for x in (-1.1, -0.45, 0.2):
            bbox(mb, x - 0.2, y - 0.02 * (s < 0), zt + 0.2, x + 0.2, y + 0.02 * (s > 0), zt + 0.38, "M_Glass")
    # mast, boom, furled sail, forestay
    mb.cylinder(0.75, 0.0, zt + 0.55, zt + 8.6, 0.07, "M_Metal", seg=6, r_top=0.05)
    tube(mb, (0.75, 0.0, zt + 1.5), (-2.6, 0.0, zt + 1.5), 0.06, "M_Metal", seg=6)
    sail = MeshBuilder()
    lathe(sail, [(0.0, 0.0), (0.17, 0.2), (0.14, 3.0), (0.0, 3.25)], "M_Awning_Cream", seg=6)
    mb.extend(sail, Matrix.Translation((0.7, 0.0, zt + 1.62)) @ Matrix.Rotation(-math.pi / 2, 4, "Y"))
    beam(mb, (0.75, 0.0, zt + 8.4), (3.3, 0.0, lift + 1.5), 0.04, 0.04, "M_Metal_Dark")
    beam(mb, (0.75, 0.0, zt + 8.4), (-3.2, 0.0, lift + 1.4), 0.04, 0.04, "M_Metal_Dark")
    # cradle: timber blocks under the keel + 4 adjustable stands
    bbox(mb, -1.4, -0.35, 0.0, 0.9, 0.35, lift - 0.95, "M_Trim_Wood")
    for x in (-1.8, 1.4):
        for s in (-1, 1):
            j = min(range(len(secs)), key=lambda i: abs(secs[i][0] - x))
            bw = secs[j][1][2][0]
            zc = lift + secs[j][1][2][1]
            beam(mb, (x, s * (bw + 0.55), 0.0), (x, s * (bw - 0.02), zc), 0.12, 0.12, "M_Hazard")
            bbox(mb, x - 0.25, s * (bw + 0.55) - 0.25, 0.0, x + 0.25, s * (bw + 0.55) + 0.25, 0.08, "M_Metal_Dark")
    return mb


def sloop_trailer_mb():
    """4.8 m day-sailer sloop on a road trailer (origin = ground, bow +X): red hull with a white boot
    stripe, white deck, little cuddy cabin, wooden cockpit, mast ~6.4 m above the deck with a furled
    mainsail in a blue cover on the boom, furled jib on the forestay, backstay. The marina's second mast."""
    mb = MeshBuilder()
    lift = 0.55
    hb, secs = hull_mb(4.8, 1.8, 0.9, "M_Awning_Red", in_mat="M_Wall_White", open_top=False, n=10,
                       rocker=0.16, sheer_rise=0.18, stripe="M_Wall_White", bow_pow=1.5)
    mb.extend(hb, Matrix.Translation((0, 0, lift)))
    zd = lift + 0.9                                                                       # deck (amidships)
    bbox(mb, -0.1, -0.52, zd - 0.06, 1.25, 0.52, zd + 0.38, "M_Wall_White", bevel=0.05)    # cuddy cabin
    bbox(mb, -0.06, -0.47, zd + 0.38, 1.2, 0.47, zd + 0.43, "M_Wood_Light")
    for s in (-1, 1):
        bbox(mb, 0.2, s * 0.52 - 0.012 * (s < 0), zd + 0.15, 0.95, s * 0.52 + 0.012 * (s > 0), zd + 0.27, "M_Glass")
    bbox(mb, -1.95, -0.58, zd - 0.02, -0.15, 0.58, zd + 0.03, "M_Wood_Light")              # cockpit sole
    for s in (-1, 1):                                                                      # coamings
        bbox(mb, -1.95, s * 0.58 - 0.04, zd, -0.15, s * 0.58 + 0.04, zd + 0.16, "M_Trim_Wood")
    beam(mb, (-2.35, 0.0, zd + 0.15), (-1.45, 0.0, zd + 0.3), 0.06, 0.05, "M_Trim_Wood")    # tiller
    bbox(mb, -2.47, -0.04, lift + 0.2, -2.37, 0.04, zd + 0.15, "M_Trim_White")              # rudder blade
    # rig
    xm, ztop = 0.85, zd + 0.43 + 6.0
    mb.cylinder(xm, 0.0, zd + 0.43, ztop, 0.06, "M_Metal", seg=6, r_top=0.045)
    lathe(mb, [(0.0, ztop - 0.02), (0.09, ztop + 0.02), (0.0, ztop + 0.14)], "M_Awning_Yellow", seg=6, cx=xm)
    zb = zd + 1.2
    tube(mb, (xm, 0.0, zb), (-2.15, 0.0, zb), 0.045, "M_Metal", seg=6)                      # boom
    cover = MeshBuilder()
    lathe(cover, [(0.0, 0.0), (0.15, 0.15), (0.13, 2.6), (0.0, 2.85)], "M_Awning_Blue", seg=6)
    mb.extend(cover, Matrix.Translation((xm - 0.05, 0.0, zb + 0.12)) @ Matrix.Rotation(-math.pi / 2, 4, "Y"))
    bow = Vector((2.38, 0.0, zd + 0.2))
    beam(mb, (xm, 0.0, ztop - 0.15), bow, 0.035, 0.035, "M_Metal_Dark")                      # forestay
    beam(mb, (xm, 0.0, ztop - 0.15), (-2.42, 0.0, zd + 0.06), 0.035, 0.035, "M_Metal_Dark")  # backstay
    d = (Vector((xm, 0.0, ztop - 0.15)) - bow)
    jib = MeshBuilder()                                                                    # furled jib
    lathe(jib, [(0.0, 0.0), (0.1, 0.25), (0.08, d.length * 0.62), (0.0, d.length * 0.7)], "M_Awning_Cream", seg=5)
    mb.extend(jib, Matrix.Translation(bow) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4())
    # trailer: frame, axle + wheels, tongue, winch post
    for s in (-1, 1):
        bbox(mb, -2.0, s * 0.62 - 0.07, 0.42, 2.0, s * 0.62 + 0.07, 0.55, "M_Metal_Dark")
        lathe_w = MeshBuilder()
        lathe_w.cylinder(0.0, 0.0, -0.13, 0.13, 0.32, "M_Hazard_Dark", seg=10, cap_bottom=True)
        mb.extend(lathe_w, Matrix.Translation((-0.4, s * 0.95, 0.32)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
        bbox(mb, -0.75, s * 0.95 - 0.12, 0.62, -0.05, s * 0.95 + 0.12, 0.68, "M_Metal_Dark")     # mudguard
        bbox(mb, -1.7, s * 0.55 - 0.07, 0.55, 1.2, s * 0.55 + 0.07, 0.66, "M_Trim_Wood")        # bunk board
    bbox(mb, -0.45, -0.95, 0.28, -0.35, 0.95, 0.36, "M_Metal_Dark")                          # axle
    beam(mb, (2.0, -0.62, 0.48), (3.4, 0.0, 0.48), 0.12, 0.12, "M_Metal_Dark")
    beam(mb, (2.0, 0.62, 0.48), (3.4, 0.0, 0.48), 0.12, 0.12, "M_Metal_Dark")
    bbox(mb, 3.3, -0.08, 0.0, 3.45, 0.08, 0.48, "M_Metal_Dark")                              # jockey wheel post
    bbox(mb, 2.55, -0.06, 0.48, 2.67, 0.06, 1.25, "M_Metal_Dark")                             # winch post
    return mb


def kayak_mb():
    """Sit-in kayak 3.8 m, recolorable AWN hull, dark cockpit coaming (origin = keel bottom centre)."""
    mb = MeshBuilder()
    L, B, H = 3.8, 0.62, 0.32
    n = 12
    rows = []
    for i in range(n + 1):
        t = -1.0 + 2.0 * i / n
        x = t * L / 2
        bw = (B / 2) * max(0.0, 1.0 - abs(t) ** 1.7) ** 0.7
        kz = 0.06 * t * t
        dz = H * (0.55 + 0.45 * (1 - t * t)) + 0.05 * t * t
        mid = kz + H * 0.42
        rows.append((x, [(bw * 0.0, dz), (bw * 0.7, dz - 0.04), (bw, mid), (bw * 0.6, kz + 0.04), (0.0, kz)]))
    for i in range(n):
        xa, pa = rows[i]
        xb, pb = rows[i + 1]
        for side in (1, -1):
            for k in range(len(pa) - 1):
                q = [v3(xa, side * pa[k][0], pa[k][1]), v3(xb, side * pb[k][0], pb[k][1]),
                     v3(xb, side * pb[k + 1][0], pb[k + 1][1]), v3(xa, side * pa[k + 1][0], pa[k + 1][1])]
                mid = sum(q, Vector()) / 4
                face_n(mb, q, AWN, (0.0, mid.y, (mid.z - H * 0.45) * 2.0))
    # oval cockpit coaming (dark), sunk into the deck crown
    cp = MeshBuilder()
    lathe(cp, [(0.2, H - 0.08), (0.2, H + 0.03), (0.16, H + 0.03), (0.16, H - 0.02), (0.0, H - 0.02)],
          AWN, seg=10, mats=[AWN, AWN, "M_Trim_Dark", "M_Trim_Dark"])
    mb.extend(cp, Matrix.Translation((-0.25, 0.0, 0.0)) @ Matrix.Scale(2.0, 4, (1.0, 0.0, 0.0)))
    return mb


def lifering_stand_mb():
    """Life ring (orange / white quarters) on a white post with a little roof box."""
    mb = MeshBuilder()
    bbox(mb, -0.07, -0.07, 0.0, 0.07, 0.07, 1.55, "M_Trim_White", bevel=0.02)
    bbox(mb, -0.12, -0.12, 0.0, 0.12, 0.12, 0.12, "M_Wall_Concrete")
    bbox(mb, -0.12, -0.1, 1.55, 0.12, 0.1, 1.65, "M_Door_Red")
    R, r = 0.34, 0.085
    cz = 1.05
    nU, nV = 12, 6
    for i in range(nU):
        a0, a1 = TAU * i / nU, TAU * (i + 1) / nU
        m = "M_Hazard_Orange" if (i // 3) % 2 == 0 else "M_Trim_White"
        for j in range(nV):
            b0, b1 = TAU * j / nV, TAU * (j + 1) / nV

            def P(a, b):
                rr = R + r * math.cos(b)
                return v3(rr * math.cos(a), -0.12 + r * math.sin(b), cz + rr * math.sin(a))
            q = [P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)]
            ctr = v3(R * math.cos((a0 + a1) / 2), -0.12, cz + R * math.sin((a0 + a1) / 2))
            mid = sum(q, Vector()) / 4
            face_n(mb, q, m, mid - ctr)
    return mb


def bollard_mb():
    """Cast-iron mooring bollard (0.55 m)."""
    mb = MeshBuilder()
    lathe(mb, [(0.26, 0.0), (0.26, 0.08), (0.17, 0.12), (0.14, 0.38), (0.2, 0.46), (0.2, 0.52), (0.12, 0.56),
               (0.0, 0.57)], "M_Metal_Dark", seg=8)
    return mb


def pile_mb(top=1.25):
    """Timber mooring pile from the canal bed to *top* with a dark cap and a rope band."""
    mb = MeshBuilder()
    mb.cylinder(0, 0, C.CANAL_BED_Z, top, 0.17, "M_Trim_Wood", seg=8)
    lathe(mb, [(0.19, top - 0.02), (0.19, top + 0.06), (0.0, top + 0.16)], "M_Metal_Dark", seg=8)
    lathe(mb, [(0.2, top - 0.75), (0.2, top - 0.6), (0.17, top - 0.6)], "M_Wood_Light", seg=8)
    return mb


# =============================================================================== quay pieces
def pontoon_mb(x0, x1, y0, y1, z_top):
    """Floating pontoon box (deck planks, fascia, floats, cleats) between x0..x1, y0..y1."""
    mb = MeshBuilder()
    bbox(mb, x0, y0, z_top - 0.22, x1, y1, z_top, "M_Wood_Light")
    k = 0
    x = x0 + 0.6
    while x < x1 - 0.3:                                   # plank joints
        bbox(mb, x - 0.03, y0 + 0.02, z_top, x + 0.03, y1 - 0.02, z_top + 0.012, "M_Trim_Wood")
        x += 0.6
        k += 1
    for (ya, yb) in ((y0 - 0.05, y0 + 0.05), (y1 - 0.05, y1 + 0.05)):
        bbox(mb, x0 - 0.05, ya, z_top - 0.3, x1 + 0.05, yb, z_top + 0.03, "M_Trim_Wood")
    x = x0 + 0.8
    while x < x1 - 0.5:                                   # floats
        bbox(mb, x - 0.55, y0 + 0.15, z_top - 0.62, x + 0.55, y1 - 0.15, z_top - 0.22, "M_Wall_White")
        x += 2.2
    for x in (x0 + 1.5, (x0 + x1) / 2, x1 - 1.5):         # cleats on the outer edge
        bbox(mb, x - 0.2, y0 + 0.08, z_top, x + 0.2, y0 + 0.18, z_top + 0.1, "M_Metal_Dark")
    return mb


def gangway_mb(L, W, drop):
    """Gangway ramp from (0, 0, 0) down to (-L, 0, -drop) along -X; width W across Y (y 0 .. -W),
    handrail on the -Y (water) side, anti-slip cleats."""
    mb = MeshBuilder()
    sub = MeshBuilder()
    sub.box(-L, -W, -0.08, 0.0, 0.0, 0.0, "M_Wood_Light")
    shear = Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (drop / L, 0, 1, 0), (0, 0, 0, 1)))
    mb.extend(sub, shear)
    for i in range(1, 8):
        u = -L * i / 8
        z = drop * u / L
        bbox(mb, u - 0.03, -W + 0.05, z, u + 0.03, -0.05, z + 0.035, "M_Trim_Wood")
    for k in range(4):
        u = -L * k / 3
        z = drop * u / L
        bbox(mb, u - 0.04, -W + 0.0, z, u + 0.04, -W + 0.08, z + 0.95, "M_Metal")
    tube(mb, (0.0, -W + 0.04, 0.95), (-L, -W + 0.04, -drop + 0.95), 0.04, "M_Metal", seg=6)
    tube(mb, (0.0, -W + 0.04, 0.5), (-L, -W + 0.04, -drop + 0.5), 0.03, "M_Metal", seg=4)
    return mb


PENNANTS = ("M_Awning_Red", "M_Wall_White", "M_Awning_Blue")      # nautical red / white / blue


def pennant_line(mb, a, b, sag=0.3, step=0.42, w=0.3, h=0.42, mats=PENNANTS, line="M_Trim_Dark", side_off=0.0):
    """Bunting: sagging line from a to b (3D) with triangular pennants hanging from it, cycling *mats*.
    Each pennant is two single-sided triangles 1.6 cm apart (holds up with backface culling)."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    n = max(3, int(round(L / 2.0)))
    rope(mb, [sag_point(a, b, i / n, sag) for i in range(n + 1)], 0.018, line)
    d = Vector((b.x - a.x, b.y - a.y, 0.0)).normalized()
    nside = Vector((-d.y, d.x, 0.0))
    m = max(1, int(L / step))
    off = nside * 0.008
    for i in range(m):
        t = (i + 0.5) / m
        dt = 0.5 * w / L
        p0 = sag_point(a, b, t - dt, sag) - Vector((0.0, 0.0, 0.02))
        p1 = sag_point(a, b, t + dt, sag) - Vector((0.0, 0.0, 0.02))
        tip = (p0 + p1) / 2 - Vector((0.0, 0.0, h)) + d * 0.04
        mat = mats[i % len(mats)]
        face_n(mb, [p0 + off, p1 + off, tip + off], mat, nside)
        face_n(mb, [p0 - off, p1 - off, tip - off], mat, -nside)


def jib_crane_mb(reach, hook_z, bunting=True):
    """Slewing jib crane: yellow post 5.6 m, jib along +X to *reach*, cable + hook block at hook_z.
    bunting: pennant lines (red / white / blue) under the jib and beside the tie rod (dressed for the
    marina, reads from the bridges)."""
    mb = MeshBuilder()
    if bunting:
        pennant_line(mb, (0.35, 0.0, 5.8), (reach - 0.6, 0.0, 5.8), sag=0.42, step=0.42)
        pennant_line(mb, (0.1, 0.3, 7.12), (reach - 0.05, 0.3, 6.32), sag=0.12, step=0.46, w=0.28, h=0.36)
        beam(mb, (0.0, 0.0, 7.12), (0.1, 0.3, 7.12), 0.04, 0.04, "M_Metal_Dark")              # line hangers
        beam(mb, (reach - 0.05, 0.0, 6.3), (reach - 0.05, 0.3, 6.32), 0.04, 0.04, "M_Metal_Dark")
    bbox(mb, -0.8, -0.8, -0.1, 0.8, 0.8, 0.22, "M_Wall_Concrete", bevel=0.04)
    mb.cylinder(0, 0, 0.22, 5.6, 0.26, "M_Hazard", seg=10, r_top=0.22)
    for k in range(3):                                         # hazard bands at the foot
        mb.cylinder(0, 0, 0.3 + k * 0.4, 0.5 + k * 0.4, 0.275, "M_Hazard_Dark", seg=10, cap_top=False)
    lathe(mb, [(0.0, 5.55), (0.36, 5.55), (0.36, 5.85), (0.0, 5.85)], "M_Hazard_Dark", seg=10)
    bbox(mb, -1.7, -0.17, 5.85, reach + 0.25, 0.17, 6.25, "M_Hazard", bevel=0.03)        # jib
    beam(mb, (0.0, 0.0, 7.1), (reach, 0.0, 6.25), 0.08, 0.08, "M_Metal_Dark")              # tie rod
    beam(mb, (0.0, 0.0, 7.1), (-1.6, 0.0, 6.25), 0.08, 0.08, "M_Metal_Dark")
    mb.cylinder(0, 0, 6.25, 7.2, 0.1, "M_Metal_Dark", seg=6)
    bbox(mb, -1.75, -0.45, 5.0, -1.0, 0.45, 5.85, "M_Wall_Concrete", bevel=0.04)          # counterweight
    bbox(mb, reach - 0.35, -0.24, 5.65, reach + 0.15, 0.24, 5.85, "M_Metal_Dark")         # trolley
    bbox(mb, reach - 0.13, -0.025, hook_z + 0.35, reach - 0.07, 0.025, 5.65, "M_Metal_Dark")     # cable
    bbox(mb, reach - 0.08, -0.025, hook_z + 0.35, reach - 0.02, 0.025, 5.65, "M_Metal_Dark")
    bbox(mb, reach - 0.3, -0.18, hook_z, reach + 0.15, 0.18, hook_z + 0.4, "M_Hazard", bevel=0.03)   # block
    return mb


def deck_run(poly_local, y_edge_fn, x0, x1, width=4.0, m=0.05, dx=0.1):
    """Longest run [xa, xb] inside [x0, x1] where the FULL deck section (front over the coping .. back)
    lies inside the (convex) site polygon -> the deck ends are cut square to the quay, no wedges."""
    best, cur = None, None
    k = 0
    while x0 + k * dx <= x1 + 1e-9:
        x = x0 + k * dx
        ye = y_edge_fn(x)
        ok = (G.point_in_poly(Vector((x, ye - 0.12 - m)), poly_local) and
              G.point_in_poly(Vector((x, ye + width + m)), poly_local))
        cur = ((cur[0] if cur else x), x) if ok else None
        if cur and (best is None or cur[1] - cur[0] > best[1] - best[0]):
            best = cur
        k += 1
    return best


def quay_deck_mb(poly_local, y_edge_fn, x0, x1, width=4.0, step=1.0):
    """Timber boardwalk on the quay from x0 to x1 (square ends, see deck_run): from the water edge (incl.
    the coping) back *width* metres; plank joints; fender posts down the quay wall every 2 m."""
    mb = MeshBuilder()
    xs = []
    x = x0
    while x < x1 - 0.3:
        xs.append(x)
        x += step
    xs.append(x1)
    front = [Vector((x, y_edge_fn(x) - 0.12)) for x in xs]
    back = [Vector((x, y_edge_fn(x) + width)) for x in reversed(xs)]
    band = clip_convex(front + back, poly_local)
    if len(band) < 3:
        return mb
    mb.prism(G.ensure_ccw(band), C.GROUND_Z - 0.06, DECK_Z, "M_Wood_Light", "M_Trim_Wood")
    for x in xs[1:-1]:                                     # plank joints (thin dark strips)
        ye = y_edge_fn(x)
        q = clip_convex([Vector((x - 0.025, ye - 0.08)), Vector((x + 0.025, ye - 0.08)),
                         Vector((x + 0.025, ye + width - 0.05)), Vector((x - 0.025, ye + width - 0.05))], band)
        if len(q) >= 3:
            mb.prism(G.ensure_ccw(q), DECK_Z - 0.01, DECK_Z + 0.008, "M_Trim_Wood", "M_Trim_Wood")
    x = x0 + 1.0
    while x < x1 - 0.5:                                    # fender posts on the quay wall face
        ye = y_edge_fn(x)
        if G.point_in_poly(Vector((x, ye - 0.3)), poly_local) and G.point_in_poly(Vector((x, ye + 0.2)), poly_local):
            bbox(mb, x - 0.12, ye - 0.26, WATER_Z - 0.25, x + 0.12, ye - 0.02, DECK_Z + 0.04, "M_Trim_Wood")
        x += 2.0
    return mb


# =============================================================================== build
def _frame(S):
    """Fit S.rot to the canal edge inside the polygon; return (edge points in local frame)."""
    river = S.ctx.get("river")
    pts = [p for p in river.left if G.point_in_poly(p, S.poly)] if river else []
    if len(pts) >= 2:
        d = pts[-1] - pts[0]
        S.rot = math.atan2(d.y, d.x)
    else:
        S.rot = math.radians(-37.5)
    near = []
    if river:
        x0, y0, x1, y1 = G.bbox(S.poly)
        near = [S.to_local(p) for p in river.left if x0 - 30 < p.x < x1 + 30 and y0 - 30 < p.y < y1 + 30]
        near.sort(key=lambda p: p.x)
    return near


def build(S):
    cnt = Counter()
    edge = _frame(S)
    P = G.ensure_ccw([S.to_local(p) for p in S.poly])

    def y_edge(x):
        if not edge:
            return -7.7
        if x <= edge[0].x:
            return edge[0].y
        for a, b in zip(edge, edge[1:]):
            if a.x <= x <= b.x:
                t = (x - a.x) / max(1e-6, b.x - a.x)
                return a.y + (b.y - a.y) * t
        return edge[-1].y

    def inside(x, y, m=0.0):
        if not G.point_in_poly(Vector((x, y)), P):
            return False
        if m <= 0:
            return True
        return all(G.point_in_poly(Vector((x + dx, y + dy)), P) for dx, dy in ((m, 0), (-m, 0), (0, m), (0, -m)))

    # water frontage inside the polygon
    fx = [x * 0.5 for x in range(-80, 80) if inside(x * 0.5, y_edge(x * 0.5) + 0.3)]
    wx0, wx1 = (min(fx), max(fx)) if fx else (-18.0, 8.0)

    # ---- hardstanding (boatyard + office forecourt) behind the deck
    yl = max(y_edge(x) for x in (-20, -10, 0, 10, 20)) + 0.75
    yard_rect = [Vector((wx0 - 1.5, yl)), Vector((30.0, yl)), Vector((30.0, 17.0)), Vector((wx0 - 1.5, 17.0))]
    land = clip_convex(clip_convex(P, yard_rect), [Vector((-60, yl)), Vector((60, yl)), Vector((60, 60)),
                                                    Vector((-60, 60))])
    if len(land) >= 3:
        mb = MeshBuilder()
        mb.prism(G.ensure_ccw(land), C.GROUND_Z - 0.06, 0.03, "M_Concrete", "M_Curb")
        put_mb(S, "Hardstanding", mb, 0.0, 0.0, 0.0, sub="Ground", counter=cnt)

    # ---- quay deck + fenders (ends cut square where the full 4 m section still fits the polygon)
    run = deck_run(P, y_edge, wx0 - 6.0, wx1 + 6.0)
    dx0, dx1 = run if run else (wx0, wx1)
    put_mb(S, "QuayDeck", quay_deck_mb(P, y_edge, dx0, dx1), 0.0, 0.0, 0.0, sub="Quay", counter=cnt)
    fx0, fx1 = max(wx0, dx0), min(wx1, dx1)          # deck furniture stays on the deck

    # ---- pontoon in the water sliver + gangway
    ye = y_edge(-8.0)
    py0, py1 = ye - 1.95, ye - 0.15
    px0, px1 = -15.0, -1.0
    while not inside(px0, py0) and px0 < -10:
        px0 += 0.25
    while not inside(px1, py0) and px1 > -6:
        px1 -= 0.25
    pz = WATER_Z + 0.4
    pm = (px0 + px1) / 2 - 1.0                     # two pontoon sections joined by a hinge plate
    put_mb(S, "Pontoon_A", pontoon_mb(px0, pm - 0.08, py0, py1, pz), 0.0, 0.0, 0.0, sub="Water", counter=cnt)
    put_mb(S, "Pontoon_B", pontoon_mb(pm + 0.08, px1, py0, py1, pz), 0.0, 0.0, 0.0, sub="Water", counter=cnt)
    hg = MeshBuilder()
    bbox(hg, pm - 0.3, py0 + 0.25, pz - 0.02, pm + 0.3, py1 - 0.25, pz + 0.025, "M_Metal")
    put_mb(S, "PontoonHinge", hg, 0.0, 0.0, 0.0, sub="Water", counter=cnt)
    # landing platform over the water at the east end of the pontoon (deck level) + gangway down
    ld = MeshBuilder()
    lx0, lx1 = px1 - 1.1, px1 + 0.35
    bbox(ld, lx0, py1 - 0.98, DECK_Z - 0.12, lx1, ye - 0.1, DECK_Z, "M_Wood_Light")
    for x in (lx0 + 0.12, lx1 - 0.12):
        ld.cylinder(x, py1 - 0.86, C.CANAL_BED_Z, DECK_Z - 0.12, 0.1, "M_Trim_Wood", seg=6, cap_top=False)
    put_mb(S, "GangwayLanding", ld, 0.0, 0.0, 0.0, sub="Water", counter=cnt)
    gw = gangway_mb(4.4, 0.92, DECK_Z - 0.02 - pz)
    put_mb(S, "Gangway", gw, lx0, py1 + 0.0, DECK_Z - 0.02, sub="Water", counter=cnt)

    # ---- boats on the water (inside the sliver)
    lau = shared_mesh("MA_Launch", launch_mb, smooth=("M_Metal",))
    by = py0 - 0.15 - 0.83
    bx = -10.2
    for _ in range(30):
        if inside(bx - 2.0, by - 0.6) and inside(bx + 2.0, by - 0.6):
            break
        bx += 0.2
    place(S, lau, "Boat_Launch", bx, by, WATER_Z - 0.32, 0.0, sub="Boats", counter=cnt)
    can = shared_mesh("MA_Canoe", canoe_mb)
    cy = py0 - 0.15 - 0.42
    cx = bx + 4.3
    for _ in range(30):
        if inside(cx + 1.6, cy - 0.3):
            break
        cx -= 0.2
    place(S, can, "Boat_Canoe", cx, cy, WATER_Z - 0.18, math.radians(3), recolor={AWN: "M_Hazard_Orange"},
          sub="Boats", counter=cnt)
    pile = shared_mesh("MA_Pile", pile_mb)
    for (x, y) in ((bx - 2.9, by - 0.75), (bx + 2.6, by - 0.5)):
        for _ in range(20):
            if inside(x, y, 0.25):
                break
            y += 0.15
        place(S, pile, "MooringPile", x, y, 0.0, 0.0, sub="Water", counter=cnt)

    # ---- jib crane at the west end lifting a dinghy off the pontoon
    hook = Vector((px0 + 1.6, (py0 + py1) / 2))
    base = Vector((max(max(wx0, -21.0) + 0.6, dx0 + 1.2), y_edge(wx0) + 2.4))     # plinth stays on the deck
    for _ in range(40):
        if inside(base.x, base.y, 0.9):
            break
        base.x += 0.25
    dv = hook - base
    reach = dv.length
    crot = math.atan2(dv.y, dv.x)
    crane = jib_crane_mb(reach, 1.25)
    put_mb(S, "JibCrane", crane, base.x, base.y, 0.03, crot, sub="Crane", counter=cnt)
    din = shared_mesh("MA_Dinghy", dinghy_mb)
    place(S, din, "Boat_Dinghy", hook.x, hook.y, 0.55, 0.12, sub="Boats", counter=cnt)

    # ---- harbor office (kit shed, gable to the water)
    oy = y_edge(-6.0) + 9.4
    spec = BuildingSpec("shed", 3, 2, 1, dict(wall="M_Wall_Sky", trim="M_Trim_White", door="M_Door_Navy",
                                               awning="M_Awning_Blue", roof="M_Roof_Terracotta",
                                               sign="M_Awning_Blue"),
                        roof="gable_front", ground_h=H3, feats={"door_i": 1, "style": "single"}, seed=4242)
    o = S.to_world(-6.0, oy)
    S.building(spec, o, S.rot, name=f"LM_{S.id}_HarborOffice")
    # sign board on the gable + life rings on the facade
    sg = MeshBuilder()
    bbox(sg, -1.5, -0.12, 0.0, 1.5, 0.0, 0.62, "M_Sign_Board", bevel=0.03)
    bbox(sg, -1.38, -0.15, 0.08, 1.38, -0.12, 0.54, "M_Sign_Face")
    for k, x in enumerate((-1.0, -0.55, -0.1, 0.35, 0.8)):
        bbox(sg, x - 0.17, -0.17, 0.2, x + 0.17, -0.15, 0.42, "M_Door_Navy" if k % 2 == 0 else "M_Awning_Blue")
    put_mb(S, "OfficeSign", sg, -6.0, oy - 0.02, 3.35, 0.0, sub="Office", counter=cnt)
    lr = shared_mesh("MA_LifeRingStand", lifering_stand_mb)
    # ---- deck furniture: bollards, life rings, lamps, benches
    bol = shared_mesh("MA_Bollard", bollard_mb, smooth=("M_Metal_Dark",), angle=55)
    x = fx0 + 1.0
    k = 0
    while x < fx1 - 0.5:
        y = y_edge(x) + 0.45
        if inside(x, y, 0.3) and not (px1 - 0.5 < x < px1 + 1.2):
            place(S, bol, f"Bollard_{k:02d}", x, y, DECK_Z, 0.0, sub="Quay", counter=cnt)
            k += 1
        x += 3.7
    for i, x in enumerate((fx0 + 3.0, (fx0 + fx1) / 2 + 1.5, fx1 - 0.8)):
        y = y_edge(x) + 3.4
        if inside(x, y, 0.4):
            place(S, lr, f"LifeRing_{i + 1}", x, y, DECK_Z, 0.0, sub="Quay", counter=cnt)
    for x in (fx0 + 6.5, fx1 - 4.5):
        y = y_edge(x) + 3.3
        if inside(x, y, 0.4):
            kit(S, "Lamp_Park", x, y, DECK_Z, 0.0, sub="Quay")
    xbn = (fx0 + fx1) / 2 - 2.5
    kit(S, "Bench", xbn, y_edge(xbn) + 3.2, DECK_Z, 0.0, sub="Quay")

    # ---- boatyard: sailboat on cradle, day-sailer sloop on its trailer (two masts from the bridges), clutter
    sb = shared_mesh("MA_Sailboat", sailboat_mb, smooth=("M_Metal", "M_Awning_Cream"))
    sx, sy = 9.0, y_edge(9.0) + 8.6
    for _ in range(40):
        if inside(sx - 3.6, sy, 1.4) and inside(sx + 3.6, sy, 1.4):
            break
        sx -= 0.25
    place(S, sb, "Boat_Sailboat", sx, sy, 0.03, math.radians(8), sub="Boatyard", counter=cnt)
    mt = shared_mesh("MA_SloopTrailer", sloop_trailer_mb, smooth=("M_Metal", "M_Awning_Blue", "M_Awning_Cream"))
    tx, ty = sx + 1.5, sy + 5.6
    for _ in range(40):
        if inside(tx - 2.6, ty, 1.2) and inside(tx + 3.6, ty, 1.2):
            break
        tx -= 0.3
    place(S, mt, "Boat_SloopTrailer", tx, ty, 0.03, math.radians(-6), sub="Boatyard", counter=cnt)
    clutter = [("CrateStack", -12.5, 0.6, 0.2), ("Crate", -11.3, -0.6, 0.6), ("Barrel", -13.8, -0.4, 0.0),
               ("Barrel", -13.4, 0.5, 0.0), ("Pallet", 1.8, 1.4, 0.3), ("Crate", 1.6, 1.4, 0.1),
               ("CrateStack", 16.0, 2.0, -0.5), ("Barrel", 3.6, 9.5, 0.0), ("Pallet", 4.2, 11.0, 1.2),
               ("TrashBin", 0.6, -2.0, 0.0)]
    for piece, x, y, r in clutter:
        y = y_edge(x) + 7.7 + y if piece != "TrashBin" else y_edge(x) + 4.6
        if inside(x, y, 0.7):
            z = 0.03
            kit(S, piece, x, y, z, r, sub="Boatyard")
    # pennant pole next to the office
    fp = shared_mesh("TS_FlagPole", flagpole_mb, smooth=("M_Awning_Yellow", "M_Metal"))
    fx_, fy_ = -11.5, oy - 1.2
    if inside(fx_, fy_, 0.5):
        place(S, fp, "PennantPole", fx_, fy_, 0.03, 0.0, recolor={AWN: "M_Awning_Blue"}, sub="Office",
              scale=(0.8, 0.8, 0.8), counter=cnt)

    # chain-link fence along the inland edges of the yard (gate toward the warehouse gap on the NW side)
    if len(land) >= 3:
        from .town_square import inset_convex
        Lc = G.ensure_ccw([G.V(p) for p in land])
        inner = inset_convex(Lc, 0.45)
        for i in range(len(Lc)):
            a, b = Lc[i], Lc[(i + 1) % len(Lc)]
            mid = (a + b) / 2
            if mid.y < yl + 2.0:
                continue                     # quay side stays open
            ia, ib = inner[i], inner[(i + 1) % len(inner)]
            L = (ib - ia).length
            if L < 1.0:
                continue
            n = max(1, round(L / 3.0))
            d = (ib - ia) / L
            for k in range(n):
                m = ia + d * (L * (k + 0.5) / n)
                if -19.5 < m.x < -13.0 and m.y > 6.0:
                    continue                 # gate gap toward the warehouse passage
                if m.y < yl + 6.5:
                    continue                 # keep the quay ends open (walk along the water)
                kit(S, "Fence_Chain_3m", m.x, m.y, 0.03, math.atan2(d.y, d.x), sub="Fence",
                    scale=(L / (3.0 * n), 1.0, 1.0))
    # storage container + barrels + trees at the back of the yard
    for (piece, x, y, r, rc) in (("Container_6m", 19.5, 6.8, -0.75, {"awning": "M_Awning_Blue"}),
                                 ("Barrel", 15.6, 9.6, 0.0, None), ("Barrel", 16.3, 10.1, 0.0, None),
                                 ("CrateStack", 22.8, 2.2, -0.7, None), ("Pallet", 24.0, 0.4, 0.3, None)):
        if inside(x, y, 0.8):
            kit(S, piece, x, y, 0.03, r, recolor=rc, sub="Boatyard")
    for (x, y, sc) in ((-24.0, 6.4, 1.0), (4.0, 17.3, 0.9)):
        if inside(x, y, 1.5):
            kit(S, "Tree_Round_A", x, y, C.GROUND_Z, 0.4 * x, recolor={"foliage": "M_Foliage"}, sub="Boatyard",
                scale=(sc, sc, sc))

    S.register_lot(S.poly)
    out = cnt.report(S.n, S)
    out["water_frontage"] = [round(wx0, 1), round(wx1, 1)]
    out["deck_run"] = [round(dx0, 2), round(dx1, 2)]
    out["crane_reach"] = round(reach, 2)
    out["rot_deg"] = round(math.degrees(S.rot), 1)
    return out
