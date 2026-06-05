import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import GroupIcon from "@mui/icons-material/Group";
import HomeIcon from "@mui/icons-material/Home";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
import Paper from "@mui/material/Paper";
import { useLocation, useNavigate } from "react-router-dom";

const navItems = [
  { label: "Trang chủ", path: "/", icon: <HomeIcon /> },
  { label: "Thành viên", path: "/members", icon: <GroupIcon /> },
  { label: "Giải đấu", path: "/tournaments", icon: <EmojiEventsIcon /> },
  { label: "Chơi cờ", path: "/play", icon: <SportsEsportsIcon /> },
  { label: "Xếp hạng", path: "/ratings", icon: <LeaderboardIcon /> },
  { label: "Tài chính", path: "/finance", icon: <AccountBalanceIcon /> },
];

function MobileNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const currentIndex = navItems.findIndex((item) => location.pathname === item.path);

  return (
    <Paper
      sx={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        display: { xs: "flex", md: "none" },
        zIndex: 1200,
      }}
      elevation={3}
    >
      <BottomNavigation
        value={currentIndex >= 0 ? currentIndex : 0}
        onChange={(_, newValue) => navigate(navItems[newValue].path)}
        showLabels
        sx={{ width: "100%" }}
      >
        {navItems.map((item) => (
          <BottomNavigationAction
            key={item.path}
            label={item.label}
            icon={item.icon}
            aria-label={item.label}
          />
        ))}
      </BottomNavigation>
    </Paper>
  );
}

export default MobileNav;
