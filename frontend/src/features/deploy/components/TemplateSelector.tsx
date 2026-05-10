/**
 * Componente de selección de plantilla de diseño instruccional.
 * HU-01: Interfaz de selección de Plantilla base.
 *
 * Responsabilidad: filtrar las plantillas disponibles y capturar
 * la selección del analista para construir el DeploymentConfig.
 */

import { useState, useMemo } from "react"
import { PLANTILLAS_DISPONIBLES } from "../types"
import type { PlantillaOption, TemplateSelection } from "../types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"

interface TemplateSelectorProps {
  onSelect: (selection: TemplateSelection) => void
}

export function TemplateSelector({ onSelect }: TemplateSelectorProps) {
  const [disenoSeleccionado, setDisenoSeleccionado]   = useState<string>("")
  const [nivelSeleccionado, setNivelSeleccionado]     = useState<string>("")
  const [tipologiaSeleccionada, setTipologiaSeleccionada] = useState<string>("")
  const [plantillaFinal, setPlantillaFinal] = useState<PlantillaOption | null>(null)

  // Opciones derivadas de los filtros previos
  const disenos = useMemo(
    () => [...new Set(PLANTILLAS_DISPONIBLES.map(p => p.disenoInstruccional))],
    []
  )

  const niveles = useMemo(
    () =>
      [
        ...new Set(
          PLANTILLAS_DISPONIBLES
            .filter(p => !disenoSeleccionado || p.disenoInstruccional === disenoSeleccionado)
            .map(p => p.nivelFormacion)
        ),
      ],
    [disenoSeleccionado]
  )

  const tipologias = useMemo(
    () =>
      [
        ...new Set(
          PLANTILLAS_DISPONIBLES
            .filter(
              p =>
                (!disenoSeleccionado || p.disenoInstruccional === disenoSeleccionado) &&
                (!nivelSeleccionado  || p.nivelFormacion      === nivelSeleccionado)
            )
            .map(p => p.tipologia)
        ),
      ],
    [disenoSeleccionado, nivelSeleccionado]
  )

  const plantillaResultante = useMemo(
    () =>
      PLANTILLAS_DISPONIBLES.find(
        p =>
          p.disenoInstruccional === disenoSeleccionado &&
          p.nivelFormacion      === nivelSeleccionado  &&
          p.tipologia           === tipologiaSeleccionada
      ) ?? null,
    [disenoSeleccionado, nivelSeleccionado, tipologiaSeleccionada]
  )

  const handleConfirmar = () => {
    if (!plantillaResultante) return
    setPlantillaFinal(plantillaResultante)
    onSelect({
      plantillaId:          plantillaResultante.id,
      plantillaNombre:      plantillaResultante.nombre,
      disenoInstruccional:  plantillaResultante.disenoInstruccional,  // ← agregar
      nivelFormacion:       plantillaResultante.nivelFormacion, 
    })
  }

  const handleReset = () => {
    setDisenoSeleccionado("")
    setNivelSeleccionado("")
    setTipologiaSeleccionada("")
    setPlantillaFinal(null)
  }

  if (plantillaFinal) {
    return (
      <div className="space-y-3">
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-semibold text-green-700 mb-1">
            Plantilla seleccionada
          </p>
          <p className="text-sm text-slate-800 font-medium">
            {plantillaFinal.nombre}
          </p>
          <div className="flex gap-2 mt-2 flex-wrap">
            <Badge variant="outline">{plantillaFinal.disenoInstruccional}</Badge>
            <Badge variant="outline">{plantillaFinal.nivelFormacion}</Badge>
            <Badge variant="outline">{plantillaFinal.tipologia}</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            ID plantilla Canvas: {plantillaFinal.id}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleReset}>
          Cambiar selección
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      {/* Filtro 1: Diseño Instruccional */}
      <div className="space-y-2">
        <Label className="text-sm font-medium">Diseño instruccional</Label>
        <div className="flex flex-wrap gap-2">
          {disenos.map(d => (
            <button
              key={d}
              onClick={() => {
                setDisenoSeleccionado(d)
                setNivelSeleccionado("")
                setTipologiaSeleccionada("")
              }}
              className={[
                "px-3 py-1.5 rounded-md text-sm border transition-colors",
                disenoSeleccionado === d
                  ? "border-blue-500 bg-blue-50 text-blue-700 font-medium"
                  : "border-slate-200 hover:border-slate-300 text-slate-600",
              ].join(" ")}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {/* Filtro 2: Nivel de formación */}
      {disenoSeleccionado && (
        <div className="space-y-2">
          <Label className="text-sm font-medium">Nivel de formación</Label>
          <div className="flex flex-wrap gap-2">
            {niveles.map(n => (
              <button
                key={n}
                onClick={() => {
                  setNivelSeleccionado(n)
                  setTipologiaSeleccionada("")
                }}
                className={[
                  "px-3 py-1.5 rounded-md text-sm border transition-colors",
                  nivelSeleccionado === n
                    ? "border-blue-500 bg-blue-50 text-blue-700 font-medium"
                    : "border-slate-200 hover:border-slate-300 text-slate-600",
                ].join(" ")}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Filtro 3: Tipología */}
      {nivelSeleccionado && (
        <div className="space-y-2">
          <Label className="text-sm font-medium">Tipología</Label>
          <div className="flex flex-wrap gap-2">
            {tipologias.map(t => (
              <button
                key={t}
                onClick={() => setTipologiaSeleccionada(t)}
                className={[
                  "px-3 py-1.5 rounded-md text-sm border transition-colors",
                  tipologiaSeleccionada === t
                    ? "border-blue-500 bg-blue-50 text-blue-700 font-medium"
                    : "border-slate-200 hover:border-slate-300 text-slate-600",
                ].join(" ")}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Resultado del filtro */}
      {plantillaResultante && (
        <div className="rounded-md bg-slate-50 border border-slate-200 p-3">
          <p className="text-xs text-slate-500 mb-0.5">Plantilla encontrada</p>
          <p className="text-sm font-medium text-slate-800">
            {plantillaResultante.nombre}
          </p>
        </div>
      )}

      <Button
        className="w-full"
        disabled={!plantillaResultante}
        onClick={handleConfirmar}
      >
        Confirmar plantilla
      </Button>
    </div>
  )
}