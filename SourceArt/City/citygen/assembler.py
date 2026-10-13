"""Building assembler: turns a compact BuildingSpec into kit-piece instances.

Local frame (same as the kit): origin = front-center of the footprint at the building base,
front facade on y = 0 facing -Y, footprint x in [-W/2, W/2], y in [0, D].
Every building is an Empty root (BLD_...) with linked-duplicate kit pieces as children, so the
whole city stays modular: editing a kit mesh updates every building that uses it.
"""
import math
import random

from mathutils import Vector

from . import config as C
from . import kit as K
from . import scene

H3, H4 = C.FLOOR_H, C.SHOP_FLOOR_H
MW = C.MODULE_W
R90 = math.pi / 2

SIDES = ("front", "right", "back", "left")
CORNERS = (("FR", 0.0), ("BR", R90), ("BL", math.pi), ("FL", -R90))


class BuildingSpec:
    def __init__(self, archetype, nw, nd, floors, colors, roof="flat", ground_h=H3, feats=None, seed=0,
                 exposed=None, district=""):
        self.archetype = archetype
        self.nw, self.nd = nw, nd
        self.floors = floors
        self.colors = colors
        self.roof = roof
        self.ground_h = ground_h
        self.feats = feats or {}
        self.seed = seed
        self.exposed = exposed or {}
        self.district = district

    @property
    def W(self):
        return self.nw * MW

    @property
    def D(self):
        return self.nd * MW

    def heights(self):
        return [self.ground_h] + [H3] * (self.floors - 1)

    def wall_top(self):
        return sum(self.heights())

    def front_protrusion(self):
        """How far things stick out in front of the facade (porch / awning)."""
        if self.feats.get("porch"):
            return 2.3
        if self.feats.get("awning"):
            return 1.6
        return 0.4

    def roof_height(self):
        if self.roof.startswith("gable"):
            span = self.D if self.roof in ("gable_side", "gable_low") else self.W
            pitch = 18.0 if span >= 12 else 35.0
            return span / 2 * math.tan(math.radians(pitch))
        return 0.9


def side_slots(spec):
    """(side, index, n, x, y, rot) for every facade module, ordered left-to-right seen from outside."""
    W, D = spec.W, spec.D
    out = []
    for i in range(spec.nw):
        out.append(("front", i, spec.nw, -W / 2 + 1.5 + MW * i, 0.0, 0.0))
    for j in range(spec.nd):
        out.append(("right", j, spec.nd, W / 2, 1.5 + MW * j, R90))
    for i in range(spec.nw):
        out.append(("back", i, spec.nw, W / 2 - 1.5 - MW * i, D, math.pi))
    for j in range(spec.nd):
        out.append(("left", j, spec.nd, -W / 2, D - 1.5 - MW * j, -R90))
    return out


def corner_slots(spec):
    W, D = spec.W, spec.D
    pos = {"FR": (W / 2, 0.0), "BR": (W / 2, D), "BL": (-W / 2, D), "FL": (-W / 2, 0.0)}
    return [(k, pos[k][0], pos[k][1], r) for k, r in CORNERS]


# --------------------------------------------------------------------------- facade rules
def _upper_style(rng, arche):
    if arche == "apartment":
        return rng.choice(["wide", "balcony", "pair", "balcony"])
    if arche in ("mixed", "shop"):
        return rng.choice(["single", "pair", "alt", "wide"])
    if arche in ("house", "townhouse"):
        return rng.choice(["shutter", "single", "shutter"])
    return "single"


