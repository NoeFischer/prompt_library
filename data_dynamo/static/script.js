const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

// Fetch initial message
fetch('/initial-message')
    .then(response => response.json())
    .then(data => {
        appendMessage('DataDynamo', data.message, 'bot');
    });

chatForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    // Display user message
    appendMessage('You', userMessage, 'user');
    userInput.value = '';

    // Fetch bot response
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
    });
    const data = await response.json();

    // Display bot message
    appendMessage('DataDynamo', data.message, 'bot');
});

function appendMessage(sender, message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;

    const senderSpan = document.createElement('strong');
    senderSpan.textContent = sender + ': ';
    messageDiv.appendChild(senderSpan);

    const contentSpan = document.createElement('span');
    contentSpan.innerHTML = marked.parse(message);
    messageDiv.appendChild(contentSpan);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}