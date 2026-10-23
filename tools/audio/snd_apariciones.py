# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "apariciones" (B3): what the Casa Morales SHOWS you (docs/design/casa_terror.md 5, events
33-45), the dog that watches the house and the long dog. Nobody speaks: breaths, nails, cloth, bones, presence.

Run from the repo root:  python3 tools/audio/snd_apariciones.py [substring ...]

  aparicion.sombra_paso (2)   the tall shadow crossing a doorway: a heavy barefoot step on old boards, the floor's
                              creak, a dry cloth drag.
  aparicion.nona_respira (2)  an old woman's breath, wet and whistling in the throat, a rattle at the bottom (the Nona
                              at the end of the hall / outside the window).
  aparicion.vidrio_unas       nails on the window glass: three slow taps that ring in the pane, then a long scrape.
  aparicion.perro_respira (2) the dog standing on two legs breathes like a person: slow, deep, through a dog's nose.
  aparicion.espejo            the mirror hums: inharmonic glass partials beating, swelling out of nothing, and a cold
                              reversed breath.
  aparicion.aliento           a breath on the back of your neck, right at the ear: dry lips, a little voice fry.
  aparicion.mano_rasguno (2)  fingernails dragged over floorboards under the bed, knuckles knocking.
  aparicion.mano_retira       the arm yanked back under the bed: a fast drag of skin on wood and a thump.
  aparicion.cuello (2)        a neck turning too far: a slow cartilage creak with cracks in it.
  aparicion.copia             the copy's smile: wet lips peeling back off the gums, teeth grinding.
  aparicion.techo_corre       something runs across the ceiling: hands and feet on plaster, fast, plaster dust.
  aparicion.ofelia            porcelain: a small click as the doll settles, one detuned music-box note far away.
  aparicion.sabana            a sheet fills with wind and flies: flapping cloth, a rising rush, a soft empty flop.
  aparicion.visitante         a presence in the dark: a sub-bass swell and a very long, slow exhale.
  perro_largo.reptar          many hands running: palms and nails on the floor, too many, too fast (1.5 s, chained).
  perro_largo.retrae          the long body pulled back into the doghouse: a wet slither, bones clicking, a thump.
  perro_largo.respira         huge panting from inside the doghouse: a big chest, a cavity that rings.

Positional sounds: mono. Stingers peak -0.5 dBFS, breaths -1 dBFS, foley -3 dBFS. Review: spectrogram PNG per file in
<work>/audio/apariciones (+ stats.json).
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import json
import os
import sys
import time

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/apariciones'))


# ------------------------------------------------------------------ basics
def N(sec):
    return max(1, int(round(sec * SR)))


def R(seed):
    return np.random.default_rng(seed)


def white(n, seed):
    return R(seed).standard_normal(n).astype(np.float32)


def env(n, pts):
    return dsp.env_points(n, pts)


def add(buf, x, t):
    s = N(t) if t > 0 else 0
    if s >= len(buf):
        return buf
    seg = x[:len(buf) - s]
    buf[s:s + len(seg)] += seg
    return buf


def sumpad(*xs):
    n = max(len(x) for x in xs)
    out = np.zeros(n, np.float32)
    for x in xs:
        out[:len(x)] += x
    return out


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


def modal(exc, modes, seed=0):
    """Excite a bank of decaying resonances (f Hz, decay s, gain)."""
    n = len(exc)
    out = np.zeros(n, np.float32)
    for f, d, g in modes:
        r = np.exp(-1.0 / (max(d, 1e-3) * SR))
        w = 2 * np.pi * f / SR
        b = [g * (1 - r)]
        a = [1, -2 * r * np.cos(w), r * r]
        out += signal.lfilter(b, a, exc).astype(np.float32)
    return out


def click(seed, dur=0.004, hp=1500.0):
    n = N(dur)
    x = white(n, seed) * np.exp(-np.arange(n) / (n * 0.25))
    return dsp.highpass(x.astype(np.float32), hp, 2)


