<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  FileText, 
  Search,
  Folder,
  ChevronRight,
  Filter,
  Users,
  Building2,
  Scale,
  Wand2,
  RefreshCw,
  Download,
  Trash2,
  CheckCircle2,
  Clock,
  AlertCircle,
  MoreVertical,
  ExternalLink,
  Eye,
  FileDown
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

const router = useRouter()

// Estado Geral
const loading = ref(true)
const searchQuery = ref('')
const sidebarOpen = ref(false)
const currentUser = ref(null)
const escritorio = ref(null)
const files = ref([])
const activeCategory = ref('todos') // 'todos', 'internos', 'clientes', 'processos', 'modelos'
const activeStatus = ref(null) // null, 'Aguardando', 'Parcial', 'Concluido'

// Carregamento de Dados
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

const fetchFiles = async () => {
    loading.value = true
    try {
        let url = `/api/arquivos/list?tipo=${activeCategory.value}`
        if (activeStatus.value) url += `&status_assinatura=${activeStatus.value}`
        if (searchQuery.value) url += `&search=${searchQuery.value}`
        
        const res = await apiFetch(url)
        if (res.ok) {
            files.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar arquivos", e)
    } finally {
        loading.value = false
    }
}

// Watchers para recarregar ao mudar filtros
watch([activeCategory, activeStatus], () => {
    fetchFiles()
})

// Debounce para busca
let searchTimeout
watch(searchQuery, () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(fetchFiles, 500)
})

onMounted(() => {
    carregarDadosBase()
    fetchFiles()
})

