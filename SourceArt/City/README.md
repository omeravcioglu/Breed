# Breed — City Foundation (Blender source)

Procedural-from-handcrafted-data city builder for the Breed project. The **layout is designed by
hand** as data (`layouts/layout_main.py`), and Python scripts turn it into a clean, organized,
Unity-friendly Blender scene: roads with real intersections, canal and bridges, terrain, a modular
building kit, buildings assembled from the kit, landmarks, street dressing and gameplay markers.

This folder lives **outside `Assets/`** on purpose: Unity never tries to import the `.blend`.
Export to Unity happens through `export_unity.py` (FBX + JSON).

## Quick start
```bash
# full rebuild -> City_Foundation.blend (+ review renders in renders/)
./run.sh --layout layout_main --out City_Foundation.blend --renders map,zoning,views,overview --tag main

# fast iteration on the road layout only
./run.sh --layout layout_main --phases terrain,roads --renders map,zoning --tag wip

# preview one kit family
./run.sh --layout layout_empty --phases kit --kit-families walls --renders kitsheet --tag walls

# Unity export (kit FBX per piece, environment FBX, instances.json)
"<blender.exe>" -b City_Foundation.blend --factory-startup --python export_unity.py -- --out Export/Unity
```
`run.sh` calls Blender 5.2 headless (Steam install path inside the script) and prints a JSON
report: validation errors/warnings, building/prop counts, kit manifest, timings.

## Pipeline phases (`build_city.py`)
| phase | module | result (collections under `CITY_Foundation`) |
|---|---|---|
| terrain | `citygen/terrain.py` | `01_Terrain`: ground split by the canal, canal walls/bed/water, ponds, park hill, district ground plates; `03_Zoning_Blockout` plates; `99_Annotations` labels |
| roads | `citygen/roads.py` | `02_Roads/*`: asphalt ribbons per road, filleted intersection patches, sidewalks + curbs, cul-de-sacs, lane paint, crosswalks, bridges |
| kit | `citygen/kit/*.py` | `KIT_Library`: the modular kit on a shelf south of the map (y < -490) |
| buildings | `citygen/placement.py` + `assembler.py` | `04_Buildings/BLD_<district>`: buildings as Empty roots with linked kit pieces; yards, fences, paths |
| landmarks | `citygen/landmarks/*.py` + `lmkit.py` | `05_Landmarks/LM_<site>`: pet shop, zoo, park, service yard, town square, footpaths |
| props | `citygen/dressing.py` | `06_Props/*`: street lights, trees, furniture, alley clutter, parked cars, traffic lights, edge forest |
| markers | `citygen/markers.py` | `07_Gameplay_Markers/*`: player spawns, animal zones, hiding spots, shop expansion plot, zoo incident, map exits |
| finalize | `citygen/finalize.py` | collection colors, units, viewport setup, `Export/city_manifest.json`, `Export/road_graph.json` |

## Conventions
- Meters, Z-up, x = east, y = north. City footprint `[-350, 350]^2`, ground to `±420`.
- Levels: ground `-0.05`, asphalt `0.0`, sidewalks / building plinths `0.15`.
- Naming prefixes: `RD_` road, `SW_` sidewalk, `IX_` intersections, `MK_` markings, `BR_` bridge,
  `TRN_` terrain, `WTR_` water, `ZN_` zoning, `KIT_` kit piece, `BLD_` building, `LM_` landmark,
  `PROP_` prop, `GP_` gameplay marker, `LBL_` label, `CAM_`/`LGT_` preview.
- Kit: 3 m facade module, 3 m floors (4 m shop ground floors), fronts face -Y; see `docs/KIT_SPEC.md`.
- Materials: one shared palette (`citygen/palette.py`, `M_` prefix, flat colors -> Unity Lit).
  Recolorable placeholder slots are swapped per instance (object-level material links).
- Buildings and props are **linked duplicates** of kit meshes: edit a kit piece once and every
  building updates. Custom properties (archetype, floors, habitat, ...) export to Unity via FBX.

## Docs
- `docs/DESIGN_BRIEF.md` — creative brief for the city.
- `docs/LAYOUT_SPEC.md` — layout data schema + design rules (roads, districts, landmarks, paths, gameplay hints).
- `docs/KIT_SPEC.md` — modular kit conventions and piece list.
- `docs/LANDMARK_SPEC.md` — landmark builder API and rules.

## Editing workflow
1. Edit `layouts/layout_main.py` (move a node, add a road, reshape a district) or a kit family.
2. Rebuild (seconds) and look at `renders/` — the validator reports overlaps, crossings, tight curves.
3. Hand-tweaks inside Blender are fine for one-off polish, but they are overwritten by a rebuild;
   prefer data/script edits for anything structural.
