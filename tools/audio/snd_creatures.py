# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "creatures": the possessed girl, the shadow, the porcelain doll, the lost soul,
the whisper beds and the case score.

Run from the repo root:  python3 tools/audio/snd_creatures.py [substring ...]

  poseida.giggle (2)  Lucia (8) giggles... and it goes wrong. 1: the giggle slows down like a dying tape until a
                      man's chuckle is laughing with her mouth. 2: every "hi" is answered by a low "heh" that grows,
                      the girl's laugh turns hysterical, chokes, and only the demon keeps laughing.
  poseida.demon (5)   rioplatense lines spoken by Lucia's mouth and the voices inside her (DTW-aligned layers):
                      1 "Lucia no esta aca." (her voice, then HIS voice takes over mid-line)
                      2 "Ella es nuestra."   (girl + demon in unison, sub-octave growl)
                      3 "Vas a morir, exorcista." (snarled, a hiss at the end)
                      4 "Somos muchos."      (legion: seven voices, child to sub-bass, one mouth)
                      5 reversed Latin, Mark 5:9 "Nomen mihi Legio est, quia multi sumus" played backwards
                        (reverb swells INTO each syllable)
  poseida.crack (2)   bones: 1 neck twisting (tendon creak, vertebrae popping in a chain), 2 a limb bending
                      backwards (fracture + fibre splinter, wet tear, bone grinding on bone, settle).
  poseida.scream      possessed scream: child shriek (source-filter synth) + a man's roar under it, sucked-in start.
  poseida.hurt        "AY!" yelp with a demonic snarl and an angry hiss under it.
  poseida.death       the demon is torn out: roar pulled away (pitch/tape drop, closing low-pass, Doppler), wind
                      vacuum, implosion... silence... and Lucia's sharp gasp, a shaky exhale and a tiny whimper.
  sombra.appear       low pressure swell: 29/33 Hz beating infrasound + harmonics, pressure noise, a long dark
                      breath behind you, faint ear-pressure tone, ends in a "whomp".
  sombra.vanish       sucked-back reverse swell (rumble + breath + whisper played backwards into a cut), air pop.
  muneca.giggle (2)   Ofelia: a tiny porcelain voice (child formants x1.6 inside a hollow ceramic head) + music-box
                      tines (free-clamped bar partials, pin click, wooden box). 2 = wound-down.
  muneca.creak        porcelain ball joint turning: stick-slip squeal through ceramic modes, grit, elastic cord, clunk.
  anima.moan (2)      lost soul's lament "ooooh" / "aaay... uuuh": source-filter voice, detuned ghost double, octave
                      undertone, tremolo, 4.6 s chapel tail.
  ambient.whispers(4) mono beds of 4-5 overlapping whispered Spanish phrases (prayers, warnings, names) at different
                      distances; every layer reversed, syllable-shuffled or locally time-reversed (180-260 ms chunks)
                      so the bed keeps the flow of speech but no word survives (STOI ~ that of reversed speech).
  music.case          STEREO 86.7 s seamless loop, D Phrygian: sub + cello drone, reed-organ fifth, music-box
                      lullaby fragment, prepared piano, pulsing spiccato basses (3+3+2), heartbeat timpani,
                      bowed metal, sul ponticello cluster, endless Shepard rise, CUT at bar 24, aftermath.

