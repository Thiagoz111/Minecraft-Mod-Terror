package com.deadline.client.hud;

import com.deadline.client.ClientState;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;

/**
 * HUD of the scripted cases: objective checklist, subtitle bar with the speaker's name, reprimand stamps, the noise
 * meter, chapter title cards and big centred texts (prayers, the file, the diary).
 */
public final class StoryHud {
	private StoryHud() {
	}

	// checklist
	public static String place = "";
	public static String chapterKey = "";
	public static int chapter;
	public static final List<String> objKeys = new ArrayList<>();
	public static final List<Boolean> objDone = new ArrayList<>();
	public static int checklistFlash;

	// subtitle
	public static String speakerKey = "";
	public static String lineKey = "";
	public static int subTicks;
	public static int subTotal = 1;

	// stamp
	public static String stampKey = "";
	public static int stampTotal;
	public static int stampTicks;
	public static final int STAMP_LEN = 70;

	// noise meter
	public static float noise;
	public static float noiseShown;
	public static int noiseFlags;
	public static int noiseTicks;

	// big text
	public static String bigKey = "";
	public static int bigTicks;
	public static int bigTotal = 1;
	public static float bigProgress = -1F;

	// chapter card
	public static String cardTitle = "";
	public static String cardSub = "";
	public static int cardTicks;
	public static int cardTotal = 1;

	public static boolean active() {
		return !chapterKey.isEmpty();
	}

	public static void reset() {
		place = chapterKey = speakerKey = lineKey = stampKey = bigKey = cardTitle = cardSub = "";
		objKeys.clear();
		objDone.clear();
		subTicks = stampTicks = noiseTicks = bigTicks = cardTicks = checklistFlash = 0;
	}

	public static void onChecklist(String s, int ch) {
		String[] parts = s.split("\n");
		place = parts.length > 0 ? parts[0] : "";
		chapterKey = parts.length > 1 ? parts[1] : "";
		boolean changed = ch != chapter;
		chapter = ch;
		List<String> keys = new ArrayList<>();
		List<Boolean> done = new ArrayList<>();
		for (int i = 2; i < parts.length; i++) {
			int eq = parts[i].lastIndexOf('=');
			keys.add(eq > 0 ? parts[i].substring(0, eq) : parts[i]);
			done.add(eq > 0 && parts[i].endsWith("=1"));
		}
		if (!keys.equals(objKeys) || !done.equals(objDone)) {
			changed = true;
		}
		objKeys.clear();
		objKeys.addAll(keys);
		objDone.clear();
		objDone.addAll(done);
		if (changed) {
			checklistFlash = 40;
		}
	}

	public static void tick() {
		if (checklistFlash > 0) {
			checklistFlash--;
		}
		if (subTicks > 0) {
			subTicks--;
		}
		if (stampTicks > 0) {
			stampTicks--;
		}
		if (noiseTicks > 0) {
			noiseTicks--;
		}
		if (bigTicks > 0) {
			bigTicks--;
		}
		if (cardTicks > 0) {
			cardTicks--;
		}
		noiseShown += (noise - noiseShown) * 0.25F;
	}

	/** "key" or "key|arg|arg" -> translatable component; "#text" -> literal. */
	public static Component text(String s) {
		if (s == null || s.isEmpty()) {
			return Component.empty();
		}
		if (s.startsWith("#")) {
			return Component.literal(s.substring(1));
		}
		String[] p = s.split("\\|");
		if (p.length == 1) {
			return Component.translatable(p[0]);
		}
		Object[] args = new Object[p.length - 1];
		System.arraycopy(p, 1, args, 0, args.length);
		return Component.translatable(p[0], args);
	}

	static int speakerColor(String key) {
		String k = key.substring(key.lastIndexOf('.') + 1);
		return switch (k) {
			case "madre" -> 0xFFD7C38A;
			case "clara" -> 0xFFF0A46E;
			case "monja" -> 0xFFE5384A;
			case "alumna", "paloma", "coro" -> 0xFFA8DCF0;
			case "cura" -> 0xFFC9B48E;
			case "operadora" -> 0xFF7FFFD4;
			default -> 0xFFF2ECE4;
		};
	}

	// ------------------------------------------------------------------ rendering
	public static void render(GuiGraphics g, Font font, int w, int h, float pt) {
		if (active()) {
			renderChecklist(g, font);
		}
		renderNoise(g, font, w, h);
		renderSubtitle(g, font, w, h, pt);
		renderBigText(g, font, w, h, pt);
		renderCard(g, font, w, h, pt);
		renderStamp(g, font, w, h, pt);
	}

