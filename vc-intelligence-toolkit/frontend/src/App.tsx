import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import CandidateDetail from "@/pages/CandidateDetail";
import Candidates from "@/pages/Candidates";
import Dashboard from "@/pages/Dashboard";
import Diligence from "@/pages/Diligence";
import Discover from "@/pages/Discover";
import History from "@/pages/History";
import RoutePage from "@/pages/Route";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/candidates", label: "Candidates" },
  { to: "/discover", label: "Discover" },
  { to: "/diligence", label: "Diligence" },
  { to: "/route", label: "Route" },
  { to: "/history", label: "History" },
];

function App() {
  return (
    <div className="min-h-screen bg-cream font-sans text-ink">
      <header className="px-6 pt-6">
        <nav className="mx-auto flex max-w-[1200px] flex-col gap-5 rounded-full border border-border bg-white px-5 py-4 shadow-sm md:flex-row md:items-center md:justify-between md:px-7">
          <NavLink
            to="/dashboard"
            className="font-sans text-sm font-medium uppercase tracking-[0.18em] text-ink"
          >
            VC Intelligence
          </NavLink>
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                      "rounded-full px-4 py-2 text-sm text-ink-secondary transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)]",
                      isActive ? "font-medium text-ink underline decoration-2 underline-offset-8" : "hover:text-ink",
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/candidates" element={<Candidates />} />
        <Route path="/candidates/:id" element={<CandidateDetail />} />
        <Route path="/discover" element={<Discover />} />
        <Route path="/diligence" element={<Diligence />} />
        <Route path="/route" element={<RoutePage />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </div>
  );
}

export default App;
