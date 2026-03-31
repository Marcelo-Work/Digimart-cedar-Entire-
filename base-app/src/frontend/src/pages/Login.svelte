<script>
  import { createEventDispatcher } from 'svelte';
  export let navigate;
  
  const dispatch = createEventDispatcher();
  
  let email = '';
  let password = '';
  let errorMessage = '';
  let loading = false;

  async function handleLogin(event) {
    event.preventDefault();
    loading = true;
    errorMessage = '';
    
    try {
      const res = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });
      
      const data = await res.json();
      
      if (res.ok && data.success) {
        dispatch('login', data.user);
      } else {
        errorMessage = data.error || 'Login failed';
      }
    } catch (e) {
      console.error('Login error:', e);
      errorMessage = 'Network error. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="row justify-content-center">
  <div class="col-md-6 col-lg-4">
    <div class="card shadow-sm">
      <div class="card-body">
        <h3 class="card-title text-center mb-4">Login to DigiMart</h3>
        
        {#if errorMessage}
          <div class="alert alert-danger" role="alert" data-testid="error-message">
            {errorMessage}
          </div>
        {/if}
        
        <form on:submit={handleLogin}>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input 
              type="email" 
              class="form-control" 
              id="email"
              bind:value={email}
              data-testid="email-input"
              required
              placeholder="Enter your email"
            />
          </div>
          
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password"
              bind:value={password}
              data-testid="password-input"
              required
              placeholder="Enter your password"
            />
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary w-100"
            data-testid="login-button"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div class="text-center mt-3">
          <small>
            Don't have an account? 
            <a href="/signup" on:click|preventDefault={() => navigate('signup')}>Sign up</a>
          </small>
        </div>
      </div>
    </div>
  </div>
</div>