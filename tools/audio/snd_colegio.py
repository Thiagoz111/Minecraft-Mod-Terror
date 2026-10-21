# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "sfx" for case 1, Colegio Santa Ines de la Vigilia (school / foley events).

Run from the repo root:  python3 tools/audio/snd_colegio.py [substring ...]

Every sound is built from physical models (modal resonators excited by contact pulses, stick-slip friction trains,
Poisson debris, turbulent noise) and placed in the room it happens in (BIBLIA 2.1 f / h):

  colegio.timbre           beat 1: 4 s electric bell hammering in the hall (clapper ~23 Hz on a steel gong).
  colegio.campana          chapter separator: one deep bronze toll (prime D3, hum D2), ~8 s tail from the tower.
  colegio.campana_triple   beat 16 (03:00, Hora Muerta): three tolls, the third struck hardest and left to ring.
  colegio.pa_chime         beat 7: 1980s PA ding-dong through horn speakers + mains hum, leaves the line open.
  colegio.viento (2)       dormitory: gust in the green shutters, rattle + whistle; plays before the moon clouds.
  colegio.polvo            after the slam: plaster flakes + grit trickling onto the checkerboard floor.
  door.slam (2)            heavy double-height school door, latch, frame/glass rattle, big hall reverb.
  tiza.escribe (3)         chalk writing by itself: stroke taps, grainy scratch, the odd squeak, variable speed.
  tiza.rompe               chalk snaps against the board, the piece bounces on the ledge.
  pupitres.giran           beat 3 [CLIP]: 16 wooden chairs scraping on tiles together, ending in ONE clack.
  farol.revienta (3)       beat 6: corridor lamp - arc buzz, pop, burst, shards raining on tiles.
  luces.fuera              beat 13: main breaker KA-CHUNK, spark, buzz cut, hum winding down, cooling ticks.
  silla.arrastra (2)       beat 13 [CLIP]: the celadora's heavy chair dragged slowly over dormitory floorboards.
  silla.gira               beat 9: the Madre's old wooden swivel chair creaking round.
  telefono_baquelita.ring  beat 9: bakelite phone, two gongs + 25 Hz clapper; 2.5 s cycle, seamless loop.
  telefono.linea           1.5 s line transition: relay clunks, pulse clicks, crackle, a ghost of 425 Hz tone.
  mate.sorbo               beat 8 [RISA]: the empty gurgling slurp of a washed-out mate through a metal bombilla.
  confesionario.rejilla    beat 10: little wooden grille sliding open in the booth (shk-TOK).
  espejo.raja              beat 14: mirror crazing slowly, accelerating runs, final crack, crumbs in the sink.
  muro.cae                 beat 16: crypt brick wall collapsing, boom, bricks, rubble, dust.
  tumba.tapa               beat 16: stone lid breaking its seal and grinding open.
  regla.rompe              finale: quebracho ruler CRACK + chapel echo + shimmering girls' choir swell.
  ui.amonestacion          comic REPRIMAND: rubber stamp thump + little desk bell.
  madre.pluma              quill scratching "Aja." fast + stamp.
  dormitorio.respira (2)   sleepers breathing under sheets (seamless 4 s loops; v2 breathes in eerie unison).
  alumna.pasos (2)         group of little girls in patent-leather shoes running on wooden floors.

Positional sounds are all mono. Loudness: stingers -0.5 dBFS, foley/UI -3 dBFS, loops -4 dBFS.
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
from scipy.ndimage import uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402

REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    _os.path.join(WORK, 'audio/colegio_sfx'))
TWO_PI = 2 * np.pi


# ====================================================================== small helpers
def N(sec):
    return max(1, int(round(sec * SR)))


def taxis(n):
    return np.arange(n) / SR


def norm(x, peak=1.0):
    return (np.asarray(x, np.float32) / (np.max(np.abs(x)) + 1e-12) * peak).astype(np.float32)


def fit(x, n):
    x = np.asarray(x, np.float32)
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def add(buf, x, t, g=1.0):
    """Mix x into buf starting at t seconds (truncated at the end of buf)."""
    s = max(0, N(t)) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        buf[s:s + m] += x[:m] * g
    return buf


def padsum(*parts):
    """Sum (array, gain) pairs of different lengths."""
    n = max(len(a) for a, _g in parts)
    out = np.zeros(n, np.float32)
    for a, g in parts:
        out[:len(a)] += a * g
    return out


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def colored(n, color, seed):
    return fit(dsp.noise(n / SR + 1e-4, color, seed), n)


def snoise(n, cutoff, seed):
    """Smooth random control signal in about -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 8192).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def grain(n, cutoff, seed, power=2.0):
    """Positive rough-texture modulator with mean 1 (|low-passed noise|^power)."""
    g = np.abs(dsp.lowpass(white(n + 4096, seed), cutoff, 2)[4096:]) ** power
    return (g / (np.mean(g) + 1e-9)).astype(np.float32)


def env_pts(n, pts):
    """Piecewise-linear envelope from [(seconds, gain), ...]."""
    ts = [p[0] * SR for p in pts]
    return np.interp(np.arange(n), ts, [p[1] for p in pts]).astype(np.float32)


def smooth(x, sec):
    return uniform_filter1d(np.asarray(x, np.float32), max(1, N(sec)))


def burst(dur, seed, shape=1.0):
    """Short noise burst with a linear-ish decay (contact / break excitation)."""
    n = N(dur)
    return (white(n, seed) * np.linspace(1, 0, n) ** shape).astype(np.float32)


def half_sine(dur):
    n = max(2, N(dur))
    return np.sin(np.pi * (np.arange(n) + 0.5) / n).astype(np.float32)


def impulses(n, times, amps):
    imp = np.zeros(n, np.float32)
    idx = np.clip((np.asarray(times) * SR).astype(int), 0, n - 1)
    np.add.at(imp, idx, np.asarray(amps, np.float32))
    return imp


def modal_ir(modes, dur, seed=None):
    """Sum of exponentially decaying sinusoids: modes = [(freq, decay_per_s, amp), ...]."""
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(seed) if seed is not None else None
    y = np.zeros(n)
    for f, d, a in modes:
        if 20 < f < SR / 2 - 1500:
            ph = r.uniform(0, TWO_PI) if r is not None else 0.0
            y += a * np.sin(TWO_PI * f * t + ph) * np.exp(-d * t)
    return y.astype(np.float32)


def excite(exc, modes, tail=0.3, seed=None):
    """Drive a modal resonator with an excitation signal (returns len(exc) + tail)."""
    return signal.fftconvolve(exc, modal_ir(modes, tail, seed))[:len(exc) + N(tail)].astype(np.float32)


def detune(modes, r, amt=0.03):
    return [(f * r.uniform(1 - amt, 1 + amt), d * r.uniform(0.85, 1.15), a * r.uniform(0.75, 1.0)) for f, d, a in modes]


def knock(seed, modes, dur=0.3, contact=0.0008, click=0.35, click_hp=2000.0, amt=0.03):
    """Generic impact: half-sine contact force into modes + a bright contact click."""
    r = dsp.rng(seed)
    n = N(dur)
    exc = np.zeros(n, np.float32)
    hs = half_sine(contact)
    exc[:len(hs)] = hs
    body = excite(exc, detune(modes, r, amt), dur)[:n]
    y = norm(body)
    if click:
        cl = dsp.highpass(burst(0.0025, seed + 7, 2.0), click_hp, 2)
        y[:len(cl)] += click * norm(cl)
    return y


def stick_slip(n, rate, seed, jitter=0.25, amp_env=None, amp_lo=0.35):
    """Friction pulse train: per-sample rate (Hz) -> (indices, amplitudes)."""
    r = dsp.rng(seed)
    rate = np.full(n, float(rate)) if np.ndim(rate) == 0 else np.asarray(rate, np.float64)[:n]
    jit = 1 + jitter * snoise(n, 25, seed + 1)
    ph = np.cumsum(np.maximum(rate * jit, 0)) / SR
    idx = np.nonzero(np.diff(np.floor(ph)))[0] + 1
    if len(idx):
        shift = (r.normal(0, jitter * 0.25, len(idx)) * SR / np.maximum(rate[idx], 1)).astype(int)
        idx = np.clip(idx + shift, 0, n - 1)
    a = r.uniform(amp_lo, 1.0, len(idx))
    if amp_env is not None:
        a = a * amp_env[idx]
    return idx, a.astype(np.float32)


def pulse_train(n, idx, amps, kernel):
    imp = np.zeros(n, np.float32)
    np.add.at(imp, idx, amps)
    return signal.fftconvolve(imp, kernel)[:n].astype(np.float32)


def poisson_times(lam, seed):
    """Event sample indices of an inhomogeneous Poisson process with per-sample rate lam (events/s)."""
    r = dsp.rng(seed)
    return np.nonzero(r.random(len(lam)) < np.asarray(lam) / SR)[0]


def tv_filter(x, kind, freqs, steps=96, bw_oct=1.0):
    """Time-varying 2nd-order filter (block-wise, state carried). kind: 'lp' | 'hp' | 'bp'."""
    n = len(x)
    freqs = np.broadcast_to(np.asarray(freqs, np.float64), (n,))
    edges = np.linspace(0, n, steps + 1).astype(int)
    out = np.zeros(n, np.float32)
    zi = None
    nyq = SR / 2
    for i in range(steps):
        a, b = edges[i], edges[i + 1]
        if b <= a:
            continue
        f = float(np.mean(freqs[a:b]))
        if kind == 'lp':
            sos = signal.butter(2, min(0.98, max(20.0, f) / nyq), 'lowpass', output='sos')
        elif kind == 'hp':
            sos = signal.butter(2, min(0.98, max(20.0, f) / nyq), 'highpass', output='sos')
        else:
            lo, hi = f * 2 ** (-bw_oct / 2), f * 2 ** (bw_oct / 2)
            sos = signal.butter(1, [max(20.0, lo) / nyq, min(0.98, hi / nyq)], 'bandpass', output='sos')
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[a:b], zi=zi)
        out[a:b] = y
    return out


def delay(x, sec, n_total=None):
    d = N(sec)
    n_total = n_total or len(x) + d
    out = np.zeros(n_total, np.float32)
    m = min(len(x), n_total - d)
    if m > 0:
        out[d:d + m] = x[:m]
    return out


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


def glass_ping(seed, f, decay=None, amp=1.0, click=0.5):
    """A shard of glass: inharmonic plate modes + a hard tick."""
    r = dsp.rng(seed)
    decay = decay or (25 + f * 0.012) * r.uniform(0.7, 1.4)
    ratios = [1.0, r.uniform(1.45, 1.62), r.uniform(2.2, 2.5), r.uniform(3.0, 3.6)]
    amps = [1.0, r.uniform(.4, .8), r.uniform(.25, .5), r.uniform(.1, .3)]
    dur = min(0.7, 6.5 / decay)
    modes = [(f * ra, decay * ra ** 0.6, a) for ra, a in zip(ratios, amps)]
    y = modal_ir(modes, dur, seed)
    y = norm(y * np.minimum(1, taxis(len(y)) / 0.0002))
    if click:
        cl = dsp.highpass(burst(0.0008, seed + 3, 2.0), 3000, 2)
        y[:len(cl)] += click * norm(cl)
    return (y * amp).astype(np.float32)


def bounces(seed, first_amp, n_max=4, dt0=(0.05, 0.12), rest=(0.4, 0.6)):
    """Times/amps of an object bouncing to rest (geometric restitution)."""
    r = dsp.rng(seed)
    t, dt, a = 0.0, r.uniform(*dt0), first_amp
    out = []
    for _ in range(n_max):
        out.append((t, a))
        e = r.uniform(*rest)
        t += dt
        dt *= e
        a *= e * r.uniform(0.8, 1.1)
        if a < 0.03:
            break
    return out


def bubble(f0, seed, rise=0.5, amp=1.0, dmul=1.0):
    r = dsp.rng(seed)
    d = (40 + f0 * 0.05) * dmul
    dur = min(0.15, 6.5 / d)
    t = taxis(N(dur))
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.001)
    return (y * amp).astype(np.float32)


# ====================================================================== rooms
ROOMS = {
    'hall': dict(decay=2.7, damp=4500.0, predelay=0.020, er=9, er_span=0.065, hf=0.5),
    'aula': dict(decay=1.0, damp=5500.0, predelay=0.007, er=7, er_span=0.028, hf=0.55),
    'pasillo': dict(decay=1.8, damp=5200.0, predelay=0.008, er=8, er_span=0.07, hf=0.5, flutter=0.0175),
    'direccion': dict(decay=0.75, damp=4500.0, predelay=0.005, er=6, er_span=0.022, hf=0.5),
    'capilla': dict(decay=4.4, damp=3800.0, predelay=0.035, er=8, er_span=0.09, hf=0.45),
    'dormitorio': dict(decay=1.5, damp=4200.0, predelay=0.012, er=8, er_span=0.05, hf=0.45),
    'banos': dict(decay=1.45, damp=8000.0, predelay=0.007, er=9, er_span=0.03, hf=0.7, flutter=0.026),
    'cripta': dict(decay=3.1, damp=2900.0, predelay=0.018, er=8, er_span=0.05, hf=0.45),
    'torre': dict(decay=3.6, damp=3200.0, predelay=0.05, er=5, er_span=0.13, hf=0.4),
    'caja': dict(decay=0.22, damp=3500.0, predelay=0.002, er=6, er_span=0.006, hf=0.6),
}
_IR_CACHE = {}


def room_ir(decay, damp, predelay, er, er_span, hf, seed=7, flutter=0.0):
    key = (decay, damp, predelay, er, er_span, hf, seed, flutter)
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    n = N(decay * 1.35)
    t = taxis(n)
    r = dsp.rng(seed)
    w = r.standard_normal(n).astype(np.float32)
    lo = dsp.lowpass(w, damp, 2) * np.exp(-6.9 * t / decay)
    hi = dsp.highpass(w, damp, 2) * np.exp(-6.9 * t / (decay * hf))
    ir = (lo + 0.5 * hi) * np.minimum(1.0, t / max(0.004, min(0.05, decay * 0.03)))
    rms = np.sqrt(np.mean(ir[:N(0.05)] ** 2)) + 1e-9
    for _k in range(er):
        p = int(r.uniform(0.002, er_span) * SR)
        if p < n:
            ir[p] += r.uniform(0.4, 1.0) * r.choice([-1, 1]) * rms * 14
    if flutter:
        for k in range(1, 14):
            p = int(k * flutter * SR)
            if p < n:
                ir[p] += rms * 9 * 0.72 ** k * (-1) ** k
    ir = np.concatenate([np.zeros(N(predelay), np.float32), ir.astype(np.float32)])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    _IR_CACHE[key] = ir
    return ir


def verb(x, room, wet=0.3, dry=1.0, seed=7, **over):
    """Mono room reverb (dry + wet), output extended by the tail."""
    p = dict(ROOMS[room])
    p.update(over)
    ir = room_ir(p['decay'], p['damp'], p['predelay'], p['er'], p['er_span'], p['hf'], seed, p.get('flutter', 0.0))
    w = signal.fftconvolve(x, ir)
    out = np.zeros(len(w), np.float32)
    out[:len(x)] += dry * x
    out += wet * w * 3.0
    return out.astype(np.float32)


def cverb(x, room, wet=0.3, dry=1.0, seed=7, **over):
    """Circular (loop-safe) mono reverb: the tail wraps round to the start."""
    p = dict(ROOMS[room])
    p.update(over)
    ir = room_ir(p['decay'], p['damp'], p['predelay'], p['er'], p['er_span'], p['hf'], seed, p.get('flutter', 0.0))
    L = len(x)
    if len(ir) > L:
        ir = np.pad(ir, (0, -len(ir) % L)).reshape(-1, L).sum(0)
    w = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(ir, L), L)
    return (dry * x + wet * w * 3.0).astype(np.float32)


def fold(x, L):
    """Wrap everything past L back onto the start (circular buffer of length L)."""
    x = np.pad(x, (0, -len(x) % L))
    return x.reshape(-1, L).sum(0).astype(np.float32)


def cfilt(x, gain_fn):
    """Circular zero-phase filter defined by a gain function of frequency (Hz)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * gain_fn(f), len(x)).astype(np.float32)


