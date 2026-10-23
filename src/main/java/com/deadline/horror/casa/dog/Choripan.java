package com.deadline.horror.casa.dog;

import com.deadline.director.Props;
import com.deadline.director.Run;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * Act-script API of the family dog (docs/design/casa_terror.md 2 and 7). He is a run actor ({@link #ACTOR} by default),
 * spawned like every scripted actor ({@link Props#spawn}).
 * <pre>
 *   Choripan.spawn(run, "silla_1", ChoripanEntity.POSE_GROWL, ChoripanEntity.LOOK_NORMAL)   // under the table
 *       .watch(nona);                                                                       // growling at her
 *   Choripan.standAt(run, pos, yaw);    // Act 1: on two legs in the middle of the road, in the headlights
 *   Choripan.get(run).dash(run.at("patio"));   // runs out; the pose comes back on arrival
 * </pre>
 */
public final class Choripan {
	public static final String ACTOR = "choripan";

	private Choripan() {
	}

	public static ChoripanEntity get(Run run) {
		return run != null && run.actor(ACTOR) instanceof ChoripanEntity c ? c : null;
	}

	/** Spawns (or replaces) the dog at a marker, facing its yaw, in a pose and a look. Null if the marker is missing. */
	public static ChoripanEntity spawn(Run run, String point, int pose, int look) {
		if (run == null || !run.def.points.containsKey(point)) {
			return null;
		}
		ChoripanEntity c = Props.spawn(run, ACTOR, DogEntities.CHORIPAN, point, false);
		if (c != null) {
			c.setVariant(look);
			c.pose(pose);
		}
		return c;
	}

	/** The dead dog standing on its hind legs anywhere (the road in Act 1): look 'muerto', still, staring along yaw. */
	public static ChoripanEntity standAt(Run run, Vec3 pos, float yaw) {
		if (run == null) {
			return null;
		}
		ChoripanEntity c = DogEntities.CHORIPAN.create(run.level, net.minecraft.world.entity.EntitySpawnReason.EVENT);
		if (c == null) {
			return null;
		}
		c.snapTo(pos.x, pos.y, pos.z, yaw, 0F);
		c.setYHeadRot(yaw);
		c.setYBodyRot(yaw);
		c.scripted = true;
		c.directorActor = true;
		c.setNoAi(true);
		c.setInvulnerable(true);
		c.setSiteIndex(run.site);
		c.setVariant(ChoripanEntity.LOOK_MUERTO);
		c.pose(ChoripanEntity.POSE_STAND);
		run.level.addFreshEntity(c);
		run.actor(ACTOR, c);
		return c;
	}

	public static void remove(Run run) {
		if (run != null) {
			run.despawn(ACTOR);
		}
	}

	/** True while the dog is an actor of the run (not removed). */
	public static boolean present(Run run) {
		Entity e = run == null ? null : run.actor(ACTOR);
		return e instanceof ChoripanEntity;
	}
}
