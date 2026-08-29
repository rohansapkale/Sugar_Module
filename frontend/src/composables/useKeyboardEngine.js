import { ref } from 'vue'
import { router } from '../router'

export const VOUCHER_TYPE_MAP = {
  P: { name: 'Sugar Purchase', title: 'Sugar Purchase Voucher', route: '/voucher/purchase' },
  D: { name: 'Dispatch Entry', title: 'Dispatch Entry (Sales/Delivery)', route: '/voucher/dispatch' },
  Y: { name: 'Purchase Payment', title: 'Purchase Payment (Supplier)', route: '/voucher/payment' },
  R: { name: 'Broker Party Payment', title: 'Broker Party Payment (Receipt)', route: '/voucher/receipt' },
  T: { name: 'Contra', title: 'Contra Voucher', route: '/voucher/contra' },
  // Function keys compatibility
  F4: { name: 'Contra', title: 'Contra Voucher', route: '/voucher/contra' },
  F5: { name: 'Purchase Payment', title: 'Purchase Payment (Supplier)', route: '/voucher/payment' },
  F6: { name: 'Broker Party Payment', title: 'Broker Party Payment (Receipt)', route: '/voucher/receipt' },
  F8: { name: 'Dispatch Entry', title: 'Dispatch Entry (Sales/Delivery)', route: '/voucher/dispatch' },
  F9: { name: 'Sugar Purchase', title: 'Sugar Purchase Voucher', route: '/voucher/purchase' },
}

// Global shared UI state for modals, overlays, and active sidebar category
export const globalUiState = {
  isHelpOpen: ref(false),
  isDateModalOpen: ref(false),
  isGoToOpen: ref(false),
  isConfirmModalOpen: ref(false),
  confirmModalData: ref(null),
  toastMessage: ref(''),
  toastVisible: ref(false),
  activeSidebarCategory: ref('ALL'), // 'ALL' | 'MASTERS' | 'VOUCHERS' | 'REPORTS'
}

let toastTimer = null
export function showToast(msg, duration = 2000) {
  clearTimeout(toastTimer)
  globalUiState.toastMessage.value = msg
  globalUiState.toastVisible.value = true
  toastTimer = setTimeout(() => {
    globalUiState.toastVisible.value = false
  }, duration)
}

export function openConfirm(title, body, onYes, onNo) {
  globalUiState.confirmModalData.value = { title, body, onYes, onNo }
  globalUiState.isConfirmModalOpen.value = true
}

export function closeConfirm(isConfirmed) {
  const data = globalUiState.confirmModalData.value
  globalUiState.isConfirmModalOpen.value = false
  globalUiState.confirmModalData.value = null
  if (isConfirmed && data && data.onYes) {
    data.onYes()
  } else if (!isConfirmed && data && data.onNo) {
    data.onNo()
  }
}

export function handleFunctionKey(fk) {
  if (fk === 'F1') {
    globalUiState.isHelpOpen.value = true
    return
  }
  if (fk === 'F2') {
    globalUiState.isDateModalOpen.value = true
    return
  }
  if (fk === 'F10') {
    if (router) router.push('/daybook')
    return
  }
  if (fk === 'F11' || fk === 'F12') {
    showToast(`${fk} — Configuration & Company Settings`)
    return
  }

  if (VOUCHER_TYPE_MAP[fk]) {
    const v = VOUCHER_TYPE_MAP[fk]
    if (router) router.push(v.route)
  }
}

// Singleton Global Keydown Handler
let isGlobalListenerAttached = false

