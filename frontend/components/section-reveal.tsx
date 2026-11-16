'use client';

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

/** Progressive enhancement: contents stay visible without JavaScript. */
export function SectionReveal({children,className=''}:{children:ReactNode;className?:string}){
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{
    const node=ref.current;
    if(!node||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    if(!('IntersectionObserver' in window))return;
    node.classList.add('can-reveal');
    const observer=new IntersectionObserver(entries=>{
      if(entries.some(entry=>entry.isIntersecting)){
        node.classList.add('is-revealed');observer.disconnect();
      }
    },{threshold:.1,rootMargin:'0px 0px 30px 0px'});
    observer.observe(node);
    return()=>observer.disconnect();
  },[]);
  return <div ref={ref} className={`section-reveal ${className}`}>{children}</div>;
}
