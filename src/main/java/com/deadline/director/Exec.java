package com.deadline.director;

import com.deadline.DeadLine;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;

/** A running sequence of steps (one beat firing, a chapter setup, a forked branch). */
public final class Exec {
	public final Run run;
	/** The hunter the sequence was started for (may be null for site-wide sequences). */
	public final ServerPlayer player;
	final String label;
	private final List<Step> steps;
	private int index;
	/** Ticks spent in the current step (reset when the sequence advances). */
	public int t;
	/** Scratch value for stateful steps (reset with t). */
	public int n;
	public Object data;
	boolean done;

	Exec(Run run, ServerPlayer player, String label, List<Step> steps) {
		this.run = run;
		this.player = player;
		this.label = label;
		this.steps = steps;
	}

	void tick() {
		int guard = 0;
		while (!done) {
			if (index >= steps.size()) {
				done = true;
				return;
			}
			boolean finished;
			try {
				finished = steps.get(index).tick(this);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Director step {}#{} failed", label, index, ex);
				finished = true;
			}
			if (finished) {
				index++;
				t = 0;
				n = 0;
				data = null;
				if (++guard > 256) {
					return;
				}
				continue;
			}
			t++;
			return;
		}
	}

	public void cancel() {
		done = true;
	}

	public ServerPlayer target() {
		return player != null && !player.isRemoved() ? player : run.star();
	}
}
