package com.deadline.client.model;

import com.deadline.client.model.gen.SombraModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** The Hat Man: almost still. A slow sway, fingers that never stop moving, a hand that reaches for you. */
public class SombraModel extends SombraModelBase {
	/** Look 1 (SombraEntity.VARIANT_VISITANTE, the Casa's tall figure): ~2.6 blocks instead of 3.4, so it fits a room. */
	private static final float VISITANTE_SCALE = 0.77F;
	private final ModelPart scaleRoot;

	public SombraModel(ModelPart root) {
		super(root);
		this.scaleRoot = root.getChild("scale_root");
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float near = blend(s, 0, s.speed > 0.02F ? 1F : 0F, 0.05F);

		walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.35F, 0.12F);
		rot("body", 0.04F, 0F, Mth.sin(t * 0.03F) * 0.03F);
		look(s, 0.5F);
		rot("head", 0F, 0F, 0.12F + Mth.sin(t * 0.025F) * 0.05F);
		ripple("coat", t, 0.09F, 0.8F, 0.05F, 0.04F, 0F);
		ripple("smoke", t, 0.12F, 0.9F, 0.08F, 0.06F, 0F);
		ripple("right_finger", t, 0.21F, 1.4F, 0.1F, 0F, 0.03F);
		ripple("left_finger", t, 0.19F, 1.2F, 0.1F, 0F, 0.03F);
		apply(pose("reach"), Math.max(atk, near * 0.6F));
		if (s.variant == com.deadline.entity.SombraEntity.VARIANT_VISITANTE) {
			// scaled round its feet (scale_root's pivot is on the ground)
			this.scaleRoot.xScale *= VISITANTE_SCALE;
			this.scaleRoot.yScale *= VISITANTE_SCALE;
			this.scaleRoot.zScale *= VISITANTE_SCALE;
		}
	}
}
