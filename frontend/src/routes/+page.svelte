<script lang="ts">
  import type { PageData } from './$types';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import DetailView from '$lib/components/DetailView.svelte';

  export let data: PageData;

  // Default to showing the first item
  let selectedIndex = 0;
  const items = data.items;

  function handleSelect(event: CustomEvent<number>) {
    selectedIndex = event.detail;
  }
</script>

<div class="min-h-screen w-full bg-gray-900 text-gray-100 font-sans">
  <div class="mx-auto flex h-screen max-w-7xl">
    
    <aside class="w-96 shrink-0 border-r border-gray-800 bg-gray-950/50">
      <Sidebar {items} {selectedIndex} on:select={handleSelect} />
    </aside>

    <main class="flex-1 overflow-y-auto">
      {#if items?.length}
        <DetailView item={items[selectedIndex]} />
      {:else}
        <div class="p-8 text-gray-500">
            <h2 class="text-xl font-semibold">No Data Found</h2>
            <p class="mt-2">Could not load items from <code>data/verified_categorization.json</code>. Please ensure the file exists and is correctly formatted.</p>
        </div>
      {/if}
    </main>

  </div>
</div>