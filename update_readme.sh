#!/bin/zsh

# Script to automatically cherry-pick the last commit affecting README.md
# from profile-assets branch to main branch

source ~/.zshrc

# Navigate to your repository's directory if not already there
cd ~/danielcalbick/Misc_codingProjects/danielcalbick

# Push changes to the profile-assets repo
git add -A 
git reset README.md
git commit -m 'Syncing local and remote'; git push

# Push readme by itself
git add README.md 
git commit -m 'Updated README.md'; git push

# Fetch the latest changes from remote
git fetch origin

# Find the latest commit hash affecting README.md in profile-assets branch
latest_commit=$(git log profile-assets -- README.md -n 1 --pretty=format:"%H")

# Checkout the main branch
git checkout main

# Pull the latest changes
git pull origin main

# Cherry-pick the commit
git cherry-pick $latest_commit

# Push changes to the remote main branch
git push origin main

git checkout profile-assets