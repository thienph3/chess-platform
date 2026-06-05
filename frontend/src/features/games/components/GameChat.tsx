import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { RefObject, useCallback, useEffect, useRef, useState } from "react";

interface IChatMessage {
  message: string;
  sender: string;
}

interface GameChatProps {
  wsRef: RefObject<WebSocket | null>;
  disabled: boolean;
}

function GameChat({ wsRef, disabled }: GameChatProps) {
  const [messages, setMessages] = useState<IChatMessage[]>([]);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = wsRef.current;
    if (!ws) return;

    const handleMessage = (event: MessageEvent) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "chat") {
        setMessages((prev) => [...prev, { message: msg.message, sender: msg.sender }]);
      }
    };

    ws.addEventListener("message", handleMessage);
    return () => { ws.removeEventListener("message", handleMessage); };
  }, [wsRef]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({ type: "chat", message: text }));
    setInput("");
  }, [input, wsRef]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper variant="outlined" sx={{ p: 1.5 }}>
      <Typography variant="subtitle2" fontWeight={600} mb={1}>
        Chat
      </Typography>
      <Box ref={listRef} sx={{ maxHeight: 200, overflow: "auto", mb: 1 }}>
        {messages.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Chưa có tin nhắn
          </Typography>
        ) : (
          <Stack spacing={0.5}>
            {messages.map((msg, i) => (
              <Typography key={i} variant="body2">
                <strong>{msg.sender}:</strong> {msg.message}
              </Typography>
            ))}
          </Stack>
        )}
      </Box>
      <Stack direction="row" spacing={1}>
        <TextField
          size="small"
          fullWidth
          placeholder="Nhập tin nhắn..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-label="Nhập tin nhắn"
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          aria-label="Gửi tin nhắn"
        >
          <SendIcon />
        </IconButton>
      </Stack>
    </Paper>
  );
}

export default GameChat;
