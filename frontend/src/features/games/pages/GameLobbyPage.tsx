import AddIcon from "@mui/icons-material/Add";
import PersonSearchIcon from "@mui/icons-material/PersonSearch";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import SportsKabaddiIcon from "@mui/icons-material/SportsKabaddi";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import EmptyState from "@/components/EmptyState";

import ChallengeDialog from "../components/ChallengeDialog";
import MatchmakingDialog from "../components/MatchmakingDialog";
import { useAcceptChallenge, useDeclineChallenge, usePendingChallenges } from "../hooks/useChallenges";
import { useCreateGameRoom, useJoinGameRoom, useLiveGames } from "../hooks/useGames";
import { IGameRoom } from "../types";

const GAME_LABELS: Record<string, string> = { chess: "Cờ vua", xiangqi: "Cờ tướng", go: "Cờ vây" };
const STATUS_LABELS: Record<string, string> = { waiting: "Chờ đối thủ", playing: "Đang chơi" };

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

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Chơi cờ trực tuyến</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<SmartToyIcon />} onClick={() => navigate("/play/ai")}>Chơi với máy</Button>
          <Button variant="outlined" onClick={() => navigate("/play/history")}>Lịch sử ván đấu</Button>
          <Button variant="outlined" startIcon={<PersonSearchIcon />} onClick={() => setMatchmakingOpen(true)}>Tìm đối thủ</Button>
          <Button variant="outlined" startIcon={<SportsKabaddiIcon />} onClick={() => setChallengeOpen(true)}>Thách đấu</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>Tạo phòng</Button>
        </Stack>
      </Stack>

      {/* Pending challenges */}
      {pendingChallenges && pendingChallenges.length > 0 && (
        <Box mb={3}>
          <Typography variant="subtitle1" fontWeight={600} mb={1}>Lời thách đấu</Typography>
          <Stack spacing={1}>
            {pendingChallenges.map((c) => (
              <Card key={c.id}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Stack spacing={0.5}>
                      <Typography fontWeight={500}>{GAME_LABELS[c.game_type] || c.game_type}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {Math.floor(c.time_control / 60)} phút • Từ: {c.challenger_id.slice(0, 8)}...
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={1}>
                      <Button size="small" variant="contained" onClick={() => acceptChallenge.mutate(c.id)}>Chấp nhận</Button>
                      <Button size="small" color="error" onClick={() => declineChallenge.mutate(c.id)}>Từ chối</Button>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      )}
      {(!rooms || rooms.length === 0) ? (
        <EmptyState
          icon={<SportsEsportsIcon sx={{ fontSize: 60 }} />}
          message="Chưa có phòng chơi nào"
          actionLabel="Tạo phòng mới"
          onAction={() => setDialogOpen(true)}
        />
      ) : (
        <Stack spacing={2}>
          {rooms.map((room) => (
            <Card key={room.id} sx={{ cursor: "pointer" }} onClick={() => handleJoin(room)}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Stack spacing={0.5}>
                    <Typography fontWeight={500}>{GAME_LABELS[room.game_type] || room.game_type}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.floor(room.time_control / 60)} phút • {room.white_player_id.slice(0, 8)}...
                    </Typography>
                  </Stack>
                  <Chip label={STATUS_LABELS[room.status] || room.status} color={room.status === "waiting" ? "success" : "primary"} size="small" />
                  {room.status === "playing" && <Chip icon={<VisibilityIcon />} label="Xem" size="small" variant="outlined" />}
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Tạo phòng chơi</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Bộ môn" select value={gameType} onChange={(e) => setGameType(e.target.value)} fullWidth>
              <MenuItem value="chess">Cờ vua</MenuItem>
              <MenuItem value="xiangqi">Cờ tướng</MenuItem>
              <MenuItem value="go">Cờ vây</MenuItem>
            </TextField>
            <TextField label="Thời gian (phút)" type="number" value={timeControl / 60} onChange={(e) => setTimeControl(Number(e.target.value) * 60)} fullWidth />
            <TextField
              label="Cộng thêm mỗi nước (giây)"
              type="number"
              value={increment}
              onChange={(e) => setIncrement(Number(e.target.value))}
              fullWidth
              helperText="Fischer increment — 0 = không cộng thêm"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Hủy</Button>
          <Button variant="contained" onClick={handleCreate} disabled={createMutation.isPending}>Tạo</Button>
        </DialogActions>
      </Dialog>
      <MatchmakingDialog open={matchmakingOpen} onClose={() => setMatchmakingOpen(false)} />
      <ChallengeDialog open={challengeOpen} onClose={() => setChallengeOpen(false)} />
    </Box>
  );
}

export default GameLobbyPage;
