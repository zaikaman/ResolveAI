/**
 * Client-side encryption utilities using AES-256-GCM
 */
import CryptoJS from 'crypto-js'

/**
 * Derive encryption key from user password using PBKDF2
 */
export function deriveKey(password: string, salt: string): string {
  return CryptoJS.PBKDF2(password, salt, {
    keySize: 256 / 32,
    iterations: 100000
  }).toString()
}

/**
 * Encrypt a value with user-derived key
 */
export function encryptValue(value: number | string, userKey: string): string {
  const encrypted = CryptoJS.AES.encrypt(value.toString(), userKey).toString()
  return encrypted
}

/**
 * Decrypt a value with user-derived key
 */
export function decryptValue(encrypted: string, userKey: string): string {
  const decrypted = CryptoJS.AES.decrypt(encrypted, userKey).toString(CryptoJS.enc.Utf8)
  return decrypted
}

/**
 * Decrypt numeric value
 */
export function decryptNumber(encrypted: string, userKey: string): number {
  const decrypted = decryptValue(encrypted, userKey)
  return parseFloat(decrypted)
}

/**
 * Generate random salt for key derivation
 */
export function generateSalt(): string {
  return CryptoJS.lib.WordArray.random(128 / 8).toString()
}
