import AddIcon from "@mui/icons-material/Add";
import PersonSearchIcon from "@mui/icons-material/PersonSearch";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import SportsKabaddiIcon from "@mui/icons-material/SportsKabaddi";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import EmptyState from "@/components/EmptyState";
import PlayerName from "@/components/PlayerName";

import ChallengeDialog from "../components/ChallengeDialog";
import MatchmakingDialog from "../components/MatchmakingDialog";
import { useAcceptChallenge, useDeclineChallenge, usePendingChallenges } from "../hooks/useChallenges";
import { useCreateGameRoom, useJoinGameRoom, useLiveGames } from "../hooks/useGames";
import { IGameRoom } from "../types";

import { GAME_LABELS } from "@/utils/gameConstants";
const STATUS_LABELS: Record<string, string> = { waiting: "Chờ đối thủ", playing: "Đang chơi" };

function MiniBoardPreview({ gameType, fen }: { gameType: string; fen: string | null }) {
  const size = 8;
  const cellSize = 16;
  const pad = 4;
  const svgSize = (size - 1) * cellSize + pad * 2;
  const bgColors: Record<string, string> = { chess: "#f0d9b5", xiangqi: "#f5deb3", go: "#d4a574", gomoku: "#DCB35C" };
  const bg = bgColors[gameType] || "#DCB35C";

  // Parse stones from gomoku/go FEN
  const stones: { row: number; col: number; color: string }[] = [];
  if (fen && (gameType === "gomoku" || gameType === "go") && fen.includes(".")) {
    const parts = fen.split(";")[0];
    if (parts) {
      for (const triple of parts.split(",")) {
        const nums = triple.split(".");
        if (nums.length === 3) {
          const r = Math.min(Math.floor(parseInt(nums[0]) * size / 15), size - 1);
          const c = Math.min(Math.floor(parseInt(nums[1]) * size / 15), size - 1);
          stones.push({ row: r, col: c, color: nums[2] === "1" ? "#111" : "#FFF" });
        }
      }
    }
  }

  return (
    <Box sx={{ width: svgSize, height: svgSize, borderRadius: 1.5, overflow: "hidden", flexShrink: 0 }}>
      <svg width={svgSize} height={svgSize} style={{ background: bg }}>
        {Array.from({ length: size }, (_, i) => (
          <g key={i}>
            <line x1={pad} y1={pad + i * cellSize} x2={pad + (size - 1) * cellSize} y2={pad + i * cellSize} stroke="rgba(0,0,0,0.25)" strokeWidth={0.5} />
            <line x1={pad + i * cellSize} y1={pad} x2={pad + i * cellSize} y2={pad + (size - 1) * cellSize} stroke="rgba(0,0,0,0.25)" strokeWidth={0.5} />
          </g>
        ))}
        {gameType === "chess" && Array.from({ length: size * size }, (_, i) => {
          const r = Math.floor(i / size), c = i % size;
          return (r + c) % 2 === 1 ? <rect key={i} x={pad + c * cellSize} y={pad + r * cellSize} width={cellSize} height={cellSize} fill="#b58863" opacity={0.4} /> : null;
        })}
        {stones.map((s, i) => (
          <circle key={i} cx={pad + s.col * cellSize} cy={pad + s.row * cellSize} r={cellSize / 2 - 2} fill={s.color} stroke="#333" strokeWidth={0.5} />
        ))}
        {stones.length === 0 && <circle cx={svgSize / 2} cy={svgSize / 2} r={5} fill="rgba(0,0,0,0.15)" />}
      </svg>
    </Box>
  );
}

function RoomCard({ room, onJoin }: { room: IGameRoom; onJoin: (r: IGameRoom) => void }) {
  const isWaiting = room.status === "waiting";
  const timeLabel = room.increment > 0 ? `${Math.floor(room.time_control / 60)}+${room.increment}` : `${Math.floor(room.time_control / 60)} phút`;

  return (
    <Card
      onClick={() => onJoin(room)}
      sx={{ cursor: "pointer", p: 0, overflow: "hidden", transition: "transform 0.15s, box-shadow 0.15s", "&:hover": { transform: "translateY(-2px)", boxShadow: "0 8px 24px rgba(0,0,0,0.12)" } }}
    >
      {/* Top player (Black / Opponent) */}
      <Stack direction="row" alignItems="center" spacing={1} sx={{ px: 2, py: 1, bgcolor: "rgba(0,0,0,0.02)" }}>
        <Avatar sx={{ width: 24, height: 24, fontSize: 10, bgcolor: "#444" }}>B</Avatar>
        {room.black_player_id ? (
          <PlayerName memberId={room.black_player_id} variant="caption" />
        ) : (
          <Typography variant="caption" color="text.secondary" fontStyle="italic">Chờ đối thủ...</Typography>
        )}
        <Box sx={{ flex: 1 }} />
        <Chip label={STATUS_LABELS[room.status]} color={isWaiting ? "success" : "primary"} size="small" sx={{ height: 20, fontSize: "0.65rem" }} />
      </Stack>

      {/* Board */}
      <Stack direction="row" alignItems="center" justifyContent="center" sx={{ px: 2, py: 1.5 }}>
        <MiniBoardPreview gameType={room.game_type} fen={room.fen} />
        <Stack sx={{ ml: 2 }} spacing={0.5}>
          <Chip label={timeLabel} size="small" variant="outlined" sx={{ fontSize: "0.7rem", height: 20, width: "fit-content" }} />
          {isWaiting && <Button size="small" variant="contained" sx={{ fontSize: "0.7rem", py: 0.25, mt: 0.5 }}>Tham gia</Button>}
          {!isWaiting && <Chip icon={<VisibilityIcon />} label="Xem" size="small" variant="outlined" sx={{ height: 20, fontSize: "0.65rem" }} />}
        </Stack>
      </Stack>

      {/* Bottom player (White / Creator) */}
      <Stack direction="row" alignItems="center" spacing={1} sx={{ px: 2, py: 1, borderTop: "1px solid #f0f0f0" }}>
        <Avatar sx={{ width: 24, height: 24, fontSize: 10, bgcolor: "#fff", color: "#333", border: "1px solid #ccc" }}>W</Avatar>
        <PlayerName memberId={room.white_player_id} variant="caption" />
      </Stack>
    </Card>
  );
}

