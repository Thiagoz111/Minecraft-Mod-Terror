# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "ui": cursed phone, teleport, case sting, jumpscares, anchor, stingers.

Run from the repo root:  python3 tools/audio/snd_ui.py

In-game use (sized to it):
  phone.ring       ClientFx: forUI, retriggered every 60 ticks (3 s) while a call is pending -> UK-style
                   double ring (0.4 on / 0.2 off / 0.4 on) that has died away before the next trigger.
  phone.vibrate    CaseManager.ring(): once per incoming call, at the player, vol 0.6.
  phone.notify     PhoneItem open (vol 0.4) and shop purchase (pitch 1.3).
  phone.accept     startCase(): just before the teleport, vol 0.8.
  phone.hangup     declining a call, vol 0.6.
  phone.voice      6 caller snippets (bad line, distressed victims).
  teleport.whoosh  at the destination right after teleport (screen fades 70 ticks).
  case.solved      ClientFx CASE_END: forUI, vol 0.8 -> relief sting.
  jumpscare        ClientFx: forUI with a 26-tick (1.3 s) visual -> 1.6-1.9 s hit.
  anchor.pulse     cursed object, every 90 ticks (4.5 s), vol 1.2, pitch 0.9-1.1.
  anchor.purify    vol 3.0 (heard ~48 blocks away).
  ambient.stinger  4 short horror stingers.
