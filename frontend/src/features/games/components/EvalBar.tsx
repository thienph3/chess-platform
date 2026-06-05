import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

interface EvalBarProps {
  /** Đánh giá vị trí tính bằng centipawns (dương = trắng lợi thế) */
  evaluation: number;
  /** Chiều cao thanh đánh giá (px) */
  height?: number;
}

/**
 * Thanh đánh giá dọc hiển thị ai đang thắng.
 * Phần trắng mở rộng/thu hẹp dựa trên evaluation.
 */
function EvalBar({ evaluation, height = 400 }: EvalBarProps) {
  // Chuyển centipawns thành phần trăm (sigmoid-like scaling)
  const clampedEval = Math.max(-1000, Math.min(1000, evaluation));
  const whitePercent = 50 + (clampedEval / 1000) * 50;

  const displayEval = formatEval(evaluation);

  return (
    <Box
      sx={{
        width: 32,
        height,
        borderRadius: 1,
        overflow: "hidden",
        border: "1px solid",
        borderColor: "grey.400",
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
      aria-label={`Đánh giá: ${displayEval}`}
    >
      {/* Phần đen (trên) */}
      <Box
        sx={{
          flex: `${100 - whitePercent} 0 0`,
          bgcolor: "grey.800",
          transition: "flex 0.3s ease",
        }}
      />
      {/* Phần trắng (dưới) */}
      <Box
        sx={{
          flex: `${whitePercent} 0 0`,
          bgcolor: "grey.100",
          transition: "flex 0.3s ease",
        }}
      />
      {/* Hiển thị số eval */}
      <Typography
        variant="caption"
        sx={{
          position: "absolute",
          top: 4,
          left: 0,
          right: 0,
          textAlign: "center",
          fontWeight: 700,
          fontSize: 10,
          color: evaluation >= 0 ? "grey.100" : "grey.800",
        }}
      >
        {displayEval}
      </Typography>
    </Box>
  );
}

function formatEval(centipawns: number): string {
  if (Math.abs(centipawns) >= 10000) {
    return centipawns > 0 ? "+M" : "-M";
  }
  const pawns = centipawns / 100;
  return pawns > 0 ? `+${pawns.toFixed(1)}` : pawns.toFixed(1);
}

export default EvalBar;
