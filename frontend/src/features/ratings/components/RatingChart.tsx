import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useRatingHistory } from "../hooks/useRatingHistory";
import { GameType, TimeFormat } from "../types";

const GAME_TYPES = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
  { value: "gomoku", label: "Cờ caro" },
];

const TIME_FORMATS = [
  { value: "bullet", label: "Bullet" },
  { value: "blitz", label: "Blitz" },
  { value: "rapid", label: "Rapid" },
  { value: "standard", label: "Standard" },
];

interface RatingChartProps {
  memberId: string;
}

function RatingChart({ memberId }: RatingChartProps) {
  const [gameType, setGameType] = useState<GameType>("chess");
  const [timeFormat, setTimeFormat] = useState<TimeFormat>("blitz");

  const { data: history } = useRatingHistory(memberId, gameType, timeFormat);

  const chartData = (history || []).map((h, i) => ({
    name: `#${i + 1}`,
    rating: h.new_rating,
    date: new Date(h.created_at).toLocaleDateString("vi-VN"),
  })).reverse();

  return (
    <Box>
      <Stack direction="row" spacing={2} mb={2}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Bộ môn</InputLabel>
          <Select value={gameType} label="Bộ môn" onChange={(e: SelectChangeEvent) => setGameType(e.target.value as GameType)}>
            {GAME_TYPES.map((g) => <MenuItem key={g.value} value={g.value}>{g.label}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Thể thức</InputLabel>
          <Select value={timeFormat} label="Thể thức" onChange={(e: SelectChangeEvent) => setTimeFormat(e.target.value as TimeFormat)}>
            {TIME_FORMATS.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </Select>
        </FormControl>
      </Stack>
      {chartData.length === 0 ? (
        <Typography color="text.secondary">Chưa có dữ liệu rating cho tổ hợp này</Typography>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={["dataMin - 50", "dataMax + 50"]} />
            <Tooltip labelFormatter={(_, payload) => payload[0]?.payload?.date || ""} />
            <Line type="monotone" dataKey="rating" stroke="#0054A6" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Box>
  );
}

export default RatingChart;
