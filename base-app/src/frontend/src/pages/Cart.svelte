<script>
  import { onMount } from 'svelte';
  export let navigate;
  
  let cart = { items: [] };
  let loading = true;
  
  onMount(async () => {
    try {
      const res = await fetch('/api/cart/');
      if (res.ok) cart = await res.json();
    } catch (e) { navigate('login'); }
    loading = false;
  });
  
  async function checkout() {
    try {
      const res = await fetch('/api/orders/', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (res.ok) { alert('Order placed!'); navigate('dashboard'); }
    } catch (e) { alert('Checkout failed'); }
  }
</script>

<h2>Shopping Cart</h2>
{#if loading}
  <div class="spinner-border"></div>
{:else if cart.items.length === 0}
  <p>Your cart is empty</p>
  <a href="/" class="btn btn-primary">Browse Products</a>
{:else}
  <div class="list-group mb-3">{#each cart.items as item}<div class="list-group-item">Product ID: {item.product_id} - Qty: {item.quantity}</div>{/each}</div>
  <button class="btn btn-success btn-lg" on:click={checkout}>Checkout</button>
{/if}