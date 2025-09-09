document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');

    // Function to add a message to the chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }
//     async function getRoute(origin, destination) {
//     try {
//         const response = await fetch("http://localhost:8000/route", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ origin, destination })
//         });

//         const data = await response.json();

//         // Insert map into chat
//         const mapFrame = document.createElement("iframe");
//         mapFrame.src = data.map_url + "&output=embed";
//         mapFrame.width = "100%";
//         mapFrame.height = "300";
//         mapFrame.style.border = "0";

//         chatMessages.appendChild(mapFrame);
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//     } catch (error) {
//         addMessage("Could not fetch route. Try again.", "ai");
//     }
// }

async function getRoute(origin, destination) {
    try {
        const response = await fetch("http://localhost:8000/route", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ origin, destination })
        });

        const data = await response.json();

        // Show clickable link instead of iframe
        const link = document.createElement("a");
        link.href = data.map_url;
        link.target = "_blank";  // open in new tab
        link.textContent = "👉 Click here to view the route on Google Maps";

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", "ai-message");
        messageDiv.appendChild(link);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        addMessage("Could not fetch route. Try again.", "ai");
    }
}

    // Function to send a message
    async function sendMessage() {
    const query = userInput.value.trim();
    if (query === '') return;

    addMessage(query, 'user');
    userInput.value = ''; // Clear input

    // Simulate typing indicator
    addMessage('Assistant is typing...', 'ai');

    try {
        // 👉 Check if it's a route query
        const routePattern = /from (.+) to (.+)/i;
        const match = query.match(routePattern);

        if (match) {
            // Remove typing indicator
            chatMessages.removeChild(chatMessages.lastChild);

            const origin = match[1].trim();
            const destination = match[2].trim();

            addMessage(`Finding best route from ${origin} to ${destination}...`, "ai");
            await getRoute(origin, destination);
            return;
        }

        // 👉 Otherwise, normal chat
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        chatMessages.removeChild(chatMessages.lastChild);

        addMessage(data.response, 'ai');

    } catch (error) {
        console.error('Error sending message:', error);
        chatMessages.removeChild(chatMessages.lastChild);
        addMessage('Oops! Something went wrong. Please try again.', 'ai');
    }
}

    // async function sendMessage() {
    //     const query = userInput.value.trim();
    //     if (query === '') return;

    //     addMessage(query, 'user');
    //     userInput.value = ''; // Clear input

    //     // Simulate typing indicator (optional)
    //     addMessage('Assistant is typing...', 'ai');

    //     try {
    //         // This is where you'll make an API call to your backend
    //         const response = await fetch('http://localhost:8000/chat', { // Replace with your backend URL
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //             },
    //             body: JSON.stringify({ query: query }),
    //         });

    //         if (!response.ok) {
    //             throw new Error(`HTTP error! status: ${response.status}`);
    //         }

    //         const data = await response.json();
    //         // Remove typing indicator before adding actual response
    //         chatMessages.removeChild(chatMessages.lastChild);
    //         addMessage(data.response, 'ai');

    //     } catch (error) {
    //         console.error('Error sending message:', error);
    //         // Remove typing indicator and show error
    //         chatMessages.removeChild(chatMessages.lastChild);
    //         addMessage('Oops! Something went wrong. Please try again.', 'ai');
    //     }
    // }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial welcome message
    addMessage('Hello! How can I assist you with information about Sri Vasavi Engineering College?', 'ai');
});