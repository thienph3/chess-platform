import ArrowBack from "@mui/icons-material/ArrowBack";
import ArrowForward from "@mui/icons-material/ArrowForward";
import SkipNext from "@mui/icons-material/SkipNext";
import SkipPrevious from "@mui/icons-material/SkipPrevious";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Chess } from "chess.js";
import { useMemo } from "react";
import { Chessboard } from "react-chessboard";

import { IMoveHistory } from "../types";

interface ReplayBoardProps {
  moves: IMoveHistory[];
  currentMoveIndex: number;
  onFirst: () => void;
  onPrev: () => void;
  onNext: () => void;
  onLast: () => void;
}

function ReplayBoard({
  moves,
  currentMoveIndex,
  onFirst,
  onPrev,
  onNext,
  onLast,
}: ReplayBoardProps) {
  const fen = useMemo(() => {
    const game = new Chess();
    for (let i = 0; i < currentMoveIndex; i++) {
      try {
        game.move(moves[i].notation);
      } catch {
        break;
      }
    }
    return game.fen();
  }, [moves, currentMoveIndex]);

  const currentNotation = currentMoveIndex > 0 ? moves[currentMoveIndex - 1]?.notation : "—";
  const totalMoves = moves.length;

  return (
    <Box>
      <Box sx={{ width: { xs: 320, sm: 400, md: 480 }, mx: "auto" }}>
        <Chessboard options={{ position: fen, allowDragging: false }} />
      </Box>

      <Stack direction="row" justifyContent="center" alignItems="center" spacing={1} mt={2}>
        <IconButton onClick={onFirst} disabled={currentMoveIndex === 0} aria-label="Về đầu">
          <SkipPrevious />
        </IconButton>
        <IconButton onClick={onPrev} disabled={currentMoveIndex === 0} aria-label="Lùi một nước">
          <ArrowBack />
        </IconButton>
        <Typography variant="body2" sx={{ minWidth: 100, textAlign: "center" }}>
          {currentMoveIndex} / {totalMoves} — {currentNotation}
        </Typography>
        <IconButton onClick={onNext} disabled={currentMoveIndex >= totalMoves} aria-label="Tiến một nước">
          <ArrowForward />
        </IconButton>
        <IconButton onClick={onLast} disabled={currentMoveIndex >= totalMoves} aria-label="Về cuối">
          <SkipNext />
        </IconButton>
      </Stack>
    </Box>
  );
}

export default ReplayBoard;
