package com.deadline.client.render;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Render state shared by every DEAD LINE creature. */
public class HauntRenderState extends LivingEntityRenderState {
	public int action;
	public boolean weakened;
	public boolean stunned;
	public boolean anchored;
	public boolean climbing;
	public boolean revealed;
	public float attackAnim;
	public float speed;
	public int seed;
	public int variant;
}
