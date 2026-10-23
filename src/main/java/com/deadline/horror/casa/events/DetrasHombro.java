package com.deadline.horror.casa.events;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * 38 detras_hombro (acts 4-6, intensity 5, SCARE -- a jumpscare: the haunt allows one every 3 minutes, never in the
 * first 4): a breath right behind his ear. If he whips round (more than ~100 degrees inside a third of a second) the red
 * face is there, pressed against his, for half a second (Fx.jumpscare 'cara_roja'). If he does not turn, only the
 * breath was there.
 */
public class DetrasHombro extends HorrorEvent {
	private static final int WINDOW = 6;
	private static final float TURN = 100F;

	public DetrasHombro() {
		super("detras_hombro", Kind.SCARE);
		this.acts(4, 6).intensity(5).cooldown(300).weight(6);
	}

	@Override
	public boolean canRun(Ctx c) {
		return Apparitions.canScare(c) && c.p.getDeltaMovement().horizontalDistance() < 0.2;
	}

	@Override
	public void start(Ctx c) {
		float[] yaw = new float[WINDOW + 1];
		java.util.Arrays.fill(yaw, c.p.getYRot());
		c.put("yaw", yaw);
		breathe(c, 0.9F);
	}

	private static void breathe(Ctx c, float vol) {
		Vec3 ear = c.p.getEyePosition().add(c.p.getViewVector(1F).scale(-0.6));
		Apparitions.sound(c, ModSounds.APARICION_ALIENTO, ear, vol, 0.9F);
	}

	@Override
	public boolean tick(Ctx c) {
		if (Apparitions.hidden(c.p)) {
			return true;
		}
		float[] yaw = c.get("yaw");
		System.arraycopy(yaw, 0, yaw, 1, WINDOW);
		yaw[0] = c.p.getYRot();
		if (c.t == 50) {
			breathe(c, 1.1F);  // again, closer
		}
		if (c.t > 2 && Math.abs(Mth.wrapDegrees(yaw[0] - yaw[WINDOW])) > TURN) {
			Fx.jumpscare(c.p, "cara_roja");
			Fx.shake(c.p, 1.3F, 14);
			Fx.redFlash(c.p, 0.6F);
			SanityManager.add(c.p, -14F);
			return true;
		}
		return c.t > 20 * 7;
	}

	@Override
	public int maxTicks() {
		return 20 * 9;
	}
}
