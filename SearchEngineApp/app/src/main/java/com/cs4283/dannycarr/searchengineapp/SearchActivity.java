package com.cs4283.dannycarr.searchengineapp;

import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

public class SearchActivity extends AppCompatActivity {

    // TAG for logging
    private static final String TAG = "SearchActivity";

    // server to connect to
    protected static final int GROUPCAST_PORT = 20000;
    protected static final String GROUPCAST_SERVER = "ec2-54-174-123-156.compute-1.amazonaws.com";

    Socket socket = null;
    BufferedReader in = null;
    PrintWriter out = null;

    Button search_button = null;
    EditText etSearch = null;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);

        search_button = (Button) this.findViewById(R.id.search_button);
        etSearch = (EditText) this.findViewById(R.id.etSearch);

        hideSearch();

        hideSearchAgain();

        search_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String entry = etSearch.getText().toString();

                if (entry.length() <= 2) {
                    Toast.makeText(getApplicationContext(), "Please enter a search term" +
                            " of 3 characters or more", Toast.LENGTH_SHORT).show();
                } else {
                    send(entry);
                }
            }
        });

        connect();

    }

    @Override
    protected void onDestroy() {
        Log.i(TAG, "onDestroy called");
        disconnect();
        super.onDestroy();
    }


    //***Networking***

    void connect() {

        new AsyncTask<Void, Void, String>() {

            String errorMsg = null;

            @Override
            protected String doInBackground(Void... args) {
                Log.i(TAG, "Connect task started");
                try {
                    connected = false;
                    socket = new Socket(GROUPCAST_SERVER, GROUPCAST_PORT);
                    Log.i(TAG, "Socket created");
                    in = new BufferedReader(new InputStreamReader(
                            socket.getInputStream()));
                    out = new PrintWriter(socket.getOutputStream());

                    connected = true;
                    Log.i(TAG, "Input and output streams ready");

                } catch (UnknownHostException e1) {
                    errorMsg = e1.getMessage();
                } catch (IOException e1) {
                    errorMsg = e1.getMessage();
                    try {
                        if (out != null) {
                            out.close();
                        }
                        if (socket != null) {
                            socket.close();
                        }
                    } catch (IOException ignored) {
                    }
                }
                Log.i(TAG, "Connect task finished");
                return errorMsg;
            }

            @Override
            protected void onPostExecute(String errorMsg) {
                if (errorMsg == null) {
                    Toast.makeText(getApplicationContext(),
                            "Connected to server", Toast.LENGTH_SHORT).show();

                    hideConnectingText();
                    showLoginControls();

                    // start receiving
                    receive();

                } else {
                    Toast.makeText(getApplicationContext(),
                            "Error: " + errorMsg, Toast.LENGTH_SHORT).show();
                    // can't connect: close the activity
                    finish();
                }
            }
        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
    }


    boolean send(String entry) {
        return true;
    }


    //***UI Methods***


    void hideSearchAgain() { findViewById(R.id.search_again).setVisibility(View.GONE);}

    void showSearchAgain() { findViewById(R.id.search_again).setVisibility(View.VISIBLE);}

    void hideSearch() { findViewById(R.id.search_bar).setVisibility(View.GONE);}

    void showSearch() { findViewById(R.id.search_bar).setVisibility(View.VISIBLE);}
}
