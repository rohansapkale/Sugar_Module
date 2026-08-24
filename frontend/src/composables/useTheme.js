import { ref, onMounted } from 'vue'

const isDarkMode = ref(false)

export function initTheme() {
  if (typeof window === 'undefined') return
  const saved = localStorage.getItem('sugar_desk_theme')
  if (saved === 'dark' || (!saved && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
    document.body.classList.add('dark-mode')
  } else {
    isDarkMode.value = false
    document.body.classList.remove('dark-mode')
  }
}

export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    if (isDarkMode.value) {
      document.body.classList.add('dark-mode')
      localStorage.setItem('sugar_desk_theme', 'dark')
    } else {
      document.body.classList.remove('dark-mode')
      localStorage.setItem('sugar_desk_theme', 'light')
    }
  }

  return {
    isDarkMode,
    toggleTheme,
  }
}