def bumps(f, peaks, floor=0.0):
    """Sum of gaussian (log-frequency) bumps: peaks = [(centre_hz, width_oct, gain)]."""
    lf = np.log2(np.maximum(f, 1.0))
    g = np.full_like(f, floor, dtype=np.float64)
    for c, w, a in peaks:
        g += a * np.exp(-0.5 * ((lf - np.log2(c)) / w) ** 2)
    return g


# ====================================================================== 1. electric school bell
def timbre():
    """Electric bell: an interrupter-driven clapper hammering a steel gong ~23 times a second, at full tilt."""
    ring, tail = 4.0, 2.6
    n = N(ring + tail)
    r = dsp.rng(11)
    times, t = [], 0.004
    while t < ring:
        times.append(t)
        rate = 23.0 * (1 + 0.04 * r.standard_normal())
        if t < 0.12:
            rate *= 0.55 + 0.45 * t / 0.12  # armature getting going
        t += 1.0 / rate
    times = np.array(times)
    amps = r.uniform(0.72, 1.0, len(times))
    imp = impulses(n, times, amps)
    exc = signal.fftconvolve(imp, half_sine(0.00035))[:n]
    f0 = 905.0
    modes = []
    for ra, a, d in [(1.0, 1.0, 3.2), (2.31, .85, 4.2), (2.72, .6, 4.8), (4.06, .55, 6.5), (5.21, .42, 8.0),
                     (6.64, .3, 10.5), (8.17, .2, 13), (9.75, .12, 17), (11.6, .07, 21)]:
        for sp in (-0.0021, 0.0021):  # split doublets -> the shimmering beat of a real gong
            modes.append((f0 * ra * (1 + sp + r.uniform(-4e-4, 4e-4)), d, a * 0.5))
    gong = excite(exc, modes, 3.0, seed=12)[:n]
    # the clapper rests on the gong for a few ms after each blow: periodic damping -> the "rrrrr" flutter
    cont = signal.fftconvolve(impulses(n, times, np.ones(len(times))), np.hanning(N(0.014))[N(0.007):])[:n]
    gong = gong * (1 - 0.42 * np.minimum(1, cont))
    clicks = dsp.highpass(signal.fftconvolve(imp, burst(0.0006, 13, 2.0))[:n], 3500, 2)
    housing = excite(signal.fftconvolve(imp, burst(0.0012, 14))[:n],
                     [(380, 70, 1), (720, 90, .7), (1290, 120, .5), (2100, 160, .3)], 0.08)[:n]
    tt = taxis(n)
    on = smooth((tt < ring).astype(np.float32), 0.01)
    coil = dsp.lowpass(np.tanh(4 * np.sin(TWO_PI * 100 * tt)) * on, 900, 2)
    y = norm(gong) + 0.22 * norm(clicks) * on + 0.2 * norm(housing) + 0.03 * coil
    y = dsp.drive(y * 1.25, 1.7)  # full volume, a little overdriven
    y = verb(y, 'hall', wet=0.09, decay=1.6)
    return y


# ====================================================================== 2. bronze bells
BELL_PARTIALS = [  # (ratio to prime, amplitude, decay 1/s): hum, prime, tierce, quint, nominal, ...
    (0.5, .62, .27), (1.0, .55, .48), (1.19, .80, .66), (1.50, .30, .95), (2.0, 1.0, .82),
    (2.51, .42, 1.45), (2.66, .32, 1.75), (3.01, .28, 2.1), (4.0, .20, 2.8), (4.2, .13, 3.2),
    (5.43, .10, 4.1), (6.0, .07, 4.9), (6.8, .05, 5.9), (8.0, .035, 7.2)]


def bronze_bell(f, dur, seed, strength=1.0, decay_scale=1.0):
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    y = np.zeros(n)
    for ra, a, d in BELL_PARTIALS:
        fr = f * ra * (1 + r.uniform(-0.0015, 0.0015))
        amp = a * strength ** (ra * 0.6)
        beat = r.uniform(0.25, 1.3)
        dd = d / decay_scale
        y += amp * (np.sin(TWO_PI * fr * t + r.uniform(0, TWO_PI))
                    + 0.6 * np.sin(TWO_PI * (fr + beat) * t + r.uniform(0, TWO_PI))) * np.exp(-dd * t)
    y *= np.minimum(1, t / 0.0025)
    y = norm(y)
    # the clapper's clang: a dense inharmonic cluster that dies within half a second
    nc = N(0.7)
    tc = taxis(nc)
    cl = np.zeros(nc)
    for _k in range(26):
        cl += r.uniform(.2, 1) * np.sin(TWO_PI * r.uniform(700, 6000) * tc + r.uniform(0, TWO_PI)) * np.exp(-tc * r.uniform(10, 38))
    cl *= np.minimum(1, tc / 0.001)
    strike = bp(burst(0.09, seed + 5, 3.0), 500, 5000)
    thud = np.sin(TWO_PI * 190 * tc) * np.exp(-tc * 26)
    y[:nc] += 0.33 * strength * norm(cl) + 0.08 * thud
    y[:len(strike)] += 0.35 * strength * norm(strike)
    # a swinging bell: slow amplitude sway
    y *= 1 + 0.05 * np.sin(TWO_PI * 0.42 * t + r.uniform(0, 6))
    return y.astype(np.float32)


def campana():
    x = bronze_bell(146.8, 9.6, 21, strength=1.0)
    x = dsp.lowpass(x, 7500, 2)  # up in the tower
    x = fit(verb(x, 'torre', wet=0.33), N(9.6))
    x *= env_pts(len(x), [(0, 1), (5.8, 1), (9.6, 0)]) ** 2
    return x


def campana_triple():
    total = 9.4
    out = np.zeros(N(total), np.float32)
    for k, (t0, s, ds) in enumerate([(0.0, 0.92, 0.85), (2.2, 0.96, 0.9), (4.4, 1.12, 1.35)]):
        b = bronze_bell(146.8, total - t0, 31 + k, strength=s, decay_scale=ds)
        tb = taxis(len(b))
        sub = np.sin(TWO_PI * 49 * tb * (1 + 0.04 * np.exp(-tb * 6))) * np.exp(-tb * 2.4) * np.minimum(1, tb / 0.01)
        add(out, b + 0.22 * sub, t0, 1.0 if k < 2 else 1.08)
    out = dsp.lowpass(out, 7500, 2)
    out = fit(verb(out, 'torre', wet=0.35), N(total))
    out *= env_pts(len(out), [(0, 1), (7.0, 1), (total, 0)]) ** 2
    return out


# ====================================================================== 3. PA chime
def horn(x, sat=1.6):
    """1980s horn loudspeaker + tired amplifier."""
    y = dsp.highpass(x, 420, 4)
    y = dsp.lowpass(y, 5200, 4)
    y = dsp.peak(y, 1750, 6.0, 1.3)
    y = dsp.peak(y, 3100, 3.0, 2.0)
    y = dsp.drive(y * sat, 1.4)
    return dsp.lowpass(y, 5000, 4)  # the horn cannot reproduce the distortion's top end either


def chime_note(f, seed, dur=2.0):
    n = N(dur)
    t = taxis(n)
    idx = 2.0 * np.exp(-t * 7) + 0.18
    fm = np.sin(TWO_PI * f * t + idx * np.sin(TWO_PI * f * t))
    y = fm * np.exp(-t * 1.5) + 0.18 * np.sin(TWO_PI * 4.0 * f * t) * np.exp(-t * 5) \
        + 0.05 * np.sin(TWO_PI * 10.0 * f * t) * np.exp(-t * 11)
    y *= np.minimum(1, t / 0.003)
    mallet = bp(burst(0.005, seed, 2.0), 1500, 6000)
    y = norm(y)
    y[:len(mallet)] += 0.12 * norm(mallet)
    return y


