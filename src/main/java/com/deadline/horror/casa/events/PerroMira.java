package com.deadline.horror.casa.events;

import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.dog.ChoripanEntity;
import com.deadline.horror.casa.dog.DogEntities;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.world.phys.Vec3;

/**
 * 36 perro_mira (acts 1-6, intensity 2 -> 4; the motif of Act 3): Choripán standing on his hind legs like a person,
 * dead-eyed, staring at the house. Every time he has been SEEN and then LOST from view he comes one stage closer:
 * perro_mira_1 (the back of the patio) -> _2 (outside the living-room window) -> _3 (the end of the ground-floor hall)
 * -> _4 (the foot of the guest bed: your bed). The stage lives per run here (it survives chapter replays), so every
 * firing continues where the last one left. After stage 4 it does not fire again ({@link #reset} starts it over).
 */
public class PerroMira extends HorrorEvent {
	public static final int STAGES = 4;
	private static final Map<Run, int[]> STAGE = new WeakHashMap<>();

	public PerroMira() {
		super("perro_mira", Kind.APPARITION);
		this.acts(1, 6).intensity(2).cooldown(70).weight(12);
	}

	/** Next stage to show (1..4), or 5 when the dog has reached the bed. */
	public static int stage(Run r) {
		return STAGE.computeIfAbsent(r, k -> new int[] {1})[0];
	}

	public static void reset(Run r) {
		STAGE.computeIfAbsent(r, k -> new int[] {1})[0] = 1;
	}

	private static int intensityFor(int stage) {
		return stage >= 4 ? 4 : stage == 3 ? 3 : 2;
	}

	@Override
	public boolean canRun(Ctx c) {
		int s = stage(c.run);
		if (s > STAGES || Apparitions.hidden(c.p)) {
			return false;
		}
		this.intensity(intensityFor(s));
		Vec3 v = Apparitions.at(c.run, "perro_mira_" + s);
		if (v == null) {
			return false;
		}
		double d = Apparitions.dist(c, v);
		// he is put there unseen; far stages are watched from the house, the last ones from close by
		double max = s <= 2 ? 48.0 : 22.0;
		return d > 4.0 && d < max && !Apparitions.sees(c, v.add(0, 0.6, 0), 75F);
	}

	@Override
	public void start(Ctx c) {
		int s = stage(c.run);
		this.intensity(intensityFor(s));  // read by the haunt right after start (tension, peak)
		Vec3 v = c.run.at("perro_mira_" + s);
		float yaw = Apparitions.yawTo(v, c.p.position());
		ChoripanEntity dog = Apparitions.spawn(c, DogEntities.CHORIPAN, v, yaw);
		if (dog != null) {
			dog.setVariant(ChoripanEntity.LOOK_MUERTO);
			dog.pose(ChoripanEntity.POSE_STAND);
		}
		c.put("e", dog);
		c.put("s", s);
	}

	@Override
	public boolean tick(Ctx c) {
		ChoripanEntity dog = c.get("e");
		int s = c.<Integer>get("s");
		if (Apparitions.gone(dog)) {
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.sees(c, dog, 40F));
		if (!was && g.ever) {
			if (s >= 2) {
				Apparitions.sound(c, ModSounds.APARICION_PERRO_RESPIRA, dog.position().add(0, 0.8, 0), s >= 3 ? 0.9F : 0.6F, 0.92F);
			}
			if (s >= STAGES) {
				// at the foot of your bed: the growl you heard him give the Nona, too low, too slow
				Apparitions.sound(c, ModSounds.CHORIPAN_GROWL_LOW, dog.position(), 1.2F, 0.62F);
				Fx.shake(c.p, 0.25F, 20);
			}
		}
		boolean close = Apparitions.dist(c, dog.position()) < (s >= STAGES ? 1.8 : 3.0);
		if (g.lookedAway(10) || (g.ever && close)) {
			advance(c.run, s);
			Apparitions.vanish(dog, false);
			return true;
		}
		// never seen in a minute: he leaves without coming closer
		return !g.ever && c.t > 20 * 60;
	}

	private void advance(Run r, int s) {
		int[] st = STAGE.computeIfAbsent(r, k -> new int[] {1});
		st[0] = Math.max(st[0], s + 1);
		this.intensity(intensityFor(Math.min(STAGES, st[0])));
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 70;
	}
}
