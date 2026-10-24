# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "set pieces" (C): the acts of Casa Morales (docs/design/casa_terror.md 2). Nobody speaks:
wood, metal, china, a child humming far away on an AM band.

Run from the repo root:  python3 tools/audio/snd_setpieces.py [substring ...]

  sp.cerrojo        an old front-door deadbolt turned from inside: the key's teeth, a dry grinding turn, the heavy
                    bolt clunking home in the frame (~1 s). Played twice, a beat apart, before the Nona opens.
  sp.puerta_cruje   a heavy old door swinging open by itself, slowly: the latch, a long stick-slip hinge creak that
                    rises and sags, the air of the hall, a soft knock against the stop (~3 s).
  sp.cubiertos (3)  the silent dinner: a fork scraping china, knife and fork clinking, a cup set down on its saucer.
  sp.radio_cuna     12 s LOOP for the car radio (stream): AM static, and through it, coming and going like a far
                    station at night, a small child humming a lullaby in a minor key (no words).
  sp.asiento        the back seat of an old car taking someone's weight: leather squeak, tired springs, cloth.

All MONO (positional). Review: spectrogram PNG per file in <work>/audio/setpieces.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402
import snd_car  # noqa: E402  (loop-safe helpers and the radio static bed)

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', os.path.join(WORK, 'audio/setpieces'))
TWO_PI = 2 * np.pi


def N(sec):
    return max(1, int(round(sec * SR)))


def T(n):
    return np.arange(n) / SR


def R(seed):
    return np.random.default_rng(seed)


def add(buf, x, t):
    i = int(round(t * SR))
    if i >= len(buf):
        return buf
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i]
    return buf


def modal(dur, modes, seed, exc_ms=3.0, bright=6000.0):
    """A struck object: an excitation burst ringing a bank of decaying partials (freq, decay/s, amp)."""
    n = N(dur)
    t = T(n)
    r = R(seed)
    exc = r.standard_normal(N(exc_ms / 1000.0)) * np.hanning(N(exc_ms / 1000.0))
    y = np.zeros(n)
    for f, dec, a in modes:
        f2 = f * (1 + r.uniform(-0.01, 0.01))
        y += a * np.exp(-t * dec) * np.sin(TWO_PI * f2 * t + r.uniform(0, TWO_PI))
    hit = np.zeros(n)
    hit[:len(exc)] = exc
    y = y * 0.7 + dsp.lowpass(hit.astype(np.float32), bright) * 0.6
    return y.astype(np.float32)


def scrape(dur, seed, lo, hi, rate=(25, 60), squeal=None):
    """Friction: band noise chopped by an irregular stick-slip rate, optionally with a resonant squeal."""
    n = N(dur)
    r = R(seed)
    noise = dsp.bandpass(r.standard_normal(n).astype(np.float32), lo, hi)
    f = np.interp(np.arange(n), np.linspace(0, n, 8), r.uniform(rate[0], rate[1], 8))
    ph = TWO_PI * np.cumsum(f) / SR
    chop = (0.55 + 0.45 * np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** 0.3)
    y = noise * chop
    if squeal:
        y = dsp.peak(y, squeal, 12.0, 14.0)
    return y.astype(np.float32)


def env(n, pts):
    return dsp.env_points(n, pts)


def room(x, decay=0.8, wet=0.2, damp=5000.0, seed=7):
    return dsp.reverb(x, decay, wet, damp, 0.012, seed)


# ====================================================================== the front door
def cerrojo():
    dur = 1.15
    y = np.zeros(N(dur), np.float32)
    # the key's teeth finding the pins: three small metal ticks
    for k, t0 in enumerate((0.0, 0.07, 0.12)):
        tick = modal(0.06, ((3400, 90, 1.0), (5200, 120, 0.5), (7100, 160, 0.3)), 10 + k, exc_ms=1.5, bright=9000)
        add(y, tick * (0.35 + 0.1 * k), t0)
    # the turn: dry metal grinding against metal, a rasp that catches
    g = scrape(0.32, 21, 900, 4800, rate=(40, 95), squeal=2300) * env(N(0.32), ((0, 0), (0.15, 1), (0.8, 0.9), (1, 0)))
    add(y, g * 0.45, 0.2)
    # the bolt slides home: a short rumble of iron in the frame, and the clunk
    slide = dsp.bandpass(R(22).standard_normal(N(0.14)).astype(np.float32), 200, 1400) * env(N(0.14), ((0, 0), (0.3, 1), (1, 0.6)))
    add(y, slide * 0.4, 0.5)
    clunk = modal(0.5, ((95, 14, 1.0), (180, 18, 0.7), (640, 22, 0.35), (1150, 30, 0.25), (2050, 45, 0.15)), 23, exc_ms=5, bright=3500)
    add(y, clunk * 1.0, 0.62)
    return room(y, 0.7, 0.18, 4200)


