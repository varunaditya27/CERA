'use client';

import { useState } from 'react';
import { ArrowRight, Check, Shield, Target } from 'lucide-react';

const stages=[
  {title:'Specify',short:'Define the reward',description:'Set permitted reward terms and hard constraints. The language model can propose weights, but code validates them.',signal:'Bounded specification',item:'Fixed mutation and budget limits'},
  {title:'Search',short:'Choose a batch',description:'Predict candidate fitness and select up to ten eligible variants. Save predictions before accessing measured scores.',signal:'Candidate ranking',item:'Only revealed measurements are known'},
  {title:'Audit',short:'Check the evidence',description:'Reveal the selected scores and record prediction misses, disagreement and other warnings. A warning is not a confirmed cause.',signal:'Observed measurements',item:'Original predictions remain in the record'},
  {title:'Repair',short:'Verify or retain',description:'Test only permitted weight changes against recorded evidence. Keep the old rule or stop if no change passes verification.',signal:'Constrained verification',item:'No successful repairs in current amylase runs'}
];

export function MethodExplorer(){
  const [active,setActive]=useState(0);
  const stage=stages[active];
  return <section className="method-explorer" aria-labelledby="explorer-heading">
    <div className="explorer-head"><h2 id="explorer-heading">The research loop</h2><span>Choose a stage</span></div>
    <div className="explorer-body">
      <div className="explorer-controls" role="group" aria-label="Research stages">
        {stages.map((item,i)=><button key={item.title} type="button" aria-pressed={active===i} onClick={()=>setActive(i)} className={active===i?'explorer-step selected':'explorer-step'}>
          <span className="explorer-number">{String(i+1).padStart(2,'0')}</span><span>{item.title}</span><ArrowRight size={17} aria-hidden="true"/>
        </button>)}
      </div>
      <div className="explorer-panel" aria-live="polite" aria-atomic="true">
        <div className="explorer-progress" aria-hidden="true"><span style={{transform:`scaleX(${(active+1)/4})`}}/></div>
        <div key={stage.title} className="explorer-content">
          <span className="explorer-step-label">{stage.signal}</span>
          <h3>{stage.short}</h3>
          <p>{stage.description}</p>
          <div className="explorer-diagram" aria-hidden="true">
            <div className="explorer-node"><Target size={23} strokeWidth={1.4}/><span>Model</span></div>
            <div className="explorer-connector"><span className={active>=1?'progressed':''}/></div>
            <div className={active===2?'explorer-node highlighted':'explorer-node'}><Shield size={23} strokeWidth={1.4}/><span>Evidence</span></div>
            <div className="explorer-connector"><span className={active>=3?'progressed':''}/></div>
            <div className={active===3?'explorer-node highlighted':'explorer-node'}><Check size={23} strokeWidth={1.4}/><span>Decision</span></div>
          </div>
          <div className="explorer-footnote">{stage.item}</div>
        </div>
      </div>
    </div>
  </section>;
}
