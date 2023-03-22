function delete_picture(key) {
    let confirmation = confirm("Do you want to delete this picture? The action is irreversible!");
    if (confirmation){
        // Read csrf token from DOM
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/delete`, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: JSON.stringify({
                key: key
            })
        })
        .then(response => response.json())
        .then(result => {
            document.querySelector("#main").innerHTML = result.message
        })
        .catch(error => {
            console.log(error);
        });
    }
}

function download_view(key){
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let preview = document.querySelector("#view-image");
    preview.querySelector("img").remove()
    
    fetch(`/download`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            key: key,
            start_row: document.querySelector("#start-row").value,
            start_col: document.querySelector("#start-col").value,
            dir_rows: document.querySelector("input[name='row-direction']:checked").value,
            dir_cols: document.querySelector("input[name='col-direction']:checked").value,
            grid_color: toRGBArray(hexToRgb(document.querySelector("input[type='color']").value)),
            size_cell: document.querySelector("input[type='range']").value,
            step: document.querySelector("#step").value
        })
    })
    .then(response => response.json())
    .then(result => {
        image = document.createElement('img');
        image.src = result.source;
        preview.append(image);
        document.querySelector("#download").href = result.source;
        document.querySelector("#download").download = key;
    })
    .catch(error => {
        console.log(error);
    });
}

function set_image_size(event, key){
    let new_size = event.target.value;
    if (document.querySelector('#view-image img').id === 'plain-image') {
        let width_image = document.querySelector('#view-image img').naturalWidth;
        document.querySelector("#view-image img").style.width = `${width_image / 18 * new_size}px`;
    }
    else {
        download_view(key)
    }
}