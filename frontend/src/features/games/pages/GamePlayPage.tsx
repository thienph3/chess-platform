import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import FlagIcon from "@mui/icons-material/Flag";
import FlipCameraAndroidIcon from "@mui/icons-material/FlipCameraAndroid";
import HandshakeIcon from "@mui/icons-material/Handshake";
import ReplayIcon from "@mui/icons-material/Replay";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Chess } from "chess.js";
import { useCallback, useEffect, useRef, useState } from "react";
import { Chessboard } from "react-chessboard";
import { useNavigate, useParams } from "react-router-dom";

import PlayerName from "@/components/PlayerName";
import { parseGomokuFen } from "@/utils/gameConstants";

import GameChat from "../components/GameChat";
import GoBoard from "../components/GoBoard";
import GomokuBoard from "../components/GomokuBoard";
import XiangqiBoard from "../components/XiangqiBoard";
import { useCreateGameRoom, useGameRoom } from "../hooks/useGames";

type GamePhase = "waiting" | "ready" | "countdown" | "playing" | "finished";

function formatClock(ms: number): string {
  if (ms <= 0) return "0:00";
  const totalSec = Math.ceil(ms / 1000);
  const min = Math.floor(totalSec / 60);
  const sec = totalSec % 60;
  return `${min}:${sec.toString().padStart(2, "0")}`;
}

function GamePlayPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: room, isLoading } = useGameRoom(id || "");
  const createMutation = useCreateGameRoom();

  // Game state
  const [phase, setPhase] = useState<GamePhase>("waiting");
  const [fen, setFen] = useState("");
  const [turn, setTurn] = useState<"white" | "black">("white");
  const [moves, setMoves] = useState<string[]>([]);
  const [gameOver, setGameOver] = useState<string | null>(null);
  const [readyCount, setReadyCount] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [isReady, setIsReady] = useState(false);

  // Clocks
  const [whiteClock, setWhiteClock] = useState(0);
  const [blackClock, setBlackClock] = useState(0);

  // Board state
  const [game, setGame] = useState(new Chess());
  const [boardOrientation, setBoardOrientation] = useState<"white" | "black">("white");

  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    if (!id) return;
    const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/game/${id}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      switch (msg.type) {
        case "waiting":
        case "room_info":
          setPhase("waiting");
          if (msg.white_clock) setWhiteClock(msg.white_clock);
          if (msg.black_clock) setBlackClock(msg.black_clock);
          break;

        case "ready_status":
          setReadyCount(msg.ready_count);
          setPhase("ready");
          break;

        case "countdown":
          setPhase("countdown");
          setCountdown(msg.seconds);
          break;

        case "game_start":
          setPhase("playing");
          setFen(msg.fen);
          setTurn(msg.turn);
          setWhiteClock(msg.white_clock);
          setBlackClock(msg.black_clock);
          if (room?.game_type === "chess") setGame(new Chess(msg.fen));
          break;

        case "state":
          // Reconnect — game already in progress
          setPhase(msg.started ? "playing" : "waiting");
          setFen(msg.fen);
          setTurn(msg.turn);
          if (msg.white_clock) setWhiteClock(msg.white_clock);
          if (msg.black_clock) setBlackClock(msg.black_clock);
          if (room?.game_type === "chess" && msg.fen) setGame(new Chess(msg.fen));
          break;

        case "move":
          setFen(msg.fen);
          setTurn(msg.turn);
          setWhiteClock(msg.white_clock);
          setBlackClock(msg.black_clock);
          if (room?.game_type === "chess" && msg.fen) setGame(new Chess(msg.fen));
          setMoves((prev) => [...prev, msg.notation || `${msg.row ?? ""},${msg.col ?? ""}`]);
          break;

        case "game_over":
          setPhase("finished");
          setGameOver(`${msg.result} — ${msg.reason}`);
          if (msg.white_clock) setWhiteClock(msg.white_clock);
          if (msg.black_clock) setBlackClock(msg.black_clock);
          break;

        case "player_disconnected":
          // Could show notification
          break;

        case "error":
          // Could show snackbar
          break;
      }
    };

    ws.onopen = () => {
      if (room?.game_type) {
        ws.send(JSON.stringify({ type: "init", game_type: room.game_type }));
      }
    };

    return () => { ws.close(); };
  }, [id, room?.game_type]);

  // Actions
  const handleReady = () => {
    wsRef.current?.send(JSON.stringify({ type: "ready" }));
    setIsReady(true);
  };

  const handleMove = useCallback((move: Record<string, unknown>) => {
    if (phase !== "playing") return;
    wsRef.current?.send(JSON.stringify({ type: "move", ...move }));
  }, [phase]);

  const handleChessDrop = useCallback(({ sourceSquare, targetSquare }: { piece: unknown; sourceSquare: string; targetSquare: string | null }) => {
    if (!targetSquare || phase !== "playing") return false;
    handleMove({ from: sourceSquare, to: targetSquare, promotion: "q" });
    return true;
  }, [phase, handleMove]);

  const handleXiangqiMove = useCallback((from: string, to: string) => {
    if (phase !== "playing") return false;
    handleMove({ from, to });
    return true;
  }, [phase, handleMove]);

  const handleGoPlace = useCallback((row: number, col: number) => {
    if (phase !== "playing") return false;
    handleMove({ row, col, notation: `${String.fromCharCode(97 + col)}${row + 1}` });
    return true;
  }, [phase, handleMove]);

  const handleGomokuPlace = useCallback((row: number, col: number) => {
    if (phase !== "playing") return;
    handleMove({ row, col });
  }, [phase, handleMove]);

  const handleResign = () => wsRef.current?.send(JSON.stringify({ type: "resign" }));
  const handleDrawOffer = () => wsRef.current?.send(JSON.stringify({ type: "draw_offer" }));

  const handleRematch = async () => {
    if (!room) return;
    const newRoom = await createMutation.mutateAsync({ game_type: room.game_type, time_control: room.time_control, increment: room.increment || 0 });
    navigate(`/play/${newRoom.id}`);
  };

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={500} sx={{ borderRadius: 2 }} /></Box>;
  if (!room) return <Box p={3}><Typography>Phòng không tồn tại</Typography></Box>;

  const allowInteraction = phase === "playing" && !gameOver;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} size="small" sx={{ mb: 1 }}>Lobby</Button>

      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="flex-start">
        {/* Board Area */}
        <Box sx={{ flex: 1 }}>
          {/* Top player (Black) */}
          <PlayerBar memberId={room.black_player_id || ""} clock={blackClock} isActive={phase === "playing" && turn === "black"} color="black" />

          {/* Countdown / Ready overlay */}
          {phase === "countdown" && (
            <Box sx={{ textAlign: "center", py: 2 }}>
              <Typography variant="h2" fontWeight={800} color="primary">{countdown}</Typography>
              <Typography variant="body2" color="text.secondary">Bắt đầu sau...</Typography>
            </Box>
          )}

          {/* Board */}
          {phase !== "countdown" && (
            <Box sx={{ my: 1 }}>
              {room.game_type === "chess" && (
                <Box sx={{ width: { xs: 320, sm: 400, md: 480 } }}>
                  <Chessboard options={{ position: game.fen(), onPieceDrop: handleChessDrop, allowDragging: allowInteraction, boardOrientation }} />
                </Box>
              )}
              {room.game_type === "xiangqi" && <XiangqiBoard position={fen} onMove={handleXiangqiMove} allowDragging={allowInteraction} />}
              {room.game_type === "go" && <GoBoard size={19} stones={[]} onPlace={handleGoPlace} allowPlacing={allowInteraction} />}
              {room.game_type === "gomoku" && <GomokuBoard stones={parseGomokuFen(fen)} onPlace={handleGomokuPlace} allowPlacing={allowInteraction} />}
            </Box>
          )}

          {/* Bottom player (White) */}
          <PlayerBar memberId={room.white_player_id} clock={whiteClock} isActive={phase === "playing" && turn === "white"} color="white" />
        </Box>

        {/* Side Panel */}
        <Card sx={{ width: { xs: "100%", md: 300 }, display: "flex", flexDirection: "column" }}>
          <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
            {/* Ready phase */}
            {(phase === "waiting" || phase === "ready") && (
              <Box sx={{ textAlign: "center", py: 4 }}>
                <Typography variant="body1" mb={2}>Sẵn sàng: {readyCount}/2</Typography>
                <Button
                  variant="contained" size="large" fullWidth
                  startIcon={<CheckCircleIcon />}
                  onClick={handleReady}
                  disabled={isReady}
                  color={isReady ? "success" : "primary"}
                >
                  {isReady ? "Đã sẵn sàng" : "Sẵn sàng"}
                </Button>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                  Cả 2 người chơi cần nhấn "Sẵn sàng" để bắt đầu
                </Typography>
              </Box>
            )}

            {/* Move list */}
            {(phase === "playing" || phase === "finished") && (
              <Box sx={{ flex: 1, overflow: "auto", maxHeight: { md: 350 }, mb: 2 }}>
                {moves.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center", py: 4 }}>Chưa có nước đi</Typography>
                ) : (
                  moves.map((m, i) => {
                    if (i % 2 !== 0) return null;
                    const num = Math.floor(i / 2) + 1;
                    return (
                      <Stack key={num} direction="row" sx={{ py: 0.5, px: 1, bgcolor: num % 2 === 0 ? "rgba(0,0,0,0.02)" : "transparent", borderRadius: 1 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ width: 32, fontFamily: "monospace", fontSize: "0.8rem" }}>{num}.</Typography>
                        <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem", fontWeight: 500 }}>{m}</Typography>
                        <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem" }}>{moves[i + 1] || ""}</Typography>
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
            )}

            {/* Actions */}
            {phase === "playing" && !gameOver && (
              <Stack spacing={1}>
                <Stack direction="row" spacing={1}>
                  <Button size="small" variant="outlined" color="error" startIcon={<FlagIcon />} fullWidth onClick={handleResign}>Đầu hàng</Button>
                  <Button size="small" variant="outlined" startIcon={<HandshakeIcon />} fullWidth onClick={handleDrawOffer}>Cầu hòa</Button>
                </Stack>
                <IconButton size="small" onClick={() => setBoardOrientation((p) => p === "white" ? "black" : "white")}><FlipCameraAndroidIcon /></IconButton>
              </Stack>
            )}
            {phase === "finished" && (
              <Button size="small" variant="contained" startIcon={<ReplayIcon />} fullWidth onClick={handleRematch} disabled={createMutation.isPending}>Chơi lại</Button>
            )}

            {/* Chat */}
            <Box sx={{ mt: 2 }}>
              <GameChat wsRef={wsRef} disabled={phase === "finished"} />
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}

function PlayerBar({ memberId, clock, isActive, color }: { memberId: string; clock: number; isActive: boolean; color: "white" | "black" }) {
  const isLow = clock > 0 && clock < 30000;
  return (
    <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1.5, py: 1, borderRadius: 1, bgcolor: isActive ? "rgba(0,98,65,0.06)" : "transparent" }}>
      <PlayerName memberId={memberId} />
      <Chip
        label={formatClock(clock)}
        size="small"
        sx={{
          fontFamily: "monospace", fontWeight: 700, fontSize: "0.9rem", minWidth: 70,
          bgcolor: isActive ? "primary.main" : "#f5f5f5",
          color: isActive ? "white" : (isLow ? "error.main" : "text.primary"),
        }}
      />
    </Stack>
  );
}

export default GamePlayPage;
