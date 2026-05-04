/**
 * Cliente HTTP centralizado para la Canvas LMS Automation API.
 * Toda llamada REST del frontend pasa por aquí.
 */

import axios from "axios"

export const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  timeout: 120_000, // 2 min — los ZIPs grandes tardan en procesarse
})

// ── Tipos que reflejan los schemas Pydantic del backend ──────────────────────

export interface UploadResponse {
  task_id: string
  filename: string
  total_files: number
  total_size_mb: number
  folders_renamed: string[]
  files_renamed: string[]
  warnings: string[]
  message: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}

// ── Funciones de API ─────────────────────────────────────────────────────────

/**
 * Sube el ZIP (y opcionalmente el Excel) al backend.
 * Retorna los metadatos del procesamiento y el task_id de sesión.
 */
export async function uploadZip(
  zipFile: File,
  excelFile?: File
): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append("zip_file", zipFile)
  if (excelFile) {
    formData.append("excel_file", excelFile)
  }

  const response = await apiClient.post<UploadResponse>(
    "/deploy/upload",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  )
  return response.data
}

/**
 * Verifica que el servidor backend está operativo.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health")
  return response.data
}