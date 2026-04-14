<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  FileText, 
  Search,
  Folder,
  ChevronRight,
  Users,
  Building2,
  Scale,
  Wand2,
  RefreshCw,
  LayoutGrid,
  List,
  ArrowLeft,
  Menu
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import FileExplorer from '../components/FileExplorer.vue'

const router = useRouter()

// Estado Geral
const loading = ref(true)
const sidebarOpen = ref(false)
const currentUser = ref(null)
const escritorio = ref(null)

// Navegação de Contexto
const activeCategory = ref('internos') // 'internos', 'clientes', 'processos', 'modelos'
const selectedContextId = ref(null)    // ID do cliente ou processo selecionado
const selectedClienteForProcesso = ref(null) // Necessário para FileExplorer em contexto de processo
const virtualFolders = ref([])         // Lista de clientes ou processos (pastas virtuais)
const searchQuery = ref('')

// Carregamento de Dados Base
const carregarDadosBase = async () => {
    try {
        const [resUser, resEsc] = await Promise.all([
            apiFetch('/api/me'),
            apiFetch('/api/escritorio')
        ])
        if (resUser.ok) currentUser.value = await resUser.json()
        if (resEsc.ok) escritorio.value = await resEsc.json()
    } catch (e) {
        console.error("Erro ao carregar dados base", e)
    }
}

