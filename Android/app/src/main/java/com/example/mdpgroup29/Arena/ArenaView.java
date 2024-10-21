package com.example.mdpgroup29.Arena;

import android.app.AlertDialog;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.annotation.Nullable;

import com.example.mdpgroup29.Bluetooth.BluetoothService;
import com.example.mdpgroup29.R;
import com.example.mdpgroup29.Tabs.AppDataModel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;


public class ArenaView extends View {
    //Zoom & Scroll
    private static float MIN_ZOOM = 1f;
    private static float MAX_ZOOM = 5f;
    private float scaleFactor = 1.f;
    private ScaleGestureDetector detector;
    private Rect clipBoundsCanvas;
    private static int NONE = 0;
    private static int DRAG = 1;
    private static int ZOOM = 2;
    private int mode;
    private float startX = 0f;
    private float startY = 0f;
    private float translateX = 0f;
    private float translateY = 0f;
    private float previousTranslateX = 0f;
    private float previousTranslateY = 0f;
    private boolean dragged;
    private AppDataModel appDataModel;

    private BluetoothService btService;


    //Arena
    public Cell[][] cells;
    public Map<Cell, RectF> gridMap;
    public ArrayList<Obstacle> obstacles;
    public Obstacle editingObs;
    public int editingObs_orig_x;
    public int editingObs_orig_y;
    public static final int COLS = 20, ROWS = 20;
    public boolean isEditMap, isSetRobot, isSetObstacles,obstacleSelected, obstacleEdit;
    private float cellSize, hMargin, vMargin;
    private final Paint wallPaint,gridPaint,textPaint, robotBodyPaint, robotHeadPaint,obstaclePaint,
            exploredGridPaint, obstacleNumPaint, obstacleImageIDPaint, gridNumberPaint, obstacleHeadPaint,exploredObstaclePaint;
    Cell maxRight,maxLeft;

