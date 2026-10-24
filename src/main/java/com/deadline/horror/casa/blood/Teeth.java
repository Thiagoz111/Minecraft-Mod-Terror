package com.deadline.horror.casa.blood;

import com.deadline.director.Run;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.horror.casa.lore.LoreDocs;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Human teeth (and the Nona's dentures, bloody) spilled out of a drawer of the casa kit: a smear of blood on the top of
 * the piece of furniture, by its front edge, the teeth scattered on it, a run of blood down the drawer front. Used by
 * event 51 'diente' and free for any drawer that turns out to hold teeth (the interactables' drawer contents). Every
 * piece is tracked like the blood: it stays until {@link BloodDecals#clear}.
 */
public final class Teeth {
	private Teeth() {
	}

	/**
	 * Spills teeth out of the drawer furniture at `drawer` (absolute), on the side facing `viewer` when the block has
	 * no facing. denture: the Nona's dentures too. Returns the displays (empty when it could not place them).
	 */
	public static List<Display.ItemDisplay> spill(Run r, BlockPos drawer, Vec3 viewer, boolean denture, RandomSource rnd) {
		return spill(r, drawer, viewer, null, denture, rnd);
	}

	/** {@link #spill(Run, BlockPos, Vec3, boolean, RandomSource)}; `who` (the hunter) lets it find the real table top. */
	public static List<Display.ItemDisplay> spill(Run r, BlockPos drawer, Vec3 viewer, Entity who, boolean denture,
			RandomSource rnd) {
		List<Display.ItemDisplay> out = new ArrayList<>();
		BlockState st = r.level.getBlockState(drawer);
		Vec3 mid = Vec3.atCenterOf(drawer);
		Direction f;
		if (st.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			f = st.getValue(BlockStateProperties.HORIZONTAL_FACING);  // the kit faces its front (the drawers) this way
		} else {
			f = com.deadline.director.Props.towards(mid, viewer == null ? mid.add(0, 0, 1) : viewer);
		}
		Vec3 front = new Vec3(f.getStepX(), 0, f.getStepZ());
		Vec3 base0 = mid.add(front.scale(0.2));
		double top = LoreDocs.surface(r, drawer, base0.x, base0.z, who);
		Vec3 base = new Vec3(base0.x, top, base0.z);
		add(out, BloodDecals.floor(r, BloodDecals.splat(rnd), base, rnd.nextFloat() * 360F, 0.5F, 0.5F));
		if (denture) {
			Vec3 at = base.add((rnd.nextFloat() - 0.5F) * 0.08, 0.004, (rnd.nextFloat() - 0.5F) * 0.08);
			float yaw = f.toYRot() + 180F + (rnd.nextFloat() - 0.5F) * 50F;
			add(out, BloodDecals.floor(r, BloodDecals.DENTURE, at, yaw, 0.3F, 0.3F));
		}
		int n = 5 + rnd.nextInt(4);
		for (int i = 0; i < n; i++) {
			double a = rnd.nextDouble() * Math.PI * 2;
			double d = 0.08 + rnd.nextDouble() * 0.22;
			Vec3 at = base.add(Math.cos(a) * d, 0.008, Math.sin(a) * d);
			// keep them on the top of the furniture
			at = new Vec3(clamp(at.x, mid.x - 0.42, mid.x + 0.42), at.y, clamp(at.z, mid.z - 0.42, mid.z + 0.42));
			float size = 0.09F + rnd.nextFloat() * 0.04F;
			add(out, BloodDecals.floor(r, BloodDecals.TEETH[rnd.nextInt(BloodDecals.TEETH.length)], at, rnd.nextFloat() * 360F, size, size));
		}
		// a run of blood down the front, from the top edge
		double inset = frontInset(r, drawer, st, f);
		Vec3 face = mid.add(front.scale(0.5 - inset));
		Vec3 runAt = new Vec3(face.x, top - 0.2, face.z).add(new Vec3(front.z, 0, -front.x).scale((rnd.nextFloat() - 0.5F) * 0.5));
		add(out, BloodDecals.wall(r, BloodDecals.RUNS[rnd.nextInt(BloodDecals.RUNS.length)], runAt, f, 0F, 0.2F, 0.42F));
		return out;
	}

	/** How far in from the block face the front of the furniture is (its outline, on the facing side). */
	private static double frontInset(Run r, BlockPos pos, BlockState st, Direction f) {
		VoxelShape sh = st.getShape(r.level, pos);
		if (sh.isEmpty()) {
			return 0.0;
		}
		AABB b = sh.bounds();
		double edge = switch (f) {
			case NORTH -> b.minZ;
			case SOUTH -> 1.0 - b.maxZ;
			case WEST -> b.minX;
			case EAST -> 1.0 - b.maxX;
			default -> 0.0;
		};
		return Math.max(0.0, Math.min(0.45, edge));
	}

	private static double clamp(double v, double lo, double hi) {
		return Math.max(lo, Math.min(hi, v));
	}

	private static void add(List<Display.ItemDisplay> out, Display.ItemDisplay d) {
		if (d != null) {
			out.add(d);
		}
	}
}
