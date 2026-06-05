import DoneAllIcon from "@mui/icons-material/DoneAll";
import NotificationsIcon from "@mui/icons-material/Notifications";
import Badge from "@mui/material/Badge";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import {
  useMarkAllRead,
  useMarkRead,
  useNotifications,
  useUnreadCount,
} from "@/features/notifications";
import type { INotification } from "@/features/notifications";

function NotificationBell() {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const { data: count = 0 } = useUnreadCount();
  const { data: notifications = [] as INotification[] } = useNotifications(20);
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  const handleOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => setAnchorEl(null);

  const handleClickNotification = (id: string, isRead: boolean) => {
    if (!isRead) {
      markRead.mutate(id);
    }
  };

  const handleMarkAllRead = () => {
    markAllRead.mutate();
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton onClick={handleOpen} aria-label="Thông báo" color="inherit">
        <Badge badgeContent={count} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <Box sx={{ width: 360, maxHeight: 400, overflow: "auto" }}>
          <Box sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Typography variant="subtitle1" fontWeight={700}>
              Thông báo
            </Typography>
            {count > 0 && (
              <Button
                size="small"
                startIcon={<DoneAllIcon />}
                onClick={handleMarkAllRead}
              >
                Đánh dấu tất cả đã đọc
              </Button>
            )}
          </Box>

          {notifications.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: "center" }}>
              Không có thông báo
            </Typography>
          ) : (
            <List disablePadding>
              {notifications.map((n: INotification) => (
                <ListItemButton
                  key={n.id}
                  onClick={() => handleClickNotification(n.id, n.is_read)}
                  sx={{ bgcolor: n.is_read ? "transparent" : "action.hover" }}
                >
                  <ListItemText
                    primary={n.title}
                    secondary={n.message}
                    primaryTypographyProps={{
                      fontWeight: n.is_read ? 400 : 700,
                      variant: "body2",
                    }}
                    secondaryTypographyProps={{ variant: "caption", noWrap: true }}
                  />
                </ListItemButton>
              ))}
            </List>
          )}
        </Box>
      </Popover>
    </>
  );
}

export default NotificationBell;
