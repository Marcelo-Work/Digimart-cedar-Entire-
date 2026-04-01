<script>
  import { onMount } from "svelte";
  import Header from "./components/Header.svelte";
  import Footer from "./components/Footer.svelte";
  import Home from "./pages/Home.svelte";
  import Login from "./pages/Login.svelte";
  import Signup from "./pages/Signup.svelte";
  import ProductDetail from "./pages/ProductDetail.svelte";
  import Cart from "./pages/Cart.svelte";
  import Dashboard from "./pages/Dashboard.svelte";
  import Profile from "./pages/Profile.svelte";
  import Orders from "./pages/Orders.svelte";
  import Support from "./pages/Support.svelte";
  import SearchResults from "./pages/SearchResults.svelte";
  import VendorDashboard from "./pages/VendorDashboard.svelte";
  import OrderConfirmation from "./pages/OrderConfirmation.svelte";
  import EmailLogs from "./pages/EmailLogs.svelte";
  import GuestCheckout from "./pages/GuestCheckout.svelte";
  import GuestTrackOrder from "./pages/GuestTrackOrder.svelte";
  let page = "home";
  let currentUser = null;
  let loading = true;

  // Helper to extract clean page name from path (ignores query params)
  function getPageFromPath() {
    const path = window.location.pathname.slice(1) || "home";
    return path.split("?")[0];
  }

  onMount(async () => {
    // 1. Set initial page on load
    page = getPageFromPath();

    // 2. Fetch User Profile
    try {
      const res = await fetch("/api/auth/profile/", { credentials: "include" });
      if (res.ok) {
        currentUser = await res.json();
      } else {
        currentUser = null;
      }
    } catch (e) {
      currentUser = null;
    }

    loading = false;

    // 3. Handle Browser Back/Forward Buttons
    window.addEventListener("popstate", () => {
      page = getPageFromPath();
    });
  });

  function navigate(newPage) {
    page = newPage.split("?")[0];

    // Update browser URL
    window.history.pushState({}, "", `/${newPage === "home" ? "" : newPage}`);
  }

  function handleLoginEvent(event) {
    currentUser = event.detail;
    navigate("dashboard");
  }

  function handleLogout() {
    fetch("/api/auth/logout/", { method: "POST", credentials: "include" })
      .then(() => {
        currentUser = null;
        navigate("home");
      })
      .catch(() => {
        currentUser = null;
        navigate("home");
      });
  }

  // Protect Routes
  $: if (
    !loading &&
    !currentUser &&
    (page === "dashboard" ||
      page === "profile" ||
      page === "orders")
  ) {
    navigate("login");
  }
</script>

<div class="d-flex flex-column min-vh-100">
  <Header {currentUser} {navigate} onLogout={handleLogout} />

  <main class="flex-grow-1 container py-4">
    {#if loading}
      <div class="text-center">
        <div class="spinner-border text-primary"></div>
      </div>
    {:else if page === "home"}
      <Home {navigate} />
    {:else if page === "login"}
      <Login {navigate} on:login={handleLoginEvent} />
    {:else if page === "signup"}
      <Signup {navigate} on:login={handleLoginEvent} />
    {:else if page.startsWith("product")}
      <ProductDetail {navigate} {currentUser} />
    {:else if page === "cart"}
        <Cart {navigate} {currentUser} />

    {:else if page === "dashboard"}
      {#if currentUser}
        <Dashboard {navigate} {currentUser} />
      {:else}
        <div class="alert alert-warning">Access Denied.</div>
      {/if}
    {:else if page === "profile"}
      {#if currentUser}
        <Profile {navigate} {currentUser} />
      {:else}
        <div class="alert alert-warning">Please login.</div>
      {/if}
    {:else if page === "orders"}
      {#if currentUser}
        <Orders {navigate} {currentUser} />
      {:else}
        <div class="alert alert-warning">Please login to view orders.</div>
      {/if}
    {:else if page.startsWith("search")}
      <!-- ✅ This block will now execute when navigate('search?q=...') is called -->
      <SearchResults {navigate} {currentUser} />
    {:else if page === "support"}
      <Support {navigate} {currentUser} />
    {:else if page === "order-confirmation"}
      <OrderConfirmation {navigate} />
    {:else if page === "email-logs"}
      <!-- We will create this next for Task 8 verification -->
      <EmailLogs {navigate} />
    {:else if page === "guest/checkout"}
      <GuestCheckout {navigate} />
    {:else if page.startsWith("guest/success") || page.startsWith("guest/track")}
      <GuestTrackOrder {navigate} />
    {:else if page === "vendor/dashboard"}
      {#if currentUser && (currentUser.role === "vendor" || currentUser.role === "admin")}
        <VendorDashboard {navigate} {currentUser} />
      {:else}
        <div class="alert alert-danger">Access Denied: Vendors only.</div>
        <button class="btn btn-secondary" on:click={() => navigate("home")}
          >Go Home</button
        >
      {/if}
    {:else}
      <div class="text-center">
        <h2>404 - Page Not Found</h2>
        <button class="btn btn-primary" on:click={() => navigate("home")}
          >Go Home</button
        >
      </div>
    {/if}
  </main>

  <Footer />
</div>
