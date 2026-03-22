import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import './App.css';

// --- ASSETS ---
import campusBackground from './assets/campus-background.jpg';
import robotImage from './assets/robot-assistant.png';
import collegeLogo from './assets/college_logo.jpg';

// --- SVG ICON ---
const SendIcon = () => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="m22 2-7 20-4-9-9-4Z" />
        <path d="m22 2-11 11" />
    </svg>
);

// --- TYPES ---
interface Message {
    id: number;
    text: string;
    isBot: boolean;
    timestamp: string;
}

interface ChatMessageProps {
    message: string;
    isBot: boolean;
    timestamp: string;
}

// --- COMPONENTS ---

// ... (start of App.tsx)

// --- COMPONENTS ---

// 🆕 New component for the Directions button
const DirectionsButton = () => (
    // Using an <a> tag is best for direct external links
    <a 
        href="https://www.mappls.com/6a2bet" 
        target="_blank" 
        id="get-directions-btn" 
        className="action-btn" // Use the common action-btn class
        rel="noopener noreferrer" // Good security practice for target="_blank"
    >
        Get Directions 🗺️
    </a>
);

// ... (Your existing imports and helper components)

const Header = () => (
    <header className="header">
        <div className="header-container">
            <div className="header-logo">
                <div className="header-logo-icon">
                    <img src={collegeLogo} alt="SVEC Logo" className="logo-img" />
                </div>
                <h1 className="header-title">
                    SVEC Infobot : Our Virtual Campus Guide
                </h1>
            </div>
            
            {/* --- MODIFICATION START --- */}
            <div className="header-actions">
                {/* Existing Study with SVEC Button */}
                <a
                    href="http://127.0.0.1:8002/"
                    className="study-button action-btn" // Added action-btn class for shared styling
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Study with SVEC
                </a>
                
                {/* NEW Get Directions Button */}
                <a 
                    href="https://www.mappls.com/6a2bet" 
                    target="_blank" 
                    id="get-directions-btn" 
                    className="action-btn directions-btn" // Shared styling and a unique class
                    rel="noopener noreferrer" 
                >
                    Get Directions
                </a>
            </div>
            {/* --- MODIFICATION END --- */}
        </div>
    </header>
);

const RobotPanel = () => (
    <div className="robot-panel-container">
        <div className="robot-image-wrapper">
            <div className="robot-glow-effect" />
            <img src={robotImage} alt="AI Robot Assistant" className="robot-image" />
        </div>
        <div className="robot-info">
            <h2 className="robot-title">SVEC Infobot</h2>
            <p className="robot-description">
                Your intelligent AI companion, ready to assist with campus life, academics, and more.
            </p>
            <div className="robot-status">
                <div className="robot-status-indicator" />
                <span className="robot-status-text">Online & Ready</span>
            </div>
        </div>
    </div>
);

const ChatMessage = ({ message, isBot, timestamp }: ChatMessageProps) => {
    const wrapperClass = isBot ? "message-wrapper bot" : "message-wrapper user";
    const bubbleClass = isBot ? "message-bubble bot" : "message-bubble user";

    const formatMessage = (text: string) => {
        // 1️⃣ Remove unwanted fragments like 'target="_blank"', '">', or Markdown brackets
        let cleanText = text.replace(/\[.*?\]\((https?:\/\/[^\s)]+)\)/g, '$1') // remove [text](url)
                        .replace(/" target="_blank" rel="noopener noreferrer">/g, '')
                        .replace(/">/g, '')
                        .trim();

        // 2️⃣ Convert plain URLs to clickable links
        cleanText = cleanText.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // 3️⃣ Convert Markdown-style bold (*text* or text)
        cleanText = cleanText.replace(/\*(.*?)\*/g, '<strong>$1</strong>');

        // 4️⃣ Convert numbered or bullet lists
        cleanText = cleanText.replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>')
                            .replace(/^- (.*)$/gm, '<li>$1</li>')
                            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

        // 5️⃣ Preserve line breaks
        cleanText = cleanText.replace(/\n/g, '<br>');

        return cleanText;
    };
    return (
        <div className={wrapperClass}>
            <div className={bubbleClass}>
                <p
                    className="message-text"
                    dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
                />
                <span className="message-timestamp">{timestamp}</span>
            </div>
        </div>
    );
};

const ChatPanel = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 1,
            text: "Hello! I'm CampusBot, your AI assistant. How can I help you today?",
            isBot: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
    ]);

    const [inputValue, setInputValue] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!inputValue.trim() || loading) return;

        const userMessage: Message = {
            id: messages.length + 1,
            text: inputValue,
            isBot: false,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue("");
        setLoading(true);

        const typingMessage: Message = {
            id: messages.length + 2,
            text: "CampusBot is typing...",
            isBot: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, typingMessage]);

        try {
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: userMessage.text }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();

            setMessages((prev) => [
                ...prev.slice(0, -1),
                {
                    id: messages.length + 2,
                    text: data.answer,
                    isBot: true,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                },
            ]);
        } catch (error) {
            console.error("Error fetching from backend:", error);
            setMessages((prev) => [
                ...prev.slice(0, -1),
                {
                    id: messages.length + 2,
                    text: "Sorry, something went wrong. Please try again.",
                    isBot: true,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") handleSend();
    };

    return (
        <div className="chat-panel-container">
            <div className="chat-header">
                <h2 className="chat-header-title">Chat</h2>
            </div>

            <div className="messages-container">
                {messages.map((message) => (
                    <ChatMessage
                        key={message.id}
                        message={message.text}
                        isBot={message.isBot}
                        timestamp={message.timestamp}
                    />
                ))}
            </div>

            <div className="input-area">
                <div className="input-flex-wrapper">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="chat-input"
                        disabled={loading}
                    />
                    <button onClick={handleSend} className="button" disabled={loading}>
                        <SendIcon />
                    </button>
                </div>
            </div>
        </div>
    );
};

// --- MAIN APP ---
const App = () => (
    <div className="app-container">
        <div
            className="background-image"
            style={{ backgroundImage: `url(${campusBackground})` }}
        />
        <div className="gradient-overlay" />

        <div className="content-wrapper">
            <Header />
            <main className="main-content">
                <div className="content-grid">
                    <RobotPanel />
                    <ChatPanel />
                </div>
            </main>
        </div>
    </div>
);

export default App;

// // --- RENDER APP ---
// const container = document.getElementById('root');
// const root = createRoot(container!);
// root.render(<App />);
