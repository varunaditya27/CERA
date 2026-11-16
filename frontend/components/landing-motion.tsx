'use client';

import { useEffect } from 'react';

/** GSAP timelines are scoped to the landing page and reverted on navigation. */
export function LandingMotion(){
  useEffect(()=>{
    let disposed=false;
    let cleanup=()=>{};
    async function initialize(){
      const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if(reduced)return;
      const [{default:gsap},{ScrollTrigger}]=await Promise.all([
        import('gsap'),import('gsap/ScrollTrigger')
      ]);
      if(disposed)return;
      gsap.registerPlugin(ScrollTrigger);

      const context=gsap.context(()=>{
        const entrance=gsap.timeline({defaults:{ease:'power3.out'}});
        entrance
          .from('.hero-line-inner',{yPercent:108,autoAlpha:0,duration:1.1,stagger:.15,clearProps:'all'},0)
          .from('.landing-hero-copy > p',{y:23,autoAlpha:0,duration:.78,clearProps:'all'},.42)
          .from('.hero-links',{y:19,autoAlpha:0,duration:.7,clearProps:'all'},.58)
          .from('.landscape-stage',{autoAlpha:0,scale:.96,duration:1.25,clearProps:'all'},.16)
          .from('.hero-bottom',{autoAlpha:0,duration:.8,clearProps:'all'},.8);

        gsap.to('.landscape-stage',{
          yPercent:12,
          ease:'none',
          scrollTrigger:{trigger:'.landing-hero',start:'top top',end:'bottom top',scrub:.8}
        });

        gsap.fromTo('.plot-fill',
          {scaleX:0},
          {scaleX:1,stagger:.12,duration:1.15,ease:'power3.out',transformOrigin:'left center',
           scrollTrigger:{trigger:'.evidence-plot',start:'top 82%',once:true}}
        );

        gsap.from('.process-item',{
          y:24,autoAlpha:0,stagger:.11,duration:.85,ease:'power3.out',
          scrollTrigger:{trigger:'.process-rail',start:'top 84%',once:true}
        });

        gsap.from('.landscape-entry',{
          y:18,autoAlpha:0,stagger:.075,duration:.65,ease:'power2.out',
          scrollTrigger:{trigger:'.landscapes-list',start:'top 82%',once:true}
        });
      });

      cleanup=()=>context.revert();
      ScrollTrigger.refresh();
    }
    void initialize();
    return()=>{disposed=true;cleanup();};
  },[]);
  return null;
}
