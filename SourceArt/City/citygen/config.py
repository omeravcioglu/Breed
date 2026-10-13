"""Global scale, grid and road-class constants. All units are meters, Z-up (Blender)."""

# ---------------------------------------------------------------- city extents
CITY_HALF = 350.0          # gameplay footprint is [-350, 350]^2  (~700m x 700m)
GROUND_HALF = 420.0        # ground plane extends a bit further for the map edge treatment

# ---------------------------------------------------------------- vertical levels
GROUND_Z = -0.05           # grass / base ground
ROAD_Z = 0.0               # asphalt top
MARK_Z = 0.02              # road paint sits slightly above asphalt
SIDEWALK_Z = 0.15          # sidewalk / curb top
LOT_Z = 0.15               # building plinth top (matches sidewalk so doors are flush)
SKIRT_Z = -0.12            # bottom of curb / sidewalk skirts (hidden below ground)

# ---------------------------------------------------------------- building grid
MODULE_W = 3.0             # one facade module is 3m wide
FLOOR_H = 3.0              # standard floor height
SHOP_FLOOR_H = 4.0         # tall ground-floor storefront height
WALL_T = 0.30              # wall thickness

# ---------------------------------------------------------------- road classes
# lanes_w: asphalt width, sidewalk: width of each sidewalk, curb_r: corner fillet radius
ROAD_CLASSES = {
    "main":      dict(lanes_w=11.0, sidewalk=3.5, curb_r=7.0, marking="double_yellow", crosswalk=True,  lights=24.0),
    "secondary": dict(lanes_w=8.0,  sidewalk=2.5, curb_r=5.5, marking="dashed_white",  crosswalk=True,  lights=28.0),
    "side":      dict(lanes_w=6.0,  sidewalk=2.0, curb_r=4.5, marking=None,            crosswalk=False, lights=34.0),
    "alley":     dict(lanes_w=4.5,  sidewalk=0.0, curb_r=2.5, marking=None,            crosswalk=False, lights=0.0),
}

SPLINE_STEP = 1.0          # sampling step for road centerline splines
RIBBON_STEP = 2.0          # resampling step for road ribbons
CULDESAC_R = 9.5           # cul-de-sac bulb radius (asphalt)

# ---------------------------------------------------------------- river / canal
CANAL_BED_Z = -2.6
CANAL_WATER_Z = -1.25
CANAL_COPING_Z = 0.10      # top of canal edge wall (below sidewalk level so bridges hide it)

# ---------------------------------------------------------------- naming prefixes (Unity friendly)
PREFIX = dict(
    road="RD_", sidewalk="SW_", intersection="IX_", marking="MK_", bridge="BR_",
    terrain="TRN_", water="WTR_", zone="ZN_", kit="KIT_", building="BLD_",
    landmark="LM_", prop="PROP_", marker="GP_", label="LBL_",
)
