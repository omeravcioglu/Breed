"""Candidate C - "Hub and Habitats".

CONCEPT
-------
Gameplay loop first: leave the shop, catch, come back. The pet shop sits at the exact heart of the
map (0, 0) on a small corner plaza at THE HUB, where four main arms meet: Founders Avenue arriving
from the park/north-west and leaving east to downtown, Zoo Avenue climbing north-east to the zoo gate,
and Harbor Road dropping south over the canal to the docks. Right beside the junction a tiny
triangular village green (Hub Green, wrapped by Elm Street) turns the 4-way into an organic
"five-point" knot, and the shop faces it across the corner plaza. Behind the shop a ~48 x 45 m
expansion plot runs back toward Canal Street and Kibble Alley (rear delivery access), so growth
(kennels, breeding rooms, aviary) has an obvious place to go and a view of the water.

Every district is also an animal habitat, and each sits one road away from the Hub:
  * NORTH-EAST  - the ZOO (incident origin). Zoo Avenue ends at a forecourt plaza in front of the
    chamfered south-west gate; Zoo Row (souvenir shops) lines the avenue. The breach is on the zoo's
    south fence, facing downtown and the Hub, so the first wave of animals pours straight into town.
    Keeper's Lane loops behind the zoo (back-of-house, hidden service strip).
  * WEST        - CENTRAL PARK: hill + lookout in the north-west, a big pond in the middle, the
    Great Lawn on the east side, facing the pet-shop block across Willow Lane. Riverwalk on its
    canal edge, woodland strip beyond Meadow Road at the map edge.
  * EAST        - DOWNTOWN: Founders Avenue becomes the high street; Town Square sits at the
    Founders / Clock Street corner; offset T's (Clock north, Mercer south) keep it from reading as a
    grid. Tanner Alley and Rope Alley run behind the frontages (raccoons, rooftop parrots).
  * SOUTH-EAST  - the CANAL DOCKS: Canal Street hugs the north bank from the park to Pier Street
    (riverside cafes in the west, Old Docks warehouses + a small marina in the east). South of the
    water, Harbor Yards: gravel work yards, Wharf Alley, Crate Alley, the open Service Yard.
  * SOUTH-WEST  - WILLOWBROOK suburbs across the canal: curving Orchard Drive, a crescent with a
    common green, four cul-de-sacs with deep backyards and a hidden canal-bank trail.
  * NORTH-WEST  - NORTHSIDE residential (townhouses, school yard) between park and zoo: leaning,
    curving streets with offset T's (Aspen / Juniper), Lark Court, and two hilltop courts in the
    far corner joined only by a footpath (the ring deliberately breaks there).

Loops: a broken outer ring (Ridge Rd - Keeper's Lane - Pier St - Yard Lane - Orchard Dr - Meadow Rd)
links neighbouring habitats so captures can be chained; spokes (Founders, Zoo Ave, Harbor Rd,
Canal St -> Willow Ln) give short return trips; Elm Street loops round the Hub Green and runs a
parallel back route Hub -> Zoo Row -> downtown; Canal Street is the waterfront back route east.
The canal (one gentle meander, west -> east-south-east) is crossed only by five bridges -
Meadow, Willow, Harbor, Dock, Pier - spaced ~150 m apart: real chokepoints for chases.

Sightlines: from the shop plaza you see the Hub Green and straight up Zoo Avenue to the zoo gate;
Founders frames downtown to the east; Harbor Road shows the bridge and the dock cranes to the south.
Exits: Founders west + east (main), Hillcrest Road north, Harbor Road south.

Animal spread: big/slow animals stay near the zoo and Zoo Row; climbers go to park trees and
downtown roofs; water animals follow the canal to the docks/marina and the park pond; burrowers and
small animals end up in the suburbs' yards, the service yard crates and the alleys.

Conventions used here: PLAYER_SPAWN.heading_deg is measured counter-clockwise from +X (east),
like the rest of the layout math (0 = east, 90 = north).
"""

