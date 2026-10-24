# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "sangre" (B1b): blood, body, the phone and the papers of the Casa Morales
(docs/design/casa_terror.md 5, events 46-54; 2, the lore documents). Nobody speaks: drops, slaps, breaths, paper.

Run from the repo root:  python3 tools/audio/snd_sangre.py [substring ...]

  sangre.gota (3)          a thick drop landing in a pool of blood: a dark bubble-plip and a soft wet tick.
  sangre.escribe           a wet finger dragged over plaster: three slow squelching strokes, very close to silence.
  sangre.revela            the writing is THERE: a low bowed swell that tears upwards and a single heavy heartbeat.
  sangre.mano_vidrio (3)   a wet palm slapped on a window from outside: skin, the pane ringing, the frame's knock.
  sangre.arrastre          the hand sliding down the glass: squeaking skin, a wet smear, slower and slower.
  sangre.pisada (3)        a bare wet foot on old boards: heel, the sole's slap, the skin peeling off the floor.
  sangre.burbujea          a bathtub of thick blood bubbling: slow deep gloops over a gurgling bed.
  sangre.hunde             something heavy going under in thick liquid, its last bubbles, then the drain sucking.
  sangre.dientes           teeth rattling in a wooden drawer: small hard clicks shaken like dice.
  sangre.cajon             an old wooden drawer dragged open, stick-slip, the stop at the end.
  sangre.respira (2)       something breathing at your ear in the dark: slow, wet, a click in the throat.
  linterna.muere           the flashlight dying: an electric fizz, the filament's ping, a last crackle.
  celular.obturador        a phone camera's shutter, a few steps behind you.
  lore.papel (2)           old paper handled: a dry crinkle and the soft flap of a page.

Positional sounds: mono. Stinger -1 dBFS, breaths -2, foley -3. Review: spectrogram PNG per file in
<work>/audio/sangre (+ stats.json).
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

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/sangre'))


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


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


def modal(exc, modes):
    """A bank of decaying resonances (f Hz, decay s, gain) excited by exc."""
    out = np.zeros(len(exc), np.float32)
    for f, d, g in modes:
        r = np.exp(-1.0 / (max(d, 1e-3) * SR))
        w = 2 * np.pi * f / SR
        out += signal.lfilter([g * (1 - r)], [1, -2 * r * np.cos(w), r * r], exc).astype(np.float32)
    return out


def click(seed, dur=0.004, hp=1500.0):
    n = N(dur)
    x = white(n, seed) * np.exp(-np.arange(n) / (n * 0.25))
    return dsp.highpass(x.astype(np.float32), hp, 2)


def thump(f0, dur, seed, amp=1.0):
    n = N(dur)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 30))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (6.0 / dur)) * amp
    x += dsp.lowpass(white(n, seed), 300, 2) * np.exp(-t * 60) * 0.5 * amp
    return x.astype(np.float32)


def bubble(f0, f1, dur, seed, amp=1.0):
    """A bubble resonance: a sine whose pitch rises as it closes, a quick decay, a breath of noise."""
    n = N(dur)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (1 - np.exp(-t / (dur * 0.35)))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (5.0 / dur))
    x[:N(0.002)] *= np.linspace(0, 1, N(0.002))
    x += bp(white(n, seed), f0 * 0.8, f1 * 2.0) * np.exp(-t * 80) * 0.25
    return (x * amp).astype(np.float32)


def room(x, decay=0.7, wet=0.18, damp=4200.0, seed=7):
    return dsp.reverb(x, decay, wet, damp, 0.01, seed)


def breath(dur, seed, lo=400.0, hi=3000.0, shape=((0, 0), (0.3, 1), (0.75, 0.8), (1, 0)), formants=(700, 1200, 2400),
           wet=0.0):
    n = N(dur)
    x = dsp.lowpass(bp(white(n, seed), lo, hi, 2), hi, 4)
    x = x * 0.25 + dsp.formant(x, (formants,), 6.0)
    y = x * env(n, list(shape))
    if wet:
        r = R(seed + 3)
        for k in range(int(dur * 30 * wet)):
            pos = r.random() * dur * 0.95
            c = dsp.lowpass(click(seed + 11 + k, 0.0025, 700), 3000, 2) * (0.3 + r.random() * 0.7) * wet * 0.6
            add(y, c, pos)
    return y.astype(np.float32)


