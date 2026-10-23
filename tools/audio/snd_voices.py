# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "voices": every voiced line of tools/audio/lines.py, turned into characters.

Run from the repo root:  python3 tools/audio/snd_voices.py [substring ...]

Writes   assets/deadline/sounds/line/<id with dots -> slashes>.ogg   (event 'line.<id>', always MONO)
         data/deadline/lines.json = {id: length_in_ticks}            (the case director waits that long)

Character presets (lines.py 'voice' field):
  madre      Madre Remedios. ef_dora at speed 0.8, -3 st by TD-PSOLA (formants kept, -0.7 st older tract),
             old-voice jitter/shimmer/tremor and a breath of rasp, gated + compressed (clipped, stern), small dry
             classroom. fx 'pa' = 1980s school loudspeaker (300-3500 Hz horn, cone grit, 50 Hz hum, slapback down a
             long corridor); fx 'head' = dry, close, inside your skull.
  clara      Hermana Clara. ef_dora 0.95, whispered (spectral-envelope noise) over a thin trembling voice, quick
             scared inhales in the pauses; fx 'phone' = dsp.phone_voice. fx 'room' = freed Clara: calm, warm chapel.
  clara84    Clara's 1984 answering-machine tape: phrase by phrase with crying breaths between them, microcassette
             band, hiss, wow/flutter, dropouts, then the phone line.
  cura       em_santa 0.8, old warm man (tremor, jitter), inside a wooden confessional (1 m box: dense 1-7 ms
             reflections, 170/340 Hz modes, lattice-grille low-pass) with the chapel faintly beyond.
  alumna     ef_dora +4 st (+2 st formants: a child's tract), band 400-6000, slow pitch wobble, long cold reverb,
             whispered where the text says (susurro). 'Shhh' is synthesised (Kokoro spells it out).
  paloma     the same girl closer, clearer, less reverb.
  coro       7 girl takes (different speeds, formant sizes, +-20 cent detune, 10-40 ms offsets) + chapel reverb.
  monja      Sor Agonia: ef_dora -5 st layered with em_santa -9 st (DTW-aligned to her words), growl + grit;
             fx 'head' = whispered right behind your ear.
  operadora  ef_dora bright and smiling, IVR compression, telephone band and tiny codec glitches.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import json
import math
import os
import re
import sys
import time

import numpy as np
from scipy import signal
from scipy.fft import dct
from scipy.ndimage import median_filter, minimum_filter1d, uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR, n_of  # noqa: E402
from lines import LINES  # noqa: E402

REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    _os.path.join(WORK, 'audio/colegio_voices'))
CASA_REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    _os.path.join(WORK, 'audio/casa_voices'))
LINES_JSON = os.path.join(dsp.ROOT, 'src/main/resources/data/deadline/lines.json')


def is_casa(lid):
    """Case 2 lines: casa.* and the switchboard's warning for that case."""
    return lid.startswith('casa.') or lid == 'operadora.casa_aviso'
TWO_PI = 2 * np.pi
PEAK_DB = -1.0


# ====================================================================== small helpers
def fit(x, n):
    x = np.asarray(x, np.float32)
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def norm(x, peak=1.0):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def taxis(n):
    return np.arange(n) / SR


def snoise(n, cutoff, seed):
    """Smooth random control signal in -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 8192).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def rms_env(x, win=0.02):
    return np.sqrt(uniform_filter1d(np.asarray(x, np.float64) ** 2, max(1, n_of(win))) + 1e-12).astype(np.float32)


def match_env(y, ref, win=0.02, lo=0.05, hi=8.0):
    """Give y the short-time loudness contour of ref (same timeline)."""
    n = min(len(y), len(ref))
    ey, er = rms_env(y[:n], win), rms_env(ref[:n], win)
    floor = 1e-3 * max(np.max(er), 1e-6)
    g = np.clip((er + floor) / (ey + floor), lo, hi)
    g = uniform_filter1d(g, n_of(win))
    return (y[:n] * g).astype(np.float32)


def add(*parts):
    """Sum signals of different lengths (zero-padded to the longest)."""
    n = max(len(p) for p in parts)
    return sum(fit(p, n) for p in parts).astype(np.float32)


def send(x, wet_sig, level):
    """Add an effect return at `level` relative to x's peak."""
    return add(x, level * wet_sig * np.max(np.abs(x)) / (np.max(np.abs(wet_sig)) + 1e-9))


def shelf_hi(x, f, gain_db):
    """High shelf as low-pass/high-pass split (phase-coherent enough for voice)."""
    hp = dsp.highpass(x, f, 2)
    return (x + (10 ** (gain_db / 20) - 1) * hp).astype(np.float32)


def shelf_lo(x, f, gain_db):
    lp = dsp.lowpass(x, f, 2)
    return (x + (10 ** (gain_db / 20) - 1) * lp).astype(np.float32)


def compress(x, thresh_db=-18.0, ratio=3.0, win=0.012, smooth=0.03):
    """RMS compressor relative to the signal's own peak level (no make-up: master() normalises)."""
    e = rms_env(x, win)
    lv = 20 * np.log10(e / (np.max(e) + 1e-9) + 1e-9)
    gdb = np.where(lv > thresh_db, (thresh_db - lv) * (1 - 1 / ratio), 0.0)
    gdb = uniform_filter1d(gdb, n_of(smooth))
    return (x * 10 ** (gdb / 20)).astype(np.float32)


def expander(x, thresh_db=-30.0, ratio=2.5, win=0.01, smooth=0.012, floor_db=-40.0):
    """Downward expander: clips word tails and breaths short (stern, clipped delivery)."""
    e = rms_env(x, win)
    lv = 20 * np.log10(e / (np.max(e) + 1e-9) + 1e-9)
    gdb = np.clip(np.where(lv < thresh_db, (lv - thresh_db) * (ratio - 1), 0.0), floor_db, 0)
    gdb = uniform_filter1d(gdb, n_of(smooth))
    return (x * 10 ** (gdb / 20)).astype(np.float32)


def limit(x, ceiling, look=0.004):
    """Look-ahead brickwall limiter (min-filter + equal-width smoothing never overshoots the ceiling)."""
    g = np.minimum(1.0, ceiling / (np.abs(x) + 1e-12))
    w = 2 * n_of(look) + 1
    g = uniform_filter1d(minimum_filter1d(g, w), w)
    return (x * g).astype(np.float32)


def deess(x, f=4800.0, thresh_db=-9.0, ratio=3.0):
    """Tame sibilant spikes: duck the band above f when it dominates the full-band level."""
    hi = dsp.highpass(x, f, 2)
    lo = x - hi
    rel = 20 * np.log10((rms_env(hi, 0.006) + 1e-7) / (rms_env(x, 0.006) + 1e-7))
    gdb = uniform_filter1d(np.where(rel > thresh_db, (thresh_db - rel) * (1 - 1 / ratio), 0.0), n_of(0.004))
    return (lo + hi * 10 ** (gdb / 20)).astype(np.float32)


def wobble_delay(x, rate=0.6, depth_ms=1.0, seed=0, jitter_ms=0.0, flutter_hz=0.0, flutter_ms=0.0):
    """Variable delay line -> tape wow (slow) and flutter (fast)."""
    n = len(x)
    t = taxis(n)
    d = depth_ms * 1e-3 * SR * 0.5 * (1 + np.sin(TWO_PI * rate * t + seed))
    if jitter_ms:
        d = d + jitter_ms * 1e-3 * SR * 0.5 * (1 + snoise(n, 3, seed + 11))
    if flutter_hz:
        d = d + flutter_ms * 1e-3 * SR * 0.5 * (1 + np.sin(TWO_PI * flutter_hz * t + 1.3 * seed))
    idx = np.arange(n)
    return np.interp(idx - d, idx, x).astype(np.float32)


def voiced_mask(x, thresh_db=-32.0, win=0.02):
    e = rms_env(x, win)
    return e > np.max(e) * 10 ** (thresh_db / 20)


def pauses(x, min_len=0.16, thresh_db=-38.0):
    """[(start, end)] sample ranges of silence between phrases (not leading/trailing)."""
    m = voiced_mask(x, thresh_db, 0.015)
    idx = np.where(m)[0]
    if not len(idx):
        return []
    a, b = idx[0], idx[-1]
    out = []
    i = a
    while i < b:
        if not m[i]:
            j = i
            while j < b and not m[j]:
                j += 1
            if j - i >= n_of(min_len):
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


# ====================================================================== TTS (with pronunciation respelling)
RESPELL = [
    (r'DEAD LINE', 'Ded Láin'),      # brand name, said in English
    (r'll', 'y'), (r'Ll', 'Y'),       # espeak gives 'ella'/'pasillos' a /jj/; 'y' gets the rioplatense /sh/
]


def respell(text):
    for a, b in RESPELL:
        text = re.sub(a, b, text)
    return text


def strip_islands(y, max_island=0.07, min_gap=0.03, thresh_db=-36.0):
    """Drop a stray click/breath that Kokoro sometimes leaves before the first word (or after the last)."""
    m = rms_env(y, 0.005) > np.max(rms_env(y, 0.005)) * 10 ** (thresh_db / 20)
    for _ in range(2):
        idx = np.where(m)[0]
        if not len(idx):
            break
        a = idx[0]
        b = a
        while b < len(m) and m[b]:
            b += 1
        g = b
        while g < len(m) and not m[g]:
            g += 1
        if b - a < n_of(max_island) and g - b >= n_of(min_gap) and g < len(m):
            y = y[g - n_of(0.004):]
            m = m[g - n_of(0.004):]
        y, m = y[::-1], m[::-1]
    return np.ascontiguousarray(y)


def say(text, voice='ef_dora', speed=0.9):
    """Kokoro line, leading/trailing silence and stray edge clicks trimmed, peak 0.8."""
    y = dsp.tts(respell(text), voice, speed)
    y = dsp.highpass(y, 60, 2)
    y = dsp.trim(y, -46, 0.03)
    y = dsp.fade(strip_islands(y), 0.003, 0.01)
    return norm(y, 0.8)


# ====================================================================== pitch tracking (YIN) + TD-PSOLA
def track_f0(x, fmin=70.0, fmax=480.0, hop=0.005, thresh=0.15):
    """YIN on a 11025 Hz copy. Returns (frame centre sample @SR, f0 Hz or 0 = unvoiced)."""
    ds = 4
    sr = SR / ds
    xd = signal.resample_poly(np.asarray(x, np.float64), 1, ds)
    W = 384
    tmax = int(sr / fmin) + 2
    tmin = max(2, int(sr / fmax))
    H = max(1, int(hop * sr))
    L = W + tmax
    xp = np.concatenate([xd, np.zeros(L)])
    nf = 1 + max(0, len(xd) - 1) // H
    idx = np.arange(nf)[:, None] * H + np.arange(L)[None, :]
    fr = xp[idx]
    nfft = 1 << int(math.ceil(math.log2(L + W)))
    A = np.fft.rfft(fr[:, :W], nfft)
    B = np.fft.rfft(fr, nfft)
    r = np.fft.irfft(np.conj(A) * B, nfft)[:, :tmax + 1]
    sq = np.concatenate([np.zeros((nf, 1)), np.cumsum(fr ** 2, axis=1)], axis=1)
    taus = np.arange(tmax + 1)
    e0 = sq[:, W]
    et = sq[:, taus + W] - sq[:, taus]
    d = np.maximum(e0[:, None] + et - 2 * r, 0)
    cm = np.cumsum(d[:, 1:], axis=1)
    dn = np.ones_like(d)
    dn[:, 1:] = d[:, 1:] * taus[1:] / (cm + 1e-12)
    rms = np.sqrt(e0 / W)
    loud = rms > np.max(rms) * 10 ** (-38 / 20)
    f0 = np.zeros(nf)
    for i in range(nf):
        if not loud[i]:
            continue
        row = dn[i]
        below = np.where(row[tmin:tmax] < thresh)[0]
        if len(below):
            t = tmin + below[0]
            while t + 1 < tmax and row[t + 1] < row[t]:
                t += 1
        else:
            t = tmin + int(np.argmin(row[tmin:tmax]))
            if row[t] > 0.3:
                continue
        if 1 <= t < tmax:
            a, b, c = row[t - 1], row[t], row[t + 1]
            den = a - 2 * b + c
            tt = t + (0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0)
        else:
            tt = t
        f0[i] = sr / tt
    # clean-up: octave jumps against a running median, short islands / gaps
    v = f0 > 0
    if v.sum() > 5:
        med = median_filter(np.where(v, f0, np.median(f0[v])), 15)
        for k in np.where(v)[0]:
            rto = f0[k] / med[k]
            if 1.7 < rto < 2.3:
                f0[k] /= 2
            elif 0.43 < rto < 0.6:
                f0[k] *= 2
        f0 = np.where(v, median_filter(f0, 5), 0)
        f0 = np.where(v & (f0 <= 0), med, f0)
    v = f0 > 0
    # remove voiced islands < 25 ms, fill gaps < 25 ms
    def runs(mask):
        out, i = [], 0
        while i < len(mask):
            j = i
            while j < len(mask) and mask[j] == mask[i]:
                j += 1
            out.append((mask[i], i, j))
            i = j
        return out
    short = max(1, int(0.025 / hop))
    for val, i, j in runs(v):
        if val and j - i < short:
            f0[i:j] = 0
    v = f0 > 0
    for val, i, j in runs(v):
        if not val and 0 < i and j < len(v) and j - i < short:
            f0[i:j] = np.linspace(f0[i - 1], f0[j], j - i + 2)[1:-1]
    centres = (np.arange(nf) * H + W / 2) * ds
    return centres, f0


def pitch_marks(x, centres, f0, unv_step=0.008):
    """Analysis pitch marks: one per glottal period in voiced runs (same-polarity peaks), fixed steps elsewhere."""
    n = len(x)
    s = np.arange(n)
    vs = np.interp(s, centres, (f0 > 0).astype(float)) > 0.5
    if (f0 > 0).any():
        f0s = np.interp(s, centres[f0 > 0], f0[f0 > 0])
    else:
        f0s = np.full(n, 150.0)
    xl = signal.sosfiltfilt(signal.butter(2, 1000 / (SR / 2), output='sos'), x)
    marks, per, vf = [], [], []
    U = n_of(unv_step)
    i = 0
    while i < n:
        j = i
        while j < n and vs[j] == vs[i]:
            j += 1
        if vs[i] and j - i > n_of(0.012):
            seg = xl[i:j]
            pol = 1.0 if np.max(seg) >= -np.min(seg) else -1.0
            T = SR / f0s[i]
            m = i + int(np.argmax(pol * xl[i:min(j, i + int(T) + 1)]))
            while m < j:
                T = SR / f0s[m]
                marks.append(m)
                per.append(int(round(T)))
                vf.append(True)
                lo, hi = m + int(0.7 * T), min(n, m + int(1.3 * T) + 1)
                if lo >= j or lo >= hi:
                    break
                m = lo + int(np.argmax(pol * xl[lo:hi]))
        else:
            for m in range(i, j, U):
                marks.append(m)
                per.append(U)
                vf.append(False)
        i = j
    return np.array(marks), np.array(per), np.array(vf)


