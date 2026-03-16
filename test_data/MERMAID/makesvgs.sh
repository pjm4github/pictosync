#!/bin/bash
# generate_svgs.sh
# Converts all *.1.mermaid files in the current directory to SVGs
# Output files are named <basename>.svg

# Directory for output SVGs
OUTPUT_DIR="svg"
mkdir -p "$OUTPUT_DIR"

# Loop through all *.1.mermaid files
for FILE in *1.mermaid; do
    # Skip if no files match
    [ -e "$FILE" ] || continue

    # Extract base filename (remove the .1.mermaid part)
    BASENAME="${FILE%.mermaid}"
    OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}.svg"

    echo "Generating $OUTPUT_FILE from $FILE..."
    mmdc -i "$FILE" -o "$OUTPUT_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ $OUTPUT_FILE created successfully."
    else
        echo "❌ Failed to create $OUTPUT_FILE."
    fi
done

echo "All diagrams processed!"