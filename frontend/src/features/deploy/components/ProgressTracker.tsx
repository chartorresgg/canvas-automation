/**
 * Componente de seguimiento del progreso de un despliegue en tiempo real.
 * HU-11: Barra de progreso con SSE + botón de cancelación.
 */

import { useEffect, useRef, useState } from "react"
import { openDeployStream, cancelDeploy } from "@/services/api"
import type { ProgressEventData } from "@/services/api"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { VerificationPanel } from "./VerificationPanel"

interface ProgressTrackerProps {
  taskId:      string
  onRetry:     () => void
  onNewDeploy: () => void
}

const ETIQUETAS_PASO: Record<number, string> = {
  0: "Iniciando proceso",
  1: "Configurando curso en Canvas",
  2: "Procesando archivos ZIP",
  3: "Subiendo archivos al aula",
  4: "Actualizando páginas HTML",
  5: "Despliegue completado",
}

export function ProgressTracker({
  taskId,
  onRetry,
  onNewDeploy,
}: ProgressTrackerProps) {
  const [eventos,          setEventos]          = useState<ProgressEventData[]>([])
  const [ultimo,           setUltimo]           = useState<ProgressEventData | null>(null)
  const [conectando,       setConectando]       = useState(true)
  const [errorConex,       setErrorConex]       = useState(false)
  const [cancelando,       setCancelando]       = useState(false)
  const [confirmCancel,    setConfirmCancel]    = useState(false)
  const sourceRef = useRef<EventSource | null>(null)
  const logRef    = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!taskId) return
    setConectando(true)
    setErrorConex(false)

    const source = openDeployStream(
      taskId,
      (event) => {
        setConectando(false)
        setUltimo(event)
        setEventos(prev => [...prev, event])
        if (
          event.status === "completed" ||
          event.status === "failed"    ||
          event.status === "cancelled"
        ) {
          source.close()
        }
      },
      (_err) => {
        setConectando(false)
        setEventos(prev => {
          if (prev.length === 0) setErrorConex(true)
          return prev
        })
      },
    )

    sourceRef.current = source
    return () => source.close()
  }, [taskId])

  // Auto-scroll del log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [eventos])

  const porcentaje    = ultimo?.percentage ?? 0
  const status        = ultimo?.status     ?? "pending"
  const courseId      = ultimo?.course_id  ?? null
  const errorMsg      = ultimo?.error      ?? null
  const estaTerminado = status === "completed" || status === "failed" || status === "cancelled"
  const esExitoso     = status === "completed"
  const esFallido     = status === "failed"
  const esCancelado   = status === "cancelled"
  const enProgreso    = !conectando && !estaTerminado

  // ── Handlers de cancelación ───────────────────────────────────────────────

  const handleCancelarClick = () => {
    setConfirmCancel(true)
  }

  const handleConfirmarCancelacion = async () => {
    setConfirmCancel(false)
    setCancelando(true)
    try {
      await cancelDeploy(taskId)
      // El evento SSE "cancelled" llegará automáticamente desde el backend
    } catch {
      // Si ya terminó antes de cancelar, ignorar el error
      setCancelando(false)
    }
  }

  const handleDenegarCancelacion = () => {
    setConfirmCancel(false)
  }

  // ── Error de conexión ─────────────────────────────────────────────────────

  if (errorConex) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <p className="font-semibold text-red-700 text-sm">
              Error de conexión con el servidor
            </p>
            <p className="text-xs text-red-600 mt-0.5">
              No fue posible conectar al stream de progreso.
              Verifica que el backend está corriendo.
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={onRetry}>
          Reintentar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-5">

      {/* ── Cabecera de estado ────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {conectando && (
            <>
              <span className="inline-block w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              <span className="text-sm text-slate-500">Conectando…</span>
            </>
          )}
          {enProgreso && !cancelando && (
            <>
              <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-sm font-medium text-slate-700">
                {ETIQUETAS_PASO[ultimo?.step ?? 0]}
              </span>
            </>
          )}
          {enProgreso && cancelando && (
            <>
              <span className="inline-block w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
              <span className="text-sm text-orange-600">Cancelando…</span>
            </>
          )}
          {esExitoso  && <span className="text-green-600 font-semibold text-sm">✓ Aula desplegada exitosamente</span>}
          {esFallido  && <span className="text-red-600 font-semibold text-sm">✗ El despliegue falló</span>}
          {esCancelado && <span className="text-orange-600 font-semibold text-sm">⊘ Despliegue cancelado</span>}
        </div>

        <Badge
          variant={
            esExitoso   ? "default"      :
            esFallido   ? "destructive"  :
            esCancelado ? "secondary"    :
            "secondary"
          }
          className="text-xs"
        >
          {Math.round(porcentaje)}%
        </Badge>
      </div>

      {/* ── Barra de progreso ─────────────────────────────────────────── */}
      <div className="space-y-1.5">
        <Progress
          value={porcentaje}
          className={[
            "h-3 transition-all duration-500",
            esFallido   ? "[&>div]:bg-red-500"    : "",
            esExitoso   ? "[&>div]:bg-green-500"  : "",
            esCancelado ? "[&>div]:bg-orange-400" : "",
          ].join(" ")}
        />
        <div className="flex justify-between px-0.5">
          {[1, 2, 3, 4, 5].map(paso => {
            const completado = (ultimo?.step ?? 0) >= paso && !esFallido && !esCancelado
            const actual     = (ultimo?.step ?? 0) === paso && enProgreso
            const fallido    = esFallido   && (ultimo?.step ?? 0) === paso
            const cancelado  = esCancelado && (ultimo?.step ?? 0) === paso
            return (
              <div key={paso} className="flex flex-col items-center gap-0.5">
                <div className={[
                  "w-2 h-2 rounded-full transition-colors",
                  completado || esExitoso ? "bg-green-500"           :
                  actual                  ? "bg-blue-500 animate-pulse" :
                  fallido                 ? "bg-red-500"             :
                  cancelado               ? "bg-orange-400"          :
                  "bg-slate-200",
                ].join(" ")} />
                <span className="text-[10px] text-slate-400 hidden sm:block">{paso}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Diálogo de confirmación de cancelación ────────────────────── */}
      {confirmCancel && (
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 space-y-3">
          <p className="text-sm font-semibold text-orange-700">
            ¿Cancelar el despliegue?
          </p>
          <p className="text-xs text-orange-600">
            El proceso se detendrá en la siguiente operación. Los archivos
            ya subidos a Canvas permanecerán en el curso.
          </p>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="destructive"
              className="bg-orange-500 hover:bg-orange-600"
              onClick={handleConfirmarCancelacion}
            >
              Sí, cancelar
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleDenegarCancelacion}
            >
              No, continuar
            </Button>
          </div>
        </div>
      )}

      {/* ── Resultado exitoso — enlace al curso ───────────────────────── */}
      {esExitoso && courseId && (
  <VerificationPanel courseId={courseId} />
)}

      {/* ── Error — detalle del fallo ──────────────────────────────────── */}
      {esFallido && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 space-y-2">
          <p className="text-sm font-semibold text-red-700">Detalle del error</p>
          {errorMsg && (
            <p className="text-xs font-mono text-red-600 break-all">{errorMsg}</p>
          )}
          <p className="text-xs text-slate-500">
            Paso donde falló: {ultimo?.step ?? "—"} de {ultimo?.total_steps ?? 5}
          </p>
        </div>
      )}

      {/* ── Cancelado — mensaje informativo ───────────────────────────── */}
      {esCancelado && (
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
          <p className="text-sm font-semibold text-orange-700">
            Despliegue cancelado
          </p>
          <p className="text-xs text-orange-600 mt-1">
            Los archivos subidos hasta el momento permanecen en Canvas.
            Puedes iniciar un nuevo despliegue cuando quieras.
          </p>
        </div>
      )}

      {/* ── Log de eventos ────────────────────────────────────────────── */}
      <div
        ref={logRef}
        className="rounded-md bg-slate-950 p-3 h-36 overflow-y-auto font-mono text-xs space-y-1 scroll-smooth"
      >
        {conectando && (
          <p className="text-slate-500">Conectando al stream SSE…</p>
        )}
        {eventos.map((ev, i) => (
          <p
            key={i}
            className={[
              "leading-relaxed",
              ev.status === "completed"  ? "text-green-400"  :
              ev.status === "failed"     ? "text-red-400"    :
              ev.status === "cancelled"  ? "text-orange-400" :
              ev.status === "running"    ? "text-blue-300"   :
              "text-slate-400",
            ].join(" ")}
          >
            <span className="text-slate-600 mr-1">
              [{String(ev.step).padStart(2, "0")}]
            </span>
            {ev.message}
            {ev.detail && (
              <span className="text-slate-500 ml-1">— {ev.detail}</span>
            )}
          </p>
        ))}
        {!conectando && !estaTerminado && (
          <p className="text-slate-600 animate-pulse">▋</p>
        )}
      </div>

      {/* ── Acciones ──────────────────────────────────────────────────── */}
      <div className="flex gap-3">
        {/* Botón cancelar — solo visible mientras el proceso está activo */}
        {enProgreso && !confirmCancel && (
          <Button
            variant="outline"
            className="flex-1 border-orange-300 text-orange-600 hover:bg-orange-50 hover:border-orange-400"
            disabled={cancelando}
            onClick={handleCancelarClick}
          >
            {cancelando ? "Cancelando…" : "Cancelar despliegue"}
          </Button>
        )}

        {/* Acciones post-proceso */}
        {estaTerminado && (
          <>
            <Button className="flex-1" onClick={onNewDeploy}>
              Nuevo despliegue
            </Button>
            {esFallido && (
              <Button variant="outline" className="flex-1" onClick={onRetry}>
                Reintentar
              </Button>
            )}
          </>
        )}
      </div>

    </div>
  )
}