def psola(x, marks, per, vf, n_out, alpha, tmap=None, jitter=0.0, shimmer=0.0, seed=0):
    """TD-PSOLA. alpha: pitch factor (scalar or per output sample). tmap: input sample position per output sample."""
    r = dsp.rng(seed)
    alpha = np.broadcast_to(np.asarray(alpha, np.float64), (n_out,)) if np.ndim(alpha) == 0 else np.asarray(alpha)
    maxp = int(np.max(per)) + 2
    xp = np.concatenate([np.zeros(maxp), x, np.zeros(maxp)])
    y = np.zeros(n_out + 2 * maxp)
    wins = {}
    ts = 0.0
    while ts < n_out:
        it = int(ts)
        tin = tmap[it] if tmap is not None else ts
        k = int(np.searchsorted(marks, tin))
        if k >= len(marks):
            k = len(marks) - 1
        elif k > 0 and (tin - marks[k - 1]) < (marks[k] - tin):
            k -= 1
        P = int(per[k])
        w = wins.get(P)
        if w is None:
            w = wins[P] = np.hanning(2 * P + 1)
        c = marks[k] + maxp
        g = xp[c - P:c + P + 1] * w
        if vf[k]:
            if shimmer:
                g = g * (1 + shimmer * r.standard_normal())
            step = P / alpha[it]
            if jitter:
                step *= 1 + jitter * float(np.clip(r.standard_normal(), -2.5, 2.5))
        else:
            step = P
        o = it + maxp
        y[o - P:o + P + 1] += g
        ts += max(step, 8.0)
    y = y[maxp:maxp + n_out].astype(np.float32)
    ref = x if tmap is None else np.interp(tmap, np.arange(len(x)), x)
    return match_env(y, fit(ref, n_out) if tmap is None else ref.astype(np.float32))


def reshape(x, semis=0.0, formant=0.0, wobble=0.0, wobble_rate=2.0, tremor=0.0, tremor_rate=5.5, jitter=0.0,
            shimmer=0.0, curve=None, tmap=None, n_out=None, seed=0, fmin=70.0, fmax=480.0):
    """Character voice: pitch by `semis` keeping the vocal tract, tract scaled by `formant` semitones.
    wobble = slow random pitch drift (cents), tremor = sinusoidal pitch tremor (fraction),
    curve = extra semitone contour over the line (array, any length, stretched to the output)."""
    beta = 2 ** (formant / 12)
    xs = dsp.resample(x, beta) if abs(formant) > 1e-3 else np.asarray(x, np.float32)
    centres, f0 = track_f0(xs, fmin * beta, fmax * beta)
    marks, per, vf = pitch_marks(xs, centres, f0)
    n_out = n_out or (len(tmap) if tmap is not None else len(x))
    if tmap is None:
        tm = np.arange(n_out) / beta
    else:
        tm = np.asarray(tmap, np.float64) / beta
    tm = np.clip(tm, 0, len(xs) - 1)
    st = np.full(n_out, semis - formant, np.float64)
    if wobble:
        st += wobble / 100 * snoise(n_out, wobble_rate, seed + 5)
    if tremor:
        st += 12 * np.log2(1 + tremor * np.sin(TWO_PI * tremor_rate * taxis(n_out) + seed))
    if curve is not None:
        st += np.interp(np.linspace(0, 1, n_out), np.linspace(0, 1, len(curve)), curve)
    alpha = 2 ** (st / 12)
    return psola(xs, marks, per, vf, n_out, alpha, tm if (tmap is not None or abs(formant) > 1e-3) else None,
                 jitter, shimmer, seed)


# ====================================================================== DTW (align a second speaker to the first)
def _mel_fb(nfft, nmel=32, fmin=80, fmax=7600):
    def mel(f):
        return 2595 * np.log10(1 + f / 700)

    def imel(m):
        return 700 * (10 ** (m / 2595) - 1)
    pts = imel(np.linspace(mel(fmin), mel(fmax), nmel + 2))
    bins = np.fft.rfftfreq(nfft, 1 / SR)
    fb = np.zeros((nmel, len(bins)))
    for i in range(nmel):
        a, b, c = pts[i], pts[i + 1], pts[i + 2]
        fb[i] = np.clip(np.minimum((bins - a) / (b - a), (c - bins) / (c - b)), 0, None)
    return fb


def mfcc(x, hop=441, nfft=1024):
    xp = np.concatenate([np.zeros(nfft // 2), x, np.zeros(nfft)])
    nf = 1 + len(x) // hop
    idx = np.arange(nf)[:, None] * hop + np.arange(nfft)[None, :]
    S = np.abs(np.fft.rfft(xp[idx] * np.hanning(nfft), axis=1)) ** 2
    E = np.log(S @ _mel_fb(nfft).T + 1e-8)
    C = dct(E, axis=1, norm='ortho')[:, 1:14]
    return (C - C.mean(0)) / (C.std(0) + 1e-6)


def align_feats(x, hop=441, w_e=3.0):
    """MFCC 1-10 + log loudness (weighted: closures and syllable nuclei are the best cross-speaker landmarks) + deltas."""
    C = mfcc(x, hop)[:, :10]
    e = np.log(rms_env(x, 0.012)[::hop][:len(C)] + 1e-5)
    e = np.pad((e - e.mean()) / (e.std() + 1e-6), (0, max(0, len(C) - len(e))), mode='edge')[:len(C)]
    return np.concatenate([C, w_e * e[:, None], 0.7 * np.gradient(C, axis=0), 2 * w_e * np.gradient(e)[:, None]], 1)


def dtw_map(ref, src, hop=441):
    """Per-sample map ref timeline -> src sample position (symmetric DTW, slopes 1/2..2, ends pinned)."""
    A, B = align_feats(ref, hop), align_feats(src, hop)
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    N, M = D.shape
    INF = 1e18
    acc = np.full((N, M), INF)
    back = np.zeros((N, M), np.int8)
    acc[0, 0] = D[0, 0]
    for i in range(1, N):
        c0 = np.full(M, INF)
        c0[1:] = acc[i - 1, :-1] + D[i, 1:]                        # (1,1)
        c1 = np.full(M, INF)
        c1[2:] = acc[i - 1, :-2] + D[i, 1:-1] + D[i, 2:]           # (1,2)
        c2 = np.full(M, INF)
        if i >= 2:
            c2[1:] = acc[i - 2, :-1] + D[i - 1, 1:] + D[i, 1:]     # (2,1)
        st = np.stack([c0, c1, c2])
        back[i] = np.argmin(st, 0)
        acc[i] = np.min(st, 0)
    i, j = N - 1, M - 1
    if acc[i, j] >= INF:
        return np.linspace(0, len(src) - 1, len(ref))
    path = [(i, j)]
    while i > 0 and j > 0:
        b = back[i, j]
        if b == 0:
            i, j = i - 1, j - 1
        elif b == 1:
            i, j = i - 1, j - 2
        else:
            i, j = i - 2, j - 1
        path.append((i, j))
    path = np.array(path[::-1])
    jj = np.interp(np.arange(N), path[:, 0], path[:, 1])
    jj = np.maximum.accumulate(uniform_filter1d(jj, 3))
    return np.clip(np.interp(np.arange(len(ref)), np.arange(N) * hop, jj * hop), 0, len(src) - 1)


# ====================================================================== breath, whisper, sounds of the mouth
def whisper(x, seed=0, smooth=9, nper=1024):
    """Replace voicing by noise with the same spectral envelope (keeps the words, loses the pitch)."""
    _, _, Z = signal.stft(x, SR, nperseg=nper, noverlap=nper * 3 // 4)
    mag = uniform_filter1d(np.abs(Z), smooth, axis=0)
    ph = dsp.rng(seed).uniform(-np.pi, np.pi, Z.shape)
    _, y = signal.istft(mag * np.exp(1j * ph), SR, nperseg=nper, noverlap=nper * 3 // 4)
    y = dsp.highpass(fit(y, len(x)), 200, 2)
    y = dsp.peak(y, 4800, 3, 1.0)
    return match_env(y, x, 0.015)


def breath_in(dur=0.3, seed=0, size=1.0, gain=1.0, shaky=0.0):
    """Mouth inhale: band noise with a rising whistle-ish resonance. size < 1 = smaller person (higher)."""
    n = n_of(dur)
    r = dsp.rng(seed)
    a = dsp.noise(dur, 'white', seed)
    a = dsp.bandpass(a, 600 / size, 4200 / size, 2)
    f = r.uniform(1500, 1900) / size
    a = dsp.peak(a, f, 7, 3) + 0.5 * dsp.peak(dsp.bandpass(a, 2500 / size, 6000 / size, 2), 3400 / size, 6, 2)
    e = dsp.env_points(n, [(0, 0), (0.35, 0.7), (0.8, 1.0), (1, 0)]) ** 1.3
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * r.uniform(9, 13) * taxis(n))))
    return norm(a * e, gain)


def breath_out(dur=0.5, seed=0, size=1.0, gain=1.0, shaky=0.0):
    n = n_of(dur)
    b = dsp.noise(dur, 'pink', seed)
    b = dsp.bandpass(b, 200 / size, 2400 / size, 2)
    b = dsp.peak(b, 700 / size, 5, 2)
    e = dsp.env_points(n, [(0, 0), (0.1, 1.0), (0.5, 0.6), (1, 0)])
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * 8.5 * taxis(n))))
    return norm(b * e, gain)


def sob(seed=0, size=1.0, gain=1.0):
    """Crying inhale 'hih-hih-hiih': two or three stuttered gasps with a squeaky voiced edge."""
    r = dsp.rng(seed)
    parts = []
    k = int(r.integers(2, 4))
    for i in range(k):
        d = r.uniform(0.07, 0.11) if i < k - 1 else r.uniform(0.2, 0.28)
        g = breath_in(d, seed + 10 * i, size * 0.95, 1.0)
        nn = len(g)
        f = dsp.glide(r.uniform(420, 500) / size, r.uniform(620, 760) / size, d)
        sq = dsp.osc(f, d, 'saw')[:nn] + 0.3 * dsp.noise(d, 'white', seed + 3 + i)[:nn]
        sq = dsp.bandpass(sq, 500 / size, 3200 / size, 2)
        sq = dsp.peak(sq, 2300 / size, 6, 3) * dsp.env_points(nn, [(0, 0), (0.3, 0), (0.6, 1), (1, 0)])
        parts.append(norm(g, 0.8) + norm(sq, 0.22 if i == k - 1 else 0.1))
        parts.append(dsp.silence(r.uniform(0.03, 0.06)))
    y = dsp.concat(*parts)
    return norm(y, gain)


def shush(dur=1.0, seed=0, size=1.0, force=1.0, attack=0.06, release=0.18, wavy=0.25):
    """Human 'shhh' (post-alveolar fricative, rounded lips): noise through the /sh/ resonances."""
    n = n_of(dur)
    r = dsp.rng(seed)
    w = dsp.noise(dur, 'white', seed)
    fc = r.uniform(2500, 2900) / size
    y = dsp.bandpass(w, 1500 / size, 8500, 2)
    y = dsp.peak(y, fc, 12, 2.2)
    y = dsp.peak(y, fc * 1.9, 5, 2.5)
    y = dsp.lowpass(y, 7500, 2) + 0.12 * dsp.highpass(w, 6000, 2)
    # breath pressure: swell, fast flutter of the lips, gentle sag
    press = 1 + wavy * snoise(n, 6, seed + 1) + 0.06 * snoise(n, 40, seed + 2)
    e = dsp.env_points(n, [(0, 0), (min(0.4, attack / dur), 1.0), (0.55, 0.85 + 0.15 * force), (1 - min(0.45, release / dur), 0.75), (1, 0)])
    y = y * e * press
    # a softer, lower start (lips not yet sealed) for realism
    lo = dsp.bandpass(w, 700 / size, 2500 / size, 2) * dsp.env_points(n, [(0, 0), (0.05, 0.5), (0.25, 0.0), (1, 0)])
    return norm(y + 0.25 * lo * np.max(np.abs(y)) / (np.max(np.abs(lo)) + 1e-9), force)


# ====================================================================== spaces
def ir_room(decay, damp=6000.0, predelay=0.0, early=(), lo=0.0, seed=0, build=0.01, er_damp=None):
    """Impulse response: early reflection taps [(ms, gain)] + exponentially decaying filtered noise tail."""
    r = dsp.rng(seed)
    pd = n_of(predelay)
    n = n_of(decay * 1.15) + pd + n_of(0.1)
    t = taxis(n - pd)
    tail = r.standard_normal(n - pd) * np.exp(-6.9 * t / decay)
    tail *= np.clip(t / max(build, 1e-3), 0, 1)
    tail = dsp.lowpass(tail.astype(np.float32), damp, 2)
    if lo:
        tail = dsp.highpass(tail, lo, 2)
    ir = np.zeros(n, np.float32)
    ir[pd:] = tail
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    if early:
        er = np.zeros(n, np.float32)
        for ms, g in early:
            k = n_of(ms / 1000)
            if k < n:
                er[k] += g * (1 if r.random() < 0.6 else -1)
        er = dsp.lowpass(er, er_damp or damp * 1.3, 2)
        return ir, er
    return ir, None


def space(x, decay=0.5, wet=0.15, damp=6000.0, predelay=0.0, early=(), er_gain=0.4, lo=0.0, seed=0, dry=1.0, build=0.01):
    ir, er = ir_room(decay, damp, predelay, early, lo, seed, build)
    pad = np.concatenate([x, np.zeros(len(ir), np.float32)])
    y = dry * pad + wet * signal.fftconvolve(pad, ir)[:len(pad)]
    if er is not None:
        y += er_gain * signal.fftconvolve(pad, er)[:len(pad)]
    return y.astype(np.float32)


CLASSROOM_ER = [(4.3, 0.55), (6.9, 0.42), (9.8, 0.36), (13.4, 0.3), (17.1, 0.24), (22.6, 0.18), (28.9, 0.14), (36.0, 0.1)]
BOX_ER = [(1.2, 0.7), (1.9, 0.55), (2.6, 0.5), (3.3, 0.42), (4.1, 0.36), (4.9, 0.3), (5.8, 0.26), (6.9, 0.2), (8.1, 0.16), (9.6, 0.12)]
CHAPEL_ER = [(17, 0.35), (26, 0.3), (38, 0.27), (47, 0.22), (61, 0.2), (74, 0.16), (89, 0.12), (107, 0.1)]
CRYPT_ER = [(9, 0.4), (15, 0.33), (23, 0.3), (31, 0.25), (42, 0.2), (55, 0.16), (70, 0.12)]


