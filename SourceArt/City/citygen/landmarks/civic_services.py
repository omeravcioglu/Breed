"""CIVIC SERVICES - Police Station, Fire Station, School, Church and Vet Clinic (densification pass).

Five civic anchors that make Willowbrook read as a busy, serviced town. One module, dispatch on S.id.
Every site uses its own frame (origin = site centre, local -Y = toward the street, see lmkit.Site);
coordinates below are site-local. Buildings come from the kit assembler (S.building) and are tuned
afterwards by swapping individual facade modules for other kit modules (swap()); custom MeshBuilder
geometry is used only for the hero pieces (signs, portico, steeple, vehicles, play equipment).
Sub collections are site-prefixed (<Site>_<Group>), object names LM_<Site>_<Thing>.

POLICE STATION (30 x 24 m, Canal Street, downtown)
  * Station: 2-storey red-brick "mixed" block 18 x 12 m (H4 civic ground floor: tall windows, centred glass
    double door), stone plinth, white cornice. Stone PORTICO on two piers with a deep navy fascia carrying big
    white "POLICE" letters, two BLUE LAMPS on brackets, flagpole (blue) on the forecourt.
  * Concrete forecourt with a plaza strip to the door, anti-ram bollards along the kerb, bench / planters /
    bike rack / mailbox.
  * Asphalt LOT (east, 10 x 24 m) with painted stalls: 3 white police cruisers (navy door panels with
    "POLICE", red/blue light bars), the yellow ANIMAL CONTROL van (gameplay hook: two-line livery + amber
    beacon) in the stall nearest the street, two staff cars; SALLY-PORT roller door on the station's east side.
  * Back yard (gravel): chain-link animal holding pen with doghouses + crates (animal control), dumpster.
  * Rooftop radio mast (lattice, dish, whips, red beacon) - a "police" silhouette among taller neighbours.
FIRE STATION (24 x 26 m, Main Street)
  * Red-brick 2-storey "commercial" block 15 x 15 m: three KIT_Wall_RollerDoor_H4 bays with custom classic red
    bay-door overlays (window row, panel grooves) and white piers, office door + window; a stepped brick
    false-front on the parapet with a cream board and red "FIRE DEPT" letters + a "1" roundel.
  * HOSE TOWER: 1 x 1 module, 5 storeys (kit assembler) with a custom hip cap -> ~18.5 m silhouette.
  * Concrete apron with bay guide lines, a chunky custom FIRE ENGINE (8.7 m, ladder, light bar) nosing out of
    the middle bay, hydrant, flagpole (red), bench; side lot with the chief's red car + a crew car, trees.
SCHOOL (50 x 40 m, Orchard Lane / Hillcrest)
  * Brick 3-storey central block (gable-front pediment with a cream "SCHOOL" panel, white cupola with a bell
    and a clock) + two 2-storey wings (42 m frontage), double glass entrance under a custom canopy.
  * Front: plaza walk with flagpole + "WILLOWBROOK SCHOOL" monument sign, bike racks, benches; bus bay with a
    custom yellow SCHOOL BUS; staff lot; lawns with trees and hedges along the wings.
  * Back: fenced basketball court (custom painted lines + two hoops) and a playground on sand (custom play
    tower with slide, seesaw, kit swings, benches, picnic tables), trees.
CHURCH (22 x 32 m, Elm Street)
  * White New-England meeting house: kit nave (tall H4 windows, steep S9 front gable, charcoal roof) raised on
    a 0.35 m plinth, kit 1 x 1 tower (3 storeys) + custom open belfry, white octagonal spire, gilded ball and
    weathervane (~21.5 m). Clock faces, red door, stone steps.
  * Front lawn with the walk, flowerbeds, lamps, benches, a "COMMUNITY CHURCH" notice board; a small
    churchyard (white pickets, rounded headstones, tree, bench) on the east side; garden behind, pines west.
VET CLINIC (22 x 20 m, Maple Street, next to the pet shop)
  * White 2-storey "shop" with teal trims, teal flat canopies, "VET CLINIC" fascia lettering and a custom
    teal CROSS + PAW medallion on the parapet (matching pylon sign at the kerb).
  * Forecourt with benches, planters, water bowl; animal-ambulance van (white, teal belt, cross+paw livery,
    "PET AMBULANCE", red/teal beacon) on its bay - gameplay hook (heal animals);
    chain-link DOG RUN (doghouse, hydrant post, shade tree, toys, water) east of the clinic; service yard.

GAMEPLAY ANCHORS: Empties LM_<Site>_Anchor_<Name> (collection <Site>_Gameplay) carry custom properties
(gameplay=<kind>, site, note) that export to Unity: animal_control, holding_pen, fire_engine, playground,
sports_court, school_bus, vet_heal, dog_run, animal_ambulance, civic_entrance. Vehicles that are hooks also
carry gameplay=<kind> (animal_control_van, animal_ambulance, school_bus).

All five register their whole site as a lot (street dressing keeps out). Report per site: custom_tris
(unique custom meshes, shared meshes counted once), instances, objects. Checked with _tmp/civic_services_audit.py
(inside polygon, clear of roads except kerb connectors, palette-only materials, LM_<Site> names) and a
backface-culling render diff (_tmp/civic_services_cull_diff.py): no see-through faces.
"""
import math

import bpy
from mathutils import Matrix, Vector

from .. import config as C
from .. import geom2d as G
from .. import kit as K
from .. import palette
from .. import scene
from ..assembler import BuildingSpec, H3, H4, side_slots
from ..meshutil import MeshBuilder
from ..kit.props import xprism, arch_pts, arch_side_mat, wheel, plate_decal, slant_decal
from .petshop import text_mb, paw_shapes, connector_poly, front_matrix, xf, Fence
from .town_square import bbox, extrude_xz, lathe, flagpole_mb, AWN as TS_AWN

Z_LOT = C.LOT_Z            # 0.15 sidewalk / plinth level
TAU = 2.0 * math.pi
R90 = math.pi / 2


# =============================================================================== small helpers
def _smooth(me, angle=40.0):
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(angle))


def flat_poly(mb, pts, z, mat):
    mb.tri_fill([G.ensure_ccw([Vector((p[0], p[1])) for p in pts])], z, mat)


def paint_line(mb, a, b, w, z, mat):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    n = Vector((-d.y, d.x)) * (w / 2)
    flat_poly(mb, [a - n, b - n, b + n, a + n], z, mat)


def paint_ring(mb, c, r, w, z, mat, a0=0.0, a1=TAU, n=24):
    def p(rr, t):
        return Vector((c[0] + rr * math.cos(t), c[1] + rr * math.sin(t)))
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n
        t1 = a0 + (a1 - a0) * (i + 1) / n
        flat_poly(mb, [p(r - w / 2, t0), p(r + w / 2, t0), p(r + w / 2, t1), p(r - w / 2, t1)], z, mat)


def paint_rect(mb, x0, y0, x1, y1, w, z, mat):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        paint_line(mb, a - d * (w / 2), b + d * (w / 2), w, z, mat)


def disc_y(mb, cx, cy, cz, r, t, mat, seg=16, side=None):
    """Disc facing -Y: front face at y = cy, thickness t back toward +Y."""
    sub = MeshBuilder()
    sub.cylinder(0, 0, 0.0, t, r, side or mat, seg=seg, cap_top=False)
    sub.face([Vector((r * math.cos(TAU * i / seg), r * math.sin(TAU * i / seg), t)) for i in range(seg)], mat)
    mb.extend(sub, Matrix.Translation((cx, cy, cz)) @ front_matrix() @ Matrix.Translation((0, 0, -t)))


def clock_face(mb, cx, cy, cz, r):
    """Clock on a wall facing -Y (front at cy): dark rim, white dial, hour ticks, two hands (10:10)."""
    disc_y(mb, cx, cy, cz, r, 0.08, "M_Trim_Dark", seg=20)
    disc_y(mb, cx, cy - 0.03, cz, r * 0.86, 0.03, "M_Sign_Face", seg=20)
    yf = cy - 0.035
    for k in range(4):
        t = TAU * k / 4
        x, z = cx + math.cos(t) * r * 0.7, cz + math.sin(t) * r * 0.7
        mb.box(x - 0.04, yf - 0.012, z - 0.04, x + 0.04, yf, z + 0.04, "M_Trim_Dark", skip=("+y",))
    for ang, L, w in ((math.radians(60), 0.45, 0.06), (math.radians(150), 0.68, 0.045)):
        sub = MeshBuilder()
        sub.box(-w / 2, -0.012, -0.04, w / 2, 0.0, r * L, "M_Trim_Dark", skip=("+y",))
        mb.extend(sub, Matrix.Translation((cx, yf - 0.002, cz)) @ Matrix.Rotation(-ang + R90, 4, "Y"))


def sign_text(txt, h, mat, max_w=None, depth=0.04):
    return text_mb(txt, h, depth, mat, max_w=max_w, offset=0.012, res=2)


def floor_z(spec, f):
    return sum(spec.heights()[:f])


def _kid_name(ch):
    parts = ch.name.split(".")
    return parts[1] if len(parts) >= 3 else ch.name


def kids(root, short=None, x=None, y=None, z=None, tol=0.03):
    out = []
    for ch in root.children:
        nm = _kid_name(ch)
        if short is not None and not nm.startswith(short):
            continue
        L = ch.location
        if (x is not None and abs(L.x - x) > tol) or (y is not None and abs(L.y - y) > tol) or \
                (z is not None and abs(L.z - z) > tol):
            continue
        out.append(ch)
    return out


def drop(objs):
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)


# =============================================================================== site context
class Civ:
    """Thin wrapper around the Site: site-prefixed sub collections, custom tri budget, swaps."""

    def __init__(self, S):
        self.S = S
        self.tris = 0
        self.seen = {}

    # -- names / frames
    def g(self, grp):
        return f"{self.S.id}_{grp}"

    def w(self, lx, ly):
        return self.S.to_world(lx, ly)

    def wp(self, pts):
        return [self.S.to_world(p[0], p[1]) for p in pts]

    def _count(self, me):
        if me.name not in self.seen:
            t = sum(len(p.vertices) - 2 for p in me.polygons)
            self.seen[me.name] = t
            self.tris += t

    # -- kit
    def put(self, piece, lx, ly, z=None, rot=0.0, grp="Props", recolor=None, scale=None, name=None):
        nm = f"LM_{self.S.id}_{name}" if name else None
        return self.S.put(piece, lx, ly, z, rot, recolor=recolor, scale=scale, local=True, sub=self.g(grp), name=nm)

    def building(self, name, spec, lx, ly, base_z=C.LOT_Z):
        return self.S.building(spec, self.w(lx, ly), self.S.rot, name=f"LM_{self.S.id}_{name}", base_z=base_z)

    def swap(self, root, spec, side, f, idx, piece, plinth=None):
        """Replace facade module (side, floor f, index idx) of an assembled building with kit *piece*.
        plinth: None keeps whatever plinth is there, "" removes it, else the plinth piece to put."""
        _, i, n, x, y, r = next(s for s in side_slots(spec) if s[0] == side and s[1] == idx)
        z = floor_z(spec, f)
        drop(kids(root, "Wall_", x, y, z))
        K.instance("KIT_" + piece, self.S.coll, (x, y, z), r, parent=root, recolor=spec.colors,
                   inst_name=f"{root.name}.{piece}.s{side[0]}{f}{idx}"[:63])
        if plinth is not None and f == 0:
            drop(kids(root, "Plinth", x, y, 0.0))
            if plinth:
                K.instance("KIT_" + plinth, self.S.coll, (x, y, 0.0), r, parent=root, recolor=spec.colors,
                           inst_name=f"{root.name}.{plinth}.s{side[0]}{idx}"[:63])
        return x, y, r

    # -- custom geometry
    def mesh(self, name, mb, lx=0.0, ly=0.0, z=0.0, rot=0.0, grp="Details", smooth=None):
        o = self.S.mesh(name, mb, sub=self.g(grp))
        p = self.w(lx, ly)
        o.location = (p.x, p.y, z)
        o.rotation_euler = (0.0, 0.0, self.S.rot + rot)
        if smooth:
            _smooth(o.data, smooth)
        self._count(o.data)
        return o

    def shared(self, key, fn, smooth=None):
        nm = "LMX_CS_" + key
        me = bpy.data.meshes.get(nm)
        if me is None:
            me = fn().build(nm)
            if smooth:
                _smooth(me, smooth)
        return me

    def inst(self, me, name, lx, ly, z, rot=0.0, grp="Details", recolor=None):
        p = self.w(lx, ly)
        self.S.n += 1
        o = scene.obj(f"LM_{self.S.id}_{name}"[:63], me, f"{self.S.coll}/{self.g(grp)}", (p.x, p.y, z),
                      self.S.rot + rot)
        if recolor:
            for i, slot in enumerate(o.material_slots):
                m = me.materials[i] if i < len(me.materials) else None
                if m is not None and m.name in recolor and recolor[m.name] != m.name:
                    slot.link = "OBJECT"
                    slot.material = palette.get(recolor[m.name])
        self._count(me)
        return o

    # -- ground
    def pave(self, name, pts, mat, z=Z_LOT, skirt=0.25, grp="Ground"):
        o = self.S.paving(name, self.wp(pts), mat, z=z, skirt=skirt, sub=self.g(grp))
        self._count(o.data)
        return o

    def connector(self, name, x0, x1, y, mat, z=Z_LOT - 0.01, grp="Ground"):
        """Paving from the site's front edge (local y) out to the kerb (hides under the kerb)."""
        S = self.S
        cp = connector_poly(S, self.w(x0, y), self.w(x1, y), Vector(S.facing), n=4)
        if cp:
            o = S.paving(name, cp, mat, z=z, skirt=0.25, sub=self.g(grp))
            self._count(o.data)
            S.register_lot(cp)
        return cp

    def flag(self, lx, ly, z, color, name="Flagpole", grp="Forecourt"):
        me = self.shared("Flagpole", flagpole_cs, smooth=50)
        return self.inst(me, name, lx, ly, z, rot=0.35, grp=grp, recolor={TS_AWN: color})

    def report(self, objects):
        top = sorted(self.seen.items(), key=lambda kv: -kv[1])[:6]
        return dict(custom_tris=self.tris, instances=self.S.n, objects=objects,
                    heaviest={k.replace("LM_", "").replace("LMX_CS_", "shared:"): v for k, v in top})


