package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Act 4 (design 2, "la Nona rezando de espaldas en el pasillo"): behind him in the dark upstairs hall a murmur starts --
 * a prayer, said backwards. Under the one lamp of the hall that has come on by itself, the Nona stands with her back to
 * him, her white hair loose, her head bowed over her walker, praying. If he comes close (or stares long enough) the
 * prayer stops dead. Silence. Her head turns -- all the way round, the body not moving -- and she looks at him. The
 * bulb bursts. In the dark, she is not there.
 */
public class SpNonaReza extends HorrorEvent {
	private static final String LAMPS = "luces_pasillo_1p";
	private static final int PRAY = 0, TURN = 1;

	public SpNonaReza() {
		super("sp_nona_reza", Kind.SETPIECE);
		this.acts(4, 6).intensity(4).cooldown(300).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c) || !Apparitions.hasArea(c.run, "pasillo_1p")) {
			return false;
		}
		AABB hall = c.run.area("pasillo_1p");
		if (!hall.inflate(1.5, 0.5, 1.5).contains(c.p.position())) {
			return false;
		}
		boolean alongX = hall.getXsize() >= hall.getZsize();
		Vec3 centre = hall.getCenter();
		Vec3 axis = alongX ? new Vec3(1, 0, 0) : new Vec3(0, 0, 1);
		Vec3 from = alongX ? new Vec3(c.p.getX(), Math.floor(c.p.getY()), centre.z) : new Vec3(centre.x, Math.floor(c.p.getY()), c.p.getZ());
		// along the hall's centre line, 7-13 blocks from him, where he is not looking (behind him, most likely)
		for (double d = 7.0; d <= 13.0; d += 1.5) {
			for (double side : new double[] {1.0, -1.0}) {
				Vec3 v = Stage.stand(c.run, from.add(axis.scale(side * d)));
				if (v == null || !hall.inflate(0.0, 1.0, 0.0).contains(v.add(0, 0.5, 0))) {
					continue;
				}
				if (Apparitions.sees(c, v.add(0, 1.0, 0), 75F) || Apparitions.sees(c, v.add(0, 0.3, 0), 75F)) {
					continue;
				}
				c.put("spot", v);
				return true;
			}
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("spot") == null && !canRun(c)) {
			c.put("abort", true);  // fired by hand without its place (a command): nothing to stage
			return;
		}
		Vec3 spot = c.get("spot");
		// her back to him: she faces the way from him to her
		float yaw = Apparitions.yawTo(c.p.position(), spot);
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, spot, yaw);
		if (n != null) {
			n.setVariant(FamilyEntity.LOOK_POSSESSED);
			n.setAction(FamilyEntity.POSE_STAND_WALKER);
			n.propSounds = false;
			n.watchPlayers(false);
			n.lookAt(spot.add(Stage.forward(yaw).scale(0.7)).add(0, 0.2, 0));  // head bowed over the walker
		}
		c.put("e", n);
		c.put("lamp", nearestLamp(c, spot));
		lamp(c, true);
		c.put("phase", PRAY);
		c.put("next", 5);
	}

	private static int nearestLamp(Ctx c, Vec3 at) {
		List<BlockPos> g = c.run.def.group(LAMPS);
		int best = -1;
		double bd = 6.0 * 6.0;
		for (int i = 0; i < g.size(); i++) {
			double d = Vec3.atCenterOf(c.run.origin.offset(g.get(i))).distanceToSqr(at);
			if (d < bd) {
				bd = d;
				best = i;
			}
		}
		return best;
	}

	private static void lamp(Ctx c, boolean on) {
		Integer i = c.get("lamp");
		if (i != null && i >= 0) {
			c.run.light(LAMPS, i, on);
		}
	}

	private static Vec3 lampPos(Ctx c) {
		Integer i = c.get("lamp");
		List<BlockPos> g = c.run.def.group(LAMPS);
		return i != null && i >= 0 && i < g.size() ? Vec3.atCenterOf(c.run.origin.offset(g.get(i))) : null;
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.get("abort") != null) {
			return true;
		}
		FamilyEntity n = c.get("e");
		if (Apparitions.gone(n)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			Apparitions.vanish(n, false);
			lamp(c, false);
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(Apparitions.watches(c, n, 50F));
		int phase = c.get("phase");
		if (phase == PRAY) {
			int next = c.get("next");
			if (c.t >= next) {
				// the prayer, backwards, under her breath
				Apparitions.sound(c, ModSounds.MONJA_WHISPER, n.getEyePosition(), 0.85F, 0.7F + c.rnd.nextFloat() * 0.06F);
				c.put("next", c.t + 50 + c.rnd.nextInt(25));
			}
			if (Apparitions.dist(c, n.position()) < 4.5 || g.total >= 20 * 6) {
				c.put("phase", TURN);
				c.put("turnAt", c.t);
			}
			if (c.t > 20 * 45 && !g.ever || c.t > 20 * 60) {
				// he never came: the lamp goes out and so does she
				lamp(c, false);
				Apparitions.vanish(n, false);
				return true;
			}
			return false;
		}
		int k = c.t - c.<Integer>get("turnAt");
		if (k == 24) {
			// the head comes round, all the way, the body does not move
			n.setExpression(FamilyEntity.EXPR_STARE);
			n.lookAt(null);
			n.watch(c.p);
			Apparitions.sound(c, ModSounds.APARICION_CUELLO, n.getEyePosition(), 1.1F, 0.85F);
		}
		if (k == 42) {
			Apparitions.sound(c, ModSounds.APARICION_CUELLO, n.getEyePosition(), 1.2F, 0.7F);
		}
		if (k == 80) {
			Vec3 bulb = lampPos(c);
			Apparitions.sound(c, ModSounds.BULB_POP, bulb != null ? bulb : n.getEyePosition().add(0, 1.0, 0), 1.3F, 0.9F);
			lamp(c, false);
			Fx.shake(c.p, 0.4F, 8);
			Apparitions.noise(c, n.position(), 50F);
			Apparitions.vanish(n, false);
		}
		return k > 90;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		lamp(c, false);
	}

	@Override
	public int maxTicks() {
		return 20 * 70;
	}
}
