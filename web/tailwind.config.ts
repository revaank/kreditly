import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: { colors: { ink: "#0F1B15", paper: "#F5F6F1", lime: "#C6F24E", muted: "#4A554F", line: "#E2E5DC" } } },
  plugins: [],
};
export default config;
