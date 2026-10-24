# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "polter" (B1a): the Casa Morales alive (docs/design/casa_terror.md 5, events 1-32) and the
things that answer a click (6.3). Nobody speaks: knocks, steps, breaths, a giggle, a music box, a backwards prayer,
claws on a door, an old phone, a child crying in a duct, taps, blinds, a rocking chair, drawers, a TV, a radio.

Run from the repo root:  python3 tools/audio/snd_polter.py [substring ...]

  polter.pasos_arriba (3)   one slow heavy step on the boards of the floor above: through the ceiling (muffled), the
                            joist flexing, a little plaster dust.
  polter.golpe (3)          one knock from inside a wall: a knuckle on hollow plaster over brick.
  polter.palmadas           two dry hand claps, close behind you, in a small room.
  polter.risita (2)         a little girl's breathy giggle in another room (vowel-ish 'hi-hi-hi', no words).
  polter.caja_musica        Lucía's music box: a slow lullaby on steel tines, a little out of tune, winding down at the
                            end (15 s).
  polter.dentadura (2)      dentures clacking right at your ear: a wet plastic clack and a suck.
  polter.susurro (2)        a whisper shaped like a name: two syllables of breath, no words.
  polter.respira (2)        heavy, wet, old breathing pressed against your ear (three breaths).
  polter.rezo_reves         an old woman murmuring a prayer, every syllable backwards (swelling and cut off), through a
                            door (9 s).
  polter.rasguno_puerta (2) claws scratching a wooden door low down, a paw thumping it.
  polter.telefono_ring      the old bell phone: two bursts of a hammer between two bells.
  polter.telefono_respira   the receiver: line static, and slow breathing on the other end (6.5 s).
  polter.llanto_rejilla     a small child sobbing, heard through a metal duct (7 s).
  polter.picaporte (2)      a door handle rattled from the other side: latch clicks, the door shaking in its frame.
  polter.heladera           an old fridge: the door seal letting go, the relay, the compressor hum, the bulb buzzing.
  polter.papel              something wrapped in paper moving: crinkles and a soft wet shift.
  polter.canilla            a tap: the valve squeaks open, water gushes into a basin.
  polter.canilla_sangre     thick blood out of a tap: glugs, gouts, a choking pipe.
  polter.persianas          every roller blind of the floor crashing down: slats rattling down fast, the bang.
  polter.persiana           one blind rolled by hand: the strap, the slats clicking past.
  polter.mecedora           the rocking chair rocking by itself faster and faster, then a dead stop. Its creaks are
                            placed on the swings of com.deadline.horror.casa.Rocker (same formula, kept in sync).
  polter.cajon (2)          a wooden drawer pulled out / pushed in.
  polter.cajones            every drawer of the room slamming shut at once.
  polter.tele_on            the old CRT switching on: relay, thunk, whine, a surge of static.
  polter.tele_off           the CRT off: click, the picture collapsing.
  polter.radio              an AM radio between stations, and inside the static a child humming a lullaby (6 s).
  polter.llave_luz          a bakelite light switch.
  polter.zumbido            a failing bulb: mains buzz and arcing crackles.
  polter.maquina_coser      the treadle Singer running: needle clatter, treadle, belt.
  polter.puerta_lenta       a door creaking open by itself: a short creak, a pause, the long one (PuertaLenta timing).
  polter.cuadro             a picture frame scraping on its nail.
  polter.objeto (2)         a thrown thing hitting: a book's thump.
  polter.vidrio (2)         a glass or a jar shattering.

Positional sounds: mono. Review: spectrogram PNG per file in <work>/audio/polter (+ stats.json).
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

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/polter'))


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


def lp(x, f, order=2):
    return dsp.lowpass(x, f, order)


def hp(x, f, order=2):
    return dsp.highpass(x, f, order)


def norm(x):
    return (x / (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


def modal(exc, modes):
    """Excite a bank of decaying resonances (f Hz, decay s, gain)."""
    out = np.zeros(len(exc), np.float32)
    for f, d, g in modes:
        r = np.exp(-1.0 / (max(d, 1e-3) * SR))
        w = 2 * np.pi * f / SR
        out += signal.lfilter([g * (1 - r)], [1, -2 * r * np.cos(w), r * r], exc).astype(np.float32)
    return out


def ringing(exc, modes):
    """modal() with room for the resonances to ring out after a short excitation (a click)."""
    maxd = max(d for _, d, _ in modes)
    x = np.zeros(max(len(exc), N(maxd * 6)), np.float32)
    x[:len(exc)] = exc
    return modal(x, modes)


def click(seed, dur=0.004, hpf=1500.0):
    n = N(dur)
    x = white(n, seed) * np.exp(-np.arange(n) / (n * 0.25))
    return hp(x.astype(np.float32), hpf)


def thump(f0, dur, seed, amp=1.0, bend=0.6):
    n = N(dur)
    t = np.arange(n) / SR
    f = f0 * (1 + bend * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * (6.0 / dur)) * amp
    x += lp(white(n, seed), 300) * np.exp(-t * 60) * 0.5 * amp
    return x.astype(np.float32)


def room(x, decay=0.6, wet=0.2, damp=4500.0, seed=7):
    return dsp.reverb(x, decay, wet, damp, 0.01, seed)


def voice(dur, f0, seed, formants, breath=0.25, vib=0.0, jitter=0.01):
    """A small voiced sound: a glottal-ish pulse train (f0 may be an array) through formants, with breath noise."""
    n = N(dur)
    f = np.broadcast_to(np.asarray(f0, np.float64), (n,)) if np.ndim(f0) == 0 else np.interp(np.arange(n), np.linspace(0, n, len(f0)), f0)
    r = R(seed)
    t = np.arange(n) / SR
    f = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t)) * (1 + jitter * lp(white(n, seed + 1), 30) * 8)
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.33 * np.sin(3 * ph) + 0.25 * np.sin(4 * ph) + 0.15 * np.sin(5 * ph))
    src = src.astype(np.float32) + white(n, seed + 2) * breath
    out = np.zeros(n, np.float32)
    for (fq, g) in formants:
        out += bp(src, fq * 0.86, fq * 1.16) * g
    return out


