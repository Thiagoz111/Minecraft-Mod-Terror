"""Colegio Santa Ines de la Vigilia (case 1). Layout from docs/design/BIBLIA.md 2.1 f.

    python3 tools/sites/colegio.py      -> src/main/resources/data/deadline/sites/colegio.json (+ a plan image)

Origin (0,0,0) is the main door; the facade is z=0, the building grows towards +z, the street is -z.
Ground floor: front rooms z 0..8 (classroom, hall, principal's office), corridor z 8..12, then the kitchen, dining
hall and chapel (with the upper choir over its entrance) from z 12. Everything is built from the colegio_* building kit
(tools/blocks/kit_colegio_*.py); K() places a kit block, PALETTE holds the semantic materials of walls and floors.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import Site, Palette  # noqa: E402

PALETTE = Palette({
    'wall_ext': ['colegio_revoque'] * 7 + ['colegio_revoque_humedad', 'colegio_revoque_descascarado', 'colegio_revoque_marcas'],
    'wall_base': 'colegio_revoque_salitre',
    'wall': ['colegio_revoque'] * 8 + ['colegio_revoque_marcas', 'colegio_revoque_humedad', 'colegio_revoque_descascarado'],
    'wall_cream': ['colegio_crema'] * 6 + ['colegio_crema_marcas'],
    'wall_damp': ['colegio_revoque_humedad', 'colegio_revoque_descascarado', 'colegio_revoque_salitre'],
    'floor': ['colegio_tablas'] * 3 + ['colegio_tablas_gastadas'],
    'floor_dark': 'colegio_madera_oscura',
    'checker': ['colegio_damero'] * 12 + ['colegio_damero_roto'] * 2 + ['colegio_damero_faltante'],
    'floor_kitchen': 'colegio_baldosa_colorada',
    'ceiling': 'colegio_cielorraso',
    'ceiling_wood': 'colegio_cielorraso_tablas',
    'ashlar': 'colegio_sillar',
    'chapel_floor': 'colegio_piso_capilla',
    'tile_wall': 'colegio_azulejo',
    'tile_floor': 'colegio_mosaico_bano',
    'crypt_wall': 'colegio_cripta_piedra',
    'crypt_floor': 'colegio_cripta_piso',
    'perimeter': 'colegio_muro_perimetral',
    'flagstone': 'colegio_patio_lajas',
    'new_brick': ['colegio_muro_ladrillo'] * 4 + ['colegio_muro_ladrillo_grieta'],
})
# story points nobody walks to: the sealed mirrored bathroom, the PA speaker, the 7 chairs behind the 1984 wall
SEALED = ('espejo_cara', 'espejo_detras', 'espejo_nena_', 'megafono', 'silla7_')
PLASTER = ('deadline:colegio_revoque', 'deadline:colegio_crema', 'deadline:colegio_azulejo', 'deadline:colegio_sillar')


def H(*a):
    return zlib.crc32(repr(a).encode()) % 1000


def K(s, x, y, z, key, facing=None, **props):
    """Places a building-kit block (key without the colegio_ prefix)."""
    if facing:
        props['facing'] = facing
    s.set(x, y, z, 'colegio_' + key, **props)


def stairs(s, x, y, z, key, facing, half='bottom'):
    K(s, x, y, z, key, facing, half=half, shape='straight')


def slab(s, x, y, z, key, type_='bottom'):
    K(s, x, y, z, key, type=type_)


def window3(s, x, y, z, facing, kind='ventana'):
    """Three-block window set into a wall (bottom, middle, arched top); faces the side it is mostly seen from."""
    for k, part in enumerate(('inf', 'med', 'sup')):
        K(s, x, y + k, z, f'{kind}_{part}', facing)


def doorway(s, name, x, y, z, facing, key, hinge='left', open_=False, transom=True):
    s.door(name, x, y, z, facing, mat='colegio_' + key, hinge=hinge, open_=open_)
    if transom:
        K(s, x, y + 2, z, 'banderola', facing)


def ring(x1, z1, x2, z2):
    for x in range(x1, x2 + 1):
        yield x, z1
        yield x, z2
    for z in range(z1 + 1, z2):
        yield x1, z
        yield x2, z


def skirting(s, x1, z1, x2, z2, y, key):
    """Replaces the plaster/tile ring of a room at height y (skirting board, tile border, salt-stained plinth)."""
    for x, z in ring(x1, z1, x2, z2):
        st = s.get(x, y, z)
        if st and st.split('[')[0].startswith(PLASTER):
            s.blocks[(x, y, z)] = 'deadline:colegio_' + key


def build():
    s = Site('colegio', PALETTE)

    # ------------------------------------------------------------ exterior: stone wall with a spear fence, the gate
    def fence(x, z, out):
        s.set(x, 0, z, 'perimeter')
        s.set(x, 1, z, 'perimeter')
        K(s, x, 2, z, 'muro_coronamiento', out)
        K(s, x, 3, z, 'reja_cerca', out)
    for x in range(-34, 35):
        if not -3 <= x <= 2:
            fence(x, -22, 'north')
        fence(x, 54, 'south')
    for z in range(-21, 54):
        fence(-34, z, 'west')
        fence(34, z, 'east')
    for x in (-3, 2):  # gate piers
        for y in range(0, 4):
            K(s, x, y, -22, 'revoque_descascarado' if y == 1 else 'revoque')
        K(s, x, 4, -22, 'pilar_remate', 'north')
    for i, x in enumerate((1, 0, -1, -2)):  # iron arch sign over the gate, 1..4 from the viewer's left
        K(s, x, 2, -22, f'letrero_{i + 1}', 'north')
    for z in (-21, -20):  # the gate stands open, its leaves swung in along the path
        for y, part in ((0, 'inf'), (1, 'sup')):
            K(s, -2, y, z, f'reja_porton_{part}', 'east')
            K(s, 1, y, z, f'reja_porton_{part}', 'west')
    K(s, -7, 0, -23, 'grafiti_kevin', 'north')
    K(s, 6, 0, -23, 'grafiti_aca_espantan', 'north')
    for z in range(-30, -4):
        for x in range(-2, 2):
            s.set(x, -1, z, 'flagstone')
    # the grotto of the Virgin: a safe island of candles that never go out
    gx, gz = -11, -10
    for dx in range(-2, 3):
        for dy in range(0, 4):
            K(s, gx + dx, dy, gz + 1, 'cripta_piedra')
            if abs(dx) == 2 or dy == 3:
                K(s, gx + dx, dy, gz, 'cripta_piedra')
    K(s, gx, 0, gz, 'virgen', 'north')
    for dx in (-1, 1):
        K(s, gx + dx, 0, gz, 'velas', 'north')
    s.light(gx, 1, gz - 1, 12, 'gruta')
    s.point('gruta', gx, 0, gz - 2, 'north')
    s.point('spawn', 0, 0, -27, 'south')
    s.area('exterior', -33, -2, -21, 33, 12, -1)
    # dry fountain and a chalk hopscotch in the front yard
    fx, fz = 15, -13
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            x, z = fx + dx, fz + dz
            if abs(dx) < 2 and abs(dz) < 2:
                K(s, x, -1, z, 'fuente_fondo')
            elif abs(dx) == 2 and abs(dz) == 2:
                K(s, x, 0, z, 'fuente_esquina', {(2, 2): 'north', (-2, 2): 'east', (-2, -2): 'south', (2, -2): 'west'}[(dx, dz)])
            else:
                K(s, x, 0, z, 'fuente_borde', 'north' if dz == 2 else 'south' if dz == -2 else ('west' if dx == 2 else 'east'))
    K(s, fx, -1, fz, 'piedra_fuente')
    K(s, fx, 0, fz, 'fuente_pila', 'north')
    for dx, dz, n in ((0, 0, '1'), (0, -1, '2'), (0, -2, '3'), (-1, -3, '4'), (1, -3, '5'), (0, -4, '6'), (-1, -5, '7'),
                      (1, -5, '8'), (0, -6, '9')):
        K(s, 8 + dx, 0, -6 + dz, 'rayuela_' + n, 'south')
    K(s, 8, 0, -13, 'rayuela_cielo', 'south')

    # ------------------------------------------------------------ facade, roof and the arched entrance portico
    for x in range(-28, 21):
        for y in range(0, 10):
            s.set(x, y, 0, 'wall_base' if y == 0 else 'wall_ext')
        for z in range(1, 8) if x in (-28, 20) else ():
            for y in range(0, 10):
                s.set(x, y, z, 'wall_base' if y == 0 else 'wall_ext')
    for x in range(-29, 22):
        K(s, x, 9, -1, 'alero', 'north')
        slab(s, x, 10, -1, 'tejas_losa')
        slab(s, x, 10, 0, 'tejas_losa', 'top')
        slab(s, x, 11, 1, 'tejas_losa')
        slab(s, x, 11, 2, 'tejas_losa', 'top')
        for z in range(3, 39):
            slab(s, x, 12, z, 'tejas_losa')
    for z in range(1, 39):  # gable ends under the roof slope
        for x in (-28, 20):
            for y in (10, 11) if z >= 3 else (10,):
                s.set(x, y, z, 'wall_ext')
    for x in range(-6, 7):
        k = (x + 6) % 4
        if k == 0:
            K(s, x, 0, -4, 'columna_base', 'north')
            K(s, x, 1, -4, 'columna_fuste', 'north')
            K(s, x, 2, -4, 'columna_capitel', 'north')
            s.set(x, 3, -4, 'wall_ext')
            s.set(x, 4, -4, 'wall_ext')
        elif k == 1:
            K(s, x, 3, -4, 'arco_bajo_izq', 'north')
            K(s, x, 4, -4, 'arco_alto_izq', 'north')
        elif k == 2:
            K(s, x, 4, -4, 'arco_alto_centro', 'north')
        else:
            K(s, x, 3, -4, 'arco_bajo_der', 'north')
            K(s, x, 4, -4, 'arco_alto_der', 'north')
        s.set(x, 5, -4, 'wall_ext')
        for z in range(-4, 0):
            s.set(x, -1, z, 'checker')
        for z in range(-3, 0):
            s.set(x, 5, z, 'ceiling_wood')
            if x % 2 == 0:
                K(s, x, 4, z, 'viga', 'north')
        K(s, x, 5, -5, 'alero', 'north')
        slab(s, x, 6, -5, 'tejas_losa')
        slab(s, x, 6, -4, 'tejas_losa', 'top')
        slab(s, x, 7, -3, 'tejas_losa')
        slab(s, x, 7, -2, 'tejas_losa', 'top')
        slab(s, x, 8, -1, 'tejas_losa')
        for (y, z) in ((6, -3), (6, -2), (6, -1), (7, -1)):
            s.set(x, y, z, 'wall_ext')

    # ------------------------------------------------------------ front rooms (z 0..8): classroom, hall, office
    s.room(-18, 0, -6, 8, 0, 4, wall='wall', floor='floor', ceiling='ceiling_wood')
    skirting(s, -18, 0, -6, 8, 0, 'friso')
    s.room(-6, 0, 6, 8, 0, 8, wall='wall', floor='checker', ceiling='ceiling')
    skirting(s, -6, 0, 6, 8, 0, 'friso')
    s.room(6, 0, 16, 8, 0, 4, wall='wall', floor='floor', ceiling='ceiling')
    skirting(s, 6, 0, 16, 8, 0, 'friso')
    # facade again on top of the room walls (rooms re-set z=0 with interior plaster)
    for x in range(-18, 17):
        for y in range(0, 10):
            if s.get(x, y, 0) and not s.get(x, y, 0).startswith('minecraft:air'):
                s.set(x, y, 0, 'wall_base' if y == 0 else 'wall_ext')
    doorway(s, 'entrada', 0, 0, 0, 'south', 'porton', hinge='left', open_=True)
    for x in (-15, -12, -9, -3, 3, 9, 12, 15):
        window3(s, x, 1, 0, 'north')
    for x in (-25, -21):
        window3(s, x, 1, 0, 'north', 'postigo')
    for x in (-24, -20, -16, -12, -8, 8, 12, 16):
        window3(s, x, 6, 0, 'north', 'ventana' if x in (-12, 12) else 'postigo')

    # hall: double height, wrought-iron chandelier, crown moulding, the founder's portrait, stairs up the east wall
    K(s, 0, 7, 4, 'arana')
    K(s, 0, 8, 4, 'cadena')
    s.fixture('hall_arana', 0, 7, 4)
    s.light(0, 5, 4, 10, 'hall_arana')
    s.light(0, 3, 2, 8, 'hall_arana')
    for x in range(-5, 6):
        K(s, x, 8, 1, 'cornisa', 'south')
        K(s, x, 8, 7, 'cornisa', 'north')
    for z in range(2, 7):
        K(s, -5, 8, z, 'cornisa', 'east')
        K(s, 5, 8, z, 'cornisa', 'west')
    for z in (3, 5):
        for x in range(-4, 5):
            K(s, x, 8, z, 'viga', 'east')
    K(s, 0, 8, 4, 'cadena')
    K(s, -5, 3, 4, 'retrato_benigna', 'east')
    K(s, -4, 2, 7, 'reglamento', 'north')  # "3. Toda voz será escuchada": the microphone counts
    K(s, -5, 0, 7, 'santa_ines', 'east')
    s.point('hall_centro', 0, 0, 4, 'north')
    s.point('hall', 0, 0, 6, 'north')
    s.point('megafono', 0, 7, 7, 'south')
    s.area('hall', -5, 0, 1, 5, 6, 7)

    # classroom (6th grade): 5x2 blackboard over the teacher's platform on the west wall, 12 desks with loose chairs
    for z in range(1, 8):
        K(s, -17, 0, z, 'tarima', 'east')
        K(s, -16, 0, z, 'tarima_borde', 'east')
    for c in range(5):  # izq = the viewer's left (south when the board faces east)
        z = 6 - c
        cn = 'izq' if c == 0 else 'der' if c == 4 else 'centro'
        K(s, -17, 2, z, f'pizarron_arriba_{cn}', 'east')
        K(s, -17, 1, z, f'pizarron_abajo_{cn}', 'east')
    s.write('pizarron', -17, 2, 4, 'east', width=5.0)
    K(s, -17, 3, 4, 'crucifijo_chico', 'east')
    K(s, -16, 0, 5, 'escritorio_maestra_izq', 'east')
    K(s, -16, 0, 6, 'escritorio_maestra_der', 'east')
    K(s, -17, 0, 6, 'silla_maestra', 'east')
    for i, z in enumerate((7, 5, 3, 1)):  # chalk squares a-d, read left to right from the class like the board
        K(s, -15, 0, z, 'tiza_' + 'abcd'[i], 'west')  # upright for the class looking at the board
        s.area('aula_' + 'abcd'[i], -15, 0, z, -15, 1, z)
    sillas = []
    for cx in (-13, -11, -9):
        for za, zb in ((1, 2), (5, 6)):
            K(s, cx, 0, zb, 'pupitre_mesa_izq', 'west')
            K(s, cx, 0, za, 'pupitre_mesa_der', 'west')
            for z in (za, zb):
                K(s, cx + 1, 0, z, 'silla_escolar', 'west')
                sillas.append([cx + 1, 0, z])
    s.markers['groups']['aula_sillas'] = sillas
    K(s, -11, -1, 4, 'tabla_floja')
    K(s, -7, 2, 3, 'mapa_argentina', 'west')
    K(s, -7, 2, 6, 'lista_castigos', 'west')
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

    # Mother Superior's office: her desk facing the door, the mate, the bakelite phone, the swivel chair, the cabinet
    K(s, 12, 0, 3, 'escritorio_madre_izq', 'south')
    K(s, 11, 0, 3, 'escritorio_madre_der', 'south')
    K(s, 12, 1, 3, 'mate_termo', 'south')
    s.point('direccion_mate', 12, 1, 3)
    K(s, 11, 1, 3, 'telefono_baquelita', 'south')
    s.point('direccion_telefono', 11, 1, 3)
    K(s, 11, 0, 2, 'silla_giratoria', 'south')
    s.markers['groups']['direccion_silla'] = [[11, 0, 2]]
    s.point('direccion_silla_pt', 11, 0, 2)
    K(s, 15, 0, 6, 'archivero', 'west')
    s.point('direccion_legajo', 15, 0, 6)
    K(s, 15, 0, 4, 'caja_fuerte', 'west')
    K(s, 7, 2, 4, 'foto_coro', 'east')
    K(s, 14, 2, 1, 'crucifijo_chico', 'south')
    K(s, 11, 4, 4, 'lampara_globo')
    s.fixture('direccion_luz', 11, 4, 4)
    s.light(13, 3, 6, 7, 'direccion_luz')
    s.area('direccion', 7, 0, 1, 15, 4, 7)

    # ------------------------------------------------------------ ground-floor corridor (z 8..12)
    s.room(-28, 8, 20, 12, 0, 3, wall='wall', floor='checker', ceiling='ceiling')
    skirting(s, -28, 8, 20, 12, 0, 'revoque_salitre')
    for x in range(-18, 17):  # the corridor ceiling cut into the taller front rooms' back wall
        s.set(x, 4, 8, 'wall')
    doorway(s, 'aula', -8, 0, 8, 'north', 'puerta_aula_6', hinge='right', open_=False)
    doorway(s, 'direccion', 11, 0, 8, 'north', 'puerta_direccion', hinge='left', open_=False)
    doorway(s, 'aula4', -20, 0, 8, 'north', 'puerta_aula_4', hinge='left', open_=False)  # locked for good
    K(s, -20, 0, 9, 'tablones_clavados', 'south')  # 4th grade: boarded up
    for x in (-1, 0, 1):  # archway into the hall
        for y in (0, 1, 2):
            s.set(x, y, 8, 'minecraft:air')
    K(s, -1, 3, 8, 'arco_bajo_izq', 'north')
    K(s, 1, 3, 8, 'arco_bajo_der', 'north')
    s.set(0, 3, 8, 'minecraft:air')
    K(s, -1, 4, 8, 'arco_alto_izq', 'north')
    K(s, 0, 4, 8, 'arco_alto_centro', 'north')
    K(s, 1, 4, 8, 'arco_alto_der', 'north')
    lamps = []
    for x in (17, 11, 5, -1, -7, -13, -19, -25):
        K(s, x, 3, 10, 'lampara_globo')
        lamps.append([x, 3, 10])
    s.markers['groups']['pasillo_pb'] = lamps
    for x in range(-26, 20):
        if x % 6 == 2:
            for z in (9, 10, 11):
                K(s, x, 3, z, 'viga', 'north')
    for x, z in ((-4, 10), (8, 9), (-16, 11)):
        K(s, x, -1, z, 'damero_huellas')
    K(s, -10, 1, 9, 'cartel_aula_6', 'south')
    K(s, -22, 1, 9, 'cartel_aula_4', 'south')
    K(s, 13, 1, 9, 'cartel_direccion', 'south')
    K(s, 4, 1, 9, 'cartel_prohibido_correr', 'south')
    K(s, 19, 2, 10, 'crucifijo_chico', 'west')
    s.point('pasillo_fondo', 18, 0, 10, 'west')
    s.area('pasillo_pb', -27, 0, 9, 19, 3, 11)

    # ------------------------------------------------------------ kitchen and dining hall (z 12..26)
    s.room(-28, 12, -18, 20, 0, 4, wall='tile_wall', floor='floor_kitchen', ceiling='ceiling')
    skirting(s, -28, 12, -18, 20, 2, 'azulejo_guarda')
    for y in (3, 4):
        for x, z in ring(-28, 12, -18, 20):
            s.set(x, y, z, 'wall_damp')
    s.room(-18, 12, -6, 26, 0, 4, wall='wall', floor='floor', ceiling='ceiling_wood')
    skirting(s, -18, 12, -6, 26, 0, 'friso')
    doorway(s, 'cocina', -23, 0, 12, 'south', 'puerta_celda', hinge='left', open_=False)
    for x in (-13, -12, -11):  # arched opening from the corridor
        for y in (0, 1, 2, 3):
            s.set(x, y, 12, 'minecraft:air')
    K(s, -13, 3, 12, 'arco_bajo_izq', 'north')
    K(s, -11, 3, 12, 'arco_bajo_der', 'north')
    K(s, -13, 4, 12, 'arco_alto_izq', 'north')
    K(s, -12, 4, 12, 'arco_alto_centro', 'north')
    K(s, -11, 4, 12, 'arco_alto_der', 'north')
    # service hatch between kitchen and dining hall (trapdoor: open = closed hatch)
    for z in (16, 17):
        K(s, -18, 1, z, 'ventanilla', 'east', half='top', open=False, powered=False)
    s.point('ventanilla', -18, 1, 16)
    s.point('ventanilla_monja', -19, 0, 16.5, 'east')
    s.point('cocina_fondo', -27, 0, 16, 'east')
    s.point('cocina_p1', -25, 0, 16, 'east')
    s.point('cocina_p2', -22, 0, 16, 'east')
    K(s, -27, 0, 14, 'cocina_hierro_izq', 'east')
    K(s, -27, 0, 15, 'cocina_hierro_der', 'east')
    for y in (2, 3, 4):
        K(s, -27, y, 14, 'cano_estufa', 'east')
    K(s, -27, 1, 15, 'olla', 'east')
    K(s, -27, 0, 17, 'ollas_piso', 'east')
    K(s, -25, 0, 18, 'mesa_larga_extremo', 'north')
    K(s, -24, 0, 18, 'mesa_larga_centro', 'north')
    K(s, -23, 0, 18, 'mesa_larga_extremo', 'south')
    K(s, -24, 1, 18, 'pila_platos', 'north')
    K(s, -25, 1, 18, 'olla', 'north')
    window3(s, -28, 1, 17, 'west')
    K(s, -23, 4, 16, 'lampara_globo_apagada')  # the kitchen is dark: her domain
    K(s, -21, 1, 19, 'tablero_llaves', 'north')
    s.point('tablero', -21, 1, 19)
    s.area('cocina', -27, 0, 13, -19, 4, 19)
    # dining hall: two long tables laid for supper with candlesticks, long benches, the reader's lectern
    velas = []
    for tx in (-14, -10):
        for z in range(15, 25):
            if z in (15, 24):
                K(s, tx, 0, z, 'mesa_larga_extremo', 'east' if z == 15 else 'west')
            else:
                K(s, tx, 0, z, 'mesa_larga_centro' if z in (16, 19, 22) else 'mesa_larga_puesta', 'east')
            K(s, tx - 1, 0, z, 'banco_largo_' + ('extremo' if z == 15 else 'fin' if z == 24 else 'centro'), 'east')
            K(s, tx + 1, 0, z, 'banco_largo_' + ('extremo' if z == 24 else 'fin' if z == 15 else 'centro'), 'west')
        for z in (16, 19, 22):
            K(s, tx, 1, z, 'candelero_mesa', 'east')
            velas.append([tx, 1, z])
    s.markers['groups']['refectorio_velas'] = velas
    K(s, -12, 0, 25, 'atril_lectura', 'north')
    K(s, -12, 2, 25, 'crucifijo_chico', 'north')
    for z in (17, 22):
        K(s, -12, 4, z, 'lampara_globo_apagada')
    window3(s, -18, 1, 23, 'west')
    for z in (16, 20, 24):
        window3(s, -6, 1, z, 'east', 'postigo')
    s.point('refectorio', -12, 0, 14, 'north')
    s.area('refectorio', -17, 0, 13, -7, 4, 25)

    # ------------------------------------------------------------ chapel (z 12..38) with the upper choir
    for x in range(4, 17):
        for z in range(12, 39):
            for y in range(0, 11):
                if x in (4, 16) or z in (12, 38):
                    K(s, x, y, z, 'sillar_tallado' if y == 1 else 'sillar_moldura' if y == 6 else 'sillar')
                else:
                    s.set(x, y, z, 'minecraft:air')
            s.set(x, -1, z, 'chapel_floor')
            s.set(x, 11, z, 'ceiling_wood')
            if z % 3 == 1 and 5 <= x <= 15:
                K(s, x, 10, z, 'viga', 'east')
    for z in (22, 26):
        K(s, 10, -1, z, 'lapida_piso')
    doorway(s, 'capilla', 10, 0, 12, 'south', 'puerta_capilla', hinge='left', open_=False)
    doorway(s, 'capilla2', 11, 0, 12, 'south', 'puerta_capilla', hinge='right', open_=False)
    for x, z, nm in ((4, 20, 'geo'), (4, 24, 'geo'), (4, 28, 'ines'), (4, 32, 'geo'), (16, 20, 'geo'), (16, 24, 'ines')):
        window3(s, x, 3, z, 'east' if x == 4 else 'west', f'vitral_{nm}')
    for x in (4, 16):
        window3(s, x, 6, 16, 'east' if x == 4 else 'west', 'vitral_geo')
    K(s, 11, 8, 38, 'roseton_sup_izq', 'north')  # rose window over the altar: izq = the viewer's left (east)
    K(s, 10, 8, 38, 'roseton_sup_der', 'north')
    K(s, 11, 7, 38, 'roseton_inf_izq', 'north')
    K(s, 10, 7, 38, 'roseton_inf_der', 'north')
    # pews in two blocks with a centre aisle (the sitter looks south at the altar)
    for z in range(21, 33, 2):
        for xa, xb in ((7, 9), (11, 13)):
            K(s, xb, 0, z, 'banco_iglesia_izq', 'south')
            K(s, xa + 1, 0, z, 'banco_iglesia_centro', 'south')
            K(s, xa, 0, z, 'banco_iglesia_der', 'south')
    K(s, 10, 0, 33, 'reclinatorio', 'south')
    # sanctuary: platform, altar with cloth, candlesticks, the big crucifix, the sanctuary lamp, statues
    for x in range(8, 13):
        K(s, x, 0, 37, 'tarima', 'north')
        K(s, x, 0, 35, 'tarima_borde', 'north')
    for x in (8, 12):
        K(s, x, 0, 36, 'tarima', 'north')
    K(s, 11, 0, 36, 'altar_izq', 'north')
    K(s, 10, 0, 36, 'altar_centro', 'north')
    K(s, 9, 0, 36, 'altar_der', 'north')
    K(s, 10, 2, 37, 'crucifijo_grande', 'north')
    K(s, 7, 0, 36, 'candelabro', 'north')
    K(s, 13, 0, 36, 'candelabro_apagado', 'north')
    K(s, 13, 0, 35, 'velas', 'north')
    K(s, 14, 0, 36, 'virgen', 'north')
    K(s, 6, 0, 36, 'santa_ines', 'north')
    s.light(10, 3, 34, 10, 'capilla_lampara')
    for x in (9, 11):
        K(s, x, 1, 36, 'candelero', 'north')
        s.fixture('capilla_lampara', x, 1, 36)
    K(s, 8, 4, 34, 'lampara_santisimo', 'north')
    s.fixture('capilla_lampara', 8, 4, 34)
    for y in range(5, 11):
        K(s, 8, y, 34, 'cadena')
    K(s, 13, 0, 15, 'pila_bautismal', 'north')
    K(s, 9, 1, 13, 'pila_agua_bendita', 'south')
    K(s, 12, 1, 13, 'pila_agua_bendita', 'south')
    # confessional against the west wall (penitent kneels on its south side)
    for r, rn in ((0, 'abajo'), (1, 'arriba')):
        K(s, 5, r, 25, f'confesionario_izq_{rn}', 'east')
        K(s, 5, r, 26, f'confesionario_centro_{rn}', 'east')
        K(s, 5, r, 27, f'confesionario_der_{rn}', 'east')
    s.point('confesionario', 5, 1, 26)
    s.point('confesionario_cara', 5, 0, 26, 'east')  # in the priest's booth, behind the grille
    s.area('confesionario_in', 6, 0, 26, 6, 2, 28)
    # upper choir over the entrance: floor at y=5, balustrade, 8 lecterns, a harmonium, stairs along the west wall
    for x in range(5, 16):
        for z in range(13, 19):
            s.set(x, 5, z, 'floor_dark')
    for x in range(6, 16):
        K(s, x, 6, 18, 'baranda', 'north')
    for k in range(6):
        stairs(s, 5, k, 23 - k, 'escalera_madera', 'north')
        for y in range(0, k):
            s.set(5, y, 23 - k, 'floor_dark')
        for y in range(k + 1, k + 4):
            s.set(5, y, 23 - k, 'minecraft:air')
        if k < 5:
            K(s, 5, k + 1, 23 - k, 'baranda_escalera_der', 'north')
    for x in range(7, 14):
        K(s, x, 6, 14, 'atril_coro_partitura' if x % 2 else 'atril_coro', 'north')
    K(s, 14, 6, 14, 'atril_albornoz', 'north')
    K(s, 14, 6, 16, 'armonio_izq', 'north')
    K(s, 15, 6, 16, 'armonio_der', 'north')
    s.point('coro_alto', 10, 6, 16, 'north')
    s.point('coro_monja', 10, 6, 17.5, 'north')
    s.point('capilla_puerta', 10, 0, 10, 'north')
    s.area('capilla', 5, 0, 13, 15, 10, 37)
    s.area('coro_alto', 5, 6, 13, 15, 9, 18)
    # sacristy (chapter 7 checkpoint)
    s.room(16, 28, 22, 34, 0, 4, wall='ashlar', floor='floor', ceiling='ceiling_wood')
    doorway(s, 'sacristia', 16, 0, 31, 'east', 'puerta_celda', hinge='left', open_=False)
    K(s, 21, 0, 33, 'ropero_abajo', 'west')
    K(s, 21, 1, 33, 'ropero_arriba', 'west')
    K(s, 21, 0, 29, 'baul', 'west')
    K(s, 17, 0, 33, 'candelabro_apagado', 'east')
    K(s, 21, 2, 31, 'crucifijo_chico', 'west')
    for z in range(28, 35):  # the sacristy ceiling must not cut into the chapel wall
        K(s, 16, 5, z, 'sillar')
    s.point('sacristia', 19, 0, 31, 'west')

    # ------------------------------------------------------------ first floor: stairs, corridor, dormitory, bathrooms
    # main staircase along the east wall of the hall, up to a landing and the first-floor corridor
    for k in range(6):
        stairs(s, 5, k, 2 + k, 'escalera_madera', 'south')
        for y in range(0, k):
            s.set(5, y, 2 + k, 'floor_dark')
        for y in range(k + 1, k + 4):
            s.set(5, y, 2 + k, 'minecraft:air')
        if k < 5:
            K(s, 5, k + 1, 2 + k, 'baranda_escalera_der', 'south')
    K(s, 4, 0, 2, 'baranda_poste', 'south')
    s.set(4, 5, 7, 'floor_dark')
    s.room(-18, 8, 8, 12, 6, 9, wall='wall', floor='floor', ceiling='ceiling')
    skirting(s, -18, 8, 8, 12, 6, 'friso')
    for x in (4, 5):
        for y in (6, 7):
            s.set(x, y, 8, 'minecraft:air')
    for x in range(-6, 7):  # the corridor floor cut into the hall's back wall
        s.set(x, 5, 8, 'wall')
    for x in range(4, 9):  # ...and its south wall into the chapel's stone front
        for y in range(5, 10):
            K(s, x, y, 12, 'sillar_moldura' if y == 6 else 'sillar')
    for x in range(-15, 7, 5):
        s.light(x, 8, 10, 4, 'pasillo_1p')
        K(s, x, 9, 10, 'lampara_globo_apagada')
    s.point('pasillo_1p', -2, 6, 10, 'west')
    s.area('pasillo_1p', -17, 6, 9, 7, 9, 11)
    # door from the first-floor corridor straight into the upper choir of the chapel
    doorway(s, 'coro', 6, 6, 12, 'south', 'puerta_celda', hinge='left', open_=False)
    # dormitory: two rows of 8 iron beds (some with shapes under the sheets), trunks, the warden's chair at the far end
    s.room(-18, 12, -6, 35, 6, 9, wall='wall', floor='floor', ceiling='ceiling_wood')
    skirting(s, -18, 12, -6, 35, 6, 'friso')
    doorway(s, 'dormitorio', -12, 6, 12, 'south', 'puerta_celda', hinge='left', open_=False)
    looks = ['', '_bulto', '_bulto', '_deshecha', '_bulto', '', '_bulto', '_deshecha']
    camas = []
    for i, z in enumerate(range(15, 31, 2)):
        w, e = looks[i], looks[(i + 3) % 8]
        if i == 7:
            e = '_deshecha'  # bed 8: Teresita's, left in a hurry
        K(s, -17, 6, z, f'cama{w}_cabecera', 'west')
        K(s, -16, 6, z, f'cama{w}_pie', 'west')
        K(s, -15, 6, z, 'baul', 'east')
        K(s, -7, 6, z, f'cama{e}_cabecera', 'east')
        K(s, -8, 6, z, f'cama{e}_pie', 'east')
        K(s, -9, 6, z, 'baul', 'west')
        camas += [[-17, 6, z], [-7, 6, z]]
    s.markers['groups']['dormitorio_camas'] = camas
    for z in range(16, 30, 2):
        if z in (18, 26):
            window3(s, -18, 6, z, 'west')
            window3(s, -6, 6, z, 'east')
            K(s, -17, 6, z, 'cortina_blanca', 'east')
            K(s, -7, 6, z, 'cortina_blanca', 'west')
        else:
            K(s, -17, 6, z, 'mesita_luz', 'east')
            K(s, -7, 6, z, 'mesita_luz', 'west')
    s.point('cama8', -8, 6, 29, 'west')
    for z in (15, 19, 23, 27, 31):  # 2x2 patches of moonlight down the aisle
        s.light(-12, 7, z, 9, 'dormitorio_luna')
        s.light(-11, 7, z + 1, 9, 'dormitorio_luna')
        for dx, dz, f in ((0, 0, 'north'), (1, 0, 'east'), (1, 1, 'south'), (0, 1, 'west')):
            K(s, -12 + dx, 6, z + dz, 'mancha_luna', f)
    s.area('dormitorio', -17, 6, 13, -7, 9, 34)
    s.point('dormitorio_puerta', -12, 6, 10, 'south')
    for i, z in enumerate((33, 29, 25, 21, 17)):
        s.point(f'dorm_silla_{i}', -12, 6, z, 'north')
    K(s, -12, 6, 33, 'silla_monja', 'north')
    s.markers['groups']['dorm_silla'] = [[-12, 6, 33]]
    K(s, -11, 6, 34, 'mesita_luz_campanita', 'north')
    K(s, -17, 6, 34, 'ropero_abajo', 'east')
    K(s, -17, 7, 34, 'ropero_arriba', 'east')
    K(s, -17, 8, 32, 'crucifijo_chico', 'east')
    # bathrooms at the far end, with a mirror wall onto a sealed mirrored copy
    s.room(-16, 35, -8, 43, 6, 9, wall='tile_wall', floor='tile_floor', ceiling='ceiling')
    skirting(s, -16, 35, -8, 43, 7, 'azulejo_guarda')
    doorway(s, 'banos', -12, 6, 35, 'south', 'puerta_celda', hinge='left', open_=False)
    s.room(-16, 43, -8, 51, 6, 9, wall='tile_wall', floor='tile_floor', ceiling='ceiling')
    skirting(s, -16, 43, -8, 51, 7, 'azulejo_guarda')
    for x in range(-15, -8):
        for y in range(6, 9):
            K(s, x, y, 43, 'espejo_bano', 'north')
    for x in (-14, -12, -10):
        K(s, x, 6, 42, 'lavatorio', 'north')
        K(s, x, 6, 44, 'lavatorio', 'south')
    K(s, -15, 6, 39, 'grafiti_sor_agonia', 'east')  # only on this side of the mirror
    K(s, -9, 6, 39, 'grafiti_tere_coro', 'west')
    s.light(-12, 8, 46, 9, 'espejo_luz')
    s.write('diario_espejo', -12, 7, 50, 'north', width=4.0)
    s.point('espejo', -12, 7, 43)
    s.point('espejo_cara', -11, 6, 44.4, 'north')  # between the mirrored sinks
    s.point('espejo_detras', -12, 6, 47, 'north')
    for i, x in enumerate((-14, -10)):
        s.point(f'espejo_nena_{i}', x, 6, 45, 'north')
    s.area('banos', -15, 6, 36, -9, 9, 42)

    # ------------------------------------------------------------ the Silence Room (a cupboard next to the sacristy)
    s.room(22, 29, 26, 33, 0, 1, wall='wall_damp', floor='floor', ceiling='ceiling_wood')
    doorway(s, 'cuarto_silencio', 22, 0, 31, 'west', 'puerta_silencio', hinge='left', open_=False, transom=False)
    K(s, 25, 0, 31, 'silla_escolar', 'west')
    s.light(24, 1, 32, 3, 'rendija')
    s.point('cuarto_silencio', 24, 0, 31, 'west')
    s.point('rendija', 25, 1, 31)
    s.area('cuarto_silencio', 23, 0, 30, 25, 1, 32)

    # ------------------------------------------------------------ the crypt under the chapel
    for x in range(4, 17):
        for z in range(20, 39):
            for y in range(-7, -1):
                edge = x in (4, 16) or z in (20, 38) or y == -2
                s.set(x, y, z, 'crypt_floor' if y == -7 else ('crypt_wall' if edge else 'minecraft:air'))
    for z in range(21, 38):  # vault springers
        stairs(s, 5, -3, z, 'cripta_escalera', 'west', half='top')
        stairs(s, 15, -3, z, 'cripta_escalera', 'east', half='top')
    # stairs down from the sacristy (east), through the chapel's east wall
    for k in range(6):
        x = 20 - k
        stairs(s, x, -k - 1, 30, 'cripta_escalera', 'east')  # rises toward the sacristy
        for y in range(-k, -k + 3):
            s.set(x, y, 30, 'minecraft:air')
    # niches on the long walls (Sister Maria's stands empty), the foundress' tomb in the middle
    for z, nm in ((22, 'garay'), (25, 'roldan'), (28, 'sellado'), (31, 'roto')):
        K(s, 4, -5, z, f'nicho_{nm}', 'east')
    for z, nm in ((22, 'iturbe'), (25, 'agonia')):
        K(s, 16, -5, z, f'nicho_{nm}', 'west')
    for x in range(9, 12):
        K(s, x, -6, 28, 'lapida_piso')
    s.point('cripta_tumba', 10, -6, 28)
    s.point('cripta_entrada', 15, -6, 30, 'west')
    # the 1984 brick wall and, behind it, the room of the 7 chairs facing the wall
    muro = []
    for x in range(5, 16):
        for y in range(-6, -2):
            if (x, y) == (10, -5):
                K(s, x, y, 33, 'muro_ladrillo_hueco', 'north')
            else:
                s.set(x, y, 33, 'new_brick')
            muro.append([x, y, 33])
    s.markers['groups']['cripta_muro'] = muro
    for i, x in enumerate(range(7, 14)):
        K(s, x, -6, 36, 'silla_escolar', 'north')
        s.point(f'silla7_{i}', x, -6, 36.2, 'north')
    islas = []
    # lit in this order by the girls as they run ahead: along the way out (tomb, stair foot, sacristy), never
    # within 4 blocks of the wall-to-tomb line where she starts
    for (x, y, z) in ((13, -6, 27), (14, -6, 32), (18, 0, 29), (19, 0, 33)):
        K(s, x, y, z, 'velas_apagadas', 'north')
        islas.append([x, y, z])
    s.markers['groups']['cripta_islas'] = islas
    s.area('cripta', 5, -6, 21, 15, -2, 37)
    s.point('regla_spawn', 10, -5, 28)

    # ------------------------------------------------------------ the upper choir: 7 unlit candles at the lecterns
    velas = []
    for i, x in enumerate(range(7, 14)):
        K(s, x, 6, 13, 'velas_apagadas', 'south')
        velas.append([x, 6, 13])
        s.point(f'vela_{i}', x, 6, 13)
        s.point(f'atril_{i}', x, 6, 15, 'north')
    s.markers['groups']['coro_velas'] = velas
    s.area('atril8', 13, 6, 14, 15, 8, 16)
    s.point('atril8', 14, 6, 15, 'north')
    s.point('coro_pared', 15, 6, 13.4, 'north')  # her kneeling spot, clear of the candle row

    # ------------------------------------------------------------ bell tower behind the corridor (the opening shot's silhouette)
    tx0, tx1, tz0, tz1, by = 17, 21, 13, 17, 17  # by = floor level of the belfry
    for x in range(tx0, tx1 + 1):
        for z in range(tz0, tz1 + 1):
            edge = x in (tx0, tx1) or z in (tz0, tz1)
            for y in range(0, by + 5):
                if by <= y <= by + 3 and not edge:
                    s.set(x, y, z, 'minecraft:air')
                elif y in (by - 1, by + 4, 11):
                    K(s, x, y, z, 'sillar_moldura')
                else:
                    K(s, x, y, z, 'sillar_tallado' if y in (1, 12) else 'sillar')
    sides = (('north', [(x, tz0) for x in range(tx0, tx1 + 1)]), ('south', [(x, tz1) for x in range(tx1, tx0 - 1, -1)]),
             ('west', [(tx0, z) for z in range(tz1, tz0 - 1, -1)]), ('east', [(tx1, z) for z in range(tz0, tz1 + 1)]))
    for facing, cells in sides:  # an arched opening on every side (izq = the left seen from outside)
        for k, (x, z) in enumerate(cells):
            if k in (0, 4):
                continue
            s.set(x, by, z, 'minecraft:air')
            s.set(x, by + 1, z, 'minecraft:air')
            if k == 2:
                s.set(x, by + 2, z, 'minecraft:air')
                K(s, x, by + 3, z, 'arco_alto_centro', facing)
            else:
                side = 'izq' if k == 1 else 'der'
                K(s, x, by + 2, z, f'arco_bajo_{side}', facing)
                K(s, x, by + 3, z, f'arco_alto_{side}', facing)
        x, z = cells[2]
        window3(s, x, 6, z, facing, 'postigo')  # a shuttered window halfway up
    K(s, 19, by + 1, 15, 'campana')
    K(s, 19, by + 2, 15, 'cadena')
    for span, y in ((range(tx0, tx1 + 1), by + 5), (range(tx0 + 1, tx1), by + 6)):  # tiled pyramid roof
        lo, hi = span[0], span[-1]
        zlo, zhi = tz0 + (lo - tx0), tz1 - (lo - tx0)
        for x in span:
            for z in range(zlo, zhi + 1):
                corner = x in (lo, hi) and z in (zlo, zhi)
                if corner or not (x in (lo, hi) or z in (zlo, zhi)):
                    K(s, x, y, z, 'tejas')
                elif z == zlo:
                    stairs(s, x, y, z, 'tejas_escalera', 'south')
                elif z == zhi:
                    stairs(s, x, y, z, 'tejas_escalera', 'north')
                elif x == lo:
                    stairs(s, x, y, z, 'tejas_escalera', 'east')
                else:
                    stairs(s, x, y, z, 'tejas_escalera', 'west')
    slab(s, 19, by + 7, 15, 'tejas_losa')
    K(s, 19, by + 8, 15, 'cruz_hierro', 'north')

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
    sp = _os.path.join(WORK, 'sites')
    os.makedirs(sp, exist_ok=True)
    plan_png(site, os.path.join(sp, 'colegio_plan.png'))
    print(os.path.join(sp, 'colegio_plan.png'))
