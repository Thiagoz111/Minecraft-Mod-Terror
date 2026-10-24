package com.deadline.horror.casa;

import com.deadline.casa.CasaProps;
import com.deadline.director.Run;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;

/**
 * The Nona's rocking chair rocking with nobody in it. The block is lifted into an identical display (CasaProps.lift)
 * that tips back and forth on its rockers (about the model's side-to-side axis at the floor) and is put back as the
 * block when it stops. Two ways: {@link #gentle} (a push, slowing down: the interactable) and {@link #frenzy} (event 27:
 * faster and faster, then a dead stop, in step with the POLTER_MECEDORA sound, whose creaks were rendered from the
 * same timeline: see tools/audio/snd_polter.py mecedora()).
 */
public final class Rocker {
	/** Frenzy timeline (ticks): it builds for RAMP ticks, then stops dead. Must match snd_polter.py. */
	public static final int RAMP = 118;
	private static final double F0 = 0.42, F1 = 1.75, A0 = 0.07, A1 = 0.21;

	public final Run run;
	public final BlockPos pos;
	private final String actor;
	private final Vec3 axis;
	private final boolean frenzy;
	private final int length;
	private double phase;
	private int t;
	private boolean done;

	private Rocker(Run run, BlockPos pos, String actor, Direction f, boolean frenzy, int length) {
		this.run = run;
		this.pos = pos.immutable();
		this.actor = actor;
		this.axis = Polter.localDir(f, 1, 0, 0);
		this.frenzy = frenzy;
		this.length = length;
	}

	public static boolean is(BlockState s) {
		return Polter.key(s).equals("casa_mecedora");
	}

	/** A push: it rocks for `ticks`, slower and slower (ROCKING_CREAK_SLOW). Null if it cannot be lifted. */
	public static Rocker gentle(Run r, BlockPos pos, int ticks) {
		Rocker k = make(r, pos, false, ticks);
		if (k != null) {
			r.sound(ModSounds.ROCKING_CREAK_SLOW, Vec3.atCenterOf(pos), 0.9F, 1.0F);
		}
		return k;
	}

	/** Event 27: faster and faster, then a dead stop (POLTER_MECEDORA). */
	public static Rocker frenzy(Run r, BlockPos pos) {
		Rocker k = make(r, pos, true, RAMP + 30);
		if (k != null) {
			r.sound(ModSounds.POLTER_MECEDORA, Vec3.atCenterOf(pos).add(0, 0.4, 0), 1.1F, 1.0F);
		}
		return k;
	}

	private static Rocker make(Run r, BlockPos pos, boolean frenzy, int ticks) {
		BlockState s = r.level.getBlockState(pos);
		if (!is(s)) {
			return null;
		}
		String actor = CasaProps.uid("mecedora");
		Display.BlockDisplay d = CasaProps.lift(r, pos, actor);
		if (d == null) {
			return null;
		}
		CasaProps.move(d, Vec3.atBottomCenterOf(pos));
		CasaProps.pose(d, new Quaternionf(), 1F, CasaProps.FLOOR, 0);
		return new Rocker(r, pos, actor, Polter.facing(s), frenzy, ticks);
	}

	/** One tick of rocking; true once it is still and back in place. */
	public boolean tick() {
		if (done) {
			return true;
		}
		Display d = run.actor(actor) instanceof Display x ? x : null;
		if (d == null) {
			done = true;  // removed from outside: the remembered block comes back by itself
			return true;
		}
		t++;
		double angle;
		if (frenzy) {
			if (t <= RAMP) {
				double u = t / (double) RAMP;
				double f = F0 + (F1 - F0) * Math.pow(u, 1.5);
				phase += 2 * Math.PI * f / 20.0;
				angle = (A0 + (A1 - A0) * u) * Math.sin(phase);
			} else {
				angle = 0;  // dead stop: and it stays like that, too still
			}
		} else {
			double u = t / (double) length;
			phase += 2 * Math.PI * 0.5 / 20.0;
			angle = 0.12 * (1 - u) * (1 - u) * Math.sin(phase);
		}
		if (t % 2 == 0 || frenzy && t == RAMP + 1) {
			int lerp = frenzy && t == RAMP + 1 ? 1 : 2;
			CasaProps.pose(d, new Quaternionf().rotationAxis((float) angle, (float) axis.x, 0F, (float) axis.z), 1F, CasaProps.FLOOR, lerp);
		}
		if (t >= length) {
			stop();
			return true;
		}
		return false;
	}

	public int age() {
		return t;
	}

	/** Puts the chair back as the block now. */
	public void stop() {
		if (!done) {
			done = true;
			CasaProps.settle(run, pos, actor);
		}
	}

	public boolean done() {
		return done;
	}
}
