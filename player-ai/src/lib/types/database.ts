export interface UserRow {
  username: string;
  password_hash: string;
  salt: string;
  created_at: string;
}

export interface UserDataRow {
  username: string;
  data_key: string;
  data_value: string;
  updated_at: string;
}
