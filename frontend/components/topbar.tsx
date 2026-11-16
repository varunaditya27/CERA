import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

export function Topbar({section,eyebrow}:{section:string;eyebrow?:string}) {
  return <header className="topbar">
    <div className="breadcrumbs"><Link href="/">CERA</Link><span aria-hidden="true">/</span><strong>{section}</strong></div>
    <div className="topbar-right"><span className="topbar-signal" aria-hidden="true"/><span>{eyebrow || 'RESEARCH / IN DEVELOPMENT'}</span>
      <a href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer" aria-label="Open CERA repository in a new tab"><ArrowUpRight size={17}/></a>
    </div>
  </header>;
}
