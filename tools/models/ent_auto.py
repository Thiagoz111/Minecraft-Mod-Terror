"""The hunter's car (DEAD LINE, case 2 'Casa Morales', docs/design/casa_terror.md 6.9) -- key 'auto'.

A 1970s Argentine four-door sedan, boxy and upright (the family car every uncle had): grey paint gone chalky, dents,
rust bubbling at the sills and arches, a cracked windshield cleaned only where the wipers reach, chrome bumpers
pitted with rust, cracked oxblood vinyl seats, a black bakelite steering wheel, and a wooden rosary hanging from the
rear-view mirror. NO brand names, badges or logos anywhere.

Scale: a VEHICLE, authored at 1x texel density (model.scale = 1.0; a 2x car would not fit a 256 x 256 atlas):
16 texels = 1 block. +Y down, ground y = 24, the car faces -Z, the driver sits on the LEFT (+X; right_* is -X).
Length 84 (5.25 blocks, bumper to bumper z -42..42), width 36 (2.25 blocks), height 32 (2.0 blocks, roof top y -8).
The seated occupants decide the cabin: car floor y = 18 (0.375 above the ground); CarEntity seats the riders' feet
0.145 below the car base, so a seated player's eye is 1.1 above the floor and the head top just under the roof
(y -6). Front hips at z -2, rear hips at z +16 (CarEntity.SEAT).

Bones (contract with com.deadline.client.model.AutoModel):
  body                       everything sprung (shell, cabin, interior); trembles while the engine idles
  wheel_fl/fr/rl/rr          roots at the axles: xRot = roll (distance / 6 texels), front yRot = steering
  door_fl/fr/rl/rr           hinged at their front edges (closed; can open with yRot)
  hood, trunk                hinged at the windscreen / the rear window (closed)
  windshield, rear_window    raked glass planes (+ wipers), a_pillars, c_pillars
  dashboard                  dash shelf + gauge binnacle (gauges glow on the eyes layer with the lights)
  steering_column -> steering_wheel   the wheel turns with zRot (its local axis is the column)
  seat_* / bench             front seat cushions + reclined backs, rear bench
  mirror -> rosary           rear-view mirror; the rosary swings (xRot / zRot) with the turns and the road
Emissive ('eyes' layer, drawn only while the lights are on): headlights, tail-lights, the gauges.
"""
import math

from mcmodel import Model, hash3, fbm, face_light, pick
from rig import Rig
from paint import hx, mix, scale

# ------------------------------------------------------------------ palettes
def H(*cs):
    return [hx(c) for c in cs]


GREY = H('#17191a', '#232625', '#313432', '#404440', '#50544f', '#61655f', '#737770', '#868981', '#999b93', '#acaea6',
         '#bfc1b9', '#d1d2cb')
PRIMER = H('#2e2b28', '#45403b', '#5d5750', '#77706a')
RUST = H('#1e0c05', '#331307', '#4d1d0a', '#6a2a0e', '#874015', '#a3561f', '#bb6d2c', '#cf8640')
MUD = H('#1d1712', '#2b231b', '#3b3025', '#4c3e2f', '#5d4d3a', '#6e5d47')
CHROME = H('#1b1d22', '#30343b', '#4a5059', '#6b727c', '#8f97a1', '#b4bbc3', '#d6dbe0', '#f0f2f5')
RUBBER = H('#0b0b0c', '#131315', '#1b1b1e', '#242428', '#2e2e33', '#3a3a40')
VINYL = H('#120506', '#1e080a', '#2c0d0f', '#3c1315', '#4e1b1c', '#622526', '#783232', '#8c4140')
CARPET = H('#0d0b0a', '#151210', '#1e1a17', '#28231f', '#332d28')
HEADLINER = H('#3b352c', '#544c40', '#6e6555', '#877d6a', '#9f957f', '#b5ab93', '#c8bfa7')
DASH = H('#070707', '#0e0d0d', '#161514', '#201e1c', '#2b2826', '#383431')
BAKELITE = H('#050505', '#0b0b0b', '#141414', '#1e1e1e', '#2a2a2a', '#3a3a3a', '#555555')
WOOD = H('#1a0d06', '#2b170b', '#3f2311', '#553018', '#6b3e21', '#83502c')
SILVER = H('#3a3d42', '#62666d', '#8c9198', '#b6bbc1', '#dfe3e7')
LENS = H('#5b5545', '#7f7860', '#a59d80', '#cbc3a2', '#e9e2c4', '#fbf7e6')
RED_LENS = H('#2a0204', '#4a0508', '#6e0a0e', '#941317', '#b8221f', '#d8433a')
AMBER = H('#3a1c02', '#6a3404', '#a35408', '#d07a12', '#eea33a')
GRILLE = H('#040404', '#0a0a0b', '#141416', '#1f1f22', '#2d2d31')
PLATE = H('#050506', '#0c0c0e', '#141418')
PLATE_TXT = hx('#d9dcdf')
UNDER = H('#0a0908', '#12100e', '#1b1814', '#26211b')
GLASS_STREAK = H('#5f6a72', '#7d8890', '#9ea8af', '#c3cbd0')
GRIME = H('#2c2620', '#3d352c', '#4e4438')
GAUGE = H('#030405', '#0a0c0e', '#14171a')


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ geometry constants (texels)
WHEEL_R = 7           # wheel radius: 0.44 blocks (CarEntity.WHEEL_RADIUS)
AXLE_Y = 24 - WHEEL_R
FRONT_AXLE, REAR_AXLE = -27, 28
BELT = 5              # beltline / bonnet / boot top
TRIM_Y = 10.4         # chrome strip along the flanks
ROOF_TOP, ROOF_BOT = -8, -6
FLOOR = 18
WS_PIVOT = (0, BELT, -18)          # windscreen bottom edge
WS_RAKE = -39.3                    # top leans back to z -9 at y -6
WS_LEN = 14
RW_PIVOT = (0, BELT, 22)           # rear window bottom edge
RW_RAKE = 36.0                     # top leans forward to z 14
RW_LEN = 14

