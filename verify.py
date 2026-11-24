"""Check leaf inventory color regressions in a locally generated pack."""
import argparse
import json
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True)
    parser.add_argument("--minecraft-jar", required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.pack) as pack, zipfile.ZipFile(args.minecraft_jar) as vanilla:
        if pack.testzip() is not None:
            raise SystemExit("Pack ZIP integrity check failed")
        spruce_path = "assets/minecraft/items/spruce_leaves.json"
        spruce = json.loads(pack.read(spruce_path))["model"]
        expected = json.loads(vanilla.read(spruce_path))["model"]["tints"]
        if spruce.get("tints") != expected:
            raise SystemExit("Spruce inventory tint differs from vanilla 26.3")
        if spruce["model"] != "minecraft:item/spruce_leaves":
            raise SystemExit("Authored spruce inventory model is not selected")
        birch = json.loads(pack.read("assets/minecraft/items/birch_leaves.json"))["model"]
        if birch.get("tints"):
            raise SystemExit("Authored birch color should not have an extra item tint")
        print("PASS: ZIP integrity, spruce constant green tint, authored leaf model, birch colors")


if __name__ == "__main__":
    main()
