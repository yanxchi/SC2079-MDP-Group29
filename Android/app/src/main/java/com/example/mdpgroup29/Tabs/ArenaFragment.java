package com.example.mdpgroup29.Tabs;

import android.os.Bundle;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.example.mdpgroup29.R;


public class ArenaFragment extends Fragment {

    View view;
    public Button setRobotBtn;
    public Button setObstaclesBtn;

    public boolean isSetRobot;
    public boolean isSetObstacles;
    private boolean isRobotMove;
    private boolean isRobotStop;
    private boolean isReset;
    private AppDataModel appDataModel;


    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        isSetRobot = false;
        isSetObstacles = false;
        isRobotMove = false;
        isRobotStop = false;
        isReset = false;
        // Inflate the layout for this fragment
        view = inflater.inflate(R.layout.fragment_arena, container, false);
        setRobotBtn = view.findViewById(R.id.setRobotButton);
        setObstaclesBtn = view.findViewById(R.id.setObstacleButton);
        appDataModel = new ViewModelProvider(requireActivity()).get(AppDataModel.class);
        appDataModel.setIsSetObstacles(isSetObstacles);
        appDataModel.setIsSetRobot(isSetRobot);

        setRobotBtn.setOnClickListener(item ->{
            if(isSetObstacles){
                isSetObstacles = false;
                setObstaclesBtn.setText(R.string.set_obstacle);
                setObstaclesBtn.setBackgroundColor(getResources().getColor(R.color.accent));
                isSetRobot = btnAction(isSetRobot, setRobotBtn, "robot");
            }else{
                isSetRobot = btnAction(isSetRobot, setRobotBtn, "robot");
            }
            appDataModel.setIsSetObstacles(isSetObstacles);
            appDataModel.setIsSetRobot(isSetRobot);
        });
        setObstaclesBtn.setOnClickListener(item ->{
            if(isSetRobot){
                isSetRobot = false;
                setRobotBtn.setText(R.string.set_robot);
                setRobotBtn.setBackgroundColor(getResources().getColor(R.color.accent));
                isSetObstacles = btnAction(isSetObstacles, setObstaclesBtn, "obstacles");
            }else{
                isSetObstacles = btnAction(isSetObstacles, setObstaclesBtn, "obstacles");
            }

            appDataModel.setIsSetObstacles(isSetObstacles);
            appDataModel.setIsSetRobot(isSetRobot);
        });

        return view;
    }

    public boolean isSetRobot() {
        return isSetRobot;
    }

    public void setSetRobot(boolean setRobot) {
        isSetRobot = setRobot;
    }

    public boolean isSetObstacles() {
        return isSetObstacles;
    }

    public void setSetObstacles(boolean setObstacles) {
        isSetObstacles = setObstacles;
    }

    public boolean isRobotMove() {
        return isRobotMove;
    }

    public void setRobotMove(boolean robotMove) {
        isRobotMove = robotMove;
    }

    public boolean isRobotStop() {
        return isRobotStop;
    }

    public void setRobotStop(boolean robotStop) {
        isRobotStop = robotStop;
    }

    public boolean isReset() {
        return isReset;
    }

    public void setReset(boolean reset) {
        isReset = reset;
    }

    private boolean btnAction(boolean btnVal, Button btn, String btnText){
        if(btnVal){
            btnVal = false;
            btn.setText(String.format(getString(R.string.set_btn_txt), btnText));
            btn.setBackgroundColor(getResources().getColor(R.color.accent));
        }
        else{
            btnVal = true;
            btn.setText(R.string.done);
            btn.setBackgroundColor(getResources().getColor(R.color.doneButton));
        }
        return btnVal;
    }
}