def classroom(x, seed=1, wet=0.11):
    return space(x, 0.55, wet, 5200, 0.004, CLASSROOM_ER, 0.32, 180, seed)


def chapel(x, seed=2, wet=0.3, decay=3.6, dry=1.0):
    return space(x, decay, wet, 4200, 0.03, CHAPEL_ER, 0.22, 250, seed, dry, build=0.04)


# ====================================================================== transmission chains
def phone_line(x, seed=0, bed=0.006):
    """dsp.phone_voice + a handset colour and a quiet line bed with 80 ms lead-in/out."""
    y = dsp.phone_voice(dsp.peak(x, 1800, 2.5, 1.2))
    y = dsp.lowpass(dsp.peak(y, 1000, 2, 1.5), 3900, 4)     # the earpiece: no crushed images above the band
    pad = n_of(0.08)
    y = np.concatenate([np.zeros(pad, np.float32), y, np.zeros(pad, np.float32)])
    nb = dsp.bandpass(dsp.noise(len(y) / SR, 'pink', seed + 77), 300, 3400, 2)
    return (y + bed * nb / (np.max(np.abs(nb)) + 1e-9) * np.max(np.abs(y)) * 4).astype(np.float32)


def mic_switch(seed=0, gain=0.25, on=True):
    """Old PA microphone key: a dull thump through the speaker plus a small contact click."""
    L = n_of(0.07)
    t = taxis(L)
    y = dsp.osc(105 if on else 80, L / SR, 'sine')[:L] * np.exp(-t * (85 if on else 60)) * 0.7
    k = n_of(0.01)
    y[:k] += dsp.bandpass(dsp.noise(0.01, 'white', seed), 500, 3200, 2)[:k] * np.exp(-taxis(k) * 450)
    return norm(dsp.bandpass(y, 70, 3500, 2), gain)


def pa_speaker(x, seed=0):
    """1980s school loudspeaker: horn + paper cone, 50 Hz hum while the mic is open, corridor slapback."""
    y = dsp.bandpass(x, 300, 3500, 4)
    y = dsp.peak(y, 950, 6, 2.0)            # horn throat
    y = dsp.peak(y, 2300, 7, 3.0)           # cone break-up
    y = dsp.peak(y, 3200, 3, 4.0)
    d = n_of(0.00055)                       # horn mouth reflection: short comb -> the 'honk'
    y = y + 0.35 * np.concatenate([np.zeros(d, np.float32), y[:-d]])
    y = dsp.drive(norm(y, 1.0) * 1.5, 1.7)
    y = norm(dsp.bandpass(y, 280, 3800, 2), 0.9)
    # nearest speaker + the next ones down the corridor + the corridor's own slapback
    taps = [(0.0, 1.0), (0.052, 0.26), (0.118, 0.2), (0.205, 0.12), (0.33, 0.07)]
    out = dsp.mix(*[(dsp.lowpass(y, 3600 - 600 * i, 2) if i else y, dl, g) for i, (dl, g) in enumerate(taps)])
    out = space(out, 1.4, 0.15, 3200, 0.02, [(31, 0.18), (63, 0.12), (97, 0.08)], 0.25, 300, seed + 9)
    # the amplifier bed only while the mic is keyed: on-click ... speech ... +0.3 s ... off-click
    lead = n_of(0.08)
    end = int(np.where(voiced_mask(y, -40))[0][-1]) + n_of(0.3)
    m = max(len(out), end + n_of(0.1))
    n = lead + m
    t = taxis(n)
    hum = sum(np.sin(TWO_PI * 50 * k * t) / k ** 1.3 for k in range(1, 8)).astype(np.float32)
    hum = dsp.highpass(hum, 90, 2) / 3.0 * 0.03
    hiss = dsp.bandpass(dsp.noise(n / SR, 'white', seed + 5), 1500, 6000, 2) * 0.012
    gate = np.zeros(n, np.float32)
    gate[n_of(0.02):lead + end] = 1
    gate = uniform_filter1d(gate, n_of(0.012))
    voice = np.zeros(n, np.float32)
    voice[lead:lead + len(out)] += out[:n - lead]
    voice[n_of(0.005):n_of(0.005) + n_of(0.07)] += mic_switch(seed, 0.22)
    voice[lead + end:lead + end + n_of(0.07)] += mic_switch(seed + 1, 0.16, on=False)[:max(0, n - lead - end)]
    return (voice + (hum + hiss) * gate).astype(np.float32)


def tape84(x, seed=0, drops=((0.31, 0.06), (0.62, 0.05))):
    """1984 microcassette answering machine: narrow band, saturation, wow/flutter, hiss, dropouts."""
    r = dsp.rng(seed)
    y = dsp.bandpass(x, 220, 4600, 3)
    y = dsp.peak(y, 1500, 2.5, 1.2)
    y = dsp.drive(norm(y, 1.0) * 1.3, 1.4)
    y = wobble_delay(y, 0.7, 1.6, seed, jitter_ms=1.2, flutter_hz=11.0, flutter_ms=0.22)
    n = len(y)
    g = np.ones(n, np.float32)
    for pos, dur in drops:   # oxide dropouts: level and highs dip
        s, L = int(pos * n), n_of(dur)
        if s + L < n:
            g[s:s + L] *= 1 - 0.8 * np.hanning(L)
    lp = dsp.lowpass(y, 1400, 2)
    y = lp + (y - lp) * g ** 2
    y = y * (0.35 + 0.65 * g)
    hiss = dsp.bandpass(dsp.noise(n / SR, 'white', seed + 1), 1800, 4600, 2) * 0.09 + \
        dsp.bandpass(dsp.noise(n / SR, 'pink', seed + 2), 200, 3000, 2) * 0.05
    hiss = hiss * (1 + 0.25 * snoise(n, 0.8, seed + 6))                         # tape hiss breathes with the wow
    motor = dsp.bandpass(dsp.osc(31.0 * (1 + 0.01 * snoise(n, 1, seed)), n / SR, 'saw')[:n], 60, 400, 2) * 0.03
    return (norm(y, 0.85) + hiss + motor).astype(np.float32)


