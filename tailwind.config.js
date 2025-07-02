/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", //------> Template at the __ Root / Project __ level...
    "./**/templates/**/*.html", //---> Template inside _Apps_...
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