def pa_chime():
    total = 3.1
    n = N(total)
    t = taxis(n)
    chime = np.zeros(n, np.float32)
    add(chime, chime_note(659.3, 1), 0.22)
    add(chime, chime_note(523.3, 2), 0.84, 0.95)
    hum = sum((1.0 / k ** 0.8) * (1.6 if k % 2 else 1.0) * np.sin(TWO_PI * 50 * k * t + k) for k in range(1, 14))
    line = smooth((t > 0.03).astype(np.float32), 0.004) * env_pts(n, [(0, 1), (2.2, 1), (total, 0.5)])
    hiss = white(n, 3)
    pop = np.zeros(n, np.float32)
    tp = taxis(N(0.12))
    add(pop, np.sin(TWO_PI * 38 * tp) * np.exp(-tp * 35), 0.03, 1.0)
    add(pop, burst(0.002, 4, 2.0), 0.03, 0.6)
    src = chime + (0.035 * norm(hum) + 0.006 * hiss) * line + 0.5 * pop
    y = horn(src)
    # several horns around the building: the hall hears the nearest one plus the others late and dull
    y = y + 0.4 * delay(dsp.lowpass(y, 3200, 2), 0.083, len(y)) + 0.22 * delay(dsp.lowpass(y, 2300, 2), 0.205, len(y))
    y = verb(y, 'hall', wet=0.24)
    return y


# ====================================================================== 4. wind in the shutters
SHUTTER = [(240, 35, .6), (410, 45, 1.0), (690, 55, .8), (1120, 70, .6), (1750, 90, .4), (2600, 120, .25)]


def creak(dur, seed, rate0=40.0, rate1=18.0, modes=((220, 40, 1), (510, 55, .6), (1150, 80, .35), (2300, 120, .2)),
          shape=None, tail=0.3, hiss=0.12):
    """Stick-slip creak (hinge, board, joint)."""
    n = N(dur)
    k = np.linspace(0, 1, n)
    rate = rate0 * (rate1 / rate0) ** k
    env = shape if shape is not None else np.sin(np.pi * k) ** 0.6
    idx, a = stick_slip(n, rate, seed, 0.3, env)
    exc = pulse_train(n, idx, a, burst(0.0015, seed + 1))
    y = excite(exc, detune(list(modes), dsp.rng(seed), 0.04), tail)
    if hiss:
        h = bp(white(len(y), seed + 2), 900, 4500)
        y = norm(y) + hiss * norm(h) * fit(env, len(y))
    return norm(y)


def viento(v):
    r = dsp.rng(40 + v)
    if v == 1:
        dur = 3.6
        pts = [(0, 0), (0.6, .3), (1.35, 1.0), (1.9, .85), (2.6, .45), (3.6, 0)]
    else:
        dur = 3.9
        pts = [(0, 0), (0.55, .5), (1.05, .72), (1.45, .42), (2.15, 1.0), (2.8, .6), (3.9, 0)]
    n = N(dur)
    g = env_pts(n, pts)
    g = np.clip(g * (1 + 0.32 * snoise(n, 5, 41 + v) + 0.15 * snoise(n, 13, 43 + v)), 0, None)
    g = smooth(g, 0.02)
    body = tv_filter(colored(n, 'pink', 44 + v), 'lp', 220 + 1700 * g ** 1.3) * (0.12 + g)
    rumble = dsp.lowpass(colored(n, 'brown', 45 + v), 140, 2) * g
    # whistling through the gaps of the shutters: narrow-band noise around a wandering centre
    fc = (520 if v == 1 else 610) * (1 + 0.35 * g + 0.07 * snoise(n, 0.8, 46 + v))
    ph = TWO_PI * np.cumsum(fc) / SR
    a1, a2 = dsp.lowpass(white(n, 47 + v), 11, 2), dsp.lowpass(white(n, 48 + v), 11, 2)
    wh = a1 * np.cos(ph) - a2 * np.sin(ph)
    wh /= np.std(wh) + 1e-9
    ph2 = TWO_PI * np.cumsum(fc * 1.47) / SR
    wh2 = a2 * np.cos(ph2) + a1 * np.sin(ph2)
    wh2 /= np.std(wh2) + 1e-9
    whistle = wh * g ** 2.4 + 0.45 * wh2 * g ** 3
    # rattle: the shutters knocking in their frames, more often when the gust pushes
    lam = 26 * np.maximum(0, g - 0.3) ** 1.2
    rat = np.zeros(n + N(0.4), np.float32)
    for j, i in enumerate(poisson_times(lam, 49 + v)):
        a = g[i] * r.uniform(0.25, 1.0)
        kn = knock(500 + j + 50 * v, SHUTTER, 0.25, contact=0.0012, click=0.25)
        add(rat, kn, i / SR, a)
        if r.random() < 0.45:
            add(rat, kn, i / SR + r.uniform(0.01, 0.028), a * 0.45)
    # big bangs: a shutter slapped against the frame by the gust
    bang_t = [1.42, 2.15] if v == 1 else [2.2]
    for k, tb in enumerate(bang_t):
        kn = knock(600 + k + 10 * v, SHUTTER + [(150, 25, .9), (95, 18, .6)], 0.5, contact=0.002, click=0.45)
        add(rat, kn, tb, 1.0 if k == 0 else 0.6)
        add(rat, knock(610 + k + 10 * v, SHUTTER, 0.3, click=0.2), tb + 0.032, 0.35)
    if v == 2:
        cr = creak(0.55, 620, 34, 16, ((330, 30, 1), (760, 45, .7), (1420, 70, .45), (2650, 110, .25)))
        add(rat, cr, 1.55, 0.35)
    y = 0.6 * norm(body) + 0.35 * norm(rumble) + 0.33 * norm(whistle) * 0.8
    y = fit(y, len(rat)) + 0.55 * norm(rat)
    return verb(y, 'dormitorio', wet=0.12)


# ====================================================================== 5. plaster dust
def polvo():
    dur = 3.2
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(31)
    out = np.zeros(n + N(0.4), np.float32)
    # grit pattering on the tiles: a sparse-ish rain of micro-impacts, each grain its own size (pitch)
    lam = 420 * np.minimum(1, t / 0.06) * np.exp(-np.maximum(0, t - 0.06) / 0.5) + 45 * np.exp(-t / 1.2)
    lam *= 0.6 + 0.4 * (snoise(n, 6, 35) > -0.3)  # it comes in little gushes
    idx = poisson_times(lam, 32)
    amps = np.minimum(1.0, r.exponential(0.22, len(idx)))
    imp = np.zeros(n, np.float32)
    np.add.at(imp, idx, amps)
    grit = dsp.highpass(signal.fftconvolve(imp, burst(0.0003, 33, 2.0))[:n], 2500, 2)
    pings = np.zeros(n + N(0.05), np.float32)
    for j, i in enumerate(idx[::3]):
        add(pings, glass_ping(3000 + j, r.uniform(2500, 9000), r.uniform(250, 600), 1.0, 0.4), i / SR, amps[3 * j] * 0.5)
    hiss = bp(white(n, 34), 2000, 8000) * smooth(lam / 420, 0.08) ** 1.2
    out[:n] += 0.55 * norm(grit) + 0.35 * norm(pings[:n]) + 0.035 * norm(hiss)
    # plaster cracking loose up there
    for j in range(9):
        add(out, knock(700 + j, [(900, 140, 1), (1700, 180, .7), (2900, 240, .5)], 0.06, click=0.5), 0.004 * j * j * 0.4, 0.25 * (1 - j / 10))
    # flakes and chunks hitting the tiles and skittering
    for k, (tf, a) in enumerate([(0.06, .9), (0.11, .55), (0.19, .7), (0.33, .45), (0.52, .35), (0.95, .4), (1.6, .3), (2.25, .18)]):
        for j, (tb, ab) in enumerate(bounces(720 + k, a, 4, (0.03, 0.07), (0.3, 0.5))):
            m = [(r.uniform(1500, 2200), 150, 1), (r.uniform(2600, 3400), 200, .7), (r.uniform(4000, 5200), 260, .5),
                 (r.uniform(600, 900), 90, .4)]
            add(out, knock(730 + 7 * k + j, m, 0.08, contact=0.0004, click=0.6), tf + tb, ab * 0.8)
    return verb(out, 'hall', wet=0.14)


# ====================================================================== 6. door slam
PANEL = [(68, 16, .9), (96, 20, 1.0), (143, 25, .9), (205, 30, .8), (290, 34, .7), (410, 38, .55), (590, 44, .45),
         (830, 55, .35), (1180, 70, .25), (1700, 95, .18), (2500, 130, .12)]
METAL = [(1620, 25, .5), (2750, 35, 1), (4100, 45, .8), (5650, 60, .6), (7300, 80, .4)]


def door_impact(seed, amp=1.0):
    r = dsp.rng(seed)
    n = N(1.2)
    exc = np.zeros(n, np.float32)
    hs = half_sine(0.0035)
    exc[:len(hs)] += hs
    hs2 = half_sine(0.0005)
    exc[N(0.0015):N(0.0015) + len(hs2)] += 0.7 * hs2
    body = norm(excite(exc, detune(PANEL, r, 0.05), 1.2)[:n])
    crack = dsp.highpass(burst(0.014, seed + 1, 3.0), 1200, 2)
    tb = taxis(n)
    sub = np.sin(TWO_PI * np.cumsum(48 * (1 + 0.5 * np.exp(-tb * 25))) / SR) * np.exp(-tb * 11) * np.minimum(1, tb / 0.003)
    y = body + 0.65 * fit(norm(crack), n) + 0.5 * sub
    return (y * amp).astype(np.float32)


def door_slam(v):
    r = dsp.rng(50 + v)
    pre = 0.24
    n = N(pre + 1.4)
    out = np.zeros(n, np.float32)
    # the swing: air pushed by the heavy leaf, accelerating into the frame
    nw = N(pre)
    tw = taxis(nw)
    whoosh = tv_filter(colored(nw, 'pink', 51 + v), 'lp', 250 + 900 * (tw / pre) ** 2) * (tw / pre) ** 2.5
    add(out, norm(whoosh), 0.0, 0.18)
    ti = pre
    add(out, door_impact(52 + v), ti)
    add(out, knock(53 + v, METAL, 0.5, click=0.5), ti + 0.009, 0.32)  # latch bolt snapping into the strike plate
    if v == 2:  # bounced off the frame first, then caught
        add(out, door_impact(56, 0.5), ti + 0.115)
        add(out, knock(57, METAL, 0.5, click=0.5), ti + 0.125, 0.28)
    # the leaf chattering in its frame, then the glass panes rattling in their putty
    t, a = ti + 0.03, 0.4
    for j in range(7 if v == 1 else 5):
        add(out, knock(60 + j + 10 * v, PANEL[5:], 0.12, contact=0.001, click=0.3), t, a)
        t += r.uniform(0.018, 0.03) * (1 + 0.15 * j)
        a *= r.uniform(0.55, 0.75)
    for j in range(14):
        tg = ti + 0.02 + r.exponential(0.06)
        add(out, glass_ping(80 + j + 20 * v, r.uniform(2400, 6500), amp=0.06 * r.uniform(.4, 1)), tg)
    hinge = modal_ir([(1630 * r.uniform(.97, 1.03), 6, 1), (3880, 9, .4)], 0.8, 90 + v)
    add(out, hinge, ti + 0.004, 0.025)
    return verb(out, 'hall', wet=0.62, decay=3.3, predelay=0.024)


# ====================================================================== 7. chalk
BOARD = [(170, 30, 1), (290, 35, .7), (480, 45, .5), (760, 60, .35), (1150, 80, .2)]
CHALK = [(3100, 300, 1), (4700, 360, .7), (6600, 420, .5)]
STROKES = {'A': 'lls', 'B': 'lcc', 'C': 'c', 'D': 'lc', 'E': 'lsss', 'I': 'l', 'J': 'c', 'L': 'ls', 'M': 'llll',
           'N': 'lll', 'O': 'c', 'P': 'lc', 'R': 'lcl', 'S': 'c', 'T': 'sl', 'U': 'c', '.': 'd', '_': 'u'}
STROKE_LEN = {'l': (0.10, 0.15), 's': (0.05, 0.08), 'c': (0.16, 0.24), 'd': (0.012, 0.018), 'u': (0.32, 0.4)}


