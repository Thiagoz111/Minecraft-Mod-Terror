package com.deadline.horror.casa;

import com.deadline.director.Run;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A tap of the house running (the kitchen sink, the washbasins, the bathtub, the laundry sink): water falling from its
 * spout, and in the later acts the water turning into thick blood (event 29 'canilla_sangre', the interactable from
 * act 4). Pure particles and sound: nothing in the world changes. The owner ticks it and stops it.
 */
public final class Tap {
	/** Spout of each tap model (north model, pixels) and how far the water falls (pixels). */
	private record Spout(double x, double y, double z, double fall) {
	}

	private static final Map<String, Spout> SPOUTS = Map.of(
			"casa_mesada_pileta", new Spout(8.0, 15.2, 9.8, 6.0),
			"casa_lavatorio", new Spout(8.0, 13.5, 10.9, 2.8),
			"casa_banadera_izq", new Spout(12.9, 10.9, 8.1, 9.0),
			"casa_pileta_lavar", new Spout(11.3, 14.5, 12.4, 4.2));
	private static final DustParticleOptions BLOOD = new DustParticleOptions(0x4A0306, 1.6F);
	private static final DustParticleOptions BLOOD_DARK = new DustParticleOptions(0x2A0103, 2.0F);

	public final Run run;
	public final BlockPos pos;
	private final Vec3 spout;
	private final double fall;
	private final int bloodAt;
	private final int length;
	private int t;
	private boolean done;

	private Tap(Run run, BlockPos pos, Vec3 spout, double fall, int bloodAt, int length) {
		this.run = run;
		this.pos = pos.immutable();
		this.spout = spout;
		this.fall = fall;
		this.bloodAt = bloodAt;
		this.length = length;
	}

	public static boolean is(BlockState s) {
		return SPOUTS.containsKey(Polter.key(s));
	}

	/**
	 * Opens the tap at pos for `ticks`: water, and from `bloodAt` ticks on (negative: never) thick blood.
	 * Null when pos is not a tap.
	 */
	public static Tap open(Run r, BlockPos pos, int bloodAt, int ticks) {
		BlockState s = r.level.getBlockState(pos);
		Spout sp = SPOUTS.get(Polter.key(s));
		if (sp == null) {
			return null;
		}
		Direction f = Polter.facing(s);
		Vec3 at = Polter.local(pos, f, sp.x(), sp.y(), sp.z());
		r.sound(ModSounds.POLTER_CANILLA, at, 0.9F, 1.0F);
		return new Tap(r, pos, at, sp.fall() / 16.0, bloodAt, ticks);
	}

	public Vec3 spout() {
		return spout;
	}

	public boolean blood() {
		return bloodAt >= 0 && t >= bloodAt;
	}

	/** One tick of running water (or blood); true when it has stopped. */
	public boolean tick() {
		if (done) {
			return true;
		}
		t++;
		if (bloodAt >= 0 && t == bloodAt) {
			run.sound(ModSounds.POLTER_CANILLA_SANGRE, spout, 1.0F, 1.0F);
		}
		if (bloodAt >= 0 && t > bloodAt && (t - bloodAt) % 80 == 0 && t < length - 20) {
			run.sound(ModSounds.POLTER_CANILLA_SANGRE, spout, 0.9F, 0.9F);
		} else if (!blood() && t % 80 == 0 && t < length - 20) {
			run.sound(ModSounds.POLTER_CANILLA, spout, 0.6F, 1.05F);
		}
		Vec3 mid = spout.add(0, -fall / 2, 0);
		if (blood()) {
			// thick: it comes in gouts, not a stream
			if (t % 3 != 0 || run.level.getRandom().nextFloat() < 0.6F) {
				run.level.sendParticles(BLOOD, mid.x, mid.y, mid.z, 3, 0.015, fall * 0.4, 0.015, 0.0);
				run.level.sendParticles(ModParticles.BLOOD_DRIP, spout.x, spout.y - 0.02, spout.z, 1, 0.01, 0.0, 0.01, 0.0);
			}
			if (t % 4 == 0) {
				Vec3 b = spout.add(0, -fall, 0);
				run.level.sendParticles(BLOOD_DARK, b.x, b.y + 0.02, b.z, 2, 0.08, 0.0, 0.08, 0.0);
			}
		} else {
			run.level.sendParticles(ParticleTypes.FALLING_WATER, spout.x, spout.y - 0.02, spout.z, 3, 0.01, 0.0, 0.01, 0.0);
			if (t % 3 == 0) {
				Vec3 b = spout.add(0, -fall, 0);
				run.level.sendParticles(ParticleTypes.SPLASH, b.x, b.y + 0.03, b.z, 2, 0.05, 0.0, 0.05, 0.0);
			}
		}
		if (t >= length) {
			stop();
			return true;
		}
		return false;
	}

	/** Closes the tap: the valve squeaks shut. */
	public void stop() {
		if (!done) {
			done = true;
			Polter.stopSound(run, ModSounds.POLTER_CANILLA);
			Polter.stopSound(run, ModSounds.POLTER_CANILLA_SANGRE);
			run.sound(ModSounds.POLTER_LLAVE_LUZ, spout, 0.5F, 0.6F);
		}
	}

	public boolean done() {
		return done;
	}
}
