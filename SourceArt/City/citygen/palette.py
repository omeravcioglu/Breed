"""Shared stylized material palette.

Every material is a plain Principled BSDF with a flat base color (plus roughness), so it
imports cleanly into Unity as a standard Lit material. Names are prefixed M_.
The viewport/Workbench color (diffuse_color) is kept in sync so solid-mode previews match.

Keep this list SHORT and shared: the whole city should read as one visual language.
"""
import bpy

# name: (hex sRGB, roughness, metallic)
PALETTE = {
    # ---------------------------------------------------------------- ground & roads
    "M_Asphalt":        ("#4a4e58", 0.92, 0.0),
    "M_Asphalt_Alley":  ("#5a5c62", 0.95, 0.0),
    "M_RoadLine_White": ("#efebe1", 0.80, 0.0),
    "M_RoadLine_Yellow":("#f0bf4c", 0.80, 0.0),
    "M_Sidewalk":       ("#cdc6b8", 0.90, 0.0),
    "M_Curb":           ("#aaa49a", 0.90, 0.0),
    "M_Grass":          ("#8dbb5e", 0.95, 0.0),
    "M_Grass_Park":     ("#7aae52", 0.95, 0.0),
    "M_Grass_Dry":      ("#b3b866", 0.95, 0.0),
    "M_Dirt":           ("#b58e62", 0.95, 0.0),
    "M_Gravel":         ("#a8a093", 0.95, 0.0),
    "M_Concrete":       ("#b9b5ad", 0.90, 0.0),
    "M_Plaza":          ("#dbc9a6", 0.90, 0.0),
    "M_Plaza_Accent":   ("#c98f6b", 0.90, 0.0),
    "M_Path":           ("#d9c39a", 0.95, 0.0),
    "M_Water":          ("#4aa6bd", 0.15, 0.0),
    "M_Water_Deep":     ("#3a8aa6", 0.15, 0.0),
    "M_CanalStone":     ("#9a948a", 0.90, 0.0),
    "M_RiverBed":       ("#6f7a6c", 0.95, 0.0),
    "M_Sand":           ("#e6d3a3", 0.95, 0.0),
    "M_Rock":           ("#a59a8a", 0.90, 0.0),

    # ---------------------------------------------------------------- building walls
    "M_Wall_Cream":     ("#f0e4c8", 0.85, 0.0),
    "M_Wall_Butter":    ("#f2d27a", 0.85, 0.0),
    "M_Wall_Peach":     ("#f1b48f", 0.85, 0.0),
    "M_Wall_Coral":     ("#e7876e", 0.85, 0.0),
    "M_Wall_Brick":     ("#b4553f", 0.88, 0.0),
    "M_Wall_Sage":      ("#a9c49f", 0.85, 0.0),
    "M_Wall_Mint":      ("#9fd4c6", 0.85, 0.0),
    "M_Wall_Sky":       ("#9dc3e0", 0.85, 0.0),
    "M_Wall_Lavender":  ("#baaad6", 0.85, 0.0),
    "M_Wall_Rose":      ("#e8a4b4", 0.85, 0.0),
    "M_Wall_White":     ("#f4f1ea", 0.85, 0.0),
    "M_Wall_Slate":     ("#6f7d8c", 0.88, 0.0),
    "M_Wall_Concrete":  ("#bab6ae", 0.90, 0.0),
    "M_Wall_Corrugated":("#8ea3ad", 0.70, 0.25),

    # ---------------------------------------------------------------- trims, roofs, openings
    "M_Trim_White":     ("#f8f5ef", 0.80, 0.0),
    "M_Trim_Dark":      ("#3f4551", 0.80, 0.0),
    "M_Trim_Wood":      ("#8a5a3c", 0.85, 0.0),
    "M_Roof_Slate":     ("#56607a", 0.85, 0.0),
    "M_Roof_Terracotta":("#c2583f", 0.85, 0.0),
    "M_Roof_Green":     ("#4f7a5a", 0.85, 0.0),
    "M_Roof_Charcoal":  ("#3c4048", 0.85, 0.0),
    "M_Roof_Flat":      ("#9b968d", 0.95, 0.0),
    "M_Glass":          ("#5d8fb2", 0.08, 0.1),
    "M_Glass_Shop":     ("#3f93bd", 0.06, 0.15),   # deeper than M_Wall_Sky so storefronts read at range
    "M_Door_Wood":      ("#9c6541", 0.80, 0.0),
    "M_Door_Red":       ("#c8473e", 0.70, 0.0),
    "M_Door_Teal":      ("#2f8f8a", 0.70, 0.0),
    "M_Door_Navy":      ("#35476c", 0.70, 0.0),
    "M_Metal":          ("#8c939c", 0.45, 0.6),
    "M_Metal_Dark":     ("#4b5059", 0.50, 0.5),
    "M_RollerDoor":     ("#a7adb3", 0.55, 0.4),

    # ---------------------------------------------------------------- awnings & signage
    "M_Awning_Red":     ("#d9534f", 0.80, 0.0),
    "M_Awning_Cream":   ("#f7edd6", 0.80, 0.0),
    "M_Awning_Green":   ("#5ea56b", 0.80, 0.0),
    "M_Awning_Blue":    ("#4f86c6", 0.80, 0.0),
    "M_Awning_Yellow":  ("#f2c14e", 0.80, 0.0),
    "M_Awning_Teal":    ("#3fa7a0", 0.80, 0.0),
    "M_Sign_Board":     ("#2f3a4a", 0.70, 0.0),
    "M_Sign_Face":      ("#f6efe0", 0.60, 0.0),
    "M_Sign_Accent":    ("#ff8a5c", 0.60, 0.0),

    # ---------------------------------------------------------------- nature & props
    "M_Foliage":        ("#69a74e", 0.90, 0.0),
    "M_Foliage_Dark":   ("#4d8a3f", 0.90, 0.0),
    "M_Foliage_Light":  ("#9cc65a", 0.90, 0.0),
    "M_Foliage_Autumn": ("#e3a13b", 0.90, 0.0),
    "M_Foliage_Blossom":("#f2a7c3", 0.90, 0.0),
    "M_Bark":           ("#7a5338", 0.90, 0.0),
    "M_Hedge":          ("#5a9346", 0.90, 0.0),
    "M_Fence_White":    ("#f3efe6", 0.80, 0.0),
    "M_Fence_Wood":     ("#a87a52", 0.85, 0.0),
    "M_Wood_Light":     ("#c9a36f", 0.85, 0.0),
    "M_Dumpster":       ("#3f7d5c", 0.70, 0.2),
    "M_Crate":          ("#c49a62", 0.85, 0.0),
    "M_Hazard":         ("#f2c14e", 0.70, 0.0),
    "M_Hazard_Dark":    ("#2d2f33", 0.70, 0.0),
    "M_Hazard_Orange":  ("#ff7a2f", 0.65, 0.0),
    "M_Light_Emit":     ("#fff2c9", 0.40, 0.0),

    # ---------------------------------------------------------------- landmark accents
    "M_PetShop_Primary":("#ff8a5c", 0.75, 0.0),   # signature orange
    "M_PetShop_Second": ("#3fb0a8", 0.75, 0.0),   # signature teal
    "M_Zoo_Primary":    ("#3e7b4f", 0.80, 0.0),   # zoo green
    "M_Zoo_Accent":     ("#f2c14e", 0.75, 0.0),   # zoo yellow
    "M_Zoo_Fence":      ("#2f5d3c", 0.70, 0.2),
    "M_Incident":       ("#2b2b2e", 0.95, 0.0),   # scorch marks / debris

    # ---------------------------------------------------------------- blockout / zoning (map overlay only)
    "M_Zone_Downtown":  ("#e07a5f", 0.90, 0.0),
    "M_Zone_Residential":("#f2cc8f", 0.90, 0.0),
    "M_Zone_Suburb":    ("#e9d8a6", 0.90, 0.0),
    "M_Zone_Park":      ("#81b29a", 0.90, 0.0),
    "M_Zone_PetShop":   ("#ff9f68", 0.90, 0.0),
    "M_Zone_Zoo":       ("#7f9c5a", 0.90, 0.0),
    "M_Zone_Service":   ("#8d99ae", 0.90, 0.0),
    "M_Zone_Riverside": ("#7fc8d6", 0.90, 0.0),
    "M_Zone_Market":    ("#d4a5c9", 0.90, 0.0),
    "M_Label":          ("#1d1f24", 0.90, 0.0),
}

