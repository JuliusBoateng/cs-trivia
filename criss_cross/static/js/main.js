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
    puzzle = document.getElementById("puzzle")
    
    cells = createCells(15, 15);
    cells.forEach(cell => puzzle.appendChild(cell));
});