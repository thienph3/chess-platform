import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef } from "@mui/x-data-grid";

import { useAuthContext } from "@/features/auth/context/AuthContext";

import { useUsers } from "../hooks/useUsers";

const columns: GridColDef[] = [
  { field: "email", headerName: "Email", flex: 1, minWidth: 200 },
  { field: "role", headerName: "Vai trò", width: 120 },
  {
    field: "is_active",
    headerName: "Trạng thái",
    width: 120,
    valueGetter: (value: boolean) => (value ? "Hoạt động" : "Vô hiệu"),
  },
  {
    field: "created_at",
    headerName: "Ngày tạo",
    width: 160,
    valueGetter: (value: string) => new Date(value).toLocaleDateString("vi-VN"),
  },
];

function AdminPage() {
  const { user } = useAuthContext();
  const { data: users, isLoading } = useUsers();

  if (user?.role !== "admin") {
    return (
      <Box p={3}>
        <Typography variant="h6" color="error">
          Không có quyền truy cập
        </Typography>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Stack spacing={2}>
        <Typography variant="h5" fontWeight={600}>Quản trị</Typography>
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 1 }} />
      </Stack>
    );
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={600}>Quản trị</Typography>
      <Typography variant="body2" color="text.secondary">
        Danh sách tất cả người dùng trong hệ thống
      </Typography>
      <Box sx={{ height: 500 }}>
        <DataGrid
          rows={users || []}
          columns={columns}
          pageSizeOptions={[10, 25, 50]}
          initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
          disableRowSelectionOnClick
        />
      </Box>
    </Stack>
  );
}

export default AdminPage;
