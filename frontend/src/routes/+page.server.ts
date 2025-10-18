import type { PageServerLoad } from './$types';
import { readFile } from 'fs/promises';
import type { CategorizedItem } from '$lib/types';

export const load: PageServerLoad = async () => {
  // This path correctly reads the file from the 'static' directory.
  const dataPath = 'static/verified_categorization.json';
  
  try {
    const fileContents = await readFile(dataPath, 'utf-8');
    const items = JSON.parse(fileContents) as CategorizedItem[];
    
    // Safety check for data - clean and simple
    const normalized = items.map((it) => ({
      ...it,
      line_number: it.line_number, // Reads the correct key directly
      tags: Array.isArray(it.tags) ? it.tags : [],
      verification: it.verification ?? { status: 'failed', notes: 'Missing verification data.' }
    }));

    return { items: normalized };

  } catch (error) {
    console.error("Failed to load or parse data file from 'static' folder:", error);
    return { items: [] };
  }
};