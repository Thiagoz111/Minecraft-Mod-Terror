# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "choripan": Choripán the dachshund, the thing that lives inside him, and the neighbour's cumbia.

Run from the repo root:  python3 tools/audio/snd_choripan.py [substring ...]

Case 2, Casa Morales (BIBLIA 2.2 g/h/l). Choripán is the case's one planned absurd exception: first he scares, then he
is funny, and he always ends well. His VOICE is a small source-filter synth (additive glottal harmonics through a
dachshund-sized formant track: a short vocal tract, F1 0.5-1 kHz) whose formants can be scaled down to the size of the
BEAST; the gore is physical models (fracture crackle into stiff modes, stick-slip friction, Minnaert bubbles, swept wet
resonances). The cumbia is an ORIGINAL 16-bar tune in A minor at 96 BPM (exactly 40 s: Am G F E7 / Dm Am G C F Dm E7),
rendered circularly and heard through a cheap boombox three houses away on a still night.

  choripan.bark_cute (3)  beat 1 hello / barking at spectres: small happy "arf!", "arf-arf!", playful "rr-ARF!", tag jingle.
  choripan.whine (2)      at the salt line / begging / "don't go": nasal pleading whine with a voice crack; whimpers + sigh.
  choripan.growl_low (2)  his warning (40 ticks before a hallucination): low pulsed growl, in-breath; growl -> lip-curl snarl.
  choripan.sneeze         the happy ending: two sniffs, a tiny "pff-CHI!", the huge ears flapping, the CHORIPÁN tag rattling.
  choripan.crack (6)      beat 7 transformation: celery snap + low wet thump, each different (double, twist, ribs, heavy, knuckles).
  choripan.unspool        beat 7: 5 s of rubber stretching over flesh WITHOUT a break while the links keep coming out
                          (one bump + click + skin flap per link) and the tail keeps knocking the doghouse walls inside.
  choripan.demon_roar (2) jumpscare: a little "arf" whose pitch and body size collapse into a deep roar, the mouth-flower
                          tearing open, then a reversed scream swelling into a hard cut.
  choripan.fetch_drop     beat 9 [RISA]: the thing drops at your feet (thunk, bounce, slobber), pants like a horse-sized happy
                          dog, and the tail thumps the floorboards far back along the chain.
  choripan.chomp          beat 10 catch: cartoon CHOMP (teeth clack + crust crunch + juicy squish + "bomp"), munch munch, GULP.
  choripan.vomit          beat 10: two retches from too deep, a gush of thick black gurgling liquid, splatter on the tiles, drips.
  choripan.metro_retract  beat 10: the body winds back like a TAPE MEASURE (a rattle-buzz whose pitch climbs with the speed:
                          "zzzz-iiiip", crescendo) + CLACK + "boiiing" ringing all the way out.
  casa.cumbia_far         STREAM, stereo, 40 s seamless: the neighbour's cumbia (güiro, bouncy bass, musette synth accordion,
                          off-beat chords, congas, timbales) through a driven boombox, band-passed by three houses of air,
                          slap-backs off the house fronts, diffuse night air, slow periodic "breeze" in level and brightness.
  casa.cumbia_cut         beat 2 "se corta la cumbia": the same far cumbia, then the record is yanked (wicka-wick) and the needle
                          skids off (zzrrrip), the amp dies with a thump and the 50 Hz hum drains away. Mono, positional.
  casa.cumbia_musicbox    STREAM, stereo, 40 s seamless: the far cumbia slides (slows, sags, loses its drums) into a 1961 music
                          box that plays the same melody, detuned and slowing until it runs down on an unresolved note;
                          silence; a key winds by itself; the cumbia comes back from far away ... and slides in again.

Positional sounds are mono; only the casa.cumbia_far / casa.cumbia_musicbox streams are stereo. Loudness: stingers
-0.5 dBFS, vocal sounds -1 dBFS, foley -3 dBFS, loops/streams -4 dBFS.

C cleanup (casa_terror.md 0: no comedy): the cute barks, the sneeze, fetch_drop, chomp, vomit,
metro_retract and the three cumbia streams were cut with their events; their builders below are kept, unused.
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
from scipy.ndimage import uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402
from sounds_def import SOUNDS  # noqa: E402

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/casa_choripan'))
TWO_PI = 2 * np.pi


# ====================================================================== small helpers
def N(sec):
    return max(1, int(round(sec * SR)))


def taxis(n):
    return np.arange(n) / SR


def norm(x, peak=1.0):
    return (np.asarray(x, np.float32) / (np.max(np.abs(x)) + 1e-12) * peak).astype(np.float32)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-12))


def fit(x, n):
    x = np.asarray(x, np.float32)
    if len(x) >= n:
        return x[:n]
    return np.pad(x, ((0, n - len(x)),) + ((0, 0),) * (x.ndim - 1))


def add(buf, x, t, g=1.0):
    """Mix x into buf starting at t seconds (truncated at the end of buf). Mono into stereo is broadcast."""
    s = int(round(t * SR)) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        seg = np.asarray(x[:m], np.float32) * g
        if buf.ndim == 2 and seg.ndim == 1:
            seg = seg[:, None]
        buf[s:s + m] += seg
    return buf


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def pink(n, seed):
    return fit(dsp.noise(n / SR + 1e-4, 'pink', seed), n)


def brown(n, seed):
    return fit(dsp.noise(n / SR + 1e-4, 'brown', seed), n)


def snoise(n, cutoff, seed):
    """Smooth random control signal in about -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 8192).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def grain(n, cutoff, seed, power=2.0):
    """Positive rough-texture modulator with mean 1."""
    g = np.abs(dsp.lowpass(white(n + 4096, seed), cutoff, 2)[4096:]) ** power
    return (g / (np.mean(g) + 1e-9)).astype(np.float32)


def env_pts(n, pts):
    """Piecewise-linear envelope from [(seconds, gain), ...]."""
    return np.interp(np.arange(n), [p[0] * SR for p in pts], [p[1] for p in pts]).astype(np.float32)


def smoothstep(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def burst(dur, seed, shape=1.0):
    n = N(dur)
    return (white(n, seed) * np.linspace(1, 0, n) ** shape).astype(np.float32)


def half_sine(dur):
    n = max(2, N(dur))
    return np.sin(np.pi * (np.arange(n) + 0.5) / n).astype(np.float32)


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
    y = norm(excite(exc, detune(modes, r, amt), dur)[:n])
    if click:
        cl = dsp.highpass(burst(0.0025, seed + 7, 2.0), click_hp, 2)
        y[:len(cl)] += click * norm(cl)
    return y


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


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


def poisson_times(lam, seed):
    r = dsp.rng(seed)
    return np.nonzero(r.random(len(lam)) < np.asarray(lam) / SR)[0]


def crackle(n, rate, seed, lo=1500.0, hi=9000.0, amp_env=None, size=(0.0003, 0.0025), pareto=2.2):
    """Poisson crackle: tiny decaying noise ticks with heavy-tailed amplitudes (fibres, droplets, sticky skin)."""
    rate = np.broadcast_to(np.asarray(rate, np.float64), (n,))
    idx = poisson_times(rate, seed)
    r = dsp.rng(seed + 1)
    out = np.zeros(n, np.float32)
    for i in idx:
        d = max(4, N(r.uniform(*size)))
        b = r.standard_normal(d) * np.exp(-np.arange(d) / (d / 3.0))
        a = min(5.0, r.pareto(pareto) + 0.15)
        if amp_env is not None:
            a *= amp_env[i]
        m = min(d, n - i)
        out[i:i + m] += a * b[:m]
    return bp(out, lo, hi)


def bubble(f0, seed, rise=0.5, amp=1.0, dmul=1.0):
    """Minnaert bubble / drop resonance: decaying sine gliding upward."""
    r = dsp.rng(seed)
    d = (40 + f0 * 0.05) * dmul
    dur = min(0.25, 6.5 / d)
    t = taxis(N(dur))
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.0008)
    return (y * amp).astype(np.float32)


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


def cfft_hp(x, f=35.0):
    """Circular (loop-safe) zero-phase high-pass, mono or stereo."""
    X = np.fft.rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / np.sqrt(1 + (f / np.maximum(fr, 1e-3)) ** 8)
    g = g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X * g, len(x), axis=0).astype(np.float32)


def cfilt(x, gain_fn):
    """Circular zero-phase filter defined by a magnitude function of frequency (Hz). Mono or stereo."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = gain_fn(f)
    g = g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X * g, len(x), axis=0).astype(np.float32)


def hp2(f, fc):
    return (f / fc) ** 2 / np.sqrt(1 + (f / fc) ** 4)


def lp2(f, fc):
    return 1 / np.sqrt(1 + (f / fc) ** 4)


def lp1(f, fc):
    return 1 / np.sqrt(1 + (f / fc) ** 2)


def bump(f, c, w_oct, gain):
    return gain * np.exp(-0.5 * ((np.log2(np.maximum(f, 1.0)) - np.log2(c)) / w_oct) ** 2)


def pan(x, p):
    return dsp.pan(np.asarray(x, np.float32), float(np.clip(p, -1, 1)))


def fold(x, L):
    """Wrap everything past L samples back onto the start (circular buffer)."""
    x = np.pad(x, ((0, -len(x) % L),) + ((0, 0),) * (x.ndim - 1))
    return x.reshape((-1, L) + x.shape[1:]).sum(0).astype(np.float32)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ====================================================================== rooms
ROOMS = {
    'living': dict(decay=0.6, damp=5200.0, predelay=0.004, er=7, er_span=0.022, hf=0.55),   # carpets, floral sofa
    'patio': dict(decay=0.55, damp=6500.0, predelay=0.006, er=5, er_span=0.045, hf=0.6),    # long yard, house wall, fence
    'cucha': dict(decay=0.12, damp=3200.0, predelay=0.001, er=6, er_span=0.004, hf=0.6),    # inside the doghouse
    'pieza': dict(decay=0.8, damp=4400.0, predelay=0.006, er=7, er_span=0.02, hf=0.5),      # the Nona's bedroom
    'eco': dict(decay=2.4, damp=4200.0, predelay=0.02, er=8, er_span=0.06, hf=0.5),         # for the reversed scream
    'barrio': dict(decay=1.4, damp=1600.0, predelay=0.03, er=6, er_span=0.25, hf=0.5, er_gain=6.0),  # night air between houses
}
_IR_CACHE = {}


def room_ir(room, seed=7, **over):
    p = dict(ROOMS[room])
    p.update(over)
    key = (room, seed, tuple(sorted(p.items())))
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    decay, damp, hf = p['decay'], p['damp'], p['hf']
    n = N(decay * 1.35)
    t = taxis(n)
    r = dsp.rng(seed)
    w = r.standard_normal(n).astype(np.float32)
    lo = dsp.lowpass(w, damp, 2) * np.exp(-6.9 * t / decay)
    hi = dsp.highpass(w, damp, 2) * np.exp(-6.9 * t / (decay * hf))
    ir = (lo + 0.5 * hi) * np.minimum(1.0, t / max(0.004, min(0.05, decay * 0.03)))
    lvl = np.sqrt(np.mean(ir[:N(0.05)] ** 2)) + 1e-9
    for _k in range(p['er']):
        q = int(r.uniform(0.002, p['er_span']) * SR)
        if q < n:
            ir[q] += r.uniform(0.4, 1.0) * r.choice([-1, 1]) * lvl * p.get('er_gain', 14.0)
    ir = np.concatenate([np.zeros(N(p['predelay']), np.float32), ir.astype(np.float32)])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    _IR_CACHE[key] = ir
    return ir


def _conv(x, ir, circular):
    if not circular:
        return signal.fftconvolve(x, ir)
    L = len(x)
    if len(ir) > L:
        ir = np.pad(ir, (0, -len(ir) % L)).reshape(-1, L).sum(0)
    return np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(ir, L), L)


def verb(x, room, wet=0.3, dry=1.0, seed=7, circular=False, **over):
    """Mono room reverb (dry + wet); output extended by the tail unless circular (loop-safe)."""
    w = _conv(x, room_ir(room, seed, **over), circular)
    out = np.zeros(len(w), np.float32)
    out[:len(x)] += dry * x
    out += wet * w * 2.0
    return out.astype(np.float32)


def verb_st(x, room, wet=0.3, dry=1.0, seed=11, circular=False, **over):
    """True-stereo reverb: four decorrelated IRs (L->L, R->L, R->R, L->R)."""
    irs = [room_ir(room, seed + i, **over) for i in range(4)]
    L, R = x[:, 0], x[:, 1]
    wl = _conv(L, irs[0], circular) + 0.55 * _conv(R, irs[1], circular)
    wr = _conv(R, irs[2], circular) + 0.55 * _conv(L, irs[3], circular)
    w = np.stack([wl, wr], 1) * (2.0 / 1.14)
    out = np.zeros_like(w, dtype=np.float32)
    out[:len(x)] += dry * x
    out += wet * w
    return out.astype(np.float32)


