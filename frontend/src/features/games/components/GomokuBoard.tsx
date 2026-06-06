import Box from "@mui/material/Box";
import { useCallback, useState } from "react";

interface GomokuBoardProps {
  size?: number;
  stones: { row: number; col: number; color: "black" | "white" }[];
  onPlace?: (row: number, col: number) => void;
  allowPlacing?: boolean;
  lastMove?: { row: number; col: number } | null;
}

const CELL_SIZE = 34;
const PADDING = 2;

function GomokuBoard({ size = 15, stones, onPlace, allowPlacing = true, lastMove }: GomokuBoardProps) {
  const [hover, setHover] = useState<{ row: number; col: number } | null>(null);
  const svgSize = size * CELL_SIZE + PADDING * 2;

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
        {/* Grid lines (squares, not intersections) */}
        {Array.from({ length: size + 1 }, (_, i) => (
          <g key={`grid-${i}`}>
            <line
              x1={PADDING} y1={PADDING + i * CELL_SIZE}
              x2={PADDING + size * CELL_SIZE} y2={PADDING + i * CELL_SIZE}
              stroke="#c8d4e0" strokeWidth={0.8}
            />
            <line
              x1={PADDING + i * CELL_SIZE} y1={PADDING}
              x2={PADDING + i * CELL_SIZE} y2={PADDING + size * CELL_SIZE}
              stroke="#c8d4e0" strokeWidth={0.8}
            />
          </g>
        ))}

        {/* Click targets (inside cells) */}
        {Array.from({ length: size }, (_, r) =>
          Array.from({ length: size }, (_, c) =>
            !hasStone(r, c) && (
              <rect
                key={`t-${r}-${c}`}
                x={PADDING + c * CELL_SIZE + 1} y={PADDING + r * CELL_SIZE + 1}
                width={CELL_SIZE - 2} height={CELL_SIZE - 2}
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
            x={PADDING + hover.col * CELL_SIZE + CELL_SIZE / 2}
            y={PADDING + hover.row * CELL_SIZE + CELL_SIZE / 2 + 1}
            textAnchor="middle" dominantBaseline="central"
            fontSize={20} fontWeight={700} fill="rgba(0,0,0,0.15)"
          >
            {stones.length % 2 === 0 ? "✕" : "○"}
          </text>
        )}

        {/* Pieces — X and O */}
        {stones.map((s, i) => {
          const cx = PADDING + s.col * CELL_SIZE + CELL_SIZE / 2;
          const cy = PADDING + s.row * CELL_SIZE + CELL_SIZE / 2;
          const isLast = lastStone && lastStone.row === s.row && lastStone.col === s.col;

          if (s.color === "black") {
            // X mark (blue)
            const offset = 9;
            return (
              <g key={i}>
                {isLast && <rect x={PADDING + s.col * CELL_SIZE + 2} y={PADDING + s.row * CELL_SIZE + 2} width={CELL_SIZE - 4} height={CELL_SIZE - 4} fill="#e3f2fd" rx={3} />}
                <line x1={cx - offset} y1={cy - offset} x2={cx + offset} y2={cy + offset} stroke="#1565c0" strokeWidth={2.5} strokeLinecap="round" />
                <line x1={cx + offset} y1={cy - offset} x2={cx - offset} y2={cy + offset} stroke="#1565c0" strokeWidth={2.5} strokeLinecap="round" />
              </g>
            );
          } else {
            // O mark (red)
            return (
              <g key={i}>
                {isLast && <rect x={PADDING + s.col * CELL_SIZE + 2} y={PADDING + s.row * CELL_SIZE + 2} width={CELL_SIZE - 4} height={CELL_SIZE - 4} fill="#fce4ec" rx={3} />}
                <circle cx={cx} cy={cy} r={10} fill="none" stroke="#c62828" strokeWidth={2.5} />
              </g>
            );
          }
        })}
      </svg>
    </Box>
  );
}

export default GomokuBoard;