def chalk_stroke(seed, dur, pressure=1.0, speed=1.0, squeak=False, tap=1.0):
    r = dsp.rng(seed)
    n = N(dur)
    tail = N(0.2)
    out = np.zeros(n + tail, np.float32)
    k = np.linspace(0, 1, n)
    env = np.minimum(1, k * dur / 0.004) * np.minimum(1, (1 - k) * dur / 0.014)
    env *= pressure * (1 + 0.25 * snoise(n, 18, seed + 1))
    tex = bp(white(n, seed + 2), 1800, 6500)
    tex = dsp.lowpass(dsp.peak(tex, 3300, 7.0, 1.4), 7500, 2)
    tex *= grain(n, 160 + 300 * speed, seed + 3, 2.4) * 0.8 + 0.2  # gritty, crackly drag rather than hiss
    ci = poisson_times(220 * speed * env, seed + 4)
    crumbs = dsp.highpass(pulse_train(n, ci, r.uniform(.3, 1, len(ci)), burst(0.0004, seed + 5)), 2000, 2)
    scratch = norm(tex) * env * (0.7 + 0.3 * speed) + 0.3 * norm(crumbs + 1e-9) * env
    board = excite(bp(white(n, seed + 6), 200, 3000) * env, BOARD, 0.12)
    out[:n] += 0.8 * scratch
    out += 0.22 * fit(norm(board), len(out))
    if tap:
        add(out, knock(seed + 8, BOARD, 0.12, contact=0.0004, click=0.0), 0, 0.6 * tap)
        tk = excite(fit(half_sine(0.00015), N(0.02)), CHALK, 0.03)
        add(out, norm(tk), 0, 0.75 * tap)
    if squeak:
        s0 = r.uniform(0.1, 0.35)
        sl = r.uniform(0.4, 0.75) * (1 - s0)
        ns = N(dur * sl)
        if ns > N(0.03):
            ks = np.linspace(0, 1, ns)
            f0 = r.uniform(1300, 2900)
            fr = f0 * (1 + r.uniform(-0.1, 0.1) * ks + 0.02 * snoise(ns, 40, seed + 9))
            ph = TWO_PI * np.cumsum(fr) / SR
            sq = sum(a * np.sin(m * ph) for m, a in [(1, 1.0), (2, .45), (3, .3), (4, .12)])
            gate = smooth((snoise(ns, 70, seed + 10) > -0.35).astype(np.float32), 0.003)
            sq = sq * gate * np.minimum(1, ks * dur * sl / 0.01) * np.minimum(1, (1 - ks) * dur * sl / 0.015)
            add(out, norm(sq), dur * s0, r.uniform(0.35, 0.7))
    return out


def tiza_escribe(v):
    r = dsp.rng(60 + v)
    if v == 1:
        words, speeds, sq = ['TE', 'DIJE'], [1.25, 1.05], 0.22
    elif v == 2:
        words, speeds, sq = ['NO', 'MIRES'], [1.2, 1.45], 0.18
    else:
        words, speeds, sq = ['ELLA', '._'], [0.8, 1.6], 0.3
    plan = []
    t = 0.03
    for wi, (w, sp) in enumerate(zip(words, speeds)):
        for li, ch in enumerate(w):
            # v3 accelerates through the word: slow, deliberate, then frantic
            s = sp * (1 + 0.6 * li / max(1, len(w) - 1)) if v == 3 and wi == 0 else sp * r.uniform(0.9, 1.1)
            for si, st in enumerate(STROKES[ch]):
                lo, hi = STROKE_LEN[st]
                d = r.uniform(lo, hi) / s
                plan.append((t, d, s, st, si == 0))
                t += d + r.uniform(0.02, 0.045) / s
            t += r.uniform(0.04, 0.08) / s
        t += r.uniform(0.18, 0.26)
    out = np.zeros(N(t + 0.5), np.float32)
    for j, (t0, d, s, st, first) in enumerate(plan):
        pres = r.uniform(0.75, 1.0) * (1.1 if st == 'u' else 1.0)
        squeak = st in 'cu' and r.random() < sq * 2.2 or r.random() < sq * 0.5
        tap = (1.0 if first else r.uniform(0.35, 0.7)) * (1.6 if st == 'd' else 1.0)
        add(out, chalk_stroke(1000 * v + 7 * j, d, pres, s, squeak and st != 'd', tap), t0)
    return verb(out, 'aula', wet=0.07)


def tiza_rompe():
    r = dsp.rng(70)
    n = N(1.3)
    out = np.zeros(n, np.float32)
    add(out, chalk_stroke(71, 0.07, 0.9, 1.4, True, 1.0), 0.0, 0.3)  # pressing harder...
    ts = 0.075
    cl = np.zeros(N(0.05), np.float32)
    for k, (dt, a) in enumerate([(0, 1.0), (0.0007, .6), (0.0021, .45), (0.0045, .25)]):
        add(cl, half_sine(0.00012), dt, a)
    snap = excite(cl, [(3300, 260, 1), (5200, 330, .8), (7900, 420, .6), (10400, 520, .4), (2100, 200, .5)], 0.06)
    add(out, norm(snap), ts, 1.0)
    add(out, dsp.highpass(burst(0.004, 72, 2.0), 2500, 2), ts, 0.6)
    add(out, knock(73, BOARD, 0.15, contact=0.0005, click=0.0), ts, 0.45)
    for j in range(16):  # crumbs
        add(out, glass_ping(740 + j, r.uniform(5000, 9500), 400, 0.06 * r.uniform(.3, 1), 0.8), ts + 0.01 + r.exponential(0.05))
    ledge = [(520, 60, 1), (980, 80, .6), (1800, 110, .4)]
    for j, (tb, a) in enumerate(bounces(75, 0.65, 6, (0.085, 0.1), (0.5, 0.62))):
        m = ledge + [(r.uniform(3800, 4400), 300, .8), (r.uniform(6000, 7000), 380, .6)]
        add(out, knock(76 + j, m, 0.08, contact=0.0003, click=0.5), ts + 0.36 + tb, a)
    rollt = ts + 0.36 + 0.24
    nr = N(0.22)
    roll = bp(white(nr, 79), 2500, 7000) * grain(nr, 60, 80, 3.0) * np.linspace(1, 0, nr) ** 2
    add(out, norm(roll), rollt, 0.06)
    return verb(out, 'aula', wet=0.12)


# ====================================================================== 8. sixteen chairs
CHAIR = [(165, 35, 1.0), (330, 45, .8), (590, 55, .6), (940, 70, .5), (1480, 90, .35), (2350, 120, .25), (3600, 160, .15)]


def pupitres_giran():
    T = 2.32
    n = N(T + 1.0)
    out = np.zeros(n, np.float32)
    r = dsp.rng(400)
    for i in range(16):
        ri = dsp.rng(401 + i)
        start = 0.0 if i < 4 else ri.uniform(0.02, 0.3)
        ln = T - start
        m = N(ln)
        k = np.linspace(0, 1, m)
        v = np.minimum(1, k * ln / ri.uniform(0.12, 0.3)) ** 0.7
        v *= 0.55 + 0.45 * k ** 1.5  # they speed up as they swing round to face you
        v *= 1 + 0.35 * snoise(m, 3.5, 410 + i)
        for _p in range(ri.integers(0, 3)):  # a hitch: the chair sticks, then lurches on
            c = ri.uniform(0.2, 0.8)
            v *= 1 - 0.85 * np.exp(-0.5 * ((k - c) * ln / 0.05) ** 2)
        v *= np.minimum(1, (1 - k) * ln / 0.03) ** 0.5  # hard stop at T
        v = np.clip(v, 0, None)
        fac = ri.uniform(0.7, 1.35)
        idx, a = stick_slip(m, (75 + 230 * v) * fac, 420 + i, 0.3, v, 0.3)
        exc = pulse_train(m, idx, a, burst(0.0005, 430 + i))
        modes = [(f * fac ** 0.3 * ri.uniform(0.9, 1.1), d, am) for f, d, am in CHAIR]
        sc = norm(excite(exc, modes, 0.15)[:m])
        rough = bp(white(m, 440 + i), 900, 5500) * grain(m, 140, 450 + i, 2.0) * v
        joints = np.zeros(m, np.float32)
        for _j in range(ri.integers(3, 8)):  # legs crossing tile grout
            tj = ri.uniform(0.15, 0.95)
            add(joints, knock(460 + 10 * i + _j, CHAIR[3:] + [(4200, 300, .6)], 0.06, contact=0.0004, click=0.5), tj * ln, v[int(tj * (m - 1))])
        ch = sc + 0.35 * norm(rough) + 0.3 * joints
        d = ri.uniform(0.0, 0.25) if i < 3 else ri.uniform(0.35, 1.0)  # three right next to you, the rest across the room
        ch = dsp.lowpass(ch, 11000 - 6500 * d, 2) / (1 + 2.2 * d)
        add(out, ch, start, 0.72)
        # all of them land at once: four legs clack on the tiles
        tl = T + ri.normal(0, 0.003)
        add(out, knock(480 + i, CHAIR + [(3900, 260, .5)], 0.25, contact=0.0009, click=0.5), tl, 1.6 / (1 + 1.6 * d))
        add(out, knock(490 + i, CHAIR[2:] + [(4400, 300, .5)], 0.12, contact=0.0006, click=0.5), tl + ri.uniform(0.012, 0.03), 0.35 / (1 + 1.6 * d))
    tb = taxis(N(0.5))
    add(out, np.sin(TWO_PI * np.cumsum(62 * (1 + 0.6 * np.exp(-tb * 40))) / SR) * np.exp(-tb * 14) * np.minimum(1, tb / 0.002), T, 1.3)
    out = norm(out)
    return verb(out, 'aula', wet=0.2, decay=1.15)


# ====================================================================== 9. lamp burst
def farol_revienta(v):
    r = dsp.rng(90 + v)
    n = N(2.4)
    out = np.zeros(n, np.float32)
    arc_len = {1: 0.09, 2: 0.26, 3: 0.025}[v]
    na = N(arc_len)
    ta = taxis(na)
    buzz = np.tanh(5 * np.sin(TWO_PI * 100 * ta)) * (1 + 0.5 * snoise(na, 40, 91 + v))
    sizzle = dsp.highpass(pulse_train(na, poisson_times(np.full(na, 900.0), 92 + v), r.uniform(.2, 1, len(poisson_times(np.full(na, 900.0), 92 + v))), burst(0.0004, 93)), 2000, 2)
    arc_env = np.minimum(1, ta / arc_len) ** 1.5
    if v == 2:  # sputtering filament
        arc_env *= (snoise(na, 25, 94) > -0.2)
        arc_env = smooth(arc_env, 0.003)
    arc = (0.5 * norm(bp(buzz, 100, 3000)) + norm(sizzle + 1e-9)) * arc_env
    add(out, arc, 0.0, 0.32)
    tp = arc_len
    # POP: pressure + glass bursting
    nb = N(0.25)
    tb = taxis(nb)
    thump = np.sin(TWO_PI * np.cumsum(65 * (1 + 1.2 * np.exp(-tb * 60))) / SR) * np.exp(-tb * 30) * np.minimum(1, tb / 0.0008)
    add(out, thump, tp, 0.6)
    add(out, dsp.highpass(burst(0.004, 95 + v, 2.0), 700, 2), tp, 1.0)
    for j in range(60):
        tj = tp + r.exponential(0.012)
        add(out, glass_ping(1100 + 100 * v + j, r.uniform(2500, 11000), amp=r.uniform(.15, .55) * np.exp(-(tj - tp) / 0.03)), tj)
    if v != 3:  # lantern frame ringing
        add(out, modal_ir([(1240 * r.uniform(.95, 1.05), 10, 1), (2980, 14, .6), (4710, 20, .4)], 1.0, 96 + v), tp + 0.001, 0.05)
    # shards land on the tiles ~0.6 s later and skitter
    count = {1: 38, 2: 30, 3: 50}[v]
    for j in range(count):
        tl = tp + r.normal(0.62, 0.12) + r.exponential(0.08)
        size = r.uniform(0, 1) ** 2
        f = 2200 + (1 - size) * 8000
        for k, (tbn, ab) in enumerate(bounces(1300 + 100 * v + j, r.uniform(0.15, 0.6) * (0.5 + size), 4, (0.03, 0.08), (0.35, 0.55))):
            add(out, glass_ping(1500 + 300 * v + 4 * j + k, f * r.uniform(0.9, 1.1), amp=ab), tl + tbn)
        if size > 0.6:
            ns = N(r.uniform(0.05, 0.12))
            add(out, bp(white(ns, 1600 + j), 2500, 8000) * np.linspace(1, 0, ns) * 0.06, tl + 0.02)
    if v == 3:  # sparks still spitting from the socket
        for j in range(5):
            ts = tp + 0.15 + r.uniform(0, 0.8)
            ns = N(r.uniform(0.01, 0.04))
            add(out, dsp.highpass(white(ns, 1700 + j), 2500, 2) * np.linspace(1, 0, ns), ts, 0.12)
    return verb(out, 'pasillo', wet=0.24)


