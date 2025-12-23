import React, { useState, useRef, useEffect } from "react";
import classNames from 'classnames/bind';
import styles from './Chatbot.module.scss';
import { BsRobot, BsSendFill } from "react-icons/bs";
import { IoClose } from "react-icons/io5";
import { MdOutlineFullscreen, MdOutlineFullscreenExit } from "react-icons/md";
import axios from 'axios';
import Markdown from 'react-markdown';

const cx = classNames.bind(styles);

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const messagesEndRef = useRef(null);

    const suggestions = [
        "Món bán chạy nhất?",
        "Gợi ý món cho bữa trưa",
        "Trời mưa nên ăn gì?",
        "Tư vấn món cay",
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleOpenChatbot = () => {
        setIsOpen(true);
        // Set an initial welcome message if the chat is empty
        if (messages.length === 0) {
            setMessages([{ sender: 'bot', text: 'Chào bạn, mình là FoodieBot! Bạn cần mình gợi ý món ăn gì không? 🤖' }]);
        }
    };

    const handleCloseChatbot = () => {
        setIsOpen(false);
    };

    const handleToggleFullScreen = () => {
        setIsFullScreen(prev => !prev);
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (inputValue.trim() === '' || isLoading) return;

        const userMessage = { sender: 'user', text: inputValue };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await axios.get('http://192.168.20.57:8000/api/chatbot/customer', {
                params: {
                    message: inputValue,
                },
            });
            const botMessage = { sender: 'bot', text: response.data.reply };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Error fetching chatbot response:", error);
            const errorMessage = { sender: 'bot', text: 'Ôi, có lỗi rồi! Bạn thử lại sau nhé.' };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = async (suggestion) => {
        if (isLoading) return;

        const userMessage = { sender: 'user', text: suggestion };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            const response = await axios.get('http://192.168.20.57:8000/api/chatbot/customer', { params: { message: suggestion } });
            const botMessage = { sender: 'bot', text: response.data.reply };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Error fetching chatbot response:", error);
            const errorMessage = { sender: 'bot', text: 'Ôi, có lỗi rồi! Bạn thử lại sau nhé.' };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };
    return (
        <>
            <div className={cx('chat-bot-icon')} onClick={handleOpenChatbot}>
                <BsRobot />
            </div>

            {isOpen && (
                <div className={cx('chat-window', { 'fullscreen': isFullScreen })}>
                    <div className={cx('chat-header')}>
                        <div className={cx('bot-info')}>
                            <BsRobot className={cx('bot-avatar')} />
                            <span className={cx('bot-name')}>FoodieBot</span>
                        </div>
                        <div className={cx('header-icons')}>
                            {isFullScreen ? (
                                <MdOutlineFullscreenExit className={cx('fullscreen-icon')} onClick={handleToggleFullScreen} />
                            ) : (
                                <MdOutlineFullscreen className={cx('fullscreen-icon')} onClick={handleToggleFullScreen} />
                            )}
                            <IoClose className={cx('close-icon')} onClick={handleCloseChatbot} />
                        </div>
                    </div>
                    <div className={cx('chat-body')}>
                        {messages.map((msg, index) => (
                            <div key={index} className={cx('message', `message-${msg.sender}`)}>
                                <div className={cx('message-content')}>
                                    <Markdown>{msg.text}</Markdown>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className={cx('message', 'message-bot')}>
                                <div className={cx('message-content', 'loading-dots')}>
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                    <div className={cx('suggestions-container')}>
                        {suggestions.map((item, index) => (
                            <button key={index} className={cx('suggestion-button')} onClick={() => handleSuggestionClick(item)}>
                                {item}
                            </button>
                        ))}
                    </div>
                    <form className={cx('chat-input-form')} onSubmit={handleSendMessage}>
                        <input
                            type="text"
                            className={cx('chat-input')}
                            placeholder="Nhập tin nhắn..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            disabled={isLoading}
                        />
                        <button type="submit" className={cx('send-button')} disabled={isLoading || !inputValue.trim()}>
                            <BsSendFill />
                        </button>
                    </form>
                </div>
            )}
        </>
    );
};

export default Chatbot; 