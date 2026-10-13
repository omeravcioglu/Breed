"""Phase 4 landmark builder "parks": LOOKOUT POINT (LANDMARKS["Lookout"], 16 x 16 m on Lookout Hill).

PLAN
  The site sits on the town-facing (south-west) foot of Lookout Hill, right where LookoutTrail leaves the
  Larch Court bulb and starts to climb. The ground here is only 0.1 - 3.5 m up the hill (it rises toward the
  NE corner), so the "lookout" is a raised timber LOOKOUT TOWER: a 4.4 x 4.4 m deck 3.4 m above the grass
  under a green hip roof (a gazebo on stilts), reached by one straight stair along its east side that lands
  next to the trail. From the deck you look south-west over the Hillcrest roofs to the canal and downtown.
    * deck: plank floor, railing with a gap at the stair landing, two benches (north rail looking south,
      east rail looking west) and a coin telescope in the south-west corner aimed at downtown.
    * under the deck: X-braced posts - a shady nook (goats like it, players can hide behind the bracing).
    * at the foot: a roofed trail-map board facing the trail, a park lamp, a bin, a dirt spur to the trail,
      bushes round the tower base and two round trees on the far (east) side of the trail to frame it.
  The trail itself crosses the site diagonally and stays completely clear (2 m wide + margins). Trail markers
  along the rest of LookoutTrail and the summit cairn / benches / flag are built by park.build_district
  (LookoutPark), which keeps out of this polygon.
Custom meshes: LM_Lookout_Tower (~2.5k tris), LM_Lookout_Telescope, LM_Lookout_MapBoard.
"""
import math

from mathutils import Vector

from .. import geom2d as G
from ..kit import nature as NK
from ..meshutil import MeshBuilder
from . import park as P

WOOD, WOOD_D = "M_Wood_Light", "M_Trim_Wood"


