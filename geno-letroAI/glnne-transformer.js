import { tokenize } from './tokenizer.js';

let embeddings = {};
let dialogue = [];
const EMBEDDING_SIZE = 8;

function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
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

function encodeInput(tokens) {
  const vecs = tokens.map(t => embeddings[t]).filter(Boolean);
  if (vecs.length === 0) return new Array(EMBEDDING_SIZE).fill(0);
  return averageVector(vecs);
}

export async function loadData() {
  embeddings = await fetch('./embeddings.json').then(res => res.json());
  const raw = await fetch('./sample_data/dialogue.json').then(res => res.json());
  dialogue = raw.map(item => {
    const tokens = tokenize(item.input);
    return {
      output: item.output,
      vector: encodeInput(tokens)
    };
  });
}

export function runGLNNE(text) {
    const math = isMathExpression(text);
  if (math) return math;

  const tokens = tokenize(text);
  const tokens = tokenize(text);
  const inputVec = encodeInput(tokens);

  let bestSim = -1;
  let bestAnswer = "Bunu anlayamadım.";

  for (let pair of dialogue) {
    const sim = cosineSimilarity(inputVec, pair.vector);
    if (sim > bestSim) {
      bestSim = sim;
      bestAnswer = pair.output;
    }
  }
  // glnne-transformer.js
function isMathExpression(text) {
  try {
    const safe = text.replace(/[^0-9+\-*/(). ]/g, '');
    const result = eval(safe);
    return isFinite(result) ? `Sonuç: ${result}` : null;
  } catch {
    return null;
  }
}


  if (bestSim < 0.90) return "Bu konuda bir şey öğrenmedim.";
  return `${bestAnswer} (benzerlik: ${bestSim.toFixed(2)})`;
}
