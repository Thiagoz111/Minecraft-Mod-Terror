package com.deadline.client.horror;

import com.deadline.client.model.ChoripanDemonioModel;
import com.deadline.client.render.HauntRenderState;
import com.deadline.client.render.HauntRenderer;
import com.deadline.horror.casa.dog.ChoripanDemonioEntity;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The long dog in "trail mode" (tools/models/ent_choripan_demonio.py ANIM_NOTES, THE CHAIN): the server entity is the
 * head; every frame the client lays the eight links of the body along the path the head has travelled (a history of
 * its positions, one every 1/8 block), back to the doghouse door -- and the links whose place on that path lies past
 * the door are still INSIDE the doghouse, telescoped 3 texels apart along the door axis, their arms hidden. While it
 * crawls far from the door the spacing stretches (up to 1.6x): the body is longer than it can be.
 */
public class ChoripanDemonioRenderer extends HauntRenderer<ChoripanDemonioEntity, ChoripanDemonioModel> {
	/** Rest pivots of link_0 .. link_7 under scale_root (java offsets) and the texels of trail from the head joint. */
	static final float[] REST_X = {-0.3945F, 0F, 0F, 0F, 0F, 0F, 0F, 0F};
	static final float[] REST_Y = {-28.2979F, -20F, -20F, -22.6994F, -27.7789F, -29.8627F, -26.4758F, -24.5274F};
	static final float[] REST_Z = {-43.0107F, -34F, -19F, -7.3076F, 4.659F, 16.4767F, 30.0608F, 43.9246F};
	static final float[] ARC = {0F, 9.0F, 24.0F, 35.7F, 47.7F, 59.5F, 73.1F, 86.9F};
	static final float HEAD_Z = 10F, INSIDE_STEP = 3F, TEXELS = 32F;
	private static final float MAX_YAW = 35F * Mth.DEG_TO_RAD;
	private static final double SAMPLE = 0.125, KEEP = 14.0, MAX_STRETCH = 1.6;

	/** HauntRenderState + the chain laid out for this frame. */
	public static class DemonState extends HauntRenderState {
		public boolean trail;
		public final float[] x = new float[8], y = new float[8], z = new float[8], yaw = new float[8], pitch = new float[8];
		public final boolean[] inside = new boolean[8];
		/** Blocks the head has travelled (drives the gait of the six hands). */
		public float odo;
		public int state;
		public float stateTicks;
	}

	private static final class Trail {
		final ArrayDeque<Vec3> hist = new ArrayDeque<>();
		double odo;
	}

	private final Map<ChoripanDemonioEntity, Trail> trails = new WeakHashMap<>();

	public ChoripanDemonioRenderer(EntityRendererProvider.Context ctx) {
		super(ctx, new ChoripanDemonioModel(ctx.bakeLayer(ApparitionRenderers.CHORIPAN_DEMONIO)), 0.6F, "choripan_demonio", true);
	}

	@Override
	public HauntRenderState createRenderState() {
		return new DemonState();
	}

	// overrides EntityRenderer#getBoundingBoxForCulling (no @Override, like CarRenderer: public widens either access level)
	public AABB getBoundingBoxForCulling(ChoripanDemonioEntity e) {
		return e.cullingBox();
	}

	@Override
	public void extractRenderState(ChoripanDemonioEntity e, HauntRenderState s, float pt) {
		super.extractRenderState(e, s, pt);
		if (!(s instanceof DemonState d)) {
			return;
		}
		d.state = e.state();
		d.stateTicks = e.stateTicks() + pt;
		Trail tr = this.trails.computeIfAbsent(e, k -> new Trail());
		Vec3 head = e.getPosition(pt);
		Vec3 door = e.door();
		Vec3 out = ChoripanDemonioEntity.forward(e.doorYaw());
		update(tr, head, door, d.state == ChoripanDemonioEntity.STATE_RETRACT);
		d.odo = (float) tr.odo;
		layout(d, tr, head, door, out, d.bodyRot * Mth.DEG_TO_RAD, d.state);
	}

