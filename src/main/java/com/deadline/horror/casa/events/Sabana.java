package com.deadline.horror.casa.events;

import com.deadline.entity.ApparitionEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.ApparitionEntities;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * 44 sabana (acts 2-5, intensity 3; El Conjuro): a sheet on the patio clothesline (marker 'soga') fills out with the
 * shape of a person -- a head, shoulders, arms reaching -- comes flying at him and falls on the ground EMPTY. If there is
 * a wall or a window between them it stops short of it and drops there.
 */
public class Sabana extends HorrorEvent {
	private static final String MARK = "soga";
	private static final int HANG = 30, FLY = 40, COLLAPSE = 8, LIE = 70;
	/** The sheet hangs from the line: the line is this far above the marker's floor, its top edge 1.56 above the entity. */
	private static final double LINE = 1.9, TOP = 1.56;

	public Sabana() {
		super("sabana", Kind.APPARITION);
		this.acts(2, 5).intensity(3).cooldown(300).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		Vec3 v = Apparitions.at(c.run, MARK);
		if (v == null || Apparitions.hidden(c.p)) {
			return false;
		}
		double d = Apparitions.dist(c, v);
		return d > 5.0 && d < 28.0 && Apparitions.sees(c, v.add(0, LINE - 0.4, 0), 55F);
	}

	@Override
	public void start(Ctx c) {
		Vec3 v = c.run.at(MARK);
		Vec3 hang = v.add(0, LINE - TOP, 0);
		ApparitionEntity s = Apparitions.spawn(c, ApparitionEntities.SABANA, hang, Apparitions.yawTo(v, c.p.position()));
		if (s != null) {
			s.setAction(ApparitionEntities.SABANA_HANG);
		}
		c.put("e", s);
		c.put("from", hang);
		// where it flies to: just short of him, or of the first wall / window between them
		Vec3 eye = c.p.getEyePosition();
		Vec3 start = hang.add(0, 1.0, 0);
		BlockHitResult hit = c.level().clip(new ClipContext(start, eye, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, c.p));
		Vec3 dir = eye.subtract(start).normalize();
		Vec3 end = hit.getType() == HitResult.Type.MISS ? eye.subtract(dir.scale(1.8)) : hit.getLocation().subtract(dir.scale(1.2));
		if (end.distanceTo(start) > 14.0) {
			end = start.add(dir.scale(14.0));
		}
		c.put("to", end.subtract(0, 1.0, 0));
	}

	@Override
	public boolean tick(Ctx c) {
		ApparitionEntity s = c.get("e");
		if (Apparitions.gone(s)) {
			return true;
		}
		Vec3 from = c.get("from");
		Vec3 to = c.get("to");
		int t = c.t;
		Integer fall = c.get("fall");
		if (t == HANG) {
			s.setAction(ApparitionEntities.SABANA_FLY);
			Apparitions.sound(c, ModSounds.APARICION_SABANA, s.position().add(0, 1.0, 0), 1.3F, 1.0F);
		}
		if (fall == null && t > HANG && t <= HANG + FLY) {
			float u = (t - HANG) / (float) FLY;
			float e = u * u * (3F - 2F * u);
			// it rises off the line and swoops at him
			Vec3 p = from.lerp(to, e).add(0, Math.sin(u * Math.PI) * 0.9, 0);
			Apparitions.glide(s, p, false);
			Apparitions.face(s, Apparitions.yawTo(p, c.p.position()));
			if (Apparitions.dist(c, p) < 2.0) {
				fall = t;
				c.put("fall", fall);
			}
		}
		if (fall == null && t > HANG + FLY) {
			fall = t;
			c.put("fall", fall);
		}
		if (fall != null) {
			if (t == fall) {
				s.setAction(ApparitionEntities.SABANA_COLLAPSE);
			}
			if (t - fall == COLLAPSE) {
				// empty, on the ground
				double y = Apparitions.floorY(c.run, BlockPos.containing(s.getX(), s.getY() + 0.5, s.getZ()));
				Apparitions.glide(s, new Vec3(s.getX(), y, s.getZ()), false);
				s.setAction(ApparitionEntities.SABANA_FLAT);
			}
			if (t - fall > COLLAPSE + LIE && !Apparitions.sees(c, s.position(), 50F)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 20;
	}
}
