/**
 * Página de benchmark de procesamiento local.
 * HU-13: Pruebas de carga masiva y simulación de escenarios.
 */

import { useRef, useState } from "react"
import { runBenchmark }     from "@/services/api"
import type { BenchmarkReport, EtapaBenchmark } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Badge }  from "@/components/ui/badge"

// Referencia: tiempo manual por aula en minutos
const TIEMPO_MANUAL_MIN = 240

export function BenchmarkPage() {
  const [zipFile,   setZipFile]   = useState<File | null>(null)
  const [excelFile, setExcelFile] = useState<File | null>(null)
  const [reporte,   setReporte]   = useState<BenchmarkReport | null>(null)
  const [corriendo, setCorriendo] = useState(false)
  const [error,     setError]     = useState<string | null>(null)
  const zipRef   = useRef<HTMLInputElement>(null)
  const excelRef = useRef<HTMLInputElement>(null)

  const handleEjecutar = async () => {
    if (!zipFile) return
    setCorriendo(true)
    setError(null)
    setReporte(null)

    try {
      const resultado = await runBenchmark(
        zipFile,
        excelFile ?? undefined,
      )
      setReporte(resultado)
    } catch {
      setError(
        "Error al ejecutar el benchmark. Verifica que el backend está activo."
      )
    } finally {
      setCorriendo(false)
    }
  }

  const limpiar = () => {
    setZipFile(null)
    setExcelFile(null)
    setReporte(null)
    setError(null)
    if (zipRef.current)   zipRef.current.value   = ""
    if (excelRef.current) excelRef.current.value = ""
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">C</span>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-800">
                Benchmark de procesamiento
              </h1>
              <p className="text-xs text-slate-400">
                HU-13 — Medición de rendimiento local
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">

        {/* ── Panel de entrada ──────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-semibold text-slate-700">
            Archivos de prueba
          </h2>
          <p className="text-xs text-slate-500">
            El benchmark procesa el ZIP localmente sin conectarse a Canvas.
            Mide el tiempo real de cada etapa del pipeline de procesamiento.
          </p>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {/* ZIP */}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Archivo ZIP del aula <span className="text-red-500">*</span>
              </label>
              <input
                ref={zipRef}
                type="file"
                accept=".zip"
                onChange={e => setZipFile(e.target.files?.[0] ?? null)}
                className="w-full text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border file:border-slate-200 file:text-xs file:font-medium file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 cursor-pointer"
              />
              {zipFile && (
                <p className="text-xs text-slate-400 mt-1">
                  {zipFile.name} ({(zipFile.size / 1024 / 1024).toFixed(1)} MB)
                </p>
              )}
            </div>

            {/* Excel */}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Excel del Guion{" "}
                <span className="text-slate-400">(opcional)</span>
              </label>
              <input
                ref={excelRef}
                type="file"
                accept=".xlsx,.xls"
                onChange={e => setExcelFile(e.target.files?.[0] ?? null)}
                className="w-full text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border file:border-slate-200 file:text-xs file:font-medium file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 cursor-pointer"
              />
              {excelFile && (
                <p className="text-xs text-slate-400 mt-1">
                  {excelFile.name}
                </p>
              )}
            </div>
          </div>

          <div className="flex gap-3 pt-1">
            <Button
              className="flex-1"
              disabled={!zipFile || corriendo}
              onClick={handleEjecutar}
            >
              {corriendo
                ? "Ejecutando benchmark…"
                : "Ejecutar benchmark"}
            </Button>
            {(zipFile || reporte) && (
              <Button variant="outline" onClick={limpiar}>
                Limpiar
              </Button>
            )}
          </div>

          {error && (
            <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              {error}
            </p>
          )}
        </div>

        {/* ── Resultados ────────────────────────────────────────────── */}
        {reporte && (
          <>
            {/* Métricas generales */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                {
                  label: "Archivos",
                  value: reporte.total_archivos,
                  sub:   `${reporte.total_size_mb} MB`,
                },
                {
                  label: "SCORM detectados",
                  value: reporte.scorm_detectados,
                  sub:   reporte.scorm_detectados > 0
                    ? "Storyline OK"
                    : "Sin SCORM",
                },
                {
                  label: "Normalizados",
                  value: reporte.carpetas_normalizadas + reporte.pdfs_normalizados,
                  sub:   `${reporte.carpetas_normalizadas} carpetas · ${reporte.pdfs_normalizados} PDFs`,
                },
                {
                  label: "Tiempo total local",
                  value: reporte.total_procesamiento_display,
                  sub:   "Sin Canvas",
                  highlight: true,
                },
              ].map(({ label, value, sub, highlight }) => (
                <div
                  key={label}
                  className={[
                    "rounded-xl border p-4 text-center",
                    highlight
                      ? "border-blue-200 bg-blue-50"
                      : "border-slate-200 bg-white",
                  ].join(" ")}
                >
                  <p className={[
                    "text-xl font-bold",
                    highlight ? "text-blue-700" : "text-slate-800",
                  ].join(" ")}>
                    {value}
                  </p>
                  <p className="text-xs font-medium text-slate-600 mt-0.5">
                    {label}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">{sub}</p>
                </div>
              ))}
            </div>

            {/* Tiempos por etapa */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100">
                <h3 className="text-sm font-semibold text-slate-700">
                  Tiempos por etapa
                </h3>
              </div>
              <div className="divide-y divide-slate-100">
                {reporte.etapas.map((etapa: EtapaBenchmark) => {
                  const pct = reporte.total_procesamiento_ms > 0
                    ? (etapa.duracion_ms / reporte.total_procesamiento_ms) * 100
                    : 0
                  return (
                    <div key={etapa.nombre} className="px-5 py-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={
                            etapa.exitosa
                              ? "text-green-500 text-sm"
                              : "text-red-500 text-sm"
                          }>
                            {etapa.exitosa ? "✓" : "✗"}
                          </span>
                          <span className="text-sm font-medium text-slate-700">
                            {etapa.nombre}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-slate-400">
                            {pct.toFixed(1)}%
                          </span>
                          <Badge
                            variant={etapa.exitosa ? "secondary" : "destructive"}
                            className="font-mono text-xs"
                          >
                            {etapa.duracion_display}
                          </Badge>
                        </div>
                      </div>

                      {/* Barra de proporción */}
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={[
                            "h-full rounded-full transition-all",
                            etapa.exitosa ? "bg-blue-400" : "bg-red-400",
                          ].join(" ")}
                          style={{ width: `${Math.max(pct, 1)}%` }}
                        />
                      </div>

                      <p className="text-xs text-slate-500">{etapa.detalle}</p>
                      {etapa.error && (
                        <p className="text-xs text-red-500 font-mono">
                          {etapa.error}
                        </p>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Comparación con proceso manual */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <h3 className="text-sm font-semibold text-slate-700">
                Impacto vs. proceso manual
              </h3>
              <p className="text-xs text-slate-500">
                El tiempo manual incluye montaje, organización y publicación
                manual de recursos en Canvas (referencia: 240 min/aula).
                El tiempo automatizado es el registrado en el AuditLog
                para despliegues end-to-end reales.
              </p>

              <div className="space-y-3">
                {/* Manual */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-slate-600">
                      Proceso manual
                    </span>
                    <span className="text-slate-500">
                      ~{TIEMPO_MANUAL_MIN} min
                    </span>
                  </div>
                  <div className="h-4 bg-red-100 rounded-full overflow-hidden">
                    <div className="h-full w-full bg-red-400 rounded-full" />
                  </div>
                </div>

                {/* Procesamiento local */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-slate-600">
                      Procesamiento local (este benchmark)
                    </span>
                    <span className="text-blue-600 font-mono">
                      {reporte.total_procesamiento_display}
                    </span>
                  </div>
                  <div className="h-4 bg-blue-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-400 rounded-full"
                      style={{
                        width: `${Math.max(
                          (reporte.total_procesamiento_ms / 1000 / 60 / TIEMPO_MANUAL_MIN) * 100,
                          0.3
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <p className="text-xs text-slate-400 pt-1">
                  * El tiempo end-to-end real (incluyendo Canvas API) se
                  registra automáticamente en el Historial de despliegues.
                  El procesamiento local representa la porción controlada
                  por el sistema.
                </p>
              </div>
            </div>

            {/* Datos para el documento */}
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold text-slate-600 mb-2">
                Datos para el documento de práctica
              </p>
              <div className="font-mono text-xs text-slate-700 space-y-1">
                <p>Archivo:              {reporte.zip_filename}</p>
                <p>Total archivos:       {reporte.total_archivos} ({reporte.total_size_mb} MB)</p>
                <p>SCORM detectados:     {reporte.scorm_detectados}</p>
                <p>Tiempo procesamiento: {reporte.total_procesamiento_display}</p>
                {reporte.etapas.map(e => (
                  <p key={e.nombre}>
                    {`  ${e.nombre.padEnd(28)}: ${e.duracion_display}`}
                  </p>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}