def codec_glitches(x, seed=0, count=3):
    """Tiny digital artefacts: 10-20 ms stutters/packet losses away from the loudest syllables."""
    r = dsp.rng(seed)
    y = x.copy()
    n = len(x)
    e = rms_env(x, 0.03)
    for _ in range(count):
        for _try in range(20):
            s = int(r.integers(n_of(0.2), max(n_of(0.3), n - n_of(0.3))))
            if e[s] < 0.6 * np.max(e):
                break
        L = n_of(r.uniform(0.012, 0.022))
        kind = r.integers(2)
        if kind == 0:          # stutter: repeat the previous frame
            y[s:s + L] = x[s - L:s]
        else:                  # packet loss: 8-bit comfort noise
            y[s:s + L] = dsp.bitcrush(x[s:s + L] * 0.4, 5, 3)
        w = min(n_of(0.002), L // 2)
        y[s:s + w] = y[s:s + w] * np.linspace(1, 0.6, w) + x[s:s + w] * np.linspace(0, 0.4, w)
    return y


# ====================================================================== character presets
def aspirate(x, y, gain=0.35, seed=0, lo=0.02, hi=0.2, duck=0.7):
    """Put back a [x] (velar fricative) in short unvoiced gaps between vowels: Kokoro voices the 'j' of 'Ajá'
    almost like a glide, so the voicing is ducked across the gap and a velar-shaped breath burst goes in."""
    c, f = track_f0(x, 90, 450)
    v = f > 0
    out = y.copy()
    pk = np.max(np.abs(y))
    k = 1
    while k < len(v):
        if v[k - 1] and not v[k]:
            j = k
            while j < len(v) and not v[j]:
                j += 1
            if j < len(v) and lo <= (c[j] - c[k]) / SR <= hi:
                a, b = int(c[k]) - n_of(0.01), int(c[j]) + n_of(0.03)
                L = b - a
                L = max(L, n_of(0.075))
                a = max(0, (a + b) // 2 - L // 2)
                L = min(L, len(out) - a)
                src = fit(y[int(c[j]):int(c[j]) + L], L)
                h = dsp.peak(dsp.highpass(whisper(src, seed + k), 700, 2), 1500, 9, 1.3)
                h = norm(h, 1.0) * dsp.env_points(L, [(0, 0), (0.25, 0.8), (0.6, 1.0), (0.85, 0.5), (1, 0)])
                out[a:a + L] *= 1 - duck * np.hanning(L)
                out[a:a + L] += gain * pk * h
            k = j
        k += 1
    return out


def vox_madre(text, fx, seed, tw):
    x = say(text, 'ef_dora', tw.get('speed', 0.8))
    y = reshape(x, semis=tw.get('semis', -3.0), formant=-0.7, wobble=8, wobble_rate=1.5, tremor=0.008, tremor_rate=5.3,
                jitter=0.012, shimmer=0.07, curve=tw.get('curve'), seed=seed, fmin=90, fmax=420)
    if tw.get('aspirate'):
        y = aspirate(x, y, tw['aspirate'], seed)
    rasp = dsp.bandpass(whisper(y, seed + 1), 1200, 6500, 2)
    y = y + 0.14 * rasp
    y = dsp.highpass(y, 110, 2)
    y = dsp.peak(y, 1250, 2.0, 1.8)       # a bit pinched/nasal
    y = dsp.peak(y, 2900, 3.0, 1.4)       # authority
    y = expander(y, -27, 2.2)
    y = compress(y, -16, 3.0)
    if tw.get('drive'):
        y = dsp.drive(norm(y, 1.0) * tw['drive'], tw['drive'])
    dry = y.copy()
    if fx == 'pa':
        return pa_speaker(norm(y, 0.9), seed), dry
    if fx == 'head':
        y = shelf_lo(y, 220, 3.5)
        y = y + 0.18 * dsp.highpass(whisper(y, seed + 7), 1500, 2)
        z = space(y, 0.25, 0.08, 4500, 0.0, [(2.1, 0.3), (3.7, 0.2)], 0.3, 150, seed)
        tail = dsp.lowpass(space(y, 2.6, 1.0, 1800, 0.06, (), 0, 300, seed + 4, dry=0.0), 1800, 2)
        return send(z, tail, 0.2), dry
    return classroom(y, seed), dry


def clara_voice(text, seed, speed=0.95, wh=0.6, tremble=1.0):
    x = say(text, 'ef_dora', speed)
    y = reshape(x, semis=0.8, formant=0.3, wobble=14 * tremble, wobble_rate=3.0, tremor=0.016 * tremble,
                tremor_rate=6.6, jitter=0.01, shimmer=0.09, seed=seed, fmin=110, fmax=480)
    w = whisper(y, seed + 3)
    v = dsp.highpass(y, 160, 2)
    v = dsp.tremolo(v, 7.2, 0.22 * tremble)
    out = (1 - wh) * v + wh * 1.25 * w
    out = dsp.peak(out, 3600, 3, 1.2)       # close-mic hush
    return out, x


def add_breaths(y, seed, size=1.0, kind='scared', gain=0.35):
    """Fill the pauses with quick scared inhales (or crying sobs) that end right before the next phrase."""
    y = y.copy()
    pk = np.max(np.abs(y))
    for i, (a, b) in enumerate(pauses(y, 0.16)):
        L = b - a
        if kind == 'sob' and L > n_of(0.45):
            s = sob(seed + 31 * i, size, 1.0)
        else:
            d = min(0.32, max(0.12, L / SR * 0.7))
            s = breath_in(d, seed + 17 * i, size, 1.0, shaky=0.5 if kind == 'sob' else 0.25)
        s = fit(s, min(len(s), L - n_of(0.02)))
        st = b - n_of(0.025) - len(s)
        if st < a:
            continue
        y[st:st + len(s)] += s * gain * pk
    return y


def vox_clara(text, fx, seed, tw):
    if fx == 'room':   # freed Clara (Maitines): calm, warm, gently breathy, chapel
        y, x = clara_voice(text, seed, tw.get('speed', 0.9), wh=0.22, tremble=0.25)
        y = dsp.peak(y, 250, 2, 1.0)
        y = shelf_hi(y, 7000, 2.5)
        dry = y.copy()
        out = chapel(y, seed, wet=0.2, decay=2.8)
        return out, dry
    y, x = clara_voice(text, seed, tw.get('speed', 0.95))
    y = add_breaths(y, seed + 50, 1.0, 'scared', 0.28)
    dry = y.copy()
    return phone_line(y, seed), dry


def vox_clara84(text, fx, seed, tw):
    """Phrase by phrase, crying breaths between, then tape and phone."""
    phrases = [p.strip() for p in re.split(r'\.\.\.', text) if p.strip(' .')]
    parts = []
    for i, p in enumerate(phrases):
        y, _ = clara_voice(p, seed + 100 * i, 0.9, wh=0.5, tremble=1.6)
        y = dsp.tremolo(y, 6.0, 0.25)          # voice breaking with the crying
        parts.append(norm(y, 0.9))
        if i < len(phrases) - 1:
            g = 0.55 + 0.2 * (i % 2)
            cry = dsp.concat(sob(seed + 7 * i, 1.0, 0.5 * g), dsp.silence(0.05),
                             breath_out(0.45, seed + 9 * i, 1.0, 0.25 * g, shaky=0.8), dsp.silence(0.12))
            parts.append(cry)
    y = dsp.concat(*parts, gap=0.06)
    dry = y.copy()
    n = len(y)
    pz = pauses(y, 0.2)
    drops = [((a + b) / 2 / n, 0.07) for a, b in pz[:2]] + [(0.78, 0.05)]
    t = tape84(y, seed, drops)
    # machine: playback key clunk + 0.12 s of hiss before the voice
    lead = n_of(0.14)
    clunk = np.zeros(lead, np.float32)
    k = n_of(0.03)
    clunk[:k] = dsp.bandpass(dsp.noise(0.03, 'white', seed + 4), 300, 2500, 2)[:k] * np.exp(-taxis(k) * 160) * 0.5
    hs = dsp.highpass(dsp.noise(0.14, 'white', seed + 8), 2500, 2)[:lead] * 0.035 * np.linspace(0, 1, lead)
    t = np.concatenate([clunk + hs, t])
    return phone_line(t, seed + 1, 0.004), np.concatenate([np.zeros(lead, np.float32), dry])


def vox_cura(text, fx, seed, tw):
    x = say(text, 'em_santa', tw.get('speed', 0.8))
    y = reshape(x, semis=tw.get('semis', -0.7), formant=-0.4, wobble=10, wobble_rate=1.2, tremor=0.011,
                tremor_rate=4.7, jitter=0.012, shimmer=0.08, seed=seed, fmin=55, fmax=300, curve=tw.get('curve'))
    y = y + tw.get('whisper', 0.07) * whisper(y, seed + 2)
    y = dsp.highpass(y, 70, 2)
    y = dsp.peak(y, 210, 3.0, 1.0)          # warm chest
    y = dsp.peak(y, 3200, -2.0, 1.0)
    y = compress(y, -18, 2.5)
    dry = y.copy()
    # inside the wooden box: dense reflections, panel modes, the lattice grille between him and you
    z = space(y, 0.2, 0.28, 3200, 0.0, BOX_ER, 0.45, 90, seed + 3)
    z = dsp.peak(z, 172, 4.0, 3.0)
    z = dsp.peak(z, 345, 3.0, 3.5)
    z = dsp.peak(z, 1900, -2.5, 2.0)
    z = dsp.lowpass(z, 5600, 2)
    beyond = space(z, 2.2, 1.0, 2600, 0.04, (), 0, 220, seed + 5, dry=0.0)
    return send(z, beyond, 0.12), dry


def girl(text, seed, speed=0.9, semis=4.0, formant=2.0, wob=28, wh=0.25, curve=None):
    x = say(text, 'ef_dora', speed)
    y = reshape(x, semis=semis, formant=formant, wobble=wob, wobble_rate=2.4, tremor=0.004, tremor_rate=6.0,
                jitter=0.006, shimmer=0.05, curve=curve, seed=seed, fmin=110, fmax=480)
    if wh:
        y = (1 - wh) * y + wh * 1.2 * whisper(y, seed + 4)
    return y


def vox_alumna(text, fx, seed, tw, lid=''):
    if lid.endswith('.shh'):
        y = dsp.concat(breath_in(0.18, seed, 0.85, 0.25), dsp.silence(0.04), shush(1.15, seed, 0.85, 1.0, 0.07, 0.35))
        y = dsp.bandpass(y, 400, 9000, 2)
    elif lid.endswith('.shh_viene'):
        sh = shush(0.62, seed, 0.85, 1.0, 0.05, 0.2)
        v = girl('viene.', seed, 0.82, wh=0.82)
        v = dsp.bandpass(v, 400, 6000, 2)
        y = dsp.concat(sh, dsp.silence(0.32), norm(v, 0.9))
    else:
        wh = 0.85 if '(susurro)' in LINES.get(lid, {}).get('es', '') else 0.25
        y = girl(text, seed, tw.get('speed', 0.86), wh=wh)
        y = dsp.bandpass(y, 400, 6000, 2)
    dry = y.copy()
    z = space(y, 2.2, 0.32, 7500, 0.035, [(23, 0.25), (37, 0.2), (52, 0.15)], 0.3, 550, seed + 2, build=0.05)
    return z, dry


def vox_paloma(text, fx, seed, tw, lid=''):
    if lid.endswith('chiste1'):       # the punchline is whispered close to the slit, then a breath on your neck
        head, tail = text.split('...')
        a = girl(head.strip(), seed, 0.92, 4.0, 1.6, 12, 0.1)
        b = girl(tail.strip(), seed + 1, 0.8, 3.5, 1.4, 10, 0.75)
        b = shelf_lo(b, 250, 3.0) * 1.15
        y = dsp.concat(norm(a, 0.9), dsp.silence(0.55), norm(b, 0.95), dsp.silence(0.08),
                       breath_out(0.5, seed + 2, 0.9, 0.18))
    else:
        y = girl(text, seed, tw.get('speed', 0.92), 4.0, 1.6, 12, 0.12)
    y = dsp.bandpass(y, 250, 7500, 2)
    dry = y.copy()
    z = space(y, 1.5, 0.13, 6500, 0.012, [(9, 0.25), (17, 0.2), (26, 0.12)], 0.25, 300, seed + 3)
    return z, dry


CHOIR = [  # (speed, formant st, detune cents, offset ms, gain)
    (0.94, 2.4, -14, 12, 1.0), (1.00, 1.6, 9, 27, 0.92), (1.06, 2.0, -6, 18, 0.85), (0.90, 1.2, 18, 35, 0.8),
    (1.10, 2.8, -19, 22, 0.75), (0.97, 1.9, 4, 40, 0.85), (1.03, 1.4, 14, 31, 0.8)]

_SYL = {}


def giggle_syllables(text):
    """Cut Kokoro's 'ji ji ji ji' into its syllables at the loudness dips."""
    if text not in _SYL:
        src = say(text, 'ef_dora', 1.0)
        e = uniform_filter1d(rms_env(src, 0.012), n_of(0.02))
        k = len(text.split())
        pk, pr = signal.find_peaks(-e, distance=n_of(0.1), prominence=0)
        inner = [p for p in pk if n_of(0.08) < p < len(src) - n_of(0.08)]
        cuts = sorted(sorted(inner, key=lambda p: -pr['prominences'][list(pk).index(p)])[:k - 1])
        edges = [0] + cuts + [len(src)]
        _SYL[text] = [src[edges[i]:edges[i + 1]] for i in range(len(edges) - 1)]
    return _SYL[text]


def giggle(text, seed, rate, semis, formant, count):
    """One girl's stifled giggle: staccato breathy 'hi-hi-hi' syllables falling in pitch, maybe a snort at the end."""
    r = dsp.rng(seed)
    syl = giggle_syllables(text)
    parts = []
    t = 0.0
    top = r.uniform(1.5, 3.0)
    for k in range(count):
        s0 = syl[int(r.integers(len(syl)))]
        d = r.uniform(0.09, 0.13)
        g = fit(s0, n_of(d)) * dsp.env_points(n_of(d), [(0, 0), (0.08, 1.0), (0.45, 0.75), (1, 0)])
        st = semis + top - k * r.uniform(0.4, 0.8) + r.normal(0, 0.3)
        v = reshape(g, semis=st, formant=formant, wobble=20, wobble_rate=6.0, seed=seed + k, fmin=110, fmax=480)
        v = 0.55 * v + 0.75 * whisper(v, seed + 50 + k)
        parts.append((norm(v, 1.0 - 0.07 * k), t, 1.0))
        t += r.uniform(0.85, 1.15) / rate
    if r.random() < 0.5:   # trying not to laugh: a little nose snort
        sn = breath_in(0.12, seed + 9, 0.8, 0.45, 0.6)
        parts.append((sn, t + 0.04, 1.0))
    return dsp.mix(*parts)


def vox_coro(text, fx, seed, tw, lid=''):
    takes = []
    if lid.endswith('shhh'):           # the seven of them shushing the Madre
        for i, (sp, fm, dt, off, g) in enumerate(CHOIR):
            d = 1.35 + 0.18 * dsp.rng(seed + i).random()
            s = shush(d, seed + 13 * i, 0.82 + 0.03 * i, 1.0, 0.025 + 0.004 * i, 0.22, 0.18)
            s = dsp.highpass(s, 500, 2)
            takes.append((s, off / 1000, g))
        y = dsp.mix(*takes)
        y = dsp.concat(breath_in(0.16, seed + 99, 0.8, 0.35 * np.max(np.abs(y))), y)
        dry = y.copy()
        return chapel(y, seed, wet=0.3, decay=3.0), dry
    if lid.endswith('risitas'):        # the ghost class giggles: never in sync, spreading around the room
        starts = [0.0, 0.12, 0.3, 0.45, 0.62, 0.8, 0.95]
        for i, (sp, fm, dt, off, g) in enumerate(CHOIR):
            v = giggle(text, seed + 31 * i, 6.2 * sp, 4.0 + dt / 100, fm, 3 + (i * 5) % 4)
            takes.append((v, starts[i] + off / 1000, g * (1.0 - 0.06 * i)))
        y = dsp.bandpass(dsp.mix(*takes), 330, 7500, 2)
        dry = y.copy()
        return space(y, 1.7, 0.22, 7000, 0.015, CLASSROOM_ER, 0.28, 500, seed + 1, build=0.03), dry
    for i, (sp, fm, dt, off, g) in enumerate(CHOIR):
        curve = np.array([0.0, 1.0, 2.5, 2.0])                        # shout: rises into the stressed vowel
        v = girl(text, seed + 7 * i, sp, 5.0 + dt / 100, fm, 22, 0.1, curve)
        v = shelf_hi(v, 1500, 6.0)                                    # vocal effort: flatter, brighter spectrum
        v = dsp.drive(norm(v, 1.0) * 1.4, 1.4)
        takes.append((norm(v, 1.0), off / 1000, g * (1.0 if i < 3 else 0.6)))   # Paloma and two more lead
    y = dsp.bandpass(dsp.mix(*takes), 330, 7500, 2)
    dry = y.copy()
    return space(y, 2.8, 0.2, 4500, 0.035, CRYPT_ER, 0.25, 250, seed + 1, build=0.03), dry


def vox_monja(text, fx, seed, tw):
    sp = tw.get('speed', 0.84)
    a = say(text, 'ef_dora', sp)
    b = say(text, 'em_santa', sp)
    tm = dtw_map(a, b)
    va = reshape(a, semis=-5.0, formant=-1.6, wobble=18, wobble_rate=1.0, jitter=0.02, shimmer=0.12, seed=seed,
                 fmin=110, fmax=420)
    vb = reshape(b, semis=-9.0, formant=-2.2, wobble=25, wobble_rate=0.8, jitter=0.03, shimmer=0.15, tmap=tm,
                 n_out=len(a), seed=seed + 1, fmin=55, fmax=300)
    n = len(a)
    t = taxis(n)
    # growl: slow irregular glottal crackle under the low voice
    fr = 38 * (1 + 0.2 * snoise(n, 3, seed + 2))
    pulses = np.maximum(0, np.sin(TWO_PI * np.cumsum(fr) / SR)) ** 6
    vb = vb * (0.55 + 0.9 * pulses)
    if fx == 'head':      # right behind your ear: whispered, close, barely any room
        wa = whisper(va, seed + 3)
        wb = whisper(vb, seed + 4)
        y = 0.25 * va + 1.15 * wa + 0.35 * vb + 0.4 * dsp.lowpass(wb, 2500, 2)
        y = shelf_lo(y, 200, 5.0)
        y = dsp.drive(norm(y, 1.0) * 1.6, 1.6)
        y = dsp.peak(y, 3800, 3, 1.2)
        dry = y.copy()
        out = space(y, 0.7, 0.09, 3500, 0.006, [(3.1, 0.25), (6.3, 0.18)], 0.25, 200, seed + 5)
        return dsp.concat(breath_in(0.22, seed + 6, 1.15, 0.22 * np.max(np.abs(y)), 0.3), out), \
            dsp.concat(np.zeros(n_of(0.22), np.float32), dry)
    y = 1.0 * va + 0.62 * vb + 0.28 * whisper(va, seed + 3)
    y = dsp.drive(norm(y, 1.0) * 1.8, 1.7)
    y = dsp.peak(y, 160, 3, 1.0)
    y = dsp.peak(y, 2600, 2.5, 1.5)
    y = dsp.lowpass(y, 7000, 2)
    dry = y.copy()
    return space(y, 1.5, 0.16, 3800, 0.03, CRYPT_ER, 0.22, 180, seed + 6, build=0.02), dry


def vox_operadora(text, fx, seed, tw):
    x = say(text, 'ef_dora', tw.get('speed', 1.0))
    y = reshape(x, semis=1.5, formant=0.6, wobble=4, wobble_rate=0.5, curve=np.array([0.6, 0.0, 0.3, 0.0, 0.8]),
                seed=seed, fmin=120, fmax=480)
    y = shelf_hi(y, 2500, 5.0)            # bright, smiling
    y = dsp.peak(y, 180, -3, 1.0)
    y = compress(y, -20, 4.0, 0.008)
    dry = y.copy()
    z = codec_glitches(y, seed, 3)
    z = phone_line(z, seed, 0.004)
    if fx == 'head':
        tail = space(z, 1.2, 1.0, 3000, 0.02, (), 0, 300, seed + 2, dry=0.0)
        z = send(z, tail, 0.3)
    return z, np.concatenate([np.zeros(n_of(0.08), np.float32), dry])


# ====================================================================== CASE 2: CASA MORALES
# Everything below is only used by casa.* lines (and operadora.casa_aviso, which reuses vox_operadora): the Colegio
# presets above are untouched.
CASA_RESPELL = [
    (r'Temperley', 'Témperlei'),     # rioplatense stress on the first syllable (espeak stresses the last)
    (r'ranked', 'ránket'),           # how a teen from the conurbano says it (espeak: 'raŋkˈed')
]


def say_c(text, voice='ef_dora', speed=0.9):
    for a, b in CASA_RESPELL:
        text = re.sub(a, b, text)
    return say(text, voice, speed)


# ---------------------------------------------------------------- the house, room by room
LIVING_ER = [(3.1, 0.42), (5.3, 0.33), (7.9, 0.27), (10.8, 0.2), (14.1, 0.15), (18.6, 0.1)]
KITCHEN_ER = [(2.4, 0.5), (4.1, 0.44), (6.3, 0.38), (8.8, 0.31), (11.9, 0.25), (15.6, 0.19), (20.3, 0.13), (26.0, 0.09)]
BEDROOM_ER = [(2.7, 0.3), (4.8, 0.24), (7.2, 0.17), (10.1, 0.11)]
HALL_ER = [(2.1, 0.45), (4.3, 0.3), (11.6, 0.32), (23.2, 0.25), (34.8, 0.19), (46.4, 0.14), (58.0, 0.1), (69.6, 0.07)]
CLOSET_ER = [(0.8, 0.62), (1.3, 0.55), (1.9, 0.48), (2.6, 0.4), (3.4, 0.32), (4.3, 0.24), (5.3, 0.17)]
UNDERBED_ER = [(0.6, 0.5), (1.1, 0.42), (1.7, 0.32), (2.5, 0.22), (3.4, 0.14)]
CELLAR_ER = [(6.2, 0.42), (11.5, 0.36), (16.8, 0.31), (23.9, 0.26), (30.7, 0.21), (39.1, 0.16), (51.4, 0.12), (66.0, 0.08)]
PATIO_ER = [(4.8, 0.3), (19.5, 0.26), (42.0, 0.15), (71.0, 0.07)]   # brick floor, house wall, medianera, next house


def casa_room(x, where, seed, wet=None):
    """The Morales house (all mono). Each line is placed where the beat happens (BIBLIA 2.2 h)."""
    if where == 'living':      # 9x7 m, flowered sofa, carpetitas, curtains: short and soft
        return space(x, 0.45, wet or 0.1, 5200, 0.003, LIVING_ER, 0.3, 160, seed)
    if where == 'kitchen':     # green 70s tiles: a brighter, ringing early field
        return space(x, 0.6, wet or 0.12, 7500, 0.002, KITCHEN_ER, 0.34, 200, seed)
    if where == 'bedroom':     # small and full of fabric (the Nona's knitting, Lucía's canopy bed)
        return space(x, 0.32, wet or 0.07, 4200, 0.002, BEDROOM_ER, 0.25, 160, seed)
    if where == 'next_room':   # shouted from the next room, through the open door
        y = dsp.lowpass(x, 5500, 2)
        return space(y, 0.55, wet or 0.2, 3800, 0.008, LIVING_ER, 0.4, 180, seed)
    if where == 'hall':        # upstairs corridor, 2x12 m: flutter between the long walls
        return space(x, 0.85, wet or 0.14, 5000, 0.002, HALL_ER, 0.3, 200, seed)
    if where == 'cellar':      # the 1961 room, 9x9x4 m: brick, sand floor
        return space(x, 1.3, wet or 0.2, 3600, 0.012, CELLAR_ER, 0.3, 140, seed, build=0.02)
    if where in ('patio', 'porch'):   # open air: no tail, a few discrete reflections, the barrio far away
        return space(x, 0.9, wet or (0.035 if where == 'patio' else 0.05), 3200, 0.03, PATIO_ER, 0.42, 250, seed,
                     build=0.06)
    if where == 'closet':      # inside the 2x1 m wardrobe, packed with clothes: tiny box, the fabric eats the highs
        y = space(x, 0.12, 0.2, 2500, 0.0, CLOSET_ER, 0.55, 120, seed)
        y = dsp.peak(y, 215, 4.0, 3.0)
        y = dsp.peak(y, 470, 3.0, 3.0)
        y = dsp.peak(y, 1500, -2.0, 1.5)
        return dsp.lowpass(y, 2900, 2)
    if where == 'underbed':    # Lucía hiding under her bed: slats and mattress 30 cm above her mouth
        y = space(x, 0.1, 0.12, 4000, 0.0, UNDERBED_ER, 0.45, 150, seed)
        y = dsp.peak(dsp.lowpass(y, 5200, 2), 320, 3.0, 2.5)
        return space(y, 0.32, 0.06, 4200, 0.004, BEDROOM_ER, 0.25, 160, seed + 1)
    return x


# ---------------------------------------------------------------- delivery helpers
def effort(y, amount=1.0):
    """Shouting: open jaw (F1 up), flatter spectral tilt, presence, saturated folds, compression."""
    y = dsp.peak(y, 850, 3.0 * amount, 1.0)
    y = shelf_hi(y, 1400, 7.0 * amount)
    y = dsp.peak(y, 3000, 2.5 * amount, 1.6)
    y = dsp.drive(norm(y, 1.0) * (1 + 0.7 * amount), 1 + 0.7 * amount)
    return compress(y, -14, 3.5)


def flatten(x, amount=0.5, seed=0, fmin=110.0, fmax=520.0):
    """Pull the pitch contour toward its median (deadpan / slightly synthetic intonation)."""
    c, f0 = track_f0(x, fmin, fmax)
    v = f0 > 0
    if v.sum() < 6:
        return x
    med = float(np.median(f0[v]))
    ratio = np.where(v, (med / np.maximum(f0, 1.0)) ** amount, 1.0)
    alpha = np.interp(np.arange(len(x)), c, ratio)
    marks, per, vf = pitch_marks(x, c, f0)
    return psola(x, marks, per, vf, len(x), alpha, None, 0.004, 0.03, seed)


def mouth_click(seed, amp=1.0):
    """Lip / tongue smack before an old lady speaks (and the dentures)."""
    r = dsp.rng(seed)
    k = n_of(0.02)
    c = fit(dsp.bandpass(dsp.noise(0.003, 'white', seed) * np.linspace(1, 0, n_of(0.003)) ** 2, 900, 5000, 2), k)
    f = r.uniform(1500, 2400)
    ring = np.sin(TWO_PI * f * taxis(k)) * np.exp(-taxis(k) * 260)
    return norm(norm(c) + 0.5 * ring, amp)


def rough_source(f0, n, seed, jitter=0.06, shimmer=0.3, sub=0.5, breath=0.5, fmax=5000.0):
    """Glottal-ish source for growls: band-limited saw with period jitter, shimmer, sub-harmonic fry, pulsed breath."""
    f0 = np.broadcast_to(np.asarray(f0, np.float64), (n,))
    f = f0 * (1 + jitter * snoise(n, 70, seed + 1))
    ph = np.cumsum(f) / SR + dsp.rng(seed).uniform(0, 1)
    y = np.zeros(n)
    for k in range(1, max(2, int(fmax / max(np.max(f), 1))) + 1):
        y += np.sin(TWO_PI * k * ph) / k
    y *= 1 + shimmer * snoise(n, 45, seed + 2)
    if sub:
        y += sub * 0.6 * np.sign(np.sin(np.pi * ph + 0.3))
    if breath:
        puls = 0.5 * (1 + np.cos(TWO_PI * ph)) ** 2
        y += breath * dsp.highpass(dsp.rng(seed + 3).standard_normal(n).astype(np.float32), 600, 2) * (0.3 + puls) * \
            np.std(y) * 2
    return y.astype(np.float32)


def crackle(n, seed, rate, lo=1500.0, hi=7000.0, size=1.0):
    """Wet spitting crackle: Poisson pops (rate = events/s, number or per-sample) with heavy-tailed sizes."""
    r = dsp.rng(seed)
    lam = np.broadcast_to(np.asarray(rate, np.float64), (n,))
    idx = np.nonzero(r.random(n) < lam / SR)[0]
    imp = np.zeros(n, np.float32)
    np.add.at(imp, idx, (r.pareto(2.2, len(idx)) + 0.3) * r.choice([-1.0, 1.0], len(idx)))
    k = max(8, n_of(0.004 * size))
    kern = r.standard_normal(k) * np.exp(-np.arange(k) / (k / 5))
    y = signal.fftconvolve(imp, kern)[:n].astype(np.float32)
    return dsp.bandpass(y, lo, hi, 2)


def grill_fat(env, seed):
    """Fat on a hot grill riding a voice envelope (0..1): pops denser on the words, a frying hiss, a few big spits."""
    n = len(env)
    pops = crackle(n, seed, 35 + 320 * env, 1800, 8000, 1.0)
    spits = crackle(n, seed + 1, 3 + 14 * env, 700, 3200, 3.0)
    hiss = dsp.highpass(dsp.noise(n / SR, 'white', seed + 2)[:n], 3500, 2)
    flick = np.abs(dsp.lowpass(dsp.rng(seed + 3).standard_normal(n).astype(np.float32), 220, 2))
    hiss = hiss * (0.25 + flick / (np.max(flick) + 1e-9)) * (0.25 + env)
    return norm(pops) + 0.7 * norm(spits) + 0.22 * norm(hiss)


def perform(chunks, take, seed, size=1.0):
    """Assemble a line from directed chunks: [(text, opts)]. opts go to take(text, seed, **kw) except:
    gap (s of silence after), gain (chunk peak), inhale (dur, gain) breath right before, click (lip smack gain),
    sigh (dur, gain) exhale in the gap after, cut (s: stop abruptly that long before the last syllable ends),
    choke (gain of the gasp after a cut). Returns (dry line, list of chunk start samples)."""
    items = []
    pos = 0
    starts = []
    prev_end = 0
    for i, (txt, o) in enumerate(chunks):
        kw = {k: v for k, v in o.items() if k not in ('gap', 'gain', 'inhale', 'click', 'sigh', 'cut', 'choke')}
        y, _ = take(txt, seed + 37 * i, **kw)
        y = norm(y, o.get('gain', 0.9))
        if o.get('cut'):
            e = rms_env(y, 0.01)
            last = int(np.where(e > np.max(e) * 10 ** (-30 / 20))[0][-1])
            y = y[:max(n_of(0.1), last - n_of(o['cut']))].copy()
            y[-n_of(0.005):] *= np.linspace(1, 0, n_of(0.005))
        pre = []
        if o.get('inhale'):
            d, g = o['inhale']
            pre.append(breath_in(d, seed + 11 * i + 1, size, g, 0.25))
        if o.get('click'):
            pre.append(np.concatenate([mouth_click(seed + 13 * i, o['click']), np.zeros(n_of(0.06), np.float32)]))
        if pre:
            p = np.concatenate([np.concatenate([q, np.zeros(n_of(0.03), np.float32)]) for q in pre])
            st = max(prev_end, pos - len(p))
            items.append((p, st))
            pos = st + len(p)
        items.append((y, pos))
        starts.append(pos)
        end = pos + len(y)
        if o.get('choke'):
            g = breath_in(0.11, seed + 17 * i, 0.85, o['choke'], 0.0)
            g = dsp.highpass(g, 900, 2)
            items.append((g, end + n_of(0.03)))
            end += n_of(0.03) + len(g)
        if o.get('sigh'):
            d, g = o['sigh']
            s = breath_out(d, seed + 19 * i, size, g, 0.2)
            items.append((s, end + n_of(0.08)))
            end += n_of(0.08) + len(s)
        prev_end = end
        pos = end + n_of(o.get('gap', 0.0))
    total = max(s + len(x) for x, s in items)
    buf = np.zeros(total, np.float32)
    for x, s in items:
        buf[s:s + len(x)] += x
    return buf, starts


def chunks_for(text, tw):
    return tw.get('chunks') or [(text, {})]


# ---------------------------------------------------------------- Marta: the mum
def marta_take(text, seed, speed=1.08, semis=0.6, curve=None, shout=0.0, shaky=1.0, breathy=0.06, flat=0.0):
    """ef_dora, natural and nervous: fast, a little unsteady in pitch, a flustered breathy edge."""
    x = say_c(text, 'ef_dora', speed)
    if flat:
        x = flatten(x, flat, seed + 9)
    y = reshape(x, semis=semis, formant=0.25 + 0.3 * shout, wobble=16 * shaky, wobble_rate=3.2, tremor=0.006 * shaky,
                tremor_rate=6.4, jitter=0.007, shimmer=0.05, curve=None if curve is None else np.asarray(curve, float),
                seed=seed, fmin=120, fmax=520)
    y = dsp.highpass(y, 90, 2)
    y = y + breathy * whisper(y, seed + 1)
    y = dsp.peak(y, 3000, 2.0, 1.4)
    y = effort(y, shout) if shout else compress(y, -18, 2.5)
    return y, x


CALL = [   # Marta's call (casa.marta.llamada), phrase by phrase: (text, direction)
    ('Hola...', dict(speed=1.0, curve=[0.5, 1.2], gap=0.32)),
    ('¿es la línea de los exorcistas?', dict(speed=1.08, curve=[0, 0, 0.5, 2.0], gap=0.32)),
    ('Perdón la hora.', dict(speed=1.12, gap=0.3)),
    ('Es mi perro...', dict(speed=1.06, gap=0.2)),
    ('Choripán...', dict(speed=1.0, gap=0.18, gain=0.8)),
    ('camina raro.', dict(speed=1.06, gap=0.3)),
    ('No, no, el perro no.', dict(speed=1.2, gap=0.1)),
    ('Mi hija.', dict(speed=1.08, gap=0.42)),
    ('Bueno...', dict(speed=1.0, gap=0.18, curve=[0, -0.6])),
    ('los dos, no sé.', dict(speed=1.12, gap=0.45)),
    ('Y la muñeca...', dict(speed=1.05, gap=0.22)),
    ('la compré en la feria de San Telmo, re barata.', dict(speed=1.12, gap=0.35)),
    ('Pasaje Las Glicinas, mil novecientos sesenta y uno.', dict(speed=1.08, gap=0.35)),
    ('Por favor, venga rápido...', dict(speed=1.08, curve=[0.5, 1.5, 1.0], gap=1.0)),
    ('y el perro.', dict(speed=1.0, gap=0.4, gain=0.8)),
    # El Eco made this call with Marta's voice (BIBLIA 2.2 b): the last phrase comes out a touch too flat, and the
    # line glitches once. Barely there: it reads as deadpan comedy first.
    ('El perro está raro.', dict(speed=0.98, flat=0.65, gain=0.85, curve=[0, 0, -0.5])),
]


def vox_marta(text, fx, seed, tw, lid=''):
    if fx == 'phone':
        y, _ = perform(CALL, marta_take, seed)
        y = add_breaths(y, seed + 50, 1.0, 'scared', 0.24)
        dry = y.copy()
        z = codec_glitches(y, seed + 3, 2)
        return phone_line(z, seed), np.concatenate([np.zeros(n_of(0.08), np.float32), dry])
    y, _ = perform(chunks_for(text, tw), marta_take, seed)
    y = add_breaths(y, seed + 50, 1.0, 'scared', 0.18)
    return casa_room(y, tw.get('place', 'living'), seed, tw.get('wet')), y


# ---------------------------------------------------------------- Jorge: the dad, king of the asado
def jorge_take(text, seed, speed=0.92, semis=-2.0, curve=None, shout=0.0, hoarse=0.17):
    """em_alex: big, jovial, low, a bit hoarse (rasp band + a little fold saturation)."""
    x = say_c(text, 'em_alex', speed)
    y = reshape(x, semis=semis, formant=-0.8, wobble=10, wobble_rate=1.6, jitter=0.012, shimmer=0.08,
                curve=None if curve is None else np.asarray(curve, float), seed=seed, fmin=60, fmax=330)
    y = y + hoarse * dsp.bandpass(whisper(y, seed + 1), 900, 5200, 2)
    y = dsp.highpass(y, 75, 2)
    y = dsp.peak(y, 170, 3.0, 1.0)          # chest and belly
    y = dsp.peak(y, 2500, 1.5, 1.4)
    y = dsp.drive(norm(y, 1.0) * 1.25, 1.25)
    y = effort(y, shout) if shout else compress(y, -18, 2.5)
    return y, x


def vox_jorge(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), jorge_take, seed, 1.2)
    return casa_room(y, tw.get('place', 'patio'), seed, tw.get('wet')), y


def jorge_demon_take(text, seed, speed=0.88, curve=None, shout=0.0, demon=0.7):
    """Jorge with AZAMEL inside: his voice + em_santa -5 st (DTW-aligned to his words), grit."""
    a = say_c(text, 'em_alex', speed)
    b = say_c(text, 'em_santa', speed)
    tm = dtw_map(a, b)
    cv = None if curve is None else np.asarray(curve, float)
    va = reshape(a, semis=-2.5, formant=-0.9, wobble=14, wobble_rate=1.2, jitter=0.018, shimmer=0.11, curve=cv,
                 seed=seed, fmin=60, fmax=330)
    vb = reshape(b, semis=-5.0, formant=-1.4, wobble=22, wobble_rate=0.9, jitter=0.026, shimmer=0.14, curve=cv,
                 tmap=tm, n_out=len(a), seed=seed + 1, fmin=45, fmax=260)
    vb = dsp.lowpass(vb, 3600, 2)
    y = norm(va) + demon * 0.85 * norm(vb) + 0.12 * whisper(va, seed + 2)
    y = dsp.highpass(y, 60, 2)
    y = dsp.peak(y, 150, 3.0, 1.0)
    y = dsp.drive(norm(y, 1.0) * (1.5 + 0.5 * demon), 1.5 + 0.5 * demon)
    if shout:
        y = effort(y, shout)
    else:
        y = compress(y, -18, 3.0)
    return dsp.lowpass(y, 7500, 2), a


def vox_jorge_poseido(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), jorge_demon_take, seed, 1.2)
    # the blue fire right under his words: fat spitting on the grill, denser on every syllable
    e = uniform_filter1d(rms_env(y, 0.03), n_of(0.05))
    e = (e / (np.max(e) + 1e-9)) ** 0.8
    lead, tail = n_of(0.12), n_of(0.25)
    env = np.concatenate([np.linspace(0.05, e[0], lead), e, np.linspace(e[-1], 0.0, tail)]).astype(np.float32)
    fat = grill_fat(env, seed + 40)
    v = np.concatenate([np.zeros(lead, np.float32), y, np.zeros(tail, np.float32)])
    fat = fat * dsp.env_points(len(fat), [(0, 0), (0.03, 1), (0.95, 1), (1, 0)])
    mixd = v + 0.2 * fat * np.max(np.abs(v)) / (np.max(np.abs(fat)) + 1e-9)
    z = casa_room(mixd, 'patio', seed)
    # outdoors, yet a dark tail that has no business in a patio
    tail_sig = dsp.lowpass(space(v, 2.2, 1.0, 1400, 0.05, (), 0, 120, seed + 5, dry=0.0), 1400, 2)
    return send(z, tail_sig, 0.14), v


