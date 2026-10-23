package com.deadline.client.hunt;

import com.deadline.DeadLine;
import com.deadline.client.ClientFx;
import com.deadline.client.ClientState;
import com.deadline.client.model.gen.AnimaModelBase;
import com.deadline.client.model.gen.ChoripanDemonioModelBase;
import com.deadline.client.model.gen.MartaModelBase;
import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.client.model.gen.PoseidaModelBase;
import com.deadline.client.model.gen.SombraModelBase;
import com.deadline.client.render.HauntModel;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.hunt.NonaRotaEntity;
import com.deadline.registry.ModSounds;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;
import net.fabricmc.fabric.api.client.rendering.v1.world.WorldRenderContext;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/**
 * Jumpscares with a face (docs/design/casa_terror.md 6.6): the creature's 3D head rushes in and fills the screen, glued
 * to the camera, shaking violently, with a red flash and its own stinger, for ~0.85 s. Keys: nona_rota, lucia, copia,
 * perro_largo, cara_roja (any other key keeps the old full-screen picture of DeadLineHud).
 * <p>Rendered in the world pass (WorldRenderEvents.BEFORE_ENTITIES) a few decimetres in front of the camera, full
 * bright, from the creature models themselves: the broken Nona (look 'rota', pose 'jumpscare'), Lucía ('scream'), a
 * smiling copy (Marta with the 'copia' look when B3's texture exists), the long dog ('lunge') and the red face (the
 * tall shadow's grinning head, painted red: hunt/cara_roja.png, or the ánima's maw tinted red as a fallback).
 */
public final class Jumpscare3D {
	/** Length in ticks (0.85 s). */
	public static final int LEN = 17;
	private static final RandomSource RNG = RandomSource.create();

	/** One face: model, pose state, textures, framing (head centre above the feet / forward, distance to the eye). */
	private static final class Face {
		final HauntModel model;
		final HauntRenderState state;
		final Identifier texture;
		final Identifier glow;
		final float up;
		final float fwd;
		final float dist;
		final int color;

		Face(HauntModel model, HauntRenderState state, Identifier texture, Identifier glow, float up, float fwd, float dist, int color) {
			this.model = model;
			this.state = state;
			this.texture = texture;
			this.glow = glow;
			this.up = up;
			this.fwd = fwd;
			this.dist = dist;
			this.color = color;
		}
	}

	private static final Map<String, Face> FACES = new HashMap<>();
	private static String key = "";
	private static int ticks;

	private Jumpscare3D() {
	}

