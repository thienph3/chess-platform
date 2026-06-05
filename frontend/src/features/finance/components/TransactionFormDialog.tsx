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

import { ITransaction } from "../types";

const INCOME_CATEGORIES = [
  { value: "membership_fee", label: "Phí thành viên" },
  { value: "sponsorship", label: "Tài trợ" },
  { value: "donation", label: "Quyên góp" },
  { value: "other_income", label: "Thu khác" },
];

const EXPENSE_CATEGORIES = [
  { value: "venue", label: "Địa điểm" },
  { value: "prize", label: "Giải thưởng" },
  { value: "equipment", label: "Thiết bị" },
  { value: "food", label: "Ăn uống" },
  { value: "other_expense", label: "Chi khác" },
];

const schema = z.object({
  type: z.enum(["income", "expense"]),
  category: z.enum([
    "membership_fee", "sponsorship", "donation", "other_income",
    "venue", "prize", "equipment", "food", "other_expense",
  ]),
  amount: z.coerce.number().positive("Số tiền phải lớn hơn 0"),
  date: z.string().min(1, "Chọn ngày"),
  description: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface TransactionFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: FormData) => void;
  transaction?: ITransaction | null;
  isLoading?: boolean;
}

function TransactionFormDialog({ open, onClose, onSubmit, transaction, isLoading }: TransactionFormDialogProps) {
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const type = watch("type");

  useEffect(() => {
    if (open) {
      reset({
        type: transaction?.type || "income",
        category: transaction?.category || "membership_fee",
        amount: transaction?.amount || 0,
        date: transaction?.date || new Date().toISOString().split("T")[0],
        description: transaction?.description || "",
      });
    }
  }, [open, transaction, reset]);

  const categories = type === "expense" ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth disableEscapeKeyDown>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{transaction ? "Sửa giao dịch" : "Thêm giao dịch"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Loại" select {...register("type")} fullWidth defaultValue="income">
              <MenuItem value="income">Thu</MenuItem>
              <MenuItem value="expense">Chi</MenuItem>
            </TextField>
            <TextField
              label="Danh mục"
              select
              {...register("category")}
              error={!!errors.category}
              helperText={errors.category?.message}
              fullWidth
              defaultValue="membership_fee"
            >
              {categories.map((c) => (
                <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              label="Số tiền (VNĐ)"
              type="number"
              {...register("amount")}
              error={!!errors.amount}
              helperText={errors.amount?.message}
              fullWidth
              required
            />
            <TextField
              label="Ngày"
              type="date"
              {...register("date")}
              error={!!errors.date}
              helperText={errors.date?.message}
              InputLabelProps={{ shrink: true }}
              fullWidth
              required
            />
            <TextField label="Mô tả" {...register("description")} multiline rows={2} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Hủy</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {transaction ? "Cập nhật" : "Tạo mới"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default TransactionFormDialog;