	private static void renderChecklist(GuiGraphics g, Font font) {
		int x = 6;
		int y = ClientState.vhs ? 22 : 6;
		int pw = 184;
		List<List<FormattedCharSequence>> lines = new ArrayList<>();
		int rows = 0;
		for (String k : objKeys) {
			List<FormattedCharSequence> l = font.split(text(k), pw - 26);
			lines.add(l);
			rows += l.size();
		}
		int ph = 28 + rows * 10 + objKeys.size() * 2 + 4;
		g.fillGradient(x, y, x + pw, y + ph, 0xB00A0608, 0x50000000);
		boolean flash = checklistFlash > 0 && (checklistFlash / 4) % 2 == 0;
		g.fill(x, y, x + 2, y + ph, flash ? 0xFFFFFFFF : 0xFFB3121B);
		g.drawString(font, text(place), x + 7, y + 4, 0xFFE33A3A, true);
		g.drawString(font, text(chapterKey), x + 7, y + 15, 0xFFF2ECE4, false);
		int cy = y + 28;
		for (int i = 0; i < objKeys.size(); i++) {
			boolean done = objDone.get(i);
			int bx = x + 8;
			g.fill(bx, cy + 1, bx + 7, cy + 8, done ? 0xFFB3121B : 0x66FFFFFF);
			g.fill(bx + 1, cy + 2, bx + 6, cy + 7, done ? 0xFFB3121B : 0xCC0A0608);
			if (done) {
				g.fill(bx + 2, cy + 4, bx + 3, cy + 6, 0xFFFFFFFF);
				g.fill(bx + 3, cy + 5, bx + 4, cy + 7, 0xFFFFFFFF);
				g.fill(bx + 4, cy + 2, bx + 5, cy + 6, 0xFFFFFFFF);
			}
			for (FormattedCharSequence l : lines.get(i)) {
				g.drawString(font, l, x + 19, cy, done ? 0x88B8B0A8 : 0xFFE8E2D8, false);
				if (done) {
					g.fill(x + 19, cy + 4, x + 19 + font.width(l), cy + 5, 0x99B3121B);
				}
				cy += 10;
			}
			cy += 2;
		}
	}

	private static void renderSubtitle(GuiGraphics g, Font font, int w, int h, float pt) {
		if (subTicks <= 0 || lineKey.isEmpty()) {
			return;
		}
		float life = subTotal - subTicks + pt;
		float a = Mth.clamp(Math.min(life / 4F, (subTicks - pt) / 8F), 0F, 1F);
		if (a <= 0.02F) {
			return;
		}
		int alpha = (int) (a * 255) << 24;
		int maxW = Math.min(340, w - 40);
		List<FormattedCharSequence> lines = font.split(text(lineKey), maxW);
		Component who = text(speakerKey);
		boolean hasWho = !who.getString().isEmpty();
		int bw = 0;
		for (FormattedCharSequence l : lines) {
			bw = Math.max(bw, font.width(l));
		}
		if (hasWho) {
			bw = Math.max(bw, font.width(who));
		}
		int bh = lines.size() * 10 + (hasWho ? 11 : 0) + 6;
		int bx = (w - bw) / 2 - 6;
		int by = h - 70 - bh;
		g.fill(bx, by, bx + bw + 12, by + bh, ((int) (a * 0xA8)) << 24);
		int yy = by + 4;
		if (hasWho) {
			g.drawString(font, who, (w - font.width(who)) / 2, yy, alpha | (speakerColor(speakerKey) & 0xFFFFFF), true);
			yy += 11;
		}
		for (FormattedCharSequence l : lines) {
			g.drawString(font, l, (w - font.width(l)) / 2, yy, alpha | 0xF2ECE4, false);
			yy += 10;
		}
	}

	private static void renderStamp(GuiGraphics g, Font font, int w, int h, float pt) {
		if (stampTicks <= 0 || stampKey.isEmpty()) {
			return;
		}
		float life = STAMP_LEN - stampTicks + pt;
		float a = Mth.clamp((stampTicks - pt) / 12F, 0F, 1F);
		float slam = life < 5 ? 2.2F - life * 0.24F : 1F;
		boolean good = stampKey.endsWith("felicitacion");
		int col = good ? 0x2FAF4A : 0xC8102E;
		int alpha = (int) (a * 230) << 24;
		Component head = good ? text(stampKey) : Component.translatable("deadline.hud.amonestacion");
		g.pose().pushMatrix();
		g.pose().translate(w * 0.74F, h * 0.36F);
		g.pose().rotate((float) Math.toRadians(-9));
		g.pose().scale(slam * 1.6F, slam * 1.6F);
		int tw = font.width(head);
		g.fill(-tw / 2 - 6, -6, tw / 2 + 6, 12, alpha | 0x150505);
		g.fill(-tw / 2 - 6, -6, tw / 2 + 6, -5, alpha | col);
		g.fill(-tw / 2 - 6, 11, tw / 2 + 6, 12, alpha | col);
		g.fill(-tw / 2 - 6, -6, -tw / 2 - 5, 12, alpha | col);
		g.fill(tw / 2 + 5, -6, tw / 2 + 6, 12, alpha | col);
		g.drawString(font, head, -tw / 2, 0, alpha | col, false);
		g.pose().popMatrix();
		if (!good) {
			Component reason = text(stampKey);
			int rw = Math.min(font.width(reason), 220);
			List<FormattedCharSequence> rl = font.split(reason, 220);
			int ry = (int) (h * 0.36F) + 22;
			for (FormattedCharSequence l : rl) {
				g.drawString(font, l, (int) (w * 0.74F) - font.width(l) / 2, ry, alpha | 0xF2ECE4, true);
				ry += 10;
			}
			Component count = Component.translatable("deadline.hud.amonestaciones", stampTotal);
			g.drawString(font, count, (int) (w * 0.74F) - font.width(count) / 2, ry + 2, alpha | 0xE33A3A, true);
			if (rw < 0) {
				return;
			}
		}
	}

