<script>
  import { createEventDispatcher } from 'svelte';
  
  export let currentUser = null; 
  export let navigate = () => {}; 
  
  const dispatch = createEventDispatcher();

  function handleLogoutClick() {
    
    dispatch('logout', {});
    
    window.location.href = '/'; 
  }
</script>

<nav class="navbar navbar-expand-lg navbar-dark mb-4" style="background-color: #4f46e5;">
  <div class="container">
    <a class="navbar-brand fw-bold" href="/" on:click|preventDefault={() => navigate('home')}>
      🛒 DigiMart
    </a>
    
    <!-- Toggler for mobile -->
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    
    <!-- Nav Links -->
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a class="nav-link" href="/" on:click|preventDefault={() => navigate('home')}>Home</a>
        </li>
        
        {#if currentUser}
          <li class="nav-item">
            <a class="nav-link" href="/dashboard" on:click|preventDefault={() => navigate('dashboard')}>Dashboard</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/cart" on:click|preventDefault={() => navigate('cart')}>Cart</a>
          </li>
        {/if}
      </ul>
      
      <!-- Right Side: User Info & Auth Buttons -->
      <ul class="navbar-nav">
        {#if currentUser}
          <!-- Logged In View -->
          <li class="nav-item d-flex align-items-center me-3">
            <span class="navbar-text text-white">
              Welcome, <strong>{currentUser.username || currentUser.email || 'User'}</strong>
            </span>
          </li>
          <li class="nav-item">
            <button class="btn btn-outline-light btn-sm" on:click={handleLogoutClick}>
              Logout
            </button>
          </li>
        {:else}
          <!-- Logged Out View -->
          <li class="nav-item">
            <a class="btn btn-outline-light btn-sm me-2" href="/login" on:click|preventDefault={() => navigate('login')}>
              Login
            </a>
          </li>
          <li class="nav-item">
            <a class="btn btn-light btn-sm" href="/signup" on:click|preventDefault={() => navigate('signup')}>
              Sign Up
            </a>
          </li>
        {/if}
      </ul>
    </div>
  </div>
</nav>