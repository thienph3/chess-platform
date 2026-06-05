import CircularProgress from "@mui/material/CircularProgress";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useJoinMatchmaking, useLeaveMatchmaking, useMatchmakingStatus } from "../hooks/useMatchmaking";

interface Props {
  open: boolean;
  onClose: () => void;
}

function MatchmakingDialog({ open, onClose }: Props) {
  const navigate = useNavigate();
  const [gameType, setGameType] = useState("chess");
  const [timeFormat, setTimeFormat] = useState("blitz");
  const [searching, setSearching] = useState(false);

  const joinMutation = useJoinMatchmaking();
  const leaveMutation = useLeaveMatchmaking();
  const { data: status } = useMatchmakingStatus(searching);

  useEffect(() => {
    if (status?.matched && status.opponent_id) {
      setSearching(false);
      onClose();
      // Tạo phòng chơi sẽ được xử lý bởi backend khi matched
      navigate("/play");
    }
  }, [status, navigate, onClose]);

  const handleSearch = async () => {
    await joinMutation.mutateAsync({ game_type: gameType, time_format: timeFormat, rating: 1200 });
    if (joinMutation.data?.matched) {
      onClose();
      navigate("/play");
    } else {
      setSearching(true);
    }
  };

  const handleCancel = async () => {
    await leaveMutation.mutateAsync({ game_type: gameType, time_format: timeFormat, rating: 1200 });
    setSearching(false);
  };

  const handleClose = () => {
    if (searching) handleCancel();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>Tìm đối thủ</DialogTitle>
      <DialogContent>
        {searching ? (
          <Stack alignItems="center" spacing={2} py={3}>
            <CircularProgress />
            <Typography>Đang tìm đối thủ...</Typography>
          </Stack>
        ) : (
          <Stack spacing={2} mt={1}>
            <TextField label="Bộ môn" select value={gameType} onChange={(e) => setGameType(e.target.value)} fullWidth>
              <MenuItem value="chess">Cờ vua</MenuItem>
              <MenuItem value="xiangqi">Cờ tướng</MenuItem>
              <MenuItem value="go">Cờ vây</MenuItem>
            </TextField>
            <TextField label="Thời gian" select value={timeFormat} onChange={(e) => setTimeFormat(e.target.value)} fullWidth>
              <MenuItem value="bullet">Bullet (1 phút)</MenuItem>
              <MenuItem value="blitz">Blitz (5 phút)</MenuItem>
              <MenuItem value="rapid">Rapid (10 phút)</MenuItem>
              <MenuItem value="standard">Standard (30 phút)</MenuItem>
            </TextField>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        {searching ? (
          <Button onClick={handleCancel} color="error">Hủy tìm</Button>
        ) : (
          <>
            <Button onClick={handleClose}>Đóng</Button>
            <Button variant="contained" onClick={handleSearch} disabled={joinMutation.isPending}>
              Tìm đối thủ
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default MatchmakingDialog;
