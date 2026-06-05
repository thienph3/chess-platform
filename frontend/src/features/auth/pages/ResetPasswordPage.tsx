import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useSearchParams } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { authApi } from "../api";

const schema = z
  .object({
    new_password: z.string().min(6, "Mật khẩu tối thiểu 6 ký tự"),
    confirm_password: z.string().min(1, "Xác nhận mật khẩu là bắt buộc"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Mật khẩu không khớp",
    path: ["confirm_password"],
  });

type FormData = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      setError(null);
      await authApi.resetPassword(token, data.new_password);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Đã xảy ra lỗi");
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#F5F7FA">
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardContent>
          <Stack spacing={3} component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Typography variant="h5" textAlign="center" fontWeight={600}>
              Đặt lại mật khẩu
            </Typography>

            {success && (
              <Alert severity="success">
                Đặt lại mật khẩu thành công. <Link to="/login">Đăng nhập ngay</Link>
              </Alert>
            )}
            {error && <Alert severity="error">{error}</Alert>}

            {!success && (
              <>
                <TextField
                  label="Mật khẩu mới"
                  type="password"
                  fullWidth
                  {...register("new_password")}
                  error={!!errors.new_password}
                  helperText={errors.new_password?.message}
                />
                <TextField
                  label="Xác nhận mật khẩu"
                  type="password"
                  fullWidth
                  {...register("confirm_password")}
                  error={!!errors.confirm_password}
                  helperText={errors.confirm_password?.message}
                />
                <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting || !token}>
                  {isSubmitting ? "Đang xử lý..." : "Đặt lại mật khẩu"}
                </Button>
              </>
            )}

            <Typography variant="body2" textAlign="center">
              <Link to="/login" style={{ color: "#0054A6" }}>Quay lại đăng nhập</Link>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