# ------------------------------------------------------------------ the sounds
def pasos_arriba(v):
    seed = 100 + v * 23
    dur = 1.2
    out = np.zeros(N(dur), np.float32)
    # heel then ball of a heavy bare/shod foot on old boards, heard from below: low and muffled
    add(out, thump(52 + v * 5, 0.5, seed, 1.0), 0.02)
    add(out, thump(66 + v * 4, 0.3, seed + 1, 0.5), 0.13)
    creak = modal(lp(white(N(0.55), seed + 2), 900) * env(N(0.55), [(0, 0), (0.15, 1), (1, 0)]),
                  [(170 + v * 12, 0.25, 1.0), (290, 0.2, 0.6), (430, 0.15, 0.4)])
    add(out, norm(creak) * 0.35, 0.08)
    # a pinch of plaster dust trickling down
    dust = hp(white(N(0.4), seed + 3), 2500) * env(N(0.4), [(0, 0), (0.1, 0.06), (1, 0)])
    add(out, dust, 0.2)
    out = lp(out, 700, 2) + lp(out, 2500, 2) * 0.08
    return room(out, 0.5, 0.18, 1500)


def golpe(v):
    seed = 200 + v * 31
    dur = 0.6
    out = np.zeros(N(dur), np.float32)
    k = np.zeros(N(0.45), np.float32)
    add(k, thump(120 + v * 14, 0.25, seed, 1.0, bend=0.3), 0.0)
    add(k, ringing(click(seed + 1, 0.003, 300), [(230 + v * 20, 0.06, 1.2), (410, 0.05, 0.8), (690, 0.03, 0.5)]) * 2.5, 0.0)
    add(out, lp(k, 1600, 2), 0.01)
    return room(out, 0.35, 0.15, 2500)


def palmadas():
    seed = 300
    dur = 1.4
    out = np.zeros(N(dur), np.float32)
    for i, t0 in enumerate((0.05, 0.43)):
        n = N(0.09)
        tt = np.arange(n) / SR
        burst = bp(white(n, seed + i), 700, 3600) * np.exp(-tt * 70) * 1.2
        body = ringing(click(seed + 10 + i, 0.002, 200), [(520 + i * 30, 0.02, 1.0), (880, 0.015, 0.6)]) * 3
        add(out, burst, t0)
        add(out, body, t0)
    return room(out, 0.5, 0.22, 6000)


def risita(v):
    seed = 400 + v * 41
    out = np.zeros(N(1.9), np.float32)
    t0 = 0.05
    r = R(seed)
    k = 5 + v
    for i in range(k):
        d = 0.08 + r.random() * 0.03
        f = 430 + 60 * np.sin(i * 1.3 + v) + r.random() * 30
        syl = voice(d, np.linspace(f * 1.05, f * 0.92, 16), seed + i, ((620, 1.0), (2300, 0.7), (3100, 0.35)), breath=0.6)
        syl *= env(len(syl), [(0, 0), (0.15, 1), (0.6, 0.7), (1, 0)])
        add(out, syl, t0)
        # the breath between: a little 'h'
        h = bp(white(N(0.05), seed + 50 + i), 1500, 5000) * env(N(0.05), [(0, 0), (0.3, 0.25), (1, 0)])
        add(out, h, t0 + d)
        t0 += d + 0.05 + r.random() * 0.03
    # the last one, longer, falling, breathy
    syl = voice(0.22, np.linspace(470, 360, 20), seed + 99, ((600, 1.0), (2100, 0.6), (3000, 0.3)), breath=0.8)
    add(out, syl * env(len(syl), [(0, 0), (0.1, 1), (1, 0)]) * 0.8, t0 + 0.05)
    return room(out, 1.1, 0.38, 3500)


# a small lullaby of our own (A minor, slow 3/4): (semitones from A4, beats)
LULLABY = [(0, 1), (3, 1), (7, 1), (5, 2), (3, 1), (2, 1), (0, 1), (-2, 1), (0, 3),
           (3, 1), (5, 1), (7, 1), (8, 2), (7, 1), (5, 1), (3, 1), (2, 1), (3, 3),
           (0, 1), (3, 1), (7, 1), (5, 2), (3, 1), (2, 1), (-2, 1), (-5, 1), (0, 4)]


def tine(f, dur, seed, detune=0.0):
    n = N(dur)
    t = np.arange(n) / SR
    f = f * (1 + detune)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
         + 0.35 * np.sin(2 * np.pi * f * 2.756 * t) * np.exp(-t * 7)
         + 0.12 * np.sin(2 * np.pi * f * 5.404 * t) * np.exp(-t * 16)).astype(np.float32)
    add(x, click(seed, 0.002, 3000) * 0.3, 0.0)    # the pin plucking the tine
    return x


