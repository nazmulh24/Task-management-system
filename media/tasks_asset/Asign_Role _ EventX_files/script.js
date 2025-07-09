document.getElementById("menu-toggle").addEventListener("click", function () {
  document.getElementById("mobile-menu").classList.toggle("hidden");
});

document
  .getElementById("user-menu-button")
  .addEventListener("click", function () {
    document.getElementById("user-menu").classList.toggle("hidden");
  });

// Close the dropdown when clicking outside
window.addEventListener("click", function (e) {
  if (!document.getElementById("user-menu-button").contains(e.target)) {
    document.getElementById("user-menu").classList.add("hidden");
  }
});
