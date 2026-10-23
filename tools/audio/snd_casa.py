# -*- coding: utf-8 -*-
"""DEAD LINE - sound group "sfx" for case 2, Casa Morales (house / foley events).

Run from the repo root:  python3 tools/audio/snd_casa.py [substring ...]

A 1950s chalet in Villa Esperanza where a demon in a porcelain doll jumps from body to body (BIBLIA 2.2 f / h / l).
Suburban family comedy turning into real dread: the comic beats are played as straight, physical foley pushed to the
point where they land (the slipper, the empty mate, the walker wheel); the scares are physical too, only wrong.
Everything is synthesised from physical models: modal resonators excited by contact pulses, stick-slip friction
trains, Poisson debris and droplets, Minnaert bubbles, time-varying delay fly-bys (true Doppler), turbulent noise
shaped by formant tracks, a small additive voice synth for the porcelain giggles and the demon yelps, and Kokoro TTS
fragments for the soap opera on the Nona's TV.

  casa.breaker_trip        beat 4: fridge, kitchen tube and the living-room CRT humming; a 1960s llave termica trips
                           (latch tick, spark, CLONK in its tin box); the tube spits once, the CRT collapses, the
                           compressor winds down and shudders to a stop; cooling ticks in the dark lavadero.
  casa.breaker_reset       lever scraped up, KA-CHUNK + spark, transformer inrush, the TV degausses (BWOMM) in the
                           living room, the tube's glow starter ticks and flickers until it catches, the fridge
                           compressor kicks back in; the hum bed settles and fades under the ambience.
  casa.tv_novela           LOOP 20 s (mono, positional TV): a telenovela at full volume through a tired CRT speaker -
                           "Mercedes"/"Rodolfo" melodrama (TTS, sobbing, shouting), a string underscore, two
                           orchestral stings with timpani; mains buzz and the 15 625 Hz line whine.
  casa.tv_static           LOOP 8 s (mono): untuned CRT snow, 50 Hz field buzz, screen-charge crackle, flyback whine.
  grill.sizzle             LOOP 5 s: fat sizzling and spitting on embers, charcoal ticks, low fire breath.
  fire.blue_whoosh         the grill flares (suck - FWOOMP), turns into a blue gas jet and then slows, unnaturally,
                           into a low breathing groan with a sub drone.
  knife.lift (2)           kitchen knives drawn out of the wooden rack by nobody: wood-slot scrape, steel shing,
                           blades left ringing and slowly turning in the air (v2: they touch and start to sing).
  knife.whoosh (3)         a spinning knife passing (true Doppler): blade/handle whirr, edge whistle.
  knife.impact (3)         THUNK into wood (fence plank / table / lemon tree), fibres crunch, the blade wobbling.
  salt.hit_scream          a fistful of salt crackling on skin, acid hiss, and possessed Jorge's yelp (man + demon).
  pool.splash              Jorge falls like a sack into the pelopincho: slap, plunge, cavity bloop, PVC walls
                           bwomp, spray raining back, slosh, overflow on the patio bricks.
  plate.whoosh (4)         a china plate frisbeeing past your head (spin whirr, rim whistle, close-pass buffet).
  plate.shatter (3)        wall hit with shards raining / floor smash and skitter / split in two big halves.
  plate.storm              4 s of plates, cups and cutlery cascading down the stair into the 1961 room.
  mate.slide               the ceramic mate dragged 2 blocks over formica: gritty chatter, bombilla rattle, rock.
  mate.sip_empty           [RISA] THE empty-mate gurgle: a wet start, a long dry rattling SHHRRRK-K-K, big glugs,
                           a lip pop ... and one last hopeless little sip.
  termo.fly                the thermos tumbling and whistling past (Doppler fiuuu), CLANG, bounce, rolling over
                           the tile joints with water glugging inside, tonk.
  alacena.golpe (3)        70s kitchen cupboard doors: single bang / swing-creak-BANG / three in a row, dishes rattle.
  chair.stack              the 8-chair tower that happened while you weren't looking: last clatter, the stack groans,
                           the top chair rocks tok... tok.. tok.tok-tk to a stop.
  door.slam_cascade        5 doors of the upstairs hallway slamming, accelerating and closer each time (far ones
                           dark and reverberant, the last right next to you with a pressure thump).
  bulb.pop (2)             incandescent bulb implodes: filament tick, pop, thin glass shards / buzz-flicker first.
  doll.turn (3)            porcelain head turning on its neck: grind + tok / ratchet / slow squeal + tink.
  doll.giggle_chorus       10 tiny porcelain giggles out of phase on Lucia's shelf; one slow giggle stays behind.
  andador.squeak (3)       the Nona's walker: rubber feet "tunk" and THE wheel motif "ee-EEK" (running gag).
  chancleta.whip           the Nona's rubber slipper flapping end over end through the air (fwap-fwap-fwap).
  chancleta.hit            ¡PLAF! sole on flesh (crack + thwack + rubber bomp + toe flap), slipper drops, plop.
  rocking.creak_slow       LOOP 4 s: the floating rocking chair, two joint creaks per swing, no floor contact.
  yarn.twang (2)           taut red wool plucked: a dull, fuzzy, lossy string with a falling twang / stretch first.
  yarn.snap                fibres giving way one by one, SNAP, the halves whipping back, slack yarn falling.
  stitch.pull (3)          ASMR-close: needle punctures the cloth, the thread hisses through, tug and squeak.
  azamel.suck              a scream run backwards, sucked into a point with the room; cut; one porcelain "tink".
  candles.out              one long (possessed) breath and 7 altar flames fluttering out, the last one stubborn.
  wall.break               two huge blows and the brick wall of the basement collapses (boom, crack, rubble, dust).
  wisp.whistle             the demon wisp: a thin wavering two-voice whistle with ember crackle travelling past.
  morning.birds            STREAM stereo 20 s loop: benteveo, horneros, sparrows, torcazas, a zorzal, a far
                           colectivo pulling away; the air of a suburban morning.
  kettle.whistle           the pava on the hob: burner, singing water, breathy first tries, full shrill two-tone
                           whistle, taken off: the pitch falls and sputters out, set down on the grate.
  ambient.casa             STREAM stereo 60 s loop (REPLACES the old bed): a suburban house at night - fridge cycling
                           on and off, the living-room clock, crickets, far traffic, dogs answering across the
                           barrio, the house settling (beams, roof tiles, a pipe knock).

Positional sounds are mono (tv_novela / tv_static too: the TV is a block in the living room); only morning.birds and
ambient.casa are stereo. Loudness: stingers -0.5 dBFS, foley/UI -3 dBFS, loops/streams -4 dBFS.
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

REVIEW_DIR = os.environ.get('DEADLINE_REVIEW_DIR', _os.path.join(WORK, 'audio/casa_sfx'))
TWO_PI = 2 * np.pi
C_AIR = 343.0


# ====================================================================== small helpers
def N(sec):
    return max(1, int(round(sec * SR)))


def taxis(n):
    return np.arange(n) / SR


def norm(x, peak=1.0):
    return (np.asarray(x, np.float32) / (np.max(np.abs(x)) + 1e-12) * peak).astype(np.float32)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-20))


def fit(x, n):
    x = np.asarray(x, np.float32)
    if len(x) >= n:
        return x[:n]
    return np.pad(x, ((0, n - len(x)),) + ((0, 0),) * (x.ndim - 1))


def add(buf, x, t, g=1.0):
    """Mix x into buf starting at t seconds (truncated at the end of buf). Mono x into stereo buf goes centre."""
    s = max(0, N(t)) if t > 0 else 0
    m = min(len(x), len(buf) - s)
    if m > 0:
        if buf.ndim == 2 and x.ndim == 1:
            buf[s:s + m] += (x[:m] * g)[:, None] * 0.7071
        else:
            buf[s:s + m] += x[:m] * g
    return buf


def addp(buf, x, t, g=1.0, p=0.0):
    """Mix mono x into a stereo buf with an equal-power pan p (-1 left .. 1 right)."""
    return add(buf, dsp.pan(np.asarray(x, np.float32) * g, float(np.clip(p, -1, 1))), t)


def white(n, seed):
    return dsp.rng(seed).standard_normal(n).astype(np.float32)


def colored(n, color, seed):
    return fit(dsp.noise(n / SR + 1e-4, color, seed), n)


def snoise(n, cutoff, seed):
    """Smooth random control signal in about -1..1 (low-passed noise)."""
    w = dsp.rng(seed).standard_normal(n + 8192).astype(np.float32)
    y = dsp.lowpass(w, cutoff, 2)[8192:]
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def csnoise(n, cutoff, seed):
    """Circular (periodic over n samples) smooth random control signal in about -1..1."""
    y = cfilt(white(n, seed), lambda f: lp2(f, cutoff))
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def grain(n, cutoff, seed, power=2.0):
    """Positive rough-texture modulator with mean 1 (|low-passed noise|^power)."""
    g = np.abs(dsp.lowpass(white(n + 4096, seed), cutoff, 2)[4096:]) ** power
    return (g / (np.mean(g) + 1e-9)).astype(np.float32)


def cgrain(n, cutoff, seed, power=2.0):
    g = np.abs(cfilt(white(n, seed), lambda f: lp2(f, cutoff))) ** power
    return (g / (np.mean(g) + 1e-9)).astype(np.float32)


def env_pts(n, pts):
    """Piecewise-linear envelope from [(seconds, gain), ...]."""
    ts = [p[0] * SR for p in pts]
    return np.interp(np.arange(n), ts, [p[1] for p in pts]).astype(np.float32)


def contour(n, pts):
    """Log-interpolated frequency contour from [(seconds, Hz), ...]."""
    return np.exp(env_pts(n, [(t, np.log(f)) for t, f in pts])).astype(np.float64)


def smooth(x, sec):
    return uniform_filter1d(np.asarray(x, np.float32), max(1, N(sec)))


def smoothstep(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


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


def scale_modes(modes, k=1.0, dk=1.0):
    return [(f * k, d * dk, a) for f, d, a in modes]


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


def crackle(n, rate, seed, lo=1500.0, hi=9000.0, amp_env=None, size=(0.0003, 0.0025), pareto=2.2):
    """Poisson crackle: tiny decaying noise ticks with heavy-tailed amplitudes (fibres, fat, embers, sparks)."""
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
            lo, hi = max(20.0, f * 2 ** (-bw_oct / 2)), min(0.97 * nyq, f * 2 ** (bw_oct / 2))
            lo = min(lo, 0.5 * hi)
            sos = signal.butter(1, [lo / nyq, hi / nyq], 'bandpass', output='sos')
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[a:b], zi=zi)
        out[a:b] = y
    return out


def bp(x, lo, hi, order=2):
    return dsp.bandpass(x, lo, hi, order)


def varispeed(x, rate, n_out=None):
    """Tape-style read with a per-output-sample speed (1 = normal): pitch and time move together."""
    rate = np.broadcast_to(np.asarray(rate, np.float64), (n_out or len(x),))
    pos = np.cumsum(rate) - rate[0]
    return np.interp(pos, np.arange(len(x)), x, right=0.0).astype(np.float32)


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
    """Minnaert bubble / drop resonance: decaying sine gliding upward."""
    r = dsp.rng(seed)
    d = (40 + f0 * 0.05) * dmul
    dur = min(0.4, 6.5 / d)
    t = taxis(N(dur))
    fr = f0 * (1 + rise * t * d / 6)
    y = np.sin(TWO_PI * np.cumsum(fr) / SR + r.uniform(0, 6)) * np.exp(-d * t) * np.minimum(1, t / 0.0008)
    return (y * amp).astype(np.float32)


def glass_ping(seed, f, decay=None, amp=1.0, click=0.5):
    """A shard of thin glass: inharmonic plate modes + a hard tick."""
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


def china_ping(seed, f, amp=1.0, decay=None, click=0.55):
    """Porcelain / china shard: denser, more damped than glass, a chalky 'clink'."""
    r = dsp.rng(seed)
    decay = decay or (40 + f * 0.016) * r.uniform(0.7, 1.3)
    ratios = [1.0, r.uniform(1.5, 1.75), r.uniform(2.3, 2.75), r.uniform(3.3, 4.0), r.uniform(4.6, 5.5)]
    amps = [1.0, r.uniform(.5, .9), r.uniform(.3, .6), r.uniform(.15, .35), r.uniform(.05, .2)]
    dur = min(0.45, 6.5 / decay)
    y = modal_ir([(f * ra, decay * ra ** 0.7, a) for ra, a in zip(ratios, amps)], dur, seed)
    y = norm(y * np.minimum(1, taxis(len(y)) / 0.00015))
    if click:
        cl = dsp.highpass(burst(0.0012, seed + 5, 2.0), 1800, 2)
        y[:len(cl)] += click * norm(cl)
    return (y * amp).astype(np.float32)


def creak(dur, seed, rate_pts, modes, amp_pts=None, jitter=0.3, grit=0.25, tail=0.15):
    """Wood/metal creak: a stick-slip pulse train (rate contour in Hz) ringing a modal body."""
    n = N(dur)
    rate = env_pts(n, rate_pts)
    amp = env_pts(n, amp_pts) if amp_pts else np.ones(n, np.float32)
    idx, a = stick_slip(n, rate, seed, jitter, amp, 0.4)
    exc = pulse_train(n, idx, a, half_sine(0.0004))
    exc += grit * bp(white(n, seed + 3), 1500, 7000) * amp * 0.05
    return excite(exc, detune(modes, dsp.rng(seed + 9), 0.03), tail)


def flyby(src, t_close, speed, d_min, lp_near=16000.0, lp_far=2200.0, buffet=0.0, seed=0):
    """Moving source passing the listener: time-varying propagation delay (true Doppler), 1/r gain, air/head LP."""
    n = len(src)
    t = taxis(n)
    d = np.sqrt((speed * (t - t_close)) ** 2 + d_min ** 2)
    read = np.arange(n) - d / C_AIR * SR
    y = np.interp(read, np.arange(n), src, left=0.0, right=0.0).astype(np.float32)
    g = (d_min / d).astype(np.float32)
    y = tv_filter(y * g, 'lp', lp_far + (lp_near - lp_far) * g ** 1.5, steps=80)
    if buffet:
        win = np.exp(-0.5 * ((t - t_close) / 0.035) ** 2)
        y += buffet * norm(dsp.lowpass(white(n, seed + 77), 180, 2)) * win.astype(np.float32)
    return y


def saw_blep(freq, n):
    """Band-limited (polyBLEP) sawtooth with a per-sample frequency."""
    dt = np.broadcast_to(np.asarray(freq, np.float64), (n,)) / SR
    ph = np.cumsum(dt) % 1.0
    y = 2 * ph - 1
    m1 = ph < dt
    u = ph[m1] / dt[m1]
    y[m1] -= u + u - u * u - 1
    m2 = ph > 1 - dt
    u = (ph[m2] - 1) / dt[m2]
    y[m2] -= u * u + u + u + 1
    return y.astype(np.float32)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ====================================================================== circular (loop-safe) tools
def cfilt(x, gain_fn):
    """Circular zero-phase filter defined by a magnitude function of frequency (Hz). Mono or stereo."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = gain_fn(f)
    g = g[:, None] if x.ndim == 2 else g
    return np.fft.irfft(X * g, len(x), axis=0).astype(np.float32)


def cfft_hp(x, f=35.0):
    return cfilt(x, lambda fr: 1 / np.sqrt(1 + (f / np.maximum(fr, 1e-3)) ** 8))


def hp2(f, fc):
    return (f / fc) ** 2 / np.sqrt(1 + (f / fc) ** 4)


def lp2(f, fc):
    return 1 / np.sqrt(1 + (f / fc) ** 4)


def lp1(f, fc):
    return 1 / np.sqrt(1 + (f / fc) ** 2)


def bump(f, c, w_oct, gain):
    return gain * np.exp(-0.5 * ((np.log2(np.maximum(f, 1.0)) - np.log2(c)) / w_oct) ** 2)


def fold(x, L):
    """Wrap everything past L samples back onto the start (circular buffer)."""
    x = np.pad(x, ((0, -len(x) % L),) + ((0, 0),) * (x.ndim - 1))
    return x.reshape((-1, L) + x.shape[1:]).sum(0).astype(np.float32)


def loop_iir(x, fn):
    """Apply a causal (IIR / time-varying) process to a periodic buffer without a seam: run it on two periods and
    keep the second, so the filter state at the start is the state it had at the end."""
    L = len(x)
    y = fn(np.concatenate([x, x], 0))
    return np.asarray(y[L:2 * L], np.float32)


