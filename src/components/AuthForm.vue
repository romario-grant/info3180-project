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

      <form @submit.prevent="handleSubmit">
        <div class="wrapper" data-width="form">
          <div class="box">
            <p v-show="error" ref="errorEl" class="error">
              {{ error }}
            </p>

            <h2>{{ title }}</h2>
            <div class="inputs">
              <div class="field">
                <label for="email">Email</label>
                <div class="input-wrap">
                  <input
                    id="email"
                    class="input-reset"
                    v-model="email"
                    type="email"
                    name="email"
                    autocomplete="email"
                    placeholder="Email"
                    required
                  />
                </div>
              </div>

              <div class="field" v-if="isSignup">
                <label for="phone_number">Phone Number</label>
                <div class="input-wrap">
                  <input
                    id="phone_number"
                    class="input-reset"
                    v-model="phone_number"
                    @input="phone_number = phone_number.replace(/[^0-9]/g, '')"
                    inputmode="numeric"
                    placeholder="Phone Number"
                    required
                  />
                </div>
              </div>

              <div class="field">
                <label for="password">Password</label>

                <div class="input-wrap">
                  <input
                    id="password"
                    class="input-reset"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    name="password"
                    autocomplete="current-password"
                    placeholder="Password"
                    required
                  />

                  <button
                    type="button"
                    class="reset-btn hide"
                    @click="showPassword = !showPassword"
                  >
                    <span
                      class="fa-solid"
                      :class="showPassword ? 'fa-eye' : 'fa-eye-slash'"
                    ></span>
                  </button>
                </div>
              </div>
            </div>

            <div class="buttons">
              <button type="submit" class="cta" :disabled="loading">
                {{ buttonText }}
              </button>
            </div>

            <p class="sub-text">
              <router-link
                :to="isSignup ? '/login' : '/signup'"
                class="account"
              >
                {{
                  isSignup ? "Already have an account?" : "Create an account"
                }}
              </router-link>
            </p>
          </div>
        </div>
      </form>
    </div>
  </section>
</template>

<script>
export default {
  props: {
    mode: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      email: "",
      phone_number: "",
      password: "",
      error: null,
      errorTimer: null,
      showPassword: false,
      loading: false,
    };
  },

  computed: {
    isSignup() {
      return this.mode === "signup";
    },
    title() {
      return this.isSignup ? "Sign Up" : "Log In";
    },
    buttonText() {
      if (this.loading) {
        return this.isSignup ? "Creating account..." : "Logging in...";
      }
      return this.isSignup ? "Sign Up" : "Login";
    },
  },

  methods: {
    async handleSubmit() {
      if (this.loading) return;

      this.error = null;
      this.loading = true;

      const base = import.meta.env.VITE_API_URL || "http://localhost:5000";

      const endpoint = this.isSignup ? "/signup" : "/login";

      const body = this.isSignup
        ? {
            email: this.email,
            phone_number: this.phone_number,
            password: this.password,
          }
        : {
            email: this.email,
            password: this.password,
          };

      try {
        const res = await fetch(base + endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(body),
        });

        let data = {};
        try {
          data = await res.json();
        } catch {}

        if (!res.ok) {
          this.triggerError(data.error || "Authentication failed");
          return;
        }

        // redirect logic
        if (this.isSignup) {
          setTimeout(() => this.$router.push("/login"), 1200);
        } else {
          this.$router.push("/dashboard");
        }
      } catch (err) {
        this.triggerError("Server error. Try again.");
      } finally {
        this.loading = false;
      }
    },

    onInput(e) {
      this.phone_number = e.target.value.replace(/[^0-9]/g, "");
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
    if (this.errorTimer) clearTimeout(this.errorTimer);
  },
};
</script>

<style scoped src="../assets/css/form.css"></style>
