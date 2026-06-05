import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}

function EmptyState({ icon, message, actionLabel, onAction }: EmptyStateProps) {
  return (
    <Box py={8}>
      <Stack alignItems="center" spacing={2}>
        <Box sx={{ color: "text.secondary", opacity: 0.5 }}>{icon}</Box>
        <Typography color="text.secondary">{message}</Typography>
        {actionLabel && onAction && (
          <Button variant="contained" onClick={onAction}>{actionLabel}</Button>
        )}
      </Stack>
    </Box>
  );
}

export default EmptyState;
