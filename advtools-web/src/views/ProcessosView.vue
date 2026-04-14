<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import {
  Scale,
  Search,
  Menu,
  Plus,
  SearchCode,
  Filter,
  ArrowRight,
  Calendar,
  Gavel,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  X,
  ChevronDown,
  LogOut,
  RefreshCw,
  TrendingUp,
  ChevronRight,
  User,
  Settings,
  Brain,
  Zap,
  Download,
  Users,
  FileText,
  AlertTriangle
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()
const router = useRouter()

// UI State
const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const isLoading = ref(true)
const isImporting = ref(false)
const isImportingMassa = ref(false)
const showImportModal = ref(false)
const showProjudiConfirm = ref(false)
const showProjudiRelatorio = ref(false)
const projudiRelatorio = ref(null)
const notification = ref({ show: false, message: '', type: 'success' })

// Data State
const processos = ref([])
const escritorio = ref(null)
const currentUser = ref(null)
const searchQuery = ref('')
const statusFilter = ref('Ativo')

// Pagination State
const currentPage = ref(1)
const itemsPerPage = ref(9)

// Import Form (Unified: DataJud + MNI)
const importForm = ref({
  numero_cnj: '',
  tribunal: '',
  cliente_id: null,
  analisar_com_ia: false,
  tipo_busca: 'cnj' // 'cnj' ou 'interno'
})

// Detecta se o número CNJ pertence ao TJGO (MNI)
const isTJGO = computed(() => {
  if (importForm.value.tipo_busca === 'interno') return true
  const limpo = importForm.value.numero_cnj.replace(/[.-]/g, '')
  if (limpo.length !== 20) return false
  return limpo[13] === '8' && limpo.substring(14, 16) === '09'
})

const importSource = computed(() => isTJGO.value ? 'PROJUDI/MNI' : 'DataJud')

const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const carregarDados = async () => {
    isLoading.value = true
    try {
        const [resEsc, resUser, resProc] = await Promise.all([
            apiFetch('/api/escritorio'),
            apiFetch('/api/me'),
            apiFetch('/api/processos')
        ])
        
        if (resEsc.ok) escritorio.value = await resEsc.json()
        if (resUser.ok) currentUser.value = await resUser.json()
        if (resProc.ok) processos.value = await resProc.json()
    } catch (e) {
        console.error("Erro ao carregar dados", e)
    } finally {
        isLoading.value = false
    }
}

// Reseta página quando filtros mudam
import { watch } from 'vue'
watch([statusFilter, searchQuery], () => {
    currentPage.value = 1
})

const filteredProcessos = computed(() => {
    return processos.value.filter(p => {
        const matchesSearch = p.titulo.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                             (p.numero_processo && p.numero_processo.includes(searchQuery.value))
        const matchesStatus = statusFilter.value === 'Todos' || p.status === statusFilter.value
        return matchesSearch && matchesStatus
    })
})

const paginatedProcessos = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredProcessos.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredProcessos.value.length / itemsPerPage.value))

const nextPag = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const prevPag = () => { if (currentPage.value > 1) currentPage.value-- }

const handleImport = async () => {
    if (!importForm.value.numero_cnj) return
    
    isImporting.value = true
    try {
        let res
        if (isTJGO.value) {
            // Importar via MNI/PROJUDI
            res = await apiFetch('/api/processos/buscar-mni', {
                method: 'POST',
                body: JSON.stringify({
                    numero_processo: importForm.value.numero_cnj,
                    cliente_id: importForm.value.cliente_id
                })
            })
        } else {
            // Importar via DataJud (original)
            res = await apiFetch('/api/processos/buscar-datajud', {
                method: 'POST',
                body: JSON.stringify(importForm.value)
            })
        }
        
        if (res.ok) {
            const novoProcesso = await res.json()
            const source = isTJGO.value ? 'PROJUDI' : 'DataJud'
            showMessage(`Processo importado via ${source} com sucesso! ${novoProcesso.movimentacoes?.length || 0} movimentações.`, 'success')
            processos.value.unshift(novoProcesso)
            showImportModal.value = false
            importForm.value = { numero_cnj: '', tribunal: '', cliente_id: null, analisar_com_ia: false, tipo_busca: 'cnj' }
        } else {
            const err = await res.json()
            showMessage(err.detail || 'Erro ao importar processo.', 'error')
        }
    } catch (e) {
        showMessage('Erro de conexão com o servidor.', 'error')
    } finally {
        isImporting.value = false
    }
}

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