"""
import os
import sys
import time

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR, n_of  # noqa: E402

REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad/audio/ui')
TWO_PI = 2 * np.pi

# ====================================================================== small helpers
_NOTE = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'F': -4, 'F#': -3, 'Gb': -3,
         'G': -2, 'G#': -1, 'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2}


def hz(name):
    return 440.0 * 2 ** ((_NOTE[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)


def secs(x):
    return len(x) / SR


def fit(x, n):
    x = np.asarray(x, np.float32)
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def norm(x, peak=1.0):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def taxis(n):
    return np.arange(n) / SR


def snoise(n, cutoff, seed):
    """Smooth random control signal in -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 4096).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[4096:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def env_ar(n, a=0.01, r=0.05, curve=1.0):
    e = np.ones(n, np.float32)
    na, nr = min(n, n_of(a)), min(n, n_of(r))
    if na:
        e[:na] = np.linspace(0, 1, na) ** curve
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def wobble(x, rate=0.5, depth_ms=1.0, seed=0, jitter_ms=0.0):
    """Variable delay -> tape wow / vocal tremor (pitch wobble)."""
    n = len(x)
    t = taxis(n)
    d = depth_ms * 1e-3 * SR * 0.5 * (1 + np.sin(TWO_PI * rate * t + seed))
    if jitter_ms:
        d = d + jitter_ms * 1e-3 * SR * 0.5 * (1 + snoise(n, 7, seed + 11))
    idx = np.arange(n)
    return np.interp(idx - d, idx, x).astype(np.float32)


def sweep_bp(x, f0, f1, q=2.0, steps=72, curve=None):
    """Time-varying band-pass (block-wise, state carried). curve: optional array of 0..1 positions."""
    n = len(x)
    out = np.zeros_like(x)
    edges = np.linspace(0, n, steps + 1).astype(int)
    pos = np.linspace(0, 1, steps) if curve is None else np.interp(np.linspace(0, 1, steps), np.linspace(0, 1, len(curve)), curve)
    fs = f0 * (f1 / f0) ** pos
    zi = np.zeros((2, 2))
    for i in range(steps):
        lo, hi = fs[i] / (1 + 0.5 / q), fs[i] * (1 + 0.5 / q)
        sos = signal.butter(2, [max(20, lo) / (SR / 2), min(0.98, hi / (SR / 2))], 'bandpass', output='sos')
        y, zi = signal.sosfilt(sos, x[edges[i]:edges[i + 1]], zi=zi)
        out[edges[i]:edges[i + 1]] = y
    return out.astype(np.float32)


VOWELS = {
    # (centre Hz, half-bandwidth Hz, gain dB)
    'scream_f': [(1050, 170, 0), (1600, 200, -2), (2950, 260, -7), (4100, 350, -12)],
    'scream_m': [(750, 140, 0), (1250, 170, -3), (2600, 230, -9), (3500, 300, -14)],
    'a': [(800, 130, 0), (1150, 150, -4), (2900, 200, -14), (3900, 250, -20)],
    'a_low': [(650, 110, 0), (1080, 140, -5), (2650, 200, -15)],
    'o': [(450, 90, 0), (800, 110, -6), (2830, 200, -20)],
    'u': [(325, 70, 0), (700, 90, -12), (2530, 170, -24)],
    'e': [(420, 90, 0), (2000, 140, -9), (2600, 180, -12)],
}


def vowel(x, name):
    out = np.zeros_like(x)
    for f, bw, g in VOWELS[name]:
        out += 10 ** (g / 20) * dsp.bandpass(x, max(30, f - bw), f + bw, 2)
    return out


def modal(freqs, amps, decays, dur, seed=0, attack=0.0015):
    """Sum of exponentially decaying sinusoids (bells, metal, membranes)."""
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    y = np.zeros(n)
    for f, a, d in zip(freqs, amps, decays):
        if 20 < f < SR / 2 - 800:
            y += a * np.sin(TWO_PI * f * t + r.uniform(0, TWO_PI)) * np.exp(-t * d)
    na = n_of(attack)
    y[:na] *= np.linspace(0, 1, na)
    return y.astype(np.float32)


def church_bell(f0, dur, seed=0, bright=1.0):
    ratios = [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.166, 5.433, 6.796]
    amps = [0.55, 0.8, 0.55, 0.35, 1.0, 0.45, 0.4, 0.3, 0.25 * bright, 0.15 * bright, 0.08 * bright]
    decays = [0.35, 0.7, 0.85, 1.2, 1.0, 1.8, 2.0, 2.5, 3.4, 4.8, 6.5]
    fr, am, de = [], [], []
    for rr, a, d in zip(ratios, amps, decays):
        for split in (-0.35, 0.35):  # doublets -> slow warble like a real bell
            fr.append(f0 * rr + split * rr)
            am.append(a * 0.5)
            de.append(d)
    x = modal(fr, am, de, dur, seed)
    strike = dsp.highpass(dsp.noise(0.03, 'white', seed), 2500, 2) * dsp.env_exp(0.03, 160) * 0.25
    return dsp.mix((x, 0, 1.0), (strike, 0, 1.0), length=dur)


def fm_bell(fc, dur, ratio=3.5, index=2.0, decay=3.5, seed=0):
    t = taxis(n_of(dur))
    ph = dsp.rng(seed).uniform(0, TWO_PI)
    idx = index * np.exp(-t * decay * 1.8) + 0.12
    y = np.sin(TWO_PI * fc * t + idx * np.sin(TWO_PI * fc * ratio * t + ph)) * np.exp(-t * decay)
    na = n_of(0.002)
    y[:na] *= np.linspace(0, 1, na)
    return y.astype(np.float32)


def piano(f0, dur, vel=1.0, seed=0, damp=None):
    """Additive piano: inharmonic partials, 3 detuned strings, two-stage decay, hammer knock."""
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    B = 0.00012 * (f0 / 110) ** 0.6 + 0.00008
    y = np.zeros(n)
    kmax = int(min(28, 14000 / f0))
    for k in range(1, kmax + 1):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        a = k ** -(1.25 - 0.45 * vel) * (abs(np.sin(np.pi * k * 0.13)) + 0.15)
        d1 = 1.0 + 0.45 * k * (f0 / 220) ** 0.5
        d2 = 0.18 + 0.04 * k * (f0 / 220) ** 0.4
        env = 0.6 * np.exp(-t * d1) + 0.4 * np.exp(-t * d2)
        for c in (-0.9, 0.0, 1.1):
            y += a / 3 * np.sin(TWO_PI * fk * 2 ** (c / 1200) * t + r.uniform(0, TWO_PI)) * env
    if damp:
        y *= np.exp(-t * damp)
    knock = dsp.lowpass(dsp.noise(0.05, 'white', seed + 1), 1800, 2) * dsp.env_exp(0.05, 90) * 0.3 * vel
    y[:len(knock)] += knock
    na = n_of(0.003)
    y[:na] *= np.linspace(0, 1, na)
    return y.astype(np.float32)


def saw_ens(f, dur, voices=3, cents=12, seed=0, vib=0.0, shape='saw'):
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    out = np.zeros(n, np.float32)
    base = np.broadcast_to(np.asarray(f, np.float64), (n,)) if np.ndim(f) == 0 else fit(f, n).astype(np.float64)
    for i in range(voices):
        c = (i - (voices - 1) / 2) * (cents / max(1, (voices - 1) / 2)) + r.normal(0, 2)
        fr = base * 2 ** (c / 1200)
        if vib:
            fr = fr * (1 + vib * np.sin(TWO_PI * (4.8 + r.random()) * t + r.uniform(0, TWO_PI)))
        out += dsp.osc(fr, n / SR, shape, phase=r.uniform(0, TWO_PI))[:n]
    return out / voices


def crackle(dur, rate=30, seed=0, lo=1500):
    n = n_of(dur)
    r = dsp.rng(seed)
    y = np.zeros(n, np.float32)
    k = r.poisson(rate * dur)
    pos = r.integers(0, n, k)
    y[pos] = r.uniform(-1, 1, k) * r.random(k) ** 2
    y = signal.lfilter([1.0], [1.0, -0.85], y).astype(np.float32)
    return dsp.highpass(y, lo, 2)


def whisperize(x, seed=0, smooth_bins=7):
    """Replace voicing with noise but keep the spectral envelope -> breathy whisper (still intelligible)."""
    _, _, Z = signal.stft(x, SR, nperseg=1024, noverlap=768)
    mag = uniform_filter1d(np.abs(Z), smooth_bins, axis=0)
    ph = dsp.rng(seed).uniform(-np.pi, np.pi, Z.shape)
    _, y = signal.istft(mag * np.exp(1j * ph), SR, nperseg=1024, noverlap=768)
    y = fit(y, len(x))
    y = dsp.highpass(y, 220, 2)
    y = dsp.peak(y, 5200, 5, 1.0)
    return norm(y, np.max(np.abs(x)))


def breath(inhale, exhale, seed=0, rasp=0.0, low=1.0, gap=0.06, gain_in=0.8):
    """One breath cycle. low < 1 lowers the noise bands (bigger creature), rasp adds vocal-fry grit."""
    a = dsp.noise(inhale, 'white', seed)
    a = dsp.bandpass(a, 700 * low, 3600 * low, 2)
    a = dsp.peak(a, 1700 * low, 8, 3) * dsp.env_points(n_of(inhale), [(0, 0), (0.55, 0.8), (0.88, 1.0), (1, 0)])
    b = dsp.noise(exhale, 'pink', seed + 1)
    b = dsp.bandpass(b, 180 * low, 2200 * low, 2)
    b = dsp.peak(b, 650 * low, 6, 2)
    nb = len(b)
    if rasp:
        fr = 42 * low * (1 + 0.15 * snoise(nb, 5, seed + 2))
        fry = np.maximum(0, dsp.osc(fr, nb / SR, 'sine')[:nb]) ** 8
        b = b * ((1 - rasp) + rasp * 3.0 * fry)
        b = b + rasp * 0.4 * vowel(dsp.osc(fr * 2, nb / SR, 'saw')[:nb] * 0.3, 'u') * np.abs(b).mean() * 8
    b = b * dsp.env_points(nb, [(0, 0), (0.12, 1.0), (0.5, 0.65), (1, 0)])
    return dsp.concat(norm(a, gain_in), dsp.silence(gap), norm(b, 1.0))


def sob(seed=0, dur=0.32, voiced=0.35):
    """Crying inhale ('hih'): breathy gasp + short voiced squeak."""
    n = n_of(dur)
    g = dsp.bandpass(dsp.noise(dur, 'white', seed), 1100, 5200, 2) * dsp.env_points(n, [(0, 0), (0.18, 1), (0.55, 0.5), (1, 0)])
    r = dsp.rng(seed)
    f = dsp.glide(r.uniform(360, 420), r.uniform(560, 680), dur)
    sq = vowel(dsp.osc(f, dur, 'saw'), 'e') * dsp.env_points(n, [(0, 0), (0.25, 0), (0.45, 1), (0.8, 0.4), (1, 0)])
    return norm(g, 1.0) * 0.8 + norm(sq, voiced)


def tts_n(text, voice, speed=0.9, peak=0.7):
    return norm(dsp.trim(dsp.tts(text, voice, speed), -50, 0.03), peak)


def bad_line(x, seed, drops=1.0, wow=0.5, hum=0.01, line_noise=0.018, crackles=10):
    """Cursed phone line: band-limit, wow, dropouts with static/garble, mains hum, crackle."""
    r = dsp.rng(seed)
    n = len(x)
    y = wobble(x, 0.6 + r.random() * 0.5, wow, seed, jitter_ms=wow * 0.7)
    y = dsp.phone_voice(y)[:n]
    g = np.ones(n, np.float32)
    extra = np.zeros(n, np.float32)
    k = r.poisson(drops * n / SR)
    for _ in range(k):
        L = n_of(r.uniform(0.04, 0.16))
        s = int(r.integers(n_of(0.25), max(n_of(0.3), n - L)))
        if s + L > n:
            continue
        g[s:s + L] *= r.uniform(0.0, 0.2)
        kind = r.integers(3)
        win = np.hanning(L).astype(np.float32)
        if kind == 0:
            extra[s:s + L] += dsp.bandpass(dsp.noise(L / SR, 'white', seed + s), 700, 5000, 2)[:L] * win * 0.35
        elif kind == 1 and s > L:
            chunk = y[s - L // 3:s]
            rep = np.tile(chunk, 4)[:L]
            extra[s:s + L] += dsp.bitcrush(rep, 4, 5)[:L] * 0.7 * win
        else:
            tones = np.repeat(r.choice([980, 1270, 1650, 2100, 2450], size=L // n_of(0.012) + 1), n_of(0.012))[:L]
            extra[s:s + L] += dsp.osc(tones, L / SR, 'square')[:L] * 0.08 * win
    g = uniform_filter1d(g, n_of(0.004))
    t = taxis(n)
    h = sum(np.sin(TWO_PI * 50 * k2 * t) / k2 for k2 in range(1, 9))
    h = dsp.bandpass(h.astype(np.float32), 120, 3400, 2) * hum
    bed = dsp.bandpass(dsp.noise(n / SR, 'pink', seed + 3), 300, 3400, 2) * line_noise
    out = y * g + extra + h + bed + crackle(n / SR, crackles, seed + 4) * 0.08
    return out.astype(np.float32)


def handset_click(seed=0, heavy=1.0):
    n = n_of(0.16)
    t = taxis(n)
    click = dsp.highpass(dsp.noise(0.16, 'white', seed), 1800, 2) * np.exp(-t * 380)
    thump = dsp.osc(150 * np.exp(-t * 5) + 60, 0.16, 'sine') * np.exp(-t * 40) * heavy
    rat = np.zeros(n, np.float32)
    for d, a in ((0.011, 0.35), (0.023, 0.2), (0.041, 0.12)):
        s = n_of(d)
        m = n_of(0.006)
        rat[s:s + m] += dsp.bandpass(dsp.noise(0.006, 'white', seed + s), 1500, 5000, 2) * a * np.hanning(m)
    return (click * 0.7 + thump * 0.6 + rat).astype(np.float32)


def scream(dur, f0=1050, seed=0, kind='scream_f', rise=1.12, fall=0.82, rough=0.5, breath_amt=0.25, vib=0.02):
    """Synthetic human scream: jittery glottal saw + subharmonic roughness + breath through scream formants."""
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    contour = dsp.env_points(n, [(0, 0.82), (0.08, rise), (0.65, rise * 1.03), (1.0, fall)])
    jit = snoise(n, 22, seed) * 0.022 + snoise(n, 4, seed + 1) * 0.035
    f = f0 * contour * (1 + jit + vib * np.sin(TWO_PI * r.uniform(5.5, 7.5) * t))
    src = dsp.osc(f, dur, 'saw') + 0.45 * dsp.osc(f * 1.004, dur, 'saw', phase=1.3)
    src = src * (1 + rough * dsp.osc(f / 2, dur, 'sine'))  # period doubling -> raw throat
    src += dsp.noise(dur, 'white', seed + 2) * breath_amt * 2.0
    y = vowel(src.astype(np.float32), kind)
    y = dsp.drive(norm(y) * 2.2, 2.4)
    amp = dsp.env_points(n, [(0, 0), (0.035, 1.0), (0.5, 0.92), (0.78, 0.7), (1, 0)]) * (1 + 0.15 * snoise(n, 12, seed + 3))
    return (y * amp).astype(np.float32)


def violin_screech(f_start, f_end, dur, seed=0, voices=4, spread=1.0, trem=13.0):
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    out = np.zeros(n, np.float32)
    for i in range(voices):
        s = 2 ** (r.uniform(-spread, spread) / 12)
        fr = dsp.glide(f_start * s, f_end * s * 2 ** (r.uniform(-0.4, 0.4) / 12), dur)
        fr = fr * (1 + 0.013 * np.sin(TWO_PI * r.uniform(5.8, 7.2) * t + r.uniform(0, 6)) + 0.008 * snoise(n, 9, seed + i))
        out += dsp.osc(fr, dur, 'saw', phase=r.uniform(0, 6))[:n]
    bow = dsp.highpass(dsp.noise(dur, 'white', seed + 9), 2500, 2) * 0.35
    x = out / voices + bow
    x = dsp.highpass(x, 700, 2)
    x = dsp.peak(dsp.peak(x, 3200, 7, 1.5), 5200, 5, 2.0)
    x = dsp.lowpass(x, 11000, 2)
    bowing = 0.55 + 0.45 * np.abs(snoise(n, trem, seed + 7))
    return (x * bowing).astype(np.float32)


def metal_ir(dur, seed=0, base=310.0, count=26, decay=1.0):
    r = dsp.rng(seed)
    freqs = [base * (k ** 1.47) * (1 + r.uniform(-0.06, 0.06)) for k in range(1, count + 1)]
    amps = [r.uniform(0.3, 1.0) / (1 + 0.08 * k) for k in range(count)]
    decays = [(0.9 + 0.12 * k) / decay for k in range(count)]
    return modal(freqs, amps, decays, dur, seed, attack=0.0005)


def choir(freq, dur, seed=0, voices=4, vname='a', vib=0.007, breath_amt=0.06):
    """Ensemble 'aah' on one note (freq may be an array for portamento)."""
    n = n_of(dur)
    t = taxis(n)
    r = dsp.rng(seed)
    base = np.broadcast_to(np.asarray(freq, np.float64), (n,)) if np.ndim(freq) == 0 else fit(freq, n).astype(np.float64)
    src = np.zeros(n, np.float32)
    for i in range(voices):
        c = r.uniform(-11, 11)
        drift = 1 + 0.003 * snoise(n, 0.7, seed * 31 + i)
        fr = base * 2 ** (c / 1200) * drift * (1 + vib * np.sin(TWO_PI * r.uniform(4.8, 6.0) * t + r.uniform(0, 6)))
        a = 0.75 + 0.25 * snoise(n, 1.5, seed * 17 + i)
        src += dsp.osc(fr, dur, 'saw', phase=r.uniform(0, 6))[:n] * a
    src = src / voices + dsp.noise(dur, 'pink', seed + 99) * breath_amt
    y = vowel(src, vname)
    return dsp.lowpass(y, 7000, 2)


# ====================================================================== phone
def phone_ring():
    """Old cursed bell phone: two slightly-detuned gongs hammered at 20 Hz, double ring + uncanny shadow."""
    total = 2.45
    n = n_of(total)
    y = np.zeros(n, np.float32)
    r = dsp.rng(101)
    ratios_a = [1.0, 2.71, 5.16, 8.43, 12.1]
    ratios_b = [1.0, 2.74, 5.21, 8.51, 12.3]
    amps = [1.0, 0.6, 0.38, 0.2, 0.09]
    decays = [4.6, 7.0, 10.0, 14.0, 19.0]
    fa, fb = 1180.0, 1180.0 * 1.0905
    strike_len = 1.6
    sl = n_of(strike_len)
    for b0 in (0.0, 0.6):
        for i in range(8):
            t0 = b0 + i / 20 + r.uniform(-0.002, 0.002)
            ff, rr = (fa, ratios_a) if i % 2 == 0 else (fb, ratios_b)
            amp = min(1.0, 0.55 + 0.16 * i) * r.uniform(0.85, 1.0)
            s = modal([ff * q for q in rr], [a * amp for a in amps], decays, strike_len, seed=int(r.integers(1e6)))
            hit = dsp.highpass(dsp.noise(0.004, 'white', int(r.integers(1e6))), 2000, 2) * 0.25 * amp
            s[:len(hit)] += hit
            st = n_of(t0)
            e = min(n, st + sl)
            y[st:e] += s[:e - st]
    y = dsp.peak(y, 2400, 4, 2)
    y = dsp.peak(y, 650, 3, 1.5)
    y = dsp.lowpass(y, 10000, 2)
    y = wobble(y, 0.45, 0.9, 3)          # slightly seasick, wrong
    shadow = dsp.lowpass(dsp.pitch_shift(y, -12), 2200, 2)
    shadow = dsp.reverb(shadow, 2.0, 0.7, 2500, seed=21)
    out = dsp.mix((y, 0, 1.0), (shadow, 0.0, 0.22))
    out = dsp.reverb(out, 0.7, 0.16, 6000, seed=5)
    out = fit(out, n) * dsp.env_points(n, [(0, 1), (0.8, 1), (1, 0)])
    return out


def phone_vibrate():
    total = 1.4
    parts = []
    for k, (start, L) in enumerate(((0.0, 0.5), (0.74, 0.5))):
        n = n_of(L)
        t = taxis(n)
        f = (112 + 58 * (1 - np.exp(-t / 0.045))) * (1 + 0.012 * snoise(n, 6, 10 + k)) * (1 - 0.02 * k)
        motor = dsp.osc(f, L, 'square') * 0.35 + dsp.osc(f, L, 'saw') * 0.4 + dsp.osc(f * 2, L, 'sine') * 0.25
        motor = dsp.lowpass(motor, 1400, 2)
        pulses = np.maximum(0, dsp.osc(f, L, 'sine')) ** 14
        rattle = dsp.bandpass(dsp.noise(L, 'white', 20 + k), 1700, 5200, 2) * pulses * 1.6
        tick = dsp.bandpass(dsp.noise(L, 'white', 30 + k), 600, 1600, 2) * pulses * 0.6
        x = motor + rattle + tick
        x = dsp.peak(x, 240, 6, 1.5)  # table resonance
        x = x * env_ar(n, 0.025, 0.06) * (0.85 + 0.15 * np.linspace(0, 1, n))
        parts.append((x.astype(np.float32), start, 1.0))
    y = dsp.mix(*parts, length=total)
    y = dsp.drive(y * 1.4, 1.6)
    return dsp.reverb(y, 0.35, 0.1, 5000, seed=4)


def phone_notify():
    e6, b5, f5 = hz('E6'), hz('B5'), hz('F5')
    n1 = dsp.mix((fm_bell(e6, 1.3, ratio=2.0, index=1.4, decay=4.0, seed=1), 0, 1.0), (fm_bell(e6 * 2.76, 0.5, 1.0, 0.3, 9, 2), 0, 0.3))
    n2 = dsp.mix((fm_bell(b5, 1.5, ratio=2.0, index=1.3, decay=3.3, seed=3), 0, 1.0), (fm_bell(b5 * 2.76, 0.5, 1.0, 0.3, 9, 4), 0, 0.25))
    ghost = fm_bell(f5, 1.4, ratio=3.5, index=0.8, decay=2.6, seed=5)  # tritone under: something is wrong
    y = dsp.mix((n1, 0, 0.8), (n2, 0.12, 0.8), (ghost, 0.12, 0.22))
    y = dsp.echo(y, 0.16, 0.25, 3, 3000)
    return dsp.reverb(y, 1.1, 0.28, 6000, seed=8)


def phone_accept():
    total = 1.15
    n = n_of(total)
    click1 = handset_click(1, 1.0)
    click2 = handset_click(2, 0.4) * 0.6
    line = dsp.bandpass(dsp.noise(total, 'pink', 3), 300, 3400, 2)
    line = line * dsp.env_points(n, [(0, 0), (0.05, 0.0), (0.12, 1.0), (0.3, 0.55), (0.85, 0.45), (1, 0)])
    line = line + crackle(total, 25, 4) * 0.25 * dsp.env_points(n, [(0, 0), (0.1, 1), (1, 0.2)])
    blips = []
    for i, f in enumerate((1400, 1850, 2450)):
        L = 0.055
        b = dsp.osc(f, L, 'sine') + 0.3 * dsp.osc(f * 1.5, L, 'square')
        b = dsp.bandpass(b, 400, 3400, 2) * env_ar(n_of(L), 0.004, 0.01)
        blips.append((b, 0.11 + i * 0.075, 0.35))
    # something exhales on the line as it opens
    br = breath(0.01, 0.55, seed=7, rasp=0.6, low=0.7, gap=0.0)
    br = dsp.phone_voice(br)
    y = dsp.mix((click1, 0, 1.0), (click2, 0.04, 1.0), (line, 0, 0.32), *blips, (br, 0.42, 0.3), length=total)
    return dsp.reverb(y, 0.3, 0.08, 5000, seed=6)


def phone_hangup():
    total = 1.45
    clunk = handset_click(11, 1.6)
    beeps = []
    for i, st in enumerate((0.24, 0.56, 0.88)):
        L = 0.19
        m = n_of(L)
        t = taxis(m)
        if i < 2:
            f = np.full(m, 425.0)
        else:
            f = 425 * np.exp(-t * 2.6)  # the last tone sags... the line dies wrong
        b = dsp.osc(f, L, 'sine') + 0.15 * dsp.osc(f * 2, L, 'sine') + 0.05 * dsp.osc(f, L, 'square')
        b = dsp.phone_voice(b * 0.6)[:m] * env_ar(m, 0.006, 0.012)
        if i == 2:
            b = dsp.bitcrush(b, 5, 6) * dsp.env_points(m, [(0, 1), (0.7, 0.9), (1, 0)])
        beeps.append((b, st, 0.85))
    hiss = dsp.bandpass(dsp.noise(total, 'pink', 12), 300, 3400, 2) * dsp.env_points(n_of(total), [(0, 0), (0.12, 0.6), (0.7, 0.5), (1, 0)])
    burst = dsp.bandpass(dsp.noise(0.18, 'white', 13), 900, 5000, 2) * dsp.env_points(n_of(0.18), [(0, 0), (0.1, 1), (1, 0)])
    y = dsp.mix((clunk, 0, 1.0), *beeps, (hiss, 0, 0.06), (burst, 1.04, 0.12), length=total)
    return dsp.reverb(y, 0.35, 0.08, 5000, seed=9)


# ---------------------------------------------------------------------- caller voices
def voice_1():
    """Woman crying: '¿Hola? ¿Me escucha? Por favor... necesito ayuda.'"""
    p = [tts_n('¿Hola?', 'ef_dora', 0.9), tts_n('¿Me escucha?', 'ef_dora', 0.9), tts_n('Por favor... necesito ayuda.', 'ef_dora', 0.8)]
    p = [dsp.tremolo(wobble(dsp.pitch_shift(x, 1.0), 6.5, 0.5, 40 + i, 0.35), 7.0, 0.35) for i, x in enumerate(p)]
    sq = dsp.osc(dsp.glide(560, 410, 0.6), 0.6, 'saw')
    whimper = vowel(sq, 'u') * dsp.env_points(n_of(0.6), [(0, 0), (0.2, 1), (1, 0)])
    seq = dsp.concat(sob(1, 0.3), p[0], dsp.silence(0.18), sob(2, 0.26), p[1], dsp.silence(0.12),
                     sob(3, 0.22), sob(4, 0.3), p[2], norm(whimper, 0.25), dsp.silence(0.2))
    return bad_line(seq, 51, drops=0.6, wow=0.5)


def voice_2():
    """Man whispering, hiding: 'Está adentro de la casa... la escucho respirar. Por favor, vengan rápido.'"""
    p = [tts_n('Está adentro de la casa...', 'em_santa', 0.85), tts_n('La escucho respirar.', 'em_santa', 0.85),
         tts_n('Por favor... vengan rápido.', 'em_santa', 0.9)]
    w = [norm(whisperize(x, 60 + i) + 0.14 * dsp.lowpass(x, 900, 2), 0.7) for i, x in enumerate(p)]
    w = [dsp.peak(x, 180, 5, 1.0) for x in w]  # mouth glued to the mic
    inh = [breath(0.28, 0.01, 70 + i, gap=0.0, gain_in=0.5) for i in range(3)]
    seq = dsp.concat(inh[0], w[0], dsp.silence(0.35), inh[1], w[1], dsp.silence(0.3), inh[2], w[2], dsp.silence(0.25))
    return bad_line(seq, 52, drops=1.0, wow=0.6, line_noise=0.03)


def voice_3():
    """Little girl (Lucía) with something huge breathing behind her: '¿Hola? No me dejan salir... Vení a jugar conmigo.'"""
    p = [tts_n('¿Hola?', 'ef_dora', 0.95), tts_n('No me dejan salir...', 'ef_dora', 0.88), tts_n('Vení a jugar conmigo.', 'ef_dora', 0.85)]
    kid = [dsp.lowpass(dsp.pitch_shift(x, 4.0), 7500, 2) for x in p]
    seq = dsp.concat(dsp.silence(0.35), kid[0], dsp.silence(0.5), kid[1], dsp.silence(0.55), kid[2], dsp.silence(0.6))
    n = len(seq)
    # demon doubling creeping into the last words
    last = p[2]
    dem = dsp.demonic(last, semis=-9, layers=(-12, 0), wet=0.3)
    dem_start = secs(seq) - secs(kid[2]) - 0.6 + secs(kid[2]) * 0.45
    dem = fit(dem[n_of(secs(last) * 0.45):], n_of(secs(last) * 0.6 + 0.6))
    dem *= dsp.env_points(len(dem), [(0, 0), (0.3, 1), (0.85, 0.8), (1, 0)])
    # heavy, wet breathing right behind the receiver
    breaths = dsp.concat(breath(1.1, 1.3, 81, rasp=0.7, low=0.55, gain_in=0.7), dsp.silence(0.25),
                         breath(1.0, 1.4, 82, rasp=0.8, low=0.5, gain_in=0.7))
    breaths = dsp.reverb(breaths, 0.6, 0.2, 3000, seed=83)
    full = dsp.mix((seq, 0, 1.0), (breaths, 0.05, 0.32), (dem, dem_start, 0.42), length=secs(seq))
    return bad_line(full, 53, drops=0.5, wow=0.7)


def voice_4():
    """Man running, panicking, call cut: '¡Ayuda! ¡Algo me está siguiendo! ...¡Está entre los árboles! ¡No, no, no!'"""
    p = [tts_n('¡Ayuda! ¡Algo me está siguiendo!', 'em_alex', 1.12), tts_n('¡Está entre los árboles!', 'em_alex', 1.15),
         tts_n('¡No, no, no!', 'em_alex', 1.2)]
    p = [wobble(dsp.pitch_shift(x, 1.5), 7.5, 0.4, 90 + i, 0.4) for i, x in enumerate(p)]
    pant = lambda s: dsp.concat(*[breath(0.14, 0.16, s + j, gap=0.02, gain_in=0.9) for j in range(3)])  # noqa: E731
    seq = dsp.concat(pant(100), p[0], pant(110), p[1], pant(120), p[2])
    n = len(seq)
    # running footsteps crunching under it
    steps = np.zeros(n, np.float32)
    for k in range(int(secs(seq) * 2.9)):
        st = n_of(k / 2.9 + 0.05)
        L = n_of(0.09)
        if st + L < n:
            steps[st:st + L] += dsp.lowpass(dsp.noise(0.09, 'brown', 130 + k), 900, 2) * dsp.env_exp(0.09, 40)
    full = bad_line(seq + steps * 0.35, 54, drops=2.0, wow=0.8)
    # the call is ripped away: garbled static burst then dead line
    cut = dsp.bitcrush(dsp.bandpass(dsp.noise(0.35, 'white', 140), 500, 6000, 2), 4, 8)
    cut *= dsp.env_points(n_of(0.35), [(0, 1), (0.8, 0.8), (1, 0)])
    return dsp.concat(full, norm(cut, 0.6), dsp.silence(0.15))


def voice_5():
    """Young woman by the river, trembling whisper-cry, a far wail behind: 'Hay una mujer de blanco en el río...'"""
    p = [tts_n('Hay una mujer de blanco en el río...', 'ef_dora', 0.82), tts_n('Está llorando...', 'ef_dora', 0.8),
         tts_n('...y me está mirando.', 'ef_dora', 0.78)]
    p = [norm(0.75 * whisperize(x, 150 + i) + 0.7 * wobble(x, 5.2, 0.55, 150 + i, 0.4), 0.7) for i, x in enumerate(p)]
    p = [dsp.tremolo(x, 6.0, 0.3) for x in p]
    sniff = lambda s: norm(dsp.bandpass(dsp.noise(0.18, 'white', s), 2000, 7000, 2) * dsp.env_points(n_of(0.18), [(0, 0), (0.3, 1), (1, 0)]), 0.35)  # noqa: E731
    seq = dsp.concat(sniff(160), dsp.silence(0.1), p[0], dsp.silence(0.4), sob(161, 0.28), p[1], dsp.silence(0.45),
                     sniff(162), p[2], dsp.silence(0.5))
    # La Llorona wailing far away on the water
    L = 2.4
    f = 560 * dsp.env_points(n_of(L), [(0, 0.92), (0.2, 1.05), (0.7, 0.97), (1, 0.7)]) * (1 + 0.025 * np.sin(TWO_PI * 5 * dsp.t_axis(L)))
    wail = vowel(dsp.osc(f, L, 'saw') + 0.3 * dsp.noise(L, 'white', 170), 'a') * dsp.env_points(n_of(L), [(0, 0), (0.2, 1), (0.7, 0.8), (1, 0)])
    wail = dsp.reverb(dsp.lowpass(wail, 2500, 2), 3.0, 0.75, 2000, seed=171)
    full = dsp.mix((seq, 0, 1.0), (norm(wail, 0.12), secs(seq) * 0.42, 1.0), length=secs(seq))
    return bad_line(full, 55, drops=0.7, wow=0.5, line_noise=0.03)


def voice_6():
    """Lost hunter... or something mimicking him: '¿Hola? ¡Ayuda! Estoy perdido en el bosque... ¿hola? ¿hola? ¿HOLA?'"""
    a = tts_n('¿Hola? ¡Ayuda! Estoy perdido en el bosque.', 'em_alex', 1.0)
    h = tts_n('¿Hola?', 'em_alex', 1.0)
    h1 = h.copy()
    h2 = dsp.pitch_shift(dsp.time_stretch(h, 0.8), -3)
    # third one: stuttered and wrong - the mimic slips
    seg = h[:n_of(0.12)]
    stut = dsp.concat(seg, seg, seg * 0.8)
    h3 = dsp.concat(stut, dsp.time_stretch(h, 0.55))
    h3 = dsp.demonic(h3, semis=-6, layers=(-12, 0), wet=0.35)
    h3 = norm(dsp.mix((h3, 0, 1.0), (dsp.pitch_shift(h3, 7) if False else h3 * 0, 0, 0)), 0.85)
    seq = dsp.concat(a, dsp.silence(0.7), h1, dsp.silence(0.75), norm(h2, 0.65), dsp.silence(0.65), h3, dsp.silence(0.3))
    return bad_line(seq, 56, drops=0.8, wow=0.7)


# ====================================================================== teleport
def teleport_whoosh():
    total = 3.6
    n = n_of(total)
    r = dsp.rng(200)
    arrive = 1.62
    na = n_of(arrive)
    # A: noise riser sucked up through the line
    a = sweep_bp(dsp.noise(arrive, 'pink', 201), 280, 7500, q=1.6, steps=80)
    a *= dsp.env_points(na, [(0, 0.15), (0.1, 0.35), (0.85, 1.0), (1, 0.9)])
    # B: tonal riser (two saws, octave apart) with opening filter
    f = dsp.glide(95, 1500, arrive)
    b = saw_ens(f, arrive, 3, 18, 202) + 0.5 * saw_ens(f * 1.5, arrive, 2, 22, 203)
    b = dsp.sweep_lowpass(b, 300, 7000) * dsp.env_points(na, [(0, 0), (0.3, 0.25), (1, 1.0)])
    # C: FSK data chirps, gated in stutters
    seglen = n_of(0.016)
    tones = np.repeat(r.choice([1070, 1270, 1650, 2025, 2225, 2600, 3100], size=na // seglen + 1), seglen)[:na]
    c = dsp.osc(tones.astype(np.float64), arrive, 'square')[:na]
    gate = np.repeat((r.random(na // n_of(0.03) + 1) > 0.35).astype(np.float32), n_of(0.03))[:na]
    c = dsp.bandpass(dsp.bitcrush(c * gate, 6, 3), 400, 3800, 2) * dsp.env_points(na, [(0, 0.2), (0.5, 0.6), (1, 0.9)])
    # D: glitch static stutters (repeated buffers)
    d = np.zeros(na, np.float32)
    st_noise = dsp.noise(arrive, 'white', 204)
    for _ in range(9):
        s = int(r.integers(n_of(0.05), na - n_of(0.3)))
        L = n_of(r.uniform(0.02, 0.05))
        reps = int(r.integers(3, 7))
        chunk = dsp.bitcrush(st_noise[s:s + L] * (0.5 + r.random()), 4, int(r.integers(2, 9)))
        blk = np.tile(chunk, reps)
        e = min(na, s + len(blk))
        d[s:e] += blk[:e - s]
    # E: arrival impact + reverse-reverb suck into it
    imp_n = dsp.lowpass(dsp.noise(0.5, 'white', 205), 5000, 2) * dsp.env_exp(0.5, 14)
    sub = dsp.osc(dsp.glide(130, 28, 1.6), 1.6, 'sine') * dsp.env_exp(1.6, 2.6)
    impact = dsp.mix((imp_n, 0, 0.7), (dsp.drive(sub * 1.8, 1.8), 0, 1.0))
    suck = dsp.reverse(dsp.reverb(imp_n, 1.0, 1.0, 4000, seed=206))[-n_of(0.45):]
    # F: settling static / downward whoosh
    tail_len = total - arrive
    nt = n_of(tail_len)
    ftail = sweep_bp(dsp.noise(tail_len, 'white', 207), 6000, 180, q=1.4, steps=60)
    ftail *= dsp.env_points(nt, [(0, 1), (0.25, 0.5), (1, 0)])
    cr = crackle(tail_len, 60, 208, 1200) * dsp.env_points(nt, [(0, 1), (1, 0)])
    hum = dsp.osc(55, tail_len, 'saw')
    hum = dsp.lowpass(hum, 400, 2) * dsp.env_points(nt, [(0, 0.6), (0.6, 0.2), (1, 0)])
    y = dsp.mix((norm(a), 0, 0.55), (norm(b), 0, 0.32), (norm(c), 0, 0.22), (norm(d), 0, 0.3),
                (suck, arrive - 0.45, 0.6), (norm(impact), arrive, 1.0),
                (norm(ftail), arrive, 0.45), (norm(cr), arrive, 0.25), (hum, arrive, 0.18), length=total)
    y = dsp.drive(y * 1.2, 1.4)
    return fit(dsp.reverb(y, 1.4, 0.2, 5000, seed=209), n)


# ====================================================================== case solved
def case_solved():
    total = 5.6
    n = n_of(total)
    res = 1.15
    t = taxis(n)

    def traj(a, b):
        k = 1 / (1 + np.exp(-(t - res) / 0.035))
        return a * (1 - k) + b * k

    notes = [hz('D3'), hz('A3'), hz('D4'), traj(hz('G4'), hz('F#4')), hz('A4')]
    body = np.zeros(n, np.float32)
    for i, f in enumerate(notes):
        vn = 'a_low' if i < 2 else 'a'
        body += choir(f, total, seed=300 + i, voices=4, vname=vn)
    top = choir(hz('D5'), total, seed=310, voices=3, vname='a') * dsp.env_points(n, [(0, 0), (res / total, 0), ((res + 0.5) / total, 1), (1, 1)])
    strings = sum(saw_ens(f, total, 3, 9, 320 + i, vib=0.004) for i, f in enumerate([hz('D2'), hz('A2'), hz('D3'), hz('F#3')]))
    strings = dsp.lowpass(strings, 1500, 2) * dsp.env_points(n, [(0, 0), (res / total, 0.2), ((res + 0.6) / total, 1), (1, 1)])
    pad = (norm(body) + 0.45 * norm(top) + 0.35 * norm(strings)) * dsp.env_points(n, [(0, 0), (0.07, 0.75), (res / total, 0.82), ((res + 0.3) / total, 1.0), (0.58, 0.9), (1, 0)])
    bell = church_bell(hz('D5'), 4.3, 330)
    sparkle = [(fm_bell(hz(nm), 1.6, 3.5, 1.2, 3.2, 340 + i), res + 0.12 + i * 0.14, 0.18) for i, nm in enumerate(('D6', 'F#6', 'A6', 'D7'))]
    sub = dsp.osc(hz('D2'), total - res, 'sine') * dsp.env_points(n_of(total - res), [(0, 0), (0.1, 1), (0.6, 0.6), (1, 0)])
    y = dsp.mix((norm(pad), 0, 0.75), (norm(bell), res, 0.5), *sparkle, (sub, res, 0.25), length=total)
    return dsp.reverb(y, 3.2, 0.33, 5500, seed=350)


# ====================================================================== jumpscares
def jumpscare(v):
    total = 1.75 if v == 1 else 1.9
    n = n_of(total)
    seed = 400 + v * 50
    imp = dsp.drive(dsp.lowpass(dsp.noise(0.3, 'white', seed), 9000, 2) * dsp.env_exp(0.3, 20) * 3, 2.5)
    kick = dsp.osc(dsp.glide(160, 40, 0.45), 0.45, 'sine') * dsp.env_exp(0.45, 8)
    if v == 1:
        names = ['C2', 'C#2', 'G2', 'C3', 'F#3', 'G3', 'C#4', 'G4', 'C5', 'C#5', 'F#5', 'G6']
    else:
        names = ['A1', 'Bb1', 'E2', 'A2', 'Eb3', 'E3', 'Bb3', 'Eb4', 'A4', 'Bb4', 'E5', 'Bb5', 'Eb6']
    stab = sum(saw_ens(hz(nm), total, 3, 16, seed + i) for i, nm in enumerate(names)) / len(names)
    stab = dsp.sweep_lowpass(stab, 9000, 900, 64)
    stab = dsp.drive(norm(stab) * 3.0, 3.0)
    stab *= dsp.env_points(n, [(0, 0), (0.004, 1), (0.12, 0.8), (0.55, 0.45), (1, 0)])
    screech = violin_screech(2600 if v == 1 else 3100, 3500 if v == 1 else 2300, total, seed + 5, 5, 1.2, 16)
    screech *= dsp.env_points(n, [(0, 0), (0.01, 1), (0.6, 0.6), (1, 0)])
    sub = dsp.osc(dsp.glide(100, 26, total), total, 'sine') * dsp.env_points(n, [(0, 0), (0.01, 1), (0.7, 0.7), (1, 0)])
    sub = sub + 0.35 * dsp.lowpass(dsp.drive(sub * 3, 3), 300, 2)
    if v == 1:
        scr = scream(1.35, 1180, seed + 7, 'scream_f', rise=1.15, fall=0.78, rough=0.55, breath_amt=0.3)
        scr2 = scream(1.25, 1590, seed + 8, 'scream_f', rise=1.08, fall=0.7, rough=0.35, breath_amt=0.35)
        voice = dsp.mix((norm(scr), 0, 1.0), (norm(scr2), 0.02, 0.45))
        metal = np.zeros(1, np.float32)
    else:
        scr = scream(1.5, 620, seed + 7, 'scream_m', rise=1.2, fall=0.7, rough=0.8, breath_amt=0.35)
        scr2 = scream(1.4, 1350, seed + 8, 'scream_f', rise=1.1, fall=0.75, rough=0.5, breath_amt=0.3)
        roar = dsp.lowpass(dsp.pitch_shift(scr, -12), 1800, 2)
        voice = dsp.mix((norm(scr), 0, 1.0), (norm(scr2), 0.03, 0.6), (norm(roar), 0, 0.7))
        metal = metal_ir(1.6, seed + 9, 420, 30, 0.8)
        metal = dsp.highpass(metal, 900, 2)
    y = dsp.mix((imp, 0, 0.6), (kick, 0, 0.7), (norm(stab), 0, 0.75), (norm(screech), 0.0, 0.32),
                (norm(voice), 0.03, 0.75), (norm(sub), 0, 0.7), (norm(metal), 0, 0.3), length=total)
    y = dsp.drive(y * 1.6, 1.8)
    y = dsp.reverb(y, 1.6, 0.22, 6000, seed=seed + 10)
    return fit(y, n_of(total + 0.35)) * dsp.env_points(n_of(total + 0.35), [(0, 1), (0.85, 1), (1, 0)])


# ====================================================================== anchor
def anchor_pulse():
    total = 2.5
    n = n_of(total)

    def thump(f0, seed, L=0.7):
        m = n_of(L)
        t = taxis(m)
        f = f0 * (0.72 + 0.9 * np.exp(-t * 16))
        body = dsp.osc(f, L, 'sine') * np.exp(-t * 6.5)
        click = dsp.lowpass(dsp.noise(L, 'white', seed), 700, 2) * np.exp(-t * 55) * 0.5
        x = dsp.drive((body + click) * 2.2, 2.2)
        return dsp.peak(x, 115, 6, 1.2)

    lub = thump(56, 501)
    dub = thump(50, 502) * 0.78
    pre = dsp.reverse(dsp.reverb(lub, 0.9, 1.0, 1200, seed=503))[-n_of(0.35):] * 0.35
    drone = saw_ens(41.2, total, 3, 20, 504) + 0.5 * dsp.osc(58.3, total, 'sine')
    drone = dsp.lowpass(drone, 240, 2)
    dr_env = dsp.env_points(n, [(0, 0.15), (0.06, 0.15), (0.16, 0.9), (0.26, 0.55), (0.36, 0.8), (0.75, 0.25), (1, 0)])
    growl_src = dsp.noise(total, 'pink', 505)
    fry = np.maximum(0, dsp.osc(31 * (1 + 0.1 * snoise(n, 3, 506)), total, 'sine')) ** 10
    growl = dsp.bandpass(growl_src * fry, 90, 700, 2) * dsp.env_points(n, [(0, 0), (0.15, 0.6), (0.5, 0.4), (1, 0)])
    y = dsp.mix((pre, 0.0, 1.0), (lub, 0.32, 1.0), (dub, 0.6, 1.0), (drone * dr_env, 0, 0.45), (norm(growl), 0, 0.18), length=total)
    return dsp.reverb(y, 1.9, 0.28, 1600, seed=507)


def anchor_purify():
    total = 4.6
    n = n_of(total)
    # holy flash: bright bells + air burst
    flash = dsp.highpass(dsp.noise(0.9, 'white', 601), 3500, 2) * dsp.env_exp(0.9, 6)
    bells = dsp.mix((church_bell(hz('E5'), 4.0, 602, 1.3), 0, 1.0), (fm_bell(hz('B6'), 2.5, 3.5, 1.6, 2.2, 603), 0, 0.6),
                    (fm_bell(hz('E7'), 2.0, 3.5, 1.2, 2.8, 604), 0, 0.45), (fm_bell(hz('G#6'), 2.5, 3.5, 1.3, 2.4, 605), 0, 0.5))
    # choir swells in (E major)
    ch = sum(choir(hz(nm), total, 610 + i, 4, 'a' if i > 1 else 'a_low') for i, nm in enumerate(('E3', 'B3', 'E4', 'G#4', 'B4', 'E5')))
    ch = norm(ch) * dsp.env_points(n, [(0, 0), (0.06, 0.25), (0.3, 1.0), (0.62, 0.9), (1, 0)])
    # evil leaving: hiss / sizzle + growl descending + upward whoosh
    sz_len = 2.6
    nz = n_of(sz_len)
    sizzle = dsp.bandpass(dsp.noise(sz_len, 'white', 620), 2500, 9500, 2) * (0.4 + 0.6 * np.abs(snoise(nz, 40, 621)))
    sizzle = sizzle + crackle(sz_len, 220, 622, 2000) * 2.5
    sizzle *= dsp.env_points(nz, [(0, 0), (0.02, 1), (0.3, 0.7), (1, 0)])
    gl = 2.2
    ng = n_of(gl)
    fg = dsp.glide(78, 30, gl) * (1 + 0.08 * snoise(ng, 18, 623))
    growl = dsp.osc(fg, gl, 'saw') * (1 + 0.6 * dsp.osc(fg / 2, gl, 'sine')) + 0.7 * dsp.noise(gl, 'pink', 624)
    growl = vowel(growl, 'o') + 0.4 * dsp.lowpass(growl, 250, 2)
    growl = dsp.drive(norm(growl) * 2, 2) * dsp.env_points(ng, [(0, 0), (0.05, 1), (0.4, 0.7), (1, 0)])
    growl = dsp.reverb(growl, 1.6, 0.35, 2500, seed=625)
    whoosh = sweep_bp(dsp.noise(1.8, 'pink', 626), 300, 7000, q=1.5, steps=60) * dsp.env_points(n_of(1.8), [(0, 0), (0.7, 1), (1, 0)])
    # shimmer sparkles
    r = dsp.rng(630)
    sp = np.zeros(n, np.float32)
    for _ in range(140):
        tt = 0.1 + (r.random() ** 1.6) * 3.6
        f = r.uniform(2500, 9000)
        L = 0.35
        ping = dsp.osc(f, L, 'sine') * dsp.env_exp(L, r.uniform(10, 18)) * r.uniform(0.3, 1.0)
        s = n_of(tt)
        e = min(n, s + len(ping))
        sp[s:e] += ping[:e - s]
    y = dsp.mix((flash, 0, 0.35), (norm(bells), 0, 0.55), (ch, 0.05, 0.5), (norm(sizzle), 0, 0.42),
                (norm(growl), 0.03, 0.55), (norm(whoosh), 0.2, 0.3), (norm(sp), 0, 0.22), length=total)
    return dsp.reverb(y, 3.0, 0.32, 6500, seed=640)


# ====================================================================== stingers
def stinger_piano():
    """Reversed dissonant piano swell sucking into a dry low hit."""
    names = [('A1', 1.0), ('E2', 0.9), ('Bb2', 0.9), ('F3', 0.7), ('B3', 0.7), ('C5', 0.45), ('F#5', 0.35)]
    ch = sum(piano(hz(nm), 4.5, v, 700 + i) for i, (nm, v) in enumerate(names))
    wet = dsp.reverb(ch, 3.5, 0.6, 4000, seed=710)
    rev = dsp.reverse(wet)
    rev = rev[-n_of(2.4):]
    rev *= np.linspace(0.3, 1.0, len(rev)) ** 1.5
    hit = (piano(hz('A0'), 2.0, 1.0, 720) + piano(hz('Bb1'), 2.0, 1.0, 721) + 0.7 * piano(hz('A1'), 2.0, 1.0, 722)
           + 0.5 * piano(hz('Eb6'), 2.0, 1.0, 723)) * dsp.env_exp(2.0, 1.4)
    hit = dsp.drive(norm(hit) * 1.5, 1.5)
    hit = dsp.reverb(hit, 2.2, 0.3, 3500, seed=724)
    sub = dsp.osc(dsp.glide(38, 45, 2.4), 2.4, 'sine') * np.linspace(0, 1, n_of(2.4)) ** 2
    swell = dsp.mix((norm(rev), 0, 1.0), (sub, 0, 0.35))
    return dsp.concat(norm(swell, 0.85), norm(hit, 1.0))


def stinger_strings():
    """High violin cluster screech (sul ponticello) + low cello grind, cut into reverb."""
    L = 1.7
    v = violin_screech(1750, 2650, L, 801, 6, 0.9, 12)
    v *= dsp.env_points(n_of(L), [(0, 0), (0.35, 0.7), (0.9, 1.0), (1, 0)])
    cello = saw_ens(hz('C2'), L, 3, 25, 802, vib=0.01) + saw_ens(hz('C#2'), L, 3, 25, 803, vib=0.01)
    cello = dsp.lowpass(dsp.drive(cello * 2, 2), 1600, 2) * dsp.env_points(n_of(L), [(0, 0), (0.5, 0.6), (0.95, 1), (1, 0)])
    stab = dsp.drive(norm(violin_screech(3100, 2900, 0.35, 804, 4, 0.6, 18)) * 2, 2) * dsp.env_exp(0.35, 7)
    y = dsp.mix((norm(v), 0, 0.75), (norm(cello), 0, 0.4), (norm(stab), L - 0.02, 0.7))
    return dsp.reverb(y, 2.4, 0.33, 5000, seed=805)


def stinger_metal():
    """A blade dragged along rusted metal, squeal rising, ending in a clang."""
    L = 2.1
    n = n_of(L)
    t = taxis(n)
    rate = dsp.glide(38, 120, L) * (1 + 0.25 * snoise(n, 6, 901))
    stick = np.maximum(0, dsp.osc(rate, L, 'saw')) ** 6
    exc = dsp.noise(L, 'white', 902) * (0.25 + stick * 1.5) * dsp.env_points(n, [(0, 0), (0.15, 0.5), (0.95, 1.0), (1, 0)])
    ir = metal_ir(1.2, 903, 330, 28, 1.2)
    scr = signal.fftconvolve(exc, ir)[:n + len(ir)].astype(np.float32)
    scr = dsp.highpass(scr, 200, 2)
    sq_f = 2870 * (1 + 0.012 * np.sin(TWO_PI * 6 * t)) * dsp.env_points(n, [(0, 1), (1, 1.06)])
    squeal = dsp.osc(sq_f, L, 'sine') + 0.3 * dsp.osc(sq_f * 2.01, L, 'sine')
    squeal *= dsp.env_points(n, [(0, 0), (0.35, 0), (0.7, 0.8), (0.97, 1), (1, 0)]) * (0.7 + 0.3 * snoise(n, 15, 904))
    clang = metal_ir(2.5, 905, 210, 30, 0.9)
    clang += 0.6 * dsp.osc(dsp.glide(90, 45, 2.5), 2.5, 'sine') * dsp.env_exp(2.5, 3)
    y = dsp.mix((norm(scr), 0, 0.8), (norm(squeal), 0, 0.22), (norm(clang), L - 0.03, 0.9))
    return dsp.reverb(y, 2.6, 0.3, 4500, seed=906)


def stinger_whisper():
    """Whispers swarm closer and closer, then a sharp inhale right in your ear."""
    lines = [('ya viene', 'em_alex', 0.9, 0.0), ('está detrás tuyo', 'ef_dora', 0.9, 2.0), ('no mires', 'ef_dora', 0.85, -2.0),
             ('te está mirando', 'em_santa', 0.85, 0.0), ('ya viene', 'ef_dora', 1.0, 3.0)]
    L = 2.5
    n = n_of(L)
    r = dsp.rng(1000)
    layers = []
    for i, (txt, vc, sp, semi) in enumerate(lines):
        x = tts_n(txt, vc, sp)
        if semi:
            x = dsp.pitch_shift(x, semi)
        w = whisperize(x, 1001 + i)
        if i in (1, 3):
            w = dsp.reverse(dsp.reverb(w, 1.5, 0.6, 5000, seed=1010 + i))  # reversed whispers swirl in
        start = 0.05 + i * 0.36 + r.uniform(-0.08, 0.08)
        layers.append((norm(w), start, 0.4 + 0.15 * i))
    cloud = dsp.granular(norm(whisperize(tts_n('está detrás tuyo', 'ef_dora', 0.9), 1020)), L, 0.09, 70, 1.0, 1.5, 1021)
    cloud *= np.linspace(0, 1, len(cloud)) ** 2
    y = dsp.mix(*layers, (norm(cloud), 0, 0.5), length=L)
    y *= dsp.env_points(n, [(0, 0.2), (0.5, 0.45), (0.92, 1.0), (1, 0.9)])
    drone = dsp.osc(dsp.glide(55, 74, L), L, 'sine') * np.linspace(0, 1, n) ** 2 * 0.3
    gasp = breath(0.32, 0.01, 1030, gap=0.0, gain_in=1.0)
    y = dsp.mix((norm(y), 0, 0.85), (drone, 0, 1.0), (dsp.highpass(gasp, 900, 2), L - 0.3, 0.9))
    return dsp.reverb(y, 1.6, 0.25, 6000, seed=1040)


# ====================================================================== build
EVENTS = [
    ('phone/ring', phone_ring, -2.0),
    ('phone/vibrate', phone_vibrate, -3.0),
    ('phone/notify', phone_notify, -3.0),
    ('phone/accept', phone_accept, -3.0),
    ('phone/hangup', phone_hangup, -3.0),
    ('phone/voice_1', voice_1, -1.0),
    ('phone/voice_2', voice_2, -1.0),
    ('phone/voice_3', voice_3, -1.0),
    ('phone/voice_4', voice_4, -1.0),
    ('phone/voice_5', voice_5, -1.0),
    ('phone/voice_6', voice_6, -1.0),
    ('teleport/whoosh', teleport_whoosh, -1.0),
    ('case/solved', case_solved, -2.0),
    ('jumpscare_1', lambda: jumpscare(1), -0.5),
    ('jumpscare_2', lambda: jumpscare(2), -0.5),
    ('anchor/purify', anchor_purify, -1.0),
    ('anchor/pulse', anchor_pulse, -1.0),
    ('ambient/stinger_1', stinger_piano, -1.0),
    ('ambient/stinger_2', stinger_strings, -1.0),
    ('ambient/stinger_3', stinger_metal, -1.0),
    ('ambient/stinger_4', stinger_whisper, -1.0),
]


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    for rel, fn, pk in EVENTS:
        if only and not any(o in rel for o in only):
            continue
        t0 = time.time()
        x = np.asarray(fn(), np.float32)
        assert x.ndim == 1, rel + ' must be mono'
        x = dsp.trim(x, -62, 0.08)
        x = dsp.master(x, peak_db=pk)
        dsp.save_ogg(x, rel)
        st = dsp.analyse(x)
        dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
        print(f'{rel:22s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    print(f'ui group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
