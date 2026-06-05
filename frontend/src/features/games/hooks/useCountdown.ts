import { useEffect, useState } from "react";

/**
 * Hook đếm ngược đến thời điểm scheduled_start.
 * Trả về secondsLeft (0 nếu đã qua) và isReady (true khi hết countdown).
 */
export function useCountdown(targetTime: string | null) {
  const [secondsLeft, setSecondsLeft] = useState(0);

  useEffect(() => {
    if (!targetTime) { setSecondsLeft(0); return; }
    const calcRemaining = () => Math.max(0, Math.floor((new Date(targetTime).getTime() - Date.now()) / 1000));
    setSecondsLeft(calcRemaining());

    const interval = setInterval(() => {
      const remaining = calcRemaining();
      setSecondsLeft(remaining);
      if (remaining <= 0) clearInterval(interval);
    }, 1000);

    return () => clearInterval(interval);
  }, [targetTime]);

  const isReady = !targetTime || secondsLeft <= 0;
  return { secondsLeft, isReady };
}

export function formatCountdown(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}
