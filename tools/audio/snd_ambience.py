#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEAD LINE -- ambience group.

Renders
  ambient.casa      creaking house: wind through cracks, settling wood, a clock that stops, steps upstairs
  ambient.rio       night river: water, frogs + insects that go silent, a weeping woman far away
  ambient.bosque    dead snowy forest: icy wind, cracking branches, animal calls that are *wrong*
  ambient.parque    abandoned fair: rusty carousel, flapping tarps, broken calliope, buzzing neon
  ambient.convento  stone nave: drips, a far choir drone of nuns, bells tolling outside
  ambient.whispers  4 mono beds of layered, unintelligible Spanish whispers
  music.case        tense minimal score: drones, pulsing low strings, prepared piano, Shepard rise

Seamless-loop technique (no seam exists, so nothing has to be hidden):
  * every stream lives on a *periodic* timeline of exactly L samples;
  * noise beds are synthesised in the frequency domain (FFT noise is periodic by construction);
  * control curves are sums of sinusoids with whole numbers of cycles per loop;
  * oscillators get a sub-0.01 Hz phase correction so they reach the same phase at the seam;
  * discrete events are wrap-added (whatever runs past the end continues at the start);
  * filters on beds and all bus reverbs are circular (FFT) so tails from the end ring into the start.
Finally the timeline is rotated so the file starts in a lull (dsp.master's 3/20 ms edge fades land there).

Run from the repo root:  python3 tools/audio/snd_ambience.py [casa rio bosque parque convento whispers music]
"""
import os
import sys
import time

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402

REVIEW = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad/audio/ambience')
TWO_PI = 2 * np.pi
STEMS = bool(os.environ.get('STEMS'))


# =====================================================================================  helpers
def N(sec):
    return dsp.n_of(sec)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _gain(f, lp=None, hp=None, order=2, peaks=(), tilt=0.0):
    """Magnitude response used by the FFT (circular) filters and the periodic noise beds."""
    g = np.ones_like(f)
    if lp:
        g /= np.sqrt(1 + (f / lp) ** (2 * order))
    if hp:
        g /= np.sqrt(1 + (hp / np.maximum(f, 1e-3)) ** (2 * order))
    for fc, db, q in peaks:
        half = fc / q / 2
        g *= 1 + (10 ** (db / 20) - 1) / (1 + ((f - fc) / half) ** 2)
    if tilt:
        g *= (np.maximum(f, 20.0) / 1000.0) ** (tilt / 6.0206)
    return g


def bed(L, seed, stereo=False, corr=0.0, **shape):
    """Periodic, spectrally-shaped noise of exactly L samples, unit RMS per channel."""
    r = dsp.rng(seed)
    f = np.fft.rfftfreq(L, 1 / SR)
    g = _gain(f, **shape)
    g[0] = 0

    def one():
        spec = (r.standard_normal(len(f)) + 1j * r.standard_normal(len(f))) * g
        x = np.fft.irfft(spec, L)
        return (x / (np.std(x) + 1e-12)).astype(np.float32)

    if not stereo:
        return one()
    a, b = one(), one()
    if corr:
        b = corr * a + np.sqrt(1 - corr ** 2) * b
    return np.stack([a, b], 1).astype(np.float32)


def sfilt(x, **shape):
    """Zero-phase circular filter (for periodic signals: the seam stays seamless)."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = _gain(f, **shape)
    X = np.fft.rfft(x, axis=0)
    X *= g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X, len(x), axis=0).astype(np.float32)


CR = 100  # control rate for slow curves


def curve(L, seed, rate=0.2, power=1.0, lo=0.0, hi=1.0, slope=0.8):
    """Periodic smooth random control curve (content below `rate` Hz), scaled to lo..hi."""
    dur = L / SR
    nc = max(8, int(round(dur * CR)))
    tt = np.arange(nc) / nc
    r = dsp.rng(seed)
    y = np.zeros(nc)
    for k in range(1, max(1, int(rate * dur)) + 1):
        y += r.standard_normal() / k ** slope * np.sin(TWO_PI * k * tt + r.uniform(0, TWO_PI))
    y = (y - y.min()) / (y.max() - y.min() + 1e-9)
    y = lo + (hi - lo) * y ** power
    xs = np.arange(L) * nc / L
    return np.interp(xs, np.arange(nc + 1), np.append(y, y[0])).astype(np.float32)


def keyframes(L, pts):
    """Periodic envelope through (t_seconds, value) points, cosine-interpolated, wrapping at L."""
    dur = L / SR
    pts = sorted(pts)
    ts = np.array([p[0] for p in pts] + [pts[0][0] + dur])
    vs = np.array([p[1] for p in pts] + [pts[0][1]])
    nc = int(dur * CR)
    t = np.arange(nc) / CR
    tt = np.where(t < ts[0], t + dur, t)
    i = np.clip(np.searchsorted(ts, tt, side='right') - 1, 0, len(ts) - 2)
    u = (tt - ts[i]) / (ts[i + 1] - ts[i])
    u = 0.5 - 0.5 * np.cos(np.pi * u)
    y = vs[i] + (vs[i + 1] - vs[i]) * u
    return np.interp(np.arange(L) * nc / L, np.arange(nc + 1), np.append(y, y[0])).astype(np.float32)


def loop_phase(freq, L):
    """Phase in *cycles* for a per-sample frequency curve; corrected so the loop seam is phase-continuous."""
    f = np.broadcast_to(np.asarray(freq, np.float64), (L,))
    ph = np.cumsum(f) / SR
    total = ph[-1]
    ph += (np.round(total) - total) * (np.arange(L) / L)
    return ph


def blep_saw(ph, dt):
    """Band-limited (PolyBLEP) sawtooth from a phase in cycles; dt = f / SR per sample."""
    t = ph % 1.0
    dt = np.broadcast_to(np.maximum(np.asarray(dt, np.float64), 1e-6), t.shape)
    y = 2 * t - 1
    m = t < dt
    x = t[m] / dt[m]
    y[m] -= x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    y[m] -= x * x + x + x + 1
    return y


def put(buf, ev, t, gain=1.0):
    """Wrap-add an event (mono or stereo) into a periodic buffer at t seconds."""
    L = len(buf)
    if ev.ndim == 1 and buf.ndim == 2:
        ev = np.stack([ev, ev], 1)
    s = int(round(t * SR)) % L
    n = len(ev)
    i = 0
    while i < n:
        a = (s + i) % L
        m = min(n - i, L - a)
        buf[a:a + m] += ev[i:i + m] * gain
        i += m


def make_ir(decay, damp, predelay, seed, hf_decay=0.45, er=6):
    """Stereo reverb impulse response: decorrelated L/R tails, HF dying faster, a few early reflections."""
    n = N(decay * 1.35)
    t = np.arange(n) / SR
    r = dsp.rng(seed)
    out = []
    for _ in range(2):
        w = r.standard_normal(n).astype(np.float32)
        lo = dsp.lowpass(w, damp, 2) * np.exp(-6.9 * t / decay)
        hi = dsp.highpass(w, damp, 2) * np.exp(-6.9 * t / (decay * hf_decay))
        ir = lo + 0.5 * hi
        att = np.minimum(1.0, t / 0.04)  # diffuse tail builds up
        ir *= att
        for _k in range(er):
            p = int(r.uniform(0.004, 0.045) * SR)
            ir[p] += r.uniform(0.3, 1.0) * r.choice([-1, 1]) * 12 / er
        ir = np.concatenate([np.zeros(N(predelay)), ir])
        out.append(ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9))
    return np.stack(out, 1)


def creverb(x, decay=2.5, damp=4000.0, predelay=0.03, seed=7, hf_decay=0.45, cross=0.3):
    """Circular stereo reverb (wet only) for a periodic stereo buffer."""
    L = len(x)
    ir = make_ir(decay, damp, predelay, seed, hf_decay)
    if len(ir) > L:  # fold an IR longer than the loop (never happens for 45 s+ loops, kept for safety)
        ir = np.pad(ir, ((0, -len(ir) % L), (0, 0))).reshape(-1, L, 2).sum(0)
    X = np.fft.rfft(x, axis=0)
    H = np.fft.rfft(ir, n=L, axis=0)
    inl = (1 - cross) * X[:, 0] + cross * X[:, 1]
    inr = (1 - cross) * X[:, 1] + cross * X[:, 0]
    wl = np.fft.irfft(inl * H[:, 0], L)
    wr = np.fft.irfft(inr * H[:, 1], L)
    return np.stack([wl, wr], 1).astype(np.float32)


def far(x, d):
    """Distance colouring: d = 0 close, 1 very far (air absorption)."""
    return dsp.lowpass(x, 9000 * (0.12 ** d), 2)


def env_ar(n, a, r_, shape=1.0):
    e = np.ones(n, np.float32)
    na, nr = min(n, N(a)), min(n, N(r_))
    if na:
        e[:na] = np.linspace(0, 1, na) ** shape
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** shape
    return e


def norm(x, peak=1.0):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def howl(L, seed, fc, depth_oct=0.5, rate=0.1, bw=15.0, stereo=True):
    """Narrow-band wind whistle: quadrature-modulated low-passed noise around a wandering centre."""
    fcur = fc * 2 ** (depth_oct * (curve(L, seed, rate) * 2 - 1))
    ph = TWO_PI * loop_phase(fcur, L)
    c, s = np.cos(ph), np.sin(ph)
    chans = []
    for k in range(2 if stereo else 1):
        n1 = bed(L, seed * 7 + 2 * k + 1, lp=bw, order=2)
        n2 = bed(L, seed * 7 + 2 * k + 2, lp=bw, order=2)
        y = n1 * c - n2 * s
        chans.append((y / (np.std(y) + 1e-9)).astype(np.float32))
    return np.stack(chans, 1) if stereo else chans[0]


def loop_tone(L, f, shape='sine', amp=None, vib=0.0, vib_rate=5.0, seed=0):
    r = dsp.rng(seed)
    fr = np.full(L, f, np.float64) if np.ndim(f) == 0 else np.asarray(f, np.float64)
    if vib:
        fr = fr * (1 + vib * (curve(L, seed + 99, vib_rate, lo=-1, hi=1, slope=0.2)))
    ph = loop_phase(fr, L) + r.random()
    y = np.sin(TWO_PI * ph) if shape == 'sine' else blep_saw(ph, fr / SR)
    if amp is not None:
        y = y * amp
    return y.astype(np.float32)


