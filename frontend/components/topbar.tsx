import Link from 'next/link';
export function Topbar({section}:{section:string}) {
  return <header className="topbar">
    <div className="breadcrumbs"><Link href="/">CERA</Link><span aria-hidden="true">/</span><strong>{section}</strong></div>
    <span className="topbar-context">Research in progress</span>
  </header>;
}
