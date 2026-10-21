package com.deadline.client.mixin;

import com.deadline.client.render.FirstPersonSleeve;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.player.AvatarRenderer;
import net.minecraft.resources.Identifier;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** First-person arms: the cassock sleeve goes on top of the bare arm when the exorcist suit is worn. */
@Mixin(AvatarRenderer.class)
public abstract class AvatarRendererMixin {
	@Inject(method = "renderHand", at = @At("TAIL"))
	private void deadline$cassockSleeve(PoseStack pose, SubmitNodeCollector collector, int light, Identifier skin, ModelPart arm,
			boolean sleeve, CallbackInfo ci) {
		AvatarRenderer<?> self = (AvatarRenderer<?>) (Object) this;
		FirstPersonSleeve.render(pose, collector, light, arm, arm == self.getModel().rightArm);
	}
}
