import 'server-only';
export type Dataset = { id: string; name: string; source: string; purpose: string; shift: string; split: string; note: string; variants: number | null; available: boolean };
export async function getDatasets(): Promise<Dataset[] | null> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/datasets`, { cache: 'no-store', signal: AbortSignal.timeout(3000) });
    return response.ok ? await response.json() as Dataset[] : null;
  } catch { return null; }
}
export const DATASET_NOTES: Record<string, { description: string; preparation: string; sourceUrl: string; sourceLabel: string }> = {
 amylase: {description:'Measurements of stain-removal activity for variants of Bacillus subtilis alpha amylase.',preparation:'Confirm target direction and the wild-type reference before applying mutation constraints.',sourceUrl:'https://flip.protein.properties/',sourceLabel:'FLIP2 benchmark'},
 ired: {description:'Activity measurements for variants of an imine reductase, with a split based on mutation count.',preparation:'The archived split contains 8,586 variants. The benchmark website lists 17,143; the difference needs investigation.',sourceUrl:'https://zenodo.org/records/11357236',sourceLabel:'Original IRED data'},
 hydro: {description:'Stability measurements across variants of three different protein backbones.',preparation:'Assign variants to their respective wild types before computing mutation distances or defining search pools.',sourceUrl:'https://doi.org/10.5281/zenodo.11175470',sourceLabel:'Original hydrophobic-core data'},
 gb1: {description:'A four-site protein binding landscape, split according to fitness relative to wild type.',preparation:'Use the documented inferred reference sequence and handle blank validation flags consistently.',sourceUrl:'https://github.com/J-SNACKKB/FLIP/blob/main/splits/gb1/README.md',sourceLabel:'FLIP GB1 documentation'},
 gfp: {description:'Fluorescence measurements for green fluorescent protein variants, including multiple mutations.',preparation:'Define a reproducible seed split before running experiments. Higher DMS score means higher fitness.',sourceUrl:'https://doi.org/10.1038/nature17995',sourceLabel:'Original GFP publication'},
};
