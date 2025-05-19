// ======== Ayarlar ========
const EMBEDDING_SIZE = 8;
const SEQ_LENGTH = 10;

// ======== Yardımcı Fonksiyonlar ========

// Rastgele sayı aralığı (-0.5 ila +0.5)
function rand() {
  return Math.random() - 0.5;
}

// Softmax
function softmax(arr) {
  const max = Math.max(...arr);
  const exps = arr.map(x => Math.exp(x - max));
  const sum = exps.reduce((a, b) => a + b);
  return exps.map(x => x / sum);
}

// Matris çarpımı
function dot(a, b) {
  let result = new Array(a.length).fill(0);
  for (let i = 0; i < a.length; i++) {
    result[i] = 0;
    for (let j = 0; j < b.length; j++) {
      result[i] += a[i][j] * b[j];
    }
  }
  return result;
}

// ======== Tokenizer (basit) ========
const vocab = {
  "merhaba": 0, "nasılsın": 1, "iyi": 2, "kötü": 3, "değilim": 4,
  "selam": 5, "ne": 6, "yapıyorsun": 7, "?": 8, ".": 9
};

function tokenize(text) {
  const words = text.toLowerCase().split(" ");
  return words.map(w => vocab[w] ?? -1).filter(i => i !== -1);
}

// ======== Embedding Vektörleri ========
const embeddings = Array.from({ length: Object.keys(vocab).length }, () =>
  Array.from({ length: EMBEDDING_SIZE }, rand)
);

// ======== Positional Encoding (sinüs tabanlı) ========
function positionalEncoding(seqLen, dim) {
  let pe = Array.from({ length: seqLen }, () => new Array(dim).fill(0));
  for (let pos = 0; pos < seqLen; pos++) {
    for (let i = 0; i < dim; i++) {
      if (i % 2 === 0)
        pe[pos][i] = Math.sin(pos / Math.pow(10000, i / dim));
      else
        pe[pos][i] = Math.cos(pos / Math.pow(10000, (i - 1) / dim));
    }
  }
  return pe;
}

// ======== Transformer Bloğu (tek katman) ========
function transformer(inputTokens) {
  // 1. Embedding + Positional Encoding
  const embedded = inputTokens.map(t => embeddings[t]);
  const pe = positionalEncoding(embedded.length, EMBEDDING_SIZE);
  const inputVecs = embedded.map((vec, i) =>
    vec.map((v, j) => v + pe[i][j])
  );

  // 2. Self-Attention (tek başına başlatma)
  const Q = inputVecs;
  const K = inputVecs;
  const V = inputVecs;

  const attentionScores = Q.map((q, i) => {
    return K.map((k, j) => {
      let dotProd = q.reduce((sum, val, idx) => sum + val * k[idx], 0);
      return dotProd / Math.sqrt(EMBEDDING_SIZE); // ölçekleme
    });
  });

  const attentionWeights = attentionScores.map(row => softmax(row));

  const attentionOutput = attentionWeights.map((row, i) => {
    let outVec = new Array(EMBEDDING_SIZE).fill(0);
    for (let j = 0; j < row.length; j++) {
      for (let k = 0; k < EMBEDDING_SIZE; k++) {
        outVec[k] += row[j] * V[j][k];
      }
    }
    return outVec;
  });

  // 3. Basit Feed-Forward Katmanı (örnek amaçlı)
  const output = attentionOutput.map(vec =>
    vec.map(v => Math.max(0, v * 0.8 + 0.1)) // ReLU
  );

  return output;
}

// ======== Çalıştırıcı Fonksiyon ========
function runGLNNE(inputText) {
  const tokens = tokenize(inputText);
  if (tokens.length === 0) return "Anlaşılamadı.";

  const outVectors = transformer(tokens);
  return `Transformer sonucu: ${JSON.stringify(outVectors, null, 2)}`;
}
// ======== Vektörden Cevap Üret (decode) ========
function decodeOutput(outputVectors) {
  // İlk vektörün ilk birkaç elemanına göre örnek cevap üretelim
  const avg = outputVectors[0].reduce((a, b) => a + b, 0) / outputVectors[0].length;

  if (avg > 0.8) return "Harika, seninle konuşmak güzel!";
  if (avg > 0.4) return "İyi gidiyoruz!";
  if (avg > 0.1) return "Hımm, ilginç bir şey söyledin.";
  return "Sanırım seni tam anlayamadım.";
}


