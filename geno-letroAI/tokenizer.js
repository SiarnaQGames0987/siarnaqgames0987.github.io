export function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-zçğıöşü0-9\s]/gi, '') // noktalama temizle
    .split(" ")
    .filter(Boolean);
}
