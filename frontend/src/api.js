/**
 * API client for Library Management System backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Books API
export const searchBooks = async (query) => {
  const response = await api.get('/books/search', { params: { q: query } });
  return response.data;
};

// Borrowers API
export const createBorrower = async (borrowerData) => {
  const response = await api.post('/borrowers', borrowerData);
  return response.data;
};

// Loans API
export const checkoutBook = async (isbn, cardId) => {
  const response = await api.post('/loans/checkout', { isbn, card_id: cardId });
  return response.data;
};

export const getOpenLoans = async (filters = {}) => {
  const response = await api.get('/loans/open', { params: filters });
  return response.data;
};

export const checkinBook = async (loanId) => {
  const response = await api.post('/loans/checkin', { loan_id: loanId });
  return response.data;
};

// Fines API
export const updateFines = async () => {
  const response = await api.post('/fines/update');
  return response.data;
};

export const getFinesSummary = async (unpaidOnly = true, cardId = null) => {
  const params = { unpaid_only: unpaidOnly };
  if (cardId) {
    params.card_id = cardId;
  }
  const response = await api.get('/fines/summary', { params });
  return response.data;
};

export const payFines = async (cardId) => {
  const response = await api.post('/fines/pay', { card_id: cardId });
  return response.data;
};

export default api;