// Carregar pastas virtuais (lista de clientes ou processos)
const fetchVirtualFolders = async () => {
    loading.value = true
    try {
        if (activeCategory.value === 'clientes') {
            const res = await apiFetch('/api/clientes')
            if (res.ok) virtualFolders.value = await res.json()
        } else if (activeCategory.value === 'processos') {
            const res = await apiFetch('/api/processos')
            if (res.ok) virtualFolders.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar pastas virtuais", e)
    } finally {
        loading.value = false
    }
}

// Watchers
watch(activeCategory, (newCat) => {
    selectedContextId.value = null
    selectedClienteForProcesso.value = null
    if (['clientes', 'processos'].includes(newCat)) {
        fetchVirtualFolders()
    }
})

onMounted(() => {
    carregarDadosBase()
})

// Ações de Navegação
const selectVirtualFolder = (item) => {
    selectedContextId.value = item.id
    if (activeCategory.value === 'processos') {
        selectedClienteForProcesso.value = item.cliente_id
    }
}

const goBackToVirtualRoots = () => {
    selectedContextId.value = null
    selectedClienteForProcesso.value = null
}

// Filtro de Pastas Virtuais na busca
const filteredVirtualFolders = computed(() => {
    const query = searchQuery.value.toLowerCase()
    return virtualFolders.value.filter(item => {
        const nome = item.nome || item.numero_processo || item.titulo || ''
        return nome.toLowerCase().includes(query)
    })
})

</script>

<template>
    <div class="h-screen flex bg-slate-50 font-sans overflow-hidden">
        <Sidebar :escritorio="escritorio" :usuario="currentUser" :sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

        <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
            <!-- HEADER -->
            <header class="bg-white border-b border-slate-200 px-6 py-4 z-10 shadow-sm">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <button @click="sidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-500">
                             <Menu class="h-6 w-6" /> <!-- Alterado para Menu icon para clareza -->
                        </button>
                        <div class="flex items-center gap-2">
                             <div class="p-2 bg-primary-50 rounded-xl">
                                <Folder class="w-6 h-6 text-primary-600" />
                             </div>
                             <div>
                                <h1 class="text-xl font-black text-slate-900 tracking-tight">Arquivos do Escritório</h1>
                                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">Explorador Centralizado</p>
                             </div>
                        </div>
                    </div>
                </div>
            </header>

            <!-- MOBILE CATEGORY SELECTOR (VISIBLE < LG) -->
            <div class="lg:hidden bg-white border-b border-slate-100 overflow-x-auto no-scrollbar">
                <div class="flex items-center gap-2 p-4 min-w-max">
                    <button @click="activeCategory = 'internos'" :class="[activeCategory === 'internos' ? 'bg-primary-600 text-white shadow-md' : 'bg-slate-50 text-slate-500 border border-slate-100', 'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all transition-all flex items-center gap-2']">
                        <Building2 class="w-4 h-4" /> Internos
                    </button>
                    <button @click="activeCategory = 'clientes'" :class="[activeCategory === 'clientes' ? 'bg-primary-600 text-white shadow-md' : 'bg-slate-50 text-slate-500 border border-slate-100', 'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all transition-all flex items-center gap-2']">
                        <Users class="w-4 h-4" /> Clientes
                    </button>
                    <button @click="activeCategory = 'processos'" :class="[activeCategory === 'processos' ? 'bg-primary-600 text-white shadow-md' : 'bg-slate-50 text-slate-500 border border-slate-100', 'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all transition-all flex items-center gap-2']">
                        <Scale class="w-4 h-4" /> Processos
                    </button>
                    <button @click="activeCategory = 'modelos'" :class="[activeCategory === 'modelos' ? 'bg-purple-600 text-white shadow-md' : 'bg-slate-50 text-slate-500 border border-slate-100', 'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all transition-all flex items-center gap-2']">
                        <Wand2 class="w-4 h-4" /> Modelos
                    </button>
                </div>
            </div>

            <div class="flex-1 flex overflow-hidden">
                <!-- CATEGORY SIDEBAR -->
                <aside class="w-72 bg-white border-r border-slate-100 hidden lg:flex flex-col p-6 gap-8">
                    <section class="space-y-1.5">
                        <h3 class="px-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Bibliotecas</h3>
                        <button @click="activeCategory = 'internos'" :class="[activeCategory === 'internos' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-slate-500 hover:bg-slate-50', 'w-full flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all group']">
                            <Building2 class="w-5 h-5 mr-3 group-hover:scale-110 transition-transform" /> Internos
                        </button>
                        <button @click="activeCategory = 'clientes'" :class="[activeCategory === 'clientes' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-slate-500 hover:bg-slate-50', 'w-full flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all group']">
                            <Users class="w-5 h-5 mr-3 group-hover:scale-110 transition-transform" /> Clientes
                        </button>
                        <button @click="activeCategory = 'processos'" :class="[activeCategory === 'processos' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-slate-500 hover:bg-slate-50', 'w-full flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all group']">
                            <Scale class="w-5 h-5 mr-3 group-hover:scale-110 transition-transform" /> Processos
                        </button>
                        <button @click="activeCategory = 'modelos'" :class="[activeCategory === 'modelos' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-slate-500 hover:bg-slate-50', 'w-full flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all group']">
                            <Wand2 class="w-5 h-5 mr-3 text-purple-500 group-hover:rotate-12 transition-transform" /> Modelos Automação
                        </button>
                    </section>

                    <div class="mt-auto p-5 bg-gradient-to-br from-slate-50 to-slate-100 rounded-3xl border border-slate-200/50">
                        <div class="flex items-center gap-2 mb-2">
                             <div class="p-1.5 bg-sky-100 rounded-lg">
                                <FileText class="w-4 h-4 text-sky-600" />
                             </div>
                             <span class="text-xs font-black text-slate-700 uppercase">Dica Rápidas</span>
                        </div>
                        <p class="text-[11px] text-slate-500 font-medium leading-relaxed">Clique em Clientes ou Processos para navegar nas pastas específicas de cada um.</p>
                    </div>
                </aside>

                <!-- MAIN AREA -->
                <main class="flex-1 overflow-y-auto bg-slate-50/50">
                    <!-- CASE 1: NAVEGAÇÃO DE CONTEXTO (EXPLORER) -->
                    <div v-if="activeCategory === 'internos' || selectedContextId || activeCategory === 'modelos'" class="h-full p-4 sm:p-8">
                        <div class="max-w-6xl mx-auto h-full flex flex-col gap-6">
                            <!-- Breadcrumb/Back Action -->
                            <div v-if="selectedContextId" class="flex items-center gap-3">
                                <button @click="goBackToVirtualRoots" class="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-primary-50 hover:text-primary-700 transition-all shadow-sm">
                                    <ArrowLeft class="w-4 h-4" /> Voltar para {{ activeCategory === 'clientes' ? 'Clientes' : 'Processos' }}
                                </button>
                                <ChevronRight class="w-4 h-4 text-slate-300" />
                                <span class="text-sm font-black text-slate-800 uppercase tracking-tight">Arquivos da Pasta</span>
                            </div>

                            <!-- O MOTOR PRINCIPAL: FILE EXPLORER REUTILIZADO -->
                            <FileExplorer 
                                v-if="activeCategory === 'internos'"
                                contextType="escritorio" 
                                contextId="0" 
                                title="Documentos Internos"
                                class="flex-1"
                            />

                            <FileExplorer 
                                v-else-if="activeCategory === 'modelos'"
                                contextType="escritorio" 
                                contextId="0" 
                                title="Modelos de Automação"
                                class="flex-1"
                            />

                            <FileExplorer 
                                v-else-if="activeCategory === 'clientes' && selectedContextId"
                                contextType="cliente" 
                                :contextId="selectedContextId" 
                                title="Arquivos do Cliente"
                                class="flex-1"
                            />

                            <FileExplorer 
                                v-else-if="activeCategory === 'processos' && selectedContextId"
                                contextType="processo" 
                                :contextId="selectedContextId" 
                                :clienteId="selectedClienteForProcesso"
                                title="Documentos do Processo"
                                class="flex-1"
                            />
                        </div>
                    </div>

                    <!-- CASE 2: LISTAGEM DE PASTAS VIRTUAIS (CLIENTES/PROCESSOS COMO PASTAS) -->
                    <div v-else class="h-full p-4 sm:p-8">
                        <div class="max-w-6xl mx-auto space-y-8">
                            <!-- Search virtual folders -->
                            <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
                                <div class="relative flex-1 max-w-lg w-full">
                                    <Search class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                                    <input v-model="searchQuery" type="text" :placeholder="activeCategory === 'clientes' ? 'Pesquisar cliente...' : 'Pesquisar processo ou numero...'" 
                                           class="w-full pl-12 pr-4 py-3.5 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-sm shadow-sm" />
                                </div>
                                <button @click="fetchVirtualFolders" class="p-3.5 bg-white border border-slate-200 rounded-2xl hover:bg-slate-50 transition-all shadow-sm">
                                    <RefreshCw :class="loading ? 'animate-spin' : ''" class="w-5 h-5 text-slate-500" />
                                </button>
                            </div>

                            <!-- Loading -->
                            <div v-if="loading" class="flex flex-col items-center justify-center py-32">
                                <RefreshCw class="h-10 w-10 text-primary-500 animate-spin mb-4" />
                                <p class="text-slate-500 font-bold uppercase tracking-widest text-xs">Mapeando pastas virtuais...</p>
                            </div>

                            <!-- Virtual Grid -->
                            <div v-else-if="filteredVirtualFolders.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                <div v-for="item in filteredVirtualFolders" :key="item.id" 
                                     @click="selectVirtualFolder(item)"
                                     class="flex items-center gap-4 bg-white p-5 rounded-3xl border border-slate-200 hover:border-primary-400 hover:shadow-xl hover:-translate-y-1 cursor-pointer transition-all group">
                                    <div class="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center group-hover:bg-primary-50 transition-colors">
                                        <Folder v-if="activeCategory === 'clientes'" class="w-7 h-7 text-slate-400 group-hover:text-primary-600 group-hover:fill-primary-100" />
                                        <Scale v-else class="w-7 h-7 text-slate-400 group-hover:text-primary-600" />
                                    </div>
                                    <div class="min-w-0">
                                        <h4 class="text-slate-900 font-black text-sm truncate uppercase tracking-tight">{{ item.nome || item.numero_processo || 'Processo sem numero' }}</h4>
                                        <p class="text-[10px] text-slate-400 font-bold mt-1 uppercase">{{ activeCategory === 'clientes' ? 'Pasta do Cliente' : (item.titulo || 'Pasta do Processo') }}</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Empty State -->
                            <div v-else class="text-center py-32 bg-white rounded-[2rem] border-2 border-dashed border-slate-200">
                                <Folder class="h-16 w-16 text-slate-100 mx-auto mb-4" />
                                <h3 class="text-xl font-black text-slate-900">Nenhum item encontrado</h3>
                                <p class="text-slate-400 text-sm font-medium">Não há {{ activeCategory === 'clientes' ? 'clientes' : 'processos' }} vinculados no momento.</p>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>
</template>

<style scoped>
.group:hover {
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
