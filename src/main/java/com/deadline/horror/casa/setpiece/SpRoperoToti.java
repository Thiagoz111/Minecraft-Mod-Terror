package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.SetPieces;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.phys.Vec3;

/**
 * Act 4 (design 2, "los golpes del ropero de Toti" -- El Conjuro): three knocks from INSIDE Toti's wardrobe. Again,
 * a little later. If he knocks on it (a left click on the wardrobe or the wall beside it), it answers: the same number
 * of knocks, from inside. Twice. Then silence -- and the doors burst open: Toti crouched in there, looking up at him with
 * a smile far too wide (the copy). The doors slam shut by themselves. Open them: empty clothes. If he opens it himself
 * before that, it is empty and the knocks come from under Toti's bed instead.
 */
public class SpRoperoToti extends HorrorEvent {
	private static final String HIDE = "hide_ropero_toti", OUT = "hide_ropero_toti_out";
	private static final int KNOCKING = 0, CLIMAX = 1, EMPTY = 2;
	/** Ticks with no new knock before his knocking counts as finished (then the wardrobe answers). */
	private static final int QUIET = 16;

	public SpRoperoToti() {
		super("sp_ropero_toti", Kind.SETPIECE);
		this.acts(4, 6).intensity(4).cooldown(300).scripted().once();
	}

	private List<String> doors(Ctx c) {
		List<String> out = new ArrayList<>();
		for (String d : List.of("ropero_toti", "ropero_toti_2")) {
			if (c.run.def.doors.containsKey(d)) {
				out.add(d);
			}
		}
		return out;
	}

	@Override
	public boolean canRun(Ctx c) {
		Vec3 hide = Apparitions.at(c.run, HIDE);
		if (hide == null || !Apparitions.has(c.run, OUT) || doors(c).isEmpty() || !Apparitions.canScare(c)) {
			return false;
		}
		double d = Apparitions.dist(c, hide);
		return d < 10.0 && Math.abs(c.p.getY() - hide.y) < 2.5 && !closedDoorsOpen(c);
	}

