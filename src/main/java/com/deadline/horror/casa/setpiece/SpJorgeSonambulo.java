package com.deadline.horror.casa.setpiece;

import com.deadline.casa.CasaProps;
import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * Act 4 (design 2 and 7, "Jorge sonámbulo"): Marta wrote that Jorge is not in his bed. Barefoot steps in the dark
 * upstairs hall: Jorge, asleep on his feet, a kitchen knife hanging from his hand, walks right past him without seeing
 * him -- his eyes open, his head never turning -- and stops at the children's door. He stands there, breathing slowly,
 * the knife against his leg. Then he opens the door, goes in, and it closes behind him. A dull thud inside. Open it:
 * the room is as it was, and nobody is in it.
 */
public class SpJorgeSonambulo extends HorrorEvent {
	private static final List<String> KIDS = List.of("toti", "lucia");
	private static final double WALK = 0.42;
	private static final Vector3f KNIFE_PIVOT = new Vector3f(0.5F, 0.03F, 0.5F);
	private static final float ROLL = (float) (Math.PI / 2);
	private static final int GO = 0, STAND = 1, ENTER = 2, GONE = 3;

	public SpJorgeSonambulo() {
		super("sp_jorge_sonambulo", Kind.SETPIECE);
		this.acts(4, 6).intensity(4).cooldown(300).scripted().once();
	}

