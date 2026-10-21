package com.deadline.client.casa;

import com.deadline.casa.CasaNet;
import com.deadline.casa.CasaNet.StitchPayload;
import com.deadline.client.ClientState;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

/**
 * The stitch ring around the crosshair: a ring of red thread that closes in while you hold your aim on Ofelia's mouth.
 * It flashes white when the stitch goes through and bursts outwards when it slips.
 */
public final class StitchOverlay {
	private static final int SEGMENTS = 48;
	private static final float R_OPEN = 34F;
	private static final float R_SHUT = 5F;
	private static final int BURST = 14;
	private static final int FLASH = 12;

	private static float progress;
	private static float shown;
	private static int stitch;
	private static int total = 3;
	private static int flags;
	/** Ticks left before the ring hides without news from the server. */
	private static int keep;
	private static int burst;
	private static float burstAt;
	private static int flash;

	private StitchOverlay() {
	}

	public static void onPayload(CasaNet.StitchPayload p) {
		if (p.progress() < 0F) {
			keep = Math.min(keep, 2);
			return;
		}
		stitch = p.stitch();
		total = Math.max(1, p.total());
		flags = p.flags();
		if ((flags & StitchPayload.FAIL) != 0) {
			burst = BURST;
			burstAt = Math.max(shown, p.progress());
			progress = shown = 0F;
			keep = 30;
			return;
		}
		if ((flags & StitchPayload.SUCCESS) != 0) {
			flash = FLASH;
			progress = shown = 1F;
			keep = FLASH + 4;
			return;
		}
		progress = p.progress();
		keep = 12;
	}

	public static void tick() {
		if (keep > 0) {
			keep--;
		}
		if (burst > 0) {
			burst--;
		}
		if (flash > 0) {
			flash--;
		}
		shown += (progress - shown) * 0.45F;
	}

	public static void reset() {
		progress = shown = 0F;
		keep = burst = flash = 0;
		flags = 0;
	}

	public static void render(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || (keep <= 0 && burst <= 0 && flash <= 0) || mc.options.hideGui) {
			return;
		}
		float pt = dt.getGameTimeDeltaPartialTick(false);
		Font font = mc.font;
		int w = g.guiWidth();
		int h = g.guiHeight();
		float cx = w / 2F;
		float cy = h / 2F;
		boolean on = (flags & StitchPayload.ON_TARGET) != 0;
		boolean cooling = (flags & StitchPayload.COOLDOWN) != 0;
		float fade = Mth.clamp((keep - pt) / 6F, 0F, 1F);

		if (burst > 0) {
			// the stitch slipped: the ring flies apart in red
			float k = 1F - (burst - pt) / BURST;
			float r = Mth.lerp(burstAt, R_OPEN, R_SHUT) + k * 46F;
			int a = (int) ((1F - k) * 255);
			for (int i = 0; i < SEGMENTS; i += 2) {
				double ang = i * Math.PI * 2 / SEGMENTS + k * 0.6;
				float jitter = (float) Math.sin(i * 12.9898 + ClientState.ticks) * 6F * k;
				dot(g, cx + (float) Math.cos(ang) * (r + jitter), cy + (float) Math.sin(ang) * (r + jitter), 2, a << 24 | 0xE01B24);
			}
			label(g, font, Component.translatable("deadline.casa.stitch.snap"), cx, cy + R_OPEN + 10, a << 24 | 0xFF3B3B);
			return;
		}
		if (flash > 0) {
			// it went through: a white ring opening out, the thread pulled tight
			float k = 1F - (flash - pt) / FLASH;
			float r = R_SHUT + k * 30F;
			int a = (int) ((1F - k) * 255);
			for (int i = 0; i < SEGMENTS; i++) {
				double ang = i * Math.PI * 2 / SEGMENTS;
				dot(g, cx + (float) Math.cos(ang) * r, cy + (float) Math.sin(ang) * r, 2, a << 24 | 0xFFFFFF);
			}
			g.fill((int) cx - 6, (int) cy, (int) cx + 7, (int) cy + 1, a << 24 | 0xD21F2B);
			label(g, font, Component.translatable("deadline.casa.stitch.done"), cx, cy + R_OPEN + 10, a << 24 | 0xF2ECE4);
			return;
		}
		float p = Mth.clamp(shown + (progress - shown) * pt * 0.45F, 0F, 1F);
		float r = Mth.lerp(p, R_OPEN, R_SHUT);
		float wobble = on ? 0F : (float) Math.sin((ClientState.ticks + pt) * 0.25F) * 1.5F;
		int lit = Math.round(p * SEGMENTS);
		int base = (int) (fade * (cooling ? 90 : 150));
		int hot = (int) (fade * 255);
		for (int i = 0; i < SEGMENTS; i++) {
			double ang = -Math.PI / 2 + i * Math.PI * 2 / SEGMENTS;
			float rr = r + wobble;
			int col;
			if (cooling) {
				col = base << 24 | ((ClientState.ticks / 3) % 2 == 0 ? 0x7A0A10 : 0x3A0508);
			} else if (i < lit) {
				col = hot << 24 | 0xD21F2B;
			} else {
				col = base << 24 | (on ? 0xF2C0C0 : 0xF2ECE4);
			}
			dot(g, cx + (float) Math.cos(ang) * rr, cy + (float) Math.sin(ang) * rr, i < lit ? 2 : 1, col);
		}
		// the mouth: a small fixed circle the ring closes onto
		for (int i = 0; i < 16; i++) {
			double ang = i * Math.PI * 2 / 16;
			dot(g, cx + (float) Math.cos(ang) * R_SHUT, cy + (float) Math.sin(ang) * R_SHUT, 1, (int) (fade * 200) << 24 | 0xFFFFFF);
		}
		int textA = (int) (fade * 255) << 24;
		if (stitch > 0) {
			label(g, font, Component.translatable("deadline.casa.stitch", stitch, total), cx, cy - R_OPEN - 16, textA | (on ? 0xFF6A6A : 0xF2ECE4));
		}
		String hint;
		if ((flags & StitchPayload.NO_KIT) != 0) {
			hint = "deadline.casa.stitch.kit";
		} else if (cooling) {
			hint = "deadline.casa.stitch.snap";
		} else if (p > 0.02F) {
			hint = "deadline.casa.stitch.hold";
		} else {
			hint = "deadline.casa.stitch.hint";
		}
		label(g, font, Component.translatable(hint), cx, cy + R_OPEN + 10, textA | (cooling ? 0xE33A3A : 0xC9C0B4));
	}

	private static void dot(GuiGraphics g, float x, float y, int size, int color) {
		int ix = Math.round(x - size / 2F);
		int iy = Math.round(y - size / 2F);
		g.fill(ix, iy, ix + size, iy + size, color);
	}

	private static void label(GuiGraphics g, Font font, Component text, float cx, float y, int color) {
		if ((color >>> 24) < 8) {
			return;
		}
		g.drawString(font, text, Math.round(cx - font.width(text) / 2F), Math.round(y), color, true);
	}
}