# ====================================================================== voice synth (source-filter, additive)
CTRL = 64
DOG = {   # a dachshund's short vocal tract: (formant Hz, bandwidth Hz, amplitude). scale < 1 = a bigger body.
    'closed': ((520, 170, 1.0), (1400, 230, 0.5), (2700, 320, 0.32), (4000, 420, 0.16), (5400, 560, 0.07)),
    'open': ((1050, 210, 1.0), (1950, 250, 0.85), (3200, 330, 0.45), (4500, 430, 0.24), (5900, 600, 0.1)),
    'mid': ((760, 180, 1.0), (1600, 230, 0.6), (2900, 330, 0.3), (4200, 430, 0.15), (5600, 580, 0.06)),
    'whine': ((950, 650, 1.0), (2450, 520, 0.22), (3700, 620, 0.1), (5100, 800, 0.04), (6500, 900, 0.02)),
    'growl': ((430, 150, 1.0), (1180, 210, 0.7), (2350, 290, 0.42), (3500, 390, 0.22), (4700, 520, 0.1)),
    'snarl': ((640, 190, 1.0), (1650, 240, 0.85), (2900, 320, 0.55), (4200, 420, 0.3), (5600, 560, 0.14)),
}
HUMAN = {  # adult female, for the reversed scream
    'a': ((850, 110, 1.0), (1350, 130, 0.55), (2850, 190, 0.28), (3900, 260, 0.14), (4900, 340, 0.06)),
    'e': ((520, 85, 1.0), (2100, 130, 0.38), (2900, 190, 0.3), (3900, 260, 0.12), (4900, 340, 0.05)),
    'o': ((560, 85, 1.0), (950, 100, 0.6), (2800, 190, 0.14), (3800, 260, 0.07), (4800, 340, 0.03)),
}


def dogv(name, scale=1.0, bw=1.0):
    return np.array([(f * scale, b * bw * (0.6 + 0.4 * scale), a) for f, b, a in DOG[name]], np.float64)


def humv(name, scale=1.0):
    return np.array([(f * scale, b * (0.6 + 0.4 * scale), a) for f, b, a in HUMAN[name]], np.float64)


def ftrack(n, keys, glide=0.06):
    """keys [(t_sec, (nf,3) formant array)] -> control-rate track (nfr, nf, 3) with `glide` s transitions."""
    nfr = n // CTRL + 2
    tc = np.arange(nfr) * CTRL / SR
    keys = sorted(keys, key=lambda k: k[0])
    pt, pv = [keys[0][0]], [keys[0][1]]
    for i in range(1, len(keys)):
        gap = keys[i][0] - pt[-1]
        g = min(glide, 0.9 * max(gap, 1e-4))
        pt += [keys[i][0] - g / 2, keys[i][0] + g / 2]
        pv += [keys[i - 1][1], keys[i][1]]
    pt = np.maximum.accumulate(np.array(pt) + np.arange(len(pt)) * 1e-7)
    flat = np.stack(pv).reshape(len(pt), -1)
    res = np.stack([np.interp(tc, pt, flat[:, j]) for j in range(flat.shape[1])], 1)
    return res.reshape((nfr,) + keys[0][1].shape)


def fgain(f, fr):
    F, B, A = fr[:, None, :, 0], fr[:, None, :, 1], fr[:, None, :, 2]
    return (A / np.sqrt(1 + ((f[..., None] - F) / (B / 2)) ** 2)).sum(-1)


def fgain_sharp(f, fr):
    """Squared-Lorentzian formant sum: skirts fall 12 dB/oct like a cascaded tract, no broadband floor under noise."""
    F, B, A = fr[:, None, :, 0], fr[:, None, :, 1], fr[:, None, :, 2]
    return (A / (1 + ((f[..., None] - F) / (B / 2)) ** 2)).sum(-1)


def shaped_noise(fr, n, seed, nper=1024, hf=0.0, sharp=0.0, lp=None):
    """White noise filtered (STFT) by the formant track: breath, aspiration, roar turbulence.

    The plain Lorentzian sum leaves a 1/f floor that, integrated over the wide top octaves, turns into hiss under
    turbulent sounds; `sharp` blends in the cascade-like response and `lp` adds a 4th-order roll-off (Hz)."""
    hop = nper // 4
    w = white(n + nper, seed)
    f, t, Z = signal.stft(w, SR, nperseg=nper, noverlap=nper - hop)
    fi = np.clip((t * SR / CTRL).astype(int), 0, fr.shape[0] - 1)
    ff = np.broadcast_to(f[None, :], (len(fi), len(f)))
    g = fgain(ff, fr[fi])
    if sharp:
        g = (1 - sharp) * g + sharp * fgain_sharp(ff, fr[fi])
    if lp:
        g = g / np.sqrt(1 + (f[None, :] / lp) ** 4)
    if hf:
        g = g * (1 + hf * f[None, :] / 4000.0)
    _, y = signal.istft(Z * g.T, SR, nperseg=nper, noverlap=nper - hop)
    return fit(y, n)


def vsynth(f0, fr, amp, tilt=1.2, jitter=0.004, shimmer=0.04, rough=0.0, rough_hz=80.0, sub=0.0, breath=0.03,
           fmax=8000.0, seed=0, coherent=False, floor=0.004, breath_hf=0.0):
    """Additive glottal source through formants. f0/amp/rough/sub per sample (or scalars), fr control-rate track."""
    n = len(f0)
    rough = np.broadcast_to(np.asarray(rough, np.float64), (n,))
    sub = np.broadcast_to(np.asarray(sub, np.float64), (n,))
    f0 = np.asarray(f0, np.float64) * (1 + jitter * snoise(n, 30, seed + 1))
    if rough.max() > 0:
        f0 = f0 * (1 + 0.025 * rough * snoise(n, rough_hz, seed + 2))
    ph = TWO_PI * np.cumsum(f0) / SR
    nfr = fr.shape[0]
    ci = np.minimum(np.arange(nfr) * CTRL, n - 1)
    f0c = f0[ci]
    K = max(1, int(fmax / max(25.0, f0c.min())))
    ks = np.arange(1, K + 1, dtype=np.float64)
    tt = np.arange(n)
    r = dsp.rng(seed)
    phs = np.zeros(K + 1) if coherent else r.uniform(0, TWO_PI, K + 1)

    def bank(mults, phases):
        fk = f0c[:, None] * mults[None, :]
        g = (fgain(fk, fr) + floor) * mults[None, :] ** (-tilt) * np.clip((fmax - fk) / (0.2 * fmax), 0, 1)
        y = np.zeros(n)
        for j, k in enumerate(mults):
            if g[:, j].max() < 1e-7:
                continue
            y += np.interp(tt, ci, g[:, j]) * np.sin(k * ph + phases[j])
        return y

    y = bank(ks, phs)
    if sub.max() > 0:
        ysub = bank(np.arange(0.5, K + 0.5, 1.0), phs[::-1])
        y += sub * (0.65 + 0.35 * snoise(n, 7, seed + 5)) * ysub
    if shimmer:
        y *= 1 + shimmer * snoise(n, 40, seed + 3)
    if rough.max() > 0:
        y *= np.clip(1 + 0.6 * rough * snoise(n, rough_hz * 1.3, seed + 4), 0.05, None)
    y *= amp
    if breath:
        nz = shaped_noise(fr, n, seed + 6, hf=breath_hf)
        nz *= rms(y) / (rms(nz * amp) + 1e-9)
        y = y + breath * nz * amp
    return y.astype(np.float32)


def contour(n, pts, log=True):
    e = env_pts(n, [(t, np.log(f) if log else f) for t, f in pts])
    return np.exp(e) if log else e


# ====================================================================== shared dog bits
def bark(seed, f0=600.0, dur=0.16, rise=1.2, fall=0.75, harsh=0.5, breath=0.3, scale=1.0, tilt=0.95):
    """One small-dog bark: plosive puff, mouth opening closed->wide->half ('w-A-f'), pitch up then down, chaotic onset."""
    n = N(dur)
    t = taxis(n)
    f0c = contour(n, [(0, f0 * 0.9), (dur * 0.2, f0 * rise), (dur * 0.5, f0 * (1 + rise) / 2), (dur, f0 * fall)])
    fr = ftrack(n, [(0, dogv('closed', scale)), (dur * 0.2, dogv('open', scale)), (dur * 0.6, dogv('open', scale * 0.96)),
                    (dur, dogv('mid', scale))], glide=dur * 0.3)
    a = env_pts(n, [(0, 0), (0.003, 0.7), (dur * 0.16, 1.0), (dur * 0.55, 0.62), (dur * 0.85, 0.25), (dur, 0)])
    sub = harsh * env_pts(n, [(0, 1.0), (dur * 0.3, 0.7), (dur * 0.55, 0.0), (dur, 0)])
    rough = harsh * env_pts(n, [(0, 1.3), (dur * 0.4, 0.5), (dur, 0.3)])
    v = vsynth(f0c, fr, a, tilt=tilt, jitter=0.02, shimmer=0.12, rough=rough, rough_hz=120, sub=sub, breath=breath,
               fmax=11000, seed=seed, breath_hf=0.6)
    pk = np.max(np.abs(v))
    puff = shaped_noise(fr, n, seed + 9, hf=1.0) * env_pts(n, [(0, 0), (0.002, 1), (0.018, 0.25), (0.04, 0), (dur, 0)])
    chest = np.sin(TWO_PI * 170 * t) * np.exp(-t * 40) * np.minimum(1, t / 0.002)
    return (v + norm(puff) * 0.3 * pk + chest * 0.15 * pk).astype(np.float32)


def tag_jingle(seed, hits=4, spread=0.12, amp=1.0):
    """The golden CHORIPÁN tag knocking against its split ring."""
    r = dsp.rng(seed)
    m = N(0.3)
    out = np.zeros(N(spread + 0.35), np.float32)
    t = 0.0
    for k in range(hits):
        f = r.uniform(3300, 4300)
        modes = [(f, r.uniform(22, 32), 1.0), (f * r.uniform(2.35, 2.5), 40, 0.5), (f * r.uniform(1.42, 1.52), 30, 0.35),
                 (r.uniform(5600, 6400), 55, 0.3)]
        p = modal_ir(modes, 0.3, seed + k) * np.minimum(1, taxis(m) / 0.0002)
        add(out, norm(p) * r.uniform(0.4, 1.0) * (0.85 ** k), t)
        t += r.uniform(0.4, 1.0) * spread / max(1, hits - 1) * 1.4
    return (dsp.lowpass(out, 11000, 2) * amp).astype(np.float32)


def growl_layer(seed, dur, f0_pts, keys, amp_pts, pulse=(26.0, 0.65), rough=1.0, sub=0.5, noise=0.7, tilt=0.85,
                fmax=7500.0, nz_lp=3400.0, out_lp=5500.0):
    """Growl: low f0, strong pulsing ('fry' bursts) of voice and turbulent noise through a closed snout."""
    n = N(dur)
    f0 = contour(n, f0_pts)
    fr = ftrack(n, keys, glide=0.25)
    a = env_pts(n, amp_pts)
    rate = pulse[0] * (1 + 0.18 * snoise(n, 6, seed + 11))
    ph = np.cumsum(rate) / SR
    am = (0.5 + 0.5 * np.cos(TWO_PI * ph)) ** 3
    am = (1 - pulse[1]) + pulse[1] * am / (np.mean(am) + 1e-9) * 0.5
    v = vsynth(f0, fr, a * am, tilt=tilt, jitter=0.03, shimmer=0.2, rough=rough, rough_hz=55, sub=sub, breath=0.0,
               fmax=fmax, seed=seed)
    nz = shaped_noise(fr, n, seed + 3, sharp=0.85, lp=nz_lp) * a * am
    nz *= rms(v) / (rms(nz) + 1e-9)
    y = v + noise * nz
    return (dsp.lowpass(y, out_lp, 2) if out_lp else y).astype(np.float32)


# ---------------------------------------------------------------------- gore building blocks
def snap(seed, amp=1.0, tone=1.0, spread=0.035, fib=1.0, lp=9500.0):
    """Celery snap / bone fracture: a hard break into stiff quickly-damped modes, a second smaller give-way a few ms
    later, and a dense crunch of fibres parting one after another inside a hollow stalk (two resonances)."""
    r = dsp.rng(seed)
    n = N(spread * 2 + 0.12)
    t = taxis(n)
    exc = np.zeros(n, np.float32)
    hs = half_sine(0.0006)
    exc[:len(hs)] = hs
    t2 = r.uniform(0.006, 0.014)
    hs2 = half_sine(0.0008) * r.uniform(0.35, 0.6)
    exc[N(t2):N(t2) + len(hs2)] += hs2
    modes = [(r.uniform(900, 1300) * tone, 140, 1.0), (r.uniform(1900, 2600) * tone, 190, 0.8),
             (r.uniform(3300, 4300) * tone, 260, 0.55), (r.uniform(5200, 6800) * tone, 380, 0.35),
             (r.uniform(480, 620) * tone, 90, 0.5)]
    main = excite(exc, modes, 0.08)[:n]
    click = fit(dsp.highpass(burst(0.0015, seed + 1, 2.0), 1500, 2), n)
    rate = 14000 * np.exp(-t / (spread * 0.45)) * (t < spread * 2.0)
    fibres = crackle(n, rate, seed + 2, 900, 10000, size=(0.0002, 0.0014), pareto=1.8)
    fibres = dsp.peak(fibres, r.uniform(1800, 2600) * tone, 8.0, 3.0)
    fibres = dsp.peak(fibres, r.uniform(3800, 4800) * tone, 6.0, 3.0)
    y = norm(main) + 0.8 * norm(click) + fib * norm(fibres)
    y = dsp.lowpass(y, lp, 2)
    return norm(y, amp)


def thump(seed, f0=75.0, dur=0.3, amp=1.0, slap=0.4):
    """Low body thump: a pitch-dropping sine + chest/flesh modes + a skin slap."""
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    f = f0 * (1 + 0.8 * np.exp(-t / 0.012))
    y = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.0015)
    exc = np.zeros(n, np.float32)
    hs = half_sine(0.004)
    exc[:len(hs)] = hs
    body = excite(exc, [(r.uniform(140, 180), 35, 1), (r.uniform(260, 320), 45, .6), (r.uniform(450, 560), 60, .4)],
                  dur)[:n]
    sl = fit(bp(burst(0.012, seed + 3, 2.0), 400, 3000), n)
    return norm(norm(y) + 0.6 * norm(body) + slap * norm(sl), amp)


