<script>
  import { onMount } from "svelte";
  export let navigate;
  export let currentUser;

  let user = null;
  let loading = true;
  let uploading = false;
  let previewUrl = null;
  let errorMessage = "";
  let successMessage = "";

  async function fetchUserProfile() {
    loading = true;
    errorMessage = "";
    try {
      const res = await fetch("/api/user/avatar/", {
        credentials: "include",
      });

      if (res.status === 401) {
        navigate("login");
        return;
      }

      if (res.ok) {
        user = await res.json();
        if (user.avatar) {
          previewUrl = user.avatar;
        }
      } else {
        const err = await res.json().catch(() => ({}));
        errorMessage = err.error || "Failed to load profile";
      }
    } catch (e) {
      console.error("Failed to load profile:", e);
      errorMessage = "Network error loading profile";
    } finally {
      loading = false;
    }
  }

  async function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/gif"];
    if (!allowedTypes.includes(file.type)) {
      errorMessage = "Invalid file type. Please upload JPG, PNG, or GIF.";
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      errorMessage = "File too large. Maximum size is 5MB.";
      return;
    }

    uploading = true;
    errorMessage = "";
    successMessage = "";

    // Create preview immediately
    previewUrl = URL.createObjectURL(file);

    const formData = new FormData();
    formData.append("avatar", file);
    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
    try {
      const res = await fetch("/api/user/avatar/", {
        method: "PUT",
        credentials: "include",
        headers: { 'X-CSRFToken': csrfToken },
        body: formData,
      });

      const contentType = res.headers.get("content-type");
      let data;
      if (contentType && contentType.includes("application/json")) {
        data = await res.json();
      } else {
        const text = await res.text();
        throw new Error(`Unexpected response: ${text}`);
      }

      if (res.ok) {
        successMessage = "Avatar uploaded successfully!";
        user = { ...user, avatar: data.avatar };
        previewUrl = data.avatar;
        event.target.value = "";
      } else {
        errorMessage = data.error || `Upload failed: ${res.status}`;
        previewUrl = user?.avatar || null;
      }
    } catch (e) {
      console.error("Upload error:", e);
      errorMessage = `Network error: ${e.message}`;
      previewUrl = user?.avatar || null;
    } finally {
      uploading = false;
      setTimeout(() => {
        errorMessage = "";
        successMessage = "";
      }, 3000);
    }
  }

  onMount(() => {
    fetchUserProfile();
  });
</script>

<div class="container py-4">
  <h2 class="mb-4">My Profile</h2>

  {#if loading}
    <div class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  {:else if errorMessage}
    <div class="alert alert-danger" role="alert" data-testid="error-message">
      {errorMessage}
      <button class="btn btn-link p-0 ms-2" on:click={fetchUserProfile}
        >Retry</button
      >
    </div>
  {:else if user}
    <div class="card shadow-sm">
      <div class="card-body">
        <!-- Avatar Section -->
        <div class="text-center mb-4">
          <div class="position-relative d-inline-block">
            <img
              src={previewUrl ||
                "https://via.placeholder.com/150?text=No+Avatar"}
              alt="Profile Avatar"
              class="rounded-circle border"
              style="width: 150px; height: 150px; object-fit: cover;"
              data-testid="avatar-preview"
            />
            {#if uploading}
              <div
                class="position-absolute top-50 start-50 translate-middle bg-white rounded-circle p-2"
              >
                <div
                  class="spinner-border spinner-border-sm text-primary"
                ></div>
              </div>
            {/if}
          </div>

          <!-- Upload Input -->
          <div class="mt-3">
            <label for="avatar-upload" class="btn btn-outline-primary btn-sm">
              {uploading ? "Uploading..." : "Change Avatar"}
            </label>
            <input
              id="avatar-upload"
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/gif"
              class="d-none"
              data-testid="avatar-input"
              on:change={handleAvatarUpload}
              disabled={uploading}
            />
          </div>

          {#if errorMessage}
            <p class="text-danger small mt-2">{errorMessage}</p>
          {/if}
          {#if successMessage}
            <p class="text-success small mt-2">{successMessage}</p>
          {/if}
        </div>

        <!-- User Info -->
        <div class="row">
          <div class="col-md-6">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </div>
          <div class="col-md-6">
            <p><strong>Role:</strong> {user.role || "customer"}</p>
            <p>
              <strong>Member since:</strong>
              {user.date_joined
                ? new Date(user.date_joined).toLocaleDateString()
                : "N/A"}
            </p>
          </div>
        </div>

        <!-- Back Button -->
        <div class="mt-4">
          <button
            class="btn btn-secondary"
            on:click={() => navigate("dashboard")}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  {:else}
    <div class="alert alert-warning text-center">
      Failed to load profile.
      <a href="/login" on:click|preventDefault={() => navigate("login")}
        >Login</a
      > again.
    </div>
  {/if}
</div>
