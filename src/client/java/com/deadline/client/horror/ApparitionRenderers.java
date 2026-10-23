package com.deadline.client.horror;

import com.deadline.DeadLine;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.ChoripanModel;
import com.deadline.client.model.ManoModel;
import com.deadline.client.model.SabanaModel;
import com.deadline.client.model.gen.ChoripanDemonioModelBase;
import com.deadline.client.model.gen.ChoripanModelBase;
import com.deadline.client.model.gen.ManoModelBase;
import com.deadline.client.model.gen.SabanaModelBase;
import com.deadline.client.render.HauntRenderer;
import com.deadline.horror.casa.ApparitionEntities;
import com.deadline.horror.casa.dog.DogEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.model.geom.ModelLayerLocation;

/**
 * Client side of B3 (the Casa apparitions and Choripán): model layers and renderers of the dog (looks 0 normal,
 * 1 bufanda, 2 muerto, each with its _eyes layer), the long dog (trail mode), the grey hand and the bedsheet.
 * Call {@link #init()} once from the client initializer.
 */
public final class ApparitionRenderers {
	public static final ModelLayerLocation CHORIPAN = layer("choripan");
	public static final ModelLayerLocation CHORIPAN_DEMONIO = layer("choripan_demonio");
	public static final ModelLayerLocation MANO = layer("mano");
	public static final ModelLayerLocation SABANA = layer("sabana");

	private static boolean done;

	private ApparitionRenderers() {
	}

	private static ModelLayerLocation layer(String key) {
		return new ModelLayerLocation(DeadLine.id(key), "main");
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		EntityModelLayerRegistry.registerModelLayer(CHORIPAN, ChoripanModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(CHORIPAN_DEMONIO, ChoripanDemonioModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(MANO, ManoModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(SABANA, SabanaModelBase::createBodyLayer);

		EntityRendererRegistry.register(DogEntities.CHORIPAN,
				ctx -> new FamilyRenderer<>(ctx, new ChoripanModel(ctx.bakeLayer(CHORIPAN)), 0.35F, "choripan", true, "", "bufanda", "muerto"));
		EntityRendererRegistry.register(DogEntities.CHORIPAN_DEMONIO, ChoripanDemonioRenderer::new);
		EntityRendererRegistry.register(ApparitionEntities.MANO,
				ctx -> new HauntRenderer<>(ctx, new ManoModel(ctx.bakeLayer(MANO)), 0.0F, "mano", false));
		EntityRendererRegistry.register(ApparitionEntities.SABANA,
				ctx -> new HauntRenderer<>(ctx, new SabanaModel(ctx.bakeLayer(SABANA)), 0.0F, "sabana", false));
	}
}
