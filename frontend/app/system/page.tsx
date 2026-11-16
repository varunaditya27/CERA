import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

export const metadata={title:'System'};

const layers=[
 {index:'01',name:'Measurement boundary',detail:'A controlled runner reveals scores only for selected variants. The web API publishes dataset metadata, not fitness labels.',source:'backend/app/experiments/experiment.py'},
 {index:'02',name:'Sequence representations',detail:'A fixed ESM-2 model converts each protein sequence into 320 numerical features.',source:'backend/app/features/'},
 {index:'03',name:'Prediction and uncertainty',detail:'Five ridge models estimate fitness and model spread. Separate examples set prediction ranges.',source:'backend/app/experiments/prediction_pilot.py'},
 {index:'04',name:'Warning and verification',detail:'Five warning checks record possible problems. Proposed reward changes face a constrained local verifier.',source:'backend/app/rewards/'},
 {index:'05',name:'Evaluation',detail:'A separate evaluator reconstructs the run after selections finish and checks fitness, measurements, stopping, and recorded evidence.',source:'backend/app/experiments/evaluation.py'},
];

const repoBase='https://github.com/varunaditya27/CERA/tree/research/experiment-foundations/';

export default function SystemPage(){
 return <div className="route-content system-page">
  <header className="route-hero">
   <p className="route-kicker">Implementation</p>
   <h1>Inside CERA.</h1>
   <p>The research engine is built in Python. The website explains the work and displays recorded results. They are deliberately separate.</p>
  </header>
  <section className="system-boundary" aria-label="System boundaries">
   <div className="system-module"><span>Research engine</span><strong>Python</strong><p>Measurement control, prediction, warnings, verification and evaluation</p></div>
   <span className="system-divider" aria-hidden="true">≠</span>
   <div className="system-module"><span>Research website</span><strong>Next.js</strong><p>Guided walkthrough, dataset catalog, methods and recorded findings</p></div>
  </section>
  <section className="system-layers">
   <div className="section-heading"><div><h2>How a run moves through the system</h2></div></div>
   <ol className="system-layer-list">{layers.map(layer=><li key={layer.index}>
    <span className="system-layer-index">{layer.index}</span>
    <h3>{layer.name}</h3>
    <p>{layer.detail}</p>
    <a href={repoBase+layer.source} target="_blank" rel="noreferrer" aria-label={`Inspect ${layer.name} in the GitHub source`}><ArrowUpRight size={18}/></a>
   </li>)}</ol>
  </section>
  <section className="system-status">
   <div><h2>What remains to be tested</h2></div>
   <div><p>Amylase experiments establish that the system runs and can be audited. They do not establish reliable diagnoses or successful repairs. Evaluation on IRED and the hydrophobic-core proteins remains ahead.</p>
    <Link className="inline-link" href="/experiments">Current results <ArrowUpRight size={16}/></Link>
   </div>
  </section>
  <footer className="site-footer"><span>CERA</span><Link href="/workflow">Method <ArrowUpRight size={15}/></Link></footer>
 </div>;
}
