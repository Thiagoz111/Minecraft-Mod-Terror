package com.deadline.client.screen;

import com.deadline.DeadLine;
import com.deadline.caseload.CaseManager;
import com.deadline.caseload.CaseType;
import com.deadline.client.ClientState;
import com.deadline.client.hud.DeadLineHud;
import com.deadline.net.PhoneActionPayload;
import com.deadline.net.PhoneDataPayload;
import com.deadline.registry.ModSounds;
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

/** The hunter's cursed smartphone: calls from victims, the active case, a shop and the bestiary. */
public class PhoneScreen extends Screen {
	private static final Identifier FRAME = DeadLine.id("textures/gui/phone/frame.png");
	private static final Identifier WALLPAPER = DeadLine.id("textures/gui/phone/wallpaper.png");
	private static final Identifier CRACK = DeadLine.id("textures/gui/phone/crack.png");
	private static final Identifier APPS = DeadLine.id("textures/gui/phone/apps.png");
	private static final Identifier AVATARS = DeadLine.id("textures/gui/phone/avatars.png");

	private static final int FW = 192;
	private static final int FH = 352;
	private static final int SX = 8;
	private static final int SY = 22;
	private static final int SW = 176;
	private static final int SH = 308;
	private static final int TOP = SY + 12;

	private static final String[] BEASTS = {"poseida", "llorona", "wendigo", "payaso", "monja", "sombra", "muneca", "anima"};

	private enum App {
		HOME, CALLS, CALL, CASE, SHOP, BESTIARY, BEAST
	}

	private record Hit(int x, int y, int w, int h, Runnable action) {
	}

	private final List<Hit> hits = new ArrayList<>();
	private App app = App.HOME;
	private int sel;
	private float scroll;
	private int age;
	private boolean confirmAbandon;
	private float scale = 1F;
	private int ox;
	private int oy;

	public PhoneScreen() {
		super(Component.translatable("item.deadline.phone"));
	}

	/** Opens directly on an app (used by the screenshot test). app: home|calls|call|case|shop|bestiary|beast. */
	public static PhoneScreen at(String app, int sel) {
		PhoneScreen s = new PhoneScreen();
		s.app = App.valueOf(app.toUpperCase(java.util.Locale.ROOT));
		s.sel = sel;
		s.age = 20;
		return s;
	}

