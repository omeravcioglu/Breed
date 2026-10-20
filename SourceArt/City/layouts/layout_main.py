"""Breed - FINAL city layout: "Willowbrook" (Canal Town base, grafts from Old Town Ring and Hub & Habitats).

CONCEPT
-------
Willowbrook is a small American canal town built along the Willow Canal (22 m). The canal enters at the west
edge right below the Willowbrook Zoo, swings south-east through the middle of town and leaves past the docks
in the south-east. The story runs downstream: the zoo is upstream, downtown and the pet shop face each other
across the water in the middle, and the warehouses and docks are downstream. Escaped animals follow the
water, the bridges and the streets, so the spread reads from above and from the gameplay camera.

THE HEART: TOWN SQUARE <-> PET SHOP (the bridgehead composition)
* Main Street crosses the canal on the Central Bridge. On the north quay, at the foot of the bridge, the
  TOWN SQUARE (clock tower, about 50 x 30 m) opens onto the water. A downtown block stands between it and Main
  Street, downtown faces it across Canal Street, and its north-west corner opens straight into...
* ZOO BOULEVARD (from Old Town Ring): a dead-straight avenue on one axis from the clock tower to the zoo gate,
  so the vista ends on the gate. It is lined by the Menagerie Market souvenir shops (Zoo Row) on the west and
  downtown on the east, and ends at a Zoo Forecourt plaza with visitor parking opposite.
* Directly across the bridge on the south bank, Maple Street (a calm side street) runs west from the south
  bridgehead along MAPLE GREEN, a village green (Hub Green, from Hub & Habitats). The PET SHOP sits on its south
  side about 70 m from the map centre. Its door looks north over the green, the canal and the Town Square
  clock tower, which stands on the same axis (Green Walk). The shop is one bridge from downtown, one block from
  Main Street, and the open FAIRGROUND LOT is across Main Street for tutorial and multiplayer round-ups.

DISTRICTS (19)
  North bank:  Willowbrook Zoo (zoo, NW, 193 x 152 m site) | Menagerie Market (market: Zoo Row triangle + west
               quay with the boathouse) | Downtown (downtown, paved: the fan of Zoo Boulevard / Main / Bell /
               Ferry under the Union Street crescent, plus the Town Quay with the square) | Riverwalk (riverside,
               east quay, allotments) | Elm Heights (residential, between the zoo and Main St) | Orchard Hill
               (residential, orchards between Main and Ferry) | Hillcrest (residential, east, inside the Union
               Street sweep) | Lookout Park (park, NE hill) | Canal Works (service: warehouses, Rope Alley,
               Marina quay) | Dock Yard (service, gravel: the Cannery Row loop)
  South bank:  Central Park (park: Swan Pond, Picnic Hill, Maple Green) | Maple Corner (petshop: the shop block
               and the Fairground block) | Bridge Corner (market: cafes on the south quay) | The Wharf (service:
               net sheds, Net Alley, Wharf Road quay) | Willow Bend (suburb, west, canal-side courts) |
               Pinecrest (residential, behind the shop, Garden Alley) | Meadowbrook (suburb: Pine Crescent around
               Crescent Commons) | Larkspur (residential, south-east courts) | Willow Woods (park, wild SW corner
               with Beaver Pond)
  The far south-east corner and the band outside the zoo are left unzoned as countryside (room to grow).

ROAD HIERARCHY  (about 8.8 km: main 1.76, secondary 2.43, side 3.67, alley 0.91 km; 58 intersections)
  main       Canal Street (W exit by the zoo -> waterfront -> docks -> E exit) and Main Street (N exit -> Central
             Bridge -> S exit). They cross at one junction (MN) only. Main Street bends NE north of Union Street
             and makes an S-curve south of Southside Parkway, so it is not a ruler-straight cross.
  secondary  Zoo Boulevard, Union Street (crescent over downtown that sweeps down to the docks), Zoo Parkway
             (around the zoo to Main St), Hillcrest Drive, Willow Road (Zoo Bridge -> Woods End), Southside
             Parkway, Dock Bridge Road, Wharf Road (truck exit E2 for the docks).
  side       Zoo Row, Swan Lane (Mill Bridge), Maple St, Elm St / Elm Ct, Bell St, Orchard Ln, Ferry St (Ferry
             Bridge), Larch St / Larch Ct, Cannery Row, Riverside Dr, Collar St, Pine St, Fair St, Pine Crescent,
             Park Ln, Larkspur Ln, Aster / Heather / Kingfisher / Heron / Wren courts.
  alley      Lantern Alley (from Zoo Row, across the boulevard, dog-leg to Union St), Cobbler Alley (downtown,
             continuing north through the Orchard Hill gardens), Tinker Alley, Keeper's Lane (zoo back-of-house),
             Kennel Lane (behind the pet shop), Garden Alley, Rope Alley, Net Alley. No alley meets a main road.
  BRIDGES (5, all 88-89 deg, about 115-135 m apart): Zoo Bridge (Willow Rd), Mill Bridge (Swan Lane), Central
  Bridge (Main St), Ferry Bridge (Ferry St), Dock Bridge (Dock Bridge Rd).
  EXITS (5): Canal St W and E, Main St N and S, Wharf Rd E2 (trucks to the docks).

LOOPS  (about 35 independent loops; every district sits on at least one)
  Canal loop: Canal St -> Zoo Bridge -> Willow Rd -> Southside Pkwy -> Dock Bridge -> Canal St, cut in the
  middle by Main St and by the parallel back routes Swan Lane / Collar St (west) and Ferry St (east). Short
  bridge loops connect the square, Maple Green and the shop (Mill Bridge <-> Central Bridge, Central <-> Ferry,
  Ferry <-> Dock). The zoo loop runs Zoo Boulevard -> Zoo Parkway -> Main St -> Canal St. The old perimeter ring
  is deliberately broken: Willow Road ends at the Woods End trailhead, Hillcrest Drive ends at the Lookout, and
  Larkspur does not reach Main St. Lookout Trail is a secret footpath over Lookout Hill that joins the two
  hilltop courts (Larch Ct, Hillcrest Dr end).

LANDMARK SITES
  PetShop (24 x 20 lot on Maple St, facing north) | Zoo (gate on the chamfered SE corner at the end of Zoo
  Boulevard; breach on the south fence at Zoo Corner) | CentralPark (Swan Pond, Picnic Hill, loop path) |
  ServiceYard = Container Yard (inside the Dock Yard loop) | TownSquare (north quay, clock tower on the boulevard
  axis) | extras: Lookout Point (on the town-facing shoulder of Lookout Hill), OpenLot = Fairground Lot,
  MapleGreen (the shop's front lawn), Marina (boat slips on the north quay, allow_water).
  NO_BUILD pockets: Zoo Landing reeds, Zoo Forecourt, Zoo Parking, Zoo Back Lot, Boathouse slip, Lantern Court
  and Cobbler Yard (hidden courtyards), Riverwalk Gardens (allotments), Net Yard (crates), Crescent Commons.

WHERE THE ANIMALS SPREAD
  The breach is on the zoo's south fence at Zoo Corner, facing Canal Street, the Zoo Landing reeds, the Zoo
  Bridge and the water. Animals fan out three ways:
  (1) over the Zoo Bridge into Central Park (monkeys, flamingos at Swan Pond) and on to Willow Bend and Willow
      Woods (bear, moose).
  (2) down Zoo Row and Zoo Boulevard through Menagerie Market (meerkats, ostriches) into downtown alleys and
      rooftops (raccoons, red pandas, parrots). Giraffes look over the Elm Heights fences across Zoo Parkway.
  (3) along the quays downstream: penguins and seals under the five bridges, a crocodile under the Central
      Bridge, then the Wharf, Canal Works and the Dock Yard (sea lions, lizards in the warehouses).
  Starter captures happen on Maple Green, in sight of the shop door. Kangaroos and tortoises roam the
  Crescent Commons gardens, and goats the Lookout.

PET-SHOP EXPANSION PLAN
  The shop lot (480 m2) sits in a row of small shops and houses on Maple Street. Behind it is a reserved
  expansion plot of about 1930 m2 (about 58 x 33 m), at least 4 m from every road corridor, reaching back to
  Kennel Lane. Kennel Lane is a rear service alley with a turning bulb (KLE) for deliveries, so kennels,
  breeding rooms, an aviary and parking can grow without touching the shop front. Maple Green (front lawn) and
  the Fairground Lot (across Main St) are open spaces for later outdoor attractions.

CONVENTIONS / GENERATOR WORKAROUNDS
  * District polygons are authored along shared road centrelines and pulled in 1.5 m by _inset(), because the
    validator counts samples on an exactly shared edge as overlap. The 3 m seam sits under the road ribbons.
  * Canal-side districts stop at the quay lines _QN / _QS, 16 m from the canal centreline, so no zoning or
    ground plate covers the water. All districts are clamped to +-345 m, inside the +-347 m building cutoff.
  * PLAYER_SPAWN.heading_deg is measured counter-clockwise from +X (east). markers.py applies it as a raw
    Z rotation, so the spawn empty's local +X points along the heading and the co-op slots line up sideways.
    97.6 deg means facing north across Maple Green toward the Town Square.
"""