def squelch(seed, dur=0.25, f_hi=1400.0, f_lo=300.0, amp=1.0, bubbles=5, visc=1.0):
    """Wet tissue: noise through a sweeping resonance with a sticky granular texture + a few Minnaert pops."""
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    fc = f_hi * (f_lo / f_hi) ** (t / dur) * (1 + 0.15 * snoise(n, 30, seed + 1))
    nz = tv_filter(white(n, seed + 2), 'bp', fc, 48, 0.7)
    nz = tv_filter(nz, 'bp', fc * 1.05, 48, 1.0)
    texture = grain(n, 90 / visc, seed + 3, 2.0)
    e = env_pts(n, [(0, 0), (0.006, 1), (dur * 0.35, 0.6), (dur, 0)])
    y = norm(nz * texture) * e
    for k in range(bubbles):
        add(y, bubble(r.uniform(180, 700) / visc, seed + 10 + k, rise=0.4, amp=r.uniform(0.2, 0.6)),
            r.uniform(0.0, dur * 0.8))
    return norm(y, amp)


def grind(seed, dur=0.35, rate=(55, 130), amp=1.0):
    """Bone grinding against bone (a joint twisting): stick-slip pulses through bony resonances."""
    r = dsp.rng(seed)
    n = N(dur)
    rr = np.geomspace(rate[0], rate[1], n)
    e = env_pts(n, [(0, 0), (0.03, 0.6), (dur * 0.8, 1.0), (dur, 0.3)])
    idx, a = stick_slip(n, rr, seed, jitter=0.35, amp_env=e, amp_lo=0.3)
    kern = modal_ir([(r.uniform(650, 850), 110, 1), (r.uniform(1400, 1800), 170, 0.7), (r.uniform(2500, 3200), 240, 0.45),
                     (r.uniform(330, 420), 70, 0.5)], 0.04, seed)
    return norm(pulse_train(n, idx, a, kern), amp)


def joint_pop(seed, f=1100.0, amp=1.0):
    """Cavitation pop (a knuckle cracking): a hard tick and a short 'tock' with a tiny pitch drop."""
    r = dsp.rng(seed)
    n = N(0.07)
    t = taxis(n)
    fr = f * (1 + 0.35 * np.exp(-t / 0.003))
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-t * 85) * np.minimum(1, t / 0.0003)
    y += 0.4 * np.sin(TWO_PI * np.cumsum(fr * 2.3) / SR) * np.exp(-t * 160)
    y += 0.5 * fit(dsp.highpass(burst(0.0008, seed + 1, 2.0), 2000, 2), n) / 3
    return norm(y, amp)


def room(x, name, wet):
    return verb(np.asarray(x, np.float32), name, wet=wet)


# ====================================================================== 1. bark_cute
def bark_cute(v):
    out = np.zeros(N(0.9), np.float32)
    if v == 1:      # one bright "arf!"
        add(out, bark(101, 610, 0.15, 1.22, 0.74, harsh=0.45, breath=0.28), 0.0)
        add(out, tag_jingle(111, 3, 0.09), 0.02, 0.05)
    elif v == 2:    # "arf-arf!"
        add(out, bark(102, 640, 0.135, 1.2, 0.76, harsh=0.4, breath=0.3), 0.0)
        add(out, bark(103, 700, 0.15, 1.26, 0.7, harsh=0.5, breath=0.3), 0.215, 1.0)
        add(out, tag_jingle(112, 4, 0.12), 0.02, 0.05)
        add(out, tag_jingle(113, 3, 0.1), 0.24, 0.045)
    else:           # playful "rr-ARF!": a tiny grumble wound up into a high bark
        gr = growl_layer(104, 0.2, [(0, 230), (0.2, 290)], [(0, dogv('closed', 1.05))],
                         [(0, 0), (0.03, 0.6), (0.16, 1.0), (0.2, 0.6)], pulse=(34, 0.55), rough=0.6, sub=0.2,
                         noise=0.5, tilt=1.0, fmax=8000)
        add(out, norm(gr) * 0.32, 0.0)
        add(out, bark(105, 760, 0.13, 1.25, 0.72, harsh=0.35, breath=0.25), 0.17)
        add(out, tag_jingle(114, 4, 0.14), 0.16, 0.055)
    return room(out, 'living', 0.12)


