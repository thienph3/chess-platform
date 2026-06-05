import FormatBoldIcon from "@mui/icons-material/FormatBold";
import FormatItalicIcon from "@mui/icons-material/FormatItalic";
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted";
import FormatListNumberedIcon from "@mui/icons-material/FormatListNumbered";
import FormatUnderlinedIcon from "@mui/icons-material/FormatUnderlined";
import TitleIcon from "@mui/icons-material/Title";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import { useCallback, useRef } from "react";

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  placeholder?: string;
  minHeight?: number;
}

function RichTextEditor({ value, onChange, placeholder = "Nhập nội dung...", minHeight = 200 }: RichTextEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);

  const execCommand = useCallback((command: string, value?: string) => {
    document.execCommand(command, false, value);
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  }, [onChange]);

  const handleInput = useCallback(() => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  }, [onChange]);

  return (
    <Box sx={{ border: 1, borderColor: "divider", borderRadius: 1, overflow: "hidden" }}>
      <Stack direction="row" spacing={0.5} sx={{ p: 0.5, borderBottom: 1, borderColor: "divider", bgcolor: "grey.50" }}>
        <IconButton size="small" onClick={() => execCommand("bold")} aria-label="In đậm">
          <FormatBoldIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand("italic")} aria-label="In nghiêng">
          <FormatItalicIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand("underline")} aria-label="Gạch chân">
          <FormatUnderlinedIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand("formatBlock", "h3")} aria-label="Tiêu đề">
          <TitleIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand("insertUnorderedList")} aria-label="Danh sách">
          <FormatListBulletedIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand("insertOrderedList")} aria-label="Danh sách số">
          <FormatListNumberedIcon fontSize="small" />
        </IconButton>
      </Stack>
      <Box
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        onInput={handleInput}
        dangerouslySetInnerHTML={{ __html: value }}
        sx={{
          p: 2, minHeight, outline: "none", fontSize: "0.875rem", lineHeight: 1.6,
          "& h3": { fontSize: "1.1rem", fontWeight: 600, mt: 1, mb: 0.5 },
          "& ul, & ol": { pl: 3 },
          "&:empty::before": { content: `"${placeholder}"`, color: "text.disabled" },
        }}
      />
    </Box>
  );
}

export default RichTextEditor;
