package com.deadline.casa;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/**
 * "LE FALTA SAL": counts handfuls of salt thrown at a possessed actor. A throw is using the salt bag (right click, in the
 * air or at the actor) within 6 blocks while looking at it, or any other source calling {@link #hit}. Every hit burns
 * (SALT_HIT_SCREAM) and stuns the actor; the last one shows the "Ahora sí tiene sal." caption.
 * Events: "sal:hit" and "sal:&lt;n&gt;" per hit ("sal:3" on the third).
 */
public final class SaltHits {
	public static final double RANGE = 6.0;
	private static final List<SaltHits> ACTIVE = new ArrayList<>();

	private final Run run;
	private final String actor;
	private final Entity entity;
	private final int needed;
	private final Map<UUID, Long> cooldown = new HashMap<>();
	private int hits;
	private boolean done;

	private SaltHits(Run run, String actor, Entity entity, int needed) {
		this.run = run;
		this.actor = actor;
		this.entity = entity;
		this.needed = Math.max(1, needed);
	}

	/** Starts counting salt on a run actor (looked up on every throw, so a respawned actor still counts). */
	public static SaltHits track(Run r, String actor) {
		return track(r, actor, 3);
	}

	public static SaltHits track(Run r, String actor, int needed) {
		return add(new SaltHits(r, actor, null, needed));
	}

	public static SaltHits track(Run r, Entity target, int needed) {
		return add(new SaltHits(r, null, target, needed));
	}

	private static SaltHits add(SaltHits s) {
		ACTIVE.removeIf(o -> o.run == s.run && (o.actor != null ? o.actor.equals(s.actor) : o.entity == s.entity));
		ACTIVE.add(s);
		return s;
	}

	public Entity target() {
		Entity e = actor != null ? run.actor(actor) : entity;
		return e == null || e.isRemoved() ? null : e;
	}

	public int hits() {
		return hits;
	}

	public int needed() {
		return needed;
	}

	public boolean done() {
		return done;
	}

	public void stop() {
		ACTIVE.remove(this);
	}

	/** A hit from any source (a thrown handful that landed): no range or aim check. */
	public boolean hit(ServerPlayer by) {
		Entity t = target();
		if (done || t == null) {
			return false;
		}
		apply(by, null, t);
		return true;
	}

	/** Salt bag used by a hunter (from the item-use hook): hits a tracked actor in range and in the crosshair. */
	static void onThrow(ServerPlayer p, InteractionHand hand) {
		ACTIVE.removeIf(s -> s.done || Director.get(s.run.type, s.run.site) != s.run);
		for (SaltHits s : new ArrayList<>(ACTIVE)) {
			if (s.run.level != p.level()) {
				continue;
			}
			Entity t = s.target();
			if (t == null) {
				continue;
			}
			Vec3 c = t.getBoundingBox().getCenter();
			Vec3 head = t.position().add(0, t.getBbHeight() * 0.85, 0);
			if (p.getEyePosition().distanceTo(c) > RANGE + 0.5
					|| !(s.run.looking(p, c, 25F, RANGE + 0.5) || s.run.looking(p, head, 25F, RANGE + 0.5))) {
				continue;
			}
			Long last = s.cooldown.get(p.getUUID());
			if (last != null && s.run.now() - last < 10) {
				return;
			}
			s.cooldown.put(p.getUUID(), s.run.now());
			s.apply(p, hand, t);
			return;
		}
	}

	private void apply(ServerPlayer p, InteractionHand hand, Entity t) {
		Vec3 c = t.getBoundingBox().getCenter();
		if (p != null) {
			Vec3 look = p.getViewVector(1F);
			Vec3 from = p.getEyePosition().add(look.scale(0.6)).add(0, -0.25, 0);
			for (int i = 0; i <= 9; i++) {
				Vec3 q = from.lerp(c, i / 9.0);
				run.level.sendParticles(ModParticles.SALT_SPARKLE, q.x, q.y, q.z, 2, 0.05, 0.05, 0.05, 0.01);
			}
			run.sound(ModSounds.SALT_PLACE, p.position().add(0, 1.2, 0), 0.8F, 1.4F);
			Fx.shake(p, 0.25F, 6);
			if (hand != null) {
				p.swing(hand, true);
				ItemStack stack = p.getItemInHand(hand);
				if (stack.is(ModItems.SALT)) {
					stack.hurtAndBreak(1, p, hand);
				}
			}
		}
		run.level.sendParticles(ModParticles.SALT_SPARKLE, c.x, c.y, c.z, 30, 0.3, 0.5, 0.3, 0.08);
		run.level.sendParticles(ModParticles.DEMON_SMOKE, c.x, c.y + 0.3, c.z, 12, 0.25, 0.4, 0.25, 0.03);
		run.sound(ModSounds.SALT_HIT_SCREAM, c, 1.8F, 0.9F + run.level.random.nextFloat() * 0.2F);
		if (t instanceof HauntEntity haunt) {
			haunt.stun(40);
		}
		hits++;
		run.post("sal:hit");
		run.post("sal:" + hits);
		for (ServerPlayer h : run.hunters()) {
			h.displayClientMessage(Component.translatable("deadline.casa.msg.sal", hits, needed), true);
		}
		if (hits >= needed) {
			done = true;
			ACTIVE.remove(this);
			for (ServerPlayer h : run.hunters()) {
				Fx.subtitle(h, "deadline.speaker.cartel", "deadline.line.casa.cartel.sal", 100);
			}
		}
	}

	static void clearAll() {
		ACTIVE.clear();
	}
}