# ====================================================================== rooms (BIBLIA 2.2 f)
ROOMS = {
    'living': dict(decay=0.65, damp=5200.0, predelay=0.004, er=7, er_span=0.024, hf=0.55),    # carpets, floral sofa
    'comedor': dict(decay=0.75, damp=5600.0, predelay=0.005, er=7, er_span=0.026, hf=0.55),   # 7x6, long table
    'cocina': dict(decay=0.7, damp=7500.0, predelay=0.004, er=8, er_span=0.02, hf=0.7, flutter=0.019),  # 70s tiles
    'lavadero': dict(decay=0.55, damp=7000.0, predelay=0.003, er=8, er_span=0.012, hf=0.7, flutter=0.0125),
    'pasillo': dict(decay=1.05, damp=5200.0, predelay=0.006, er=8, er_span=0.05, hf=0.5, flutter=0.0118),  # 2x12
    'pieza': dict(decay=0.5, damp=4300.0, predelay=0.004, er=7, er_span=0.018, hf=0.5),       # bedrooms, textiles
    'patio': dict(decay=0.5, damp=6500.0, predelay=0.006, er=5, er_span=0.045, hf=0.6),       # long yard, house wall
    'sotano': dict(decay=1.7, damp=3800.0, predelay=0.012, er=8, er_span=0.04, hf=0.45),      # concrete basement
    'cuarto61': dict(decay=1.25, damp=4200.0, predelay=0.008, er=8, er_span=0.03, hf=0.5),
    'escalera': dict(decay=1.15, damp=4800.0, predelay=0.006, er=8, er_span=0.035, hf=0.5),
    'cerca': dict(decay=0.22, damp=6000.0, predelay=0.001, er=4, er_span=0.004, hf=0.6),      # ASMR close
    'barrio': dict(decay=1.6, damp=2400.0, predelay=0.03, er=6, er_span=0.25, hf=0.5, er_gain=6.0),  # between houses
    'casa_noche': dict(decay=0.9, damp=4600.0, predelay=0.006, er=7, er_span=0.03, hf=0.5),
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
    fl = p.get('flutter', 0.0)
    if fl:
        for k in range(1, 14):
            q = int(k * fl * SR)
            if q < n:
                ir[q] += lvl * 8 * 0.7 ** k * (-1) ** k
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
VOW = {  # adult male: (formant Hz, bandwidth Hz, amplitude); scale ~1.17 = woman, ~1.3 = child, ~1.6 = porcelain doll
    'a': ((730, 90, 1.0), (1100, 110, 0.55), (2450, 160, 0.28), (3400, 230, 0.13), (4400, 300, 0.05)),
    'e': ((450, 70, 1.0), (1850, 110, 0.42), (2500, 160, 0.3), (3500, 230, 0.12), (4500, 300, 0.05)),
    'i': ((290, 60, 1.0), (2250, 120, 0.32), (3000, 170, 0.32), (3700, 230, 0.15), (4600, 300, 0.05)),
    'o': ((500, 80, 1.0), (850, 90, 0.6), (2450, 160, 0.13), (3400, 230, 0.06), (4400, 300, 0.03)),
    'u': ((320, 60, 1.0), (800, 90, 0.42), (2300, 160, 0.08), (3300, 230, 0.04), (4300, 300, 0.02)),
    'h': ((650, 300, 0.6), (1500, 350, 0.6), (2500, 400, 0.5), (3500, 450, 0.4), (4500, 500, 0.3)),
}


def vowel(name, scale=1.0, bw=1.0, name2=None, mix=0.0):
    a = np.array(VOW[name], np.float64)
    if name2:
        a = (1 - mix) * a + mix * np.array(VOW[name2], np.float64)
    a[:, 0] *= scale
    a[:, 1] *= bw * (0.6 + 0.4 * scale)
    return a


def ftrack(n, keys, glide=0.05):
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


def shaped_noise(fr, n, seed, nper=1024, hf=0.0, lp=None):
    """White noise filtered (STFT) by a formant track: breath, aspiration, roar turbulence."""
    hop = nper // 4
    w = white(n + nper, seed)
    f, t, Z = signal.stft(w, SR, nperseg=nper, noverlap=nper - hop)
    fi = np.clip((t * SR / CTRL).astype(int), 0, fr.shape[0] - 1)
    ff = np.broadcast_to(f[None, :], (len(fi), len(f)))
    g = fgain(ff, fr[fi])
    if lp:
        g = g / np.sqrt(1 + (f[None, :] / lp) ** 4)
    if hf:
        g = g * (1 + hf * f[None, :] / 4000.0)
    _, y = signal.istft(Z * g.T, SR, nperseg=nper, noverlap=nper - hop)
    return fit(y, n)


def vsynth(f0, fr, amp, tilt=1.2, jitter=0.006, shimmer=0.05, rough=0.0, rough_hz=70.0, sub=0.0, breath=0.05,
           fmax=8000.0, seed=0, floor=0.004):
    """Additive glottal source through formants. f0/amp per sample, fr control-rate track (see ftrack)."""
    n = len(f0)
    rough = np.broadcast_to(np.asarray(rough, np.float64), (n,))
    f0 = np.asarray(f0, np.float64) * (1 + jitter * snoise(n, 30, seed + 1))
    if rough.max() > 0:
        f0 = f0 * (1 + 0.03 * rough * snoise(n, rough_hz, seed + 2))
    ph = TWO_PI * np.cumsum(f0) / SR
    nfr = fr.shape[0]
    ci = np.minimum(np.arange(nfr) * CTRL, n - 1)
    f0c = f0[ci]
    K = max(1, int(fmax / max(25.0, f0c.min())))
    tt = np.arange(n)
    r = dsp.rng(seed)
    phs = r.uniform(0, TWO_PI, 2 * K + 2)

    def bank(mults, phases):
        fk = f0c[:, None] * mults[None, :]
        g = (fgain(fk, fr) + floor) * mults[None, :] ** (-tilt) * np.clip((fmax - fk) / (0.2 * fmax), 0, 1)
        y = np.zeros(n)
        for j, k in enumerate(mults):
            if g[:, j].max() < 1e-6:
                continue
            y += np.interp(tt, ci, g[:, j]) * np.sin(k * ph + phases[j])
        return y

    y = bank(np.arange(1, K + 1, dtype=np.float64), phs)
    if sub > 0:
        y += sub * (0.65 + 0.35 * snoise(n, 7, seed + 5)) * bank(np.arange(0.5, K + 0.5, 1.0), phs[K:])
    if shimmer:
        y *= 1 + shimmer * snoise(n, 40, seed + 3)
    if rough.max() > 0:
        y *= np.clip(1 + 0.6 * rough * snoise(n, rough_hz * 1.3, seed + 4), 0.05, None)
    y *= amp
    if breath:
        nz = shaped_noise(fr, n, seed + 6, hf=0.3)
        nz *= rms(y) / (rms(nz * amp) + 1e-9)
        y = y + breath * nz * amp
    return y.astype(np.float32)


# ====================================================================== house electrics (shared)
BREAKER_BOX = [(160, 45, 0.7), (290, 50, 1.0), (520, 60, 0.85), (880, 75, 0.6), (1420, 95, 0.45), (2300, 130, 0.3),
               (3600, 170, 0.18)]   # tin box screwed to the lavadero wall
LEVER = [(1750, 70, 1.0), (3150, 90, 0.8), (4800, 120, 0.55), (6900, 160, 0.35)]   # bakelite toggle + steel latch
FRIDGE_HZ = 48.6   # 2-pole compressor motor on 50 Hz mains, slipping a little under load


def fridge_motor(f, seed, rattle=0.35):
    """Fridge compressor: motor fundamental + harmonics (piston), 100 Hz magnetostriction, tube rattle per stroke."""
    n = len(f)
    ph = TWO_PI * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.65 * np.sin(2 * ph + 0.4) + 0.42 * np.sin(3 * ph + 1.1) + 0.3 * np.sin(4 * ph + 2.0)
         + 0.16 * np.sin(6 * ph + 0.3) + 0.09 * np.sin(8 * ph + 2.4) + 0.05 * np.sin(11 * ph + 1.3))
    stroke = (0.5 + 0.5 * np.cos(ph)) ** 10   # one knock per revolution into the cabinet and the copper tubes
    knockn = bp(white(n, seed), 250, 1600) * stroke
    return (norm(y) + rattle * norm(knockn)).astype(np.float32)


def tube_buzz(n, seed, level=1.0):
    """Fluorescent tube + magnetic ballast: 100 Hz buzz with odd/even grit and a thin hiss."""
    t = taxis(n)
    b = np.tanh(3.2 * np.sin(TWO_PI * 100 * t)) + 0.35 * np.tanh(5 * np.sin(TWO_PI * 200 * t + 0.9))
    b = bp(b, 95, 5000) * (1 + 0.12 * snoise(n, 5, seed))
    hiss = bp(white(n, seed + 1), 3500, 9000) * 0.05
    return (norm(b) + hiss) * level


def crt_whine(n, seed, f=15625.0):
    t = taxis(n)
    return (np.sin(TWO_PI * f * t + 0.3 * snoise(n, 2, seed)) * (1 + 0.15 * snoise(n, 3, seed + 1))).astype(np.float32)


# ====================================================================== 1. breaker trips
def breaker_trip():
    total = 3.4
    n = N(total)
    t = taxis(n)
    t0 = 0.62
    r = dsp.rng(10)
    on = (t < t0).astype(np.float32)
    # the bed before: fridge in the kitchen next door, the tube above the washtub, the CRT down the hall
    f = np.where(t < t0, FRIDGE_HZ, FRIDGE_HZ * np.exp(-np.maximum(0, t - t0) / 0.42))
    menv = np.where(t < t0, 1.0, np.exp(-np.maximum(0, t - t0) / 0.38)) * np.minimum(1, t / 0.2)
    motor = dsp.lowpass(fridge_motor(f, 11), 1400, 2) * menv * (f > 6)
    mains = np.sin(TWO_PI * 100 * t) + 0.3 * np.sin(TWO_PI * 200 * t)          # transformer / ballast core
    mains *= np.where(t < t0, 1.0, np.exp(-np.maximum(0, t - t0) / 0.012)) * np.minimum(1, t / 0.2)
    flick = np.exp(-0.5 * ((t - (t0 + 0.085)) / 0.012) ** 2) * 0.55              # the tube spits once more
    tube = tube_buzz(n, 12) * smooth(np.maximum(on, flick), 0.002) * np.minimum(1, t / 0.2)
    fw = np.where(t < t0, 15625.0, 15625.0 * np.exp(-np.maximum(0, t - t0) / 0.09))   # flyback collapses
    crt = np.sin(TWO_PI * np.cumsum(fw) / SR) * np.where(t < t0, 1.0, np.exp(-np.maximum(0, t - t0) / 0.12))
    crt *= (fw > 800)
    y = 0.13 * motor + 0.035 * mains + 0.1 * tube + 0.008 * crt * np.minimum(1, t / 0.2)
    out = np.zeros(n + N(0.4), np.float32)
    out[:n] = y
    # latch lets go (tick) -> arc across the opening contacts -> lever slams down: CLONK in the tin box
    add(out, knock(13, LEVER, 0.08, contact=0.0002, click=0.7), t0 - 0.007, 0.35)
    ns = N(0.045)
    lam = 5200 * np.exp(-taxis(ns) / 0.012)
    spk = crackle(ns, lam, 14, 1800, 12000, size=(0.0001, 0.0006))
    arc = np.tanh(4 * np.sin(TWO_PI * 100 * taxis(ns))) * np.exp(-taxis(ns) / 0.01)
    add(out, norm(spk) + 0.35 * norm(bp(arc, 150, 4000)), t0 - 0.002, 0.5)
    add(out, knock(15, BREAKER_BOX, 0.55, contact=0.0018, click=0.55), t0 + 0.005, 1.0)
    add(out, knock(16, LEVER, 0.12, contact=0.0004, click=0.4), t0 + 0.006, 0.45)
    ts = taxis(N(0.35))
    add(out, np.sin(TWO_PI * 660 * ts) * np.exp(-ts * 16) * np.minimum(1, ts / 0.001), t0 + 0.006, 0.05)  # spring
    tb = taxis(N(0.4))
    add(out, np.sin(TWO_PI * 118 * tb) * np.exp(-tb * 22) * np.minimum(1, tb / 0.002), t0 + 0.005, 0.35)  # wall
    # CRT down the hall: the screen charge lets go with a soft crackle and a 'thoom'
    nc = N(0.25)
    add(out, dsp.lowpass(crackle(nc, 900 * np.exp(-taxis(nc) / 0.05), 17, 1200, 7000), 3500, 2), t0 + 0.03, 0.05)
    tc = taxis(N(0.5))
    add(out, dsp.lowpass(np.sin(TWO_PI * 62 * tc) * np.exp(-tc * 9), 300, 2), t0 + 0.02, 0.06)
    # the compressor stalls against its own pressure and shudders on its rubber mounts
    tcl = t0 + 1.02
    add(out, knock(18, [(70, 18, 1.0), (125, 24, 0.8), (210, 30, 0.5), (390, 45, 0.3)], 0.45, contact=0.006,
                   click=0.0), tcl, 0.38)
    for k in range(4):
        add(out, knock(19 + k, [(1350, 60, 1), (2450, 80, .6), (3800, 110, .3)], 0.08, contact=0.0005, click=0.2),
            tcl + 0.03 + 0.045 * k + r.uniform(0, 0.01), 0.07 * 0.6 ** k)
    # cooling ticks in the dark
    for k, tt in enumerate([1.95, 2.55, 3.05]):
        add(out, glass_ping(30 + k, r.uniform(3800, 6000), 300, 1.0, 0.6), tt, 0.035)
    return verb(out, 'lavadero', wet=0.22)


# ====================================================================== 2. breaker reset
def breaker_reset():
    total = 4.6
    n = N(total)
    t = taxis(n)
    t0 = 0.32
    r = dsp.rng(40)
    out = np.zeros(n + N(0.4), np.float32)
    # the lever scraped up through its detent, KA- (latch catches) -CHUNK (contacts home) + a little spark
    add(out, creak(0.07, 41, [(0, 260), (0.07, 420)], LEVER, [(0, 0.3), (0.05, 1), (0.07, 0.5)]), t0 - 0.09, 0.12)
    add(out, knock(42, LEVER, 0.1, contact=0.0003, click=0.6), t0 - 0.012, 0.4)
    add(out, knock(43, BREAKER_BOX, 0.55, contact=0.0022, click=0.5), t0 + 0.03, 1.0)
    add(out, knock(44, LEVER, 0.12, contact=0.0004, click=0.4), t0 + 0.031, 0.4)
    tb = taxis(N(0.4))
    add(out, np.sin(TWO_PI * 112 * tb) * np.exp(-tb * 24) * np.minimum(1, tb / 0.002), t0 + 0.03, 0.3)
    ns = N(0.02)
    add(out, norm(crackle(ns, 4000 * np.exp(-taxis(ns) / 0.006), 45, 2000, 12000, size=(0.0001, 0.0005))),
        t0 + 0.029, 0.3)
    ton = t0 + 0.035
    on = smoothstep((t - ton) / 0.004)
    fade_out = env_pts(n, [(0, 1), (total - 1.4, 1), (total, 0)])
    # transformer: magnetising inrush thump then the steady 100 Hz
    mains = (np.sin(TWO_PI * 100 * t) + 0.3 * np.sin(TWO_PI * 200 * t)) * on
    tin = np.maximum(0, t - ton)
    inrush = np.sin(TWO_PI * 50 * t) * np.exp(-tin / 0.06) * on
    # fluorescent: starter ticks, two failed flashes, then it catches and warms up
    fl = np.zeros(n, np.float32)
    for a, b, g in [(t0 + 0.42, t0 + 0.5, 0.55), (t0 + 0.72, t0 + 0.78, 0.4), (t0 + 1.02, total, 1.0)]:
        fl += g * smoothstep((t - a) / 0.004) * (1 - smoothstep((t - b) / 0.004))
    warm = np.where(t > t0 + 1.02, 0.65 + 0.35 * np.minimum(1, (t - t0 - 1.02) / 0.6), 1.0)
    tube = tube_buzz(n, 46) * smooth(fl, 0.002) * warm
    for k, tt in enumerate([t0 + 0.4, t0 + 0.7, t0 + 1.0]):   # glow starter bimetal ticking
        add(out, knock(47 + k, [(2600, 90, 1), (4300, 120, .7), (6100, 160, .4)], 0.06, contact=0.0002, click=0.6),
            tt, 0.12)
    for k, tt in enumerate([t0 + 0.42, t0 + 0.72, t0 + 1.02]):  # tube ends ping as they heat
        add(out, glass_ping(50 + k, r.uniform(4200, 6200), 220, 1.0, 0.3), tt + 0.01, 0.05)
    # fridge: relay clack, the compressor heaves itself up to speed (groan), then settles
    tf = t0 + 0.62
    add(out, knock(55, [(1800, 70, 1), (3300, 90, .6)], 0.06, contact=0.0003, click=0.5), tf - 0.03, 0.12)
    add(out, knock(56, [(70, 18, 1.0), (125, 24, 0.8), (210, 30, 0.5), (390, 45, 0.3)], 0.45, contact=0.008,
                   click=0.0), tf, 0.4)
    ramp = smoothstep((t - tf) / 0.32)
    f = np.maximum(1.0, FRIDGE_HZ * ramp)
    motor = dsp.lowpass(fridge_motor(f, 57, rattle=0.5), 1400, 2) * np.minimum(1, ramp * 3) * (t > tf)
    groan = 1 + 0.6 * np.exp(-np.maximum(0, t - tf) / 0.25) * (t > tf)
    # the living-room TV degausses: relay tuk + the coil's 50 Hz shaking the mask and chassis - BWOMMM (far, LP)
    td = t0 + 0.18
    tdd = np.maximum(0, t - td)
    deg = (np.tanh(2.5 * np.sin(TWO_PI * 50 * t)) + 0.4 * np.sin(TWO_PI * 150 * t + 1) + 0.25 * np.sin(TWO_PI * 250 * t))
    deg = dsp.lowpass(deg * (1 + 0.3 * snoise(n, 30, 58)), 1500, 2) * np.exp(-tdd / 0.45) * smoothstep(tdd / 0.03) * (t > td)
    add(out, dsp.lowpass(knock(59, [(900, 60, 1), (1700, 80, .6)], 0.06, contact=0.0004, click=0.2), 3000, 2), td - 0.01, 0.06)
    whine = crt_whine(n, 60) * smoothstep((t - td - 0.4) / 0.6)
    bed = (0.04 * mains + 0.12 * inrush + 0.3 * tube + 0.15 * motor * groan + 0.2 * deg + 0.01 * whine) * fade_out
    out[:n] += bed.astype(np.float32)
    return verb(out, 'lavadero', wet=0.2)


# ====================================================================== 3. the telenovela (loop)
NOVELA = [  # (voice, speed, text, semitones, style, gap_before)
    ('em_alex', 1.0, '¡Mentira! Vos nunca me quisiste, Mercedes.', -1.0, 'shout', 0.35),
    ('ef_dora', 1.05, '¡Ese hijo no es tuyo, Rodolfo!', 1.0, 'shout', 0.3),
    ('STING1', 0, '', 0, '', 0.15),
    ('em_alex', 0.85, '¿Qué...? ¿Qué estás diciendo?', -1.5, 'stunned', 0.2),
    ('ef_dora', 0.9, 'Perdoname... no te lo podía decir.', 0.5, 'sob', 0.35),
    ('ef_dora', 1.0, '¿Mamá? ¿Es verdad?', 4.0, 'girl', 0.4),
    ('ef_dora', 1.1, '¡Andate de esta casa!', 0.0, 'shout', 0.25),
    ('STING2', 0, '', 0, '', 0.1),
]


def novela_line(voice, speed, text, semis, style, seed):
    x = dsp.tts(text, voice, speed)
    x = dsp.trim(x, -45, 0.04)
    if semis:
        x = dsp.pitch_shift(x, semis)
    if style == 'shout':
        x = dsp.peak(x, 2600, 5, 1.2)
        x = dsp.drive(norm(x) * 2.2, 2.4)
    elif style == 'sob':   # tremulous, crying voice: 5.5 Hz varispeed wobble + breath on the phrase
        n = len(x) - N(0.05)
        rate = 1 + 0.035 * np.sin(TWO_PI * 5.3 * taxis(n)) + 0.01 * snoise(n, 8, seed)
        x = varispeed(x, rate, n)
        x *= 1 + 0.25 * np.sin(TWO_PI * 5.3 * taxis(len(x)) + 1.0)
        env = smooth(np.abs(x), 0.03)
        x = x + 0.12 * norm(bp(white(len(x), seed), 1500, 7000)) * env / (env.max() + 1e-9)
    elif style == 'girl':
        x = dsp.peak(x, 3200, 3, 1.5)
    return norm(x)


def string_chord(midis, dur, seed, att=0.12, rel=0.4, trem=0.0, vib=0.006, voices=3, amp=1.0, bow=0.04):
    """A small string section: per note `voices` detuned polyBLEP saws with own vibrato, bow noise, body EQ."""
    r = dsp.rng(seed)
    n = N(dur + rel)
    t = taxis(n)
    env = env_pts(n, [(0, 0), (att, 1.0), (dur, 0.85), (dur + rel, 0)]) ** 1.3
    y = np.zeros(n, np.float32)
    for m in midis:
        for v in range(voices):
            f0 = mtof(m) * (1 + r.uniform(-0.004, 0.004))
            rate = r.uniform(4.8, 6.3)
            dep = vib * r.uniform(0.6, 1.2) * smoothstep(t / 0.35)
            f = f0 * (1 + dep * np.sin(TWO_PI * rate * t + r.uniform(0, 6)))
            y += saw_blep(f, n) * (1 + 0.04 * snoise(n, 12, seed + 7 * v + m))
    y = y / (len(midis) * voices) ** 0.5
    if trem:   # bowed tremolo: fast unsynchronised strokes
        stroke = 0.55 + 0.45 * np.abs(np.sin(np.pi * trem * t + 2 * snoise(n, 3, seed + 99)))
        y *= stroke
    y += bow * norm(bp(white(n, seed + 5), 2500, 7000)) * (1 + 3 * np.exp(-t / 0.05))
    for fpk, g, q in [(290, 4, 2), (520, 3, 2), (1050, 2.5, 1.5), (2600, 5, 1.2)]:
        y = dsp.peak(y, fpk, g, q)
    y = dsp.lowpass(y, 7000, 2)
    return (y * env * amp).astype(np.float32)


def timpani(f0, seed, amp=1.0, dur=1.6):
    r = dsp.rng(seed)
    modes = [(f0 * k, d, a) for k, d, a in [(1.0, 3.5, 1.0), (1.5, 4.5, 0.6), (1.98, 5, 0.45), (2.44, 6, 0.3), (2.9, 8, 0.2)]]
    y = knock(seed, modes, dur, contact=0.006, click=0.15, click_hp=600, amt=0.01)
    felt = dsp.lowpass(burst(0.03, seed + 1, 1.5), 700, 2)       # felt mallet on the calfskin
    y[:len(felt)] += 0.25 * r.uniform(0.8, 1.0) * norm(felt)
    return y * amp


def sting1():
    """TAN - TAN - TAAAN: two stabs and a long tremolo chord over a timpani hit."""
    out = np.zeros(N(4.2), np.float32)
    add(out, string_chord([62, 65, 69, 74], 0.14, 301, att=0.01, rel=0.12, voices=3, bow=0.08), 0.0, 0.9)
    add(out, string_chord([62, 65, 69, 74], 0.14, 302, att=0.01, rel=0.12, voices=3, bow=0.08), 0.3, 0.9)
    add(out, string_chord([58, 62, 65, 70, 74, 77], 2.4, 303, att=0.02, rel=1.2, trem=13, voices=3, bow=0.06), 0.62, 1.1)
    add(out, string_chord([38, 50], 2.4, 304, att=0.02, rel=1.2, voices=2), 0.62, 0.7)
    add(out, timpani(73.4, 305, 1.0), 0.0, 0.5)
    add(out, timpani(73.4, 306, 1.0), 0.3, 0.5)
    add(out, timpani(58.3, 307, 1.4, 2.2), 0.62, 0.9)
    return out


