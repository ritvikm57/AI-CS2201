// In-memory store for captcha challenges (server-side only)
const store = new Map();

const EXPIRY_MS = 5 * 60 * 1000;

function cleanup() {
  const now = Date.now();
  for (const [id, entry] of store) {
    if (now - entry.createdAt > EXPIRY_MS) {
      store.delete(id);
    }
  }
}

setInterval(cleanup, 60_000);

function randomId() {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateChallenge() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
  let text = "";
  const length = randomInt(5, 7);
  for (let i = 0; i < length; i++) {
    text += chars[randomInt(0, chars.length - 1)];
  }
  return {
    display: {
      chars: text.split("").map((ch) => ({
        char: ch,
        rotation: randomInt(-30, 30),
        offsetY: randomInt(-10, 10),
        fontSize: randomInt(26, 40),
        skewX: randomInt(-15, 15),
      })),
      noiseLines: randomInt(5, 9),
      noiseDots: randomInt(40, 80),
      bgHue: randomInt(0, 360),
    },
    answer: text,
  };
}

export function generateCaptcha() {
  const challenge = generateChallenge();
  const id = randomId();

  store.set(id, {
    answer: challenge.answer,
    createdAt: Date.now(),
    attempts: 0,
  });

  return {
    id,
    display: challenge.display,
  };
}

export function verifyCaptcha(id, userAnswer) {
  const entry = store.get(id);

  if (!entry) {
    return { success: false, message: "Challenge expired or not found." };
  }

  entry.attempts += 1;

  if (entry.attempts > 3) {
    store.delete(id);
    return { success: false, message: "Too many attempts. Please get a new challenge." };
  }

  const correct = entry.answer.toLowerCase() === (userAnswer || "").trim().toLowerCase();

  if (correct) {
    store.delete(id);
    return { success: true, message: "Verified! You are human." };
  }

  return {
    success: false,
    message: `Incorrect. ${3 - entry.attempts} attempt(s) remaining.`,
  };
}
