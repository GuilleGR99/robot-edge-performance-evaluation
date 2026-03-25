#!/bin/bash

nodes=$(rosnode list)

for node in $nodes
do
    echo "========================================"
    echo "NODE: $node"
    echo "----------------------------------------"
    rosnode info $node
    echo ""
done
