<script>
  import { onMount } from 'svelte';
  export let navigate;
  let products = [];
  let searchQuery = '';
  let loading = true;

  async function fetchProducts(query = '') {
    loading = true;
    try {
      const url = query 
        ? `/api/products/search/?q=${encodeURIComponent(query)}` 
        : '/api/products/';
      const res = await fetch(url);
      if (res.ok) products = await res.json();
    } catch (e) {
      console.error("Fetch error:", e);
      products = [];
    } finally {
      loading = false;
    }
  }

  function handleSearch() {
    fetchProducts(searchQuery);
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') handleSearch();
  }

  onMount(() => fetchProducts());
</script>

<h2 class="mb-4">Featured Products</h2>

<!-- TASK 1: Search Bar -->
<div class="input-group mb-4">
  <input 
    type="text" 
    class="form-control" 
    placeholder="Search products..." 
    bind:value={searchQuery}
    data-testid="search-input"
    on:keydown={handleKeyDown}
  />
  <button class="btn btn-primary" on:click={handleSearch} data-testid="search-button">
    Search
  </button>
</div>

{#if loading}
  <div class="text-center"><div class="spinner-border"></div></div>
{:else if products.length === 0}
  <p class="text-center">No products found.</p>
{:else}
  <div class="row row-cols-1 row-cols-md-3 g-4">
    {#each products as product}
      <div class="col">
        <div class="card h-100 d-flex flex-column shadow-sm" data-testid="product-card">
          <img src="{product.file_url || 'https://via.placeholder.com/300'}" class="card-img-top" alt="{product.title}" style="height: 200px; object-fit: cover;">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{product.title}</h5>
            <p class="card-text text-muted small flex-grow-1">{product.description}</p>
            <h4 class="text-primary mt-auto">${product.price}</h4>
            <button class="btn btn-primary w-100 mt-3" on:click={() => navigate('product')}>View Details</button>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}