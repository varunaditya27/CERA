'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowUpRight, ChartNoAxesCombined, Database, FlaskConical, LayoutGrid } from 'lucide-react';
import { BrandMark } from './brand-mark';

const routes = [
  {href:'/',label:'Overview',icon:LayoutGrid},
  {href:'/datasets',label:'Datasets',icon:Database},
  {href:'/experiments',label:'Results',icon:ChartNoAxesCombined},
  {href:'/workflow',label:'Method',icon:FlaskConical}
];

export function Navigation() {
  const pathname=usePathname();
  return <aside className="sidebar" aria-label="Main navigation">
    <Link className="brand" href="/" aria-label="CERA home"><span className="brand-emblem"><BrandMark size={34} light/></span><span>CERA</span></Link>
    <nav className="side-links" aria-label="Pages">{routes.map(({href,label,icon:Icon})=>{
      const current=href==='/'?pathname==='/' : pathname.startsWith(href);
      return <Link key={href} className={current?'side-link is-current':'side-link'} href={href} aria-current={current?'page':undefined}>
        <Icon size={18} strokeWidth={1.7} aria-hidden="true"/>{label}
      </Link>;
    })}</nav>
    <a className="sidebar-external" href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">
      GitHub <ArrowUpRight size={15} aria-hidden="true"/>
    </a>
  </aside>;
}
