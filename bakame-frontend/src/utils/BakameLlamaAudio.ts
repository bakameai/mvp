import { authAPI } from '@/services/api';

export interface BakameSession {
  subject: string;
  startTime: Date;
  endTime?: Date;
  interactions: number;
  status: 'active' | 'ended';
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }>;
}

export class BakameLlamaChat {
  private session: BakameSession | null = null;
  private sessionCheckInterval: NodeJS.Timeout | null = null;
  private isRecording = false;
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;

  constructor(
    private onMessage: (message: any) => void,
    private onSessionUpdate: (session: BakameSession) => void,
    private onSpeakingChange: (speaking: boolean) => void
  ) {}

  async init(subject: string) {
    try {
      // Create new session
      this.session = {
        subject,
        startTime: new Date(),
        interactions: 0,
        status: 'active',
        messages: []
      };

      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      // Start session monitoring
      this.startSessionMonitoring();

      // Send initial greeting
      await this.sendWelcomeMessage(subject);

      console.log("Bakame Llama chat initialized successfully");

    } catch (error) {
      console.error("Error initializing Bakame Llama chat:", error);
      throw error;
    }
  }

  private async sendWelcomeMessage(subject: string) {
    const welcomeMessages = {
      english: "Hello! I'm Bakame, your English tutor powered by Llama AI. I'm here to help you improve your English skills. What would you like to work on today?",
      math: "Welcome! I'm Bakame, your Math tutor powered by Llama AI. I'm excited to help you with mathematics. What math topic can we explore together?", 
      reading: "Hi there! I'm Bakame, your Reading tutor powered by Llama AI. I'm here to help you become a better reader. Would you like to read something together or discuss a book?",
      debate: "Greetings! I'm Bakame, your Debate coach powered by Llama AI. I'll help you develop your argumentation and critical thinking skills. What topic interests you for discussion?"
    };

    const message = welcomeMessages[subject as keyof typeof welcomeMessages] || welcomeMessages.english;
    await this.speakText(message);
    
    if (this.session) {
      this.session.messages.push({
        role: 'assistant',
        content: message,
        timestamp: new Date()
      });
      this.onSessionUpdate(this.session);
    }
  }

  async startListening() {
    if (!this.stream || this.isRecording) return;

    try {
      this.isRecording = true;
      const chunks: Blob[] = [];

      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        await this.processAudio(audioBlob);
      };

      this.mediaRecorder.start();
      this.onMessage({ type: 'listening_started' });

      // Auto-stop after 30 seconds
      setTimeout(() => {
        if (this.isRecording) {
          this.stopListening();
        }
      }, 30000);

    } catch (error) {
      console.error('Error starting recording:', error);
      this.isRecording = false;
    }
  }

  stopListening() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.onMessage({ type: 'listening_stopped' });
    }
  }

  private async processAudio(audioBlob: Blob) {
    try {
      // Convert audio to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      // Transcribe using Whisper via FastAPI backend
      const transcriptionData = await authAPI.transcribeAudio(base64Audio);

      if (!transcriptionData?.text) {
        throw new Error('Failed to transcribe audio');
      }

      const userText = transcriptionData.text.trim();
      if (!userText) return;

      console.log('User said:', userText);

      // Add user message to session
      if (this.session) {
        this.session.messages.push({
          role: 'user',
          content: userText,
          timestamp: new Date()
        });
        this.onMessage({ 
          type: 'user_message',
          content: userText
        });
      }

      // Get AI response using Llama
      await this.getAIResponse(userText);

    } catch (error) {
      console.error('Error processing audio:', error);
      this.onMessage({ 
        type: 'error',
        content: 'Sorry, I had trouble understanding that. Please try again.'
      });
    }
  }

  private async getAIResponse(userText: string) {
    try {
      if (!this.session) return;

      // Prepare conversation history for Llama
      const messages = this.session.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Get response from Llama via FastAPI backend
      const llamaData = await authAPI.getLlamaResponse(messages, this.session.subject);

      if (!llamaData?.response) {
        throw new Error('Failed to get AI response');
      }

      const aiResponse = llamaData.response;
      console.log('Bakame AI response:', aiResponse);

      // Add AI message to session
      this.session.messages.push({
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      });

      this.session.interactions++;
      this.onSessionUpdate(this.session);

      this.onMessage({
        type: 'ai_message',
        content: aiResponse
      });

      // Convert AI response to speech
      await this.speakText(aiResponse);

    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage = "I'm sorry, I'm having trouble right now. Please try again.";
      this.onMessage({
        type: 'ai_message', 
        content: errorMessage
      });
      await this.speakText(errorMessage);
    }
  }

  private async speakText(text: string) {
    try {
      this.onSpeakingChange(true);

      const ttsData = await authAPI.generateSpeech(text, 'alloy');

      if (!ttsData?.audioContent) {
        throw new Error('Failed to generate speech');
      }

      // Play the audio
      const audio = new Audio(`data:audio/mp3;base64,${ttsData.audioContent}`);
      
      audio.onended = () => {
        this.onSpeakingChange(false);
      };

      audio.onerror = () => {
        this.onSpeakingChange(false);
      };

      await audio.play();

    } catch (error) {
      console.error('Error playing speech:', error);
      this.onSpeakingChange(false);
    }
  }

  private startSessionMonitoring() {
    // Check for subject switching every 3 interactions
    this.sessionCheckInterval = setInterval(() => {
      if (this.session && this.session.interactions > 0 && this.session.interactions % 3 === 0) {
        this.askAboutSubjectSwitch();
      }
    }, 30000);

    // Auto-end session after 10 minutes
    setTimeout(() => {
      this.endSession();
    }, 600000);
  }

  private async askAboutSubjectSwitch() {
    const message = "Would you like to switch to a different subject? I can help you with English, Math, Reading, or Debate.";
    await this.speakText(message);
    
    if (this.session) {
      this.session.messages.push({
        role: 'assistant',
        content: message,
        timestamp: new Date()
      });
      this.onSessionUpdate(this.session);
    }
  }

  async switchSubject(newSubject: string) {
    if (this.session) {
      this.session.subject = newSubject;
      this.session.messages = []; // Clear conversation history
      this.onSessionUpdate(this.session);
      await this.sendWelcomeMessage(newSubject);
    }
  }

  async sendTextMessage(text: string) {
    if (!this.session) return;

    // Add user message to session
    this.session.messages.push({
      role: 'user',
      content: text,
      timestamp: new Date()
    });

    this.onMessage({
      type: 'user_message',
      content: text
    });

    // Get AI response
    await this.getAIResponse(text);
  }

  endSession() {
    if (this.session) {
      this.session.endTime = new Date();
      this.session.status = 'ended';
      this.onSessionUpdate(this.session);
    }

    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
    }

    this.disconnect();
  }

  disconnect() {
    this.stopListening();
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
    }
  }

  getSession(): BakameSession | null {
    return this.session;
  }

  isCurrentlyRecording(): boolean {
    return this.isRecording;
  }
}
