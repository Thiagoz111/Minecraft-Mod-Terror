package com.deadline.horror.casa.events;

import com.deadline.entity.MunecaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * 43 ofelia_aparece (acts 2-6, intensity 2): Ofelia, Lucía's porcelain doll, is somewhere she cannot be: sitting on
 * HIS bed, on his chair at the table, on top of the fridge. Put there unseen; a porcelain click when he finds her;
 * when he looks back after having looked away, she is not there any more.
 */
public class OfeliaAparece extends HorrorEvent {
	public OfeliaAparece() {
		super("ofelia_aparece", Kind.APPARITION);
		this.acts(2, 6).intensity(2).cooldown(120).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		List<Vec3> ok = new ArrayList<>();
		for (Vec3 v : candidates(c)) {
			double d = Apparitions.dist(c, v);
			if (d >= 3.0 && d <= 22.0 && !Apparitions.sees(c, v.add(0, 0.4, 0), 70F)) {
				ok.add(v);
			}
		}
		if (ok.isEmpty()) {
			return false;
		}
		c.put("spot", ok.get(c.rnd.nextInt(ok.size())));
		return true;
	}

	/** On top of: the guest bed (his), any dining chair (his first), the fridge. */
	private static List<Vec3> candidates(Ctx c) {
		List<Vec3> out = new ArrayList<>();
		Vec3 bed = onTop(c, "huespedes_cama", "cama");
		if (bed != null) {
			out.add(bed);
		}
		for (String s : HouseQuery.points(c.run, "silla_")) {
			Vec3 v = onTop(c, s, "silla");
			if (v != null) {
				out.add(v);
				if (s.equals("silla_6")) {
					out.add(v);  // his chair: twice as likely
				}
			}
		}
		Vec3 fridge = onTop(c, "heladera", "heladera");
		if (fridge != null) {
			out.add(fridge);
		}
		return out;
	}

	/** The top of the nearest kit block named *part* within 2 blocks of the marker (stacked blocks: the top one). */
	private static Vec3 onTop(Ctx c, String marker, String part) {
		Vec3 m = Apparitions.at(c.run, marker);
		if (m == null) {
			return null;
		}
		BlockPos centre = BlockPos.containing(m);
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(centre.offset(-2, -1, -2), centre.offset(2, 1, 2))) {
			BlockState s = c.level().getBlockState(p);
			if (!s.isAir() && HouseQuery.key(s).contains(part)) {
				double d = p.distSqr(centre);
				if (d < bd) {
					bd = d;
					best = p.immutable();
				}
			}
		}
		if (best == null) {
			return null;
		}
		while (HouseQuery.key(c.level().getBlockState(best.above())).contains(part)) {
			best = best.above();
		}
		VoxelShape shape = c.level().getBlockState(best).getCollisionShape(c.level(), best);
		double top = shape.isEmpty() ? best.getY() + 0.5 : best.getY() + shape.max(Direction.Axis.Y);
		BlockPos above = BlockPos.containing(best.getX(), top + 0.05, best.getZ());
		if (!c.level().getBlockState(above).getCollisionShape(c.level(), above).isEmpty() && above.getY() > best.getY()) {
			return null;  // no room on top
		}
		return new Vec3(best.getX() + 0.5, top, best.getZ() + 0.5);
	}

	@Override
	public void start(Ctx c) {
		Vec3 spot = c.get("spot");
		MunecaEntity doll = Apparitions.spawn(c, ModEntities.MUNECA, spot, Apparitions.yawTo(spot, c.p.position()));
		if (doll != null) {
			doll.noPhysics = true;
			doll.setNoGravity(true);
		}
		c.put("e", doll);
	}

	@Override
	public boolean tick(Ctx c) {
		MunecaEntity doll = c.get("e");
		if (Apparitions.gone(doll)) {
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.sees(c, doll, 45F));
		if (!was && g.ever) {
			Apparitions.sound(c, ModSounds.APARICION_OFELIA, doll.position().add(0, 0.4, 0), 0.8F, Apparitions.pitch(c, 0.95F, 1.1F));
		}
		if (g.lookedAway(20) || Apparitions.dist(c, doll.position()) < 1.4) {
			Apparitions.vanish(doll, false);
			return true;
		}
		return !g.ever && c.t > 20 * 80;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 110;
	}
}
