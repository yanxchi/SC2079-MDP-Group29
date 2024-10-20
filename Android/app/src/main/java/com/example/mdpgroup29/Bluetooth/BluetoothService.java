package com.example.mdpgroup29.Bluetooth;
import android.Manifest;
import android.app.Activity;
import android.app.Dialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.LocationManager;
import android.os.Debug;
import android.os.ParcelUuid;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.mdpgroup29.Arena.Cell;
import com.example.mdpgroup29.Arena.Obstacle;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class  BluetoothService {
    public static BluetoothAdapter mBluetoothAdapter;
    public static BluetoothSocket mBluetoothSocket;
    public static BluetoothDevice mConnectedDevice;
    public static boolean CONNECT_AS_CLIENT = true; // if false, will make device discoverable and accept connections
    public static Cell[][] cells;
    public static ArrayList<Obstacle> obstacles = null;
    public enum BluetoothStatus {
        UNCONNECTED, SCANNING, CONNECTING, CONNECTED, DISCONNECTED
    }

    private static BluetoothStatus btStatus;
    private static  final String[] permissions = {
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.ACCESS_COARSE_LOCATION
    };
    private static final UUID BT_MODULE_UUID = ParcelUuid.fromString("00001101-0000-1000-8000-00805F9B34FB").getUuid(); // "random" unique identifier (https://novelbits.io/uuid-for-custom-services-and-characteristics/#:~:text=%E2%80%9CA%20UUID%20is%20a%20universally,by%20their%2016%2Dbit%20aliases.)
    private static final int MAX_RECONNECT_RETRIES = 5;
    private static final String NAME = "MDP_Group_29_Tablet";
    public static ConnectedThread mConnectedThread;
    public AcceptThread mAcceptThread;
    public ConnectAsClientThread mClientThread;
    public Activity mContext;



    // sends bt_status_changed broadcast when status is set
    public static void setBtStatus(BluetoothStatus newStatus, Map<String, String> extras, Activity context) {
        btStatus = newStatus;
        Intent intent = new Intent("bt_status_changed");
        for (String key: extras.keySet()){
            intent.putExtra(key, extras.get(key));
        }
        System.out.println("BtStatus changed to "+newStatus.toString());
        context.sendBroadcast(intent);
    }

    public static BluetoothStatus getBtStatus(){
        return btStatus;
    }

    private static boolean hasPermissions(Activity activity) {
        if (permissions != null) {
            for (String permission : permissions) {
                if (ActivityCompat.checkSelfPermission(activity, permission) != PackageManager.PERMISSION_GRANTED) {
                    return false;
                }
            }
        }
        return true;
    }

    public static void stopSearch() { mBluetoothAdapter.cancelDiscovery(); }

    public static void startSearch() {
        mBluetoothAdapter.startDiscovery();
    }

    public static void initialize(Activity activity){
        if (btStatus == null) setBtStatus(BluetoothStatus.UNCONNECTED, new HashMap<String, String>(), activity);
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // Request permissions
        if (!hasPermissions(activity)) {
            ActivityCompat.requestPermissions(activity, permissions, 1);
        }

        // Request to turn on bluetooth
        if(!mBluetoothAdapter.isEnabled())
        {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            activity.startActivity(enableBtIntent);
        }

        // Request to turn on location
        LocationManager lm = (LocationManager) activity.getSystemService(Context.LOCATION_SERVICE);
        if (!lm.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                !lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
            // Build the alert dialog
            AlertDialog.Builder builder = new AlertDialog.Builder(activity);
            builder.setTitle("Location Services Not Active");
            builder.setMessage("Please enable Location Services and GPS");
            builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialogInterface, int i) {
                    // Show location settings when the user acknowledges the alert dialog
                    Intent enableLocIntent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                    activity.startActivity(enableLocIntent);
                }
            });
            Dialog alertDialog = builder.create();
            alertDialog.setCanceledOnTouchOutside(false);
            alertDialog.show();
        }
    }

    // Setting mContext to the current activity.
    public BluetoothService(Activity context){
        mContext = context;
    }

    // Used after Bluetooth connection has already been establish to handle data transfer
    // and run communication process
    public void startConnectedThread() {
        // mBluetoothSocket represents established connection between 2 bluetooth device.
        mConnectedThread = new ConnectedThread(mBluetoothSocket);
        mConnectedThread.start();
    }

    public boolean write(String message, boolean DEBUG){
        if (mConnectedThread == null){
            Toast.makeText(mContext, "Bluetooth not connected!", Toast.LENGTH_SHORT).show();
            return false;
        }
        // comment out the \n below only when performing checklist
//        message = message + "\n";
//        if (DEBUG) {
//            try {
//                mConnectedThread.write(message.getBytes("US-ASCII"));
//            } catch (UnsupportedEncodingException e) {
//                mConnectedThread.write(message.getBytes());
//            }
//
//        } else {
        mConnectedThread.write(message.getBytes());
//        }
        return true;
    }

    public void disconnect() {
        if (mConnectedThread != null) mConnectedThread.cancel();
        mConnectedDevice = null;
    }

    // Initiates connection to a remote Bluetooth device.
    // Used to discover remote device and establish socket connection
    public void clientConnect(String address, String name, Activity context) {
        mClientThread = new ConnectAsClientThread(address, name, context);
        mClientThread.start();
        Log.d("bluetoothyc", "trying to connect to: " +name);
        // when you call .start() it will create new thread of execution and
        // invoke run() on the new thread.
    }


    public void serverStartListen(Activity context) {
        if (CONNECT_AS_CLIENT) return; // COMMENT OUT WHEN USING AMD TOOL
        if(mBluetoothAdapter.getScanMode() != BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE)
        {
            // Make device discoverable
            Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
            discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 30);
            context.startActivityForResult(discoverableIntent, 1);
        }
        // If no thread currently running to accept incoming connection, create a new thread.
        if (mAcceptThread == null){
            mAcceptThread = new AcceptThread(context);
            mAcceptThread.start();
        }
    }

    public void serverStopListen() {
        if (mAcceptThread != null) {
            mAcceptThread.cancel();
            mAcceptThread = null;
        }
    }

    private static BluetoothSocket createBluetoothSocket(BluetoothDevice device) throws IOException {
        try {
            return device.createInsecureRfcommSocketToServiceRecord(BT_MODULE_UUID);
        } catch (Exception e) {
            System.out.println("Could not create connection");
        }
        return  device.createRfcommSocketToServiceRecord(BT_MODULE_UUID);
    }
