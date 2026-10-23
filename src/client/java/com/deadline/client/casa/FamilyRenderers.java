package com.deadline.client.casa;

import com.deadline.DeadLine;
import com.deadline.casa.FamilyEntities;
import com.deadline.client.model.JorgeModel;
import com.deadline.client.model.MartaModel;
import com.deadline.client.model.NonaModel;
import com.deadline.client.model.TotiModel;
import com.deadline.client.model.gen.JorgeModelBase;
import com.deadline.client.model.gen.MartaModelBase;
import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.client.model.gen.TotiModelBase;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.model.geom.ModelLayerLocation;

/**
 * Casa Morales P1 (client): model layers and renderers of the family. Looks by variant: Jorge 0 jorge.png /
 * 1 jorge_poseido.png, the Nona 0 nona.png / 1 nona_poseida.png (each with its _eyes layer); Marta and Toti have one.
 * B3: look 2 (FamilyEntity.LOOK_COPIA) of Marta, Jorge and Toti is the copy (marta_copia.png, jorge_copia.png,
 * toti_copia.png + _eyes); Marta's and Toti's look 1 is their normal texture.
 * Call {@link #init()} once from the client initializer.
 */
public final class FamilyRenderers {
	public static final ModelLayerLocation MARTA = layer("marta");
	public static final ModelLayerLocation JORGE = layer("jorge");
	public static final ModelLayerLocation NONA = layer("nona");
	public static final ModelLayerLocation TOTI = layer("toti");

	private static boolean done;

	private FamilyRenderers() {
	}

	private static ModelLayerLocation layer(String key) {
		return new ModelLayerLocation(DeadLine.id(key), "main");
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		EntityModelLayerRegistry.registerModelLayer(MARTA, MartaModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(JORGE, JorgeModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(NONA, NonaModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(TOTI, TotiModelBase::createBodyLayer);

		EntityRendererRegistry.register(FamilyEntities.MARTA,
				ctx -> new FamilyRenderer<>(ctx, new MartaModel(ctx.bakeLayer(MARTA)), 0.45F, "marta", true, "", "", "copia"));
		EntityRendererRegistry.register(FamilyEntities.JORGE,
				ctx -> new FamilyRenderer<>(ctx, new JorgeModel(ctx.bakeLayer(JORGE)), 0.55F, "jorge", true, "", "poseido", "copia"));
		EntityRendererRegistry.register(FamilyEntities.NONA,
				ctx -> new FamilyRenderer<>(ctx, new NonaModel(ctx.bakeLayer(NONA)), 0.45F, "nona", true, "", "poseida"));
		EntityRendererRegistry.register(FamilyEntities.TOTI,
				ctx -> new FamilyRenderer<>(ctx, new TotiModel(ctx.bakeLayer(TOTI)), 0.4F, "toti", true, "", "", "copia"));
	}
}
