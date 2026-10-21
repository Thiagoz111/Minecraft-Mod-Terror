package com.deadline.director;

/** A scripted case (chapters, beats and the custom logic of its set pieces). */
public abstract class CaseScript {
	/** Key of data/deadline/sites/&lt;key&gt;.json. */
	public abstract String siteKey();

	public abstract void define(Script s);

	/** Called every tick for the run (custom mechanics that are not beats). */
	public void tick(Run run) {
	}

	/** Called when a hunter (re)enters the case at a chapter checkpoint. */
	public void onCheckpoint(Run run, net.minecraft.server.level.ServerPlayer p) {
	}

	/** Called when a hunter leaves the case (solved, abandoned or sent home). */
	public void onLeave(Run run, net.minecraft.server.level.ServerPlayer p) {
	}
}
