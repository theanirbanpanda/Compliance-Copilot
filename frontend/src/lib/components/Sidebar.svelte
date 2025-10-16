<script lang="ts">
  import type { CategorizedItem } from '$lib/types';
  import { createEventDispatcher } from 'svelte';

  export let items: CategorizedItem[] = [];
  export let selectedIndex = 0;

  const dispatch = createEventDispatcher<{ select: number }>();

  // Function to create a short text preview
  function preview(text: string, words = 8): string {
    const parts = text.trim().split(/\s+/);
    const sample = parts.slice(0, words).join(' ');
    return parts.length > words ? sample + '…' : sample;
  }
</script>

<div class="flex h-full flex-col">
  <div class="sticky top-0 z-10 border-b border-gray-800 bg-gray-900/80 px-4 py-3 backdrop-blur">
    <h2 class="text-lg font-semibold tracking-wide text-white">Compliance Copilot</h2>
    <p class="mt-1 text-sm text-gray-400">{items.length} items processed</p>
  </div>

  <ul class="flex-1 overflow-y-auto">
    {#each items as item, i}
      <li>
        <button
          type="button"
          class="block w-full border-b border-gray-800/60 px-4 py-3 text-left transition-colors duration-150 hover:bg-gray-800/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          class:bg-gray-800={i === selectedIndex}
          on:click={() => dispatch('select', i)}
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-mono text-gray-400">ID: {item.line_number}</span>
            <span class:text-green-400={item.verification.status === 'passed'} class:text-red-400={item.verification.status === 'failed'} class="text-xs font-semibold uppercase tracking-wider">
              {item.verification.status}
            </span>
          </div>
          <div class="mt-1 line-clamp-2 text-sm text-gray-200">
            {preview(item.text_sample)}
          </div>
        </button>
      </li>
    {/each}
  </ul>
</div>