def caja_musica():
    seed = 500
    dur = 15.0
    out = np.zeros(N(dur), np.float32)
    t = 0.1
    beat = 0.5
    total = sum(b for _, b in LULLABY)
    acc = 0
    r = R(seed)
    for i, (semi, beats) in enumerate(LULLABY):
        f = 880.0 * 2 ** (semi / 12)
        late = acc / total
        det = (r.random() - 0.5) * 0.006 + (-0.012 * late ** 3)    # it goes flat as the spring runs down
        x = tine(f, min(2.5, beats * beat + 1.2), seed + i, det)
        add(out, x * (0.9 - 0.25 * late), t)
        if beats >= 2 and r.random() < 0.6:
            add(out, tine(f / 2, 1.6, seed + 200 + i, det) * 0.3, t)    # a lower tine with it
        acc += beats
        # winding down: the beats get longer towards the end
        t += beats * beat * (1 + 0.8 * late ** 2.2)
        if t > dur - 1.5:
            break
    # the mechanism: a soft comb tick and the spring's purr
    mech = lp(white(len(out), seed + 900), 1200) * 0.015
    out += mech * env(len(out), [(0, 1), (0.85, 0.7), (1, 0)])
    out = hp(out, 300, 2)
    return room(out, 0.9, 0.3, 6000)


def dentadura(v):
    seed = 600 + v * 17
    out = np.zeros(N(0.55), np.float32)
    for i, t0 in enumerate((0.02, 0.11 + v * 0.03)):
        c = ringing(click(seed + i, 0.0025, 600), [(1500 + v * 120, 0.025, 1.0), (2600 + v * 200, 0.012, 0.7), (900, 0.03, 0.6)]) * 3
        add(out, lp(c, 6000), t0)
    # the wet suck afterwards
    n = N(0.28)
    suck = bp(white(n, seed + 9), 500, 2400) * env(n, [(0, 0), (0.2, 0.5), (0.7, 0.35), (1, 0)])
    crackle = np.zeros(n, np.float32)
    rr = R(seed + 3)
    for _ in range(14):
        add(crackle, lp(click(seed + 30 + _, 0.0012, 1500), 4500) * (0.1 + rr.random() * 0.2), rr.random() * 0.26)
    add(out, suck * 0.8 + crackle, 0.2)
    return out


def susurro(v):
    seed = 700 + v * 19
    out = np.zeros(N(1.5), np.float32)
    # two syllables of breath, vowel-ish (a... o), no pitch: someone breathing a name
    for i, (t0, d, fm) in enumerate(((0.05, 0.38, ((800, 1.0), (1300, 0.8), (2600, 0.4))), (0.55, 0.6, ((550, 1.0), (900, 0.8), (2400, 0.3))))):
        n = N(d)
        b = white(n, seed + i)
        x = np.zeros(n, np.float32)
        for (f, g) in fm:
            x += bp(b, f * 0.85, f * 1.18) * g
        x += bp(b, 3500, 6000) * 0.05    # the lips
        x *= env(n, [(0, 0), (0.25, 1), (0.6, 0.8), (1, 0)])
        add(out, x, t0)
    return room(lp(out, 6000, 2), 1.0, 0.3, 4000)


def breath(dur, seed, lo=400.0, hi=3000.0, shape=((0, 0), (0.25, 1), (0.7, 0.8), (1, 0)), formants=(700, 1200, 2400), rattle=0.0):
    n = N(dur)
    b = bp(white(n, seed), lo, hi)
    x = b * 0.25
    for f in formants:
        x += bp(b, f * 0.86, f * 1.16)
    e = env(n, list(shape))
    y = x * e
    if rattle:
        t = np.arange(n) / SR
        pulses = np.maximum(0, np.sin(2 * np.pi * 34 * t * (1 + 0.1 * np.sin(t * 7)))) ** 10
        y += bp(pulses.astype(np.float32) * white(n, seed + 1), 150, 1600) * e * rattle
    return y.astype(np.float32)


def respira(v):
    seed = 800 + v * 13
    out = np.zeros(N(4.2), np.float32)
    t0 = 0.05
    for k in range(3):
        add(out, breath(0.8, seed + k * 3, 300, 2600, ((0, 0), (0.6, 1), (1, 0)), (600, 1100, 2200), rattle=0.3), t0)
        add(out, breath(0.9, seed + k * 3 + 1, 250, 2200, ((0, 0), (0.1, 1), (0.5, 0.6), (1, 0)), (500, 950, 2000), rattle=0.8), t0 + 0.75)
        t0 += 1.35 + v * 0.05
    return out


def rezo_reves():
    seed = 900
    dur = 9.0
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    vowels = [((750, 1.0), (1150, 0.7), (2500, 0.3)), ((450, 1.0), (1900, 0.6), (2600, 0.3)), ((400, 1.0), (800, 0.7), (2400, 0.2)),
              ((550, 1.0), (1700, 0.5), (2500, 0.3)), ((350, 1.0), (2100, 0.5), (2800, 0.25))]
    t0 = 0.2
    phrase = 0
    while t0 < dur - 0.6:
        # a phrase of 6-10 syllables, the pitch falling (it will rise once reversed), then a breath
        k = 6 + r.integers(0, 5)
        base = 205 + r.random() * 20
        for i in range(k):
            d = 0.13 + r.random() * 0.09
            f = base * (1 - 0.12 * i / k) * (1 + (r.random() - 0.5) * 0.04)
            syl = voice(d, np.linspace(f, f * 0.97, 8), seed + phrase * 20 + i, vowels[r.integers(0, len(vowels))], breath=0.35, vib=0.01, jitter=0.03)
            syl *= env(len(syl), [(0, 0), (0.08, 1), (0.5, 0.8), (1, 0.05)])
            if r.random() < 0.4:   # a consonant-ish hiss at the syllable's edge
                add(syl, hp(white(N(0.04), seed + 500 + i), 3000) * 0.3, 0.0)
            add(out, syl, t0)
            t0 += d + 0.02
        add(out, breath(0.35, seed + 700 + phrase, 300, 2400, ((0, 0), (0.4, 0.5), (1, 0)), (700, 1200, 2400)) * 0.4, t0 + 0.05)
        t0 += 0.5 + r.random() * 0.3
        phrase += 1
    out = dsp.reverse(out)
    out = lp(out, 2600, 2)                     # through the door
    return room(out, 1.2, 0.35, 2500)


