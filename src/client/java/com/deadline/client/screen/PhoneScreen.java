package com.deadline.client.screen;

import com.deadline.DeadLine;
import com.deadline.caseload.CaseManager;
import com.deadline.client.ClientState;
import com.deadline.client.hud.DeadLineHud;
import com.deadline.client.phone.ClientMessages;
import com.deadline.net.PhoneActionPayload;
import com.deadline.net.PhoneDataPayload;
import com.deadline.phone.PhoneMessagesPayload;
import com.deadline.phone.PhoneMsg;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;
import org.lwjgl.glfw.GLFW;

/** The hunter's cursed smartphone: text messages (cases arrive as threads), the active case, a shop and the bestiary. */
public class PhoneScreen extends Screen {
	private static final Identifier FRAME = DeadLine.id("textures/gui/phone/frame.png");
	private static final Identifier WALLPAPER = DeadLine.id("textures/gui/phone/wallpaper.png");
	private static final Identifier APPS = DeadLine.id("textures/gui/phone/apps.png");
	private static final Identifier AVATARS = DeadLine.id("textures/gui/phone/avatars.png");

	private static final int FW = 192;
	private static final int FH = 352;
	private static final int SX = 8;
	private static final int SY = 22;
	private static final int SW = 176;
	private static final int SH = 308;
	private static final int TOP = SY + 12;

	private static final String[] BEASTS = {"monja", "poseida", "sombra", "muneca", "anima"};

	private enum App {
		HOME, MESSAGES, THREAD, CASE, SHOP, BESTIARY, BEAST
	}

	private record Hit(int x, int y, int w, int h, Runnable action) {
	}

	private final List<Hit> hits = new ArrayList<>();
	private App app = App.HOME;
	private int sel;
	private float scroll;
	/** The open conversation (App.THREAD) and how far it is scrolled up from the newest message. */
	private String threadId = "";
	private float chatScroll;
	private int age;
	private boolean confirmAbandon;
	private float scale = 1F;
	private int ox;
	private int oy;

	public PhoneScreen() {
		super(Component.translatable("item.deadline.phone"));
	}

	/** Opens directly on an app (used by the screenshot test). app: home|messages|thread|case|shop|bestiary|beast. */
	public static PhoneScreen at(String app, int sel) {
		PhoneScreen s = new PhoneScreen();
		s.app = App.valueOf(app.toUpperCase(java.util.Locale.ROOT));
		s.sel = sel;
		s.age = 20;
		if (s.app == App.THREAD) {
			PhoneMessagesPayload.View t = ClientMessages.at(sel);
			s.threadId = t == null ? "" : t.id();
		}
		return s;
	}

