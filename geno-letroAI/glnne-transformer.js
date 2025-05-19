// glnne-transformer.js

let embeddings = {}; // embeddings.json'dan yüklenecek
let dialogue = [];   // sample_data/dialogue.json'dan yüklenecek
const EMBEDDING_SIZE = 8;

// ========== YARDIMCI FONKSİYONLAR ==========

function softmax(arr) {
  const max = Math.max(...arr);
  const exps = arr.map(x => Math.exp(x - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map(x => x / sum);
}

function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function addVectors(a, b) {
  return a.map((v, i) => v + b[i]);
}

function relu(v) {
  return v.map(x => Math.max(0, x));
}

function averageVector(vectors) {
  const result = new Array(EMBEDDING_SIZE).fill(0);
  for (let v of vectors) {
    for (let i = 0; i < EMBEDDING_SIZE; i++) {
      result[i] += v[i];
    }
  }
  return result.map(x => x / vectors.length);
}

function positionalEncoding(length) {
  const pe = [];
  for (let pos = 0; pos < length; pos++) {
    const vec = [];
    for (let i = 0; i < EMBEDDING_SIZE; i++) {
      vec.push(i % 2 === 0
        ? Math.sin(pos / Math.pow(10000, i / EMBEDDING_SIZE))
        : Math.cos(pos / Math.pow(10000, (i - 1) / EMBEDDING_SIZE))
      );
    }
    pe.push(vec);
  }
  return pe;
}

// ========== EMBEDDING + ENCODER BLOĞU ==========

function encodeInput(tokens) {
  let embedded = tokens.map(t => embeddings[t] || new Array(EMBEDDING_SIZE).fill(0));
  let pe = positionalEncoding(tokens.length);
  let added = embedded.map((vec, i) => addVectors(vec, pe[i]));

  // Self-attention (tek head, kendi embedding'i ile dot)
  const attention = added.map(q => {
    const scores = added.map(k => cosineSimilarity(q, k));
    const weights = softmax(scores);
    const context = new Array(EMBEDDING_SIZE).fill(0);

    for (let j = 0; j < weights.length; j++) {
      for (let k = 0; k < EMBEDDING_SIZE; k++) {
        context[k] += weights[j] * added[j][k];
      }
    }

    return context;
  });

  // FeedForward layer
  const ffn = attention.map(vec => relu(vec.map(x => x * 1.1 + 0.1)));

  return averageVector(ffn);
}

// ========== YÜKLEME ==========

export async function loadData() {
  const embRes = await fetch("embeddings.json");
  embeddings = await embRes.json();

  const dlgRes = await fetch("sample_data/dialogue.json");
  const rawData = await dlgRes.json();

  dialogue = rawData.map(item => {
    const tokens = item.input.toLowerCase().split(" ");
    const encoded = encodeInput(tokens);
    return {
      input: item.input,
      output: item.output,
      vector: encoded
    };
  });
}

// ========== ANA ÇALIŞTIRICI ==========

export function runGLNNE(userText) {
  const tokens = userText.toLowerCase().split(" ");
  const inputVec = encodeInput(tokens);

  let bestSim = -1;
  let bestAnswer = "Bunu henüz öğrenmedim.";

  for (let pair of dialogue) {
    const sim = cosineSimilarity(inputVec, pair.vector);
    if (sim > bestSim) {
      bestSim = sim;
      bestAnswer = pair.output;
    }
  }

  return bestAnswer + ` (benzerlik: ${bestSim.toFixed(2)})`;
}
