#!/usr/bin/env bash

mkdir -p test_results

# Run 2016 test
python ../run.py -i images/goal2016.png -o test_results/goal2016.jpg -l 60 100 175 -u 85 250 255
result2016=$(cmp --silent tests/images/goal2016.png test_results/goal2016.jpg || echo "1")

# Run 2017 test
python ../run.py -i images/goal2017.png -o test_results/goal2017.jpg -l 60 225 225 -u 70 255 255
result2017=$(cmp --silent tests/images/goal2016.png test_results/goal2016.jpg || echo "1")

result=$(echo "$result2016$result2017" | xargs)

if [ "$result" = "" ]
then
    echo "Test passed!"
    exit 0
else
    echo "Test failed!"
    exit 1
fi
