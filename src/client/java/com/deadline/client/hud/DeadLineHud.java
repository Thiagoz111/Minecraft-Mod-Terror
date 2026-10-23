package com.deadline.client.hud;

import com.deadline.DeadLine;
import com.deadline.client.ClientState;
import com.deadline.client.DeadLineKeys;
import com.deadline.registry.ModItems;
import java.util.List;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** In-game overlays: sanity ECG, objective, incoming text messages, VHS camera, jumpscares and screen effects. */
public final class DeadLineHud {
	private DeadLineHud() {
	}

	private static final Identifier VIGNETTE = DeadLine.id("textures/gui/overlay/vignette.png");
	private static final Identifier STATIC = DeadLine.id("textures/gui/overlay/static.png");
	private static final Identifier FIGURE = DeadLine.id("textures/gui/overlay/shadow_figure.png");
	private static final Identifier APPS = DeadLine.id("textures/gui/phone/apps.png");

	public static Identifier jumpscareTexture(String key) {
		return DeadLine.id("textures/gui/jumpscare/" + key + ".png");
	}

	/** Drawn under the chat: world-space feel effects (vignette, figure, static, VHS). */
	public static void renderBackdrop(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui && !ClientState.vhs) {
			return;
		}
		float pt = dt.getGameTimeDeltaPartialTick(false);
		int w = g.guiWidth();
		int h = g.guiHeight();
		float s = ClientState.sanityShown;

		// darkness creeping in from the edges as sanity drops
		float vig = Mth.clamp((70F - s) / 70F, 0F, 1F);
		if (vig > 0F) {
			int a = (int) (vig * 230);
			g.blit(RenderPipelines.GUI_TEXTURED, VIGNETTE, 0, 0, 0F, 0F, w, h, 256, 256, 256, 256, a << 24);
		}
		if (s < 25F) {
			float beat = (float) Math.pow(Math.max(0, Math.sin((ClientState.ticks + pt) * 0.45)), 6);
			int a = (int) ((1F - s / 25F) * 120 * beat);
			if (a > 0) {
				g.blit(RenderPipelines.GUI_TEXTURED, VIGNETTE, 0, 0, 0F, 0F, w, h, 256, 256, 256, 256, a << 24 | 0x9A0000);
			}
		}

		// a shadow at the corner of your eye
		if (ClientState.figureTicks > 0) {
			float k = ClientState.figureTicks / 34F;
			float alpha = Mth.clamp(Math.min(k, 1F - k) * 3F, 0F, 1F) * 0.85F;
			int fh = (int) (h * 0.75F);
			int fw = fh / 2;
			int x = ClientState.figureLeft ? (int) (w * 0.02F) : (int) (w * 0.98F) - fw;
			g.blit(RenderPipelines.GUI_TEXTURED, FIGURE, x, h - fh, 0F, 0F, fw, fh, 64, 128, 64, 128, ((int) (alpha * 255)) << 24 | 0xFFFFFF);
		}

		if (ClientState.vhs) {
			renderVhs(g, mc, w, h, pt);
		}

