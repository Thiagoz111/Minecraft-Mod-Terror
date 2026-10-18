#!/usr/bin/env bash
# Dev-only API probe. Prints filtered javap signatures / class names / source excerpts
# requested in tools/ci/probe-*.txt. Output is wrapped between markers.
set -u
JARS=$(find ~/.gradle/caches .gradle -name 'minecraft-*.jar' ! -name '*-sources.jar' 2>/dev/null | grep -i mapping | sort -u)
SRCS=$(find ~/.gradle/caches .gradle -name 'minecraft-*-sources.jar' 2>/dev/null | sort -u)
CP=$(echo "$JARS" | tr '\n' ':')
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
    cls=$(echo "$cls" | xargs); pat=$(echo "$pat" | xargs)
    [ -z "$cls" ] && continue
    echo "=== JAVAP $cls"
    if [ -z "$pat" ]; then javap -cp "$CP" -public "$cls" 2>&1 | grep -v '^Compiled from' | sed -E 's/net\.minecraft\.([a-z]+\.)*//g; s/java\.(lang|util)\.//g'
    else javap -cp "$CP" -public "$cls" 2>&1 | grep -E "$pat|^(public|abstract|final).*(class|interface|record|enum)" | sed -E 's/net\.minecraft\.([a-z]+\.)*//g; s/java\.(lang|util)\.//g'; fi
  done < tools/ci/probe-javap.txt
fi
if [ -s tools/ci/probe-src.txt ]; then
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    echo "=== SRC $p"
    for s in $SRCS; do unzip -p "$s" "$p" 2>/dev/null; done | grep -vE '^import |^package |^\s*$'
  done < tools/ci/probe-src.txt
fi
echo "=== PROBE END"
