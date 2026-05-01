import React, { useState, useEffect, useRef } from "react";
import {
  Send,
  Plus,
  MessageSquare,
  Bot,
  User,
  Loader2,
  FileText,
  ChevronDown,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

import { auth, db } from "../firebase";
import { ChatMessage } from "../types/api";
import {
  collection,
  addDoc,
  getDocs,
  doc,
  updateDoc,
  query,
  orderBy,
  Timestamp,
} from "firebase/firestore";

interface UserDocument {
  id: string;
  fileName: string;
  uploadedAt: string;
}

interface ChatSession {
  id: string;
  title: string;
  fileName: string;
  messages: ChatMessage[];
  createdAt: string;
}

const ChatSection: React.FC = () => {
  const API_URL = "https://ai-legal-assistance-co-pilot-gm09.onrender.com";

  const user = auth.currentUser;
  const userId = user?.uid;

  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] =
    useState<UserDocument | null>(null);
  const [showDocDropdown, setShowDocDropdown] =
    useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // const docsKey = `documents_${userId}`;
  // const chatsKey = `chat_sessions_${userId}`;

  useEffect(() => {
    if (!userId) return;

    const loadData = async () => {
      const docsRef = collection(
        db,
        "users",
        userId,
        "documents"
      );

      const chatsRef = collection(
        db,
        "users",
        userId,
        "chats"
      );

      const docsSnapshot =
        await getDocs(docsRef);

      const chatsSnapshot =
        await getDocs(
          query(
            chatsRef,
            orderBy(
              "createdAt",
              "desc"
            )
          )
        );

      const docs =
        docsSnapshot.docs.map(
          (doc) => ({
            id: doc.id,
            ...doc.data(),
          })
        );

      const chats =
        chatsSnapshot.docs.map(
          (doc) => ({
            id: doc.id,
            ...doc.data(),
          })
        );

      setDocuments(docs as any);
      setChatSessions(chats as any);

      if (chats.length > 0) {
        setActiveChatId(chats[0].id);
      }
    };

    loadData();
  }, [userId]);


  // useEffect(() => {
  //   if (!userId) return;

  //   localStorage.setItem(
  //     chatsKey,
  //     JSON.stringify(chatSessions)
  //   );
  // }, [chatSessions, userId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [chatSessions, isLoading]);

  const activeChat = chatSessions.find(
    (chat) => chat.id === activeChatId
  );

  useEffect(() => {
    if (!activeChat) return;

    if (activeChat.fileName) {
      const doc = documents.find(
        (d) => d.fileName === activeChat.fileName
      );

      if (doc) setSelectedDocument(doc);
    } else {
      setSelectedDocument(null);
    }
  }, [activeChatId, documents]);

  const createNewChat = async () => {
    const currentUser = auth.currentUser;

    if (!currentUser) {
      console.error("No authenticated user");
      return;
    }

    const chatsRef = collection(
      db,
      "users",
      currentUser.uid,
      "chats"
    );

    const newChat = {
      title: "New chat",
      fileName: "",
      messages: [],
      createdAt: Timestamp.now(),
    };

    console.log(auth.currentUser);
    console.log(auth.currentUser?.uid);

    const chatRef = await addDoc(
      chatsRef,
      newChat
    );

    const createdChat = {
      id: chatRef.id,
      ...newChat,
    };

    setChatSessions((prev) => [
      createdChat as ChatSession,
      ...prev,
    ]);

    setActiveChatId(chatRef.id);
    setSelectedDocument(null);
  };

  const updateActiveChat = async (
    chatId: string,
    updatedMessages: ChatMessage[],
    fileName?: string
  ) => {
    const chatRef = doc(
      db,
      "users",
      auth.currentUser!.uid,
      "chats",
      chatId
    );

    await updateDoc(chatRef, {
      messages: updatedMessages,
      fileName: fileName ?? "",
      title:
        updatedMessages[0]?.content.slice(
          0,
          40
        ) || "New chat",
    });

    setChatSessions((prev) =>
      prev.map((chat) =>
        chat.id === chatId
          ? {
            ...chat,
            messages: updatedMessages,
            fileName:
              fileName ??
              chat.fileName,
            title:
              updatedMessages[0]?.content.slice(
                0,
                40
              ) || "New chat",
          }
          : chat
      )
    );
  };

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (
      !currentQuestion.trim() ||
      !activeChat ||
      !selectedDocument
    )
      return;

    const lockedFileName =
      activeChat.fileName || selectedDocument.fileName;

    const userMessage: ChatMessage = {
      type: "user",
      content: currentQuestion.trim(),
      timestamp: new Date(),
    };

    const updatedMessages = [
      ...activeChat.messages,
      userMessage,
    ];

    await updateActiveChat(
      activeChat.id,
      updatedMessages,
      lockedFileName
    );

    const questionToSend = currentQuestion.trim();

    setCurrentQuestion("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/ask-question`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: questionToSend,
            file_name: lockedFileName,
          }),
        }
      );

      const result = await response.json();

      const aiMessage: ChatMessage = {
        type: "ai",
        content: result.answer,
        timestamp: new Date(),
      };

      await updateActiveChat(
        activeChat.id,
        [...updatedMessages, aiMessage],
        lockedFileName
      );
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[91vh] bg-[#010409] text-white overflow-hidden">

      {/* Sidebar */}
      <div className="w-[300px] border-r border-[#30363d] bg-[#010409] flex flex-col">
        <div className="p-4">
          <button
            onClick={createNewChat}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-md border border-[#30363d] hover:bg-[#161b22]"
          >
            <Plus className="w-4 h-4" />
            New chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          {chatSessions.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setActiveChatId(chat.id)}
              className={`w-full text-left px-3 py-3 rounded-md ${activeChatId === chat.id
                ? "bg-[#161b22]"
                : "hover:bg-[#161b22]"
                }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-gray-400" />
                <span className="truncate text-sm">
                  {chat.title}
                </span>
              </div>

              <p className="text-xs text-gray-500 mt-1 truncate">
                {chat.fileName || "No document"}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col">

        {/* Header */}
        <div className="h-14 border-b border-[#21262d] px-8 flex items-center">
          <h2 className="text-sm font-semibold">
            {activeChat?.fileName || "New Chat"}
          </h2>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-4xl mx-auto space-y-10">

            {activeChat?.messages.map(
              (message, index) => (
                <div
                  key={index}
                  className={`flex  ${message.type === "user"
                    ? "justify-end"
                    : "justify-start"
                    }`}
                >
                  <div className="flex gap-4 max-w-3xl text-sm font-normal">

                    {message.type === "ai" && (
                      <div className="w-8 h-8 rounded-full bg-[#21262d] flex items-center justify-center">
                        <Bot className="w-9 h-5" />
                      </div>
                    )}

                    <div
                      className={`rounded-2xl px-6 py-4 ${message.type === "user"
                        ? "bg-[#0d1117]"
                        : "text-[#e6edf3]"
                        }`}
                    >
                      {message.type === "user" ? (
                        <p>{message.content}</p>
                      ) : (
                        <div className="max-w-none text-[10px] text-[#e6edf3] leading-7">
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => (
                                <p className="mb-5 leading-8 text-[14px]">
                                  {children}
                                </p>
                              ),

                              ul: ({ children }) => (
                                <ul className="list-disc pl-8 mb-6 space-y-1">
                                  {children}
                                </ul>
                              ),

                              ol: ({ children }) => (
                                <ol className="list-decimal pl-8 mb-6 space-y-1">
                                  {children}
                                </ol>
                              ),

                              li: ({ children }) => (
                                <li className="leading-6 text-[14px]">
                                  {children}
                                </li>
                              ),

                              h1: ({ children }) => (
                                <h1 className="text-2xl font-semibold mb-6 mt-8">
                                  {children}
                                </h1>
                              ),

                              h2: ({ children }) => (
                                <h2 className="text-xl font-semibold mb-5 mt-8">
                                  {children}
                                </h2>
                              ),

                              h3: ({ children }) => (
                                <h3 className="text-lg font-semibold mb-4 mt-6">
                                  {children}
                                </h3>
                              ),

                              strong: ({ children }) => (
                                <strong className="font-semibold text-white">
                                  {children}
                                </strong>
                              ),

                              blockquote: ({ children }) => (
                                <blockquote className="border-l-4 border-[#30363d] pl-4 italic my-5 text-gray-300">
                                  {children}
                                </blockquote>
                              ),

                              code: ({ children }) => (
                                <code className="bg-[#161b22] px-1 py-0.5 rounded text-sm">
                                  {children}
                                </code>
                              ),
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>

                    {message.type === "user" && (
                      <div className="w-8 h-8 rounded-full bg-[#21262d] flex items-center justify-center">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                </div>
              )
            )}

            {isLoading && (
              <div className="flex gap-3 items-center">
                <Bot className="w-5 h-5" />
                <Loader2 className="w-4 h-4 animate-spin" />
                Thinking...
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Section */}
        <div className="border-t border-[#21262d] p-6">
          <div className="max-w-4xl mx-auto">
            <form
              onSubmit={handleSubmit}
              className="
border
border-[#1f6feb]
rounded-2xl
bg-[#010409]
px-4
py-3
shadow-[0_0_0_1px_rgba(31,111,235,0.25)]
focus-within:shadow-[0_0_0_2px_rgba(31,111,235,0.35)]
transition-all
duration-200
"
            >
              <textarea
                value={currentQuestion}
                onChange={(e) =>
                  setCurrentQuestion(e.target.value)
                }
                placeholder="Ask anything or add context......"
                rows={1}
                className="w-full bg-transparent resize-none outline-none text-white placeholder-gray-500 text-sm font-normal"
              />

              <div className="flex items-center justify-between mt-4">

                {/* Document selector inside input */}
                <div className="relative">
                  <button
                    type="button"
                    disabled={
                      activeChat?.messages.length !== 0
                    }
                    onClick={() =>
                      setShowDocDropdown(
                        !showDocDropdown
                      )
                    }
                    className={`flex items-center gap-2 px-4 py-2 rounded-md border border-[#30363d] text-sm ${activeChat?.messages.length !== 0
                      ? "opacity-60 cursor-not-allowed"
                      : "hover:bg-[#161b22]"
                      }`}
                  >
                    <FileText className="w-4 h-4" />
                    {selectedDocument
                      ? selectedDocument.fileName
                      : "Select document"}
                    <ChevronDown className="w-4 h-4" />
                  </button>

                  {showDocDropdown &&
                    activeChat?.messages.length ===
                    0 && (
                      <div className="absolute bottom-14 left-0 w-72 bg-[#161b22] border border-[#30363d] rounded-md shadow-lg z-50">
                        {documents.map((doc) => (
                          <button
                            key={doc.id}
                            type="button"
                            onClick={() => {
                              setSelectedDocument(doc);
                              setShowDocDropdown(
                                false
                              );
                            }}
                            className="w-full text-left px-4 py-3 hover:bg-[#21262d] text-sm"
                          >
                            {doc.fileName}
                          </button>
                        ))}
                      </div>
                    )}
                </div>

                {/* Send */}
                <div className="flex items-center gap-3">

                  {/* Model Selector */}
                  <button
                    type="button"
                    className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition"
                  >
                    llama-3.3-70b-versatile
                  </button>

                  {/* Divider */}
                  <div className="h-6 w-px bg-[#30363d]" />

                  {/* Send Button */}
                  <button
                    type="submit"
                    disabled={
                      isLoading ||
                      !currentQuestion.trim() ||
                      !selectedDocument
                    }
                    className="flex items-center justify-center text-gray-400 hover:text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" strokeWidth={1.8} />
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatSection;