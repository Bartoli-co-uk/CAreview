import { AppStateProvider, useAppState } from "./state/appState";
import { useHashRoute } from "./state/navigation";
import { Shell } from "./components/layout/Shell";
import { TopBar } from "./components/layout/TopBar";
import { SignIn } from "./pages/SignIn";
import { Overview } from "./pages/Overview";
import { Recommendations } from "./pages/Recommendations";
import { Policies } from "./pages/Policies";
import { PolicyExplorer } from "./pages/PolicyExplorer";
import { Insights } from "./pages/Insights";
import { Reports } from "./pages/Reports";
import { AuditLog } from "./pages/AuditLog";
import { Settings } from "./pages/Settings";
import { About } from "./pages/About";
import type { Page } from "./state/navigation";

const PAGE_META: Record<Page, { title: string; subtitle: string }> = {
  overview: { title: "Overview", subtitle: "Summary of your Conditional Access environment and recommendations." },
  recommendations: { title: "Recommendations", subtitle: "Every finding from the current analysis, in priority order." },
  policies: { title: "Policies", subtitle: "All Conditional Access policies in this tenant." },
  explorer: { title: "Policy Explorer", subtitle: "Search and filter policies by state, control, and target." },
  insights: { title: "Insights", subtitle: "Additional breakdowns derived from your current data." },
  reports: { title: "Reports", subtitle: "Exportable reports." },
  "audit-log": { title: "Audit Log", subtitle: "A record of tenant activity." },
  settings: { title: "Settings", subtitle: "Session and local session controls." },
  about: { title: "About", subtitle: "What CAreview is and how to read its output." },
};

function PageBody({ page, onNavigate }: { page: Page; onNavigate: (page: Page) => void }) {
  switch (page) {
    case "overview":
      return <Overview onNavigate={onNavigate} />;
    case "recommendations":
      return <Recommendations />;
    case "policies":
      return <Policies />;
    case "explorer":
      return <PolicyExplorer />;
    case "insights":
      return <Insights />;
    case "reports":
      return <Reports />;
    case "audit-log":
      return <AuditLog />;
    case "settings":
      return <Settings />;
    case "about":
      return <About />;
  }
}

function Dashboard() {
  const { mode, lastRefreshed } = useAppState();
  const [page, navigate] = useHashRoute();

  if (mode === "signedOut") {
    return <SignIn />;
  }

  const meta = PAGE_META[page];

  return (
    <Shell page={page} onNavigate={navigate}>
      <TopBar title={meta.title} subtitle={meta.subtitle} lastRefreshed={lastRefreshed} />
      <PageBody page={page} onNavigate={navigate} />
    </Shell>
  );
}

export default function App() {
  return (
    <AppStateProvider>
      <Dashboard />
    </AppStateProvider>
  );
}
