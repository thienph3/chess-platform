import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Chess } from "chess.js";
import { useEffect, useRef, useState } from "react";
import { Chessboard } from "react-chessboard";
import { useNavigate, useParams } from "react-router-dom";

import PlayerName from "@/components/PlayerName";

import { useGameRoom } from "../hooks/useGames";

function SpectatorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: room, isLoading } = useGameRoom(id || "");
  const [game, setGame] = useState(new Chess());
  const [moves, setMoves] = useState<string[]>([]);
  const [gameOver, setGameOver] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!id) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/game/${id}`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "state") setGame(new Chess(msg.fen));
      else if (msg.type === "move") { setGame(new Chess(msg.fen)); setMoves((p) => [...p, `${msg.from}${msg.to}`]); }
      else if (msg.type === "game_over") {
        const r: Record<string, string> = { white_win: "1-0", black_win: "0-1", draw: "½-½" };
        setGameOver(r[msg.result] || msg.result);
      }
    };
    return () => { ws.close(); };
  }, [id]);

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={500} /></Box>;
  if (!room) return <Box p={3}><Typography>Phòng không tồn tại</Typography></Box>;

  return (
    <Box>
      <Stack direction="row" alignItems="center" spacing={1} mb={1}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} size="small">Lobby</Button>
        <Chip icon={<VisibilityIcon />} label="Đang xem trực tiếp" size="small" color="warning" />
      </Stack>
      <Stack direction={{ xs: "column", md: "row" }} spacing={0} alignItems="flex-start">
        <Box>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mb: 0.5 }}>
            <PlayerName memberId={room.black_player_id || ""} />
          </Stack>
          <Box sx={{ width: { xs: 320, sm: 400, md: 480 } }}>
            <Chessboard options={{ position: game.fen(), allowDragging: false }} />
          </Box>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mt: 0.5 }}>
            <PlayerName memberId={room.white_player_id} />
          </Stack>
        </Box>
        <Card sx={{ width: { xs: "100%", md: 280 }, ml: { md: 2 }, mt: { xs: 2, md: 0 }, height: { md: 540 }, display: "flex", flexDirection: "column" }}>
          <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
            <Box sx={{ flex: 1, overflow: "auto" }}>
              {moves.length === 0 ? (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>Đang chờ nước đi...</Typography>
              ) : (
                moves.filter((_, i) => i % 2 === 0).map((_, i) => {
                  const num = i + 1;
                  const idx = i * 2;
                  return (
                    <Stack key={num} direction="row" sx={{ py: 0.5, px: 1, bgcolor: num % 2 === 0 ? "rgba(0,0,0,0.02)" : "transparent", borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ width: 32, fontFamily: "monospace", fontSize: "0.8rem" }}>{num}.</Typography>
                      <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem", fontWeight: 500 }}>{moves[idx]}</Typography>
                      <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem" }}>{moves[idx + 1] || ""}</Typography>
                    </Stack>
                  );
                })
              )}
              {gameOver && (
                <Typography variant="body2" fontWeight={700} sx={{ mt: 1, py: 1, fontFamily: "monospace", textAlign: "center", bgcolor: "rgba(0,0,0,0.04)", borderRadius: 1 }}>
                  {gameOver}
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}

export default SpectatorPage;