# =============================================================================== shared props
def flagpole_cs(h=8.6, fw=1.9, fh=1.15):
    """town_square.flagpole_mb + a white hoist sleeve that closes the flag's open edge at the pole
    (the shared flag has no face there - a 1 px see-through sliver with backface culling)."""
    mb = flagpole_mb(h, fw, fh)
    z1 = h - 0.25
    bbox(mb, 0.03, -0.04, z1 - fh - 0.03, 0.105, 0.04, z1 + 0.03, "M_Trim_White")
    return mb


def blue_lamp():
    """Classic police blue lamp on a wall bracket. Origin = wall plate centre on the wall (y = 0), lamp toward -Y."""
    mb = MeshBuilder()
    bbox(mb, -0.1, -0.05, -0.22, 0.1, 0.0, 0.18, "M_Metal_Dark", bevel=0.015)
    bbox(mb, -0.035, -0.5, 0.04, 0.035, -0.05, 0.11, "M_Metal_Dark")
    cy = -0.52
    bbox(mb, -0.04, cy - 0.04, -0.06, 0.04, cy + 0.04, 0.11, "M_Metal_Dark")
    lathe(mb, [(0.25, -0.12), (0.25, -0.06), (0.0, 0.06)], "M_Trim_Dark", seg=4, cx=0.0, cy=cy, phase=math.pi / 4)
    bbox(mb, -0.17, cy - 0.17, -0.7, 0.17, cy + 0.17, -0.12, "M_Awning_Blue", bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.17, cy + sy * 0.17
            bbox(mb, x - 0.03, y - 0.03, -0.72, x + 0.03, y + 0.03, -0.1, "M_Trim_Dark")
    bbox(mb, -0.2, cy - 0.2, -0.8, 0.2, cy + 0.2, -0.7, "M_Trim_Dark", bevel=0.015)
    bbox(mb, -0.17, cy - 0.175, -0.5, 0.17, cy + 0.175, -0.36, "M_Sign_Face")     # white "POLICE" band
    return mb


def radio_mast(h=6.4):
    """Rooftop police radio mast: triangular lattice, side dish, whip antennas, red beacon. Origin = base."""
    mb = MeshBuilder()
    bbox(mb, -0.45, -0.45, 0.0, 0.45, 0.45, 0.16, "M_Metal_Dark", bevel=0.02)
    r0, r1 = 0.32, 0.14
    legs = [TAU * k / 3 + math.pi / 2 for k in range(3)]

    def leg(t, z):
        r = r0 + (r1 - r0) * z / h
        return Vector((r * math.cos(t), r * math.sin(t), z))
    for t in legs:
        a, b = leg(t, 0.16), leg(t, h)
        d = b - a
        sub = MeshBuilder()
        sub.box(-0.035, -0.035, 0.0, 0.035, 0.035, d.length, "M_Metal")
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        mb.extend(sub, Matrix.Translation(a) @ rot)
    z = 0.9
    while z < h - 0.3:
        for i in range(3):
            a, b = leg(legs[i], z), leg(legs[(i + 1) % 3], z + 0.45)
            d = b - a
            sub = MeshBuilder()
            sub.box(-0.02, -0.02, 0.0, 0.02, 0.02, d.length, "M_Metal")
            mb.extend(sub, Matrix.Translation(a) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4())
        z += 0.9
    mb.cylinder(0, 0, h - 0.05, h + 1.6, 0.03, "M_Metal_Dark", seg=6, cap_bottom=True)
    mb.sphere(0, 0, h + 1.68, 0.11, "M_Awning_Red", seg=8, rings=4)
    for sx in (-1, 1):                         # whips (closed: seen from the street below)
        mb.cylinder(sx * 0.25, 0.0, h - 0.6, h + 0.7, 0.02, "M_Metal_Dark", seg=4, cap_bottom=True)
        bbox(mb, min(0.0, sx * 0.25), -0.02, h - 0.62, max(0.0, sx * 0.25), 0.02, h - 0.56, "M_Metal_Dark")
    dish = MeshBuilder()
    dish.cylinder(0, 0, 0.0, 0.12, 0.42, "M_Wall_White", seg=14, cap_top=True, cap_bottom=True, r_top=0.36)
    mb.extend(dish, Matrix.Translation((0.0, -0.3, h * 0.62)) @ Matrix.Rotation(R90, 4, "X"))
    return mb


def anchor(C_, name, lx, ly, z, kind, **props):
    """Gameplay anchor empty (exported to Unity with custom properties)."""
    p = C_.w(lx, ly)
    return scene.empty(f"LM_{C_.S.id}_Anchor_{name}", f"{C_.S.coll}/{C_.g('Gameplay')}", (p.x, p.y, z), C_.S.rot,
                       display="SPHERE", size=0.6, props=dict(gameplay=kind, site=C_.S.id, **props))


def police_livery():
    """Light bar + navy door panels with white POLICE lettering for KIT_Car_Sedan (same origin)."""
    mb = MeshBuilder()
    bbox(mb, -0.62, 0.1, 1.49, 0.62, 0.5, 1.56, "M_Trim_Dark", bevel=0.015)
    bbox(mb, -0.6, 0.14, 1.56, -0.04, 0.46, 1.7, "M_Awning_Red", bevel=0.025)
    bbox(mb, 0.04, 0.14, 1.56, 0.6, 0.46, 1.7, "M_Awning_Blue", bevel=0.025)
    bbox(mb, -0.04, 0.17, 1.56, 0.04, 0.43, 1.66, "M_Light_Emit")
    word = sign_text("POLICE", 0.2, "M_Sign_Face", max_w=1.25, depth=0.02)
    for sx in (-1, 1):
        x = sx * 0.905
        pts = [(x, -0.85, 0.42), (x, 0.85, 0.42), (x, 0.85, 0.84), (x, -0.85, 0.84)]
        plate_decal(mb, pts, (sx, 0, 0), 0.012, "M_Door_Navy")
        mb.extend(word, Matrix.Translation((x + sx * 0.011, 0.0, 0.63)) @ Matrix.Rotation(sx * R90, 4, "Z"))
    return mb


def animal_control_livery():
    """Two-line ANIMAL / CONTROL lettering on the cargo panel + green belt + amber beacon (KIT_Car_Van)."""
    mb = MeshBuilder()
    l1 = sign_text("ANIMAL", 0.3, "M_Zoo_Primary", max_w=1.6, depth=0.02)
    l2 = sign_text("CONTROL", 0.3, "M_Zoo_Primary", max_w=1.6, depth=0.02)
    for sx in (-1, 1):
        x = sx * 1.006
        for txt, z in ((l1, 1.82), (l2, 1.42)):
            mb.extend(txt, Matrix.Translation((x, 1.45, z)) @ Matrix.Rotation(sx * R90, 4, "Z"))
        plate_decal(mb, [(x, -1.05, 0.62), (x, 1.1, 0.62), (x, 1.1, 0.8), (x, -1.05, 0.8)], (sx, 0, 0), 0.012,
                    "M_Zoo_Primary")
    bbox(mb, -0.5, -0.4, 2.19, 0.5, 0.0, 2.27, "M_Trim_Dark", bevel=0.015)
    bbox(mb, -0.45, -0.36, 2.27, 0.45, -0.04, 2.42, "M_Hazard_Orange", bevel=0.03)
    return mb


def ambulance_livery():
    """Vet animal-ambulance livery for KIT_Car_Van: teal belt, cross+paw discs, PET AMBULANCE, beacon."""
    mb = MeshBuilder()
    txt = sign_text("PET AMBULANCE", 0.2, "M_Door_Teal", max_w=2.0, depth=0.02)
    for sx in (-1, 1):
        x = sx * 1.006
        plate_decal(mb, [(x, -1.7, 1.05), (x, 2.3, 1.05), (x, 2.3, 1.2), (x, -1.7, 1.2)], (sx, 0, 0), 0.012,
                    "M_Awning_Teal")       # starts behind the sloped bonnet (no floating sliver)
        med = cross_paw_mb(0.48, 0.03, rim="M_Awning_Teal")
        mb.extend(med, Matrix.Translation((x - sx * 0.0, 1.5, 1.66)) @ Matrix.Rotation(sx * R90, 4, "Z"))
        mb.extend(txt, Matrix.Translation((x, 0.05, 0.6)) @ Matrix.Rotation(sx * R90, 4, "Z"))
    # front: teal cross on the bonnet area above the grille
    bbox(mb, -0.5, -0.4, 2.19, 0.5, 0.0, 2.27, "M_Trim_Dark", bevel=0.015)
    bbox(mb, -0.47, -0.36, 2.27, -0.03, -0.04, 2.4, "M_Awning_Red", bevel=0.025)
    bbox(mb, 0.03, -0.36, 2.27, 0.47, -0.04, 2.4, "M_Awning_Teal", bevel=0.025)
    return mb


def cross_paw_mb(R=1.25, depth=0.36, rim="M_Awning_Red", cross="M_Sign_Face", paw="M_Door_Red", seg=28):
    """Round sign: teal disc, white medical cross, teal paw in its centre. Faces -Y; origin = disc back centre."""
    mb = MeshBuilder()
    d0 = depth * 0.55
    mb.cylinder(0, 0, 0.0, d0, R, rim, seg=seg, cap_top=True, cap_bottom=True)
    a, b = R * 0.74, R * 0.32
    cr = [(-b, -a), (b, -a), (b, -b), (a, -b), (a, b), (b, b), (b, a), (-b, a), (-b, b), (-a, b), (-a, -b), (-b, -b)]
    t = max(0.01, depth * 0.2)
    mb.prism(cr, d0, d0 + t, cross, cross)
    for shp in paw_shapes(2 * b * 0.92):
        mb.prism(shp, d0 + t, depth, paw, paw)
    return xf(mb, front_matrix())


def headstone():
    mb = MeshBuilder()
    pts = [(-0.3, 0.0), (0.3, 0.0), (0.3, 0.55)]
    pts += [(0.3 * math.cos(t), 0.55 + 0.22 * math.sin(t)) for t in [math.pi * k / 6 for k in range(1, 6)]]
    pts += [(-0.3, 0.55)]
    extrude_xz(mb, pts, -0.08, 0.08, "M_CanalStone")
    bbox(mb, -0.38, -0.16, -0.06, 0.38, 0.16, 0.08, "M_Rock", bevel=0.02)
    return mb


def hoop():
    """Basketball hoop: pole behind (+Y), backboard facing -Y, orange rim. Origin = pole foot... board at y=0."""
    mb = MeshBuilder()
    bbox(mb, -0.25, 0.85, -0.05, 0.25, 1.35, 0.25, "M_Wall_Concrete", bevel=0.03)
    bbox(mb, -0.08, 1.02, 0.25, 0.08, 1.18, 3.3, "M_Metal_Dark")
    bbox(mb, -0.06, 0.1, 3.0, 0.06, 1.18, 3.12, "M_Metal_Dark")
    bbox(mb, -0.92, 0.0, 2.72, 0.92, 0.1, 3.82, "M_Sign_Face", bevel=0.02)
    for (x0, z0, x1, z1) in ((-0.3, 2.95, 0.3, 3.0), (-0.3, 3.38, 0.3, 3.43), (-0.3, 2.95, -0.25, 3.43),
                             (0.25, 2.95, 0.3, 3.43)):
        mb.box(x0, -0.012, z0, x1, 0.0, z1, "M_Awning_Red", skip=("+y",))
    n = 10
    for k in range(n):
        t0, t1 = TAU * k / n, TAU * (k + 1) / n
        a = Vector((0.24 * math.cos(t0), -0.3 + 0.24 * math.sin(t0), 3.05))
        b = Vector((0.24 * math.cos(t1), -0.3 + 0.24 * math.sin(t1), 3.05))
        d = b - a
        sub = MeshBuilder()
        sub.box(0, -0.02, -0.02, d.length, 0.02, 0.02, "M_Hazard_Orange")
        mb.extend(sub, Matrix.Translation(a) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, "Z"))
    bbox(mb, -0.05, -0.08, 3.0, 0.05, 0.0, 3.08, "M_Hazard_Orange")
    return mb


