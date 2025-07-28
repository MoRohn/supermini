#!/bin/bash
# Quick script to run SuperMini and check if it starts without errors

echo "Starting SuperMini..."
timeout 10s python3 supermini.py 2>&1 | grep -E "(ERROR|Exception|Traceback|Failed)" | head -20

if [ $? -eq 124 ]; then
    echo "✓ App ran for 10 seconds without crashing"
else
    echo "✗ App exited or had errors"
fi