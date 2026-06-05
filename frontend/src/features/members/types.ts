export interface IMember {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  skill_level: string | null;
  notes: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface IMemberCreate {
  full_name: string;
  email?: string;
  phone?: string;
  skill_level?: string;
  notes?: string;
}

export interface IMemberUpdate {
  full_name?: string;
  email?: string;
  phone?: string;
  skill_level?: string;
  notes?: string;
}
