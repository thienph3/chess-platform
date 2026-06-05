import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

interface IMatch {
  id: string;
  white_player_id: string;
  black_player_id: string;
  result: string;
}

interface IRound {
  id: string;
  round_number: number;
  matches: IMatch[];
}

interface KnockoutBracketProps {
  rounds: IRound[];
}

function MatchBox({ match }: { match: IMatch }) {
  const whiteWon = match.result === "white_win";
  const blackWon = match.result === "black_win";

  return (
    <Card sx={{ minWidth: 160, border: "1px solid", borderColor: "grey.300" }}>
      <Box sx={{ px: 1.5, py: 0.5, bgcolor: whiteWon ? "success.light" : "transparent" }}>
        <Stack direction="row" justifyContent="space-between">
          <Typography variant="body2" fontWeight={whiteWon ? 700 : 400}>
            {match.white_player_id.slice(0, 8)}...
          </Typography>
          {whiteWon && <Typography variant="caption" color="success.dark">✓</Typography>}
        </Stack>
      </Box>
      <Box sx={{ px: 1.5, py: 0.5, borderTop: "1px solid", borderColor: "grey.200", bgcolor: blackWon ? "success.light" : "transparent" }}>
        <Stack direction="row" justifyContent="space-between">
          <Typography variant="body2" fontWeight={blackWon ? 700 : 400}>
            {match.black_player_id.slice(0, 8)}...
          </Typography>
          {blackWon && <Typography variant="caption" color="success.dark">✓</Typography>}
        </Stack>
      </Box>
    </Card>
  );
}

function KnockoutBracket({ rounds }: KnockoutBracketProps) {
  if (!rounds.length) {
    return <Typography color="text.secondary">Chưa có lịch đấu</Typography>;
  }

  return (
    <Box sx={{ overflowX: "auto", py: 2 }}>
      <Stack direction="row" spacing={4} alignItems="center">
        {rounds.map((round) => (
          <Stack key={round.id} spacing={2} alignItems="center">
            <Typography variant="subtitle2" fontWeight={600}>
              Vòng {round.round_number}
            </Typography>
            <Stack spacing={3} justifyContent="center" sx={{ minHeight: 200 }}>
              {round.matches.map((match) => (
                <MatchBox key={match.id} match={match} />
              ))}
            </Stack>
          </Stack>
        ))}
      </Stack>
      {/* SVG connector lines */}
      <Box sx={{ position: "relative", mt: -2 }}>
        <svg width="100%" height="4" style={{ position: "absolute", top: 0 }}>
          <line x1="0" y1="2" x2="100%" y2="2" stroke="#ccc" strokeWidth="1" strokeDasharray="4" />
        </svg>
      </Box>
    </Box>
  );
}

export default KnockoutBracket;
