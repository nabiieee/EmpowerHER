import { describe, it, expect, vi, beforeEach } from 'vitest'
import { postMatchQuery } from '../api'

// Mock fetch globally
const fetchMock = vi.fn()
global.fetch = fetchMock

describe('API Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('postMatchQuery', () => {
    it('should make a successful API call', async () => {
      const mockResponse = {
        summary: 'Test summary',
        mentors: [{ name: 'Test Mentor', title: 'Test Title' }],
        jobs: [{ title: 'Test Job', company: 'Test Company' }],
        next_steps: ['Step 1', 'Step 2']
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const result = await postMatchQuery('Test message')

      expect(fetchMock).toHaveBeenCalledWith('/api/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'Test message' }),
        cache: 'no-cache',
      })

      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ detail: 'Server error' })
      })

      await expect(postMatchQuery('Test message')).rejects.toThrow('Server error')
    })

    it('should handle network errors', async () => {
      fetchMock.mockRejectedValueOnce(new Error('Network error'))

      await expect(postMatchQuery('Test message')).rejects.toThrow('Network error')
    })
  })
})