# =============================================================================== NODES
NODES = {
    # ---- exits
    "XW": dict(pos=(-420, 212), exit=True),
    "XN": dict(pos=(82, 420), exit=True),
    "XE": dict(pos=(420, -48), exit=True),
    "XE2": dict(pos=(420, -232), exit=True),
    "XS": dict(pos=(10, -420), exit=True),
    # ---- north bank: Canal Street junctions (west -> east)
    "ZC": (-212, 162),     # Zoo Corner: Canal St x Willow Rd (Zoo Bridge) x Zoo Row
    "SWN": (-112, 104),    # Canal St x Swan Lane (Mill Bridge, north end)
    "SQN": (-71.6, 105),   # Canal St x Zoo Boulevard (at the Town Square corner)
    "MN": (5, 100),        # Canal St x Main St (north bridgehead)
    "BELL": (88, 87),      # Canal St x Bell St
    "FN": (160, 58),       # Canal St x Ferry St
    "CR0": (232, 24),      # Canal St x Larch St
    "DN": (296, -4),       # Canal St x Union St x Dock Bridge Rd
    "CE": (334, -25),      # Canal St x Cannery Row
    # ---- zoo approach
    "SA0": (-186, 180),    # Zoo Row x Lantern Alley (west end)
    # Zoo Boulevard axis: clock tower (-53, 73) -> zoo gate (-143.3, 232.3), direction (-0.4908, 0.8713)
    "G": (-132, 212.3),    # Zoo Gate junction: Zoo Blvd end x Zoo Row x Zoo Pkwy
    "LA0": (-92.3, 141.7), # Zoo Blvd x Lantern Alley (crossing)
    "UB": (-112.9, 178.3), # Zoo Blvd x Union St
    "KPS": (-100, 290),    # Zoo Pkwy x Keeper's Lane
    # ---- downtown + north
    "LA2": (-38, 185),     # Union St x Lantern Alley (north end) x Elm St
    "MAU": (11, 186),      # Main St x Union St
    "CA1": (50, 183),      # Union St x Cobbler Alley
    "BU": (112, 172),      # Bell St x Union St
    "FU": (182, 150),      # Ferry St x Union St
    "LU": (250, 136),      # Union St x Larch St x Larch Ct
    "CA0": (97, 128),      # Bell St x Cobbler Alley x Tinker Alley
    "TF": (171, 110),      # Ferry St x Tinker Alley
    "ECT": (-45, 297),     # Zoo Pkwy x Elm St x Elm Ct
    "MH": (30, 258),       # Main St x Zoo Pkwy x Orchard Ln
    "MH2": (55, 300),      # Main St x Hillcrest Dr
    "BH": (130, 315),      # Hillcrest Dr x Bell St
    "FH": (240, 290),      # Hillcrest Dr x Ferry St
    "OB": (121, 247),      # Bell St x Orchard Ln
    "FO": (217, 232),      # Ferry St x Orchard Ln
    # ---- north bank service
    "RF": (150, 30),       # Ferry St x Rope Alley (north end of the Ferry Bridge)
    "DBR": (273, -76),     # Dock Bridge Rd x Rope Alley x Cannery Row (north end of the Dock Bridge)
    # ---- south bank
    "ZBS": (-260, 70),     # Willow Rd x Kingfisher Ln (south end of the Zoo Bridge)
    "WR1": (-280, 6),      # Willow Rd x Park Ln
    "WR2": (-288, -72),    # Willow Rd x Heron Ct x Wren Ct
    "WR3": (-272, -158),   # Willow Rd x Southside Pkwy
    "MSS": (4, -12),       # Main St x Maple St x Riverside Dr (south bridgehead)
    "MC": (-123, -47),     # Maple St x Swan Lane x Collar St
    "PLM": (-160, -80),    # Maple St x Park Ln
    "SSMP": (-205, -168),  # Southside Pkwy x Maple St
    "KLC": (-121, -98),    # Collar St x Kennel Lane
    "KLP": (-55, -101),    # Kennel Lane x Pine St
    "FM": (13, -115),      # Main St x Fair St
    "PC2": (-62, -302),    # Pine St x Pine Crescent
    "SSC": (-128, -190),   # Southside Pkwy x Collar St x Pine Crescent (west arm)
    "PCE": (-48, -197),    # Southside Pkwy x Pine St x Pine Crescent (east arm)
    "SSM": (24, -180),     # Southside Pkwy x Main St
    "SSF": (112, -162),    # Southside Pkwy x Ferry St
    "FS": (112, -60),      # Ferry St x Riverside Dr (south end of the Ferry Bridge)
    "FC": (110, -118),     # Ferry St x Net Alley
    "NA1": (196, -98),     # Riverside Dr x Net Alley
    "DS": (227, -120),     # Dock Bridge Rd x Riverside Dr x Southside Pkwy x Wharf Rd
    "WLK": (295, -178),    # Wharf Rd x Larkspur Ln
    "LK1": (118, -228),    # Ferry St x Larkspur Ln
    "MSL": (47, -285),     # Main St x Larkspur Ln
    "HC0": (200, -243),    # Larkspur Ln x Heather Ct x Aster Ct
    "GA0": (-124, -146),   # Collar St x Garden Alley
    "GA1": (-52, -146),    # Pine St x Garden Alley
    "OC": (68, 251),       # Orchard Ln x Cobbler Alley (north end)
    # ---- dead ends (turning bulbs)
    "ECT_E": dict(pos=(-46, 336), culdesac=True),
    "KPL_E": dict(pos=(-110, 330), culdesac=True),
    "LAR_E": dict(pos=(258, 178), culdesac=True),
    "LKN": dict(pos=(300, 292), culdesac=True),
    "KFL_E": dict(pos=(-330, 100), culdesac=True),
    "HER_E": dict(pos=(-330, -110), culdesac=True),
    "WRN_E": dict(pos=(-218, -100), culdesac=True),
    "WE": dict(pos=(-264, -212), culdesac=True),
    "KLE": dict(pos=(-10, -101), culdesac=True),
    "HTE": dict(pos=(208, -308), culdesac=True),
    "ASE": dict(pos=(196, -198), culdesac=True),
    "FE": dict(pos=(126, -292), culdesac=True),
}

