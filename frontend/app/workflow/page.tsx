import { ArrowUpRight } from 'lucide-react';
import { MethodExplorer } from '../../components/method-explorer';

export const metadata={title:'Method'};

const parameters=[
  {value:'100',label:'Starting measurements'},
  {value:'100',label:'Maximum new measurements'},
  {value:'10',label:'Variants per batch'},
  {value:'4',label:'Maximum substitutions'}
];

export default function Workflow(){
  return <div className="route-content method-page">
    <header className="route-hero"><h1>The method</h1>
      <p>A retrospective search where unselected fitness scores remain hidden until a variant is queried.</p>
    </header>
    <MethodExplorer/>
    <section className="method-parameters" aria-label="Development protocol parameters">
      {parameters.map(item=><div key={item.label}><strong>{item.value}</strong><span>{item.label}</span></div>)}
    </section>
    <div className="method-context">
      <div><h2>What the checks establish</h2></div>
      <div><p>A passing repair is an allowed change supported by earlier evidence, not proof of improved future fitness. The full evaluation is still pending on the other proteins.</p>
        <a href="https://github.com/varunaditya27/CERA/blob/research/experiment-foundations/research/repeated_matched_protocol.md" className="inline-link" target="_blank" rel="noreferrer">
          Experiment protocol <ArrowUpRight size={16}/>
        </a>
      </div>
    </div>
    <footer className="site-footer"><span>CERA</span><span>Development methodology</span></footer>
  </div>;
}
