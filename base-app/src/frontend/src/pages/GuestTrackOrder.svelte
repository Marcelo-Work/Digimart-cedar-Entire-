<script>
    import { onMount } from "svelte";
    export let navigate;
    let order = null;
    let loading = true;
    let error = "";

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");

        // Or get token from URL path if routed that way
        const pathToken = window.location.pathname.split("/").pop();
        const finalToken = token || pathToken;

        if (!finalToken) {
            error = "No order token provided";
            loading = false;
            return;
        }

        try {
            const res = await fetch(`/api/guest/order/${finalToken}/`);
            if (res.ok) {
                order = await res.json();
            } else {
                error = "Order not found or invalid token";
            }
        } catch (e) {
            error = "Network error";
        } finally {
            loading = false;
        }
    });
</script>

<div class="container py-5">
    {#if loading}
        <div class="spinner-border"></div>
    {:else if error}
        <div class="alert alert-danger">{error}</div>
        <button class="btn btn-secondary" on:click={() => navigate("home")}
            >Go Home</button
        >
    {:else if order}
        <!-- ✅ ORDER LOOKUP TEST ID -->
        <div class="alert alert-success" data-testid="order-lookup">
            <h1>Order Status</h1>
            <h3>Order #{order.id}</h3>
            <p>Status: <strong>{order.status}</strong></p>
            <p>Total: ${order.total_amount}</p>
            <p>Email: {order.guest_email}</p>

            <h4 class="mt-4">Items:</h4>
            <ul>
                {#each order.items as item}
                    <li>{item.product} x {item.quantity}</li>
                {/each}
            </ul>

            <div class="mt-4 p-3 bg-light rounded">
                <h5>Want to track future orders easily?</h5>
                <button
                    class="btn btn-primary"
                    data-testid="create-account"
                    on:click={() =>
                        navigate(`signup?email=${order.guest_email}`)}
                >
                    Create Account
                </button>
            </div>
        </div>
    {/if}
</div>
