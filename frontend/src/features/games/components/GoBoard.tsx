import Box from "@mui/material/Box";
import { useCallback, useState } from "react";

interface GoBoardProps {
  size?: 9 | 13 | 19;
  stones: { row: number; col: number; color: "black" | "white" }[];
  onPlace?: (row: number, col: number) => boolean;
  allowPlacing?: boolean;
}

const CELL_SIZE = 28;
const PADDING = 20;

// Star points (hoshi) cho bàn 19x19
const STAR_POINTS_19 = [[3, 3], [3, 9], [3, 15], [9, 3], [9, 9], [9, 15], [15, 3], [15, 9], [15, 15]];
const STAR_POINTS_13 = [[3, 3], [3, 9], [6, 6], [9, 3], [9, 9]];
const STAR_POINTS_9 = [[2, 2], [2, 6], [4, 4], [6, 2], [6, 6]];

function getStarPoints(size: number): number[][] {
  if (size === 19) return STAR_POINTS_19;
  if (size === 13) return STAR_POINTS_13;
  return STAR_POINTS_9;
}

function GoBoard({ size = 19, stones, onPlace, allowPlacing = true }: GoBoardProps) {
  const [hover, setHover] = useState<{ row: number; col: number } | null>(null);

  const svgSize = (size - 1) * CELL_SIZE + PADDING * 2;
  const starPoints = getStarPoints(size);

  const handleClick = useCallback((row: number, col: number) => {
    if (!allowPlacing) return;
    if (onPlace) onPlace(row, col);
  }, [onPlace, allowPlacing]);

  const hasStone = (row: number, col: number) => stones.find((s) => s.row === row && s.col === col);

  return (
    <Box sx={{ display: "inline-block" }}>
      <svg width={svgSize} height={svgSize} style={{ background: "#DCB35C" }}>
        {/* Lưới */}
        {Array.from({ length: size }, (_, i) => (
          <g key={`grid-${i}`}>
            <line x1={PADDING} y1={PADDING + i * CELL_SIZE} x2={PADDING + (size - 1) * CELL_SIZE} y2={PADDING + i * CELL_SIZE} stroke="#333" strokeWidth={i === 0 || i === size - 1 ? 1.5 : 0.8} />
            <line x1={PADDING + i * CELL_SIZE} y1={PADDING} x2={PADDING + i * CELL_SIZE} y2={PADDING + (size - 1) * CELL_SIZE} stroke="#333" strokeWidth={i === 0 || i === size - 1 ? 1.5 : 0.8} />
          </g>
        ))}
        {/* Star points */}
        {starPoints.map(([r, c]) => (
          <circle key={`star-${r}-${c}`} cx={PADDING + c * CELL_SIZE} cy={PADDING + r * CELL_SIZE} r={3.5} fill="#333" />
        ))}
        {/* Click targets (invisible) */}
        {Array.from({ length: size }, (_, r) =>
          Array.from({ length: size }, (_, c) => !hasStone(r, c) && (
            <circle
              key={`target-${r}-${c}`}
              cx={PADDING + c * CELL_SIZE}
              cy={PADDING + r * CELL_SIZE}
              r={CELL_SIZE / 2 - 2}
              fill="transparent"
              style={{ cursor: allowPlacing ? "pointer" : "default" }}
              onClick={() => handleClick(r, c)}
              onMouseEnter={() => setHover({ row: r, col: c })}
              onMouseLeave={() => setHover(null)}
            />
          ))
        )}
        {/* Hover indicator */}
        {hover && allowPlacing && !hasStone(hover.row, hover.col) && (
          <circle cx={PADDING + hover.col * CELL_SIZE} cy={PADDING + hover.row * CELL_SIZE} r={CELL_SIZE / 2 - 4} fill="rgba(0,0,0,0.2)" />
        )}
        {/* Stones */}
        {stones.map((stone, i) => (
          <circle
            key={i}
            cx={PADDING + stone.col * CELL_SIZE}
            cy={PADDING + stone.row * CELL_SIZE}
            r={CELL_SIZE / 2 - 2}
            fill={stone.color === "black" ? "#111" : "#FFF"}
            stroke="#333"
            strokeWidth={1}
          />
        ))}
      </svg>
    </Box>
  );
}

export default GoBoard;
