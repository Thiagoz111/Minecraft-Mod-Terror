package com.deadline.voice.svc;

import com.deadline.voice.VoiceBackend;

/** Tiny DSP for voice clips (48 kHz mono 16-bit): reversal, telephone band, slow-down, demonic octave layer. */
final class Dsp {
	private Dsp() {
	}

	static short[] apply(short[] in, VoiceBackend.Effect fx) {
		float[] x = new float[in.length];
		for (int i = 0; i < in.length; i++) {
			x[i] = in[i] / 32768F;
		}
		switch (fx) {
			case REVERSED -> x = reverse(x);
			case PHONE -> x = phone(x);
			case PHONE_REVERSED -> x = phone(reverse(x));
			case SLOW -> x = resample(x, 0.7F);
			case DEMON -> {
				float[] low = resample(x, 0.6F);
				float[] out = new float[low.length];
				for (int i = 0; i < low.length; i++) {
					float dry = i < x.length ? x[i] * 0.5F : 0F;
					out[i] = (float) Math.tanh((low[i] * 1.2F + dry) * 1.8F) * 0.8F;
				}
				x = out;
			}
			default -> {
			}
		}
		short[] out = new short[(x.length / SvcBackend.FRAME + 1) * SvcBackend.FRAME];
		for (int i = 0; i < x.length; i++) {
			out[i] = (short) Math.max(-32767, Math.min(32767, x[i] * 32767F));
		}
		return out;
	}

	static float[] reverse(float[] x) {
		float[] y = new float[x.length];
		for (int i = 0; i < x.length; i++) {
			y[i] = x[x.length - 1 - i];
		}
		return y;
	}

	/** Band-pass 300-3400 Hz (two one-pole sections) with a little saturation and line hiss. */
	static float[] phone(float[] x) {
		float[] y = new float[x.length];
		float hp = 0F, lpPrev = 0F, xPrev = 0F;
		float aHp = (float) Math.exp(-2 * Math.PI * 300 / 48000.0);
		float aLp = (float) Math.exp(-2 * Math.PI * 3400 / 48000.0);
		java.util.Random r = new java.util.Random(7);
		for (int i = 0; i < x.length; i++) {
			hp = aHp * (hp + x[i] - xPrev);
			xPrev = x[i];
			lpPrev = (1 - aLp) * hp + aLp * lpPrev;
			y[i] = (float) Math.tanh(lpPrev * 2.2F) * 0.7F + (r.nextFloat() - 0.5F) * 0.012F;
		}
		return y;
	}

	/** Plays the clip at `rate` speed (rate < 1 = slower and deeper). */
	static float[] resample(float[] x, float rate) {
		int n = (int) (x.length / rate);
		float[] y = new float[n];
		for (int i = 0; i < n; i++) {
			float p = i * rate;
			int j = (int) p;
			float f = p - j;
			float a = j < x.length ? x[j] : 0F;
			float b = j + 1 < x.length ? x[j + 1] : 0F;
			y[i] = a + (b - a) * f;
		}
		return y;
	}
}