# ====================================================================== 2. whine
def whine_seg(seed, pts, dur, amp_pts=None, vib=(6.2, 0.012), breath=0.07, tilt=1.4, keys=None):
    n = N(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    f0 = contour(n, pts)
    vibenv = env_pts(n, [(0, 0.3), (dur * 0.3, 1.0), (dur, 1.0)])
    f0 = f0 * (1 + vib[1] * vibenv * np.sin(TWO_PI * vib[0] * t + r.uniform(0, 6)))
    keys = keys or [(0, dogv('whine', 0.95)), (dur * 0.5, dogv('whine', 1.08)), (dur, dogv('whine', 0.95))]
    fr = ftrack(n, keys, glide=dur * 0.4)
    a = env_pts(n, amp_pts or [(0, 0), (0.04, 0.8), (dur * 0.3, 1.0), (dur * 0.8, 0.8), (dur, 0)])
    return vsynth(f0, fr, a, tilt=tilt, jitter=0.006, shimmer=0.07, breath=breath, fmax=9000, seed=seed, breath_hf=0.6)


def nose_air(seed, dur, lo=900.0, hi=5000.0, pts=None):
    n = N(dur)
    e = env_pts(n, pts or [(0, 0), (dur * 0.3, 1), (dur, 0)])
    return bp(white(n, seed), lo, hi) * e


def whine(v):
    if v == 1:  # long pleading "hnnnn-IIII(crack)-nnnn"
        L = 2.1
        out = np.zeros(N(L), np.float32)
        add(out, nose_air(201, 0.14, 1200, 5000, [(0, 0), (0.07, 1), (0.14, 0)]), 0.0, 0.05)
        w = whine_seg(202, [(0, 760), (0.22, 1000), (0.55, 1240), (0.8, 1180), (1.06, 1300), (1.1, 1560), (1.2, 1480),
                            (1.45, 1050), (1.75, 820)], 1.75,
                      amp_pts=[(0, 0), (0.08, 0.55), (0.5, 1.0), (1.05, 0.85), (1.1, 1.0), (1.4, 0.7), (1.75, 0)])
        add(out, w, 0.12)
        add(out, nose_air(203, 0.35, 700, 3500, [(0, 0), (0.05, 1), (0.35, 0)]), 1.8, 0.07 * np.max(np.abs(w)))
    else:       # three short whimpers, then a long falling one and a sigh through the nose
        L = 2.75
        out = np.zeros(N(L), np.float32)
        for k, (t0, a0, a1) in enumerate([(0.0, 700, 1020), (0.3, 740, 1080), (0.58, 800, 1150)]):
            d = 0.2
            w = whine_seg(210 + k, [(0, a0), (d * 0.6, a1), (d, a1 * 0.92)], d,
                          amp_pts=[(0, 0), (0.025, 0.9), (d * 0.6, 1.0), (d, 0)], vib=(7.0, 0.006))
            add(out, w, t0, 0.75 + 0.1 * k)
        w = whine_seg(215, [(0, 1120), (0.2, 1260), (0.55, 1040), (1.0, 760)], 1.0,
                      amp_pts=[(0, 0), (0.05, 0.9), (0.3, 1.0), (0.8, 0.6), (1.0, 0)])
        add(out, w, 0.92)
        add(out, nose_air(216, 0.6, 600, 3000, [(0, 0), (0.06, 1), (0.6, 0)]), 2.0, 0.08 * np.max(np.abs(w)))
    return room(out, 'living', 0.1)


# ====================================================================== 3. growl_low
def growl_low(v):
    if v == 1:  # steady warning: out-breath growl, then a quieter in-breath growl
        L = 2.5
        out = np.zeros(N(L), np.float32)
        g1 = growl_layer(301, 1.55, [(0, 92), (0.6, 100), (1.3, 96), (1.55, 88)],
                         [(0, dogv('growl', 1.0)), (0.8, dogv('growl', 1.04)), (1.55, dogv('growl', 0.98))],
                         [(0, 0), (0.18, 0.75), (0.6, 1.0), (1.25, 0.9), (1.55, 0)], pulse=(27, 0.7))
        g2 = growl_layer(302, 0.6, [(0, 120), (0.6, 112)], [(0, dogv('growl', 1.08))],
                         [(0, 0), (0.15, 0.6), (0.45, 0.55), (0.6, 0)], pulse=(33, 0.6), noise=1.1, rough=1.2)
        add(out, g1, 0.0)
        add(out, g2, 1.62, 0.55)
    else:       # low rumble -> lips curl (formants open, brighter) -> a snarl -> a huff through the nose
        L = 3.0
        out = np.zeros(N(L), np.float32)
        g = growl_layer(311, 2.45, [(0, 84), (0.9, 90), (1.3, 112), (1.9, 128), (2.3, 118), (2.45, 100)],
                        [(0, dogv('growl', 0.98)), (1.0, dogv('growl', 1.0)), (1.5, dogv('snarl', 1.0)),
                         (2.2, dogv('snarl', 1.05))],
                        [(0, 0), (0.25, 0.55), (0.9, 0.7), (1.4, 1.0), (2.2, 1.0), (2.45, 0)], pulse=(25, 0.7),
                        rough=1.2, sub=0.6, noise=0.9)
        add(out, g, 0.0)
        r = dsp.rng(312)
        for k in range(5):  # saliva on bared teeth
            add(out, bubble(r.uniform(1800, 3200), 313 + k, rise=1.0, amp=0.04), r.uniform(1.4, 2.3))
        add(out, nose_air(318, 0.18, 500, 4000, [(0, 0), (0.01, 1), (0.18, 0)]), 2.5, 0.25 * np.max(np.abs(g)))
    return room(out, 'living', 0.1)


# ====================================================================== 4. sneeze
def sneeze():
    L = 1.5
    out = np.zeros(N(L), np.float32)
    r = dsp.rng(400)
    # the tickle: two quick nasal sniffs in
    for k, t0 in enumerate((0.0, 0.1)):
        add(out, nose_air(401 + k, 0.065, 1100, 5500, [(0, 0), (0.02, 1), (0.065, 0)]), t0, 0.22)
    # the sneeze: an explosive nasal "pff-CHI!" with a tiny squeak in it
    t0, d = 0.25, 0.12
    m = N(d)
    fr = ftrack(m, [(0, dogv('closed', 1.15)), (d, dogv('mid', 1.2))])
    blast = shaped_noise(fr, m, 410, hf=1.6, lp=9500.0) * env_pts(m, [(0, 0), (0.003, 1), (0.03, 0.5), (0.08, 0.12), (d, 0)])
    sq = whine_seg(411, [(0, 1250), (0.035, 1550), (0.08, 1100)], 0.08,
                   amp_pts=[(0, 0), (0.006, 1.0), (0.045, 0.4), (0.08, 0)], vib=(0.1, 0.0), breath=0.25, tilt=1.2)
    tl = taxis(N(0.045))
    lips = bp(white(len(tl), 412), 200, 1600) * (0.5 + 0.5 * np.sin(TWO_PI * 70 * tl)) ** 4 * np.linspace(1, 0, len(tl))
    add(out, norm(blast), t0, 0.9)
    add(out, norm(sq), t0 + 0.004, 0.45)
    add(out, norm(lips), t0 + 0.07, 0.25)
    # head shake: the huge ears flap against the head (left, right, left...), the tag rattles along
    ts = 0.47
    for k in range(7):
        tk = ts + k / 11.5 + r.uniform(-0.006, 0.006)
        a = 0.85 ** k
        lo, hi = (260, 2000) if k % 2 == 0 else (330, 2600)
        fl = bp(burst(0.014, 420 + k, 1.5), lo, hi)
        add(out, norm(fl), tk, 0.42 * a)
        add(out, thump(430 + k, 150 + 25 * (k % 2), 0.05, 1.0, 0.0), tk, 0.12 * a)
        add(out, bp(white(N(0.04), 440 + k), 400, 3000) * np.linspace(1, 0, N(0.04)) ** 2, tk - 0.03, 0.05 * a)
        if k % 2 == 0 or k < 3:
            add(out, tag_jingle(450 + k, 2, 0.03), tk + 0.004, 0.11 * a)
    # and a happy lick of the nose
    add(out, bubble(1700, 460, rise=0.8, amp=0.09), 1.18)
    add(out, nose_air(461, 0.06, 1500, 6000, [(0, 0), (0.01, 1), (0.06, 0)]), 1.24, 0.12)
    return room(out, 'patio', 0.08)


# ====================================================================== 5. crack (x6)
def crack(v):
    out = np.zeros(N(0.95), np.float32)
    s = 500 + 20 * v
    if v == 1:    # one clean snap and the thump of it
        add(out, snap(s, 1.0, 1.0), 0.0)
        add(out, thump(s + 1, 72, 0.3, 0.5), 0.004)
        add(out, squelch(s + 2, 0.13, 1500, 400, 0.3, 2), 0.01)
    elif v == 2:  # double crack, the second one lower and wetter
        add(out, snap(s, 1.0, 1.12), 0.0)
        add(out, snap(s + 1, 0.85, 0.82, spread=0.03), 0.085)
        add(out, thump(s + 2, 62, 0.32, 0.55), 0.088)
        add(out, squelch(s + 3, 0.22, 1300, 300, 0.5, 4), 0.05)
    elif v == 3:  # a joint twisted until it gives: grinding creak -> snap -> wet pop out of the socket
        add(out, grind(s, 0.38, (48, 140), 0.45), 0.0)
        add(out, snap(s + 1, 1.0, 0.95), 0.37)
        add(out, joint_pop(s + 2, 900, 0.5), 0.372)
        add(out, thump(s + 3, 80, 0.3, 0.55), 0.375)
        add(out, squelch(s + 4, 0.26, 1200, 280, 0.55, 5), 0.38)
    elif v == 4:  # the ribcage widening: a crunchy cascade over a long sticky stretch
        r = dsp.rng(s)
        add(out, squelch(s + 1, 0.5, 900, 260, 0.35, 6, visc=1.4), 0.0)
        for k, t0 in enumerate((0.0, 0.06, 0.11, 0.19, 0.25, 0.33)):
            add(out, snap(s + 10 + k, r.uniform(0.45, 0.8) * (0.7 + 0.06 * k), r.uniform(0.8, 1.25), spread=0.015,
                          fib=0.6), t0)
        add(out, thump(s + 2, 68, 0.3, 0.5), 0.335)
    elif v == 5:  # heavy: a bone breaking deep inside meat - muffled crack, big thump, thick squelch
        add(out, snap(s, 0.8, 0.75, lp=3500.0), 0.0)
        add(out, thump(s + 1, 56, 0.45, 1.0, slap=0.6), 0.006)
        add(out, squelch(s + 2, 0.36, 900, 200, 0.7, 6, visc=1.5), 0.012)
    else:         # knuckles: six human hands opening, pop-pop-pop-pop, then a wet snap
        for k, (t0, f) in enumerate(((0.0, 1300), (0.07, 1100), (0.13, 1450), (0.21, 950))):
            add(out, joint_pop(s + k, f, 0.55 + 0.08 * k), t0)
        add(out, snap(s + 5, 0.9, 1.2), 0.3)
        add(out, thump(s + 6, 85, 0.25, 0.45), 0.302)
        add(out, squelch(s + 7, 0.15, 1600, 500, 0.3, 2), 0.31)
    return room(out, 'patio', 0.12)


# ====================================================================== 6. unspool
def unspool():
    """5 s: rubber stretched over flesh, never stopping, while link after link comes out of the doghouse."""
    L = 5.0
    n = N(L)
    r = dsp.rng(600)
    links, tl = [], 0.22
    while tl < L - 0.25:
        links.append(tl)
        tl += r.uniform(0.5, 0.66)
    # tension builds between links and lets go when one pops out
    tension = np.zeros(n)
    edges = [0.0] + links + [L]
    for a, b in zip(edges[:-1], edges[1:]):
        i0, i1 = N(a) if a > 0 else 0, min(n, N(b))
        u = np.linspace(0, 1, i1 - i0, endpoint=False)
        tension[i0:i1] = (0.25 if a == 0 else 0.0) + u ** 1.4
    tension = smooth_arr(tension, 0.035)
    # 1. high rubber squeal (a balloon / latex glove dragged and stretched): tonal stick-slip whose PITCH follows the
    #    tension - it climbs while a link is being dragged out and sags when the link pops free. The latex body is a
    #    set of broad resonances (so the harmonic comb, i.e. the pitch, reads) plus a little narrow ring on top.
    rate_hi = 260 * (1.85 ** tension) * (1 + 0.035 * snoise(n, 6, 601)) * (1 + 0.012 * np.sin(TWO_PI * 5.5 * taxis(n)))
    e_hi = np.clip(0.7 + 0.35 * snoise(n, 4, 602), 0.35, 1.0)
    idx, a = stick_slip(n, rate_hi, 603, jitter=0.05, amp_env=e_hi, amp_lo=0.8)
    kern = modal_ir([(r.uniform(1050, 1250), 650, 1.0), (r.uniform(2100, 2500), 800, 0.7), (r.uniform(3300, 3900), 1000, 0.4),
                     (r.uniform(620, 720), 500, 0.6), (r.uniform(4800, 5400), 1400, 0.15)], 0.02, 604)
    ring = modal_ir([(r.uniform(1050, 1250), 70, 1.0), (r.uniform(2100, 2500), 110, 0.5)], 0.06, 614)
    squeak = norm(pulse_train(n, idx, a, kern)) + 0.25 * norm(pulse_train(n, idx, a, ring))
    # 2. low creak of stretched skin (leathery, jittery)
    rate_lo = 78 * (1 + 0.6 * tension) * (1 + 0.1 * snoise(n, 4, 605))
    idx, a = stick_slip(n, rate_lo, 606, jitter=0.3, amp_lo=0.4)
    kern = modal_ir([(r.uniform(280, 340), 160, 1.0), (r.uniform(620, 720), 210, 0.7), (r.uniform(1150, 1350), 270, 0.4),
                     (r.uniform(2100, 2500), 350, 0.2)], 0.05, 607)   # damped: each slip is heard, no 300 Hz drone
    creak = pulse_train(n, idx, a, kern)
    # 3. wet flesh sliding over itself: swept resonance, sticky peel, gloopy texture
    slide = tv_filter(pink(n, 608), 'bp', 520 * (1 + 0.45 * snoise(n, 2, 609)) * (1 + 0.4 * tension), 96, 1.1)
    slide *= grain(n, 45, 610, 1.5)
    peel = crackle(n, 220 + 450 * tension, 611, 2000, 8000, size=(0.0002, 0.0009), pareto=2.6)
    wet = np.zeros(n, np.float32)
    for k, i in enumerate(poisson_times(np.full(n, 3.5), 612)):
        add(wet, squelch(620 + k, r.uniform(0.08, 0.16), r.uniform(900, 1600), r.uniform(250, 450), 1.0, 2),
            i / SR, r.uniform(0.25, 0.55))
    # 4. each link coming out: a bump, a cartilage click, a slap of loose skin, a squelch
    lk = np.zeros(n, np.float32)
    for k, t0 in enumerate(links):
        add(lk, thump(650 + k, r.uniform(80, 100), 0.25, 1.0, slap=0.7), t0, r.uniform(0.75, 1.0))
        add(lk, joint_pop(660 + k, r.uniform(900, 1400), 1.0), t0 + r.uniform(-0.01, 0.02), r.uniform(0.25, 0.4))
        add(lk, squelch(670 + k, 0.17, 1300, 350, 1.0, 3), t0 + 0.01, 0.45)
    # 5. inside the doghouse the tail keeps wagging: tok-tok against the plywood walls
    wag = np.zeros(n, np.float32)
    tw, k = 0.05, 0
    while tw < L:
        modes = [(185, 40, 1.0), (340, 55, 0.7), (610, 75, 0.45), (1050, 110, 0.25)] if k % 2 == 0 else \
            [(210, 42, 1.0), (390, 55, 0.7), (700, 80, 0.4), (1200, 120, 0.22)]
        add(wag, knock(680 + k, modes, 0.18, contact=0.005, click=0.08, click_hp=1200), tw, r.uniform(0.7, 1.0))
        tw += 0.31 + r.uniform(-0.02, 0.02)
        k += 1
    wag = dsp.lowpass(verb(wag, 'cucha', wet=0.35)[:n], 2500, 2)
    # 6. under everything, the low strained breath of the thing
    groan = growl_layer(690, L, [(0, 52), (2.5, 58), (L, 54)], [(0, dogv('growl', 0.5))],
                        [(0, 0), (0.6, 1.0), (L - 0.4, 1.0), (L, 0)], pulse=(18, 0.4), rough=1.0, sub=0.7, noise=0.9,
                        fmax=3000)
    out = (0.7 * norm(squeak) * (0.6 + 0.6 * tension) + 0.45 * norm(creak) + 0.42 * norm(slide) + 0.18 * norm(peel)
           + 0.4 * norm(wet) + 0.85 * norm(lk) + 0.16 * norm(wag) + 0.22 * norm(dsp.lowpass(groan, 2500, 2)))
    out *= env_pts(n, [(0, 0), (0.12, 1.0), (L - 0.35, 1.0), (L, 0)])
    return room(out, 'patio', 0.12)


def smooth_arr(x, sec):
    return uniform_filter1d(np.asarray(x, np.float64), max(1, N(sec)), mode='nearest')


# ====================================================================== 7. demon_roar
def rev_scream(seed, dur=1.1, f0=950.0, tail_keep=1.7):
    """A shrieking woman's scream through a big echo, played backwards: it swells out of nothing and stops dead."""
    n = N(dur)
    f0c = contour(n, [(0, f0 * 0.82), (0.15, f0 * 1.15), (dur * 0.7, f0 * 1.05), (dur, f0 * 0.72)])
    fr = ftrack(n, [(0, humv('a', 1.0)), (dur * 0.6, humv('e', 1.02)), (dur, humv('a', 0.96))], glide=0.3)
    a = env_pts(n, [(0, 0), (0.05, 1), (dur * 0.8, 0.9), (dur, 0)])
    v1 = vsynth(f0c, fr, a, tilt=0.9, jitter=0.02, shimmer=0.15, rough=0.7, rough_hz=70, sub=0.3, breath=0.25,
                fmax=10000, seed=seed)
    v2 = vsynth(f0c * 0.707, fr, a, tilt=0.95, jitter=0.02, shimmer=0.15, rough=0.9, rough_hz=60, sub=0.4, breath=0.25,
                fmax=9000, seed=seed + 1)
    y = norm(v1) + 0.6 * norm(v2)
    y = verb(y, 'eco', wet=0.55, seed=seed + 2)
    y = y[::-1].copy()
    return y[-N(tail_keep):]


def bloom(seed, dur=0.75, f_hi=95.0, f_lo=36.0, amp=1.0):
    """The body opening up as the little dog becomes the beast: a sub-bass drop (the chest cavity growing) + a wet thud."""
    n = N(dur)
    t = taxis(n)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / 0.12)
    y = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.2) * np.minimum(1, t / 0.006)
    y = norm(y) + 0.5 * norm(thump(seed, 60, dur, 1.0, slap=0.5))
    return norm(dsp.lowpass(y, 900, 2), amp)


def demon_roar(v):
    L = 3.0
    out = np.zeros(N(L), np.float32)
    if v == 1:
        dur = 2.05
        f0p = [(0, 560), (0.04, 680), (0.12, 600), (0.2, 300), (0.4, 95), (0.6, 70), (1.5, 62), (dur, 50)]
        scp = [(0, 1.0), (0.13, 1.0), (0.45, 0.45), (dur, 0.42)]
        ap = [(0, 0), (0.005, 0.8), (0.04, 1.0), (0.13, 0.35), (0.22, 0.55), (0.34, 1.0), (0.6, 0.88), (1.4, 0.95),
              (1.85, 0.5), (dur, 0)]
        t_tear, t_cut, sc_f0, t_on = 0.3, 2.42, 950.0, 0.33
        lead = 0.0
    else:
        lead = 0.17    # an extra "yip" first
        add(out, bark(712, 740, 0.1, 1.2, 0.8, harsh=0.3, breath=0.25), 0.0, 0.8)
        dur = 2.1
        f0p = [(0, 620), (0.05, 720), (0.12, 640), (0.24, 280), (0.45, 82), (0.75, 104), (1.1, 76), (1.7, 64),
               (dur, 52)]
        scp = [(0, 1.0), (0.14, 1.0), (0.5, 0.44), (1.0, 0.4), (dur, 0.43)]
        ap = [(0, 0), (0.005, 0.8), (0.045, 1.0), (0.14, 0.3), (0.25, 0.5), (0.41, 1.0), (0.62, 0.85), (0.75, 0.9),
              (1.2, 1.0), (1.8, 0.6), (dur, 0)]
        t_tear, t_cut, sc_f0, t_on = 0.38, 2.62, 720.0, 0.4
    n = N(dur)
    f0 = contour(n, f0p)
    fr = ftrack(n, [(t, dogv('open', s)) for t, s in scp], glide=0.12)
    a = env_pts(n, ap)
    rough = env_pts(n, [(0, 0.4), (0.15, 0.5), (0.45, 1.4), (dur, 1.6)])
    sub = env_pts(n, [(0, 0.3), (0.12, 0.0), (0.35, 0.9), (dur, 0.9)])
    flutter = np.clip(1 + 0.35 * snoise(n, 38, 700 + v) * env_pts(n, [(0, 0), (0.4, 1), (dur, 1)]), 0.2, None)
    voice = vsynth(f0, fr, a * flutter, tilt=0.75, jitter=0.03, shimmer=0.25, rough=rough, rough_hz=45, sub=sub,
                   breath=0.0, fmax=9000, seed=701 + v, coherent=True)
    nz = shaped_noise(fr, n, 703 + v, sharp=0.75, lp=4500.0) * a * env_pts(n, [(0, 0.35), (0.3, 1.0), (dur, 1.0)])
    nz *= rms(voice) / (rms(nz) + 1e-9)
    octv = vsynth(f0 * 0.5, ftrack(n, [(0, dogv('open', 0.36))]), a * env_pts(n, [(0, 0), (0.3, 0), (0.55, 1), (dur, 1)]),
                  tilt=0.8, jitter=0.03, shimmer=0.2, rough=1.4, rough_hz=35, sub=0.6, breath=0.0, fmax=4000,
                  seed=705 + v)
    roar = norm(voice) + 0.6 * norm(nz) + 0.6 * norm(octv)
    roar = dsp.drive(norm(roar) * 1.5, 1.8)
    # the body closes as the little dog becomes the throat of something huge: bright "arf" -> dark roar
    roar = tv_filter(roar, 'lp', contour(n, [(0, 9500), (0.14, 9500), (0.5, 3800), (dur, 3200)]), 96)
    roar = dsp.lowpass(roar, 7000, 2)
    add(out, roar, lead)
    # ...and the moment the pitch collapses, the body under it blooms: a sub drop you feel more than hear
    add(out, bloom(760 + v), lead + t_on, 0.75)
    # the mouth opens in four petals: flesh tearing, strings of spit
    add(out, squelch(720 + v, 0.35, 1800, 350, 1.0, 6), lead + t_tear, 0.35)
    tr = N(0.25)
    add(out, crackle(tr, 2500 * np.exp(-taxis(tr) / 0.08), 722 + v, 1500, 8000, size=(0.0003, 0.002)), lead + t_tear,
        0.35 / 1.0)
    if v == 2:  # needle teeth chattering
        r = dsp.rng(730)
        for k in range(9):
            add(out, joint_pop(731 + k, r.uniform(2300, 3200), 1.0), lead + 0.95 + k * 0.045, 0.12)
    # the reversed scream swells under the roar and stops dead
    sc = rev_scream(740 + v, 1.1, sc_f0)
    add(out, sc, t_cut - len(sc) / SR, 0.95)
    out = norm(out)
    cut = N(t_cut)
    out[cut:] *= 0.0
    out[cut - N(0.004):cut] *= np.linspace(1, 0, N(0.004))
    return room(out, 'patio', 0.13)


