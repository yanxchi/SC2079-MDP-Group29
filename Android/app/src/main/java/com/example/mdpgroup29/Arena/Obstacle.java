package com.example.mdpgroup29.Arena;

public class Obstacle extends Cell{
    public enum ImageDirection{
        NORTH,
        SOUTH,
        EAST,
        WEST
    }
    private int obstacleID;
    private int imageID;
    private ImageDirection imageDirection;
    private boolean isRecognizing;

    public Obstacle(int col, int row, int obstacleID) {
        super(col, row, CellType.OBSTACLE);
        this.obstacleID = obstacleID;
        this.imageID = -1;
        this.imageDirection = ImageDirection.NORTH;
        this.isRecognizing = false;
    }

    public Obstacle(int col, int row) {
        super(col, row, CellType.OBSTACLE);
        this.obstacleID = -1;
        this.imageID = -1;
        this.imageDirection = ImageDirection.NORTH;
        this.isRecognizing = false;
    }

    public int getObstacleID() {
        return obstacleID;
    }

    public void setObstacleID(int obstacleID) {
        this.obstacleID = obstacleID;
    }

    public int getImageID() {
        return imageID;
    }

    public void setImageID(int imageID) {
        this.imageID = imageID;
    }

    public boolean isRecognizing() {
        return isRecognizing;
    }

    public void setRecognizing(boolean recognizing) {
        isRecognizing = recognizing;
    }

    public ImageDirection getImageDirection() {
        return imageDirection;
    }

    public void setImageDirection(ImageDirection imageDirection) {
        this.imageDirection = imageDirection;
    }
}