# dents: (side, centre (a, b) on that face's plane, radius, depth) -- side: 'L' x=+18, 'R' x=-18, 'T' top, 'F' front
DENTS = [('R', (11.0, 13.0), 4.5, 1.0),      # right rear door, someone backed into it
         ('L', (-31.0, 9.5), 3.2, 0.8),      # left front wing above the wheel
         ('T', (-7.0, -31.0), 3.5, 0.7),     # bonnet
         ('T', (9.0, 35.0), 3.0, 0.9),       # boot lid corner
         ('L', (24.0, 14.5), 2.6, 0.7),      # left rear quarter
         ('R', (-12.0, 9.0), 2.2, 0.6)]      # right front door


# ------------------------------------------------------------------ helpers
def lum(v, ramp):
    return pick(ramp, v)


def h2(i, j, s=0):
    return hash3(i, j, s * 7 + 3, s)


def side_dent(ctx, x, y, z):
    """Concave shading for the dents: lit on the side facing the light, dark on the far side."""
    v = 0.0
    n = ctx.n
    for side, (a, b), r, depth in DENTS:
        if side == 'L' and n[0] > 0.5 and x > 16:
            da, db = z - a, y - b
        elif side == 'R' and n[0] < -0.5 and x < -16:
            da, db = z - a, y - b
        elif side == 'T' and n[1] < -0.5:
            da, db = x - a, z - b
        else:
            continue
        d = math.sqrt(da * da + db * db)
        if d < r:
            k = 1.0 - d / r
            # light comes from the front-top: the wall of the dent toward it is in shade, the far wall catches light
            v += (-(da / r) * 0.38 + (db / r) * 0.2) * k * depth
            if 0.35 < d / r < 0.55 and h2(int(da * 3), int(db * 3), 5) > 0.55:
                v -= 0.08 * depth   # creased paint
    return v


def rust_amount(x, y, z, extra=0.0):
    """0..1 rust coverage: the sills, the wheel arches, the bottom of the doors and a few spots elsewhere."""
    low = max(0.0, (y - 11.0) / 7.0)
    arch = 0.0
    for az in (FRONT_AXLE, REAR_AXLE):
        d = math.sqrt((z - az) ** 2 + (y - AXLE_Y) ** 2)
        if WHEEL_R - 0.5 < d < WHEEL_R + 4.5:
            arch = max(arch, 1.0 - abs(d - (WHEEL_R + 1.5)) / 3.0)
    n = fbm(x * 0.13 + 7, y * 0.13, z * 0.13, 3, 11)
    t = 0.7 - 0.24 * low - 0.2 * arch - extra
    a = (n - t) * 5.0
    spots = fbm(x * 0.32, y * 0.32 + 3, z * 0.32, 2, 19)
    if spots > 0.8:
        a = max(a, (spots - 0.8) * 7.0)
    return max(0.0, min(1.0, a))


def dirt_amount(x, y, z):
    """Mud thrown up by the wheels: heavy on the sills and behind the arches, splatter above."""
    low = max(0.0, (y - 9.0) / 10.0) ** 1.6
    behind = 0.0
    for az in (FRONT_AXLE, REAR_AXLE):
        if 0 < z - az < 14:
            behind = max(behind, 0.5 * (1 - (z - az) / 14))
    n = fbm(x * 0.6, y * 0.6, z * 0.6, 2, 23)
    return max(0.0, min(1.0, low * 1.25 + behind * low + (n - 0.5) * 0.6))


# ------------------------------------------------------------------ materials
def paint_mat(ctx):
    """The body: chalky grey paint, panel gaps, dents, scratches, rust and mud."""
    x, y, z = ctx.pos
    cube = ctx.cube
    v = 0.43 + face_light(ctx) * 0.85
    v += (fbm(x * 0.18, y * 0.18, z * 0.18, 3, 2) - 0.5) * 0.14    # faded, uneven paint
    if ctx.n[1] < -0.5:
        v += (fbm(x * 0.12, 0, z * 0.12, 2, 4) - 0.5) * 0.16 + 0.04  # sun-bleached patches on the top
    v += side_dent(ctx, x, y, z)
    e = ctx.edge()
    gaps = getattr(cube, 'gaps', True)
    if e == 0 and gaps:
        v -= 0.13                                                 # panel gaps
    elif e == 1 and gaps and ctx.n[1] > -0.5:
        v += 0.03
    v += (h2(ctx.i, ctx.j, 77) - 0.5) * 0.04
    col = lum(v, GREY)
    # the chrome strip along the flanks and round the wheel arches
    if abs(ctx.n[0]) > 0.5 and TRIM_Y - 0.4 <= y <= TRIM_Y + 0.4 and abs(x) > 17:
        tv = 0.62 + (0.2 if (int(z) % 6) == 0 else 0) + (h2(int(z), 1, 3) - 0.5) * 0.2
        col = lum(tv, CHROME)
    # a chrome line round the window openings (beltline)
    if abs(ctx.n[0]) > 0.5 and BELT <= y <= BELT + 0.5 and abs(x) > 17:
        col = lum(0.55, CHROME)
    # key scratch: somebody keyed the right flank long ago (primer in the line)
    if ctx.n[0] < -0.5 and x < -17 and abs(y - (8.0 + (z + 15) * 0.03)) < 0.5 and -15 < z < 17 and h2(int(z * 2), 3, 9) > 0.2:
        col = lum(0.6 + (h2(int(z), 2, 4) - 0.5) * 0.3, PRIMER)
    name = getattr(cube, 'name', '')
    if name == 'hood' and ctx.face == 'top':
        if abs(abs(x) - 7.5) < 0.5:
            col = lum(v + 0.1, GREY)                              # the two bonnet creases
        elif abs(abs(x) - 8.5) < 0.5:
            col = lum(v - 0.08, GREY)
        if z > -22 and abs(x) < 12 and int(x) % 2 == 0:
            col = lum(0.12, GRILLE)                               # cowl vents under the windscreen
    if name == 'quarter' and ctx.n[0] < -0.5 and (z - 30) ** 2 + (y - BELT - 2.5) ** 2 < 2.3:
        col = lum(0.62 if (z - 30) + (y - BELT - 2.5) < 0 else 0.4, CHROME)    # fuel cap
    if name == 'trunk' and ctx.face == 'back':
        if abs(x) < 0.8 and abs(y - (BELT + 1.5)) < 0.8:
            col = lum(0.7, CHROME)                                # boot lock
        if abs(y - (BELT + 0.5)) < 0.4 and abs(x) < 11:
            col = lum(0.55, CHROME)                               # chrome strip over the plate
    # chipped paint along the edges
    if e == 0 and h2(ctx.i, ctx.j, 5) > 0.88:
        col = lum(0.45, PRIMER)
    r = rust_amount(x, y, z)
    if r > 0:
        rv = 0.3 + r * 0.25 + (fbm(x * 0.9, y * 0.9, z * 0.9, 2, 31) - 0.5) * 0.45 + face_light(ctx) * 0.6
        rc = lum(rv, RUST)
        col = mix(col, rc, 0.45) if r < 0.3 else rc               # orange bloom under the paint, then bare rust
    d = dirt_amount(x, y, z)
    if d > 0.25:
        dv = 0.45 + (fbm(x * 1.1, y * 1.1, z * 1.1, 2, 41) - 0.5) * 0.5 + face_light(ctx) * 0.5
        col = mix(col, lum(dv, MUD), min(0.85, (d - 0.25) * 1.6))
    return col


