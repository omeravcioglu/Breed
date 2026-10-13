# Modular Building Kit Spec

The kit is built by Python in `citygen/kit/<family>.py` (families: `walls`, `roofs`, `details`,
`props`, `nature`). Each module defines `build(K)` and calls `K.add(name, meshbuilder, family,
category, bevel=0.0, meta={...})` once per piece. `citygen/kit/walls.py` is the reference style.

Build & preview a single family:
```
./run.sh --layout layout_empty --phases kit --kit-families walls --renders kitsheet --tag <tag>
```
-> `renders/kitsheet_<family>_<tag>.png` plus a JSON manifest (dims and tri counts per piece) and
`kit_errors` (tracebacks). Pieces sit on a shelf south of the map (y ~ -560 and below).

## Global conventions (MUST)
- Units = meters, Z up. Every piece's **front faces -Y** (Blender "front" view looks at it).
- **Grid:** facade module `W = 3.0 m`; floor heights `H3 = 3.0 m` (standard) and `H4 = 4.0 m`
  (tall ground floor for shops / warehouses). Wall thickness `T = 0.3 m`.
- **Facade-attached pieces** (walls, trims, awnings, signs, balconies, porches...): origin on the
  facade plane **y = 0**, centered in x on the module (3 m pieces span x in [-1.5, 1.5]),
  z = 0 at the piece's base (see each piece). Wall bodies occupy y in [0, 0.3] (into the building);
  anything sticking out of the facade goes to **y < 0**.
- **Corner pieces**: origin at the building's outer corner, bottom. Authored for the
  **front-right** corner (building occupies x <= 0, y >= 0 relative to the corner; the outward sides
  are -Y and +X). The assembler rotates them 90/180/270 deg for the other corners. Pieces that are
  symmetric around the corner (e.g. a centered pilaster) are fine too.
- **Props / free-standing pieces**: origin at ground level, bottom center of the footprint, front -Y.
- **Materials:** only names from `citygen/palette.py` (`MeshBuilder` takes material *names*).
  Recolorable parts MUST use these placeholder materials so buildings can vary per instance:
  | role    | placeholder material | used for |
  |---------|----------------------|----------|
  | wall    | `M_Wall_Cream`   | main wall body / gable infill / parapet body |
  | trim    | `M_Trim_White`   | frames, sills, cornices, bands, posts, fascia |
  | door    | `M_Door_Wood`    | doors, shutters |
  | awning  | `M_Awning_Red`   | awning fabric stripes, container/car body |
  | roof    | `M_Roof_Slate`   | pitched roof surfaces |
  | sign    | `M_Sign_Accent`  | sign face color |
  | foliage | `M_Foliage`      | tree crowns / bushes |
  Non-recolorable parts use any other palette material (glass `M_Glass` / `M_Glass_Shop`, metal,
  concrete, `M_Roof_Flat`, etc.).
- **Winding / normals:** use `MeshBuilder` helpers (box, prism, cylinder, sphere, strip, wall,
  face) and `citygen/facade.py` (panel, window, door, frame, sill, glass, reveal, wall_module).
  All produce outward normals. Hand-made `mb.face()` polygons must be CCW seen from outside.
- **Seams:** wall-module bodies must tile flush side by side (no bevel on wall bodies). Use
  `facade.bevelled(sub_mb, 0.02-0.04)` for chunky free-standing parts (posts, props, roof edges)
  to get the soft stylized edge, then `mb.extend(...)`.
- **Style:** clean, chunky, readable at 20-60 m. Slightly exaggerated proportions (thick frames,
  chunky sills, generous roof overhangs 0.4-0.5 m). Nothing thinner than 0.04 m. Low-poly but
  not cheap: a few deliberate bevels and silhouette details beat noise.
- **Budgets (tris):** wall module <= 350, roof segment <= 250, detail <= 450, small prop <= 350,
  tree <= 700, vehicle <= 900.
- **Names:** exactly as listed (prefix `KIT_`). You may add extra pieces (document them in the
  module docstring) but never rename the required ones.

## Piece list

