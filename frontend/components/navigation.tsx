'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Database,
  FlaskConical,
  Layers3,
  BookOpen,
  ChartNoAxesCombined,
  ScanSearch,
  PlayCircle,
  Target,
} from 'lucide-react';
const routes = [
  { href: '/', label: 'Overview', icon: Layers3 },
  { href: '/datasets', label: 'Datasets', icon: Database },
  { href: '/workflow', label: 'Method', icon: FlaskConical },
  { href: '/results', label: 'Results', icon: ChartNoAxesCombined },
  { href: '/predict', label: 'Predict', icon: ScanSearch },
  { href: '/experiments', label: 'Experiments', icon: PlayCircle },
  { href: '/goals', label: 'Goals', icon: Target },
];
export function Navigation() {
  const pathname = usePathname();
  return (
    <aside className="sidebar" aria-label="Workspace sidebar">
      <Link className="brand" href="/">
        <svg className="brand-mark" viewBox="0 0 64 64" aria-hidden="true">
          <rect width="64" height="64" rx="14" />
          <path d="M13 48 26 33 34 40 51 17" />
          <circle cx="34" cy="40" r="6" />
        </svg>
        <span>
          CERA<small>Research workspace</small>
        </span>
      </Link>
      <div className="side-content">
        <span className="side-label">Workspace</span>
        <nav aria-label="Workspace navigation">
          {routes.map(({ href, label, icon: Icon }) => {
            const active = href === '/' ? pathname === '/' : pathname.startsWith(href);
            return (
              <Link
                key={href}
                className={active ? 'nav-active' : undefined}
                aria-current={active ? 'page' : undefined}
                href={href}
              >
                <Icon size={17} aria-hidden="true" />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="sidebar-bottom">
        <span className="sidebar-icon">
          <BookOpen size={17} aria-hidden="true" />
        </span>
        <div>
          <strong>Project reference</strong>
          <p>Reward auditing for protein fitness optimization</p>
        </div>
      </div>
    </aside>
  );
}
