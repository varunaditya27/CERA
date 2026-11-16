import 'server-only';

export type Dataset={id:string;name:string;source:string;purpose:string;shift:string;split:string;note:string;variants:number|null;available:boolean};

export async function getDatasets():Promise<Dataset[]|null>{
 try{
  const response=await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/datasets`,{cache:'no-store',signal:AbortSignal.timeout(3000)});
  return response.ok?await response.json() as Dataset[]:null;
 }catch{return null;}
}

export const DATASET_NOTES:Record<string,{description:string;preparation:string;sourceUrl:string;sourceLabel:string}>={
 amylase:{
  description:'Variants of Bacillus subtilis alpha amylase, measured for stain-removal activity.',
  preparation:'3,706 measurements matched to the original source. The 425-residue reference and higher-is-better score direction were checked. Development searches apply a four-substitution limit.',
  sourceUrl:'https://flip.protein.properties/',sourceLabel:'FLIP2 benchmark'
 },
 ired:{
  description:'Imine reductase variants measured by enrichment relative to the original enzyme.',
  preparation:'All 8,586 sequence and score pairs were matched against the original laboratory data. The reference and 320-feature representation cache are prepared. The source filtering that produced this split remains incompletely explained.',
  sourceUrl:'https://zenodo.org/records/14544486',sourceLabel:'Original IRED archive'
 },
 hydro:{
  description:'A hydrophobic-core mutagenesis landscape covering three separate protein domains.',
  preparation:'All 24,935 scores match the original fitness_raw data. Reference segments and embeddings are prepared separately for P06241, P01053 and P0A9X9. The original split is derived from fitness, so initial-set construction uses privileged retrospective information.',
  sourceUrl:'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE266299',sourceLabel:'Original GEO study'
 },
 gb1:{
  description:'Four-site protein-binding landscape from the FLIP benchmark.',
  preparation:'Optional evaluation dataset. Reference handling, validation flags and redistribution terms need review before use.',
  sourceUrl:'https://github.com/J-SNACKKB/FLIP/blob/main/splits/gb1/README.md',sourceLabel:'FLIP documentation'
 },
 gfp:{
  description:'Green fluorescent protein fluorescence measurements from ProteinGym.',
  preparation:'Optional dataset. A reproducible starting split and assay redistribution terms need to be established before evaluation.',
  sourceUrl:'https://doi.org/10.1038/nature17995',sourceLabel:'Original GFP paper'
 }
};
