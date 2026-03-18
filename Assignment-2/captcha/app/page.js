"use client";

import { useState } from "react";
import CaptchaChallenge from "@/components/captcha/CaptchaChallenge";

export default function Home() {
  const [verified, setVerified] = useState(false);

  return (
    <div className="page-wrapper">
      <main className="page-main">
        <div className="page-header">
          <h1>CAPTCHA — Reverse Turing Test</h1>
          <p>
            A CAPTCHA is a <strong>Completely Automated Public Turing test to tell
            Computers and Humans Apart</strong>. Unlike the classic Turing Test where
            a human judges if a respondent is a machine, here a
            <em> machine</em> judges whether <em>you</em> are human by presenting
            distorted text that humans can read but bots cannot.
          </p>
        </div>

        {verified ? (
          <div className="verified-banner">
            <div className="verified-icon-circle">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M5 10l3.5 3.5L15 7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </div>
            <div>
              <h2>Access Granted</h2>
              <p>You have been verified as a human.</p>
            </div>
            <button
              className="captcha-btn-secondary"
              onClick={() => setVerified(false)}
            >
              Try Again
            </button>
          </div>
        ) : (
          <CaptchaChallenge onVerified={() => setVerified(true)} />
        )}

        <div className="info-section">
          <h2>How It Works</h2>
          <div className="info-grid-single">
            <div className="info-card">
              <div className="info-icon-wrap">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M4 7h3M9 7h3M4 10h8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>
              </div>
              <h3>Distorted Text on Canvas</h3>
              <p>Random characters are rendered with rotation, skew, noise lines, and dots. Humans parse this easily; OCR and bots struggle with the distortion.</p>
            </div>
            <div className="info-card">
              <div className="info-icon-wrap">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="3" y="7" width="10" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.5"/><path d="M5 7V5a3 3 0 0 1 6 0v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
              </div>
              <h3>Server-Side Verification</h3>
              <p>The answer is never sent to the browser. It stays on the server and is compared when you submit — no way to cheat via DevTools.</p>
            </div>
            <div className="info-card">
              <div className="info-icon-wrap">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5"/><path d="M8 4v4.5l3 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </div>
              <h3>Rate Limited</h3>
              <p>Each challenge allows 3 attempts, then expires. Challenges also expire after 5 minutes to prevent replay attacks.</p>
            </div>
          </div>
        </div>

        <div className="info-section">
          <h2>Turing Test Connection</h2>
          <p>
            Alan Turing proposed that if a machine can exhibit intelligent behavior
            indistinguishable from a human, it passes the &quot;Turing Test.&quot; A CAPTCHA
            inverts this: the <strong>computer is the judge</strong>, and it designs
            challenges that exploit tasks humans find trivial but machines find hard —
            like reading warped, noisy text.
          </p>
        </div>
      </main>
    </div>
  );
}
