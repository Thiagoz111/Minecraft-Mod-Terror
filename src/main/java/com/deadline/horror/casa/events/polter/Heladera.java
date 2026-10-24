package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Fridge;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

/**
 * 31 heladera (acts 2-5, intensity 3): the kitchen fridge swings open by itself. Inside, a dying bulb flickering, and
 * on the middle shelf something wrapped in white paper, the size of a small animal, that moves. If he comes close or
 * touches it, the door slams shut.
 */
public class Heladera extends HorrorEvent {
	public Heladera() {
		super("heladera", Kind.POLTER);
		this.acts(2, 5).intensity(3).cooldown(260).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.has(c.run, "heladera")) {
			return false;
		}
		CasaProps.sweep(c.run);
		BlockPos lower = null;
		for (BlockPos p : Polter.kitNear(c.run, c.run.at("heladera"), 2, 2, k -> k.startsWith("casa_heladera_"))) {
			lower = Fridge.lowerOf(c.run, p);
			if (lower != null) {
				break;
			}
		}
		if (lower == null || CasaProps.held(c.run, lower)) {
			return false;
		}
		Vec3 v = Vec3.atCenterOf(lower).add(0, 0.5, 0);
		double d = Apparitions.dist(c, v);
		String room = HouseQuery.roomAt(c.run, v);
		if (d < 2.5 || d > 11.0 || room == null || !room.equals(c.room()) && !Apparitions.sees(c, v, 50F)) {
			return false;
		}
		c.put("lower", lower);
		return true;
	}

	@Override
	public void start(Ctx c) {
		BlockPos lower = c.get("lower");
		Fridge f = Fridge.open(c.run, lower);
		c.put("fridge", f);
		if (f == null) {
			return;
		}
		c.put("bundle", f.addBlock(Blocks.WHITE_WOOL.defaultBlockState(), 3.6, 9.4, 4.0, 12.0, 12.8, 11.4));
		Polter.noise(c.run, Vec3.atCenterOf(lower), 20F);
	}

	@Override
	public boolean tick(Ctx c) {
		Fridge f = c.get("fridge");
		if (f == null) {
			return true;
		}
		if (!f.open()) {
			return f.tick();
		}
		f.tick();
		Vec3 front = Vec3.atCenterOf(f.lower).add(0, 0.5, 0);
		// the bulb is dying
		f.light(c.rnd.nextFloat() < 0.3F ? 2 + c.rnd.nextInt(5) : 10 + c.rnd.nextInt(3));
		if (c.t % 100 == 0) {
			c.run.sound(ModSounds.POLTER_HELADERA, front, 0.7F, 0.95F);
		}
		String bundle = c.get("bundle");
		Entity b = bundle == null ? null : c.run.actor(bundle);
		if (b != null) {
			Vec3 home = c.get("home");
			if (home == null) {
				home = b.position();
				c.put("home", home);
			}
			if (c.rnd.nextFloat() < 0.1F) {
				// it twitches inside its paper
				CasaProps.move(b, home.add((c.rnd.nextFloat() - 0.5) * 0.05, c.rnd.nextFloat() * 0.04, (c.rnd.nextFloat() - 0.5) * 0.05));
				if (c.rnd.nextFloat() < 0.5F) {
					c.run.sound(ModSounds.POLTER_PAPEL, home, 0.7F, Polter.pitch(c, 0.8F, 1.1F));
				}
			} else if (c.t % 6 == 0) {
				CasaProps.move(b, home);
			}
			if (c.t % 9 == 0) {
				Vec3 drip = f.inside(9.2);
				c.level().sendParticles(ModParticles.BLOOD_DRIP, drip.x, drip.y, drip.z, 1, 0.12, 0.0, 0.12, 0.0);
			}
		}
		if (Polter.got(c, "heladera") || Apparitions.dist(c, front) < 1.7) {
			f.close();
			c.run.sound(ModSounds.DOOR_SLAM, front, 1.0F, 1.3F);
			Polter.noise(c.run, front, 50F);
			return false;
		}
		if (c.t > 20 * 40 && !Apparitions.sees(c, front, 60F)) {
			f.close();
		}
		return false;
	}

	@Override
	public void stop(Ctx c) {
		Fridge f = c.get("fridge");
		if (f != null) {
			f.end();
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 60;
	}
}
