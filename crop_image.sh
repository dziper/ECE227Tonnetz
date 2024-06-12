#!/bin/bash

# Define input and output directories
input_dir="analysis/tonnetzImages"
output_dir="analysis/croppedImages"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Process each .png file in the input directory
for input_image in "$input_dir"/*.png; do
    # Get the filename without the directory path
    filename=$(basename "$input_image")

    # Define the output image path
    output_image="$output_dir/$filename"

    # Get the dimensions of the input image
    width=$(identify -format "%w" "$input_image")
    height=$(identify -format "%h" "$input_image")

    if [ "$height" -lt 750 ]; then
        echo "Skipping $input_image: The height of the image is less than 750 pixels. Cropping would result in a negative height."
        continue
    fi

    # Crop the image
    convert "$input_image" -crop "${width}x600+0+150" "$output_image"

    echo "Cropped $input_image and saved to $output_image"
done

echo "All images processed successfully."
