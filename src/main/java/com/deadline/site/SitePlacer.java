package com.deadline.site;

import com.deadline.DeadLine;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Places a {@link SiteDef} into the world a few thousand blocks per tick (a whole school at once would freeze the
 * server for seconds while the player is fading in). Neighbour updates are skipped so half-built doors survive.
 */
public final class SitePlacer {
	public static final int PER_TICK = 6000;
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;
	private static final List<Job> JOBS = new ArrayList<>();

	public static final class Job {
		final ServerLevel level;
		final BlockPos origin;
		final SiteDef def;
		final Runnable onDone;
		int cursor;
		int placed;

		Job(ServerLevel level, BlockPos origin, SiteDef def, Runnable onDone) {
			this.level = level;
			this.origin = origin;
			this.def = def;
			this.onDone = onDone;
		}

		/** Places up to `budget` blocks; true when the site is complete. */
		boolean step(int budget) {
			short[] data = def.data;
			BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
			while (cursor < data.length && budget > 0) {
				int idx = data[cursor] & 0xFFFF;
				if (idx != 0) {
					BlockState st = def.palette[idx];
					BlockPos c = def.cell(cursor);
					m.set(origin.getX() + c.getX(), origin.getY() + c.getY(), origin.getZ() + c.getZ());
					level.setBlock(m, st, FLAGS);
					placed++;
					budget--;
				}
				cursor++;
			}
			return cursor >= data.length;
		}

		public float progress() {
			return def.data.length == 0 ? 1F : (float) cursor / def.data.length;
		}
	}

	private SitePlacer() {
	}

	public static Job place(ServerLevel level, BlockPos origin, SiteDef def, Runnable onDone) {
		Job j = new Job(level, origin, def, onDone);
		JOBS.add(j);
		return j;
	}

	/** Builds the whole site right now (smoke tests, commands). */
	public static int placeNow(ServerLevel level, BlockPos origin, SiteDef def) {
		Job j = new Job(level, origin, def, null);
		j.step(Integer.MAX_VALUE);
		return j.placed;
	}

	public static boolean busy() {
		return !JOBS.isEmpty();
	}

	public static void tick(MinecraftServer server) {
		if (JOBS.isEmpty()) {
			return;
		}
		Iterator<Job> it = JOBS.iterator();
		while (it.hasNext()) {
			Job j = it.next();
			if (j.step(PER_TICK)) {
				it.remove();
				DeadLine.LOGGER.info("Site {} placed at {} ({} blocks)", j.def.key, j.origin, j.placed);
				if (j.onDone != null) {
					j.onDone.run();
				}
			}
			break; // one job at a time keeps the per-tick cost bounded
		}
	}
}
