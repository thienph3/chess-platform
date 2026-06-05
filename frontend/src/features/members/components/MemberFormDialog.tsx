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

import { IMember } from "../types";

const schema = z.object({
  full_name: z.string().min(1, "Họ tên không được để trống"),
  email: z.string().email("Email không hợp lệ").or(z.literal("")).optional(),
  phone: z.string().optional(),
  skill_level: z.string().optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

const SKILL_LEVELS = [
  { value: "beginner", label: "Mới bắt đầu" },
  { value: "intermediate", label: "Trung bình" },
  { value: "advanced", label: "Nâng cao" },
];

interface MemberFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: FormData) => void;
  member?: IMember | null;
  isLoading?: boolean;
}

function MemberFormDialog({ open, onClose, onSubmit, member, isLoading }: MemberFormDialogProps) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  useEffect(() => {
    if (open) {
      reset({
        full_name: member?.full_name || "",
        email: member?.email || "",
        phone: member?.phone || "",
        skill_level: member?.skill_level || "",
        notes: member?.notes || "",
      });
    }
  }, [open, member, reset]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth disableEscapeKeyDown>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{member ? "Sửa thành viên" : "Thêm thành viên"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Họ tên"
              {...register("full_name")}
              error={!!errors.full_name}
              helperText={errors.full_name?.message}
              fullWidth
              required
              autoFocus
            />
            <TextField
              label="Email"
              type="email"
              {...register("email")}
              error={!!errors.email}
              helperText={errors.email?.message}
              fullWidth
            />
            <TextField label="Số điện thoại" {...register("phone")} fullWidth />
            <TextField label="Trình độ" select {...register("skill_level")} fullWidth defaultValue="">
              <MenuItem value="">-- Chọn --</MenuItem>
              {SKILL_LEVELS.map((s) => (
                <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>
              ))}
            </TextField>
            <TextField label="Ghi chú" {...register("notes")} multiline rows={3} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Hủy</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {member ? "Cập nhật" : "Tạo mới"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default MemberFormDialog;
