// Hide and display side bar
document.getElementById('toggle-sidebar').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    var content = document.getElementById('main-content');
    var button = document.getElementById('toggle-sidebar');
    // Toggle sidebar visibility based on the 'left' property or class presence
    if (sidebar.style.left === '0px' || sidebar.style.left === '') {
        sidebar.style.left = '-250px';  // Move sidebar out of view
        content.style.marginLeft = '0';  // Expand content area
        button.style.left = '5px';
    } else {
        sidebar.style.left = '0';  // Bring sidebar into view
        content.style.marginLeft = '250px';  // Reset content margin
        button.style.left = '255px';
    }
});

document.getElementById('image-box').addEventListener('click', function() {
    window.location.href = '';
})

// Add Event Listener to chat-input, which send the message if press enter
document.getElementById('chat-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();  
        sendMessage();
        document.getElementById('chat-input').value = '';
    }
});

// Function to send message through chat input
let isSent = false;
function sendMessage() {
    var userInput = document.getElementById('chat-input').value;
    if (userInput.trim() !== '') {
        socket.send(JSON.stringify({ message: userInput }));
    }
    if (!isSent) {
        isSent = true;
    }
}

let socket = new WebSocket("ws://" + window.location.host + "/ws");
let messageQueue = [];
// Flag to track if a message is being processed
let isProcessing = false;

// Receiving data from socket
socket.onmessage = function(event) {
    let response = JSON.parse(event.data);
    // Add the new message to the queue
    messageQueue.push(response);
    // Start processing if not already processing
    if (!isProcessing) {
        processNextMessage();
    }
};

// Function handles displaying message, character illustration (emotion image), and playing audio (text-to-speech)
function processNextMessage() {
    if (messageQueue.length > 0) {
        // Set the flag to true to indicate processing
        isProcessing = true;
        // Get the next message from the queue
        let response = messageQueue.shift();
        // Process the message
        audioImage(response).then(() => {
            // After processing, call processNextMessage to check for more messages
            isProcessing = false;
            processNextMessage();
        });
    }
}

// Speech recognition process
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
isRecording = false;

if (typeof SpeechRecognition !== "undefined") {
    const recognition = new SpeechRecognition();
    let isRecording = false; // Initialize the recording state
    recognition.continuous = false;
    recognition.lang = "en-US";

    const button = document.getElementById('start-button');
    button.addEventListener('click', () => {
        // Toggle recording state
        if (isRecording) {
            recognition.stop();
        } else {
            isRecording = true;
            recognition.start();
            // Apply active state styles
            button.style.backgroundColor = '#383838';
            button.style.color = 'white';
        }
    });

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chat-input').value = transcript;
        sendMessage();
        toggleButton();
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
        toggleButton();
    };

    recognition.onend = function() {
        console.log("Speech recognition service disconnected");
        toggleButton();
    };

    function toggleButton() {
        isRecording = false;
        // Reset styles to enable CSS hover to work again
        button.style.backgroundColor = '';
        button.style.color = '';
    }
} else {
    console.log("Speech recognition not supported");
    document.getElementById('start-button').style.display = 'none';
}


// Display character illustration (emotion image), message, and playing audio (text-to-speech) process
let currentEmotion = ""; // Tracks the currently displayed emotion
let currentAudio = null; // Maintain a reference to the currently playing audio

function audioImage(data) {
    return new Promise((resolve) => {
        if (isSent) {
            document.getElementById('chat-input').value = '';
            isSent = false; // Reset the flag
        }
        const emotion = data.emotion; // The emotion for emotion image
        const url = data.audio_url; // The URL of the current audio
        const message = data.message; // The sentence to display
        const imagePath = `/static/images/${emotion}.jpg`; // The path to the current emotion image

        // Clear the previous message and update the chat history with the new sentence
        const history = document.getElementById('chat-history');
        while (history.firstChild) {
            history.removeChild(history.firstChild);
        }
        const newMessage = document.createElement('div');
        newMessage.textContent = message;
        history.appendChild(newMessage);

        // Update the emotion image
        const emotionImage = document.getElementById('emotion-image');
        emotionImage.src = imagePath;
        emotionImage.hidden = false;

        const audio = new Audio(url);
        audio.onloadeddata = () => {
            console.log("Audio data loaded:", url);
            audio.play()
            .then(() => {
                // Handle successful playback
                console.log("Audio started playing immediately after loading.");
            })
            .catch((error) => {
                console.error("Error playing audio:", error);
            });

            // Resolve the promise when the audio ends
            audio.onended = () => {
                resolve();
            };
    }});
}
