"use client";

import { useState, useCallback, useRef, useEffect } from "react";

export default function CaptchaChallenge({ onVerified }) {
  const [challenge, setChallenge] = useState(null);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | success | fail
  const [message, setMessage] = useState("");
  const canvasRef = useRef(null);
  const inputRef = useRef(null);

  const fetchChallenge = useCallback(async () => {
    setStatus("loading");
    setAnswer("");
    setMessage("");
    try {
      const res = await fetch("/api/captcha/generate");
      const data = await res.json();
      setChallenge(data);
      setStatus("idle");
    } catch {
      setMessage("Failed to load challenge");
      setStatus("fail");
    }
  }, []);

  // Draw distorted text on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    const display = challenge?.display;
    if (!canvas || !display) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;

    // Background with subtle gradient
    const bg = ctx.createLinearGradient(0, 0, w, h);
    bg.addColorStop(0, `hsl(${display.bgHue}, 15%, 92%)`);
    bg.addColorStop(1, `hsl(${(display.bgHue + 40) % 360}, 15%, 88%)`);
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Noise dots
    for (let i = 0; i < display.noiseDots; i++) {
      ctx.fillStyle = `hsl(${Math.random() * 360}, 40%, 70%)`;
      ctx.beginPath();
      ctx.arc(Math.random() * w, Math.random() * h, Math.random() * 2.5 + 0.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Noise lines
    for (let i = 0; i < display.noiseLines; i++) {
      ctx.strokeStyle = `hsl(${Math.random() * 360}, 30%, 65%)`;
      ctx.lineWidth = Math.random() * 1.5 + 0.5;
      ctx.beginPath();
      ctx.moveTo(Math.random() * w, Math.random() * h);
      ctx.bezierCurveTo(
        Math.random() * w, Math.random() * h,
        Math.random() * w, Math.random() * h,
        Math.random() * w, Math.random() * h
      );
      ctx.stroke();
    }

    // Draw characters
    const charWidth = w / (display.chars.length + 1);
    display.chars.forEach((ch, i) => {
      ctx.save();
      const x = charWidth * (i + 0.7);
      const y = h / 2 + ch.offsetY;
      ctx.translate(x, y);
      ctx.rotate((ch.rotation * Math.PI) / 180);
      ctx.transform(1, 0, (ch.skewX * Math.PI) / 180, 1, 0, 0);
      ctx.font = `bold ${ch.fontSize}px monospace`;
      ctx.fillStyle = `hsl(${Math.random() * 360}, 60%, 30%)`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(ch.char, 0, 0);
      ctx.restore();
    });

    // Focus input after drawing
    inputRef.current?.focus();
  }, [challenge]);

  const verify = useCallback(async () => {
    if (!challenge || !answer.trim()) return;
    setStatus("loading");
    try {
      const res = await fetch("/api/captcha/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: challenge.id, answer: answer.trim() }),
      });
      const data = await res.json();
      if (data.success) {
        setStatus("success");
        setMessage(data.message);
        setTimeout(() => onVerified?.(), 1200);
      } else {
        setStatus("fail");
        setMessage(data.message);
      }
    } catch {
      setMessage("Verification failed");
      setStatus("fail");
    }
  }, [challenge, answer, onVerified]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter") verify();
    },
    [verify]
  );

  // Not started yet
  if (!challenge && status !== "loading") {
    return (
      <div className="captcha-widget">
        <div className="captcha-start">
          <div className="captcha-shield-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7L12 2z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/><path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </div>
          <h2>Human Verification</h2>
          <p>Complete a CAPTCHA to prove you&apos;re not a robot</p>
          <button className="captcha-btn-primary" onClick={fetchChallenge}>
            Start Verification
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="captcha-widget">
      <div className="captcha-header">
        <div className="captcha-header-left">
          <div className="captcha-header-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7L12 2z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/></svg>
          </div>
          <div>
            <h3>Human Verification</h3>
            <p>Type the characters you see below</p>
          </div>
        </div>
      </div>

      <div className="captcha-body">
        {status === "success" ? (
          <div className="captcha-success">
            <div className="success-check">✓</div>
            <p className="success-title">Verified</p>
            <p className="success-subtitle">Verification successful</p>
          </div>
        ) : status === "loading" && !challenge ? (
          <div className="captcha-loading">Loading challenge...</div>
        ) : (
          <div className="captcha-type-container">
            <canvas
              ref={canvasRef}
              width={300}
              height={90}
              className="captcha-canvas"
            />
            <input
              ref={inputRef}
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type what you see..."
              className="captcha-input"
              maxLength={8}
              autoComplete="off"
              autoCorrect="off"
              spellCheck="false"
              disabled={status === "success"}
            />
          </div>
        )}
      </div>

      {status !== "success" && challenge && (
        <div className="captcha-footer">
          <button
            className="captcha-btn-secondary"
            onClick={fetchChallenge}
            disabled={status === "loading"}
          >
            ↻ New
          </button>

          {message && (
            <span className={`captcha-message ${status === "fail" ? "error" : ""}`}>
              {message}
            </span>
          )}

          <button
            className="captcha-btn-primary"
            onClick={verify}
            disabled={!answer.trim() || status === "loading"}
          >
            Verify
          </button>
        </div>
      )}
    </div>
  );
}
