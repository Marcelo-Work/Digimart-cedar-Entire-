<script>
  import { onMount } from 'svelte';
  export let navigate;
  export let currentUser;
  
  let orders = [];
  let loading = true;
  let sortBy = 'created_at';
  let sortOrder = 'desc';
  let statusFilter = '';

  onMount(async () => {
    await fetchOrders();
  });

  async function fetchOrders() {
    loading = true;
    try {
      const params = new URLSearchParams();
      params.append('sort', sortBy);
      params.append('order', sortOrder);
      if (statusFilter) {
        params.append('status', statusFilter);
      }
      
      const res = await fetch(`/api/orders/?${params.toString()}`, {
        credentials: 'include'
      });
      
      if (res.ok) {
        orders = await res.json();
        console.log('Orders loaded:', orders.length);  // Debug log
      } else {
        console.error('Failed to load orders:', res.status);
        orders = [];
      }
    } catch (e) {
      console.error('Error fetching orders:', e);
      orders = [];
    } finally {
      loading = false;
    }
  }

  function handleSortChange(event) {
    sortBy = event.target.value;
    fetchOrders();
  }

  function handleOrderChange(event) {
    sortOrder = event.target.value;
    fetchOrders();
  }

  function handleFilterChange(event) {
    statusFilter = event.target.value;
    fetchOrders();
  }

  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
</script>

<div class="container py-4">
  <h2 class="mb-4">My Orders</h2>
  
  {#if loading}
    <div class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  {:else}
    <!-- Sort and Filter Controls -->
    <div class="row mb-4 g-3">
      <div class="col-md-3">
        <label class="form-label">Sort By</label>
        <select 
          class="form-select" 
          data-testid="order-sort"
          value={sortBy}
          on:change={handleSortChange}
        >
          <option value="created_at">Date</option>
          <option value="total_amount">Amount</option>
          <option value="status">Status</option>
        </select>
      </div>
      
      <div class="col-md-3">
        <label class="form-label">Order</label>
        <select 
          class="form-select"
          data-testid="order-direction"
          value={sortOrder}
          on:change={handleOrderChange}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>
      
      <div class="col-md-3">
        <label class="form-label">Filter by Status</label>
        <select 
          class="form-select"
          data-testid="order-filter"
          value={statusFilter}
          on:change={handleFilterChange}
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <div class="col-md-3 d-flex align-items-end">
        <button class="btn btn-outline-secondary w-100" on:click={fetchOrders}>
          Refresh
        </button>
      </div>
    </div>
    
    <!-- ✅ FIX: Check orders.length === 0 BEFORE rendering table -->
    {#if orders.length === 0}
      <div class="alert alert-info text-center" role="alert" data-testid="no-orders-message">
        <h5 class="alert-heading">No orders found</h5>
        <p>You haven't placed any orders yet.</p>
        <button class="btn btn-primary" on:click={() => navigate('home')}>
          Browse Products
        </button>
      </div>
    {:else}
      <!-- Orders Table - Only show if orders exist -->
      <div class="table-responsive">
        <table class="table table-striped table-hover" data-testid="order-table">
          <thead class="table-dark">
            <tr>
              <th>Order ID</th>
              <th data-testid="order-date">Date</th>
              <th data-testid="order-status">Status</th>
              <th data-testid="order-amount">Amount</th>
              <th>Items</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each orders as order}
              <tr data-testid="order-row">
                <td>
                  <strong>#{order.id}</strong>
                </td>
                <td data-testid="order-date">
                  {formatDate(order.created_at)}
                </td>
                <td data-testid="order-status">
                  <span class="badge {
                    order.status === 'completed' ? 'bg-success' : 
                    order.status === 'pending' ? 'bg-warning text-dark' : 
                    'bg-danger'
                  }">
                    {order.status}
                  </span>
                </td>
                <td data-testid="order-amount">
                  <strong>${parseFloat(order.total_amount).toFixed(2)}</strong>
                </td>
                <td>
                  {order.items ? order.items.length : 0} items
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary">
                    View Details
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {/if}
  
  <div class="mt-4">
    <button class="btn btn-secondary" on:click={() => navigate('dashboard')}>
      ← Back to Dashboard
    </button>
  </div>
</div>