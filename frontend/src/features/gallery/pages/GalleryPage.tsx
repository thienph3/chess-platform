import AddPhotoAlternateIcon from "@mui/icons-material/AddPhotoAlternate";
import DeleteIcon from "@mui/icons-material/Delete";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import AppSnackbar from "@/components/AppSnackbar";
import EmptyState from "@/components/EmptyState";

import { useDeleteImage, useGallery, useUploadImage } from "../hooks/useGallery";

const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace("/api/v1", "") || "http://localhost:8000";

function GalleryPage() {
  const [page] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({
    open: false, message: "", severity: "success",
  });

  const { data, isLoading } = useGallery(page);
  const uploadMutation = useUploadImage();
  const deleteMutation = useDeleteImage();

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);

    try {
      await uploadMutation.mutateAsync(formData);
      setSnackbar({ open: true, message: "Tải ảnh lên thành công", severity: "success" });
      setDialogOpen(false);
      setFile(null);
      setTitle("");
      setDescription("");
    } catch {
      setSnackbar({ open: true, message: "Có lỗi xảy ra", severity: "error" });
    }
  };

  const handleDelete = async (id: string) => {
    await deleteMutation.mutateAsync(id);
    setSnackbar({ open: true, message: "Đã xóa ảnh", severity: "success" });
  };

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Thư viện ảnh</Typography>
        <Button variant="contained" startIcon={<AddPhotoAlternateIcon />} onClick={() => setDialogOpen(true)}>
          Tải ảnh lên
        </Button>
      </Stack>

      {(!data?.data || data.data.length === 0) ? (
        <EmptyState
          icon={<AddPhotoAlternateIcon sx={{ fontSize: 40 }} />}
          message="Chưa có ảnh nào"
          actionLabel="Tải ảnh lên"
          onAction={() => setDialogOpen(true)}
        />
      ) : (
        <Grid container spacing={2}>
          {data.data.map((img) => (
            <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={img.id}>
              <Card sx={{ position: "relative" }}>
                <CardMedia component="img" height={200} image={`${API_BASE}${img.url}`} alt={img.title || "Ảnh CLB"} />
                <IconButton
                  size="small" color="error" sx={{ position: "absolute", top: 4, right: 4, bgcolor: "white" }}
                  onClick={() => handleDelete(img.id)} aria-label="Xóa ảnh"
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
                {img.title && (
                  <Box p={1}><Typography variant="body2" noWrap>{img.title}</Typography></Box>
                )}
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Tải ảnh lên</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Button variant="outlined" component="label">
              {file ? file.name : "Chọn file ảnh"}
              <input type="file" hidden accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </Button>
            <TextField label="Tiêu đề" value={title} onChange={(e) => setTitle(e.target.value)} fullWidth />
            <TextField label="Mô tả" value={description} onChange={(e) => setDescription(e.target.value)} fullWidth multiline rows={2} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Hủy</Button>
          <Button variant="contained" onClick={handleUpload} disabled={!file || uploadMutation.isPending}>Tải lên</Button>
        </DialogActions>
      </Dialog>

      <AppSnackbar open={snackbar.open} message={snackbar.message} severity={snackbar.severity}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))} />
    </Box>
  );
}

export default GalleryPage;