# =============================================================================== ROADS
ROADS = [
    # ------------------------------------------------------------------ main
    dict(id="CanalSt", name="Canal Street", cls="main",
         path=["XW", (-355, 206), (-290, 193), "ZC", (-165, 130), "SWN", "SQN", "MN", (50, 95), "BELL",
               (125, 75), "FN", "CR0", "DN", "CE", "XE"]),
    dict(id="MainSt", name="Main Street", cls="main",
         path=["XN", (72, 340), "MH2", "MH", (18, 225), "MAU", "MN", "MSS", (8, -70), "FM", "SSM", (45, -240), "MSL",
               (30, -345), "XS"]),
    # ------------------------------------------------------------------ secondary
    dict(id="ZooBlvd", name="Zoo Boulevard", cls="secondary", path=["SQN", "LA0", "UB", "G"]),
    dict(id="WillowRd", name="Willow Road", cls="secondary",
         path=["ZC", "ZBS", "WR1", "WR2", "WR3", (-268, -195), "WE"]),
    dict(id="SouthsidePkwy", name="Southside Parkway", cls="secondary",
         path=["WR3", "SSMP", (-168, -180), "SSC", "PCE", "SSM", (75, -172), "SSF", (170, -145), "DS"]),
    dict(id="DockBridgeRd", name="Dock Bridge Road", cls="secondary", path=["DS", "DBR", (290, -40), "DN"]),
    dict(id="UnionSt", name="Union Street", cls="secondary",
         path=["UB", "LA2", "MAU", "CA1", "BU", (150, 162), "FU", "LU", (298, 112), (318, 60), "DN"]),
    dict(id="ZooPkwy", name="Zoo Parkway", cls="secondary",
         path=["G", (-112, 240), (-108, 268), "KPS", (-75, 302), "ECT", (0, 284), "MH"]),
    dict(id="HillcrestDr", name="Hillcrest Drive", cls="secondary",
         path=["MH2", (95, 305), "BH", (185, 312), "FH", (272, 296), "LKN"]),
    dict(id="WharfRd", name="Wharf Road", cls="secondary",
         path=["DS", (262, -150), "WLK", (340, -208), "XE2"]),
    # ------------------------------------------------------------------ side
    dict(id="ZooRow", name="Zoo Row", cls="side", path=["ZC", "SA0", "G"]),
    dict(id="SwanLn", name="Swan Lane", cls="side", path=["SWN", (-112, 80), (-126, 35), (-127, 0), "MC"]),
    dict(id="MapleSt", name="Maple Street", cls="side",
         path=["MSS", (-30, -27), (-75, -33), "MC", "PLM", (-188, -120), "SSMP"]),
    dict(id="ElmSt", name="Elm Street", cls="side", path=["LA2", (-42, 240), "ECT"]),
    dict(id="ElmCt", name="Elm Court", cls="side", path=["ECT", (-44, 318), "ECT_E"]),
    dict(id="BellSt", name="Bell Street", cls="side", path=["BELL", "CA0", "BU", "OB", "BH"]),
    dict(id="OrchardLn", name="Orchard Lane", cls="side", path=["MH", "OC", "OB", (170, 246), "FO"]),
    dict(id="FerrySt", name="Ferry Street", cls="side",
         path=["FH", "FO", "FU", "TF", "FN", "RF", "FS", "FC", "SSF", "LK1", (124, -262), "FE"]),
    dict(id="LarchSt", name="Larch Street", cls="side", path=["CR0", (240, 80), "LU"]),
    dict(id="LarchCt", name="Larch Court", cls="side", path=["LU", (255, 160), "LAR_E"]),
    dict(id="CanneryRow", name="Cannery Row", cls="side",
         path=["DBR", (300, -100), (328, -95), (336, -65), "CE"]),
    dict(id="RiversideDr", name="Riverside Drive", cls="side",
         path=["MSS", (45, -22), (85, -38), "FS", (160, -74), "NA1", "DS"]),
    dict(id="CollarSt", name="Collar Street", cls="side", path=["MC", "KLC", "GA0", "SSC"]),
    dict(id="PineSt", name="Pine Street", cls="side", path=["KLP", "GA1", "PCE", (-50, -250), "PC2"]),
    dict(id="FairSt", name="Fair Street", cls="side", path=["FM", (60, -110), "FC"]),
    dict(id="PineCres", name="Pine Crescent", cls="side",
         path=["SSC", (-150, -238), (-132, -288), "PC2", (0, -300), "MSL"]),
    dict(id="ParkLn", name="Park Lane", cls="side", path=["WR1", (-232, -12), (-190, -44), "PLM"]),
    dict(id="LarkspurLn", name="Larkspur Lane", cls="side",
         path=["LK1", (170, -246), "HC0", (240, -232), "WLK"]),
    dict(id="AsterCt", name="Aster Court", cls="side", path=["HC0", (198, -220), "ASE"]),
    dict(id="HeatherCt", name="Heather Court", cls="side", path=["HC0", (205, -280), "HTE"]),
    dict(id="KingfisherLn", name="Kingfisher Lane", cls="side", path=["ZBS", (-295, 84), "KFL_E"]),
    dict(id="HeronCt", name="Heron Court", cls="side", path=["WR2", (-312, -90), "HER_E"]),
    dict(id="WrenCt", name="Wren Court", cls="side", path=["WR2", (-250, -88), "WRN_E"]),
    # ------------------------------------------------------------------ alleys
    dict(id="LanternAly", name="Lantern Alley", cls="alley",
         path=["SA0", (-150, 152), (-118, 140), "LA0", (-50, 145), (-38, 160), "LA2"]),
    dict(id="CobblerAly", name="Cobbler Alley", cls="alley",
         path=["CA0", (62, 132), (52, 148), "CA1", (60, 216), "OC"]),
    dict(id="GardenAly", name="Garden Alley", cls="alley", path=["GA0", (-88, -142), "GA1"]),
    dict(id="TinkerAly", name="Tinker Alley", cls="alley", path=["CA0", (135, 119), "TF"]),
    dict(id="KeepersLn", name="Keeper's Lane", cls="alley", path=["KPS", (-106, 310), "KPL_E"]),
    dict(id="KennelLn", name="Kennel Lane", cls="alley", path=["KLC", (-88, -100), "KLP", "KLE"]),
    dict(id="RopeAly", name="Rope Alley", cls="alley", path=["RF", (192, 0), (236, -40), "DBR"]),
    dict(id="NetAly", name="Net Alley", cls="alley", path=["FC", (152, -114), "NA1"]),
]

