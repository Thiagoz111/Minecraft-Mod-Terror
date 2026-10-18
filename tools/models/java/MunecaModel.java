package com.deadline.client.model;

import com.deadline.client.model.gen.MunecaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** The doll: perfectly still while watched (frozen mid-creep), a jerky waddle when it thinks nobody is looking. */
public class MunecaModel extends MunecaModelBase {
	public MunecaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float moving = s.action == 1 ? 1F : 0F;
		float pos = s.walkAnimationPos * 1.2F;
		float spd = Math.min(1F, s.walkAnimationSpeed);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		if (moving > 0F) {
			walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.9F, 0.5F);
			rot("body", 0F, 0F, Mth.sin(pos) * 0.18F * spd);
			rot("head", 0F, Mth.sin(pos * 0.5F) * 0.2F * spd, -Mth.sin(pos) * 0.12F * spd);
			look(s, 0.0F);
		}
		// when frozen it keeps the creepy tilt it had when you turned around
		apply(pose("creep"), Math.max(atk, 1F - moving));
	}
}
