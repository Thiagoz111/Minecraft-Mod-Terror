package com.deadline;

import com.deadline.caseload.CaseSites;
import com.deadline.caseload.CaseType;
import com.deadline.caseload.sites.SiteBuilder;
import com.deadline.entity.AnchorEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModEntities;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;

/**
 * CI-only runtime check (-Ddeadline.smoketest=true): once the dedicated server is up, build every case site
 * in its dimension, spawn its entities, report problems and shut the server down.
 */
public final class SmokeTest {
	private SmokeTest() {
	}

	public static void register() {
		if (!Boolean.getBoolean("deadline.smoketest")) {
			return;
		}
		ServerLifecycleEvents.SERVER_STARTED.register(SmokeTest::run);
	}

	/** Scripted cases: load and place the Python-authored site, compile the script, check its checkpoints. */
	private static int scripted(MinecraftServer server, CaseType type) {
		int failures = 0;
		ServerLevel level = server.getLevel(type.levelKey());
		com.deadline.site.SiteDef def = com.deadline.site.SiteDef.get(server, type.script().siteKey());
		if (level == null || def == null) {
			DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL {}: site data or dimension missing", type.key());
			return 1;
		}
		long t0 = System.nanoTime();
		BlockPos origin;
		int placed;
		if (type.overworld()) {
			// the real overworld: find a plain 150-400 blocks from the world origin, level the pad, place the site
			origin = com.deadline.caseload.OverworldSite.findOrigin(level, BlockPos.ZERO, def, level.getRandom());
			placed = com.deadline.caseload.OverworldSite.prepareNow(level, type, origin, def);
			DeadLine.LOGGER.info("DEADLINE-SMOKE {} overworld origin {} biome {}", type.key(), origin,
					level.getBiome(origin).unwrapKey().map(k -> k.identifier().toString()).orElse("?"));
		} else {
			origin = CaseSites.origin(950);
			placed = com.deadline.site.SitePlacer.placeNow(level, origin, def);
		}
		com.deadline.director.Run run = com.deadline.director.Director.create(type, 950, level, origin, def);
		for (com.deadline.director.Chapter c : run.compiled.chapters()) {
			if (!def.points.containsKey(c.checkpoint)) {
				DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL {}: chapter {} checkpoint '{}' is not a site point", type.key(), c.n, c.checkpoint);
				failures++;
			}
			run.startChapter(c.n, false);
		}
		com.deadline.director.Director.end(type, 950);
		DeadLine.LOGGER.info("DEADLINE-SMOKE OK {} site: {} blocks, {} beats, {} points, {} ms", type.key(), placed,
				run.compiled.beats().size(), def.points.size(), (System.nanoTime() - t0) / 1_000_000);
		return failures;
	}

	private static void run(MinecraftServer server) {
		int failures = 0;
		for (CaseType type : CaseType.values()) {
			if (type.scripted()) {
				failures += scripted(server, type);
			}
			try {
				ServerLevel level = server.getLevel(type.levelKey());
				if (level == null) {
					DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL {}: dimension {} missing", type.key(), type.levelKey().identifier());
					failures++;
					continue;
				}
				long t0 = System.nanoTime();
				BlockPos origin = CaseSites.origin(900);
				SiteBuilder.Layout layout = type.newBuilder().build(level, origin, level.getRandom());
				int spawned = 0;
				Entity boss = type.boss().create(level, EntitySpawnReason.EVENT);
				if (boss instanceof HauntEntity h) {
					h.snapTo(layout.boss().x, layout.boss().y, layout.boss().z, 0, 0);
					h.setAnchored(true);
					spawned += level.addFreshEntity(h) ? 1 : 0;
				}
				AnchorEntity anchor = ModEntities.ANCHOR.create(level, EntitySpawnReason.EVENT);
				if (anchor != null) {
					anchor.setItem(new ItemStack(type.anchor()));
					anchor.snapTo(layout.anchor().x, layout.anchor().y, layout.anchor().z, 0, 0);
					spawned += level.addFreshEntity(anchor) ? 1 : 0;
				}
				for (SiteBuilder.Extra e : layout.extras()) {
					Entity ent = e.type().create(level, EntitySpawnReason.EVENT);
					if (ent != null) {
						ent.snapTo(e.pos().x, e.pos().y, e.pos().z, 0, 0);
						spawned += level.addFreshEntity(ent) ? 1 : 0;
					}
				}
				for (int i = 0; i < 40; i++) {
					level.tick(() -> true);
				}
				DeadLine.LOGGER.info("DEADLINE-SMOKE OK {}: built in {} ms, spawned {}, spawn={} boss={} anchor={}",
						type.key(), (System.nanoTime() - t0) / 1_000_000, spawned, layout.spawn(), layout.boss(), layout.anchor());
			} catch (Throwable t) {
				failures++;
				DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL " + type.key(), t);
			}
		}
		DeadLine.LOGGER.info("DEADLINE-SMOKE DONE failures={}", failures);
		server.halt(false);
	}
}
