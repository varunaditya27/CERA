import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, ArrowUpRight } from 'lucide-react';
import { DATASET_NOTES, getDatasets } from '../../../lib/datasets';
import { DATASET_REFERENCE } from '../../../lib/research';

export const dynamic='force-dynamic';

export async function generateMetadata({params}:{params:Promise<{id:string}>}){
  const {id}=await params;
  const names:Record<string,string>={amylase:'Alpha amylase',ired:'Imine reductase',hydro:'Hydrophobic core',gb1:'GB1',gfp:'Green fluorescent protein'};
  return {title:names[id]??'Dataset'};
}
export default async function DatasetDetail({params}:{params:Promise<{id:string}>}){
  const {id}=await params;
  const info=DATASET_NOTES[id];
  if(!info)notFound();
  const live=await getDatasets();
  const data=(live??DATASET_REFERENCE).find(d=>d.id===id);
  if(!data)notFound();

  return <div className="route-content">
    <Link href="/datasets" className="detail-back"><ArrowLeft size={16} aria-hidden="true"/> All datasets</Link>
    <div className="detail-layout">
      <div>
        <div className="route-hero"><h1>{data.name}</h1><p className="detail-lead">{info.description}</p></div>
        <section className="detail-section"><h2>Preparation</h2><p>{info.preparation}</p></section>
        <section className="detail-section"><h2>Source</h2><a className="inline-link" href={info.sourceUrl} target="_blank" rel="noreferrer">{info.sourceLabel}<ArrowUpRight size={15}/></a></section>
        {!live&&<p className="quiet-note">Counts from the committed reference snapshot.</p>}
      </div>
      <aside className="detail-meta"><h2>Dataset details</h2><dl>
        <div><dt>Variants</dt><dd>{data.variants?.toLocaleString('en-US')??'Unavailable'}</dd></div>
        <div><dt>Role</dt><dd>{data.purpose}</dd></div>
        <div><dt>Split</dt><dd>{data.split}</dd></div>
        <div><dt>Shift</dt><dd>{data.shift}</dd></div>
      </dl></aside>
    </div>
    <footer className="site-footer"><span>CERA</span><Link href="/datasets">Datasets</Link></footer>
  </div>;
}