WALL_COLORS_WARM = ["M_Wall_Cream", "M_Wall_Butter", "M_Wall_Peach", "M_Wall_Coral", "M_Wall_Rose", "M_Wall_White"]
WALL_COLORS_COOL = ["M_Wall_Sage", "M_Wall_Mint", "M_Wall_Sky", "M_Wall_Lavender", "M_Wall_White"]
WALL_COLORS_DOWNTOWN = ["M_Wall_Brick", "M_Wall_Cream", "M_Wall_Butter", "M_Wall_Coral", "M_Wall_Sage",
                        "M_Wall_Sky", "M_Wall_Peach", "M_Wall_White", "M_Wall_Lavender"]
WALL_COLORS_INDUSTRIAL = ["M_Wall_Slate", "M_Wall_Concrete", "M_Wall_Corrugated", "M_Wall_Brick"]
ROOF_COLORS = ["M_Roof_Slate", "M_Roof_Terracotta", "M_Roof_Green", "M_Roof_Charcoal"]
AWNING_COLORS = ["M_Awning_Red", "M_Awning_Green", "M_Awning_Blue", "M_Awning_Yellow", "M_Awning_Teal"]
DOOR_COLORS = ["M_Door_Wood", "M_Door_Red", "M_Door_Teal", "M_Door_Navy"]


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def get(name):
    """Return (creating on first use) the palette material *name*."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    if name not in PALETTE:
        raise KeyError(f"Material {name!r} is not in the shared palette (citygen/palette.py)")
    hexcol, rough, metal = PALETTE[name]
    lin = hex_to_linear(hexcol)
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    bsdf = None
    if m.node_tree is not None:
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if name == "M_Light_Emit":
            try:
                bsdf.inputs["Emission Color"].default_value = (*lin, 1.0)
                bsdf.inputs["Emission Strength"].default_value = 2.0
            except KeyError:
                pass
    m.diffuse_color = (*lin, 1.0)
    m.roughness = rough
    m.metallic = metal
    m["citygen_palette"] = True
    return m


def ensure_all():
    for n in PALETTE:
        get(n)
