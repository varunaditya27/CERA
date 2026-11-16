import { ArrowUpRight } from 'lucide-react';
import { Topbar } from '../../components/topbar';

export const metadata={title:'Method'};

const steps=[
 {name:'Prepare',body:'Start with 100 measured variants. Fit models on 80 and reserve 20 to set prediction ranges.'},
 {name:'Predict',body:'A frozen ESM-2 encoder provides sequence features. Five ridge models estimate fitness for unmeasured variants.'},
 {name:'Select',body:'Choose up to ten eligible variants per round. Record predictions before revealing their measured scores.'},
 {name:'Audit and repair',body:'Check warnings, then verify any permitted reward-weight change. Retain the old rule or stop when no proposal passes.'}
];

export default function Workflow(){
 return <><Topbar section="Method"/><div className="route-content">
  <header className="route-hero method-intro"><h1>The method</h1><p>Retrospective search over measured protein variants. Hidden scores are revealed only when selected.</p></header>
  <ol className="method-list">{steps.map((step,i)=><li className="method-item" key={step.name}>
    <span className="method-number">{String(i+1).padStart(2,'0')}</span><h2>{step.name}</h2><p>{step.body}</p>
  </li>)}</ol>
  <div className="method-outro"><span>The current amylase experiments accepted no repairs. The procedure is still under evaluation.</span><a href="https://github.com/varunaditya27/CERA/blob/research/experiment-foundations/research/repeated_matched_protocol.md" className="inline-link" target="_blank" rel="noreferrer">Experiment protocol <ArrowUpRight size={17}/></a></div>
  <footer className="site-footer"><span>CERA</span><span>Research in progress</span></footer>
 </div></>;
}
