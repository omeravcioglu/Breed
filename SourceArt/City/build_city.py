"""Entry point: build the Breed city foundation into a .blend.

Usage (from this folder):
    blender -b --factory-startup --python build_city.py -- [--layout layout_main]
            [--phases terrain,roads,kit,buildings,landmarks,props,markers]
            [--out City_Foundation.blend] [--renders map,zoning,views] [--render-dir renders]
            [--report report.json]

Every run rebuilds the scene from scratch (deterministic), so the layout data and kit code are
the source of truth. Hand edits should go into the data/scripts, or be made after the final build.
"""
import sys
sys.dont_write_bytecode = True  # several builds may run in parallel
import argparse
import importlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy  # noqa: E402

from citygen import config as C, scene, terrain, roads, validate, render  # noqa: E402

ALL_PHASES = ["terrain", "roads", "kit", "buildings", "landmarks", "props", "markers", "finalize"]


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", default="layout_main")
    ap.add_argument("--phases", default=",".join(ALL_PHASES))
    ap.add_argument("--out", default="")
    ap.add_argument("--renders", default="map,zoning")
    ap.add_argument("--render-dir", default=os.path.join(HERE, "renders"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--kit-families", default="")
    ap.add_argument("--landmark-modules", default="", help="only build these landmark modules (comma list)")
    ap.add_argument("--cams", default="", help="JSON file {name: [[x,y,z],[tx,ty,tz],lens]} of extra views")
    return ap.parse_args(argv)


def main():
    args = parse()
    t0 = time.time()
    phases = [p for p in args.phases.split(",") if p]
    layout = importlib.import_module(f"layouts.{args.layout}")
    scene.clear_scene()
    scene.ensure_hierarchy()
    ctx = dict(layout=layout, out=args.out)
    report = {}
    timings = {}
    report["timings"] = timings

    def lap(name, t_prev=[t0]):
        now = time.time()
        timings[name] = round(now - t_prev[0], 1)
        t_prev[0] = now

    river = terrain.River(layout.RIVER) if getattr(layout, "RIVER", None) else None
    ctx["river"] = river
    net = roads.Network(layout)  # graph only (cheap) - needed by most phases
    if "roads" in phases:
        net = roads.build(layout)
        roads.build_bridges(net, river.poly if river else None, river.hw if river else 0.0)
    ctx["net"] = net
    lap("roads")
    if "terrain" in phases:
        terrain.build_ground(layout, river)
        terrain.build_canal(river, net.clearance_hash(extra=0.0))
        terrain.build_ponds(layout)
        terrain.build_hills(layout)
        terrain.build_district_grounds(layout)
        terrain.build_zoning(layout)
        terrain.build_labels(layout, net)
    lap("terrain")

    if "kit" in phases:
        from citygen import kit
        fams = [f for f in args.kit_families.split(",") if f] or None
        ctx["kit"] = kit.build_kit(fams)
        if kit.ERRORS:
            report["kit_errors"] = kit.ERRORS
    lap("kit")
    if "buildings" in phases:
        from citygen import placement
        report["buildings"] = placement.populate(ctx)
    lap("buildings")
    if "landmarks" in phases:
        from citygen import landmarks
        only = set(m for m in args.landmark_modules.split(",") if m) or None
        report["landmarks"] = landmarks.build_all(ctx, only=only)
    lap("landmarks")
    if "props" in phases:
        from citygen import dressing
        report["props"] = dressing.populate(ctx)
    lap("props")
    if "markers" in phases:
        from citygen import markers
        report["markers"] = markers.build(ctx)
    if "finalize" in phases:
        from citygen import finalize
        report["finalize"] = finalize.run(ctx)
    lap("markers+finalize")

    v = validate.validate(layout, net, river)
    report["validation"] = v
    report["build_seconds"] = round(time.time() - t0, 1)
    report["object_count"] = len(bpy.data.objects)

    # ---- renders
    os.makedirs(args.render_dir, exist_ok=True)
    tag = f"_{args.tag}" if args.tag else ""
    rlist = [r for r in args.renders.split(",") if r]
    if "map" in rlist:
        render.map_top(os.path.join(args.render_dir, f"map{tag}.png"), res=2048, flat=True,
                       hide=("03_Zoning_Blockout",), show=("99_Annotations",))
    if "zoning" in rlist:
        render.map_top(os.path.join(args.render_dir, f"zoning{tag}.png"), res=2048, flat=True,
                       show=("03_Zoning_Blockout", "99_Annotations"))
    if "clean" in rlist:
        render.map_top(os.path.join(args.render_dir, f"clean{tag}.png"), res=2048, flat=False,
                       hide=("03_Zoning_Blockout", "99_Annotations", "KIT_Library"))
    if "views" in rlist and hasattr(layout, "VIEWS"):
        for name, (loc, tgt, lens) in layout.VIEWS.items():
            render.view(os.path.join(args.render_dir, f"view_{name}{tag}.png"), loc, tgt, lens=lens,
                        hide=("03_Zoning_Blockout", "99_Annotations", "KIT_Library"))
    if args.cams:
        with open(args.cams) as f:
            cams = json.load(f)
        for name, (loc, tgt, lens) in cams.items():
            render.view(os.path.join(args.render_dir, f"cam_{name}{tag}.png"), loc, tgt, lens=lens,
                        hide=("03_Zoning_Blockout", "99_Annotations", "KIT_Library"))
    if "overview" in rlist:
        # four oblique "drone" shots from the corners + an EEVEE top-down beauty map
        for nm, (sx, sy) in dict(SW=(-1, -1), SE=(1, -1), NE=(1, 1), NW=(-1, 1)).items():
            render.view(os.path.join(args.render_dir, f"overview_{nm}{tag}.png"),
                        (sx * 430.0, sy * 430.0, 330.0), (sx * 20.0, sy * 20.0, 0.0), lens=30,
                        res=(1920, 1080), hide=("03_Zoning_Blockout", "99_Annotations", "KIT_Library"))
        cam = render._camera("CAM_MapTop", (0.0, 0.0, 600.0), ortho_scale=2 * C.GROUND_HALF)
        render.render(os.path.join(args.render_dir, f"beauty_top{tag}.png"), cam, (2048, 2048), beauty=True,
                      hide=("03_Zoning_Blockout", "99_Annotations", "KIT_Library"))
    if "kitsheet" in rlist and "kit" in ctx:
        from citygen import kit
        for fam in sorted({r["family"] for r in kit.REG.values()}):
            kit.render_sheet(os.path.join(args.render_dir, f"kitsheet_{fam}{tag}.png"), family=fam)
        report["kit_manifest"] = kit.manifest()
        report["kit_errors"] = kit.ERRORS

    # leave the saved file in a sensible display state
    scene.set_visible("03_Zoning_Blockout", False)
    scene.set_visible("99_Annotations", False)
    if args.out:
        out = args.out if os.path.isabs(args.out) else os.path.join(HERE, args.out)
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
        report["saved"] = out
    s = json.dumps(report, indent=1, default=str)
    if args.report:
        with open(args.report, "w") as f:
            f.write(s)
    print("CITYGEN_REPORT_BEGIN")
    print(s)
    print("CITYGEN_REPORT_END")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        print("CITYGEN_FAILED")
        sys.exit(1)