def _upper_piece(style, i, n, exposed=True):
    if not exposed:
        return "Wall_Window_H3" if (i == n // 2 and n >= 3) else "Wall_Plain_H3"
    if style == "pair":
        return "Wall_WindowPair_H3"
    if style == "wide":
        return "Wall_WindowWide_H3"
    if style == "alt":
        return "Wall_WindowPair_H3" if i % 2 else "Wall_Window_H3"
    if style == "balcony":
        return "Wall_BalconyDoor_H3" if i % 2 == (n % 2 == 0) else "Wall_WindowWide_H3"
    if style == "shutter":
        return "Wall_WindowShutter_H3"
    return "Wall_Window_H3"


def plan_facade(spec):
    """Return {(side, floor, idx): piece_name} plus a list of extra (piece, side, floor, idx, dz)."""
    rng = random.Random(spec.seed)
    a = spec.archetype
    plan, extras = {}, []
    n_of = {"front": spec.nw, "back": spec.nw, "right": spec.nd, "left": spec.nd}
    style = spec.feats.get("style") or _upper_style(rng, a)
    spec.feats["style"] = style
    door_i = spec.feats.get("door_i")
    if door_i is None:
        door_i = rng.randrange(spec.nw) if spec.nw <= 2 else rng.choice([spec.nw // 2, (spec.nw - 1) // 2])
        spec.feats["door_i"] = door_i
    shopish = a in ("shop", "mixed", "cafe", "commercial")
    for side in SIDES:
        n = n_of[side]
        exposed = side == "front" or spec.exposed.get(side, False)
        for f in range(spec.floors):
            for i in range(n):
                p = None
                if a == "warehouse":
                    if f == 0:
                        if side == "front":
                            pool = list(range(1, n - 1)) if n >= 3 else list(range(n))   # keep rollers off the corners
                            rd = spec.feats.setdefault("rollers", sorted(rng.sample(pool, min(len(pool), max(1, n // 2)))))
                            p = "Wall_RollerDoor_H4" if i in rd else ("Wall_Door_H4" if i == (rd[0] + 1) % n and i not in rd else "Wall_Industrial_H4")
                        elif side == "back" and i == n // 2:
                            p = "Wall_RollerDoor_H4"
                        else:
                            p = "Wall_Industrial_H4"
                    else:
                        p = "Wall_IndustrialWindow_H3" if (i % 2 == 0 and exposed) or (side in ("left", "right") and i % 3 == 1) else "Wall_Industrial_H3"
                elif a == "shed":
                    if side == "front":
                        p = "Wall_Door_H3" if i == door_i else rng.choice(["Wall_Industrial_H3", "Wall_Window_H3"])
                    else:
                        p = "Wall_Industrial_H3"
                elif shopish and f == 0:
                    if side == "front":
                        p = "Wall_StorefrontDoor_H4" if i == door_i else "Wall_Storefront_H4"
                    elif side == "back" and spec.feats.get("waterfront"):
                        p = "Wall_StorefrontDoor_H4" if i == n // 2 else "Wall_Storefront_H4"
                    elif exposed and i < 2:
                        p = "Wall_Storefront_H4"
                    elif side == "back" and i == 0:
                        p = "Wall_Door_H4"
                    elif side == "back":
                        p = "Wall_Window_H4" if i % 2 else "Wall_Plain_H4"
                    else:
                        p = "Wall_Window_H4" if (exposed and i % 2) else "Wall_Plain_H4"
                elif a == "apartment" and f == 0:
                    if side == "front":
                        p = "Wall_DoorGlass_H3" if i == door_i else "Wall_Window_H3"
                    elif side == "back" and i == 0:
                        p = "Wall_Door_H3"
                    else:
                        p = "Wall_Window_H3" if exposed or i % 2 else "Wall_Plain_H3"
                elif a in ("house", "townhouse") and f == 0:
                    if side == "front":
                        if i == door_i:
                            p = "Wall_Door_H3"
                        elif spec.feats.get("garage") and i == spec.feats.get("garage_i", -1):
                            p = "Wall_Garage_H3"
                        else:
                            p = "Wall_WindowShutter_H3" if style == "shutter" else "Wall_Window_H3"
                    elif side == "back" and i == n - 1:
                        p = "Wall_Door_H3"
                    else:
                        p = "Wall_Window_H3" if (i == n // 2 or exposed) else "Wall_Plain_H3"
                else:
                    if side == "front":
                        p = _upper_piece(style, i, n)
                        if a == "apartment" and i == door_i and p == "Wall_BalconyDoor_H3":
                            p = "Wall_WindowWide_H3"   # keep the entrance canopy clear of balconies
                    elif side == "back":
                        p = _upper_piece("single" if a != "apartment" else "single", i, n, exposed=(i % 2 == 0))
                    else:
                        if a == "apartment":
                            p = "Wall_Window_H3" if i % 2 == 0 or exposed else "Wall_Plain_H3"
                        else:
                            p = _upper_piece(style if exposed else "single", i, n, exposed=exposed)
                plan[(side, f, i)] = p
    return plan


# --------------------------------------------------------------------------- assembly
class _Asm:
    def __init__(self, spec, root, path, prefix):
        self.spec, self.root, self.path, self.prefix = spec, root, path, prefix
        self.k = 0
        self.count = 0

    def put(self, piece, x, y, z, rot=0.0, scale=None, recolor=True):
        name = piece if piece.startswith("KIT_") else "KIT_" + piece
        if not K.has(name):
            return None
        self.k += 1
        short = name[4:]
        inst = f"{self.prefix}.{short}.{self.k}"
        o = K.instance(name, self.path, (x, y, z), rot, parent=self.root,
                       recolor=self.spec.colors if recolor else None, scale=scale, inst_name=inst[:63])
        self.count += 1
        return o


HOUSE_RAISE = 0.35   # raised ground floor of houses = porch deck / Steps_2 height


def _pick_piece(name, fallback):
    return name if K.has("KIT_" + name) else fallback


def _meta(piece, key, default):
    """Numeric snap datum published by a kit piece (see walls.py docstring)."""
    r = K.REG.get("KIT_" + piece)
    if r is None:
        return default
    v = r["meta"].get(key, default)
    return v if isinstance(v, (int, float)) else default


_meta_det = _meta


def _corner_variant(p, i, n):
    """Swap wide-opening modules at a building end for their corner-safe variants.

    Modules are ordered left-to-right seen from outside, so module 0 touches the corner with its
    local -X end and module n-1 with its +X end.
    """
    if n <= 1 or 0 < i < n - 1:
        return p
    left = i == 0
    if p == "Wall_Storefront_H4":
        return _pick_piece("Wall_StorefrontCornerL_H4" if left else "Wall_StorefrontCorner_H4", p)
    if p == "Wall_StorefrontDoor_H4" and not left:
        return _pick_piece("Wall_StorefrontDoorL_H4", p)   # keep the door away from the corner
    if p.startswith("Wall_IndustrialWindow_") and not left:
        return _pick_piece(p.replace("IndustrialWindow_", "IndustrialWindowEnd_"), p)
    return p


def assemble(spec, name, loc, rot_z, path, base_z=C.LOT_Z):
    """Create the building. Returns (root_empty, piece_count)."""
    rng = random.Random(spec.seed * 7 + 3)
    root = scene.empty(name, path, (loc[0], loc[1], base_z), rot_z, display="ARROWS", size=1.5,
                       props=dict(bld_archetype=spec.archetype, bld_floors=spec.floors, bld_width=spec.W,
                                  bld_depth=spec.D, bld_roof=spec.roof, bld_district=spec.district,
                                  bld_wall=spec.colors.get("wall", ""), bld_seed=spec.seed))
    A = _Asm(spec, root, path, name)
    W, D = spec.W, spec.D
    hs = spec.heights()
    zs = [sum(hs[:i]) for i in range(len(hs))]
    top = spec.wall_top()
    a = spec.archetype
    shopish = a in ("shop", "mixed", "cafe", "commercial")
    industrial = a in ("warehouse", "shed")

    # houses sit on a raised ground floor (porch deck / steps height) like classic American homes
    RAISE = HOUSE_RAISE if a in ("house", "townhouse") else 0.0
    zs = [z + RAISE for z in zs]
    top += RAISE

    # foundation (fills the gap between ground and the building base / raised floor)
    depth = base_z - C.GROUND_Z + 0.25 + RAISE
    A.put("Foundation_1x1", 0.0, D / 2, RAISE, 0.0, scale=(W + 0.1, D + 0.1, depth), recolor=False)

    # facade modules (with corner-safe variants at building ends)
    plan = plan_facade(spec)
    final = {}
    slots = side_slots(spec)
    for f, (z, h) in enumerate(zip(zs, hs)):
        tag = "H4" if abs(h - H4) < 0.01 else "H3"
        for side, i, n, x, y, r in slots:
            p = plan[(side, f, i)]
            if tag == "H4" and p.endswith("_H3"):
                p = p[:-3] + "_H4"
            if industrial and p in ("Wall_Door_H4", "Wall_Door_H3"):
                p = _pick_piece("Wall_IndustrialDoor_" + tag, p)
            if RAISE and f == 0 and p == "Wall_Garage_H3":
                p = _pick_piece("Wall_GarageGrade_H3", p)
            p = _corner_variant(p, i, n)
            p = _pick_piece(p, "Wall_Plain_" + tag)
            final[(side, f, i)] = p
            A.put(p, x, y, z, r)
        cpiece = ("Corner_Industrial_" if industrial else "Corner_") + tag
        for _, cx, cy, cr in corner_slots(spec):
            A.put(_pick_piece(cpiece, "Corner_" + tag), cx, cy, z, cr)

    # plinth (door modules get the gapped variant; corner pieces are buried in the pilasters)
    if a in ("house", "townhouse", "apartment", "mixed") and K.has("KIT_Plinth_3m"):
        for side, i, n, x, y, r in slots:
            p = final[(side, 0, i)]
            if any(k in p for k in ("Storefront", "Garage", "Roller")):
                continue
            if "Door" in p:
                A.put("Plinth_Door_3m", x, y, 0.0, r)
            else:
                A.put("Plinth_3m", x, y, 0.0, r)

    # floor bands (corner pieces skipped: hidden inside the corner pilasters)
    if a in ("mixed", "apartment", "shop", "commercial") and spec.floors >= 2:
        for f in range(1, spec.floors):
            zb = zs[f] - 0.09
            for side, i, n, x, y, r in slots:
                A.put("FloorBand_3m", x, y, zb, r)

    # balconies / fire escapes / window boxes / window awnings
    win_awn = spec.feats.get("window_awnings")
    for side, i, n, x, y, r in slots:
        for f in range(spec.floors):
            p = final[(side, f, i)]
            if p == "Wall_BalconyDoor_H3":
                A.put("Balcony_3m", x, y, zs[f], r)
            if a in ("house", "townhouse") and spec.feats.get("windowboxes") and side == "front" and \
                    p.startswith("Wall_Window") and f == 0:
                A.put("WindowBox", x, y, zs[f] + _meta(p, "sill_bottom_z", 0.79) - 0.27, r)
            if win_awn and side == "front" and f >= 1 and p in ("Wall_Window_H3", "Wall_WindowShutter_H3"):
                A.put("Awning_Window", x, y, zs[f] + 2.75, r)
    if spec.feats.get("fire_escape") and spec.floors >= 3:
        fside = spec.feats.get("fire_escape_side", "back")
        cand = [s for s in slots if s[0] == fside]
        if cand:
            side, i, n, x, y, r = cand[min(1, len(cand) - 1)]
            for f in range(1, spec.floors):
                A.put("FireEscape_3m", x, y, zs[f], r)

    # entrances: porch / steps / canopies
    di = spec.feats.get("door_i", 0)
    fx = -W / 2 + 1.5 + MW * di
    if a in ("house", "townhouse"):
        if spec.feats.get("porch"):
            A.put("Porch_3m", fx, 0.0, 0.0, 0.0)
        else:
            A.put("Steps_2", fx, 0.0, 0.0, 0.0)
            A.put("Canopy_Door", fx, 0.0, zs[0] + _meta("Wall_Door_H3", "head_top_z", 2.34) + 0.11, 0.0)
        for side, i, n, x, y, r in slots:      # back door steps
            if side == "back" and final[(side, 0, i)].startswith("Wall_Door"):
                A.put("Steps_2", x, y, 0.0, r)
    if a == "apartment":
        A.put("Canopy_Door", fx, 0.0, zs[0] + _meta("Wall_DoorGlass_H3", "head_top_z", 2.74) + 0.06, 0.0)

    # shopfronts: fascia sign over the door, awnings over the display windows
    if shopish and spec.ground_h == H4:
        awn = spec.feats.get("awning")
        for side, i, n, x, y, r in slots:
            if side != "front":
                continue
            if i == di:
                A.put("Sign_Board_3m", x, y, 3.2, r)
            elif awn == "flat":
                A.put("Awning_Flat_3m", x, y, 3.25, r)
            elif awn:
                A.put("Awning_3m", x, y, _meta_det("Awning_3m", "place_z_on_H4", 3.3), r)
        if spec.feats.get("blade_sign") and spec.floors >= 2:
            A.put("Sign_Blade", -W / 2 + 0.5, 0.0, H4 + 0.4, 0.0)

    # roof
    if spec.roof == "flat":
        has_parapet = a not in ("shed",)
        cornice = a in ("mixed", "apartment", "shop", "commercial", "cafe") and spec.floors >= 1
        if cornice and K.has("KIT_Cornice_3m"):
            for side, i, n, x, y, r in slots:
                A.put("Cornice_3m", x, y, top - 0.4, r)
            for _, cx, cy, cr in corner_slots(spec):
                A.put("Cornice_Corner", cx, cy, top - 0.4, cr)
        if has_parapet:
            A.put("Roof_Flat_1x1", 0.0, D / 2, top, 0.0, scale=(W - 0.5, D - 0.5, 1.0), recolor=False)
            for side, i, n, x, y, r in slots:
                A.put("Parapet_3m", x, y, top, r)
            for _, cx, cy, cr in corner_slots(spec):
                A.put("Parapet_Corner", cx, cy, top, cr)
        else:
            A.put("Roof_Flat_1x1", 0.0, D / 2, top, 0.0, scale=(W + 0.3, D + 0.3, 1.0), recolor=False)
        # rooftop clutter
        roof_z = top + 0.2
        spots = []
        for _ in range(12):
            if W < 6 or D < 6:
                break
            spots.append((rng.uniform(-W / 2 + 1.6, W / 2 - 1.6), rng.uniform(1.6, D - 1.6)))
        used = []

        def free(px, py, rad):
            if any((px - ux) ** 2 + (py - uy) ** 2 < (rad + ur) ** 2 for ux, uy, ur in used):
                return False
            used.append((px, py, rad))
            return True

        if spec.feats.get("water_tank") and W >= 6 and D >= 6:
            px, py = W / 2 - 2.0, D - 2.0
            if free(px, py, 1.8):
                A.put("Roof_WaterTank", px, py, roof_z, rng.uniform(0, 6.28), recolor=False)
        if spec.feats.get("roof_access") and W >= 9:
            px, py = -W / 2 + 2.2, D - 2.2
            if free(px, py, 1.9):
                A.put("Roof_Access", px, py, roof_z, R90 * rng.randrange(4))
        for (px, py) in spots[: spec.feats.get("ac_units", 1 + (W * D > 120))]:
            if free(px, py, 1.0):
                A.put("Roof_AC_Unit", px, py, roof_z, R90 * rng.randrange(4), recolor=False)
        if a in ("commercial", "shop") and W >= 9:
            for (px, py) in spots[3:5]:
                if free(px, py, 1.1):
                    A.put("Roof_Skylight", px, py, roof_z, 0.0, recolor=False)
        if spec.feats.get("billboard") and W >= 6:
            A.put("Sign_Rooftop", 0.0, D * 0.55, roof_z, 0.0)
        if rng.random() < 0.6:
            for (px, py) in spots[5:7]:
                if free(px, py, 0.5):
                    A.put("Roof_Vent", px, py, roof_z, 0.0, recolor=False)
    else:
        _gable(A, spec, top, rng)
    return root, A.count


def _gable(A, spec, top, rng):
    W, D = spec.W, spec.D
    if spec.roof in ("gable_side", "gable_low"):
        span = int(round(D))
        if not K.has(f"KIT_Roof_Gable_S{span}_Mid"):
            A.put("Roof_Flat_1x1", 0.0, D / 2, top, 0.0, scale=(W + 0.3, D + 0.3, 1.0), recolor=False)
            return
        for i in range(spec.nw):
            A.put(f"Roof_Gable_S{span}_Mid", -W / 2 + 1.5 + MW * i, 0.0, top, 0.0)
        A.put(f"Roof_Gable_S{span}_EndL", -W / 2, 0.0, top, 0.0)
        A.put(f"Roof_Gable_S{span}_EndR", W / 2, 0.0, top, 0.0)
        A.put(f"Gable_S{span}", W / 2, D / 2, top, R90)
        A.put(f"Gable_S{span}", -W / 2, D / 2, top, -R90)
        ridge_axis = "x"
    else:  # gable_front: ridge along Y, gables face front/back
        span = int(round(W))
        if not K.has(f"KIT_Roof_Gable_S{span}_Mid"):
            A.put("Roof_Flat_1x1", 0.0, D / 2, top, 0.0, scale=(W + 0.3, D + 0.3, 1.0), recolor=False)
            return
        for j in range(spec.nd):
            A.put(f"Roof_Gable_S{span}_Mid", -W / 2, 1.5 + MW * j, top, -R90)
        # local +x of the end pieces maps to world -y under rot -90: EndR caps the front (y<0)
        A.put(f"Roof_Gable_S{span}_EndR", -W / 2, 0.0, top, -R90)
        A.put(f"Roof_Gable_S{span}_EndL", -W / 2, D, top, -R90)
        A.put(f"Gable_S{span}", 0.0, 0.0, top, 0.0)
        A.put(f"Gable_S{span}", 0.0, D, top, math.pi)
        ridge_axis = "y"
    if spec.feats.get("chimney") and span <= 9:
        pitch = math.radians(35.0)
        if ridge_axis == "x":
            cy = span * 0.28
            cz = top + math.tan(pitch) * cy - 0.25
            cx = rng.choice([-1, 1]) * (W / 2 - 1.2)
        else:
            cx = -W / 2 + span * 0.28
            cz = top + math.tan(pitch) * (span * 0.28) - 0.25
            cy = D - 1.5
        A.put("Chimney", cx, cy, cz, 0.0, recolor=False)
