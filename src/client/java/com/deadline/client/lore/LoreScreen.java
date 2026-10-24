package com.deadline.client.lore;

import com.deadline.DeadLine;
import com.deadline.horror.casa.lore.LoreBook;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

/**
 * A document of the house held up to the eyes, full screen: an old letter, a page of Lucía's notebook, a photograph of
 * 1961 and its back, the broken rosary. No voice reads it. A click (or the right arrow, space) turns to the next page,
 * the left arrow goes back, Esc puts it down. The world goes on behind it: it does not pause the game.
 */
public class LoreScreen extends Screen {
	private final List<LoreBook.Page> pages;
	private int page;
	private int age;
	private int turnedAt;

	public LoreScreen(LoreBook.Doc doc, boolean late) {
		super(Component.empty());
		this.pages = doc.pages(late);
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
		g.fillGradient(0, 0, width, height, (int) (k * 0xC0) << 24 | 0x070405, (int) (k * 0xE6) << 24);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		if (pages.isEmpty()) {
			return;
		}
		LoreBook.Page p = pages.get(Mth.clamp(page, 0, pages.size() - 1));
		float in = Mth.clamp((age - turnedAt + pt) / 5F, 0F, 1F);
		int alpha = Math.max(8, (int) (in * 255));
		switch (p.kind()) {
			case PAPER -> paper(g, p, alpha);
			case PHOTO -> photo(g, p, alpha);
			case OBJECT -> object(g, p, alpha);
		}
		// page count and how to turn it, small, at the bottom
		int dim = alpha * 160 / 255 << 24;
		if (pages.size() > 1) {
			String n = (page + 1) + " / " + pages.size();
			g.drawString(font, n, width / 2 - font.width(n) / 2, height - 22, dim | 0x9A9080, false);
		}
		Component hint = Component.translatable("deadline.lore.hint");
		g.drawString(font, hint, width / 2 - font.width(hint) / 2, height - 11, dim | 0x6A6258, false);
	}

	private static Identifier tex(LoreBook.Page p) {
		return DeadLine.id(p.texture());
	}

	private static int ink(int argb, int alpha) {
		return alpha << 24 | argb & 0xFFFFFF;
	}

	/** A sheet of paper with its text written on it (in texture pixels, scaled with the sheet). */
	private void paper(GuiGraphics g, LoreBook.Page p, int alpha) {
		float s = Math.min((height - 40F) / p.h(), (width * 0.9F) / p.w());
		float x0 = (width - p.w() * s) / 2F;
		float y0 = (height - 30F - p.h() * s) / 2F;
		g.pose().pushMatrix();
		g.pose().translate(x0 + 3F, y0 + 4F);
		g.fill(0, 0, Math.round(p.w() * s), Math.round(p.h() * s), alpha * 120 / 255 << 24);  // its shadow
		g.pose().popMatrix();
		g.pose().pushMatrix();
		g.pose().translate(x0, y0);
		g.pose().scale(s, s);
		g.blit(RenderPipelines.GUI_TEXTURED, tex(p), 0, 0, 0F, 0F, p.w(), p.h(), p.w(), p.h(), alpha << 24 | 0xFFFFFF);
		if (p.text() != null) {
			// red crayon is written big
			float k = p.ink() == LoreBook.CRAYON ? 1.45F : 1F;
			int wrap = Math.round(p.width() / k);
			float y = p.y();
			for (FormattedCharSequence line : font.split(Component.translatable(p.text()), wrap)) {
				if (y + p.line() * k > p.h() - 6) {
					break;
				}
				g.pose().pushMatrix();
				g.pose().translate(p.x(), y);
				g.pose().scale(k, k);
				g.drawString(font, line, 0, 0, ink(p.ink(), alpha), false);
				g.pose().popMatrix();
				y += p.line() * k;
			}
		}
		g.pose().popMatrix();
	}

	/** A photograph on its card, a little askew. */
	private void photo(GuiGraphics g, LoreBook.Page p, int alpha) {
		int border = 7;
		int cw = p.w() + border * 2;
		int ch = p.h() + border * 2 + 12;
		float s = Math.min((height - 50F) / ch, (width * 0.8F) / cw);
		g.pose().pushMatrix();
		g.pose().translate(width / 2F, (height - 30F) / 2F);
		g.pose().rotate(-0.035F);
		g.pose().scale(s, s);
		g.pose().translate(-cw / 2F, -ch / 2F);
		g.fill(3, 4, cw + 3, ch + 4, alpha * 120 / 255 << 24);
		g.fill(0, 0, cw, ch, alpha << 24 | 0xDDD4C2);
		g.fill(border - 1, border - 1, border + p.w() + 1, border + p.h() + 1, alpha << 24 | 0x2A2420);
		g.blit(RenderPipelines.GUI_TEXTURED, tex(p), border, border, 0F, 0F, p.w(), p.h(), p.w(), p.h(), alpha << 24 | 0xFFFFFF);
		g.pose().popMatrix();
	}

	/** Something seen up close, with a line under it. */
	private void object(GuiGraphics g, LoreBook.Page p, int alpha) {
		float s = Math.min((height - 90F) / p.h(), (width * 0.8F) / p.w());
		float x0 = (width - p.w() * s) / 2F;
		float y0 = Math.max(8F, (height - 60F - p.h() * s) / 2F);
		g.pose().pushMatrix();
		g.pose().translate(x0, y0);
		g.pose().scale(s, s);
		g.blit(RenderPipelines.GUI_TEXTURED, tex(p), 0, 0, 0F, 0F, p.w(), p.h(), p.w(), p.h(), alpha << 24 | 0xFFFFFF);
		g.pose().popMatrix();
		if (p.text() != null) {
			int y = Math.round(y0 + p.h() * s + 10F);
			for (FormattedCharSequence line : font.split(Component.translatable(p.text()), Math.min(width - 40, p.width()))) {
				g.drawString(font, line, width / 2 - font.width(line) / 2, y, ink(p.ink(), alpha), false);
				y += p.line();
			}
		}
	}

	private void turn(int dir) {
		int next = page + dir;
		if (next >= pages.size()) {
			onClose();
			return;
		}
		if (next < 0) {
			return;
		}
		page = next;
		turnedAt = age;
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.LORE_PAPEL, 0.9F + 0.2F * (page % 3) / 2F, 0.6F));
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent e, boolean dbl) {
		turn(1);
		return true;
	}

	@Override
	public boolean keyPressed(KeyEvent e) {
		int k = e.key();
		if (k == GLFW.GLFW_KEY_RIGHT || k == GLFW.GLFW_KEY_SPACE || k == GLFW.GLFW_KEY_ENTER || k == GLFW.GLFW_KEY_D) {
			turn(1);
			return true;
		}
		if (k == GLFW.GLFW_KEY_LEFT || k == GLFW.GLFW_KEY_BACKSPACE || k == GLFW.GLFW_KEY_A) {
			turn(-1);
			return true;
		}
		return super.keyPressed(e);
	}
}
