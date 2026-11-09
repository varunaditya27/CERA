import Link from 'next/link';
import { ArrowUpRight, Beaker } from 'lucide-react';
import type { Dataset } from '../lib/datasets';
export function Catalog({datasets}:{datasets:Dataset[]|null}) {
 if (!datasets) return <div className="offline"><strong>Dataset catalog unavailable</strong><p>Start the FastAPI server to load the local dataset catalog.</p><code>uvicorn app.main:app --app-dir backend --reload</code></div>;
 return <div className="dataset-list"><div className="list-head" aria-hidden="true"><span>Landscape</span><span>Role</span><span>Split / shift</span><span>Variants</span></div><ul className="catalog-items">{datasets.map((d,i)=><li key={d.id}><Link className="dataset-row" href={`/datasets/${d.id}`}><div className="landscape"><span className={`dataset-icon tone-${i}`}><Beaker size={19} aria-hidden="true"/></span><div><h3>{d.name}</h3><p>{d.source} <span>·</span> {d.note}</p></div></div><span className="role"><span className="sr-only">Role: </span>{d.purpose}</span><div className="split"><strong><span className="sr-only">Split: </span>{d.split}</strong><small>{d.shift === 'Not assigned' ? 'Shift not assigned' : `${d.shift} shift`}</small></div><div className="variant-count"><span className="sr-only">Variants: </span>{d.variants !== null ? d.variants.toLocaleString('en-US') : 'Unavailable'} <ArrowUpRight size={14} aria-hidden="true"/></div></Link></li>)}</ul></div>
}