# ====================================================================== 8. fetch_drop
def pant(seed, scale=0.55, ex_dur=0.15, in_dur=0.11, voiced=0.3):
    """One 'HAH-hhh' of a dog panting, with a big mouth and a wet tongue."""
    gap = 0.03
    out = np.zeros(N(ex_dur + gap + in_dur + 0.05), np.float32)
    ne = N(ex_dur)
    fr = ftrack(ne, [(0, dogv('open', scale)), (ex_dur, dogv('mid', scale))], glide=ex_dur)
    ee = env_pts(ne, [(0, 0), (0.012, 1), (ex_dur * 0.45, 0.7), (ex_dur, 0)])
    ex = norm(shaped_noise(fr, ne, seed, hf=0.2, sharp=0.6, lp=4200.0) * ee)
    vf = vsynth(contour(ne, [(0, 150), (ex_dur, 118)]), fr, ee, tilt=1.2, jitter=0.03, rough=0.8, breath=0.0, fmax=5000,
                seed=seed + 1)
    add(out, ex + voiced * norm(vf), 0.0)
    ni = N(in_dur)
    fri = ftrack(ni, [(0, dogv('mid', scale * 1.1))])
    inh = shaped_noise(fri, ni, seed + 2, hf=0.5, sharp=0.5, lp=5000.0)
    inh *= env_pts(ni, [(0, 0), (in_dur * 0.5, 1), (in_dur, 0)])
    add(out, norm(inh), ex_dur + gap, 0.42)
    r = dsp.rng(seed + 3)
    add(out, bubble(r.uniform(900, 1600), seed + 4, rise=0.6, amp=0.12), r.uniform(0.0, 0.03))  # tongue flap
    return out


def fetch_drop():
    L = 3.85
    n = N(L)
    out = np.zeros(n, np.float32)
    r = dsp.rng(700)
    floor_modes = [(92, 30, 1.0), (165, 38, .8), (285, 50, .55), (470, 65, .4), (760, 85, .25), (1250, 120, .15)]
    obj_modes = [(r.uniform(520, 600), 55, 1.0), (r.uniform(980, 1100), 70, .7), (r.uniform(1700, 1900), 95, .45),
                 (r.uniform(2700, 3000), 130, .25)]
    # it lets go of the thing at your feet: a thunk on the floorboards, a bounce, a tick, a slobber splat
    for k, (t0, a) in enumerate(((0.05, 1.0), (0.165, 0.32), (0.235, 0.1))):
        add(out, knock(701 + k, floor_modes, 0.4, contact=0.0025, click=0.25, click_hp=1500), t0, a)
        add(out, knock(711 + k, obj_modes, 0.3, contact=0.0012, click=0.4), t0, 0.7 * a)
    add(out, squelch(705, 0.16, 1600, 500, 1.0, 3), 0.055, 0.32)
    add(out, bubble(1150, 706, rise=1.0, amp=0.1), 0.62)
    add(out, bubble(1400, 707, rise=1.1, amp=0.08), 0.97)
    # panting: a happy dog at the scale of a horse
    tp, k = 0.34, 0
    pn = np.zeros(n, np.float32)
    while tp < L - 0.35:
        add(pn, pant(720 + 5 * k, scale=r.uniform(0.53, 0.58)), tp, r.uniform(0.85, 1.0))
        tp += r.uniform(0.32, 0.36)
        k += 1
    pn *= env_pts(n, [(0, 0), (0.34, 0), (0.6, 0.85), (L - 0.4, 1.0), (L, 0.6)])
    add(out, pn, 0.0, 0.55)
    # the tail thumps the floor, somewhere far back along the chain
    tt, k = 0.62, 0
    tail = np.zeros(n, np.float32)
    while tt < L - 0.15:
        add(tail, knock(760 + k, floor_modes, 0.35, contact=0.008, click=0.05, click_hp=800), tt, r.uniform(0.75, 1.0))
        add(tail, bp(white(N(0.06), 780 + k), 300, 2500) * np.linspace(0, 1, N(0.06)) ** 2, tt - 0.06, 0.05)
        tt += 0.42 + r.uniform(-0.02, 0.02)
        k += 1
    tail = verb(dsp.lowpass(tail, 2200, 2), 'living', wet=0.35, seed=9)[:n]
    add(out, norm(tail), 0.0, 0.5)
    return room(out, 'living', 0.1)


# ====================================================================== 9. chomp
def chomp():
    L = 1.55
    out = np.zeros(N(L), np.float32)
    r = dsp.rng(800)
    # the jaws flip open upwards: a quick rising whoosh
    m = N(0.12)
    wh = tv_filter(white(m, 801), 'bp', np.geomspace(500, 1900, m), 32, 1.0) * env_pts(m, [(0, 0), (0.09, 1), (0.12, 0)])
    add(out, norm(wh), 0.0, 0.25)
    tc = 0.12
    # CHOMP: needle teeth clack (two rows), the bread crust crunches, the chorizo squirts, a cartoon "bomp"
    for k, dt in enumerate((0.0, 0.007)):
        cl = modal_ir([(r.uniform(2400, 2700), 220, 1), (r.uniform(3800, 4200), 280, 0.8), (r.uniform(5600, 6200), 380, 0.5),
                       (r.uniform(1400, 1600), 160, 0.4)], 0.05, 802 + k)
        cl[:N(0.0012)] += burst(0.0012, 804 + k, 2.0) * 2.0
        add(out, norm(cl), tc + dt, 0.75 - 0.25 * k)
    cm = N(0.13)
    add(out, norm(crackle(cm, 9000 * np.exp(-taxis(cm) / 0.03), 806, 900, 9000, size=(0.0003, 0.0015))), tc + 0.003,
        0.65)
    add(out, squelch(807, 0.2, 1500, 350, 1.0, 4), tc + 0.01, 0.6)
    bm = N(0.14)
    tb = taxis(bm)
    bomp = np.sin(TWO_PI * np.cumsum(190 * np.exp(-tb / 0.05) + 60) / SR) * np.exp(-tb / 0.05) * np.minimum(1, tb / 0.002)
    add(out, bomp, tc, 0.7)
    # munch, munch
    for k, (t0, a) in enumerate(((0.46, 0.55), (0.72, 0.42))):
        add(out, norm(crackle(N(0.08), 5000 * np.exp(-taxis(N(0.08)) / 0.025), 810 + k, 900, 7000)), t0, a * 0.7)
        add(out, squelch(815 + k, 0.15, 1100, 300, 1.0, 3), t0 + 0.005, a * 0.8)
        add(out, thump(818 + k, 110, 0.12, 1.0, slap=0.2), t0, a * 0.4)
    # GULP: throat closes, a big bubble goes down
    tg = 1.02
    gm = N(0.16)
    tgx = taxis(gm)
    fg = 170 + 280 * smoothstep(tgx / 0.07)
    gulp = np.sin(TWO_PI * np.cumsum(fg) / SR) * env_pts(gm, [(0, 0), (0.006, 1), (0.07, 0.8), (0.16, 0)])
    gulp = dsp.lowpass(gulp + 0.3 * np.sin(2 * TWO_PI * np.cumsum(fg) / SR) * np.exp(-tgx * 30), 2500, 2)
    add(out, joint_pop(820, 700, 1.0), tg - 0.02, 0.25)
    add(out, norm(gulp), tg, 0.6)
    add(out, thump(821, 95, 0.15, 1.0, slap=0.0), tg + 0.05, 0.3)
    return room(out, 'patio', 0.08)


# ====================================================================== 10. vomit
def retch(seed, dur, f0, scale=0.55):
    n = N(dur)
    fr = ftrack(n, [(0, dogv('mid', scale)), (dur * 0.4, dogv('open', scale)), (dur, dogv('mid', scale * 0.95))],
                glide=dur * 0.3)
    a = env_pts(n, [(0, 0), (dur * 0.12, 0.8), (dur * 0.4, 1.0), (dur, 0)])
    v = vsynth(contour(n, [(0, f0 * 1.2), (dur * 0.3, f0), (dur, f0 * 0.8)]), fr, a, tilt=0.8, jitter=0.04,
               shimmer=0.25, rough=1.6, rough_hz=45, sub=0.8, breath=0.0, fmax=6000, seed=seed)
    nz = shaped_noise(fr, n, seed + 1, sharp=0.8, lp=3600.0) * a
    return norm(dsp.lowpass(norm(v) + 0.9 * norm(nz), 6000, 2))


def vomit():
    L = 4.4
    n = N(L)
    t = taxis(n)
    out = np.zeros(n, np.float32)
    r = dsp.rng(850)
    # the heave: two retches from the far end of a too-long body
    add(out, retch(851, 0.22, 110), 0.0, 0.5)
    add(out, retch(852, 0.42, 88), 0.32, 0.9)
    # the gush: a column of thick black liquid
    g0, g1 = 0.62, 3.05
    ge = env_pts(n, [(0, 0), (g0, 0), (g0 + 0.04, 1), (1.6, 0.9), (2.4, 0.6), (g1, 0.25), (3.5, 0)])
    pour = bp(brown(n, 853), 110, 1100) * grain(n, 18, 854, 1.6)
    pour = dsp.lowpass(pour, 1500, 2) * ge
    glugs = np.zeros(n, np.float32)
    tg = g0
    while tg < g1:
        add(glugs, bubble(r.uniform(140, 320), 860 + int(tg * 100), rise=0.8, amp=r.uniform(0.6, 1.0), dmul=0.5),
            tg, float(np.interp(tg, t, ge)))
        tg += 1 / r.uniform(8.0, 11.0)
    small = np.zeros(n, np.float32)
    for k, i in enumerate(poisson_times(70 * ge, 855)):
        add(small, bubble(r.uniform(300, 1200), 1000 + k, rise=0.5, amp=r.uniform(0.2, 0.7)), i / SR)
    gm = N(2.1)
    tgm = taxis(gm)
    garg = vsynth(contour(gm, [(0, 72), (2.1, 64)]), ftrack(gm, [(0, dogv('mid', 0.5))]),
                  env_pts(gm, [(0, 0), (0.1, 1), (1.6, 0.7), (2.1, 0)]) * (0.55 + 0.45 * np.sin(TWO_PI * 34 * tgm)),
                  tilt=0.9, jitter=0.05, shimmer=0.3, rough=1.4, rough_hz=40, sub=0.6, breath=0.0, fmax=4000, seed=856)
    add(out, norm(pour), 0.0, 0.6)
    add(out, norm(glugs), 0.0, 0.55)
    add(out, norm(small), 0.0, 0.3)
    add(out, norm(garg), g0, 0.28)
    # the splatter: it hits the patio tiles
    s0 = 0.7
    sm = N(0.25)
    add(out, norm(bp(white(sm, 857), 400, 9000) * np.exp(-taxis(sm) / 0.05)), s0, 0.6)
    add(out, thump(858, 62, 0.3, 1.0, slap=0.8), s0, 0.5)
    se = env_pts(n, [(0, 0), (s0, 0), (s0 + 0.03, 1), (1.8, 0.8), (2.8, 0.4), (3.3, 0.05), (L, 0)])
    splat = crackle(n, 420 * se, 859, 700, 9000, size=(0.0004, 0.004), pareto=2.0)
    add(out, norm(splat), 0.0, 0.42)
    slaps = np.zeros(n, np.float32)
    for k, i in enumerate(poisson_times(6 * se, 870)):
        add(slaps, bp(burst(0.02, 880 + k, 1.5), 200, 2500), i / SR, r.uniform(0.4, 1.0))
    add(out, norm(slaps), 0.0, 0.3)
    drops = np.zeros(n, np.float32)
    for k, i in enumerate(poisson_times(30 * se, 890)):
        add(drops, bubble(r.uniform(1500, 4000), 2000 + k, rise=1.5, amp=r.uniform(0.2, 0.8), dmul=1.5), i / SR)
    add(out, norm(drops), 0.0, 0.2)
    # drips after
    for k, td in enumerate((3.25, 3.55, 3.72, 4.05)):
        add(out, bubble(r.uniform(1200, 2400), 3000 + k, rise=1.2, amp=1.0), td, 0.12 * (0.85 ** k))
    # the black column itself: a low breathy rush rising out of him
    wh = tv_filter(pink(n, 895), 'bp', 150 * (4.0 ** smoothstep((t - 0.6) / 2.4)), 64, 1.5)
    add(out, norm(wh) * env_pts(n, [(0, 0), (0.6, 0), (1.4, 1), (2.8, 0.4), (3.4, 0)]), 0.0, 0.22)
    return room(out, 'patio', 0.12)