def limit(x, crest_db=15.0, win=0.012, rel=0.08):
    """Circular look-ahead peak limiter: caps peaks at crest_db above the overall RMS."""
    m = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    rms = np.sqrt(np.mean(m ** 2))
    thr = rms * 10 ** (crest_db / 20)
    env = maximum_filter1d(m, N(win), mode='wrap')
    g = np.minimum(1.0, thr / (env + 1e-9))
    g = minimum_filter1d(g, N(rel), mode='wrap')
    g = uniform_filter1d(g, N(rel), mode='wrap')
    return (x * (g[:, None] if x.ndim == 2 else g)).astype(np.float32)


def rotate_to_lull(x, search=8.0):
    """Roll the periodic buffer so the file starts at the quietest 60 ms within +/- search seconds of 0."""
    m = np.abs(x).mean(axis=1) if x.ndim == 2 else np.abs(x)
    e = uniform_filter1d(m, N(0.06), mode='wrap')
    L = len(x)
    cand = np.r_[np.arange(0, N(search)), np.arange(L - N(search), L)]
    i = int(cand[np.argmin(e[cand])])
    return np.roll(x, -i, axis=0), i / SR


def seam_report(x):
    """Ratio of the step across the loop seam to the typical sample-to-sample step (1.0 = invisible)."""
    m = x.mean(axis=1) if x.ndim == 2 else x
    d = np.abs(np.diff(m))
    return float(abs(m[0] - m[-1]) / (np.percentile(d, 75) + 1e-9))


def finish_stream(x, peak_db=-4.0, crest_db=15.0, rotate=True):
    x = sfilt(x, hp=28, order=2)
    x = limit(x, crest_db)
    off = 0.0
    if rotate:
        x, off = rotate_to_lull(x)
    seam = seam_report(x)
    return dsp.master(x, peak_db=peak_db), seam, off


class Scene:
    """Periodic stereo timeline with a dry bus and named reverb send buses."""

    def __init__(self, dur):
        self.L = N(dur)
        self.dur = self.L / SR
        self.dry = np.zeros((self.L, 2), np.float32)
        self.buses = {}

    def bus(self, name, **kw):
        self.buses[name] = [np.zeros((self.L, 2), np.float32), kw]

    def add(self, x, t, p=0.0, dry=1.0, send=None, wet=0.0):
        st = dsp.pan(x, float(np.clip(p, -1, 1))) if x.ndim == 1 else x
        if dry:
            put(self.dry, st, t, dry)
            if STEMS:
                self.stem_ev = self.stem_ev if hasattr(self, 'stem_ev') else np.zeros((self.L, 2), np.float32)
                put(self.stem_ev, st, t, dry)
        if send and wet:
            put(self.buses[send][0], st, t, wet)

    def bed(self, x, dry=1.0, send=None, wet=0.0):
        if x.ndim == 1:
            x = np.stack([x, x], 1)
        self.dry += x * dry
        if STEMS:
            self.stem_bed = (self.stem_bed if hasattr(self, 'stem_bed') else 0) + x * dry
        if send and wet:
            self.buses[send][0] += x * wet

    def mix(self):
        out = self.dry.copy()
        wet = 0
        for buf, kw in self.buses.values():
            wet = wet + creverb(buf, **kw)
        out += wet
        if STEMS:
            def db(v):
                return f'{20 * np.log10(v + 1e-12):6.1f}'
            for nm, st in (('bed', getattr(self, 'stem_bed', None)), ('events', getattr(self, 'stem_ev', None)),
                           ('reverb', wet), ('total', out)):
                if st is not None and np.ndim(st) == 2:
                    m = st.mean(1)
                    print(f'    stem {nm:7s} rms {db(np.sqrt(np.mean(m ** 2)))} dB  peak {db(np.max(np.abs(m)))} dB'
                          f'  p99.9 {db(np.percentile(np.abs(m), 99.9))} dB')
        return out


# =====================================================================================  sound objects
def modal(exc, modes, tail=0.3):
    """Excite decaying sinusoid modes [(freq, decay_per_s, amp)] with an exciter signal."""
    t = np.arange(N(tail)) / SR
    ir = np.zeros(len(t))
    for f, d, a in modes:
        if f < SR / 2 - 500:
            ir += a * np.sin(TWO_PI * f * t) * np.exp(-d * t)
    return signal.fftconvolve(exc, ir).astype(np.float32)


def creak(dur, seed, rate0=40.0, rate1=18.0, modes=((220, 40, 1), (510, 55, .6), (1150, 80, .35), (2300, 120, .2)),
          wobble=0.3, jitter=0.25, hiss=0.15, shape=None, tail=0.35):
    """Stick-slip friction creak: an irregular pulse train exciting wood/metal modes."""
    r = dsp.rng(seed)
    n = N(dur)
    k = np.linspace(0, 1, n)
    rate = rate0 * (rate1 / rate0) ** k
    rate *= 1 + wobble * np.interp(k, np.linspace(0, 1, 9), r.uniform(-1, 1, 9))
    ph = np.cumsum(rate) / SR
    idx = np.nonzero(np.diff(np.floor(ph)))[0]
    idx = np.clip(idx + (r.normal(0, jitter, len(idx)) * SR / rate[idx] * 0.3).astype(int), 0, n - 1)
    env = shape if shape is not None else np.sin(np.pi * k) ** 0.6
    imp = np.zeros(n, np.float32)
    np.add.at(imp, idx, env[idx] * r.uniform(0.35, 1.0, len(idx)))
    burst = dsp.noise(0.0015, 'white', seed + 1) * np.linspace(1, 0, N(0.0015))
    exc = signal.fftconvolve(imp, burst)[:n]
    md = [(f * r.uniform(0.96, 1.04), d, a) for f, d, a in modes]
    y = modal(exc, md, tail)
    if hiss:
        h = dsp.bandpass(dsp.noise(len(y) / SR, 'white', seed + 2), 900, 4500, 2)
        e = np.pad(env, (0, len(y) - n)) * np.pad(np.minimum(1, rate / rate0), (0, len(y) - n))
        y = norm(y) + hiss * h * e
    return norm(y)


def thump(seed, f=55.0, dur=0.7, click=0.35, muffle=320.0):
    r = dsp.rng(seed)
    t = np.arange(N(dur)) / SR
    fr = f * (1 + 1.4 * np.exp(-t * 28)) * r.uniform(0.93, 1.07)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR) * np.exp(-t * 9)
    nz = dsp.lowpass(dsp.noise(dur, 'pink', seed), 900, 2) * np.exp(-t * 45)
    y = y + click * nz
    return norm(dsp.lowpass(y, muffle, 2))


def tick(seed, tock=False):
    r = dsp.rng(seed)
    exc = dsp.noise(0.002, 'white', seed) * np.linspace(1, 0, N(0.002))
    m = 0.86 if tock else 1.0
    modes = [(2650 * m, 140, .8), (4100 * m, 190, .5), (6200 * m, 260, .3), (880 * m, 70, .5), (1450 * m, 110, .4)]
    y = modal(exc, [(f * r.uniform(.99, 1.01), d, a) for f, d, a in modes], 0.12)
    return norm(dsp.highpass(y, 300, 2))


def chime(f, seed, dur=6.0):
    """Clock-chime rod / gong strike: inharmonic, long, beating."""
    r = dsp.rng(seed)
    t = np.arange(N(dur)) / SR
    y = np.zeros(len(t))
    for ratio, amp, dec in [(1.0, 1.0, 0.55), (2.76, 0.55, 1.1), (5.40, 0.3, 2.0), (8.93, 0.18, 3.2), (1.5, 0.12, 1.4)]:
        for det in (-0.6, 0.55):
            y += amp * np.sin(TWO_PI * (f * ratio + det * ratio ** 0.5) * t + r.uniform(0, 6)) * np.exp(-dec * t)
    strike = dsp.bandpass(dsp.noise(0.05, 'white', seed), 800, 5000, 2) * np.exp(-np.arange(N(0.05)) / SR * 90)
    y[:len(strike)] += strike * 1.5
    return norm(y * np.minimum(1, t / 0.002))


def bell(f, seed, dur=9.0):
    """Church bell: hum / prime / minor-third tierce / quint / nominal ... each partial a beating pair."""
    r = dsp.rng(seed)
    t = np.arange(N(dur)) / SR
    y = np.zeros(len(t))
    parts = [(0.5, 0.9, 0.32), (1.0, 0.75, 0.55), (1.183, 0.7, 0.8), (1.506, 0.35, 1.1), (2.0, 0.6, 1.25),
             (2.514, 0.28, 1.8), (2.662, 0.22, 2.0), (3.011, 0.2, 2.5), (4.166, 0.12, 3.3), (5.433, 0.08, 4.2),
             (6.796, 0.05, 5.5)]
    for ratio, amp, dec in parts:
        beat = r.uniform(0.3, 1.6)
        fr = f * ratio
        y += amp * (np.sin(TWO_PI * fr * t + r.uniform(0, 6)) + 0.7 * np.sin(TWO_PI * (fr + beat) * t + r.uniform(0, 6))) * np.exp(-dec * t)
    strike = dsp.bandpass(dsp.noise(0.08, 'white', seed + 1), 600, 4500, 2) * np.exp(-np.arange(N(0.08)) / SR * 60)
    y[:len(strike)] += 2.5 * strike
    return norm(y * np.minimum(1, t / 0.003))


def bubble(f0, seed, rise=0.35, amp=1.0):
    r = dsp.rng(seed)
    d = 45 + f0 * 0.045
    dur = min(0.12, 6.0 / d)
    t = np.arange(N(dur)) / SR
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.0015)
    return (y * amp).astype(np.float32)


def drip(f0, seed):
    """Water drop into a puddle: tiny impact click + rising bubble ring."""
    r = dsp.rng(seed)
    b = bubble(f0, seed, rise=r.uniform(0.6, 1.2))
    click = dsp.highpass(dsp.noise(0.004, 'white', seed), 2500, 2) * np.linspace(1, 0, N(0.004)) * 0.6
    out = np.zeros(len(b) + N(0.003), np.float32)
    out[:len(click)] += click
    out[N(0.003):] += b
    # occasional second, smaller ring (splash-back)
    if r.random() < 0.5:
        b2 = bubble(f0 * r.uniform(1.3, 1.8), seed + 5, rise=0.8, amp=0.35)
        out = np.pad(out, (0, N(0.03)))
        s = N(r.uniform(0.008, 0.025))
        out[s:s + len(b2)] += b2[:len(out) - s]
    return out


