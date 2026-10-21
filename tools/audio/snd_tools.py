# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "tools": the hunter's kit and the sanity hallucinations.

Run from the repo root:  python3 tools/audio/snd_tools.py [substring ...]

Every sound is built from physical models (modal resonators excited by contact pulses, stick-slip friction, Poisson
debris and crackle, turbulent noise through vocal-tract formants) or from Kokoro speech turned into a character.
All files are MONO (positional). In-game use it is sized to (see the Java items):

  sanity.heartbeat     one tight lub-dub (0.5 s), retriggered every 0.65-1.5 s as sanity drops.
  sanity.whisper (5)   a woman whispering right at your ear (rioplatense): "Estoy aca." / "Mira, atras." /
                       "No estas solo." (doubled by a second, lower whisper) / "Te estoy viendo." / "Veni... veni conmigo."
  sanity.footsteps (3) shoes on old floorboards: approaching / circling you / three heavy steps that stop behind you.
  sanity.knock (3)     knuckles on a door (slow x3) / inside the wall (knock-knock... knock-knock) / frantic fists.
  sanity.breath (2)    heavy breathing right behind your head: slow and deep / excited, wet and raspy.
  crucifix.activate    holy shimmer: celesta arpeggio, boys'-choir "aah" swell, sparkles, chapel air.
  crucifix.repel       holy blast: reverse swell -> boom + bell clang + choir burst, shock-wave whoosh, demon snarl.
  holy_water.throw     bottle grabbed (glass tick), liquid sloshing inside, whoosh past the ear.
  holy_water.splash    bottle hits the floor: crack, shatter, shards tinkling, splash, bubbles, drops.
  holy_water.sizzle    acid hiss on burning flesh (frying crackle, steam whistle) + the demon's pained growl.
  salt.place           salt poured from a box: sandy grain patter on the floor.
  emf.beep             short piezo beep (2.7 kHz); the meter retriggers it fast at pitch 0.8-1.55.
  flashlight.click     plastic slide switch: press + spring snap through the torch tube.
  flashlight.flicker   1 s: bad battery contact - arcing crackle, buzzing, filament ticks, stuttering on/off.
  spirit_box.static    1.5 s FM sweep: channel clicks, static, carrier whistles, chopped radio voices.
  spirit_box.voice (8) a ghost voice answering through the sweep: "Clara... Clara..." / "Ocho." / "Shhh." / "Mira." /
                       "Vacio." / "Te veo." / "Ayuda." / "Frio."  (the sweep ducks under the voice; words intact)
  camera.flash         old flash camera: shutter-button click, capacitor whine, xenon POP, recharge whine.
  ritual.chant         priests chanting "Exorcizamus te, omnis immundus spiritus" in organum (spoken words over a
                       cross-synthesised A2/E3/A1 chant), chapel; replayed every 5 s while praying.
  ritual.complete      holy release (swell -> bells + choir major chord) and the demon's scream dragged away.
  jar.capture          a soul sucked into a glass jar (vortex + shrinking wail), jar ring, cork squeak + pop.
  pills.swallow        pill bottle rattle, cap pop, pills in the palm, gulp, relieved exhale.
  flare.ignite         road flare struck on its cap, pops, ignition whoosh, settling into the burn.
  flare.burn           2.0 s seamless loop (FlareEntity retriggers it every 40 ticks): roaring hiss, crackle, sputter,
                       slag snaps, spits; mastered on three tiled periods (master_loop) so no fade touches the seam.

Loudness: screams/stingers -0.5 dBFS, voices -1 dBFS, foley/UI -3 dBFS, loops -4 dBFS. build() decodes every OGG it
writes and re-masters lower when the Vorbis encoder overshoots the target peak by more than 0.25 dB.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
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
    _os.path.join(WORK, 'audio/colegio_tools'))
TWO_PI = 2 * np.pi


# ====================================================================== small helpers
def N(sec):
    return dsp.n_of(sec)


def taxis(n):
    return np.arange(n) / SR


def fit(x, n):
    x = np.asarray(x, np.float32)
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def norm(x, peak=1.0):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def colored(n, color, seed):
    w = dsp.rng(seed).standard_normal(n)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    p = {'pink': 0.5, 'brown': 1.0, 'white': 0.0}[color]
    x = np.fft.irfft(np.fft.rfft(w) / f ** p, n)
    return (x / (np.std(x) + 1e-12)).astype(np.float32)


def snoise(n, cutoff, seed):
    """Smooth random control signal in about -1..1 (low-passed noise)."""
    w = white(n + 8192, seed)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def grain(n, cutoff, seed, power=2.0):
    """Positive rough-texture modulator with mean 1."""
    g = np.abs(dsp.lowpass(white(n + 4096, seed), cutoff, 2)[4096:]) ** power
    return (g / (np.mean(g) + 1e-9)).astype(np.float32)


def env_pts(n, pts):
    """Piecewise-linear envelope from [(seconds, gain), ...]."""
    return np.interp(np.arange(n), [p[0] * SR for p in pts], [p[1] for p in pts]).astype(np.float32)


def add(buf, x, t, g=1.0):
    """buf[t:] += g * x (clipped to buf)."""
    s = N(t) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        buf[s:s + m] += g * x[:m]
    return buf


def padsum(*parts):
    n = max(len(p) for p in parts)
    return sum(fit(p, n) for p in parts).astype(np.float32)


def half_sine(dur):
    n = max(2, N(dur))
    return np.sin(np.pi * (np.arange(n) + 0.5) / n).astype(np.float32)


def burst(dur, seed, shape=1.0):
    n = N(dur)
    return (white(n, seed) * np.linspace(1, 0, n) ** shape).astype(np.float32)


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
            sos = signal.butter(2, [max(20.0, lo) / nyq, min(0.98, hi / nyq)], 'bandpass', output='sos')
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[a:b], zi=zi)
        out[a:b] = y
    return out


def rms_env(x, win=0.02):
    return np.sqrt(uniform_filter1d(np.asarray(x, np.float64) ** 2, max(1, N(win))) + 1e-12).astype(np.float32)


def match_env(y, ref, win=0.02, lo=0.05, hi=8.0):
    n = min(len(y), len(ref))
    ey, er = rms_env(y[:n], win), rms_env(ref[:n], win)
    floor = 1e-3 * max(np.max(er), 1e-6)
    g = np.clip((er + floor) / (ey + floor), lo, hi)
    g = uniform_filter1d(g, N(win))
    return (y[:n] * g).astype(np.float32)


def shelf_lo(x, f, gain_db):
    return (x + (10 ** (gain_db / 20) - 1) * dsp.lowpass(x, f, 2)).astype(np.float32)


def shelf_hi(x, f, gain_db):
    return (x + (10 ** (gain_db / 20) - 1) * dsp.highpass(x, f, 2)).astype(np.float32)


def wobble(x, rate=0.6, depth_ms=1.0, seed=0, jitter_ms=0.0):
    """Variable delay line -> slow pitch wobble (ghostly / tape)."""
    n = len(x)
    t = taxis(n)
    d = depth_ms * 1e-3 * SR * 0.5 * (1 + np.sin(TWO_PI * rate * t + seed))
    if jitter_ms:
        d = d + jitter_ms * 1e-3 * SR * 0.5 * (1 + snoise(n, 4, seed + 11))
    idx = np.arange(n)
    return np.interp(idx - d, idx, x).astype(np.float32)


def poisson(lam, seed):
    """Event sample indices of an inhomogeneous Poisson process with per-sample rate lam (events/s)."""
    return np.nonzero(dsp.rng(seed).random(len(lam)) < np.asarray(lam) / SR)[0]


def pulse_train(n, idx, amps, kernel):
    imp = np.zeros(n, np.float32)
    np.add.at(imp, idx, amps)
    return signal.fftconvolve(imp, kernel)[:n].astype(np.float32)


def stick_slip(n, rate, seed, jitter=0.25, amp_env=None, amp_lo=0.35):
    """Friction pulse train: per-sample rate (Hz) -> (indices, amplitudes)."""
    r = dsp.rng(seed)
    rate = np.full(n, float(rate)) if np.ndim(rate) == 0 else np.asarray(rate, np.float64)[:n]
    jit = 1 + jitter * snoise(n, 25, seed + 1)
    ph = np.cumsum(np.maximum(rate * jit, 0)) / SR
    idx = np.nonzero(np.diff(np.floor(ph)))[0] + 1
    a = r.uniform(amp_lo, 1.0, len(idx))
    if amp_env is not None:
        a = a * amp_env[idx]
    return idx, a.astype(np.float32)


def additive_saw(f, n, fmax=9000.0, tilt=1.0, seed=0):
    """Band-limited saw by additive synthesis; f = Hz (number or per-sample array)."""
    f = np.broadcast_to(np.asarray(f, np.float64), (n,))
    ph = TWO_PI * np.cumsum(f) / SR + dsp.rng(seed).uniform(0, TWO_PI)
    k_max = max(1, int(fmax / max(np.max(f), 1)))
    y = np.zeros(n)
    for k in range(1, k_max + 1):
        y += np.sin(k * ph) / k ** tilt
    return y.astype(np.float32)


VOWELS = {
    # (centre Hz, half-bandwidth Hz, gain dB)
    'a': [(800, 130, 0), (1150, 150, -4), (2900, 200, -14), (3900, 250, -20)],
    'a_low': [(650, 110, 0), (1080, 140, -5), (2650, 200, -15)],
    'o': [(450, 90, 0), (800, 110, -6), (2830, 200, -20)],
    'u': [(325, 70, 0), (700, 90, -12), (2530, 170, -24)],
    'e': [(420, 90, 0), (2000, 140, -9), (2600, 180, -12)],
    'scream_f': [(1050, 170, 0), (1600, 200, -2), (2950, 260, -7), (4100, 350, -12)],
    'scream_m': [(750, 140, 0), (1250, 170, -3), (2600, 230, -9), (3500, 300, -14)],
}


def vowel(x, name, shift=1.0):
    out = np.zeros_like(x)
    for f, bw, g in VOWELS[name]:
        out += 10 ** (g / 20) * bp(x, max(30, (f - bw) * shift), (f + bw) * shift)
    return out


def vowel_morph(x, a, b, curve, shift=1.0):
    """Cross-fade between two vowel colourings with curve 0..1 (per sample)."""
    c = fit(curve, len(x))
    return (vowel(x, a, shift) * (1 - c) + vowel(x, b, shift) * c).astype(np.float32)


def glottal(f0, n, seed, jitter=0.01, shimmer=0.08, sub=0.0, breath=0.05, fmax=7000.0):
    """Voice source: band-limited saw with period jitter and shimmer, optional sub-harmonic fry, aspiration."""
    f0 = np.broadcast_to(np.asarray(f0, np.float64), (n,)).copy()
    f = f0 * (1 + jitter * snoise(n, 70, seed + 1))
    y = additive_saw(f, n, fmax, 1.0, seed)
    y = y * (1 + shimmer * snoise(n, 45, seed + 2))
    if sub:
        ph = np.cumsum(f) / SR
        y += sub * np.sign(np.sin(np.pi * ph + 0.3)) * 0.6
    if breath:
        # aspiration pulsed with the glottal cycle (what makes a growl or a rasp sound wet and real)
        ph = np.cumsum(f) / SR
        puls = 0.5 * (1 + np.cos(TWO_PI * ph)) ** 2
        y += breath * dsp.highpass(white(n, seed + 3), 600, 2) * (0.3 + puls) * np.std(y) * 2
    return y.astype(np.float32)


def growl(dur, f0_pts, seed, vow=('a_low', 'o'), shift=0.78, rough=0.06, sub=0.7, grit=3.5, morph_pts=None):
    """Demonic growl / pained roar: rough low voice, sub-harmonic fry, pulsed rasp, big vocal tract, saturation."""
    n = N(dur)
    f0 = env_pts(n, f0_pts)
    src = glottal(f0, n, seed, jitter=rough, shimmer=0.25, sub=sub, breath=0.6, fmax=6000)
    mp = morph_pts or [(0, 0), (dur, 1)]
    y = vowel_morph(src, vow[0], vow[1], env_pts(n, mp), shift)
    y = y + 0.25 * bp(src, 120, 400)
    y = dsp.drive(norm(y), grit)
    return dsp.lowpass(y, 6500, 2)


