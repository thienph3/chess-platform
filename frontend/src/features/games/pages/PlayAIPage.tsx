import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import FlagIcon from "@mui/icons-material/Flag";
import ReplayIcon from "@mui/icons-material/Replay";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import ButtonGroup from "@mui/material/ButtonGroup";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useCallback, useState } from "react";
import { Chessboard } from "react-chessboard";
import { useNavigate } from "react-router-dom";

import apiClient from "@/api/client";
import { useAuthContext } from "@/features/auth/context/AuthContext";

import GameClock from "../components/GameClock";
import GoBoard from "../components/GoBoard";
import GomokuBoard from "../components/GomokuBoard";
import XiangqiBoard from "../components/XiangqiBoard";
import { Difficulty, GameType, ColorChoice, usePlayAI } from "../hooks/usePlayAI";

const GAME_OPTIONS: { value: GameType; label: string }[] = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
  { value: "gomoku", label: "Cờ caro" },
];

const DIFFICULTY_OPTIONS: { value: Difficulty; label: string; aiName: string }[] = [
  { value: "easy", label: "Dễ", aiName: "VCC Bot (Dễ)" },
  { value: "medium", label: "Trung bình", aiName: "VCC Bot (TB)" },
  { value: "hard", label: "Khó", aiName: "VCC Bot (Khó)" },
];

const TIME_OPTIONS: { value: number; increment: number; label: string }[] = [
  { value: 60, increment: 0, label: "1+0" },
  { value: 60, increment: 1, label: "1+1" },
  { value: 180, increment: 0, label: "3+0" },
  { value: 180, increment: 2, label: "3+2" },
  { value: 300, increment: 0, label: "5+0" },
  { value: 300, increment: 5, label: "5+5" },
  { value: 600, increment: 0, label: "10+0" },
  { value: 600, increment: 5, label: "10+5" },
  { value: 900, increment: 0, label: "15+0" },
];

