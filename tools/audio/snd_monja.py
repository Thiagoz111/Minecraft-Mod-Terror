# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "nun": Sor Agonia and the ghost choir of Colegio Santa Ines de la Vigilia (case 1).

Run from the repo root:  python3 tools/audio/snd_monja.py [substring ...]

Sor Agonia hunts by SOUND and burns in light (BIBLIA 2.1 g/h). Her cues are built from physical models (modal
resonators, friction/turbulence noise, Poisson crackle) and a small source-filter VOICE SYNTH (additive glottal
harmonics through Lorentzian formants, jitter/shimmer, roughness AM and period-doubling sub-harmonics, formant-shaped
breath noise). The choir is the same synth with child formants singing Schubert's Ave Maria (public domain).

  monja.campanita     her warning (2 s before she appears): small brass hand-bell, "ti-LIN, ti-LIN", beating doublets.
  monja.regla_tap     proximity loop (< 16 blocks): quebracho ruler tapped on her palm, "tac... tac...", 1.4 s seamless.
  monja.reglazo       her attack: ruler whoosh + painful slap on skin + wood crack + body thud + ear ring.
  monja.shh           2.5 s enveloping SHHHHH: five mouths at different distances, a huge low exhale, chapel wash.
  monja.burn          flashlight burns her (beat 3): fat sizzle, crackle, smoke, pained INHALED inhuman gasp.
  monja.soplido       she blows a candle out (beat 5): cold breath, flame flutter, snuff, thin smoke hiss.
  monja.ceiling       Maitines wave: cloth and bones crawling over the ceiling above you, muffled through plaster.
  monja.mojada        beat 13 gag [RISA]: offended "Mmmmm... ¿¡HM-EH?!" (her two voices) dripping tap water.
  monja.scream        confessional/mirror jumpscare: shriek + dissonant choir harmonics + demonic undertone.
  monja.hiss          beat 5 at the hatch: feral hiss of a large cat-like thing, spit + throat rattle + growl.
  monja.whisper (3)   inverted prayer: whispered Latin Pater noster, REVERSED, layered with a low voice, pre-swells.
  monja.hurt          pained shriek while burning, voice cracking, fat sizzle under it.
  monja.death         the demon tears out of her: rising scream + falling demon, then a sucking reverse swell, cut.
  coro.ave_reves      STEREO 20 s seamless loop: 7 lo-fi girls humming the Ave Maria, reversed, in the chapel.
  coro.ave_derecho_1  STEREO: phrase 1 forward, 3 timid voices (Maitines, after phrase 1 of the prayer).
  coro.ave_derecho_2  STEREO: phrase 2, 7 voices in two parts.
  coro.ave_derecho_3  STEREO: phrase 3, full choir in three parts + pipe organ, swelling reverb, final cadence.
  coro.acorde_final   Laudes catharsis (mono, positional): Bb major choir + organ swell, handbells cascading, shimmer.

Positional sounds are mono; only the coro.* streams are stereo. Loudness: screams -0.5 dBFS, voices -1 dBFS,
foley -3 dBFS, loops/streams -4 dBFS.
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

REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    _os.path.join(WORK, 'audio/colegio_nun'))
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
    """Mix x into buf starting at t seconds (truncated at the end of buf). Works for mono and stereo."""
    s = N(t) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        buf[s:s + m] += x[:m] * g
    return buf


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def pink(n, seed):
    return fit(dsp.noise(n / SR + 1e-4, 'pink', seed), n)


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


def smooth(x, sec):
    return uniform_filter1d(np.asarray(x, np.float64), max(1, N(sec)), mode='nearest')


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
    """Poisson crackle (fat, embers, joints): tiny decaying noise ticks with heavy-tailed amplitudes."""
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
    dur = min(0.2, 6.5 / d)
    t = taxis(N(dur))
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.0008)
    return (y * amp).astype(np.float32)


def cfft_hp(x, f=35.0):
    """Circular (loop-safe) zero-phase high-pass, works on mono or stereo."""
    X = np.fft.rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / np.sqrt(1 + (f / np.maximum(fr, 1e-3)) ** 8)
    g = g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X * g, len(x), axis=0).astype(np.float32)


def pan(x, p):
    return dsp.pan(np.asarray(x, np.float32), float(np.clip(p, -1, 1)))


