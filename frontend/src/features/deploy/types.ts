/**
 * Tipos del dominio de despliegue.
 * Reflejan DeploymentConfig y las entidades del backend.
 */

// ── Plantillas ────────────────────────────────────────────────────────────────

export interface PlantillaOption {
  id: number                    // ID del curso Canvas (plantilla origen)
  nombre: string                // Nombre descriptivo para mostrar en la UI
  disenoInstruccional: string   // "Unidades" | "Escenarios"
  nivelFormacion: string        // "Pregrado" | "Posgrado"
  tipologia: string             // "Teórico" | "Práctica" | "Teórico-Práctico"
}

/**
 * Catálogo de plantillas institucionales del Politécnico Grancolombiano.
 *
 * IMPORTANTE: Los IDs aquí son PLACEHOLDERS temporales para Sprint 1.
 * En Sprint 2 estos datos se cargan dinámicamente desde el endpoint
 * GET /api/v1/templates, que lee el archivo templates_aulasmaster.xlsx.
 *
 * Para actualizar los IDs reales de Canvas, reemplaza los valores
 * numéricos de cada entrada con el ID del curso plantilla correspondiente
 * visible en la URL: poli.instructure.com/courses/{ID}
 */
export const PLANTILLAS_DISPONIBLES: PlantillaOption[] = [
  // ── Diseño: Unidades / Pregrado ──────────────────────────────────────
  {
    id: 63449,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Unidades — Pregrado — Teórico",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico",
  },
  {
    id: 69238,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Unidades — Pregrado — Práctica",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Pregrado",
    tipologia: "Práctica",
  },
  {
    id: 63801,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Unidades — Pregrado — Teórico-Práctico",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico-Práctico",
  },
  // ── Diseño: Unidades / Posgrado ──────────────────────────────────────
  {
    id: 69243,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Unidades — Posgrado — Teórico",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico",
  },
  {
    id: 69239,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Unidades — Posgrado — Teórico-Práctico",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico-Práctico",
  },
  // ── Diseño: Escenarios / Pregrado ────────────────────────────────────
  {
    id: 99007,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Pregrado — Teórico",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico",
  },
  {
    id: 99008,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Pregrado — Práctica",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Pregrado",
    tipologia: "Práctica",
  },
  {
    id: 99009,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Pregrado — Teórico-Práctico",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico-Práctico",
  },
  // ── Diseño: Escenarios / Posgrado ────────────────────────────────────
  {
    id: 99010,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Posgrado — Teórico",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico",
  },
  {
    id: 99011,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Posgrado — Práctica",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Posgrado",
    tipologia: "Práctica",
  },
  {
    id: 99012,   // ← REEMPLAZAR con ID real Canvas
    nombre: "Escenarios — Posgrado — Teórico-Práctico",
    disenoInstruccional: "Escenarios",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico-Práctico",
  },
]

// ── Opciones de curso ─────────────────────────────────────────────────────────

export type CourseOption = "new" | "existing"

// ── Estado del wizard de despliegue ──────────────────────────────────────────

export type DeployStep = 1 | 2 | 3

export interface UploadedFiles {
  zipFile: File
  excelFile?: File
}

export interface UploadResult {
  taskId: string
  filename: string
  totalFiles: number
  totalSizeMb: number
  foldersRenamed: string[]
  filesRenamed: string[]
  warnings: string[]
}

export interface TemplateSelection {
  plantillaId: number
  plantillaNombre: string
}

export interface CourseMetadata {
  courseOption: CourseOption
  courseName?: string
  courseId?: number
}

export interface DeployWizardState {
  step: DeployStep
  uploadResult: UploadResult | null
  templateSelection: TemplateSelection | null
  courseMetadata: CourseMetadata | null
}