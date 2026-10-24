package com.deadline.horror.casa.blood;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.item.FlashlightItem;
import com.deadline.item.FlashlightLights;
import com.deadline.item.ItemUtil;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/**
 * 54 linterna_muere (acts 3-6, intensity 3): the flashlight flickers and dies for 4 seconds. Clicking it does nothing.
 * In those 4 seconds something breathes right next to him, one side, then the other. The beam comes back by itself --
 * and on the floor in front of him, where it stood, two bare bloody footprints facing him.
 * <p>The beam is the flashlight item's own state (custom_model_data flag 0, lit by {@link FlashlightLights}): the
 * event turns it off and back on; while it is dead a first-look use-item hook (BloodEvents) eats the clicks.
 */
public class LinternaMuere extends HorrorEvent {
	private static final int FLICKER = 20, DEAD = 80;
	private static final Map<UUID, Ctx> DEAD_NOW = new HashMap<>();

	public LinternaMuere() {
		super("linterna_muere", Kind.POLTER);
		this.acts(3, 6).intensity(3).cooldown(200).weight(7);
	}

	/** The lit flashlight in one of his hands (EMPTY when none). */
	static ItemStack lit(ServerPlayer p) {
		ItemStack m = p.getMainHandItem();
		if (m.is(ModItems.FLASHLIGHT) && FlashlightItem.isOn(m)) {
			return m;
		}
		ItemStack o = p.getOffhandItem();
		return o.is(ModItems.FLASHLIGHT) && FlashlightItem.isOn(o) ? o : ItemStack.EMPTY;
	}

	/** While dead, the flashlight's clicks are eaten (BloodEvents' use-item hook asks). */
	public static boolean dead(ServerPlayer p) {
		return DEAD_NOW.containsKey(p.getUUID());
	}

	/** A click on the dead flashlight: a dry click, nothing. The stack is touched so the client drops its own guess. */
	public static void deadClick(ServerPlayer p, ItemStack stack) {
		p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.FLASHLIGHT_CLICK, SoundSource.PLAYERS, 0.7F, 0.6F);
		boolean mark = ItemUtil.getFlag(stack, 2);
		ItemUtil.setFlags(stack, false, FlashlightItem.isUv(stack), !mark);
	}

	/** Gives the light back (disconnect, the event stopped). */
	public static void revive(ServerPlayer p) {
		Ctx c = DEAD_NOW.remove(p.getUUID());
		if (c != null) {
			light(c, true);
		}
	}

	@Override
	public boolean canRun(Ctx c) {
		if (Apparitions.hidden(c.p) || !HouseQuery.inHouse(c.run, c.p) || dead(c.p)) {
			return false;
		}
		ItemStack st = lit(c.p);
		if (st.isEmpty() || st.getDamageValue() >= st.getMaxDamage() - 2) {
			return false;
		}
		return HouseQuery.dark(c.run, BlockPos.containing(c.p.getEyePosition()));
	}

	@Override
	public void start(Ctx c) {
		ItemStack st = lit(c.p);
		if (st.isEmpty()) {
			return;
		}
		c.put("stack", st);
		c.put("uv", FlashlightItem.isUv(st));
		c.put("side", c.rnd.nextBoolean());
	}

	private static void light(Ctx c, boolean on) {
		ItemStack st = c.get("stack");
		Boolean uv = c.get("uv");
		if (st == null || st.isEmpty() || !st.is(ModItems.FLASHLIGHT)) {
			return;
		}
		if (on && st.getDamageValue() >= st.getMaxDamage() - 1) {
			on = false;  // the battery really is gone
		}
		ItemUtil.setFlags(st, on, uv != null && uv);
		if (!on) {
			FlashlightLights.clear(c.p);
		}
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.get("stack") == null) {
			return true;
		}
		// it stutters...
		if (c.t < FLICKER) {
			if (c.t == 1 || c.t == 7 || c.t == 12 || c.t == 16) {
				light(c, false);
				c.p.level().playSound(null, c.p.getX(), c.p.getY(), c.p.getZ(), ModSounds.FLASHLIGHT_FLICKER, SoundSource.PLAYERS, 0.6F,
						Apparitions.pitch(c, 0.9F, 1.1F));
			} else if (c.t == 4 || c.t == 10 || c.t == 14) {
				light(c, true);
			}
			return false;
		}
		// ...and dies
		if (c.t == FLICKER) {
			light(c, false);
			DEAD_NOW.put(c.p.getUUID(), c);
			Apparitions.sound(c, ModSounds.LINTERNA_MUERE, c.p.getEyePosition(), 0.7F, 1.0F);
		}
		boolean side = c.get("side");
		if (c.t == FLICKER + 14 || c.t == FLICKER + 46) {
			// breathing at his ear, one side and then the other
			boolean left = (c.t == FLICKER + 14) == side;
			Vec3 look = c.p.getViewVector(1F).multiply(1, 0, 1);
			Vec3 l = look.lengthSqr() > 1.0E-4 ? look.normalize() : new Vec3(0, 0, 1);
			Vec3 lateral = new Vec3(l.z, 0, -l.x).scale(left ? 1.1 : -1.1);
			Vec3 at = c.p.getEyePosition().add(lateral).add(l.scale(-0.4));
			Apparitions.sound(c, ModSounds.SANGRE_RESPIRA, at, 0.9F, Apparitions.pitch(c, 0.9F, 1.0F));
		}
		if (c.t == FLICKER + DEAD) {
			DEAD_NOW.remove(c.p.getUUID());
			light(c, true);
			c.p.level().playSound(null, c.p.getX(), c.p.getY(), c.p.getZ(), ModSounds.FLASHLIGHT_CLICK, SoundSource.PLAYERS, 0.7F, 1.2F);
			footprints(c);
		}
		return c.t > FLICKER + DEAD + 4;
	}

	/** Where it stood: two bare footprints a step in front of him, toes towards him. */
	private static void footprints(Ctx c) {
		Vec3 look = c.p.getViewVector(1F).multiply(1, 0, 1);
		if (look.lengthSqr() < 1.0E-4 || Apparitions.hidden(c.p)) {
			return;
		}
		Vec3 l = look.normalize();
		Vec3 spot = c.p.position().add(l.scale(1.15));
		BlockPos feet = BlockPos.containing(spot.x, c.p.getY() + 0.2, spot.z);
		if (!HouseQuery.standable(c.run, feet)) {
			return;
		}
		Vec3 toward = l.scale(-1);
		float yaw = Pisadas.yaw(toward);
		Vec3 side = new Vec3(toward.z, 0, -toward.x);
		BloodDecals.floor(c.run, BloodDecals.FOOT_L, BloodDecals.onFloor(c.run, spot.add(side.scale(0.12))), yaw, 0.17F, 0.36F);
		BloodDecals.floor(c.run, BloodDecals.FOOT_R, BloodDecals.onFloor(c.run, spot.add(side.scale(-0.12))), yaw, 0.17F, 0.36F);
	}

	@Override
	public void stop(Ctx c) {
		if (DEAD_NOW.get(c.p.getUUID()) == c) {
			DEAD_NOW.remove(c.p.getUUID());
		}
		if (c.get("stack") != null && c.t <= FLICKER + DEAD) {
			light(c, true);  // aborted half way: give the light back
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 8;
	}
}
