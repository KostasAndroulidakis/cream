// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Wallet types
export type WalletType = 'bank' | 'cash' | 'digital' | 'stash';

export interface Wallet {
  id: number;
  name: string;
  type: WalletType;
  currency: string;
  initial_balance: string;
  balance: string;
  created_at: string;
}

export interface WalletCreate {
  name: string;
  type: WalletType;
  currency?: string;
  initial_balance?: string;
}

export interface WalletUpdate {
  name?: string;
  type?: WalletType;
  currency?: string;
}

// Category types
export type CategoryType = 'income' | 'expense';

export interface Category {
  id: number;
  name: string;
  type: CategoryType;
  parent_id: number | null;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  type: CategoryType;
  parent_id?: number | null;
}

export interface CategoryUpdate {
  name?: string;
  parent_id?: number | null;
}

// Transaction types
export interface Transaction {
  id: number;
  wallet_id: number;
  category_id: number;
  amount: string;
  description: string | null;
  occurred_at: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  wallet_id: number;
  category_id: number;
  amount: string;
  description?: string | null;
  occurred_at: string;
}

export interface TransactionUpdate {
  category_id?: number;
  amount?: string;
  description?: string | null;
  occurred_at?: string;
}

// Statistics types
export interface WalletBalance {
  wallet_id: number;
  wallet_name: string;
  balance: string;
}

export interface CategoryTotal {
  category_id: number;
  category_name: string;
  total: string;
}

export interface Statistics {
  total_balance: string;
  total_income: string;
  total_expenses: string;
  wallet_balances: WalletBalance[];
  spending_by_category: CategoryTotal[];
  income_by_category: CategoryTotal[];
}

// Report types
export interface ReportPeriod {
  start_date: string;
  end_date: string;
}

export interface ReportSummary {
  income: string;
  expenses: string;
  net_change: string;
  transaction_count: number;
}

export interface CategoryBreakdown {
  category_id: number;
  category_name: string;
  type: CategoryType;
  total: string;
  count: number;
}

export interface WalletBreakdown {
  wallet_id: number;
  wallet_name: string;
  income: string;
  expenses: string;
  net_change: string;
}

export interface Report {
  period: ReportPeriod;
  summary: ReportSummary;
  by_category: CategoryBreakdown[];
  by_wallet: WalletBreakdown[];
}

// Error types
export interface ApiError {
  detail: string | ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
}
