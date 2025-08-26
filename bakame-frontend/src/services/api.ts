import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('API Base URL:', API_BASE_URL, 'Environment:', import.meta.env.VITE_API_URL);

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
      
      const currentTime = Math.floor(Date.now() / 1000);
      if (payload.exp && payload.exp < currentTime) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return { user: null, session: null };
      }
      
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
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
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
  },


  async sendIVRMessage(messageData: any): Promise<any> {
    const response = await api.post('/api/ivr/message', messageData);
    return response.data;
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

  async getIVRStats(): Promise<any> {
    const response = await api.get('/admin/ivr-stats');
    return response.data;
  },

  async getUserSessions(phoneNumber?: string, limit: number = 100): Promise<any[]> {
    const params = new URLSearchParams();
    if (phoneNumber) params.append('phone_number', phoneNumber);
    params.append('limit', limit.toString());
    const response = await api.get(`/admin/sessions?${params.toString()}`);
    return response.data;
  },

  async getUsers(): Promise<any[]> {
    const response = await api.get('/admin/users');
    return response.data;
  },

  async updateUserRole(userId: string, role: string): Promise<void> {
    await api.put(`/admin/users/${userId}/role`, { role });
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
  },

  async getNewsletterSubscriptions(): Promise<any[]> {
    const response = await api.get('/admin/newsletter/subscriptions');
    return response.data;
  },

  async getNewsletterCampaigns(): Promise<any[]> {
    const response = await api.get('/admin/newsletter/campaigns');
    return response.data;
  },

  async createNewsletterCampaign(campaignData: any): Promise<any> {
    const response = await api.post('/admin/newsletter/campaigns', campaignData);
    return response.data;
  },

  async sendNewsletterCampaign(campaignId: string): Promise<any> {
    const response = await api.post(`/admin/newsletter/campaigns/${campaignId}/send`);
    return response.data;
  },

  async createUser(userData: any): Promise<any> {
    const response = await api.post('/admin/users', userData);
    return response.data;
  },

  async updateUser(userId: string, userData: any): Promise<any> {
    const response = await api.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  async deleteUser(userId: string): Promise<void> {
    await api.delete(`/admin/users/${userId}`);
  },

  async getAnalytics(): Promise<any> {
    const response = await api.get('/admin/analytics');
    return response.data;
  },

  async getContentPages(): Promise<any[]> {
    const response = await api.get('/admin/content/pages');
    return response.data;
  },

  async updateContent(pageName: string, content: string): Promise<any> {
    const response = await api.put(`/admin/content/${pageName}`, { content });
    return response.data;
  },

  async getAuditLogs(): Promise<any[]> {
    const response = await api.get('/admin/audit-logs');
    return response.data;
  },

  async getBackups(): Promise<any[]> {
    const response = await api.get('/admin/backups');
    return response.data;
  },

  async createBackup(type: string): Promise<any> {
    const response = await api.post('/admin/backups', { type });
    return response.data;
  },

  async downloadBackup(backupId: string): Promise<Blob> {
    const response = await api.get(`/admin/backups/${backupId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async restoreBackup(backupId: string): Promise<any> {
    const response = await api.post(`/admin/backups/${backupId}/restore`);
    return response.data;
  },

  async getSystemNotifications(): Promise<any[]> {
    const response = await api.get('/admin/notifications');
    return response.data;
  },

  async markNotificationRead(notificationId: string): Promise<any> {
    const response = await api.put(`/admin/notifications/${notificationId}/read`);
    return response.data;
  },

  async dismissNotification(notificationId: string): Promise<void> {
    await api.delete(`/admin/notifications/${notificationId}`);
  },

  async getNotificationSettings(): Promise<any> {
    const response = await api.get('/admin/notification-settings');
    return response.data;
  },

  async updateNotificationSettings(settings: any): Promise<any> {
    const response = await api.put('/admin/notification-settings', settings);
    return response.data;
  },

  async getMediaFiles(): Promise<any[]> {
    const response = await api.get('/admin/media');
    return response.data;
  },

  async uploadMediaFile(formData: FormData): Promise<any> {
    const response = await api.post('/admin/media', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteMediaFile(fileId: string): Promise<void> {
    await api.delete(`/admin/media/${fileId}`);
  },

  async getAPIKeys(): Promise<any[]> {
    const response = await api.get('/admin/api-keys');
    return response.data;
  },

  async createAPIKey(keyData: any): Promise<any> {
    const response = await api.post('/admin/api-keys', keyData);
    return response.data;
  },

  async toggleAPIKey(keyId: string, isActive: boolean): Promise<any> {
    const response = await api.put(`/admin/api-keys/${keyId}/toggle`, { is_active: isActive });
    return response.data;
  },

  async deleteAPIKey(keyId: string): Promise<void> {
    await api.delete(`/admin/api-keys/${keyId}`);
  },

  async getWebhooks(): Promise<any[]> {
    const response = await api.get('/admin/webhooks');
    return response.data;
  },

  async createWebhook(webhookData: any): Promise<any> {
    const response = await api.post('/admin/webhooks', webhookData);
    return response.data;
  },

  async getSystemMetrics(): Promise<any> {
    const response = await api.get('/admin/system/metrics');
    return response.data;
  },

  async getHealthChecks(): Promise<any[]> {
    const response = await api.get('/admin/system/health');
    return response.data;
  },

  async updateProfile(profileData: any): Promise<any> {
    const response = await api.put('/admin/profile', profileData);
    return response.data;
  },

  async createDepartment(orgId: string, data: any): Promise<any> {
    const response = await api.post(`/admin/organizations/${orgId}/departments`, data);
    return response.data;
  },

  async updateDepartment(orgId: string, deptId: string, data: any): Promise<any> {
    const response = await api.put(`/admin/organizations/${orgId}/departments/${deptId}`, data);
    return response.data;
  },

  async deleteDepartment(orgId: string, deptId: string): Promise<void> {
    await api.delete(`/admin/organizations/${orgId}/departments/${deptId}`);
  },

  async updateOrganizationPermissions(orgId: string, permissions: any): Promise<any> {
    const response = await api.put(`/admin/organizations/${orgId}/permissions`, { permissions });
    return response.data;
  },

  async getTeamMembers(): Promise<any[]> {
    const response = await api.get('/admin/team/members');
    return response.data;
  },

  async getTeamInvitations(): Promise<any[]> {
    const response = await api.get('/admin/team/invitations');
    return response.data;
  },

  async sendTeamInvitation(data: any): Promise<any> {
    const response = await api.post('/admin/team/invitations', data);
    return response.data;
  },

  async resendTeamInvitation(invitationId: string): Promise<any> {
    const response = await api.post(`/admin/team/invitations/${invitationId}/resend`);
    return response.data;
  },

  async revokeTeamInvitation(invitationId: string): Promise<void> {
    await api.delete(`/admin/team/invitations/${invitationId}`);
  },

  async updateTeamMemberRole(memberId: string, role: string): Promise<any> {
    const response = await api.put(`/admin/team/members/${memberId}/role`, { role });
    return response.data;
  },

  async deactivateTeamMember(memberId: string): Promise<any> {
    const response = await api.put(`/admin/team/members/${memberId}/deactivate`);
    return response.data;
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

  async getUsers(): Promise<any[]> {
    return await adminAPI.getUsers();
  },

  async updateUserRole(userId: string, role: string): Promise<void> {
    return await adminAPI.updateUserRole(userId, role);
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
  }
});

export default api;
