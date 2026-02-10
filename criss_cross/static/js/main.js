function createCells(rows, cols) {
    cells = [];
    for (row = 0; row < rows; row++) {
        for (col = 0; col < cols; col++) {
            cell = document.createElement("div");

            cell.classList.add("cell");
            cell.setAttribute("data-row", row);
            cell.setAttribute("data-col", col);
    
            cells.push(cell);
        }
    }
    return cells;
}

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM fully loaded and parsed");
    cells = createCells(15, 15);

    puzzle = document.getElementById("puzzle")
    cells.forEach(cell => puzzle.appendChild(cell));
});