def sting2():
    """Rising tremolo on a diminished chord, then the big minor TAAAN with a timpani roll."""
    out = np.zeros(N(5.5), np.float32)
    rise = string_chord([62, 65, 68, 71], 1.15, 311, att=1.1, rel=0.03, trem=14, voices=3, bow=0.05)
    rise *= np.linspace(0.3, 1.0, len(rise)) ** 1.5
    add(out, rise, 0.0, 0.8)
    for k in range(14):   # timpani roll under the rise
        add(out, timpani(73.4, 320 + k, 0.25 + 0.55 * k / 13, 0.6), 0.08 * k, 0.5)
    add(out, string_chord([50, 57, 62, 65, 69, 74, 77], 2.8, 312, att=0.015, rel=1.4, vib=0.008, voices=3, bow=0.07),
        1.15, 1.25)
    add(out, string_chord([38], 2.8, 313, att=0.015, rel=1.4, voices=3), 1.15, 0.8)
    add(out, timpani(73.4, 314, 1.6, 2.4), 1.15, 1.1)
    return out


def tv_speaker(x, level=1.0):
    """A tired 1980s CRT set at full volume: small oval cone, cabinet rattle, a crunchy output stage."""
    y = bp(x, 170, 5200, 2)
    y = dsp.peak(y, 950, 4.5, 1.4)
    y = dsp.peak(y, 2900, 3.5, 2.0)
    y = dsp.peak(y, 240, 3, 2.5)        # cabinet box resonance
    y = dsp.drive(y * 1.7 * level, 1.9)
    return dsp.lowpass(y, 4800, 4)


def tv_novela():
    L = N(20.0)
    buf = np.zeros(L + N(6.0), np.float32)
    dlg = np.zeros_like(buf)
    t = 0.0
    for k, (voice, speed, text, semis, style, gap) in enumerate(NOVELA):
        t += gap
        if voice == 'STING1':
            add(buf, sting1(), t, 0.85)
            t += 1.6
            continue
        if voice == 'STING2':
            add(buf, sting2(), t, 0.95)
            continue
        x = novela_line(voice, speed, text, semis, style, 400 + k)
        add(dlg, x, t, 1.0 if style != 'stunned' else 0.85)
        t += len(x) / SR
    assert t < 17.0, f'novela script too long ({t:.1f}s)'
    # the underscore: low strings slowly breathing through Dm - Bb - Gm - A, four 5 s chords round the loop
    pad = np.zeros_like(buf)
    for i, ch in enumerate([[50, 57, 65], [46, 53, 62], [43, 50, 58], [45, 52, 61]]):
        add(pad, string_chord(ch, 5.0, 330 + i, att=0.9, rel=0.9, vib=0.005, voices=2, bow=0.01), 5.0 * i - 0.45, 1.0)
    # balance like a broadcast mix: dialogue up front, underscore ~-15 dB, stings as loud as the shouting
    act = smooth(np.abs(dlg), 0.05) > 0.03 * np.max(np.abs(dlg))
    d_rms = rms(dlg[act])
    pad *= 0.18 * d_rms / rms(pad)
    s_act = smooth(np.abs(buf), 0.05) > 0.05 * np.max(np.abs(buf))
    buf *= 0.9 * d_rms / rms(buf[s_act])
    sig = norm(fold(buf + dlg + pad, L))
    sig = loop_iir(sig, lambda z: tv_speaker(z, 0.85))
    n = L
    tt = taxis(n)
    buzz = loop_iir(np.tanh(6 * np.sin(TWO_PI * 50 * tt)).astype(np.float32), lambda z: bp(z, 45, 900))
    hiss = cfilt(white(n, 340), lambda f: hp2(f, 2500) * lp2(f, 7000))
    whine = np.sin(TWO_PI * 15625.0 * tt).astype(np.float32)
    y = norm(sig) + 0.02 * norm(buzz) + 0.006 * norm(hiss) + 0.01 * whine
    return verb(y, 'living', wet=0.28, circular=True)


# ====================================================================== 4. TV static (loop)
def tv_static():
    L = N(8.0)
    tt = taxis(L)
    r = dsp.rng(350)
    snow = cfilt(white(L, 351), lambda f: hp2(f, 160) * lp2(f, 6200) * (1 + bump(f, 1000, 0.7, 0.6) + bump(f, 3000, 0.5, 0.9)))
    snow *= (1 + 0.12 * csnoise(L, 3, 352)) * (0.75 + 0.25 * cgrain(L, 90, 353, 1.0))
    # vertical sync buzz bleeding into the audio: 50 Hz narrow pulses (400 whole cycles in 8 s)
    pulse = (np.sin(TWO_PI * 50 * tt) > 0.93).astype(np.float32)
    buzz = cfilt(pulse, lambda f: hp2(f, 60) * lp2(f, 2500))
    # screen-charge crackle: a few sharp pops wrapping round the loop
    pops = np.zeros(L + N(0.05), np.float32)
    for k in range(int(r.poisson(9))):
        add(pops, burst(r.uniform(0.0008, 0.003), 360 + k, 2.0) * r.uniform(0.3, 1.0), r.uniform(0, 8.0))
    pops = cfilt(fold(pops, L), lambda f: hp2(f, 1200))
    whine = np.sin(TWO_PI * 15625.0 * tt + 0.15 * csnoise(L, 1.5, 361)).astype(np.float32)
    y = norm(snow) + 0.09 * norm(buzz) + 0.35 * norm(pops) + 0.05 * whine
    y = loop_iir(y, lambda z: dsp.drive(z * 1.2, 1.3))
    return verb(y, 'living', wet=0.12, circular=True)


# ====================================================================== 5. grill sizzle (loop)
def grill_sizzle():
    L = N(5.0)
    r = dsp.rng(500)
    swell = 1 + 0.35 * csnoise(L, 0.7, 501)
    # fat film frying: dense hiss with a crisp micro-texture
    hiss = cfilt(white(L, 502), lambda f: hp2(f, 1700) * lp2(f, 11000) * (1 + bump(f, 5200, 0.6, 0.8)))
    hiss *= cgrain(L, 260, 503, 2.2) * swell
    # droplets of fat bursting: Poisson ticks, heavy-tailed amplitudes, wrapped round the loop
    pad = N(0.1)
    ticks = np.zeros(L + pad, np.float32)
    idx = np.nonzero(r.random(L) < 160 * swell / SR)[0]
    for i in idx:
        d = max(4, N(r.uniform(0.0002, 0.0015)))
        a = min(4.0, r.pareto(2.0) + 0.1)
        ticks[i:i + d] += a * r.standard_normal(d) * np.exp(-np.arange(d) / (d / 3))
    ticks = cfilt(fold(ticks, L), lambda f: hp2(f, 2200) * lp2(f, 12000))
    # bigger spits: a drop lands on a coal, 'pssht' + tiny thup
    spits = np.zeros(L + N(0.3), np.float32)
    for k in range(13):
        tk = r.uniform(0, 5.0)
        d = r.uniform(0.03, 0.09)
        sp = dsp.lowpass(bp(white(N(d), 510 + k), 1200, 9000), 6000, 2) * np.exp(-taxis(N(d)) / (d / 3))
        add(spits, sp, tk, r.uniform(0.3, 1.0))
        add(spits, np.sin(TWO_PI * r.uniform(280, 520) * taxis(N(0.015))) * np.exp(-taxis(N(0.015)) / 0.004), tk, 0.25)
    spits = fold(spits, L)
    # charcoal ticking (lower, woody) and the low breath of the fire
    embers = np.zeros(L + pad, np.float32)
    for k in range(int(r.poisson(45))):
        add(embers, knock(530 + k, [(r.uniform(900, 2400), 120, 1), (r.uniform(2600, 4200), 160, .5)], 0.02,
                          contact=0.0002, click=0.5), r.uniform(0, 5.0), r.uniform(0.05, 0.3))
    embers = fold(embers, L)
    roar = cfilt(white(L, 520), lambda f: hp2(f, 60) * lp2(f, 380)) * (1 + 0.4 * csnoise(L, 4, 521))
    y = 0.5 * norm(hiss) + 0.55 * norm(ticks) + 0.4 * norm(spits) + 0.22 * norm(embers) + 0.16 * norm(roar)
    return verb(y, 'patio', wet=0.12, circular=True)


# ====================================================================== 6. blue fire whoosh
def fire_blue_whoosh():
    total = 4.8
    n = N(total)
    t = taxis(n)
    ti = 0.3
    out = np.zeros(n + N(0.6), np.float32)
    # the air is sucked towards the grill
    suck_env = env_pts(n, [(0, 0), (ti - 0.02, 1.0), (ti, 0)]) ** 2.5
    suck = tv_filter(colored(n, 'pink', 601), 'bp', 300 + 2600 * (t / ti), bw_oct=1.4) * suck_env
    out[:n] += 0.35 * norm(suck)
    # FWOOMP: pressure thump + the flame front ripping through the air + a crackle burst
    tb = taxis(N(0.9))
    thump = np.sin(TWO_PI * np.cumsum(38 + 60 * np.exp(-tb / 0.06)) / SR) * np.exp(-tb * 5.5) * np.minimum(1, tb / 0.004)
    add(out, thump, ti, 0.9)
    nw = N(1.6)
    tw = taxis(nw)
    whoosh = tv_filter(colored(nw, 'pink', 602), 'lp', 600 + 7000 * np.exp(-tw / 0.18) + 900 * np.exp(-tw / 0.8))
    whoosh *= np.minimum(1, tw / 0.025) * np.exp(-tw / 0.45)
    add(out, norm(whoosh), ti, 0.85)
    ncr = N(0.6)
    add(out, norm(crackle(ncr, 3000 * np.exp(-taxis(ncr) / 0.12), 603, 1500, 10000)), ti + 0.01, 0.35)
    # the blue gas jet: a smooth, pressured hiss with a faint whistle - premixed flame, not wood
    tj = np.maximum(0, t - ti)
    jet_env = smoothstep(tj / 0.12) * env_pts(n, [(0, 1), (ti + 1.2, 1), (ti + 2.4, 0.2), (total, 0)])
    jet = bp(white(n, 604), 1800, 9000) + 0.15 * np.sin(TWO_PI * 3150 * t) * (1 + 0.3 * snoise(n, 4, 605))
    out[:n] += 0.16 * norm(jet) * jet_env
    # ... and then it goes wrong: the roar slows like a tape running down, resonances gliding into a low groan
    src_n = N(4.0)
    roar = dsp.lowpass(colored(src_n, 'pink', 606), 1400, 2) * (1 + 0.55 * snoise(src_n, 9, 607))
    rate = 1.0 - 0.72 * smoothstep(taxis(src_n) / 2.6)
    slow = varispeed(roar, rate, src_n)
    groan_f = 260 * np.exp(-1.3 * smoothstep(taxis(src_n) / 2.4)) + 40
    groan = tv_filter(slow, 'bp', groan_f, bw_oct=0.35) + 0.6 * tv_filter(slow, 'bp', groan_f * 1.5, bw_oct=0.35)
    genv = env_pts(src_n, [(0, 0), (0.25, 0.4), (0.9, 1.0), (2.6, 0.9), (4.0, 0)])
    add(out, norm(0.6 * slow + groan) * genv, ti + 0.15, 0.55)
    # the demon breathes through the flames: huge-throat 'oh' turbulence and a rough sub voice under it
    nb = N(3.2)
    fr = ftrack(nb, [(0, vowel('o', 0.62)), (1.6, vowel('u', 0.6)), (3.2, vowel('o', 0.6))])
    breath = shaped_noise(fr, nb, 608, lp=2500) * env_pts(nb, [(0, 0), (0.8, 0.6), (1.6, 1.0), (2.6, 0.7), (3.2, 0)])
    add(out, norm(breath), ti + 0.8, 0.22)
    f0 = contour(nb, [(0, 58), (1.4, 46), (3.2, 38)])
    amp = env_pts(nb, [(0, 0), (1.0, 0.5), (1.8, 1.0), (2.8, 0.6), (3.2, 0)])
    growl = vsynth(f0, fr, amp, tilt=1.0, rough=1.0, rough_hz=45, sub=0.6, breath=0.3, fmax=3000, seed=609)
    add(out, norm(dsp.lowpass(growl, 1800, 2)), ti + 0.8, 0.22)
    sub = (np.sin(TWO_PI * 36 * t) + 0.5 * np.sin(TWO_PI * 54.3 * t)) * env_pts(n, [(0, 0), (ti + 0.6, 0), (ti + 1.9, 1.0), (total - 0.4, 0.3), (total, 0)])
    out[:n] += 0.14 * sub.astype(np.float32)
    return verb(out, 'patio', wet=0.2)


# ====================================================================== 7. knives off the rack
BLADE = [(1210, 7, 0.5), (2680, 9, 1.0), (4150, 12, 0.8), (5930, 15, 0.6), (7720, 20, 0.45), (9850, 26, 0.3),
         (12100, 32, 0.15)]   # free-free modes of a 20 cm kitchen blade
WOOD_BLOCK = [(380, 60, 1.0), (720, 70, 0.7), (1250, 90, 0.45), (2100, 120, 0.25)]   # the rack's wooden slots


def blade_modes(r, scale):
    return [(f * scale * r.uniform(.97, 1.03), d * r.uniform(.8, 1.2), a * r.uniform(.7, 1)) for f, d, a in BLADE]


def blade_draw(seed, scale, slide=0.25, ring=1.3, rot_hz=2.2):
    """One knife drawn out of its wooden slot: wood scrape, the steel singing while dragged, the tip's 'shing'."""
    r = dsp.rng(seed)
    ns = N(slide)
    ts = taxis(ns)
    pos = smoothstep(ts / slide)
    exc = white(ns, seed) * grain(ns, 350, seed + 1, 1.6)
    exc *= env_pts(ns, [(0, 0), (0.012, 0.7), (slide * 0.6, 1.0), (slide * 0.92, 0.85), (slide, 0)])
    modes = blade_modes(r, scale)
    shing = excite(tv_filter(exc, 'bp', (2000 + 5200 * pos) * scale, bw_oct=1.2), modes, ring, seed)
    tip = knock(seed + 3, modes, ring, contact=0.00015, click=0.25)
    wood = excite(dsp.lowpass(exc, 2600, 2), WOOD_BLOCK, 0.1)
    # the 'zing': edge against the slot's steel guard, a narrow resonance sweeping up with the draw
    zing = tv_filter(white(ns, seed + 5) * grain(ns, 600, seed + 6, 1.2), 'bp', (2600 + 5400 * pos ** 1.4) * scale,
                     bw_oct=0.12) * env_pts(ns, [(0, 0), (slide * 0.3, 0.5), (slide * 0.9, 1.0), (slide, 0)])
    out = np.zeros(ns + N(ring) + N(0.05), np.float32)
    add(out, norm(shing), 0.0, 1.0)
    add(out, norm(zing), 0.0, 0.45)
    add(out, tip, slide * 0.96, 0.45)
    add(out, norm(wood), 0.0, 0.3)
    add(out, knock(seed + 4, WOOD_BLOCK, 0.08, contact=0.0008, click=0.3), 0.0, 0.25)   # handle knocks the block
    # in the air, the blade turns slowly: its ring swings in and out of your ear
    t = taxis(len(out))
    out *= 1 + 0.45 * np.sin(TWO_PI * rot_hz * t + r.uniform(0, 6)) * smoothstep((t - slide) / 0.25)
    return out


def knife_lift(v):
    r = dsp.rng(650 + v)
    out = np.zeros(N(2.6), np.float32)
    if v == 1:   # three knives, one after the other: shk-shiing, shk-shiing, shiiing
        for k, (tk, sc, sl) in enumerate([(0.0, 1.0, 0.22), (0.17, 0.86, 0.2), (0.33, 1.17, 0.26)]):
            add(out, blade_draw(660 + k, sc, sl, 1.4, r.uniform(1.6, 2.8)), tk, [1.0, 0.85, 0.95][k])
    else:        # three at once, dragged slower; they touch (tink, tink) and start to sing on their own
        for k, (tk, sc) in enumerate([(0.0, 0.93), (0.045, 1.08), (0.085, 1.24)]):
            add(out, blade_draw(670 + k, sc, 0.36, 1.5, r.uniform(1.4, 2.4)), tk, 0.8)
        for k, tk in enumerate([0.72, 0.86, 0.93]):
            add(out, knock(680 + k, blade_modes(r, r.uniform(0.95, 1.2)), 0.9, contact=0.00012, click=0.4), tk,
                [0.35, 0.22, 0.15][k])
        nb = N(1.6)
        tb = taxis(nb)
        bow = bp(white(nb, 685), 1500, 9000) * env_pts(nb, [(0, 0), (0.7, 0.6), (1.2, 1.0), (1.6, 0)])
        sing = excite(bow * (1 + 0.5 * np.sin(TWO_PI * 5.5 * tb)), blade_modes(r, 1.08), 0.6, 686)
        add(out, norm(sing), 0.55, 0.22)
    return verb(out, 'patio', wet=0.1)


# ====================================================================== 8. knife whoosh (fly-by)
def knife_whoosh(v):
    rot, speed, dmin, dur, tc = {1: (11.0, 16.0, 0.6, 1.0, 0.5), 2: (16.0, 19.0, 0.4, 0.9, 0.42),
                                 3: (8.0, 13.0, 0.9, 1.15, 0.58)}[v]
    seed = 700 + 10 * v
    n = N(dur)
    t = taxis(n)
    ph = TWO_PI * rot * t + v
    blade = np.abs(np.sin(ph)) ** 8           # the flat of the blade slaps the air twice per turn
    handle = np.abs(np.sin(ph + 0.7)) ** 3     # the heavier handle: a lower 'vvvp'
    edge = bp(white(n, seed), 1400, 8000) * (0.15 + blade)
    body = bp(white(n, seed + 1), 220, 1900) * (0.3 + handle)
    whistle = np.sin(TWO_PI * np.cumsum(3300 * (1 + 0.04 * snoise(n, 6, seed + 2))) / SR) * blade ** 2
    src = 0.8 * norm(edge) + 0.75 * norm(body) + 0.12 * whistle
    y = flyby(src.astype(np.float32), tc, speed, dmin, buffet=0.35, seed=seed)
    return verb(y, 'patio', wet=0.1)


# ====================================================================== 9. knife into wood
KNIFE_TARGETS = {
    1: [(115, 28, .8), (185, 32, 1.0), (300, 38, .8), (470, 46, .6), (720, 55, .45), (1050, 70, .3), (1600, 95, .18)],
    2: [(88, 22, 1.0), (150, 26, .9), (262, 32, .7), (415, 40, .5), (640, 50, .35), (980, 65, .22)],
    3: [(160, 60, 1.0), (330, 70, .7), (620, 85, .45), (1100, 110, .25), (1900, 140, .12)],
}   # 1 fence plank, 2 the long patio table, 3 the lemon tree (dull, wet wood)


def knife_impact(v):
    r = dsp.rng(740 + v)
    n = N(1.35)
    out = np.zeros(n, np.float32)
    nc = N(0.012)
    add(out, norm(crackle(nc, 9000 * np.exp(-taxis(nc) / 0.004), 741 + v, 1200, 10000, size=(0.0001, 0.0005))), 0, 0.55)
    add(out, knock(742 + v, KNIFE_TARGETS[v], 0.6, contact=0.0011, click=0.55), 0.001, 1.0)
    tb = taxis(N(0.4))
    add(out, np.sin(TWO_PI * [0, 98, 80, 120][v] * tb) * np.exp(-tb * 26) * np.minimum(1, tb / 0.002), 0.001, 0.5)
    # the blade quivering, clamped in the wood: a damped ring swung by the cantilever wobble, and the bending
    # mode 'vrrroonng' that a stuck knife makes
    fc = {1: 24.0, 2: 31.0, 3: 19.0}[v]
    nr = N(1.2)
    tr = taxis(nr)
    ring = modal_ir([(f, d * 2.2, a) for f, d, a in blade_modes(r, 1.05)], 1.2, 743 + v)
    wob = 0.5 + 0.5 * np.cos(TWO_PI * fc * tr)
    ring = ring * (0.3 + 0.7 * wob) * np.exp(-tr * 4.5)
    fb = {1: 205.0, 2: 238.0, 3: 172.0}[v]
    bend = np.sin(TWO_PI * fb * tr * (1 + 0.01 * np.exp(-tr * 8))) * (0.4 + 0.6 * wob) * np.exp(-tr * 6) * np.minimum(1, tr / 0.003)
    add(out, norm(ring), 0.002, 0.2 if v != 3 else 0.12)
    add(out, bend, 0.002, 0.16 if v != 3 else 0.1)
    for k in range(int(r.integers(3, 6))):   # splinters
        add(out, knock(750 + 10 * v + k, [(r.uniform(1800, 4200), 200, 1)], 0.02, contact=0.0002, click=0.6),
            r.uniform(0.008, 0.12), r.uniform(0.04, 0.12))
    return verb(out, 'patio', wet=0.13)