def puerta_cruje():
    dur = 3.2
    n = N(dur)
    y = np.zeros(n, np.float32)
    # the latch lets go
    latch = modal(0.18, ((820, 30, 1.0), (1500, 40, 0.5), (2600, 60, 0.3)), 31, exc_ms=3, bright=5000)
    add(y, latch * 0.3, 0.0)
    # stick-slip creak: impulses at a slowly wandering rate, each ringing the door's wooden body
    r = R(32)
    cdur = 2.6
    cn = N(cdur)
    rate = np.interp(np.arange(cn), np.linspace(0, cn, 9), [38, 55, 70, 62, 85, 110, 96, 70, 45])
    rate *= 1 + 0.06 * np.sin(TWO_PI * 0.9 * T(cn))
    ph = np.cumsum(rate) / SR
    ticks = np.where(np.diff(np.floor(ph), prepend=0) > 0)[0]
    imp = np.zeros(cn, np.float32)
    amp = env(cn, ((0, 0.0), (0.08, 0.7), (0.35, 1.0), (0.6, 0.75), (0.85, 0.9), (1.0, 0.0)))
    pulse = np.hanning(9).astype(np.float32)
    for i in ticks:
        j = min(cn, i + len(pulse))
        imp[i:j] += pulse[:j - i] * amp[i] * r.uniform(0.6, 1.0)
    body = np.zeros(cn, np.float32)
    for f, q, g in ((420, 9, 1.0), (980, 12, 0.7), (1850, 14, 0.45), (3100, 16, 0.25)):
        body += dsp.peak(dsp.bandpass(imp, f * 0.7, f * 1.4), f, 9.0, q) * g
    body = dsp.lowpass(body, 5200)
    body = body / (np.max(np.abs(body)) + 1e-9)
    add(y, body * 0.9, 0.12)
    # the air of the hall moving as the door swings
    air = dsp.bandpass(R(33).standard_normal(N(2.6)).astype(np.float32), 120, 900) * env(N(2.6), ((0, 0), (0.4, 1), (1, 0)))
    add(y, air * 0.12, 0.2)
    # it comes to rest against the stop
    stop = modal(0.4, ((140, 16, 1.0), (330, 22, 0.6), (760, 30, 0.25)), 34, exc_ms=6, bright=2500)
    add(y, stop * 0.25, 2.75)
    return room(y, 1.1, 0.22, 4500)


# ====================================================================== the silent dinner
CHINA = ((2780, 9, 1.0), (4630, 11, 0.6), (6150, 14, 0.35), (8200, 18, 0.2))


def cubiertos(v):
    if v == 0:
        # a fork drawn across a plate, then a small clink as it is set down
        dur = 1.0
        y = np.zeros(N(dur), np.float32)
        s = scrape(0.34, 41, 2500, 9000, rate=(18, 34), squeal=3600) * env(N(0.34), ((0, 0), (0.2, 1), (0.85, 0.7), (1, 0)))
        add(y, s * 0.55, 0.0)
        add(y, modal(0.6, CHINA, 42, exc_ms=1.2, bright=9000) * 0.5, 0.42)
        return room(y, 0.6, 0.16, 6000)
    if v == 1:
        # knife and fork: a cut against the china, two clinks
        dur = 1.1
        y = np.zeros(N(dur), np.float32)
        s = scrape(0.2, 43, 3000, 9500, rate=(30, 50), squeal=4100) * env(N(0.2), ((0, 0), (0.3, 1), (1, 0)))
        add(y, s * 0.45, 0.0)
        add(y, modal(0.5, CHINA, 44, exc_ms=1.0, bright=9500) * 0.45, 0.24)
        steel = ((3900, 12, 1.0), (6100, 16, 0.5), (8800, 22, 0.25))
        add(y, modal(0.4, steel, 45, exc_ms=0.8, bright=10000) * 0.35, 0.33)
        add(y, modal(0.5, CHINA, 46, exc_ms=1.0, bright=9000) * 0.3, 0.58)
        return room(y, 0.6, 0.16, 6000)
    # a cup set down on its saucer
    dur = 1.0
    y = np.zeros(N(dur), np.float32)
    knock = modal(0.3, ((420, 28, 1.0), (980, 34, 0.5)), 47, exc_ms=4, bright=3000)
    add(y, knock * 0.45, 0.0)
    cup = ((2150, 10, 1.0), (3700, 13, 0.55), (5600, 17, 0.3))
    add(y, modal(0.7, cup, 48, exc_ms=1.5, bright=8000) * 0.5, 0.005)
    add(y, modal(0.4, CHINA, 49, exc_ms=1.0, bright=8000) * 0.2, 0.06)
    return room(y, 0.6, 0.16, 6000)


# ====================================================================== the car radio
# A small original lullaby in A minor (MIDI notes, beats). 12 s at 50 bpm = 10 beats; the phrase ends on a rest so
# the loop seam falls in the silence between two hummed phrases.
MELODY = [(69, 1.0), (72, 1.0), (71, 0.75), (69, 0.25), (64, 1.5), (None, 0.5),
          (67, 0.75), (69, 0.25), (67, 0.75), (64, 0.25), (69, 2.0), (None, 1.0)]