function PlayAIPage() {
  const navigate = useNavigate();
  const { user } = useAuthContext();
  const [gameType, setGameType] = useState<GameType>("chess");
  const [difficulty, setDifficulty] = useState<Difficulty>("medium");
  const [timeControl, setTimeControl] = useState(600);
  const [increment, setIncrement] = useState(0);
  const [colorChoice, setColorChoice] = useState<ColorChoice>("white");
  const [customMode, setCustomMode] = useState(false);
  const [customMinutes, setCustomMinutes] = useState(10);
  const [customIncrement, setCustomIncrement] = useState(0);
  const { state, isThinking, started, startGame, makeMove, endGame, moves } = usePlayAI(gameType, difficulty);

  const aiName = DIFFICULTY_OPTIONS.find((d) => d.value === difficulty)?.aiName || "VCC Bot";
  const playerName = user?.email?.split("@")[0] || "Bạn";

  const handleChessDrop = useCallback(
    ({ sourceSquare, targetSquare }: { piece: unknown; sourceSquare: string; targetSquare: string | null }) => {
      if (!targetSquare || isThinking || state.gameOver) return false;
      makeMove({ from: sourceSquare, to: targetSquare, promotion: "q" });
      return true;
    },
    [isThinking, state.gameOver, makeMove],
  );

  const handleXiangqiMove = useCallback(
    (from: string, to: string) => {
      if (isThinking || state.gameOver) return false;
      makeMove({ from, to });
      return true;
    },
    [isThinking, state.gameOver, makeMove],
  );

  const handleGoPlace = useCallback(
    (row: number, col: number) => {
      if (isThinking || state.gameOver) return false;
      makeMove({ notation: `${String.fromCharCode(97 + col)}${row + 1}`, row, col });
      return true;
    },
    [isThinking, state.gameOver, makeMove],
  );

  const handleGomokuPlace = useCallback(
    (row: number, col: number) => {
      if (isThinking || state.gameOver) return;
      makeMove({ row, col });
    },
    [isThinking, state.gameOver, makeMove],
  );

  const handleDrawOffer = useCallback(async () => {
    // Hỏi AI: gọi /ai/move để lấy evaluation, nếu |eval| < 100cp thì đồng ý
    try {
      const res = await apiClient.post("/games/ai/move", { fen: state.fen, game_type: gameType, difficulty });
      const evalScore = Math.abs(res.data?.data?.evaluation || 0);
      if (evalScore < 100) {
        endGame("½-½");
      } else {
        // AI từ chối — hiện thông báo nhẹ (không làm gì, user tiếp tục chơi)
        alert("Đối thủ từ chối cầu hòa");
      }
    } catch {
      endGame("½-½"); // fallback: chấp nhận nếu không gọi được
    }
  }, [state.fen, gameType, difficulty, endGame]);

  if (!started) {
    return (
      <Box>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} sx={{ mb: 2 }}>Lobby</Button>
        <Typography variant="h5" fontWeight={600} mb={3}>
          <SmartToyIcon sx={{ mr: 1, verticalAlign: "middle" }} />Chơi với máy
        </Typography>
        <Card sx={{ maxWidth: 400 }}>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle2" mb={1}>Bộ môn</Typography>
                <ButtonGroup fullWidth>
                  {GAME_OPTIONS.map((o) => (
                    <Button key={o.value} variant={gameType === o.value ? "contained" : "outlined"}
                      onClick={() => setGameType(o.value)}>{o.label}</Button>
                  ))}
                </ButtonGroup>
              </Box>
              <Box>
                <Typography variant="subtitle2" mb={1}>Độ khó</Typography>
                <ButtonGroup fullWidth>
                  {DIFFICULTY_OPTIONS.map((o) => (
                    <Button key={o.value} variant={difficulty === o.value ? "contained" : "outlined"}
                      onClick={() => setDifficulty(o.value)}>{o.label}</Button>
                  ))}
                </ButtonGroup>
              </Box>
              <Box>
                <Typography variant="subtitle2" mb={1}>Thể thức</Typography>
                <Stack direction="row" flexWrap="wrap" gap={1} mb={1}>
                  {TIME_OPTIONS.map((o) => (
                    <Chip key={o.label} label={o.label} size="small"
                      variant={!customMode && timeControl === o.value && increment === o.increment ? "filled" : "outlined"}
                      color={!customMode && timeControl === o.value && increment === o.increment ? "primary" : "default"}
                      onClick={() => { setTimeControl(o.value); setIncrement(o.increment); setCustomMode(false); }} />
                  ))}
                  <Chip label="Tùy chỉnh" size="small"
                    variant={customMode ? "filled" : "outlined"}
                    color={customMode ? "primary" : "default"}
                    onClick={() => setCustomMode(true)} />
                </Stack>
                {customMode && (
                  <Stack direction="row" spacing={1}>
                    <TextField label="Phút" type="number" size="small" value={customMinutes}
                      onChange={(e) => { const v = Math.max(1, Math.min(15, Number(e.target.value))); setCustomMinutes(v); setTimeControl(v * 60); }}
                      inputProps={{ min: 1, max: 15 }} sx={{ width: 80 }} />
                    <TextField label="Cộng (giây)" type="number" size="small" value={customIncrement}
                      onChange={(e) => { const v = Math.max(0, Math.min(30, Number(e.target.value))); setCustomIncrement(v); setIncrement(v); }}
                      inputProps={{ min: 0, max: 30 }} sx={{ width: 100 }} />
                  </Stack>
                )}
              </Box>
              <Box>
                <Typography variant="subtitle2" mb={1}>Màu quân</Typography>
                <ButtonGroup fullWidth>
                  <Button variant={colorChoice === "white" ? "contained" : "outlined"} onClick={() => setColorChoice("white")}>Trắng</Button>
                  <Button variant={colorChoice === "random" ? "contained" : "outlined"} onClick={() => setColorChoice("random")}>Ngẫu nhiên</Button>
                  <Button variant={colorChoice === "black" ? "contained" : "outlined"} onClick={() => setColorChoice("black")}>Đen</Button>
                </ButtonGroup>
              </Box>
              <Button variant="contained" size="large" onClick={() => startGame(colorChoice, timeControl, increment)} startIcon={<SmartToyIcon />}>Bắt đầu</Button>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} size="small" sx={{ mb: 1 }}>Lobby</Button>
      <Stack direction={{ xs: "column", md: "row" }} spacing={0} alignItems="flex-start">
        {/* Board Area */}
        <Box>
          {/* Top bar (opponent) */}
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mb: 0.5 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              {state.playerColor === "white" ? (
                <><Avatar sx={{ width: 28, height: 28, bgcolor: "primary.main", fontSize: 12 }}><SmartToyIcon sx={{ fontSize: 16 }} /></Avatar>
                <Typography variant="body2" fontWeight={600}>{aiName}</Typography></>
              ) : (
                <><Avatar sx={{ width: 28, height: 28, bgcolor: "secondary.main", color: "text.primary", fontSize: 12 }}>{playerName[0]?.toUpperCase()}</Avatar>
                <Typography variant="body2" fontWeight={600}>{playerName}</Typography></>
              )}
            </Stack>
            <GameClock initialTime={timeControl} isActive={state.playerColor === "white" ? isThinking : (!isThinking && !state.gameOver)}
              color={state.playerColor === "white" ? "black" : "white"} increment={increment}
              onTimeout={() => endGame(state.playerColor === "white" ? "1-0" : "0-1")} />
          </Stack>

          {/* Board */}
          {gameType === "chess" && state.fen && (
            <Box sx={{ width: { xs: 320, sm: 400, md: 480 } }}>
              <Chessboard options={{ position: state.fen, onPieceDrop: handleChessDrop, allowDragging: !isThinking && !state.gameOver, boardOrientation: state.playerColor === "white" ? "white" : "black" }} />
            </Box>
          )}
          {gameType === "xiangqi" && <XiangqiBoard position={state.fen} onMove={handleXiangqiMove} allowDragging={!isThinking && !state.gameOver} />}
          {gameType === "go" && <GoBoard size={19} stones={[]} onPlace={handleGoPlace} allowPlacing={!isThinking && !state.gameOver} />}
          {gameType === "gomoku" && <GomokuBoard stones={[]} onPlace={handleGomokuPlace} allowPlacing={!isThinking && !state.gameOver} />}

          {/* Bottom bar (me) */}
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 1, py: 0.75, mt: 0.5 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              {state.playerColor === "white" ? (
                <><Avatar sx={{ width: 28, height: 28, bgcolor: "secondary.main", color: "text.primary", fontSize: 12 }}>{playerName[0]?.toUpperCase()}</Avatar>
                <Typography variant="body2" fontWeight={600}>{playerName}</Typography></>
              ) : (
                <><Avatar sx={{ width: 28, height: 28, bgcolor: "primary.main", fontSize: 12 }}><SmartToyIcon sx={{ fontSize: 16 }} /></Avatar>
                <Typography variant="body2" fontWeight={600}>{aiName}</Typography></>
              )}
            </Stack>
            <GameClock initialTime={timeControl} isActive={state.playerColor === "white" ? (!isThinking && !state.gameOver) : isThinking}
              color={state.playerColor === "white" ? "white" : "black"} increment={increment}
              onTimeout={() => endGame(state.playerColor === "white" ? "0-1" : "1-0")} />
          </Stack>
        </Box>

        {/* Side Panel */}
        <Card sx={{ width: { xs: "100%", md: 280 }, ml: { md: 2 }, mt: { xs: 2, md: 0 }, height: { md: 540 }, display: "flex", flexDirection: "column" }}>
          <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
            <MoveList moves={moves} result={state.gameOver ? state.result : null} />
            <Stack direction="row" spacing={1} sx={{ mt: "auto", pt: 2 }}>
              {!state.gameOver && (
                <>
                  <Button size="small" variant="outlined" color="error" startIcon={<FlagIcon />} fullWidth
                    onClick={() => endGame("0-1")}>
                    Đầu hàng
                  </Button>
                  <Button size="small" variant="outlined" fullWidth
                    onClick={handleDrawOffer}>
                    Cầu hòa
                  </Button>
                </>
              )}
              {state.gameOver && (
                <Button size="small" variant="contained" startIcon={<ReplayIcon />} fullWidth
                  onClick={() => startGame(colorChoice, timeControl, increment)}>
                  Chơi lại
                </Button>
              )}
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}

