import HomeIcon from "@mui/icons-material/Home";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import MuiBreadcrumbs from "@mui/material/Breadcrumbs";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { useLocation, useNavigate } from "react-router-dom";

const PATH_LABELS: Record<string, string> = {
  members: "Thành viên",
  tournaments: "Giải đấu",
  play: "Chơi cờ",
  openings: "Khai cuộc",
  ratings: "Bảng xếp hạng",
  attendance: "Điểm danh",
  achievements: "Huy hiệu",
  finance: "Tài chính",
  news: "Tin tức",
  training: "Luyện tập",
  admin: "Quản trị",
  gallery: "Thư viện ảnh",
  calendar: "Lịch",
  history: "Lịch sử",
  stats: "Thống kê",
  watch: "Xem lại",
  replay: "Phát lại",
};

function Breadcrumb() {
  const location = useLocation();
  const navigate = useNavigate();

  if (location.pathname === "/") return null;

  const segments = location.pathname.split("/").filter(Boolean);

  return (
    <MuiBreadcrumbs separator={<NavigateNextIcon fontSize="small" />} sx={{ mb: 2 }}>
      <Link
        underline="hover"
        color="inherit"
        sx={{ display: "flex", alignItems: "center", cursor: "pointer" }}
        onClick={() => navigate("/")}
      >
        <HomeIcon sx={{ mr: 0.5, fontSize: 18 }} />
        Trang chủ
      </Link>
      {segments.map((segment, index) => {
        const path = "/" + segments.slice(0, index + 1).join("/");
        const isLast = index === segments.length - 1;
        const label = PATH_LABELS[segment] || segment;

        if (isLast) {
          return (
            <Typography key={path} color="text.primary" fontWeight={500}>
              {label}
            </Typography>
          );
        }

        return (
          <Link
            key={path}
            underline="hover"
            color="inherit"
            sx={{ cursor: "pointer" }}
            onClick={() => navigate(path)}
          >
            {label}
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
}

export default Breadcrumb;
