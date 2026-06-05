import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Icon from "@mui/material/Icon";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useMemo } from "react";

import EmptyState from "@/components/EmptyState";

import { IAchievement, IMemberAchievement, useAchievements, useMemberAchievements } from "../hooks/useAchievements";

function AchievementsPage() {
  const { data: allAchievements, isLoading } = useAchievements();
  const { data: memberAchievements } = useMemberAchievements();

  const earnedMap = useMemo(() => {
    const map = new Map<string, string>();
    (memberAchievements || []).forEach((ma: IMemberAchievement) => {
      map.set(ma.achievement_id, ma.earned_at);
    });
    return map;
  }, [memberAchievements]);

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;

  if (!allAchievements || allAchievements.length === 0) {
    return (
      <Box>
        <Typography variant="h5" fontWeight={600} mb={3}>Huy hiệu</Typography>
        <EmptyState
          icon={<EmojiEventsIcon sx={{ fontSize: 60 }} />}
          message="Chưa có huy hiệu nào"
        />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" fontWeight={600} mb={3}>Huy hiệu</Typography>
      <Grid container spacing={2}>
        {allAchievements.map((achievement: IAchievement) => {
          const earnedAt = earnedMap.get(achievement.id);
          const isEarned = !!earnedAt;
          return (
            <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={achievement.id}>
              <Card sx={{ opacity: isEarned ? 1 : 0.5, height: "100%" }}>
                <CardContent>
                  <Stack alignItems="center" spacing={1}>
                    <Icon color={isEarned ? "secondary" : "disabled"} sx={{ fontSize: 40 }}>
                      {achievement.icon || "emoji_events"}
                    </Icon>
                    <Typography fontWeight={600} textAlign="center">{achievement.name}</Typography>
                    <Typography variant="body2" color="text.secondary" textAlign="center">
                      {achievement.description}
                    </Typography>
                    {isEarned && (
                      <Typography variant="caption" color="success.main">
                        Đạt được: {new Date(earnedAt).toLocaleDateString("vi-VN")}
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}

export default AchievementsPage;
