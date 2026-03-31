<script>
    let name = "";
    let email = "";
    let subject = "";
    let message = "";

    let errors = {};
    let successMessage = "";
    let submitting = false;

    function validateForm() {
        const newErrors = {};
        if (!name.trim()) newErrors.name = "Name is required.";
        if (!email.trim()) {
            newErrors.email = "Email is required.";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            newErrors.email = "Enter a valid email address.";
        }
        if (!subject.trim()) newErrors.subject = "Subject is required.";
        if (!message.trim()) {
            newErrors.message = "Message is required.";
        } else {
            if (message.length < 10)
                newErrors.message =
                    "Message must be at least 10 characters long.";
            if (message.length > 500)
                newErrors.message = "Message must not exceed 500 characters.";
        }
        return newErrors;
    }

    async function handleSubmit() {
        successMessage = "";
        errors = {};

        // 1. Client Validation
        const clientErrors = validateForm();
        if (Object.keys(clientErrors).length > 0) {
            errors = clientErrors;
            return;
        }

        submitting = true;

        try {
            // 2. Send Request
            const res = await fetch("/api/contact/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // Explicitly include credentials for cookies
                    Accept: "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ name, email, subject, message }),
            });

            const data = await res.json();

            // 3. Handle Response
            if (res.ok && data.success) {
                successMessage =
                    data.message || "Your message has been sent successfully!";
                // Clear Form
                name = "";
                email = "";
                subject = "";
                message = "";
                errors = {};
            } else {
                // Handle Validation Errors or Server Errors
                if (data.errors) {
                    errors = data.errors;
                } else if (data.error) {
                    errors.general = data.error;
                } else {
                    errors.general = "Submission failed. Please try again.";
                }
                console.error("Submission failed:", data);
            }
        } catch (e) {
            errors.general = "Network error. Please check your connection.";
            console.error("Network error:", e);
        } finally {
            submitting = false;
        }
    }
</script>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <h2 class="text-center mb-4">Contact Support</h2>

            {#if successMessage}
                <div
                    class="alert alert-success text-center"
                    data-testid="submit-success"
                    role="alert"
                >
                    {successMessage}
                </div>
            {/if}

            {#if errors.general}
                <div class="alert alert-danger" role="alert">
                    {errors.general}
                </div>
            {/if}

            <form on:submit|preventDefault={handleSubmit} novalidate>
                <!-- Name -->
                <div class="mb-3">
                    <label for="contact-name" class="form-label">Name</label>
                    <input
                        type="text"
                        id="contact-name"
                        class="form-control {errors.name ? 'is-invalid' : ''}"
                        bind:value={name}
                        data-testid="contact-name"
                    />
                    {#if errors.name}
                        <div
                            class="invalid-feedback d-block"
                            data-testid="field-error"
                        >
                            {errors.name}
                        </div>
                    {/if}
                </div>

                <!-- Email -->
                <div class="mb-3">
                    <label for="contact-email" class="form-label">Email</label>
                    <input
                        type="email"
                        id="contact-email"
                        class="form-control {errors.email ? 'is-invalid' : ''}"
                        bind:value={email}
                        data-testid="contact-email"
                    />
                    {#if errors.email}
                        <div
                            class="invalid-feedback d-block"
                            data-testid="field-error"
                        >
                            {errors.email}
                        </div>
                    {/if}
                </div>

                <!-- Subject -->
                <div class="mb-3">
                    <label for="contact-subject" class="form-label"
                        >Subject</label
                    >
                    <input
                        type="text"
                        id="contact-subject"
                        class="form-control {errors.subject
                            ? 'is-invalid'
                            : ''}"
                        bind:value={subject}
                        data-testid="contact-subject"
                    />
                    {#if errors.subject}
                        <div
                            class="invalid-feedback d-block"
                            data-testid="field-error"
                        >
                            {errors.subject}
                        </div>
                    {/if}
                </div>

                <!-- Message - CRITICAL FIX HERE -->
                <div class="mb-3">
                    <label for="contact-message" class="form-label"
                        >Message</label
                    >

                    <!-- 1. The Textarea -->
                    <textarea
                        id="contact-message"
                        class="form-control {errors.message
                            ? 'is-invalid'
                            : ''}"
                        bind:value={message}
                        data-testid="contact-message"
                        rows="5"
                        placeholder="Describe your issue (10-500 characters)"
                    ></textarea>

                    <!-- 2. ✅ THE ERROR MUST BE HERE (Immediate Sibling) -->
                    {#if errors.message}
                        <div
                            class="invalid-feedback d-block"
                            data-testid="field-error"
                        >
                            {errors.message}
                        </div>
                    {/if}

                    <!-- 3. Character Count (Must be AFTER the error) -->
                    <div class="form-text text-end">{message.length}/500</div>
                </div>

                <button
                    type="submit"
                    class="btn btn-primary w-100"
                    disabled={submitting}
                >
                    {submitting ? "Sending..." : "Send Message"}
                </button>
            </form>
        </div>
    </div>
</div>
