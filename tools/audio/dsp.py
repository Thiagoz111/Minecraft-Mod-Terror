"""Shared sound-design toolkit for DEAD LINE (numpy/scipy). Every generator imports this.

Conventions
  * float32 mono arrays at SR = 44100, nominal range -1..1.
  * Positional (in-world) sounds MUST be mono; only ambience/music streams may be stereo (shape (n, 2)).
  * save_ogg(x, 'llorona/cry_1') writes src/main/resources/assets/deadline/sounds/llorona/cry_1.ogg.
  * Always finish a sound with master(x, peak_db=-1.0) (normalise + DC removal + tiny fades).
"""
import hashlib
import os
import subprocess
import tempfile

import numpy as np
from scipy import signal

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'src/main/resources/assets/deadline/sounds')
TTS_CACHE = '/tmp/tts/cache'
RNG = np.random.default_rng(1234)


# ------------------------------------------------------------------ basics
def n_of(dur):
    return max(1, int(round(dur * SR)))


def t_axis(dur):
    return np.arange(n_of(dur)) / SR


def silence(dur):
    return np.zeros(n_of(dur), np.float32)


def rng(seed):
    return np.random.default_rng(seed)


def noise(dur, color='white', seed=None):
    r = rng(seed) if seed is not None else RNG
    n = n_of(dur)
    w = r.standard_normal(n)
    if color == 'white':
        x = w
    else:
        f = np.fft.rfftfreq(n, 1 / SR)
        f[0] = f[1] if n > 1 else 1
        spec = np.fft.rfft(w)
        if color == 'pink':
            spec /= np.sqrt(f)
        elif color == 'brown':
            spec /= f
        elif color == 'blue':
            spec *= np.sqrt(f)
        x = np.fft.irfft(spec, n)
    x = x / (np.max(np.abs(x)) + 1e-9)
    return x.astype(np.float32)


def osc(freq, dur, shape='sine', phase=0.0):
    """Oscillator; freq may be a number or an array (per-sample Hz) for glides/vibrato."""
    n = n_of(dur)
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,)) if np.ndim(freq) == 0 else np.asarray(freq, np.float64)[:n]
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if shape == 'sine':
        x = np.sin(ph)
    elif shape == 'saw':
        x = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    elif shape == 'square':
        x = np.sign(np.sin(ph))
    elif shape == 'tri':
        x = 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1.0) - 1) - 1
    else:
        raise ValueError(shape)
    return x.astype(np.float32)


def glide(f0, f1, dur, curve='exp'):
    n = n_of(dur)
    if curve == 'exp':
        return np.geomspace(max(f0, 1e-3), max(f1, 1e-3), n)
    return np.linspace(f0, f1, n)


def vibrato(base, dur, rate=5.0, depth=0.02):
    t = t_axis(dur)
    return base * (1 + depth * np.sin(2 * np.pi * rate * t))


