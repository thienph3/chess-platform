import { useCallback, useState } from "react";

import { Chess } from "chess.js";

import apiClient from "@/api/client";

export type GameType = "chess" | "xiangqi" | "go" | "gomoku";
export type Difficulty = "easy" | "medium" | "hard";
export type ColorChoice = "white" | "black" | "random";

interface PlayAIState {
  fen: string;
  gameOver: boolean;
  result: string | null;
  playerColor: string;
  roomId: string | null;
}

function uciToSan(fen: string, uci: string, gameType: GameType): string {
  if (gameType !== "chess" || !uci || uci.length < 4) return uci;
  try {
    const chess = new Chess(fen);
    const m = chess.move({ from: uci.slice(0, 2), to: uci.slice(2, 4), promotion: uci[4] || undefined });
    return m ? m.san : uci;
  } catch {
    return uci;
  }
}

export function usePlayAI(gameType: GameType, difficulty: Difficulty) {
  const [state, setState] = useState<PlayAIState>({
    fen: "", gameOver: false, result: null, playerColor: "white", roomId: null,
  });
  const [isThinking, setIsThinking] = useState(false);
  const [started, setStarted] = useState(false);
  const [moves, setMoves] = useState<string[]>([]);

  const startGame = useCallback(async (colorChoice: ColorChoice = "white", timeControl = 600, increment = 0) => {
    setMoves([]);
    try {
      const res = await apiClient.post("/games/ai/start", {
        game_type: gameType, difficulty, time_control: timeControl, increment, player_color: colorChoice,
      });
      const d = res.data?.data || res.data;
      setState({ fen: d.fen, gameOver: false, result: null, playerColor: d.player_color, roomId: d.room_id });
      if (d.ai_first_move) {
        const startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
        setMoves([uciToSan(startFen, d.ai_first_move, gameType)]);
      }
      setStarted(true);
    } catch {
      setState({ fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        gameOver: false, result: null, playerColor: "white", roomId: null });
      setStarted(true);
    }
  }, [gameType, difficulty]);

  const makeMove = useCallback(async (move: Record<string, unknown>) => {
    if (!state.roomId || state.gameOver) return false;
    const currentFen = state.fen;

    setIsThinking(true);
    try {
      const res = await apiClient.post("/games/ai/play", { room_id: state.roomId, move });
      const d = res.data?.data || res.data;
      if (!d.valid) { setIsThinking(false); return false; }

      // Player move → SAN
      const playerSan = uciToSan(currentFen, d.player_move_san, gameType);
      const newMoves = [playerSan];

      // AI move → SAN (need intermediate FEN after player move)
      if (d.ai_move && d.new_fen !== d.ai_fen) {
        // d.new_fen is after player move but before AI (backend returns ai_fen as final)
        // Actually backend returns new_fen = ai_fen (final state)
        // We need FEN after player move to convert AI UCI → SAN
        const intermediateChess = new Chess(currentFen);
        intermediateChess.move({ from: move.from as string, to: move.to as string, promotion: (move.promotion as string) || undefined });
        const aiSan = uciToSan(intermediateChess.fen(), d.ai_move, gameType);
        newMoves.push(aiSan);
      } else if (d.ai_move) {
        newMoves.push(d.ai_move);
      }

      setMoves((prev) => [...prev, ...newMoves]);
      setState((prev) => ({
        ...prev, fen: d.ai_fen || d.new_fen, gameOver: d.game_over || false, result: d.result || null,
      }));
    } catch {
      // ignore
    }
    setIsThinking(false);
    return true;
  }, [state.roomId, state.fen, state.gameOver, gameType]);

  const endGame = useCallback(async (result: string) => {
    if (state.roomId) {
      try { await apiClient.post("/games/ai/resign", null, { params: { room_id: state.roomId } }); } catch { /* */ }
    }
    setState((prev) => ({ ...prev, gameOver: true, result }));
  }, [state.roomId]);

  return { state, isThinking, started, startGame, makeMove, endGame, moves };
}
