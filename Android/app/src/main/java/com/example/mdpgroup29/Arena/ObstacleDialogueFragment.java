package com.example.mdpgroup29.Arena;

import android.app.Activity;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RelativeLayout;
import android.widget.Spinner;

import androidx.annotation.Nullable;

import com.example.mdpgroup29.Bluetooth.BluetoothService;
import com.example.mdpgroup29.R;


public class ObstacleDialogueFragment extends android.app.DialogFragment{

    private RelativeLayout relativeLayout;
    private Spinner  imageDir;
    private EditText xPos,yPos;
    private Button cancelBtn, submitBtn;
    private ObstacleEditDrawing obstacleView;
    private static BluetoothService btService;
    String[] Directions = { "NORTH", "SOUTH", "EAST", "WEST" };
    public static ObstacleDialogueFragment newInstance(int obsIndex, String imageID, String imageDir, int x, int y, BluetoothService bt) {
//public static ObstacleDialogueFragment newInstance(int obsIndex, String imageID, String imageDir, int x, int y) {
    ObstacleDialogueFragment dialog = new ObstacleDialogueFragment();
        Bundle bundle = new Bundle();
        bundle.putString("OBSDIR",imageDir);
        bundle.putString("OBSID",imageID);
        bundle.putInt("OBSX",x);
        bundle.putInt("OBSY",y);
        bundle.putInt("OBSINDEX",obsIndex);
        dialog.setArguments(bundle);
        btService = bt;
        return dialog;
    }
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
//        obstacleView = new ObstacleEditDrawing(getActivity());
        return inflater.inflate(R.layout.dialog_edit_obstacle, container,false);
    }


    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        relativeLayout = view.findViewById(R.id.obstacleCanvas);
        obstacleView = new ObstacleEditDrawing(getActivity());
        relativeLayout.addView(obstacleView);

        cancelBtn = view.findViewById(R.id.cancelButton);
        submitBtn = view.findViewById(R.id.saveButton);

        xPos = view.findViewById(R.id.xCoordEditText);
        obstacleView.x = getArguments().getInt("OBSX");
//        xPos.setText(obstacleView.x.toString());
        yPos = view.findViewById(R.id.yCoordEditText);
        obstacleView.y = getArguments().getInt("OBSY");
        Integer convertedY = obstacleView.y;
        Integer convertedX = obstacleView.x;
//        yPos.setText(obstacleView.y.toString());
        xPos.setText(convertedX.toString());
        yPos.setText(convertedY.toString());

        imageDir = view.findViewById(R.id.imageDirectionSpinner);
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getActivity(), android.R.layout.simple_spinner_dropdown_item, Directions);
        adapter.setDropDownViewResource(android.R.layout.simple_dropdown_item_1line);
        imageDir.setAdapter(adapter);
        String spinnerVal = getArguments().getString("OBSDIR");
        int spinnerPos = adapter.getPosition(spinnerVal);
        imageDir.setSelection(spinnerPos);
        assert spinnerVal != null;
        if(spinnerVal.equals("NORTH")){
            obstacleView.imageDir = Obstacle.ImageDirection.NORTH;
        } else if(spinnerVal.equals("EAST")){
            obstacleView.imageDir = Obstacle.ImageDirection.EAST;
        } else if(spinnerVal.equals("SOUTH")){
            obstacleView.imageDir = Obstacle.ImageDirection.SOUTH;
        } else if(spinnerVal.equals("WEST")){
            obstacleView.imageDir = Obstacle.ImageDirection.WEST;
        }

        obstacleView.imageID = Integer.parseInt(getArguments().getString("OBSID"));
        imageDir.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {
                if(imageDir.getSelectedItem().toString().equals("NORTH"))
                {
                    obstacleView.imageDir = Obstacle.ImageDirection.NORTH;
                } else if(imageDir.getSelectedItem().toString().equals("EAST"))
                {
                    obstacleView.imageDir = Obstacle.ImageDirection.EAST;
                } else if(imageDir.getSelectedItem().toString().equals("SOUTH"))
                {
                    obstacleView.imageDir = Obstacle.ImageDirection.SOUTH;
                } else if(imageDir.getSelectedItem().toString().equals("WEST"))
                {
                    obstacleView.imageDir = Obstacle.ImageDirection.WEST;
                }
                obstacleView.invalidate();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {

            }

        });
        xPos.addTextChangedListener(new TextWatcher() {

            @Override
            public void afterTextChanged(Editable s) {
                if(s.length() != 0)
                    obstacleView.x = Integer.parseInt(s.toString());
            }

            @Override
            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                if(s.length() != 0){
                    obstacleView.x = Integer.parseInt(s.toString());
                }


            }
        });
        yPos.addTextChangedListener(new TextWatcher() {

            @Override
            public void afterTextChanged(Editable s) {
                if(s.length() != 0)
                    obstacleView.y = Integer.parseInt(s.toString());
                obstacleView.y = obstacleView.y;
            }

            @Override
            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                if(s.length() != 0){
                    obstacleView.y = Integer.parseInt(s.toString());
                    obstacleView.y = obstacleView.y;
                }


            }
        });


        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialogDataListener.setObstacleEdit(false);
                getDialog().dismiss();
            }
        });
        submitBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Obstacle.ImageDirection direction = Obstacle.ImageDirection.NORTH;

                if(imageDir.getSelectedItem().toString().equals("NORTH")){
                    direction = Obstacle.ImageDirection.NORTH;
                } else if(imageDir.getSelectedItem().toString().equals("EAST")){
                    direction = Obstacle.ImageDirection.EAST;
                } else if(imageDir.getSelectedItem().toString().equals("SOUTH")){
                    direction = Obstacle.ImageDirection.SOUTH;
                } else if(imageDir.getSelectedItem().toString().equals("WEST")){
                    direction = Obstacle.ImageDirection.WEST;
                }

                dialogDataListener.dialogData(getArguments().getInt("OBSINDEX"), direction, obstacleView.x, obstacleView.y);
                dialogDataListener.setObstacleEdit(false);
                getDialog().dismiss();
                btService.write(String.format("Obstacle set at (%d,%d) facing (%s)", obstacleView.x, obstacleView.y, imageDir.getSelectedItem().toString()), false);
            }
        });


    }
    public interface DialogDataListener {
        void dialogData(int obsIndex, Obstacle.ImageDirection direction, int x, int y);
        void setObstacleEdit(boolean obsEdit);
 }
    DialogDataListener dialogDataListener;
    @Override
    public void onAttach(Activity activity) {
        super.onAttach(activity);
        try {
            dialogDataListener = (DialogDataListener) activity;
        } catch (ClassCastException e) {
            throw new ClassCastException(activity.toString() + " must implement onSomeEventListener");
        }
    }
    @Override
    public void onPause() {
        super.onPause();
        dismissAllowingStateLoss();
    }
    @Override
    public void onDismiss(DialogInterface frag) {
        super.onDismiss(frag);
        // DO Something
    }


}
