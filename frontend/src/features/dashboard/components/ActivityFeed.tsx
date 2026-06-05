import ExtensionIcon from "@mui/icons-material/Extension";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";

import { useActivityFeed } from "../hooks/useActivityFeed";

function getGameIcon(gameType: string) {
  if (gameType === "go") return <ExtensionIcon color="success" />;
  return <SportsEsportsIcon color="primary" />;
}

function ActivityFeed() {
  const { data: activities, isLoading } = useActivityFeed();

  if (isLoading) {
    return <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 1 }} />;
  }

  if (!activities || activities.length === 0) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="text.secondary">Chưa có hoạt động gần đây</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" fontWeight={600} mb={1}>
        Hoạt động gần đây
      </Typography>
      <List disablePadding>
        {activities.map((item) => (
          <ListItem key={item.id} disableGutters>
            <ListItemIcon sx={{ minWidth: 40 }}>
              {getGameIcon(item.gameType)}
            </ListItemIcon>
            <ListItemText
              primary={`${item.white} vs ${item.black}`}
              secondary={`${item.result} • ${item.date}`}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}

export default ActivityFeed;
