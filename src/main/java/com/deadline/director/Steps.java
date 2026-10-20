package com.deadline.director;

import com.deadline.net.Fx;
import java.util.Arrays;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/** Step library for scripts. Every step is stateless (state lives in the {@link Exec}), so beats can repeat. */
public final class Steps {
	private Steps() {
	}

	public static Step wait(int ticks) {
		return e -> e.t >= ticks;
	}

	public static Step waitUntil(Predicate<Exec> cond) {
		return cond::test;
	}

	/** Waits until the condition holds or `timeout` ticks pass. */
	public static Step waitUntil(Predicate<Exec> cond, int timeout) {
		return e -> cond.test(e) || e.t >= timeout;
	}

	/** Runs code once. */
	public static Step run(Consumer<Exec> code) {
		return e -> {
			code.accept(e);
			return true;
		};
	}

	/** Runs code every tick until it returns true. */
	public static Step loop(Predicate<Exec> code) {
		return code::test;
	}

	/** Starts the steps in a parallel sequence and continues immediately. */
	public static Step fork(Step... steps) {
		List<Step> list = Arrays.asList(steps);
		return e -> {
			e.run.start(e.label + "/fork", e.player, list);
			return true;
		};
	}

	public static Step flag(String f) {
		return run(e -> e.run.flag(f));
	}

	public static Step unflag(String f) {
		return run(e -> e.run.unflag(f));
	}

	public static Step complete(String objective) {
		return run(e -> e.run.complete(objective));
	}

	public static Step chapter(int n) {
		return run(e -> e.run.startChapter(n, false));
	}

	/** Plays a voice line and waits for it to finish. at = marker point name, or null for "in your head". */
	public static Step say(String lineId, String at) {
		return e -> {
			if (e.t == 0) {
				e.n = e.run.say(lineId, at == null ? null : e.run.at(at));
			}
			return e.t >= e.n;
		};
	}

	/** Plays a voice line and continues immediately. */
	public static Step sayAsync(String lineId, String at) {
		return run(e -> e.run.say(lineId, at == null ? null : e.run.at(at)));
	}

	/** Subtitle without audio (thoughts, signs). */
	public static Step caption(String lineId, int ticks) {
		return run(e -> {
			for (ServerPlayer p : e.run.hunters()) {
				Fx.subtitle(p, "deadline.speaker." + Run.speakerOf(lineId), "deadline.line." + lineId, ticks);
			}
		});
	}

	public static Step sound(SoundEvent s, String at, float volume) {
		return run(e -> e.run.sound(s, at == null ? null : e.run.at(at), volume, 1.0F));
	}

	public static Step soundAt(SoundEvent s, Function<Exec, Vec3> at, float volume, float pitch) {
		return run(e -> e.run.sound(s, at.apply(e), volume, pitch));
	}

	public static Step lights(String group, boolean on) {
		return run(e -> e.run.lights(group, on));
	}

	public static Step door(String name, boolean open, boolean slam) {
		return run(e -> e.run.door(name, open, slam));
	}

	public static Step shake(float intensity, int ticks) {
		return run(e -> e.run.hunters().forEach(p -> Fx.shake(p, intensity, ticks)));
	}

	public static Step flash(float strength) {
		return run(e -> e.run.hunters().forEach(p -> Fx.flash(p, strength)));
	}

	public static Step redFlash(float strength) {
		return run(e -> e.run.hunters().forEach(p -> Fx.redFlash(p, strength)));
	}

	public static Step jumpscare(String key) {
		return run(e -> {
			ServerPlayer p = e.target();
			if (p != null) {
				Fx.jumpscare(p, key);
			}
		});
	}

	public static Step fade(int ticks) {
		return run(e -> e.run.hunters().forEach(p -> Fx.fade(p, ticks)));
	}

	public static Step bigText(String key, int ticks) {
		return run(e -> e.run.hunters().forEach(p -> Fx.bigText(p, key, ticks, -1F)));
	}

	public static Step give(Item item, int count) {
		return run(e -> {
			ServerPlayer p = e.target();
			if (p != null && !p.getInventory().add(new ItemStack(item, count))) {
				p.drop(new ItemStack(item, count), false);
			}
		});
	}

	/** Teleports the target hunter to a marker point. */
	public static Step teleport(String point) {
		return run(e -> {
			ServerPlayer p = e.target();
			if (p != null) {
				Vec3 v = e.run.at(point);
				p.teleportTo(e.run.level, v.x, v.y, v.z, java.util.Set.of(), e.run.yaw(point), 0F, false);
			}
		});
	}

	public static Step despawn(String actor) {
		return run(e -> e.run.despawn(actor));
	}
}
