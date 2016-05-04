package com.cs4283.dannycarr.searchengine;

import android.app.ActionBar;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.nfc.Tag;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.view.ViewGroup;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

public class SearchActivity extends AppCompatActivity {

    // server to connect to
    protected static final int EC2_PORT = 20000;
    protected static final String EC2_SERVER = "ec2-54-174-123-156.compute-1.amazonaws.com";
    // TAG for logging
    private static final String TAG = "SearchActivity";
    //protected static final String EC2_SERVER = "10.0.3.2";
    Socket socket = null;
    BufferedReader in = null;
    PrintWriter out = null;
    boolean connected = false;

    LinearLayout resultLayout = null;
    Button search_button = null;
    Button search_again = null;
    EditText etSearch = null;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);

        resultLayout = (LinearLayout) this.findViewById(R.id.llResults);
        search_again = (Button) this.findViewById(R.id.search_again);
        search_button = (Button) this.findViewById(R.id.search_button);
        etSearch = (EditText) this.findViewById(R.id.etSearch);

        hideSearch();
        hideSearchAgain();
        hideWaiting();
        hideResults();

        search_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String entry = etSearch.getText().toString();

                if (entry.length() <= 2) {
                    Toast.makeText(getApplicationContext(), "Please enter a search term" +
                            " of 3 characters or more", Toast.LENGTH_SHORT).show();
                } else {
                    send(entry);

                    hideSearch();
                    showWaiting();

                    receive();
                }
            }
        });

        search_again.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resultLayout.removeAllViews();
                etSearch.setText("");

                hideSearchAgain();

                hideResults();
                showSearch();

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
                    socket = new Socket(EC2_SERVER, EC2_PORT);
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
                Log.i(TAG, "Connect task finished: " + (errorMsg == null ? "success" : errorMsg));
                return errorMsg;
            }

            @Override
            protected void onPostExecute(String errorMsg) {
                if (errorMsg == null) {
                    Toast.makeText(getApplicationContext(),
                            "Connected to server", Toast.LENGTH_SHORT).show();

                    hideConnectingText();
                    showSearch();

                } else {
                    Toast.makeText(getApplicationContext(),
                            "Error: " + errorMsg, Toast.LENGTH_LONG).show();
                    // can't connect: close the activity
                    finish();
                }
            }
        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void receive() {

        new AsyncTask<Void, Void, String>() {

            protected String doInBackground(Void... args) {
                Log.i(TAG, "Receive task started");
                try {
                    String msg = null;
                    while (connected) {
                        Log.i(TAG, "waiting for response");

                        msg = in.readLine();

                        if (msg == null) { // other side closed the
                            // connection
                            Log.i(TAG, "message was null");
                            break;
                        }
                        publishProgress(msg);
                    }

                } catch (UnknownHostException e1) {
                    Log.i(TAG, "UnknownHostException in receive task");
                } catch (IOException e1) {
                    Log.i(TAG, "IOException in receive task");
                } finally {
                    connected = false;
                    try {
                        if (out != null)
                            out.close();
                        if (socket != null)
                            socket.close();
                    } catch (IOException e) {
                    }
                }
                Log.i(TAG, "Receive task finished");
                return null;
            }

            protected void publishProgress(String... received) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        hideWaiting();
                        hideSearch();
                        showSearchAgain();
                        resultLayout = (LinearLayout) findViewById(R.id.llResults);
                        resultLayout.setVisibility(View.VISIBLE);
                    }
                });

                Log.i(TAG, "reached onPost");

                Log.i(TAG, received[0]);


                String[] results = received[0].split("\\|");

                int resCount = 0;
                for (String result : results) {
                    Log.i(TAG, result);

                    String[] commas = result.split(",");

                    System.out.println(result);
                    final String url = commas[1];
                    Button link = new Button(getApplicationContext());
                    link.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View v) {
                            Intent webLink = new Intent(Intent.ACTION_VIEW);
                            webLink.setData(Uri.parse(url));
                            startActivity(webLink);
                        }
                    });
                    link.setText(commas[0]);
                    link.setTextSize(12);
                    link.setLayoutParams(new ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.WRAP_CONTENT,
                            ViewGroup.LayoutParams.WRAP_CONTENT));

                    //this is so awful I'm sorry

                    final Button putButton = link;
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            resultLayout.addView(putButton);
                        }
                    });
                    resCount++;
                    if (resCount >= 9) break;
                }
                return;
            }
        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void disconnect() {
        new Thread() {
            @Override
            public void run() {
                if (connected) {
                    connected = false;
                }
                // make sure that we close the output, not the input
                if (out != null) {
                    out.print("BYE");
                    out.flush();
                    out.close();
                }
                // in some rare cases, out can be null, so we need to close the socket itself
                if (socket != null)
                    try {
                        socket.close();
                    } catch (IOException ignored) {
                    }

                Log.i(TAG, "Disconnect task finished");
            }
        }.start();
    }

    boolean send(String msg) {
        if (!connected) {
            Log.i(TAG, "can't send: not connected");
            return false;
        }

        new AsyncTask<String, Void, Boolean>() {

            @Override
            protected Boolean doInBackground(String... msg) {
                Log.i(TAG, "sending: " + msg[0]);
                out.println(msg[0]);
                return out.checkError();
            }

            @Override
            protected void onPostExecute(Boolean error) {
                if (!error) {
                    /*Toast.makeText(getApplicationContext(),
                            "Message sent to server", Toast.LENGTH_SHORT)
                            .show();*/
                } else {
                    Toast.makeText(getApplicationContext(),
                            "Error sending message to server",
                            Toast.LENGTH_SHORT).show();
                }
            }
        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR, msg);

        return true;
    }


    //***UI Methods***

    void hideConnectingText() {
        findViewById(R.id.tvConnecting).setVisibility(View.GONE);
    }

    void hideSearchAgain() {
        findViewById(R.id.search_again).setVisibility(View.GONE);
    }

    void showSearchAgain() {
        findViewById(R.id.search_again).setVisibility(View.VISIBLE);
    }

    void hideSearch() {
        findViewById(R.id.search_bar).setVisibility(View.GONE);
    }

    void showSearch() {
        findViewById(R.id.search_bar).setVisibility(View.VISIBLE);
    }

    void hideWaiting() {
        findViewById(R.id.waiting).setVisibility(View.GONE);
    }

    void showWaiting() {
        findViewById(R.id.waiting).setVisibility(View.VISIBLE);
    }

    void hideResults() {
        findViewById(R.id.llResults).setVisibility(View.GONE);
    }
}
