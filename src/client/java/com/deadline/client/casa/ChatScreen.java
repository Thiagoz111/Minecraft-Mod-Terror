package com.deadline.client.casa;

import com.deadline.DeadLine;
import com.deadline.casa.CasaNet;
import com.deadline.casa.CasaNet.ChatMsg;
import com.deadline.client.ClientFx;
import com.deadline.client.ClientState;
import com.deadline.client.hud.StoryHud;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;

/**
 * Marta's phone open on the family group (a WhatsApp-like chat: bubbles, times, names, date chips). Live messages
 * arrive after a few seconds of "escribiendo..." with a notification. Closing it tells the server ("chat:closed").
 */
public class ChatScreen extends Screen {
	private static final Identifier FRAME = DeadLine.id("textures/gui/phone/frame.png");
	private static final Identifier CRACK = DeadLine.id("textures/gui/phone/crack.png");
	private static final Identifier APPS = DeadLine.id("textures/gui/phone/apps.png");

	private static final int FW = 192;
	private static final int FH = 352;
	private static final int SX = 8;
	private static final int SY = 22;
	private static final int SW = 176;
	private static final int SH = 308;
	/** Header, message area and input bar (phone coordinates). */
	private static final int HY = SY + 12;
	private static final int BT = HY + 24;
	private static final int BB = SY + SH - 24;
	private static final int TYPING_TICKS = 36;

	private static final int BG = 0xFF0B141A;
	private static final int BAR = 0xFF1F2C34;
	private static final int IN = 0xFF1F2C34;
	private static final int OUT = 0xFF005C4B;
	private static final int TEXT = 0xFFE9EDEF;
	private static final int GREY = 0xFF8696A0;

	// the conversation (kept while the screen is closed, replaced by the next OPEN)
	private static String titleKey = "";
	private static String membersKey = "";
	private static final List<ChatMsg> MESSAGES = new ArrayList<>();
	private static final List<ChatMsg> PENDING = new ArrayList<>();
	private static int typing;
	private static int liveIndex = -1;
	private static int liveAge;
	private static ChatMsg banner;
	private static int bannerTicks;
	private static float scroll;
	private static boolean silentClose;

	private int age;
	private float scale = 1F;
	private int ox;
	private int oy;

	public ChatScreen() {
		super(Component.translatable("deadline.casa.chat.title"));
	}

	/** The family chat with "ya llegó?" just in, already open (screenshots: ClientSmoke). */
	public static ChatScreen preview() {
		titleKey = "deadline.casa.chat.title";
		membersKey = "deadline.casa.chat.members";
		MESSAGES.clear();
		MESSAGES.addAll(CasaNet.familyChat());
		ChatMsg m = CasaNet.yaLlego();
		MESSAGES.add(new ChatMsg(m.from(), m.text(), m.date(), "03:33", m.flags()));
		PENDING.clear();
		typing = 0;
		liveIndex = MESSAGES.size() - 1;
		liveAge = 40;
		scroll = 0F;
		ChatScreen s = new ChatScreen();
		s.age = 20;
		return s;
	}

	// ------------------------------------------------------------------ network
	public static void onPayload(CasaNet.ChatPayload p) {
		Minecraft mc = Minecraft.getInstance();
		switch (p.mode()) {
			case CasaNet.ChatPayload.OPEN -> {
				String[] t = p.title().split("\n", 2);
				titleKey = t[0];
				membersKey = t.length > 1 ? t[1] : "";
				MESSAGES.clear();
				MESSAGES.addAll(p.messages());
				PENDING.clear();
				typing = 0;
				liveIndex = -1;
				bannerTicks = 0;
				scroll = 0F;
				if (!(mc.screen instanceof ChatScreen)) {
					if (blocked(mc)) {
						// the history is kept, but the phone cannot come up now: the server must not wait for it
						CasaClientNet.send(CasaNet.ActionPayload.CHAT_CLOSED, "");
					} else {
						mc.setScreen(new ChatScreen());
					}
				}
			}
			case CasaNet.ChatPayload.LIVE -> {
				PENDING.addAll(p.messages());
				if (mc.screen instanceof ChatScreen) {
					if (typing <= 0) {
						typing = TYPING_TICKS;
					}
				} else if (blocked(mc)) {
					deliver(true);  // it just arrives (sound and jolt); nothing is open, so the beat goes on
					CasaClientNet.send(CasaNet.ActionPayload.CHAT_CLOSED, "");
				} else {
					mc.setScreen(new ChatScreen());  // over the hunter's own phone, the inventory, a container...
					typing = TYPING_TICKS;
				}
			}
			case CasaNet.ChatPayload.CLOSE -> {
				if (mc.screen instanceof ChatScreen) {
					silentClose = true;
					mc.setScreen(null);
				}
			}
			default -> {
			}
		}
	}

