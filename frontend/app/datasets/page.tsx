import { Catalog } from '../../components/catalog';
import { Topbar } from '../../components/topbar';
import { getDatasets } from '../../lib/datasets';
import { DATASET_REFERENCE } from '../../lib/research';

export const metadata={title:'Datasets'};
export const dynamic='force-dynamic';

export default async function DatasetsPage(){
 const live=await getDatasets();
 const datasets=live ?? DATASET_REFERENCE;
 return <><Topbar section="Datasets"/><div className="route-content catalog-container">
   <header className="route-hero catalog-header"><div><h1>Protein datasets</h1></div>
     <p>Three primary FLIP2 landscapes and two optional datasets. Alpha amylase is used for development; IRED and hydrophobic core are prepared for evaluation.</p>
   </header>
   <Catalog datasets={datasets}/>
   {!live && <p className="catalog-aside">Showing committed reference counts. The local dataset API is not connected.</p>}
   <footer className="site-footer"><span>CERA</span><span>Dataset sources are linked in each profile.</span></footer>
 </div></>;
}
