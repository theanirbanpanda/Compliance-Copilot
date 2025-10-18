import type { PageServerLoad } from './$types';
import { readFile } from 'fs/promises';
import path from 'path';
import type { CategorizedItem } from '$lib/types';

export const load: PageServerLoad = async () => {
  // This path correctly reads the file from the 'static' directory,
  // which is where our build command guarantees it will be.
  const dataPath = path.resolve('static/verified_categorization.json');
  
  try {
    const fileContents = await readFile(dataPath, 'utf-8');
    const items = JSON.parse(fileContents) as CategorizedItem[];
    
    // Safety check for data
    const normalized = items.map((it) => ({
      ...it,
      // The line_number is now read directly, without any confusing fallbacks.
      line_number: it.line_number, 
      tags: Array.isArray(it.tags) ? it.tags : [],
      verification: it.verification ?? { status: 'failed', notes: 'Missing verification data.' }
    }));

    return { items: normalized };

  } catch (error) {
    console.error("Failed to load or parse data file from 'static' folder:", error);
    return { items: [] };
  }
};