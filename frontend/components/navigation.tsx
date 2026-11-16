'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { BrandMark } from './brand-mark';

const links=[
  {href:'/datasets',label:'Datasets'},
  {href:'/experiments',label:'Results'},
  {href:'/workflow',label:'Method'}
];

export function Navigation(){
  const pathname=usePathname();
  const home=pathname==='/';
  const [open,setOpen]=useState(false);
  const [scrolled,setScrolled]=useState(false);

  useEffect(()=>{setOpen(false);},[pathname]);
  useEffect(()=>{
    const onScroll=()=>setScrolled(window.scrollY>26);
    onScroll();
    window.addEventListener('scroll',onScroll,{passive:true});
    return ()=>window.removeEventListener('scroll',onScroll);
  },[]);
  useEffect(()=>{
    if(!open)return;
    const onKey=(event:KeyboardEvent)=>{if(event.key==='Escape')setOpen(false);};
    window.addEventListener('keydown',onKey);
    return()=>window.removeEventListener('keydown',onKey);
  },[open]);

  return <header className={['site-nav',home?'nav-home':'nav-interior',scrolled?'nav-scrolled':'',open?'nav-open':''].join(' ')}>
    <div className="nav-inner">
      <Link href="/" className="site-brand" aria-label="CERA home">
        <span className="brand-symbol"><BrandMark size={32} light={home&&!scrolled}/></span>
        <span className="brand-name">CERA</span>
      </Link>

      <nav className="nav-desktop" aria-label="Primary navigation">
        {links.map(link=><Link key={link.href} href={link.href} aria-current={pathname.startsWith(link.href)?'page':undefined}>{link.label}</Link>)}
      </nav>

      <a className="nav-repository" href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">
        GitHub <ArrowUpRight size={15} strokeWidth={1.8} aria-hidden="true"/>
      </a>

      <button type="button" className="nav-menu-button" aria-expanded={open} aria-controls="mobile-navigation" aria-label={open?'Close navigation':'Open navigation'} onClick={()=>setOpen(value=>!value)}>
        {open?<X size={23}/>:<Menu size={23}/>}
      </button>
    </div>

    <nav id="mobile-navigation" className="nav-mobile" aria-label="Mobile navigation" inert={!open}>
      {[{href:'/',label:'Overview'},...links].map(link=><Link key={link.href} href={link.href} aria-current={pathname===link.href?'page':undefined} onClick={()=>setOpen(false)}>{link.label}<ArrowUpRight size={17} aria-hidden="true"/></Link>)}
      <a href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={17}/></a>
    </nav>
  </header>;
}
