import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef } from "@mui/x-data-grid";

import { useMemberRatings } from "@/features/ratings/hooks/useRatingHistory";

const GAME_TYPE_LABELS: Record<string, string> = {
  chess: "Cờ vua",
  xiangqi: "Cờ tướng",
  go: "Cờ vây",
};

const TIME_FORMAT_LABELS: Record<string, string> = {
  bullet: "Bullet",
  blitz: "Blitz",
  rapid: "Rapid",
  standard: "Standard",
};

const columns: GridColDef[] = [
  {
    field: "game_type",
    headerName: "Bộ môn",
    width: 120,
    valueGetter: (value: string) => GAME_TYPE_LABELS[value] || value,
  },
  {
    field: "time_format",
    headerName: "Thể thức",
    width: 120,
    valueGetter: (value: string) => TIME_FORMAT_LABELS[value] || value,
  },
  { field: "rating", headerName: "ELO", width: 100 },
  { field: "games_played", headerName: "Số ván", width: 100 },
  { field: "wins", headerName: "Thắng", width: 80 },
  { field: "draws", headerName: "Hòa", width: 80 },
  { field: "losses", headerName: "Thua", width: 80 },
];

interface MemberRatingsTableProps {
  memberId: string;
}

function MemberRatingsTable({ memberId }: MemberRatingsTableProps) {
  const { data: ratings, isLoading } = useMemberRatings(memberId);

  if (isLoading) {
    return <Skeleton variant="rectangular" height={200} />;
  }

  if (!ratings || ratings.length === 0) {
    return <Typography color="text.secondary">Chưa có dữ liệu rating</Typography>;
  }

  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={600} mb={1}>
        Bảng ELO hiện tại
      </Typography>
      <DataGrid
        rows={ratings}
        columns={columns}
        pageSizeOptions={[10]}
        disableRowSelectionOnClick
        autoHeight
        hideFooter={ratings.length <= 10}
      />
    </Box>
  );
}

export default MemberRatingsTable;