function GameLobbyPage() {
  const navigate = useNavigate();
  const { data: rooms, isLoading } = useLiveGames();
  const { data: pendingChallenges } = usePendingChallenges();
  const createMutation = useCreateGameRoom();
  const joinMutation = useJoinGameRoom();
  const acceptChallenge = useAcceptChallenge();
  const declineChallenge = useDeclineChallenge();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [matchmakingOpen, setMatchmakingOpen] = useState(false);
  const [challengeOpen, setChallengeOpen] = useState(false);
  const [gameType, setGameType] = useState("chess");
  const [timeControl, setTimeControl] = useState(300);
  const [increment, setIncrement] = useState(0);

  const handleCreate = async () => {
    const room = await createMutation.mutateAsync({ game_type: gameType, time_control: timeControl, increment });
    setDialogOpen(false);
    navigate(`/play/${room.id}`);
  };

  const handleJoin = async (room: IGameRoom) => {
    if (room.status === "waiting") {
      await joinMutation.mutateAsync(room.id);
      navigate(`/play/${room.id}`);
    } else {
      navigate(`/play/${room.id}/watch`);
    }
  };

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} /></Box>;

  return (
    <Box>
      {/* Header */}
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "center" }} spacing={2} mb={4}>
        <Box>
          <Typography variant="h5" fontWeight={700}>Chơi cờ trực tuyến</Typography>
          <Typography variant="body2" color="text.secondary">Tạo phòng, tìm đối thủ, hoặc xem ván đấu đang diễn ra</Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Button variant="outlined" size="small" startIcon={<SmartToyIcon />} onClick={() => navigate("/play/ai")}>Chơi với máy</Button>
          <Button variant="outlined" size="small" onClick={() => navigate("/play/history")}>Lịch sử</Button>
          <Button variant="outlined" size="small" startIcon={<PersonSearchIcon />} onClick={() => setMatchmakingOpen(true)}>Tìm đối thủ</Button>
          <Button variant="outlined" size="small" startIcon={<SportsKabaddiIcon />} onClick={() => setChallengeOpen(true)}>Thách đấu</Button>
          <Button variant="contained" size="small" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>Tạo phòng</Button>
        </Stack>
      </Stack>

      {/* Challenges */}
      {pendingChallenges && pendingChallenges.length > 0 && (
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} mb={1}>Lời thách đấu đến bạn</Typography>
          <Grid container spacing={2}>
            {pendingChallenges.map((c) => (
              <Grid key={c.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card sx={{ p: 2 }}>
                  <Typography fontWeight={600} mb={0.5}>{GAME_LABELS[c.game_type]}</Typography>
                  <Typography variant="body2" color="text.secondary" mb={1}>{Math.floor(c.time_control / 60)} phút</Typography>
                  <Stack direction="row" spacing={1}>
                    <Button size="small" variant="contained" fullWidth onClick={() => acceptChallenge.mutate(c.id)}>Chấp nhận</Button>
                    <Button size="small" color="error" variant="outlined" fullWidth onClick={() => declineChallenge.mutate(c.id)}>Từ chối</Button>
                  </Stack>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Room grid */}
      {(!rooms || rooms.length === 0) ? (
        <EmptyState icon={<SportsEsportsIcon sx={{ fontSize: 60 }} />} message="Chưa có phòng chơi nào" actionLabel="Tạo phòng mới" onAction={() => setDialogOpen(true)} />
      ) : (
        <Grid container spacing={2}>
          {rooms.map((room) => (
            <Grid key={room.id} size={{ xs: 12, sm: 6, lg: 4 }}>
              <RoomCard room={room} onJoin={handleJoin} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Tạo phòng chơi</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Bộ môn" select value={gameType} onChange={(e) => setGameType(e.target.value)} fullWidth>
              <MenuItem value="chess">Cờ vua</MenuItem>
              <MenuItem value="xiangqi">Cờ tướng</MenuItem>
              <MenuItem value="go">Cờ vây</MenuItem>
              <MenuItem value="gomoku">Cờ caro</MenuItem>
            </TextField>
            <TextField label="Thời gian (phút)" type="number" value={timeControl / 60} onChange={(e) => setTimeControl(Number(e.target.value) * 60)} fullWidth />
            <TextField label="Cộng thêm mỗi nước (giây)" type="number" value={increment} onChange={(e) => setIncrement(Number(e.target.value))} fullWidth helperText="Fischer increment" />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Hủy</Button>
          <Button variant="contained" onClick={handleCreate} disabled={createMutation.isPending}>Tạo phòng</Button>
        </DialogActions>
      </Dialog>
      <MatchmakingDialog open={matchmakingOpen} onClose={() => setMatchmakingOpen(false)} />
      <ChallengeDialog open={challengeOpen} onClose={() => setChallengeOpen(false)} />
    </Box>
  );
}

export default GameLobbyPage;
