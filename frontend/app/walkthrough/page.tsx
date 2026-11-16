import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { WalkthroughLab } from '../../components/walkthrough-lab';

export const metadata={title:'Walkthrough'};
const walkthroughSource='https://github.com/varunaditya27/CERA/blob/research/experiment-foundations/research/experiment_walkthrough.md';

export default function WalkthroughPage(){
 return <div className="route-content walkthrough-page">
  <header className="route-hero">
   <p className="route-kicker">A two-round example</p>
   <h1>Watch a prediction go wrong.</h1>
   <p>Choose a candidate, reveal its measurement, and see what the system knows at each step.</p>
  </header>
  <WalkthroughLab/>
  <div className="walkthrough-after">
   <div><h2>From an example to the real study.</h2><p>This demonstration uses invented scores to explain the experiment. The amylase results are recorded separately and can be inspected.</p></div>
   <div><Link className="inline-link" href="/experiments">See measured results <ArrowUpRight size={16}/></Link>
    <a className="inline-link" href={walkthroughSource} target="_blank" rel="noreferrer">Example source <ArrowUpRight size={16}/></a></div>
  </div>
  <footer className="site-footer"><span>CERA</span><Link href="/workflow">Method <ArrowUpRight size={15}/></Link></footer>
 </div>;
}