	/**
	 * The chat must not come up now: no hunter (or a dead one), or the name / spirit box choice is on screen (the server
	 * is waiting for that answer, and those screens are never replaced by the chat).
	 */
	private static boolean blocked(Minecraft mc) {
		return mc.player == null || !mc.player.isAlive() || mc.screen instanceof NameScreen || mc.screen instanceof SpiritWheelScreen;
	}

	/** Every client tick, open or not: the typing delay, the notification banner. */
	public static void tickAlways(Minecraft mc) {
		if (typing > 0 && --typing == 0) {
			deliver(true);
		}
		if (liveAge < 10000) {
			liveAge++;
		}
		if (bannerTicks > 0) {
			bannerTicks--;
		}
	}

	public static void reset() {
		MESSAGES.clear();
		PENDING.clear();
		titleKey = membersKey = "";
		typing = bannerTicks = 0;
		liveIndex = -1;
		scroll = 0F;
		banner = null;
		silentClose = false;
	}

	/** The waiting live messages land: stamped with the phone clock, a notification and a jolt. */
	private static void deliver(boolean loud) {
		if (PENDING.isEmpty()) {
			return;
		}
		String now = clock();
		for (ChatMsg m : PENDING) {
			ChatMsg landed = m.time().isEmpty() ? new ChatMsg(m.from(), m.text(), m.date(), now, m.flags()) : m;
			MESSAGES.add(landed);
			banner = landed;
		}
		PENDING.clear();
		typing = 0;
		liveIndex = MESSAGES.size() - 1;
		liveAge = 0;
		scroll = 0F;
		if (loud) {
			bannerTicks = 80;
			Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.PHONE_NOTIFY, 1.0F, 1.0F));
			ClientFx.shake(0.45F, 10);
		}
	}

	private static String clock() {
		Minecraft mc = Minecraft.getInstance();
		long tod = mc.level == null ? 18000 : (mc.level.getDayTime() + 6000) % 24000;
		return String.format(Locale.ROOT, "%02d:%02d", tod / 1000, (tod % 1000) * 60 / 1000);
	}

	// ------------------------------------------------------------------ screen
	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void tick() {
		age++;
	}

	@Override
	public void removed() {
		if (typing > 0) {
			deliver(false);  // closed while it was typing: the message is there next time
		}
		if (!silentClose) {
			CasaClientNet.send(CasaNet.ActionPayload.CHAT_CLOSED, "");
		}
		silentClose = false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		float k = Mth.clamp((age + pt) / 6F, 0F, 1F);
		g.fillGradient(0, 0, width, height, (int) (k * 0x70) << 24, (int) (k * 0xC0) << 24);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		scale = Math.min(1F, (height - 8) / (float) FH);
		float slide = Mth.clamp((age + pt) / 7F, 0F, 1F);
		float ease = 1F - (1F - slide) * (1F - slide) * (1F - slide);
		ox = Math.round((width - FW * scale) / 2F);
		oy = Math.round((height - FH * scale) / 2F + (1F - ease) * height * 0.7F);

		g.pose().pushMatrix();
		g.pose().translate(ox, oy);
		g.pose().scale(scale, scale);
		g.fill(SX, SY, SX + SW, SY + SH, BG);
		drawWallpaper(g);
		drawMessages(g, pt);
		drawHeader(g);
		drawInput(g);
		drawStatusBar(g);
		drawBanner(g, pt);
		if (ClientState.sanityShown < 35F) {
			int a = (int) (Mth.clamp((35F - ClientState.sanityShown) / 25F, 0F, 1F) * 255);
			g.blit(RenderPipelines.GUI_TEXTURED, CRACK, SX, SY, 0F, 0F, SW, SH, SW, SH, a << 24 | 0xFFFFFF);
		}
		if (liveIndex >= 0 && liveAge < 14 && liveAge % 4 < 2) {
			int gy = SY + (int) ((ClientState.ticks * 53) % SH);
			g.fill(SX, gy, SX + SW, gy + 2, 0x66FF2030);
		}
		g.blit(RenderPipelines.GUI_TEXTURED, FRAME, 0, 0, 0F, 0F, FW, FH, FW, FH);
		g.pose().popMatrix();
	}

	// ------------------------------------------------------------------ pieces
	private void drawStatusBar(GuiGraphics g) {
		g.fill(SX, SY, SX + SW, SY + 12, 0xFF0B141A);
		g.drawString(font, clock(), SX + 5, SY + 2, 0xFFFFFFFF, false);
		g.drawString(font, "4G", SX + SW - 58, SY + 2, 0xFFFFFFFF, false);
		for (int i = 0; i < 4; i++) {
			g.fill(SX + SW - 42 + i * 4, SY + 9 - (i + 1) * 2, SX + SW - 39 + i * 4, SY + 9, i < 2 ? 0xFFFFFFFF : 0x44FFFFFF);
		}
		// Marta's battery: 12%
		g.renderOutline(SX + SW - 20, SY + 3, 13, 7, 0xFFFFFFFF);
		g.fill(SX + SW - 7, SY + 5, SX + SW - 6, SY + 8, 0xFFFFFFFF);
		g.fill(SX + SW - 18, SY + 5, SX + SW - 16, SY + 8, 0xFFE33A3A);
	}

	private void drawHeader(GuiGraphics g) {
		g.fill(SX, HY, SX + SW, HY + 24, BAR);
		g.drawString(font, "‹", SX + 5, HY + 8, TEXT, false);
		disc(g, SX + 22, HY + 12, 8, 0xFF6A7175);
		g.drawCenteredString(font, "M", SX + 22, HY + 8, 0xFFFFFFFF);
		Component title = StoryHud.text(titleKey);
		g.drawString(font, font.plainSubstrByWidth(title.getString(), SW - 40), SX + 34, HY + 3, TEXT, false);
		String sub;
		int subColor;
		if (typing > 0 && !PENDING.isEmpty()) {
			sub = Component.translatable("deadline.casa.chat.typing", name(PENDING.get(0).from())).getString();
			subColor = 0xFF00A884;
		} else {
			sub = StoryHud.text(membersKey).getString();
			subColor = GREY;
		}
		small(g, font.plainSubstrByWidth(sub, (int) ((SW - 40) / 0.75F)), SX + 34, HY + 14, subColor);
	}

	private void drawInput(GuiGraphics g) {
		g.fill(SX, BB, SX + SW, SY + SH, BG);
		g.fill(SX + 4, BB + 4, SX + SW - 24, BB + 20, IN);
		g.fill(SX + 5, BB + 3, SX + SW - 25, BB + 4, IN);
		g.fill(SX + 5, BB + 20, SX + SW - 25, BB + 21, IN);
		g.drawString(font, Component.translatable("deadline.casa.chat.input"), SX + 11, BB + 8, GREY, false);
		int mx = SX + SW - 12;
		int my = BB + 12;
		disc(g, mx, my, 8, 0xFF00A884);
		// microphone
		g.fill(mx - 1, my - 5, mx + 2, my + 1, 0xFFFFFFFF);
		g.fill(mx - 3, my - 1, mx - 2, my + 2, 0xFFFFFFFF);
		g.fill(mx + 2, my - 1, mx + 3, my + 2, 0xFFFFFFFF);
		g.fill(mx - 2, my + 2, mx + 2, my + 3, 0xFFFFFFFF);
		g.fill(mx, my + 3, mx + 1, my + 5, 0xFFFFFFFF);
	}

	private void drawWallpaper(GuiGraphics g) {
		int off = (int) (scroll * 0.3F) % 16;
		for (int y = BT + 4 + off - 16; y < BB; y += 16) {
			if (y < BT) {
				continue;
			}
			for (int x = SX + 6 + ((y / 16) % 2) * 8; x < SX + SW; x += 16) {
				g.fill(x, y, x + 1, y + 1, 0x14FFFFFF);
			}
		}
	}

	/** One laid-out line of the chat: a date chip or a bubble. */
	private record Row(ChatMsg msg, int index, String chip, List<FormattedCharSequence> lines, boolean head, int w, int h, boolean inlineTime) {
	}

	private void drawMessages(GuiGraphics g, float pt) {
		List<Row> rows = new ArrayList<>();
		int total = 6;
		String lastDate = null;
		String lastFrom = null;
		for (int i = 0; i < MESSAGES.size(); i++) {
			ChatMsg m = MESSAGES.get(i);
			if (!m.date().equals(lastDate)) {
				lastDate = m.date();
				lastFrom = null;
				Row chip = new Row(null, -1, m.date().isEmpty() ? Component.translatable("deadline.casa.chat.today").getString() : m.date(),
						List.of(), false, 0, 18, false);
				rows.add(chip);
				total += chip.h;
			}
			boolean head = !m.from().equals(lastFrom);
			lastFrom = m.from();
			Row r = layout(m, i, head);
			rows.add(r);
			total += r.h + (head ? 4 : 2);
		}
		boolean showTyping = typing > 0 && !PENDING.isEmpty();
		if (showTyping) {
			total += 22;
		}
		int view = BB - BT;
		float max = Math.max(0, total - view);
		scroll = Mth.clamp(scroll, 0F, max);
		int y = BB - total + (int) scroll;
		for (Row r : rows) {
			if (r.msg == null) {
				if (y + r.h > BT - 20 && y < BB) {
					int cw = font.width(r.chip) + 10;
					int cx = SX + SW / 2;
					g.fill(cx - cw / 2, y + 4, cx + cw / 2, y + 15, 0xFF182229);
					g.drawCenteredString(font, r.chip, cx, y + 6, GREY);
				}
				y += r.h;
				continue;
			}
			y += r.head ? 4 : 2;
			if (y + r.h > BT - 30 && y < BB && y >= 0 && y + r.h <= FH) {
				drawBubble(g, r, y, pt);
			}
			y += r.h;
		}
		if (showTyping) {
			y += 4;
			ChatMsg m = PENDING.get(0);
			int x = SX + 20;
			avatar(g, m, SX + 9, y + 6);
			g.fill(x, y, x + 30, y + 14, IN);
			for (int i = 0; i < 3; i++) {
				float bob = (float) Math.sin((ClientState.ticks + pt) * 0.5F - i * 0.9F);
				int dy = bob > 0.3F ? -1 : 0;
				g.fill(x + 8 + i * 6, y + 6 + dy, x + 11 + i * 6, y + 9 + dy, bob > 0.3F ? 0xFFD0D7DB : GREY);
			}
		}
	}

	private Row layout(ChatMsg m, int index, boolean head) {
		boolean mine = m.is(ChatMsg.MINE);
		int maxW = mine ? SW - 56 : SW - 62;
		List<FormattedCharSequence> lines = font.split(StoryHud.text(m.text()), maxW);
		int textW = 0;
		for (FormattedCharSequence l : lines) {
			textW = Math.max(textW, font.width(l));
		}
		int timeW = timeWidth(m);
		int last = lines.isEmpty() ? 0 : font.width(lines.get(lines.size() - 1));
		boolean inline = last + 6 + timeW <= maxW;
		int w = Math.max(textW, inline ? last + 6 + timeW : timeW);
		boolean named = head && !mine;
		if (named) {
			w = Math.max(w, font.width(name(m.from())));
		}
		if (m.is(ChatMsg.PHOTO)) {
			w = Math.max(w, 72);
		}
		int h = 6 + lines.size() * 10 + (inline ? 0 : 8) + (named ? 10 : 0) + (m.is(ChatMsg.PHOTO) ? 76 : 0);
		return new Row(m, index, null, lines, head, w + 8, h, inline);
	}

	private int timeWidth(ChatMsg m) {
		int w = (int) Math.ceil(font.width(m.time()) * 0.75F);
		return m.is(ChatMsg.MINE) ? w + 11 : w;
	}

	private void drawBubble(GuiGraphics g, Row r, int y, float pt) {
		ChatMsg m = r.msg;
		boolean mine = m.is(ChatMsg.MINE);
		boolean live = r.index == liveIndex && liveAge < 100;
		int x = mine ? SX + SW - 6 - r.w : SX + 20;
		if (live && liveAge < 8) {
			float k = Mth.clamp((liveAge + pt) / 8F, 0F, 1F);
			x -= (int) ((1F - k * (2F - k)) * 40);
		}
		int col = mine ? OUT : IN;
		g.fill(x, y, x + r.w, y + r.h, col);
		// the little tail on the first bubble of a run
		if (r.head) {
			if (mine) {
				g.fill(x + r.w, y, x + r.w + 4, y + 1, col);
				g.fill(x + r.w, y + 1, x + r.w + 2, y + 3, col);
			} else {
				g.fill(x - 4, y, x, y + 1, col);
				g.fill(x - 2, y + 1, x, y + 3, col);
				avatar(g, m, SX + 9, y + 6);
			}
		}
		if (live) {
			float pulse = 0.5F + 0.5F * (float) Math.sin((liveAge + pt) * 0.35F);
			int a = (int) (Mth.clamp(1F - liveAge / 100F, 0F, 1F) * (120 + 135 * pulse));
			g.renderOutline(x - 1, y - 1, r.w + 2, r.h + 2, a << 24 | 0xE33A3A);
		}
		int ty = y + 3;
		if (r.head && !mine) {
			g.drawString(font, name(m.from()), x + 4, ty, color(m.from()), false);
			ty += 10;
		}
		if (m.is(ChatMsg.PHOTO)) {
			g.fill(x + 3, ty, x + r.w - 3, ty + 72, 0xFF000000);
			dollPhoto(g, x + (r.w - 64) / 2, ty + 4);
			ty += 76;
		}
		for (FormattedCharSequence l : r.lines) {
			g.drawString(font, l, x + 4, ty, TEXT, false);
			ty += 10;
		}
		int tw = timeWidth(m);
		int tx = x + r.w - 4 - tw;
		int tyy = y + r.h - 8;
		small(g, m.time(), tx, tyy, mine ? 0xFF99BEB7 : GREY);
		if (mine) {
			small(g, "✓✓", x + r.w - 13, tyy, 0xFF53BDEB);
		}
	}

	private void avatar(GuiGraphics g, ChatMsg m, int cx, int cy) {
		if (m.is(ChatMsg.LOGO)) {
			g.fill(cx - 6, cy - 6, cx + 7, cy + 7, 0xFF120406);
			g.blit(RenderPipelines.GUI_TEXTURED, APPS, cx - 6, cy - 6, 0F, 0F, 13, 13, 32, 32, 128, 32);
			return;
		}
		disc(g, cx, cy, 6, color(m.from()));
		String n = name(m.from());
		String initial = n.isEmpty() ? "?" : n.substring(0, 1).toUpperCase(Locale.ROOT);
		g.drawString(font, initial, cx + 1 - font.width(initial) / 2, cy - 3, 0xFF0B141A, false);
	}

	private void drawBanner(GuiGraphics g, float pt) {
		if (bannerTicks <= 0 || banner == null) {
			return;
		}
		float life = 80 - bannerTicks + pt;
		float in = Mth.clamp(life / 6F, 0F, 1F);
		float out = Mth.clamp((bannerTicks - pt) / 8F, 0F, 1F);
		float k = Math.min(in, out);
		int y = SY + 2 - (int) ((1F - k) * 34);
		g.fill(SX + 4, y, SX + SW - 4, y + 28, 0xF2202C33);
		g.renderOutline(SX + 4, y, SW - 8, 28, 0x40FFFFFF);
		g.fill(SX + 8, y + 6, SX + 24, y + 22, 0xFF120406);
		g.blit(RenderPipelines.GUI_TEXTURED, APPS, SX + 8, y + 6, 0F, 0F, 16, 16, 32, 32, 128, 32);
		small(g, "DEAD LINE · " + banner.time(), SX + 28, y + 4, 0xFFE33A3A);
		g.drawString(font, font.plainSubstrByWidth(name(banner.from()), SW - 40), SX + 28, y + 10, TEXT, false);
		String txt = StoryHud.text(banner.text()).getString();
		small(g, font.plainSubstrByWidth(txt, (int) ((SW - 40) / 0.75F)), SX + 28, y + 20, 0xFFD0D7DB);
	}

	/** Marta's photo of Ofelia at the fair stall (16x16, 4 px a dot): the broken eye, the mouth still sewn. */
	private static final String[] DOLL = {
			".,..,hhhhhh,..,.", "...hhhhhhhhhh...", "..hhHhhhhhhHhh..", "..hHssssssssHh..",
			".hhssssssssskhh.", ".hsssssssssksSh.", ".hssewsssseksSh.", ".hsseesssseeSsh.",
			".hpsssssssssSph.", ".hsssrsrsrsSssh.", ".hssskkkkkksSsh.", ".hSssrsrsrssSSh.",
			"..hSsssssssSSh..", "..dlSSssssSSlD..", ".ddllllllllllDD.", "dddDddddddddDDDD"};

	private static void dollPhoto(GuiGraphics g, int x, int y) {
		for (int j = 0; j < DOLL.length; j++) {
			String row = DOLL[j];
			for (int i = 0; i < row.length(); i++) {
				int c = switch (row.charAt(i)) {
					case ',' -> 0xFF4A3426;
					case 'h' -> 0xFF6A3C1A;
					case 'H' -> 0xFF42240F;
					case 's' -> 0xFFECE2D6;
					case 'S' -> 0xFFC8B8A8;
					case 'e' -> 0xFF3B6FC0;
					case 'w' -> 0xFFFFFFFF;
					case 'k' -> 0xFF141010;
					case 'r' -> 0xFFC0141E;
					case 'p' -> 0xFFE8A4A0;
					case 'd' -> 0xFF8A1A22;
					case 'D' -> 0xFF5A0E14;
					case 'l' -> 0xFFE8E0D0;
					default -> 0xFF3A2A22;
				};
				g.fill(x + i * 4, y + j * 4, x + i * 4 + 4, y + j * 4 + 4, c);
			}
		}
		// a phone photo: a little washed out at the top
		g.fillGradient(x, y, x + 64, y + 24, 0x30FFF4E0, 0x00FFF4E0);
	}

	// ------------------------------------------------------------------ helpers
	private void small(GuiGraphics g, String s, int x, int y, int color) {
		g.pose().pushMatrix();
		g.pose().translate(x, y);
		g.pose().scale(0.75F, 0.75F);
		g.drawString(font, s, 0, 0, color, false);
		g.pose().popMatrix();
	}

	private static void disc(GuiGraphics g, int cx, int cy, int r, int color) {
		for (int dy = -r; dy <= r; dy++) {
			int half = (int) Math.round(Math.sqrt(r * r - dy * dy));
			g.fill(cx - half, cy + dy, cx + half + 1, cy + dy + 1, color);
		}
	}

	private static String name(String from) {
		if (from.startsWith("#")) {
			return from.substring(1);
		}
		return Component.translatable("deadline.casa.chat.from." + from).getString();
	}

	private static int color(String from) {
		return switch (from) {
			case "jorge" -> 0xFF53BDEB;
			case "nona" -> 0xFFE5A445;
			case "toti" -> 0xFF7AD06B;
			case "lucia" -> 0xFFFF7EB6;
			case "unknown" -> 0xFFE33A3A;
			case "marta" -> 0xFFF15C6D;
			default -> 0xFFB0B8BE;
		};
	}

	// ------------------------------------------------------------------ input
	@Override
	public boolean mouseClicked(MouseButtonEvent e, boolean dbl) {
		double lx = (e.x() - ox) / scale;
		double ly = (e.y() - oy) / scale;
		boolean back = lx >= SX && lx < SX + 40 && ly >= HY && ly < HY + 24;
		boolean home = lx >= 74 && lx < 118 && ly >= 334 && ly < 346;
		if (back || home) {
			Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1.2F));
			onClose();
			return true;
		}
		return super.mouseClicked(e, dbl);
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		scroll += (float) sy * 16F;
		return true;
	}
}
