import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";

interface AppSnackbarProps {
  open: boolean;
  message: string;
  severity?: "success" | "error" | "info" | "warning";
  onClose: () => void;
  autoHideDuration?: number;
}

function AppSnackbar({
  open,
  message,
  severity = "success",
  onClose,
  autoHideDuration = 3000,
}: AppSnackbarProps) {
  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={onClose}
      anchorOrigin={{ vertical: "top", horizontal: "right" }}
    >
      <Alert severity={severity} variant="filled" onClose={onClose}>
        {message}
      </Alert>
    </Snackbar>
  );
}

export default AppSnackbar;
