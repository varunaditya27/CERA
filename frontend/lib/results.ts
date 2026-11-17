import 'server-only';

type Method = { covered: number; measured: number; mean_width: number; mean_seconds: number };
export type MixedSearchResults = {
  pairs: number; mixed_higher: number; ties: number; ridge_higher: number;
  methods: { mixed: Method; ridge: Method }; audit_sha256: string;
};

export async function getMixedSearchResults(): Promise<MixedSearchResults | null> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/results/mixed-search`, { cache: 'no-store', signal: AbortSignal.timeout(3000) });
    return response.ok ? await response.json() as MixedSearchResults : null;
  } catch { return null; }
}
