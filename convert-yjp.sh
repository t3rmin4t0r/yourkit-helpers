#!/bin/bash
YJP_DIR=${YJP_HOME-/opt/yourkit}
for i in $*; do
	SNAP=$(basename $i .snapshot);
	TMP=$(mktemp -d)
	java -Dexport.xml -Dexport.call.tree.cpu -jar $YJP_DIR/lib/yjp.jar -export $i $TMP
	for xml in $TMP/Call*.xml; do
		mv $xml  $SNAP-$(basename $xml);
	done
	rm -r $TMP;
done
