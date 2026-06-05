import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useTournamentCalendar } from "../hooks/useTournamentCalendar";
import { ITournament } from "../types";

const WEEKDAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];
const MONTH_NAMES = [
  "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
  "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12",
];

function getCalendarDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  // Ngày đầu tuần (T2 = 0)
  let startDow = firstDay.getDay() - 1;
  if (startDow < 0) startDow = 6;

  const days: (number | null)[] = [];
  for (let i = 0; i < startDow; i++) days.push(null);
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(d);
  // Padding cuối
  while (days.length % 7 !== 0) days.push(null);
  return days;
}

function TournamentCalendarPage() {
  const navigate = useNavigate();
  const [year, setYear] = useState(() => new Date().getFullYear());
  const [month, setMonth] = useState(() => new Date().getMonth());

  const { data: tournaments, isLoading } = useTournamentCalendar(year, month);

  const days = useMemo(() => getCalendarDays(year, month), [year, month]);

  // Map ngày → danh sách giải đấu
  const tournamentsByDay = useMemo(() => {
    const map: Record<number, ITournament[]> = {};
    if (!tournaments) return map;
    tournaments.forEach((t) => {
      if (!t.start_date) return;
      const date = new Date(t.start_date);
      if (date.getFullYear() === year && date.getMonth() === month) {
        const day = date.getDate();
        if (!map[day]) map[day] = [];
        map[day].push(t);
      }
    });
    return map;
  }, [tournaments, year, month]);

  const handlePrev = () => {
    if (month === 0) { setMonth(11); setYear(year - 1); }
    else setMonth(month - 1);
  };

  const handleNext = () => {
    if (month === 11) { setMonth(0); setYear(year + 1); }
    else setMonth(month + 1);
  };

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={500} /></Box>;
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Lịch giải đấu</Typography>
      </Stack>
      <Stack direction="row" alignItems="center" justifyContent="center" spacing={2} mb={2}>
        <IconButton onClick={handlePrev} aria-label="Tháng trước">
          <ChevronLeftIcon />
        </IconButton>
        <Typography variant="h6" fontWeight={600} sx={{ minWidth: 160, textAlign: "center" }}>
          {MONTH_NAMES[month]} {year}
        </Typography>
        <IconButton onClick={handleNext} aria-label="Tháng sau">
          <ChevronRightIcon />
        </IconButton>
      </Stack>
      <CalendarGrid
        days={days}
        tournamentsByDay={tournamentsByDay}
        onTournamentClick={(id) => navigate(`/tournaments/${id}`)}
      />
    </Box>
  );
}

interface CalendarGridProps {
  days: (number | null)[];
  tournamentsByDay: Record<number, ITournament[]>;
  onTournamentClick: (id: string) => void;
}

function CalendarGrid({ days, tournamentsByDay, onTournamentClick }: CalendarGridProps) {
  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: "repeat(7, 1fr)",
        gap: 0.5,
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        overflow: "hidden",
      }}
    >
      {WEEKDAYS.map((day) => (
        <Box key={day} sx={{ p: 1, bgcolor: "primary.main", textAlign: "center" }}>
          <Typography variant="body2" fontWeight={600} color="white">{day}</Typography>
        </Box>
      ))}
      {days.map((day, idx) => (
        <Box
          key={idx}
          sx={{
            minHeight: 80,
            p: 0.5,
            bgcolor: day ? "background.paper" : "action.hover",
            borderTop: 1,
            borderColor: "divider",
          }}
        >
          {day && (
            <>
              <Typography variant="caption" color="text.secondary" sx={{ pl: 0.5 }}>
                {day}
              </Typography>
              <Stack spacing={0.25} mt={0.25}>
                {(tournamentsByDay[day] || []).slice(0, 3).map((t) => (
                  <Chip
                    key={t.id}
                    label={t.name}
                    size="small"
                    color="primary"
                    variant="outlined"
                    onClick={() => onTournamentClick(t.id)}
                    sx={{ maxWidth: "100%", fontSize: "0.65rem", height: 20, cursor: "pointer" }}
                  />
                ))}
                {(tournamentsByDay[day]?.length || 0) > 3 && (
                  <Typography variant="caption" color="text.secondary">
                    +{tournamentsByDay[day].length - 3} giải khác
                  </Typography>
                )}
              </Stack>
            </>
          )}
        </Box>
      ))}
    </Box>
  );
}

export default TournamentCalendarPage;
