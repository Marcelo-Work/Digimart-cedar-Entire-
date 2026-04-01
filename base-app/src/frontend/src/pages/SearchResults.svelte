<script>
  import { onMount } from 'svelte';
  export let navigate;
  export let currentUser;

  let products = [];
  let loading = true;
  let query = '';

  async function performSearch() {
    loading = true;
    // Get query param from URL
    const urlParams = new URLSearchParams(window.location.search);
    query = urlParams.get('q') || '';

    if (!query) {
      products = [];
      loading = false;
      return;
    }

    try {
      const res = await fetch(`/api/products/search/?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        products = await res.json();
      } else {
        products = [];
      }
    } catch (e) {
      console.error("Search failed", e);
      products = [];
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    performSearch();
  });
</script>

<div class="container py-4">
  <h2 class="mb-4">{query ? `Search Results for "${query}"` : 'Search Products'}</h2>

  {#if loading}
    <div class="text-center"><div class="spinner-border"></div></div>
    
  {:else if products.length === 0}
    <div class="alert alert-info">
      {query ? `No products found matching "${query}".` : "Enter a search term above."}
    </div>
    {#if query}
      <button class="btn btn-secondary" on:click={() => navigate('home')}>Back to Home</button>
    {/if}
    
  {:else}
    <div class="row row-cols-1 row-cols-md-3 g-4">
      {#each products as product}
        <div class="col">
          <div class="card h-100 shadow-sm" data-testid="product-card">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">{product.title}</h5>
              <p class="card-text text-muted small flex-grow-1">{product.description}</p>
              <h4 class="text-primary">${product.price}</h4>
              <div class="mt-3">
                <button 
                  class="btn btn-primary w-100" 
                  data-testid="add-to-cart-button"
                  on:click={() => navigate(`product?id=${product.id}`)}
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>