export interface UserRow {
  username: string;
  password_hash: string;
  salt: string;
  email: string | null;
  reset_token: string | null;
  reset_token_expires_at: string | null;
  created_at: string;
}

export interface UserDataRow {
  username: string;
  data_key: string;
  data_value: string;
  updated_at: string;
}