//    // Trying to create Bluetooth socket
//    private static BluetoothSocket createBluetoothSocket(BluetoothDevice device) throws IOException {
//        BluetoothSocket socket = null;
//        try {
//            // Try using the insecure RFComm socket method first
//            socket = (BluetoothSocket) device.getClass().getMethod("createRfcommSocket", int.class).invoke(device, 1);
//        } catch (Exception e) {
//            Log.d("bluetoothyc", "Insecure socket creation failed: " + e.getMessage());
//        }
//
//        // If the insecure RFComm socket creation fails, use reflection to try the fallback method
//        if (socket == null) {
//            try {
//                // Use reflection to create a socket with the fallback port number
//                socket = (BluetoothSocket) device.getClass().getMethod("createRfcommSocket", int.class).invoke(device, 1);
//            } catch (Exception e) {
//                Log.d("bluetoothyc", "Fallback socket creation failed: " + e.getMessage());
//                throw new IOException("Could not create Bluetooth socket", e);
//            }
//        }
//
//        return socket;
//    }

    private static class ConnectAsClientThread extends Thread {
        public Activity context;
        public String name, address;

        public ConnectAsClientThread(String address, String name, Activity context) {
            this.context = context;
            this.address = address;
            this.name = name;
        }

        @Override
        public void run() {
            System.out.println("starts");
            boolean fail = false;
            BluetoothService.stopSearch();
            BluetoothDevice device = BluetoothService.mBluetoothAdapter.getRemoteDevice(address);

            try {
                BluetoothService.mBluetoothSocket = createBluetoothSocket(device);
                Log.d("bluetoothyc", "SOCKET CREATED");

                // Check if the socket is valid
                if (BluetoothService.mBluetoothSocket == null) {
                    Log.d("bluetoothyc", "socket creation failed after creation");
                }


            } catch (IOException e) {
                fail = true;
                Intent intent = new Intent("message_received");
                intent.putExtra("message", "DEBUG/Socket creation failed");
                context.sendBroadcast(intent);
            }
            // Establish the Bluetooth socket connection.
            try {
                // Initiate connection process between local device and remote device using the socket.
                // Check if the socket is valid
                if (BluetoothService.mBluetoothSocket == null) {
                    Log.d("bluetoothyc", "socket failed before connection");
                }else{
                    Log.d("bluetoothyc", BluetoothService.mBluetoothSocket.toString());
                }
                BluetoothService.mBluetoothSocket.connect();
                Log.d("bluetoothyc", "CONNECTION SUCCESSFUL");
                BluetoothService.mConnectedDevice = device;
            } catch (IOException e) {
                try {
                    fail = true;
                    System.out.println(e.getMessage());
                    Log.d("bluetoothyc", "connection failed " + e.getMessage());
                    BluetoothService.mBluetoothSocket.close();
                } catch (IOException e2) {
                    Intent intent = new Intent("message_received");
                    intent.putExtra("message", "DEBUG/Socket creation failed");
                    context.sendBroadcast(intent);
                }
            }
            System.out.println("ends");
            if(!fail) {
                Intent intent = new Intent("message_received");
                intent.putExtra("message", "DEBUG/Connected!");
                context.sendBroadcast(intent);
                Map<String, String> extra = new HashMap<>();
                extra.put("device", !name.equals("null") ? name : address);
                BluetoothService.setBtStatus(BluetoothService.BluetoothStatus.CONNECTED, extra, context);
            } else {
                Intent intent = new Intent("message_received");
                intent.putExtra("message", "DEBUG/Connection Failed");
                context.sendBroadcast(intent);
                Map<String, String> extra = new HashMap<>();
                BluetoothService.setBtStatus(BluetoothStatus.UNCONNECTED, extra, context);
            }
        }
    }

    private static class AcceptThread extends Thread {
        private final BluetoothServerSocket mmServerSocket;
        private final Activity context;

        public AcceptThread(Activity context) {
            this.context = context;
            BluetoothServerSocket tmp = null;
            try {
                tmp = mBluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(NAME, BT_MODULE_UUID);
            } catch (IOException e) {
                System.out.println("Socket's listen() method failed");
            }
            mmServerSocket = tmp;
        }

        public void run() {
            BluetoothSocket socket = null;
            // Keep listening until exception occurs or a socket is returned.
            while (true) {
                try {
                    socket = mmServerSocket.accept();
                } catch (IOException e) {
                    System.out.println("Socket's accept() method failed");
                    break;
                }

                if (socket != null) {
                    // A connection was accepted. Perform work associated with
                    // the connection in a separate thread.
                    mBluetoothSocket = socket;
                    mConnectedDevice = socket.getRemoteDevice();
                    String name = socket.getRemoteDevice().getName();
                    String address = socket.getRemoteDevice().getAddress();
                    Map<String, String> extra = new HashMap<>();
                    extra.put("device", !name.equals("null") ? name : address);
                    Intent intent = new Intent("message_received");
                    intent.putExtra("message", "DEBUG/Connected!");
                    context.sendBroadcast(intent);
                    BluetoothService.setBtStatus(BluetoothService.BluetoothStatus.CONNECTED, extra, context);
                    try {
                        mmServerSocket.close();
                    } catch (IOException e) {
                        System.out.println(e.getMessage());;
                    }
                    break;
                }
            }
        }

        // Closes the connect socket and causes the thread to finish.
        public void cancel() {
            try {
                mmServerSocket.close();
            } catch (IOException e) {
                System.out.println("Could not close the connect socket");
            }
        }
    }

    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;

        public ConnectedThread(BluetoothSocket socket) {
            mmSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            // Get the input and output streams; using temp objects because
            // member streams are final.
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                System.out.println("Error occurred when creating input stream " + e.getMessage());
            }
            try {
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                System.out.println("Error occurred when creating output stream " + e.getMessage());
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
        }

        public void run() {
            // mmBuffer store for the stream
            byte[] buffer = new byte[1024];
            int numBytes; // bytes returned from read()
            StringBuilder stringBuffer = new StringBuilder();

            // Keep listening to the InputStream until an exception occurs.
            while (true) {
                try {
                    // Read from the InputStream.
                    numBytes = mmInStream.read(buffer);
                    // Send the obtained bytes to the UI activity.
                    Intent intent = new Intent("message_received");
                    String received_message = new String(buffer, 0, numBytes);
                    stringBuffer.append(received_message);
                    int idx = stringBuffer.lastIndexOf("|");
                    if (idx != -1) {
                        intent.putExtra("message", stringBuffer.substring(0, idx));
                        mContext.sendBroadcast(intent);
                        stringBuffer.delete(0, idx + 1);
                    }
                } catch (IOException e) {
                    System.out.println("DEBUG/Input stream was disconnected " + e.getMessage());
                    setBtStatus(BluetoothStatus.DISCONNECTED, new HashMap<>(), mContext);
                    break;
                }
            }
        }

        // Call this from the main activity to send data to the remote device.
        public void write(byte[] bytes) {
            try {
                mmOutStream.write(bytes);
            } catch (IOException e) {
                System.out.println("Error occurred when sending data " + e.getMessage());

                // Send a failure message back to the activity.
                Intent intent = new Intent("message_received");
                intent.putExtra("message", "DEBUG/Couldn't send data to the other device");
                mContext.sendBroadcast(intent);
            }
        }

        // Call this method from the main activity to shut down the connection.
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                System.out.println("Could not close the connect socket " + e.getMessage());
            }
        }
    }

    // Receiver for DEVICE_DISCONNECTED, automatically tries to reconnect as client
    public class BluetoothLostReceiver extends BroadcastReceiver {

        Activity main;

        public BluetoothLostReceiver(Activity main) {
            super();
            this.main = main;
        }

        @Override
        public void onReceive(Context context, Intent intent) {
            if (getBtStatus() == BluetoothStatus.DISCONNECTED) {
                Intent intent2 = new Intent("message_received");
                if (CONNECT_AS_CLIENT){
                    intent2.putExtra("message", "DEBUG/Connection lost, attempting to reconnect...");
                    context.sendBroadcast(intent2);
                    if(getBtStatus() == BluetoothStatus.DISCONNECTED && mConnectedDevice != null) {
                        for (int i = 0; i < MAX_RECONNECT_RETRIES; i++) {
                            if (btStatus == BluetoothStatus.CONNECTED) return;
                            try {
                                clientConnect(mConnectedDevice.getAddress(), mConnectedDevice.getName(), main);
                            } catch (Exception e) {
                                System.out.println(e.getMessage());
                            }
                            try {
                                intent2 = new Intent("message_received");
                                intent2.putExtra("message", "DEBUG/Reconnect attempt " + i + " failed");
                                context.sendBroadcast(intent2);
                                Thread.sleep(2000);
                            } catch (InterruptedException e) {
                                System.out.println(e.getMessage());
                            }
                        }
                    }
                    // Max tries elapsed
                    intent2 = new Intent("message_received");
                    intent2.putExtra("message", "DEBUG/Reconnect failed");
                    context.sendBroadcast(intent2);
                    setBtStatus(BluetoothStatus.UNCONNECTED, new HashMap<>(), (Activity) context);
                }
                else {
                    // reconnect as server
                    intent2.putExtra("message", "DEBUG/Connection lost, making device discoverable...");
                    context.sendBroadcast(intent2);
                    serverStartListen(main);
                }
            }
        }
    }

}

