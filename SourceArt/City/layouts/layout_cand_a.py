"""Candidate A - "Canal Town".

CONCEPT
-------
The Willow Canal (22 m) is the spine of the town. It enters from the west edge (upstream) right under
the fence of the Willowbrook Zoo, swings south-east through the middle of town and leaves through the
south-east corner past the docks. Everything is organised around it and around the Central Bridge.

* NORTH BANK, CENTRE - DOWNTOWN. Canal Street (main) is the waterfront avenue; Main Street (main)
  meets it at the foot of the Central Bridge. Downtown fans out from the bridgehead: Mill Street
  leans north-west, Bell Street and Ferry Street lean north-east, Union Street bows across them as a
  crescent, so the three downtown blocks are trapezoids, not a grid. The TOWN SQUARE sits between
  Canal Street and the water at the north bridgehead - the clock tower is the first thing you see
  crossing from the pet shop. Each downtown block has a back alley (Lantern Alley with the hidden
  Lantern Court, the dog-leg Cobbler Alley, Tinker Alley). The Riverwalk promenade runs along both
  quays. Menagerie Market (market stalls on Market Lane) links downtown to the zoo gate.
* SOUTH BANK, CENTRE - MAPLE CORNER (pet shop) + CENTRAL PARK. Directly across the bridge, Maple
  Street (secondary, the shop street) peels off west past the Bridge Corner shops. The PET SHOP faces
  north across Maple Street onto Central Park, the canal and the downtown skyline: one bridge from
  downtown, ~70 m from the map centre, impossible to lose. An L-shaped expansion reserve (~1900 m2)
  wraps the side and back of the shop and reaches Kennel Lane (back alley) for deliveries. Across Main
  Street the Fairground Lot is an open chase / gathering space. Central Park fills the land between
  Maple Street and the water: Swan Pond, Picnic Hill, lawns, loop path and the south Riverwalk; the
  Boathouse sits opposite on the north quay.
* UPSTREAM / NORTH-WEST - WILLOWBROOK ZOO. The zoo fills the north-west corner between Canal Street
  (the west exit road) and Zoo Parkway. Its gate faces Canal Street; the breach (incident point) is the
  south-east corner at Zoo Corner, facing the Zoo Bridge, the water and the town. Escaped animals fan
  out three ways: over the Zoo Bridge into the park and Willow Bend, along Canal Street through the
  Menagerie Market into downtown, and down the quays / Riverwalk toward the docks. Zoo Landing, a
  reedy meadow between the fence and the water, is the first escape pocket.
* DOWNSTREAM / EAST - CANAL WORKS + THE WHARF (service). Warehouses, a cannery and the Dock Yard
  straddle the canal between the Ferry Bridge and the Dock Bridge. Cannery Row runs along the north
  quay from the Ferry Bridge and loops back to Canal Street; Rope Alley cuts through to it; Net Alley
  threads the Wharf on the south bank; Wharf Road follows the south quay.
* NEIGHBOURHOODS. Elm Heights (north) between Union Street and Zoo Parkway with Elm Court; Hillcrest
  (north-east) inside the sweeping Hillcrest Drive with Orchard Lane, Larch Court and the Lookout hill
  in the corner; Willow Bend (west suburb) on canal-side Kingfisher Lane and Heron / Wren Courts;
  Collar Row and Pinecrest behind the pet shop; Meadowbrook (south suburb) on Daisy, Clover and Fawn
  Courts; Larkspur (south-east) on Larkspur Lane inside Wharf Road; Meadow Edge along the south rim;
  and the wild Willow Woods in the south-west corner for the big animals.

ROAD STRUCTURE
--------------
Two main roads cross at the Central Bridge (Canal Street W-E, Main Street N-S) and carry the four
exits (west past the zoo, north, east past the docks, south). A secondary loop rings the canal:
Canal Street -> Zoo Bridge -> Willow Road -> Southside Parkway -> Dock Bridge -> Canal Street, cut in
the middle by Main Street, so every district sits on a loop; Willow Road continues as the southern
arc around Meadowbrook. Staggered T-junctions (Zoo Parkway / Hillcrest Drive on Main Street) break
the outer ring. Bridges: Zoo Bridge (secondary), Central Bridge (main), Ferry Bridge (narrow side
street), Dock Bridge (secondary) - all near-perpendicular to the canal.

SIGHTLINES
----------
Pet shop door -> park lawn -> canal -> Town Square clock tower. South end of the Central Bridge ->
straight up Main Street to the northern hills. Zoo Corner -> down the canal toward downtown.
Lookout hill -> down the canal corridor toward the docks.

NOTE: district polygons are authored along shared road centrelines and pulled in 1.5 m by _inset()
(the validator counts exact shared edges as overlap); canal-side districts stop at the quay lines
QN / QS (16 m from the canal centreline).
"""

