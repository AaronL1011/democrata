<script lang="ts">
  import { api } from '$lib/api/client';

  let selectedFile: File | null = $state(null);
  let title = $state('');
  let documentType = $state('other');
  let uploading = $state(false);
  let result: { success: boolean; message: string; jobId?: string } | null = $state(null);

  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      selectedFile = input.files[0];
      if (!title) {
        title = selectedFile.name.replace(/\.[^/.]+$/, '');
      }
    }
  }

  async function handleUpload() {
    if (!selectedFile) return;

    uploading = true;
    result = null;

    try {
      const response = await api.upload(selectedFile, {
        title: title || selectedFile.name,
        document_type: documentType,
        source: 'manual',
      });

      result = {
        success: true,
        message: `Upload successful! Job ID: ${response.job_id}`,
        jobId: response.job_id,
      };
      
      selectedFile = null;
      title = '';
    } catch (error) {
      result = {
        success: false,
        message: error instanceof Error ? error.message : 'Upload failed',
      };
    } finally {
      uploading = false;
    }
  }
</script>

<main>
  <header>
    <h1>Upload Document</h1>
    <p class="tagline">Upload PDF or text files for ingestion</p>
  </header>

  <section class="upload-section">
    <form onsubmit={(e) => { e.preventDefault(); handleUpload(); }}>
      <div class="form-group">
        <label for="file">Select File</label>
        <input
          type="file"
          id="file"
          accept=".pdf,.txt,.md,.json,.csv"
          onchange={handleFileSelect}
          disabled={uploading}
        />
        {#if selectedFile}
          <p class="file-info">Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</p>
        {/if}
      </div>

      <div class="form-group">
        <label for="title">Document Title</label>
        <input
          type="text"
          id="title"
          bind:value={title}
          placeholder="Enter document title"
          disabled={uploading}
        />
      </div>

      <div class="form-group">
        <label for="docType">Document Type</label>
        <select id="docType" bind:value={documentType} disabled={uploading}>
          <option value="other">Other</option>
          <option value="bill">Bill</option>
          <option value="hansard">Hansard</option>
          <option value="report">Report</option>
          <option value="vote">Vote</option>
          <option value="member">Member</option>
        </select>
      </div>

      <button type="submit" disabled={!selectedFile || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </form>

    {#if result}
      <div class="result" class:success={result.success} class:error={!result.success}>
        {result.message}
      </div>
    {/if}
  </section>

  <footer>
    <a href="/">Back to Query</a>
  </footer>
</main>

<style>
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    padding: 2rem;
    text-align: center;
    background: white;
    border-bottom: 1px solid #e5e7eb;
  }

  header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.5rem;
  }

  .tagline {
    color: #6b7280;
    margin: 0;
  }

  .upload-section {
    flex: 1;
    padding: 2rem;
    max-width: 32rem;
    width: 100%;
    margin: 0 auto;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    font-weight: 500;
    color: #374151;
  }

  input[type="text"],
  select {
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
  }

  input[type="file"] {
    padding: 0.5rem;
    border: 2px dashed #d1d5db;
    border-radius: 0.375rem;
    background: #f9fafb;
    cursor: pointer;
  }

  input[type="file"]:hover {
    border-color: #9ca3af;
  }

  .file-info {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
  }

  button {
    padding: 0.75rem 1.5rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
  }

  button:hover:not(:disabled) {
    background: #1d4ed8;
  }

  button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }

  .result {
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 0.375rem;
  }

  .result.success {
    background: #d1fae5;
    color: #065f46;
  }

  .result.error {
    background: #fee2e2;
    color: #991b1b;
  }

  footer {
    padding: 1.5rem;
    text-align: center;
    border-top: 1px solid #e5e7eb;
    background: white;
  }

  footer a {
    color: #2563eb;
    text-decoration: none;
  }

  footer a:hover {
    text-decoration: underline;
  }
</style>
