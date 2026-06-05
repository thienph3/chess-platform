import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { useState } from "react";

import { useLeaderboard } from "../hooks/useLeaderboard";
import { GameType, ILeaderboardEntry, TimeFormat } from "../types";

const GAME_TYPES: { value: GameType; label: string }[] = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
  { value: "gomoku", label: "Cờ caro" },
];

const TIME_FORMATS: { value: TimeFormat; label: string }[] = [
  { value: "bullet", label: "Bullet" },
  { value: "blitz", label: "Blitz" },
  { value: "rapid", label: "Rapid" },
  { value: "standard", label: "Standard" },
];

const columns: GridColDef[] = [
  { field: "rank", headerName: "Hạng", width: 80 },
  { field: "rating", headerName: "Hệ số ELO", width: 120 },
  { field: "games_played", headerName: "Số ván", width: 100 },
  { field: "wins", headerName: "Thắng", width: 80 },
  { field: "draws", headerName: "Hòa", width: 80 },
  { field: "losses", headerName: "Thua", width: 80 },
];

function LeaderboardPage() {
  const [gameType, setGameType] = useState<GameType>("chess");
  const [timeFormat, setTimeFormat] = useState<TimeFormat>("blitz");

  const { data, isLoading } = useLeaderboard({ gameType, timeFormat });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setGameType(GAME_TYPES[newValue].value);
  };

  const tabIndex = GAME_TYPES.findIndex((g) => g.value === gameType);

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;
  }

  const rows = (data?.data || []).map((entry: ILeaderboardEntry, index: number) => ({
    ...entry,
    rank: index + 1,
  }));

  return (
    <Box>
      <Typography variant="h5" fontWeight={600} mb={3}>Bảng xếp hạng</Typography>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <Tabs value={tabIndex} onChange={handleTabChange}>
          {GAME_TYPES.map((g) => (
            <Tab key={g.value} label={g.label} />
          ))}
        </Tabs>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Thể thức</InputLabel>
          <Select value={timeFormat} label="Thể thức" onChange={(e: SelectChangeEvent) => setTimeFormat(e.target.value as TimeFormat)}>
            {TIME_FORMATS.map((tf) => (
              <MenuItem key={tf.value} value={tf.value}>{tf.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSizeOptions={[20, 50]}
        disableRowSelectionOnClick
        autoHeight
      />
    </Box>
  );
}

export default LeaderboardPage;
