package com.deadline.site;

import java.util.Optional;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.Property;

/**
 * Light fixtures the director and the nun switch: invisible light blocks, blocks with a LIT property and building-kit
 * pairs such as {@code colegio_arana} / {@code colegio_arana_apagada}.
 */
public final class Fixtures {
	private static final String[] OFF = {"_apagado", "_apagada", "_apagadas"};

	private Fixtures() {
	}

	/** The dark version of a fixture (air for light blocks), the state itself if already dark, null if not a fixture. */
	public static BlockState dark(BlockState s) {
		if (s.is(Blocks.LIGHT)) {
			return Blocks.AIR.defaultBlockState();
		}
		if (s.hasProperty(BlockStateProperties.LIT)) {
			return s.setValue(BlockStateProperties.LIT, false);
		}
		Identifier id = BuiltInRegistries.BLOCK.getKey(s.getBlock());
		for (String suf : OFF) {
			if (id.getPath().endsWith(suf)) {
				return s;
			}
		}
		for (String suf : OFF) {
			Optional<Block> b = BuiltInRegistries.BLOCK.getOptional(Identifier.fromNamespaceAndPath(id.getNamespace(), id.getPath() + suf));
			if (b.isPresent()) {
				return copy(s, b.get());
			}
		}
		return null;
	}

	/** The lit version of a fixture (the state itself when it has no lit form). */
	public static BlockState lit(BlockState s) {
		if (s.hasProperty(BlockStateProperties.LIT)) {
			return s.setValue(BlockStateProperties.LIT, true);
		}
		Identifier id = BuiltInRegistries.BLOCK.getKey(s.getBlock());
		for (String suf : OFF) {
			if (id.getPath().endsWith(suf)) {
				String path = id.getPath().substring(0, id.getPath().length() - suf.length());
				Optional<Block> b = BuiltInRegistries.BLOCK.getOptional(Identifier.fromNamespaceAndPath(id.getNamespace(), path));
				if (b.isPresent()) {
					return copy(s, b.get());
				}
			}
		}
		return s;
	}

	/** A lit fixture that can be put out (candles, chandeliers, lamps; not invisible light blocks). */
	public static boolean burning(BlockState s) {
		if (s.is(Blocks.LIGHT) || s.isAir()) {
			return false;
		}
		BlockState d = dark(s);
		return d != null && d != s;
	}

	private static BlockState copy(BlockState from, Block to) {
		BlockState st = to.defaultBlockState();
		for (Property<?> p : from.getProperties()) {
			if (st.hasProperty(p)) {
				st = with(st, from, p);
			}
		}
		return st;
	}

	private static <T extends Comparable<T>> BlockState with(BlockState st, BlockState from, Property<T> p) {
		return st.setValue(p, from.getValue(p));
	}
}
