import { createServerClient } from '@/lib/supabase/server';

export async function getUserData<T>(
  username: string,
  dataKey: string
): Promise<T | null> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('user_data')
      .select('data_value')
      .eq('username', username)
      .eq('data_key', dataKey)
      .single();
    if (error || !data) return null;
    return JSON.parse(data.data_value) as T;
  } catch {
    return null;
  }
}
