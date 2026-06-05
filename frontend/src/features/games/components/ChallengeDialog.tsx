import Autocomplete from "@mui/material/Autocomplete";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { useState } from "react";

import { useCreateChallenge } from "../hooks/useChallenges";
import { useMembers } from "@/features/members/hooks/useMembers";

interface Props {
  open: boolean;
  onClose: () => void;
}

function ChallengeDialog({ open, onClose }: Props) {
  const [targetId, setTargetId] = useState<string | null>(null);
  const [gameType, setGameType] = useState("chess");
  const [timeControl, setTimeControl] = useState(300);

  const { data: membersData } = useMembers({ pageSize: 100 });
  const createMutation = useCreateChallenge();

  const handleSubmit = async () => {
    if (!targetId) return;
    await createMutation.mutateAsync({
      challenged_id: targetId,
      game_type: gameType,
      time_control: timeControl,
    });
    onClose();
  };

  const memberOptions = (membersData?.data || []).map((m) => ({ id: m.id, label: m.full_name || m.id }));

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Thách đấu</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          <Autocomplete
            options={memberOptions}
            getOptionLabel={(opt) => opt.label}
            onChange={(_, val) => setTargetId(val?.id || null)}
            renderInput={(params) => <TextField {...params} label="Chọn đối thủ" />}
          />
          <TextField label="Bộ môn" select value={gameType} onChange={(e) => setGameType(e.target.value)} fullWidth>
            <MenuItem value="chess">Cờ vua</MenuItem>
            <MenuItem value="xiangqi">Cờ tướng</MenuItem>
            <MenuItem value="go">Cờ vây</MenuItem>
          </TextField>
          <TextField
            label="Thời gian (phút)"
            type="number"
            value={timeControl / 60}
            onChange={(e) => setTimeControl(Number(e.target.value) * 60)}
            fullWidth
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Hủy</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={!targetId || createMutation.isPending}>
          Thách đấu
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ChallengeDialog;
