# gRank

gRank ranks every episode of **Nerd Snipe with Theo and Ben** by:

1. how long it takes for `gstack` to be mentioned, and
2. how many explicit `gstack` mentions occur.

The production site is a fully static SvelteKit build. A separate Python pipeline discovers episodes from RSS, optionally maps YouTube videos/captions, transcribes audio locally with MLX Whisper, generates review candidates, and publishes a validated JSON artifact.

## Requirements

- Node.js 24+
- pnpm 10+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- ffmpeg / ffprobe / ffplay
- Apple Silicon for the default MLX transcription path

## Site

```bash
pnpm install
pnpm dev
```

Quality checks:

```bash
pnpm check
pnpm test
pnpm build
pnpm test:e2e
```

The committed `data/grank.json` is published after reproducible automated transcript adjudication.
No listening pass is required. Exact `gstack` forms are accepted, generic stack-family matches are
rejected, and cross-source evidence is retained in the review records.

## Pipeline

```bash
uv sync --extra dev --extra analysis
uv run grank sync-feed
uv run grank match-youtube
uv run grank download
uv run grank transcribe
uv run grank detect
uv run grank auto-review
uv run grank review <rss-guid>
uv run grank publish
uv run grank verify
```

Use `uv run grank publish --draft` for local UI development while reviews remain incomplete. A production publication fails if any catalog episode lacks a completed review.

### Source priority

1. RSS is the source of record for episode inventory and audio.
2. YouTube is optional enrichment for watch links and captions.
3. Local MLX Whisper transcription covers missing captions and supplies a second detection source.
4. Automated transcript consensus applies the versioned publication policy. The optional interactive
   review command remains available for corrections.

Heavy audio, model, and transcript artifacts live under `work/` and are ignored by Git. Adjudicated
decisions under `data/review/` and the published `data/grank.json` form the auditable record.

## Deployment

Vercel builds `pnpm build` and serves the static `build/` directory. The MVP uses no functions, database, scheduled jobs, or paid APIs.
