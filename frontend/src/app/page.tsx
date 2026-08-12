"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  FileText,
  Send,
  Plus,
  Trash2,
  LogOut,
  FolderOpen,
  CheckCircle,
  AlertTriangle,
  Play,
  Terminal,
  Search,
  BookOpen,
  User,
  ShieldAlert,
  Bug,
  RefreshCw,
  Copy,
  ChevronDown,
  ChevronUp,
  Cpu,
  Loader2,
  Key,
  Database,
  ArrowRight,
  Sun,
  Moon,
  Info,
  Layers,
  Sparkles,
  ChevronRight,
  GitBranch,
  Eye,
  EyeOff,
  Pencil,
  Check,
  X,
  Code2,
  CornerDownLeft,
} from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

// Custom Github SVG Icon to avoid package version discrepancies
const GithubIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    viewBox="0 0 24 24"
    width="24"
    height="24"
    stroke="currentColor"
    strokeWidth="2"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
  </svg>
);

// Copy code utility button
const CopyButton = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 px-2 py-1 text-xs bg-github-bg hover:bg-github-border border border-github-border rounded text-github-muted hover:text-github-text transition-colors font-sans cursor-pointer"
    >
      <Copy className="w-3.5 h-3.5" />
      {copied ? "Copied!" : "Copy"}
    </button>
  );
};

