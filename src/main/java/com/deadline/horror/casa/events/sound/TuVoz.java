package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.voice.Voice;
import com.deadline.voice.VoiceBackend;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.world.phys.Vec3;

/**
 * 7 tu_voz (acts 2-5, intensity 3): his own voice, recorded from his microphone, calling him from another room. With
 * Simple Voice Chat the house keeps the next thing he says ("casa_voz"; the Colegio's roll-call answer "presente" if
 * there is one already) and plays it back from over there. Without a recording: something whispers there, a breath
 * shaped like a name, and then knocks once.
 */
public class TuVoz extends HorrorEvent {
	public static final String CLIP = "casa_voz";
	private static final Map<UUID, Long> ARMED = new HashMap<>();

	public TuVoz() {
		super("tu_voz", Kind.SOUND);
		this.acts(2, 5).intensity(3).cooldown(240).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		arm(c);
		Vec3 at = Risita.otherRoom(c, 5.0, 18.0);
		if (at == null) {
			return false;
		}
		c.put("at", at.add(0, 0.5, 0));
		return true;
	}

	/** Opens a capture window for his next words (once a minute at most) while the house has nothing of his yet. */
	private static void arm(Ctx c) {
		if (!Voice.enabled(c.p) || Voice.hasClip(c.p, CLIP)) {
			return;
		}
		Long last = ARMED.get(c.p.getUUID());
		if (last == null || c.run.now() - last > 20 * 60 || c.run.now() < last) {
			ARMED.put(c.p.getUUID(), c.run.now());
			Voice.tagNext(c.p, CLIP, 30_000);
		}
	}

	private static String clip(Ctx c) {
		if (Voice.hasClip(c.p, CLIP)) {
			return CLIP;
		}
		return Voice.hasClip(c.p, "presente") ? "presente" : null;
	}

	@Override
	public void start(Ctx c) {
		Vec3 at = c.get("at");
		String tag = clip(c);
		boolean voiced = tag != null && Voice.play(c.p, c.p, tag, VoiceBackend.Effect.DRY, at);
		c.put("voiced", voiced);
		if (!voiced) {
			c.run.sound(ModSounds.POLTER_SUSURRO, at, 0.9F, Polter.pitch(c, 0.9F, 1.0F));
		}
	}

	@Override
	public boolean tick(Ctx c) {
		boolean voiced = c.get("voiced");
		if (!voiced && c.t == 26) {
			c.run.sound(ModSounds.POLTER_GOLPE, c.<Vec3>get("at"), 1.0F, 0.8F);
		}
		return c.t >= 30;
	}
}
