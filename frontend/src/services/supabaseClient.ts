/**
 * Supabase client singleton for frontend
 */
import { createClient, SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables. Check .env file.')
}

// Singleton pattern to prevent multiple client instances
let supabaseInstance: SupabaseClient | null = null

function getSupabaseClient(): SupabaseClient {
  if (!supabaseInstance) {
    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: false, // Disabled to prevent Navigator Lock conflict in OAuth flow
        flowType: 'implicit',
        storage: window.localStorage,
        storageKey: 'resolveai-auth',
        debug: false,
      }
    })
  }
  return supabaseInstance
}

export const supabase = getSupabaseClient()
