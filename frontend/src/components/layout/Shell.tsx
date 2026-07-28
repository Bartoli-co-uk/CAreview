import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import type { Page } from "../../state/navigation";
import { useAppState } from "../../state/appState";

interface ShellProps {
  page: Page;
  onNavigate: (page: Page) => void;
  children: ReactNode;
}

export function Shell({ page, onNavigate, children }: ShellProps) {
  const { isSample, exitSample } = useAppState();
  return (
    <div className="app-shell">
      <Sidebar page={page} onNavigate={onNavigate} />
      <div className="main">
        {isSample && (
          <div className="sample-banner">
            <span>Sample data — this is not your tenant's data.</span>
            <button type="button" onClick={exitSample}>
              Exit sample
            </button>
          </div>
        )}
        <div className="page-content">{children}</div>
      </div>
    </div>
  );
}
