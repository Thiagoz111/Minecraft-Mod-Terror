# -*- coding: utf-8 -*-
"""Generates every JSON resource of the mod: dimensions, biomes, item/block models, blockstates,
particles, loot tables and language files."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio'))
from lang import ITEMS, ENTITIES, BLOCKS, CASES, BESTIARY, SPIRIT_BOX, MISC, WEAKNESS, SCRIPT
from sounds_def import SOUNDS
from lines import LINES, TEXTS, SPEAKERS

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'src/main/resources')
A = os.path.join(RES, 'assets/deadline')
D = os.path.join(RES, 'data/deadline')
NS = 'deadline'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------ dimensions
CASE_ENV = {
    # key: fog, water, water_fog, particles, sky_light, fog_end, mood_delay
    'casa': ('#120f16', '#4a0b0e', '#1a0608', 'minecraft:white_ash', 0.004, 2.0, 40.0),
    'colegio': ('#0a0b12', '#141a2a', '#05070d', 'minecraft:white_ash', 0.005, 1.5, 36.0),
}


def dimensions():
    for key, (fog, water, wfog, particle, chance, sky, fog_end) in CASE_ENV.items():
        dim = f'caso_{key}'
        write(f'{D}/dimension_type/{dim}.json', {
            'ambient_light': 0.0,
            'attributes': {
                'minecraft:audio/ambient_sounds': {
                    'loop': f'{NS}:ambient.{key}',
                    'mood': {'block_search_extent': 8, 'offset': 2.0, 'sound': f'{NS}:ambient.stinger', 'tick_delay': 2400},
                    'additions': {'sound': f'{NS}:ambient.whispers', 'tick_chance': 0.0035},
                },
                'minecraft:audio/background_music': {
                    'default': {'sound': f'{NS}:music.case', 'min_delay': 3600, 'max_delay': 9000, 'replace_current_music': True},
                },
                'minecraft:gameplay/bed_rule': {'can_set_spawn': 'never', 'can_sleep': 'never', 'explodes': False},
                'minecraft:gameplay/respawn_anchor_works': False,
                'minecraft:gameplay/sky_light_level': sky,
                'minecraft:visual/sky_color': '#050508',
                'minecraft:visual/fog_color': fog,
                'minecraft:visual/fog_start_distance': 2.0,
                'minecraft:visual/fog_end_distance': fog_end,
                'minecraft:visual/water_fog_color': wfog,
                'minecraft:visual/ambient_particles': [{'particle': {'type': particle}, 'probability': chance}],
            },
            'coordinate_scale': 1.0,
            'has_ceiling': False,
            'has_fixed_time': True,
            'has_skylight': True,
            'height': 256,
            'infiniburn': '#minecraft:infiniburn_overworld',
            'logical_height': 256,
            'min_y': 0,
            'monster_spawn_block_light_limit': 0,
            'monster_spawn_light_level': 0,
            'skybox': 'none',
            'timelines': '#minecraft:in_end',
        })
        write(f'{D}/worldgen/biome/bruma_{key}.json', {
            'attributes': {},
            'carvers': [],
            'downfall': 0.0,
            'effects': {'water_color': water},
            'features': [[] for _ in range(11)],
            'has_precipitation': False,
            'spawn_costs': {},
            'spawners': {k: [] for k in ['ambient', 'axolotls', 'creature', 'misc', 'monster', 'underground_water_creature', 'water_ambient', 'water_creature']},
            'temperature': 0.4,
        })
        write(f'{D}/dimension/{dim}.json', {
            'type': f'{NS}:{dim}',
            'generator': {
                'type': 'minecraft:flat',
                'settings': {
                    'biome': f'{NS}:bruma_{key}',
                    'features': False,
                    'lakes': False,
                    'layers': [
                        {'block': 'minecraft:bedrock', 'height': 1},
                        {'block': 'minecraft:stone', 'height': 58},
                        {'block': 'minecraft:dirt', 'height': 3},
                        {'block': 'minecraft:grass_block', 'height': 1},
                    ],
                    'structure_overrides': [],
                },
            },
        })


# ------------------------------------------------------------------ items
def model(name, parent='minecraft:item/generated', **tex):
    return {'parent': parent, 'textures': tex}


def ref(m):
    return {'type': 'minecraft:model', 'model': m}


SIMPLE_ITEMS = ['crucifix', 'holy_water', 'salt', 'spirit_box', 'camera', 'ritual_book', 'spirit_jar', 'spirit_jar_full',
                'pills', 'rosary', 'inverted_rosary', 'cursed_doll', 'llave_capilla']
EGGS = ['monja', 'poseida', 'sombra', 'muneca', 'anima']


def items():
    for n in SIMPLE_ITEMS:
        write(f'{A}/models/item/{n}.json', model(n, layer0=f'{NS}:item/{n}'))
        write(f'{A}/items/{n}.json', {'model': ref(f'{NS}:item/{n}')})
    write(f'{A}/models/item/silver_dagger.json', model('silver_dagger', 'minecraft:item/handheld', layer0=f'{NS}:item/silver_dagger'))
    write(f'{A}/items/silver_dagger.json', {'model': ref(f'{NS}:item/silver_dagger')})
    # flare: lit while flying is the entity; inventory icon is the unlit flare
    write(f'{A}/models/item/flare.json', model('flare', layer0=f'{NS}:item/flare'))
    write(f'{A}/models/item/flare_lit.json', model('flare_lit', layer0=f'{NS}:item/flare_lit'))
    write(f'{A}/items/flare.json', {'model': ref(f'{NS}:item/flare')})
    # phone: rings while calls are pending (custom_model_data flag 0)
    for n in ('phone', 'phone_ringing'):
        write(f'{A}/models/item/{n}.json', model(n, layer0=f'{NS}:item/{n}'))
    write(f'{A}/items/phone.json', {'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:custom_model_data', 'index': 0,
        'on_true': ref(f'{NS}:item/phone_ringing'), 'on_false': ref(f'{NS}:item/phone')}})
    # EMF: LEDs from custom_model_data float 0
    for i in range(6):
        write(f'{A}/models/item/emf_{i}.json', model(f'emf_{i}', layer0=f'{NS}:item/emf_{i}'))
    write(f'{A}/items/emf.json', {'model': {
        'type': 'minecraft:range_dispatch', 'property': 'minecraft:custom_model_data', 'index': 0,
        'entries': [{'threshold': float(i), 'model': ref(f'{NS}:item/emf_{i}')} for i in range(1, 6)],
        'fallback': ref(f'{NS}:item/emf_0')}})
    # flashlight: flag 0 = on, flag 1 = uv
    for n in ('flashlight', 'flashlight_on', 'flashlight_uv'):
        write(f'{A}/models/item/{n}.json', model(n, layer0=f'{NS}:item/{n}'))
    write(f'{A}/items/flashlight.json', {'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:custom_model_data', 'index': 0,
        'on_true': {'type': 'minecraft:condition', 'property': 'minecraft:custom_model_data', 'index': 1,
                    'on_true': ref(f'{NS}:item/flashlight_uv'), 'on_false': ref(f'{NS}:item/flashlight_on')},
        'on_false': ref(f'{NS}:item/flashlight')}})
    for e in EGGS:
        n = f'{e}_spawn_egg'
        write(f'{A}/models/item/{n}.json', model(n, layer0=f'{NS}:item/{n}'))
        write(f'{A}/items/{n}.json', {'model': ref(f'{NS}:item/{n}')})


# ------------------------------------------------------------------ blocks
def blocks():
    # salt line: flat decal
    write(f'{A}/models/block/salt_line.json', {
        'parent': 'minecraft:block/block', 'ambientocclusion': False,
        'textures': {'particle': f'{NS}:block/salt_line', 'salt': f'{NS}:block/salt_line'},
        'elements': [{'from': [0, 0.1, 0], 'to': [16, 0.1, 16], 'shade': False,
                      'faces': {'up': {'uv': [0, 0, 16, 16], 'texture': '#salt'}, 'down': {'uv': [0, 16, 16, 0], 'texture': '#salt'}}}]})
    write(f'{A}/blockstates/salt_line.json', {'variants': {'': [{'model': f'{NS}:block/salt_line'}, {'model': f'{NS}:block/salt_line', 'y': 90},
                                                                 {'model': f'{NS}:block/salt_line', 'y': 180}, {'model': f'{NS}:block/salt_line', 'y': 270}]}})
    # blood stain: 4 variants x random rotation
    variants = {}
    for v in range(4):
        write(f'{A}/models/block/blood_stain_{v}.json', {
            'parent': 'minecraft:block/block', 'ambientocclusion': False,
            'textures': {'particle': f'{NS}:block/blood_stain_{v}', 'blood': f'{NS}:block/blood_stain_{v}'},
            'elements': [{'from': [0, 0.05, 0], 'to': [16, 0.05, 16],
                          'faces': {'up': {'uv': [0, 0, 16, 16], 'texture': '#blood'}}}]})
        variants[f'variant={v}'] = [{'model': f'{NS}:block/blood_stain_{v}', 'y': r} for r in (0, 90, 180, 270)]
    write(f'{A}/blockstates/blood_stain.json', {'variants': variants})
    write(f'{A}/models/item/blood_stain.json', model('blood_stain', layer0=f'{NS}:block/blood_stain_0'))
    write(f'{A}/items/blood_stain.json', {'model': ref(f'{NS}:item/blood_stain')})
    # ritual candles reuse vanilla candle templates
    words = {1: 'one_candle', 2: 'two_candles', 3: 'three_candles', 4: 'four_candles'}
    v = {}
    for n, w in words.items():
        for lit in (False, True):
            suffix = '_lit' if lit else ''
            mname = f'ritual_candle_{w}{suffix}'
            tex = f'{NS}:block/ritual_candle{suffix}'
            write(f'{A}/models/block/{mname}.json', {'parent': f'minecraft:block/template_{"candle" if n == 1 else w}',
                                                       'textures': {'all': tex, 'particle': tex}})
            v[f'candles={n},lit={"true" if lit else "false"}'] = {'model': f'{NS}:block/{mname}'}
    write(f'{A}/blockstates/ritual_candle.json', {'variants': v})
    write(f'{A}/models/item/ritual_candle.json', model('ritual_candle', layer0=f'{NS}:item/ritual_candle'))
    write(f'{A}/items/ritual_candle.json', {'model': ref(f'{NS}:item/ritual_candle')})
    # loot: candles drop their count; decals drop nothing
    write(f'{D}/loot_table/blocks/ritual_candle.json', {
        'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0, 'entries': [{
            'type': 'minecraft:item', 'name': f'{NS}:ritual_candle',
            'functions': [{'function': 'minecraft:set_count', 'add': False, 'count': float(n),
                           'conditions': [{'condition': 'minecraft:block_state_property', 'block': f'{NS}:ritual_candle',
                                           'properties': {'candles': str(n)}}]} for n in (2, 3, 4)]
            + [{'function': 'minecraft:explosion_decay'}]}],
            'conditions': [{'condition': 'minecraft:survives_explosion'}]}],
        'random_sequence': f'{NS}:blocks/ritual_candle'})


# ------------------------------------------------------------------ particles
PARTICLES = {'ectoplasm': 4, 'holy_spark': 4, 'demon_smoke': 6, 'wisp': 4, 'salt_sparkle': 2, 'blood_drip': 3, 'handprint': 1, 'cold_breath': 4}


def particles():
    for p, n in PARTICLES.items():
        write(f'{A}/particles/{p}.json', {'textures': [f'{NS}:{p}_{i}' for i in range(n)]})


# ------------------------------------------------------------------ language
def lang():
    es, en = {}, {}
    for k, (e, n) in ITEMS.items():
        es[f'item.{NS}.{k}'] = e
        en[f'item.{NS}.{k}'] = n
    for k, (e, n) in ENTITIES.items():
        es[f'entity.{NS}.{k}'] = e
        en[f'entity.{NS}.{k}'] = n
    for k, (e, n) in BLOCKS.items():
        es[f'block.{NS}.{k}'] = e
        en[f'block.{NS}.{k}'] = n
    for k in EGGS:
        es[f'item.{NS}.{k}_spawn_egg'] = f'Huevo de {ENTITIES[k][0]}'
        en[f'item.{NS}.{k}_spawn_egg'] = f'{ENTITIES[k][1]} Spawn Egg'
    for key, c in CASES.items():
        es[f'{NS}.case.{key}.place'], en[f'{NS}.case.{key}.place'] = c['place']
        es[f'{NS}.case.{key}.hint'], en[f'{NS}.case.{key}.hint'] = c['hint']
        for i, (n_es, m_es, n_en, m_en) in enumerate(c['callers']):
            es[f'{NS}.case.{key}.caller.{i}'] = n_es
            es[f'{NS}.case.{key}.msg.{i}'] = m_es
            en[f'{NS}.case.{key}.caller.{i}'] = n_en
            en[f'{NS}.case.{key}.msg.{i}'] = m_en
    for k, (e, n) in BESTIARY.items():
        es[f'{NS}.bestiary.{k}'] = e
        en[f'{NS}.bestiary.{k}'] = n
    for k, (e, n) in WEAKNESS.items():
        es[f'{NS}.weakness.{k}'] = e
        en[f'{NS}.weakness.{k}'] = n
    for i, (e, n) in enumerate(SPIRIT_BOX):
        es[f'{NS}.spiritbox.{i}'] = e
        en[f'{NS}.spiritbox.{i}'] = n
    for k, (e, n) in MISC.items():
        es[k] = e
        en[k] = n
    for name, (_, sub_es, sub_en, _) in SOUNDS.items():
        es[f'subtitles.{NS}.{name}'] = sub_es
        en[f'subtitles.{NS}.{name}'] = sub_en
    for k, (e, n) in SCRIPT.items():
        es[k], en[k] = e, n
    for k, v in LINES.items():
        es[f'{NS}.line.{k}'], en[f'{NS}.line.{k}'] = v['es'], v['en']
    for k, (e, n) in TEXTS.items():
        es[f'{NS}.text.{k}'], en[f'{NS}.text.{k}'] = e, n
    for k, (e, n) in SPEAKERS.items():
        es[f'{NS}.speaker.{k}'], en[f'{NS}.speaker.{k}'] = e, n
    extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blocks', 'out', 'lang_blocks.json')
    if os.path.exists(extra):
        for k, (e_es, e_en) in json.load(open(extra)).items():
            es[k], en[k] = e_es, e_en
    write(f'{A}/lang/en_us.json', dict(sorted(en.items())))
    for loc in ('es_es', 'es_ar', 'es_mx', 'es_cl', 'es_uy', 'es_ve', 'es_ec'):
        write(f'{A}/lang/{loc}.json', dict(sorted(es.items())))


if __name__ == '__main__':
    dimensions()
    items()
    blocks()
    particles()
    lang()
    print('data generated')
