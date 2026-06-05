import Skeleton from "@mui/material/Skeleton";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";

interface PlayerNameProps {
  memberId: string;
  variant?: "body2" | "body1" | "caption";
}

async function fetchMemberName(id: string): Promise<string> {
  const { data } = await apiClient.get(`/members/${id}`);
  return data.data?.full_name || id.slice(0, 8);
}

function PlayerName({ memberId, variant = "body2" }: PlayerNameProps) {
  const { data: name, isLoading } = useQuery({
    queryKey: ["member-name", memberId],
    queryFn: () => fetchMemberName(memberId),
    staleTime: 5 * 60 * 1000,
    enabled: !!memberId,
  });

  if (!memberId) return <Typography variant={variant}>—</Typography>;

  if (isLoading) {
    return <Skeleton width={80} height={20} />;
  }

  return (
    <Tooltip title={memberId} arrow>
      <Typography variant={variant} noWrap sx={{ maxWidth: 150 }}>
        {name || memberId.slice(0, 8) + "..."}
      </Typography>
    </Tooltip>
  );
}

export default PlayerName;
