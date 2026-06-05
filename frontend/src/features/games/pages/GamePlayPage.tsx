import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import FlagIcon from "@mui/icons-material/Flag";
import FlipCameraAndroidIcon from "@mui/icons-material/FlipCameraAndroid";
import HandshakeIcon from "@mui/icons-material/Handshake";
import ReplayIcon from "@mui/icons-material/Replay";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
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
import { useSoundEffects } from "@/hooks/useSoundEffects";

import GameChat from "../components/GameChat";
import GameClock from "../components/GameClock";
import GoBoard from "../components/GoBoard";
import GomokuBoard from "../components/GomokuBoard";
import XiangqiBoard from "../components/XiangqiBoard";
import { formatCountdown, useCountdown } from "../hooks/useCountdown";
import { useCreateGameRoom, useGameRoom } from "../hooks/useGames";

function GamePlayPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: room, isLoading } = useGameRoom(id || "");
  const createMutation = useCreateGameRoom();
  const { play: playSound, enabled: soundEnabled, toggle: toggleSound } = useSoundEffects();
  const [game, setGame] = useState(new Chess());
  const [moves, setMoves] = useState<string[]>([]);
  const [gameOver, setGameOver] = useState<string | null>(null);
  const [turn, setTurn] = useState<"white" | "black">("white");
  const [boardOrientation, setBoardOrientation] = useState<"white" | "black">("white");
  const [xiangqiFen, setXiangqiFen] = useState("rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR");
  const [goStones, setGoStones] = useState<{ row: number; col: number; color: "black" | "white" }[]>([]);
  const [gomokuStones, setGomokuStones] = useState<{ row: number; col: number; color: "black" | "white" }[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const { secondsLeft, isReady } = useCountdown(room?.scheduled_start || null);

  useEffect(() => {
    if (!id) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/game/${id}`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "state") {
        if (room?.game_type === "chess") setGame(new Chess(msg.fen));
        else if (room?.game_type === "xiangqi") setXiangqiFen(msg.fen || xiangqiFen);
        setTurn(msg.turn);
      } else if (msg.type === "move") {
        if (msg.fen && room?.game_type === "chess") setGame(new Chess(msg.fen));
        else if (msg.fen && room?.game_type === "xiangqi") setXiangqiFen(msg.fen);
        setTurn(msg.turn);
        setMoves((prev) => [...prev, msg.notation || `${msg.from}${msg.to}`]);
        playSound(msg.capture ? "capture" : "move");
      } else if (msg.type === "game_over") {
        const results: Record<string, string> = { white_win: "Trắng thắng", black_win: "Đen thắng", draw: "Hòa" };
        const reasons: Record<string, string> = { checkmate: "Chiếu hết", stalemate: "Hết nước", agreement: "Đồng ý hòa" };
        setGameOver(`${results[msg.result] || msg.result} — ${reasons[msg.reason] || msg.reason}`);
        playSound("gameOver");
      } else if (msg.type === "resign") {
        setGameOver("Đối thủ đầu hàng — Bạn thắng!");
        playSound("gameOver");
      } else if (msg.type === "check") {
        playSound("check");
      }
    };
    return () => { ws.close(); };
  }, [id, room?.game_type]);

  const handleChessDrop = useCallback(({ sourceSquare, targetSquare }: { piece: unknown; sourceSquare: string; targetSquare: string | null }) => {
    if (!targetSquare) return false;
    const copy = new Chess(game.fen());
    const move = copy.move({ from: sourceSquare, to: targetSquare, promotion: "q" });
    if (!move) return false;
    wsRef.current?.send(JSON.stringify({ type: "move", from: sourceSquare, to: targetSquare, promotion: "q" }));
    return true;
  }, [game]);

  const handleXiangqiMove = useCallback((from: string, to: string) => {
    wsRef.current?.send(JSON.stringify({ type: "move", from, to, notation: `${from}${to}` }));
    return true;
  }, []);

  const handleGoPlace = useCallback((row: number, col: number) => {
    const notation = `${String.fromCharCode(97 + col)}${row + 1}`;
    wsRef.current?.send(JSON.stringify({ type: "move", notation, row, col }));
    setGoStones((prev) => [...prev, { row, col, color: turn === "white" ? "white" : "black" }]);
    setMoves((prev) => [...prev, notation]);
    return true;
  }, [turn]);

  const handleGomokuPlace = useCallback((row: number, col: number) => {
    wsRef.current?.send(JSON.stringify({ type: "move", row, col }));
    setGomokuStones((prev) => [...prev, { row, col, color: turn === "white" ? "white" : "black" }]);
    setMoves((prev) => [...prev, `${row},${col}`]);
  }, [turn]);

  // Fix 73: Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "f" || e.key === "F") {
        setBoardOrientation((prev) => (prev === "white" ? "black" : "white"));
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleResign = () => { setGameOver("Bạn đã đầu hàng"); wsRef.current?.send(JSON.stringify({ type: "resign" })); };

  const handleRematch = async () => {
    if (!room) return;
    // Tạo phòng mới với cùng settings, đổi màu quân
    const newRoom = await createMutation.mutateAsync({
      game_type: room.game_type,
      time_control: room.time_control,
      increment: room.increment || 0,
    });
    navigate(`/play/${newRoom.id}`);
  };

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={500} /></Box>;
  if (!room) return <Box p={3}><Typography>Phòng không tồn tại</Typography></Box>;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} size="small" sx={{ mb: 1 }}>Lobby</Button>
      <Stack direction={{ xs: "column", md: "row" }} spacing={0} alignItems="flex-start">
        {/* Board Area */}
        <Box>
          {/* Countdown trước khi bắt đầu */}
          {!isReady && secondsLeft > 0 && (
            <Chip label={`Bắt đầu sau ${formatCountdown(secondsLeft)}`} color="warning" sx={{ mb: 1, fontFamily: "monospace", fontWeight: 600 }} />
          )}

          {/* Opponent bar (black) */}
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mb: 0.5 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <PlayerName memberId={room.black_player_id || ""} />
            </Stack>
            <GameClock initialTime={room.time_control} isActive={isReady && !gameOver && turn === "black"} color="black" increment={room.increment || 0} />
          </Stack>

          {/* Board */}
          <BoardRenderer gameType={room.game_type} chessFen={game.fen()} xiangqiFen={xiangqiFen} goStones={goStones} gomokuStones={gomokuStones} gameOver={!!gameOver} onChessDrop={handleChessDrop} onXiangqiMove={handleXiangqiMove} onGoPlace={handleGoPlace} onGomokuPlace={handleGomokuPlace} boardOrientation={boardOrientation} allowDragging={isReady && !gameOver} />

          {/* Player bar (white) */}
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mt: 0.5 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <PlayerName memberId={room.white_player_id} />
            </Stack>
            <GameClock initialTime={room.time_control} isActive={isReady && !gameOver && turn === "white"} color="white" increment={room.increment || 0} />
          </Stack>
        </Box>

        {/* Side Panel */}
        <Card sx={{ width: { xs: "100%", md: 300 }, ml: { md: 2 }, mt: { xs: 2, md: 0 }, height: { md: 560 }, display: "flex", flexDirection: "column" }}>
          <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
            {/* Move list */}
            <Box sx={{ flex: 1, overflow: "auto", mb: 2 }}>
              {moves.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center", py: 4 }}>Chưa có nước đi</Typography>
              ) : (
                moves.map((m, i) => {
                  if (i % 2 !== 0) return null;
                  const num = Math.floor(i / 2) + 1;
                  return (
                    <Stack key={num} direction="row" sx={{ py: 0.5, px: 1, bgcolor: num % 2 === 0 ? "rgba(0,0,0,0.02)" : "transparent", borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ width: 32, fontFamily: "monospace", fontSize: "0.8rem" }}>{num}.</Typography>
                      <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem", fontWeight: 500, bgcolor: moves.length === i + 1 ? "rgba(0,101,62,0.1)" : "transparent", borderRadius: 0.5, px: 0.5 }}>{m}</Typography>
                      <Typography variant="body2" sx={{ width: 70, fontFamily: "monospace", fontSize: "0.8rem", bgcolor: moves.length === i + 2 ? "rgba(0,101,62,0.1)" : "transparent", borderRadius: 0.5, px: 0.5 }}>{moves[i + 1] || ""}</Typography>
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

            {/* Actions */}
            <Stack spacing={1}>
              {!gameOver && (
                <Stack direction="row" spacing={1}>
                  <Button size="small" variant="outlined" color="error" startIcon={<FlagIcon />} fullWidth onClick={handleResign}>Đầu hàng</Button>
                  <Button size="small" variant="outlined" startIcon={<HandshakeIcon />} fullWidth onClick={() => wsRef.current?.send(JSON.stringify({ type: "draw_offer" }))}>Cầu hòa</Button>
                </Stack>
              )}
              {!gameOver && (
                <Stack direction="row" spacing={1}>
                  <IconButton size="small" onClick={toggleSound}>{soundEnabled ? <VolumeUpIcon /> : <VolumeOffIcon />}</IconButton>
                  <IconButton size="small" onClick={() => setBoardOrientation((prev) => prev === "white" ? "black" : "white")}><FlipCameraAndroidIcon /></IconButton>
                </Stack>
              )}
              {gameOver && (
                <Stack direction="row" spacing={1}>
                  <Button size="small" variant="contained" startIcon={<ReplayIcon />} fullWidth onClick={handleRematch} disabled={createMutation.isPending}>Chơi lại</Button>
                  <IconButton size="small" onClick={toggleSound}>{soundEnabled ? <VolumeUpIcon /> : <VolumeOffIcon />}</IconButton>
                  <IconButton size="small" onClick={() => setBoardOrientation((prev) => prev === "white" ? "black" : "white")}><FlipCameraAndroidIcon /></IconButton>
                </Stack>
              )}
            </Stack>

            {/* Chat */}
            <Box sx={{ mt: 2 }}>
              <GameChat wsRef={wsRef} disabled={!!gameOver} />
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}

interface BoardRendererProps {
  gameType: string;
  chessFen: string;
  xiangqiFen: string;
  goStones: { row: number; col: number; color: "black" | "white" }[];
  gomokuStones: { row: number; col: number; color: "black" | "white" }[];
  gameOver: boolean;
  onChessDrop: (args: { piece: unknown; sourceSquare: string; targetSquare: string | null }) => boolean;
  onXiangqiMove: (from: string, to: string) => boolean;
  onGoPlace: (row: number, col: number) => boolean;
  onGomokuPlace: (row: number, col: number) => void;
  boardOrientation: "white" | "black";
  allowDragging: boolean;
}

function BoardRenderer({ gameType, chessFen, xiangqiFen, goStones, gomokuStones, onChessDrop, onXiangqiMove, onGoPlace, onGomokuPlace, boardOrientation, allowDragging }: BoardRendererProps) {
  if (gameType === "xiangqi") {
    return <XiangqiBoard position={xiangqiFen} onMove={onXiangqiMove} allowDragging={allowDragging} />;
  }
  if (gameType === "go") {
    return <GoBoard size={19} stones={goStones} onPlace={onGoPlace} allowPlacing={allowDragging} />;
  }
  if (gameType === "gomoku") {
    return <GomokuBoard stones={gomokuStones} onPlace={onGomokuPlace} allowPlacing={allowDragging} />;
  }
  return (
    <Box sx={{ width: { xs: 300, sm: 360, md: 480 } }}>
      <Chessboard options={{ position: chessFen, onPieceDrop: onChessDrop, allowDragging, boardOrientation }} />
    </Box>
  );
}

export default GamePlayPage;