# =============================================================================== NODES
NODES = {
    # ---- exits
    "XW": dict(pos=(-420, 210), exit=True),
    "XN": dict(pos=(52, 420), exit=True),
    "XE": dict(pos=(420, -48), exit=True),
    "XS": dict(pos=(85, -420), exit=True),
    # ---- north bank: waterfront + downtown
    "ZC": (-212, 162),     # Zoo Corner: Canal St x Willow Rd (Zoo Bridge) x Zoo Pkwy
    "MKC": (-155, 133),    # Canal St x Market Ln
    "MILL": (-97, 111),    # Canal St x Mill St
    "MN": (5, 100),        # Canal St x Main St (north bridgehead)
    "BELL": (88, 87),      # Canal St x Bell St
    "FN": (160, 58),       # Canal St x Ferry St
    "CR0": (232, 22),      # Canal St x Rope Alley
    "DN": (292, -8),       # Canal St x Dock Bridge Rd x Hillcrest Dr
    "CE": (368, -35),      # Canal St x Cannery Row (east end of the docks loop)
    "ZPU": (-203, 216),    # Zoo Pkwy x Union St
    "MKU": (-152, 196),    # Union St x Market Ln
    "MU": (-110, 184),     # Union St x Mill St
    "LA0": (-102, 148),    # Mill St x Lantern Alley
    "LA1": (7, 143),       # Main St x Lantern Alley
    "MAU": (11, 186),      # Main St x Union St
    "CA0": (97, 128),      # Bell St x Cobbler Alley
    "CA1": (50, 183),      # Union St x Cobbler Alley
    "BU": (112, 172),      # Bell St x Union St
    "TF": (171, 110),      # Ferry St x Tinker Alley
    "FU": (182, 150),      # Ferry St x Union St
    "UH": (316, 104),      # Union St x Hillcrest Dr
    "LU": (250, 136),      # Union St x Larch Ct
    "MHM": (-122, 272),    # Zoo Pkwy x Mill St
    "ECT": (-50, 266),     # Zoo Pkwy x Elm Ct
    "MH": (22, 262),       # Main St x Zoo Pkwy (T from the west)
    "MH2": (31, 305),      # Main St x Hillcrest Dr (T from the east, staggered)
    "AC0": (80, 311),      # Hillcrest Dr x Aster Ct
    "BH": (126, 308),      # Hillcrest Dr x Bell St
    "FH": (238, 282),      # Hillcrest Dr x Ferry St
    "OB": (121, 247),      # Bell St x Orchard Ln
    "FO": (217, 232),      # Ferry St x Orchard Ln (Ferry St leans NE toward the Lookout)
    # ---- north bank: service
    "RF": (150, 30),       # Ferry St x Cannery Row (west end, just north of the Ferry Bridge)
    "RAC": (222, -20),     # Cannery Row x Rope Alley
    "DBR": (281, -60),     # Dock Bridge Rd x Cannery Row
    # ---- south bank
    "ZBS": (-260, 70),     # Willow Rd x Kingfisher Ln (south of the Zoo Bridge)
    "WR1": (-280, 6),      # Willow Rd x Park Ln x Reed Ct
    "WR2": (-288, -72),    # Willow Rd x Heron Ct x Wren Ct
    "WR3": (-272, -158),   # Willow Rd x Southside Pkwy
    "MCC": (-100, -302),   # Willow Rd x Clover Ct
    "MSS": (4, -12),       # Main St x Maple St x Riverside Dr (south bridgehead)
    "KL0": (9, -88),       # Main St x Kennel Lane
    "PINE": (14, -125),    # Main St x Pine St
    "MC": (-120, -46),     # Maple St x Collar St
    "KLC": (-121, -90),    # Collar St x Kennel Lane
    "PC": (-123, -127),    # Collar St x Pine St
    "PLM": (-160, -80),    # Maple St x Park Ln
    "SSMP": (-205, -168),  # Southside Pkwy x Maple St
    "DC0": (-165, -180),   # Southside Pkwy x Daisy Ct
    "SSC": (-126, -188),   # Southside Pkwy x Collar St
    "FWC": (-40, -198),    # Southside Pkwy x Fawn Ct
    "SSM": (30, -188),     # Southside Pkwy x Main St
    "SSF": (112, -166),    # Southside Pkwy x Ferry St
    "FS": (112, -60),      # Ferry St x Riverside Dr (south of the Ferry Bridge)
    "FC": (110, -120),     # Ferry St x Pine St x Net Alley
    "NA1": (196, -101),    # Riverside Dr x Net Alley
    "DS": (218, -128),     # Dock Bridge Rd x Riverside Dr x Southside Pkwy x Wharf Rd
    "MSM": (58, -300),     # Main St x Willow Rd x Wharf Rd
    "FLK": (118, -230),    # Ferry St x Larkspur Ln
    "FL": (122, -302),     # Ferry St x Wharf Rd
    "WLK": (316, -216),    # Wharf Rd x Larkspur Ln
    # ---- cul-de-sacs
    "ECT_E": dict(pos=(-48, 326), culdesac=True),
    "LAR_E": dict(pos=(262, 195), culdesac=True),
    "KFL_E": dict(pos=(-348, 106), culdesac=True),
    "HER_E": dict(pos=(-336, -112), culdesac=True),
    "WRN_E": dict(pos=(-218, -100), culdesac=True),
    "DAI_E": dict(pos=(-170, -238), culdesac=True),
    "CLO_E": dict(pos=(-95, -245), culdesac=True),
    "FAW_E": dict(pos=(-38, -248), culdesac=True),
}

