import json
import os
import shutil
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPS_DIR = os.path.join(ROOT_DIR, "maps")
TILESETS_DIR = os.path.join(ROOT_DIR, "tilesets")
DIST_DIR = os.path.join(ROOT_DIR, "dist")


def parse_tsx(tsx_path):
    """Extract tileset metadata, collision tile IDs, and animations from a .tsx file."""
    tree = ET.parse(tsx_path)
    root = tree.getroot()

    image_el = root.find("image")
    image_source = os.path.basename(image_el.get("source")) if image_el is not None else ""
    image_width = int(image_el.get("width", 0)) if image_el is not None else 0
    image_height = int(image_el.get("height", 0)) if image_el is not None else 0

    tilewidth = int(root.get("tilewidth", 32))
    tileheight = int(root.get("tileheight", 32))
    tilecount = int(root.get("tilecount", 0))
    columns = int(root.get("columns", 0))
    name = root.get("name", os.path.splitext(os.path.basename(tsx_path))[0])

    tiles_by_id = {}

    for tile in root.findall("tile"):
        tid = int(tile.get("id"))
        entry = tiles_by_id.setdefault(tid, {"id": tid})

        has_collision = False
        objgroup = tile.find("objectgroup")
        if objgroup is not None and len(objgroup.findall("object")) > 0:
            has_collision = True

        props = tile.find("properties")
        if props is not None:
            for p in props.findall("property"):
                if p.get("name") == "collides" and p.get("value") == "true":
                    has_collision = True

        if has_collision:
            entry["properties"] = [{"name": "collides", "type": "bool", "value": True}]

        anim = tile.find("animation")
        if anim is not None:
            entry["animation"] = [
                {"duration": int(frame.get("duration")), "tileid": int(frame.get("tileid"))}
                for frame in anim.findall("frame")
            ]

    return {
        "columns": columns,
        "image": image_source,
        "imageheight": image_height,
        "imagewidth": image_width,
        "margin": 0,
        "name": name,
        "spacing": 0,
        "tilecount": tilecount,
        "tileheight": tileheight,
        "tilewidth": tilewidth,
        "tiles": list(tiles_by_id.values()),
    }


def build():
    tmj_path = os.path.join(MAPS_DIR, "sala.tmj")
    wam_path = os.path.join(MAPS_DIR, "sala.wam")

    with open(tmj_path, "r", encoding="utf-8") as f:
        mapdata = json.load(f)

    # Inline external .tsx references as WorkAdventure-compatible external-PNG tilesets
    resolved_tilesets = []
    for ts in mapdata.get("tilesets", []):
        if "source" in ts:
            tsx_rel = ts["source"]
            tsx_abs = os.path.normpath(os.path.join(MAPS_DIR, tsx_rel))
            parsed = parse_tsx(tsx_abs)
            parsed["firstgid"] = ts["firstgid"]
            resolved_tilesets.append(parsed)
        else:
            resolved_tilesets.append(ts)
    mapdata["tilesets"] = resolved_tilesets

    # Normalize Start -> start
    for layer in mapdata.get("layers", []):
        if layer.get("name") == "Start":
            layer["name"] = "start"

    # Convert parede-sc tilelayer into parede-acima objectlayer (above player)
    parede_layer = next(
        (l for l in mapdata.get("layers", []) if l.get("name") == "parede-sc" and l.get("type") == "tilelayer"),
        None,
    )
    if parede_layer:
        width = parede_layer["width"]
        obj_id = mapdata.get("nextobjectid", 1)
        next_layer_id = mapdata.get("nextlayerid", len(mapdata["layers"]) + 1)
        objects = []
        for idx, gid in enumerate(parede_layer["data"]):
            if gid > 0:
                col = idx % width
                row = idx // width
                objects.append({
                    "gid": gid,
                    "height": 32,
                    "id": obj_id,
                    "name": "",
                    "rotation": 0,
                    "type": "",
                    "visible": True,
                    "width": 32,
                    "x": col * 32,
                    "y": (row + 1) * 32,
                })
                obj_id += 1
        wall_above = {
            "draworder": "topdown",
            "id": next_layer_id,
            "name": "parede-acima",
            "objects": objects,
            "opacity": 1,
            "type": "objectgroup",
            "visible": True,
            "x": 0,
            "y": 0,
        }
        parede_idx = mapdata["layers"].index(parede_layer)
        mapdata["layers"].insert(parede_idx + 1, wall_above)
        mapdata["nextlayerid"] = next_layer_id + 1
        mapdata["nextobjectid"] = obj_id

    if os.path.exists(DIST_DIR):
        for entry in os.listdir(DIST_DIR):
            entry_path = os.path.join(DIST_DIR, entry)
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)
    else:
        os.makedirs(DIST_DIR, exist_ok=True)

    # Write map JSON & WAM
    with open(os.path.join(DIST_DIR, "sala.json"), "w", encoding="utf-8") as f:
        json.dump(mapdata, f, indent=1, ensure_ascii=False)

    shutil.copy2(wam_path, os.path.join(DIST_DIR, "sala.wam"))

    # Copy tileset PNGs referenced by the map
    for fname in os.listdir(TILESETS_DIR):
        if fname.lower().endswith(".png"):
            shutil.copy2(os.path.join(TILESETS_DIR, fname), os.path.join(DIST_DIR, fname))

    # Prevent GitHub Pages Jekyll from ignoring any files
    with open(os.path.join(DIST_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        pass

    print("Build concluido em dist/: sala.json, sala.wam e PNGs copiados.")


if __name__ == "__main__":
    build()
