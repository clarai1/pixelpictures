// convert hex to rgb notation (https://stackoverflow.com/a/11508164/21044513)
function hexToRgb(hex) {
    hex = hex.slice(1);
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;

    return `rgb(${r}, ${g}, ${b})`;
}

// Function from RGB string to array
const toRGBArray = rgbStr => rgbStr.match(/\d+/g).map(Number);
