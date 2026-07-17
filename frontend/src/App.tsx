import { Route, Routes, useLocation } from 'react-router-dom';
import { Layout } from './components/Layout';
import { AdminLayout } from './components/AdminLayout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { RequireAuth } from './auth/RequireAuth';

import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Catalog from './pages/Catalog';
import BookDetail from './pages/BookDetail';
import MemberDashboard from './pages/MemberDashboard';
import MyLoans from './pages/MyLoans';
import Reservations from './pages/Reservations';
import Fines from './pages/Fines';
import PaymentCheckout from './pages/PaymentCheckout';
import PaymentResult from './pages/PaymentResult';
import PaymentReceipt from './pages/PaymentReceipt';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';

import AdminDashboard from './pages/admin/AdminDashboard';
import AdminBooks from './pages/admin/AdminBooks';
import AdminBookEditor from './pages/admin/AdminBookEditor';
import AdminMembers from './pages/admin/AdminMembers';
import AdminLoanRequests from './pages/admin/AdminLoanRequests';
import AdminLoans from './pages/admin/AdminLoans';
import AdminReservations from './pages/admin/AdminReservations';
import AdminFines from './pages/admin/AdminFines';
import AdminReviewModeration from './pages/admin/AdminReviewModeration';
import AdminReports from './pages/admin/AdminReports';

function NotFound() {
  return <div className="text-center py-24 font-serif text-2xl">Page not found</div>;
}

function App() {
  const location = useLocation();
  return (
    <Layout>
      <ErrorBoundary key={location.pathname}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/catalog/:id" element={<BookDetail />} />

          <Route path="/dashboard" element={<RequireAuth><MemberDashboard /></RequireAuth>} />
          <Route path="/loans" element={<RequireAuth><MyLoans /></RequireAuth>} />
          <Route path="/reservations" element={<RequireAuth><Reservations /></RequireAuth>} />
          <Route path="/fines" element={<RequireAuth><Fines /></RequireAuth>} />
          <Route path="/pay/:fineId" element={<RequireAuth><PaymentCheckout /></RequireAuth>} />
          <Route path="/pay/result/:paymentId" element={<RequireAuth><PaymentResult /></RequireAuth>} />
          <Route path="/pay/receipt/:paymentId" element={<RequireAuth><PaymentReceipt /></RequireAuth>} />
          <Route path="/notifications" element={<RequireAuth><Notifications /></RequireAuth>} />
          <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />

          <Route path="/admin" element={<RequireAuth adminOnly><AdminLayout><AdminDashboard /></AdminLayout></RequireAuth>} />
          <Route path="/admin/books" element={<RequireAuth adminOnly><AdminLayout><AdminBooks /></AdminLayout></RequireAuth>} />
          <Route path="/admin/books/new" element={<RequireAuth adminOnly><AdminLayout><AdminBookEditor /></AdminLayout></RequireAuth>} />
          <Route path="/admin/books/:id" element={<RequireAuth adminOnly><AdminLayout><AdminBookEditor /></AdminLayout></RequireAuth>} />
          <Route path="/admin/members" element={<RequireAuth adminOnly><AdminLayout><AdminMembers /></AdminLayout></RequireAuth>} />
          <Route path="/admin/loan-requests" element={<RequireAuth adminOnly><AdminLayout><AdminLoanRequests /></AdminLayout></RequireAuth>} />
          <Route path="/admin/loans" element={<RequireAuth adminOnly><AdminLayout><AdminLoans /></AdminLayout></RequireAuth>} />
          <Route path="/admin/reservations" element={<RequireAuth adminOnly><AdminLayout><AdminReservations /></AdminLayout></RequireAuth>} />
          <Route path="/admin/fines" element={<RequireAuth adminOnly><AdminLayout><AdminFines /></AdminLayout></RequireAuth>} />
          <Route path="/admin/reviews" element={<RequireAuth adminOnly><AdminLayout><AdminReviewModeration /></AdminLayout></RequireAuth>} />
          <Route path="/admin/reports" element={<RequireAuth adminOnly><AdminLayout><AdminReports /></AdminLayout></RequireAuth>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </ErrorBoundary>
    </Layout>
  );
}

export default App;