// Auxiliares de UI
const getFileExtension = (path) => {
    if (!path) return 'FILE'
    const parts = path.split('.')
    return parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

const getExtensionColor = (ext) => {
    const colors = {
        'PDF': 'bg-red-50 text-red-600 border-red-100',
        'DOCX': 'bg-blue-50 text-blue-600 border-blue-100',
        'XLSX': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'PNG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPG': 'bg-purple-50 text-purple-600 border-purple-100',
    }
    return colors[ext] || 'bg-slate-50 text-slate-500 border-slate-100'
}

const getStatusBadge = (status) => {
    if (status === 'Concluido') return { label: 'Assinado', class: 'bg-emerald-100 text-emerald-700 border-emerald-200' }
    if (status === 'Parcial' || status === 'Aguardando') return { label: 'Pendente', class: 'bg-amber-100 text-amber-700 border-amber-200' }
    return { label: 'Sem Assinatura', class: 'bg-slate-100 text-slate-500 border-slate-200' }
}

const getDownloadUrl = (path) => {
    if (!path) return '#'
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    let cleanPath = path
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('static/')) {
        cleanPath = `armazenamento/${cleanPath}`
    }
    return `${baseUrl}/static/${cleanPath}`
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Ações
const openAssinaturas = (id) => {
    router.push(`/documentos/${id}/assinaturas`)
}

const openOriginal = (path) => {
    window.open(getDownloadUrl(path), '_blank')
}
</script>

<template>
    <div class="h-screen flex bg-slate-50 font-sans overflow-hidden">
        <Sidebar :escritorio="escritorio" :usuario="currentUser" :sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

        <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
            <!-- HEADER -->
            <header class="bg-white border-b border-slate-200 px-6 py-4 z-10">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <button @click="sidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-500">
                            <Folder class="h-6 w-6" />
                        </button>
                        <div>
                            <h1 class="text-xl font-black text-slate-900 flex items-center gap-2">
                                <Folder class="w-6 h-6 text-primary-600" /> Arquivos do Escritório
                            </h1>
                            <p class="text-xs text-slate-500 font-bold uppercase tracking-widest">Painel Global de Documentos</p>
                        </div>
                    </div>
                </div>
            </header>

            <div class="flex-1 flex overflow-hidden">
                <!-- CATEGORY SIDEBAR (INTERNAL) -->
                <aside class="w-64 bg-white border-r border-slate-200 hidden lg:flex flex-col p-4 gap-6">
                    <section class="space-y-1">
                        <h3 class="px-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3">Categorias</h3>
                        <button @click="activeCategory = 'todos'" :class="[activeCategory === 'todos' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50', 'w-full flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all']">
                            <Folder class="w-4 h-4 mr-3" /> Todos
                        </button>
                        <button @click="activeCategory = 'internos'" :class="[activeCategory === 'internos' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50', 'w-full flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all']">
                            <Building2 class="w-4 h-4 mr-3" /> Internos
                        </button>
                        <button @click="activeCategory = 'clientes'" :class="[activeCategory === 'clientes' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50', 'w-full flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all']">
                            <Users class="w-4 h-4 mr-3" /> Clientes
                        </button>
                        <button @click="activeCategory = 'processos'" :class="[activeCategory === 'processos' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50', 'w-full flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all']">
                            <Scale class="w-4 h-4 mr-3" /> Processos
                        </button>
                        <button @click="activeCategory = 'modelos'" :class="[activeCategory === 'modelos' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50', 'w-full flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all']">
                            <Wand2 class="w-4 h-4 mr-3 text-purple-500" /> Modelos
                        </button>
                    </section>

                    <section class="space-y-1">
                        <h3 class="px-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3">Assinaturas Digitais</h3>
                        <button @click="activeStatus = null" :class="[!activeStatus ? 'text-primary-600 bg-slate-50' : 'text-slate-500', 'w-full flex items-center justify-between px-4 py-2 text-xs font-bold rounded-lg']">
                            Qualquer Status <span class="w-2 h-2 rounded-full" :class="!activeStatus ? 'bg-primary-500' : 'bg-slate-200'"></span>
                        </button>
                        <button @click="activeStatus = 'Aguardando'" :class="[activeStatus === 'Aguardando' ? 'text-amber-600 bg-amber-50' : 'text-slate-500', 'w-full flex items-center justify-between px-4 py-2 text-xs font-bold rounded-lg']">
                            Aguardando <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                        </button>
                        <button @click="activeStatus = 'Parcial'" :class="[activeStatus === 'Parcial' ? 'text-amber-600 bg-amber-50' : 'text-slate-500', 'w-full flex items-center justify-between px-4 py-2 text-xs font-bold rounded-lg']">
                            Parcial <span class="w-2 h-2 rounded-full bg-amber-600"></span>
                        </button>
                        <button @click="activeStatus = 'Concluido'" :class="[activeStatus === 'Concluido' ? 'text-emerald-600 bg-emerald-50' : 'text-slate-500', 'w-full flex items-center justify-between px-4 py-2 text-xs font-bold rounded-lg']">
                            Assinados <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        </button>
                    </section>
                </aside>

                <!-- MAIN FILE LIST -->
                <main class="flex-1 overflow-y-auto p-4 sm:p-8">
                    <div class="max-w-6xl mx-auto space-y-6">
                        <!-- FILTERS BAR -->
                        <div class="flex flex-col sm:flex-row gap-4">
                            <div class="relative flex-1">
                                <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                                <input v-model="searchQuery" type="text" placeholder="Pesquisar por nome do arquivo ou cliente..." 
                                       class="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-medium text-sm shadow-sm" />
                            </div>
                            <button @click="fetchFiles" class="p-3 bg-white border border-slate-200 rounded-2xl hover:bg-slate-50 transition-all shadow-sm">
                                <RefreshCw :class="loading ? 'animate-spin' : ''" class="w-5 h-5 text-slate-500" />
                            </button>
                        </div>

                        <!-- LISTING -->
                        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
                            <RefreshCw class="h-10 w-10 text-primary-500 animate-spin mb-4" />
                            <p class="text-slate-500 font-bold uppercase tracking-widest text-xs">Sincronizando arquivos...</p>
                        </div>

                        <div v-else-if="files.length === 0" class="text-center py-24 bg-white rounded-3xl border border-slate-200 border-dashed">
                            <Folder class="h-12 w-12 text-slate-200 mx-auto mb-4" />
                            <h3 class="text-lg font-black text-slate-900">Nenhum arquivo encontrado</h3>
                            <p class="text-slate-400 text-sm font-medium">Tente ajustar seus filtros ou busca.</p>
                        </div>

                        <div v-else class="grid grid-cols-1 gap-3">
                            <div v-for="file in files" :key="file.id" 
                                 class="bg-white rounded-2xl border border-slate-200 p-4 flex items-center justify-between group hover:shadow-lg hover:border-primary-200 transition-all cursor-pointer shadow-sm">
                                <div class="flex items-center gap-4 min-w-0" @click="openOriginal(file.arquivo_path)">
                                    <div class="w-12 h-12 rounded-xl flex items-center justify-center border font-black text-[10px] tracking-tighter flex-shrink-0"
                                         :class="getExtensionColor(getFileExtension(file.arquivo_path))">
                                        {{ getFileExtension(file.arquivo_path) }}
                                    </div>
                                    <div class="min-w-0">
                                        <h3 class="text-slate-900 font-bold truncate group-hover:text-primary-600 transition-colors" :title="file.nome">{{ file.nome }}</h3>
                                        <div class="flex items-center gap-2 mt-1">
                                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ formatDate(file.data_criacao) }}</span>
                                            <span class="text-slate-200">•</span>
                                            <span v-if="file.is_modelo" class="text-[9px] font-black px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full border border-purple-100 uppercase">Modelo de Automação</span>
                                            <span v-else class="text-[9px] font-black px-2 py-0.5 bg-slate-50 text-slate-500 rounded-full border border-slate-100 uppercase">{{ file.cliente }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex items-center gap-2">
                                    <!-- Status Assinatura -->
                                    <div v-if="!file.is_modelo" class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border text-[10px] font-black uppercase tracking-tighter" :class="getStatusBadge(file.status_assinatura).class">
                                        <CheckCircle2 v-if="file.status_assinatura === 'Concluido'" class="w-3 h-3" />
                                        <Clock v-else class="w-3 h-3" />
                                        {{ getStatusBadge(file.status_assinatura).label }}
                                    </div>

                                    <!-- Ações -->
                                    <div class="flex items-center gap-1">
                                        <button v-if="!file.is_modelo" @click.stop="openAssinaturas(file.id)" class="p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all" title="Gerenciar Assinaturas">
                                            <PenTool class="w-5 h-5" />
                                        </button>
                                        <a :href="getDownloadUrl(file.arquivo_path)" target="_blank" download class="p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all" title="Download">
                                            <FileDown class="w-5 h-5" />
                                        </a>
                                        <div class="relative group/menu">
                                            <button class="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-all">
                                                <MoreVertical class="w-5 h-5" />
                                            </button>
                                            <div class="absolute right-0 top-full mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl py-1 z-20 hidden group-hover/menu:block">
                                                <button @click.stop="openOriginal(file.arquivo_path)" class="w-full text-left px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 flex items-center gap-2">
                                                    <Eye class="w-4 h-4" /> Visualizar
                                                </button>
                                                <button v-if="!file.is_modelo" @click.stop="openAssinaturas(file.id)" class="w-full text-left px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 flex items-center gap-2 font-bold">
                                                    <CheckCircle2 class="w-4 h-4 text-emerald-500" /> Assinaturas
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
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
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
</style>
