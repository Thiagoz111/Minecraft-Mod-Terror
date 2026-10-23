package com.deadline.client.model;

import com.deadline.client.car.CarRenderState;
import com.deadline.client.model.gen.AutoModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The car (tools/models/ent_auto.py): wheels roll with the distance driven, the front wheels and the steering wheel
 * follow the steering, the body shivers a little while the engine idles, and the rosary under the rear-view mirror
 * swings with the turns and the bumps.
 */
public class AutoModel extends AutoModelBase {
	/** Front wheel lock and steering wheel turn at full steering (radians). */
	private static final float WHEEL_LOCK = 0.45F, STEERING_WHEEL_TURN = 2.2F;

	public AutoModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		if (!(s instanceof CarRenderState c)) {
			return;
		}
		float t = s.ageInTicks;
		float spin = c.wheelSpin;
		float lock = -c.steer * WHEEL_LOCK;  // steering left turns the front of the wheel towards the car's left (+X)
		rot("wheel_fl", spin, lock, 0F);
		rot("wheel_fr", spin, lock, 0F);
		rot("wheel_rl", spin, 0F, 0F);
		rot("wheel_rr", spin, 0F, 0F);
		rot("steering_wheel", 0F, 0F, c.steer * STEERING_WHEEL_TURN);
		if (c.engineOn) {
			// an old engine idling: the body trembles, more at low revs
			float idle = Math.max(0F, 1F - Math.abs(s.speed) * 3F);
			offset("body", 0F, Mth.sin(t * 2.7F) * 0.06F * idle, 0F);
			rot("body", 0F, 0F, Mth.sin(t * 1.9F) * 0.0025F * idle);
		}
		// the rosary: a pendulum pushed by the turns and the road
		float swing = Mth.sin(t * 0.21F) * 0.06F + Mth.sin(t * 0.53F) * 0.03F * Math.min(1F, Math.abs(s.speed) * 2F);
		rot("rosary", swing * 0.6F + Math.abs(s.speed) * 0.08F, 0F, swing + c.steer * Math.min(1F, Math.abs(s.speed) * 2.5F) * 0.35F);
	}
}