def snap(seed, size=1.0):
    """Branch crack: sharp break transient + crackle of fibres + wood resonance (+ thud if big)."""
    r = dsp.rng(seed)
    dur = 0.25 + 0.5 * size
    n = N(dur)
    imp = np.zeros(n, np.float32)
    imp[0] = 1.0
    k = int(4 + 10 * size)
    pos = np.clip((r.exponential(0.05 + 0.12 * size, k) * SR).astype(int), 1, n - 1)
    np.add.at(imp, pos, r.uniform(0.15, 0.7, k) * np.exp(-pos / SR * 4))
    burst = dsp.noise(0.003, 'white', seed + 1) * np.linspace(1, 0, N(0.003))
    exc = signal.fftconvolve(imp, burst)[:n]
    modes = [(r.uniform(700, 1200), 160, 1), (r.uniform(1600, 2400), 210, .7), (r.uniform(2800, 4200), 300, .5),
             (r.uniform(350, 550), 90, .6 * size)]
    y = modal(exc, modes, 0.2)[:n] + 0.6 * dsp.highpass(exc, 1500, 2)
    if size > 1.2:
        th = thump(seed + 3, 70, 0.8, 0.6, 500) * 0.5
        s = N(0.12 + 0.15 * size)
        y = np.pad(y, (0, s + len(th)))
        y[s:s + len(th)] += th
    return norm(y)


def voice_src(f0, dur, seed, jitter=0.01, breath=0.25, vib=0.0, vib_rate=5.5):
    """Breathy glottal-ish source: band-limited saw + aspiration noise, with jitter/vibrato."""
    r = dsp.rng(seed)
    n = N(dur)
    t = np.arange(n) / SR
    f = np.broadcast_to(np.asarray(f0, np.float64), (n,)).copy()
    f *= 1 + jitter * np.interp(t, np.linspace(0, dur, max(4, int(dur * 30))), r.standard_normal(max(4, int(dur * 30))))
    if vib:
        f *= 1 + vib * np.sin(TWO_PI * vib_rate * t + r.uniform(0, 6))
    ph = np.cumsum(f) / SR + r.random()
    y = blep_saw(ph, f / SR)
    y = dsp.lowpass(y.astype(np.float32), 4000, 1)
    y += breath * dsp.noise(dur, 'pink', seed + 1) * 2
    return y.astype(np.float32)


VOWELS = {'a': ((800, 1150, 2900), (1.0, 0.6, 0.25)), 'o': ((450, 800, 2830), (1.0, 0.45, 0.15)),
          'u': ((325, 700, 2530), (1.0, 0.25, 0.08)), 'e': ((480, 2000, 2900), (1.0, 0.35, 0.2)),
          'i': ((300, 2500, 3300), (1.0, 0.25, 0.2))}


def vowel(x, v, q=7.0, scale=1.0):
    fs, amps = VOWELS[v]
    y = np.zeros_like(x)
    for f, a in zip(fs, amps):
        f *= scale
        y += a * dsp.bandpass(x, f / (1 + 1 / q), f * (1 + 1 / q), 2)
    return y


def whisperize(x, seed, smooth=7, tilt=0.4):
    """Turn voiced TTS into a whisper: noise excitation shaped by the speech's spectral envelope."""
    f, _, Z = signal.stft(x, SR, nperseg=1024, noverlap=768)
    env = uniform_filter1d(np.abs(Z), size=smooth, axis=0)
    r = dsp.rng(seed)
    Y = env * ((np.maximum(f, 150) / 1000) ** tilt)[:, None] * np.exp(2j * np.pi * r.random(Z.shape))
    _, y = signal.istft(Y, SR, nperseg=1024, noverlap=768)
    y = dsp.highpass(y[:len(x)].astype(np.float32), 280, 2)
    return norm(y)


# =====================================================================================  AMBIENT.CASA
def build_casa():
    sc = Scene(60.0)
    L = sc.L
    r = dsp.rng(101)
    sc.bus('room', decay=1.7, damp=4500, predelay=0.012, seed=11)
    sc.bus('house', decay=3.2, damp=2200, predelay=0.03, seed=12, hf_decay=0.35)

    gust = curve(L, 102, rate=0.11, power=1.7)
    gust_s = gust[:, None]
    # room tone + structure-borne rumble
    sc.bed(bed(L, 103, True, 0.5, lp=170, hp=25, tilt=-6) * 0.02)
    # draught through the gaps, breathing with the gusts
    draft = bed(L, 104, True, 0.3, hp=260, lp=2400, tilt=-3, peaks=[(700, 6, 2)])
    sc.bed(draft * (0.004 + 0.022 * gust_s), send='room', wet=0.3)
    # whistle through a cracked window and under a door
    h1 = howl(L, 105, 520, 0.55, 0.08, 16) * (gust_s ** 2.2)
    h2 = howl(L, 106, 1180, 0.35, 0.11, 10) * (curve(L, 107, 0.15, 3.0)[:, None] * gust_s)
    sc.bed(h1 * 0.02 + h2 * 0.007, send='room', wet=0.5)
    # unease: sub drone with slow beating (E1 vs F1) swelling in and out
    sw = keyframes(L, [(0, 0.35), (15, 0.6), (30, 1.0), (40, 0.25), (50, 0.7)])
    sub = (loop_tone(L, 41.2, seed=1) + 0.8 * loop_tone(L, 43.65, seed=2) + 0.35 * loop_tone(L, 82.4, seed=3)
           + 0.25 * loop_tone(L, 87.3, seed=4)) * sw
    sc.bed(sub * 0.012)

    # --- grandfather clock in the next room: tick-tock every second; it STOPS for 4 s, then resumes
    for s in range(60):
        if 37 <= s <= 40:
            continue
        tk = tick(200 + s, tock=bool(s % 2))
        sc.add(far(tk, 0.35), s + r.normal(0, 0.003), p=0.38, dry=0.16, send='room', wet=0.09)
    # the clock strikes three (whirr of gears, then three deep strikes)
    whirr = dsp.bandpass(dsp.noise(1.1, 'white', 210), 1200, 5000, 2)
    whirr *= np.abs(np.sin(TWO_PI * 23 * np.arange(len(whirr)) / SR)) ** 4 * env_ar(len(whirr), 0.1, 0.4)
    sc.add(far(whirr, 0.4), 20.4, p=0.38, dry=0.05, send='room', wet=0.05)
    for i in range(3):
        c = far(chime(146.8, 220 + i), 0.3)
        sc.add(c, 21.7 + i * 2.6, p=0.36, dry=0.16, send='house', wet=0.16)

    # --- floorboards / walls settling
    for t0 in (3.2, 12.5, 26.0, 34.0, 45.5, 55.0):
        dur = r.uniform(0.6, 1.6)
        c = creak(dur, int(t0 * 10), r.uniform(28, 45), r.uniform(10, 18),
                  modes=((160, 30, 1), (380, 45, .7), (900, 70, .4), (1900, 110, .2)), hiss=0.08)
        d = r.uniform(0.25, 0.6)
        sc.add(far(c, d), t0, p=r.uniform(-0.8, 0.8), dry=0.17 * (1 - 0.5 * d), send='room', wet=0.12)
    # a door slowly swinging open somewhere (long pitched creak)
    door = creak(3.2, 301, 95, 38, modes=((310, 22, 1), (690, 30, .8), (1380, 45, .55), (2650, 70, .35), (3900, 90, .2)),
                 wobble=0.45, jitter=0.15, hiss=0.1,
                 shape=dsp.env_points(N(3.2), [(0, 0), (0.08, 0.7), (0.4, 1.0), (0.7, 0.6), (0.85, 0.9), (1, 0)]))
    sc.add(far(door, 0.45), 7.5, p=-0.6, dry=0.15, send='house', wet=0.14)
    # small settling ticks of the old wood
    for i in range(16):
        exc = np.zeros(N(0.002), np.float32)
        exc[0] = 1
        tk = modal(exc, [(r.uniform(1300, 2400), 160, 1), (r.uniform(2900, 4200), 240, .5), (r.uniform(500, 800), 90, .4)], 0.08)
        d = r.uniform(0.2, 0.8)
        sc.add(far(norm(tk), d), r.uniform(0, 60), p=r.uniform(-1, 1), dry=0.08 * (1 - 0.6 * d), send='room', wet=0.06)

    # --- someone walking upstairs: five slow heavy steps, each with a ceiling creak; then silence
    t0 = 27.6
    for i in range(5):
        tt = t0 + i * 0.78 + r.normal(0, 0.03)
        st = thump(400 + i, f=r.uniform(52, 62), dur=0.6, click=1.1, muffle=520)
        exc = np.zeros(N(0.003), np.float32)
        exc[0] = 1
        knock = modal(exc, [(r.uniform(180, 220), 45, 1), (r.uniform(420, 480), 70, .6), (r.uniform(900, 1000), 110, .3)], 0.25)
        st = norm(st + 0.5 * norm(knock)[:len(st)])
        sc.add(st, tt, p=0.1 + 0.08 * i, dry=0.45, send='house', wet=0.2)
        cr = creak(0.35, 410 + i, 30, 15, modes=((140, 30, 1), (330, 45, .6), (700, 70, .3)), hiss=0.0)
        sc.add(far(cr, 0.55), tt + 0.05, p=0.1 + 0.08 * i, dry=0.08, send='house', wet=0.06)
    # a door slams far away in the house
    slam = thump(450, f=62, dur=1.0, click=0.9, muffle=600)
    rat = modal(np.r_[1.0, np.zeros(N(0.3))].astype(np.float32), [(820, 30, .5), (1430, 40, .4), (2210, 60, .3)], 0.4)
    slam = np.pad(slam, (0, N(0.5)))
    slam[N(0.01):N(0.01) + len(rat)] += norm(rat)[:len(slam) - N(0.01)] * 0.25
    sc.add(far(slam, 0.5), 50.6, p=-0.3, dry=0.33, send='house', wet=0.3)

    # --- window frame rattling in the strongest gusts
    gk = gust[::N(0.25)]
    peaks = [i * 0.25 for i in signal.find_peaks(gk, height=0.6, distance=40)[0]]
    for j, tp in enumerate(peaks):
        n = N(r.uniform(0.4, 0.9))
        imp = np.zeros(n, np.float32)
        ph = np.cumsum(np.full(n, r.uniform(14, 22))) / SR
        idx = np.nonzero(np.diff(np.floor(ph)))[0]
        imp[idx] = r.uniform(0.3, 1, len(idx)) * np.sin(np.pi * idx / n)
        rt = modal(imp, [(1850, 90, .7), (2950, 120, .5), (4350, 160, .3), (420, 60, .6)], 0.12)
        sc.add(far(norm(rt), 0.3), tp - 0.3, p=0.7, dry=0.06, send='room', wet=0.05)

    x = sc.mix()
    return finish_stream(x, -4.0, 14.0)


