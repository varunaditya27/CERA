'use client';

import { useState } from 'react';
import { RESULTS, fitness } from '../lib/research';

type Filter = 'all' | 'baseline' | 'repair';

export function ResultsTable() {
  const [filter,setFilter] = useState<Filter>('all');
  const filtered = RESULTS.filter(result => filter==='all' || result.category===filter);
  return <section className="results-shell" aria-labelledby="results-table-title">
    <div className="results-toolbar"><div><p className="eyebrow">METHODS / COMPARABLE STARTING SETS</p><h2 id="results-table-title">The nine-policy comparison</h2></div>
      <div className="filter-tabs" role="group" aria-label="Filter result methods">
        {([{key:'all',label:'All nine'},{key:'baseline',label:'Baselines'},{key:'repair',label:'Repairs'}] as const).map(option=>
          <button type="button" key={option.key} aria-pressed={filter===option.key} onClick={()=>setFilter(option.key)} className={filter===option.key?'filter-tab active':'filter-tab'}>{option.label}</button>
        )}
      </div>
    </div>
    <div className="table-scroll"><table className="result-table">
      <caption className="sr-only">Median best measured fitness and new measurement counts for alpha-amylase development, ten matched seeds per method.</caption>
      <thead><tr><th scope="col">Method</th><th scope="col">Median best fitness <span aria-label="Higher is better">↑</span></th><th scope="col">New measurements</th><th scope="col">Observed outcome</th></tr></thead>
      <tbody>{filtered.map((result,index)=><tr key={result.id}>
        <th scope="row"><span className="result-index">{String(index+1).padStart(2,'0')}</span><strong>{result.name}</strong><span className="result-kind">{result.category==='repair'?'REPAIR':'BASELINE'}</span></th>
        <td><span className="result-score">{fitness(result.median)}</span></td>
        <td className="mono-data">{result.measurements}</td>
        <td><span className={result.result==='stopped'?'outcome-dot outcome-stopped':'outcome-dot'} aria-hidden="true"/>{result.detail}</td>
      </tr>)}</tbody>
    </table></div>
    <div className="results-endnote"><span>{filtered.length} of 9 methods shown</span><span>Fitness is not normalized across protein landscapes. Comparison is within amylase only.</span></div>
  </section>;
}
