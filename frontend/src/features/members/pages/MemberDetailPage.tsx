import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BarChartIcon from "@mui/icons-material/BarChart";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import RatingChart from "@/features/ratings/components/RatingChart";

import MemberRatingsTable from "../components/MemberRatingsTable";
import MemberStatsCard from "../components/MemberStatsCard";
import MemberTournamentHistory from "../components/MemberTournamentHistory";
import RankingHistoryChart from "../components/RankingHistoryChart";
import { useMember } from "../hooks/useMembers";

const SKILL_LABELS: Record<string, string> = {
  beginner: "Mới bắt đầu",
  intermediate: "Trung bình",
  advanced: "Nâng cao",
};

function MemberDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: member, isLoading } = useMember(id || "");
  const [tab, setTab] = useState(0);

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={300} /></Box>;
  }

  if (!member) {
    return (
      <Box p={3}>
        <Typography>Không tìm thấy thành viên</Typography>
        <Button onClick={() => navigate("/members")}>Quay lại</Button>
      </Box>
    );
  }

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/members")} sx={{ mb: 2 }}>
        Danh sách thành viên
      </Button>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar
                src={member.avatar_url || undefined}
                alt={member.full_name}
                sx={{ width: 56, height: 56, bgcolor: "primary.main", fontSize: 24 }}
              >
                {member.full_name.charAt(0).toUpperCase()}
              </Avatar>
              <Stack spacing={0.5}>
                <Typography variant="h5" fontWeight={600}>{member.full_name}</Typography>
                <Stack direction="row" spacing={1}>
                  {member.email && <Typography color="text.secondary">{member.email}</Typography>}
                  {member.phone && <Typography color="text.secondary">• {member.phone}</Typography>}
                </Stack>
              </Stack>
            </Stack>
            <Stack direction="row" spacing={1} alignItems="center">
              <Button
                variant="outlined"
                size="small"
                startIcon={<BarChartIcon />}
                onClick={() => navigate(`/members/${member.id}/stats`)}
              >
                Thống kê chi tiết
              </Button>
              {member.skill_level && (
                <Chip label={SKILL_LABELS[member.skill_level] || member.skill_level} color="primary" variant="outlined" />
              )}
            </Stack>
          </Stack>
        </CardContent>
      </Card>
      <MemberStatsCard memberId={member.id} />
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ my: 2 }}>
        <Tab label="Hồ sơ" />
        <Tab label="Lịch sử giải đấu" />
        <Tab label="ELO Ratings" />
      </Tabs>
      {tab === 0 && <ProfileTab member={member} />}
      {tab === 1 && <MemberTournamentHistory memberId={member.id} />}
      {tab === 2 && <RatingsTab memberId={member.id} />}
    </Box>
  );
}

function ProfileTab({ member }: { member: { notes: string | null; created_at: string } }) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="body2" color="text.secondary">Ngày tham gia</Typography>
            <Typography>{new Date(member.created_at).toLocaleDateString("vi-VN")}</Typography>
          </Box>
          {member.notes && (
            <Box>
              <Typography variant="body2" color="text.secondary">Ghi chú</Typography>
              <Typography>{member.notes}</Typography>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

function RatingsTab({ memberId }: { memberId: string }) {
  return (
    <Stack spacing={3}>
      <MemberRatingsTable memberId={memberId} />
      <RatingChart memberId={memberId} />
      <RankingHistoryChart memberId={memberId} />
    </Stack>
  );
}

export default MemberDetailPage;
