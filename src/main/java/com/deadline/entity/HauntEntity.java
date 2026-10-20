package com.deadline.entity;

import com.deadline.caseload.CaseManager;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.sanity.SanityManager;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * Base for every paranormal entity.
 * <ul>
 *   <li>While its anchor (cursed object) is intact it shrugs off most damage.</li>
 *   <li>It cannot be killed by damage: at 25% health it becomes <b>weakened</b> and must be banished
 *   (spirit jar or exorcism).</li>
 *   <li>Crucifix / camera flash stun it; holy water and the silver dagger hurt it more.</li>
 *   <li>It drains the sanity of nearby hunters.</li>
 * </ul>
 */
public abstract class HauntEntity extends Monster {
	/** Dev/screenshot mode: freezes special behaviours so creatures can be photographed. Never set in normal play. */
	public static boolean SHOWCASE = false;
	/** Driven by a director beat: no AI of its own (the script moves it and sets its pose). */
	public boolean scripted;

	private static final EntityDataAccessor<Boolean> WEAKENED = SynchedEntityData.defineId(HauntEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Boolean> ANCHORED = SynchedEntityData.defineId(HauntEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Integer> STUN = SynchedEntityData.defineId(HauntEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> ACTION = SynchedEntityData.defineId(HauntEntity.class, EntityDataSerializers.INT);

	/** Case site this entity belongs to, -1 when spawned freely (spawn egg / command). */
	protected int siteIndex = -1;
	private boolean stunSetNoAi;
	protected int ambientCooldown;

	protected HauntEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.setPersistenceRequired();
		this.xpReward = 30;
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(WEAKENED, false);
		builder.define(ANCHORED, false);
		builder.define(STUN, 0);
		builder.define(ACTION, 0);
	}

	// ------------------------------------------------------------------ state
	public boolean isWeakened() {
		return this.entityData.get(WEAKENED);
	}

	public void setWeakened(boolean v) {
		this.entityData.set(WEAKENED, v);
	}

	public boolean isAnchored() {
		return this.entityData.get(ANCHORED);
	}

	public void setAnchored(boolean v) {
		this.entityData.set(ANCHORED, v);
	}

	public boolean isStunned() {
		return this.entityData.get(STUN) > 0;
	}

	public int stunTicks() {
		return this.entityData.get(STUN);
	}

	/** Free-form animation/behaviour id synced to the client (meaning depends on subclass). */
	public int action() {
		return this.entityData.get(ACTION);
	}

	public void setAction(int a) {
		this.entityData.set(ACTION, a);
	}

	public void stun(int ticks) {
		if (ticks > this.stunTicks()) {
			this.entityData.set(STUN, ticks);
		}
		this.getNavigation().stop();
		this.setDeltaMovement(Vec3.ZERO);
	}

	public int siteIndex() {
		return siteIndex;
	}

	public void setSiteIndex(int site) {
		this.siteIndex = site;
	}

	/** Banishing this entity requires an exorcism instead of the spirit jar. */
	public boolean requiresExorcism() {
		return false;
	}

	/** Damage multiplier for holy sources (holy water, crucifix, dagger). */
	public float holyWeakness() {
		return 1.0F;
	}

	/** Sanity drained per second from a hunter within 8 blocks. */
	public float fearAura() {
		return 0.6F;
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		super.tick();
		Level level = this.level();
		if (level.isClientSide()) {
			clientEffects();
			return;
		}
		int stun = this.stunTicks();
		if (stun > 0) {
			this.entityData.set(STUN, stun - 1);
			if (!this.isNoAi() && stun > 1) {
				this.setNoAi(true);
				this.stunSetNoAi = true;
			}
			this.getNavigation().stop();
			this.setDeltaMovement(this.getDeltaMovement().multiply(0.2, 1.0, 0.2));
			if (stun == 1 && this.stunSetNoAi) {
				this.setNoAi(false);
				this.stunSetNoAi = false;
			}
		}
		if (this.isWeakened() && this.tickCount % 10 == 0 && level instanceof ServerLevel server) {
			server.sendParticles(ModParticles.ECTOPLASM, this.getX(), this.getY() + this.getBbHeight() * 0.6, this.getZ(), 3, 0.3, 0.4, 0.3, 0.01);
		}
		if (this.tickCount % 20 == 0 && level instanceof ServerLevel server) {
			for (ServerPlayer p : server.players()) {
				if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < 64) {
					SanityManager.add(p, -this.fearAura() * (this.isWeakened() ? 0.4F : 1.0F));
				}
			}
		}
	}

	/** Client-only ambient particles. */
	protected void clientEffects() {
		if (this.isAnchored() && this.random.nextInt(6) == 0) {
			this.level().addParticle(ModParticles.DEMON_SMOKE, this.getRandomX(0.6), this.getRandomY(), this.getRandomZ(0.6), 0, 0.02, 0);
		}
		if (this.isStunned() && this.random.nextInt(2) == 0) {
			this.level().addParticle(ModParticles.HOLY_SPARK, this.getRandomX(0.8), this.getRandomY(), this.getRandomZ(0.8), 0, 0.03, 0);
		}
	}

	// ------------------------------------------------------------------ damage
	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		Entity attacker = source.getEntity();
		boolean holy = source.getDirectEntity() instanceof HolyWaterEntity;
		if (attacker instanceof LivingEntity living && living.getMainHandItem().is(ModItems.SILVER_DAGGER)) {
			holy = true;
		}
		if (holy) {
			amount *= 1.8F * holyWeakness();
		}
		if (this.isAnchored()) {
			amount *= 0.15F;
			level.sendParticles(ParticleTypes.LARGE_SMOKE, this.getX(), this.getY() + 1, this.getZ(), 6, 0.3, 0.5, 0.3, 0.02);
			if (attacker instanceof ServerPlayer player && this.random.nextInt(3) == 0) {
				player.displayClientMessage(net.minecraft.network.chat.Component.translatable("deadline.msg.anchored"), true);
			}
		}
		if (this.isWeakened()) {
			// Already beaten: only flinches.
			this.stun(10);
			return false;
		}
		float floor = this.getMaxHealth() * (this.isAnchored() ? 0.5F : 0.25F);
		if (this.getHealth() - amount <= floor) {
			boolean result = super.hurtServer(level, source, Math.max(0, this.getHealth() - floor));
			this.setHealth(Math.max(1.0F, floor));
			if (!this.isAnchored()) {
				this.becomeWeakened(level);
			}
			return result;
		}
		return super.hurtServer(level, source, amount);
	}