# ------------------------------------------------------------------ the sounds
def gota(v):
    seed = 100 + v * 13
    out = np.zeros(N(0.5), np.float32)
    f0 = [340, 420, 300][v]
    add(out, bubble(f0, f0 * 2.4, 0.09, seed, 1.0), 0.0)
    add(out, thump(90 + v * 10, 0.12, seed + 1, 0.4), 0.0)
    add(out, dsp.lowpass(click(seed + 2, 0.003, 900), 2600, 2) * 0.5, 0.004)
    if v != 1:
        add(out, bubble(f0 * 1.6, f0 * 3.0, 0.05, seed + 3, 0.35), 0.11)  # a smaller one after
    return room(out, 0.6, 0.16)


def escribe():
    out = np.zeros(N(2.0), np.float32)
    for k, (t0, d) in enumerate(((0.05, 0.5), (0.65, 0.42), (1.2, 0.6))):
        n = N(d)
        smear = bp(white(n, 200 + k), 260, 2200) * env(n, [(0, 0), (0.15, 1), (0.7, 0.8), (1, 0)])
        smear *= 0.6 + 0.4 * np.sin(np.arange(n) / SR * 2 * np.pi * (9 + k * 3)) ** 2
        add(out, smear * 0.5, t0)
        r = R(210 + k)
        for j in range(int(d * 50)):  # wet crackle under the finger
            add(out, dsp.lowpass(click(220 + k * 50 + j, 0.002, 600), 2400, 2) * (0.2 + r.random() * 0.5), t0 + r.random() * d)
    return room(out, 0.5, 0.12)


def revela():
    dur = 2.8
    n = N(dur)
    t = np.arange(n) / SR
    low = np.zeros(n, np.float32)
    for f, g in ((55.0, 1.0), (58.3, 0.8), (82.4, 0.5), (110.6, 0.35)):
        low += dsp.osc(f * (1 + 0.004 * np.sin(2 * np.pi * 0.7 * t)), dur, 'saw') * g
    low = dsp.lowpass(low, 420, 4) * env(n, [(0, 0), (0.35, 0.9), (0.8, 0.7), (1, 0)])
    # a bowed scrape tearing upwards
    scrape = dsp.sweep_lowpass(bp(white(n, 301), 300, 5000), 400, 4200) * env(n, [(0, 0), (0.25, 0.1), (0.55, 0.8), (0.75, 0.3), (1, 0)])
    out = low * 0.6 + scrape * 0.35
    beat = thump(48, 0.6, 302, 1.4)
    add(out, beat, 1.55)
    return room(out, 1.4, 0.25)


def mano_vidrio(v):
    seed = 400 + v * 17
    out = np.zeros(N(0.9), np.float32)
    n = N(0.012)
    slap = white(n, seed) * np.exp(-np.arange(n) / (n * 0.2))
    slap = bp(slap, 500, 6000)
    add(out, slap * 1.0, 0.0)
    exc = np.zeros(N(0.6), np.float32)
    exc[:len(slap)] = slap
    ring = modal(exc, [(1650 + v * 90, 0.12, 1.0), (2480 + v * 60, 0.09, 0.7), (3720, 0.07, 0.5), (5100, 0.05, 0.3)])
    add(out, ring / (np.max(np.abs(ring)) + 1e-9) * 0.35, 0.0)
    add(out, thump(85 + v * 8, 0.18, seed + 1, 0.6), 0.002)  # the frame
    m = N(0.3)
    wetx = bp(white(m, seed + 2), 400, 1600) * env(m, [(0, 0), (0.05, 1), (0.4, 0.3), (1, 0)])
    add(out, wetx * 0.3, 0.015)
    r = R(seed + 3)
    for j in range(8):
        add(out, dsp.lowpass(click(seed + 20 + j, 0.002, 800), 2800, 2) * (0.2 + r.random() * 0.3), 0.03 + r.random() * 0.25)
    return room(out, 0.5, 0.12)


