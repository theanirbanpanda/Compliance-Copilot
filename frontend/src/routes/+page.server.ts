import type { PageServerLoad } from './$types';
import { readFile } from 'fs/promises';
import path from 'path';
import type { CategorizedItem } from '$lib/types';

export const load: PageServerLoad = async () => {
  // --- THIS IS THE DEFINITIVE FIX ---
  // The server code runs inside the 'frontend' directory during the build.
  // This path correctly navigates up one level ('../') to find the 'data' folder.
  const dataPath = path.resolve('../data/verified_categorization.json');
  
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
    // Return an empty array if the file is missing or broken
    return { items: [] };
  }
};