# =============================================================================== ROADS
ROADS = [
    # ------------------------------------------------------------------ main
    dict(id="CanalSt", name="Canal Street", cls="main",
         path=["XW", (-350, 203), (-285, 191), "ZC", "MKC", "MILL", (-45, 103), "MN", (50, 95), "BELL",
               (125, 75), "FN", "CR0", "DN", "CE", "XE"]),
    dict(id="MainSt", name="Main Street", cls="main",
         path=["XN", (43, 360), "MH2", "MH", (16, 224), "MAU", "LA1", "MN", "MSS", "KL0", "PINE", "SSM",
               (46, -248), "MSM", (70, -356), "XS"]),
    # ------------------------------------------------------------------ secondary
    dict(id="WillowRd", name="Willow Road", cls="secondary",
         path=["ZC", "ZBS", "WR1", "WR2", "WR3", (-245, -225), (-190, -272), "MCC", (-25, -308), "MSM"]),
    dict(id="SouthsidePkwy", name="Southside Parkway", cls="secondary",
         path=["WR3", "SSMP", "DC0", "SSC", "FWC", "SSM", (75, -178), "SSF", (165, -150), "DS"]),
    dict(id="DockBridgeRd", name="Dock Bridge Road", cls="secondary",
         path=["DS", (250, -97), "DBR", "DN"]),
    dict(id="MapleSt", name="Maple Street", cls="secondary",
         path=["MSS", (-28, -27), (-75, -32), "MC", "PLM", (-188, -120), "SSMP"]),
    dict(id="UnionSt", name="Union Street", cls="secondary",
         path=["ZPU", "MKU", "MU", (-50, 186), "MAU", "CA1", "BU", (150, 162), "FU", "LU", "UH"]),
    dict(id="ZooPkwy", name="Zoo Parkway", cls="secondary",
         path=["ZC", "ZPU", (-196, 250), (-176, 274), "MHM", "ECT", "MH"]),
    dict(id="HillcrestDr", name="Hillcrest Drive", cls="secondary",
         path=["MH2", "AC0", "BH", (180, 302), "FH", (282, 240), (306, 180), "UH", (312, 48), "DN"]),
    # ------------------------------------------------------------------ side
    dict(id="MillSt", name="Mill Street", cls="side", path=["MILL", "LA0", "MU", "MHM"]),
    dict(id="MarketLn", name="Market Lane", cls="side", path=["MKC", (-153, 165), "MKU"]),
    dict(id="BellSt", name="Bell Street", cls="side", path=["BELL", "CA0", "BU", "OB", "BH"]),
    dict(id="FerrySt", name="Ferry Street", cls="side",
         path=["FH", "FO", "FU", "TF", "FN", "RF", "FS", "FC", "SSF", "FLK", "FL"]),
    dict(id="RiversideDr", name="Riverside Drive", cls="side",
         path=["MSS", (45, -22), (85, -38), "FS", (160, -72), "NA1", "DS"]),
    dict(id="PineSt", name="Pine Street", cls="side", path=["PC", (-50, -134), "PINE", (62, -117), "FC"]),
    dict(id="CollarSt", name="Collar Street", cls="side", path=["MC", "KLC", "PC", "SSC"]),
    dict(id="ParkLn", name="Park Lane", cls="side", path=["WR1", (-232, -12), (-190, -44), "PLM"]),
    dict(id="WharfRd", name="Wharf Road", cls="side",
         path=["DS", (262, -160), (302, -196), "WLK", (325, -245), (315, -282), (268, -302), (200, -308), "FL",
               "MSM"]),
    dict(id="LarkspurLn", name="Larkspur Lane", cls="side", path=["FLK", (175, -238), (240, -232), "WLK"]),
    dict(id="CanneryRow", name="Cannery Row", cls="side",
         path=["RF", (188, 5), "RAC", "DBR", (322, -88), (360, -70), "CE"]),
    # cul-de-sacs
    dict(id="ElmCt", name="Elm Court", cls="side", path=["ECT", (-49, 298), "ECT_E"]),
    # Orchard Lane drops off Hillcrest Drive, bends east through the orchards and ends on Ferry St
    dict(id="OrchardLn", name="Orchard Lane", cls="side",
         path=["AC0", (77, 276), (90, 252), "OB", (170, 246), "FO"]),
    dict(id="LarchCt", name="Larch Court", cls="side", path=["LU", (256, 165), "LAR_E"]),
    dict(id="KingfisherLn", name="Kingfisher Lane", cls="side", path=["ZBS", (-295, 84), (-325, 100), "KFL_E"]),
    dict(id="HeronCt", name="Heron Court", cls="side", path=["WR2", (-315, -90), "HER_E"]),
    dict(id="WrenCt", name="Wren Court", cls="side", path=["WR2", (-250, -88), "WRN_E"]),
    dict(id="DaisyCt", name="Daisy Court", cls="side", path=["DC0", (-167, -210), "DAI_E"]),
    dict(id="CloverCt", name="Clover Court", cls="side", path=["MCC", (-97, -272), "CLO_E"]),
    dict(id="FawnCt", name="Fawn Court", cls="side", path=["FWC", (-39, -220), "FAW_E"]),
    # ------------------------------------------------------------------ alleys
    dict(id="LanternAly", name="Lantern Alley", cls="alley", path=["LA0", (-45, 146), "LA1"]),
    dict(id="CobblerAly", name="Cobbler Alley", cls="alley", path=["CA0", (62, 132), (52, 148), "CA1"]),
    dict(id="TinkerAly", name="Tinker Alley", cls="alley", path=["CA0", (135, 119), "TF"]),
    dict(id="KennelLn", name="Kennel Lane", cls="alley", path=["KL0", (-55, -92), "KLC"]),
    dict(id="RopeAly", name="Rope Alley", cls="alley", path=["CR0", "RAC"]),
    dict(id="NetAly", name="Net Alley", cls="alley", path=["FC", (152, -114), "NA1"]),
]