# =====================================================================================  AMBIENT.RIO
def frog_call(seed, f0, pulses, prate, plen=0.035, form=(600, 1300)):
    r = dsp.rng(seed)
    dur = pulses / prate + 0.1
    src = voice_src(f0 * r.uniform(0.97, 1.03), dur, seed, jitter=0.02, breath=0.08)
    t = np.arange(len(src)) / SR
    gate = np.zeros(len(src), np.float32)
    for k in range(pulses):
        s = N(k / prate)
        e = np.sin(np.pi * np.linspace(0, 1, N(plen))) ** 1.5 * r.uniform(0.6, 1.0)
        gate[s:s + len(e)] += e[:len(gate) - s]
    y = src * gate
    y = dsp.bandpass(y, 120, 3500, 2) + 1.5 * dsp.bandpass(y, form[0] * 0.8, form[0] * 1.25, 2) + dsp.bandpass(y, form[1] * 0.85, form[1] * 1.2, 2)
    return norm(y * np.minimum(1, t / 0.005))


def cricket_chirp(seed, fc, pulses=3, pdur=0.016, gap=0.032):
    r = dsp.rng(seed)
    dur = pulses * gap + 0.02
    t = np.arange(N(dur)) / SR
    gate = np.zeros(len(t), np.float32)
    for k in range(pulses):
        s = N(k * gap)
        e = np.sin(np.pi * np.linspace(0, 1, N(pdur))) ** 2 * (0.8 + 0.2 * r.random())
        gate[s:s + len(e)] += e[:len(gate) - s]
    y = np.sin(TWO_PI * fc * t) + 0.25 * np.sin(TWO_PI * 2 * fc * t + 1)
    return (y * gate).astype(np.float32)


def sob_phrase(seed, n=4, f0=420):
    """Distant convulsive female sobbing: short breathy vocal bursts + gasping in-breaths."""
    r = dsp.rng(seed)
    out = []
    for k in range(n):
        d = r.uniform(0.18, 0.34)
        fs = dsp.glide(f0 * r.uniform(1.0, 1.15), f0 * r.uniform(0.72, 0.85), d)
        s = voice_src(fs, d, seed + k, jitter=0.03, breath=0.45, vib=0.02, vib_rate=7)
        v = vowel(s, r.choice(['a', 'u', 'o']), 6)
        v *= dsp.env_points(len(v), [(0, 0), (0.12, 1), (0.6, 0.6), (1, 0)])
        out.append(norm(v))
        if r.random() < 0.6:
            g = r.uniform(0.18, 0.3)
            gasp = dsp.bandpass(dsp.noise(g, 'white', seed + 50 + k), 900, 4200, 2)
            gasp = vowel(gasp, 'i', 5) * dsp.env_points(N(g), [(0, 0), (0.7, 1), (1, 0)])
            out.append(norm(gasp) * 0.45)
        out.append(np.zeros(N(r.uniform(0.05, 0.22)), np.float32))
    return dsp.concat(*out)


def ghost_wail(text, seed, voice='ef_dora', speed=0.72, semis=0.0, stretch=0.82):
    """TTS line processed into a far, wavering ghost wail (still intelligible)."""
    x = dsp.tts(text, voice, speed)
    x = dsp.time_stretch(x, stretch)
    if semis:
        x = dsp.pitch_shift(x, semis)
    a = x
    b = dsp.pitch_shift(x, 0.35)
    c = dsp.pitch_shift(x, -12) * 0.25
    n = min(len(a), len(b), len(c))
    y = a[:n] + 0.6 * np.pad(b, (N(0.018), 0))[:n] + c[:n]
    y = dsp.tremolo(y, 5.5, 0.25)
    y = dsp.bandpass(y, 260, 2600, 2)
    return norm(y)


def build_rio():
    sc = Scene(64.0)
    L = sc.L
    r = dsp.rng(201)
    sc.bus('night', decay=2.0, damp=3200, predelay=0.04, seed=21)
    sc.bus('far', decay=5.0, damp=1700, predelay=0.09, seed=22, hf_decay=0.35)

    gust = curve(L, 202, 0.09, 1.4)[:, None]
    # the river: rushing bed with irregular babble + low body
    babble = (0.55 + 0.45 * curve(L, 203, 2.5, 1.0))[:, None]
    flow = bed(L, 204, True, 0.25, hp=140, lp=2400, tilt=-3, peaks=[(480, 5, 1.6), (1300, 4, 2.2)])
    sc.bed(flow * babble * 0.05, send='night', wet=0.25)
    sc.bed(bed(L, 205, True, 0.6, lp=280, hp=35, tilt=-6) * 0.05)
    # night wind + reeds
    sc.bed(bed(L, 206, True, 0.2, hp=180, lp=1100, tilt=-3) * (0.006 + 0.03 * gust))
    sc.bed(bed(L, 207, True, 0.0, hp=2800, lp=9000) * (gust ** 2) * 0.012)

    # density of life: full -> everything goes quiet (something is here) -> returns
    D = keyframes(L, [(0, 1), (21, 1), (25.5, 0.1), (27, 0), (43, 0), (47, 0.35), (52, 1)])

    # bubbles / gurgles of the current
    t = 0.0
    while t < sc.dur:
        t += r.exponential(1 / 24)
        f0 = float(np.exp(r.uniform(np.log(380), np.log(1900))))
        a = r.uniform(0.2, 1) ** 2
        sc.add(bubble(f0, int(t * 1000), amp=a), t, p=r.uniform(-0.75, 0.75), dry=0.05, send='night', wet=0.02)
    # lapping against the bank
    t = 1.0
    while t < sc.dur:
        d = r.uniform(0.6, 1.1)
        sl = dsp.lowpass(dsp.noise(d, 'pink', int(t * 7)), 700, 2) * dsp.env_points(N(d), [(0, 0), (0.35, 1), (1, 0)])
        for _ in range(r.integers(2, 5)):
            b = bubble(r.uniform(170, 420), int(t * 31) + _, rise=0.5, amp=0.8)
            s = N(r.uniform(0.1, d * 0.8))
            sl[s:s + len(b)] += b[:len(sl) - s]
        sc.add(norm(sl), t, p=r.uniform(-0.3, 0.3), dry=0.07, send='night', wet=0.05)
        t += r.uniform(2.8, 5.5)

    # crickets: each its own carrier and rhythm, they drop out one by one and return one by one
    for c in range(6):
        fc = r.uniform(3900, 5300)
        per = r.uniform(0.42, 0.85)
        pulses = int(r.integers(3, 5))
        pp = r.uniform(-0.9, 0.9)
        d = r.uniform(0.15, 0.6)
        off0, on0 = 22 + c * 0.9 + r.uniform(0, 0.8), 44 + c * 1.6 + r.uniform(0, 1)
        t = r.uniform(0, per)
        while t < sc.dur:
            if not (off0 < t < on0):
                ch = cricket_chirp(int(t * 100) + c, fc, pulses)
                sc.add(ch, t, p=pp, dry=0.022 * (1 - 0.6 * d), send='night', wet=0.008)
            t += per * r.uniform(0.96, 1.04)
    # a tree-cricket trill as a continuous periodic layer
    trill = loop_tone(L, 2950.0, seed=7) * (0.5 + 0.5 * np.sin(TWO_PI * loop_phase(np.full(L, 44.0), L))) ** 4
    trill_g = D * keyframes(L, [(0, 1), (8, 1), (9, 0), (12, 0), (13, 1), (30, 1), (52, 0.1), (56, 1)]) ** 2
    sc.bed(dsp.pan(trill * trill_g, 0.55) * 0.006, send='night', wet=0.004)

    # frogs: chorus that thins out and stops
    frogs = [(210, 8, 13, 2.1, -0.6, 0.3), (265, 5, 18, 1.7, 0.45, 0.4), (330, 12, 22, 3.2, -0.2, 0.55),
             (180, 4, 9, 2.6, 0.8, 0.5), (240, 6, 15, 2.3, 0.1, 0.65)]
    for i, (f0, pulses, prate, per, pp, d) in enumerate(frogs):
        t = r.uniform(0, per)
        while t < sc.dur:
            g = float(D[min(L - 1, N(t))])
            if r.random() < g:
                fc = frog_call(int(t * 50) + i, f0, int(pulses * r.uniform(0.7, 1.2)), prate * r.uniform(0.92, 1.08))
                sc.add(far(fc, d), t, p=pp, dry=0.07 * (1 - 0.5 * d), send='night', wet=0.04)
            t += per * r.uniform(0.75, 1.35)
    # bullfrog far across the water
    for t in np.arange(3.0, 64, 6.3):
        if r.random() < float(D[min(L - 1, N(t))]):
            bf = frog_call(int(t * 9), 92, 3, 6, 0.12, (330, 800))
            sc.add(far(bf, 0.55), t + r.uniform(-0.5, 0.5), p=-0.75, dry=0.08, send='far', wet=0.04)

    # the silence: a low tone creeps in
    hush = keyframes(L, [(0, 0), (22, 0), (30, 1), (42, 1), (50, 0)])
    drone = (loop_tone(L, 55.0, seed=11) + 0.7 * loop_tone(L, 58.27, seed=12) + 0.3 * loop_tone(L, 110.0, 'saw', seed=13)) * hush
    sc.bed(sfilt(drone, lp=400) * 0.03)

    # far away a woman weeps ... and wails for her children
    sob = sob_phrase(240, 7, 430)
    sc.add(far(sob, 0.55), 29.0, p=-0.65, dry=0.08, send='far', wet=0.12)
    wail = ghost_wail('¡Aaaay, mis hijos!', 241)
    sc.add(far(wail, 0.45), 34.6, p=-0.45, dry=0.13, send='far', wet=0.24)
    sob2 = sob_phrase(242, 4, 400)
    sc.add(far(sob2, 0.7), 39.8, p=-0.25, dry=0.05, send='far', wet=0.1)
    wail2 = ghost_wail('¿Dónde están?', 243, speed=0.7, semis=-1.0)
    sc.add(far(wail2, 0.65), 43.5, p=0.3, dry=0.05, send='far', wet=0.13)

    x = sc.mix()
    return finish_stream(x, -4.0, 15.0)


# =====================================================================================  AMBIENT.BOSQUE
def wrong_owl(seed):
    """Three owl hoots that keep sliding down, too slow, the last one curdling into a growl."""
    r = dsp.rng(seed)
    parts = []
    for k, (d, f0, f1) in enumerate([(0.55, 360, 300), (0.4, 330, 240), (1.1, 310, 120)]):
        fs = dsp.glide(f0, f1, d)
        src = voice_src(fs, d, seed + k, jitter=0.004, breath=0.12)
        src = src + 0.6 * np.sin(TWO_PI * np.cumsum(fs) / SR).astype(np.float32)
        h = vowel(src, 'u', 5, 0.9) + 0.5 * dsp.lowpass(src, 700, 2)
        if k == 2:
            h = h * (1 + 0.8 * np.sin(TWO_PI * 31 * np.arange(len(h)) / SR) * np.linspace(0, 1, len(h)))
        h *= dsp.env_points(len(h), [(0, 0), (0.15, 1), (0.7, 0.8), (1, 0)])
        parts += [norm(h), np.zeros(N(r.uniform(0.35, 0.6)), np.float32)]
    return dsp.concat(*parts)