# ---------------------------------------------------------------- la Nona Pocha
def nona_take(text, seed, speed=0.78, semis=-2.0, curve=None, old=1.0, loud=1.0):
    """ef_dora -2 st, slow: old rasp, voice tremor, a little deaf-loud (projected, bright, dense)."""
    x = say_c(text, 'ef_dora', speed)
    y = reshape(x, semis=semis, formant=-0.6 * old, wobble=16 * old, wobble_rate=2.0, tremor=0.014 * old,
                tremor_rate=5.2, jitter=0.016 * old, shimmer=0.1 * old,
                curve=None if curve is None else np.asarray(curve, float), seed=seed, fmin=100, fmax=460)
    y = y + 0.16 * old * dsp.bandpass(whisper(y, seed + 1), 1100, 6000, 2)
    y = dsp.tremolo(y, 5.2, 0.14 * old)
    y = dsp.highpass(y, 110, 2)
    y = shelf_hi(y, 1500, 3.5 * loud)
    y = dsp.peak(y, 1100, 2.0 * loud, 1.2)
    y = compress(y, -16, 3.0)
    return y, x


def vox_nona(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), nona_take, seed, 1.0)
    return casa_room(y, tw.get('place', 'bedroom'), seed, tw.get('wet')), y


def nona_shout_take(text, seed, speed=0.92, curve=(2.5, 4.5, 4.0, 3.0), amount=1.0):
    """The same woman SHOUTING: no old-age effect at all, strong and clear (her hero moment)."""
    x = say_c(text, 'ef_dora', speed)
    y = reshape(x, semis=-1.0, formant=-0.3, wobble=8, wobble_rate=2.5, jitter=0.004, shimmer=0.03,
                curve=np.asarray(curve, float), seed=seed, fmin=110, fmax=520)
    y = dsp.highpass(y, 120, 2)
    y = effort(y, amount)
    return y, x