def thump(f0, dur, seed, amp=1.0):
    n = N(dur)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * (6.0 / dur)) * amp
    x += dsp.lowpass(white(n, seed), 300, 2) * np.exp(-t * 60) * 0.5 * amp
    return x.astype(np.float32)


def breath(dur, seed, lo=500.0, hi=3200.0, shape=((0, 0), (0.25, 1), (0.7, 0.8), (1, 0)), formants=(800, 1300, 2500), fry=0.0,
           fry_hz=38.0, wet=0.0):
    """Air through a throat: noise through a few resonances, an envelope, optional vocal fry and wet crackle."""
    n = N(dur)
    x = dsp.lowpass(bp(white(n, seed), lo, hi, 2), hi, 4)
    x = x * 0.22 + dsp.formant(x, (formants,), 6.0) * 1.0
    e = env(n, list(shape))
    y = x * e
    if fry:
        t = np.arange(n) / SR
        jit = 1 + 0.08 * dsp.lowpass(white(n, seed + 1), 6, 1) * 40
        ph = 2 * np.pi * np.cumsum(fry_hz * jit) / SR
        pulses = np.maximum(0, np.sin(ph)) ** 12
        y += bp(pulses.astype(np.float32) * white(n, seed + 2) * 0.6 + pulses.astype(np.float32), 200, 2400) * e * fry
    if wet:
        r = R(seed + 3)
        k = int(dur * 40 * wet)
        for _ in range(k):
            pos = r.random() * dur * 0.95
            c = dsp.lowpass(click(seed + 7 + _, 0.0025, 700), 3200, 2) * (0.3 + r.random() * 0.7)
            add(y, c * env(len(c), [(0, 1), (1, 1)]) * wet * float(e[min(n - 1, N(pos))] + 0.15), pos)
    return y.astype(np.float32)


def scrape(dur, seed, f_lo=1800.0, f_hi=5200.0, rate=(30, 70), amp_pts=((0, 0), (0.1, 1), (0.8, 0.8), (1, 0))):
    """Stick-slip friction: grains of squeal + grit at a wandering rate."""
    n = N(dur)
    r = R(seed)
    out = np.zeros(n, np.float32)
    t = 0.0
    while t < dur:
        g = click(seed + int(t * 1000), 0.006 + r.random() * 0.01, f_lo)
        g = bp(g, f_lo, f_hi)
        add(out, g * (0.4 + r.random()), t)
        t += 1.0 / (rate[0] + r.random() * (rate[1] - rate[0]))
    grit = bp(white(n, seed + 99), f_lo * 0.8, f_hi * 1.2) * 0.25
    squeal = np.sin(2 * np.pi * np.cumsum(f_lo * 1.4 * (1 + 0.03 * np.sin(np.arange(n) / SR * 2 * np.pi * 7))) / SR) * 0.08
    y = (out + grit + squeal) * env(n, list(amp_pts))
    return y.astype(np.float32)


def room(x, decay=0.9, wet=0.22, damp=4500.0, seed=7):
    return dsp.reverb(x, decay, wet, damp, 0.012, seed)


# ------------------------------------------------------------------ the sounds
def sombra_paso(v):
    seed = 100 + v * 17
    dur = 1.3
    out = np.zeros(N(dur), np.float32)
    # the heavy bare step: heel then ball, the board flexing under it
    add(out, thump(58 + v * 6, 0.45, seed, 1.0), 0.02)
    add(out, thump(75, 0.25, seed + 1, 0.45), 0.11)
    creak = modal(dsp.lowpass(white(N(0.5), seed + 2), 1200, 2) * env(N(0.5), [(0, 0), (0.1, 1), (1, 0)]),
                  [(210 + v * 15, 0.25, 1.0), (340, 0.2, 0.7), (520, 0.15, 0.5), (780, 0.1, 0.3)])
    creak = creak / (np.max(np.abs(creak)) + 1e-9)
    add(out, creak * 0.55, 0.06)
    # a dry cloth drag over the boards (the coat brushing the jamb): dark, under the step
    n = N(0.7)
    drag = dsp.lowpass(bp(white(n, seed + 3), 300, 2500), 1800, 4) * env(n, [(0, 0), (0.2, 0.6), (0.6, 0.4), (1, 0)])
    add(out, drag * 0.18, 0.2)
    return room(out, 1.1, 0.25)


