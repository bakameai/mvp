import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  organization?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role?: string;
  organization?: string;
}

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    return response.data;
  },

  async register(userData: RegisterData): Promise<User> {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  getSession(): { user: User | null; session: any | null } {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { user: null, session: null };
    }
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const user: User = {
        id: payload.user_id,
        email: payload.email,
        full_name: payload.full_name || '',
        role: payload.role,
        organization: payload.organization,
        is_active: true,
        created_at: new Date().toISOString()
      };
      return { user, session: { access_token: token } };
    } catch {
      return { user: null, session: null };
    }
  },

  onAuthStateChange(callback: (event: string, session: any) => void) {
    const checkAuth = () => {
      const { session } = this.getSession();
      callback(session ? 'SIGNED_IN' : 'SIGNED_OUT', session);
    };
    
    checkAuth();
    
    return {
      data: {
        subscription: {
          unsubscribe: () => {}
        }
      }
    };
  }
};

export const contentAPI = {
  async getPageContent(pageName: string): Promise<any> {
    const response = await api.get(`/api/content/${pageName}`);
    return response.data;
  },

  async updatePageContent(pageName: string, contentData: any): Promise<any> {
    const response = await api.put(`/api/content/${pageName}`, {
      page_name: pageName,
      content_data: contentData
    });
    return response.data;
  },

  async listAllContent(): Promise<any[]> {
    const response = await api.get('/api/content');
    return response.data;
  }
};

export const telephonyAPI = {
  async getStats(): Promise<any> {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  async getSessionHistory(): Promise<any[]> {
    const response = await api.get('/admin/sessions');
    return response.data;
  },

  async getUserAnalytics(): Promise<any> {
    const response = await api.get('/admin/analytics');
    return response.data;
  }
};

export const llamaAPI = {
  async speechToText(audioBase64: string): Promise<any> {
    const response = await api.post('/api/speech-to-text', {
      audio: audioBase64
    });
    return response.data;
  },

  async llamaChat(messages: any[], subject?: string): Promise<any> {
    const response = await api.post('/api/llama-chat', {
      messages,
      subject
    });
    return response.data;
  },

  async textToSpeech(text: string, voice: string = 'alloy'): Promise<any> {
    const response = await api.post('/api/text-to-speech', {
      text,
      voice
    });
    return response.data;
  },

  async realtimeSession(subject: string): Promise<any> {
    const response = await api.post('/api/realtime-session', {
      subject
    });
    return response.data;
  }
};

export const rateLimitAPI = {
  async checkRateLimit(action: string, limit: number = 5): Promise<boolean> {
    try {
      const response = await api.post('/api/rate-limit-check', {
        action,
        limit
      });
      return response.data.allowed || false;
    } catch {
      return false;
    }
  }
};

export const adminAPI = {
  async getAdminStats(): Promise<any> {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  async getOrganizations(): Promise<any[]> {
    const response = await api.get('/admin/organizations');
    return response.data;
  },

  async createOrganization(orgData: any): Promise<any> {
    const response = await api.post('/admin/organizations', orgData);
    return response.data;
  },

  async deleteOrganization(id: string): Promise<void> {
    await api.delete(`/admin/organizations/${id}`);
  },

  async updatePassword(oldPassword: string, newPassword: string): Promise<void> {
    await api.put('/auth/password', { old_password: oldPassword, new_password: newPassword });
  }
};

Object.assign(authAPI, {
  async transcribeAudio(audioBase64: string): Promise<any> {
    return await llamaAPI.speechToText(audioBase64);
  },

  async getLlamaResponse(messages: any[], subject?: string): Promise<any> {
    return await llamaAPI.llamaChat(messages, subject);
  },

  async generateSpeech(text: string, voice: string = 'alloy'): Promise<any> {
    return await llamaAPI.textToSpeech(text, voice);
  },

  async getAdminStats(): Promise<any> {
    return await adminAPI.getAdminStats();
  },

  async getOrganizations(): Promise<any[]> {
    return await adminAPI.getOrganizations();
  },

  async createOrganization(orgData: any): Promise<any> {
    return await adminAPI.createOrganization(orgData);
  },

  async deleteOrganization(id: string): Promise<void> {
    return await adminAPI.deleteOrganization(id);
  },

  async updateProfile(profileData: any): Promise<any> {
    const response = await api.put('/auth/profile', profileData);
    return response.data;
  },

  async sendIVRMessage(messageData: any): Promise<any> {
    const response = await api.post('/api/ivr/message', messageData);
    return response.data;
  }
});

export default api;
