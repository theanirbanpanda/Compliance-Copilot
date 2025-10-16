import type { PageServerLoad } from './$types';
/// <reference types="node" />
import { readFile } from 'fs/promises';
import path from 'path';
import type { CategorizedItem } from '$lib/types';

export const load: PageServerLoad = async () => {
  // Go up one level from the 'frontend' folder to find the 'data' folder
  const dataPath = path.resolve(process.cwd(), '../data/verified_categorization.json');
  
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