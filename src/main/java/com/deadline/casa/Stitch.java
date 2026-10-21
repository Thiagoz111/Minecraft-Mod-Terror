package com.deadline.casa;

import com.deadline.casa.CasaNet.StitchPayload;
import com.deadline.director.Exec;
import com.deadline.director.Run;
import com.deadline.director.Step;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.List;
import java.util.function.Function;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * The three stitches on Ofelia's mouth (BIBLIA 2.2 m): keep your aim on her mouth for {@link #HOLD_TICKS} while a
 * ring closes around the crosshair (the server checks the angle like {@link Run#looking}). Let go halfway and the
 * stitch slips: a jolt, -10 sanity and the needle pulled back out. Events: "stitch:hold", "stitch:&lt;n&gt;:hold"
 * (a hold starts), "stitch:&lt;n&gt;" (done), "stitch:fail", "stitch:&lt;n&gt;:fail".
 */
public final class Stitch {
	public static final int TOTAL = 3;
	public static final int HOLD_TICKS = 40;
	/** The default actor whose mouth is sewn. */
	public static final String ACTOR = "ofelia";
	public static final double MAX_DIST = 6.0;
	/** Hunters farther than this from the mouth do not see the ring. */
	private static final double SHOW_DIST = 14.0;
	/** Ticks off the mouth before a hold counts as released (aim jitter, the screen shake). */
	private static final int GRACE = 5;
	/** A hold shorter than this is a glance, not a stitch: letting go just resets it. */
	private static final int MIN_FAIL = 8;
	/** Ticks after a slip before a new hold can start. */
	private static final int RECOVER = 24;
	private static final String SNAP_AT = "stitch:snapAt", SNAP = "stitch:snap";

	private Stitch() {
	}

	/** The hold of one stitch (lives in the {@link Exec} while the step runs). */
	private static final class Hold {
		int progress;
		int off;
		int recover;
		long seenSnap;
		ServerPlayer by;
	}

	/** Stitch n on the mouth of the "ofelia" actor; no thread and needle needed. */
	public static Step step(int n) {
		return step(n, ACTOR, false);
	}

	/** Stitch n on the mouth of a run actor; needKit: the hunter must carry the blessed thread and the needle. */
	public static Step step(int n, String actor, boolean needKit) {
		return step(n, e -> {
			Entity a = e.run.actor(actor);
			return a == null ? null : mouth(a);
		}, needKit);
	}

	/** Stitch n on any point (null while there is nothing to sew: the step waits and hides the ring). */
	public static Step step(int n, Function<Exec, Vec3> target, boolean needKit) {
		return e -> {
			Run r = e.run;
			Hold h;
			if (e.data instanceof Hold x) {
				h = x;
			} else {
				h = new Hold();
				h.seenSnap = r.now();
				e.data = h;
			}
			Vec3 m = target.apply(e);
			List<ServerPlayer> hunters = r.hunters();
			if (m == null) {
				if (e.t % 10 == 0) {
					hunters.forEach(p -> CasaNet.stitchRing(p, -1F));
				}
				return false;
			}
			// a scripted slip (the yarn hooks your arm): Stitch.snap from the script
			if (r.vars.get(SNAP) instanceof Long t && t > h.seenSnap) {
				h.seenSnap = t;
				h.progress = 0;
				h.off = 0;
				h.recover = RECOVER;
			}
			if (h.recover > 0) {
				h.recover--;
			}
			ServerPlayer aiming = null;
			boolean anyKit = !needKit;
			for (ServerPlayer p : hunters) {
				boolean kit = !needKit || CasaItems.hasSewingKit(p);
				anyKit |= kit;
				if (aiming == null && kit && h.recover == 0 && aims(r, p, m)) {
					aiming = p;
				}
			}
			if (aiming != null) {
				if (h.progress == 0) {
					r.post("stitch:hold");
					r.post("stitch:" + n + ":hold");
				}
				h.by = aiming;
				h.off = 0;
				h.progress++;
			} else if (h.progress > 0 && ++h.off > GRACE) {
				if (h.progress >= MIN_FAIL && h.by != null) {
					slip(r, h.by, n, m, (float) h.progress / HOLD_TICKS);
					h.recover = RECOVER;
				}
				h.progress = 0;
				h.off = 0;
			}
			float prog = Math.min(1F, (float) h.progress / HOLD_TICKS);
			// a scripted slip at a given point of the hold (Stitch.snapAt)
			if (aiming != null && r.vars.get(SNAP_AT) instanceof Float at && prog >= at) {
				r.vars.remove(SNAP_AT);
				slip(r, aiming, n, m, prog);
				h.progress = 0;
				h.off = 0;
				h.recover = RECOVER;
				return false;
			}
			if (h.progress >= HOLD_TICKS) {
				sewn(r, h.by, n, m);
				for (ServerPlayer p : hunters) {
					if (p.distanceToSqr(m) < SHOW_DIST * SHOW_DIST) {
						CasaNet.stitchRing(p, 1F, n, StitchPayload.SUCCESS);
					}
				}
				r.post("stitch:" + n);
				return true;
			}
			if (aiming != null || h.progress > 0 || e.t % 3 == 0) {
				int flags = (aiming != null ? StitchPayload.ON_TARGET : 0) | (h.recover > 0 ? StitchPayload.COOLDOWN : 0)
						| (anyKit ? 0 : StitchPayload.NO_KIT);
				for (ServerPlayer p : hunters) {
					boolean near = p.distanceToSqr(m) < SHOW_DIST * SHOW_DIST;
					if (near || e.t % 10 == 0) {
						CasaNet.stitchRing(p, near ? prog : -1F, n, flags);
					}
				}
			}
			return false;
		};
	}

	/** Where the mouth of an actor is: a little below its eyes. */
	public static Vec3 mouth(Entity e) {
		return e.getEyePosition().add(0, -e.getBbHeight() * 0.1, 0);
	}

	/** Aim test: a cone that gets narrower with distance (about a third of a block around the mouth), line of sight. */
	public static boolean aims(Run r, ServerPlayer p, Vec3 mouth) {
		double d = p.getEyePosition().distanceTo(mouth);
		if (d > MAX_DIST) {
			return false;
		}
		float deg = (float) Math.max(5.0, Math.min(14.0, Math.toDegrees(Math.atan2(0.32, Math.max(0.5, d)))));
		return r.looking(p, mouth, deg, MAX_DIST);
	}

	/** Makes the stitch being held slip now (the yarn hooks your arm): the running step resets and recovers. */
	public static void snap(Run run, ServerPlayer p) {
		run.vars.put(SNAP, run.now());
		Vec3 at = p.getEyePosition().add(p.getViewVector(1.0F).scale(1.5));
		slip(run, p, 0, at, 0.5F);
	}

	/** The next hold of a stitch slips when it reaches this fraction (0..1): a scripted failure. */
	public static void snapAt(Run run, float fraction) {
		run.vars.put(SNAP_AT, fraction);
	}

	/** Step version of {@link #snapAt}. */
	public static Step snapAtStep(float fraction) {
		return e -> {
			snapAt(e.run, fraction);
			return true;
		};
	}

	private static void slip(Run r, ServerPlayer p, int n, Vec3 m, float prog) {
		// the needle pulled back out: the stitch sound, low and slow
		r.sound(ModSounds.STITCH_PULL, m, 1.0F, 0.55F);
		r.sound(ModSounds.YARN_SNAP, m, 0.6F, 1.3F);
		Fx.shake(p, 1.8F, 16);
		Fx.redFlash(p, 0.3F);
		SanityManager.add(p, -10.0F);
		CasaNet.stitchRing(p, prog, n, StitchPayload.FAIL);
		r.post("stitch:fail");
		if (n > 0) {
			r.post("stitch:" + n + ":fail");
		}
	}

	private static void sewn(Run r, ServerPlayer p, int n, Vec3 m) {
		r.sound(ModSounds.STITCH_PULL, m, 1.2F, 0.95F + r.level.getRandom().nextFloat() * 0.1F);
		r.level.sendParticles(ParticleTypes.CRIT, m.x, m.y, m.z, 8, 0.06, 0.04, 0.06, 0.02);
		if (p != null && !p.isRemoved()) {
			Fx.shake(p, 0.35F, 6);
		}
	}
}
