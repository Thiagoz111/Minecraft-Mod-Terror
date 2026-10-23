# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "hunt" (B2: Act 5 of Casa Morales, "Ella escucha todo"; docs/design/casa_terror.md 6.1,
6.2, 6.6, 7).  Nobody speaks: every sound here is a body, a breath, a bone or a scream.

Run from the repo root:  python3 tools/audio/snd_hunt.py [substring ...]

Positional sounds are MONO (they come from her, or from you); the stingers and the heartbeat are heard in the head
(played by the client with forUI / a relative loop) and the chase loop is a stereo music stream.  Loops are built on a
periodic timeline (events placed modulo the loop length, every tone a whole number of cycles, filters and reverb
circular in the frequency domain) so they repeat without a seam.

  hunt.stinger_nona   the broken Nona in your face: a string cluster tearing upward, her shriek, bone, a sub hit
  hunt.stinger_lucia  Lucía: a girl's scream folded over itself, reversed swell into a hit, crushed noise
  hunt.stinger_copia  a copy's smile: grinding teeth, a detuned electric stab, static bursts, a choked click
  hunt.stinger_perro  the long dog: a wet roar from too big a chest, snapping jaws, a body slam
  hunt.stinger_cara   the red face: a ring-modulated demon screech over a metal scrape and a sub drop
  hunt.bone_crack x4  bones breaking and settling (her limbs as she moves; the transformation)
  hunt.neck_twist     ~2 s: the neck grinding round 180 degrees, cartilage popping, a last crunch
  hunt.crawl_tap x4   palms, knuckles and heels slapping the floorboards (the spider crawl)
  hunt.sniff x3       short wet sniffs (she smells for you)
  hunt.hiss x2        a throat hiss with a rattling growl under it (crucifix, salt, lunges)
  hunt.groan x3       an old woman's possessed groan: vocal fry, a second voice an octave under
  hunt.jaw x2         the dentures clacking in the unhinged jaw
  hunt.scream         her shriek when she starts a chase / is burnt by holy water
  hunt.rattle x2      a door handle rattling before she opens it
  hunt.grab           she gets you: a lunge, cloth, a shriek right at your ear, a thud
  hunt.gasp x2        out of air: the desperate inhale after holding the breath
  hunt.breath_in      the sharp intake before holding it (quiet)
  hunt.breath_out     letting it go, shaky (quiet)
  hunt.heartbeat      loop, 4 beats at 70 bpm (the client pitches it up as she comes closer)
  hunt.chase          loop ~15 s, stereo: dissonant strings, a pounding low drum, scrapes; no melody

Review PNGs (waveform + spectrogram) and stats.json go to <WORK>/audio/hunt (tools/workdir.py).
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import json
import os
import sys
import time

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/hunt'))
TWO_PI = 2 * np.pi


# ====================================================================== helpers
def N(sec):
    return max(1, int(round(sec * SR)))


def taxis(n):
    return np.arange(n) / SR


def norm(x, peak=1.0):
    x = np.asarray(x, np.float32)
    return (x / (np.max(np.abs(x)) + 1e-12) * peak).astype(np.float32)


def pshift(x, semis):
    """dsp.pitch_shift, same length as the input."""
    y = dsp.pitch_shift(x, semis)
    out = np.zeros(len(x), np.float32)
    out[:min(len(x), len(y))] = y[:len(x)]
    return out