	@Override
	protected void init() {
		if (age == 0 && ClientMessages.toastTicks > 0 && ClientMessages.find(ClientMessages.toastThread) != null) {
			// a message just came in: the phone opens on it
			openThread(ClientMessages.toastThread);
		}
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void tick() {
		age++;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		float k = Mth.clamp((age + pt) / 6F, 0F, 1F);
		g.fillGradient(0, 0, width, height, (int) (k * 0x70) << 24, (int) (k * 0xC0) << 24);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		hits.clear();
		scale = Math.min(1F, (height - 8) / (float) FH);
		float slide = Mth.clamp((age + pt) / 7F, 0F, 1F);
		float ease = 1F - (1F - slide) * (1F - slide) * (1F - slide);
		ox = Math.round((width - FW * scale) / 2F);
		oy = Math.round((height - FH * scale) / 2F + (1F - ease) * height * 0.7F);

		g.pose().pushMatrix();
		g.pose().translate(ox, oy);
		g.pose().scale(scale, scale);

		g.fill(SX, SY, SX + SW, SY + SH, 0xFF050507);
		PhoneDataPayload d = ClientState.phone;
		switch (app) {
			case HOME -> drawHome(g, d);
			case MESSAGES -> drawMessages(g);
			case THREAD -> drawThread(g, pt);
			case CASE -> drawCase(g, d);
			case SHOP -> drawShop(g, d);
			case BESTIARY -> drawBestiary(g, d);
			case BEAST -> drawBeast(g, d);
		}
		drawStatusBar(g);
		g.blit(RenderPipelines.GUI_TEXTURED, FRAME, 0, 0, 0F, 0F, FW, FH, FW, FH);
		hits.add(new Hit(74, 334, 44, 12, this::goHome));
		g.pose().popMatrix();
	}

	// ------------------------------------------------------------------ common pieces
	private void drawStatusBar(GuiGraphics g) {
		g.fill(SX, SY, SX + SW, SY + 12, 0xAA000000);
		Minecraft mc = Minecraft.getInstance();
		long tod = mc.level == null ? 18000 : (mc.level.getDayTime() + 6000) % 24000;
		String time = String.format("%d:%02d", tod / 1000, (tod % 1000) * 60 / 1000);
		g.drawString(font, time, SX + 5, SY + 2, 0xFFFFFFFF, false);
		String carrier = "DEAD LINE";
		g.drawString(font, carrier, SX + SW / 2 - font.width(carrier) / 2, SY + 2, 0xFFB3121B, false);
		// signal
		for (int i = 0; i < 4; i++) {
			g.fill(SX + SW - 40 + i * 4, SY + 9 - (i + 1) * 2, SX + SW - 37 + i * 4, SY + 9, 0xFFFFFFFF);
		}
		g.renderOutline(SX + SW - 20, SY + 3, 13, 7, 0xFFFFFFFF);
		g.fill(SX + SW - 7, SY + 5, SX + SW - 6, SY + 8, 0xFFFFFFFF);
		g.fill(SX + SW - 18, SY + 5, SX + SW - 12, SY + 8, 0xFFFFFFFF);
	}

	private void header(GuiGraphics g, Component title, App back) {
		g.fill(SX, TOP, SX + SW, TOP + 20, 0xFF121218);
		g.fill(SX, TOP + 20, SX + SW, TOP + 21, 0xFF2A0A0E);
		g.drawString(font, "‹", SX + 6, TOP + 6, 0xFFE33A3A, false);
		g.drawString(font, title, SX + 16, TOP + 6, 0xFFFFFFFF, false);
		hits.add(new Hit(SX, TOP, 60, 20, () -> {
			app = back;
			scroll = 0F;
			confirmAbandon = false;
		}));
	}

	private boolean button(GuiGraphics g, int x, int y, int w, int h, Component label, int color, Runnable action) {
		g.fill(x, y, x + w, y + h, color);
		g.fill(x, y, x + w, y + 1, 0x40FFFFFF);
		g.fill(x, y + h - 1, x + w, y + h, 0x60000000);
		g.drawCenteredString(font, label, x + w / 2, y + (h - 8) / 2, 0xFFFFFFFF);
		hits.add(new Hit(x, y, w, h, action));
		return true;
	}

	private int wrap(GuiGraphics g, Component text, int x, int y, int w, int color) {
		List<FormattedCharSequence> lines = font.split(text, w);
		for (FormattedCharSequence l : lines) {
			g.drawString(font, l, x, y, color, false);
			y += 10;
		}
		return y;
	}

	private void wrapCentered(GuiGraphics g, Component text, int y, int color) {
		for (FormattedCharSequence l : font.split(text, SW - 24)) {
			g.drawString(font, l, SX + SW / 2 - font.width(l) / 2, y, color, false);
			y += 10;
		}
	}

	private static void send(int action, int arg) {
		if (ClientPlayNetworking.canSend(PhoneActionPayload.TYPE)) {
			ClientPlayNetworking.send(new PhoneActionPayload(action, arg));
		}
	}

	private void goHome() {
		app = App.HOME;
		scroll = 0F;
		confirmAbandon = false;
	}

	// ------------------------------------------------------------------ home
	private void drawHome(GuiGraphics g, PhoneDataPayload d) {
		g.blit(RenderPipelines.GUI_TEXTURED, WALLPAPER, SX, SY, 0F, 0F, SW, SH, SW, SH);
		Minecraft mc = Minecraft.getInstance();
		long dayTime = mc.level == null ? 18000 : mc.level.getDayTime();
		long tod = (dayTime + 6000) % 24000;
		String time = String.format("%d:%02d", tod / 1000, (tod % 1000) * 60 / 1000);
		g.pose().pushMatrix();
		g.pose().translate(SX + SW / 2F, SY + 26);
		g.pose().scale(3F, 3F);
		g.drawString(font, time, -font.width(time) / 2, 0, 0xEEFFFFFF, true);
		g.pose().popMatrix();
		Component day = Component.translatable("deadline.phone.day", dayTime / 24000 + 1);
		g.drawCenteredString(font, day, SX + SW / 2, SY + 56, 0xFFD8D0C8);

		// status widget
		int wy = SY + 72;
		g.fill(SX + 10, wy, SX + SW - 10, wy + 42, 0xB0101016);
		g.renderOutline(SX + 10, wy, SW - 20, 42, 0x40FFFFFF);
		g.drawString(font, Component.translatable("deadline.phone.money"), SX + 16, wy + 5, 0xFF9A9AA6, false);
		g.drawString(font, "$" + d.money(), SX + 16, wy + 16, 0xFF6BFF8E, true);
		g.drawString(font, Component.translatable("deadline.phone.solved", d.solved()), SX + 16, wy + 29, 0xFFD8D0C8, false);

		// apps
		Component[] names = {Component.translatable("deadline.phone.messages"), Component.translatable("deadline.phone.case"),
				Component.translatable("deadline.phone.shop"), Component.translatable("deadline.phone.bestiary")};
		App[] targets = {App.MESSAGES, App.CASE, App.SHOP, App.BESTIARY};
		for (int i = 0; i < 4; i++) {
			int cx = SX + 44 + (i % 2) * 88;
			int cy = SY + 140 + (i / 2) * 62;
			g.fill(cx - 19, cy - 3, cx + 19, cy + 35, 0x55000000);
			g.blit(RenderPipelines.GUI_TEXTURED, APPS, cx - 16, cy, i * 32F, 0F, 32, 32, 128, 32);
			g.drawCenteredString(font, names[i], cx, cy + 38, 0xFFFFFFFF);
			int unread = ClientMessages.unreadTotal();
			if (i == 0 && unread > 0) {
				g.fill(cx + 10, cy - 5, cx + 21, cy + 6, 0xFFE01B24);
				g.drawCenteredString(font, String.valueOf(Math.min(9, unread)), cx + 16, cy - 3, 0xFFFFFFFF);
			}
			if (i == 1 && !d.activeCase().isEmpty() && (ClientState.ticks / 10) % 2 == 0) {
				g.fill(cx + 12, cy - 3, cx + 18, cy + 3, 0xFFFFC23A);
			}
			App t = targets[i];
			hits.add(new Hit(cx - 22, cy - 4, 44, 52, () -> {
				app = t;
				scroll = 0F;
			}));
		}

		if (!d.activeCase().isEmpty()) {
			int by = SY + SH - 40;
			g.fill(SX + 10, by, SX + SW - 10, by + 28, 0xD0300A10);
			g.renderOutline(SX + 10, by, SW - 20, 28, 0x80E33A3A);
			Component place = Component.translatable("deadline.case." + d.activeCase() + ".place");
			g.drawString(font, font.plainSubstrByWidth(place.getString(), SW - 34), SX + 16, by + 5, 0xFFFFFFFF, false);
			Component line = com.deadline.client.hud.StoryHud.active() ? com.deadline.client.hud.StoryHud.text(com.deadline.client.hud.StoryHud.chapterKey)
					: Component.translatable(ClientState.objectiveKey(d.activeCase(), d.stage()));
			g.drawString(font, font.plainSubstrByWidth(line.getString(), SW - 34), SX + 16, by + 16, 0xFFFFC23A, false);
			hits.add(new Hit(SX + 10, by, SW - 20, 28, () -> app = App.CASE));
		}
	}

	// ------------------------------------------------------------------ messages (WhatsApp-like threads)
	private static final int HY = SY + 12;
	private static final int BT = HY + 24;
	private static final int BB = SY + SH - 4;
	private static final int CHAT_BG = 0xFF0B141A;
	private static final int CHAT_BAR = 0xFF1F2C34;
	private static final int BUBBLE = 0xFF1F2C34;
	private static final int TEXT = 0xFFE9EDEF;
	private static final int GREY = 0xFF8696A0;
	private static final int GREEN = 0xFF00A884;
	private static final int PHOTO_W = 112;
	private static final int PHOTO_H = 84;

	/** True while this phone shows that conversation (a message landing in it is read at once). */
	public boolean viewing(String thread) {
		return app == App.THREAD && thread.equals(threadId);
	}

	private void openThread(String id) {
		app = App.THREAD;
		threadId = id;
		chatScroll = 0F;
		ClientMessages.markRead(id);
	}

	/** Contact picture: the case avatars atlas for the known contacts, an initial on a disc for the rest. */
	private void contactAvatar(GuiGraphics g, String id, int x, int y, int size) {
		int[] cell = switch (id) {
			case "marta" -> new int[] {0, 0};
			case "ignacio" -> new int[] {1, 0};
			case "clara" -> new int[] {0, 4};
			case "desconocido" -> new int[] {3, 4};
			default -> null;
		};
		if (cell != null) {
			g.blit(RenderPipelines.GUI_TEXTURED, AVATARS, x, y, cell[0] * 32F, cell[1] * 32F, size, size, 32, 32, 160, 160);
			return;
		}
		disc(g, x + size / 2, y + size / 2, size / 2, 0xFF6A7175);
		String n = ClientMessages.name(id).getString();
		String initial = n.isEmpty() ? "?" : n.substring(0, 1).toUpperCase(java.util.Locale.ROOT);
		g.drawString(font, initial, x + size / 2 + 1 - font.width(initial) / 2, y + size / 2 - 4, 0xFF0B141A, false);
	}

	private static void disc(GuiGraphics g, int cx, int cy, int r, int color) {
		for (int dy = -r; dy <= r; dy++) {
			int half = (int) Math.round(Math.sqrt(r * r - dy * dy));
			g.fill(cx - half, cy + dy, cx + half + 1, cy + dy + 1, color);
		}
	}

	private void small(GuiGraphics g, String s, int x, int y, int color) {
		g.pose().pushMatrix();
		g.pose().translate(x, y);
		g.pose().scale(0.75F, 0.75F);
		g.drawString(font, s, 0, 0, color, false);
		g.pose().popMatrix();
	}

	private int smallWidth(String s) {
		return (int) Math.ceil(font.width(s) * 0.75F);
	}

	private void drawMessages(GuiGraphics g) {
		g.fill(SX, SY, SX + SW, SY + SH, CHAT_BG);
		header(g, Component.translatable("deadline.phone.messages"), App.HOME);
		List<PhoneMessagesPayload.View> threads = ClientMessages.THREADS;
		if (threads.isEmpty()) {
			wrapCentered(g, Component.translatable("deadline.phone.no_messages"), SY + SH / 2 - 10, 0xFF6A6A76);
			return;
		}
		int top = TOP + 24;
		int bottom = SY + SH - 4;
		int rowH = 40;
		float maxScroll = Math.max(0, threads.size() * rowH - (bottom - top));
		scroll = Mth.clamp(scroll, 0F, maxScroll);
		for (int i = 0; i < threads.size(); i++) {
			int y = top + i * rowH - (int) scroll;
			if (y < top || y + rowH - 2 > bottom) {
				continue;
			}
			PhoneMessagesPayload.View t = threads.get(i);
			g.fill(SX + 4, y, SX + SW - 4, y + rowH - 2, 0xFF111B21);
			contactAvatar(g, t.id(), SX + 7, y + 4, 30);
			PhoneMsg last = t.messages().isEmpty() ? null : t.messages().get(t.messages().size() - 1);
			String time = last == null ? "" : ClientMessages.clock(last.time());
			g.drawString(font, time, SX + SW - 8 - font.width(time), y + 6, t.unread() > 0 ? GREEN : GREY, false);
			String name = ClientMessages.name(t.id()).getString();
			g.drawString(font, font.plainSubstrByWidth(name, SW - 52 - font.width(time) - 6), SX + 42, y + 6, TEXT, false);
			boolean typing = ClientMessages.typing(t.id()) > 0;
			String prev = typing ? Component.translatable("deadline.phone.typing").getString()
					: last == null ? "" : ClientMessages.preview(last).getString();
			int prevW = SW - 52 - (t.unread() > 0 ? 18 : 0);
			g.drawString(font, font.plainSubstrByWidth(prev, prevW), SX + 42, y + 21, typing ? GREEN : GREY, false);
			if (t.unread() > 0) {
				String n = t.unread() > 99 ? "99" : String.valueOf(t.unread());
				int bx = SX + SW - 15;
				disc(g, bx, y + 24, 6, GREEN);
				g.drawString(font, n, bx + 1 - font.width(n) / 2, y + 20, 0xFF0B141A, false);
			}
			String id = t.id();
			hits.add(new Hit(SX + 4, y, SW - 8, rowH - 2, () -> openThread(id)));
		}
		if (maxScroll > 0) {
			int track = bottom - top;
			int knob = Math.max(16, (int) (track * track / (float) (track + maxScroll)));
			int ky = top + (int) ((track - knob) * (scroll / maxScroll));
			g.fill(SX + SW - 3, ky, SX + SW - 1, ky + knob, 0x88FFFFFF);
		}
	}

	/** One laid-out line of a conversation: a day chip (msg == null) or a bubble. */
	private record Row(int index, PhoneMsg msg, String chip, List<FormattedCharSequence> lines, boolean head, int w, int h) {
	}

	private Row layout(int index, PhoneMsg m, boolean head) {
		int maxW = SW - 44;
		String time = ClientMessages.clock(m.time());
		int timeW = smallWidth(time);
		return switch (m.kind()) {
			case PhoneMsg.PHOTO -> new Row(index, m, null, List.of(), head, PHOTO_W + 6, PHOTO_H + 6 + 9);
			case PhoneMsg.CASE -> new Row(index, m, null, List.of(), head, SW - 40, 94);
			default -> {
				List<FormattedCharSequence> lines = font.split(Component.translatable(m.value()), maxW);
				int textW = 0;
				for (FormattedCharSequence l : lines) {
					textW = Math.max(textW, font.width(l));
				}
				int last = lines.isEmpty() ? 0 : font.width(lines.get(lines.size() - 1));
				boolean inline = last + 6 + timeW <= maxW;
				int w = Math.max(textW, inline ? last + 6 + timeW : timeW) + 8;
				int h = 6 + lines.size() * 10 + (inline ? 0 : 8);
				yield new Row(index, m, null, lines, head, w, h);
			}
		};
	}

	private void drawThread(GuiGraphics g, float pt) {
		PhoneMessagesPayload.View t = ClientMessages.find(threadId);
		if (t == null) {
			app = App.MESSAGES;
			return;
		}
		g.fill(SX, SY, SX + SW, SY + SH, CHAT_BG);
		// faint wallpaper dots
		for (int y = BT + 6; y < BB; y += 16) {
			for (int x = SX + 6 + ((y / 16) % 2) * 8; x < SX + SW; x += 16) {
				g.fill(x, y, x + 1, y + 1, 0x14FFFFFF);
			}
		}
		List<Row> rows = new ArrayList<>();
		int total = 6;
		long lastDay = Long.MIN_VALUE;
		for (int i = 0; i < t.messages().size(); i++) {
			PhoneMsg m = t.messages().get(i);
			long day = ClientMessages.day(m.time());
			boolean head = day != lastDay;
			if (day != lastDay) {
				lastDay = day;
				Row chip = new Row(-1, null, Component.translatable("deadline.phone.day", day).getString(), List.of(), false, 0, 18);
				rows.add(chip);
				total += chip.h();
			}
			Row r = layout(i, m, head || i == 0);
			rows.add(r);
			total += r.h() + 3;
		}
		boolean typing = ClientMessages.typing(t.id()) > 0;
		if (typing) {
			total += 20;
		}
		int view = BB - BT;
		float max = Math.max(0, total - view);
		chatScroll = Mth.clamp(chatScroll, 0F, max);
		int y = BB - total + (int) chatScroll;
		for (Row r : rows) {
			if (r.msg() == null) {
				if (y >= BT && y + r.h() <= BB) {
					int cw = font.width(r.chip()) + 10;
					int cx = SX + SW / 2;
					g.fill(cx - cw / 2, y + 4, cx + cw / 2, y + 15, 0xFF182229);
					g.drawString(font, r.chip(), cx - font.width(r.chip()) / 2, y + 6, GREY, false);
				}
				y += r.h();
				continue;
			}
			y += 3;
			if (y >= BT && y + r.h() <= BB) {
				drawBubble(g, r, y);
			}
			y += r.h();
		}
		if (typing && y + 4 >= BT && y + 18 <= BB) {
			y += 4;
			int x = SX + 8;
			g.fill(x, y, x + 30, y + 14, BUBBLE);
			for (int i = 0; i < 3; i++) {
				float bob = (float) Math.sin((ClientState.ticks + pt) * 0.5F - i * 0.9F);
				int dy = bob > 0.3F ? -1 : 0;
				g.fill(x + 8 + i * 6, y + 6 + dy, x + 11 + i * 6, y + 9 + dy, bob > 0.3F ? 0xFFD0D7DB : GREY);
			}
		}
		// header over the conversation
		g.fill(SX, HY, SX + SW, HY + 24, CHAT_BAR);
		g.drawString(font, "‹", SX + 5, HY + 8, TEXT, false);
		contactAvatar(g, t.id(), SX + 14, HY + 4, 16);
		String name = ClientMessages.name(t.id()).getString();
		g.drawString(font, font.plainSubstrByWidth(name, SW - 40), SX + 35, HY + (typing ? 3 : 8), TEXT, false);
		if (typing) {
			small(g, Component.translatable("deadline.phone.typing").getString(), SX + 35, HY + 14, GREEN);
		}
		hits.add(new Hit(SX, HY, 60, 24, () -> {
			app = App.MESSAGES;
			scroll = 0F;
		}));
		g.fill(SX, BB, SX + SW, SY + SH, CHAT_BG);
		if (max > 0) {
			int track = view;
			int knob = Math.max(16, (int) (track * track / (float) (track + max)));
			int ky = BT + (int) ((track - knob) * (1F - chatScroll / max));
			g.fill(SX + SW - 3, ky, SX + SW - 1, ky + knob, 0x55FFFFFF);
		}
	}

	private void drawBubble(GuiGraphics g, Row r, int y) {
		PhoneMsg m = r.msg();
		int x = SX + 8;
		g.fill(x, y, x + r.w(), y + r.h(), BUBBLE);
		if (r.head()) {
			// the little tail on the first bubble of the day
			g.fill(x - 4, y, x, y + 1, BUBBLE);
			g.fill(x - 2, y + 1, x, y + 3, BUBBLE);
		}
		String time = ClientMessages.clock(m.time());
		int tw = smallWidth(time);
		int ty = y + 3;
		switch (m.kind()) {
			case PhoneMsg.PHOTO -> {
				g.fill(x + 3, ty, x + 3 + PHOTO_W, ty + PHOTO_H, 0xFF000000);
				g.blit(RenderPipelines.GUI_TEXTURED, DeadLine.id("textures/gui/photo/" + m.value() + ".png"), x + 3, ty, 0F, 0F,
						PHOTO_W, PHOTO_H, 128, 96, 128, 96);
			}
			case PhoneMsg.CASE -> drawLocation(g, r, x, ty);
			default -> {
				for (FormattedCharSequence l : r.lines()) {
					g.drawString(font, l, x + 4, ty, TEXT, false);
					ty += 10;
				}
			}
		}
		small(g, time, x + r.w() - 4 - tw, y + r.h() - 8, GREY);
	}

	/** A shared location: a dark map tile with a red pin, the place, and the "Aceptar caso" button. */
	private void drawLocation(GuiGraphics g, Row r, int x, int y) {
		PhoneMsg m = r.msg();
		int mx = x + 3;
		int mw = r.w() - 6;
		int mh = 40;
		g.fill(mx, y, mx + mw, y + mh, 0xFF15201B);
		for (int gx = mx + 7; gx < mx + mw; gx += 14) {
			g.fill(gx, y, gx + 1, y + mh, 0x18FFFFFF);
		}
		for (int gy = y + 6; gy < y + mh; gy += 12) {
			g.fill(mx, gy, mx + mw, gy + 1, 0x18FFFFFF);
		}
		g.fill(mx, y + 25, mx + mw, y + 28, 0x30FFFFFF);
		g.fill(mx + mw / 3, y, mx + mw / 3 + 3, y + mh, 0x30FFFFFF);
		int px = mx + mw / 2;
		int py = y + 16;
		disc(g, px, py, 5, 0xFFE0242C);
		disc(g, px, py, 2, 0xFF5A0A0E);
		g.fill(px - 1, py + 4, px + 2, py + 11, 0xFFE0242C);
		int ty = y + mh + 4;
		Component place = Component.translatable("deadline.case." + m.value() + ".place");
		g.drawString(font, font.plainSubstrByWidth(place.getString(), mw), mx, ty, TEXT, false);
		small(g, Component.translatable("deadline.phone.location").getString(), mx, ty + 11, GREY);
		int by = ty + 20;
		boolean accepted = m.is(PhoneMsg.ACCEPTED);
		Component label = Component.translatable(accepted ? "deadline.phone.case_accepted" : "deadline.phone.accept_case");
		String thread = threadId;
		int index = r.index();
		button(g, mx, by, mw, 16, label, accepted ? 0xFF2A3A34 : 0xFF1F8A55, () -> {
			if (!accepted) {
				ClientMessages.accept(thread, index);
				onClose();
			}
		});
	}

	// ------------------------------------------------------------------ active case
	private void drawCase(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF0B0B10);
		header(g, Component.translatable("deadline.phone.case"), App.HOME);
		if (d.activeCase().isEmpty()) {
			wrapCentered(g, Component.translatable("deadline.phone.no_case"), SY + SH / 2 - 10, 0xFF6A6A76);
			return;
		}
		String key = d.activeCase();
		int y = TOP + 28;
		String contact = "colegio".equals(key) ? "clara" : "marta";
		contactAvatar(g, contact, SX + 8, y, 32);
		Component place = Component.translatable("deadline.case." + key + ".place");
		wrap(g, place, SX + 46, y + 2, SW - 54, 0xFFE33A3A);
		g.drawString(font, font.plainSubstrByWidth(ClientMessages.name(contact).getString(), SW - 54), SX + 46, y + 22, 0xFF9A9AA6, false);
		y += 42;

		// progress (a scripted case shows its chapter and the HUD checklist instead of the four legacy stages)
		boolean story = com.deadline.client.hud.StoryHud.active();
		// a scripted case without objectives (the Casa) shows no progress, objective, hint or weakness: only the way out
		boolean quiet = !story && ClientState.caseType(key).scripted();
		if (!quiet) {
			drawCaseProgress(g, d, key, story, y);
		}

		int by = SY + SH - 30;
		if (!story && !quiet && d.stage() >= 3) {
			button(g, SX + 10, by, SW - 20, 22, Component.translatable("deadline.phone.go_home"), 0xFF1FAF5A, () -> {
				send(PhoneActionPayload.RETURN_HOME, 0);
				onClose();
			});
		} else {
			Component label = Component.translatable(confirmAbandon ? "deadline.phone.sure" : "deadline.phone.abandon");
			button(g, SX + 10, by, SW - 20, 22, label, confirmAbandon ? 0xFFE01B24 : 0xFF5A1218, () -> {
				if (confirmAbandon) {
					send(PhoneActionPayload.ABANDON, 0);
					onClose();
				} else {
					confirmAbandon = true;
				}
			});
		}
	}

