// MindWell AI Chat API Integration
class MindWellAIChat {
    constructor() {
        this.apiEndpoint = 'http://localhost:8000/api/chat';
        this.conversationHistory = [];
        this.isTyping = false;
    }

    async sendMessage(message, chatContainer) {
        try {
            // Add user message to conversation history
            this.conversationHistory.push({
                message: message,
                is_user: true,
                timestamp: new Date().toISOString()
            });

            // Show typing indicator
            this.showTypingIndicator(chatContainer);

            // Make API call to backend
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: this.conversationHistory.slice(-5) // Send last 5 messages for context
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator(chatContainer);

            // Add AI response to conversation history
            this.conversationHistory.push({
                message: data.response,
                is_user: false,
                timestamp: new Date().toISOString()
            });

            // Return the AI response and suggestions
            return {
                response: data.response,
                suggestions: data.suggestions || []
            };

        } catch (error) {
            console.error('AI Chat API Error:', error);
            this.hideTypingIndicator(chatContainer);
            
            // Return fallback response
            return {
                response: "I'm sorry, I'm having trouble connecting to my AI service right now. Please try again in a moment, or consider reaching out to a counselor if you need immediate support.",
                suggestions: ["Try refreshing the page", "Contact campus counseling services"]
            };
        }
    }

    showTypingIndicator(chatContainer) {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingRow = document.createElement('div');
        typingRow.className = 'message-row bot d-flex align-items-end';
        typingRow.id = 'typing-indicator';

        const typingAvatar = document.createElement('div');
        typingAvatar.className = 'avatar bot';
        typingAvatar.innerHTML = '<i class="fas fa-robot"></i>';

        const typingBubble = document.createElement('div');
        typingBubble.className = 'message-bubble typing-indicator';
        typingBubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

        typingRow.appendChild(typingAvatar);
        typingRow.appendChild(typingBubble);
        chatContainer.appendChild(typingRow);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    hideTypingIndicator(chatContainer) {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    clearHistory() {
        this.conversationHistory = [];
    }

    getConversationHistory() {
        return this.conversationHistory;
    }
}

// Initialize AI chat service
const aiChat = new MindWellAIChat();

// Export for use in other scripts
window.MindWellAIChat = MindWellAIChat;
window.aiChat = aiChat;