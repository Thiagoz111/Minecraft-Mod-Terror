package com.deadline.horror.casa.dog;

import com.deadline.director.Run;
import com.deadline.horror.HouseQuery;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;

/**
 * Act-script API of the long dog (docs/design/casa_terror.md 7: "el perro largo: sale de la cucha y no termina de
 * salir"). One per run, kept as the run actor {@link #ACTOR} (so {@code Run.end()} removes it too). Run events posted:
 * {@code perro_largo:emerged} (the 6 s unspool is over), {@code perro_largo:caught} (it reached a hunter: jumpscare),
 * {@code perro_largo:retracted} (back in the doghouse, gone).
 * <pre>
 *   PerroLargo.emerge(run);                       // comes out of the doghouse (marker 'cucha') for ~6 s
 *   PerroLargo.chase(run, player);                // skitters at him (ground path, open doors)
 *   PerroLargo.crawl(run, "patio", "puerta_patio", "cocina");   // or along markers
 *   PerroLargo.retract(run);                      // back inside along its own path, then gone
 * </pre>
 */
public final class PerroLargo {
	public static final String ACTOR = "perro_largo";

	private PerroLargo() {
	}

	public static ChoripanDemonioEntity get(Run run) {
		return run != null && run.actor(ACTOR) instanceof ChoripanDemonioEntity d ? d : null;
	}

	public static boolean active(Run run) {
		return get(run) != null;
	}

	/** Spawns it in the doghouse door and starts the emerge. Null if the site has no 'cucha' marker. */
	public static ChoripanDemonioEntity emerge(Run run) {
		if (run == null || !run.def.points.containsKey("cucha")) {
			return null;
		}
		ChoripanDemonioEntity d = DogEntities.CHORIPAN_DEMONIO.create(run.level, EntitySpawnReason.EVENT);
		if (d == null) {
			return null;
		}
		Door door = door(run);
		Vec3 plane = door.plane();
		float yaw = door.yaw();
		d.setDoor(plane, yaw);
		d.snapTo(plane.x, plane.y, plane.z, yaw, 0F);
		d.setYHeadRot(yaw);
		d.setYBodyRot(yaw);
		d.directorActor = true;
		d.setSiteIndex(run.site);
		d.onRetracted = () -> run.post("perro_largo:retracted");
		d.onCaught = p -> run.post("perro_largo:caught");
		run.level.addFreshEntity(d);
		run.actor(ACTOR, d);
		d.emerge();
		run.post("perro_largo:emerging");
		return d;
	}

	/** Sends it after a hunter (ground navigation). False if it is not out. */
	public static boolean chase(Run run, ServerPlayer target) {
		ChoripanDemonioEntity d = get(run);
		if (d == null || target == null) {
			return false;
		}
		d.chase(target);
		return true;
	}

	/** Skitters through these markers in order (missing ones are skipped), then holds. */
	public static boolean crawl(Run run, String... points) {
		ChoripanDemonioEntity d = get(run);
		if (d == null) {
			return false;
		}
		List<Vec3> path = new ArrayList<>();
		for (String p : points) {
			if (run.def.points.containsKey(p)) {
				Vec3 v = run.at(p);
				path.add(new Vec3(v.x, v.y, v.z));
			}
		}
		if (path.isEmpty()) {
			return false;
		}
		d.crawl(path);
		return true;
	}

	public static boolean retract(Run run) {
		ChoripanDemonioEntity d = get(run);
		if (d == null) {
			return false;
		}
		d.retract();
		return true;
	}

	/** Gone at once (no retract), e.g. when the act changes. */
	public static void remove(Run run) {
		if (run != null) {
			run.despawn(ACTOR);
		}
	}

	/** True once the emerge is over and it waits, staring (the script may chase now). */
	public static boolean emerged(Run run) {
		ChoripanDemonioEntity d = get(run);
		return d != null && d.state() == ChoripanDemonioEntity.STATE_HOLD;
	}

	/** The doghouse door: the centre of its plane on the floor and the yaw a body coming out of it faces. */
	public record Door(Vec3 plane, float yaw) {
	}

	/**
	 * The doghouse door. Found from the
	 * doghouse block next to the 'cucha' marker (a kit block named *cucha*, its facing = the door side); without one,
	 * the marker itself, coming out against its yaw (the marker stands in front of the doghouse looking at it).
	 */
	public static Door door(Run run) {
		Vec3 m = run.at("cucha");
		float myaw = run.yaw("cucha");
		BlockPos c = BlockPos.containing(m);
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-3, -1, -3), c.offset(3, 1, 3))) {
			BlockState s = run.level.getBlockState(p);
			if (s.isAir() || !HouseQuery.key(s).contains("cucha") || !s.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
				continue;
			}
			double d = sq(p, c);
			if (d < bd) {
				bd = d;
				best = p.immutable();
			}
		}
		if (best != null) {
			Direction f = run.level.getBlockState(best).getValue(BlockStateProperties.HORIZONTAL_FACING);
			Vec3 plane = new Vec3(best.getX() + 0.5 + f.getStepX() * 0.5, m.y, best.getZ() + 0.5 + f.getStepZ() * 0.5);
			return new Door(plane, f.toYRot());
		}
		return new Door(m, myaw + 180F);
	}

	private static double sq(BlockPos a, BlockPos b) {
		double dx = a.getX() - b.getX(), dy = a.getY() - b.getY(), dz = a.getZ() - b.getZ();
		return dx * dx + dy * dy + dz * dz;
	}
}