# =============================================================================== WATER
RIVER = dict(name="Willow Canal", width=22,
             path=[(-440, 168), (-370, 163), (-300, 148), (-235, 118), (-170, 80), (-105, 50), (-40, 34),
                   (20, 30), (80, 24), (140, 2), (195, -38), (245, -92), (300, -148), (360, -185),
                   (440, -208)])

# quay lines 16 m from the canal centreline (5 m of dry land beyond the water edge) - used as the
# water-side boundary of the canal-side districts so no zoning / ground plate covers the water.
QN = [(-367.7, 178.8), (-294.9, 163.2), (-227.6, 132.2), (-162.6, 94.2), (-99.7, 65.1), (-37.5, 49.8),
      (21.3, 46.0), (83.6, 39.6), (147.6, 16.1), (205.7, -26.1), (256.6, -81.0), (310.1, -135.6),
      (366.3, -170.3)]
QS = [(-372.3, 147.2), (-305.1, 132.8), (-242.4, 103.8), (-177.4, 65.8), (-110.3, 34.9), (-42.5, 18.2),
      (18.7, 14.0), (76.4, 8.4), (132.4, -12.1), (184.3, -49.9), (233.4, -103.0), (289.9, -160.4),
      (353.7, -199.7)]

PONDS = [
    dict(id="SwanPond", center=(-140, 0), radii=[26, 31, 23, 28, 21, 27, 24], rot=0.3, bank=3.0),
]

