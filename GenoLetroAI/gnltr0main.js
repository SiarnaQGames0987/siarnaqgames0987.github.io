<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs"></script>
<script>
    const model = tf.sequential();
    model.add(tf.layers.dense({inputShape: [2], units: 4, activation: 'relu'}));
    model.add(tf.layers.dense({units: 1, activation: 'sigmoid'}));
    model.compile({optimizer: 'adam', loss: 'binaryCrossentropy'});

    // Eğitim verisi (örnek)
    const xs = tf.tensor2d([[0,0], [0,1], [1,0], [1,1]]);
    const ys = tf.tensor2d([[0], [1], [1], [0]]); // XOR problemi

    async function trainModel() {
        await model.fit(xs, ys, {epochs: 100});
        const output = model.predict(tf.tensor2d([[1, 0]])).dataSync();
        console.log("Tahmin:", output[0]);
    }

    trainModel();
</script>
