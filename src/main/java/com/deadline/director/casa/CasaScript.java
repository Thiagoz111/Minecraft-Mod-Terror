package com.deadline.director.casa;

import com.deadline.director.CaseScript;
import com.deadline.director.Run;
import com.deadline.director.Script;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * PLACEHOLDER for case 2, "Casa Morales v2" (docs/design/casa_terror.md): the full horror script replaces this class.
 * The case happens in the real overworld (CaseType.overworld()); the hunter drives there. One chapter, no objectives,
 * no checklist, no title card. The only thing it does: when a hunter first comes within {@link #ARRIVAL_RADIUS} blocks
 * of the site marker "llegada" (fallback "spawn") the run posts the event "llegada" (once; flag "llegada").
 */
public class CasaScript extends CaseScript {
	public static final double ARRIVAL_RADIUS = 24.0;

	@Override
	public String siteKey() {
		return "casa";
	}

	@Override
	public void define(Script s) {
		s.chapter(1, "spawn").noCard();
	}

	@Override
	public void tick(Run run) {
		if (run.has("llegada")) {
			return;
		}
		Vec3 target = arrival(run);
		for (ServerPlayer p : run.hunters()) {
			if (p.position().distanceToSqr(target) < ARRIVAL_RADIUS * ARRIVAL_RADIUS) {
				run.flag("llegada");
				run.post("llegada");
				return;
			}
		}
	}

	/** World position of the arrival marker ("llegada", or "spawn" for sites that do not have one). */
	public static Vec3 arrival(Run run) {
		return run.at(run.def.points.containsKey("llegada") ? "llegada" : "spawn");
	}
}
