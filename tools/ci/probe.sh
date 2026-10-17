#!/usr/bin/env bash
# Prints class lists, javap signatures and decompiled sources requested in tools/ci/probe-*.txt
set -u
JARS=$(find ~/.gradle/caches .gradle -name 'minecraft-*.jar' ! -name '*-sources.jar' 2>/dev/null | grep -i mapping | sort -u)
SRCS=$(find ~/.gradle/caches .gradle -name 'minecraft-*-sources.jar' 2>/dev/null | sort -u)
echo "JARS:"; echo "$JARS"; echo "SRCS:"; echo "$SRCS"
CP=$(echo "$JARS" | tr '\n' ':')
if [ -s tools/ci/probe-list.txt ]; then
  while read -r pfx; do
    [ -z "$pfx" ] && continue
    echo "=== LIST $pfx"
    for j in $JARS; do unzip -Z1 "$j" | grep "^$pfx" | grep -v '\$' | sed 's/\.class$//'; done | sort -u
  done < tools/ci/probe-list.txt
fi
if [ -s tools/ci/probe-javap.txt ]; then
  while read -r cls; do
    [ -z "$cls" ] && continue
    echo "=== JAVAP $cls"
    javap -cp "$CP" -public "$cls" 2>&1 | grep -v '^Compiled from'
  done < tools/ci/probe-javap.txt
fi
if [ -s tools/ci/probe-src.txt ]; then
  while read -r p; do
    [ -z "$p" ] && continue
    echo "=== SRC $p"
    for s in $SRCS; do unzip -p "$s" "$p" 2>/dev/null; done | grep -v '^import ' 
  done < tools/ci/probe-src.txt
fi
if [ -s tools/ci/probe-grep.txt ]; then
  TMP=$(mktemp -d); for s in $SRCS; do unzip -q -o "$s" -d "$TMP"; done
  while read -r pat; do
    [ -z "$pat" ] && continue
    echo "=== GREP $pat"
    grep -rnE "$pat" "$TMP" | sed "s#$TMP/##" | head -60
  done < tools/ci/probe-grep.txt
fi
echo "=== PROBE DONE"