def tower_mb(gz, half=2.2, deck=3.4, eave=2.45, apex=3.85, stair_side=1, stair_w=1.15, landing=1.15):
    """Lookout tower in local coords (origin = deck centre at reference ground, z up).
    gz(x, y) -> local ground height at a local point (for the post / stringer feet).
    The stair runs along the +X side (stair_side=1), rising toward +Y, landing at the NE corner."""
    mb = MeshBuilder()
    h = half
    zd = deck
    # ---------------------------------------------------------------- posts (corners run up to the roof)
    pw = 0.15
    corners = [(sx * (h - 0.05), sy * (h - 0.05)) for sx in (-1, 1) for sy in (-1, 1)]
    for (x, y) in corners:
        NK.bbox(mb, x - pw, y - pw, gz(x, y) - 0.35, x + pw, y + pw, zd + eave, WOOD_D, bevel=0.025, skip=("-z",))
        # concrete footing
        NK.bbox(mb, x - 0.26, y - 0.26, gz(x, y) - 0.3, x + 0.26, y + 0.26, gz(x, y) + 0.18, "M_Concrete",
                bevel=0.02, skip=("-z",))
    # mid posts under the deck on the long sides
    for (x, y) in ((0.0, -h + 0.05), (0.0, h - 0.05), (-h + 0.05, 0.0)):
        NK.bbox(mb, x - 0.11, y - 0.11, gz(x, y) - 0.35, x + 0.11, y + 0.11, zd - 0.2, WOOD_D, skip=("-z",))
    # X bracing on the W, S and N faces under the deck
    zb0 = max(gz(x, y) for x, y in corners) + 0.35
    zb1 = zd - 0.35
    for (a, b) in (((-h, -h), (h, -h)), ((-h, h), (h, h)), ((-h, -h), (-h, h))):
        a, b = Vector(a), Vector(b)
        for (p0, p1) in ((a, b), (b, a)):
            q0 = Vector((p0.x, p0.y, zb0))
            q1 = Vector((p1.x, p1.y, zb1))
            d = (q1 - q0)
            q0 += d.normalized() * 0.18
            q1 -= d.normalized() * 0.18
            NK.beam(mb, q0, q1, 0.09, 0.13, WOOD_D, up=(0.0, 0.0, 1.0))
    # ---------------------------------------------------------------- deck: rim joists + planks
    NK.bbox(mb, -h, -h, zd - 0.32, h, h, zd - 0.1, WOOD_D)
    n = 14
    for k in range(n):
        x0 = -h + 0.02 + (2 * h - 0.04) * k / n
        x1 = -h + 0.02 + (2 * h - 0.04) * (k + 1) / n - 0.03
        NK.bbox(mb, x0, -h - 0.04, zd - 0.1, x1, h + 0.04, zd, WOOD if k % 4 else "M_Fence_Wood")
    # ---------------------------------------------------------------- railing (gap at the stair landing)
    rail_h = 1.05
    gap = (h - landing, h)       # y-range of the opening on the +X side
    segs = [((-h, -h), (h, -h)), ((h, h), (-h, h)), ((-h, h), (-h, -h)), ((h, -h), (h, gap[0]))]
    for (a, b) in segs:
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        d = (b - a) / L
        nn = max(1, int(round(L / 1.1)))
        for k in range(nn + 1):
            p = a + d * (L * k / nn)
            if (abs(abs(p.x) - h) < 1e-3 and abs(abs(p.y) - h) < 1e-3):
                continue           # corner posts already there
            NK.bbox(mb, p.x - 0.05, p.y - 0.05, zd, p.x + 0.05, p.y + 0.05, zd + rail_h, WOOD_D)
        for z, t in ((zd + rail_h - 0.06, 0.1), (zd + 0.5, 0.06)):
            NK.beam(mb, Vector((a.x, a.y, z)), Vector((b.x, b.y, z)), 0.12 if t > 0.08 else 0.06, t, WOOD,
                    up=(0.0, 0.0, 1.0))
        # balusters
        nb = int(L / 0.32)
        for k in range(1, nb):
            p = a + d * (L * k / nb)
            NK.bbox(mb, p.x - 0.025, p.y - 0.025, zd + 0.02, p.x + 0.025, p.y + 0.025, zd + 0.5, WOOD)
    # ---------------------------------------------------------------- hip roof
    ov = 0.5
    R = h + ov
    ze, za = zd + eave, zd + apex
    NK.bbox(mb, -h - 0.08, -h - 0.08, ze - 0.22, h + 0.08, h + 0.08, ze, WOOD_D)
    NK.lathe(mb, [(NK.sq(R), ze - 0.05), (NK.sq(R), ze + 0.1), (NK.sq(R - 0.05), ze + 0.13), (0.0, za)],
             "M_Roof_Green", seg=4, phase=math.pi / 4, mats=["M_Trim_White", "M_Roof_Green", "M_Roof_Green"])
    # soffit (underside, facing down)
    sof = [(-R, -R), (-R, R), (R, R), (R, -R)]
    mb.face([(x, y, ze - 0.05) for x, y in sof], "M_Trim_White")
    NK.lathe(mb, [(0.12, za - 0.08), (0.12, za + 0.18), (0.18, za + 0.24), (0.0, za + 0.45)], "M_Metal_Dark", seg=6)
    # ---------------------------------------------------------------- stair along +X, rising to +Y
    sx0 = h + 0.1
    sx1 = sx0 + stair_w
    xs = stair_side
    xa, xb = (sx0, sx1) if xs > 0 else (-sx1, -sx0)
    xm = (xa + xb) / 2
    y_top = h - landing                      # stair arrives here, the landing continues to +h
    nr = int(round(zd / 0.2))
    rise = zd / nr
    run = 0.28
    y_bot = y_top - run * (nr - 1)
    # landing platform
    NK.bbox(mb, xa, y_top, zd - 0.1, xb, h + 0.04, zd, WOOD)
    NK.bbox(mb, xa, y_top, zd - 0.32, xb, h, zd - 0.1, WOOD_D)
    for yy in (h - 0.05,):
        x = xb - 0.06 if xs > 0 else xa + 0.06
        NK.bbox(mb, x - 0.09, yy - 0.09, gz(x, yy) - 0.35, x + 0.09, yy + 0.09, zd + rail_h, WOOD_D, skip=("-z",))
    # treads
    for k in range(nr - 1):
        z = rise * (k + 1)
        y1 = y_bot + run * (k + 1)
        y0 = y1 - run - 0.02
        NK.bbox(mb, xa + 0.06, y0, z - 0.05, xb - 0.06, y1, z, WOOD)
    # stringers (from ground at the foot to the landing)
    for x in (xa + 0.03, xb - 0.03):
        g = gz(x, y_bot - run)
        a = Vector((x, y_bot - run - 0.1, g - 0.05))
        b = Vector((x, y_top, zd - 0.12))
        NK.beam(mb, a, b, 0.07, 0.3, WOOD_D, up=(0.0, 0.0, 1.0))
        # handrail posts + rail
        pb = Vector((x, y_bot - 0.05, gz(x, y_bot) - 0.1))
        NK.bbox(mb, x - 0.05, pb.y - 0.05, pb.z, x + 0.05, pb.y + 0.05, rise + 0.95, WOOD_D)
        NK.beam(mb, Vector((x, y_bot - 0.05, rise + 0.92)), Vector((x, y_top + 0.05, zd + rail_h - 0.05)), 0.08,
                0.07, WOOD, up=(0.0, 0.0, 1.0))
    # outer landing rail (closing the landing's +X and +Y edges)
    xo = xb - 0.04 if xs > 0 else xa + 0.04
    NK.beam(mb, Vector((xo, y_top + 0.05, zd + rail_h - 0.05)), Vector((xo, h - 0.05, zd + rail_h - 0.05)), 0.1, 0.07,
            WOOD, up=(0.0, 0.0, 1.0))
    NK.beam(mb, Vector((xa, h - 0.04, zd + rail_h - 0.05)), Vector((xb, h - 0.04, zd + rail_h - 0.05)), 0.1, 0.07,
            WOOD, up=(0.0, 0.0, 1.0))
    # stair-side post under the landing
    x = xb - 0.06 if xs > 0 else xa + 0.06
    NK.bbox(mb, x - 0.09, y_top - 0.09, gz(x, y_top) - 0.35, x + 0.09, y_top + 0.09, zd - 0.1, WOOD_D, skip=("-z",))
    return mb, (xm, y_bot - run)


