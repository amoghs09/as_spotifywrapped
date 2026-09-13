"""
Spotify Wrapped
Usage:
    python wrapped.py Streaming_History_Audio_2026.json
"""

import json
import sys
from collections import defaultdict
 
# A "play" only counts if the track was listened to for at least 30 seconds
MIN_MS_PLAYED = 30_000
 
 
def load_entries(paths):
    #Load and combine entries from one or more Spotify export JSON files
    entries = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            entries.extend(json.load(f))
    return entries
 
 
def analyze(entries):
    song_plays = defaultdict(int)          # (track, artist) -> play count
    artist_ms = defaultdict(int)           # artist -> total ms played
 
    for e in entries:
        track = e.get("master_metadata_track_name")
        artist = e.get("master_metadata_album_artist_name")
        ms_played = e.get("ms_played", 0)
 
        # Skip podcasts, audiobooks, or entries missing track/artist info
        if not track or not artist:
            continue
 
        # Count towards total listening time for the artist regardless of length
        artist_ms[artist] += ms_played
 
        # Only count as a "play" if listened past the minimum threshold
        if ms_played >= MIN_MS_PLAYED:
            song_plays[(track, artist)] += 1
 
    return song_plays, artist_ms
 
 
def print_top_songs(song_plays, top_n=5):
    print(f"\n🎵 Top {top_n} Songs of the Year")
    print("-" * 40)
    top_songs = sorted(song_plays.items(), key=lambda x: x[1], reverse=True)[:top_n]
    for i, ((track, artist), plays) in enumerate(top_songs, start=1):
        play_word = "play" if plays == 1 else "plays"
        print(f"{i}. {track} — {artist} ({plays} {play_word})")
 
 
def print_top_artists(artist_ms, top_n=5):
    print(f"\n🎤 Top {top_n} Artists of the Year")
    print("-" * 40)
    top_artists = sorted(artist_ms.items(), key=lambda x: x[1], reverse=True)[:top_n]
    for i, (artist, ms) in enumerate(top_artists, start=1):
        minutes = ms / 60_000
        print(f"{i}. {artist} ({minutes:,.1f} minutes)")
 
 
def main():
    if len(sys.argv) < 2:
        print("Usage: wrapped.py <streaming_history.json> [more_files.json ...]")
        sys.exit(1)
 
    paths = sys.argv[1:]
    entries = load_entries(paths)
    song_plays, artist_ms = analyze(entries)
 
    print_top_songs(song_plays)
    print_top_artists(artist_ms)
 
 
if __name__ == "__main__":
    main()