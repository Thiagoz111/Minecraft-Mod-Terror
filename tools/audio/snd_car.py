# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "car": the hunter's old 1970s sedan (docs/design/casa_terror.md 6.9).

Run from the repo root:  python3 tools/audio/snd_car.py [substring ...]

All MONO (positional, they follow the car). Loops are built circularly (impulse trains placed modulo the loop length,
noise and filters applied in the frequency domain), so they repeat without a seam; CarSounds (client) sets their
pitch/volume by speed.

  car.engine_start   ~2.6 s: key, a tired starter motor cranking (rrr-rrr-rrr), the engine catches, revs and settles.
  car.idle           2.25 s loop: a four-cylinder at ~800 rpm (27 firings/s), uneven, valve tick, exhaust burble.
  car.rev            1.5 s loop: the same engine at ~2400 rpm under load (80 firings/s); pitched 0.6-1.65 in game.
  car.door_open      latch clack + a dry hinge creak.
  car.door_close     a heavy steel door: thump, latch, loose trim rattling.
  car.horn           an old two-tone horn (a nasal minor third), ~0.9 s.
  car.radio_static   4 s loop: AM static, crackle, a drifting heterodyne whistle, fading in and out.
  car.gravel         1.6 s loop: tyres crunching gravel/dirt with the low road rumble under it.
  car.bump           a collision: body thud, a metal clang, trim rattle.
  car.lights         the headlight switch: two plastic clicks.
"""
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402

TWO_PI = 2 * np.pi


def N(dur):
    return dsp.n_of(dur)


def taxis(n):
    return np.arange(n) / SR


# ------------------------------------------------------------------ circular (loop-safe) tools
def circ_filter(x, lo=None, hi=None, peaks=()):
    """Band-limit + resonant peaks in the frequency domain (circular: the loop seam stays clean)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 8)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 8)
    for fc, gain_db, q in peaks:
        bw = fc / q
        g *= 1 + (10 ** (gain_db / 20) - 1) * np.exp(-0.5 * ((f - fc) / bw) ** 2)
    return np.fft.irfft(X * g, n).astype(np.float32)


def circ_place(n, times, pulse, amps):
    """Places `pulse` at the given sample times (wrapping round the end)."""
    y = np.zeros(n, np.float32)
    L = len(pulse)
    for t, a in zip(times, amps):
        t = int(t) % n
        end = t + L
        if end <= n:
            y[t:end] += pulse * a
        else:
            k = n - t
            y[t:] += pulse[:k] * a
            y[:L - k] += pulse[k:] * a
    return y


