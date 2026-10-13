"""Candidate B - "Old Town Ring"   (Breed city foundation layout)

CONCEPT
-------
A compact, lopsided OLD TOWN sits just north of the map centre, wrapped by an irregular main-class
ring road ("Founders Ring", ~830 m around).  The ring is egg-shaped: tight and flat on the park
side (110-120 m from the square), stretched 165 m toward the market in the east.  Inside it the
streets are old and crooked: a skewed COURTHOUSE SQUARE (Town Square + clock tower, plaza ~42 m) is
framed by a narrow cobbled loop and the lanes leave its corners like a pinwheel - Zoo Boulevard (NE),
Bell Lane (N), Cobbler Lane (NW, the short-cut to the pet shop), Old Mill Lane (W), Chapel Street
(S) and Market Street (E).  Broken back alleys (Clocktower, Gaslight, Tanner's, Lantern Alley) and
the crooked Lamplighter Lane split each old-town wedge into a ring-facing row and a square-facing
row of 2-5 storey buildings; two hidden courtyards sit inside the western blocks.
Bell Lane and Chapel Street hit the ring as T's (Bell Lane looks straight into the park gate);
Lookout Road and Bridge Street leave the ring 40 m further east - offset T's instead of one
straight cross through town.  Lantern Street (market) runs on into Old Town as Lantern Alley.

Outside the ring the avenues leave like spokes and are stitched by curving secondary streets:
  * NE  ZOO BOULEVARD - dead-straight main avenue from the Town Square through the ring to the ZOO
        GATE (the town's main sightline: clock tower -> boulevard -> zoo gate).  Zoo Drive wraps the
        zoo's south and west side and links East Ave to Lookout Road.  Zoo parking at the gate.
  * N   LOOKOUT ROAD climbs north along the park's east edge to the north exit; MAPLE RISE
        (residential, Acorn Court cul-de-sac) fills the land between it, the boulevard and the zoo.
  * NW  CENTRAL PARK - green wedge whose tip touches the ring and widens to the NW map edge: duck
        pond, Lookout Hill (lookout) at the wide end, a loop path, back gate from the pet shop.
  * W   WILLOW STREET - the friendly mixed street of the pet-shop quarter WILLOW END.  It leaves the
        ring at the park tip and loops west through FERNHILL (suburb, cul-de-sacs) to WEST AVENUE
        (west exit).  The PET SHOP sits 70 m outside the ring on Willow's north side, at the head of
        Kettle Lane (terminated vista from West Ave), its back fence on the park, with a reserved
        side lot for growth.  From the Town Square it is one crooked lane away (Cobbler Lane).
  * SW  TANNERY ROAD crosses the canal into the TANNERY YARDS (warehouses, wharf, container yard)
        on the south bank; Towpath Road leaves the yards to the SW exit.  Brook Street (WESTBROOK
        residential) bends south over the old mill bridge into the yards - a back-way loop.
  * S   BRIDGE STREET (main) drops to the canal.  CANAL STREET runs along the north bank through the
        riverside CANAL QUARTER (cafes, boathouses, riverwalk, Lock Plaza, Ropewalk Alley, allotment
        gardens); TOWPATH ROAD runs along the south bank past BOATHOUSE ROW to the WILLOWBROOK suburb
        (five cul-de-sacs fanning off the towpath, school yard).
  * SE  ORCHARD ROAD crosses the canal on the fourth bridge; LANTERN STREET is a walkable market
        street just outside the ring (LANTERN MARKET), Cart Alley cuts through its shops.
  * E   EAST AVENUE (main) through ORCHARD HILL to the east exit.
The OLD MILL CANAL crosses the south of the map, bridged 4 times, all near-perpendicular.

Exits: West Ave (W), East Ave (E), Towpath Rd (SW, trucks to the yards), Lookout Rd (N).
Build stats (terrain,roads): ~8.8 km of road (main 1.77 / secondary 3.08 / side 3.12 / alley 0.81 km),
58 intersections (22 four-way, 36 T), 4 bridges, 13 cul-de-sacs + 2 dead-end alleys, 0 errors,
0 warnings.  District polygons are drawn on shared road-centre / canal-bank chains and inset 1.5 m.

Animal spread: the breach is in the zoo's WEST wall facing Maple Rise.  Animals spill into the
Maple Rise backyards (giraffe over fences), down the boulevard into Old Town (parrots on roofs,
raccoons in the alleys), across Lookout Rd into the park (monkeys, flamingos at the pond), and on to
the canal (penguins, otters), the Tannery Yards (reptiles in warehouses) and the suburbs.  The pet
shop is on the park side of town, so the first loop is shop -> park -> Old Town -> boulevard -> zoo,
and every spoke brings the player back to the ring and Willow Street.
"""
import math


