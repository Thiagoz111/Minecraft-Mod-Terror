package com.deadline.client.mixin;

import com.deadline.client.ClientFx;
import net.minecraft.client.Camera;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Screen shake: jumpscares, the ringing phone and a failing mind rattle the camera. */
@Mixin(Camera.class)
public abstract class CameraMixin {
	@Shadow
	private float xRot;

	@Shadow
	private float yRot;

	@Shadow
	protected abstract void setRotation(float yRot, float xRot);

	@Inject(method = "setup", at = @At("TAIL"))
	private void deadline$shake(Level level, Entity entity, boolean detached, boolean mirror, float partialTick, CallbackInfo ci) {
		float[] o = ClientFx.shakeOffset(partialTick);
		if (o != null) {
			this.setRotation(this.yRot + o[0], this.xRot + o[1]);
		}
	}
}
