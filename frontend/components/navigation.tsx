'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { BrandLogo } from './brand-logo';
import { jumpToPageTop } from '../lib/scroll';

const links=[
 {href:'/walkthrough',label:'Walkthrough'},
 {href:'/workflow',label:'Method'},
 {href:'/experiments',label:'Results'},
 {href:'/datasets',label:'Datasets'},
 {href:'/system',label:'System'},
];

export function Navigation(){
 const pathname=usePathname();
 const home=pathname==='/';
 const [open,setOpen]=useState(false);
 const [scrolled,setScrolled]=useState(false);
 useEffect(()=>{setOpen(false)},[pathname]);
 useEffect(()=>{
  const onScroll=()=>setScrolled(window.scrollY>24);
  onScroll();
  window.addEventListener('scroll',onScroll,{passive:true});
  return()=>window.removeEventListener('scroll',onScroll);
 },[]);
 useEffect(()=>{
  if(!open)return;
  const escape=(e:KeyboardEvent)=>{if(e.key==='Escape')setOpen(false)};
  window.addEventListener('keydown',escape);
  return()=>window.removeEventListener('keydown',escape);
 },[open]);
 const light=home&&!scrolled&&!open;
 return <header className={['site-nav',home?'nav-home':'nav-interior',scrolled?'nav-scrolled':'',open?'nav-open':''].join(' ')}>
  <div className="nav-inner">
   <Link href="/" scroll={true} onClick={pathname==='/'?jumpToPageTop:undefined} className="site-brand" aria-label="CERA home"><BrandLogo light={light}/></Link>
   <nav className="nav-desktop" aria-label="Main navigation">
    {links.map(link=><Link key={link.href} href={link.href} scroll={true} onClick={pathname===link.href?jumpToPageTop:undefined} aria-current={pathname.startsWith(link.href)?'page':undefined}>{link.label}</Link>)}
   </nav>
   <a className="nav-repository" href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={15} aria-hidden="true"/></a>
   <button type="button" className="nav-menu-button" aria-expanded={open} aria-controls="mobile-navigation" aria-label={open?'Close navigation':'Open navigation'} onClick={()=>setOpen(v=>!v)}>
    {open?<X size={23}/>:<Menu size={23}/>}
   </button>
  </div>
  <nav id="mobile-navigation" className="nav-mobile" aria-label="Mobile navigation" inert={!open}>
   {[{href:'/',label:'Overview'},...links].map(link=><Link key={link.href} href={link.href} scroll={true} aria-current={pathname===link.href?'page':undefined} onClick={()=>{setOpen(false);if(pathname===link.href)jumpToPageTop()}}>{link.label}<ArrowUpRight size={16} aria-hidden="true"/></Link>)}
   <a href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={16}/></a>
  </nav>
 </header>;
}
