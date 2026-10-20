package com.deadline.voice.svc;

import com.deadline.DeadLine;
import de.maxhenkel.voicechat.api.VoicechatApi;
import de.maxhenkel.voicechat.api.VoicechatPlugin;
import de.maxhenkel.voicechat.api.events.EventRegistration;
import de.maxhenkel.voicechat.api.events.MicrophonePacketEvent;
import de.maxhenkel.voicechat.api.events.VoicechatServerStartedEvent;

/** Simple Voice Chat entrypoint ("voicechat" in fabric.mod.json); only loaded when that mod is installed. */
public class DeadLineVoicechatPlugin implements VoicechatPlugin {
	@Override
	public String getPluginId() {
		return DeadLine.MOD_ID;
	}

	@Override
	public void initialize(VoicechatApi api) {
		SvcBackend.install(api);
		DeadLine.LOGGER.info("DEAD LINE: Simple Voice Chat found, the dead can hear you now");
	}

	@Override
	public void registerEvents(EventRegistration registration) {
		registration.registerEvent(VoicechatServerStartedEvent.class, e -> SvcBackend.serverStarted(e.getVoicechat()));
		registration.registerEvent(MicrophonePacketEvent.class, SvcBackend::onMic);
	}
}
