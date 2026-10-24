package com.deadline.horror.casa.blood;

import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.phys.Vec3;

/**
 * 46 escritura (acts 2-6, intensity 3): blood writing on a wall he looked at a few seconds ago -- now behind his back
 * -- "ELLA ESCUCHA", "NO HABLES", "LEMAZA", "ESTÁ DETRÁS". It is there, wet, when he turns round: the letters still
 * run. Reading "ESTÁ DETRÁS" earns a breath on the back of his neck. The writing stays until the case ends
 * ({@link BloodDecals#clear}).
 * <p>Which walls he looked at is remembered by {@link #watch} (every few ticks for every hunter in the house); when he
 * has looked at none of them lately, any blood wall near him that he is not looking at will do.
 */
public class Escritura extends HorrorEvent {
	public static final String ELLA_ESCUCHA = "ELLA ESCUCHA", NO_HABLES = "NO HABLES", LEMAZA = "LEMAZA",
			ESTA_DETRAS = "ESTÁ DETRÁS";
	private static final String[] TEXTS = {ELLA_ESCUCHA, NO_HABLES, LEMAZA, ESTA_DETRAS};
	private static final Map<UUID, Map<String, Long>> SEEN = new HashMap<>();

	public Escritura() {
		super("escritura", Kind.BLOOD);
		this.acts(2, 6).intensity(3).cooldown(150).weight(9);
	}

	/** Remembers which blood walls the hunter is looking at now (called every few ticks by BloodEvents). */
	public static void watch(Run r, ServerPlayer p) {
		if (!HouseQuery.inHouse(r, p)) {
			return;
		}
		Map<String, Long> m = SEEN.computeIfAbsent(p.getUUID(), k -> new HashMap<>());
		for (String k : BloodDecals.walls(r)) {
			Vec3 w = BloodDecals.wallCenter(r, k);
			if (w != null && w.distanceTo(p.getEyePosition()) < 14.0 && r.looking(p, w, 38F, 14.0)) {
				m.put(k, r.now());
			}
		}
	}

	public static void forget(ServerPlayer p) {
		SEEN.remove(p.getUUID());
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		Map<String, Long> seen = SEEN.getOrDefault(c.p.getUUID(), Map.of());
		List<String> recent = new ArrayList<>();
		List<String> any = new ArrayList<>();
		long now = c.run.now();
		for (String k : BloodDecals.walls(c.run)) {
			if (BloodDecals.written(c.run, k)) {
				continue;
			}
			Vec3 w = BloodDecals.wallCenter(c.run, k);
			if (w == null) {
				continue;
			}
			double d = w.distanceTo(c.p.getEyePosition());
			if (d < 2.5 || d > 14.0 || Math.abs(w.y - 1.0 - c.p.getY()) > 2.5) {
				continue;
			}
			if (Apparitions.sees(c, w, 75F)) {
				continue;  // it happens behind his back
			}
			Long t = seen.get(k);
			if (t != null && now - t >= 30 && now - t <= 20 * 30) {
				recent.add(k);
			} else if (d <= 9.0) {
				any.add(k);
			}
		}
		List<String> pool = !recent.isEmpty() ? recent : any;
		if (pool.isEmpty()) {
			return false;
		}
		c.put("w", pool.get(c.rnd.nextInt(pool.size())));
		return true;
	}

	private static String pick(Ctx c, String marker) {
		if (marker.equals("lemaza")) {
			return LEMAZA;  // the 1961 room: his name, again, over the children's scratches
		}
		List<String> used = BloodDecals.texts(c.run);
		List<String> fresh = new ArrayList<>();
		for (String t : TEXTS) {
			if (!used.contains(t)) {
				fresh.add(t);
			}
		}
		List<String> from = fresh.isEmpty() ? List.of(TEXTS) : fresh;
		return from.get(c.rnd.nextInt(from.size()));
	}

	@Override
	public void start(Ctx c) {
		if (c.get("w") == null && !canRun(c)) {
			return;  // fired by hand where it has no wall to write on
		}
		String w = c.get("w");
		String text = pick(c, w);
		List<Display.ItemDisplay> letters = BloodDecals.write(c.run, w, text, c.rnd);
		Vec3 at = BloodDecals.wallCenter(c.run, w);
		c.put("text", text);
		c.put("letters", letters);
		c.put("at", at);
		// a wet finger on plaster, very quiet, somewhere behind him
		Apparitions.sound(c, ModSounds.SANGRE_ESCRIBE, at, 0.3F, Apparitions.pitch(c, 0.85F, 1.0F));
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 at = c.get("at");
		if (at == null) {
			return true;
		}
		Integer seenAt = c.get("seenAt");
		if (seenAt == null) {
			if (!Apparitions.hidden(c.p) && Apparitions.dist(c, at) < 13.0 && Apparitions.sees(c, at, 40F)) {
				c.put("seenAt", c.t);
				Apparitions.sound(c, ModSounds.SANGRE_REVELA, at, 1.0F, 1.0F);
				SanityManager.add(c.p, -5F);
			}
			return c.t > 20 * 45;  // he never turned round: it waits for him on the wall all the same
		}
		int since = c.t - seenAt;
		if (since < 80 && since % 5 == 0) {
			drip(c);
		}
		if (ESTA_DETRAS.equals(c.get("text")) && since == 24 && !Apparitions.hidden(c.p)) {
			Vec3 neck = c.p.getEyePosition().add(c.p.getViewVector(1F).scale(-0.6));
			Apparitions.sound(c, ModSounds.APARICION_ALIENTO, neck, 0.9F, 0.9F);
			SanityManager.add(c.p, -3F);
		}
		return since > 90;
	}

	/** Fresh blood still running from the bottom of a letter. */
	private static void drip(Ctx c) {
		List<Display.ItemDisplay> letters = c.get("letters");
		if (letters == null || letters.isEmpty()) {
			return;
		}
		Display.ItemDisplay d = letters.get(c.rnd.nextInt(letters.size()));
		if (d.isRemoved()) {
			return;
		}
		c.level().sendParticles(ModParticles.BLOOD_DRIP, d.getX(), d.getY() - 0.18, d.getZ(), 1, 0.06, 0.0, 0.06, 0.0);
	}

	@Override
	public int maxTicks() {
		return 20 * 60;
	}
}
