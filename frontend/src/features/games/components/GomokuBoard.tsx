import Box from "@mui/material/Box";
import { useCallback, useState } from "react";

interface GomokuBoardProps {
  size?: number;
  stones: { row: number; col: number; color: "black" | "white" }[];
  onPlace?: (row: number, col: number) => void;
  allowPlacing?: boolean;
  lastMove?: { row: number; col: number } | null;
}

const CELL_SIZE = 32;
const PADDING = 20;

function GomokuBoard({ size = 15, stones, onPlace, allowPlacing = true, lastMove }: GomokuBoardProps) {
  const [hover, setHover] = useState<{ row: number; col: number } | null>(null);
  const svgSize = (size - 1) * CELL_SIZE + PADDING * 2;

  const hasStone = useCallback(
    (row: number, col: number) => stones.find((s) => s.row === row && s.col === col),
    [stones]
  );

  const lastStone = lastMove || (stones.length > 0 ? stones[stones.length - 1] : null);

  return (
    <Box sx={{ display: "inline-block" }}>
      <svg
        width={svgSize} height={svgSize}
        style={{ background: "#FFFFFF", borderRadius: 4, border: "1px solid #e0e0e0" }}
        role="img" aria-label="Bàn cờ caro"
      >
        {/* Grid lines */}
        {Array.from({ length: size }, (_, i) => (
          <g key={`grid-${i}`}>
            <line
              x1={PADDING} y1={PADDING + i * CELL_SIZE}
              x2={PADDING + (size - 1) * CELL_SIZE} y2={PADDING + i * CELL_SIZE}
              stroke="#c8d4e0" strokeWidth={0.8}
            />
            <line
              x1={PADDING + i * CELL_SIZE} y1={PADDING}
              x2={PADDING + i * CELL_SIZE} y2={PADDING + (size - 1) * CELL_SIZE}
              stroke="#c8d4e0" strokeWidth={0.8}
            />
          </g>
        ))}

        {/* Click targets (on intersections) */}
        {Array.from({ length: size }, (_, r) =>
          Array.from({ length: size }, (_, c) =>
            !hasStone(r, c) && (
              <circle
                key={`t-${r}-${c}`}
                cx={PADDING + c * CELL_SIZE} cy={PADDING + r * CELL_SIZE}
                r={CELL_SIZE / 2 - 1}
                fill="transparent"
                style={{ cursor: allowPlacing ? "pointer" : "default" }}
                onClick={() => allowPlacing && onPlace?.(r, c)}
                onMouseEnter={() => setHover({ row: r, col: c })}
                onMouseLeave={() => setHover(null)}
              />
            )
          )
        )}

        {/* Hover indicator */}
        {hover && allowPlacing && !hasStone(hover.row, hover.col) && (
          <text
            x={PADDING + hover.col * CELL_SIZE}
            y={PADDING + hover.row * CELL_SIZE + 1}
            textAnchor="middle" dominantBaseline="central"
            fontSize={18} fontWeight={700} fill="rgba(0,0,0,0.15)"
          >
            {stones.length % 2 === 0 ? "✕" : "○"}
          </text>
        )}

        {/* Pieces — X and O on intersections */}
        {stones.map((s, i) => {
          const cx = PADDING + s.col * CELL_SIZE;
          const cy = PADDING + s.row * CELL_SIZE;
          const isLast = lastStone && lastStone.row === s.row && lastStone.col === s.col;

          if (s.color === "black") {
            // X mark (blue)
            const d = 8;
            return (
              <g key={i}>
                {isLast && <circle cx={cx} cy={cy} r={13} fill="#e3f2fd" />}
                <line x1={cx - d} y1={cy - d} x2={cx + d} y2={cy + d} stroke="#1565c0" strokeWidth={2.5} strokeLinecap="round" />
                <line x1={cx + d} y1={cy - d} x2={cx - d} y2={cy + d} stroke="#1565c0" strokeWidth={2.5} strokeLinecap="round" />
              </g>
            );
          } else {
            // O mark (red)
            return (
              <g key={i}>
                {isLast && <circle cx={cx} cy={cy} r={13} fill="#fce4ec" />}
                <circle cx={cx} cy={cy} r={9} fill="none" stroke="#c62828" strokeWidth={2.5} />
              </g>
            );
          }
        })}
      </svg>
    </Box>
  );
}

export default GomokuBoard;
