# Omnix Play - Automated Playlist Generator

This project automatically generates and updates the `Omnix_play.m3u` playlist every 30 minutes with fresh access tokens.

## Files
- `all_channels.json`: The source data for TV channels.
- `convert_to_m3u.py`: The Python script that fetches a new token and creates the playlist.
- `.github/workflows/update_playlist.yml`: The automation script for GitHub Actions.
- `Omnix_play.m3u`: The generated playlist (output).

## Setup Instructions

1.  **Create a New Repository on GitHub:**
    *   Go to GitHub and create a new repository (e.g., `omnix-playlist`).
    *   Make sure it is **Public** (or Private, if you prefer).

2.  **Upload Files:**
    *   Upload all the files in this folder to your new repository.
    *   Ensure the structure looks like this:
        ```
        .github/workflows/update_playlist.yml
        all_channels.json
        convert_to_m3u.py
        README.md
        ```

3.  **Enable Actions (if needed):**
    *   Go to the "Actions" tab in your repository.
    *   You should see "Update Playlist" listed.
    *   It will run automatically every 30 minutes.
    *   You can also manually trigger it by clicking "Run workflow".

4.  **Get Your Playlist Link:**
    *   Once the action runs successfully, it will update `Omnix_play.m3u`.
    *   Your raw playlist link will be:
        `https://raw.githubusercontent.com/<YOUR_USERNAME>/<REPO_NAME>/main/Omnix_play.m3u`
    *   Use this link in your IPTV player. It will always have the latest valid tokens.
