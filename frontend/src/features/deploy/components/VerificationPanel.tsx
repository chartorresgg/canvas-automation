/**
 * Panel de verificación post-despliegue.
 * HU-14: muestra el estado de páginas, actividades y front del curso.
 */

import { useEffect, useState } from "react"
import { verifyDeploy } from "@/services/api"
import type { VerificationReport, PageCheckResult } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Badge }  from "@/components/ui/badge"

interface VerificationPanelProps {
  courseId: number
}

export function VerificationPanel({ courseId }: VerificationPanelProps) {
  const [reporte,    setReporte]    = useState<VerificationReport | null>(null)
  const [cargando,   setCargando]   = useState(false)
  const [error,      setError]      = useState<string | null>(null)
  const [verificado, setVerificado] = useState(false)

  const verificar = async () => {
    setCargando(true)
    setError(null)
    try {
      const data = await verifyDeploy(courseId)
      setReporte(data)
      setVerificado(true)
    } catch (e: unknown) {
      setError("No se pudo verificar el aula. Inténtalo manualmente en Canvas.")
    } finally {
      setCargando(false)
    }
  }

  // Verificar automáticamente al montar
  useEffect(() => {
    verificar()
  }, [courseId])

  // ── Cargando ────────────────────────────────────────────────────────────
  if (cargando) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <div className="flex items-center gap-3">
          <span className="inline-block w-3 h-3 rounded-full bg-blue-400 animate-pulse" />
          <p className="text-sm text-slate-600">
            Verificando integridad del aula en Canvas…
          </p>
        </div>
      </div>
    )
  }

  // ── Error de conexión ────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 space-y-2">
        <p className="text-sm font-semibold text-red-700">
          Error de verificación
        </p>
        <p className="text-xs text-red-600">{error}</p>
        <Button size="sm" variant="outline" onClick={verificar}>
          Reintentar verificación
        </Button>
      </div>
    )
  }

  if (!reporte) return null

  const { resumen, paginas, resultado, course_url } = reporte

  const colorSemaforo = {
    success: "border-green-200 bg-green-50",
    warning: "border-yellow-200 bg-yellow-50",
    error:   "border-red-200 bg-red-50",
  }[resultado]

  const textoSemaforo = {
    success: { icon: "✓", label: "Aula verificada correctamente", color: "text-green-700" },
    warning: { icon: "⚠", label: "Aula con observaciones",        color: "text-yellow-700" },
    error:   { icon: "✗", label: "Se encontraron problemas",       color: "text-red-700"   },
  }[resultado]

  const badgeVariant: "default" | "secondary" | "destructive" = {
    success: "default",
    warning: "secondary",
    error:   "destructive",
  }[resultado] as "default" | "secondary" | "destructive"

  const paginasFaltantes = paginas.filter(p => !p.existe)

  return (
    <div className={`rounded-lg border p-4 space-y-4 ${colorSemaforo}`}>

      {/* ── Encabezado ───────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`font-bold text-lg ${textoSemaforo.color}`}>
            {textoSemaforo.icon}
          </span>
          <p className={`text-sm font-semibold ${textoSemaforo.color}`}>
            {textoSemaforo.label}
          </p>
        </div>
        <Badge variant={badgeVariant} className="text-xs">
          {resumen.porcentaje_paginas}% páginas OK
        </Badge>
      </div>

      {/* ── Métricas resumen ─────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-md bg-white/60 p-3 text-center border border-white/80">
          <p className="text-lg font-bold text-slate-800">
            {resumen.paginas_ok}
            <span className="text-sm font-normal text-slate-500">
              /{resumen.paginas_total}
            </span>
          </p>
          <p className="text-xs text-slate-500 mt-0.5">Páginas OK</p>
        </div>
        <div className="rounded-md bg-white/60 p-3 text-center border border-white/80">
          <p className="text-lg font-bold text-slate-800">
            {resumen.actividades_con_pdf}
            <span className="text-sm font-normal text-slate-500">
              /{resumen.actividades_total}
            </span>
          </p>
          <p className="text-xs text-slate-500 mt-0.5">PDFs vinculados</p>
        </div>
        <div className="rounded-md bg-white/60 p-3 text-center border border-white/80">
          <p className={`text-lg font-bold ${
            resumen.front_con_contenido ? "text-green-700" : "text-red-600"
          }`}>
            {resumen.front_con_contenido ? "✓" : "✗"}
          </p>
          <p className="text-xs text-slate-500 mt-0.5">Front del curso</p>
        </div>
      </div>

      {/* ── Lista de páginas ─────────────────────────────────────────── */}
      <div className="space-y-1">
        <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
          Páginas institucionales
        </p>
        <div className="grid grid-cols-2 gap-1">
          {paginas.map((p: PageCheckResult) => (
            <div
              key={p.slug}
              className="flex items-center gap-1.5 text-xs"
            >
              <span className={p.existe ? "text-green-600" : "text-red-500"}>
                {p.existe ? "✓" : "✗"}
              </span>
              <span className={
                p.existe ? "text-slate-700" : "text-red-600 font-medium"
              }>
                {p.titulo}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Páginas faltantes ─────────────────────────────────────────── */}
      {paginasFaltantes.length > 0 && (
        <div className="rounded-md bg-white/50 border border-yellow-200 p-3">
          <p className="text-xs font-semibold text-yellow-800 mb-1">
            Páginas no encontradas ({paginasFaltantes.length})
          </p>
          <p className="text-xs text-yellow-700">
            Es normal que algunas páginas complementarias no existan si
            el aula no tiene ese contenido. Verifica en Canvas si es esperado.
          </p>
        </div>
      )}

      {/* ── Acciones ──────────────────────────────────────────────────── */}
      <div className="flex gap-2 pt-1">
        
      <a
          href={course_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1"
        >
          <Button className="w-full" size="sm">
            Abrir en Canvas ↗
          </Button>
        </a>
        <Button
          size="sm"
          variant="outline"
          className="flex-1"
          onClick={verificar}
          disabled={cargando}
        >
          {cargando ? "Verificando…" : "Re-verificar"}
        </Button>
      </div>
    </div>
  )
}