def vox_nona_grito(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), nona_shout_take, seed, 1.0)
    return casa_room(y, tw.get('place', 'hall'), seed, tw.get('wet')), y


def vox_nona_poseida(text, fx, seed, tw, lid=''):
    """AZAMEL in the Nona, whispering at your ear while she holds you in the air: her whisper + a demon layer."""
    sp = tw.get('speed', 0.78)
    a = say_c(text, 'ef_dora', sp)
    b = say_c(text, 'em_santa', sp)
    tm = dtw_map(a, b)
    va = reshape(a, semis=-2.5, formant=-0.8, wobble=25, wobble_rate=1.0, jitter=0.02, shimmer=0.12, seed=seed,
                 fmin=100, fmax=460)
    vb = reshape(b, semis=-8.0, formant=-2.0, wobble=30, wobble_rate=0.8, jitter=0.03, shimmer=0.15, tmap=tm,
                 n_out=len(a), seed=seed + 1, fmin=45, fmax=260)
    wa = whisper(va, seed + 3)
    wb = whisper(vb, seed + 4)
    y = 0.22 * norm(va) + 1.1 * norm(wa) + 0.45 * norm(vb) + 0.35 * norm(dsp.lowpass(wb, 2500, 2))
    y = shelf_lo(y, 220, 5.0)              # lips at your ear: proximity bass
    y = dsp.drive(norm(y, 1.0) * 1.5, 1.5)
    y = dsp.peak(y, 3800, 3.0, 1.2)
    pk = np.max(np.abs(y))
    out = space(y, 0.5, 0.06, 3500, 0.004, [(2.4, 0.25), (4.9, 0.16)], 0.25, 180, seed + 5)
    pre = breath_in(0.3, seed + 6, 1.1, 0.3 * pk, 0.35)
    post = dsp.lowpass(breath_out(0.9, seed + 7, 1.25, 0.22 * pk), 1800, 2)    # the cold exhale on your neck
    gap = np.zeros(n_of(0.04), np.float32)
    return dsp.concat(pre, gap, out, post), dsp.concat(np.zeros(len(pre) + len(gap), np.float32), y)


# ---------------------------------------------------------------- Lucía (8)
def lucia_take(text, seed, speed=0.88, curve=None, wh=0.25, demon=0.0):
    """ef_dora +3 st with a child's tract, soft and shy. demon > 0: a faint em_santa unison under her words."""
    x = say_c(text, 'ef_dora', speed)
    cv = None if curve is None else np.asarray(curve, float)
    y = reshape(x, semis=3.0, formant=1.8, wobble=18, wobble_rate=2.4, tremor=0.004, tremor_rate=6.0, jitter=0.006,
                shimmer=0.05, curve=cv, seed=seed, fmin=110, fmax=480)
    y = (1 - wh) * y + wh * 1.2 * whisper(y, seed + 4)
    y = dsp.highpass(y, 160, 2)
    y = shelf_hi(y, 3500, -2.0)              # shy: little vocal effort
    y = compress(y, -20, 2.0)
    if demon:
        b = say_c(text, 'em_santa', speed)
        vb = reshape(b, semis=-9.0, formant=-2.0, wobble=20, jitter=0.02, shimmer=0.12, curve=cv,
                     tmap=dtw_map(x, b), n_out=len(x), seed=seed + 1, fmin=45, fmax=260)
        y = norm(y) + demon * norm(dsp.lowpass(vb, 2200, 2))
    return y, x


def vox_lucia(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), lucia_take, seed, 0.8)
    y = add_breaths(y, seed + 50, 0.8, tw.get('breaths', 'scared'), 0.22)
    return casa_room(y, tw.get('place', 'bedroom'), seed, tw.get('wet')), y


def lucia_double_take(text, seed, speed=0.84, curve=None):
    """Lucía on the ceiling: her small voice in exact unison with em_santa -9 st. Both voices carry the words: the
    girl the consonants and the top, the demon the vowels underneath."""
    a = say_c(text, 'ef_dora', speed)
    b = say_c(text, 'em_santa', speed)
    tm = dtw_map(a, b)
    cv = None if curve is None else np.asarray(curve, float)
    va = reshape(a, semis=3.0, formant=1.8, wobble=12, wobble_rate=2.0, jitter=0.006, shimmer=0.05, curve=cv,
                 seed=seed, fmin=110, fmax=480)
    vb = reshape(b, semis=-9.0, formant=-2.0, wobble=18, wobble_rate=0.8, jitter=0.024, shimmer=0.13, curve=cv,
                 tmap=tm, n_out=len(a), seed=seed + 1, fmin=45, fmax=260)
    va = dsp.highpass(va, 180, 2)
    vb = dsp.drive(norm(dsp.lowpass(vb, 3400, 2)) * 1.6, 1.6)
    y = norm(va) + 0.8 * norm(vb) + 0.2 * whisper(va, seed + 2)
    y = dsp.peak(y, 140, 2.5, 1.0)
    return compress(y, -18, 2.5), a


def vox_lucia_doble(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), lucia_double_take, seed, 0.8)
    z = casa_room(y, 'hall', seed, 0.16)
    tail = dsp.lowpass(space(y, 2.4, 1.0, 2400, 0.04, (), 0, 200, seed + 3, dry=0.0), 2400, 2)
    return send(z, tail, 0.16), y


# ---------------------------------------------------------------- Toti (15), in the wardrobe
def toti_take(text, seed, speed=1.08, curve=None, shout=0.0):
    x = say_c(text, 'em_alex', speed)
    y = reshape(x, semis=2.0, formant=0.9, wobble=12, wobble_rate=2.5, jitter=0.008, shimmer=0.06,
                curve=None if curve is None else np.asarray(curve, float), seed=seed, fmin=70, fmax=380)
    y = dsp.highpass(y, 110, 2)
    y = effort(y, shout) if shout else compress(y, -18, 2.5)
    return y, x


def vox_toti(text, fx, seed, tw, lid=''):
    y, _ = perform(chunks_for(text, tw), toti_take, seed, 0.95)
    return casa_room(y, tw.get('place', 'closet'), seed, tw.get('wet')), y


# ---------------------------------------------------------------- Choripán speaks
def chori_take(text, seed, speed=0.86, semis=-5.0, curve=None, sub=0.45, grit=1.8):
    """em_santa -5 st with an octave-down layer (-17 st, low-passed), grit."""
    x = say_c(text, 'em_santa', speed)
    cv = None if curve is None else np.asarray(curve, float)
    v = reshape(x, semis=semis, formant=-1.5, wobble=18, wobble_rate=1.4, jitter=0.02, shimmer=0.12, curve=cv,
                seed=seed, fmin=45, fmax=260)
    o = reshape(x, semis=semis - 12, formant=-2.5, wobble=25, wobble_rate=1.0, jitter=0.03, shimmer=0.15, curve=cv,
                seed=seed + 1, fmin=45, fmax=260)
    y = norm(v) + sub * norm(dsp.lowpass(o, 1600, 2)) + 0.12 * whisper(v, seed + 2)
    y = dsp.highpass(y, 45, 2)
    y = dsp.drive(norm(y, 1.0) * grit, grit)
    y = dsp.peak(y, 2600, 2.5, 1.4)
    return compress(y, -16, 3.0), x


def wet_growl(dur, seed):
    """A sausage dog's growl out of a throat far too big: rough fry source, long dark tract, jowl flutter, two
    surges, saliva crackle and a sub rumble an octave down."""
    n = n_of(dur)
    f0 = dsp.env_points(n, [(0, 64), (0.3, 76), (0.6, 68), (1, 54)]) * (1 + 0.08 * snoise(n, 12, seed))
    src = rough_source(f0, n, seed, jitter=0.07, shimmer=0.3, sub=0.6, breath=0.6)
    tract = sum(10 ** (g / 20) * dsp.bandpass(src, f - bw, f + bw, 2)
                for f, bw, g in [(430, 90, 0), (790, 120, -4), (1900, 200, -12), (2750, 260, -16)])
    tract = tract + 0.35 * dsp.bandpass(src, 60, 260, 2)
    t = taxis(n)
    flutter = 1 + 0.35 * np.sin(TWO_PI * 23 * t + 3 * snoise(n, 2, seed + 1))
    e = dsp.env_points(n, [(0, 0), (0.12, 0.7), (0.35, 1.0), (0.5, 0.72), (0.68, 0.95), (0.88, 0.55), (1, 0)])
    y = dsp.drive(norm(tract) * 2.5, 2.5) * e * flutter
    wet = crackle(n, seed + 3, 25 + 60 * e, 1200, 5000, 1.5) * e
    rum = np.sin(TWO_PI * np.cumsum(f0 / 2) / SR) * e
    return norm(norm(y) + 0.3 * norm(wet) + 0.3 * rum).astype(np.float32)


def vox_choripan(text, fx, seed, tw, lid=''):
    """'¿Quién es un buen chico?' (the sing-song you use with a dog, from the demon) ... wet growl ... 'YO NO.'"""
    a_txt, b_txt = [p.strip() for p in text.split('...')]
    A, _ = chori_take(a_txt, seed, 0.86, -5.0, [0.5, 2.0, 1.0, 3.5], 0.4, 1.8)
    B, _ = chori_take(b_txt, seed + 1, 0.74, -6.0, [0.5, -1.5], 0.75, 2.4)
    G = wet_growl(1.1, seed + 2)
    A, B = norm(A, 0.8), norm(B, 1.0)
    tg = len(A) / SR + 0.22
    tb = tg + len(G) / SR + 0.2
    y = dsp.mix((A, 0.0, 1.0), (G, tg, 0.6), (B, tb, 1.0))
    z = casa_room(y, 'hall', seed, 0.12)
    tail = dsp.lowpass(space(y, 1.8, 1.0, 1600, 0.04, (), 0, 100, seed + 3, dry=0.0), 1600, 2)
    return send(z, tail, 0.12), y


# ---------------------------------------------------------------- the spirit box in Lucía's room
# Same voice family and speaker as tools/audio/snd_tools.py (spirit_box.voice): ef_dora ghost voice (whisper layer,
# a faint octave below, slow wobble, a little distant room), the same radio broadcasts in the sweep, the same band.
_RADIO_C = None


def _say_plain(text, voice, speed):
    """snd_tools.say (no respelling): same TTS cache entries as the spirit box broadcasts."""
    y = dsp.tts(text, voice, speed)
    y = dsp.highpass(y, 60, 2)
    y = dsp.trim(y, -46, 0.03)
    return norm(dsp.fade(y, 0.003, 0.012), 0.8)


def radio_source_c():
    global _RADIO_C
    if _RADIO_C is None:
        a = _say_plain('Y ahora, el pronóstico para Córdoba y alrededores: cielo nublado, frío.', 'em_alex', 1.1)
        b = _say_plain('¡Llame ya! Ofertas en electrodomésticos, todo el mes de junio.', 'ef_dora', 1.15)
        c = _say_plain('Gol, gol, gol de Talleres, señores.', 'em_santa', 1.2)
        n = n_of(1.5)
        t = taxis(n)
        mus = np.zeros(n, np.float32)
        for j, fr in enumerate([196.0, 246.94, 293.66, 392.0, 329.63]):
            ph = np.cumsum(fr * (1 + 0.003 * np.sin(TWO_PI * 5 * t))) / SR
            s = sum(np.sin(TWO_PI * k * ph) / k ** 1.2 for k in range(1, int(5000 / fr) + 1))
            mus += s.astype(np.float32) * (0.6 + 0.4 * (j % 2))
        mus = mus * (0.6 + 0.4 * np.abs(np.sin(TWO_PI * 2.2 * t)))
        _RADIO_C = [a, b, c, norm(mus)]
    return _RADIO_C