def rasguno_puerta(v):
    seed = 1000 + v * 29
    dur = 2.6
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    t0 = 0.05
    while t0 < dur - 0.3:
        for j in range(2 + r.integers(0, 2)):          # a stroke of two or three claws
            n = N(0.07 + r.random() * 0.05)
            s = bp(white(n, seed + int(t0 * 1000) + j), 1500, 6000) * env(n, [(0, 0), (0.1, 1), (0.8, 0.6), (1, 0)])
            s = s * (0.6 + 0.4 * np.sin(np.arange(n) / SR * 2 * np.pi * (90 + r.random() * 60)))
            add(out, s.astype(np.float32) * 0.6, t0 + j * 0.012)
        t0 += 0.11 + r.random() * 0.07
        if r.random() < 0.12:
            add(out, thump(95, 0.25, seed + int(t0 * 77), 0.8), t0)   # a paw against the door
            t0 += 0.15
    wood = modal(out * 0.5, [(180, 0.08, 0.8), (320, 0.06, 0.6), (520, 0.05, 0.4)])
    out = out + wood * 2
    return room(lp(out, 5000, 2), 0.4, 0.18, 4000)


def telefono_ring():
    seed = 1100
    dur = 2.4
    out = np.zeros(N(dur), np.float32)
    t = np.arange(N(1.0)) / SR
    bells = (np.sin(2 * np.pi * 1180 * t) + 0.6 * np.sin(2 * np.pi * 1180 * 2.31 * t) + 0.3 * np.sin(2 * np.pi * 1180 * 3.9 * t)
             + 0.8 * np.sin(2 * np.pi * 1420 * t) + 0.4 * np.sin(2 * np.pi * 1420 * 2.31 * t))
    striker = (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 21 * t))) * env(len(t), [(0, 0), (0.02, 1), (0.9, 1), (1, 0)])
    burst = (bells * striker).astype(np.float32)
    burst += hp(white(len(t), seed), 3000) * 0.04 * striker.astype(np.float32)
    for t0 in (0.05, 1.3):
        add(out, burst, t0)
    tail = modal(out * 0.3, [(1180, 0.4, 0.3), (1420, 0.35, 0.3)])
    return room(out + tail, 0.7, 0.25, 6000)


def phone_band(x):
    return dsp.drive(bp(x, 300, 3400, 3) * 1.5, 1.6)


def telefono_respira():
    seed = 1200
    dur = 6.5
    n = N(dur)
    static = bp(white(n, seed), 300, 3400) * 0.08
    r = R(seed)
    crackle = np.zeros(n, np.float32)
    for _ in range(60):
        add(crackle, click(seed + _, 0.003, 600) * (0.2 + r.random() * 0.5), r.random() * dur)
    out = static + crackle * 0.4
    t0 = 0.6
    for k in range(3):
        add(out, breath(1.0, seed + 20 + k, 250, 2500, ((0, 0), (0.6, 1), (1, 0)), (500, 1000, 2100), rattle=0.4) * 0.9, t0)
        add(out, breath(1.1, seed + 30 + k, 200, 2200, ((0, 0), (0.1, 1), (1, 0)), (450, 900, 1900), rattle=0.9), t0 + 1.0)
        t0 += 2.0
    return phone_band(out)


def llanto_rejilla():
    seed = 1300
    dur = 7.0
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    t0 = 0.2
    while t0 < dur - 0.8:
        # a sob: two or three short cries and a gasping inhale
        for i in range(2 + r.integers(0, 2)):
            d = 0.25 + r.random() * 0.35
            f = 470 + r.random() * 80
            cry = voice(d, np.array([f * 1.08, f * 1.12, f, f * 0.85]), seed + int(t0 * 100) + i,
                        ((850, 1.0), (1300, 0.7), (3000, 0.3)), breath=0.4, vib=0.03, jitter=0.04)
            add(out, cry * env(len(cry), [(0, 0), (0.1, 1), (0.7, 0.8), (1, 0)]), t0)
            t0 += d + 0.08
        gasp = breath(0.3, seed + int(t0 * 31), 600, 4000, ((0, 0), (0.7, 1), (1, 0)), (900, 1500, 2800))
        add(out, gasp * 0.7, t0)
        t0 += 0.45 + r.random() * 0.4
    # the duct: a band, a comb of short reflections ringing in sheet metal
    x = bp(out, 300, 3000)
    duct = x.copy()
    for d, g in ((0.0071, 0.55), (0.0113, 0.45), (0.0167, 0.35), (0.026, 0.25)):
        k = N(d)
        duct[k:] += x[:-k] * g
    duct = dsp.peak(duct, 1400, 6.0, 8.0)
    return room(duct * 0.7, 1.4, 0.35, 3000)


