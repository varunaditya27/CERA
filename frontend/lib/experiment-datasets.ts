export const experimentDatasets = {
  amylase: 'Alpha amylase',
  ired: 'Imine reductase (IRED)',
  'hydro-P06241': 'Hydrophobic core · P06241',
  'hydro-P01053': 'Hydrophobic core · P01053',
  'hydro-P0A9X9': 'Hydrophobic core · P0A9X9',
} as const;

export function datasetName(id: string | undefined): string {
  return experimentDatasets[id as keyof typeof experimentDatasets] ?? (id || 'Alpha amylase');
}
