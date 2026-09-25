const pct = (x) => `${Math.round(x * 100)}%`;

export default function ResultView({ result }) {
  const { violent, decided_by, audio_probability, violent_clip_share, clips, seconds, note } = result;
  return (
    <section className={`card result ${violent ? "violent" : "calm"}`}>
      <h2>{violent ? "Violent content detected" : "No violence detected"}</h2>
      <dl>
        <dt>Decided by</dt>
        <dd>{decided_by === "audio" ? "audio model (video model skipped)" : decided_by === "video" ? "video model" : "—"}</dd>
        <dt>Audio model</dt>
        <dd>{audio_probability == null ? "no audio track" : `${pct(audio_probability)} violent`}</dd>
        {violent_clip_share != null && (<><dt>Violent clips</dt><dd>{pct(violent_clip_share)} of {clips.length}</dd></>)}
        <dt>Time</dt>
        <dd>{seconds.toFixed(1)} s</dd>
      </dl>
      {note && <p className="note">{note}</p>}
      {clips.length > 0 && <Timeline clips={clips} />}
    </section>
  );
}

function Timeline({ clips }) {
  const w = 100 / clips.length;
  return (
    <figure>
      <svg viewBox="0 0 100 30" preserveAspectRatio="none" role="img"
           aria-label="violence probability for each 16-frame clip">
        <line x1="0" x2="100" y1={30 - 0.75 * 30} y2={30 - 0.75 * 30} className="threshold" />
        {clips.map((c, i) => (
          <rect key={i} x={i * w + w * 0.1} width={w * 0.8} y={30 - c.probability * 30}
                height={c.probability * 30} className={c.probability >= 0.75 ? "hot" : "cold"}>
            <title>{`${c.start}s – ${c.end}s: ${pct(c.probability)}`}</title>
          </rect>
        ))}
      </svg>
      <figcaption>Violence probability per 16-frame clip (dashed line: 0.75 clip threshold)</figcaption>
    </figure>
  );
}
