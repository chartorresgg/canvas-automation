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
  // ── Unidades / Posgrado ──────────────────────────────────
  {
    id: 69243,
    nombre: "Teórico — Posgrado / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico",
  },
  {
    id: 69239,
    nombre: "Teórico-Práctico — Posgrado / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Posgrado",
    tipologia: "Teórico-Práctico",
  },
  // ── Unidades / Pregrado ──────────────────────────────────
  {
    id: 63449,
    nombre: "Teórico — Pregrado / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico",
  },
  {
    id: 63801,
    nombre: "Teórico-Práctico — Pregrado / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico-Práctico",
  },
  // ── Unidades / Transversal ───────────────────────────────
  {
    id: 69238,
    nombre: "Práctica 16 semanas / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Transversal",
    tipologia: "Práctica (16 semanas)",
  },
  {
    id: 63888,
    nombre: "Práctica 8 semanas / Unidades",
    disenoInstruccional: "Unidades",
    nivelFormacion: "Transversal",
    tipologia: "Práctica (8 semanas)",
  },
  // ── Nuevo sistema / Pregrado ─────────────────────────────
  {
    id: 96005,
    nombre: "Teórico — Pregrado / Nuevo sistema",
    disenoInstruccional: "Nuevo sistema",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico",
  },
  {
    id: 96005,
    nombre: "Teórico-Práctico — Pregrado / Nuevo sistema",
    disenoInstruccional: "Nuevo sistema",
    nivelFormacion: "Pregrado",
    tipologia: "Teórico-Práctico",
  },
  {
    id: 96006,
    nombre: "Práctica — Pregrado / Nuevo sistema",
    disenoInstruccional: "Nuevo sistema",
    nivelFormacion: "Pregrado",
    tipologia: "Práctica",
  },
  // ── Nuevo sistema / Posgrado ─────────────────────────────
  {
    id: 96007,
    nombre: "Fundamentación — Posgrado / Nuevo sistema",
    disenoInstruccional: "Nuevo sistema",
    nivelFormacion: "Posgrado",
    tipologia: "Fundamentación",
  },
  {
    id: 96008,
    nombre: "Profundización — Posgrado / Nuevo sistema",
    disenoInstruccional: "Nuevo sistema",
    nivelFormacion: "Posgrado",
    tipologia: "Profundización",
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