<script>
  import { createEventDispatcher } from "svelte";

  export let currentUser = null;
  export let navigate = () => {};
  let loggingOut = false;
  const dispatch = createEventDispatcher();

    async function handleLogout() {
      loggingOut = true;
      
      try {
        // 1. Call Backend Logout
        const res = await fetch("/api/auth/logout/", {
          method: "POST",
          credentials: "include", // Important to send the session cookie so backend knows who to log out
          headers: {
            "Content-Type": "application/json",
            // If your CSRF protection is strict on POST, you might need the token here
            // 'X-CSRFToken': getCookie('csrftoken')
          },
        });

        // 2. Clear Frontend State
        currentUser = null; // Reset user variable

        // 3. Clear LocalStorage (Cart, Drafts, etc.)
        localStorage.clear();

        // 4. Force Delete Cookies via JavaScript (Safety Net)
        // This ensures deletion even if the backend header fails slightly
        document.cookie.split(";").forEach(function (c) {
          document.cookie = c
            .replace(/^ +/, "")
            .replace(
              /=.*/,
              "=;expires=" + new Date().toUTCString() + ";path=/",
            );
        });

        // 5. Redirect to Home
        navigate("home");

        // 6. Force Reload (Optional but recommended to clear any in-memory caches)
        // window.location.href = '/';
      } catch (e) {
        console.error("Logout error:", e);
        // Even on error, clear local state to prevent stuck UI
        currentUser = null;
        localStorage.clear();
        navigate("home");
      } finally {
        loggingOut = false;
      }
    }

</script>

<nav
  class="navbar navbar-expand-lg navbar-dark mb-4"
  style="background-color: #4f46e5;"
>
  <div class="container">
    <a
      class="navbar-brand fw-bold"
      href="/"
      on:click|preventDefault={() => navigate("home")}
    >
      🛒 DigiMart
    </a>

    <!-- Toggler for mobile -->
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <!-- Nav Links -->

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a
            class="nav-link"
            href="/"
            on:click|preventDefault={() => navigate("home")}>Home</a
          >
        </li>
        <li class="nav-item">
            <a
              class="nav-link"
              href="/cart"
              on:click|preventDefault={() => navigate("cart")}>Cart</a
            >
          </li>
        {#if currentUser && currentUser.role === "vendor"}
          <a
            class="nav-link"
            href="/vendor/dashboard"
            on:click|preventDefault={() => navigate("vendor/dashboard")}
            >Vendor Dashboard</a
          >
        {/if}
        {#if currentUser}
          <li class="nav-item">
            <a
              class="nav-link"
              href="/dashboard"
              on:click|preventDefault={() => navigate("dashboard")}>Dashboard</a
            >
          </li>
          <a
            class="nav-link"
            href="/orders"
            on:click|preventDefault={() => navigate("orders")}
          >
            Orders
          </a>
          
          <li class="nav-item">
            <a
              class="nav-link"
              href="/support"
              on:click|preventDefault={() => navigate("support")}>Support</a
            >
          </li>
        {/if}
        {#if currentUser}
          <li class="nav-item">
            <a
              class="nav-link"
              href="/profile"
              on:click|preventDefault={() => navigate("profile")}
            >
              Profile
            </a>
          </li>
        {/if}
      </ul>

      <!-- Right Side: User Info & Auth Buttons -->
      <ul class="navbar-nav">
        {#if currentUser}
          <!-- Logged In View -->
          <li class="nav-item d-flex align-items-center me-3">
            <span class="navbar-text text-white">
              Welcome, <strong
                >{currentUser.username || currentUser.email || "User"}</strong
              >
            </span>
          </li>
          <li class="nav-item">
            <button
              class="btn btn-outline-light btn-sm"
              on:click={handleLogout}
            >
              {#if loggingOut}Logging out...{:else}Logout{/if}
            </button>
          </li>
        {:else}
          <!-- Logged Out View -->
          <li class="nav-item">
            <a
              class="btn btn-outline-light btn-sm me-2"
              href="/login"
              on:click|preventDefault={() => navigate("login")}
            >
              Login
            </a>
          </li>
          <li class="nav-item">
            <a
              class="btn btn-light btn-sm"
              href="/signup"
              on:click|preventDefault={() => navigate("signup")}
            >
              Sign Up
            </a>
          </li>
        {/if}
      </ul>
    </div>
  </div>
</nav>
