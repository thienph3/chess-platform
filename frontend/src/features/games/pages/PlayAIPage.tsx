import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import ButtonGroup from "@mui/material/ButtonGroup";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "@/api/client";

const GAME_OPTIONS = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
  { value: "gomoku", label: "Cờ caro" },
];

const DIFFICULTY_OPTIONS = [
  { value: "easy", label: "Dễ" },
  { value: "medium", label: "Trung bình" },
  { value: "hard", label: "Khó" },
];

const TIME_OPTIONS = [
  { value: 60, increment: 0, label: "1+0" },
  { value: 180, increment: 2, label: "3+2" },
  { value: 300, increment: 0, label: "5+0" },
  { value: 300, increment: 5, label: "5+5" },
  { value: 600, increment: 0, label: "10+0" },
  { value: 900, increment: 0, label: "15+0" },
];

function PlayAIPage() {
  const navigate = useNavigate();
  const [gameType, setGameType] = useState("chess");
  const [difficulty, setDifficulty] = useState("medium");
  const [timeControl, setTimeControl] = useState(600);
  const [increment, setIncrement] = useState(0);
  const [colorChoice, setColorChoice] = useState("white");
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post("/games/ai/start", {
        game_type: gameType, difficulty, time_control: timeControl,
        increment, player_color: colorChoice,
      });
      const roomId = res.data?.data?.room_id;
      if (roomId) {
        navigate(`/play/${roomId}`);
      }
    } catch {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/play")} sx={{ mb: 2 }}>Lobby</Button>
      <Typography variant="h5" fontWeight={700} mb={3}>
        <SmartToyIcon sx={{ mr: 1, verticalAlign: "middle" }} />Chơi với máy
      </Typography>
      <Card sx={{ maxWidth: 420 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle2" mb={1}>Bộ môn</Typography>
              <ButtonGroup fullWidth>
                {GAME_OPTIONS.map((o) => (
                  <Button key={o.value} variant={gameType === o.value ? "contained" : "outlined"}
                    onClick={() => setGameType(o.value)}>{o.label}</Button>
                ))}
              </ButtonGroup>
            </Box>
            <Box>
              <Typography variant="subtitle2" mb={1}>Độ khó</Typography>
              <ButtonGroup fullWidth>
                {DIFFICULTY_OPTIONS.map((o) => (
                  <Button key={o.value} variant={difficulty === o.value ? "contained" : "outlined"}
                    onClick={() => setDifficulty(o.value)}>{o.label}</Button>
                ))}
              </ButtonGroup>
            </Box>
            <Box>
              <Typography variant="subtitle2" mb={1}>Thể thức</Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                {TIME_OPTIONS.map((o) => (
                  <Chip key={o.label} label={o.label} size="small"
                    variant={timeControl === o.value && increment === o.increment ? "filled" : "outlined"}
                    color={timeControl === o.value && increment === o.increment ? "primary" : "default"}
                    onClick={() => { setTimeControl(o.value); setIncrement(o.increment); }} />
                ))}
              </Stack>
            </Box>
            <Box>
              <Typography variant="subtitle2" mb={1}>Màu quân</Typography>
              <ButtonGroup fullWidth>
                <Button variant={colorChoice === "white" ? "contained" : "outlined"} onClick={() => setColorChoice("white")}>Trắng</Button>
                <Button variant={colorChoice === "random" ? "contained" : "outlined"} onClick={() => setColorChoice("random")}>Ngẫu nhiên</Button>
                <Button variant={colorChoice === "black" ? "contained" : "outlined"} onClick={() => setColorChoice("black")}>Đen</Button>
              </ButtonGroup>
            </Box>
            <Button variant="contained" size="large" onClick={handleStart} disabled={loading} startIcon={<SmartToyIcon />}>
              {loading ? "Đang tạo..." : "Bắt đầu"}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}

export default PlayAIPage;