onMounted(carregarDados)

// Importação em massa PROJUDI
const handleImportMassaProjudi = async () => {
    showProjudiConfirm.value = false
    isImportingMassa.value = true
    try {
        const res = await apiFetch('/api/importacao/projudi', { method: 'POST' })
        if (!res.ok) {
            const err = await res.json()
            throw new Error(err.detail || 'Erro na importação')
        }
        projudiRelatorio.value = await res.json()
        showProjudiRelatorio.value = true
        await carregarDados()
    } catch (e) {
        showMessage(e.message, 'error')
    } finally {
        isImportingMassa.value = false
    }
}

const getPriorityClass = (priority) => {
    switch (priority) {
        case 'Urgente': return 'bg-red-100 text-red-700 font-black ring-1 ring-red-200'
        case 'Alta': return 'bg-orange-100 text-orange-700 font-bold ring-1 ring-orange-200'
        case 'Normal': return 'bg-blue-100 text-blue-700 font-medium ring-1 ring-blue-200'
        default: return 'bg-slate-100 text-slate-600 font-medium'
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return d.toLocaleDateString('pt-BR')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex relative">
    
    <!-- Toast -->
    <div v-if="notification.show" 
         :class="['fixed top-4 right-4 z-[100] px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center gap-3 transition-all animate-fade-in-down', 
                  notification.type === 'error' ? 'bg-red-600' : 'bg-emerald-600']">
        <component :is="notification.type === 'error' ? AlertCircle : CheckCircle2" class="w-5 h-5 flex-shrink-0" />
        <span class="max-w-[300px] break-words">{{ notification.message }}</span>
        <button @click="notification.show = false" class="ml-2 mt-0.5 hover:opacity-75">
            <X class="w-4 h-4" />
        </button>
    </div>

    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col overflow-hidden">
      
      <!-- Top Header -->
      <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-30">
        <div class="flex items-center flex-1 gap-4">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 text-slate-500 hover:text-slate-700">
            <Menu class="w-6 h-6" />
          </button>
          
          <div class="max-w-md w-full relative group">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
            <input v-model="searchQuery" 
                   type="text" 
                   placeholder="Buscar número, título ou tribunal..." 
                   class="w-full pl-10 pr-4 py-2 bg-slate-100 border-none rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:bg-white transition-all outline-none" />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <!-- Profile Dropdown -->
          <div class="relative">
            <button @click="showProfileMenu = !showProfileMenu" class="flex items-center gap-2 p-1.5 rounded-full hover:bg-slate-100 transition-colors focus:outline-none">
               <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700">
                 <span class="text-xs font-bold">{{ currentUser ? currentUser.nome.charAt(0).toUpperCase() : 'U' }}</span>
               </div>
               <ChevronDown class="hidden md:block w-4 h-4 text-slate-400" />
            </button>
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-slate-100 divide-y divide-slate-100 z-50 animate-fade-in-up">
              <div class="px-4 py-3">
                <p class="text-sm font-bold text-slate-900 truncate">{{ currentUser?.nome }}</p>
                <p class="text-xs text-slate-500 truncate">{{ currentUser?.email }}</p>
              </div>
              <div class="py-1">
                <button @click="handleLogout" class="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                  <LogOut class="mr-3 h-4 w-4" /> Sair
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in-up">
          <div>
            <h1 class="text-2xl font-black text-slate-900 flex items-center gap-3">
              <Scale class="w-8 h-8 text-primary-600" />
              Processos Judiciais
            </h1>
            <p class="mt-1 text-sm text-slate-500">Monitoramento DataJud e gestão interna de tramitações.</p>
          </div>
          <div class="mt-4 sm:mt-0 flex gap-3">
            <button @click="showProjudiConfirm = true" 
                    :disabled="isImportingMassa"
                    class="px-4 py-2.5 bg-emerald-50 text-emerald-700 font-bold rounded-xl hover:bg-emerald-100 transition-all flex items-center gap-2 border border-emerald-200 shadow-sm shadow-emerald-500/10 disabled:opacity-50">
               <template v-if="isImportingMassa">
                  <RefreshCw class="w-4 h-4 animate-spin" /> Importando...
               </template>
               <template v-else>
                  <Download class="w-4 h-4" /> Importar do PROJUDI
               </template>
            </button>
            <button @click="showImportModal = true" class="px-4 py-2.5 bg-indigo-50 text-indigo-700 font-bold rounded-xl hover:bg-indigo-100 transition-all flex items-center gap-2 border border-indigo-200 shadow-sm shadow-indigo-500/10">
               <SearchCode class="w-4 h-4" /> Importar Processo
            </button>
            <button @click="router.push('/processos/novo')" class="btn-primary flex items-center gap-2 shadow-primary-500/30">
               <Plus class="w-4 h-4" /> Cadastrar Manual
            </button>
          </div>
        </div>

        <!-- Filters & Summary -->
        <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
           <div class="flex gap-2">
              <button v-for="st in ['Todos', 'Ativo', 'Suspenso', 'Arquivado']" 
                      :key="st"
                      @click="statusFilter = st"
                      :class="[statusFilter === st ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/30' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50', 'px-4 py-1.5 rounded-full text-xs font-bold transition-all']">
                {{ st }}
              </button>
           </div>
           <div class="text-xs text-slate-400 font-bold uppercase tracking-widest">
              {{ filteredProcessos.length }} Processos Encontrados
           </div>
        </div>

        <!-- Process List (Premium Grid) -->
        <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-pulse">
           <div v-for="i in 6" :key="i" class="h-48 bg-white rounded-3xl border border-slate-100"></div>
        </div>

        <div v-else-if="filteredProcessos.length === 0" class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
           <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
              <Scale class="w-10 h-10 text-slate-300" />
           </div>
           <h3 class="text-lg font-bold text-slate-900">Nenhum processo encontrado</h3>
           <p class="text-slate-500 text-sm mt-1 max-w-xs text-center">Inicie importando um novo processo diretamente da base do CNJ via DataJud.</p>
           <button @click="showImportModal = true" class="mt-6 font-bold text-primary-600 hover:text-primary-800 transition-colors flex items-center gap-2">
              Começar agora <ArrowRight class="w-4 h-4" />
           </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in-up" style="animation-delay: 0.1s">
           <div v-for="p in paginatedProcessos" 
                :key="p.id" 
                @click="router.push('/processos/' + p.id)"
                class="group bg-white p-6 rounded-3xl border border-slate-100 hover:border-primary-500/30 shadow-sm hover:shadow-xl hover:shadow-primary-500/5 transition-all cursor-pointer relative overflow-hidden flex flex-col">
              
              <!-- Priority Indicator -->
              <div class="absolute top-0 right-0 p-4">
                 <span :class="['text-[9px] px-2 py-0.5 rounded-full uppercase font-black tracking-wider', getPriorityClass(p.prioridade)]">
                    {{ p.prioridade }}
                 </span>
              </div>

              <!-- Header Info -->
              <div class="flex items-start gap-4 mb-4">
                 <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center text-slate-400 group-hover:from-primary-500 group-hover:to-indigo-600 group-hover:text-white transition-all duration-500 shadow-sm flex-shrink-0">
                    <Gavel class="w-6 h-6" />
                 </div>
                 <div class="min-w-0 flex-1">
                    <h3 class="text-base font-black text-slate-900 truncate leading-tight group-hover:text-primary-700 transition-colors" :title="p.titulo">
                       {{ p.titulo }}
                    </h3>
                    <div class="flex items-center gap-1.5 mt-1 text-primary-600 font-bold text-xs uppercase tracking-tight">
                       {{ p.numero_processo || 'NÃO CADASTRADO' }}
                    </div>
                    <!-- Nome do Cliente -->
                    <div v-if="p.cliente" class="mt-2.5 flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-100 rounded-xl">
                       <User class="w-3.5 h-3.5 text-slate-400" />
                       <span class="text-[11px] font-black text-slate-600 truncate">{{ p.cliente.nome }}</span>
                    </div>
                 </div>
              </div>

              <!-- Meta Data -->
              <div class="grid grid-cols-2 gap-4 mt-auto">
                 <div class="flex flex-col">
                    <span class="text-[9px] text-slate-400 uppercase font-black tracking-widest leading-none mb-1.5 flex items-center gap-1">
                       <ShieldCheck class="w-3 h-3" /> Tribunal
                    </span>
                    <span class="text-xs font-bold text-slate-700 truncate capitalize">{{ p.tribunal?.toLowerCase() || '-' }}</span>
                 </div>
                 <div class="flex flex-col items-end">
                    <span class="text-[9px] text-slate-400 uppercase font-black tracking-widest leading-none mb-1.5 flex items-center gap-1">
                       <Calendar class="w-3 h-3" /> Ajuizamento
                    </span>
                    <span class="text-xs font-bold text-slate-700">{{ formatDate(p.data_ajuizamento) }}</span>
                 </div>
              </div>

              <!-- Status & Last Update -->
              <div class="mt-4 pt-4 border-t border-slate-50 flex items-center justify-between">
                 <div class="flex items-center gap-2">
                    <div :class="['w-2 h-2 rounded-full', p.status === 'Ativo' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-300']"></div>
                     <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest">{{ p.status }}</span>
                     <span v-if="p.origem === 'PROJUDI'" class="ml-1 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[8px] font-black uppercase tracking-wider border border-emerald-200">
                        <Zap class="w-2.5 h-2.5" /> PROJUDI
                     </span>
                 </div>
                 <div class="flex items-center gap-1.5 text-slate-400 text-xs">
                    <RefreshCw class="w-3 h-3" />
                    <span class="text-[9px] font-bold">{{ formatDate(p.data_atualizacao) }}</span>
                 </div>
              </div>

              <!-- Hover Arrow -->
              <div class="absolute -right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 group-hover:right-4 transition-all duration-300">
                 <ChevronRight class="w-6 h-6 text-primary-400" />
              </div>
           </div>
        </div>

        <!-- Pagination Controls -->
        <div v-if="totalPages > 1" class="mt-10 flex items-center justify-between bg-white px-8 py-4 rounded-[40px] border border-slate-100 shadow-sm">
            <div class="text-xs text-slate-400 font-bold uppercase tracking-widest">
               Página {{ currentPage }} de {{ totalPages }}
            </div>
            <div class="flex gap-4">
               <button @click="prevPag" 
                       :disabled="currentPage === 1"
                       class="p-2 bg-slate-50 text-slate-400 rounded-2xl hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-slate-50 transition-all border border-slate-100">
                  <ArrowRight class="w-5 h-5 rotate-180" />
               </button>
               <button @click="nextPag" 
                       :disabled="currentPage === totalPages"
                       class="p-2 bg-slate-600 text-white rounded-2xl hover:bg-slate-700 disabled:opacity-30 transition-all shadow-lg shadow-slate-500/10">
                  <ArrowRight class="w-5 h-5" />
               </button>
            </div>
         </div>

      </main>
       <!-- Import Modal (Unified: DataJud + MNI/PROJUDI) -->
    <div v-show="showImportModal" class="fixed inset-0 z-[60] overflow-y-auto px-4 py-8 flex items-center justify-center">
       <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity" @click="showImportModal = false"></div>
       <div class="relative w-full max-w-lg bg-white rounded-[40px] shadow-2xl overflow-hidden border border-white/20 animate-fade-in-up">
          
          <!-- Modal Header -->
          <div class="relative h-40 bg-gradient-to-br from-indigo-600 via-primary-600 to-indigo-800 p-8 text-white overflow-hidden">
             <Scale class="absolute -right-4 -bottom-4 w-48 h-48 opacity-10 rotate-12" />
             <div class="relative z-10 flex flex-col justify-end h-full">
                <div class="w-12 h-12 bg-white/20 backdrop-blur-xl rounded-2xl flex items-center justify-center mb-4">
                   <SearchCode class="w-6 h-6" />
                </div>
                <h2 class="text-2xl font-black">Importar Processo</h2>
                <p class="text-white/70 text-sm font-medium">Conectando ao sistema do tribunal para coleta de dados oficiais.</p>
             </div>
             <button @click="showImportModal = false" class="absolute top-6 right-6 p-2 bg-black/10 hover:bg-black/20 rounded-full transition-colors">
                <X class="w-5 h-5 text-white" />
             </button>
          </div>

          <!-- Modal Body -->
          <div class="p-8 pb-10">
             <div class="space-y-6">
                 <!-- CNJ Number -->
                 <div class="space-y-2">
                    <div class="flex items-center justify-between px-1">
                        <label class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Identificador do Processo</label>
                        <div class="flex bg-slate-100 p-1 rounded-lg gap-1">
                            <button @click="importForm.tipo_busca = 'cnj'" 
                                    :class="['px-2 py-0.5 text-[9px] font-black uppercase rounded-md transition-all', 
                                             importForm.tipo_busca === 'cnj' ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-400']">CNJ</button>
                            <button @click="importForm.tipo_busca = 'interno'" 
                                    :class="['px-2 py-0.5 text-[9px] font-black uppercase rounded-md transition-all', 
                                             importForm.tipo_busca === 'interno' ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-400']">Interno</button>
                        </div>
                    </div>
                    <div class="relative">
                       <input v-model="importForm.numero_cnj" 
                              type="text" 
                              :placeholder="importForm.tipo_busca === 'cnj' ? 'NNNNNNN-DD.AAAA.J.TR.OOOO' : 'Número interno do sistema (Projudi/Outros)'" 
                              class="w-full pl-4 pr-4 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl text-slate-900 font-bold focus:border-primary-500 focus:bg-white transition-all outline-none" />
                       <div class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 font-black">{{ importForm.tipo_busca.toUpperCase() }}</div>
                    </div>
                    <p class="text-[10px] text-slate-400 font-medium px-1">
                        {{ importForm.tipo_busca === 'cnj' ? 'Exemplo: 5760243-22.2025.8.09.0051' : 'Insira o número de registro interno do processo no tribunal.' }}
                    </p>
                 </div>

                <!-- Source Detection Badge -->
                <div v-if="importForm.numero_cnj.replace(/[.-]/g, '').length >= 20" 
                     :class="['flex items-center gap-3 p-4 rounded-2xl border transition-all', 
                              isTJGO ? 'bg-emerald-50/60 border-emerald-200' : 'bg-blue-50/60 border-blue-200']">
                   <div :class="['w-10 h-10 rounded-xl flex items-center justify-center', 
                                isTJGO ? 'bg-emerald-100 text-emerald-600' : 'bg-blue-100 text-blue-600']">
                     <Zap v-if="isTJGO" class="w-5 h-5" />
                     <SearchCode v-else class="w-5 h-5" />
                   </div>
                   <div>
                     <p :class="['text-sm font-black', isTJGO ? 'text-emerald-800' : 'text-blue-800']">
                       {{ isTJGO ? '⚡ PROJUDI TJGO detectado' : '🔗 Tribunal detectado' }}
                     </p>
                     <p :class="['text-[11px] font-medium', isTJGO ? 'text-emerald-600' : 'text-blue-600']">
                       {{ isTJGO ? 'Importação via MNI — dados enriquecidos (partes, advogados, 100+ movimentações)' : 'Importação via DataJud — dados básicos do CNJ' }}
                     </p>
                   </div>
                </div>

                <!-- Tribunal Selection (only for non-TJGO) -->
                <div v-if="!isTJGO" class="space-y-2">
                   <label class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Tribunal (Opcional)</label>
                   <div class="relative">
                      <select v-model="importForm.tribunal" 
                              class="w-full pl-4 pr-10 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl text-slate-900 font-bold appearance-none focus:border-primary-500 focus:bg-white transition-all outline-none">
                         <option value="">Detectar Automaticamente</option>
                         <option value="TJGO">TJGO - Goiás</option>
                         <option value="TJSP">TJSP - São Paulo</option>
                         <option value="TJRJ">TJRJ - Rio de Janeiro</option>
                         <option value="TJMG">TJMG - Minas Gerais</option>
                         <option value="TJRS">TJRS - Rio Grande do Sul</option>
                         <option value="TJPR">TJPR - Paraná</option>
                         <option value="TJBA">TJBA - Bahia</option>
                         <option value="TJSC">TJSC - Santa Catarina</option>
                         <option value="TJPE">TJPE - Pernambuco</option>
                         <option value="TJCE">TJCE - Ceará</option>
                      </select>
                      <ChevronDown class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                   </div>
                </div>


                <!-- Action Button -->
                <button @click="handleImport" 
                        :disabled="isImporting || !importForm.numero_cnj"
                        class="w-full py-5 bg-gradient-to-r from-primary-600 to-indigo-700 text-white rounded-3xl font-black text-lg shadow-xl shadow-primary-500/30 hover:shadow-primary-500/50 hover:-translate-y-1 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none">
                   <template v-if="isImporting">
                      <RefreshCw class="w-6 h-6 animate-spin" />
                      <span>{{ isTJGO ? 'Conectando ao PROJUDI...' : 'Consultando DataJud...' }}</span>
                   </template>
                   <template v-else>
                      <TrendingUp class="w-6 h-6" /> Buscar Processo
                   </template>
                </button>
             </div>
             
             <div class="mt-8 p-4 bg-blue-50/50 rounded-2xl border border-blue-100 flex gap-4">
                <AlertCircle class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <p class="text-[11px] text-blue-700 font-medium leading-relaxed">
                   A importação trará automaticamente a <span class="font-bold">capa</span>, 
                   <span class="font-bold">partes</span>, <span class="font-bold">assuntos</span> e a <span class="font-bold">timeline completa</span> de movimentações direto do Tribunal.
                   <template v-if="isTJGO">
                     <br/><span class="text-emerald-700 font-bold">Via PROJUDI:</span> inclui advogados, documentos catalogados e complementos detalhados.
                   </template>
                </p>
             </div>
          </div>
       </div>
    </div>
    </div>

    <!-- Modal Confirmação Importação PROJUDI -->
    <div v-if="showProjudiConfirm" class="fixed inset-0 z-[70] overflow-y-auto px-4 py-8 flex items-center justify-center">
       <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md" @click="showProjudiConfirm = false"></div>
       <div class="relative w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 animate-fade-in-up">
          <div class="text-center">
             <div class="mx-auto w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center mb-4">
                <Download class="w-8 h-8 text-emerald-600" />
             </div>
             <h3 class="text-xl font-black text-slate-900 mb-2">Importar do PROJUDI</h3>
             <p class="text-sm text-slate-500 leading-relaxed">
                Isso consultará suas <span class="font-bold">intimações pendentes</span> no PROJUDI/TJGO e importará automaticamente todos os processos encontrados.
             </p>
             <p class="text-xs text-slate-400 mt-2">Processos existentes serão atualizados. Clientes serão identificados e vinculados automaticamente.</p>
          </div>
          <div class="mt-6 flex gap-3">
             <button @click="showProjudiConfirm = false" class="flex-1 py-3 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-all">Cancelar</button>
             <button @click="handleImportMassaProjudi" class="flex-1 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-all flex items-center justify-center gap-2">
                <Zap class="w-4 h-4" /> Confirmar
             </button>
          </div>
       </div>
    </div>

    <!-- Modal Relatório PROJUDI -->
    <div v-if="showProjudiRelatorio" class="fixed inset-0 z-[70] overflow-y-auto px-4 py-8 flex items-center justify-center">
       <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md" @click="showProjudiRelatorio = false"></div>
       <div class="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden animate-fade-in-up">
          <!-- Header -->
          <div class="bg-gradient-to-br from-emerald-500 to-emerald-700 p-6 text-white">
             <div class="flex items-center gap-3">
                <CheckCircle2 class="w-8 h-8" />
                <div>
                   <h3 class="text-xl font-black">Importação Concluída</h3>
                   <p class="text-emerald-100 text-sm">{{ projudiRelatorio?.total_avisos || 0 }} avisos encontrados no PROJUDI</p>
                </div>
             </div>
             <button @click="showProjudiRelatorio = false" class="absolute top-4 right-4 p-2 bg-black/10 hover:bg-black/20 rounded-full">
                <X class="w-5 h-5 text-white" />
             </button>
          </div>
          <!-- Stats -->
          <div class="p-6">
             <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-emerald-50 p-4 rounded-2xl border border-emerald-100 text-center">
                   <div class="text-3xl font-black text-emerald-700">{{ projudiRelatorio?.processos_novos || 0 }}</div>
                   <div class="text-xs font-bold text-emerald-600 mt-1 flex items-center justify-center gap-1"><FileText class="w-3 h-3" /> Processos Novos</div>
                </div>
                <div class="bg-blue-50 p-4 rounded-2xl border border-blue-100 text-center">
                   <div class="text-3xl font-black text-blue-700">{{ projudiRelatorio?.processos_atualizados || 0 }}</div>
                   <div class="text-xs font-bold text-blue-600 mt-1 flex items-center justify-center gap-1"><RefreshCw class="w-3 h-3" /> Atualizados</div>
                </div>
                <div class="bg-indigo-50 p-4 rounded-2xl border border-indigo-100 text-center">
                   <div class="text-3xl font-black text-indigo-700">{{ projudiRelatorio?.clientes_criados || 0 }}</div>
                   <div class="text-xs font-bold text-indigo-600 mt-1 flex items-center justify-center gap-1"><Users class="w-3 h-3" /> Clientes Criados</div>
                </div>
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-center">
                   <div class="text-3xl font-black text-slate-700">{{ projudiRelatorio?.clientes_vinculados || 0 }}</div>
                   <div class="text-xs font-bold text-slate-500 mt-1 flex items-center justify-center gap-1"><User class="w-3 h-3" /> Vinculados</div>
                </div>
             </div>

             <!-- Merges Sugeridos -->
             <div v-if="projudiRelatorio?.merges_sugeridos?.length" class="mb-4">
                <h4 class="text-xs font-black text-amber-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                   <AlertTriangle class="w-3.5 h-3.5" /> Divergências de Nome Detectadas
                </h4>
                <div v-for="(m, i) in projudiRelatorio.merges_sugeridos" :key="i" 
                     class="p-3 bg-amber-50 rounded-xl border border-amber-100 mb-2 text-xs">
                   <div class="font-bold text-amber-800">CPF/CNPJ: {{ m.cpf_cnpj }}</div>
                   <div class="text-amber-700">No sistema: <span class="font-bold">{{ m.nome_banco }}</span></div>
                   <div class="text-amber-700">No PROJUDI: <span class="font-bold">{{ m.nome_projudi }}</span></div>
                </div>
             </div>

             <!-- Erros -->
             <div v-if="projudiRelatorio?.erros?.length" class="mb-4">
                <h4 class="text-xs font-black text-red-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                   <AlertCircle class="w-3.5 h-3.5" /> Erros
                </h4>
                <div v-for="(err, i) in projudiRelatorio.erros" :key="i" 
                     class="p-3 bg-red-50 rounded-xl border border-red-100 mb-2 text-xs text-red-700">
                   {{ err }}
                </div>
             </div>

             <button @click="showProjudiRelatorio = false" class="w-full py-3 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all mt-2">
                Fechar
             </button>
          </div>
       </div>
    </div>
    
  </div>
</template>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white font-bold py-2.5 px-6 rounded-xl hover:bg-primary-700 active:scale-95 transition-all;
}

.animate-fade-in-down {
  animation: fade-in-down 0.4s ease-out;
}

.animate-fade-in-up {
  animation: fade-in-up 0.4s ease-out;
}

@keyframes fade-in-down {
  0% { opacity: 0; transform: translateY(-20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
