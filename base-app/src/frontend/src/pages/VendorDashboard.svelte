<script>
    import { onMount } from "svelte";
    export let navigate;
    export let currentUser;

    let products = [];
    let loading = true;
    let error = "";

    // Form State
    let isEditing = false;
    let editingId = null;
    let formTitle = "";
    let formDesc = "";
    let formPrice = "";
    let formUrl = "";
    let formError = "";

    onMount(async () => {
        // Check Role
        if (!currentUser || !["vendor", "admin"].includes(currentUser.role)) {
            error = "Access Denied: Vendors only.";
            loading = false;
            return;
        }
        await fetchProducts();
    });

    async function fetchProducts() {
        loading = true;
        try {
            const res = await fetch("/api/vendor/products/", {
                credentials: "include",
            });
            if (res.status === 403) {
                error = "Access Denied";
                navigate("home");
                return;
            }
            if (res.ok) {
                products = await res.json();
            }
        } catch (e) {
            error = "Failed to load products";
        } finally {
            loading = false;
        }
    }

    function resetForm() {
        isEditing = false;
        editingId = null;
        formTitle = "";
        formDesc = "";
        formPrice = "";
        formUrl = "";
        formError = "";
    }

    function startEdit(product) {
        isEditing = true;
        editingId = product.id;
        formTitle = product.title;
        formDesc = product.description;
        formPrice = product.price;
        formUrl = product.file_url || "";
    }

    async function handleSubmit() {
        formError = "";
        const method = isEditing ? "PUT" : "POST";
        const url = isEditing
            ? `/api/vendor/products/${editingId}/`
            : "/api/vendor/products/";

        try {
            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    title: formTitle,
                    description: formDesc,
                    price: formPrice,
                    file_url: formUrl,
                }),
            });

            const data = await res.json();

            if (res.ok) {
                resetForm();
                await fetchProducts();
            } else {
                formError = data.error || "Failed to save product";
            }
        } catch (e) {
            formError = "Network error";
        }
    }

    async function handleDelete(id) {
        if (!confirm("Are you sure you want to delete this product?")) return;

        try {
            const res = await fetch(`/api/vendor/products/${id}/`, {
                method: "DELETE",
                credentials: "include",
            });
            if (res.ok) {
                await fetchProducts();
            } else {
                alert(
                    "Failed to delete. You can only delete your own products.",
                );
            }
        } catch (e) {
            alert("Network error");
        }
    }
</script>

<div class="container py-5">
    <h2 class="mb-4">Vendor Dashboard</h2>

    {#if loading}
        <div class="spinner-border"></div>
    {:else if error}
        <div class="alert alert-danger">{error}</div>
        <button class="btn btn-secondary" on:click={() => navigate("home")}
            >Go Home</button
        >
    {:else}
        <!-- Add/Edit Form -->
        <div class="card p-4 mb-5 bg-light">
            <h4>{isEditing ? "Edit Product" : "Add New Product"}</h4>
            {#if formError}<div class="alert alert-danger">
                    {formError}
                </div>{/if}

            <div class="mb-2">
                <label>Title</label>
                <input
                    type="text"
                    class="form-control"
                    bind:value={formTitle}
                    required
                />
            </div>
            <div class="mb-2">
                <label>Description</label>
                <textarea class="form-control" bind:value={formDesc} rows="2"
                ></textarea>
            </div>
            <div class="mb-2">
                <label>Price</label>
                <input
                    type="number"
                    step="0.01"
                    class="form-control"
                    bind:value={formPrice}
                />
            </div>
            <div class="mb-2">
                <label>Image URL</label>
                <input
                    type="url"
                    class="form-control"
                    bind:value={formUrl}
                    placeholder="https://..."
                />
            </div>

            <div class="mt-3">
                <button class="btn btn-success me-2" on:click={handleSubmit}>
                    {isEditing ? "Update Product" : "Add Product"}
                </button>
                {#if isEditing}
                    <button class="btn btn-secondary" on:click={resetForm}
                        >Cancel</button
                    >
                {/if}
            </div>
        </div>

        <!-- Product List -->
        <h4>Your Products</h4>
        <div class="list-group" data-testid="vendor-product-list">
            {#each products as product}
                <div
                    class="list-group-item d-flex justify-content-between align-items-center"
                >
                    <div>
                        <h5 class="mb-1">{product.title}</h5>
                        <p class="mb-1 text-muted small">
                            {product.description}
                        </p>
                        <span class="badge bg-primary">${product.price}</span>
                    </div>
                    <div>
                        <!-- ✅ Edit Button -->
                        <button
                            class="btn btn-sm btn-outline-primary me-2"
                            data-testid="edit-product"
                            on:click={() => startEdit(product)}
                        >
                            Edit
                        </button>
                        <!-- ✅ Delete Button -->
                        <button
                            class="btn btn-sm btn-outline-danger"
                            data-testid="delete-product"
                            on:click={() => handleDelete(product.id)}
                        >
                            Delete
                        </button>
                    </div>
                </div>
            {:else}
                <p class="text-muted">No products found. Add one above!</p>
            {/each}
        </div>
    {/if}
</div>
