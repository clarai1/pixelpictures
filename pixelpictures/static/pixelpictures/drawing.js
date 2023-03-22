var drag = false;

document.addEventListener("DOMContentLoaded", function() {

    // Color clicks for drawing
    document.addEventListener("mouseup", () => {
        drag = false;
    });

    document.querySelectorAll("#create-image td").forEach(td => {
        colorable_cell(td);
    });

});

function colorable_cell(td) {

    td.addEventListener("mousedown", () => {
        td.style.backgroundColor = color;
        drag = true;
    });

    td.addEventListener("mouseover", () => {
        if (drag) {
            td.style.backgroundColor = color;
        }
    });

    td.addEventListener("dblclick", () => {
        td.style.backgroundColor = 'rgb(255,255,255)';
    })
}

function get_image(table_name) {
    // returns image as an array of colors from desired table

    // Get image from html, heightXwidth array
    let image = new Array();
    document.querySelectorAll(`#${table_name} tr`).forEach(row => {
        let image_row = new Array();
        row.querySelectorAll('td').forEach(cell => {
            image_row.push(toRGBArray(cell.style.backgroundColor));
        });
        image.push(image_row);
    })

    return image
}

function draw_image(image, table_name) {

    // Display correct table:
    document.querySelector(`#${table_name}`).style.display = 'block';
    
    // First empty table if there is one
    if (document.querySelector(`#${table_name} table`)) {
       var new_table = document.querySelector(`#${table_name} table`);
       new_table.innerHTML = '';
    } else {
        var new_table = document.createElement('table');
        document.querySelector(`#${table_name}`).append(new_table);
    }

    if (image) {
        height = image.length;
        width = image[0].length;
    }
    for (let i = 0; i < height; i++) {
        let tr = document.createElement('tr');
        for (let j = 0; j < width; j++){
            let td = document.createElement('td');
            td.dataset.row = i;
            td.dataset.col = j;
            if (image) {
                td.style.backgroundColor = `rgb(${image[i][j][0]}, ${image[i][j][1]}, ${image[i][j][2]})`;
            } else {
                td.style.backgroundColor = 'rgb(255, 255, 255)';
            }

            // Give event listeners to cell depending on table
            if (table_name === 'sample-image') {
                td.addEventListener("click", () => {
                    add_remove_color(td.style.backgroundColor);
                })
            } else {
                colorable_cell(td);
            }

            tr.append(td)
        }
        new_table.append(tr)
    }

}

function set_size_cells(event) {
    let new_size = event.target.value;
    document.querySelectorAll("td").forEach(td => {
        td.style.height = `${new_size}px`;
        td.style.width = `${new_size}px`;
    })
}