import Box from "@mui/material/Box";
import { useCallback, useState } from "react";

interface GomokuBoardProps {
  size?: number;
  stones: { row: number; col: number; color: "black" | "white" }[];
  onPlace?: (row: number, col: number) => void;
  allowPlacing?: boolean;
  lastMove?: { row: number; col: number } | null;
  winLine?: { row: number; col: number }[];
}

const CELL_SIZE = 32;
const PADDING = 24;

function GomokuBoard({ size = 15, stones, onPlace, allowPlacing = true, lastMove, winLine }: GomokuBoardProps) {
  const [hover, setHover] = useState<{ row: number; col: number } | null>(null);
  const svgSize = (size - 1) * CELL_SIZE + PADDING * 2;

  const hasStone = useCallback(
    (row: number, col: number) => stones.find((s) => s.row === row && s.col === col),
    [stones]
  );

  const isWinCell = useCallback(
    (row: number, col: number) => winLine?.some((w) => w.row === row && w.col === col),
    [winLine]
  );

  return (
    <Box sx={{ display: "inline-block" }}>
      <svg
        width={svgSize}
        height={svgSize}
        style={{ background: "#DCB35C", borderRadius: 8 }}
        role="img"
        aria-label="Bàn cờ caro"
      >
        {/* Grid lines */}
        {Array.from({ length: size }, (_, i) => (
          <g key={`grid-${i}`}>
            <line
              x1={PADDING} y1={PADDING + i * CELL_SIZE}
              x2={PADDING + (size - 1) * CELL_SIZE} y2={PADDING + i * CELL_SIZE}
              stroke="#333" strokeWidth={i === 0 || i === size - 1 ? 1.5 : 0.8}
            />
            <line
              x1={PADDING + i * CELL_SIZE} y1={PADDING}
              x2={PADDING + i * CELL_SIZE} y2={PADDING + (size - 1) * CELL_SIZE}
              stroke="#333" strokeWidth={i === 0 || i === size - 1 ? 1.5 : 0.8}
            />
          </g>
        ))}
        {/* Star points */}
        {[[3, 3], [3, 11], [7, 7], [11, 3], [11, 11]].map(([r, c]) => (
          <circle key={`star-${r}-${c}`} cx={PADDING + c * CELL_SIZE} cy={PADDING + r * CELL_SIZE} r={3.5} fill="#333" />
        ))}
        {/* Click targets */}
        {Array.from({ length: size }, (_, r) =>
          Array.from({ length: size }, (_, c) =>
            !hasStone(r, c) && (
              <circle
                key={`t-${r}-${c}`}
                cx={PADDING + c * CELL_SIZE} cy={PADDING + r * CELL_SIZE}
                r={CELL_SIZE / 2 - 1} fill="transparent"
                style={{ cursor: allowPlacing ? "pointer" : "default" }}
                onClick={() => allowPlacing && onPlace?.(r, c)}
                onMouseEnter={() => setHover({ row: r, col: c })}
                onMouseLeave={() => setHover(null)}
              />
            )
          )
        )}
        {/* Hover */}
        {hover && allowPlacing && !hasStone(hover.row, hover.col) && (
          <circle
            cx={PADDING + hover.col * CELL_SIZE} cy={PADDING + hover.row * CELL_SIZE}
            r={CELL_SIZE / 2 - 4} fill="rgba(0,0,0,0.2)"
          />
        )}
        {/* Stones */}
        {stones.map((s, i) => (
          <circle
            key={i}
            cx={PADDING + s.col * CELL_SIZE} cy={PADDING + s.row * CELL_SIZE}
            r={CELL_SIZE / 2 - 3}
            fill={s.color === "black" ? "#111" : "#FFF"}
            stroke={isWinCell(s.row, s.col) ? "#FF4444" : "#333"}
            strokeWidth={isWinCell(s.row, s.col) ? 2.5 : 1}
          />
        ))}
        {/* Last move marker */}
        {lastMove && (
          <circle
            cx={PADDING + lastMove.col * CELL_SIZE} cy={PADDING + lastMove.row * CELL_SIZE}
            r={5} fill="#E53935" opacity={0.8}
          />
        )}
      </svg>
    </Box>
  );
}

export default GomokuBoard;
