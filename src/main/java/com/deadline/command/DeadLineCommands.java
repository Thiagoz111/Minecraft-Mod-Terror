package com.deadline.command;

import com.deadline.caseload.CaseManager;
import com.deadline.caseload.CaseRequest;
import com.deadline.caseload.CaseType;
import com.deadline.caseload.HunterData;
import com.deadline.net.Fx;
import com.deadline.registry.ModAttachments;
import com.deadline.sanity.SanityManager;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import java.util.Arrays;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * /deadline -- tools for creators filming the mod.
 * <pre>
 * /deadline call &lt;case&gt; [player]      ring the phone with a specific case
 * /deadline start &lt;case&gt; [player]     jump straight into a case
 * /deadline home [player]              leave the current case
 * /deadline sanity &lt;0-100&gt; [player]   set sanity
 * /deadline money &lt;amount&gt; [player]   add money
 * /deadline jumpscare &lt;entity&gt; [player]
 * /deadline kit [player]               full hunter kit
 * /deadline calls &lt;minSeconds&gt; &lt;maxSeconds&gt;  how often the phone rings
 * /deadline chapter &lt;n&gt;              replay a chapter of the scripted case from its checkpoint
 * /deadline beat &lt;id&gt;                 fire a scripted beat now
 * /deadline flag &lt;name&gt;               raise a director flag
 * /deadline voice on|off               allow / forbid capturing your voice (Simple Voice Chat)
 * </pre>
 */
public final class DeadLineCommands {
	private static final String[] SCARES = {"monja", "poseida", "sombra", "muneca", "anima"};

	private DeadLineCommands() {
	}

	public static void register(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx, Commands.CommandSelection env) {
		dispatcher.register(Commands.literal("deadline")
				.requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
				.then(Commands.literal("call")
						.then(Commands.argument("case", StringArgumentType.word()).suggests(DeadLineCommands::cases)
								.executes(c -> call(c, self(c)))
								.then(Commands.argument("player", EntityArgument.player()).executes(c -> call(c, EntityArgument.getPlayer(c, "player"))))))
				.then(Commands.literal("start")
						.then(Commands.argument("case", StringArgumentType.word()).suggests(DeadLineCommands::cases)
								.executes(c -> start(c, self(c)))
								.then(Commands.argument("player", EntityArgument.player()).executes(c -> start(c, EntityArgument.getPlayer(c, "player"))))))
				.then(Commands.literal("home")
						.executes(c -> home(self(c)))
						.then(Commands.argument("player", EntityArgument.player()).executes(c -> home(EntityArgument.getPlayer(c, "player")))))
				.then(Commands.literal("sanity")
						.then(Commands.argument("value", FloatArgumentType.floatArg(0, 100))
								.executes(c -> sanity(c, self(c)))
								.then(Commands.argument("player", EntityArgument.player()).executes(c -> sanity(c, EntityArgument.getPlayer(c, "player"))))))
				.then(Commands.literal("money")
						.then(Commands.argument("amount", IntegerArgumentType.integer())
								.executes(c -> money(c, self(c)))
								.then(Commands.argument("player", EntityArgument.player()).executes(c -> money(c, EntityArgument.getPlayer(c, "player"))))))
				.then(Commands.literal("jumpscare")
						.then(Commands.argument("entity", StringArgumentType.word()).suggests((c, b) -> SharedSuggestionProvider.suggest(SCARES, b))
								.executes(c -> scare(c, self(c)))
								.then(Commands.argument("player", EntityArgument.player()).executes(c -> scare(c, EntityArgument.getPlayer(c, "player"))))))
				.then(Commands.literal("kit")
						.executes(c -> kit(self(c)))
						.then(Commands.argument("player", EntityArgument.player()).executes(c -> kit(EntityArgument.getPlayer(c, "player")))))
				.then(Commands.literal("chapter")
						.then(Commands.argument("n", IntegerArgumentType.integer(1, 20)).executes(DeadLineCommands::chapter)))
				.then(Commands.literal("beat")
						.then(Commands.argument("id", StringArgumentType.greedyString()).executes(DeadLineCommands::beat)))
				.then(Commands.literal("flag")
						.then(Commands.argument("name", StringArgumentType.word()).executes(DeadLineCommands::flag)))
				.then(Commands.literal("voice")
						.then(Commands.literal("on").executes(c -> voice(c, false)))
						.then(Commands.literal("off").executes(c -> voice(c, true))))
				.then(Commands.literal("calls")
						.then(Commands.argument("min", IntegerArgumentType.integer(5))
								.then(Commands.argument("max", IntegerArgumentType.integer(5)).executes(DeadLineCommands::calls)))));
	}