function initGlobalKeyboardListener() {
  if (isGlobalListenerAttached || typeof window === 'undefined') return
  isGlobalListenerAttached = true

  window.addEventListener('keydown', (e) => {
    const targetTag = (e.target?.tagName || '').toUpperCase()
    const activeTag = (document.activeElement?.tagName || '').toUpperCase()
    const inInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(targetTag) || ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeTag)

    // 1. Alt+G / Alt+g / Ctrl+G / Ctrl+K -> Toggle Go To Command Palette
    const isGKey = e.key === 'g' || e.key === 'G' || e.code === 'KeyG'
    const isKKey = e.key === 'k' || e.key === 'K' || e.code === 'KeyK'

    if ((e.altKey && isGKey) || (e.ctrlKey && (isGKey || isKKey))) {
      e.preventDefault()
      e.stopPropagation()
      globalUiState.isGoToOpen.value = !globalUiState.isGoToOpen.value
      return
    }

    // 2. Priority: Confirm Modal
    if (globalUiState.isConfirmModalOpen.value) {
      if (e.key === 'Enter' || e.key.toLowerCase() === 'y') {
        e.preventDefault()
        closeConfirm(true)
      } else if (e.key === 'Escape' || e.key.toLowerCase() === 'n') {
        e.preventDefault()
        closeConfirm(false)
      }
      return
    }

    // 3. Priority: Go To command palette
    if (globalUiState.isGoToOpen.value) {
      if (e.key === 'Escape') {
        e.preventDefault()
        globalUiState.isGoToOpen.value = false
      }
      return
    }

    // 4. Priority: Help Modal or Date Modal
    if (globalUiState.isHelpOpen.value || globalUiState.isDateModalOpen.value) {
      if (e.key === 'Escape' || e.key === 'Enter') {
        e.preventDefault()
        globalUiState.isHelpOpen.value = false
        globalUiState.isDateModalOpen.value = false
      }
      return
    }

    // If currently typing in ANY input or search bar, do NOT intercept keystrokes!
    if (inInput) {
      return
    }

    // 5. Function Keys F1-F12
    if (e.key.startsWith('F') && /^F([1-9]|1[0-2])$/.test(e.key)) {
      e.preventDefault()
      handleFunctionKey(e.key)
      return
    }

    // 6. Global Escape Navigation Handler (returns to Gateway)
    if (e.key === 'Escape') {
      e.preventDefault()
      if (router && router.currentRoute.value.path !== '/') {
        router.push('/')
      }
      return
    }

    // 7. Navigation Hotkeys outside inputs (M = Masters, V = Vouchers, R = Reports / Receipt)
    if (!e.altKey && !e.ctrlKey && !e.metaKey) {
      const key = e.key.toUpperCase()

      // Category Switching
      if (key === 'M') {
        e.preventDefault()
        globalUiState.activeSidebarCategory.value = 'MASTERS'
        showToast('🏛️ Masters Menu Activated (M)')
        return
      }
      if (key === 'V') {
        e.preventDefault()
        globalUiState.activeSidebarCategory.value = 'VOUCHERS'
        showToast('📝 Vouchers Menu Activated (V)')
        return
      }

      // Direct Voucher Hotkeys (P = Purchase, D = Dispatch, Y = Payment, R = Receipt, T = Contra)
      if (key === 'P') {
        e.preventDefault()
        if (router) router.push('/voucher/purchase')
        return
      }
      if (key === 'D') {
        e.preventDefault()
        if (router) router.push('/voucher/dispatch')
        return
      }
      if (key === 'Y') {
        e.preventDefault()
        if (router) router.push('/voucher/payment')
        return
      }
      if (key === 'T') {
        e.preventDefault()
        if (router) router.push('/voucher/contra')
        return
      }
      if (key === 'R') {
        e.preventDefault()
        if (globalUiState.activeSidebarCategory.value === 'VOUCHERS' || router.currentRoute.value.path.startsWith('/voucher')) {
          if (router) router.push('/voucher/receipt')
        } else {
          globalUiState.activeSidebarCategory.value = 'REPORTS'
          showToast('📊 Reports Menu Activated (R)')
        }
        return
      }
    }
  })
}

// Auto-initialize singleton listener
initGlobalKeyboardListener()

export function useKeyboardEngine() {
  return {
    globalUiState,
    handleFunctionKey,
    showToast,
    openConfirm,
    closeConfirm,
  }
}
