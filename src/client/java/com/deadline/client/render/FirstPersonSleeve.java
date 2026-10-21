package com.deadline.client.render;

import com.deadline.DeadLine;
import com.deadline.registry.ModItems;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;

/** The exorcist's black cassock sleeve over the first-person arm (vanilla draws no armour on the hand). */
public final class FirstPersonSleeve {
	private static final Identifier TEXTURE = DeadLine.id("textures/entity/exorcist_sleeve.png");
	private static ModelPart right;
	private static ModelPart left;

	private FirstPersonSleeve() {
	}

	public static void render(PoseStack pose, SubmitNodeCollector collector, int light, ModelPart arm, boolean isRight) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || !mc.player.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.EXORCIST_CASSOCK)) {
			return;
		}
		if (right == null) {
			// a wide arm a little inflated, so it wraps both arm types without touching the skin's own sleeve layer
			ModelPart root = LayerDefinition.create(PlayerModel.createMesh(new CubeDeformation(0.45F), false), 64, 64).bakeRoot();
			right = root.getChild("right_arm");
			left = root.getChild("left_arm");
		}
		ModelPart sleeve = isRight ? right : left;
		sleeve.loadPose(arm.storePose());
		sleeve.visible = true;
		collector.submitModelPart(sleeve, pose, RenderTypes.entityCutoutNoCull(TEXTURE), light, OverlayTexture.NO_OVERLAY, null);
	}
}
