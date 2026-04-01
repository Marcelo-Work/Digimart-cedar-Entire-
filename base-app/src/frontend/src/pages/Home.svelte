<script>
  import { onMount } from "svelte";
  export let navigate;
  let products = [];
  let loading = true;
  let searchQuery = "";

  function handleSearch(event) {
    event.preventDefault();
    if (searchQuery.trim()) {
      navigate('search');
      const newUrl = `/search?q=${encodeURIComponent(searchQuery.trim())}`;
      window.history.replaceState({}, "", newUrl);
    }
  }
  onMount(async () => {
    try {
      const res = await fetch("/api/products/");
      if (res.ok) products = await res.json();
    } catch (e) {
      console.error("Failed to load products", e);
    } finally {
      loading = false;
    }
  });
</script>
 <form
      class="d-flex mx-auto"
      style="max-width: 400px;"
      on:submit={handleSearch}
    >
      <input
        class="form-control me-2"
        type="search"
        placeholder="Search products..."
        aria-label="Search"
        bind:value={searchQuery}
        data-testid="search-input"
      />
      <button class="btn btn-outline-primary" type="submit">Search</button>
    </form>
<h2 class="mb-4">Featured Products</h2>

{#if loading}
  <div class="text-center"><div class="spinner-border"></div></div>
{:else if products.length === 0}
  <p>No products available.</p>
{:else}
  <div class="row row-cols-1 row-cols-md-3 g-4">
    {#each products as product}
      <div class="col">
        <div
          class="card h-100 d-flex flex-column shadow-sm"
          data-testid="product-card"
        >
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{product.title}</h5>
            <p class="card-text text-muted small">{product.description}</p>
            <h4 class="text-primary mt-auto">${product.price}</h4>
            <div class="mt-3">
              <button
                class="btn btn-primary w-100"
                on:click={() => navigate(`product?id=${product.id}`)}
                data-testid="add-to-cart-button"
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
