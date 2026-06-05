/** Helpers cho hiển thị review data (đã lưu trong move_history). */

/** Map classification → annotation symbol */
export function classificationToSymbol(c: string | null): string {
  switch (c) {
    case "brilliant": return "!!";
    case "great": return "!";
    case "good": return "";
    case "book": return "";
    case "inaccuracy": return "?!";
    case "mistake": return "?";
    case "blunder": return "??";
    default: return "";
  }
}

/** Map classification → color */
export function classificationColor(c: string | null): string {
  switch (c) {
    case "brilliant": return "#1BACA6";
    case "great": return "#5C8BB0";
    case "good": return "#96BC4B";
    case "book": return "#A0A0A0";
    case "inaccuracy": return "#F7C631";
    case "mistake": return "#E58F2A";
    case "blunder": return "#CA3431";
    default: return "inherit";
  }
}

/** Format eval score (centipawns → display) */
export function formatEval(cp: number | null): string {
  if (cp === null) return "";
  if (Math.abs(cp) >= 10000) return cp > 0 ? "#" : "-#";
  const pawns = cp / 100;
  return pawns > 0 ? `+${pawns.toFixed(1)}` : pawns.toFixed(1);
}
