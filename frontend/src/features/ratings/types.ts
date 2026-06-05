export type GameType = "chess" | "xiangqi" | "go" | "gomoku";
export type TimeFormat = "bullet" | "blitz" | "rapid" | "standard";

export interface ILeaderboardEntry {
  id: string;
  member_id: string;
  rating: number;
  games_played: number;
  wins: number;
  draws: number;
  losses: number;
}