# ====================================================================== 10. lights out
def luces_fuera():
    total = 3.6
    n = N(total)
    t = taxis(n)
    t0 = 0.55
    r = dsp.rng(100)
    # buzzing tubes and ballasts (50 Hz mains -> 100 Hz magnetostriction), a deep transformer hum
    buzz = np.tanh(3.5 * np.sin(TWO_PI * 100 * t)) + 0.3 * np.tanh(6 * np.sin(TWO_PI * 200 * t + 1.0))
    buzz = bp(buzz, 90, 4000) * (1 + 0.15 * snoise(n, 6, 101))
    hiss = bp(white(n, 102), 3000, 9000) * 0.25
    buzz_env = np.where(t < t0, 1.0, np.exp(-(t - t0) * 40))
    flick = np.exp(-0.5 * ((t - (t0 + 0.42)) / 0.025) ** 2) * 0.35  # one tube spits once more
    tubes = (norm(buzz) + hiss) * smooth(np.maximum(buzz_env, flick), 0.003)
    f = np.where(t < t0, 100.0, 100 * (0.45 + 0.55 * np.exp(-(t - t0) * 1.1)))  # motor/transformer winding down
    ph = TWO_PI * np.cumsum(f) / SR
    hum = np.sin(ph / 2) + 0.7 * np.sin(ph) + 0.35 * np.sin(1.5 * ph) + 0.2 * np.sin(2 * ph)
    hum_env = np.where(t < t0, 1.0, np.exp(-(t - t0) * 1.5)) * np.minimum(1, t / 0.15)
    y = 0.16 * tubes * np.minimum(1, t / 0.15) + 0.13 * norm(hum) * hum_env
    out = np.zeros(n + N(0.3), np.float32)
    out[:n] = y
    # KA-: lever and spring
    add(out, knock(103, [(1850, 60, 1), (3200, 80, .8), (5100, 110, .6), (7200, 150, .4)], 0.2, contact=0.0003, click=0.6), t0 - 0.045, 0.55)
    tsp = taxis(N(0.3))
    add(out, np.sin(TWO_PI * 640 * tsp * (1 + 0.01 * np.exp(-tsp * 20))) * np.exp(-tsp * 18), t0 - 0.04, 0.06)
    # spark across the knife contacts
    ns = N(0.025)
    spk = dsp.highpass(pulse_train(ns, poisson_times(np.full(ns, 3000.0), 104), r.uniform(.3, 1, len(poisson_times(np.full(ns, 3000.0), 104))), burst(0.0003, 105)), 1800, 2)
    add(out, norm(spk + 1e-9), t0 - 0.002, 0.3)
    # -CHUNK: the contact block slams home in its iron box
    box = [(85, 38, 1), (140, 42, .8), (260, 50, .7), (410, 60, .5), (720, 75, .35), (1300, 95, .25), (2400, 130, .2)]
    add(out, knock(106, box, 0.6, contact=0.0025, click=0.5), t0, 1.3)
    tb = taxis(N(0.8))
    add(out, np.sin(TWO_PI * 46 * tb) * np.exp(-tb * 7) * np.minimum(1, tb / 0.004), t0, 0.55)
    for k, tt in enumerate([1.25, 1.95, 2.75]):  # cooling glass and filaments ticking in the dark
        add(out, glass_ping(107 + k, r.uniform(3800, 6500), 260, 1.0, 0.6), tt, 0.05)
    return verb(out, 'hall', wet=0.3)


# ====================================================================== 11. dragged chair (dormitory)
HEAVY_CHAIR = [(95, 15, 1.0), (180, 22, .9), (310, 30, .75), (540, 40, .55), (880, 55, .4), (1400, 75, .28), (2300, 110, .15)]
FLOOR = [(70, 12, .8), (140, 18, .9), (260, 26, .6), (430, 35, .4)]


def silla_arrastra(v):
    r = dsp.rng(110 + v)
    dur = 1.5
    n = N(dur)
    if v == 1:
        sp = env_pts(n, [(0, 0), (0.18, .75), (0.5, 1.0), (0.95, .85), (1.3, .7), (1.44, 0), (1.5, 0)])
    else:  # two pulls with a catch on a board seam in between
        sp = env_pts(n, [(0, 0), (0.12, .9), (0.48, .8), (0.58, 0), (0.83, 0), (0.92, 1.0), (1.3, .75), (1.42, 0), (1.5, 0)])
    sp = np.clip(sp * (1 + 0.28 * snoise(n, 4, 111 + v)), 0, None)
    rate = 16 + 32 * sp
    idx, a = stick_slip(n, rate, 112 + v, 0.35, sp, 0.4)
    exc = pulse_train(n, idx, a, burst(0.0025, 113))
    groan = norm(excite(exc, detune(HEAVY_CHAIR + FLOOR, r, 0.03), 0.4))
    # leg squeal riding on top, intermittent
    idx2, a2 = stick_slip(n, 135 + 60 * sp, 114 + v, 0.15, sp * (snoise(n, 5, 115 + v) > 0.1), 0.5)
    squeal = norm(excite(pulse_train(n, idx2, a2, half_sine(0.0004)), [(620, 40, 1), (1240, 55, .6), (1870, 70, .4), (2480, 90, .25)], 0.15) + 1e-9)
    rough = dsp.lowpass(bp(white(n, 116 + v), 300, 2200), 2600, 2) * grain(n, 90, 117 + v, 2.2) * sp
    y = np.zeros(len(groan) + N(0.6), np.float32)
    y[:len(groan)] += groan
    y[:len(squeal)] += 0.2 * squeal
    y[:n] += 0.2 * norm(rough)
    # floorboard seams under the legs: double knocks (front legs, back legs)
    pos = np.cumsum(sp) / SR
    seams = np.searchsorted(pos, np.arange(0.11, pos[-1], 0.11) + r.uniform(0, 0.05))
    for j, s in enumerate(seams):
        if s < n:
            for k, dt in enumerate((0.0, r.uniform(0.04, 0.07))):
                add(y, knock(118 + 3 * j + k, FLOOR + [(900, 60, .4)], 0.25, contact=0.002, click=0.15), s / SR + dt, 0.35 * (1 - 0.4 * k))
    if v == 2:  # the catch: a hard hitch before the second pull
        add(y, knock(130, HEAVY_CHAIR, 0.35, contact=0.0015, click=0.3), 0.585, 0.7)
    # a board creaking under the weight, then the chair settles
    cr = creak(0.5, 131 + v, 30, 22, ((280, 30, 1), (610, 45, .7), (1150, 70, .45), (2100, 100, .25)), hiss=0.05)
    add(y, cr, 0.55 if v == 1 else 0.95, 0.25)
    end = 1.45 if v == 1 else 1.43
    add(y, knock(132 + v, HEAVY_CHAIR + FLOOR, 0.6, contact=0.004, click=0.15), end, 0.85)
    return verb(y, 'dormitorio', wet=0.15)


# ====================================================================== 12. swivel chair
def silla_gira():
    dur = 2.15
    n = N(dur)
    r = dsp.rng(120)
    sp = env_pts(n, [(0, 0), (0.1, .55), (0.45, .9), (0.72, .45), (0.86, .85), (1.55, .7), (1.86, 0), (2.15, 0)])
    sp = np.clip(sp * (1 + 0.2 * snoise(n, 3, 121)), 0, None)
    # iron screw squeal: harmonic stick-slip whose pitch follows the speed, stuttering on and off
    f = (650 + 420 * sp) * (1 + 0.03 * snoise(n, 220, 122) + 0.025 * snoise(n, 9, 129))
    ph = TWO_PI * np.cumsum(f) / SR
    # stick-slip: a jittery pulse-like wave (sharp slip, slow stick), harmonics rough rather than pure
    saw = (ph / TWO_PI) % 1.0
    sq = saw ** 2.5 - 0.3 + 0.1 * dsp.highpass(white(n, 130), 2000, 2) * (saw > 0.85)  # slow stick, sudden slip
    sq = dsp.lowpass(sq, 4800, 2)
    gate = smooth((snoise(n, 7, 123) > 0.1).astype(np.float32), 0.012)
    sq = sq * sp ** 1.4 * gate * (0.6 + 0.4 * grain(n, 70, 131, 1.2) / 2)
    sq = dsp.peak(dsp.peak(dsp.peak(sq, 1450, 9, 5), 2900, 7, 5), 4300, 4, 4)
    sq = dsp.highpass(sq, 400, 2)
    # wooden seat joints creaking
    idx, a = stick_slip(n, 26 + 40 * sp, 124, 0.3, sp, 0.35)
    wood = excite(pulse_train(n, idx, a, burst(0.0015, 125)), [(210, 35, 1), (460, 50, .8), (830, 60, .6), (1500, 90, .4), (2600, 130, .2)], 0.3)
    grind = bp(white(n, 126), 200, 900) * grain(n, 40, 127) * sp
    y = np.zeros(n + N(0.6), np.float32)
    y[:n] += 0.4 * norm(sq)
    y[:len(wood)] += 0.75 * norm(wood)[:len(y)]
    y[:n] += 0.1 * norm(grind)
    # stop: wood clunk + the spring under the seat ringing faintly
    add(y, knock(128, [(140, 20, .8), (260, 28, 1), (520, 40, .7), (980, 60, .45), (1800, 90, .25)], 0.4, contact=0.003, click=0.2), 1.87, 0.55)
    tsp = taxis(N(0.7))
    add(y, np.sin(TWO_PI * 330 * tsp * (1 + 0.004 * np.sin(TWO_PI * 6 * tsp))) * np.exp(-tsp * 8), 1.875, 0.06)
    return verb(y, 'direccion', wet=0.12)


# ====================================================================== 13. bakelite phone
def telefono_ring():
    L = N(2.5)
    ring_on = 1.15
    r = dsp.rng(130)
    ratios = [(1.0, 1.0, 5.0), (2.36, .7, 7.0), (2.79, .5, 8.0), (4.13, .45, 11), (5.3, .3, 14), (6.8, .2, 18), (8.4, .12, 24)]

    def gong(f0, seed):
        rr = dsp.rng(seed)
        m = []
        for ra, a, d in ratios:
            for s, g in ((-0.0007, 0.68), (0.0007, 0.32)):  # unequal doublet: a gentle, irregular shimmer
                m.append((f0 * ra * (1 + s + rr.uniform(-3e-4, 3e-4)), d, a * g))
        return m
    ta = np.arange(0.006, ring_on, 1 / 25.0)
    ta = ta + r.normal(0, 0.0012, len(ta))
    tb = ta + 0.02 + r.normal(0, 0.001, len(ta))
    aa = r.uniform(0.8, 1.0, len(ta))
    ab = r.uniform(0.8, 1.0, len(tb))
    aa[:2] *= [0.55, 0.8]
    ab[:2] *= [0.6, 0.85]
    n = L + N(1.5)
    ia, ib = impulses(n, ta, aa), impulses(n, tb, ab)
    ya = excite(signal.fftconvolve(ia, half_sine(0.0003))[:n], gong(1180, 131), 1.4, 132)[:n]
    yb = excite(signal.fftconvolve(ib, half_sine(0.0003))[:n], gong(1395, 133), 1.4, 134)[:n]
    win = np.hanning(N(0.01))[N(0.005):]
    ya *= 1 - 0.35 * np.minimum(1, signal.fftconvolve(impulses(n, ta, np.ones(len(ta))), win)[:n])
    yb *= 1 - 0.35 * np.minimum(1, signal.fftconvolve(impulses(n, tb, np.ones(len(tb))), win)[:n])
    case = excite(signal.fftconvolve(ia + ib, burst(0.001, 135))[:n],
                  [(310, 60, .8), (520, 70, 1), (870, 90, .7), (1400, 120, .5), (2300, 160, .3)], 0.1)[:n]
    tt = taxis(n)
    on = smooth((tt < ring_on).astype(np.float32), 0.006)
    arm = dsp.lowpass(np.tanh(6 * np.sin(TWO_PI * 25 * tt)) * on, 400, 2)
    clicks = dsp.highpass(signal.fftconvolve(ia + ib, burst(0.0005, 136, 2.0))[:n], 3000, 2)
    y = norm(ya) + 0.9 * norm(yb) + 0.22 * norm(case) + 0.04 * arm + 0.12 * norm(clicks)
    y = dsp.drive(y, 1.4)
    y = fold(y, L)
    return cverb(y, 'direccion', wet=0.1)