def chassis_mat(ctx):
    """Valance and chassis boxes: painted where they show, dark underneath."""
    if ctx.face == 'bottom' or (abs(ctx.n[0]) > 0.5):
        return under_mat(ctx)
    return paint_mat(ctx)


def chrome_mat(ctx):
    x, y, z = ctx.pos
    v = 0.55 + face_light(ctx) * 1.2
    if ctx.n[1] < -0.5:
        v += 0.18
    # a bright reflection band and dark sky line, like old bumpers
    t = ctx.t if ctx.h > 1 else 0.5
    v += 0.25 if t < 0.35 else (-0.2 if t > 0.75 else 0)
    v += (h2(ctx.i, ctx.j, 7) - 0.5) * 0.12
    col = lum(v, CHROME)
    pit = fbm(x * 0.9, y * 0.9, z * 0.9, 2, 51)
    if pit > 0.62:
        col = lum(0.25 + (pit - 0.62) * 2, RUST)               # pitted, rust bleeding through
    elif pit > 0.56:
        col = mix(col, lum(0.4, RUST), 0.5)
    if ctx.edge() == 0:
        col = scale(col, 0.75)
    return col


def rubber_mat(ctx):
    """Tyres: tread blocks on the rolling faces, a smooth worn sidewall."""
    if ctx.face in ('east', 'west'):
        e = min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)
        v = 0.45 + face_light(ctx) + (0.1 if e == 1 else 0) + (h2(ctx.i, ctx.j, 2) - 0.5) * 0.1
        return lum(v, RUBBER)
    # tread: across the tyre (i) there are 2 ribs, along it (j) blocks every 2 texels
    groove = (ctx.j % 2 == 0) or ctx.i in (0, ctx.w - 1)
    v = (0.25 if groove else 0.65) + face_light(ctx) + (h2(ctx.i, ctx.j, 4) - 0.5) * 0.12
    return lum(v, RUBBER)


def hubcap_mat(ctx):
    """Steel rim painted dark grey with its ring of holes, a small chrome cap in the middle (painted once for 4)."""
    if ctx.face not in ('east', 'west'):
        return lum(0.35 + face_light(ctx), GREY)
    cx, cy = (ctx.w - 1) / 2.0, (ctx.h - 1) / 2.0
    dx, dy = ctx.i - cx, ctx.j - cy
    d = math.sqrt(dx * dx + dy * dy)
    if d > 3.9:
        return lum(0.12, RUBBER)
    if d > 3.2:
        return lum(0.42 + (0.1 if dy < 0 else -0.05), GREY)      # rim lip
    if d < 1.7:
        v = 0.8 - d * 0.15 + (0.15 if dx < 0 and dy < 0 else 0)
        return lum(v, CHROME)                                     # chrome cap
    ang = math.atan2(dy, dx)
    if int((ang + 3.2) / (math.pi / 3)) % 2 == 0 and 2.0 < d < 3.0:
        return lum(0.05, RUBBER)                                  # holes in the steel wheel
    col = lum(0.3 + (h2(ctx.i, ctx.j, 3) - 0.5) * 0.1, GREY)
    if h2(ctx.i, ctx.j, 9) > 0.75:
        col = lum(0.35, RUST)
    return col


def nut_mat(ctx):
    return lum(0.55 + face_light(ctx), CHROME)


def glass_mat(kind):
    """Glass: see-through (cutout) with dirt, streaks, wiper arcs and (on the windscreen) a crack."""
    def f(ctx):
        x, y, z = ctx.pos
        # local plane coordinates
        if kind == 'ws':
            u, w = x, ctx.t                       # w: 0 top .. 1 bottom
        elif kind == 'rw':
            u, w = x, ctx.t
        else:
            u, w = z, (y + 6) / 13.0
        grime = 0.01 + 0.16 * max(0.0, w - 0.8) * 5
        if kind == 'ws':
            # the two wiper sweeps (pivots under the glass) stay clean; outside them, a film of dust
            inside = False
            for px in (-8.0, 7.0):
                dd = math.sqrt((u - px) ** 2 + ((1.0 - w) * WS_LEN + 2.0) ** 2)
                if dd < 11.5:
                    inside = True
            grime = 0.004 if inside else 0.07 + 0.2 * max(0.0, w - 0.75) * 4
            # a crack from a stone hit on the passenger side: a small star, thin dark-and-light lines
            cx, cy = -9.0, 0.3
            ax, ay = u - cx, (w - cy) * WS_LEN
            r = math.sqrt(ax * ax + ay * ay)
            if r < 6.0:
                ang = math.atan2(ay, ax)
                for k in range(6):
                    a0 = k * 1.05 + 0.35 * math.sin(k * 3.1)
                    length = 2.5 + (k * 37 % 4)
                    if abs(math.sin(ang - a0)) * r < 0.35 and math.cos(ang - a0) > 0 and r < length:
                        return A(lum(0.45, GLASS_STREAK)) if (k + int(r)) % 2 else A(GRIME[0])
                if r < 0.7:
                    return A(GLASS_STREAK[2])
        if h2(int(u * 2), int(w * 40), 13 + len(kind)) < grime:
            return A(lum(h2(int(u), int(w * 9), 2) * 0.7, GRIME))
        # streaky reflections (diagonal)
        s = (u * 0.55 + w * 14) % 13
        if kind != 'side' and s < 0.5 and h2(int(u), int(w * 30), 7) > 0.7:
            return A(lum(0.1 + h2(int(u * 3), 1, 1) * 0.25, GLASS_STREAK))
        return None
    return f


