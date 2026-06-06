import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { Navigate, Outlet } from "react-router-dom";

import { useAuthContext } from "@/features/auth/context/AuthContext";

export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthContext();

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", bgcolor: "#FAFAF7" }}>
        <CircularProgress size={40} sx={{ color: "#00653E" }} />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
