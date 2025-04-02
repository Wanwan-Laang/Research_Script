#!/bin/bash

# === 設定路徑 ===
SRC_DIR="../04.pre-adsorption_sites"
TEMPLATE_DIR="00.prepared-vasp-files"
TARGET_DIR=$(pwd)

rm -f mapping.log
touch mapping.log

for site_type in ontop bridge hollow; do
    folder="$SRC_DIR/adsorption_${site_type}"
    if [ -d "$folder" ]; then
        echo "📂 Processing $site_type ..."
        counter=1

        mkdir -p "$site_type"

        for vaspfile in $(ls "$folder"/*.vasp | sort -V); do
            subfolder=$(printf "%02d" "$counter")
            fullpath="$site_type/$subfolder"

            mkdir -p "$fullpath"

            cp -r "$TEMPLATE_DIR"/* "$fullpath"/
            cp "$vaspfile" "$fullpath/POSCAR"

            echo "$site_type/$subfolder ← $(basename "$vaspfile")  [$site_type]" >> mapping.log

            ((counter++))
        done
    else
        echo "⚠️  Warning: $folder does not exist."
    fi
done

echo "✅ All VASP input folders organized by site type."
echo "📝 Mapping log written to: mapping.log"
