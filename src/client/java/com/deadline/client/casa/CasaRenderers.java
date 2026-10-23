package com.deadline.client.casa;

import com.deadline.casa.CasaSetEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.entity.NoopRenderer;

/** Client side of the Casa Morales case: every casa renderer, payload and screen hook in one place. */
public final class CasaRenderers {
	private CasaRenderers() {
	}

	public static void init() {
		CasaClientNet.init();
		CasaItemRenderers.init();
		FamilyRenderers.init();
		// the demon wisp is only particles and sound
		EntityRendererRegistry.register(CasaSetEntities.DEMON_WISP, NoopRenderer::new);
	}
}