# ====================================================================== 11. metro_retract
def boing(seed, dur=1.9, f0=150.0):
    """Cartoon jaw-harp spring: swoops up, then wobbles 'boi-oi-oi-oing' while it dies (all the way to silence)."""
    n = N(dur)
    t = taxis(n)
    depth = 0.22 * np.exp(-t / 0.33) + 0.015
    rate = 12.5
    f = f0 * (1 - 0.3 * np.exp(-t / 0.03)) * (1 + depth * np.sin(TWO_PI * rate * t))
    src = dsp.osc(f, dur, 'saw')[:n] * 0.6 + dsp.osc(f, dur, 'sine')[:n]
    fc = 950 * (1 + 0.55 * np.sin(TWO_PI * rate * t + 0.6) * (depth / 0.235))
    tw = tv_filter(src, 'bp', fc, 192, 0.8)
    y = 0.65 * norm(tw) + 0.5 * norm(dsp.lowpass(src, 1200, 2))
    y *= np.exp(-t / 0.42) * np.minimum(1, t / 0.003) * env_pts(n, [(0, 1), (dur * 0.7, 1), (dur, 0)])
    return norm(y)


def metro_retract():
    L = 3.0
    out = np.zeros(N(L), np.float32)
    r = dsp.rng(900)
    # the lock lets go
    lk = modal_ir([(2300, 180, 1), (3900, 250, .7), (5600, 350, .4)], 0.03, 901)
    lk[:N(0.001)] += burst(0.001, 902, 2.0)
    add(out, norm(lk), 0.0, 0.45)
    # ZZZZIP: the steel blade whips back in, faster and faster. Its rattle against the throat of the case is a buzz
    # whose pitch IS the speed (short, broad steel resonances so the rising comb reads: "zzzz-iiiip"), over a fainter
    # ringing of the blade, the slide hiss and the spool whirring up; a 14 dB crescendo into the clack.
    z0, z1 = 0.04, 1.02
    zd = z1 - z0
    zn = N(zd)
    u = np.linspace(0, 1, zn)
    ez = env_pts(zn, [(0, 0), (0.02, 0.62), (zd * 0.5, 0.74), (zd * 0.85, 0.9), (zd * 0.97, 1.0), (zd, 0.9)])
    idx, a = stick_slip(zn, 85.0 * (1000.0 / 85.0) ** (u ** 1.25), 903, jitter=0.05, amp_env=ez, amp_lo=0.7)
    kern = modal_ir([(r.uniform(2600, 3000), 900, 1.0), (r.uniform(4200, 4700), 1100, 0.7), (r.uniform(6300, 7000), 1400, 0.45),
                     (r.uniform(1300, 1500), 700, 0.6), (r.uniform(650, 800), 500, 0.4)], 0.012, 904)
    rattle = pulse_train(zn, idx, a, kern)
    ring = pulse_train(zn, idx, a, modal_ir([(2800, 260, 1.0), (4450, 330, 0.6)], 0.03, 914))
    hiss = tv_filter(white(zn, 905), 'bp', 2500 * (1 + 1.4 * u), 64, 1.2) * ez
    rot = np.cumsum(10 + 60 * u ** 1.5) / SR
    whirr = bp(white(zn, 906), 900, 3500) * (0.55 + 0.45 * np.cos(TWO_PI * rot)) * ez
    tone = np.sin(TWO_PI * np.cumsum(380 * (1 + 2.0 * u ** 1.5)) / SR) * ez * (1 + 0.3 * snoise(zn, 40, 907))
    zipx = (0.85 * norm(rattle) + 0.2 * norm(ring) + 0.22 * norm(hiss) + 0.25 * norm(whirr)
            + 0.1 * norm(bp(tone, 300, 5000)))
    add(out, zipx, z0)
    add(out, squelch(908, 0.8, 1300, 300, 1.0, 4, visc=1.2), z0 + 0.05, 0.14)  # it IS a body going in
    # CLACK: the hook - his head - slams into the case
    tc = z1
    cl = knock(910, [(1100, 90, 1), (1900, 120, .8), (3100, 170, .6), (4500, 240, .4), (700, 60, .5)], 0.25,
               contact=0.0006, click=0.6, click_hp=2500)
    add(out, cl, tc, 1.0)
    add(out, thump(911, 110, 0.18, 1.0, slap=0.3), tc, 0.55)
    # BOING (rings out to silence: no truncated tail)
    add(out, boing(912, 1.9, 200.0), tc + 0.03, 1.25)
    return room(out, 'patio', 0.08)


# ====================================================================== 12. the cumbia (original)
BPM = 96.0
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
NBARS = 16
LOOP = NBARS * BAR          # 40.0 s exactly

CHORDS = ['Am', 'G', 'F', 'E7', 'Am', 'G', ('F', 'E7'), 'Am', 'Dm', 'Am', 'G', 'C', 'F', 'Dm', 'E7', 'Am']
CH_BASS = {'Am': (33, 40), 'G': (31, 38), 'F': (29, 36), 'E7': (28, 35), 'Dm': (38, 33), 'C': (36, 31)}
CH_VOICE = {'Am': (57, 60, 64), 'G': (55, 59, 62), 'F': (53, 57, 60), 'E7': (52, 56, 59, 62), 'Dm': (57, 62, 65),
            'C': (55, 60, 64)}
# melody: per bar [(position in 16ths, length in 16ths, MIDI)]. Original tune (repeated-note syncopated hook, A minor).
MELODY = [
    [(0, 2, 76), (3, 1, 76), (4, 2, 74), (6, 2, 72), (8, 3, 71), (11, 1, 72), (12, 4, 74)],
    [(0, 2, 71), (3, 1, 71), (4, 2, 72), (6, 2, 74), (8, 6, 67), (14, 2, 71)],
    [(0, 2, 72), (3, 1, 72), (4, 2, 74), (6, 2, 76), (8, 3, 77), (11, 1, 76), (12, 2, 74), (14, 2, 72)],
    [(0, 3, 71), (3, 1, 68), (4, 2, 71), (6, 2, 74), (8, 8, 76)],
    [(0, 2, 81), (3, 1, 81), (4, 2, 79), (6, 2, 76), (8, 3, 72), (11, 1, 74), (12, 4, 76)],
    [(0, 2, 74), (3, 1, 74), (4, 2, 71), (6, 2, 67), (8, 2, 71), (10, 2, 74), (12, 2, 79), (14, 2, 77)],
    [(0, 2, 76), (2, 2, 77), (4, 2, 76), (6, 2, 74), (8, 2, 72), (10, 2, 71), (12, 2, 68), (14, 2, 71)],
    [(0, 6, 69), (12, 1, 72), (13, 1, 74), (14, 2, 76)],
    [(0, 2, 77), (3, 1, 77), (4, 2, 76), (6, 2, 74), (8, 3, 81), (11, 1, 79), (12, 4, 77)],
    [(0, 2, 76), (3, 1, 76), (4, 2, 72), (6, 2, 69), (8, 6, 76)],
    [(0, 2, 74), (3, 1, 74), (4, 2, 71), (6, 2, 67), (8, 3, 74), (11, 1, 76), (12, 2, 77), (14, 2, 79)],
    [(0, 6, 76), (6, 2, 72), (8, 4, 67), (12, 2, 72), (14, 2, 76)],
    [(0, 2, 81), (3, 1, 81), (4, 2, 79), (6, 2, 77), (8, 3, 76), (11, 1, 77), (12, 4, 81)],
    [(0, 2, 79), (2, 2, 77), (4, 2, 76), (6, 2, 74), (8, 4, 77), (12, 4, 74)],
    [(0, 2, 76), (2, 2, 74), (4, 2, 71), (6, 2, 68), (8, 2, 76), (10, 2, 74), (12, 2, 71), (14, 2, 68)],
    [(0, 4, 69), (4, 2, 64)],
]


def chord_at(bar, pos16):
    c = CHORDS[bar % NBARS]
    if isinstance(c, tuple):
        return c[0] if pos16 < 8 else c[1]
    return c


def tpos(bar, pos16):
    return bar * BAR + pos16 * S16


_WT = {}


def wtable(K, seed=5):
    """Single-cycle reed waveform with K harmonics (band-limited per note)."""
    if K not in _WT:
        r = dsp.rng(seed)
        k = np.arange(1, K + 1)
        amps = k ** -0.78 * (1 + 0.35 * np.cos(k * 1.3 + 0.4))
        if K > 1:
            amps[1] *= 1.3
        ph = np.arange(4096) / 4096
        phases = r.uniform(0, TWO_PI, K)
        tab = np.zeros(4096)
        for a, kk, p in zip(amps, k, phases):
            tab += a * np.sin(TWO_PI * kk * ph + p)
        _WT[K] = (tab / np.max(np.abs(tab))).astype(np.float32)
    return _WT[K]


def wt_osc(freq, tab, phase0=0.0):
    ph = (phase0 + np.cumsum(freq) / SR) % 1.0
    pos = ph * len(tab)
    i0 = pos.astype(int)
    fr = pos - i0
    return (tab[i0 % len(tab)] * (1 - fr) + tab[(i0 + 1) % len(tab)] * fr).astype(np.float32)


def accordion_note(midi, dur, seed, vel=1.0, reeds=(-0.0034, 0.0, 0.0041), low_reed=0.0, bright=1.0):
    """Synth accordion in musette: three slightly detuned reeds beating, a bellows attack, reedy spectrum."""
    r = dsp.rng(seed)
    f = mtof(midi)
    rel = 0.06
    n = N(dur + rel)
    t = taxis(n)
    K = max(3, min(28, int(9500 * bright / f)))
    tab = wtable(K)
    vib = 1 + 0.0025 * np.sin(TWO_PI * 5.2 * t + r.uniform(0, 6))
    y = np.zeros(n, np.float32)
    for d in reeds:
        y += wt_osc(f * (1 + d) * vib, tab, r.uniform())
    if low_reed:
        y += low_reed * wt_osc(f * 0.5 * vib, wtable(min(40, 2 * K)), r.uniform())
    e = env_pts(n, [(0, 0), (0.018, 1.0), (0.08, 0.85), (max(0.081, dur), 0.8), (dur + rel, 0)])
    return (y * e * vel / len(reeds)).astype(np.float32)


def bass_note(midi, dur, seed, vel=1.0):
    r = dsp.rng(seed)
    f = mtof(midi)
    rel = 0.05
    n = N(dur + rel)
    t = taxis(n)
    ph = TWO_PI * f * t + r.uniform(0, 6)
    y = np.sin(ph) + 0.5 * np.sin(2 * ph + 0.3) + 0.3 * np.sin(3 * ph + 0.7) + 0.16 * np.sin(4 * ph + 1.1) \
        + 0.08 * np.sin(5 * ph + 0.2)
    y += (0.3 * np.sin(6 * ph) + 0.2 * np.sin(7 * ph) + 0.15 * np.sin(8 * ph)) * np.exp(-t / 0.03)
    e = env_pts(n, [(0, 0), (0.004, 1.0), (0.12, 0.7), (max(0.121, dur), 0.6), (dur + rel, 0)])
    return (y * e * vel).astype(np.float32)


def guiro_stroke(seed, dur, rate0, rate1, amp=1.0):
    """A stick scraped over the gourd's ridges: an accelerating click train exciting the hollow body."""
    r = dsp.rng(seed)
    n = N(dur + 0.03)
    nd = N(dur)
    rate = np.concatenate([np.geomspace(rate0, rate1, nd), np.full(n - nd, 1.0)])
    e = env_pts(n, [(0, 0), (0.004, 0.8), (dur * 0.6, 1.0), (dur, 0.9), (dur + 0.004, 0), (n / SR, 0)])
    idx, a = stick_slip(n, rate, seed, jitter=0.12, amp_env=e, amp_lo=0.55)
    kern = modal_ir([(r.uniform(1900, 2300), 500, 1.0), (r.uniform(3300, 3800), 650, 0.8), (r.uniform(5200, 5900), 800, 0.55),
                     (r.uniform(1150, 1400), 380, 0.85), (r.uniform(750, 900), 300, 0.45)], 0.012, seed)
    y = pulse_train(n, idx, a, kern)
    y = norm(y) + 0.25 * norm(bp(white(n, seed + 1), 2500, 8000)) * e
    return norm(y, amp)


def kick(seed, amp=1.0):
    n = N(0.35)
    t = taxis(n)
    f = 52 * (1 + 1.6 * np.exp(-t / 0.018))
    y = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.11) * np.minimum(1, t / 0.001)
    y = norm(y) + 0.25 * fit(norm(bp(burst(0.004, seed, 2.0), 1500, 5000)), n)
    return (y * amp).astype(np.float32)


def conga(kind, seed, amp=1.0):
    r = dsp.rng(seed)
    f = {'open_hi': 335.0, 'open_lo': 228.0, 'slap': 340.0, 'heel': 180.0}[kind] * r.uniform(0.99, 1.01)
    dec = {'open_hi': 1.0, 'open_lo': 0.9, 'slap': 2.5, 'heel': 4.0}[kind]
    modes = [(f, 18 * dec, 1.0), (f * 1.5, 28 * dec, 0.55), (f * 1.98, 36 * dec, 0.4), (f * 2.44, 45 * dec, 0.25),
             (f * 2.9, 55 * dec, 0.15)]
    contact = {'open_hi': 0.002, 'open_lo': 0.0022, 'slap': 0.0008, 'heel': 0.006}[kind]
    click = {'open_hi': 0.1, 'open_lo': 0.08, 'slap': 0.9, 'heel': 0.03}[kind]
    return knock(seed, modes, 0.35, contact=contact, click=click, click_hp=1800) * amp


