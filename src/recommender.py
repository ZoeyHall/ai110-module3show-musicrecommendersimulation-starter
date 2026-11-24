import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# Balanced weights out of a 10-point max (genre 30%, mood 25%, energy 30%,
# acousticness 15%). No single feature exceeds 30%, so no one signal can
# override the rest. Energy is weighted as high as genre on purpose: it is
# scored by closeness (1 - |diff|), so most songs earn a large share of it
# and its real spread between songs is much smaller than its nominal weight.
GENRE_WEIGHT = 3.0
PARTIAL_GENRE_WEIGHT = 1.5   # e.g. "pop" vs "indie pop" (half credit)
MOOD_WEIGHT = 2.5
MOOD_RANK_DECAY = 0.25       # each lower-ranked mood earns 25% less
MOOD_MIN_CREDIT = 0.25       # floor so long mood lists still give some credit
ENERGY_WEIGHT = 3.0
ACOUSTIC_WEIGHT = 1.5


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs to recommend from."""
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Convert a UserProfile into the preference dict that score_song expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the k highest-scoring songs for the user, best first."""
        prefs = self._prefs(user)
        ranked = sorted(self.songs, key=lambda s: score_song(prefs, vars(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a song's score and the reasons behind it as one readable string."""
        score, reasons = score_song(self._prefs(user), vars(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting id to int and audio features to float."""
    numeric = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            song = dict(row)
            song["id"] = int(row["id"])
            for key in numeric:
                song[key] = float(row[key])
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences (max 10) and return (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    fav_genre = str(user_prefs.get("genre", "")).lower().strip()
    genre = song["genre"].lower().strip()
    if fav_genre and genre == fav_genre:
        score += GENRE_WEIGHT
        reasons.append(f"matches your favorite genre ({song['genre']}) +{GENRE_WEIGHT:.2f}")
    elif fav_genre and (fav_genre in genre.split() or genre in fav_genre.split()):
        score += PARTIAL_GENRE_WEIGHT
        reasons.append(f"related genre ({song['genre']}) +{PARTIAL_GENRE_WEIGHT:.2f}")

    # Moods: accepts a ranked list ("moods") or a single string ("mood").
    # The first mood earns full credit; each later one earns 25% less
    # (2.5, 1.875, 1.25, 0.625, ...), so close-but-not-exact moods still count.
    moods = user_prefs.get("moods")
    if moods is None:
        moods = [user_prefs["mood"]] if user_prefs.get("mood") else []
    moods = [str(m).lower().strip() for m in moods]
    song_mood = song["mood"].lower().strip()
    if song_mood in moods:
        rank = moods.index(song_mood)
        pts = MOOD_WEIGHT * max(MOOD_MIN_CREDIT, 1 - MOOD_RANK_DECAY * rank)
        score += pts
        label = "matches your mood" if rank == 0 else "related mood"
        reasons.append(f"{label} ({song['mood']}) +{pts:.2f}")

    if "energy" in user_prefs:
        closeness = 1 - abs(float(song["energy"]) - float(user_prefs["energy"]))
        pts = ENERGY_WEIGHT * closeness
        score += pts
        reasons.append(f"energy {song['energy']:.2f} vs target {float(user_prefs['energy']):.2f} +{pts:.2f}")

    if "target_acousticness" in user_prefs:
        # Closeness to a 0.0-1.0 target, scored the same way as energy.
        target = float(user_prefs["target_acousticness"])
        acoustic = float(song["acousticness"])
        pts = ACOUSTIC_WEIGHT * (1 - abs(acoustic - target))
        score += pts
        reasons.append(f"acousticness {acoustic:.2f} vs target {target:.2f} +{pts:.2f}")
    elif "likes_acoustic" in user_prefs:
        acoustic = float(song["acousticness"])
        fit = acoustic if user_prefs["likes_acoustic"] else 1 - acoustic
        pts = ACOUSTIC_WEIGHT * fit
        score += pts
        reasons.append(f"acousticness fit +{pts:.2f}")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), highest first."""
    scored = (
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    )
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