Positional sounds are mono; music.case is the only stereo stream. Loudness: screams -0.5 dBFS, voices -1 dBFS,
foley -3 dBFS, stream -4 dBFS (dsp.master; the loop goes through master_loop so master's edge fades never land on
the loop point; the bone cracks get 6 dB of transient limiting first so they sit with the project's other impacts);
every OGG is decoded back and re-mastered lower if Vorbis overshoot would clip it. Demonic lines report a STOI intelligibility proxy against the clean (time-aligned) TTS. Self-contained: the voice tools (YIN, TD-PSOLA, DTW, whisper,
source-filter synth) are local so this build never depends on another group's module.
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
from scipy.ndimage import maximum_filter1d, median_filter, minimum_filter1d, uniform_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402
from dsp import SR  # noqa: E402

REVIEW_DIR = os.environ.get(
    'DEADLINE_REVIEW_DIR',
    _os.path.join(WORK, 'audio/colegio_creatures'))
TWO_PI = 2 * np.pi


# ====================================================================== small helpers
def N(sec):
    return max(1, int(round(sec * SR)))


def taxis(n):
    return np.arange(n) / SR


def norm(x, peak=1.0):
    return (np.asarray(x, np.float32) / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def fit(x, n):
    x = np.asarray(x, np.float32)
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def rms(x):
    return float(np.sqrt(np.mean(np.square(np.asarray(x, np.float64))) + 1e-20))


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def add(buf, x, t, g=1.0):
    """Add x into buf at t seconds (clipped to the buffer)."""
    s = N(t) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        buf[s:s + m] += g * x[:m]
    return buf


def stack(*parts, length=None):
    """parts: (x, t, gain) -> mono sum, long enough for every part (or `length` s)."""
    n = N(length) if length else max(N(t) + len(x) for x, t, _ in parts)
    out = np.zeros(n, np.float32)
    for x, t, g in parts:
        add(out, x, t, g)
    return out


def env_pts(n, pts):
    """Piecewise-linear envelope through [(seconds, value)]."""
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    return np.interp(taxis(n), ts, vs).astype(np.float32)


def snoise(n, cutoff, seed):
    """Smooth random control signal in -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 8192).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def rms_env(x, win=0.02):
    return np.sqrt(uniform_filter1d(np.asarray(x, np.float64) ** 2, max(1, N(win))) + 1e-12).astype(np.float32)


def match_env(y, ref, win=0.02, lo=0.05, hi=8.0):
    n = min(len(y), len(ref))
    ey, er = rms_env(y[:n], win), rms_env(ref[:n], win)
    floor = 1e-3 * max(np.max(er), 1e-6)
    g = uniform_filter1d(np.clip((er + floor) / (ey + floor), lo, hi), N(win))
    return (y[:n] * g).astype(np.float32)


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


def tv_bandpass(x, centres, steps=64, bw_oct=1.0):
    """Block-wise time-varying band-pass following `centres` (Hz per sample)."""
    out = np.zeros_like(x)
    edges = np.linspace(0, len(x), steps + 1).astype(int)
    zi = None
    for i in range(steps):
        a, b = edges[i], edges[i + 1]
        if b <= a:
            continue
        fc = float(np.mean(centres[a:b]))
        lo, hi = fc * 2 ** (-bw_oct / 2), min(fc * 2 ** (bw_oct / 2), SR / 2 * 0.95)
        sos = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], 'bandpass', output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[a:b], zi = signal.sosfilt(sos, x[a:b], zi=zi)
    return out.astype(np.float32)


def comb(x, delay_ms, fb):
    """Feedback comb (hollow body resonance)."""
    d = max(1, int(round(delay_ms * 1e-3 * SR)))
    a = np.zeros(d + 1)
    a[0], a[d] = 1.0, -fb
    return signal.lfilter([1.0], a, x).astype(np.float32)


def vlimit(x, ceiling, look=0.004):
    """Look-ahead brickwall limiter (never overshoots)."""
    g = np.minimum(1.0, ceiling / (np.abs(x) + 1e-12))
    w = 2 * N(look) + 1
    g = uniform_filter1d(minimum_filter1d(g, w), w)
    return (x * g).astype(np.float32)


def varispeed(x, speed_in):
    """Tape-style speed change; speed_in = playback speed per INPUT sample (1 normal, 0.5 = octave down)."""
    t_out = np.cumsum(1.0 / np.maximum(np.asarray(speed_in, np.float64), 0.05))
    k = np.arange(int(t_out[-1]))
    pos = np.interp(k, t_out, np.arange(len(x)))
    return np.interp(pos, np.arange(len(x)), x).astype(np.float32), t_out


# ====================================================================== rooms
_IR = {}


def room_ir(decay, damp, predelay, seed, hf=0.5, er=8, er_span=0.04):
    key = (decay, damp, predelay, seed, hf, er, er_span)
    if key in _IR:
        return _IR[key]
    n = N(decay * 1.35)
    t = taxis(n)
    r = dsp.rng(seed)
    w = r.standard_normal(n).astype(np.float32)
    lo = dsp.lowpass(w, damp, 2) * np.exp(-6.9 * t / decay)
    hi = dsp.highpass(w, damp, 2) * np.exp(-6.9 * t / (decay * hf))
    ir = (lo + 0.5 * hi) * np.minimum(1.0, t / max(0.004, min(0.05, decay * 0.03)))
    lvl = np.sqrt(np.mean(ir[:N(0.05)] ** 2)) + 1e-9
    for _ in range(er):
        q = int(r.uniform(0.002, er_span) * SR)
        if q < n:
            ir[q] += r.uniform(0.4, 1.0) * r.choice([-1, 1]) * lvl * 14
    ir = np.concatenate([np.zeros(N(predelay), np.float32), ir.astype(np.float32)])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    _IR[key] = ir
    return ir


ROOMS = {   # decay, damp, predelay, hf, er, er_span
    'cuarto': (0.7, 5200.0, 0.004, 0.55, 8, 0.02),
    'dormitorio': (1.5, 4200.0, 0.012, 0.45, 8, 0.05),
    'pasillo': (1.9, 5000.0, 0.009, 0.5, 8, 0.07),
    'capilla': (4.6, 3800.0, 0.035, 0.45, 9, 0.09),
    'cripta': (3.2, 2900.0, 0.02, 0.45, 8, 0.05),
    'catedral': (6.5, 3200.0, 0.05, 0.4, 9, 0.12),
}


def verb(x, room, wet=0.25, dry=1.0, seed=7):
    d, damp, pd, hf, er, span = ROOMS[room]
    w = signal.fftconvolve(x, room_ir(d, damp, pd, seed, hf, er, span))
    out = np.zeros(len(w), np.float32)
    out[:len(x)] += dry * x
    out += wet * w
    return out.astype(np.float32)


# ====================================================================== TTS + TD-PSOLA voice tools
RESPELL = [(r'll', 'y'), (r'Ll', 'Y')]   # espeak's /jj/ for 'll' -> 'y' gets the rioplatense /sh/


def strip_islands(y, max_island=0.07, min_gap=0.03, thresh_db=-36.0):
    """Drop a stray click/breath Kokoro sometimes leaves before the first word (or after the last)."""
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
        if b - a < N(max_island) and g - b >= N(min_gap) and g < len(m):
            y = y[g - N(0.004):]
            m = m[g - N(0.004):]
        y, m = y[::-1], m[::-1]
    return np.ascontiguousarray(y)


def say(text, voice='ef_dora', speed=0.9):
    for a, b in RESPELL:
        text = re.sub(a, b, text)
    y = dsp.tts(text, voice, speed)
    y = dsp.highpass(y, 60, 2)
    y = dsp.trim(y, -46, 0.03)
    y = dsp.fade(strip_islands(y), 0.003, 0.01)
    return norm(y, 0.8)


def track_f0(x, fmin=70.0, fmax=480.0, hop=0.005, thresh=0.15):
    """YIN on an 11025 Hz copy -> (frame centre sample @SR, f0 Hz or 0 = unvoiced)."""
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
    loud = np.sqrt(e0 / W) > np.max(np.sqrt(e0 / W)) * 10 ** (-38 / 20)
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
    return (np.arange(nf) * H + W / 2) * ds, f0


def pitch_marks(x, centres, f0, unv_step=0.008):
    n = len(x)
    s = np.arange(n)
    vs = np.interp(s, centres, (f0 > 0).astype(float)) > 0.5
    f0s = np.interp(s, centres[f0 > 0], f0[f0 > 0]) if (f0 > 0).any() else np.full(n, 150.0)
    xl = signal.sosfiltfilt(signal.butter(2, 1000 / (SR / 2), output='sos'), x)
    marks, per, vf = [], [], []
    U = N(unv_step)
    i = 0
    while i < n:
        j = i
        while j < n and vs[j] == vs[i]:
            j += 1
        if vs[i] and j - i > N(0.012):
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
    """Pitch by `semis` keeping the tract; tract scaled by `formant` semitones; wobble (cents), tremor, curve (st)."""
    beta = 2 ** (formant / 12)
    xs = dsp.resample(x, beta) if abs(formant) > 1e-3 else np.asarray(x, np.float32)
    centres, f0 = track_f0(xs, fmin * beta, fmax * beta)
    marks, per, vf = pitch_marks(xs, centres, f0)
    n_out = n_out or (len(tmap) if tmap is not None else len(x))
    tm = (np.arange(n_out) if tmap is None else np.asarray(tmap, np.float64)) / beta
    tm = np.clip(tm, 0, len(xs) - 1)
    st = np.full(n_out, semis - formant, np.float64)
    if wobble:
        st += wobble / 100 * snoise(n_out, wobble_rate, seed + 5)
    if tremor:
        st += 12 * np.log2(1 + tremor * np.sin(TWO_PI * tremor_rate * taxis(n_out) + seed))
    if curve is not None:
        st += np.interp(np.linspace(0, 1, n_out), np.linspace(0, 1, len(curve)), curve)
    return psola(xs, marks, per, vf, n_out, 2 ** (st / 12), tm if (tmap is not None or abs(formant) > 1e-3) else None,
                 jitter, shimmer, seed)


def whisper(x, seed=0, smooth=9, nper=1024):
    """Voicing replaced by noise with the same spectral envelope (keeps the words, loses the pitch)."""
    _, _, Z = signal.stft(x, SR, nperseg=nper, noverlap=nper * 3 // 4)
    mag = uniform_filter1d(np.abs(Z), smooth, axis=0)
    ph = dsp.rng(seed).uniform(-np.pi, np.pi, Z.shape)
    _, y = signal.istft(mag * np.exp(1j * ph), SR, nperseg=nper, noverlap=nper * 3 // 4)
    y = dsp.highpass(fit(y, len(x)), 200, 2)
    y = dsp.peak(y, 4800, 3, 1.0)
    return match_env(y, x, 0.015)


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


def _feats(x, hop=441, nfft=1024, w_e=3.0):
    xp = np.concatenate([np.zeros(nfft // 2), x, np.zeros(nfft)])
    nf = 1 + len(x) // hop
    idx = np.arange(nf)[:, None] * hop + np.arange(nfft)[None, :]
    S = np.abs(np.fft.rfft(xp[idx] * np.hanning(nfft), axis=1)) ** 2
    C = dct(np.log(S @ _mel_fb(nfft).T + 1e-8), axis=1, norm='ortho')[:, 1:11]
    C = (C - C.mean(0)) / (C.std(0) + 1e-6)
    e = np.log(rms_env(x, 0.012)[::hop][:len(C)] + 1e-5)
    e = np.pad((e - e.mean()) / (e.std() + 1e-6), (0, max(0, len(C) - len(e))), mode='edge')[:len(C)]
    return np.concatenate([C, w_e * e[:, None], 0.7 * np.gradient(C, axis=0), 2 * w_e * np.gradient(e)[:, None]], 1)


def dtw_map(ref, src, hop=441):
    """Per-sample map: ref timeline -> src sample position (symmetric DTW, slopes 1/2..2)."""
    A, B = _feats(ref, hop), _feats(src, hop)
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    n, m = D.shape
    INF = 1e18
    acc = np.full((n, m), INF)
    back = np.zeros((n, m), np.int8)
    acc[0, 0] = D[0, 0]
    for i in range(1, n):
        c0 = np.full(m, INF)
        c0[1:] = acc[i - 1, :-1] + D[i, 1:]
        c1 = np.full(m, INF)
        c1[2:] = acc[i - 1, :-2] + D[i, 1:-1] + D[i, 2:]
        c2 = np.full(m, INF)
        if i >= 2:
            c2[1:] = acc[i - 2, :-1] + D[i - 1, 1:] + D[i, 1:]
        st = np.stack([c0, c1, c2])
        back[i] = np.argmin(st, 0)
        acc[i] = np.min(st, 0)
    i, j = n - 1, m - 1
    if acc[i, j] >= INF:
        return np.linspace(0, len(src) - 1, len(ref))
    path = [(i, j)]
    while i > 0 and j > 0:
        b = back[i, j]
        i, j = (i - 1, j - 1) if b == 0 else ((i - 1, j - 2) if b == 1 else (i - 2, j - 1))
        path.append((i, j))
    path = np.array(path[::-1])
    jj = np.interp(np.arange(n), path[:, 0], path[:, 1])
    jj = np.maximum.accumulate(uniform_filter1d(jj, 3))
    return np.clip(np.interp(np.arange(len(ref)), np.arange(n) * hop, jj * hop), 0, len(src) - 1)


def stoi(clean, proc):
    """Simplified STOI (1/3-octave envelope correlation on 384 ms segments): intelligibility proxy, 0..1."""
    fs = 10000
    c = signal.resample_poly(clean, fs, SR)
    p = signal.resample_poly(proc, fs, SR)
    n = min(len(c), len(p))
    c, p = c[:n], p[:n]
    Nw, hop, nfft = 256, 128, 512
    if n < Nw * 4:
        return float('nan')
    win = np.hanning(Nw + 2)[1:-1]
    idx = np.arange(0, n - Nw, hop)[:, None] + np.arange(Nw)[None, :]
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


def best_lag(ref, y, max_lag=1.0):
    h = 110
    a = rms_env(ref, 0.01)[::h]
    b = rms_env(y, 0.01)[::h]
    c = signal.correlate(b - b.mean(), a - a.mean(), 'full')
    lags = np.arange(-len(a) + 1, len(b))
    ok = (lags >= 0) & (lags <= int(max_lag * SR / h))
    return int(lags[ok][np.argmax(c[ok])] * h) if ok.any() else 0


# ====================================================================== breaths
def breath_in(dur=0.3, seed=0, size=1.0, gain=1.0, shaky=0.0):
    """Mouth inhale: band noise with a whistle-ish resonance. size < 1 = smaller person."""
    n = N(dur)
    r = dsp.rng(seed)
    a = bp(dsp.noise(dur, 'white', seed), 600 / size, min(4200 / size, 15000))
    a = dsp.peak(a, r.uniform(1500, 1900) / size, 7, 3) + \
        0.5 * dsp.peak(bp(a, 2500 / size, min(6000 / size, 16000)), 3400 / size, 6, 2)
    e = env_pts(n, [(0, 0), (0.35 * dur, 0.7), (0.8 * dur, 1.0), (dur, 0)]) ** 1.3
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * r.uniform(9, 13) * taxis(n))))
    return norm(a[:n] * e, gain)


def breath_out(dur=0.5, seed=0, size=1.0, gain=1.0, shaky=0.0):
    n = N(dur)
    b = bp(dsp.noise(dur, 'pink', seed), 200 / size, 2400 / size)
    b = dsp.peak(b, 700 / size, 5, 2)
    e = env_pts(n, [(0, 0), (0.1 * dur, 1.0), (0.5 * dur, 0.6), (dur, 0)])
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * 8.5 * taxis(n))))
    return norm(b[:n] * e, gain)


# ====================================================================== source-filter voice synth
CTRL = 64
VOWELS = {   # adult female: (formant Hz, bandwidth Hz, amplitude)
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
    """keys [(t_sec, (nf,3) formant array)] -> control-rate track (nfr, nf, 3)."""
    nfr = n // CTRL + 2
    tc = np.arange(nfr) * CTRL / SR
    keys = sorted(keys, key=lambda k: k[0])
    pt, pv = [keys[0][0]], [keys[0][1]]
    for i in range(1, len(keys)):
        g = min(glide, 0.9 * max(keys[i][0] - pt[-1], 1e-4))
        pt += [keys[i][0] - g / 2, keys[i][0] + g / 2]
        pv += [keys[i - 1][1], keys[i][1]]
    pt = np.maximum.accumulate(np.array(pt) + np.arange(len(pt)) * 1e-7)
    flat = np.stack(pv).reshape(len(pt), -1)
    res = np.stack([np.interp(tc, pt, flat[:, j]) for j in range(flat.shape[1])], 1)
    return res.reshape((nfr,) + keys[0][1].shape)


def fgain(f, fr):
    F, B, A = fr[:, None, :, 0], fr[:, None, :, 1], fr[:, None, :, 2]
    return (A / np.sqrt(1 + ((f[..., None] - F) / (B / 2)) ** 2)).sum(-1)


def shaped_noise(fr, n, seed, nper=1024, hf=0.0):
    """White noise filtered (STFT) through the formant track: breath, aspiration, whisper."""
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
           fmax=8000.0, seed=0, floor=0.004, f1_track=False, breath_hf=0.0):
    """Additive glottal source through Lorentzian formants. f0/amp per sample, fr control-rate formant track."""
    n = len(f0)
    r = dsp.rng(seed)
    f0 = np.asarray(f0, np.float64) * (1 + jitter * snoise(n, 30, seed + 1))
    if rough:
        f0 = f0 * (1 + 0.025 * rough * snoise(n, rough_hz, seed + 2))
    ph = TWO_PI * np.cumsum(f0) / SR
    nfr = fr.shape[0]
    ci = np.minimum(np.arange(nfr) * CTRL, n - 1)
    f0c = f0[ci]
    if f1_track:
        fr = fr.copy()
        fr[:, 0, 0] = np.maximum(fr[:, 0, 0], 1.08 * f0c)
    K = max(1, int(fmax / max(25.0, f0c.min())))
    ks = np.arange(1, K + 1, dtype=np.float64)
    tt = np.arange(n)
    phs = r.uniform(0, TWO_PI, K + 1)

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
        ysub = bank(np.arange(0.5, K + 0.5, 1.0), phs[::-1])
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


def contour(n, pts):
    """f0 contour from [(sec, Hz)], log-interpolated."""
    return np.exp(env_pts(n, [(t, np.log(f)) for t, f in pts])).astype(np.float64)


def hiss(dur, seed, scale=0.7, vow='h', gain=1.0, shape=None):
    """Throat hiss / exhale: noise through a (big) vocal tract."""
    n = N(dur)
    fr = ftrack(n, [(0, vowel(vow, scale, 1.6))])
    y = shaped_noise(fr, n, seed, hf=0.6)
    e = env_pts(n, shape or [(0, 0), (0.06, 1), (0.5 * dur, 0.8), (dur, 0)])
    return norm(y * e, gain)


# ====================================================================== giggles
def giggle_voice(syls, total, seed, scale=1.25, tilt=1.0, rough=0.0, sub=0.0, breath=0.3, asp=0.8, fmax=10000.0,
                 vows=('i', 'e'), jitter=0.012):
    """'hi-hi-hi' giggle. syls = [(t, dur, f0_start, f0_end, amp, vowel_mix)], aspirated onsets, breathy voice."""
    n = N(total)
    f0 = np.zeros(n)
    amp = np.zeros(n, np.float32)
    asp_env = np.zeros(n, np.float32)
    keys = []
    last = syls[0][2]
    for (t, d, fa, fb, a, mv) in syls:
        i0, i1 = N(t), min(n, N(t + d))
        seg = i1 - i0
        if seg <= 8:
            continue
        f0[i0:i1] = np.geomspace(fa, fb, seg)
        e = env_pts(seg, [(0, 0), (0.007, 1.0), (0.45 * d, 0.75), (d, 0)]) ** 1.2
        amp[i0:i1] = np.maximum(amp[i0:i1], a * e)
        h0 = max(0, i0 - N(0.022))
        he = env_pts(i0 + N(0.012) - h0, [(0, 0), (0.012, 1), (0.022, 0.6), (0.034, 0)])
        asp_env[h0:h0 + len(he)] += a * he[:max(0, min(len(he), n - h0))]
        keys.append((t, vowel(vows[0], scale, 1.2, vows[1], mv)))
        last = fb
    # hold the pitch through the gaps (phase continuity)
    idx = np.where(f0 > 0, np.arange(n), 0)
    np.maximum.accumulate(idx, out=idx)
    f0 = np.where(f0 > 0, f0, f0[idx])
    f0[f0 <= 0] = last
    fr = ftrack(n, keys, glide=0.02)
    y = vsynth(f0, fr, amp, tilt=tilt, jitter=jitter, shimmer=0.08, rough=rough, sub=sub, breath=breath,
               breath_hf=0.5, fmax=fmax, seed=seed, f1_track=True)
    h = shaped_noise(fr, n, seed + 7, hf=0.8) * asp_env
    return (norm(y) + asp * norm(h)).astype(np.float32)


def demon_chuckle(times, durs, total, seed, f0=70.0, scale=0.66, amps=None, rough=0.8, sub=0.9, breath=0.28):
    """Low 'heh... heh...' of a huge throat (rough, sub-harmonic, very aspirated)."""
    n = N(total)
    f = np.full(n, f0, np.float64)
    amp = np.zeros(n, np.float32)
    asp_env = np.zeros(n, np.float32)
    keys = [(0.0, vowel('e', scale, 1.3, 'a', 0.5))]
    for k, (t, d) in enumerate(zip(times, durs)):
        a = 1.0 if amps is None else amps[k]
        i0, i1 = N(t), min(n, N(t + d))
        if i1 - i0 < 16:
            continue
        f[i0:i1] = np.geomspace(f0 * 1.12, f0 * 0.82, i1 - i0)
        amp[i0:i1] = np.maximum(amp[i0:i1], a * env_pts(i1 - i0, [(0, 0), (0.015, 1), (0.5 * d, 0.7), (d, 0)]))
        h0 = max(0, i0 - N(0.05))
        he = env_pts(i0 + N(0.03) - h0, [(0, 0), (0.03, 1), (0.08, 0)])
        asp_env[h0:h0 + len(he)] += a * he[:max(0, min(len(he), n - h0))]
    fr = ftrack(n, keys)
    y = vsynth(f, fr, amp, tilt=0.95, jitter=0.03, shimmer=0.2, rough=rough, rough_hz=60, sub=sub, breath=breath,
               fmax=5500, seed=seed)
    h = shaped_noise(ftrack(n, [(0, vowel('h', scale, 1.4))]), n, seed + 3, hf=0.3) * asp_env
    return dsp.lowpass(norm(y) + 0.3 * norm(h), 3800, 2)


def poseida_giggle(v):
    r = dsp.rng(100 + v)
    if v == 1:
        # a sweet giggle that slows down like a dying tape: her voice sinks into a man's chuckle
        syls, t = [], 0.06
        for i in range(10):
            d = r.uniform(0.07, 0.09)
            base = 580 - 12 * i + r.normal(0, 9)
            syls.append((t, d, base * 1.07, base * 0.9, 1.0 - 0.03 * i, r.uniform(0.15, 0.6)))
            t += d + r.uniform(0.05, 0.07)
        total = t + 0.12
        g = giggle_voice(syls, total, 1101, scale=1.24)
        n = len(g)
        tw = syls[3][0]
        u = np.clip((taxis(n) - tw) / (syls[-1][0] + syls[-1][1] - tw), 0, 1)
        speed = 1.0 - 0.7 * (0.5 - 0.5 * np.cos(np.pi * u))
        gs, t_out = varispeed(g, speed)
        out_t = [float(np.interp(N(s_[0]), np.arange(n), t_out)) / SR for s_ in syls]
        out_d = [float(np.interp(N(s_[0] + s_[1]), np.arange(n), t_out)) / SR - o for s_, o in zip(syls, out_t)]
        k0 = 4
        dem_amp = list(np.linspace(0.1, 1.0, len(syls) - k0) ** 1.5)
        end = out_t[-1] + out_d[-1]
        tot2 = end + 1.2
        ch = demon_chuckle(out_t[k0:] + [end + 0.35], out_d[k0:] + [0.42], tot2, 1102, f0=72, amps=dem_amp + [0.9])
        girl_fade = env_pts(len(gs), [(0, 1), (out_t[k0 + 2], 1), (end, 0.3)])
        y = stack((gs * girl_fade, 0.0, 1.0), (ch, 0.0, 0.9))
        # a last low throat rattle (vocal fry) after the final "heh"
        m = N(0.55)
        fry = hiss(0.55, 1103, 0.6, vow='a', shape=[(0, 0), (0.05, 1), (0.3, 0.6), (0.55, 0)])
        fry = dsp.lowpass(fry * np.maximum(0, np.sin(TWO_PI * np.cumsum(24 + 4 * snoise(m, 4, 1104)) / SR)) ** 6, 2500, 2)
        add(y, norm(fry), end + 0.85, 0.35)
        y = dsp.drive(norm(y) * 1.3, 1.3)
        return dsp.highpass(verb(y, 'dormitorio', 0.15, seed=1105), 45, 2)
    # v == 2: each "hi" answered by a low "heh" that grows; she gets hysterical, chokes; only he keeps laughing
    syls, t = [], 0.05
    for i in range(9):
        d = r.uniform(0.065, 0.085) * (1 - 0.02 * i)
        base = 540 + 22 * i + r.normal(0, 12)          # rising: the laugh gets strained and high
        syls.append((t, d, base * 1.05, base * 0.88, 0.85 + 0.02 * i, r.uniform(0.2, 0.7)))
        t += d + r.uniform(0.045, 0.06) * (1 - 0.03 * i)
    total = t + 0.1
    g = giggle_voice(syls, total + 1.6, 1201, scale=1.26, rough=0.0, breath=0.35)
    # choke: hard cut right after the last syllable, a tiny glottal click
    cut = N(syls[-1][0] + syls[-1][1] * 0.6)
    g[cut:] = 0
    g[cut - N(0.004):cut] *= np.linspace(1, 0, N(0.004))
    times = [s[0] + 0.085 for s in syls[2:]] + [total + 0.25, total + 0.75]
    durs = [0.07] * (len(syls) - 2) + [0.2, 0.32]
    amps = list(np.linspace(0.15, 0.85, len(syls) - 2)) + [1.0, 0.9]
    ch = demon_chuckle(times, durs, total + 1.6, 1202, f0=66, amps=amps)
    click = bp(white(N(0.012), 1203), 1500, 6000) * np.exp(-taxis(N(0.012)) / 0.002)
    y = stack((g, 0.0, 1.0), (ch, 0.0, 0.9), (norm(click), cut / SR, 0.35))
    y = dsp.drive(norm(y) * 1.3, 1.3)
    return dsp.highpass(verb(y, 'dormitorio', 0.15, seed=1204), 45, 2)


# ====================================================================== demonic speech
def possessed(text, seed, speed=0.86, girl_curve=None, demon_semis=-5.0, sub_semis=-14.0, growl_hz=34.0):
    """Lucia's mouth + the voices behind it, all on Lucia's timeline (DTW). Returns peak-normalised layers."""
    a = say(text, 'ef_dora', speed)
    b = say(text, 'em_santa', speed)
    tm = dtw_map(a, b)
    n = len(a)
    girl = reshape(a, semis=3.5, formant=2.5, wobble=30, wobble_rate=2.2, tremor=0.004, tremor_rate=6.0,
                   jitter=0.008, shimmer=0.06, curve=girl_curve, seed=seed, fmin=110, fmax=480)
    dem = reshape(b, semis=demon_semis, formant=-1.8, wobble=35, wobble_rate=0.9, jitter=0.03, shimmer=0.15,
                  tmap=tm, n_out=n, seed=seed + 1, fmin=50, fmax=300)
    sub = reshape(b, semis=sub_semis, formant=-4.0, wobble=25, wobble_rate=0.7, jitter=0.04, shimmer=0.2,
                  tmap=tm, n_out=n, seed=seed + 2, fmin=50, fmax=300)
    fr = growl_hz * (1 + 0.25 * snoise(n, 3, seed + 3))
    pulses = np.maximum(0, np.sin(TWO_PI * np.cumsum(fr) / SR)) ** 5
    sub = sub * (0.35 + 1.3 * pulses)
    dem = dem * (0.85 + 0.3 * pulses)
    ref = reshape(b, tmap=tm, n_out=n, seed=seed + 6, fmin=50, fmax=300)
    return dict(girl=norm(girl), demon=norm(dem), sub=norm(sub), wh=norm(whisper(dem, seed + 4)),
                gwh=norm(whisper(girl, seed + 5)), ref=ref, dora=a, n=n, tm=tm, santa=b)


def demon_chain(y, seed, drv=1.7, room='dormitorio', wet=0.15):
    y = dsp.drive(norm(y) * drv, drv)
    y = dsp.peak(y, 150, 3.0, 1.0)
    y = dsp.peak(y, 2600, 2.5, 1.4)
    y = dsp.lowpass(y, 7500, 2)
    return verb(y, room, wet, seed=seed)


def smooth_step(n, a, b):
    u = np.clip((taxis(n) - a) / max(1e-3, b - a), 0, 1)
    return (u * u * (3 - 2 * u)).astype(np.float32)


def demon_line(v):
    """Returns (processed, intelligibility reference on the same timeline)."""
    if v == 1:      # "Lucia no esta aca." -- starts as her, HE finishes it
        L = possessed('Lucía no está acá.', 2110, 0.84, girl_curve=np.array([0, 0, 0, -1.0, -3.0, -4.5]))
        n = L['n']
        d = n / SR
        xf = smooth_step(n, 0.3 * d, 0.5 * d)
        y = (1.0 - 0.72 * xf) * L['girl'] + (0.12 + 0.95 * xf) * L['demon'] + (0.05 + 0.6 * xf) * L['sub'] + \
            0.25 * xf * L['wh'] + 0.15 * (1 - xf) * L['gwh']
        y = demon_chain(y, 2111)
        ref = (1 - xf) * norm(L['dora']) + xf * norm(L['ref'])
        return stack((breath_in(0.32, 2112, 0.8, 0.15), 0.0, 1.0), (y, 0.3, 1.0)), np.r_[np.zeros(N(0.3)), ref]
    if v == 2:      # "Ella es nuestra." -- one mouth, two voices in unison
        L = possessed('Ella es nuestra.', 2120, 0.8)
        y = 0.55 * L['girl'] + 1.0 * L['demon'] + 0.62 * L['sub'] + 0.3 * L['wh']
        y = demon_chain(y, 2121, 1.8)
        pre = hiss(0.55, 2122, 0.62, gain=0.2, shape=[(0, 0), (0.4, 1), (0.55, 0)])     # inhaled rasp
        return stack((pre, 0.0, 1.0), (y, 0.5, 1.0)), np.r_[np.zeros(N(0.5)), L['ref']]
    if v == 3:      # "Vas a morir, exorcista." -- snarled, ends in a hiss
        L = possessed('Vas a morir, exorcista.', 2130, 0.86, demon_semis=-4.0, growl_hz=30.0,
                      girl_curve=np.array([0, 1.0, 0, 0, -1.0, 0]))
        y = 0.35 * L['girl'] + 1.0 * L['demon'] + 0.78 * L['sub'] + 0.35 * L['wh']
        y = demon_chain(y, 2131, 2.3, 'pasillo', 0.13)
        tail = hiss(0.9, 2132, 0.6, gain=0.45, shape=[(0, 0), (0.05, 1), (0.4, 0.6), (0.9, 0)])
        tail = tail * (0.7 + 0.3 * np.maximum(0, np.sin(TWO_PI * 26 * taxis(len(tail)))) ** 4)
        pre = dsp.lowpass(hiss(0.4, 2133, 0.62, gain=0.22, shape=[(0, 0), (0.3, 1), (0.4, 0)]), 3000, 2)
        out = stack((pre, 0.0, 1.0), (y, 0.38, 1.0), (tail, 0.38 + L['n'] / SR - 0.08, 1.0))
        return out, np.r_[np.zeros(N(0.38)), L['ref']]
    if v == 4:      # "Somos muchos." -- legion: seven voices, one mouth
        text = 'Somos muchos.'
        sp = 0.78
        a = say(text, 'ef_dora', sp)
        n = len(a)
        b = say(text, 'em_santa', sp)
        c = say(text, 'em_alex', sp)
        tb, tc = dtw_map(a, b), dtw_map(a, c)
        layers = [  # (src, tmap, semis, formant, offset s, gain, whisper, fmin, fmax)
            (a, None, 3.5, 2.5, 0.000, 0.55, 0.15, 110, 480),     # Lucia
            (a, None, 8.0, 4.0, 0.035, 0.22, 0.8, 110, 480),      # a tiny one, whispering
            (a, None, -2.0, -1.0, 0.018, 0.45, 0.0, 110, 480),    # a woman
            (c, tc, -3.0, -1.5, 0.026, 0.55, 0.0, 60, 320),       # a man
            (b, tb, -5.0, -1.8, 0.008, 1.0, 0.0, 50, 300),        # HIM
            (b, tb, -14.0, -4.0, 0.012, 0.6, 0.0, 50, 300),       # sub
            (c, tc, 2.0, 0.5, 0.045, 0.3, 0.9, 60, 320),          # a whisperer
        ]
        parts = []
        for k, (src, tm, st, fm, off, g, wh, fmin, fmax) in enumerate(layers):
            v_ = reshape(src, semis=st, formant=fm, wobble=30, wobble_rate=1.2, jitter=0.02, shimmer=0.12,
                         tmap=tm, n_out=n, seed=2140 + 7 * k, fmin=fmin, fmax=fmax)
            if wh:
                v_ = (1 - wh) * norm(v_) + wh * norm(whisper(v_, 2141 + k))
            parts.append((norm(v_), off, g))
        y = dsp.mix(*parts)
        nn = len(y)
        pulses = np.maximum(0, np.sin(TWO_PI * np.cumsum(32 * (1 + 0.2 * snoise(nn, 3, 2148))) / SR)) ** 5
        y = y * (0.9 + 0.2 * pulses)
        y = demon_chain(y, 2149, 1.6, 'cripta', 0.2)
        ref = reshape(b, tmap=tb, n_out=n, seed=2147, fmin=50, fmax=300)
        pre = breath_in(0.45, 2150, 0.7, 0.18)
        return stack((pre, 0.0, 1.0), (y, 0.42, 1.0)), np.r_[np.zeros(N(0.42)), ref]
    # v == 5: reversed Latin -- the reverb swells INTO each syllable
    L = possessed('Nomen mihi Legio est, quia multi sumus.', 2150, 0.8, demon_semis=-6.0)
    y = 0.45 * L['girl'] + 1.0 * L['demon'] + 0.7 * L['sub'] + 0.45 * L['wh']
    y = dsp.drive(norm(y) * 1.7, 1.7)
    y = dsp.peak(y, 150, 3.0, 1.0)
    y = verb(dsp.lowpass(y, 7000, 2), 'cripta', 0.6, 0.8, seed=2151)
    y = dsp.reverse(dsp.trim(y, -60, 0.02))
    # keep ~1.1 s of reversed tail swelling in before the first (reversed) word
    e = rms_env(y, 0.03)
    first = int(np.argmax(e > np.max(e) * 10 ** (-22 / 20)))
    y = y[max(0, first - N(1.1)):]
    y[:N(1.1)] *= np.linspace(0, 1, N(1.1)) ** 2
    # a dark forward exhale at the very end so it lands on something that breathes
    ex = dsp.lowpass(hiss(0.6, 2152, 0.65), 2500, 2)
    out = stack((y, 0.0, 1.0), (ex, len(y) / SR - 0.2, 0.18))
    return out, None


# ====================================================================== possessed scream / hurt / death
def child_scream(n, f0_pts, amp, seed, scale=1.22, vkeys=None, rough=0.6, sub=0.25, bright=0.55, breath=0.15):
    """Source-filter scream with the irregularities of a real one: slow wobble, vocal-fold chaos bursts."""
    f0 = contour(n, f0_pts) * (1 + 0.045 * snoise(n, 6, seed + 9) + 0.02 * snoise(n, 25, seed + 10))
    burst = np.clip(snoise(n, 3, seed + 11), 0, None) ** 2
    f0 = f0 * (1 + 0.08 * burst * snoise(n, 140, seed + 12))
    keys = vkeys or [(0, vowel('a', scale, 1.3))]
    fr = ftrack(n, keys, 0.12)
    return vsynth(f0, fr, amp, tilt=bright, jitter=0.012, shimmer=0.12, rough=rough, rough_hz=95, sub=sub,
                  breath=breath, breath_hf=0.6, fmax=11000, seed=seed, f1_track=True)


def demon_roar(n, f0_pts, amp, seed, scale=0.62, vkeys=None, rough=1.3, sub=0.95, breath=0.4):
    f0 = contour(n, f0_pts)
    keys = vkeys or [(0, vowel('a', scale, 1.5, 'o', 0.3))]
    fr = ftrack(n, keys, 0.2)
    return vsynth(f0, fr, amp, tilt=0.85, jitter=0.03, shimmer=0.2, rough=rough, rough_hz=55, sub=sub,
                  breath=breath, fmax=6000, seed=seed)


def poseida_scream():
    dur = 2.75
    n = N(dur)
    amp = env_pts(n, [(0, 0), (0.025, 0.8), (0.08, 1.0), (1.3, 0.92), (2.0, 0.88), (2.45, 0.5), (2.72, 0)])
    f0p = [(0, 520), (0.08, 880), (0.3, 960), (0.75, 920), (0.78, 1180), (1.1, 1100), (1.6, 1020), (2.1, 900),
           (2.5, 720), (2.75, 560)]
    vk = [(0, vowel('a', 1.22, 1.3)), (0.9, vowel('a', 1.22, 1.3, 'e', 0.45)), (2.0, vowel('a', 1.22, 1.3, 'o', 0.3))]
    clean = child_scream(n, f0p, amp, 3101, vkeys=vk, rough=0.45, sub=0.15)
    torn = child_scream(n, f0p, amp, 3101, vkeys=vk, rough=1.5, sub=1.0, breath=0.3)    # vocal folds breaking up
    ep = env_pts(n, [(0, 0.2), (0.45, 0.2), (0.55, 1.0), (0.85, 0.9), (0.95, 0.15), (1.55, 0.15), (1.7, 0.85),
                     (2.1, 0.7), (2.3, 0.3), (2.75, 0.5)])
    girl = (1 - ep) * norm(clean) + ep * norm(torn)
    damp = env_pts(n, [(0, 0), (0.12, 0.35), (0.5, 0.9), (1.6, 1.0), (2.3, 0.85), (2.75, 0)])
    dem = demon_roar(n, [(0, 72), (0.2, 96), (0.9, 104), (1.7, 92), (2.4, 76), (2.75, 64)], damp, 3102)
    # a third voice: the girl's scream an octave and a fifth down, choked (one mouth, two throats)
    mid = child_scream(n, [(0, 175), (0.3, 320), (1.1, 300), (2.0, 280), (2.75, 200)], damp * 0.8, 3103,
                       scale=0.85, rough=1.0, sub=0.6, bright=0.8, breath=0.3)
    y = norm(girl) + 0.6 * norm(dem) + 0.28 * norm(mid)
    tear = bp(white(n, 3104), 1800, 7000) * (0.5 + 0.5 * snoise(n, 120, 3105)) * amp
    y += 0.12 * norm(tear)
    y = dsp.drive(norm(y) * 1.8, 1.7)
    y = dsp.peak(y, 3100, 2.0, 1.2)
    y = verb(y, 'dormitorio', 0.15, seed=3106)
    # sucked-in start: reversed reverb of the onset swelling into the attack. The reversed IR ends in its predelay
    # and onset ramp (~85 ms of near-silence), which left a dead gap before the scream: cut the swell where it is
    # still loud and overlap it 12 ms into the attack so it flows straight in.
    on = verb(y[:N(0.5)], 'capilla', 1.0, 0.0, seed=3107)
    rv = dsp.reverse(on)
    e = rms_env(rv, 0.01)
    k = len(rv) - N(0.15) + int(np.argmax(e[-N(0.15):]))
    rv = rv[:k + N(0.004)]
    pre = rv[-N(0.45):] * np.linspace(0, 1, N(0.45)) ** 2
    pre[-N(0.004):] *= np.linspace(1, 0, N(0.004))
    return stack((norm(pre), 0.0, 0.45), (y, len(pre) / SR - 0.012, 1.0))


def poseida_hurt():
    dur = 1.15
    n = N(dur)
    amp = env_pts(n, [(0, 0), (0.012, 1.0), (0.18, 0.95), (0.42, 0.6), (0.62, 0.0), (dur, 0)])
    girl = child_scream(n, [(0, 640), (0.05, 930), (0.14, 860), (0.3, 700), (0.55, 520)], amp, 3201,
                        vkeys=[(0, vowel('a', 1.22, 1.2)), (0.16, vowel('a', 1.22, 1.2)), (0.38, vowel('i', 1.22, 1.2))],
                        rough=0.45, sub=0.15, bright=0.6, breath=0.12)
    damp = env_pts(n, [(0, 0), (0.06, 0.8), (0.3, 1.0), (0.7, 0.7), (1.0, 0)])
    snarl = demon_roar(n, [(0, 88), (0.2, 74), (0.8, 58), (dur, 52)], damp, 3202,
                       vkeys=[(0, vowel('a', 0.6, 1.6, 'e', 0.5))], rough=1.6, sub=1.0, breath=0.7)
    hs = hiss(0.7, 3203, 0.6, gain=1.0, shape=[(0, 0), (0.08, 1), (0.45, 0.6), (0.7, 0)])
    y = stack((norm(girl), 0.0, 1.0), (norm(snarl), 0.0, 0.55), (hs, 0.35, 0.3))
    y = dsp.drive(norm(y) * 1.6, 1.6)
    y = dsp.lowpass(y, 9500, 2)          # the drive's fizz above 10 kHz only feeds codec overshoot
    return verb(y, 'cuarto', 0.18, seed=3204)


def poseida_death():
    dur = 5.6
    n = N(dur)
    out = np.zeros(n, np.float32)
    # A 0-2.0 s: the roar, with her scream thin beneath it, being pulled OUT (tape drop, closing low-pass)
    na = N(2.05)
    amp = env_pts(na, [(0, 0), (0.06, 1.0), (1.0, 0.95), (1.7, 0.7), (2.05, 0.0)])
    roar = demon_roar(na, [(0, 84), (0.25, 132), (0.8, 124), (1.4, 100), (2.05, 70)], amp, 3301,
                      vkeys=[(0, vowel('a', 0.62, 1.5)), (0.9, vowel('o', 0.62, 1.5)), (1.8, vowel('u', 0.62, 1.5))])
    gamp = env_pts(na, [(0, 0), (0.05, 0.6), (0.9, 0.45), (1.3, 0.0), (2.05, 0)])
    girl = child_scream(na, [(0, 700), (0.2, 950), (1.0, 900), (1.3, 760)], gamp, 3302, rough=0.7)
    a = norm(roar) + 0.45 * norm(girl)
    for k, tr in enumerate((0.3, 0.72, 1.15)):     # tearing out: wet rips
        m = N(0.16)
        rip = bp(white(m, 3303 + k), 900, 5000) * (0.5 + 0.5 * snoise(m, 300, 3310 + k)) ** 2
        add(a, norm(rip * np.sin(np.pi * np.linspace(0, 1, m)) ** 0.5) * 0.35, tr)
    a = dsp.drive(norm(a) * 1.6, 1.6)
    u = np.clip((taxis(na) - 0.7) / 1.35, 0, 1)
    a, _ = varispeed(a, 1.0 - 0.55 * u ** 1.6)             # pitch and time sag as it is dragged away
    a = fit(a, na)
    a = dsp.sweep_lowpass(a, 9000, 350, 64)
    a = a * env_pts(na, [(0, 1), (1.6, 1), (2.05, 0)])
    imp = 2.1
    wet = verb(a, 'capilla', 1.0, 0.0, seed=3320)
    nb = N(imp)
    pre = np.zeros(nb, np.float32)
    add(pre, a, 0.0)
    add(pre, wet * env_pts(len(wet), [(0, 0.15), (1.0, 0.45), (2.0, 1.0), (len(wet) / SR, 1.0)]), 0.0, 0.55)
    # B: vacuum -- rising wind and a reversed swell, everything sucked into the implosion at 2.1 s
    rise = np.clip((taxis(nb) - 0.5) / (imp - 0.5), 0, 1)
    vac = tv_bandpass(white(nb, 3330), 250 + 5000 * rise ** 2.4, 64, 1.2) * rise ** 2.5
    rv = dsp.reverse(verb(norm(roar[:N(0.6)]), 'cripta', 1.0, 0.0, seed=3331))
    rv = fit(rv[-min(len(rv), nb):][::-1], nb)[::-1] * rise ** 1.5
    pre += 0.5 * (norm(vac) * 0.55 + norm(rv) * 0.45)
    pre *= env_pts(nb, [(0, 1), (imp - 0.012, 1), (imp, 0)])
    add(out, pre, 0.0)
    # implosion: a low thump and a puff of air in a small dead room, then the ears ring in the silence
    m = N(1.2)
    tm = taxis(m)
    thump = np.sin(TWO_PI * np.cumsum(32 + 60 * np.exp(-tm / 0.05)) / SR) * np.exp(-tm / 0.3)
    thump += 0.5 * dsp.lowpass(white(m, 3340), 180, 2) * np.exp(-tm / 0.08)
    puff = bp(white(N(0.25), 3341), 400, 3000) * np.exp(-taxis(N(0.25)) / 0.04)
    add(out, verb(norm(thump), 'cuarto', 0.2, seed=3342)[:m], imp, 0.6)
    add(out, norm(puff), imp, 0.2)
    nr = N(1.3)
    ringing = np.sin(TWO_PI * 3350 * taxis(nr)) * env_pts(nr, [(0, 0), (0.05, 1), (1.3, 0)]) ** 2
    add(out, ringing.astype(np.float32), imp + 0.05, 0.012)
    # C: silence... then Lucia comes back: a sharp gasp, a shaky exhale, a tiny whimper
    tg = 3.55
    gasp = breath_in(0.42, 3350, 0.72, 1.0)
    ng = len(gasp)
    sq = vsynth(np.geomspace(430, 610, ng), ftrack(ng, [(0, vowel('a', 1.22, 1.4, 'h', 0.4))]),
                env_pts(ng, [(0, 0), (0.22, 0.0), (0.36, 1.0), (0.42, 0)]), tilt=1.3, breath=0.6, seed=3351)
    gasp = norm(gasp) + 0.3 * norm(sq)
    add(out, gasp, tg, 0.75)
    add(out, breath_out(0.7, 3352, 0.75, 0.4, shaky=0.7), tg + 0.55)
    nw = N(0.55)
    wh = vsynth(contour(nw, [(0, 420), (0.25, 450), (0.55, 330)]), ftrack(nw, [(0, vowel('m', 1.2)), (0.2, vowel('u', 1.22, 1.2, 'm', 0.4))]),
                env_pts(nw, [(0, 0), (0.06, 0.8), (0.3, 1.0), (0.55, 0)]), tilt=1.4, breath=0.35, jitter=0.02,
                shimmer=0.15, seed=3353)
    add(out, norm(wh), tg + 1.35, 0.28)
    add(out, breath_in(0.35, 3354, 0.75, 0.22, shaky=0.6), tg + 1.95)
    tail = verb(out[N(tg):], 'dormitorio', 0.12, seed=3355)
    out[N(tg):] = tail[:n - N(tg)]
    return out


# ====================================================================== bones
def modal_ir(modes, dur, seed=None, jitter=0.0):
    t = taxis(N(dur))
    r = dsp.rng(seed or 0)
    ir = np.zeros(len(t))
    for f, d, a in modes:
        ff = f * (1 + jitter * r.normal()) if jitter else f
        ir += a * np.sin(TWO_PI * ff * t + r.uniform(0, TWO_PI)) * np.exp(-d * t)
    return ir.astype(np.float32)


def excite(exc, modes, dur=0.4, seed=None, jitter=0.0):
    return signal.fftconvolve(exc, modal_ir(modes, dur, seed, jitter))[:len(exc) + N(dur)].astype(np.float32)


BONE = [(430, 260, 0.6), (880, 330, 1.0), (1550, 400, 0.85), (2450, 470, 0.65), (3650, 560, 0.5), (5300, 700, 0.35)]


def bone_snap(seed, size=1.0, fibres=8, spread=0.03, body=0.6):
    """A fracture: a primary snap, a burst of fibre micro-snaps (Pareto amplitudes), a dull flesh thud.
    Heavily damped modes (bone in flesh does not ring), crunch in the 2-9 kHz band."""
    r = dsp.rng(seed)
    n = N(spread + 0.2)
    exc = np.zeros(n, np.float32)
    exc[N(0.002)] = 1.0
    exc[N(0.002) + 3] = -0.8
    for _ in range(fibres):
        p = N(0.002 + r.uniform(0, spread) * r.random() ** 0.5)
        exc[p] += r.choice([-1, 1]) * min(1.0, 0.15 * r.pareto(2.0) + 0.08)
    tt = taxis(n)
    nz = white(n, seed + 1) * (np.exp(-tt / 0.003) + 0.25 * np.exp(-tt / max(0.004, spread * 0.6)))
    exc = exc + 0.35 * nz
    modes = [(f / size, d, a) for f, d, a in BONE]
    y = excite(exc, modes, 0.06, seed + 2, 0.08)[:n]
    crunch = bp(exc, 2000, 10000)
    thud = np.sin(TWO_PI * np.cumsum(90 / size + 80 * np.exp(-tt / 0.006)) / SR) * np.exp(-tt / 0.025)
    thud += 0.6 * dsp.lowpass(white(n, seed + 3), 280, 2) * np.exp(-tt / 0.02)
    return norm(norm(y) + 0.8 * norm(crunch) + body * 0.5 * norm(thud))


def stick_slip(dur, rate, seed, modes, grit=0.3, amp=None, jit=0.35, direct=0.0, band=(900.0, 7000.0), flip=0.25,
               avar=0.6):
    """Creak/grind: irregular impulse train (stick-slip) through resonances. rate = Hz per sample (array).
    direct > 0 also radiates the slip pulses themselves through a broad band (a pitched squeal)."""
    n = N(dur)
    r = dsp.rng(seed)
    rate = np.broadcast_to(np.asarray(rate, np.float64), (n,))
    exc = np.zeros(n, np.float32)
    t = 0.0
    while True:
        i = int(t * SR)
        if i >= n:
            break
        exc[i] += r.uniform(1.0 - avar, 1.0) * (-1 if r.random() < flip else 1)
        t += (1.0 / max(rate[i], 1.0)) * (1 + jit * r.normal())
        t = max(t, i / SR + 0.0006)
    y = excite(exc, modes, 0.15, seed + 1)[:n]
    g = bp(white(n, seed + 2), 1500, 8000) * uniform_filter1d(np.abs(exc), N(0.01)) * 30
    y = norm(y) + grit * norm(g)
    if direct:
        y = y + direct * norm(bp(exc, *band))
    if amp is not None:
        y = y * amp
    return y.astype(np.float32)


def wet_squelch(dur, seed, lo=250, hi=1800, rate=60):
    n = N(dur)
    y = bp(white(n, seed), lo, hi)
    am = np.clip(snoise(n, rate, seed + 1), 0, None) ** 2
    pops = np.zeros(n, np.float32)
    r = dsp.rng(seed + 2)
    for _ in range(int(dur * 25)):
        p = int(r.uniform(0, n - N(0.02)))
        m = N(r.uniform(0.006, 0.02))
        f = r.uniform(300, 900)
        tt = taxis(m)
        pops[p:p + m] += np.sin(TWO_PI * np.cumsum(f * (1 + 1.5 * tt / tt[-1])) / SR) * np.exp(-tt / (0.3 * tt[-1])) * r.uniform(0.3, 1)
    e = env_pts(n, [(0, 0), (0.1 * dur, 1), (0.7 * dur, 0.6), (dur, 0)])
    return norm((norm(y * am) + 0.5 * norm(pops)) * e)


TENDON = [(290, 70, 1.0), (470, 85, 0.75), (760, 110, 0.55), (1180, 140, 0.4), (1900, 190, 0.25)]
GRIND = [(210, 90, 1.0), (390, 110, 0.8), (680, 140, 0.65), (1150, 170, 0.5), (1900, 220, 0.35), (3100, 300, 0.2)]


def poseida_crack(v):
    if v == 1:     # the neck turns too far: tendon creak, vertebrae pop in a chain, a last grind
        dur = 2.0
        n = N(dur)
        out = np.zeros(n, np.float32)
        rate = env_pts(N(1.0), [(0, 18), (0.5, 34), (1.0, 52)])
        cr = stick_slip(1.0, rate, 4101, TENDON, 0.06, env_pts(N(1.0), [(0, 0), (0.15, 0.6), (0.9, 1.0), (1.0, 0.5)]),
                        jit=0.3)
        add(out, cr, 0.0, 0.3)
        for k, (t, s_, g) in enumerate([(0.3, 1.25, 0.4), (0.56, 1.15, 0.5), (0.92, 1.0, 1.0), (0.985, 0.95, 0.85),
                                        (1.06, 1.05, 0.75)]):
            add(out, bone_snap(4110 + k, s_, fibres=6 + 3 * k, spread=0.014, body=0.5), t, g)
        add(out, wet_squelch(0.45, 4120, 300, 1600), 0.92, 0.18)
        rate2 = env_pts(N(0.75), [(0, 40), (0.75, 14)])
        cr2 = stick_slip(0.75, rate2, 4121, GRIND, 0.12, env_pts(N(0.75), [(0, 0), (0.1, 1), (0.75, 0)]), jit=0.45)
        add(out, cr2, 1.15, 0.32)
        add(out, bone_snap(4130, 1.3, fibres=4, spread=0.006, body=0.2), 1.72, 0.4)
        return verb(out, 'cuarto', 0.1, seed=4131)
    # v == 2: a limb bends backwards: fracture + fibre splinter, wet tear, bone grinding on bone, settle
    dur = 1.9
    n = N(dur)
    out = np.zeros(n, np.float32)
    add(out, stick_slip(0.16, 30, 4201, TENDON, 0.05, env_pts(N(0.16), [(0, 0), (0.16, 1)])), 0.0, 0.25)
    add(out, bone_snap(4202, 0.85, fibres=28, spread=0.07, body=1.0), 0.15, 1.0)
    add(out, wet_squelch(0.5, 4203, 220, 1500, 90), 0.2, 0.35)
    rate = env_pts(N(0.9), [(0, 30), (0.3, 70), (0.6, 45), (0.9, 18)])
    add(out, stick_slip(0.9, rate, 4204, GRIND, 0.15, env_pts(N(0.9), [(0, 0), (0.08, 1), (0.8, 0.8), (0.9, 0)]),
                        jit=0.5), 0.48, 0.42)
    add(out, bone_snap(4205, 1.0, fibres=12, spread=0.03, body=0.5), 0.82, 0.7)
    add(out, bone_snap(4206, 1.15, fibres=7, spread=0.015, body=0.3), 1.18, 0.55)
    tt = taxis(N(0.3))
    settle = np.sin(TWO_PI * 85 * tt) * np.exp(-tt / 0.02) + 0.8 * dsp.lowpass(white(len(tt), 4207), 300, 2) * np.exp(-tt / 0.04)
    add(out, norm(settle), 1.45, 0.25)
    return verb(out, 'cuarto', 0.1, seed=4208)


# ====================================================================== the shadow
def sombra_appear():
    dur = 4.0
    n = N(dur)
    t = taxis(n)
    pk = 2.3
    swell = env_pts(n, [(0, 0), (0.6, 0.15), (1.6, 0.6), (pk - 0.05, 1.0), (pk + 0.08, 0.45), (3.4, 0.05), (dur, 0)]) ** 1.3
    # infrasound beating 29/33 Hz under an audible 55-110 Hz rumble (drive adds the harmonics speakers can play)
    inf = np.sin(TWO_PI * 29 * t) + 0.8 * np.sin(TWO_PI * 33.3 * t + 1.0)
    aud = np.sin(TWO_PI * 58 * t + 0.3) + 0.7 * np.sin(TWO_PI * 66.6 * t + 2.0) + 0.45 * np.sin(TWO_PI * 87.3 * t)
    aud = dsp.drive(norm(aud) * 2.5, 2.5)
    rumble = dsp.lowpass(dsp.noise(dur, 'brown', 5101), 140, 4)
    press = tv_bandpass(dsp.noise(dur, 'pink', 5102), 110 + 450 * np.clip(t / pk, 0, 1) ** 2, 48, 1.6)
    # (QA: the pure 29/33 Hz sines are inaudible on phones/laptops yet ate the headroom; trimmed 0.45 -> 0.3 and the
    #  breath/whispers raised so the audible band gains ~2.4 dB. The whomp stays the climax.)
    low = norm(inf) * 0.3 + norm(aud) * 0.35 + norm(rumble) * 0.55 + norm(press) * 0.5
    low = low * swell
    # a long dark breath right behind you (huge chest, closed throat), and a faint inhale first
    br = hiss(1.9, 5103, 0.72, vow='a', shape=[(0, 0), (0.9, 0.7), (1.6, 1.0), (1.9, 0)])
    br = dsp.lowpass(br, 3200, 2)
    inh = breath_in(0.5, 5104, 1.3, 1.0)
    # a few unintelligible whispered syllables smeared through the breath
    w = whisper(say('ya estoy acá, detrás tuyo', 'em_alex', 0.85), 5105)
    w = dsp.granular(w, 1.6, grain=0.09, density=24, pitch_jitter=1.5, seed=5106)
    w = dsp.lowpass(w, 4000, 2) * env_pts(N(1.6), [(0, 0), (0.8, 1), (1.6, 0)])
    # ear pressure: a faint high tone creeping in, gone with the whomp
    tone = np.sin(TWO_PI * 7350 * t) * env_pts(n, [(0, 0), (0.9, 0), (pk - 0.02, 1), (pk, 0)]) ** 2
    m = N(1.6)
    tm = taxis(m)
    whomp = np.sin(TWO_PI * np.cumsum(30 + 40 * np.exp(-tm / 0.07)) / SR) * np.exp(-tm / 0.35)
    whomp += 0.6 * dsp.lowpass(white(m, 5107), 160, 2) * np.exp(-tm / 0.12)
    whomp = dsp.drive(norm(whomp) * 1.8, 1.8) * env_pts(m, [(0, 1), (1.2, 1), (1.6, 0)])
    out = stack((low, 0.0, 1.0), (inh, 0.15, 0.08), (br, 0.5, 0.42), (w, 0.7, 0.14), (tone, 0.0, 0.004),
                (whomp, pk - 0.02, 0.7), length=dur)
    return verb(out, 'pasillo', 0.18, seed=5108)


def sombra_vanish():
    # material: rumble + breath + whisper with a big tail, played BACKWARDS so it is sucked into a cut
    d = 1.4
    n = N(d)
    t = taxis(n)
    inf = np.sin(TWO_PI * 31 * t) + 0.7 * np.sin(TWO_PI * 36 * t + 1.3)
    inf = dsp.drive(norm(inf) * 2.0, 2.0) * np.exp(-t / 0.5)
    br = hiss(1.2, 5201, 0.75, vow='o', shape=[(0, 0), (0.03, 1), (0.4, 0.6), (1.2, 0)])
    w = whisper(say('me voy, pero vuelvo', 'em_alex', 0.9), 5202)
    w = fit(w, n) * np.exp(-t / 0.4)
    src = stack((norm(inf), 0.0, 0.7), (br, 0.0, 0.5), (norm(w), 0.0, 0.35), length=d)
    tail = verb(src, 'cripta', 0.9, 0.6, seed=5203)
    rv = dsp.reverse(dsp.trim(tail, -55, 0.01))
    rv = rv[-N(1.55):] if len(rv) > N(1.55) else rv
    rv = rv * np.linspace(0.0, 1.0, len(rv)) ** 1.6
    rv[-N(0.003):] *= np.linspace(1, 0, N(0.003))
    m = N(0.35)
    tm = taxis(m)
    pop = bp(white(m, 5204), 300, 2500) * np.exp(-tm / 0.012)
    sub = np.sin(TWO_PI * np.cumsum(40 + 30 * np.exp(-tm / 0.03)) / SR) * np.exp(-tm / 0.08)
    end = len(rv) / SR
    out = stack((rv, 0.0, 1.0), (norm(pop), end, 0.25), (norm(sub), end, 0.4))
    return verb(out, 'cuarto', 0.12, seed=5205)


# ====================================================================== the porcelain doll
def tine(f, seed, dur=2.4, amp=1.0):
    """Music-box comb tooth: free-clamped bar modes (1, 6.27, 17.55), pin pluck, small wooden box."""
    r = dsp.rng(seed)
    n = N(dur)
    t = taxis(n)
    y = np.sin(TWO_PI * f * t + r.uniform(0, 6)) * np.exp(-t * 1.9)
    y += 0.25 * np.sin(TWO_PI * f * 1.0013 * t) * np.exp(-t * 2.2)          # comb tooth + its neighbour beat
    y += 0.22 * np.sin(TWO_PI * f * 6.267 * t) * np.exp(-t * 9)
    y += 0.07 * np.sin(TWO_PI * f * 17.55 * t) * np.exp(-t * 30)
    y += 0.05 * np.sin(TWO_PI * f * 2 * t) * np.exp(-t * 4)
    pin = bp(white(N(0.006), seed + 1), 3000, 12000) * np.exp(-taxis(N(0.006)) / 0.0012)
    y[:len(pin)] += 0.6 * pin
    y = dsp.peak(y.astype(np.float32), 450, 4, 2) + 0.1 * dsp.peak(y.astype(np.float32), 900, 3, 2)
    return norm(y * np.minimum(1, t / 0.0008), amp)


def porcelain(x, seed):
    """A tiny voice inside a hollow ceramic head: comb resonance, glassy modes, thin band."""
    y = bp(x, 700, 10000)
    y = 0.6 * y + 0.4 * comb(y, 0.42, 0.55)
    for f, g, q in ((2650, 7, 9), (4150, 6, 10), (6300, 5, 11)):
        y = dsp.peak(y, f, g, q)
    return y


def muneca_giggle(v):
    r = dsp.rng(600 + v)
    syls, t = [], 0.04 if v == 1 else 0.55
    k = 7 if v == 1 else 6
    for i in range(k):
        d = r.uniform(0.05, 0.065)
        base = 980 - 25 * i + r.normal(0, 15)
        syls.append((t, d, base * 1.06, base * 0.9, 1.0 - 0.05 * i, r.uniform(0.2, 0.7)))
        t += d + r.uniform(0.04, 0.055)
    g = giggle_voice(syls, t + 0.2, 6100 + v, scale=1.62, tilt=0.85, breath=0.15, asp=0.45, fmax=12000)
    if v == 2:   # wound-down: the mechanism slows, the voice sags
        u = np.clip((taxis(len(g)) - 0.55) / (len(g) / SR - 0.55), 0, 1)
        g, _ = varispeed(g, 1.0 - 0.38 * u ** 1.3)
    g = porcelain(g, 6110 + v)
    if v == 1:
        notes = [(t + 0.05, 1760.0, 0.9)]                      # one last note of the music box (A6)
    else:
        notes = [(0.0, 1108.7, 0.8), (0.24, 880.0, 0.75)]     # C#6 ... A5, then the giggle
    parts = [(norm(g), 0.0, 1.0)]
    for j, (tt, f, a) in enumerate(notes):
        parts.append((tine(f * (1 - 0.004 * (v == 2)), 6120 + 10 * v + j), tt, 0.55 * a))
    y = stack(*parts)
    return verb(y, 'cuarto', 0.15, seed=6130 + v)


CERAMIC = [(1930, 45, 1.0), (3120, 60, 0.75), (4480, 75, 0.55), (6230, 95, 0.4), (8350, 130, 0.25)]


def muneca_creak():
    """Glazed porcelain ball joint: the head turns in three jerks (squeal + grind), then locks with a knock."""
    dur = 1.5
    n = N(dur)
    out = np.zeros(n, np.float32)
    r = dsp.rng(6200)
    for k, (t0, d, f0, f1, g) in enumerate([(0.0, 0.34, 430, 610, 0.8), (0.44, 0.3, 520, 700, 1.0),
                                             (0.8, 0.2, 640, 470, 0.7)]):
        m = N(d)
        f = np.geomspace(f0, f1, m) * (1 + 0.04 * snoise(m, 18, 6201 + k))
        amp = env_pts(m, [(0, 0), (0.03, 1), (0.6 * d, 0.85), (d, 0)]) * (0.75 + 0.25 * snoise(m, 25, 6205 + k))
        sq = stick_slip(d, f, 6210 + k, CERAMIC, 0.05, amp, jit=0.02, direct=0.9, band=(1100.0, 6500.0), flip=0.0,
                        avar=0.25)   # the squeal: periodic slip pulses
        gr = stick_slip(d, r.uniform(45, 70), 6220 + k, CERAMIC, 0.3, amp, jit=0.5)   # gritty grind under it
        add(out, norm(sq), t0, 0.7 * g)
        add(out, norm(gr), t0, 0.35 * g)
    # the elastic cord inside stretching (low, rubbery)
    cord = stick_slip(0.9, env_pts(N(0.9), [(0, 18), (0.9, 30)]), 6230, [(240, 60, 1), (410, 80, 0.6), (690, 110, 0.3)],
                      0.05, env_pts(N(0.9), [(0, 0), (0.2, 1), (0.9, 0)]))
    add(out, norm(cord), 0.05, 0.18)
    # it locks into place: ceramic knock + a tiny rattle of a loose chip inside
    m = N(0.4)
    exc = np.zeros(m, np.float32)
    exc[0], exc[2] = 1.0, -0.6
    knock = excite(exc, [(1150, 40, 1.0), (2440, 55, 0.7), (3890, 75, 0.5), (5600, 110, 0.3)], 0.3, 6240)[:m]
    add(out, norm(knock), 1.06, 0.75)
    for j in range(4):
        e = np.zeros(N(0.08), np.float32)
        e[0] = 1
        c = excite(e, [(f * r.uniform(0.95, 1.05), 160, a) for f, _, a in CERAMIC], 0.06, 6250 + j)
        add(out, norm(c), 1.13 + 0.045 * j + r.uniform(0, 0.02), 0.25 * 0.6 ** j)
    return verb(out, 'cuarto', 0.13, seed=6260)


# ====================================================================== the lost soul
def anima_moan(v):
    if v == 1:     # a woman's "ooooh" sinking, vibrato widening
        dur = 3.6
        n = N(dur)
        f0 = contour(n, [(0, 300), (0.45, 345), (1.4, 335), (2.3, 290), (3.1, 245), (dur, 225)])
        vib = 1 + (0.008 + 0.012 * np.clip(taxis(n) / dur, 0, 1)) * np.sin(TWO_PI * 4.9 * taxis(n))
        amp = env_pts(n, [(0, 0), (0.55, 0.75), (1.5, 1.0), (2.6, 0.75), (dur, 0)])
        keys = [(0, vowel('u', 1.0, 1.1)), (0.6, vowel('o', 1.0, 1.1)), (1.7, vowel('o', 1.0, 1.1, 'a', 0.3)),
                (3.0, vowel('u', 1.0, 1.1))]
        undertone = 0.5
    else:          # "aaaay... uuuh": higher cry that breaks, then sinks
        dur = 3.9
        n = N(dur)
        f0 = contour(n, [(0, 240), (0.35, 290), (0.95, 285), (1.12, 360), (1.3, 270), (2.2, 235), (3.2, 190),
                         (dur, 170)])
        vib = 1 + 0.014 * np.sin(TWO_PI * 5.2 * taxis(n))
        amp = env_pts(n, [(0, 0), (0.4, 0.8), (1.0, 1.0), (1.1, 0.35), (1.22, 0.9), (2.4, 0.75), (dur, 0)])
        keys = [(0, vowel('a', 1.0, 1.1)), (0.8, vowel('a', 1.0, 1.1, 'e', 0.4)), (1.05, vowel('i', 1.0, 1.1)),
                (1.45, vowel('u', 1.0, 1.1)), (3.2, vowel('u', 1.0, 1.1, 'm', 0.5))]
        undertone = 1.0
    fr = ftrack(n, keys, 0.35)
    a = vsynth(f0 * vib, fr, amp, tilt=1.3, jitter=0.006, shimmer=0.06, breath=0.16, breath_hf=0.3, fmax=7000,
               seed=7100 + v)
    b = vsynth(f0 * vib * 2 ** (9 / 1200), fr, amp, tilt=1.4, jitter=0.008, shimmer=0.08, breath=0.25, fmax=7000,
               seed=7110 + v)
    lo = vsynth(f0 * vib * 0.5, ftrack(n, [(t, f * np.array([0.82, 1.2, 1.0])) for t, f in keys], 0.35),
                amp, tilt=1.2, jitter=0.01, shimmer=0.1, breath=0.25, fmax=4000, seed=7120 + v)
    air = shaped_noise(fr, n, 7130 + v, hf=0.4) * amp
    y = stack((norm(a), 0.0, 1.0), (norm(b), 0.037, 0.55), (norm(lo), 0.02, 0.22 * undertone), (norm(air), 0.0, 0.1))
    y = dsp.tremolo(y, 5.6, 0.12)
    y = dsp.lowpass(y, 5200, 2)
    return verb(y, 'capilla', 0.42, 0.9, seed=7140 + v)


# ====================================================================== whisper beds
WHISPERS = [   # (text, voice, speed, semis, mode, start s, gain, distance 0 near .. 1 far)
    [('Dios te salve María, llena eres de gracia, el Señor es contigo', 'ef_dora', 1.0, 0, 'fwd', 0.0, 0.9, 0.3),
     ('ella viene, ella viene, ella viene', 'em_alex', 0.95, 0, 'fwd', 0.55, 0.8, 0.5),
     ('no se corre en los pasillos', 'ef_dora', 1.0, 4, 'shuf', 1.0, 1.0, 0.1),
     ('bendita tú eres entre todas las mujeres', 'em_santa', 0.95, 0, 'rev', 0.2, 0.75, 0.7),
     ('shh, callate, nos va a escuchar', 'ef_dora', 1.05, 4, 'fwd', 2.2, 0.7, 0.0)],
    [('Lucía, Lucía, vení, vení acá', 'ef_dora', 0.95, 4, 'fwd', 0.1, 0.9, 0.2),
     ('somos muchas, somos muchas, somos muchas', 'ef_dora', 1.0, 0, 'shuf', 0.0, 0.85, 0.5),
     ('Santa María, madre de Dios, ruega por nosotros', 'em_alex', 0.95, 0, 'rev', 0.6, 0.8, 0.6),
     ('el que habla se queda después de hora', 'em_santa', 0.9, 0, 'fwd', 1.4, 0.7, 0.8),
     ('no la mires, no la mires', 'ef_dora', 1.05, 3, 'fwd', 2.3, 0.85, 0.05)],
    [('padre nuestro que estás en el cielo, santificado sea tu nombre', 'em_alex', 0.95, 0, 'fwd', 0.0, 0.8, 0.5),
     ('¿quién habló? ¿quién habló?', 'ef_dora', 1.0, -1, 'fwd', 0.9, 0.85, 0.2),
     ('ahora y en la hora de nuestra muerte, amén', 'ef_dora', 0.95, 0, 'rev', 0.3, 0.8, 0.6),
     ('Albornoz, Albornoz, ausente', 'ef_dora', 1.0, 4, 'shuf', 1.8, 0.9, 0.3),
     ('te estamos mirando desde el coro', 'em_santa', 0.9, 0, 'fwd', 2.6, 0.75, 0.75)],
    [('andate, andate de acá, todavía estás a tiempo', 'ef_dora', 1.0, 4, 'fwd', 0.0, 0.9, 0.15),
     ('veintiuno de junio, veintiuno de junio', 'em_alex', 0.95, 0, 'shuf', 0.4, 0.8, 0.55),
     ('perdón madre, perdón madre, no lo hago más', 'ef_dora', 1.05, 3, 'rev', 1.0, 0.8, 0.4),
     ('ella escucha todo, ella escucha todo', 'em_santa', 0.9, 0, 'fwd', 1.7, 0.75, 0.8)],
]
WHISPER_LEN = [3.5, 4.1, 4.6, 3.8]


def shuffle_syllables(x, seed, chunk=(0.12, 0.24)):
    """Cut at random 120-240 ms points and shuffle (cross-faded): keeps the speech texture, kills the words."""
    r = dsp.rng(seed)
    cuts = [0]
    while cuts[-1] < len(x):
        cuts.append(cuts[-1] + N(r.uniform(*chunk)))
    pieces = [x[cuts[i]:min(len(x), cuts[i + 1])] for i in range(len(cuts) - 1)]
    pieces = [p for p in pieces if len(p) > N(0.03)]
    order = r.permutation(len(pieces))
    out = []
    for k in order:
        p = pieces[k].copy()
        f = min(len(p) // 3, N(0.012))
        p[:f] *= np.linspace(0, 1, f)
        p[-f:] *= np.linspace(1, 0, f)
        out.append(p)
    return np.concatenate(out).astype(np.float32)


def local_reverse(x, seed, chunk=(0.18, 0.26)):
    """Reverse each 180-260 ms chunk in place: keeps the flow and prosody of speech, destroys the words."""
    r = dsp.rng(seed)
    out = np.zeros_like(x)
    i = 0
    while i < len(x):
        m = min(len(x) - i, N(r.uniform(*chunk)))
        p = x[i:i + m][::-1].copy()
        f = min(m // 3, N(0.01))
        if f:
            p[:f] *= np.linspace(0, 1, f)
            p[-f:] *= np.linspace(1, 0, f)
        out[i:i + m] = p
        i += m
    return out


def ambient_whispers(v):
    r = dsp.rng(800 + v)
    dur = WHISPER_LEN[v - 1]
    parts = []
    for i, (text, voice, sp, st, mode, start, g, dist) in enumerate(WHISPERS[v - 1]):
        x = say(text, voice, sp)
        if st:
            x = reshape(x, semis=st, formant=min(st, 2.5), seed=810 + i, fmin=60 if voice != 'ef_dora' else 110,
                        fmax=480)
        w = whisper(x, 820 + 10 * v + i, smooth=7 if voice == 'ef_dora' else 5)
        if mode == 'rev':
            w = dsp.reverse(w)
        elif mode == 'shuf':
            w = shuffle_syllables(w, 830 + v + i)
        else:                      # 'fwd': forward flow, but every syllable-sized chunk reversed in place
            w = local_reverse(w, 835 + v + i)
        w = dsp.trim(w, -45, 0.02)
        room = dur - start
        if len(w) > N(room):
            off = int(r.uniform(0, len(w) - N(room)))
            w = w[off:off + N(room)]
        n = len(w)
        fl = 1 + 0.35 * np.interp(np.arange(n), np.linspace(0, n, 10), r.uniform(-1, 1, 10))
        w = w * fl * env_pts(n, [(0, 0), (min(0.35, n / SR / 4), 1), (n / SR * 0.8, 0.85), (n / SR, 0)])
        # distance: air absorption, less level, more room
        w = dsp.lowpass(w, 9000 * 0.35 ** dist, 2)
        w = verb(w, 'pasillo', 0.15 + 0.5 * dist, 1.0 - 0.4 * dist, seed=840 + 10 * v + i)
        parts.append((norm(w), start, g * (1 - 0.35 * dist)))
    parts.append((breath_in(r.uniform(0.35, 0.5), 850 + v, 0.9, 1.0), r.uniform(0.0, 0.4), 0.25))
    s = bp(dsp.noise(0.9, 'white', 860 + v), 3800, 8500) * env_pts(N(0.9), [(0, 0), (0.25, 1), (0.9, 0)])
    parts.append((norm(dsp.peak(s, 5200, 4, 2)), dur - r.uniform(1.3, 1.7), 0.09))
    y = stack(*parts)
    y = dsp.highpass(y, 160, 2)
    y = fit(y, N(dur))
    y[-N(0.6):] *= np.linspace(1, 0, N(0.6)) ** 2
    return y


# ====================================================================== music.case (periodic timeline)
BPM = 72.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 26           # 86.67 s


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(buf, ev, t, gain=1.0):
    """Wrap-add an event (mono or stereo) into a periodic buffer at t seconds."""
    L = len(buf)
    if ev.ndim == 1 and buf.ndim == 2:
        ev = np.stack([ev, ev], 1)
    s = int(round(t * SR)) % L
    i = 0
    while i < len(ev):
        a = (s + i) % L
        m = min(len(ev) - i, L - a)
        buf[a:a + m] += ev[i:i + m] * gain
        i += m


def loop_phase(freq, L):
    f = np.broadcast_to(np.asarray(freq, np.float64), (L,))
    ph = np.cumsum(f) / SR
    ph += (np.round(ph[-1]) - ph[-1]) * (np.arange(L) / L)
    return ph


def blep_saw(ph, dt):
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


def ctl_curve(L, seed, rate=0.1, lo=0.0, hi=1.0):
    """Periodic smooth random curve (whole cycles per loop)."""
    dur = L / SR
    nc = max(16, int(dur * 50))
    tt = np.arange(nc) / nc
    r = dsp.rng(seed)
    y = np.zeros(nc)
    for k in range(1, max(1, int(rate * dur)) + 1):
        y += r.standard_normal() / k ** 0.8 * np.sin(TWO_PI * k * tt + r.uniform(0, TWO_PI))
    y = (y - y.min()) / (y.max() - y.min() + 1e-9)
    return np.interp(np.arange(L) * nc / L, np.arange(nc + 1), np.append(y, y[0])).astype(np.float32) * (hi - lo) + lo


def keyframes(L, pts):
    """Periodic envelope through (t_seconds, value), cosine-interpolated, wrapping at L."""
    dur = L / SR
    pts = sorted(pts)
    ts = np.array([p[0] for p in pts] + [pts[0][0] + dur])
    vs = np.array([p[1] for p in pts] + [pts[0][1]])
    nc = int(dur * 200)
    t = np.arange(nc) / 200
    tt = np.where(t < ts[0], t + dur, t)
    i = np.clip(np.searchsorted(ts, tt, side='right') - 1, 0, len(ts) - 2)
    u = (tt - ts[i]) / (ts[i + 1] - ts[i])
    y = vs[i] + (vs[i + 1] - vs[i]) * (0.5 - 0.5 * np.cos(np.pi * u))
    return np.interp(np.arange(L) * nc / L, np.arange(nc + 1), np.append(y, y[0])).astype(np.float32)


def sfilt(x, lp=None, hp=None, order=2, peaks=()):
    """Zero-phase circular filter for periodic signals."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lp:
        g /= np.sqrt(1 + (f / lp) ** (2 * order))
    if hp:
        g /= np.sqrt(1 + (hp / np.maximum(f, 1e-3)) ** (2 * order))
    for fc, db, q in peaks:
        g *= 1 + (10 ** (db / 20) - 1) / (1 + ((f - fc) / (fc / q / 2)) ** 2)
    X = np.fft.rfft(x, axis=0)
    X *= g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X, len(x), axis=0).astype(np.float32)


def stereo_ir(decay, damp, predelay, seed, hf=0.45):
    n = N(decay * 1.35)
    t = taxis(n)
    r = dsp.rng(seed)
    out = []
    for _ in range(2):
        w = r.standard_normal(n).astype(np.float32)
        ir = dsp.lowpass(w, damp, 2) * np.exp(-6.9 * t / decay) + 0.5 * dsp.highpass(w, damp, 2) * np.exp(-6.9 * t / (decay * hf))
        ir *= np.minimum(1.0, t / 0.04)
        for _k in range(6):
            ir[int(r.uniform(0.004, 0.045) * SR)] += r.uniform(0.3, 1.0) * r.choice([-1, 1]) * 2
        ir = np.concatenate([np.zeros(N(predelay)), ir])
        out.append(ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9))
    return np.stack(out, 1)