def timbal(high, seed, amp=1.0, rim=False):
    """Timbales: tuned head on a metal shell, struck with a stick (rimshot = more crack and shell ring)."""
    r = dsp.rng(seed)
    f = (560.0 if high else 390.0) * r.uniform(0.99, 1.01)
    modes = [(f, 22, 1.0), (f * 1.59, 30, 0.6), (f * 2.14, 38, 0.45), (f * 2.65, 45, 0.3), (f * 3.15, 55, 0.2),
             (r.uniform(1800, 2200), 9, 0.15 + 0.2 * rim), (r.uniform(3100, 3500), 12, 0.1 + 0.15 * rim),
             (r.uniform(4500, 4900), 15, 0.08 + 0.1 * rim)]
    y = knock(seed, modes, 0.6, contact=0.0006, click=0.5 + 0.6 * rim, click_hp=2500)
    return (y * amp).astype(np.float32)


def shell_tick(seed, amp=1.0):
    r = dsp.rng(seed)
    modes = [(r.uniform(1800, 2200), 60, 1.0), (r.uniform(3100, 3500), 80, 0.7), (r.uniform(4600, 5000), 110, 0.5),
             (r.uniform(6800, 7400), 150, 0.3)]
    return knock(seed, modes, 0.12, contact=0.0004, click=0.6, click_hp=3000) * amp


_STEMS = {}


def cumbia_stems():
    """Dry band, rendered circularly: dict of mono stems, each exactly LOOP s (notes ringing past the end wrap round)."""
    if _STEMS:
        return _STEMS
    n = N(LOOP)
    ext = n + N(2.0)
    st = {k: np.zeros(ext, np.float32) for k in ('bass', 'acc', 'comp', 'guiro', 'conga', 'timb', 'kick')}
    r = dsp.rng(1961)
    sd = [10000]

    def seed():
        sd[0] += 1
        return sd[0]

    # melody: synth accordion, a hair ahead of the beat on syncopations
    for b, notes in enumerate(MELODY):
        for (p, d, m) in notes:
            t0 = tpos(b, p) + r.uniform(-0.004, 0.004) - (0.006 if p % 4 == 3 else 0.0)
            vel = (1.0 if p % 4 == 0 else 0.86 if p % 2 == 0 else 0.92) * r.uniform(0.9, 1.0)
            add(st['acc'], accordion_note(m, d * S16 * 0.9, seed(), vel), max(0.0, t0))
    # off-beat chords (the keyboard "chuck")
    for b in range(NBARS):
        for p in (2, 6, 10, 14):
            for m in CH_VOICE[chord_at(b, p)]:
                add(st['comp'], accordion_note(m, S16 * 1.3, seed(), 0.5 * r.uniform(0.85, 1.0), reeds=(-0.002, 0.003),
                                               low_reed=0.4, bright=0.7), tpos(b, p) + r.uniform(0, 0.006))
    # bass: bouncy root / fifth with pickups and chromatic approaches
    for b in range(NBARS):
        for (p, kind, d) in ((0, 'R', 3), (4, 'F', 2), (7, 'R', 1), (8, 'R', 3), (12, 'F', 2), (14, 'A', 2)):
            c = chord_at(b, p)
            R, F = CH_BASS[c]
            if kind == 'R':
                m = R
            elif kind == 'F':
                m = F
            else:
                nR = CH_BASS[chord_at(b + 1, 0)][0]
                m = R + 12 if nR == R else nR - 1
            vel = (1.0 if p in (0, 8) else 0.8) * r.uniform(0.9, 1.0)
            add(st['bass'], bass_note(m, d * S16 * 0.78, seed(), vel), tpos(b, p) + r.uniform(0, 0.005))
    # güiro: long scrape on the beat, two short ones on '&' and 'a'
    for b in range(NBARS):
        for q in range(4):
            base = tpos(b, 4 * q) - 0.006
            add(st['guiro'], guiro_stroke(seed(), 0.19, 170, 260, 1.0 if q % 2 else 0.85), max(0.0, base))
            add(st['guiro'], guiro_stroke(seed(), 0.065, 240, 300, 0.7), base + 2 * S16)
            add(st['guiro'], guiro_stroke(seed(), 0.05, 250, 320, 0.6), base + 3 * S16)
    # congas (tumbao) + kick on 1 and 3
    pat = ((0, 'heel', 0.5), (4, 'slap', 0.8), (6, 'open_lo', 0.9), (7, 'open_lo', 0.7), (8, 'heel', 0.5),
           (12, 'slap', 0.8), (14, 'open_hi', 0.9), (15, 'open_lo', 0.8))
    for b in range(NBARS):
        for p, kind, a in pat:
            add(st['conga'], conga(kind, seed(), a * r.uniform(0.85, 1.0)), tpos(b, p) + r.uniform(0, 0.006))
        add(st['kick'], kick(seed(), 1.0), tpos(b, 0))
        add(st['kick'], kick(seed(), 0.85), tpos(b, 8))
    # timbales: accents and fills
    fills = {3: [(12, 1), (13, 1), (14, 0), (15, 0)],
             7: [(8, 1), (10, 1), (11, 1), (12, 0), (13, 0), (14, 2), (15, 0)],
             11: [(12, 1), (13, 0), (14, 1), (15, 0)],
             15: [(4, 1), (5, 1), (6, 0), (7, 0), (8, 1), (9, 1), (10, 0), (11, 0), (12, 2), (13, 1), (14, 0), (15, 0)]}
    for b in range(NBARS):
        if b in fills:
            for k, (p, h) in enumerate(fills[b]):
                a = (0.7 + 0.3 * k / max(1, len(fills[b]) - 1)) * r.uniform(0.9, 1.0)
                add(st['timb'], timbal(h >= 1, seed(), a, rim=(h == 2)), tpos(b, p))
        else:
            add(st['timb'], timbal(True, seed(), 0.6), tpos(b, 14))
            for p in (0, 3, 6, 8, 10, 12):
                add(st['timb'], shell_tick(seed(), 0.22 if p % 4 else 0.3), tpos(b, p))
        if b == 0:
            add(st['timb'], timbal(True, seed(), 0.9, rim=True), 0.0)
    for k, v in st.items():
        _STEMS[k] = fold(v, n)
    return _STEMS


MIX = {'bass': 0.9, 'acc': 0.72, 'comp': 0.3, 'guiro': 0.62, 'conga': 0.4, 'timb': 0.58, 'kick': 0.5}
MELODIC = ('bass', 'acc', 'comp')
DRUMS = ('guiro', 'conga', 'timb', 'kick')


def band_mix(keys):
    st = cumbia_stems()
    y = sum(norm(st[k]) * MIX[k] for k in keys)
    acc_eq = st['acc']  # (melody presence handled in the stem EQ below)
    del acc_eq
    return y.astype(np.float32)


def stem_mix(keys):
    st = cumbia_stems()
    out = np.zeros(N(LOOP), np.float32)
    for k in keys:
        x = norm(st[k]) * MIX[k]
        if k == 'acc':
            x = cfilt(x, lambda f: 1 + bump(f, 1700, 0.7, 0.6))
        out += x
    return out


def wind(n, L, circular=True):
    """Slow 'breeze' between the houses: periodic over the loop (whole cycles) so the stream stays seamless."""
    t = taxis(n)
    gain = 1 + 0.16 * np.sin(TWO_PI * 2 * t / L + 1.3) + 0.09 * np.sin(TWO_PI * 5 * t / L + 0.2)
    bright = 0.5 + 0.3 * np.sin(TWO_PI * 3 * t / L + 0.7) + 0.15 * np.sin(TWO_PI * 7 * t / L + 2.0)
    return gain.astype(np.float32), np.clip(bright, 0, 1).astype(np.float32)


def far_chain(x, pre, circular=True, stereo=True, bright_hz=1900.0, L=None):
    """The neighbour's boombox flat out, heard three houses away at night."""
    n0 = len(x)
    if not circular:
        x = np.concatenate([np.zeros(N(0.5), np.float32), x, np.zeros(N(3.0), np.float32)])
    n = len(x)
    spk = cfilt(x, lambda f: hp2(f, 65) * lp2(f, 7500) * (1 + bump(f, 2600, 0.5, 0.5)))
    spk = dsp.drive(spk * pre, 1.6) / pre
    gb, mb = wind(n, L or LOOP)
    bright = cfilt(spk, lambda f: hp2(f, 90) * lp2(f, bright_hz * 1.35) * lp1(f, 4500) * (1 + bump(f, 150, 0.5, 0.6)))
    dark = cfilt(spk, lambda f: hp2(f, 90) * lp2(f, bright_hz * 0.7) * lp1(f, 3500) * (1 + bump(f, 150, 0.5, 0.6)))
    direct = (dark * (1 - mb) + bright * mb) * gb
    taps = ((0.043, 0.22, 0.55, 1300), (0.097, 0.17, -0.6, 1150), (0.152, 0.13, 0.8, 1000), (0.236, 0.1, -0.35, 900),
            (0.371, 0.06, 0.5, 800))
    if stereo:
        out = pan(direct, -0.3)
    else:
        out = direct.copy()
    for d, g, p, fc in taps:
        tap = np.roll(cfilt(direct, lambda f, fc=fc: lp2(f, fc)), N(d)) * g
        out = out + (pan(tap, p) if stereo else tap)
    if stereo:
        out = verb_st(out, 'barrio', wet=0.16, dry=1.0, seed=31, circular=True)
    else:
        out = verb(out, 'barrio', wet=0.16, dry=1.0, seed=31, circular=True)
    if not circular:
        out = out[N(0.5):]
        out = out[:n0 + N(2.4)]
    return out.astype(np.float32)


_FAR = {}


def far_stems():
    """(melodic, drums) far-away stereo stems, circular, exactly LOOP s. Their sum is casa.cumbia_far."""
    if not _FAR:
        mel, drm = stem_mix(MELODIC), stem_mix(DRUMS)
        pre = 1.3 / (np.max(np.abs(mel + drm)) + 1e-9)
        _FAR['pre'] = pre
        _FAR['mel'] = far_chain(mel, pre)
        _FAR['drm'] = far_chain(drm, pre)
    return _FAR['mel'], _FAR['drm']


def cumbia_far():
    mel, drm = far_stems()
    return (mel + drm).astype(np.float32)


def cumbia_cut():
    """The far cumbia, then the record is yanked back and forth, the needle skids off, the power dies."""
    far_stems()
    pre = _FAR['pre']
    dry = stem_mix(MELODIC) + stem_mix(DRUMS)
    total = 3.0
    n = N(total)
    t = taxis(n)
    ts = 0.85
    v = np.ones(n)
    for a0, a1, v0, v1 in ((ts, ts + 0.055, 1.0, -2.3), (ts + 0.055, ts + 0.12, -2.3, 2.6), (ts + 0.12, ts + 0.19, 2.6, -1.0)):
        i0, i1 = N(a0), N(a1)
        v[i0:i1] = v0 + (v1 - v0) * smoothstep(np.linspace(0, 1, i1 - i0))
    v[N(ts + 0.19):] = 0.0
    pos = 12.5 * SR + np.cumsum(v)
    L = len(dry)
    ext = np.concatenate([dry, dry[:2]])
    rec = np.interp(np.mod(pos, L), np.arange(L + 2), ext).astype(np.float32)
    gate = np.ones(n, np.float32)
    g0 = N(ts + 0.19)
    gate[g0:] = 0.0
    gate[g0 - N(0.006):g0] = np.linspace(1, 0, N(0.006))
    rec *= gate
    # hand on the vinyl: stylus noise while the speed is wrong
    sv = np.abs(v - 1) * (t > ts) * (t < ts + 0.2)
    scr = bp(white(n, 960), 1500, 7000) * smooth_arr(sv, 0.005) * 0.08
    # the needle skids across the grooves: ZZRRRIP
    k0, kd = ts + 0.16, 0.3
    kn = N(kd)
    ke = env_pts(kn, [(0, 0), (0.008, 1), (kd * 0.7, 0.7), (kd, 0)])
    idx, a = stick_slip(kn, np.geomspace(240, 90, kn), 961, jitter=0.2, amp_env=ke, amp_lo=0.5)
    kern = modal_ir([(1800, 300, 1), (3500, 450, .8), (6200, 600, .5), (900, 200, .4)], 0.015, 962)
    skid = norm(pulse_train(kn, idx, a, kern)) + 0.45 * norm(bp(white(kn, 963), 2000, 8000)) * ke
    sk = np.zeros(n, np.float32)
    add(sk, norm(skid), k0, 0.6)
    add(sk, thump(964, 45, 0.25, 1.0, slap=0.0), k0, 0.35)                     # the tonearm jumps
    add(sk, fit(dsp.highpass(burst(0.002, 965, 2.0), 800, 2), N(0.01)), k0 + kd, 0.4)  # needle leaves the record
    # then the neighbour's power dies: amp thump, 50 Hz hum draining away
    tp = k0 + kd + 0.12
    hum_t = t
    hum = sum(a_ * np.sin(TWO_PI * 50 * h * hum_t) for h, a_ in ((1, 1.0), (2, 0.6), (3, 0.5), (4, 0.35), (5, 0.2)))
    hum_env = np.where(t < tp, 1.0, np.exp(-(t - tp) / 0.22)) * 0.02
    pw = np.zeros(n, np.float32)
    add(pw, half_sine(0.018) * 0.5, tp)
    add(pw, fit(dsp.highpass(burst(0.0015, 966, 2.0), 1000, 2), N(0.01)), tp, 0.15)
    music = far_chain(rec + scr + pw + hum * hum_env, pre, circular=False, stereo=False)
    scratch = far_chain(sk, pre, circular=False, stereo=False, bright_hz=2800.0)
    out = music + scratch * 1.25
    return out[:N(total + 1.0)].astype(np.float32)


