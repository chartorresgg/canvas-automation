/**
 * Pantalla de autenticación por token Canvas.
 * HU-16: Token de Canvas como contraseña de ingreso.
 */

import fondoLogin from "@/assets/wallpaper.webp"
import { useState } from "react"
import { useToken } from "@/context/TokenContext"
import { Button } from "@/components/ui/button"
import { Input }  from "@/components/ui/input"
import { Label }  from "@/components/ui/label"

export function LoginPage() {
  const { login }          = useToken()
  const [token,  setToken] = useState("")
  const [visible, setVisible] = useState(false)
  const [cargando, setCargando] = useState(false)
  const [error,  setError] = useState<string | null>(null)

  const handleLogin = async () => {
    if (!token.trim()) {
      setError("Ingresa tu token de Canvas antes de continuar.")
      return
    }
    setCargando(true)
    setError(null)
    try {
      await login(token.trim())
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error de conexión"
      setError(
        msg.includes("401")
          ? "Token inválido o sin permisos. Verifica que sea correcto."
          : "No fue posible conectar con Canvas. Verifica tu conexión."
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-slate-950 flex items-center justify-center px-4 overflow-hidden">

      {/* Capa 1 — Imagen de fondo */}
      <div
        className="absolute inset-0 z-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${fondoLogin})` }}
        aria-hidden="true"
      />

      {/* Capa 2 — Degradado diagonal con los tonos de marca (slate + blue) */}
      <div
        className="absolute inset-0 z-0 bg-gradient-to-br from-slate-950/5 via-slate-900/0 to-blue-950/5"
        aria-hidden="true"
      />

      {/* Capa 3 — Viñeta: oscurece los bordes y concentra la atención al centro */}
      <div
        className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_center,transparent_35%,rgba(2,6,23,0.55)_100%)]"
        aria-hidden="true"
      />

      {/* Tarjeta de acceso — z-10 la mantiene sobre las tres capas de fondo */}
      <div className="relative z-10 w-full max-w-sm bg-white rounded-2xl border border-slate-200 shadow-2xl shadow-slate-950/50 p-8 space-y-6">

        {/* Logo e identidad */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center mx-auto">
            <span className="text-white text-xl font-bold">C</span>
          </div>
          <h1 className="text-lg font-semibold text-slate-800">
            Automatización de Aulas Máster
          </h1>
          <p className="text-xs text-slate-400">
            Politécnico Grancolombiano
          </p>
        </div>

        {/* Campo de token */}
        <div className="space-y-2">
          <Label
            htmlFor="token"
            className="text-xs font-medium text-slate-700"
          >
            Token de Canvas
          </Label>
          <div className="relative">
            <Input
              id="token"
              type={visible ? "text" : "password"}
              value={token}
              onChange={e => setToken(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              placeholder="Ingrese su token de Canvas"
              className="pr-10 text-xs font-mono"
              disabled={cargando}
              autoComplete="off"
            />
            <button
              type="button"
              onClick={() => setVisible(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs"
            >
              {visible ? "Ocultar" : "Ver"}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
            {error}
          </p>
        )}

        {/* Botón */}
        <Button
          className="w-full"
          onClick={handleLogin}
          disabled={cargando || !token.trim()}
        >
          {cargando ? "Verificando token…" : "Ingresar"}
        </Button>
      </div>
    </div>
  )
}