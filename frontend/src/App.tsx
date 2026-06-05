import Box from "@mui/material/Box";
import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

const LoginPage = lazy(() => import("./features/auth/pages/LoginPage"));
const RegisterPage = lazy(() => import("./features/auth/pages/RegisterPage"));
const ForgotPasswordPage = lazy(() => import("./features/auth/pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./features/auth/pages/ResetPasswordPage"));
const DashboardPage = lazy(() => import("./features/dashboard/pages/DashboardPage"));
const MembersPage = lazy(() => import("./features/members/pages/MembersPage"));
const MemberDetailPage = lazy(() => import("./features/members/pages/MemberDetailPage"));
const MemberStatsPage = lazy(() => import("./features/members/pages/MemberStatsPage"));
const TournamentsPage = lazy(() => import("./features/tournaments/pages/TournamentsPage"));
const TournamentDetailPage = lazy(() => import("./features/tournaments/pages/TournamentDetailPage"));
const TournamentCalendarPage = lazy(() => import("./features/tournaments/pages/TournamentCalendarPage"));
const LeaderboardPage = lazy(() => import("./features/ratings/pages/LeaderboardPage"));
const FinancePage = lazy(() => import("./features/finance/pages/FinancePage"));
const GameLobbyPage = lazy(() => import("./features/games/pages/GameLobbyPage"));
const GamePlayPage = lazy(() => import("./features/games/pages/GamePlayPage"));
const PlayAIPage = lazy(() => import("./features/games/pages/PlayAIPage"));
const SpectatorPage = lazy(() => import("./features/games/pages/SpectatorPage"));
const GameHistoryPage = lazy(() => import("./features/games/pages/GameHistoryPage"));
const GameReplayPage = lazy(() => import("./features/games/pages/GameReplayPage"));
const OpeningExplorerPage = lazy(() => import("./features/games/pages/OpeningExplorerPage"));
const AttendancePage = lazy(() => import("./features/attendance/pages/AttendancePage"));
const AchievementsPage = lazy(() => import("./features/achievements/pages/AchievementsPage"));
const AdminPage = lazy(() => import("./features/admin/pages/AdminPage"));
const TrainingPage = lazy(() => import("./features/training/pages/TrainingPage"));
const NewsPage = lazy(() => import("./features/news/pages/NewsPage"));
const GalleryPage = lazy(() => import("./features/gallery/pages/GalleryPage"));

const PageFallback = () => <Box p={3} />;

function LazyPage({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageFallback />}>{children}</Suspense>
    </ErrorBoundary>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LazyPage><LoginPage /></LazyPage>} />
      <Route path="/register" element={<LazyPage><RegisterPage /></LazyPage>} />
      <Route path="/forgot-password" element={<LazyPage><ForgotPasswordPage /></LazyPage>} />
      <Route path="/reset-password" element={<LazyPage><ResetPasswordPage /></LazyPage>} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Layout />}>
          <Route index element={<LazyPage><DashboardPage /></LazyPage>} />
          <Route path="members" element={<LazyPage><MembersPage /></LazyPage>} />
          <Route path="members/:id" element={<LazyPage><MemberDetailPage /></LazyPage>} />
          <Route path="members/:id/stats" element={<LazyPage><MemberStatsPage /></LazyPage>} />
          <Route path="tournaments" element={<LazyPage><TournamentsPage /></LazyPage>} />
          <Route path="tournaments/calendar" element={<LazyPage><TournamentCalendarPage /></LazyPage>} />
          <Route path="tournaments/:id" element={<LazyPage><TournamentDetailPage /></LazyPage>} />
          <Route path="ratings" element={<LazyPage><LeaderboardPage /></LazyPage>} />
          <Route path="finance" element={<LazyPage><FinancePage /></LazyPage>} />
          <Route path="play" element={<LazyPage><GameLobbyPage /></LazyPage>} />
          <Route path="play/ai" element={<LazyPage><PlayAIPage /></LazyPage>} />
          <Route path="play/history" element={<LazyPage><GameHistoryPage /></LazyPage>} />
          <Route path="play/:id" element={<LazyPage><GamePlayPage /></LazyPage>} />
          <Route path="play/:id/watch" element={<LazyPage><SpectatorPage /></LazyPage>} />
          <Route path="play/:id/replay" element={<LazyPage><GameReplayPage /></LazyPage>} />
          <Route path="openings" element={<LazyPage><OpeningExplorerPage /></LazyPage>} />
          <Route path="attendance" element={<LazyPage><AttendancePage /></LazyPage>} />
          <Route path="achievements" element={<LazyPage><AchievementsPage /></LazyPage>} />
          <Route path="admin" element={<LazyPage><AdminPage /></LazyPage>} />
          <Route path="training" element={<LazyPage><TrainingPage /></LazyPage>} />
          <Route path="news" element={<LazyPage><NewsPage /></LazyPage>} />
          <Route path="gallery" element={<LazyPage><GalleryPage /></LazyPage>} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
