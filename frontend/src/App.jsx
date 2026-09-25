import { useEffect, useRef, useState } from "react";
import { analyzeVideo } from "./api.js";
import Uploader from "./components/Uploader.jsx";
import ResultView from "./components/ResultView.jsx";

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const abort = useRef(null);

  useEffect(() => {
    if (!file) return undefined;
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  async function run() {
    abort.current?.abort();
    abort.current = new AbortController();
    setStatus("loading");
    setError("");
    try {
      setResult(await analyzeVideo(file, { signal: abort.current.signal }));
      setStatus("done");
    } catch (e) {
      if (e.name === "AbortError") return;
      setError(e.message);
      setStatus("error");
    }
  }

  function choose(f) {
    setFile(f);
    setResult(null);
    setStatus("idle");
  }

  return (
    <main>
      <header>
        <h1>Violence Detection</h1>
        <p>Audio spectrogram CNN + C3D video model. Upload a clip to check it for violent content.</p>
      </header>

      <section className="card">
        <Uploader onFile={choose} file={file} />
        {preview && <video className="preview" src={preview} controls muted />}
        <button disabled={!file || status === "loading"} onClick={run}>
          {status === "loading" ? "Analysing…" : "Detect violence"}
        </button>
        {status === "error" && <p className="error" role="alert">{error}</p>}
      </section>

      {status === "done" && result && <ResultView result={result} />}
    </main>
  );
}
