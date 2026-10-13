"""Preview renders (Workbench for speed, EEVEE for beauty shots)."""
import math
import os

import bpy
from mathutils import Vector

from . import config as C
from . import scene


def _workbench(sc, flat=False, shadows=True):
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "FLAT" if flat else "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_shadows = shadows and not flat
    sh.shadow_intensity = 0.45
    sh.show_cavity = not flat
    try:
        sh.cavity_type = "WORLD"
        sh.cavity_ridge_factor = 0.6
        sh.cavity_valley_factor = 0.8
    except Exception:
        pass
    sc.display.light_direction = (0.45, -0.35, 0.82)
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.color = (0.62, 0.74, 0.86)
    try:
        sc.display.render_aa = "8"
    except Exception:
        pass


def _camera(name, loc, target=None, ortho_scale=None, lens=35.0, rot=None):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = scene.obj(name, cd, "08_Preview_Cameras", loc)
    cam.location = Vector(loc)
    cd = cam.data
    cd.clip_start = 0.5
    cd.clip_end = 4000
    if ortho_scale:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho_scale
        cam.rotation_euler = (0.0, 0.0, 0.0) if rot is None else rot
    else:
        cd.type = "PERSP"
        cd.lens = lens
        d = Vector(target) - Vector(loc)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return cam


def _eevee(sc):
    sc.render.engine = "BLENDER_EEVEE"
    try:
        sc.eevee.taa_render_samples = 24
    except Exception:
        pass
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    w = sc.world
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg is not None:
        bg.inputs["Color"].default_value = (0.55, 0.70, 0.88, 1.0)
        bg.inputs["Strength"].default_value = 0.95
    sun = bpy.data.objects.get("LGT_PreviewSun")
    if sun is None:
        ld = bpy.data.lights.new("LGT_PreviewSun", "SUN")
        sun = scene.obj("LGT_PreviewSun", ld, "08_Preview_Cameras", (0, 0, 100))
        sun.rotation_euler = (math.radians(48), math.radians(8), math.radians(35))
    sun.data.energy = 2.7
    sun.data.color = (1.0, 0.96, 0.9)
    sun.data.angle = math.radians(3.0)


def render(path, cam, res=(1600, 1200), flat=False, shadows=True, hide=(), show=(), beauty=False):
    sc = bpy.context.scene
    if beauty:
        _eevee(sc)
    else:
        _workbench(sc, flat=flat, shadows=shadows)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.abspath(path)
    prev = {}
    for p in hide:
        c = bpy.data.collections.get(p)
        if c:
            prev[p] = c.hide_render
            c.hide_render = True
    for p in show:
        c = bpy.data.collections.get(p)
        if c:
            prev[p] = c.hide_render
            c.hide_render = False
    bpy.ops.render.render(write_still=True)
    for p, v in prev.items():
        bpy.data.collections[p].hide_render = v
    return path


def map_top(path, half=None, res=2048, flat=True, center=(0, 0), hide=(), show=()):
    half = half or C.GROUND_HALF
    cam = _camera("CAM_MapTop", (center[0], center[1], 600.0), ortho_scale=2 * half)
    return render(path, cam, (res, res), flat=flat, shadows=not flat, hide=hide, show=show)


def view(path, loc, target, lens=30.0, res=(1600, 1000), name="CAM_View", hide=(), show=(), beauty=True):
    cam = _camera(name, loc, target=target, lens=lens)
    return render(path, cam, res, flat=False, hide=hide, show=show, beauty=beauty)
