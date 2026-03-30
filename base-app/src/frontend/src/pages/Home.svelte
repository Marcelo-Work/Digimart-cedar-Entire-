<script>
  import { onMount } from 'svelte';
  export let navigate;
  let products = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch('/api/products/');
      if (res.ok) products = await res.json();
    } catch (e) {
      console.error("Failed to load products", e);
    } finally {
      loading = false;
    }
  });
</script>

<h2 class="mb-4">Featured Products</h2>

{#if loading}
  <div class="text-center"><div class="spinner-border"></div></div>
{:else if products.length === 0}
  <p>No products available.</p>
{:else}
  <div class="row row-cols-1 row-cols-md-3 g-4">
    {#each products as product}
      <div class="col">
        <div class="card h-100 d-flex flex-column shadow-sm">
        
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{product.title}</h5>
            <p class="card-text text-muted small">{product.description}</p>
            <h4 class="text-primary mt-auto">${product.price}</h4>
            <div class="mt-3">
              <button 
                class="btn btn-primary w-100" 
                on:click={() => navigate('product')}
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