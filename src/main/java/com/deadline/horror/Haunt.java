package com.deadline.horror;

import com.deadline.DeadLine;
import com.deadline.director.Run;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;
import net.minecraft.server.level.ServerPlayer;

/**
 * The horror director of one case run (an "AI director" for scares). Tension rises with time and with every event;
 * a big scare (intensity 4+) is a PEAK, after which the house goes quiet for 40-90 s (RELAX) before building again.
 * Every few seconds (faster in later acts and at high tension) it picks an eligible random event, weighted towards
 * events not seen yet and events that match the current tension. Set pieces call {@link #fire} directly.
 *
 * <p>The case script owns the act number ({@link #act(int)}) and calls {@link #tick()} every tick.
 */
public final class Haunt {
	public enum Phase {
		BUILD, PEAK, RELAX
	}

	/** Haunts live beside their run (run vars are reset per chapter, so they are not kept there). */
	private static final Map<Run, Haunt> HAUNTS = new WeakHashMap<>();
	private static final int RECENT = 6;
	/** Events that threw (start, tick, stop or canRun) since the server started; the CI smoke test fails on any. */
	public static int errors;

	public final Run run;
	private int act;
	private long actStart;
	private final long started;
	private float tension;
	private Phase phase = Phase.BUILD;
	private long phaseUntil;
	private long nextAt;
	private long lastJumpscare = -1_000_000L;
	private int bigScares;
	private boolean paused;
	private Ctx peak;
	private String last = "";
	private final Map<String, Long> lastRun = new HashMap<>();
	private final Map<String, Integer> times = new HashMap<>();
	private final Set<String> done = new HashSet<>();
	private final Deque<String> recent = new ArrayDeque<>();
	private final List<Ctx> running = new ArrayList<>();
	private final List<Ctx> incoming = new ArrayList<>();

	private Haunt(Run run) {
		this.run = run;
		this.started = run.now();
		this.actStart = started;
		this.nextAt = started + 20 * 20;
	}

	public static Haunt of(Run run) {
		return HAUNTS.computeIfAbsent(run, Haunt::new);
	}

	/** The haunt of a run if it exists, without creating one. */
	public static Haunt peek(Run run) {
		return run == null ? null : HAUNTS.get(run);
	}

	public static void forget(Run run) {
		Haunt h = HAUNTS.remove(run);
		if (h != null) {
			h.stopAll();
		}
	}

	// ------------------------------------------------------------------ state
	public int act() {
		return act;
	}

	/** Enter an act: resets the act clock and gives the new act a short breath before its first random event. */
	public void act(int n) {
		act = n;
		actStart = run.now();
		nextAt = Math.max(nextAt, actStart + 20 * 8);
	}

	public long actTicks() {
		return run.now() - actStart;
	}

	public long caseTicks() {
		return run.now() - started;
	}

	public float tension() {
		return tension;
	}

	public void tension(float v) {
		tension = Math.max(0F, Math.min(100F, v));
	}

	public void addTension(float v) {
		tension(tension + v);
	}

	public Phase phase() {
		return phase;
	}

	/** Big scares (intensity 4+) lived in this case; acts use it to advance. */
	public int bigScares() {
		return bigScares;
	}

	public int times(String id) {
		return times.getOrDefault(id, 0);
	}

	public boolean happened(String id) {
		return times.containsKey(id);
	}

	public void pause(boolean p) {
		paused = p;
	}

	public boolean paused() {
		return paused;
	}

	/** Forces a quiet window: no random events but whispers-level ones until it ends. */
	public void relax(int ticks) {
		phase = Phase.RELAX;
		phaseUntil = run.now() + ticks;
		nextAt = Math.max(nextAt, run.now() + 20 * 6);
	}

	/** Jumpscares: at most one every 3 minutes and never in the first 4 minutes of the case. */
	public boolean canJumpscare() {
		long now = run.now();
		return now - lastJumpscare > 20 * 180 && now - started > 20 * 240;
	}

	public void jumpscared() {
		lastJumpscare = run.now();
	}

	public boolean isRunning(String id) {
		for (Ctx c : running) {
			if (c.event.id.equals(id)) {
				return true;
			}
		}
		for (Ctx c : incoming) {
			if (c.event.id.equals(id)) {
				return true;
			}
		}
		return false;
	}

	/** Something heavy is going on (a set piece, a big scare or the peak): random events wait. */
	public boolean busy() {
		if (phase == Phase.PEAK) {
			return true;
		}
		for (Ctx c : running) {
			if (c.event.intensity >= 3 || c.event.kind == HorrorEvent.Kind.SETPIECE) {
				return true;
			}
		}
		return !incoming.isEmpty();
	}

	public String status() {
		return String.format("act %d (%ds) tension %.0f %s big %d next %ds last %s running %s", act, actTicks() / 20, tension,
				phase, bigScares, Math.max(0, (nextAt - run.now()) / 20), last, running.stream().map(c -> c.event.id).toList());
	}

	// ------------------------------------------------------------------ tick
	public void tick() {
		long now = run.now();
		for (Iterator<Ctx> it = running.iterator(); it.hasNext();) {
			Ctx c = it.next();
			boolean end;
			if (c.p.isRemoved() || !c.p.isAlive()) {
				end = true;
			} else {
				c.t++;
				end = safeTick(c) || c.t >= c.event.maxTicks();
			}
			if (end) {
				it.remove();
				finish(c);
			}
		}
		running.addAll(incoming);
		incoming.clear();

		ServerPlayer p = run.star();
		if (paused || p == null) {
			return;
		}
		switch (phase) {
			case RELAX -> {
				tension = Math.max(0F, tension - 0.05F);
				if (now >= phaseUntil) {
					phase = Phase.BUILD;
				}
			}
			case BUILD -> tension = Math.min(100F, tension + 0.004F * (1 + act));
			case PEAK -> {
			}
		}
		if (now < nextAt || busy()) {
			return;
		}
		nextAt = now + interval();
		Ctx c = pick(p, now);
		if (c != null) {
			begin(c);
		}
	}

