export myTerm=asthma

curl -L -o bootstrap.xml "http://connects.catalyst.harvard.edu/profiles/DIRECT.xml"
curl -L -o asthmaFromGuess.xml   "http://connects.catalyst.harvard.edu/profiles/DirectService.asp?Request=IncomingCount&SearchPhrase=$myTerm"

export queryUrlBS=`cat bootstrap.xml | grep "aggregate-query" | sed 's/.*http/http/;s/<.*//;s/&amp\;/\&/'`$myTerm
echo queryUrlBS from bootstrap is $queryUrlBS
curl -L -o asthmaFromBS.xml "$queryUrlBS"

export countBS=`cat asthmaFromBS.xml | grep "aggregation-result" | sed 's/.*<count>//;s/<.*//'`
if (( $countBS >= 0 )); then
    echo "---Count ($countBS) is non-zero"
else
    echo "---Count ($countBS) FAILS to be non-zero"
fi

if cmp -s "asthmaFromGuess.xml" "asthmaFromBS.xml"; then
    echo "---asthmaFromGuess.xml IS THE SAME as asthmaFromBS.xml"
else
    echo "---asthmaFromGuess.xml is NOT the same as asthmaFromBS.xml"
fi