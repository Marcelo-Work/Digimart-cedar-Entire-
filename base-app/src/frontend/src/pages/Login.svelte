<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  export let navigate;

  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin(e) {
    e.preventDefault();
    loading = true;
    error = '';

    if (!email || !password) {
      error = 'Please enter email and password.';
      loading = false;
      return;
    }

    try {
      const res = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        dispatch('login', data.user);
      } else {
        error = data.error || 'Login failed';
      }
    } catch (err) {
      error = 'Network error. Is backend running?';
    } finally {
      loading = false;
    }
  }
</script>

<div class="row justify-content-center">
  <div class="col-md-6 col-lg-4">
    <div class="card shadow-sm">
      <div class="card-body p-4">
        <h2 class="text-center mb-4 text-primary">Login to DigiMart</h2>
        {#if error}
          <div class="alert alert-danger">{error}</div>
        {/if}
        <form on:submit={handleLogin}>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" bind:value={email} placeholder="customer@public.com" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input type="password" class="form-control" bind:value={password} placeholder="PublicPass123!" required />
          </div>
          <button type="submit" class="btn btn-primary w-100" disabled={loading}>
            {#if loading}Logging in...{:else}Login{/if}
          </button>
        </form>
        <div class="mt-3 text-center">
          <a href="/signup" on:click|preventDefault={() => navigate('signup')}>Need an account? Sign Up</a>
        </div>
      </div>
    </div>
  </div>
</div>