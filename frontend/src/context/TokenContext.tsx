/**
 * Contexto de autenticación por token Canvas.
 * El token nunca se persiste en disco — vive solo en memoria React.
 * HU-16: Token de Canvas como contraseña de ingreso.
 */

import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
  } from "react"
  import { login as apiLogin, logout as apiLogout } from "@/services/api"
  
  interface AuthState {
    sessionId:  string | null
    userName:   string | null
    userEmail:  string | null
    isLoggedIn: boolean
  }
  
  interface TokenContextValue extends AuthState {
    login:  (token: string) => Promise<void>
    logout: () => Promise<void>
  }
  
  const TokenContext = createContext<TokenContextValue | null>(null)
  
  export function TokenProvider({ children }: { children: ReactNode }) {
    const [auth, setAuth] = useState<AuthState>({
      sessionId:  null,
      userName:   null,
      userEmail:  null,
      isLoggedIn: false,
    })
  
    const login = useCallback(async (token: string) => {
      const response = await apiLogin(token)
      setAuth({
        sessionId:  response.session_id,
        userName:   response.user_name,
        userEmail:  response.user_email,
        isLoggedIn: true,
      })
    }, [])
  
    const logout = useCallback(async () => {
      if (auth.sessionId) {
        try {
          await apiLogout(auth.sessionId)
        } catch {
          // Si falla el logout en el servidor, igual limpiamos localmente
        }
      }
      setAuth({
        sessionId: null, userName: null,
        userEmail: null, isLoggedIn: false,
      })
    }, [auth.sessionId])
  
    return (
      <TokenContext.Provider value={{ ...auth, login, logout }}>
        {children}
      </TokenContext.Provider>
    )
  }
  
  export function useToken(): TokenContextValue {
    const ctx = useContext(TokenContext)
    if (!ctx) throw new Error("useToken debe usarse dentro de TokenProvider")
    return ctx
  }