def creverb(x, decay, damp, predelay, seed, hf=0.45, cross=0.3):
    """Circular (loop-safe) stereo reverb, wet only."""
    L = len(x)
    ir = stereo_ir(decay, damp, predelay, seed, hf)
    if len(ir) > L:
        ir = np.pad(ir, ((0, -len(ir) % L), (0, 0))).reshape(-1, L, 2).sum(0)
    X = np.fft.rfft(x, axis=0)
    H = np.fft.rfft(ir, n=L, axis=0)
    wl = np.fft.irfft(((1 - cross) * X[:, 0] + cross * X[:, 1]) * H[:, 0], L)
    wr = np.fft.irfft(((1 - cross) * X[:, 1] + cross * X[:, 0]) * H[:, 1], L)
    return np.stack([wl, wr], 1).astype(np.float32)


class Score:
    """Periodic stereo timeline: dry bus + reverb sends."""

    def __init__(self, dur):
        self.L = N(dur)
        self.dry = np.zeros((self.L, 2), np.float32)
        self.sends = {}

    def bus(self, name, **kw):
        self.sends[name] = [np.zeros((self.L, 2), np.float32), kw]

    def add(self, x, t, p=0.0, dry=1.0, send=None, wet=0.0):
        st = dsp.pan(x, float(np.clip(p, -1, 1))) if x.ndim == 1 else x
        put(self.dry, st, t, dry)
        if send and wet:
            put(self.sends[send][0], st, t, wet)

    def bed(self, x, dry=1.0, send=None, wet=0.0):
        x = np.stack([x, x], 1) if x.ndim == 1 else x
        self.dry += x * dry
        if send and wet:
            self.sends[send][0] += x * wet

    def mix(self):
        out = self.dry.copy()
        for buf, kw in self.sends.values():
            out += creverb(buf, **kw)
        return out


