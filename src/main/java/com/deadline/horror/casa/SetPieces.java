package com.deadline.horror.casa;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.horror.HorrorEvents;
import com.deadline.horror.casa.setpiece.SpADormir;
import com.deadline.horror.casa.setpiece.SpCena;
import com.deadline.horror.casa.setpiece.SpCuarto61;
import com.deadline.horror.casa.setpiece.SpFinalAuto;
import com.deadline.horror.casa.setpiece.SpJorgeSonambulo;
import com.deadline.horror.casa.setpiece.SpLlegada;
import com.deadline.horror.casa.setpiece.SpLuciaTecho;
import com.deadline.horror.casa.setpiece.SpNonaReza;
import com.deadline.horror.casa.setpiece.SpNonaSeRompe;
import com.deadline.horror.casa.setpiece.SpPerroCamino;
import com.deadline.horror.casa.setpiece.SpRoperoToti;
import com.deadline.horror.casa.setpiece.Stage;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.AttackBlockCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.Vec3;

/**
 * C: the set pieces of the Casa Morales acts (docs/design/casa_terror.md 2), scripted {@link com.deadline.horror.HorrorEvent}s
 * ({@code Kind.SETPIECE}, never picked at random) that {@link com.deadline.director.casa.CasaScript} fires by id at
 * their moment of the night and that post the run events it waits for:
 * <ul>
 *   <li>act 1 {@code sp_perro_camino} -- Choripán on two legs in the headlights, his back turned; gone in a flicker.</li>
 *   <li>act 2 {@code sp_llegada} -- the steps, the bolt twice, the door opens by itself: the Nona, backlit, staring.</li>
 *   <li>act 2 {@code sp_cena} -- the silent dinner; posts {@code cena:fin}.</li>
 *   <li>act 3 {@code sp_a_dormir} -- the family goes to bed in silence, Marta points at your door; posts
 *   {@code a_dormir:fin}.</li>
 *   <li>act 4 (once each, random order) {@code sp_lucia_techo}, {@code sp_jorge_sonambulo}, {@code sp_ropero_toti},
 *   {@code sp_nona_reza}.</li>
 *   <li>act 5 {@code sp_nona_se_rompe} -- the kitchen, her back turned: the hunt begins (Hunt.transform).</li>
 *   <li>act 6 {@code sp_cuarto61} -- the 1961 room, the heads, the ceiling, the corridor that repeats; posts
 *   {@code cuarto61:fin} at the front door.</li>
 *   <li>the ending {@code sp_final_auto} -- the back seat; posts {@code final:fin}.</li>
 * </ul>
 * Also owns the knock listener (a left click on a block = a knock: the wardrobe answers) and the chores of {@link Stage}.
 * Call {@link #register()} once from the mod initializer; {@link #forget(Run)} when the case ends.
 */
public final class SetPieces {
	/** One knock of a hunter (a left click on a block of the house). */
	public record Knock(BlockPos pos, long at) {
	}

	private static final Map<UUID, List<Knock>> KNOCKS = new HashMap<>();
	private static boolean done;

	private SetPieces() {
	}

	public static void register() {
		if (done) {
			return;
		}
		done = true;
		HorrorEvents.register("casa", new SpPerroCamino());
		HorrorEvents.register("casa", new SpLlegada());
		HorrorEvents.register("casa", new SpCena());
		HorrorEvents.register("casa", new SpADormir());
		HorrorEvents.register("casa", new SpLuciaTecho());
		HorrorEvents.register("casa", new SpJorgeSonambulo());
		HorrorEvents.register("casa", new SpRoperoToti());
		HorrorEvents.register("casa", new SpNonaReza());
		HorrorEvents.register("casa", new SpNonaSeRompe());
		HorrorEvents.register("casa", new SpCuarto61());
		HorrorEvents.register("casa", new SpFinalAuto());
		// a knock: a left click on any block while a case runs (nothing else happens: the house is unbreakable)
		AttackBlockCallback.EVENT.register((player, world, hand, pos, direction) -> {
			if (!world.isClientSide() && player instanceof ServerPlayer sp && !sp.isSpectator() && Director.of(sp) != null) {
				List<Knock> l = KNOCKS.computeIfAbsent(sp.getUUID(), k -> new ArrayList<>());
				long now = world.getGameTime();
				l.removeIf(k -> now - k.at() > 200);
				l.add(new Knock(pos.immutable(), now));
			}
			return InteractionResult.PASS;
		});
		ServerTickEvents.END_SERVER_TICK.register(Stage::tickChores);
	}

	/** Knocks of a player within `radius` of a point after game time `since` (oldest first). */
	public static List<Knock> knocks(ServerPlayer p, Vec3 near, double radius, long since) {
		List<Knock> out = new ArrayList<>();
		List<Knock> l = KNOCKS.get(p.getUUID());
		if (l == null) {
			return out;
		}
		for (Knock k : l) {
			if (k.at() > since && Vec3.atCenterOf(k.pos()).distanceTo(near) <= radius) {
				out.add(k);
			}
		}
		return out;
	}

	/** Forgets what the set pieces kept for a run (call it when the case ends: CasaScript.onLeave). */
	public static void forget(Run run) {
		Stage.forget(run);
		for (var p : run.hunters()) {
			KNOCKS.remove(p.getUUID());
		}
	}
}