HILLS = [
    dict(id="PicnicHill", center=(-222, 42), radius=32, height=6, squash=(1.0, 0.8), rot=0.45),
    dict(id="LookoutHill", center=(318, 305), radius=40, height=10, squash=(1.0, 0.85), rot=0.6),
]

# =============================================================================== DISTRICTS
def _inset(poly, d=1.5):
    """Pull a polygon in by d metres (mitred). Districts are authored along shared road centrelines;
    a small inset keeps neighbours from sharing an exact edge (the validator counts shared-edge
    samples as overlap). The gap sits under the road ribbons, so it is invisible."""
    import math
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sgn = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        x0, y0 = poly[i - 1]
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        ax, ay = x1 - x0, y1 - y0
        bx, by = x2 - x1, y2 - y1
        la, lb = math.hypot(ax, ay) or 1.0, math.hypot(bx, by) or 1.0
        na = (-ay / la * sgn, ax / la * sgn)
        nb = (-by / lb * sgn, bx / lb * sgn)
        mx, my = na[0] + nb[0], na[1] + nb[1]
        lm = math.hypot(mx, my)
        if lm < 1e-6:
            mx, my, lm = na[0], na[1], 1.0
        mx, my = mx / lm, my / lm
        k = d / max(mx * na[0] + my * na[1], 0.35)
        out.append((round(x1 + mx * k, 2), round(y1 + my * k, 2)))
    return out


_D = [
    # (id, name, kind, ground, raw polygon along road centrelines / quay lines)
    ("Zoo", "Willowbrook Zoo", "zoo", None,
     [(-400, 208), (-350, 203), (-285, 191), (-212, 162), (-203, 216), (-196, 250), (-176, 274), (-190, 350),
      (-400, 350)]),
    ("Market", "Menagerie Market", "market", None,
     [(-212, 162), (-155, 133), (-97, 111), (-102, 148), (-110, 184), (-152, 196), (-203, 216)]),
    ("Downtown", "Downtown", "downtown", "paved",
     [(-97, 111), (-45, 103), (5, 100), (50, 95), (88, 87), (125, 75), (160, 58), (170, 104), (182, 150),
      (150, 162), (112, 172), (50, 183), (11, 186), (-50, 186), (-110, 184), (-102, 148)]),
    ("ElmHeights", "Elm Heights", "residential", None,
     [(-203, 216), (-152, 196), (-110, 184), (-50, 186), (11, 186), (16, 224), (22, 262), (31, 305), (43, 350),
      (-190, 350), (-176, 274), (-196, 250)]),
    ("Hillcrest", "Hillcrest", "residential", None,
     [(160, 58), (232, 22), (292, -8), (368, -35), (368, 240), (296, 250), (262, 292), (258, 350), (43, 350),
      (31, 305), (22, 262), (16, 224), (11, 186), (50, 183), (112, 172), (150, 162), (182, 150), (170, 104)]),
    ("LookoutPark", "Lookout Park", "park", None,
     [(262, 292), (296, 250), (368, 240), (368, 350), (258, 350)]),
    ("Riverwalk", "Riverwalk", "riverside", None,
     [(-212, 162), (-155, 133), (-97, 111), (-45, 103), (5, 100), (50, 95), (88, 87), (125, 75), (160, 58),
      (147, 24), QN[7], QN[6], QN[5], QN[4], QN[3], QN[2]]),
    ("CanalWorks", "Canal Works", "service", "gravel",
     [(160, 58), (232, 22), (292, -8), (368, -35), (385, -40), (385, -174), QN[12], QN[11], QN[10], QN[9],
      QN[8], (147, 24)]),
    ("Bridgeside", "Bridgeside", "riverside", None,
     [(4, -12), (45, -22), (85, -38), (112, -60), QS[8], QS[7], QS[6], (4, 14)]),
    ("Wharf", "The Wharf", "service", None,
     [(112, -60), QS[8], QS[9], QS[10], QS[11], QS[12], (360, -240), (325, -245), (316, -216), (302, -196),
      (262, -160), (218, -128), (165, -150), (112, -166), (110, -120)]),
    ("MapleCorner", "Maple Corner", "petshop", None,
     [(4, -12), (-28, -27), (-75, -32), (-120, -46), (-121, -90), (-123, -127), (-50, -134), (14, -125),
      (62, -117), (110, -120), (112, -60), (85, -38), (45, -22)]),
    ("BridgeCorner", "Bridge Corner", "market", None,
     [(4, -12), (4, 14), (-34, 17), (-34, -27.6), (-28, -27)]),
    ("CentralPark", "Central Park", "park", None,
     [(-260, 70), (-280, 6), (-232, -12), (-190, -44), (-160, -80), (-120, -46), (-75, -32), (-34, -27.6),
      (-34, 17), QS[5], QS[4], QS[3], QS[2]]),
    ("WillowBend", "Willow Bend", "suburb", None,
     [(-360, 138), QS[1], QS[2], (-260, 70), (-280, 6), (-232, -12), (-190, -44), (-160, -80), (-188, -120),
      (-205, -168), (-272, -158), (-292, -180), (-360, -180)]),
    ("CollarRow", "Collar Row", "residential", None,
     [(-120, -46), (-160, -80), (-188, -120), (-205, -168), (-165, -180), (-126, -188), (-123, -127),
      (-121, -90)]),
    ("Pinecrest", "Pinecrest", "residential", None,
     [(-123, -127), (-126, -188), (-40, -198), (30, -188), (75, -178), (112, -166), (110, -120), (62, -117),
      (14, -125), (-50, -134)]),
    ("Meadowbrook", "Meadowbrook", "suburb", None,
     [(-272, -158), (-205, -168), (-165, -180), (-126, -188), (-40, -198), (30, -188), (46, -248), (58, -300),
      (-25, -308), (-100, -302), (-190, -272), (-245, -225)]),
    ("Larkspur", "Larkspur", "residential", None,
     [(30, -188), (75, -178), (112, -166), (165, -150), (218, -128), (262, -160), (302, -196), (316, -216),
      (325, -245), (315, -282), (268, -302), (200, -308), (122, -302), (58, -300), (46, -248)]),
    ("SouthEdge", "Meadow Edge", "suburb", None,
     [(-190, -272), (-100, -302), (-25, -308), (58, -300), (122, -302), (200, -308), (268, -302), (315, -282),
      (325, -245), (360, -240), (360, -360), (-180, -360), (-190, -292)]),
    ("WillowWoods", "Willow Woods", "park", None,
     [(-360, -180), (-292, -180), (-270, -225), (-235, -262), (-190, -292), (-180, -360), (-360, -360)]),
]
DISTRICTS = [dict(id=i, name=n, kind=k, ground=g, poly=_inset(p)) for i, n, k, g, p in _D]