def picaporte(v):
    seed = 1400 + v * 11
    dur = 1.2
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    t0 = 0.03
    while t0 < dur - 0.15:
        c = ringing(click(seed + int(t0 * 999), 0.002, 1200), [(1900 + v * 150, 0.03, 1.0), (3100, 0.02, 0.6), (850, 0.04, 0.5)]) * 2.5
        add(out, c * (0.6 + r.random() * 0.4), t0)
        if r.random() < 0.4:
            add(out, thump(130, 0.12, seed + int(t0 * 55), 0.35), t0 + 0.01)   # the door in its frame
        t0 += 0.07 + r.random() * 0.05
    return room(out, 0.4, 0.15, 5000)


def heladera():
    seed = 1500
    dur = 5.0
    n = N(dur)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    # the seal letting go, then the relay
    add(out, bp(white(N(0.12), seed), 200, 1500) * env(N(0.12), [(0, 0), (0.1, 1), (1, 0)]) * 0.8, 0.02)
    add(out, ringing(click(seed + 1, 0.002, 800), [(1500, 0.02, 1.0), (600, 0.03, 0.6)]) * 2, 0.25)
    hum = (np.sin(2 * np.pi * 50 * t) + 0.6 * np.sin(2 * np.pi * 100 * t) + 0.35 * np.sin(2 * np.pi * 150 * t) + 0.2 * np.sin(2 * np.pi * 200 * t))
    hum *= (1 + 0.05 * np.sin(2 * np.pi * 0.7 * t))
    hum = hum.astype(np.float32) * env(n, [(0, 0), (0.06, 0), (0.15, 0.5), (0.9, 0.5), (1, 0)])
    buzz = bp(np.sign(np.sin(2 * np.pi * 100 * t)).astype(np.float32), 1500, 6000) * 0.05
    out += hum * 0.5 + buzz * env(n, [(0, 0), (0.07, 0), (0.1, 1), (1, 0.8)])
    return room(out, 0.4, 0.15, 3000)


def papel():
    seed = 1600
    dur = 2.4
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    for _ in range(90):
        tt = (r.random() ** 0.8) * (dur - 0.2)
        c = bp(click(seed + _, 0.004, 1500), 2000, 8000) * (0.3 + r.random() * 0.7)
        add(out, c, tt)
    shift = bp(white(N(0.6), seed + 300), 150, 900) * env(N(0.6), [(0, 0), (0.3, 0.6), (1, 0)])
    add(out, shift, 0.6)
    wet = np.zeros(N(0.4), np.float32)
    for _ in range(8):
        add(wet, lp(click(seed + 400 + _, 0.003, 300), 1500) * 0.6, r.random() * 0.35)
    add(out, wet, 0.9)
    return room(out, 0.3, 0.12, 6000)


def water(n, seed, lo=500.0, hi=5000.0):
    x = bp(white(n, seed), lo, hi)
    fl = lp(white(n, seed + 1), 12) * 25
    return (x * (0.7 + 0.3 * np.tanh(fl))).astype(np.float32)


def canilla():
    seed = 1700
    dur = 4.0
    n = N(dur)
    out = np.zeros(n, np.float32)
    # the old valve squeaks open
    sq = dsp.osc(np.geomspace(950, 1350, N(0.35)), 0.35, 'saw') * 0.15
    sq = bp(sq + white(N(0.35), seed) * 0.05, 800, 4000) * env(N(0.35), [(0, 0), (0.2, 1), (1, 0)])
    add(out, sq, 0.02)
    w = water(n, seed + 2) * env(n, [(0, 0), (0.1, 0), (0.2, 1), (0.9, 1), (1, 0)])
    out += w * 0.6
    # into a basin: low splashes
    r = R(seed)
    for _ in range(40):
        add(out, lp(click(seed + 50 + _, 0.006, 200), 1200) * (0.2 + r.random() * 0.3), 0.4 + r.random() * 3.4)
    return room(out, 0.5, 0.2, 5000)


def canilla_sangre():
    seed = 1800
    dur = 4.2
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = R(seed)
    t0 = 0.05
    while t0 < dur - 0.3:
        # a glug: a resonant bubble in the pipe, low, then the gout landing
        f = 140 + r.random() * 220
        m = N(0.12 + r.random() * 0.1)
        tt = np.arange(m) / SR
        bub = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * tt / (m / SR))) / SR) * np.exp(-tt * 18)
        add(out, bub.astype(np.float32) * (0.5 + r.random() * 0.5), t0)
        splat = lp(bp(white(N(0.15), seed + int(t0 * 300)), 150, 1800), 1200) * env(N(0.15), [(0, 0), (0.05, 1), (1, 0)])
        add(out, splat * 0.5, t0 + 0.08)
        t0 += 0.14 + r.random() * 0.25
    # a choking gurgle under it all
    gur = lp(white(n, seed + 99), 400) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * np.arange(n) / SR)).astype(np.float32) * 0.3
    return room(out + gur, 0.5, 0.2, 2500)


def slats(dur, rate0, rate1, seed, f0=1600.0):
    """Slats of a roller blind clicking past, rate going from rate0 to rate1 per second."""
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    t0 = 0.0
    while t0 < dur:
        u = t0 / dur
        rate = rate0 + (rate1 - rate0) * u
        c = ringing(click(seed + int(t0 * 2000), 0.002, 400), [(f0 * (1 - 0.25 * u) * (0.9 + r.random() * 0.2), 0.02, 1.0), (f0 * 0.45, 0.03, 0.5)])
        add(out, c * (0.5 + r.random() * 0.5), t0)
        t0 += 1.0 / rate * (0.8 + r.random() * 0.4)
    return out


