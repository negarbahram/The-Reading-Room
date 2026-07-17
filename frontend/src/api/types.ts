export type Role = 'ADMIN' | 'MEMBER';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_suspended: boolean;
  phone_number: string;
  date_joined: string;
}

export interface AdminUser extends User {
  is_active: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Author {
  id: number;
  name: string;
  bio: string;
}

export interface Genre {
  id: number;
  name: string;
}

export type CopyStatus = 'AVAILABLE' | 'ON_LOAN' | 'HELD' | 'LOST' | 'DAMAGED' | 'ARCHIVED';

export interface BookCopy {
  id: number;
  book: number;
  barcode: string;
  status: CopyStatus;
  shelf_location: string;
  acquired_at: string;
  notes: string;
}

export interface Book {
  id: number;
  title: string;
  author: number;
  author_name: string;
  genre: number;
  genre_name: string;
  publication_year: number;
  cover_url: string;
  language: string;
  is_archived: boolean;
  available_copies: number;
  total_copies: number;
  average_rating: number | null;
}

export interface BookDetail extends Book {
  isbn: string | null;
  publisher: string;
  description: string;
  shelf_location: string;
  copies: BookCopy[];
}

export interface RecommendedBook extends Book {
  reason: string;
}

export type LoanRequestStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
export type LoanStatus = 'ACTIVE' | 'OVERDUE' | 'RETURNED' | 'LOST';
export type ReservationStatus = 'WAITING' | 'READY' | 'FULFILLED' | 'EXPIRED' | 'CANCELLED';
export type FineStatus = 'UNPAID' | 'PENDING_PAYMENT' | 'PAID' | 'WAIVED';
export type PaymentStatus = 'PENDING' | 'SUCCEEDED' | 'FAILED' | 'CANCELLED';

export interface LoanRequest {
  id: number;
  member: number;
  member_email: string;
  book: number;
  book_detail: Book;
  status: LoanRequestStatus;
  requested_at: string;
  decided_at: string | null;
  decision_reason: string;
}

export interface Loan {
  id: number;
  member: number;
  member_email: string;
  book: number;
  book_detail: Book;
  copy: number;
  copy_barcode: string;
  status: LoanStatus;
  borrowed_at: string;
  due_at: string;
  returned_at: string | null;
  is_overdue: boolean;
}

export interface Reservation {
  id: number;
  member: number;
  member_email: string;
  book: number;
  book_detail: Book;
  status: ReservationStatus;
  created_at: string;
  ready_at: string | null;
  expires_at: string | null;
}

export interface Fine {
  id: number;
  member: number;
  member_email: string;
  loan: number;
  book_title: string;
  amount: string;
  status: FineStatus;
  reason: string;
  created_at: string;
  resolved_at: string | null;
  waived_reason: string;
}

export interface PaymentEvent {
  id: number;
  event_type: string;
  detail: string;
  created_at: string;
}

export interface Payment {
  id: number;
  member: number;
  fine: number;
  fine_reason: string;
  amount: string;
  status: PaymentStatus;
  session_id: string;
  created_at: string;
  updated_at: string;
  events: PaymentEvent[];
}

export interface Review {
  id: number;
  member: number;
  member_email: string;
  book: number;
  rating: number;
  comment: string;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface AppNotification {
  id: number;
  event_type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationPreference {
  email_enabled: boolean;
  sms_enabled: boolean;
  in_app_enabled: boolean;
}

export interface MemberInterest {
  id: number;
  genre: number | null;
  author: number | null;
  genre_name: string | null;
  author_name: string | null;
}

export interface MemberSummary {
  active_loans: number;
  overdue_loans: number;
  returned_loans: number;
  pending_requests: number;
  active_reservations: number;
  outstanding_fines_total: string | number;
  unread_notifications: number;
}

export interface AdminKPIs {
  total_books: number;
  total_copies: number;
  available_copies: number;
  loaned_books: number;
  overdue_loans: number;
  pending_requests: number;
  active_reservations: number;
  total_members: number;
  outstanding_fines_total: string | number;
}
