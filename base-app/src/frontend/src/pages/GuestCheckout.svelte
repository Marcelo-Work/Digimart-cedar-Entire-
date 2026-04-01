<script>
    export let navigate;
    let email = "";
    let name = "",
        address = "",
        city = "",
        zip = "";
    let error = "";
    let loading = false;
    let cartItems = []; // Populate this from localStorage or context

    async function handleGuestCheckout() {
        error = "";
        loading = true;

        // Simple Validation
        if (!email.includes("@")) {
            error = "Valid email required";
            loading = false;
            return;
        }
        if (!name || !address) {
            error = "All fields required";
            loading = false;
            return;
        }

        try {
            // Get cart from localStorage (since no user session)
            const storedCart = localStorage.getItem("cart");
            const items = storedCart ? JSON.parse(storedCart) : [];

            if (items.length === 0) {
                error = "Cart is empty";
                loading = false;
                return;
            }

            const res = await fetch("/api/guest/checkout/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email,
                    billing_name: name,
                    billing_address: address,
                    billing_city: city,
                    billing_zip: zip,
                    items,
                }),
            });

            const data = await res.json();

            if (res.ok) {
                localStorage.removeItem("cart"); // Clear cart
                navigate(`guest/success?token=${data.access_token}&email=${data.guest_email}`);
            } else {
                error = data.error || "Failed to place order";
            }
        } catch (e) {
            error = "Network error";
        } finally {
            loading = false;
        }
    }
</script>

<div class="container py-5">
    <h2>Checkout as Guest</h2>

    {#if error}
        <div class="alert alert-danger" data-testid="guest-error">{error}</div>
    {/if}

    <!-- ✅ GUEST FORM TEST ID -->
    <form
        on:submit|preventDefault={handleGuestCheckout}
        data-testid="guest-form"
        class="mt-4"
    >
        <div class="mb-3">
            <label>Email Address (for order updates)</label>
            <input
                type="email"
                class="form-control"
                bind:value={email}
                required
                placeholder="you@example.com"
            />
        </div>

        <div class="mb-3">
            <label>Full Name</label>
            <input
                type="text"
                class="form-control"
                bind:value={name}
                required
            />
        </div>

        <div class="mb-3">
            <label>Address</label>
            <textarea class="form-control" bind:value={address} required
            ></textarea>
        </div>

        <div class="row">
            <div class="col">
                <input
                    type="text"
                    class="form-control"
                    bind:value={city}
                    placeholder="City"
                    required
                />
            </div>
            <div class="col">
                <input
                    type="text"
                    class="form-control"
                    bind:value={zip}
                    placeholder="ZIP"
                    required
                />
            </div>
        </div>

        <button
            type="submit"
            class="btn btn-success btn-lg mt-4"
            disabled={loading}
        >
            {#if loading}Processing...{:else}Place Order{/if}
        </button>
    </form>

    <div class="mt-3">
        <p>Already have an account? <a href="/login">Login here</a></p>
        <!-- ✅ CREATE ACCOUNT OPTION TEST ID -->
        <button
            class="btn btn-outline-primary btn-sm"
            on:click={() => navigate("signup")}
            data-testid="create-account"
        >
            Create an Account instead
        </button>
    </div>
</div>