# ====================================================================== rooms
ROOMS = {
    'pasillo': dict(decay=1.8, damp=5200.0, predelay=0.008, er=8, er_span=0.07, hf=0.5),
    'aula': dict(decay=1.0, damp=5500.0, predelay=0.007, er=7, er_span=0.028, hf=0.55),
    'cocina': dict(decay=0.9, damp=5000.0, predelay=0.005, er=7, er_span=0.025, hf=0.55),
    'refectorio': dict(decay=1.6, damp=4800.0, predelay=0.012, er=8, er_span=0.045, hf=0.5),
    'dormitorio': dict(decay=1.5, damp=4200.0, predelay=0.012, er=8, er_span=0.05, hf=0.45),
    'capilla': dict(decay=4.6, damp=3800.0, predelay=0.035, er=9, er_span=0.09, hf=0.45),
    'cripta': dict(decay=3.1, damp=2900.0, predelay=0.018, er=8, er_span=0.05, hf=0.45),
    'banos': dict(decay=1.4, damp=7000.0, predelay=0.007, er=9, er_span=0.03, hf=0.7),
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
            ir[q] += r.uniform(0.4, 1.0) * r.choice([-1, 1]) * lvl * 14
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


def verb(x, room, wet=0.3, dry=1.0, seed=7, wet_env=None, circular=False, **over):
    """Mono room reverb (dry + wet); output extended by the tail unless circular (loop-safe)."""
    w = _conv(x, room_ir(room, seed, **over), circular)
    out = np.zeros(len(w), np.float32)
    out[:len(x)] += dry * x
    g = wet if wet_env is None else wet * fit(wet_env, len(w))
    out += g * w * 2.0
    return out.astype(np.float32)


def verb_st(x, room, wet=0.3, dry=1.0, seed=11, wet_env=None, circular=False, **over):
    """True-stereo reverb: four decorrelated IRs (L->L, R->L, R->R, L->R)."""
    irs = [room_ir(room, seed + i, **over) for i in range(4)]
    L, R = x[:, 0], x[:, 1]
    wl = _conv(L, irs[0], circular) + 0.55 * _conv(R, irs[1], circular)
    wr = _conv(R, irs[2], circular) + 0.55 * _conv(L, irs[3], circular)
    w = np.stack([wl, wr], 1) * (2.0 / 1.14)
    out = np.zeros_like(w, dtype=np.float32)
    out[:len(x)] += dry * x
    g = wet if wet_env is None else wet * fit(wet_env, len(w))[:, None]
    out += g * w
    return out.astype(np.float32)


# ====================================================================== voice synth (source-filter, additive)
CTRL = 64          # control-rate hop (samples)
VOWELS = {         # adult female: (formant Hz, bandwidth Hz, amplitude)
    'a': ((850, 110, 1.0), (1350, 130, 0.55), (2850, 190, 0.28), (3900, 260, 0.14), (4900, 340, 0.06)),
    'e': ((520, 85, 1.0), (2100, 130, 0.38), (2900, 190, 0.3), (3900, 260, 0.12), (4900, 340, 0.05)),
    'i': ((330, 70, 1.0), (2600, 150, 0.33), (3300, 210, 0.3), (4200, 280, 0.12), (4900, 340, 0.05)),
    'o': ((560, 85, 1.0), (950, 100, 0.6), (2800, 190, 0.14), (3800, 260, 0.07), (4800, 340, 0.03)),
    'u': ((380, 70, 1.0), (850, 95, 0.35), (2700, 190, 0.06), (3800, 260, 0.035), (4800, 340, 0.02)),
    'm': ((260, 60, 1.0), (1100, 250, 0.035), (2300, 300, 0.02), (3500, 300, 0.01), (4500, 300, 0.005)),
    'h': ((900, 300, 0.5), (1700, 400, 0.5), (2900, 400, 0.5), (4000, 500, 0.4), (5200, 600, 0.3)),
}


def vowel(name, scale=1.0, bw=1.0, mixwith=None, mix=0.0):
    v = np.array([(f * scale, b * bw * (0.6 + 0.4 * scale), a) for f, b, a in VOWELS[name]], np.float64)
    if mixwith is not None and mix > 0:
        u = np.array([(f * scale, b * bw * (0.6 + 0.4 * scale), a) for f, b, a in VOWELS[mixwith]], np.float64)
        v = (1 - mix) * v + mix * u
    return v


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
    """Formant gain at frequencies f (nfr, nb) for track fr (nfr, nf, 3): sum of Lorentzian peaks."""
    F, B, A = fr[:, None, :, 0], fr[:, None, :, 1], fr[:, None, :, 2]
    return (A / np.sqrt(1 + ((f[..., None] - F) / (B / 2)) ** 2)).sum(-1)


def shaped_noise(fr, n, seed, nper=1024, hf=0.0):
    """White noise filtered (STFT) by the formant track: breath, whisper, aspiration."""
    hop = nper // 4
    w = white(n + nper, seed)
    f, t, Z = signal.stft(w, SR, nperseg=nper, noverlap=nper - hop)
    fi = np.clip((t * SR / CTRL).astype(int), 0, fr.shape[0] - 1)
    g = fgain(np.broadcast_to(f[None, :], (len(fi), len(f))), fr[fi])
    if hf:
        g = g * (1 + hf * f[None, :] / 4000.0)
    _, y = signal.istft(Z * g.T, SR, nperseg=nper, noverlap=nper - hop)
    return fit(y, n)


def vsynth(f0, fr, amp, tilt=1.2, jitter=0.004, shimmer=0.04, rough=0.0, rough_hz=80.0, sub=0.0, breath=0.03,
           fmax=8000.0, seed=0, coherent=False, floor=0.004, f1_track=False, breath_hf=0.0):
    """Additive glottal source through formants. f0/amp per sample, fr control-rate formant track."""
    n = len(f0)
    r = dsp.rng(seed)
    f0 = np.asarray(f0, np.float64) * (1 + jitter * snoise(n, 30, seed + 1))
    if rough:
        f0 = f0 * (1 + 0.025 * rough * snoise(n, rough_hz, seed + 2))
    ph = TWO_PI * np.cumsum(f0) / SR
    nfr = fr.shape[0]
    ci = np.minimum(np.arange(nfr) * CTRL, n - 1)
    f0c = f0[ci]
    if f1_track:  # singers raise F1 to the fundamental on high notes
        fr = fr.copy()
        fr[:, 0, 0] = np.maximum(fr[:, 0, 0], 1.08 * f0c)
    K = max(1, int(fmax / max(25.0, f0c.min())))
    ks = np.arange(1, K + 1, dtype=np.float64)
    tt = np.arange(n)
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
    if sub:
        ks2 = np.arange(0.5, K + 0.5, 1.0)
        ysub = bank(ks2, phs[::-1])
        y += sub * (0.65 + 0.35 * snoise(n, 7, seed + 5)) * ysub
    if shimmer:
        y *= 1 + shimmer * snoise(n, 40, seed + 3)
    if rough:
        y *= np.clip(1 + 0.6 * rough * snoise(n, rough_hz * 1.3, seed + 4), 0.05, None)
    y *= amp
    if breath:
        nz = shaped_noise(fr, n, seed + 6, hf=breath_hf)
        nz *= rms(y) / (rms(nz * amp) + 1e-9)
        y = y + breath * nz * amp
    return y.astype(np.float32)


def contour(n, pts, log=True):
    """f0 contour from [(sec, Hz)] (log-interpolated)."""
    e = env_pts(n, [(t, np.log(f) if log else f) for t, f in pts])
    return np.exp(e) if log else e


def whisperize(x, seed, smooth_bins=10, hf_db=4.0):
    """Replace phonation by noise with the same spectral envelope (a whisper)."""
    f, _t, Z = signal.stft(x, SR, nperseg=1024, noverlap=768)
    env = uniform_filter1d(np.abs(Z), smooth_bins, axis=0)
    env *= (1 + (10 ** (hf_db / 20) - 1) * np.clip((f[:, None] - 1500) / 3000, 0, 1))
    ph = np.exp(1j * dsp.rng(seed).uniform(0, TWO_PI, Z.shape))
    _, y = signal.istft(env * ph, SR, nperseg=1024, noverlap=768)
    return fit(y, len(x))


# ====================================================================== 1. campanita
def small_bell_ir(prime, dur, seed):
    """Small brass hand-bell: church-bell partial ratios (minor-third tierce), every mode a beating doublet."""
    r = dsp.rng(seed)
    # QA: hum (0.5) lowered and damped faster: at 0.07 / 3.2 s^-1 it was the loudest line in the ring (the clapper's
    # soft contact favours low modes), which made the "campanita" read as a much bigger, lower bell.
    parts = [(0.5, 6.0, 0.025), (1.0, 4.5, 0.55), (1.19, 5.5, 0.38), (1.5, 6.5, 0.22), (2.0, 6.0, 1.0),
             (2.52, 9.0, 0.42), (2.67, 10.0, 0.3), (3.02, 12.0, 0.3), (4.08, 17.0, 0.18), (5.32, 24.0, 0.1),
             (6.7, 32.0, 0.05)]
    modes = []
    for ratio, d, a in parts:
        f = prime * ratio * r.uniform(0.997, 1.003)
        split = r.uniform(0.8, 2.6)
        modes += [(f - split / 2, d, a * 0.55), (f + split / 2, d * 1.08, a * 0.45)]
    return modal_ir(modes, dur, seed)


def campanita():
    n = N(1.05)
    prime = 1290.0
    out = np.zeros(n, np.float32)
    # QA: the soft "ti" strikes used a 0.7 ms contact, whose spectral null sat on the 2.6 kHz nominal, so they came
    # out ~20 dB under the "LIN" and the bell read as two plain dings. A short contact for every strike, softer "ti".
    strikes = [(0.0, 0.42, 0.00034), (0.085, 1.0, 0.00028), (0.43, 0.38, 0.00036), (0.512, 0.92, 0.0003)]
    exc = np.zeros(n, np.float32)
    clk = np.zeros(n, np.float32)
    for i, (t, a, contact) in enumerate(strikes):
        add(exc, half_sine(contact), t, a)
        add(clk, dsp.highpass(burst(0.0015, 30 + i, 2.0), 5000, 2), t, a)
    ir = small_bell_ir(prime, 1.3, 21)
    ring = signal.fftconvolve(exc, ir)[:n]
    out += norm(ring) + 0.25 * norm(clk)
    out *= env_pts(n, [(0, 1), (0.72, 1), (1.0, 0), (1.05, 0)])
    out = verb(out, 'pasillo', wet=0.16, seed=3)[:n]
    return out


# ====================================================================== 2. regla_tap (loop)
def palm_tap(seed, amp=1.0, bright=1.0):
    """Quebracho ruler slapped against a palm: fleshy slap + wood knock + low hand thud."""
    r = dsp.rng(seed)
    n = N(0.35)
    y = np.zeros(n, np.float32)
    t = taxis(n)
    slap = bp(white(n, seed), 500, 4500) * np.exp(-t / 0.006) * np.minimum(1, t / 0.0006)
    exc = np.zeros(n, np.float32)
    exc[:N(0.0012)] = half_sine(0.0012)
    # QA: hard quebracho is heavily damped; the old 55/s first mode left a pitched 1 kHz "tink" ringing through the
    # whole hallway tail. Faster modes, plus a mid-band palm "thwack" so the tac has body at a distance.
    wood = excite(exc, detune([(980, 110, 1.0), (2380, 150, 0.6), (3900, 200, 0.4), (5700, 260, 0.25)], r, 0.04),
                  0.2)[:n]
    thud = dsp.lowpass(white(n, seed + 1), 380, 2) * np.exp(-t / 0.018) * np.minimum(1, t / 0.0015)
    thwack = bp(white(n, seed + 3), 250, 1100) * np.exp(-t / 0.012) * np.minimum(1, t / 0.0008)
    y += 0.9 * norm(slap) + 0.6 * bright * norm(wood) + 0.32 * norm(thud) + 0.3 * norm(thwack)
    y = dsp.highpass(y, 110, 2)
    y = dsp.drive(norm(y) * 1.7, 1.7)       # QA: tame the 1 ms spike so the tac carries at -4 dBFS peak
    swish = bp(white(N(0.14), seed + 2), 900, 3800) * np.linspace(0, 1, N(0.14)) ** 2
    out = np.zeros(N(0.14) + n, np.float32)
    out[:len(swish)] += 0.05 * norm(swish)
    out[N(0.14):] += y
    return out * amp, 0.14


def regla_tap():
    L = N(1.4)
    out = np.zeros(L + N(0.6), np.float32)
    for t, a, s, br in [(0.12, 1.0, 41, 1.0), (0.82, 0.86, 47, 0.85)]:
        x, pre = palm_tap(s, a, br)
        add(out, x, t - pre)
    loop = out[:L].copy()
    loop[:len(out) - L] += out[L:]          # wrap the tail (loop-safe)
    return verb(loop, 'pasillo', wet=0.17, seed=5, circular=True)


# ====================================================================== 3. reglazo
def reglazo():
    # QA: the game plays this on the same tick as the damage, red flash and camera shake (ColegioScript.reglazo),
    # so the slap must land almost at once. The old 0.27 s wind-up put it ~0.2 s late; a quebracho ruler swung
    # by a 2.7 m nun is a fast, short swish anyway.
    n = N(1.05)
    out = np.zeros(n, np.float32)
    ti = 0.085
    # whoosh: the ruler swung through the air, rising band + thin edge whistle (Doppler-ish rise into the hit)
    nw = N(ti + 0.012)
    tw = taxis(nw)
    wenv = np.clip(tw / ti, 0, 1) ** 2.2
    w = tv_filter(white(nw, 51), 'bp', 700 + 3200 * np.clip(tw / ti, 0, 1) ** 2, 24, 1.2) * wenv
    whistle = np.sin(TWO_PI * np.cumsum(900 + 1700 * np.clip(tw / ti, 0, 1) ** 2) / SR) * wenv \
        * (0.5 + 0.5 * grain(nw, 40, 52, 1))
    add(out, norm(w) * 0.42 + norm(whistle) * 0.05, 0.0)
    # impact: skin slap (broadband), meaty mid smack, wood crack (damped hardwood), flesh/body thud
    m = N(0.6)
    t = taxis(m)
    slap = bp(white(m, 53), 700, 9000, 2) * np.exp(-t / 0.009) * np.minimum(1, t / 0.0004)
    smack = bp(white(m, 54), 1600, 5000, 2) * np.exp(-t / 0.025)
    meat = bp(white(m, 57), 260, 1200, 2) * np.exp(-t / 0.03) * np.minimum(1, t / 0.0008)
    exc = np.zeros(m, np.float32)
    exc[:N(0.0005)] = half_sine(0.0005)
    r = dsp.rng(55)
    crack = excite(exc, detune([(1150, 120, 1.0), (2650, 160, 0.7), (4300, 220, 0.5), (6800, 300, 0.3)], r),
                   0.3)[:m]
    thud = dsp.lowpass(white(m, 56), 320, 2) * np.exp(-t / 0.03) * np.minimum(1, t / 0.002)
    body = np.sin(TWO_PI * 105 * t) * np.exp(-t / 0.028) * np.minimum(1, t / 0.002)
    hit = (norm(slap) * 1.0 + norm(smack) * 0.45 + norm(meat) * 0.5 + norm(crack) * 0.42 + norm(thud) * 0.45
           + norm(body) * 0.25)
    hit = dsp.drive(norm(hit) * 2.0, 2.0)
    add(out, hit, ti)
    # the sting: a faint tinnitus ring in the struck ear
    ring_n = N(0.8)
    tr = taxis(ring_n)
    ring = np.sin(TWO_PI * 5600 * tr) * np.exp(-tr / 0.25) * np.minimum(1, tr / 0.05)
    add(out, ring * 0.03, ti + 0.02)
    out = verb(out, 'aula', wet=0.2, seed=9)
    return out[:N(1.05)] * env_pts(N(1.05), [(0, 1), (0.8, 1), (1.05, 0)])


# ====================================================================== 4. shh
def shush_layer(n, seed, fc, env, flutter=0.25):
    y = white(n, seed)
    y = dsp.highpass(y, fc * 0.6, 4)
    y = dsp.peak(y, fc, 10.0, 1.3)
    y = dsp.peak(y, fc * 1.9, 4.0, 1.5)
    # QA: /ʃ/ (not /s/): energy falls away above ~5 kHz. At 9.5 kHz the 6-10 kHz band sat only 3-6 dB under the
    # 2.5 kHz peak, which reads as hiss or static rather than a mouth going SHHH.
    y = dsp.lowpass(y, 5200, 2)
    turb = grain(n, 90, seed + 1, 1.0) ** 0.4
    sway = 1 + flutter * snoise(n, 1.3, seed + 2)
    return norm(y) * turb * sway * env


def shh():
    n = N(2.5)
    out = np.zeros(n, np.float32)
    layers = [(2600, 0.00, 1.0, 0.0), (3300, 0.10, 0.75, 0.02), (2200, 0.18, 0.7, 0.035), (3900, 0.28, 0.45, 0.05),
              (2900, 0.05, 0.6, 0.012)]
    for i, (fc, t0, g, dly) in enumerate(layers):
        e = env_pts(n, [(0, 0), (t0, 0), (t0 + 0.35, 0.8), (1.0, 1.0), (1.55, 1.05), (1.95, 0.55), (2.25, 0.0),
                        (2.5, 0.0)])
        x = shush_layer(n, 600 + 7 * i, fc, e)
        # each mouth at its own distance: delay + darker when farther
        x = dsp.lowpass(x, 9000 - 1200 * i, 2)
        add(out, x, dly, g)
    # the moving mouth: a sweeping band, like the sound circling the player
    sweep = 2700 + 600 * np.sin(TWO_PI * 0.7 * taxis(n))
    out = 0.7 * out + 0.5 * norm(tv_filter(out, 'bp', sweep, 64, 0.8)) * rms(out) / 0.3
    # huge low exhale under it
    e2 = env_pts(n, [(0, 0), (0.25, 0.6), (1.2, 1.0), (1.9, 0.5), (2.3, 0)])
    low = bp(pink(n, 621), 180, 1400) * e2 * (0.8 + 0.2 * grain(n, 30, 622, 1))
    out += norm(low) * 0.1 * np.max(np.abs(out))
    out = verb(out, 'capilla', wet=0.42, seed=13, decay=2.6)
    return out[:N(2.55)] * env_pts(N(2.55), [(0, 1), (2.3, 1), (2.55, 0)])


# ====================================================================== 5. burn
def demon_layer(n, f0_pts, seed, scale=0.72, sub=0.6, rough=0.9, vow='a', amp=None, tilt=0.9):
    f0 = contour(n, f0_pts)
    fr = ftrack(n, [(0, vowel(vow, scale))])
    amp = np.ones(n) if amp is None else amp
    y = vsynth(f0, fr, amp, tilt=tilt, jitter=0.02, shimmer=0.15, rough=rough, rough_hz=35, sub=sub, breath=0.25,
               fmax=6000, seed=seed, coherent=True)
    return dsp.drive(norm(y) * 2.0, 2.2)


def burn():
    n = N(2.05)
    t = taxis(n)
    out = np.zeros(n, np.float32)
    # fat sizzle: dense crackle + frying hiss (rate & level decay as she pulls back into the dark)
    rate = 900 * np.exp(-t / 0.5) + 120
    crk = crackle(n, rate, 71, 1800, 10000, amp_env=np.exp(-t / 0.9) + 0.15)
    fry = bp(white(n, 72), 2500, 11000) * (grain(n, 400, 73, 2.0) ** 0.5)
    fenv = env_pts(n, [(0, 0), (0.015, 1.0), (0.35, 0.75), (1.2, 0.35), (2.05, 0.0)])
    pops = np.zeros(n, np.float32)
    r = dsp.rng(74)
    for j in range(26):
        tp = r.uniform(0.02, 1.8)
        add(pops, bubble(r.uniform(2500, 6000), 300 + j, rise=0.8, amp=r.uniform(0.3, 1.0), dmul=2.5), tp)
    sizzle = norm(crk) * 0.6 + norm(fry) * 0.35 * fenv + norm(pops) * 0.18 * fenv
    sizzle = dsp.drive(norm(sizzle) * 1.8, 1.6) * env_pts(n, [(0, 1.0), (0.25, 0.6), (0.9, 0.38), (1.4, 0.2),
                                                              (2.05, 0.05)])
    # smoke: a dark billow rising and drifting
    senv = env_pts(n, [(0, 0), (0.25, 0.7), (0.8, 1.0), (2.05, 0.0)])
    smoke = tv_filter(pink(n, 75), 'bp', 450 + 400 * snoise(n, 0.8, 76) ** 2, 48, 1.5) * senv
    # pained INHALED gasp: noisy ingress with tonal squeaks breaking through + demon underneath
    ge = env_pts(n, [(0, 0), (0.06, 0.0), (0.25, 0.55), (0.8, 1.0), (0.98, 1.0), (1.02, 0.0), (2.05, 0)])
    fr = ftrack(n, [(0.0, vowel('a', 1.1)), (0.5, vowel('e', 1.1)), (0.95, vowel('i', 1.1))], glide=0.4)
    gasp = shaped_noise(fr, n, 77, hf=0.8)
    gasp = dsp.highpass(gasp, 600, 2) * ge
    f0 = contour(n, [(0, 480), (0.3, 620), (0.9, 980), (1.0, 1050)])
    gate = np.clip(0.5 + 1.6 * snoise(n, 9, 78), 0, 1)
    squeal = vsynth(f0, fr, ge * gate, tilt=0.8, jitter=0.03, shimmer=0.2, rough=0.8, rough_hz=60, sub=0.35,
                    breath=0.2, fmax=9000, seed=79)
    dem = demon_layer(n, [(0, 120), (1.0, 150)], 80, scale=0.7, amp=ge) * ge
    voice = norm(gasp) * 0.7 + norm(squeal) * 0.5 + norm(dem) * 0.3
    out = dsp.lowpass(sizzle, 12000, 2) * 0.75 + norm(dsp.highpass(smoke, 150, 2)) * 0.12 + voice * 0.85
    out = verb(out, 'aula', wet=0.16, seed=17)
    return out[:N(2.15)] * env_pts(N(2.15), [(0, 1), (1.85, 1), (2.15, 0)])


# ====================================================================== 6. soplido
def soplido():
    n = N(1.8)
    t = taxis(n)
    # the blow: a big cold mouth with rounded lips, "ffffuuuh" (energy low, a thin fricative edge on top)
    be = env_pts(n, [(0, 0), (0.04, 0.8), (0.12, 1.0), (0.32, 0.7), (0.5, 0.0), (1.8, 0)])
    fr = ftrack(n, [(0, vowel('u', 0.8, mixwith='h', mix=0.12)), (0.3, vowel('o', 0.78, mixwith='h', mix=0.2))])
    blow = shaped_noise(fr, n, 91) * be * (0.7 + 0.3 * grain(n, 60, 92, 1.0))
    fric = bp(white(n, 93), 1800, 6500) * be ** 2
    low = bp(pink(n, 94), 70, 400) * be
    # the flame flapping in the gust (13-21 Hz) then guttering out
    fe = env_pts(n, [(0, 0), (0.06, 0.0), (0.1, 1.0), (0.38, 0.9), (0.46, 0.3), (0.5, 0.0), (1.8, 0)])
    rate = 13 + 8 * np.clip((t - 0.08) / 0.4, 0, 1)
    flap = 0.5 + 0.5 * np.sin(TWO_PI * np.cumsum(rate * (1 + 0.15 * snoise(n, 6, 95))) / SR)
    flutter = dsp.lowpass(white(n, 96), 380, 2) * (0.15 + flap ** 3) * fe
    sput = crackle(n, 30 * fe + 1e-3, 97, 1500, 6000, amp_env=fe)
    # the snuff: a soft low "fwup" as the flame dies
    snuff = dsp.lowpass(burst(0.07, 98, 1.5), 260, 2)
    # thin smoke hiss curling off the wick, slowly wavering
    he = env_pts(n, [(0, 0), (0.46, 0), (0.56, 1.0), (1.1, 0.6), (1.75, 0)])
    hiss = bp(white(n, 99), 4000, 9000) * he * np.clip(1 + 0.5 * snoise(n, 4, 100), 0.2, None)
    out = (norm(blow) * 0.85 + norm(fric) * 0.08 + norm(low) * 0.3 + norm(flutter) * 0.55 + norm(sput) * 0.1
           + norm(hiss) * 0.1)
    add(out, norm(snuff) * 0.4, 0.46)
    out = verb(out, 'refectorio', wet=0.15, seed=19)
    return out[:N(1.8)] * env_pts(N(1.8), [(0, 1), (1.6, 1), (1.8, 0)])


# ====================================================================== 7. ceiling
CEIL_BOARD = [(88, 28, 0.55), (162, 34, 0.75), (305, 48, 0.55), (610, 75, 0.35), (1150, 120, 0.2)]


def ceiling():
    dur = 3.0
    n = N(dur)
    r = dsp.rng(111)
    above = np.zeros(n, np.float32)      # everything heard through the ceiling
    room = np.zeros(n, np.float32)       # what falls into the room
    plants = [0.1, 0.36, 0.95, 1.16, 1.62, 1.83, 2.3, 2.5]
    for i, tp in enumerate(plants):
        a = r.uniform(0.6, 1.0) * (1.0 if i % 2 == 0 else 0.7)
        exc = np.zeros(N(0.6), np.float32)
        exc[:N(0.006)] = half_sine(0.006)
        thump = excite(exc, detune(CEIL_BOARD, r, 0.05), 0.5)[:N(0.6)]
        add(above, norm(thump), tp, a)
        # bones: fingertip / knuckle ticks on plaster a hair before and after the plant
        for k in range(r.integers(1, 4)):
            tk = tp + r.uniform(-0.03, 0.05)
            ex2 = np.zeros(N(0.08), np.float32)
            ex2[:N(0.0004)] = half_sine(0.0004)
            tick = excite(ex2, detune([(2100, 260, 1), (3400, 380, .6), (5200, 500, .3)], r, 0.1), 0.06)
            add(above, norm(tick), tk, a * r.uniform(0.25, 0.5))
    # cloth drags between plants: heavy wool on rough plaster
    drags = [(0.16, 0.5), (0.45, 0.95), (1.22, 1.62), (1.9, 2.3), (2.56, 2.95)]
    for j, (t0, t1) in enumerate(drags):
        m = N(t1 - t0)
        e = np.sin(np.pi * np.linspace(0, 1, m)) ** 0.7
        tex = grain(m, 22, 120 + j, 2.0) ** 0.7 * (0.6 + 0.4 * grain(m, 180, 130 + j, 1.0))
        cloth = bp(white(m, 140 + j), 250, 3000) * tex * e
        add(above, norm(cloth), t0, 0.75)
    # joints cracking (a run of sharp pops)
    for tc in (0.7, 2.08):
        for k in range(5):
            ex3 = np.zeros(N(0.05), np.float32)
            ex3[:N(0.0003)] = half_sine(0.0003)
            pop = excite(ex3, detune([(1700, 300, 1), (2900, 420, .7), (4600, 600, .4)], r, 0.15), 0.04)
            add(above, norm(pop), tc + k * r.uniform(0.008, 0.02), r.uniform(0.4, 0.8))
    # a joist creaking under her weight
    cm = N(0.5)
    rate = 55 + 25 * np.sin(np.linspace(0, np.pi, cm))
    ph = np.cumsum(rate * (1 + 0.2 * snoise(cm, 15, 150))) / SR
    pulses = np.zeros(cm, np.float32)
    idx = np.nonzero(np.diff(np.floor(ph)))[0]
    pulses[idx] = r.uniform(0.4, 1.0, len(idx))
    creak = excite(pulses, [(240, 45, 1), (520, 60, .6), (1100, 90, .3)], 0.2)[:cm]
    add(above, norm(creak) * np.sin(np.linspace(0, np.pi, cm)) ** 0.5, 1.28, 0.35)
    # through the plaster: dark, boomy; she crosses over the player (loudest in the middle)
    above = dsp.lowpass(above, 2600, 2)
    above = dsp.highpass(dsp.peak(above, 140, 2.0, 1.0), 70, 2)
    path = env_pts(n, [(0, 0.55), (1.5, 1.0), (3.0, 0.6)])
    above *= path
    # grit and plaster dust trickling down into the room (bright, close)
    for k, td in enumerate((0.98, 1.66, 2.34)):
        m = N(0.6)
        lam = 140 * np.exp(-taxis(m) / 0.15) + 5
        grit = crackle(m, lam, 160 + k, 3000, 11000, size=(0.0002, 0.0008))
        add(room, grit * np.exp(-taxis(m) / 0.25), td, 0.5)
    out = norm(above) + 0.12 * norm(room)
    out = verb(out, 'dormitorio', wet=0.14, seed=23)
    return out[:N(3.25)] * env_pts(N(3.25), [(0, 1), (3.0, 1), (3.25, 0)])


# ====================================================================== 8. mojada
def monja_voice(n, f0_pts, fkeys, amp, seed, breath=0.12, low_gain=0.45, glide=0.08):
    """Sor Agonia's two voices: a woman (-5 st) doubled by something huge an octave and a half below."""
    f0 = contour(n, f0_pts)
    fr = ftrack(n, fkeys, glide)
    hi = vsynth(f0, fr, amp, tilt=1.15, jitter=0.008, shimmer=0.08, rough=0.15, rough_hz=50, breath=breath,
                fmax=8000, seed=seed)
    fr_lo = fr.copy()
    fr_lo[:, :, 0] *= 0.78
    lo = vsynth(f0 * 0.39, fr_lo, amp, tilt=0.95, jitter=0.02, shimmer=0.12, rough=0.6, rough_hz=30, sub=0.4,
                breath=0.1, fmax=5000, seed=seed + 10, coherent=True)
    lo = dsp.drive(norm(lo) * 1.8, 1.8)
    return norm(hi) + low_gain * lo


def mojada():
    dur = 3.1
    n = N(dur)
    r = dsp.rng(171)
    water = np.zeros(n, np.float32)
    # the habit streaming water: a burst of drops thinning out, then single fat drips into the puddle
    lam = 70 * np.exp(-taxis(n) / 0.35)
    for j, i in enumerate(poisson_times(lam, 172)):
        f = r.uniform(900, 2600)
        add(water, bubble(f, 400 + j, rise=r.uniform(0.3, 0.9), amp=r.uniform(0.2, 0.7)), i / SR)
        add(water, dsp.lowpass(dsp.highpass(burst(0.004, 500 + j, 2.0), 2500, 2), 7000, 2), i / SR,
            r.uniform(0.02, 0.07))
    for j, td in enumerate((0.72, 1.12, 1.41, 2.28, 2.62, 2.9)):
        add(water, bubble(r.uniform(1100, 1700), 600 + j, rise=0.9, amp=1.0, dmul=0.8), td)
        add(water, dsp.lowpass(dsp.highpass(burst(0.003, 650 + j, 2.0), 2500, 2), 7000, 2), td, 0.07)
    trickle = bp(white(n, 173), 1500, 6000) * env_pts(n, [(0, 0), (0.03, 1), (0.5, 0.2), (1.0, 0)]) \
        * grain(n, 120, 174, 2.0) ** 0.5
    water += 0.25 * norm(trickle) * np.max(np.abs(water))
    # "Mmmmmmm..." (closed mouth, offended, wavering) then "¿¡hm-EH?!" (rising, indignant)
    amp = env_pts(n, [(0, 0), (0.32, 0), (0.45, 0.75), (0.9, 0.85), (1.25, 0.6), (1.38, 0.0), (1.5, 0.0),
                      (1.55, 0.55), (1.68, 0.7), (1.76, 1.0), (2.0, 1.0), (2.1, 0.0), (dur, 0)])
    f0 = [(0, 215), (0.4, 212), (0.75, 198), (1.0, 206), (1.3, 190), (1.5, 185), (1.62, 190), (1.75, 240),
          (1.95, 330), (2.1, 345)]
    keys = [(0, vowel('m', 1.0)), (1.2, vowel('m', 1.0)), (1.3, vowel('u', 1.0, mixwith='m', mix=0.5)),
            (1.55, vowel('m', 1.0)), (1.74, vowel('e', 1.0)), (1.95, vowel('a', 1.0)), (2.1, vowel('a', 1.0))]
    v = monja_voice(n, f0, keys, amp, 181, breath=0.1)
    # the [h] of "hm-EH": a voiceless puff shaped like the vowel that follows
    he = env_pts(n, [(0, 0), (1.62, 0), (1.7, 1.0), (1.78, 0.4), (1.85, 0), (dur, 0)])
    asp = shaped_noise(ftrack(n, [(0, vowel('e', 1.0))]), n, 182, hf=0.5) * he
    v = norm(v) + 0.35 * norm(asp)
    v = dsp.peak(v, 2500, 3.0, 1.2)
    out = norm(water) * 0.5 + norm(v) * 0.9
    out = verb(out, 'dormitorio', wet=0.16, seed=29)
    return out[:N(3.25)] * env_pts(N(3.25), [(0, 1), (3.0, 1), (3.25, 0)])


# ====================================================================== 9. scream (+ hurt, death)
def scream_core(n, f0_pts, amp, seed, choir=((7, 0.3), (-12, 0.32), (-5, 0.24), (1, 0.16)), demon=0.42,
                demon_pts=((0, 95), (1.6, 78)), bright=0.45, rough=0.55):
    """Shriek: rough bright female scream + choir-like parallel voices + demonic undertone."""
    # QA: with a smooth contour the fundamental drew one clean, steady line (a siren / synth "aah", not a throat
    # tearing). Real screams wobble by several percent, and break into bursts of vocal-fold chaos (sub-harmonics,
    # noise). The parallel choir voices ride on the same unstable f0.
    f0 = contour(n, f0_pts)
    f0 = f0 * (1 + 0.035 * snoise(n, 7, seed + 50) + 0.015 * snoise(n, 28, seed + 51))
    chaos = np.clip(snoise(n, 4, seed + 52), 0, None) ** 2
    f0 = f0 * (1 + 0.07 * chaos * snoise(n, 150, seed + 53))
    fr = ftrack(n, [(0, vowel('a', 1.18)), (0.35, vowel('a', 1.18, mixwith='e', mix=0.35)),
                    (0.8, vowel('a', 1.18)), (1.3, vowel('a', 1.18, mixwith='o', mix=0.25))], glide=0.25)
    main = vsynth(f0, fr, amp, tilt=bright, jitter=0.012, shimmer=0.12, rough=rough, rough_hz=95, sub=0.28,
                  breath=0.18, breath_hf=0.6, fmax=11000, seed=seed, f1_track=True)
    torn = vsynth(f0, fr, amp, tilt=bright, jitter=0.03, shimmer=0.25, rough=rough * 2.6, rough_hz=110, sub=0.95,
                  breath=0.4, breath_hf=0.8, fmax=11000, seed=seed + 60, f1_track=True)
    ep = np.clip(0.2 + 1.4 * chaos, 0, 0.85)
    y = (1 - ep) * norm(main) + ep * norm(torn)
    for k, (semi, g) in enumerate(choir):
        fk = f0 * 2 ** (semi / 12) * (1 + 0.006 * np.sin(TWO_PI * 5.8 * taxis(n) + k))
        vk = vsynth(fk, ftrack(n, [(0, vowel('a' if semi < 0 else 'o', 1.12))]), amp, tilt=0.95, jitter=0.006,
                    shimmer=0.06, breath=0.05, fmax=9000, seed=seed + 20 + k, f1_track=True)
        y += g * norm(vk)
    if demon:
        dem = demon_layer(n, list(demon_pts), seed + 40, scale=0.7, amp=amp)
        y += demon * dem * amp
    return y


def scream():
    n = N(1.62)
    amp = env_pts(n, [(0, 0), (0.012, 0.85), (0.06, 1.0), (0.9, 0.95), (1.2, 0.8), (1.42, 0.0), (1.62, 0)])
    f0 = [(0, 640), (0.07, 990), (0.25, 1060), (0.95, 1130), (1.2, 1070), (1.42, 820)]
    y = scream_core(n, f0, amp, 201)
    blast = bp(white(N(0.05), 202), 900, 7000) * np.exp(-taxis(N(0.05)) / 0.012)
    add(y, norm(blast) * 0.6, 0.0)
    y = dsp.drive(norm(y) * 1.5, 1.6)
    y = dsp.peak(y, 3000, 2.5, 1.0)
    out = verb(y, 'aula', wet=0.14, seed=31)
    return out[:N(1.62)] * env_pts(N(1.62), [(0, 1), (1.45, 1), (1.62, 0)])


def hurt():
    n = N(1.0)
    t = taxis(n)
    amp = env_pts(n, [(0, 0), (0.01, 0.9), (0.15, 1.0), (0.6, 0.85), (0.86, 0.35), (0.98, 0)])
    f0 = [(0, 880), (0.05, 1230), (0.19, 1290), (0.215, 1640), (0.3, 1520), (0.36, 1180), (0.6, 1080),
          (0.85, 620), (1.0, 470)]
    y = scream_core(n, f0, amp, 211, choir=((7, 0.22), (-12, 0.2), (1, 0.14)), demon=0.3,
                    demon_pts=((0, 110), (1.0, 82)), bright=0.55, rough=0.75)
    y = dsp.drive(norm(y) * 1.4, 1.5)
    sizz = crackle(n, 500 * np.exp(-t / 0.4) + 80, 212, 2000, 10000, amp_env=np.exp(-t / 0.6) + 0.2)
    out = norm(y) + 0.28 * norm(sizz)
    return verb(out, 'aula', wet=0.13, seed=33)[:N(1.05)] * env_pts(N(1.05), [(0, 1), (0.92, 1), (1.05, 0)])


def death():
    dur = 3.0
    n = N(dur)
    cut = 2.86
    # A: the scream rises while the demon drops away under it (tearing apart)
    na = N(1.9)
    amp = env_pts(na, [(0, 0), (0.05, 0.7), (0.6, 0.9), (1.4, 1.0), (1.75, 0.7), (1.9, 0.0)])
    f0 = [(0, 330), (0.5, 520), (1.0, 820), (1.5, 1280), (1.9, 1420)]
    choir = ((7, 0.3), (-12, 0.3), (12, 0.12), (1, 0.18))
    core = scream_core(na, f0, amp, 221, choir=choir, demon=0.0, bright=0.5, rough=0.7)
    dem = demon_layer(na, [(0, 120), (0.8, 80), (1.9, 42)], 222, scale=0.68, sub=0.8, rough=1.0, amp=amp)
    a = norm(core) + 0.55 * dem * amp
    for k, tr in enumerate((0.32, 0.78, 1.21, 1.55)):        # flesh and cloth tearing
        m = N(0.18)
        rip = crackle(m, 2200 * np.ones(m), 230 + k, 900, 6000, size=(0.0004, 0.002))
        rip *= np.sin(np.pi * np.linspace(0, 1, m)) ** 0.5
        add(a, norm(rip) * 0.35, tr)
    a = dsp.drive(norm(a) * 1.5, 1.6)
    # B: sucking reverse swell: her reverb tail played backwards, a vacuum inhale, a rising whistle; cut dead
    wet_only = verb(a, 'cripta', wet=1.0, dry=0.0, seed=37, decay=3.5)
    rev = dsp.reverse(wet_only)
    nb = N(cut)
    sw = np.zeros(nb, np.float32)
    sw[nb - min(nb, len(rev)):] = rev[-min(nb, len(rev)):]
    rise = np.clip((taxis(nb) - 1.0) / (cut - 1.0), 0, 1)
    vac = tv_filter(white(nb, 240), 'bp', 300 + 6000 * rise ** 2.5, 64, 1.2) * rise ** 3
    whistle = np.sin(TWO_PI * np.cumsum(260 + 1700 * rise ** 3) / SR) * rise ** 4
    swell = norm(sw) * rise ** 1.2 + 0.6 * norm(vac) + 0.1 * whistle
    swell = dsp.drive(norm(swell) * 1.3, 1.4)
    # QA: the swell used to end no louder than the scream (both ~-10 dB short-term) and the hand-over only dipped to
    # -18 dB, so the "sucking" climax never arrived. Now the scream sits ~3 dB under, the hand-over drops to about
    # -25 dB, and the reverse swell climbs ~20 dB to the loudest moment of the file, right at the cut.
    out = np.zeros(n, np.float32)
    add(out, 0.47 * a * env_pts(na, [(0, 1), (1.4, 1), (1.9, 0)]), 0.0)
    add(out, norm(swell) * env_pts(nb, [(0, 0), (1.35, 0.0), (1.8, 0.14), (2.35, 0.36), (2.7, 0.75), (cut, 1)]),
        0.0)
    out[N(cut) - N(0.006):N(cut)] *= np.linspace(1, 0, N(0.006))
    out[N(cut):] = 0
    # C: implosion thump and a breath of dark air
    m = N(dur - cut)
    tm = taxis(m)
    thump = np.sin(TWO_PI * (70 - 30 * tm / tm[-1]) * tm) * np.exp(-tm / 0.03)
    thump += 0.3 * dsp.lowpass(white(m, 241), 200, 2) * np.exp(-tm / 0.05)
    add(out, thump * 0.5, cut)
    return out


# ====================================================================== 10. hiss
def hiss():
    # QA: the first version was a flat 1.3 s band of noise (no visible spit, no articulation), which reads as
    # static. Now: an explosive spit "KKH!", the hiss bursting out of it and decaying, a throat flutter you can
    # see in the envelope, a second shorter push ("...hhKKHH") and the low growl.
    n = N(1.3)
    env = env_pts(n, [(0, 0), (0.004, 0.0), (0.03, 1.0), (0.12, 0.8), (0.42, 0.55), (0.56, 0.3), (0.6, 0.28),
                      (0.64, 0.85), (0.72, 0.6), (0.95, 0.25), (1.2, 0.0), (1.3, 0)])
    y = white(n, 251)
    y = dsp.highpass(y, 600, 2)
    y = dsp.peak(y, 1750, 12.0, 2.2)
    y = dsp.peak(y, 3400, 9.0, 2.5)
    y = dsp.peak(y, 5200, 4.0, 2.0)
    y = dsp.lowpass(y, 7000, 2)
    # big throat: a husky lower fricative band that a house cat does not have
    husk = bp(white(n, 257), 500, 1600, 2)
    # throat flutter: irregular ~30 Hz pulsing of the airflow (the rattle a big cat's hiss has)
    rate = 28 + 6 * snoise(n, 2, 252)
    flut = 0.5 + 0.5 * np.sin(TWO_PI * np.cumsum(rate) / SR)
    rattle = 0.55 + 0.45 * flut ** 2 * np.clip(1 + 0.5 * snoise(n, 60, 258), 0, None)
    h = (norm(y) + 0.35 * norm(husk)) * env * rattle * (0.85 + 0.15 * grain(n, 300, 253, 1))
    # spits: a hard plosive burst (lips/teeth) with a click at the front, then the second, smaller one
    spit = np.zeros(n, np.float32)
    for t_s, g, sd, dur in ((0.004, 1.0, 254, 0.045), (0.6, 0.55, 255, 0.03)):
        m = N(dur)
        tm = taxis(m)
        b = bp(white(m, sd), 600, 9000) * np.exp(-tm / (dur / 3.5)) * np.minimum(1, tm / 0.0008)
        clk = dsp.highpass(burst(0.0015, sd + 7, 2.0), 2500, 2)
        add(spit, norm(b) + 0.5 * fit(norm(clk), m), t_s, g)
    ge = env_pts(n, [(0, 0), (0.05, 0.15), (0.16, 0.8), (0.5, 0.55), (0.62, 0.75), (0.9, 0.3), (1.2, 0)])
    growl = demon_layer(n, [(0, 66), (0.6, 58), (1.3, 52)], 256, scale=0.75, sub=0.7, rough=1.0, amp=ge)
    growl = bp(growl * ge, 70, 2200)
    out = 0.62 * norm(h) + 1.0 * norm(spit) + 0.32 * norm(growl)
    out = verb(out, 'cocina', wet=0.14, seed=41)
    return out[:N(1.45)] * env_pts(N(1.45), [(0, 1), (1.25, 1), (1.45, 0)])


# ====================================================================== 11. whisper (3)
PATER = [
    'Pater noster, qui es in caelis, sanctificetur nomen tuum.',
    'Adveniat regnum tuum, fiat voluntas tua, sicut in caelo et in terra.',
    'Panem nostrum quotidianum da nobis hodie, et dimitte nobis debita nostra.',
]


def whisper(v):
    target = 3.6
    text = PATER[v - 1]
    a = dsp.tts(text, 'ef_dora', 0.95)
    b = dsp.tts(text, 'em_santa', 0.9)
    wa = whisperize(a, 260 + v)
    wb = whisperize(dsp.pitch_shift(b, -2.0), 270 + v)
    murmur = bp(dsp.pitch_shift(a, -5.0), 200, 2500)
    ra, rb, rm = dsp.reverse(wa), dsp.reverse(wb), dsp.reverse(murmur)
    n = N(target + 0.6)
    y = np.zeros(n, np.float32)
    rate = len(ra) / SR / (target - 0.25)
    ra = dsp.time_stretch(ra, max(0.5, min(2.0, rate)))
    rb = dsp.time_stretch(rb, max(0.5, min(2.0, len(rb) / SR / (target - 0.6))))
    rm = dsp.time_stretch(rm, max(0.5, min(2.0, len(rm) / SR / (target - 0.25))))
    add(y, norm(ra), 0.15, 1.0)
    add(y, norm(rb), 0.42, 0.55)
    add(y, norm(rm), 0.15, 0.07)
    # reverse reverb: every reversed word is preceded by a swell sucked out of the dark
    pre = dsp.reverse(verb(dsp.reverse(y), 'cripta', wet=1.0, dry=0.0, seed=43 + v)[:n])
    y = y + 0.45 * norm(pre) * np.max(np.abs(y))
    y = dsp.highpass(y, 320, 2)
    y = y + 0.6 * dsp.highpass(y, 2200, 2)
    y = dsp.peak(y, 5200, 3.0, 1.0)
    y *= env_pts(n, [(0, 0), (0.25, 1), (target - 0.3, 1), (target + 0.1, 0), (n / SR, 0)])
    out = verb(y, 'capilla', wet=0.16, seed=47 + v, decay=2.5)
    return out[:N(target + 0.35)] * env_pts(N(target + 0.35), [(0, 1), (target, 1), (target + 0.35, 0)])


# ====================================================================== 12. the choir (Schubert's Ave Maria, Bb major)
CHORDS = {'Bb': (10, 2, 5), 'Eb': (3, 7, 10), 'F': (5, 9, 0), 'F7': (5, 9, 0, 3), 'Gm': (7, 10, 2),
          'Cm': (0, 3, 7), 'Cm7': (0, 3, 7, 10)}
# (beats, midi, vowel, consonant at onset: None = slur, '' = vowel onset, letter = consonant)
P1 = [(1.5, 70, 'a', ''), (0.25, 69, 'e', 'v'), (0.25, 70, 'e', None), (0.75, 74, 'a', 'm'), (0.25, 72, 'i', 'r'),
      (1.0, 70, 'a', ''), (0.5, 74, 'a', 'g'), (0.5, 75, 'i', 't'), (1.0, 77, 'a', ''), (0.5, 75, 'e', 'p'),
      (0.5, 74, 'e', None), (1.5, 72, 'a', 'n')]
P1_CH = [(0, 1.5, 'Bb'), (1.5, 2, 'F'), (2, 2.75, 'Bb'), (2.75, 3, 'F'), (3, 4, 'Bb'), (4, 4.5, 'Gm'),
         (4.5, 5, 'Cm'), (5, 6, 'Bb'), (6, 7, 'Eb'), (7, 8.5, 'F')]
P2 = [(1.0, 77, 'a', 'm'), (0.5, 75, 'i', 'r'), (0.5, 74, 'i', None), (1.0, 72, 'a', ''), (0.5, 74, 'a', 'g'),
      (0.5, 75, 'i', 't'), (0.75, 77, 'a', ''), (0.25, 79, 'a', None), (0.5, 77, 'e', 'p'), (0.5, 75, 'e', None),
      (2.0, 74, 'a', 'n')]
P2_CH = [(0, 1, 'Bb'), (1, 1.5, 'Eb'), (1.5, 2, 'Bb'), (2, 3, 'F'), (3, 3.5, 'Bb'), (3.5, 4, 'Eb'), (4, 4.75, 'Bb'),
         (4.75, 5, 'Eb'), (5, 5.5, 'Bb'), (5.5, 6, 'F7'), (6, 8, 'Bb')]
P3 = [(1.0, 77, 'a', ''), (1.0, 82, 'e', 'v'), (0.75, 79, 'a', ''), (0.25, 77, 'a', None), (1.0, 75, 'e', 'v'),
      (0.5, 74, 'o', 'd'), (0.25, 75, 'i', 'm'), (0.25, 74, 'i', None), (1.0, 72, 'u', 'n'), (0.5, 72, 'e', 't'),
      (0.5, 69, 'e', None), (2.5, 70, 'u', 'k')]
P3_CH = [(0, 1, 'Bb'), (1, 2, 'Eb'), (2, 3, 'Cm7'), (3, 4, 'F7'), (4, 5, 'Bb'), (5, 6, 'Cm'), (6, 7, 'F7'),
         (7, 9.5, 'Bb')]
CONS = {'m': (0.6, 0.09, True), 'n': (0.55, 0.08, True), 'v': (0.5, 0.07, False), 'r': (0.3, 0.035, False),
        't': (0.85, 0.06, False), 'p': (0.9, 0.06, False), 'k': (0.85, 0.06, False), 'd': (0.6, 0.05, False),
        'g': (0.6, 0.05, False), '': (0.25, 0.05, False)}


def timeline(phrase, t0, spb, rit=None):
    """Phrase in beats -> [(t_on, t_off, midi, vowel, cons)] in seconds (rit=(from_beat, extra_s_per_beat^2))."""
    def tb(b):
        x = b * spb
        if rit is not None and b > rit[0]:
            x += rit[1] * (b - rit[0]) ** 2
        return t0 + x
    out, b = [], 0.0
    for beats, m, v, c in phrase:
        out.append((tb(b), tb(b + beats), m, v, c))
        b += beats
    return out


def chord_line(chords, t_of_beat, lo, hi, start, below=None):
    """Voice-led harmony part: nearest chord tone in [lo, hi] (optionally under the `below` line)."""
    res, prev = [], start
    for b0, b1, name in chords:
        pcs = CHORDS[name]
        cand = [m for m in range(lo, hi + 1) if m % 12 in pcs]
        if below is not None:
            ceiling = below(b0, b1) - 3
            cand = [m for m in cand if m <= ceiling] or cand[:1]
        m = min(cand, key=lambda c: (abs(c - prev), -c))
        res.append((t_of_beat(b0), t_of_beat(b1), m))
        prev = m
    merged = []
    for t0, t1, m in res:                      # tie common tones
        if merged and merged[-1][2] == m and abs(merged[-1][1] - t0) < 1e-6:
            merged[-1] = (merged[-1][0], t1, m)
        else:
            merged.append((t0, t1, m))
    return merged


def bass_line(chords, t_of_beat, lo, hi, start):
    """Organ pedal: the chord ROOT in [lo, hi], nearest to the previous one (cadences land on the tonic)."""
    res, prev = [], start
    for b0, b1, name in chords:
        root = CHORDS[name][0]
        m = min((c for c in range(lo, hi + 1) if c % 12 == root), key=lambda c: abs(c - prev))
        if res and res[-1][2] == m and abs(res[-1][1] - t_of_beat(b0)) < 1e-6:
            res[-1] = (res[-1][0], t_of_beat(b1), m)
        else:
            res.append((t_of_beat(b0), t_of_beat(b1), m))
        prev = m
    return res


def girl(n, notes, seed, hum=0.3, tilt=1.05, vib=0.18, breath=0.07, scale=1.15, detune=0.0, drift=8.0,
         glide=0.07, offset=0.0, dyn=None, hum_vowel='u', fmax=7500.0, bw=1.8):
    """One ghost schoolgirl singing notes [(t_on, t_off, midi, vowel, cons)] (seconds)."""
    r = dsp.rng(seed)
    notes = [(a + offset + r.normal(0, 0.008), b + offset, m, v, c) for a, b, m, v, c in notes]
    tt = taxis(n)
    mid = np.full(n, float(notes[0][2]))
    for a, b, m, v, c in notes:
        mid[max(0, N(a)):] = m
    mid = smooth(smooth(mid, glide * 0.5), glide * 0.5)
    vibd = np.zeros(n)
    for a, b, m, v, c in notes:
        i0, i1 = max(0, N(a)), min(n, N(b))
        if i1 <= i0:
            continue
        k = np.arange(i1 - i0) / SR
        if c is not None:
            mid[i0:i1] -= 0.3 * r.uniform(0.4, 1.0) * np.exp(-k / 0.05)
        if b - a > 0.45:
            vibd[i0:i1] = np.clip((k - 0.25) / 0.4, 0, 1)
    vibd = smooth(vibd, 0.12)
    mid = mid + vib * vibd * np.sin(TWO_PI * r.uniform(4.9, 5.7) * tt + r.uniform(0, 6))
    mid = mid + drift / 100 * snoise(n, 0.6, seed + 1) + detune / 100
    f0 = 440.0 * 2 ** ((mid - 69) / 12)
    # amplitude: phrase segments, consonant dips, swells on long notes
    amp = np.zeros(n)
    seg_start = notes[0][0]
    for i, (a, b, m, v, c) in enumerate(notes):
        last = i == len(notes) - 1
        if last or abs(notes[i + 1][0] - b) > 0.06:
            amp += env_pts(n, [(0, 0), (seg_start, 0), (seg_start + 0.14, 1), (max(seg_start + 0.15, b - 0.22), 1),
                               (b + 0.08, 0), (n / SR, 0)])
            if not last:
                seg_start = notes[i + 1][0]
    for a, b, m, v, c in notes:
        if b - a > 0.6:
            amp *= 1 + 0.12 * env_pts(n, [(0, 0), (a, 0), ((a + b) / 2, 1), (b, 0), (n / SR, 0)])
    keys = []
    for a, b, m, v, c in notes:
        base = vowel(v, scale, bw, mixwith=hum_vowel, mix=hum)
        if c and c in CONS:
            depth, w, nasal = CONS[c]
            amp *= 1 - depth * np.exp(-0.5 * ((tt - a + w * 0.2) / (w * 0.45)) ** 2)
            if nasal:
                keys += [(a - w * 0.6, None), (a - w * 0.25, vowel('m', scale, bw)), (a + w * 0.3, base)]
                continue
        keys.append((a, base))
    filled, prev = [], keys[0][1] if keys[0][1] is not None else vowel('m', scale, bw)
    for t, v in keys:
        if v is None:
            v = prev
        filled.append((max(0.0, t), v))
        prev = v
    fr = ftrack(n, filled, 0.07)
    if dyn is not None:
        amp *= dyn
    y = vsynth(f0, fr, amp, tilt=tilt, jitter=0.0035, shimmer=0.05, breath=breath, fmax=fmax, seed=seed + 3,
               f1_track=True, breath_hf=0.4, floor=0.008)
    return y


def inhale(n, t, seed, gain):
    """The girls breathing in before a phrase."""
    m = N(0.4)
    fr = ftrack(m, [(0, vowel('a', 1.15, mixwith='h', mix=0.6))])
    x = dsp.highpass(shaped_noise(fr, m, seed, hf=1.0), 700, 2) * np.sin(np.pi * np.linspace(0, 1, m)) ** 1.5
    out = np.zeros(n, np.float32)
    add(out, norm(x) * gain, t)
    return out


def sing(n, phrase, chords, t0, spb, voices, seed, hum, rit=None, dyn=None, tilt=1.05, vib=0.18, breath=0.07,
         drift=8.0, spread=0.6):
    """voices = (n_melody, n_alto, n_low). Returns a stereo dry choir."""
    notes = timeline(phrase, t0, spb, rit)

    def t_of_beat(b):
        x = b * spb
        if rit is not None and b > rit[0]:
            x += rit[1] * (b - rit[0]) ** 2
        return t0 + x

    def mel_min(b0, b1):
        ms = [m for a, b, m, _v, _c in notes if a < t_of_beat(b1) - 1e-6 and b > t_of_beat(b0) + 1e-6]
        return min(ms) if ms else 70
    alto = chord_line(chords, t_of_beat, 60, 70, 65, below=mel_min)

    def alto_at(b0, b1):
        ms = [m for a, b, m in alto if a < t_of_beat(b1) - 1e-6 and b > t_of_beat(b0) + 1e-6]
        return min(ms) if ms else 65
    low = chord_line(chords, t_of_beat, 55, 64, 58, below=alto_at)
    r = dsp.rng(seed)
    nm, na, nl = voices
    total = nm + na + nl
    pans = np.linspace(-spread, spread, total)
    r.shuffle(pans)
    out = np.zeros((n, 2), np.float32)
    k = 0
    vow_h = {'alto': 'u', 'low': 'o'}
    for part, cnt in (('mel', nm), ('alto', na), ('low', nl)):
        for j in range(cnt):
            s = seed + 100 * k
            if part == 'mel':
                nts, g = notes, (1.0 if j == 0 else 0.8)
            else:
                line = alto if part == 'alto' else low
                vw = ('a' if part == 'alto' else 'o') if hum < 0.25 else 'u'
                nts = [(a, b, m, vw, ('m' if i == 0 else None)) for i, (a, b, m) in enumerate(line)]
                g = 0.55 if part == 'alto' else 0.5
            y = girl(n, nts, s, hum=hum if part == 'mel' else min(0.5, hum + 0.2), tilt=tilt + r.uniform(-0.1, 0.15),
                     vib=vib,
                     breath=breath, scale=r.uniform(1.08, 1.22), detune=r.normal(0, 7), drift=drift,
                     offset=r.normal(0, 0.018), dyn=dyn, hum_vowel=vow_h.get(part, 'u'))
            y = fit(y, n)
            d = r.uniform(0, 0.012)
            y = fit(np.concatenate([np.zeros(N(d), np.float32), y]), n)
            out += pan(norm(y) * g, pans[k])
            k += 1
    out += pan(inhale(n, max(0.0, t0 - 0.45), seed + 7, 0.05 * total ** 0.5), 0.0)
    return out


def lofi(x, seed, lo=160.0, hi=6500.0, drv=1.4, wow=(0.5, 1.4), flutter=(6.0, 0.07), hiss_db=-50.0, loop=False):
    """Old-recording / ghost treatment for a stereo buffer. With loop=True every modulation is periodic."""
    n = len(x)
    t = taxis(n)
    if loop:  # snap modulation rates to whole cycles over the buffer
        L = n / SR
        wow = (round(wow[0] * L) / L, wow[1])
        flutter = (round(flutter[0] * L) / L, flutter[1])
    d = (wow[1] * (1 + np.sin(TWO_PI * wow[0] * t)) / 2 + flutter[1] * (1 + np.sin(TWO_PI * flutter[0] * t)) / 2) \
        * 1e-3 * SR
    pos = np.arange(n) - d
    y = np.zeros_like(x)
    for c in range(x.shape[1]):
        if loop:
            ext = np.concatenate([x[-64:, c], x[:, c], x[:64, c]])
            y[:, c] = np.interp(np.mod(pos, n) + 64, np.arange(len(ext)), ext)
        else:
            y[:, c] = np.interp(pos, np.arange(n), x[:, c])
    y = dsp.highpass(y, lo, 2) if not loop else cfft_hp(y, lo)
    y = dsp.lowpass(y, hi, 2) if not loop else lp_circ(y, hi)
    pk = np.max(np.abs(y)) + 1e-9
    y = dsp.drive(y / pk * drv * 0.7, drv) * pk
    hs = np.stack([bp(white(n, seed), 2500, 9000), bp(white(n, seed + 1), 2500, 9000)], 1)
    y += hs / (rms(hs) + 1e-9) * rms(y) * 10 ** (hiss_db / 20)
    return y.astype(np.float32)


def limit(x, reduce_db=6.0, look=0.006):
    """Smooth look-ahead peak limiter: pulls the loudest sample peaks down by up to `reduce_db`.
    After master() normalises the peak, the denser choir phrases come out louder (a real crescendo at -4 dBFS)."""
    from scipy.ndimage import maximum_filter1d
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    ceiling = np.max(a) * 10 ** (-reduce_db / 20)
    env = uniform_filter1d(maximum_filter1d(a, N(look)), N(look))
    env = uniform_filter1d(np.maximum(env, ceiling), N(0.02))      # slower release, no zipper
    env = np.maximum(env, uniform_filter1d(maximum_filter1d(a, N(look)), N(look)))
    gain = np.minimum(1.0, ceiling / (env + 1e-12))
    return (x * (gain[:, None] if x.ndim == 2 else gain)).astype(np.float32)


def lp_circ(x, f):
    X = np.fft.rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / np.sqrt(1 + (fr / f) ** 4)
    return np.fft.irfft(X * g[:, None], len(x), axis=0).astype(np.float32)


def ave_reves():
    L = 20.0
    n = N(L)
    spb = 1.0
    p1 = sing(n, P1, P1_CH, 0.7, spb, (4, 2, 1), 5001, hum=0.4, drift=10.0, breath=0.09, tilt=1.1)
    p2 = sing(n, P2, P2_CH, 0.7 + 9.0 * spb, spb, (4, 2, 1), 5002, hum=0.4, drift=10.0, breath=0.09, tilt=1.1)
    dry = p1 + p2
    wet = verb_st(dry, 'capilla', wet=0.75, dry=0.55, seed=61, circular=True)
    rev = wet[::-1].copy()
    return lofi(rev, 5003, lo=170, hi=6000, drv=1.5, hiss_db=-48, loop=True)


def organ_note(midi, dur, seed, gain=1.0, ped=False):
    f = 440.0 * 2 ** ((midi - 69) / 12)
    r = dsp.rng(seed)
    rel = 0.18
    n = N(dur + rel)
    t = taxis(n)
    amps = [1.0, 0.55, 0.32, 0.22, 0.14, 0.1, 0.07, 0.05, 0.035, 0.025] if not ped else [1.0, 0.35, 0.12, 0.05]
    y = np.zeros(n)
    for k, a in enumerate(amps, 1):
        if f * k > 9000:
            break
        y += a * np.sin(TWO_PI * f * k * (1 + r.normal(0, 0.0004)) * t + r.uniform(0, 6))
    if not ped:   # 4' octave rank, a hair out of tune (gentle beating)
        for k, a in ((2, 0.3), (4, 0.12), (6, 0.06)):
            y += a * np.sin(TWO_PI * f * k * 1.0009 * t + r.uniform(0, 6))
    env = np.minimum(1, t / 0.07) * env_pts(n, [(0, 1), (dur, 1), (dur + rel, 0)])
    y *= env
    chiff = bp(white(n, seed + 1), min(8000, f * 2.5), min(10000, f * 5)) * np.exp(-t / 0.035) * 0.08
    return ((y / len(amps) ** 0.5 + chiff * (0 if ped else 1)) * gain).astype(np.float32)


def organ(n, chords, t_of_beat, seed):
    out = np.zeros(n, np.float32)
    lines = [bass_line(chords, t_of_beat, 39, 50, 46), chord_line(chords, t_of_beat, 50, 58, 53),
             chord_line(chords, t_of_beat, 55, 62, 58), chord_line(chords, t_of_beat, 60, 66, 62)]
    for li, line in enumerate(lines):
        for j, (a, b, m) in enumerate(line):
            if li == 0:
                add(out, organ_note(m, b - a, seed + j, 0.9, ped=True), a)
                add(out, organ_note(m - 12, b - a, seed + 50 + j, 0.35, ped=True), a)
            else:
                add(out, organ_note(m, b - a, seed + 100 * li + j, 0.55), a)
    return out


def ave_derecho(k):
    spb = 1.0
    t0 = 0.55
    if k == 1:
        n = N(t0 + 8.5 + 2.3)
        dyn = env_pts(n, [(0, 0.4), (3.0, 0.5), (t0 + 5.2, 0.9), (t0 + 6.5, 0.6), (9.5, 0.45)])
        dry = sing(n, P1, P1_CH, t0, spb, (2, 1, 0), 6101, hum=0.5, dyn=dyn, tilt=1.2, vib=0.12, breath=0.11,
                   drift=14.0, spread=0.35)
        wet = verb_st(dry, 'capilla', wet=0.62, dry=0.7, seed=71)[:n]
        y = lofi(wet, 6102, lo=180, hi=6000, drv=1.4, hiss_db=-50)
        fade_from = t0 + 8.5 + 0.6
    elif k == 2:
        n = N(t0 + 8.0 + 2.3)
        dyn = env_pts(n, [(0, 0.75), (4.0, 0.95), (8.5, 1.0)])
        dry = sing(n, P2, P2_CH, t0, spb, (4, 2, 1), 6201, hum=0.3, dyn=dyn, tilt=1.05, vib=0.18, breath=0.08,
                   drift=10.0, spread=0.55)
        wet = verb_st(dry, 'capilla', wet=0.6, dry=0.75, seed=73)[:n]
        y = lofi(wet, 6202, lo=150, hi=7000, drv=1.3, hiss_db=-54, wow=(0.45, 1.0))
        y = limit(y, 2.0)
        fade_from = t0 + 8.0 + 0.6
    else:
        rit = (6.5, 0.12)
        span = 9.5 + rit[1] * 3.0 ** 2
        n = N(t0 + span + 3.0)

        def t_of_beat(b):
            x = b * spb
            if b > rit[0]:
                x += rit[1] * (b - rit[0]) ** 2
            return t0 + x
        dyn = env_pts(n, [(0, 0.8), (t_of_beat(1.5), 1.0), (t_of_beat(4), 1.0), (t_of_beat(7), 0.95),
                          (n / SR, 1.0)])
        dry = sing(n, P3, P3_CH, t0, spb, (6, 4, 3), 6301, hum=0.1, rit=rit, dyn=dyn, tilt=0.9, vib=0.22,
                   breath=0.06, drift=7.0, spread=0.75)
        org = organ(n, P3_CH, t_of_beat, 6302)
        oenv = env_pts(n, [(0, 0.0), (t0 + 0.2, 0.5), (t_of_beat(1.5), 1.0), (n / SR, 1.0)])
        org_st = np.stack([dsp.lowpass(org, 5000, 2) * oenv, dsp.lowpass(np.roll(org, N(0.004)), 5000, 2) * oenv], 1)
        mix_ = dry + 0.32 * org_st * np.max(np.abs(dry)) / (np.max(np.abs(org_st)) + 1e-9)
        wenv = env_pts(n, [(0, 0.45), (t_of_beat(4), 0.7), (t_of_beat(8), 1.0), (n / SR, 1.0)])
        mix_ = mix_ + 0.5 * dsp.highpass(mix_, 2200, 2)            # presence: the full choir opens up
        wet = verb_st(mix_, 'capilla', wet=0.75, dry=0.75, seed=75, wet_env=np.pad(wenv, (0, N(8))), decay=5.2,
                      damp=5000.0)[:n]
        y = lofi(wet, 6303, lo=90, hi=10000, drv=1.15, hiss_db=-60, wow=(0.4, 0.5), flutter=(6.0, 0.03))
        y = limit(y, 9.0)
        fade_from = t0 + span + 0.9
    return y * env_pts(n, [(0, 1), (fade_from, 1), (n / SR, 0)])[:, None]


# ====================================================================== 13. acorde_final (mono)
def handbell(midi, seed, dur=3.5, amp=1.0):
    f = 440.0 * 2 ** ((midi - 69) / 12)
    r = dsp.rng(seed)
    parts = [(1.0, 1.1, 1.0), (2.0, 2.2, 0.12), (3.0, 1.8, 0.45), (4.18, 3.5, 0.18), (5.43, 5.0, 0.12),
             (6.8, 7.0, 0.06), (8.2, 9.0, 0.04)]
    modes = []
    for ratio, d, a in parts:
        fm = f * ratio * r.uniform(0.999, 1.001)
        modes += [(fm - 0.6, d, a * 0.5), (fm + 0.6, d * 1.05, a * 0.5)]
    ir = modal_ir(modes, dur, seed)
    exc = np.zeros(N(0.002), np.float32)
    exc[:N(0.0004)] = half_sine(0.0004)
    y = signal.fftconvolve(exc, ir)[:N(dur)]
    clk = dsp.highpass(burst(0.002, seed + 1, 2.0), 4000, 2)
    y = norm(y)
    y[:len(clk)] += 0.15 * norm(clk)
    return y * amp


def acorde_final():
    dur = 5.0
    n = N(dur)
    t = taxis(n)
    swell = env_pts(n, [(0, 0.0), (0.4, 0.25), (1.0, 0.85), (1.3, 1.0), (2.6, 0.95), (3.4, 0.55), (4.2, 0.0),
                        (dur, 0)]) ** 1.2
    choir = np.zeros(n, np.float32)
    for j, m in enumerate((62, 65, 70, 74, 77, 82, 70, 74, 77)):
        nts = [(0.05, 3.6, m, 'a', '')]
        y = girl(n, nts, 7000 + 13 * j, hum=0.05, tilt=0.85, vib=0.2, breath=0.05,
                 scale=1.1 + 0.02 * (j % 5), detune=dsp.rng(7100 + j).normal(0, 5), drift=5.0, dyn=swell)
        choir += norm(y) * (0.8 if m >= 74 else 0.65)
    org = np.zeros(n, np.float32)
    for j, m in enumerate((34, 46, 53, 58, 62, 65)):
        org += fit(organ_note(m, 3.4, 7200 + j, 0.45 if m < 40 else 1.0, ped=m < 47), n)
    org = dsp.lowpass(org, 6000, 2) * swell
    # luminous shimmer: high partials slowly beating
    shim = np.zeros(n)
    for j, m in enumerate((94, 98, 101, 106)):
        f = 440.0 * 2 ** ((m - 69) / 12)
        shim += np.sin(TWO_PI * f * t + j) * (0.6 + 0.4 * np.sin(TWO_PI * (0.7 + 0.3 * j) * t))
    shim = shim * env_pts(n, [(0, 0), (0.9, 0.0), (1.6, 1.0), (3.2, 0.6), (4.4, 0.0), (dur, 0)])
    # rising light: a reverse-cymbal-like air swell into the first bell
    air = bp(white(n, 7300), 3000, 11000) * env_pts(n, [(0, 0), (0.85, 1.0), (0.95, 0.0), (dur, 0)]) ** 2
    bells = np.zeros(n, np.float32)
    for j, (tb, m, a) in enumerate(((0.9, 82, 1.0), (1.05, 86, 0.8), (1.2, 89, 0.75), (1.35, 94, 0.7),
                                    (1.9, 89, 0.4), (2.25, 94, 0.35))):
        add(bells, handbell(m, 7400 + j, 3.5, a), tb)
    choir = choir + 0.6 * dsp.highpass(choir, 2500, 2)
    mix_ = (norm(choir) * 0.75 + norm(org) * 0.38 + norm(shim) * 0.06 + norm(air) * 0.12)
    out = verb(mix_, 'capilla', wet=0.5, dry=0.8, seed=79, decay=4.0)[:n]
    bv = verb(bells, 'capilla', wet=0.45, dry=0.9, seed=81, decay=4.0)[:n]
    out = norm(out) * 0.7 + norm(bv) * 0.95
    return out * env_pts(n, [(0, 1), (4.3, 1), (dur, 0)])


# ====================================================================== event table + build
EVENTS = {  # event -> ([variant builders], peak dBFS, loop)
    'monja.campanita': ([campanita], -3.0, False),
    'monja.regla_tap': ([regla_tap], -4.0, True),
    'monja.reglazo': ([reglazo], -3.0, False),
    'monja.shh': ([shh], -1.0, False),
    'monja.burn': ([burn], -1.0, False),
    'monja.soplido': ([soplido], -3.0, False),
    'monja.ceiling': ([ceiling], -3.0, False),
    'monja.mojada': ([mojada], -1.0, False),
    'monja.scream': ([scream], -0.5, False),
    'monja.hiss': ([hiss], -1.0, False),
    'monja.whisper': ([lambda: whisper(1), lambda: whisper(2), lambda: whisper(3)], -1.0, False),
    'monja.hurt': ([hurt], -0.5, False),
    'monja.death': ([death], -0.5, False),
    'coro.ave_reves': ([ave_reves], -4.0, True),
    'coro.ave_derecho_1': ([lambda: ave_derecho(1)], -4.0, False),
    'coro.ave_derecho_2': ([lambda: ave_derecho(2)], -4.0, False),
    'coro.ave_derecho_3': ([lambda: ave_derecho(3)], -4.0, False),
    'coro.acorde_final': ([acorde_final], -0.5, False),
}


def rel_paths(name):
    n = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if n > 1 else '') for i in range(n)]