# ====================================================================== 10. salt + demon yelp
def salt_hit_scream():
    n = N(2.4)
    out = np.zeros(n + N(0.6), np.float32)
    r = dsp.rng(800)
    # a fistful of coarse salt: ~450 grains hitting skin within ~70 ms (soft target: no ring, just crisp ticks)
    times = 0.004 + r.gamma(1.6, 0.018, 450)
    idx = np.clip((times * SR).astype(int), 0, n - 1)
    amps = np.minimum(4.0, r.pareto(2.4, len(idx)) + 0.1).astype(np.float32)
    grains = pulse_train(n, idx, amps, burst(0.0004, 801, 1.5))
    out[:n] += 0.5 * norm(dsp.lowpass(dsp.highpass(grains, 2500, 2), 11000, 2))
    # the burn: acid hiss with crackle and a puff of steam
    nh = N(1.5)
    th = taxis(nh)
    henv = np.minimum(1, th / 0.03) * np.exp(-th / 0.45)
    hiss = bp(white(nh, 802), 2500, 10000) * grain(nh, 300, 803, 2.0) * henv
    crk = crackle(nh, 700 * np.exp(-th / 0.35), 804, 1800, 9000)
    steam = dsp.lowpass(bp(white(nh, 805), 600, 9000), 4500, 2) * np.minimum(1, th / 0.08) * np.exp(-th / 0.5)
    add(out, norm(hiss), 0.02, 0.3)
    add(out, norm(crk), 0.02, 0.22)
    add(out, norm(steam), 0.05, 0.15)
    # the yelp: Jorge's own throat with the demon an octave and a fifth under it, both torn
    nv = N(1.1)
    f_h = contour(nv, [(0, 250), (0.04, 560), (0.2, 520), (0.42, 400), (0.7, 240), (1.1, 150)])
    keys_h = [(0, vowel('a', 1.08)), (0.3, vowel('a', 1.05, name2='o', mix=0.3)), (0.8, vowel('o'))]
    amp_h = env_pts(nv, [(0, 0), (0.02, 1.0), (0.3, 0.9), (0.55, 0.5), (1.1, 0)])
    human = vsynth(f_h, ftrack(nv, keys_h), amp_h, tilt=0.75, rough=0.45, rough_hz=60, breath=0.18, fmax=8000,
                   seed=810)
    # the demon an octave and a fifth under it, a hair late, and staying on as a growl when Jorge's voice gives out
    amp_d = env_pts(nv, [(0, 0), (0.04, 0.8), (0.35, 0.9), (0.8, 0.7), (1.1, 0)])
    keys_d = [(0, vowel('a', 0.7)), (0.4, vowel('o', 0.68)), (1.1, vowel('u', 0.66))]
    demon = vsynth(f_h * 0.335, ftrack(nv, keys_d), amp_d, tilt=0.8, rough=1.0, rough_hz=45, sub=0.7, breath=0.3,
                   fmax=4500, seed=811)
    voice = dsp.drive(norm(human) + 0.5 * norm(demon), 1.6)
    add(out, voice, 0.07, 0.8)
    return verb(out, 'patio', wet=0.18)


# ====================================================================== 11. Jorge into the pelopincho
PVC_FRAME = [(620, 30, 1.0), (1340, 40, 0.7), (2280, 55, 0.45), (3500, 70, 0.25)]


def pool_splash():
    total = 4.0
    n = N(total)
    r = dsp.rng(900)
    out = np.zeros(n + N(0.6), np.float32)
    ti = 0.14
    nf = N(ti)
    add(out, bp(colored(nf, 'pink', 901), 150, 1500) * (taxis(nf) / ti) ** 2, 0.0, 0.12)   # falling like a sack
    # SLAP: a lot of belly on a flat water surface
    add(out, norm(bp(burst(0.014, 902, 1.5), 250, 9000)), ti, 0.85)
    add(out, norm(dsp.highpass(burst(0.002, 903, 2.0), 2500, 2)), ti, 0.4)
    tb = taxis(N(0.6))
    add(out, np.sin(TWO_PI * np.cumsum(42 + 40 * np.exp(-tb / 0.04)) / SR) * np.exp(-tb * 9) * np.minimum(1, tb / 0.003), ti, 0.9)
    # the plunge: water thrown up, the air cavity roaring shut
    npl = N(0.9)
    tp = taxis(npl)
    plunge = tv_filter(colored(npl, 'pink', 904), 'lp', 1100 + 8000 * np.exp(-tp / 0.16)) * np.minimum(1, tp / 0.004) * np.exp(-tp / 0.34)
    plunge *= 1 + 0.5 * snoise(npl, 25, 9041)
    add(out, norm(plunge), ti, 1.0)
    churn = bp(white(npl, 9042), 250, 2500) * grain(npl, 40, 9043, 2.0) * np.minimum(1, tp / 0.05) * np.exp(-tp / 0.3)
    add(out, norm(churn), ti + 0.05, 0.45)
    for k, (f0, dt, a) in enumerate([(92, 0.1, 1.0), (148, 0.13, 0.7), (225, 0.17, 0.55), (340, 0.21, 0.4)]):
        add(out, bubble(f0, 905 + k, 1.0, a, 0.35), ti + dt, 0.55)
    for k in range(30):
        add(out, bubble(r.uniform(300, 1200), 910 + k, r.uniform(0.3, 1.2), r.uniform(0.2, 0.7)), ti + r.uniform(0.12, 0.6), 0.25)
    # spray raining back on the water
    tt = taxis(n)
    u = np.maximum(0, tt - ti - 0.12)
    lam = 1100 * (u / 0.33) * np.exp(1 - u / 0.33) * (tt > ti + 0.12)
    idx = poisson_times(lam, 950)
    amps = (r.uniform(0.1, 1.0, len(idx)) ** 2).astype(np.float32)
    drops = pulse_train(n, idx, amps, burst(0.0007, 951, 1.5))
    out[:n] += 0.45 * norm(bp(drops, 1500, 9500))
    for k, i in enumerate(idx[::4][:400]):
        add(out, bubble(r.uniform(1000, 4500), 1000 + k, r.uniform(0.2, 0.6), r.uniform(0.05, 0.4)), i / SR, 0.15)
    # the PVC walls bulge (bwomp) and the steel frame creaks
    tw = taxis(N(0.8))
    add(out, np.sin(TWO_PI * 64 * (1 - 0.08 * tw) * tw) * np.exp(-tw * 7) * np.minimum(1, tw / 0.01), ti + 0.16, 0.45)
    add(out, norm(creak(0.3, 960, [(0, 520), (0.3, 360)], PVC_FRAME, [(0, 0), (0.05, 1), (0.25, 0.6), (0.3, 0)])), ti + 0.33, 0.1)
    # slosh: the water rocking against the walls (~1.35 Hz) and calming down
    ns = N(3.3)
    tsl = taxis(ns)
    rock = (0.5 + 0.5 * np.sin(TWO_PI * 1.35 * tsl - 1.2)) ** 3
    slosh = bp(white(ns, 961), 120, 1500) * grain(ns, 30, 962, 2.0) * rock * np.exp(-tsl / 1.3) * smoothstep(tsl / 0.3)
    add(out, norm(slosh), ti + 0.35, 0.32)
    for k in range(5):
        add(out, bubble(r.uniform(180, 420), 970 + k, 0.8, 0.5, 0.5), ti + 0.35 + (k + 0.6) / 1.35 + r.uniform(-0.05, 0.05), 0.2 * 0.75 ** k)
    # overflow slapping onto the patio bricks
    no = N(1.0)
    over = bp(white(no, 980), 1200, 8000) * grain(no, 80, 981, 2.0) * env_pts(no, [(0, 0), (0.05, 1), (0.5, 0.6), (1.0, 0)])
    add(out, norm(over), ti + 0.55, 0.14)
    return verb(out, 'patio', wet=0.16)


# ====================================================================== 12. plates
PLATE = [(780, 30, 1.0), (1480, 34, 0.9), (2420, 40, 0.75), (3450, 48, 0.6), (4700, 55, 0.45), (6100, 65, 0.3),
         (7800, 80, 0.2)]   # a 25 cm china dinner plate
MUG = [(1050, 55, 1.0), (2300, 65, 0.7), (3900, 85, 0.5), (5600, 100, 0.3)]
CUTLERY = [(2400, 22, 1.0), (5300, 30, 0.6), (8200, 45, 0.3), (11500, 60, 0.15)]


def plate_spin_src(n, seed, spin, wobble, rim_f):
    """A china plate frisbeeing: steady rush made uneven by its decoration/chip and its precession, rim whistle."""
    t = taxis(n)
    ph = TWO_PI * spin * t
    asym = 1 + 0.45 * np.sin(ph) + 0.2 * np.sin(2 * ph + 1)
    wob = 1 + wobble * np.sin(TWO_PI * spin * 0.37 * t)
    air = bp(white(n, seed), 300, 6000) * asym * wob
    low = bp(white(n, seed + 1), 80, 700) * (1 + 0.6 * np.sin(ph + 0.5)) * wob
    rim = np.sin(TWO_PI * np.cumsum(rim_f * (1 + 0.02 * snoise(n, 5, seed + 2))) / SR) * (0.5 + 0.5 * np.sin(ph)) ** 2
    return (norm(air) + 0.8 * norm(low) + 0.12 * rim).astype(np.float32)


def plate_whoosh(v):
    spin, speed, dmin, wob, rim = {1: (9, 11, 0.35, 0.0, 1250), 2: (12, 13, 0.45, 0.3, 1480),
                                   3: (6.5, 9, 0.3, 0.7, 1120), 4: (14, 15, 0.55, 0.1, 1650)}[v]
    n = N(1.2)
    src = plate_spin_src(n, 1100 + 10 * v, spin, wob, rim)
    y = flyby(src, 0.6, speed, dmin, buffet=0.5, seed=1100 + v)
    return verb(y, 'living', wet=0.12)


def plate_break(out, seed, t0, amp=1.0, floor=False, pieces=40, fall=0.0, halves=False, modes=PLATE, crumbs=True):
    """One plate breaking at t0: a ring cut short by the fracture, a crack run, shards landing / bouncing / skittering."""
    r = dsp.rng(seed)
    hit = knock(seed, modes, 0.35, contact=0.0004, click=0.7, amt=0.06)
    hit *= np.exp(-taxis(len(hit)) / (0.06 if halves else 0.03))
    add(out, hit, t0, amp)
    add(out, norm(bp(burst(0.03, seed + 1, 1.5), 1500, 12000)), t0, amp * 0.75)
    if floor:
        tb = taxis(N(0.25))
        add(out, np.sin(TWO_PI * 120 * tb) * np.exp(-tb * 35) * np.minimum(1, tb / 0.002), t0, amp * 0.45)
    for k in range(8):
        add(out, china_ping(seed + 10 + k, r.uniform(2500, 7000), click=0.8), t0 + r.uniform(0, 0.006), amp * 0.3)
    for j in range(pieces):
        size = r.random() ** 2
        if not crumbs:
            size = 0.3 + 0.7 * size
        f = (6800 - 5000 * size) * r.uniform(0.9, 1.1)
        tl = t0 + (fall + r.normal(0, 0.06) if fall else r.exponential(0.05)) + 0.01
        a0 = amp * (0.12 + 0.55 * size) * r.uniform(0.5, 1.0)
        for k, (tb_, ab) in enumerate(bounces(seed + 100 + j, a0, 4, (0.03, 0.09), (0.35, 0.55))):
            add(out, china_ping(seed + 300 + 4 * j + k, f * r.uniform(0.95, 1.05)), tl + tb_, ab)
        if size < 0.3 and r.random() < 0.45:
            ns = N(r.uniform(0.03, 0.09))
            add(out, bp(white(ns, seed + 900 + j), 3000, 9500) * np.linspace(1, 0, ns) * 0.08 * amp, tl + 0.02)
    if halves:   # the two big halves land and rock on their curved backs: clack ... k-k-k-kk
        for h, (th, f) in enumerate([(0.05, 1150.0), (0.12, 1420.0)]):
            add(out, china_ping(seed + 50 + h, f, decay=55), t0 + th, amp * 0.8)
            tk, dt, a = t0 + th, 0.09, amp * 0.45
            for k in range(9):
                tk += dt
                add(out, china_ping(seed + 60 + 10 * h + k, f * r.uniform(1.0, 1.15), decay=80), tk, a)
                dt *= 0.78
                a *= 0.8
    return out


def plate_shatter(v):
    out = np.zeros(N(1.9), np.float32)
    if v == 1:     # against the wall: shards rain down onto the floor
        plate_break(out, 1200, 0.02, 1.0, floor=False, pieces=45, fall=0.38)
    elif v == 2:   # smashed flat on the floor: skitter everywhere
        plate_break(out, 1210, 0.02, 1.0, floor=True, pieces=55)
    else:          # cracks in two big halves + crumbs
        plate_break(out, 1220, 0.02, 1.0, floor=True, pieces=10, halves=True)
    return verb(out, 'comedor', wet=0.18)


def euler_wobble(seed, dur=1.0, f0=7.0, f1=65.0):
    """A plate spinning down on the floor: contact clicks accelerating 'wa-wa-wa-wrrrr' + final clack."""
    n = N(dur)
    rate = contour(n, [(0, f0), (dur * 0.85, f1), (dur, f1 * 1.2)])
    amp = env_pts(n, [(0, 0.5), (dur * 0.3, 1.0), (dur * 0.9, 0.7), (dur, 0)])
    idx, a = stick_slip(n, rate, seed, 0.08, amp, 0.8)
    exc = pulse_train(n, idx, a, half_sine(0.0005))
    y = excite(exc, [(f, d * 2.5, a_) for f, d, a_ in PLATE], 0.2)
    y = norm(y) + 0.3 * fit(norm(dsp.lowpass(excite(exc, [(140, 30, 1), (260, 40, .6)], 0.1), 600, 2)), len(y))
    out = np.zeros(len(y) + N(0.3), np.float32)
    out[:len(y)] = y
    add(out, knock(seed + 5, PLATE, 0.3, contact=0.0004, click=0.6), dur, 0.8)
    return out


def plate_storm():
    total = 4.6
    out = np.zeros(N(total + 1.0), np.float32)
    r = dsp.rng(1300)
    # plates whizzing down from above first
    for k, tw in enumerate([0.0, 0.32, 0.6, 0.95, 1.35]):
        src = plate_spin_src(N(0.9), 1310 + k, r.uniform(7, 14), r.uniform(0, 0.5), r.uniform(1100, 1700))
        add(out, flyby(src, 0.45, r.uniform(9, 14), r.uniform(0.5, 1.5), seed=1320 + k), tw, r.uniform(0.35, 0.6))
    # the torrent: plates, cups and cutlery breaking on the steps and the floor of the room
    crashes = [0.38, 0.62, 0.8, 0.97, 1.1, 1.22, 1.36, 1.48, 1.63, 1.78, 1.97, 2.18, 2.42, 2.7, 3.02]
    for k, tc in enumerate(crashes):
        dens = 1.0 if 0.9 < tc < 2.2 else 0.7
        plate_break(out, 1400 + 37 * k, tc + r.uniform(-0.03, 0.03), dens * r.uniform(0.55, 1.0),
                    floor=r.random() < 0.6, pieces=int(r.integers(12, 26)))
    for k in range(8):   # mugs: thick, dull, bounce before they break
        tm = r.uniform(0.6, 2.6)
        add(out, knock(1500 + k, detune(MUG, r, 0.08), 0.25, contact=0.0006, click=0.5), tm, r.uniform(0.35, 0.6))
        for j in range(int(r.integers(4, 9))):
            add(out, china_ping(1520 + 10 * k + j, r.uniform(2500, 6000)), tm + 0.12 + r.exponential(0.05), r.uniform(0.1, 0.3))
    # plates tumbling down the stair, one step at a time
    for s_ in range(3):
        ts, a = r.uniform(0.5, 1.8), r.uniform(0.4, 0.6)
        for k in range(int(r.integers(5, 8))):
            add(out, knock(1600 + 20 * s_ + k, detune(PLATE, r, 0.08), 0.2, contact=0.0005, click=0.5), ts, a)
            tb = taxis(N(0.15))
            add(out, np.sin(TWO_PI * 150 * tb) * np.exp(-tb * 40), ts, a * 0.4)        # the wooden step
            ts += r.uniform(0.15, 0.2)
            a *= 0.85
    # cutlery jangling in bursts
    for k in range(34):
        tcut = r.choice([1.0, 1.5, 2.1]) + r.exponential(0.12)
        add(out, knock(1700 + k, detune(CUTLERY, r, 0.15), 0.4, contact=0.0002, click=0.5), tcut, r.uniform(0.06, 0.18))
    # the big serving dish last, and one plate left spinning down on the floor
    plate_break(out, 1800, 3.35, 1.0, floor=True, pieces=30, modes=scale_modes(PLATE, 0.78))
    add(out, euler_wobble(1810, 1.0), 3.55, 0.45)
    return verb(out, 'cuarto61', wet=0.24)


# ====================================================================== 13. the mate slides
MATE = [(1150, 45, 1.0), (2480, 55, 0.7), (3900, 70, 0.5), (5600, 90, 0.3)]          # glazed ceramic mate
COUNTER = [(210, 45, 1.0), (380, 55, 0.7), (690, 70, 0.45), (1150, 90, 0.25)]        # formica over chipboard
BOMBILLA = [(3150, 35, 1.0), (6900, 50, 0.5), (10400, 70, 0.25)]                     # nickel-silver straw


def mate_slide():
    total = 1.95
    n = N(total)
    t = taxis(n)
    r = dsp.rng(1900)
    t0, t1 = 0.04, 1.36
    v = np.where(t < t0, 0.0, np.where(t < t0 + 0.1, (t - t0) / 0.1, np.maximum(0, 1 - (t - t0 - 0.1) / (t1 - t0 - 0.1))))
    v = smooth(v.astype(np.float32), 0.01)
    # the unglazed foot ring chattering over the laminate: stick-slip faster with speed + grit
    idx, a = stick_slip(n, 110 + 430 * v, 1901, 0.35, v, 0.3)
    exc = pulse_train(n, idx, a, half_sine(0.0003))
    cup = excite(exc, MATE, 0.15)[:n]
    board = excite(exc, COUNTER, 0.15)[:n]
    grit = bp(white(n, 1902), 1200, 8000) * grain(n, 90, 1903, 2.0) * v
    out = np.zeros(n + N(0.3), np.float32)
    out[:n] += 0.5 * norm(cup) + 0.45 * norm(board) + 0.3 * norm(grit)
    add(out, knock(1904, MATE + COUNTER[:2], 0.12, contact=0.0006, click=0.4), 0.03, 0.3)   # nudged by nobody
    # the bombilla rattling in the cup, and a little cluster when it stops
    for k, i in enumerate(poisson_times(9.0 * v, 1905)):
        add(out, knock(1910 + k, detune(BOMBILLA, r, 0.05), 0.15, contact=0.0002, click=0.4), i / SR, r.uniform(0.05, 0.14))
    for k, (dt, g) in enumerate([(0.012, 0.16), (0.05, 0.1), (0.11, 0.06), (0.15, 0.03)]):
        add(out, knock(1950 + k, detune(BOMBILLA, r, 0.05), 0.15, contact=0.0002, click=0.4), t1 + dt, g)
    # it rocks on its foot and settles
    for k, (dt, g) in enumerate([(0.02, 0.4), (0.13, 0.2), (0.2, 0.09)]):
        add(out, knock(1960 + k, MATE + COUNTER, 0.15, contact=0.0009, click=0.3), t1 + dt, g)
    return verb(out, 'cocina', wet=0.12)


