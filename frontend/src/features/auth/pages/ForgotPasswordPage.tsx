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
import { Link } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { authApi } from "../api";

const schema = z.object({
  email: z.string().min(1, "Email là bắt buộc").email("Email không hợp lệ"),
});

type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
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
      await authApi.forgotPassword(data.email);
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
              Quên mật khẩu
            </Typography>

            {success && <Alert severity="success">Link đặt lại mật khẩu đã được gửi</Alert>}
            {error && <Alert severity="error">{error}</Alert>}

            {!success && (
              <>
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  Nhập email để nhận link đặt lại mật khẩu
                </Typography>
                <TextField
                  label="Email"
                  type="email"
                  fullWidth
                  {...register("email")}
                  error={!!errors.email}
                  helperText={errors.email?.message}
                />
                <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
                  {isSubmitting ? "Đang xử lý..." : "Gửi link đặt lại"}
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
