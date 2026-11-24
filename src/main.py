"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs      # python main.py


# Taste profile used for every comparison. Keys match what score_song() reads:
#   genre               -> favorite_genre (exact or partial match)
#   moods               -> ranked moods; first = full credit, later = partial
#   energy              -> target_energy (0.0-1.0, closer is better)
#   target_acousticness -> desired acousticness (0.0-1.0, closer is better)
TASTE_PROFILE = {
    "genre": "lofi",
    "moods": ["chill", "relaxed", "peaceful", "focused"],
    "energy": 0.40,
    "target_acousticness": 0.75,
}


WIDTH = 64
MAX_SCORE = 10.0


def print_profile(prefs: dict) -> None:
    """Show the taste profile the recommendations are based on."""
    moods = ", ".join(prefs.get("moods", [prefs.get("mood", "-")]))
    print("Your taste profile")
    print(f"  Genre: {prefs.get('genre', '-')}   Moods: {moods}")
    print(f"  Energy: {prefs.get('energy', '-')}   "
          f"Acousticness: {prefs.get('target_acousticness', prefs.get('likes_acoustic', '-'))}")


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print one song: title and score on the first line, then one reason per line."""
    title = f"{rank}. {song['title']} - {song['artist']}"
    score_text = f"{score:.2f} / {MAX_SCORE:.0f}"
    print(f"{title:<{WIDTH - len(score_text)}}{score_text}")
    print(f"   {song['genre']} | {song['mood']} | energy {song['energy']:.2f}")
    for reason in explanation.split("; "):
        # Reasons end in "+points"; split them off so the points line up.
        text, _, points = reason.rpartition(" +")
        print(f"   - {text:<{WIDTH - 12}}{'+' + points:>7}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    recommendations = recommend_songs(TASTE_PROFILE, songs, k=5)

    print("=" * WIDTH)
    print_profile(TASTE_PROFILE)
    print("=" * WIDTH)
    print(f"\nTop {len(recommendations)} recommendations\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)


if __name__ == "__main__":
    main()