# =============================================================================== LANDMARKS
LANDMARKS = {
    # 24 x 20 m shop lot, rotated to the Maple Street tangent, front 2.5 m behind the sidewalk. It looks
    # north across Maple Street at the park, the canal and the Town Square.
    "PetShop": dict(name="Pet Shop", center=(-48, -48.3),
                    poly=[(-60.9, -39.6), (-37.1, -37.0), (-35.0, -56.9), (-58.8, -59.5)],
                    facing=(-0.106, 0.994), road="MapleSt",
                    # L-shaped reserve: 32 x 43 m side lot + 25 x 22 m back yard (~1900 m2), reaching
                    # Kennel Lane for service access (kennels, breeding rooms, aviary, parking).
                    expansion_poly=[(-61.9, -39.7), (-93.7, -43.1), (-89.1, -85.8), (-32.7, -79.8),
                                    (-34.9, -57.9), (-59.8, -60.6)]),
    # ~150 x 135 m; south fence on Canal Street (gate), east fence on Zoo Parkway, breach at the
    # south-east chamfer facing Zoo Corner, the Zoo Bridge and the town.
    "Zoo": dict(name="Willowbrook Zoo", center=(-288, 280),
                poly=[(-348, 216), (-285, 206), (-228, 188), (-219, 215), (-214, 255), (-212, 290),
                      (-200, 348), (-348, 348)],
                entrance=(-262, 199), entrance_facing=(-0.369, -0.929), incident_at=(-224, 200)),
    "CentralPark": dict(name="Central Park", center=(-140, 15),
                        poly=[(-233, 96), (-250, 62), (-260, 22), (-240, 2), (-200, -24), (-165, -60),
                              (-130, -40), (-75, -21), (-38, -18), (-38, 15), (-45, 16), (-110, 30),
                              (-175, 62)]),
    "ServiceYard": dict(name="Dock Yard", center=(318, -120),
                        poly=[(292, -98), (330, -100), (345, -112), (340, -150), (300, -127)]),
    "TownSquare": dict(name="Town Square", center=(-37, 72),
                       poly=[(-60, 54), (-14, 54), (-14, 90), (-60, 90)]),
    # optional extras
    "Lookout": dict(name="Lookout Hill", center=(318, 305),
                    poly=[(310, 297), (326, 297), (326, 313), (310, 313)]),
    # open lot fronting Main Street, right across from the pet shop block
    "OpenLot": dict(name="Fairground Lot", center=(52, -76),
                    poly=[(22, -48), (80, -56), (82, -102), (24, -104)]),
    "Boathouse": dict(name="Boathouse", center=(-188, 115),
                      poly=[(-171, 115.1), (-178.4, 100.9), (-205, 114.9), (-197.6, 129.1)]),
}

