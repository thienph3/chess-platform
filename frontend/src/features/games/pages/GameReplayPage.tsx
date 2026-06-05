import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DownloadIcon from "@mui/icons-material/Download";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import IconButton from "@mui/material/IconButton";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Chess } from "chess.js";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Chessboard } from "react-chessboard";
import { useNavigate, useParams } from "react-router-dom";

import PlayerName from "@/components/PlayerName";

import EvalBar from "../components/EvalBar";
import { useExportPgn } from "../hooks/useExportPgn";
import { useGameMoves } from "../hooks/useGameMoves";
import { useGameRoom } from "../hooks/useGames";
import { classificationColor, classificationToSymbol, formatEval } from "../hooks/useGameReview";
import { useReviewGame } from "../hooks/useGameHistory";

function GameReplayPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: moves, isLoading, refetch: refetchMoves } = useGameMoves(id || "");
  const { data: room, refetch: refetchRoom } = useGameRoom(id || "");
  const { exportPgn } = useExportPgn();
  const reviewMutation = useReviewGame();
  const [moveIndex, setMoveIndex] = useState(0);
  const [reviewing, setReviewing] = useState(false);

  // Auto-review khi mở page
  useEffect(() => {
    if (!id || !room || room.status !== "finished") return;
    setReviewing(true);
    reviewMutation.mutate(id, {
      onSuccess: () => { refetchRoom(); refetchMoves(); setReviewing(false); },
      onError: () => setReviewing(false),
    });
  }, [id, room?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const fen = useMemo(() => {
    if (!moves || moveIndex === 0) return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    const chess = new Chess();
    for (let i = 0; i < moveIndex && i < moves.length; i++) {
      try { chess.move({ from: moves[i].notation.slice(0, 2), to: moves[i].notation.slice(2, 4), promotion: moves[i].notation[4] || undefined }); }
      catch { break; }
    }
    return chess.fen();
  }, [moves, moveIndex]);

  const handleFirst = useCallback(() => setMoveIndex(0), []);
  const handlePrev = useCallback(() => setMoveIndex((i) => Math.max(0, i - 1)), []);
  const handleNext = useCallback(() => setMoveIndex((i) => Math.min(moves?.length || 0, i + 1)), [moves?.length]);
  const handleLast = useCallback(() => setMoveIndex(moves?.length || 0), [moves?.length]);

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") handlePrev();
      else if (e.key === "ArrowRight") handleNext();
      else if (e.key === "Home") handleFirst();
      else if (e.key === "End") handleLast();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleFirst, handlePrev, handleNext, handleLast]);

  // Current eval at moveIndex
  const currentEval = useMemo(() => {
    if (!moves || moveIndex === 0) return 0;
    const m = moves[moveIndex - 1];
    return m?.eval_after ?? 0;
  }, [moves, moveIndex]);

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={500} /></Box>;

  // Convert UCI notations to SAN
  const sanMoves = useMemo(() => {
    if (!moves) return [];
    const chess = new Chess();
    return moves.map((m) => {
      try {
        const result = chess.move({ from: m.notation.slice(0, 2), to: m.notation.slice(2, 4), promotion: m.notation[4] || undefined });
        return result ? result.san : m.notation;
      } catch {
        return m.notation;
      }
    });
  }, [moves]);

  const result = room?.result;
  const resultStr = result === "white_win" ? "1-0" : result === "black_win" ? "0-1" : result === "draw" ? "½-½" : "";
  const isReviewed = room?.is_reviewed && moves?.[0]?.classification != null;

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play/history")} size="small">Lịch sử</Button>
        {id && <Button variant="outlined" size="small" startIcon={<DownloadIcon />} onClick={() => exportPgn(id)}>PGN</Button>}
      </Stack>
      <Stack direction={{ xs: "column", md: "row" }} spacing={0} alignItems="flex-start">
        {/* Eval Bar */}
        {isReviewed && (
          <EvalBar evaluation={currentEval} height={480} />
        )}

        <Box>
          <Stack direction="row" alignItems="center" sx={{ px: 1, py: 0.75, mb: 0.5 }}>
            <PlayerName memberId={room?.black_player_id || ""} />
          </Stack>
          <Box sx={{ width: { xs: 320, sm: 400, md: 480 } }}>
            <Chessboard options={{ position: fen, allowDragging: false }} />
          </Box>
          <Stack direction="row" alignItems="center" sx={{ px: 1, py: 0.75, mt: 0.5 }}>
            <PlayerName memberId={room?.white_player_id || ""} />
          </Stack>
          {/* Navigation controls */}
          <Stack direction="row" justifyContent="center" spacing={1} mt={1}>
            <IconButton size="small" onClick={handleFirst} disabled={moveIndex === 0}><SkipPreviousIcon /><SkipPreviousIcon sx={{ ml: -1.5 }} /></IconButton>
            <IconButton size="small" onClick={handlePrev} disabled={moveIndex === 0}><SkipPreviousIcon /></IconButton>
            <Typography variant="body2" sx={{ lineHeight: "34px", fontFamily: "monospace" }}>{moveIndex}/{moves?.length || 0}</Typography>
            <IconButton size="small" onClick={handleNext} disabled={moveIndex >= (moves?.length || 0)}><SkipNextIcon /></IconButton>
            <IconButton size="small" onClick={handleLast} disabled={moveIndex >= (moves?.length || 0)}><SkipNextIcon /><SkipNextIcon sx={{ ml: -1.5 }} /></IconButton>
          </Stack>
        </Box>
        <Card sx={{ width: { xs: "100%", md: 280 }, ml: { md: 2 }, mt: { xs: 2, md: 0 }, height: { md: 560 }, display: "flex", flexDirection: "column" }}>
          <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} mb={1}>
              <Typography variant="subtitle2" fontWeight={600}>Nước đi</Typography>
              {reviewing && (
                <Chip label="Đang phân tích..." size="small" color="warning" icon={<CircularProgress size={12} />} />
              )}
            </Stack>
            {isReviewed && !reviewing && room && (
              <Stack spacing={0.5} mb={1.5}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: "grey.100", border: "1px solid grey" }} />
                  <Box sx={{ flex: 1, height: 6, borderRadius: 3, bgcolor: "grey.200" }}>
                    <Box sx={{ width: `${room.white_accuracy || 0}%`, height: "100%", borderRadius: 3, bgcolor: "#96BC4B" }} />
                  </Box>
                  <Typography variant="caption" fontWeight={600} sx={{ width: 36 }}>{room.white_accuracy?.toFixed(0)}%</Typography>
                </Stack>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: "grey.800" }} />
                  <Box sx={{ flex: 1, height: 6, borderRadius: 3, bgcolor: "grey.200" }}>
                    <Box sx={{ width: `${room.black_accuracy || 0}%`, height: "100%", borderRadius: 3, bgcolor: "#96BC4B" }} />
                  </Box>
                  <Typography variant="caption" fontWeight={600} sx={{ width: 36 }}>{room.black_accuracy?.toFixed(0)}%</Typography>
                </Stack>
              </Stack>
            )}
            <Box sx={{ flex: 1, overflow: "auto" }}>
              {sanMoves.filter((_, i) => i % 2 === 0).map((_, i) => {
                const num = i + 1;
                const idx = i * 2;
                const whiteMove = moves?.[idx];
                const blackMove = moves?.[idx + 1];
                const wSym = classificationToSymbol(whiteMove?.classification || null);
                const bSym = classificationToSymbol(blackMove?.classification || null);
                const wColor = classificationColor(whiteMove?.classification || null);
                const bColor = classificationColor(blackMove?.classification || null);
                return (
                  <Stack key={num} direction="row" alignItems="center" sx={{
                    py: 0.4, px: 1, borderRadius: 1, cursor: "pointer",
                    bgcolor: (moveIndex === idx + 1 || moveIndex === idx + 2) ? "rgba(0,101,62,0.08)" : num % 2 === 0 ? "rgba(0,0,0,0.02)" : "transparent",
                  }} onClick={() => setMoveIndex(idx + 2)}>
                    <Typography variant="body2" color="text.secondary" sx={{ width: 28, fontFamily: "monospace", fontSize: "0.75rem" }}>{num}.</Typography>
                    <Typography variant="body2" sx={{ width: 72, fontFamily: "monospace", fontSize: "0.75rem", fontWeight: moveIndex === idx + 1 ? 700 : 500, color: wColor }}>
                      {sanMoves[idx]}{wSym}
                    </Typography>
                    <Typography variant="body2" sx={{ width: 72, fontFamily: "monospace", fontSize: "0.75rem", fontWeight: moveIndex === idx + 2 ? 700 : 400, color: bColor }}>
                      {sanMoves[idx + 1] || ""}{bSym}
                    </Typography>
                    {isReviewed && whiteMove?.eval_after != null && (
                      <Typography variant="caption" sx={{ width: 40, textAlign: "right", fontFamily: "monospace", fontSize: "0.65rem", color: (blackMove?.eval_after ?? whiteMove.eval_after) > 0 ? "text.primary" : "error.main" }}>
                        {formatEval(blackMove?.eval_after ?? whiteMove.eval_after)}
                      </Typography>
                    )}
                  </Stack>
                );
              })}
              {resultStr && (
                <Typography variant="body2" fontWeight={700} sx={{ mt: 1, py: 1, fontFamily: "monospace", textAlign: "center", bgcolor: "rgba(0,0,0,0.04)", borderRadius: 1 }}>
                  {resultStr}
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}

export default GameReplayPage;
