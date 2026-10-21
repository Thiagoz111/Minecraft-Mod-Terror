package com.deadline.casa;

import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * A blessed choripán in flight (a copy of the holy water flask). A {@link Catcher} (the demon dog's head) within
 * {@link #CATCH_RADIUS} blocks snatches it out of the air; anything else it hits gets a holy splash that stuns haunts
 * for {@link #STUN_TICKS} (event "choripan:splash").
 */
public class ChoripanBenditoEntity extends ThrowableItemProjectile {
	public static final double CATCH_RADIUS = 2.0;
	public static final int STUN_TICKS = 40;

	/** Something that snatches a blessed choripán out of the air (the demon dog's head). */
	public interface Catcher {
		/**
		 * The choripán passed within {@link #CATCH_RADIUS} blocks of this entity's bounding box centre (or hit it).
		 * Return true to take it: it then vanishes without splashing (the catcher plays the chomp).
		 */
		boolean catchChoripan(ChoripanBenditoEntity choripan);
	}

	private boolean caught;

	public ChoripanBenditoEntity(EntityType<? extends ChoripanBenditoEntity> type, Level level) {
		super(type, level);
	}

	public ChoripanBenditoEntity(Level level, LivingEntity owner, ItemStack stack) {
		super(CasaItems.CHORIPAN_BENDITO_ENTITY, owner, level, stack);
	}

	@Override
	protected Item getDefaultItem() {
		return CasaItems.CHORIPAN_BENDITO;
	}

	public boolean isCaught() {
		return caught;
	}

	/** Removes it quietly: somebody ate it. */
	public void consume() {
		caught = true;
		if (!this.isRemoved()) {
			this.discard();
		}
	}

	@Override
	public void tick() {
		if (!caught && this.level() instanceof ServerLevel level && offer(level)) {
			return;
		}
		super.tick();
		if (this.level().isClientSide() && !this.isRemoved() && this.tickCount % 2 == 0) {
			this.level().addParticle(ModParticles.HOLY_SPARK, this.getX(), this.getY() + 0.1, this.getZ(), 0, 0.01, 0);
		}
	}

	/** Offers itself to every catcher close enough; true when one took it. */
	private boolean offer(ServerLevel level) {
		Vec3 here = this.position();
		for (Entity e : level.getEntities(this, this.getBoundingBox().inflate(CATCH_RADIUS + 1.0), e -> e instanceof Catcher && e.isAlive())) {
			if (e.getBoundingBox().getCenter().distanceTo(here) <= CATCH_RADIUS && ((Catcher) e).catchChoripan(this)) {
				consume();
				return true;
			}
		}
		return false;
	}

	@Override
	protected void onHit(HitResult hit) {
		if (caught) {
			return;
		}
		if (hit instanceof EntityHitResult eh && eh.getEntity() instanceof Catcher c && c.catchChoripan(this)) {
			consume();
			return;
		}
		super.onHit(hit);
		if (!(this.level() instanceof ServerLevel level) || this.isRemoved()) {
			return;
		}
		double x = this.getX(), y = this.getY(), z = this.getZ();
		level.sendParticles(ParticleTypes.SPLASH, x, y + 0.2, z, 30, 0.5, 0.2, 0.5, 0.3);
		level.sendParticles(ModParticles.HOLY_SPARK, x, y + 0.3, z, 24, 0.6, 0.4, 0.6, 0.08);
		level.playSound(null, x, y, z, ModSounds.HOLY_WATER_SPLASH, SoundSource.PLAYERS, 1.0F, 1.3F);
		for (Entity e : level.getEntities(this, this.getBoundingBox().inflate(2.5), e -> e instanceof HauntEntity)) {
			HauntEntity h = (HauntEntity) e;
			h.stun(STUN_TICKS);
			level.sendParticles(ModParticles.DEMON_SMOKE, h.getX(), h.getY() + h.getBbHeight() * 0.6, h.getZ(), 10, 0.3, 0.4, 0.3, 0.04);
			level.playSound(null, h.getX(), h.getY(), h.getZ(), ModSounds.HOLY_WATER_SIZZLE, SoundSource.HOSTILE, 1.2F, 1.1F);
		}
		CasaItems.post(level, this.position(), "choripan:splash");
		this.discard();
	}
}
