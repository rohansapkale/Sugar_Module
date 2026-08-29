import { ref, reactive } from 'vue'

const bootState = reactive({
  user: 'Administrator',
  full_name: 'Administrator',
  roles: ['System Manager', 'Sugar Operations'],
  companies: [],
  default_company: 'Rajendra Narahari Lokhande',
  today: new Date().toISOString().split('T')[0],
  isLoaded: false,
})

export function useFrappeApi() {
  const isOnline = ref(true)

  const getCsrfToken = () => {
    if (bootState.csrf_token) return bootState.csrf_token
    if (window.csrf_token) return window.csrf_token
    if (window.frappe_boot && window.frappe_boot.csrf_token) return window.frappe_boot.csrf_token
    const match = document.cookie.match(/csrf_token=([^;]+)/)
    return match ? match[1] : ''
  }

  const call = async (method, args = {}) => {
    try {
      if (!bootState.isLoaded) {
        await initBoot()
      }
      const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
      const token = getCsrfToken()
      if (token) {
        headers['X-Frappe-CSRF-Token'] = token
      }

      const bodyObj = { ...args }
      if (token) {
        bodyObj.csrf_token = token
      }

      const response = await fetch(`/api/method/${method}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(bodyObj),
      })

      if (!response.ok) {
        let errMsg = `Server error (${response.status})`
        try {
          const errData = await response.json()
          if (errData._server_messages) {
            const msgs = JSON.parse(errData._server_messages)
            if (Array.isArray(msgs) && msgs.length) {
              const parsed = typeof msgs[0] === 'string' ? JSON.parse(msgs[0]) : msgs[0]
              if (parsed.message) {
                errMsg = parsed.message.replace(/<[^>]*>/g, '').trim()
              }
            }
          } else if (errData.exception) {
            errMsg = errData.exception.split(':').pop().trim()
          } else if (errData.message) {
            errMsg = errData.message
          }
        } catch (_) {}
        throw new Error(errMsg)
      }

      const data = await response.json()
      return data.message !== undefined ? data.message : data
    } catch (err) {
      console.warn(`[FrappeApi] API Call ${method} failed:`, err.message)
      throw err
    }
  }

  const initBoot = async () => {
    if (window.frappe_boot) {
      Object.assign(bootState, window.frappe_boot)
      bootState.isLoaded = true
      return bootState
    }

    try {
      const res = await fetch('/api/method/sugar_module.sugar_module.api.get_boot')
      if (res.ok) {
        const data = await res.json()
        const boot = data.message || data
        Object.assign(bootState, boot)
        if (boot.csrf_token) {
          window.csrf_token = boot.csrf_token
        }
        bootState.isLoaded = true
      }
    } catch (e) {
      console.warn('[FrappeApi] Boot fetch fallback:', e)
    }
    bootState.isLoaded = true
    return bootState
  }

  const searchLedgers = async (query = '', doctype = null) => {
    try {
      const url = new URL('/api/method/sugar_module.sugar_module.api.search_ledgers_and_parties', window.location.origin)
      if (doctype) url.searchParams.set('doctype', doctype)
      if (query) url.searchParams.set('query', query)
      url.searchParams.set('limit', '50')

      const res = await fetch(url.toString(), {
        headers: {
          'Accept': 'application/json',
        }
      })

      if (res.ok) {
        const data = await res.json()
        const list = data.message || data
        if (Array.isArray(list)) {
          return list
        }
      }
    } catch (e) {
      console.error('[FrappeApi] searchLedgers error:', e)
    }
    return []
  }

  const saveVoucher = async (voucherType, payload, submit = 0) => {
    const res = await call('sugar_module.sugar_module.api.save_sugar_voucher', {
      voucher_type: voucherType,
      payload,
      submit,
    })
    return res
  }

  const getRegisterData = async (voucherType, query = '') => {
    try {
      const url = new URL('/api/method/sugar_module.sugar_module.api.get_register_data', window.location.origin)
      url.searchParams.set('voucher_type', voucherType)
      if (query) url.searchParams.set('query', query)
      url.searchParams.set('limit', '100')

      const res = await fetch(url.toString(), {
        headers: { 'Accept': 'application/json' }
      })
      if (res.ok) {
        const data = await res.json()
        return data.message || data
      }
    } catch (e) {
      console.error('[FrappeApi] getRegisterData error:', e)
    }
    return { records: [], summary: {} }
  }

  const getDayBook = async (date = null, voucherType = null) => {
    try {
      const url = new URL('/api/method/sugar_module.sugar_module.api.get_daybook', window.location.origin)
      if (date) url.searchParams.set('date', date)
      if (voucherType) url.searchParams.set('voucher_type', voucherType)
      url.searchParams.set('limit', '100')

      const res = await fetch(url.toString(), {
        headers: {
          'Accept': 'application/json',
        }
      })

      if (res.ok) {
        const data = await res.json()
        const list = data.message || data
        if (Array.isArray(list)) {
          return list
        }
      }
    } catch (e) {
      console.error('[FrappeApi] getDayBook error:', e)
    }
    return []
  }

  const getVoucherDetails = async (doctype, name) => {
    try {
      const url = `/api/method/sugar_module.sugar_module.api.get_voucher_details?doctype=${encodeURIComponent(doctype)}&name=${encodeURIComponent(name)}`
      const res = await fetch(url)
      if (res.ok) {
        const data = await res.json()
        return data.message || data
      }
    } catch (e) {
      console.error('[FrappeApi] getVoucherDetails error:', e)
    }
    return null
  }

  const getMastersSummary = async () => {
    try {
      const res = await fetch('/api/method/sugar_module.sugar_module.api.get_masters_summary')
      if (res.ok) {
        const data = await res.json()
        return data.message || data
      }
    } catch (e) {
      console.error('[FrappeApi] getMastersSummary error:', e)
    }
    return null
  }

  const getGatewayMetrics = async (period = 'Today') => {
    try {
      const res = await fetch(`/api/method/sugar_module.sugar_module.api.get_gateway_metrics?period=${encodeURIComponent(period)}`)
      if (res.ok) {
        const data = await res.json()
        return data.message || data
      }
    } catch (e) {
      console.error('[FrappeApi] getGatewayMetrics error:', e)
    }
    return null
  }

  return {
    bootState,
    isOnline,
    initBoot,
    call,
    searchLedgers,
    saveVoucher,
    getRegisterData,
    getDayBook,
    getVoucherDetails,
    getMastersSummary,
    getGatewayMetrics,
  }
}
