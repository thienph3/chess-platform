import TimelineIcon from "@mui/icons-material/Timeline";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

import EmptyState from "@/components/EmptyState";

interface RankingHistoryChartProps {
  memberId: string;
}

function RankingHistoryChart({ memberId: _memberId }: RankingHistoryChartProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={600} mb={2}>
          Lịch sử xếp hạng
        </Typography>
        <Box>
          <EmptyState
            icon={<TimelineIcon sx={{ fontSize: 40 }} />}
            message="Dữ liệu xếp hạng sẽ được cập nhật theo thời gian"
          />
        </Box>
      </CardContent>
    </Card>
  );
}

export default RankingHistoryChart;