// Custom markup and code rendering component
const MarkdownText = ({ text }: { text: string }) => {
  if (!text) return null;

  const parts = text.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-3 text-sm leading-relaxed text-github-text font-sans select-text">
      {parts.map((part, index) => {
        if (part.startsWith("```")) {
          const match = part.match(/```(\w*)\n([\s\S]*?)```/);
          const lang = match ? match[1] : "";
          const code = match ? match[2] : part.slice(3, -3);

          return (
            <div
              key={index}
              className="my-3 border border-github-border rounded-md overflow-hidden bg-black/35 font-mono text-xs select-text"
            >
              <div className="flex justify-between items-center px-4 py-2 bg-github-panel border-b border-github-border text-github-muted select-none">
                <span>{lang || "code"}</span>
                <CopyButton text={code} />
              </div>
              <pre className="p-4 overflow-x-auto text-[13px] leading-relaxed text-[#e6edf3] select-text bg-[#05070a]">
                <code>{code}</code>
              </pre>
            </div>
          );
        }

        const lines = part.split("\n");
        return (
          <div key={index} className="space-y-2">
            {lines.map((line, lineIdx) => {
              if (line.startsWith("### ")) {
                return (
                  <h3 key={lineIdx} className="text-base font-semibold mt-4 mb-2 text-github-text select-text">
                    {line.slice(4)}
                  </h3>
                );
              }
              if (line.startsWith("## ")) {
                return (
                  <h2 key={lineIdx} className="text-lg font-bold mt-5 mb-2 text-github-text border-b border-github-border/40 pb-1 select-text">
                    {line.slice(3)}
                  </h2>
                );
              }
              if (line.startsWith("# ")) {
                return (
                  <h1 key={lineIdx} className="text-xl font-extrabold mt-6 mb-3 text-github-text border-b border-github-border pb-2 select-text">
                    {line.slice(2)}
                  </h1>
                );
              }
              if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
                const cleanLine = line.trim().slice(2);
                return (
                  <ul key={lineIdx} className="list-disc list-inside ml-4 space-y-1 my-1 select-text">
                    <li>{renderInlineStyles(cleanLine)}</li>
                  </ul>
                );
              }
              return (
                <p key={lineIdx} className="min-h-[1rem] select-text">
                  {renderInlineStyles(line)}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

function renderInlineStyles(text: string) {
  const inlineRegex = /(\*\*.*?\*\*|`.*?`)/g;
  const parts = text.split(inlineRegex);

  return parts.map((part, idx) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={idx} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={idx}
          className="px-1.5 py-0.5 rounded font-mono text-xs bg-black/40 text-github-agent border border-github-border"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

interface TraceStep {
  emoji: string;
  label: string;
  details?: string;
}

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  trace?: TraceStep[];
  active_specialist?: "nexus" | "octolyzer" | "synthex";
}

export default function Home() {
  // Global Theme state
  const [isDark, setIsDark] = useState<boolean>(true);

  // View state: 'landing' | 'auth' | 'dashboard'
  const [view, setView] = useState<"landing" | "auth" | "dashboard">("landing");
  const [landingTab, setLandingTab] = useState<"home" | "features" | "how-it-works">("home");
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [signUpStep, setSignUpStep] = useState<"form" | "otp">("form");

  // Authentication session
  const [token, setToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string>("");

  // Auth inputs
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [otp, setOtp] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");
  const [resendStatus, setResendStatus] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // Chat Sessions (ChatGPT style)
  interface ChatSession {
    id: string;
    title: string;
    tool: "agent" | "github" | "codex";
    messages: Message[];
  }

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentTool, setCurrentTool] = useState<"agent" | "github" | "codex">("agent");
  const [editingMsgIdx, setEditingMsgIdx] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [renamingSessionId, setRenamingSessionId] = useState<string | null>(null);
  const [renameTitle, setRenameTitle] = useState("");

  // Current active chat states
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [currentTrace, setCurrentTrace] = useState<TraceStep[]>([]);
  const [expandedTraceIdx, setExpandedTraceIdx] = useState<number | null>(null);

  // Ingestion states
  const [githubUrl, setGithubUrl] = useState("");
  const [indexingLoading, setIndexingLoading] = useState(false);
  const [indexingStatus, setIndexingStatus] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [activeRepos, setActiveRepos] = useState<string[]>([]);
  const [uploadedDocs, setUploadedDocs] = useState<string[]>([]);

  // ChatGPT file attachments & Claude loader
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [loaderIndex, setLoaderIndex] = useState(0);
  const loaderStatuses = [
    "Thinking...",
    "Scanning project workspace...",
    "Locating target source files...",
    "Tracing import trees...",
    "Drafting corrections...",
    "Running AST compiler syntax check...",
    "Verifying results with verification gate...",
    "Formulating final explanation..."
  ];

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Theme initializer
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
      setIsDark(false);
      document.documentElement.classList.remove("dark");
    } else {
      setIsDark(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  // Check for local session & Supabase redirect hash on mount
  useEffect(() => {
    // 1. Detect tokens in URL hash (from Supabase email confirmation redirect)
    if (typeof window !== "undefined" && window.location.hash) {
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);
      const accessToken = params.get("access_token");
      const refreshToken = params.get("refresh_token");

      if (accessToken) {
        let emailFromToken = "";
        try {
          const payloadPart = accessToken.split(".")[1];
          const decodedPayload = JSON.parse(atob(payloadPart.replace(/-/g, "+").replace(/_/g, "/")));
          emailFromToken = decodedPayload.email || "";
        } catch (e) {
          console.error("JWT decoding failed:", e);
        }

        localStorage.setItem("token", accessToken);
        if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
        if (emailFromToken) localStorage.setItem("email", emailFromToken);

        setToken(accessToken);
        setUserEmail(emailFromToken);
        setView("dashboard");
        fetchHistory(accessToken);
        
        // Clean URL hash from address bar
        window.history.replaceState(null, "", window.location.pathname);
        return;
      }
    }

    // 2. Fallback to localStorage session
    const savedToken = localStorage.getItem("token");
    const savedEmail = localStorage.getItem("email");
    if (savedToken) {
      setToken(savedToken);
      if (savedEmail) setUserEmail(savedEmail);
      setView("dashboard");
      fetchHistory(savedToken);
    }
  }, []);

  // Scroll chat window on message update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, chatLoading, currentTrace]);

  // Cycle loader statuses when chatLoading is active
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (chatLoading) {
      setLoaderIndex(0);
      interval = setInterval(() => {
        setLoaderIndex((prev) => (prev + 1) % loaderStatuses.length);
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [chatLoading]);

  const saveSessionsToStorage = (updatedSessions: ChatSession[]) => {
    localStorage.setItem("reactise_sessions", JSON.stringify(updatedSessions));
  };

  const fetchHistory = async (authToken: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/memory/`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (response.ok) {
        // Load sessions from storage
        const savedSessions = localStorage.getItem("reactise_sessions");
        if (savedSessions) {
          const parsed = JSON.parse(savedSessions);
          setSessions(parsed);
          if (parsed.length > 0) {
            setCurrentSessionId(parsed[0].id);
            setCurrentTool(parsed[0].tool);
            setMessages(parsed[0].messages);
          }
        }
        
        // Scan workspaces on disk
        try {
          const docScan = await fetch(`${BACKEND_URL}/documents/`, {
            headers: { Authorization: `Bearer ${authToken}` },
          });
          if (docScan.ok) {
            const docList = await docScan.json();
            setUploadedDocs(docList);
          }
        } catch (e) {
          console.error("Failed to fetch documents:", e);
        }
        
        setActiveRepos(["react-enterprise-agent"]);
      } else if (response.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");

    try {
      const response = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("email", data.email);
        setToken(data.access_token);
        setUserEmail(data.email);
        setView("dashboard");
        fetchHistory(data.access_token);
      } else {
        setAuthError(data.detail || "Invalid email or password.");
      }
    } catch (err) {
      setAuthError("Failed to connect to FastAPI server.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setAuthLoading(true);
    setResendStatus("Resending OTP verification code...");
    setAuthError("");

    try {
      const response = await fetch(`${BACKEND_URL}/auth/resend-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, type: "signup" }),
      });

      const data = await response.json();
      if (response.ok) {
        setResendStatus("Verification code resent! Please check your email.");
      } else {
        setAuthError(data.detail || "Failed to resend verification email.");
      }
    } catch (err) {
      setAuthError("Failed to connect to backend server.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");

    try {
      const response = await fetch(`${BACKEND_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.access_token) {
          // Email confirmation is disabled! Direct login.
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("email", data.email);
          setToken(data.access_token);
          setUserEmail(data.email);
          setView("dashboard");
          fetchHistory(data.access_token);
        } else {
          // Email confirmation is enabled! Prompt for OTP code.
          setSignUpStep("otp");
        }
      } else {
        setAuthError(data.detail || "Signup failed. Please try again.");
      }
    } catch (err) {
      setAuthError("Failed to connect to FastAPI server.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    setResendStatus("");

    let success = false;
    try {
      const response = await fetch(`${BACKEND_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token: otp, type: "signup" }),
      });

      const data = await response.json();

      if (response.ok) {
        success = true;
        setResendStatus("✅ Account registered successfully! Logging you in...");
        
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("email", data.email);
        setToken(data.access_token);
        setUserEmail(data.email);
        
        setTimeout(() => {
          setView("dashboard");
          fetchHistory(data.access_token);
          setResendStatus("");
          setAuthLoading(false);
        }, 1500);
      } else {
        setAuthError(data.detail || "Verification failed. Please check the code.");
      }
    } catch (err) {
      setAuthError("Failed to connect to FastAPI server.");
    } finally {
      if (!success) {
        setAuthLoading(false);
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    localStorage.removeItem("reactise_sessions");
    setToken(null);
    setUserEmail("");
    setMessages([]);
    setSessions([]);
    setCurrentSessionId(null);
    setView("landing");
    setSignUpStep("form");
    setAuthMode("login");
    setEmail("");
    setPassword("");
    setName("");
    setOtp("");
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setCurrentTrace([]);
    setExpandedTraceIdx(null);
    setInput("");
  };

  const handleSelectSession = (sessionId: string) => {
    const session = sessions.find((s) => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      setCurrentTool(session.tool);
      setMessages(session.messages);
      setCurrentTrace([]);
      setExpandedTraceIdx(null);
    }
  };

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = sessions.filter((s) => s.id !== sessionId);
    setSessions(updated);
    saveSessionsToStorage(updated);
    
    if (currentSessionId === sessionId) {
      if (updated.length > 0) {
        setCurrentSessionId(updated[0].id);
        setCurrentTool(updated[0].tool);
        setMessages(updated[0].messages);
      } else {
        handleNewChat();
      }
    }
  };

  const handleRenameSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const session = sessions.find((s) => s.id === sessionId);
    if (session) {
      setRenamingSessionId(sessionId);
      setRenameTitle(session.title);
    }
  };

  const handleSaveRename = (sessionId: string) => {
    const updated = sessions.map((s) => {
      if (s.id === sessionId) {
        return { ...s, title: renameTitle.trim() || s.title };
      }
      return s;
    });
    setSessions(updated);
    saveSessionsToStorage(updated);
    setRenamingSessionId(null);
  };

  const handleSendMessage = async (e?: React.FormEvent, directMessage?: string) => {
    if (e) e.preventDefault();
    const rawMsg = directMessage || input;
    if (!rawMsg.trim() || !token) return;

    const userMessage = rawMsg.trim();
    if (!directMessage) setInput("");

    // If a file is attached, upload it first (ChatGPT style)
    let currentAttached = attachedFile;
    if (currentAttached) {
      setChatLoading(true);
      const uploadSuccess = await uploadAttachedFile(currentAttached);
      setAttachedFile(null);
      if (!uploadSuccess) {
        setChatLoading(false);
        return;
      }
    }
    
    const newUserMsg = { role: "user" as const, content: userMessage };
    const updatedMessages = [...messages, newUserMsg];
    
    let activeSessionId = currentSessionId;
    let updatedSessions = [...sessions];

    // If new chat session, generate details
    if (!activeSessionId) {
      activeSessionId = "session_" + Math.random().toString(36).substring(7);
      const newTitle = userMessage.substring(0, 30) + (userMessage.length > 30 ? "..." : "");
      
      const newSession: ChatSession = {
        id: activeSessionId,
        title: newTitle,
        tool: currentTool,
        messages: updatedMessages
      };
      updatedSessions = [newSession, ...sessions];
      setSessions(updatedSessions);
      saveSessionsToStorage(updatedSessions);
      setCurrentSessionId(activeSessionId);
    } else {
      updatedSessions = sessions.map((s) => {
        if (s.id === activeSessionId) {
          return { ...s, messages: updatedMessages };
        }
        return s;
      });
      setSessions(updatedSessions);
      saveSessionsToStorage(updatedSessions);
    }

    setMessages(updatedMessages);
    setChatLoading(true);
    setCurrentTrace([
      { emoji: "🤔", label: "Planning...", details: "Schedules sequential code browsing steps." }
    ]);

    try {
      // Append tool prefix context to steers planner instructions
      let promptText = userMessage;
      if (currentTool === "github") {
        promptText = `[GitHub Agent Workspace] ${userMessage}`;
      } else if (currentTool === "codex") {
        promptText = `[Codex Code Refactor] ${userMessage}`;
      }

      // Convert history to payload schema
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch(`${BACKEND_URL}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: activeSessionId,
          message: promptText,
          history: historyPayload,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: "Request failed." }));
        const errorMsg = {
          role: "assistant" as const,
          content: `❌ Error: ${data.detail || "Request failed."}`,
        };
        setMessages([...updatedMessages, errorMsg]);
        setChatLoading(false);
        return;
      }

      // Initialize empty assistant message in bubble for streaming
      let assistantMsg: Message = {
        role: "assistant",
        content: "",
        trace: [],
        active_specialist: currentTool === "github" ? "octolyzer" : currentTool === "codex" ? "synthex" : "nexus",
      };

      setMessages([...updatedMessages, assistantMsg]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let streamBuffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        streamBuffer += decoder.decode(value, { stream: true });
        const lines = streamBuffer.split("\n\n");
        streamBuffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim() || !line.startsWith("data: ")) continue;
          try {
            const parsed = JSON.parse(line.substring(6));
            if (parsed.type === "trace") {
              assistantMsg.trace = [...(assistantMsg.trace || []), {
                emoji: parsed.emoji,
                label: parsed.label,
                details: parsed.details,
              }];
              setMessages([...updatedMessages, { ...assistantMsg }]);
            } else if (parsed.type === "token") {
              assistantMsg.content += parsed.content;
              setMessages([...updatedMessages, { ...assistantMsg }]);
            } else if (parsed.type === "done") {
              assistantMsg.active_specialist = parsed.active_specialist;
              if (parsed.tools_used?.includes("github")) {
                const matchUrl = userMessage.match(/https?:\/\/github\.com\/[^\s]+/);
                if (matchUrl) {
                  const parsedUrl = new URL(matchUrl[0]);
                  const repo = parsedUrl.pathname.split("/").filter(Boolean).pop();
                  if (repo && !activeRepos.includes(repo)) {
                    setActiveRepos((prev) => [...prev, repo]);
                  }
                }
              }
              setMessages([...updatedMessages, { ...assistantMsg }]);
            }
          } catch (e) {
            console.error("Stream parse error:", e);
          }
        }
      }

      const finalMessages = [...updatedMessages, { ...assistantMsg }];
      const finalSessions = updatedSessions.map((s) => {
        if (s.id === activeSessionId) {
          return { ...s, messages: finalMessages };
        }
        return s;
      });
      setSessions(finalSessions);
      saveSessionsToStorage(finalSessions);
    } catch (err) {
      const errorMsg = {
        role: "assistant" as const,
        content: "⚠️ Connection error: Failed to connect to ReActise agent API.",
      };
      setMessages([...updatedMessages, errorMsg]);
    } finally {
      setChatLoading(false);
      setCurrentTrace([]);
    }
  };

  const handleEditSubmit = async (idx: number) => {
    if (!editText.trim() || !currentSessionId) return;

    setEditingMsgIdx(null);
    setChatLoading(true);
    setCurrentTrace([
      { emoji: "🤔", label: "Planning...", details: "Schedules sequential code browsing steps." }
    ]);
    setExpandedTraceIdx(null);

    // Truncate messages up to the edited user message
    const truncatedHistory = messages.slice(0, idx);
    const updatedUserMsg = { role: "user" as const, content: editText };
    const updatedMessages = [...truncatedHistory, updatedUserMsg];
    
    setMessages(updatedMessages);

    const updatedSessions = sessions.map((s) => {
      if (s.id === currentSessionId) {
        return { ...s, messages: updatedMessages };
      }
      return s;
    });
    setSessions(updatedSessions);
    saveSessionsToStorage(updatedSessions);

    try {
      let promptText = editText;
      if (currentTool === "github") {
        promptText = `[GitHub Agent Workspace] ${editText}`;
      } else if (currentTool === "codex") {
        promptText = `[Codex Code Refactor] ${editText}`;
      }

      const historyPayload = truncatedHistory.map((m) => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch(`${BACKEND_URL}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: promptText,
          history: historyPayload,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: "Request failed." }));
        const errorMsg = {
          role: "assistant" as const,
          content: `❌ Error: ${data.detail || "Request failed."}`,
        };
        setMessages([...updatedMessages, errorMsg]);
        setChatLoading(false);
        return;
      }

      // Initialize empty assistant message in bubble for streaming
      let assistantMsg: Message = {
        role: "assistant",
        content: "",
        trace: [],
        active_specialist: currentTool === "github" ? "octolyzer" : currentTool === "codex" ? "synthex" : "nexus",
      };

      setMessages([...updatedMessages, assistantMsg]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let streamBuffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        streamBuffer += decoder.decode(value, { stream: true });
        const lines = streamBuffer.split("\n\n");
        streamBuffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim() || !line.startsWith("data: ")) continue;
          try {
            const parsed = JSON.parse(line.substring(6));
            if (parsed.type === "trace") {
              assistantMsg.trace = [...(assistantMsg.trace || []), {
                emoji: parsed.emoji,
                label: parsed.label,
                details: parsed.details,
              }];
              setMessages([...updatedMessages, { ...assistantMsg }]);
            } else if (parsed.type === "token") {
              assistantMsg.content += parsed.content;
              setMessages([...updatedMessages, { ...assistantMsg }]);
            } else if (parsed.type === "done") {
              assistantMsg.active_specialist = parsed.active_specialist;
              setMessages([...updatedMessages, { ...assistantMsg }]);
            }
          } catch (e) {
            console.error("Stream parse error:", e);
          }
        }
      }

      const finalMessages = [...updatedMessages, { ...assistantMsg }];
      const finalSessions = sessions.map((s) => {
        if (s.id === currentSessionId) {
          return { ...s, messages: finalMessages };
        }
        return s;
      });
      setSessions(finalSessions);
      saveSessionsToStorage(finalSessions);
    } catch (err) {
      const errorMsg = {
        role: "assistant" as const,
        content: "❌ Connection error to FastAPI backend server.",
      };
      setMessages([...updatedMessages, errorMsg]);
    } finally {
      setChatLoading(false);
      setCurrentTrace([]);
    }
  };

  const handleIndexGithub = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl.trim() || !token) return;

    setIndexingLoading(true);
    setIndexingStatus("Cloning repository and indexing code vector stores...");

    try {
      const response = await fetch(`${BACKEND_URL}/github/index`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ repo_url: githubUrl.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setIndexingStatus(`✅ ${data.message || "Repository cloned and indexed!"}`);
        const urlParts = githubUrl.trim().replace(/\/$/, "").split("/");
        const repoName = urlParts[urlParts.length - 1].replace(".git", "");
        if (!activeRepos.includes(repoName)) {
          setActiveRepos((prev) => [...prev, repoName]);
        }
        setGithubUrl("");

        // Trigger auto-summarization of repo
        const triggerMsg = `Analyze this indexed repository: read the README.md file, summarize the project structure, list the main modules, and suggest 3 code optimizations or adjustments I can make.`;
        setTimeout(() => {
          handleSendMessage(undefined, triggerMsg);
        }, 1000);
      } else {
        setIndexingStatus(`❌ Error: ${data.detail || "Index failed."}`);
      }
    } catch (err) {
      setIndexingStatus("❌ Connection error to indexing node.");
    } finally {
      setIndexingLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setAttachedFile(files[0]);
    }
  };

  const uploadAttachedFile = async (fileToUpload: File): Promise<boolean> => {
    if (!token) return false;
    setUploadLoading(true);
    setUploadStatus(`Indexing file: ${fileToUpload.name}...`);

    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const response = await fetch(`${BACKEND_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setUploadStatus(`✅ Index complete: ${fileToUpload.name}`);
        setUploadedDocs((prev) => {
          if (prev.includes(fileToUpload.name)) return prev;
          return [...prev, fileToUpload.name];
        });
        return true
      } else {
        setUploadStatus(`❌ Index failed: ${data.detail || "Upload failed."}`);
        return false;
      }
    } catch (err) {
      setUploadStatus("❌ Connection error uploading document.");
      return false;
    } finally {
      setUploadLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${BACKEND_URL}/memory/`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        setMessages([]);
        setSessions([]);
        setCurrentSessionId(null);
        localStorage.removeItem("reactise_sessions");
      }
    } catch (err) {
      console.error("Failed to clear memory:", err);
    }
  };

  const toggleTheme = () => {
    if (isDark) {
      setIsDark(false);
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      setIsDark(true);
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    }
  };

  return (
    <div className="min-h-screen bg-github-bg text-github-text flex flex-col transition-colors duration-200 relative select-none">
      {/* Background Dot Mesh Grid (Premium Detail) */}
      <div className="absolute inset-0 mesh-grid opacity-30 pointer-events-none select-none z-0" />

      {/* HEADER BAR (Only visible on landing/auth page) */}
      {view !== "dashboard" && (
        <header className="sticky top-0 z-50 flex items-center justify-between px-4 py-3 bg-github-panel/85 backdrop-blur border-b border-github-border transition-colors duration-200">
          {/* Logo */}
          <div 
            onClick={() => setView("landing")}
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            <img src="/logo.png" alt="ReActise Logo" className="w-6 h-6 rounded-full object-cover border border-github-border bg-white shrink-0" />
            <span className="text-xl font-bold tracking-tight text-github-text font-sans">
              ReActise
            </span>
          </div>

          {/* Theme switch & Navigation */}
          <div className="flex items-center gap-4 select-none">
            {view === "landing" && (
              <nav className="hidden sm:flex items-center gap-4 text-sm font-medium font-sans">
                <button 
                  onClick={() => setLandingTab("home")} 
                  className={`hover:text-github-text transition-colors cursor-pointer ${landingTab === "home" ? "text-github-text border-b-2 border-github-agent pb-1" : "text-github-muted"}`}
                >
                  Home
                </button>
                <button 
                  onClick={() => setLandingTab("features")} 
                  className={`hover:text-github-text transition-colors cursor-pointer ${landingTab === "features" ? "text-github-text border-b-2 border-github-agent pb-1" : "text-github-muted"}`}
                >
                  Features
                </button>
                <button 
                  onClick={() => setLandingTab("how-it-works")} 
                  className={`hover:text-github-text transition-colors cursor-pointer ${landingTab === "how-it-works" ? "text-github-text border-b-2 border-github-agent pb-1" : "text-github-muted"}`}
                >
                  How It Works
                </button>
              </nav>
            )}

            <button
              onClick={toggleTheme}
              className="p-1.5 rounded-full hover:bg-github-border/40 text-github-muted hover:text-github-text transition-colors cursor-pointer"
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {token ? (
              <button
                onClick={() => setView("dashboard")}
                className="px-3.5 py-1.5 text-xs font-semibold text-white bg-github-agent hover:bg-[#8f5ae8] rounded border border-github-agent/50 shadow-sm transition-colors cursor-pointer font-sans"
              >
                Go to Workspace
              </button>
            ) : (
              <button
                onClick={() => {
                  setAuthMode("login");
                  setView("auth");
                }}
                className="px-3.5 py-1.5 text-xs font-semibold text-white bg-github-agent hover:bg-[#8f5ae8] rounded border border-github-agent/50 shadow-sm transition-colors cursor-pointer font-sans"
              >
                Sign In
              </button>
            )}
          </div>
        </header>
      )}

      {/* 1. LANDING VIEW */}
      {view === "landing" && (
        <main className="flex-1 flex flex-col max-w-6xl mx-auto w-full px-4 py-12 md:py-20 select-text z-10">
          {landingTab === "home" && (
            <div className="flex-1 flex flex-col md:flex-row items-center gap-12">
              <div className="flex-1 space-y-6 text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-github-agent/10 border border-github-agent/30 rounded-full text-xs font-bold text-github-agent tracking-wide uppercase font-sans animate-pulse">
                  <Sparkles className="w-3.5 h-3.5" /> Core Agentic Engine Live
                </div>
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-github-text leading-tight font-sans">
                  The Persistent Coding Agent That <span className="text-github-agent">ReActs</span>.
                </h1>
                <p className="text-base md:text-lg text-github-muted leading-relaxed font-sans max-w-xl">
                  ReActise connects directly to your codebase repository, analyzes syntax structures, writes precise changes, and verifies compile stability before delivering solutions.
                </p>
                <div className="flex flex-wrap gap-4 pt-2">
                  <button
                    onClick={() => {
                      setAuthMode("signup");
                      setSignUpStep("form");
                      setView("auth");
                    }}
                    className="px-5 py-2.5 text-sm font-semibold text-white bg-github-success hover:bg-[#2c973e] border border-transparent rounded shadow-sm hover:shadow transition-colors flex items-center gap-2 cursor-pointer font-sans"
                  >
                    Get Started Free <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setLandingTab("features")}
                    className="px-5 py-2.5 text-sm font-semibold text-github-text bg-github-panel hover:bg-github-border border border-github-border rounded shadow-sm hover:shadow transition-colors cursor-pointer font-sans"
                  >
                    Explore Features
                  </button>
                </div>
              </div>

              {/* Graphic Graphic Box */}
              <div className="flex-1 w-full max-w-md bg-github-panel border border-github-border rounded-xl p-5 shadow-2xl relative select-none">
                <div className="absolute top-2.5 right-3 flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
                </div>
                <p className="text-[10px] text-github-muted font-mono uppercase tracking-wider mb-4 pb-2 border-b border-github-border/40">
                  Agent Execution Trace Timeline
                </p>
                <div className="space-y-4 font-mono text-[11px] text-github-muted text-left">
                  <div className="flex items-start gap-2.5">
                    <span className="text-github-agent">🤔</span>
                    <div>
                      <span className="font-semibold text-github-text">Planning...</span>
                      <p className="text-[10px] text-github-muted/80">Schedules repository index lookup.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <span className="text-github-warning">🔍</span>
                    <div>
                      <span className="font-semibold text-github-text">Searching auth_service.py</span>
                      <p className="text-[10px] text-github-muted/80">Locates email SMTP handler config.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <span className="text-github-success">⚙️</span>
                    <div>
                      <span className="font-semibold text-github-text">Writing Code Fix</span>
                      <p className="text-[10px] text-github-muted/80">Replaces environment credential maps.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <span className="text-github-agent">✅</span>
                    <div>
                      <span className="font-semibold text-github-text">AST Verifier Passed</span>
                      <p className="text-[10px] text-github-muted/80">0 syntax compile errors detected.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {landingTab === "features" && (
            <div className="space-y-12">
              <div className="text-center space-y-3">
                <h2 className="text-3xl font-extrabold text-github-text font-sans">Meet Your AI Engineering Team</h2>
                <p className="text-sm text-github-muted max-w-lg mx-auto font-sans">
                  Three specialized agents, each designed for a different dimension of software development.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Nexus */}
                <div className="group p-6 bg-github-panel border border-github-border rounded-xl space-y-4 text-left shadow-sm hover:border-[#6366f1]/40 hover:shadow-lg hover:shadow-[#6366f1]/5 transition-all duration-300 font-sans relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#6366f1]/10 to-transparent rounded-bl-full pointer-events-none" />
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#6366f1] to-[#a855f7] flex items-center justify-center text-white shadow-md shadow-purple-500/20">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-extrabold text-github-text tracking-tight">Nexus</h3>
                    <p className="text-[10px] font-bold text-[#6366f1] uppercase tracking-wider mt-0.5">General AI Companion</p>
                  </div>
                  <p className="text-xs text-github-muted leading-relaxed">
                    Your all-purpose AI developer assistant. Ask anything — from debugging logic errors to explaining complex architectures, writing documentation, or brainstorming solutions. Nexus understands context, remembers conversations, and adapts to your coding style.
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#6366f1]/10 text-[#6366f1] rounded-full border border-[#6366f1]/20">Planning</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#6366f1]/10 text-[#6366f1] rounded-full border border-[#6366f1]/20">Debugging</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#6366f1]/10 text-[#6366f1] rounded-full border border-[#6366f1]/20">Docs</span>
                  </div>
                </div>

                {/* Octolyzer */}
                <div className="group p-6 bg-github-panel border border-github-border rounded-xl space-y-4 text-left shadow-sm hover:border-[#f59e0b]/40 hover:shadow-lg hover:shadow-[#f59e0b]/5 transition-all duration-300 font-sans relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#f59e0b]/10 to-transparent rounded-bl-full pointer-events-none" />
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#f59e0b] to-[#ef4444] flex items-center justify-center text-white shadow-md shadow-orange-500/20">
                    <GitBranch className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-extrabold text-github-text tracking-tight">Octolyzer</h3>
                    <p className="text-[10px] font-bold text-[#f59e0b] uppercase tracking-wider mt-0.5">GitHub Intelligence Agent</p>
                  </div>
                  <p className="text-xs text-github-muted leading-relaxed">
                    Paste any public GitHub URL and Octolyzer clones it, indexes every file into vector stores, and builds a semantic map of your entire codebase. Navigate directory trees, trace import chains, discover API endpoints, and analyze test coverage — all through natural language.
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#f59e0b]/10 text-[#f59e0b] rounded-full border border-[#f59e0b]/20">Cloning</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#f59e0b]/10 text-[#f59e0b] rounded-full border border-[#f59e0b]/20">Indexing</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#f59e0b]/10 text-[#f59e0b] rounded-full border border-[#f59e0b]/20">RAG Search</span>
                  </div>
                </div>

                {/* Synthex */}
                <div className="group p-6 bg-github-panel border border-github-border rounded-xl space-y-4 text-left shadow-sm hover:border-[#10b981]/40 hover:shadow-lg hover:shadow-[#10b981]/5 transition-all duration-300 font-sans relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#10b981]/10 to-transparent rounded-bl-full pointer-events-none" />
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
                    <Code2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-extrabold text-github-text tracking-tight">Synthex</h3>
                    <p className="text-[10px] font-bold text-[#10b981] uppercase tracking-wider mt-0.5">Code Synthesis Engine</p>
                  </div>
                  <p className="text-xs text-github-muted leading-relaxed">
                    Purpose-built for high-fidelity code generation and refactoring. Synthex writes production-ready code, applies targeted fixes, converts between languages, and validates every edit through AST compilation gates — ensuring zero syntax errors before delivery.
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#10b981]/10 text-[#10b981] rounded-full border border-[#10b981]/20">Refactor</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#10b981]/10 text-[#10b981] rounded-full border border-[#10b981]/20">Generate</span>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#10b981]/10 text-[#10b981] rounded-full border border-[#10b981]/20">AST Verify</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {landingTab === "how-it-works" && (
            <div className="space-y-12 select-none">
              <div className="text-center space-y-3 font-sans">
                <h2 className="text-3xl font-extrabold text-github-text">The ReAct Execution Loop</h2>
                <p className="text-sm text-github-muted max-w-xl mx-auto">
                  Trace the exact steps our LangGraph architecture executes to compile, write, and verify your code files.
                </p>
              </div>

              <div className="max-w-2xl mx-auto relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-[2px] before:bg-github-border">
                {/* Step 1 */}
                <div className="relative pl-12 pb-8">
                  <div className="absolute left-[7px] w-5 h-5 bg-github-panel border-4 border-github-agent rounded-full flex items-center justify-center" />
                  <div className="space-y-1.5 font-sans">
                    <span className="text-xs font-bold text-github-agent uppercase tracking-wider">Step 1</span>
                    <h4 className="text-lg font-bold text-github-text">Cloning or Ingesting Files</h4>
                    <p className="text-xs text-github-muted leading-relaxed">
                      You index your public GitHub URL or drop specification PDFs. The system clones files to your account directory on disk and parses text into database memory.
                    </p>
                  </div>
                </div>
                {/* Step 2 */}
                <div className="relative pl-12 pb-8">
                  <div className="absolute left-[7px] w-5 h-5 bg-github-panel border-4 border-github-warning rounded-full flex items-center justify-center" />
                  <div className="space-y-1.5 font-sans">
                    <span className="text-xs font-bold text-github-warning uppercase tracking-wider">Step 2</span>
                    <h4 className="text-lg font-bold text-github-text">Sequential Step-Planning</h4>
                    <p className="text-xs text-github-muted leading-relaxed">
                      The planner node evaluates your question, looks up active workspaces, and schedules a sequential plan of actions (list directory, read code files, check web info) to compile full context.
                    </p>
                  </div>
                </div>
                {/* Step 3 */}
                <div className="relative pl-12 pb-8">
                  <div className="absolute left-[7px] w-5 h-5 bg-github-panel border-4 border-github-success rounded-full flex items-center justify-center" />
                  <div className="space-y-1.5 font-sans">
                    <span className="text-xs font-bold text-github-success uppercase tracking-wider">Step 3</span>
                    <h4 className="text-lg font-bold text-github-text">Executing Corrections & Syntax Checks</h4>
                    <p className="text-xs text-github-muted leading-relaxed">
                      The executor loops through the steps, writes necessary fixes directly to files, and executes checks to ensure code compiles and doesn't contain python syntax errors.
                    </p>
                  </div>
                </div>
                {/* Step 4 */}
                <div className="relative pl-12">
                  <div className="absolute left-[7px] w-5 h-5 bg-github-panel border-4 border-github-agent rounded-full flex items-center justify-center" />
                  <div className="space-y-1.5 font-sans">
                    <span className="text-xs font-bold text-github-agent uppercase tracking-wider">Step 4</span>
                    <h4 className="text-lg font-bold text-github-text">Verification & Response</h4>
                    <p className="text-xs text-github-muted leading-relaxed">
                      The verifier checks the final results against the initial prompt. If approved, the agent returns the detailed code refactor along with the execution timeline logs.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      )}

      {/* 2. AUTHENTICATION VIEW */}
      {view === "auth" && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <div className="w-full max-w-[340px] flex flex-col space-y-6">
            <div className="flex flex-col items-center space-y-2 select-none">
              <img src="/logo.png" alt="ReActise Logo" className="w-16 h-16 rounded-full object-cover border border-github-border bg-white shadow-md" />
              <h1 className="text-2xl font-normal text-github-text tracking-tight font-sans">
                Sign in to ReActise
              </h1>
            </div>

            <div className="bg-github-panel border border-github-border rounded-md p-5 shadow-lg">
              {resendStatus && (
                <div className="mb-4 p-3 bg-github-success/15 border border-github-success/30 rounded text-github-success text-xs text-center font-sans">
                  {resendStatus}
                </div>
              )}
              {authError && (
                <div className="mb-4 p-3 bg-github-error/15 border border-github-error/30 rounded text-github-error text-xs flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{authError}</span>
                </div>
              )}

              {/* Login mode */}
              {authMode === "login" && (
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-1.5 font-sans">
                    <label className="block text-xs font-normal text-github-muted">Email address</label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-3 py-1.5 text-sm bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link focus:ring-1 focus:ring-github-link transition-all text-github-text"
                    />
                  </div>
                  <div className="space-y-1.5 font-sans">
                    <div className="flex justify-between items-center">
                      <label className="block text-xs font-normal text-github-muted">Password</label>
                    </div>
                    <div className="relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-3 pr-10 py-1.5 text-sm bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link focus:ring-1 focus:ring-github-link transition-all text-github-text"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-github-muted hover:text-github-text bg-transparent border-0 cursor-pointer p-0"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={authLoading}
                    className="w-full py-1.5 text-sm font-semibold text-white bg-github-success hover:bg-[#2c973e] border border-[#2c973e]/50 rounded cursor-pointer transition-colors flex items-center justify-center gap-2 font-sans"
                  >
                    {authLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Sign in"}
                  </button>
                </form>
              )}

              {/* Sign up mode */}
              {authMode === "signup" && signUpStep === "form" && (
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-1.5 font-sans">
                    <label className="block text-xs font-normal text-github-muted">Full Name</label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-3 py-1.5 text-sm bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link focus:ring-1 focus:ring-github-link transition-all text-github-text"
                    />
                  </div>
                  <div className="space-y-1.5 font-sans">
                    <label className="block text-xs font-normal text-github-muted">Email address</label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-3 py-1.5 text-sm bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link focus:ring-1 focus:ring-github-link transition-all text-github-text"
                    />
                  </div>
                  <div className="space-y-1.5 font-sans">
                    <label className="block text-xs font-normal text-github-muted">Password</label>
                    <div className="relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        required
                        minLength={8}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-3 pr-10 py-1.5 text-sm bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link focus:ring-1 focus:ring-github-link transition-all text-github-text"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-github-muted hover:text-github-text bg-transparent border-0 cursor-pointer p-0"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={authLoading}
                    className="w-full py-1.5 text-sm font-semibold text-white bg-github-success hover:bg-[#2c973e] border border-[#2c973e]/50 rounded cursor-pointer transition-colors flex items-center justify-center gap-2 font-sans"
                  >
                    {authLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Sign up"}
                  </button>
                </form>
              )}

              {/* Sign up OTP confirmation step */}
              {authMode === "signup" && signUpStep === "otp" && (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div className="space-y-2 text-center font-sans">
                    <Key className="w-8 h-8 text-github-warning mx-auto animate-bounce" />
                    <p className="text-xs text-github-muted leading-relaxed">
                      We have sent a 6-digit confirmation code to your email. Enter it below to verify your account:
                    </p>
                  </div>
                  <div className="space-y-1.5">
                    <label className="block text-xs font-normal text-github-muted font-sans text-center">6-digit OTP Code</label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      pattern="\d{6}"
                      placeholder="123456"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      className="w-full px-3 py-1.5 text-center text-lg font-mono tracking-widest bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link transition-all text-github-text"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={authLoading}
                    className="w-full py-1.5 text-sm font-semibold text-white bg-github-success hover:bg-[#2c973e] border border-[#2c973e]/50 rounded cursor-pointer transition-colors flex items-center justify-center gap-2 font-sans"
                  >
                    {authLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Verify Code"}
                  </button>
                  <div className="text-center mt-2.5">
                    <button
                      type="button"
                      onClick={handleResendOtp}
                      disabled={authLoading}
                      className="text-xs text-github-link hover:underline bg-transparent border-0 cursor-pointer font-sans"
                    >
                      Didn't receive a code? Resend Code
                    </button>
                  </div>
                </form>
              )}
            </div>

            <div className="border border-github-border rounded-md py-4 px-5 text-center text-xs bg-github-panel font-sans">
              {authMode === "login" ? (
                <span className="text-github-muted">
                  New to ReActise?{" "}
                  <button
                    onClick={() => {
                      setAuthMode("signup");
                      setAuthError("");
                      setShowPassword(false);
                    }}
                    className="text-github-link hover:underline font-medium cursor-pointer"
                  >
                    Create an account
                  </button>
                </span>
              ) : (
                <span className="text-github-muted">
                  Already have an account?{" "}
                  <button
                    onClick={() => {
                      setAuthMode("login");
                      setSignUpStep("form");
                      setAuthError("");
                    }}
                    className="text-github-link hover:underline font-medium cursor-pointer"
                  >
                    Sign in
                  </button>
                </span>
              )}
            </div>
            
            <button
              onClick={() => setView("landing")}
              className="text-xs text-github-muted hover:text-github-text hover:underline transition-colors text-center font-sans cursor-pointer"
            >
              &larr; Back to landing page
            </button>
          </div>
        </div>
      )}

      {/* 3. DASHBOARD VIEW (ChatGPT / Antigravity Style Layout) */}
      {view === "dashboard" && (
        <div className="flex-1 flex overflow-hidden h-[100vh]">
          {/* Hidden File Input for Prompt Bar Uploads */}
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf"
            className="hidden"
            onChange={handleFileSelect}
          />

          {/* LEFT SIDEBAR */}
          <aside className="hidden md:flex w-72 bg-github-panel border-r border-github-border flex-col shrink-0 transition-colors duration-200">
            {/* Sidebar Header & Brand */}
            <div className="p-4 border-b border-github-border flex items-center justify-between">
              <div 
                onClick={() => setView("landing")}
                className="flex items-center gap-2.5 cursor-pointer select-none"
              >
                <img src="/logo.png" alt="ReActise Logo" className="w-6 h-6 rounded-full object-cover border border-github-border bg-white shrink-0" />
                <span className="text-lg font-bold tracking-tight text-github-text font-sans">
                  ReActise
                </span>
              </div>
              <button
                onClick={toggleTheme}
                className="p-1.5 rounded-full hover:bg-github-border/40 text-github-muted hover:text-github-text transition-colors cursor-pointer"
              >
                {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Tool Selection List */}
            <div className="p-3 border-b border-github-border space-y-1 select-none">
              <span className="block text-[10px] font-bold text-github-muted uppercase tracking-wider pl-2 pb-1.5 font-sans">
                Active Tools
              </span>
              {/* Tool 1: The Agent */}
              <button
                onClick={() => setCurrentTool("agent")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors cursor-pointer text-left font-sans ${currentTool === "agent" ? "bg-github-bg text-github-agent border border-github-border" : "text-github-muted hover:bg-github-bg/50 hover:text-github-text border border-transparent"}`}
              >
                <Sparkles className="w-4 h-4 shrink-0 text-github-agent" />
                <div className="flex flex-col min-w-0">
                  <span className="font-semibold leading-tight text-github-text">Nexus</span>
                  <span className="text-[10px] text-github-muted/80 font-normal mt-0.5">General AI Assistant</span>
                </div>
              </button>

              {/* Tool 2: The GitHub Agent */}
              <button
                onClick={() => setCurrentTool("github")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors cursor-pointer text-left font-sans ${currentTool === "github" ? "bg-github-bg text-github-agent border border-github-border" : "text-github-muted hover:bg-github-bg/50 hover:text-github-text border border-transparent"}`}
              >
                <GitBranch className="w-4 h-4 shrink-0 text-github-agent" />
                <div className="flex flex-col min-w-0">
                  <span className="font-semibold leading-tight text-github-text">Octolyzer</span>
                  <span className="text-[10px] text-github-muted/80 font-normal mt-0.5">GitHub Intelligence</span>
                </div>
              </button>

              {/* Tool 3: The Codex */}
              <button
                onClick={() => setCurrentTool("codex")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors cursor-pointer text-left font-sans ${currentTool === "codex" ? "bg-github-bg text-github-agent border border-github-border" : "text-github-muted hover:bg-github-bg/50 hover:text-github-text border border-transparent"}`}
              >
                <Code2 className="w-4 h-4 shrink-0 text-github-agent" />
                <div className="flex flex-col min-w-0">
                  <span className="font-semibold leading-tight text-github-text">Synthex</span>
                  <span className="text-[10px] text-github-muted/80 font-normal mt-0.5">Code Intelligence</span>
                </div>
              </button>
            </div>

            {/* New Chat Button */}
            <div className="p-3 select-none">
              <button
                onClick={handleNewChat}
                className="w-full py-2 bg-github-agent hover:bg-[#8f5ae8] text-white rounded-lg cursor-pointer transition-colors flex items-center justify-center gap-2 text-sm font-semibold font-sans border border-github-agent/50 shadow-sm"
              >
                <Plus className="w-4 h-4" /> New chat
              </button>
            </div>

            {/* Chat History Memory list */}
            <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 select-none">
              <span className="block text-[10px] font-bold text-github-muted uppercase tracking-wider pl-2 pb-1.5 font-sans">
                Chat History
              </span>
              {sessions.length === 0 ? (
                <div className="text-center py-6 text-xs text-github-muted/70 font-sans">
                  No past chats saved
                </div>
              ) : (
                sessions.map((session) => {
                  const isActive = session.id === currentSessionId;
                  const isRenaming = session.id === renamingSessionId;

                  return (
                    <div
                      key={session.id}
                      onClick={() => !isRenaming && handleSelectSession(session.id)}
                      className={`group flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer relative ${isActive ? "bg-github-bg border border-github-border text-github-text" : "text-github-muted hover:bg-github-bg/40 hover:text-github-text"}`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0 flex-1">
                        {session.tool === "github" ? (
                          <GitBranch className="w-3.5 h-3.5 shrink-0 text-github-muted" />
                        ) : session.tool === "codex" ? (
                          <Code2 className="w-3.5 h-3.5 shrink-0 text-github-muted" />
                        ) : (
                          <Sparkles className="w-3.5 h-3.5 shrink-0 text-github-muted" />
                        )}
                        
                        {isRenaming ? (
                          <input
                            type="text"
                            value={renameTitle}
                            onChange={(e) => setRenameTitle(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleSaveRename(session.id);
                              if (e.key === "Escape") setRenamingSessionId(null);
                            }}
                            autoFocus
                            className="bg-github-panel border border-github-border rounded px-1.5 py-0.5 text-xs text-github-text focus:outline-none w-full"
                          />
                        ) : (
                          <span className="truncate font-sans font-medium">{session.title}</span>
                        )}
                      </div>

                      {/* Rename / Delete Actions */}
                      {!isRenaming && (
                        <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1.5 pl-2 shrink-0 transition-opacity z-10">
                          <button
                            onClick={(e) => handleRenameSession(session.id, e)}
                            className="p-1 hover:bg-github-border/50 text-github-muted hover:text-github-text rounded bg-transparent border-0 cursor-pointer"
                          >
                            <Pencil className="w-3 h-3" />
                          </button>
                          <button
                            onClick={(e) => handleDeleteSession(session.id, e)}
                            className="p-1 hover:bg-github-error/10 text-github-muted hover:text-github-error rounded bg-transparent border-0 cursor-pointer"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      )}

                      {isRenaming && (
                        <div className="flex items-center gap-1 shrink-0 z-10 pl-2">
                          <button
                            onClick={() => handleSaveRename(session.id)}
                            className="p-0.5 hover:bg-github-success/20 text-github-success rounded bg-transparent border-0 cursor-pointer"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => setRenamingSessionId(null)}
                            className="p-0.5 hover:bg-github-error/20 text-github-error rounded bg-transparent border-0 cursor-pointer"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            {/* Uploaded Documents List */}
            <div className="flex-1 overflow-y-auto px-3 py-2 border-t border-github-border/40 select-none max-h-[220px]">
              <span className="block text-[10px] font-bold text-github-muted uppercase tracking-wider pl-2 pb-1.5 font-sans">
                Uploaded Documents
              </span>
              {uploadedDocs.length === 0 ? (
                <div className="text-center py-4 text-[11px] text-github-muted/70 font-sans">
                  No documents uploaded
                </div>
              ) : (
                uploadedDocs.map((doc) => (
                  <div
                    key={doc}
                    onClick={() => setInput(`Summarize or analyze details about the uploaded document "${doc}": `)}
                    className="group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-github-muted hover:bg-github-bg/40 hover:text-github-text transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <FileText className="w-3.5 h-3.5 shrink-0 text-github-link" />
                      <span className="truncate font-sans font-medium">{doc}</span>
                    </div>
                    
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        try {
                          const res = await fetch(`${BACKEND_URL}/documents/${encodeURIComponent(doc)}`, {
                            method: "DELETE",
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          if (res.ok) {
                            setUploadedDocs((prev) => prev.filter((d) => d !== doc));
                          }
                        } catch (err) {
                          console.error("Failed to delete document:", err);
                        }
                      }}
                      className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-github-error/10 text-github-muted hover:text-github-error rounded bg-transparent border-0 cursor-pointer shrink-0 transition-opacity"
                      title="Delete document"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* User details & logout */}
            <div className="p-4 border-t border-github-border flex items-center justify-between font-sans">
              <div className="flex items-center gap-2 min-w-0 max-w-[70%] select-text font-sans">
                <User className="w-4 h-4 text-github-muted shrink-0" />
                <span className="truncate text-xs font-semibold text-github-muted">{userEmail}</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-1.5 text-github-muted hover:text-github-error hover:bg-github-error/10 rounded-lg cursor-pointer transition-colors border border-transparent"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </aside>

          {/* MAIN CHAT AREA */}
          <main className="flex-1 flex flex-col overflow-hidden bg-github-bg h-[100vh] relative">
            {/* Mobile Header Bar */}
            <header className="md:hidden flex items-center justify-between px-4 py-3 bg-github-panel border-b border-github-border select-none">
              <div 
                onClick={() => setView("landing")}
                className="flex items-center gap-2 cursor-pointer select-none"
              >
                <img src="/logo.png" alt="ReActise Logo" className="w-5 h-5 rounded-full bg-white" />
                <span className="text-sm font-bold text-github-text font-sans">ReActise</span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={toggleTheme}
                  className="p-1 hover:bg-github-border text-github-muted rounded-full"
                >
                  {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </button>
                <button
                  onClick={handleLogout}
                  className="p-1 hover:bg-github-error/10 text-github-muted rounded-full"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </header>

            {/* Chat Header showing active Tool context */}
            <div className="hidden md:flex px-6 py-3 bg-github-panel border-b border-github-border items-center justify-between select-none">
              <div className="flex items-center gap-2.5 font-sans">
                {currentTool === "github" ? (
                  <GitBranch className="w-4 h-4 text-github-agent" />
                ) : currentTool === "codex" ? (
                  <Code2 className="w-4 h-4 text-github-agent" />
                ) : (
                  <Sparkles className="w-4 h-4 text-github-agent" />
                )}
                <div>
                  <h3 className="text-sm font-bold text-github-text">
                    {currentTool === "github"
                      ? "Octolyzer"
                      : currentTool === "codex"
                      ? "Synthex"
                      : "Nexus"}
                  </h3>
                  <p className="text-[10px] text-github-muted">
                    {currentTool === "github"
                      ? "Deep codebase intelligence — parse, index & navigate any repository"
                      : currentTool === "codex"
                      ? "Precision code synthesis — refactor, generate & verify with AST gates"
                      : "Your multi-modal AI developer companion — plan, build & ship faster"}
                  </p>
                </div>
              </div>
              
              {/* Active Workspace Status indicator */}
              {activeRepos.length > 0 && (
                <div className="flex items-center gap-1.5 bg-github-bg border border-github-border px-2.5 py-1 rounded-md text-[10px] text-github-muted font-mono">
                  <Database className="w-3.5 h-3.5 text-github-success" />
                  <span>Workspace: {activeRepos[0]}</span>
                </div>
              )}
            </div>

            {/* Inline Config Drawer when GitHub Agent is selected */}
            {currentTool === "github" && (
              <div className="px-6 py-2.5 bg-github-panel/60 border-b border-github-border flex flex-col md:flex-row gap-3 items-center justify-between select-none transition-all duration-200">
                <div className="flex items-center gap-1.5 text-xs text-github-muted font-sans font-semibold">
                  <GithubIcon className="w-4 h-4 text-github-text shrink-0" />
                  <span>Repository URL:</span>
                </div>
                <form onSubmit={handleIndexGithub} className="flex-1 max-w-lg flex items-center gap-2 w-full">
                  <input
                    type="url"
                    required
                    placeholder="https://github.com/user/repo"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    className="flex-1 px-2.5 py-1 text-xs bg-github-bg border border-github-border rounded focus:outline-none focus:border-github-link text-github-text"
                  />
                  <button
                    type="submit"
                    disabled={indexingLoading}
                    className="px-3.5 py-1 text-xs font-semibold text-white bg-github-success hover:bg-[#2c973e] rounded cursor-pointer transition-colors flex items-center gap-1.5 shrink-0 font-sans"
                  >
                    {indexingLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : "Index repo"}
                  </button>
                </form>
                {indexingStatus && (
                  <span className="text-[10px] font-mono text-github-muted bg-github-bg px-2 py-0.5 border border-github-border rounded max-w-xs truncate">
                    {indexingStatus}
                  </span>
                )}
              </div>
            )}

            {/* Messages History Container */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-6 py-12 select-none">
                  <div className="p-1.5 bg-github-panel border border-github-border rounded-full shadow-lg">
                    <img src="/logo.png" alt="ReActise Logo" className="w-14 h-14 rounded-full object-cover border border-github-border bg-white" />
                  </div>
                  <div className="space-y-1.5 font-sans">
                    <h2 className="text-xl font-bold text-github-text">
                      {currentTool === "github"
                        ? "What repo should we explore?"
                        : currentTool === "codex"
                        ? "What code should we build?"
                        : "How can I help you today?"}
                    </h2>
                    <p className="text-xs text-github-muted leading-relaxed">
                      {currentTool === "github"
                        ? "Paste a GitHub URL or ask about repository files, directory layouts, and dependency trees."
                        : currentTool === "codex"
                        ? "Describe a feature, paste a code snippet, or request a precision refactor with compile verification."
                        : "Ask anything — from quick questions to full codebase analysis and code generation."}
                    </p>
                  </div>
                  <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2 font-sans">
                    {currentTool === "agent" && (
                      <>
                        <button onClick={() => setInput("Explain how async/await works in Python with examples.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Explain async/await in Python</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Write a REST API endpoint for user registration with validation.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Build a registration endpoint</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Identify if my workspace code compiles correctly.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Check code compilation</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Review my project structure and suggest improvements.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Review project structure</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                      </>
                    )}
                    {currentTool === "github" && (
                      <>
                        <button onClick={() => setInput("Index https://github.com/langchain-ai/langgraph and show me the directory tree.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Clone & explore LangGraph</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Show the imports and dependencies across all Python files.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Map file dependencies</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Find all API endpoints defined in this repository.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Discover all API routes</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Analyze the test coverage and suggest missing test cases.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Analyze test coverage</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                      </>
                    )}
                    {currentTool === "codex" && (
                      <>
                        <button onClick={() => setInput("Refactor auth_service.py to use bcrypt for password hashing.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Refactor with bcrypt hashing</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Generate a complete CRUD module for a Todo app with FastAPI.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Generate CRUD module</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Add comprehensive error handling and input validation to my API.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Add error handling</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                        <button onClick={() => setInput("Convert this JavaScript file to TypeScript with proper types.")} className="p-3 bg-github-panel hover:bg-github-border/60 border border-github-border rounded-xl text-left text-xs text-github-muted hover:text-github-text transition-all cursor-pointer flex items-center justify-between gap-2">
                          <span>Convert JS → TypeScript</span>
                          <ArrowRight className="w-3.5 h-3.5 text-github-agent shrink-0" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-6 max-w-3xl mx-auto pb-4">
                  {messages.map((msg, idx) => {
                    const isUser = msg.role === "user";
                    const isEditing = idx === editingMsgIdx;

                    return (
                      <div
                        key={idx}
                        className="group flex gap-3 w-full"
                      >
                        {/* Avatar */}
                        <div className="shrink-0 mt-1">
                          {isUser ? (
                            <div className="w-7 h-7 bg-gradient-to-br from-[#6366f1] to-[#a855f7] rounded-full flex items-center justify-center text-[11px] text-white font-bold shadow-sm">
                              <User className="w-3.5 h-3.5" />
                            </div>
                          ) : (
                            <div className="w-7 h-7 rounded-full flex items-center justify-center text-white shadow-sm shrink-0 select-none overflow-hidden">
                              {msg.active_specialist === "octolyzer" ? (
                                <div className="w-full h-full bg-gradient-to-br from-[#f59e0b] to-[#ef4444] flex items-center justify-center">
                                  <GitBranch className="w-4 h-4 text-white" />
                                </div>
                              ) : msg.active_specialist === "synthex" ? (
                                <div className="w-full h-full bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center">
                                  <Code2 className="w-4 h-4 text-white" />
                                </div>
                              ) : (
                                <div className="w-full h-full bg-gradient-to-br from-[#6366f1] to-[#a855f7] flex items-center justify-center">
                                  <Sparkles className="w-4 h-4 text-white" />
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {/* Name label */}
                          <p className="text-xs font-bold text-github-text mb-1 font-sans select-none flex items-center gap-1.5">
                            {isUser ? (
                              "You"
                            ) : (
                              <>
                                {msg.active_specialist === "octolyzer" ? (
                                  <>🌿 <span className="text-[#f59e0b]">Octolyzer (GitHub Intelligence)</span></>
                                ) : msg.active_specialist === "synthex" ? (
                                  <>💻 <span className="text-[#10b981]">Synthex (Code Intelligence)</span></>
                                ) : (
                                  <>✨ <span className="text-[#a855f7]">Nexus (General AI Assistant)</span></>
                                )}
                              </>
                            )}
                          </p>

                          {isUser && isEditing ? (
                            <div className="bg-github-panel border border-github-border rounded-lg p-3 space-y-2.5">
                              <textarea
                                value={editText}
                                onChange={(e) => setEditText(e.target.value)}
                                className="w-full min-h-[70px] p-2 bg-github-bg border border-github-border rounded text-sm text-github-text focus:outline-none focus:border-github-link font-sans resize-y"
                              />
                              <div className="flex items-center gap-2 justify-end">
                                <button
                                  onClick={() => setEditingMsgIdx(null)}
                                  className="px-3 py-1.5 text-xs text-github-muted bg-github-bg border border-github-border rounded hover:bg-github-border/40 cursor-pointer font-sans"
                                >
                                  Cancel
                                </button>
                                <button
                                  onClick={() => handleEditSubmit(idx)}
                                  disabled={!editText.trim()}
                                  className="px-3 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-[#6366f1] to-[#a855f7] hover:from-[#818cf8] hover:to-[#c084fc] rounded cursor-pointer transition-colors disabled:opacity-50 font-sans"
                                >
                                  Save & Submit
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="relative">
                              <div className="text-sm text-github-text font-sans leading-relaxed select-text">
                                <MarkdownText text={msg.content} />
                              </div>

                              {/* Hover actions: copy + edit */}
                              <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 mt-2 transition-opacity select-none">
                                <button
                                  onClick={() => { navigator.clipboard.writeText(msg.content); }}
                                  className="p-1 text-github-muted hover:text-github-text hover:bg-github-border/30 rounded cursor-pointer transition-all bg-transparent border-0"
                                  title="Copy message"
                                >
                                  <Copy className="w-3.5 h-3.5" />
                                </button>
                                {isUser && !chatLoading && (
                                  <button
                                    onClick={() => {
                                      setEditingMsgIdx(idx);
                                      setEditText(msg.content);
                                    }}
                                    className="p-1 text-github-muted hover:text-github-text hover:bg-github-border/30 rounded cursor-pointer transition-all bg-transparent border-0"
                                    title="Edit message"
                                  >
                                    <Pencil className="w-3.5 h-3.5" />
                                  </button>
                                )}
                              </div>

                              {/* Trace log for assistant responses */}
                              {!isUser && msg.trace && msg.trace.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-github-border/30 select-none">
                                  <button
                                    onClick={() =>
                                      setExpandedTraceIdx(expandedTraceIdx === idx ? null : idx)
                                    }
                                    className="flex items-center gap-1.5 text-xs font-mono text-github-agent hover:underline cursor-pointer"
                                  >
                                    <Terminal className="w-3.5 h-3.5" />
                                    <span>
                                      {expandedTraceIdx === idx ? "Hide execution trace" : "View execution trace"}
                                    </span>
                                    {expandedTraceIdx === idx ? (
                                      <ChevronUp className="w-3.5 h-3.5" />
                                    ) : (
                                      <ChevronDown className="w-3.5 h-3.5" />
                                    )}
                                  </button>

                                  {expandedTraceIdx === idx && (
                                    <div className="mt-2 bg-black/30 border border-github-border rounded-md p-3 space-y-2.5 font-mono text-xs text-github-muted leading-relaxed select-text">
                                      <div className="space-y-2.5 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[1px] before:bg-github-border/50">
                                        {msg.trace.map((step, stepIdx) => (
                                          <div key={stepIdx} className="flex items-start gap-3 relative pl-1">
                                            <div className="w-5 h-5 bg-github-bg border border-github-border rounded-full flex items-center justify-center text-xs shrink-0 z-10">
                                              {step.emoji}
                                            </div>
                                            <div className="space-y-0.5">
                                              <p className="font-semibold text-github-text">{step.label}</p>
                                              {step.details && (
                                                <p className="text-[11px] text-github-muted">{step.details}</p>
                                              )}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}

                  {/* LOADING - ChatGPT style thinking indicator */}
                  {chatLoading && (
                    <div className="flex gap-3 w-full select-none">
                      <div className="shrink-0 mt-1">
                        <div className="w-7 h-7 rounded-full flex items-center justify-center text-white shadow-sm shrink-0 select-none overflow-hidden">
                          {currentTool === "github" ? (
                            <div className="w-full h-full bg-gradient-to-br from-[#f59e0b] to-[#ef4444] flex items-center justify-center">
                              <GitBranch className="w-4 h-4 text-white" />
                            </div>
                          ) : currentTool === "codex" ? (
                            <div className="w-full h-full bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center">
                              <Code2 className="w-4 h-4 text-white" />
                            </div>
                          ) : (
                            <div className="w-full h-full bg-gradient-to-br from-[#6366f1] to-[#a855f7] flex items-center justify-center">
                              <Sparkles className="w-4 h-4 text-white" />
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-bold text-github-text mb-1 font-sans flex items-center gap-1.5">
                          {currentTool === "github" ? (
                            <>🌿 <span className="text-[#f59e0b]">Octolyzer (GitHub Intelligence)</span></>
                          ) : currentTool === "codex" ? (
                            <>💻 <span className="text-[#10b981]">Synthex (Code Intelligence)</span></>
                          ) : (
                            <>✨ <span className="text-[#a855f7]">Nexus (General AI Assistant)</span></>
                          )}
                        </p>
                        <div className="flex items-center gap-2.5 text-sm text-github-muted font-sans">
                          <Loader2 className="w-4 h-4 animate-spin text-github-agent" />
                          <span className="text-github-agent font-medium animate-pulse">
                            {loaderStatuses[loaderIndex]}
                          </span>
                        </div>
                        <div className="mt-3 flex gap-1">
                          <div className="w-2 h-2 rounded-full bg-github-agent/60 animate-bounce" style={{animationDelay: '0ms'}} />
                          <div className="w-2 h-2 rounded-full bg-github-agent/60 animate-bounce" style={{animationDelay: '150ms'}} />
                          <div className="w-2 h-2 rounded-full bg-github-agent/60 animate-bounce" style={{animationDelay: '300ms'}} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* PDF Ingestion status indicator */}
            {uploadStatus && (
              <div className="max-w-2xl mx-auto w-full px-4 mb-1 select-none z-10">
                <div className="p-2 bg-github-panel border border-github-border rounded-lg flex items-center justify-between text-xs text-github-muted animate-fade-in font-sans">
                  <div className="flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-github-link" />
                    <span>{uploadStatus}</span>
                  </div>
                  <button 
                    onClick={() => setUploadStatus("")}
                    className="text-github-muted hover:text-github-text bg-transparent border-0 cursor-pointer text-xs font-bold font-sans"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}

            {/* CHATGPT STYLE PROMPT BAR FOOTER */}
            <div className="p-4 bg-github-bg border-t border-github-border select-none z-10">
              <div className="max-w-2xl mx-auto w-full">
                <form
                  onSubmit={handleSendMessage}
                  className="relative flex items-center bg-github-panel border border-github-border rounded-xl px-4 py-2.5 shadow-md focus-within:border-github-link focus-within:ring-1 focus-within:ring-github-link transition-all"
                >
                  {/* File Upload Trigger (+) */}
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploadLoading || chatLoading}
                    className="p-2 bg-gradient-to-br from-[#6366f1] to-[#a855f7] text-white hover:from-[#818cf8] hover:to-[#c084fc] rounded-lg cursor-pointer transition-all flex items-center justify-center shrink-0 shadow-md shadow-purple-500/20 disabled:opacity-40"
                    title="Upload PDF Document"
                  >
                    {uploadLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin text-github-agent" />
                    ) : (
                      <Plus className="w-4 h-4" />
                    )}
                  </button>

                  {/* Message Input textfield */}
                  <div className="flex-1 flex flex-col min-w-0">
                    {/* Attached file preview tag (ChatGPT style) */}
                    {attachedFile && (
                      <div className="flex items-center gap-2 bg-github-border/30 border border-github-border px-2.5 py-1 rounded-lg text-xs text-github-text w-fit mb-2 animate-fade-in font-sans">
                        <FileText className="w-3.5 h-3.5 text-github-link shrink-0" />
                        <span className="truncate max-w-[150px] font-semibold">{attachedFile.name}</span>
                        <button
                          type="button"
                          onClick={() => setAttachedFile(null)}
                          className="text-github-muted hover:text-github-error bg-transparent border-0 cursor-pointer p-0 text-xs font-bold font-sans ml-1"
                        >
                          ×
                        </button>
                      </div>
                    )}
                    <textarea
                      disabled={chatLoading}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          if (input.trim() && !chatLoading) {
                            handleSendMessage(e);
                          }
                        }
                      }}
                      placeholder={
                        currentTool === "github"
                          ? "Ask about repository structure or file details..."
                          : currentTool === "codex"
                          ? "Paste code file or request code refactors..."
                          : "Message ReActise..."
                      }
                      rows={Math.min(5, input.split('\n').length)}
                      className="w-full bg-transparent px-3 py-1.5 text-sm text-github-text placeholder-github-muted focus:outline-none font-sans resize-none max-h-32 overflow-y-auto"
                    />
                  </div>

                  {/* Send Arrow button */}
                  <button
                    type="submit"
                    disabled={chatLoading || !input.trim()}
                    className={`p-2 rounded-lg cursor-pointer transition-all shrink-0 flex items-center justify-center border-0 ${
                      input.trim() && !chatLoading
                        ? "bg-gradient-to-br from-[#6366f1] to-[#a855f7] text-white hover:from-[#818cf8] hover:to-[#c084fc] shadow-md shadow-purple-500/20"
                        : "bg-github-border/20 text-github-muted cursor-not-allowed"
                    }`}
                    title="Send message"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </form>

                {/* Disclaimer banner */}
                <p className="text-[10px] text-github-muted text-center mt-2 font-sans">
                  ReActise can make mistakes. Verify important code.
                </p>
              </div>
            </div>
          </main>
        </div>
      )}
    </div>
  );
}
