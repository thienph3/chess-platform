import { useCallback, useMemo, useSyncExternalStore } from "react";

type ThemeMode = "light" | "dark";

const STORAGE_KEY = "vcc_theme_mode";

function getSnapshot(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "dark" || stored === "light") return stored;
  return "light";
}

function getServerSnapshot(): ThemeMode {
  return "light";
}

let listeners: Array<() => void> = [];

function subscribe(listener: () => void) {
  listeners = [...listeners, listener];
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
}

function emitChange() {
  listeners.forEach((listener) => listener());
}

export function useThemeMode() {
  const mode = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const toggleMode = useCallback(() => {
    const next: ThemeMode = mode === "light" ? "dark" : "light";
    localStorage.setItem(STORAGE_KEY, next);
    emitChange();
  }, [mode]);

  return useMemo(() => ({ mode, toggleMode }), [mode, toggleMode]);
}
