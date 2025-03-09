"use client";
import { useState } from "react";

export default function Home() {
    const [lyrics, setLyrics] = useState<string>("");
    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    const fetchAIResponse = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: lyrics }),
            });

            if (!res.ok) throw new Error("Error generating vocals");

            const data = await res.json();
            setAudioUrl(data.audio_url);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1>🎶 OpenSingAI 🎶</h1>
            <textarea
                rows={4}
                cols={50}
                placeholder="Enter lyrics..."
                value={lyrics}
                onChange={(e) => setLyrics(e.target.value)}
            />
            <br />
            <button onClick={fetchAIResponse}>Generate Vocals</button>

            {audioUrl && (
                <div>
                    <h3>Generated AI Vocals:</h3>
                    <audio controls>
                        <source src={audioUrl} type="audio/wav" />
                        Your browser does not support the audio element.
                    </audio>
                    <br />
                    <a href={audioUrl} download="generated_song.wav">
                        Download AI Vocals
                    </a>
                </div>
            )}
        </div>
    );
}