# ---------------------------------------------------------------------- 1961 music box
def tine(midi, seed, vel=1.0, cents=0.0, buzz=0.0):
    """One steel comb tooth plucked by a cylinder pin: beating fundamental, a fast 'tink' overtone, pin click, box knock."""
    r = dsp.rng(seed)
    f = mtof(midi) * 2 ** (cents / 1200)
    tau = float(np.clip(2.6 * (600 / f) ** 0.7, 0.5, 3.2))
    dur = min(3.5, tau * 3.5)
    n = N(dur)
    t = taxis(n)
    y = np.sin(TWO_PI * f * t + r.uniform(0, 6)) * np.exp(-t / tau)
    y += 0.35 * np.sin(TWO_PI * f * (1 + r.uniform(0.0006, 0.0014)) * t + r.uniform(0, 6)) * np.exp(-t / (tau * 0.9))
    f2 = f * r.uniform(5.6, 6.1)
    if f2 < 17000:
        y += 0.22 * vel * np.sin(TWO_PI * f2 * t) * np.exp(-t * 14)
    y += 0.05 * np.sin(TWO_PI * 2 * f * t) * np.exp(-t / (tau * 0.4))
    y *= np.minimum(1, t / 0.0004)
    y = y.astype(np.float32)
    y[:N(0.0007)] += dsp.highpass(burst(0.0007, seed + 1, 2.0), 2500, 2) * 0.25
    exc = np.zeros(N(0.25), np.float32)
    hs = half_sine(0.0015)
    exc[:len(hs)] = hs
    box = excite(exc, [(r.uniform(290, 330), 28, 1.0), (r.uniform(520, 580), 34, 0.7), (r.uniform(860, 920), 45, 0.5),
                       (r.uniform(1400, 1500), 60, 0.3)], 0.25)
    add(y, norm(box) * 0.08, 0.0)
    if buzz:  # a worn damper touching the still-ringing tooth
        bm = N(0.035)
        tb = taxis(bm)
        bz = bp(white(bm, seed + 3), 1500, 6000) * (np.sin(TWO_PI * f * tb) > 0.6) * np.linspace(1, 0, bm)
        add(y, bz, 0.0, buzz * 0.25)
    return (y * vel).astype(np.float32)


def ratchet_turn(seed, clicks=7, dur=0.38):
    """A turn of the winding key: the pawl clicking over the ratchet wheel, the spring tightening."""
    r = dsp.rng(seed)
    out = np.zeros(N(dur + 0.1), np.float32)
    for k in range(clicks):
        tk = k * dur / clicks + r.uniform(-0.006, 0.006)
        cl = modal_ir([(r.uniform(2700, 3000), 200, 1.0), (r.uniform(4500, 4900), 260, 0.7), (r.uniform(6900, 7400), 350, 0.4),
                       (r.uniform(600, 700), 80, 0.3)], 0.04, seed + k)
        cl[:N(0.0008)] += burst(0.0008, seed + 50 + k, 2.0)
        add(out, norm(cl), max(0.0, tk), r.uniform(0.6, 1.0) * (0.85 + 0.15 * k / clicks))
    fr = bp(white(len(out), seed + 99), 600, 3000) * env_pts(len(out), [(0, 0), (0.05, 1), (dur, 1), (dur + 0.05, 0),
                                                                          (len(out) / SR, 0)])
    return (norm(out) + 0.06 * norm(fr)).astype(np.float32)


def musicbox_map(L, t_stop=34.4, s_end=19.62, dt=0.001):
    """Song-time map s(t) of the music box: the cumbia's 96 BPM sagging to ~0.2x until the spring runs out."""
    t = np.arange(0, L + dt, dt)
    shape = np.where(t < 3.0, 0.0, 1 - 0.78 * np.clip((t - 3.0) / (t_stop - 3.0), 0, 1) ** 1.7)

    def build(vA):
        v = np.where(t < 3.0, 1 - (1 - vA) * smoothstep(t / 3.0), vA * shape)
        v = np.where(t > t_stop, 0.0, v)
        return v, np.concatenate([[0.0], np.cumsum(v[:-1]) * dt])

    lo, hi = 0.3, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        _, s = build(mid)
        if np.interp(t_stop, t, s) < s_end:
            lo = mid
        else:
            hi = mid
    v, s = build((lo + hi) / 2)
    return t, v, s


def cumbia_musicbox():
    L = LOOP
    n = N(L)
    mel_far, drm_far = far_stems()
    t_stop = 34.4
    tg, vg, sg = musicbox_map(L, t_stop)
    vA = float(np.interp(3.0, tg, vg))
    r = dsp.rng(1961)
    # ---- the music box (mono, dry) playing bars 1-8 of the same melody
    box = np.zeros(n + N(4.0), np.float32)
    cents = {m: float(np.clip(r.normal(0, 12), -25, 25)) for m in range(55, 100)}
    cents[86] = -38.0     # two worn teeth
    cents[79] = 31.0
    s_last = float(np.interp(t_stop, tg, sg))
    notes = []
    for b in range(8):
        for (p, d, m) in MELODY[b]:
            notes.append((tpos(b, p), m + 12, 1.0))
        c0 = CH_BASS[chord_at(b, 0)][0]
        c8 = CH_BASS[chord_at(b, 8)]
        notes.append((tpos(b, 0), c0 + 36, 0.7))
        notes.append((tpos(b, 8), (c8[1] if chord_at(b, 8) == chord_at(b, 0) else c8[0]) + 36, 0.6))
    sd = 20000
    for s_note, m, a in sorted(notes):
        if s_note > s_last:
            continue
        tn = float(np.interp(s_note, sg, tg))
        speed = float(np.interp(tn, tg, vg))
        entry = 0.3 + 0.7 * smoothstep(s_note / 2.5)
        strength = 0.6 + 0.4 * min(1.0, speed / max(vA, 1e-3))
        droop = -55.0 * np.clip((tn - 3.0) / (t_stop - 3.0), 0, 1) ** 1.3
        sd += 1
        y = tine(m, sd, a * entry * strength * dsp.rng(sd).uniform(0.85, 1.0), cents.get(m, 0.0) + droop,
                 buzz=1.0 if m in (86, 79) else 0.0)
        add(box, y, tn + dsp.rng(sd + 7).uniform(0, 0.008))
    # the mechanism: governor fan whirring at the speed of the spring, a clunk when it stops
    tt = taxis(n)
    speed_t = np.interp(tt, tg, vg)
    run = smooth_arr(((tt > 0.1) & (tt < t_stop)).astype(np.float32), 0.15)
    fan = bp(white(n, 1970), 700, 2600) * (0.6 + 0.4 * np.cos(TWO_PI * np.cumsum(36 * speed_t / vA) / SR)) * run
    gear = bp(white(n, 1971), 90, 260) * run
    mech = 0.012 * norm(fan) + 0.008 * norm(gear)
    add(box, mech, 0.0)
    add(box, knock(1972, [(310, 40, 1), (560, 55, .7), (980, 80, .4), (2100, 150, .25)], 0.3, contact=0.002, click=0.4),
        t_stop + 0.05, 0.22)
    # silence ... then the key winds by itself
    for k, tw in enumerate((35.75, 36.3, 36.85)):
        add(box, ratchet_turn(1980 + 10 * k), tw, 0.16)
    box = fold(box, n)
    box_st = verb_st(pan(box, 0.12), 'pieza', wet=0.3, dry=1.0, seed=41, circular=True)
    room_tone = np.stack([dsp.lowpass(pink(n, 1990), 2500, 2), dsp.lowpass(pink(n, 1991), 2500, 2)], 1) * 0.0025
    # ---- the far cumbia: comes back from three houses away before the seam, then slides into the box after it
    pre, post = 2.6, 3.4
    m_g = N(pre + post)
    tgh = taxis(m_g) - pre
    s_g = np.where(tgh < 0, LOOP + tgh, np.interp(np.maximum(tgh, 0), tg, sg))
    s_g = s_g + 0.004 * np.sin(TWO_PI * 3.1 * np.maximum(tgh, 0)) * smoothstep(tgh / 1.5)   # wow while it sags
    idx = np.mod(s_g * SR, n)

    def read(x):
        ext = np.concatenate([x, x[:2]], 0)
        return np.stack([np.interp(idx, np.arange(n + 2), ext[:, c]) for c in range(2)], 1).astype(np.float32)

    e_in = smoothstep((tgh + pre) / pre)
    e_mel = np.where(tgh < 0, 1.0, np.cos(0.5 * np.pi * np.clip(tgh / post, 0, 1)) ** 1.5)
    e_drm = np.where(tgh < 0, 1.0, np.cos(0.5 * np.pi * np.clip(tgh / 1.1, 0, 1)) ** 2)
    ghost = (read(mel_far) * e_mel[:, None] + read(drm_far) * e_drm[:, None]) * e_in[:, None]
    cut = np.where(tgh < 0.15, 9000.0, 9000.0 * (450 / 9000.0) ** smoothstep((tgh - 0.15) / (post - 0.15)))
    ghost = np.stack([tv_filter(ghost[:, c], 'lp', cut, 128) for c in range(2)], 1)
    # level: the box (near) peaks about where the far cumbia peaks, so the switch from the stream is seamless
    gpk = np.max(np.abs(mel_far + drm_far))
    box_st = box_st * (0.95 * gpk / (np.max(np.abs(box_st)) + 1e-9))
    out = box_st + room_tone * gpk
    a = N(pre)
    out[-a:] += ghost[:a]
    out[:m_g - a] += ghost[a:]
    return out.astype(np.float32), N(0.0)


# ====================================================================== event table + build
EVENTS = {  # event -> ([variant builders], peak dBFS, loop)
    'choripan.whine': ([lambda: whine(1), lambda: whine(2)], -1.0, False),
    'choripan.growl_low': ([lambda: growl_low(1), lambda: growl_low(2)], -1.0, False),
    'choripan.crack': ([lambda v=v: crack(v) for v in range(1, 7)], -3.0, False),
    'choripan.unspool': ([unspool], -3.0, False),
    'choripan.demon_roar': ([lambda: demon_roar(1), lambda: demon_roar(2)], -0.5, False),
}
SEAM_WINDOW = {'casa.cumbia_musicbox': 0.35}   # keep the seam inside the far-cumbia ghost (the swap point)


def rel_paths(name):
    k = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if k > 1 else '') for i in range(k)]


def seam_report(x):
    m = x if x.ndim == 1 else x.mean(axis=1)
    d = np.abs(np.diff(m))
    return float(abs(m[0] - m[-1]) / (np.percentile(d, 75) + 1e-9))


def rotate_to_lull(x, window=None):
    """Roll a periodic buffer so it starts at its quietest 60 ms (optionally only within +-window s of the seam)."""
    m = np.abs(x if x.ndim == 1 else x.mean(axis=1))
    e = uniform_filter1d(m, N(0.06), mode='wrap')
    if window:
        w = N(window)
        cand = np.concatenate([np.arange(0, w), np.arange(len(e) - w, len(e))])
        i = int(cand[np.argmin(e[cand])])
    else:
        i = int(np.argmin(e))
    return np.roll(x, -i, axis=0)


def finish(x, peak_db, loop, window=None):
    x = np.asarray(x, np.float32)
    if loop:  # exact period kept; circular high-pass so master's filter has nothing left to settle
        return dsp.master(rotate_to_lull(cfft_hp(x, 32.0), window), peak_db=peak_db)
    x = dsp.trim(x, -62, 0.08)
    return dsp.master(x, peak_db=peak_db)


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    report = {}
    for name, (fns, pk, loop) in EVENTS.items():
        rels = rel_paths(name)
        stream = SOUNDS[name][3]
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        assert loop == stream, f'{name}: only the streams loop'
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            raw = fn()
            assert raw.ndim == 1 or stream, rel + ' is positional: must be mono'
            x = finish(raw, pk, loop, SEAM_WINDOW.get(name))
            path = dsp.save_ogg(x, rel)
            # Vorbis can overshoot dense, driven material by ~1 dB: re-master if the decoded peak lands over target
            over = 20 * np.log10(np.max(np.abs(sf.read(path, dtype='float32')[0])) + 1e-12) - pk
            if over > 0.3:
                x = finish(raw, pk - (over - 0.1), loop, SEAM_WINDOW.get(name))
                dsp.save_ogg(x, rel)
            st = dsp.analyse(x)
            if loop:
                st['seam'] = round(seam_report(x), 2)
                seam = np.concatenate([x[-N(1.0):], x[:N(1.0)]], 0)
                dsp.spectrogram_png(seam, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '__seam.png'))
            report[rel] = st
            dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            print(f'{rel:30s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    sp = os.path.join(REVIEW_DIR, 'stats.json')
    old = json.load(open(sp)) if os.path.exists(sp) else {}
    old.update(report)
    with open(sp, 'w') as fh:
        json.dump(old, fh, indent=1)
    missing = [rel for name in EVENTS for rel in rel_paths(name)
               if not os.path.exists(os.path.join(dsp.OUT, rel + '.ogg'))]
    if missing:
        print('MISSING:', missing)
    print(f'choripan group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
