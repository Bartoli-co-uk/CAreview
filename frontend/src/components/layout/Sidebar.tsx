import type { SVGProps } from "react";
import type { Page } from "../../state/navigation";
import { PAGES } from "../../state/navigation";
import {
  ShieldIcon,
  LightbulbIcon,
  DocumentIcon,
  SearchIcon,
  ChartIcon,
  BarChartIcon,
  ListIcon,
  GearIcon,
  InfoIcon,
} from "../icons";

type IconComponent = (props: SVGProps<SVGSVGElement>) => ReturnType<typeof ShieldIcon>;

const NAV_ITEMS: { page: Page; label: string; icon: IconComponent }[] = [
  { page: "overview", label: "Overview", icon: ShieldIcon },
  { page: "recommendations", label: "Recommendations", icon: LightbulbIcon },
  { page: "policies", label: "Policies", icon: DocumentIcon },
  { page: "explorer", label: "Policy Explorer", icon: SearchIcon },
  { page: "insights", label: "Insights", icon: ChartIcon },
  { page: "reports", label: "Reports", icon: BarChartIcon },
  { page: "audit-log", label: "Audit Log", icon: ListIcon },
  { page: "settings", label: "Settings", icon: GearIcon },
  { page: "about", label: "About", icon: InfoIcon },
];

interface SidebarProps {
  page: Page;
  onNavigate: (page: Page) => void;
}

export function Sidebar({ page, onNavigate }: SidebarProps) {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      <div className="sidebar-brand">
        <ShieldIcon className="sidebar-brand-icon" width={32} height={32} color="#fff" />
        <div>
          <h1>CAreview</h1>
          <p>Conditional Access overview</p>
        </div>
      </div>
      <ul className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <li key={item.page} className={item.page === page ? "active" : undefined}>
            <button type="button" onClick={() => onNavigate(item.page)} aria-current={item.page === page ? "page" : undefined}>
              <item.icon width={18} height={18} />
              {item.label}
            </button>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">CAreview runs locally. Your tenant data stays on this machine.</div>
    </nav>
  );
}

export { PAGES };
