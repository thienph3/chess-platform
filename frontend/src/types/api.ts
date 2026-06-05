export interface IResponseEnvelope<T> {
  data: T | null;
  message: string;
  errors: unknown | null;
}

export interface IPaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  message: string;
  errors: unknown | null;
}
