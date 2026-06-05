import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import apiClient from "@/api/client";
import EmptyState from "@/components/EmptyState";
import { IResponseEnvelope } from "@/types/api";

interface IMemberTournament {
  id: string;
  tournament_id: string;
  tournament_name: string;
  game_type: string;
  status: string;
  final_rank: number | null;
  created_at: string;
}

const GAME_TYPE_LABELS: Record<string, string> = {
  chess: "Cờ vua",
  xiangqi: "Cờ tướng",
  go: "Cờ vây",
};

const STATUS_LABELS: Record<string, string> = {
  registered: "Đã đăng ký",
  active: "Đang thi đấu",
  eliminated: "Đã loại",
  completed: "Hoàn thành",
};

function useMemberTournaments(memberId: string) {
  return useQuery({
    queryKey: ["members", memberId, "tournaments"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IMemberTournament[]>>(
        `/members/${memberId}/tournaments`
      );
      return data.data || [];
    },
    enabled: !!memberId,
  });
}

interface MemberTournamentHistoryProps {
  memberId: string;
}

function MemberTournamentHistory({ memberId }: MemberTournamentHistoryProps) {
  const navigate = useNavigate();
  const { data: tournaments, isLoading } = useMemberTournaments(memberId);

  const columns: GridColDef[] = [
    { field: "tournament_name", headerName: "Giải đấu", flex: 1 },
    {
      field: "game_type",
      headerName: "Bộ môn",
      width: 120,
      valueGetter: (value: string) => GAME_TYPE_LABELS[value] || value,
    },
    {
      field: "status",
      headerName: "Trạng thái",
      width: 140,
      renderCell: (params) => (
        <Chip
          label={STATUS_LABELS[params.value] || params.value}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: "final_rank",
      headerName: "Xếp hạng",
      width: 100,
      valueGetter: (value: number | null) => (value ? `#${value}` : "—"),
    },
    {
      field: "created_at",
      headerName: "Ngày tham gia",
      width: 130,
      valueGetter: (value: string) => new Date(value).toLocaleDateString("vi-VN"),
    },
  ];

  if (isLoading) {
    return <Skeleton variant="rectangular" height={200} />;
  }

  if (!tournaments || tournaments.length === 0) {
    return (
      <EmptyState
        icon={<EmojiEventsIcon sx={{ fontSize: 60 }} />}
        message="Chưa tham gia giải đấu nào"
      />
    );
  }

  return (
    <Box>
      <DataGrid
        rows={tournaments}
        columns={columns}
        pageSizeOptions={[10, 20]}
        disableRowSelectionOnClick
        autoHeight
        onRowClick={(params) => navigate(`/tournaments/${params.row.tournament_id}`)}
        sx={{ cursor: "pointer" }}
      />
    </Box>
  );
}

export default MemberTournamentHistory;