def seam_report(x):
    m = x if x.ndim == 1 else x.mean(axis=1)
    d = np.abs(np.diff(m))
    return float(abs(m[0] - m[-1]) / (np.percentile(d, 75) + 1e-9))


def rotate_to_lull(x):
    """Roll a periodic buffer so it starts at its quietest 60 ms (where master's edge fades are inaudible)."""
    m = np.abs(x if x.ndim == 1 else x.mean(axis=1))
    e = uniform_filter1d(m, N(0.06), mode='wrap')
    return np.roll(x, -int(np.argmin(e)), axis=0)


def finish(x, peak_db, loop):
    x = np.asarray(x, np.float32)
    if loop:  # exact period kept; circular high-pass so master's filter has nothing left to settle
        return dsp.master(rotate_to_lull(cfft_hp(x, 32.0)), peak_db=peak_db)
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
        for rel, fn in zip(rels, fns):
            if only and not any(o in rel or o in name for o in only):
                continue
            t0 = time.time()
            raw = fn()
            assert raw.ndim == 1 or stream, rel + ' is positional: must be mono'
            x = finish(raw, pk, loop)
            path = dsp.save_ogg(x, rel)
            # QA: Vorbis can overshoot dense, driven material by ~1 dB (death decoded at +0.3 dBFS = clipping).
            # If the decoded peak lands more than 0.3 dB over target, master again with the target lowered.
            over = 20 * np.log10(np.max(np.abs(sf.read(path, dtype='float32')[0])) + 1e-12) - pk
            if over > 0.3:
                x = finish(raw, pk - (over - 0.1), loop)
                dsp.save_ogg(x, rel)
            st = dsp.analyse(x)
            if loop:
                st['seam'] = round(seam_report(x), 2)
            report[rel] = st
            dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            print(f'{rel:26s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    sp = os.path.join(REVIEW_DIR, 'stats.json')
    old = json.load(open(sp)) if os.path.exists(sp) else {}
    old.update(report)
    with open(sp, 'w') as fh:
        json.dump(old, fh, indent=1)
    missing = [rel for name in EVENTS for rel in rel_paths(name)
               if not os.path.exists(os.path.join(dsp.OUT, rel + '.ogg'))]
    if missing:
        print('MISSING:', missing)
    print(f'nun group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