def hum_note(freq, dur, seed):
    """A child humming one note through closed lips: fundamental-heavy, nasal, a little unsteady."""
    n = N(dur)
    t = T(n)
    r = R(seed)
    drift = 1 + 0.008 * np.sin(TWO_PI * r.uniform(0.3, 0.6) * t + r.uniform(0, 6)) + 0.006 * np.sin(TWO_PI * 5.2 * t)
    scoop = 1 - 0.03 * np.exp(-t * 18)  # a child slides up into the note
    f = freq * drift * scoop
    ph = TWO_PI * np.cumsum(f) / SR
    y = np.zeros(n)
    for h, a in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.09), (5, 0.05)):
        y += a * np.sin(h * ph)
    a = min(0.09, dur * 0.3)
    rel = min(0.18, dur * 0.4)
    e = np.ones(n)
    na, nr = N(a), N(rel)
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return (y * e).astype(np.float32)


def radio_cuna():
    dur = 12.0
    n = N(dur)
    static = np.tile(snd_car.radio_static(), 3)[:n]
    if len(static) < n:
        static = np.pad(static, (0, n - len(static)))
    beat = 60.0 / 50.0
    hum = np.zeros(n, np.float32)
    t0 = 0.35
    for k, (note, beats) in enumerate(MELODY):
        d = beats * beat
        if note is not None:
            f = 440.0 * 2 ** ((note - 69) / 12.0)
            add(hum, hum_note(f, d * 1.02, 60 + k), t0)
        t0 += d
    # a breath before the phrase comes round again
    br = dsp.bandpass(R(70).standard_normal(N(0.35)).astype(np.float32), 600, 3500) * env(N(0.35), ((0, 0), (0.5, 1), (1, 0)))
    add(hum, br * 0.06, dur - 0.5)
    # the AM band: nasal, narrow, a little distorted, the station drifting in and out (whole cycles: seamless)
    hum = snd_car.circ_filter(hum, 330, 2600, peaks=((300, 6, 2), (2400, 3, 3)))
    hum = dsp.drive(hum * 1.5, 1.6)
    t = T(n)
    drift = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(TWO_PI * t / dur - 1.2)) * (0.6 + 0.4 * np.sin(TWO_PI * 3 * t / dur))
    flutter = 1 + 0.12 * np.sin(TWO_PI * 7 * t / dur * 4)
    y = static * 0.55 + hum * 0.38 * drift * flutter
    return dsp.bitcrush(y.astype(np.float32), 10, 2)


# ====================================================================== the back seat
def asiento():
    dur = 1.1
    y = np.zeros(N(dur), np.float32)
    # leather taking the weight: a low squeak with stick-slip in it
    sq = scrape(0.45, 81, 350, 2600, rate=(70, 140), squeal=900) * env(N(0.45), ((0, 0), (0.2, 1), (0.7, 0.6), (1, 0)))
    add(y, sq * 0.55, 0.05)
    # the tired springs underneath
    springs = modal(0.9, ((190, 6, 1.0), (430, 8, 0.6), (770, 11, 0.35), (1320, 16, 0.2)), 82, exc_ms=8, bright=2200)
    add(y, springs * 0.45, 0.12)
    # cloth
    cloth = dsp.bandpass(R(83).standard_normal(N(0.5)).astype(np.float32), 1500, 7000) * env(N(0.5), ((0, 0), (0.3, 1), (1, 0)))
    add(y, cloth * 0.12, 0.25)
    return room(y, 0.35, 0.1, 5000)


# ====================================================================== registry / build
EVENTS = [
    # name, renderers (one per variant), peak dBFS, loop
    ('sp.cerrojo', [cerrojo], -1.5, False),
    ('sp.puerta_cruje', [puerta_cruje], -2.0, False),
    ('sp.cubiertos', [lambda: cubiertos(0), lambda: cubiertos(1), lambda: cubiertos(2)], -4.0, False),
    ('sp.radio_cuna', [radio_cuna], -6.0, True),
    ('sp.asiento', [asiento], -3.0, False),
]


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    for name, fns, peak_db, loop in EVENTS:
        if only and not any(s in name for s in only):
            continue
        assert name in SOUNDS and SOUNDS[name][0] == len(fns), f'{name}: variants must match sounds_def'
        for i, fn in enumerate(fns):
            raw = np.asarray(fn(), np.float32)
            assert raw.ndim == 1, f'{name} must be mono'
            x = snd_car.loop_master(raw, peak_db) if loop else dsp.master(dsp.trim(raw, -60.0, 0.06), peak_db)
            rel = name.replace('.', '/') + (f'_{i + 1}' if len(fns) > 1 else '')
            dsp.save_ogg(x, rel)
            try:
                dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '_') + '.png'))
            except Exception:  # noqa: BLE001 (review images are optional)
                pass
            print(f'{rel:24s} {dsp.analyse(x)}', flush=True)


if __name__ == '__main__':
    build(sys.argv[1:] or None)
