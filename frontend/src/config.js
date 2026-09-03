// Centralized API Configuration for Local and Cloud Deployments
// In production (e.g. Vercel), set VITE_API_BASE_URL to your deployed backend URL (e.g. https://logvista-backend.onrender.com)
// In local development, it defaults to http://127.0.0.1:5000 if not provided.
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000').replace(/\/+$/, '');
