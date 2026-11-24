"""Unofficial local converter. Contains no Stay True or Minecraft artwork.

Supply original author downloads yourself; generated packs retain upstream rights.
"""
import pathlib, zipfile, json, io, re, hashlib, collections, copy
from PIL import Image
import argparse

def main():
    parser = argparse.ArgumentParser(description='Convert an original Stay True 1.21.5 pack to Minecraft Java 26.3 locally.')
    parser.add_argument('--input', required=True, type=pathlib.Path, help="Original author's Stay True 1.21.5 ZIP")
    parser.add_argument('--minecraft-jar', required=True, type=pathlib.Path, help='Minecraft Java 26.3 client JAR')
    parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path('Stay True 26.3 - Local Port.zip'))
    args = parser.parse_args()
    W = pathlib.Path(__file__).resolve().parent
    S = args.input.resolve()
    V = args.minecraft_jar.resolve()
    output_path = args.output.resolve()
    if output_path in (S, V):
        parser.error('Output must differ from both input files.')
    if not S.is_file() or not V.is_file():
        parser.error('Both input files must exist.')
    if hashlib.sha256(S.read_bytes()).hexdigest() != 'c61397d8e9d1f15e069f718c0bd61c5c347be1f3e18603ea576dccb570302c82':
        parser.error('Expected the unmodified official Stay True 1.21.5 ZIP (CurseForge file 6534716).')
    with zipfile.ZipFile(V) as version_jar:
        version = json.loads(version_jar.read('version.json'))
        if version.get('id') != '26.3':
            parser.error('This converter supports Minecraft Java 26.3 only.')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    a = zipfile.ZipFile(S)
    vanilla = zipfile.ZipFile(V)
    vanilla_names = set(vanilla.namelist())
    files = {n: a.read(n) for n in a.namelist() if not n.endswith('/')}
    changes = []

    def record(kind, name, detail):
        changes.append({'kind': kind, 'path': name, 'detail': detail})

    def putjson(name, obj):
        files[name] = (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()

    def image(data):
        return Image.open(io.BytesIO(data)).convert('RGBA')

    def png(im):
        b = io.BytesIO()
        im.save(b, format='PNG')
        return b.getvalue()

    def alias(old, new):
        if old in files:
            files[new] = files[old]
            record('texture_path', new, old)
            if old + '.mcmeta' in files:
                files[new + '.mcmeta'] = files[old + '.mcmeta']
    meta = json.loads(files['pack.mcmeta'])
    meta['pack'] = {'min_format': [97, 1], 'max_format': [97, 1], 'description': 'Stay True | HaiMcFly Update 34\nUnofficial local compatibility port for Minecraft 26.3'}
    putjson('pack.mcmeta', meta)
    for (old, new) in [('block/chain', 'block/iron_chain'), ('item/chain', 'item/iron_chain'), ('block/quartz_pillar', 'block/quartz_pillar_side'), ('block/purpur_pillar', 'block/purpur_pillar_side'), ('entity/armorstand/wood', 'entity/armorstand/armorstand'), ('environment/sun', 'environment/celestial/sun'), ('entity/squid', 'entity/squid/squid')]:
        alias('assets/minecraft/textures/' + old + '.png', 'assets/minecraft/textures/' + new + '.png')
    cow = 'assets/minecraft/textures/entity/cow/cow_temperate.png'
    if 'assets/minecraft/textures/entity/cow/cow.png' in files:
        out = image(vanilla.read(cow))
        legacy = image(files['assets/minecraft/textures/entity/cow/cow.png'])
        out.paste(legacy, (0, 0))
        files[cow] = png(out)
        record('legacy_texture', cow, 'Reuse legacy 64x32 adult cow skin in upper UV region; retain vanilla new regions and baby variants')
    maps = json.loads((W / 'sign-mapping.json').read_text())
    for row in maps['sign']:
        if row[0] == [0, 28, 24, 30]:
            row[1] = [26, 0, 50, 2, int(Image.Transpose.FLIP_TOP_BOTTOM)]
        if row[0] == [28, 30, 30, 32]:
            row[1] = [4, 14, 6, 16, int(Image.Transpose.ROTATE_180)]
    for row in maps['hanging_sign']:
        if row[0] == [18, 16, 32, 26]:
            row[1] = [18, 14, 32, 24, None]
        if row[0] == [16, 16, 18, 26]:
            row[1] = [16, 14, 18, 24, None]
    for old in list(files):
        if old.startswith('assets/minecraft/textures/entity/signs/') and old.endswith('.png'):
            hanging = '/hanging/' in old
            wood = pathlib.PurePosixPath(old).stem
            kind = 'hanging_sign' if hanging else 'sign'
            src = image(files[old])
            out = Image.new('RGBA', (32, 32))
            for (dst, source) in maps[kind]:
                tile = src.crop(source[:4])
                tile = tile if source[4] is None else tile.transpose(source[4])
                out.paste(tile, dst[:2])
            dest = f'assets/minecraft/textures/block/{wood}_{kind}.png'
            files[dest] = png(out)
            record('sign_uv_repack', dest, old)
            if not hanging:
                gui = Image.new('RGBA', (24, 26))
                gui.paste(src.crop((2, 2, 26, 14)), (0, 0))
                gui.paste(src.crop((2, 16, 4, 30)), (11, 12))
                dest = f'assets/minecraft/textures/gui/signs/{wood}.png'
                files[dest] = png(gui)
                record('sign_gui', dest, old)
    for name in list(files):
        if '/models/' in name and name.endswith('.json'):
            d = json.loads(files[name].decode('utf-8-sig'))
            count = 0
            for element in d.get('elements', []):
                if 'shade' in element:
                    if element.pop('shade') is False:
                        element['shade_direction_override'] = 'up'
                    count += 1
            if count:
                putjson(name, d)
                record('model_shading', name, count)
    for wood in ['acacia', 'birch', 'dark_oak', 'jungle', 'mangrove', 'pale_oak', 'spruce']:
        name = f'assets/minecraft/models/item/{wood}_leaves.json'
        d = json.loads(files[name].decode('utf-8-sig'))
        if wood == 'pale_oak':
            d['parent'] = 'minecraft:block/pale_oak_leaves'
            putjson(name, d)
        target = f'assets/minecraft/items/{wood}_leaves.json'
        definition = json.loads(vanilla.read(target))
        definition['model']['model'] = f'minecraft:item/{wood}_leaves'
        if wood == 'birch':
            definition['model'].pop('tints', None)
        putjson(target, definition)
        record('item_definition', target, 'Select authored Stay True inventory model')
    chest = 'assets/minecraft/models/item/chest.json'
    d = json.loads(files[chest].decode('utf-8-sig'))
    d['parent'] = 'minecraft:item/template_chest'
    putjson(chest, d)
    record('legacy_model', chest, 'Replace removed builtin/entity parent; retain authored display transforms')
    for material in ['sandstone', 'red_sandstone']:
        name = f'assets/minecraft/blockstates/cut_{material}.json'
        d = json.loads(files[name])
        putjson(name, {'variants': {'': d['variants']['axis=y']}})
        record('blockstate', name, 'Cut sandstone has no axis property; use authored upright model')
    block_ids = {pathlib.PurePosixPath(n).stem for n in vanilla_names if '/blockstates/' in n and n.endswith('.json')}
    fixes = {'bed_rock': 'bedrock', 'bone_blok': 'bone_block', 'black_terracottaterracotta': 'black_terracotta', 'chiseled_sanstone': 'chiseled_sandstone', 'deepslate_emerald': 'deepslate_emerald_ore', 'farmland_moist': 'farmland[moisture=7]', 'grass_path': 'dirt_path', 'hardened_clay': 'terracotta', 'hay_bale_side': 'hay_block', 'infested_cracked_stone_brick': 'infested_cracked_stone_bricks', 'infested_stonebrick': 'infested_stone_bricks', 'netherrack_gold_ore': 'nether_gold_ore', 'predodzol': 'podzol', 'pumking': 'pumpkin', 'silver_glazed_terracotta': 'light_gray_glazed_terracotta', 'basalt_top': 'basalt', "jack_o'lantern": 'jack_o_lantern', 'planks': ' '.join(sorted((x for x in block_ids if x.endswith('_planks')))), 'stained_hardened_clay': ' '.join(sorted((x for x in block_ids if x.endswith('_terracotta') and 'glazed' not in x)))}
    fixes.update({'_sand': '', 'light_glazed_terracotta': '', 'mossy_block': ''})
    fixes['farmland_moist'] = 'farmland:moisture=7'
    for name in list(files):
        if '/optifine/ctm/' in name and name.endswith('.properties'):
            original = files[name].decode('utf-8-sig')
            lines = []
            for line in original.splitlines():
                (key, sep, value) = line.partition('=')
                key = key.strip()
                if sep and key in ['matchBlocks', 'connectBlocks']:
                    tokens = []
                    for token in value.split():
                        token = fixes.get(token, token)
                        tokens.extend(token.split())
                    line = key + '=' + ' '.join(dict.fromkeys(tokens))
                if key == 'tintBlock' and sep and (value.strip() == 'mossy_block'):
                    line = 'tintBlock=' + ('pale_moss_block' if '/pale_moss_block/' in name else 'moss_block')
                if key == 'tintIndex' and sep:
                    try:
                        int(value)
                    except ValueError:
                        continue
                lines.append(line)
            if 'mushroom_stem_dirt/mushroom_stem.properties' in name:
                lines.append('method=overlay')
            result = '\n'.join(lines) + '\n'
            if result.replace('\r', '').split() != original.replace('\r', '').split():
                files[name] = result.encode()
                record('ctm_compatibility', name, 'Correct obsolete block IDs / invalid tint or missing overlay method')
    for name in list(files):
        if name.startswith('assets/') and (not re.fullmatch('[a-z0-9_./-]+', name)):
            dest = 'optional_original_assets/' + name
            files[dest] = files.pop(name)
            record('archive_optional', dest, 'Unused original variant; invalid game resource path')
    models = {}
    for name in vanilla_names:
        if '/models/' in name and name.endswith('.json'):
            models[name] = json.loads(vanilla.read(name))
    for (name, data) in files.items():
        if '/models/' in name and name.endswith('.json'):
            models[name] = json.loads(data.decode('utf-8-sig'))

    def modelpath(ref):
        return 'assets/minecraft/models/' + ref.removeprefix('minecraft:') + '.json'
    roots = set()

    def walk(obj):
        if isinstance(obj, dict):
            for (k, v) in obj.items():
                if k == 'model' and isinstance(v, str):
                    roots.add(modelpath(v))
                else:
                    walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    for name in vanilla_names:
        if ('/blockstates/' in name or '/items/' in name) and name.endswith('.json'):
            walk(json.loads(files.get(name, vanilla.read(name))))
    missing = []
    visited = set()
    cache = {}

    def inherited(name, stack=()):
        if name in cache:
            return cache[name]
        if name in stack:
            raise AssertionError('Model inheritance cycle ' + name)
        visited.add(name)
        if name not in models:
            if '/builtin/' in name:
                return ({}, [])
            missing.append(('model', name))
            return ({}, [])
        d = models[name]
        textures = {}
        elements = []
        if d.get('parent'):
            (textures, elements) = inherited(modelpath(d['parent']), stack + (name,))
            textures = textures.copy()
        textures.update(d.get('textures', {}))
        elements = d.get('elements', elements)
        cache[name] = (textures, elements)
        return (textures, elements)
    for root in roots:
        (textures, elements) = inherited(root)
        refs = ['#particle'] if 'particle' in textures else []
        refs += [face['texture'] for e in elements for face in e.get('faces', {}).values()]
        for ref in refs:
            seen = set()
            while ref.startswith('#'):
                if ref in seen or ref[1:] not in textures:
                    missing.append(('binding', root, ref))
                    break
                seen.add(ref)
                ref = textures[ref[1:]]
                if isinstance(ref, dict):
                    ref = ref['sprite']
            if not ref.startswith('#'):
                path = 'assets/minecraft/textures/' + ref.removeprefix('minecraft:') + '.png'
                if path not in files and path not in vanilla_names:
                    missing.append(('texture', root, path))
    missing = sorted(set(missing))
    vanilla_sentinels = [x for x in missing if x[0] == 'texture' and (x[-1].endswith('/missingno.png') or x[1] == 'assets/minecraft/models/block/heavy_core.json')]
    missing = [x for x in missing if x not in vanilla_sentinels]
    assert not missing, json.dumps(missing[:40], indent=2)
    json_count = 0
    png_count = 0
    for (name, data) in files.items():
        if name.endswith(('.json', '.mcmeta')):
            try:
                d = json.loads(data.decode('utf-8-sig'))
                json_count += 1
            except Exception as e:
                raise AssertionError((name, str(e)))
            if name.endswith('.png.mcmeta') and 'animation' in d:
                im = image(files[name[:-7]])
                anim = d['animation']
                fw = anim.get('width', im.width if 'height' not in anim else min(im.size))
                fh = anim.get('height', min(im.size))
                frames = im.width // fw * (im.height // fh)
                for f in anim.get('frames', []):
                    assert (f if isinstance(f, int) else f['index']) < frames, (name, f, frames)
        if name.endswith('.png'):
            image(data).load()
            png_count += 1
    report = {'source': 'https://www.curseforge.com/minecraft/texture-packs/stay-true/files/6534716', 'source_sha256': hashlib.sha256(S.read_bytes()).hexdigest(), 'target': 'Minecraft Java 26.3 / resource format 97.1', 'changes': changes, 'validation': {'json_files': json_count, 'png_files': png_count, 'reachable_models': len(visited), 'missing_effective_model_textures': missing}, 'notes': ['Original author: HaiMcFly; unofficial local compatibility conversion.', 'No newly drawn textures. New blocks and new baby animal variants use vanilla assets.', 'Continuity is required for connected textures on Fabric. OptiFine-only custom colors need separate mod support.', 'Legacy unused GUI sheets and optional alternative texture folders are retained unchanged; they were already inactive in 1.21.5.']}
    putjson('stay_true_port_info.json', {'author': 'HaiMcFly', 'upstream_file': 6534716, 'target': '26.3', 'unofficial': True})
    out = output_path
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for (name, data) in sorted(files.items()):
            z.writestr(name, data)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
    report['output'] = str(out)
    report['output_sha256'] = hashlib.sha256(out.read_bytes()).hexdigest()
    out.with_suffix('.report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(out), 'bytes': out.stat().st_size, 'changes': len(changes), 'validation': report['validation']}, indent=2))

if __name__ == "__main__":
    main()
