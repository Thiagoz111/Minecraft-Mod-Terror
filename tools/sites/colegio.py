"""Colegio Santa Ines de la Vigilia (case 1). Layout from docs/design/BIBLIA.md 2.1 f.

    python3 tools/sites/colegio.py      -> src/main/resources/data/deadline/sites/colegio.json (+ a plan image)

Origin (0,0,0) is the main door; the facade is z=0, the building grows towards +z, the street is -z.
Ground floor: front rooms z 0..8 (classroom, hall, principal's office), corridor z 8..12, then the kitchen, dining
hall and chapel (with the upper choir over its entrance) from z 12. Materials are semantic (see PALETTE); the
colegio_* building kit replaces the vanilla stand-ins by editing PALETTE only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import Site, Palette  # noqa: E402

PALETTE = Palette({
    'wall_ext': ['minecraft:calcite', 'minecraft:calcite', 'minecraft:white_terracotta'],
    'wall_base': 'minecraft:stone_bricks',
    'wall': 'minecraft:calcite',
    'zocalo': 'minecraft:dark_oak_planks',
    'floor': 'minecraft:spruce_planks',
    'floor_kitchen': ['minecraft:terracotta', 'minecraft:brown_terracotta'],
    'checker_a': 'minecraft:white_concrete',
    'checker_b': 'minecraft:black_concrete',
    'ceiling': 'minecraft:dark_oak_planks',
    'beam': 'minecraft:stripped_dark_oak_log',
    'roof': 'minecraft:brick_slab',
    'chapel_wall': ['minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks'],
    'chapel_floor_a': 'minecraft:polished_diorite',
    'chapel_floor_b': 'minecraft:polished_deepslate',
    'door': 'minecraft:dark_oak_door',
    'iron_door': 'minecraft:iron_door',
    'window': 'minecraft:glass_pane',
    'stained': 'minecraft:red_stained_glass_pane',
    'board': 'minecraft:green_terracotta',
    'chair': 'minecraft:spruce_stairs',
    'desk': 'minecraft:spruce_slab',
    'bench': 'minecraft:dark_oak_stairs',
    'table': 'minecraft:dark_oak_slab',
    'tarima': 'minecraft:spruce_slab',
    'chalk_square': 'minecraft:white_carpet',
    'lamp': 'minecraft:waxed_exposed_copper_bulb',
    'chandelier': 'minecraft:lantern',
    'candle': 'minecraft:candle',
    'red_candle': 'minecraft:red_candle',
    'hatch': 'minecraft:spruce_trapdoor',
    'key_board': 'minecraft:spruce_trapdoor',
    'stove': 'minecraft:blast_furnace',
    'pot': 'minecraft:cauldron',
    'office_desk': 'minecraft:dark_oak_slab',
    'mate': 'minecraft:decorated_pot',
    'file': 'minecraft:lectern',
    'phone': 'minecraft:heavy_core',
    'office_chair': 'minecraft:dark_oak_stairs',
    'confessional': 'minecraft:dark_oak_planks',
    'grille': 'minecraft:iron_trapdoor',
    'altar': 'minecraft:quartz_block',
    'font': 'minecraft:water_cauldron',
    'rail': 'minecraft:dark_oak_fence',
    'stairs_wood': 'minecraft:dark_oak_stairs',
    'path': ['minecraft:coarse_dirt', 'minecraft:gravel', 'minecraft:dirt_path'],
    'fence_wall': 'minecraft:stone_brick_wall',
    'bars': 'minecraft:iron_bars',
    'grotto': ['minecraft:mossy_cobblestone', 'minecraft:cobblestone', 'minecraft:tuff'],
    'virgin': 'minecraft:white_glazed_terracotta',
    'bookshelf': 'minecraft:bookshelf',
    'shelf': 'minecraft:barrel',
    'coat_rack': 'minecraft:dark_oak_fence',
})


def checker(s, x1, z1, x2, z2, y, a='checker_a', b='checker_b'):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            s.set(x, y, z, a if (x + z) % 2 == 0 else b)


def window(s, x, y, z, axis):
    """Glass pane connected along the wall (axis 'x' = wall runs along x)."""
    if axis == 'x':
        s.set(x, y, z, 'window', east=True, west=True, north=False, south=False, waterlogged=False)
    else:
        s.set(x, y, z, 'window', north=True, south=True, east=False, west=False, waterlogged=False)


def build():
    s = Site('colegio', PALETTE)

    # ------------------------------------------------------------ exterior
    for x in range(-34, 35):
        for y in range(0, 3):
            s.set(x, y, -22, 'fence_wall', up=True, north='none', south='none', east='low' if y < 2 else 'none', west='low' if y < 2 else 'none', waterlogged=False)
            s.set(x, y, 44, 'fence_wall', up=True, north='none', south='none', east='low', west='low', waterlogged=False)
    for z in range(-22, 45):
        for y in range(0, 3):
            s.set(-34, y, z, 'fence_wall', up=True, north='low', south='low', east='none', west='none', waterlogged=False)
            s.set(34, y, z, 'fence_wall', up=True, north='low', south='low', east='none', west='none', waterlogged=False)
    for x in range(-2, 3):  # the gate stands open
        for y in range(0, 3):
            s.clear(x, y, -22)
    for z in range(-30, 0):
        for x in range(-1, 2):
            s.set(x, -1, z, 'path')
    # the grotto of the Virgin: a safe island of candles that never go out
    gx, gz = -11, -10
    for dx in range(-2, 3):
        for dy in range(0, 4):
            if abs(dx) == 2 or dy == 3:
                s.set(gx + dx, dy, gz + 1, 'grotto')
        s.set(gx + dx, 3, gz, 'grotto')
    s.set(gx, 1, gz + 1, 'virgin', facing='north')
    for dx in (-1, 1):
        s.set(gx + dx, 0, gz, 'candle', candles=4, lit=True, waterlogged=False)
    s.light(gx, 1, gz - 1, 12, 'gruta')
    s.point('gruta', gx, 0, gz - 2, 'north')
    s.point('spawn', 0, 0, -27, 'south')
    s.area('exterior', -33, -2, -21, 33, 12, -1)

    # ------------------------------------------------------------ shell and front rooms (z 0..8)
    # facade: two storeys of white render with a stone plinth
    for x in range(-28, 21):
        for y in range(0, 10):
            s.set(x, y, 0, 'wall_base' if y == 0 else 'wall_ext')
    for x in range(-28, 21):
        for z in range(0, 39):
            s.set(x, 10, z, 'roof', type='bottom', waterlogged=False)
    # classroom (aula de 6), hall, principal's office
    s.room(-18, 0, -6, 8, 0, 4, wall='wall', floor='floor', ceiling='ceiling')
    s.room(-6, 0, 6, 8, 0, 8, wall='wall', floor='floor', ceiling='ceiling')
    s.room(6, 0, 16, 8, 0, 4, wall='wall', floor='floor', ceiling='ceiling')
    checker(s, -5, 1, 5, 7, -1)
    # facade wall again on top of the room walls (rooms re-set z=0 with interior plaster)
    for x in range(-18, 17):
        for y in range(0, 10):
            if s.get(x, y, 0) and not s.get(x, y, 0).startswith('minecraft:air'):
                s.set(x, y, 0, 'wall_base' if y == 0 else 'wall_ext')
    # main door
    s.door('entrada', 0, 0, 0, 'south', hinge='left', open_=True)
    window(s, -2, 2, 0, 'x')
    window(s, 2, 2, 0, 'x')
    for y in (1, 2):
        for x in (-15, -12, -9):
            window(s, x, y, 0, 'x')
        for x in (9, 12, 15):
            window(s, x, y, 0, 'x')
    for y in (6, 7):
        for x in range(-24, 20, 4):
            if x not in (0,):
                window(s, x, y, 0, 'x')
    # hall: chandelier and the open archway to the corridor
    s.set(0, 8, 4, 'chandelier', hanging=True, waterlogged=False)
    s.light(0, 6, 4, 10, 'hall_arana')
    s.light(0, 3, 2, 8, 'hall_arana')
    for x in (-1, 0, 1):
        for y in (0, 1, 2):
            s.set(x, y, 8, 'minecraft:air')
    s.point('hall_centro', 0, 0, 4, 'north')
    s.point('hall', 0, 0, 6, 'north')
    s.point('megafono', 0, 7, 7, 'south')
    s.area('hall', -5, 0, 1, 5, 6, 7)

    # classroom: blackboard on the west wall, platform, chalk squares, 3 x 4 desks facing the board
    s.door('aula', -8, 0, 8, 'north', hinge='right', open_=True)
    for z in range(2, 7):
        for y in (1, 2):
            s.set(-18, y, z, 'board')
    s.write('pizarron', -17, 2, 4, 'east', width=5.0)
    for x in (-17, -16):
        for z in range(1, 8):
            s.set(x, 0, z, 'tarima', type='bottom', waterlogged=False)
    s.set(-16, 1, 4, 'office_desk', type='bottom', waterlogged=False)
    for i, z in enumerate((1, 3, 5, 7)):
        s.set(-15, 0, z, 'chalk_square')
        s.area('aula_' + 'abcd'[i], -15, 0, z, -15, 1, z)
    sillas = []
    for cx in (-13, -11, -9):
        for z in (1, 3, 5, 7):
            s.set(cx, 0, z, 'desk', type='top', waterlogged=False)
            s.set(cx + 1, 0, z, 'chair', facing='east', half='bottom', shape='straight', waterlogged=False)
            sillas.append([cx + 1, 0, z])
    s.markers['groups']['aula_sillas'] = sillas
    s.light(-12, 3, 1, 6, 'aula_ventanas')
    s.light(-9, 3, 1, 5, 'aula_ventanas')
    s.point('aula_puerta', -8, 0, 10, 'south')
    s.point('aula_pizarron', -17, 1.5, 4, 'east')
    s.point('aula_fondo', -7, 0, 4, 'west')
    s.point('aula_frente', -16, 1, 4, 'east')
    s.point('aula_centro', -11, 0, 4, 'west')
    for i, (x, z) in enumerate(((-12, 2), (-10, 6), (-8, 3), (-12, 7))):
        s.point(f'aula_voz_{i + 1}', x, 0.6, z, 'west')
    s.area('aula', -17, 0, 1, -7, 4, 7)
    s.area('aula_tarima', -17, 0, 1, -15, 3, 7)

    # principal's office: desk, the file on a lectern, the mate, the bakelite phone, the swivel chair
    s.door('direccion', 11, 0, 8, 'north', hinge='left', open_=False)
    for x in (10, 11, 12):
        s.set(x, 0, 4, 'office_desk', type='top', waterlogged=False)
    s.set(10, 1, 4, 'mate')
    s.point('direccion_mate', 10, 1, 4)
    s.set(11, 1, 4, 'file', facing='north', has_book=False, powered=False)
    s.point('direccion_legajo', 11, 1, 4)
    s.set(12, 1, 4, 'phone', waterlogged=False)
    s.point('direccion_telefono', 12, 1, 4)
    s.set(11, 0, 2, 'office_chair', facing='north', half='bottom', shape='straight', waterlogged=False)
    s.markers['groups']['direccion_silla'] = [[11, 0, 2]]
    s.point('direccion_silla_pt', 11, 0, 2)
    for z in range(1, 8):
        s.set(15, 0, z, 'bookshelf')
        s.set(15, 1, z, 'bookshelf')
    s.light(13, 3, 6, 7, 'direccion_luz')
    s.area('direccion', 7, 0, 1, 15, 4, 7)

    # ------------------------------------------------------------ corridor (z 8..12)
    s.room(-28, 8, 20, 12, 0, 3, wall='wall', floor='floor', ceiling='ceiling')
    # re-open the doorways the corridor walls just covered
    s.door('aula', -8, 0, 8, 'north', hinge='right', open_=True)
    s.door('direccion', 11, 0, 8, 'north', hinge='left', open_=False)
    for x in (-1, 0, 1):
        for y in (0, 1, 2):
            s.set(x, y, 8, 'minecraft:air')
    lamps = []
    for x in (17, 11, 5, -1, -7, -13, -19, -25):
        s.set(x, 3, 10, 'lamp', lit=True, powered=False)
        lamps.append([x, 3, 10])
    s.markers['groups']['pasillo_pb'] = lamps
    for x in range(-26, 19, 6):  # coat racks with old smocks, crucifixes
        s.set(x, 0, 11, 'coat_rack', north=False, south=False, east=False, west=False, waterlogged=False)
    s.point('pasillo_fondo', 18, 0, 10, 'west')
    s.area('pasillo_pb', -27, 0, 9, 19, 3, 11)

    # ------------------------------------------------------------ kitchen and dining hall (z 12..26)
    s.room(-28, 12, -18, 20, 0, 4, wall='wall', floor='floor_kitchen', ceiling='ceiling')
    s.room(-18, 12, -6, 26, 0, 4, wall='wall', floor='floor', ceiling='ceiling')
    s.door('cocina', -23, 0, 12, 'south', hinge='left', open_=True)
    for x in (-13, -12, -11):
        for y in (0, 1, 2):
            s.set(x, y, 12, 'minecraft:air')
    # service hatch between kitchen and dining hall (trapdoor: open = closed hatch)
    for z in (16, 17):
        s.set(-18, 1, z, 'hatch', facing='east', half='top', open=False, powered=False, waterlogged=False)
    s.point('ventanilla', -18, 1, 16)
    s.point('ventanilla_monja', -19, 0, 16.5, 'east')
    s.point('cocina_fondo', -27, 0, 16, 'east')
    s.point('cocina_p1', -25, 0, 16, 'east')
    s.point('cocina_p2', -22, 0, 16, 'east')
    for x in range(-27, -20):
        if x % 2 == 0:
            s.set(x, 0, 13, 'stove', facing='south', lit=False)
        else:
            s.set(x, 0, 13, 'pot')
    s.set(-21, 1, 19, 'key_board', facing='north', half='top', open=True, powered=False, waterlogged=False)
    s.point('tablero', -21, 1, 19)
    s.area('cocina', -27, 0, 13, -19, 4, 19)
    # dining hall: two long tables with candles, benches
    velas = []
    for tx in (-14, -10):
        for z in range(15, 25):
            s.set(tx, 0, z, 'table', type='top', waterlogged=False)
            s.set(tx - 1, 0, z, 'bench', facing='east', half='bottom', shape='straight', waterlogged=False)
            s.set(tx + 1, 0, z, 'bench', facing='west', half='bottom', shape='straight', waterlogged=False)
        for z in (16, 19, 22):
            s.set(tx, 1, z, 'candle', candles=3, lit=True, waterlogged=False)
            velas.append([tx, 1, z])
    s.markers['groups']['refectorio_velas'] = velas
    s.point('refectorio', -12, 0, 14, 'north')
    s.area('refectorio', -17, 0, 13, -7, 4, 25)

    # ------------------------------------------------------------ chapel (z 12..38) with the upper choir
    for x in range(4, 17):
        for z in range(12, 39):
            for y in range(0, 11):
                edge = x in (4, 16) or z in (12, 38)
                if edge:
                    s.set(x, y, z, 'chapel_wall')
                else:
                    s.set(x, y, z, 'minecraft:air')
            s.set(x, -1, z, 'chapel_floor_a' if (x + z) % 2 == 0 else 'chapel_floor_b')
            s.set(x, 11, z, 'ceiling')
    s.door('capilla', 10, 0, 12, 'south', hinge='left', open_=False)
    for z in range(16, 37, 4):  # tall red windows
        for y in range(2, 8):
            window(s, 4, y, z, 'z')
            s.set(4, y, z, 'stained', north=True, south=True, east=False, west=False, waterlogged=False)
            s.set(16, y, z, 'stained', north=True, south=True, east=False, west=False, waterlogged=False)
    # pews (north-facing benches) in two blocks
    for z in range(21, 33, 2):
        for x in list(range(6, 9)) + list(range(12, 15)):
            s.set(x, 0, z, 'bench', facing='north', half='bottom', shape='straight', waterlogged=False)
    # altar, sanctuary lamp, crucifix wall
    for x in range(8, 13):
        for z in (35, 36):
            s.set(x, 0, z, 'altar')
    s.set(10, 1, 35, 'red_candle', candles=4, lit=True, waterlogged=False)
    s.light(10, 3, 34, 10, 'capilla_lampara')
    s.markers['groups']['capilla_lampara'].append([10, 1, 35])
    s.set(9, 0, 15, 'font', level=3)
    # confessional against the west wall: a booth with a grille
    for y in range(0, 3):
        for z in (25, 29):
            s.set(5, y, z, 'confessional')
            s.set(6, y, z, 'confessional')
        s.set(5, y, 26, 'confessional')
        s.set(5, y, 28, 'confessional')
    for z in range(25, 30):
        s.set(5, 3, z, 'confessional')
        s.set(6, 3, z, 'confessional')
    s.set(6, 1, 26, 'grille', facing='north', half='bottom', open=True, powered=False, waterlogged=False)
    s.point('confesionario', 5, 1, 26)
    s.point('confesionario_cara', 6, 0, 25.6, 'south')
    s.area('confesionario_in', 6, 0, 27, 6, 2, 28)
    # upper choir over the entrance: floor at y=5, railing, 8 lecterns, stairs along the west wall
    for x in range(5, 16):
        for z in range(13, 19):
            s.set(x, 5, z, 'floor')
        s.set(x, 6, 19, 'rail', north=False, south=False, east=x < 15, west=x > 5, waterlogged=False)
    for k in range(5):
        s.set(5, k, 23 - k, 'stairs_wood', facing='north', half='bottom', shape='straight', waterlogged=False)
        for y in range(k + 1, 11):
            if y <= k + 3:
                s.set(5, y, 23 - k, 'minecraft:air')
    s.set(5, 6, 19, 'minecraft:air')
    for i, x in enumerate(range(6, 15)):
        if i < 8:
            s.set(x, 6, 14, 'file', facing='south', has_book=False, powered=False)
    s.point('coro_alto', 10, 6, 16, 'north')
    s.point('coro_monja', 10, 6, 17.5, 'south')
    s.point('capilla_puerta', 10, 0, 10, 'north')
    s.area('capilla', 5, 0, 13, 15, 10, 37)
    s.area('coro_alto', 5, 6, 13, 15, 9, 18)
    # sacristy (chapter 7 checkpoint)
    s.room(16, 28, 22, 34, 0, 4, wall='chapel_wall', floor='floor', ceiling='ceiling')
    s.door('sacristia', 16, 0, 31, 'east', hinge='left', open_=False)
    s.point('sacristia', 19, 0, 31, 'west')

    # dormitory placeholder checkpoint (chapter 6, built in a later pass)
    s.point('dormitorio_puerta', -26, 0, 10, 'east')

    # whole interior (the "no running in the halls" rule)
    s.area('edificio', -28, 0, 0, 22, 10, 38)
    return s


def plan_png(s, path):
    """Top-down plan of the ground floor (y=0 and y=-1) for a quick sanity check."""
    from PIL import Image, ImageDraw
    x0, y0, z0, x1, y1, z1 = s.bounds()
    k = 8
    img = Image.new('RGB', ((x1 - x0 + 1) * k, (z1 - z0 + 1) * k), (24, 30, 22))
    d = ImageDraw.Draw(img)
    for (x, y, z), st in s.blocks.items():
        if y not in (0, 1):
            continue
        name = st.split('[')[0].split(':')[1]
        if name == 'air':
            continue
        col = (200, 200, 190)
        if 'door' in name:
            col = (150, 90, 40)
        elif 'glass' in name or 'pane' in name:
            col = (120, 170, 220)
        elif 'stairs' in name or 'slab' in name:
            col = (130, 100, 70)
        elif 'candle' in name or 'bulb' in name or 'lantern' in name:
            col = (255, 210, 90)
        elif 'wall' in name and 'brick' in name:
            col = (110, 110, 110)
        elif 'carpet' in name:
            col = (255, 255, 255)
        elif 'terracotta' in name and 'green' in name:
            col = (40, 90, 50)
        X, Z = (x - x0) * k, (z - z0) * k
        d.rectangle([X, Z, X + k - 1, Z + k - 1], fill=col)
    for name, (x, y, z, yaw) in s.markers['points'].items():
        X, Z = (x - x0) * k + k // 2, (z - z0) * k + k // 2
        d.ellipse([X - 3, Z - 3, X + 3, Z + 3], fill=(230, 40, 40))
        d.text((X + 4, Z - 4), name, fill=(255, 230, 230))
    img.save(path)


if __name__ == '__main__':
    site = build()
    out, n, pal = site.export()
    print(f'{out}: {n} blocks, {pal} states')
    sp = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad/sites'
    os.makedirs(sp, exist_ok=True)
    plan_png(site, os.path.join(sp, 'colegio_plan.png'))
    print(os.path.join(sp, 'colegio_plan.png'))
