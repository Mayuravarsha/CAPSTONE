import { useState } from "react";

export default function Uploader({ onFile, file }) {
  const [over, setOver] = useState(false);

  function drop(e) {
    e.preventDefault();
    setOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  }

  return (
    <label
      className={`drop ${over ? "over" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={drop}
    >
      <input type="file" accept="video/*" onChange={(e) => e.target.files[0] && onFile(e.target.files[0])} />
      {file ? <span><strong>{file.name}</strong> ({(file.size / 2 ** 20).toFixed(1)} MB)</span>
            : <span>Drop a video here or <u>browse</u></span>}
    </label>
  );
}
