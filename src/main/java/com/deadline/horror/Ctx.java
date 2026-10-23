package com.deadline.horror;

import com.deadline.director.Run;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;

/** One running instance of a {@link HorrorEvent}: who it targets, how long it has run, and its scratch data. */
public final class Ctx {
	public final Run run;
	public final Haunt haunt;
	public final ServerPlayer p;
	public final HorrorEvent event;
	public final RandomSource rnd;
	public final Map<String, Object> data = new HashMap<>();
	/** Ticks since start (0 during canRun/start). */
	public int t;

	Ctx(Run run, Haunt haunt, ServerPlayer p, HorrorEvent event) {
		this.run = run;
		this.haunt = haunt;
		this.p = p;
		this.event = event;
		this.rnd = run.level.getRandom();
	}

	public ServerLevel level() {
		return run.level;
	}

	/** The room (site area) the player is in, or null outside every room. */
	public String room() {
		return HouseQuery.room(run, p);
	}

	@SuppressWarnings("unchecked")
	public <T> T get(String key) {
		return (T) data.get(key);
	}

	public Ctx put(String key, Object value) {
		data.put(key, value);
		return this;
	}

	public boolean chance(float f) {
		return rnd.nextFloat() < f;
	}

	public int between(int min, int max) {
		return min + rnd.nextInt(Math.max(1, max - min + 1));
	}
}
