import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <Box p={4}>
          <Stack alignItems="center" spacing={2}>
            <Typography variant="h5" color="error" fontWeight={600}>
              Đã xảy ra lỗi
            </Typography>
            <Typography variant="body1" color="text.secondary" textAlign="center">
              Trang này gặp sự cố. Vui lòng thử lại hoặc quay về trang chủ.
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button variant="contained" onClick={this.handleRetry}>
                Thử lại
              </Button>
              <Button variant="outlined" href="/">
                Về trang chủ
              </Button>
            </Stack>
          </Stack>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