def vixen(seed, f0=950, dur=0.75):
    """Fox-scream: a harsh, rough, woman-like shriek."""
    r = dsp.rng(seed)
    fs = np.interp(np.linspace(0, 1, N(dur)), [0, 0.12, 0.45, 1], [f0 * 0.7, f0 * 1.25, f0, f0 * 0.62])
    src = voice_src(fs, dur, seed, jitter=0.03, breath=0.35)
    src *= 1 + 0.6 * np.sin(TWO_PI * r.uniform(55, 75) * np.arange(len(src)) / SR)
    y = vowel(src, 'a', 5, 1.15) + 0.4 * vowel(src, 'e', 5, 1.1)
    y *= dsp.env_points(len(y), [(0, 0), (0.08, 1), (0.6, 0.8), (1, 0)])
    return norm(dsp.drive(norm(y), 2.0))


def wrong_call(seed):
    """An animal call run through a reversed reverb: it swells *towards* you and stops dead."""
    v = vixen(seed, 620, 0.9)
    v = dsp.pitch_shift(v, -5)
    w = dsp.reverb(v, 3.5, 0.85, 2500, 0.03, seed)
    return norm(dsp.reverse(w)[N(0.3):])


def build_bosque():
    sc = Scene(66.0)
    L = sc.L
    r = dsp.rng(301)
    sc.bus('forest', decay=2.6, damp=2600, predelay=0.05, seed=31)
    sc.bus('valley', decay=6.0, damp=1500, predelay=0.18, seed=32, hf_decay=0.3)

    gust = curve(L, 302, 0.1, 1.4)
    gs = gust[:, None]
    g2 = curve(L, 303, 0.22, 2.0)[:, None]
    sc.bed(bed(L, 304, True, 0.4, lp=330, hp=25, tilt=-6) * (0.03 + 0.08 * gs))
    sc.bed(bed(L, 305, True, 0.2, hp=280, lp=3600, tilt=-3, peaks=[(820, 4, 1.3)]) * (0.006 + 0.045 * gs ** 1.5),
           send='forest', wet=0.2)
    sc.bed(bed(L, 306, True, 0.0, hp=4500, lp=12000) * (gs ** 2.5) * 0.02)  # blown snow
    sc.bed(howl(L, 307, 880, 0.7, 0.15, 10) * gs ** 3 * 0.045, send='forest', wet=0.4)
    sc.bed(howl(L, 308, 1650, 0.5, 0.2, 7) * (g2 * gs) ** 2 * 0.02, send='forest', wet=0.4)
    sc.bed(howl(L, 309, 410, 0.5, 0.06, 14) * gs ** 2 * 0.03, send='valley', wet=0.3)
    # threat underneath: a low open fifth that swells like breath
    br = curve(L, 310, 0.05, 1.5, 0.3, 1.0)
    drone = (loop_tone(L, 36.7, seed=1) + 0.6 * loop_tone(L, 55.0, seed=2) + 0.25 * loop_tone(L, 73.4, 'saw', seed=3)) * br
    sc.bed(sfilt(drone, lp=300) * 0.03)

    # branches cracking (cold wood), mostly far
    for i in range(14):
        tt = r.uniform(0, 66)
        d = r.uniform(0.45, 0.9)
        sn = snap(500 + i, r.uniform(0.3, 0.9))
        sc.add(far(sn, d), tt, p=r.uniform(-1, 1), dry=0.11 * (1 - 0.5 * d), send='forest', wet=0.08)
    for i, tt in enumerate((15.5, 33.2, 52.4)):
        sn = snap(520 + i, 1.0)
        sc.add(far(sn, 0.35), tt, p=r.uniform(-0.8, 0.8), dry=0.2, send='forest', wet=0.12)
    big = snap(530, 2.0)  # a whole branch breaks and drops into snow
    sc.add(far(big, 0.4), 46.8, p=0.55, dry=0.28, send='valley', wet=0.18)
    # trunks creaking as they sway
    for i, tt in enumerate((5.0, 19.0, 28.5, 41.0, 58.5)):
        dur = r.uniform(1.8, 3.4)
        cr = creak(dur, 540 + i, r.uniform(12, 18), r.uniform(5, 9),
                   modes=((105, 14, 1), (250, 20, .7), (520, 32, .45), (1050, 55, .2)), wobble=0.4, hiss=0.05, tail=0.6)
        sc.add(far(cr, 0.4), tt, p=r.uniform(-0.9, 0.9), dry=0.17, send='forest', wet=0.12)

    # things that call out in the dark -- and sound wrong
    ow = wrong_owl(560)
    sc.add(far(ow, 0.5), 8.8, p=0.7, dry=0.1, send='valley', wet=0.14)
    vx = dsp.concat(vixen(561), np.zeros(N(0.55), np.float32), vixen(562, 1010),
                    np.zeros(N(0.8), np.float32), vixen(563, 880, 1.1))
    vx = dsp.echo(vx, 0.43, 0.35, 4, 2000)
    sc.add(far(vx, 0.6), 23.6, p=-0.75, dry=0.07, send='valley', wet=0.13)
    wc = wrong_call(564)
    sc.add(far(wc, 0.35), 36.4, p=-0.1, dry=0.09, send='valley', wet=0.08)
    hola = dsp.tts('¿Hola?', 'em_alex', 0.8)
    hola = dsp.time_stretch(hola, 0.62)
    hola = dsp.pitch_shift(hola, -2.5)
    hola = norm(dsp.bandpass(hola, 200, 3000, 2))
    hola = dsp.echo(np.pad(hola, (0, N(0.2))), 0.47, 0.42, 5, 1800)
    sc.add(far(hola, 0.55), 55.0, p=-0.35, dry=0.12, send='valley', wet=0.12)
    hola2 = dsp.pitch_shift(norm(dsp.bandpass(dsp.time_stretch(dsp.tts('¿Hola?', 'em_alex', 0.8), 0.5), 200, 2600, 2)), -4.0)
    sc.add(far(hola2, 0.8), 61.2, p=0.6, dry=0.06, send='valley', wet=0.1)

    x = sc.mix()
    return finish_stream(x, -4.0, 15.0)


# =====================================================================================  AMBIENT.PARQUE
def calliope(notes, seed, beat=0.58, droop=0.0, cut=None):
    """Steam-organ fragment from [(start_beat, len_beats, midi), ...]: detuned pipes, wow, a dying motor."""
    r = dsp.rng(seed)
    end = max(s + l for s, l, _ in notes)
    # tempo slows towards the end if droop (beat-time -> seconds via a stretching map)
    def sec(b):
        u = b / end
        return beat * (b + droop * 2.2 * end * u ** 3)
    total = sec(end) + 1.0
    n = N(total)
    out = np.zeros(n, np.float32)
    tt = np.arange(n) / SR
    wow = 1 + 0.011 * np.sin(TWO_PI * 0.55 * tt) + 0.005 * np.sin(TWO_PI * 1.7 * tt + 1)
    sag = 1 - droop * 0.16 * np.clip((tt / sec(end)), 0, 1) ** 3
    for s, l, m in notes:
        t0, t1 = sec(s), sec(s + l)
        if cut is not None and t0 >= cut:
            continue
        d = min((t1 - t0) * 0.92, (cut - t0) if cut is not None else 99)
        a = N(t0)
        k = N(d + 0.12)
        f = midi(m) * 2 ** (r.normal(0, 22) / 1200) * wow[a:a + k] * sag[a:a + k]
        k = len(f)
        ph = np.cumsum(f) / SR + r.random()
        tone = (np.sin(TWO_PI * ph) + 0.55 * np.sin(TWO_PI * 2 * ph) + 0.35 * np.sin(TWO_PI * 3 * ph)
                + 0.12 * np.sin(TWO_PI * 4 * ph) + 0.08 * np.sin(TWO_PI * 5 * ph))
        air = dsp.bandpass(dsp.noise(k / SR, 'white', seed + a % 997), 900, 5000, 2) * 0.18
        e = env_ar(k, 0.025, 0.1)
        if cut is not None and t0 + d >= cut - 0.01:
            e = env_ar(k, 0.025, 0.01)
        out[a:a + k] += (tone + air) * e * (0.6 if m < 60 else 1.0)
    return norm(out)


WALTZ = {
    'm1': ([(0, 1, 76), (1, 1, 75), (2, 1, 76), (3, 2, 72), (5, 1, 69), (6, 1, 71), (7, 1, 72), (8, 1, 74), (9, 3, 69),
            (12, 1, 76), (13, 1, 75), (14, 1, 76), (15, 2, 79), (17, 1, 77), (18, 3, 76)],
           [(45, (57, 60, 64)), (41, (57, 60, 65)), (40, (56, 59, 62)), (45, (57, 60, 64)), (45, (57, 60, 64)),
            (43, (55, 59, 62)), (45, (57, 60, 64))]),
    'm2': ([(0, 1, 81), (1, 1, 80), (2, 1, 79), (3, 1, 78), (4, 1, 77), (5, 1, 76), (6, 2, 75), (8, 1, 72), (9, 3, 71),
            (12, 1, 69), (13, 1, 68), (14, 1, 69), (15, 3, 64)],
           [(45, (57, 60, 64)), (38, (54, 57, 62)), (40, (56, 59, 62)), (40, (56, 59, 62)), (45, (57, 60, 64)), (40, (56, 59, 64))]),
    'm3': ([(0, 1, 64), (1, 1, 67), (2, 1, 71), (3, 2, 70), (5, 1, 69), (6, 3, 68)],
           [(40, (55, 59, 64)), (40, (56, 59, 62)), (45, (57, 60, 63))]),
}


def waltz_notes(key):
    mel, bars = WALTZ[key]
    notes = list(mel)
    for b, (bass, chord) in enumerate(bars):
        notes.append((b * 3, 0.9, bass))
        for beat in (1, 2):
            for m in chord:
                notes.append((b * 3 + beat, 0.7, m))
    return notes


