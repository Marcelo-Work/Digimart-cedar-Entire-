<script>
    import { onMount } from "svelte";
    export let navigate;
    export let currentUser;

    let logs = [];
    let loading = true;

    onMount(async () => {
        // Optional: Restrict to admin/staff if desired, but open for testing
        try {
            const res = await fetch("/api/email-logs/", {
                credentials: "include",
            });
            if (res.ok) {
                logs = await res.json();
            }
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="container py-5">
    <h2>Email Notification Logs</h2>
    <p class="text-muted">Real-time record of all transactional emails sent.</p>

    {#if loading}
        <div class="spinner-border"></div>
    {:else if logs.length === 0}
        <div class="alert alert-info">No email logs found yet.</div>
    {:else}
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Recipient</th>
                        <th>Subject</th>
                        <th>Status</th>
                        <th>Order ID</th>
                        <th>Error Details</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {#each logs as log}
                        <!-- ✅ CRITICAL TEST ID FOR TASK 8 -->
                        <tr data-testid="email-log-entry">
                            <td>{log.id}</td>
                            <td>{log.recipient_email}</td>
                            <td>{log.subject}</td>
                            <td>
                                {#if log.status === "sent"}
                                    <span class="badge bg-success">Sent</span>
                                {:else if log.status === "failed"}
                                    <span class="badge bg-danger">Failed</span>
                                {:else}
                                    <span class="badge bg-warning text-dark"
                                        >Pending</span
                                    >
                                {/if}
                            </td>
                            <td>{log.related_order_id || "-"}</td>
                            <td class="text-danger small">
                                {#if log.error_message}
                                    <span data-testid="email-error-log"
                                        >{log.error_message}</span
                                    >
                                {:else}
                                    -
                                {/if}
                            </td>
                            <td class="text-muted small"
                                >{new Date(log.created_at).toLocaleString()}</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}

    <button class="btn btn-secondary mt-3" on:click={() => navigate("home")}
        >Back to Home</button
    >
</div>
