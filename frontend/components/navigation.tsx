'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Database, FlaskConical, Layers3, BookOpen } from 'lucide-react';
const routes = [{href:'/',label:'Overview',icon:Layers3},{href:'/datasets',label:'Datasets',icon:Database},{href:'/workflow',label:'Method',icon:FlaskConical}];
export function Navigation() {
 const pathname = usePathname();
 return <aside className="sidebar" aria-label="Workspace sidebar"><Link className="brand" href="/"><span className="brand-mark" aria-hidden="true"><span/><span/><span/><span/></span><span>CERA<small>Research workspace</small></span></Link><div className="side-content"><span className="side-label">Workspace</span><nav aria-label="Workspace navigation">{routes.map(({href,label,icon:Icon})=>{const active=href==='/' ? pathname==='/' : pathname.startsWith(href);return <Link key={href} className={active?'nav-active':undefined} aria-current={active?'page':undefined} href={href}><Icon size={17} aria-hidden="true"/><span>{label}</span></Link>})}</nav></div><div className="sidebar-bottom"><span className="sidebar-icon"><BookOpen size={17} aria-hidden="true"/></span><div><strong>Project reference</strong><p>Reward auditing for protein fitness optimization</p></div></div></aside>
}
