package com.deadline.director;

import net.minecraft.server.level.ServerPlayer;

/** Condition that fires a beat for a hunter. Polled every tick while the beat is eligible. */
@FunctionalInterface
public interface Trigger {
	boolean test(Run run, ServerPlayer player);

	default Trigger and(Trigger other) {
		return (r, p) -> test(r, p) && other.test(r, p);
	}

	default Trigger or(Trigger other) {
		return (r, p) -> test(r, p) || other.test(r, p);
	}
}
