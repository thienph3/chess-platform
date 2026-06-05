import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useRef, useState } from "react";

interface GameClockProps {
  initialTime: number;
  isActive: boolean;
  color: "white" | "black";
  increment?: number;
  onTimeout?: () => void;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function GameClock({ initialTime, isActive, color, increment = 0, onTimeout }: GameClockProps) {
  const [timeLeft, setTimeLeft] = useState(initialTime);
  const wasActive = useRef(isActive);
  const timeoutFired = useRef(false);

  useEffect(() => {
    setTimeLeft(initialTime);
    timeoutFired.current = false;
  }, [initialTime]);

  useEffect(() => {
    if (wasActive.current && !isActive && increment > 0) {
      setTimeLeft((prev) => prev + increment);
    }
    wasActive.current = isActive;
  }, [isActive, increment]);

  useEffect(() => {
    if (!isActive || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        const next = prev - 1;
        if (next <= 0 && onTimeout && !timeoutFired.current) {
          timeoutFired.current = true;
          onTimeout();
        }
        return Math.max(0, next);
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isActive, timeLeft, onTimeout]);

  const isLow = timeLeft < 30;

  return (
    <Box
      sx={{
        px: 2, py: 1, borderRadius: 1,
        bgcolor: isActive ? (isLow ? "error.main" : "primary.main") : "grey.300",
        color: isActive ? "white" : "text.primary",
        minWidth: 100, textAlign: "center",
      }}
    >
      <Stack alignItems="center">
        <Typography variant="caption">
          {color === "white" ? "Trắng" : "Đen"}
          {increment > 0 && ` +${increment}s`}
        </Typography>
        <Typography variant="h6" fontWeight={700} fontFamily="monospace">
          {formatTime(timeLeft)}
        </Typography>
      </Stack>
    </Box>
  );
}

export default GameClock;
