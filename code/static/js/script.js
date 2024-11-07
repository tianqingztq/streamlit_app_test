// Function to show/hide sections
function showSection(sectionId) {
  console.log("Showing section:", sectionId); // Debug log

  // Hide all sections
  document.querySelectorAll(".section").forEach((section) => {
    section.classList.remove("active");
  });

  // Show selected section
  const selectedSection = document.getElementById(sectionId);
  if (selectedSection) {
    selectedSection.classList.add("active");
  } else {
    console.error("Section not found:", sectionId);
  }
}

// Function to handle user type selection
function selectUserType(type) {
  console.log("Selected user type:", type); // Debug log

  if (type === "hcp") {
    showSection("hcpSection");
  } else if (type === "customer") {
    showSection("customerSection");
  }
}

// Function to handle going back to user type selection
function goBack() {
  console.log("Going back to user type selection"); // Debug log
  showSection("userTypeSection");
}

// Function to handle survey submission
async function submitSurvey(event) {
  event.preventDefault();

  // Show loading state
  const submitButton = event.target.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = "Submitting...";

  try {
    // Collect form data
    const formData = {
      bmi: document.getElementById("bmi").value,
      bloodPressure: document.getElementById("bloodPressure").value,
      cholesterol: document.getElementById("cholesterol").value,
      cholesterolCheck: document.getElementById("cholesterolCheck").value,
      smoking: document.getElementById("smoking").value,
      stroke: document.getElementById("stroke").value,
      heartDisease: document.getElementById("heartDisease").value,
      physicalActivity: document.getElementById("physicalActivity").value,
      fruitConsumption: document.getElementById("fruitConsumption").value,
      vegetableConsumption: document.getElementById("vegetableConsumption")
        .value,
      heavyDrinker: document.getElementById("heavyDrinker").value,
      healthCoverage: document.getElementById("healthCoverage").value,
      costBarrier: document.getElementById("costBarrier").value,
      generalHealth: document.getElementById("generalHealth").value,
      mentalHealth: document.getElementById("mentalHealth").value,
      physicalHealth: document.getElementById("physicalHealth").value,
      education: document.getElementById("education").value,
      income: document.getElementById("income").value,
    };

    console.log("Sending data:", JSON.stringify(formData));

    const response = await fetch("/api/submit-survey", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Server error");
    }

    if (result.success) {
      console.log("Survey submitted successfully:", result);
      alert("Survey submitted successfully!");
      showSection("visualizationSection");
    } else {
      throw new Error(result.error || "Unknown error occurred");
    }
  } catch (error) {
    console.error("Error submitting survey:", error);
    alert(`Error submitting survey: ${error.message}. Please try again.`);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Submit Survey";
  }
}

// Add event listener when the document loads
document.addEventListener("DOMContentLoaded", function () {
  console.log("Document loaded"); // Debug log

  // Verify all sections exist
  [
    "userTypeSection",
    "hcpSection",
    "customerSection",
    "surveySection",
    "visualizationSection",
  ].forEach((id) => {
    const section = document.getElementById(id);
    if (!section) {
      console.error(`Section not found: ${id}`);
    }
  });

  // Add click event listeners to all buttons
  document.querySelectorAll("button").forEach((button) => {
    if (button.onclick === null) {
      console.log("Button without click handler:", button);
    }
  });
});

// Function to handle login form submission
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store user info (in a real app, store the token)
      sessionStorage.setItem("hcpUser", JSON.stringify(data.user));

      // Update dashboard with user info
      document.getElementById("hcpName").textContent = data.user.name;

      // Show dashboard
      showSection("hcpDashboard");
      showDashboardSection("patientData"); // Show default dashboard section
    } else {
      alert(data.error || "Login failed. Please try again.");
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("An error occurred during login. Please try again.");
  }
}

// Function to handle logout
function handleLogout() {
  // Clear session storage
  sessionStorage.removeItem("hcpUser");

  // Redirect to home
  showSection("userTypeSection");
}

// Function to toggle password visibility
function togglePassword() {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.querySelector(".toggle-password");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleButton.textContent = "Hide";
  } else {
    passwordInput.type = "password";
    toggleButton.textContent = "Show";
  }
}

// Function to show forgot password form
function showForgotPassword(event) {
  event.preventDefault();
  alert("Please contact administrator to reset your password.");
}

// Function to show dashboard sections
function showDashboardSection(sectionId) {
  // Hide all dashboard sections
  document.querySelectorAll(".dashboard-section").forEach((section) => {
    section.classList.remove("active");
  });

  // Show selected section
  const selectedSection = document.getElementById(sectionId);
  if (selectedSection) {
    selectedSection.classList.add("active");
  }
}

// Check login status on page load
document.addEventListener("DOMContentLoaded", function () {
  const user = JSON.parse(sessionStorage.getItem("hcpUser"));
  if (
    user &&
    document.getElementById("hcpDashboard").classList.contains("active")
  ) {
    document.getElementById("hcpName").textContent = user.name;
  }
});

// Authentication related functions

function toggleAuthForm(formType) {
  // Handle login form
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  if (formType === "login") {
    loginForm.style.display = "block";
    registerForm.style.display = "none";
  } else {
    loginForm.style.display = "none";
    registerForm.style.display = "block";
  }
}

function togglePasswordVisibility(inputId) {
  const input = document.getElementById(inputId);
  const button = input.nextElementSibling;

  if (input.type === "password") {
    input.type = "text";
    button.textContent = "Hide";
  } else {
    input.type = "password";
    button.textContent = "Show";
  }
}

async function handleRegistration(event) {
  event.preventDefault();

  const submitButton = event.target.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = "Registering...";

  try {
    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    const formData = {
      name: document.getElementById("registerName").value,
      email: document.getElementById("registerEmail").value,
      password: password,
      licenseNumber: document.getElementById("licenseNumber").value,
    };

    console.log(formData);

    const response = await fetch("/api/hcp/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    console.log("Server response:", data);

    if (response.ok) {
      alert("Registration successful! Please login with your credentials.");
      toggleAuthForm("login");
    } else {
      alert(data.error || "Registration failed. Please try again.");
    }
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Create Account";
  }
}

async function handleLogin(event) {
  event.preventDefault();

  const formData = {
    email: document.getElementById("loginEmail").value,
    password: document.getElementById("loginPassword").value,
  };

  try {
    const response = await fetch("/api/hcp/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (response.ok) {
      // Store auth token
      localStorage.setItem("hcpToken", data.token);
      localStorage.setItem("hcpName", data.name);

      // Update dashboard
      document.getElementById("hcpName").textContent = data.name;

      // Show dashboard
      showSection("hcpDashboard");
    } else {
      alert(data.error || "Login failed. Please try again.");
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("An error occurred during login. Please try again.");
  }
}

function validatePassword(password) {
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasMinLength = password.length >= 8;

  if (hasUpperCase && hasLowerCase && hasNumbers && hasMinLength) {
    return "strong";
  } else if ((hasUpperCase || hasLowerCase) && hasNumbers) {
    return "medium";
  } else {
    return "weak";
  }
}
