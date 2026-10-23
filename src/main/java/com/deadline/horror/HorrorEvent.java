package com.deadline.horror;

/**
 * One thing the house can do to the player (a sound, a door, a figure at the end of the hall, blood on a wall...).
 * The {@link Haunt} picks events at random by act, tension, cooldown and place; set pieces fire them by id.
 * Subclasses configure themselves in the constructor with the fluent setters and implement {@link #start}.
 */
public abstract class HorrorEvent {
	public enum Kind {
		SOUND, POLTER, APPARITION, BLOOD, PHONE, SCARE, SETPIECE
	}

	public final String id;
	public final Kind kind;
	int minAct = 1;
	int maxAct = 6;
	int intensity = 1;
	int cooldown = 60;
	int weight = 10;
	boolean once;
	boolean random = true;

	protected HorrorEvent(String id, Kind kind) {
		this.id = id;
		this.kind = kind;
	}

	/** Acts (inclusive) in which the director may pick it. */
	public HorrorEvent acts(int min, int max) {
		this.minAct = min;
		this.maxAct = max;
		return this;
	}

	/** 1 (a creak) .. 5 (a jumpscare). Raises the tension by that much and decides when it may appear. */
	public HorrorEvent intensity(int n) {
		this.intensity = Math.max(1, Math.min(5, n));
		return this;
	}

	/** Seconds before the director may pick it again. */
	public HorrorEvent cooldown(int seconds) {
		this.cooldown = seconds;
		return this;
	}

	public HorrorEvent weight(int w) {
		this.weight = Math.max(1, w);
		return this;
	}

	/** Happens at most once per case. */
	public HorrorEvent once() {
		this.once = true;
		return this;
	}

	/** Never picked at random: only set pieces / commands fire it with {@link Haunt#fire}. */
	public HorrorEvent scripted() {
		this.random = false;
		return this;
	}

	public int minAct() {
		return minAct;
	}

	public int maxAct() {
		return maxAct;
	}

	public int intensity() {
		return intensity;
	}

	public int cooldown() {
		return cooldown;
	}

	public int weight() {
		return weight;
	}

	public boolean isOnce() {
		return once;
	}

	public boolean isRandom() {
		return random;
	}

	/** Extra conditions (room of the player, darkness, a free spot behind him...). Store what you found in c.data. */
	public boolean canRun(Ctx c) {
		return true;
	}

	public abstract void start(Ctx c);

	/** Called every tick after start; return true when finished. Default: instant event. */
	public boolean tick(Ctx c) {
		return true;
	}

	/** Always called exactly once when the event ends or is aborted: put the world back, despawn actors. */
	public void stop(Ctx c) {
	}

	/** Safety net: the event is aborted after this many ticks. */
	public int maxTicks() {
		return 20 * 90;
	}
}
