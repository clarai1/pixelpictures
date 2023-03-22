var width = 30;
var height = 30;

document.addEventListener("DOMContentLoaded", function() {

    // Set default height and width
    document.querySelector("input[name='width']").value = width;
    document.querySelector("input[name='height']").value = height;

    // Changing height and width
    document.querySelector("input[name='width']").addEventListener("change", (event) => {
        let new_width = event.target.value;
        if (new_width <= 0) {
            document.querySelector("input[name='width']").value = width;
        } else {
            width = new_width;
            if (document.querySelector("input[type='file']").value) {
                resize_image();
            }
        }
    });

    document.querySelector("input[name='height']").addEventListener("change", (event) => {
        let new_height = event.target.value;
        if (new_height <= 0) {
            document.querySelector("input[name='height']").value = height;
        } else {
            height = new_height;
            if (document.querySelector("input[type='file']").value) {
                resize_image();
            }
        }
    });
    
    // Start drawing:
    document.querySelector('#start-drawing').addEventListener('click', () => {
        document.querySelector('.options').style.display = 'none';
        document.querySelector('#create-image').style.display = 'block';
        document.querySelector('#save').style.display = 'block';
        if (document.querySelector('#sample-image table')) {
            document.querySelector('#sample-image').style.display = 'none';
            image_to_pixels();
        } else {
            draw_image(null, 'create-image');
        }
    });

    // Options public/private toggle
    document.querySelector("#public").addEventListener("click", (event) => {
        if (event.target.innerHTML === "Private") {
            event.target.innerHTML = "Public";
        } else {
            event.target.innerHTML = "Private"
        }
    });

    // Options add tags
    document.querySelectorAll("#all-tags button").forEach(button => {
        button.addEventListener("click", (event) => {
            event.target.parentElement.remove()
        });
    })

});

function add_tag() {
    let tag = document.querySelector("#tag").value.replace(/\s/g, "");
        if (tag) {
            let new_tag = document.createElement("span");
            let delete_button = document.createElement("button");
            new_tag.append(delete_button);
            delete_button.innerHTML = 'x';
            delete_button.addEventListener("click", (event) => {
                event.target.parentElement.remove()
            });
            let tag_span = document.createElement('span');
            tag_span.innerHTML = tag;
            new_tag.append(tag_span);
            document.querySelector("#all-tags").append(new_tag);
            document.querySelector("#tag").value = '';
        }
}
