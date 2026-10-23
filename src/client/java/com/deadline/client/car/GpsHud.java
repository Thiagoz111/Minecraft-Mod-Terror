package com.deadline.client.car;

import com.deadline.car.GpsPayload;
import com.deadline.client.ClientState;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;

/**
 * The GPS of an accepted overworld case (docs/design/casa_terror.md 6.9): an arrow at the top centre pointing at the
 * house relative to where the hunter looks, and the distance ("312 m"), styled like the checklist panel. Hidden within
 * 30 blocks of the arrival marker. The target comes from the server ({@link GpsPayload}).
 */
public final class GpsHud {
	public static final double HIDE = 30.0;
	public static boolean on;
	public static double x, y, z;
	public static String caseKey = "";
	private static float shownAngle;
	private static float alpha;

	private GpsHud() {
	}

	public static void onPayload(GpsPayload p) {
		on = p.on();
		x = p.x();
		y = p.y();
		z = p.z();
		caseKey = p.on() ? p.caseKey() : "";
	}

	public static void reset() {
		on = false;
		caseKey = "";
		alpha = 0F;
	}

	/** Horizontal distance from the player to the target (MAX_VALUE without a target). */
	public static double distance(Player pl) {
		if (!on || pl == null) {
			return Double.MAX_VALUE;
		}
		double dx = x - pl.getX();
		double dz = z - pl.getZ();
		return Math.sqrt(dx * dx + dz * dz);
	}

	public static void render(GuiGraphics g, Font font, int w, int h, float pt) {
		Minecraft mc = Minecraft.getInstance();
		Player pl = mc.player;
		double dist = distance(pl);
		boolean show = on && pl != null && dist > HIDE;
		alpha = Mth.clamp(alpha + (show ? 0.08F : -0.08F), 0F, 1F);
		if (alpha <= 0.01F || pl == null) {
			return;
		}
		double dx = x - pl.getX();
		double dz = z - pl.getZ();
		float targetYaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
		float rel = Mth.wrapDegrees(targetYaw - pl.getYRot(pt));
		shownAngle += Mth.wrapDegrees(rel - shownAngle) * 0.35F;
		int a = (int) (alpha * 255) << 24;
		int aBg = (int) (alpha * 0xB0) << 24;
		int aBg2 = (int) (alpha * 0x50) << 24;

		int pw = 74;
		int ph = 34;
		int px = (w - pw) / 2;
		int py = ClientState.vhs ? 22 : 4;
		g.fillGradient(px, py, px + pw, py + ph, aBg | 0x0A0608, aBg2);
		g.fill(px, py, px + pw, py + 1, a | 0xB3121B);
		g.fill(px, py + ph - 1, px + pw, py + ph, (int) (alpha * 0x55) << 24 | 0xB3121B);

		// the arrow: straight up = straight ahead; it pulses red when the house is behind you
		boolean behind = Math.abs(rel) > 100F;
		boolean pulse = behind && (ClientState.ticks / 6) % 2 == 0;
		int col = pulse ? 0xFF3B3B : 0xF2ECE4;
		g.pose().pushMatrix();
		g.pose().translate(px + 17F, py + ph / 2F);
		g.pose().rotate((float) Math.toRadians(shownAngle));
		arrow(g, 0x000000, a, 1);
		arrow(g, col, a, 0);
		g.pose().popMatrix();

		String meters = Mth.floor(dist) + " m";
		g.drawString(font, meters, px + 32, py + 8, a | 0xF2ECE4, true);
		Component label = Component.translatable("deadline.gps.label");
		g.drawString(font, label, px + 32, py + 20, a | 0xE33A3A, false);
	}

	/** An arrow pointing up (-y) around the origin; grow = 1 draws its dark outline. */
	private static void arrow(GuiGraphics g, int rgb, int a, int grow) {
		int c = a | rgb;
		for (int i = 0; i <= 6; i++) {
			g.fill(-i - grow, -9 + i - grow, i + 1 + grow, -8 + i + grow, c);  // head (a triangle of rows)
		}
		g.fill(-2 - grow, -2 - grow, 3 + grow, 9 + grow, c);                  // shaft
	}
}