# =============================================================================== PATHS
PATHS = [
    dict(id="RiverwalkN_W", kind="riverwalk", width=4.0,
         path=[(-165, 93), (-100.3, 63.2), (-37.7, 48.3), (-12, 50)]),
    dict(id="RiverwalkN_E", kind="riverwalk", width=4.0,
         path=[(16, 50), (50, 45.5), (83.2, 38), (128, 21)]),
    dict(id="RiverwalkS", kind="riverwalk", width=4.0,
         path=[(-232, 94), (-176.5, 67.6), (-109.7, 36.8), (-42.2, 20.2), (-14, 12)]),
    dict(id="RiverwalkSE", kind="riverwalk", width=3.5,
         path=[(18, 8), (77, 9), (124, -9)]),
    dict(id="ZooLandingPath", kind="trail", width=2.5,
         path=[(-380, 178), (-368, 177), (-296, 161), (-250, 141)]),
    dict(id="ParkLoop", kind="park", width=3.0,
         path=[(-60, -15), (-110, -28), (-160, -45), (-188, -15), (-182, 35), (-145, 52), (-95, 35),
               (-60, -15)]),
    dict(id="PicnicHillPath", kind="park", width=2.5,
         path=[(-188, -15), (-206, 14), (-222, 42)]),
    dict(id="WoodsTrail", kind="trail", width=2.0,
         path=[(-285, -190), (-315, -230), (-305, -285), (-260, -320), (-215, -312)]),
    dict(id="LookoutTrail", kind="trail", width=2.0,
         path=[(275, 262), (290, 278), (305, 292), (318, 305)]),
]

NO_BUILD = [
    dict(id="ZooLanding", reason="reedy meadow between the zoo fence and the canal - first escape pocket",
         poly=[(-400, 192), (-350, 189), (-285, 177), (-240, 158), (-250, 140), (-296, 160), (-368, 176),
               (-400, 178)]),
    dict(id="LanternCourt", reason="hidden courtyard off Lantern Alley (bins, crates, a fig tree)",
         poly=[(-60, 151), (-35, 151), (-35, 162), (-60, 162)]),
]

# =============================================================================== GAMEPLAY HINTS
ANIMAL_ZONES = [
    dict(id="ZooBreach", center=(-224, 196), radius=30, habitat="breached fence at Zoo Corner",
         animals=["mixed stampede"], notes="incident point; animals radiate over the Zoo Bridge, along "
                                           "Canal Street and down the canal"),
    dict(id="ZooLanding", center=(-310, 172), radius=40, habitat="reedy canal meadow",
         animals=["penguins", "flamingos", "capybaras"], notes="first escape pocket between fence and water"),
    dict(id="MarketStalls", center=(-150, 165), radius=40, habitat="market stalls / fruit crates",
         animals=["meerkats", "ostriches", "goats"], notes="Menagerie Market, right outside the zoo"),
    dict(id="ParkCanopy", center=(-195, 15), radius=50, habitat="park tree clusters / Picnic Hill",
         animals=["monkeys", "lemurs", "sloth"], notes="tree clumps around Picnic Hill"),
    dict(id="SwanPond", center=(-140, 0), radius=40, habitat="pond", animals=["flamingos", "pelicans", "otters"],
         notes="Swan Pond in Central Park"),
    dict(id="CanalCorridor", center=(60, 25), radius=70, habitat="canal water / quays / under bridges",
         animals=["penguins", "seals", "crocodile"], notes="the escape highway; crocodile under the Central Bridge"),
    dict(id="DowntownRoofs", center=(-10, 145), radius=70, habitat="rooftops / awnings / water tanks",
         animals=["parrots", "macaws", "toucans"], notes="downtown skyline"),
    dict(id="Alleys", center=(-45, 150), radius=35, habitat="alleys / bins", animals=["raccoons", "red pandas"],
         notes="Lantern Alley, Lantern Court, Cobbler Alley"),
    dict(id="Fairground", center=(52, -76), radius=32, habitat="open lot", animals=["ostriches", "emus"],
         notes="open chase arena right next to the pet shop - tutorial captures"),
    dict(id="Warehouses", center=(300, -90), radius=60, habitat="warehouses / containers",
         animals=["lizards", "snakes", "tortoises"], notes="Canal Works and the Dock Yard"),
    dict(id="WharfDocks", center=(200, -110), radius=45, habitat="docks / net sheds",
         animals=["sea lions", "pelicans", "otters"], notes="Net Alley and the Wharf quay"),
    dict(id="HillcrestGardens", center=(220, 190), radius=60, habitat="gardens / cul-de-sacs",
         animals=["rabbits", "peacocks", "tortoises"], notes="Hillcrest back gardens"),
    dict(id="LookoutHill", center=(318, 300), radius=40, habitat="grassy hilltop",
         animals=["goats", "llamas", "zebras"], notes="Lookout Hill"),
    dict(id="SuburbYards", center=(-110, -245), radius=70, habitat="backyards / pools / trampolines",
         animals=["giraffe", "kangaroos", "tortoise"], notes="giraffe peeking over Meadowbrook fences"),
    dict(id="WillowWoods", center=(-285, -270), radius=60, habitat="woods",
         animals=["bear", "moose", "wolves"], notes="big animals - need teamwork or tools"),
]

