import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { useAttendanceHistory, useAttendanceSummary, useCheckIn } from "../hooks/useAttendance";

const EVENT_LABELS: Record<string, string> = {
  regular: "Sinh hoạt",
  tournament: "Giải đấu",
  special: "Đặc biệt",
};

function AttendancePage() {
  const { data: history, isLoading } = useAttendanceHistory();
  const { data: summary } = useAttendanceSummary();
  const checkInMutation = useCheckIn();
  const [snackOpen, setSnackOpen] = useState(false);
  const [snackMsg, setSnackMsg] = useState("");

  const handleCheckIn = async () => {
    try {
      await checkInMutation.mutateAsync({ event_type: "regular" });
      setSnackMsg("Điểm danh thành công!");
      setSnackOpen(true);
    } catch (err: unknown) {
      setSnackMsg(err instanceof Error ? err.message : "Đã xảy ra lỗi");
      setSnackOpen(true);
    }
  };

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Điểm danh</Typography>
        <Button variant="contained" startIcon={<CheckCircleIcon />} onClick={handleCheckIn} disabled={checkInMutation.isPending}>
          Điểm danh
        </Button>
      </Stack>

      {summary && (
        <Stack direction="row" spacing={2} mb={3}>
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">Tổng buổi</Typography>
              <Typography variant="h4" fontWeight={600}>{summary.total_sessions}</Typography>
            </CardContent>
          </Card>
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">Streak hiện tại</Typography>
              <Typography variant="h4" fontWeight={600}>{summary.current_streak} ngày</Typography>
            </CardContent>
          </Card>
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">Lần cuối</Typography>
              <Typography variant="h6" fontWeight={500}>{summary.last_attendance || "—"}</Typography>
            </CardContent>
          </Card>
        </Stack>
      )}

      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Ngày</TableCell>
              <TableCell>Loại</TableCell>
              <TableCell>Ghi chú</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(history || []).map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.date}</TableCell>
                <TableCell><Chip label={EVENT_LABELS[row.event_type] || row.event_type} size="small" /></TableCell>
                <TableCell>{row.notes || "—"}</TableCell>
              </TableRow>
            ))}
            {(!history || history.length === 0) && (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  <Stack alignItems="center" py={3}>
                    <EventAvailableIcon sx={{ fontSize: 40, color: "text.secondary" }} />
                    <Typography color="text.secondary">Chưa có lịch sử điểm danh</Typography>
                  </Stack>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Snackbar open={snackOpen} autoHideDuration={3000} onClose={() => setSnackOpen(false)}>
        <Alert severity={checkInMutation.isError ? "error" : "success"} onClose={() => setSnackOpen(false)}>
          {snackMsg}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default AttendancePage;
