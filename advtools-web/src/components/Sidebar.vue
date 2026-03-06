<script setup>
import { 
  ref, 
  watch, 
  onMounted,
  computed
} from 'vue'
import { 
  LayoutDashboard, 
  Users, 
  Scale, 
  PenTool, 
  BadgeDollarSign, 
  X,
  Wand2,
  CheckCircle2
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps({
  escritorio: { type: Object, default: null },
  usuario: { type: Object, default: null },
  sidebarOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const navigation = [
  { name: 'Home', icon: LayoutDashboard, path: '/dashboard' },
  { name: 'Clientes e Serviços', icon: Users, path: '/clientes' },
  { name: 'Processos Judiciais', icon: Scale, path: '/processos' },
  { name: 'Docs do Escritório', icon: PenTool, path: '/modelos' },
  { name: 'Redator Inteligente', icon: Wand2, path: '/redator' },
  { name: 'Tarefas e Prazos', icon: CheckCircle2, path: '/tarefas' },
  { name: 'Financeiro', icon: BadgeDollarSign, path: '#' },
]

const navigationAdmin = computed(() => {
  if (props.usuario?.is_admin) {
    return [
      { name: 'Gestão Global', icon: ShieldCheck, path: '/configuracoes?tab=global' }
    ]
  }
  return []
})

import { ShieldCheck } from 'lucide-vue-next'

// Aspect Ratio Detection
const isRectangular = ref(false)
const logoUrl = computed(() => {
  if (props.escritorio?.logo_path) {
    return `http://localhost:8000/static/${props.escritorio.logo_path}`
  }
  return null
})

const checkLogoAspectRatio = () => {
  if (!logoUrl.value) return
  
  const img = new Image()
  img.onload = () => {
    // Se a largura for significativamente maior que a altura (ex: 1.2x), consideramos retangular
    isRectangular.value = img.width / img.height > 1.2
  }
  img.src = logoUrl.value
}

watch(() => logoUrl.value, checkLogoAspectRatio, { immediate: true })

onMounted(checkLogoAspectRatio)

const isActive = (path) => {
  if (path === '#') return false
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}
</script>

<template>
  <div>
    <!-- Mobile Sidebar -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-[60] md:hidden flex">
      <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="emit('close')"></div>
      <aside class="relative flex-1 flex flex-col max-w-xs w-full bg-white shadow-2xl transition-transform transform">
        <div class="absolute top-0 right-0 -mr-12 pt-4">
          <button @click="emit('close')" class="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
            <X class="h-6 w-6 text-white" />
          </button>
        </div>

        <!-- Branding Area -->
        <div class="p-6 border-b border-slate-100 flex flex-col items-center">
          <img src="../assets/logo-horizontal.png" alt="ADVtools" class="h-8 object-contain" />
        </div>

        <nav class="flex-1 px-4 py-8 space-y-1 overflow-y-auto">
          <router-link v-for="item in navigation" 
                       :key="item.name" 
                       :to="item.path" 
                       @click="emit('close')"
                       :class="[isActive(item.path) ? 'bg-primary-50 text-primary-700 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900', 'group flex items-center px-4 py-3 text-sm rounded-xl transition-all']">
            <component :is="item.icon" :class="[isActive(item.path) ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-600', 'mr-3 h-5 w-5']" />
            {{ item.name }}
          </router-link>

          <!-- Admin Section Mobile -->
          <div v-if="navigationAdmin.length > 0" class="pt-4 mt-4 border-t border-slate-100">
            <p class="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Administração</p>
            <router-link v-for="item in navigationAdmin" 
                         :key="item.name" 
                         :to="item.path" 
                         @click="emit('close')"
                         :class="[isActive(item.path) ? 'bg-indigo-50 text-indigo-700 font-bold' : 'text-slate-600 hover:bg-indigo-50/30 hover:text-indigo-600', 'group flex items-center px-4 py-3 text-sm rounded-xl transition-all']">
              <component :is="item.icon" :class="[isActive(item.path) ? 'text-indigo-600' : 'text-slate-400 group-hover:text-indigo-500', 'mr-3 h-5 w-5']" />
              {{ item.name }}
            </router-link>
          </div>
        </nav>

        <!-- Mobile Footer Branding -->
        <div class="p-6 border-t border-slate-100">
           <div class="flex items-center gap-3">
              <template v-if="escritorio?.logo_path">
                <img :src="logoUrl" 
                     alt="Logo do Escritório" 
                     :class="[isRectangular ? 'max-h-16 w-full object-contain' : 'h-12 w-12 object-contain rounded-lg shadow-sm']" />
                <span v-if="!isRectangular" class="text-slate-900 font-bold text-xs uppercase tracking-wider line-clamp-1">{{ escritorio.nome }}</span>
              </template>
              <div v-else-if="escritorio?.nome" class="flex items-center gap-3">
                 <div class="h-10 w-10 flex-shrink-0 flex items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-indigo-600 text-white font-black text-lg shadow-sm">
                   {{ escritorio.nome.charAt(0).toUpperCase() }}
                 </div>
                 <span class="text-slate-900 font-bold text-xs uppercase tracking-wider line-clamp-1">{{ escritorio.nome }}</span>
              </div>
           </div>
        </div>
      </aside>
    </div>

    <!-- Desktop Sidebar -->
    <aside class="hidden md:flex flex-col w-72 bg-white border-r border-slate-200 shadow-[20px_0_40px_-15px_rgba(0,0,0,0,0.03)] min-h-screen z-20">
      <!-- Top Branding Area (Minimalist) -->
      <div class="px-8 pt-10 pb-6 flex flex-col items-start">
        <img src="../assets/logo-horizontal.png" alt="ADVtools" class="h-10 object-contain hover:opacity-80 transition-opacity cursor-pointer" />
      </div>

      <!-- Navigation Menu (Expanded) -->
      <nav class="flex-1 px-4 py-6 space-y-1.5">
        <router-link v-for="item in navigation" 
                     :key="item.name" 
                     :to="item.path" 
                     :class="[isActive(item.path) 
                       ? 'bg-primary-50 text-primary-700 shadow-[inset_4px_0_0_0_#2563eb]' 
                       : 'text-slate-500 hover:bg-slate-50 hover:text-primary-600', 
                       'group flex items-center px-5 py-3.5 text-sm font-bold transition-all duration-200 rounded-xl mb-1']">
          <component :is="item.icon" :class="[isActive(item.path) ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-600', 'mr-3 h-5 w-5 transition-transform group-hover:scale-110']" />
          {{ item.name }}
        </router-link>

        <!-- Admin Section Desktop -->
        <div v-if="navigationAdmin.length > 0" class="pt-6 mt-6 border-t border-slate-100">
           <div class="px-6 mb-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Administração</div>
           <router-link v-for="item in navigationAdmin" 
                       :key="item.name" 
                       :to="item.path" 
                       :class="[isActive(item.path) 
                         ? 'bg-indigo-50 text-indigo-700 shadow-[inset_4px_0_0_0_#4f46e5]' 
                         : 'text-slate-500 hover:bg-indigo-50/50 hover:text-indigo-600', 
                         'group flex items-center px-5 py-3.5 text-sm font-bold transition-all duration-200 rounded-xl mb-1']">
            <component :is="item.icon" :class="[isActive(item.path) ? 'text-indigo-600' : 'text-slate-400 group-hover:text-indigo-500', 'mr-3 h-5 w-5 transition-transform group-hover:scale-110']" />
            {{ item.name }}
          </router-link>
        </div>
      </nav>
      
      <!-- Premium Office Footer (Relocated Branding) -->
      <div class="p-6 border-t border-slate-50">
        <!-- Adaptive Box Container -->
        <div :class="[
          'bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-2xl border border-slate-100/50 shadow-sm transition-all duration-300',
          isRectangular && escritorio?.logo_path ? 'p-2' : 'p-4 flex items-center gap-4'
        ]">
          
          <!-- Case: Rectangular Logo (Full Container) -->
          <template v-if="isRectangular && escritorio?.logo_path">
            <div class="w-full h-20 flex items-center justify-center overflow-hidden rounded-xl bg-white p-1 border border-white hover:border-primary-100 transition-colors">
              <img :src="logoUrl" 
                   alt="Logo do Escritório" 
                   class="max-h-full max-w-full object-contain" />
            </div>
          </template>

          <!-- Case: Square Logo or Fallback (Small Icon + Text) -->
          <template v-else>
            <!-- Office Logo/Initial -->
            <div v-if="escritorio?.logo_path" class="h-12 w-12 flex-shrink-0 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center overflow-hidden">
               <img :src="logoUrl" 
                    alt="Logo do Escritório" 
                    class="h-full w-full object-contain" />
            </div>
            <div v-else-if="escritorio?.nome" class="h-12 w-12 flex-shrink-0 flex items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-indigo-600 text-white font-black text-xl shadow-lg ring-2 ring-white">
              {{ escritorio.nome.charAt(0).toUpperCase() }}
            </div>
            
            <!-- Office Name (Only for non-rectangular) -->
            <div class="flex flex-col min-w-0">
              <span class="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest leading-none mb-1">Escritório</span>
              <div class="flex flex-col">
                <span class="text-[12px] text-slate-900 font-black truncate max-w-[140px]" :title="escritorio?.nome">{{ escritorio?.nome || 'Carregando...' }}</span>
                <span class="text-[10px] text-emerald-600 font-bold flex items-center gap-1 mt-0.5">
                   <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                   Painel Ativo
                </span>
              </div>
            </div>
          </template>

        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.router-link-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
