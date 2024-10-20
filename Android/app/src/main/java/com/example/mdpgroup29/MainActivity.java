package com.example.mdpgroup29;

import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;
import androidx.viewpager2.widget.ViewPager2;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import android.content.IntentFilter;
import android.graphics.RectF;
import android.os.Bundle;
import android.os.Handler;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import android.widget.Button;

import com.example.mdpgroup29.Arena.ObstacleDialogueFragment;
import com.example.mdpgroup29.Arena.ArenaView;
import com.example.mdpgroup29.Arena.Cell;
import com.example.mdpgroup29.Arena.Obstacle;
import com.example.mdpgroup29.Arena.Robot;
import com.example.mdpgroup29.Tabs.AppDataModel;
import com.example.mdpgroup29.Bluetooth.DeviceList;
import com.example.mdpgroup29.Tabs.ChatFragment;
import com.example.mdpgroup29.Tabs.TabAdapter;
import com.example.mdpgroup29.Bluetooth.BluetoothService;

import com.google.android.material.tabs.TabLayout;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;

public class MainActivity extends AppCompatActivity implements ObstacleDialogueFragment.DialogDataListener {

    private ArenaView arena;
    private AppDataModel appDataModel;
    private BluetoothService btService;
    private BluetoothService.BluetoothLostReceiver btLostReceiver;
    private BtStatusChangedReceiver conReceiver;
    private boolean valid_pos;
    private boolean valid_target;
    private boolean valid_image;
    private final String DELIMITER = "/";
    public boolean DEBUG = false;
    public boolean RUN_TO_END = false;
    private final Handler timerHandler = new Handler();
    TimerRunnable timerRunnable = null;
    private List<String> moveList;
    private String curObsNum = "0";
    public String robotDir;
    ArrayList<double[]> pathCoordinates;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        BluetoothService.initialize(this);
        btService = new BluetoothService(this);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Make sure this points to your correct XML layout
        arena = findViewById(R.id.arena);
        pathCoordinates = new ArrayList<>();
        arena.getBluetoothService(btService);
        appDataModel = new ViewModelProvider(this).get(AppDataModel.class);
        appDataModel.getIsSetRobot().observe(this, data -> {
            arena.isSetRobot = data;
        });
        appDataModel.getIsSetObstacles().observe(this, data -> {
            arena.isSetObstacles = data;
        });
        arena.setEventListener(new ArenaView.DataEventListener() {
            @Override
            public void onEventOccurred() {
                if (arena.obstacleEdit) {
                    showObstacleDialog();
                }
            }
        });


        // ----------------------------------BLUETOOTH---------------------------------------------
        // Make device discoverable and accept connections
        btService.serverStartListen(this);
        // register event receivers
        registerReceiver(msgReceiver, new IntentFilter("message_received"));
        conReceiver = new BtStatusChangedReceiver(this);
        registerReceiver(conReceiver, new IntentFilter("bt_status_changed"));
        btLostReceiver = btService.new BluetoothLostReceiver(this);
        registerReceiver(btLostReceiver, new IntentFilter("bt_status_changed"));
        // Find the ImageView by ID
        ImageView bluetoothImageView = findViewById(R.id.bluetoothIcon);

