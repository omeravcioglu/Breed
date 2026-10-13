# Landmark Spec (Phase 4)

Landmarks are the hand-placed special areas: the **Pet Shop** (home base), the **Zoo** (incident
origin), **Central Park**, the **Service Yard**, the **Town Square**, plus optional extras from the
layout (`LANDMARKS` in `layouts/layout_main.py`). Each kind has a builder module in
`citygen/landmarks/<module>.py` exposing `build(S)`; `S` is a `citygen.lmkit.Site`.
Footpaths (`layout.PATHS`) are drawn automatically before the sites.

## Module routing (citygen/landmarks/__init__.py)
- Sites (`LANDMARKS`): PetShop->`petshop`, MapleGreen->`maple_green`, OpenLot->`open_lot`, Zoo->`zoo`,
  CentralPark->`park`, Lookout->`lookout`, TownSquare->`town_square`, Marina->`marina`,
  ServiceYard->`service_yard`. Each module exposes `build(S)`.
- NO_BUILD areas: ZooLanding/ZooForecourt/ZooParking/ZooBackLot->`zoo`, CrescentCommons/
  RiverwalkGardens->`park`, LanternCourt/CobblerYard/BoathouseSlip->`courts`, NetYard->`service_yard`.
  The module exposes `build_area(S)`; `S.data` is the NO_BUILD entry, `S.poly` its polygon,
  `S.id` its id (no facing: the local frame is axis-aligned unless you set `S.rot`).
- Districts of kind `park` (CentralPark, LookoutPark, WillowWoods) -> `park.build_district(S)`.
- Global pass: `hiding_spots.build_all(ctx)` (runs last; dresses `layout.HIDING_SPOTS`).

## Build & preview
```
# fast: only your modules, no generic buildings/props (a few seconds), with your own cameras
./run.sh --layout layout_main --phases terrain,roads,kit,landmarks --landmark-modules zoo --renders "" \
         --cams _tmp/<you>_cams.json --tag <tag>
# in context: full city (buildings + street dressing), ~25 s + renders
./run.sh --layout layout_main --cams _tmp/<you>_cams.json --renders "" --tag <tag>
```
`--cams` takes a JSON file `{name: [[x, y, z], [tx, ty, tz], lens_mm]}` and writes
`renders/cam_<name>_<tag>.png` (EEVEE). The JSON report lists `landmarks.built / missing / errors`.

## The Site API (citygen/lmkit.py)
- `S.data` (the LANDMARKS entry), `S.poly`, `S.center`, `S.facing`, `S.rot`, `S.rng` (seeded).
- Site frame: origin = center, local **-Y faces the street / entrance** (like kit pieces).
  `S.to_world(lx, ly)`, `S.to_local(p)`; `S.put(..., local=True)` uses the site frame.
- `S.put(piece, x, y, z=None, rot=0, recolor={'wall': 'M_Wall_Sky', ...}, scale=(sx,sy,sz), local=False, sub=None)`
  -> linked kit instance (z defaults to ground incl. hills).
- `S.building(BuildingSpec(...), origin, rot)` -> a modular building from the kit through the
  assembler (same code as the city buildings). Import `from citygen.assembler import BuildingSpec, H3, H4`.
  `BuildingSpec(archetype, nw, nd, floors, colors, roof='flat'|'gable_side'|'gable_front'|'gable_low',
  ground_h=H3|H4, feats={...})` — archetypes: shop, mixed, apartment, commercial, cafe, townhouse,
  house, warehouse, shed. colors: dict(wall, trim, door, awning, roof, sign) of palette names.
- `S.mesh(name, MeshBuilder)` for custom geometry (signs, gates, enclosures, fountains...).
  Use `citygen.meshutil.MeshBuilder` and `citygen.facade` helpers; palette materials only.
- `S.paving(name, poly, mat, z)`, `S.path_ribbon(name, pts, width, mat)`, `S.pool(name, outline, ...)`,
  `S.fence_along(pts, piece, closed, gaps=[(point, width)])`, `S.scatter(pieces, count, poly, min_dist, ...)`,
  `S.register_lot(poly)` (keeps later street dressing out), `S.clear_of_roads(p)`, `S.ground_z(x, y)`.

## Rules
- Stay **inside your site polygon** (and `expansion_poly` for the pet shop). Never cover roads,
  sidewalks or the canal. Check `S.clear_of_roads(p)` for anything near the edges.
- Kit first: reuse kit pieces and the assembler wherever possible; custom meshes only for truly
  unique hero elements (gate arch, big signs, fountain, enclosure rocks, aviary dome, ...).
- Same visual language as the kit: chunky, soft, readable, palette materials, recolor via `recolor=`.
- Name everything clearly (`LM_<Site>_<Thing>`); group with `sub=` (e.g. "Enclosures", "Gate").
- Gameplay first: leave open walkable space, clear entrances, hiding spots and sightlines.
- Ground level is z = -0.05 (grass); sidewalk / plinth level is 0.15. Buildings sit at 0.15.
- Performance: prefer instances; keep custom meshes lean (< 20k tris per site).

## Notes (lead integration pass)
- Collections: `sub=` names are resolved under the site's own collection (two sites may both use
  "Trees"); on a global name clash the new collection is named `<parent>.<sub>`.
- `S.mesh(name, mb, sub, rot=..)` takes a Z rotation; `S.building(..., base_z=..)` raises a building.
- `S.path_ribbon(..., clip=True)` drops segments deep under roads/sidewalks or over the canal; layout
  PATHS ends are auto-extended to the nearest sidewalk (<= 12 m) in `landmarks/__init__.py`.
- `net.clearance_hash()` includes cul-de-sac bulbs; `SegmentHash.blocked(p, extra>0)` scans neighbour cells.
- `hiding_spots.build_all` skips HIDING_SPOTS inside a dressed LANDMARKS / NO_BUILD polygon: the owning
  site builder must dress those spots (and may publish hide points in `ctx["lm_hides"]`). Its report is
  `ctx["hiding_anchors"]`, which `markers.py` uses to place the `GP_HidingSpot_*` empties.
- `Site.pool()` water sits below the flat ground plane unless raised: use raised rims / above-ground water.
- Kit instances may be tilted (X/Y rotation); `export_unity.py` writes full rotations (`quat_wxyz`).
