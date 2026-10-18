package com.deadline.entity;

import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;

/** Thrown flask of holy water: burns entities in a small radius and purifies anchors. */
public class HolyWaterEntity extends ThrowableItemProjectile {
	public HolyWaterEntity(EntityType<? extends HolyWaterEntity> type, Level level) {
		super(type, level);
	}

	public HolyWaterEntity(Level level, LivingEntity owner, ItemStack stack) {
		super(ModEntities.HOLY_WATER, owner, level, stack);
	}

	@Override
	protected Item getDefaultItem() {
		return ModItems.HOLY_WATER;
	}

	@Override
	protected void onHit(HitResult hit) {
		super.onHit(hit);
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		double x = this.getX(), y = this.getY(), z = this.getZ();
		level.sendParticles(ParticleTypes.SPLASH, x, y + 0.2, z, 40, 0.6, 0.2, 0.6, 0.3);
		level.sendParticles(ModParticles.HOLY_SPARK, x, y + 0.3, z, 30, 0.8, 0.4, 0.8, 0.08);
		level.playSound(null, x, y, z, ModSounds.HOLY_WATER_SPLASH, SoundSource.PLAYERS, 1.2F, 1.0F);
		AABB area = this.getBoundingBox().inflate(3.0);
		for (Entity e : level.getEntities(this, area, e -> e instanceof HauntEntity || e instanceof AnchorEntity)) {
			if (e instanceof AnchorEntity anchor && this.getOwner() instanceof ServerPlayer p) {
				anchor.purify(level, p);
			} else if (e instanceof HauntEntity haunt) {
				haunt.hurtServer(level, this.damageSources().thrown(this, this.getOwner()), 6.0F);
				haunt.stun(40);
				level.sendParticles(ModParticles.DEMON_SMOKE, haunt.getX(), haunt.getY() + 1, haunt.getZ(), 15, 0.3, 0.6, 0.3, 0.05);
				level.playSound(null, haunt.getX(), haunt.getY(), haunt.getZ(), ModSounds.HOLY_WATER_SIZZLE, SoundSource.HOSTILE, 1.5F, 1.0F);
			}
		}
		this.discard();
	}
}
