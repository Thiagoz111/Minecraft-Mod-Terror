package com.deadline.horror;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * Creator/debug tools for the horror director.
 * <pre>
 * /deadline horror status          act, tension, phase, last and running events
 * /deadline horror event &lt;id&gt;      fire an event now (ignores its conditions)
 * /deadline horror act &lt;n&gt;         jump to an act (the case script reacts to the "act:&lt;n&gt;" event)
 * /deadline horror tension &lt;0-100&gt;
 * /deadline horror pause           pause / resume random events
 * </pre>
 */
public final class HorrorCommands {
	private HorrorCommands() {
	}

	public static void register(CommandDispatcher<CommandSourceStack> d) {
		d.register(Commands.literal("deadline")
				.requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
				.then(Commands.literal("horror")
						.then(Commands.literal("status").executes(HorrorCommands::status))
						.then(Commands.literal("event")
								.then(Commands.argument("id", StringArgumentType.word())
										.suggests((c, b) -> SharedSuggestionProvider.suggest(HorrorEvents.ids("casa"), b))
										.executes(HorrorCommands::event)))
						.then(Commands.literal("act")
								.then(Commands.argument("n", IntegerArgumentType.integer(0, 6)).executes(HorrorCommands::act)))
						.then(Commands.literal("tension")
								.then(Commands.argument("v", FloatArgumentType.floatArg(0F, 100F)).executes(HorrorCommands::tension)))
						.then(Commands.literal("pause").executes(HorrorCommands::pause))));
	}

	private static Haunt haunt(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		Run r = Director.of(p);
		if (r == null) {
			c.getSource().sendFailure(Component.literal("No case running"));
			return null;
		}
		return Haunt.of(r);
	}

	private static int status(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		Haunt h = haunt(c);
		if (h == null) {
			return 0;
		}
		String s = h.status();
		c.getSource().sendSuccess(() -> Component.literal(s), false);
		return 1;
	}

	private static int event(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		Haunt h = haunt(c);
		if (h == null) {
			return 0;
		}
		String id = StringArgumentType.getString(c, "id");
		boolean ok = h.fire(id, c.getSource().getPlayerOrException(), false) != null;
		c.getSource().sendSuccess(() -> Component.literal((ok ? "Fired " : "Could not fire ") + id), false);
		return ok ? 1 : 0;
	}

	private static int act(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		Haunt h = haunt(c);
		if (h == null) {
			return 0;
		}
		int n = IntegerArgumentType.getInteger(c, "n");
		h.stopAll();
		h.act(n);
		h.run.post("act:" + n);
		c.getSource().sendSuccess(() -> Component.literal("Act " + n), true);
		return 1;
	}

	private static int tension(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		Haunt h = haunt(c);
		if (h == null) {
			return 0;
		}
		h.tension(FloatArgumentType.getFloat(c, "v"));
		return 1;
	}

	private static int pause(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		Haunt h = haunt(c);
		if (h == null) {
			return 0;
		}
		h.pause(!h.paused());
		boolean p = h.paused();
		c.getSource().sendSuccess(() -> Component.literal(p ? "Horror paused" : "Horror running"), false);
		return 1;
	}
}
