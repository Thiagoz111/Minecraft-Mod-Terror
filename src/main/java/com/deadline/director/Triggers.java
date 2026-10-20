package com.deadline.director;

import net.minecraft.world.item.Item;

/** Trigger library for scripts. */
public final class Triggers {
	private Triggers() {
	}

	public static Trigger always() {
		return (r, p) -> true;
	}

	/** The hunter is inside an area marker. */
	public static Trigger enter(String area) {
		return (r, p) -> r.inside(p, area);
	}

	/** The hunter stayed `ticks` inside an area (counter resets when leaving). */
	public static Trigger inside(String area, int ticks) {
		return (r, p) -> {
			String k = "in:" + area + ":" + p.getUUID();
			if (r.inside(p, area)) {
				return r.inc(k) >= ticks;
			}
			r.counters.remove(k);
			return false;
		};
	}

	/** The hunter crouched for `ticks` inside an area. */
	public static Trigger crouch(String area, int ticks) {
		return (r, p) -> {
			String k = "crouch:" + area + ":" + p.getUUID();
			if (r.inside(p, area) && p.isShiftKeyDown()) {
				return r.inc(k) >= ticks;
			}
			r.counters.remove(k);
			return false;
		};
	}

	/** The hunter looks at a point (within `deg` degrees, closer than `dist`, line of sight). */
	public static Trigger lookAt(String point, float deg, double dist) {
		return (r, p) -> r.looking(p, r.at(point), deg, dist);
	}

	/** An event posted this tick (e.g. "use:tablero", "item:deadline:holy_water", "noise"). */
	public static Trigger event(String name) {
		return (r, p) -> r.event(name);
	}

	public static Trigger hasFlag(String f) {
		return (r, p) -> r.has(f);
	}

	/** `ticks` after a flag was raised. */
	public static Trigger after(String f, int ticks) {
		return (r, p) -> r.since(f) >= ticks && r.since(f) != Long.MAX_VALUE;
	}

	/** `ticks` into the current chapter. */
	public static Trigger chapterTime(int ticks) {
		return (r, p) -> r.chapterTicks() >= ticks;
	}

	public static Trigger holding(Item item) {
		return (r, p) -> p.getMainHandItem().is(item) || p.getOffhandItem().is(item);
	}

	public static Trigger objective(String id) {
		return (r, p) -> r.completed(id);
	}
}