def arrastre():
    dur = 1.5
    n = N(dur)
    r = R(500)
    out = np.zeros(n, np.float32)
    t = 0.0
    rate = 34.0
    while t < dur * 0.92:
        g = click(510 + int(t * 1000), 0.008 + r.random() * 0.01, 900)
        f_hi = 2600 - t * 900
        g = bp(g, 900, max(1200, f_hi))
        add(out, g * (0.5 + r.random() * 0.5) * (1 - t / dur * 0.6), t)
        t += 1.0 / rate
        rate = max(9.0, rate * 0.985)  # slower and slower
    tt = np.arange(n) / SR
    squeal = np.sin(2 * np.pi * np.cumsum(1500 - 500 * tt / dur + 20 * np.sin(2 * np.pi * 6 * tt)) / SR) * env(n, [(0, 0), (0.1, 0.25), (0.6, 0.15), (1, 0)])
    smear = bp(white(n, 520), 300, 1400) * env(n, [(0, 0), (0.1, 0.6), (0.9, 0.4), (1, 0)])
    out += squeal.astype(np.float32) * 0.18 + smear * 0.3
    return room(out, 0.5, 0.12)


def pisada(v):
    seed = 600 + v * 19
    out = np.zeros(N(0.55), np.float32)
    add(out, thump(64 + v * 7, 0.22, seed, 0.9), 0.0)          # heel
    n = N(0.03)
    slap = bp(white(n, seed + 1), 500, 3200) * np.exp(-np.arange(n) / (n * 0.3))
    add(out, slap * 0.8, 0.045 + v * 0.01)                     # the sole lands
    creak = modal(dsp.lowpass(white(N(0.25), seed + 2), 900, 2) * env(N(0.25), [(0, 0), (0.1, 1), (1, 0)]),
                  [(230 + v * 20, 0.15, 1.0), (380, 0.1, 0.6)])
    add(out, creak / (np.max(np.abs(creak)) + 1e-9) * 0.12, 0.05)
    r = R(seed + 3)
    for j in range(6):                                         # the skin peeling off the wet floor
        add(out, dsp.lowpass(click(seed + 30 + j, 0.002, 700), 2600, 2) * (0.25 + r.random() * 0.35), 0.18 + r.random() * 0.12)
    return room(out, 0.55, 0.14)


def burbujea():
    dur = 4.6
    n = N(dur)
    r = R(700)
    out = np.zeros(n, np.float32)
    bed = dsp.lowpass(white(n, 701), 260, 4) * (0.5 + 0.5 * dsp.lowpass(np.abs(white(n, 702)), 3, 1) * 12)
    out += bed * 0.25 * env(n, [(0, 0), (0.1, 1), (0.9, 1), (1, 0)])
    t = 0.05
    while t < dur - 0.3:
        f0 = 90 + r.random() * 90
        add(out, bubble(f0, f0 * (1.8 + r.random()), 0.09 + r.random() * 0.12, 710 + int(t * 100), 0.6 + r.random() * 0.5), t)
        t += 0.12 + r.random() * 0.35
    return room(out, 0.8, 0.2)


def hunde():
    dur = 3.0
    n = N(dur)
    out = np.zeros(n, np.float32)
    # the gloop as it goes under
    tt = np.arange(N(0.8)) / SR
    g = np.sin(2 * np.pi * np.cumsum(220 * np.exp(-tt * 2.2) + 50) / SR) * np.exp(-tt * 3.5)
    g += dsp.lowpass(white(len(tt), 801), 500, 2) * np.exp(-tt * 6) * 0.6
    add(out, g.astype(np.float32) * 0.9, 0.0)
    r = R(802)
    t = 0.45
    k = 0
    while t < 2.2:                    # its last bubbles, lower and slower
        f0 = 260 - k * 18 + r.random() * 30
        add(out, bubble(max(70, f0), max(140, f0 * 2.2), 0.12, 810 + k, 0.7 - k * 0.04), t)
        t += 0.12 + k * 0.03 + r.random() * 0.08
        k += 1
    m = N(0.8)
    suck = bp(white(m, 830), 200, 900) * env(m, [(0, 0), (0.7, 1), (0.95, 0.4), (1, 0)])
    add(out, suck * 0.4, 2.1)
    return room(out, 0.8, 0.2)