# =============================================================================== WATER
RIVER = dict(name="Willow Canal", width=22,
             path=[(-440, 168), (-370, 163), (-300, 148), (-235, 118), (-170, 80), (-105, 50), (-40, 34),
                   (20, 30), (80, 24), (140, 2), (195, -38), (245, -92), (300, -148), (360, -185),
                   (440, -208)])

# quay lines 16 m from the canal centreline (5 m of dry land beyond the water edge) - helpers for DISTRICTS
_QN = [(-367.7, 178.8), (-294.9, 163.2), (-227.6, 132.2), (-162.6, 94.2), (-99.7, 65.1), (-37.5, 49.8),
      (21.3, 46.0), (83.6, 39.6), (147.6, 16.1), (205.7, -26.1), (256.6, -81.0), (310.1, -135.6),
      (366.3, -170.3)]
_QS = [(-372.3, 147.2), (-305.1, 132.8), (-242.4, 103.8), (-177.4, 65.8), (-110.3, 34.9), (-42.5, 18.2),
      (18.7, 14.0), (76.4, 8.4), (132.4, -12.1), (184.3, -49.9), (233.4, -103.0), (289.9, -160.4),
      (353.7, -199.7)]

PONDS = [
    dict(id="SwanPond", center=(-172, 0), radii=[24, 28, 21, 26, 20, 25, 22], rot=0.3, bank=3.0),
    dict(id="BeaverPond", center=(-292, -282), radii=[16, 19, 14, 18, 15], rot=0.8, bank=2.5),
]

HILLS = [
    dict(id="PicnicHill", center=(-225, 45), radius=30, height=6, squash=(1.0, 0.8), rot=0.45),
    dict(id="LookoutHill", center=(290, 230), radius=40, height=9, squash=(1.0, 0.85), rot=0.6),
]