# =============================================================================== NODES
NODES = {
    # --- exits
    "X_W": dict(pos=(-420, 172), exit=True),
    "X_E": dict(pos=(420, 10), exit=True),
    "X_N": dict(pos=(42, 420), exit=True),
    "X_S": dict(pos=(62, -420), exit=True),

    # --- Founders Avenue (west -> hub -> east)
    "FW1": (-318, 165),     # x Meadow Rd
    "FN1": (-195, 156),     # x Birch St
    "FP": (-112, 108),      # x Willow Ln
    "FA": (-88, 85),        # x Kibble Alley
    "FN2": (-62, 60),       # x Elm St
    "HUB": (0, 0),          # THE HUB: Founders / Zoo Ave / Harbor Rd
    "FE1": (95, 6),         # x Cooper St
    "FE2": (170, 22),       # x Dock Rd
    "FE3": (250, 33),       # x Clock St (north)
    "FE4": (290, 31),       # x Mercer St (south)
    "FE5": (334, 24),       # x Pier St

    # --- hub north / zoo approach
    "EA": (-20, 88),        # Elm x Aspen
    "ZE": (38, 84),         # Zoo Ave x Elm
    "CE": (100, 80),        # Elm x Cooper
    "ZG": (75, 135),        # zoo gate junction: Zoo Ave / Menagerie / Hillcrest

    # --- downtown
    "DM": (165, 143),       # Menagerie x Dock
    "DA": (168, 80),        # Dock x Elm / Tanner Alley
    "DS": (174, -12),       # Dock x Rope Alley
    "DB": (180, -46),       # Dock x Bay
    "MW1": (266, 141),      # Menagerie x Clock
    "MA2": (258, 89),       # Clock x Tanner Alley
    "MW2": (325, 128),      # Menagerie / Pier / Keeper's Lane
    "PA": (330, 81),        # Pier x Tanner Alley
    "PS": (337, -7),        # Pier x Rope Alley
    "MS": (291, -14),       # Mercer x Rope Alley
    "MB": (290, -48),       # Mercer x Bay
    "PB": (340, -42),       # Pier x Bay

    # --- canal north bank
    "WL1": (-130, -84),     # Willow x Canal St
    "CK": (-92, -77),       # Canal St x Kibble Alley
    "CS1": (2, -58),        # Harbor Rd x Canal St
    "WC": (100, -80),       # Canal St x Cooper
    "WD": (190, -112),      # Canal St x Dock Rd
    "WN": (268, -150),      # Canal St x Mercer
    "WP": (336, -168),      # Canal St x Pier

    # --- harbor yards (south of canal, east)
    "HW": (20, -165),       # Harbor x Wharf Alley
    "DW": (185, -200),      # Dock x Wharf Alley
    "HM": (32, -245),       # Harbor x Mill / Orchard
    "DMill": (184, -250),   # Dock x Mill
    "CA1": (250, -262),     # Mill x Crate Alley
    "PM": (318, -268),      # Pier / Mill / Yard Lane
    "CA2": (238, -338),     # Yard Lane x Crate Alley
    "HY": (50, -330),       # Harbor x Yard Lane

    # --- Willowbrook suburbs (south of canal, west)
    "WS1": (-133, -190),    # Willow x Robin Ct
    "OW": (-138, -255),     # Orchard x Willow
    "MO": (-290, -250),     # Meadow x Orchard
    "OF": (-215, -262),     # Orchard x Fox Ct
    "OC1": (-178, -262),    # Orchard x Pine Crescent (west)
    "OC2": (-92, -268),     # Orchard x Pine Crescent (east)
    "OA": (-30, -268),      # Orchard x Acorn Ct
    "FC": dict(pos=(-212, -182), culdesac=True),
    "RC": dict(pos=(-30, -188), culdesac=True),
    "AC": dict(pos=(-24, -325), culdesac=True),
    "MC": dict(pos=(-292, -325), culdesac=True),

    # --- Northside
    "LW": (-312, 245),      # Meadow x Linden
    "LB": (-200, 248),      # Linden x Birch
    "LL": (-128, 236),      # Linden x Lark Ct
    "LA": (-52, 250),       # Linden x Aspen
    "HL": (55, 262),        # Hillcrest x Linden
    "RB": (-215, 318),      # Ridge x Birch
    "LJ": (-8, 256),        # Linden x Juniper Way (offset T vs Aspen)
    "RJ": (-22, 332),       # Ridge x Juniper Way
    "HR": (48, 336),        # Hillcrest / Ridge / Keeper's Lane
    "LC": dict(pos=(-128, 168), culdesac=True),
    "MN": dict(pos=(-310, 300), culdesac=True),   # Meadow Rd north end (hilltop court)
    "RW": dict(pos=(-258, 326), culdesac=True),   # Ridge Rd west end
}

