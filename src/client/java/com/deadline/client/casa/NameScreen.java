package com.deadline.client.casa;

import com.deadline.casa.CasaNet;
import com.deadline.client.ClientState;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

/**
 * "¿Cómo se llama?": the demon's name, chosen while the Nona pulls the last thread. Three trembling words
 * (LEMAZA / AZAMEL / OFELIA); click one or press 1-3. With a time limit the red thread runs out (answer "").
 * It cannot be dismissed: the server is waiting for the name.
 */
public class NameScreen extends Screen {
	private static final float WORD_SCALE = 3F;

	/** Set by {@link CasaClientNet} just before the server takes the screen away or asks again: no answer for it. */
	static boolean silentClose;

	private final List<String> options;
	private final int limit;
	private final List<int[]> boxes = new ArrayList<>();
	private int age;
	private boolean answered;
	private int hover = -1;

	public NameScreen(List<String> options, int ticks) {
		super(Component.translatable("deadline.casa.name.title"));
		this.options = List.copyOf(options);
		this.limit = ticks;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean shouldCloseOnEsc() {
		return false;
	}

	@Override
	protected void init() {
		if (age == 0) {
			Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.DOLL_GIGGLE_CHORUS, 0.8F, 0.6F));
		}
	}

	@Override
	public void tick() {
		age++;
		if (limit > 0 && age >= limit && !answered) {
			answer("");
		}
	}

	private void answer(String name) {
		if (answered) {
			return;
		}
		answered = true;
		CasaClientNet.send(CasaNet.ActionPayload.NAME, name);
		onClose();
	}

	/** Pushed away by another screen (death, a chat...) before choosing: it counts as the thread running out. */
	@Override
	public void removed() {
		if (!answered && !silentClose) {
			answered = true;
			CasaClientNet.send(CasaNet.ActionPayload.NAME, "");
		}
		silentClose = false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		float k = Mth.clamp((age + pt) / 10F, 0F, 1F);
		g.fillGradient(0, 0, width, height, (int) (k * 0xC8) << 24 | 0x0A0204, (int) (k * 0xF0) << 24 | 0x1A0306);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		float t = age + pt;
		float in = Mth.clamp(t / 12F, 0F, 1F);
		int a = (int) (in * 255) << 24;

		// title
		Component title = Component.translatable("deadline.casa.name.title");
		g.pose().pushMatrix();
		g.pose().translate(width / 2F, height * 0.2F);
		g.pose().scale(2F, 2F);
		g.drawString(font, title, -font.width(title) / 2, 0, a | 0xF2ECE4, true);
		g.pose().popMatrix();
		Component sub = Component.translatable("deadline.casa.name.sub");
		g.drawString(font, sub, (width - font.width(sub)) / 2, (int) (height * 0.2F) + 24, a | 0xB8A8A0, false);

		// the three names, trembling
		boxes.clear();
		hover = -1;
		int n = options.size();
		float slot = Math.min(width / (float) Math.max(1, n), 220F);
		float startX = width / 2F - slot * n / 2F;
		float wy = height * 0.48F;
		for (int i = 0; i < n; i++) {
			String word = options.get(i).toUpperCase(Locale.ROOT);
			float cx = startX + slot * (i + 0.5F);
			int ww = (int) (font.width(word) * WORD_SCALE);
			int x0 = (int) (cx - ww / 2F) - 8;
			int y0 = (int) wy - 8;
			int x1 = (int) (cx + ww / 2F) + 8;
			int y1 = (int) (wy + 9 * WORD_SCALE) + 8;
			boxes.add(new int[] {x0, y0, x1, y1});
			if (mx >= x0 && mx < x1 && my >= y0 && my < y1) {
				hover = i;
			}
		}
		for (int i = 0; i < n; i++) {
			drawWord(g, options.get(i).toUpperCase(Locale.ROOT), startX + slot * (i + 0.5F), wy, t, i, i == hover, a);
			int[] b = boxes.get(i);
			String key = "[" + (i + 1) + "]";
			g.drawString(font, key, (b[0] + b[2]) / 2 - font.width(key) / 2, b[3] + 4, a | (i == hover ? 0xE33A3A : 0x6A5A58), false);
		}

		// the thread running out
		if (limit > 0) {
			float left = Mth.clamp(1F - t / limit, 0F, 1F);
			int bw = (int) (width * 0.5F);
			int bx = (width - bw) / 2;
			int by = (int) (height * 0.78F);
			g.fill(bx, by, bx + bw, by + 1, a | 0x3A1012);
			int lw = (int) (bw * left);
			int sag = (int) (Math.sin(t * 0.3F) * 1.5F);
			g.fill(bx + (bw - lw) / 2, by + sag, bx + (bw + lw) / 2, by + 2 + sag, a | 0xD21F2B);
			if (left < 0.3F && (ClientState.ticks / 4) % 2 == 0) {
				g.fill(bx + (bw - lw) / 2 - 2, by - 1 + sag, bx + (bw - lw) / 2, by + 3 + sag, a | 0xFFFFFF);
			}
		}
		Component help = Component.translatable("deadline.casa.name.help");
		g.drawString(font, help, (width - font.width(help)) / 2, height - 22, a | 0x5A4A48, false);
	}

	/** One name: letters shiver on their own; the hovered one goes red and grows. */
	private void drawWord(GuiGraphics g, String word, float cx, float y, float t, int idx, boolean hot, int alpha) {
		float s = hot ? WORD_SCALE * 1.12F : WORD_SCALE;
		float ww = font.width(word) * s;
		float x = cx - ww / 2F;
		float amp = hot ? 1.6F : 0.7F;
		for (int i = 0; i < word.length(); i++) {
			String c = String.valueOf(word.charAt(i));
			float dx = (float) Math.sin(t * 1.7F + i * 2.1F + idx * 5F) * amp;
			float dy = (float) Math.cos(t * 2.3F + i * 1.3F + idx * 3F) * amp;
			g.pose().pushMatrix();
			g.pose().translate(x + dx, y + dy);
			g.pose().scale(s, s);
			g.drawString(font, c, 0, 0, alpha | (hot ? 0xE01B24 : 0xE8DED2), true);
			g.pose().popMatrix();
			x += font.width(c) * s;
		}
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent e, boolean dbl) {
		if (hover >= 0 && hover < options.size() && age > 8) {
			answer(options.get(hover));
			return true;
		}
		return super.mouseClicked(e, dbl);
	}

	@Override
	public boolean keyPressed(KeyEvent e) {
		int k = e.key() - GLFW.GLFW_KEY_1;
		if (k >= 0 && k < options.size() && k < 9 && age > 8) {
			answer(options.get(k));
			return true;
		}
		return super.keyPressed(e);
	}
}
