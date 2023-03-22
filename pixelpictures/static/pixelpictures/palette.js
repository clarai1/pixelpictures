var palette = new Set();
var remove = false;
var color = 'rgb(0,0,0)';

document.addEventListener("DOMContentLoaded", function() {

    // Initial current color:
    document.querySelector('#current-color').style.backgroundColor = color;

    // Black and white are in palette by default. If we are in modify, prefill palette variable
    if (document.querySelector("#colors-palette").innerHTML.trim() === '') {
        add_remove_color(('rgb(255, 255, 255)'));
        add_remove_color(('rgb(0, 0, 0)'));
    }
    else {
        document.querySelectorAll("#colors-palette button").forEach(button => {
            palette.add(button.style.backgroundColor);
        })
    }

    // Change color 
    document.querySelector("#color").addEventListener("change", () => {
        color = document.querySelector("#color").value;
        document.querySelector("#current-color").style.backgroundColor = color;
    });

    // Add color to palette when drawing
    document.querySelector(".add-color").addEventListener("click", () => {
        add_remove_color(hexToRgb(document.querySelector("#color").value));
    });

    // Add event listener  to each pre-existing palette color:
    document.querySelectorAll('#colors-palette button').forEach(button => {
        add_event_button_palette(button);
    });
});

function add_remove_color(new_color) {
    if (!palette.has(new_color)){
        palette.add(new_color)
        let new_button = document.createElement('button');
        document.querySelector("#colors-palette").append(new_button);
        new_button.style.backgroundColor = `${new_color}`;
        add_event_button_palette(new_button);
    }
}

function add_event_button_palette(button) {
    button.addEventListener("click", () => {
        if (remove) {
            button.remove();
            palette.delete(button.style.backgroundColor);
        } else {
            color = button.style.backgroundColor;
            document.querySelector("#current-color").style.backgroundColor = color;
        }
    });
} 

function remove_color_button() {
    remove = !remove;
    let remove_button = document.querySelector(".remove-color");
    if (remove) {
        document.querySelectorAll("#colors-palette button").forEach(button => {
            button.style.borderColor = 'blue';
        });
        remove_button.innerHTML = 'Done';
    } else {
        document.querySelectorAll("#colors-palette button").forEach(button => {
            button.style.borderColor = 'gray';
        });
        remove_button.innerHTML = 'Remove';
    }
}

