<script>
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();
  export let navigate;

  let username = "";
  let email = "";
  let password = "";
  let confirmPassword = "";
  let error = "";
  let loading = false;

  async function handleSignup(e) {
    e.preventDefault();
    loading = true;
    error = "";

    if (!username || !email || !password) {
      error = "All fields are required.";
      loading = false;
      return;
    }

    if (password !== confirmPassword) {
      error = "Passwords do not match.";
      loading = false;
      return;
    }

    try {
      const res = await fetch("/api/auth/signup/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        dispatch("login", data.user);
      } else {
        if (data.username) error = "Username: " + data.username[0];
        else if (data.email) error = "Email: " + data.email[0];
        else if (data.password) error = "Password: " + data.password[0];
        else error = data.error || "Signup failed.";
      }
    } catch (err) {
      error = "Network error.";
    } finally {
      loading = false;
    }
  }
</script>

<div class="row justify-content-center">
  <div class="col-md-6 col-lg-4">
    <div class="card shadow-sm">
      <div class="card-body p-4">
        <h2 class="text-center mb-4 text-success">Create Account</h2>
        {#if error}
          <div class="alert alert-danger">{error}</div>
        {/if}
        <form on:submit={handleSignup}>
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input
              type="text"
              class="form-control"
              bind:value={username}
              data-testid="username-input" 
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input
              type="email"
              class="form-control"
              data-testid="email-input" 
              bind:value={email}
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              type="password"
              class="form-control"
              bind:value={password}
              data-testid="password-input" 
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Confirm Password</label>
            <input
              type="password"
              class="form-control"
              bind:value={confirmPassword}
              data-testid="confirmPassword-input" 
              required
            />
          </div>
          <button
            type="submit"
            class="btn btn-success w-100"
            data-testid="signup-button"
            disabled={loading}
          >
            {#if loading}Creating...{:else}Sign Up{/if}
          </button>
        </form>
        <div class="mt-3 text-center">
          <a href="/login" on:click|preventDefault={() => navigate("login")}
            >Already have an account? Login</a
          >
        </div>
      </div>
    </div>
  </div>
</div>