def sb_radio_band(x):
    y = dsp.bandpass(x, 280, 4200, 2)
    y = dsp.peak(y, 1250, 4, 1.4)
    y = dsp.drive(y * 1.6, 1.8)
    y = dsp.bitcrush(y, 11, 2)
    return dsp.lowpass(y, 4800, 4)


def sb_voice_band(x):
    y = dsp.bandpass(x, 190, 6200, 2)
    y = dsp.peak(y, 1250, 3, 1.4)
    y = dsp.peak(y, 3000, 3, 1.2)
    y = dsp.drive(y * 1.4, 1.5)
    y = dsp.bitcrush(y, 12, 2)
    return dsp.lowpass(y, 6800, 4)


def sb_sweep(dur, seed, voices=0.3, seg=(0.06, 0.11)):
    """Spirit-box FM sweep (as snd_tools.sweep_static): static / carrier whistles / chopped broadcasts per channel,
    tuner clicks between them. Returns (signal, channel boundary times)."""
    r = dsp.rng(seed)
    n = n_of(dur)
    y = np.zeros(n, np.float32)
    src = radio_source_c()
    bounds = []
    t = 0.0
    k = 0
    while t < dur:
        d = r.uniform(*seg)
        m = n_of(d)
        kind = r.choice(['static', 'whistle', 'voice', 'static', 'hollow'], p=[0.32, 0.18, voices, 0.0, 0.5 - voices])
        w = dsp.rng(seed + k).standard_normal(m).astype(np.float32)
        if kind == 'static':
            g = np.abs(dsp.lowpass(dsp.rng(seed + 100 + k).standard_normal(m + 4096).astype(np.float32), 2500, 2)[4096:])
            s = w * r.uniform(0.6, 1.0) * (0.7 + 0.3 * g ** 1.5 / (np.mean(g ** 1.5) + 1e-9))
        elif kind == 'whistle':
            f0 = r.uniform(500, 3000)
            s = 0.55 * dsp.osc(dsp.glide(f0, f0 * r.uniform(0.7, 1.4), d), d)[:m] + 0.5 * w
        elif kind == 'voice':
            x = src[int(r.integers(0, len(src)))]
            a = int(r.integers(0, max(1, len(x) - m)))
            s = fit(x[a:a + m], m)
            if r.random() < 0.35:
                s = s[::-1].copy()
            s = norm(s) * r.uniform(0.6, 1.0) + 0.35 * w
        else:
            s = 0.3 * dsp.lowpass(w, 2500, 2) + 0.15 * dsp.osc(r.uniform(150, 400), d)[:m]
        gap = r.uniform(0.003, 0.012) if r.random() < 0.7 else 0.0
        e = np.interp(np.arange(m) / SR, [0, gap, gap + 0.002, d - 0.003, d], [0, 0, 1, 1, 0])
        s = fit(s, m) * e * r.uniform(0.35, 1.0)
        a0 = n_of(t)
        L = min(m, n - a0)
        y[a0:a0 + L] += s[:L]
        kc = n_of(0.0012)
        cl = dsp.highpass(dsp.rng(seed + 500 + k).standard_normal(kc).astype(np.float32) * np.linspace(1, 0, kc) ** 2,
                          800, 2)
        L = min(kc, n - a0)
        y[a0:a0 + L] += 0.35 * norm(cl)[:L]
        bounds.append(t)
        t += d
        k += 1
    y = y * (0.85 + 0.15 * snoise(n, 3, seed + 7))
    return sb_radio_band(y), bounds


def ghost_c(v, seed):
    """snd_tools.ghost_voice on an already spoken chunk: breathy, a faint octave below, slow wobble, distant room."""
    w = whisper(v, seed)
    lo = dsp.pitch_shift(v, -12)
    y = norm(v) + 0.2 * norm(w) + 0.1 * norm(fit(lo, len(v)))
    y = wobble_delay(y, 0.9, 1.0, seed, 0.8)
    y = space(y, 1.0, 0.1, 3500, 0.025, CHAPEL_ER, 0.1, 150, seed)
    return norm(dsp.trim(y, -50, 0.12))


def split_syllables(x, k):
    """Cut a take into k pieces: at its k-1 longest pauses, else at the deepest loudness dips."""
    if k <= 1:
        return [x]
    pz = sorted(pauses(x, 0.06, -34), key=lambda p: -(p[1] - p[0]))[:k - 1]
    if len(pz) == k - 1:
        cuts = sorted((a + b) // 2 for a, b in pz)
    else:
        e = uniform_filter1d(rms_env(x, 0.012), n_of(0.02))
        pk, pr = signal.find_peaks(-e, distance=n_of(0.08), prominence=0)
        inner = [(p, q) for p, q in zip(pk, pr['prominences']) if n_of(0.06) < p < len(x) - n_of(0.06)]
        cuts = sorted(p for p, _ in sorted(inner, key=lambda z: -z[1])[:k - 1])
    edges = [0] + list(cuts) + [len(x)]
    return [dsp.trim(x[edges[i]:edges[i + 1]], -40, 0.03) for i in range(len(edges) - 1)]


def vox_spirit(text, fx, seed, tw, lid=''):
    """Syllables picked out of the sweep one station at a time: static, a syllable (the sweep ducks under it), static,
    the next syllable... Each syllable is its own 'lock' with hard tuner edges."""
    r = dsp.rng(seed)
    groups = [g.strip() for g in text.split('...') if g.strip(' .')]
    v = say_c(text, 'ef_dora', tw.get('speed', 0.9))
    syl = split_syllables(v, len(groups))
    syl = [ghost_c(s, seed + 7 * i) for i, s in enumerate(syl)]
    gaps = tw.get('gaps') or [0.3] * (len(syl) - 1)
    pre, post = r.uniform(0.32, 0.42), 0.3
    starts = []
    t = pre
    for i, s in enumerate(syl):
        starts.append(t)
        t += len(s) / SR + (gaps[i] if i < len(gaps) else 0.0)
    total = t + post
    st, bounds = sb_sweep(total, seed + 50, 0.3)
    n = len(st)
    vm = np.zeros(n, np.float32)
    vo = np.zeros(n, np.float32)
    dry = np.zeros(n, np.float32)
    for i, (s, t0) in enumerate(zip(syl, starts)):
        a = n_of(t0)
        L = min(len(s), n - a)
        e = rms_env(s, 0.01)
        voiced = np.where(e > np.max(e) * 10 ** (-28 / 20))[0]
        end = int(voiced[-1]) + n_of(0.06) if len(voiced) else L
        g = np.zeros(L, np.float32)                     # tuner lock: hard 4 ms edges
        g[:min(L, end)] = 1.0
        g = uniform_filter1d(g, n_of(0.004))
        col = sb_voice_band(s)[:L] * r.uniform(0.85, 1.0)
        if r.random() < 0.5:
            col = dsp.lowpass(col, r.uniform(4800, 6200), 2)
        vo[a:a + L] += col * g
        dry[a:a + L] += s[:L] * g
        vm[max(0, a - n_of(0.02)):a + min(L, end) - n_of(0.04)] = 1.0
    duck = 1 - 0.94 * uniform_filter1d(vm, n_of(0.04))
    chop = np.ones(n, np.float32)
    for b in bounds:
        if r.random() < 0.3:
            a0 = n_of(b)
            chop[a0:a0 + n_of(0.01)] = r.uniform(0.6, 0.8)
    chop = uniform_filter1d(chop, n_of(0.002))
    y = norm(st) * duck * 0.34 + norm(vo) * chop
    y = y * np.interp(np.arange(n) / SR, [0, 0.01, total - 0.05, total], [0, 1, 1, 0])
    z = casa_room(y.astype(np.float32), 'bedroom', seed, 0.05)
    return z, dry


# ---------------------------------------------------------------- Tomi's VOD on Lucía's tablet
_SYLC = {}


def syllables(text, voice, speed, k):
    key = (text, voice, speed, k)
    if key not in _SYLC:
        _SYLC[key] = split_syllables(say_c(text, voice, speed), k)
    return _SYLC[key]


def laugh_m(seed, count=6, semis=4.0):
    """The streamer's laugh: breathy 'ja' syllables falling in pitch and slowing down, a wheezy inhale at the end."""
    r = dsp.rng(seed)
    syl = syllables('ja ja ja ja', 'em_alex', 1.05, 4)
    parts = []
    t = 0.0
    for k in range(count):
        s0 = syl[k % len(syl)]
        d = r.uniform(0.12, 0.15) + 0.012 * k
        g = fit(s0, n_of(d)) * dsp.env_points(n_of(d), [(0, 0), (0.06, 1.0), (0.5, 0.8), (1, 0)])
        st = semis + 1.2 - k * r.uniform(0.6, 0.9) + r.normal(0, 0.3)
        v = reshape(g, semis=st, formant=0.4, wobble=25, wobble_rate=6.0, seed=seed + k, fmin=70, fmax=420)
        v = 0.6 * v + 0.7 * whisper(v, seed + 40 + k)
        parts.append((norm(v, 1.0 - 0.08 * k), t, 1.0))
        t += d + r.uniform(0.035, 0.06) + 0.01 * k
    parts.append((breath_in(0.26, seed + 9, 0.9, 0.5, 0.6), t + 0.03, 1.0))
    return dsp.mix(*parts)


def tablet(x, seed):
    """The VOD: streamer USB mic (hard compression, the San Lázaro corridor behind him), video codec, and the tablet's
    tiny speaker on Lucía's bed (no bass, peaky, buzzes when loud)."""
    y = compress(x, -24, 4.0, 0.006)
    y = space(y, 1.6, 0.12, 4000, 0.02, CRYPT_ER, 0.12, 300, seed + 1)      # hospital corridor in the stream
    y = dsp.lowpass(y, 11000, 4)                                            # streaming codec
    n = len(y)
    y = y + 0.006 * dsp.bandpass(dsp.noise(n / SR, 'pink', seed + 2)[:n], 300, 8000, 2) * np.max(np.abs(y)) * 4
    y = dsp.highpass(y, 520, 4)
    y = dsp.lowpass(y, 7600, 4)
    y = dsp.peak(y, 1100, 4.0, 1.5)
    y = dsp.peak(y, 3300, 5.0, 2.0)
    y = dsp.peak(y, 750, -3.0, 1.0)
    y = dsp.drive(norm(y, 1.0) * 1.7, 1.7)
    buzz = dsp.highpass(np.sign(y) * np.maximum(np.abs(y) - 0.7, 0), 2000, 2)    # grille rattle on peaks
    return (y + 0.5 * buzz).astype(np.float32)


def vox_tomi(text, fx, seed, tw, lid=''):
    head = text.split(',')[:-1]
    words = ','.join(head) + ','
    x = say_c(words, 'em_alex', 1.1)
    v = reshape(x, semis=1.0, formant=0.3, wobble=12, wobble_rate=2.0, jitter=0.006, shimmer=0.05,
                curve=np.array([1.0, 2.0, 0.5, 2.5, 1.5]), seed=seed, fmin=70, fmax=380)
    v = dsp.highpass(v, 90, 2)
    v = shelf_hi(v, 2000, 3.0)                    # hyped streamer: bright, forward
    lg = laugh_m(seed + 3)
    y = dsp.concat(norm(v, 0.9), dsp.silence(0.06), norm(lg, 0.8))
    z = tablet(y, seed)
    return casa_room(z, 'bedroom', seed, 0.06), y


# ---------------------------------------------------------------- per-line direction (BIBLIA 2.2 h, k, l, m)
def C(text, **o):
    return (text, o)


CASA_DIRECTION = {
    # 1. arrival: Marta at the door in curlers; Jorge on the sofa; the Nona with the soap opera blaring
    'casa.marta.hola': dict(place='porch', chunks=[
        C('Ay, gracias a Dios.', speed=1.02, curve=[1.5, 0.5, -0.5], gap=0.14),
        C('¿Lo mandó el Padre Ignacio?', speed=1.12, curve=[0, 0, 0.5, 1.8], gap=0.12),
        C('Pase, pase...', speed=1.15, gap=0.34),
        C('y límpiese los pies.', speed=1.0, semis=0.2, curve=[0, 0, -0.8], gain=0.85)]),
    'casa.jorge.humedad': dict(place='living', chunks=[C('Es la humedad, flaco.', speed=0.88, curve=[0.5, 0, 0.8, -0.8])]),
    'casa.jorge.mucha_humedad': dict(place='living', chunks=[
        C('Mucha humedad.', speed=0.8, curve=[0, -0.5, -1.2], inhale=(0.3, 0.3), gain=0.8)]),
    'casa.nona.mate': dict(place='living', chunks=[
        C('¿Querés un mate, nene?', speed=0.8, curve=[1.5, 1.5, 2.5, 3.0], loud=1.3, click=0.25)]),
    'casa.jorge.carbon': dict(place='living', chunks=[
        C('Bueno,', speed=0.95, gap=0.14), C('yo me voy a buscar carbón para el asado.', speed=0.98, gap=0.2),
        C('Ya vuelvo.', speed=0.95, curve=[0.8, 0])]),
    # 2. the family chat
    'casa.marta.chat': dict(place='living', chunks=[C('Mire, mire el grupo de la familia...', speed=1.12)]),
    'casa.marta.no_celular': dict(place='living', chunks=[
        C('Lucía no tiene celular.', speed=0.94, semis=0.3, shaky=2.0, breathy=0.22, curve=[0.5, 0, -0.8],
          inhale=(0.28, 0.4), gain=0.8)]),
    'casa.marta.telefono': dict(place='living', chunks=[
        C('¿Yo?', speed=1.0, curve=[0, 2.5], gap=0.28), C('Nos cortaron el teléfono en marzo.', speed=1.1)]),
    # 3. Lucía's room
    'casa.lucia.perro': dict(place='underbed', chunks=[
        C('Ofelia dice que tu perro...', speed=0.86, gap=0.42),
        C('digo, nuestro perro...', speed=0.8, demon=0.16, gap=0.36),
        C('tiene hambre.', speed=0.82, curve=[0, -0.5])]),
    'casa.spirit.azamel': dict(speed=0.9, gaps=[0.3, 0.36]),
    'casa.spirit.al_perro': dict(speed=0.9, gaps=[0.32, 0.26]),
    'casa.spirit.nunca': dict(speed=0.9, gaps=[0.42]),
    'casa.spirit.temperley': dict(speed=0.9, gaps=[0.62]),
    # 4. the kitchen
    'casa.marta.sillas': dict(place='living', chunks=[
        C('¡Esas sillas eran de mi suegra!', shout=0.85, speed=1.08, curve=[2, 4, 3, 3.5, 2], inhale=(0.2, 0.4))]),
    'casa.nona.son_mias': dict(place='next_room', chunks=[
        C('¡Todavía son mías!', speed=0.9, curve=[3, 5, 4.5, 5.5, 3.5], inhale=(0.22, 0.5))]),
    # 5. the calm beat
    'casa.nona.esperando': dict(place='bedroom', chunks=[
        C('A vos', speed=0.78, click=0.22, gap=0.14), C('te estaba esperando, nene.', speed=0.76, curve=[0.3, 0, 0, -0.8])]),
    'casa.nona.guardame': dict(place='bedroom', chunks=[
        C('Tomá,', speed=0.8, gap=0.16), C('guardame esto.', speed=0.78, curve=[0.5, 0, -0.5])]),
    'casa.marta.llamalo': dict(place='bedroom', chunks=[
        C('Llamalo vos, decile Choripán,', speed=1.1, gap=0.12), C('capaz a vos te hace caso.', speed=1.12, curve=[0, 0.5, -0.5])]),
    # 8. the wardrobe
    'casa.toti.ocupado': dict(place='closet', chunks=[
        C('¡Ocupado!', shout=1.0, speed=1.05, curve=[3, 4.5, 3], gap=0.1),
        C('¡Estoy en ranked!', shout=0.8, speed=1.12, curve=[2.5, 3, 4, 2])]),
    'casa.toti.callate': dict(place='closet', chunks=[C('¡Callate, Chori!', shout=0.85, speed=1.12, curve=[3, 4, 3, 2])]),
    # 9-10. fetch, the grill
    'casa.marta.tirale': dict(place='hall', wet=0.2, chunks=[
        C('¡Tirale algo!', shout=1.0, speed=1.05, curve=[3, 5, 4], inhale=(0.18, 0.5))]),
    'casa.marta.choripan': dict(place='kitchen', chunks=[
        C('¡Lo único que lo calma es un choripán!', shout=0.75, speed=1.12, curve=[2, 3, 2.5, 3.5, 2.5], gap=0.22,
          inhale=(0.16, 0.4)),
        C('¡Tomá!', shout=1.0, speed=1.0, curve=[3, 5], inhale=(0.12, 0.45))]),
    # 11. Jorge
    'casa.jorge.llegue': dict(place='patio', chunks=[
        C('¡Llegué!', speed=0.95, curve=[1.5, 2.5], gap=0.2, inhale=(0.35, 0.45)),
        C('No había carbón en lo de Rubén,', speed=1.02, gap=0.1),
        C('tuve que ir hasta la', speed=1.05, cut=0.03, choke=0.7)]),
    'casa.jorge.jugoso': dict(chunks=[C('¿Jugoso o a punto, pibe?', speed=0.86, curve=[1.5, 2.5, 1.0, 2.5], demon=0.55)]),
    'casa.jorge.es_la_humedad': dict(chunks=[
        C('Es la humedad...', speed=0.8, demon=0.5, curve=[0, -0.5, -1.2], gap=0.6, gain=0.65),
        C('¡Es la humedad!', shout=1.0, speed=0.9, demon=1.0, curve=[2.5, 4.5, 4, 2.5])]),
    'casa.jorge.falta_sal': dict(chunks=[C('¡Le falta sal!', shout=1.0, speed=0.8, demon=1.1, curve=[2, 4, 3, 1])]),
    'casa.marta.chorizo': dict(place='patio', chunks=[
        C('¡Te dije que no comas tanto chorizo!', shout=0.6, speed=1.12, curve=[2, 3, 2, 3, 1.5], inhale=(0.18, 0.35))]),
    # 13-14. Lucía, the slipper
    'casa.lucia.voces': dict(chunks=[C('Él te llamó.', speed=0.84, gap=0.45), C('Él tiene muchas voces.', speed=0.82)]),
    'casa.nona.atorrante': dict(place='hall', chunks=[
        C('¡Salí de mi nieta,', speed=0.95, curve=[3.5, 5.5, 4.5, 4], gap=0.06, inhale=(0.2, 0.55)),
        C('atorrante!', speed=0.9, curve=[5, 6, 3.5])]),
    'casa.nona.aca': dict(place='hall', chunks=[
        C('¡Acá!', speed=0.9, curve=[4, 6], gap=0.24, inhale=(0.2, 0.55)),
        C('¡Vení con la vieja, como antes!', speed=0.98, curve=[4, 5, 4, 5, 3.5], gap=0.2, inhale=(0.16, 0.45)),
        C('¡Dejala a la nena!', speed=0.95, curve=[4.5, 5.5, 4.5, 3], inhale=(0.16, 0.45))]),
    'casa.lucia.liberada': dict(place='hall', breaths='sob', chunks=[
        C('Ofelia tenía miedo...', speed=0.84, wh=0.35, gap=0.5),
        C('el señor feo quiere ir con la Nona.', speed=0.86, wh=0.3, curve=[0, 0.5, 0, -0.5])]),
    # 15-16. the 1961 room, the stitches
    'casa.nona.nene_veni': dict(speed=0.78),
    'casa.nona.damelo': dict(place='cellar', chunks=[
        C('Dámelo, nene.', speed=0.78, old=0.7, curve=[0.5, 0, -0.5], gap=0.42),
        C('Esta vez lo cierro yo.', speed=0.74, old=0.6, curve=[0, 0, 0.5, -1.0])]),
    'casa.nona.sesenta': dict(place='cellar', chunks=[
        C('Sesenta y cinco años esperando para esto.', speed=0.76, old=1.1, sigh=(0.75, 0.35), gap=0.25),
        C('¿Me alcanzás el mate?', speed=0.82, curve=[0, 0.5, 2.0])]),
    # 17. breakfast
    'casa.jorge.asado': dict(place='kitchen', chunks=[C('¿Te quedás al asado?', speed=0.95, curve=[0.5, 0.5, 2.0])]),
    'casa.toti.que_perdi': dict(place='kitchen', chunks=[C('¿Qué me perdí?', speed=1.0, curve=[0.5, 0, 2.0])]),
    'casa.nona.quien_asado': dict(place='kitchen', chunks=[
        C('¿Quién quiere asado?', speed=0.85, curve=[1.5, 1, 1, 3], click=0.2)]),
    'casa.marta.perro': dict(place='kitchen', chunks=[
        C('Llevate al perro un par de días,', speed=1.05, gap=0.15), C('nos da miedo.', speed=1.0, curve=[0, -0.5, -1], gain=0.8)]),
}


PRESETS = {
    'madre': vox_madre, 'clara': vox_clara, 'clara84': vox_clara84, 'cura': vox_cura, 'alumna': vox_alumna,
    'paloma': vox_paloma, 'coro': vox_coro, 'monja': vox_monja, 'operadora': vox_operadora,
    # casa
    'marta': vox_marta, 'jorge': vox_jorge, 'jorge_poseido': vox_jorge_poseido, 'nona': vox_nona,
    'nona_grito': vox_nona_grito, 'nona_poseida': vox_nona_poseida, 'lucia': vox_lucia, 'lucia_doble': vox_lucia_doble,
    'toti': vox_toti, 'choripan': vox_choripan, 'spirit': vox_spirit, 'tomi': vox_tomi,
}
NEEDS_ID = {'alumna', 'paloma', 'coro', 'marta', 'jorge', 'jorge_poseido', 'nona', 'nona_grito', 'nona_poseida',
            'lucia', 'lucia_doble', 'toti', 'choripan', 'spirit', 'tomi'}

# per-line direction (speed, pitch contour in semitones, extra grit...)
TWEAKS = {
    'colegio.madre.como_dijo': dict(curve=np.array([0.0, 0.5, 2.5, 3.5, 2.0]), drive=1.25, speed=0.85),
    'colegio.madre.usted': dict(speed=0.82),
    'colegio.madre.aja': dict(speed=0.75, curve=np.array([0.0, 0.0, -1.0]), aspirate=0.5),
    'colegio.madre.albornoz': dict(speed=0.78),
    'colegio.madre.megafonia': dict(speed=0.86),
    'colegio.madre.pregunta1': dict(speed=0.84),
    'colegio.madre.pregunta2': dict(speed=0.84),
    'colegio.cura.corre': dict(speed=0.72, semis=-1.5, whisper=0.35, curve=np.array([0.0, 0.0, 0.0, -1.0, -1.5])),
    'colegio.cura.r3': dict(speed=0.86),
    'colegio.cura.r4': dict(speed=0.8),
    'colegio.clara.gracias': dict(speed=0.9),
}
TWEAKS.update(CASA_DIRECTION)


# ====================================================================== review helpers
def stoi(clean, proc):
    """Simplified STOI (Taal et al. 2011) on 10 kHz copies: 1/3-octave envelope correlation, 384 ms segments."""
    fs = 10000
    c = signal.resample_poly(clean, fs, SR)
    p = signal.resample_poly(proc, fs, SR)
    n = min(len(c), len(p))
    c, p = c[:n], p[:n]
    N, hop, nfft = 256, 128, 512
    if n < N * 4:
        return float('nan')
    win = np.hanning(N + 2)[1:-1]
    idx = np.arange(0, n - N, hop)[:, None] + np.arange(N)[None, :]
    C = np.fft.rfft(c[idx] * win, nfft)
    P = np.fft.rfft(p[idx] * win, nfft)
    e = 20 * np.log10(np.linalg.norm(c[idx] * win, axis=1) + 1e-12)
    keep = e > np.max(e) - 40
    C, P = C[keep], P[keep]
    f = np.fft.rfftfreq(nfft, 1 / fs)
    cf = 150 * 2 ** (np.arange(15) / 3)
    bands = [(f >= lo) & (f < hi) for lo, hi in zip(cf * 2 ** (-1 / 6), cf * 2 ** (1 / 6))]
    X = np.sqrt(np.array([np.sum(np.abs(C[:, b]) ** 2, 1) for b in bands]))
    Y = np.sqrt(np.array([np.sum(np.abs(P[:, b]) ** 2, 1) for b in bands]))
    M = 30
    if X.shape[1] < M:
        return float('nan')
    ds = []
    for m in range(M, X.shape[1] + 1):
        x = X[:, m - M:m]
        y = Y[:, m - M:m]
        a = np.linalg.norm(x, axis=1, keepdims=True) / (np.linalg.norm(y, axis=1, keepdims=True) + 1e-12)
        y = np.minimum(y * a, x * (1 + 10 ** (15 / 20)))
        x = x - x.mean(1, keepdims=True)
        y = y - y.mean(1, keepdims=True)
        ds.append(np.mean(np.sum(x * y, 1) / (np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1) + 1e-12)))
    return float(np.mean(ds))


