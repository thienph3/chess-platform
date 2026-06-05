export interface IUser {
  id: string;
  email: string;
  role: "admin" | "member";
  member_id: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ILoginRequest {
  email: string;
  password: string;
}

export interface IRegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface ITokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