def scream(dur, f0_pts, seed, vow='scream_f', shift=1.0, rough=0.03, grit=2.5):
    n = N(dur)
    f0 = env_pts(n, f0_pts)
    f0 = f0 * (1 + 0.025 * np.sin(TWO_PI * 6.3 * taxis(n)) + 0.02 * snoise(n, 9, seed + 5))
    src = glottal(f0, n, seed, jitter=rough, shimmer=0.2, sub=0.0, breath=0.35, fmax=9000)
    y = vowel(src, vow, shift)
    y = dsp.drive(norm(y), grit)
    return dsp.lowpass(y, 9000, 2)


# ====================================================================== rooms
def ir_room(decay, damp=6000.0, predelay=0.0, early=(), lo=0.0, seed=0, build=0.01):
    r = dsp.rng(seed)
    pd = N(predelay)
    n = N(decay * 1.15) + pd + N(0.1)
    t = taxis(n - pd)
    tail = r.standard_normal(n - pd) * np.exp(-6.9 * t / decay)
    tail *= np.clip(t / max(build, 1e-3), 0, 1)
    tail = dsp.lowpass(tail.astype(np.float32), damp, 2)
    if lo:
        tail = dsp.highpass(tail, lo, 2)
    ir = np.zeros(n, np.float32)
    ir[pd:] = tail
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    er = None
    if early:
        er = np.zeros(n, np.float32)
        for ms, g in early:
            k = N(ms / 1000)
            if k < n:
                er[k] += g * (1 if r.random() < 0.6 else -1)
        er = dsp.lowpass(er, damp * 1.3, 2)
    return ir, er


def space(x, decay=0.5, wet=0.15, damp=6000.0, predelay=0.0, early=(), er_gain=0.4, lo=0.0, seed=0, dry=1.0, build=0.01):
    ir, er = ir_room(decay, damp, predelay, early, lo, seed, build)
    pad = np.concatenate([x, np.zeros(len(ir), np.float32)])
    y = dry * pad + wet * signal.fftconvolve(pad, ir)[:len(pad)]
    if er is not None:
        y += er_gain * signal.fftconvolve(pad, er)[:len(pad)]
    return y.astype(np.float32)


EAR_ER = [(0.9, 0.35), (1.6, 0.25), (2.4, 0.18)]                                    # head/shoulder, right at you
WOOD_ER = [(5.1, 0.5), (8.3, 0.4), (12.2, 0.33), (16.9, 0.27), (23.4, 0.2), (31.0, 0.15), (40.2, 0.1)]
CHAPEL_ER = [(17, 0.35), (26, 0.3), (38, 0.27), (47, 0.22), (61, 0.2), (74, 0.16), (89, 0.12), (107, 0.1)]
SMALL_ER = [(2.2, 0.4), (3.9, 0.3), (6.1, 0.22), (8.8, 0.15)]


def corridor(x, wet=0.3, seed=4, dry=1.0):
    """Old wooden-floored corridor/dormitory of the school."""
    return space(x, 1.5, wet, 4300, 0.006, WOOD_ER, 0.35, 120, seed, dry)


def chapel(x, wet=0.3, decay=3.4, seed=2, dry=1.0):
    return space(x, decay, wet, 4200, 0.03, CHAPEL_ER, 0.22, 200, seed, dry, build=0.04)


def finish(x, peak_db, thresh_db=-60.0, tail=0.06):
    x = dsp.trim(np.asarray(x, np.float32), thresh_db, tail)
    return dsp.master(x, peak_db)


# ====================================================================== mouth / breath / speech helpers
def breath_in(dur, seed, size=1.0, shaky=0.0):
    """Mouth inhale: band noise with whistly resonances. size > 1 = bigger person (lower)."""
    n = N(dur)
    r = dsp.rng(seed)
    a = bp(white(n, seed), 380 / size, 4600 / size, 4)
    f = r.uniform(1500, 1900) / size
    a = dsp.peak(a, f, 9, 3.5)
    a = dsp.peak(a, f * r.uniform(1.6, 1.8), 6, 3)
    a = dsp.peak(a, 650 / size, 3, 1.5)
    a = dsp.lowpass(a, 5200 / size, 4)
    a = a * (1 + 0.3 * snoise(n, 25, seed + 4))
    e = env_pts(n, [(0, 0), (dur * 0.3, 0.7), (dur * 0.82, 1.0), (dur, 0)]) ** 1.3
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * r.uniform(8, 12) * taxis(n))))
    return norm(a * e)


def breath_out(dur, seed, size=1.0, shaky=0.0):
    n = N(dur)
    b = colored(n, 'pink', seed)
    b = bp(b, 140 / size, 3400 / size, 4)
    b = dsp.peak(b, 620 / size, 7, 2)
    b = dsp.peak(b, 1150 / size, 5, 2.5)
    b = dsp.peak(b, 2450 / size, 3, 3)
    b = dsp.lowpass(b, 3800 / size, 4)
    b = b * (1 + 0.25 * snoise(n, 30, seed + 4))
    e = env_pts(n, [(0, 0), (dur * 0.1, 1.0), (dur * 0.45, 0.7), (dur, 0)])
    if shaky:
        e = e * (1 - shaky * 0.5 * (1 + np.sin(TWO_PI * 9.0 * taxis(n))))
    return norm(b * e)


def lip_click(seed, amp=1.0):
    """Wet tongue/lip tick right at the mic."""
    c = fit(bp(burst(0.003, seed, 2.0), 900, 5000), N(0.02))
    c = norm(c) + 0.5 * norm(modal_ir([(dsp.rng(seed).uniform(1500, 2400), 260, 1.0)], 0.02, seed))[:len(c)]
    return norm(c, amp)


def shush(dur, seed, size=1.0, force=1.0):
    """Human 'shhh': noise through the /sh/ resonances, with breath pressure and lip flutter."""
    n = N(dur)
    r = dsp.rng(seed)
    w = white(n, seed)
    fc = r.uniform(2500, 2900) / size
    y = bp(w, 1500 / size, 8500)
    y = dsp.peak(y, fc, 12, 2.2)
    y = dsp.peak(y, fc * 1.9, 5, 2.5)
    y = dsp.lowpass(y, 7500, 2) + 0.12 * dsp.highpass(w, 6000, 2)
    press = 1 + 0.25 * snoise(n, 6, seed + 1) + 0.06 * snoise(n, 40, seed + 2)
    e = env_pts(n, [(0, 0), (min(0.4 * dur, 0.07), 1.0), (dur * 0.55, 0.85 + 0.15 * force), (dur * 0.8, 0.7), (dur, 0)])
    return norm(y * e * press, force)


