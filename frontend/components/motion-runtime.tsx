'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

/**
 * A single clock for Lenis and GSAP. We deliberately keep native touch
 * scrolling and respect the user's reduced-motion preference.
 */
export function MotionRuntime(){
  const pathname=usePathname();

  useEffect(()=>{
    let disposed=false;
    let dispose=()=>{};
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const coarse=window.matchMedia('(pointer: coarse)');

    async function initialize(){
      if(reduced.matches||coarse.matches)return;
      const [{default:Lenis},{default:gsap},{ScrollTrigger}]=await Promise.all([
        import('lenis'),import('gsap'),import('gsap/ScrollTrigger')
      ]);
      if(disposed)return;

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

      dispose=()=>{
        gsap.ticker.remove(tick);
        lenis.off('scroll',update);
        lenis.destroy();
      };
    }

    void initialize();
    return()=>{disposed=true;dispose();};
  },[pathname]);
  return null;
}