# ====================================================================== 14. THE empty mate
def mate_sip_empty():
    total = 2.75
    n = N(total)
    t = taxis(n)
    r = dsp.rng(2000)
    out = np.zeros(n + N(0.3), np.float32)
    # A: a hopeful wet start / B: the long, dry, rattling SHHRRRRK-K-K / D: one more hopeless little sip
    pull = env_pts(n, [(0, 0), (0.04, 0.8), (0.3, 1.0), (0.4, 0.6), (0.44, 0), (0.56, 0), (0.62, 0.9), (1.0, 1.0),
                       (1.45, 1.15), (1.62, 1.0), (1.7, 0), (2.18, 0), (2.21, 0.55), (2.33, 0.45), (2.37, 0)])
    pull = np.clip(pull * (1 + 0.15 * snoise(n, 6, 2001)), 0, None)
    wet = env_pts(n, [(0, 1.0), (0.44, 0.9), (0.56, 0.3), (1.2, 0.25), (1.5, 0.55), (1.7, 0.6), (2.2, 0.08), (2.4, 0.08)])
    # air through the filter and the steel tube (open pipe ~17 cm: a 1 kHz harmonic series)
    air = dsp.lowpass(bp(white(n, 2002), 700, 8000), 7000, 2)
    for fpk, g in [(1010, 9), (2020, 8), (3030, 6), (4040, 4), (5050, 2)]:
        air = dsp.peak(air, fpk, g, 6)
    # the rattle: the water film bursting 24-40 times a second, irregular, getting angrier towards the end
    rate = 24 + 12 * smoothstep((t - 0.6) / 1.0) + 4 * snoise(n, 3, 2003)
    idx, ra = stick_slip(n, rate, 2004, 0.45, None, 0.2)
    rattle = pulse_train(n, idx, ra, np.exp(-taxis(N(0.03)) / 0.007))
    dry = smoothstep((t - 0.56) / 0.1) * (1 - smoothstep((t - 1.7) / 0.05))
    floor_ = 0.12 - 0.08 * dry          # the dry part goes nearly silent between bursts: k-k-k
    rattle = floor_ + (1 - floor_) * np.clip(rattle / (np.percentile(rattle, 98) + 1e-9), 0, 1)
    out[:n] += 0.6 * norm(air) * pull * rattle
    # each burst also rings the straw: the gurgle gets a buzzy 'voice'
    buzz = excite(pulse_train(n, idx, ra * pull[idx] * (0.3 + dry[idx]), half_sine(0.0006)),
                  [(1010, 60, 1), (2020, 80, .6), (520, 50, .45)], 0.05)[:n]
    out[:n] += 0.32 * norm(buzz)
    # bubbles in the wet yerba: many small ones in A, a few big ones in B ... and the final glk-glk-GLK
    lam = 110 * pull ** 1.5 * wet
    for j, i in enumerate(poisson_times(lam, 2005)):
        add(out, bubble(r.uniform(550, 1900), 2100 + j, r.uniform(0.3, 1.2), r.uniform(0.2, 1.0), r.uniform(0.6, 1.4)), i / SR, 0.3)
    for k, (tg, f0, g) in enumerate([(1.5, 420, 0.4), (1.57, 350, 0.5), (1.645, 300, 0.65)]):
        add(out, bubble(f0, 2050 + k, 1.4, 1.0, 0.55), tg, g)
    slosh = dsp.lowpass(white(n, 2006), 900, 2) * grain(n, 12, 2007, 2.0) * pull * wet
    out[:n] += 0.12 * norm(slosh)
    gourd = excite(dsp.lowpass(white(n, 2008), 1200, 2) * pull * rattle, [(420, 40, 1), (860, 60, .4)], 0.1)
    out[:len(gourd)] += 0.1 * norm(gourd)[:len(out)]
    # lips: a little smack, then the POP off the bombilla ('pah'), and the tiny tick of the last sip
    lip = lambda s, g: knock(s, [(900, 120, 1), (1800, 160, .5)], 0.05, contact=0.0006, click=0.3)
    add(out, lip(2010, 1), 0.445, 0.15)
    add(out, lip(2011, 1), 1.715, 0.35)
    add(out, dsp.lowpass(burst(0.03, 2012, 2.0), 2500, 2), 1.715, 0.12)
    add(out, lip(2013, 1), 2.375, 0.12)
    return verb(out, 'cerca', wet=0.1)


# ====================================================================== 15. ¡EL TERMO NO!
def cylinder_modes(base, r):
    """Thin-walled steel cylinder: (n,m) shell modes come in close doublets that beat."""
    out = []
    for ra, d, a in [(1.0, 7, 1.0), (2.34, 9, 0.8), (3.7, 11, 0.7), (5.32, 14, 0.55), (7.18, 18, 0.4), (9.34, 22, 0.3),
                     (11.8, 28, 0.2)]:
        for sp in (-0.004, 0.004):
            out.append((base * ra * (1 + sp + r.uniform(-0.001, 0.001)), d, a * 0.5))
    return out


def termo_fly():
    total = 3.4
    n = N(total)
    r = dsp.rng(2100)
    out = np.zeros(n + N(0.8), np.float32)
    # flight: the open mouth whistles each time it faces the airflow, tumbling end over end, Doppler'd past you
    nf = N(1.5)
    tf = taxis(nf)
    tumble = 2.3
    mouth = 0.2 + 0.8 * np.abs(np.sin(np.pi * tumble * tf + 0.3)) ** 3
    fw = 790 * (1 + 0.03 * snoise(nf, 4, 2101)) * (1 + 0.05 * mouth)
    ph = TWO_PI * np.cumsum(fw) / SR
    whistle = (np.sin(ph) + 0.22 * np.sin(2 * ph + 0.5)) * mouth
    breathy = tv_filter(white(nf, 2102), 'bp', fw, bw_oct=0.25) * mouth
    rush = bp(white(nf, 2103), 250, 3000) * (0.35 + 0.65 * np.abs(np.sin(TWO_PI * tumble * tf)))
    src = 0.55 * norm(whistle) + 0.35 * norm(breathy) + 0.45 * norm(rush)
    add(out, flyby(src.astype(np.float32), 0.7, 9.0, 0.7, buffet=0.3, seed=2104), 0.0, 1.0)
    # CLANG into the cupboard door and the tiles (now ~5 m away): double-walled steel + the water inside
    tcl = 1.32
    termo = cylinder_modes(560, r)
    add(out, knock(2110, termo, 1.7, contact=0.0007, click=0.6, amt=0.0), tcl, 0.8)
    add(out, knock(2111, CUPBOARD, 0.5, contact=0.0015, click=0.3), tcl, 0.45)
    tb = taxis(N(0.4))
    add(out, np.sin(TWO_PI * 140 * tb) * np.exp(-tb * 18) * np.minimum(1, tb / 0.002), tcl, 0.4)
    for k in range(4):
        add(out, bubble(r.uniform(180, 380), 2120 + k, 1.0, 0.7, 0.5), tcl + 0.04 + 0.05 * k, 0.25)
    for tb_, g in [(1.6, 0.42), (1.76, 0.2)]:
        add(out, knock(2130 + int(tb_ * 10), termo, 1.2, contact=0.0006, click=0.5, amt=0.0), tb_, g)
    # rolling over the floor tiles: a joint every 20 cm, slowing; water glugging inside; tonk against the wall
    tk, dt = 1.86, 0.085
    k = 0
    while tk < 2.95:
        add(out, knock(2140 + k, termo[:6], 0.3, contact=0.0006, click=0.3, amt=0.0), tk, 0.1 * (1 - (tk - 1.86) / 1.4))
        add(out, knock(2180 + k, [(160, 60, 1), (320, 80, .5)], 0.08, contact=0.001, click=0.1), tk, 0.12)
        tk += dt
        dt *= 1.12
        k += 1
    nr = N(1.15)
    rumble = bp(white(nr, 2150), 80, 700) * grain(nr, 25, 2151, 1.5) * np.linspace(1, 0.1, nr)
    add(out, norm(rumble), 1.86, 0.12)
    for k in range(6):
        add(out, bubble(r.uniform(220, 600), 2160 + k, 0.8, 0.6, 0.6), 1.9 + r.uniform(0, 1.0), 0.12)
    add(out, knock(2170, termo, 0.9, contact=0.0008, click=0.4, amt=0.0), 3.02, 0.22)
    return verb(out, 'cocina', wet=0.18)


# ====================================================================== 16. cupboards
CUPBOARD = [(135, 26, .8), (215, 30, 1.0), (340, 36, .85), (520, 44, .7), (790, 55, .5), (1180, 70, .35),
            (1760, 90, .22), (2600, 120, .12)]       # 70s chipboard door, laminate face
CARCASS = [(95, 20, 1.0), (170, 25, .8), (290, 32, .6), (480, 42, .4)]
HINGE = [(1450, 25, 1.0), (2900, 35, 0.6), (4400, 45, 0.3)]


def cupboard_bang(out, seed, t0, amp=1.0, dishes=10):
    r = dsp.rng(seed)
    add(out, knock(seed, detune(CUPBOARD, r, 0.08), 0.6, contact=0.0018, click=0.5), t0, amp)
    add(out, knock(seed + 1, CARCASS, 0.5, contact=0.003, click=0.0), t0 + 0.001, amp * 0.6)
    tb = taxis(N(0.3))
    add(out, np.sin(TWO_PI * 82 * tb) * np.exp(-tb * 22) * np.minimum(1, tb / 0.003), t0, amp * 0.45)
    add(out, knock(seed + 2, [(2600, 90, 1), (4700, 120, .6)], 0.05, contact=0.0002, click=0.6), t0 + 0.004, amp * 0.2)
    for k in range(dishes):   # the plates and glasses inside jump
        f = r.uniform(1800, 6500)
        ping = china_ping(seed + 10 + k, f) if r.random() < 0.6 else glass_ping(seed + 10 + k, f * 1.3)
        add(out, ping, t0 + 0.006 + r.exponential(0.025), amp * r.uniform(0.04, 0.16))
    return out


def alacena_golpe(v):
    out = np.zeros(N(1.6), np.float32)
    if v == 1:
        cupboard_bang(out, 2200, 0.02, 1.0, 12)
    elif v == 2:   # swings open on a dry hinge ... BANG
        add(out, norm(creak(0.34, 2210, [(0, 90), (0.2, 55), (0.34, 35)], HINGE, [(0, 0), (0.05, 1), (0.28, 0.7), (0.34, 0)])), 0.0, 0.25)
        cupboard_bang(out, 2220, 0.4, 1.0, 10)
    else:          # three doors, irregular, the poltergeist's drum solo
        for k, (tb, g) in enumerate([(0.02, 0.85), (0.2, 1.0), (0.31, 0.7), (0.52, 0.55)]):
            cupboard_bang(out, 2230 + 20 * k, tb, g, 7)
    return verb(out, 'cocina', wet=0.14)


# ====================================================================== 17. the chair tower
CHAIR = [(190, 30, .8), (310, 35, 1.0), (470, 40, .8), (720, 50, .6), (1050, 60, .45), (1600, 80, .3), (2400, 110, .15)]
CHAIR_JOINT = [(260, 25, 1.0), (520, 35, 0.6), (980, 50, 0.35), (1700, 70, 0.2)]


def chair_stack():
    total = 3.8
    out = np.zeros(N(total + 0.5), np.float32)
    r = dsp.rng(2300)
    # the last of it settling into place: a short clatter of legs finding legs
    for k, (tc, g) in enumerate([(0.0, 0.7), (0.05, 0.5), (0.09, 0.9), (0.16, 0.45), (0.23, 0.35)]):
        add(out, knock(2301 + k, detune(CHAIR, r, 0.1), 0.35, contact=0.0012, click=0.45), tc, g)
    # the whole tower groans under its own weight
    add(out, norm(creak(0.6, 2310, [(0, 45), (0.3, 70), (0.6, 30)], CHAIR_JOINT, [(0, 0), (0.1, 1), (0.45, 0.6), (0.6, 0)])), 0.35, 0.3)
    add(out, norm(creak(0.45, 2311, [(0, 60), (0.45, 35)], scale_modes(CHAIR_JOINT, 1.3), [(0, 0), (0.08, 0.8), (0.45, 0)])), 2.05, 0.2)
    # the top chair balancing on one leg: tok... tok.. tok.tok-tk (rocking settles like a bounce)
    tk, dt, a = 0.75, 0.62, 0.55
    for k in range(11):
        modes = scale_modes(CHAIR, 1.18 if k % 2 else 1.0)
        add(out, knock(2320 + k, detune(modes, r, 0.04), 0.3, contact=0.0009, click=0.5), tk, a)
        tk += dt
        dt *= 0.72
        a *= 0.82
    add(out, norm(creak(0.18, 2340, [(0, 80), (0.18, 50)], CHAIR_JOINT, [(0, 0), (0.05, 1), (0.18, 0)])), tk + 0.1, 0.1)
    # dust and a flake of paint from the ceiling it is touching
    nd = N(1.2)
    dust = bp(white(nd, 2350), 2500, 9000) * env_pts(nd, [(0, 0), (0.1, 1), (1.2, 0)]) * grain(nd, 40, 2351, 2)
    add(out, dust, 0.3, 0.015)
    add(out, china_ping(2352, 3800, decay=120), 2.9, 0.05)
    return verb(out, 'comedor', wet=0.2)


# ====================================================================== 18. five doors, closer each time
DOOR = [(85, 18, .9), (120, 22, 1.0), (175, 26, .9), (250, 30, .8), (350, 34, .7), (480, 40, .55), (680, 48, .45),
        (950, 60, .35), (1350, 75, .25), (1900, 100, .18), (2700, 130, .12)]   # solid 1950s interior door
LATCH = [(1900, 30, .5), (3100, 40, 1), (4600, 55, .7), (6300, 70, .5)]


def interior_slam(seed, swing=0.18):
    r = dsp.rng(seed)
    n = N(swing + 1.2)
    out = np.zeros(n, np.float32)
    nw = N(swing)
    tw = taxis(nw)
    whoosh = tv_filter(colored(nw, 'pink', seed + 1), 'lp', 250 + 1200 * (tw / swing) ** 2) * (tw / swing) ** 2.5
    add(out, norm(whoosh), 0.0, 0.16)
    exc = np.zeros(N(1.0), np.float32)
    hs = half_sine(0.003)
    exc[:len(hs)] = hs
    exc[N(0.0012):N(0.0012) + len(half_sine(0.0005))] += 0.6 * half_sine(0.0005)
    body = norm(excite(exc, detune(DOOR, r, 0.06), 1.0)[:N(1.0)])
    add(out, body, swing, 1.0)
    add(out, norm(dsp.highpass(burst(0.012, seed + 2, 3.0), 1200, 2)), swing, 0.6)
    tb = taxis(N(0.6))
    add(out, np.sin(TWO_PI * np.cumsum(52 * (1 + 0.5 * np.exp(-tb * 25))) / SR) * np.exp(-tb * 12) * np.minimum(1, tb / 0.003), swing, 0.5)
    add(out, knock(seed + 3, LATCH, 0.4, click=0.5), swing + 0.008, 0.3)
    tk, a = swing + 0.025, 0.35
    for j in range(5):   # the leaf chattering in its frame
        add(out, knock(seed + 10 + j, DOOR[5:], 0.12, contact=0.001, click=0.3), tk, a)
        tk += r.uniform(0.018, 0.03)
        a *= r.uniform(0.5, 0.7)
    return out


def door_slam_cascade():
    total = 3.6
    n = N(total)
    dry = np.zeros(n, np.float32)
    send = np.zeros(n, np.float32)
    # five doors down the 12 m hallway, accelerating towards you: far ones dark and drowned in the hall
    for k, (tk, d) in enumerate([(0.0, 10.0), (0.62, 7.4), (1.1, 5.0), (1.44, 2.9), (1.68, 1.1)]):
        s = interior_slam(2400 + 17 * k, swing=0.12 + 0.03 * k)
        g = (1.1 / d) ** 0.8
        s = dsp.lowpass(s, 2600 + 12000 * (1.1 / d), 2)
        add(dry, s, tk, g)
        add(send, s, tk, 0.32)
    # the last one is right next to you: the air of the hallway thumps your ears, the picture frames rattle
    tl = 1.68 + 0.24
    tb = taxis(N(0.9))
    add(dry, dsp.lowpass(white(N(0.9), 2490), 120, 2) * np.exp(-tb * 7) * 1.0, tl, 0.6)
    add(dry, np.sin(TWO_PI * 38 * tb) * np.exp(-tb * 6) * np.minimum(1, tb / 0.005), tl, 0.7)
    r = dsp.rng(2491)
    for j in range(10):
        add(dry, glass_ping(2500 + j, r.uniform(2500, 6000), amp=r.uniform(0.3, 1)), tl + 0.01 + r.exponential(0.05), 0.05)
    for j in range(4):
        add(dry, knock(2520 + j, [(600, 60, 1), (1300, 80, .6)], 0.1, contact=0.0008, click=0.3), tl + 0.03 + r.exponential(0.06), 0.06)
    wet = signal.fftconvolve(send, room_ir('pasillo', 7, decay=1.4))
    out = np.zeros(len(wet), np.float32)
    out[:n] += dry
    out += 1.6 * wet.astype(np.float32)
    return out


# ====================================================================== 19. light bulb pops
def bulb_pop(v):
    r = dsp.rng(2600 + v)
    n = N(1.6)
    out = np.zeros(n, np.float32)
    tp = 0.02
    if v == 2:   # filament arcing first: a sputtering 100 Hz buzz with sizzle
        na = N(0.3)
        ta = taxis(na)
        buzz = np.tanh(5 * np.sin(TWO_PI * 100 * ta)) * (snoise(na, 30, 2601) > -0.25)
        sizz = crackle(na, 1500, 2602, 2500, 11000, size=(0.0001, 0.0004))
        add(out, (0.4 * norm(bp(smooth(buzz, 0.0005), 100, 3500)) + norm(sizz)) * smoothstep(ta / 0.3), 0.0, 0.22)
        tp = 0.3
    add(out, norm(dsp.highpass(burst(0.0006, 2603 + v, 2.0), 4000, 2)), tp - 0.004, 0.25)   # filament snaps
    # the envelope implodes: a sharp 'pomp' (low-pressure gas) + glass bursting
    nb = N(0.2)
    tb = taxis(nb)
    pomp = np.sin(TWO_PI * np.cumsum(140 * (1 + 1.5 * np.exp(-tb * 80))) / SR) * np.exp(-tb * 45) * np.minimum(1, tb / 0.0005)
    add(out, pomp, tp, 0.8)
    add(out, norm(bp(burst(0.006, 2605 + v, 1.5), 400, 9000)), tp, 0.9)
    for j in range(45):
        tj = tp + r.exponential(0.01)
        add(out, glass_ping(2610 + 100 * v + j, r.uniform(4000, 12000), amp=r.uniform(.15, .55) * np.exp(-(tj - tp) / 0.03)), tj)
    # thin shards landing on the hallway floor
    for j in range(26 if v == 1 else 16):
        tl = tp + r.normal(0.45, 0.08) + r.exponential(0.06)
        for k, (tbn, ab) in enumerate(bounces(2700 + 50 * v + j, r.uniform(0.1, 0.45), 3, (0.02, 0.06), (0.3, 0.5))):
            add(out, glass_ping(2800 + 200 * v + 3 * j + k, r.uniform(4500, 11000), amp=ab), tl + tbn)
    if v == 2:   # what is left of the filament sizzles in the socket
        ns = N(0.4)
        add(out, crackle(ns, 600 * np.exp(-taxis(ns) / 0.12), 2650, 3000, 11000), tp + 0.05, 0.25)
    return verb(out, 'pasillo', wet=0.22)


# ====================================================================== 20. porcelain head turning
PORC = [(2900, 90, 1.0), (4700, 110, 0.8), (6800, 140, 0.5), (9100, 180, 0.3)]
HEAD = [(640, 70, 0.7), (1480, 90, 0.5)]     # the hollow porcelain head (air cavity + shell)


