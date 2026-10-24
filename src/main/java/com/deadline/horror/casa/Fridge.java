package com.deadline.horror.casa;

import com.deadline.casa.CasaProps;
import com.deadline.director.Run;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.Display;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * The old AURORA fridge of the kitchen, opened (event 31 'heladera' and the interactable). The kit model has no open
 * variant, so while it is open the two fridge blocks are taken away (remembered, see {@link CasaProps#remember}) and
 * drawn with displays: a white enamel shell with two glass shelves, a light block inside, and the door, which is the
 * fridge's own model squashed flat against its front plane and swung open on its hinge. Closing swings it back and
 * puts the real blocks back. Whatever is inside is added by the owner with {@link #inside} / {@link #addBlock}.
 */
public final class Fridge {
	/** Hinge of the door in the north model (pixels): the viewer's right edge of the door, on its front plane. */
	private static final double HX = 1.4, HZ = 1.4;
	private static final float SQUASH = 0.075F;
	private static final float OPEN = 1.9F;

	public final Run run;
	public final BlockPos lower;
	private final Direction facing;
	private final boolean tall;
	private final String door;
	private final String doorTop;
	private final List<String> parts = new ArrayList<>();
	private int t;
	private int closing = -1;
	private boolean done;
	private int lightLevel = 11;

	private Fridge(Run run, BlockPos lower, Direction facing, boolean tall, String door, String doorTop) {
		this.run = run;
		this.lower = lower;
		this.facing = facing;
		this.tall = tall;
		this.door = door;
		this.doorTop = doorTop;
	}

	/** The lower block of the fridge at or under pos (null if pos is not a fridge). */
	public static BlockPos lowerOf(Run r, BlockPos pos) {
		String k = Polter.key(r.level.getBlockState(pos));
		if (k.equals("casa_heladera_abajo")) {
			return pos;
		}
		if (k.equals("casa_heladera_arriba") && Polter.key(r.level.getBlockState(pos.below())).equals("casa_heladera_abajo")) {
			return pos.below();
		}
		return null;
	}

	/** Opens the fridge whose lower block is at `lower` (null if it is not one or another set piece holds it). */
	public static Fridge open(Run r, BlockPos lower) {
		CasaProps.sweep(r);
		BlockState lo = r.level.getBlockState(lower);
		if (!Polter.key(lo).equals("casa_heladera_abajo") || CasaProps.held(r, lower)) {
			return null;
		}
		BlockPos upper = lower.above();
		BlockState up = r.level.getBlockState(upper);
		boolean tall = Polter.key(up).equals("casa_heladera_arriba") && !CasaProps.held(r, upper);
		Direction f = Polter.facing(lo);
		String door = CasaProps.uid("heladera");
		Display.BlockDisplay dd = CasaProps.block(r, door, Vec3.atCenterOf(lower), Polter.north(lo));
		if (dd == null) {
			return null;
		}
		String doorTop = null;
		Display.BlockDisplay du = null;
		if (tall) {
			doorTop = CasaProps.uid("heladera");
			du = CasaProps.block(r, doorTop, Vec3.atCenterOf(upper), Polter.north(up));
		}
		Fridge fr = new Fridge(r, lower.immutable(), f, tall && du != null, door, doorTop);
		fr.swing(0F, 0);
		// the real fridge goes while the door stands open; it comes back when the door closes (or its displays vanish)
		List<String> links = fr.tall ? List.of(door, doorTop) : List.of(door);
		CasaProps.remember(r, lower, lo, links);
		r.setBlock(lower, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, fr.lightLevel));
		if (fr.tall) {
			CasaProps.remember(r, upper, up, links);
			r.setBlock(upper, Blocks.AIR.defaultBlockState());
		}
		fr.shell();
		// the door swings open on the next ticks (a pose sent with the spawn would just appear open)
		r.sound(ModSounds.POLTER_HELADERA, Vec3.atCenterOf(lower).add(0, 0.5, 0), 0.9F, 1.0F);
		return fr;
	}

	private void shell() {
		BlockState white = Blocks.SMOOTH_QUARTZ.defaultBlockState();
		BlockState grey = Blocks.LIGHT_GRAY_CONCRETE.defaultBlockState();
		BlockState glass = Blocks.WHITE_STAINED_GLASS.defaultBlockState();
		double top = tall ? 24.6 : 15.4;
		box(grey, 1.0, 0.0, 2.0, 15.0, 2.0, 15.4);          // kick grille
		box(white, 1.0, 2.0, 2.0, 15.0, 2.6, 15.4);         // floor
		box(white, 1.0, 2.0, 14.8, 15.0, top, 15.4);        // back
		box(white, 1.0, 2.0, 2.0, 1.6, top, 14.8);          // sides
		box(white, 14.4, 2.0, 2.0, 15.0, top, 14.8);
		box(white, 1.0, top - 0.6, 2.0, 15.0, top, 14.8);   // ceiling
		box(glass, 1.6, 9.0, 3.0, 14.4, 9.4, 14.8);         // shelves
		if (tall) {
			box(glass, 1.6, 16.6, 3.0, 14.4, 17.0, 14.8);
			box(white, 1.6, top, 2.6, 14.4, top + 1.0, 15.0);  // the rounded top
		}
	}

	private void box(BlockState st, double x0, double y0, double z0, double x1, double y1, double z1) {
		String a = CasaProps.uid("heladera");
		if (Polter.box(run, a, lower, facing, st, x0, y0, z0, x1, y1, z1) != null) {
			parts.add(a);
		}
	}

	/** The door's angle (0 shut, about 1.9 open): the squashed fridge model turned about the hinge. */
	private void swing(float angle, int lerp) {
		Quaternionf q = new Quaternionf().rotationY(angle);
		Vector3f scale = new Vector3f(1F, 1F, SQUASH);
		Vector3f pivot = new Vector3f((float) (HX / 16.0), 0F, (float) (HZ / 16.0));
		if (run.actor(door) instanceof Display d) {
			Polter.poseLocal(d, lower, facing, q, scale, pivot, lerp);
		}
		if (doorTop != null && run.actor(doorTop) instanceof Display d) {
			Polter.poseLocal(d, lower.above(), facing, q, scale, pivot, lerp);
		}
	}

	/** World point inside the fridge at a height in pixels from its floor block (on a shelf: 2.6, 9.4, 17.0). */
	public Vec3 inside(double py) {
		return Polter.local(lower, facing, 8.0, py, 8.0);
	}

	/** Puts a block-display thing inside (a bundle wrapped in paper on a shelf): returns its actor. */
	public String addBlock(BlockState st, double x0, double y0, double z0, double x1, double y1, double z1) {
		String a = CasaProps.uid("heladera");
		if (Polter.box(run, a, lower, facing, st, x0, y0, z0, x1, y1, z1) != null) {
			parts.add(a);
			return a;
		}
		return null;
	}

	/** Puts an item standing inside (a bottle, a plate). */
	public String addItem(ItemStack stack, double px, double py, double pz, float scale) {
		String a = CasaProps.uid("heladera");
		Display.ItemDisplay d = CasaProps.item(run, a, Polter.local(lower, facing, px, py + scale * 8.0, pz), stack);
		if (d == null) {
			return null;
		}
		CasaProps.pose(d, Polter.yaw(facing), scale, CasaProps.ZERO, 0);
		parts.add(a);
		return a;
	}

	public Direction facing() {
		return facing;
	}

	/** The light inside: level 0..15 (a dying bulb flickers). */
	public void light(int level) {
		level = Math.max(0, Math.min(15, level));
		if (!done && level != lightLevel && run.level.getBlockState(lower).is(Blocks.LIGHT)) {
			lightLevel = level;
			run.setBlock(lower, level == 0 ? Blocks.AIR.defaultBlockState() : Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, level));
		} else if (!done && level != lightLevel && run.level.getBlockState(lower).isAir() && level > 0) {
			lightLevel = level;
			run.setBlock(lower, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, level));
		}
	}

	public boolean open() {
		return !done && closing < 0;
	}

	/** Swings the door shut (the real fridge is back 8 ticks later, in {@link #tick}). */
	public void close() {
		if (!done && closing < 0) {
			closing = t;
			swing(0F, 7);
		}
	}

	/** Advances closing; true once the fridge is whole again. */
	public boolean tick() {
		if (done) {
			return true;
		}
		t++;
		if (t == 2 && closing < 0) {
			swing(OPEN, 9);
		}
		if (run.actor(door) == null) {
			end();  // removed from outside (a chapter replay): the remembered blocks come back by themselves
			return true;
		}
		if (closing >= 0 && t - closing >= 8) {
			end();
			run.sound(ModSounds.ALACENA_GOLPE, Vec3.atCenterOf(lower).add(0, 0.6, 0), 0.8F, 0.7F);
			return true;
		}
		return false;
	}

	/** Puts it back at once: every display goes and the real fridge blocks return. */
	public void end() {
		if (done) {
			return;
		}
		done = true;
		for (String a : parts) {
			run.despawn(a);
		}
		parts.clear();
		run.despawn(door);
		if (doorTop != null) {
			run.despawn(doorTop);
		}
		CasaProps.settleAt(run, lower);
		if (tall) {
			CasaProps.settleAt(run, lower.above());
		}
	}

	public boolean done() {
		return done;
	}
}
