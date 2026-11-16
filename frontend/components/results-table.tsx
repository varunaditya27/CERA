'use client';

import { useState } from 'react';
import { RESULTS, fitness } from '../lib/research';

type Filter='all'|'baseline'|'repair';

export function ResultsTable(){
 const [filter,setFilter]=useState<Filter>('all');
 const filtered=RESULTS.filter(m=>filter==='all'||m.category===filter);
 return <section className="results-shell" aria-labelledby="comparison-title">
   <div className="results-toolbar"><h2 id="comparison-title">Method comparison</h2><div className="filter-tabs" role="group" aria-label="Filter methods">
     {([{id:'all',label:'All'},{id:'baseline',label:'Baselines'},{id:'repair',label:'Repair'}] as const).map(item=>
       <button type="button" key={item.id} onClick={()=>setFilter(item.id)} className={filter===item.id?'filter-tab active':'filter-tab'} aria-pressed={filter===item.id}>{item.label}</button>)}
   </div></div>
   <div className="table-scroll"><table className="result-table">
     <caption className="sr-only">Median best measured fitness and additional measurements in ten matched amylase seeds.</caption>
     <thead><tr><th scope="col">Method</th><th scope="col">Median best fitness ↑</th><th scope="col">New measurements</th><th scope="col">Outcome</th></tr></thead>
     <tbody>{filtered.map(m=><tr key={m.id}><th scope="row">{m.name}</th><td className="result-score">{fitness(m.median)}</td><td className="mono-data">{m.measurements}</td><td>{m.detail}</td></tr>)}</tbody>
   </table></div>
   <p className="table-note">Higher fitness is better. Values summarize ten matched seeds; methods that stopped early used fewer measurements.</p>
 </section>;
}
