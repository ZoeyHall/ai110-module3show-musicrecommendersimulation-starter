"""Sanity checks that the scoring weights produce sensible rankings on data/songs.csv."""
from src import recommender as r

songs = r.load_songs("data/songs.csv")
ENERGY = {s["title"]: s["energy"] for s in songs}

INTENSE_ROCK = {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
CHILL_LOFI = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}


def top(prefs, k=3):
    return [s["title"] for s, _, _ in r.recommend_songs(prefs, songs, k=k)]


def test_max_score_is_ten():
    assert r.GENRE_WEIGHT + r.MOOD_WEIGHT + r.ENERGY_WEIGHT + r.ACOUSTIC_WEIGHT == 10.0


def test_no_single_feature_dominates():
    total = r.GENRE_WEIGHT + r.MOOD_WEIGHT + r.ENERGY_WEIGHT + r.ACOUSTIC_WEIGHT
    for w in (r.GENRE_WEIGHT, r.MOOD_WEIGHT, r.ENERGY_WEIGHT, r.ACOUSTIC_WEIGHT):
        assert w / total <= 0.30


def test_intense_rock_top_pick_and_high_energy_neighbors():
    titles = top(INTENSE_ROCK, k=3)
    assert titles[0] == "Storm Runner"
    assert all(ENERGY[t] >= 0.75 for t in titles)


def test_chill_lofi_top3_are_low_energy_lofi():
    titles = top(CHILL_LOFI, k=3)
    assert set(titles) == {"Library Rain", "Midnight Coding", "Focus Flow"}
    assert all(ENERGY[t] < 0.5 for t in titles)


def test_off_genre_mood_match_stays_competitive():
    # An ambient/chill song should land right behind the lofi songs, not far back.
    assert top(CHILL_LOFI, k=4)[3] == "Spacewalk Thoughts"


def test_unknown_genre_still_returns_mood_matches():
    titles = top({"genre": "k-pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}, k=2)
    assert set(titles) == {"Sunrise City", "Rooftop Lights"}
