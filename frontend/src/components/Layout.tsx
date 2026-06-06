import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import GroupIcon from "@mui/icons-material/Group";
import HomeIcon from "@mui/icons-material/Home";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import LightModeIcon from "@mui/icons-material/LightMode";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import PhotoLibraryIcon from "@mui/icons-material/PhotoLibrary";
import SchoolIcon from "@mui/icons-material/School";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { ReactNode, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuthContext } from "@/features/auth/context/AuthContext";
import { useThemeMode } from "@/hooks/useThemeMode";

import MobileNav from "./MobileNav";
import NotificationBell from "./NotificationBell";
import WelcomeDialog from "./WelcomeDialog";

const DRAWER_WIDTH = 240;

interface NavItem { label: string; path: string; icon: ReactNode; }

const navItems: NavItem[] = [
  { label: "Trang chủ", path: "/", icon: <HomeIcon /> },
  { label: "Thành viên", path: "/members", icon: <GroupIcon /> },
  { label: "Giải đấu", path: "/tournaments", icon: <EmojiEventsIcon /> },
  { label: "Chơi cờ", path: "/play", icon: <SportsEsportsIcon /> },
  { label: "Khai cuộc", path: "/openings", icon: <MenuBookIcon /> },
  { label: "Bảng xếp hạng", path: "/ratings", icon: <LeaderboardIcon /> },
  { label: "Huy hiệu", path: "/achievements", icon: <MilitaryTechIcon /> },
  { label: "Điểm danh", path: "/attendance", icon: <EventAvailableIcon /> },
  { label: "Tài chính", path: "/finance", icon: <AccountBalanceIcon /> },
  { label: "Tin tức", path: "/news", icon: <NewspaperIcon /> },
  { label: "Luyện tập", path: "/training", icon: <SchoolIcon /> },
  { label: "Thư viện ảnh", path: "/gallery", icon: <PhotoLibraryIcon /> },
];

const adminItem: NavItem = { label: "Quản trị", path: "/admin", icon: <AdminPanelSettingsIcon /> };

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthContext();
  const { mode, toggleMode } = useThemeMode();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleLogout = () => { setAnchorEl(null); logout(); navigate("/login"); };
  const isActive = (path: string) => path === "/" ? location.pathname === "/" : location.pathname.startsWith(path);

  const items = user?.role === "admin" ? [...navItems, adminItem] : navItems;
  const userInitial = user?.email?.[0]?.toUpperCase() || "U";

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH, flexShrink: 0, display: { xs: "none", md: "block" },
          "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", border: "none", bgcolor: "#FFFFFF" },
        }}
      >
        {/* Logo */}
        <Box sx={{ px: 3, py: 2.5 }}>
          <Typography variant="h6" fontWeight={800} color="primary" sx={{ letterSpacing: -0.5, cursor: "pointer" }} onClick={() => navigate("/")}>
            VCC Platform
          </Typography>
        </Box>

        {/* Nav */}
        <List sx={{ flex: 1, overflow: "auto", px: 1.5 }}>
          {items.map((item) => (
            <ListItemButton
              key={item.path}
              onClick={() => navigate(item.path)}
              selected={isActive(item.path)}
              sx={{ py: 1, mb: 0.25, borderRadius: 2 }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: isActive(item.path) ? "primary.main" : "text.secondary" }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: isActive(item.path) ? 600 : 400 }}
              />
            </ListItemButton>
          ))}
        </List>

        {/* User section at bottom */}
        <Box sx={{ px: 2, py: 2, borderTop: "1px solid #F0F0F0" }}>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Avatar sx={{ width: 36, height: 36, bgcolor: "primary.main", fontSize: 14, fontWeight: 700 }}>{userInitial}</Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="body2" fontWeight={600} noWrap>{user?.email?.split("@")[0]}</Typography>
              <Typography variant="caption" color="text.secondary">Thành viên</Typography>
            </Box>
          </Stack>
        </Box>
      </Drawer>

      {/* Main area */}
      <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {/* Top bar */}
        <Box sx={{ px: { xs: 2, md: 4 }, py: 1.5, display: "flex", alignItems: "center", bgcolor: "#FFFFFF", borderBottom: "1px solid #F0F0F0" }}>
          <Box sx={{ flex: 1 }} />
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <IconButton onClick={toggleMode} size="small" aria-label="Chuyển giao diện">
              {mode === "dark" ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
            </IconButton>
            <NotificationBell />
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small">
              <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main", fontSize: 13, fontWeight: 700 }}>{userInitial}</Avatar>
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem disabled><Typography variant="body2" color="text.secondary">{user?.email}</Typography></MenuItem>
              <MenuItem onClick={handleLogout}><ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>Đăng xuất</MenuItem>
            </Menu>
          </Stack>
        </Box>

        {/* Content */}
        <Box component="main" sx={{ flex: 1, p: { xs: 2, md: 4 }, pb: { xs: 10, md: 4 } }}>
          <Box sx={{ maxWidth: 1280 }}>
            <Outlet />
          </Box>
        </Box>
      </Box>

      <MobileNav />
      <WelcomeDialog />
    </Box>
  );
}

export default Layout;