def persianas():
    seed = 1900
    dur = 2.3
    out = np.zeros(N(dur), np.float32)
    add(out, slats(1.0, 25, 70, seed) * 2.5, 0.02)
    whirr = bp(white(N(1.0), seed + 5), 200, 1500) * env(N(1.0), [(0, 0), (0.3, 0.4), (0.9, 0.6), (1, 0)])
    add(out, whirr * 0.5, 0.02)
    add(out, thump(80, 0.6, seed + 7, 1.4), 1.02)
    add(out, slats(0.4, 40, 10, seed + 9, 1200) * 1.5, 1.04)
    return room(out, 0.7, 0.25, 4000)


def persiana():
    seed = 2000
    dur = 1.6
    out = np.zeros(N(dur), np.float32)
    add(out, slats(1.3, 14, 18, seed, 1400) * 1.6, 0.03)
    strap = bp(white(N(1.3), seed + 3), 600, 3000) * env(N(1.3), [(0, 0), (0.1, 0.3), (0.9, 0.3), (1, 0)])
    add(out, strap * 0.4, 0.03)
    add(out, thump(140, 0.2, seed + 4, 0.5), 1.35)
    return room(out, 0.5, 0.2, 5000)


# --- the rocking chair: the same timeline as com.deadline.horror.casa.Rocker.frenzy (ticks of 1/20 s)
ROCK_RAMP = 118
ROCK_F0, ROCK_F1, ROCK_A0, ROCK_A1 = 0.42, 1.75, 0.07, 0.21


def rocker_extremes():
    """(time s, amplitude 0..1, forward?) of every swing extreme, from the Java formula, and the stop time."""
    out = []
    phase = 0.0
    prev = 0.0
    for k in range(1, ROCK_RAMP + 1):
        u = k / ROCK_RAMP
        f = ROCK_F0 + (ROCK_F1 - ROCK_F0) * u ** 1.5
        p0 = phase
        phase += 2 * np.pi * f / 20.0
        # an extreme each time the phase passes pi/2 + n*pi
        n0 = np.floor((p0 - np.pi / 2) / np.pi)
        n1 = np.floor((phase - np.pi / 2) / np.pi)
        if n1 > n0:
            ext = np.pi / 2 + n1 * np.pi
            frac = (ext - p0) / (phase - p0)
            t = (k - 1 + frac) / 20.0
            amp = (ROCK_A0 + (ROCK_A1 - ROCK_A0) * u) / ROCK_A1
            out.append((t, amp, int(n1) % 2 == 0))
        prev = phase
    return out, (ROCK_RAMP + 1) / 20.0


def creak(dur, f, seed, amp=1.0):
    n = N(dur)
    tt = np.arange(n) / SR
    rate = 40 + 60 * np.sin(np.pi * tt / dur)        # stick-slip
    ph = 2 * np.pi * np.cumsum(rate) / SR
    pulses = (np.maximum(0, np.sin(ph)) ** 8).astype(np.float32)
    x = modal(pulses * 0.6 + white(n, seed) * 0.05, [(f, 0.05, 1.0), (f * 1.7, 0.04, 0.6), (f * 2.9, 0.03, 0.3)])
    return (norm(x) * env(n, [(0, 0), (0.2, 1), (0.8, 0.7), (1, 0)]) * amp).astype(np.float32)


def mecedora():
    seed = 2100
    ext, stop = rocker_extremes()
    dur = stop + 1.5
    out = np.zeros(N(dur), np.float32)
    # it starts to move: the wood takes the weight that is not there
    add(out, creak(0.5, 300, seed, 0.25), 0.0)
    for i, (t, amp, fwd) in enumerate(ext):
        d = max(0.12, min(0.4, 0.35 - 0.15 * t / stop))
        add(out, creak(d, (330 if fwd else 260) * (1 + 0.1 * amp), seed + i, 0.35 + 0.65 * amp), max(0.0, t - d * 0.5))
        if fwd:
            add(out, thump(90, 0.2, seed + 100 + i, 0.4 + 0.6 * amp), t)    # the rockers on the floor
    # the dead stop: a hard knock, and nothing
    add(out, thump(75, 0.35, seed + 999, 1.6, bend=0.2), stop)
    add(out, ringing(click(seed + 998, 0.002, 300), [(260, 0.08, 1.0), (520, 0.05, 0.5)]) * 3, stop)
    return room(out, 0.6, 0.2, 4000)


def cajon(v):
    seed = 2200 + v * 7
    dur = 0.75
    out = np.zeros(N(dur), np.float32)
    n = N(0.4)
    slide = bp(white(n, seed), 250, 1600) * env(n, [(0, 0), (0.15, 1), (0.85, 0.8), (1, 0)])
    slide *= (0.7 + 0.3 * np.sin(2 * np.pi * (35 + v * 10) * np.arange(n) / SR)).astype(np.float32)
    add(out, modal(slide * 0.6, [(210, 0.05, 0.8), (380, 0.04, 0.5)]) + slide * 0.5, 0.02)
    add(out, thump(190, 0.15, seed + 3, 0.8, bend=0.2), 0.42)
    add(out, ringing(click(seed + 4, 0.002, 400), [(700, 0.03, 1.0), (1300, 0.02, 0.5)]) * 2, 0.42)
    return room(out, 0.35, 0.15, 5000)


def cajones():
    seed = 2300
    dur = 1.6
    out = np.zeros(N(dur), np.float32)
    r = R(seed)
    for i in range(11):
        t0 = 0.02 + r.random() * 0.14
        add(out, thump(150 + r.random() * 80, 0.2, seed + i, 0.7 + r.random() * 0.4, bend=0.25), t0)
        add(out, ringing(click(seed + 50 + i, 0.002, 400), [(600 + r.random() * 400, 0.03, 1.0), (1300, 0.02, 0.4)]) * 1.6, t0)
    # what was inside rattles
    for i in range(16):
        add(out, lp(click(seed + 100 + i, 0.002, 1200), 4000) * (0.1 + r.random() * 0.15), 0.15 + r.random() * 0.4)
    return room(lp(out, 7000, 2), 0.6, 0.25, 4500)