def nona_respira(v):
    seed = 200 + v * 31
    dur = 3.4 if v == 0 else 4.2
    n = N(dur)
    out = np.zeros(n, np.float32)
    # in through the mouth (whistling in the throat), a stop, out with a rattle
    inh = breath(1.1, seed, 900, 4200, ((0, 0), (0.6, 1), (0.9, 0.9), (1, 0)), (1100, 1900, 2900), wet=0.4)
    t = np.arange(len(inh)) / SR
    whistle = np.sin(2 * np.pi * np.cumsum(2300 + 180 * np.sin(2 * np.pi * 3.3 * t)) / SR) * env(len(inh), [(0, 0), (0.5, 0.25), (0.95, 0.4), (1, 0)])
    add(out, inh + whistle.astype(np.float32) * 0.18, 0.05)
    exh = breath(1.8 if v == 0 else 2.4, seed + 5, 300, 2600, ((0, 0), (0.08, 1), (0.6, 0.5), (1, 0)), (600, 1050, 2300),
                 fry=0.55, fry_hz=33.0, wet=1.0)
    add(out, exh * 0.9, 1.35)
    if v == 1:
        # a click of the dentures at the end
        add(out, modal(click(seed + 9, 0.003, 2000), [(2600, 0.04, 1), (3900, 0.03, 0.6)]) * 0.6, 3.85)
    return room(out, 0.7, 0.18)


def vidrio_unas():
    seed = 300
    dur = 4.6
    out = np.zeros(N(dur), np.float32)
    glass = [(1750, 0.5, 1.0), (2630, 0.35, 0.7), (3910, 0.25, 0.5), (5480, 0.15, 0.35), (980, 0.4, 0.4)]
    for k, t0 in enumerate((0.1, 0.85, 1.6)):
        tap = sumpad(click(seed + k, 0.002, 1200), dsp.lowpass(click(seed + 10 + k, 0.004, 100), 900, 2) * 0.6)
        ring = modal(np.pad(tap, (0, N(0.6))), glass)
        ring = ring / (np.max(np.abs(ring)) + 1e-9)
        add(out, (ring + np.pad(tap, (0, len(ring) - len(tap))) * 0.5) * (0.9 + 0.05 * k), t0)
    # the long scrape down the pane, slow, catching
    sc = scrape(2.3, seed + 5, 2200, 6500, (18, 45), ((0, 0), (0.08, 0.9), (0.5, 1.0), (0.85, 0.6), (1, 0)))
    sc = dsp.lowpass(sc, 6500, 4)
    sr = modal(sc, [(2630, 0.08, 0.6), (3910, 0.06, 0.5)])
    sr = sr / (np.max(np.abs(sr)) + 1e-9)
    add(out, (sr * 0.5 + sc / (np.max(np.abs(sc)) + 1e-9) * 0.2) * 0.6, 2.2)
    return room(out, 0.6, 0.12, 6000)


def perro_respira(v):
    seed = 400 + v * 11
    dur = 4.0
    out = np.zeros(N(dur), np.float32)
    # slow and deep, like a man asleep -- but through a dog's nose (narrow, snorting) and with a growl under it
    for k, t0 in enumerate((0.05, 2.0)):
        inh = breath(1.2, seed + k * 7, 1200, 5200, ((0, 0), (0.7, 1), (1, 0)), (1800, 2900, 4100))
        exh = breath(0.75, seed + k * 7 + 3, 500, 3000, ((0, 0), (0.1, 1), (1, 0)), (700, 1400, 2400), fry=0.35, fry_hz=52 - v * 8)
        add(out, inh * 0.8, t0)
        add(out, exh, t0 + 1.25)
        # a wet snort at the turn
        add(out, bp(white(N(0.07), seed + k), 400, 2400) * env(N(0.07), [(0, 0), (0.2, 1), (1, 0)]) * 0.5, t0 + 1.2)
    n = N(dur)
    t = np.arange(n) / SR
    growl = np.sin(2 * np.pi * np.cumsum(68 + 6 * np.sin(2 * np.pi * 0.7 * t)) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) ** 2
    out += dsp.lowpass(growl.astype(np.float32), 400, 2) * 0.12 * env(n, [(0, 0), (0.2, 1), (0.9, 1), (1, 0)])
    return room(out, 0.5, 0.1)


