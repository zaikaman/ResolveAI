/**
 * Vapi service for voice AI integration (frontend)
 * Uses @vapi-ai/web SDK for voice conversations
 */
import Vapi from '@vapi-ai/web'

const vapiPublicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY

if (!vapiPublicKey) {
  console.warn('VITE_VAPI_PUBLIC_KEY is not set - Vapi features will be disabled')
}

class VapiService {
  private vapi: Vapi | null = null
  private isInitialized = false

  /**
   * Initialize Vapi client
   */
  initialize() {
    if (this.isInitialized || !vapiPublicKey) return

    this.vapi = new Vapi(vapiPublicKey)
    this.isInitialized = true
  }

  /**
   * Start a voice conversation with an assistant
   */
  async startCall(assistantId: string, assistantOverrides?: Record<string, any>) {
    if (!this.vapi) {
      throw new Error('Vapi is not initialized')
    }

    return this.vapi.start(assistantId, assistantOverrides)
  }

  /**
   * Start a voice conversation with inline assistant configuration
   */
  async startCallWithConfig(config: {
    model: {
      provider: string
      model: string
      messages: Array<{ role: string; content: string }>
    }
    voice: {
      provider: string
      voiceId: string
    }
    [key: string]: any
  }) {
    if (!this.vapi) {
      throw new Error('Vapi is not initialized')
    }

    return this.vapi.start(config)
  }

  /**
   * Stop the current call
   */
  stopCall() {
    if (!this.vapi) return
    this.vapi.stop()
  }

  /**
   * Send a text message during the call
   */
  sendMessage(message: { role: string; content: string }) {
    if (!this.vapi) return

    this.vapi.send({
      type: 'add-message',
      message,
    })
  }

  /**
   * Check if microphone is muted
   */
  isMuted(): boolean {
    if (!this.vapi) return false
    return this.vapi.isMuted()
  }

  /**
   * Mute/unmute the microphone
   */
  setMuted(muted: boolean) {
    if (!this.vapi) return
    this.vapi.setMuted(muted)
  }

  /**
   * Make the assistant say something and optionally end the call
   */
  say(message: string, endCallAfterSpoken = false) {
    if (!this.vapi) return
    this.vapi.say(message, endCallAfterSpoken)
  }

  /**
   * Subscribe to Vapi events
   */
  on(event: string, callback: (...args: any[]) => void) {
    if (!this.vapi) return
    this.vapi.on(event as any, callback)
  }

  /**
   * Unsubscribe from Vapi events
   */
  off(event: string, callback: (...args: any[]) => void) {
    if (!this.vapi) return
    this.vapi.off(event as any, callback)
  }

  /**
   * Check if Vapi is available
   */
  isAvailable(): boolean {
    return this.isInitialized && this.vapi !== null
  }
}

// Export singleton instance
export const vapiService = new VapiService()

// Initialize on module load
if (vapiPublicKey) {
  vapiService.initialize()
}