# =============================================================================== DISTRICTS
def _inset(poly, d=1.5):
    """Pull a polygon in by d metres (mitred). Districts are authored along shared road centrelines;
    the inset keeps neighbours from sharing an exact edge (the validator counts shared-edge samples
    as overlap). The 3 m seam sits under the road ribbons and is invisible."""
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
    # (id, name, kind, ground, label_at, raw polygon along road centrelines / quay lines)
    ("Zoo", "Willowbrook Zoo", "zoo", None, (-250, 312),
     [(-345, 204), (-290, 193), (-212, 162), (-186, 180), (-132, 212.3), (-112, 240), (-108, 268), (-100, 290),
      (-106, 310), (-110, 330), (-110, 345), (-345, 345)]),
    ("Market", "Menagerie Market", "market", None, (-150, 168),
     [(-212, 162), (-186, 180), (-132, 212.3), (-92.3, 141.7), (-71.6, 105), (-112, 104), (-112, 80), (-117, 66),
      _QN[3], _QN[2]]),
    ("Downtown", "Downtown", "downtown", "paved", (60, 120),
     [(-112, 104), (-112, 80), (-117, 66), _QN[4], _QN[5], (4, 47), (5, 100), (50, 95), (88, 87), (125, 75),
      (160, 58), (171, 110), (182, 150), (150, 162), (112, 172), (50, 183), (11, 186), (-38, 185),
      (-112.9, 178.3), (-92.3, 141.7), (-71.6, 105)]),
    ("Riverwalk", "Riverwalk", "riverside", None, None,
     [(4, 47), _QN[6], _QN[7], _QN[8], (150, 30), (160, 58), (125, 75), (88, 87), (50, 95), (5, 100)]),
    ("ElmHeights", "Elm Heights", "residential", None, None,
     [(-112.9, 178.3), (-38, 185), (11, 186), (18, 225), (30, 258), (55, 300), (72, 340), (74, 345),
      (-110, 345), (-110, 330), (-106, 310), (-100, 290), (-108, 268), (-112, 240), (-132, 212.3)]),
    ("OrchardHill", "Orchard Hill", "residential", None, None,
     [(11, 186), (50, 183), (112, 172), (150, 162), (182, 150), (217, 232), (240, 290), (240, 345),
      (74, 345), (72, 340), (55, 300), (30, 258), (18, 225)]),
    ("Hillcrest", "Hillcrest", "residential", None, None,
     [(160, 58), (232, 24), (296, -4), (345, -23), (345, 155), (300, 160), (262, 192), (248, 210),
      (240, 270), (240, 290), (217, 232), (182, 150), (171, 110)]),
    ("LookoutPark", "Lookout Park", "park", None, (318, 190),
     [(345, 155), (345, 345), (240, 345), (240, 290), (240, 270), (248, 210), (262, 192), (300, 160)]),
    ("CanalWorks", "Canal Works", "service", "gravel", (215, -5),
     [(160, 58), (232, 24), (296, -4), (290, -40), (273, -76), (300, -100), (328, -95), (336, -65), (334, -25),
      (345, -27), (345, -157), _QN[11], _QN[10], _QN[9], _QN[8], (150, 30)]),
    ("DockYard", "Dock Yard", "service", "gravel", (316, -50),
     [(296, -4), (290, -40), (273, -76), (300, -100), (328, -95), (336, -65), (334, -25)]),
    ("CentralPark", "Central Park", "park", None, (-200, -20),
     [(-242, 104), _QS[3], _QS[4], _QS[5], (4, 15), (4, -12), (-30, -27), (-75, -33), (-123, -47), (-160, -80),
      (-190, -44), (-232, -12), (-280, 6), (-260, 70)]),
    ("WillowBend", "Willow Bend", "suburb", None, None,
     [(-345, 141), _QS[1], (-242, 104), (-260, 70), (-280, 6), (-232, -12), (-190, -44), (-160, -80),
      (-188, -120), (-205, -168), (-272, -158), (-345, -160)]),
    ("WillowWoods", "Willow Woods", "park", None, None,
     [(-345, -160), (-272, -158), (-205, -168), (-200, -200), (-205, -345), (-345, -345)]),
    ("MapleCorner", "Maple Corner", "petshop", None, (60, -140),
     [(4, -12), (45, -22), (85, -38), (112, -60), (110, -118), (112, -162), (75, -172), (24, -180),
      (13, -115), (11, -101), (-10, -101), (-55, -101), (-88, -100), (-121, -98), (-123, -47), (-75, -33),
      (-30, -27)]),
    ("BridgeCorner", "Bridge Corner", "market", None, None,
     [(4, -12), (4, 15), _QS[6], _QS[7], (130, -12), (112, -60), (85, -38), (45, -22)]),
    ("Wharf", "The Wharf", "service", "gravel", None,
     [(112, -60), (130, -12), _QS[9], _QS[10], _QS[11], (345, -194), (345, -210), (340, -208), (295, -178),
      (262, -150), (227, -120), (170, -145), (112, -162), (110, -118)]),
    ("Pinecrest", "Pinecrest", "residential", None, None,
     [(-123, -47), (-160, -80), (-188, -120), (-205, -168), (-168, -180), (-128, -190), (-48, -197), (24, -180),
      (13, -115), (11, -101), (-10, -101), (-55, -101), (-88, -100), (-121, -98)]),
    ("Meadowbrook", "Meadowbrook", "residential", None, None,
     [(-205, -168), (-168, -180), (-128, -190), (-48, -197), (24, -180), (45, -240), (47, -285), (30, -345),
      (-205, -345), (-200, -200)]),
    ("Larkspur", "Larkspur", "residential", None, None,
     [(24, -180), (75, -172), (112, -162), (170, -145), (227, -120), (262, -150), (295, -178), (340, -208),
      (345, -210), (345, -232), (300, -232), (262, -262), (240, -300), (232, -340), (30, -340), (47, -285),
      (45, -240)]),
]
DISTRICTS = []
for _i, _n, _k, _g, _lab, _p in _D:
    _d = dict(id=_i, name=_n, kind=_k, ground=_g, poly=_inset(_p))
    if _lab:
        _d["label_at"] = _lab
    DISTRICTS.append(_d)

