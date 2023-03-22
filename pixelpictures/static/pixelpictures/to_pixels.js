var key = null;

document.addEventListener("DOMContentLoaded", function() {

    // If we are in modify, there is data-key in tag table
    if (document.querySelector("table[data-key]")) {
        key = document.querySelector("table").dataset.key;
    }

    document.querySelector("input[type='file']").onchange = resize_image;

    // Save image
    document.querySelector("#save-image").addEventListener("click", () => {
        save_image();
    });
});

function save_image() {
    
    let image = get_image('create-image');

    // Read csrf token from DOM
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get public or private: 
    let public = false;
    if (document.querySelector("#public").innerHTML === "Public") {
        public = true;
    }

    // Get tags:
    let tags = [];
    document.querySelectorAll("#all-tags span span").forEach(tag_span => {
        let tag = tag_span.innerHTML;
        tags.push(tag);
    });

    // Get palette of colors as array
    let palette_array = []
    palette.forEach(color => {
        palette_array.push(toRGBArray(color))
    })

    // If image has an id -> PUT request, save image
    if (key) {
        fetch(`/save`, {
            method: 'PUT',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: JSON.stringify({
                image: image,
                key: key,
                public: public,
                tags: tags,
                palette: palette_array
            })
        })
        .then(response => response.json())
        .then(result => {

            let info = document.createElement('span');
            info.innerHTML = result.message;
            document.querySelector('#save').prepend(info);
            setTimeout(() => { 
                info.remove();
            }, 1000);   
        })
        .catch(error => {
            console.log(error);
        });
    } else {
        // If it doesn't -> POST request, new image
        fetch(`/save`, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: JSON.stringify({
                image: image,
                public: public,
                tags: tags,
                palette: palette_array
            })
        })
        .then(response => response.json())
        .then(result => {
            key = result.key;

            let info = document.createElement('span');
            info.innerHTML = result.message;
            document.querySelector('#save').prepend(info);
            setTimeout(() => { 
                info.remove();
            }, 1000); 
        })
        .catch(error => {
            console.log(error);
        });
    }
}

function resize_image() {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(document.querySelector("form"))
    data.append('height', height);
    data.append('width', width);

    if (document.querySelector("input[type='file']").value) {
        fetch(`/sample`, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: data
        })
        .then(response => response.json())
        .then(result => {
            draw_image(result.sample_image, 'sample-image');
            document.querySelector('input[type=range]').value = 15;

        })
        .catch(error => {
            console.log(error);
        });
    }
}

function image_to_pixels() {

    let image = get_image('sample-image');
    let colors_palette = []

    palette.forEach(color => {
        colors_palette.push(toRGBArray(color));
    })

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/image_to_pixels`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            image: image,
            palette: colors_palette
        })
    })
    .then(response => response.json())
    .then(result => {
        draw_image(result.pixels_image, 'create-image');
    })
}