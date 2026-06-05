import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import GroupIcon from "@mui/icons-material/Group";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useNavigate } from "react-router-dom";

import { useDashboardStats } from "../hooks/useDashboardStats";
import ActivityFeed from "../components/ActivityFeed";

function formatCurrency(value: number): string {
  return `${value.toLocaleString("vi-VN")} ₫`;
}

function DashboardPage() {
  const navigate = useNavigate();
  const { data: stats, isLoading } = useDashboardStats();

  if (isLoading) {
    return (
      <Stack spacing={3}>
        <Typography variant="h5" fontWeight={600}>Trang chủ</Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 1 }} />
            </Grid>
          ))}
        </Grid>
      </Stack>
    );
  }

  const cards = [
    { title: "Thành viên", value: `${stats?.totalMembers || 0} người`, icon: <GroupIcon sx={{ fontSize: 40 }} />, path: "/members", color: "#00653E" },
    { title: "Giải đấu đang diễn ra", value: `${stats?.activeTournaments || 0} giải`, icon: <EmojiEventsIcon sx={{ fontSize: 40 }} />, path: "/tournaments", color: "#FFB800" },
    { title: "Bảng xếp hạng", value: "Xem chi tiết", icon: <LeaderboardIcon sx={{ fontSize: 40 }} />, path: "/ratings", color: "#4CAF50" },
    { title: "Số dư CLB", value: formatCurrency(stats?.balance || 0), icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />, path: "/finance", color: "#00653E" },
  ];

  return (
    <Stack spacing={4}>
      <Typography variant="h5" fontWeight={700}>Trang chủ</Typography>
      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={card.path}>
            <Card sx={{
              transition: "transform 0.2s, box-shadow 0.2s",
              "&:hover": { transform: "translateY(-4px)", boxShadow: "0 8px 24px rgba(0,0,0,0.1)" },
            }}>
              <CardActionArea onClick={() => navigate(card.path)} sx={{ p: 1 }}>
                <CardContent>
                  <Stack alignItems="center" spacing={1.5} py={3}>
                    <Stack
                      alignItems="center" justifyContent="center"
                      sx={{ width: 64, height: 64, borderRadius: "50%", bgcolor: `${card.color}14`, color: card.color }}
                    >
                      {card.icon}
                    </Stack>
                    <Typography variant="h6" fontWeight={600}>{card.title}</Typography>
                    <Typography variant="body2" color="text.secondary">{card.value}</Typography>
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
      <ActivityFeed />
    </Stack>
  );
}

export default DashboardPage;