def loop_tone(L, f, shape='sine', vib=0.0, vib_rate=0.2, seed=0):
    r = dsp.rng(seed)
    fr = np.full(L, f, np.float64) if np.ndim(f) == 0 else np.asarray(f, np.float64)
    if vib:
        fr = fr * (1 + vib * (ctl_curve(L, seed + 99, vib_rate) * 2 - 1))
    ph = loop_phase(fr, L) + r.random()
    return (np.sin(TWO_PI * ph) if shape == 'sine' else blep_saw(ph, fr / SR)).astype(np.float32)


def bowed(f, dur, seed, cutoff=1500.0, voices=4, bow=0.06, spic=True, rel=0.25):
    """Section string note: detuned band-limited saws, body resonances, bow noise; spiccato or sustained."""
    r = dsp.rng(seed)
    n = N(dur + rel)
    t = taxis(n)
    y = np.zeros(n)
    for _ in range(voices):
        det = 2 ** (r.normal(0, 7) / 1200)
        vib = 1 + 0.004 * np.sin(TWO_PI * r.uniform(4.6, 5.6) * t + r.uniform(0, 6)) * np.minimum(1, t / 0.25)
        fr = f * det * vib
        y += blep_saw(np.cumsum(fr) / SR + r.random(), fr / SR)
    y = dsp.lowpass(y.astype(np.float32), cutoff, 2)
    y = dsp.peak(y, 280, 4, 1.2)
    y = dsp.peak(y, 520, 2, 1.5)
    nz = bp(white(n, seed + 1), 1500, 6000) * bow * voices
    if spic:
        e = np.exp(-t * 7) * np.minimum(1, t / 0.01) * np.r_[np.ones(N(dur)), np.linspace(1, 0, n - N(dur))]
        ne = np.exp(-t * 45)
    else:
        e = np.minimum(1, t / 0.08) * np.r_[np.ones(N(dur)), np.linspace(1, 0, n - N(dur))]
        ne = e
    return ((y * e + nz * ne) / voices).astype(np.float32)