# =============================================================================== LANDMARKS
LANDMARKS = {
    # 24 x 20 m lot on the south side of Maple Street, front 2.5 m behind the sidewalk, looking north
    # across Maple Green, the canal and the Town Square.
    "PetShop": dict(name="Pet Shop", center=(-49.7, -47.2),
                    poly=[(-62.9, -38.9), (-39.1, -35.7), (-36.5, -55.5), (-60.3, -58.7)],
                    facing=(-0.132, 0.991), road="MapleSt",
                    expansion_poly=[(-60.3, -59.2), (-36.5, -56.0), (-26, -57.4), (-26, -92), (-84, -92),
                                    (-84, -62.4)]),
    "Zoo": dict(name="Willowbrook Zoo", center=(-235, 262),
                poly=[(-318, 222), (-290, 212), (-248, 198), (-222, 186), (-200, 198), (-160.7, 222.5),
                      (-125.9, 242.1), (-125, 295), (-130, 338), (-318, 338)],
                entrance=(-143.3, 232.3), entrance_facing=(0.4908, -0.8713), incident_at=(-235, 192)),
    "CentralPark": dict(name="Central Park", center=(-185, 20),
                        poly=[(-238, 92), (-252, 62), (-262, 22), (-240, 4), (-200, -18), (-170, -48),
                              (-136, -38), (-134, 0), (-136, 34), (-160, 60), (-200, 80)]),
    "ServiceYard": dict(name="Container Yard", center=(314, -58),
                        poly=[(300, -32), (326, -38), (327, -84), (304, -84)]),
    "TownSquare": dict(name="Town Square", center=(-53, 73),
                       poly=[(-78, 62), (-28, 52), (-28, 90), (-78, 90)]),
    # optional extras
    "Lookout": dict(name="Lookout Point", center=(266, 206),
                    poly=[(258, 198), (274, 198), (274, 214), (258, 214)]),
    "OpenLot": dict(name="Fairground Lot", center=(52, -66),
                    poly=[(22, -36), (80, -46), (82, -92), (24, -94)]),
    # the pet shop's front lawn across Maple Street: village green + starter capture zone (C's Hub Green)
    "MapleGreen": dict(name="Maple Green", center=(-62, -4),
                       poly=[(-112, -30), (-80, -25), (-35, -19), (-16, -11), (-10, 8), (-42, 15), (-111, 28),
                             (-116, 0)]),
    "Marina": dict(name="Marina", center=(318, -138), allow_water=True,
                   poly=[(296, -116), (338, -126), (342, -160), (300, -140)]),
}

# =============================================================================== PATHS
PATHS = [
    dict(id="RiverwalkN_W", kind="riverwalk", width=4.0,
         path=[(-222, 124), (-165, 93), (-100.3, 63.2), (-80, 58)]),
    dict(id="RiverwalkN_E", kind="riverwalk", width=4.0,
         path=[(-26, 50), (16, 50), (50, 45.5), (83.2, 38), (128, 21)]),
    dict(id="RiverwalkS", kind="riverwalk", width=4.0,
         path=[(-232, 94), (-176.5, 67.6), (-109.7, 36.8), (-42.2, 20.2), (-14, 12)]),
    dict(id="RiverwalkSE", kind="riverwalk", width=3.5,
         path=[(18, 8), (77, 9), (124, -9)]),
    dict(id="ZooLandingPath", kind="trail", width=2.5,
         path=[(-345, 172), (-296, 161), (-250, 141)]),
    dict(id="SquareAxis", kind="plaza", width=5.0, path=[(-53, 60), (-53, 73), (-68, 98)]),
    dict(id="GreenWalk", kind="park", width=3.0, path=[(-50, -18), (-50, 0), (-52, 15)]),
    dict(id="ParkLoop", kind="park", width=3.0,
         path=[(-140, -28), (-185, -35), (-214, -6), (-212, 40), (-175, 55), (-140, 40), (-134, 10), (-140, -28)]),
    dict(id="PicnicHillPath", kind="park", width=2.5, path=[(-212, 40), (-225, 45)]),
    dict(id="WoodsTrail", kind="trail", width=2.0,
         path=[(-264, -224), (-300, -255), (-310, -300), (-262, -322), (-215, -305)]),
    dict(id="LookoutTrail", kind="trail", width=2.0,
         path=[(258, 190), (266, 206), (285, 228), (296, 260), (300, 280)]),
    dict(id="CommonsWalk", kind="park", width=2.5, path=[(-60, -247), (-84, -247)]),
]

NO_BUILD = [
    dict(id="BoathouseSlip", reason="boathouse + slipway on the west quay (kayaks, a hiding spot under the deck)",
         poly=[(-171, 115.1), (-178.4, 100.9), (-205, 114.9), (-197.6, 129.1)]),
    dict(id="RiverwalkGardens", reason="community allotments on the north quay (B's canal gardens)",
         poly=[(92, 34), (126, 22), (130, 40), (96, 52)]),
    dict(id="NetYard", reason="open crate and net yard on the Wharf quay, reached from Riverside Drive",
         poly=[(150, -42), (174, -56), (170, -68), (146, -58)]),
    dict(id="ZooLanding", reason="reedy meadow between Canal Street and the water below the zoo fence - "
                                 "first escape pocket",
         poly=[(-345, 188), (-285, 177), (-240, 158), (-250, 140), (-296, 160), (-345, 170)]),
    dict(id="ZooForecourt", reason="zoo entrance forecourt: ticket booths, crowd space, terminates the "
                                   "Zoo Boulevard vista",
         poly=[(-158, 221), (-128, 238.5), (-133, 227), (-142, 218)]),
    dict(id="ZooParking", reason="zoo visitor parking across Zoo Parkway from the gate",
         poly=[(-110, 201), (-90, 192), (-86, 228), (-100, 233)]),
    dict(id="ZooBackLot", reason="zoo back-of-house on Keeper's Lane: feed sheds, keeper trucks",
         poly=[(-123, 296), (-114, 296), (-116, 312), (-121, 321), (-121, 338), (-127, 338)]),  # clear of the Keeper's Lane bulb
    dict(id="LanternCourt", reason="hidden courtyard off Lantern Alley (bins, crates, a fig tree)",
         poly=[(-74, 150), (-52, 150), (-52, 164), (-74, 164)]),
    dict(id="CobblerYard", reason="hidden courtyard at the dog-leg of Cobbler Alley",
         poly=[(64, 140), (84, 140), (84, 158), (64, 158)]),
    dict(id="CrescentCommons", reason="shared green inside Pine Crescent (swings, hedge maze), houses ring it",
         poly=[(-114, -266), (-84, -266), (-84, -228), (-114, -228)]),
]