def espejo():
    seed = 500
    dur = 3.8
    n = N(dur)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    # inharmonic glass partials, each pair a few Hz apart so they beat; out of nothing to a hum and away
    for k, (f, g) in enumerate([(1137, 1.0), (1891, 0.7), (2643, 0.55), (3517, 0.4), (4729, 0.25)]):
        beat = 2.1 + k * 0.9
        out += (np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * (f + beat) * t + k)).astype(np.float32) * g * 0.5
    out *= env(n, [(0, 0), (0.35, 0.6), (0.6, 1.0), (0.85, 0.3), (1, 0)])
    # a cold breath, reversed, swelling into the hum
    br = breath(1.6, seed + 3, 600, 4500, ((0, 0), (0.1, 1), (1, 0)), (900, 1500, 2700), fry=0.2)
    rb = dsp.reverse(room(br, 1.4, 0.6, 3000))[:N(2.2)]
    add(out, rb * 1.4, 0.4)
    return room(out, 1.8, 0.3, 6000)


def aliento():
    seed = 600
    dur = 1.9
    out = np.zeros(N(dur), np.float32)
    # a soft wet click of the lips parting, a short inhale, then the exhale right at your ear
    add(out, click(seed, 0.003, 1500) * 0.3, 0.02)
    add(out, breath(0.45, seed + 1, 1400, 6000, ((0, 0), (0.7, 1), (1, 0)), (2000, 3200, 4500)) * 0.45, 0.05)
    ex = breath(1.2, seed + 2, 250, 5000, ((0, 0), (0.06, 1), (0.5, 0.55), (1, 0)), (500, 1100, 2600), fry=0.3, fry_hz=40.0)
    # proximity: lots of low end, nothing of a room
    ex = ex + dsp.lowpass(ex, 300, 2) * 1.5
    add(out, ex, 0.55)
    return out


def mano_rasguno(v):
    seed = 700 + v * 13
    dur = 2.4 if v == 0 else 1.6
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = R(seed)
    t0 = 0.05
    while t0 < dur - 0.3:
        stroke = 0.18 + r.random() * 0.3
        sc = scrape(stroke, seed + int(t0 * 100), 1600 + r.random() * 600, 5500, (40, 90), ((0, 0), (0.15, 1), (0.8, 0.7), (1, 0)))
        add(out, modal(sc, [(380, 0.06, 0.4), (610, 0.05, 0.3)]) * 0.5 + sc, t0)
        if r.random() < 0.5:
            add(out, thump(160 + r.random() * 60, 0.12, seed + int(t0 * 50), 0.35), t0)
        t0 += stroke + 0.05 + r.random() * 0.25
    return room(out, 0.4, 0.12)


def mano_retira():
    seed = 800
    dur = 1.1
    n = N(dur)
    out = np.zeros(n, np.float32)
    # skin dragged fast over the boards: a rising-then-falling friction swish, nails clicking
    m = N(0.38)
    drag = bp(white(m, seed), 500, 3000) * env(m, [(0, 0), (0.15, 1), (0.8, 0.8), (1, 0)])
    drag = dsp.sweep_lowpass(drag, 4000, 900)
    add(out, drag * 1.2, 0.02)
    for k in range(5):
        add(out, click(seed + k, 0.002, 2500) * 0.4, 0.04 + k * 0.05)
    add(out, thump(70, 0.5, seed + 9, 1.0), 0.38)
    return room(out, 0.5, 0.15)