# =============================================================================== ROADS
ROADS = [
    # ---------------------------------------------------------------- main
    dict(id="Founders", name="Founders Avenue", cls="main",
         path=["X_W", "FW1", "FN1", "FP", "FA", "FN2", "HUB", "FE1", "FE2", "FE3", "FE4", "FE5", "X_E"]),
    dict(id="ZooAve", name="Zoo Avenue", cls="main", path=["HUB", "ZE", "ZG"]),
    dict(id="HarborRd", name="Harbor Road", cls="main", path=["HUB", "CS1", "HW", "HM", "HY", "X_S"]),

    # ---------------------------------------------------------------- secondary
    dict(id="Menagerie", name="Menagerie Way", cls="secondary",
         path=["ZG", (120, 146), "DM", "MW1", "MW2"]),
    dict(id="Hillcrest", name="Hillcrest Road", cls="secondary",
         path=["ZG", (66, 200), "HL", "HR", "X_N"]),
    dict(id="Meadow", name="Meadow Road", cls="secondary",
         path=["MN", "LW", "FW1", (-330, 90), (-318, 10), (-296, -60), (-290, -100), (-288, -180), "MO", "MC"]),
    dict(id="Willow", name="Willow Lane", cls="secondary",
         path=["FP", (-132, 35), (-136, -30), "WL1", "WS1", "OW"]),
    dict(id="DockRd", name="Dock Road", cls="secondary",
         path=["DM", "DA", "FE2", "DS", "DB", "WD", "DW", "DMill"]),
    dict(id="BaySt", name="Bay Street", cls="secondary", path=["DB", (235, -56), "MB", "PB"]),
    dict(id="PierSt", name="Pier Street", cls="secondary",
         path=["MW2", "PA", "FE5", "PS", "PB", (343, -105), "WP", "PM"]),
    dict(id="MillRd", name="Mill Road", cls="secondary", path=["HM", (110, -240), "DMill", "CA1", "PM"]),
    dict(id="Orchard", name="Orchard Drive", cls="secondary",
         path=["MO", "OF", "OC1", "OW", "OC2", "OA", "HM"]),

    # ---------------------------------------------------------------- side
    dict(id="ElmSt", name="Elm Street", cls="side", path=["FN2", "EA", "ZE", "CE", "DA"]),
    dict(id="AspenLn", name="Aspen Lane", cls="side", path=["EA", (-30, 150), (-45, 205), "LA"]),
    dict(id="JuniperWy", name="Juniper Way", cls="side", path=["LJ", (-12, 295), "RJ"]),
    dict(id="LindenSt", name="Linden Street", cls="side",
         path=["LW", (-262, 250), "LB", "LL", "LA", "LJ", "HL"]),
    dict(id="RidgeRd", name="Ridge Road", cls="side",
         path=["HR", "RJ", (-105, 320), "RB", "RW"]),
    dict(id="BirchSt", name="Birch Street", cls="side", path=["FN1", (-204, 200), "LB", "RB"]),
    dict(id="LarkCt", name="Lark Court", cls="side", path=["LL", (-130, 200), "LC"]),
    dict(id="KeeperLn", name="Keeper's Lane", cls="alley",
         path=["HR", (105, 350), (190, 345), (255, 346), (305, 320), (334, 265), (334, 190), "MW2"]),
    dict(id="CanalSt", name="Canal Street", cls="side",
         path=["WL1", "CK", (-40, -66), "CS1", (50, -68), "WC", (150, -95), "WD", "WN", "WP"]),
    dict(id="CooperSt", name="Cooper Street", cls="side", path=["CE", "FE1", "WC"]),
    dict(id="ClockSt", name="Clock Street", cls="side", path=["FE3", "MA2", "MW1"]),
    dict(id="MercerSt", name="Mercer Street", cls="side", path=["FE4", "MS", "MB", (282, -100), "WN"]),
    dict(id="YardLn", name="Yard Lane", cls="side",
         path=["PM", (300, -310), (265, -333), "CA2", (150, -336), "HY"]),
    dict(id="FoxCt", name="Fox Court", cls="side", path=["OF", (-214, -222), "FC"]),
    dict(id="RobinCt", name="Robin Court", cls="side", path=["WS1", (-80, -196), "RC"]),
    dict(id="PineCres", name="Pine Crescent", cls="side",
         path=["OC1", (-182, -305), (-150, -338), (-110, -332), "OC2"]),
    dict(id="AcornCt", name="Acorn Court", cls="side", path=["OA", (-28, -298), "AC"]),

    # ---------------------------------------------------------------- alleys
    dict(id="KibbleAly", name="Kibble Alley", cls="alley", path=["CK", (-96, -10), (-100, 50), "FA"]),
    dict(id="TannerAly", name="Tanner Alley", cls="alley", path=["DA", "MA2", "PA"]),
    dict(id="RopeAly", name="Rope Alley", cls="alley", path=["DS", "MS", "PS"]),
    dict(id="WharfAly", name="Wharf Alley", cls="alley", path=["HW", (100, -178), "DW"]),
    dict(id="CrateAly", name="Crate Alley", cls="alley", path=["CA1", "CA2"]),
]

