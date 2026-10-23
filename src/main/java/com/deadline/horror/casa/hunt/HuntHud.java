package com.deadline.horror.casa.hunt;

import com.deadline.director.Director;
import com.deadline.director.Run;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * Feeds the client what the hunt HUD needs (HuntHudPayload): the lungs bar, the hiding-place overlay, the heartbeat
 * that beats harder as she comes closer and the chase music. Only sent while something is going on.
 */
final class HuntHud {
	private static final Set<UUID> SHOWING = new HashSet<>();

	private HuntHud() {
	}

	static void tick(MinecraftServer server) {
		if (server.getTickCount() % 2 != 0) {
			return;
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			Run run = Director.of(p);
			boolean hunt = run != null && Hunt.active(run);
			boolean hidden = HideSpots.hidden(p);
			float breath = Breath.breath(p);
			boolean busy = hunt || hidden || breath < 99.9F || Breath.holding(p);
			if (!busy) {
				if (SHOWING.remove(p.getUUID())) {
					send(p, new HuntHudPayload(100F, 0, -1F, 0));
				}
				continue;
			}
			if (!hidden && !hunt && server.getTickCount() % 6 != 0) {
				continue;  // only the lungs bar to refresh
			}
			SHOWING.add(p.getUUID());
			float dist = -1F;
			int flags = 0;
			if (hunt) {
				flags |= HuntHudPayload.HUNT;
				NonaRotaEntity n = Hunt.nona(run);
				if (n != null && n.level() == p.level()) {
					dist = n.distanceTo(p);
					if (n.isChasing(p)) {
						flags |= HuntHudPayload.CHASED;
					}
				}
			}
			if (HideSpots.beingSearched(p)) {
				flags |= HuntHudPayload.SEARCHED;
			}
			if (Breath.holding(p)) {
				flags |= HuntHudPayload.HOLDING;
			}
			if (Breath.spent(p)) {
				flags |= HuntHudPayload.SPENT;
			}
			send(p, new HuntHudPayload(breath, HideSpots.typeOf(p).ordinal(), dist, flags));
		}
	}

	/** Clears the client's hunt HUD at once (the hunt ended). */
	static void clear(ServerPlayer p) {
		SHOWING.remove(p.getUUID());
		send(p, new HuntHudPayload(Breath.breath(p), HideSpots.typeOf(p).ordinal(), -1F, 0));
	}

	static void forget(ServerPlayer p) {
		SHOWING.remove(p.getUUID());
	}

	private static void send(ServerPlayer p, HuntHudPayload payload) {
		if (ServerPlayNetworking.canSend(p, HuntHudPayload.TYPE)) {
			ServerPlayNetworking.send(p, payload);
		}
	}
}
