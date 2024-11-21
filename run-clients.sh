#!/bin/bash

# Define the static path to the Python Tkinter app
app_path="./client/client.py"

# Start 10 instances in parallel, each with a unique instance number
for i in $(seq 1 12); do
    # Run each instance in the background with the instance number as an argument
    python3 "$app_path" "$i" &
    echo "Started instance $i of the client  app."
done

# Wait for all background processes to finish
wait
echo "All instances started."

