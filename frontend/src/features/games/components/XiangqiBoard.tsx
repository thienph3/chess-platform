/**
 * Xiangqi board wrapper sử dụng react-xiangqiboard package.
 * API tương tự react-chessboard v4: position (FEN), onPieceDrop, arePiecesDraggable.
 */
import { Chessboard } from "react-xiangqiboard";

interface XiangqiBoardProps {
  position: string; // Xiangqi FEN
  onMove?: (from: string, to: string) => boolean;
  allowDragging?: boolean;
}

// FEN khởi đầu cờ tướng
const INITIAL_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1";

function XiangqiBoard({ position, onMove, allowDragging = true }: XiangqiBoardProps) {
  const fen = position || INITIAL_FEN;

  const handleDrop = (sourceSquare: string, targetSquare: string) => {
    if (onMove) return onMove(sourceSquare, targetSquare);
    return true;
  };

  return (
    <Chessboard
      position={fen}
      onPieceDrop={handleDrop}
      arePiecesDraggable={allowDragging}
      boardWidth={480}
    />
  );
}

export default XiangqiBoard;
