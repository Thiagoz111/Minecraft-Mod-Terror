#!/usr/bin/env bash
# Dev-only API probe. Prints filtered javap signatures / class names / source excerpts
# requested in tools/ci/probe-*.txt. Output is wrapped between markers.
set -u
JARS=$(find ~/.gradle/caches .gradle -name 'minecraft-*.jar' ! -name '*-sources.jar' 2>/dev/null | grep -i mapping | sort -u)
SRCS=$(find ~/.gradle/caches .gradle -name 'minecraft-*-sources.jar' 2>/dev/null | sort -u)
FJARS=$(find .gradle ~/.gradle/caches -path '*remapped*' -name 'fabric-*.jar' 2>/dev/null | sort -u)
[ -z "$FJARS" ] && FJARS=$(find ~/.gradle/caches -name 'fabric-*.jar' 2>/dev/null | sort -u)
JARS="$JARS
$FJARS"
CP=$(echo "$JARS" | tr '\n' ':')
echo "=== FJARS"; echo "$FJARS" | head -5
echo "=== PROBE BEGIN"
if [ -s tools/ci/probe-find.txt ]; then
  ALL=$(for j in $JARS; do unzip -Z1 "$j"; done | grep '\.class$' | grep -v '\$' | sed 's/\.class$//' | sort -u)
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    echo "=== FIND $pat"; echo "$ALL" | grep -E "$pat" | head -40
  done < tools/ci/probe-find.txt
fi
if [ -s tools/ci/probe-javap.txt ]; then
  while IFS='|' read -r cls pat; do
    cls="${cls#"${cls%%[![:space:]]*}"}"; cls="${cls%"${cls##*[![:space:]]}"}"
    pat="${pat#"${pat%%[![:space:]]*}"}"; pat="${pat%"${pat##*[![:space:]]}"}"
    [ -z "$cls" ] && continue
    echo "=== JAVAP $cls"
    MODE=-public; case "$cls" in *'#p') MODE=-p; cls="${cls%#p}";; esac
    if [ -z "$pat" ]; then javap -cp "$CP" $MODE "$cls" 2>&1 | grep -v '^Compiled from' | sed -E 's/net\.minecraft\.([a-z]+\.)*//g; s/java\.(lang|util)\.//g'
    else javap -cp "$CP" $MODE "$cls" 2>&1 | grep -E "$pat|^(public|abstract|final).*(class|interface|record|enum)" | sed -E 's/net\.minecraft\.([a-z]+\.)*//g; s/java\.(lang|util)\.//g'; fi
  done < tools/ci/probe-javap.txt
fi
if [ -s tools/ci/probe-src.txt ]; then
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    echo "=== SRC $p"
    for s in $SRCS; do unzip -p "$s" "$p" 2>/dev/null; done | grep -vE '^import |^package |^\s*$'
  done < tools/ci/probe-src.txt
fi
if [ -s tools/ci/probe-assets.txt ]; then
  # vanilla GUI assets: path, PNG size and the .mcmeta (gui scaling) of every match; never the images themselves
  for j in $(find ~/.gradle/caches .gradle -name 'minecraft-*.jar' 2>/dev/null | sort -u); do
    if unzip -Z1 "$j" 2>/dev/null | grep -q '^assets/minecraft/textures/gui/'; then CJ="$j"; break; fi
  done
  echo "=== ASSETS JAR $CJ"
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    echo "=== ASSETS $pat"
    unzip -Z1 "$CJ" | grep -E "$pat" | while IFS= read -r f; do
      case "$f" in
        *.png) dims=$(unzip -p "$CJ" "$f" | python3 -c 'import sys,struct; b=sys.stdin.buffer.read(24); print("%dx%d" % struct.unpack(">II", b[16:24]))'); echo "$f $dims";;
        *.mcmeta) echo "$f $(unzip -p "$CJ" "$f" | tr -d '\n\t ')";;
      esac
    done
  done < tools/ci/probe-assets.txt
fi
echo "=== PROBE END"
