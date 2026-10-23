package com.deadline.horror.casa.dog;

import com.deadline.casa.FamilyEntity;
import com.deadline.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Choripán, the family dachshund (docs/design/casa_terror.md 7): "el que avisa". At first a dog -- asleep under the
 * table, sitting, growling low at the Nona -- and then the thing that stands at the back of the patio on its hind legs
 * like a person and stares at the house ({@link #POSE_STAND}, look {@link #LOOK_MUERTO}).
 * <p>A {@link FamilyEntity} (scripted actor: no AI of its own, cannot be hurt or pushed, {@link #walkTo}, {@link #face},
 * {@link #watch}); the client model is {@code ChoripanModel} (tools/models/ent_choripan.py), textures by look:
 * 0 choripan.png, 1 choripan_bufanda.png, 2 choripan_muerto.png (+ their _eyes layers).
 * <ul>
 *   <li>Poses ({@link #setAction}): {@link #POSE_IDLE} on four legs, {@link #POSE_SIT}, {@link #POSE_SLEEP},
 *   {@link #POSE_GROWL} (head low at whatever {@link #watch} points it to -- the Nona -- with the lip up, a low growl
 *   every few seconds), {@link #POSE_STAND} (upright, front legs hanging, head tilted, perfectly still: the head does
 *   not follow anybody). {@link #POSE_WALK} / {@link #POSE_RUN} are the gaits; {@link #trot} and {@link #dash} set them
 *   for the walk and put the previous pose back on arrival.</li>
 * </ul>
 */
public class ChoripanEntity extends FamilyEntity {
	public static final int POSE_IDLE = 0, POSE_SIT = 1, POSE_SLEEP = 2, POSE_GROWL = 3, POSE_STAND = 4, POSE_WALK = 5, POSE_RUN = 6;
	public static final int LOOK_NORMAL = 0, LOOK_BUFANDA = 1, LOOK_MUERTO = 2;

	/** Pose to go back to when a {@link #trot} / {@link #dash} arrives (-1: none pending). */
	private int afterWalk = -1;
	private int soundCd = 40;

	public ChoripanEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.propSounds = false;
	}

	@Override
	public boolean isPossessed() {
		return this.variant() == LOOK_MUERTO;
	}

	/** The dead dog chills you; the family dog does not. */
	@Override
	public float fearAura() {
		return this.variant() == LOOK_MUERTO ? 0.5F : 0F;
	}

	// ------------------------------------------------------------------ walking with a gait
	/** Walks there at a dachshund trot (gait {@link #POSE_WALK}); the current pose comes back on arrival. */
	public boolean trot(Vec3 target) {
		return this.gait(target, POSE_WALK, 1.0);
	}

	/** Runs there (gait {@link #POSE_RUN}, ears streaming); the current pose comes back on arrival. */
	public boolean dash(Vec3 target) {
		return this.gait(target, POSE_RUN, 2.2);
	}

	private boolean gait(Vec3 target, int gait, double speed) {
		int now = this.action();
		if (now != POSE_WALK && now != POSE_RUN) {
			this.afterWalk = now == POSE_STAND || now == POSE_SLEEP || now == POSE_SIT ? POSE_IDLE : now;
		}
		this.setAction(gait);
		this.watchPlayers(true);
		return this.walkTo(target, speed);
	}

	/** Sets a pose and does what it implies for the head: in STAND it is fixed (he stares where the body points). */
	public void pose(int pose) {
		this.afterWalk = -1;
		this.setAction(pose);
		this.watchPlayers(pose != POSE_STAND && pose != POSE_SLEEP);
		if (pose == POSE_STAND || pose == POSE_SLEEP) {
			this.watch(null);
		}
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		int a = this.action();
		if (this.afterWalk >= 0 && !this.isWalking() && (a == POSE_WALK || a == POSE_RUN)) {
			this.setAction(this.afterWalk);
			this.afterWalk = -1;
			a = this.action();
		}
		if (a == POSE_STAND) {
			// perfectly still: no head turning, the body never drifts off the yaw the script gave it
			this.setYHeadRot(this.getYRot());
			this.setXRot(0F);
		}
		if (--this.soundCd > 0) {
			return;
		}
		if (a == POSE_GROWL) {
			this.soundCd = 45 + this.random.nextInt(40);
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.CHORIPAN_GROWL_LOW, SoundSource.NEUTRAL, 0.55F,
					0.85F + this.random.nextFloat() * 0.1F);
		} else if (a == POSE_STAND && this.variant() == LOOK_MUERTO) {
			this.soundCd = 160 + this.random.nextInt(120);
			level.playSound(null, this.getX(), this.getY() + 0.8, this.getZ(), ModSounds.APARICION_PERRO_RESPIRA, SoundSource.HOSTILE, 0.5F,
					0.9F + this.random.nextFloat() * 0.1F);
		} else {
			this.soundCd = 40;
		}
	}

	/** The head follows this entity (the Nona while growling at her); null: back to the nearest hunter. */
	@Override
	public void watch(Entity target) {
		super.watch(target);
	}
}
