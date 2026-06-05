export type GameType = "chess" | "xiangqi" | "go";
export type TimeFormat = "bullet" | "blitz" | "rapid" | "standard";
export type TournamentFormat = "round_robin" | "swiss" | "knockout";
export type TournamentMode = "online" | "otb";
export type TournamentStatus = "draft" | "registration" | "in_progress" | "completed" | "cancelled";

export interface ITournament {
  id: string;
  name: string;
  description: string | null;
  game_type: GameType;
  time_format: TimeFormat;
  format: TournamentFormat;
  mode: TournamentMode;
  status: TournamentStatus;
  max_participants: number;
  start_date: string | null;
  end_date: string | null;
  spectator_delay: number;
  created_at: string;
  updated_at: string;
}

export interface ITournamentCreate {
  name: string;
  description?: string;
  game_type: GameType;
  time_format: TimeFormat;
  format: TournamentFormat;
  mode?: TournamentMode;
  max_participants: number;
  start_date?: string;
  end_date?: string;
  spectator_delay?: number;
}

export interface ITournamentUpdate {
  name?: string;
  description?: string;
  game_type?: GameType;
  time_format?: TimeFormat;
  format?: TournamentFormat;
  mode?: TournamentMode;
  max_participants?: number;
  start_date?: string;
  end_date?: string;
  status?: TournamentStatus;
  spectator_delay?: number;
}

export interface IRound {
  id: string;
  tournament_id: string;
  round_number: number;
  status: "pending" | "in_progress" | "completed";
  start_time: string | null;
  matches: IMatch[];
  created_at: string;
}

export interface IMatch {
  id: string;
  round_id: string;
  white_player_id: string;
  black_player_id: string;
  result: "white_win" | "black_win" | "draw" | "pending";
  played_at: string | null;
  created_at: string;
}
