"""Export the city foundation for Unity (run on a built .blend).

    blender -b City_Foundation.blend --factory-startup --python export_unity.py -- [--out Export/Unity] [--what kit,env,instances]

Outputs (default <this folder>/Export/Unity):
  Kit/<family>/<KIT_Name>.fbx    one FBX per kit piece, origin at the piece origin (-> Unity prefabs)
  Env/<Collection>.fbx           static environment chunks (terrain, roads, landmarks' custom meshes)
  instances.json                 every kit instance (buildings, props, landmark pieces) with its Unity-space
                                 transform, parent building and per-slot material overrides, so an editor
                                 script can rebuild the city from prefabs (GPU instancing / static batching).

Axis conversion: Blender Z-up right-handed -> Unity Y-up left-handed. FBX is written with
axis_forward='-Z', axis_up='Y', bake_space_transform=True (no -90 deg X rotation in Unity).
instances.json stores RAW Blender-space transforms (position, rot_z_deg, scale). The Unity-side
importer must apply the same axis conversion Unity applies to these FBX files - verify once with a
single prefab (expected: unity_pos = (-x, z, -y), unity_yaw = -rot_z_deg; kit fronts face -Y in Blender).
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "Export", "Unity"))
    ap.add_argument("--what", default="kit,env,instances,markers")
    return ap.parse_args(argv)


def _select_only(objs):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        try:
            o.select_set(True)
        except RuntimeError:
            pass
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def _fbx(path, objs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _select_only(objs)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH", "EMPTY"},
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", bake_space_transform=True,
                             use_custom_props=True, mesh_smooth_type="FACE", add_leaf_bones=False,
                             use_mesh_modifiers=True, path_mode="STRIP")


def _ensure_visible():
    def walk(lc):
        if lc.exclude:
            lc.exclude = False
        if lc.hide_viewport:
            lc.hide_viewport = False
        for c in lc.children:
            walk(c)
    walk(bpy.context.view_layer.layer_collection)
    for o in bpy.data.objects:          # only touch what is actually hidden (100k objects)
        if o.hide_viewport:
            o.hide_viewport = False
        if o.hide_get():
            o.hide_set(False)


def _coll_map():
    """object name -> first owning collection name, built once (users_collection is O(N) per call)."""
    m = {}
    for c in bpy.data.collections:
        for o in c.objects:
            m.setdefault(o.name, c.name)
    return m


def _kit_meshes():
    return {o.data.name: o.name for o in bpy.data.objects if o.name.startswith("KIT_") and o.type == "MESH"}


def export_kit(out):
    kit_root = bpy.data.collections.get("KIT_Library")
    if kit_root is None:
        return 0
    n = 0
    for o in kit_root.all_objects:
        if o.type != "MESH" or not o.name.startswith("KIT_") or o.name == "KIT_ShelfGround":
            continue
        fam = o.get("kit_family", "misc")
        loc = o.location.copy()
        o.location = (0, 0, 0)
        bpy.context.view_layer.update()
        _fbx(os.path.join(out, "Kit", fam, o.name + ".fbx"), [o])
        o.location = loc
        n += 1
    return n


ENV_COLLECTIONS = ["01_Terrain", "Roads_Surface", "Roads_Intersections", "Roads_Sidewalks", "Roads_Markings",
                   "Roads_Bridges"]


def export_env(out, covered):
    """Static environment + every custom (non-kit) mesh: landmarks per site, custom props (wires...)."""
    kit = _kit_meshes()
    n = 0
    for cname in ENV_COLLECTIONS:
        c = bpy.data.collections.get(cname)
        if c is None:
            continue
        objs = [o for o in c.all_objects if o.type == "MESH"]
        if objs:
            _fbx(os.path.join(out, "Env", cname + ".fbx"), objs)
            covered.update(o.name for o in objs)
            n += 1
    for top, sub in (("05_Landmarks", "Landmarks"), ("06_Props", "Props")):
        root = bpy.data.collections.get(top)
        if root is None:
            continue
        for site in root.children:
            objs = [o for o in site.all_objects
                    if o.type == "MESH" and o.data.name not in kit and o.name not in covered]
            if objs:
                _fbx(os.path.join(out, "Env", sub, site.name.replace(".", "_") + ".fbx"), objs)
                covered.update(o.name for o in objs)
                n += 1
    return n


def _blender_transform(o):
    loc, rot, sc = o.matrix_world.decompose()
    e = rot.to_euler("XYZ")
    return dict(position=[round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)],
                rot_z_deg=round(math.degrees(e.z), 3),
                rot_euler_xyz_deg=[round(math.degrees(e.x), 3), round(math.degrees(e.y), 3), round(math.degrees(e.z), 3)],
                quat_wxyz=[round(rot.w, 6), round(rot.x, 6), round(rot.y, 6), round(rot.z, 6)],
                scale=[round(sc.x, 4), round(sc.y, 4), round(sc.z, 4)])


def _props(o):
    out = {}
    for k in o.keys():
        v = o[k]
        if isinstance(v, (int, float, str, bool)):
            out[k] = v
    return out


def export_instances(out, covered, cmap):
    kit_meshes = _kit_meshes()
    rows = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith("KIT_"):
            continue
        src = kit_meshes.get(o.data.name)
        if not src:
            continue
        overrides = {}
        for i, slot in enumerate(o.material_slots):
            if slot.link == "OBJECT" and slot.material is not None:
                overrides[str(i)] = slot.material.name
        top = o
        while top.parent is not None:
            top = top.parent
        rows.append(dict(name=o.name, prefab=src, collection=cmap.get(o.name, ""),
                         building=top.name if top is not o else None, materials=overrides, **_blender_transform(o)))
        covered.add(o.name)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "instances.json"), "w") as f:
        json.dump(dict(coordinate_note="RAW Blender space (Z-up, meters); convert like the FBX import (see export_unity.py)",
                       count=len(rows), instances=rows), f)
    return len(rows)


def export_markers(out, cmap):
    """Gameplay empties (GP_*, *_Anchor_*) and building / lot roots with all their custom properties."""
    markers, roots = [], []
    for o in bpy.data.objects:
        if o.type != "EMPTY":
            continue
        row = dict(name=o.name, collection=cmap.get(o.name, ""), props=_props(o), **_blender_transform(o))
        if o.name.startswith("GP_") or "_Anchor_" in o.name:
            if "gp_type" not in row["props"] and "gameplay" in row["props"]:
                row["props"]["gp_type"] = row["props"]["gameplay"]
            markers.append(row)
        elif o.name.startswith(("BLD_", "LOT_")):
            roots.append(row)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "markers.json"), "w") as f:
        json.dump(dict(note="local -Y is each marker's facing; RAW Blender space", count=len(markers), markers=markers), f, indent=0)
    with open(os.path.join(out, "roots.json"), "w") as f:
        json.dump(dict(count=len(roots), roots=roots), f)
    return dict(markers=len(markers), roots=len(roots))


def coverage(covered):
    """Every visible mesh outside the kit shelf should be exported by exactly one path."""
    shelf = set()
    kc = bpy.data.collections.get("KIT_Library")
    if kc is not None:
        shelf = {o.name for o in kc.all_objects}
    hidden_colls = {"03_Zoning_Blockout", "99_Annotations", "08_Preview_Cameras"}
    skip = set()
    for cn in hidden_colls:
        c = bpy.data.collections.get(cn)
        if c is not None:
            skip.update(o.name for o in c.all_objects)
    missing = [o.name for o in bpy.data.objects
               if o.type == "MESH" and o.name not in covered and o.name not in shelf and o.name not in skip]
    return dict(missing=len(missing), examples=missing[:12])


def main():
    a = args()
    _ensure_visible()
    what = a.what.split(",")
    rep = {}
    covered = set()
    cmap = _coll_map()
    if "kit" in what:
        rep["kit_fbx"] = export_kit(a.out)
    if "env" in what:
        rep["env_fbx"] = export_env(a.out, covered)
    if "instances" in what:
        rep["instances"] = export_instances(a.out, covered, cmap)
    if "markers" in what:
        rep.update(export_markers(a.out, cmap))
    if "env" in what and "instances" in what:
        rep["coverage"] = coverage(covered)
    rep["out"] = a.out
    print("EXPORT_REPORT", json.dumps(rep))


if __name__ == "__main__":
    main()