def cuello(v):
    seed = 900 + v * 19
    dur = 1.7 if v == 0 else 1.2
    n = N(dur)
    out = np.zeros(n, np.float32)
    # the slow creak: stick-slip pulses through the throat's resonances (a door hinge made of cartilage)
    r = R(seed)
    t = 0.05
    rate = 26.0
    while t < dur - 0.25:
        p = click(seed + int(t * 1000), 0.004, 60)
        add(out, modal(np.pad(p, (0, N(0.05))), [(95 + v * 10, 0.03, 1.0), (240, 0.025, 0.6), (510, 0.015, 0.4)]) * (0.5 + r.random() * 0.5), t)
        rate = max(9.0, rate * (0.97 + r.random() * 0.04))
        t += 1.0 / rate
    out *= env(n, [(0, 0), (0.1, 1), (0.8, 0.9), (1, 0)])
    # the cracks
    for k, tc in enumerate((0.45, 0.9) if v == 0 else (0.3,)):
        cr = modal(sumpad(click(seed + 50 + k, 0.003, 800), click(seed + 60 + k, 0.002, 1500) * 0.6),
                   [(1300, 0.02, 1.0), (2100, 0.015, 0.7), (380, 0.04, 0.6)])
        add(out, cr * 1.8, tc)
    return room(out, 0.4, 0.1)


def copia():
    seed = 1000
    dur = 2.2
    n = N(dur)
    out = np.zeros(n, np.float32)
    # wet lips peeling back off the gums: sticky crackle that spreads
    r = R(seed)
    for k in range(70):
        tt = 0.05 + (k / 70.0) ** 0.8 * 0.9 + r.random() * 0.02
        c = bp(click(seed + k, 0.0035, 300), 600, 4000) * (0.25 + r.random() * 0.6)
        add(out, c, tt)
    # teeth grinding: slow, gritty, enamel on enamel
    gr = scrape(1.1, seed + 5, 2600, 8000, (55, 110), ((0, 0), (0.2, 1), (0.8, 1), (1, 0)))
    add(out, modal(gr, [(3300, 0.02, 0.5), (4800, 0.015, 0.4)]) + gr * 0.6, 0.95)
    # an exhale through the clenched teeth
    add(out, breath(0.9, seed + 9, 2500, 8000, ((0, 0), (0.1, 1), (1, 0)), (3500, 5200, 6800)) * 0.25, 1.2)
    return room(out, 0.4, 0.12)


def techo_corre():
    seed = 1100
    dur = 2.4
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = R(seed)
    t = 0.05
    while t < dur - 0.3:
        hard = r.random()
        hit = thump(120 + r.random() * 90, 0.08, seed + int(t * 997), 0.6 + 0.4 * hard)
        add(out, hit, t)
        # plaster: a tick of nails, crumbs falling after
        add(out, click(seed + int(t * 331), 0.0025, 1800) * 0.35 * hard, t + 0.004)
        if r.random() < 0.25:
            crumbs = bp(white(N(0.25), seed + int(t * 77)), 2500, 9000) * env(N(0.25), [(0, 0), (0.1, 1), (1, 0)]) * 0.08
            add(out, crumbs, t + 0.05)
        speed = 13 + 6 * np.sin(t * 3.0)
        t += 1.0 / speed * (0.6 + r.random() * 0.8)
    out *= env(n, [(0, 0.2), (0.1, 1), (0.75, 1), (1, 0)])
    # from above, through the ceiling: muffled body
    out = dsp.lowpass(out, 3500, 2) + out * 0.25
    return room(out, 0.8, 0.25, 3500)


def ofelia():
    seed = 1200
    dur = 2.6
    n = N(dur)
    out = np.zeros(n, np.float32)
    # the porcelain settling: a tiny ceramic tick, then another, smaller
    for k, t0 in enumerate((0.03, 0.21)):
        tick = modal(click(seed + k, 0.0018, 2500), [(3820, 0.05, 1.0), (5310, 0.04, 0.7), (7240, 0.03, 0.4)])
        add(out, tick * (1.0 - 0.45 * k), t0)
    # one music-box note far away, detuned, out of a dead mechanism
    m = N(2.0)
    t = np.arange(m) / SR
    f = 1046.5 * 0.985
    note = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) + 0.18 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 2.2)
    note = dsp.lowpass(note.astype(np.float32), 4000, 2)
    add(out, room(note, 1.6, 0.5, 3000)[:m] * 0.3, 0.55)
    return out