# ====================================================================== 14. phone line transition
def telefono_linea():
    dur = 1.5
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(140)
    hiss_env = env_pts(n, [(0, 0), (0.05, .45), (0.6, .4), (1.05, 1.0), (1.3, .9), (1.34, .3), (1.5, .25)])
    hiss = white(n, 141) * hiss_env * (1 + 0.4 * snoise(n, 9, 142))
    hiss = tv_filter(hiss, 'bp', 900 + 1600 * smooth(hiss_env, 0.1), 48, 1.6) + 0.4 * hiss
    lam = (45 + 160 * np.exp(-0.5 * ((t - 1.0) / 0.2) ** 2)) * (0.4 + 0.6 * (snoise(n, 8, 147) > 0))
    ci = poisson_times(lam, 143)
    crackle = pulse_train(n, ci, np.minimum(1, r.exponential(0.3, len(ci))), burst(0.0006, 144))
    for j in range(5):  # a few fat pops on the line
        add(crackle, burst(0.003, 148 + j, 1.5), r.uniform(0.1, 1.3), r.uniform(1.0, 2.0))
    hum = sum(np.sin(TWO_PI * 50 * k * t) / k for k in range(1, 9))
    out = 0.35 * norm(hiss) + 0.6 * norm(crackle + 1e-9) + 0.09 * norm(hum)
    # exchange relays: a clunk, a run of dial pulses (10 per second), the line seizing at the end
    relay = [(1100, 200, 1), (2300, 260, .6), (3400, 300, .4), (480, 120, .5)]
    add(out, knock(145, relay, 0.1, contact=0.001, click=0.6), 0.03, 1.0)
    for k in range(7):
        tk = 0.2 + k * 0.1 + r.normal(0, 0.003)
        add(out, knock(146 + k, relay, 0.06, contact=0.0004, click=0.7), tk, 0.6)
        add(out, knock(156 + k, relay, 0.04, contact=0.0003, click=0.7), tk + 0.062, 0.3)
    add(out, knock(170, relay, 0.12, contact=0.0015, click=0.7), 1.33, 1.1)
    # a ghost of the 425 Hz dial tone bleeding through, wavering
    nt = N(0.42)
    tt = taxis(nt)
    tone = np.sin(TWO_PI * np.cumsum(425 * (1 + 0.006 * np.sin(TWO_PI * 3.1 * tt))) / SR)
    add(out, tone * np.sin(np.pi * tt / tt[-1]) ** 2, 0.82, 0.14)
    y = bp(out, 300, 3400, 4)
    y = dsp.drive(y * 1.8, 2.0)
    y = dsp.bitcrush(y, 10, 2)
    return dsp.lowpass(y, 3800, 4)


# ====================================================================== 15. washed-out mate
def mate_sorbo():
    dur = 1.75
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(150)
    pull = env_pts(n, [(0, 0), (0.06, .9), (0.25, 1.0), (0.55, .85), (0.62, 0), (0.78, 0), (0.85, 1.0), (1.3, .9), (1.42, .6), (1.47, 0), (1.75, 0)])
    pull = np.clip(pull * (1 + 0.2 * snoise(n, 6, 151)), 0, None)
    # air rushing through the filter and the steel tube (open pipe ~17 cm -> 1 kHz series)
    air = dsp.lowpass(bp(white(n, 152), 800, 7000), 6500, 2)
    for fpk, g in [(1010, 8), (2020, 7), (3030, 5), (4040, 3), (5050, 2)]:
        air = dsp.peak(air, fpk, g, 5)
    # the dry rattle of the last drops: a 25-45 Hz stutter that gets wetter in the second pull
    ri, ra = stick_slip(n, 30 * (1 + 0.35 * snoise(n, 3, 153)), 154, 0.55, None, 0.15)
    rattle = pulse_train(n, ri, ra, np.exp(-taxis(N(0.03)) / 0.008))  # liquid film bursting, irregularly
    rattle = 0.1 + 0.9 * np.clip(rattle / (np.percentile(rattle, 98) + 1e-9), 0, 1)
    airy = norm(air) * pull * rattle
    # gurgle: slugs of water bursting into bubbles in the yerba
    out = np.zeros(n + N(0.3), np.float32)
    out[:n] += 0.55 * airy
    wetter = env_pts(n, [(0, 0.6), (0.7, 0.8), (0.85, 1.0), (1.47, 1.6), (1.75, 1.6)])
    lam = 85 * pull ** 1.5 * wetter * (0.5 + 0.5 * (snoise(n, 4, 155) > 0))
    for j, i in enumerate(poisson_times(lam, 156)):
        add(out, bubble(r.uniform(550, 1900), 1700 + j, r.uniform(0.3, 1.2), r.uniform(0.2, 1.0), r.uniform(0.6, 1.4)), i / SR, 0.35)
    slosh = dsp.lowpass(white(n, 157), 900, 2) * grain(n, 12, 158, 2.0) * pull
    out[:n] += 0.12 * norm(slosh)
    gourd = excite(dsp.lowpass(white(n, 159), 1200, 2) * pull * rattle, [(420, 40, 1), (860, 60, .4)], 0.1)
    out[:len(gourd)] += 0.12 * norm(gourd)[:len(out)]
    # lips leaving the bombilla
    add(out, knock(160, [(900, 120, 1), (1800, 160, .5)], 0.05, contact=0.0006, click=0.3), 1.49, 0.25)
    return verb(out, 'direccion', wet=0.06)


# ====================================================================== 16. confessional grille
def confesionario_rejilla():
    n = N(1.0)
    out = np.zeros(n, np.float32)
    add(out, knock(170, [(900, 90, 1), (1700, 120, .6), (3100, 180, .4)], 0.05, contact=0.0005, click=0.3), 0.0, 0.25)
    ts, ln = 0.05, 0.3
    m = N(ln)
    k = np.linspace(0, 1, m)
    sp = np.sin(np.pi * np.minimum(1, k * 1.15)) ** 0.5 * (1 + 0.2 * snoise(m, 9, 171))
    sp = np.clip(sp, 0, None)
    idx, a = stick_slip(m, 70 + 160 * sp, 172, 0.3, sp, 0.35)
    slide = excite(pulse_train(m, idx, a, burst(0.0006, 173)), [(620, 60, 1), (1100, 80, .8), (1900, 110, .6), (3100, 150, .4), (4600, 200, .2)], 0.1)
    scrape = bp(white(m, 174), 1500, 6000) * grain(m, 200, 175) * sp
    add(out, norm(slide), ts, 0.6)
    add(out, norm(scrape), ts, 0.25)
    booth = [(160, 25, .8), (260, 30, 1), (420, 40, .7), (700, 55, .5), (1150, 80, .3), (2300, 120, .2)]
    add(out, knock(176, booth, 0.4, contact=0.0012, click=0.35), ts + ln, 1.0)
    y = verb(out, 'caja', wet=0.3)
    return verb(y, 'capilla', wet=0.1, decay=3.0)


# ====================================================================== 17. mirror cracking
def espejo_raja():
    r = dsp.rng(180)
    n = N(2.6)
    out = np.zeros(n, np.float32)
    plate = [(240, 18, 1), (410, 25, .7), (690, 32, .5), (1050, 45, .35)]

    def run(t0, ln, dens, amp, seed, big=False):
        rr = dsp.rng(seed)
        m = N(ln)
        k = np.linspace(0, 1, m)
        lam = dens * np.sin(np.pi * k) ** 0.5 * (1 + 0.7 * snoise(m, 40, seed))
        idx = poisson_times(np.clip(lam, 0, None), seed + 1)
        a = rr.uniform(0.2, 1.0, len(idx)) * (0.6 + 0.4 * k[idx])
        exc = pulse_train(m, idx, a, half_sine(0.00012))
        modes = [(rr.uniform(1800, 11000), rr.uniform(40, 160), rr.uniform(.3, 1)) for _ in range(12)]
        y = norm(excite(exc, modes, 0.25, seed + 2))
        y += 0.5 * fit(norm(dsp.highpass(exc, 3000, 2) + 1e-9), len(y))
        if big:
            y += 0.6 * norm(excite(exc, plate, 0.5)[:len(y)])
        add(out, y, t0, amp)
    for k, (tt, a) in enumerate([(0.0, .35), (0.21, .3), (0.4, .45), (0.53, .3)]):  # first lonely ticks
        add(out, glass_ping(181 + k, r.uniform(3000, 7000), 90, 1.0, 0.8), tt, a)
    for k, (t0, ln, d, a) in enumerate([(0.62, 0.06, 1500, .4), (0.84, 0.09, 2000, .5), (1.03, 0.07, 2500, .55),
                                        (1.18, 0.12, 2600, .65), (1.36, 0.05, 3000, .6), (1.47, 0.16, 3500, .75)]):
        run(t0, ln, d, a, 190 + 10 * k)
    run(1.7, 0.09, 6500, 1.0, 260, big=True)  # the last, loud split
    add(out, dsp.highpass(burst(0.003, 261, 2.0), 1500, 2), 1.7, 0.6)
    for k in range(5):  # crumbs of silvered glass into the sink
        tc = 1.85 + r.uniform(0, 0.3)
        for j, (tb, ab) in enumerate(bounces(270 + k, r.uniform(0.15, 0.35), 3, (0.03, 0.06))):
            add(out, glass_ping(280 + 5 * k + j, r.uniform(4500, 9000), amp=ab), tc + tb)
    return verb(out, 'banos', wet=0.22)


# ====================================================================== 18. brick wall collapse
def brick(seed, amp, heavy=1.0):
    r = dsp.rng(seed)
    n = N(0.35)
    modes = [(r.uniform(500, 800), r.uniform(40, 70), 1), (r.uniform(1000, 1500), r.uniform(50, 90), .8),
             (r.uniform(1700, 2600), r.uniform(70, 110), .5), (r.uniform(2800, 3800), 140, .3)]
    y = knock(seed, modes, 0.35, contact=0.0012, click=0.45, click_hp=1200)
    tt = taxis(n)
    thud = np.sin(TWO_PI * r.uniform(85, 170) * tt) * np.exp(-tt * 30) * np.minimum(1, tt / 0.002)
    grit = bp(burst(0.02, seed + 1, 2.0), 800, 6000)
    y = y + heavy * 0.8 * thud
    y[:len(grit)] += 0.35 * norm(grit)
    return (norm(y) * amp).astype(np.float32)


