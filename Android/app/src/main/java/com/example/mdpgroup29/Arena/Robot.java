package com.example.mdpgroup29.Arena;

import java.util.ArrayList;

/**
 * [B, H, B]
 * [B, B, B]
 * [B, B, B]
 */
public class Robot {
    public static Cell[][] robotMatrix;
    private static Cell[][] grid;
    public static String robotDir;
    private static int numGrids = 3; //number of grids to move by for BR,BL,R,L

    public static void initializeRobot(Cell[][] cells){
        robotMatrix = new Cell[3][3];
        robotMatrix[1][1] = null;
        grid = cells;
    }

    public static boolean setRobot(int xCenter, int yCenter,  String dir, ArrayList<Obstacle> obstacles){
        boolean obsFlag = checkObs(xCenter,yCenter,obstacles);
        if(!obsFlag){
            setRobotPosition(xCenter, yCenter);
            setRobotDirection(dir);
            return true;
        } else {
            return false;
        }
    }
    /**
     * @param xCenter x Coordinate of new centre of robot
     * @param yCenter y Coordinate of new centre of robot
     */
    private static void setRobotPosition(int xCenter, int yCenter){
        int yTopLeft=yCenter-1, xTopLeft= xCenter-1;
        Cell curCell;
        if (xTopLeft < 0 || xTopLeft + 2 > 19 || yTopLeft < 0 || yTopLeft + 2 > 19)
        {
            System.out.println("Out of bound : Robot need nine cells");
            return;
        }
        else
        {
            // wipe old robot position
            if (robotMatrix[0][0] != null){ // skip on initial robot set
                for (int i=0; i<robotMatrix[0].length; i++){ // iterate through rows: i = x coordinate
                    for (int j=0; j<robotMatrix.length; j++){ // iterate through cols: j = y coordinate
                        robotMatrix[i][j].setType(Cell.CellType.EMPTY);
                    }
                }
            }

            // set new robot position
            for (int i=0; i<robotMatrix[0].length; i++){ // iterate through rows: i = x coordinate
                for (int j=0; j<robotMatrix.length; j++){ // iterate through cols: j = y coordinate
                    curCell = grid[xTopLeft+i][yTopLeft+j];
                    curCell.setType(Cell.CellType.ROBOT_BODY);
                    robotMatrix[i][j] = curCell;
                }
            }
        }

    }

    public static void clearRobot() {
        if (robotMatrix[0][0] != null) { // skip on initial robot set
            for (int i = 0; i < robotMatrix[0].length; i++) { // iterate through rows: i = x coordinate
                for (int j = 0; j < robotMatrix.length; j++) { // iterate through cols: j = y coordinate
                    robotMatrix[i][j].setType(Cell.CellType.EMPTY);
                    robotMatrix[i][j] = null;
                }
            }
        }
    }

    /**
     * Sets the direction of the Robot
     * @param dir Possible values: N, S, E, W
     */

    private static void setRobotDirection(String dir){
        //int xHead =1 , yHead = 2; // Default is N
        int xHead, yHead;
        switch(dir){
            case("N"): {
                xHead = 1; yHead = 2;
                robotDir = dir;
                break;
            }
            case("S"): {
                xHead = 1; yHead = 0;
                robotDir = dir;
                break;
            }
            case("E"): {
                xHead = 2; yHead = 1;
                robotDir = dir;
                break;
            }
            case("W"): {
                xHead = 0; yHead = 1;
                robotDir = dir;
                break;
            }
            default:
                return;
        }

        // Update robot direction
        for (int i=0; i<robotMatrix[0].length; i++){ // iterate through cols: i = x coordinate
            for (int j=0; j<robotMatrix.length; j++){ // iterate through cols: j = y coordinate
                if (i==xHead && j==yHead) robotMatrix[i][j].setType(Cell.CellType.ROBOT_HEAD);
                else robotMatrix[i][j].setType(Cell.CellType.ROBOT_BODY); // reset old head
            }
        }
    }

