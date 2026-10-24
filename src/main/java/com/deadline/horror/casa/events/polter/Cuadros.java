package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * 25 cuadros (acts 2-5, intensity 2): every picture of the halls he is not looking at is turned to face the wall
 * (the cardboard back showing), and the crucifixes hang upside down. Silent; a frame scrapes on its nail when he
 * first notices. They STAY like that for the rest of the case: {@link #clear(Run)} puts them back when the case is left
 * (PoltergeistEvents.cleanup); a chapter replay puts them back too (their displays are run actors).
 */
public class Cuadros extends HorrorEvent {
	/** Turned pictures of each run: block position -> display actor. */
	private static final Map<Run, Map<BlockPos, String>> TURNED = new WeakHashMap<>();

	public Cuadros() {
		super("cuadros", Kind.POLTER);
		this.acts(2, 5).intensity(2).cooldown(240).weight(8);
	}

	private static boolean picture(String k) {
		return k.startsWith("casa_foto_") || k.equals("casa_crucifijo") || k.equals("casa_cuadro_ultima_cena");
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		Map<BlockPos, String> done = turned(c.run);
		done.values().removeIf(a -> c.run.actor(a) == null);  // a replay put them back
		List<BlockPos> todo = new ArrayList<>();
		for (BlockPos rel : c.run.def.group("cuadros_pasillo")) {
			BlockPos p = c.run.origin.offset(rel);
			BlockState s = c.level().getBlockState(p);
			if (done.containsKey(p) || !picture(Polter.key(s)) || CasaProps.held(c.run, p)) {
				continue;
			}
			if (!Apparitions.sees(c, Vec3.atCenterOf(p), 75F)) {
				todo.add(p);
			}
		}
		if (todo.size() < 3) {
			return false;
		}
		c.put("todo", todo);
		return true;
	}

	private static Map<BlockPos, String> turned(Run r) {
		return TURNED.computeIfAbsent(r, k -> new LinkedHashMap<>());
	}

	@Override
	public void start(Ctx c) {
		List<BlockPos> todo = c.get("todo");
		Map<BlockPos, String> done = turned(c.run);
		List<BlockPos> mine = new ArrayList<>();
		for (BlockPos p : todo) {
			String a = turn(c.run, p);
			if (a != null) {
				done.put(p, a);
				mine.add(p);
			}
		}
		c.put("mine", mine);
	}

	/** Turns one picture to the wall (a crucifix upside down): its block becomes a display, remembered. */
	private static String turn(Run r, BlockPos p) {
		BlockState s = r.level.getBlockState(p);
		String k = Polter.key(s);
		Direction f = Polter.facing(s);
		String a = CasaProps.uid("cuadro");
		Display.BlockDisplay d = CasaProps.block(r, a, Vec3.atCenterOf(p), Polter.north(s));
		if (d == null) {
			return null;
		}
		if (k.equals("casa_crucifijo")) {
			// upside down on the wall: turned about the axis out of the wall, through the middle of the cross
			Polter.poseLocal(d, p, f, new Quaternionf().rotationZ((float) Math.PI), new Vector3f(0.5F, 8.5F / 16F, 15.5F / 16F), 0);
		} else {
			// face to the wall: turned about the vertical line through the frame, against the wall
			Polter.poseLocal(d, p, f, new Quaternionf().rotationY((float) Math.PI), new Vector3f(0.5F, 0.5F, 15.5F / 16F), 0);
		}
		CasaProps.remember(r, p, s, List.of(a));
		r.setBlock(p, Blocks.AIR.defaultBlockState());
		return a;
	}

	@Override
	public boolean tick(Ctx c) {
		List<BlockPos> mine = c.get("mine");
		if (mine.isEmpty()) {
			return true;
		}
		for (BlockPos p : mine) {
			Vec3 at = Vec3.atCenterOf(p);
			if (Apparitions.dist(c, at) < 12 && Apparitions.sees(c, at, 25F)) {
				c.run.sound(ModSounds.POLTER_CUADRO, at, 0.7F, Polter.pitch(c, 0.85F, 1.05F));
				SanityManager.add(c.p, -3F);
				return true;
			}
		}
		return c.t > 20 * 120;
	}

	@Override
	public int maxTicks() {
		return 20 * 130;
	}

	/** Puts every turned picture of the run back on its nail (the case is left). */
	public static void clear(Run r) {
		Map<BlockPos, String> m = TURNED.remove(r);
		if (m == null) {
			return;
		}
		for (Map.Entry<BlockPos, String> e : m.entrySet()) {
			r.despawn(e.getValue());
			CasaProps.settleAt(r, e.getKey());
		}
	}
}
