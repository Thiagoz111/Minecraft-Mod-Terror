package com.deadline.client.model;

import com.deadline.client.model.gen.MunecaModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.entity.MunecaEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The doll: perfectly still while watched (frozen mid-creep), a jerky waddle when it thinks nobody is looking. C: Ofelia
 * sitting on the iron bed of the 1961 room ({@link MunecaEntity#ACT_SIT}); with {@link MunecaEntity#ACT_SIT_TURN} her head
 * comes all the way round, slowly, the body not moving (with the family's heads).
 */
public class MunecaModel extends MunecaModelBase {
	public MunecaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		if (s.action == MunecaEntity.ACT_SIT || s.action == MunecaEntity.ACT_SIT_TURN) {
			seated(s);
			return;
		}
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

	/** Sitting still; the head turns round 180 degrees (neck 30 %, head 70 %) with a small hitch, as the family's do. */
	private void seated(HauntRenderState s) {
		float t = s.ageInTicks;
		apply(POSE_SIT, 1F);
		float twist = blend(s, 1, s.action == MunecaEntity.ACT_SIT_TURN ? 1F : 0F, t < 4F ? 1F : 0.06F);
		if (twist > 0.001F) {
			float e = twist * twist * (3F - 2F * twist);
			float hitch = Mth.sin(t * 9F) * 0.035F * Mth.clamp(twist * (1F - twist) * 4F, 0F, 1F);
			rot("neck", 0F, Mth.PI * 0.3F * e + hitch, 0F);
			rot("head", 0F, Mth.PI * 0.7F * e + hitch, 0.15F * e);
		}
	}
}