def sabana():
    seed = 1300
    dur = 3.2
    n = N(dur)
    t = np.arange(n) / SR
    # cloth flapping: noise chopped by a wind that speeds up as it fills, then the rush of the throw
    flap_rate = np.interp(t, [0, 1.0, 1.8, 2.4], [5, 9, 14, 3])
    ph = 2 * np.pi * np.cumsum(flap_rate) / SR
    chop = (0.5 + 0.5 * np.sin(ph)) ** 6
    cloth = bp(white(n, seed), 300, 4500) * chop.astype(np.float32)
    rush = dsp.sweep_lowpass(bp(white(n, seed + 1), 200, 8000), 700, 6000) * env(n, [(0, 0), (0.3, 0.2), (0.65, 1.0), (0.78, 0.3), (1, 0)])
    out = cloth * env(n, [(0, 0), (0.1, 0.6), (0.6, 1.0), (0.76, 0.2), (1, 0)]) + rush * 0.6
    # empty: the soft flop on the grass
    flop = sumpad(thump(90, 0.35, seed + 3, 0.5), bp(white(N(0.3), seed + 4), 300, 2000) * env(N(0.3), [(0, 0), (0.05, 1), (1, 0)]) * 0.4)
    add(out, flop, 2.5)
    return out


def visitante():
    seed = 1400
    dur = 5.0
    n = N(dur)
    t = np.arange(n) / SR
    # a pressure you feel more than hear
    sub = np.sin(2 * np.pi * np.cumsum(34 + 3 * np.sin(2 * np.pi * 0.13 * t)) / SR) + 0.4 * np.sin(2 * np.pi * 51 * t + 1)
    sub = sub.astype(np.float32) * env(n, [(0, 0), (0.35, 1), (0.8, 0.9), (1, 0)])
    # a very long, slow exhale from something with a much bigger chest
    ex = breath(3.6, seed + 1, 150, 1800, ((0, 0), (0.15, 0.8), (0.7, 0.6), (1, 0)), (320, 700, 1500), fry=0.6, fry_hz=24.0)
    out = sub * 0.8
    add(out, ex * 0.9, 0.9)
    return room(out, 2.2, 0.3, 2500)


def reptar():
    seed = 1500
    dur = 1.5
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = R(seed)
    # six hands and two dog paws: dense, uneven, palms slapping, nails ticking
    for k in range(int(dur * 44)):
        tt = r.random() * (dur - 0.1)
        if r.random() < 0.7:
            add(out, thump(140 + r.random() * 120, 0.06, seed + k, 0.5 + r.random() * 0.6), tt)
        add(out, dsp.lowpass(click(seed + 100 + k, 0.002, 1500), 5500, 2) * (0.15 + r.random() * 0.3), tt + 0.003)
    # a slithering under it
    out += bp(white(n, seed + 5), 300, 2500) * 0.08
    out *= env(n, [(0, 0.6), (0.05, 1), (0.95, 1), (1, 0.6)])
    return room(out, 0.5, 0.12)


def retrae():
    seed = 1600
    dur = 3.0
    n = N(dur)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    # the wet slither, fast and accelerating, like a hose sucked back
    sl = bp(white(n, seed), 200, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 2.5], [6, 22])) / SR)).astype(np.float32)
    sl *= env(n, [(0, 0), (0.05, 1), (0.8, 1), (0.85, 0.2), (1, 0)])
    out += dsp.sweep_lowpass(sl, 2500, 900) * 0.8
    # squelches and bone clicks, closer together as it goes
    r = R(seed)
    tt = 0.1
    gap = 0.22
    while tt < 2.4:
        add(out, modal(click(seed + int(tt * 999), 0.003, 900), [(1200, 0.02, 1), (2400, 0.015, 0.5), (420, 0.03, 0.6)]) * 0.9, tt)
        if r.random() < 0.6:
            m = N(0.12)
            sq = bp(white(m, seed + int(tt * 13)), 250, 1400) * env(m, [(0, 0), (0.2, 1), (1, 0)])
            add(out, sq * 0.6, tt + 0.02)
        gap = max(0.05, gap * 0.9)
        tt += gap * (0.7 + r.random() * 0.6)
    # inside: a hollow thump in the doghouse
    hollow = modal(thump(65, 0.4, seed + 9, 1.0), [(180, 0.15, 0.6), (310, 0.1, 0.4)])
    add(out, sumpad(thump(65, 0.5, seed + 8, 1.0), hollow * 0.4), 2.45)
    return room(out, 0.6, 0.15)


