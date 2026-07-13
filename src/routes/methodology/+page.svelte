<svelte:head>
  <title>Methodology | gRank</title>
  <meta
    name="description"
    content="How gRank discovers, transcribes, reviews, and ranks Nerd Snipe episodes."
  />
</svelte:head>

<div class="shell methodology-page">
  <header class="method-poster">
    <h1>A small leaderboard with an unusually thorough audit trail.</h1>
    <p>
      Two literal rankings, derived from timestamped transcript evidence and a reproducible
      automated adjudication policy.
    </p>
  </header>

  <nav class="method-index" aria-label="On this page">
      <strong>Method atlas</strong>
      <a href="#rankings">The rankings</a>
      <a href="#sources">Sources</a>
      <a href="#detection">Detection</a>
      <a href="#review">Automated review</a>
      <a href="#limits">Limitations</a>
  </nav>

    <article class="method-chapters">
      <section id="rankings">
        <header><h2>The rankings</h2></header>
        <div class="ranking-definitions">
          <div>
            <h3>Fastest to gstack</h3>
            <p>
              The timer begins at <code>00:00</code> of the analyzed podcast enclosure. Intros, ads,
              music, and pre-roll all count. The first accepted transcript reference supplies the
              timestamp. Episodes with no accepted mention appear below mentioned episodes and
              display “No mention.”
            </p>
          </div>
          <div>
            <h3>Most gstack</h3>
            <p>
              Every distinct, explicit transcript reference counts. We accept “gstack,” “g-stack,”
              “g stack,” possessives, and a clearly intended “gee stack.” Generic software-stack
              discussion and pronouns do not count. Raw count determines rank; mentions per hour is
              secondary context.
            </p>
          </div>
        </div>
      </section>

      <section id="sources">
        <header><h2>Source priority</h2></header>
        <ol>
          <li>
            <strong>RSS feed:</strong> canonical episode inventory, metadata, GUIDs, and audio.
          </li>
          <li>
            <strong>YouTube:</strong> optional video mapping, watch links, and usable captions.
          </li>
          <li><strong>MLX Whisper:</strong> local timestamped transcription of the RSS audio.</li>
        </ol>
        <p>
          YouTube is enrichment rather than the source of record because public caption access can
          change and the video catalog may not exactly match the podcast feed.
        </p>
      </section>

      <section id="detection">
        <header><h2>Candidate detection</h2></header>
        <p>
          Transcript and caption tokens are normalized and searched in short windows for exact,
          phonetic, and constrained fuzzy variants. Every suspicious occurrence of “stack” enters
          the audit queue. Show-note chapter timestamps seed additional windows but never count as
          proof by themselves.
        </p>
      </section>

      <section id="review">
        <header><h2>Automated transcript consensus</h2></header>
        <p>
          Policy v1 accepts exact “gstack,” “g stack,” and “gee stack” candidates. It records
          whether MLX Whisper and YouTube captions corroborate the event, rejects generic stack,
          TanStack, and Substack matches, rejects metadata-only chapter hints, and collapses
          overlapping fuzzy windows as duplicates. An episode receives “No mention” only after the
          broader stack audit has been adjudicated. Metrics are derived from accepted events and
          cannot be edited independently.
        </p>
      </section>

      <section id="limits">
        <header><h2>Snapshot limitations</h2></header>
        <p>
          Podcast enclosures can be replaced or receive dynamic ads. Published records therefore
          retain the analyzed file’s byte length and SHA-256 hash. Transcription models can also
          change; model and config provenance are attached to each completed review.
        </p>
        <p>
          This policy avoids mandatory listening, but speech recognition can still miss a reference
          or place a timestamp slightly early or late. Every accepted mention exposes its context,
          source set, confidence, and audio provenance so corrections remain auditable.
        </p>
        <p>
          Found a mistake? Open a correction against the public review record and regenerated
          <a href="/data/grank.json">dataset</a>.
        </p>
      </section>
    </article>
</div>
