<script>
  import { onMount } from 'svelte';
  export let navigate;
  export let currentUser;
  
  let orders = [];
  let loading = true;

  if (!currentUser) {
    setTimeout(() => navigate('login'), 0);
  }

  onMount(async () => {

    if (!currentUser) {
      navigate('login');
      return; 
    }

    try {
      const ordersRes = await fetch('/api/orders/');
      if (ordersRes.ok) {
        orders = await ordersRes.json();
      }
    } catch (e) {
      console.error("Error loading orders", e);
    } finally {
      loading = false;
    }
  });
</script>
{#if !currentUser}
  <div class="text-center mt-5">
    <div class="spinner-border text-warning"></div>
    <p class="mt-2">Securing access...</p>
  </div>
{:else if loading}
  <div class="text-center"><div class="spinner-border"></div></div>
{:else}
  <h2>Dashboard</h2>
  <div class="card mb-4 shadow-sm">
    <div class="card-body">
      <h4 class="card-title text-primary">Welcome, {currentUser.username || currentUser.email}!</h4>
      <hr>
      <p><strong>Email:</strong> {currentUser.email}</p>
      <p><strong>Role:</strong> <span class="badge bg-info">{currentUser.role}</span></p>
    </div>
  </div>

  <h3>Order History</h3>
  {#if orders.length === 0}
    <div class="alert alert-info">No orders found.</div>
  {:else}
    <div class="list-group shadow-sm">
      {#each orders as order}
        <div class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <strong>Order #{order.id}</strong>
            <small class="d-block text-muted">{order.status}</small>
          </div>
          <span class="badge bg-primary rounded-pill">${order.total_amount}</span>
        </div>
      {/each}
    </div>
  {/if}
{/if}