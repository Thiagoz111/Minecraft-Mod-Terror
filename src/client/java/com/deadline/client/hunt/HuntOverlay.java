package com.deadline.client.hunt;

import com.deadline.client.ClientState;
import com.deadline.horror.casa.hunt.HideSpots;
import com.deadline.horror.casa.hunt.HuntHudPayload;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.Mth;

/**
 * The hunt's screen layers. Under the HUD: the view from inside a hiding place (the wardrobe's slats -- dark wood with
 * thin horizontal slits of light --, the low gap under a bed, the bathtub curtain, the trunk's keyhole, the crack of a
 * pantry door), pulsing darker with the heartbeat as she comes near; when she searches the place the door is open and
 * only a black frame is left round her face. On top: the lungs bar under the noise meter (only while not full) and the
 * frame of a 3D jumpscare.
 */
final class HuntOverlay {
	private HuntOverlay() {
	}

	// ---------------------------------------------------------------- inside a hiding place
	static void renderHide(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || !HuntClient.hidden()) {
			return;
		}
		float pt = dt.getGameTimeDeltaPartialTick(false);
		int w = g.guiWidth();
		int h = g.guiHeight();
		float in = Mth.clamp((HuntClient.hideTicks + pt) / 8F, 0F, 1F);
		float d = HuntClient.nonaShown;
		float close = d < 0F ? 0F : Mth.clamp(1F - (d - 2F) / 14F, 0F, 1F);
		float t = ClientState.ticks + pt;
		// the heartbeat in the dark: two quick pulses per beat, faster as she comes closer
		float bpm = 70F + 70F * close;
		float ph = (t / 20F * bpm / 60F) % 1F;
		float beat = (float) (Math.exp(-Math.pow((ph - 0.08F) / 0.04F, 2)) + 0.6F * Math.exp(-Math.pow((ph - 0.24F) / 0.05F, 2)));
		float pulse = beat * (0.06F + 0.22F * close);
		boolean searched = HuntClient.flag(HuntHudPayload.SEARCHED);
		float open = Mth.clamp(HuntClient.searchedTicks / 4F, 0F, 1F);
		HideSpots.Type type = HideSpots.Type.of(HuntClient.hide);
		if (searched) {
			// the door is open: only a black frame and the dark, she is right THERE
			frame(g, w, h, (int) (w * 0.12F), 0.96F * in);
			g.fill(0, 0, w, h, a(0.25F * open + pulse) );
			return;
		}
		switch (type) {
			case WARDROBE -> slats(g, w, h, in, pulse, t, 9, 0.30F);
			case DOOR -> crack(g, w, h, in, pulse, t);
			case BED -> underBed(g, w, h, in, pulse, t);
			case TUB -> curtain(g, w, h, in, pulse, t);
			case CHEST -> keyhole(g, w, h, in, pulse);
			default -> {
			}
		}
	}

	/** ARGB black with alpha 0..1. */
	private static int a(float alpha) {
		return ((int) (Mth.clamp(alpha, 0F, 1F) * 255F)) << 24;
	}

	private static int argb(float alpha, int rgb) {
		return a(alpha) | (rgb & 0xFFFFFF);
	}

	/** Wardrobe: louvred slats of dark wood; between them thin slits through which the room shows. */
	private static void slats(GuiGraphics g, int w, int h, float in, float pulse, float t, int count, float gap) {
		int pitch = Math.max(8, h / count);
		int slit = Math.max(2, (int) (pitch * gap));
		int y0 = (int) (h * 0.5F) % pitch;
		// the slats (dark varnished wood, a lit lower edge where the room's light catches them)
		for (int y = y0 - pitch; y < h; y += pitch) {
			int top = y + slit;
			int bottom = y + pitch;
			g.fill(0, Math.max(0, top), w, Math.min(h, bottom), argb(0.97F * in, 0x0B0705));
			g.fill(0, Math.max(0, bottom - 2), w, Math.min(h, bottom - 1), argb(0.55F * in, 0x2A1A10));
			g.fill(0, Math.max(0, top), w, Math.min(h, top + 1), argb(0.6F * in, 0x000000));
			// the slit itself is dimmed a little: you peek through dust
			g.fill(0, Math.max(0, y), w, Math.min(h, top), argb((0.28F + pulse) * in, 0x050302));
		}
		// the door frame / the other leaf at the sides, darker toward the edges
		frame(g, w, h, (int) (w * 0.08F), 0.98F * in);
		g.fillGradient(0, 0, w, h / 5, argb(0.6F * in, 0), argb(0F, 0));
	}

	/** Pantry / shed door: almost black; a thin vertical crack of light and a sliver under the door. */
	private static void crack(GuiGraphics g, int w, int h, float in, float pulse, float t) {
		int cx = (int) (w * 0.56F);
		int cw = Math.max(3, w / 90);
		g.fill(0, 0, cx, h, argb(0.97F * in, 0x060403));
		g.fill(cx + cw, 0, w, h, argb(0.97F * in, 0x060403));
		g.fill(cx, 0, cx + cw, h, argb((0.35F + pulse) * in, 0x000000));
		int under = (int) (h * 0.94F);
		g.fill(0, under, cx, h, argb(0.82F * in, 0x060403));
		g.fill(cx + cw, under, w, h, argb(0.82F * in, 0x060403));
	}

	/** Under a bed: the slats and the mattress over you, the floor of the room in a low gap of light. */
	private static void underBed(GuiGraphics g, int w, int h, float in, float pulse, float t) {
		int gapTop = (int) (h * 0.62F);
		int gapBottom = (int) (h * 0.93F);
		g.fill(0, 0, w, gapTop, argb(0.97F * in, 0x070504));
		// the bed's slats seen from below
		for (int x = w / 14; x < w; x += w / 7) {
			g.fill(x, 0, x + w / 40, gapTop, argb(0.5F * in, 0x1A120C));
		}
		g.fillGradient(0, gapTop, w, gapTop + h / 12, argb(0.9F * in, 0x070504), argb((0.25F + pulse) * in, 0));
		g.fill(0, gapTop + h / 12, w, gapBottom, argb((0.18F + pulse) * in, 0));
		g.fill(0, gapBottom, w, h, argb(0.96F * in, 0x050403));
		// the legs of the bed at the sides of the gap
		g.fill((int) (w * 0.06F), gapTop, (int) (w * 0.11F), gapBottom, argb(0.95F * in, 0x0E0907));
		g.fill((int) (w * 0.89F), gapTop, (int) (w * 0.94F), gapBottom, argb(0.95F * in, 0x0E0907));
		// a dangling sheet corner
		g.fill((int) (w * 0.3F), gapTop, (int) (w * 0.42F), gapTop + h / 9, argb(0.85F * in, 0x2C2924));
	}

	/** Bathtub: a dirty, half-translucent shower curtain with folds, swaying; open a little at one edge. */
	private static void curtain(GuiGraphics g, int w, int h, float in, float pulse, float t) {
		int edge = (int) (w * 0.09F + Math.sin(t * 0.05F) * w * 0.01F);
		int folds = 16;
		int fw = Math.max(4, (w - edge) / folds);
		for (int i = 0; i < folds + 1; i++) {
			int x = edge + i * fw + (int) (Math.sin(t * 0.04F + i * 0.9F) * 3F);
			float shade = 0.55F + 0.25F * (float) Math.sin(i * 1.7F + t * 0.03F);
			g.fill(x, 0, x + fw, h, argb((0.70F + pulse) * in * shade + 0.25F * in, 0x2F2D26));
			g.fill(x + fw - 2, 0, x + fw, h, argb(0.5F * in, 0x0D0C0A));
		}
		// mould and a rusty brown stain at the bottom of the curtain
		g.fillGradient(0, (int) (h * 0.7F), w, h, argb(0.0F, 0x2A1A0C), argb(0.75F * in, 0x2A1A0C));
		g.fill(0, 0, edge, h, argb((0.35F + pulse) * in, 0));
	}

	/** Trunk: black, but for the keyhole of the lid. */
	private static void keyhole(GuiGraphics g, int w, int h, float in, float pulse) {
		int cx = w / 2;
		int cy = (int) (h * 0.46F);
		int r = Math.max(6, h / 26);
		int top = cy - r;
		int bottom = cy + r * 3;
		int black = argb(0.985F * in, 0x020101);
		g.fill(0, 0, w, top, black);
		g.fill(0, bottom, w, h, black);
		for (int y = top; y < bottom; y++) {
			int half;
			if (y < cy + r) {
				double dy = y + 0.5 - cy;
				half = (int) Math.sqrt(Math.max(0.0, r * r - dy * dy));
			} else {
				half = (int) (r * 0.45F + (y - (cy + r)) * 0.22F);
			}
			g.fill(0, y, cx - half, y + 1, black);
			g.fill(cx + half, y, w, y + 1, black);
		}
		g.fill(cx - r * 2, top, cx + r * 2, bottom, argb((0.15F + pulse) * in, 0));
	}

	private static void frame(GuiGraphics g, int w, int h, int border, float alpha) {
		g.fillGradient(0, 0, w, border, argb(alpha, 0), argb(0F, 0));
		g.fillGradient(0, h - border, w, h, argb(0F, 0), argb(alpha, 0));
		for (int i = 0; i < border; i += 2) {
			float k = 1F - (float) i / border;
			g.fill(i, 0, i + 2, h, argb(alpha * k, 0));
			g.fill(w - i - 2, 0, w - i, h, argb(alpha * k, 0));
		}
	}

	// ---------------------------------------------------------------- on top: lungs bar, jumpscare frame
	static void renderFront(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) {
			return;
		}
		float pt = dt.getGameTimeDeltaPartialTick(false);
		int w = g.guiWidth();
		int h = g.guiHeight();
		if (Jumpscare3D.active()) {
			float k = Jumpscare3D.progress(pt);
			frame(g, w, h, (int) (w * 0.18F), 0.9F);
			if (((ClientState.ticks / 2) % 3) == 0) {
				g.fill(0, 0, w, h, argb(0.12F * (1F - k), 0x400000));
			}
		}
		if (!mc.options.hideGui) {
			lungs(g, w, h, pt);
		}
	}

	/** A thin bar under the noise meter (StoryHud: x 8, y h-92, 64 wide): the air left while holding the breath. */
	private static void lungs(GuiGraphics g, int w, int h, float pt) {
		float b = HuntClient.breathShown;
		boolean holding = HuntClient.flag(HuntHudPayload.HOLDING);
		boolean spent = HuntClient.flag(HuntHudPayload.SPENT);
		if (b > 99.5F && !holding) {
			return;
		}
		int x = 8;
		int y = h - 81;
		int bw = 64;
		g.fill(x, y, x + bw, y + 5, 0xAA000000);
		// two tiny lobes
		int lc = holding ? 0xFFDCE8F2 : 0x88DCE8F2;
		g.fill(x + 2, y + 1, x + 5, y + 4, lc);
		g.fill(x + 6, y + 1, x + 9, y + 4, lc);
		g.fill(x + 5, y, x + 6, y + 2, lc);
		float v = Mth.clamp(b / 100F, 0F, 1F);
		int col = v > 0.5F ? 0xFF9FC6E0 : v > 0.25F ? 0xFFFFC23A : 0xFFE5384A;
		if (spent && (ClientState.ticks / 3) % 2 == 0) {
			col = 0xFFFF2A2A;
		}
		g.fill(x + 12, y + 1, x + 12 + (int) (50 * v), y + 4, col);
	}
}
