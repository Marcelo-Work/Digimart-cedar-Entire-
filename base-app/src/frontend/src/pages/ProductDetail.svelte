<script>
  import { onMount } from 'svelte';
  export let navigate;
  
  let product = null;
  let loading = true;
  let message = '';
  
  onMount(async () => {
    const productId = window.location.pathname.split('/').pop();
    try {
      const res = await fetch(`/api/products/${productId}/`);
      product = await res.json();
    } catch (e) { message = 'Product not found'; }
    loading = false;
  });
  
  async function addToCart() {
    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id })
      });
      if (res.ok) { message = 'Added to cart!'; setTimeout(() => navigate('cart'), 1000); }
    } catch (e) { message = 'Please login first'; navigate('login'); }
  }
</script>

{#if loading}
  <div class="text-center py-5"><div class="spinner-border"></div></div>
{:else if product}
  <div class="row">
    <div class="col-md-8">
      <h1 data-testid="product-title">{product.title}</h1>
      <p class="lead">{product.description}</p>
      <h2 class="text-primary">${product.price}</h2>
      {#if message}<div class="alert alert-info mt-3">{message}</div>{/if}
      <button class="btn btn-primary btn-lg mt-3" on:click={addToCart}>Add to Cart</button>
    </div>
  </div>
{:else}
  <div class="alert alert-danger">Product not found</div>
{/if}