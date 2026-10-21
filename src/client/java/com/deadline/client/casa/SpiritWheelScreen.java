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
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

/**
 * The spirit box question wheel: the radio dial sweeping in the middle, the questions around it (up to four, one per
 * side; more go on a circle). Click one or press its number; the answer comes through the static.
 */
public class SpiritWheelScreen extends Screen {
	private static final int CARD_W = 118;

	private final List<String> questions;
	private final int asked;
	private final List<int[]> cards = new ArrayList<>();
	private int age;
	private int hover = -1;

	public SpiritWheelScreen(List<String> questions, int askedMask) {
		super(Component.translatable("deadline.casa.spirit.title"));
		this.questions = List.copyOf(questions);
		this.asked = askedMask;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	protected void init() {
		if (age == 0) {
			Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.SPIRIT_BOX_STATIC, 1.0F, 0.5F));
		}
	}

	@Override
	public void tick() {
		age++;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		float k = Mth.clamp((age + pt) / 6F, 0F, 1F);
		g.fillGradient(0, 0, width, height, (int) (k * 0x90) << 24 | 0x020806, (int) (k * 0xD0) << 24 | 0x050A08);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		float t = age + pt;
		float in = Mth.clamp(t / 6F, 0F, 1F);
		int a = (int) (in * 255) << 24;
		int cx = width / 2;
		int cy = height / 2;
		int n = questions.size();
		float reach = Math.min(width * 0.3F, 150F) * (0.7F + 0.3F * in);
		float reachY = Math.min(height * 0.3F, 90F) * (0.7F + 0.3F * in);

		// layout: one card per side for up to four questions (top, right, bottom, left), else around a circle
		cards.clear();
		hover = -1;
		List<List<FormattedCharSequence>> texts = new ArrayList<>();
		for (int i = 0; i < n; i++) {
			List<FormattedCharSequence> lines = font.split(Component.translatable("deadline.casa.spirit.q." + questions.get(i)), CARD_W - 12);
			texts.add(lines);
			int ch = lines.size() * 10 + 14;
			double ang = n <= 4 ? -Math.PI / 2 + i * Math.PI / 2 : -Math.PI / 2 + i * Math.PI * 2 / n;
			int qx = cx + (int) Math.round(Math.cos(ang) * reach);
			int qy = cy + (int) Math.round(Math.sin(ang) * reachY);
			int x0 = qx - CARD_W / 2;
			int y0 = qy - ch / 2;
			cards.add(new int[] {x0, y0, x0 + CARD_W, y0 + ch, qx, qy});
			if (mx >= x0 && mx < x0 + CARD_W && my >= y0 && my < y0 + ch) {
				hover = i;
			}
		}

		// wires from the dial to each question (straight ones only for the cross layout)
		if (n <= 4) {
			for (int i = 0; i < n; i++) {
				int[] c = cards.get(i);
				int col = (i == hover ? 0xCC5CFF9A : 0x5530A060) & 0x00FFFFFF | (int) (in * (i == hover ? 0xCC : 0x55)) << 24;
				if (c[4] == cx) {
					int y0 = Math.min(cy, c[5]);
					int y1 = Math.max(cy, c[5]);
					g.fill(cx, y0, cx + 1, y1, col);
				} else {
					int x0 = Math.min(cx, c[4]);
					int x1 = Math.max(cx, c[4]);
					g.fill(x0, cy, x1, cy + 1, col);
				}
			}
		}

		drawDial(g, cx, cy, t, a);

		for (int i = 0; i < n; i++) {
			int[] c = cards.get(i);
			boolean hot = i == hover;
			boolean done = (asked & (1 << i)) != 0;
			g.fill(c[0], c[1], c[2], c[3], (int) (in * (hot ? 0xF0 : 0xD8)) << 24 | (hot ? 0x10301C : 0x0C1410));
			g.renderOutline(c[0], c[1], c[2] - c[0], c[3] - c[1], a | (hot ? 0x5CFF9A : 0x2A5A3A));
			String num = (i + 1) + (done ? " ✓" : "");
			g.drawString(font, num, c[0] + 4, c[1] + 3, a | (done ? 0x5A7A66 : 0x5CFF9A), false);
			int ty = c[1] + 12;
			for (FormattedCharSequence l : texts.get(i)) {
				g.drawString(font, l, (c[0] + c[2]) / 2 - font.width(l) / 2, ty, a | (hot ? 0xFFFFFF : done ? 0x8A9A90 : 0xD8E8DC), false);
				ty += 10;
			}
		}
		Component help = Component.translatable("deadline.casa.spirit.sub");
		g.drawString(font, help, (width - font.width(help)) / 2, height - 22, a | 0x6A8A76, false);
	}

	/** The radio in the middle: a frequency that never settles and a needle of static. */
	private void drawDial(GuiGraphics g, int cx, int cy, float t, int a) {
		int w = 92;
		int h = 40;
		g.fill(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, a | 0x061008);
		g.renderOutline(cx - w / 2, cy - h / 2, w, h, a | 0x2A5A3A);
		Component title = Component.translatable("deadline.casa.spirit.title");
		g.drawString(font, title, cx - font.width(title) / 2, cy - h / 2 + 4, a | 0x5CFF9A, false);
		float sweep = (float) (Math.sin(t * 0.21F) * 0.5 + 0.5);
		float mhz = 87.5F + sweep * 20.5F + (float) Math.sin(t * 1.7F) * 0.15F;
		String freq = String.format(Locale.ROOT, "%.1f MHz", mhz);
		g.drawString(font, freq, cx - font.width(freq) / 2, cy - 3, a | 0xD8E8DC, false);
		// the scale with the needle
		int sx0 = cx - w / 2 + 6;
		int sx1 = cx + w / 2 - 6;
		int sy = cy + h / 2 - 8;
		for (int x = sx0; x <= sx1; x += 4) {
			int noise = (int) ((Math.sin(x * 0.9F + ClientState.ticks * 1.3F) * 0.5 + 0.5) * 4);
			g.fill(x, sy - noise, x + 1, sy + 1, a | 0x2A5A3A);
		}
		int nx = sx0 + (int) ((sx1 - sx0) * sweep);
		g.fill(nx, sy - 6, nx + 1, sy + 2, a | 0xE33A3A);
	}

	private void ask(int i) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 0.8F));
		CasaClientNet.send(CasaNet.ActionPayload.SPIRIT, questions.get(i));
		onClose();
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent e, boolean dbl) {
		if (hover >= 0 && hover < questions.size() && age > 4) {
			ask(hover);
			return true;
		}
		return super.mouseClicked(e, dbl);
	}

	@Override
	public boolean keyPressed(KeyEvent e) {
		int k = e.key() - GLFW.GLFW_KEY_1;
		if (k >= 0 && k < questions.size() && k < 9) {
			ask(k);
			return true;
		}
		return super.keyPressed(e);
	}
}
