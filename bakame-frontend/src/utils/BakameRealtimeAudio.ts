import { authAPI } from '@/services/api';

export interface BakameSession {
  subject: string;
  startTime: Date;
  endTime?: Date;
  interactions: number;
  status: 'active' | 'ended';
}

export class AudioRecorder {
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;

  constructor(private onAudioData: (audioData: Float32Array) => void) {}

  async start() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 24000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      this.audioContext = new AudioContext({
        sampleRate: 24000,
      });
      
      this.source = this.audioContext.createMediaStreamSource(this.stream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        this.onAudioData(new Float32Array(inputData));
      };
      
      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      throw error;
    }
  }

  stop() {
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}

export class BakameRealtimeChat {
  private pc: RTCPeerConnection | null = null;
  private dc: RTCDataChannel | null = null;
  private audioEl: HTMLAudioElement;
  private recorder: AudioRecorder | null = null;
  private session: BakameSession | null = null;
  private sessionCheckInterval: NodeJS.Timeout | null = null;

  constructor(
    private onMessage: (message: any) => void,
    private onSessionUpdate: (session: BakameSession) => void
  ) {
    this.audioEl = document.createElement("audio");
    this.audioEl.autoplay = true;
  }

  async init(subject: string) {
    try {
      // Create new session
      this.session = {
        subject,
        startTime: new Date(),
        interactions: 0,
        status: 'active'
      };

      // Get ephemeral token from our FastAPI backend
      const { data, error } = await authAPI.getRealtimeToken(subject);

      if (error || !data.client_secret?.value) {
        throw new Error("Failed to get ephemeral token");
      }

      const EPHEMERAL_KEY = data.client_secret.value;

      // Create peer connection
      this.pc = new RTCPeerConnection();

      // Set up remote audio
      this.pc.ontrack = e => this.audioEl.srcObject = e.streams[0];

      // Add local audio track
      const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.pc.addTrack(ms.getTracks()[0]);

      // Set up data channel
      this.dc = this.pc.createDataChannel("oai-events");
      this.dc.addEventListener("message", (e) => {
        const event = JSON.parse(e.data);
        this.handleRealtimeEvent(event);
      });

      // Create and set local description
      const offer = await this.pc.createOffer();
      await this.pc.setLocalDescription(offer);

      // Connect to OpenAI's Realtime API
      const baseUrl = "https://api.openai.com/v1/realtime";
      const model = "gpt-4o-realtime-preview-2024-12-17";
      const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
        method: "POST",
        body: offer.sdp,
        headers: {
          Authorization: `Bearer ${EPHEMERAL_KEY}`,
          "Content-Type": "application/sdp"
        },
      });

      const answer = {
        type: "answer" as RTCSdpType,
        sdp: await sdpResponse.text(),
      };
      
      await this.pc.setRemoteDescription(answer);
      console.log("Bakame WebRTC connection established");

      // Start recording
      this.recorder = new AudioRecorder((audioData) => {
        if (this.dc?.readyState === 'open') {
          this.dc.send(JSON.stringify({
            type: 'input_audio_buffer.append',
            audio: this.encodeAudioData(audioData)
          }));
        }
      });
      await this.recorder.start();

      // Start session monitoring
      this.startSessionMonitoring();

      // Send initial greeting
      this.sendWelcomeMessage(subject);

    } catch (error) {
      console.error("Error initializing Bakame chat:", error);
      throw error;
    }
  }

  private handleRealtimeEvent(event: any) {
    console.log('Bakame event:', event);
    
    if (this.session) {
      // Count interactions
      if (event.type === 'response.done') {
        this.session.interactions++;
        this.onSessionUpdate(this.session);
      }
    }

    this.onMessage(event);
  }

  private sendWelcomeMessage(subject: string) {
    const welcomeMessages = {
      english: "Hello! I'm Bakame, your English tutor. I'm here to help you improve your English skills. What would you like to work on today?",
      math: "Welcome! I'm Bakame, your Math tutor. I'm excited to help you with mathematics. What math topic can we explore together?",
      reading: "Hi there! I'm Bakame, your Reading tutor. I'm here to help you become a better reader. Would you like to read something together or discuss a book?",
      debate: "Greetings! I'm Bakame, your Debate coach. I'll help you develop your argumentation and critical thinking skills. What topic interests you for discussion?"
    };

    const message = welcomeMessages[subject as keyof typeof welcomeMessages] || welcomeMessages.english;
    
    if (this.dc?.readyState === 'open') {
      this.dc.send(JSON.stringify({
        type: 'conversation.item.create',
        item: {
          type: 'message',
          role: 'assistant',
          content: [{ type: 'text', text: message }]
        }
      }));
      this.dc.send(JSON.stringify({ type: 'response.create' }));
    }
  }

  private startSessionMonitoring() {
    // Check for subject switching every 3 interactions
    this.sessionCheckInterval = setInterval(() => {
      if (this.session && this.session.interactions > 0 && this.session.interactions % 3 === 0) {
        this.askAboutSubjectSwitch();
      }
    }, 30000); // Check every 30 seconds

    // Auto-end session after 10 minutes
    setTimeout(() => {
      this.endSession();
    }, 600000); // 10 minutes
  }

  private askAboutSubjectSwitch() {
    if (this.dc?.readyState === 'open') {
      this.dc.send(JSON.stringify({
        type: 'conversation.item.create',
        item: {
          type: 'message',
          role: 'assistant',
          content: [{ 
            type: 'text', 
            text: "Would you like to switch to a different subject? I can help you with English, Math, Reading, or Debate." 
          }]
        }
      }));
      this.dc.send(JSON.stringify({ type: 'response.create' }));
    }
  }

  private encodeAudioData(float32Array: Float32Array): string {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    
    const uint8Array = new Uint8Array(int16Array.buffer);
    let binary = '';
    const chunkSize = 0x8000;
    
    for (let i = 0; i < uint8Array.length; i += chunkSize) {
      const chunk = uint8Array.subarray(i, Math.min(i + chunkSize, uint8Array.length));
      binary += String.fromCharCode.apply(null, Array.from(chunk));
    }
    
    return btoa(binary);
  }

  async sendMessage(text: string) {
    if (!this.dc || this.dc.readyState !== 'open') {
      throw new Error('Bakame is not ready');
    }

    const event = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{ type: 'input_text', text }]
      }
    };

    this.dc.send(JSON.stringify(event));
    this.dc.send(JSON.stringify({type: 'response.create'}));
  }

  switchSubject(newSubject: string) {
    if (this.session) {
      this.session.subject = newSubject;
      this.onSessionUpdate(this.session);
      this.sendWelcomeMessage(newSubject);
    }
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

    // Send goodbye message
    if (this.dc?.readyState === 'open') {
      this.dc.send(JSON.stringify({
        type: 'conversation.item.create',
        item: {
          type: 'message',
          role: 'assistant',
          content: [{ 
            type: 'text', 
            text: "Great job today! Thanks for learning with Bakame. Come back anytime to continue your studies!" 
          }]
        }
      }));
      this.dc.send(JSON.stringify({ type: 'response.create' }));
    }

    setTimeout(() => {
      this.disconnect();
    }, 3000);
  }

  disconnect() {
    this.recorder?.stop();
    this.dc?.close();
    this.pc?.close();
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
    }
  }

  getSession(): BakameSession | null {
    return this.session;
  }
}