def play_tower():
    """Playground tower: posts, deck, red pyramid roof, yellow slide (+X), green ladder (-X). Origin ground."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.95, sy * 0.95
            bbox(mb, x - 0.08, y - 0.08, 0.0, x + 0.08, y + 0.08, 3.05, "M_Awning_Blue", bevel=0.02)
    bbox(mb, -1.05, -1.05, 1.38, 1.05, 1.05, 1.52, "M_Wood_Light", bevel=0.02)
    for sy in (-1, 1):       # rails front / back
        bbox(mb, -0.95, sy * 0.95 - 0.04, 2.25, 0.95, sy * 0.95 + 0.04, 2.33, "M_Awning_Yellow")
        bbox(mb, -0.9, sy * 0.95 - 0.02, 1.52, 0.9, sy * 0.95 + 0.02, 2.25, "M_Awning_Green", skip=("-z", "+z"))
    # roof
    lathe(mb, [(1.55, 3.0), (1.55, 3.1), (0.0, 4.05)], "M_Awning_Red", seg=4, phase=math.pi / 4)
    lathe(mb, [(0.0, 2.98), (1.55, 3.0)], "M_Awning_Cream", seg=4, phase=math.pi / 4)
    # slide toward +X: chute from the deck edge down to the ground
    L0, L1, z0, z1 = 1.05, 3.9, 1.5, 0.3
    ang = math.atan2(z0 - z1, L1 - L0)
    ln = math.hypot(L1 - L0, z0 - z1)
    ch = MeshBuilder()
    ch.box(0.0, -0.4, -0.06, ln, 0.4, 0.0, "M_Awning_Yellow")
    for sy in (-1, 1):
        ch.box(0.0, sy * 0.4 - 0.04, -0.06, ln, sy * 0.4 + 0.04, 0.22, "M_Awning_Yellow")
    mb.extend(ch, Matrix.Translation((L0, 0.0, z0)) @ Matrix.Rotation(ang, 4, "Y"))
    bbox(mb, L1 - 0.05, -0.45, 0.0, L1 + 0.35, 0.45, 0.32, "M_Awning_Yellow", bevel=0.04)
    # ladder toward -X
    for sy in (-1, 1):
        bbox(mb, -1.75, sy * 0.35 - 0.05, 0.0, -1.62, sy * 0.35 + 0.05, 1.6, "M_Awning_Green")
    for k in range(4):
        z = 0.3 + k * 0.36
        x = -1.7 + (z / 1.6) * 0.6
        bbox(mb, -1.72, -0.35, z - 0.03, -1.6, 0.35, z + 0.03, "M_Awning_Green")
    return mb


def seesaw():
    mb = MeshBuilder()
    bbox(mb, -0.2, -0.3, 0.0, 0.2, 0.3, 0.55, "M_Awning_Red", bevel=0.04)
    pl = MeshBuilder()
    pl.box(-1.8, -0.16, -0.04, 1.8, 0.16, 0.04, "M_Wood_Light")
    for sx in (-1, 1):
        pl.box(sx * 1.55 - 0.18, -0.2, 0.04, sx * 1.55 + 0.18, 0.2, 0.1, "M_Awning_Blue")
        pl.box(sx * 1.25 - 0.03, -0.18, 0.04, sx * 1.25 + 0.03, 0.18, 0.45, "M_Awning_Yellow")
    mb.extend(F_bev(pl), Matrix.Translation((0, 0, 0.6)) @ Matrix.Rotation(math.radians(9), 4, "Y"))
    return mb


def merry_go_round():
    """Playground spinner: red/yellow segmented disc, centre post, four handle hoops."""
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0.0, 0.12, 0.25, "M_Metal_Dark", seg=10, cap_top=True)
    n = 8
    for k in range(n):
        t0, t1 = TAU * k / n, TAU * (k + 1) / n
        mat = "M_Awning_Red" if k % 2 else "M_Awning_Yellow"
        ring = [(0.0, 0.0)] + [(1.25 * math.cos(t0 + (t1 - t0) * j / 3), 1.25 * math.sin(t0 + (t1 - t0) * j / 3))
                               for j in range(4)]
        mb.prism(ring, 0.12, 0.26, mat, "M_Trim_White")
    mb.cylinder(0, 0, 0.26, 1.0, 0.06, "M_Metal", seg=8, cap_top=True)
    for k in range(4):
        t = TAU * k / 4 + math.pi / 8
        a = Vector((0.2 * math.cos(t), 0.2 * math.sin(t), 0.95))
        b = Vector((1.05 * math.cos(t), 1.05 * math.sin(t), 0.6))
        sub = MeshBuilder()
        d = b - a
        sub.box(0.0, -0.03, -0.03, d.length, 0.03, 0.03, "M_Metal")
        M = Matrix.Translation(a) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, "Z") @             Matrix.Rotation(-math.atan2(d.z, math.hypot(d.x, d.y)), 4, "Y")
        mb.extend(sub, M)
        mb.box(b.x - 0.03, b.y - 0.03, 0.26, b.x + 0.03, b.y + 0.03, 0.62, "M_Metal")
    return mb


def spring_rider(body="M_Awning_Green", accent="M_Awning_Yellow"):
    """Chunky spring rider (stylized pup) on a coil, facing -Y."""
    mb = MeshBuilder()
    mb.cylinder(0, 0, -0.02, 0.06, 0.3, "M_Metal_Dark", seg=10, cap_top=True)
    for k in range(4):
        mb.cylinder(0, 0, 0.06 + k * 0.1, 0.11 + k * 0.1, 0.12, "M_Metal", seg=8, cap_top=True)
        mb.cylinder(0, 0, 0.11 + k * 0.1, 0.16 + k * 0.1, 0.07, "M_Metal_Dark", seg=8, cap_top=True)
    bbox(mb, -0.2, -0.45, 0.45, 0.2, 0.42, 0.78, body, bevel=0.07)                 # body
    bbox(mb, -0.17, -0.62, 0.7, 0.17, -0.3, 1.02, body, bevel=0.06)                # head
    for sx in (-1, 1):
        bbox(mb, sx * 0.13 - 0.05, -0.5, 0.95, sx * 0.13 + 0.05, -0.38, 1.12, accent, bevel=0.02)   # ears
        bbox(mb, sx * 0.24 - 0.03, -0.42, 0.8, sx * 0.24 + 0.03, -0.36, 0.86, "M_Trim_Dark")      # handles
    bbox(mb, -0.07, -0.67, 0.78, 0.07, -0.6, 0.86, "M_Trim_Dark")                   # nose
    bbox(mb, -0.04, 0.4, 0.7, 0.04, 0.58, 0.78, accent, bevel=0.015)                # tail
    bbox(mb, -0.22, -0.12, 0.76, 0.22, 0.18, 0.82, accent, bevel=0.02)              # seat
    return mb


def F_bev(mb, w=0.015):
    from .. import facade as F
    return F.bevelled(mb, w)


# =============================================================================== vehicles
def fire_engine():
    """Chunky stylized fire engine ~8.7 m (nose -Y, origin ground centre): cab + body with roll-up lockers,
    white belt stripe, aerial ladder on a turntable, light bar, gold door roundels, dual rear wheels."""
    mb = MeshBuilder()
    RED, DK = "M_Door_Red", "M_Trim_Dark"
    zb, wr, R = 0.42, 0.55, 0.66
    fy, ry = -2.75, 2.35
    HW = 1.24
    cab = ([(-4.25, 0.55), (-4.15, zb)] + arch_pts(fy, wr, R, zb) +
           [(-1.72, zb), (-1.72, 2.95), (-3.86, 2.95), (-4.02, 2.82), (-4.25, 1.72)])
    xprism(mb, cab, -HW, HW, RED, side_mat=arch_side_mat([(fy, wr, R)], zb, body=RED, well=DK), bevel=0.07)
    body = [(-1.8, zb)] + arch_pts(ry, wr, R, zb) + [(4.35, zb), (4.42, 0.55), (4.42, 2.4), (4.3, 2.48), (-1.8, 2.48)]
    xprism(mb, body, -HW, HW, RED, side_mat=arch_side_mat([(ry, wr, R)], zb, body=RED, well=DK), bevel=0.06)
    bbox(mb, -0.85, -4.0, 0.3, 0.85, 4.3, zb + 0.06, DK)
    # glazing: windscreen + door windows
    slant_decal(mb, (-4.25, 1.72), (-4.02, 2.82), -1.06, 1.06, 0.1, 0.9, (-3.0, 1.6), "M_Glass", depth=0.01)
    for sx in (-1, 1):
        x = sx * (HW + 0.004)
        plate_decal(mb, [(x, -3.9, 1.85), (x, -2.25, 1.85), (x, -2.25, 2.68), (x, -3.75, 2.68)], (sx, 0, 0), 0.01,
                    "M_Glass")
        plate_decal(mb, [(x, -2.1, 1.85), (x, -1.85, 1.85), (x, -1.85, 2.68), (x, -2.1, 2.68)], (sx, 0, 0), 0.01,
                    "M_Glass")
        # white belt stripe (cab + body) and roll-up lockers
        plate_decal(mb, [(x, -4.2, 1.28), (x, 4.38, 1.28), (x, 4.38, 1.4), (x, -4.2, 1.4)], (sx, 0, 0), 0.01,
                    "M_Trim_White")
        for (y0, y1) in ((-1.55, -0.12), (0.0, 1.55), (3.12, 4.2)):
            plate_decal(mb, [(x, y0, 1.5), (x, y1, 1.5), (x, y1, 2.3), (x, y0, 2.3)], (sx, 0, 0), 0.012, "M_Metal")
            plate_decal(mb, [(x, y0, 0.62), (x, y1, 0.62), (x, y1, 1.2), (x, y0, 1.2)], (sx, 0, 0), 0.012, "M_Metal")
        # gold roundel on the cab door
        sub = MeshBuilder()
        sub.cylinder(0, 0, 0.0, 0.03, 0.2, "M_Awning_Yellow", seg=12, cap_top=True)
        mb.extend(sub, Matrix.Translation((sx * (HW - 0.005), -3.05, 1.58)) @ Matrix.Rotation(sx * R90, 4, "Y"))
        # mirrors
        bbox(mb, sx * (HW + 0.05) - 0.06, -3.98, 2.0, sx * (HW + 0.32) + 0.06, -3.9, 2.08, DK)
        bbox(mb, sx * (HW + 0.24), -4.02, 1.75, sx * (HW + 0.36), -3.88, 2.25, DK, bevel=0.02)
    # front: grille, headlights, bumper
    bbox(mb, -0.7, -4.29, 0.72, 0.7, -4.25, 1.5, "M_Metal_Dark")
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.82, sx * 1.12))
        bbox(mb, xa, -4.29, 1.05, xb, -4.25, 1.32, "M_Light_Emit")
        xa, xb = sorted((sx * 0.85, sx * 1.15))
        bbox(mb, xa, 4.42, 0.9, xb, 4.46, 1.2, "M_Awning_Red")
    bbox(mb, -1.3, -4.5, 0.42, 1.3, -4.22, 0.8, "M_Metal", bevel=0.05)
    bbox(mb, -1.2, 4.38, 0.42, 1.2, 4.6, 0.72, "M_Metal", bevel=0.04)
    # light bar
    bbox(mb, -1.0, -3.62, 2.95, 1.0, -3.28, 3.03, DK)
    bbox(mb, -0.98, -3.6, 3.03, -0.12, -3.3, 3.2, "M_Awning_Red", bevel=0.03)
    bbox(mb, 0.12, -3.6, 3.03, 0.98, -3.3, 3.2, "M_Awning_Red", bevel=0.03)
    bbox(mb, -0.12, -3.58, 3.03, 0.12, -3.32, 3.16, "M_Light_Emit")
    # aerial ladder: turntable + pedestal at the back, rest bracket over the cab
    mb.cylinder(0.0, 3.4, 2.46, 2.72, 0.85, "M_Metal_Dark", seg=12, cap_top=True)
    bbox(mb, -0.55, 2.8, 2.72, 0.55, 3.95, 3.12, RED, bevel=0.04)
    bbox(mb, -0.7, -2.95, 2.95, 0.7, -2.75, 3.12, "M_Metal_Dark")
    for sx in (-1, 1):
        bbox(mb, sx * 0.5 - 0.05, -3.15, 3.12, sx * 0.5 + 0.05, 4.65, 3.26, "M_Metal", bevel=0.015)
    y = -2.95
    while y < 4.5:
        bbox(mb, -0.46, y - 0.035, 3.15, 0.46, y + 0.035, 3.22, "M_Metal")
        y += 0.5
    # hose bed rails on the body roof
    for sx in (-1, 1):
        bbox(mb, sx * 1.1 - 0.04, -1.6, 2.48, sx * 1.1 + 0.04, 2.6, 2.62, "M_Metal")
    for sx in (-1, 1):
        wheel(mb, HW - 0.02, fy, wr, 0.38, sx)
        wheel(mb, HW, ry, wr, 0.52, sx)
    return mb


def school_bus():
    """Classic yellow school bus ~10.6 m (nose -Y, origin ground centre): bonnet, window band, black rub
    rails, SCHOOL BUS headers front and back, red/amber corner lights, stop arm, passenger door (+X side)."""
    mb = MeshBuilder()
    Y, DK = "M_Awning_Yellow", "M_Trim_Dark"
    zb, wr, R = 0.4, 0.5, 0.6
    fy, ry = -3.85, 2.85
    HW = 1.25
    prof = ([(-5.3, 0.5), (-5.2, zb)] + arch_pts(fy, wr, R, zb) + arch_pts(ry, wr, R, zb) +
            [(5.15, zb), (5.3, 0.55), (5.3, 2.8), (5.12, 3.0), (-3.3, 3.0), (-3.5, 2.86), (-3.62, 1.74),
             (-5.08, 1.56), (-5.3, 1.36)])
    xprism(mb, prof, -HW, HW, Y, side_mat=arch_side_mat([(fy, wr, R), (ry, wr, R)], zb, body=Y, well=DK), bevel=0.07)
    bbox(mb, -0.8, -5.0, 0.28, 0.8, 5.0, zb + 0.05, DK)
    slant_decal(mb, (-3.62, 1.74), (-3.5, 2.86), -1.12, 1.12, 0.06, 0.94, (0.0, 1.6), "M_Glass", depth=0.01)
    for sx in (-1, 1):
        x = sx * (HW + 0.004)
        for (z0, z1) in ((1.2, 1.28), (1.55, 1.63)):
            plate_decal(mb, [(x, -3.45, z0), (x, 5.2, z0), (x, 5.2, z1), (x, -3.45, z1)], (sx, 0, 0), 0.012, DK)
        ys = [-3.2 + 0.98 * k for k in range(9)]
        for k, y0 in enumerate(ys[:-1]):
            if sx > 0 and k == 0:
                continue
            plate_decal(mb, [(x, y0 + 0.08, 1.8), (x, y0 + 0.9, 1.8), (x, y0 + 0.9, 2.62), (x, y0 + 0.08, 2.62)],
                        (sx, 0, 0), 0.01, "M_Glass")
        bbox(mb, sx * (HW + 0.03) - 0.05, -3.75, 2.25, sx * (HW + 0.35) + 0.05, -3.67, 2.32, DK)
        bbox(mb, sx * (HW + 0.25), -3.8, 1.9, sx * (HW + 0.37), -3.62, 2.4, DK, bevel=0.02)
    # passenger door (+X side, front)
    x = HW + 0.004
    plate_decal(mb, [(x, -3.15, 0.55), (x, -2.3, 0.55), (x, -2.3, 2.66), (x, -3.15, 2.66)], (1, 0, 0), 0.012, DK)
    plate_decal(mb, [(x + 0.012, -3.08, 0.65), (x + 0.012, -2.76, 0.65), (x + 0.012, -2.76, 2.58),
                     (x + 0.012, -3.08, 2.58)], (1, 0, 0), 0.008, "M_Glass")
    plate_decal(mb, [(x + 0.012, -2.69, 0.65), (x + 0.012, -2.37, 0.65), (x + 0.012, -2.37, 2.58),
                     (x + 0.012, -2.69, 2.58)], (1, 0, 0), 0.008, "M_Glass")
    # stop arm (-X side)
    st = MeshBuilder()
    oct_ = [(0.32 * math.cos(math.pi / 8 + TAU * k / 8), 0.32 * math.sin(math.pi / 8 + TAU * k / 8)) for k in range(8)]
    st.prism(oct_, 0.0, 0.04, "M_Door_Red", "M_Sign_Face")
    mb.extend(st, Matrix.Translation((-HW - 0.005, -2.6, 2.0)) @ Matrix.Rotation(-R90, 4, "Y"))
    # headers + lettering front and back
    word = sign_text("SCHOOL BUS", 0.22, DK, max_w=1.45, depth=0.03)
    bbox(mb, -1.18, -3.42, 2.98, 1.18, -3.22, 3.36, Y, bevel=0.03)
    mb.extend(word, Matrix.Translation((0.0, -3.435, 3.17)))
    mb.extend(word, Matrix.Translation((0.0, 5.315, 2.55)) @ Matrix.Rotation(math.pi, 4, "Z"))
    for sx in (-1, 1):
        for (yy, ny) in ((-3.43, -1), (5.31, 1)):
            for k, mat in enumerate(("M_Hazard_Orange", "M_Door_Red")):
                xc = sx * (0.88 + 0.19 * k)
                if ny < 0:
                    bbox(mb, xc - 0.075, yy - 0.03, 3.05, xc + 0.075, yy + 0.02, 3.27, mat)
                else:
                    bbox(mb, xc - 0.075, yy - 0.01, 2.75, xc + 0.075, yy + 0.04, 2.95, mat)
    # nose: grille, headlights, bumpers; rear: emergency door seam + tail lights
    bbox(mb, -0.65, -5.33, 0.62, 0.65, -5.28, 1.3, "M_Metal_Dark")
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.78, sx * 1.08))
        bbox(mb, xa, -5.33, 1.0, xb, -5.27, 1.22, "M_Light_Emit")
        xa, xb = sorted((sx * 0.9, sx * 1.15))
        bbox(mb, xa, 5.29, 0.75, xb, 5.34, 1.05, "M_Door_Red")
    bbox(mb, -1.3, -5.5, 0.38, 1.3, -5.25, 0.68, DK, bevel=0.05)
    bbox(mb, -1.3, 5.22, 0.38, 1.3, 5.45, 0.66, DK, bevel=0.05)
    plate_decal(mb, [(-0.55, 5.304, 0.8), (0.55, 5.304, 0.8), (0.55, 5.304, 2.3), (-0.55, 5.304, 2.3)], (0, 1, 0),
                0.01, DK)
    plate_decal(mb, [(-0.45, 5.316, 1.55), (0.45, 5.316, 1.55), (0.45, 5.316, 2.2), (-0.45, 5.316, 2.2)], (0, 1, 0),
                0.008, "M_Glass")
    for sx in (-1, 1):
        wheel(mb, HW - 0.02, fy, wr, 0.3, sx)
        wheel(mb, HW, ry, wr, 0.42, sx)
    return mb


# =============================================================================== POLICE STATION
def _police(C_):
    S = C_.S
    BX, BY = -5.0, -5.0                  # station front-centre (entrance axis)
    colors = dict(wall="M_Wall_Brick", trim="M_Trim_White", door="M_Door_Navy", awning="M_Awning_Blue",
                  roof="M_Roof_Slate", sign="M_Door_Navy")
    spec = BuildingSpec("mixed", 6, 4, 2, colors, roof="flat", ground_h=H4,
                        feats=dict(door_i=2, style="pair", awning=None, ac_units=3, roof_access=True),
                        seed=9101, exposed={"left": True, "right": True}, district="civic")
    root = C_.building("Station", spec, BX, BY)
    # civic ground floor: tall windows + centred glass double door (storefront door pair)
    for i in (0, 1, 4, 5):
        C_.swap(root, spec, "front", 0, i, "Wall_Window_H4", plinth="Plinth_3m")
    C_.swap(root, spec, "front", 0, 3, "Wall_StorefrontDoorL_H4")
    for i in (0, 1):
        C_.swap(root, spec, "left", 0, i, "Wall_Window_H4", plinth="Plinth_3m")
    C_.swap(root, spec, "right", 0, 0, "Wall_Window_H4", plinth="Plinth_3m")
    C_.swap(root, spec, "right", 0, 1, "Wall_Window_H4", plinth="Plinth_3m")
    C_.swap(root, spec, "right", 0, 2, "Wall_RollerDoor_H4", plinth="")          # sally port
    C_.swap(root, spec, "right", 0, 3, "Wall_Door_H4", plinth="Plinth_Door_3m")
    drop(kids(root, "Sign_Board_3m"))

    # ---- portico with the POLICE fascia + blue lamps (facade frame of the entrance axis)
    pm = MeshBuilder()
    for sx in (-1, 1):
        x = sx * 3.05
        bbox(pm, x - 0.4, -2.78, -0.02, x + 0.4, -1.98, 0.45, "M_Wall_Concrete", bevel=0.04)
        bbox(pm, x - 0.27, -2.65, 0.45, x + 0.27, -2.11, 3.25, "M_Wall_Concrete", bevel=0.03)
        bbox(pm, x - 0.35, -2.73, 3.15, x + 0.35, -2.03, 3.3, "M_Trim_White", bevel=0.02)
    bbox(pm, -3.72, -2.98, 3.3, 3.72, -0.16, 4.1, "M_Door_Navy", bevel=0.03)
    bbox(pm, -3.8, -3.06, 4.1, 3.8, -0.16, 4.24, "M_Trim_White", bevel=0.02)
    pm.box(-3.76, -3.02, 3.24, 3.76, -0.16, 3.32, "M_Trim_White", skip=("+y",))
    pm.extend(sign_text("POLICE", 0.56, "M_Sign_Face", max_w=6.2, depth=0.05), Matrix.Translation((0, -3.005, 3.72)))
    C_.mesh("Portico", pm, BX, BY, Z_LOT, grp="Station")
    lamp = C_.shared("BlueLamp", blue_lamp)
    for sx in (-1, 1):
        C_.inst(lamp, f"BlueLamp_{'W' if sx > 0 else 'E'}", BX + sx * 3.05, BY - 2.65, Z_LOT + 2.75, grp="Station")

    # ---- ground: forecourt, entry strip, lot, back yard, kerb connectors
    LX0, LX1 = 4.6, 14.85
    C_.pave("Forecourt", [(-14.9, -11.95), (LX0, -11.95), (LX0, BY), (-14.9, BY)], "M_Concrete")
    C_.pave("EntryWalk", [(-8.9, -11.95), (-1.1, -11.95), (-1.1, BY - 0.02), (-8.9, BY - 0.02)], "M_Plaza",
            z=Z_LOT + 0.01, skirt=0.05)
    C_.pave("Lot", [(LX0, -11.95), (LX1, -11.95), (LX1, 11.85), (LX0, 11.85)], "M_Asphalt")
    C_.pave("BackYard", [(-14.9, 7.0), (LX0, 7.0), (LX0, 11.85), (-14.9, 11.85)], "M_Gravel", z=0.02, skirt=0.12)
    C_.connector("FrontApron", -14.9, LX0, -11.8, "M_Concrete")
    C_.connector("LotMouth", LX0, LX1, -11.8, "M_Asphalt")
    paint = MeshBuilder()
    for k in range(8):
        y = -9.35 + 2.7 * k
        paint_line(paint, (9.85, y), (14.7, y), 0.12, Z_LOT + 0.008, "M_RoadLine_White")
    paint_line(paint, (5.4, -11.6), (5.4, 11.4), 0.12, Z_LOT + 0.008, "M_RoadLine_Yellow")
    for k in range(5):                     # hatched no-parking box in front of the sally port
        y = 0.9 + k * 0.7
        paint_line(paint, (5.9, y), (6.9, y + 0.6), 0.1, Z_LOT + 0.008, "M_RoadLine_Yellow")
    paint_rect(paint, 5.75, 0.6, 9.4, 4.4, 0.12, Z_LOT + 0.008, "M_RoadLine_Yellow")
    C_.mesh("Lot_Paint", paint, grp="Lot")

    # ---- vehicles: animal control van (street end), three cruisers, two staff cars
    car_rot = -R90                                 # noses toward the aisle (-X)
    cop = C_.shared("PoliceLivery", police_livery, smooth=40)
    van = C_.put("Car_Van", 12.3, -8.0, Z_LOT, car_rot, grp="Lot", recolor={"awning": "M_Zoo_Accent"},
                 name="AnimalControlVan")
    if van is not None:
        van["gameplay"] = "animal_control_van"
        C_.inst(C_.shared("AnimalControlLivery", animal_control_livery, smooth=40), "AnimalControlVan_Livery",
                12.3, -8.0, Z_LOT, car_rot, grp="Lot")
    for k, y in enumerate((-5.3, -2.6, 0.1)):
        C_.put("Car_Sedan", 12.3, y, Z_LOT, car_rot + (0.02 if k == 1 else 0.0), grp="Lot",
               recolor={"awning": "M_Wall_White"}, name=f"PoliceCar_{k + 1}")
        C_.inst(cop, f"PoliceCar_{k + 1}_Livery", 12.3, y, Z_LOT, car_rot + (0.02 if k == 1 else 0.0), grp="Lot")
    C_.put("Car_Sedan", 12.3, 5.5, Z_LOT, car_rot, grp="Lot", recolor={"awning": "M_Wall_Slate"}, name="StaffCar_1")
    C_.put("Car_Sedan", 12.3, 8.2, Z_LOT, car_rot - 0.03, grp="Lot", recolor={"awning": "M_Awning_Green"},
           name="StaffCar_2")
    C_.put("StreetLight", 14.45, 2.9, Z_LOT, -R90, grp="Lot")

    # ---- forecourt dressing
    C_.flag(-12.6, -9.4, Z_LOT, "M_Awning_Blue")
    for x in [-13.8 + 1.75 * k for k in range(11)]:
        C_.put("Bollard", x, -11.35, Z_LOT, grp="Forecourt")
    C_.put("Planter", -11.2, -5.9, Z_LOT, recolor={"trim": "M_Door_Navy"}, grp="Forecourt")
    C_.put("Planter", 1.2, -5.9, Z_LOT, recolor={"trim": "M_Door_Navy"}, grp="Forecourt")
    C_.put("Bench", -12.9, -6.1, Z_LOT, 0.0, grp="Forecourt")
    C_.put("Bench", 2.9, -6.1, Z_LOT, 0.0, grp="Forecourt")
    C_.put("TrashBin", -9.7, -6.0, Z_LOT, grp="Forecourt")
    C_.put("BikeRack", 1.3, -9.4, Z_LOT, 0.0, grp="Forecourt")
    C_.put("Mailbox", 3.7, -10.6, Z_LOT, 0.0, grp="Forecourt")
    C_.put("Tree_Small", -14.1, -9.0, Z_LOT, grp="Forecourt")

    # ---- back yard: animal-control holding pen, dumpster, AC units
    pen = Fence(S, "Fence_Chain_3m", sub=C_.g("Yard"), z=0.02)
    pen.line([(-6.4, 7.7), (-14.4, 7.7), (-14.4, 11.6), (-6.4, 11.6), (-6.4, 7.7)], gates=[(3, 0.5, None, 1.6)])
    C_.put("Doghouse", -12.6, 10.4, 0.02, 0.2, grp="Yard", recolor={"wall": "M_Zoo_Accent", "roof": "M_Zoo_Primary",
                                                                    "trim": "M_Trim_White", "sign": "M_Zoo_Primary"})
    C_.put("Doghouse", -10.3, 10.6, 0.02, -0.15, grp="Yard",
           recolor={"wall": "M_Wall_Sky", "roof": "M_Door_Navy", "trim": "M_Trim_White", "sign": "M_Door_Navy"})
    C_.put("CrateStack", -8.0, 10.6, 0.02, 0.1, grp="Yard")
    C_.put("Crate", -13.3, 8.5, 0.02, 0.4, grp="Yard")
    C_.put("Dumpster", -3.4, 10.7, 0.02, 0.0, grp="Yard")
    C_.put("TrashBin", -1.6, 10.9, 0.02, grp="Yard")
    C_.put("Roof_AC_Unit", 1.2, 8.0, 0.02, 0.0, grp="Yard")
    C_.put("Roof_AC_Unit", 2.6, 8.0, 0.02, 0.0, grp="Yard")
    # rooftop radio mast (back-right corner) - reads as "police" among taller neighbours
    C_.mesh("RadioMast", radio_mast(), BX + spec.W / 2 - 1.3, BY + spec.D - 1.3, Z_LOT + spec.wall_top() + 0.2,
            grp="Station")
    anchor(C_, "AnimalControl", 9.3, -8.0, Z_LOT, "animal_control", note="animal control van / impound drop-off")
    anchor(C_, "HoldingPen", -10.4, 9.6, 0.02, "holding_pen", note="captured animals held by animal control")
    anchor(C_, "Entrance", BX, BY - 3.6, Z_LOT, "civic_entrance", building="police_station")
    return dict(station=root.name)


# =============================================================================== FIRE STATION
def bay_door():
    """Classic red sectional bay door overlay for KIT_Wall_RollerDoor_H4 (module frame: sits inside the
    reveal in front of the roller curtain at y 0.22): window row, white panel grooves."""
    mb = MeshBuilder()
    y = 0.12
    mb.box(-1.27, y, 0.13, 1.27, 0.21, 3.37, "M_Awning_Red", skip=("+y", "-z"))
    for z in (0.95, 1.7):
        mb.box(-1.2, y - 0.012, z - 0.025, 1.2, y, z + 0.025, "M_Trim_White", skip=("+y",))
    mb.box(-1.2, y - 0.012, 2.95, 1.2, y, 3.0, "M_Trim_White", skip=("+y",))
    for k in range(4):
        x0 = -1.12 + k * 0.57
        mb.box(x0, y - 0.015, 2.22, x0 + 0.47, y, 2.72, "M_Trim_White", skip=("+y",))
        mb.box(x0 + 0.04, y - 0.02, 2.26, x0 + 0.43, y - 0.015, 2.68, "M_Glass", skip=("+y", "-z", "+z", "-x", "+x"))
    return mb


def _fire(C_):
    S = C_.S
    BX, BY = -3.5, -3.5
    colors = dict(wall="M_Wall_Brick", trim="M_Trim_White", door="M_Door_Red", awning="M_Awning_Red",
                  roof="M_Roof_Charcoal", sign="M_Awning_Red")
    spec = BuildingSpec("commercial", 5, 5, 2, colors, roof="flat", ground_h=H4,
                        feats=dict(door_i=3, style="single", awning=None, ac_units=2), seed=9201,
                        exposed={"left": True, "right": True}, district="civic")
    root = C_.building("Station", spec, BX, BY)
    bays = (0, 1, 2)
    for i in bays:
        C_.swap(root, spec, "front", 0, i, "Wall_RollerDoor_H4")
    C_.swap(root, spec, "front", 0, 3, "Wall_Door_H4")
    C_.swap(root, spec, "front", 0, 4, "Wall_Window_H4")
    for side in ("left", "right"):
        for i in (0, 1):
            C_.swap(root, spec, side, 0, i, "Wall_Window_H4")
    drop(kids(root, "Sign_Board_3m"))
    W = spec.W
    door = C_.shared("FireBayDoor", bay_door)
    for i in bays:
        bx = -W / 2 + 1.5 + 3.0 * i
        C_.inst(door, f"BayDoor_{i + 1}", BX + bx, BY, Z_LOT, grp="Station")
    # white piers between / beside the bays
    piers = MeshBuilder()
    for bx in (-4.5, -1.5, 1.5):            # module joints between / beside the bays
        bbox(piers, bx - 0.16, -0.12, 0.0, bx + 0.16, 0.02, 3.98, "M_Trim_White", bevel=0.02)
    C_.mesh("BayPiers", piers, BX, BY, Z_LOT, grp="Station")

    # ---- stepped false front with FIRE DEPT over the bays
    top = spec.wall_top()
    cx = -W / 2 + 1.5 + 3.0      # centre of the 3 bays (building frame)
    ff = MeshBuilder()
    w0, w1 = 4.4, 2.1
    prof = [(-w0, 0.0), (w0, 0.0), (w0, 1.15), (w1, 1.15), (w1, 1.85), (-w1, 1.85), (-w1, 1.15), (-w0, 1.15)]
    extrude_xz(ff, prof, -0.14, 0.42, "M_Wall_Brick")
    for (xa, xb, z) in ((-w0 - 0.07, -w1, 1.15), (w1, w0 + 0.07, 1.15), (-w1 - 0.07, w1 + 0.07, 1.85)):
        bbox(ff, xa, -0.21, z, xb, 0.49, z + 0.13, "M_Trim_White", bevel=0.02)
    for sx in (-1, 1):
        bbox(ff, sx * w1 - 0.07, -0.21, 1.15, sx * w1 + 0.07, 0.49, 1.98, "M_Trim_White", bevel=0.02)
    bbox(ff, -3.7, -0.25, 0.14, 3.7, -0.1, 1.0, "M_Sign_Face", bevel=0.02)
    ff.extend(sign_text("FIRE DEPT", 0.62, "M_Awning_Red", max_w=6.8, depth=0.05), Matrix.Translation((0, -0.275, 0.57)))
    disc_y(ff, 0.0, -0.18, 1.5, 0.3, 0.06, "M_Sign_Face", seg=16, side="M_Trim_White")
    ff.extend(sign_text("1", 0.4, "M_Awning_Red", depth=0.03), Matrix.Translation((0, -0.195, 1.5)))
    C_.mesh("FalseFront_Sign", ff, BX + cx, BY, Z_LOT + top, grp="Station")

    # ---- hose tower (kit, 5 storeys) + custom hip cap
    tspec = BuildingSpec("apartment", 1, 1, 5, dict(colors), roof="flat", ground_h=H3,
                         feats=dict(door_i=0, style="single", ac_units=0), seed=9202,
                         exposed={"left": True, "right": True, "back": True}, district="civic")
    TX, TY = BX + W / 2 + 1.4, 6.6
    C_.building("HoseTower", tspec, TX, TY)
    ttop = Z_LOT + tspec.wall_top() + 0.8
    cap = MeshBuilder()
    bbox(cap, -1.85, -1.85 + 1.5, 0.0, 1.85, 1.85 + 1.5, 0.22, "M_Trim_White", bevel=0.03)
    lathe(cap, [(2.45, 0.22), (2.45, 0.3), (0.0, 2.45)], "M_Roof_Charcoal", seg=4, cx=0.0, cy=1.5, phase=math.pi / 4)
    cap.cylinder(0.0, 1.5, 2.3, 3.0, 0.035, "M_Metal_Dark", seg=6)
    cap.sphere(0.0, 1.5, 3.05, 0.12, "M_Awning_Yellow", seg=8, rings=4)
    C_.mesh("HoseTower_Cap", cap, TX, TY, ttop - 0.08, grp="Station")

    # ---- apron, side lot, paint, kerb connector
    C_.pave("Apron", [(-11.95, -12.95), (4.3, -12.95), (4.3, BY), (-11.95, BY)], "M_Concrete")
    C_.pave("SideLot", [(4.3, -12.95), (11.95, -12.95), (11.95, 5.0), (4.3, 5.0)], "M_Asphalt")
    C_.pave("BackStrip", [(-11.95, BY + spec.D), (4.3, BY + spec.D), (4.3, 12.95), (-11.95, 12.95)], "M_Gravel",
            z=0.02, skirt=0.12)
    C_.connector("ApronMouth", -11.95, 11.95, -12.85, "M_Concrete")
    paint = MeshBuilder()
    for bx in (-7.5, -4.5, -1.5, 1.5):
        x = BX + bx
        paint_line(paint, (x, BY - 0.4), (x, -11.6), 0.14, Z_LOT + 0.008, "M_RoadLine_Yellow")
    for k in range(6):
        x = -10.6 + k * 1.6
        paint_line(paint, (x, -12.5), (x + 0.9, -11.7), 0.14, Z_LOT + 0.008, "M_Awning_Red")
    paint_line(paint, (-11.0, -11.65), (-1.8, -11.65), 0.14, Z_LOT + 0.008, "M_Awning_Red")
    for k in range(3):                       # two side-lot stalls against the back of the lot
        x = 4.75 + k * 2.7
        paint_line(paint, (x, -0.2), (x, 4.8), 0.12, Z_LOT + 0.008, "M_RoadLine_White")
    C_.mesh("Apron_Paint", paint, grp="Apron")

    # ---- fire engine nosing out of the middle bay
    eng = C_.shared("FireEngine", fire_engine, smooth=40)
    C_.inst(eng, "FireEngine", BX - 3.0, BY - 0.55 - 4.6, Z_LOT, 0.0, grp="Apron")
    C_.put("Hydrant", -11.3, -12.2, Z_LOT, 0.4, grp="Apron")
    C_.put("Hydrant", 4.9, -12.3, Z_LOT, -0.3, grp="Apron")
    C_.flag(3.6, -11.6, Z_LOT, "M_Awning_Red", grp="Apron")
    C_.put("Bench", BX + 6.0, BY - 0.7, Z_LOT, 0.0, grp="Apron")
    C_.put("Planter", BX + 4.4, BY - 0.6, Z_LOT, recolor={"trim": "M_Awning_Red"}, grp="Apron")
    C_.put("TrafficCone", -0.6, -10.4, Z_LOT, 0.0, grp="Apron")
    C_.put("TrafficCone", -0.2, -11.2, Z_LOT, 0.0, grp="Apron")
    # side lot: chief's car, crew car, trees
    C_.put("Car_Sedan", 6.1, 2.4, Z_LOT, 0.0, grp="SideLot", recolor={"awning": "M_Door_Red"}, name="ChiefCar")
    C_.put("Car_Sedan", 8.8, 2.5, Z_LOT, 0.03, grp="SideLot", recolor={"awning": "M_Wall_Sky"}, name="CrewCar")
    C_.put("Tree_Round_A", 10.6, 9.8, None, 0.5, grp="SideLot")
    C_.put("Tree_Cone", 10.8, 6.6, None, 0.0, grp="SideLot")
    C_.put("Bush_B", 8.9, 11.6, None, 1.0, grp="SideLot")
    C_.put("Dumpster", -9.5, 12.0, 0.02, math.pi, grp="SideLot")
    anchor(C_, "Engine", BX - 3.0, BY - 5.15, Z_LOT, "fire_engine", note="engine nosing out of the middle bay")
    anchor(C_, "Entrance", BX + 3.0, BY - 1.2, Z_LOT, "civic_entrance", building="fire_station")
    return dict(station=root.name)


# =============================================================================== SCHOOL
def cupola():
    """White bell cupola straddling a gable ridge (origin = ridge point), clock on the front, copper roof."""
    mb = MeshBuilder()
    bbox(mb, -1.0, -1.0, -0.75, 1.0, 1.0, 1.0, "M_Wall_White", bevel=0.03)
    bbox(mb, -1.08, -1.08, 1.0, 1.08, 1.08, 1.15, "M_Trim_White", bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.85, sy * 0.85
            bbox(mb, x - 0.12, y - 0.12, 1.15, x + 0.12, y + 0.12, 2.35, "M_Trim_White", bevel=0.02)
    bbox(mb, -0.6, -0.6, 1.15, 0.6, 0.6, 2.3, "M_Trim_Dark")
    lathe(mb, [(0.0, 1.45), (0.3, 1.53), (0.36, 1.95), (0.18, 2.17), (0.0, 2.21)], "M_Awning_Yellow", seg=8)
    bbox(mb, -1.1, -1.1, 2.35, 1.1, 1.1, 2.55, "M_Trim_White", bevel=0.02)
    lathe(mb, [(1.62, 2.55), (1.62, 2.62), (0.0, 3.7)], "M_Roof_Green", seg=4, phase=math.pi / 4)
    mb.cylinder(0, 0, 3.6, 4.3, 0.035, "M_Metal_Dark", seg=6)
    mb.sphere(0, 0, 4.35, 0.11, "M_Awning_Yellow", seg=8, rings=4)
    clock_face(mb, 0.0, -1.03, 0.52, 0.42)
    return mb


def monument_sign(lines, w=4.4):
    mb = MeshBuilder()
    bbox(mb, -w / 2 - 0.15, -0.4, -0.1, w / 2 + 0.15, 0.4, 0.5, "M_Wall_Brick", bevel=0.04)
    bbox(mb, -w / 2 - 0.22, -0.47, 0.5, w / 2 + 0.22, 0.47, 0.6, "M_Trim_White", bevel=0.02)
    bbox(mb, -w / 2, -0.18, 0.6, w / 2, 0.18, 1.85, "M_Sign_Face", bevel=0.03)
    bbox(mb, -w / 2 - 0.08, -0.24, 1.85, w / 2 + 0.08, 0.24, 1.97, "M_Trim_White", bevel=0.02)
    for side in (0, 1):
        for txt, h, z, mat in lines:
            t = sign_text(txt, h, mat, max_w=w - 0.4, depth=0.03)
            M = Matrix.Translation((0, -0.195, z))
            if side:
                M = Matrix.Rotation(math.pi, 4, "Z") @ M
            mb.extend(t, M)
    return mb


def _school(C_):
    S = C_.S
    colors = dict(wall="M_Wall_Brick", trim="M_Trim_White", door="M_Door_Navy", awning="M_Awning_Blue",
                  roof="M_Roof_Slate", sign="M_Awning_Blue")
    MY = -12.0
    cspec = BuildingSpec("apartment", 4, 5, 3, dict(colors), roof="gable_front", ground_h=H3,
                         feats=dict(door_i=1, style="wide"), seed=9301,
                         exposed={"left": True, "right": True, "back": True}, district="civic")
    root = C_.building("Main", cspec, 0.0, MY)
    C_.swap(root, cspec, "front", 0, 2, "Wall_DoorGlass_H3")
    drop(kids(root, "Canopy_Door"))
    wings = {}
    WY = -9.0
    for nm, cxw, di, ex in (("WingW", -13.4, 0, "left"), ("WingE", 13.4, 4, "right")):
        ws = BuildingSpec("apartment", 5, 4, 2, dict(colors), roof="flat", ground_h=H3,
                          feats=dict(door_i=di, style="wide", ac_units=2), seed=9302 + di,
                          exposed={ex: True, "back": True}, district="civic")
        wings[nm] = C_.building(nm, ws, cxw, WY)
    # entrance canopy over the double door
    ca = MeshBuilder()
    bbox(ca, -3.3, -1.75, 2.8, 3.3, -0.16, 3.05, "M_Trim_White", bevel=0.03)
    bbox(ca, -3.25, -1.7, 2.76, 3.25, -0.2, 2.8, "M_Door_Navy")
    for sx in (-1, 1):
        bbox(ca, sx * 3.05 - 0.1, -1.6, 0.0, sx * 3.05 + 0.1, -1.4, 2.8, "M_Trim_White", bevel=0.02)
    C_.mesh("EntranceCanopy", ca, 0.0, MY, Z_LOT, grp="Main")
    # SCHOOL panel in the front pediment
    top = cspec.wall_top()
    pd = MeshBuilder()
    bbox(pd, -2.35, -0.26, 0.2, 2.35, -0.12, 1.0, "M_Sign_Face", bevel=0.02)
    pd.extend(sign_text("SCHOOL", 0.56, "M_Door_Navy", max_w=4.2, depth=0.04), Matrix.Translation((0, -0.28, 0.6)))
    C_.mesh("Pediment_Sign", pd, 0.0, MY, Z_LOT + top, grp="Main")
    ridge = top + 2.25
    r = K.REG.get("KIT_Roof_Gable_S12_Mid")
    if r:
        ridge = top + r["dims"]["z"][1]
    C_.mesh("Cupola", cupola(), 0.0, MY + cspec.D / 2, Z_LOT + ridge - 0.05, grp="Main")

    # ---- front: plaza walk, bus bay, staff lot, lawns
    C_.pave("Plaza", [(-4.6, -19.95), (4.6, -19.95), (4.6, MY - 0.02), (-4.6, MY - 0.02)], "M_Plaza")
    C_.pave("BusBay", [(-23.6, -19.95), (-5.4, -19.95), (-5.4, -16.3), (-23.6, -16.3)], "M_Asphalt")
    C_.pave("StaffLot", [(6.0, -19.95), (24.0, -19.95), (24.0, -13.8), (6.0, -13.8)], "M_Asphalt")
    C_.connector("PlazaMouth", -4.6, 4.6, -19.8, "M_Plaza")
    C_.connector("BusBayMouth", -23.6, -5.4, -19.8, "M_Asphalt")
    C_.connector("StaffLotMouth", 6.0, 24.0, -19.8, "M_Asphalt")
    paint = MeshBuilder()
    paint_rect(paint, -22.8, -19.4, -6.2, -16.85, 0.15, Z_LOT + 0.008, "M_RoadLine_Yellow")
    for k in range(7):
        x = 7.2 + 2.7 * k
        paint_line(paint, (x, -19.4), (x, -14.4), 0.12, Z_LOT + 0.008, "M_RoadLine_White")
    C_.mesh("Front_Paint", paint, grp="Front")
    bus = C_.shared("SchoolBus", school_bus, smooth=40)
    o = C_.inst(bus, "SchoolBus", -14.6, -18.1, Z_LOT, R90, grp="Front")
    o["gameplay"] = "school_bus"
    for k, col in ((0, "M_Wall_Sky"), (1, "M_Wall_White"), (3, "M_Awning_Green"), (4, "M_Trim_Dark")):
        C_.put("Car_Sedan", 8.55 + 2.7 * k, -16.9, Z_LOT, math.pi + (0.03 if k % 2 else -0.02), grp="Front",
               recolor={"awning": col}, name=f"StaffCar_{k + 1}")
    C_.flag(-3.7, -17.6, Z_LOT, "M_Awning_Blue", grp="Front")
    ms = monument_sign([("WILLOWBROOK", 0.36, 1.48, "M_Door_Navy"), ("SCHOOL", 0.42, 0.98, "M_Wall_Brick")])
    C_.mesh("MonumentSign", ms, 2.9, -18.7, Z_LOT, grp="Front")
    for y in (-14.6, -16.8):
        C_.put("BikeRack", -3.9, y, Z_LOT, R90, grp="Front")
    C_.put("Bench", 3.9, -15.0, Z_LOT, -R90, grp="Front")
    C_.put("TrashBin", 3.95, -16.5, Z_LOT, grp="Front")
    for x in (-19.4, -16.4, -13.4, -10.4, -7.4):
        C_.put("Hedge_3m", x, WY - 1.0, None, 0.0, grp="Front")
    for x in (7.4, 10.4, 13.4, 16.4, 19.4):
        C_.put("Hedge_3m", x, WY - 1.0, None, 0.0, grp="Front")
    for (x, y, t, r) in ((-20.4, -12.7, "Tree_Round_B", 0.3), (-10.2, -13.3, "Tree_Round_A", 1.2),
                         (11.8, -11.8, "Tree_Round_A", 2.2), (21.6, -11.6, "Tree_Round_A", 0.7),
                         (-23.2, -3.0, "Tree_Cone", 0.0), (-23.4, 1.6, "Tree_Small", 0.4),
                         (23.2, -4.5, "Tree_Small", 0.0), (23.3, 0.5, "Tree_Cone", 1.0)):
        C_.put(t, x, y, None, r, grp="Front")
    C_.put("Flowerbed_2m", -6.0, -13.6, None, R90, grp="Front")
    C_.put("Flowerbed_2m", 5.3, -13.4, None, R90, grp="Front", recolor={"foliage": "M_Foliage_Light"})

    # ---- back: basketball court (west) and playground (east)
    cx0, cx1, cy0, cy1 = -24.3, -6.5, 6.3, 19.5
    C_.pave("Court", [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)], "M_Asphalt_Alley", z=0.06, skirt=0.15)
    lines = MeshBuilder()
    zl = 0.068
    lx0, lx1, ly0, ly1 = cx0 + 0.9, cx1 - 0.9, cy0 + 0.8, cy1 - 0.8
    paint_rect(lines, lx0, ly0, lx1, ly1, 0.1, zl, "M_RoadLine_White")
    mx, my = (lx0 + lx1) / 2, (ly0 + ly1) / 2
    paint_line(lines, (mx, ly0), (mx, ly1), 0.1, zl, "M_RoadLine_White")
    paint_ring(lines, (mx, my), 1.6, 0.1, zl, "M_RoadLine_White", n=24)
    for sgn, xe in ((1, lx0), (-1, lx1)):
        kx = xe + sgn * 4.6
        xa, xb = sorted((xe, kx))
        flat_poly(lines, [(xa, my - 1.8), (xb, my - 1.8), (xb, my + 1.8), (xa, my + 1.8)], zl - 0.002, "M_Awning_Red")
        paint_rect(lines, xa, my - 1.8, xb, my + 1.8, 0.1, zl, "M_RoadLine_White")
        a0 = -R90 if sgn > 0 else R90
        paint_ring(lines, (kx, my), 1.8, 0.1, zl, "M_RoadLine_White", a0=a0, a1=a0 + math.pi, n=12)
        paint_ring(lines, (xe + sgn * 1.4, my), 5.4, 0.1, zl, "M_RoadLine_White", a0=a0 + 0.2, a1=a0 + math.pi - 0.2,
                   n=18)
    C_.mesh("Court_Lines", lines, grp="Court")
    hp = C_.shared("Hoop", hoop)
    C_.inst(hp, "Hoop_W", lx0 + 0.2, my, 0.06, R90, grp="Court")
    C_.inst(hp, "Hoop_E", lx1 - 0.2, my, 0.06, -R90, grp="Court")
    Fence(S, "Fence_Chain_3m", sub=C_.g("Court"), z=0.06).line(
        [(cx1, cy0 + 2.6), (cx1, cy0), (cx0, cy0), (cx0, cy1), (cx1, cy1), (cx1, cy0 + 4.4)])
    # playground on sand
    sand = MeshBuilder()
    pts = [(3.2, 6.6), (24.4, 6.6), (24.4, 19.6), (3.2, 19.6)]
    flat_poly(sand, pts, 0.0, "M_Sand")
    sand.wall(G.ensure_ccw([Vector(p) for p in pts]), -0.1, 0.0, "M_Sand", closed=True)
    border = MeshBuilder()
    P = G.ensure_ccw([Vector(p) for p in pts])
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        d = (b - a).normalized()
        n = Vector((d.y, -d.x))
        q0, q1 = a - d * 0.15, b + d * 0.15
        bbox_pts = [q0, q1, q1 - n * 0.15, q0 - n * 0.15]
        sub = MeshBuilder()
        sub.prism(bbox_pts, -0.05, 0.12, "M_Wood_Light", "M_Wood_Light")
        border.extend(sub)
    sand.extend(border)
    C_.mesh("Playground_Sand", sand, grp="Playground")
    C_.mesh("PlayTower", play_tower(), 12.0, 14.0, 0.0, 0.0, grp="Playground")
    C_.mesh("Seesaw", seesaw(), 6.6, 16.6, 0.0, 0.0, grp="Playground")
    C_.mesh("MerryGoRound", merry_go_round(), 7.2, 10.4, 0.0, 0.0, grp="Playground")
    C_.mesh("SpringRider_A", spring_rider(), 16.4, 8.6, 0.0, 0.4, grp="Playground")
    C_.mesh("SpringRider_B", spring_rider("M_Awning_Blue", "M_Awning_Red"), 17.6, 17.2, 0.0, -2.6, grp="Playground")
    C_.put("Swing", 20.6, 9.4, 0.0, R90, grp="Playground", recolor={"awning": "M_Awning_Blue"})
    C_.put("Swing", 20.6, 13.6, 0.0, R90, grp="Playground", recolor={"awning": "M_Awning_Red"})
    C_.put("Bench", 4.0, 10.6, 0.0, R90, grp="Playground")
    C_.put("Bench", 16.0, 18.9, 0.0, 0.0, grp="Playground")
    for (x, y, r) in ((-2.2, 10.8, 0.1), (-1.6, 15.6, -0.15)):
        C_.put("PicnicTable", x, y, None, r, grp="Playground")
    for (x, y, t, r) in ((-4.2, 18.8, "Tree_Round_A", 0.4), (1.4, 17.3, "Tree_Round_B", 0.0), (23.4, 16.6, "Tree_Round_A", 1.0),
                         (23.6, 19.4, "Tree_Cone", 0.0), (-2.6, 7.0, "Bush_B", 0.3), (2.5, 7.2, "Bush_A", 1.1)):
        C_.put(t, x, y, None, r, grp="Playground")
    anchor(C_, "Playground", 13.0, 12.5, 0.0, "playground", note="open sand play area (round-ups)")
    anchor(C_, "Court", -15.4, 12.9, 0.06, "sports_court")
    anchor(C_, "BusStop", -14.6, -15.6, Z_LOT, "school_bus")
    anchor(C_, "Entrance", 0.0, MY - 2.4, Z_LOT, "civic_entrance", building="school")
    return dict(main=root.name)


# =============================================================================== CHURCH
def belfry_spire():
    """Open belfry (louvred), cornice, white octagonal spire, gilded ball + weathervane. Origin = tower roof
    centre (inside the parapet)."""
    mb = MeshBuilder()
    W = "M_Wall_White"
    bbox(mb, -1.1, -1.1, 0.0, 1.1, 1.1, 0.4, W, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.88, sy * 0.88
            bbox(mb, x - 0.2, y - 0.2, 0.4, x + 0.2, y + 0.2, 2.75, "M_Trim_White", bevel=0.03)
    bbox(mb, -0.72, -0.72, 0.4, 0.72, 0.72, 2.75, "M_Trim_Dark")
    for k in range(5):                        # tilted louvre boards in every opening
        z = 0.78 + k * 0.4
        for ax in range(4):
            sub = MeshBuilder()
            sub.box(-0.68, -0.02, -0.17, 0.68, 0.02, 0.17, W)
            M = Matrix.Rotation(ax * R90, 4, "Z") @ Matrix.Translation((0, -0.78, z)) @ Matrix.Rotation(-0.6, 4, "X")
            mb.extend(sub, M)
    # lintel + cornice
    bbox(mb, -1.12, -1.12, 2.75, 1.12, 1.12, 3.15, W, bevel=0.03)
    bbox(mb, -1.26, -1.26, 3.15, 1.26, 1.26, 3.32, "M_Trim_White", bevel=0.03)
    # octagonal lantern drum + white spire (one surface of revolution, closed to the apex)
    lathe(mb, [(0.95, 3.3), (0.95, 3.95), (1.08, 4.0), (1.08, 4.12), (0.98, 4.14), (0.0, 11.4)], W, seg=8,
          phase=math.pi / 8)
    mb.sphere(0, 0, 11.45, 0.2, "M_Awning_Yellow", seg=10, rings=5)
    mb.cylinder(0, 0, 11.6, 12.6, 0.03, "M_Trim_Dark", seg=6)
    vane = MeshBuilder()
    vane.box(-0.75, -0.02, -0.03, 0.75, 0.02, 0.03, "M_Trim_Dark")
    tail = MeshBuilder()
    extrude_xz(tail, [(-0.95, -0.22), (-0.6, -0.05), (-0.6, 0.05), (-0.95, 0.22)], -0.02, 0.02, "M_Trim_Dark")
    extrude_xz(tail, [(0.6, -0.12), (0.98, 0.0), (0.6, 0.12)], -0.02, 0.02, "M_Trim_Dark")
    vane.extend(tail)
    mb.extend(vane, Matrix.Translation((0, 0, 12.3)) @ Matrix.Rotation(0.5, 4, "Z"))
    for ax in range(4):
        sub = MeshBuilder()
        sub.box(-0.015, -0.4, -0.015, 0.015, 0.0, 0.015, "M_Trim_Dark")
        mb.extend(sub, Matrix.Translation((0, 0, 12.0)) @ Matrix.Rotation(ax * R90, 4, "Z"))
    return mb


def notice_board():
    mb = MeshBuilder()
    for sx in (-1, 1):
        bbox(mb, sx * 1.15 - 0.08, -0.08, 0.0, sx * 1.15 + 0.08, 0.08, 2.05, "M_Trim_White", bevel=0.02)
    bbox(mb, -1.3, -0.1, 0.75, 1.3, 0.1, 1.95, "M_Trim_Dark", bevel=0.03)
    for side in (0, 1):
        sub = MeshBuilder()
        sub.box(-1.18, -0.13, 0.85, 1.18, -0.1, 1.85, "M_Sign_Face", skip=("+y",))
        sub.extend(sign_text("COMMUNITY", 0.24, "M_Door_Navy", max_w=2.0, depth=0.03), Matrix.Translation((0, -0.145, 1.58)))
        sub.extend(sign_text("CHURCH", 0.3, "M_Door_Red", max_w=2.0, depth=0.03), Matrix.Translation((0, -0.145, 1.2)))
        sub.box(-0.7, -0.14, 0.93, 0.7, -0.13, 0.98, "M_Trim_Dark", skip=("+y",))
        mb.extend(sub, Matrix.Rotation(math.pi * side, 4, "Z"))
    sub = MeshBuilder()
    sub.prism([(-1.45, -0.3), (1.45, -0.3), (1.45, 0.3), (-1.45, 0.3)], 1.95, 2.05, "M_Roof_Charcoal", "M_Trim_White")
    mb.extend(sub)
    return mb


def _church(C_):
    S = C_.S
    BASE = Z_LOT + 0.35
    colors = dict(wall="M_Wall_White", trim="M_Trim_White", door="M_Door_Red", awning="M_Awning_Red",
                  roof="M_Roof_Charcoal", sign="M_Door_Red")
    NX, NY = -3.5, -5.0
    nspec = BuildingSpec("apartment", 3, 5, 1, dict(colors), roof="gable_front", ground_h=H4,
                         feats=dict(door_i=1, style="single"), seed=9401,
                         exposed={"left": True, "right": True, "back": True}, district="civic")
    nave = C_.building("Nave", nspec, NX, NY, base_z=BASE)
    drop(kids(nave, "Canopy_Door"))
    TY = NY - 2.9
    tspec = BuildingSpec("apartment", 1, 1, 3, dict(colors), roof="flat", ground_h=H3,
                         feats=dict(door_i=0, style="single", ac_units=0), seed=9402,
                         exposed={"left": True, "right": True, "back": True}, district="civic")
    tower = C_.building("Tower", tspec, NX, TY, base_z=BASE)
    C_.swap(tower, tspec, "front", 0, 0, "Wall_Door_H3", plinth="Plinth_Door_3m")
    for side in ("front", "left", "right"):
        C_.swap(tower, tspec, side, 2, 0, "Wall_Plain_H3")
    drop(kids(tower, "Canopy_Door"))
    drop(kids(tower, "Roof_AC"))
    r = K.REG.get("KIT_Wall_Door_H3")
    head = (r["meta"].get("head_top_z", 2.34) if r else 2.34) + 0.11
    C_.put("Canopy_Door", NX, TY, BASE + head, 0.0, grp="Church", recolor={"trim": "M_Trim_White"})
    ttop = BASE + tspec.wall_top()
    C_.mesh("Belfry_Spire", belfry_spire(), NX, TY + 1.5, ttop + 0.2, grp="Church", smooth=None)
    clocks = MeshBuilder()
    zc = 6.0 + 1.5
    clock_face(clocks, 0.0, -0.02, zc, 0.95)
    C_.mesh("TowerClock_S", clocks, NX, TY, BASE, grp="Church")
    for side, rot in (("E", R90), ("W", -R90)):
        cm = MeshBuilder()
        clock_face(cm, 0.0, -0.02, zc, 0.95)
        sgn = 1 if side == "E" else -1
        C_.mesh(f"TowerClock_{side}", cm, NX + sgn * 1.5, TY + 1.5, BASE, rot=rot, grp="Church")
    for dx in (-0.72, 0.72):
        C_.put("Steps_2", NX + dx, TY, Z_LOT, 0.0, grp="Church")

    # ---- ground: walk, connectors, cross path to the churchyard gate
    C_.pave("FrontWalk", [(NX - 1.7, -15.95), (NX + 1.7, -15.95), (NX + 1.7, TY - 0.55), (NX - 1.7, TY - 0.55)],
            "M_Plaza")
    C_.pave("SideWalk", [(NX + 1.7, -10.4), (7.4, -10.4), (7.4, -8.8), (NX + 1.7, -8.8)], "M_Path", z=Z_LOT - 0.005,
            skirt=0.2)
    C_.pave("YardGateWalk", [(5.6, -8.8), (7.4, -8.8), (7.4, -6.3), (5.6, -6.3)], "M_Path", z=Z_LOT - 0.005, skirt=0.2)
    C_.connector("WalkMouth", NX - 1.7, NX + 1.7, -15.8, "M_Plaza")
    for (x, y) in ((NX - 2.6, -15.2), (NX + 2.6, -15.2), (NX - 2.6, -10.0)):
        C_.put("Lamp_Park", x, y, None, 0.0, grp="Garden")
    C_.put("Flowerbed_2m", NX - 2.7, -12.4, None, R90, grp="Garden")
    C_.put("Flowerbed_2m", NX + 2.7, -12.6, None, R90, grp="Garden", recolor={"foliage": "M_Foliage_Light"})
    C_.put("Bench", NX - 3.0, -8.6, None, R90, grp="Garden")
    nb = notice_board()
    C_.mesh("NoticeBoard", nb, 3.6, -14.6, -0.05, 0.0, grp="Garden")
    for (x, y, t, r) in ((-9.4, -13.2, "Tree_Round_A", 0.6), (8.0, -12.4, "Tree_Round_B", 1.9),
                         (-9.7, 1.5, "Tree_Small", 0.0), (-9.7, 7.5, "Tree_Small", 0.7), (-6.4, 14.0, "Tree_Round_A", 2.4),
                         (-10.2, -5.5, "Bush_B", 0.2), (1.6, -6.9, "Bush_A", 0.9), (-8.6, -6.7, "Bush_A", 2.0),
                         (-9.9, 4.5, "Bush_A", 1.4)):
        C_.put(t, x, y, None, r, grp="Garden")
    C_.put("Bench", -2.4, 13.6, None, 0.0, grp="Garden")
    C_.put("Bench", 0.8, 13.6, None, 0.0, grp="Garden")
    C_.put("Birdbath", -0.8, 12.0, None, 0.0, grp="Garden")

    # ---- churchyard: white pickets, gate, headstones, tree, bench
    yx0, yx1, yy0, yy1 = 2.7, 10.5, -6.3, 15.4
    pick = Fence(S, "Fence_Picket_3m", sub=C_.g("Churchyard"))
    pick.line([(yx0, yy0), (yx0, yy1), (yx1, yy1), (yx1, yy0), (yx0, yy0)],
              gates=[(3, (yx1 - 6.5) / (yx1 - yx0), 1.4)])
    hs = C_.shared("Headstone", headstone)
    k = 0
    for row, y in enumerate((-3.0, 0.4, 3.8, 7.2)):
        for col, x in enumerate((4.2, 6.0, 7.8)):
            if (row, col) in ((1, 2), (3, 0)):
                continue
            jit = ((row * 7 + col * 3) % 5 - 2) * 0.04
            C_.inst(hs, f"Headstone_{k + 1:02d}", x + jit, y, -0.05, jit * 2, grp="Churchyard")
            k += 1
    C_.put("Tree_Round_A", 8.3, 11.8, None, 0.4, grp="Churchyard")
    C_.put("Bench", 5.0, 13.9, None, 0.0, grp="Churchyard")
    C_.put("Bush_A", 9.6, 1.9, None, 0.3, grp="Churchyard")
    C_.put("Flowerbed_2m", 4.6, 10.0, None, 0.0, grp="Churchyard", recolor={"foliage": "M_Foliage_Blossom"})
    anchor(C_, "Entrance", NX, TY - 1.6, Z_LOT, "civic_entrance", building="church")
    return dict(nave=nave.name, tower=tower.name, spire_top=round(ttop + 0.2 + 12.6, 2))


# =============================================================================== VET CLINIC
def pylon_sign():
    mb = MeshBuilder()
    bbox(mb, -0.3, -0.3, -0.05, 0.3, 0.3, 0.3, "M_Wall_Concrete", bevel=0.03)
    bbox(mb, -0.08, -0.08, 0.3, 0.08, 0.08, 2.4, "M_Trim_White", bevel=0.02)
    bbox(mb, -0.9, -0.12, 2.0, 0.9, 0.12, 2.55, "M_Awning_Blue", bevel=0.03)
    for side in (0, 1):
        sub = MeshBuilder()
        sub.extend(sign_text("VET", 0.36, "M_Sign_Face", max_w=1.4, depth=0.03), Matrix.Translation((0, -0.135, 2.28)))
        sub.extend(cross_paw_mb(0.62, 0.12), Matrix.Translation((0, 0.0, 3.25)))
        mb.extend(sub, Matrix.Rotation(math.pi * side, 4, "Z"))
    bbox(mb, -0.08, -0.08, 2.55, 0.08, 0.08, 2.7, "M_Trim_White")
    return mb


def _vet(C_):
    S = C_.S
    TEAL = "M_Awning_Blue"     # clinic accent (teal/orange is reserved for the pet shop)
    colors = dict(wall="M_Wall_White", trim="M_Trim_White", door="M_Door_Navy", awning=TEAL, roof="M_Roof_Slate",
                  sign=TEAL)
    BX, BY = -3.5, -3.5
    spec = BuildingSpec("shop", 4, 3, 2, colors, roof="flat", ground_h=H4,
                        feats=dict(door_i=1, style="pair", awning="flat", ac_units=2), seed=9501,
                        exposed={"right": True}, district="civic")
    root = C_.building("Clinic", spec, BX, BY)
    W = spec.W
    fx = -W / 2 + 1.5 + 3.0 * spec.feats["door_i"]
    fl = MeshBuilder()
    fl.box(-1.235, -0.1045, 0.165, 1.235, -0.0975, 0.535, TEAL, skip=("+y",))
    fl.extend(text_mb("VET CLINIC", 0.27, 0.022, "M_Sign_Face", max_w=2.2, offset=0.02, res=2),
              Matrix.Translation((0.0, -0.1155, 0.35)))
    C_.mesh("FasciaLettering", fl, BX + fx, BY, Z_LOT + 3.2, grp="Clinic")
    for dx in (-0.85, 0.85):
        C_.put("Sign_Lamp", BX + fx + dx, BY, Z_LOT + 3.95, grp="Clinic")
    # hero cross + paw medallion standing on the parapet
    top = Z_LOT + spec.wall_top()
    R = 1.3
    med = cross_paw_mb(R, 0.36)
    for bx in (-0.7, 0.7):
        bbox(med, bx - 0.08, 0.0, -R * 0.6 - 0.08, bx + 0.08, 0.6, -R * 0.6 + 0.08, "M_Metal_Dark")
    bbox(med, -0.08, 0.0, -R - 0.55, 0.08, 0.14, -R + 0.1, "M_Metal_Dark")
    C_.mesh("HeroSign_CrossPaw", med, BX, BY - 0.45, top + 0.28 + R, grp="Clinic")
    C_.mesh("PylonSign", pylon_sign(), 2.7, -9.0, Z_LOT, 0.0, grp="Forecourt")

    # ---- ground
    C_.pave("Forecourt", [(-10.95, -9.95), (3.3, -9.95), (3.3, BY), (-10.95, BY)], "M_Plaza")
    C_.pave("Doormat", [(fx + BX - 0.9, -6.2), (fx + BX + 0.9, -6.2), (fx + BX + 0.9, BY - 0.1), (fx + BX - 0.9, BY - 0.1)],
            "M_Awning_Teal", z=Z_LOT + 0.012, skirt=0.05)
    C_.pave("VanBay", [(3.3, -9.95), (10.95, -9.95), (10.95, -2.9), (3.3, -2.9)], "M_Concrete")
    C_.pave("ServiceYard", [(-10.95, BY + spec.D), (3.3, BY + spec.D), (3.3, 9.95), (-10.95, 9.95)], "M_Gravel",
            z=0.02, skirt=0.12)
    C_.connector("FrontApron", -10.95, 10.95, -9.8, "M_Plaza")
    paint = MeshBuilder()
    paint_rect(paint, 4.1, -9.5, 9.9, -3.4, 0.12, Z_LOT + 0.008, "M_RoadLine_White")
    for k in range(3):
        paint_line(paint, (4.5 + k * 0.6, -9.2), (5.0 + k * 0.6, -8.6), 0.1, Z_LOT + 0.008, TEAL)
    C_.mesh("VanBay_Paint", paint, grp="Ambulance")

    # ---- ambulance van (gameplay hook)
    van = C_.put("Car_Van", 7.0, -6.3, Z_LOT, 0.0, grp="Ambulance", recolor={"awning": "M_Wall_White"},
                 name="AnimalAmbulance")
    if van is not None:
        van["gameplay"] = "animal_ambulance"
        C_.inst(C_.shared("AmbulanceLivery", ambulance_livery, smooth=40), "AnimalAmbulance_Livery", 7.0, -6.3, Z_LOT,
                0.0, grp="Ambulance")

    # ---- forecourt dressing
    C_.put("Bench", -9.4, -8.2, Z_LOT, R90, grp="Forecourt")
    C_.put("Bench", -9.4, -5.6, Z_LOT, R90, grp="Forecourt")
    C_.put("Planter", -6.9, -4.2, Z_LOT, recolor={"trim": TEAL}, grp="Forecourt")
    C_.put("Planter", 1.9, -4.2, Z_LOT, recolor={"trim": TEAL}, grp="Forecourt")
    C_.put("BikeRack", -2.6, -9.2, Z_LOT, 0.0, grp="Forecourt")
    C_.put("TrashBin", -10.2, -9.4, Z_LOT, grp="Forecourt")
    bw = MeshBuilder()
    for (x, y) in ((-3.3, -4.3), (-0.1, -4.3)):
        bw.cylinder(x, y, Z_LOT, Z_LOT + 0.1, 0.2, TEAL, seg=12, cap_top=True, r_top=0.23)
        bw.cylinder(x, y, Z_LOT + 0.1, Z_LOT + 0.105, 0.19, "M_Water", seg=12, cap_top=True)
    C_.mesh("WaterBowls", bw, grp="Forecourt")

    # ---- dog run
    rx0, rx1, ry0, ry1 = 5.2, 10.7, -2.4, 9.7
    run = Fence(S, "Fence_Chain_3m", sub=C_.g("DogRun"))
    run.line([(rx0, ry0 + 3.4), (rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1), (rx0, ry0 + 5.0)])
    C_.put("Doghouse", 9.4, 8.2, None, -0.25, grp="DogRun",
           recolor={"wall": TEAL, "roof": "M_Wall_White", "trim": "M_Trim_White", "sign": "M_Door_Teal"})
    C_.put("Hydrant", 6.2, 1.2, None, 0.3, grp="DogRun")
    C_.put("Tree_Small", 9.6, 0.6, None, 0.0, grp="DogRun")
    C_.put("Bush_B", 4.6, 8.6, None, 0.7, grp="DogRun")
    C_.put("Bench", 4.4, 4.6, None, R90, grp="DogRun")
    toys = MeshBuilder()
    for (x, y, r, m) in ((7.4, 3.6, 0.17, "M_Awning_Yellow"), (8.8, 5.6, 0.14, "M_Awning_Red"),
                         (6.6, 6.9, 0.13, TEAL)):
        toys.sphere(x, y, -0.05 + r, r, m, seg=8, rings=5)
    toys.cylinder(4.5, -1.3, -0.05, 0.05, 0.22, TEAL, seg=12, cap_top=True, r_top=0.25)
    toys.cylinder(4.5, -1.3, 0.05, 0.055, 0.21, "M_Water", seg=12, cap_top=True)
    C_.mesh("DogRun_Toys", toys, grp="DogRun")
    # service yard
    C_.put("Dumpster", -9.6, 8.6, 0.02, 0.0, grp="Yard")
    C_.put("TrashBin", -7.8, 8.9, 0.02, grp="Yard")
    C_.put("Roof_AC_Unit", -5.6, 8.2, 0.02, 0.0, grp="Yard")
    C_.put("Car_Sedan", -0.8, 7.8, 0.02, R90, grp="Yard", recolor={"awning": "M_Wall_Mint"}, name="StaffCar")
    anchor(C_, "Heal", BX + fx, BY - 1.6, Z_LOT, "vet_heal", note="bring injured animals here to heal them")
    anchor(C_, "DogRun", 7.2, 3.6, -0.05, "dog_run", note="fenced run, gate on the clinic side")
    anchor(C_, "Ambulance", 7.0, -6.3, Z_LOT, "animal_ambulance")
    return dict(clinic=root.name)


# =============================================================================== entry point
BUILDERS = {"PoliceStation": _police, "FireStation": _fire, "School": _school, "Church": _church,
            "VetClinic": _vet}


def build(S):
    fn = BUILDERS.get(S.id)
    if fn is None:
        return dict(skipped=f"no civic_services builder for {S.id}")
    before = set(o.name for o in bpy.data.objects)
    C_ = Civ(S)
    out = fn(C_) or {}
    S.register_lot(S.poly)
    new = [o for o in bpy.data.objects if o.name not in before]
    out.update(C_.report(len(new)))
    return out