    /**
     * Check whether at least one of the new robot cells is obstacle
     * @param xCenter x Coordinate of new centre of robot
     * @param yCenter y Coordinate of new centre of robot
     * @param obstacles list of plotted obstacles
     */
    private static boolean checkObs(int xCenter,int yCenter,ArrayList<Obstacle> obstacles){
        int yTopLeft=yCenter-1, xTopLeft= xCenter-1;
        for (int i=0; i<robotMatrix[0].length; i++){ // iterate through rows: i = x coordinate
            for (int j=0; j<robotMatrix.length; j++){ // iterate through cols: j = y coordinate
                for(Obstacle obs: obstacles ){
                    if((obs.getCol() == xTopLeft+i) &&(obs.getRow() == yTopLeft+j)){
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public static void moveRobot(String dir,String movement,ArrayList<Obstacle> obstacles){
        switch(movement){
            case("F"):
            case("B"):
                forwardBackwardMove(dir,movement,obstacles);
                break;
            case("L"):
                turnLeft(dir,obstacles);
                break;
            case("BL"):
                reverseLeft(dir,obstacles);
                break;
            case("R"):
                turnRight(dir,obstacles);
                break;
            case("BR"):
                reverseRight(dir,obstacles);
                break;
        }
    }

    public static boolean isWithinBounds(int xCenter, int yCenter) {
        int xTopLeft = xCenter - 1;
        int yTopLeft = yCenter - 1;
        if (xTopLeft < 0 || xTopLeft + 2 > 19 || yTopLeft < 0 || yTopLeft + 2 > 19) {
            System.out.println("Out of bounds: Robot needs nine cells");
            return false;
        }
        return true;
    }

    private static void forwardBackwardMove(String dir, String movement, ArrayList<Obstacle> obstacles) {
        int xCenter = robotMatrix[1][1].col;
        int yCenter = robotMatrix[1][1].row;
        int newX = xCenter, newY = yCenter;

        switch (dir) {
            case "N":
                newY += (movement.equals("F")) ? 1 : -1;
                break;
            case "E":
                newX += (movement.equals("F")) ? 1 : -1;
                break;
            case "S":
                newY += (movement.equals("F")) ? -1 : 1;
                break;
            case "W":
                newX += (movement.equals("F")) ? -1 : 1;
                break;
            default:
                return;
        }

        if (isWithinBounds(newX, newY)) {
            // Update xCenter and yCenter to the proposed values after checking bounds
            xCenter = newX;
            yCenter = newY;

            setRobot(xCenter, yCenter, dir, obstacles);
        }
        else
            robotDir = dir;
    }

    private static void turnLeft(String dir, ArrayList<Obstacle> obstacles){
        int xCenter = robotMatrix[1][1].col;
        int yCenter = robotMatrix[1][1].row;
        int newX = xCenter, newY = yCenter;
        String newDir;

        switch (dir){
            case "N":
                newX -= numGrids;
                newY += numGrids;
                newDir = "W";
                break;
            case "S":
                newX += numGrids;
                newY -= numGrids;
                newDir = "E";
                break;
            case "E":
                newX += numGrids;
                newY += numGrids;
                newDir = "N";
                break;
            case "W":
                newX -= numGrids;
                newY -= numGrids;
                newDir = "S";
                break;
            default:
                return;
        }

        if (isWithinBounds(newX, newY)) {
            // Update xCenter and yCenter to the proposed values after checking bounds
            xCenter = newX;
            yCenter = newY;

            setRobot(xCenter, yCenter, newDir, obstacles);
        }
        else
            robotDir = dir;
    }

    private static void turnRight(String dir,ArrayList<Obstacle> obstacles){
        int xCenter = robotMatrix[1][1].col;
        int yCenter = robotMatrix[1][1].row;
        int newX = xCenter, newY = yCenter;
        String newDir;

        switch (dir){
            case"N":
                newX +=numGrids;
                newY +=numGrids;
                newDir = "E";
                break;
            case"S":
                newX -=numGrids;
                newY -=numGrids;
                newDir = "W";
                break;
            case"E":
                newX +=numGrids;
                newY -=numGrids;
                newDir = "S";
                break;
            case"W":
                newX -=numGrids;
                newY +=numGrids;
                newDir = "N";
                break;
            default:
                return;

        }

        if (isWithinBounds(newX, newY)) {
            // Update xCenter and yCenter to the proposed values after checking bounds
            xCenter = newX;
            yCenter = newY;

            setRobot(xCenter, yCenter, newDir, obstacles);
        }
        else
            robotDir = dir;

    }

    private static void reverseRight(String dir, ArrayList<Obstacle> obstacles){
        int xCenter = robotMatrix[1][1].col;
        int yCenter = robotMatrix[1][1].row;
        int newX = xCenter, newY = yCenter;
        String newDir;

        switch (dir) {
            case "N":
                newX += numGrids;
                newY -= numGrids;
                newDir = "W";
                break;
            case "S":
                newX -= numGrids;
                newY += numGrids;
                newDir = "E";
                break;
            case "E":
                newX -= numGrids;
                newY -= numGrids;
                newDir = "N";
                break;
            case "W":
                newX += numGrids;
                newY += numGrids;
                newDir = "S";
                break;
            default:
                return;
        }

        if (isWithinBounds(newX, newY)) {
            // Update xCenter and yCenter to the proposed values after checking bounds
            xCenter = newX;
            yCenter = newY;

            setRobot(xCenter, yCenter, newDir, obstacles);
        }
        else
            robotDir = dir;
    }

    private static void reverseLeft(String dir, ArrayList<Obstacle> obstacles){
        int xCenter = robotMatrix[1][1].col;
        int yCenter = robotMatrix[1][1].row;
        int newX = xCenter, newY = yCenter;
        String newDir;

        switch (dir) {
            case "N":
                newX -= numGrids;
                newY -= numGrids;
                newDir = "E";
                break;
            case "S":
                newX += numGrids;
                newY += numGrids;
                newDir = "W";
                break;
            case "E":
                newX -= numGrids;
                newY += numGrids;
                newDir = "S";
                break;
            case "W":
                newX += numGrids;
                newY -= numGrids;
                newDir = "N";
                break;
            default:
                return;
        }
        if (isWithinBounds(newX, newY)) {
            // Update xCenter and yCenter to the proposed values after checking bounds
            xCenter = newX;
            yCenter = newY;

            setRobot(xCenter, yCenter, newDir, obstacles);
        }
        else
            robotDir = dir;
    }
}