def _shrink(poly, d=1.5):
    """Inset a polygon by d metres.  Neighbouring zones share road centrelines as borders; the inset
    leaves a hairline gap so the validator does not count shared edges as overlap."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0

    def inward(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        return -dy / ln * s, dx / ln * s

    out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        n1, n2 = inward(p0, p1), inward(p1, p2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            bx, by, k = n1[0], n1[1], d
        else:
            bx, by = bx / bl, by / bl
            k = d / max(bx * n1[0] + by * n1[1], 0.4)
        out.append((round(p1[0] + bx * k, 2), round(p1[1] + by * k, 2)))
    return out


# =============================================================================== NODES
NODES = {
    # ---- Old Town: skewed courthouse square (plaza ~42 m) + lane / alley junctions
    "SQ_NE": (20, 44), "SQ_NW": (-40, 48), "SQ_SW": (-44, -12), "SQ_SE": (16, -16),
    "BV_M": (48, 72), "BL_M": (-37, 90), "OM_M": (-98, 8), "CH_M": (0, -66), "MK_M": (68, -14),
    "LL_J": (64, -60),
    # ---- Founders Ring
    "RE": (152, 0), "RENE": (126, 64), "RNE": (78, 102), "RN2": (8, 122), "RN": (-30, 124), "RNW": (-98, 96),
    "RW": (-128, 12), "RSW": (-110, -64), "RS": (-15, -98), "RS2": (25, -102), "RSE": (92, -94),
    "RLT": (138, -50),
    # ---- north: boulevard, Maple Rise, zoo
    "BV_2": (118, 142), "G": (168, 192), "ZD_W": (145, 235), "ZD1": (232, 143),
    "MP1": (86, 210), "LK1": (-20, 208), "LK3": (10, 335),
    "AC_END": dict(pos=(80, 284), culdesac=True),
    "EX_N": dict(pos=(20, 420), exit=True),
    # ---- east: East Ave, Orchard Hill, Lantern Market
    "E1": (205, 10), "E2": (268, 2), "OL1": (214, 75), "LT_M": (196, -60),
    "PC_END": dict(pos=(162, 92), culdesac=True),
    "PP1": (262, -70), "PP2": (254, -140),
    "RC_END": dict(pos=(318, -88), culdesac=True),
    "QC_END": dict(pos=(184, -122), culdesac=True),
    "EX_E": dict(pos=(420, -42), exit=True),
    # ---- west: Willow End (pet shop), Fernhill, Westbrook
    "WL1": (-165, 125), "WL2": (-240, 146), "W1": (-192, 14), "W2": (-258, 36), "W3": (-340, 60),
    "EX_W": dict(pos=(-420, 82), exit=True),
    "FH1": (-258, 245), "FH_END": dict(pos=(-252, 325), culdesac=True),
    "FC_END": dict(pos=(-322, 282), culdesac=True),
    "CC_END": dict(pos=(-276, 98), culdesac=True),
    "TR1": (-145, -110), "KT2": (-182, -100), "SY1": (-252, -96),
    # ---- canal, north bank
    "BS_M": (18, -145), "TR_C": (-172, -158), "C_S": (10, -188), "C_E": (160, -178), "C_E2": (262, -198),
    "CE_END": dict(pos=(312, -222), culdesac=True),
    # ---- south bank: Tannery Yards, Boathouse Row, Willowbrook
    "WA0": (-318, -214), "TP1": (-310, -250), "TR2": (-202, -253), "TP2": (-105, -265),
    "T_S": (16, -268), "TP3": (92, -262), "TP_E": (172, -258), "DPA": (-205, -333), "LS1": (270, -288),
    "EX_SW": dict(pos=(-420, -236), exit=True),
    "WA_END": (-245, -206),
    "MPC_END": dict(pos=(2, -332), culdesac=True),
    "HC_END": dict(pos=(88, -330), culdesac=True),
    "SC_END": dict(pos=(200, -322), culdesac=True),
    "WC_END": dict(pos=(258, -342), culdesac=True),
    "LS_END": dict(pos=(338, -312), culdesac=True),
}

# =============================================================================== ROADS
ROADS = [
    # ------------------------------------------------------------------ main
    dict(id="Ring", name="Founders Ring", cls="main",
         path=["RE", "RENE", "RNE", "RN2", "RN", "RNW", "RW", "RSW", "RS", "RS2", "RSE", "RLT", "RE"]),
    dict(id="Boulevard", name="Zoo Boulevard", cls="main", path=["SQ_NE", "BV_M", "RNE", "BV_2", "G"]),
    dict(id="WestAve", name="West Avenue", cls="main", path=["RW", "W1", "W2", (-300, 46), "W3", "EX_W"]),
    dict(id="EastAve", name="East Avenue", cls="main", path=["RE", "E1", "E2", (330, -18), "EX_E"]),
    dict(id="BridgeSt", name="Bridge Street", cls="main", path=["RS2", "BS_M", "C_S", "T_S"]),
    # ------------------------------------------------------------------ secondary
    dict(id="ChapelSt", name="Chapel Street", cls="secondary", path=["SQ_SE", (8, -44), "CH_M", "RS"]),
    dict(id="MarketSt", name="Market Street", cls="secondary", path=["SQ_SE", "MK_M", (110, -6), "RE"]),
    dict(id="LookoutRd", name="Lookout Road", cls="secondary",
         path=["RN2", (0, 165), "LK1", (-8, 255), (-12, 300), "LK3", "EX_N"]),
    dict(id="ZooDr", name="Zoo Drive", cls="secondary",
         path=["E2", (286, 62), (272, 110), "ZD1", "G", "ZD_W", (132, 284), (108, 324), (62, 340), "LK3"]),
    dict(id="WillowSt", name="Willow Street", cls="secondary",
         path=["RNW", (-128, 116), "WL1", (-200, 129), "WL2", (-275, 160), (-308, 160), (-338, 140),
               (-354, 108), "W3"]),
    dict(id="TanneryRd", name="Tannery Road", cls="secondary", path=["RSW", "TR1", "TR_C", "TR2"]),
    dict(id="OrchardRd", name="Orchard Road", cls="secondary", path=["RSE", (125, -122), "C_E", "TP_E"]),
    dict(id="CanalSt", name="Canal Street", cls="secondary",
         path=["TR_C", (-110, -180), "C_S", (80, -180), "C_E", (215, -186), "C_E2", (290, -212), "CE_END"]),
    dict(id="TowpathRd", name="Towpath Road", cls="secondary",
         path=["EX_SW", "TP1", "TR2", "TP2", "T_S", "TP3", "TP_E"]),
    dict(id="PippinSt", name="Pippin Street", cls="secondary",
         path=["E2", (272, -28), "PP1", (250, -105), "PP2", (264, -172), "C_E2"]),
    # ------------------------------------------------------------------ side streets
    dict(id="SquareLoop", name="Courthouse Square", cls="side",
         path=["SQ_NE", (-10, 46), "SQ_NW", (-42, 18), "SQ_SW", (-14, -14), "SQ_SE", (18, 14), "SQ_NE"]),
    dict(id="BellLn", name="Bell Lane", cls="side", path=["SQ_NW", (-41, 68), "BL_M", "RN"]),
    dict(id="CobblerLn", name="Cobbler Lane", cls="side", path=["SQ_NW", (-58, 52), (-72, 70), "RNW"]),
    dict(id="OldMillLn", name="Old Mill Lane", cls="side", path=["SQ_SW", (-72, -8), "OM_M", "RW"]),
    dict(id="LamplighterLn", name="Lamplighter Lane", cls="side", path=["CH_M", (33, -68), "LL_J", "RSE"]),
    dict(id="MapleSt", name="Maple Street", cls="side", path=["LK1", (28, 216), "MP1", "ZD_W"]),
    dict(id="HawthornLn", name="Hawthorn Lane", cls="side", path=["BV_2", (100, 176), "MP1"]),
    dict(id="AcornCt", name="Acorn Court", cls="side", path=["MP1", (88, 250), "AC_END"]),
    dict(id="OrchardLn", name="Orchard Lane", cls="side", path=["E1", "OL1", "ZD1"]),
    dict(id="PlumCt", name="Plum Court", cls="side", path=["OL1", (188, 87), "PC_END"]),
    dict(id="LanternSt", name="Lantern Street", cls="side", path=["RLT", (168, -60), "LT_M", (228, -64), "PP1"]),
    dict(id="RussetCt", name="Russet Court", cls="side", path=["PP1", (292, -72), "RC_END"]),
    dict(id="QuinceCt", name="Quince Court", cls="side", path=["PP2", (215, -130), "QC_END"]),
    dict(id="KettleLn", name="Kettle Lane", cls="side", path=["WL1", (-180, 70), "W1", (-190, -45), "KT2"]),
    dict(id="FernhillRd", name="Fernhill Road", cls="side",
         path=["WL2", (-246, 195), "FH1", (-262, 290), "FH_END"]),
    dict(id="FernCt", name="Fern Court", cls="side", path=["FH1", (-296, 256), "FC_END"]),
    dict(id="CloverCt", name="Clover Court", cls="side", path=["W2", (-264, 72), "CC_END"]),
    dict(id="SycamoreSt", name="Sycamore Street", cls="side", path=["W2", (-272, -18), (-262, -62), "SY1"]),
    dict(id="BrookSt", name="Brook Street", cls="side",
         path=["TR1", "KT2", (-215, -92), "SY1", (-292, -108), (-322, -122), (-326, -160), "WA0", "TP1"]),
    dict(id="DepotRd", name="Depot Road", cls="side",
         path=["TP1", (-318, -295), (-290, -330), "DPA", (-160, -320), (-125, -298), "TP2"]),
    dict(id="MillPondCt", name="Mill Pond Court", cls="side", path=["T_S", (12, -300), "MPC_END"]),
    dict(id="HeronCt", name="Heron Court", cls="side", path=["TP3", (98, -298), "HC_END"]),
    dict(id="SparrowCt", name="Sparrow Court", cls="side", path=["TP_E", (182, -292), "SC_END"]),
    dict(id="LarkspurLn", name="Larkspur Lane", cls="side", path=["TP_E", (225, -272), "LS1", (305, -298), "LS_END"]),
    dict(id="WrenCt", name="Wren Court", cls="side", path=["LS1", (266, -318), "WC_END"]),
    # ------------------------------------------------------------------ alleys
    dict(id="ClocktowerAly", name="Clocktower Alley", cls="alley", path=["BV_M", (12, 88), "BL_M"]),
    dict(id="GaslightAly", name="Gaslight Alley", cls="alley", path=["MK_M", (80, 22), (100, 45), "RENE"]),
    dict(id="TannersAly", name="Tanner's Alley", cls="alley", path=["OM_M", (-90, -30), (-55, -58), "CH_M"]),
    dict(id="LanternAly", name="Lantern Alley", cls="alley", path=["LL_J", (90, -42), (112, -38), "RLT"]),
    dict(id="CartAly", name="Cart Alley", cls="alley", path=["E1", (200, -22), "LT_M"]),
    dict(id="RopewalkAly", name="Ropewalk Alley", cls="alley", path=["TR1", (-100, -128), (-45, -142), "BS_M"]),
    dict(id="CrateAly", name="Crate Alley", cls="alley", path=["TR2", (-208, -292), "DPA"]),
    dict(id="WharfAly", name="Wharf Alley", cls="alley", path=["WA0", (-285, -205), "WA_END"]),
]

# =============================================================================== WATER / TERRAIN
RIVER = dict(name="Old Mill Canal", width=22,
             path=[(-440, -150), (-330, -158), (-220, -185), (-110, -218), (0, -228), (110, -212),
                   (220, -222), (320, -255), (440, -275)])

PONDS = [dict(id="DuckPond", center=(-95, 212), radii=[30, 26, 33, 24, 28, 31, 23, 27], rot=0.3, bank=3.0)]

HILLS = [dict(id="LookoutHill", center=(-118, 302), radius=46, height=10, squash=(1.25, 0.9), rot=0.25)]

# =============================================================================== DISTRICTS
# Shared border chains (road centrelines / canal banks + 3.5 m) so the zones tile the map.
# ring centreline sampled from the spline: even index = ring node, odd index = mid-arc point
#        0 RE       1          2 RENE     3          4 RNE      5          6 RN2      7
_RING = [(152, 0), (141, 33), (126, 64), (105, 85), (78, 102), (44, 114), (8, 122), (-11, 125),
         # 8 RN      9           10 RNW     11          12 RW       13           14 RSW       15
         (-30, 124), (-64, 115), (-98, 96), (-119, 58), (-128, 12), (-126, -29), (-110, -64), (-66, -86),
         # 16 RS      17         18 RS2      19          20 RSE     21          22 RLT      23
         (-15, -98), (4, -101), (25, -102), (59, -101), (92, -94), (118, -75), (138, -50), (147, -26)]
_NBANK = [(-180, -183), (-190, -180), (-210, -173), (-230, -168), (-250, -162), (-270, -157), (-290, -152),
          (-310, -147), (-330, -144), (-350, -141), (-370, -139)]                       # west of Tannery Rd
_NBANK_E = [(262, -221), (250, -216), (230, -210), (210, -206), (190, -202), (170, -200), (150, -198),
            (130, -197), (110, -198), (90, -199), (70, -202), (50, -207), (30, -210), (10, -213),
            (-10, -214), (-30, -213), (-50, -212), (-70, -210), (-90, -207), (-110, -204), (-130, -199),
            (-150, -193), (-170, -186), (-180, -183)]                                   # Pippin -> Tannery
_SBANK_W = [(-370, -168), (-350, -170), (-330, -172), (-310, -176), (-290, -181), (-270, -186), (-250, -191),
            (-230, -197), (-210, -202), (-190, -209), (-170, -215), (-150, -222), (-130, -228), (-110, -232),
            (-100, -234)]
_SBANK_E = [(-100, -234), (-90, -236), (-70, -239), (-50, -241), (-30, -242), (-10, -243), (10, -242),
            (30, -239), (50, -236), (70, -231), (90, -228), (110, -226), (130, -226), (150, -227),
            (170, -229), (190, -231), (210, -235), (230, -239), (250, -245), (270, -253), (290, -260),
            (310, -267), (330, -272), (350, -276), (370, -279)]
_TOWPATH_S = [(-105, -265), (16, -268), (92, -262), (172, -258), (225, -272), (270, -288), (305, -298),
              (340, -302), (370, -292)]
_PARK_W = [(-140, 182), (-195, 208), (-208, 255), (-212, 300), (-215, 355)]
_LOOKOUT = [(8, 122), (0, 165), (-20, 208), (-8, 255), (-12, 300), (10, 335), (13, 355)]
_ZOODR_W = [(168, 192), (145, 235), (132, 284), (108, 324), (62, 340), (10, 335)]
_WESTAVE = [(-128, 12), (-192, 14), (-222, 24), (-258, 36), (-300, 46), (-340, 60), (-370, 68)]
_EASTAVE = [(152, 0), (205, 10), (268, 2), (330, -18), (370, -29)]
_PIPPIN = [(268, 2), (272, -28), (262, -70), (255, -102), (254, -140), (264, -172), (262, -198)]
_MARKET_S = [_RING[21], (165, -95), (210, -97), (255, -102)]

DISTRICTS = [
    dict(id="OldTown", name="Old Town", kind="downtown", ground="paved", label_at=(70, -40),
         poly=_shrink(_RING)),
    dict(id="CentralPark", name="Central Park", kind="park", label_at=(-120, 165),
         poly=_shrink(_RING[6:11] + [(-128, 116), (-140, 119)] + _PARK_W + _LOOKOUT[::-1][:-1])),
    dict(id="WillowEnd", name="Willow End", kind="petshop", label_at=(-195, 60),
         poly=_shrink(_RING[10:13] + _WESTAVE[1:3] + [(-222, 136), (-222, 182), (-140, 182),
                                                      (-140, 119), (-128, 116)])),
    dict(id="Fernhill", name="Fernhill", kind="suburb", label_at=(-300, 205),
         poly=_shrink(_PARK_W + [(-370, 355)] + _WESTAVE[::-1][:-2] + [(-222, 136), (-222, 182)])),
    dict(id="MapleRise", name="Maple Rise", kind="residential", label_at=(40, 175),
         poly=_shrink(_LOOKOUT[:6] + _ZOODR_W[::-1][1:] + [(118, 142), _RING[4], _RING[5]])),
    dict(id="Zoo", name="Zoo Grounds", kind="zoo", label_at=(300, 195),
         poly=_shrink(_ZOODR_W[:4] + [(115, 365), (370, 365), (370, 128), (272, 110), (232, 143)])),
    dict(id="OrchardHill", name="Orchard Hill", kind="residential", label_at=(200, 110),
         poly=_shrink(_EASTAVE + [(370, 128), (272, 110), (232, 143), (168, 192), (118, 142)] + _RING[4:0:-1])),
    dict(id="OrchardHillSouth", name="Pippin Hill", kind="residential", label_at=(318, -110),
         poly=_shrink(_EASTAVE[2:] + [(370, -250), (350, -247), (330, -243), (310, -238), (290, -231),
                                      (270, -224), (262, -221)] + _PIPPIN[::-1][:-1])),
    dict(id="LanternMarket", name="Lantern Market", kind="market",
         poly=_shrink(_EASTAVE[:3] + _PIPPIN[1:4] + _MARKET_S[::-1][1:] + _RING[22:24])),
    dict(id="Westbrook", name="Westbrook", kind="residential",
         poly=_shrink(_RING[12:15] + [(-145, -110), (-172, -158)] + _NBANK + _WESTAVE[::-1][:-1])),
    dict(id="CanalQuarter", name="Canal Quarter", kind="riverside", label_at=(60, -150),
         poly=_shrink(_RING[14:22] + _MARKET_S[1:] + _PIPPIN[4:] + _NBANK_E + [(-172, -158), (-145, -110)])),
    dict(id="TanneryYards", name="Tannery Yards", kind="service", ground="gravel",
         poly=_shrink(_SBANK_W + [(-105, -265), (-125, -298), (-160, -320), (-180, -370), (-370, -370)])),
    dict(id="BoathouseRow", name="Boathouse Row", kind="riverside", label_at=(140, -243), label_size=6.0,
         poly=_shrink(_SBANK_E + [(370, -292)] + _TOWPATH_S[::-1][1:])),
    dict(id="Willowbrook", name="Willowbrook", kind="suburb",
         poly=_shrink(_TOWPATH_S + [(370, -370), (-180, -370), (-160, -320), (-125, -298)])),
]

# =============================================================================== LANDMARKS
LANDMARKS = {
    "PetShop": dict(name="Pet Shop", center=(-165, 145),
                    poly=[(-177, 135), (-153, 135), (-153, 155), (-177, 155)],
                    facing=(0.0, -1.0), road="WillowSt",
                    expansion_poly=[(-181, 136), (-181, 159), (-150, 159), (-150, 177), (-217, 177), (-217, 149)]),
    "Zoo": dict(name="City Zoo", center=(248, 268),
                poly=[(182, 206), (212, 178), (250, 162), (288, 152), (330, 167), (345, 215), (345, 292),
                      (330, 337), (280, 348), (200, 348), (150, 340), (150, 300), (160, 257), (168, 228)],
                entrance=(182, 206), entrance_facing=(-0.707, -0.707),
                incident_at=(157, 270)),
    "CentralPark": dict(name="Central Park", center=(-110, 240),
                        poly=[(-95, 124), (-60, 138), (-12, 146), (-14, 165), (-32, 208), (-22, 255),
                              (-26, 300), (-8, 340), (-200, 345), (-200, 300), (-196, 255), (-185, 214),
                              (-140, 190), (-133, 135), (-115, 128)]),
    "ServiceYard": dict(name="Container Yard", center=(-256, -303),
                        poly=[(-292, -288), (-220, -288), (-220, -318), (-288, -318)]),
    "TownSquare": dict(name="Town Square", center=(-12, 16),
                       poly=[(10, 36), (-32, 39), (-35, -3), (7, -7)]),
    "Lookout": dict(name="Lookout Hill", center=(-118, 302),
                    poly=[(-128, 294), (-108, 294), (-108, 310), (-128, 310)]),
    "Riverwalk": dict(name="Lock Plaza", center=(47, -200),
                      poly=[(30, -196), (64, -193), (64, -205), (30, -207)]),
    "SchoolYard": dict(name="Willowbrook School", center=(-58, -308),
                       poly=[(-88, -282), (-30, -282), (-30, -335), (-88, -335)]),
}

# =============================================================================== PATHS
PATHS = [
    dict(id="ParkLoop", kind="park", width=3.0,
         path=[(-50, 212), (-62, 245), (-95, 262), (-130, 250), (-145, 212), (-130, 178), (-95, 165),
               (-60, 178), (-50, 212)]),
    dict(id="ParkTip", kind="park", width=3.5, path=[(-68, 136), (-75, 152), (-95, 165)]),
    dict(id="PetShopGate", kind="park", width=3.0, path=[(-165, 178), (-150, 186), (-130, 178)]),
    dict(id="BellGate", kind="park", width=3.5, path=[(-30, 140), (-45, 160), (-60, 178)]),
    dict(id="LookoutGate", kind="park", width=3.0, path=[(-34, 210), (-50, 212)]),
    dict(id="LookoutTrail", kind="trail", width=2.5,
         path=[(-95, 262), (-100, 282), (-118, 302), (-140, 318), (-170, 336)]),
    dict(id="ParkNorth", kind="park", width=3.0, path=[(-62, 245), (-42, 280), (-30, 322)]),
    dict(id="Riverwalk", kind="riverwalk", width=4.0,
         path=[(-165, -180), (-110, -197), (-50, -203), (0, -206), (40, -201), (110, -193), (160, -194),
               (215, -202), (262, -214)]),
    dict(id="TowpathWalk", kind="riverwalk", width=3.0,
         path=[(-95, -246), (-30, -252), (30, -249), (90, -240), (150, -238), (170, -240)]),
    dict(id="SquareCross", kind="plaza", width=4.0, path=[(-32, 39), (7, -7)]),
]

# =============================================================================== NO_BUILD
NO_BUILD = [
    dict(id="ZooParking", reason="zoo visitor parking lot at the end of the boulevard",
         poly=[(118, 166), (146, 196), (138, 220), (104, 204)]),
    dict(id="OldTownCourtyard", reason="hidden courtyard reached from Tanner's Alley (raccoon den)",
         poly=[(-80, -20), (-66, -20), (-66, -34), (-80, -34)]),
    dict(id="Wharf", reason="open canal-side quay of the Tannery Yards",
         poly=[(-305, -182), (-258, -190), (-258, -199), (-305, -199)]),
    dict(id="CobblerYard", reason="hidden Old Town courtyard behind the Cobbler Lane shops",
         poly=[(-90, 30), (-76, 30), (-76, 46), (-90, 46)]),
    dict(id="CanalGardens", reason="community allotment gardens in the middle of the Canal Quarter east block",
         poly=[(50, -135), (95, -130), (98, -156), (50, -160)]),
    dict(id="BrookLot", reason="overgrown empty lot between Brook Street and the canal",
         poly=[(-262, -110), (-232, -108), (-232, -145), (-262, -150)]),
]

# =============================================================================== GAMEPLAY HINTS
ANIMAL_ZONES = [
    dict(id="ZooBreach", center=(150, 268), radius=45, habitat="zoo edge / backyards",
         animals=["giraffe", "zebra"], notes="breach in the zoo's west wall; big animals linger here"),
    dict(id="MapleBackyards", center=(60, 265), radius=60, habitat="backyards",
         animals=["giraffe", "tortoise", "goat"], notes="giraffe peeking over Maple Rise fences"),
    dict(id="ParkTrees", center=(-140, 280), radius=60, habitat="park trees",
         animals=["monkey", "lemur", "sloth"], notes="monkeys in the tree clusters around Lookout Hill"),
    dict(id="DuckPond", center=(-95, 212), radius=40, habitat="pond", animals=["flamingo", "pelican"],
         notes="flamingos wading at the duck pond"),
    dict(id="OldTownAlleys", center=(-70, -35), radius=50, habitat="alleys", animals=["raccoon", "red panda"],
         notes="raccoons raiding bins along Tanner's Alley"),
    dict(id="Rooftops", center=(40, 60), radius=50, habitat="rooftops", animals=["parrot", "toucan"],
         notes="parrots on Old Town rooftops along the boulevard"),
    dict(id="CanalPenguins", center=(0, -215), radius=50, habitat="canal", animals=["penguin", "otter"],
         notes="penguins sliding off the canal steps by Bridge Street and Lock Plaza"),
    dict(id="Warehouses", center=(-250, -275), radius=60, habitat="warehouses",
         animals=["lizard", "snake", "tortoise"], notes="reptiles warming up in the Tannery Yards"),
    dict(id="Gardens", center=(140, -300), radius=60, habitat="suburb gardens",
         animals=["meerkat", "rabbit", "kangaroo"], notes="burrowers in the Willowbrook lawns"),
    dict(id="FernhillYards", center=(-300, 230), radius=55, habitat="suburb backyards",
         animals=["kangaroo", "ostrich"], notes="hopping between Fernhill backyards"),
]

HIDING_SPOTS = [
    dict(id="UnderBridgeSt", at=(4, -226), notes="ledge under the Bridge Street bridge"),
    dict(id="UnderTanneryBridge", at=(-200, -196), notes="under the Tannery Road bridge"),
    dict(id="UnderMillBridge", at=(-338, -160), notes="under the old mill bridge (Brook Street)"),
    dict(id="WharfCrates", at=(-280, -192), notes="stacked crates on the wharf at the end of Wharf Alley"),
    dict(id="ContainerYard", at=(-255, -305), notes="gap between shipping containers"),
    dict(id="CourtyardBins", at=(-73, -27), notes="hidden Old Town courtyard with bins"),
    dict(id="ClocktowerAlley", at=(15, 90), notes="behind the shops on Clocktower Alley"),
    dict(id="LookoutBushes", at=(-150, 320), notes="thick bushes on the back of Lookout Hill"),
    dict(id="PondReeds", at=(-128, 212), notes="reeds on the duck pond's west bank"),
    dict(id="AcornCourt", at=(80, 305), notes="hedge behind the Acorn Court cul-de-sac"),
    dict(id="FernCourt", at=(-335, 300), notes="woodland edge beyond Fern Court"),
    dict(id="BrookLot", at=(-248, -130), notes="tall grass in the empty lot on Brook Street"),
    dict(id="ZooParkingHedge", at=(110, 200), notes="hedge around the zoo parking lot"),
    dict(id="CanalCulDeSac", at=(325, -232), notes="boat ramp at the end of Canal Street"),
]

# heading_deg: degrees CCW from +X (east); 90 = facing north, i.e. looking at the shop door.
PLAYER_SPAWN = dict(at=(-160, 129.5), heading_deg=90.0)

# =============================================================================== VIEWS
VIEWS = {
    "overview": ((-150, -560, 480), (20, 30, 0), 24),
    "downtown": ((75, -60, 42), (-10, 20, 0), 30),
    "petshop": ((-188, 40, 22), (-165, 145, 3), 30),
    "zoo": ((-12, 14, 30), (200, 228, 0), 30),
    "park": ((0, 140, 50), (-110, 250, 0), 28),
    "canal": ((80, -160, 22), (-30, -228, 0), 28),
    "service": ((-120, -195, 70), (-262, -292, 0), 26),
    "suburb": ((40, -200, 60), (165, -312, 0), 28),
}
