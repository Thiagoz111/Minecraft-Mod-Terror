package com.deadline.director;

/** One instruction of a beat or chapter setup. Called once per tick until it reports completion. */
@FunctionalInterface
public interface Step {
	/** @return true when finished; the sequence then moves on (in the same tick) to the next step. */
	boolean tick(Exec e);
}
