package com.deadline.director;

import com.deadline.DeadLine;
import com.deadline.entity.HauntEntity;
import com.deadline.item.FlashlightItem;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.site.SiteDef;
import com.mojang.math.Transformation;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Shared stagecraft for scripts: actors, chalk writing, furniture that turns, the flashlight beam, reprimands. */
public final class Props {
	/** Tag on the director's text displays: one loaded back from disk (after a crash) is an orphan and is removed. */
	public static final String ACTOR_TAG = "deadline_director";

	private Props() {
	}

	// ------------------------------------------------------------------ actors
	/** Spawns a scripted haunt (no AI) at a marker point, facing its marker yaw (or the star when faceStar). */
	public static <T extends Entity> T spawn(Run r, String actor, EntityType<T> type, String point, boolean faceStar) {
		T e = type.create(r.level, EntitySpawnReason.EVENT);
		if (e == null) {
			return null;
		}
		Vec3 v = r.at(point);
		float yaw = r.yaw(point);
		ServerPlayer star = r.star();
		if (faceStar && star != null) {
			yaw = yawTowards(v, star.position());
		}
		e.snapTo(v.x, v.y, v.z, yaw, 0F);
		e.setYHeadRot(yaw);
		e.setYBodyRot(yaw);
		if (e instanceof HauntEntity h) {
			h.scripted = true;
			h.setNoAi(true);
			h.setInvulnerable(true);
			h.setSiteIndex(r.site);
			h.setPersistenceRequired();
			h.directorActor = true;
		}
		r.level.addFreshEntity(e);
		r.actor(actor, e);
		return e;
	}

	public static void place(Run r, String actor, String point, boolean faceStar) {
		Entity e = r.actor(actor);
		if (e == null) {
			return;
		}
		Vec3 v = r.at(point);
		float yaw = r.yaw(point);
		ServerPlayer star = r.star();
		if (faceStar && star != null) {
			yaw = yawTowards(v, star.position());
		}
		e.teleportTo(v.x, v.y, v.z);
		e.setYRot(yaw);
		if (e instanceof net.minecraft.world.entity.LivingEntity l) {
			l.setYHeadRot(yaw);
			l.setYBodyRot(yaw);
		}
	}

	public static void action(Run r, String actor, int action) {
		if (r.actor(actor) instanceof HauntEntity h) {
			h.setAction(action);
		}
	}

	/** Smoke, a burning hiss and the actor sinks out of existence. */
	public static void burnAway(Run r, String actor) {
		Entity e = r.actor(actor);
		if (e == null) {
			return;
		}
		r.level.sendParticles(ModParticles.DEMON_SMOKE, e.getX(), e.getY() + 1.4, e.getZ(), 40, 0.3, 0.7, 0.3, 0.03);
		r.level.playSound(null, e.getX(), e.getY(), e.getZ(), ModSounds.MONJA_BURN, SoundSource.HOSTILE, 1.8F, 1.0F);
		r.despawn(actor);
	}

	public static float yawTowards(Vec3 from, Vec3 to) {
		return (float) (Math.toDegrees(Math.atan2(to.z - from.z, to.x - from.x)) - 90.0);
	}

	// ------------------------------------------------------------------ flashlight beam
	/** True when the player's lit flashlight beam (cone, 12 blocks, line of sight) is on the entity. */
	public static boolean beamOn(ServerPlayer p, Entity e) {
		if (e == null || !lit(p)) {
			return false;
		}
		Vec3 eye = p.getEyePosition();
		Vec3 target = e.position().add(0, e.getBbHeight() * 0.6, 0);
		Vec3 to = target.subtract(eye);
		double d = to.length();
		if (d > 12 || d < 0.1) {
			return d < 0.1;
		}
		if (p.getViewVector(1F).dot(to.scale(1 / d)) < 0.94) {
			return false;
		}
		BlockHitResult hit = p.level().clip(new ClipContext(eye, target, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, p));
		return hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(eye) >= d - 0.8;
	}

	public static boolean lit(ServerPlayer p) {
		ItemStack m = p.getMainHandItem();
		ItemStack o = p.getOffhandItem();
		return (m.is(ModItems.FLASHLIGHT) && FlashlightItem.isOn(m)) || (o.is(ModItems.FLASHLIGHT) && FlashlightItem.isOn(o));
	}

