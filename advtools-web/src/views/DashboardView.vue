<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  LayoutDashboard,
  Scale,
  Users,
  PenTool,
  BadgeDollarSign,
  Settings,
  Bell,
  Search,
  Menu,
  MoreVertical,
  CheckCircle2,
  Clock,
  AlertCircle,
  X,
  User,
  LogOut,
  ChevronDown,
  Briefcase,
  Plus,
  Building2
} from 'lucide-vue-next'
import GlobalClientSearch from '../components/GlobalClientSearch.vue'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

const router = useRouter() // Initialized useRouter

const handleLogout = () => {
  localStorage.removeItem('advtools_token')
  router.push('/')
}

const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const escritorio = ref(null)
const currentUser = ref(null)

const carregarEscritorio = async () => {
    try {
        const res = await apiFetch('/api/escritorio')
        if (res.ok) {
            escritorio.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar escritório", e)
    }
}

const carregarUsuario = async () => {
    try {
        const res = await apiFetch('/api/me')
        if (res.ok) {
            currentUser.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar usuario", e)
    }
}

const dashboardStats = ref({
    processos_ativos: 0,
    assinaturas_pendentes: 0,
    clientes_ativos: 0,
    receita_mes: 0
})

const carregarStats = async () => {
    try {
        const res = await apiFetch('/api/escritorio/stats')
        if (res.ok) {
            dashboardStats.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar estatísticas do dashboard", e)
    }
}

onMounted(() => {
    carregarEscritorio()
    carregarUsuario()
    carregarStats()
    carregarTarefas()
})

const stats = computed(() => [
  { 
    name: 'Processos Ativos', 
    stat: dashboardStats.value.processos_ativos.toString(), 
    change: 'Total', 
    changeType: 'increase', 
    icon: Scale, 
    color: 'text-primary-600', 
    bg: 'bg-primary-50',
    path: '/processos'
  },
  { 
    name: 'Assinaturas Pend.', 
    stat: dashboardStats.value.assinaturas_pendentes.toString(), 
    change: 'Aguardando', 
    changeType: 'neutral', 
    icon: PenTool, 
    color: 'text-amber-600', 
    bg: 'bg-amber-50',
    path: '/arquivos'
  },
  { 
    name: 'Clientes Ativos', 
    stat: dashboardStats.value.clientes_ativos.toString(), 
    change: 'Base Total', 
    changeType: 'increase', 
    icon: Users, 
    color: 'text-emerald-600', 
    bg: 'bg-emerald-50',
    path: '/clientes'
  },
  { 
    name: 'Receita deste mês', 
    stat: new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(dashboardStats.value.receita_mes), 
    change: 'Faturamento', 
    changeType: 'increase', 
    icon: BadgeDollarSign, 
    color: 'text-indigo-600', 
    bg: 'bg-indigo-50',
    path: '/financeiro'
  },
])

const processos = [
  { id: '0010234-55.2023.8.26.0100', cliente: 'TechCorp S.A.', tribunal: 'TJSP', status: 'Aguardando Prazo', date: 'Hoje, 14:30', badgeRef: 'bg-amber-50 text-amber-700 ring-amber-600/20' },
  { id: '1053001-12.2024.8.26.0100', cliente: 'João da Silva', tribunal: 'TJSP', status: 'Petição Juntada', date: 'Ontem, 09:15', badgeRef: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' },
  { id: '0812345-88.2022.4.03.6100', cliente: 'Construtora XYZ', tribunal: 'TRF3', status: 'Concluso p/ Sentença', date: '22/10/2023', badgeRef: 'bg-primary-50 text-primary-700 ring-primary-600/20' },
  { id: '0000111-22.2021.5.02.0001', cliente: 'Maria Oliveira', tribunal: 'TRT2', status: 'Audiência Marcada', date: '15/10/2023', badgeRef: 'bg-purple-50 text-purple-700 ring-purple-600/20' },
]

const tarefas = ref([])

const carregarTarefas = async () => {
    try {
        // Buscamos apenas pendentes e em andamento para o dashboard
        const res = await apiFetch('/api/tarefas?limit=10')
        if (res.ok) {
            const allTasks = await res.json()
            // Filtramos apenas as que não estão concluídas/canceladas
            tarefas.value = allTasks
                .filter(t => t.status !== 'Concluída' && t.status !== 'Cancelada')
                .slice(0, 5) // Mostramos apenas as 5 mais urgentes
        }
    } catch (e) {
        console.error("Erro ao carregar tarefas", e)
    }
}

const showSignDropdown = ref(false)
const signContainer = ref(null)

const handleClickOutsideSign = (event) => {
    if (signContainer.value && !signContainer.value.contains(event.target)) {
        showSignDropdown.value = false
    }
}

onMounted(() => {
    document.addEventListener('mousedown', handleClickOutsideSign)
})


onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutsideSign)
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    
    <!-- Sidebar Centralizado -->
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      
      <!-- Top Header -->
      <header class="relative h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-50">
        <div class="flex items-center flex-1 gap-4">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 text-slate-500 hover:text-slate-700">
            <Menu class="w-6 h-6" />
          </button>
          
          <div class="max-w-md w-full hidden sm:block">
            <GlobalClientSearch placeholder="Buscar clientes..." />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <button class="relative p-2 text-slate-400 hover:text-slate-500 transition-colors rounded-full hover:bg-slate-100">
            <span class="absolute top-1.5 right-1.5 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
            <Bell class="w-6 h-6" />
          </button>
          <!-- Profile Dropdown -->
          <div class="relative ml-2">
            <button @click="showProfileMenu = !showProfileMenu" @blur="setTimeout(() => showProfileMenu = false, 200)" class="flex items-center gap-2 p-1.5 rounded-full hover:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
               <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700">
                 <span class="text-xs font-bold">{{ currentUser ? currentUser.nome.charAt(0).toUpperCase() : 'U' }}</span>
               </div>
               <span class="hidden md:block text-sm font-medium text-slate-700">{{ currentUser ? currentUser.nome : 'Carregando...' }}</span>
               <ChevronDown class="hidden md:block w-4 h-4 text-slate-400" />
            </button>
            
            <!-- Dropdown Menu -->
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 focus:outline-none z-50 animate-fade-in-up" role="menu">
              <div class="px-4 py-3">
                <p class="text-sm text-slate-900 truncate">{{ currentUser ? currentUser.nome : 'Carregando...' }}</p>
                <p class="text-xs font-medium text-slate-500 truncate">{{ currentUser ? currentUser.email : '' }}</p>
              </div>
              <div class="py-1" role="none">
                <router-link to="/configuracoes" class="group flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors" role="menuitem">
                  <Settings class="mr-3 h-4 w-4 text-slate-400 group-hover:text-primary-500" aria-hidden="true" />
                  Configs. e perfil
                </router-link>
              </div>
              <div class="py-1" role="none">
                <button @click="handleLogout" class="group flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors" role="menuitem">
                  <LogOut class="mr-3 h-4 w-4 text-red-500 group-hover:text-red-600" aria-hidden="true" />
                  Sair do Sistema
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Scrollable Area -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        
        <!-- Welcome Section -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in-up relative z-10">
          <div>
            <h1 class="text-2xl font-bold text-slate-900">Visão Geral</h1>
            <p class="mt-1 text-sm text-slate-500">Acompanhe seus processos, prazos e métricas do escritório.</p>
          </div>
          <div class="mt-4 sm:mt-0 flex gap-3">
            <div class="relative" ref="signContainer">
                <button @click="showSignDropdown = !showSignDropdown" class="btn-secondary flex items-center gap-2">
                   <PenTool class="w-4 h-4" /> Nova Assinatura <ChevronDown class="w-4 h-4 opacity-50" />
                </button>
                
                <div v-if="showSignDropdown" class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl ring-1 ring-black ring-opacity-5 py-1 z-40 animate-fade-in-up">
                    <button @click="router.push('/clientes?focus=true')" class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors flex items-center gap-3">
                        <Users class="w-4 h-4 text-slate-400" />
                        <div>
                            <p class="font-bold">Documento de Cliente</p>
                            <p class="text-[10px] text-slate-500">Assinaturas vinculadas a um cliente</p>
                        </div>
                    </button>
                    <button @click="router.push('/modelos?tab=internos')" class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors flex items-center gap-3 border-t border-slate-50">
                        <Building2 class="w-4 h-4 text-slate-400" />
                        <div>
                            <p class="font-bold">Documento do Escritório</p>
                            <p class="text-[10px] text-slate-500">Documentos de uso interno</p>
                        </div>
                    </button>
                </div>
            </div>
            
            <button @click="router.push('/processos/novo')" class="btn-primary flex items-center gap-2 shadow-primary-500/30">
               <Scale class="w-4 h-4" /> Novo Processo
            </button>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <router-link v-for="(item, index) in stats" :key="item.name" :to="item.path" class="card p-6 animate-fade-in-up relative overflow-hidden group hover:border-primary-200 transition-colors cursor-pointer block" :style="`animation-delay: ${index * 0.1}s`">
            <!-- Decorative background block -->
            <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-slate-50 group-hover:bg-primary-50/50 transition-colors z-0"></div>
            
            <div class="relative z-10 flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-slate-500">{{ item.name }}</p>
                <p class="mt-2 text-3xl font-bold tracking-tight text-slate-900">{{ item.stat }}</p>
              </div>
              <div :class="[item.bg, item.color, 'p-3 rounded-xl shadow-sm']">
                <component :is="item.icon" class="w-6 h-6" />
              </div>
            </div>
            <div class="relative z-10 mt-4 flex items-center text-sm">
              <span :class="[item.changeType === 'increase' ? 'text-emerald-600' : 'text-red-600', 'font-medium flex items-center gap-1']">
                 <svg v-if="item.changeType === 'increase'" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/></svg>
                 <svg v-else class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                {{ item.change }}
              </span>
              <span class="ml-2 text-slate-400">em relação ao último mês</span>
            </div>
          </router-link>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <!-- Recent Processes Table -->
          <div class="lg:col-span-2 card p-0 animate-fade-in-up" style="animation-delay: 0.4s;">
            <div class="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-white">
              <h2 class="text-base font-semibold leading-6 text-slate-900">Últimas Movimentações DataJud</h2>
              <button class="text-sm font-medium text-primary-600 hover:text-primary-700">Ver todas &rarr;</button>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-200">
                <thead class="bg-slate-50">
                  <tr>
                    <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Processo</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Cliente / Tribunal</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status Atual</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Data</th>
                    <th scope="col" class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Ações</span></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 bg-white">
                  <tr v-for="proc in processos" :key="proc.id" class="hover:bg-slate-50 transition-colors">
                    <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium text-slate-900">{{ proc.id }}</td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm">
                      <div class="text-slate-900 font-medium">{{ proc.cliente }}</div>
                      <div class="text-slate-500">{{ proc.tribunal }}</div>
                    </td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm">
                      <span :class="[proc.badgeRef, 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset']">
                        {{ proc.status }}
                      </span>
                    </td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">{{ proc.date }}</td>
                    <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm font-medium">
                      <button class="text-slate-400 hover:text-slate-600">
                        <MoreVertical class="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tasks / To-Dos Column -->
          <div class="lg:col-span-1 flex flex-col gap-6">
             <div class="card p-0 animate-fade-in-up" style="animation-delay: 0.5s;">
                <div class="px-6 py-5 border-b border-slate-200 bg-white">
                  <h2 class="text-base font-semibold leading-6 text-slate-900">(Próximas Tarefas)</h2>
                </div>
                <div class="p-2">
                   <ul v-if="tarefas.length > 0" class="divide-y divide-slate-100">
                      <li v-for="tarefa in tarefas" :key="tarefa.id" @click="router.push(`/tarefas?edit=${tarefa.id}`)" class="p-4 flex items-start gap-4 hover:bg-slate-50 rounded-lg transition-colors cursor-pointer group">
                         <div class="flex-shrink-0 mt-0.5">
                            <Clock v-if="tarefa.prioridade === 'Normal'" class="w-5 h-5 text-slate-400 group-hover:text-primary-500" />
                            <AlertCircle v-else-if="tarefa.prioridade === 'Alta' || tarefa.prioridade === 'Urgente'" class="w-5 h-5 text-red-400 group-hover:text-red-500" />
                            <CheckCircle2 v-else class="w-5 h-5 text-emerald-400 group-hover:text-emerald-500" />
                         </div>
                         <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between gap-2">
                                <p class="text-sm font-semibold text-slate-900 truncate">{{ tarefa.titulo }}</p>
                                <span :class="[
                                    tarefa.status === 'Pendente' ? 'bg-slate-100 text-slate-600' : 'bg-blue-100 text-blue-700',
                                    'inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium'
                                ]">
                                    {{ tarefa.status }}
                                </span>
                            </div>
                            <div class="flex items-center gap-3 mt-1">
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                   {{ tarefa.data_vencimento ? new Date(tarefa.data_vencimento).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) : 'Sem prazo' }}
                                </p>
                                <div v-if="tarefa.responsavel" class="flex items-center gap-1.5 py-0.5 px-2 bg-slate-50 rounded-full border border-slate-100">
                                    <div class="w-3.5 h-3.5 rounded-full bg-primary-100 flex items-center justify-center text-[8px] font-bold text-primary-700">
                                        {{ tarefa.responsavel.nome.charAt(0).toUpperCase() }}
                                    </div>
                                    <span class="text-[10px] text-slate-500 font-medium">{{ tarefa.responsavel.nome.split(' ')[0] }}</span>
                                </div>
                            </div>
                         </div>
                      </li>
                   </ul>
                   <div v-else class="py-12 text-center">
                      <p class="text-sm text-slate-400 font-medium">Nenhuma tarefa pendente.</p>
                   </div>
                </div>
                <div class="px-6 py-4 border-t border-slate-100 bg-slate-50 text-center rounded-b-xl">
                   <button @click="router.push('/tarefas')" class="text-sm font-medium text-primary-600 hover:text-primary-700">Ver Tarefas &rarr;</button>
                </div>
             </div>

             <!-- Document Quick Action -->
             <div class="card bg-gradient-to-br from-primary-600 to-primary-800 text-white p-6 animate-fade-in-up" style="animation-delay: 0.6s;">
                <h3 class="font-semibold text-lg mb-2">Petição Inteligente</h3>
                <p class="text-primary-100 text-sm mb-4">Gere petições altamente assertivas em segundos utilizando a Inteligência Artificial Gemini integrada aos dados do seu processo.</p>
                <button @click="router.push('/redator')" class="bg-white text-primary-700 hover:bg-primary-50 font-medium py-2 px-4 rounded-lg shadow-sm transition-colors text-sm w-full">
                  Gerar Nova Peça com IA
                </button>
             </div>
          </div>

        </div>

      </main>
    </div>
  </div>
</template>
