import GroupIcon from "@mui/icons-material/Group";
import SearchIcon from "@mui/icons-material/Search";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import InputAdornment from "@mui/material/InputAdornment";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef, GridPaginationModel } from "@mui/x-data-grid";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppSnackbar from "@/components/AppSnackbar";
import { dataGridLocaleText } from "@/utils/dataGridLocale";

import MemberFormDialog from "../components/MemberFormDialog";
import { useCreateMember, useUpdateMember } from "../hooks/useMemberMutations";
import { useMembers } from "../hooks/useMembers";
import { IMember, IMemberCreate } from "../types";

const columns: GridColDef[] = [
  { field: "full_name", headerName: "Họ tên", flex: 1 },
  { field: "email", headerName: "Email", flex: 1 },
  { field: "phone", headerName: "Điện thoại", width: 150 },
  { field: "skill_level", headerName: "Trình độ", width: 120 },
];

function MembersPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMember, setEditMember] = useState<IMember | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({
    open: false, message: "", severity: "success",
  });

  const { data, isLoading } = useMembers({ page: page + 1, pageSize, search });
  const createMutation = useCreateMember();
  const updateMutation = useUpdateMember();

  const handleCreate = () => { setEditMember(null); setDialogOpen(true); };

  const handleSubmit = async (formData: IMemberCreate) => {
    try {
      if (editMember) {
        await updateMutation.mutateAsync({ id: editMember.id, data: formData });
        setSnackbar({ open: true, message: "Cập nhật thành viên thành công", severity: "success" });
      } else {
        await createMutation.mutateAsync(formData);
        setSnackbar({ open: true, message: "Thêm thành viên thành công", severity: "success" });
      }
      setDialogOpen(false);
    } catch {
      setSnackbar({ open: true, message: "Có lỗi xảy ra", severity: "error" });
    }
  };

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Thành viên</Typography>
        <Button variant="contained" startIcon={<GroupIcon />} onClick={handleCreate}>Thêm thành viên</Button>
      </Stack>
      <TextField
        placeholder="Tìm kiếm theo tên..."
        size="small"
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(0); }}
        sx={{ mb: 2, width: 300 }}
        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }}
      />
      <DataGrid
        rows={data?.data || []}
        columns={columns}
        rowCount={data?.total || 0}
        paginationMode="server"
        paginationModel={{ page, pageSize }}
        onPaginationModelChange={(model: GridPaginationModel) => { setPage(model.page); setPageSize(model.pageSize); }}
        onRowClick={(params) => navigate(`/members/${params.row.id}`)}
        pageSizeOptions={[10, 20, 50]}
        disableRowSelectionOnClick
        autoHeight
        localeText={dataGridLocaleText}
        sx={{ cursor: "pointer" }}
      />
      <MemberFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleSubmit}
        member={editMember}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />
      <AppSnackbar
        open={snackbar.open}
        message={snackbar.message}
        severity={snackbar.severity}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
      />
    </Box>
  );
}

export default MembersPage;
