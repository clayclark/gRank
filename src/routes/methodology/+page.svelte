<svelte:head>
  <title>Methodology — gRank</title>
  <meta
    name="description"
    content="How gRank discovers, transcribes, reviews, and ranks Nerd Snipe episodes."
  />
</svelte:head>

<div class="shell methodology-page">
  <header class="prose-hero">
    <span class="eyebrow">Methodology v1.0</span>
    <h1>A small leaderboard with an unusually thorough audit trail.</h1>
    <p>
      gRank is intentionally literal. It does not calculate a mysterious composite score. It
      publishes two measurements derived from timestamped, manually accepted audio events.
    </p>
  </header>

  <div class="method-grid">
    <aside aria-label="On this page">
      <strong>On this page</strong>
      <a href="#rankings">The rankings</a>
      <a href="#sources">Sources</a>
      <a href="#detection">Detection</a>
      <a href="#review">Human review</a>
      <a href="#limits">Limitations</a>
    </aside>

    <article class="prose">
      <section id="rankings">
        <span class="section-number">01</span>
        <h2>The rankings</h2>
        <h3>Fastest to gstack</h3>
        <p>
          The timer begins at <code>00:00</code> of the analyzed podcast enclosure. Intros, ads, music,
          and pre-roll all count. The first accepted audible reference supplies the timestamp. Episodes
          with no accepted mention appear below mentioned episodes and display “No mention.”
        </p>
        <h3>Most gstack</h3>
        <p>
          Every distinct, explicit audible reference counts. We accept “gstack,” “g-stack,” “g
          stack,” possessives, and a clearly intended “gee stack.” Generic software-stack discussion
          and pronouns do not count. Raw count determines rank; mentions per hour is secondary
          context.
        </p>
      </section>

      <section id="sources">
        <span class="section-number">02</span>
        <h2>Source priority</h2>
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
        <span class="section-number">03</span>
        <h2>Candidate detection</h2>
        <p>
          Transcript and caption tokens are normalized and searched in short windows for exact,
          phonetic, and constrained fuzzy variants. Every suspicious occurrence of “stack” enters
          the audit queue. Show-note chapter timestamps seed additional windows but never count as
          proof by themselves.
        </p>
      </section>

      <section id="review">
        <span class="section-number">04</span>
        <h2>Human review</h2>
        <p>
          A reviewer listens around each candidate, accepts or rejects it, and corrects the
          timestamp when necessary. An episode cannot be published as “No mention” until its broader
          low-confidence audit is complete. Metrics are derived from accepted events and cannot be
          edited independently.
        </p>
      </section>

      <section id="limits">
        <span class="section-number">05</span>
        <h2>Snapshot limitations</h2>
        <p>
          Podcast enclosures can be replaced or receive dynamic ads. Published records therefore
          retain the analyzed file’s byte length and SHA-256 hash. Transcription models can also
          change; model and config provenance are attached to each completed review.
        </p>
        <p>
          Found a mistake? Open a correction against the public review record and regenerated
          <a href="/data/grank.json">dataset</a>.
        </p>
      </section>
    </article>
  </div>
</div>
