import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import MeetingRoomIcon from "@mui/icons-material/MeetingRoom";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
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
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import PlayerName from "@/components/PlayerName";
import { dataGridLocaleText } from "@/utils/dataGridLocale";
import { useAuthContext } from "@/features/auth/context/AuthContext";

import KnockoutBracket from "../components/KnockoutBracket";
import OtbResultDialog from "../components/OtbResultDialog";
import { useTournamentDetail, useTournamentParticipants, useTournamentRounds } from "../hooks/useTournamentDetail";
import { useCreateRoundRooms, useStartMatchGame, useSubmitMatchResult } from "../hooks/useTournamentOnline";

const STATUS_LABELS: Record<string, string> = {
  draft: "Nháp", registration: "Đăng ký", in_progress: "Đang diễn ra", completed: "Đã kết thúc", cancelled: "Đã hủy",
};
import { GAME_LABELS } from "@/utils/gameConstants";
const RESULT_LABELS: Record<string, string> = { white_win: "Trắng thắng", black_win: "Đen thắng", draw: "Hòa", pending: "Chưa đấu" };
const RESULT_COLORS: Record<string, "success" | "error" | "default" | "warning"> = {
  white_win: "success", black_win: "error", draw: "default", pending: "warning",
};

function TournamentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: tournament, isLoading } = useTournamentDetail(id || "");
  const [tab, setTab] = useState(0);

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={300} /></Box>;
  if (!tournament) return <Box p={3}><Typography>Không tìm thấy giải đấu</Typography></Box>;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/tournaments")} sx={{ mb: 2 }}>
        Danh sách giải đấu
      </Button>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack spacing={0.5}>
              <Typography variant="h5" fontWeight={600}>{tournament.name}</Typography>
              <Stack direction="row" spacing={1}>
                <Chip label={GAME_LABELS[tournament.game_type] || tournament.game_type} size="small" />
                <Chip label={tournament.time_format} size="small" variant="outlined" />
                <Chip label={tournament.format} size="small" variant="outlined" />
              </Stack>
            </Stack>
            <Chip label={STATUS_LABELS[tournament.status] || tournament.status} color="primary" />
          </Stack>
        </CardContent>
      </Card>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Thông tin" />
        <Tab label="Người tham gia" />
        <Tab label="Lịch đấu" />
      </Tabs>
      {tab === 0 && <InfoTab tournament={tournament} />}
      {tab === 1 && <ParticipantsTab tournamentId={id || ""} />}
      {tab === 2 && <RoundsTab tournamentId={id || ""} format={tournament.format} mode={tournament.mode} />}
    </Box>
  );
}

function InfoTab({ tournament }: { tournament: { description: string | null; max_participants: number; start_date: string | null; end_date: string | null } }) {
  return (
    <Card><CardContent><Stack spacing={2}>
      {tournament.description && <Box><Typography variant="body2" color="text.secondary">Mô tả</Typography><Typography>{tournament.description}</Typography></Box>}
      <Box><Typography variant="body2" color="text.secondary">Số người tối đa</Typography><Typography>{tournament.max_participants}</Typography></Box>
      <Box><Typography variant="body2" color="text.secondary">Thời gian</Typography><Typography>{tournament.start_date || "—"} → {tournament.end_date || "—"}</Typography></Box>
    </Stack></CardContent></Card>
  );
}

const participantCols: GridColDef[] = [
  { field: "member_id", headerName: "Thành viên", flex: 1, renderCell: (params) => <PlayerName memberId={params.value} /> },
  { field: "status", headerName: "Trạng thái", width: 140 },
];

function ParticipantsTab({ tournamentId }: { tournamentId: string }) {
  const { data, isLoading } = useTournamentParticipants(tournamentId);
  if (isLoading) return <Skeleton variant="rectangular" height={200} />;
  if (!data?.length) return <Typography color="text.secondary">Chưa có ai đăng ký</Typography>;
  return (
    <DataGrid
      rows={data}
      columns={participantCols}
      autoHeight
      disableRowSelectionOnClick
      pageSizeOptions={[10]}
      localeText={dataGridLocaleText}
    />
  );
}

function RoundsTab({ tournamentId, format, mode }: { tournamentId: string; format: string; mode: string }) {
  const { data: rounds, isLoading } = useTournamentRounds(tournamentId);
  const { user } = useAuthContext();
  const createRoomsMutation = useCreateRoundRooms(tournamentId);
  const startMatchMutation = useStartMatchGame();
  const submitResultMutation = useSubmitMatchResult(tournamentId);
  const [resultMatch, setResultMatch] = useState<{ id: string; white_player_id: string; black_player_id: string } | null>(null);

  if (isLoading) return <Skeleton variant="rectangular" height={200} />;
  if (!rounds?.length) return <Typography color="text.secondary">Chưa có vòng đấu nào</Typography>;

  if (format === "knockout") {
    return <KnockoutBracket rounds={rounds} />;
  }

  const isAdmin = user?.role === "admin";
  const isOnline = mode === "online";
  const isOtb = mode === "otb";

  return (
    <>
      <Stack spacing={2}>
        {rounds.map((round) => (
          <Card key={round.id}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle1" fontWeight={600}>Vòng {round.round_number}</Typography>
                {isOnline && isAdmin && (
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<MeetingRoomIcon />}
                    onClick={() => createRoomsMutation.mutate(round.id)}
                    disabled={createRoomsMutation.isPending}
                  >
                    Tạo phòng
                  </Button>
                )}
              </Stack>
              {round.matches.map((m) => {
                const isMyMatch = isOnline && user?.member_id && (m.white_player_id === user.member_id || m.black_player_id === user.member_id);
                return (
                  <Stack key={m.id} direction="row" spacing={2} alignItems="center" py={0.5}>
                    <PlayerName memberId={m.white_player_id} />
                    <Chip label={RESULT_LABELS[m.result] || m.result} size="small" color={RESULT_COLORS[m.result] || "default"} />
                    <PlayerName memberId={m.black_player_id} />
                    {isMyMatch && m.result === "pending" && (
                      <Button size="small" variant="contained" startIcon={<PlayArrowIcon />}
                        onClick={() => startMatchMutation.mutate(m.id)} disabled={startMatchMutation.isPending}>
                        Chơi
                      </Button>
                    )}
                    {isOtb && isAdmin && m.result === "pending" && (
                      <Button size="small" variant="outlined"
                        onClick={() => setResultMatch({ id: m.id, white_player_id: m.white_player_id, black_player_id: m.black_player_id })}>
                        Nhập KQ
                      </Button>
                    )}
                  </Stack>
                );
              })}
            </CardContent>
          </Card>
      ))}
      </Stack>
      <OtbResultDialog
        open={!!resultMatch}
        onClose={() => setResultMatch(null)}
        match={resultMatch}
        isLoading={submitResultMutation.isPending}
        onSubmit={(data) => {
          if (resultMatch) {
            submitResultMutation.mutate({ matchId: resultMatch.id, ...data }, { onSuccess: () => setResultMatch(null) });
          }
        }}
      />
    </>
  );
}

export default TournamentDetailPage;