def dientes():
    dur = 1.3
    out = np.zeros(N(dur), np.float32)
    r = R(900)
    shakes = [0.0, 0.32, 0.6, 0.9]
    for s in shakes:
        for j in range(r.integers(6, 11)):
            t = s + r.random() * 0.16
            c = click(910 + int(t * 1000) + j, 0.0015, 2500)
            hit = modal(np.pad(c, (0, N(0.05))), [(3300 + r.random() * 1800, 0.02, 1.0), (5600 + r.random() * 1500, 0.015, 0.6)])
            add(out, hit / (np.max(np.abs(hit)) + 1e-9) * (0.25 + r.random() * 0.5), t)
        wood = modal(np.pad(dsp.lowpass(click(950 + int(s * 100), 0.004, 200), 1200, 2), (0, N(0.2))), [(240, 0.08, 1.0), (430, 0.06, 0.6)])
        add(out, wood / (np.max(np.abs(wood)) + 1e-9) * 0.3, s)
    return room(out, 0.4, 0.1)


def cajon():
    dur = 1.0
    n = N(dur)
    r = R(1000)
    out = np.zeros(n, np.float32)
    t = 0.02
    while t < 0.72:
        g = bp(click(1010 + int(t * 1000), 0.01 + r.random() * 0.012, 150), 250, 1400)
        add(out, g * (0.5 + r.random() * 0.5), t)
        t += 1.0 / (22 + r.random() * 30)
    grind = bp(white(n, 1020), 180, 900) * env(n, [(0, 0), (0.05, 0.5), (0.7, 0.4), (0.74, 0), (1, 0)])
    out += grind * 0.3
    add(out, thump(120, 0.2, 1021, 0.9), 0.74)                 # the stop
    rattle = modal(np.pad(click(1022, 0.002, 2500), (0, N(0.06))), [(3800, 0.02, 1.0), (5200, 0.015, 0.5)])
    add(out, rattle / (np.max(np.abs(rattle)) + 1e-9) * 0.2, 0.76)  # something small inside rolls
    return room(out, 0.45, 0.12)


def respira(v):
    seed = 1100 + v * 23
    dur = 2.4 if v == 0 else 2.9
    out = np.zeros(N(dur), np.float32)
    inh = breath(0.9, seed, 900, 4200, ((0, 0), (0.6, 1), (0.9, 0.9), (1, 0)), (1000, 1800, 2900), wet=0.5)
    tt = np.arange(len(inh)) / SR
    whistle = np.sin(2 * np.pi * np.cumsum(2100 + 140 * np.sin(2 * np.pi * 3.1 * tt)) / SR) * env(len(inh), [(0, 0), (0.6, 0.15), (0.95, 0.3), (1, 0)])
    if v == 0:
        add(out, inh + whistle.astype(np.float32) * 0.12, 0.05)
    exh = breath(1.3 if v == 0 else 2.2, seed + 5, 250, 2400, ((0, 0), (0.08, 1), (0.6, 0.5), (1, 0)), (550, 950, 2200), wet=1.0)
    t = np.arange(len(exh)) / SR
    fry = np.maximum(0, np.sin(2 * np.pi * np.cumsum(np.full(len(exh), 34.0)) / SR)) ** 14
    exh += bp(fry.astype(np.float32), 150, 2000) * env(len(exh), [(0, 0), (0.1, 0.6), (0.7, 0.3), (1, 0)]) * 0.5
    add(out, exh, 1.0 if v == 0 else 0.2)
    add(out, modal(np.pad(click(seed + 9, 0.002, 1800), (0, N(0.05))), [(2400, 0.03, 1.0)]) * 0.4, dur - 0.25)  # a click in the throat
    return room(out, 0.35, 0.08)