	private static void update(Trail tr, Vec3 head, Vec3 door, boolean retracting) {
		if (retracting) {
			// pulled back along its own path: drop the samples the head has gone back past
			while (!tr.hist.isEmpty()) {
				Iterator<Vec3> it = tr.hist.iterator();
				Vec3 h0 = it.next();
				Vec3 h1 = it.hasNext() ? it.next() : door;
				if (head.distanceTo(h1) <= h0.distanceTo(h1) + 0.02) {
					tr.hist.pollFirst();
				} else {
					break;
				}
			}
			return;
		}
		Vec3 h0 = tr.hist.peekFirst();
		if (h0 == null) {
			tr.hist.addFirst(head);
			return;
		}
		double step = h0.distanceTo(head);
		if (step >= SAMPLE) {
			if (step > 4.0) {
				tr.hist.clear();  // teleported: start a new path
			} else {
				tr.odo += step;
			}
			tr.hist.addFirst(head);
			// keep KEEP blocks of path
			double len = 0;
			Vec3 prev = null;
			List<Vec3> kept = new ArrayList<>();
			for (Vec3 v : tr.hist) {
				if (prev != null) {
					len += prev.distanceTo(v);
				}
				kept.add(v);
				prev = v;
				if (len > KEEP) {
					break;
				}
			}
			if (kept.size() < tr.hist.size()) {
				tr.hist.clear();
				tr.hist.addAll(kept);
			}
		}
	}

	private static void layout(DemonState d, Trail tr, Vec3 head, Vec3 door, Vec3 out, float bodyRad, int state) {
		// the path: head -> history (newest first) -> the door
		List<Vec3> path = new ArrayList<>();
		path.add(head);
		for (Vec3 v : tr.hist) {
			if (v.distanceToSqr(path.get(path.size() - 1)) > 1.0E-6) {
				path.add(v);
			}
		}
		if (path.get(path.size() - 1).distanceToSqr(door) > 1.0E-4) {
			path.add(door);
		}
		double total = 0;
		for (int i = 1; i < path.size(); i++) {
			total += path.get(i - 1).distanceTo(path.get(i));
		}
		double body = (HEAD_Z + ARC[7]) / TEXELS;
		double stretch = state == ChoripanDemonioEntity.STATE_RETRACT ? 1.0 : Mth.clamp(total / body, 1.0, MAX_STRETCH);
		Vec3 f = new Vec3(-Mth.sin(bodyRad), 0, Mth.cos(bodyRad));
		Vec3 r = new Vec3(-Mth.cos(bodyRad), 0, -Mth.sin(bodyRad));
		d.trail = true;
		d.x[0] = 0F;
		d.y[0] = REST_Y[0];
		d.z[0] = HEAD_Z;
		d.yaw[0] = 0F;
		d.pitch[0] = 0F;
		d.inside[0] = false;
		int insideCount = 0;
		for (int k = 1; k < 8; k++) {
			double sk = (HEAD_Z + ARC[k]) / TEXELS * stretch;
			Vec3 q;
			if (sk <= total) {
				q = along(path, sk);
				d.inside[k] = false;
			} else {
				// past the door plane: still in the doghouse
				q = door.subtract(out.scale(insideCount * INSIDE_STEP / TEXELS));
				insideCount++;
				d.inside[k] = true;
			}
			Vec3 dv = q.subtract(head);
			d.x[k] = (float) (-TEXELS * dv.dot(r));
			d.z[k] = (float) (-TEXELS * dv.dot(f));
			d.y[k] = (float) (REST_Y[k] - TEXELS * dv.y);
		}
		// headings: each link points at the one behind it (the last one along the one before); yaw clamped to its leader
		float lead = 0F;
		for (int k = 1; k < 8; k++) {
			int a = k < 7 ? k : 6;
			float vx = d.x[a + 1] - d.x[a];
			float vy = d.y[a + 1] - d.y[a];
			float vz = d.z[a + 1] - d.z[a];
			float h = Mth.sqrt(vx * vx + vz * vz);
			float yaw = h < 1.0E-3F ? lead : (float) Mth.atan2(vx, vz);
			yaw = lead + Mth.clamp(Mth.wrapDegrees((yaw - lead) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD, -MAX_YAW, MAX_YAW);
			d.yaw[k] = yaw;
			d.pitch[k] = h < 1.0E-3F ? 0F : (float) Mth.atan2(-vy, h);
			lead = yaw;
		}
	}

	private static Vec3 along(List<Vec3> path, double s) {
		double left = s;
		for (int i = 1; i < path.size(); i++) {
			Vec3 a = path.get(i - 1);
			Vec3 b = path.get(i);
			double len = a.distanceTo(b);
			if (len >= left && len > 1.0E-6) {
				return a.lerp(b, left / len);
			}
			left -= len;
		}
		return path.get(path.size() - 1);
	}
}