	/** Starts a 3D jumpscare for this key; false = not one of ours (the caller shows the old picture). */
	public static boolean start(String k) {
		if (!handles(k)) {
			return false;
		}
		key = k;
		ticks = LEN;
		ClientFx.shake(3.4F, 20);
		ClientState.redFlash = Math.max(ClientState.redFlash, 0.65F);
		ClientState.flash = Math.max(ClientState.flash, 0.25F);
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(stinger(k), 1.0F, 1.0F));
		return true;
	}

	public static boolean handles(String k) {
		return switch (k) {
			case "nona_rota", "lucia", "copia", "perro_largo", "cara_roja" -> true;
			default -> false;
		};
	}

	public static boolean active() {
		return ticks > 0;
	}

	/** 0 at the start .. 1 at the end. */
	static float progress(float pt) {
		return Mth.clamp((LEN - ticks + pt) / LEN, 0F, 1F);
	}

	static SoundEvent stinger(String k) {
		return switch (k) {
			case "lucia" -> ModSounds.HUNT_STINGER_LUCIA;
			case "copia" -> ModSounds.HUNT_STINGER_COPIA;
			case "perro_largo" -> ModSounds.HUNT_STINGER_PERRO;
			case "cara_roja" -> ModSounds.HUNT_STINGER_CARA;
			default -> ModSounds.HUNT_STINGER_NONA;
		};
	}

	static void tick(Minecraft mc) {
		if (ticks > 0) {
			ticks--;
			ClientState.redFlash = Math.max(ClientState.redFlash, ticks > LEN - 4 ? 0.45F : 0.12F);
		}
	}

	static void reset() {
		ticks = 0;
		key = "";
	}

	// ---------------------------------------------------------------- rendering
	static void render(WorldRenderContext ctx) {
		if (ticks <= 0) {
			return;
		}
		Minecraft mc = Minecraft.getInstance();
		Face f = face(key);
		if (f == null) {
			return;
		}
		float pt = mc.getDeltaTracker().getGameTimeDeltaPartialTick(false);
		float k = progress(pt);
		float life = LEN - ticks + pt;
		// rushes in over the first 2 ticks, then sits in your face, shaking; a last twitch closer before the cut
		float rush = Mth.clamp(life / 2.2F, 0F, 1F);
		float dist = Mth.lerp(rush * rush * (3F - 2F * rush), f.dist * 3.4F, f.dist) - 0.05F * k;
		float amp = 1F - 0.5F * k;
		float jx = (RNG.nextFloat() - 0.5F) * 0.045F * amp;
		float jy = (RNG.nextFloat() - 0.5F) * 0.045F * amp;
		float rz = (RNG.nextFloat() - 0.5F) * 9F * amp;
		float ry = (RNG.nextFloat() - 0.5F) * 7F * amp;

		f.state.ageInTicks = ClientState.ticks + pt;
		if (f.state instanceof NonaRotaRenderer.State st) {
			st.actionTime = life;
		}
		PoseStack ps = ctx.matrices();
		ps.pushPose();
		ps.mulPose(ctx.worldState().cameraRenderState.orientation);
		// camera space: -Z ahead. The model stands with its head centre on the eye line, `dist` in front.
		ps.translate(jx, -f.up + jy, -(dist + f.fwd));
		ps.mulPose(Axis.ZP.rotationDegrees(rz));
		ps.mulPose(Axis.YP.rotationDegrees(180F + ry));
		ps.scale(-1F, -1F, 1F);
		ps.translate(0F, -1.501F, 0F);
		int light = LightTexture.FULL_BRIGHT;
		ctx.commandQueue().submitModel(f.model, f.state, ps, f.model.renderType(f.texture), light, OverlayTexture.NO_OVERLAY, f.color, null, 0, null);
		if (f.glow != null) {
			ctx.commandQueue().submitModel(f.model, f.state, ps, RenderTypes.eyes(f.glow), light, OverlayTexture.NO_OVERLAY, -1, null, 0, null);
		}
		ps.popPose();
	}

	private static Face face(String k) {
		Face f = FACES.get(k);
		if (f == null) {
			try {
				f = build(k);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Jumpscare face {} failed", k, ex);
				f = null;
			}
			if (f != null) {
				FACES.put(k, f);
			}
		}
		return f;
	}

	private static boolean exists(Identifier id) {
		return Minecraft.getInstance().getResourceManager().getResource(id).isPresent();
	}

	private static Identifier tex(String name) {
		return DeadLine.id("textures/entity/" + name + ".png");
	}

	private static Face build(String k) {
		switch (k) {
			case "nona_rota" -> {
				NonaRotaModel m = new NonaRotaModel(NonaModelBase.createBodyLayer().bakeRoot());
				NonaRotaRenderer.State s = new NonaRotaRenderer.State();
				s.action = NonaRotaEntity.ACT_GRAB;
				s.variant = NonaRotaEntity.LOOK_ROTA;
				s.seed = 0x5EED;
				return new Face(m, s, tex("nona_rota"), tex("nona_rota_eyes"), 1.15F, 0.28F, 0.40F, -1);
			}
			case "lucia" -> {
				HauntModel m = posed(() -> PoseidaModelBase.createBodyLayer().bakeRoot(), r -> new PoseidaModelBase(r) {
					@Override
					public void setupAnim(HauntRenderState s) {
						super.setupAnim(s);
						apply(pose("scream"), 1F);
						scare(this, s, 0.35F);
					}
				});
				return new Face(m, state(), tex("poseida"), null, 1.25F, -0.15F, 0.42F, -1);
			}
			case "copia" -> {
				boolean copy = exists(tex("marta_copia"));
				HauntModel m = posed(() -> MartaModelBase.createBodyLayer().bakeRoot(), r -> new MartaModelBase(r) {
					@Override
					public void setupAnim(HauntRenderState s) {
						super.setupAnim(s);
						scare(this, s, 0F);  // the copy does not scream: it smiles, too wide, too close
					}
				});
				// without B3's copy look, a bloodless Marta (grey tint) is the fallback
				return new Face(m, state(), tex(copy ? "marta_copia" : "marta"), null, 1.47F, 0.03F, 0.36F, copy ? -1 : 0xFFB8BEC4);
			}
			case "perro_largo" -> {
				HauntModel m = posed(() -> ChoripanDemonioModelBase.createBodyLayer().bakeRoot(), r -> new ChoripanDemonioModelBase(r) {
					@Override
					public void setupAnim(HauntRenderState s) {
						super.setupAnim(s);
						apply(pose("lunge"), 1F);
						scare(this, s, 0.35F);
					}
				});
				Identifier glow = tex("choripan_demonio_eyes");
				return new Face(m, state(), tex("choripan_demonio"), exists(glow) ? glow : null, 0.75F, 1.75F, 0.45F, -1);
			}
			case "cara_roja" -> {
				Identifier red = DeadLine.id("textures/entity/hunt/cara_roja.png");
				if (exists(red)) {
					HauntModel m = posed(() -> SombraModelBase.createBodyLayer().bakeRoot(), r -> new SombraModelBase(r) {
						@Override
						public void setupAnim(HauntRenderState s) {
							super.setupAnim(s);
							apply(pose("scream"), 1F);
							hide("hat", true);
							scare(this, s, 0.45F);
						}
					});
					Identifier glow = DeadLine.id("textures/entity/hunt/cara_roja_eyes.png");
					return new Face(m, state(), red, exists(glow) ? glow : null, 2.71F, 0.10F, 0.42F, -1);
				}
				HauntModel m = posed(() -> AnimaModelBase.createBodyLayer().bakeRoot(), r -> new AnimaModelBase(r) {
					@Override
					public void setupAnim(HauntRenderState s) {
						super.setupAnim(s);
						apply(pose("scream"), 1F);
						scare(this, s, 0.35F);
					}
				});
				return new Face(m, state(), tex("anima"), null, 1.47F, 0.10F, 0.40F, 0xFFFF3A2A);
			}
			default -> {
				return null;
			}
		}
	}

	private interface Maker {
		HauntModel make(ModelPart root);
	}

	private static HauntModel posed(Supplier<ModelPart> root, Maker maker) {
		return maker.make(root.get());
	}

	private static HauntRenderState state() {
		HauntRenderState s = new HauntRenderState();
		s.seed = 0x5CA4E;
		return s;
	}

	/** Called from inside the anonymous models: the head trembles, the jaw drops `jaw` radians further. */
	private static void scare(HauntModel m, HauntRenderState s, float jaw) {
		float t = s.ageInTicks;
		ModelPart head = m.has("head") ? m.get("head") : null;
		if (head != null) {
			head.xRot += 0.06F * Mth.sin(t * 4.3F);
			head.yRot += 0.05F * Mth.sin(t * 5.1F);
		}
		ModelPart j = m.has("jaw") ? m.get("jaw") : null;
		if (j != null) {
			j.xRot += jaw;
		}
	}
}
