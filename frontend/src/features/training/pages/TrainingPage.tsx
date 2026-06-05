import SchoolIcon from "@mui/icons-material/School";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import EmptyState from "@/components/EmptyState";

function TrainingPage() {
  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={600}>Luyện tập</Typography>
      <Box>
        <EmptyState
          icon={<SchoolIcon sx={{ fontSize: 80 }} />}
          message="Tính năng đang phát triển"
        />
        <Typography variant="body2" color="text.secondary" textAlign="center" mt={2}>
          Sắp ra mắt: Bài tập chiến thuật, câu đố cờ vua, cờ tướng và cờ vây.
          Luyện tập hàng ngày để nâng cao kỹ năng của bạn.
        </Typography>
      </Box>
    </Stack>
  );
}

export default TrainingPage;
