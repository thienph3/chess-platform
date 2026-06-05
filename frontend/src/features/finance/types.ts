export type TransactionType = "income" | "expense";

export type TransactionCategory =
  | "membership_fee"
  | "sponsorship"
  | "donation"
  | "other_income"
  | "venue"
  | "prize"
  | "equipment"
  | "food"
  | "other_expense";

export interface ITransaction {
  id: string;
  type: TransactionType;
  category: TransactionCategory;
  amount: number;
  date: string;
  description: string | null;
  member_id: string | null;
  tournament_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ITransactionCreate {
  type: TransactionType;
  category: TransactionCategory;
  amount: number;
  date: string;
  description?: string;
  member_id?: string;
  tournament_id?: string;
}

export interface ITransactionUpdate {
  type?: TransactionType;
  category?: TransactionCategory;
  amount?: number;
  date?: string;
  description?: string;
  member_id?: string;
  tournament_id?: string;
}

export interface IBalance {
  total_income: number;
  total_expense: number;
  balance: number;
  tournament_id: string | null;
}
