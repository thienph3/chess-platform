import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import PlayerName from "@/components/PlayerName";

interface OtbResultDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: { result: string; pgn?: string }) => void;
  match: { id: string; white_player_id: string; black_player_id: string } | null;
  isLoading: boolean;
}

function OtbResultDialog({ open, onClose, onSubmit, match, isLoading }: OtbResultDialogProps) {
  const [result, setResult] = useState("");
  const [pgn, setPgn] = useState("");

  const handleSubmit = () => {
    if (!result) return;
    onSubmit({ result, pgn: pgn.trim() || undefined });
    setResult("");
    setPgn("");
  };

  if (!match) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Nhập kết quả ván đấu</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          <Stack direction="row" alignItems="center" spacing={2} justifyContent="center">
            <PlayerName memberId={match.white_player_id} />
            <Typography variant="body2" color="text.secondary">vs</Typography>
            <PlayerName memberId={match.black_player_id} />
          </Stack>
          <FormControl fullWidth>
            <InputLabel>Kết quả</InputLabel>
            <Select value={result} label="Kết quả" onChange={(e) => setResult(e.target.value)}>
              <MenuItem value="white_win">1-0 (Trắng thắng)</MenuItem>
              <MenuItem value="black_win">0-1 (Đen thắng)</MenuItem>
              <MenuItem value="draw">½-½ (Hòa)</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="PGN (không bắt buộc)"
            multiline
            rows={4}
            value={pgn}
            onChange={(e) => setPgn(e.target.value)}
            placeholder="1. e4 e5 2. Nf3 Nc6 ..."
            fullWidth
            sx={{ fontFamily: "monospace" }}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Hủy</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={!result || isLoading}>
          Lưu kết quả
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default OtbResultDialog;
