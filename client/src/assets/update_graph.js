window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_graph: function (msg) {
            if (!msg) { return {}; }  // no data, just return
            console.log("||| I am here |||")
            const startTime = performance.now();
            const data = JSON.parse(msg.data);  // read the data
            const x_dim = data.x;
            const y_dim = data.y;
            const xval = arange(x_dim);
            const yval = arange(y_dim);
            const timestamp = data.time_stamp;
            const uid = data.uid;
            const figtitle = timestamp + " " + uid;
            const plot = document.getElementById('bl-cam');

            let img = data.img;
            img = vectorTo2DArray(img, [y_dim, x_dim])

            const layout = {
                title: figtitle,
                xaxis: { title: 'Pixel', scaleratio: 1, scaleanchor: 'y' },
                yaxis: { title: 'Pixel', scaleratio: 1, scaleanchor: 'x' },
                width: 550,
                height: 550,
            };

            const figure = {
                data: [{ x: xval, y: yval, z: img, type: "heatmap" }],
                layout: layout
            };

            Plotly.react(plot, figure.data, figure.layout);

            const end = performance.now();
            const renderingTime = end - startTime;

            return `Rendering Time: ${renderingTime.toFixed(2)} ms`;
        }
    }
});

function vectorTo2DArray(vector, dimensions) {
    let ndarray = []
    let currentIndex = 0

    // Iterate over 2 dimensions
    for (let i = 0; i < dimensions[0]; i++) {
        let subArray = [];
        for (let j = 0; j < dimensions[1]; j++) {
            subArray.push(vector[currentIndex]);
            currentIndex++;
        }
        ndarray.push(subArray);
    }

    return ndarray;
}

function arange(value) {
    const arr = new Array(value);
    for (let i = 0; i < value; i++) {
        arr[i] = i;
    }
    return arr
}