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

      <form @submit.prevent="handleSignup">
        <div class="wrapper" data-width="form">
          <div class="box">
            <p v-show="error" ref="errorEl" class="error">
              {{ error }}
            </p>

            <h2>Sign Up</h2>
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
                <label for="phone_number">Phone Number</label>
                <input
                  id="phone_number"
                  v-model="phone_number"
                  type="text"
                  name="phone_number"
                  autocomplete="phone_number"
                  placeholder="Phone Number"
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
                <span v-if="loading">⏳ Creating account...</span>
                <span v-else>Sign Up</span>
              </button>
            </div>

            <p class="sub-text">
              <span>
                <router-link to="/login" class="account">
                  Already have an account?
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
      phone_number: "",
      password: "",
      error: null,
      success: null,
    };
  },
  methods: {
    async handleSignup() {
      if (this.loading) return;

      this.error = null;
      this.success = null;
      this.loading = true;

      try {
        const res = await fetch("http://localhost:5000/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email: this.email,
            phone_number: this.phone_number,
            password: this.password,
          }),
        });

        let data = {};

        try {
          data = await res.json();
        } catch {
          console.warn("Invalid JSON response");
        }

        if (!res.ok) {
          this.error = data.error || "Signup failed";
          return;
        }

        this.success = "Account created successfully!";

        setTimeout(() => {
          this.$router.push("/login");
        }, 1500);
      } catch (err) {
        console.error(err);
        this.error = "Server error. Try again.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped src="../assets/css/form.css"></style>