### walls.py — category "Walls" / "Corners"   (all W = 3.0, origin bottom-center on facade)
| name | notes |
|---|---|
| `KIT_Wall_Plain_H3`, `KIT_Wall_Plain_H4` | plain body (done) |
| `KIT_Wall_Half_H3`, `KIT_Wall_Half_H4` | 1.5 m wide plain filler (x in [-0.75, 0.75]) |
| `KIT_Wall_Window_H3` | single 1.1 x 1.5 window, sill at 0.95 (done) |
| `KIT_Wall_WindowPair_H3` | two 0.8 x 1.5 windows |
| `KIT_Wall_WindowWide_H3` | 2.2 x 1.4 window, 2 vertical mullions (apartments / offices) |
| `KIT_Wall_WindowShutter_H3` | single window + two shutters (`M_Door_Wood`) with slat detail (houses) |
| `KIT_Wall_BalconyDoor_H3` | glazed French door 1.3 x 2.4 to floor level (pairs with KIT_Balcony_3m) |
| `KIT_Wall_Door_H3` | residential front door 1.0 x 2.25 (done) |
| `KIT_Wall_DoorGlass_H3` | door with glazed upper half + small transom (apartment lobby) |
| `KIT_Wall_Garage_H3` | sectional garage door 2.6 x 2.3 (`M_Trim_White`), horizontal panel grooves |
| `KIT_Wall_Window_H4` | tall-floor window 1.2 x 2.0, sill at 1.2 |
| `KIT_Wall_Door_H4` | service door 1.0 x 2.3 + transom window above, in a 4 m wall |
| `KIT_Wall_Storefront_H4` | shop display: glass 2.6 x 2.6 from 0.45 up (kick plate below), 1 vertical mullion + transom bar; glass `M_Glass_Shop`, frames `M_Trim_White` |
| `KIT_Wall_StorefrontDoor_H4` | glazed shop door 1.1 x 2.6 + side display glass in the same module |
| `KIT_Wall_RollerDoor_H4` | warehouse roller door 2.7 x 3.4 (`M_RollerDoor`, horizontal ribs) + housing box above |
| `KIT_Wall_Industrial_H3`, `KIT_Wall_Industrial_H4` | corrugated look: body `M_Wall_Cream` with vertical ribs every ~0.5 m |
| `KIT_Wall_IndustrialWindow_H3` | ribbon window 2.8 x 1.1 at z 1.2, 3 mullions, frames `M_Trim_Dark` |
| `KIT_Corner_H3`, `KIT_Corner_H4` | pilaster on the corner (done; may refine) |
| `KIT_Corner_Industrial_H3`, `KIT_Corner_Industrial_H4` | corner flashing/angle in `M_Metal_Dark` |

### roofs.py — categories "Roofs", "Trims", "Rooftop"
Trims (facade-attached; z = 0 is the bottom of the trim):
| name | notes |
|---|---|
| `KIT_Roof_Flat_1x1` | unit slab x,y in [-0.5, 0.5], z in [0, 0.2]; top `M_Roof_Flat`. Scaled by the assembler to the footprint. Origin bottom-center (NOT facade) |
| `KIT_Parapet_3m` | x in [-1.5, 1.5], y in [0, 0.3], z in [0, 0.7] body `M_Wall_Cream` + cap 0.7..0.8 overhanging 0.06 both sides (`M_Trim_White`) |
| `KIT_Parapet_Corner` | corner post covering the parapet corner, ~0.4 x 0.4 x 0.85 with cap |
| `KIT_Cornice_3m` | stepped 2-3 step profile, y in [-0.32, 0], z in [0, 0.4], `M_Trim_White` |
| `KIT_Cornice_Corner` | fills the outer corner of the cornice (x in [0, 0.32], y in [-0.32, 0]) |
| `KIT_FloorBand_3m` / `KIT_FloorBand_Corner` | band y in [-0.1, 0], z in [0, 0.18], `M_Trim_White` |
| `KIT_Plinth_3m` / `KIT_Plinth_Corner` | base course y in [-0.07, 0], z in [0, 0.45], `M_Wall_Concrete` |

