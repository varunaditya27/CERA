import { Catalog } from '../../components/catalog';
import { Topbar } from '../../components/topbar';
import { getDatasets } from '../../lib/datasets';
export const metadata={title:'Datasets'};
export const dynamic='force-dynamic';
export default async function DatasetsPage(){const datasets=await getDatasets();return <><Topbar section="Datasets"/><div className="content route-content"><div className="route-header"><h1>Fitness landscapes</h1><p>Experimental measurements used to evaluate a search without running new laboratory experiments.</p></div><div className="workspace-heading"><div><h2>Dataset catalog</h2><p>Choose a landscape to see its purpose and preparation notes.</p></div><div className="catalog-status"><span className="status-dot"/> {datasets ? `${datasets.filter(d=>d.available).length} of ${datasets.length} available`:'Connection required'}</div></div><Catalog datasets={datasets}/><div className="catalog-footnote"><strong>About the labels</strong><p>The raw files contain measured fitness values. Future experiment runs must keep unqueried labels hidden from the optimizer.</p></div></div></>}
