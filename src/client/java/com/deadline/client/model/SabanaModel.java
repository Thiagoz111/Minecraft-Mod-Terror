package com.deadline.client.model;

import com.deadline.client.model.gen.SabanaModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.ApparitionEntities;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The bedsheet of the patio line (tools/models/ent_sabana.py ANIM_NOTES). Two shapes on one rig: 'flat' (the sheet
 * with nobody in it: hanging from the line, or lying crumpled on the ground) and 'figure' (full of somebody who is not
 * there: a head, shoulders, arms reaching, drapes streaming). The collapse deflates the figure into nothing.
 */
public class SabanaModel extends SabanaModelBase {
	private static final String[] SIDES = {"front", "back", "right", "left"};

	public SabanaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		boolean fresh = t < 4F;
		// the deflation runs 0 -> 1 over ~8 ticks once the collapse starts (and stays 1 lying flat)
		float gone = blend(s, 0, a == ApparitionEntities.SABANA_COLLAPSE || a == ApparitionEntities.SABANA_FLAT ? 1F : 0F,
				fresh ? 1F : 0.3F);
		boolean showFigure = a == ApparitionEntities.SABANA_FLY || (a == ApparitionEntities.SABANA_COLLAPSE && gone < 0.95F);
		boolean showFlat = a == ApparitionEntities.SABANA_HANG || a == ApparitionEntities.SABANA_FLAT
				|| (a == ApparitionEntities.SABANA_COLLAPSE && gone >= 0.95F);
		figure.visible = showFigure;
		flat.visible = showFlat;

		if (showFigure) {
			apply(POSE_FLY, 1F);
			for (String side : SIDES) {
				for (int k = 1; k <= 3; k++) {
					rot("drape_" + side + "_" + k, Mth.sin(t * 0.5F - k * 0.9F) * 0.12F * k, 0F, 0F);
				}
			}
			rot("right_sleeve", 0F, 0F, Mth.sin(t * 0.3F) * 0.1F);
			rot("left_sleeve", 0F, 0F, -Mth.sin(t * 0.3F + 0.6F) * 0.1F);
			rot("head", Mth.sin(t * 0.17F) * 0.06F, 0F, 0.1F + Mth.sin(t * 0.11F) * 0.08F);
			// deflating: it sags into itself and spreads, then there is nothing in it
			float k = Mth.clamp(gone / 0.95F, 0F, 1F);
			figure.yScale *= 1F - 0.85F * k;
			figure.xScale *= 1F + 0.25F * k;
			figure.zScale *= 1F + 0.25F * k;
			figure.y += 46F * 0.85F * k;
		}
		if (showFlat) {
			if (a == ApparitionEntities.SABANA_HANG) {
				// on the line: it breathes in the wind, a gust now and then
				float gust = Math.max(0F, Mth.sin(t * 0.045F)) * Math.max(0F, Mth.sin(t * 0.31F));
				rot("flat", Mth.sin(t * 0.08F) * 0.06F - 0.25F * gust, 0F, 0F);
				rot("flat_2", Mth.sin(t * 0.08F + 1F) * 0.12F - 0.2F * gust, 0F, 0F);
				rot("flat_3", Mth.sin(t * 0.08F + 2F) * 0.18F - 0.15F * gust, 0F, 0F);
			} else {
				// empty on the ground, crumpled
				flat.xRot = Mth.PI * 0.5F;
				flat.y = -0.4F;
				rot("flat_2", -0.18F, 0F, 0F);
				rot("flat_3", 0.12F, 0F, 0F);
			}
		}
	}
}