def respira_grande():
    seed = 1700
    dur = 4.0
    n = N(dur)
    out = np.zeros(n, np.float32)
    # a dog's pant, slowed to the size of something huge: in-out-in-out with a ringing wooden cavity around it
    t0 = 0.05
    k = 0
    while t0 < dur - 0.6:
        inh = breath(0.32, seed + k, 250, 2400, ((0, 0), (0.5, 1), (1, 0)), (420, 900, 1700))
        exh = breath(0.42, seed + k + 1, 200, 2000, ((0, 0), (0.15, 1), (1, 0)), (380, 760, 1500), fry=0.5, fry_hz=30.0)
        add(out, inh * 0.7, t0)
        add(out, exh, t0 + 0.34)
        t0 += 0.86 + (k % 3) * 0.05
        k += 2
    out = out + modal(out * 0.3, [(140, 0.12, 0.6), (233, 0.09, 0.5), (377, 0.07, 0.3)])
    return room(out, 0.5, 0.2, 2500)


# ------------------------------------------------------------------ table + build
# event -> (variant renderers, peak dBFS)
EVENTS = {
    'aparicion.sombra_paso': ([lambda: sombra_paso(0), lambda: sombra_paso(1)], -3.0),
    'aparicion.nona_respira': ([lambda: nona_respira(0), lambda: nona_respira(1)], -1.0),
    'aparicion.vidrio_unas': ([vidrio_unas], -2.0),
    'aparicion.perro_respira': ([lambda: perro_respira(0), lambda: perro_respira(1)], -1.0),
    'aparicion.espejo': ([espejo], -2.0),
    'aparicion.aliento': ([aliento], -1.0),
    'aparicion.mano_rasguno': ([lambda: mano_rasguno(0), lambda: mano_rasguno(1)], -3.0),
    'aparicion.mano_retira': ([mano_retira], -2.0),
    'aparicion.cuello': ([lambda: cuello(0), lambda: cuello(1)], -1.5),
    'aparicion.copia': ([copia], -2.0),
    'aparicion.techo_corre': ([techo_corre], -1.0),
    'aparicion.ofelia': ([ofelia], -3.0),
    'aparicion.sabana': ([sabana], -2.0),
    'aparicion.visitante': ([visitante], -1.0),
    'perro_largo.reptar': ([reptar], -2.0),
    'perro_largo.retrae': ([retrae], -1.0),
    'perro_largo.respira': ([respira_grande], -1.0),
}


def rel_paths(name):
    n = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if n > 1 else '') for i in range(n)]


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    report = {}
    for name, (fns, pk) in EVENTS.items():
        rels = rel_paths(name)
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        assert not SOUNDS[name][3], f'{name}: no streams here'
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            raw = np.asarray(fn(), np.float32)
            assert raw.ndim == 1, rel + ' is positional: must be mono'
            x = dsp.master(dsp.trim(raw, -62.0, 0.08), pk)
            dsp.save_ogg(x, rel)
            st = dsp.analyse(x)
            report[rel] = st
            dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            print(f'{rel:32s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    sp = os.path.join(REVIEW_DIR, 'stats.json')
    old = json.load(open(sp)) if os.path.exists(sp) else {}
    old.update(report)
    with open(sp, 'w') as fh:
        json.dump(old, fh, indent=1)
    missing = [rel for name in EVENTS for rel in rel_paths(name) if not os.path.exists(os.path.join(dsp.OUT, rel + '.ogg'))]
    if missing:
        print('MISSING:', missing)
    print(f'apariciones group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
