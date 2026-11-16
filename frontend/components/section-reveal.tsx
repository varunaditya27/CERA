'use client';

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

/** Content is immediately readable without JavaScript or when motion is reduced. */
export function SectionReveal({children,className=''}:{children:ReactNode;className?:string}){
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{
    const element=ref.current;
    if(!element||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    let disposed=false;
    let cleanup=()=>{};
    async function initialize(){
      const [{default:gsap},{ScrollTrigger}]=await Promise.all([
        import('gsap'),import('gsap/ScrollTrigger')
      ]);
      if(disposed)return;
      gsap.registerPlugin(ScrollTrigger);
      const context=gsap.context(()=>{
        gsap.from(element,{
          autoAlpha:0,y:28,duration:.86,ease:'power3.out',
          scrollTrigger:{trigger:element,start:'top 89%',once:true}
        });
      });
      cleanup=()=>context.revert();
    }
    void initialize();
    return()=>{disposed=true;cleanup();};
  },[]);
  return <div ref={ref} className={`section-reveal ${className}`}>{children}</div>;
}