# ------------------------------------------------------------------ envelopes
def env_adsr(n_or_dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = n_or_dur if isinstance(n_or_dur, int) else n_of(n_or_dur)
    na, nd, nr = n_of(a), n_of(d), n_of(r)
    ns = max(0, n - na - nd - nr)
    e = np.concatenate([np.linspace(0, 1, na, endpoint=False), np.linspace(1, s, nd, endpoint=False), np.full(ns, s), np.linspace(s, 0, nr)])
    return np.pad(e, (0, max(0, n - len(e))))[:n].astype(np.float32)


def env_exp(n_or_dur, decay=4.0, attack=0.002):
    n = n_or_dur if isinstance(n_or_dur, int) else n_of(n_or_dur)
    t = np.arange(n) / SR
    e = np.exp(-t * decay)
    na = n_of(attack)
    e[:na] *= np.linspace(0, 1, na)
    return e.astype(np.float32)


def env_points(n_or_dur, pts):
    """Piecewise-linear envelope from [(time_fraction, gain), ...]."""
    n = n_or_dur if isinstance(n_or_dur, int) else n_of(n_or_dur)
    xs = [p[0] * n for p in pts]
    ys = [p[1] for p in pts]
    return np.interp(np.arange(n), xs, ys).astype(np.float32)


def fade(x, fin=0.005, fout=0.02):
    x = x.copy()
    a, b = min(len(x), n_of(fin)), min(len(x), n_of(fout))
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


# ------------------------------------------------------------------ filters
def _sos(kind, f, order=4):
    nyq = SR / 2
    if isinstance(f, (tuple, list)):
        wn = [max(1e-4, min(0.999, v / nyq)) for v in f]
    else:
        wn = max(1e-4, min(0.999, f / nyq))
    return signal.butter(order, wn, btype=kind, output='sos')


def lowpass(x, f, order=4):
    return signal.sosfilt(_sos('lowpass', f, order), x, axis=0).astype(np.float32)


def highpass(x, f, order=4):
    return signal.sosfilt(_sos('highpass', f, order), x, axis=0).astype(np.float32)


def bandpass(x, lo, hi, order=4):
    return signal.sosfilt(_sos('bandpass', (lo, hi), order), x, axis=0).astype(np.float32)


def peak(x, f, gain_db=6.0, q=4.0):
    """Peaking EQ (resonance) at f Hz."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def sweep_lowpass(x, f0, f1, steps=48):
    """Time-varying low-pass (block-wise) from f0 to f1 Hz."""
    out = np.zeros_like(x)
    n = len(x)
    edges = np.linspace(0, n, steps + 1).astype(int)
    fs = np.geomspace(max(20, f0), max(20, f1), steps)
    zi = None
    for i in range(steps):
        sos = _sos('lowpass', fs[i], 2)
        seg = x[edges[i]:edges[i + 1]]
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        y, zi = signal.sosfilt(sos, seg, zi=zi)
        out[edges[i]:edges[i + 1]] = y
    return out.astype(np.float32)


def formant(x, formants=((700, 1200, 2600),), q=8.0):
    """Vowel-ish colouring: sum of resonant band-passes."""
    out = np.zeros_like(x)
    for fset in formants:
        for f in fset:
            out += bandpass(x, f / (1 + 1 / q), f * (1 + 1 / q), 2)
    return out


# ------------------------------------------------------------------ effects
def reverb(x, decay=2.2, wet=0.35, damp=5000.0, predelay=0.02, seed=7, stereo=False):
    """Convolution reverb with a synthetic decaying-noise impulse response."""
    n = n_of(decay * 1.3)
    r = rng(seed)
    t = np.arange(n) / SR
    ir_l = r.standard_normal(n) * np.exp(-6.9 * t / decay)
    ir_l = lowpass(ir_l.astype(np.float32), damp, 2)
    pd = n_of(predelay)
    ir_l = np.concatenate([np.zeros(pd), ir_l])
    ir_l /= np.sqrt(np.sum(ir_l ** 2)) + 1e-9
    mono = x if x.ndim == 1 else x.mean(axis=1)
    pad = np.concatenate([mono, np.zeros(len(ir_l))])
    if stereo:
        ir_r = r.standard_normal(n) * np.exp(-6.9 * t / decay)
        ir_r = np.concatenate([np.zeros(pd), lowpass(ir_r.astype(np.float32), damp, 2)])
        ir_r /= np.sqrt(np.sum(ir_r ** 2)) + 1e-9
        wl = signal.fftconvolve(pad, ir_l)[:len(pad)]
        wr = signal.fftconvolve(pad, ir_r)[:len(pad)]
        dry = np.stack([pad, pad], 1)
        return ((1 - wet) * dry + wet * np.stack([wl, wr], 1)).astype(np.float32)
    w = signal.fftconvolve(pad, ir_l)[:len(pad)]
    return ((1 - wet) * pad + wet * w).astype(np.float32)


def echo(x, delay=0.25, feedback=0.4, taps=5, damp=4000.0):
    d = n_of(delay)
    out = np.concatenate([x, np.zeros(d * taps)]).astype(np.float32)
    tap = x.copy()
    for i in range(1, taps + 1):
        tap = lowpass(tap, damp, 2) * feedback
        out[i * d:i * d + len(tap)] += tap
    return out


def drive(x, amount=3.0):
    return (np.tanh(x * amount) / np.tanh(amount)).astype(np.float32)


def bitcrush(x, bits=8, down=4):
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    y = np.repeat(y[::down], down)[:len(x)]
    return y.astype(np.float32)


def ring(x, freq):
    return (x * osc(freq, len(x) / SR)[:len(x)]).astype(np.float32)


def tremolo(x, rate=6.0, depth=0.5):
    t = np.arange(len(x)) / SR
    return (x * (1 - depth * 0.5 * (1 + np.sin(2 * np.pi * rate * t)))).astype(np.float32)


def reverse(x):
    return x[::-1].copy()


def resample(x, factor):
    """Speed change: factor > 1 = faster & higher (tape style)."""
    n = max(1, int(len(x) / factor))
    return signal.resample(x, n).astype(np.float32)


def pitch_shift(x, semitones, frame=2048, hop=512):
    """Duration-preserving pitch shift (phase vocoder stretch + resample)."""
    if abs(semitones) < 1e-3:
        return x.copy()
    factor = 2 ** (semitones / 12)
    stretched = time_stretch(x, 1 / factor, frame, hop)
    return resample(stretched, factor)[:len(x)] if len(stretched) else x


def time_stretch(x, rate, frame=2048, hop=512):
    """Phase-vocoder time stretch. rate < 1 = slower/longer."""
    win = np.hanning(frame)
    pad = np.concatenate([np.zeros(frame), x, np.zeros(frame)])
    stft = np.array([np.fft.rfft(win * pad[i:i + frame]) for i in range(0, len(pad) - frame, hop)])
    if len(stft) < 2:
        return x.copy()
    steps = np.arange(0, len(stft) - 1, rate)
    phase = np.angle(stft[0])
    omega = 2 * np.pi * hop * np.arange(frame // 2 + 1) / frame
    out = np.zeros(int(len(steps) * hop + frame))
    for k, s in enumerate(steps):
        i = int(s)
        frac = s - i
        mag = (1 - frac) * np.abs(stft[i]) + frac * np.abs(stft[i + 1])
        frame_out = np.fft.irfft(mag * np.exp(1j * phase))
        out[k * hop:k * hop + frame] += win * frame_out
        dphi = np.angle(stft[i + 1]) - np.angle(stft[i]) - omega
        dphi -= 2 * np.pi * np.round(dphi / (2 * np.pi))
        phase += omega + dphi
    out = out[frame:-frame] if len(out) > 2 * frame else out
    return (out / (np.max(np.abs(out)) + 1e-9) * (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


def granular(x, dur, grain=0.08, density=40, jitter=1.0, pitch_jitter=0.0, seed=3):
    """Granular cloud: sprinkles windowed grains of x across dur seconds."""
    r = rng(seed)
    out = np.zeros(n_of(dur) + n_of(grain) * 2, np.float32)
    g = n_of(grain)
    win = np.hanning(g).astype(np.float32)
    count = int(density * dur)
    for _ in range(count):
        src = int(r.random() * max(1, len(x) - g))
        piece = x[src:src + g]
        if len(piece) < g:
            continue
        if pitch_jitter:
            piece = resample(piece, 2 ** (r.normal(0, pitch_jitter) / 12))[:g]
            piece = np.pad(piece, (0, g - len(piece)))
        pos = int(r.random() * jitter * (len(out) - g))
        out[pos:pos + g] += piece * win
    return out[:n_of(dur)]


def mix(*parts, length=None):
    """mix((sound, start_seconds, gain), ...) -> mono or stereo sum."""
    stereo = any(p[0].ndim == 2 for p in parts)
    end = max(n_of(p[1]) + len(p[0]) for p in parts) if length is None else n_of(length)
    out = np.zeros((end, 2) if stereo else end, np.float32)
    for snd, start, gain in parts:
        s = n_of(start) if start > 0 else 0
        if stereo and snd.ndim == 1:
            snd = np.stack([snd, snd], 1)
        seg = snd[:max(0, end - s)]
        out[s:s + len(seg)] += seg * gain
    return out


def pan(x, p):
    """Mono -> stereo with equal-power pan p in -1..1."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1).astype(np.float32)


def concat(*xs, gap=0.0):
    out = []
    for i, x in enumerate(xs):
        out.append(x)
        if gap and i < len(xs) - 1:
            out.append(np.zeros((n_of(gap),) + x.shape[1:], np.float32))
    return np.concatenate(out).astype(np.float32)


def trim(x, thresh_db=-60.0, tail=0.05):
    """Cut trailing (and leading) near-silence, keeping a short tail."""
    m = np.abs(x if x.ndim == 1 else x.mean(axis=1))
    th = np.max(m) * 10 ** (thresh_db / 20)
    idx = np.where(m > th)[0]
    if not len(idx):
        return x
    return x[max(0, idx[0] - n_of(0.005)):min(len(x), idx[-1] + n_of(tail))]


def master(x, peak_db=-1.0, hp=30.0):
    """DC/rumble removal, normalisation to peak_db dBFS, click-free edges."""
    y = highpass(x, hp, 2)
    y = fade(y, 0.003, 0.02)
    p = np.max(np.abs(y)) + 1e-9
    return (y / p * 10 ** (peak_db / 20)).astype(np.float32)


# ------------------------------------------------------------------ voices (Kokoro TTS, Spanish)
_K = None


def tts(text, voice='ef_dora', speed=0.9, lang='es', accent='rioplatense'):
    """Spanish speech as mono float32 @ 44.1 kHz. Voices: ef_dora (woman), em_alex (man), em_santa (deep man).

    accent='rioplatense' (default): Latin-American phonemes (seseo, no Castilian 'th') plus Buenos Aires sheismo
    (ll/y -> sh). accent=None uses espeak's plain 'es'. Cached on disk, so re-running generators is cheap."""
    global _K
    os.makedirs(TTS_CACHE, exist_ok=True)
    key = hashlib.sha1(f'{voice}|{speed}|{lang}|{accent}|{text}'.encode()).hexdigest()[:16]
    path = os.path.join(TTS_CACHE, key + '.npy')
    if os.path.exists(path):
        return np.load(path)
    if _K is None:
        from kokoro_onnx import Kokoro
        _K = Kokoro('/tmp/tts/kokoro-v1.0.int8.onnx', '/tmp/tts/voices-v1.0.bin')
    if accent == 'rioplatense':
        ph = _K.tokenizer.phonemize(text, 'es-419')
        ph = ph.replace('ʝ', 'ʃ').replace('ʎ', 'ʃ')
        s, sr = _K.create(ph, voice=voice, speed=speed, lang='es-419', is_phonemes=True)
    else:
        s, sr = _K.create(text, voice=voice, speed=speed, lang=lang)
    y = signal.resample_poly(np.asarray(s, np.float64), SR, sr).astype(np.float32)
    np.save(path, y)
    return y


def phone_voice(x):
    """Telephone line: band-limited, slightly crushed, with line hiss."""
    y = bandpass(x, 320, 3400, 4)
    y = drive(y * 1.5, 2.0)
    y = bitcrush(y, 10, 2)
    hiss = bandpass(noise(len(y) / SR, 'white', 9), 2000, 6000, 2) * 0.02
    return y + hiss[:len(y)]


def demonic(x, semis=-7, layers=(-12, 0), wet=0.25):
    """Layered pitch-shifted voice with grit: possession / monster speech."""
    parts = [pitch_shift(x, semis + l) * (0.8 if l else 1.0) for l in layers]
    n = min(len(p) for p in parts)
    y = sum(p[:n] for p in parts)
    y = drive(y, 2.5)
    return reverb(y, 1.6, wet, 3500)


# ------------------------------------------------------------------ output + analysis
def save_ogg(x, rel, quality=5):
    """Write OGG Vorbis at sounds/<rel>.ogg. Mono stays mono (needed for 3D positioning)."""
    import soundfile as sf
    path = os.path.join(OUT, rel + '.ogg')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = np.clip(np.asarray(x, np.float32), -1, 1)
    fd, wav = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    try:
        sf.write(wav, x, SR, subtype='PCM_16')
        ch = '1' if x.ndim == 1 else '2'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-ac', ch, '-ar', str(SR), '-c:a', 'libvorbis', '-q:a', str(quality), path], check=True)
    finally:
        os.unlink(wav)
    return path


def analyse(x):
    m = x if x.ndim == 1 else x.mean(axis=1)
    rms = np.sqrt(np.mean(m ** 2) + 1e-12)
    spec = np.abs(np.fft.rfft(m * np.hanning(len(m)))) if len(m) > 32 else np.zeros(2)
    f = np.fft.rfftfreq(len(m), 1 / SR) if len(m) > 32 else np.zeros(2)
    cent = float(np.sum(f * spec) / (np.sum(spec) + 1e-9))
    env = np.abs(m)
    silent = float(np.mean(env < 10 ** (-50 / 20)))
    return {
        'dur': round(len(m) / SR, 2), 'peak_db': round(float(20 * np.log10(np.max(env) + 1e-12)), 1),
        'rms_db': round(float(20 * np.log10(rms)), 1), 'centroid_hz': int(cent), 'silent_ratio': round(silent, 2),
        'clipped': int(np.sum(env > 0.999)), 'channels': 1 if x.ndim == 1 else 2,
    }


def spectrogram_png(x, path, width=900, height=300):
    """Waveform (top) + log spectrogram (bottom) for visual self-review."""
    from PIL import Image
    m = x if x.ndim == 1 else x.mean(axis=1)
    f, t, S = signal.spectrogram(m, SR, nperseg=1024, noverlap=768)
    S = 10 * np.log10(S + 1e-12)
    S = np.clip((S + 100) / 80, 0, 1)
    keep = f < 12000
    S = S[keep][::-1]
    spec = Image.fromarray((np.stack([S ** 0.7, S ** 1.6, S ** 3], -1) * 255).astype(np.uint8)).resize((width, height))
    wave = np.zeros((90, width, 3), np.uint8) + 20
    cols = np.array_split(m, width)
    for i, c in enumerate(cols):
        if len(c):
            hi, lo = int(45 - np.max(c) * 44), int(45 - np.min(c) * 44)
            wave[max(0, hi):min(90, lo + 1), i] = (90, 220, 120)
    img = Image.new('RGB', (width, height + 90))
    img.paste(Image.fromarray(wave), (0, 0))
    img.paste(spec, (0, 90))
    img.save(path)
    return path