	@Override
	protected void init() {
		if (age == 0) {
			PhoneDataPayload d = ClientState.phone;
			if (ClientState.callTicks > 0 && !d.requests().isEmpty()) {
				app = App.CALLS;
			}
			ClientState.callTicks = 0;
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
			case CALLS -> drawCalls(g, d);
			case CALL -> drawCall(g, d);
			case CASE -> drawCase(g, d);
			case SHOP -> drawShop(g, d);
			case BESTIARY -> drawBestiary(g, d);
			case BEAST -> drawBeast(g, d);
		}
		drawStatusBar(g);
		if (ClientState.sanityShown < 35F) {
			int a = (int) (Mth.clamp((35F - ClientState.sanityShown) / 25F, 0F, 1F) * 255);
			g.blit(RenderPipelines.GUI_TEXTURED, CRACK, SX, SY, 0F, 0F, SW, SH, SW, SH, a << 24 | 0xFFFFFF);
		}
		if (ClientState.sanityShown < 20F && (ClientState.ticks % 37) < 3) {
			int gy = SY + (int) ((ClientState.ticks * 53) % SH);
			g.fill(SX, gy, SX + SW, gy + 3, 0x66FF2030);
		}
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
		// signal: fades as sanity drops
		int bars = ClientState.sanityShown > 75 ? 4 : ClientState.sanityShown > 50 ? 3 : ClientState.sanityShown > 25 ? 2 : 1;
		for (int i = 0; i < 4; i++) {
			int c = i < bars ? 0xFFFFFFFF : 0x44FFFFFF;
			g.fill(SX + SW - 40 + i * 4, SY + 9 - (i + 1) * 2, SX + SW - 37 + i * 4, SY + 9, c);
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

	private void avatar(GuiGraphics g, String caseKey, int caller, int x, int y, int size) {
		int row = ClientState.caseRow(caseKey);
		g.blit(RenderPipelines.GUI_TEXTURED, AVATARS, x, y, caller * 32F, row * 32F, size, size, 32, 32, 160, 160);
	}

	private int wrap(GuiGraphics g, Component text, int x, int y, int w, int color) {
		List<FormattedCharSequence> lines = font.split(text, w);
		for (FormattedCharSequence l : lines) {
			g.drawString(font, l, x, y, color, false);
			y += 10;
		}
		return y;
	}

	private static String ago(int secs) {
		if (secs < 60) {
			return secs + "s";
		}
		if (secs < 3600) {
			return secs / 60 + "m";
		}
		return secs / 3600 + "h";
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
		Component san = Component.translatable("deadline.phone.sanity");
		g.drawString(font, san, SX + SW - 16 - font.width(san), wy + 5, 0xFF9A9AA6, false);
		int sc = d.sanity() > 60 ? 0xFF55FF8A : d.sanity() > 30 ? 0xFFFFC23A : 0xFFFF3B3B;
		String sp = Mth.ceil(d.sanity()) + "%";
		g.drawString(font, sp, SX + SW - 16 - font.width(sp), wy + 16, sc, true);
		g.fill(SX + SW - 66, wy + 30, SX + SW - 16, wy + 33, 0x55FFFFFF);
		g.fill(SX + SW - 66, wy + 30, SX + SW - 66 + (int) (50 * d.sanity() / 100F), wy + 33, sc);

		// apps
		Component[] names = {Component.translatable("deadline.phone.calls"), Component.translatable("deadline.phone.case"),
				Component.translatable("deadline.phone.shop"), Component.translatable("deadline.phone.bestiary")};
		App[] targets = {App.CALLS, App.CASE, App.SHOP, App.BESTIARY};
		for (int i = 0; i < 4; i++) {
			int cx = SX + 44 + (i % 2) * 88;
			int cy = SY + 140 + (i / 2) * 62;
			g.fill(cx - 19, cy - 3, cx + 19, cy + 35, 0x55000000);
			g.blit(RenderPipelines.GUI_TEXTURED, APPS, cx - 16, cy, i * 32F, 0F, 32, 32, 128, 32);
			g.drawCenteredString(font, names[i], cx, cy + 38, 0xFFFFFFFF);
			if (i == 0 && !d.requests().isEmpty()) {
				g.fill(cx + 10, cy - 5, cx + 21, cy + 6, 0xFFE01B24);
				g.drawCenteredString(font, String.valueOf(d.requests().size()), cx + 16, cy - 3, 0xFFFFFFFF);
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
			g.drawString(font, font.plainSubstrByWidth(Component.translatable(ClientState.objectiveKey(d.activeCase(), d.stage())).getString(), SW - 34),
					SX + 16, by + 16, 0xFFFFC23A, false);
			hits.add(new Hit(SX + 10, by, SW - 20, 28, () -> app = App.CASE));
		}
	}

	// ------------------------------------------------------------------ calls
	private void drawCalls(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF0B0B10);
		header(g, Component.translatable("deadline.phone.calls"), App.HOME);
		List<PhoneDataPayload.Request> reqs = d.requests();
		if (reqs.isEmpty()) {
			wrapCentered(g, Component.translatable("deadline.phone.no_calls"), SY + SH / 2 - 10, 0xFF6A6A76);
			return;
		}
		int y = TOP + 26;
		for (int i = 0; i < reqs.size() && y + 40 <= SY + SH; i++) {
			PhoneDataPayload.Request r = reqs.get(i);
			g.fill(SX + 4, y, SX + SW - 4, y + 38, 0xFF15151C);
			avatar(g, r.caseKey(), r.caller(), SX + 7, y + 3, 32);
			Component name = Component.translatable("deadline.case." + r.caseKey() + ".caller." + r.caller());
			g.drawString(font, font.plainSubstrByWidth(name.getString(), SW - 70), SX + 44, y + 6, 0xFFFFFFFF, false);
			Component place = Component.translatable("deadline.case." + r.caseKey() + ".place");
			g.drawString(font, font.plainSubstrByWidth(place.getString(), SW - 56), SX + 44, y + 20, 0xFFE33A3A, false);
			String a = ago(r.ageSeconds());
			g.drawString(font, a, SX + SW - 8 - font.width(a), y + 6, 0xFF6A6A76, false);
			int idx = i;
			hits.add(new Hit(SX + 4, y, SW - 8, 38, () -> {
				sel = idx;
				app = App.CALL;
				// the caller's voice message, through a bad line
				Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.PHONE_VOICE, 1.0F, 0.9F));
			}));
			y += 42;
		}
	}

	private void wrapCentered(GuiGraphics g, Component text, int y, int color) {
		for (FormattedCharSequence l : font.split(text, SW - 24)) {
			g.drawString(font, l, SX + SW / 2 - font.width(l) / 2, y, color, false);
			y += 10;
		}
	}

