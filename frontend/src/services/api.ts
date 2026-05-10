/**
 * Cliente HTTP centralizado para la Canvas LMS Automation API.
 * Toda llamada REST del frontend pasa por aquí.
 */

import axios from "axios"

export const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  timeout: 120_000,
})

// ── Tipos de respuesta del backend ───────────────────────────────────────────

export interface UploadResponse {
  task_id:         string
  filename:        string
  total_files:     number
  total_size_mb:   number
  folders_renamed: string[]
  files_renamed:   string[]
  warnings:        string[]
  message:         string
}

export interface DeployStartResponse {
  task_id:    string
  stream_url: string
  message:    string
}

export interface ProgressEventData {
  step:        number
  total_steps: number
  message:     string
  percentage:  number
  status:      "pending" | "running" | "completed" | "failed" | "cancelled"
  detail:      string | null
  course_id:   number | null
  error:       string | null
}

export interface HealthResponse {
  status:  string
  service: string
  version: string
}

// ── Funciones de API ─────────────────────────────────────────────────────────

/**
 * Sube el ZIP (y opcionalmente el Excel) al endpoint de validación previa.
 * No inicia el despliegue — solo valida y normaliza el ZIP.
 */
export async function uploadZip(
  zipFile:    File,
  excelFile?: File,
): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append("zip_file", zipFile)
  if (excelFile) {
    formData.append("excel_file", excelFile)
  }
  const response = await apiClient.post<UploadResponse>(
    "/deploy/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  )
  return response.data
}

/**
 * Inicia el despliegue completo del aula virtual.
 *
 * Envía el ZIP, el Excel opcional y todos los metadatos al backend.
 * El backend retorna 202 Accepted inmediatamente con el task_id.
 * El progreso se monitorea con openDeployStream().
 */
export async function startDeploy(params: {
  zipFile:              File
  excelFile?:           File
  courseOption:         "new" | "existing"
  courseName?:          string
  courseId?:            number
  templateId:           number
  modeloInstruccional:  string
  nivelFormacion:       string
}): Promise<DeployStartResponse> {
  const formData = new FormData()

  formData.append("zip_file", params.zipFile)
  if (params.excelFile) {
    formData.append("excel_file", params.excelFile)
  }

  formData.append("course_option",        params.courseOption)
  formData.append("template_id",          String(params.templateId))
  formData.append("modelo_instruccional", params.modeloInstruccional)
  formData.append("nivel_formacion",      params.nivelFormacion)

  if (params.courseOption === "new" && params.courseName) {
    formData.append("course_name", params.courseName)
  }
  if (params.courseOption === "existing" && params.courseId) {
    formData.append("course_id", String(params.courseId))
  }

  const response = await apiClient.post<DeployStartResponse>(
    "/deploy",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  )
  return response.data
}

/**
 * Abre una conexión SSE hacia el stream de progreso de un despliegue.
 *
 * Usa la API nativa EventSource del navegador.
 * El llamador es responsable de llamar source.close() cuando termine.
 *
 * @param taskId   - ID de la tarea retornado por startDeploy()
 * @param onEvent  - Callback invocado por cada ProgressEvent recibido
 * @param onError  - Callback invocado si la conexión SSE falla
 * @returns        EventSource que el llamador puede cerrar con .close()
 */
export function openDeployStream(
  taskId:  string,
  onEvent: (event: ProgressEventData) => void,
  onError: (err: Event) => void,
): EventSource {
  const url = `http://localhost:8000/api/v1/deploy/stream/${taskId}`
  const source = new EventSource(url)

  source.onmessage = (e: MessageEvent) => {
    try {
      const data = JSON.parse(e.data) as ProgressEventData
      onEvent(data)
    } catch {
      console.warn("SSE: evento no parseable:", e.data)
    }
  }

  source.onerror = (err: Event) => {
    onError(err)
    source.close()
  }

  return source
}

/**
 * Verifica que el servidor backend está operativo.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health")
  return response.data
}

/**
 * Solicita la cancelación de un despliegue en curso.
 *
 * El backend inyecta CancelledError en el asyncio.Task del orquestador.
 * El SSE stream emitirá un evento con status='cancelled' antes de cerrar.
 *
 * @param taskId - ID de la tarea a cancelar
 */
export async function cancelDeploy(taskId: string): Promise<void> {
  await apiClient.post(`/deploy/cancel/${taskId}`)
}

// ── Tipos de verificación ────────────────────────────────────────────────────

export interface PageCheckResult {
  slug:   string
  titulo: string
  existe: boolean
}

export interface VerificationResumen {
  paginas_ok:          number
  paginas_total:       number
  porcentaje_paginas:  number
  front_con_contenido: boolean
  actividades_con_pdf: number
  actividades_total:   number
}

export interface VerificationReport {
  course_id:   number
  course_name: string
  course_url:  string
  resultado:   "success" | "warning" | "error"
  resumen:     VerificationResumen
  paginas:     PageCheckResult[]
}

/**
 * Verifica la integridad del aula desplegada en Canvas.
 * Consulta páginas, actividades y contenido del front del curso.
 */
export async function verifyDeploy(
  courseId: number
): Promise<VerificationReport> {
  const response = await apiClient.get<VerificationReport>(
    `/deploy/verify/${courseId}`
  )
  return response.data
}