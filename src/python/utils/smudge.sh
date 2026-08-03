#!/bin/bash
# Get the latest commit metadata for the current file
# $1 is passed by Git as the filename
USER=$(git log -1 --format="%an" -- "$1" 2>/dev/null || echo "Unknown User")
DATE=$(git log -1 --format="%ad" --date=short -- "$1" 2>/dev/null || echo "Unknown Date")
VERSION=$(git describe --tags --always 2>/dev/null || echo "No Version")

sed -e "s/\$UserName\$/\$UserName: $USER\$/g" \
    -e "s/\$CommitTime\$/\$CommitTime: $DATE\$/g" \
    -e "s/\$Version\$/\$Version: $VERSION\$/g"