def prep_piano(f, seed, dur=4.5, bolt=0.6, B=0.0028):
    """Piano string with a bolt between the strings: stretched partials + inharmonic ones, buzzing rattle."""
    r = dsp.rng(seed)
    t = taxis(N(dur))
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
    return norm(((y / 3 + rattle + ham) * np.minimum(1, t / 0.0015)).astype(np.float32))


def timp(f, seed, dur=2.0):
    """Muffled timpani / heartbeat: membrane modes, felt mallet thump."""
    t = taxis(N(dur))
    r = dsp.rng(seed)
    y = np.zeros(len(t))
    for ratio, a, d in ((1.0, 1.0, 3.5), (1.5, 0.5, 5.0), (1.98, 0.3, 7.0), (2.44, 0.18, 9.0), (2.9, 0.1, 12.0)):
        y += a * np.sin(TWO_PI * f * ratio * (1 + 0.04 * np.exp(-t / 0.03)) * t + r.uniform(0, 6)) * np.exp(-d * t)
    y += 0.6 * dsp.lowpass(dsp.noise(dur, 'pink', seed), 400, 2) * np.exp(-t * 40)
    return norm((y * np.minimum(1, t / 0.002)).astype(np.float32))


def boom(seed, dur=3.0):
    t = taxis(N(dur))
    y = np.sin(TWO_PI * np.cumsum(34 + 42 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.3)
    hit = dsp.lowpass(dsp.noise(dur, 'brown', seed), 300, 2) * np.exp(-t * 12) * 1.5
    return norm(dsp.drive(norm(y + hit), 1.6))


def shepard(L, octaves=8, fmin=40.0, seed=0):
    """Endless Shepard-Risset rising glissando: exactly `octaves` octaves per loop."""
    t = taxis(L)
    period = L / SR / octaves
    out = np.zeros((L, 2))
    r = dsp.rng(seed)
    for k in range(octaves):
        pos = (k + t / period) % octaves
        amp = np.exp(-0.5 * ((pos - octaves / 2 + 0.3) / (octaves / 6.5)) ** 2)
        y = np.sin(TWO_PI * loop_phase(fmin * 2 ** pos, L) + r.random()) * amp
        out += dsp.pan(y.astype(np.float32), -0.6 if k % 2 else 0.6)
    return out.astype(np.float32)


def bowed_metal(L, seed, freqs=(1183, 1741, 2618, 3427)):
    """Narrow-band resonances driven by periodic noise (a bowed cymbal / saw)."""
    out = np.zeros((L, 2), np.float32)
    f = np.fft.rfftfreq(L, 1 / SR)
    r = dsp.rng(seed)
    for i, fc in enumerate(freqs):
        g = 1 / (1 + ((f - fc) / 3.0) ** 2) + 0.3 / (1 + ((f - fc * 2.01) / 4.0) ** 2)
        for c in range(2):
            spec = (r.standard_normal(len(f)) + 1j * r.standard_normal(len(f))) * g
            y = np.fft.irfft(spec, L)
            out[:, c] += (y / (np.std(y) + 1e-12) / (1 + 0.5 * i)).astype(np.float32)
    return out


def circ_limit(x, crest_db=14.0, win=0.012, rel=0.08):
    m = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    thr = np.sqrt(np.mean(m ** 2)) * 10 ** (crest_db / 20)
    g = np.minimum(1.0, thr / (maximum_filter1d(m, N(win), mode='wrap') + 1e-9))
    g = uniform_filter1d(minimum_filter1d(g, N(rel), mode='wrap'), N(rel), mode='wrap')
    return (x * (g[:, None] if x.ndim == 2 else g)).astype(np.float32)


def music_case():
    sc = Score(BARS * BAR)
    L = sc.L
    r = dsp.rng(901)

    def T(bar, beat=0.0):
        return (bar - 1) * BAR + beat * BEAT

    CUT = T(24, 3)
    sc.bus('hall', decay=3.2, damp=4500.0, predelay=0.03, seed=91)
    sc.bus('cave', decay=7.5, damp=2600.0, predelay=0.07, seed=92, hf=0.35)
    ten = keyframes(L, [(T(1), 0.0), (T(7), 0.15), (T(11), 0.35), (T(15), 0.55), (T(19), 0.75), (T(23), 0.95),
                        (CUT - 0.05, 1.0), (CUT + 0.06, 0.04), (T(26, 3.9), 0.0)])
    cutenv = keyframes(L, [(T(1), 1.0), (CUT - 0.04, 1.0), (CUT + 0.05, 0.0), (T(26, 3.95), 0.0)])

    # drones: sub D, cello D2 ensemble; Eb2 grinds in for the climb
    sw = ctl_curve(L, 902, 0.06, 0.7, 1.0)
    sub = loop_tone(L, 36.71, seed=1) * 0.9 + loop_tone(L, 73.42, seed=2) * 0.35
    sc.bed(sub * sw * 0.10)
    cello = sum(loop_tone(L, 73.42 * 2 ** (r.normal(0, 6) / 1200), 'saw', vib=0.003, seed=10 + i) for i in range(4))
    cello = sfilt(cello, lp=650, peaks=[(280, 5, 1.5)]) / 4
    sc.bed(np.stack([cello * 0.9, cello * 0.75], 1) * (sw * 0.06)[:, None], send='hall', wet=0.03)
    eb = sum(loop_tone(L, 77.78 * 2 ** (r.normal(0, 8) / 1200), 'saw', vib=0.004, seed=20 + i) for i in range(3))
    eb = sfilt(eb, lp=700, peaks=[(300, 4, 1.5)]) / 3
    ebg = keyframes(L, [(T(1), 0), (T(14), 0), (T(17), 0.6), (T(23), 1.0), (CUT - 0.04, 1.0), (CUT + 0.05, 0),
                        (T(26, 3.9), 0)])
    sc.bed(np.stack([eb * 0.7, eb * 0.95], 1) * (ebg * 0.045)[:, None], send='hall', wet=0.03)

    # reed organ open fifth (the chapel harmonium), only in the calm before and after
    org = np.zeros(L, np.float32)
    for m, g in ((50, 1.0), (57, 0.7), (62, 0.45)):
        for d in (-3, 3):
            f = midi(m) * 2 ** (d / 1200)
            ph = loop_phase(np.full(L, f), L) + r.random()
            org += g * ((ph % 1.0) < 0.18).astype(np.float32)
    org = sfilt(org - org.mean(), lp=1800, hp=90, peaks=[(900, 4, 2), (1700, 3, 3)])
    og = keyframes(L, [(T(1), 0.85), (T(5), 0.8), (T(7), 0.0), (CUT + 1.0, 0.0), (T(25, 2), 0.6), (T(26, 3.9), 0.85)])
    sc.bed(norm(org) * og * 0.028, send='cave', wet=0.02)

    # glass: high beating sine cluster D6/Eb6/A6, opening up with the tension
    gl = np.zeros((L, 2), np.float32)
    for i, (m, det) in enumerate([(86, 0), (86, 1.3), (87, 0), (87, -0.9), (93, 0.0), (93, 0.7)]):
        gl += dsp.pan(loop_tone(L, midi(m) + det, seed=30 + i), -0.8 + 1.6 * (i % 2))
    sc.bed(gl * ((0.25 + 0.75 * ctl_curve(L, 903, 0.08)) * (0.1 + 0.9 * ten) * cutenv * 0.0045)[:, None],
           send='cave', wet=0.012)

    # bowed metal in the second half
    bm = bowed_metal(L, 904)
    bmg = keyframes(L, [(T(1), 0), (T(12), 0), (T(14), 0.5), (T(17), 0.4), (T(21), 0.8), (CUT - 0.04, 1.0),
                        (CUT + 0.05, 0.0), (T(26, 3.9), 0)])
    sc.bed(bm * (bmg * 0.009)[:, None], send='cave', wet=0.01)

    # Shepard rise: never resolves (8 octaves per loop)
    sp = shepard(L, 8, 40.0, 905)
    spg = keyframes(L, [(T(1), 0.2), (T(9), 0.3), (T(17), 0.65), (T(23), 1.0), (CUT - 0.04, 1.0), (CUT + 0.05, 0.1),
                        (T(26, 3.9), 0.18)])
    sc.bed(sp * (spg * 0.026)[:, None], send='hall', wet=0.01)

    # music box lullaby fragment (bars 2-4), and its wound-down ghost after the cut (bars 25-26)
    mel = [(2, 0, 81), (2, 1, 86), (2, 2, 84), (2, 3, 81), (3, 0, 82), (3, 1, 81), (3, 2, 77), (3, 3, 76), (4, 0, 74)]
    for k, (bar, beat, m) in enumerate(mel):
        sc.add(tine(midi(m) * 2 ** (r.normal(0, 4) / 1200), 9100 + k, 3.0), T(bar, beat), p=0.35, dry=0.11,
               send='cave', wet=0.07)
    ghost = [(25, 0.4, 81, -10), (25, 1.7, 86, -18), (25, 3.2, 84, -28), (26, 0.9, 81, -40), (26, 2.8, 82, -55)]
    for k, (bar, beat, m, cents) in enumerate(ghost):
        sc.add(tine(midi(m) * 2 ** (cents / 1200), 9150 + k, 3.0), T(bar, beat), p=-0.3, dry=0.07, send='cave',
               wet=0.08)

    # prepared piano: low bolted D clusters on structural downbeats, high plinks between
    for bar, g in ((1, 0.45), (5, 0.45), (9, 0.5), (13, 0.55), (15, 0.6), (17, 0.65), (19, 0.75), (21, 0.8), (23, 0.9)):
        cl = prep_piano(36.71, 9200 + bar) + 0.6 * prep_piano(77.78, 9230 + bar, bolt=0.9) + 0.4 * prep_piano(110.0, 9260 + bar)
        sc.add(norm(cl), T(bar), p=0.15, dry=g * 0.4, send='hall', wet=g * 0.22)
    plinks = [(6, 2.5, 87), (8, 1.0, 98), (10, 3.0, 87), (12, 1.5, 93), (14, 2.0, 99), (16, 3.5, 87), (18, 0.5, 98),
              (20, 2.0, 99), (21, 3.0, 93), (22, 1.5, 98), (23, 2.5, 99)]
    for bar, beat, m in plinks:
        sc.add(prep_piano(midi(m), 9300 + bar, dur=2.5, bolt=0.9, B=0.006), T(bar, beat), p=r.uniform(-0.6, 0.7),
               dry=0.12, send='cave', wet=0.09)

    # pulsing low strings: spiccato ostinato, 3+3+2 accents, D2 -> D2/Eb2 grind, eighths -> sixteenths
    acc = [1.0, 0.45, 0.5, 0.9, 0.45, 0.5, 0.9, 0.5]
    D2, EB2 = 73.42, 77.78
    for bar in range(7, 25):
        if bar <= 10:
            vel, sub8, octv = 0.32 + 0.05 * (bar - 7), 2, False
        elif bar <= 14:
            vel, sub8, octv = 0.55, 2, True
        elif bar <= 18:
            vel, sub8, octv = 0.7, 2 if bar <= 16 else 4, True
        else:
            vel, sub8, octv = 0.8 + 0.035 * (bar - 19), 4, True
        for s in range(4 * sub8):
            beat = s / sub8
            if T(bar, beat) >= CUT - 0.01:
                break
            root = EB2 if (bar >= 15 and ((bar % 2 == 0) or (bar >= 21 and beat >= 2))) else D2
            a = acc[(s * 2 // sub8) % 8] if sub8 == 2 else acc[s % 8]
            d = BEAT / sub8 * 0.9
            note = bowed(root, d, 7000 + bar * 50 + s, cutoff=800 + 1500 * vel * a)
            if octv and a > 0.8:
                note = note + 0.5 * bowed(root * 2, d, 7500 + bar * 50 + s, cutoff=2200)[:len(note)]
            sc.add(note, T(bar, beat), p=-0.25, dry=0.5 * vel * a, send='hall', wet=0.12 * vel * a)

    # heartbeat timpani (lub-dub) from bar 11, crescendo
    for bar in range(11, 25):
        g = 0.18 + 0.04 * (bar - 11)
        for beat, gg in ((0.0, 1.0), (0.42, 0.6)) if bar < 19 else ((0.0, 1.0), (0.42, 0.6), (2.0, 0.8), (2.42, 0.5)):
            if T(bar, beat) >= CUT - 0.01:
                continue
            sc.add(timp(55.0, 9400 + bar * 4 + int(beat * 10)), T(bar, beat), p=0.05, dry=g * gg, send='hall', wet=g * gg * 0.25)

    # high sul ponticello tremolo cluster: crescendo bars 17-24, cut dead
    for bar in range(17, 25):
        for m, pp in ((86, -0.5), (87, 0.5), (93, 0.0)):
            dur = BAR if bar < 24 else 3 * BEAT
            nn = bowed(midi(m), dur, 8000 + bar * 7 + m, cutoff=6000, voices=3, bow=0.18, spic=False, rel=0.03)
            nn = dsp.highpass(nn, 1200, 2)
            nn = nn * (0.55 + 0.45 * np.sin(TWO_PI * 13.0 * taxis(len(nn)))) ** 2
            g = 0.025 + 0.045 * (bar - 17)
            sc.add(nn, T(bar), p=pp, dry=g, send='hall', wet=g * 0.6)

    # reverse swells sucked into bar 19 and into the cut; booms on 15, 19, 23 and the cut
    for t_hit, seed in ((T(19), 9500), (CUT, 9550)):
        cl = prep_piano(36.71, seed) + 0.7 * prep_piano(77.78, seed + 1)
        rv = dsp.reverse(dsp.reverb(norm(cl), 3.0, 0.8, 3000, 0.02, seed + 2))
        rv = rv[-N(2 * BAR):] * np.linspace(0, 1, N(2 * BAR)) ** 1.6
        sc.add(norm(rv), t_hit - 2 * BAR, p=0.0, dry=0.3, send='hall', wet=0.06)
    for t_hit, g in ((T(15), 0.5), (T(19), 0.6), (T(23), 0.7), (CUT, 0.95)):
        sc.add(boom(9600 + int(t_hit)), t_hit, p=0.0, dry=g * 0.45, send='cave', wet=g * 0.1)
    last = prep_piano(36.71, 9700, bolt=1.0) + prep_piano(73.42, 9701, bolt=1.0) + 0.6 * prep_piano(77.78, 9702, bolt=1.0)
    sc.add(norm(last), CUT, p=0.0, dry=0.42, send='cave', wet=0.35)

    x = sc.mix()
    x = sfilt(x, hp=28, order=2)
    x = circ_limit(x, 14.0)
    # rotate so the file starts in the quietest 60 ms near bar 1 (master_loop keeps the seam itself fade-free)
    m = np.abs(x).mean(axis=1)
    e = uniform_filter1d(m, N(0.06), mode='wrap')
    cand = np.r_[np.arange(0, N(1.5)), np.arange(L - N(1.5), L)]
    i0 = int(cand[np.argmin(e[cand])])
    return np.roll(x, -i0, axis=0)


# ====================================================================== finishing
def finish_voice(y, peak_db, crest_db=15.0, trim_db=-50.0, tail=0.06):
    """Cap the crest factor (look-ahead limiter, <= 8 dB of reduction), trim dead air, soft end, master."""
    y = np.asarray(y, np.float32)
    act = rms_env(y, 0.02)
    a = act > np.max(act) * 10 ** (-30 / 20)
    level = float(np.sqrt(np.mean(y[a] ** 2))) if a.any() else rms(y)
    ceiling = level * 10 ** (crest_db / 20)
    pk = np.max(np.abs(y))
    if pk > ceiling:
        y = vlimit(y, max(ceiling, pk * 10 ** (-8 / 20)))
    y = dsp.trim(y, trim_db, tail)
    fl = min(len(y) // 4, N(0.1))
    y = y.copy()
    y[-fl:] *= np.linspace(1, 0, fl) ** 1.5
    return dsp.master(y, peak_db=peak_db)


def finish_sfx(y, peak_db, trim_db=-58.0, tail=0.05):
    """Trim dead air (keeping the reverb tail above trim_db), soft end, master."""
    y = dsp.trim(np.asarray(y, np.float32), trim_db, tail)
    fl = min(len(y) // 4, N(0.06))
    y = y.copy()
    y[-fl:] *= np.linspace(1, 0, fl) ** 1.5
    return dsp.master(y, peak_db=peak_db)


def finish_impact(y, peak_db, reduce_db=6.0):
    """Percussive foley whose single-sample snaps set the peak: a short look-ahead limiter takes `reduce_db` off the
    clicks (their attacks stay sharp) so the body reads as loud as the project's other impacts, then finish_sfx."""
    y = np.asarray(y, np.float32)
    return finish_sfx(vlimit(y, np.max(np.abs(y)) * 10 ** (-reduce_db / 20), 0.0015), peak_db)


def master_loop(x, peak_db, pad=2.0):
    """dsp.master for a seamless loop: master a wrap-padded copy and keep one period, so master's edge fades land in
    the discarded padding and its high-pass runs with the loop's own history (no dip at the loop point)."""
    p = N(pad)
    y = dsp.master(np.concatenate([x[-p:], x, x[:p]], axis=0), peak_db=peak_db)
    return y[p:p + len(x)]


def seam_report(x):
    m = x.mean(axis=1) if x.ndim == 2 else x
    d = np.abs(np.diff(m))
    return float(abs(m[0] - m[-1]) / (np.percentile(d, 75) + 1e-9))


# ====================================================================== build
def _demon(v):
    y, ref = demon_line(v)
    return finish_voice(y, -1.0, 15.0, -52.0, 0.08), ref


JOBS = [   # (event, file, renderer -> (array, reference or None))
    ('poseida.giggle', 'poseida/giggle_1', lambda: (finish_voice(poseida_giggle(1), -1.0, 15.0, -52.0), None)),
    ('poseida.giggle', 'poseida/giggle_2', lambda: (finish_voice(poseida_giggle(2), -1.0, 15.0, -52.0), None)),
    ('poseida.demon', 'poseida/demon_1', lambda: _demon(1)),
    ('poseida.demon', 'poseida/demon_2', lambda: _demon(2)),
    ('poseida.demon', 'poseida/demon_3', lambda: _demon(3)),
    ('poseida.demon', 'poseida/demon_4', lambda: _demon(4)),
    ('poseida.demon', 'poseida/demon_5', lambda: _demon(5)),
    ('poseida.crack', 'poseida/crack_1', lambda: (finish_impact(poseida_crack(1), -3.0), None)),
    ('poseida.crack', 'poseida/crack_2', lambda: (finish_impact(poseida_crack(2), -3.0), None)),
    ('poseida.scream', 'poseida/scream', lambda: (finish_voice(poseida_scream(), -0.5, 13.0, -55.0, 0.1), None)),
    ('poseida.hurt', 'poseida/hurt', lambda: (finish_voice(poseida_hurt(), -0.5, 13.0, -55.0, 0.08), None)),
    ('poseida.death', 'poseida/death', lambda: (finish_sfx(poseida_death(), -0.5, -60.0, 0.1), None)),
    ('sombra.appear', 'sombra/appear', lambda: (finish_sfx(sombra_appear(), -0.5, -55.0, 0.1), None)),
    ('sombra.vanish', 'sombra/vanish', lambda: (finish_sfx(sombra_vanish(), -3.0, -55.0, 0.08), None)),
    ('muneca.giggle', 'muneca/giggle_1', lambda: (finish_voice(muneca_giggle(1), -1.0, 16.0, -55.0, 0.1), None)),
    ('muneca.giggle', 'muneca/giggle_2', lambda: (finish_voice(muneca_giggle(2), -1.0, 16.0, -55.0, 0.1), None)),
    ('muneca.creak', 'muneca/creak', lambda: (finish_sfx(muneca_creak(), -3.0), None)),
    ('anima.moan', 'anima/moan_1', lambda: (finish_voice(anima_moan(1), -1.0, 15.0, -48.0, 0.15), None)),
    ('anima.moan', 'anima/moan_2', lambda: (finish_voice(anima_moan(2), -1.0, 15.0, -48.0, 0.15), None)),
    ('ambient.whispers', 'ambient/whispers_1', lambda: (finish_voice(ambient_whispers(1), -1.0, 16.0, -55.0, 0.1), None)),
    ('ambient.whispers', 'ambient/whispers_2', lambda: (finish_voice(ambient_whispers(2), -1.0, 16.0, -55.0, 0.1), None)),
    ('ambient.whispers', 'ambient/whispers_3', lambda: (finish_voice(ambient_whispers(3), -1.0, 16.0, -55.0, 0.1), None)),
    ('ambient.whispers', 'ambient/whispers_4', lambda: (finish_voice(ambient_whispers(4), -1.0, 16.0, -55.0, 0.1), None)),
    ('music.case', 'music/case', lambda: (master_loop(music_case(), -4.0), None)),
]


def build(only=None):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    t_all = time.time()
    stats_path = os.path.join(REVIEW_DIR, 'stats.json')
    stats = {}
    if os.path.exists(stats_path):
        try:
            stats = json.load(open(stats_path))
        except (ValueError, OSError):
            stats = {}
    for event, rel, fn in JOBS:
        if only and not any(o in rel or o in event for o in only):
            continue
        t0 = time.time()
        x, ref = fn()
        x = np.asarray(x, np.float32)
        if event != 'music.case':
            assert x.ndim == 1, rel + ' must be mono'
        q = 4 if x.ndim == 2 else 5
        dsp.save_ogg(x, rel, quality=q)
        # Vorbis can overshoot the PCM peak by ~0.5 dB on hot transients: re-master lower if the decoded file clips
        import soundfile as sf
        target = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
        dec = 20 * np.log10(np.max(np.abs(sf.read(os.path.join(dsp.OUT, rel + '.ogg'))[0])) + 1e-12)
        if dec > -0.1:
            x = (master_loop if event == 'music.case' else dsp.master)(x, peak_db=target - (dec - target) - 0.15)
            dsp.save_ogg(x, rel, quality=q)
            print(f'  {rel}: decoded peak {dec:+.2f} dBFS -> re-mastered at {target - (dec - target) - 0.15:.2f}')
        st = dsp.analyse(x)
        if x.ndim == 2:
            st['seam'] = round(seam_report(x), 2)
            seam = np.concatenate([x[-N(3):], x[:N(3)]])
            dsp.spectrogram_png(seam, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '_seam.png'), 600, 200)
        if ref is not None:
            lag = best_lag(ref, x, 0.3)
            st['stoi'] = round(stoi(np.pad(ref, (lag, max(0, len(x) - len(ref) - lag)))[:len(x)], x), 2)
        dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
        stats[rel] = st
        print(f'{rel:22s} {st}  ({time.time() - t0:.1f}s)', flush=True)
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=1)
    print(f'creatures group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