		// TV static from the spirit box / camera / entity interference
		float st = 0F;
		if (ClientState.staticTicks > 0) {
			st = ClientState.staticStrength * Math.min(1F, ClientState.staticTicks / (float) Math.min(10, ClientState.staticTotal));
		}
		if (s < 15F) {
			st = Math.max(st, (15F - s) / 15F * 0.22F * (0.6F + 0.4F * (float) Math.sin(ClientState.ticks * 0.7)));
		}
		if (st > 0.01F) {
			drawStatic(g, w, h, st);
		}
	}

	/** Drawn on top of everything: HUD panels, titles, flashes and jumpscares. */
	public static void renderFront(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		Player pl = mc.player;
		if (pl == null) {
			return;
		}
		float pt = dt.getGameTimeDeltaPartialTick(false);
		int w = g.guiWidth();
		int h = g.guiHeight();
		Font font = mc.font;

		if (!mc.options.hideGui) {
			renderSanity(g, font, h, pt);
			if (!StoryHud.active()) {
				renderObjective(g, font, w);
			}
			renderItemInfo(g, font, pl, w, h);
			renderMessageToast(g, font, w, pt);
			renderTitle(g, font, w, h, pt);
			renderCaseEnd(g, font, w, h);
			StoryHud.render(g, font, w, h, pt);
		}

		// full-screen flashes
		if (ClientState.fadeTicks > 0) {
			float k = 1F - (ClientState.fadeTicks - pt) / ClientState.fadeTotal;
			float a = k < 0.5F ? k * 2F : (1F - k) * 2F;
			g.fill(0, 0, w, h, ((int) (Mth.clamp(a * 1.4F, 0F, 1F) * 255)) << 24);
		}
		if (ClientState.redFlash > 0.01F) {
			g.fill(0, 0, w, h, ((int) (Math.min(0.8F, ClientState.redFlash) * 255)) << 24 | 0x8A0000);
		}
		if (ClientState.flash > 0.01F) {
			g.fill(0, 0, w, h, ((int) (Math.min(1F, ClientState.flash) * 255)) << 24 | 0xFFFFFF);
		}
		if (ClientState.jumpscareTicks > 0) {
			renderJumpscare(g, w, h, pt);
		}
	}

	// ------------------------------------------------------------------ sanity
	private static void renderSanity(GuiGraphics g, Font font, int h, float pt) {
		float s = ClientState.sanityShown;
		int pw = 96;
		int ph = 30;
		int x = 6;
		int y = h - ph - 6;
		if (s < 30F) {
			float j = (30F - s) / 30F;
			x += (int) ((Math.sin(ClientState.ticks * 1.7) * 1.2) * j);
			y += (int) ((Math.cos(ClientState.ticks * 2.3) * 1.2) * j);
		}
		int col = s > 60F ? 0xFF55FF8A : s > 30F ? 0xFFFFC23A : 0xFFFF3B3B;
		g.fill(x, y, x + pw, y + ph, 0x99000000);
		g.fill(x, y, x + pw, y + 1, 0x55FFFFFF & col);
		g.fill(x, y + ph - 1, x + pw, y + ph, 0x33FFFFFF & col);
		g.drawString(font, Component.translatable("deadline.hud.sanity"), x + 4, y + 3, 0xFFB8B8B8, false);
		String pct = Mth.ceil(s) + "%";
		g.drawString(font, pct, x + pw - 4 - font.width(pct), y + 3, col, false);

		// electrocardiogram: rate rises as sanity falls
		int gx = x + 4;
		int gy = y + 13;
		int gw = pw - 8;
		int gh = 14;
		g.fill(gx, gy + gh / 2, gx + gw, gy + gh / 2 + 1, 0x22FFFFFF);
		float bpm = 62F + (100F - s) * 1.15F;
		float speed = bpm / 60F / 20F;
		float now = (ClientState.ticks + pt) * speed;
		int prevY = gy + gh / 2;
		for (int i = 0; i < gw; i++) {
			float phase = now - (gw - i) * 0.012F;
			float v = ecg(phase - (float) Math.floor(phase), s);
			int py = gy + gh / 2 - Math.round(v * gh * 0.5F);
			float age = i / (float) gw;
			int a = (int) (40 + 215 * age * age);
			int c = (a << 24) | (col & 0xFFFFFF);
			int y0 = Math.min(prevY, py);
			int y1 = Math.max(prevY, py);
			g.fill(gx + i, y0, gx + i + 1, y1 + 1, c);
			prevY = py;
		}
		// leading dot
		g.fill(gx + gw - 1, prevY - 1, gx + gw + 1, prevY + 1, 0xFFFFFFFF);
	}

	/** One heartbeat of an ECG trace, t in 0..1 -> -1..1. Low sanity makes it erratic. */
	private static float ecg(float t, float sanity) {
		float v = 0F;
		v += 0.12F * bump(t, 0.12F, 0.035F);
		v -= 0.18F * bump(t, 0.23F, 0.012F);
		v += 1.00F * bump(t, 0.26F, 0.014F);
		v -= 0.35F * bump(t, 0.29F, 0.014F);
		v += 0.22F * bump(t, 0.50F, 0.05F);
		if (sanity < 30F) {
			float n = (30F - sanity) / 30F;
			v += (float) (Math.sin(t * 91.0 + ClientState.ticks * 0.3) * 0.12 * n);
		}
		return Mth.clamp(v, -1F, 1F);
	}

	private static float bump(float t, float c, float w) {
		float d = (t - c) / w;
		return (float) Math.exp(-d * d);
	}

	// ------------------------------------------------------------------ objective
	private static void renderObjective(GuiGraphics g, Font font, int w) {
		if (ClientState.objCase.isEmpty() || ClientState.objStage < 0) {
			return;
		}
		int x = 6;
		int y = ClientState.vhs ? 22 : 6;
		int pw = 170;
		Component place = Component.translatable("deadline.case." + ClientState.objCase + ".place");
		Component obj = Component.translatable(ClientState.objectiveKey(ClientState.objCase, ClientState.objStage));
		List<FormattedCharSequence> lines = font.split(obj, pw - 14);
		int ph = 16 + lines.size() * 10 + 4;
		g.fillGradient(x, y, x + pw, y + ph, 0xAA0A0608, 0x55000000);
		int accent = ClientState.objFlash > 0 && (ClientState.objFlash / 4) % 2 == 0 ? 0xFFFFFFFF : 0xFFB3121B;
		g.fill(x, y, x + 2, y + ph, accent);
		g.drawString(font, place, x + 7, y + 4, 0xFFE33A3A, true);
		for (int i = 0; i < lines.size(); i++) {
			g.drawString(font, lines.get(i), x + 7, y + 16 + i * 10, 0xFFE8E2D8, false);
		}
		// stage pips
		for (int i = 0; i < 4; i++) {
			int c = i < ClientState.objStage ? 0xFFB3121B : i == ClientState.objStage ? 0xFFFFFFFF : 0x44FFFFFF;
			g.fill(x + pw - 30 + i * 7, y + 6, x + pw - 25 + i * 7, y + 9, c);
		}
	}

	// ------------------------------------------------------------------ held tool readouts
	private static void renderItemInfo(GuiGraphics g, Font font, Player pl, int w, int h) {
		ItemStack st = pl.getMainHandItem();
		String txt = null;
		int col = 0xFFE8E2D8;
		if (st.is(ModItems.FLASHLIGHT) || st.is(ModItems.CAMERA) || st.is(ModItems.SALT) || st.is(ModItems.CRUCIFIX)) {
			if (st.getMaxDamage() > 0) {
				float f = 1F - st.getDamageValue() / (float) st.getMaxDamage();
				String label = st.is(ModItems.CAMERA) ? "FILM" : st.is(ModItems.SALT) ? "SAL" : st.is(ModItems.CRUCIFIX) ? "FE" : "BAT";
				txt = label + " " + Mth.ceil(f * 100) + "%";
				col = f > 0.5F ? 0xFF8CFFB0 : f > 0.2F ? 0xFFFFC23A : 0xFFFF3B3B;
				int bx = w / 2 + 96;
				int by = h - 20;
				g.fill(bx, by, bx + 40, by + 6, 0xAA000000);
				g.fill(bx + 1, by + 1, bx + 1 + (int) (38 * f), by + 5, col);
				g.drawString(font, txt, bx, by - 10, col, true);
			}
		}
	}

	// ------------------------------------------------------------------ incoming text message
	/** Top right banner when a text arrives (even with the phone closed): contact, first line, how to open the phone. */
	private static void renderMessageToast(GuiGraphics g, Font font, int w, float pt) {
		com.deadline.phone.PhoneMsg m = com.deadline.client.phone.ClientMessages.toastMsg;
		int ticks = com.deadline.client.phone.ClientMessages.toastTicks;
		if (ticks <= 0 || m == null || Minecraft.getInstance().screen instanceof com.deadline.client.screen.PhoneScreen) {
			return;
		}
		int pw = 172;
		int ph = 42;
		float life = com.deadline.client.phone.ClientMessages.TOAST_LEN - ticks + pt;
		float in = Mth.clamp(life / 6F, 0F, 1F);
		float out = Mth.clamp((ticks - pt) / 10F, 0F, 1F);
		float k = Math.min(1F - (1F - in) * (1F - in), out);
		int x = w - (int) ((pw + 6) * k);
		int y = 6;
		// the buzz: a short shiver while it lands
		if (life < 14F) {
			x += (int) (Math.sin((ClientState.ticks + pt) * 3.1) * 1.5);
		}
		g.fill(x, y, x + pw, y + ph, 0xE60B141A);
		g.fill(x, y, x + pw, y + 1, 0xFF00A884);
		g.renderOutline(x, y, pw, ph, 0x40FFFFFF);
		g.fill(x + 6, y + 6, x + 22, y + 22, 0xFF120406);
		g.blit(RenderPipelines.GUI_TEXTURED, APPS, x + 6, y + 6, 0F, 0F, 16, 16, 32, 32, 128, 32);
		String thread = com.deadline.client.phone.ClientMessages.toastThread;
		String name = com.deadline.client.phone.ClientMessages.name(thread).getString();
		g.drawString(font, font.plainSubstrByWidth(name, pw - 34), x + 28, y + 5, 0xFFE9EDEF, false);
		String first = com.deadline.client.phone.ClientMessages.preview(m).getString();
		g.drawString(font, font.plainSubstrByWidth(first, pw - 34), x + 28, y + 17, 0xFFB8C2C8, false);
		Component hint = Component.translatable("deadline.hud.open_phone", DeadLineKeys.PHONE.getTranslatedKeyMessage());
		g.pose().pushMatrix();
		g.pose().translate(x + 28, y + 30);
		g.pose().scale(0.75F, 0.75F);
		g.drawString(font, hint, 0, 0, 0xFF6F7C84, false);
		g.pose().popMatrix();
	}

	// ------------------------------------------------------------------ titles
	private static void renderTitle(GuiGraphics g, Font font, int w, int h, float pt) {
		if (ClientState.titleTicks <= 0 || ClientState.titleKey.isEmpty()) {
			return;
		}
		float life = ClientState.titleTotal - ClientState.titleTicks + pt;
		float a = Mth.clamp(Math.min(life / 10F, (ClientState.titleTicks - pt) / 15F), 0F, 1F);
		if (a <= 0.02F) {
			return;
		}
		Component txt = Component.translatable(ClientState.titleKey);
		boolean spirit = ClientState.titleKey.startsWith("deadline.spiritbox");
		float scale = spirit ? 2.0F : 3.0F;
		int alpha = (int) (a * 255) << 24;
		g.pose().pushMatrix();
		g.pose().translate(w / 2F, h * (spirit ? 0.62F : 0.33F));
		g.pose().scale(scale, scale);
		int tw = font.width(txt);
		// chromatic split + glitch jitter
		float jx = (ClientState.ticks % 13 == 0) ? 2F : 0F;
		g.drawString(font, txt, (int) (-tw / 2F - 0.6F - jx), 0, alpha | 0xC8102E, false);
		g.drawString(font, txt, (int) (-tw / 2F + 0.6F + jx), 0, alpha | 0x1EC8C8, false);
		g.drawString(font, txt, -tw / 2, 0, alpha | (spirit ? 0xD8E8FF : 0xF2ECE4), false);
		g.pose().popMatrix();
	}

	private static void renderCaseEnd(GuiGraphics g, Font font, int w, int h) {
		if (ClientState.endTicks <= 0) {
			return;
		}
		float k = ClientState.endTicks / 120F;
		float a = Mth.clamp(Math.min((1F - k) * 6F, k * 4F), 0F, 1F);
		int alpha = (int) (a * 255) << 24;
		int cy = (int) (h * 0.42F);
		g.fillGradient(0, cy - 26, w, cy + 30, (int) (a * 160) << 24, (int) (a * 160) << 24);
		Component head = Component.translatable(ClientState.endSolved ? "deadline.title.solved" : "deadline.hud.failed");
		g.pose().pushMatrix();
		g.pose().translate(w / 2F, cy - 18);
		g.pose().scale(2.5F, 2.5F);
		int tw = font.width(head);
		g.drawString(font, head, -tw / 2, 0, alpha | (ClientState.endSolved ? 0xE8D9A8 : 0xC8102E), true);
		g.pose().popMatrix();
		if (ClientState.endSolved && ClientState.endReward > 0) {
			Component r = Component.translatable("deadline.hud.reward", ClientState.endReward);
			g.pose().pushMatrix();
			g.pose().translate(w / 2F, cy + 12);
			g.pose().scale(1.6F, 1.6F);
			g.drawString(font, r, -font.width(r) / 2, 0, alpha | 0x6BFF8E, true);
			g.pose().popMatrix();
		}
	}

	// ------------------------------------------------------------------ VHS camera mode
	private static void renderVhs(GuiGraphics g, Minecraft mc, int w, int h, float pt) {
		Font font = mc.font;
		// scanlines
		for (int y = (int) (ClientState.ticks % 3); y < h; y += 3) {
			g.fill(0, y, w, y + 1, 0x1A000000);
		}
		// rolling tracking band
		int band = (int) ((ClientState.ticks * 2.3F + pt * 2.3F) % (h + 40)) - 20;
		g.fill(0, band, w, band + 3, 0x14FFFFFF);
		g.fill(0, band + 3, w, band + 5, 0x0C000000);
		// corner brackets
		int m = 10;
		int l = 18;
		int c = 0xCCFFFFFF;
		g.fill(m, m, m + l, m + 2, c);
		g.fill(m, m, m + 2, m + l, c);
		g.fill(w - m - l, m, w - m, m + 2, c);
		g.fill(w - m - 2, m, w - m, m + l, c);
		g.fill(m, h - m - 2, m + l, h - m, c);
		g.fill(m, h - m - l, m + 2, h - m, c);
		g.fill(w - m - l, h - m - 2, w - m, h - m, c);
		g.fill(w - m - 2, h - m - l, w - m, h - m, c);
		// REC
		if ((ClientState.ticks / 12) % 2 == 0) {
			g.fill(m + 6, m + 7, m + 12, m + 13, 0xFFE01B24);
		}
		g.drawString(font, "REC", m + 16, m + 6, 0xFFFFFFFF, true);
		long secs = (ClientState.ticks - ClientState.vhsStart) / 20;
		String tc = String.format("%02d:%02d:%02d", secs / 3600, (secs / 60) % 60, secs % 60);
		g.drawString(font, tc, m + 44, m + 6, 0xFFFFFFFF, true);
		// battery
		int bx = w - m - 34;
		g.renderOutline(bx, m + 5, 22, 10, 0xFFFFFFFF);
		g.fill(bx + 22, m + 8, bx + 24, m + 12, 0xFFFFFFFF);
		int bars = 3 - (int) ((ClientState.ticks / 1200) % 4);
		for (int i = 0; i < bars; i++) {
			g.fill(bx + 2 + i * 7, m + 7, bx + 7 + i * 7, m + 13, 0xFFFFFFFF);
		}
		// date stamp
		long day = mc.level == null ? 0 : mc.level.getDayTime();
		long tod = (day + 6000) % 24000;
		int hh = (int) (tod / 1000);
		int mm = (int) ((tod % 1000) * 60 / 1000);
		String stamp = (hh < 12 ? "AM " : "PM ") + String.format("%2d:%02d", hh % 12 == 0 ? 12 : hh % 12, mm);
		String date = "OCT. 31 1998";
		g.drawString(font, stamp, w - m - 6 - font.width(stamp), h - m - 26, 0xFFFFFFFF, true);
		g.drawString(font, date, w - m - 6 - font.width(date), h - m - 15, 0xFFFFFFFF, true);
		g.drawString(font, "SP ▶", m + 6, h - m - 15, 0xFFFFFFFF, true);
		drawStatic(g, w, h, 0.05F);
	}

	private static void drawStatic(GuiGraphics g, int w, int h, float strength) {
		long t = ClientState.ticks;
		float u = (float) ((t * 37) % 128);
		float v = (float) ((t * 91) % 128);
		int a = (int) (Mth.clamp(strength, 0F, 1F) * 255);
		g.blit(RenderPipelines.GUI_TEXTURED, STATIC, 0, 0, u, v, w, h, 128, 128, 256, 256, a << 24 | 0xFFFFFF);
	}

	// ------------------------------------------------------------------ jumpscare
	private static void renderJumpscare(GuiGraphics g, int w, int h, float pt) {
		float life = ClientState.JUMPSCARE_LEN - ClientState.jumpscareTicks + pt;
		float k = life / ClientState.JUMPSCARE_LEN;
		float zoom = 1.05F + (float) Math.pow(k, 0.5) * 0.35F;
		int size = (int) (Math.max(w, h) * zoom);
		int jx = (int) (Math.sin(life * 4.7) * 8 * (1F - k));
		int jy = (int) (Math.cos(life * 5.3) * 8 * (1F - k));
		int x = (w - size) / 2 + jx;
		int y = (h - size) / 2 + jy;
		float a = k > 0.8F ? (1F - k) / 0.2F : 1F;
		int alpha = (int) (Mth.clamp(a, 0F, 1F) * 255) << 24;
		g.fill(0, 0, w, h, alpha);
		// flicker frames
		boolean flick = ((int) life) % 5 == 3;
		int tint = flick ? 0xFF6060 : 0xFFFFFF;
		g.blit(RenderPipelines.GUI_TEXTURED, jumpscareTexture(ClientState.jumpscareKey), x, y, 0F, 0F, size, size, 512, 512, 512, 512, alpha | tint);
		drawStatic(g, w, h, 0.25F * (1F - k));
	}
}