def circ_noise(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def loop_master(x, peak_db):
    """dsp.master on three tiled periods, keeping the middle: no fade touches the seam."""
    L = len(x)
    return dsp.master(np.tile(x, 3), peak_db)[L:2 * L].copy()


# ------------------------------------------------------------------ engine
def firing_pulse(rate, seed, bright=1.0):
    """One combustion/exhaust pulse: a pressure kick that rings the exhaust pipe."""
    dur = min(0.08, 2.2 / rate)
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    kick = np.exp(-t * (90 + 40 * bright)) * np.sin(TWO_PI * (55 + 30 * bright) * t)
    pipe = np.exp(-t * 60) * np.sin(TWO_PI * r.uniform(150, 175) * t) * 0.45
    hiss = r.standard_normal(n) * np.exp(-t * 300) * 0.25 * bright
    return (kick + pipe + hiss).astype(np.float32)


def engine_loop(dur, rate, seed, irregular=0.12, bright=1.0, load=0.0):
    """A four-cylinder as a circular train of firings: `rate` firings per second (dur * rate must be whole)."""
    n = N(dur)
    r = dsp.rng(seed)
    count = int(round(dur * rate))
    period = n / count
    times, amps = [], []
    for k in range(count):
        cyl = k % 4
        jitter = r.normal(0, irregular * 0.25) * period
        amp = (1.0 + (0.18 if cyl == 2 else 0.0) - (0.25 if cyl == 3 and irregular > 0.1 else 0.0)) * r.uniform(1 - irregular, 1 + irregular * 0.5)
        times.append(k * period + jitter)
        amps.append(amp)
    pulse = firing_pulse(rate, seed, bright)
    body = circ_place(n, times, pulse, amps)
    # valve train: a light tick at twice the cam rate
    tick = (np.exp(-taxis(N(0.006)) * 1400) * circ_noise(N(0.006), seed + 1)).astype(np.float32)
    ticks = circ_place(n, [k * period * 0.5 + r.uniform(0, 30) for k in range(count * 2)], tick, [0.08 + 0.05 * r.random() for _ in range(count * 2)])
    ticks = circ_filter(ticks, 2200, 6000) * 0.5
    # intake / exhaust roar under load
    roar = circ_filter(circ_noise(n, seed + 2), 70, 900 + 600 * load) * (0.05 + 0.25 * load)
    y = circ_filter(body, 28, 1800 + 900 * bright, peaks=((rate * 1.0, 6, 3), (165, 4, 4), (340, 3, 5)))
    y = y + ticks + roar
    # the fan belt's faint squeal
    t = taxis(n)
    belt_f = round(1900 * dur) / dur
    y += (np.sin(TWO_PI * belt_f * t) * (0.006 + 0.004 * np.sin(TWO_PI * t / dur))).astype(np.float32)
    y = dsp.drive(y * 1.4, 1.3)
    # drive adds harmonics: tame them again (circularly, the loop stays seamless)
    return circ_filter(y, 25, 2600 + 1200 * load, peaks=((rate * 2.0, 3, 3),))


def idle():
    return engine_loop(2.25, 800 / 60 * 2, 11, irregular=0.16, bright=0.8, load=0.0)


def rev():
    return engine_loop(1.5, 2400 / 60 * 2, 12, irregular=0.06, bright=1.3, load=0.7)


def engine_start():
    """Key click, starter cranking with compression stalls, the catch, a blip of throttle, settling to idle."""
    r = dsp.rng(21)
    parts = []
    key = dsp.highpass(dsp.noise(0.012, 'white', 22), 1800) * np.exp(-taxis(N(0.012)) * 400)
    parts.append((key.astype(np.float32), 0.0, 0.35))
    # starter: an electric whine whose speed sags on each compression stroke
    crank_dur = 1.15
    n = N(crank_dur)
    t = taxis(n)
    comp = 0.5 + 0.5 * np.cos(TWO_PI * 3.4 * t)          # 3.4 compressions per second
    spd = 1.0 - 0.35 * comp ** 3
    f = 115 * spd * np.minimum(1, t / 0.08 + 0.4)
    ph = TWO_PI * np.cumsum(f) / SR
    whine = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sign(np.sin(3 * ph))) * 0.35
    gear = dsp.bandpass(dsp.noise(crank_dur, 'white', 23), 900, 3500) * (0.12 + 0.1 * comp)
    chug = np.sin(TWO_PI * 52 * t) * comp ** 4 * 0.6
    crank = (whine + gear + chug) * np.minimum(1, t / 0.03) * np.minimum(1, (crank_dur - t) / 0.06 + 0.2)
    parts.append((crank.astype(np.float32), 0.08, 0.55))
    # the catch: firing accelerating to a blip (~2600 rpm) then dropping to idle
    run_dur = 1.55
    n2 = N(run_dur)
    t2 = taxis(n2)
    rpm = np.interp(t2, [0, 0.12, 0.42, 0.8, 1.55], [300, 1500, 2600, 1100, 800])
    rate = rpm / 60 * 2
    phase = np.cumsum(rate) / SR
    idx = np.where(np.diff(np.floor(phase)) > 0)[0]
    y = np.zeros(n2 + N(0.1), np.float32)
    for i in idx:
        rr = rate[i]
        p = firing_pulse(rr, int(i) % 97, bright=0.8 + 0.6 * (rr - 26) / 60)
        a = r.uniform(0.75, 1.1) * (0.6 if i < N(0.1) else 1.0)
        y[i:i + len(p)] += p[:len(y) - i] * a
    y = dsp.lowpass(y, 2400)
    roar = dsp.lowpass(dsp.noise(run_dur + 0.1, 'pink', 24), 700) * 0.18 * np.interp(taxis(len(y)), [0, 0.42, 0.9, 1.6], [0.2, 1.0, 0.3, 0.2])
    run = dsp.drive((y + roar.astype(np.float32)) * 1.6, 1.5)
    run *= np.minimum(1, (len(run) - np.arange(len(run))) / N(0.25))
    parts.append((run.astype(np.float32), 0.08 + crank_dur - 0.05, 0.9))
    return dsp.mix(*parts)


