import { useState }        from "react"
import { DeployPage }      from "@/features/deploy/DeployPage"
import { AuditPage }       from "@/features/audit/AuditPage"
import { BenchmarkPage }   from "@/features/benchmark/BenchmarkPage"

type Vista = "deploy" | "audit" | "benchmark"

export default function App() {
  const [vista, setVista] = useState<Vista>("deploy")

  const navItems: { id: Vista; label: string }[] = [
    { id: "deploy",    label: "Desplegar"   },
    { id: "audit",     label: "Historial"   },
    { id: "benchmark", label: "Benchmark"   },
  ]

  return (
    <div>
      <nav className="fixed top-0 right-0 p-4 z-50 flex gap-2">
        {navItems.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setVista(id)}
            className={[
              "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
              vista === id
                ? "bg-blue-600 text-white"
                : "bg-white border border-slate-200 text-slate-600 hover:border-slate-300",
            ].join(" ")}
          >
            {label}
          </button>
        ))}
      </nav>

      {vista === "deploy"    && <DeployPage />}
      {vista === "audit"     && <AuditPage />}
      {vista === "benchmark" && <BenchmarkPage />}
    </div>
  )
}