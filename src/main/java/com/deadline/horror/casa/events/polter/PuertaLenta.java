package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * 13 puerta_lenta (acts 1-5, intensity 2): a door off one of the halls opens by itself, slowly, while he is looking at
 * it: a creak, it moves a hand's width, stops, and then swings all the way open. A vanilla door cannot move slowly, so
 * for those seconds both halves are display copies turning on the hinge (found from the door's own closed and open
 * shapes); then the real door is put back, open.
 */
public class PuertaLenta extends HorrorEvent {
	private record Plan(String door, BlockPos lower, Vector3f pivot, float sign) {
	}

	public PuertaLenta() {
		super("puerta_lenta", Kind.POLTER);
		this.acts(1, 5).intensity(2).cooldown(90).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		for (String d : HouseQuery.doorsNear(c.run, c.p.position(), 16.0)) {
			if (!Polter.plainDoor(d) || !Polter.isDoor(c.run, d) || c.run.doorOpen(d)) {
				continue;
			}
			Vec3 dp = HouseQuery.doorPos(c.run, d);
			double dist = dp.distanceTo(c.p.position());
			if (dist < 4.0 || Math.abs(dp.y - c.p.getY() - 0.5) > 2.0 || !inHall(c, dp)) {
				continue;
			}
			if (!Apparitions.sees(c, dp.add(0, 0.5, 0), 40F)) {
				continue;
			}
			Plan p = plan(c, d);
			if (p != null) {
				c.put("plan", p);
				return true;
			}
		}
		return false;
	}

	private static boolean inHall(Ctx c, Vec3 dp) {
		for (String a : List.of("pasillo_pb", "pasillo_1p", "rellano_1p")) {
			if (Apparitions.hasArea(c.run, a) && c.run.area(a).inflate(2.6, 0, 2.6).contains(dp)) {
				return true;
			}
		}
		return false;
	}

	/** The hinge (a vertical line, block units of the lower half) and the turn that takes the closed leaf open. */
	private static Plan plan(Ctx c, String door) {
		BlockPos lower = c.run.origin.offset(c.run.def.doors.get(door));
		BlockState s = c.level().getBlockState(lower);
		if (!(s.getBlock() instanceof DoorBlock) || CasaProps.held(c.run, lower) || CasaProps.held(c.run, lower.above())) {
			return null;
		}
		AABB shut = s.setValue(DoorBlock.OPEN, false).getShape(c.level(), lower).bounds();
		AABB open = s.setValue(DoorBlock.OPEN, true).getShape(c.level(), lower).bounds();
		double x0 = Math.max(shut.minX, open.minX), x1 = Math.min(shut.maxX, open.maxX);
		double z0 = Math.max(shut.minZ, open.minZ), z1 = Math.min(shut.maxZ, open.maxZ);
		if (x1 <= x0 || z1 <= z0) {
			return null;
		}
		double hx = (x0 + x1) / 2, hz = (z0 + z1) / 2;
		// closed leaf direction from the hinge (u) and open leaf direction (v): rotationY(+90) takes (x, z) to (z, -x)
		double ux = shut.getCenter().x - hx, uz = shut.getCenter().z - hz;
		double vx = open.getCenter().x - hx, vz = open.getCenter().z - hz;
		float sign = uz * vx - ux * vz >= 0 ? 1F : -1F;
		return new Plan(door, lower.immutable(), new Vector3f((float) hx, 0F, (float) hz), sign);
	}

	@Override
	public void start(Ctx c) {
		Plan p = c.get("plan");
		BlockPos lo = p.lower();
		BlockPos up = lo.above();
		BlockState ls = c.level().getBlockState(lo);
		BlockState us = c.level().getBlockState(up);
		String a = CasaProps.uid("puerta");
		String b = CasaProps.uid("puerta");
		Display.BlockDisplay dl = CasaProps.block(c.run, a, Vec3.atLowerCornerOf(lo).add(p.pivot().x, 0, p.pivot().z), ls);
		Display.BlockDisplay du = us.getBlock() instanceof DoorBlock
				? CasaProps.block(c.run, b, Vec3.atLowerCornerOf(up).add(p.pivot().x, 0, p.pivot().z), us) : null;
		CasaProps.pose(dl, new Quaternionf(), 1F, p.pivot(), 0);
		CasaProps.pose(du, new Quaternionf(), 1F, p.pivot(), 0);
		List<String> links = du != null ? List.of(a, b) : List.of(a);
		if (du != null) {
			CasaProps.remember(c.run, up, us, links);
			c.run.setBlock(up, Blocks.AIR.defaultBlockState());
		}
		CasaProps.remember(c.run, lo, ls, links);
		c.run.setBlock(lo, Blocks.AIR.defaultBlockState());
		c.put("a", a);
		c.put("b", du != null ? b : null);
		Vec3 at = Vec3.atCenterOf(lo).add(0, 0.5, 0);
		c.put("at", at);
		c.run.sound(ModSounds.POLTER_PUERTA_LENTA, at, 1.0F, Polter.pitch(c, 0.9F, 1.0F));
		Polter.noise(c.run, at, 15F);
	}

	private static void turn(Ctx c, float angle, int lerp) {
		Plan p = c.get("plan");
		Quaternionf q = new Quaternionf().rotationY(p.sign() * angle);
		for (String k : new String[] {c.get("a"), c.get("b")}) {
			if (k != null && c.run.actor(k) instanceof Display d) {
				CasaProps.pose(d, q, 1F, p.pivot(), lerp);
			}
		}
	}

	@Override
	public boolean tick(Ctx c) {
		String a = c.get("a");
		if (c.run.actor(a) == null) {
			return true;  // removed from outside: the remembered door comes back by itself
		}
		Vec3 at = c.get("at");
		boolean close = Apparitions.dist(c, at) < 1.6;
		if (c.t == 4 && !close) {
			turn(c, 0.32F, 22);
		}
		if (c.t == 40 && !close) {
			turn(c, (float) (Math.PI / 2), 44);
		}
		if (close || c.t >= 86) {
			finish(c, true);
			return true;
		}
		return false;
	}

	/** The copies go and the real door is back: open if it got there, else as it was. */
	private static void finish(Ctx c, boolean open) {
		Plan p = c.get("plan");
		String a = c.get("a");
		String b = c.get("b");
		boolean had = c.run.actor(a) != null;
		c.run.despawn(a);
		if (b != null) {
			c.run.despawn(b);
		}
		CasaProps.settleAt(c.run, p.lower());
		CasaProps.settleAt(c.run, p.lower().above());
		if (open && had) {
			c.run.door(p.door(), true, false);
		}
		c.put("a", "");
	}

	@Override
	public void stop(Ctx c) {
		String a = c.get("a");
		if (a != null && !a.isEmpty()) {
			finish(c, false);
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 8;
	}
}