	private boolean closedDoorsOpen(Ctx c) {
		for (String d : doors(c)) {
			if (c.run.doorOpen(d)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		c.put("phase", KNOCKING);
		c.put("nextKnock", 10);
		c.put("since", c.run.now());
		c.put("heard", 0);
		c.put("lastHeard", -1);
		c.put("answers", 0);
		c.put("answerAt", -1);
		c.put("answerN", 0);
		c.put("close", 0);
	}

	@Override
	public boolean tick(Ctx c) {
		if (Apparitions.hidden(c.p)) {
			return true;  // he got in somewhere (maybe in there): the knocking stops dead
		}
		int phase = c.get("phase");
		return switch (phase) {
			case KNOCKING -> knocking(c);
			case CLIMAX -> climax(c, c.t - c.<Integer>get("phaseAt"));
			default -> empty(c, c.t - c.<Integer>get("phaseAt"));
		};
	}

	private Vec3 inside(Ctx c) {
		return c.run.at(HIDE).add(0, 1.0, 0);
	}

	private boolean knocking(Ctx c) {
		Vec3 in = inside(c);
		if (closedDoorsOpen(c)) {
			next(c, EMPTY);  // he opened it himself: nothing in there
			return false;
		}
		// the wardrobe knocks on its own, now and then, until he answers
		int nextKnock = c.get("nextKnock");
		if (c.t == nextKnock && c.<Integer>get("answers") == 0) {
			c.put("answerAt", c.t);
			c.put("answerN", 3);
			c.put("nextKnock", c.t + 20 * 7 + c.rnd.nextInt(60));
		}
		// his knocks on the wardrobe (or the wall right by it)
		long since = c.get("since");
		List<SetPieces.Knock> ks = SetPieces.knocks(c.p, in, 2.6, since);
		if (!ks.isEmpty()) {
			for (SetPieces.Knock k : ks) {
				c.run.sound(ModSounds.HORROR_KNOCK, Vec3.atCenterOf(k.pos()), 0.8F, 1.0F);  // his own knock, wood
			}
			c.put("since", ks.get(ks.size() - 1).at());
			c.put("heard", Math.min(6, c.<Integer>get("heard") + ks.size()));
			c.put("lastHeard", c.t);
		}
		int heard = c.get("heard");
		int last = c.get("lastHeard");
		if (heard > 0 && c.t - last == QUIET) {
			// it answers: as many knocks as he gave
			c.put("answerAt", c.t + 10);
			c.put("answerN", heard);
			c.put("heard", 0);
			c.put("answers", c.<Integer>get("answers") + 1);
		}
		int at = c.get("answerAt");
		int n = c.get("answerN");
		if (at >= 0 && c.t >= at && (c.t - at) % 8 == 0) {
			int k = (c.t - at) / 8;
			if (k < n) {
				c.run.sound(ModSounds.HORROR_KNOCK, in, 0.75F, 0.78F + 0.02F * k);
			} else {
				c.put("answerAt", -1);
			}
		}
		// he stands right in front of it, waiting: it does not need him to knock
		Vec3 out = c.run.at(OUT);
		int close = c.p.position().distanceTo(out) < 2.2 ? c.<Integer>get("close") + 1 : 0;
		c.put("close", close);
		boolean ready = c.<Integer>get("answers") >= 2 && c.<Integer>get("answerAt") < 0 && c.t - last > 30;
		if (ready || close > 20 * 6 || c.t > 20 * 50 && Apparitions.dist(c, in) < 5.0) {
			next(c, CLIMAX);
		}
		return c.t > 20 * 70;
	}

	/** Silence. The doors fly open: the copy of Toti crouched inside, grinning up at him. The doors slam. */
	private boolean climax(Ctx c, int k) {
		Vec3 in = inside(c);
		if (k == 0) {
			FamilyEntity t = Apparitions.spawn(c, FamilyEntities.TOTI, c.run.at(HIDE), c.run.yaw(HIDE));
			if (t != null) {
				t.setVariant(FamilyEntity.LOOK_COPIA);
				t.setAction(FamilyEntity.POSE_CROUCH_CLOSET);
				t.watch(c.p);
			}
			c.put("e", t);
		}
		if (k == 32) {
			if (closedDoorsOpen(c) && c.get("e") instanceof FamilyEntity t && Apparitions.watches(c, t, 70F)) {
				// he opened it in the silence and is looking right in: the face is the first thing he sees
				c.run.sound(ModSounds.APARICION_COPIA, t.getEyePosition(), 1.2F, 0.9F);
			}
			for (String d : doors(c)) {
				c.run.door(d, true, false);
			}
			c.run.sound(ModSounds.DOOR_SLAM, in, 1.3F, 0.65F);
			c.run.sound(ModSounds.APARICION_COPIA, in, 1.0F, 0.95F);
			Fx.shake(c.p, 0.6F, 10);
			Apparitions.noise(c, in, 70F);
		}
		if (k == 58) {
			for (String d : doors(c)) {
				c.run.door(d, false, true);
			}
			Apparitions.noise(c, in, 70F);
		}
		if (k == 60) {
			Apparitions.despawnAll(c);
		}
		return k > 80;
	}

	/** He opened it first: empty. Then three knocks from under Toti's bed. */
	private boolean empty(Ctx c, int k) {
		Vec3 bed = Apparitions.at(c.run, "hide_cama_toti");
		if (bed == null) {
			bed = Apparitions.at(c.run, "toti_cama");
		}
		if (bed != null && k >= 40 && k <= 56 && (k - 40) % 8 == 0) {
			c.run.sound(ModSounds.HORROR_KNOCK, bed.add(0, 0.2, 0), 0.8F, 0.7F);
		}
		return k > 70 || bed == null;
	}

	private static void next(Ctx c, int phase) {
		c.put("phase", phase);
		c.put("phaseAt", c.t);
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		if (c.<Integer>get("phase") != null && c.<Integer>get("phase") == CLIMAX) {
			for (String d : doors(c)) {
				c.run.door(d, false, false);  // the wardrobe as it was: closed
			}
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 90;
	}
}
