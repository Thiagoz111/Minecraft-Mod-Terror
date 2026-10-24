package com.deadline.horror.casa.hunt;

import com.deadline.casa.CasaProps;
import com.deadline.director.Director;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Drawers;
import com.deadline.horror.casa.Tap;
import com.deadline.voice.NoiseMeter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Hiding places of the house (docs/design/casa_terror.md 6.2, markers of 11: {@code hide_<id>} inside looking out,
 * {@code hide_<id>_out} in front of it). Right-click the wardrobe door, the bed, the bathtub, the pantry door or the
 * trunk while standing in front of it and the hunter gets in: he sits on an invisible {@link HideSeatEntity} with his
 * eyes at the slats, can only turn his head, and sneaks to get out. Works in every act; while hidden his noise is
 * halved, the hunter cannot see him and only finds him by searching that very place (and only if he breathes).
 * Random events must not jumpscare a hidden hunter: check {@link #hidden(ServerPlayer)}.
 */
public final class HideSpots {
	/** Kind of hiding place: the overlay the client draws and how she searches it. */
	public enum Type {
		NONE, WARDROBE, BED, TUB, CHEST, DOOR;

		public static Type of(int id) {
			Type[] v = values();
			return id >= 0 && id < v.length ? v[id] : NONE;
		}
	}

	/** One hiding place of a run, absolute positions. low = she bends to the floor to look (bed, trunk). */
	public record Spot(String id, Type type, Vec3 hide, Vec3 out, float yaw, List<String> doors) {
		public boolean low() {
			return type == Type.BED || type == Type.CHEST;
		}
	}

	/** A hunter inside a hiding place. */
	static final class Hidden {
		final Run run;
		final Spot spot;
		final HideSeatEntity seat;
		final long since;
		boolean searched;

		Hidden(Run run, Spot spot, HideSeatEntity seat, long since) {
			this.run = run;
			this.spot = spot;
			this.seat = seat;
			this.since = since;
		}
	}

	private static final Map<Run, List<Spot>> SPOTS = new WeakHashMap<>();
	private static final Map<UUID, Hidden> HIDDEN = new HashMap<>();

	private HideSpots() {
	}

	// ------------------------------------------------------------------ queries
	/** True while the player is inside a hiding place. */
	public static boolean hidden(ServerPlayer p) {
		return p != null && p.getVehicle() instanceof HideSeatEntity;
	}

	/** The hiding place the player is in (null when he is not hidden). */
	public static Spot spotOf(ServerPlayer p) {
		Hidden h = p == null ? null : HIDDEN.get(p.getUUID());
		return h != null && hidden(p) ? h.spot : null;
	}

	/** Kind of place the player hides in (NONE when he is out). */
	public static Type typeOf(ServerPlayer p) {
		Spot s = spotOf(p);
		return s == null ? Type.NONE : s.type();
	}

	/** True while she is searching the place this player hides in (her face at the slats). */
	public static boolean beingSearched(ServerPlayer p) {
		Hidden h = HIDDEN.get(p.getUUID());
		return h != null && h.searched;
	}

	/** Noise multiplier of a player (the noise meter): halved inside a hiding place. */
	public static float noiseFactor(ServerPlayer p) {
		return hidden(p) ? 0.5F : 1F;
	}

	/** Every hiding place of the run's site (the ones with both markers). */
	public static List<Spot> spots(Run run) {
		if (run == null) {
			return List.of();
		}
		return SPOTS.computeIfAbsent(run, HideSpots::build);
	}

	private static List<Spot> build(Run run) {
		List<Spot> out = new ArrayList<>();
		for (String k : HouseQuery.points(run, "hide_")) {
			if (k.endsWith("_out") || !run.def.points.containsKey(k + "_out")) {
				continue;
			}
			String id = k.substring("hide_".length());
			Vec3 hide = run.at(k);
			Vec3 o = run.at(k + "_out");
			List<String> doors = new ArrayList<>();
			for (Map.Entry<String, BlockPos> d : run.def.doors.entrySet()) {
				String n = d.getKey();
				if ((n.equals(id) || n.startsWith(id + "_")) && Vec3.atCenterOf(run.origin.offset(d.getValue())).distanceTo(hide) < 3.2) {
					doors.add(n);
				}
			}
			out.add(new Spot(id, typeOfId(id), hide, o, Props.yawTowards(hide, o), List.copyOf(doors)));
		}
		return List.copyOf(out);
	}

	private static Type typeOfId(String id) {
		if (id.startsWith("ropero")) {
			return Type.WARDROBE;
		}
		if (id.startsWith("cama")) {
			return Type.BED;
		}
		if (id.startsWith("banera") || id.startsWith("banadera")) {
			return Type.TUB;
		}
		if (id.startsWith("baul")) {
			return Type.CHEST;
		}
		return Type.DOOR;
	}

	/** The hunter hidden in this place (null when it is empty). */
	public static ServerPlayer occupant(Run run, Spot s) {
		for (Map.Entry<UUID, Hidden> e : HIDDEN.entrySet()) {
			Hidden h = e.getValue();
			if (h.run == run && h.spot.id().equals(s.id())) {
				ServerPlayer p = h.seat.getFirstPassenger() instanceof ServerPlayer sp ? sp : null;
				if (p != null) {
					return p;
				}
			}
		}
		return null;
	}

	// ------------------------------------------------------------------ getting in
	/** UseBlockCallback: a click on a hiding place (wardrobe door, bed, tub, pantry, trunk) from in front of it. */
	static InteractionResult onUse(Player player, Level level, InteractionHand hand, BlockHitResult hit) {
		if (!(player instanceof ServerPlayer sp) || hand != InteractionHand.MAIN_HAND || sp.isPassenger() || sp.isSpectator()
				|| sp.isShiftKeyDown()) {
			return InteractionResult.PASS;
		}
		Run run = Director.of(sp);
		if (run == null || run.level != level) {
			return InteractionResult.PASS;
		}
		List<Spot> spots = spots(run);
		if (spots.isEmpty()) {
			return InteractionResult.PASS;
		}
		BlockPos pos = hit.getBlockPos();
		BlockState state = level.getBlockState(pos);
		if (Drawers.is(state) || Tap.is(state)) {
			return InteractionResult.PASS;  // the bedside table (the Nona's radio), the dresser, the tub tap: the interactables
		}
		Vec3 clicked = Vec3.atCenterOf(pos);
		Spot best = null;
		double bd = Double.MAX_VALUE;
		for (Spot s : spots) {
			double dOut = horizontal(sp.position(), s.out());
			if (dOut > 2.6 || Math.abs(sp.getY() - s.out().y) > 1.6 || !partOf(run, s, pos, state)) {
				continue;
			}
			double dClick = clicked.distanceTo(s.hide().add(0, 0.5, 0));
			for (String d : s.doors()) {
				dClick = Math.min(dClick, clicked.distanceTo(HouseQuery.doorPos(run, d)));
			}
			if (dClick > 2.4) {
				continue;
			}
			double score = dClick + dOut * 0.5;
			if (score < bd) {
				bd = score;
				best = s;
			}
		}
		if (best == null) {
			return InteractionResult.PASS;
		}
		if (occupant(run, best) != null) {
			return InteractionResult.PASS;
		}
		NonaRotaEntity n = Hunt.nona(run);
		if (n != null && n.position().distanceTo(best.out()) < 1.6) {
			return InteractionResult.FAIL;  // she is right there
		}
		return enter(sp, run, best) ? InteractionResult.SUCCESS : InteractionResult.PASS;
	}

	/**
	 * True when the clicked block is the hiding place itself: one of its doors, the block it is in (or the one over it:
	 * the bed, the tub's curtain), or a piece of its own bed / tub right beside it. The furniture next to it is not.
	 */
	private static boolean partOf(Run run, Spot s, BlockPos pos, BlockState state) {
		for (String d : s.doors()) {
			BlockPos rel = run.def.doors.get(d);
			if (rel != null) {
				BlockPos door = run.origin.offset(rel);
				if (pos.equals(door) || pos.equals(door.above())) {
					return true;
				}
			}
		}
		BlockPos hide = BlockPos.containing(s.hide());
		int dy = pos.getY() - hide.getY();
		int dx = Math.abs(pos.getX() - hide.getX());
		int dz = Math.abs(pos.getZ() - hide.getZ());
		if (dy < 0 || dy > 1 || dx > 1 || dz > 1) {
			return false;
		}
		if (dx == 0 && dz == 0) {
			return true;
		}
		String k = CasaProps.path(state);
		return switch (s.type()) {
			case BED -> k.startsWith("casa_cama_");
			case TUB -> k.startsWith("casa_banadera") || k.startsWith("casa_cortina_ducha");
			default -> false;
		};
	}

	private static double horizontal(Vec3 a, Vec3 b) {
		double dx = a.x - b.x;
		double dz = a.z - b.z;
		return Math.sqrt(dx * dx + dz * dz);
	}

	/** Puts the player in the hiding place (false if the seat could not be made). */
	public static boolean enter(ServerPlayer p, Run run, Spot s) {
		HideSeatEntity seat = HuntEntities.HIDE_SEAT.create(run.level, EntitySpawnReason.EVENT);
		if (seat == null) {
			return false;
		}
		Vec3 eye = eyeFor(run, s);
		// the rider sits at the seat with the vehicle attachment of a player (0.6) below it: eye = seat + 1.02
		double seatY = eye.y - (p.getEyeHeight() - 0.6);
		seat.setup(s.out());
		seat.snapTo(eye.x, seatY, eye.z, s.yaw(), 0F);
		run.level.addFreshEntity(seat);
		p.teleportTo(run.level, eye.x, seatY - 0.6, eye.z, java.util.Set.of(), s.yaw(), 0F, false);
		if (!p.startRiding(seat, true, false)) {
			seat.discard();
			return false;
		}
		HIDDEN.put(p.getUUID(), new Hidden(run, s, seat, run.now()));
		open(run, s, false);
		run.level.playSound(null, s.hide().x, s.hide().y + 0.5, s.hide().z, s.doors().isEmpty() ? SoundEvents.WOOL_PLACE
				: SoundEvents.WOODEN_DOOR_CLOSE, SoundSource.PLAYERS, 0.5F, 0.8F);
		NoiseMeter.add(p, 12F);  // halved: he is inside now
		Breath.touch(p);
		run.post("hide:" + s.id());
		return true;
	}

	/** Eye position inside the place: in the wardrobe door's own slab (so the view goes through it), under the bed... */
	static Vec3 eyeFor(Run run, Spot s) {
		Vec3 hide = s.hide();
		Vec3 dir = s.out().subtract(hide);
		dir = new Vec3(dir.x, 0, dir.z);
		Vec3 n = dir.lengthSqr() > 1.0E-4 ? dir.normalize() : new Vec3(0, 0, 1);
		switch (s.type()) {
			case BED -> {
				return new Vec3(hide.x + n.x * 0.2, hide.y + 0.45, hide.z + n.z * 0.2);
			}
			case TUB -> {
				return new Vec3(hide.x, hide.y + 0.95, hide.z);
			}
			case CHEST -> {
				return new Vec3(hide.x, hide.y + 0.55, hide.z);
			}
			default -> {
				Vec3 slab = doorSlab(run, s, hide, n);
				if (slab != null) {
					return slab;
				}
				return new Vec3(hide.x + n.x * 0.3, hide.y + 1.5, hide.z + n.z * 0.3);
			}
		}
	}

	/** Centre of the closed door's slab right in front of the hiding place, at eye height (null without a door). */
	private static Vec3 doorSlab(Run run, Spot s, Vec3 hide, Vec3 n) {
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (String d : s.doors()) {
			BlockPos rel = run.def.doors.get(d);
			if (rel == null) {
				continue;
			}
			BlockPos abs = run.origin.offset(rel);
			Vec3 c = Vec3.atBottomCenterOf(abs);
			// the door in line with the hiding place (a double wardrobe has two)
			double side = Math.abs((c.x - hide.x) * n.z - (c.z - hide.z) * n.x);
			double ahead = (c.x - hide.x) * n.x + (c.z - hide.z) * n.z;
			if (ahead < -0.2) {
				continue;
			}
			double score = side * 3 + Math.abs(ahead);
			if (score < bd) {
				bd = score;
				best = abs;
			}
		}
		if (best == null) {
			return null;
		}
		BlockState st = run.level.getBlockState(best);
		if (!(st.getBlock() instanceof DoorBlock)) {
			return null;
		}
		VoxelShape sh = st.setValue(DoorBlock.OPEN, false).getShape(run.level, best);
		if (sh.isEmpty()) {
			return null;
		}
		AABB b = sh.bounds().move(best);
		double y = hide.y + 1.5;
		if (Math.abs(n.x) >= Math.abs(n.z)) {
			return new Vec3((b.minX + b.maxX) * 0.5, y, hide.z);
		}
		return new Vec3(hide.x, y, (b.minZ + b.maxZ) * 0.5);
	}

	/** Opens / closes the doors of a hiding place (she flings the wardrobe open; the hunter pulls it shut). */
	static void open(Run run, Spot s, boolean open) {
		if (s.doors().isEmpty()) {
			return;
		}
		for (String d : s.doors()) {
			if (run.doorOpen(d) != open) {
				run.door(d, open, false);
			}
		}
		run.level.playSound(null, s.hide().x, s.hide().y + 1.0, s.hide().z, open ? SoundEvents.WOODEN_DOOR_OPEN : SoundEvents.WOODEN_DOOR_CLOSE,
				SoundSource.BLOCKS, 0.7F, open ? 0.6F : 0.75F);
	}

	/** Marks the hiding place as being searched (the client drops the slats overlay: the door is open, she is there). */
	static void searched(Run run, Spot s, boolean on) {
		for (Hidden h : HIDDEN.values()) {
			if (h.run == run && h.spot.id().equals(s.id())) {
				h.searched = on;
			}
		}
	}

	// ------------------------------------------------------------------ getting out
	/** The seat lost its rider (he sneaked out, logged out, was teleported): a creak, and he is out. */
	static void seatEmptied(HideSeatEntity seat) {
		for (Iterator<Map.Entry<UUID, Hidden>> it = HIDDEN.entrySet().iterator(); it.hasNext();) {
			Hidden h = it.next().getValue();
			if (h.seat == seat) {
				it.remove();
				h.run.level.playSound(null, h.spot.out().x, h.spot.out().y + 0.5, h.spot.out().z, SoundEvents.WOODEN_DOOR_OPEN,
						SoundSource.PLAYERS, 0.45F, 0.85F);
				Hunt.noise(h.run, h.spot.hide(), 10F);
			}
		}
	}

	/** She drags him out (capture): out of the seat and the doors flung open. */
	static void drag(ServerPlayer p) {
		Hidden h = HIDDEN.remove(p.getUUID());
		if (p.getVehicle() instanceof HideSeatEntity seat) {
			p.stopRiding();
			seat.discard();
		}
		if (h != null) {
			h.seat.discard();
			open(h.run, h.spot, true);
		}
	}

	/** Lets every hunter of the run out (the hunt ends, the act changes). */
	public static void releaseAll(Run run) {
		for (Iterator<Map.Entry<UUID, Hidden>> it = HIDDEN.entrySet().iterator(); it.hasNext();) {
			Hidden h = it.next().getValue();
			if (h.run == run) {
				it.remove();
				if (h.seat.getFirstPassenger() instanceof ServerPlayer p) {
					p.stopRiding();
				}
				h.seat.discard();
			}
		}
	}

	/** Lets one hunter out (a set piece that needs him). */
	public static void release(ServerPlayer p) {
		Hidden h = HIDDEN.remove(p.getUUID());
		if (p.getVehicle() instanceof HideSeatEntity seat) {
			p.stopRiding();
			seat.discard();
		}
		if (h != null) {
			h.seat.discard();
		}
	}

	static void forget(ServerPlayer p) {
		release(p);
	}

	static void tick(MinecraftServer server) {
		if (HIDDEN.isEmpty()) {
			return;
		}
		for (Iterator<Map.Entry<UUID, Hidden>> it = HIDDEN.entrySet().iterator(); it.hasNext();) {
			Map.Entry<UUID, Hidden> e = it.next();
			Hidden h = e.getValue();
			ServerPlayer p = server.getPlayerList().getPlayer(e.getKey());
			if (p == null || h.seat.isRemoved() || p.getVehicle() != h.seat || Director.get(h.run.type, h.run.site) != h.run) {
				it.remove();
				if (p != null && p.getVehicle() == h.seat) {
					p.stopRiding();
				}
				h.seat.discard();
			}
		}
	}
}
