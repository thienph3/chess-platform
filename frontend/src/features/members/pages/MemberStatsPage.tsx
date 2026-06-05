import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useNavigate, useParams } from "react-router-dom";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer } from "recharts";

import { useMemberGameStats } from "../hooks/useMemberStats";

const COLORS = ["#4CAF50", "#9E9E9E", "#F44336"];

function MemberStatsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: stats, isLoading } = useMemberGameStats(id || "");

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;
  }

  if (!stats) {
    return (
      <Box p={3}>
        <Typography>Không có dữ liệu thống kê</Typography>
      </Box>
    );
  }

  const pieData = [
    { name: "Thắng", value: stats.wins },
    { name: "Hòa", value: stats.draws },
    { name: "Thua", value: stats.losses },
  ];

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(`/members/${id}`)} sx={{ mb: 2 }}>
        Quay lại hồ sơ
      </Button>
      <Typography variant="h5" fontWeight={600} mb={3}>
        Thống kê chi tiết
      </Typography>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={1}>Tổng quan</Typography>
              <Stack spacing={1}>
                <StatRow label="Tổng ván" value={stats.totalGames} />
                <StatRow label="Thắng" value={stats.wins} />
                <StatRow label="Hòa" value={stats.draws} />
                <StatRow label="Thua" value={stats.losses} />
                <StatRow label="Tỷ lệ thắng" value={`${stats.winRate.toFixed(1)}%`} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={2}>
                Phân bố kết quả
              </Typography>
              {stats.totalGames > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                      {pieData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="text.secondary">Chưa có dữ liệu</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <Stack direction="row" justifyContent="space-between">
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600}>{value}</Typography>
    </Stack>
  );
}

export default MemberStatsPage;
