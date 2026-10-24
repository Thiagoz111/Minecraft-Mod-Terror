package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.FlyingProp;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * 23 platos_vuelan (acts 3-5, intensity 4): the sideboard spits its plates out, one after another, and they smash all
 * around him (a few hit him: a little damage, never more). {@link FlyingProp}s: thrown with an arc, spinning, they
 * shatter into shards of the plate model on whatever they hit.
 */
public class PlatosVuelan extends HorrorEvent {
	public PlatosVuelan() {
		super("platos_vuelan", Kind.POLTER);
		this.acts(3, 5).intensity(4).cooldown(300).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.has(c.run, "aparador")) {
			return false;
		}
		Vec3 a = c.run.at("aparador");
		String room = HouseQuery.roomAt(c.run, a.add(0, 0.5, 0));
		double d = Apparitions.dist(c, a);
		return d >= 2.5 && d <= 9.0 && room != null && room.equals(c.room())
				&& Apparitions.clear(c.run, a.add(0, 1.3, 0), c.p.getEyePosition(), c.p);
	}

	/** Where the plates come out: in front of the sideboard's hutch (its plate rail), else over the marker. */
	private static List<Vec3> mouths(Ctx c) {
		List<Vec3> out = new ArrayList<>();
		for (BlockPos rel : c.run.def.group("aparador_platos")) {
			BlockPos p = c.run.origin.offset(rel);
			out.add(Polter.local(p, Polter.facing(c.level().getBlockState(p)), 8.0, 18.0, -3.0));
		}
		if (out.isEmpty()) {
			out.add(c.run.at("aparador").add(0, 1.3, 0));
		}
		return out;
	}

	@Override
	public void start(Ctx c) {
		c.put("props", new ArrayList<FlyingProp>());
		c.put("left", 7 + c.rnd.nextInt(4));
		c.put("next", 6);
		Vec3 m = mouths(c).get(0);
		c.run.sound(ModSounds.PLATE_STORM, m, 1.6F, 1.0F);
		Polter.noise(c.run, m, 55F);
	}

	@Override
	public boolean tick(Ctx c) {
		List<FlyingProp> props = c.get("props");
		int left = c.get("left");
		int next = c.get("next");
		if (left > 0 && c.t >= next) {
			List<Vec3> mouths = mouths(c);
			Vec3 from = mouths.get(c.rnd.nextInt(mouths.size())).add(c.rnd.nextDouble() * 0.4 - 0.2, c.rnd.nextDouble() * 0.2, c.rnd.nextDouble() * 0.4 - 0.2);
			// around him: most smash at his feet and on the walls beside him, one in three is at him
			boolean atHim = c.rnd.nextInt(3) == 0;
			double spread = atHim ? 0.2 : 0.9 + c.rnd.nextDouble() * 0.9;
			double ang = c.rnd.nextDouble() * Math.PI * 2;
			Vec3 to = c.p.position().add(Math.cos(ang) * spread, atHim ? 1.2 : 0.2 + c.rnd.nextDouble() * 1.4, Math.sin(ang) * spread);
			BlockState plate = CasaProps.kitOr("casa_plato", Blocks.WHITE_CARPET.defaultBlockState());
			FlyingProp f = FlyingProp.spawn(c.run, from, plate, c.rnd.nextFloat() * 6.28F, FlyingProp.FLAT);
			if (f != null) {
				f.breakable(ModSounds.PLATE_SHATTER).radius(0.15).damage(1.5F).loud(45F).hitSound(null)
						.spin(new net.minecraft.world.phys.Vec3(0, 1, 0), 0.5F + c.rnd.nextFloat() * 0.3F)
						.throwAt(to, 0.5 + c.rnd.nextDouble() * 0.2);
				if (c.rnd.nextInt(3) < 2) {
					c.run.sound(ModSounds.PLATE_WHOOSH, from, 1.0F, Polter.pitch(c, 0.9F, 1.2F));
				}
				props.add(f);
			}
			c.put("left", left - 1);
			c.put("next", c.t + 4 + c.rnd.nextInt(4));
		}
		boolean flying = false;
		for (FlyingProp f : props) {
			if (f.moving()) {
				f.tick();
				if (f.hit() == c.p && f.broken()) {
					Fx.shake(c.p, 0.4F, 8);
				}
				flying = true;
			}
		}
		return left <= 0 && !flying;
	}

	@Override
	public void stop(Ctx c) {
		FlyingProp.restoreAll(c.get("props"));
	}

	@Override
	public int maxTicks() {
		return 20 * 20;
	}
}
