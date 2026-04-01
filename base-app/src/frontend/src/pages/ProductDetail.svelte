<script>
  import { onMount } from 'svelte';
  export let navigate;

  let product = null;
  let loading = true;
  let error = '';
  let productId = null;

  onMount(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    productId = urlParams.get('id');

    if (!productId) {
      error = 'No product ID specified.';
      loading = false;
      return;
    }

    await fetchProduct();
  });

  async function fetchProduct() {
    loading = true;
    try {
      const res = await fetch(`/api/products/${productId}/`);
      if (res.ok) {
        product = await res.json();
      } else {
        error = 'Product not found.';
      }
    } catch (e) {
      error = 'Failed to load product.';
    } finally {
      loading = false;
    }
  }

  async function addToCart() {
    if (!product) return;
    
    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ 
          product_id: product.id,
          quantity: 1 
        })
      });

      const data = await res.json();

      if (res.ok) {
        alert('✅ Added to cart successfully!');
        // Optional: Navigate to cart immediately
        // navigate('cart');
      } else {
        // Show specific error from backend
        alert('❌ Failed to add to cart: ' + (data.error || 'Unknown error'));
      }
    } catch (e) {
      console.error(e);
      alert('❌ Network error. Is the backend running?');
    }
  }
</script>

<div class="container py-5">
  {#if loading}
    <div class="text-center"><div class="spinner-border"></div></div>
  {:else if error}
    <div class="alert alert-danger">{error}</div>
    <button class="btn btn-secondary" on:click={() => navigate('home')}>Back to Home</button>
  {:else if product}
    <div class="row">
      <div class="col-md-6">
        <div class="bg-light d-flex align-items-center justify-content-center" style="height: 300px;">
          <span class="text-muted">Product Image</span>
        </div>
      </div>
      <div class="col-md-6">
        <h1 class="display-4">{product.title}</h1>
        <p class="lead text-muted">{product.description}</p>
        <h2 class="text-primary my-4">${product.price}</h2>
        <button class="btn btn-primary btn-lg" on:click={addToCart} data-testid="add-to-cart-button">
          Add to Cart
        </button>
      </div>
    </div>
  {/if}
</div>