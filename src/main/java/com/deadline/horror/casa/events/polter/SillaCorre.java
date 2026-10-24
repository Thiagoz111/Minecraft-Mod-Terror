package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.FlyingProp;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.Vec3;

/**
 * 21 silla_corre (acts 1-5, intensity 2): a chair he is looking at drags itself a few blocks across the floor, in
 * jerks, and stops. It is back in its place once he is not looking.
 */
public class SillaCorre extends HorrorEvent {
	public static final Set<String> CHAIRS = Set.of("casa_silla_comedor", "casa_silla_cocina", "casa_silla_nena", "casa_silla_jorge",
			"casa_silla_gamer", "casa_silla_plastica");

	public SillaCorre() {
		super("silla_corre", Kind.POLTER);
		this.acts(1, 5).intensity(2).cooldown(110).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		CasaProps.sweep(c.run);
		for (BlockPos ch : Polter.kitNear(c.run, c.p.position(), 12, 2, CHAIRS::contains)) {
			Vec3 cc = Vec3.atCenterOf(ch);
			double d = Apparitions.dist(c, cc);
			if (d < 3.5 || d > 13.0 || CasaProps.held(c.run, ch) || !Apparitions.sees(c, cc, 35F)) {
				continue;
			}
			BlockPos dest = path(c, ch);
			if (dest != null) {
				c.put("chair", ch);
				c.put("dest", dest);
				return true;
			}
		}
		return false;
	}

	/** 2-3 free floor cells in a straight line from the chair (not towards his own cell). */
	private static BlockPos path(Ctx c, BlockPos from) {
		List<Direction> dirs = new ArrayList<>(List.of(Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST));
		java.util.Collections.shuffle(dirs, new java.util.Random(c.rnd.nextLong()));
		BlockPos feet = c.p.blockPosition();
		for (Direction d : dirs) {
			int len = 0;
			for (int k = 1; k <= 3; k++) {
				BlockPos q = from.relative(d, k);
				if (!c.level().getBlockState(q).isAir() || !HouseQuery.standable(c.run, q) || q.distSqr(feet) < 2 || CasaProps.held(c.run, q)) {
					break;
				}
				len = k;
			}
			if (len >= 2) {
				return from.relative(d, len);
			}
		}
		return null;
	}

	@Override
	public void start(Ctx c) {
		BlockPos ch = c.get("chair");
		BlockPos dest = c.get("dest");
		FlyingProp f = FlyingProp.lift(c.run, ch);
		List<FlyingProp> props = new ArrayList<>();
		if (f != null) {
			int len = (int) Math.round(Math.sqrt(ch.distSqr(dest)));
			f.slideTo(Vec3.atCenterOf(dest), 30 + 14 * len);
			props.add(f);
			c.run.sound(ModSounds.SILLA_ARRASTRA, Vec3.atCenterOf(ch), 1.2F, Polter.pitch(c, 0.85F, 1.0F));
			Polter.noise(c.run, Vec3.atCenterOf(ch), 30F);
		}
		c.put("props", props);
	}

	@Override
	public boolean tick(Ctx c) {
		List<FlyingProp> props = c.get("props");
		if (props.isEmpty()) {
			return true;
		}
		FlyingProp f = props.get(0);
		if (f.moving()) {
			f.tick();
			if (!f.moving()) {
				SanityManager.add(c.p, -2F);
			}
			return false;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(f.seen(55F));
		return g.lost >= 40 || c.t > 20 * 45 && !f.seen(70F);
	}

	@Override
	public void stop(Ctx c) {
		FlyingProp.restoreAll(c.get("props"));
	}

	@Override
	public int maxTicks() {
		return 20 * 70;
	}
}