Gable roofs — spans S = 6, 9 (pitch 35 deg, houses) and S = 12 (pitch 18 deg, warehouses).
The ridge runs along **X**. The roof covers the depth y in [0, S] (y = 0 is the outer face of the
front wall, y = S the outer face of the back wall) plus eave overhang 0.45 front and back.
**Origin = top of the front wall on the facade plane** (z = 0 is the wall top / eave line at y = 0).
Slab thickness ~0.18; top surfaces `M_Roof_Slate` (recolorable), fascia + soffit `M_Trim_White`,
ridge cap in `M_Roof_Slate`.
| name | notes |
|---|---|
| `KIT_Roof_Gable_S6_Mid` (also S9, S12) | 3 m segment, x in [-1.5, 1.5] |
| `KIT_Roof_Gable_S6_EndL` / `_EndR` (also S9, S12) | 0.45 m gable overhang for the -X end (x in [-0.45, 0]) / +X end (x in [0, 0.45]), with barge board trim |
| `KIT_Gable_S6` (also S9, S12) | triangular gable-end wall infill in WALL convention: outer face y = 0, x in [-S/2, S/2], z from 0 to the ridge, thickness 0.3 into +Y, body `M_Wall_Cream`, small attic vent detail (`M_Trim_White`). Sits on top of the end walls |

Rooftop / misc (origin bottom center):
`KIT_Roof_AC_Unit` (1.2 x 0.9 x 0.8, fan grill), `KIT_Roof_WaterTank` (classic wooden water tower on
steel legs, ~2.2 m dia, ~4 m tall, conical cap — a signature silhouette), `KIT_Roof_Vent`,
`KIT_Roof_Skylight` (1.5 x 1.5), `KIT_Roof_Access` (2.4 x 2.4 x 2.5 stair hut with door),
`KIT_Chimney` (0.8 x 0.8 x 2.4 brick `M_Wall_Brick` with cap; base at z = 0 extends 1 m below
for sinking into sloped roofs).

### details.py — categories "Awnings", "Signs", "Facade"
| name | origin / notes |
|---|---|
| `KIT_Awning_3m` | z = 0 = where the awning top meets the facade; slopes out to y = -1.5 and down 0.9; side cheeks; front valance 0.25; ALTERNATING stripes `M_Awning_Red` (recolor) / `M_Awning_Cream`; width 2.9. Placed above storefront glass (~z 3.3 on an H4 floor) |
| `KIT_Awning_Flat_3m` | modern flat canopy 3.0 x 1.2 x 0.15 + 2 tie rods to the wall (`M_Trim_White`), z = 0 = canopy underside |
| `KIT_Awning_Window` | small dome/sloped awning for a 1.1 m window (1.5 w), striped; z = 0 = top attach |
| `KIT_Sign_Board_3m` | fascia sign 2.8 x 0.7 x 0.12 (frame `M_Sign_Board`, face `M_Sign_Accent`), z = 0 bottom |
| `KIT_Sign_Blade` | projecting sign: wall bracket + 0.9 x 0.9 panel perpendicular to the facade reaching y = -1.2; z = 0 bottom of bracket |
| `KIT_Sign_Rooftop` | billboard 6 x 2.5 panel on two posts + catwalk (free-standing, origin bottom center) |
| `KIT_Porch_3m` | wood deck x in [-1.5, 1.5], y in [-2.2, 0], 0.35 high, 2 posts, sloped porch roof at ~2.7 (`M_Roof_Slate`) with fascia; integrated 2 steps at front center |
| `KIT_Steps_2` | 2 concrete steps 1.4 w x 0.6 deep x 0.35 (2 x 0.175, matches the 0.35 raised house floor and the porch deck; y in [-0.6, 0]) |
| `KIT_Canopy_Door` | small door canopy 1.6 x 0.8 with 2 brackets; z = 0 = canopy underside (placed at door head ~2.45) |
| `KIT_Balcony_3m` | slab 2.6 x 1.1 x 0.15 + railing 1.0 tall (`M_Metal_Dark` posts + top rail); z = 0 = slab top (= floor level) |
| `KIT_WindowBox` | 1.2 x 0.3 x 0.25 planter + flower blobs (`M_Foliage_Blossom`, `M_Foliage`); z = 0 = box bottom |
| `KIT_FireEscape_3m` | platform 2.8 x 1.2 + railing + diagonal stair down 3.0 m to the level below (`M_Metal_Dark`); z = 0 = platform top |
| `KIT_DownPipe_H3` | gutter downpipe 3 m (thin vertical pipe + brackets, `M_Metal`) at x = 0 |