def tele_on():
    seed = 2400
    dur = 1.6
    n = N(dur)
    out = np.zeros(n, np.float32)
    add(out, ringing(click(seed, 0.002, 600), [(900, 0.02, 1.0), (2200, 0.01, 0.5)]) * 2, 0.02)
    add(out, thump(60, 0.4, seed + 1, 0.9, bend=1.0), 0.08)
    t = np.arange(n) / SR
    whine = np.sin(2 * np.pi * 7800 * t).astype(np.float32) * 0.04 * env(n, [(0, 0), (0.1, 0), (0.3, 1), (1, 0.7)])
    st = bp(white(n, seed + 2), 300, 7000) * env(n, [(0, 0), (0.15, 0), (0.35, 1), (0.7, 0.6), (1, 0)]) * 0.6
    out += whine + st
    return out


def tele_off():
    seed = 2500
    dur = 0.9
    n = N(dur)
    out = np.zeros(n, np.float32)
    add(out, ringing(click(seed, 0.002, 600), [(900, 0.02, 1.0), (2200, 0.01, 0.5)]) * 2, 0.0)
    st = bp(white(n, seed + 1), 300, 7000) * env(n, [(0, 1), (0.4, 0.3), (1, 0)]) * 0.5
    out += dsp.sweep_lowpass(st, 7000, 200)
    add(out, thump(55, 0.3, seed + 2, 0.5), 0.05)
    return out


def radio():
    seed = 2600
    dur = 6.0
    n = N(dur)
    t = np.arange(n) / SR
    static = bp(white(n, seed), 200, 4500) * (0.5 + 0.3 * np.sin(2 * np.pi * 0.3 * t)).astype(np.float32)
    r = R(seed)
    crackle = np.zeros(n, np.float32)
    for _ in range(80):
        add(crackle, click(seed + _, 0.003, 500) * (0.2 + r.random() * 0.6), r.random() * dur)
    whistle = np.sin(2 * np.pi * np.cumsum(1800 + 600 * np.sin(2 * np.pi * 0.17 * t)) / SR).astype(np.float32) * 0.02
    # inside the static, far away, a child humming the music box's lullaby (a closed-mouth 'mmm')
    hum = np.zeros(n, np.float32)
    tt = 1.0
    for i, (semi, beats) in enumerate(LULLABY[:9]):
        d = beats * 0.42
        f = 440.0 * 2 ** (semi / 12)
        v = voice(d, np.array([f, f * 1.01, f * 0.99]), seed + 100 + i, ((300, 1.0), (2500, 0.15)), breath=0.05, vib=0.012)
        add(hum, v * env(len(v), [(0, 0), (0.15, 1), (0.8, 0.8), (1, 0)]), tt)
        tt += d + 0.03
    fade_in = (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t + 1.0)).astype(np.float32)   # it drifts in and out of the static
    out = static * 0.35 + crackle * 0.4 + whistle + bp(hum, 250, 3000) * fade_in * 0.5
    return dsp.drive(bp(out, 200, 4500), 1.3)


def llave_luz():
    seed = 2700
    out = np.zeros(N(0.25), np.float32)
    add(out, ringing(click(seed, 0.0015, 1500), [(3200, 0.01, 1.0), (5200, 0.006, 0.6), (1800, 0.015, 0.4)]) * 3, 0.01)
    add(out, ringing(click(seed + 1, 0.0015, 1500), [(2600, 0.01, 1.0), (4400, 0.006, 0.5)]) * 1.6, 0.045)
    return room(out, 0.25, 0.12, 6000)


def zumbido():
    seed = 2800
    dur = 2.0
    n = N(dur)
    t = np.arange(n) / SR
    hum = (np.sign(np.sin(2 * np.pi * 100 * t)) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.3).astype(np.float32)
    hum = bp(hum, 90, 3000) * (0.4 + 0.6 * (lp(white(n, seed), 8) * 20 > -0.3)).astype(np.float32)
    r = R(seed)
    arcs = np.zeros(n, np.float32)
    for _ in range(25):
        add(arcs, hp(click(seed + _, 0.004, 2500), 2500) * (0.3 + r.random() * 0.7), r.random() * dur)
    out = hum * 0.6 + lp(arcs, 7000) * 0.2
    return out * env(n, [(0, 0), (0.05, 1), (0.85, 1), (1, 0)])


def maquina_coser():
    seed = 2900
    dur = 3.0
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = R(seed)
    t0 = 0.05
    speed = 6.0
    while t0 < dur - 0.2:
        speed = min(13.0, speed * 1.04)
        c = ringing(click(seed + int(t0 * 3000), 0.002, 500), [(1250, 0.02, 1.0), (2400, 0.012, 0.5), (600, 0.03, 0.4)]) * 2
        add(out, c * (0.6 + r.random() * 0.3), t0)
        t0 += 1.0 / speed
    for tt in np.arange(0.1, dur - 0.3, 0.48):
        add(out, thump(70, 0.25, seed + int(tt * 100), 0.6), tt)       # the treadle
    belt = bp(white(n, seed + 7), 300, 1200) * 0.08 * env(n, [(0, 0), (0.1, 1), (0.9, 1), (1, 0)])
    return room(out + belt, 0.4, 0.15, 5000)


