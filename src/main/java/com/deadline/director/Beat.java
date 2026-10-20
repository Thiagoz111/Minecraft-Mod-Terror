package com.deadline.director;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** A scripted event: when its trigger matches (in its chapter, with its flags), its steps run. */
public final class Beat {
	public final String id;
	int chapter = -1;
	int fromChapter = -1;
	Trigger trigger = (r, p) -> false;
	final List<String> requires = new ArrayList<>();
	final List<String> unless = new ArrayList<>();
	boolean once = true;
	int cooldown;
	final List<Step> steps = new ArrayList<>();

	Beat(String id) {
		this.id = id;
	}

	/** Only during this chapter. */
	public Beat chapter(int n) {
		this.chapter = n;
		return this;
	}

	/** From this chapter on. */
	public Beat from(int n) {
		this.fromChapter = n;
		return this;
	}

	public Beat when(Trigger t) {
		this.trigger = t;
		return this;
	}

	public Beat requires(String... flags) {
		requires.addAll(Arrays.asList(flags));
		return this;
	}

	public Beat unless(String... flags) {
		unless.addAll(Arrays.asList(flags));
		return this;
	}

	/** Can fire again after `ticks` once its previous run is over. */
	public Beat repeat(int ticks) {
		this.once = false;
		this.cooldown = ticks;
		return this;
	}

	public Beat then(Step... s) {
		steps.addAll(Arrays.asList(s));
		return this;
	}
}
