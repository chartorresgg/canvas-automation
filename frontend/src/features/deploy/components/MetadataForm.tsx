/**
 * Formulario de captura de metadatos del curso.
 * HU-02: Formulario de captura de Metadatos (Nombre, opción de curso).
 *
 * Responsabilidad: construir el CourseMetadata que el orquestador
 * necesita para crear o localizar el curso en Canvas.
 */

import { useState } from "react"
import type { CourseMetadata, CourseOption } from "../types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"

interface MetadataFormProps {
  onComplete: (metadata: CourseMetadata) => void
}

export function MetadataForm({ onComplete }: MetadataFormProps) {
  const [courseOption, setCourseOption] = useState<CourseOption>("new")
  const [courseName, setCourseName]     = useState("")
  const [courseId, setCourseId]         = useState("")
  const [errors, setErrors]             = useState<Record<string, string>>({})
  const [confirmed, setConfirmed]       = useState<CourseMetadata | null>(null)

  const validar = (): boolean => {
    const nuevosErrores: Record<string, string> = {}

    if (courseOption === "new") {
      if (!courseName.trim()) {
        nuevosErrores.courseName = "El nombre del curso es obligatorio"
      } else if (courseName.trim().length < 5) {
        nuevosErrores.courseName = "El nombre debe tener al menos 5 caracteres"
      } else if (courseName.trim().length > 255) {
        nuevosErrores.courseName = "El nombre no puede superar 255 caracteres"
      }
    } else {
      const idNum = parseInt(courseId)
      if (!courseId.trim()) {
        nuevosErrores.courseId = "El ID del curso es obligatorio"
      } else if (isNaN(idNum) || idNum <= 0) {
        nuevosErrores.courseId = "El ID debe ser un número entero positivo"
      }
    }

    setErrors(nuevosErrores)
    return Object.keys(nuevosErrores).length === 0
  }

  const handleSubmit = () => {
    if (!validar()) return

    const metadata: CourseMetadata =
      courseOption === "new"
        ? { courseOption: "new", courseName: courseName.trim() }
        : { courseOption: "existing", courseId: parseInt(courseId) }

    setConfirmed(metadata)
    onComplete(metadata)
  }

  const handleReset = () => {
    setConfirmed(null)
    setErrors({})
  }

  if (confirmed) {
    return (
      <div className="space-y-3">
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-semibold text-green-700 mb-2">
            Metadatos configurados
          </p>
          {confirmed.courseOption === "new" ? (
            <>
              <Badge className="mb-2">Curso nuevo</Badge>
              <p className="text-sm text-slate-800 font-medium">
                {confirmed.courseName}
              </p>
            </>
          ) : (
            <>
              <Badge variant="outline" className="mb-2">Curso existente</Badge>
              <p className="text-sm text-slate-800">
                ID Canvas: <span className="font-mono font-medium">{confirmed.courseId}</span>
              </p>
            </>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={handleReset}>
          Modificar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      {/* Selector de opción */}
      <div className="space-y-2">
        <Label className="text-sm font-medium">¿Qué deseas hacer?</Label>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => { setCourseOption("new"); setErrors({}) }}
            className={[
              "rounded-lg border p-3 text-left transition-colors",
              courseOption === "new"
                ? "border-blue-500 bg-blue-50"
                : "border-slate-200 hover:border-slate-300",
            ].join(" ")}
          >
            <p className={[
              "text-sm font-medium",
              courseOption === "new" ? "text-blue-700" : "text-slate-700",
            ].join(" ")}>
              Crear curso nuevo
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Duplica una plantilla Canvas
            </p>
          </button>

          <button
            onClick={() => { setCourseOption("existing"); setErrors({}) }}
            className={[
              "rounded-lg border p-3 text-left transition-colors",
              courseOption === "existing"
                ? "border-blue-500 bg-blue-50"
                : "border-slate-200 hover:border-slate-300",
            ].join(" ")}
          >
            <p className={[
              "text-sm font-medium",
              courseOption === "existing" ? "text-blue-700" : "text-slate-700",
            ].join(" ")}>
              Usar curso existente
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Solo sube el contenido
            </p>
          </button>
        </div>
      </div>

      {/* Campos según opción */}
      {courseOption === "new" ? (
        <div className="space-y-1.5">
          <Label htmlFor="courseName" className="text-sm font-medium">
            Nombre del curso
          </Label>
          <Input
            id="courseName"
            placeholder="Ej. Fundamentos de Programación 2025-2"
            value={courseName}
            onChange={e => {
              setCourseName(e.target.value)
              if (errors.courseName) setErrors({})
            }}
            className={errors.courseName ? "border-red-400" : ""}
          />
          {errors.courseName && (
            <p className="text-xs text-red-600">{errors.courseName}</p>
          )}
          <p className="text-xs text-slate-400">
            Este nombre aparecerá en Canvas LMS
          </p>
        </div>
      ) : (
        <div className="space-y-1.5">
          <Label htmlFor="courseId" className="text-sm font-medium">
            ID del curso en Canvas
          </Label>
          <Input
            id="courseId"
            type="number"
            placeholder="Ej. 12345"
            value={courseId}
            onChange={e => {
              setCourseId(e.target.value)
              if (errors.courseId) setErrors({})
            }}
            className={errors.courseId ? "border-red-400" : ""}
          />
          {errors.courseId && (
            <p className="text-xs text-red-600">{errors.courseId}</p>
          )}
          <p className="text-xs text-slate-400">
            Encuéntralo en la URL del curso: poli.instructure.com/courses/<strong>ID</strong>
          </p>
        </div>
      )}

      <Button className="w-full" onClick={handleSubmit}>
        Confirmar configuración
      </Button>
    </div>
  )
}