# ------------------------------------------------------------------ doors, horn, bumps, switch
def modal(exc, modes, tail):
    n = len(exc) + N(tail)
    t = taxis(N(tail))
    ir = np.zeros(N(tail))
    for f, d, a in modes:
        ir += a * np.sin(TWO_PI * f * t) * np.exp(-d * t)
    return signal.fftconvolve(exc, ir)[:n].astype(np.float32)


def latch(seed, bright=1.0):
    exc = dsp.noise(0.004, 'white', seed) * np.exp(-taxis(N(0.004)) * 900)
    return modal(exc, [(1850 * bright, 60, 1.0), (3120 * bright, 90, 0.6), (4700 * bright, 140, 0.3), (980, 45, 0.4)], 0.18)


def creak(dur, seed, f0=520, f1=700):
    """Stick-slip of a dry hinge: a train of slips at a wandering rate, through the door panel's resonances."""
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    rate = np.interp(t, [0, dur * 0.3, dur * 0.7, dur], [f0 * 0.6, f0, f1, f0 * 0.8]) * (1 + 0.05 * np.sin(TWO_PI * 7 * t))
    phase = np.cumsum(rate / 4) / SR
    idx = np.where(np.diff(np.floor(phase)) > 0)[0]
    imp = np.zeros(n, np.float32)
    imp[idx] = r.uniform(0.5, 1.0, len(idx))
    y = modal(imp, [(f0 * 2.1, 40, 1.0), (f0 * 3.4, 60, 0.6), (1450, 30, 0.4), (2600, 80, 0.25)], 0.08)[:n]
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    return (y * env).astype(np.float32)


def door_open():
    return dsp.mix((latch(31, 1.0), 0.0, 1.0), (creak(0.55, 32), 0.05, 0.55))


def door_close():
    t = taxis(N(0.5))
    thump = np.sin(TWO_PI * (68 * (1 + 0.6 * np.exp(-t * 30))) * t) * np.exp(-t * 14)
    slap = dsp.lowpass(dsp.noise(0.5, 'white', 41), 900) * np.exp(-t * 45) * 0.8
    body = (thump + slap).astype(np.float32)
    rattle_exc = np.zeros(N(0.35), np.float32)
    r = dsp.rng(42)
    for k in range(9):
        i = int(r.uniform(0.02, 0.3) * SR)
        rattle_exc[i] = r.uniform(0.2, 0.6) * (1 - i / len(rattle_exc))
    rattle = modal(rattle_exc, [(1230, 70, 1), (2010, 90, 0.7), (3330, 120, 0.4)], 0.06)
    glass = modal(np.array([1.0], np.float32), [(2650, 25, 0.5), (4120, 35, 0.3)], 0.3)
    return dsp.mix((body, 0.0, 1.0), (latch(43, 0.85), 0.012, 0.7), (rattle, 0.02, 0.35), (glass, 0.01, 0.12))


def horn():
    """Two electric horns a minor third apart: buzzy diaphragms through short trumpets (nasal), a little sag."""
    dur = 0.9
    n = N(dur)
    t = taxis(n)
    out = np.zeros(n, np.float32)
    for f0, a in ((415.0, 1.0), (494.0, 0.85)):
        f = f0 * (1 - 0.03 * np.exp(-t * 25)) * (1 + 0.002 * np.sin(TWO_PI * 31 * t))
        ph = TWO_PI * np.cumsum(f) / SR
        buzz = np.tanh(np.sin(ph) * 1.8) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
        out += (buzz * a).astype(np.float32)
    out = dsp.bandpass(out, 300, 3200)
    out = dsp.peak(out, 900, 7, 2.5)
    out = dsp.peak(out, 1750, 4, 3.0)
    env = np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.05)
    return dsp.lowpass(dsp.drive(out * env * 1.1, 1.3), 4000)


def bump():
    t = taxis(N(0.45))
    thud = np.sin(TWO_PI * 55 * t) * np.exp(-t * 16) + dsp.lowpass(dsp.noise(0.45, 'white', 51), 500) * np.exp(-t * 30) * 0.7
    clang = modal(dsp.noise(0.003, 'white', 52), [(410, 22, 1), (1035, 30, 0.6), (1710, 45, 0.5), (2830, 70, 0.3)], 0.5)
    rattle_exc = np.zeros(N(0.3), np.float32)
    r = dsp.rng(53)
    for k in range(12):
        rattle_exc[int(r.uniform(0.01, 0.25) * SR)] = r.uniform(0.2, 0.7)
    rattle = modal(rattle_exc, [(1500, 80, 1), (2400, 100, 0.6)], 0.05)
    return dsp.mix((thud.astype(np.float32), 0.0, 1.0), (clang, 0.004, 0.35), (rattle, 0.02, 0.3))


