import { useToken, TokenProvider } from "@/context/TokenContext"
import { LoginPage }   from "@/features/auth/LoginPage"
import { DeployPage }  from "@/features/deploy/DeployPage"
import { AuditPage }   from "@/features/audit/AuditPage"
import { BenchmarkPage } from "@/features/benchmark/BenchmarkPage"
import { useState } from "react"

type Vista = "deploy" | "audit" | "benchmark"

function AppContent() {
  const { isLoggedIn, userName, logout } = useToken()
  const [vista, setVista] = useState<Vista>("deploy")

  if (!isLoggedIn) return <LoginPage />

  const navItems: { id: Vista; label: string }[] = [
    { id: "deploy",    label: "Desplegar" },
    { id: "audit",     label: "Historial" },
    { id: "benchmark", label: "Benchmark" },
  ]

  return (
    <div>
      <nav className="fixed top-0 right-0 p-4 z-50 flex items-center gap-2">
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
        {/* Usuario activo + logout */}
        <div className="flex items-center gap-2 ml-2 pl-2 border-l border-slate-200">
          <span className="text-xs text-slate-500 hidden sm:block">
            {userName}
          </span>
          <button
            onClick={logout}
            className="px-2 py-1.5 rounded-md text-xs text-slate-500 hover:text-red-600 hover:bg-red-50 transition-colors"
          >
            Salir
          </button>
        </div>
      </nav>

      {vista === "deploy"    && <DeployPage />}
      {vista === "audit"     && <AuditPage />}
      {vista === "benchmark" && <BenchmarkPage />}
    </div>
  )
}

export default function App() {
  return (
    <TokenProvider>
      <AppContent />
    </TokenProvider>
  )
}