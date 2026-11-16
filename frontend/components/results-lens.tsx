'use client';

import { useState } from 'react';
import { RESULTS, fitness } from '../lib/research';

const methods=RESULTS.filter(m=>['genetic','random','greedy','fixed','repair','gemini_repair'].includes(m.id));

export function ResultsLens(){
 const [left,setLeft]=useState('genetic');
 const [right,setRight]=useState('fixed');
 const a=methods.find(x=>x.id===left)!;
 const b=methods.find(x=>x.id===right)!;
 const maximum=Math.max(...methods.map(x=>x.median));
 const same=Math.abs(a.median-b.median)<1e-10;
 const stops=a.result==='stopped'||b.result==='stopped';

 return <section className="result-lens" aria-labelledby="result-lens-title">
  <div className="result-lens-head"><div><h2 id="result-lens-title">Compare two methods</h2><p>Median best observed fitness after each method stopped.</p></div><span>10 matched seeds</span></div>
  <div className="result-lens-grid">
   {[{selected:left,set:setLeft,method:a},{selected:right,set:setRight,method:b}].map((item,i)=><div className="result-lens-column" key={i}>
    <label htmlFor={`compare-method-${i}`}>Method {i===0?'A':'B'}</label>
    <select id={`compare-method-${i}`} value={item.selected} onChange={e=>item.set(e.target.value)}>
     {methods.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}
    </select>
    <div className="result-lens-value">{fitness(item.method.median)}</div>
    <div className="result-lens-track"><span style={{width:`${item.method.median/maximum*100}%`}}/></div>
    <div className="result-lens-meta"><span>New measurements</span><strong>{item.method.measurements}</strong></div>
    <div className="result-lens-meta"><span>Stop</span><strong>{item.method.result==='stopped'?'Early':'Budget used'}</strong></div>
   </div>)}
  </div>
  <p className="result-lens-note">{same
    ? 'Both methods finished with the same median best score. This does not make their behavior equivalent.'
    : `Difference in median best fitness: ${Math.abs(a.median-b.median).toFixed(5)}. Higher is better on this dataset.`}
   {stops?' An early stop is not a demonstrated efficiency gain.':''}
  </p>
 </section>;
}
