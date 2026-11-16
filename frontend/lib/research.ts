/** Frozen, attributed snapshot from research/experiment-foundations, 2026-11-16.
 * Not a live API, clinical claim, or cross-landscape result.
 */
export const RESEARCH_SOURCE = 'https://github.com/varunaditya27/CERA/blob/research/experiment-foundations/research/repeated_matched_findings.md';
export const RESEARCH_BRANCH = 'https://github.com/varunaditya27/CERA/tree/research/experiment-foundations';
export const SNAPSHOT_DATE = '16 NOV 2026';

export type MethodResult = {
  id: string;
  name: string;
  category: 'baseline' | 'repair';
  median: number;
  measurements: string;
  detail: string;
  result: 'complete' | 'stopped';
};

export const RESULTS: MethodResult[] = [
  {id:'random',name:'Random selection',category:'baseline',median:0.1971083333333333,measurements:'100',detail:'Exhausted budget in all ten seeds',result:'complete'},
  {id:'greedy',name:'Greedy prediction',category:'baseline',median:0.19331666666666664,measurements:'100',detail:'Exhausted budget in all ten seeds',result:'complete'},
  {id:'fixed',name:'Fixed reward',category:'baseline',median:0.19331666666666664,measurements:'100',detail:'Exhausted budget in all ten seeds',result:'complete'},
  {id:'repair',name:'Rule-based repair',category:'repair',median:0.19331666666666664,measurements:'20',detail:'Two failed repairs; stopped in every seed',result:'stopped'},
  {id:'gemini_repair',name:'Gemini-assisted repair',category:'repair',median:0.19331666666666664,measurements:'20',detail:'No repair accepted; stopped in every seed',result:'stopped'},
  {id:'ucb',name:'Mean + model spread',category:'baseline',median:0.19331666666666664,measurements:'100',detail:'Ensemble uncertainty as an acquisition bonus',result:'complete'},
  {id:'ei',name:'Expected improvement',category:'baseline',median:0.19331666666666664,measurements:'100',detail:'Gaussian approximation, not calibrated posterior',result:'complete'},
  {id:'genetic',name:'Recombination + mutation',category:'baseline',median:0.2116333333333333,measurements:'100',detail:'Reached the finite-pool maximum in 8/10 seeds',result:'complete'},
  {id:'adalead',name:'AdaLead-style local search',category:'baseline',median:0.19331666666666664,measurements:'0–32',detail:'No eligible neighbors in all ten seeds',result:'stopped'}
];

export const DATASET_REFERENCE = [
  {id:'amylase',name:'Alpha amylase',source:'FLIP2',purpose:'Development',shift:'Position',split:'Close to far',note:'Stain-removal activity across positional shift',variants:3706,available:true},
  {id:'ired',name:'Imine reductase',source:'FLIP2',purpose:'Evaluation',shift:'Mutation count',split:'Two to many',note:'Enzyme variants across mutation-count shift',variants:8586,available:true},
  {id:'hydro',name:'Hydrophobic core',source:'FLIP2',purpose:'Evaluation',shift:'Fitness',split:'Low to high',note:'Three separate protein backbones',variants:24935,available:true},
  {id:'gb1',name:'GB1',source:'FLIP',purpose:'Additional',shift:'Fitness',split:'Low vs high',note:'Optional four-site binding landscape',variants:null,available:false},
  {id:'gfp',name:'Green fluorescent protein',source:'ProteinGym',purpose:'Additional',shift:'Not assigned',split:'Needs seed split',note:'Optional fluorescence assay',variants:null,available:false}
] as const;

export function fitness(value: number) { return value.toFixed(5); }
