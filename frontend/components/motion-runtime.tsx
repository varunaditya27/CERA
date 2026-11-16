'use client';

import { useEffect, useLayoutEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import { jumpToPageTop } from '../lib/scroll';

/** Lenis uses GSAP's ticker. Native touch and reduced-motion requests are respected. */
export function MotionRuntime(){
  const pathname=usePathname();
  const previousPath=useRef(pathname);
  const resetPending=useRef(false);

  // Reset before the new route is painted; don't interfere with same-page anchors.
  useLayoutEffect(()=>{
    if(previousPath.current===pathname)return;
    previousPath.current=pathname;
    resetPending.current=!window.location.hash;
    if(resetPending.current)jumpToPageTop();
  },[pathname]);

  useEffect(()=>{
    let disposed=false;
    let request=0;
    let teardown=()=>{};
    let lenisResetPending=resetPending.current;
    resetPending.current=false;
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const coarse=window.matchMedia('(pointer: coarse)');

    async function sync(){
      teardown();
      teardown=()=>{};
      const id=++request;
      const needsReset=lenisResetPending;
      lenisResetPending=false;
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
      // Lenis tracks scroll internally, so synchronize its state after route resets.
      if(needsReset)lenis.scrollTo(0,{immediate:true,force:true});
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