def to_whisper(x, seed=0, smooth=7, nper=1024):
    """Replace voicing by noise with the same spectral envelope (keeps the words, loses the pitch)."""
    _, _, Z = signal.stft(x, SR, nperseg=nper, noverlap=nper * 3 // 4)
    mag = uniform_filter1d(np.abs(Z), smooth, axis=0)
    ph = dsp.rng(seed).uniform(-np.pi, np.pi, Z.shape)
    _, y = signal.istft(mag * np.exp(1j * ph), SR, nperseg=nper, noverlap=nper * 3 // 4)
    y = dsp.highpass(fit(y, len(x)), 180, 2)
    y = dsp.peak(y, 4800, 3, 1.0)
    return match_env(y, x, 0.012)


def say(text, voice='ef_dora', speed=0.85):
    """Kokoro speech, edges trimmed, peak 0.8."""
    y = dsp.tts(text, voice, speed)
    y = dsp.highpass(y, 60, 2)
    y = dsp.trim(y, -46, 0.03)
    return norm(dsp.fade(y, 0.003, 0.012), 0.8)


# ====================================================================== sanity hallucinations
def heartbeat():
    """lub (S1: longer, lower) + dub (S2: shorter, higher, snappier), felt from inside the chest."""
    n = N(0.5)
    out = np.zeros(n, np.float32)

    def thump(dur, f_hi, f_lo, decay, seed, valve):
        m = N(dur)
        t = taxis(m)
        f = f_lo + (f_hi - f_lo) * np.exp(-t * 32)
        ph = TWO_PI * np.cumsum(f) / SR
        e = np.exp(-t * decay) * np.minimum(1, t / 0.007) ** 1.5
        body = np.sin(ph) * e + 0.32 * np.sin(2 * ph + 0.6) * e ** 1.6 + 0.12 * np.sin(3 * ph + 1.1) * e ** 2.2
        # valve snap: a short band of noise at the start (what makes it a *beat* and not a sine)
        v = bp(white(m, seed), 70, 420) * np.exp(-t * 55) * np.minimum(1, t / 0.0025)
        return (norm(body) + valve * norm(v)).astype(np.float32)

    add(out, thump(0.22, 74, 44, 21, 1, 0.42), 0.006, 1.0)
    add(out, thump(0.17, 96, 60, 30, 2, 0.55), 0.2, 0.8)
    # blood swish between the beats (very low)
    sw = dsp.lowpass(colored(n, 'pink', 3), 260, 2) * env_pts(n, [(0, 0), (0.05, 0.2), (0.2, 0.05), (0.26, 0.16), (0.42, 0.0), (0.5, 0)])
    out = out + 0.5 * norm(sw) * 0.35
    y = dsp.lowpass(out, 800, 2)
    y = dsp.peak(y, 115, 4.5, 1.2)          # chest resonance: keeps it audible on small speakers
    y = dsp.drive(norm(y) * 1.4, 1.8)         # tissue saturation -> 2nd/3rd harmonics around 150-300 Hz
    return fit(y, n)


WHISPERS = [
    # (text, seed, double_voice, slow_echo)
    ('Estoy acá.', 11, False, False),
    ('Mirá, atrás.', 12, False, False),      # QA: the comma keeps "mirá" and "atrás" apart (ASR heard "miraba atrás")
    ('No estás solo.', 13, True, False),
    ('Te estoy viendo.', 14, False, False),
    ('Vení... vení conmigo.', 15, False, True),
]


def whisper_voice(text, seed, voice='ef_dora', speed=0.85, keep=0.1):
    v = say(text, voice, speed)
    w = to_whisper(v, seed)
    # a breath of the voiced original above 1.4 kHz keeps the consonants and vowels crisp (stage whisper)
    y = norm(w) + keep * norm(dsp.highpass(v, 1400, 2))
    y = shelf_lo(y, 260, 5.0)               # proximity effect: lips 3 cm from your ear
    y = dsp.peak(y, 6500, 3.0, 1.0)          # air
    y = wobble(y, 0.7, 0.6, seed, 0.6)
    return norm(y)


def sanity_whisper(i):
    text, seed, double, echo_ = WHISPERS[i]
    r = dsp.rng(seed)
    w = whisper_voice(text, seed)
    pre = 0.42
    n = N(pre) + len(w) + N(0.9)
    out = np.zeros(n, np.float32)
    add(out, breath_in(0.32, seed + 1, 1.0), 0.02, 0.11)
    add(out, lip_click(seed + 2, 0.18), pre - 0.06)
    add(out, w, pre, 1.0)
    if double:
        # a second, lower whisper a hair behind the first: "no estas solo" said by two mouths. QA: it is time-aligned
        # to the first voice and kept below 2.8 kHz, so its sibilants no longer smear the final 's' of "estás"
        # (whisper-base ASR heard "no está solo" before, "no estás solo" now).
        v2 = say(text, 'em_alex', 0.85)
        v2 = dsp.time_stretch(v2, len(v2) / max(1, len(say(text, 'ef_dora', 0.85))))
        w2 = to_whisper(v2, seed + 7)
        w2 = dsp.lowpass(shelf_lo(norm(w2), 300, 3.0), 2800, 2)
        add(out, norm(w2), pre + 0.03, 0.38)
    t_end = pre + len(w) / SR
    add(out, breath_out(r.uniform(0.45, 0.6), seed + 3, 1.0), t_end + 0.04, 0.1)
    if echo_:
        tail = dsp.lowpass(out, 3500, 2)
        out = padsum(out, 0.22 * fit(np.concatenate([np.zeros(N(0.33), np.float32), tail]), len(out) + N(0.33)))
    y = space(out, 0.45, 0.06, 5000, 0.002, EAR_ER, 0.3, 150, seed)
    return y


WOOD_FLOOR = [(92, 28, 1.0), (171, 36, .75), (243, 45, .55), (388, 60, .45), (547, 75, .32), (820, 95, .22),
              (1240, 130, .14), (1830, 170, .08), (2600, 230, .05)]
CREAK_MODES = [(330, 55, 1.0), (612, 70, .7), (1040, 95, .5), (1690, 130, .3), (2480, 180, .15)]


def board_creak(dur, seed, rate=(85, 40), amp=1.0):
    """Floorboard creak: stick-slip of nail/board through wood resonances."""
    r = dsp.rng(seed)
    n = N(dur)
    rate_c = env_pts(n, [(0, rate[0]), (dur * 0.4, (rate[0] + rate[1]) / 2 * r.uniform(0.9, 1.15)), (dur, rate[1])])
    e = env_pts(n, [(0, 0), (dur * 0.2, 1.0), (dur * 0.65, 0.8), (dur, 0)])
    idx, a = stick_slip(n, rate_c, seed, 0.3, e, 0.5)
    k = modal_ir(detune(CREAK_MODES, r, 0.08), 0.06, seed)
    y = pulse_train(n + N(0.06), idx, a, k)
    return norm(y, amp)


def wood_step(seed, weight=1.0, creak=0.0, scuff=0.5):
    """One shoe on old floorboards: heel thud into the boards, toe roll, sole scuff, optional board creak."""
    r = dsp.rng(seed)
    dur = 0.55 + creak * 0.55
    n = N(dur)
    y = np.zeros(n, np.float32)
    modes = [(f / weight ** 0.25, d, a) for f, d, a in WOOD_FLOOR]
    exc = np.zeros(N(0.35), np.float32)
    hs = half_sine(0.0045 * weight ** 0.3)
    exc[:len(hs)] = hs
    exc[:N(0.004)] += 0.08 * white(N(0.004), seed + 1)
    heel = excite(exc, detune(modes, r, 0.04), 0.35, seed)
    heel = norm(heel)
    cl = dsp.highpass(burst(0.002, seed + 5, 2.0), 1500, 2)
    heel[:len(cl)] += 0.25 * norm(cl)
    add(y, heel, 0.0, 1.0)
    t_toe = r.uniform(0.06, 0.1) * weight ** 0.5
    exc2 = np.zeros(N(0.2), np.float32)
    hs2 = half_sine(0.003)
    exc2[:len(hs2)] = hs2
    toe = norm(excite(exc2, detune([(f * 1.2, d * 1.2, a) for f, d, a in modes], r, 0.05), 0.2, seed + 3))
    add(y, toe, t_toe, r.uniform(0.3, 0.45))
    if scuff:
        m = N(0.07)
        sc = bp(white(m, seed + 6), 900, 5200) * grain(m, 900, seed + 7, 1.5) * env_pts(m, [(0, 0), (0.01, 1), (0.07, 0)])
        add(y, norm(sc), t_toe - 0.01, 0.12 * scuff)
    if creak:
        cr = board_creak(r.uniform(0.25, 0.45) * (0.7 + creak), seed + 9, (r.uniform(70, 110), r.uniform(30, 45)))
        add(y, cr, r.uniform(0.04, 0.1), 0.22 * min(creak, 1.0) ** 0.7)
    return y


def walk(steps, seed, total, room_wet=0.35):
    """steps = [(time, distance 0..1, weight, creak)] -> distance-filtered steps in the wooden corridor."""
    n = N(total)
    dry = np.zeros(n, np.float32)
    send = np.zeros(n, np.float32)
    for i, (t, d, w, c) in enumerate(steps):
        s = wood_step(seed + 31 * i, w, c, 0.6 - 0.4 * d)
        lp = 9000 * (1800 / 9000) ** d
        s = dsp.lowpass(s, lp, 2)
        g = 1.0 / (0.75 + 1.3 * d)
        add(dry, s, t, g)
        add(send, s, t, g * (0.25 + 0.9 * d))
    rv = corridor(send, 1.0, seed, dry=0.0)
    return padsum(dry, room_wet * rv)


def sanity_footsteps(i):
    if i == 0:      # approaching from the end of the corridor, slowly, and stopping close
        st = [(0.0, 0.95, 1.0, 0.0), (0.68, 0.75, 1.0, 0.3), (1.34, 0.52, 1.0, 0.0), (2.0, 0.3, 1.0, 0.0), (2.7, 0.12, 1.05, 0.9)]
        return walk(st, 100, 4.6)
    if i == 1:      # circling: passes behind you and away again (head-shadow brightness changes)
        st = [(0.0, 0.55, 0.9, 0.0), (0.5, 0.36, 0.9, 0.0), (1.0, 0.2, 0.9, 0.5), (1.52, 0.33, 0.9, 0.0), (2.05, 0.52, 0.9, 0.0)]
        return walk(st, 200, 3.8, 0.4)
    # three heavy, deliberate steps that stop right behind you; the last board groans
    st = [(0.0, 0.6, 1.4, 0.4), (0.95, 0.32, 1.4, 0.0), (1.95, 0.08, 1.5, 1.4)]
    return walk(st, 300, 4.0, 0.3)


DOOR_MODES = [(98, 30, 1.0), (186, 38, .8), (274, 48, .6), (402, 60, .55), (611, 75, .4), (870, 95, .3),
              (1180, 120, .22), (1650, 160, .14), (2350, 220, .08), (3300, 300, .04)]


def knock_hit(seed, kind='knuckle', amp=1.0):
    r = dsp.rng(seed)
    contact = {'knuckle': 0.0008, 'fist': 0.0028, 'wall': 0.0012}[kind]
    modes = DOOR_MODES if kind != 'wall' else [(f * 0.85, d * 1.6, a) for f, d, a in DOOR_MODES[:7]]
    exc = np.zeros(N(0.4), np.float32)
    hs = half_sine(contact * r.uniform(0.85, 1.15))
    exc[:len(hs)] = hs
    y = norm(excite(exc, detune(modes, r, 0.03), 0.4, seed))
    if kind == 'knuckle':
        cl = dsp.highpass(burst(0.0015, seed + 7, 2.0), 1800, 2)
        y[:len(cl)] += 0.45 * norm(cl)
    if kind == 'wall':      # knuckle on lath and plaster: a dull, short tick on top of the thud
        cl = bp(burst(0.004, seed + 7, 1.5), 700, 2600)
        y[:len(cl)] += 0.35 * norm(cl)
    if kind == 'fist':
        # thump of the door in its frame + latch rattle
        add(y, norm(dsp.lowpass(burst(0.03, seed + 8, 3.0), 260, 2)), 0.0, 0.5)
        rat = np.zeros(len(y), np.float32)
        for j in range(int(r.integers(2, 4))):
            ping = modal_ir([(r.uniform(2200, 3400), 260, 1.0), (r.uniform(3900, 5200), 340, 0.6), (r.uniform(6000, 7500), 450, 0.3)], 0.03, seed + j)
            ping[:N(0.001)] += 0.5 * dsp.highpass(burst(0.001, seed + 20 + j, 2), 2000, 2)
            add(rat, ping, r.uniform(0.006, 0.03) + 0.012 * j, r.uniform(0.3, 0.6))
        y += 0.1 * norm(rat)
    return norm(y, amp)


def sanity_knock(i):
    r = dsp.rng(400 + i)
    if i == 0:      # slow: three even, deliberate knuckle knocks on the door
        n = N(3.6)
        y = np.zeros(n, np.float32)
        for k, t in enumerate([0.0, 0.95, 1.9]):
            add(y, knock_hit(410 + k, 'knuckle', 1.0 - 0.05 * k), t)
        return corridor(dsp.lowpass(y, 5000, 2), 0.32, 5)
    if i == 1:      # double, from INSIDE the wall: muffled, heavier ... knock-knock ... knock-knock
        n = N(3.2)
        y = np.zeros(n, np.float32)
        for k, t in enumerate([0.0, 0.19, 1.15, 1.34]):
            add(y, knock_hit(420 + k, 'wall', 1.0 if k % 2 == 0 else 0.85), t)
        y = dsp.lowpass(y, 2200, 2)
        y = dsp.peak(y, 520, 5.0, 1.2)        # the plaster/lath panel: what makes it read as 'inside the wall'
        y = shelf_lo(y, 160, 3.0)
        return space(y, 0.6, 0.18, 2500, 0.004, SMALL_ER, 0.4, 80, 6)
    # frantic: fists pounding, accelerating, rattling the latch, then a dead stop
    n = N(3.0)
    y = np.zeros(n, np.float32)
    t = 0.0
    k = 0
    while t < 1.95:
        dt = 0.17 - 0.05 * min(1, t / 1.5) + r.uniform(-0.025, 0.025)
        add(y, knock_hit(430 + k, 'fist', r.uniform(0.7, 1.0)), t)
        if r.random() < 0.25:      # a flam: the second fist lands right after
            add(y, knock_hit(470 + k, 'fist', r.uniform(0.35, 0.55)), t + r.uniform(0.035, 0.055))
        t += dt
        k += 1
    return corridor(dsp.lowpass(y, 4500, 2), 0.3, 7)


def rasp(dur, seed, f0=82.0, amt=1.0):
    """Throat rasp under an exhale: very rough, low, pulsed."""
    n = N(dur)
    f = f0 * (1 + 0.1 * snoise(n, 3, seed + 1))
    src = glottal(f, n, seed, jitter=0.035, shimmer=0.45, sub=0.15, breath=0.45, fmax=4000)
    y = vowel(src, 'a_low', 0.85) + 0.3 * bp(src, 90, 350)
    return norm(dsp.drive(norm(y), 2.0), amt)


def sanity_breath(i):
    if i == 0:      # slow, deep, big chest: in ... out (rasp) ... in ... long out
        seq = [('in', 0.95), ('gap', 0.12), ('out', 1.25), ('gap', 0.35), ('in', 0.85), ('gap', 0.1), ('out', 1.5)]
        size, shaky, rasp_amt, seed = 1.25, 0.15, 0.8, 500
    else:           # excited, wet, ragged: fast shallow cycles with a rattle
        seq = [('in', 0.42), ('out', 0.5), ('gap', 0.06), ('in', 0.38), ('out', 0.46), ('gap', 0.05), ('in', 0.4),
               ('out', 0.55), ('gap', 0.08), ('in', 0.5), ('out', 0.8)]
        size, shaky, rasp_amt, seed = 1.15, 0.5, 0.65, 520
    r = dsp.rng(seed)
    total = sum(d for _, d in seq) + 0.3
    out = np.zeros(N(total), np.float32)
    t = 0.05
    for j, (kind, d) in enumerate(seq):
        if kind == 'in':
            b = breath_in(d, seed + j, size, shaky)
            add(out, b, t, r.uniform(0.6, 0.75))
        elif kind == 'out':
            b = breath_out(d, seed + j, size, shaky)
            ra = rasp(d, seed + 50 + j, r.uniform(72, 95)) * env_pts(N(d), [(0, 0), (d * 0.15, 1), (d * 0.6, 0.6), (d, 0)])
            add(out, norm(b) + rasp_amt * ra, t, 1.0)
            # saliva crackle
            m = N(d)
            ci = poisson(np.full(m, 18.0 if i == 0 else 40.0), seed + 70 + j)
            cr = pulse_train(m, ci, dsp.rng(seed + j).uniform(0.2, 1, len(ci)).astype(np.float32),
                             dsp.highpass(burst(0.0015, seed + 80, 2), 2500, 2))
            add(out, cr, t, 0.12)
        t += d
    y = shelf_lo(dsp.highpass(out, 90, 2), 220, 4.0)     # right at your neck
    y = dsp.lowpass(y, 6500, 2)              # behind the head: a little shadowed
    return space(y, 0.5, 0.07, 4500, 0.002, EAR_ER, 0.35, 120, seed)


# ====================================================================== holy tools
def chime(f, dur, seed, decay=2.2, bright=1.0):
    """Celesta / glass-bell note with a slow beating twin for shimmer."""
    r = dsp.rng(seed)
    modes = []
    for ratio, a, dm in [(1.0, 1.0, 1.0), (2.0, 0.35 * bright, 1.6), (3.0, 0.12 * bright, 2.4), (4.07, 0.08 * bright, 3.0), (5.98, 0.03 * bright, 4.0)]:
        modes.append((f * ratio, decay * dm, a))
        modes.append((f * ratio * (1 + r.uniform(0.0015, 0.004)), decay * dm, a * 0.7))
    y = modal_ir(modes, dur, seed)
    a = N(0.002)
    y[:a] *= np.linspace(0, 1, a)
    return norm(y)


def choir(notes, dur, seed, vow='a', env=None, vib=0.006, detunes=(-0.004, 0.0, 0.0045), fmax=8000.0):
    """'Aah' pad: detuned band-limited saws with vibrato through vowel formants."""
    n = N(dur)
    r = dsp.rng(seed)
    t = taxis(n)
    y = np.zeros(n, np.float32)
    for j, f in enumerate(notes):
        for k, dt in enumerate(detunes):
            rate = r.uniform(4.6, 5.6)
            fr = f * (1 + dt) * (1 + vib * np.sin(TWO_PI * rate * t + r.uniform(0, 6)) + 0.002 * snoise(n, 2, seed + 10 * j + k))
            y += additive_saw(fr, n, fmax, 1.0, seed + 10 * j + k) * (1.0 if k == 1 else 0.7)
    y = vowel(y, vow) + 0.15 * dsp.highpass(y, 3000, 2) * 0.3
    y = y + 0.025 * bp(white(n, seed + 99), 2000, 6000) * np.std(y) * 3    # breath of the singers
    if env is not None:
        y = y * fit(env, n)
    return norm(y)


def sparkles(dur, seed, rate_pts, fmin=3500, fmax=9500):
    n = N(dur)
    r = dsp.rng(seed)
    lam = env_pts(n, rate_pts)
    out = np.zeros(n + N(0.2), np.float32)
    for k in poisson(lam, seed):
        f = r.uniform(fmin, fmax)
        p = modal_ir([(f, r.uniform(25, 60), 1.0), (f * 2.7, 90, 0.2)], 0.15, int(k))
        out[k:k + len(p)] += p * r.uniform(0.2, 1.0)
    return out[:n]


def crucifix_activate():
    dur = 2.6
    n = N(dur)
    y = np.zeros(n, np.float32)
    # celesta arpeggio up a Dadd9 chord
    notes = [587.33, 739.99, 880.0, 1174.66, 1318.51, 1760.0]
    for j, f in enumerate(notes):
        add(y, chime(f, dur - 0.05, 600 + j, 2.0 + 0.3 * j), 0.02 + 0.055 * j, 0.55 - 0.04 * j)
    # boys' choir "aah" swelling in under it
    e = env_pts(n, [(0, 0), (0.35, 0.8), (0.7, 1.0), (1.4, 0.55), (dur, 0)])
    add(y, choir([293.66, 440.0, 587.33, 739.99], dur, 610, 'a', e), 0.0, 0.5)
    # a few sparkles + rising air
    add(y, sparkles(dur, 620, [(0, 0), (0.25, 14), (0.9, 8), (1.6, 0), (dur, 0)], 3000, 7000), 0.0, 0.12)
    air = colored(n, 'white', 630)
    air = tv_filter(air, 'bp', env_pts(n, [(0, 1200), (0.6, 5000), (dur, 4000)]), 64, 1.0)
    add(y, norm(air) * env_pts(n, [(0, 0), (0.4, 1), (0.9, 0.3), (2.0, 0)]), 0.0, 0.06)
    return chapel(y, 0.32, 2.2, 640)


def crucifix_repel():
    dur = 2.8
    n = N(dur)
    t0 = 0.16
    y = np.zeros(n, np.float32)
    # reverse swell into the hit
    rs = chime(1174.66, 0.6, 700, 3.0)[:N(t0)][::-1] * np.linspace(0, 1, N(t0)) ** 2
    rn = dsp.highpass(white(N(t0), 701), 2000, 2) * np.linspace(0, 1, N(t0)) ** 3
    add(y, norm(rs) + 0.5 * norm(rn), 0.0, 0.5)
    # boom
    m = N(1.2)
    tt = taxis(m)
    fb = 32 + 46 * np.exp(-tt * 9)
    boom = np.sin(TWO_PI * np.cumsum(fb) / SR) * np.exp(-tt * 4.5) * np.minimum(1, tt / 0.003)
    thump = dsp.lowpass(burst(0.09, 702, 2.0), 220, 2)
    add(y, dsp.drive(norm(boom) + 0.6 * norm(fit(thump, m)), 2.0), t0, 1.0)
    # bell clang (struck hard) + a fifth above
    bell = modal_ir([(392.0, 3.0, 1.0), (392 * 2.0, 4.5, 0.8), (392 * 2.4, 6, 0.5), (392 * 3.0, 6.5, 0.45), (392 * 4.2, 9, 0.3),
                     (392 * 5.4, 12, 0.2), (392 * 6.8, 16, 0.12), (196, 1.5, 0.4)], 2.0, 703)
    bell2 = modal_ir([(587.33, 3.5, 1.0), (587.33 * 2.0, 5, 0.6), (587.33 * 3.0, 8, 0.3), (587.33 * 4.2, 11, 0.2)], 2.0, 704)
    cl = dsp.highpass(burst(0.003, 705, 2), 2500, 2)
    add(y, norm(bell) + 0.5 * norm(bell2) + 0.4 * norm(fit(cl, len(bell))), t0, 0.8)
    # choir burst (G major, open "ah")
    e = env_pts(N(1.6), [(0, 0), (0.025, 1.0), (0.3, 0.6), (1.6, 0)])
    add(y, choir([196.0, 293.66, 392.0, 493.88, 587.33], 1.6, 706, 'a', e, vib=0.008), t0, 0.75)
    # shock-wave whoosh pushing outward
    m = N(1.1)
    wsh = tv_filter(white(m, 707), 'bp', env_pts(m, [(0, 3500), (0.25, 1400), (1.1, 250)]), 64, 1.4)
    add(y, norm(wsh) * env_pts(m, [(0, 0), (0.02, 1), (0.3, 0.5), (1.1, 0)]), t0, 0.2)
    # the demon recoils: snarl/hiss swallowed as it is shoved back
    g = growl(0.75, [(0, 120), (0.15, 165), (0.75, 70)], 708, ('a', 'o'), 0.75, 0.07, 0.6, 3.5)
    g = tv_filter(g, 'lp', env_pts(len(g), [(0, 5000), (0.75, 600)]), 48)
    g = g * env_pts(len(g), [(0, 0), (0.03, 1), (0.4, 0.6), (0.75, 0)])
    add(y, norm(g), t0 + 0.07, 0.38)
    return chapel(y, 0.32, 2.8, 709)


def glass_ping(seed, f, decay=None, amp=1.0, click=0.5):
    r = dsp.rng(seed)
    decay = decay or (25 + f * 0.012) * r.uniform(0.7, 1.4)
    ratios = [1.0, r.uniform(1.45, 1.62), r.uniform(2.2, 2.5), r.uniform(3.0, 3.6)]
    amps = [1.0, r.uniform(.4, .8), r.uniform(.25, .5), r.uniform(.1, .3)]
    dur = min(0.7, 6.5 / decay)
    y = modal_ir([(f * ra, decay * ra ** 0.6, a) for ra, a in zip(ratios, amps)], dur, seed)
    y = norm(y * np.minimum(1, taxis(len(y)) / 0.0002))
    if click:
        cl = dsp.highpass(burst(0.0008, seed + 3, 2.0), 3000, 2)
        y[:len(cl)] += click * norm(cl)
    return (y * amp).astype(np.float32)


def bubble(f0, seed, rise=0.5, amp=1.0, dmul=1.0):
    r = dsp.rng(seed)
    d = (40 + f0 * 0.05) * dmul
    dur = min(0.15, 6.5 / d)
    t = taxis(N(dur))
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.001)
    return (y * amp).astype(np.float32)


def holy_water_throw():
    dur = 0.9
    n = N(dur)
    r = dsp.rng(800)
    y = np.zeros(n, np.float32)
    # bottle taken from the belt: glass tick against the cross / buckle
    add(y, glass_ping(801, 2350, 70, 1.0, 0.6), 0.0, 0.25)
    # slosh inside the bottle: clustered bubbles + liquid noise, muffled by the glass
    m = N(0.45)
    lam = env_pts(m, [(0, 0), (0.05, 90), (0.2, 160), (0.45, 20)])
    sl = np.zeros(m + N(0.2), np.float32)
    for k in poisson(lam, 802):
        b = bubble(r.uniform(320, 1100), int(k), r.uniform(0.3, 0.9), r.uniform(0.3, 1.0))
        sl[k:k + len(b)] += b
    liq = bp(white(m, 803), 300, 2000) * grain(m, 40, 804, 2.0) * env_pts(m, [(0, 0), (0.08, 1), (0.45, 0)])
    sl[:m] += 0.25 * norm(liq) * np.max(np.abs(sl))
    sl = dsp.lowpass(sl, 2600, 2)
    sl = dsp.peak(sl, 1300, 5, 3)            # bottle cavity
    add(y, norm(sl), 0.05, 0.55)
    # whoosh: arm swing then the bottle flying past the ear (doppler-ish bandpass hump)
    m = N(0.5)
    w = white(m, 805)
    lo = tv_filter(w, 'bp', env_pts(m, [(0, 250), (0.22, 700), (0.5, 300)]), 48, 1.6)
    hi = tv_filter(w, 'bp', env_pts(m, [(0, 1200), (0.2, 3800), (0.5, 1500)]), 48, 1.2)
    e = env_pts(m, [(0, 0), (0.16, 0.6), (0.24, 1.0), (0.32, 0.35), (0.5, 0)]) ** 1.5
    add(y, (norm(lo) + 0.6 * norm(hi)) * e, 0.2, 0.9)
    return space(y, 0.35, 0.05, 5000, 0.003, SMALL_ER, 0.2, 100, 806)


def holy_water_splash():
    dur = 1.6
    n = N(dur)
    r = dsp.rng(900)
    y = np.zeros(n, np.float32)
    # impact: bottle base on the floor (thud) + the crack
    th = knock_hit(901, 'wall', 1.0)
    add(y, dsp.lowpass(th, 900, 2), 0.0, 0.45)
    crack = dsp.highpass(burst(0.006, 902, 1.5), 1200, 2)
    add(y, norm(crack), 0.0, 0.9)
    # shatter: dense glass pings decaying, then tinkling shards bouncing away
    for k in range(70):
        tt = r.exponential(0.06)
        f = r.uniform(1800, 9000)
        add(y, glass_ping(910 + k, f, None, r.uniform(0.2, 1.0) * np.exp(-tt * 4), 0.6), 0.002 + tt, 0.32)
    for k in range(10):
        tt = r.uniform(0.2, 0.95)
        add(y, glass_ping(990 + k, r.uniform(2500, 7000), None, r.uniform(0.1, 0.3), 0.8), tt, 0.4)
    # splash: water burst
    m = N(0.6)
    sp = bp(white(m, 903), 250, 5500) * grain(m, 120, 904, 1.6) * env_pts(m, [(0, 0), (0.006, 1), (0.08, 0.55), (0.6, 0)]) ** 1.3
    sp = dsp.peak(sp, 900, 4, 1.2)
    sp = sp + 0.6 * norm(dsp.lowpass(sp, 700, 2)) * np.max(np.abs(sp))     # the body of water hitting the floor
    add(y, norm(sp), 0.004, 1.0)
    # bubbles and drops
    m = N(1.0)
    lam = env_pts(m, [(0, 250), (0.15, 80), (0.6, 15), (1.0, 3)])
    bb = np.zeros(m + N(0.2), np.float32)
    for k in poisson(lam, 905):
        bb[k:k + N(0.15)] += fit(bubble(r.uniform(450, 2000), int(k) + 3, r.uniform(0.4, 1.2), r.uniform(0.2, 1.0)), N(0.15))
    add(y, norm(bb), 0.01, 0.55)
    return corridor(y, 0.22, 906)


def holy_water_sizzle():
    dur = 2.1
    n = N(dur)
    r = dsp.rng(1000)
    y = np.zeros(n + N(0.9), np.float32)
    env = env_pts(n, [(0, 0), (0.015, 1.0), (0.6, 0.85), (1.2, 0.45), (dur, 0)])
    # acid hiss: bright noise with frying-pan crackle texture
    h = dsp.highpass(white(n, 1001), 1800, 2)
    h = dsp.peak(h, 4500, 6, 1.5)
    h = dsp.peak(h, 7200, 4, 2)
    h = dsp.lowpass(h, 9000, 2)
    h = h * (0.45 + grain(n, 300, 1002, 2.5) * 0.55)
    add(y, norm(h * env), 0.0, 0.65)
    # pops
    lam = 300 * env ** 1.5
    idx = poisson(lam, 1003)
    amps = (r.pareto(2.5, len(idx)) + 0.2).astype(np.float32)
    amps = np.minimum(amps, 4.0)
    pops = pulse_train(n, idx, amps, dsp.highpass(burst(0.0012, 1004, 2), 2000, 2))
    add(y, norm(pops), 0.0, 0.35)
    # steam whistle
    st = tv_filter(white(n, 1005), 'bp', env_pts(n, [(0, 3200), (0.8, 4200), (dur, 3600)]), 64, 0.15)
    add(y, norm(st) * env, 0.0, 0.08)
    # low fizz of boiling bubbles
    m = n
    bb = np.zeros(m + N(0.2), np.float32)
    for k in poisson(60 * env, 1006):
        bb[k:k + N(0.15)] += fit(bubble(r.uniform(500, 1600), int(k) + 9, 0.6, r.uniform(0.3, 1.0)), N(0.15))
    add(y, norm(bb), 0.0, 0.12)
    # QA: the burn layers sat 16 dB (RMS) under the growl, so the event read as a growl with a faint hiss. +9.5 dB puts
    # the acid hiss ~6 dB under the growl: both are heard, the hiss owning 2-9 kHz and the growl 100-1500 Hz.
    y = (0.8 * np.tanh(3.0 * y / 0.8)).astype(np.float32)      # soft-limited so the frying peaks don't set the master gain
    # the pained growl: catches its breath, rises in pain, falls into a snarl
    g = growl(1.45, [(0, 90), (0.12, 150), (0.35, 175), (0.8, 120), (1.45, 72)], 1007, ('a_low', 'o'), 0.78, 0.07, 0.6, 3.2,
              [(0, 0), (0.6, 0.2), (1.45, 1.0)])
    g = g * env_pts(len(g), [(0, 0), (0.04, 1), (0.5, 0.9), (1.1, 0.5), (1.45, 0)])
    sh = scream(1.0, [(0, 280), (0.2, 430), (0.6, 360), (1.0, 220)], 1008, 'scream_m', 0.9, 0.05, 3.0)
    sh = sh * env_pts(len(sh), [(0, 0), (0.06, 1), (0.5, 0.6), (1.0, 0)])
    vo = padsum(norm(g), 0.35 * norm(sh))
    vo = space(vo, 0.9, 0.18, 3500, 0.01, SMALL_ER, 0.3, 80, 1009)
    add(y, norm(vo), 0.05, 1.0)
    return y


def salt_place():
    dur = 1.15
    n = N(dur)
    r = dsp.rng(1100)
    y = np.zeros(n, np.float32)
    # the box is tipped: cardboard shk
    m = N(0.07)
    shk = bp(white(m, 1101), 1500, 7000) * grain(m, 2000, 1102, 2.0) * env_pts(m, [(0, 0), (0.008, 1), (0.07, 0)])
    add(y, norm(shk), 0.0, 0.3)
    # grains: a stream of tiny impacts on the floorboards; the flow pulses as the box is tilted
    flow = env_pts(n, [(0, 0), (0.06, 0), (0.15, 1.0), (0.7, 0.85), (0.95, 0.15), (1.1, 0)])
    flow = flow * np.clip(1 + 0.35 * snoise(n, 14, 1110), 0.2, 2)
    lam = 650 * flow
    idx = poisson(lam, 1103)
    amps = np.minimum(r.pareto(3.0, len(idx)) + 0.1, 3.0).astype(np.float32)
    k1 = dsp.highpass(burst(0.0005, 1104, 2.0), 2500, 2)
    k2 = modal_ir([(3300, 900, 1.0), (5200, 1200, 0.6)], 0.004, 1105)
    gr = pulse_train(n, idx, amps, k1 + 0.5 * fit(k2, len(k1)))
    # the growing pile: grains landing on grains, lower and softer
    idx2 = poisson(lam * 0.5, 1106)
    pile = pulse_train(n, idx2, r.uniform(0.1, 0.6, len(idx2)).astype(np.float32), bp(burst(0.0015, 1107, 1.5), 900, 3500))
    hiss = bp(white(n, 1108), 2500, 7000) * flow
    yy = norm(gr) + 0.5 * norm(pile) + 0.12 * norm(hiss)
    add(y, dsp.lowpass(yy, 9500, 2), 0.0, 1.0)
    return space(y, 0.4, 0.06, 6000, 0.003, SMALL_ER, 0.2, 200, 1109)


# ====================================================================== electronic tools
def emf_beep():
    """Piezo beep: mostly the fundamental with a little 3rd harmonic, the buzzer's own resonance, 80 ms."""
    dur = 0.085
    n = N(dur)
    t = taxis(n)
    f = 2730.0
    ph = TWO_PI * f * t
    sq = np.sin(ph) + 0.22 * np.sin(3 * ph + 0.4) + 0.08 * np.sin(2 * ph)
    sq = dsp.peak(sq.astype(np.float32), f, 4, 4)
    sq = dsp.lowpass(sq, 6000, 2)
    e = env_pts(n, [(0, 0), (0.0025, 1), (0.06, 0.92), (0.072, 0.3), (dur, 0)])
    y = norm(sq * e)
    cl = dsp.highpass(burst(0.0012, 1201, 2), 1500, 2)     # the transistor/relay tick
    y[:len(cl)] += 0.12 * norm(cl)
    return y


def flashlight_click():
    n = N(0.16)
    y = np.zeros(n, np.float32)

    def click(seed, amp, f_shift=1.0):
        r = dsp.rng(seed)
        c = dsp.highpass(burst(0.0012, seed, 2.0), 2000, 2)
        body = modal_ir([(2150 * f_shift * r.uniform(0.97, 1.03), 320, 1.0), (3620 * f_shift, 420, 0.7), (5100 * f_shift, 600, 0.45),
                         (7900 * f_shift, 900, 0.2)], 0.03, seed)
        tube = modal_ir([(180, 90, 1.0), (430, 140, 0.5), (1250, 260, 0.35)], 0.06, seed + 1)
        spring = modal_ir([(6600 * r.uniform(0.98, 1.02), 70, 1.0)], 0.06, seed + 2)
        x = np.zeros(N(0.07), np.float32)
        add(x, norm(c), 0, 1.0)
        add(x, norm(body), 0, 0.7)
        add(x, norm(tube), 0, 0.35)
        add(x, norm(spring), 0.001, 0.07)
        return norm(x, amp)

    add(y, click(1300, 1.0), 0.002)
    add(y, click(1310, 0.55, 1.12), 0.028)       # the slider snaps into its detent
    return space(y, 0.2, 0.04, 6000, 0.001, EAR_ER, 0.15, 200, 1320)


def flashlight_flicker():
    dur = 1.0
    n = N(dur)
    r = dsp.rng(1400)
    # bad battery contact: on/off stutter (seconds); it limps on and finally dies
    pattern = [(0.0, 0.11, 1.0), (0.11, 0.16, 0), (0.16, 0.2, 0.8), (0.2, 0.31, 0), (0.31, 0.5, 1.0), (0.5, 0.53, 0),
               (0.53, 0.58, 0.9), (0.58, 0.7, 0), (0.7, 0.75, 0.7), (0.75, 0.79, 0), (0.79, 0.81, 0.6), (0.81, 0.9, 0),
               (0.9, 0.925, 0.35), (0.925, 1.0, 0)]
    gate = np.zeros(n, np.float32)
    for a, b, s_ in pattern:
        gate[N(a):N(b)] = s_ * r.uniform(0.8, 1.0)
    gate = uniform_filter1d(gate, N(0.002))
    # buzz: the contact chattering at ~118 Hz -> a rough electrical 'zzzt'
    f = 118 * (1 + 0.04 * snoise(n, 6, 1401))
    bz = additive_saw(f, n, 5000, 0.9, 1402)
    bz = bz * (0.55 + 0.45 * grain(n, 300, 1403, 2.0))
    bz = bp(bz, 110, 5000)
    bz = dsp.peak(bz, 1500, 5, 1.5)
    bz = dsp.peak(bz, 240, 4, 1.5)
    y = norm(bz * gate)
    # arcing crackle at every transition and sputtering inside the 'on' bursts
    lam = 400 * np.abs(np.gradient(uniform_filter1d(gate, N(0.008)))) * SR / 50 + 60 * gate
    idx = poisson(lam, 1404)
    cr = pulse_train(n, idx, r.uniform(0.2, 1.0, len(idx)).astype(np.float32), bp(burst(0.0015, 1405, 2), 1200, 6500))
    y = y + 0.4 * norm(cr)
    # filament ticks (the hot glass pinging) on some switch-ons
    for k, (a, b, s_) in enumerate(pattern):
        if s_ and r.random() < 0.6:
            add(y, glass_ping(1410 + k, r.uniform(4200, 6200), 90, 1.0, 0.3), a, 0.1)
    # torch body (aluminium tube) resonance
    y = y + 0.35 * dsp.peak(dsp.lowpass(y, 2500, 2), 900, 6, 3)
    y = dsp.lowpass(y, 7000, 2)
    return fit(y, n) * env_pts(n, [(0, 1), (0.97, 1), (1.0, 0)])


_RADIO_SRC = None


def radio_source():
    """Snippets of 'real' broadcasts for the sweep: an announcer, an ad, a tango-ish music stab."""
    global _RADIO_SRC
    if _RADIO_SRC is None:
        a = say('Y ahora, el pronóstico para Córdoba y alrededores: cielo nublado, frío.', 'em_alex', 1.1)
        b = say('¡Llame ya! Ofertas en electrodomésticos, todo el mes de junio.', 'ef_dora', 1.15)
        c = say('Gol, gol, gol de Talleres, señores.', 'em_santa', 1.2)
        n = N(1.5)
        t = taxis(n)
        mus = np.zeros(n, np.float32)
        for j, fr in enumerate([196.0, 246.94, 293.66, 392.0, 329.63]):
            mus += additive_saw(fr * (1 + 0.003 * np.sin(TWO_PI * 5 * t)), n, 5000, 1.2, 1500 + j) * (0.6 + 0.4 * (j % 2))
        mus = mus * (0.6 + 0.4 * np.abs(np.sin(TWO_PI * 2.2 * t)))
        _RADIO_SRC = [a, b, c, norm(mus)]
    return _RADIO_SRC


def radio_band(x, seed=0):
    """Tiny speaker of the spirit box: 300-4000 Hz, cone grit, a little crushed."""
    y = bp(x, 280, 4200, 2)
    y = dsp.peak(y, 1250, 4, 1.4)
    y = dsp.drive(y * 1.6, 1.8)
    y = dsp.bitcrush(y, 11, 2)
    return dsp.lowpass(y, 4800, 4)


def sweep_static(dur, seed, voices=0.35, seg=(0.06, 0.11)):
    """Spirit-box FM sweep: per-channel segments of static / carrier whistles / chopped broadcasts, with clicks.
    Returns (signal, list of segment boundary times)."""
    r = dsp.rng(seed)
    n = N(dur)
    y = np.zeros(n, np.float32)
    src = radio_source()
    bounds = []
    t = 0.0
    k = 0
    while t < dur:
        d = r.uniform(*seg)
        m = N(d)
        kind = r.choice(['static', 'whistle', 'voice', 'static', 'hollow'], p=[0.32, 0.18, voices, 0.0, 0.5 - voices])
        if kind == 'static':
            s = white(m, seed + k) * r.uniform(0.6, 1.0)
            s = s * (0.7 + 0.3 * grain(m, 2500, seed + 100 + k, 1.5))
        elif kind == 'whistle':
            f0 = r.uniform(500, 3000)
            f1 = f0 * r.uniform(0.7, 1.4)
            s = 0.55 * dsp.osc(dsp.glide(f0, f1, d), d)[:m] + 0.5 * white(m, seed + k)
        elif kind == 'voice':
            x = src[int(r.integers(0, len(src)))]
            a = int(r.integers(0, max(1, len(x) - m)))
            s = fit(x[a:a + m], m)
            if r.random() < 0.35:
                s = s[::-1].copy()
            s = norm(s) * r.uniform(0.6, 1.0) + 0.35 * white(m, seed + k)
        else:   # 'hollow': nearly dead air between stations, low hiss with carrier hum
            s = 0.3 * dsp.lowpass(white(m, seed + k), 2500, 2) + 0.15 * dsp.osc(r.uniform(150, 400), d)[:m]
        # every channel has its own level; between channels the tuner mutes for a few ms
        gap = r.uniform(0.003, 0.012) if r.random() < 0.7 else 0.0
        s = fit(s, m) * env_pts(m, [(0, 0), (gap, 0), (gap + 0.002, 1), (d - 0.003, 1), (d, 0)]) * r.uniform(0.35, 1.0)
        add(y, s, t)
        # channel-step click of the tuner
        cl = dsp.highpass(burst(0.0012, seed + 500 + k, 2), 800, 2)
        add(y, norm(cl), t, 0.35)
        bounds.append(t)
        t += d
        k += 1
    y = y * (0.85 + 0.15 * snoise(n, 3, seed + 7))
    return radio_band(y, seed), bounds


def spirit_box_static():
    y, _ = sweep_static(1.5, 1600)
    n = len(y)
    return y * env_pts(n, [(0, 0), (0.01, 1), (1.42, 1), (1.5, 0)])


SPIRIT_LINES = [
    # (text or None for synthesized shush, seed, Kokoro speed)
    # QA: speed 0.9, not 0.8. Kokoro slurs single words when slowed (whisper-base ASR on the CLEAN TTS: "Frio" at 0.8 ->
    # "Ferreo", at 0.9 -> "frio"; "Mira" at 0.8 -> "Miren la", at 0.9 -> "Mira"). The ghostliness comes from the processing.
    ('Clara, Clara.', 1701, 0.9),   # QA: one take (two separate 'Clara.' takes were heard as 'Claro! Claro!')
    ('Ocho.', 1702, 0.9),
    (None, 1703, 0.9),
    ('Mirá.', 1704, 0.9),
    ('Vacío.', 1705, 0.9),
    ('Te veo.', 1706, 0.9),
    ('Ayuda.', 1707, 0.9),
    ('Frío.', 1708, 0.9),
]


# QA: Kokoro starts "Te veo." with a 40 ms /s/-like hiss before the /t/ closure; ASR heard "Este veo" even on the
# clean TTS. Cutting it gives "Te veo" on the clean TTS (and "De veo" after the ghost room, a soft t).
LEAD_CUT = {'Te veo.': 0.045}
PAUSE = {'Clara, Clara.': 0.15}     # seconds of silence added at the comma (ASR best at 0.15)


def ghost_voice(text, seed, speed=0.9):
    """The voice from the other side: breathy (whisper layer), a faint octave below, a slow wobble, a distant room.
    QA: room and layers kept light (they smeared the single words); the voice must be understood in one hearing."""
    v = say(text, 'ef_dora', speed)
    if text in LEAD_CUT:
        v = v[N(LEAD_CUT[text]):].copy()
        v[:N(0.004)] *= np.linspace(0, 1, N(0.004))
    if text in PAUSE:
        # widen the comma pause ("Clara... Clara..."): split at the quietest point of the middle third
        e = rms_env(v, 0.015)
        a0, b0 = len(v) // 3, 2 * len(v) // 3
        cut = a0 + int(np.argmin(e[a0:b0]))
        v = np.concatenate([v[:cut], np.zeros(N(PAUSE[text]), np.float32), v[cut:]])
    w = to_whisper(v, seed)
    lo = dsp.pitch_shift(v, -12)
    y = norm(v) + 0.2 * norm(w) + 0.08 * norm(fit(lo, len(v)))
    y = wobble(y, 0.9, 1.0, seed, 0.8)
    y = space(y, 1.0, 0.1, 3500, 0.025, CHAPEL_ER, 0.1, 150, seed)
    return norm(dsp.trim(y, -50, 0.2))


def voice_band(x):
    """The spirit box speaker for the ANSWER: wider than the sweep's radio band so f / s / ch survive ("Frio", "Vacio",
    "Shhh"), a presence lift for the consonants, the same cone grit."""
    y = bp(x, 190, 6200, 2)
    y = dsp.peak(y, 1250, 3, 1.4)
    y = dsp.peak(y, 3000, 3, 1.2)
    y = dsp.drive(y * 1.4, 1.5)
    y = dsp.bitcrush(y, 12, 2)
    return dsp.lowpass(y, 6800, 4)


def spirit_box_voice(i):
    text, seed, speed = SPIRIT_LINES[i]
    r = dsp.rng(seed)
    if text is None:
        v = shush(1.0, seed, 1.05, 1.0)
        v = space(wobble(v, 0.8, 1.0, seed), 1.2, 0.15, 3500, 0.03, CHAPEL_ER, 0.12, 150, seed)
    elif i == 0:
        # "Clara... Clara..." : the second call drifts further away (darker, quieter) as the phrase goes on
        v = ghost_voice(text, seed, speed)
        k = len(v)
        v = tv_filter(v, 'lp', env_pts(k, [(0, 7000), (0.45 * k / SR, 7000), (k / SR, 2600)]), 48)
        v = v * env_pts(k, [(0, 1.0), (0.45 * k / SR, 1.0), (k / SR, 0.6)])
    else:
        v = ghost_voice(text, seed, speed)
    v = dsp.trim(v, -50, 0.12)
    pre, post = r.uniform(0.32, 0.45), 0.3
    total = pre + len(v) / SR + post
    st, bounds = sweep_static(total, seed + 50, 0.3)
    n = len(st)
    # the voice "locks" the tuner: the sweep drops away ~24 dB under the words. QA: the sweep around the answer is
    # also lower (0.32, was 0.55) so the voice sits ~6 dB above it instead of level with it.
    vm = np.zeros(n, np.float32)
    vm[max(0, N(pre) - N(0.03)):N(pre) + len(v) - N(0.1)] = 1.0
    duck = 1 - 0.94 * uniform_filter1d(vm, N(0.05))
    vo = np.zeros(n, np.float32)
    add(vo, voice_band(v), pre)
    # the sweep keeps chopping: shallow dropouts on the voice at channel steps (words stay whole)
    chop = np.ones(n, np.float32)
    for b in bounds:
        if r.random() < 0.3:
            a0 = N(b)
            chop[a0:a0 + N(0.01)] = r.uniform(0.6, 0.8)
    chop = uniform_filter1d(chop, N(0.002))
    y = norm(st) * duck * 0.32 + norm(vo) * chop
    return y * env_pts(n, [(0, 0), (0.01, 1), (total - 0.05, 1), (total, 0)])


def camera_flash():
    dur = 1.45
    n = N(dur)
    r = dsp.rng(1800)
    y = np.zeros(n, np.float32)
    # 1) shutter button + mechanism (two clicks)
    for k, (tt, amp, fs) in enumerate([(0.0, 1.0, 1.0), (0.03, 0.6, 1.3)]):
        c = dsp.highpass(burst(0.0015, 1801 + k, 2), 1800, 2)
        b = modal_ir([(1650 * fs, 300, 1), (2900 * fs, 420, 0.6), (4700 * fs, 650, 0.35), (520, 160, 0.4)], 0.04, 1803 + k)
        add(y, norm(fit(c, len(b)) + 0.6 * norm(b)), tt, 1.0 * amp)
    # 2) capacitor charging whine (fast, then the pop)
    t_pop = 0.46
    m = N(t_pop - 0.04)
    tt = taxis(m)
    f = 6600 - (6600 - 1400) * np.exp(-tt / 0.17)
    wh = np.sin(TWO_PI * np.cumsum(f) / SR) + 0.25 * np.sin(2 * TWO_PI * np.cumsum(f) / SR)
    wh = wh * (1 + 0.15 * np.sin(TWO_PI * 120 * tt))
    wh = wh * env_pts(m, [(0, 0), (0.02, 0.6), (m / SR, 1.0)])
    add(y, norm(wh), 0.04, 0.14)
    # 3) xenon POP: crack + low thup + a burst of sizzle
    pc = dsp.highpass(burst(0.0025, 1810, 1.5), 900, 2)
    m = N(0.08)
    tt = taxis(m)
    thup = np.sin(TWO_PI * np.cumsum(140 * np.exp(-tt * 18) + 60) / SR) * np.exp(-tt * 40)
    sz = dsp.highpass(white(N(0.04), 1811), 3000, 2) * np.linspace(1, 0, N(0.04)) ** 2
    pop = np.zeros(N(0.1), np.float32)
    add(pop, norm(pc), 0, 1.0)
    add(pop, norm(thup), 0, 0.7)
    add(pop, norm(sz), 0.002, 0.35)
    add(y, norm(pop), t_pop, 1.0)
    # 4) recharge whine after the flash, quieter, rising again
    m = N(0.85)
    tt = taxis(m)
    f = 6200 - (6200 - 1000) * np.exp(-tt / 0.3)
    wh2 = np.sin(TWO_PI * np.cumsum(f) / SR) * env_pts(m, [(0, 0), (0.05, 0.7), (0.6, 1.0), (0.85, 0)])
    add(y, norm(wh2), t_pop + 0.12, 0.06)
    return space(y, 0.5, 0.08, 6000, 0.004, SMALL_ER, 0.25, 150, 1812)


# ====================================================================== ritual
def cross_synth(mod, car, nper=1024, smooth_bins=11):
    """Impose mod's spectral envelope on car (channel-vocoder / cross-synthesis); voiced frames only."""
    n = min(len(mod), len(car))
    kw = dict(fs=SR, nperseg=nper, noverlap=nper * 3 // 4)
    f, _, M = signal.stft(mod[:n], **kw)
    _, _, C = signal.stft(car[:n], **kw)
    lm = uniform_filter1d(np.log(np.abs(M) + 1e-6), smooth_bins, axis=0)
    lc = uniform_filter1d(np.log(np.abs(C) + 1e-6), smooth_bins, axis=0)
    Y = C * np.exp(lm - lc)
    # voicing: low-band share of energy per frame
    lo = np.sum(np.abs(M[f < 1200]) ** 2, axis=0)
    tot = np.sum(np.abs(M) ** 2, axis=0) + 1e-12
    v = np.clip((lo / tot - 0.35) / 0.4, 0, 1)
    Y = Y * v[None, :]
    _, y = signal.istft(Y, **kw)
    return fit(y, n)


def ritual_chant():
    text = 'Exorcizamus te, omnis immundus spiritus.'
    a = say(text, 'em_santa', 0.85)
    b = say(text, 'em_alex', 0.85)
    n = max(len(a), len(b)) + N(0.05)
    a, b = fit(a, n), fit(b, n)
    t = taxis(n)
    # organum: reciting tone A2, a fifth above (E3), the octave below (A1)
    layers = []
    for j, (f, g) in enumerate([(110.0, 1.0), (164.81, 0.55), (55.0, 0.4)]):
        car = np.zeros(n, np.float32)
        for k, dt in enumerate([-0.003, 0.0, 0.0035]):       # a few priests per part
            fr = f * (1 + dt) * (1 + 0.004 * np.sin(TWO_PI * (4.8 + 0.4 * k) * t + k))
            car += additive_saw(fr, n, 6000, 1.0, 1900 + 10 * j + k)
        layers.append(g * norm(cross_synth(a, car)))
    chant = sum(layers)
    chant = dsp.lowpass(chant, 5000, 2)
    # the choir holds the reciting tone under the words (humming 'o' on A2 + E3), swelling in and out
    e = env_pts(n, [(0, 0), (0.25, 0.8), (n / SR * 0.6, 1.0), (n / SR, 0.5)])
    hold = choir([110.0, 164.81], n / SR, 1920, 'o', e, vib=0.004, fmax=4000)
    # the spoken words stay on top (intelligible), the second priest a hair behind
    dry = norm(a) + 0.45 * norm(fit(np.concatenate([np.zeros(N(0.022), np.float32), b]), n))
    y = norm(dry) + 0.8 * norm(chant) + 0.18 * fit(hold, n)
    y = shelf_lo(y, 180, 2.0)
    return chapel(y, 0.18, 2.6, 1910)        # more would smear the Latin (simplified STOI ~0.8 at this setting)


def ritual_complete():
    dur = 6.0
    n = N(dur)
    t0 = 0.75
    r = dsp.rng(2000)
    y = np.zeros(n, np.float32)
    # swell: rising noise + reversed choir + rising tone
    m = N(t0)
    sw = tv_filter(white(m, 2001), 'bp', env_pts(m, [(0, 400), (t0, 6000)]), 48, 1.5)
    add(y, norm(sw) * np.linspace(0, 1, m) ** 2.5, 0.0, 0.45)
    rc = choir([220.0, 329.63, 440.0, 554.37], 1.0, 2002, 'a')[::-1][:m] * np.linspace(0, 1, m) ** 2
    add(y, norm(rc), 0.0, 0.4)
    # HIT: sub boom + bells + choir chord + air blast
    m = N(2.5)
    tt = taxis(m)
    fb = 30 + 50 * np.exp(-tt * 7)
    boom = np.sin(TWO_PI * np.cumsum(fb) / SR) * np.exp(-tt * 2.2) * np.minimum(1, tt / 0.004)
    add(y, dsp.drive(norm(boom), 1.8), t0, 0.9)
    for j, f0 in enumerate([220.0, 329.63, 440.0, 659.25]):
        bell = modal_ir([(f0, 1.2, 1.0), (f0 * 2.0, 1.8, 0.7), (f0 * 2.4, 2.4, 0.45), (f0 * 3.0, 2.8, 0.4), (f0 * 4.2, 4, 0.25),
                         (f0 * 5.4, 5.5, 0.15), (f0 * 0.5, 0.8, 0.35)], 4.0, 2010 + j)
        add(y, norm(bell), t0 + 0.01 * j, 0.32)
    e = env_pts(N(4.5), [(0, 0), (0.05, 1.0), (1.0, 0.8), (2.5, 0.45), (4.5, 0)])
    add(y, choir([110.0, 220.0, 277.18, 329.63, 440.0, 554.37, 659.25], 4.5, 2003, 'a', e, vib=0.007), t0, 0.45)
    blast = bp(white(N(1.2), 2004), 300, 9000) * env_pts(N(1.2), [(0, 0), (0.01, 1), (0.25, 0.35), (1.2, 0)]) ** 1.5
    add(y, norm(blast), t0, 0.25)
    add(y, sparkles(3.0, 2005, [(0, 18), (1.0, 8), (3.0, 0)], 3000, 7500), t0, 0.1)
    # the demon's scream, dragged down and away into the floor
    sd = 3.4
    sc = scream(sd, [(0, 520), (0.3, 610), (1.2, 430), (2.4, 250), (sd, 140)], 2006, 'scream_f', 0.9, 0.04, 3.0)
    sc2 = scream(sd, [(0, 260), (0.3, 300), (1.2, 210), (2.4, 120), (sd, 70)], 2007, 'scream_m', 0.75, 0.06, 3.5)
    gr = growl(sd, [(0, 95), (1.5, 75), (sd, 45)], 2008, ('a', 'o'), 0.75, 0.08, 0.7, 3.5)
    dm = norm(sc) + 0.7 * norm(sc2) + 0.6 * norm(gr)
    k = len(dm)
    dm = tv_filter(dm, 'lp', env_pts(k, [(0, 9000), (1.0, 5000), (2.5, 1200), (sd, 400)]), 64)
    dm = dm * env_pts(k, [(0, 0), (0.04, 1.0), (0.8, 0.85), (2.0, 0.4), (sd, 0)])
    dm = space(dm, 2.5, 0.25, 3000, 0.02, CHAPEL_ER, 0.2, 100, 2009, 1.0)
    add(y, norm(dm), t0 + 0.05, 1.4)
    return chapel(y, 0.3, 3.4, 2011)


def jar_capture():
    dur = 2.6
    n = N(dur)
    r = dsp.rng(2100)
    y = np.zeros(n, np.float32)
    t_in = 1.05
    # vortex: rising, accelerating swirl of air (flanged noise)
    m = N(t_in)
    tt = taxis(m)
    v = tv_filter(white(m, 2101), 'bp', env_pts(m, [(0, 300), (t_in, 3800)]), 64, 1.0)
    rate = 3 + 16 * (tt / t_in) ** 2
    v = v * (0.55 + 0.45 * np.sin(TWO_PI * np.cumsum(rate) / SR))
    d = (0.002 + 0.0015 * np.sin(TWO_PI * np.cumsum(rate * 0.5) / SR)) * SR
    idx = np.arange(m)
    v = v + 0.8 * np.interp(idx - d, idx, v)                 # flanger
    add(y, norm(v) * env_pts(m, [(0, 0), (0.6, 0.6), (t_in - 0.03, 1.0), (t_in, 0.2)]), 0.0, 0.6)
    # the soul's wail: rising and shrinking as it is pulled in
    m = N(t_in)
    f0 = env_pts(m, [(0, 330), (0.5, 420), (t_in, 980)])
    wl = glottal(f0 * (1 + 0.02 * np.sin(TWO_PI * 5.5 * tt)), m, 2102, 0.01, 0.1, 0.0, 0.3, 8000)
    wl = vowel_morph(wl, 'o', 'u', np.linspace(0, 1, m), 1.25)
    wl = wobble(wl, 1.3, 1.5, 2102)
    add(y, norm(wl) * env_pts(m, [(0, 0), (0.25, 0.7), (0.8, 1.0), (t_in, 0.0)]), 0.0, 0.45)
    # into the jar: hollow whomp + glass ring
    m = N(0.25)
    tt = taxis(m)
    wh = np.sin(TWO_PI * np.cumsum(170 * np.exp(-tt * 9) + 80) / SR) * np.exp(-tt * 18)
    add(y, norm(wh), t_in, 0.7)
    jar = modal_ir([(905, 3.2, 1.0), (905 * 2.32, 5, 0.6), (905 * 3.9, 8, 0.35), (905 * 5.6, 11, 0.2), (430, 6, 0.3)], 1.4, 2103)
    add(y, norm(jar), t_in, 0.4)
    # cork twisted in (squeak) and pressed home (pop)
    t_c = 1.32
    m = N(0.16)
    idx2, a2 = stick_slip(m, env_pts(m, [(0, 280), (0.16, 650)]), 2104, 0.3, env_pts(m, [(0, 0), (0.03, 1), (0.16, 0.6)]))
    sq = pulse_train(m + N(0.03), idx2, a2, modal_ir([(1450, 180, 1), (2900, 300, 0.5), (4100, 420, 0.2)], 0.03, 2105))
    add(y, norm(sq), t_c, 0.35)
    m = N(0.12)
    tt = taxis(m)
    pop = np.sin(TWO_PI * np.cumsum(620 * np.exp(-tt * 30) + 330) / SR) * np.exp(-tt * 45) * np.minimum(1, tt / 0.0005)
    pk = dsp.highpass(burst(0.002, 2106, 2), 1200, 2)
    add(y, norm(pop) + 0.5 * norm(fit(pk, m)), t_c + 0.17, 0.75)
    add(y, norm(jar) * 0.5, t_c + 0.17, 0.25)
    # a last muffled knock from inside the jar
    kn = dsp.lowpass(knock_hit(2107, 'knuckle', 1.0), 1400, 2)
    add(y, norm(kn), 2.05, 0.14)
    return space(y, 0.9, 0.1, 4500, 0.008, SMALL_ER, 0.25, 120, 2108)


# ====================================================================== consumables / flare
def pill_click(seed, amp=1.0, plastic=True):
    r = dsp.rng(seed)
    c = dsp.highpass(burst(0.0006, seed, 2), 2500, 2)
    modes = [(r.uniform(1700, 2000), 500, 1.0), (r.uniform(2800, 3100), 700, 0.7), (r.uniform(4100, 4500), 900, 0.4)] if plastic \
        else [(r.uniform(5200, 7000), 1400, 1.0)]
    b = modal_ir(modes, 0.012, seed)
    x = fit(c, len(b)) + 0.5 * norm(b)
    return norm(x, amp)


def pills_swallow():
    dur = 2.3
    n = N(dur)
    r = dsp.rng(2200)
    y = np.zeros(n, np.float32)
    # two shakes of the bottle: pills hitting the walls and each other, bottle body thump
    for s, t0 in enumerate([0.0, 0.19, 0.38]):
        add(y, dsp.lowpass(modal_ir([(420, 60, 1.0), (980, 90, 0.4)], 0.08, 2210 + s), 2000, 2), t0 + 0.035, 0.3)
        for k in range(int(r.integers(24, 34))):
            # the pills fly as one clump: most land within 40 ms of the reversal, a few stragglers
            dt = r.gamma(2.0, 0.012)
            add(y, pill_click(2220 + 60 * s + k, r.uniform(0.15, 1.0), r.random() < 0.6), t0 + 0.03 + dt, 0.35)
    # child-proof cap pressed and popped off
    add(y, pill_click(2300, 0.6), 0.62, 0.6)
    m = N(0.06)
    tt = taxis(m)
    cap = np.sin(TWO_PI * np.cumsum(900 * np.exp(-tt * 40) + 500) / SR) * np.exp(-tt * 70)
    add(y, norm(cap) + 0.4 * norm(fit(dsp.highpass(burst(0.002, 2301, 2), 2000, 2), m)), 0.68, 0.7)
    # pills poured into the palm (muffled)
    for k in range(4):
        add(y, dsp.lowpass(pill_click(2310 + k, r.uniform(0.4, 1.0), False), 3000, 2), 0.9 + 0.035 * k + r.uniform(0, 0.02), 0.3)
    # swallow: lips, tongue click, gulp (two throat blips), relieved exhale through the nose
    add(y, lip_click(2320, 0.4), 1.25)
    for k, (tg, f0, a) in enumerate([(1.38, 260, 1.0), (1.5, 190, 0.6)]):
        m = N(0.09)
        tt = taxis(m)
        g = np.sin(TWO_PI * np.cumsum(f0 * (1 - 0.45 * tt / 0.09)) / SR) * np.exp(-tt * 45) * np.minimum(1, tt / 0.004)
        wet = bp(burst(0.012, 2330 + k, 1.5), 700, 2600)
        gl = norm(g) + 0.5 * norm(fit(wet, m))
        add(y, dsp.lowpass(gl, 2500, 2), tg, a * 1.1)
    add(y, breath_out(0.5, 2340, 1.1), 1.72, 0.22)
    return space(y, 0.3, 0.05, 6000, 0.002, EAR_ER, 0.2, 150, 2350)


def flare_texture(n, seed, env, crackle=1.0):
    """Burning strontium-nitrate flare: roaring hiss, low rumble, crackle and spits, irregular sputter."""
    r = dsp.rng(seed)
    hiss = bp(white(n, seed), 650, 7000)
    hiss = dsp.peak(hiss, 2600, 5, 1.0)
    hiss = dsp.lowpass(hiss, 8000, 4)
    roar = bp(colored(n, 'pink', seed + 1), 120, 560)
    sput = 0.5 + 0.5 * np.abs(snoise(n, 11, seed + 2)) + 0.1 * snoise(n, 60, seed + 3)
    y = (norm(hiss) * 0.55 + norm(roar) * 0.35) * sput * env
    lam = 110 * env * crackle
    idx = poisson(lam, seed + 4)
    amps = np.minimum(r.pareto(2.2, len(idx)) + 0.3, 5.0).astype(np.float32)
    pops = pulse_train(n, idx, amps, bp(burst(0.003, seed + 5, 1.5), 400, 4500))
    sidx = poisson(5 * env * crackle, seed + 6)
    spits = pulse_train(n, sidx, r.uniform(0.5, 1.0, len(sidx)).astype(np.float32), bp(burst(0.02, seed + 7, 2.0), 500, 3000))
    return y + (0.45 * norm(pops) + 0.3 * norm(spits)) * np.max(np.abs(y))


def flare_ignite():
    dur = 1.8
    n = N(dur)
    r = dsp.rng(2400)
    y = np.zeros(n, np.float32)
    # strike: the cap's scratch surface dragged across the igniter button (gritty friction)
    m = N(0.2)
    sc = bp(white(m, 2401), 1200, 8000) * grain(m, 1800, 2402, 2.5) * env_pts(m, [(0, 0), (0.02, 0.6), (0.15, 1.0), (0.2, 0)])
    idx, a = stick_slip(m, 160, 2403, 0.4, env_pts(m, [(0, 0.3), (0.2, 1)]))
    ss = pulse_train(m, idx, a, dsp.highpass(burst(0.001, 2404, 2), 1500, 2))
    add(y, norm(sc) + 0.4 * norm(ss), 0.0, 0.7)
    # catch: a few chemical pops, then the whoosh
    for k in range(4):
        add(y, norm(bp(burst(0.004, 2410 + k, 1.2), 600, 6000)), 0.16 + 0.03 * k + r.uniform(0, 0.02), 0.5)
    m = N(0.6)
    wh = tv_filter(white(m, 2420), 'bp', env_pts(m, [(0, 600), (0.12, 2600), (0.6, 1800)]), 48, 2.0)
    thump = dsp.lowpass(white(m, 2421), 260, 2) * env_pts(m, [(0, 0), (0.02, 1), (0.25, 0)])
    add(y, (norm(wh) + 0.7 * norm(thump)) * env_pts(m, [(0, 0), (0.03, 1), (0.3, 0.45), (0.6, 0.1)]), 0.24, 0.9)
    # settling into the burn
    m = N(dur - 0.26)
    env = env_pts(m, [(0, 0), (0.06, 1.0), (0.4, 0.7), (1.0, 0.55), (m / SR, 0.0)])
    add(y, flare_texture(m, 2430, env, 1.5), 0.26, 0.55)
    return y


def flare_burn():
    """2.0 s seamless loop (FlareEntity retriggers it every 40 ticks). Everything lives on a periodic timeline: FFT noise
    beds, periodic control curves and events wrap-added across the seam, so there is no seam to hide.
    QA rewrite: the first version was a near-stationary hiss (crackle 20 dB under the bed, sputter +-2 dB) and its seam
    sat inside a dip that master()'s fades turned into a 23 ms hole every 2 s. Now: a roaring hiss that really
    sputters (fast irregular AM plus two 'motorboat' flutter episodes), sharp crackle and burning-slag snaps on top,
    molten spits, low combustion roar."""
    L = N(2.0)
    r = dsp.rng(2500)
    f = np.fft.rfftfreq(L, 1 / SR)
    t = taxis(L)

    def pbed(seed, g):
        rr = dsp.rng(seed)
        spec = (rr.standard_normal(len(f)) + 1j * rr.standard_normal(len(f))) * g
        spec[0] = 0
        x = np.fft.irfft(spec, L)
        return (x / (np.std(x) + 1e-12)).astype(np.float32)

    def pnoise(seed, cutoff):
        x = pbed(seed, 1 / np.sqrt(1 + (f / cutoff) ** 4))
        return x / (np.max(np.abs(x)) + 1e-9)

    def wrap(kernel, idx, amps):
        out = np.zeros(L + len(kernel), np.float32)
        for i, a_ in zip(idx, amps):
            out[i:i + len(kernel)] += a_ * kernel
        y_ = out[:L].copy()
        y_[:len(kernel)] += out[L:L + len(kernel)]
        return y_

    def ploop(cycles, phase=0.0):
        return np.sin(TWO_PI * cycles * t / 2.0 + phase)     # whole number of cycles per loop -> periodic

    fs = np.maximum(f, 1)
    hp = lambda fc, o=2: 1 / np.sqrt(1 + (fc / fs) ** (2 * o))      # noqa: E731
    lp = lambda fc, o=2: 1 / np.sqrt(1 + (fs / fc) ** (2 * o))      # noqa: E731
    hiss = pbed(2501, hp(700) * lp(8500, 4) * (1 + 0.9 / (1 + ((f - 2600) / 1200) ** 2)))
    fizz = pbed(2502, hp(4200, 3) * lp(9500, 3))
    roar = pbed(2503, hp(70) * lp(480) / np.sqrt(fs / 70))
    # sputter: fast irregular amplitude flicker of the flame + two 'motorboat' episodes (~34 Hz flutter)
    sput = 0.3 + 0.7 * np.abs(pnoise(2505, 26)) ** 0.8 + 0.15 * pnoise(2506, 90)
    epis = np.clip(0.5 + 0.5 * ploop(2, 0.7), 0, 1) ** 5                    # two bursts per loop
    flutter = 1 - 0.75 * epis * (0.5 + 0.5 * np.sin(TWO_PI * 17 * t * 2))    # 34 Hz, 68 cycles per loop
    # slow flare-ups: the flame breathes brighter and louder (1 and 3 cycles per loop)
    swell = 1 + 0.22 * ploop(1, 1.3) + 0.12 * ploop(3, 0.2)
    bright = np.clip(0.5 + 0.5 * ploop(3, 2.1), 0, 1) ** 2
    bed = (0.62 * hiss * (0.8 + 0.4 * bright) + 0.3 * fizz * np.abs(pnoise(2507, 40)) * (0.5 + bright)
           + 0.38 * roar * (0.7 + 0.3 * np.abs(pnoise(2508, 9))))
    bed = bed * sput * flutter * swell
    sb = float(np.std(bed))
    # crackle: sharp clicks with Pareto amplitudes, denser when the flame flares
    k_click = norm(dsp.highpass(burst(0.0007, 2510, 2.0), 1500, 2))
    lam = 170 * (0.5 + 0.5 * sput)
    ci = np.nonzero(r.random(L) < lam / SR)[0]
    ca = np.minimum(r.pareto(1.8, len(ci)) + 0.3, 4.0)
    crackle = wrap(k_click, ci, ca)
    # burning slag snaps: a click plus a short metallic/ceramic ring
    snaps = np.zeros(L, np.float32)
    for j, tt in enumerate(np.sort(r.uniform(0, 2.0, 7))):
        k = modal_ir([(r.uniform(2400, 4200), 300, 1.0), (r.uniform(5000, 7000), 450, 0.5)], 0.03, 2520 + j)
        k[:N(0.0008)] += dsp.highpass(burst(0.0008, 2530 + j, 2), 1500, 2)
        snaps += wrap(norm(k), [N(tt) % L], [r.uniform(0.5, 1.0)])
    # molten spits: short low-mid bursts (material blown out of the flame)
    spits = np.zeros(L, np.float32)
    for j, tt in enumerate(np.sort(r.uniform(0, 2.0, 6))):
        d = r.uniform(0.018, 0.045)
        k = bp(white(N(d), 2540 + j), 450, 3200) * np.exp(-taxis(N(d)) * r.uniform(50, 100))
        spits += wrap(norm(k), [N(tt) % L], [r.uniform(0.6, 1.0)])
    y = bed + sb * (3.0 * crackle + 5.0 * snaps + 4.0 * spits)
    lim = 5.5 * sb                                   # soft ceiling: the loudest pops can't swallow the master gain
    return (lim * np.tanh(y / lim)).astype(np.float32)


def master_loop(x, peak_db):
    """dsp.master on three tiled periods, keeping the middle one: the DC/rumble high-pass reaches steady state and
    master()'s edge fades land outside the kept period, so the loop stays sample-continuous across its seam."""
    L = len(x)
    return dsp.master(np.tile(x, 3), peak_db)[L:2 * L].copy()


# ====================================================================== registry / build
def V(fn, k):
    return lambda: fn(k)


EVENTS = [
    # name, [variant renderers], peak dBFS, loop
    ('sanity.heartbeat', [heartbeat], -3.0, False),
    ('sanity.whisper', [V(sanity_whisper, k) for k in range(5)], -1.0, False),
    ('sanity.footsteps', [V(sanity_footsteps, k) for k in range(3)], -3.0, False),
    ('sanity.knock', [V(sanity_knock, k) for k in range(3)], -3.0, False),
    ('sanity.breath', [V(sanity_breath, k) for k in range(2)], -3.0, False),
    ('crucifix.activate', [crucifix_activate], -1.0, False),
    ('crucifix.repel', [crucifix_repel], -0.5, False),
    ('holy_water.throw', [holy_water_throw], -3.0, False),
    ('holy_water.splash', [holy_water_splash], -3.0, False),
    ('holy_water.sizzle', [holy_water_sizzle], -0.5, False),
    ('salt.place', [salt_place], -3.0, False),
    ('emf.beep', [emf_beep], -3.0, False),
    ('flashlight.click', [flashlight_click], -3.0, False),
    ('flashlight.flicker', [flashlight_flicker], -3.0, False),
    ('spirit_box.static', [spirit_box_static], -3.0, False),
    ('spirit_box.voice', [V(spirit_box_voice, k) for k in range(8)], -1.0, False),
    ('camera.flash', [camera_flash], -3.0, False),
    ('ritual.chant', [ritual_chant], -1.0, False),
    ('ritual.complete', [ritual_complete], -0.5, False),
    ('jar.capture', [jar_capture], -0.5, False),
    ('pills.swallow', [pills_swallow], -3.0, False),
    ('flare.ignite', [flare_ignite], -3.0, False),
    ('flare.burn', [flare_burn], -4.0, True),
]


def rel_paths(name):
    count = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base] if count == 1 else [f'{base}_{i + 1}' for i in range(count)]


def build(only=None, review=True):
    os.makedirs(REVIEW_DIR, exist_ok=True)
    report = {}
    for name, fns, peak_db, loop in EVENTS:
        if only and not any(s in name for s in only):
            continue
        rels = rel_paths(name)
        assert len(rels) == len(fns), f'{name}: sounds_def wants {len(rels)} variants, module has {len(fns)}'
        for rel, fn in zip(rels, fns):
            t0 = time.time()
            raw = np.asarray(fn(), np.float32)
            assert raw.ndim == 1, f'{rel} must be mono'
            x = master_loop(raw, peak_db) if loop else finish(raw, peak_db)
            path = dsp.save_ogg(x, rel)
            # QA: Vorbis overshoots transient peaks by up to ~0.8 dB; re-master lower until the DECODED file meets its peak
            target = peak_db
            for _ in range(3):
                over = 20 * np.log10(np.max(np.abs(sf.read(path, dtype='float32')[0])) + 1e-12) - peak_db
                if over <= 0.25:
                    break
                target -= over + 0.05
                x = master_loop(raw, target) if loop else finish(raw, target)
                dsp.save_ogg(x, rel)
            a = dsp.analyse(x)
            a['secs'] = round(time.time() - t0, 1)
            report[rel] = a
            if review:
                dsp.spectrogram_png(x, os.path.join(REVIEW_DIR, rel.replace('/', '__') + '.png'))
            print(f'{rel:28s} {a}', flush=True)
    return report


if __name__ == '__main__':
    t_start = time.time()
    build(sys.argv[1:] or None)
    print(f'done in {time.time() - t_start:.1f} s')
