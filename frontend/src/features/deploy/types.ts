/**
 * Tipos del dominio de despliegue.
 * Reflejan DeploymentConfig y las entidades del backend.
 */

// ── Plantillas ────────────────────────────────────────────────────────────────

export interface PlantillaOption {
    id: number
    nombre: string
    disenoInstruccional: string
    nivelFormacion: string
    tipologia: string
  }
  
  // Datos estáticos para Sprint 1.
  // En Sprint 2 estos vienen del endpoint GET /api/v1/templates
  export const PLANTILLAS_DISPONIBLES: PlantillaOption[] = [
    {
      id: 10001,
      nombre: "Aula Estándar Pregrado",
      disenoInstruccional: "DI Estándar",
      nivelFormacion: "Pregrado",
      tipologia: "Curso regular",
    },
    {
      id: 10002,
      nombre: "Aula Estándar Posgrado",
      disenoInstruccional: "DI Estándar",
      nivelFormacion: "Posgrado",
      tipologia: "Especialización",
    },
    {
      id: 10003,
      nombre: "Aula Electiva Pregrado",
      disenoInstruccional: "DI Estándar",
      nivelFormacion: "Pregrado",
      tipologia: "Electiva",
    },
    {
      id: 10004,
      nombre: "Aula Maestría",
      disenoInstruccional: "DI Investigativo",
      nivelFormacion: "Posgrado",
      tipologia: "Maestría",
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
  
  // Estado global del wizard — se eleva a DeployPage
  export interface DeployWizardState {
    step: DeployStep
    uploadResult: UploadResult | null
    templateSelection: TemplateSelection | null
    courseMetadata: CourseMetadata | null
  }