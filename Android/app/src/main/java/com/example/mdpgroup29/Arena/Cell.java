package com.example.mdpgroup29.Arena;

public class Cell {
    public enum CellType {
        EMPTY,
        OBSTACLE,
        ROBOT_BODY,
        ROBOT_HEAD
    }
    private CellType type;
    public int row, col;

    public CellType getType() {
        return type;
    }

    public void setType(CellType type) {
        this.type = type;
    }

    public int getCol() {
        return col;
    }

    public void setCol(int col) {
        this.col = col;
    }

    public int getRow() {
        return row;
    }

    public void setRow(int row) {
        this.row = row;
    }

    public Cell (int col, int row, CellType type){
        this.col = col;
        this.row = row;
        this.type = type;
    }

    @Override
    public boolean equals(Object o){
        if (o instanceof Cell){
            Cell that = (Cell) o;
            return (this.col==that.col) && (this.row== that.row);
        }
        return false;
    }
}
