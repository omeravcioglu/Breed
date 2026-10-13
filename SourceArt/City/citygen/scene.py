"""Scene / collection helpers and the canonical collection hierarchy."""
import bpy
from mathutils import Euler, Vector

ROOT = "CITY_Foundation"

# Canonical hierarchy. Paths are '/' separated under ROOT (or KIT_Library for the kit).
HIERARCHY = [
    "01_Terrain",
    "02_Roads/Roads_Surface",
    "02_Roads/Roads_Intersections",
    "02_Roads/Roads_Sidewalks",
    "02_Roads/Roads_Markings",
    "02_Roads/Roads_Bridges",
    "03_Zoning_Blockout",
    "04_Buildings",
    "05_Landmarks",
    "06_Props",
    "07_Gameplay_Markers",
    "08_Preview_Cameras",
    "99_Annotations",
]


def clear_scene():
    _COLL_CACHE.clear()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for b in list(blocks):
            blocks.remove(b)


def coll(path, root=ROOT):
    """Get/create a nested collection 'A/B/C' under root (root itself linked to the scene)."""
    sc = bpy.context.scene
    parent = bpy.data.collections.get(root)
    if parent is None:
        parent = bpy.data.collections.new(root)
        sc.collection.children.link(parent)
    if not path:
        return parent
    for part in path.split("/"):
        key = (parent.name, part)
        c = _COLL_CACHE.get(key)
        try:
            stale = c is None or c.name not in bpy.data.collections
        except ReferenceError:
            stale = True
        if stale:
            # resolve among THIS parent's children only (names are global in Blender, so two
            # sites may both want a "Trees" sub-collection)
            c = next((ch for ch in parent.children if ch.get("cg_part", ch.name) == part), None)
            if c is None:
                name = part
                if bpy.data.collections.get(name) is not None:      # clash elsewhere -> qualify
                    name = f"{parent.name}.{part}"[:63]
                c = bpy.data.collections.new(name)
                c["cg_part"] = part
                parent.children.link(c)
            _COLL_CACHE[key] = c
        parent = c
    return parent


_COLL_CACHE = {}


def ensure_hierarchy():
    for p in HIERARCHY:
        coll(p)


def obj(name, data, path, loc=(0, 0, 0), rot_z=0.0, root=ROOT, parent=None):
    o = bpy.data.objects.new(name, data)
    o.location = Vector(loc) if len(loc) == 3 else Vector((loc[0], loc[1], 0.0))
    o.rotation_euler = Euler((0.0, 0.0, rot_z))
    coll(path, root).objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


def empty(name, path, loc=(0, 0, 0), rot_z=0.0, display="PLAIN_AXES", size=1.0, root=ROOT, parent=None, props=None):
    o = obj(name, None, path, loc, rot_z, root=root, parent=parent)
    o.empty_display_type = display
    o.empty_display_size = size
    if props:
        for k, v in props.items():
            o[k] = v
    return o


def set_visible(path, visible, root=ROOT):
    """Exclude/include a collection in the active view layer."""
    c = coll(path, root)

    def find(lc):
        if lc.collection == c:
            return lc
        for ch in lc.children:
            r = find(ch)
            if r:
                return r
        return None

    lc = find(bpy.context.view_layer.layer_collection)
    if lc:
        lc.exclude = not visible
    c.hide_render = not visible
