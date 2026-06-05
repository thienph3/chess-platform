export interface IGalleryImage {
  id: string;
  title: string | null;
  description: string | null;
  filename: string;
  url: string;
  tournament_id: string | null;
  uploaded_by: string | null;
  created_at: string;
}
