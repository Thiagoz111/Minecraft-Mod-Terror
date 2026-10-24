package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.world.phys.Vec3;

/**
 * 16 picaporte (acts 2-5, intensity 3): the handle of the door of the room he is in moves by itself, from outside:
 * somebody trying to get in, quietly, then harder. If he opens it, the hall is empty.
 */
public class Picaporte extends HorrorEvent {
	private static final int[] BURSTS = {0, 30, 66};

	public Picaporte() {
		super("picaporte", Kind.POLTER);
		this.acts(2, 5).intensity(3).cooldown(170).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String door = Polter.roomDoor(c.run, c.room(), c.p.position());
		if (door == null || !Polter.isDoor(c.run, door) || c.run.doorOpen(door)) {
			return false;
		}
		Vec3 dp = HouseQuery.doorPos(c.run, door);
		double d = dp.distanceTo(c.p.position());
		if (d < 1.6 || d > 7.0) {
			return false;
		}
		c.put("door", door);
		c.put("at", dp.add(0, 0.5, 0));
		return true;
	}

	@Override
	public void start(Ctx c) {
	}

	@Override
	public boolean tick(Ctx c) {
		String door = c.get("door");
		Vec3 at = c.get("at");
		if (c.run.doorOpen(door)) {
			return true;
		}
		for (int i = 0; i < BURSTS.length; i++) {
			if (c.t == BURSTS[i]) {
				c.run.sound(ModSounds.POLTER_PICAPORTE, at, 0.8F + i * 0.25F, Polter.pitch(c, 0.9F, 1.05F) + i * 0.05F);
				Polter.noise(c.run, at, 20F + i * 10F);
				if (i == BURSTS.length - 1) {
					SanityManager.add(c.p, -3F);
				}
			}
		}
		return c.t >= 90;
	}
}
