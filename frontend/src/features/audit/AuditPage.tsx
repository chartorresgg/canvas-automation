/**
 * Página de historial de despliegues.
 * HU-15: Reporte histórico de operación.
 */

import { useEffect, useState } from "react"
import { getAuditHistory, downloadAuditExcel } from "@/services/api"
import type { AuditEntryData, AuditListResponse } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Badge }  from "@/components/ui/badge"

export function AuditPage() {
  const [data,      setData]      = useState<AuditListResponse | null>(null)
  const [cargando,  setCargando]  = useState(true)
  const [error,     setError]     = useState<string | null>(null)
  const [filtro,    setFiltro]    = useState<string | undefined>(undefined)

  const cargar = async () => {
    setCargando(true)
    setError(null)
    try {
      const result = await getAuditHistory({ limite: 50, estado: filtro })
      setData(result)
    } catch {
      setError("No se pudo cargar el historial. Verifica que el backend está activo.")
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => { cargar() }, [filtro])

  const estadoBadge = (estado: AuditEntryData["estado"]) => {
    const map = {
      completed: { variant: "default"      as const, label: "Exitoso"   },
      failed:    { variant: "destructive"  as const, label: "Error"     },
      cancelled: { variant: "secondary"    as const, label: "Cancelado" },
    }
    return map[estado] ?? { variant: "secondary" as const, label: estado }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">C</span>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-800">
                Historial de despliegues
              </h1>
              <p className="text-xs text-slate-400">
                Politécnico Grancolombiano
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={downloadAuditExcel}
            className="gap-2"
          >
            ↓ Exportar Excel
          </Button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-6">

        {/* Filtros */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Filtrar:</span>
          {[
            { value: undefined,    label: "Todos"      },
            { value: "completed",  label: "✅ Exitosos"  },
            { value: "failed",     label: "❌ Errores"   },
            { value: "cancelled",  label: "⊘ Cancelados" },
          ].map(({ value, label }) => (
            <button
              key={label}
              onClick={() => setFiltro(value)}
              className={[
                "px-3 py-1 rounded-md text-xs border transition-colors",
                filtro === value
                  ? "border-blue-500 bg-blue-50 text-blue-700 font-medium"
                  : "border-slate-200 text-slate-600 hover:border-slate-300",
              ].join(" ")}
            >
              {label}
            </button>
          ))}
          {data && (
            <span className="ml-auto text-xs text-slate-400">
              {data.total} registro{data.total !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Estado de carga */}
        {cargando && (
          <div className="text-center py-12 text-slate-400 text-sm">
            Cargando historial…
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-700">{error}</p>
            <Button size="sm" variant="outline" onClick={cargar} className="mt-2">
              Reintentar
            </Button>
          </div>
        )}

        {/* Sin registros */}
        {!cargando && !error && data?.entradas.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <p className="text-4xl mb-3">📋</p>
            <p className="text-sm font-medium">Sin despliegues registrados</p>
            <p className="text-xs mt-1">
              Los despliegues aparecerán aquí automáticamente.
            </p>
          </div>
        )}

        {/* Tabla */}
        {!cargando && data && data.entradas.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                    Fecha
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                    Curso
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide hidden md:table-cell">
                    Modelo
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide hidden sm:table-cell">
                    Archivos
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide hidden sm:table-cell">
                    Duración
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.entradas.map((entrada) => {
                  const badge = estadoBadge(entrada.estado)
                  const fecha = new Date(entrada.iniciado_en)
                  return (
                    <tr
                      key={entrada.task_id}
                      className="hover:bg-slate-50 transition-colors"
                    >
                      <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                        <div>{fecha.toLocaleDateString("es-CO")}</div>
                        <div className="text-slate-400">
                          {fecha.toLocaleTimeString("es-CO", {
                            hour: "2-digit", minute: "2-digit"
                          })}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-800 text-xs leading-tight">
                          {entrada.course_name || "—"}
                        </div>
                        {entrada.course_id && (
                          
                          <a
                            href={`https://poli.instructure.com/courses/${entrada.course_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-500 text-xs hover:underline"
                          >
                            ID {entrada.course_id} ↗
                          </a>
                        )}
                        {entrada.error_detalle && (
                          <p className="text-xs text-red-500 mt-0.5 font-mono truncate max-w-xs">
                            {entrada.error_detalle}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <span className="text-xs text-slate-500">
                          {entrada.modelo_instruccional || "—"}
                        </span>
                        <br />
                        <span className="text-xs text-slate-400">
                          {entrada.nivel_formacion}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center hidden sm:table-cell">
                        <span className="text-xs font-mono text-slate-600">
                          {entrada.archivos_subidos}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center hidden sm:table-cell">
                        <span className="text-xs font-mono text-slate-600">
                          {entrada.duracion_display}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={badge.variant} className="text-xs">
                          {badge.label}
                        </Badge>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}