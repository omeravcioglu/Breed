"""Phase 4b: gameplay marker empties (GP_*) for Unity: spawns, animal zones, hiding spots,
expansion plot, zoo incident, landmark anchors and vehicle entry points.

Empties carry custom properties (exported by FBX as user properties) so Unity tooling can read
habitat / animal lists without hardcoding positions.
"""
import math

from mathutils import Vector

from . import config as C
from . import geom2d as G
from . import scene

ROOT = "07_Gameplay_Markers"


def _z(ctx, x, y):
    from . import terrain
    z = C.SIDEWALK_Z
    for hd in getattr(ctx["layout"], "HILLS", []):
        z = max(z, C.GROUND_Z + terrain.hill_height(hd, x, y))
    return z


def build(ctx):
    layout, net = ctx["layout"], ctx["net"]
    n = {}

    def mk(name, sub, x, y, rot=0.0, disp="PLAIN_AXES", size=1.0, props=None, z=None):
        n[sub] = n.get(sub, 0) + 1
        return scene.empty(name[:63], f"{ROOT}/{sub}", (x, y, _z(ctx, x, y) if z is None else z), rot,
                           display=disp, size=size, props=props)

    sp = getattr(layout, "PLAYER_SPAWN", None)
    if sp:
        # heading_deg: facing direction, degrees counter-clockwise from +X (east).
        # Like kit pieces, GP_ empties face their local -Y, so rot = heading + 90 deg.
        h = math.radians(sp.get("heading_deg", 0.0))
        rot = h + math.pi / 2
        mk("GP_PlayerSpawn", "Spawns", sp["at"][0], sp["at"][1], rot,
           "ARROWS", 2.0, dict(gp_type="player_spawn", heading_deg=float(sp.get("heading_deg", 0.0)),
                               facing="local -Y"))
        # four co-op spawn slots side by side (perpendicular to the heading)
        side = Vector((math.cos(h + math.pi / 2), math.sin(h + math.pi / 2)))
        for i in range(4):
            off = side * (i - 1.5) * 1.6
            mk(f"GP_PlayerSpawn_Slot{i + 1}", "Spawns", sp["at"][0] + off.x, sp["at"][1] + off.y,
               rot, "SINGLE_ARROW", 1.0, dict(gp_type="player_slot", slot=i + 1, facing="local -Y"))
    for z in getattr(layout, "ANIMAL_ZONES", []):
        mk(f"GP_AnimalZone_{z['id']}", "AnimalZones", z["center"][0], z["center"][1], 0.0, "SPHERE",
           float(z.get("radius", 20.0)),
           dict(gp_type="animal_zone", habitat=z.get("habitat", ""), animals=", ".join(z.get("animals", [])),
                radius=float(z.get("radius", 20.0)), notes=z.get("notes", "")))
    anchors = ctx.get("hiding_anchors") or {}
    for h in getattr(layout, "HIDING_SPOTS", []):
        a = anchors.get(h["id"]) or {}
        x, y = a.get("anchor", h["at"])
        hd = a.get("heading_deg")
        rot = math.radians(hd) + math.pi / 2 if hd is not None else 0.0
        mk(f"GP_HidingSpot_{h['id']}", "HidingSpots", x, y, rot, "CONE", 1.5,
           dict(gp_type="hiding_spot", notes=h.get("notes", ""), status=a.get("status", "layout"),
                facing="local -Y" if hd is not None else ""),
           z=a.get("z"))
    for sid, site in getattr(layout, "LANDMARKS", {}).items():
        c = site.get("center")
        if c:
            mk(f"GP_Landmark_{sid}", "Landmarks", c[0], c[1], 0.0, "PLAIN_AXES", 4.0,
               dict(gp_type="landmark", name=site.get("name", sid)))
        if sid == "PetShop":
            f = G.V(site.get("facing", (0, -1))).normalized()
            rot = math.atan2(-f.y, -f.x) - math.pi / 2
            if site.get("expansion_poly"):
                poly = [G.V(p) for p in site["expansion_poly"]]
                cc = G.centroid(poly)
                o = mk("GP_ShopExpansionPlot", "PetShop", cc.x, cc.y, rot, "CUBE", 1.0,
                       dict(gp_type="shop_expansion", area_m2=round(abs(G.poly_area(poly)), 1)))
                # size the cube to the plot extents in its own frame
                X = Vector((math.cos(rot), math.sin(rot)))
                Y = Vector((-math.sin(rot), math.cos(rot)))
                xs = [(p - cc).dot(X) for p in poly]
                ys = [(p - cc).dot(Y) for p in poly]
                o.scale = ((max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2, 2.0)
            if c:
                mk("GP_ShopCounter", "PetShop", c[0], c[1], rot, "ARROWS", 1.5, dict(gp_type="shop_anchor"))
        if sid == "Zoo":
            if site.get("entrance"):
                f = G.V(site.get("entrance_facing", (0, -1))).normalized()
                mk("GP_ZooEntrance", "Zoo", site["entrance"][0], site["entrance"][1],
                   math.atan2(-f.y, -f.x) - math.pi / 2, "ARROWS", 3.0, dict(gp_type="zoo_entrance"))
            if site.get("incident_at"):
                mk("GP_ZooIncident", "Zoo", site["incident_at"][0], site["incident_at"][1], 0.0, "SPHERE", 10.0,
                   dict(gp_type="zoo_incident", notes="breach point; escaped animals radiate from here"))
    # vehicle / NPC entry points at map exits
    for nid, ends in net.ends_at.items():
        p = net.nodes[nid]["pos"]
        if len(ends) == 1 and (net.nodes[nid].get("exit") or max(abs(p.x), abs(p.y)) > C.CITY_HALF):
            d = ends[0].dir
            # faces into the city (local -Y along the road, away from the map edge)
            mk(f"GP_MapExit_{nid}", "MapExits", p.x, p.y, math.atan2(d.y, d.x) + math.pi / 2, "SINGLE_ARROW", 4.0,
               dict(gp_type="map_exit", road=ends[0].edge.road["id"]))
    return n