def porcelain_click(seed, amp=1.0, k=1.0):
    return knock(seed, scale_modes(PORC, k) + HEAD, 0.12, contact=0.00025, click=0.5) * amp


def doll_turn(v):
    out = np.zeros(N(0.9), np.float32)
    r = dsp.rng(2900 + v)
    if v == 1:     # krrk-TOK
        ng = N(0.11)
        idx, a = stick_slip(ng, env_pts(ng, [(0, 120), (0.11, 210)]), 2901, 0.4, env_pts(ng, [(0, 0.3), (0.05, 1), (0.11, 0.6)]), 0.3)
        grind = excite(pulse_train(ng, idx, a, half_sine(0.0002)), PORC + HEAD, 0.05)
        add(out, norm(grind), 0.0, 0.5)
        add(out, porcelain_click(2902, 1.0), 0.13)
    elif v == 2:   # tk-tk-tk-tk ratchet, then TOK
        for k, tk in enumerate([0.0, 0.075, 0.16, 0.22]):
            add(out, porcelain_click(2910 + k, r.uniform(0.4, 0.6), r.uniform(0.95, 1.08)), tk)
        add(out, porcelain_click(2915, 1.0, 0.92), 0.3)
    else:          # slow squealing grind, porcelain on porcelain, and a clean 'tink' at the end
        ng = N(0.4)
        rate = env_pts(ng, [(0, 60), (0.25, 160), (0.4, 260)])
        idx, a = stick_slip(ng, rate, 2920, 0.2, env_pts(ng, [(0, 0.2), (0.1, 0.8), (0.4, 1.0)]), 0.6)
        squeal = excite(pulse_train(ng, idx, a, half_sine(0.0002)), PORC + HEAD, 0.05)
        add(out, norm(squeal), 0.0, 0.45)
        add(out, china_ping(2921, 3650, decay=35, click=0.2), 0.43, 0.6)
    return verb(out, 'pieza', wet=0.18)


# ====================================================================== 21. ten porcelain giggles
def giggle(seed, syls, total, scale=1.6, breath=0.3, asp=0.6, fmax=11000.0):
    """'hi-hi-hi' giggle: syls = [(t, dur, f_start, f_end, amp)], aspirated onsets, breathy tiny voice."""
    n = N(total)
    f0 = np.zeros(n)
    amp = np.zeros(n, np.float32)
    asp_env = np.zeros(n, np.float32)
    for (t, d, fa, fb, a) in syls:
        i0, i1 = N(t), min(n, N(t + d))
        if i1 - i0 < 16:
            continue
        f0[i0:i1] = np.geomspace(fa, fb, i1 - i0)
        amp[i0:i1] = np.maximum(amp[i0:i1], a * env_pts(i1 - i0, [(0, 0), (0.007, 1.0), (0.45 * d, 0.75), (d, 0)]) ** 1.2)
        h0 = max(0, i0 - N(0.02))
        he = env_pts(i0 + N(0.01) - h0, [(0, 0), (0.012, 1), (0.02, 0.6), (0.03, 0)])
        m = max(0, min(len(he), n - h0))
        asp_env[h0:h0 + m] += a * he[:m]
    idx = np.where(f0 > 0, np.arange(n), 0)
    np.maximum.accumulate(idx, out=idx)
    f0 = np.where(f0 > 0, f0, f0[idx])
    f0[f0 <= 0] = syls[0][2]
    fr = ftrack(n, [(0, vowel('i', scale, 1.2, 'e', 0.5))])
    y = vsynth(f0, fr, amp, tilt=1.0, jitter=0.012, shimmer=0.08, breath=breath, fmax=fmax, seed=seed)
    h = shaped_noise(fr, n, seed + 7, hf=0.8) * asp_env
    return (norm(y) + asp * norm(h)).astype(np.float32)


def hollow(x, seed):
    """Inside a porcelain head: cavity resonances and a short comb."""
    y = dsp.peak(dsp.peak(x, 1100, 5, 2.0), 3000, 4, 2.5)
    d = N(0.0011 + 0.0004 * dsp.rng(seed).random())
    y2 = np.zeros_like(y)
    y2[d:] = y[:-d]
    return (y + 0.35 * y2).astype(np.float32)


def doll_giggle_chorus():
    total = 3.6
    out = np.zeros(N(total + 0.6), np.float32)
    r = dsp.rng(3000)
    for k in range(10):
        front = k < 3                     # three on the near end of the shelf, clearly giggling ...
        start = [0.0, 0.42, 0.86][k] if front else r.uniform(0.1, 1.4)
        rate = r.uniform(6.5, 9.5)
        nsyl = int(r.integers(4, 7)) if front else int(r.integers(3, 7))
        base = r.uniform(620, 980)
        syls = []
        for j in range(nsyl):
            fs = base * (1 - 0.045 * j) * r.uniform(0.98, 1.02)
            syls.append((0.03 + j / rate, 0.55 / rate, fs, fs * 0.84, (1 - 0.1 * j) * r.uniform(0.8, 1.0)))
        g = giggle(3001 + k, syls, 0.1 + nsyl / rate + 0.1, scale=r.uniform(1.5, 1.72))
        g = hollow(g, 3020 + k)
        dist = 0.0 if front else r.uniform(0.35, 1)   # ... the rest further along the 2 m shelf, duller, quieter
        g = dsp.lowpass(g, 9000 - 4500 * dist, 2)
        add(out, g, start, (r.uniform(0.85, 1.0) if front else r.uniform(0.35, 0.6)) * (1 - 0.35 * dist))
    # and one stays behind, slower and lower, after the others stop
    syls = [(0.03, 0.12, 560, 500, 1.0), (0.31, 0.12, 520, 460, 0.85), (0.62, 0.16, 470, 400, 0.7)]
    g = hollow(giggle(3050, syls, 1.0, scale=1.55, breath=0.4), 3051)
    add(out, dsp.lowpass(g, 6500, 2), 2.45, 0.6)
    return verb(out, 'pieza', wet=0.3)


# ====================================================================== 22. the Nona's walker (running gag)
WALKER = [(410, 30, .7), (980, 40, 1.0), (1720, 55, .7), (2650, 70, .5), (3900, 90, .3)]   # aluminium tubes


def squeak(seed, dur, f_pts, amp_pts, rough=0.2):
    """Axle squeal: a near-periodic stick-slip tone with harmonics, rough amplitude and a little breath."""
    n = N(dur)
    f = contour(n, f_pts) * (1 + 0.006 * snoise(n, 60, seed))
    ph = TWO_PI * np.cumsum(f) / SR
    y = np.sin(ph) + 0.5 * np.sin(2 * ph + .3) + 0.28 * np.sin(3 * ph + 1) + 0.14 * np.sin(4 * ph + 2) + 0.07 * np.sin(5 * ph)
    e = env_pts(n, amp_pts)
    y = y * (1 + rough * snoise(n, 90, seed + 1)) * e
    y += 0.12 * norm(tv_filter(white(n, seed + 2), 'bp', f, bw_oct=0.3)) * e
    body = excite(y.astype(np.float32) * 0.3, WALKER, 0.1)
    return (y + fit(norm(body), n) * 0.3).astype(np.float32)


def squeak_motif(seed, k=1.0):
    """THE squeak: a little 'ee' then a louder, higher 'EEK' - identical every time the Nona moves."""
    out = np.zeros(N(0.32), np.float32)
    add(out, squeak(seed, 0.085, [(0, 1650 * k), (0.085, 1720 * k)], [(0, 0), (0.01, 0.55), (0.07, 0.5), (0.085, 0)]), 0.0)
    add(out, squeak(seed + 5, 0.16, [(0, 2050 * k), (0.06, 2380 * k), (0.16, 2240 * k)],
                    [(0, 0), (0.012, 1.0), (0.12, 0.85), (0.16, 0)]), 0.125)
    return out


def walker_tunk(seed, amp=1.0):
    tb = taxis(N(0.2))
    y = knock(seed, WALKER, 0.3, contact=0.0015, click=0.25)
    y[:len(tb)] += 0.8 * np.sin(TWO_PI * 130 * tb) * np.exp(-tb * 40) * np.minimum(1, tb / 0.002)
    return y * amp


def andador_squeak(v):
    out = np.zeros(N(1.6), np.float32)
    if v == 1:
        add(out, walker_tunk(3100, 0.7), 0.0)
        add(out, squeak_motif(3110), 0.2, 0.8)
    elif v == 2:
        add(out, walker_tunk(3101, 0.7), 0.0)
        add(out, squeak_motif(3110), 0.22, 0.8)
        add(out, squeak_motif(3110, 0.97), 0.8, 0.7)
        add(out, walker_tunk(3102, 0.5), 1.22)
    else:        # dragged instead of lifted: one long rising squeal ... beat ... and a tiny 'ik'
        add(out, walker_tunk(3103, 0.7), 0.0)
        add(out, squeak(3120, 0.55, [(0, 1600), (0.3, 2100), (0.55, 2500)],
                        [(0, 0), (0.03, 0.6), (0.4, 0.9), (0.5, 1.0), (0.55, 0)], rough=0.3), 0.2, 0.8)
        add(out, squeak(3121, 0.045, [(0, 2400), (0.045, 2500)], [(0, 0), (0.008, 0.7), (0.045, 0)]), 1.08, 0.6)
    return verb(out, 'pieza', wet=0.12)


# ====================================================================== 23. the Nona's chancleta
FLESH = [(190, 90, 1.0), (330, 110, 0.8), (560, 140, 0.6), (900, 180, 0.35), (1400, 220, 0.2)]


def chancleta_whip():
    total = 1.05
    n = N(total)
    t = taxis(n)
    # end over end ~9 turns a second: the flat sole slaps the air each half turn, the strap flutters
    ph = TWO_PI * 9.0 * t
    flap = np.abs(np.sin(ph)) ** 6
    strap = np.abs(np.sin(ph + 1.2)) ** 10
    air = bp(white(n, 3201), 250, 3500) * (0.12 + flap)
    flutter = bp(white(n, 3202), 1500, 6000) * strap * (1 + 0.5 * snoise(n, 200, 3203))
    low = bp(white(n, 3204), 80, 500) * flap
    src = norm(air) + 0.4 * norm(flutter) + 0.7 * norm(low)
    y = flyby(src.astype(np.float32), 0.45, 11.0, 0.45, buffet=0.45, seed=3205)
    out = np.zeros(n + N(0.3), np.float32)
    out[:n] += y
    nr = N(0.07)   # the flick of the wrist at release
    add(out, bp(white(nr, 3206), 500, 4000) * env_pts(nr, [(0, 0), (0.015, 1), (0.07, 0)]), 0.0, 0.12)
    return verb(out, 'pasillo', wet=0.1)


def chancleta_hit():
    total = 1.3
    out = np.zeros(N(total), np.float32)
    ti = 0.01
    # ¡PLAF! the flat rubber sole meets skin: a short, very wide crack ...
    add(out, norm(dsp.peak(bp(burst(0.0035, 3301, 1.2), 900, 14000), 2600, 6, 1.0)), ti, 1.0)
    add(out, norm(dsp.highpass(burst(0.0008, 3302, 2.0), 3000, 2)), ti, 0.45)
    # ... the thwack of flesh and EVA rubber (a dull knock that dies at once) and a bass punch for the cartoon
    add(out, knock(3303, FLESH, 0.12, contact=0.0025, click=0.0), ti, 0.85)
    tb = taxis(N(0.15))
    add(out, np.sin(TWO_PI * np.cumsum(92 + 130 * np.exp(-tb / 0.006)) / SR) * np.exp(-tb * 32) * np.minimum(1, tb / 0.001), ti, 0.75)
    add(out, dsp.lowpass(bp(burst(0.012, 3304, 1.5), 400, 3500), 3000, 2), ti + 0.004, 0.3)   # trapped air 'pff'
    # the toe of the sole flaps on a beat later: p-TAP
    add(out, norm(bp(burst(0.0025, 3305, 1.2), 1200, 12000)), ti + 0.042, 0.32)
    add(out, knock(3306, FLESH, 0.08, contact=0.0018, click=0.0), ti + 0.042, 0.25)
    # the slipper drops on the floorboards: plop ... pok
    PLOP = [(150, 60, 1.0), (320, 80, 0.6), (700, 110, 0.3), (1300, 150, 0.15)]
    add(out, knock(3307, PLOP, 0.2, contact=0.004, click=0.2), 0.62, 0.3)
    add(out, knock(3308, PLOP, 0.15, contact=0.003, click=0.15), 0.745, 0.12)
    y = out + 0.22 * fit(np.concatenate([np.zeros(N(0.017)), out]), len(out)) \
        + 0.12 * fit(np.concatenate([np.zeros(N(0.034)), out]), len(out))     # slapback off the hallway walls
    return verb(y.astype(np.float32), 'pasillo', wet=0.15)


# ====================================================================== 24. the floating rocking chair (loop)
ROCKER = [(165, 22, 0.8), (290, 28, 1.0), (480, 34, 0.75), (760, 42, 0.55), (1150, 55, 0.4), (1750, 70, 0.25),
          (2600, 95, 0.12)]   # light oak, woven cushion


def rocking_creak_slow():
    L = N(4.0)
    buf = np.zeros(L + N(1.0), np.float32)
    r = dsp.rng(3400)
    # swing period 4 s, no floor under the rockers: only the joints talk, once per half swing
    c1 = creak(1.5, 3401, [(0, 28), (0.5, 72), (1.0, 60), (1.5, 30)], ROCKER,
               [(0, 0), (0.25, 0.6), (0.7, 1.0), (1.2, 0.5), (1.5, 0)], jitter=0.35, tail=0.25)
    c2 = creak(1.4, 3402, [(0, 40), (0.6, 95), (1.4, 42)], scale_modes(ROCKER, 1.35),
               [(0, 0), (0.3, 0.7), (0.75, 0.85), (1.1, 0.4), (1.4, 0)], jitter=0.3, tail=0.25)
    add(buf, norm(c1), 0.25, 1.0)
    add(buf, norm(c2), 2.3, 0.75)
    for tk, g in [(0.02, 0.18), (2.04, 0.13)]:    # the spindles knock in their holes at each turn-around
        add(buf, knock(3410 + int(tk), ROCKER[2:], 0.2, contact=0.0012, click=0.3), tk, g)
    y = fold(buf, L)
    tt = taxis(L)
    w = np.abs(np.cos(TWO_PI * tt / 4.0)).astype(np.float32)
    cushion = cfilt(white(L, 3420), lambda f: hp2(f, 900) * lp2(f, 5000)) * cgrain(L, 60, 3421, 2.0) * w ** 2
    air = cfilt(white(L, 3422), lambda f: hp2(f, 60) * lp2(f, 400)) * w ** 2
    y = norm(y) + 0.04 * norm(cushion) + 0.05 * norm(air)
    return verb(y, 'cuarto61', wet=0.25, circular=True)


# ====================================================================== 25. red wool
def wool_string(seed, f0, dur, pos=0.18, d0=5.0, damp=1.6, twang=0.05, inharm=0.0004, fuzz=0.25):
    """A taut wool yarn: harmonic string modes with very lossy highs, a tension-modulation pitch fall, fibre rasp."""
    modes = []
    for k in range(1, 50):
        fk = f0 * k * np.sqrt(1 + inharm * k * k)
        if fk > 9000:
            break
        modes.append((fk, d0 + damp * k * k, abs(np.sin(k * np.pi * pos)) / k))
    y = modal_ir(modes, dur, seed)
    n = len(y)
    tt = taxis(n)
    y = varispeed(y, 1 + twang * np.exp(-tt / 0.07), n)
    rasp = bp(white(n, seed + 1), 800, 6000) * grain(n, 300, seed + 2, 1.5) * np.exp(-tt / 0.035)
    return (norm(y) + fuzz * norm(rasp)).astype(np.float32)


def yarn_twang(v):
    out = np.zeros(N(1.8), np.float32)
    if v == 1:
        add(out, wool_string(3501, 98.0, 1.4, twang=0.07), 0.0, 1.0)
        tb = taxis(N(0.3))
        add(out, np.sin(TWO_PI * 72 * tb) * np.exp(-tb * 20) * np.minimum(1, tb / 0.003), 0.0, 0.35)   # the anchor nail
    else:      # pulled tight first (fibres creak, the yarn starts to sing), then plucked
        ns = N(0.42)
        ts = taxis(ns)
        f = 118 + 34 * smoothstep(ts / 0.42)
        bow = bp(white(ns, 3510), 300, 4000) * grain(ns, 200, 3511, 1.5) * env_pts(ns, [(0, 0), (0.3, 1), (0.42, 0.6)])
        tone = sum(np.sin(TWO_PI * k * np.cumsum(f) / SR) / k ** 1.5 for k in range(1, 7)) * env_pts(ns, [(0, 0), (0.35, 1), (0.42, 0.5)])
        crk = crackle(ns, 40 + 260 * (ts / 0.42) ** 2, 3512, 900, 6000)
        add(out, 0.35 * norm(bow) + 0.25 * norm(tone) + 0.35 * norm(crk), 0.0, 0.6)
        add(out, wool_string(3513, 152.0, 1.3, pos=0.11, twang=0.09, d0=4.0), 0.42, 1.0)
    return verb(out, 'cuarto61', wet=0.2)


def yarn_snap():
    out = np.zeros(N(1.4), np.float32)
    tsn = 0.42
    ns = N(tsn)
    ts = taxis(ns)
    # fibres giving way one by one (accelerating), the yarn singing higher as it stretches
    crk = crackle(ns, 25 + 420 * (ts / tsn) ** 2.2, 3601, 900, 7000, amp_env=0.4 + 0.6 * ts / tsn)
    f = 170 + 100 * (ts / tsn) ** 1.5
    sing = sum(np.sin(TWO_PI * k * np.cumsum(f) / SR) / k ** 1.4 for k in range(1, 8)) * (ts / tsn) ** 1.5
    sing = sing * (1 + 0.3 * snoise(ns, 40, 3602))
    add(out, 0.5 * norm(crk) + 0.18 * norm(sing), 0.0, 0.7)
    # SNAP
    add(out, norm(bp(burst(0.003, 3603, 1.2), 900, 10000)), tsn, 1.0)
    add(out, norm(dsp.highpass(burst(0.0007, 3604, 2.0), 3500, 2)), tsn, 0.4)
    tb = taxis(N(0.25))
    add(out, np.sin(TWO_PI * 70 * tb) * np.exp(-tb * 30) * np.minimum(1, tb / 0.002), tsn, 0.5)
    # the two halves whip back, their free ends buzzing low, and the slack falls
    for k, dt in enumerate([0.004, 0.022]):
        nw = N(0.09)
        add(out, bp(white(nw, 3610 + k), 400, 3500) * env_pts(nw, [(0, 0), (0.01, 1), (0.09, 0)]), tsn + dt, 0.3)
    add(out, wool_string(3620, 68.0, 0.5, pos=0.3, twang=0.15, d0=10.0, fuzz=0.4), tsn + 0.01, 0.35)
    nf = N(0.35)
    add(out, bp(white(nf, 3630), 600, 4000) * grain(nf, 60, 3631, 2.0) * env_pts(nf, [(0, 0), (0.08, 1), (0.35, 0)]), tsn + 0.3, 0.06)
    return verb(out, 'cuarto61', wet=0.18)


