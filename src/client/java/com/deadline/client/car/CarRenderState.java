package com.deadline.client.car;

import com.deadline.client.render.HauntRenderState;

/** Render state of the car (extends the creature state so the generated model base can be reused). */
public class CarRenderState extends HauntRenderState {
	/** Wheel roll, radians (distance / wheel radius). */
	public float wheelSpin;
	/** Steering, -1 (right) .. 1 (left). */
	public float steer;
	public boolean lightsOn;
	public boolean engineOn;
}
