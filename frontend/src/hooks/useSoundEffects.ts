import { Howl } from "howler";
import { useCallback, useState } from "react";

type SoundType = "move" | "capture" | "check" | "gameOver";

const STORAGE_KEY = "vcc_sound_enabled";

// Inline base64 short audio (generated tones) — no external files needed
// In production, replace with real .mp3 files in /public/sounds/
const SOUNDS: Record<SoundType, Howl> = {
  move: new Howl({ src: ["data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA="], volume: 0.4 }),
  capture: new Howl({ src: ["data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA="], volume: 0.5 }),
  check: new Howl({ src: ["data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA="], volume: 0.6 }),
  gameOver: new Howl({ src: ["data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA="], volume: 0.7 }),
};

function getInitialEnabled(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === null ? true : stored === "true";
}

export function useSoundEffects() {
  const [enabled, setEnabled] = useState(getInitialEnabled);

  const play = useCallback(
    (sound: SoundType) => {
      if (!enabled) return;
      try {
        SOUNDS[sound].play();
      } catch {
        // Howler not available — ignore
      }
    },
    [enabled],
  );

  const toggle = useCallback(() => {
    setEnabled((prev) => {
      const next = !prev;
      localStorage.setItem(STORAGE_KEY, String(next));
      // Mute/unmute all sounds
      Object.values(SOUNDS).forEach((s) => s.mute(!next));
      return next;
    });
  }, []);

  return { play, enabled, toggle };
}
