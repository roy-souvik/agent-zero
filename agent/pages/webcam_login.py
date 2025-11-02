import streamlit as st
import streamlit.components.v1 as components

def show():
    st.title("🎥 Webcam Login")
    st.markdown("Use facial recognition to log in")

    # Path to your Teachable Machine model served via FastAPI
    model_path = "http://localhost:8001/static/model/"

    st.info("📌 Click 'Start' to begin webcam authentication")

    # Embed the Teachable Machine code
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }}
            #webcam-container {{
                margin: 20px auto;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                display: inline-block;
                padding: 10px;
            }}
            #label-container {{
                margin: 20px auto;
                max-width: 400px;
            }}
            #label-container div {{
                background: #f0f0f0;
                padding: 10px;
                margin: 5px;
                border-radius: 5px;
                font-weight: bold;
            }}
            button {{
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 20px;
            }}
            button:hover {{
                background-color: #45a049;
            }}
            button:disabled {{
                background-color: #cccccc;
                cursor: not-allowed;
            }}
            .status {{
                padding: 10px;
                margin: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
            }}
            .error {{
                background-color: #f8d7da;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <div id="status"></div>
        <button type="button" onclick="init()" id="startBtn">🎥 Start Webcam</button>
        <button type="button" onclick="stopWebcam()" id="stopBtn" style="display:none;">⏹️ Stop</button>
        <div id="webcam-container"></div>
        <div id="label-container"></div>

        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
        <script type="text/javascript">
            const URL = "{model_path}";
            let model, webcam, labelContainer, maxPredictions;
            let isRunning = false;

            function showStatus(message, type) {{
                const statusDiv = document.getElementById("status");
                statusDiv.innerHTML = `<div class="status ${{type}}">${{message}}</div>`;
            }}

            async function init() {{
                try {{
                    showStatus("Loading model...", "");
                    const modelURL = URL + "model.json";
                    const metadataURL = URL + "metadata.json";

                    model = await tmImage.load(modelURL, metadataURL);
                    maxPredictions = model.getTotalClasses();

                    showStatus("Starting webcam...", "");
                    const flip = true;
                    webcam = new tmImage.Webcam(300, 300, flip);
                    await webcam.setup();
                    await webcam.play();
                    isRunning = true;

                    document.getElementById("startBtn").style.display = "none";
                    document.getElementById("stopBtn").style.display = "inline-block";

                    window.requestAnimationFrame(loop);

                    document.getElementById("webcam-container").appendChild(webcam.canvas);
                    labelContainer = document.getElementById("label-container");
                    labelContainer.innerHTML = "";
                    for (let i = 0; i < maxPredictions; i++) {{
                        labelContainer.appendChild(document.createElement("div"));
                    }}

                    showStatus("Webcam active! Detecting...", "success");
                }} catch (error) {{
                    showStatus("Error: " + error.message, "error");
                    console.error(error);
                }}
            }}

            async function loop() {{
                if (isRunning) {{
                    webcam.update();
                    await predict();
                    window.requestAnimationFrame(loop);
                }}
            }}

            async function predict() {{
                const prediction = await model.predict(webcam.canvas);

                // Check for high confidence match
                let highestPrediction = prediction[0];
                for (let i = 0; i < maxPredictions; i++) {{
                    const classPrediction = prediction[i].className + ": " +
                                          (prediction[i].probability * 100).toFixed(1) + "%";
                    labelContainer.childNodes[i].innerHTML = classPrediction;

                    if (prediction[i].probability > highestPrediction.probability) {{
                        highestPrediction = prediction[i];
                    }}
                }}

                // Auto-login if confidence > 95%
                if (highestPrediction.probability > 0.95) {{
                    showStatus(`✅ Recognized: ${{highestPrediction.className}}`, "success");
                    // Send login event to Streamlit
                    window.parent.postMessage({{
                        type: 'webcam_login',
                        user: highestPrediction.className,
                        confidence: highestPrediction.probability
                    }}, '*');
                }}
            }}

            function stopWebcam() {{
                if (webcam) {{
                    isRunning = false;
                    webcam.stop();
                    document.getElementById("webcam-container").innerHTML = "";
                    document.getElementById("label-container").innerHTML = "";
                    document.getElementById("startBtn").style.display = "inline-block";
                    document.getElementById("stopBtn").style.display = "none";
                    showStatus("Webcam stopped", "");
                }}
            }}
        </script>
    </body>
    </html>
    """

    # Render the HTML component
    components.html(html_code, height=700, scrolling=True)

    st.divider()

    st.markdown("### 🔒 Security Note")
    st.warning("This is a demo. For production, implement proper authentication backend and HTTPS.")