	private void drawCall(GuiGraphics g, PhoneDataPayload d) {
		g.fill(SX, SY, SX + SW, SY + SH, 0xFF0B0B10);
		header(g, Component.translatable("deadline.phone.calls"), App.CALLS);
		if (sel < 0 || sel >= d.requests().size()) {
			app = App.CALLS;
			return;
		}
		PhoneDataPayload.Request r = d.requests().get(sel);
		CaseType type = ClientState.caseType(r.caseKey());
		int cx = SX + SW / 2;
		int y = TOP + 28;
		boolean unknown = r.caller() == type.callers() - 1 && !"casa".equals(r.caseKey());
		int ring = unknown ? 0xFFB3121B : 0xFF2BD96B;
		g.fill(cx - 35, y - 3, cx + 35, y + 67, ring);
		avatar(g, r.caseKey(), r.caller(), cx - 32, y, 64);
		y += 72;
		Component name = Component.translatable("deadline.case." + r.caseKey() + ".caller." + r.caller());
		g.drawCenteredString(font, name, cx, y, 0xFFFFFFFF);
		y += 11;
		g.drawCenteredString(font, Component.translatable("deadline.case." + r.caseKey() + ".place"), cx, y, 0xFFE33A3A);
		y += 15;
		Component msg = Component.translatable("deadline.case." + r.caseKey() + ".msg." + r.caller());
		List<FormattedCharSequence> lines = font.split(msg, SW - 28);
		int bh = lines.size() * 10 + 8;
		g.fill(SX + 8, y, SX + SW - 8, y + bh, 0xFF1C1C26);
		g.fill(SX + 8, y, SX + 10, y + bh, ring);
		int ly = y + 5;
		for (FormattedCharSequence l : lines) {
			g.drawString(font, l, SX + 14, ly, 0xFFE8E2D8, false);
			ly += 10;
		}
		y += bh + 8;
		g.drawString(font, Component.translatable("deadline.phone.difficulty"), SX + 10, y, 0xFF9A9AA6, false);
		StringBuilder skulls = new StringBuilder();
		for (int i = 0; i < 5; i++) {
			skulls.append(i < type.difficulty() ? "☠" : "·");
		}
		g.drawString(font, skulls.toString(), SX + SW - 10 - font.width(skulls.toString()), y, 0xFFE33A3A, false);
		y += 12;
		g.drawString(font, Component.translatable("deadline.phone.reward"), SX + 10, y, 0xFF9A9AA6, false);
		String pay = "$" + type.reward();
		g.drawString(font, pay, SX + SW - 10 - font.width(pay), y, 0xFF6BFF8E, false);

		int by = SY + SH - 30;
		if (!d.activeCase().isEmpty()) {
			wrapCentered(g, Component.translatable("deadline.phone.busy"), by - 14, 0xFFFFC23A);
			button(g, SX + 10, by, SW - 20, 22, Component.translatable("deadline.phone.decline"), 0xFFA01E26, () -> {
				send(PhoneActionPayload.DECLINE, r == null ? 0 : sel);
				app = App.CALLS;
			});
			return;
		}
		int idx = sel;
		button(g, SX + 10, by, 74, 22, Component.translatable("deadline.phone.decline"), 0xFFA01E26, () -> {
			send(PhoneActionPayload.DECLINE, idx);
			app = App.CALLS;
		});
		button(g, SX + SW - 84, by, 74, 22, Component.translatable("deadline.phone.accept"), 0xFF1FAF5A, () -> {
			send(PhoneActionPayload.ACCEPT, idx);
			onClose();
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
		avatar(g, key, d.activeCaller(), SX + 8, y, 32);
		Component place = Component.translatable("deadline.case." + key + ".place");
		wrap(g, place, SX + 46, y + 2, SW - 54, 0xFFE33A3A);
		g.drawString(font, font.plainSubstrByWidth(Component.translatable("deadline.case." + key + ".caller." + d.activeCaller()).getString(), SW - 54),
				SX + 46, y + 22, 0xFF9A9AA6, false);
		y += 42;

		// progress
		int steps = 4;
		int bw = (SW - 20 - (steps - 1) * 4) / steps;
		for (int i = 0; i < steps; i++) {
			int c = i < d.stage() ? 0xFFB3121B : i == d.stage() ? ((ClientState.ticks / 8) % 2 == 0 ? 0xFFFFFFFF : 0xFFB3121B) : 0xFF2A2A34;
			g.fill(SX + 10 + i * (bw + 4), y, SX + 10 + i * (bw + 4) + bw, y + 4, c);
		}
		y += 12;
		g.drawString(font, Component.translatable("deadline.phone.objective"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		y = wrap(g, Component.translatable(ClientState.objectiveKey(key, d.stage())), SX + 10, y, SW - 20, 0xFFFFFFFF) + 6;
		g.drawString(font, Component.translatable("deadline.phone.evidence", d.evidence()), SX + 10, y, 0xFF8CFFB0, false);
		y += 16;
		g.drawString(font, Component.translatable("deadline.phone.hint"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		y = wrap(g, Component.translatable("deadline.case." + key + ".hint"), SX + 10, y, SW - 20, 0xFFE8D9A8) + 6;
		String beast = ClientState.caseEntity(key);
		g.drawString(font, Component.translatable("deadline.phone.weakness"), SX + 10, y, 0xFF9A9AA6, false);
		y += 11;
		wrap(g, Component.translatable("deadline.weakness." + beast), SX + 10, y, SW - 20, 0xFFFFC23A);

		int by = SY + SH - 30;
		if (d.stage() >= 3) {
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
		scroll -= (float) sy * 14F;
		return true;
	}

	@Override
	public boolean keyPressed(KeyEvent e) {
		if (e.key() == GLFW.GLFW_KEY_ESCAPE && app != App.HOME) {
			app = switch (app) {
				case CALL -> App.CALLS;
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
