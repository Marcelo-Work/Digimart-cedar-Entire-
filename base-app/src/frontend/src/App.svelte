<script>
  import { onMount } from 'svelte';
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import Home from './pages/Home.svelte';
  import Login from './pages/Login.svelte';
  import Signup from './pages/Signup.svelte';
  import ProductDetail from './pages/ProductDetail.svelte';
  import Cart from './pages/Cart.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  
  let page = 'home';
  let currentUser = null;
  let loading = true;

  onMount(async () => {
    const path = window.location.pathname.slice(1) || 'home';
    page = path;

    try {
      const res = await fetch('/api/auth/profile/');
      if (res.ok) {
        currentUser = await res.json();
      }
    } catch (e) {}
    
    loading = false;

    window.addEventListener('popstate', () => {
      page = window.location.pathname.slice(1) || 'home';
    });
  });
  
  function navigate(newPage) {
    page = newPage;
    window.history.pushState({}, '', `/${newPage === 'home' ? '' : newPage}`);
  }

  function handleLoginEvent(event) {
    currentUser = event.detail;
    navigate('dashboard');
  }

  function handleLogout() {
    fetch('/api/auth/logout/', { 
      method: 'POST',
      credentials: 'include' 
    })
    .then(res => {
      currentUser = null;
      navigate('home');
    setTimeout(() => {
        if (page !== 'home') navigate('home');
    }, 100);
  })
  .catch(err => {
    currentUser = null;
    navigate('home');
  });
  }

 
  $: if (!loading && !currentUser && (page === 'dashboard' || page === 'cart')) {
    navigate('login');
  }
</script>

<div class="d-flex flex-column min-vh-100">
  <Header {currentUser} {navigate} onLogout={handleLogout} />
  
  <main class="flex-grow-1 container py-4">
    {#if loading}
      <div class="text-center"><div class="spinner-border text-primary"></div></div>
    {:else}
      {#if page === 'home'}
        <Home {navigate} />
      {:else if page === 'login'}
        <Login {navigate} on:login={handleLoginEvent} />
      {:else if page === 'signup'}
        <Signup {navigate} on:login={handleLoginEvent} />
      {:else if page === 'product'}
        <ProductDetail {navigate} />
      {:else if page === 'cart'}
        {#if currentUser}<Cart {navigate} />{:else}<div>Please login.</div>{/if}
      {:else if page === 'dashboard'}
        {#if currentUser}
          <Dashboard {navigate} {currentUser} />
        {:else}
          <div class="alert alert-warning">Access Denied. Redirecting...</div>
        {/if}
      {/if}
    {/if}
  </main>
  <Footer />
</div>