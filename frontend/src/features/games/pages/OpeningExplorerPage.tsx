import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { useOpeningStats } from "../hooks/useOpenings";

function OpeningExplorerPage() {
  const [moves, setMoves] = useState<string[]>([]);
  const [gameType, setGameType] = useState("chess");
  const { data: stats, isLoading } = useOpeningStats(moves, gameType);

  const handleMoveClick = (move: string) => {
    setMoves((prev) => [...prev, move]);
  };

  const handleBack = () => {
    setMoves((prev) => prev.slice(0, -1));
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Khai cuộc</Typography>
        <TextField label="Bộ môn" select value={gameType} onChange={(e) => { setGameType(e.target.value); setMoves([]); }} size="small" sx={{ width: 150 }}>
          <MenuItem value="chess">Cờ vua</MenuItem>
          <MenuItem value="xiangqi">Cờ tướng</MenuItem>
          <MenuItem value="go">Cờ vây</MenuItem>
        </TextField>
      </Stack>

      <Stack direction="row" spacing={1} mb={2} alignItems="center">
        {moves.length > 0 && (
          <Button size="small" startIcon={<ArrowBackIcon />} onClick={handleBack}>Quay lại</Button>
        )}
        {moves.map((m, i) => (
          <Chip key={i} label={`${i + 1}. ${m}`} size="small" variant="outlined" />
        ))}
        {moves.length === 0 && <Typography variant="body2" color="text.secondary">Chọn nước đi để khám phá</Typography>}
      </Stack>

      {stats && (
        <Stack direction="row" spacing={2} mb={2}>
          <Chip label={`Tổng: ${stats.total_games} ván`} />
          <Chip label={`Trắng thắng: ${stats.white_wins}`} color="default" />
          <Chip label={`Hòa: ${stats.draws}`} color="info" />
          <Chip label={`Đen thắng: ${stats.black_wins}`} color="default" />
        </Stack>
      )}

      {isLoading ? (
        <Skeleton variant="rectangular" height={300} />
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nước đi</TableCell>
                <TableCell align="right">Số ván</TableCell>
                <TableCell align="right">Tỷ lệ thắng trắng</TableCell>
                <TableCell align="right">Hòa</TableCell>
                <TableCell align="right">Thắng đen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(stats?.next_moves || []).map((row) => (
                <TableRow key={row.move} hover sx={{ cursor: "pointer" }} onClick={() => handleMoveClick(row.move)}>
                  <TableCell><Typography fontWeight={500}>{row.move}</Typography></TableCell>
                  <TableCell align="right">{row.count}</TableCell>
                  <TableCell align="right">{row.win_rate_white}%</TableCell>
                  <TableCell align="right">{row.draw_rate}%</TableCell>
                  <TableCell align="right">{row.win_rate_black}%</TableCell>
                </TableRow>
              ))}
              {stats?.next_moves.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="text.secondary" py={2}>Không có dữ liệu</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

export default OpeningExplorerPage;
