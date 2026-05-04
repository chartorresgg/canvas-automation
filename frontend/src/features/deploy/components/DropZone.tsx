/**
 * Componente de carga de archivos con Drag & Drop.
 * HU-03: Interfaz visual de carga de archivos (ZIP y Excel).
 *
 * Responsabilidad: recibir archivos del analista, validarlos en el cliente
 * y llamar al endpoint de upload del backend.
 */

import { useCallback, useRef, useState } from "react"
import { uploadZip } from "@/services/api"
import type { UploadResponse } from "@/services/api"
import type { UploadedFiles, UploadResult } from "../types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent } from "@/components/ui/card"

interface DropZoneProps {
  onUploadSuccess: (result: UploadResult) => void
}

type UploadState = "idle" | "uploading" | "success" | "error"

export function DropZone({ onUploadSuccess }: DropZoneProps) {
  const [uploadState, setUploadState] = useState<UploadState>("idle")
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [files, setFiles] = useState<UploadedFiles | null>(null)
  const [error, setError]   = useState<string | null>(null)
  const [result, setResult] = useState<UploadResponse | null>(null)

  const zipInputRef   = useRef<HTMLInputElement>(null)
  const excelInputRef = useRef<HTMLInputElement>(null)

  // ── Validación cliente ───────────────────────────────────────────────────

  const validarArchivo = (file: File, tipo: "zip" | "excel"): string | null => {
    const MAX_MB = tipo === "zip" ? 500 : 50
    const MAX_BYTES = MAX_MB * 1024 * 1024

    if (tipo === "zip" && !file.name.toLowerCase().endsWith(".zip")) {
      return "El archivo debe tener extensión .zip"
    }
    if (tipo === "excel" && !file.name.match(/\.(xlsx|xls)$/i)) {
      return "El archivo Excel debe tener extensión .xlsx o .xls"
    }
    if (file.size > MAX_BYTES) {
      return `El archivo supera el límite de ${MAX_MB} MB`
    }
    return null
  }

  // ── Drag & Drop handlers ─────────────────────────────────────────────────

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const dropped = Array.from(e.dataTransfer.files)
    const zip   = dropped.find(f => f.name.toLowerCase().endsWith(".zip"))
    const excel = dropped.find(f => f.name.match(/\.(xlsx|xls)$/i))

    if (!zip) {
      setError("Arrastra al menos un archivo .zip")
      return
    }

    const errZip = validarArchivo(zip, "zip")
    if (errZip) { setError(errZip); return }

    if (excel) {
      const errExcel = validarArchivo(excel, "excel")
      if (errExcel) { setError(errExcel); return }
    }

    setError(null)
    setFiles({ zipFile: zip, excelFile: excel })
  }, [])

  // ── Selección por clic ───────────────────────────────────────────────────

  const handleZipSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const err = validarArchivo(file, "zip")
    if (err) { setError(err); return }
    setError(null)
    setFiles(prev => ({ ...prev, zipFile: file }))
  }

  const handleExcelSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const err = validarArchivo(file, "excel")
    if (err) { setError(err); return }
    setError(null)
    setFiles(prev => prev ? { ...prev, excelFile: file } : null)
  }

  // ── Upload ───────────────────────────────────────────────────────────────

  const handleUpload = async () => {
    if (!files?.zipFile) return

    setUploadState("uploading")
    setProgress(0)
    setError(null)

    // Simulación de progreso visual mientras el servidor procesa
    const intervalo = setInterval(() => {
      setProgress(prev => Math.min(prev + 8, 85))
    }, 400)

    try {
      const response = await uploadZip(files.zipFile, files.excelFile)

      clearInterval(intervalo)
      setProgress(100)
      setResult(response)
      setUploadState("success")

      onUploadSuccess({
        taskId:         response.task_id,
        filename:       response.filename,
        totalFiles:     response.total_files,
        totalSizeMb:    response.total_size_mb,
        foldersRenamed: response.folders_renamed,
        filesRenamed:   response.files_renamed,
        warnings:       response.warnings,
      })
    } catch (err: unknown) {
      clearInterval(intervalo)
      setUploadState("error")
      const mensaje =
        err instanceof Error ? err.message : "Error al procesar el archivo"
      setError(mensaje)
    }
  }

  const handleReset = () => {
    setFiles(null)
    setResult(null)
    setError(null)
    setProgress(0)
    setUploadState("idle")
    if (zipInputRef.current)   zipInputRef.current.value = ""
    if (excelInputRef.current) excelInputRef.current.value = ""
  }

  // ── Render ───────────────────────────────────────────────────────────────

  if (uploadState === "success" && result) {
    return (
      <div className="space-y-4">
        {/* Resultado exitoso */}
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-green-700 font-semibold text-sm">
              ZIP procesado correctamente
            </span>
            <Badge variant="secondary">{result.total_files} archivos</Badge>
            <Badge variant="secondary">{result.total_size_mb} MB</Badge>
          </div>
          <p className="text-xs text-green-600 mb-3">{result.filename}</p>

          {result.folders_renamed.length > 0 && (
            <div className="mb-2">
              <p className="text-xs font-medium text-slate-600 mb-1">
                Carpetas normalizadas ({result.folders_renamed.length})
              </p>
              <ul className="text-xs text-slate-500 space-y-0.5">
                {result.folders_renamed.map((r, i) => (
                  <li key={i} className="font-mono">→ {r}</li>
                ))}
              </ul>
            </div>
          )}

          {result.warnings.length > 0 && (
            <div className="mt-2 rounded bg-yellow-50 border border-yellow-200 p-2">
              <p className="text-xs font-medium text-yellow-700 mb-1">
                Advertencias ({result.warnings.length})
              </p>
              <ul className="text-xs text-yellow-600 space-y-0.5">
                {result.warnings.map((w, i) => (
                  <li key={i}>⚠ {w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <Button variant="outline" size="sm" onClick={handleReset}>
          Cargar otro archivo
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Zona principal de Drag & Drop */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => uploadState === "idle" && zipInputRef.current?.click()}
        className={[
          "relative flex flex-col items-center justify-center",
          "rounded-lg border-2 border-dashed p-10 text-center",
          "transition-colors cursor-pointer select-none",
          isDragging
            ? "border-blue-400 bg-blue-50"
            : "border-slate-300 hover:border-slate-400 hover:bg-slate-50",
          uploadState === "uploading" ? "pointer-events-none opacity-70" : "",
        ].join(" ")}
      >
        <div className="text-4xl mb-3">
          {isDragging ? "📂" : "📁"}
        </div>

        {!files?.zipFile ? (
          <>
            <p className="text-sm font-medium text-slate-700">
              Arrastra el archivo ZIP aquí
            </p>
            <p className="text-xs text-slate-400 mt-1">
              o haz clic para seleccionarlo
            </p>
            <p className="text-xs text-slate-400 mt-3">
              Máximo 500 MB · Solo archivos .zip
            </p>
          </>
        ) : (
          <div onClick={e => e.stopPropagation()}>
            <p className="text-sm font-medium text-slate-700">
              {files.zipFile.name}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {(files.zipFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

        <input
          ref={zipInputRef}
          type="file"
          accept=".zip"
          className="hidden"
          onChange={handleZipSelected}
        />
      </div>

      {/* Carga opcional del Excel de guion */}
      <Card className="border-dashed">
        <CardContent className="pt-4 pb-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-700">
                Excel del guion del curso{" "}
                <span className="text-slate-400 font-normal">(opcional)</span>
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                Actualiza los textos del front del curso
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => excelInputRef.current?.click()}
              disabled={uploadState === "uploading"}
            >
              {files?.excelFile ? "✓ " + files.excelFile.name : "Seleccionar .xlsx"}
            </Button>
          </div>
          <input
            ref={excelInputRef}
            type="file"
            accept=".xlsx,.xls"
            className="hidden"
            onChange={handleExcelSelected}
          />
        </CardContent>
      </Card>

      {/* Error de validación */}
      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-4 py-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Barra de progreso durante upload */}
      {uploadState === "uploading" && (
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <p className="text-xs text-slate-500 text-center">
            Procesando y normalizando archivos… {progress}%
          </p>
        </div>
      )}

      {/* Botón de acción */}
      <Button
        className="w-full"
        disabled={!files?.zipFile || uploadState === "uploading"}
        onClick={handleUpload}
      >
        {uploadState === "uploading"
          ? "Procesando…"
          : "Validar y continuar"}
      </Button>
    </div>
  )
}