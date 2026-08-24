import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export const VOUCHER_TYPE_MAP = {
  F4: { name: 'Contra', title: 'Contra Voucher', route: '/voucher/contra' },
  F5: { name: 'Purchase Payment', title: 'Purchase Payment (Supplier)', route: '/voucher/payment' },
  F6: { name: 'Broker Party Payment', title: 'Broker Party Payment (Receipt)', route: '/voucher/receipt' },
  F8: { name: 'Dispatch Entry', title: 'Dispatch Entry (Sales/Delivery)', route: '/voucher/dispatch' },
  F9: { name: 'Sugar Purchase', title: 'Sugar Purchase Voucher', route: '/voucher/purchase' },
}

// Global shared UI state for modals and overlays
export const globalUiState = {
  isHelpOpen: ref(false),
  isDateModalOpen: ref(false),
  isGoToOpen: ref(false),
  isConfirmModalOpen: ref(false),
  confirmModalData: ref(null),
  toastMessage: ref(''),
  toastVisible: ref(false),
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

export function useKeyboardEngine(callbacks = {}) {
  const router = useRouter()

  const handleGlobalKeyDown = (e) => {
    // 1. If Alt+G pressed -> toggle Go To palette
    if (e.altKey && (e.key === 'g' || e.key === 'G')) {
      e.preventDefault()
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

    // 5. Function Keys F1-F12
    if (e.key.startsWith('F') && /^F([1-9]|1[0-2])$/.test(e.key)) {
      e.preventDefault()
      handleFunctionKey(e.key)
      return
    }

    // 6. Delegate view-specific keys if provided
    if (callbacks.onKeyDown) {
      const handled = callbacks.onKeyDown(e)
      if (handled) return
    }

    // 7. Global Escape navigation fallback
    if (e.key === 'Escape') {
      if (callbacks.onEscape) {
        callbacks.onEscape()
      } else if (router && router.currentRoute.value.path !== '/') {
        router.push('/')
      }
    }
  }

  const handleFunctionKey = (fk) => {
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

  onMounted(() => {
    window.addEventListener('keydown', handleGlobalKeyDown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeyDown)
  })

  return {
    globalUiState,
    handleFunctionKey,
    showToast,
    openConfirm,
    closeConfirm,
  }
}
