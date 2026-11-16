'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowUpRight, BookOpen, ChartNoAxesCombined, Database, FlaskConical, LayoutGrid } from 'lucide-react';
import { BrandMark } from './brand-mark';

const routes = [
  {href:'/', label:'Overview', number:'01', icon:LayoutGrid},
  {href:'/datasets', label:'Landscapes', number:'02', icon:Database},
  {href:'/experiments', label:'Experiments', number:'03', icon:ChartNoAxesCombined},
  {href:'/workflow', label:'Method', number:'04', icon:FlaskConical}
];

export function Navigation() {
  const pathname = usePathname();
  return <aside className="sidebar" aria-label="Workspace navigation">
    <Link className="brand" href="/" aria-label="CERA, return to overview">
      <span className="brand-emblem"><BrandMark size={34} light/></span>
      <span className="brand-type">CERA<small>COUNTEREXAMPLE RESEARCH</small></span>
    </Link>
    <div className="sidebar-section">
      <span className="sidebar-caption">RESEARCH ATLAS / 2026</span>
      <nav className="side-links" aria-label="Primary">
        {routes.map(({href,label,number,icon:Icon})=>{
          const active = href === '/' ? pathname === '/' : pathname.startsWith(href);
          return <Link key={href} href={href} className={active ? 'side-link is-current' : 'side-link'} aria-current={active?'page':undefined}>
            <span className="nav-number">{number}</span><Icon size={17} strokeWidth={1.65} aria-hidden="true"/><span>{label}</span>
          </Link>;
        })}
      </nav>
    </div>
    <div className="sidebar-bottom">
      <span className="sidebar-caption">WORKING STUDY</span>
      <p>Building a search that can question its own reward.</p>
      <a href="https://github.com/varunaditya27/CERA/tree/research/experiment-foundations" target="_blank" rel="noreferrer" className="sidebar-external">
        <BookOpen size={15} aria-hidden="true"/> Read the research <ArrowUpRight size={14} aria-hidden="true"/>
      </a>
      <span className="sidebar-edition">CERA · EVIDENCE FIRST</span>
    </div>
  </aside>;
}
