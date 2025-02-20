#!/bin/bash

# Ensure that the script is being run with two arguments (e.g., major/minor/patch and a commit message)
if [ "$#" -ne 2 ]; then
  echo "Usage: sudo build.sh <major|minor|patch> <commit message>"
  exit 1
fi

# Assign arguments to variables
version_type=$1
commit_message=$2

# Step 1: Build Docker image
echo "Building Docker image..."
sudo docker build -t selenium-chrome .

if [ $? -eq 0 ]; then
  echo "Docker build succeeded."

  # Step 2: Find the latest version in CHANGELOG.md and determine new version number
  #current_version=$(grep -oP '(?<=## \[)[^]]+' CHANGELOG.md | head -n 1)
  # Get the current version from the latest version in CHANGELOG.md
  current_version=$(grep -oP '^## \[\K[^\]]+' CHANGELOG.md | head -n 1)

  echo "Current version: $current_version"

  # Split the version into its components (major, minor, patch)
  IFS='.' read -r major minor patch <<< "$current_version"

  case $version_type in
    major)
      # Increment the major version and reset minor and patch
      major=$((major + 1))
      minor=0
      patch=0
      ;;
    minor)
      # Increment the minor version and reset patch
      minor=$((minor + 1))
      patch=0
      ;;
    patch)
      # Increment the patch version
      patch=$((patch + 1))
      ;;
    *)
      echo "Invalid version type. Use major, minor, or patch."
      exit 1
      ;;
  esac

  # Format the new version number
  new_version="${major}.${minor}.${patch}"
  echo "New version: $new_version"

  # Step 4: Update CHANGELOG.md
  echo "Updating CHANGELOG.md..."
  { 
    echo -e "## [$new_version] - $(date +%Y-%m-%d)"
    echo "- $commit_message"
    cat CHANGELOG.md
  } > temp_changelog && mv temp_changelog CHANGELOG.md
  git add CHANGELOG.md
  git commit -m "$new_version: $commit_message"
  git push

  # Step 5: Run Docker image prune to clean up unused images
  echo "Cleaning up Docker images..."
  sudo docker image prune -f

else
  echo "Docker build failed. Exiting..."
  exit 1
fi
