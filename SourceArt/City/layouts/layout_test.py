"""Tiny test layout for the road/terrain generator."""
NODES = {
    "A": (-200, 0), "B": (0, 0), "C": (200, 20), "D": (0, 150), "E": (0, -150),
    "F": (120, -120), "G": dict(pos=(160, -200), culdesac=True), "X1": dict(pos=(-420, 0), exit=True),
    "H": (-100, 100),
}
ROADS = [
    dict(id="Main", name="Harbor Ave", cls="main", path=["X1", "A", "B", (100, 10), "C"]),
    dict(id="North", name="Elm St", cls="secondary", path=["B", (10, 80), "D"]),
    dict(id="South", name="Pine St", cls="secondary", path=["B", "E"]),
    dict(id="Curve", cls="side", path=["E", (60, -160), "F", (90, -60), "C"]),
    dict(id="Cul", cls="side", path=["F", (150, -150), "G"]),
    dict(id="Alley1", cls="alley", path=["A", (-140, 60), "H", "D"]),
]
RIVER = dict(name="Test Canal", path=[(-400, -300), (-150, -80), (-60, 60), (100, 250), (300, 420)], width=20)
PONDS = [dict(id="Pond", center=(-200, -250), radii=[30, 24, 34, 26, 30, 22])]
HILLS = [dict(id="Hill", center=(220, 200), radius=60, height=10, squash=(1.0, 0.75))]
DISTRICTS = [
    dict(id="D1", name="Downtown", kind="downtown", poly=[(20, 20), (180, 30), (180, 140), (20, 140)], ground="paved"),
    dict(id="D2", name="Suburb", kind="suburb", poly=[(20, -20), (190, -20), (190, -230), (20, -230)]),
]
LANDMARKS = {}
VIEWS = {
    "ixB": ((40, -45, 30), (0, 0, 0), 30),
    "bridge": ((-60, -60, 18), (-105, 0, 0), 28),
    "culdesac": ((185, -170, 22), (160, -200, 0), 30),
    "nodeA": ((-170, -40, 25), (-200, 5, 0), 30),
}
VIEWS.update({
    "downtown": ((60, -30, 45), (100, 80, 0), 32),
    "suburb": ((60, -60, 35), (110, -150, 0), 30),
})
LANDMARKS = {
    "PetShop": dict(name="Pet Shop", center=(60, -40), facing=(0, 1), poly=[(45, -30), (75, -30), (75, -55), (45, -55)],
                    expansion_poly=[(78, -30), (110, -30), (110, -60), (78, -60)]),
}
PATHS = [dict(id="P1", kind="park", width=3.0, path=[(-260, -200), (-230, -220), (-200, -210), (-180, -230)])]
ANIMAL_ZONES = [dict(id="Pond", center=(-200, -250), radius=40, habitat="pond", animals=["flamingo"], notes="")]
HIDING_SPOTS = [dict(id="H1", at=(120, 60), notes="behind shops")]
PLAYER_SPAWN = dict(at=(60, -25), heading_deg=0)
VIEWS.update({
    "shopclose": ((70, 2, 9), (85, 30, 4), 35),
    "houseclose": ((95, -105, 8), (75, -125, 3), 35),
})