# ====================================================================== 26. stitches (ASMR close)
def stitch_once(seed, pulls, squeak_amt=0.5):
    """Needle through cloth: puncture pops + 'thup', eye dragging, thread hissing through, tug squeak + gather."""
    r = dsp.rng(seed)
    total = 0.12 + sum(d + gap for d, gap in pulls) + 0.4
    out = np.zeros(N(total), np.float32)
    for k in range(int(r.integers(3, 7))):
        add(out, dsp.highpass(burst(r.uniform(0.0003, 0.0008), seed + k, 2.0), 1500, 2), r.uniform(0, 0.016), r.uniform(0.1, 0.3))
    add(out, dsp.lowpass(burst(0.012, seed + 10, 1.5), 400, 2), 0.0, 0.35)
    ne = N(0.06)
    add(out, bp(white(ne, seed + 11), 1500, 8000) * grain(ne, 400, seed + 12, 2.0) * env_pts(ne, [(0, 0), (0.01, 1), (0.06, 0)]), 0.02, 0.3)
    t = 0.1
    for j, (d, gap) in enumerate(pulls):
        nP = N(d)
        v = env_pts(nP, [(0, 0), (0.12 * d, 0.8), (0.4 * d, 1.0), (0.55 * d, 0.75), (0.7 * d, 1.0), (0.88 * d, 0.6), (d, 0)])
        v = np.clip(v * (1 + 0.15 * snoise(nP, 8, seed + 19 + j)), 0, None)
        # the thread's fibres stick and slip in the weave: a buzzy 'zzzip' whose pitch follows the pull speed,
        # rung through the (heavily damped) cloth and thread, over a softer fibre hiss
        idx, a = stick_slip(nP, 120 + 520 * v, seed + 20 + j, 0.35, v, 0.4)
        zipk = excite(pulse_train(nP, idx, a, half_sine(0.00025)),
                      [(1300, 300, 1.0), (2600, 380, 0.7), (4200, 500, 0.4), (650, 250, 0.4)], 0.02)[:nP]
        hiss = bp(white(nP, seed + 40 + j), 2000, 7500) * (0.5 + 0.5 * grain(nP, 120, seed + 41 + j, 1.5)) * v
        add(out, 0.85 * norm(zipk) + 0.3 * norm(hiss), t, 1.0)
        t += d + gap
    # the tug: the thread squeaks tight and the cloth gathers
    tq = t - pulls[-1][1]
    nq = N(0.07)
    fq = contour(nq, [(0, 1350 + 300 * r.random()), (0.07, 1800 + 200 * r.random())])
    sq = np.sin(TWO_PI * np.cumsum(fq) / SR) * (1 + 0.5 * snoise(nq, 120, seed + 50)) * env_pts(nq, [(0, 0), (0.01, 1), (0.07, 0)])
    add(out, sq, tq, 0.25 * squeak_amt)
    add(out, dsp.lowpass(bp(white(N(0.045), seed + 51), 400, 6000), 3000, 2) * np.linspace(1, 0, N(0.045)), tq + 0.01, 0.3)
    add(out, dsp.lowpass(burst(0.01, seed + 52, 1.5), 500, 2), tq + 0.005, 0.3)
    y = dsp.peak(out, 140, 4, 0.8)    # proximity effect: the mic is at the doll's mouth
    return y


def stitch_pull(v):
    if v == 1:
        y = stitch_once(3700, [(0.8, 0.0)], 0.5)
    elif v == 2:
        y = stitch_once(3720, [(0.34, 0.12), (0.3, 0.0)], 0.4)
    else:
        y = stitch_once(3740, [(1.1, 0.0)], 1.0)
    return verb(y, 'cerca', wet=0.08)


# ====================================================================== 27. AZAMEL sucked into the doll
def azamel_suck():
    # a scream (the girl, the old woman and the thing in them) with the 1961 room's tail, run backwards
    nv = N(1.6)
    fw = contour(nv, [(0, 700), (0.08, 980), (0.6, 900), (1.1, 760), (1.6, 520)])
    amp = env_pts(nv, [(0, 0), (0.03, 1.0), (0.9, 0.85), (1.4, 0.4), (1.6, 0)])
    woman = vsynth(fw, ftrack(nv, [(0, vowel('a', 1.17)), (0.9, vowel('e', 1.17, name2='a', mix=0.5))]), amp,
                   tilt=0.9, rough=0.5, rough_hz=70, breath=0.35, fmax=9000, seed=3801)
    demon = vsynth(fw * 0.25, ftrack(nv, [(0, vowel('a', 0.7)), (1.6, vowel('o', 0.68))]), amp, tilt=0.8, rough=1.0,
                   rough_hz=45, sub=0.8, breath=0.3, fmax=4500, seed=3802)
    scream = dsp.drive(norm(woman) + 0.7 * norm(demon), 1.7)
    wet = verb(scream, 'cuarto61', wet=0.55, decay=2.0)
    rev = dsp.reverse(wet)
    t_cut = 2.0
    nrev = N(t_cut)
    seg = rev[-int(nrev * 1.25):]
    # ... and it accelerates into the point: varispeed rising -> pitch climbing as it is swallowed
    rate = 1.0 + 0.55 * smoothstep(taxis(nrev) / t_cut) ** 2
    pulled = varispeed(seg, rate, nrev)
    tt = taxis(nrev)
    whoosh = tv_filter(colored(nrev, 'pink', 3803), 'bp', 300 * (7000 / 300) ** ((tt / t_cut) ** 1.6),
                       bw_oct=1.5) * (tt / t_cut) ** 2.2
    sub = np.sin(TWO_PI * np.cumsum(28 + 50 * (tt / t_cut) ** 2) / SR) * (tt / t_cut) ** 1.8
    body = norm(pulled) + 0.25 * norm(whoosh) + 0.35 * sub
    body *= 1 - smoothstep((tt - (t_cut - 0.004)) / 0.004)      # cut: swallowed
    out = np.zeros(N(t_cut + 1.3), np.float32)
    out[:nrev] = body
    # silence ... and the porcelain lips close: tink (and a smaller one as the head settles)
    tk = t_cut + 0.14
    add(out, china_ping(3810, 3400, decay=30, click=0.3), tk, 0.42)
    add(out, china_ping(3811, 4150, decay=45, click=0.2), tk + 0.17, 0.14)
    tail = np.zeros_like(out)
    tail[N(tk):] = out[N(tk):]
    out[N(tk):] = 0
    return out + fit(verb(tail, 'pieza', wet=0.25), len(out))


# ====================================================================== 28. seven altar candles
def flame_out(seed, flutter, amp=1.0):
    """A candle flame bent by breath: fluttering combustion roar, the 'pfft' as it goes, the wick ticking."""
    r = dsp.rng(seed)
    nf = N(flutter + 0.6)
    tf = taxis(nf)
    flick = 1 + 0.8 * snoise(nf, r.uniform(15, 25), seed)
    env = env_pts(nf, [(0, 0), (0.04, 1.0), (flutter, 0.8), (flutter + 0.03, 0)])
    roar = bp(white(nf, seed + 1), 60, 900) * flick * env
    out = norm(roar) * 0.6
    # the flame lets go: a soft dull 'fup' (the gas column collapsing) and a puff of air
    tb = taxis(N(0.08))
    add(out, np.sin(TWO_PI * r.uniform(150, 210) * tb) * np.exp(-tb * 45) * np.minimum(1, tb / 0.002), flutter, 0.7)
    add(out, norm(dsp.lowpass(bp(burst(0.035, seed + 2, 1.5), 200, 3000), 1800, 2)), flutter, 0.6)
    ns = N(0.5)
    add(out, crackle(ns, 120 * np.exp(-taxis(ns) / 0.15), seed + 3, 2500, 9000, size=(0.0001, 0.0004)), flutter + 0.02, 0.25)
    return out * amp


def candles_out():
    total = 3.9
    out = np.zeros(N(total), np.float32)
    # one long breath, too long and too even for an old woman: lips 'ffff' + an 'uh' of air from deep down
    nb = N(2.5)
    fr = ftrack(nb, [(0, vowel('u', 1.17)), (2.5, vowel('o', 1.17))])
    env = env_pts(nb, [(0, 0), (0.12, 1.0), (1.8, 0.85), (2.1, 0.5), (2.5, 0)])
    breath = shaped_noise(fr, nb, 3901, hf=1.5) * env
    lips = bp(white(nb, 3902), 1500, 9000) * grain(nb, 150, 3903, 1.5) * env
    growl = vsynth(contour(nb, [(0, 58), (2.5, 50)]), ftrack(nb, [(0, vowel('o', 0.7))]), env, tilt=1.0, rough=1.0,
                   rough_hz=40, sub=0.6, breath=0.5, fmax=2500, seed=3904)
    cands = [(0.3, 0.1), (0.47, 0.09), (0.62, 0.12), (0.78, 0.1), (0.93, 0.11), (1.1, 0.1), (1.25, 0.75)]
    # where the breath meets a flame it breaks up for an instant (turbulence round the wick)
    tb_ = taxis(nb)
    hit = np.ones(nb, np.float32)
    for tc, fl in cands:
        hit *= 1 - 0.35 * np.exp(-0.5 * ((tb_ - tc - fl) / 0.02) ** 2)
    add(out, (0.7 * norm(breath) + 0.45 * norm(lips) + 0.06 * norm(growl)) * hit, 0.0, 0.32)
    # the flames, swept by the breath one after the other; the seventh hangs on, then goes
    for k, (tc, fl) in enumerate(cands):
        add(out, flame_out(3910 + k, fl, 1.0 if k < 6 else 1.25), tc, 0.6)
    return verb(out, 'pieza', wet=0.22)


# ====================================================================== 29. the basement wall comes down
def brick(seed, amp, heavy=1.0):
    r = dsp.rng(seed)
    n = N(0.35)
    modes = [(r.uniform(500, 800), r.uniform(40, 70), 1), (r.uniform(1000, 1500), r.uniform(50, 90), .8),
             (r.uniform(1700, 2600), r.uniform(70, 110), .5), (r.uniform(2800, 3800), 140, .3)]
    y = knock(seed, modes, 0.35, contact=0.0012, click=0.45, click_hp=1200)
    tt = taxis(n)
    y = y + heavy * 0.8 * np.sin(TWO_PI * r.uniform(85, 170) * tt) * np.exp(-tt * 30) * np.minimum(1, tt / 0.002)
    grit = bp(burst(0.02, seed + 1, 2.0), 800, 6000)
    y[:len(grit)] += 0.35 * norm(grit)
    return (norm(y) * amp).astype(np.float32)


def blow(out, seed, t0, amp=1.0, f=34.0):
    tb = taxis(N(1.8))
    boom = np.sin(TWO_PI * np.cumsum(f * (1 + 0.5 * np.exp(-tb * 8))) / SR) * np.exp(-tb * 3.2) * np.minimum(1, tb / 0.005)
    thud = bp(colored(len(tb), 'pink', seed), 50, 400) * np.exp(-tb * 9)
    add(out, norm(boom) + 0.7 * norm(thud), t0, amp)
    add(out, knock(seed + 1, [(110, 30, 1), (190, 35, .8), (320, 45, .6), (560, 60, .4), (950, 80, .25)], 0.6,
                   contact=0.004, click=0.4), t0, amp * 0.8)
    nc = N(0.15)
    add(out, norm(crackle(nc, 4000 * np.exp(-taxis(nc) / 0.03), seed + 2, 700, 8000)), t0 + 0.005, amp * 0.5)


def wall_break():
    total = 5.2
    n = N(total)
    r = dsp.rng(4000)
    out = np.zeros(n + N(0.5), np.float32)
    # first blow: the wall takes it; mortar cracks run, grit trickles out of the joints
    blow(out, 4001, 0.0, 0.75)
    for j in range(10):
        add(out, brick(4010 + j, r.uniform(0.05, 0.18), 0.2), r.uniform(0.05, 0.5))
    nt = N(0.8)
    add(out, bp(white(nt, 4030), 1500, 8000) * grain(nt, 40, 4031, 2.0) * env_pts(nt, [(0, 0), (0.1, 1), (0.8, 0)]), 0.08, 0.05)
    # second blow: it gives. crunch, the wall folds into the basement, bricks avalanche over the concrete
    t2 = 0.95
    blow(out, 4040, t2, 1.0, 30.0)
    nc = N(0.35)
    lam = 1100 * np.exp(-taxis(nc) / 0.09)
    idx = poisson_times(lam, 4041)
    crunch = excite(pulse_train(nc, idx, r.uniform(.2, 1, len(idx)).astype(np.float32), burst(0.0008, 4042)),
                    [(620, 60, 1), (1150, 80, .8), (2100, 110, .5), (3300, 150, .3)], 0.08)
    add(out, norm(crunch), t2 + 0.01, 0.7)
    bt = np.concatenate([t2 + 0.1 + r.gamma(2.0, 0.3, 95), t2 + 0.7 + r.gamma(2.0, 0.3, 30)])
    bt = bt[bt < 4.0]
    for j, tb_ in enumerate(np.sort(bt)):
        a = 1.4 * r.uniform(0.25, 0.9) * np.exp(-max(0, tb_ - t2 - 0.3) / 1.6)
        add(out, brick(4100 + j, a), tb_)
        if r.random() < 0.5:
            add(out, brick(4300 + j, a * 0.35, 0.5), tb_ + r.uniform(0.05, 0.16))
    tt = taxis(n)
    rum_env = env_pts(n, [(0, 0), (t2, 0), (t2 + 0.15, 1.0), (t2 + 0.9, 0.7), (t2 + 2.2, 0.15), (total, 0)])
    out[:n] += 0.3 * norm(dsp.lowpass(colored(n, 'brown', 4050), 220, 2)) * rum_env
    slide_env = env_pts(n, [(0, 0), (t2 + 0.2, 0), (t2 + 0.4, 1.0), (t2 + 1.4, 0.5), (t2 + 2.6, 0.08), (total, 0)])
    out[:n] += 0.2 * norm(bp(white(n, 4051), 180, 2600) * grain(n, 55, 4052, 2.0)) * slide_env
    dust_env = env_pts(n, [(0, 0), (t2 + 0.4, 0), (t2 + 0.9, 1.0), (total - 0.3, 0.25), (total, 0)])
    out[:n] += 0.04 * norm(bp(white(n, 4053), 2500, 9000)) * dust_env
    lam = 28 * env_pts(n, [(0, 0), (t2 + 1.6, 0), (t2 + 2.0, 1), (total - 0.4, 0.1), (total, 0)])
    for j, i in enumerate(poisson_times(lam, 4054)):
        add(out, brick(4500 + j, r.uniform(.03, .1), 0.1), i / SR)
    return verb(out, 'sotano', wet=0.24)


# ====================================================================== 30. the demon wisp
def wisp_whistle():
    total = 3.6
    n = N(total)
    t = taxis(n)
    f1 = 2350 * (1 + 0.035 * snoise(n, 1.2, 4101)) * (1 + 0.008 * np.sin(TWO_PI * 6.3 * t))
    f2 = f1 * 1.06 * (1 + 0.01 * snoise(n, 0.8, 4102))     # a semitone above: the two voices rub
    p1 = TWO_PI * np.cumsum(f1) / SR
    tone = np.sin(p1) + 0.45 * np.sin(TWO_PI * np.cumsum(f2) / SR) + 0.08 * np.sin(2 * p1)
    tone *= 1 + 0.3 * snoise(n, 3, 4103)
    breathy = tv_filter(white(n, 4104), 'bp', f1, bw_oct=0.2)
    embers = crackle(n, 70 * (1 + 0.5 * snoise(n, 1, 4105)), 4106, 1500, 9000)
    smoke = bp(white(n, 4107), 200, 2000) * grain(n, 15, 4108, 1.5)
    src = 0.6 * norm(tone) + 0.35 * norm(breathy) + 0.45 * norm(embers) + 0.18 * norm(smoke)
    src *= env_pts(n, [(0, 0), (0.4, 1), (total - 0.6, 1), (total, 0)])
    y = flyby(src.astype(np.float32), 1.7, 5.0, 1.1, lp_far=2800.0, seed=4109)
    return verb(y, 'patio', wet=0.15)


# ====================================================================== 31. the kettle
KETTLE = [(620, 12, 1.0), (1450, 15, 0.7), (2600, 20, 0.5), (3900, 28, 0.3)]


def kettle_whistle():
    total = 7.4
    n = N(total)
    t = taxis(n)
    r = dsp.rng(4200)
    out = np.zeros(n + N(0.5), np.float32)
    off = 5.95
    # the gas hob under it
    burner = bp(white(n, 4201), 80, 1500) * (1 + 0.25 * snoise(n, 12, 4202)) * env_pts(n, [(0, 0), (0.2, 1), (total - 0.6, 1), (total, 0)])
    out[:n] += 0.08 * norm(burner)
    # water coming to the boil: the rising 'singing' hiss, bubbles collapsing faster and faster, a low churn
    heat = smoothstep(t / 3.2)
    sing = bp(white(n, 4203), 1000, 7000) * grain(n, 180, 4204, 1.8) * heat * (1 - 0.5 * smoothstep((t - off) / 0.8))
    churn = bp(white(n, 4205), 90, 450) * (1 + 0.6 * snoise(n, 6, 4206)) * smoothstep((t - 1.5) / 2.0) * (1 - 0.6 * smoothstep((t - off) / 1.0))
    out[:n] += 0.18 * norm(sing) + 0.1 * norm(churn)
    lam = 6 + 110 * heat * (1 - 0.7 * smoothstep((t - off) / 0.6))
    for j, i in enumerate(poisson_times(lam, 4207)[:500]):
        add(out, bubble(r.uniform(1500, 5000), 4300 + j, r.uniform(0.2, 0.8), r.uniform(0.05, 0.4)), i / SR, 0.12)
    # the whistle: breathy tries first, then the full two-chamber shriek rising with the pressure
    t_w = 2.55
    f = np.where(t < 3.2, 1650 + 130 * smoothstep((t - t_w) / 0.65), 1780 + 270 * smoothstep((t - 3.2) / 2.6))
    f = np.where(t > off, f[N(off)] * (1 - 0.45 * smoothstep((t - off) / 0.7)), f)
    f = f * (1 + 0.004 * snoise(n, 25, 4208))
    tries = (snoise(n, 9, 4209) > 0.1).astype(np.float32) * smoothstep((t - t_w) / 0.2)
    gate = np.where(t < 3.2, smooth(tries, 0.02) * 0.6, 1.0)
    w_env = gate * smoothstep((t - t_w) / 0.1) * np.where(t < off, 0.55 + 0.45 * smoothstep((t - 3.2) / 0.8), 1.0)
    w_env = w_env * np.where(t > off, np.exp(-np.maximum(0, t - off) / 0.28), 1.0)
    w_env = w_env * np.where(t > off, 0.6 + 0.4 * (snoise(n, 14, 4210) > -0.3), 1.0)      # sputtering as it dies
    ph = TWO_PI * np.cumsum(f) / SR
    ph2 = TWO_PI * np.cumsum(f * 1.031) / SR
    whistle = np.sin(ph) + 0.55 * np.sin(ph2 + 1) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath_w = tv_filter(white(n, 4211), 'bp', f, bw_oct=0.3)
    out[:n] += (0.55 * norm(whistle) + 0.2 * norm(breath_w)) * smooth(w_env, 0.01)
    # lifted off and set down on the grate: tonk + rattle
    add(out, knock(4220, KETTLE, 1.0, contact=0.0015, click=0.35), off + 0.18, 0.3)
    add(out, knock(4221, [(900, 40, 1), (2100, 55, .6), (3500, 70, .3)], 0.3, contact=0.0008, click=0.4), off + 0.2, 0.15)
    add(out, knock(4222, [(900, 40, 1), (2100, 55, .6), (3500, 70, .3)], 0.3, contact=0.0008, click=0.4), off + 0.26, 0.07)
    return verb(out, 'cocina', wet=0.14)


# ====================================================================== 32. morning birds (stereo loop)
def bird_note(f_pts, dur, amp_pts=None, harm=((1, 1.0), (2, 0.15)), rough=0.0, am_hz=180.0, seed=0):
    n = N(dur)
    f = contour(n, f_pts) * (1 + 0.004 * snoise(n, 40, seed))
    ph = TWO_PI * np.cumsum(f) / SR
    y = sum(a * np.sin(k * ph + 0.7 * k) for k, a in harm)
    if rough:
        y = y * (1 + rough * np.sin(TWO_PI * am_hz * taxis(n)))
    env = env_pts(n, amp_pts or [(0, 0), (0.12 * dur, 1.0), (0.75 * dur, 0.85), (dur, 0)])
    return (y * env).astype(np.float32)


def phrase(notes, seed):
    """notes = [(t, dur, f_pts, amp, kwargs)] -> one bird's phrase (mono)."""
    end = max(t + d for t, d, *_ in notes)
    out = np.zeros(N(end + 0.05), np.float32)
    for k, (t, d, fp, a, kw) in enumerate(notes):
        add(out, bird_note(fp, d, seed=seed + k, **kw), t, a)
    return out