        // Set an OnClickListener
        bluetoothImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Create an Intent to start the new Activity (new page)
                Intent bluetoothIntent = new Intent(MainActivity.this, DeviceList.class);
                startActivity(bluetoothIntent); // This will start the new Activity
            }
        });



        // -------------------------------TAB VIEW ------------------------------------------------
        TabLayout tabLayout = findViewById(R.id.tabLayout);
        ViewPager2 viewPager = findViewById(R.id.viewPager);

        TabAdapter adapter = new TabAdapter(this);
        viewPager.setAdapter(adapter);

        // This is where you can add more tabs.
        tabLayout.addTab(tabLayout.newTab().setText("Arena"));
        tabLayout.addTab(tabLayout.newTab().setText("Controller"));
        tabLayout.addTab(tabLayout.newTab().setText("Chat"));


        // Link TabLayout and ViewPager2
        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                viewPager.setCurrentItem(tab.getPosition());
            }

            // Must implement interface methods
            @Override
            public void onTabUnselected(TabLayout.Tab tab) {
            }

            @Override
            public void onTabReselected(TabLayout.Tab tab) {
            }
        });

        viewPager.registerOnPageChangeCallback(new ViewPager2.OnPageChangeCallback() {
            @Override
            public void onPageSelected(int position) {
                tabLayout.selectTab(tabLayout.getTabAt(position));
            }
        });
    }

    public void clearArena(View view) {
        TextView robotStatus = findViewById(R.id.robotStatusText);
        robotStatus.setText(R.string.idle);
        arena.clearArena();
    }

    // -------------------------------- OBSTACLE EDITING -------------------------------------------
    private void showObstacleDialog() {
        int obsIndex = arena.obstacles.indexOf(arena.editingObs);
        int obsX = arena.editingObs.getCol();
        int obsY = arena.editingObs.getRow();
        String imageDir = arena.editingObs.getImageDirection().toString();
        String imageID;
        if (arena.editingObs.getImageID() == -1) {
            imageID = Integer.toString(obsIndex + 1);
        } else {
            imageID = Integer.toString(arena.editingObs.getImageID());
        }

        ObstacleDialogueFragment obstacleDialogueFragment = ObstacleDialogueFragment.newInstance(obsIndex,imageID,imageDir,obsX,obsY,btService);
        obstacleDialogueFragment.show(getFragmentManager(), "hello");
        obstacleDialogueFragment.setCancelable(false);
    }

    public void setObstacleEdit(boolean obsEdit) {
        arena.obstacleEdit = obsEdit;
    }

    @Override
    public void dialogData(int obsIndex, Obstacle.ImageDirection direction, int x, int y) {
        Cell curCell;
        Cell oldCell = arena.obstacles.get(obsIndex);

        for (Map.Entry<Cell, RectF> entry : arena.gridMap.entrySet()) {
            curCell = entry.getKey();

            if (curCell.getCol() == x && curCell.getRow() == y && curCell.getType().equals(Cell.CellType.EMPTY)) {
                curCell.setType(Cell.CellType.OBSTACLE);
                arena.cells[arena.obstacles.get(obsIndex).getCol()][arena.obstacles.get(obsIndex).getRow()].setType(Cell.CellType.EMPTY);
                arena.obstacles.get(obsIndex).setImageDirection(direction);
                arena.obstacles.get(obsIndex).setCol(curCell.getCol());
                arena.obstacles.get(obsIndex).setRow(curCell.getRow());
                Log.d("obstacleyc", Integer.toString(oldCell.getCol()) + " , " + Integer.toString(oldCell.getRow()) + "set to " + arena.cells[oldCell.getCol()][oldCell.getRow()].getType());
//                oldCell.setType(Cell.CellType.EMPTY);
            } else if (curCell.getCol() == x && curCell.getRow() == y && !curCell.getType().equals(Cell.CellType.EMPTY)) {
                arena.obstacles.get(obsIndex).setImageDirection(direction);
                if (!(curCell.getCol() == oldCell.getCol() && curCell.getRow() == oldCell.getRow())) {
                    Toast toast = Toast.makeText(getApplicationContext(),
                            "Grid is already occupied",
                            Toast.LENGTH_SHORT);
                    toast.show();
                }
            }
        }
        arena.invalidate();
    }

    // -----------------------------------MANUAL CONTROLLER-------------------------------------
    // Method to handle button clicks for robot movement
    public void moveRobotManually(View view) {
        Button pressedBtn = (Button) view;
        //String dir;
        int id = pressedBtn.getId();
        if (Robot.robotMatrix[1][1] == null) { // To check if robot is set up
            System.out.println("Robot is not set up on map");
            return;
        }

        if (Robot.robotDir == null) {
            Robot.robotDir = "N"; // set default North
        }

        if (arena != null || arena.obstacles != null) {
            Cell oldPositionCell = Robot.robotMatrix[1][1];
            if (id == R.id.moveForwardButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "F"); // Forward
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell){
                    btService.write("f", false);
                }
            } else if (id == R.id.moveForwardRightButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "R"); // Right
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell) {
                    btService.write("fr", false);
                }

            } else if (id == R.id.moveForwardLeftButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "L"); //Left
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell) {
                    btService.write("fl", false);
                }

            } else if (id == R.id.moveBackwardButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "B"); // Backward
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell) {
                    btService.write("b", false);
                }

            } else if (id == R.id.moveBackwardRightButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "BR"); // Backward Right
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell) {
                    btService.write("br", false);
                }

            } else if (id == R.id.moveBackwardLeftButton) {
                Robot.robotDir = arena.moveRobot(Robot.robotDir, "BL"); // Backward Left
                Cell newPositionCell = Robot.robotMatrix[1][1];
                if(oldPositionCell != newPositionCell) {
                    btService.write("bl", false);
                }
            }
            else {
                return;
            }
        }
        if(Robot.robotMatrix[1][1] == null){
            System.out.println("Robot is not set up on map");
        }else{
//            btService.write(String.format("MOVE/%s", Robot.robotDir), DEBUG);
            if(robotDir != null){ //just to catch error
                robotDir = arena.moveRobot(robotDir,Robot.robotDir);
            }
        }
    }
    // --------------------------------- BLUETOOTH --------------------------------

    // Create a BroadcastReceiver for message_received.
    private final BroadcastReceiver msgReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String fullMessage = intent.getExtras().getString("message");
            if (DEBUG) {
                displayMessage("Debug Mode\n" + fullMessage);
                System.out.println("Debug Mode\n" + fullMessage);
//                return;
            }
            if (fullMessage.length() == 0) return;
            //Categorize received messages
            if (fullMessage.charAt(0) == '&') fullMessage = fullMessage.substring(1);
            String[] commandArr = fullMessage.split("&");
            for (String message : commandArr) {
                try {
                    String[] messageArr = message.split("\\|"); // remove header
//                    if (messageArr.length > 1) messageArr = messageArr[1].split(DELIMITER);
//                    else messageArr = messageArr[0].split(DELIMITER); //just takes away |
                    for (String messageElement: messageArr){
                        String[] messageA = messageElement.split(DELIMITER);
                        switch (messageA[0]) {
                            // Format: TOWARDS/<obstacle number>
                            case ("TOWARDS"): {
                                TextView robotStatus = findViewById(R.id.robotStatusText);
                                String movingMessage = getString(R.string.moving_towards, messageA[1]);
                                robotStatus.setText(movingMessage);
                                break;
                            }
                            case ("PATH"): {
                                // Split the string into lines
                                String[] lines = messageA[1].split("\n");

                                pathCoordinates.clear();
                                // Iterate over each line
                                for (String line : lines) {
                                    // Split each line into elements based on spaces
                                    String[] parts = line.split("\\s+"); // Split the line by any whitespace

                                    if (parts.length >= 3) {
                                        double y = Double.parseDouble(parts[0]);
                                        double x = Double.parseDouble(parts[1]);
                                        double theta = Double.parseDouble(parts[2]);
                                        pathCoordinates.add(new double[]{y, x, theta});
                                    }
                                }
                                Log.d("DEBUGYC", String.valueOf(pathCoordinates.size()));
                                pathTask(arena, pathCoordinates);
                                break;
                            }
                            // Format: TARGET/<obstacle number>/<target id>
                            case ("TARGET"): {
                                if (Integer.parseInt(messageA[2]) < 0 || Integer.parseInt(messageA[2]) > 45) {
                                    valid_image = false;
                                    valid_target = arena.setObstacleImageID(Integer.valueOf(messageA[1]), -1);
                                } else {
                                    valid_image = true;
                                    valid_target = arena.setObstacleImageID(Integer.valueOf(messageA[1]), Integer.valueOf(messageA[2]));
                                    TextView robotStatus = findViewById(R.id.robotStatusText);
                                    String obstacleMessage = getString(R.string.robot_status_message, messageA[1], messageA[2]);
                                    robotStatus.setText(obstacleMessage);
                                }
                                if (!valid_target || !valid_image) {
                                    displayMessage("Invalid imageID or obstacleID: " + message);
                                }
                                break;
                            }
                            // Format: STATUS/<msg>
                            // E.g. STATUS/READY --> when path by algo is complete and task is ready to begin.
                            case ("STATUS"): {
                                displayMessage(messageA[1]);
                                if(messageA[1].contains("READY")){
                                    TextView robotStatus = findViewById(R.id.robotStatusText);
                                    robotStatus.setText(R.string.task_1_ready);
                                    break;
                                } else if(messageA[1].contains("RECOGNIZING")){
                                    TextView robotStatus = findViewById(R.id.robotStatusText);
                                    robotStatus.setText(R.string.recognizing);
                                    break;
                                }

                            }
                            // Format: DEBUG/<msg>
                            case ("DEBUG"): {
                                if (DEBUG) displayMessage("DEBUG\n" + messageA[1]);
                                break;
                            }
                            // Format: FINISH
                            case ("FINISH"): {
                                if (((Button) findViewById(R.id.startTask1)).getText().toString().equals(getString(R.string.running))) {
                                    startStopTimer(findViewById(R.id.startTask1));
                                    TextView posTV = findViewById(R.id.robotStatusText);
//                                TextView statTV = findViewById(R.id.obstacleStatusText);
                                    if (posTV != null) posTV.setText(R.string.task_1_completed);
//                                if (statTV != null) statTV.setText(R.string.idle);
                                    String timeTaken = ((TextView) findViewById(R.id.timeElapsedText)).getText().toString();
                                    displayMessage("Task 1 complete!\nTime taken: " + timeTaken);
                                } else if (((Button) findViewById(R.id.startTask2)).getText().toString().equals(getString(R.string.running))) {
                                    startStopTimer(findViewById(R.id.startTask2));
                                    TextView posTV = findViewById(R.id.robotStatusText);
                                    if (posTV != null) posTV.setText(R.string.task_2_completed);
                                    String timeTaken = ((TextView) findViewById(R.id.timeElapsedText)).getText().toString();
                                    displayMessage("Task 2 complete!\nTime taken: " + timeTaken);
                                } else {
                                    displayMessage("Task is not running: " + messageA[1]);
                                }
                                break;
                            }

                            default: {
                                displayMessage("Unrecognized Command\n" + message);
                                break;
                            }
                        }
                    }

                } catch (Exception e) {
                    // message incorrect message parameters
                    displayMessage("ERROR (" + e.getMessage() + ")\n" + fullMessage);
                }
            }
        }
    };

    // Displays a string in the log TextView, prepends time received as well
    private void displayMessage(String msg) {
        Calendar c = Calendar.getInstance();
        msg = "\n\n"
                + c.get(Calendar.HOUR_OF_DAY) + ":"
                + c.get(Calendar.MINUTE) + ":"
                + c.get(Calendar.SECOND) + " - "
                + msg;
        // Append the message directly to the TextView
        TextView btMessageTextView = findViewById(R.id.btMessageTextView);
        btMessageTextView.append(msg);
        ScrollView scrollView = findViewById(R.id.scrollView);
        scrollView.getViewTreeObserver().addOnGlobalLayoutListener(() -> {
            scrollView.post(() -> scrollView.fullScroll(View.FOCUS_DOWN));
        });
    }

    private class TimerRunnable implements Runnable {
        private final TextView timerTextView;
        private long startTime = 0;

        public TimerRunnable(TextView timerTextView) {
            this.timerTextView = timerTextView;
        }

        @Override
        public void run() {
            long millis = System.currentTimeMillis() - startTime;
            int seconds = (int) (millis / 1000);
            int minutes = seconds / 60;
            seconds = seconds % 60;

            timerTextView.setText(String.format(Locale.getDefault(), "%02d:%02d", minutes, seconds));

            timerHandler.postDelayed(this, 500);
        }
    }

    public void startStopTimer(View view) {
        try {
            Button b = (Button) view;
            if (timerRunnable != null) { // timer was running, reset the timer and send stop command
                if (b.getId() == R.id.startTask1) {
                    b.setText(R.string.start_task1);
                } else {
                    b.setText(R.string.start_task2);
                }
                timerHandler.removeCallbacks(timerRunnable);
                timerRunnable = null;
                toggleActivateButtons(true);
//                btService.write("STOP", DEBUG);
                TextView rbTV = findViewById(R.id.robotStatusText);
                rbTV.setText(R.string.idle);
            } else {
                    timerRunnable = new TimerRunnable(findViewById(R.id.timeElapsedText));
                    btService.write("START/PATH", DEBUG);
                    b.setText(R.string.running);
                    TextView rbTV = findViewById(R.id.robotStatusText);
                    if(b.getId() == R.id.startTask1)
                    {
                        rbTV.setText(R.string.task_1_start);
                    } else {
                        rbTV.setText(R.string.task_2_start);
                    }
                    timerRunnable.startTime = System.currentTimeMillis();
                    timerHandler.postDelayed(timerRunnable, 0);
                    toggleActivateButtons(false);
            }
            } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    private void toggleActivateButtons(boolean val) {
        // deactivate obstacle and robot setting when robot is moving
        try {
            if (appDataModel.getIsSetObstacles().getValue()) {
                findViewById(R.id.setObstacleButton).callOnClick();
            }
            if (appDataModel.getIsSetRobot().getValue()) {
                findViewById(R.id.setRobotButton).callOnClick();
            }
            findViewById(R.id.setObstacleButton).setEnabled(val);
            findViewById(R.id.setRobotButton).setEnabled(val);
            findViewById(R.id.setClearArenaButton).setEnabled(val);
            // disable tabs
            TabLayout tabLayout = findViewById(R.id.tabLayout);
            LinearLayout tabStrip = ((LinearLayout) tabLayout.getChildAt(0));
            tabStrip.setEnabled(val);
            for (int i = 0; i < tabStrip.getChildCount(); i++) {
                tabStrip.getChildAt(i).setClickable(val);
            }
            if (RUN_TO_END) {
                findViewById(R.id.startTask1).setEnabled(val);
                findViewById(R.id.startTask2).setEnabled(val);
            }
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }


    // Create a BroadcastReceiver for bt_status_changed.
    public class BtStatusChangedReceiver extends BroadcastReceiver {
        Activity main;

        public BtStatusChangedReceiver(Activity main) {
            super();
            this.main = main;
        }

        @Override
        public void onReceive(Context context, Intent intent) {
            if (!(context instanceof MainActivity)) {
                return;
            }

            MainActivity mainActivity = (MainActivity) context;
            String message = "";
            if (BluetoothService.getBtStatus() == BluetoothService.BluetoothStatus.CONNECTING) {
                btService.serverStopListen();
                btService.clientConnect(intent.getStringExtra("address"),
                        intent.getStringExtra("name"),
                        mainActivity);
            } else if (BluetoothService.getBtStatus() == BluetoothService.BluetoothStatus.CONNECTED) {
                btService.startConnectedThread();
                btService.serverStopListen();
                message = "Status update\nConnected";
            } else if (BluetoothService.getBtStatus() == BluetoothService.BluetoothStatus.UNCONNECTED) {
                btService.disconnect();
//                btService.serverStartListen(mainActivity);
                return;
            } else if (BluetoothService.getBtStatus() == BluetoothService.BluetoothStatus.DISCONNECTED) {
                if (BluetoothService.CONNECT_AS_CLIENT) {
                    message = "Status update\nDisconnected, attempting to reconnect...";
                } else {
                    message = "Status update\nDisconnected, waiting for reconnect...";
                }
            } else {
                return;
            }
                mainActivity.displayMessage(message);
        }
    }

    public void onClickChat(View view) {
        String sendText = null;
        EditText chatET = findViewById(R.id.sendEditText);

        if (chatET != null) {
            sendText = chatET.getText().toString();
            System.out.println("Send Text = " + sendText);
            chatET.setText("");
        }
        displayMessage("Status update\n" + sendText);
        btService.write(String.format("%s", sendText), DEBUG);

        // Collapse Keyboard on click
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        imm.hideSoftInputFromWindow(getCurrentFocus().getWindowToken(), 0);
    }


    public void clearLogsBtn(View view) {
        TextView logs = ((TextView) findViewById(R.id.receiveText));
        logs.setText(null);
    }

    // -----------------------------------ALGO PATH SIMULATOR--------------------------------------

    // obstacles are all placed
    // setSendArenaButton button is pressed -- obstacle info is printed in logcat
    public void printObstacles(View view) {
        Button pressedBtn = (Button) view;
        int id = pressedBtn.getId();

        if (id == R.id.setSendArenaButton) {

            // Create the target list string
            StringBuilder targetListBuilder = new StringBuilder("targetlst = [");
            ArrayList<String> rpiObstacleList = new ArrayList<>();

            for (int i = 0; i < arena.obstacles.size(); i++) {
                Obstacle obstacle = arena.obstacles.get(i);

                // Convert obstacle direction to the required string format
                String dir = "";
                switch (obstacle.getImageDirection()) {
                    case NORTH:
                        dir = "N";
                        break;
                    case EAST:
                        dir = "E";
                        break;
                    case SOUTH:
                        dir = "S";
                        break;
                    case WEST:
                        dir = "W";
                        break;
                }

                // Get the y, x coordinates and add 0.5 to each
                double yCoord = obstacle.getRow() + 0.5;
                double xCoord = obstacle.getCol() + 0.5;

                // Append the obstacle info in the required format
                targetListBuilder.append(String.format("Target(%.1f, %.1f, \"%s\")", yCoord, xCoord, dir));
                rpiObstacleList.add(String.format("[%.1f, %.1f, \"%s\", %d]", yCoord, xCoord, dir, obstacle.getObstacleID()));

                // Add a comma between targets, except after the last one
                if (i < arena.obstacles.size() - 1) {
                    targetListBuilder.append(", ");
                }
            }

            targetListBuilder.append("]");

            // Print the target list string to the log
            Log.d("MainActivity", targetListBuilder.toString());
            btService.write(rpiObstacleList.toString(), false);
            TextView robotStatus = findViewById(R.id.robotStatusText);
            robotStatus.setText(getString(R.string.calc_path));
        }
    }

    public void startTask1(View view){
        Button pressedBtn = (Button) view;
        if (pressedBtn.getText() != getString(R.string.running)) {
            startStopTimer(findViewById(R.id.startTask1));
        }
        else{
            startStopTimer(findViewById(R.id.startTask1));
        }
    }

    public void startTask2(View view){
        Button pressedBtn = (Button) view;
        if (pressedBtn.getText() != getString(R.string.running)) {
            startStopTimer(findViewById(R.id.startTask2));
        }
        else{
            startStopTimer(findViewById(R.id.startTask2));
        }
    }

    public void pathTask(View view, ArrayList<double[]> pathCoordinates) {
        // Run the path in a background thread
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (double[] coords : pathCoordinates) {
                    double y = (double)Math.round(coords[0] * 100000d) / 100000d;
                    double x = (double)Math.round(coords[1] * 100000d) / 100000d;
                    double theta = coords[2];

                    // Run on UI thread to update the robot position
                    view.post(new Runnable() {
                        @Override
                        public void run() {
                            if (!moveRobotTo(y, x, theta)) {
                                System.out.println("Movement stopped due to out of bounds at (" + y + ", " + x + ")");
                            }
                        }
                    });

                    try {
                        // Sleep for 100 milliseconds between each movement to show robot progression
                        Thread.sleep(50);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }).start();
    }

//    //startPathCalc button is pressed -- obstacles will be displayed and robot also moves on grid
//    public void startSimulation(View view) {
//        Button pressedBtn = (Button) view;
//        int id = pressedBtn.getId();
//
//        if (id == R.id.startPathCalc) {
//            //obstacles loaded from res/raw/obstacles.txt
//            ArrayList<Obstacle> obstacleList = loadObstacles();
//
//            valid_pos = arena.setRobot(1, 1, "N");
//
//            //set the loaded obstacles on the grid
//            if (obstacleList != null && !obstacleList.isEmpty()) {
//                arena.obstacles.clear();  // Clear any existing obstacles
//                arena.obstacles.addAll(obstacleList);  // Add the new obstacles to the arena
//                arena.invalidate();
//            }
//
//            //call the pathSimulator function to simulate the robot's movement
//            pathSimulator(view);
//        }
//    }

    //reads the obstacle info from obstacle.txt in res/raw when
    public ArrayList<Obstacle> loadObstacles() {
        ArrayList<Obstacle> obstacles = new ArrayList<>();
        int obstacleID = 1;  // Start obstacle ID from 1

        try {
            // Open the obstacles.txt file from the res/raw directory
            InputStream inputStream = getResources().openRawResource(R.raw.obstacles); // R.raw.obstacles refers to res/raw/obstacles.txt
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
            String line;

            // Read each line from the file
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("\\s+"); // Split the line by whitespace

                if (parts.length == 3) {
                    // Parse the coordinates and direction from the file
                    int yCoord = Integer.parseInt(parts[0]);
                    int xCoord = Integer.parseInt(parts[1]);
                    String direction = parts[2];

                    // Create a new obstacle
                    Obstacle obstacle = new Obstacle(xCoord, yCoord, obstacleID);

                    // Set the direction for the obstacle
                    obstacle.setImageDirection(Obstacle.ImageDirection.valueOf(direction.toUpperCase(Locale.US)));

                    // Add the obstacle to the list
                    obstacles.add(obstacle);

                    // Increment the obstacle ID for the next obstacle
                    obstacleID++;
                }
            }
            reader.close(); // Close the reader after use

        } catch (Exception e) {
            e.printStackTrace();
        }

        return obstacles;
    }

    //reads the path info from path.txt in res/raw
    public ArrayList<double[]> loadPathCoordinates(Context context) {
        ArrayList<double[]> pathCoordinates = new ArrayList<>();

        try {
            // Open the text file from the res/raw directory
            InputStream inputStream = context.getResources().openRawResource(R.raw.path); // R.raw.path refers to res/raw/path.txt
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
            String line;

            // Read each line from the file
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("\\s+"); // Split the line by any whitespace

                if (parts.length >= 3) {
                    double y = Double.parseDouble(parts[0]);
                    double x = Double.parseDouble(parts[1]);
                    double theta = Double.parseDouble(parts[2]);
                    pathCoordinates.add(new double[]{y, x, theta});
                }
            }

            reader.close(); // Close the reader after use

        } catch (Exception e) {
            e.printStackTrace();
        }

        return pathCoordinates;
    }

    //simulates robot when setSendArenaButton button is pressed based on the coordinated retrieved by loadPathCoordinates using moveRobotTo
    public void pathSimulator(View view) {
            // Load the path coordinates from the external file
            ArrayList<double[]> pathCoordinates = loadPathCoordinates(this);

            // Run the path simulation in a background thread
            new Thread(new Runnable() {
                @Override
                public void run() {
                    for (double[] coords : pathCoordinates) {
                        double y = (double)Math.round(coords[0] * 100000d) / 100000d;
                        double x = (double)Math.round(coords[1] * 100000d) / 100000d;
                        double theta = coords[2];

                        // Run on UI thread to update the robot position
                        view.post(new Runnable() {
                            @Override
                            public void run() {
                                if (!moveRobotTo(y, x, theta)) {
                                    System.out.println("Movement stopped due to out of bounds at (" + y + ", " + x + ")");
                                }
                            }
                        });

                        try {
                            // Sleep for 100 milliseconds between each movement to show robot progression
                            Thread.sleep(100);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }).start();
    }

    //function to display the robot movement on the grid
    private boolean moveRobotTo(double y, double x, double theta) {
        int gridX = (int) Math.floor(x);
        int gridY = (int) Math.floor(y);

        if (!Robot.isWithinBounds(gridX, gridY)) {
            return false;
        }

        Robot.simulatorRobot(gridX,gridY, radiansToDirection(theta));
        arena.invalidate();
        return true;
    }

    //converts radians from algo to directions (N,S,E,W)
    public static String radiansToDirection(double theta) {
        // normalize theta to be within -pi to pi
       /* theta = theta % (2 * Math.PI);  // Normalize to [0, 2π)
        if (theta < -Math.PI) {
            theta += 2 * Math.PI;  // Adjust if less than -π
        } else if (theta > Math.PI) {
            theta -= 2 * Math.PI;  // Adjust if greater than π
        }*/

        // radians to direction
        if (theta > Math.PI / 4 && theta <= 3 * Math.PI / 4) {
            return "N";  // North from π/4 to 3π/4
        } else if (theta > -Math.PI / 4 && theta <= Math.PI / 4) {
            return "E";  // East from -π/4 to π/4
        } else if (theta > -3 * Math.PI / 4 && theta <= -Math.PI / 4) {
            return "S";  // South from -3π/4 to -π/4
        } else if (theta > 3 * Math.PI / 4 || theta <= -3 * Math.PI / 4) {
            return "W";  // West from 3π/4 to π and -π to -3π/4
        } else {
            return "Exception";
        }

    }

}