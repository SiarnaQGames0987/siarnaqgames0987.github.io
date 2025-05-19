// ✅ tokenizer.js
export function tokenize(text) {
  return text.toLowerCase().split(" ").filter(Boolean);
}
