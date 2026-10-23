package com.deadline.horror.casa.events;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * 37 figura_espejo (acts 2-5, intensity 4): he stands at the big mirror of the hall or the bathroom mirror
 * (espejo_hall / espejo_bano), looking into it -- and somebody is standing right behind him. The glass hums, a breath
 * on the back of his neck; if he keeps looking at the mirror it breathes again, closer. When he turns round, the
 * moment it would come into view: nothing there.
 * <p>(Minecraft draws no reflections: what stands behind him is real and it is gone before he can turn far enough to
 * see more than a sliver of it at the edge of the screen.)
 */
public class FiguraEspejo extends HorrorEvent {
	private static final String[] MIRRORS = {"espejo_hall", "espejo_bano"};

	public FiguraEspejo() {
		super("figura_espejo", Kind.APPARITION);
		this.acts(2, 5).intensity(4).cooldown(240).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		for (String m : MIRRORS) {
			Vec3 v = Apparitions.at(c.run, m);
			if (v == null || Apparitions.dist(c, v) > 2.2 || Math.abs(v.y - c.p.getY()) > 1.0) {
				continue;
			}
			// facing the mirror (the marker looks at it)
			if (Math.abs(Mth.wrapDegrees(c.p.getYRot() - c.run.yaw(m))) > 35F) {
				continue;
			}
			Vec3 spot = HouseQuery.behind(c.run, c.p, 1.4);
			if (spot == null || spot.distanceTo(c.p.position()) < 0.9) {
				continue;
			}
			c.put("m", m);
			c.put("spot", spot);
			return true;
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		Vec3 spot = c.get("spot");
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, spot, Apparitions.yawTo(spot, c.p.position()));
		if (n != null) {
			n.propSounds = false;
			n.setAction(FamilyEntity.POSE_IDLE);
			n.watch(c.p);
		}
		c.put("e", n);
		String m = c.get("m");
		Apparitions.sound(c, ModSounds.APARICION_ESPEJO, c.run.at(m).add(0, 1.5, 0), 0.9F, 1.0F);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity n = c.get("e");
		if (Apparitions.gone(n)) {
			return true;
		}
		Vec3 neck = c.p.getEyePosition().add(c.p.getViewVector(1F).scale(-0.5));
		if (c.t == 12) {
			Apparitions.sound(c, ModSounds.APARICION_ALIENTO, neck, 0.8F, 0.95F);
		}
		if (c.t == 70) {
			// still looking at the mirror: closer, and again
			Vec3 closer = HouseQuery.behind(c.run, c.p, 0.8);
			if (closer != null) {
				n.teleportTo(closer.x, closer.y, closer.z);
			}
			Apparitions.sound(c, ModSounds.APARICION_ALIENTO, neck, 1.1F, 0.85F);
			SanityManager.add(c.p, -4F);
		}
		// he turns: the instant it would be on screen, it is not there
		Vec3 to = n.position().add(0, 1.2, 0).subtract(c.p.getEyePosition());
		double cos = c.p.getViewVector(1F).dot(to.normalize());
		if (cos > Math.cos(Math.toRadians(62.0)) || Apparitions.dist(c, n.position()) > 4.0) {
			Apparitions.vanish(n, false);
			if (cos > Math.cos(Math.toRadians(62.0))) {
				SanityManager.add(c.p, -6F);
			}
			return true;
		}
		return c.t > 20 * 9;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 12;
	}
}