def lens_mat(ramp, kind):
    def f(ctx):
        lit_face = (kind == 'head' and ctx.face == 'front') or (kind == 'tail' and ctx.face == 'back') or \
                   (kind == 'ind' and ctx.face == 'front')
        if not lit_face:
            return chrome_mat(ctx)
        e = ctx.edge()
        if e == 0:
            return lum(0.6 + face_light(ctx), CHROME)             # chrome bezel
        if kind == 'head':
            # square lens with a reflector bowl: rings + a dimpled pattern; one lens yellowed and cracked
            cx, cy = (ctx.w - 1) / 2.0, (ctx.h - 1) / 2.0
            d = math.sqrt((ctx.i - cx) ** 2 + ((ctx.j - cy) * 1.4) ** 2)
            v = 0.75 - d * 0.1 + (0.12 if (ctx.i + ctx.j) % 2 == 0 else 0)
            if ctx.pos[0] < 0:
                v -= 0.15
                if abs(ctx.i - ctx.j * 1.2 - 1) < 0.6:
                    return A(GRIME[0])
            return lum(v, ramp)
        if kind == 'tail':
            v = 0.55 + (0.2 if ctx.j % 2 == 0 else 0) - (0.25 if ctx.j == ctx.h // 2 else 0)
            if 0 < ctx.j < 2:
                return lum(0.7, AMBER)                            # indicator section on top
            return lum(v, ramp)
        return lum(0.65 + (0.15 if ctx.i % 2 else 0), ramp)
    return f


def grille_mat(ctx):
    """Grille panel: horizontal black slats between the two headlights, a chrome surround."""
    if ctx.face != 'front':
        return paint_mat(ctx)
    e = ctx.edge()
    if e == 0:
        return lum(0.62 + face_light(ctx), CHROME)
    x = ctx.pos[0]
    if abs(x) > 8.5:                       # behind the headlights: painted panel
        return paint_mat(ctx)
    v = 0.6 if ctx.j % 2 == 0 else 0.15
    if abs(x) < 0.6:
        v = 0.45
    col = lum(v, GRILLE)
    if h2(ctx.i, ctx.j, 61) > 0.93:
        col = lum(0.3, RUST)
    return col


def plate_mat(ctx):
    """Old Argentine plate: black with white embossed characters (no brand, no logo)."""
    if ctx.face not in ('front', 'back'):
        return lum(0.4, CHROME)
    e = ctx.edge()
    if e == 0:
        return lum(0.5, CHROME)
    # 'X 404.661' as 3x? blocks would not fit: a row of dashes that read as characters from afar
    i, j = ctx.i, ctx.j
    glyph = (i - 1) % 3 != 2 and j in (1,) or ((i - 1) % 3 == 0 and j == 1)
    if 1 <= i < ctx.w - 1 and j == 1 and (i % 3 != 0) and i != 2:
        return PLATE_TXT if h2(i, j, 3) > 0.15 else lum(0.5, PLATE)
    return lum(0.5 + (h2(i, j, 2) - 0.5) * 0.2, PLATE)


def under_mat(ctx):
    x, y, z = ctx.pos
    v = 0.45 + face_light(ctx) + (fbm(x * 0.5, y * 0.5, z * 0.5, 2, 71) - 0.5) * 0.4
    col = lum(v, UNDER)
    if rust_amount(x, y, z, 0.25) > 0.3:
        col = mix(col, lum(0.3, RUST), 0.6)
    return col


def vinyl_mat(ctx):
    """Cracked oxblood vinyl, piped seams; the driver's seat worn through to the foam on one side."""
    x, y, z = ctx.pos
    v = 0.5 + face_light(ctx) * 1.2 + (fbm(x * 0.5, y * 0.5, z * 0.5, 2, 81) - 0.5) * 0.25
    # tufted channels
    if ctx.face in ('front', 'back') and ctx.h > 4:
        if ctx.i % 3 == 0:
            v -= 0.2
    if ctx.face in ('top',) and ctx.w > 6 and ctx.i % 4 == 0:
        v -= 0.18
    if ctx.edge() == 0:
        v -= 0.15
    col = lum(v, VINYL)
    crack = fbm(x * 1.7, y * 1.7, z * 1.7, 2, 83)
    if 0.49 < crack < 0.51:
        col = lum(0.15, VINYL)
    if x > 3 and x < 7 and ctx.face == 'top' and -6 < z < -1:
        col = H('#8a7a5a', '#a8976f')[int(h2(ctx.i, ctx.j, 3) * 2)]    # foam showing through the split
    return col


def beads_mat(ctx):
    """The driver's seat wears a wooden-bead cover (every taxi and every uncle's car had one)."""
    if ctx.face not in ('back', 'front', 'top'):
        return vinyl_mat(ctx)
    i, j = ctx.i, ctx.j
    if i % 2 == 0 and j % 2 == 0:
        return lum(0.55 + (h2(i, j, 7) - 0.5) * 0.35 + (0.12 if (i // 2 + j // 2) % 3 == 0 else 0), WOOD)
    if i % 2 == 1 and j % 2 == 1:
        return lum(0.1, VINYL)
    return lum(0.25, WOOD)


def paper_mat(ctx):
    """An old folded newspaper on the parcel shelf (columns of grey 'text', a dark photo block)."""
    i, j = ctx.i, ctx.j
    v = 0.6 + face_light(ctx) * 0.5
    col = lum(v, HEADLINER)
    if ctx.face == 'top':
        if j % 2 == 1 and i % 4 != 3 and h2(i, j, 5) > 0.25:
            col = lum(0.3, HEADLINER)
        if 1 <= i <= 3 and 1 <= j <= 3:
            col = lum(0.15, HEADLINER)
    return col


def flap_mat(ctx):
    return lum(0.35 + face_light(ctx) + (h2(ctx.i, ctx.j, 3) - 0.5) * 0.15, RUBBER)


def carpet_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom':
        return under_mat(ctx)
    v = 0.5 + (h2(int(x * 2), int(z * 2), 3) - 0.5) * 0.35 + face_light(ctx)
    col = lum(v, CARPET)
    # a dark old stain under the rear bench, and the rubber mat under the driver's feet
    if 3 < x < 14 and -18 < z < -9:
        col = lum(0.5 + (0.2 if int(z) % 2 else 0), RUBBER)
    if (x + 4) ** 2 + (z - 14) ** 2 < 10:
        col = scale(col, 0.6)
    return col


def headliner_mat(ctx):
    x, y, z = ctx.pos
    v = 0.55 + (fbm(x * 0.4, 0, z * 0.4, 2, 91) - 0.5) * 0.3
    col = lum(v, HEADLINER)
    stain = fbm(x * 0.25 + 3, 0, z * 0.25, 2, 93)
    if stain > 0.66:
        col = mix(col, lum(0.25, MUD), 0.6)                      # water stains; and smoke
    return col


def roof_mat(ctx):
    if ctx.face == 'bottom':
        return headliner_mat(ctx)
    return paint_mat(ctx)


def dash_mat(ctx):
    x, y, z = ctx.pos
    v = 0.5 + face_light(ctx) * 1.2 + (fbm(x * 0.6, y * 0.6, z * 0.6, 2, 101) - 0.5) * 0.2
    col = lum(v, DASH)
    if ctx.face == 'top' and abs(fbm(x * 0.9, 0, z * 0.9, 2, 103) - 0.5) < 0.012:
        col = lum(0.9, DASH)                                      # sun-cracked dash top
    # glovebox (passenger side) with its chrome button; a faded saint's sticker
    if ctx.face == 'back':
        if -13 < x < -4 and 8 < y < 10.5:
            col = lum(v + 0.12, DASH)
            if abs(x + 4.6) < 0.6 and abs(y - 9.3) < 0.6:
                col = lum(0.7, CHROME)
        if -2 < x < 0 and 8 < y < 10:
            col = H('#7a6a3c', '#9a8a54', '#c2b27a', '#556a8a')[(ctx.i + ctx.j) % 4]
        if 1 < x < 3 and 8.5 < y < 10:
            col = lum(0.6, CHROME)                                # radio knobs
    return col


def binnacle_mat(ctx):
    """Gauge hood: two round dials facing the driver (white ticks, orange needles)."""
    if ctx.face != 'back':
        return dash_mat(ctx)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    for gcx in (w * 0.28, w * 0.72):
        dx, dy = i - gcx + 0.5, j - (h - 1) / 2.0
        d = math.sqrt(dx * dx + dy * dy)
        if d < h * 0.55:
            if d > h * 0.45:
                return lum(0.7, CHROME)
            ang = math.atan2(dy, dx)
            if d > h * 0.28 and int((ang + 4) * 3) % 2 == 0:
                return hx('#d8d4c8')
            if abs(dy - dx * 0.4) < 0.5 and d < h * 0.4 and dx < 0:
                return hx('#e07020')
            return lum(0.5, GAUGE)
    return dash_mat(ctx)


def bakelite_mat(ctx):
    v = 0.5 + face_light(ctx) + (0.2 if ctx.edge() == 0 and ctx.n[1] < 0 else 0) + (h2(ctx.i, ctx.j, 111) - 0.5) * 0.1
    col = lum(v, BAKELITE)
    if h2(ctx.i, ctx.j, 113) > 0.9:
        col = H('#6a5a3a', '#4a3e28')[ctx.i % 2]                 # worn through to the brown bakelite
    return col


def mirror_mat(ctx):
    if ctx.face == 'back':
        if ctx.edge() == 0:
            return lum(0.3, BAKELITE)
        # dark glass with the faint reflection of the empty back seat
        v = 0.25 + (0.2 if ctx.j == 0 else 0) + (h2(ctx.i, ctx.j, 3) - 0.5) * 0.1
        return lum(v, GLASS_STREAK)
    return bakelite_mat(ctx)


def rosary_mat(ctx):
    """Wooden beads on a cord (cutout), five decades shown as a loop of beads with a gap at the top."""
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    # a hanging loop: two strands converging at the bottom
    mid = (w - 1) / 2.0
    spread = mid * (1 - j / max(1.0, h - 1.0)) ** 0.7
    on_strand = abs(abs(i - mid) - spread) < 0.6
    if not on_strand:
        return None
    if (j + (1 if i < mid else 0)) % 2 == 0:
        return lum(0.55 + (h2(i, j, 5) - 0.5) * 0.3 + (0.15 if i < mid else 0), WOOD)   # a bead
    return hx('#2a2018')                                          # cord


def cross_mat(ctx):
    return lum(0.55 + face_light(ctx) + (0.2 if ctx.edge() == 0 else 0), SILVER)


def door_mat(side):
    """Doors: paint outside; inside, the vinyl door card with a chrome handle and the window winder."""
    def f(ctx):
        inner = (side > 0 and ctx.face == 'west') or (side < 0 and ctx.face == 'east')
        if not inner:
            return paint_mat(ctx)
        x, y, z = ctx.pos
        if ctx.edge() == 0:
            return paint_mat(ctx)
        v = 0.45 + (fbm(y * 0.5, z * 0.5, x, 2, 121) - 0.5) * 0.2
        col = lum(v, VINYL)
        if BELT + 1.5 < y < BELT + 2.5:
            col = lum(0.6, CHROME)                                # chrome trim strip
        zc = z - getattr(ctx.cube, 'zc', 0)
        if abs(zc - 4) < 1.5 and BELT + 3 < y < BELT + 4.5:
            col = lum(0.7, CHROME)                                # door handle
        if abs(zc + 2) < 1.2 and abs(y - (BELT + 6)) < 1.2:
            col = lum(0.5, CHROME)                                # window winder
        if y > 16:
            col = lum(0.4, CARPET)
        return col
    return f


def wood_mat(ctx):
    return lum(0.5 + face_light(ctx), WOOD)


def antenna_mat(ctx):
    return lum(0.6 + face_light(ctx) + (0.2 if ctx.j % 3 == 0 else 0), CHROME)


MATS = {
    'paint': paint_mat, 'chrome': chrome_mat, 'rubber': rubber_mat, 'hubcap': hubcap_mat, 'nut': nut_mat,
    'ws_glass': glass_mat('ws'), 'rw_glass': glass_mat('rw'), 'side_glass': glass_mat('side'),
    'headlight': lens_mat(LENS, 'head'), 'taillight': lens_mat(RED_LENS, 'tail'), 'indicator': lens_mat(AMBER, 'ind'),
    'grille': grille_mat, 'plate': plate_mat, 'under': under_mat, 'vinyl': vinyl_mat, 'carpet': carpet_mat,
    'roof': roof_mat, 'chassis': chassis_mat, 'dash': dash_mat, 'binnacle': binnacle_mat, 'bakelite': bakelite_mat, 'mirror': mirror_mat,
    'rosary': rosary_mat, 'cross': cross_mat, 'door_l': door_mat(1), 'door_r': door_mat(-1), 'wood': wood_mat,
    'antenna': antenna_mat, 'beads': beads_mat, 'paper': paper_mat, 'flap': flap_mat, 'skip': lambda ctx: None,
}


def DEFAULT_MAT(ctx):
    kind = getattr(ctx.cube, 'kind', 'paint')
    return MATS[kind](ctx)


# ------------------------------------------------------------------ emissive decals ('eyes' layer)
def glow_fill(color, edge=1, centre=None):
    def fn(img, u0, v0, w, h):
        px = img.load()
        for j in range(edge, h - edge):
            for i in range(edge, w - edge):
                c = color
                if centre is not None:
                    d = math.sqrt((i - (w - 1) / 2.0) ** 2 + (j - (h - 1) / 2.0) ** 2)
                    if d < 1.6:
                        c = centre
                px[u0 + i, v0 + j] = c
    return fn


def gauge_glow(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            for gcx in (w * 0.28, w * 0.72):
                dx, dy = i - gcx + 0.5, j - (h - 1) / 2.0
                d = math.sqrt(dx * dx + dy * dy)
                if h * 0.28 < d < h * 0.45:
                    ang = math.atan2(dy, dx)
                    if int((ang + 4) * 3) % 2 == 0:
                        px[u0 + i, v0 + j] = (150, 230, 170, 255)
                elif abs(dy - dx * 0.4) < 0.5 and d < h * 0.4 and dx < 0:
                    px[u0 + i, v0 + j] = (255, 150, 60, 255)


# ------------------------------------------------------------------ model
class AutoModel(Model):
    """Shares UVs: the four wheels are painted once (right wheels mirror the left ones' UV)."""
    shared = []   # (cube, source cube)

    def pack(self, pad=0):
        held = []
        for b in self.bones():
            keep = []
            for c in b.cubes:
                if getattr(c, 'share', None) is not None:
                    held.append((b, c))
                else:
                    keep.append(c)
            b.cubes = keep
        super().pack(pad=pad)
        for b, c in held:
            c.uv = c.share.uv
            b.cubes.append(c)
        return self


FOCUS = 'dashboard'
POSES = {
    'turn_left': {'wheel_fl': (0, -0.45, 0, 0, 0, 0), 'wheel_fr': (0, -0.45, 0, 0, 0, 0), 'steering_wheel': (0, 0, 2.2, 0, 0, 0),
                  'rosary': (0.1, 0, 0.4, 0, 0, 0)},
    'doors_open': {'door_fl': (0, 1.1, 0, 0, 0, 0), 'door_fr': (0, -1.1, 0, 0, 0, 0), 'door_rl': (0, 1.0, 0, 0, 0, 0),
                   'door_rr': (0, -1.0, 0, 0, 0, 0)},
}
ANIM_NOTES = """wheel_*: xRot += distance driven / 6 texels (forward = positive); wheel_fl/fr yRot = -steer * 0.45 (steer +1 = left).
steering_wheel: zRot = steer * 2.2. body: tiny tremble while idling. rosary: pendulum, pushed by turns and bumps.
doors/hood/trunk: hinged, closed at rest."""


def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, kind='paint', name=None, inflate=0.0, decals=None, mirror=False, **attrs):
        c = r.box(b, frm, size, inflate=inflate, decals=decals, mirror=mirror)
        c.kind = kind
        c.name = name
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    W_TOP = AXLE_Y - WHEEL_R            # top of the wheel arch
    FA0, FA1 = FRONT_AXLE - WHEEL_R, FRONT_AXLE + WHEEL_R
    RA0, RA1 = REAR_AXLE - WHEEL_R, REAR_AXLE + WHEEL_R

    # ---------------------------------------------------------------- body (shell)
    bone('body', (0, 18, 0))
    for s in (1, -1):
        x0 = 14 if s > 0 else -18
        # front wing above the wheel, the corner ahead of it, the strip behind it
        box('body', (x0, BELT, -40), (4, W_TOP - BELT, 21), 'paint', 'wing')
        box('body', (x0, W_TOP, -40), (4, 17 - W_TOP, FA0 + 40), 'paint', 'wing_nose')
        box('body', (x0, W_TOP, FA1), (4, 18 - W_TOP, -19 - FA1), 'paint', 'wing_tail')
        # rear quarter above the wheel, ahead of it, behind it
        box('body', (x0, BELT, 20), (4, W_TOP - BELT, 20), 'paint', 'quarter')
        box('body', (x0, W_TOP, 20), (4, 18 - W_TOP, RA0 - 20), 'paint', 'quarter_nose')
        box('body', (x0, W_TOP, RA1), (4, 17 - W_TOP, 40 - RA1), 'paint', 'quarter_tail')
        # B pillar between the door windows, drip rail along the roof edge
        box('body', (16 if s > 0 else -18, ROOF_BOT, 0), (2, BELT - ROOF_BOT, 2), 'paint', 'b_pillar', gaps=False)
        box('body', (17 if s > 0 else -18, ROOF_TOP + 1, -9), (1, 1, 23), 'chrome', 'drip')
    # valance + chassis between the wheels, front and rear (painted faces, dark underside)
    box('body', (-14, W_TOP, -40), (28, 18 - W_TOP, 21), 'chassis', 'front_chassis')
    box('body', (-14, W_TOP, 22), (28, 18 - W_TOP, 18), 'chassis', 'rear_chassis')
    # grille panel, headlights, indicators, bumpers, plates, exhaust
    box('body', (-17, BELT + 1, -41), (34, 4, 1), 'grille', 'grille')
    for s in (1, -1):
        box('body', (10 if s > 0 else -16, BELT + 1, -41.6), (6, 4, 1), 'headlight', 'headlight',
            decals={'eyes:front': glow_fill((255, 244, 214, 255), 1, (255, 255, 245, 255))})
        box('body', (11 if s > 0 else -16, BELT + 5, -41), (5, 1, 1), 'indicator', 'indicator')
        box('body', (12 if s > 0 else -17, BELT + 1, 40), (5, 5, 1), 'taillight', 'taillight',
            decals={'eyes:back': glow_fill((255, 40, 30, 255), 1)})
    bone('bumper_front', (0, 12, -42), 'body', rot=(0, 0, 1.6))      # bent in some old parking manoeuvre
    box('bumper_front', (-18, 11, -43), (36, 2, 2), 'chrome', 'bumper_front')
    for s in (1, -1):
        box('bumper_front', (7 if s > 0 else -9, 10, -43.6), (2, 4, 1), 'flap', 'overrider')
        box('body', (7 if s > 0 else -9, 10, 42.6), (2, 4, 1), 'flap', 'overrider_rear')
    box('body', (-18, 11, 41), (36, 2, 2), 'chrome', 'bumper_rear')
    box('body', (-4, BELT + 2, 40.2), (8, 3, 0), 'plate', 'plate')
    box('body', (-4, 13, -42.2), (8, 3, 0), 'plate', 'plate_front')
    box('body', (-11, 17, 36), (2, 1, 6), 'under', 'exhaust')
    for s in (1, -1):
        box('body', (14 if s > 0 else -18, 15, REAR_AXLE + WHEEL_R + 0.3), (4, 4, 0), 'flap', 'mud_flap')
    box('body', (-6, BELT - 1.5, 19.5), (7, 1, 2), 'paper', 'newspaper')
    # cabin floor, firewall, parcel shelf, roof
    box('body', (-16, FLOOR, -19), (32, 1, 41), 'carpet', 'floor')
    box('body', (-16, BELT + 4, -19), (32, 18 - BELT - 4, 1), 'dash', 'firewall')
    box('body', (-15, BELT - 1, 19), (30, 1, 3), 'dash', 'parcel_shelf')
    box('body', (-17, ROOF_TOP, -9), (34, 2, 23), 'roof', 'roof')
    # radio aerial on the right wing
    bone('antenna', (-16, BELT, -36), 'body', rot=(-12, 0, 0))
    box('antenna', (-16.5, BELT - 13, -36.5), (1, 13, 1), 'antenna', 'antenna')

    # bonnet and boot lids
    bone('hood', (0, BELT, -19), 'body')
    box('hood', (-14, BELT, -40), (28, W_TOP - BELT, 21), 'paint', 'hood')
    bone('trunk', (0, BELT, 22), 'body')
    box('trunk', (-14, BELT, 22), (28, W_TOP - BELT, 18), 'paint', 'trunk')

    # ---------------------------------------------------------------- doors (hinged at the front edge)
    for name, s, z0, z1 in (('door_fl', 1, -19, 1), ('door_rl', 1, 1, 20), ('door_fr', -1, -19, 1), ('door_rr', -1, 1, 20)):
        xo = 16 if s > 0 else -18
        bone(name, (17 * s, BELT, z0), 'body')
        box(name, (xo, BELT, z0), (2, 18 - BELT, z1 - z0), 'door_l' if s > 0 else 'door_r', 'door', zc=(z0 + z1) / 2.0)
        gx = 17 if s > 0 else -17
        gh = BELT - ROOF_BOT
        if name.startswith('door_f'):
            # stepped at the front to follow the raked A pillar
            box(name, (gx, ROOF_BOT, -9), (0, gh, 9), 'side_glass', 'glass')
            box(name, (gx, ROOF_BOT + 4, -13), (0, gh - 4, 4), 'side_glass', 'glass')
            box(name, (gx, ROOF_BOT + 8, -16), (0, gh - 8, 3), 'side_glass', 'glass')
        else:
            box(name, (gx, ROOF_BOT, 2), (0, gh, 12), 'side_glass', 'glass')
            box(name, (gx, ROOF_BOT + 6, 14), (0, gh - 6, 4), 'side_glass', 'glass')
        hz = z1 - 4 if name.startswith('door_f') else z1 - 5
        box(name, (17.6 if s > 0 else -18.6, BELT + 2, hz), (1, 1, 3), 'chrome', 'handle')
    # the driver's door mirror
    box('door_fl', (18, BELT - 1, -17), (1, 1, 1), 'chrome', 'mirror_arm')
    box('door_fl', (18.5, BELT - 3, -17.5), (2, 2, 2), 'chrome', 'mirror_head')

    # ---------------------------------------------------------------- greenhouse
    bone('windshield', WS_PIVOT, 'body', rot=(WS_RAKE, 0, 0))
    box('windshield', (-16, BELT - WS_LEN, -18), (32, WS_LEN, 0), 'ws_glass', 'ws')
    box('windshield', (-13, BELT - 2, -18.6), (11, 1, 1), 'bakelite', 'wiper')
    box('windshield', (1, BELT - 2, -18.6), (11, 1, 1), 'bakelite', 'wiper')
    bone('a_pillars', WS_PIVOT, 'body', rot=(WS_RAKE, 0, 0))
    for s in (1, -1):
        box('a_pillars', (15 if s > 0 else -18, BELT - WS_LEN - 1, -19), (3, WS_LEN + 1, 2), 'paint', 'a_pillar', gaps=False)
    bone('rear_window', RW_PIVOT, 'body', rot=(RW_RAKE, 0, 0))
    box('rear_window', (-15, BELT - RW_LEN, 22), (30, RW_LEN, 0), 'rw_glass', 'rw')
    bone('c_pillars', RW_PIVOT, 'body', rot=(RW_RAKE, 0, 0))
    for s in (1, -1):
        box('c_pillars', (15 if s > 0 else -18, BELT - RW_LEN - 1, 16), (3, RW_LEN + 1, 6), 'paint', 'c_pillar', gaps=False)

    # ---------------------------------------------------------------- interior
    bone('dashboard', (0, BELT, -16), 'body')
    box('dashboard', (-16, BELT, -18), (32, 4, 5), 'dash', 'dash')
    box('dashboard', (4, BELT - 1, -14), (10, 3, 2), 'binnacle', 'binnacle', decals={'eyes:back': gauge_glow})
    box('dashboard', (-1, 11, -11), (1, 6, 1), 'chrome', 'gear_lever')
    box('dashboard', (-1.5, 10, -11.5), (2, 2, 2), 'bakelite', 'gear_knob')
    # steering: the column tilts toward the driver, the wheel turns about the column (zRot)
    wy = 6.0
    bone('steering_column', (8.5, wy, -9), 'dashboard', rot=(25, 0, 0))
    box('steering_column', (7.5, wy - 1, -14), (2, 2, 5), 'bakelite', 'column')
    bone('steering_wheel', (8.5, wy, -9), 'steering_column')
    box('steering_wheel', (4.5, wy - 5, -9.5), (8, 1, 1), 'bakelite', 'rim_top')
    box('steering_wheel', (4.5, wy + 4, -9.5), (8, 1, 1), 'bakelite', 'rim_bottom')
    box('steering_wheel', (3.5, wy - 4, -9.5), (1, 8, 1), 'bakelite', 'rim_left')
    box('steering_wheel', (12.5, wy - 4, -9.5), (1, 8, 1), 'bakelite', 'rim_right')
    box('steering_wheel', (4.5, wy - 0.5, -9.3), (8, 1, 0), 'bakelite', 'spoke')
    box('steering_wheel', (7.5, wy - 1, -10), (2, 2, 1), 'chrome', 'horn_button')
    # sun visors
    for s in (1, -1):
        box('body', (2 if s > 0 else -15, ROOF_BOT, -9), (13, 1, 5), 'roof', 'visor', gaps=False)
    # front seats: cushions + reclined backs; rear bench
    for name, s in (('seat_fl', 1), ('seat_fr', -1)):
        x0 = 3 if s > 0 else -14
        bone(name, (8.5 * s, 16, 1), 'body')
        box(name, (x0, 16, -8), (11, 2, 9), 'vinyl', 'cushion')
        bone(name + '_back', (8.5 * s, 16, 1), name, rot=(-9, 0, 0))
        box(name + '_back', (x0, 1, 0.5), (11, 15, 3), 'beads' if s > 0 else 'vinyl', 'back')
    bone('bench', (0, 16, 18.5), 'body')
    box('bench', (-15, 16, 8), (30, 2, 11), 'vinyl', 'bench')
    bone('bench_back', (0, 16, 18.5), 'bench', rot=(-10, 0, 0))
    box('bench_back', (-15, 2, 18.5), (30, 14, 3), 'vinyl', 'bench_back')

    # rear-view mirror and the rosary hanging from it
    bone('mirror', (0, ROOF_BOT, -9), 'body')
    box('mirror', (-0.5, ROOF_BOT, -9.5), (1, 2, 1), 'bakelite', 'stem')
    box('mirror', (-3.5, -4.5, -10), (7, 2, 1), 'mirror', 'mirror')
    bone('rosary', (0, -2.5, -9.5), 'mirror')
    box('rosary', (-2, -2.5, -9.5), (4, 7, 0), 'rosary', 'beads')
    box('rosary', (0, -2.5, -11.5), (0, 7, 4), 'rosary', 'beads_side')
    box('rosary', (-0.5, 4.5, -10), (1, 3, 1), 'cross', 'cross')
    box('rosary', (-1.5, 5.2, -10.2), (3, 1, 0), 'cross', 'cross_bar')

    # ---------------------------------------------------------------- wheels (roots at the axles)
    src = {}
    R = WHEEL_R
    for name, s, az in (('wheel_fl', 1, FRONT_AXLE), ('wheel_rl', 1, REAR_AXLE), ('wheel_fr', -1, FRONT_AXLE), ('wheel_rr', -1, REAR_AXLE)):
        bone(name, (16 * s, AXLE_Y, az))
        x0 = 14 if s > 0 else -18
        parts = [
            ((x0, AXLE_Y - R, az - R + 2), (4, 2 * R, 2 * R - 4), 'rubber', 'tyre_a'),
            ((x0, AXLE_Y - R + 2, az - R), (4, 2 * R - 4, 2 * R), 'rubber', 'tyre_b'),
            ((x0, AXLE_Y - R + 1, az - R + 1), (4, 2 * R - 2, 2 * R - 2), 'rubber', 'tyre_c', -0.05),
            ((17.3 if s > 0 else -18.3, AXLE_Y - 4, az - 4), (1, 8, 8), 'hubcap', 'hubcap'),
            ((17.8 if s > 0 else -18.8, AXLE_Y - 1, az - 1), (1, 2, 2), 'nut', 'nut'),
        ]
        for k, part in enumerate(parts):
            frm, size, kind, nm = part[:4]
            inf = part[4] if len(part) > 4 else 0.0
            if name == 'wheel_fl':
                src[k] = box(name, frm, size, kind, nm, inflate=inf)
            else:
                # painted once (wheel_fl): the others reuse its UV, the right side mirrored
                box(name, frm, size, 'skip', nm, inflate=inf, mirror=s < 0, share=src[k])

    m = AutoModel('auto', 256, 256, r.roots)
    m.scale = 1.0
    return m
