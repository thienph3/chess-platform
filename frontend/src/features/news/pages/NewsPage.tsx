import AddIcon from "@mui/icons-material/Add";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import PushPinIcon from "@mui/icons-material/PushPin";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import EmptyState from "@/components/EmptyState";
import { useAuthContext } from "@/features/auth/context/AuthContext";

import RichTextEditor from "../components/RichTextEditor";
import { useCreateNews, useNewsList } from "../hooks/useNews";

function NewsPage() {
  const { data: posts, isLoading } = useNewsList();
  const { user } = useAuthContext();
  const [open, setOpen] = useState(false);
  const isAdmin = user?.role === "admin";

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={200} /></Box>;
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Tin tức CLB</Typography>
        {isAdmin && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
            Đăng tin
          </Button>
        )}
      </Stack>

      {!posts?.length ? (
        <EmptyState icon={<NewspaperIcon sx={{ fontSize: 40 }} />} message="Chưa có tin tức nào" />
      ) : (
        <Stack spacing={2}>
          {posts.map((post) => (
            <Card key={post.id}>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} mb={1}>
                  <Typography variant="h6" fontWeight={600}>{post.title}</Typography>
                  {post.is_pinned && <Chip icon={<PushPinIcon />} label="Ghim" size="small" color="warning" />}
                </Stack>
                <Typography color="text.secondary" sx={{ whiteSpace: "pre-line" }}
                  dangerouslySetInnerHTML={{
                    __html: post.content.length > 300 ? `${post.content.slice(0, 300)}...` : post.content,
                  }}
                />
                <Typography variant="caption" color="text.secondary" mt={1} display="block">
                  {new Date(post.created_at).toLocaleDateString("vi-VN")}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      <CreateNewsDialog open={open} onClose={() => setOpen(false)} />
    </Box>
  );
}

function CreateNewsDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isPinned, setIsPinned] = useState(false);
  const createNews = useCreateNews();

  const handleSubmit = () => {
    createNews.mutate({ title, content, is_pinned: isPinned }, {
      onSuccess: () => { onClose(); setTitle(""); setContent(""); setIsPinned(false); },
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Đăng tin mới</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          <TextField label="Tiêu đề" value={title} onChange={(e) => setTitle(e.target.value)} fullWidth />
          <RichTextEditor value={content} onChange={setContent} placeholder="Nhập nội dung bài viết..." />
          <Button
            variant={isPinned ? "contained" : "outlined"}
            size="small"
            startIcon={<PushPinIcon />}
            onClick={() => setIsPinned(!isPinned)}
            sx={{ alignSelf: "flex-start" }}
          >
            {isPinned ? "Đã ghim" : "Ghim bài viết"}
          </Button>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Hủy</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={!title || !content || createNews.isPending}>
          Đăng tin
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default NewsPage;
