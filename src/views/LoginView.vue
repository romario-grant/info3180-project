<template>
  <section class="section-authentication">
    <div class="authentication">
      <div class="company">
        <div class="wrapper">
          <div class="lockup">
            <router-link to="/">
              <img class="lo" src="@/assets/icons/m-logo.svg" />
            </router-link>
            <h1>Drift Your Way Into Someone's Heart.</h1>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleLogin" >
        <div class="wrapper" data-width="form">
          <div class="box">
            <p v-show="error" ref="errorEl" class="error">
              {{ error }}
            </p>

            <h2>Log In</h2>
            <div class="inputs">
              <div class="field">
                <label for="email">Email</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  name="email"
                  autocomplete="email"
                  placeholder="Email"
                  required
                />
              </div>

              <div class="field">
                <label for="password">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  name="password"
                  autocomplete="current-password"
                  placeholder="Password"
                  required
                />
              </div>
            </div>

            <div class="buttons">
              <button type="submit" class="cta" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
              </button>
            </div>

            <p class="sub-text">
              Need a Drift Dating account?
              <br />
              <span>
                <router-link to="/signup" class="account">
                  Create an account
                </router-link>
              </span>
            </p>
          </div>
        </div>
      </form>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      error: null,
      errorTimer: null,
    };
  },

  methods: {
    async handleLogin() {
      this.error = null;
      this.loading = true;
      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/login`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
              email: this.email,
              password: this.password,
            }),
          },
        );

        let data = {};

        try {
          data = await res.json();
        } catch (e) {
          console.warn("Invalid JSON response");
        }

        if (!res.ok) {
          this.triggerError(data.error || "Login failed");
          return;
        }

        this.$router.push("/dashboard");
      } catch (err) {
        console.error(err);
        this.triggerError("Server error. Try again.");
      } finally {
        this.loading = false;
      }
    },

    triggerError(message) {
      this.error = null;

      this.$nextTick(() => {
        this.error = message;
      });
    },
  },

  watch: {
    error(val) {
      if (!val) return;

      this.$nextTick(() => {
        const el = this.$refs.errorEl;
        if (!el) return;

        if (this.errorTimer) {
          clearTimeout(this.errorTimer);
        }

        el.classList.remove("active");

        requestAnimationFrame(() => {
          el.classList.add("active");

          this.errorTimer = setTimeout(() => {
            el.classList.remove("active");
          }, 3000);
        });
      });
    },
  },

  beforeUnmount() {
    if (this.errorTimer) {
      clearTimeout(this.errorTimer);
    }
  },
};
</script>

<style scoped src="../assets/css/form.css"></style>
