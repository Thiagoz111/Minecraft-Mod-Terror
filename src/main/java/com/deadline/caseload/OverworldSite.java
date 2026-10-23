package com.deadline.caseload;

import com.deadline.DeadLine;
import com.deadline.site.SiteDef;
import com.deadline.site.SitePlacer;
import com.mojang.datafixers.util.Pair;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.phys.AABB;

/**
 * Puts a case site into the player's real overworld (docs/design/casa_terror.md 6.10): finds a plain 150-400 blocks
 * away (the level's biome search, else the flattest spot sampled from the generator's heightmaps), levels a pad of the
 * site footprint + {@link #MARGIN} (dirt/stone below, grass on top, everything above cleared up to +{@link #CLEAR_UP},
 * the outer {@link #SMOOTH} blocks blended into the terrain) with the chunks force-loaded, then places the site with
 * {@link SitePlacer} in batches and lets the chunks go. The footprint is read from the {@link SiteDef} at runtime.
 */
public final class OverworldSite {
	public static final int MARGIN = 6;
	public static final int CLEAR_UP = 40;
	public static final int SMOOTH = 2;
	public static final int MIN_DIST = 150, MAX_DIST = 400;
	/** Columns levelled per tick. */
	private static final int COLUMNS_PER_TICK = 160;
	/** Ticks to wait for the forced chunks before levelling anyway (getBlockState then loads what is missing). */
	private static final int CHUNK_WAIT = 20 * 20;
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;
	private static final List<Job> JOBS = new ArrayList<>();

	private OverworldSite() {
	}

	// ------------------------------------------------------------------ finding a spot
	public static boolean preferred(Holder<Biome> b) {
		return b.is(Biomes.PLAINS) || b.is(Biomes.SUNFLOWER_PLAINS) || b.is(Biomes.SAVANNA) || b.is(Biomes.MEADOW);
	}

	/** Footprint centre (x, z) relative to the site origin. */
	private static int centreX(SiteDef def) {
		return def.min.getX() + def.w / 2;
	}

	private static int centreZ(SiteDef def) {
		return def.min.getZ() + def.d / 2;
	}

	/**
	 * Chooses the site origin for a hunter standing at {@code from}: a plains/sunflower plains/savanna/meadow spot
	 * {@link #MIN_DIST}-{@link #MAX_DIST} blocks away (biome search), else the flattest dry spot of a ring of samples.
	 * Uses only the biome source and the generator's base heights, so no chunk is loaded or generated.
	 */
	public static BlockPos findOrigin(ServerLevel level, BlockPos from, SiteDef def, RandomSource rnd) {
		List<BlockPos> candidates = new ArrayList<>();
		double a0 = rnd.nextDouble() * Math.PI * 2;
		int sea = level.getSeaLevel();
		for (int k = 0; k < 6; k++) {
			double a = a0 + k * Math.PI / 3;
			BlockPos c = new BlockPos(from.getX() + (int) (Math.cos(a) * 275), sea, from.getZ() + (int) (Math.sin(a) * 275));
			Pair<BlockPos, Holder<Biome>> hit;
			try {
				hit = level.findClosestBiome3d(OverworldSite::preferred, c, 128, 16, 400);  // only around sea level
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.warn("Biome search failed around {}", c, ex);
				hit = null;
			}
			if (hit != null) {
				BlockPos p = hit.getFirst();
				double d = Math.sqrt(sq(p.getX() - from.getX()) + sq(p.getZ() - from.getZ()));
				if (d >= MIN_DIST && d <= MAX_DIST) {
					candidates.add(p);
				}
			}
		}
		BlockPos best = null;
		double bestScore = Double.MAX_VALUE;
		int bestY = sea;
		for (BlockPos c : candidates) {
			double[] s = score(level, c.getX(), c.getZ(), def);
			if (s[0] < bestScore) {
				bestScore = s[0];
				best = c;
				bestY = (int) s[1];
			}
		}
		if (best == null || bestScore > 40) {
			// fallback: the flattest dry spot of a ring of samples (any biome; plains still win ties)
			for (int k = 0; k < 28; k++) {
				double a = rnd.nextDouble() * Math.PI * 2;
				double r = MIN_DIST + 20 + rnd.nextDouble() * (MAX_DIST - MIN_DIST - 40);
				int x = from.getX() + (int) (Math.cos(a) * r);
				int z = from.getZ() + (int) (Math.sin(a) * r);
				double[] s = score(level, x, z, def);
				if (!preferred(level.getBiome(new BlockPos(x, (int) s[1], z)))) {
					s[0] += 12;
				}
				if (s[0] < bestScore) {
					bestScore = s[0];
					best = new BlockPos(x, 0, z);
					bestY = (int) s[1];
				}
			}
		}
		if (best == null) {
			best = from.offset(MIN_DIST + 50, 0, 0);
			bestY = sea + 1;
		}
		// y = the first air layer above the ground; never so low that the basement would cut through the world floor
		int y = Math.max(bestY + 1, level.dimensionType().minY() - def.min.getY() + 2);
		BlockPos origin = new BlockPos(best.getX() - centreX(def), y, best.getZ() - centreZ(def));
		DeadLine.LOGGER.info("Overworld site {}: origin {} (score {}, {} biome candidates)", def.key, origin, (int) bestScore, candidates.size());
		return origin;
	}

