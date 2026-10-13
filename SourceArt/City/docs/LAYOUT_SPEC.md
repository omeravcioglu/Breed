# City Layout Spec (layout data modules)

A layout is a plain Python module in `layouts/` (e.g. `layouts/layout_main.py`). It is pure data:
the generator (`citygen/`) turns it into geometry. Layouts are **hand-authored**: every road,
district and landmark site is placed deliberately — never generated randomly.

Coordinates: meters, **x = east, y = north**, origin at the city center. The gameplay footprint is
`[-350, 350]^2`; the ground extends to `±420` (outskirts / map-edge treatment).
Top-down renders are 2048 px for 840 m: `x = px/2048*840 - 420`, `y = 420 - py/2048*840`.

## Build & check
```
./run.sh --layout <module> --phases terrain,roads --renders map,zoning,views --tag <tag>
```
Prints a JSON report (`validation.errors`, `validation.warnings`, `stats`) and writes
`renders/map_<tag>.png` (lit top-down with labels), `renders/zoning_<tag>.png` (flat district
colors) and `renders/view_<name>_<tag>.png` for each entry in `VIEWS` (EEVEE perspective).
A layout is acceptable only with **0 errors**; treat warnings seriously (overlaps, tight curves).

## Schema

### NODES
`{node_id: (x, y)}` or `{node_id: dict(pos=(x, y), culdesac=True | exit=True)}`
- A node shared by 2+ roads is an intersection. `culdesac=True` on a dead-end node makes a turning
  bulb. `exit=True` marks a road leaving the map (place exits at/just inside ±420).

### ROADS
`[dict(id, name, cls, path=[node_id | (x, y), ...], marking=None?)]`
- `cls` in `main | secondary | side | alley`.
  Asphalt / each sidewalk / total corridor width:
  `main 11 / 3.5 / 18 m`, `secondary 8 / 2.5 / 13 m`, `side 6 / 2.0 / 10 m`, `alley 4.5 / 0 / 4.5 m`.
- The centerline is a smooth Catmull-Rom spline through all path points; intermediate `(x, y)`
  tuples shape curves. **Every crossing of two roads must be a shared node** (validator error otherwise).
- A road passes smoothly *through* nodes it shares with other roads (continuous avenue).

Design rules (enforced or warned by the validator):
- Edges between intersections: ideally **>= 30 m** (minimum ~20 m for side streets).
- Intersection angles **>= 50 deg** where possible (< 35 deg is warned and looks bad).
- Curve radius: main >= 30 m, secondary >= 20 m, side >= 14 m, alley >= 8 m.
- No more than 4 roads per node; prefer T-junctions and 4-ways; offset T's feel organic.
- Parallel roads need their corridors not to overlap (main+main: >= 25 m apart centerline).

### Block sizing (so Phase 3 buildings fit)
Buildings are placed automatically along road frontage, facing the road, behind the sidewalk.
Typical lot depths: downtown 12-20 m, residential 20-35 m (house + yard), suburb 30-45 m,
service 20-40 m. So distance between parallel road centerlines should be roughly:
- downtown 55-90 m (two building rows + optional alley in the middle),
- residential 70-110 m, suburb 90-140 m, service 70-130 m.

### RIVER (optional, one)
`dict(name, path=[(x, y), ...], width)` — a canal that crosses the whole map boundary-to-boundary
(the path ends must lie outside ±420; they are auto-extended). Width 16-26 m. Every road that crosses
it automatically gets a **bridge** (deck, fascia, railings). Keep crossings near-perpendicular
(>= 60 deg) and limit them to 3-6 bridges.

### PONDS
`[dict(id, center, radii=[r0, r1, ...], rot=0, bank=3.0)]` — smooth star-shaped blob; radii evenly
around the circle. Must not touch roads.

### HILLS
`[dict(id, center, radius, height, squash=(sx, sy), rot=0)]` — smooth mound (cosine profile). Keep
height <= 12 m, radius 30-70 m; must not touch roads (keep them in parks).

### DISTRICTS
`[dict(id, name, kind, poly=[(x, y), ...], ground=None|'paved'|'gravel'|'plaza', label_at=None)]`
- `kind` drives building placement:
  - `downtown`: dense 2-5 storey shops / mixed-use / apartments, small setbacks, few gaps.
  - `market`: 1-2 storey shops, awnings, very walkable.
  - `petshop`: the pet-shop neighborhood: friendly mix of small shops + houses.
  - `residential`: townhouses + 2-storey houses, front yards, some gaps.
  - `suburb`: detached houses with big yards, garages, more gaps.
  - `service`: warehouses, sheds, utility buildings, yards, alleys.
  - `riverside`: low-density cafes / boathouses / small shops along the canal.
  - `park`, `zoo`: no generic buildings.
- Polygons may include road corridors (they are zoning areas) but must not overlap each other
  much, and must not cover the river if `ground` is set (a ground plate would hide the water).
- `ground='paved'` lays a concrete plate (downtown backlots), `'gravel'` for service yards.

### LANDMARKS (reserved sites, built in Phase 4)
`{site_id: dict(name, center=(x, y), poly=[...], ...)}`. Site polygons must **not** overlap roads /
sidewalks; generic buildings are never placed inside them. Required sites:
- `PetShop`: `facing=(dx, dy)` (unit vector from the shop front toward its street), `road=<road id>`,
  lot ~24 x 20 m, plus `expansion_poly` — an adjacent reserved plot (>= 30 x 25 m) for growth
  (future kennels, breeding rooms, aviary...). Central, easy to find, near the park.
- `Zoo`: 130-200 m across; `entrance=(x, y)` + `entrance_facing=(dx, dy)` on a main/secondary road;
  `incident_at=(x, y)` = point on the zoo boundary (facing the city) where the breach happened.
- `CentralPark` (or any park site): the park area (ponds/hills/paths go inside).
- `ServiceYard`: open work yard in the service district (containers, crates, hiding spots).
- `TownSquare`: downtown plaza (~35-50 m) — fountain / clock tower landmark.
- Optional extras (0-4): e.g. `Riverwalk`, `MarketStreet`, `Lookout`, `OpenLot`, `SchoolYard`...

### PATHS (footpaths, built in Phase 4)
`[dict(id, kind='park'|'riverwalk'|'trail'|'plaza', width=3.0, path=[(x, y), ...])]`

### NO_BUILD
`[dict(id, poly, reason)]` — intentional open spaces kept clear of generic buildings
(open lots, hidden courtyards, sports field, parking lot...).

### Gameplay hints
- `ANIMAL_ZONES = [dict(id, center, radius, habitat, animals=[...], notes)]` — where escaped animals
  roam (e.g. monkeys in park trees, penguins at the canal, flamingos at the pond, raccoons in alleys,
  giraffe peeking over suburb backyards, lizards in warehouses, parrots on downtown rooftops).
- `HIDING_SPOTS = [dict(id, at=(x, y), notes)]`
- `PLAYER_SPAWN = dict(at=(x, y), heading_deg=..)` — in front of the pet shop.

### VIEWS (review cameras)
`{name: ((x, y, z), (tx, ty, tz), lens_mm)}` — 4-8 views: overview, downtown, pet shop, zoo, park...

## Quality bar
Organic, handcrafted, readable. Distinct districts with personality; a clear hierarchy of
main → secondary → side → alley; loops for exploration (no dead-end-only networks); some
cul-de-sacs in suburbs; alleys behind downtown and service buildings; the pet shop central and
easy to return to; the zoo a memorable destination; the canal and park as natural landmarks.
