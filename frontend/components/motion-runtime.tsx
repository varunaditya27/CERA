'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

/** Lenis uses GSAP's ticker. Native touch and reduced-motion requests are respected. */
export function MotionRuntime(){
  const pathname=usePathname();

  useEffect(()=>{
    let disposed=false;
    let request=0;
    let teardown=()=>{};
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const coarse=window.matchMedia('(pointer: coarse)');

    async function sync(){
      teardown();
      teardown=()=>{};
      const id=++request;
      if(reduced.matches||coarse.matches)return;

      const [{default:Lenis},{default:gsap},{ScrollTrigger}]=await Promise.all([
        import('lenis'),import('gsap'),import('gsap/ScrollTrigger')
      ]);
      if(disposed||id!==request)return;

      gsap.registerPlugin(ScrollTrigger);
      const lenis=new Lenis({
        duration:1.12,
        smoothWheel:true,
        syncTouch:false,
        autoRaf:false,
        anchors:true,
        wheelMultiplier:.92
      });
      const update=()=>ScrollTrigger.update();
      const tick=(time:number)=>lenis.raf(time*1000);
      lenis.on('scroll',update);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);
      ScrollTrigger.refresh();

      teardown=()=>{
        gsap.ticker.remove(tick);
        lenis.off('scroll',update);
        lenis.destroy();
      };
    }

    const onPreference=()=>void sync();
    reduced.addEventListener('change',onPreference);
    coarse.addEventListener('change',onPreference);
    void sync();

    return()=>{
      disposed=true;request++;
      reduced.removeEventListener('change',onPreference);
      coarse.removeEventListener('change',onPreference);
      teardown();
    };
  },[pathname]);
  return null;
}