def flap(seed, dur):
    """Loose tarp flapping in a gust: fluttering noise with occasional whip-cracks."""
    r = dsp.rng(seed)
    n = N(dur)
    t = np.arange(n) / SR
    rate = r.uniform(7, 13) * (1 + 0.3 * np.interp(t, np.linspace(0, dur, 6), r.uniform(-1, 1, 6)))
    ph = np.cumsum(rate) / SR
    fl = (0.5 + 0.5 * np.sin(TWO_PI * ph)) ** 3
    nz = dsp.bandpass(dsp.noise(dur, 'pink', seed), 140, 2600, 2)
    y = nz * fl * dsp.env_points(n, [(0, 0), (0.2, 1), (0.75, 0.8), (1, 0)])
    for _ in range(r.integers(1, 4)):
        s = N(r.uniform(0.1, dur - 0.1))
        c = dsp.highpass(dsp.noise(0.02, 'white', seed + _), 600, 2) * np.exp(-np.arange(N(0.02)) / SR * 220)
        y[s:s + len(c)] += c[:n - s] * 2.5
    return norm(y)


def metal_hit(seed, size=1.0):
    r = dsp.rng(seed)
    exc = dsp.lowpass(dsp.noise(0.006, 'white', seed), 4000, 2) * np.linspace(1, 0, N(0.006))
    base = r.uniform(150, 210) / size
    modes = [(base * k * r.uniform(.97, 1.03), 3 + 2.5 * k ** 0.8, 1 / k ** 0.4) for k in (1, 2.31, 3.89, 6.02, 8.47, 11.6, 15.2)]
    return norm(modal(exc, modes, 2.2))


def build_parque():
    sc = Scene(56.0)
    L = sc.L
    r = dsp.rng(401)
    sc.bus('park', decay=2.8, damp=3000, predelay=0.05, seed=41)
    sc.bus('far', decay=5.0, damp=1600, predelay=0.13, seed=42, hf_decay=0.35)

    gust = curve(L, 402, 0.12, 1.3)
    gs = gust[:, None]
    sc.bed(bed(L, 403, True, 0.25, hp=150, lp=2000, tilt=-3) * (0.01 + 0.05 * gs), send='park', wet=0.2)
    sc.bed(bed(L, 404, True, 0.5, lp=240, hp=25, tilt=-6) * (0.03 + 0.06 * gs))
    sc.bed(howl(L, 405, 1700, 0.35, 0.2, 9) * gs ** 3 * 0.03, send='park', wet=0.3)  # chain-link fence singing
    sc.bed(howl(L, 406, 2450, 0.25, 0.25, 6) * gs ** 4 * 0.012, send='park', wet=0.3)

    # a broken neon sign buzzing on and off (100 Hz mains buzz)
    flick = keyframes(L, [(0, 1), (9.9, 1), (10.0, 0), (10.3, 1), (10.5, 0), (14.0, 0), (14.1, 1), (31.0, 1),
                          (31.05, 0), (31.25, 1), (31.3, 0), (31.6, 1), (44.0, 1), (44.1, 0), (49.5, 0), (49.6, 1)])
    hum = sum(loop_tone(L, 100.0 * k, seed=60 + k) / k ** 0.6 for k in range(1, 18))
    hum = sfilt(hum, hp=150, lp=3500, peaks=[(1200, 6, 2)]) * flick * (0.9 + 0.1 * curve(L, 407, 3.0))
    sc.bed(dsp.pan(hum, 0.45) * 0.008, send='park', wet=0.01)
    for tt in (10.0, 10.3, 10.5, 14.05, 31.05, 31.25, 31.3, 31.6, 44.05, 49.55):
        cl = dsp.highpass(dsp.noise(0.012, 'white', int(tt * 100)), 1500, 2) * np.exp(-np.arange(N(0.012)) / SR * 300)
        sc.add(cl, tt, p=0.45, dry=0.05, send='park', wet=0.02)

    # the carousel, turned by the wind: one rusty squeal per revolution, its position rotating around you
    per = 5.6
    for k in range(10):
        t0 = k * per + r.normal(0, 0.12)
        g = 0.6 + 0.4 * float(gust[N(t0) % L])
        sq = creak(r.uniform(1.0, 1.6), 600 + k, r.uniform(190, 240), r.uniform(120, 150),
                   modes=((1180, 18, 1), (2650, 26, .7), (3720, 34, .45), (5300, 45, .25), (640, 14, .5)),
                   wobble=0.18, jitter=0.08, hiss=0.12, tail=0.9)
        gr = creak(1.4, 650 + k, 26, 15, modes=((92, 9, 1), (231, 12, .8), (470, 18, .5), (980, 30, .3)),
                   wobble=0.2, hiss=0.04, tail=0.9)
        pp = 0.55 * np.sin(TWO_PI * k / 10)
        sc.add(far(sq, 0.4), t0, p=pp, dry=0.07 * g, send='park', wet=0.07 * g)
        sc.add(far(gr, 0.3), t0 + 0.2, p=pp, dry=0.12 * g, send='park', wet=0.06 * g)
        for j in range(r.integers(2, 5)):  # loose chains on the horses
            exc = np.zeros(N(0.002), np.float32)
            exc[0] = 1
            ch = modal(exc, [(r.uniform(2000, 2400), 30, 1), (r.uniform(5000, 5600), 50, .6), (r.uniform(7800, 8600), 70, .4)], 0.25)
            sc.add(far(norm(ch), 0.45), t0 + r.uniform(0.1, 1.5), p=pp + r.uniform(-.2, .2), dry=0.025, send='park', wet=0.02)

    # tarps on the stalls flapping with the gusts
    tk = gust[::N(0.25)]
    for j, i in enumerate(signal.find_peaks(tk, height=0.45, distance=12)[0]):
        tp = i * 0.25
        d = r.uniform(0.7, 2.2)
        fl = flap(700 + j, d)
        sc.add(far(fl, r.uniform(0.25, 0.5)), tp - d * 0.4, p=r.uniform(-0.8, 0.8), dry=0.1, send='park', wet=0.06)

    # the ferris wheel groaning under its own weight
    for i, tt in enumerate((17.8, 39.5)):
        gw = creak(3.6, 720 + i, 11, 6, modes=((68, 3, 1), (157, 4, .8), (331, 6, .6), (612, 9, .4), (1040, 14, .25)),
                   wobble=0.35, jitter=0.2, hiss=0.03, tail=2.0)
        sc.add(far(gw, 0.55), tt, p=-0.5 + i, dry=0.13, send='far', wet=0.12)
    # loose sheet metal banging
    for i, tt in enumerate((13.1, 34.6, 52.2)):
        mh = metal_hit(740 + i, r.uniform(0.9, 1.4))
        sc.add(far(mh, 0.5), tt, p=r.uniform(-0.9, 0.9), dry=0.14, send='far', wet=0.12)
        sc.add(far(mh, 0.6), tt + 0.19, p=r.uniform(-0.9, 0.9), dry=0.05, send='far', wet=0.05)

    # the calliope: detuned, far, and it keeps dying
    for key, t0, droop, cut, pp in (('m1', 5.5, 0.35, None, 0.65), ('m2', 27.0, 0.8, None, -0.55), ('m3', 46.5, 0.0, 2.35, 0.2)):
        cf = calliope(waltz_notes(key), 760 + int(t0), beat=0.56, droop=droop, cut=cut)
        cf = dsp.bandpass(cf, 260, 3200, 2)
        cf = dsp.echo(cf, 0.31, 0.28, 3, 1800)
        sc.add(far(cf, 0.45), t0, p=pp, dry=0.055, send='far', wet=0.1)

    x = sc.mix()
    return finish_stream(x, -4.0, 14.0)


# =====================================================================================  AMBIENT.CONVENTO
CHORDS = [(50, 57, 62, 65, 69), (50, 57, 61, 65, 70), (50, 55, 62, 64, 70), (50, 57, 61, 64, 69)]


def choir(L, seed, chords=CHORDS, glide=2.4, singers=4, sag=None):
    """Periodic distant choir of women's voices: voice-led chord cycle, vowel morph u<->a, breath."""
    r = dsp.rng(seed)
    dur = L / SR
    seg = dur / len(chords)
    lines = list(zip(*chords))
    t = np.arange(L) / SR
    src = np.zeros(L, np.float64)
    for li, line in enumerate(lines):
        pts = []
        for ci, m in enumerate(line):
            pts += [(ci * seg + glide / 2, midi(m)), ((ci + 1) * seg - glide / 2, midi(m))]
        base = keyframes(L, pts).astype(np.float64)
        if sag is not None:
            base *= sag
        for s in range(singers):
            det = 2 ** (r.normal(0, 9) / 1200)
            vib = 1 + r.uniform(0.006, 0.011) * np.sin(TWO_PI * loop_phase(np.full(L, r.uniform(4.6, 5.8)), L) + r.uniform(0, 6))
            drift = 1 + 0.004 * (curve(L, seed + 31 * li + s, 0.15) * 2 - 1)
            f = base * det * vib * drift
            amp = 0.6 + 0.4 * curve(L, seed + 97 * li + s, 0.12)
            src += blep_saw(loop_phase(f, L) + r.random(), f / SR) * amp * (1.2 if li == 0 else 1.0)
    src = sfilt(src.astype(np.float32), lp=2500, order=1)
    u = sfilt(src, hp=150, lp=3200, peaks=[(325, 16, 4), (700, 10, 5), (2550, 8, 7)])
    a = sfilt(src, hp=150, lp=3200, peaks=[(800, 16, 4), (1150, 12, 5), (2900, 9, 7)])
    m = curve(L, seed + 5, 0.05, 1.0)
    y = u * (1 - m) + a * m
    breath = bed(L, seed + 6, hp=1200, lp=5000) * 0.04 * np.std(y)
    return (y / (np.std(y) + 1e-9) + breath).astype(np.float32)