def lights_click():
    c = modal(dsp.noise(0.002, 'white', 61), [(2900, 300, 1), (5100, 500, 0.5)], 0.03)
    c2 = modal(dsp.noise(0.002, 'white', 62), [(2400, 260, 1), (4300, 420, 0.4)], 0.03)
    return dsp.mix((c, 0.0, 1.0), (c2, 0.045, 0.7))


# ------------------------------------------------------------------ radio + tyres (loops)
def radio_static():
    dur = 4.0
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(71)
    hiss = circ_filter(circ_noise(n, 72), 250, 4200, peaks=((1200, 3, 2),))
    # crackle: sparse clicks and bursts, wrapped round the loop
    clicks = circ_place(n, r.uniform(0, n, 70), (np.exp(-taxis(N(0.003)) * 2500) * circ_noise(N(0.003), 73)).astype(np.float32),
                        r.uniform(0.3, 1.5, 70))
    clicks = circ_filter(clicks, 400, 6000)
    # a heterodyne whistle drifting slowly (whole number of cycles: seamless)
    wob = np.sin(TWO_PI * t / dur) * 0.5 + np.sin(TWO_PI * 2 * t / dur + 1.0) * 0.25
    fw = round(1350 * dur) / dur
    whistle = np.sin(TWO_PI * fw * t + 6 * np.sin(TWO_PI * t / dur)) * (0.04 + 0.04 * (wob > 0.3))
    # the signal fades in and out like a far station at night (periodic envelope)
    fade = 0.65 + 0.35 * np.sin(TWO_PI * t / dur * 2 + 0.4) * np.sin(TWO_PI * t / dur * 3)
    y = (hiss * 0.5 * fade + clicks * 0.6 + whistle).astype(np.float32)
    return dsp.bitcrush(y, 10, 2)


def gravel():
    dur = 1.6
    n = N(dur)
    r = dsp.rng(81)
    grain = (np.exp(-taxis(N(0.004)) * 1500) * circ_noise(N(0.004), 82)).astype(np.float32)
    crunch = circ_place(n, r.uniform(0, n, 900), grain, r.uniform(0.1, 1.0, 900) ** 2)
    crunch = circ_filter(crunch, 900, 7000, peaks=((2400, 4, 2),))
    pops = circ_place(n, r.uniform(0, n, 40), grain, r.uniform(0.8, 1.6, 40))
    pops = circ_filter(pops, 300, 3000)
    rumble = circ_filter(circ_noise(n, 83), 40, 260) * 0.6
    return (crunch * 0.6 + pops * 0.4 + rumble).astype(np.float32)


# ====================================================================== registry / build
EVENTS = [
    # name, renderer, peak dBFS, loop
    ('car.engine_start', engine_start, -2.0, False),
    ('car.idle', idle, -4.0, True),
    ('car.rev', rev, -4.0, True),
    ('car.door_open', door_open, -3.0, False),
    ('car.door_close', door_close, -2.0, False),
    ('car.horn', horn, -1.0, False),
    ('car.radio_static', radio_static, -6.0, True),
    ('car.gravel', gravel, -5.0, True),
    ('car.bump', bump, -2.0, False),
    ('car.lights', lights_click, -6.0, False),
]


def build(only=None):
    for name, fn, peak_db, loop in EVENTS:
        if only and not any(s in name for s in only):
            continue
        assert name in SOUNDS and SOUNDS[name][0] == 1, f'{name} must be a single-variant event in sounds_def'
        raw = np.asarray(fn(), np.float32)
        assert raw.ndim == 1, f'{name} must be mono'
        x = loop_master(raw, peak_db) if loop else dsp.master(dsp.trim(raw, -60.0, 0.06), peak_db)
        rel = name.replace('.', '/')
        dsp.save_ogg(x, rel)
        print(f'{rel:22s} {dsp.analyse(x)}', flush=True)


if __name__ == '__main__':
    build(sys.argv[1:] or None)