HIDING_SPOTS = [
    dict(id="UnderZooBridge", at=(-235, 118), notes="under the Zoo Bridge deck"),
    dict(id="UnderCentralBridge", at=(4, 30), notes="under the Central Bridge deck"),
    dict(id="UnderFerryBridge", at=(138, 3), notes="under the narrow Ferry Bridge"),
    dict(id="UnderDockBridge", at=(250, -95), notes="under the Dock Bridge"),
    dict(id="ZooLandingReeds", at=(-330, 168), notes="reeds on the canal bank below the zoo fence"),
    dict(id="Boathouse", at=(-188, 112), notes="behind the boathouse slipway"),
    dict(id="LanternCourt", at=(-48, 156), notes="hidden courtyard off Lantern Alley"),
    dict(id="CobblerBend", at=(55, 140), notes="dog-leg of Cobbler Alley"),
    dict(id="MarketLaneStalls", at=(-153, 165), notes="under the market awnings"),
    dict(id="RopeAlley", at=(227, 0), notes="between the warehouses on Rope Alley"),
    dict(id="DockYardContainers", at=(318, -125), notes="container stacks in the Dock Yard"),
    dict(id="NetAlley", at=(152, -112), notes="net sheds on Net Alley"),
    dict(id="KennelLane", at=(-80, -91), notes="behind the pet shop, Kennel Lane"),
    dict(id="PicnicHillThicket", at=(-235, 50), notes="thicket on the far side of Picnic Hill"),
    dict(id="ElmCourtBulb", at=(-48, 334), notes="end of Elm Court"),
    dict(id="HeronCourtBulb", at=(-340, -120), notes="end of Heron Court, backing onto the woods"),
    dict(id="TinkerAlley", at=(135, 122), notes="back doors and bins on Tinker Alley"),
    dict(id="WoodsHollow", at=(-305, -300), notes="fallen-log hollow in Willow Woods"),
    dict(id="LookoutBushes", at=(332, 318), notes="bushes behind the lookout"),
    dict(id="FairgroundCorner", at=(86, -98), notes="behind the fairground stage"),
]

# On the sidewalk in front of the pet shop door (heading 0 = rotation 0 about Z).
PLAYER_SPAWN = dict(at=(-49, -34.5), heading_deg=0)

# =============================================================================== VIEWS
VIEWS = {
    "overview": ((330, -430, 260), (-40, 30, 0), 24),
    "downtown": ((-8, -25, 24), (-20, 120, 0), 24),
    "petshop": ((-38, -2, 14), (-62, -62, 0), 26),
    "zoo": ((-170, 140, 45), (-270, 235, 0), 24),
    "park": ((-30, 30, 45), (-180, 20, 0), 26),
    "canal": ((-240, 140, 22), (20, 30, 0), 26),
    "service": ((190, -210, 60), (300, -80, 0), 26),
    "suburb": ((-60, -150, 50), (-130, -260, 0), 28),
}
