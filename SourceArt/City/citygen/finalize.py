"""Phase 5: organization, sanity checks, viewport setup and Unity-facing JSON manifests."""
import json
import math
import os

import bpy

from . import config as C
from . import scene

COLL_COLORS = {
    "01_Terrain": "COLOR_04", "02_Roads": "COLOR_08", "03_Zoning_Blockout": "COLOR_07",
    "04_Buildings": "COLOR_02", "05_Landmarks": "COLOR_01", "06_Props": "COLOR_03",
    "07_Gameplay_Markers": "COLOR_06", "08_Preview_Cameras": "NONE", "99_Annotations": "NONE",
    "KIT_Library": "COLOR_05",
}
GENERATOR_VERSION = "0.1.0"


def _organize():
    for name, tag in COLL_COLORS.items():
        c = bpy.data.collections.get(name)
        if c is not None:
            try:
                c.color_tag = tag
            except Exception:
                pass
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"
    # objects linked directly to the scene master collection would be "loose" - adopt them
    loose = list(sc.collection.objects)
    for o in loose:
        scene.coll("99_Annotations").objects.link(o)
        sc.collection.objects.unlink(o)
    return len(loose)


def _checks():
    issues = []
    empty_meshes = [m.name for m in bpy.data.meshes if len(m.polygons) == 0 and m.users > 0]
    if empty_meshes:
        issues.append(f"{len(empty_meshes)} meshes without faces: {empty_meshes[:8]}")
    bad_scale = [o.name for o in bpy.data.objects if o.type == "MESH" and any(s < 0 for s in o.scale)]
    if bad_scale:
        issues.append(f"negative scale on {len(bad_scale)} objects (bad for Unity): {bad_scale[:8]}")
    off_palette = [m.name for m in bpy.data.materials if m.users and not m.get("citygen_palette")]
    if off_palette:
        issues.append(f"materials outside the shared palette: {off_palette[:8]}")
    return issues


def _viewport():
    """Make the saved .blend open in a readable state (solid + material colors, clip far)."""
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != "VIEW_3D":
                continue
            for sp in area.spaces:
                if sp.type != "VIEW_3D":
                    continue
                sp.clip_end = 6000.0
                sp.clip_start = 0.3
                sh = sp.shading
                sh.type = "SOLID"
                sh.color_type = "MATERIAL"
                sh.light = "STUDIO"
                sh.show_cavity = True
                try:
                    sh.cavity_type = "WORLD"
                except Exception:
                    pass
                sh.show_shadows = False
                r3d = sp.region_3d
                if r3d is not None:
                    r3d.view_location = (0.0, -40.0, 0.0)
                    r3d.view_distance = 650.0
                    from mathutils import Euler
                    r3d.view_rotation = Euler((math.radians(52), 0.0, math.radians(20))).to_quaternion()
                    r3d.view_perspective = "PERSP"


def _road_graph(net):
    nodes = {k: dict(x=round(v["pos"].x, 2), y=round(v["pos"].y, 2),
                     degree=len(net.ends_at.get(k, [])), culdesac=bool(v.get("culdesac")), exit=bool(v.get("exit")))
             for k, v in net.nodes.items() if k in net.ends_at}
    edges = []
    for e in net.edges:
        st = e.poly.stations(0.0, e.poly.length, 4.0)
        edges.append(dict(id=e.id, road=e.road["id"], name=e.road.get("name", ""), cls=e.cls, a=e.a, b=e.b,
                          half_width=e.hw, sidewalk=e.sw, length=round(e.poly.length, 1),
                          points=[[round(e.poly.pos(s).x, 2), round(e.poly.pos(s).y, 2)] for s in st]))
    return dict(units="meters, Blender Z-up (x east, y north); Unity: x->x, y->z", nodes=nodes, edges=edges)


def run(ctx, export_dir=None):
    loose = _organize()
    issues = _checks()
    _viewport()
    root = bpy.data.collections.get(scene.ROOT)
    if root is not None:
        root["generator"] = "citygen"
        root["generator_version"] = GENERATOR_VERSION
        root["layout"] = ctx["layout"].__name__
    out = dict(loose_objects_adopted=loose, issues=issues)
    export_dir = export_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Export")
    os.makedirs(export_dir, exist_ok=True)
    net = ctx["net"]
    with open(os.path.join(export_dir, "road_graph.json"), "w") as f:
        json.dump(_road_graph(net), f, indent=1)
    layout = ctx["layout"]
    manifest = dict(
        generator_version=GENERATOR_VERSION, layout=layout.__name__,
        footprint=dict(city_half=C.CITY_HALF, ground_half=C.GROUND_HALF),
        districts=[dict(id=d["id"], name=d.get("name", d["id"]), kind=d["kind"]) for d in layout.DISTRICTS],
        landmarks={k: dict(name=v.get("name", k), center=v.get("center")) for k, v in getattr(layout, "LANDMARKS", {}).items()},
        buildings=ctx.get("placed", []),
        object_count=len(bpy.data.objects),
        mesh_count=len(bpy.data.meshes),
        material_count=len([m for m in bpy.data.materials if m.users]),
    )
    try:
        from . import kit
        manifest["kit"] = kit.manifest()
    except Exception:
        pass
    with open(os.path.join(export_dir, "city_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, default=str)
    out["export_dir"] = export_dir
    return out