    public ArenaView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        gridMap = new HashMap<Cell, RectF>();
        obstacles = new ArrayList<Obstacle>();
        cells = new Cell[COLS][ROWS];
        clipBoundsCanvas = new Rect();
        createArena();
        Robot.initializeRobot(cells);
        detector = new ScaleGestureDetector(getContext(), new ScaleListener());
        wallPaint = new Paint();
        wallPaint.setColor(getResources().getColor(R.color.transparent));
        gridPaint = new Paint();
        gridPaint.setColor(getResources().getColor(R.color.fontColor));
        exploredGridPaint = new Paint();
        exploredGridPaint.setColor(getResources().getColor(R.color.exploredGrid));
        textPaint = new Paint();
        textPaint.setColor(getResources().getColor(R.color.fontColor));
        robotBodyPaint = new Paint();
        robotBodyPaint.setColor(getResources().getColor(R.color.robotBody));
        robotHeadPaint = new Paint();
        robotHeadPaint.setColor(getResources().getColor(R.color.robotHead));
        obstaclePaint = new Paint();
        obstaclePaint.setColor(getResources().getColor(R.color.obstacle));
        obstacleImageIDPaint = new Paint();
        obstacleImageIDPaint.setColor(getResources().getColor(R.color.fontColor));
        obstacleImageIDPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        obstacleNumPaint = new Paint();
        obstacleNumPaint.setColor(getResources().getColor(R.color.obstacleNumber));
        obstacleHeadPaint = new Paint();
        obstacleHeadPaint.setColor(getResources().getColor(R.color.obstacleHead));
        exploredObstaclePaint = new Paint();
        exploredObstaclePaint.setColor(getResources().getColor(R.color.exploredObstacle));
        gridNumberPaint = new Paint();
        gridNumberPaint.setColor(getResources().getColor(R.color.fontColor));
    }

    public void getBluetoothService(BluetoothService btService)
    {
        this.btService = btService;
    }

    private void createArena(){
        RectF curRect;
        for (int x = 0; x < COLS; x++){
            for (int y = 0; y < ROWS; y++){
                cells[x][y] = new Cell(x, y, Cell.CellType.EMPTY);
                curRect = new RectF();
                gridMap.put(cells[x][y], curRect);
            }
        }
    }

    //called whenever object of the class is called
    @Override
    protected  void onDraw(Canvas canvas){
        canvas.getClipBounds(clipBoundsCanvas);
        canvas.drawColor(getResources().getColor(R.color.transparent));
        int width = getWidth();
        int height = getHeight();
        if (width/height < COLS/ROWS)
            cellSize = width/(COLS+2);
        else
            cellSize = height/(ROWS+2);
        obstacleImageIDPaint.setTextSize(cellSize/2);
        obstacleNumPaint.setTextSize(cellSize/3);
        gridNumberPaint.setTextSize(cellSize/2);
        hMargin = (width-(COLS+1)*cellSize)/2; //distance from the left border
        vMargin = (height-(ROWS+1)*cellSize)/2; //distance from the top border
        canvas.translate(hMargin,vMargin); // shift to margin
        canvas.scale(scaleFactor, scaleFactor);

        if((translateX * -1) < 0) {
            translateX = 0;
        }
        else if((translateX * -1) > (scaleFactor - 1) * width) {
            translateX = (1 - scaleFactor) * width;
        }
        if(translateY * -1 < 0) {
            translateY = 0;
        }
        else if((translateY * -1) > (scaleFactor - 1) * height) {
            translateY = (1 - scaleFactor) * height;
        }
        canvas.translate(translateX / scaleFactor, translateY / scaleFactor);

        //draw grid numbers
        for (int i=0; i<COLS; i++){
            plotSquare(canvas, 0, ROWS - i - 1, wallPaint, gridNumberPaint, String.valueOf(i)); //for row numbering
            plotSquare(canvas,i+1,COLS, wallPaint, gridNumberPaint, String.valueOf(i)); //for column numbering
        }

        for (int x = 1; x < COLS+1; x++) { // col 0 is for grid number
            for (int y = 0; y < ROWS; y++) { // row ROWS is for grid number

                // Invert y-coordinate
                int invertedY = (ROWS - 1) - y;

                // Paint normal cell
                RectF cellRect = gridMap.get(cells[x-1][y]);
                if (cellRect != null) {
                    cellRect.set((x + 0.1f) * cellSize, (invertedY + 0.1f) * cellSize, (x + 1f) * cellSize, (invertedY + 1f) * cellSize);
                    int cellRadius = 10;
                    canvas.drawRoundRect(cellRect, cellRadius, cellRadius, gridPaint);
                }
            }
        }


        // Paint Obstacles
        for(int i = 0; i < obstacles.size(); i++){
            // Default: Paint obstacle with no Image ID
            int id = obstacles.get(i).getObstacleID();
            Paint txtPaint = obstacleNumPaint;
            Paint obsPaint = obstaclePaint;
            // Paint obstacle with Image ID
            if (obstacles.get(i).getImageID()!=-1) {
                id = obstacles.get(i).getImageID();
                txtPaint = obstacleImageIDPaint;
                obsPaint = exploredObstaclePaint;
            }
            String message = Integer.toString(obstacles.get(i).getRow());
            plotSquare(canvas,(float) obstacles.get(i).getCol()+1,19 - (float) obstacles.get(i).getRow(), obsPaint, txtPaint, String.valueOf(id));
            plotObstacleDir(canvas,obstacles.get(i));
        }

        if (Robot.robotMatrix[0][0] != null){// Skip below if Robot not initialized
            // Paint Robot
            Cell robotCell;
            Paint robotPaint;
            for (int i=0; i<Robot.robotMatrix[0].length; i++){ // iterate through rows: i = x coordinate
                for (int j=0; j<Robot.robotMatrix.length; j++){ // iterate through cols: j = y coordinate
                    robotCell = Robot.robotMatrix[i][j];
                    if(robotCell.getType()==Cell.CellType.ROBOT_HEAD){
                        robotPaint = robotHeadPaint;
                    }
                    else if(robotCell.getType()== Cell.CellType.ROBOT_BODY) robotPaint = robotBodyPaint;
                    else robotPaint = gridPaint;
                    plotSquare(canvas,(float) robotCell.getCol()+1,19 - (float) robotCell.getRow(), robotPaint, null, null);
                }
            }
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event){
        if (!isSetObstacles && !isSetRobot && !obstacleEdit){
            scaleGrid(event);
            return true;
        }
        if(isSetObstacles || isSetRobot){
            isEditMap = true;
        }

        float x = (event.getX()-hMargin)/scaleFactor - translateX / scaleFactor + clipBoundsCanvas.left;
        float y = (event.getY()-vMargin)/scaleFactor - translateY / scaleFactor + clipBoundsCanvas.top;
        Cell curCell;
        RectF curRect;

        for (Map.Entry<Cell, RectF> entry : gridMap.entrySet()) {
            curCell = entry.getKey();
            curRect = entry.getValue();
            if(curCell.col== 0 && curCell.row == 0){
                maxLeft = entry.getKey();
            }else if(curCell.col== 19 && curCell.row == 19){
                maxRight = entry.getKey();
            }
            if(curRect != null && curCell != null) {
                float rectX = curRect.centerX();
                float rectY = curRect.centerY();
                if (curRect.contains(x , y )) {
                    System.out.println(x + " : " + y + " : " + rectX + " : " + rectY + " : " + hMargin + " : " + vMargin + " : " + cellSize);
                    System.out.println("Coordinates: (" + curCell.col + "," + curCell.row + ")");
                    if(isEditMap){
                        if(isSetObstacles){
                            if(!obstacleSelected){
                                if(curCell.getType() == Cell.CellType.EMPTY && event.getAction()==MotionEvent.ACTION_UP){
                                    curCell.setType(Cell.CellType.OBSTACLE);
                                    obstacles.add(new Obstacle(curCell.getCol(), curCell.getRow(), obstacles.size()+1));
                                    invalidate();
                                    String direction0 = "NORTH";
                                    if(obstacles.get(obstacles.size() - 1).getImageDirection() == Obstacle.ImageDirection.NORTH){
                                        direction0 = "NORTH";
                                    } else if (obstacles.get(obstacles.size() - 1).getImageDirection() == Obstacle.ImageDirection.SOUTH) {
                                        direction0 = "SOUTH";
                                    } else if (obstacles.get(obstacles.size() - 1).getImageDirection() == Obstacle.ImageDirection.WEST) {
                                        direction0 = "WEST";
                                    } else if (obstacles.get(obstacles.size() - 1).getImageDirection() == Obstacle.ImageDirection.EAST) {
                                        direction0 = "EAST";
                                    }
                                    this.btService.write(String.format("Obstacle set at (%d,%d) facing (%s)", curCell.col, curCell.row, direction0), false);
                                    break;
                                } else if (curCell.getType()== Cell.CellType.OBSTACLE){
                                    for(Obstacle obstacle: obstacles){
                                        if(obstacle.getCol() == curCell.getCol() && obstacle.getRow() == curCell.getRow()){
                                            editingObs = obstacle;
                                            editingObs_orig_x = obstacle.getCol();
                                            editingObs_orig_y = obstacle.getRow();
                                        }
                                    }
                                    obstacleSelected = true;
                                    System.out.println("Obstacle Selected");
                                }
                            } else if(obstacleSelected && event.getAction()==MotionEvent.ACTION_UP){
                                if(curCell.getCol() == editingObs.getCol() && curCell.getRow() == editingObs.getRow() && curCell.getType()==Cell.CellType.EMPTY){
                                    curCell.setType(Cell.CellType.OBSTACLE);
                                    String direction1 = "NORTH";
                                    if(editingObs.getImageDirection() == Obstacle.ImageDirection.NORTH){
                                        direction1 = "NORTH";
                                    } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.SOUTH) {
                                        direction1 = "SOUTH";
                                    } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.WEST) {
                                        direction1 = "WEST";
                                    } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.EAST) {
                                        direction1 = "EAST";
                                    }
                                    this.btService.write(String.format("Obstacle set at (%d,%d) facing (%s)", curCell.col, curCell.row, direction1), false);
                                }
                                invalidate();
                                obstacleSelected = false;
                            } else if(obstacleSelected && event.getAction()==MotionEvent.ACTION_MOVE){
                                cells[editingObs.getCol()][editingObs.getRow()].setType(Cell.CellType.EMPTY);
                                dragObstacle(event, entry.getKey(), editingObs);
                            }

                            // Here is the code for rotating obstacle direction
                            if (curCell.getType() == Cell.CellType.OBSTACLE && event.getAction() == MotionEvent.ACTION_UP) {
                                for (Obstacle obstacle : obstacles) {
                                    if (obstacle.getCol() == curCell.getCol() && obstacle.getRow() == curCell.getRow()) {
                                        rotateObstacleDirection(obstacle);  // Rotate obstacle direction

                                        String newDirection = "NORTH";
                                        if (obstacle.getImageDirection() == Obstacle.ImageDirection.NORTH) {
                                            newDirection = "NORTH";
                                        } else if (obstacle.getImageDirection() == Obstacle.ImageDirection.SOUTH) {
                                            newDirection = "SOUTH";
                                        } else if (obstacle.getImageDirection() == Obstacle.ImageDirection.WEST) {
                                            newDirection = "WEST";
                                        } else if (obstacle.getImageDirection() == Obstacle.ImageDirection.EAST) {
                                            newDirection = "EAST";
                                        }

                                        // Send the updated direction via Bluetooth
                                        this.btService.write(String.format("Obstacle at (%d,%d) now facing (%s)",
                                                obstacle.getCol(), obstacle.getRow(), newDirection), false);

                                        break;
                                    }
                                }
                                return true;
                            }

                        } else if(isSetRobot){
                            setRobot(curCell.getCol(), curCell.getRow(), "N");

                            if (event.getAction()==MotionEvent.ACTION_UP) {
                                System.out.println("Robot is set.");
                                this.btService.write(String.format("Robot set at (%d, %d) facing %s", curCell.col, curCell.row, "N"), false);
                            }
                        }
                    } else {
                        obstacleEdit = false;
                    }
                } else if(obstacleSelected && editingObs != null && isSetObstacles){
                    if(event.getAction() ==MotionEvent.ACTION_MOVE){
                        if(x < gridMap.get(maxLeft).centerX() || x > gridMap.get(maxRight).centerX()){
                            if(editingObs != null){
                                cells[editingObs.getCol()][editingObs.getRow()].setType(Cell.CellType.EMPTY);
                                int deletedId = editingObs.getObstacleID();
                                obstacles.remove(editingObs);
                                obstacleSelected = false;
                                for(Obstacle obs: obstacles){
                                    if(obs.getObstacleID() > deletedId){
                                        obs.setObstacleID(obs.getObstacleID()-1);
                                    }
                                }
                                invalidate();
                                String direction = "NORTH";
                                if(editingObs.getImageDirection() == Obstacle.ImageDirection.NORTH){
                                    direction = "NORTH";
                                } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.SOUTH) {
                                    direction = "SOUTH";
                                } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.WEST) {
                                    direction = "WEST";
                                } else if (editingObs.getImageDirection() == Obstacle.ImageDirection.EAST) {
                                    direction = "EAST";
                                }
                                this.btService.write(String.format("Obstacle removed from (%d,%d) facing (%s)", editingObs_orig_x, editingObs_orig_y, direction), false);
                            }
                        }
                    }
                }
            }
        }
        return true;
    }

    // Method to rotate the obstacle direction
    private void rotateObstacleDirection(Obstacle obstacle) {
        switch (obstacle.getImageDirection()) {
            case NORTH:
                obstacle.setImageDirection(Obstacle.ImageDirection.EAST);
                break;
            case EAST:
                obstacle.setImageDirection(Obstacle.ImageDirection.SOUTH);
                break;
            case SOUTH:
                obstacle.setImageDirection(Obstacle.ImageDirection.WEST);
                break;
            case WEST:
                obstacle.setImageDirection(Obstacle.ImageDirection.NORTH);
                break;
        }
        invalidate(); // Redraw the grid to reflect the updated direction
    }

    private void scaleGrid(MotionEvent event){
        isEditMap = false;
        float x = event.getX();
        float y = event.getY();
        Cell curCell;
        RectF curRect;
        for (Map.Entry<Cell, RectF> entry : gridMap.entrySet()) {
            curCell = entry.getKey();
            curRect = entry.getValue();
            if(curRect != null && curCell != null) {
                float rectX = curRect.centerX();
                float rectY = curRect.centerY();
                float translateRectX;
                float translateRectY;

                switch (event.getAction() & MotionEvent.ACTION_MASK) {

                    case MotionEvent.ACTION_DOWN:
                        mode = DRAG;
                        startX = x - previousTranslateX;
                        startY = y - previousTranslateY;
                        break;

                    case MotionEvent.ACTION_MOVE:
                        if (scaleFactor == 1f) break;
                        translateX = x - startX;
                        translateY = y - startY;
                        double distance = Math.sqrt(Math.pow(x - (startX + previousTranslateX), 2) +
                                Math.pow(y - (startY + previousTranslateY), 2)
                        );

                        if(distance > 0) {
                            dragged = true;
                        }
                        break;

                    case MotionEvent.ACTION_POINTER_DOWN:
                        mode = ZOOM;
                        break;

                    case MotionEvent.ACTION_UP:
                        mode = NONE;
                        dragged = false;
                        previousTranslateX = translateX;
                        previousTranslateY = translateY;
                        setObstacleEdit(event,curCell,curRect);
                        break;
                }
            }
        }
        detector.onTouchEvent(event);

        if ((mode == DRAG && scaleFactor != 1f && dragged) || mode == ZOOM) {
            invalidate();
        }
    }

    private void dragObstacle(MotionEvent event, Cell curCell, Obstacle obstacle){
        int index = obstacles.indexOf(obstacle);
        try{
            if(curCell.getType()==Cell.CellType.EMPTY){
                switch (event.getAction()) {
                    case MotionEvent.ACTION_UP:
                        if(obstacles.size() != 0){
                            curCell.setType(Cell.CellType.OBSTACLE);
                            obstacles.get(index).setCol(curCell.getCol());
                            obstacles.get(index).setRow(curCell.getRow());
                            obstacleSelected = false;
                        }
                        break;
                    default:
                        if(obstacles.size() != 0){
                            obstacleSelected = true;
                            curCell.setType(Cell.CellType.EMPTY);
                            obstacles.get(index).setCol(curCell.getCol());
                            obstacles.get(index).setRow(curCell.getRow());
                        }

                        break;
                }
            }
        }catch (Exception e){
            System.out.print(e);
        }

        invalidate();
    }
    private void setObstacleEdit(MotionEvent event, Cell curCell, RectF curRect){
        float x = (event.getX()-hMargin)/scaleFactor - translateX / scaleFactor + clipBoundsCanvas.left;
        float y = (event.getY()-vMargin)/scaleFactor - translateY / scaleFactor + clipBoundsCanvas.top;
        if (curRect.contains(x , y )) {
            for(Obstacle obstacle: obstacles){
                if(obstacle.getCol() == curCell.getCol() && obstacle.getRow() == curCell.getRow()){
                    obstacleEdit = true;
                    editingObs = obstacle;
                    if (dataEventListener != null) {
                        dataEventListener.onEventOccurred();
                    }
                }
            }
        }

    }
    // Plot the individual cells
    private void plotSquare(Canvas canvas, float x, float y, Paint paint, Paint numPaint, String text){
        RectF cellRect = new RectF(
                (x+0.1f)*cellSize,
                (y+0.1f)*cellSize,
                (x+1f)*cellSize,
                (y+1f)*cellSize);
        int cellRadius = 10;
        canvas.drawRoundRect(cellRect, // rectf
                cellRadius, // rx
                cellRadius, // ry
                paint // Paint
        );
        // draw number on obstacle
        if (text != null){
            float cellWidth = ((x+1f)*cellSize - (x+0.1f)*cellSize);
            float cellHeight = ((y+1f)*cellSize - (y+0.1f)*cellSize);
            Rect bounds = new Rect();
            numPaint.getTextBounds(text, 0, text.length(), bounds);
            canvas.drawText(text,
                    ((x+0.1f)*cellSize + cellWidth / 2f - bounds.width() / 2f - bounds.left),
                    ((y+0.1f)*cellSize + cellHeight / 2f + bounds.height() / 2f - bounds.bottom),
                    numPaint);
        }
    }
    private void plotObstacleDir(Canvas canvas,Obstacle obstacle){
        RectF cellRect = new RectF(0,0,0,0);
        // For all plotting of rectangles, need to +1 to the col value to account for the grid numbers
        switch (obstacle.getImageDirection()) {
            case NORTH:
                cellRect = new RectF((obstacle.getCol() + 1.2f) * cellSize, ((19 - obstacle.getRow()) + 0.1f) * cellSize,
                        (obstacle.getCol() + 1.9f) * cellSize, ((19 - obstacle.getRow()) + 0.25f) * cellSize);
                break;
            case WEST:
                cellRect = new RectF((obstacle.getCol() + 1.1f) * cellSize, ((19 - obstacle.getRow()) + 0.2f) * cellSize,
                        (obstacle.getCol() + 1.25f) * cellSize, ((19 - obstacle.getRow()) + 0.9f) * cellSize);
                break;
            case EAST:
                cellRect = new RectF((obstacle.getCol() + 1.85f) * cellSize, ((19 - obstacle.getRow()) + 0.2f) * cellSize,
                        (obstacle.getCol() + 2f) * cellSize, ((19 - obstacle.getRow()) + 0.9f) * cellSize);
                break;
            case SOUTH:
                cellRect = new RectF((obstacle.getCol() + 1.2f) * cellSize, ((19 - obstacle.getRow()) + 0.85f) * cellSize,
                        (obstacle.getCol() + 1.9f) * cellSize, ((19 - obstacle.getRow()) + 1f) * cellSize);
                break;
        }
        int cellRadius = 10;
        canvas.drawRoundRect(cellRect, cellRadius, cellRadius, obstacleHeadPaint);
    }


    public boolean setObstacleImageID(int obstacleNumber, int imageID){
        if (-1 < obstacleNumber-1 && obstacleNumber-1 < obstacles.size()) {
            Obstacle obs = obstacles.get(obstacleNumber-1);
            obs.setImageID(imageID);
            invalidate();
            return true;
        } else {
            return false;
        }
    }

    public Boolean setRobot(int xCenter, int yCenter,  String dir){
        if(yCenter<1 || yCenter>=ROWS-1 || xCenter>=COLS-1 || xCenter<1){
            System.out.println("Out of bound : Robot need nine cells");
            return false;
        }else{
            boolean valid = Robot.setRobot(xCenter, yCenter, dir,obstacles);
            invalidate();
            return valid;
        }
    }
    public String moveRobot(String dir,String movement){
        Robot.moveRobot(dir,movement,obstacles);
        invalidate();
        return Robot.robotDir;
    }

    private class ScaleListener extends ScaleGestureDetector.SimpleOnScaleGestureListener {
        @Override
        public boolean onScale(ScaleGestureDetector detector) {
            scaleFactor *= detector.getScaleFactor();
            scaleFactor = Math.max(MIN_ZOOM, Math.min(scaleFactor, MAX_ZOOM));
            return true;
        }
    }

    public void clearArena() {
        for (int x = 0; x < COLS; x++) {
            for (int y = 0; y < ROWS; y++) {
                if (cells[x][y] instanceof Obstacle) {
                    cells[x][y].setType(Cell.CellType.EMPTY);  // Change type to EMPTY
                } else if (cells[x][y] != null) {
                    cells[x][y].setType(Cell.CellType.EMPTY);  // Ensure all cells are EMPTY
                }
            }

            if (obstacles != null) {
                obstacles.clear();  // Clear the list of obstacles
            }
            Robot.clearRobot();
            obstacles.clear();
            invalidate(); //redraw view
        }
    }

    //To listen arena view data changes on Main activity.
    public interface DataEventListener {
        public void onEventOccurred();
    }

    private DataEventListener dataEventListener;

    public void setEventListener(DataEventListener dataEventListener) {
        this.dataEventListener = dataEventListener;
    }

    public String findObstacle(int xCoord, int yCoord) {
        for (int i=0;i<obstacles.size();i++) {
            Obstacle obs = obstacles.get(i);
            if (obs.getCol() == xCoord && obs.getRow() == yCoord){
                return Integer.toString(i+1);
            }
        }
        return Integer.toString(0);
    }

}

