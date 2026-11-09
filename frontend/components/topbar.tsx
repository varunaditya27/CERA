import Link from 'next/link';
export function Topbar({section}:{section:string}) { return <header className="topbar"><div className="breadcrumbs"><Link href="/">CERA</Link><span className="slash">/</span><strong>{section}</strong></div><span className="top-right">Protein fitness research</span></header> }
