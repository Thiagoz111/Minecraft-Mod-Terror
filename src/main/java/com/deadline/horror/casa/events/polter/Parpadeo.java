package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.phys.Vec3;

/** 17 parpadeo (acts 1-3, intensity 1): the lights of the room he is in flicker, buzz, and come back. */
public class Parpadeo extends HorrorEvent {
	/** Ticks at which the lights go off / on (alternating, starting with off). */
	private static final int[] FLIPS = {0, 3, 6, 8, 15, 23};

	public Parpadeo() {
		super("parpadeo", Kind.POLTER);
		this.acts(1, 3).intensity(1).cooldown(70).weight(12);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String g = Polter.roomLights(c.run, c.room());
		if (g == null) {
			return false;
		}
		List<Integer> lit = new ArrayList<>();
		for (int i = 0; i < c.run.def.group(g).size(); i++) {
			if (Polter.lit(c.run, g, i)) {
				lit.add(i);
			}
		}
		if (lit.isEmpty()) {
			return false;
		}
		c.put("group", g);
		c.put("lit", lit);
		return true;
	}

	@Override
	public void start(Ctx c) {
		String g = c.get("group");
		List<Integer> lit = c.get("lit");
		Vec3 at = Vec3.atCenterOf(Polter.fixture(c.run, g, lit.get(0)));
		c.run.sound(ModSounds.POLTER_ZUMBIDO, at, 0.9F, Polter.pitch(c, 0.95F, 1.05F));
	}

	@Override
	public boolean tick(Ctx c) {
		String g = c.get("group");
		List<Integer> lit = c.get("lit");
		for (int k = 0; k < FLIPS.length; k++) {
			if (c.t == FLIPS[k]) {
				for (int i : lit) {
					c.run.light(g, i, k % 2 == 1);
				}
			}
		}
		return c.t >= FLIPS[FLIPS.length - 1];
	}

	@Override
	public void stop(Ctx c) {
		String g = c.get("group");
		List<Integer> lit = c.get("lit");
		if (g != null && lit != null) {
			for (int i : lit) {
				c.run.light(g, i, true);
			}
		}
	}
}