function MoveList({ moves, result }: { moves: string[]; result: string | null }) {
  const pairs: { num: number; white: string; black?: string }[] = [];
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push({ num: Math.floor(i / 2) + 1, white: moves[i], black: moves[i + 1] });
  }

  const formatResult = (r: string | null): string => {
    if (!r) return "";
    if (r.includes("1-0") || r.includes("white_win")) return "1-0";
    if (r.includes("0-1") || r.includes("black_win")) return "0-1";
    return "½-½";
  };

  return (
    <Box sx={{ flex: 1, overflow: "auto", maxHeight: { md: 380 } }}>
      {pairs.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center", py: 4 }}>
          Chưa có nước đi
        </Typography>
      )}
      {pairs.map((p, idx) => (
        <Stack key={p.num} direction="row" sx={{
          py: 0.5, px: 1, bgcolor: idx % 2 === 0 ? "transparent" : "rgba(0,0,0,0.02)", borderRadius: 1,
        }}>
          <Typography variant="body2" color="text.secondary" sx={{ width: 32, fontFamily: "monospace", fontSize: "0.8rem" }}>
            {p.num}.
          </Typography>
          <Typography variant="body2" sx={{
            width: 70, fontFamily: "monospace", fontSize: "0.8rem", fontWeight: 500,
            bgcolor: moves.length === p.num * 2 - 1 ? "rgba(0,101,62,0.1)" : "transparent",
            borderRadius: 0.5, px: 0.5,
          }}>
            {p.white}
          </Typography>
          <Typography variant="body2" sx={{
            width: 70, fontFamily: "monospace", fontSize: "0.8rem",
            bgcolor: moves.length === p.num * 2 ? "rgba(0,101,62,0.1)" : "transparent",
            borderRadius: 0.5, px: 0.5,
          }}>
            {p.black || ""}
          </Typography>
        </Stack>
      ))}
      {result && (
        <Typography variant="body2" fontWeight={700} sx={{ mt: 1, py: 1, fontFamily: "monospace", textAlign: "center", bgcolor: "rgba(0,0,0,0.04)", borderRadius: 1 }}>
          {formatResult(result)}
        </Typography>
      )}
    </Box>
  );
}

export default PlayAIPage;
