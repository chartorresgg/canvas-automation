/**
 * Página principal del flujo de despliegue.
 * Orquesta los tres pasos del wizard: carga → plantilla → metadatos.
 *
 * Responsabilidad: gestionar el estado global del wizard y coordinar
 * la transición entre pasos.
 */

import { useState } from "react"
import type { DeployWizardState, UploadResult, TemplateSelection, CourseMetadata } from "./types"
import { DropZone }         from "./components/DropZone"
import { TemplateSelector } from "./components/TemplateSelector"
import { MetadataForm }     from "./components/MetadataForm"
import { Button }           from "@/components/ui/button"
import { Badge }            from "@/components/ui/badge"

const PASOS = [
  { numero: 1, titulo: "Cargar archivos",    descripcion: "ZIP del aula y Excel del guion" },
  { numero: 2, titulo: "Seleccionar plantilla", descripcion: "Diseño instruccional y nivel" },
  { numero: 3, titulo: "Configurar curso",   descripcion: "Nombre y opción de despliegue" },
]

export function DeployPage() {
  const [state, setState] = useState<DeployWizardState>({
    step:             1,
    uploadResult:     null,
    templateSelection: null,
    courseMetadata:   null,
  })

  const handleUploadSuccess = (result: UploadResult) => {
    setState(prev => ({ ...prev, uploadResult: result, step: 2 }))
  }

  const handleTemplateSelect = (selection: TemplateSelection) => {
    setState(prev => ({ ...prev, templateSelection: selection, step: 3 }))
  }

  const handleMetadataComplete = (metadata: CourseMetadata) => {
    setState(prev => ({ ...prev, courseMetadata: metadata }))
  }

  const isReadyToDeploy =
    state.uploadResult &&
    state.templateSelection &&
    state.courseMetadata

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-2xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">C</span>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-800">
                Canvas LMS Automation
              </h1>
              <p className="text-xs text-slate-400">
                Politécnico Grancolombiano
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">
        {/* Indicador de pasos */}
        <div className="flex items-center gap-0 mb-8">
          {PASOS.map((paso, idx) => (
            <div key={paso.numero} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div className={[
                  "w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold",
                  "transition-colors",
                  state.step > paso.numero
                    ? "bg-green-500 text-white"
                    : state.step === paso.numero
                    ? "bg-blue-600 text-white"
                    : "bg-slate-200 text-slate-400",
                ].join(" ")}>
                  {state.step > paso.numero ? "✓" : paso.numero}
                </div>
                <p className={[
                  "text-xs font-medium mt-1.5 text-center",
                  state.step >= paso.numero ? "text-slate-700" : "text-slate-400",
                ].join(" ")}>
                  {paso.titulo}
                </p>
              </div>
              {idx < PASOS.length - 1 && (
                <div className={[
                  "h-0.5 flex-1 mb-5 transition-colors",
                  state.step > idx + 1 ? "bg-green-400" : "bg-slate-200",
                ].join(" ")} />
              )}
            </div>
          ))}
        </div>

        {/* Paso activo */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          {state.step === 1 && (
            <>
              <h2 className="text-base font-semibold text-slate-800 mb-1">
                Cargar archivos del aula
              </h2>
              <p className="text-sm text-slate-500 mb-5">
                Sube el ZIP con el contenido del aula virtual.
                El sistema validará y normalizará la estructura automáticamente.
              </p>
              <DropZone onUploadSuccess={handleUploadSuccess} />
            </>
          )}

          {state.step === 2 && (
            <>
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-base font-semibold text-slate-800">
                  Seleccionar plantilla base
                </h2>
                {state.uploadResult && (
                  <Badge variant="outline" className="text-xs">
                    {state.uploadResult.totalFiles} archivos listos
                  </Badge>
                )}
              </div>
              <p className="text-sm text-slate-500 mb-5">
                Elige el diseño instruccional y nivel para determinar
                la plantilla Canvas que se usará como base del aula.
              </p>
              <TemplateSelector onSelect={handleTemplateSelect} />
            </>
          )}

          {state.step === 3 && (
            <>
              <h2 className="text-base font-semibold text-slate-800 mb-1">
                Configurar el curso
              </h2>
              <p className="text-sm text-slate-500 mb-5">
                Indica si se crea un curso nuevo o se usa uno existente en Canvas.
              </p>
              <MetadataForm onComplete={handleMetadataComplete} />
            </>
          )}
        </div>

        {/* Resumen y botón de despliegue */}
        {isReadyToDeploy && (
          <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">
              Resumen del despliegue
            </h3>
            <div className="space-y-2 text-sm text-slate-600 mb-5">
              <div className="flex justify-between">
                <span className="text-slate-400">Archivo</span>
                <span className="font-medium">{state.uploadResult!.filename}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Archivos</span>
                <span className="font-medium">{state.uploadResult!.totalFiles}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Plantilla</span>
                <span className="font-medium">{state.templateSelection!.plantillaNombre}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Modo</span>
                <span className="font-medium">
                  {state.courseMetadata!.courseOption === "new"
                    ? `Nuevo: ${state.courseMetadata!.courseName}`
                    : `Existente ID: ${state.courseMetadata!.courseId}`}
                </span>
              </div>
            </div>

            <Button className="w-full" size="lg" disabled>
              Iniciar despliegue — disponible en Sprint 2
            </Button>
            <p className="text-xs text-center text-slate-400 mt-2">
              La integración con Canvas LMS se implementa en el siguiente sprint
            </p>
          </div>
        )}
      </main>
    </div>
  )
}