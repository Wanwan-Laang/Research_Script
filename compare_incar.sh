#!/bin/bash

# here I just want to compare the INCAR files in two folders. 

# check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <folder1> <folder2>"
    exit 1
fi

folder1=$1
folder2=$2
any_difference=0 

# search for subdirectories 
for subdir1 in "$folder1"/iter.000.*; do
    if [ -d "$subdir1" ]; then
        # check if the corresponding subdirectory exists in the second folder
        subname=$(basename "$subdir1")
        subdir2="$folder2/$subname"

        if [ -d "$subdir2" ]; then
            incar1="$subdir1/INCAR"
            incar2="$subdir2/INCAR"

            # check if both INCAR files exist
            if [ -f "$incar1" ] && [ -f "$incar2" ]; then
                # compare the two INCAR files
                if ! cmp -s "$incar1" "$incar2"; then
                    echo "Difference found in: $subname"
                    any_difference=1
                fi
            else
                echo "Missing INCAR in one of the directories: $subname"
                any_difference=1
            fi
        else
            echo "Missing subdirectory: $subname in $folder2"
            any_difference=1
        fi
    fi
done

# print and tell if all INCAR files are identical
if [ "$any_difference" -eq 0 ]; then
    echo "All INCAR files are identical across corresponding subdirectories."
fi
