<script lang="ts">
  import type { CategorizedItem } from '$lib/types';
  export let item: CategorizedItem;

  $: status = (item?.verification?.status ?? '').toLowerCase();
  $: isPassed = status === 'passed';
</script>

<div class="px-8 py-6">
  <header class="mb-6 border-b border-gray-800 pb-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-white">
        Document Chunk #{item.line_number}
      </h1>
      
      <span
        class="rounded-full px-3 py-1 text-xs font-semibold {isPassed ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}"
      >
        Verification: {status}
      </span>
      </div>
    <div class="mt-3 flex flex-wrap gap-2">
      {#each item.tags as tag}
        <span class="rounded-full bg-gray-700 px-3 py-1 text-xs font-medium text-gray-200">
          {tag}
        </span>
      {/each}
    </div>
  </header>

  <section class="prose prose-invert max-w-none">
    <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">Text Sample</h2>
    <p class="whitespace-pre-wrap rounded-lg bg-gray-950 p-4 leading-relaxed text-gray-200 border border-gray-800">
      {item.text_sample}
    </p>
  </section>

  <section class="mt-6">
    <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">Verification Notes</h2>
    <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 text-gray-300 mt-2">
      {item.verification?.notes || 'No notes provided.'}
    </div>
  </section>
  
  <section class="mt-6">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">AI Confidence</h2>
      <div class="flex items-center gap-3 mt-2">
          <div class="h-2 w-64 overflow-hidden rounded-full bg-gray-800">
              <div
                  class="h-full bg-indigo-500"
                  style={`width: ${Math.max(0, Math.min(1, item.category_confidence || 0)) * 100}%`}
              />
          </div>
          <span class="text-sm font-semibold text-gray-300">
              {((item.category_confidence || 0) * 100).toFixed(0)}%
          </span>
      </div>
  </section>
</div>