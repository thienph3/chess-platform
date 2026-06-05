import { zodResolver } from "@hookform/resolvers/zod";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ITournament } from "../types";

const schema = z.object({
  name: z.string().min(1, "Tên giải đấu không được để trống"),
  description: z.string().optional(),
  game_type: z.enum(["chess", "xiangqi", "go"]),
  time_format: z.enum(["bullet", "blitz", "rapid", "standard"]),
  format: z.enum(["round_robin", "swiss", "knockout"]),
  max_participants: z.coerce.number().min(2, "Tối thiểu 2 người"),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

const GAME_TYPES = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
];

const TIME_FORMATS = [
  { value: "bullet", label: "Bullet (1+0)" },
  { value: "blitz", label: "Blitz (3+2, 5+0)" },
  { value: "rapid", label: "Rapid (10+0, 15+10)" },
  { value: "standard", label: "Standard (30+0)" },
];

const FORMATS = [
  { value: "round_robin", label: "Round Robin" },
  { value: "swiss", label: "Swiss" },
  { value: "knockout", label: "Knockout" },
];

interface TournamentFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: FormData) => void;
  tournament?: ITournament | null;
  isLoading?: boolean;
}

function TournamentFormDialog({ open, onClose, onSubmit, tournament, isLoading }: TournamentFormDialogProps) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  useEffect(() => {
    if (open) {
      reset({
        name: tournament?.name || "",
        description: tournament?.description || "",
        game_type: tournament?.game_type || "chess",
        time_format: tournament?.time_format || "blitz",
        format: tournament?.format || "swiss",
        max_participants: tournament?.max_participants || 16,
        start_date: tournament?.start_date || "",
        end_date: tournament?.end_date || "",
      });
    }
  }, [open, tournament, reset]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth disableEscapeKeyDown>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{tournament ? "Sửa giải đấu" : "Tạo giải đấu"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Tên giải đấu"
              {...register("name")}
              error={!!errors.name}
              helperText={errors.name?.message}
              fullWidth
              required
              autoFocus
            />
            <TextField label="Mô tả" {...register("description")} multiline rows={2} fullWidth />
            <TextField label="Bộ môn" select {...register("game_type")} fullWidth defaultValue="chess">
              {GAME_TYPES.map((g) => (
                <MenuItem key={g.value} value={g.value}>{g.label}</MenuItem>
              ))}
            </TextField>
            <TextField label="Thể thức thời gian" select {...register("time_format")} fullWidth defaultValue="blitz">
              {TIME_FORMATS.map((t) => (
                <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
              ))}
            </TextField>
            <TextField label="Hình thức" select {...register("format")} fullWidth defaultValue="swiss">
              {FORMATS.map((f) => (
                <MenuItem key={f.value} value={f.value}>{f.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              label="Số người tối đa"
              type="number"
              {...register("max_participants")}
              error={!!errors.max_participants}
              helperText={errors.max_participants?.message}
              fullWidth
            />
            <TextField label="Ngày bắt đầu" type="date" {...register("start_date")} InputLabelProps={{ shrink: true }} fullWidth />
            <TextField label="Ngày kết thúc" type="date" {...register("end_date")} InputLabelProps={{ shrink: true }} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Hủy</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {tournament ? "Cập nhật" : "Tạo mới"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default TournamentFormDialog;
