package com.deadline.client.car;

import com.deadline.DeadLine;
import com.deadline.car.CarEntity;
import com.deadline.client.model.AutoModel;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/** The car: generated model (tools/models/ent_auto.py), headlights/tail-lights glowing on the eyes layer when lit. */
public class CarRenderer extends MobRenderer<CarEntity, CarRenderState, AutoModel> {
	private static final Identifier TEXTURE = DeadLine.id("textures/entity/auto.png");
	private static final Identifier LIGHTS = DeadLine.id("textures/entity/auto_eyes.png");

	public CarRenderer(EntityRendererProvider.Context ctx) {
		super(ctx, new AutoModel(ctx.bakeLayer(CarClient.LAYER)), 1.4F);
		this.addLayer(new LightsLayer(this));
	}

	@Override
	public CarRenderState createRenderState() {
		return new CarRenderState();
	}

	@Override
	public Identifier getTextureLocation(CarRenderState state) {
		return TEXTURE;
	}

	@Override
	public void extractRenderState(CarEntity car, CarRenderState s, float pt) {
		super.extractRenderState(car, s, pt);
		// a car points where it drives: no body/head split like a creature
		s.bodyRot = Mth.rotLerp(pt, car.yRotO, car.getYRot());
		s.yRot = 0F;
		s.xRot = 0F;
		s.wheelSpin = Mth.lerp(pt, car.wheelRotO, car.wheelRot);
		s.steer = car.steerAngle();
		s.lightsOn = car.lightsShown();
		s.engineOn = car.isEngineOn();
		s.speed = car.clientSpeed();
		s.seed = car.getId();
	}

	/** Full-bright headlights, tail-lights and dashboard glow, only while the lights are on. */
	static final class LightsLayer extends RenderLayer<CarRenderState, AutoModel> {
		private final RenderType type = RenderTypes.eyes(LIGHTS);

		LightsLayer(RenderLayerParent<CarRenderState, AutoModel> parent) {
			super(parent);
		}

		@Override
		public void submit(PoseStack pose, SubmitNodeCollector collector, int light, CarRenderState s, float yRot, float xRot) {
			if (!s.lightsOn) {
				return;
			}
			collector.order(1).submitModel(this.getParentModel(), s, pose, type, light, OverlayTexture.NO_OVERLAY, -1, null, s.outlineColor, null);
		}
	}
}