	// ------------------------------------------------------------------ chalk / writing
	/** Writes text on a write marker (a blackboard) as a fixed text display; replaces the previous text there. */
	public static Display.TextDisplay write(Run r, String marker, Component text, float scale) {
		SiteDef.Write w = r.def.writes.get(marker);
		if (w == null) {
			return null;
		}
		String actor = "write:" + marker;
		Display.TextDisplay td = r.actor(actor) instanceof Display.TextDisplay old ? old : null;
		if (td == null) {
			td = EntityType.TEXT_DISPLAY.create(r.level, EntitySpawnReason.EVENT);
			if (td == null) {
				return null;
			}
			Vec3 c = Vec3.atCenterOf(r.origin.offset(w.pos()));
			Direction f = w.facing();
			Vec3 v = c.add(-f.getStepX() * 0.35, -0.25, -f.getStepZ() * 0.35);
			td.snapTo(v.x, v.y, v.z, f.toYRot(), 0F);
			td.setBillboardConstraints(Display.BillboardConstraints.FIXED);
			td.setBackgroundColor(0);
			td.addTag(ACTOR_TAG);
			r.level.addFreshEntity(td);
			r.actor(actor, td);
		}
		td.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(scale, scale, scale), new Quaternionf()));
		td.setLineWidth(Math.max(60, Math.round(w.width() * 40 / scale)));  // wrap at the board's width (40 px a block)
		td.setText(text);
		return td;
	}

	public static Component chalk(String s) {
		return Component.literal(s).withStyle(Style.EMPTY.withColor(0xE9E6DA));
	}

	/** Step: writes `text` letter by letter (2 ticks each) with chalk squeaks; waits until finished. */
	public static Step chalkWrite(String marker, java.util.function.Function<Exec, String> text) {
		return e -> {
			if (e.t == 0) {
				e.data = text.apply(e);
				e.run.sound(ModSounds.TIZA_ESCRIBE, Vec3.atCenterOf(e.run.origin.offset(e.run.def.writes.get(marker).pos())), 1.2F, 1.0F);
			}
			String s = (String) e.data;
			int n = Math.min(s.length(), e.t / 2 + 1);
			write(e.run, marker, chalk(s.substring(0, n)), 1.6F);
			if (n < s.length() && e.t % 24 == 23) {
				e.run.sound(ModSounds.TIZA_ESCRIBE, Vec3.atCenterOf(e.run.origin.offset(e.run.def.writes.get(marker).pos())), 1.0F, 0.9F + e.run.level.random.nextFloat() * 0.2F);
			}
			return n >= s.length() && e.t >= s.length() * 2 + 6;
		};
	}

	// ------------------------------------------------------------------ furniture
	/** Swaps the block at a point marker for another building-kit block, keeping its facing (the key board missing a key). */
	public static void swap(Run r, String point, String block) {
		BlockPos pos = BlockPos.containing(r.at(point));
		BlockState old = r.level.getBlockState(pos);
		net.minecraft.world.level.block.Block b = net.minecraft.core.registries.BuiltInRegistries.BLOCK.getOptional(DeadLine.id(block)).orElse(null);
		if (b == null) {
			return;
		}
		BlockState st = b.defaultBlockState();
		if (old.hasProperty(BlockStateProperties.HORIZONTAL_FACING) && st.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			st = st.setValue(BlockStateProperties.HORIZONTAL_FACING, old.getValue(BlockStateProperties.HORIZONTAL_FACING));
		}
		r.setBlock(pos, st);
	}

	/** Turns every directional block of a group to face a position (chairs that drag round to stare at you). */
	public static void faceGroup(Run r, String group, Vec3 target) {
		for (BlockPos rel : r.def.group(group)) {
			BlockPos pos = r.origin.offset(rel);
			BlockState s = r.level.getBlockState(pos);
			if (s.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
				r.setBlock(pos, s.setValue(BlockStateProperties.HORIZONTAL_FACING, towards(Vec3.atCenterOf(pos), target)));
			}
		}
	}

	public static Direction towards(Vec3 from, Vec3 to) {
		double dx = to.x - from.x;
		double dz = to.z - from.z;
		if (Math.abs(dx) > Math.abs(dz)) {
			return dx > 0 ? Direction.EAST : Direction.WEST;
		}
		return dz > 0 ? Direction.SOUTH : Direction.NORTH;
	}

	// ------------------------------------------------------------------ reprimands
	/** Adds `n` reprimands for a reason (20 s cooldown per reason) and shows the stamp. */
	public static void reprimand(Run r, ServerPlayer p, String reason, int n) {
		String cd = "stampcd:" + reason + ":" + p.getUUID();
		Long last = (Long) r.vars.get(cd);
		if (last != null && r.now() - last < 400) {
			return;
		}
		r.vars.put(cd, r.now());
		String k = "conduct:" + p.getUUID();
		int total = r.counters.merge(k, n, Integer::sum);
		Fx.stamp(p, "deadline." + r.type.key() + ".stamp." + reason, total);
		r.level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.UI_AMONESTACION, SoundSource.PLAYERS, 1.0F, 1.0F);
	}

	public static int conduct(Run r, ServerPlayer p) {
		return r.count("conduct:" + p.getUUID());
	}

	/** A commendation removes one reprimand. */
	public static void commend(Run r, ServerPlayer p) {
		String k = "conduct:" + p.getUUID();
		r.counters.put(k, Math.max(0, r.count(k) - 1));
		Fx.stamp(p, "deadline." + r.type.key() + ".stamp.felicitacion", r.count(k));
	}
}