	private static void renderNoise(GuiGraphics g, Font font, int w, int h) {
		if (noiseTicks <= 0) {
			return;
		}
		int x = 8;
		int y = h - 92;
		boolean heard = (noiseFlags & 1) != 0;
		boolean mic = (noiseFlags & 2) != 0;
		float v = Mth.clamp(noiseShown / 100F, 0F, 1F);
		g.fill(x, y, x + 64, y + 9, 0xAA000000);
		int col = v > 0.55F ? 0xFFE5384A : v > 0.3F ? 0xFFFFC23A : 0xFF8CFFB0;
		g.fill(x + 12, y + 3, x + 12 + (int) (50 * v), y + 6, col);
		g.fill(x + 12 + 27, y + 2, x + 12 + 28, y + 7, 0x88FFFFFF);
		// microphone glyph
		int mc = mic ? 0xFFF2ECE4 : 0x66F2ECE4;
		g.fill(x + 3, y + 1, x + 7, y + 6, mc);
		g.fill(x + 2, y + 5, x + 8, y + 6, mc);
		g.fill(x + 4, y + 6, x + 6, y + 8, mc);
		if (heard && (ClientState.ticks / 5) % 2 == 0) {
			Component t = Component.translatable("deadline.hud.te_escucha");
			g.drawString(font, t, x + 68, y + 1, 0xFFE5384A, true);
		}
	}

	private static void renderBigText(GuiGraphics g, Font font, int w, int h, float pt) {
		if (bigTicks <= 0 || bigKey.isEmpty()) {
			return;
		}
		float life = bigTotal - bigTicks + pt;
		float a = Mth.clamp(Math.min(life / 8F, (bigTicks - pt) / 10F), 0F, 1F);
		if (a <= 0.02F) {
			return;
		}
		int alpha = (int) (a * 255) << 24;
		float scale = 1.6F;
		int maxW = (int) ((w * 0.7F) / scale);
		List<FormattedCharSequence> lines = font.split(text(bigKey).copy().withStyle(Style.EMPTY), maxW);
		int lh = 11;
		int total = lines.size() * lh;
		g.fill(0, (int) (h * 0.42F - total * scale / 2 - 14), w, (int) (h * 0.42F + total * scale / 2 + 18), ((int) (a * 0xB0)) << 24);
		g.pose().pushMatrix();
		g.pose().translate(w / 2F, h * 0.42F - total * scale / 2F);
		g.pose().scale(scale, scale);
		int yy = 0;
		for (FormattedCharSequence l : lines) {
			g.drawString(font, l, -font.width(l) / 2, yy, alpha | 0xF4EEDF, true);
			yy += lh;
		}
		g.pose().popMatrix();
		if (bigProgress >= 0F) {
			int bw = (int) (w * 0.5F);
			int bx = (w - bw) / 2;
			int by = (int) (h * 0.42F + total * scale / 2 + 8);
			g.fill(bx, by, bx + bw, by + 4, alpha | 0x222222);
			g.fill(bx, by, bx + (int) (bw * Mth.clamp(bigProgress, 0F, 1F)), by + 4, alpha | 0xF2D27A);
		}
	}

	private static void renderCard(GuiGraphics g, Font font, int w, int h, float pt) {
		if (cardTicks <= 0 || cardTitle.isEmpty()) {
			return;
		}
		float life = cardTotal - cardTicks + pt;
		float a = Mth.clamp(Math.min(life / 12F, (cardTicks - pt) / 18F), 0F, 1F);
		if (a <= 0.02F) {
			return;
		}
		int alpha = (int) (a * 255) << 24;
		Component title = text(cardTitle);
		Component sub = text(cardSub);
		g.fill(0, (int) (h * 0.30F), w, (int) (h * 0.30F) + 62, ((int) (a * 0x90)) << 24);
		g.pose().pushMatrix();
		g.pose().translate(w / 2F, h * 0.30F + 10);
		g.pose().scale(2.6F, 2.6F);
		int tw = font.width(title);
		g.drawString(font, title, -tw / 2, 0, alpha | 0xF2ECE4, false);
		g.pose().popMatrix();
		int lw = (int) Math.min(w * 0.5F, tw * 2.6F + 40);
		g.fill((w - lw) / 2, (int) (h * 0.30F) + 37, (w + lw) / 2, (int) (h * 0.30F) + 38, alpha | 0xB3121B);
		g.pose().pushMatrix();
		g.pose().translate(w / 2F, h * 0.30F + 44);
		g.pose().scale(1.3F, 1.3F);
		int sw = font.width(sub);
		g.drawString(font, sub, -sw / 2, 0, alpha | 0xC9C0B4, false);
		g.pose().popMatrix();
	}
}