	protected void becomeWeakened(ServerLevel level) {
		if (this.isWeakened()) {
			return;
		}
		this.setWeakened(true);
		this.setTarget(null);
		this.stun(60);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), this.getHurtSoundEvent(), SoundSource.HOSTILE, 2.0F, 0.6F);
		CaseManager.onBossWeakened(this);
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(this) < 48 * 48) {
				Fx.shake(p, 0.6F, 20);
				p.displayClientMessage(net.minecraft.network.chat.Component.translatable(
						this.requiresExorcism() ? "deadline.msg.weakened_exorcism" : "deadline.msg.weakened_jar"), true);
			}
		}
	}

	/** Called when the entity is banished (jar / exorcism). */
	public void banish(ServerLevel level, Player by) {
		level.sendParticles(ModParticles.WISP, this.getX(), this.getY() + 1, this.getZ(), 40, 0.5, 0.8, 0.5, 0.15);
		level.sendParticles(ParticleTypes.END_ROD, this.getX(), this.getY() + 1, this.getZ(), 30, 0.2, 0.4, 0.2, 0.12);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), this.getDeathSoundEvent(), SoundSource.HOSTILE, 2.0F, 1.0F);
		CaseManager.onBossBanished(this, by);
		this.discard();
	}

	public abstract SoundEvent getHurtSoundEvent();

	public abstract SoundEvent getDeathSoundEvent();

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return getHurtSoundEvent();
	}

	@Override
	protected SoundEvent getDeathSound() {
		return getDeathSoundEvent();
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return false;
	}

	@Override
	public boolean doHurtTarget(ServerLevel level, Entity target) {
		boolean hit = super.doHurtTarget(level, target);
		if (hit && target instanceof ServerPlayer player) {
			SanityManager.add(player, -6.0F);
			Fx.redFlash(player, 0.6F);
		}
		return hit;
	}

	// ------------------------------------------------------------------ helpers
	/** True when the given player is looking roughly at this entity with clear line of sight. */
	public boolean isWatchedBy(LivingEntity player, double tolerance) {
		return this.isLookingAtMe(player, tolerance, true, false, this.getEyeY(), this.getY() + this.getBbHeight() * 0.5);
	}

	/** Teleports to a random valid standing spot around a point. */
	protected boolean teleportNear(Vec3 center, double minR, double maxR) {
		for (int i = 0; i < 16; i++) {
			double a = this.random.nextDouble() * Math.PI * 2;
			double r = Mth.lerp(this.random.nextDouble(), minR, maxR);
			double x = center.x + Math.cos(a) * r;
			double z = center.z + Math.sin(a) * r;
			for (int dy = 3; dy >= -4; dy--) {
				double y = Math.floor(center.y) + dy;
				net.minecraft.core.BlockPos pos = net.minecraft.core.BlockPos.containing(x, y, z);
				if (this.level().getBlockState(pos.below()).isSolid()
						&& this.level().noCollision(this, this.getBoundingBox().move(x - this.getX(), pos.getY() - this.getY(), z - this.getZ()))
						&& !SaltGuard.blocked(this.level(), pos)) {
					this.teleportTo(x, pos.getY(), z);
					this.getNavigation().stop();
					return true;
				}
			}
		}
		return false;
	}

	/** Teleports behind a target, outside its view. */
	protected boolean teleportBehind(LivingEntity target, double dist) {
		Vec3 look = target.getLookAngle();
		Vec3 behind = target.position().subtract(look.x * dist, 0, look.z * dist);
		return teleportNear(behind, 0.0, 2.0);
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		super.addAdditionalSaveData(out);
		out.putInt("Site", this.siteIndex);
		out.putBoolean("Weakened", this.isWeakened());
		out.putBoolean("Anchored", this.isAnchored());
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		super.readAdditionalSaveData(in);
		this.siteIndex = in.getIntOr("Site", -1);
		this.setWeakened(in.getBooleanOr("Weakened", false));
		this.setAnchored(in.getBooleanOr("Anchored", false));
	}
}