def align(ref, y, max_lag=0.6):
    """Delay (samples) of ref inside y, from the cross-correlation of their loudness envelopes."""
    h = 110
    a = rms_env(ref, 0.01)[::h]
    b = rms_env(y, 0.01)[::h]
    a = a - a.mean()
    b = b - b.mean()
    c = signal.correlate(b, a, 'full')
    lags = np.arange(-len(a) + 1, len(b))
    ok = (lags >= 0) & (lags <= int(max_lag * SR / h))
    return int(lags[ok][np.argmax(c[ok])] * h) if ok.any() else 0


CREST_DB = 15.0      # peak-to-active-speech-RMS after limiting: similar loudness for every line at -1 dBFS peak
TRIM_DB = {'alumna': -46, 'coro': -46, 'paloma': -48, 'clara84': -50, 'monja': -48,
           'spirit': -52, 'nona_poseida': -50, 'lucia_doble': -48, 'jorge_poseido': -50, 'choripan': -50}
CASA_DEESS = {'marta', 'nona', 'nona_grito', 'nona_poseida', 'lucia', 'lucia_doble', 'toti', 'jorge'}


def active_rms(x, thresh_db=-30.0):
    e = rms_env(x, 0.02)
    act = e > np.max(e) * 10 ** (thresh_db / 20)
    return float(np.sqrt(np.mean(x[act] ** 2))) if act.any() else float(np.sqrt(np.mean(x ** 2)))


def finish(y, voice):
    """De-ess hushed voices, limit the crest factor, trim dead air (keeping the audible tail), master -1 dBFS."""
    y = np.asarray(y, np.float32)
    if voice in ('clara', 'clara84', 'paloma', 'alumna', 'operadora', 'madre') or voice in CASA_DEESS:
        y = deess(y)
    ceiling = active_rms(y) * 10 ** (CREST_DB / 20)
    pk = np.max(np.abs(y))
    if pk > ceiling:
        y = limit(y, max(ceiling, pk * 10 ** (-8 / 20)))     # at most 8 dB of peak reduction
    y = dsp.trim(y, TRIM_DB.get(voice, -48), 0.04)
    fl = min(len(y) // 4, n_of(0.12))
    y = y.copy()
    y[-fl:] *= np.linspace(1, 0, fl) ** 1.5
    return dsp.master(y, peak_db=PEAK_DB)


# ====================================================================== build
def render(lid):
    d = LINES[lid]
    voice = d['voice']
    text = d.get('say') or d['es']
    seed = int(int.from_bytes(lid.encode(), 'little') % 9973)
    tw = TWEAKS.get(lid, {})
    fn = PRESETS[voice]
    if voice in NEEDS_ID:
        y, ref = fn(text, d.get('fx'), seed, tw, lid)
    else:
        y, ref = fn(text, d.get('fx'), seed, tw)
    return voice, np.asarray(y, np.float32), np.asarray(ref, np.float32)


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    ticks = {}
    if os.path.exists(LINES_JSON):
        try:
            ticks = json.load(open(LINES_JSON))
        except (ValueError, OSError):
            ticks = {}
    for lid, d in LINES.items():
        if not d.get('voice'):
            continue
        if only and not any((o == 'casa' and is_casa(lid)) or (o != 'casa' and (o in lid or o == d['voice']))
                            for o in only):
            continue
        t0 = time.time()
        voice, y, ref = render(lid)
        assert y.ndim == 1, lid + ' must be mono'
        x = finish(y, voice)
        rel = 'line/' + lid.replace('.', '/')
        dsp.save_ogg(x, rel)
        st = dsp.analyse(x)
        ticks[lid] = int(math.ceil(len(x) / SR * 20))
        # intelligibility proxy: final file vs the dry character voice (before room / line / tape)
        lag = align(ref, x)
        si = stoi(np.pad(ref, (lag, max(0, len(x) - len(ref) - lag))), x)
        rd = CASA_REVIEW_DIR if is_casa(lid) else REVIEW_DIR
        os.makedirs(rd, exist_ok=True)
        dsp.spectrogram_png(x, os.path.join(rd, lid.replace('.', '_') + '.png'))
        print(f'{lid:30s} {voice:9s} ticks={ticks[lid]:4d} stoi={si:.2f} {st}  ({time.time() - t0:.1f}s)', flush=True)
    want = [k for k, d in LINES.items() if d.get('voice')]
    ticks = {k: ticks[k] for k in want if k in ticks}
    os.makedirs(os.path.dirname(LINES_JSON), exist_ok=True)
    with open(LINES_JSON, 'w') as f:
        json.dump(ticks, f, indent=1, ensure_ascii=False)
    print(f'voices group done in {time.time() - t_all:.1f}s; {len(ticks)} lines -> {LINES_JSON}')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
