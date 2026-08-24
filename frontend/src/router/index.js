import { createRouter, createWebHashHistory } from 'vue-router'
import GatewayView from '../views/GatewayView.vue'
import VoucherEntryView from '../views/VoucherEntryView.vue'
import RegisterView from '../views/RegisterView.vue'
import DayBookView from '../views/DayBookView.vue'
import MastersView from '../views/MastersView.vue'

const routes = [
  {
    path: '/',
    name: 'Gateway',
    component: GatewayView,
    meta: { title: 'Gateway — Sugar Module' },
  },
  {
    path: '/voucher/:type',
    name: 'VoucherEntry',
    component: VoucherEntryView,
    meta: { title: 'Voucher Entry' },
  },
  {
    path: '/register/:type',
    name: 'Register',
    component: RegisterView,
    meta: { title: 'Register List' },
  },
  {
    path: '/daybook',
    name: 'DayBook',
    component: DayBookView,
    meta: { title: 'Day Book & Audit Register' },
  },
  {
    path: '/masters',
    name: 'Masters',
    component: MastersView,
    meta: { title: 'Masters Directory' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
})
