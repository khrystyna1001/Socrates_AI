import { defineStore } from 'pinia'


const AUTH_BASE_URL = "/auth/api"

function getCookie(name: string) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? ''
  }
  return ''
}

function parseRegisterError(payload: unknown) {
  if (!payload || typeof payload !== 'object') {
    return 'Registration failed. Please try again.'
  }

  const maybePayload = payload as Record<string, unknown>

  if (typeof maybePayload.message === 'string' && maybePayload.message.length > 0) {
    return maybePayload.message
  }

  if (typeof maybePayload.error === 'string' && maybePayload.error.length > 0) {
    try {
      const parsed = JSON.parse(maybePayload.error) as Record<string, Array<{ message?: string }>>
      const firstField = Object.values(parsed)[0]
      const firstMessage = firstField?.[0]?.message
      if (firstMessage) {
        return firstMessage
      }
    } catch {
      return maybePayload.error
    }
  }

  return 'Registration failed. Please check your data and try again.'
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const storedState = localStorage.getItem('authState')
    return storedState
      ? JSON.parse(storedState)
      : {
          user: null,
          isAuthenticated: false,
        }
  },
  actions: {
    async setCsrfToken() {
      await fetch(`${AUTH_BASE_URL}/set-csrf-token`, {
        method: 'GET',
        credentials: 'include',
      })
    },

    async login(username: string, password: string, router: { push: (path: string) => Promise<void> } | null = null) {
      try {
        await this.setCsrfToken()

        const response = await fetch(`${AUTH_BASE_URL}/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            username,
            password,
          }),
          credentials: 'include',
        })

        const data = await response.json().catch(() => ({}))

        if (response.ok) {
          const maybeUser = typeof data === 'object' && data !== null && 'user' in data ? data.user : null
          this.isAuthenticated = true
          this.user = maybeUser
          this.saveState()
          if (router) {
            await router.push('/')
          }
          return {
            success: true,
            message: typeof data.message === 'string' ? data.message : 'Logged in successfully.',
          }
        }

        this.user = null
        this.isAuthenticated = false
        this.saveState()
        return {
          success: false,
          message: typeof data.message === 'string' ? data.message : 'Invalid credentials.',
        }
      } catch {
        this.user = null
        this.isAuthenticated = false
        this.saveState()
        return {
          success: false,
          message: 'Could not connect to server. Please try again.',
        }
      }
    },

    async register(email: string, password: string) {
      await this.setCsrfToken()

      try {
        const response = await fetch(`${AUTH_BASE_URL}/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            email,
            password,
          }),
          credentials: 'include',
        })

        const payload = await response.json().catch(() => ({}))

        if (response.ok) {
          return {
            success: true,
            message: 'Account created successfully. You can now log in.',
          }
        }

        return {
          success: false,
          message: parseRegisterError(payload),
        }
      } catch {
        return {
          success: false,
          message: 'Could not connect to server. Please try again.',
        }
      }
    },

    async logout(router: { push: (path: string) => Promise<void> } | null = null) {
      try {
        await fetch(`${AUTH_BASE_URL}/logout`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          },
          credentials: 'include',
        })

        this.user = null
        this.isAuthenticated = false
        this.saveState()

        if (router) {
          await router.push('/login')
        }
      } catch (error) {
        console.error('Logout failed', error)
        throw error
      }
    },

    async fetchUser() {
      try {
        const response = await fetch(`${AUTH_BASE_URL}/user`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
        })
        if (response.ok) {
          const data = await response.json()
          this.user = data
          this.isAuthenticated = true
        } else {
          this.user = null
          this.isAuthenticated = false
        }
      } catch (error) {
        console.error('Failed to fetch user', error)
        this.user = null
        this.isAuthenticated = false
      }
      this.saveState()
    },

    saveState() {
      localStorage.setItem(
        'authState',
        JSON.stringify({
          user: this.user,
          isAuthenticated: this.isAuthenticated,
        }),
      )
    },
  },
})
