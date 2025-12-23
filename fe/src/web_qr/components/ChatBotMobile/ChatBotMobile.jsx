import React, { useState, useRef, useEffect } from "react";
import classNames from "classnames/bind";
import styles from "./ChatBotMobile.module.scss";
import { BsRobot, BsSendFill } from "react-icons/bs";
import { IoClose } from "react-icons/io5";
import {
  MdOutlineFullscreen,
  MdOutlineFullscreenExit,
} from "react-icons/md";
import axios from "axios";
import Markdown from "react-markdown";

const cx = classNames.bind(styles);

const ChatBotMobile = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [bottomPosition, setBottomPosition] = useState("8rem");

  const messagesEndRef = useRef(null);

  const suggestions = [
    "Món bán chạy nhất?",
    "Gợi ý món cho bữa trưa",
    "Trời mưa nên ăn gì?",
    "Tư vấn món cay",
  ];

  /* ================= SCROLL HANDLE ================= */
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      if (documentHeight - scrollPosition < 100) {
        setBottomPosition("15rem");
      } else {
        setBottomPosition("8rem");
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  /* ================= AUTO SCROLL ================= */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  /* ================= HANDLERS ================= */
  const handleOpenChatbot = () => {
    setIsOpen(true);
    if (messages.length === 0) {
      setMessages([
        {
          sender: "bot",
          text: "Chào bạn 👋 Mình là **FoodieBot** 🤖\n\nMình có thể gợi ý món ăn cho bạn 🍜🍔",
        },
      ]);
    }
  };

  const handleCloseChatbot = () => {
    setIsOpen(false);
    setIsFullScreen(false);
  };

  const handleToggleFullScreen = () => {
    setIsFullScreen((prev) => !prev);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { sender: "user", text: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const res = await axios.get(
        "http://192.168.20.57:8000/api/chatbot/customer",
        { params: { message: userMessage.text } }
      );

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: res.data.reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Có lỗi xảy ra, bạn thử lại nhé!" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = async (text) => {
    if (isLoading) return;

    setMessages((prev) => [...prev, { sender: "user", text }]);
    setIsLoading(true);

    try {
      const res = await axios.get(
        "http://192.168.20.57:8000/api/chatbot/customer",
        { params: { message: text } }
      );

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: res.data.reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Có lỗi xảy ra!" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* CHATBOT ICON */}
      {!isOpen && (
        <div
          className={cx("chatBotIcon")}
          style={{ bottom: bottomPosition }}
          onClick={handleOpenChatbot}
        >
          <BsRobot />
        </div>
      )}

      {/* CHAT WINDOW */}
      {isOpen && (
        <div
          className={cx("chatWindow", { fullscreen: isFullScreen })}
          style={{ bottom: bottomPosition }}
        >
          <div className={cx("chatHeader")}>
            <div className={cx("botInfo")}>
              <BsRobot />
              <span>FoodieBot</span>
            </div>
            <div className={cx("headerActions")}>
              <IoClose onClick={handleCloseChatbot} />
            </div>
          </div>

          <div className={cx("chatBody")}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={cx("message", msg.sender)}
              >
                <div className={cx("bubble")}>
                  <Markdown>{msg.text}</Markdown>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className={cx("message", "bot")}>
                <div className={cx("bubble", "loading")}>
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className={cx("suggestions")}>
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => handleSuggestionClick(s)}
              >
                {s}
              </button>
            ))}
          </div>

          <form className={cx("inputForm")} onSubmit={handleSendMessage}>
            <input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Nhập tin nhắn..."
              disabled={isLoading}
            />
            <button disabled={!inputValue.trim() || isLoading}>
              <BsSendFill />
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default ChatBotMobile;