	/** Progress bar, objective, evidence, hint and weakness of the case page (legacy cases and story chapters). */
	private void drawCaseProgress(GuiGraphics g, PhoneDataPayload d, String key, boolean story, int y) {
		int steps = story ? 9 : 4;
		int bw = (SW - 20 - (steps - 1) * 4) / steps;
		for (int i = 0; i < steps; i++) {
			int c = i < d.stage() ? 0xFFB3121B : i == d.stage() ? ((ClientState.ticks / 8) % 2 == 0 ? 0xFFFFFFFF : 0xFFB3121B) : 0xFF2A2A34;
			g.fill(SX + 10 + i * (bw + 4), y, SX + 10 + i * (bw + 4) + bw, y + 4, c);
		}
		y += 12;
		g.drawString(font, Component.translatable("deadline.phone.objective"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		if (story) {
			y = wrap(g, com.deadline.client.hud.StoryHud.text(com.deadline.client.hud.StoryHud.chapterKey), SX + 10, y, SW - 20, 0xFFFFFFFF) + 3;
			for (int i = 0; i < com.deadline.client.hud.StoryHud.objKeys.size(); i++) {
				boolean ok = com.deadline.client.hud.StoryHud.objDone.get(i);
				y = wrap(g, Component.literal(ok ? "✔ " : "□ ").append(com.deadline.client.hud.StoryHud.text(com.deadline.client.hud.StoryHud.objKeys.get(i))),
						SX + 10, y, SW - 20, ok ? 0xFF8A8A92 : 0xFFE8E2D6) + 2;
			}
			y += 4;
		} else {
			y = wrap(g, Component.translatable(ClientState.objectiveKey(key, d.stage())), SX + 10, y, SW - 20, 0xFFFFFFFF) + 6;
		}
		g.drawString(font, Component.translatable("deadline.phone.evidence", d.evidence()), SX + 10, y, 0xFF8CFFB0, false);
		y += 16;
		g.drawString(font, Component.translatable("deadline.phone.hint"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		y = wrap(g, Component.translatable("deadline.case." + key + ".hint"), SX + 10, y, SW - 20, 0xFFE8D9A8) + 6;
		String beast = ClientState.caseEntity(key);
		g.drawString(font, Component.translatable("deadline.phone.weakness"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		wrap(g, Component.translatable("deadline.weakness." + beast), SX + 10, y, SW - 20, 0xFFFFC23A);
	}

	// ------------------------------------------------------------------ shop
	private void drawShop(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF0B0B10);
		header(g, Component.translatable("deadline.phone.shop"), App.HOME);
		String money = "$" + d.money();
		g.drawString(font, money, SX + SW - 8 - font.width(money), TOP + 6, 0xFF6BFF8E, false);
		CaseManager.initShop();
		List<CaseManager.ShopEntry> shop = CaseManager.SHOP;
		int top = TOP + 24;
		int bottom = SY + SH - 4;
		int rowH = 28;
		float maxScroll = Math.max(0, shop.size() * rowH - (bottom - top));
		scroll = Mth.clamp(scroll, 0F, maxScroll);
		for (int i = 0; i < shop.size(); i++) {
			int y = top + i * rowH - (int) scroll;
			if (y < top || y + rowH - 2 > bottom) {
				continue;
			}
			CaseManager.ShopEntry e = shop.get(i);
			ItemStack st = new ItemStack(e.item(), e.count());
			boolean afford = d.money() >= e.price();
			g.fill(SX + 4, y, SX + SW - 4, y + rowH - 2, 0xFF15151C);
			g.fill(SX + 8, y + 4, SX + 26, y + 22, 0xFF22222C);
			g.renderItem(st, SX + 9, y + 5);
			g.renderItemDecorations(font, st, SX + 9, y + 5);
			g.drawString(font, font.plainSubstrByWidth(st.getHoverName().getString(), SW - 84), SX + 32, y + 5, 0xFFFFFFFF, false);
			g.drawString(font, "$" + e.price(), SX + 32, y + 15, afford ? 0xFF6BFF8E : 0xFFFF3B3B, false);
			int bx = SX + SW - 50;
			g.fill(bx, y + 5, bx + 42, y + 21, afford ? 0xFF1F6F3A : 0xFF33333C);
			g.drawCenteredString(font, Component.translatable("deadline.phone.buy"), bx + 21, y + 9, afford ? 0xFFFFFFFF : 0xFF777777);
			int idx = i;
			hits.add(new Hit(bx, y + 5, 42, 16, () -> send(PhoneActionPayload.BUY, idx)));
		}
		if (maxScroll > 0) {
			int track = bottom - top;
			int knob = Math.max(16, (int) (track * track / (float) (track + maxScroll)));
			int ky = top + (int) ((track - knob) * (scroll / maxScroll));
			g.fill(SX + SW - 3, ky, SX + SW - 1, ky + knob, 0x88FFFFFF);
		}
	}

	// ------------------------------------------------------------------ bestiary
	private static boolean known(PhoneDataPayload d, int i) {
		if (i < 5) {
			return (d.bestiary() & (1 << i)) != 0;
		}
		return d.bestiary() != 0;
	}

	private void portrait(GuiGraphics g, String key, int x, int y, int size, boolean known) {
		g.blit(RenderPipelines.GUI_TEXTURED, DeadLineHud.jumpscareTexture(key), x, y, 0F, 0F, size, size, 512, 512, 512, 512,
				known ? 0xFFFFFFFF : 0xFF000000);
	}

	private void drawBestiary(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF0B0B10);
		header(g, Component.translatable("deadline.phone.bestiary"), App.HOME);
		int top = TOP + 24;
		int bottom = SY + SH - 4;
		int rowH = 38;
		float maxScroll = Math.max(0, BEASTS.length * rowH - (bottom - top));
		scroll = Mth.clamp(scroll, 0F, maxScroll);
		for (int i = 0; i < BEASTS.length; i++) {
			int y = top + i * rowH - (int) scroll;
			if (y < top || y + rowH - 2 > bottom) {
				continue;
			}
			boolean k = known(d, i);
			g.fill(SX + 4, y, SX + SW - 4, y + rowH - 2, 0xFF15151C);
			g.fill(SX + 6, y + 2, SX + 38, y + 34, 0xFF2A0A0E);
			portrait(g, BEASTS[i], SX + 6, y + 2, 32, k);
			Component name = k ? Component.translatable("entity.deadline." + BEASTS[i]) : Component.translatable("deadline.phone.unknown");
			g.drawString(font, name, SX + 44, y + 7, k ? 0xFFFFFFFF : 0xFF6A6A76, false);
			Component sub = k ? Component.translatable("deadline.weakness." + BEASTS[i]) : Component.translatable("deadline.phone.locked");
			g.drawString(font, font.plainSubstrByWidth(sub.getString(), SW - 52), SX + 44, y + 20, k ? 0xFFFFC23A : 0xFF4A4A56, false);
			if (k) {
				int idx = i;
				hits.add(new Hit(SX + 4, y, SW - 8, rowH - 2, () -> {
					sel = idx;
					app = App.BEAST;
				}));
			}
		}
	}

	private void drawBeast(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF070709);
		header(g, Component.translatable("deadline.phone.bestiary"), App.BESTIARY);
		String key = BEASTS[Mth.clamp(sel, 0, BEASTS.length - 1)];
		int cx = SX + SW / 2;
		int y = TOP + 26;
		g.fill(cx - 50, y - 2, cx + 50, y + 98, 0xFF2A0A0E);
		portrait(g, key, cx - 48, y, 96, true);
		y += 104;
		g.pose().pushMatrix();
		g.pose().translate(cx, y);
		g.pose().scale(1.5F, 1.5F);
		Component name = Component.translatable("entity.deadline." + key);
		g.drawString(font, name, -font.width(name) / 2, 0, 0xFFE33A3A, true);
		g.pose().popMatrix();
		y += 18;
		y = wrap(g, Component.translatable("deadline.bestiary." + key), SX + 10, y, SW - 20, 0xFFE8E2D8) + 6;
		g.drawString(font, Component.translatable("deadline.phone.weakness"), SX + 10, y, 0xFF9A9AA6, false);
		wrap(g, Component.translatable("deadline.weakness." + key), SX + 10, y + 11, SW - 20, 0xFFFFC23A);
	}

	// ------------------------------------------------------------------ input
	@Override
	public boolean mouseClicked(MouseButtonEvent e, boolean dbl) {
		double lx = (e.x() - ox) / scale;
		double ly = (e.y() - oy) / scale;
		for (int i = hits.size() - 1; i >= 0; i--) {
			Hit h = hits.get(i);
			if (lx >= h.x && lx < h.x + h.w && ly >= h.y && ly < h.y + h.h) {
				Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1.2F));
				h.action.run();
				return true;
			}
		}
		return super.mouseClicked(e, dbl);
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		if (app == App.THREAD) {
			chatScroll += (float) sy * 16F;
		} else {
			scroll -= (float) sy * 14F;
		}
		return true;
	}

	@Override
	public boolean keyPressed(KeyEvent e) {
		if (e.key() == GLFW.GLFW_KEY_ESCAPE && app != App.HOME) {
			app = switch (app) {
				case THREAD -> App.MESSAGES;
				case BEAST -> App.BESTIARY;
				default -> App.HOME;
			};
			scroll = 0F;
			confirmAbandon = false;
			return true;
		}
		return super.keyPressed(e);
	}
}
