export type NotificationType = "tournament_invite" | "match_result" | "game_invite" | "system";

export interface INotification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  created_at: string;
}

export interface IUnreadCount {
  count: number;
}
