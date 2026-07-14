# gRank

[gRank](https://g-rank.vercel.app) is an unofficial leaderboard for **Nerd Snipe with Theo and Ben** built around one recurring question: how much `gstack` is in each episode?

Every episode is ranked two ways:

- **Fastest to gstack** measures the time from the beginning of an episode to its first explicit `gstack` mention.
- **Most gstack** counts every explicit `gstack` mention in the episode.

Episode pages show the timestamp and transcript context for every counted mention, so each result can be checked without listening through the full episode.

**[View the rankings](https://g-rank.vercel.app)**

## About the data

The episode catalog comes from the podcast RSS feed. Transcript evidence is compared across available YouTube captions and local transcription, then validated before publication. Only explicit spoken references to `gstack` count.

The published rankings are also available as [machine-readable JSON](https://g-rank.vercel.app/data/grank.json).

## Project

The site is built with SvelteKit. A Python pipeline handles episode discovery, transcription, mention detection, review, and publication. Audio, full transcripts, and model files are not included in the repository.

gRank is a fan project and is not affiliated with Nerd Snipe, Theo Browne, or Ben Holmen.

## License

The code is available under the [MIT License](LICENSE). Podcast audio, episode metadata, and transcript excerpts remain the property of their respective owners.
