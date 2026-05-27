import { createClient } from '@/utils/supabase/server'
import { cookies } from 'next/headers'

export default async function Page() {
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)

  const { data: todos } = await supabase.from('todos').select()

  return (
    <div style={{
      fontFamily: 'system-ui, sans-serif',
      padding: '40px',
      backgroundColor: '#0f172a',
      color: '#f8fafc',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        background: 'rgba(30, 41, 59, 0.7)',
        padding: '30px',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.5)'
      }}>
        <h1 style={{ margin: '0 0 20px 0', fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', textAlign: 'center' }}>
          ⚽ Player AI Todo List
        </h1>
        
        {todos && todos.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {todos.map((todo) => (
              <li key={todo.id} style={{
                padding: '12px 16px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <span style={{ color: '#10b981' }}>✓</span>
                <span>{todo.name}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div style={{ textAlign: 'center', color: '#94a3b8', padding: '20px 0' }}>
            <p style={{ margin: '0 0 8px 0' }}>No tasks found in Supabase `todos` table.</p>
            <p style={{ fontSize: '14px', margin: 0, opacity: 0.8 }}>Verify your Supabase URL, Publishable Key, and ensure a `todos` table with a `name` column has entries!</p>
          </div>
        )}
      </div>
    </div>
  )
}
