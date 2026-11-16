'use client';

import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, Expand, Minimize2, RotateCcw } from 'lucide-react';

type Step=0|1|2|3;

const scenes=[
 {step:'01',title:'Start with what we know.',explain:'Two proteins have been measured. Four others have only model predictions.',action:'Choose C'},
 {step:'02',title:'The model chooses C.',explain:'C has the highest predicted score. The next measurement is still hidden.',action:'Reveal the measurement'},
 {step:'03',title:'The prediction missed.',explain:'The model predicted 9. The measurement was 3. That mismatch is a counterexample, not a proven diagnosis.',action:'Continue the search'},
 {step:'04',title:'Use the new evidence.',explain:'In the second round, D is predicted at 7 and measured at 8. The best observed score is now 8. The two-measurement budget is spent.',action:'Start again'}
] as const;

const initial=[
 {id:'C',prediction:9},
 {id:'D',prediction:7},
 {id:'E',prediction:5},
 {id:'F',prediction:4},
] as const;
const second=[
 {id:'D',prediction:7},
 {id:'E',prediction:6},
 {id:'F',prediction:5},
] as const;

export function WalkthroughLab(){
 const [step,setStep]=useState<Step>(0);
 const [present,setPresent]=useState(false);
 useEffect(()=>{
  if(!present)return;
  const prior=document.body.style.overflow;
  document.body.style.overflow='hidden';
  const esc=(e:KeyboardEvent)=>{if(e.key==='Escape')setPresent(false)};
  window.addEventListener('keydown',esc);
  return()=>{document.body.style.overflow=prior;window.removeEventListener('keydown',esc)};
 },[present]);

 const scene=scenes[step];
 const candidates=step===3?second:initial;
 const select=step===1||step===2?'C':step===3?'D':undefined;
 const used=step===0?0:step===3?2:1;
 const next=()=>setStep(v=>v===3?0:(v+1) as Step);
 const back=()=>setStep(v=>Math.max(0,v-1) as Step);

 return <section className={present?'walkthrough-lab is-presenting':'walkthrough-lab'} aria-labelledby="lab-heading">
  <div className="lab-toolbar">
   <div className="lab-title"><span className="lab-live-dot" aria-hidden="true"/><span>Illustrative walkthrough</span></div>
   <button type="button" className="lab-present" onClick={()=>setPresent(v=>!v)} aria-label={present?'Exit presentation view':'Expand walkthrough for presentation'}>
    {present?<Minimize2 size={17}/>:<Expand size={17}/>}<span>{present?'Exit':'Present'}</span>
   </button>
  </div>
  <div className="lab-layout">
   <div className="lab-main">
    <div className="lab-step-index"><span>STEP {scene.step} / 04</span><span>MEASUREMENT BUDGET · {used}/2</span></div>
    <div className="lab-progress" aria-hidden="true">{scenes.map((s,i)=><span className={i<=step?'filled':''} key={s.step}/>)}</div>
    <div className="lab-headline" aria-live="polite" aria-atomic="true"><h2 id="lab-heading">{scene.title}</h2><p>{scene.explain}</p></div>

    <div className="lab-observations">
     <div className="lab-known">
      <span className="lab-small-label">Measured already</span>
      <div className="lab-known-scores"><span>Protein A <strong>4</strong></span><span>Protein B <strong>6</strong></span>
       {step>=2&&<span className="lab-new-known">Protein C <strong>3</strong></span>}
       {step===3&&<span className="lab-new-known">Protein D <strong>8</strong></span>}
      </div>
     </div>
     <div className="lab-candidates">
      <div className="lab-candidates-head"><span>Candidate</span><span>Predicted score</span><span>Measured score</span></div>
      {candidates.map(candidate=>{
       const observed=step>=2&&candidate.id==='C'?3:step===3&&candidate.id==='D'?8:null;
       const chosen=select===candidate.id;
       return <div key={candidate.id} className={chosen?'lab-candidate is-chosen':'lab-candidate'}>
        <div className="lab-candidate-id"><span className="lab-sequence-symbol">{candidate.id}</span>{chosen&&<span className="lab-selected-label">Selected</span>}</div>
        <strong>{candidate.prediction}</strong>
        <span className={observed!==null?'lab-observed':'lab-hidden'}>{observed!==null?observed:'?'}</span>
       </div>;
      })}
      {step>=2&&step!==3&&<div className="lab-error-note"><span>Predicted 9</span><span className="lab-difference">−6</span><span>Measured 3</span></div>}
      {step===3&&<div className="lab-error-note"><span>Predicted 7</span><span className="lab-difference">+1</span><span>Measured 8</span></div>}
     </div>
    </div>
   </div>
   <aside className="lab-sidebar">
    <div><span className="lab-small-label">What changes</span>
     <p>{step===0?'The model has two observations and a fixed measurement budget.':step===1?'C is selected using predictions, not its hidden score.':step===2?'C is now known to score 3. Its recorded prediction remains 9.':'The best measured score rises from 6 to 8. The run finishes.'}</p>
    </div>
    <div className="lab-metrics">
     <div><span>New measurements</span><strong>{used}<small> / 2</small></strong></div>
     <div><span>Best measured score</span><strong>{step===3?'8':'6'}</strong></div>
     <div><span>Recorded mismatch</span><strong>{step<2?'—':step===2?'6':'1'}</strong></div>
    </div>
    <p className="lab-warning">This example illustrates the information flow. It does not run the trained models or demonstrate a successful repair.</p>
   </aside>
  </div>
  <div className="lab-controls">
   <div className="lab-dots" role="group" aria-label="Jump to a step">{scenes.map((scene,i)=><button type="button" key={scene.step} onClick={()=>setStep(i as Step)} aria-current={step===i?'step':undefined} aria-label={`Go to step ${i+1}: ${scene.title}`}>{scene.step}</button>)}</div>
   <div className="lab-actions">
    <button type="button" className="lab-back" onClick={back} disabled={step===0}><ArrowLeft size={17} aria-hidden="true"/>Back</button>
    <button type="button" className="lab-next" onClick={next}>{scene.action}{step===3?<RotateCcw size={17} aria-hidden="true"/>:<ArrowRight size={17} aria-hidden="true"/>}</button>
   </div>
  </div>
 </section>;
}
