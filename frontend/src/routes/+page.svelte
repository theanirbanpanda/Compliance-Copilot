<script lang="ts">
  // --- Your working JavaScript logic remains UNCHANGED ---
  let analysisResults: any[] = [];
  let isLoading = false;
  let errorMessage = '';
  let inputText = ''; // Start empty

  async function analyzeText() {
    if (!inputText.trim()) {
      errorMessage = 'Please paste some text to analyze.';
      analysisResults = [];
      return;
    }
    isLoading = true;
    errorMessage = '';
    analysisResults = [];
    try {
      const response = await fetch('http://127.0.0.1:5000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      const results = await response.json();
      analysisResults = Array.isArray(results) ? results : [];
    } catch (error: any) {
      errorMessage = `Failed to connect: ${error.message}. Is Python server running?`;
    } finally {
      isLoading = false;
    }
  }
  // --- End of unchanged JavaScript logic ---
</script>

<div class="page-container">
  <div class="main-layout">

    <div class="main-content">
      <header class="page-header">
        <h1 class="main-title">
          Compliance <span class="accent-text">Copilot</span> <span class="emoji">🤖</span>
        </h1>
        <p class="subtitle">
          Unlock insights hiding in your compliance documents. ✨
        </p>
      </header>

      <div class="card input-card narrow-card">
        <div class="card-content">
          <h2 class="card-title">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2Z" /></svg>
            Input Document Text
          </h2>
          <section>
            <textarea
              bind:value={inputText}
              class="text-input"
              placeholder="Paste text here..."
            ></textarea>
            <button
              on:click={analyzeText}
              disabled={isLoading}
              class="analyze-button button-primary"
            >
              {#if isLoading}
                <span class="loading-indicator">
                  <svg class="spinner" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Processing...
                </span>
              {:else}
                Search
              {/if}
            </button>
          </section>
        </div>
      </div>

      <section class="results-section">
        <h2 class="results-title">
          Analysis Dashboard
        </h2>
        {#if errorMessage}
          <div class="error-box">
            <svg class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span><strong>Error:</strong> {errorMessage}</span>
          </div>
        {/if}

        {#if analysisResults.length > 0}
          <div class="results-grid">
            {#each analysisResults as item (item.id)}
              <div class="result-card">
                <div class="card-header">
                  <span class="status-pill {item.verification?.status === 'passed' ? 'status-passed' : 'status-failed'}">
                    {item.verification?.status || 'N/A'}
                  </span>
                  <h3 class="chunk-id">Chunk ID: {item.id}</h3>
                </div>
                <p class="summary">{item.summary || 'No summary.'}</p>
                <div class="tags-section">
                  <h4 class="tags-title">Categories</h4>
                  <div class="tags-container">
                    {#each item.tags || [] as tag}
                      <span class="tag-item">{tag}</span>
                    {/each}
                  </div>
                </div>
                <div class="details-section">
                  <h4 class="details-title">Verification</h4>
                  <p class="verification-notes {item.verification?.status === 'passed' ? 'notes-passed' : 'notes-failed'}">
                    {item.verification?.notes || 'No notes.'}
                  </p>
                  <details class="details-toggle">
                    <summary class="details-summary">Show Sample</summary>
                    <p class="text-sample">
                      {item.text_sample || 'No sample.'}
                    </p>
                  </details>
                </div>
              </div>
            {/each}
          </div>
        {:else if !isLoading && !errorMessage}
          <div class="empty-state">
            <svg class="empty-state-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2Z" /></svg>
            <h3 class="empty-state-title">Awaiting Analysis</h3>
            <p class="empty-state-text">Paste text above and click 'Search'.</p>
          </div>
        {/if}
      </section>

      <footer class="page-footer">
        Compliance Copilot MVP &copy; {new Date().getFullYear()}
      </footer>
    </div><aside class="sidebar-notifications">
      <div class="card notification-card">
        <h2 class="card-title notification-title">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.017 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" /></svg>
          Recent Alerts
        </h2>
        <div class="notification-content">
          <p class="notification-description">Stay updated on relevant compliance changes.</p>
          <ul class="notification-list">
            <li><span class="status-dot status-new"></span> New tax filing deadline announced for Q4.</li>
            <li><span class="status-dot status-update"></span> Update to labor law regarding remote work policy.</li>
            <li><span class="status-dot status-info"></span> Reminder: Annual safety compliance report due soon.</li>
          </ul>
           <a href="#" class="view-all-link">View All Alerts</a>
        </div>
      </div>
    </aside></div> </div> <style>
  /* Base Layout */
  .page-container {
    min-height: 100vh; width: 100%;
    background-image: linear-gradient(to bottom right, #111827, #1f2937);
    color: #e5e7eb;
    font-family: 'Inter', system-ui, sans-serif;
    padding: 2rem 1rem;
  }
  /* NEW: Main layout using Grid */
  .main-layout {
    display: grid;
    grid-template-columns: 1fr auto; /* Main content takes remaining space, sidebar takes auto */
    gap: 2rem; /* Space between main content and sidebar */
    max-width: 80rem; /* Increased max-width */
    margin: auto;
  }
  .main-content {
    /* Takes the first column */
  }
  .sidebar-notifications {
    /* Takes the second column */
    width: 20rem; /* Fixed width for the sidebar */
    padding-top: 1rem; /* Align top with main content */
  }

  /* Header */
  .page-header { text-align: center; margin-bottom: 3rem; grid-column: 1 / -1; /* Span across both columns if needed, adjust if header is inside main-content only */ }
  .main-title { font-size: 2.5rem; font-weight: 800; color: white; letter-spacing: -0.025em; }
  .accent-text { background-image: linear-gradient(to right, #a78bfa, #6366f1); color: transparent; -webkit-background-clip: text; background-clip: text; }
  .emoji { font-size: 1.8rem; vertical-align: middle; margin-left: 0.3rem; }
  .subtitle { margin-top: 0.5rem; font-size: 1.1rem; color: #9ca3af; }

  /* Card Styles */
  .card {
    background-color: rgba(31, 41, 55, 0.7); backdrop-filter: blur(8px);
    padding: 1.25rem; border-radius: 0.75rem; /* Slightly smaller padding */
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(55, 65, 81, 0.4);
    position: relative; overflow: hidden;
  }
  .input-card { margin-bottom: 2.5rem; }
  .narrow-card {
    /* Applied to input card */
    max-width: 85%; /* Input slightly narrower than results */
    margin-left: auto;
    margin-right: auto;
  }
  .card-content { position: relative; z-index: 10; }
  .card-title {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;
    color: #c7d2fe; border-bottom: 1px solid rgba(129, 140, 248, 0.2);
    padding-bottom: 0.5rem;
  }
  .card-title svg { height: 1.1rem; width: 1.1rem; color: #a5b4fc; }

  /* Input Section */
  .text-input {
    width: 100%; height: 10rem;
    padding: 0.75rem; background-color: #111827;
    border: 1px solid #4b5563; border-radius: 0.375rem;
    color: #d1d5db; font-family: monospace; font-size: 0.875rem;
    resize: vertical; outline: none; transition: border-color 0.2s, box-shadow 0.2s;
  }
  .text-input:focus { border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3); }
  .analyze-button {
    margin-top: 0.75rem; width: 100%;
    padding: 0.6rem 1.25rem; font-size: 0.95rem;
    background-image: linear-gradient(to right, #8b5cf6, #4f46e5);
    color: white; font-weight: 600; border-radius: 0.375rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s;
    cursor: pointer; border: none;
  }
  .analyze-button:hover:not(:disabled) { filter: brightness(1.1); box-shadow: 0 4px 8px rgba(79, 70, 229, 0.2); }
  .analyze-button:disabled { cursor: wait; opacity: 0.6; background-image: none; background-color: #4b5563; }
  .loading-indicator { display: flex; align-items: center; justify-content: center; gap: 0.5rem; }

  /* Notification Sidebar Styles */
  .notification-card {
      /* Inherits .card styles */
      border-color: rgba(20, 184, 166, 0.3); /* Teal border */
      background-color: rgba(17, 24, 39, 0.6); /* Darker background */
  }
  .notification-title {
     font-size: 1rem;
     color: #5eead4; /* Teal text */
     border-bottom-color: rgba(45, 212, 191, 0.2);
     margin-bottom: 0.75rem;
  }
  .notification-title svg {
      color: #5eead4;
      height: 1rem; width: 1rem;
  }
  .notification-description {
      font-size: 0.8rem;
      color: #99f6e4; /* Lighter teal */
      margin-bottom: 1rem;
      opacity: 0.9;
  }
  .notification-list {
      list-style: none; /* Remove default bullets */
      padding: 0;
      margin: 0;
      font-size: 0.75rem; /* Smaller text */
      color: #a7f3d0; /* Even lighter teal */
      opacity: 0.85;
      display: flex;
      flex-direction: column;
      gap: 0.5rem; /* Space between items */
      margin-bottom: 1rem;
  }
  .notification-list li {
      display: flex;
      align-items: center;
      gap: 0.4rem;
  }
  .status-dot {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      flex-shrink: 0;
  }
  .status-new { background-color: #34d399; } /* Green */
  .status-update { background-color: #fbbf24; } /* Amber */
  .status-info { background-color: #60a5fa; } /* Blue */
  .view-all-link {
      display: block;
      margin-top: 1rem;
      font-size: 0.75rem;
      text-align: right;
      color: #5eead4;
      text-decoration: none;
      transition: color 0.2s;
  }
  .view-all-link:hover {
      color: #99f6e4;
  }


  /* Results Section */
  .results-section { margin-top: 0; /* No top margin needed in grid */ }
  .results-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 1.25rem; color: white; border-bottom: 1px solid rgba(79, 70, 229, 0.2); padding-bottom: 0.5rem; }
  .error-box { padding: 0.75rem; margin-bottom: 1.5rem; background-color: rgba(153, 27, 27, 0.4); border: 1px solid #ef4444; color: #fecaca; border-radius: 0.5rem; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
  .error-icon { height: 1.25rem; width: 1.25rem; flex-shrink: 0; }
  .results-grid { display: flex; flex-direction: column; gap: 1.5rem; }
  .result-card {
    padding: 1.25rem; background-color: rgba(31, 41, 55, 0.4);
    border: 1px solid rgba(55, 65, 81, 0.5); border-radius: 0.75rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: border-color 0.3s, box-shadow 0.3s;
  }
  .result-card:hover { border-color: rgba(99, 102, 241, 0.3); box-shadow: 0 2px 5px rgba(79, 70, 229, 0.1); }
  .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
  .status-pill { padding: 0.15rem 0.6rem; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; border-radius: 9999px; letter-spacing: 0.05em; }
  .status-passed { background-color: #10b981; color: #064e3b; }
  .status-failed { background-color: #ef4444; color: #fef2f2; }
  .chunk-id { font-family: monospace; font-size: 0.75rem; color: #6b7280; }
  .summary { margin-top: 0.25rem; color: #e0e7ff; font-size: 0.95rem; border-bottom: 1px solid #4b5563; padding-bottom: 0.75rem; margin-bottom: 0.75rem; line-height: 1.5; }
  .tags-section { margin-bottom: 1rem; }
  .tags-title { font-size: 0.7rem; font-weight: 500; text-transform: uppercase; color: #9ca3af; margin-bottom: 0.4rem; letter-spacing: 0.05em; }
  .tags-container { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .tag-item { border-radius: 9999px; background-color: rgba(55, 48, 163, 0.5); padding: 0.15rem 0.6rem; font-size: 0.7rem; color: #c7d2fe; border: 1px solid rgba(79, 70, 229, 0.3); }
  .details-section { margin-top: 1rem; padding: 0.75rem; border-radius: 0.5rem; background-color: rgba(17, 24, 39, 0.5); border: 1px solid rgba(55, 65, 81, 0.7); }
  .details-title { font-size: 0.75rem; font-weight: 500; text-transform: uppercase; color: #9ca3af; margin-bottom: 0.4rem; letter-spacing: 0.025em; }
  .verification-notes { font-size: 0.8rem; margin-bottom: 0.5rem; }
  .notes-passed { color: #6ee7b7; }
  .notes-failed { color: #fca5a5; }
  .details-toggle { font-size: 0.7rem; }
  .details-summary { cursor: pointer; color: #6b7280; font-weight: 500; outline: none; transition: color 0.2s; }
  .details-summary:hover { color: #9ca3af; }
  .text-sample { white-space: pre-wrap; font-family: monospace; color: #9ca3af; background-color: rgba(31, 41, 55, 0.3); padding: 0.5rem; margin-top: 0.3rem; border-radius: 0.25rem; border: 1px solid #4b5563; max-height: 8rem; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #4b5563 #1f2937; }
  .text-sample::-webkit-scrollbar { width: 5px; }
  .text-sample::-webkit-scrollbar-track { background: #1f2937; border-radius: 2px; }
  .text-sample::-webkit-scrollbar-thumb { background-color: #4b5563; border-radius: 2px; }

  /* Empty State */
  .empty-state { text-align: center; padding: 2rem; background-color: rgba(31, 41, 55, 0.3); border-radius: 0.75rem; border: 1px dashed #4b5563; }
  .empty-state-icon { margin: auto; height: 2.5rem; width: 2.5rem; color: #6366f1; }
  .empty-state-title { margin-top: 0.8rem; font-size: 1rem; font-weight: 500; color: #d1d5db; }
  .empty-state-text { margin-top: 0.1rem; font-size: 0.8rem; color: #6b7280; }

  /* Footer */
  .page-footer { margin-top: 3rem; text-align: center; font-size: 0.7rem; color: #6b7280; border-top: 1px solid #374151; padding-top: 1rem; grid-column: 1 / -1; /* Span footer across grid */ }

  /* Spinner Animation */
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { animation: spin 1s linear infinite; }

</style>