	/** Seconds between random events: long and sparse early, short and relentless in the hunt and the descent. */
	private long interval() {
		int[][] table = {{30, 50}, {30, 50}, {26, 45}, {18, 34}, {12, 24}, {8, 16}, {6, 12}};
		int[] r = table[Math.max(0, Math.min(6, act))];
		var rnd = run.level.getRandom();
		float s = r[0] + rnd.nextFloat() * (r[1] - r[0]);
		s *= 1F - tension / 250F;
		if (phase == Phase.RELAX) {
			s = Math.max(s, 15F);
		}
		return (long) (s * 20);
	}

	private Ctx pick(ServerPlayer p, long now) {
		int cap = phase == Phase.RELAX ? 1 : tension < 25 ? 2 : tension < 50 ? 3 : tension < 75 ? 4 : 5;
		List<Ctx> pool = new ArrayList<>();
		List<Integer> weights = new ArrayList<>();
		int total = 0;
		for (HorrorEvent e : HorrorEvents.of(run.type.key())) {
			if (!e.random || act < e.minAct || act > e.maxAct || e.intensity > cap || recent.contains(e.id)) {
				continue;
			}
			if (e.once && done.contains(e.id)) {
				continue;
			}
			Long lr = lastRun.get(e.id);
			if (lr != null && now - lr < e.cooldown * 20L) {
				continue;
			}
			if (e.kind == HorrorEvent.Kind.SCARE && !canJumpscare()) {
				continue;
			}
			Ctx c = new Ctx(run, this, p, e);
			if (!safeCanRun(c)) {
				continue;
			}
			int w = e.weight * (lr == null ? 3 : 1) * (e.intensity == cap ? 2 : 1);
			pool.add(c);
			weights.add(w);
			total += w;
		}
		if (pool.isEmpty()) {
			return null;
		}
		int roll = run.level.getRandom().nextInt(total);
		for (int i = 0; i < pool.size(); i++) {
			roll -= weights.get(i);
			if (roll < 0) {
				return pool.get(i);
			}
		}
		return pool.get(pool.size() - 1);
	}

	// ------------------------------------------------------------------ firing
	/** Fires an event of this case by id for the star (or the given player). checkConditions runs canRun first. */
	public Ctx fire(String id, ServerPlayer target, boolean checkConditions) {
		HorrorEvent e = HorrorEvents.get(run.type.key(), id);
		ServerPlayer p = target != null ? target : run.star();
		if (e == null || p == null) {
			if (e == null) {
				DeadLine.LOGGER.warn("Unknown horror event {}:{}", run.type.key(), id);
			}
			return null;
		}
		Ctx c = new Ctx(run, this, p, e);
		if (checkConditions && !safeCanRun(c)) {
			return null;
		}
		return begin(c) ? c : null;
	}

	public Ctx fire(String id) {
		return fire(id, null, false);
	}

	private boolean begin(Ctx c) {
		HorrorEvent e = c.event;
		try {
			e.start(c);
		} catch (RuntimeException ex) {
			errors++;
			DeadLine.LOGGER.error("Horror event {} failed to start", e.id, ex);
			return false;
		}
		incoming.add(c);
		long now = run.now();
		lastRun.put(e.id, now);
		times.merge(e.id, 1, Integer::sum);
		last = e.id;
		if (e.once) {
			done.add(e.id);
		}
		recent.addFirst(e.id);
		while (recent.size() > RECENT) {
			recent.removeLast();
		}
		addTension(e.intensity * 5F);
		if (e.kind == HorrorEvent.Kind.SCARE) {
			jumpscared();
		}
		if (e.intensity >= 4) {
			bigScares++;
			phase = Phase.PEAK;
			peak = c;
		}
		return true;
	}

	private void finish(Ctx c) {
		try {
			c.event.stop(c);
		} catch (RuntimeException ex) {
			errors++;
			DeadLine.LOGGER.error("Horror event {} failed to stop", c.event.id, ex);
		}
		if (c == peak) {
			peak = null;
			relax(20 * (40 + run.level.getRandom().nextInt(51)));
		}
	}

	/** Aborts every running event (leaving the case, checkpoints): each one restores the world in stop(). */
	public void stopAll() {
		List<Ctx> all = new ArrayList<>(running);
		all.addAll(incoming);
		running.clear();
		incoming.clear();
		for (Ctx c : all) {
			finish(c);
		}
		if (phase == Phase.PEAK) {
			phase = Phase.BUILD;
		}
	}

	private boolean safeTick(Ctx c) {
		try {
			return c.event.tick(c);
		} catch (RuntimeException ex) {
			errors++;
			DeadLine.LOGGER.error("Horror event {} crashed", c.event.id, ex);
			return true;
		}
	}

	private boolean safeCanRun(Ctx c) {
		try {
			return c.event.canRun(c);
		} catch (RuntimeException ex) {
			errors++;
			DeadLine.LOGGER.error("Horror event {} canRun crashed", c.event.id, ex);
			return false;
		}
	}
}
