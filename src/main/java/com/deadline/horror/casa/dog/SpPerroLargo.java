package com.deadline.horror.casa.dog;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import java.util.List;
import net.minecraft.world.phys.Vec3;

/**
 * The long dog (docs/design/casa_terror.md 7, the end of act 5 or 6; one of the jumpscares of 6.6). With him in the
 * kitchen, the lavadero or out the back, the patio door swings open by itself and out of the doghouse comes Choripán --
 * and keeps coming, longer than any dog, never quite all of him out. It stares; then it skitters at him. If it reaches
 * him: the face (the 'perro_largo' jumpscare) and it is pulled back in. If he gets away (a shut door, a hiding place,
 * enough distance) it slides back into the doghouse.
 * <p>Scripted, once: CasaScript fires it with its conditions checked. {@link PerroLargo} posts {@code perro_largo:caught}.
 */
public class SpPerroLargo extends HorrorEvent {
	private static final double NEAR = 22.0;
	private static final int STARE = 30, CHASE = 20 * 30;
	private static final int EMERGING = 0, STARING = 1, CHASING = 2, BACK = 3;

	public SpPerroLargo() {
		super("sp_perro_largo", Kind.SETPIECE);
		this.acts(5, 6).intensity(5).cooldown(30).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		if (Apparitions.hidden(c.p) || !c.haunt.canJumpscare() || PerroLargo.active(c.run) || !Apparitions.has(c.run, "cucha")) {
			return false;
		}
		Vec3 cucha = c.run.at("cucha");
		return Math.abs(c.p.getY() - cucha.y) < 3.0 && c.p.position().distanceTo(cucha) < NEAR;
	}

	@Override
	public void start(Ctx c) {
		// the way in: the back door nearest to him opens by itself
		String door = null;
		double best = Double.MAX_VALUE;
		for (String k : List.of("puerta_patio", "lavadero_patio")) {
			Vec3 dp = HouseQuery.doorPos(c.run, k);
			if (dp != null && dp.distanceTo(c.p.position()) < best) {
				best = dp.distanceTo(c.p.position());
				door = k;
			}
		}
		if (door != null && !c.run.doorOpen(door)) {
			c.run.door(door, true, false);
		}
		PerroLargo.emerge(c.run);
		c.put("phase", EMERGING);
		c.put("at", 0);
	}

	@Override
	public boolean tick(Ctx c) {
		ChoripanDemonioEntity d = PerroLargo.get(c.run);
		if (d == null) {
			return true;  // back in the doghouse and gone (or it never came out)
		}
		if (d.caught) {
			if (c.get("scared") == null) {
				c.put("scared", true);
				c.haunt.jumpscared();
			}
			return false;  // it is pulled back in by itself
		}
		int phase = c.<Integer>get("phase");
		int since = c.t - c.<Integer>get("at");
		if (phase == EMERGING && PerroLargo.emerged(c.run)) {
			c.put("phase", STARING);
			c.put("at", c.t);
		} else if (phase == STARING && since >= STARE) {
			if (Apparitions.hidden(c.p) || !PerroLargo.chase(c.run, c.p)) {
				back(c);
			} else {
				c.put("phase", CHASING);
				c.put("at", c.t);
			}
		} else if (phase == CHASING && (Apparitions.hidden(c.p) || since > CHASE)) {
			back(c);
		}
		return false;
	}

	private static void back(Ctx c) {
		PerroLargo.retract(c.run);
		c.put("phase", BACK);
	}

	@Override
	public void stop(Ctx c) {
		ChoripanDemonioEntity d = PerroLargo.get(c.run);
		if (d != null && d.state() != ChoripanDemonioEntity.STATE_RETRACT) {
			PerroLargo.retract(c.run);
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 75;
	}
}
