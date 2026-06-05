import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { useMemberGameStats } from "../hooks/useMemberStats";

interface MemberStatsCardProps {
  memberId: string;
}

const FORM_COLORS: Record<string, "success" | "warning" | "error"> = {
  W: "success",
  D: "warning",
  L: "error",
};

const FORM_LABELS: Record<string, string> = {
  W: "Thắng",
  D: "Hòa",
  L: "Thua",
};

function MemberStatsCard({ memberId }: MemberStatsCardProps) {
  const { data: stats, isLoading } = useMemberGameStats(memberId);

  if (isLoading) {
    return <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 1 }} />;
  }

  if (!stats || stats.totalGames === 0) {
    return (
      <Card>
        <CardContent>
          <Typography color="text.secondary">Chưa có dữ liệu ván đấu</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Stack direction="row" spacing={4} alignItems="center" flexWrap="wrap">
          <Box>
            <Typography variant="body2" color="text.secondary">Tổng ván</Typography>
            <Typography variant="h6" fontWeight={600}>{stats.totalGames}</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">Thắng / Hòa / Thua</Typography>
            <Typography variant="h6" fontWeight={600}>
              {stats.wins} / {stats.draws} / {stats.losses}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">Tỷ lệ thắng</Typography>
            <Typography variant="h6" fontWeight={600}>{stats.winRate.toFixed(1)}%</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">Phong độ gần đây</Typography>
            <Stack direction="row" spacing={0.5} mt={0.5}>
              {stats.recentForm.map((result, idx) => (
                <Chip
                  key={idx}
                  label={result}
                  size="small"
                  color={FORM_COLORS[result]}
                  aria-label={FORM_LABELS[result]}
                />
              ))}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default MemberStatsCard;