	private record Plan(String door, Vec3 start, Vec3 stop, Vec3 inside, boolean wasOpen) {
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c) || !Apparitions.hasArea(c.run, "pasillo_1p")) {
			return false;
		}
		AABB hall = c.run.area("pasillo_1p");
		if (!hall.inflate(1.2, 0.5, 1.2).contains(c.p.position())) {
			return false;
		}
		boolean alongX = hall.getXsize() >= hall.getZsize();
		Vec3 centre = hall.getCenter();
		for (String door : KIDS) {
			Vec3 dp = HouseQuery.doorPos(c.run, door);
			if (dp == null) {
				continue;
			}
			double d = dp.distanceTo(c.p.position());
			if (d < 3.0 || d > 13.0) {
				continue;
			}
			// the spot in front of the door on the hall's centre line, and a start on the FAR side of him: he passes him
			Vec3 stop = alongX ? new Vec3(dp.x, Math.floor(c.p.getY()), centre.z) : new Vec3(centre.x, Math.floor(c.p.getY()), dp.z);
			Vec3 axis = alongX ? new Vec3(1, 0, 0) : new Vec3(0, 0, 1);
			double side = c.p.position().subtract(stop).dot(axis) >= 0 ? 1.0 : -1.0;
			Vec3 from = new Vec3(alongX ? c.p.getX() : stop.x, stop.y, alongX ? stop.z : c.p.getZ());
			Vec3 start = null;
			for (double s = 8.0; s >= 4.5; s -= 1.0) {
				Vec3 v = Stage.stand(c.run, from.add(axis.scale(side * s)));
				if (v != null && hall.inflate(0.0, 1.0, 0.0).contains(v.add(0, 0.5, 0))
						&& !Apparitions.sees(c, v.add(0, 1.2, 0), 75F) && !Apparitions.sees(c, v.add(0, 0.4, 0), 75F)) {
					start = v;
					break;
				}
			}
			Vec3 atDoor = Stage.doorStep(c.run, door, stop, 1.4);
			Vec3 standAt = atDoor != null ? Stage.stand(c.run, atDoor) : null;
			Vec3 inside = Stage.doorStep(c.run, door, dp.add(dp.subtract(stop).multiply(1, 0, 1)), 1.6);
			if (start == null || standAt == null || inside == null) {
				continue;
			}
			c.put("plan", new Plan(door, start, standAt, inside, c.run.doorOpen(door)));
			return true;
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		Plan plan = c.get("plan");
		if (plan.wasOpen()) {
			c.run.door(plan.door(), false, false);
		}
		FamilyEntity j = Apparitions.spawn(c, FamilyEntities.JORGE, plan.start(), Apparitions.yawTo(plan.start(), plan.stop()));
		if (j != null) {
			j.setVariant(FamilyEntity.LOOK_NORMAL);
			j.setAction(FamilyEntity.POSE_IDLE);
			j.watchPlayers(false);  // asleep: the head never turns, the eyes see nothing
			j.walkTo(plan.stop(), WALK);
		}
		c.put("e", j);
		BlockState knife = CasaProps.kitOr("casa_cuchillo", Blocks.TRIPWIRE_HOOK.defaultBlockState());
		String actor = CasaProps.uid("cuchillo_jorge");
		Display.BlockDisplay d = CasaProps.block(c.run, actor, plan.start(), knife);
		c.put("knife", actor);
		c.put("kd", d);
		c.put("phase", GO);
		c.put("phaseAt", 0);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity j = c.get("e");
		Plan plan = c.get("plan");
		if (Apparitions.gone(j)) {
			return true;
		}
		holdKnife(c, j);
		int phase = c.get("phase");
		int since = c.t - c.<Integer>get("phaseAt");
		if (c.t % 70 == 35 && phase <= STAND) {
			// the slow breath of a sleeper
			Apparitions.sound(c, ModSounds.SANITY_BREATH, j.getEyePosition(), 0.45F, 0.72F);
		}
		switch (phase) {
			case GO -> {
				if (j.hasArrived() && !j.isWalking() || since > 20 * 20) {
					j.face(HouseQuery.doorPos(c.run, plan.door()));
					next(c, STAND);
				}
			}
			case STAND -> {
				// he stands at the door, the knife against his leg; the closer he comes, the sooner Jorge goes in
				double d = Apparitions.dist(c, j.position());
				if (since > 20 * 12 || d < 2.2 && since > 30) {
					c.run.door(plan.door(), true, false);
					c.run.sound(ModSounds.SP_PUERTA_CRUJE, HouseQuery.doorPos(c.run, plan.door()), 0.8F, 1.15F);
					j.walkTo(plan.inside(), WALK);
					next(c, ENTER);
				}
			}
			case ENTER -> {
				if (j.hasArrived() && !j.isWalking() || since > 20 * 6) {
					c.run.door(plan.door(), false, false);
					next(c, GONE);
				}
			}
			default -> {
				// behind the closed door (or once nobody looks): gone. A dull thud in the room.
				if (since == 40) {
					Apparitions.sound(c, ModSounds.APARICION_SOMBRA_PASO, plan.inside(), 0.9F, 0.6F);
					Apparitions.noise(c, plan.inside(), 30F);
				}
				boolean seen = Apparitions.watches(c, j, 60F);
				if (!seen && j.isAlive()) {
					Apparitions.vanish(j, false);
					c.run.despawn(c.get("knife"));
				}
				return since > 60 && Apparitions.gone(j);
			}
		}
		return false;
	}

	/** The knife hangs from his right hand, blade down, swinging a little with the walk. */
	private static void holdKnife(Ctx c, FamilyEntity j) {
		Display.BlockDisplay d = c.get("kd");
		if (d == null || d.isRemoved()) {
			return;
		}
		float yaw = j.yBodyRot;
		Vec3 hand = j.position().add(Stage.right(yaw).scale(0.43)).add(Stage.forward(yaw).scale(0.08)).add(0, 0.62, 0);
		CasaProps.move(d, hand);
		Vec3 fwd = Stage.forward(yaw);
		double swing = Math.sin(j.tickCount * 0.35) * 0.12 * Math.min(1.0, j.getDeltaMovement().horizontalDistance() * 8.0);
		Vec3 blade = new Vec3(fwd.x * (0.18 + swing), -1.0, fwd.z * (0.18 + swing));
		CasaProps.pose(d, CasaProps.alongX(blade, ROLL), 0.85F, KNIFE_PIVOT, 2);
	}

	private static void next(Ctx c, int phase) {
		c.put("phase", phase);
		c.put("phaseAt", c.t);
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		String knife = c.get("knife");
		if (knife != null) {
			c.run.despawn(knife);
		}
		Plan plan = c.get("plan");
		if (plan != null) {
			c.run.door(plan.door(), plan.wasOpen(), false);  // the children's door as it was
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 60;
	}
}