# =============================================================================== WATER / TERRAIN
RIVER = dict(name="Breed Canal", width=22, path=[
    (-440, -152), (-340, -130), (-240, -140), (-150, -128), (-60, -112), (30, -108),
    (110, -125), (190, -158), (270, -190), (350, -205), (440, -212),
])

PONDS = [
    dict(id="ParkPond", center=(-205, -30), radii=[44, 36, 30, 40, 48, 42, 34, 38, 46, 40], rot=0.3, bank=3.0),
]

HILLS = [
    dict(id="LookoutHill", center=(-240, 85), radius=50, height=9, squash=(1.0, 0.8), rot=0.2),
]

# =============================================================================== DISTRICTS
def _inset(poly, d=1.5):
    """Shrink a polygon by d metres (mitred). Districts are authored along shared road centerlines;
    the inset leaves a ~3 m seam so neighbouring zoning polygons never overlap."""
    import math
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sgn = 1.0 if area > 0 else -1.0
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        dx, dy = dx / L, dy / L
        nx, ny = -dy * sgn, dx * sgn
        lines.append(((x0 + nx * d, y0 + ny * d), (dx, dy)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-6:
            out.append((round(q[0], 2), round(q[1], 2)))
            continue
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((round(p[0] + u[0] * t, 2), round(p[1] + u[1] * t, 2)))
    return out


_DISTRICTS_RAW = [
    dict(id="PetShopCorner", name="Pet Shop Corner", kind="petshop", label_at=(-62, 40), poly=[
        (-130, -84), (-136, -30), (-132, 35), (-112, 108), (-62, 60), (-20, 88), (38, 84),
        (100, 80), (95, 6), (100, -80), (50, -68), (2, -58), (-40, -66), (-92, -77)]),
    dict(id="CentralPark", name="Central Park", kind="park", label_at=(-178, 70), poly=[
        (-360, 168), (-318, 165), (-195, 156), (-112, 108), (-132, 35), (-136, -30), (-130, -84),
        (-134, -109), (-150, -112), (-200, -118), (-250, -124), (-300, -119), (-360, -118)]),
    dict(id="Northside", name="Northside", kind="residential", label_at=(-140, 280), poly=[
        (-360, 168), (-360, 360), (40, 360), (48, 336), (55, 262), (62, 195), (75, 135), (38, 84),
        (-20, 88), (-62, 60), (-112, 108), (-195, 156), (-318, 165)]),
    dict(id="ZooDistrict", name="Zoo", kind="zoo", label_at=(200, 300), poly=[
        (75, 135), (120, 146), (165, 143), (266, 141), (325, 128), (360, 126), (360, 360),
        (40, 360), (48, 336), (55, 262), (62, 195)]),
    dict(id="ZooRow", name="Zoo Row", kind="market", label_at=(115, 112), poly=[
        (38, 84), (75, 135), (120, 146), (165, 143), (168, 80), (100, 80)]),
    dict(id="Downtown", name="Downtown", kind="downtown", ground="paved", label_at=(300, 62), poly=[
        (100, 80), (168, 80), (165, 143), (266, 141), (325, 128), (360, 126), (360, -40),
        (340, -42), (290, -48), (235, -56), (180, -46), (174, -12), (170, 22), (95, 6)]),
    dict(id="CanalQuarter", name="Canal Quarter", kind="riverside", label_at=(140, -45), poly=[
        (95, 6), (170, 22), (174, -12), (180, -46), (190, -112), (190, -143), (150, -127),
        (110, -113), (100, -110), (100, -80)]),
    dict(id="OldDocks", name="Old Docks", kind="service", label_at=(255, -95), poly=[
        (180, -46), (235, -56), (290, -48), (340, -42), (360, -40), (360, -190), (300, -180),
        (250, -167), (190, -143), (190, -112)]),
    dict(id="HarborYards", name="Harbor Yards", kind="service", ground="gravel", label_at=(210, -300), poly=[
        (24, -126), (60, -130), (110, -139), (150, -153), (190, -173), (230, -190), (270, -205),
        (310, -213), (360, -220), (356, -275), (338, -325), (300, -360), (56, -360), (50, -330),
        (32, -245), (20, -165)]),
    dict(id="Willowbrook", name="Willowbrook", kind="suburb", label_at=(-215, -300), poly=[
        (-360, -150), (-300, -150), (-240, -155), (-180, -147), (-130, -139), (-60, -127),
        (0, -123), (22, -125), (20, -165), (32, -245), (50, -330), (56, -360), (-360, -360)]),
]
DISTRICTS = [dict(d, poly=_inset(d["poly"], 1.5)) for d in _DISTRICTS_RAW]

# =============================================================================== LANDMARKS
_SHOP = [(-31.6, -4.5), (-18.0, -24.1), (-34.4, -35.5), (-48.0, -15.9)]          # 24 x 20, faces the Hub
_EXPANSION = [(-50.9, -11.8), (-31.5, -39.6), (-38, -57), (-84, -65), (-86, -30)]  # ~48 x 45 behind the shop

LANDMARKS = {
    "PetShop": dict(
        name="Pet Shop", center=(-33, -20), poly=_SHOP, facing=(0.82, 0.57), road="Founders",
        expansion_poly=_EXPANSION,
        notes="Corner shop facing the Hub across a small plaza; expansion plot behind it reaches "
              "Canal Street (water view) and Kibble Alley (rear deliveries)."),
    "Zoo": dict(
        name="City Zoo", center=(200, 245),
        poly=[(125, 160), (200, 157), (262, 163), (292, 185), (304, 240), (296, 292), (262, 318),
              (200, 328), (140, 326), (108, 305), (95, 260), (96, 212), (102, 188)],
        entrance=(112, 174), entrance_facing=(-0.62, -0.78),
        incident_at=(205, 157),
        notes="Gate on the chamfered SW corner, forecourt opens onto the Zoo Ave / Menagerie / "
              "Hillcrest junction. Breach on the south fence, facing downtown and the Hub."),
    "CentralPark": dict(
        name="Central Park", center=(-220, 20),
        poly=[(-300, 140), (-205, 142), (-150, 112), (-140, 100), (-143, 40), (-147, -30),
              (-142, -92), (-150, -106), (-200, -112), (-250, -118), (-280, -112), (-280, -95),
              (-292, -30), (-304, 70)],
        notes="Lookout hill NW, pond centre, Great Lawn east facing the pet-shop block."),
    "ServiceYard": dict(
        name="Service Yard", center=(105, -287),
        poly=[(62, -256), (148, -254), (148, -320), (62, -320)],
        notes="Open gravel work yard: containers, crate stacks, a gantry; fronts Harbor Rd."),
    "TownSquare": dict(
        name="Town Square", center=(218, 59),
        poly=[(192, 44), (244, 46), (244, 74), (192, 72)],
        notes="Clock tower + fountain; Founders Ave on the south, Clock St east, Tanner Alley north."),
    # ---- optional extras
    "Lookout": dict(
        name="Lookout", center=(-240, 85),
        poly=[(-250, 75), (-230, 75), (-230, 95), (-250, 95)],
        notes="Gazebo / telescope on top of Lookout Hill - sightline over the whole city."),
    "Marina": dict(
        name="Marina", center=(300, -186), allow_water=True,
        poly=[(280, -175), (320, -180), (320, -200), (280, -194)],
        notes="Boat slips and a boathouse on the Old Docks quay; penguins and otters."),
    "SchoolYard": dict(
        name="School", center=(8, 177),
        poly=[(-16, 150), (32, 150), (34, 205), (-18, 205)],
        notes="Northside school with a fenced yard; small-animal hiding in the playground."),
}

# =============================================================================== PATHS
def _ring(cx, cy, r, n=14, squash=(1.0, 1.0)):
    import math
    pts = [(round(cx + math.cos(2 * math.pi * k / n) * r * squash[0], 1),
            round(cy + math.sin(2 * math.pi * k / n) * r * squash[1], 1)) for k in range(n)]
    return pts + [pts[0]]


PATHS = [
    dict(id="PondLoop", kind="park", width=3.0, path=_ring(-205, -30, 56, n=16, squash=(1.0, 0.95))),
    dict(id="ParkEastGate", kind="park", width=3.5, path=[(-144, -8), (-160, -10), (-158, -20)]),
    dict(id="HillTrail", kind="trail", width=2.5,
         path=[(-205, 26), (-215, 45), (-232, 60), (-246, 72), (-240, 85)]),
    dict(id="NorthGate", kind="park", width=3.0, path=[(-175, 128), (-200, 112), (-222, 100), (-240, 85)]),
    dict(id="MeadowGate", kind="park", width=3.0, path=[(-298, 20), (-275, 12), (-260, -5)]),
    dict(id="GreatLawnWalk", kind="park", width=3.0, path=[(-160, -10), (-162, 40), (-172, 80), (-190, 108)]),
    dict(id="Riverwalk_Park", kind="riverwalk", width=3.5,
         path=[(-280, -114), (-240, -124), (-200, -116), (-150, -110), (-140, -106)]),
    dict(id="Riverwalk_Hub", kind="riverwalk", width=3.5,
         path=[(-120, -104), (-60, -96), (-12, -92)]),
    dict(id="Riverwalk_Quarter", kind="riverwalk", width=3.5,
         path=[(14, -93), (60, -98), (110, -110), (150, -124), (176, -134)]),
    dict(id="Riverwalk_Docks", kind="riverwalk", width=3.5,
         path=[(200, -143), (240, -158), (276, -172)]),
    dict(id="CanalTrail_West", kind="trail", width=2.5,
         path=[(-276, -152), (-240, -157), (-200, -151), (-148, -143)]),
    dict(id="CanalTrail_East", kind="trail", width=2.5,
         path=[(-118, -139), (-60, -129), (0, -125)]),
    dict(id="ShopPlaza", kind="plaza", width=8.0, path=[(-26, -6), (-16, -14), (-14, -22)]),
    dict(id="ShopToPark", kind="trail", width=2.5,
         path=[(-50, -8), (-70, -5), (-92, -2), (-112, 0), (-130, -2)]),
    dict(id="RidgeSteps", kind="trail", width=2.5,
         path=[(-126, 244), (-122, 270), (-118, 295), (-112, 316)]),
    dict(id="HilltopPath", kind="trail", width=2.5,
         path=[(-298, 304), (-285, 316), (-270, 324)]),
    dict(id="HubGreenWalk", kind="plaza", width=3.0, path=[(-30, 56), (-8, 52), (10, 62)]),
    dict(id="ZooForecourt", kind="plaza", width=10.0, path=[(88, 154), (100, 165), (110, 173)]),
    dict(id="SquareCross", kind="plaza", width=4.0, path=[(194, 46), (218, 59), (242, 72)]),
]

# =============================================================================== NO_BUILD
NO_BUILD = [
    dict(id="HubGreen", reason="Tiny village green inside the Hub knot (big tree, benches, statue)",
         poly=[(-6, 24), (-38, 58), (-20, 74), (18, 70)]),
    dict(id="ShopPlazaNB", reason="Pet-shop corner plaza: stalls, customers, spawn point",
         poly=[(-31.6, -4.5), (-22, -4), (-12, -11), (-12, -22), (-18, -24.1)]),
    dict(id="ZooForecourtNB", reason="Zoo entrance forecourt (ticket booths, crowd space)",
         poly=[(84, 152), (114, 155), (125, 160), (100, 188), (86, 172)]),
    dict(id="DocksideLot", reason="Hidden open lot between Bay St and the quay (fenced, overgrown)",
         poly=[(205, -75), (250, -75), (255, -115), (212, -110)]),
    dict(id="CrescentCommons", reason="Shared green in the heart of Pine Crescent (swings, hedge maze); houses ring it",
         poly=[(-164, -288), (-112, -288), (-118, -314), (-148, -322), (-164, -306)]),
    dict(id="CooperCourtyard", reason="Hidden courtyard garden inside the Canal Quarter block (back gates only)",
         poly=[(124, -16), (149, -16), (150, -62), (124, -62)]),
    dict(id="ZooBackLot", reason="Zoo back-of-house strip along Keeper's Lane (feed sheds, trucks)",
         poly=[(300, 185), (318, 190), (318, 290), (300, 296)]),
]

# =============================================================================== GAMEPLAY HINTS
ANIMAL_ZONES = [
    dict(id="ZooBreach", center=(205, 175), radius=45, habitat="zoo grounds / breach",
         animals=["elephant", "rhino", "zebra", "lion"], notes="Big animals linger near the broken fence - team captures."),
    dict(id="ZooRowGiraffes", center=(115, 110), radius=40, habitat="shop awnings / street trees",
         animals=["giraffe", "ostrich"], notes="Tall animals browsing Zoo Row trees, visible from the Hub."),
    dict(id="HubGreenStarter", center=(-10, 50), radius=25, habitat="village green",
         animals=["rabbit", "guinea pig", "peacock"], notes="Tutorial catches right outside the shop."),
    dict(id="ParkCanopy", center=(-260, 40), radius=45, habitat="tree clusters",
         animals=["monkey", "lemur", "sloth"], notes="Monkeys in the woods between hill and pond."),
    dict(id="PondShore", center=(-205, -30), radius=55, habitat="pond / reeds",
         animals=["flamingo", "capybara", "duck", "turtle"], notes="Flamingos wade, capybaras graze the banks."),
    dict(id="HillGoats", center=(-240, 85), radius=40, habitat="hill slopes",
         animals=["mountain goat", "alpaca"], notes="Goats around the lookout."),
    dict(id="DowntownRoofs", center=(260, 40), radius=70, habitat="rooftops / alleys",
         animals=["parrot", "raccoon", "red panda"], notes="Parrots on the roofline, raccoons in Tanner/Rope alleys."),
    dict(id="MarinaWater", center=(300, -190), radius=40, habitat="canal / boat slips",
         animals=["penguin", "otter", "sea lion"], notes="Penguins on the pontoons, otters under the Pier St bridge."),
    dict(id="CanalReeds", center=(-60, -118), radius=50, habitat="canal edge",
         animals=["pelican", "beaver"], notes="Between Willow and Harbor bridges, along the riverwalk."),
    dict(id="YardLizards", center=(150, -280), radius=70, habitat="warehouses / crates",
         animals=["komodo dragon", "iguana", "meerkat"], notes="Lizards bask on the gravel, meerkats burrow under crates."),
    dict(id="SuburbYards", center=(-180, -220), radius=70, habitat="backyards / hedges",
         animals=["kangaroo", "tortoise", "giraffe calf"], notes="Kangaroos hop between backyards; giraffe peeks over fences."),
    dict(id="NorthsideGardens", center=(-110, 300), radius=60, habitat="gardens / school yard",
         animals=["porcupine", "fox", "hedgehog"], notes="Quieter late-game zone."),
]

HIDING_SPOTS = [
    dict(id="UnderWillowBridge", at=(-130, -126), notes="Ledge under Willow Lane bridge."),
    dict(id="UnderHarborBridge", at=(12, -108), notes="Ledge under Harbor Road bridge - close to the shop."),
    dict(id="UnderDockBridge", at=(187, -158), notes="Under Dock Road bridge."),
    dict(id="KibbleAlleyEnd", at=(-98, 30), notes="Bins and a fence gap halfway up Kibble Alley."),
    dict(id="TannerDumpsters", at=(210, 82), notes="Dumpsters behind Town Square."),
    dict(id="RopeAlleyFireEscape", at=(310, -10), notes="Fire escapes behind the high street."),
    dict(id="ContainerStack", at=(120, -300), notes="Gap between stacked containers in the Service Yard."),
    dict(id="CrateAlleyShed", at=(247, -300), notes="Open shed off Crate Alley."),
    dict(id="DocksideLotWeeds", at=(230, -95), notes="Overgrown fenced lot."),
    dict(id="FoxCourtBackyards", at=(-245, -195), notes="Hedges behind the Fox Court houses."),
    dict(id="PondReeds", at=(-160, -50), notes="Reed bed on the east bank of the pond."),
    dict(id="HillThicket", at=(-275, 110), notes="Thicket on the back of Lookout Hill."),
    dict(id="ZooBackLotSheds", at=(310, 240), notes="Feed sheds along Keeper's Lane."),
    dict(id="CrescentHedge", at=(-135, -300), notes="Hedge maze in the Crescent Commons."),
]

PLAYER_SPAWN = dict(at=(-19, -11), heading_deg=35.0)

# =============================================================================== VIEWS
VIEWS = {
    "overview": ((430, -560, 470), (-20, 10, 0), 24),
    "petshop": ((38, -98, 62), (-30, 2, 0), 30),
    "downtown": ((365, -95, 62), (220, 60, 0), 28),
    "zoo": ((10, 62, 55), (150, 215, 0), 26),
    "park": ((-110, -85, 60), (-220, 40, 0), 26),
    "canal": ((40, -70, 20), (200, -165, 0), 30),
    "service": ((10, -170, 60), (170, -290, 0), 26),
    "suburb": ((-40, -200, 45), (-180, -285, 0), 30),
}
