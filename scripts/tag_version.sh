#!/bin/bash

# Read version from VERSION file
VERSION=$(cat VERSION)

# Confirm what will happen
echo "Tagging current commit as version $VERSION"

# Create annotated tag
git tag -a "v$VERSION" -m "Version $VERSION"

# Push the tag to GitHub
git push origin "v$VERSION"

echo "Done. Tagged and pushed version v$VERSION"