def build_convento():
    sc = Scene(70.0)
    L = sc.L
    r = dsp.rng(501)
    sc.bus('nave', decay=5.5, damp=3400, predelay=0.045, seed=51, hf_decay=0.4)
    sc.bus('far', decay=7.0, damp=1800, predelay=0.12, seed=52, hf_decay=0.3)

    sc.bed(bed(L, 502, True, 0.5, lp=150, hp=25, tilt=-6) * 0.05)
    sc.bed(howl(L, 503, 230, 0.4, 0.05, 9) * curve(L, 504, 0.08, 2.0)[:, None] * 0.02, send='nave', wet=0.5)
    sc.bed(howl(L, 505, 345, 0.3, 0.07, 7) * curve(L, 506, 0.08, 2.5)[:, None] * 0.012, send='nave', wet=0.5)
    sc.bed(bed(L, 507, True, 0.0, hp=1500, lp=6000, tilt=-3) * 0.0035)

    # the choir: somewhere deep in the building; at ~50 s it sags flat, as if the voices were dying
    sag = keyframes(L, [(0, 1), (46, 1), (51, 2 ** (-45 / 1200)), (55, 2 ** (-45 / 1200)), (60, 1)]).astype(np.float64)
    ch = choir(L, 510, sag=sag)
    swell = keyframes(L, [(0, 0.45), (10, 0.9), (22, 0.6), (34, 1.0), (46, 0.7), (53, 1.0), (63, 0.5)])
    chs = np.stack([ch, np.roll(ch, N(0.013))], 1) * swell[:, None]
    chs = sfilt(chs, lp=2600, hp=120)
    sc.bed(chs * 0.011, send='far', wet=0.05)

    # water dripping from the vaults into puddles: three steady sources + strays
    for (per, f0, pp, dd) in ((2.35, 2100, -0.55, 0.15), (3.62, 1450, 0.35, 0.3), (6.1, 2650, 0.85, 0.45)):
        t = r.uniform(0, per)
        while t < sc.dur:
            dr = drip(f0 * r.uniform(0.95, 1.05), int(t * 100 + f0))
            sc.add(far(dr, dd), t, p=pp, dry=0.05 * (1 - 0.5 * dd), send='nave', wet=0.07)
            t += per * r.uniform(0.92, 1.08)
    for i in range(10):
        tt = r.uniform(0, 70)
        dr = drip(r.uniform(1100, 3000), 900 + i)
        sc.add(far(dr, 0.5), tt, p=r.uniform(-1, 1), dry=0.02, send='nave', wet=0.05)

    # bells tolling outside, far away
    for i, tt in enumerate((13.0, 17.6, 22.2)):
        b = bell(196.0, 520 + i)
        sc.add(far(b, 0.55), tt, p=0.25, dry=0.07, send='far', wet=0.1)
    b = bell(174.6, 530)
    sc.add(far(b, 0.65), 57.5, p=-0.4, dry=0.05, send='far', wet=0.09)

    # a heavy door closing somewhere in the cloister
    dc = creak(1.6, 540, 70, 30, modes=((240, 20, 1), (560, 28, .7), (1250, 40, .45), (2400, 60, .25)), hiss=0.08)
    th = thump(541, 58, 1.2, 0.9, 700)
    dc = np.pad(dc, (0, len(th)))
    dc[N(1.55):N(1.55) + len(th)] += th[:len(dc) - N(1.55)] * 1.6
    sc.add(far(dc, 0.55), 39.0, p=-0.7, dry=0.1, send='nave', wet=0.22)
    # a faint metallic scrape (chains? a censer?) once
    sc_ = creak(1.2, 545, 260, 180, modes=((1800, 30, 1), (3100, 40, .6), (4700, 55, .3)), hiss=0.1)
    sc.add(far(sc_, 0.6), 31.0, p=0.7, dry=0.03, send='nave', wet=0.06)

    x = sc.mix()
    return finish_stream(x, -4.0, 14.0)


# =====================================================================================  AMBIENT.WHISPERS
WHISPER_SETS = [
    [('vení… vení con nosotros', 'ef_dora', 0.85, False, 0.0, 0.10, 1.0),
     ('no te des vuelta', 'em_alex', 0.9, False, -2.0, 0.85, 0.8),
     ('te estamos mirando', 'ef_dora', 0.9, True, 1.5, 0.35, 0.7),
     ('ella está acá', 'em_santa', 0.85, False, -1.0, 2.0, 0.75),
     ('quedate quieto', 'ef_dora', 1.0, True, -3.0, 1.6, 0.5)],
    [('¿por qué viniste?', 'em_alex', 0.85, False, 0.0, 0.0, 1.0),
     ('nadie te va a escuchar', 'ef_dora', 0.95, False, 2.0, 0.7, 0.8),
     ('abrí la puerta', 'em_santa', 0.9, True, 0.0, 0.3, 0.6),
     ('shh… está despierto', 'ef_dora', 0.85, False, -1.5, 2.1, 0.85),
     ('no hay salida', 'em_alex', 1.0, True, 3.0, 1.4, 0.45)],
    [('te vimos entrar', 'ef_dora', 0.85, False, 0.0, 0.2, 1.0),
     ('quedate con nosotros', 'em_santa', 0.85, False, 0.0, 0.9, 0.8),
     ('Lucía no está sola', 'ef_dora', 0.9, True, -2.0, 0.0, 0.6),
     ('no hay salida', 'em_alex', 0.9, False, -3.0, 2.3, 0.75),
     ('está detrás tuyo', 'ef_dora', 1.0, True, 2.5, 1.7, 0.5)],
    [('date vuelta', 'em_alex', 0.85, False, 0.0, 0.15, 1.0),
     ('estamos debajo', 'ef_dora', 0.9, False, 1.0, 0.75, 0.85),
     ('te conocemos', 'em_santa', 0.85, True, 0.0, 0.0, 0.6),
     ('no respires', 'ef_dora', 0.95, False, -2.0, 2.2, 0.8),
     ('falta poco', 'em_alex', 1.0, True, 2.0, 1.5, 0.5)],
]


def breath_in(seed, dur=0.5):
    nz = dsp.bandpass(dsp.noise(dur, 'white', seed), 600, 5500, 2)
    nz = vowel(nz, 'o', 4) + 0.3 * nz
    return norm(nz * dsp.env_points(N(dur), [(0, 0), (0.75, 1), (1, 0)]))


def build_whisper(v):
    r = dsp.rng(600 + v)
    layers = []
    for i, (text, voice, speed, rev, semis, start, g) in enumerate(WHISPER_SETS[v]):
        x = dsp.tts(text, voice, speed)
        w = whisperize(x, 610 + 10 * v + i, smooth=7 if voice == 'ef_dora' else 5)
        if semis:
            w = dsp.pitch_shift(w, semis)
        if rev:
            w = dsp.reverse(w)
        w = dsp.trim(w, -45, 0.02)
        # breathing amplitude flutter + swell in/out so layers overlap like a crowd of mouths
        n = len(w)
        fl = 1 + 0.35 * np.interp(np.arange(n), np.linspace(0, n, 12), r.uniform(-1, 1, 12))
        w = w * fl * dsp.env_points(n, [(0, 0), (0.12, 1), (0.8, 0.85), (1, 0)])
        layers.append((norm(w), start, g))
    # a close in-breath and an exhaled "ssss" around the words
    layers.append((breath_in(650 + v, r.uniform(0.4, 0.6)), 0.0, 0.35))
    sss = dsp.bandpass(dsp.noise(0.9, 'white', 660 + v), 4200, 9000, 2)
    sss *= dsp.env_points(len(sss), [(0, 0), (0.2, 1), (1, 0)])
    layers.append((norm(sss), r.uniform(2.6, 3.3), 0.28))
    y = dsp.mix(*layers)
    y = y[:N(4.6)]
    y = dsp.peak(y, 2600, 4, 1.5)
    y = dsp.reverb(y, 1.2, 0.3, 5000, 0.015, 670 + v)
    y = dsp.highpass(y, 180, 2)
    y = dsp.trim(y, -50, 0.25)
    if len(y) > N(5.0):
        y = y[:N(5.0)] * np.r_[np.ones(N(4.6)), np.linspace(1, 0, N(5.0) - N(4.6))].astype(np.float32)
    return dsp.master(y, peak_db=-1.0)


# =====================================================================================  MUSIC.CASE
BPM = 72.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT  # 3.333 s, 24 bars = 80 s


def string_note(f, dur, seed, cutoff=1600.0, voices=4, bow=0.06, spic=True):
    r = dsp.rng(seed)
    n = N(dur + 0.3)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for v in range(voices):
        det = 2 ** (r.normal(0, 7) / 1200)
        vib = 1 + 0.004 * np.sin(TWO_PI * r.uniform(4.6, 5.6) * t + r.uniform(0, 6)) * np.minimum(1, t / 0.2)
        fr = f * det * vib
        y += blep_saw(np.cumsum(fr) / SR + r.random(), fr / SR)
    y = dsp.lowpass(y.astype(np.float32), cutoff, 2)
    y = dsp.peak(y, 280, 4, 1.2)
    nz = dsp.bandpass(dsp.noise(n / SR, 'white', seed + 1), 1500, 5000, 2) * bow * voices
    if spic:
        e = np.exp(-t * 7) * np.minimum(1, t / 0.012)
        e *= np.r_[np.ones(N(dur)), np.linspace(1, 0, n - N(dur))]
        ne = np.exp(-t * 40)
    else:
        e = env_ar(n, 0.08, 0.3)
        ne = e
    return ((y * e + nz * ne) / voices).astype(np.float32)


def prepared_piano(f, seed, dur=4.5, bolt=0.6, B=0.0025):
    """Piano string with a bolt between the strings: stretched + extra inharmonic partials, buzz rattle."""
    r = dsp.rng(seed)
    t = np.arange(N(dur)) / SR
    y = np.zeros(len(t))
    for k in range(1, 40):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        a = (1 / k ** 0.85) * abs(np.sin(np.pi * k * 0.13)) + 0.02
        d = 0.7 + 0.32 * k ** 1.25
        for det in (-0.35, 0.4):
            y += a * np.sin(TWO_PI * (fk + det * k ** 0.5) * t + r.uniform(0, 6)) * np.exp(-d * t)
    for ratio in r.uniform(1.5, 9.0, 6):
        y += bolt * 0.5 * np.sin(TWO_PI * f * ratio * t + r.uniform(0, 6)) * np.exp(-r.uniform(2.5, 6) * t)
    rattle = dsp.highpass(dsp.noise(dur, 'white', seed), 1800, 2) * np.exp(-t * 11)
    rattle *= (0.5 + 0.5 * np.sign(np.sin(TWO_PI * r.uniform(38, 62) * t))) * bolt * 0.35
    ham = dsp.lowpass(dsp.noise(dur, 'pink', seed + 2), 900, 2) * np.exp(-t * 70) * 0.8
    out = (y / 3 + rattle + ham) * np.minimum(1, t / 0.0015)
    return norm(out.astype(np.float32))


def boom(seed, dur=3.0):
    t = np.arange(N(dur)) / SR
    f = 36 + 40 * np.exp(-t * 6)
    y = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t * 1.4)
    hit = dsp.lowpass(dsp.noise(dur, 'brown', seed), 300, 2) * np.exp(-t * 12) * 1.5
    return norm(dsp.drive(norm(y + hit), 1.6))


def shepard(L, period, fmin=40.0, octaves=8, seed=0):
    """Endless Shepard-Risset rising glissando; one octave per `period` s, period*octaves must divide L."""
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    r = dsp.rng(seed)
    for k in range(octaves):
        pos = (k + t / period) % octaves
        f = fmin * 2 ** pos
        amp = np.exp(-0.5 * ((pos - octaves / 2 + 0.3) / (octaves / 6.5)) ** 2)
        y = np.sin(TWO_PI * loop_phase(f, L) + r.random()) * amp
        p = -0.6 if k % 2 else 0.6
        out += dsp.pan(y.astype(np.float32), p)
    return out.astype(np.float32)


