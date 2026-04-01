<script>
    export let product;
    export let navigate;
</script>

<div class="card h-100 d-flex flex-column shadow-sm" data-testid="product-card">
    <div class="card-body d-flex flex-column">
        <h5 class="card-title">{product.title}</h5>
        <p class="card-text text-muted small">{product.description}</p>
        <h4 class="text-primary mt-auto">${product.price}</h4>
        <div class="mt-3">
            <button
                class="btn btn-primary w-100"
                on:click={() => navigate(`product?id=${product.id}`)}
                data-testid="view-details-button"
            >
                View Details
            </button>
        </div>
    </div>
</div>
