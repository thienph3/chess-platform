import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useFinanceReport } from "../hooks/useFinanceReport";

function FinanceChart() {
  const currentYear = new Date().getFullYear();
  const [year, setYear] = useState(currentYear);
  const [period, setPeriod] = useState<"monthly" | "quarterly">("monthly");

  const { data: report } = useFinanceReport(year, period);

  const chartData = (report?.items || []).map((item) => ({
    name: item.period.replace(`${year}-`, ""),
    "Thu": item.total_income,
    "Chi": item.total_expense,
  }));

  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  return (
    <Box>
      <Stack direction="row" spacing={2} mb={2}>
        <FormControl size="small" sx={{ minWidth: 100 }}>
          <InputLabel>Năm</InputLabel>
          <Select value={String(year)} label="Năm" onChange={(e: SelectChangeEvent) => setYear(Number(e.target.value))}>
            {years.map((y) => <MenuItem key={y} value={String(y)}>{y}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Kỳ</InputLabel>
          <Select value={period} label="Kỳ" onChange={(e: SelectChangeEvent) => setPeriod(e.target.value as "monthly" | "quarterly")}>
            <MenuItem value="monthly">Theo tháng</MenuItem>
            <MenuItem value="quarterly">Theo quý</MenuItem>
          </Select>
        </FormControl>
      </Stack>
      {chartData.length === 0 ? (
        <Typography color="text.secondary">Chưa có dữ liệu</Typography>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v: number) => `${(v / 1000000).toFixed(1)}M`} />
            <Tooltip formatter={(value) => `${Number(value).toLocaleString("vi-VN")} ₫`} />
            <Legend />
            <Bar dataKey="Thu" fill="#4CAF50" />
            <Bar dataKey="Chi" fill="#F44336" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </Box>
  );
}

export default FinanceChart;
