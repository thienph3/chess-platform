import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import GroupIcon from "@mui/icons-material/Group";
import HomeIcon from "@mui/icons-material/Home";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import LightModeIcon from "@mui/icons-material/LightMode";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import SchoolIcon from "@mui/icons-material/School";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { ReactNode, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuthContext } from "@/features/auth/context/AuthContext";
import { useThemeMode } from "@/hooks/useThemeMode";

import MobileNav from "./MobileNav";
import NotificationBell from "./NotificationBell";
import WelcomeDialog from "./WelcomeDialog";

const DRAWER_WIDTH = 250;
const HEADER_HEIGHT = 64;

interface NavItem { label: string; path: string; icon: ReactNode; }
interface NavSection { title: string; items: NavItem[]; }

const navSections: NavSection[] = [
  { title: "Chính", items: [
    { label: "Trang chủ", path: "/", icon: <HomeIcon /> },
    { label: "Thành viên", path: "/members", icon: <GroupIcon /> },
    { label: "Giải đấu", path: "/tournaments", icon: <EmojiEventsIcon /> },
    { label: "Chơi cờ", path: "/play", icon: <SportsEsportsIcon /> },
  ]},
  { title: "Khám phá", items: [
    { label: "Khai cuộc", path: "/openings", icon: <MenuBookIcon /> },
    { label: "Bảng xếp hạng", path: "/ratings", icon: <LeaderboardIcon /> },
    { label: "Huy hiệu", path: "/achievements", icon: <MilitaryTechIcon /> },
  ]},
  { title: "CLB", items: [
    { label: "Điểm danh", path: "/attendance", icon: <EventAvailableIcon /> },
    { label: "Tài chính", path: "/finance", icon: <AccountBalanceIcon /> },
    { label: "Tin tức", path: "/news", icon: <NewspaperIcon /> },
  ]},
  { title: "Khác", items: [
    { label: "Luyện tập", path: "/training", icon: <SchoolIcon /> },
    { label: "Thư viện ảnh", path: "/gallery", icon: <MoreHorizIcon /> },
  ]},
];

const adminItem: NavItem = { label: "Quản trị", path: "/admin", icon: <AdminPanelSettingsIcon /> };

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthContext();
  const { mode, toggleMode } = useThemeMode();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({ "Khác": true });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleLogout = () => { setAnchorEl(null); logout(); navigate("/login"); };
  const toggleSection = (title: string) => setCollapsed((prev) => ({ ...prev, [title]: !prev[title] }));
  const isActive = (path: string) => path === "/" ? location.pathname === "/" : location.pathname.startsWith(path);

  const sections = user?.role === "admin"
    ? [...navSections.slice(0, 2), { ...navSections[2], items: [...navSections[2].items, adminItem] }, navSections[3]]
    : navSections;

  const userInitial = user?.email?.[0]?.toUpperCase() || "U";

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Header */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{ bgcolor: "white", borderBottom: "1px solid #F0EDE8", zIndex: (t) => t.zIndex.drawer + 1 }}
      >
        <Toolbar sx={{ height: HEADER_HEIGHT }}>
          <Typography variant="h6" noWrap color="primary" fontWeight={800} sx={{ letterSpacing: -0.5, width: DRAWER_WIDTH - 32 }}>
            VCC Platform
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Stack direction="row" alignItems="center" spacing={1}>
            <IconButton onClick={toggleMode} size="small" aria-label="Chuyển giao diện">
              {mode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
            <NotificationBell />
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small">
              <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main", fontSize: 14 }}>{userInitial}</Avatar>
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem disabled>
                <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
                Đăng xuất
              </MenuItem>
            </Menu>
          </Stack>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: "flex", flex: 1, pt: `${HEADER_HEIGHT}px` }}>
        {/* Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH, flexShrink: 0, display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", top: HEADER_HEIGHT, height: `calc(100% - ${HEADER_HEIGHT}px)` },
          }}
        >
          <List sx={{ flex: 1, overflow: "auto", px: 1, pt: 2 }}>
            {sections.map((section) => (
              <Box key={section.title} sx={{ mb: 0.5 }}>
                <ListSubheader
                  onClick={() => toggleSection(section.title)}
                  sx={{ cursor: "pointer", display: "flex", alignItems: "center", userSelect: "none", bgcolor: "transparent", lineHeight: 2.5 }}
                >
                  <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ flex: 1, textTransform: "uppercase", letterSpacing: 0.5, fontSize: "0.65rem" }}>
                    {section.title}
                  </Typography>
                  {collapsed[section.title] ? <ExpandMoreIcon fontSize="small" /> : <ExpandLessIcon fontSize="small" />}
                </ListSubheader>
                <Collapse in={!collapsed[section.title]}>
                  {section.items.map((item) => (
                    <ListItemButton key={item.path} onClick={() => navigate(item.path)} selected={isActive(item.path)} sx={{ py: 1 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: "0.875rem" }} />
                    </ListItemButton>
                  ))}
                </Collapse>
              </Box>
            ))}
          </List>
        </Drawer>

        {/* Content */}
        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 4 }, pb: { xs: 10, md: 4 }, bgcolor: "background.default", minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
          <Box sx={{ maxWidth: 1200 }}>
            <Outlet />
          </Box>
        </Box>
      </Box>

      {/* Footer */}
      <Box component="footer" sx={{ py: 2, px: 4, textAlign: "center", borderTop: "1px solid #F0EDE8", bgcolor: "white", ml: { md: `${DRAWER_WIDTH}px` } }}>
        <Typography variant="caption" color="text.secondary">
          © 2025 Vinamilk Chess Club. Powered by VCC Platform.
        </Typography>
      </Box>

      <MobileNav />
      <WelcomeDialog />
    </Box>
  );
}

export default Layout;
