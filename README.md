# 🎵 Music Recommender Simulation

## Project Summary



This project models a small, content-based music recommender. Songs are described by attributes such as genre, mood, energy, tempo, and acousticness, while a user profile captures preferred genres and moods, target energy, and acoustic preference. The recommender is designed to score and rank songs against those preferences and explain its suggestions, making it possible to explore the strengths and limitations of a simple, transparent approach.

---

## How The System Works

Songs use these features in the simulation:

- `id`, `title`, and `artist`: identify and display the song
- `genre` and `mood`: describe the song's category and emotional quality
- `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`: describe its audio characteristics

User profiles use these preferences:

- `favorite_genre` and `favorite_mood`: the user's preferred categories
- `target_energy`: the energy level the user wants
- `likes_acoustic`: whether the user prefers more acoustic songs

The recommender compares the profile preferences with each song's genre, mood, energy, and acousticness when calculating a match score. The other song features are available for future scoring experiments.

This is a content-based recommender: it scores every song against the user's preferences and returns the top `k`. It does not use other listeners' behavior.

### Algorithm Recipe

For each song, the recommender:

1. Adds points for each feature below (maximum **10 points**).
2. Sorts all songs by total score, highest first.
3. Returns the top `k`, with a breakdown of the points each feature contributed.

| Feature | Max points | Share | How it is scored |
|---|---|---|---|
| Genre | 3.0 | 30% | Exact match = 3.0; related genre (e.g. `pop` vs `indie pop`) = 1.5; otherwise 0 |
| Mood | 2.5 | 25% | User's top mood = 2.5; each lower-ranked mood in their list earns 25% less (minimum 0.625); otherwise 0 |
| Energy | 3.0 | 30% | `3.0 × (1 − abs(song energy − target energy))` |
| Acousticness | 1.5 | 15% | Likes acoustic: `1.5 × acousticness`; doesn't: `1.5 × (1 − acousticness)`; with a `target_acousticness`, scored by closeness like energy |

**Why these weights**

- **No single feature dominates.** None is worth more than 30% of the total. An earlier genre-first version (genre 4.0 of 8 points) let a genre match outweigh everything else combined.
- **Mood is close to genre (2.5 vs 3.0).** Mood reflects what a listener wants right now, but mood labels are subjective and overlap (chill, relaxed, peaceful), so it sits slightly lower.
- **Energy is weighted as high as genre.** Closeness scoring gives almost every song a large share of the energy points (with a 0.5 target, every song earns at least 53%), so energy needs a higher weight to actually separate songs.
- **Acousticness is a tie-breaker.** It reorders similar songs rather than deciding the ranking.

**Expected results**

- *Intense rock*: Storm Runner ranks first, followed by other high-energy songs (Gym Hero, Iron Cathedral).
- *Chill lofi*: the three lofi songs rank first, with an ambient/chill song close behind.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python3 -m src.main` with the default lofi taste profile:

```text
$ python3 -m src.main
Loaded songs: 20
================================================================
Your taste profile
  Genre: lofi   Moods: chill, relaxed, peaceful, focused
  Energy: 0.4   Acousticness: 0.75
================================================================

Top 5 recommendations

1. Midnight Coding - LoRoom                            9.88 / 10
   lofi | chill | energy 0.42
   - matches your favorite genre (lofi)                    +3.00
   - matches your mood (chill)                             +2.50
   - energy 0.42 vs target 0.40                            +2.94
   - acousticness 0.71 vs target 0.75                      +1.44

2. Library Rain - Paper Lanterns                       9.68 / 10
   lofi | chill | energy 0.35
   - matches your favorite genre (lofi)                    +3.00
   - matches your mood (chill)                             +2.50
   - energy 0.35 vs target 0.40                            +2.85
   - acousticness 0.86 vs target 0.75                      +1.33

3. Focus Flow - LoRoom                                 8.08 / 10
   lofi | focused | energy 0.40
   - matches your favorite genre (lofi)                    +3.00
   - related mood (focused)                                +0.62
   - energy 0.40 vs target 0.40                            +3.00
   - acousticness 0.78 vs target 0.75                      +1.46

4. Spacewalk Thoughts - Orbit Bloom                    6.39 / 10
   ambient | chill | energy 0.28
   - matches your mood (chill)                             +2.50
   - energy 0.28 vs target 0.40                            +2.64
   - acousticness 0.92 vs target 0.75                      +1.24

5. Coffee Shop Stories - Slow Stereo                   6.08 / 10
   jazz | relaxed | energy 0.37
   - related mood (relaxed)                                +1.88
   - energy 0.37 vs target 0.40                            +2.91
   - acousticness 0.89 vs target 0.75                      +1.29
```


---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

This system might let genre and energy (60% of the score together) outweigh mood, ignoring great songs that match how the user feels. For example, a user who wants melancholic songs at high energy still gets upbeat pop. It may also under-serve fans of genres with only one song in the catalog (rock, metal, jazz), because it matches genre and mood labels exactly and has few same-genre songs to offer them.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