	private static ServerPlayer self(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		return c.getSource().getPlayerOrException();
	}

	private static java.util.concurrent.CompletableFuture<com.mojang.brigadier.suggestion.Suggestions> cases(
			CommandContext<CommandSourceStack> c, com.mojang.brigadier.suggestion.SuggestionsBuilder b) {
		return SharedSuggestionProvider.suggest(Arrays.stream(CaseType.values()).map(CaseType::key), b);
	}

	private static CaseType parseCase(CommandContext<CommandSourceStack> c) {
		return CaseType.byKey(StringArgumentType.getString(c, "case"));
	}

	private static int call(CommandContext<CommandSourceStack> c, ServerPlayer p) {
		CaseType t = parseCase(c);
		CaseManager.ring(p, new CaseRequest(t, p.getRandom().nextInt(t.callers()), p.level().getGameTime()));
		c.getSource().sendSuccess(() -> Component.literal("Ring ring: " + t.key()), true);
		return 1;
	}

	private static int start(CommandContext<CommandSourceStack> c, ServerPlayer p) {
		HunterData d = ModAttachments.get(p);
		if (d.active != null) {
			CaseManager.returnHome(p, false);
		}
		CaseType t = parseCase(c);
		CaseManager.startCase(p, new CaseRequest(t, p.getRandom().nextInt(t.callers()), p.level().getGameTime()));
		return 1;
	}

	private static int home(ServerPlayer p) {
		CaseManager.returnHome(p, false);
		return 1;
	}

	private static int sanity(CommandContext<CommandSourceStack> c, ServerPlayer p) {
		SanityManager.set(p, FloatArgumentType.getFloat(c, "value"));
		return 1;
	}

	private static int money(CommandContext<CommandSourceStack> c, ServerPlayer p) {
		HunterData d = ModAttachments.get(p);
		d.money = Math.max(0, d.money + IntegerArgumentType.getInteger(c, "amount"));
		CaseManager.syncPhone(p, false);
		c.getSource().sendSuccess(() -> Component.literal("$" + d.money), false);
		return 1;
	}

	private static int scare(CommandContext<CommandSourceStack> c, ServerPlayer p) {
		Fx.jumpscare(p, StringArgumentType.getString(c, "entity"));
		return 1;
	}

	private static int chapter(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		ServerPlayer p = self(c);
		com.deadline.director.Run r = com.deadline.director.Director.of(p);
		if (r == null) {
			c.getSource().sendFailure(Component.literal("No scripted case running (use /deadline start colegio)"));
			return 0;
		}
		int n = IntegerArgumentType.getInteger(c, "n");
		r.jump(n, p);
		return 1;
	}

	private static int beat(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		ServerPlayer p = self(c);
		com.deadline.director.Run r = com.deadline.director.Director.of(p);
		com.deadline.director.Beat b = r == null ? null : r.compiled.find(StringArgumentType.getString(c, "id"));
		if (b == null) {
			c.getSource().sendFailure(Component.literal("Unknown beat"));
			return 0;
		}
		r.fire(b, p);
		return 1;
	}

	private static int flag(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		com.deadline.director.Run r = com.deadline.director.Director.of(self(c));
		if (r != null) {
			r.flag(StringArgumentType.getString(c, "name"));
		}
		return 1;
	}

	private static int voice(CommandContext<CommandSourceStack> c, boolean off) throws CommandSyntaxException {
		ServerPlayer p = self(c);
		com.deadline.voice.Voice.optOut(p, off);
		c.getSource().sendSuccess(() -> Component.literal(!com.deadline.voice.Voice.available()
				? "Simple Voice Chat is not installed"
				: off ? "Voice capture OFF (nothing is recorded)" : "Voice capture ON"), false);
		return 1;
	}

	private static int kit(ServerPlayer p) {
		CaseManager.giveKit(p, true);
		return 1;
	}

	private static int calls(CommandContext<CommandSourceStack> c) {
		int min = IntegerArgumentType.getInteger(c, "min");
		int max = Math.max(min, IntegerArgumentType.getInteger(c, "max"));
		CaseManager.callMinTicks = min * 20;
		CaseManager.callMaxTicks = max * 20;
		c.getSource().sendSuccess(() -> Component.literal("Calls every " + min + "-" + max + "s"), true);
		return 1;
	}
}
