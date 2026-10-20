# City Foundation — Development Summary

Blender file: `SourceArt/City/City_Foundation.blend` (built by `build_city.py`, Blender 5.2 headless).
Review renders: `SourceArt/City/renders/*_final.png` (overview_SW/SE/NE/NW, beauty_top, map, zoning,
view_* and cam_* close-ups of every landmark and civic anchor).

## 1. What was created
**Phase 1 — road network & blockout ("Willowbrook", a canal city).** Hand-designed layout data
(`layouts/layout_main.py`) chosen by a design panel (3 candidate layouts, 3 judges, synthesis):
~8.8 km of streets in a main → secondary → side → alley hierarchy, 58 organic intersections with
filleted curbs, crosswalks and stop lines, 5 bridges over a 22 m canal, cul-de-sacs, 5 map exits,
riverwalk promenades, a park hill, two ponds, 19 districts.

**Phase 2 — modular kit (~125 pieces, `citygen/kit/`).** Walls/openings on a 3 m module with 3 m and
4 m floors (storefronts, doors, windows, garage, roller, industrial, corner-safe variants), roofs
and trims (flat, parapets, cornices, bands, plinths, gable roofs for 6/9/12 m spans, rooftop water
towers / AC / vents), facade details (striped awnings, signs, porches, balconies, fire escapes,
window boxes), street props (lights, signals, benches, bins, hydrants, cars, vans, trucks,
containers, utility poles) and nature (trees, bushes, hedges, fences). One shared palette; recolour
slots let every building vary without new meshes. Pieces publish snap metadata for the assembler.

**Phase 3 — buildings.** A frontage placer + block-interior infill assemble kit buildings by
district rules: dense downtown (4-6 floors), mixed-use corridors, attached rowhouse/apartment
residential, one detached-house suburb, industrial service yards, waterfront cafes facing the
canal. Paved lots, parking lots with driveways, kerb parking, traffic, utility poles with wires,
street trees, gap trees and a woodland edge.

**Phase 4 — landmarks.** Pet shop home base (paw medallion, play yard, readable expansion plot),
Maple Green (bandstand; spawn vista to the clock tower), Fairground Lot, Willowbrook Zoo (gate arch,
enclosures, aviary, the exploded breach with overturned truck + footprints), Central Park + Swan
Pond + Picnic Hill, Lookout Point, Willow Woods, Town Square (clock tower, market), Marina, hidden
courtyards, Container Yard (gantry crane), 8 civic anchors (police with animal control, fire
station, school, church, vet clinic, gas station, supermarket, diner), hiding-spot clutter.

**Phase 5 — organization.** Numbered collections, Unity-friendly prefixes, gameplay marker empties
(spawns, animal zones, hiding spots, expansion plot, zoo incident, map exits, civic anchors),
manifests and a road graph JSON, and an exporter for Unity.

## 2. How it is organized
See `README.md` (collections, prefixes, levels, commands) and the specs in `docs/`.
Everything is regenerated from data + code in seconds-to-minutes; edit the data, rebuild.

## 3. Assumptions
- 1 unit = 1 m, Z-up in Blender; city footprint ~700 x 700 m; flat ground except park hills/canal.
- American small-city vocabulary, stylized flat-colour materials (Unity Lit / URP Lit friendly).
- Buildings are exterior shells (no interiors yet); houses sit on a 0.35 m raised floor.
- Vehicles / pedestrians placed are static placeholders for future systems.

## Final build numbers (2026-10-20)
849 buildings (582 street-front + 267 block-interior, incl. 13 parking lots), ~94k objects, 12.3 MB
.blend, built in ~3 min; validation 0 errors / 0 warnings; 0 landmark errors. Props: 427 parked
cars, 55 traffic cars, 104 signals/street signs, 89 utility poles with wires, 122 street lights,
593 street + gap trees, ~3.4k woodland trees. 72 gameplay markers (spawns, 21 animal zones,
29 hiding spots, landmarks, expansion plot, zoo incident, map exits) + civic gameplay anchors.

## 4. Still to do
- **Unity import tooling (next):** an Editor script that reads `Export/Unity/instances.json`,
  `markers.json`, `roots.json` and instantiates prefabs made from `Kit/*.fbx` (verify the axis
  conversion once with a single prefab), then static-batch / GPU-instance by material.
- **Runtime budget:** ~8.6M rendered tris city-wide. Add LODs (trees, cars, rooftop clutter),
  impostors for the woodland, occlusion culling, merged trim runs (one cornice/band per facade
  side), a palette atlas or vertex-colour material (93 materials today), box colliders per
  building root, road/sidewalk meshes split into ~100 m tiles.
- **Look:** URP + warm haze / time-of-day lighting to match the references; the project is on the
  Built-in pipeline today. Optional map-edge hills/berm, an elevated highway landmark (ref 2).
- **Gameplay systems:** animal spawning from `GP_AnimalZone_*`, capture interactions at
  `GP_HidingSpot_*`, traffic / pedestrians on `Export/road_graph.json`, pet-shop expansion modules
  on `GP_ShopExpansionPlot` (kennels, breeding rooms, aviary), shop interior.
- **Open audit items (lower priority):** spawn intro camera, extra quay passages on long
  waterfront rows, corner pieces on party-wall contact sides, back doors facing neighbours.