def puerta_lenta():
    seed = 3000
    dur = 4.6
    out = np.zeros(N(dur), np.float32)
    # PuertaLenta: it moves a hand's width (ticks 4-26) and, after a pause, all the way (ticks 40-84)
    add(out, creak(1.1, 820, seed, 0.7), 0.2)
    long = creak(2.2, 700, seed + 1, 1.0)
    long2 = creak(2.2, 1150, seed + 2, 0.45)
    add(out, long + long2, 2.0)
    add(out, thump(110, 0.25, seed + 3, 0.3), 4.25)   # it touches the wall
    return room(out, 0.8, 0.25, 4500)


def cuadro():
    seed = 3100
    out = np.zeros(N(0.8), np.float32)
    n = N(0.45)
    scr = bp(white(n, seed), 800, 4000) * env(n, [(0, 0), (0.2, 1), (0.7, 0.6), (1, 0)])
    add(out, scr * 0.6, 0.02)
    add(out, creak(0.3, 1900, seed + 1, 0.4), 0.1)
    return room(out, 0.4, 0.15, 5000)


def objeto(v):
    seed = 3200 + v * 9
    out = np.zeros(N(0.5), np.float32)
    add(out, thump(140 + v * 30, 0.2, seed, 1.0, bend=0.3), 0.01)
    flap = bp(white(N(0.12), seed + 1), 600, 3000) * env(N(0.12), [(0, 0), (0.1, 1), (1, 0)])
    add(out, flap * 0.4, 0.02)
    return room(out, 0.3, 0.12, 5000)


def vidrio(v):
    seed = 3300 + v * 13
    dur = 0.9
    out = np.zeros(N(dur), np.float32)
    add(out, hp(click(seed, 0.008, 1500), 1500) * 0.5, 0.01)
    r = R(seed)
    for i in range(34):
        f = 2200 + r.random() * 5500
        add(out, ringing(click(seed + 10 + i, 0.002, 1500), [(f, 0.08 + r.random() * 0.2, 1.0), (f * 1.53, 0.05, 0.4)]) * (30 + r.random() * 30),
            0.01 + r.random() ** 2 * 0.5)
    return room(out, 0.4, 0.18, 8000)


# ------------------------------------------------------------------ table + build
# event -> (variant renderers, peak dBFS, trim leading/trailing silence?)
EVENTS = {
    'polter.pasos_arriba': ([lambda: pasos_arriba(0), lambda: pasos_arriba(1), lambda: pasos_arriba(2)], -2.0, True),
    'polter.golpe': ([lambda: golpe(0), lambda: golpe(1), lambda: golpe(2)], -1.5, True),
    'polter.palmadas': ([palmadas], -1.0, True),
    'polter.risita': ([lambda: risita(0), lambda: risita(1)], -2.0, True),
    'polter.caja_musica': ([caja_musica], -2.0, True),
    'polter.dentadura': ([lambda: dentadura(0), lambda: dentadura(1)], -1.0, True),
    'polter.susurro': ([lambda: susurro(0), lambda: susurro(1)], -2.0, True),
    'polter.respira': ([lambda: respira(0), lambda: respira(1)], -1.0, True),
    'polter.rezo_reves': ([rezo_reves], -2.0, True),
    'polter.rasguno_puerta': ([lambda: rasguno_puerta(0), lambda: rasguno_puerta(1)], -2.0, True),
    'polter.telefono_ring': ([telefono_ring], -1.5, True),
    'polter.telefono_respira': ([telefono_respira], -2.0, True),
    'polter.llanto_rejilla': ([llanto_rejilla], -2.0, True),
    'polter.picaporte': ([lambda: picaporte(0), lambda: picaporte(1)], -2.0, True),
    'polter.heladera': ([heladera], -3.0, True),
    'polter.papel': ([papel], -3.0, True),
    'polter.canilla': ([canilla], -3.0, True),
    'polter.canilla_sangre': ([canilla_sangre], -2.0, True),
    'polter.persianas': ([persianas], -1.0, True),
    'polter.persiana': ([persiana], -2.0, True),
    'polter.mecedora': ([mecedora], -1.5, False),
    'polter.cajon': ([lambda: cajon(0), lambda: cajon(1)], -3.0, True),
    'polter.cajones': ([cajones], -1.0, True),
    'polter.tele_on': ([tele_on], -2.0, True),
    'polter.tele_off': ([tele_off], -3.0, True),
    'polter.radio': ([radio], -3.0, True),
    'polter.llave_luz': ([llave_luz], -3.0, True),
    'polter.zumbido': ([zumbido], -3.0, True),
    'polter.maquina_coser': ([maquina_coser], -2.0, True),
    'polter.puerta_lenta': ([puerta_lenta], -1.5, False),
    'polter.cuadro': ([cuadro], -3.0, True),
    'polter.objeto': ([lambda: objeto(0), lambda: objeto(1)], -2.0, True),
    'polter.vidrio': ([lambda: vidrio(0), lambda: vidrio(1)], -1.5, True),
}


def rel_paths(name):
    n = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if n > 1 else '') for i in range(n)]


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    report = {}
    for name, (fns, pk, trim) in EVENTS.items():
        rels = rel_paths(name)
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        assert not SOUNDS[name][3], f'{name}: no streams here'
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            raw = np.asarray(fn(), np.float32)
            assert raw.ndim == 1, rel + ' is positional: must be mono'
            x = dsp.master(dsp.trim(raw, -62.0, 0.08) if trim else raw, pk)
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
    print(f'polter group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