def add(*xs):
    """Sum of arrays of different lengths (padded with silence)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n, np.float32)
    for x in xs:
        out[:len(x)] += x
    return out


def place(n, items):
    """Sum of (sound, start_seconds, gain) into n samples (sounds running past the end are cut)."""
    out = np.zeros(n, np.float32)
    for x, t, g in items:
        s = int(t * SR)
        if s >= n:
            continue
        seg = x[:n - s]
        out[s:s + len(seg)] += seg * g
    return out


def burst(dur, lo, hi, decay, seed, attack=0.0008):
    """A filtered noise burst with a sharp attack and exponential decay."""
    x = dsp.noise(dur, 'white', seed)
    x = dsp.bandpass(x, lo, hi, 2) if lo else dsp.lowpass(x, hi, 2)
    return (x * dsp.env_exp(N(dur), decay, attack)).astype(np.float32)


def thump(f0, f1, dur, decay, seed=0):
    """A pitched body thump (sine glide with exponential decay)."""
    x = dsp.osc(dsp.glide(f0, f1, dur), dur)
    return (x * dsp.env_exp(N(dur), decay, 0.001)).astype(np.float32)


def resonate(x, freqs, q=12.0, gain=1.0):
    """Adds resonant modes (wood, metal, bone) to an excitation."""
    out = np.zeros_like(x)
    for f in freqs:
        out += dsp.bandpass(x, f / (1 + 1 / q), f * (1 + 1 / q), 2)
    return (x * 0.3 + out * gain).astype(np.float32)


def glottal(f0, n, seed, jitter=0.02, shimmer=0.15, oq=0.55):
    """A rough voice source: Rosenberg-ish pulses at f0 (Hz per sample array or number) with jitter / shimmer."""
    r = dsp.rng(seed)
    f = np.broadcast_to(np.asarray(f0, np.float64), (n,)) if np.ndim(f0) == 0 else np.asarray(f0, np.float64)[:n]
    jit = 1 + jitter * dsp.lowpass(r.standard_normal(n).astype(np.float32), 30, 2) * 6
    ph = np.cumsum(f * jit) / SR
    frac = ph % 1.0
    pulse = np.where(frac < oq, np.sin(np.pi * frac / oq) ** 2, 0.0)
    src = np.diff(pulse, prepend=0.0) * SR / np.maximum(f, 20) * 0.1
    amp = 1 + shimmer * dsp.lowpass(r.standard_normal(n).astype(np.float32), 20, 2) * 5
    return (src * amp).astype(np.float32)


def vowel(src, fm, bw=(80, 110, 160, 200)):
    """Formant filter: resonators at fm (list of Hz)."""
    out = np.zeros_like(src)
    for i, f in enumerate(fm):
        b = bw[min(i, len(bw) - 1)]
        out += dsp.bandpass(src, max(30, f - b), f + b, 2) * (1.0 / (1 + i * 0.35))
    return out.astype(np.float32)


def crackle(dur, density, seed, lo=1500, hi=9000):
    """Dry micro-cracks (cartilage, knuckles) scattered over dur."""
    r = dsp.rng(seed)
    n = N(dur)
    out = np.zeros(n, np.float32)
    k = int(density * dur)
    for i in range(k):
        s = int(r.uniform(0, n - N(0.01)))
        g = burst(0.006, lo, hi, 900, seed * 31 + i) * r.uniform(0.2, 1.0)
        out[s:s + len(g)] += g
    return out


def crack(seed, big=1.0):
    """One bone breaking: a dry snap, a hollow pop, splinters, a wet squelch of tissue."""
    r = dsp.rng(seed)
    snap = burst(0.03, 1800, 9000, 260, seed) * 1.0
    snap = resonate(snap, [r.uniform(2200, 2800), r.uniform(3500, 4300)], 10, 0.8)
    pop = thump(r.uniform(160, 230), 70, 0.12, 45) * 0.8 * big
    split = crackle(0.12, 140, seed + 3) * 0.5
    wet = dsp.bandpass(dsp.noise(0.25, 'pink', seed + 5), 250, 1200, 2)
    wet *= dsp.env_points(N(0.25), [(0, 0), (0.08, 1), (0.4, 0.4), (1, 0)])
    wet = dsp.tremolo(wet, r.uniform(28, 45), 0.8) * 0.45
    return place(N(0.4), [(snap, 0.0, 1.0), (pop, 0.002, 1.0), (split, 0.01, 1.0), (wet, 0.012, big)])


def roomy(x, decay=0.6, wet=0.18, damp=4500.0, seed=11):
    return dsp.reverb(x, decay, wet, damp, 0.008, seed)


# ====================================================================== her body
def bone_crack(seed):
    def fn():
        r = dsp.rng(seed)
        x = crack(seed * 7 + 1, r.uniform(0.7, 1.2))
        if r.random() < 0.7:
            x = place(N(0.7), [(x, 0.0, 1.0), (crack(seed * 7 + 2, 0.6), r.uniform(0.08, 0.22), 0.6)])
        return roomy(x, 0.5, 0.15)
    return fn


def neck_twist():
    dur = 2.1
    n = N(dur)
    r = dsp.rng(201)
    # stick-slip grinding: an irregular pulse train (vertebrae catching and letting go), rising in rate
    rate = dsp.glide(18, 46, dur)
    ph = np.cumsum(rate * (1 + 0.35 * dsp.lowpass(r.standard_normal(n).astype(np.float32), 8, 2) * 4)) / SR
    pulses = (np.diff(np.floor(ph), prepend=0) > 0).astype(np.float32)
    grain = burst(0.012, 300, 3500, 400, 202)
    grind = signal.fftconvolve(pulses, grain)[:n].astype(np.float32)
    grind = resonate(grind, [420, 760, 1250], 6, 1.2)
    grind *= dsp.env_points(n, [(0, 0), (0.05, 0.6), (0.6, 1.0), (0.88, 1.0), (1, 0)])
    pops = crackle(dur, 35, 203, 1200, 7000) * dsp.env_points(n, [(0, 0.3), (1, 1.0)])
    stretch = dsp.bandpass(dsp.noise(dur, 'brown', 204), 90, 600, 2) * dsp.env_points(n, [(0, 0), (0.3, 0.7), (0.9, 1), (1, 0)])
    big = [(crack(205, 1.1), 0.35, 0.45), (crack(206, 0.9), 0.95, 0.45), (crack(208, 0.8), 1.3, 0.4), (crack(207, 1.4), 1.72, 0.8)]
    x = place(n + N(0.4), [(norm(grind), 0, 1.0), (norm(pops), 0, 0.55), (norm(stretch), 0, 0.45)] + big)
    return roomy(x, 0.7, 0.2)


def crawl_tap(seed):
    def fn():
        r = dsp.rng(seed)
        parts = []
        t = 0.0
        for i in range(r.integers(3, 6)):
            # dry contacts on floorboards: a palm slap, a knuckle knock, a nail tick, a heel; quick and uneven
            kind = r.integers(0, 4)
            if kind == 0:
                x = dsp.lowpass(burst(0.04, 150, 3200, 140, seed * 13 + i), 2600, 2)
                x = resonate(x, [r.uniform(170, 230), r.uniform(480, 560)], 3, 0.5)
            elif kind == 1:
                x = resonate(burst(0.03, 300, 4000, 220, seed * 17 + i), [r.uniform(700, 900), 1600], 4, 0.6)
            elif kind == 2:
                x = burst(0.012, 3000, 10000, 900, seed * 19 + i) * 0.8
            else:
                x = dsp.lowpass(burst(0.05, 60, 900, 110, seed * 23 + i), 700, 2) * 1.2
            parts.append((x, t, r.uniform(0.5, 1.0)))
            t += r.uniform(0.025, 0.09)
        return roomy(place(N(t + 0.12), parts), 0.35, 0.1)
    return fn


def sniff(seed):
    def fn():
        r = dsp.rng(seed)
        parts = []
        t = 0.0
        for i in range(r.integers(2, 4)):
            d = r.uniform(0.09, 0.18)
            x = dsp.noise(d, 'white', seed * 5 + i)
            x = dsp.bandpass(x, 1200, 6500, 2)
            x = dsp.peak(x, r.uniform(2400, 3600), 9, 3)
            x *= dsp.env_points(N(d), [(0, 0), (0.15, 1), (0.6, 0.6), (1, 0)])
            # the wet flutter of a nostril
            x = dsp.tremolo(x, r.uniform(55, 80), 0.35)
            parts.append((x, t, r.uniform(0.7, 1.0)))
            t += d + r.uniform(0.02, 0.07)
        return roomy(place(N(t + 0.1), parts), 0.35, 0.12)
    return fn


def hiss(seed):
    def fn():
        r = dsp.rng(seed)
        d = r.uniform(0.9, 1.3)
        n = N(d)
        air = dsp.highpass(dsp.noise(d, 'white', seed), 1800, 2)
        air = dsp.peak(dsp.peak(air, 2800, 8, 2), 5200, 6, 3)
        env = dsp.env_points(n, [(0, 0), (0.06, 1), (0.7, 0.75), (1, 0)])
        rattle = vowel(glottal(dsp.glide(46, 38, d), n, seed + 1, 0.06, 0.4), [420, 900, 2300])
        rattle = dsp.drive(norm(rattle) * 2.5, 2)
        x = air * env + rattle * env * 0.45
        return roomy(x, 0.6, 0.15)
    return fn


def groan(seed):
    def fn():
        r = dsp.rng(seed)
        d = r.uniform(1.8, 2.6)
        n = N(d)
        f0 = dsp.glide(r.uniform(78, 92), r.uniform(58, 70), d) * (1 + 0.04 * np.sin(TWO_PI * 3.3 * taxis(n)))
        src = glottal(f0, n, seed, 0.05, 0.35, 0.45)
        # an 'o' sliding to an 'a', then closing to a hum
        a = vowel(src, [520, 900, 2500, 3300])
        o = vowel(src, [420, 750, 2400, 3200])
        k = dsp.env_points(n, [(0, 1), (0.5, 0.2), (1, 0.6)])
        voice = o * k + a * (1 - k)
        under = pshift(voice, -12) * 0.7       # the second voice an octave under hers
        breath = dsp.bandpass(dsp.noise(d, 'pink', seed + 9), 500, 3500, 2) * 0.25
        env = dsp.env_points(n, [(0, 0), (0.12, 1), (0.75, 0.85), (1, 0)])
        x = dsp.drive(norm(voice + under + breath) * 1.8, 1.6) * env
        return roomy(x, 0.9, 0.22)
    return fn


def jaw(seed):
    def fn():
        r = dsp.rng(seed)
        parts = []
        t = 0.0
        for i in range(r.integers(2, 4)):
            c = resonate(burst(0.015, 2000, 9000, 700, seed * 3 + i), [r.uniform(2600, 3000), r.uniform(4200, 4800)], 14, 1.2)
            c = add(c, resonate(burst(0.02, 400, 2500, 250, seed * 7 + i), [900, 1400], 8, 0.5))
            parts.append((c, t, r.uniform(0.6, 1.0)))
            t += r.uniform(0.05, 0.12)
        slurp = dsp.bandpass(dsp.noise(0.2, 'pink', seed + 40), 300, 2000, 2) * dsp.env_points(N(0.2), [(0, 0), (0.2, 1), (1, 0)])
        parts.append((dsp.tremolo(slurp, 40, 0.7), t, 0.35))
        return roomy(place(N(t + 0.3), parts), 0.4, 0.14)
    return fn


def shriek(seed, d=1.9, base=880, under=-12, harsh=2.4):
    """Her shriek: a strained high voice tearing upward and cracking, with a low voice and a breath layer."""
    r = dsp.rng(seed)
    n = N(d)
    f0 = np.interp(np.arange(n), [0, n * 0.1, n * 0.45, n * 0.8, n], [base * 0.7, base * 1.25, base * 1.55, base * 1.1, base * 0.8])
    f0 = f0 * (1 + 0.025 * np.sin(TWO_PI * 7.5 * taxis(n)) + 0.01 * dsp.lowpass(r.standard_normal(n).astype(np.float32), 40, 2) * 8)
    src = glottal(f0, n, seed, 0.03, 0.4, 0.4)
    v = vowel(src, [1000, 2300, 3200, 4200], (150, 250, 300, 400))
    low = pshift(v, under) * 0.6
    air = dsp.bandpass(dsp.noise(d, 'white', seed + 3), 2500, 9000, 2) * 0.35
    env = dsp.env_points(n, [(0, 0), (0.02, 1), (0.6, 0.9), (1, 0)])
    x = dsp.drive(norm(v + low + air) * harsh, 2.0) * env
    return x.astype(np.float32)


def scream():
    return roomy(shriek(301), 1.4, 0.28)


def rattle(seed):
    def fn():
        r = dsp.rng(seed)
        d = r.uniform(0.55, 0.8)
        n = N(d)
        parts = []
        t = 0.0
        while t < d - 0.05:
            c = resonate(burst(0.02, 1500, 9000, 600, int(t * 1000) + seed), [2150, 3420, 5100], 20, 1.4)
            c = add(c, resonate(burst(0.03, 100, 1200, 120, int(t * 777) + seed), [180, 360], 6, 0.5))
            parts.append((c, t, r.uniform(0.4, 1.0)))
            t += r.uniform(0.03, 0.07)
        return roomy(place(n + N(0.2), parts), 0.5, 0.15)
    return fn


def grab():
    d = 1.6
    whoosh = dsp.bandpass(dsp.noise(0.35, 'pink', 401), 200, 4000, 2) * dsp.env_points(N(0.35), [(0, 0), (0.8, 1), (1, 0)])
    cloth = dsp.bandpass(dsp.noise(0.3, 'white', 402), 1500, 7000, 2) * dsp.env_exp(N(0.3), 9)
    cloth = dsp.tremolo(cloth, 70, 0.8)
    shr = shriek(403, 1.0, 1100, -7, 3.0)
    thud = add(thump(90, 40, 0.4, 12), burst(0.2, 60, 600, 25, 404) * 0.8)
    x = place(N(d), [(whoosh, 0, 0.7), (cloth, 0.25, 0.6), (shr, 0.28, 1.0), (crack(405, 1.2), 0.3, 0.8), (thud, 0.62, 1.0)])
    return roomy(x, 0.8, 0.2)


# ====================================================================== your body
def gasp(seed):
    def fn():
        r = dsp.rng(seed)
        d = 1.0
        n = N(d)
        # a strained, rasping inhale (the vowel of a gasp: an open throat) then a ragged second pull
        inh = dsp.noise(0.55, 'white', seed)
        inh = vowel(inh, [r.uniform(700, 900), 1250, 2600], (200, 300, 500)) + dsp.bandpass(inh, 3000, 5500, 2) * 0.08
        inh = dsp.lowpass(inh, 4500, 2)
        inh *= dsp.env_points(N(0.55), [(0, 0), (0.1, 1), (0.7, 0.9), (1, 0)])
        rasp = vowel(glottal(dsp.glide(160, 220, 0.55), N(0.55), seed + 1, 0.08, 0.6), [800, 1300, 2700]) * 0.25
        second = dsp.noise(0.3, 'white', seed + 2)
        second = dsp.lowpass(vowel(second, [650, 1150, 2500], (200, 300, 500)), 4000, 2) * dsp.env_points(N(0.3), [(0, 0), (0.2, 1), (1, 0)])
        x = place(n, [(inh + rasp * dsp.env_points(N(0.55), [(0, 0), (0.3, 1), (1, 0)]), 0.0, 1.0), (second, 0.62, 0.6)])
        return x
    return fn


def breath_in():
    d = 0.4
    x = dsp.noise(d, 'white', 501)
    x = vowel(x, [900, 1500, 3000], (300, 400, 600)) * dsp.env_points(N(d), [(0, 0), (0.25, 1), (0.6, 0.6), (1, 0)])
    return x


def breath_out():
    d = 0.9
    n = N(d)
    x = dsp.noise(d, 'pink', 502)
    x = vowel(x, [600, 1100, 2400], (250, 350, 500))
    x = dsp.tremolo(x, 9, 0.5)  # shaky
    return x * dsp.env_points(n, [(0, 0), (0.08, 1), (0.6, 0.6), (1, 0)])


# ====================================================================== loops (periodic timelines)
def circ_filter(x, lo=None, hi=None, peaks=()):
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 8)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 8)
    for fc, gain_db, q in peaks:
        bw = fc / q
        g *= 1 + (10 ** (gain_db / 20) - 1) * np.exp(-0.5 * ((f - fc) / bw) ** 2)
    if x.ndim == 2:
        g = g[:, None]
    return np.fft.irfft(X * g, n, axis=0).astype(np.float32)


def circ_place(n, items):
    out = np.zeros(n, np.float32)
    for x, t, g in items:
        s = int(t * SR) % n
        k = min(len(x), n)
        idx = (np.arange(k) + s) % n
        np.add.at(out, idx, x[:k] * g)
    return out


def circ_reverb(x, decay, wet, seed):
    n = len(x)
    r = dsp.rng(seed)
    m = min(n, N(decay * 1.3))
    t = taxis(m)
    ir = r.standard_normal(m) * np.exp(-6.9 * t / decay)
    ir = dsp.lowpass(ir.astype(np.float32), 5000, 2)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    irp = np.zeros(n)
    irp[:m] = ir
    w = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(irp), n)
    return ((1 - wet) * x + wet * w).astype(np.float32)


def periodic(f, L):
    """Nearest frequency with a whole number of cycles in L seconds."""
    return max(1, round(f * L)) / L


def heartbeat():
    bpm = 70.0
    beat = 60.0 / bpm
    L = beat * 4
    n = N(L)
    items = []
    for i in range(4):
        t = i * beat
        lub = add(thump(58, 42, 0.18, 22), burst(0.05, 40, 300, 40, 600 + i) * 0.5)
        dub = add(thump(72, 50, 0.13, 30) * 0.65, burst(0.04, 60, 400, 50, 620 + i) * 0.3)
        items += [(lub, t, 1.0 - 0.06 * (i % 2)), (dub, t + 0.24, 0.85)]
    x = circ_place(n, items)
    x = circ_filter(x, 25, 900)
    return circ_reverb(x, 0.25, 0.1, 601)


def chase():
    bpm = 132.0
    beat = 60.0 / bpm
    L = beat * 32                     # 8 bars of 4: ~14.5 s
    n = N(L)
    t = taxis(n)
    r = dsp.rng(700)
    # ---- strings: a cluster of minor seconds and a tritone, sul ponticello, tremolo bowing, swelling and fading
    cluster = [110.0, 116.54, 155.56, 164.81, 233.08, 246.94, 311.13, 329.63]
    strings = np.zeros((n, 2), np.float32)
    for i, f in enumerate(cluster):
        for det in (-0.004, 0.0, 0.0045):
            fr = periodic(f * (1 + det), L)
            ph = r.uniform(0, TWO_PI)
            saw = 2 * ((fr * t + ph / TWO_PI) % 1.0) - 1
            trem = 0.55 + 0.45 * np.sin(TWO_PI * periodic(r.uniform(9, 13), L) * t + r.uniform(0, TWO_PI))
            swell = 0.5 + 0.5 * np.sin(TWO_PI * periodic(r.uniform(0.13, 0.4), L) * t + r.uniform(0, TWO_PI))
            v = (saw * trem * (0.35 + 0.65 * swell ** 2)).astype(np.float32)
            p = (i / (len(cluster) - 1)) * 1.4 - 0.7
            strings += dsp.pan(v, p) * (0.12 if f < 200 else 0.09)
    strings = circ_filter(strings, 90, 5200, peaks=((2900, 6, 2), (1300, 3, 2)))
    # bow noise (ponticello scratch)
    scratch = circ_filter(np.stack([dsp.rng(701).standard_normal(n), dsp.rng(702).standard_normal(n)], 1).astype(np.float32),
                          2000, 8000) * 0.05
    scratch *= (0.5 + 0.5 * np.sin(TWO_PI * periodic(11.0, L) * t))[:, None]
    # ---- the drum: low toms / a bass drum in a broken pattern, accents off the beat
    pattern = [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0]       # 16ths over two beats, repeated
    drum_items = []
    for k in range(32 * 2):
        step = pattern[k % 16]
        if not step:
            continue
        tt = k * beat / 2
        g = 1.0 if k % 8 == 0 else 0.7
        hit = add(thump(70, 38, 0.5, 9), burst(0.08, 80, 900, 35, 710 + k) * 0.6)
        drum_items.append((hit, tt, g))
    for bar in range(8):
        tt = bar * beat * 4 + beat * 3.5
        drum_items.append((add(thump(95, 42, 0.6, 7), burst(0.15, 60, 1200, 18, 790 + bar)), tt, 1.1))  # the floor tom
    drum = circ_place(n, drum_items)
    drum = circ_filter(drum, 30, 2500)
    # ---- a metal scrape / bowed-cymbal whine every two bars
    scrape_items = []
    for bar in range(0, 8, 2):
        d = 1.6
        sc = dsp.noise(d, 'white', 720 + bar)
        sc = resonate(sc, [1870, 2930, 4410, 5980], 40, 1.5) * dsp.env_points(N(d), [(0, 0), (0.5, 1), (1, 0)])
        scrape_items.append((sc, bar * beat * 4 + beat * 2, 0.25))
    scrape = circ_place(n, scrape_items)
    mono = drum * 0.9 + scrape
    x = strings + scratch + np.stack([mono, mono], 1)
    x = np.stack([circ_reverb(x[:, 0], 1.6, 0.25, 731), circ_reverb(x[:, 1], 1.6, 0.25, 732)], 1)
    return dsp.drive(norm(x) * 1.3, 1.3)


# ====================================================================== stingers (heard in the head)
def sub_hit(seed, f0=55, d=1.2):
    return add(thump(f0 * 1.6, f0 * 0.6, d, 4.5), burst(0.12, 30, 400, 20, seed) * 0.7)


def string_tear(seed, d=1.6, low=600):
    """Strings sforzando tearing upward: a cluster of high bowed saws glissing up, scratchy."""
    r = dsp.rng(seed)
    n = N(d)
    out = np.zeros(n, np.float32)
    for i in range(9):
        f0 = low * 2 ** (r.uniform(0, 1.3))
        fr = dsp.glide(f0, f0 * r.uniform(1.4, 2.2), d)
        v = dsp.osc(fr * (1 + 0.01 * np.sin(TWO_PI * r.uniform(5, 8) * taxis(n))), d, 'saw')
        out += v * r.uniform(0.6, 1.0)
    out = dsp.peak(dsp.bandpass(out, 400, 9000, 2), 3200, 8, 2)
    out += dsp.highpass(dsp.noise(d, 'white', seed + 1), 3000, 2) * 0.4
    return out * dsp.env_points(n, [(0, 0), (0.01, 1), (0.25, 0.8), (1, 0)])


def stinger_nona():
    d = 2.2
    x = place(N(d), [
        (sub_hit(801), 0.0, 1.0),
        (string_tear(802, 1.7, 700), 0.0, 0.8),
        (shriek(803, 1.6, 950, -12, 3.2), 0.02, 1.0),
        (crack(804, 1.4), 0.0, 1.0),
        (crack(805, 1.0), 0.18, 0.7),
    ])
    return roomy(dsp.drive(norm(x) * 1.6, 1.5), 1.6, 0.3, seed=806)


def stinger_lucia():
    d = 2.2
    girl = shriek(811, 1.5, 1250, 5, 2.6)                          # a child's scream, a fifth over itself
    fold = pshift(girl, -5) * 0.5
    swell = dsp.reverse(roomy(burst(0.6, 300, 8000, 4, 812) * 1.5, 1.2, 0.8)) * 0.6
    swell = swell[-N(0.35):]
    crushed = dsp.bitcrush(dsp.bandpass(dsp.noise(1.2, 'white', 813), 800, 9000, 2), 6, 8) * dsp.env_exp(N(1.2), 3.5)
    x = place(N(d), [(swell, 0.0, 0.8), (sub_hit(814, 60), 0.35, 1.0), (girl, 0.35, 1.0), (fold, 0.36, 1.0), (crushed, 0.35, 0.4)])
    return roomy(dsp.drive(norm(x) * 1.5, 1.4), 1.4, 0.25, seed=815)


def stinger_copia():
    d = 2.0
    r = dsp.rng(820)
    # grinding teeth: dense micro-clicks through enamel resonances
    grind = resonate(crackle(1.4, 260, 821, 1500, 8000), [2900, 4100, 5600], 12, 1.0) * dsp.env_points(N(1.4), [(0, 0.2), (0.3, 1), (1, 0)])
    # a detuned electric stab (a smile too wide: a major chord pulled out of tune)
    stab = np.zeros(N(1.2), np.float32)
    for f in (220, 277.2, 329.6, 440, 466.2):
        stab += dsp.osc(f * (1 + r.uniform(-0.02, 0.02)), 1.2, 'square') * 0.2
    stab = dsp.bitcrush(dsp.lowpass(stab, 3500, 2), 5, 6) * dsp.env_exp(N(1.2), 2.5)
    static = np.zeros(N(d), np.float32)
    for i in range(7):
        s = burst(r.uniform(0.03, 0.12), 500, 9000, 10, 830 + i)
        static = place(N(d), [(static, 0, 1.0), (s, r.uniform(0, 1.2), r.uniform(0.4, 0.9))])
    click = burst(0.02, 1000, 6000, 300, 840)
    x = place(N(d), [(sub_hit(841, 48), 0.0, 1.0), (stab, 0.0, 0.8), (grind, 0.05, 0.9), (static, 0, 0.6), (click, 1.25, 0.8)])
    return roomy(dsp.drive(norm(x) * 1.6, 1.5), 1.0, 0.22, seed=842)


def stinger_perro():
    d = 2.2
    n = N(1.6)
    # a roar from a chest too big: a low growling voice with fry, huge formants, distorted
    f0 = dsp.glide(95, 55, 1.6) * (1 + 0.06 * np.sin(TWO_PI * 23 * taxis(n)))
    roar = vowel(glottal(f0, n, 851, 0.08, 0.6, 0.35), [300, 650, 1800, 2600], (120, 160, 250, 300))
    roar = dsp.drive(norm(roar + pshift(roar, -7) * 0.6) * 3, 2.5) * dsp.env_points(n, [(0, 0), (0.03, 1), (0.6, 0.8), (1, 0)])
    wet = dsp.tremolo(dsp.bandpass(dsp.noise(1.6, 'pink', 852), 200, 2500, 2), 32, 0.9) * 0.4
    snaps = place(N(0.6), [(resonate(burst(0.03, 1000, 8000, 300, 853 + i), [1800, 3000], 10, 1.0), i * 0.11, 1.0) for i in range(4)])
    slam = add(thump(80, 35, 0.6, 7), burst(0.25, 40, 1500, 14, 860))
    x = place(N(d), [(slam, 0.0, 1.0), (roar, 0.01, 1.0), (wet, 0.05, 1.0), (snaps, 0.9, 0.7)])
    return roomy(dsp.drive(norm(x) * 1.5, 1.4), 1.2, 0.22, seed=861)


def stinger_cara():
    d = 2.2
    n = N(1.7)
    hi = shriek(871, 1.7, 1400, -19, 3.5)
    ringed = dsp.ring(hi, 137.0) * 0.8
    lo = vowel(glottal(dsp.glide(70, 45, 1.7), n, 872, 0.1, 0.5), [400, 800, 2200]) * 1.2
    scrape = resonate(dsp.noise(1.2, 'white', 873), [1660, 2490, 3730, 5100], 35, 1.5) * dsp.env_points(N(1.2), [(0, 0), (0.05, 1), (1, 0)])
    drop = thump(120, 28, 1.6, 2.8)
    x = place(N(d), [(drop, 0.0, 1.0), (hi, 0.0, 0.9), (ringed, 0.0, 0.7), (lo, 0.0, 0.8), (scrape, 0.04, 0.4), (crack(874, 1.0), 0.0, 0.8)])
    return roomy(dsp.drive(norm(x) * 1.7, 1.6), 1.6, 0.3, seed=875)


# ====================================================================== registry / build
EVENTS = {
    # name: ([renderers per variant], peak dBFS, loop)
    'hunt.stinger_nona': ([stinger_nona], -0.8, False),
    'hunt.stinger_lucia': ([stinger_lucia], -0.8, False),
    'hunt.stinger_copia': ([stinger_copia], -0.8, False),
    'hunt.stinger_perro': ([stinger_perro], -0.8, False),
    'hunt.stinger_cara': ([stinger_cara], -0.8, False),
    'hunt.bone_crack': ([bone_crack(s) for s in (1, 2, 3, 4)], -2.0, False),
    'hunt.neck_twist': ([neck_twist], -1.5, False),
    'hunt.crawl_tap': ([crawl_tap(s) for s in (11, 12, 13, 14)], -4.0, False),
    'hunt.sniff': ([sniff(s) for s in (21, 22, 23)], -4.0, False),
    'hunt.hiss': ([hiss(s) for s in (31, 32)], -2.0, False),
    'hunt.groan': ([groan(s) for s in (41, 42, 43)], -2.5, False),
    'hunt.jaw': ([jaw(s) for s in (51, 52)], -4.0, False),
    'hunt.scream': ([scream], -1.0, False),
    'hunt.rattle': ([rattle(s) for s in (61, 62)], -3.0, False),
    'hunt.grab': ([grab], -1.0, False),
    'hunt.gasp': ([gasp(s) for s in (71, 72)], -2.0, False),
    'hunt.breath_in': ([breath_in], -9.0, False),
    'hunt.breath_out': ([breath_out], -9.0, False),
    'hunt.heartbeat': ([heartbeat], -3.0, True),
    'hunt.chase': ([chase], -3.0, True),
}


def rel_paths(name):
    n = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base] if n == 1 else [f'{base}_{i + 1}' for i in range(n)]


def finish(x, peak_db, loop):
    x = np.asarray(x, np.float32)
    if loop:
        # the master's edge fades would dip the seam: master three tiled periods and keep the middle one
        L = len(x)
        return dsp.master(np.concatenate([x, x, x], 0), peak_db=peak_db)[L:2 * L]
    x = dsp.trim(x, -62, 0.08)
    return dsp.master(x, peak_db=peak_db)


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    report = {}
    for name, (fns, pk, loop) in EVENTS.items():
        assert name in SOUNDS, name + ' missing from sounds_def'
        rels = rel_paths(name)
        stream = SOUNDS[name][3]
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            raw = fn()
            assert raw.ndim == 1 or stream, rel + ' is positional / non-streamed: must be mono'
            x = finish(raw, pk, loop)
            path = dsp.save_ogg(x, rel)
            over = 20 * np.log10(np.max(np.abs(sf.read(path, dtype='float32')[0])) + 1e-12) - pk
            if over > 0.3:
                x = finish(raw, pk - (over - 0.1), loop)
                dsp.save_ogg(x, rel)
            st = dsp.analyse(x)
            report[rel] = st
            dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            if loop:
                seam = np.concatenate([x[-N(1.0):], x[:N(1.0)]], 0)
                dsp.spectrogram_png(seam, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '__seam.png'))
            print(f'{rel:28s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    sp = os.path.join(REVIEW_DIR, 'stats.json')
    old = json.load(open(sp)) if os.path.exists(sp) else {}
    old.update(report)
    with open(sp, 'w') as fh:
        json.dump(old, fh, indent=1)
    missing = [rel for name in EVENTS for rel in rel_paths(name) if not os.path.exists(os.path.join(dsp.OUT, rel + '.ogg'))]
    if missing:
        print('MISSING:', missing)
    print(f'hunt sfx group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