def muro_cae():
    dur = 3.0
    n = N(dur + 0.6)
    t = taxis(n)
    r = dsp.rng(200)
    out = np.zeros(n, np.float32)
    # mortar letting go: a crunching run of cracks
    ct = np.sort(0.28 * (1 - r.random(26) ** 1.6))
    for j, tc in enumerate(ct):
        add(out, brick(201 + j, r.uniform(.15, .45), 0.2), tc)
    add(out, dsp.highpass(burst(0.006, 230, 2.0), 900, 2), 0.0, 0.5)
    # the mass coming down
    rum_env = env_pts(n, [(0, 0), (0.18, .4), (0.55, 1.0), (1.2, .6), (2.4, .15), (3.4, 0)])
    rumble = dsp.lowpass(colored(n, 'brown', 231), 220, 2) * rum_env
    ti = 0.5
    tb = taxis(N(1.6))
    boom = np.sin(TWO_PI * np.cumsum(36 * (1 + 0.45 * np.exp(-tb * 7))) / SR) * np.exp(-tb * 3.5) * np.minimum(1, tb / 0.006)
    nb = bp(colored(len(tb), 'pink', 232), 40, 300) * np.exp(-tb * 6)
    out += 0.35 * norm(rumble)
    add(out, norm(boom) + 0.6 * norm(nb), ti, 0.8)
    # crunch of the wall hitting the floor
    nc = N(0.3)
    lam = 900 * np.exp(-taxis(nc) / 0.08)
    idx = poisson_times(lam, 233)
    crunch = excite(pulse_train(nc, idx, r.uniform(.2, 1, len(idx)), burst(0.0008, 234)),
                    [(620, 60, 1), (1150, 80, .8), (2100, 110, .5), (3300, 150, .3)], 0.08)
    add(out, norm(crunch), ti, 0.7)
    # bricks: tumbling, clacking, bouncing
    bt = np.concatenate([ti - 0.15 + r.gamma(2.0, 0.28, 85), 1.15 + r.gamma(2.0, 0.25, 28)])  # then the top courses
    bt = bt[bt < 2.75]
    for j, tb_ in enumerate(np.sort(bt)):
        a = 1.5 * r.uniform(0.25, 0.9) * np.exp(-max(0, tb_ - 0.7) / 1.7)
        add(out, brick(300 + j, a), tb_)
        if r.random() < 0.5:
            add(out, brick(500 + j, a * 0.35, 0.5), tb_ + r.uniform(0.05, 0.16))
    # rubble sliding and settling, dust hissing, pebbles trickling
    slide_env = env_pts(n, [(0, 0), (0.55, 0), (0.75, 1.0), (1.6, .55), (2.7, .1), (3.2, 0)])
    rub = bp(white(n, 240), 180, 2600) * grain(n, 55, 241, 2.0) * slide_env
    dust = bp(white(n, 242), 2500, 9000) * env_pts(n, [(0, 0), (0.8, 0), (1.3, 1.0), (3.2, .3), (3.6, 0)])
    out += 0.2 * norm(rub) + 0.04 * norm(dust)
    lam = 30 * env_pts(n, [(0, 0), (1.8, 0), (2.1, 1), (3.1, .1), (3.6, 0)])
    for j, i in enumerate(poisson_times(lam, 243)):
        add(out, brick(700 + j, r.uniform(.03, .1), 0.1), i / SR)
    return verb(out, 'cripta', wet=0.22)


# ====================================================================== 19. stone lid
STONE = [(62, 10, 1), (118, 14, .9), (205, 20, .8), (330, 28, .6), (540, 40, .45), (860, 60, .3), (1350, 85, .2)]


def tumba_tapa():
    dur = 2.5
    n = N(dur)
    r = dsp.rng(210)
    sp = env_pts(n, [(0, 0), (0.09, 0), (0.13, .95), (0.26, .5), (0.8, .7), (0.9, .08), (1.02, .05), (1.12, .85), (1.9, .62), (2.25, .15), (2.31, 0), (2.5, 0)])
    sp = np.clip(sp * (1 + 0.3 * snoise(n, 6, 211)), 0, None)
    idx, a = stick_slip(n, 9 + 26 * sp, 212, 0.35, sp, 0.4)
    grind = norm(excite(pulse_train(n, idx, a, burst(0.002, 213)), detune(STONE, r, 0.03), 0.45))
    rough = dsp.lowpass(bp(white(n, 214), 150, 1600), 1800, 2)
    rough = dsp.peak(rough, 600, 5, 1.5) * grain(n, 45, 215, 2.0) * sp
    gl = 55 * sp
    gi = poisson_times(gl, 216)
    grit = dsp.highpass(pulse_train(n, gi, r.uniform(.2, 1, len(gi)), burst(0.0005, 217)), 1500, 2)
    out = np.zeros(len(grind) + N(0.6), np.float32)
    out[:len(grind)] += grind
    out[:n] += 0.55 * norm(rough) + 0.22 * norm(grit + 1e-9)
    # the seal breaking
    add(out, knock(218, STONE + [(2100, 120, .3)], 0.4, contact=0.002, click=0.35), 0.1, 0.8)
    nc = N(0.12)
    ci = poisson_times(np.full(nc, 600.0) * np.exp(-taxis(nc) / 0.04), 219)
    add(out, dsp.highpass(pulse_train(nc, ci, r.uniform(.3, 1, len(ci)), burst(0.0006, 220)), 1200, 2), 0.1, 0.5)
    # comes to rest
    add(out, knock(221, STONE, 0.7, contact=0.006, click=0.1), 2.31, 0.9)
    tb = taxis(N(0.6))
    add(out, np.sin(TWO_PI * 52 * tb) * np.exp(-tb * 8) * np.minimum(1, tb / 0.005), 2.31, 0.5)
    for j in range(10):
        add(out, brick(230 + j, r.uniform(.02, .06), 0.0), 2.33 + r.exponential(0.15))
    return verb(out, 'cripta', wet=0.2)


# ====================================================================== 20. the ruler breaks
CHILD_AH = [(950, 0.18, 1.0), (1450, 0.16, 0.55), (3100, 0.14, 0.18), (4300, 0.15, 0.08)]


def choir_voice(f, dur, seed, vib=0.006):
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    fr = f * (1 + vib * np.sin(TWO_PI * r.uniform(4.8, 5.8) * t + r.uniform(0, 6)) * np.minimum(1, t / 0.8))
    fr *= 1 + 0.004 * snoise(n, 3, seed + 1)
    ph = TWO_PI * np.cumsum(fr) / SR
    K = max(1, int(7000 / f))
    y = sum(np.sin(k * ph + r.uniform(0, 6)) / k ** 1.15 for k in range(1, K + 1))
    y = y + 0.08 * dsp.highpass(white(n, seed + 2), 1500, 2) * (1 + np.sin(ph))
    return y.astype(np.float32)


def regla_rompe():
    total = 6.8
    n = N(total)
    r = dsp.rng(220)
    out = np.zeros(n, np.float32)
    tc = 0.26
    # bending: fibres creaking up to the break
    nbnd = N(tc)
    kb = np.linspace(0, 1, nbnd)
    idx, a = stick_slip(nbnd, 40 + 160 * kb ** 2, 221, 0.4, kb ** 1.5, 0.3)
    rul = [(430, 30, .8), (1180, 45, 1), (2240, 60, .8), (3600, 80, .6), (5300, 110, .45), (7400, 150, .3)]
    bend = excite(pulse_train(nbnd, idx, a, half_sine(0.0003)), rul, 0.1)
    add(out, norm(bend), 0.0, 0.16)
    # CRACK: the fracture and its splinters
    nk = N(0.06)
    kt = np.concatenate([[0.0], np.sort(r.exponential(0.012, 14))])
    ka = np.concatenate([[1.0], r.uniform(0.15, 0.6, 14) * np.exp(-np.sort(r.exponential(0.012, 14)) / 0.02)])
    exc = pulse_train(nk, (kt * SR).astype(int).clip(0, nk - 1), ka, half_sine(0.00015))
    crack = norm(excite(exc, rul, 0.25, 222)) + 0.8 * norm(excite(exc, detune(rul, r, 0.12), 0.25, 223))
    crack = norm(crack)
    crack[:N(0.012)] += 0.9 * norm(dsp.highpass(burst(0.012, 224, 2.0), 2500, 2))
    tt = taxis(len(crack))
    crack += 0.3 * np.sin(TWO_PI * np.cumsum(140 * (1 - 0.35 * np.minimum(1, tt / 0.1))) / SR) * np.exp(-tt * 20)
    crack = norm(crack)
    ce = dsp.echo(crack, 0.36, 0.5, 5, 4500)  # slap-back off the far end of the chapel
    ce = verb(ce, 'capilla', wet=0.3)
    add(out, ce, tc, 1.0)
    # the choir swells in: eight voices at last (D major, girls), with a shimmer an octave up
    cs, cl = tc + 0.12, total - tc - 0.12
    notes = [293.66, 369.99, 440.0, 587.33, 739.99, 880.0]
    ch = np.zeros(N(cl), np.float32)
    for i, f in enumerate(notes):
        for vv in range(3):
            ch += choir_voice(f * 2 ** (r.uniform(-9, 9) / 1200), cl, 2300 + 10 * i + vv) * (0.75 if f > 700 else 1.0)
    form = sum(g * bp(ch, c * 2 ** (-w), c * 2 ** w) for c, w, g in CHILD_AH)
    nch = len(form)
    sw = env_pts(nch, [(0, 0), (0.3, .1), (2.3, 1.0), (3.4, .9), (cl - 0.2, 0.0), (cl, 0)])
    sw = sw ** 1.5
    form = norm(form) * sw
    shimmer = dsp.pitch_shift(form, 12)
    shimmer = fit(shimmer, nch) * (1 + 0.3 * snoise(nch, 9, 2400))
    choir = padsum((verb(form, 'capilla', wet=0.4, decay=5.0), 1.0),
                   (verb(dsp.highpass(shimmer, 1200, 2), 'capilla', wet=1.0, dry=0.0, decay=6.0, seed=9), 0.55))
    for j in range(9):  # sparkles in the vault
        fz = notes[j % 6] * 4
        tz = r.uniform(0.9, 3.8)
        nz = N(1.6)
        tzz = taxis(nz)
        z = (np.sin(TWO_PI * fz * tzz) + 0.3 * np.sin(TWO_PI * fz * 2.76 * tzz) * np.exp(-tzz * 4)) * np.exp(-tzz * 2.5) * np.minimum(1, tzz / 0.002)
        add(choir, verb(z, 'capilla', wet=0.6), tz, 0.07)
    add(out, norm(choir), cs, 0.62)
    return out


# ====================================================================== 21. reprimand (UI)
DESK = [(95, 45, .8), (160, 50, 1), (270, 60, .8), (430, 70, .5), (700, 85, .35), (1150, 110, .2)]


def stamp(seed, amp=1.0, heavy=1.0):
    n = N(0.5)
    out = np.zeros(n, np.float32)
    add(out, knock(seed, DESK, 0.5, contact=0.006, click=0.0), 0, 1.0)
    add(out, bp(burst(0.012, seed + 1, 1.5), 700, 5000), 0, 0.5)
    add(out, knock(seed + 2, [(1900, 90, 1), (3100, 120, .6)], 0.06, contact=0.0005, click=0.3), 0.012, 0.12)
    tb = taxis(N(0.3))
    add(out, np.sin(TWO_PI * 75 * tb) * np.exp(-tb * 38) * np.minimum(1, tb / 0.003), 0, 0.35 * heavy)
    return norm(out) * amp


def ui_amonestacion():
    n = N(1.9)
    out = np.zeros(n, np.float32)
    add(out, stamp(240), 0.005, 1.0)
    # little desk bell: plunger tick, then the bright ding with its warble
    add(out, knock(241, [(6200, 300, 1), (8100, 400, .6)], 0.03, contact=0.0002, click=0.5), 0.17, 0.08)
    tb = taxis(N(1.6))
    f0 = 2350.0
    ding = np.zeros(len(tb))
    for ra, a, d in [(1.0, 1.0, 2.2), (2.21, .45, 4.5), (3.86, .25, 8.0), (5.9, .12, 12.0)]:
        ding += a * (np.sin(TWO_PI * f0 * ra * tb) + 0.5 * np.sin(TWO_PI * (f0 * ra + 3.5) * tb + 1.0)) * np.exp(-tb * d)
    ding *= np.minimum(1, tb / 0.0008)
    add(out, norm(ding), 0.175, 0.55)
    return verb(out, 'direccion', wet=0.08)


