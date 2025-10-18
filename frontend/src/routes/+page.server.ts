import type { PageServerLoad } from './$types';
import { readFile } from 'fs/promises';
import type { CategorizedItem } from '$lib/types';

export const load: PageServerLoad = async () => {
  // --- THIS IS THE DEFINITIVE FIX ---
  // This path correctly reads the file from the 'static' directory
  // from within the SvelteKit server environment.
  const dataPath = './static/verified_categorization.json';
  
  try {
    const fileContents = await readFile(dataPath, 'utf-8');
    const items = JSON.parse(fileContents) as CategorizedItem[];
    
    // Safety check for data
    const normalized = items.map((it) => ({
      ...it,
      tags: Array.isArray(it.tags) ? it.tags : [],
      verification: it.verification ?? { status: 'failed', notes: 'Missing verification data.' }
    }));

    return { items: normalized };

  } catch (error) {
    console.error("Failed to load or parse data file:", error);
    return { items: [] };
  }
};