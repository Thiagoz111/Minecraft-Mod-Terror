package com.deadline.sanity;

import com.deadline.caseload.CaseType;
import com.deadline.caseload.HunterData;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.SombraEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModBlocks;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.phys.Vec3;

/**
 * Cordura (0-100). Darkness, haunted places and entities drain it; light, candles, the rosary and pills
 * restore it. The lower it gets, the more the world lies to you.
 */
public final class SanityManager {
	private SanityManager() {
	}

	public static float get(ServerPlayer p) {
		return ModAttachments.get(p).sanity;
	}

	public static void set(ServerPlayer p, float value) {
		HunterData d = ModAttachments.get(p);
		d.sanity = Mth.clamp(value, 0.0F, 100.0F);
		Fx.sanity(p, d.sanity);
	}

	public static void add(ServerPlayer p, float delta) {
		if (p.isCreative() && delta < 0) {
			return;
		}
		HunterData d = ModAttachments.get(p);
		float before = d.sanity;
		d.sanity = Mth.clamp(d.sanity + delta, 0.0F, 100.0F);
		if (Math.abs(before - d.sanity) >= 0.5F || d.sanity == 0 || d.sanity == 100) {
			Fx.sanity(p, d.sanity);
		}
	}

	public static void tick(MinecraftServer server) {
		if (server.getTickCount() % 10 != 0) {
			return;
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (p.isSpectator() || p.isCreative()) {
				continue;
			}
			tickPlayer(p);
		}
	}

	private static void tickPlayer(ServerPlayer p) {
		ServerLevel level = p.level();
		HunterData d = ModAttachments.get(p);
		boolean haunted = CaseType.forLevel(level.dimension()) != null || com.deadline.caseload.OverworldCase.atSite(p);
		BlockPos pos = p.blockPosition();
		int light = level.getMaxLocalRawBrightness(pos);

		float delta = 0;
		if (haunted) {
			delta -= light < 5 ? 0.22F : (light < 9 ? 0.1F : 0.02F);
		} else if (level.isDarkOutside() && light < 4) {
			delta -= 0.04F;
		} else if (light >= 10) {
			delta += 0.25F;
		}
		if (nearLitCandles(level, pos)) {
			delta = Math.max(delta, 0) + 0.15F;
		}
		boolean rosary = p.getOffhandItem().is(ModItems.ROSARY) || p.getMainHandItem().is(ModItems.ROSARY);
		if (delta < 0 && rosary) {
			delta *= 0.5F;
		}
		if (delta < 0 && ModItems.wearsSuit(p)) {
			delta *= 0.65F;
		}
		if (delta != 0) {
			add(p, delta);
		}

		RandomSource r = p.getRandom();
		float s = d.sanity;
		if (s < 65 && r.nextInt(100) < 2) {
			Fx.hallucination(p, "whisper");
		}
		if (s < 45 && r.nextInt(100) < 2) {
			Fx.hallucination(p, r.nextBoolean() ? "footsteps" : "knock");
		}
		if (s < 30 && r.nextInt(150) == 0) {
			Fx.hallucination(p, "figure");
		}
		if (s < 22 && r.nextInt(240) == 0) {
			trySpawnSombra(level, p);
		}
		if (s <= 0.01F) {
			if (r.nextInt(4) == 0) {
				p.hurtServer(level, level.damageSources().magic(), 1.0F);
			}
			if (!p.hasEffect(MobEffects.NAUSEA)) {
				p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 200, 0));
			}
		}
	}

	private static boolean nearLitCandles(ServerLevel level, BlockPos pos) {
		for (BlockPos q : BlockPos.betweenClosed(pos.offset(-3, -1, -3), pos.offset(3, 1, 3))) {
			var st = level.getBlockState(q);
			if (st.is(ModBlocks.RITUAL_CANDLE) && st.getValue(CandleBlock.LIT)) {
				return true;
			}
		}
		return false;
	}

	private static void trySpawnSombra(ServerLevel level, ServerPlayer p) {
		if (!level.getEntitiesOfClass(SombraEntity.class, p.getBoundingBox().inflate(48)).isEmpty()) {
			return;
		}
		Vec3 look = p.getLookAngle();
		for (int i = 0; i < 10; i++) {
			double a = p.getRandom().nextDouble() * Math.PI * 2;
			double r = 12 + p.getRandom().nextDouble() * 8;
			Vec3 at = p.position().add(Math.cos(a) * r, 0, Math.sin(a) * r);
			// Prefer the edge of vision: not right in front, not right behind.
			Vec3 to = at.subtract(p.position()).normalize();
			double dot = to.x * look.x + to.z * look.z;
			if (dot > 0.85 || dot < -0.6) {
				continue;
			}
			BlockPos bp = BlockPos.containing(at);
			for (int dy = 4; dy >= -4; dy--) {
				BlockPos q = bp.above(dy);
				if (level.getBlockState(q.below()).isSolid() && level.getBlockState(q).isAir() && level.getBlockState(q.above()).isAir()
						&& level.getBrightness(LightLayer.BLOCK, q) < 6) {
					SombraEntity s = ModEntities.SOMBRA.create(level, EntitySpawnReason.EVENT);
					if (s != null) {
						s.snapTo(q.getX() + 0.5, q.getY(), q.getZ() + 0.5, 0, 0);
						level.addFreshEntity(s);
						level.playSound(null, q, ModSounds.SOMBRA_APPEAR, SoundSource.HOSTILE, 0.8F, 1.0F);
					}
					return;
				}
			}
		}
	}

	/** True if the haunt entity is close enough to count as an EMF source. */
	public static boolean isSource(HauntEntity e) {
		return e.isAlive();
	}
}