def build(S):
    lay = S.layout
    rng = S.rng
    plan = P.Planner(S, keep_in=S.poly)
    trail = next((p for p in lay.PATHS if p["id"] == "LookoutTrail"), None)
    tpl = P.path_polyline(trail) if trail else None
    objs = []
    rep = {}
    # ---------------------------------------------------------------- tower position: NW half of the site
    x0, y0, x1, y1 = G.bbox(S.poly)
    half = 2.2
    T = Vector((x0 + half + 0.55 + 0.0, y1 - half - 1.7))
    zref = S.ground_z(T.x, T.y)

    def gz(lx, ly):
        return S.ground_z(T.x + lx, T.y + ly) - zref

    mb, foot = tower_mb(gz, half=half)
    objs.append(P.obj_at(S, "Tower", mb, T.x, T.y, zref, 0.0, sub=P.subc(S, "Tower")))
    for k in (-1, 0, 1):
        plan.occ.add(T + Vector((0.0, k * 1.6)), 3.0)
    deck_z = zref + 3.4
    rep["tower"] = dict(center=(round(T.x, 1), round(T.y, 1)), ground=round(zref, 2), deck_z=round(deck_z, 2))
    # trail clearance check (report)
    if tpl is not None:
        dmin = 1e9
        for lx in (-half - 0.5, half + 1.35):
            for ly in (-half - 1.5, 0.0, half + 0.5):
                q = T + Vector((lx, ly))
                s, d = P._closest_s(tpl, q)
                dmin = min(dmin, d)
        rep["tower_trail_clear_m"] = round(dmin - 1.0, 2)
    # ---------------------------------------------------------------- deck furniture
    to_town = (Vector((40.0, 60.0)) - T).normalized()
    tel = T + Vector((-half + 0.55, -half + 0.55))
    objs.append(P.obj_at(S, "Telescope", P.coin_telescope_mb(), tel.x, tel.y, deck_z, P.face_rot(to_town),
                         sub=P.subc(S, "Tower"), smooth=("M_Metal_Dark", "M_Awning_Teal"), angle=45))
    S.put("Bench", T.x, T.y + half - 0.55, deck_z, P.face_rot((0.0, -1.0)), sub=P.subc(S, "Tower"))
    S.put("Bench", T.x + half - 0.55, T.y - 0.75, deck_z, P.face_rot((-1.0, 0.0)), sub=P.subc(S, "Tower"))
    # ---------------------------------------------------------------- foot of the stair: path, board, lamp, bin
    fw = T + Vector(foot)
    if tpl is not None:
        s, d = P._closest_s(tpl, fw)
        tp = tpl.pos(s)
        dirt = (tp - fw)
        if dirt.length > 1.2:
            e = tp - dirt.normalized() * 0.6
            S.path_ribbon("Path_Stair", [fw + Vector((0.0, 0.4)), (fw + e) / 2, e], width=1.4, mat="M_Dirt",
                          sub=P.subc(S, "Paths"))
            plan.paths.add(fw, e, 0.7)
        # trail-map board on the stair side, facing the trail
        tn = G.left_normal(tpl.tangent(s))
        if tn.dot(T - tp) < 0:
            tn = -tn
        bp = tp + tn * 2.6 - tpl.tangent(s) * 4.2
        if not plan.ok(bp, r=1.0, road=0.5, path=0.3):
            bp = tp + tn * 2.6 - tpl.tangent(s) * 6.0
        objs.append(P.obj_at(S, "MapBoard", P.notice_board_mb(face_notes=("M_Wall_Sky", "M_Sign_Face", "M_Wall_Mint"),
                                                                roof="M_Roof_Green", w=1.4),
                             bp.x, bp.y, P.zmin(S, bp, 0.8) - 0.02, P.face_rot(-tn), sub=P.subc(S, "Trailhead")))
        plan.occ.add(bp, 1.1)
        for off in ((-0.3, -1.7), (-1.2, -2.0), (0.4, -2.4)):
            lp = fw + Vector(off)
            if not plan.paths.blocked(lp, extra=0.35) and plan.occ.free(lp, 0.3):
                plan.occ.add(lp, 0.4)
                S.put("Lamp_Park", lp.x, lp.y, P.zmin(S, lp, 0.3) - 0.02, 0.0, sub=P.subc(S, "Trailhead"))
                rep["lamp"] = (round(lp.x, 1), round(lp.y, 1))
                break
        plan.prop("TrashBin", fw + Vector((-1.1, -1.3)), P.face_rot((0.0, -1.0)), r=0.4, sub="Trailhead")
        # two framing trees on the far (east) side of the trail
        tr = 0
        for q in ((x1 - 2.6, y0 + 3.2), (x1 - 1.8, y0 + 9.2), (x1 - 6.5, y0 + 2.2)):
            q = Vector(q)
            if tr < 2 and plan.ok(q, r=1.5, road=1.0, path=1.8):
                plan.tree(q, piece="Tree_Round_A", foliage="M_Foliage" if tr == 0 else "M_Foliage_Autumn",
                          scale=1.1, r=3.0)
                tr += 1
        rep["trees"] = tr
    # bushes hugging the tower base (W + N sides)
    for q in ((-half - 0.9, -1.2), (-half - 0.8, 1.0), (-0.6, half + 0.9), (1.2, half + 1.0), (-half - 0.7, -half - 0.6)):
        p = T + Vector(q)
        if S.inside(p) and S.clear_of_roads(p, extra=0.5):
            S.put("Bush_B" if q[1] > 0 else "Bush_A", p.x, p.y, P.zmin(S, p, 0.6) - 0.03, rng.uniform(0, 6.28),
                  recolor={"foliage": rng.choice(["M_Foliage", "M_Foliage_Dark"])}, sub=P.subc(S, "Plants"))
    rep["custom_tris"] = P.tri_count(objs)
    return rep