# =============================================================================== GAMEPLAY HINTS
# Escape story: the breach is on the zoo's south fence at Zoo Corner, facing Canal Street, Zoo Landing, the Zoo
# Bridge and the water. Animals spread three ways: (1) over the Zoo Bridge into Central Park / Willow Bend and on
# to the woods, (2) down Zoo Row and the Zoo Boulevard through Menagerie Market into downtown, (3) along the
# canal quays downstream to the bridges, the Wharf and the docks.
ANIMAL_ZONES = [
    dict(id="ZooBreach", center=(-235, 192), radius=30, habitat="breached south fence at Zoo Corner",
         animals=["mixed stampede"], notes="incident point; three spread routes: Zoo Bridge, Zoo Row / boulevard, "
                                           "the canal quays"),
    dict(id="ZooLanding", center=(-300, 172), radius=40, habitat="reedy canal meadow",
         animals=["penguins", "flamingos", "capybaras"], notes="first escape pocket between Canal St and the water"),
    dict(id="ZooRowStalls", center=(-150, 168), radius=40, habitat="souvenir stalls / fruit crates / Lantern Alley",
         animals=["meerkats", "ostriches", "goats"], notes="Menagerie Market, right outside the zoo gate"),
    dict(id="ElmGardens", center=(-80, 240), radius=50, habitat="back gardens across Zoo Parkway",
         animals=["giraffe", "zebras"], notes="giraffe peeking over Elm Heights fences next to the zoo"),
    dict(id="ParkCanopy", center=(-215, 15), radius=50, habitat="park tree clusters / Picnic Hill",
         animals=["monkeys", "lemurs", "sloth"], notes="tree clumps around Picnic Hill"),
    dict(id="SwanPond", center=(-172, 0), radius=40, habitat="pond", animals=["flamingos", "pelicans", "otters"],
         notes="Swan Pond in Central Park"),
    dict(id="MapleGreen", center=(-62, -2), radius=40, habitat="village green in front of the pet shop",
         animals=["rabbits", "guinea pigs", "peacocks"], notes="starter / tutorial captures in view of the shop door"),
    dict(id="CanalCorridor", center=(40, 30), radius=70, habitat="canal water / quays / under bridges",
         animals=["penguins", "seals", "crocodile"], notes="the escape highway; crocodile under the Central Bridge"),
    dict(id="DowntownRoofs", center=(40, 140), radius=70, habitat="rooftops / awnings / water tanks",
         animals=["parrots", "macaws", "toucans"], notes="downtown skyline around the Town Square"),
    dict(id="Alleys", center=(-55, 150), radius=40, habitat="alleys / bins / courtyards",
         animals=["raccoons", "red pandas"], notes="Lantern Alley, Lantern Court, Cobbler Yard"),
    dict(id="Fairground", center=(52, -66), radius=32, habitat="open lot", animals=["ostriches", "emus"],
         notes="open chase arena across Main Street from the pet shop - multiplayer round-ups"),
    dict(id="Warehouses", center=(240, -20), radius=60, habitat="warehouses / sheds / Rope Alley",
         animals=["lizards", "snakes", "tortoises"], notes="Canal Works"),
    dict(id="DocksMarina", center=(315, -110), radius=45, habitat="dock yard containers / boat slips",
         animals=["sea lions", "pelicans"], notes="Dock Yard and the Marina"),
    dict(id="WharfDocks", center=(175, -80), radius=45, habitat="net sheds / crate yard",
         animals=["otters", "pelicans", "crabs"], notes="Net Alley and the Wharf quay"),
    dict(id="LookoutHill", center=(290, 230), radius=45, habitat="grassy hilltop",
         animals=["goats", "llamas", "alpacas"], notes="Lookout Park, reached from Larch Court or Hillcrest Drive"),
    dict(id="CrescentCommons", center=(-99, -247), radius=45, habitat="backyards / hedge maze / pools",
         animals=["kangaroos", "tortoise", "hedgehogs"], notes="Meadowbrook gardens around Crescent Commons"),
    dict(id="WillowWoods", center=(-280, -270), radius=60, habitat="woods / beaver pond",
         animals=["bear", "moose", "wolves"], notes="big animals - need teamwork or tools"),
]

HIDING_SPOTS = [
    dict(id="UnderZooBridge", at=(-235, 118), notes="under the Zoo Bridge deck"),
    dict(id="UnderMillBridge", at=(-120, 56), notes="under the Mill Bridge (Swan Lane)"),
    dict(id="UnderCentralBridge", at=(4, 30), notes="under the Central Bridge deck"),
    dict(id="UnderFerryBridge", at=(138, 3), notes="under the narrow Ferry Bridge"),
    dict(id="UnderDockBridge", at=(250, -98), notes="under the Dock Bridge"),
    dict(id="ZooLandingReeds", at=(-330, 168), notes="reeds on the canal bank below the zoo"),
    dict(id="ZooBackLot", at=(-122, 320), notes="feed sheds on Keeper's Lane behind the zoo"),
    dict(id="BoathouseSlip", at=(-188, 112), notes="under the boathouse deck"),
    dict(id="LanternCourt", at=(-63, 157), notes="hidden courtyard off Lantern Alley"),
    dict(id="CobblerYard", at=(74, 149), notes="hidden courtyard at the Cobbler Alley dog-leg"),
    dict(id="ZooRowCrates", at=(-140, 170), notes="crate stacks behind the Zoo Row stalls"),
    dict(id="RopeAlley", at=(214, -20), notes="between the warehouses on Rope Alley"),
    dict(id="DockYardContainers", at=(314, -60), notes="container stacks in the Dock Yard"),
    dict(id="NetYard", at=(160, -55), notes="net piles in the Wharf crate yard"),
    dict(id="KennelLane", at=(-80, -100), notes="behind the pet shop on Kennel Lane"),
    dict(id="GardenAlley", at=(-88, -144), notes="bins and hedges on Garden Alley"),
    dict(id="PicnicHillThicket", at=(-238, 52), notes="thicket on the far side of Picnic Hill"),
    dict(id="RiverwalkGardens", at=(110, 36), notes="bean rows in the riverwalk allotments"),
    dict(id="ElmCourtBulb", at=(-46, 344), notes="end of Elm Court"),
    dict(id="HeronCourtBulb", at=(-336, -114), notes="end of Heron Court, backing onto the woods"),
    dict(id="CrescentHedge", at=(-99, -250), notes="hedge maze in Crescent Commons"),
    dict(id="WoodsHollow", at=(-300, -305), notes="fallen-log hollow by the beaver pond"),
    dict(id="LookoutBushes", at=(306, 248), notes="bushes behind the lookout"),
    dict(id="FairgroundCorner", at=(84, -90), notes="behind the fairground stage"),
]

