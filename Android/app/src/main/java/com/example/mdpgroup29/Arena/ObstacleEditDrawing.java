package com.example.mdpgroup29.Arena;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.View;

import androidx.annotation.Nullable;

import com.example.mdpgroup29.R;

public class ObstacleEditDrawing extends View{
    //    public Obstacle obstacle;
    public Integer x,y, imageID;
    public Obstacle.ImageDirection imageDir, stringID;
    private Paint obstaclePaint,obstacleHeadPaint,obstacleImageIDPaint,obstacleNumPaint;
    public ObstacleEditDrawing(Context context) {
        super(context);
        obstaclePaint = new Paint();
        obstaclePaint.setColor(getResources().getColor(R.color.obstacle));
        obstacleImageIDPaint = new Paint();
        obstacleImageIDPaint.setColor(getResources().getColor(R.color.obstacleNumber));
        obstacleNumPaint = new Paint();
        obstacleNumPaint.setColor(getResources().getColor(R.color.obstacleNumber));
        obstacleHeadPaint = new Paint();
        obstacleHeadPaint.setColor(getResources().getColor(R.color.obstacleHead));
    }
    @Override
    protected  void onDraw(Canvas canvas){
        super.onDraw(canvas);
        int canvasWidth = canvas.getWidth();
        int canvasHeight = canvas.getHeight();
        RectF cellRect = new RectF((1f), (1f), (1f)*canvasWidth, (1f)*canvasHeight);
        int cellRadius = 40;
        canvas.drawRoundRect(cellRect, // rect
                cellRadius, // rx
                cellRadius, // ry
                obstaclePaint // Paint
        );
        RectF topRect = new RectF((1f), (1f), 1f*canvasWidth, (1f/5)*canvasHeight);
        RectF leftRect = new RectF((1f), (1f), (1f/5)*canvasWidth, (1f)*canvasHeight);
        RectF rightRect = new RectF(canvasWidth, (1f), (1f/1.25f)*canvasWidth, (1f)*canvasHeight);
        RectF bottomRect = new RectF((1f), canvasHeight, 1f*canvasWidth, (1f/1.25f)*canvasHeight);
        if(imageDir.equals(Obstacle.ImageDirection.NORTH)){
            canvas.drawRoundRect(topRect,cellRadius,cellRadius,obstacleHeadPaint);
        }else if(imageDir.equals(Obstacle.ImageDirection.WEST)){
            canvas.drawRoundRect(leftRect,cellRadius,cellRadius,obstacleHeadPaint);
        }else if(imageDir.equals(Obstacle.ImageDirection.EAST)){
            canvas.drawRoundRect(rightRect,cellRadius,cellRadius,obstacleHeadPaint);
        }else if(imageDir.equals(Obstacle.ImageDirection.SOUTH)){
            canvas.drawRoundRect(bottomRect,cellRadius,cellRadius,obstacleHeadPaint);
        }
        obstacleNumPaint.setTextAlign(Paint.Align.CENTER);
        obstacleNumPaint.setTextSize(90);
        int xPos = (canvas.getWidth() / 2);
        int yPos = (int) ((canvas.getHeight() / 2)- ((obstacleNumPaint.descent() + obstacleNumPaint.ascent()) / 2)) ;
        canvas.drawText(Integer.toString(imageID), xPos, yPos, obstacleNumPaint);

    }

}