def bowed_metal(L, seed, freqs=(1183, 1741, 2618, 3427), bw=6.0):
    out = 0
    for i, f in enumerate(freqs):
        out = out + howl(L, seed + i, f, 0.02, 0.1, bw) / (1 + i * 0.5)
    return out


def build_music():
    bars = 24
    sc = Scene(bars * BAR)
    L = sc.L
    r = dsp.rng(701)
    sc.bus('hall', decay=3.4, damp=4200, predelay=0.03, seed=71)
    sc.bus('cave', decay=7.0, damp=2500, predelay=0.08, seed=72, hf_decay=0.35)

    def T(bar, beat=0.0):
        return (bar - 1) * BAR + beat * BEAT

    # tension curve over the 24 bars (periodic): sparse -> build -> peak -> cut -> sparse
    ten = keyframes(L, [(T(1), 0.0), (T(5), 0.2), (T(9), 0.4), (T(13), 0.6), (T(17), 0.8), (T(21), 1.0), (T(22, 3), 1.0),
                        (T(22, 3.3), 0.05), (T(24, 3), 0.0)])

    # --- drones: D (sub + low strings) always there, A fifth joins as tension rises
    dsw = (0.7 + 0.3 * curve(L, 702, 0.06))
    sub = loop_tone(L, 36.71, seed=1) * 0.9 + loop_tone(L, 73.42, seed=2) * 0.5
    cello = sum(loop_tone(L, 73.42 * 2 ** (r.normal(0, 6) / 1200), 'saw', vib=0.003, vib_rate=0.25, seed=10 + i) for i in range(4))
    viola = sum(loop_tone(L, 110.0 * 2 ** (r.normal(0, 6) / 1200), 'saw', vib=0.003, vib_rate=0.25, seed=20 + i) for i in range(3))
    cello = sfilt(cello, lp=700, peaks=[(280, 5, 1.5)]) / 4
    viola = sfilt(viola, lp=900, peaks=[(400, 4, 1.5)]) / 3 * (0.15 + 0.85 * ten)
    sc.bed(sub * dsw * 0.11)
    sc.bed(np.stack([cello * 0.9, cello * 0.75], 1) * (dsw * 0.07)[:, None], send='hall', wet=0.03)
    sc.bed(np.stack([viola * 0.6, viola * 0.9], 1) * 0.05, send='hall', wet=0.03)

    # --- glass: high beating sine cluster D5/Eb5/A5 (+ near unisons), widening as tension grows
    gl = np.zeros((L, 2), np.float32)
    for i, (m, det) in enumerate([(74, 0), (74, 1.3), (75, 0), (75, -0.9), (81, 0), (81, 0.7), (86, 0.4)]):
        y = loop_tone(L, midi(m) + det, seed=30 + i)
        gl += dsp.pan(y, -0.8 + 1.6 * (i % 2)) / (1 + 0.3 * (m > 80))
    gsw = (0.25 + 0.75 * curve(L, 703, 0.08)) * (0.2 + 0.8 * ten)
    sc.bed(gl * gsw[:, None] * 0.0065, send='cave', wet=0.012)

    # --- bowed metal: rises in the second half
    bm = bowed_metal(L, 704)
    bmg = keyframes(L, [(T(1), 0), (T(9), 0), (T(11), 0.6), (T(13), 0.3), (T(17), 0.6), (T(21), 1.0), (T(22, 3), 1.0),
                        (T(22, 3.25), 0.0)])
    sc.bed(bm * bmg[:, None] * 0.01, send='cave', wet=0.012)

    # --- Shepard rise: never resolves (1 octave / 10 s, 8 octaves = 80 s loop)
    sp = shepard(L, 10.0, 40.0, 8, 705)
    spg = keyframes(L, [(T(1), 0.25), (T(9), 0.35), (T(17), 0.7), (T(21), 1.0), (T(22, 3), 1.0), (T(22, 3.25), 0.15)])
    sc.bed(sp * spg[:, None] * 0.03, send='hall', wet=0.01)

    # --- pulsing low strings (spiccato ostinato, 3+3+2 accents)
    acc = [1.0, 0.45, 0.5, 0.85, 0.45, 0.5, 0.85, 0.5]
    D2, EB2 = 73.42, 77.78
    for bar in range(5, 23):
        if bar <= 8:
            vel, sub8, oct_ = 0.35 + 0.06 * (bar - 5), 2, False
        elif bar <= 12:
            vel, sub8, oct_ = 0.6, 2, True
        elif bar <= 16:
            vel, sub8, oct_ = 0.75, 2, True
        else:
            vel, sub8, oct_ = 0.85 + 0.05 * (bar - 17), 4, True
        if bar in (13, 14) or (bar >= 17 and bar % 2 == 0):
            root = EB2
        else:
            root = D2
        steps = 4 * sub8
        for s in range(steps):
            beat = s / sub8
            if bar == 22 and beat >= 3.0:
                break
            a = acc[(s * 2 // sub8) % 8] if sub8 == 2 else acc[s % 8]
            d = BEAT / sub8 * 0.9
            note = string_note(root, d, 7000 + bar * 50 + s, cutoff=900 + 1400 * vel * a)
            if oct_ and a > 0.8:
                note = note + 0.5 * string_note(root * 2, d, 7500 + bar * 50 + s, cutoff=2000)[:len(note)]
            sc.add(note, T(bar, beat), p=-0.25, dry=0.5 * vel * a, send='hall', wet=0.12 * vel * a)

    # --- high sul ponticello tremolo cluster: crescendo bars 17-22, cut dead
    for bar in range(17, 23):
        for m, pp in ((86, -0.5), (87, 0.5), (93, 0.0)):
            dur = BAR if bar < 22 else 3 * BEAT
            n = string_note(midi(m), dur, 8000 + bar * 7 + m, cutoff=6000, voices=3, bow=0.18, spic=False)
            n = dsp.highpass(n, 1200, 2)
            tt = np.arange(len(n)) / SR
            n = n * (0.55 + 0.45 * np.sin(TWO_PI * 13.0 * tt)) ** 2
            if bar == 22:
                n *= np.r_[np.ones(N(3 * BEAT)), np.linspace(1, 0, len(n) - N(3 * BEAT))][:len(n)]
            g = 0.03 + 0.05 * (bar - 17)
            sc.add(n, T(bar), p=pp, dry=g, send='hall', wet=g * 0.6)

    # --- prepared piano: low bolted D clusters on structural downbeats, high plinks in between
    for bar, gain in ((1, 0.55), (3, 0.45), (5, 0.5), (9, 0.55), (13, 0.7), (17, 0.75), (21, 0.9)):
        cl = prepared_piano(36.71, 9000 + bar) + 0.6 * prepared_piano(77.78, 9100 + bar, bolt=0.9) + 0.4 * prepared_piano(110.0, 9200 + bar)
        sc.add(norm(cl), T(bar), p=0.15, dry=gain * 0.4, send='hall', wet=gain * 0.25)
    plinks = [(2, 2.5, 87), (4, 1.0, 98), (6, 3.0, 87), (8, 1.5, 93), (10, 2.0, 99), (11, 3.5, 87), (12, 0.5, 98),
              (15, 2.0, 99), (16, 3.0, 93), (19, 1.5, 98), (20, 2.5, 99), (23, 2.0, 87), (24, 0.5, 98)]
    for bar, beat, m in plinks:
        pl = prepared_piano(midi(m), 9300 + bar, dur=2.5, bolt=0.9, B=0.006)
        sc.add(pl, T(bar, beat), p=r.uniform(-0.6, 0.7), dry=0.13, send='cave', wet=0.1)

    # --- reverse swells sucking into bar 13 and bar 21; booms on 13, 17, 21
    for bar in (13, 21):
        cl = prepared_piano(36.71, 9500 + bar) + 0.7 * prepared_piano(77.78, 9550 + bar)
        rv = dsp.reverse(dsp.reverb(norm(cl), 3.0, 0.8, 3000, 0.02, 9600 + bar))
        rv = rv[-N(2 * BAR):] * np.linspace(0, 1, N(2 * BAR)) ** 1.5
        sc.add(norm(rv), T(bar) - 2 * BAR, p=0.0, dry=0.32, send='hall', wet=0.08)
    for bar, g in ((13, 0.5), (17, 0.55), (21, 0.85)):
        sc.add(boom(9700 + bar), T(bar), p=0.0, dry=g * 0.45, send='cave', wet=g * 0.1)
    # the cut at bar 22 beat 3: one last bolted hit, then only the drone answers
    last = prepared_piano(36.71, 9800, bolt=1.0) + prepared_piano(73.42, 9801, bolt=1.0)
    sc.add(norm(last), T(22, 3), p=0.0, dry=0.45, send='cave', wet=0.35)

    x = sc.mix()
    return finish_stream(x, -4.0, 15.0, rotate=False)


# =====================================================================================  driver
def review(name, x, extra=''):
    os.makedirs(REVIEW, exist_ok=True)
    a = dsp.analyse(x)
    dsp.spectrogram_png(x, os.path.join(REVIEW, name.replace('/', '_') + '.png'))
    if x.ndim == 2 and a['dur'] > 10:
        seam = np.concatenate([x[-N(3):], x[:N(3)]])
        dsp.spectrogram_png(seam, os.path.join(REVIEW, name.replace('/', '_') + '_seam.png'), 600, 200)
    print(f'  {name:22s} {a} {extra}', flush=True)
    return a


STREAMS = {'casa': build_casa, 'rio': build_rio, 'bosque': build_bosque, 'parque': build_parque,
           'convento': build_convento}


def build(only=None):
    t_all = time.time()
    want = set(only or ['casa', 'rio', 'bosque', 'parque', 'convento', 'whispers', 'music'])
    for key, fn in STREAMS.items():
        if key in want:
            t0 = time.time()
            x, seam, off = fn()
            dsp.save_ogg(x, f'ambient/{key}', quality=4)
            review(f'ambient/{key}', x, f'seam={seam:.2f} rot={off:.2f}s t={time.time() - t0:.1f}s')
    if 'whispers' in want:
        for v in range(4):
            x = build_whisper(v)
            dsp.save_ogg(x, f'ambient/whispers_{v + 1}')
            review(f'ambient/whispers_{v + 1}', x)
    if 'music' in want:
        t0 = time.time()
        x, seam, off = build_music()
        dsp.save_ogg(x, 'music/case', quality=4)
        review('music/case', x, f'seam={seam:.2f} t={time.time() - t0:.1f}s')
    print(f'ambience done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
