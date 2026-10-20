package com.deadline.director;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * A chapter of a scripted case: title card, objective checklist, hint and checkpoint. Entering a chapter (normally or
 * from its checkpoint after a death or /deadline chapter) runs its setup steps.
 */
public final class Chapter {
	public final int n;
	public final String checkpoint;
	final List<String> objectives = new ArrayList<>();
	final List<Step> setup = new ArrayList<>();
	String hint = "";
	boolean card = true;
	int hintAfter = 20 * 180;

	Chapter(int n, String checkpoint) {
		this.n = n;
		this.checkpoint = checkpoint;
	}

	public Chapter objectives(String... ids) {
		objectives.addAll(Arrays.asList(ids));
		return this;
	}

	public Chapter hint(String key) {
		this.hint = key;
		return this;
	}

	public Chapter noCard() {
		this.card = false;
		return this;
	}

	public Chapter setup(Step... s) {
		setup.addAll(Arrays.asList(s));
		return this;
	}
}
