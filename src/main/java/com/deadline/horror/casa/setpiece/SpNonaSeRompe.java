package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.hunt.Hunt;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * Act 5 begins (design 2, "La Nona se rompe"): in the dark house one light comes on -- the kitchen -- and the kettle
 * starts to scream on the stove. The Nona stands at the counter with her back to the room, humming, her loose white hair
 * on her shoulders. When he finds her (sees her from the doorway, or comes close) she breaks: the bones crack, the neck
 * turns all the way round, the jaw drops, she stretches up to the ceiling and comes down on all fours
 * ({@link Hunt#transform}); then the hunt begins. If he never comes, it happens anyway, out of his sight, and he hears it.
 * The kitchen bulb bursts on her scream.
 */
public class SpNonaSeRompe extends HorrorEvent {
	private static final int LURE = 0, BREAK = 1;
	private static final int UNSEEN_LIMIT = 20 * 75;
	/** No new transformation starts after this: the BREAK (~131 ticks) always fits before {@link #maxTicks}. */
	private static final int LURE_LIMIT = UNSEEN_LIMIT + 20 * 30;
	private static final int BREAK_TICKS = 140;

	public SpNonaSeRompe() {
		super("sp_nona_se_rompe", Kind.SETPIECE);
		this.acts(5, 5).intensity(5).cooldown(600).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		return (Apparitions.has(c.run, "mesada") || Apparitions.has(c.run, "cocina")) && !Hunt.active(c.run);
	}

	@Override
	public void start(Ctx c) {
		if (!Apparitions.has(c.run, "mesada") && !Apparitions.has(c.run, "cocina")) {
			// fired without its conditions on a site with no kitchen: nothing to stage (the act script's hunt starts her)
			c.put("phase", LURE);
			c.put("abort", true);
			return;
		}
		String m = Apparitions.has(c.run, "mesada") ? "mesada" : "cocina";
		Vec3 at = Stage.stand(c.run, c.run.at(m));
		if (at == null) {
			at = c.run.at(m);
		}
		// her back to the room: she faces the counter (the mesada marker looks at it)
		float yaw = m.equals("mesada") ? c.run.yaw(m) : c.run.yaw(m) + 180F;
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, at, yaw);
		if (n != null) {
			n.setVariant(FamilyEntity.LOOK_POSSESSED);
			n.setAction(FamilyEntity.POSE_STAND_WALKER);
			n.propSounds = false;
			n.watchPlayers(false);
			n.lookAt(at.add(Stage.forward(yaw).scale(0.8)).add(0, 0.9, 0));
		}
		c.put("e", n);
		c.put("phase", LURE);
		c.put("stove", at.add(Stage.forward(yaw).scale(0.9)).add(Stage.right(yaw).scale(1.5)).add(0, 1.0, 0));
		if (c.run.def.groups.containsKey("luces_cocina")) {
			c.run.lights("luces_cocina", true);
		}
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.get("abort") != null) {
			return true;
		}
		int phase = c.get("phase");
		if (phase == BREAK) {
			int k = c.t - c.<Integer>get("breakAt");
			if (k == 122 && c.run.def.groups.containsKey("luces_cocina")) {
				// her scream (NonaRotaEntity, t 122): the kitchen bulb bursts
				c.run.sound(ModSounds.BULB_POP, c.get("stove"), 1.4F, 0.85F);
				c.run.lights("luces_cocina", false);
			}
			if (k > 130) {
				c.put("done", true);
				return true;
			}
			return false;
		}
		FamilyEntity n = c.get("e");
		if (Hunt.active(c.run) || Apparitions.gone(n)) {
			c.put("done", true);
			return true;  // the hunt started some other way
		}
		Vec3 stove = c.get("stove");
		if (c.t < 20 * 40 && c.t % (20 * 8) == 10) {
			c.run.sound(ModSounds.KETTLE_WHISTLE, stove, 1.3F, 0.95F);  // the kettle screaming in the dark house
		}
		if (c.t % 80 == 40) {
			Apparitions.sound(c, ModSounds.MONJA_WHISPER, n.getEyePosition(), 0.6F, 0.62F);  // she hums, low, backwards
		}
		boolean hidden = Apparitions.hidden(c.p);
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(!hidden && Apparitions.dist(c, n.position()) < 16.0 && Apparitions.watches(c, n, 50F));
		boolean found = g.seen >= 15 || !hidden && Apparitions.dist(c, n.position()) < 6.0;
		if (c.t >= LURE_LIMIT) {
			return true;  // he stayed hidden all along: the act script lets her out (Hunt.start) without the scene
		}
		if (found || c.t > UNSEEN_LIMIT && !hidden) {
			Vec3 pos = n.position();
			float yaw = n.getYRot();
			Apparitions.despawnAll(c);
			Hunt.transform(c.run, pos, yaw);
			c.put("phase", BREAK);
			c.put("breakAt", c.t);
		}
		return false;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		if (c.get("done") != null) {
			return;
		}
		// aborted (a replay of the act, the case ending, he dropped out): the kitchen dark again. A transformation already
		// under way is left to finish -- she is the hunter of the act; the act script stops her when the act changes
		if (c.run.def.groups.containsKey("luces_cocina")) {
			c.run.lights("luces_cocina", false);
		}
	}

	@Override
	public int maxTicks() {
		return LURE_LIMIT + BREAK_TICKS;
	}
}
