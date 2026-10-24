package com.deadline.horror.casa;

import com.deadline.casa.CasaProps;
import com.deadline.director.Run;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.Display;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;

/**
 * The drawers of the Casa kit furniture (nightstands, the dresser, the kitchen counter, the sideboard, Lucía's desk,
 * the dining table's cutlery drawer). The kit models have no open variant, so an open drawer is drawn over the block
 * with display boxes: the dark hole where its front was and the drawer itself pulled out (front, bottom, sides) with
 * whatever is inside sitting in it. Nothing in the world changes: closing it is removing the displays.
 */
public final class Drawers {
	/** One drawer front of a north-facing model, in pixels: x0..x1, y0..y1 and the z of its face. */
	private record Front(double x0, double x1, double y0, double y1, double z) {
	}

	private static final Map<String, List<Front>> FRONTS = Map.ofEntries(
			Map.entry("casa_mesa_luz", List.of(new Front(2.8, 13.2, 8.6, 10.8, 2.4))),
			Map.entry("casa_mesa_luz_nona", List.of(new Front(2.8, 13.2, 8.6, 10.8, 2.4))),
			Map.entry("casa_comoda_der", rows(1.2, 15.9, 3.2, new double[][] {{2.0, 5.4}, {5.6, 9.0}, {9.2, 12.0}})),
			Map.entry("casa_comoda_izq", rows(0.1, 14.8, 3.2, new double[][] {{2.0, 5.4}, {5.6, 9.0}, {9.2, 12.0}})),
			Map.entry("casa_mesada_cajones", rows(0.6, 15.4, 1.2, new double[][] {{1.6, 5.2}, {5.4, 9.0}, {9.2, 12.8}})),
			Map.entry("casa_aparador_der", List.of(new Front(1.2, 15.9, 9.8, 12.2, 2.6))),
			Map.entry("casa_aparador_izq", List.of(new Front(0.1, 14.8, 9.8, 12.2, 2.6))),
			Map.entry("casa_mesita_auxiliar", List.of(new Front(3.8, 12.2, 9.4, 11.0, 3.4))),
			Map.entry("casa_escritorio_lucia", List.of(new Front(2.6, 13.4, 7.6, 10.2, 3.6))),
			Map.entry("casa_escritorio_lucia_apagada", List.of(new Front(2.6, 13.4, 7.6, 10.2, 3.6))),
			Map.entry("casa_mesa_comedor_extremo", List.of(new Front(4.0, 14.0, 9.2, 10.8, 1.6))));
	/** How far an open drawer comes out (pixels). */
	private static final double OUT = 6.5;

	private Drawers() {
	}

	private static List<Front> rows(double x0, double x1, double z, double[][] ys) {
		List<Front> out = new ArrayList<>();
		for (double[] y : ys) {
			out.add(new Front(x0, x1, y[0], y[1], z));
		}
		return out;
	}

	/** True for a kit block with drawers. */
	public static boolean is(BlockState s) {
		return s != null && FRONTS.containsKey(Polter.key(s));
	}

	/** True for the registry path of a kit block with drawers ("casa_comoda_izq"). */
	public static boolean isKey(String key) {
		return FRONTS.containsKey(key);
	}

	public static int count(BlockState s) {
		List<Front> f = FRONTS.get(Polter.key(s));
		return f == null ? 0 : f.size();
	}

	/** The drawer under a clicked point (fraction 0..1 of the block height), the top one if none. */
	public static int at(BlockState s, double fracY) {
		List<Front> f = FRONTS.get(Polter.key(s));
		if (f == null) {
			return 0;
		}
		double py = fracY * 16.0;
		for (int i = 0; i < f.size(); i++) {
			if (py >= f.get(i).y0() - 0.5 && py <= f.get(i).y1() + 0.5) {
				return i;
			}
		}
		return f.size() - 1;
	}

