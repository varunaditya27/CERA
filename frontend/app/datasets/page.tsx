import { Catalog } from '../../components/catalog';
import { getDatasets } from '../../lib/datasets';
import { DATASET_REFERENCE } from '../../lib/research';

export const metadata={title:'Datasets'};
export const dynamic='force-dynamic';

export default async function DatasetsPage(){
  const live=await getDatasets();
  const datasets=live??DATASET_REFERENCE;
  return <div className="route-content catalog-container">
    <header className="route-hero catalog-header">
      <h1>Protein datasets</h1>
      <p>Alpha amylase is used for development. IRED and hydrophobic-core proteins are prepared for evaluation.</p>
    </header>
    <Catalog datasets={datasets}/>
    {!live&&<p className="catalog-aside">Showing committed reference counts. The local dataset API is not connected.</p>}
    <footer className="site-footer"><span>CERA</span><span>Source details in each dataset profile.</span></footer>
  </div>;
}
