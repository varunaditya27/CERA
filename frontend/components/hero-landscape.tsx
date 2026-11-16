'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * An illustrative, procedural fitness surface.
 * This visualization is NOT built from protein assay scores or experiment results.
 * Canvas is isolated from the research data pipeline and uses no network calls.
 */
export function HeroLandscape(){
  const ref=useRef<HTMLCanvasElement>(null);
  const [ready,setReady]=useState(false);

  useEffect(()=>{
    const canvas=ref.current;
    if(!canvas)return;
    const ctx=canvas.getContext('2d',{alpha:true});
    if(!ctx)return;

    let width=1,height=1,frame=0,raf=0,visible=true,active=true;
    let mouse={x:0,y:0},drift={x:0,y:0};
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const viewport=new IntersectionObserver(entries=>{
      visible=Boolean(entries[0]?.isIntersecting);
      if(visible&&active)start();
    },{rootMargin:'120px'});
    viewport.observe(canvas);

    const size=()=>{
      const bounds=canvas.getBoundingClientRect();
      width=Math.max(1,bounds.width);height=Math.max(1,bounds.height);
      const dpr=Math.min(2,window.devicePixelRatio||1);
      canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0);
      render();
    };
    const observer=new ResizeObserver(size);observer.observe(canvas);

    const landscape=(u:number,v:number)=>{
      const peakA=0.79*Math.exp(-((u-.21)**2/.20+(v+.16)**2/.18));
      const peakB=0.40*Math.exp(-((u+.55)**2/.14+(v-.47)**2/.24));
      const trough=0.23*Math.exp(-((u-.55)**2/.19+(v-.61)**2/.18));
      return peakA+peakB-trough+0.065*Math.sin(u*8.8)*Math.cos(v*7.7);
    };

    const project=(u:number,v:number,t:number)=>{
      const z=landscape(u,v);
      const spin=0.015*Math.sin(t*.25);
      return {
        x:width*(.52+u*.32+v*.16+spin+drift.x*.025),
        y:height*(.64+v*.29-u*.07-z*.34+drift.y*.02),
        z
      };
    };

    function render(){
      if(!ctx)return;
      ctx.clearRect(0,0,width,height);
      const t=frame/60;
      drift.x+=(mouse.x-drift.x)*.045;
      drift.y+=(mouse.y-drift.y)*.045;

      // Contour lattice: open sightlines, no filled fog or ornamental particles.
      const n=22,m=25;
      for(let j=0;j<=n;j++){
        const v=-1+j*2/n;
        ctx.beginPath();
        for(let i=0;i<=m;i++){
          const p=project(-1+i*2/m,v,t);
          if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);
        }
        const alpha=.13+.38*(j/n);
        ctx.strokeStyle=`rgba(175,201,189,${alpha})`;
        ctx.lineWidth=j%4===0?1.1:.72;
        ctx.stroke();
      }
      for(let i=0;i<=m;i++){
        const u=-1+i*2/m;
        ctx.beginPath();
        for(let j=0;j<=n;j++){
          const p=project(u,-1+j*2/n,t);
          if(j===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);
        }
        ctx.strokeStyle=`rgba(175,201,189,${.18+.18*(i/m)})`;
        ctx.lineWidth=.75;
        ctx.stroke();
      }

      const target=project(.21,-.16,t);
      const bloom=ctx.createRadialGradient(target.x,target.y,2,target.x,target.y,80);
      bloom.addColorStop(0,'rgba(222,150,108,.22)');
      bloom.addColorStop(1,'rgba(222,150,108,0)');
      ctx.fillStyle=bloom;
      ctx.beginPath();ctx.arc(target.x,target.y,80,0,Math.PI*2);ctx.fill();

      ctx.strokeStyle='rgba(222,150,108,.32)';
      ctx.lineWidth=1;
      ctx.setLineDash([4,7]);
      ctx.beginPath();ctx.moveTo(target.x,target.y);ctx.lineTo(target.x,height*.89);ctx.stroke();
      ctx.setLineDash([]);

      const pulse=reduced.matches?1:1+.04*Math.sin(t*1.65);
      ctx.strokeStyle='rgba(222,150,108,.7)';
      ctx.lineWidth=1.1;
      ctx.beginPath();ctx.arc(target.x,target.y,17*pulse,0,Math.PI*2);ctx.stroke();
      ctx.fillStyle='#DE966C';
      ctx.beginPath();ctx.arc(target.x,target.y,4.3,0,Math.PI*2);ctx.fill();
    }

    function tick(){raf=0;if(!active||!visible||reduced.matches)return;frame++;render();raf=requestAnimationFrame(tick);}
    function start(){if(raf||reduced.matches||!visible)return;raf=requestAnimationFrame(tick);}
    const move=(event:PointerEvent)=>{
      if(event.pointerType==='touch')return;
      const box=canvas.getBoundingClientRect();
      mouse={x:(event.clientX-box.left)/Math.max(box.width,1)*2-1,y:(event.clientY-box.top)/Math.max(box.height,1)*2-1};
      if(reduced.matches)render();
    };
    const leave=()=>{mouse={x:0,y:0};};
    const motionChange=()=>{cancelAnimationFrame(raf);raf=0;render();start();};
    canvas.addEventListener('pointermove',move,{passive:true});
    canvas.addEventListener('pointerleave',leave);
    reduced.addEventListener('change',motionChange);
    size();setReady(true);start();
    return()=>{active=false;cancelAnimationFrame(raf);observer.disconnect();viewport.disconnect();canvas.removeEventListener('pointermove',move);canvas.removeEventListener('pointerleave',leave);reduced.removeEventListener('change',motionChange);};
  },[]);

  return <div className={ready?'landscape-stage rendered':'landscape-stage'}>
    <div className="landscape-axis landscape-axis-y" aria-hidden="true"/>
    <svg className="landscape-static" viewBox="0 0 600 500" aria-hidden="true" focusable="false">
      {Array.from({length:14},(_,i)=> {
        const offset=i*20;
        return <path key={i} d={`M 45 ${340-offset*.32} C 150 ${300-offset} 240 ${390-offset*1.1} 310 ${185-offset*.25} S 485 ${180+offset*.48} 552 ${220+offset*.6}`} fill="none" stroke="var(--sea)" strokeOpacity={.13+i*.018} strokeWidth="1"/>;
      })}
      <circle cx="318" cy="169" r="10" fill="none" stroke="var(--copper)"/><circle cx="318" cy="169" r="3" fill="var(--copper)"/>
    </svg>
    <canvas className="landscape-canvas" ref={ref} aria-hidden="true"/>
    <div className="landscape-label"><span className="landscape-label-mark" aria-hidden="true"/>Conceptual fitness landscape</div>
  </div>;
}