	private static double sq(double v) {
		return v * v;
	}

	/**
	 * [score, ground block y] of a footprint centred on (cx, cz): height spread + a heavy penalty per wet sample (lakes,
	 * rivers, ocean) + a penalty for ground below sea level. Lower is better.
	 */
	private static double[] score(ServerLevel level, int cx, int cz, SiteDef def) {
		ChunkGenerator gen = level.getChunkSource().getGenerator();
		RandomState rs = level.getChunkSource().randomState();
		int hw = def.w / 2 + MARGIN;
		int hd = def.d / 2 + MARGIN;
		int[] hs = new int[25];
		int wet = 0;
		int n = 0;
		for (int i = 0; i < 5; i++) {
			for (int j = 0; j < 5; j++) {
				int x = cx - hw + i * 2 * hw / 4;
				int z = cz - hd + j * 2 * hd / 4;
				int top = gen.getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, level, rs);
				int floor = gen.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, level, rs);
				if (top - floor > 0) {
					wet++;
				}
				hs[n++] = floor - 1; // heightmaps give the first free block: the ground block is one below
			}
		}
		Arrays.sort(hs);
		int median = hs[12];
		double spread = hs[22] - hs[2];
		double s = spread + wet * 12.0 + Math.max(0, level.getSeaLevel() - median) * 4.0;
		return new double[] {s, median};
	}

	// ------------------------------------------------------------------ levelling + placing
	/** A site being levelled and placed. */
	private static final class Job {
		final ServerLevel level;
		final CaseType type;
		final BlockPos origin;
		final SiteDef def;
		final Runnable onDone;
		/** Footprint (inclusive) and the levelled rectangle around it. */
		final int fx0, fz0, fx1, fz1, ox0, oz0, ox1, oz1;
		final int padY;
		final int bottomY;
		final List<long[]> chunks = new ArrayList<>();
		int phase;
		int cursor;
		int waited;

		Job(ServerLevel level, CaseType type, BlockPos origin, SiteDef def, Runnable onDone) {
			this.level = level;
			this.type = type;
			this.origin = origin;
			this.def = def;
			this.onDone = onDone;
			fx0 = origin.getX() + def.min.getX();
			fz0 = origin.getZ() + def.min.getZ();
			fx1 = fx0 + def.w - 1;
			fz1 = fz0 + def.d - 1;
			ox0 = fx0 - MARGIN - SMOOTH;
			oz0 = fz0 - MARGIN - SMOOTH;
			ox1 = fx1 + MARGIN + SMOOTH;
			oz1 = fz1 + MARGIN + SMOOTH;
			padY = origin.getY() - 1;
			bottomY = Math.min(padY - 4, origin.getY() + def.min.getY() - 2);
			for (int cx = ox0 >> 4; cx <= ox1 >> 4; cx++) {
				for (int cz = oz0 >> 4; cz <= oz1 >> 4; cz++) {
					chunks.add(new long[] {cx, cz});
				}
			}
		}

		int width() {
			return ox1 - ox0 + 1;
		}

		int columns() {
			return width() * (oz1 - oz0 + 1);
		}

		void force(boolean on) {
			for (long[] c : chunks) {
				level.setChunkForced((int) c[0], (int) c[1], on);
			}
		}

		boolean chunksReady() {
			for (long[] c : chunks) {
				if (!level.getChunkSource().hasChunk((int) c[0], (int) c[1])) {
					return false;
				}
			}
			return true;
		}

		/** Vanilla things standing on the future pad (cows, items, boats) would end up inside the walls. */
		void clearEntities() {
			AABB box = new AABB(ox0, padY - 8, oz0, ox1 + 1, padY + CLEAR_UP + 1, oz1 + 1);
			for (Entity e : level.getEntities((Entity) null, box, e -> !(e instanceof Player)
					&& "minecraft".equals(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace()))) {
				e.discard();
			}
		}

		/** Levels up to `budget` columns; true when every column is done. */
		boolean levelColumns(int budget) {
			BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
			int total = columns();
			while (cursor < total && budget-- > 0) {
				int x = ox0 + cursor % width();
				int z = oz0 + cursor / width();
				column(m, x, z);
				cursor++;
			}
			return cursor >= total;
		}

		private void column(BlockPos.MutableBlockPos m, int x, int z) {
			boolean foot = x >= fx0 && x <= fx1 && z >= fz0 && z <= fz1;
			// Chebyshev distance outside the pad (footprint + margin): 0 on the pad, 1..SMOOTH on the blend ring
			int dx = Math.max(0, Math.max((fx0 - MARGIN) - x, x - (fx1 + MARGIN)));
			int dz = Math.max(0, Math.max((fz0 - MARGIN) - z, z - (fz1 + MARGIN)));
			int ring = Math.max(dx, dz);
			int ground = groundY(m, x, z);
			int top = ring == 0 ? padY : (int) Math.round(padY + (ground - padY) * ring / (double) (SMOOTH + 1));
			// everything above the new surface goes (trees, tall grass, snow, hills), up to +CLEAR_UP over the pad
			int clearTo = Math.max(padY + CLEAR_UP, ground + 1);
			for (int y = top + 1; y <= clearTo; y++) {
				m.set(x, y, z);
				if (!level.getBlockState(m).isAir()) {
					level.setBlock(m, Blocks.AIR.defaultBlockState(), FLAGS);
				}
			}
			// fill below up to the surface: under the house down past its basement, elsewhere down to the old ground
			int floor = foot ? bottomY : Math.max(ground + 1, top - 24);
			for (int y = top - 1; y >= floor; y--) {
				m.set(x, y, z);
				BlockState s = level.getBlockState(m);
				if (!isGround(s)) {
					level.setBlock(m, (top - y <= 3 ? Blocks.DIRT : Blocks.STONE).defaultBlockState(), FLAGS);
				} else if (!foot && y <= ground) {
					break;
				}
			}
			m.set(x, top, z);
			BlockState s = level.getBlockState(m);
			if (ring == 0 || !isGround(s) || s.is(Blocks.DIRT) || s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.PODZOL)) {
				level.setBlock(m, Blocks.GRASS_BLOCK.defaultBlockState(), FLAGS);
			}
		}

		/** Height of the natural ground (ignoring trees, plants and fluids) in a column around the pad. */
		private int groundY(BlockPos.MutableBlockPos m, int x, int z) {
			int start = Math.max(padY + CLEAR_UP, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z));
			for (int y = Math.min(start, padY + CLEAR_UP + 96); y > padY - 24; y--) {
				m.set(x, y, z);
				if (isGround(level.getBlockState(m))) {
					return y;
				}
			}
			return padY - 24;
		}
	}

	/** Solid natural ground: not air, fluid, plants, logs or leaves. */
	static boolean isGround(BlockState s) {
		return !s.isAir() && s.getFluidState().isEmpty() && s.isSolid() && !s.is(BlockTags.LOGS) && !s.is(BlockTags.LEAVES);
	}

	/**
	 * Levels the pad and places the site in batches (chunks force-loaded meanwhile), then runs onDone. Re-placing at the
	 * same origin resets the house: the clearing pass removes whatever was there.
	 */
	public static void prepareAndPlace(ServerLevel level, CaseType type, BlockPos origin, SiteDef def, Runnable onDone) {
		for (Job j : JOBS) {
			if (j.type == type) {
				DeadLine.LOGGER.info("Overworld site {} is already being placed", type.key());
				return;
			}
		}
		Job j = new Job(level, type, origin, def, onDone);
		CaseSites.get(level.getServer()).setPlacing(type, true);
		j.force(true);
		JOBS.add(j);
		DeadLine.LOGGER.info("Levelling overworld site {} at {} ({} columns, {} chunks)", type.key(), origin, j.columns(), j.chunks.size());
	}

	public static boolean busy(CaseType type) {
		return JOBS.stream().anyMatch(j -> j.type == type);
	}

	/** Levels and places a site right now, without batching (smoke tests). Returns the number of site blocks placed. */
	public static int prepareNow(ServerLevel level, CaseType type, BlockPos origin, SiteDef def) {
		Job j = new Job(level, type, origin, def, null);
		j.clearEntities();
		j.levelColumns(Integer.MAX_VALUE);
		return SitePlacer.placeNow(level, origin, def);
	}

	public static void tick(MinecraftServer server) {
		Iterator<Job> it = JOBS.iterator();
		while (it.hasNext()) {
			Job j = it.next();
			switch (j.phase) {
				case 0 -> {
					if (j.chunksReady() || ++j.waited > CHUNK_WAIT) {
						j.clearEntities();
						j.phase = 1;
					}
				}
				case 1 -> {
					if (j.levelColumns(COLUMNS_PER_TICK)) {
						j.phase = 2;
						SitePlacer.place(j.level, j.origin, j.def, () -> j.phase = 3);
					}
				}
				case 3 -> {
					j.force(false);
					CaseSites.get(server).setPlacing(j.type, false);
					it.remove();
					DeadLine.LOGGER.info("Overworld site {} ready at {}", j.type.key(), j.origin);
					if (j.onDone != null) {
						j.onDone.run();
					}
					continue;
				}
				default -> {
				}
			}
			break; // one site at a time
		}
	}

	/** After a restart in the middle of a placement: place it again (its chunks are still forced) and release them. */
	public static void resume(MinecraftServer server) {
		CaseSites sites = CaseSites.get(server);
		for (String key : sites.placingKeys()) {
			CaseType type = CaseType.byKey(key);
			BlockPos origin = sites.overworldOrigin(type);
			SiteDef def = type.script() == null ? null : SiteDef.get(server, type.script().siteKey());
			if (!type.overworld() || origin == null || def == null) {
				sites.setPlacing(type, false);
				continue;
			}
			DeadLine.LOGGER.info("Resuming the interrupted placement of overworld site {}", key);
			prepareAndPlace(server.overworld(), type, origin, def, null);
		}
	}

	public static void clear() {
		JOBS.clear();
	}
}
