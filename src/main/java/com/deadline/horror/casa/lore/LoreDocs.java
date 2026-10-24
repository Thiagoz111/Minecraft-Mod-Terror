package com.deadline.horror.casa.lore;

import com.deadline.director.Run;
import com.deadline.horror.Haunt;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Where the papers of {@link LoreBook} are in the house, and reading them: a right click on one opens it full screen
 * on the client ({@link LorePayload}), with the rustle of old paper and no voice.
 * <ul>
 *   <li>Kit blocks that already are documents ({@link #KIT}): Lucía's notebook on her desk, the photos of the young
 *   Nona (Pocha with Father Anselmo, 1961), the photo "Nélida y Ofelia, 1960", the box of old photos in the Nono's
 *   study (1961: the family, the basement bed, the newspaper), the missal on the floor of the 1961 room.</li>
 *   <li>Props this class lays out once per run ({@link #ensure}): Father Anselmo's letters on the boxes of the study,
 *   broken rosaries on the Nona's altar and on the floor of the 1961 room. They are item displays tracked like the
 *   blood ({@link BloodDecals#clear} removes them) and read from a "spot": a click whose hit lands near them.</li>
 * </ul>
 * Other systems may open a document too ({@link #open}), e.g. a letter found in a drawer.
 */
public final class LoreDocs {
	/** Kit block (registry path) -&gt; document. */
	public static final Map<String, String> KIT = Map.of(
			"casa_cuaderno_lemaza", LoreBook.CUADERNO,
			"casa_foto_nona_joven", LoreBook.NONA_CURA,
			"casa_foto_nelida", LoreBook.NELIDA,
			"casa_lata_galletitas_abierta", LoreBook.NELIDA,
			"casa_caja_abierta", LoreBook.FOTOS_61,
			"casa_misal", LoreBook.MISAL);

	public record Spot(Vec3 at, String doc, double radius) {
	}

	private static final class State {
		boolean placed;
		final List<Spot> spots = new ArrayList<>();
	}

	private static final Map<Run, State> STATES = new WeakHashMap<>();
	private static final Map<UUID, Long> LAST_OPEN = new HashMap<>();

	private LoreDocs() {
	}

	// ------------------------------------------------------------------ reading
	/** The document a right click hits (a kit document block, or near a laid-out prop), or null. */
	public static String docAt(Run r, BlockPos pos, BlockState st, Vec3 hit) {
		String doc = KIT.get(HouseQuery.key(st));
		if (doc != null && r.siteBox().contains(Vec3.atCenterOf(pos))) {
			return doc;
		}
		State s = STATES.get(r);
		if (s == null || hit == null) {
			return null;
		}
		Spot best = null;
		double bd = Double.MAX_VALUE;
		for (Spot sp : s.spots) {
			double d = sp.at().distanceTo(hit);
			if (d <= sp.radius() && d < bd) {
				bd = d;
				best = sp;
			}
		}
		return best == null ? null : best.doc();
	}

	/** Opens a document on a hunter's screen (paper rustle at `at`). False when it does not exist or he cannot get it. */
	public static boolean open(ServerPlayer p, Run r, String doc, Vec3 at) {
		if (p == null || !LoreBook.exists(doc)) {
			return false;
		}
		long now = p.level().getGameTime();
		Long last = LAST_OPEN.get(p.getUUID());
		if (last != null && now - last < 10 && now >= last) {
			return true;  // the same click again (both hands, a held button): already open
		}
		LAST_OPEN.put(p.getUUID(), now);
		Haunt h = r == null ? null : Haunt.peek(r);
		int flags = h != null && h.act() >= 4 ? LorePayload.LATE : 0;
		if (r != null) {
			r.sound(ModSounds.LORE_PAPEL, at != null ? at : p.position(), 0.6F, 0.9F + p.getRandom().nextFloat() * 0.2F);
		}
		if (ServerPlayNetworking.canSend(p, LorePayload.TYPE)) {
			ServerPlayNetworking.send(p, new LorePayload(doc, flags));
		}
		return true;
	}

	/** True for a couple of ticks after a document opened for him (the same click must not use his item too). */
	public static boolean justOpened(ServerPlayer p) {
		Long last = LAST_OPEN.get(p.getUUID());
		long now = p.level().getGameTime();
		return last != null && now >= last && now - last <= 2;
	}

	/** A spot where a click opens a document (a prop of yours lying there). */
	public static void addSpot(Run r, Vec3 at, String doc, double radius) {
		state(r).spots.add(new Spot(at, doc, radius));
	}

	public static void forget(Run r) {
		STATES.remove(r);
	}

	public static void forgetPlayer(ServerPlayer p) {
		LAST_OPEN.remove(p.getUUID());
	}

	private static State state(Run r) {
		return STATES.computeIfAbsent(r, k -> new State());
	}

	// ------------------------------------------------------------------ the props
	/** Lays out the letters and the rosaries once per run (when a hunter is at the house). Every lookup is guarded. */
	public static void ensure(Run r, Entity viewer) {
		State s = state(r);
		if (s.placed) {
			return;
		}
		s.placed = true;
		// Father Anselmo's letters, tied with string, on the stacked boxes of the Nono's study
		BlockPos boxes = first(r, "escritorio", "casa_cajas_apiladas");
		if (boxes != null) {
			Vec3 at = new Vec3(boxes.getX() + 0.5, surface(r, boxes, boxes.getX() + 0.5, boxes.getZ() + 0.5, viewer), boxes.getZ() + 0.5);
			if (BloodDecals.floor(r, "lore/cartas", at, 160F, 0.46F, 0.46F) != null) {
				s.spots.add(new Spot(at, LoreBook.CARTAS, 0.6));
			}
		}
		// a broken rosary on the Nona's altar, in front of the saints
		BlockPos altar = first(r, "nona_cuarto", "casa_altar");
		if (altar != null) {
			BlockState st = r.level.getBlockState(altar);
			Direction f = st.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? st.getValue(BlockStateProperties.HORIZONTAL_FACING)
					: Direction.NORTH;
			// in front of the statue, between the tea lights, on the lace of the table top
			double x = altar.getX() + 0.5 + f.getStepX() * 0.1;
			double z = altar.getZ() + 0.5 + f.getStepZ() * 0.1;
			Vec3 at = new Vec3(x, surface(r, altar, x, z, viewer), z);
			if (BloodDecals.floor(r, "lore/rosario_roto", at, f.toYRot() + 25F, 0.36F, 0.36F) != null) {
				s.spots.add(new Spot(at, LoreBook.ROSARIO, 0.55));
			}
		}
		// another one on the sand of the 1961 room, by the iron bed (beads all around)
		if (Apparitions.hasAll(r, "cuarto61_cama", "cuarto61")) {
			Vec3 bed = r.at("cuarto61_cama");
			Vec3 mid = r.at("cuarto61");
			Vec3 dir = mid.subtract(bed).multiply(1, 0, 1);
			Vec3 v = dir.lengthSqr() > 0.01 ? bed.add(dir.normalize().scale(0.9)) : bed.add(0.6, 0, 0);
			Vec3 at = BloodDecals.onFloor(r, v);
			if (BloodDecals.floor(r, "lore/rosario_roto", at, 70F, 0.36F, 0.36F) != null) {
				s.spots.add(new Spot(at, LoreBook.ROSARIO, 0.55));
			}
		}
	}

	/** The first block of a kit key inside a room area (null when the site has neither). */
	private static BlockPos first(Run r, String area, String key) {
		if (!Apparitions.hasArea(r, area)) {
			return null;
		}
		List<BlockPos> l = HouseQuery.blocks(r, area, st -> key.equals(HouseQuery.key(st)));
		return l.isEmpty() ? null : l.get(0);
	}

	/** Height of the top of a block's outline (a table top), absolute. */
	public static double top(Run r, BlockPos pos) {
		VoxelShape sh = r.level.getBlockState(pos).getShape(r.level, pos);
		return pos.getY() + (sh.isEmpty() ? 1.0 : sh.max(Direction.Axis.Y));
	}

	/**
	 * The surface of a piece of furniture under a point (x, z): a ray down through the block's outline, so a table
	 * top is found under the statue and the candles standing on it. Falls back to {@link #top} when the ray misses.
	 */
	public static double surface(Run r, BlockPos pos, double x, double z, Entity viewer) {
		Vec3 from = new Vec3(x, pos.getY() + 0.999, z);  // from inside the block: never the one above
		Vec3 to = new Vec3(x, pos.getY() - 0.05, z);
		if (viewer != null) {
			BlockHitResult hit = r.level.clip(new ClipContext(from, to, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, viewer));
			if (hit.getType() == HitResult.Type.BLOCK && hit.getBlockPos().equals(pos)) {
				return hit.getLocation().y;
			}
		}
		return top(r, pos);
	}
}
