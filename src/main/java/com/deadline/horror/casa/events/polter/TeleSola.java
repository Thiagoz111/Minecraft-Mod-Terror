package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.director.Props;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Interactables;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import com.mojang.math.Transformation;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * 20 tele_sola (acts 2-5, intensity 3): the old TV of the living room turns itself on, static at full volume. When he
 * looks at it, for a moment there is a face in the snow, pressed against the glass from the inside. It goes off when
 * he turns it off (right click) or by itself after a while.
 */
public class TeleSola extends HorrorEvent {
	/** The face in the static, drawn with block glyphs (grey on the snow). */
	private static final String FACE = " ▄▓▓▓▓▄ \n▓▀ ▓▓ ▀▓\n▓ ● ▓ ● ▓\n▓▓  ▼  ▓▓\n ▓ ▀▀▀ ▓ \n  ▀▓▓▀  ";
	private static final int LENGTH = 20 * 25;

	public TeleSola() {
		super("tele_sola", Kind.POLTER);
		this.acts(2, 5).intensity(3).cooldown(240).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		BlockPos tv = tv(c);
		if (tv == null || !Polter.key(c.level().getBlockState(tv)).equals("casa_tele_vieja_apagada")) {
			return false;
		}
		double d = Apparitions.dist(c, Vec3.atCenterOf(tv));
		if (d < 3.0 || d > 18.0) {
			return false;
		}
		c.put("tv", tv);
		return true;
	}

	/** The TV block: the site's "tv" group, or a kit TV next to the "tv" point. */
	private static BlockPos tv(Ctx c) {
		List<BlockPos> g = c.run.def.group("tv");
		if (!g.isEmpty()) {
			BlockPos p = c.run.origin.offset(g.get(0));
			if (Polter.key(c.level().getBlockState(p)).startsWith("casa_tele_vieja")) {
				return p;
			}
		}
		if (Apparitions.has(c.run, "tv")) {
			List<BlockPos> near = Polter.kitNear(c.run, c.run.at("tv"), 2, 1, k -> k.startsWith("casa_tele_vieja"));
			return near.isEmpty() ? null : near.get(0);
		}
		return null;
	}

	@Override
	public void start(Ctx c) {
		BlockPos tv = c.get("tv");
		BlockState s = c.level().getBlockState(tv);
		c.put("prev", s);
		Interactables.setKept(c.run, tv, CasaProps.kit("casa_tele_vieja_estatica", s));
		Vec3 at = screen(c, tv, 2.6);
		c.put("at", at);
		c.run.sound(ModSounds.POLTER_TELE_ON, at, 1.2F, 1.0F);
		Polter.noise(c.run, at, 65F);
		c.put("face", -1);
	}

	/** A point on the screen's face (north model: screen x 2.6..13.4, y 11.4..20.4, glass at z 2.9). */
	private static Vec3 screen(Ctx c, BlockPos tv, double z) {
		return Polter.local(tv, Polter.facing(c.level().getBlockState(tv)), 8.0, 15.9, z);
	}

	@Override
	public boolean tick(Ctx c) {
		BlockPos tv = c.get("tv");
		Vec3 at = c.get("at");
		if (!Polter.key(c.level().getBlockState(tv)).equals("casa_tele_vieja_estatica")) {
			return true;  // someone switched it
		}
		if (c.t % 160 == 0) {
			c.run.sound(ModSounds.CASA_TV_STATIC, at, 2.0F, 1.0F);
		}
		int face = c.get("face");
		if (face < 0 && c.t > 30 && Apparitions.dist(c, at) < 10 && Apparitions.sees(c, at, 22F)) {
			c.put("face", c.t);
			showFace(c, tv);
			Fx.staticNoise(c.p, 0.45F, 10);
			c.run.sound(ModSounds.POLTER_SUSURRO, at, 0.8F, 0.6F);
		}
		if (face >= 0 && c.t - face == 9) {
			c.run.despawn("tele_sola:cara");
		}
		if (Polter.got(c, "tele") || c.t >= LENGTH) {
			c.run.sound(ModSounds.POLTER_TELE_OFF, at, 1.0F, 1.0F);
			return true;
		}
		return false;
	}

	private static void showFace(Ctx c, BlockPos tv) {
		Display.TextDisplay td = EntityType.TEXT_DISPLAY.create(c.level(), EntitySpawnReason.EVENT);
		if (td == null) {
			return;
		}
		Direction f = Polter.facing(c.level().getBlockState(tv));
		Vec3 v = Polter.local(tv, f, 8.0, 11.8, 2.6);
		td.snapTo(v.x, v.y, v.z, f.toYRot(), 0F);
		td.setBillboardConstraints(Display.BillboardConstraints.FIXED);
		td.setBackgroundColor(0);
		td.addTag(Props.ACTOR_TAG);
		float k = 0.34F;  // six lines of text, ~0.5 block: the height of the screen
		td.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(k, k, k), new Quaternionf()));
		td.setLineWidth(200);
		td.setText(Component.literal(FACE).withStyle(Style.EMPTY.withColor(0x5A5A5A)));
		c.level().addFreshEntity(td);
		c.run.actor("tele_sola:cara", td);
	}

	@Override
	public void stop(Ctx c) {
		c.run.despawn("tele_sola:cara");
		BlockPos tv = c.get("tv");
		BlockState prev = c.get("prev");
		if (tv != null && prev != null && Polter.key(c.level().getBlockState(tv)).equals("casa_tele_vieja_estatica")) {
			Interactables.setKept(c.run, tv, prev);
		}
		Polter.stopSound(c.run, ModSounds.CASA_TV_STATIC);
	}

	@Override
	public int maxTicks() {
		return LENGTH + 40;
	}
}
