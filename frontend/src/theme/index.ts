import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#006241",
      light: "#338a6a",
      dark: "#004430",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#F5E6C8",
      light: "#FFF8EC",
      dark: "#D4B896",
    },
    warning: {
      main: "#F5A623",
    },
    error: {
      main: "#D32F2F",
    },
    success: {
      main: "#006241",
    },
    background: {
      default: "#F9FAFB",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1A1A1A",
      secondary: "#5F6368",
    },
  },
  typography: {
    fontFamily: "'Nunito', 'Inter', -apple-system, sans-serif",
    h4: { fontWeight: 800 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600 },
    body1: { lineHeight: 1.6 },
    body2: { lineHeight: 1.5 },
    button: { fontWeight: 600 },
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
          paddingLeft: 24,
          paddingRight: 24,
          paddingTop: 10,
          paddingBottom: 10,
        },
        contained: {
          boxShadow: "none",
          "&:hover": {
            boxShadow: "0 4px 12px rgba(0, 98, 65, 0.3)",
          },
        },
        outlined: {
          borderWidth: 1.5,
          "&:hover": {
            borderWidth: 1.5,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 1px 8px rgba(0,0,0,0.04)",
          border: "1px solid #F0F0F0",
          "&:hover": {
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          },
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
          fontWeight: 500,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#FFFFFF",
          borderRight: "1px solid #F0F0F0",
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
            backgroundColor: "rgba(0, 98, 65, 0.08)",
            color: "#006241",
            borderLeft: "3px solid #006241",
            "& .MuiListItemIcon-root": {
              color: "#006241",
            },
          },
          "&:hover": {
            backgroundColor: "rgba(0, 98, 65, 0.04)",
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
  },
});

export default theme;
