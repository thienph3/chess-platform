import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#00653E",
      light: "#4CAF50",
    },
    secondary: {
      main: "#F5E6C8",
    },
    warning: {
      main: "#FFB800",
    },
    error: {
      main: "#D32F2F",
    },
    success: {
      main: "#2E7D32",
    },
    background: {
      default: "#FAFAF7",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1A1A1A",
      secondary: "#6B6B6B",
    },
  },
  typography: {
    fontFamily: "'Nunito', 'Inter', sans-serif",
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600 },
    body1: { lineHeight: 1.6 },
    body2: { lineHeight: 1.6 },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
          borderRadius: 24,
          paddingLeft: 20,
          paddingRight: 20,
        },
        outlined: {
          borderWidth: 1.5,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 12,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 20,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#FFFFFF",
          borderRight: "1px solid #F0EDE8",
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginLeft: 8,
          marginRight: 8,
          "&.Mui-selected": {
            backgroundColor: "rgba(0, 101, 62, 0.08)",
            color: "#00653E",
            borderLeft: "3px solid #00653E",
            "& .MuiListItemIcon-root": {
              color: "#00653E",
            },
          },
          "&:hover": {
            backgroundColor: "rgba(0, 101, 62, 0.04)",
          },
        },
      },
    },
  },
});

export default theme;
