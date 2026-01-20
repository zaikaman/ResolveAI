/**
 * Job polling utility for handling async backend operations
 */

import api from './api';

export interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
}

export interface JobPollOptions {
  pollInterval?: number; // milliseconds between polls (default: 1000)
  maxAttempts?: number; // maximum number of poll attempts (default: 60)
  onProgress?: (progress: number) => void; // callback for progress updates
  signal?: AbortSignal; // abort signal for cancellation
}

/**
 * Poll a job until it completes or fails
 * 
 * @param jobId - Job ID to poll
 * @param options - Polling options
 * @returns Job result when completed
 * @throws Error if job fails or polling times out
 */
export async function pollJob<T = any>(
  jobId: string,
  options: JobPollOptions = {}
): Promise<T> {
  const {
    pollInterval = 1000,
    maxAttempts = 60,
    onProgress,
    signal
  } = options;

  let attempts = 0;

  while (attempts < maxAttempts) {
    // Check if cancelled
    if (signal?.aborted) {
      throw new Error('Job polling cancelled');
    }

    try {
      // Poll job status
      const response = await api.get<JobStatus>(`/jobs/${jobId}/status`);
      const job = response.data;

      // Update progress if callback provided
      if (onProgress && job.progress !== undefined) {
        onProgress(job.progress);
      }

      // Check job status
      if (job.status === 'completed') {
        // Get full result
        const resultResponse = await api.get<JobStatus>(`/jobs/${jobId}`);
        return resultResponse.data.result as T;
      }

      if (job.status === 'failed') {
        throw new Error(job.error || 'Job failed');
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
      attempts++;
    } catch (error: any) {
      // If it's a network error, retry
      if (error.code === 'ERR_NETWORK' && attempts < maxAttempts - 1) {
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        attempts++;
        continue;
      }
      throw error;
    }
  }

  throw new Error('Job polling timeout - maximum attempts reached');
}

/**
 * Create a job and immediately start polling for results
 * 
 * @param createJobFn - Function that creates and returns the job
 * @param options - Polling options
 * @returns Job result when completed
 */
export async function createAndPollJob<T = any>(
  createJobFn: () => Promise<{ data: { id: string } }>,
  options: JobPollOptions = {}
): Promise<T> {
  // Create the job
  const jobResponse = await createJobFn();
  const jobId = jobResponse.data.id;

  // Poll for results
  return pollJob<T>(jobId, options);
}