# ====================================================================== 22. quill + stamp
def madre_pluma():
    r = dsp.rng(250)
    n = N(2.3)
    out = np.zeros(n, np.float32)
    t = 0.02
    strokes = []
    for j in range(17):  # quick cursive: "Aja." and a flourish
        d = r.uniform(0.04, 0.1)
        strokes.append((t, d, 1.0 if j % 2 == 0 else 0.55))
        t += d + r.uniform(0.006, 0.025)
    strokes.append((t + 0.03, 0.24, 0.9))  # the flourish
    for j, (t0, d, pr) in enumerate(strokes):
        m = N(d)
        k = np.linspace(0, 1, m)
        e = np.minimum(1, k * d / 0.006) * np.minimum(1, (1 - k) * d / 0.01) * pr * (1 + 0.3 * snoise(m, 25, 260 + j))
        tex = bp(white(m, 270 + j), 2500, 11000)
        tex = dsp.peak(dsp.peak(tex, 4200, 6, 2), 6500, 4, 2)
        tex = tex * grain(m, 450, 280 + j, 2.2)
        add(out, norm(tex) * e, t0, 0.8)
        if r.random() < 0.22:  # the nib catches the paper
            ns = N(r.uniform(0.015, 0.03))
            ts_ = taxis(ns)
            fsq = r.uniform(3500, 5000)
            sq = np.sin(TWO_PI * fsq * ts_) + 0.4 * np.sin(TWO_PI * 2 * fsq * ts_)
            add(out, sq * np.sin(np.pi * ts_ / ts_[-1]), t0 + d * r.uniform(0.2, 0.7), 0.18)
    tdot = strokes[-1][0] + strokes[-1][1] + 0.08
    add(out, knock(290, DESK[2:] + [(2500, 200, .5)], 0.06, contact=0.0004, click=0.5), tdot, 0.4)  # "."
    ts = tdot + 0.25
    add(out, stamp(291, heavy=1.3), ts, 1.4)
    nl = N(0.05)  # rubber peeling off the paper
    add(out, bp(white(nl, 292), 900, 3500) * grain(nl, 300, 293, 2.5) * np.linspace(1, 0, nl), ts + 0.24, 0.15)
    return verb(out, 'aula', wet=0.08, decay=1.4)


# ====================================================================== 23. sleepers breathing (loop)
def breather(L, seed, phase, depth=1.0, muffle=2200.0, voiced=0.0, f0=170.0, inhale=0.3):
    """One sleeper under a sheet over a circular buffer of L samples (one slow breath per loop:
    inhale ~1.2 s, exhale ~1.6 s, then a held pause)."""
    r = dsp.rng(seed)
    t = np.arange(L) / L
    p = (t + phase) % 1.0
    ex0, ex1 = inhale + 0.03, 0.72
    ein = np.where(p < inhale, np.clip(np.sin(np.pi * p / inhale), 0, 1) ** 1.8, 0.0)
    q = np.clip((p - ex0) / (ex1 - ex0), 0, 1)
    eex = np.where((p >= ex0) & (p < ex1), (1 - np.exp(-q * 14)) * (1 - q) ** 1.6, 0.0)
    w = r.standard_normal(L)
    nin = cfilt(w, lambda f: bumps(f, [(520, .35, 1.0), (1500, .3, .7), (2600, .25, .4)], 0.05) / (1 + (f / muffle) ** 4))
    nex = cfilt(r.standard_normal(L), lambda f: bumps(f, [(380, .45, 1.0), (1100, .35, .55), (2300, .3, .2)], 0.04) / (1 + (f / (muffle * 0.8)) ** 4))
    y = norm(nin) * ein * 0.8 + norm(nex) * eex
    if voiced:  # a faint hum on the out-breath
        cycles = max(1, int(round(f0 * L / SR)))
        ph = TWO_PI * cycles * t + 0.15 * np.sin(TWO_PI * 3 * t)
        v = sum(np.sin(k * ph) / k ** 1.4 for k in range(1, 12))
        v = cfilt(v, lambda f: bumps(f, [(450, .3, 1.0), (900, .3, .5)], 0.02) / (1 + (f / muffle) ** 4))
        y = y + voiced * norm(v) * eex ** 1.5
    return (y * depth).astype(np.float32)


def rustle(seed, dur):
    n = N(dur)
    r = dsp.rng(seed)
    lam = 600 * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    idx = poisson_times(lam, seed + 1)
    crk = pulse_train(n, idx, r.uniform(.2, 1, len(idx)), burst(0.0006, seed + 2))
    crk = bp(crk, 1200, 7000)
    soft = bp(white(n, seed + 3), 500, 4000) * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return norm(0.6 * norm(crk + 1e-9) + 0.4 * norm(soft)) * 0.5


def dormitorio_respira(v):
    L = N(4.0)
    out = np.zeros(L, np.float32)
    r = dsp.rng(300 + v)
    if v == 1:  # one close sleeper, three further down the rows, out of step
        sleepers = [(0.0, 1.0, 3000, 0.0), (0.31, 0.42, 2000, 0.12), (0.58, 0.28, 1700, 0.0), (0.84, 0.18, 1400, 0.0)]
    else:  # too many of them breathing exactly together, and one that is not
        sleepers = [(0.0, 1.0, 3000, 0.0), (0.01, 0.75, 2200, 0.15), (0.02, 0.6, 1800, 0.0), (0.03, 0.45, 1500, 0.1), (0.5, 0.2, 1300, 0.0)]
    for i, (ph, g, muf, vo) in enumerate(sleepers):
        b = breather(L, 310 + 10 * v + i, ph, g, muf, vo, r.uniform(150, 200))
        out += b
    for j, (tr, a) in enumerate([(1.3, 0.1), (3.1, 0.07)] if v == 1 else [(2.6, 0.09)]):
        rs = rustle(330 + 5 * v + j, r.uniform(0.35, 0.6))
        e = np.zeros(L, np.float32)
        add(e, rs, 0)
        out += np.roll(e, N(tr)) * a
    out = dsp.lowpass(np.tile(out, 2), 7000, 2)[L:]
    return cverb(out, 'dormitorio', wet=0.12)


# ====================================================================== 24. little girls running
STEP_FLOOR = [(88, 20, .8), (150, 25, 1), (240, 30, .8), (370, 38, .6), (560, 50, .4), (850, 70, .3), (1300, 90, .2)]


def alumna_pasos(v):
    dur = 3.0
    n = N(dur + 0.8)
    r = dsp.rng(310 + v)
    out = np.zeros(n, np.float32)
    girls = 6 if v == 1 else 5
    for g in range(girls):
        rg = dsp.rng(320 + 10 * v + g)
        rate = rg.uniform(3.6, 4.4)
        t0 = rg.uniform(0.0, 0.25)
        ts = t0 + np.arange(int((dur - t0) * rate) + 1) / rate + rg.normal(0, 0.012, int((dur - t0) * rate) + 1)
        ts = ts[(ts > 0) & (ts < dur)]
        lr = np.where(np.arange(len(ts)) % 2 == 0, 1.0, rg.uniform(0.7, 0.9))
        amps = lr * rg.uniform(0.6, 1.0, len(ts))
        exc = np.zeros(n, np.float32)
        clk = np.zeros(n, np.float32)
        for j, (tt, a) in enumerate(zip(ts, amps)):
            hs = half_sine(rg.uniform(0.002, 0.0035))
            add(exc, hs, tt, a)
            add(clk, burst(0.0015, 2000 + 50 * g + j, 2.0), tt, a)
            if rg.random() < 0.3:  # toe then heel
                add(exc, hs, tt + rg.uniform(0.015, 0.03), 0.4 * a)
                add(clk, burst(0.0012, 2600 + 50 * g + j, 2.0), tt + 0.02, 0.3 * a)
            if rg.random() < 0.25:
                ns = N(0.03)
                add(clk, bp(white(ns, 2900 + 50 * g + j), 1500, 5000) * np.linspace(1, 0, ns) * 0.15, tt + 0.01, a)
        board = excite(exc, detune(STEP_FLOOR, rg, 0.06), 0.3)[:n]
        shoe = dsp.highpass(clk, 1800, 2)
        y = norm(board) + 0.45 * norm(shoe)
        # distance over time: v1 they run past, v2 they run away
        tn = taxis(n)
        if v == 1:
            d = 0.25 + np.abs(tn - rg.uniform(1.2, 1.7)) * 0.9
        else:
            d = 0.15 + np.maximum(0, tn - 0.3) * 1.1 + 0.15 * g
        y = tv_filter(y, 'lp', 12000 * 0.4 ** d, 48) / (1 + 1.4 * d)
        out += y * rg.uniform(0.7, 1.0)
    for j in range(3):  # boards creaking under them
        tc = r.uniform(0.3, 2.2)
        add(out, creak(0.18, 340 + j + 5 * v, 45, 30, ((300, 35, 1), (700, 50, .6), (1300, 80, .3)), hiss=0.0), tc, 0.12)
    out *= env_pts(n, [(0, 0), (0.12, 1), (dur - 0.3, 1), (dur + 0.1, 0), (n / SR, 0)])
    return verb(out, 'pasillo', wet=0.2)


# ====================================================================== event table + build
EVENTS = {  # event -> ([variant builders], peak dBFS, loop)
    'colegio.timbre': ([timbre], -3.0, False),
    'colegio.campana': ([campana], -3.0, False),
    'colegio.campana_triple': ([campana_triple], -0.5, False),
    'colegio.pa_chime': ([pa_chime], -3.0, False),
    'colegio.viento': ([lambda: viento(1), lambda: viento(2)], -3.0, False),
    'colegio.polvo': ([polvo], -3.0, False),
    'door.slam': ([lambda: door_slam(1), lambda: door_slam(2)], -3.0, False),
    'tiza.escribe': ([lambda: tiza_escribe(1), lambda: tiza_escribe(2), lambda: tiza_escribe(3)], -3.0, False),
    'tiza.rompe': ([tiza_rompe], -3.0, False),
    'pupitres.giran': ([pupitres_giran], -3.0, False),
    'farol.revienta': ([lambda: farol_revienta(1), lambda: farol_revienta(2), lambda: farol_revienta(3)], -3.0, False),
    'luces.fuera': ([luces_fuera], -3.0, False),
    'silla.arrastra': ([lambda: silla_arrastra(1), lambda: silla_arrastra(2)], -3.0, False),
    'silla.gira': ([silla_gira], -3.0, False),
    'telefono_baquelita.ring': ([telefono_ring], -4.0, True),
    'telefono.linea': ([telefono_linea], -3.0, False),
    'mate.sorbo': ([mate_sorbo], -3.0, False),
    'confesionario.rejilla': ([confesionario_rejilla], -3.0, False),
    'espejo.raja': ([espejo_raja], -3.0, False),
    'muro.cae': ([muro_cae], -3.0, False),
    'tumba.tapa': ([tumba_tapa], -3.0, False),
    'regla.rompe': ([regla_rompe], -0.5, False),
    'ui.amonestacion': ([ui_amonestacion], -3.0, False),
    'madre.pluma': ([madre_pluma], -3.0, False),
    'dormitorio.respira': ([lambda: dormitorio_respira(1), lambda: dormitorio_respira(2)], -3.0, True),
    'alumna.pasos': ([lambda: alumna_pasos(1), lambda: alumna_pasos(2)], -3.0, False),
}


def rel_paths(name):
    n = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if n > 1 else '') for i in range(n)]


def seam_report(x):
    d = np.abs(np.diff(x))
    return float(abs(x[0] - x[-1]) / (np.percentile(d, 75) + 1e-9))


def rotate_to_lull(x):
    """Roll a periodic buffer so it starts at its quietest 60 ms (where master's edge fades are inaudible)."""
    e = uniform_filter1d(np.abs(x), N(0.06), mode='wrap')
    return np.roll(x, -int(np.argmin(e)))


def finish(x, peak_db, loop):
    x = np.asarray(x, np.float32)
    if loop:  # keep the exact period; master's tiny edge fades sit on the quiet seam
        x = dsp.highpass(np.tile(x, 2), 30, 2)[len(x):]  # settle master's filter state on the loop itself
        return dsp.master(rotate_to_lull(x), peak_db=peak_db)
    x = dsp.trim(x, -62, 0.08)
    return dsp.master(x, peak_db=peak_db)


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    report = {}
    for name, (fns, pk, loop) in EVENTS.items():
        rels = rel_paths(name)
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        assert not SOUNDS[name][3], name + ' is a stream; this module only writes mono positional sounds'
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            x = fn()
            assert x.ndim == 1, rel + ' must be mono'
            x = finish(x, pk, loop)
            dsp.save_ogg(x, rel)
            st = dsp.analyse(x)
            if loop:
                st['seam'] = round(seam_report(x), 2)
            report[rel] = st
            dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            print(f'{rel:32s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    with open(os.path.join(REVIEW_DIR, 'stats.json'), 'w') as fh:
        json.dump(report, fh, indent=1)
    missing = [rel for name in EVENTS for rel in rel_paths(name) if not os.path.exists(os.path.join(dsp.OUT, rel + '.ogg'))]
    if missing:
        print('MISSING:', missing)
    print(f'colegio sfx group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
