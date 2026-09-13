"""
Spotify Wrapped

You can now optionally narrow the analysis to a specific date range using
--start and --end (format: YYYY-MM-DD, both inclusive). Leave either one
out to leave that end of the range open.
 
Usage:
    python wrapped.py Streaming_History_Audio_2026.json
    python wrapped.py Streaming_History_Audio_2026.json --start 2026-06-01 --end 2026-08-31
    python wrapped.py Streaming_History_Audio_2026.json --start 2026-06-01
"""

import argparse
import json
from collections import defaultdict
 
# A "play" only counts if the track was listened to for at least 30 seconds
MIN_MS_PLAYED = 30_000
 
 
def load_entries(paths):
    """ Load and combine entries from one or more Spotify export JSON files """
    entries = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            entries.extend(json.load(f))
    return entries

def in_date_range(ts, start, end):
    """
    Check whether a timestamp string (e.g. "2026-06-15T14:03:00Z") falls
    within the given start/end dates. 
    `start` and `end` are "YYYY-MM-DD" strings
    """
    date_str = ts[:10]  # take just the "YYYY-MM-DD" part of the timestamp
    if start and date_str < start:
        return False
    if end and date_str > end:
        return False
    return True
 
 
def filter_by_date(entries, start, end):
    """Return only the entries whose timestamp falls within [start, end]."""
    if not start and not end:
        return entries  # no range given -> keep everything, same as before
    return [e for e in entries if in_date_range(e["ts"], start, end)]
 
 
def analyze(entries):
    song_plays = defaultdict(int)          # (track, artist) -> play count
    artist_ms = defaultdict(int)           # artist -> total ms played
    total_ms = 0                           # total ms played across everything
 
    for e in entries:
        track = e.get("master_metadata_track_name")
        artist = e.get("master_metadata_album_artist_name")
        ms_played = e.get("ms_played", 0)
 
        # Skip podcasts, audiobooks, or entries missing track/artist info
        if not track or not artist:
            continue
        
        # Total listening time counts everything: songs, podcasts, audiobooks
        total_ms += ms_played
 
        # Count towards total listening time for the artist regardless of length
        artist_ms[artist] += ms_played
 
        # Only count as a "play" if listened past the minimum threshold
        if ms_played >= MIN_MS_PLAYED:
            song_plays[(track, artist)] += 1
 
    return song_plays, artist_ms, total_ms
 
 
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
    
def print_total_minutes(total_ms):
    minutes = total_ms / 60_000
    hours = minutes / 60
    print(f"\n⏱️  Total Listening Time")
    print("-" * 40)
    print(f"{minutes:,.1f} minutes ({hours:,.1f} hours)")

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze Spotify streaming history.")
    parser.add_argument("files", nargs="+", help="One or more Spotify export JSON files")
    parser.add_argument("--start", metavar="YYYY-MM-DD", default=None,
                         help="Only include plays on/after this date")
    parser.add_argument("--end", metavar="YYYY-MM-DD", default=None,
                         help="Only include plays on/before this date")
    return parser.parse_args()
 
def main():
    args = parse_args()  # NEW: was `sys.argv[1:]` before
 
    entries = load_entries(args.files)
    entries = filter_by_date(entries, args.start, args.end)  # NEW: apply date filter
 
    if not entries:
        print("No streaming history found in that date range.")
        return
 
    # NEW: label the range being reported on, so it's clear what you're looking at
    if args.start or args.end:
        range_label = f"{args.start or 'the beginning'} to {args.end or 'the end'}"
    else:
        range_label = "your entire history"
    print(f"Showing results for: {range_label}")
 
    song_plays, artist_ms, total_ms = analyze(entries)
 
    print_top_songs(song_plays, 50)
    print_top_artists(artist_ms, 20)
    print_total_minutes(total_ms)

 
if __name__ == "__main__":
    main()