### props.py — categories "Street", "Utility", "Vehicles"   (origin bottom center, front -Y)
`KIT_StreetLight` (6 m pole, arm over the road toward -Y, lamp head `M_Light_Emit`),
`KIT_TrafficLight` (pole + arm + 3-light head), `KIT_StreetSign` (street-name sign post),
`KIT_Bench` (1.8 m), `KIT_TrashBin`, `KIT_Dumpster` (2.0 x 1.2 x 1.3, `M_Dumpster`, lids),
`KIT_Crate` (1 m), `KIT_CrateStack` (3-4 crates), `KIT_Pallet`, `KIT_Barrel`,
`KIT_Container_6m` (6.1 x 2.44 x 2.6 corrugated, body `M_Awning_Red` recolor), `KIT_Hydrant`,
`KIT_Mailbox` (generic blue street mailbox), `KIT_Bollard`, `KIT_TrafficCone`, `KIT_Barrier`
(striped `M_Hazard` / `M_Hazard_Dark`), `KIT_BusStop` (3.5 m shelter), `KIT_BikeRack`,
`KIT_CafeTable` (table + 2 chairs + striped umbrella), `KIT_NewsStand`,
`KIT_Car_Sedan` (4.3 x 1.8 x 1.5, chunky stylized, body `M_Awning_Red` recolor, glass, wheels),
`KIT_Car_Van` (5.0 x 2.0 x 2.2), `KIT_Truck_Box` (box delivery truck 6.5 m).

### nature.py — categories "Trees", "Plants", "Fences", "Yard"   (origin bottom center)
`KIT_Tree_Round_A` (~6.5 m, chunky lollipop crown of 2-3 overlapping blobs, trunk `M_Bark`, crown
`M_Foliage` recolor), `KIT_Tree_Round_B` (~8 m, wider), `KIT_Tree_Cone` (pine, stacked cones ~8 m),
`KIT_Tree_Small` (young street tree ~4 m), `KIT_Tree_Palm` (exotic, for the zoo),
`KIT_Bush_A` (1.2 m), `KIT_Bush_B` (2.0 m wide), `KIT_Hedge_3m` (3 x 0.9 x 1.1, `M_Hedge`),
`KIT_Flowerbed_2m`, `KIT_Rock_A`, `KIT_Rock_B`,
`KIT_Fence_Picket_3m` (white picket 1.0 tall, x in [-1.5, 1.5] along X), `KIT_Fence_Wood_3m`
(privacy 1.8 tall), `KIT_Fence_Chain_3m` (chain-link 2.0 tall), `KIT_Fence_Iron_3m` (decorative
bars 1.6 tall, park / zoo), `KIT_Gate_Picket` (1.2 m), `KIT_Lamp_Park` (3.5 m lantern post),
`KIT_PicnicTable`, `KIT_Planter` (box planter with bush), `KIT_Doghouse` (cute, pet theme),
`KIT_Birdbath`, `KIT_Mailbox_House` (post mailbox), `KIT_Swing` (yard swing set).
Fences: origin at the fence line bottom center, run along X, thickness centered on y = 0.

## Snap metadata (published by the families, consumed by citygen/assembler.py)
Opening modules publish numeric datums in their custom properties / `K.REG[name]['meta']`:
`opening`, `head_top_z`, `sill_top_z`, `sill_bottom_z`, `threshold_z`, `trim_x`, `corner_ok`,
`corner_side` (corner variants), `grade_drop` (GarageGrade). Details publish `place_z` /
`place_z_on_H4` / `place_z_on_H3`. Houses use a 0.35 m raised ground floor (`assembler.HOUSE_RAISE`).
Corner-safe variants the assembler swaps in at building ends: `KIT_Wall_StorefrontCorner_H4` /
`...CornerL_H4`, `KIT_Wall_StorefrontDoorL_H4`, `KIT_Wall_IndustrialWindowEnd_H3/_H4`.
See each family module's docstring for the full list of extra pieces.
