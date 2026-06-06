export const GAME_LABELS: Record<string, string> = {
  chess: "Cờ vua",
  xiangqi: "Cờ tướng",
  go: "Cờ vây",
  gomoku: "Cờ caro",
};

export const GAME_TYPES = [
  { value: "chess", label: "Cờ vua" },
  { value: "xiangqi", label: "Cờ tướng" },
  { value: "go", label: "Cờ vây" },
  { value: "gomoku", label: "Cờ caro" },
] as const;

export const TIME_FORMAT_LABELS: Record<string, string> = {
  bullet: "Bullet",
  blitz: "Blitz",
  rapid: "Rapid",
  standard: "Standard",
};

export function parseGomokuFen(fen: string): { row: number; col: number; color: "black" | "white" }[] {
  if (!fen || fen === ";1" || fen === ";2") return [];
  const stones: { row: number; col: number; color: "black" | "white" }[] = [];
  const parts = fen.split(";");
  if (!parts[0]) return [];
  for (const triple of parts[0].split(",")) {
    const nums = triple.split(".");
    if (nums.length === 3) {
      stones.push({ row: parseInt(nums[0]), col: parseInt(nums[1]), color: nums[2] === "1" ? "black" : "white" });
    }
  }
  return stones;
}
