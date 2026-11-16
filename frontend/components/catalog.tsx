import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import type { Dataset } from '../lib/datasets';

export function Catalog({datasets}:{datasets:readonly Dataset[]}) {
 return <div className="catalog-list">
   {datasets.map(d=><Link key={d.id} className="catalog-entry" href={'/datasets/'+d.id}>
     <span className="catalog-name">{d.name}<small>{d.note}</small></span>
     <span className="catalog-role">{d.purpose}</span>
     <span className="catalog-split">{d.split}</span>
     <span className="catalog-count">{d.variants?.toLocaleString('en-US') ?? '—'}</span>
     <ArrowUpRight size={18} strokeWidth={1.5} aria-hidden="true"/>
   </Link>)}
 </div>;
}
