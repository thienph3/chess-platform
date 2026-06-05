export type GameRoomStatus = "waiting" | "playing" | "finished" | "aborted";

export interface IGameRoom {
  id: string;
  match_id: string | null;
  white_player_id: string;
  black_player_id: string | null;
  status: GameRoomStatus;
  game_type: string;
  time_control: number;
  increment: number;
  scheduled_start: string | null;
  fen: string | null;
  result: string | null;
  white_accuracy: number | null;
  black_accuracy: number | null;
  is_reviewed: boolean;
  created_at: string;
}

export interface IGameRoomCreate {
  game_type: string;
  time_control: number;
  increment?: number;
  black_player_id?: string;
}

export interface IMoveHistory {
  id: string;
  room_id: string;
  move_number: number;
  notation: string;
  fen_after: string | null;
  classification: string | null;
  eval_after: number | null;
  best_move: string | null;
  created_at: string;
}