def linterna_muere():
    dur = 1.1
    n = N(dur)
    t = np.arange(n) / SR
    buzz = np.zeros(n, np.float32)
    for k, g in ((1, 1.0), (2, 0.6), (3, 0.5), (5, 0.3), (7, 0.2)):
        buzz += np.sin(2 * np.pi * 120 * k * t) * g
    gate = (dsp.lowpass(white(n, 1201), 40, 2) > 0.0).astype(np.float32)
    buzz = buzz * gate * env(n, [(0, 0.2), (0.1, 1), (0.55, 0.8), (0.62, 0), (1, 0)])
    out = dsp.highpass(buzz, 200, 2) * 0.6
    r = R(1202)
    for j in range(18):  # crackle
        tt = r.random() * 0.62
        add(out, dsp.lowpass(click(1210 + j, 0.002, 1500), 6000, 2) * (0.12 + r.random() * 0.25), tt)
    ping = np.sin(2 * np.pi * 2650 * t[:N(0.25)]) * np.exp(-t[:N(0.25)] * 22)
    add(out, ping.astype(np.float32) * 0.3, 0.62)               # the filament
    add(out, click(1250, 0.006, 600) * 0.8, 0.64)                # the last pop
    return room(out, 0.3, 0.08)


def obturador():
    out = np.zeros(N(0.35), np.float32)
    a = bp(white(N(0.02), 1300), 1500, 7000) * np.exp(-np.arange(N(0.02)) / N(0.004))
    b = bp(white(N(0.03), 1301), 900, 5000) * np.exp(-np.arange(N(0.03)) / N(0.006))
    add(out, a, 0.0)
    add(out, modal(np.pad(click(1302, 0.002, 2500), (0, N(0.04))), [(4200, 0.015, 1.0), (6100, 0.01, 0.6)]) * 0.5, 0.002)
    add(out, b * 0.8, 0.075)
    add(out, modal(np.pad(click(1303, 0.002, 2500), (0, N(0.04))), [(3800, 0.015, 1.0)]) * 0.4, 0.078)
    return room(out, 0.4, 0.15)


def papel(v):
    seed = 1400 + v * 29
    dur = 0.8
    n = N(dur)
    r = R(seed)
    out = np.zeros(n, np.float32)
    k = 0
    t = 0.02
    while t < dur * 0.7:
        c = bp(click(seed + k, 0.002 + r.random() * 0.003, 900), 1000, 7000)
        add(out, c * (0.15 + r.random() * 0.6), t)
        t += 0.004 + r.random() * 0.03
        k += 1
    m = N(0.35)
    flap = bp(white(m, seed + 99), 250, 2200) * env(m, [(0, 0), (0.3, 1), (1, 0)])
    add(out, flap * 0.45, 0.3 + v * 0.08)
    return room(out, 0.35, 0.1)


EVENTS = {
    'sangre.gota': ([lambda: gota(0), lambda: gota(1), lambda: gota(2)], -3.0),
    'sangre.escribe': ([escribe], -3.0),
    'sangre.revela': ([revela], -1.0),
    'sangre.mano_vidrio': ([lambda: mano_vidrio(0), lambda: mano_vidrio(1), lambda: mano_vidrio(2)], -1.5),
    'sangre.arrastre': ([arrastre], -2.0),
    'sangre.pisada': ([lambda: pisada(0), lambda: pisada(1), lambda: pisada(2)], -3.0),
    'sangre.burbujea': ([burbujea], -2.0),
    'sangre.hunde': ([hunde], -1.5),
    'sangre.dientes': ([dientes], -3.0),
    'sangre.cajon': ([cajon], -3.0),
    'sangre.respira': ([lambda: respira(0), lambda: respira(1)], -2.0),
    'linterna.muere': ([linterna_muere], -3.0),
    'celular.obturador': ([obturador], -3.0),
    'lore.papel': ([lambda: papel(0), lambda: papel(1)], -4.0),
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
    print(f'sangre group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