def benteveo(seed, k=1.0):
    """Great kiskadee: a loud, harsh 'bien-te-VEO'."""
    harsh = dict(harm=((1, 1.0), (2, 0.35), (3, 0.12)), rough=0.35, am_hz=170.0)
    return phrase([(0.0, 0.11, [(0, 2500 * k), (0.04, 3100 * k), (0.11, 2800 * k)], 0.8, harsh),
                   (0.17, 0.07, [(0, 3200 * k), (0.07, 3350 * k)], 0.7, harsh),
                   (0.29, 0.3, [(0, 3700 * k), (0.05, 3950 * k), (0.3, 2650 * k)], 1.0,
                    dict(harsh, amp_pts=[(0, 0), (0.03, 1), (0.2, 0.8), (0.3, 0)]))], seed)


def hornero(seed, dur=2.3, k=1.0, offset=0.0):
    """Rufous hornero: a loud accelerating, descending run of sharp notes."""
    r = dsp.rng(seed)
    notes, t, i = [], offset, 0
    while t < dur:
        u = t / dur
        dt = 0.14 - 0.085 * u
        f = (3400 - 700 * u) * k * r.uniform(0.98, 1.02)
        notes.append((t, 0.038, [(0, f * 1.1), (0.012, f * 1.04), (0.038, f * 0.9)], 0.6 + 0.4 * np.sin(np.pi * u),
                      dict(harm=((1, 1.0), (2, 0.2)), amp_pts=[(0, 0), (0.004, 1), (0.03, 0.6), (0.038, 0)])))
        t += dt
        i += 1
    return phrase(notes, seed)


def gorrion(seed):
    r = dsp.rng(seed)
    f = r.uniform(0.92, 1.08)
    return bird_note([(0, 4300 * f), (0.02, 5300 * f), (0.06, 3900 * f)], 0.06, harm=((1, 1.0), (2, 0.25)), seed=seed)


def torcaza(seed):
    """Eared dove: soft low 'hu-HUUU-hu-hu'."""
    soft = dict(harm=((1, 1.0), (2, 0.22), (3, 0.04)))
    y = phrase([(0.0, 0.13, [(0, 520), (0.13, 540)], 0.6, soft),
                (0.22, 0.38, [(0, 560), (0.12, 625), (0.38, 560)], 1.0, soft),
                (0.68, 0.14, [(0, 525), (0.14, 515)], 0.6, soft),
                (0.9, 0.14, [(0, 505), (0.14, 495)], 0.55, soft)], seed)
    return dsp.lowpass(y, 1600, 2) + 0.03 * dsp.lowpass(bp(white(len(y), seed + 9), 400, 1500), 1500, 2) * smooth(np.abs(y), 0.02) * 8


def zorzal(seed):
    """Rufous-bellied thrush: a short fluted phrase on a few notes with slides."""
    r = dsp.rng(seed)
    scale = [2000, 2300, 2650, 3000, 3400]
    notes, t = [], 0.0
    for k in range(int(r.integers(4, 7))):
        f0 = scale[int(r.integers(0, 5))] * r.uniform(0.98, 1.02)
        f1 = f0 * r.choice([0.85, 1.0, 1.15])
        d = r.uniform(0.08, 0.2)
        notes.append((t, d, [(0, f0), (d, f1)], r.uniform(0.6, 1.0), dict(harm=((1, 1.0), (2, 0.18), (3, 0.05)))))
        t += d + r.uniform(0.03, 0.08)
    return phrase(notes, seed)


def colectivo(seed, dur=7.5):
    """A far city bus pulling away from the stop: air brakes, diesel climbing, a gear change, gone round the corner."""
    n = N(dur)
    t = taxis(n)
    rpm = np.interp(t, [0, 1.0, 1.4, 4.4, 4.7, 6.5, dur], [700, 700, 1100, 1850, 1150, 1700, 1600])
    f = rpm / 60 * 3      # 6 cylinders, 4-stroke
    idx, a = stick_slip(n, f, seed, 0.12, None, 0.7)
    kern = (np.sin(TWO_PI * 120 * taxis(N(0.025))) * np.exp(-taxis(N(0.025)) / 0.006)).astype(np.float32)
    eng = pulse_train(n, idx, a, kern)
    eng = dsp.lowpass(eng, 650, 2) + 0.15 * dsp.lowpass(np.sin(TWO_PI * np.cumsum(f * 8) / SR).astype(np.float32), 900, 2)
    load = env_pts(n, [(0, 0.5), (1.0, 0.5), (1.4, 1.0), (4.4, 1.0), (4.6, 0.6), (5.0, 1.0), (dur, 0.9)])
    away = env_pts(n, [(0, 0.8), (1.5, 1.0), (4.0, 0.9), (dur - 1.5, 0.45), (dur, 0)])
    out = norm(eng) * load * away
    nb = N(0.6)
    psst = bp(white(nb, seed + 1), 1500, 6000) * env_pts(nb, [(0, 0), (0.02, 1), (0.6, 0)])
    add(out, psst, 0.35, 0.25)
    return dsp.lowpass(out, 900, 2)


def morning_birds():
    L = N(20.0)
    buf = np.zeros((L + N(4.0), 2), np.float32)
    r = dsp.rng(4400)
    # benteveos on the left (the neighbour's lemon tree), horneros on the right (their mud oven on the lamp post)
    for k, (tb, p) in enumerate([(1.2, -0.5), (9.8, -0.42), (16.4, -0.58)]):
        addp(buf, benteveo(4401 + k, r.uniform(0.97, 1.03)), tb, 0.42, p)
    addp(buf, hornero(4410, 2.3), 5.4, 0.45, 0.45)
    addp(buf, hornero(4411, 1.9, 0.86, 0.06), 5.75, 0.35, 0.5)
    # sparrows hopping about close by, in little bunches
    for b in range(5):
        tb, p = r.uniform(0, 20), r.uniform(-0.8, 0.8)
        for j in range(int(r.integers(3, 8))):
            addp(buf, gorrion(4420 + 10 * b + j), tb + j * r.uniform(0.12, 0.35), r.uniform(0.15, 0.3), p + r.uniform(-0.15, 0.15))
    # eared doves cooing further off, a thrush practising
    for k, tb in enumerate([3.0, 13.2]):
        addp(buf, torcaza(4480 + k), tb, 0.3, 0.22)
    for k, tb in enumerate([8.0, 11.3, 14.7, 18.2]):
        addp(buf, dsp.lowpass(zorzal(4490 + k), 6000, 2), tb, 0.22, -0.12)
    # a far, far chorus of other birds (tiny chirps, heavily filtered)
    for j in range(70):
        f = r.uniform(2800, 5200)
        ch = bird_note([(0, f), (0.04, f * r.uniform(0.85, 1.2))], r.uniform(0.03, 0.08), seed=4500 + j)
        addp(buf, dsp.lowpass(ch, 3500, 2), r.uniform(0, 20), r.uniform(0.02, 0.06), r.uniform(-1, 1))
    # the 7:10 colectivo pulling away two blocks down, crossing from left to right
    bus = colectivo(4600)
    nb_ = len(bus)
    pans = np.linspace(-0.7, 0.35, nb_)
    a = (pans + 1) * np.pi / 4
    st = np.stack([bus * np.cos(a), bus * np.sin(a)], 1).astype(np.float32)
    add(buf, st, 10.6, 0.16)
    y = fold(buf, L)
    # morning air and the far avenue, built periodic
    airL = cfilt(white(L, 4700), lambda f: hp2(f, 120) * lp2(f, 2200) / np.sqrt(np.maximum(f, 20) / 200))
    airR = cfilt(white(L, 4701), lambda f: hp2(f, 120) * lp2(f, 2200) / np.sqrt(np.maximum(f, 20) / 200))
    swell = 1 + 0.3 * csnoise(L, 0.15, 4702)
    traffic = cfilt(white(L, 4703), lambda f: hp2(f, 40) * lp2(f, 320)) * (1 + 0.35 * csnoise(L, 0.1, 4704))
    bed = np.stack([norm(airL) * swell + 0.6 * norm(traffic), norm(airR) * swell + 0.6 * norm(traffic)], 1)
    y = y + 0.022 * bed
    return verb_st(y, 'barrio', wet=0.14, circular=True)


# ====================================================================== 33. the house at night (stereo loop)
DOG_V = np.array([(900, 200, 1.0), (1700, 260, 0.7), (2800, 330, 0.35), (4000, 420, 0.15)], np.float64)
CLOCK_TICK = [(2300, 140, 1.0), (3900, 170, 0.7), (5600, 220, 0.4)]
CLOCK_CASE = [(420, 45, 1.0), (880, 60, 0.6), (1500, 80, 0.3)]
PIPE = [(180, 18, 1.0), (410, 24, 0.6), (760, 32, 0.35), (1300, 45, 0.2)]


def bark(seed, f0=520.0, dur=0.16, scale=1.0):
    n = N(dur)
    f = contour(n, [(0, f0 * 0.75), (0.03, f0 * 1.2), (dur, f0 * 0.85)])
    amp = env_pts(n, [(0, 0), (0.01, 1.0), (0.6 * dur, 0.7), (dur, 0)])
    fr = ftrack(n, [(0, DOG_V * [scale, 1, 1])])
    y = vsynth(f, fr, amp, tilt=0.9, rough=0.5, rough_hz=60, breath=0.45, fmax=6000, seed=seed)
    return norm(y)


def dog_far(seed, times, f0, scale=1.0):
    r = dsp.rng(seed)
    end = max(times) + 0.5
    out = np.zeros(N(end), np.float32)
    for k, tb in enumerate(times):
        add(out, bark(seed + k, f0 * r.uniform(0.95, 1.05), r.uniform(0.13, 0.19), scale), tb, r.uniform(0.7, 1.0))
    return dsp.lowpass(out, 2200, 2)


def ambient_casa():
    T = 60.0
    L = N(T)
    buf = np.zeros((L + N(4.0), 2), np.float32)       # interior events (go through the house reverb)
    outside = np.zeros((L + N(6.0), 2), np.float32)   # barrio events (their own long, dark air)
    r = dsp.rng(4800)
    t = taxis(L)
    # --- the fridge in the kitchen (left, through a wall): kicks in at 9 s, runs, shudders off at 41 s
    on0, on1 = 9.0, 41.0
    ramp = smoothstep((t - on0) / 0.3) * (1 - smoothstep((t - on1) / 0.25))
    fr_hz = np.maximum(1.0, FRIDGE_HZ * np.where(t < on1, smoothstep((t - on0) / 0.3), np.exp(-np.maximum(0, t - on1) / 0.35)))
    motor = dsp.lowpass(fridge_motor(fr_hz, 4801, rattle=0.25), 420, 2) * np.maximum(ramp, (t > on1) * np.exp(-np.maximum(0, t - on1) / 0.35) * (t < on1 + 1.5))
    motor *= 1 + 0.08 * csnoise(L, 0.3, 4802)
    addp(buf, motor.astype(np.float32), 0.0, 0.017, -0.55)
    for tk, s in [(on0 - 0.02, 4803), (on1 + 0.7, 4804)]:
        addp(buf, dsp.lowpass(knock(s, [(70, 18, 1.0), (125, 24, 0.8), (210, 30, 0.5), (390, 45, 0.3)], 0.45,
                                    contact=0.007, click=0.0), 800, 2), tk, 0.05, -0.55)
    addp(buf, dsp.lowpass(knock(4805, [(1800, 70, 1), (3300, 90, .6)], 0.06, contact=0.0003, click=0.5), 2500, 2), on0 - 0.05, 0.03, -0.55)
    # --- the living-room clock (right): tick-tock, 60 per loop, with the escapement's little double click
    for k in range(60):
        tk = k + 0.37
        hi = k % 2 == 0
        tick = knock(4810 + (k % 2), scale_modes(CLOCK_TICK, 1.0 if hi else 0.86), 0.06, contact=0.00018, click=0.6, amt=0.0)
        case = knock(4812 + (k % 2), CLOCK_CASE, 0.12, contact=0.0006, click=0.0, amt=0.0)
        y = np.zeros(N(0.15), np.float32)
        add(y, tick, 0.0, 1.0)
        add(y, tick, 0.006, 0.35)
        add(y, case, 0.0, 0.35)
        addp(buf, y, tk, 0.03 * (1.0 if hi else 0.85), 0.38)
    # --- the house settling: floorboards upstairs, beams and roof tiles ticking, a pipe knocking in the wall
    for k, (tc, p) in enumerate([(6.5, 0.2), (24.2, -0.3), (38.8, 0.5), (55.0, -0.1)]):
        c = creak(r.uniform(0.35, 0.7), 4820 + k, [(0, r.uniform(25, 40)), (0.2, r.uniform(55, 80)), (0.6, 30)],
                  detune(CHAIR_JOINT, r, 0.2), [(0, 0), (0.08, 1.0), (0.35, 0.6), (0.7, 0)])
        addp(buf, dsp.lowpass(norm(c), 3000, 2), tc, 0.045, p)
    for k in range(14):
        f = r.uniform(900, 2600)
        tic = knock(4830 + k, [(f, 90, 1), (f * 2.3, 120, .5)], 0.05, contact=0.0004, click=0.4)
        addp(buf, tic, r.uniform(0, T), r.uniform(0.012, 0.03), r.uniform(-0.8, 0.8))
    for k, tp in enumerate([44.5, 44.68, 44.79]):
        addp(buf, dsp.lowpass(knock(4850 + k, PIPE, 0.6, contact=0.002, click=0.2), 1500, 2), tp, 0.05 * 0.7 ** k, -0.2)
    nw = N(0.9)       # a gust rattles a window pane in its putty
    rat = np.zeros(nw, np.float32)
    for k in range(9):
        add(rat, glass_ping(4860 + k, r.uniform(1800, 3200), decay=90, click=0.3), 0.08 * k + r.uniform(0, 0.02), 0.6 * np.sin(np.pi * (k + 0.5) / 9))
    addp(buf, rat, 34.0, 0.025, 0.6)
    # --- outside: dogs answering each other across the barrio, crickets, the avenue
    addp(outside, dog_far(4870, [0, 0.42, 0.8, 1.45, 1.85], 560), 14.0, 0.06, -0.6)
    addp(outside, dog_far(4880, [0, 0.55, 1.05], 430, 0.85), 31.0, 0.05, 0.7)
    addp(outside, dog_far(4885, [0, 0.4], 560), 32.6, 0.04, -0.6)
    addp(outside, dog_far(4890, [0, 0.35, 0.7, 1.6], 700, 1.15), 51.5, 0.03, 0.3)
    for c, (f, p, rate) in enumerate([(4650, -0.75, 2.4), (4380, 0.7, 2.1)]):
        tc = r.uniform(0, 0.5)
        while tc < T:
            ch = np.zeros(N(0.12), np.float32)
            for j in range(3):
                add(ch, np.sin(TWO_PI * f * taxis(N(0.018))) * np.sin(np.pi * np.arange(N(0.018)) / N(0.018)), 0.03 * j, 1.0)
            addp(outside, ch, tc, 0.016 * r.uniform(0.7, 1.0), p)
            tc += 1 / rate + r.uniform(-0.05, 0.08) + (r.uniform(1.5, 4.0) if r.random() < 0.08 else 0)
    for k, (tcar, p0, p1) in enumerate([(21.0, -0.8, 0.8), (47.0, 0.7, -0.7)]):
        nc = N(7.0)
        car = dsp.lowpass(colored(nc, 'pink', 4900 + k), 700, 2) * env_pts(nc, [(0, 0), (3.5, 1.0), (7.0, 0)]) ** 2
        pans = np.linspace(p0, p1, nc)
        a = (pans + 1) * np.pi / 4
        add(outside, np.stack([car * np.cos(a), car * np.sin(a)], 1).astype(np.float32), tcar, 0.025)
    inside = verb_st(fold(buf, L), 'casa_noche', wet=0.22, circular=True)
    outdoor = verb_st(fold(outside, L), 'barrio', wet=0.3, circular=True)
    outdoor = cfilt(outdoor, lambda f: lp2(f, 4500))         # heard through the walls and the closed persianas
    # room tone and the far avenue, periodic by construction
    tone = np.stack([cfilt(white(L, 4910 + c), lambda f: hp2(f, 40) * lp2(f, 1200) / np.sqrt(np.maximum(f, 20) / 100))
                     for c in range(2)], 1)
    avenue = cfilt(white(L, 4912), lambda f: hp2(f, 35) * lp2(f, 300)) * (1 + 0.4 * csnoise(L, 0.05, 4913))
    bed = 0.012 * tone / (np.max(np.abs(tone)) + 1e-9) + 0.018 * norm(avenue)[:, None]
    return (inside + outdoor + bed).astype(np.float32)


# ====================================================================== event table + build
EVENTS = {  # event -> ([variant builders], peak dBFS, loop)
    'casa.breaker_trip': ([breaker_trip], -3.0, False),
    'casa.breaker_reset': ([breaker_reset], -3.0, False),
    'casa.tv_novela': ([tv_novela], -4.0, True),
    'casa.tv_static': ([tv_static], -4.0, True),
    'grill.sizzle': ([grill_sizzle], -4.0, True),
    'fire.blue_whoosh': ([fire_blue_whoosh], -0.5, False),
    'knife.lift': ([lambda: knife_lift(1), lambda: knife_lift(2)], -3.0, False),
    'knife.whoosh': ([lambda v=v: knife_whoosh(v) for v in (1, 2, 3)], -3.0, False),
    'knife.impact': ([lambda v=v: knife_impact(v) for v in (1, 2, 3)], -3.0, False),
    'salt.hit_scream': ([salt_hit_scream], -0.5, False),
    'pool.splash': ([pool_splash], -3.0, False),
    'plate.whoosh': ([lambda v=v: plate_whoosh(v) for v in (1, 2, 3, 4)], -3.0, False),
    'plate.shatter': ([lambda v=v: plate_shatter(v) for v in (1, 2, 3)], -3.0, False),
    'plate.storm': ([plate_storm], -3.0, False),
    'mate.slide': ([mate_slide], -3.0, False),
    'mate.sip_empty': ([mate_sip_empty], -3.0, False),
    'termo.fly': ([termo_fly], -3.0, False),
    'alacena.golpe': ([lambda v=v: alacena_golpe(v) for v in (1, 2, 3)], -3.0, False),
    'chair.stack': ([chair_stack], -3.0, False),
    'door.slam_cascade': ([door_slam_cascade], -0.5, False),
    'bulb.pop': ([lambda: bulb_pop(1), lambda: bulb_pop(2)], -3.0, False),
    'doll.turn': ([lambda v=v: doll_turn(v) for v in (1, 2, 3)], -3.0, False),
    'doll.giggle_chorus': ([doll_giggle_chorus], -1.0, False),
    'andador.squeak': ([lambda v=v: andador_squeak(v) for v in (1, 2, 3)], -3.0, False),
    'chancleta.whip': ([chancleta_whip], -3.0, False),
    'chancleta.hit': ([chancleta_hit], -0.5, False),
    'rocking.creak_slow': ([rocking_creak_slow], -4.0, True),
    'yarn.twang': ([lambda: yarn_twang(1), lambda: yarn_twang(2)], -3.0, False),
    'yarn.snap': ([yarn_snap], -3.0, False),
    'stitch.pull': ([lambda v=v: stitch_pull(v) for v in (1, 2, 3)], -3.0, False),
    'azamel.suck': ([azamel_suck], -0.5, False),
    'candles.out': ([candles_out], -3.0, False),
    'wall.break': ([wall_break], -0.5, False),
    'wisp.whistle': ([wisp_whistle], -3.0, False),
    'kettle.whistle': ([kettle_whistle], -3.0, False),
    'morning.birds': ([morning_birds], -4.0, True),
    'ambient.casa': ([ambient_casa], -4.0, True),
}


def rel_paths(name):
    k = SOUNDS[name][0]
    base = name.replace('.', '/')
    return [base + (f'_{i + 1}' if k > 1 else '') for i in range(k)]


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
            # Vorbis can overshoot dense material by ~1 dB: re-master if the decoded peak lands over target
            over = 20 * np.log10(np.max(np.abs(sf.read(path, dtype='float32')[0])) + 1e-12) - pk
            if over > 0.3:
                x = finish(raw, pk - (over - 0.1), loop)
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
    print(f'casa sfx group done in {time.time() - t_all:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1:] or None)