PLAYER_SPAWN = dict(at=(-51.5, -33.9), heading_deg=97.6)

# =============================================================================== VIEWS
VIEWS = {
    "overview": ((330, -430, 260), (-40, 30, 0), 24),
    "downtown": ((-38, 48, 26), (-143, 232, 0), 30),
    "petshop": ((-48, -72, 18), (-40, 60, 2), 26),
    "zoo": ((-88, 158, 22), (-145, 232, 2), 28),
    "park": ((-100, 40, 40), (-200, 0, 0), 26),
    "canal": ((-240, 140, 22), (20, 30, 0), 26),
    "service": ((200, -200, 60), (300, -60, 0), 26),
    "suburb": ((20, -200, 60), (-99, -247, 0), 30),
}


# =============================================================================== CROSSWALKS
# Mid-block zebra crossings (intersections get theirs automatically). Lead integration pass:
# the spawn -> Maple Green -> clock tower axis, the Fairground arch, and the Town Square front.
CROSSWALKS = [
    dict(road="MapleSt", at=(-50.5, -30.0)),   # pet shop door / spawn -> Green Walk
    dict(road="MainSt", at=(8.0, -66.0)),      # Maple Corner -> Fairground Lot arch
    dict(road="CanalSt", at=(-45.0, 101.0)),   # downtown -> Town Square
]


# =============================================================================== CIVIC ANCHORS
# Lead densification pass (2026-10-20): civic / commercial anchors that make the town read as a
# busy city. Sites were fitted along their roads by _tmp/site_finder.py (clear of roads, canal,
# paths and other sites). Built by citygen/landmarks/civic_services.py and civic_commerce.py.
LANDMARKS.update({
    "GasStation": dict(name="Gas Station", module="civic_commerce", road="MainSt", center=(58.0, -203.3), facing=(-0.931, -0.365),
                  poly=[(38.8, -192.6), (51.2, -224.2), (77.3, -214.0), (64.9, -182.3)]),
    "PoliceStation": dict(name="Police Station", module="civic_services", road="CanalSt", center=(65.2, 114.7), facing=(-0.185, -0.983),
                  poly=[(48.2, 105.7), (77.7, 100.1), (82.2, 123.7), (52.7, 129.3)]),
    "FireStation": dict(name="Fire Station", module="civic_services", road="MainSt", center=(43.3, 229.4), facing=(-0.95, 0.314),
                  poly=[(34.7, 244.9), (27.2, 222.1), (51.9, 213.9), (59.4, 236.7)]),
    "Supermarket": dict(name="Supermarket", module="civic_commerce", road="SouthsidePkwy", center=(-2.9, -216.8), facing=(-0.256, 0.967),
                  poly=[(16.9, -189.8), (-33.4, -203.1), (-22.7, -243.7), (27.6, -230.4)]),
    "School": dict(name="Willowbrook School", module="civic_services", road="OrchardLn|HillcrestDr|BellSt|UnionSt|FerrySt|LarchSt", center=(178.1, 207.9), facing=(0.914, -0.405),
                  poly=[(186.2, 176.9), (206.5, 222.6), (169.9, 238.8), (149.6, 193.1)]),
    "VetClinic": dict(name="Vet Clinic", module="civic_services", road="MapleSt", center=(-94.1, -53.4), facing=(-0.244, 0.97),
                  poly=[(-85.9, -41.0), (-107.2, -46.4), (-102.3, -65.8), (-81.0, -60.4)]),
    "Diner": dict(name="Diner", module="civic_commerce", road="MainSt", center=(35.0, -135.4), facing=(-0.99, -0.143),
                  poly=[(24.5, -125.8), (27.6, -147.5), (45.5, -145.0), (42.3, -123.2)]),
    "Church": dict(name="Church", module="civic_services", road="ElmSt", center=(-20.9, 255.9), facing=(-0.999, -0.055),
                  poly=[(-37.5, 266.0), (-36.3, 244.0), (-4.3, 245.8), (-5.5, 267.8)]),
})


# civic anchors as habitats / hiding places (lead densification pass, 2026-10-20)
ANIMAL_ZONES += [
    dict(id="SchoolYard", center=(180.0, 214.0), radius=30, habitat="school playground / fenced sports court",
         animals=["kangaroos", "ostriches"], notes="open sand + court for round-ups; school bus as cover"),
    dict(id="SupermarketLot", center=(-2.9, -216.8), radius=32, habitat="supermarket parking lot / loading dock",
         animals=["raccoons", "monkeys"], notes="cart corrals, dock bins, parked cars"),
    dict(id="Churchyard", center=(-20.9, 255.9), radius=22, habitat="churchyard / headstones / steeple",
         animals=["owls", "bats", "peacocks"], notes="quiet corner next to Elm Heights"),
    dict(id="GasCanopy", center=(58.0, -203.3), radius=22, habitat="gas station canopy / pumps / mart",
         animals=["parrots", "lemurs"], notes="canopy roof is a perch; snacks in the mart"),
]
HIDING_SPOTS += [
    dict(id="SupermarketDock", at=(-2.9, -226.0), notes="behind the supermarket loading dock"),
    dict(id="ChurchyardHeadstones", at=(-14.0, 258.0), notes="between the churchyard headstones"),
    dict(id="SchoolPlayTower", at=(186.0, 216.0), notes="under the school play tower"),
    dict(id="DinerBins", at=(35.0, -142.0), notes="diner back bins"),
    dict(id="FireBay", at=(43.3, 233.0), notes="behind the fire engine in the open bay"),
]
