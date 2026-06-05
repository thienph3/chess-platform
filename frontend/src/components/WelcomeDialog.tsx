import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import GroupIcon from "@mui/icons-material/Group";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

const STORAGE_KEY = "vcc_welcome_shown";

function WelcomeDialog() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const shown = localStorage.getItem(STORAGE_KEY);
    if (!shown) setOpen(true);
  }, []);

  const handleClose = () => {
    localStorage.setItem(STORAGE_KEY, "true");
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ textAlign: "center", fontWeight: 700 }}>
        Chào mừng đến VCC Platform! 🎉
      </DialogTitle>
      <DialogContent>
        <Typography color="text.secondary" textAlign="center" mb={3}>
          Nền tảng quản lý và thi đấu cờ của CLB Cờ Vinamilk
        </Typography>
        <Stack spacing={2}>
          <Feature icon={<SportsEsportsIcon color="primary" />} title="Chơi cờ trực tuyến" desc="Cờ vua, Cờ tướng, Cờ vây — chơi với thành viên CLB" />
          <Feature icon={<EmojiEventsIcon color="secondary" />} title="Giải đấu" desc="Tham gia giải, theo dõi bảng xếp hạng ELO" />
          <Feature icon={<GroupIcon color="success" />} title="Cộng đồng" desc="Kết nối, thách đấu, và cùng nhau tiến bộ" />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ justifyContent: "center", pb: 3 }}>
        <Button variant="contained" size="large" onClick={handleClose}>
          Bắt đầu khám phá
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <Stack direction="row" spacing={2} alignItems="center">
      {icon}
      <Stack>
        <Typography fontWeight={600}>{title}</Typography>
        <Typography variant="body2" color="text.secondary">{desc}</Typography>
      </Stack>
    </Stack>
  );
}

export default WelcomeDialog;