	/** The wood an open drawer is made of: mahogany for the lustred pieces, cream for the counter, pink for the desk. */
	private static BlockState wood(String key) {
		if (key.startsWith("casa_mesada")) {
			return Blocks.WHITE_TERRACOTTA.defaultBlockState();
		}
		if (key.startsWith("casa_escritorio_lucia")) {
			return Blocks.PINK_TERRACOTTA.defaultBlockState();
		}
		return Blocks.DARK_OAK_PLANKS.defaultBlockState();
	}

	/** Opens drawer `which` of the kit block at pos: returns the display actors (close with {@link #close}). */
	public static List<String> open(Run r, BlockPos pos, int which) {
		List<String> out = new ArrayList<>();
		BlockState s = r.level.getBlockState(pos);
		List<Front> fronts = FRONTS.get(Polter.key(s));
		if (fronts == null || fronts.isEmpty()) {
			return out;
		}
		Front f = fronts.get(Math.max(0, Math.min(fronts.size() - 1, which)));
		Direction dir = Polter.facing(s);
		BlockState w = wood(Polter.key(s));
		BlockState hole = Blocks.BLACK_CONCRETE.defaultBlockState();
		double z0 = f.z() - OUT;
		double x0 = f.x0() + 0.3;
		double x1 = f.x1() - 0.3;
		double y0 = f.y0() + 0.2;
		double y1 = f.y1() - 0.2;
		box(r, out, pos, dir, hole, f.x0() + 0.2, f.y0() + 0.15, f.z() - 0.3, f.x1() - 0.2, f.y1() - 0.15, f.z() - 0.12);
		box(r, out, pos, dir, w, f.x0(), f.y0(), z0 - 0.5, f.x1(), f.y1(), z0);          // its front
		box(r, out, pos, dir, w, x0, y0, z0, x1, y0 + 0.5, f.z());                        // bottom
		box(r, out, pos, dir, w, x0, y0, z0, x0 + 0.5, y1, f.z());                         // sides
		box(r, out, pos, dir, w, x1 - 0.5, y0, z0, x1, y1, f.z());
		return out;
	}

	private static void box(Run r, List<String> out, BlockPos pos, Direction dir, BlockState st, double x0, double y0, double z0,
			double x1, double y1, double z1) {
		String a = CasaProps.uid("cajon");
		if (Polter.box(r, a, pos, dir, st, x0, y0, z0, x1, y1, z1) != null) {
			out.add(a);
		}
	}

	/** The middle of the bottom of an open drawer (where its contents lie). */
	public static Vec3 inside(Run r, BlockPos pos, int which) {
		BlockState s = r.level.getBlockState(pos);
		List<Front> fronts = FRONTS.get(Polter.key(s));
		if (fronts == null || fronts.isEmpty()) {
			return Vec3.atCenterOf(pos);
		}
		Front f = fronts.get(Math.max(0, Math.min(fronts.size() - 1, which)));
		return Polter.local(pos, Polter.facing(s), (f.x0() + f.x1()) / 2, f.y0() + 0.8, f.z() - OUT / 2);
	}

	/** Puts an item lying in an open drawer; its actor is added to the drawer's list. */
	public static void content(Run r, List<String> actors, BlockPos pos, int which, ItemStack stack, float yawRad) {
		if (stack == null || stack.isEmpty()) {
			return;
		}
		String a = CasaProps.uid("cajon");
		Display.ItemDisplay d = CasaProps.item(r, a, inside(r, pos, which).add(0, 0.02, 0), stack);
		if (d != null) {
			CasaProps.pose(d, new Quaternionf().rotationY(yawRad).rotateX((float) (Math.PI / 2)), 0.32F, CasaProps.ZERO, 0);
			actors.add(a);
		}
	}

	public static void close(Run r, List<String> actors) {
		if (actors == null) {
			return;
		}
		for (String a : actors) {
			r.despawn(a);
		}
		actors.clear();
	}
}
