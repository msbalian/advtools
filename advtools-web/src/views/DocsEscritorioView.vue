<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  FileText, 
  UploadCloud, 
  Trash2, 
  RefreshCw, 
  Search,
  Tag,
  Copy,
  CheckCircle2,
  Plus,
  PenTool,
  FileSpreadsheet,
  FileCode,
  FileDigit,
  FileBox,
  FileType,
  FileCheck,
  FileJson,
  FileVideo,
  FileImage,
  Music,
  FileDown,
  Building2,
  Wand2
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

const route = useRoute()
const router = useRouter()

// Estado Geral
const currentTab = ref(route.query.tab || 'modelos') // 'modelos' ou 'internos'
const loading = ref(true)
const searchQuery = ref('')
const sidebarOpen = ref(false)
const currentUser = ref(null)
const escritorio = ref(null)
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

// ==========================================
// ESTADO MODELOS
// ==========================================
const modelos = ref([])
const loadModelos = async () => {
  if (currentTab.value !== 'modelos') return
  loading.value = true
  try {
    const res = await apiFetch('/api/modelos')
    const data = await res.json()
    modelos.value = data
  } catch (err) {
    showToast('Erro ao carregar modelos', 'error')
  } finally {
    loading.value = false
  }
}

// ==========================================
// ESTADO DOCUMENTOS INTERNOS
// ==========================================
const documentosInternos = ref([])
const loadDocumentosInternos = async () => {
  if (currentTab.value !== 'internos') return
  loading.value = true
  try {
    const res = await apiFetch('/api/documentos/escritorio')
    if (res.ok) {
        documentosInternos.value = await res.json()
    }
  } catch (err) {
    showToast('Erro ao carregar documentos', 'error')
  } finally {
    loading.value = false
  }
}

// ==========================================
// ESTADO UPLOAD / GESTÃO
// ==========================================
const isUploading = ref(false)
const fileInput = ref(null)
const replaceInput = ref(null)
const replacingId = ref(null)

const triggerUpload = () => {
  fileInput.value.click()
}

const triggerReplace = (id) => {
  replacingId.value = id
  replaceInput.value.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const isModelo = currentTab.value === 'modelos'
  if (isModelo && !file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos para modelos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('nome', file.name.split('.').slice(0, -1).join('.'))

  isUploading.value = true
  try {
    const endpoint = isModelo ? '/api/modelos' : '/api/documentos/escritorio'
    const res = await apiFetch(endpoint, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Erro ao enviar arquivo')
    }
    showToast('Arquivo enviado com sucesso')
    if (isModelo) loadModelos() 
    else loadDocumentosInternos()
  } catch (err) {
    showToast(err.message || 'Erro ao enviar arquivo', 'error')
  } finally {
    isUploading.value = false
    event.target.value = '' 
  }
}

const handleReplaceUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (currentTab.value === 'modelos' && !file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos para modelos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)

  isUploading.value = true
  try {
    const res = await apiFetch(`/api/documentos/${replacingId.value}`, {
      method: 'PUT',
      body: formData
    })
    if (!res.ok) throw new Error('Erro ao substituir arquivo')
    
    showToast('Arquivo substituído com sucesso')
    if (currentTab.value === 'modelos') loadModelos()
    else loadDocumentosInternos()
  } catch (err) {
    showToast('Erro ao substituir arquivo', 'error')
  } finally {
    isUploading.value = false
    replacingId.value = null
    event.target.value = ''
  }
}

const deleteItem = async (id) => {
  if (!confirm('Tem certeza que deseja excluir permanentemente?')) return
  
  try {
    const endpoint = currentTab.value === 'modelos' ? `/api/modelos/${id}` : `/api/documentos/${id}`
    const res = await apiFetch(endpoint, { method: 'DELETE' })
    if(!res.ok) throw new Error('Erro')
    showToast('Excluído com sucesso')
    if (currentTab.value === 'modelos') loadModelos()
    else loadDocumentosInternos()
  } catch (err) {
    showToast('Erro ao excluir', 'error')
  }
}

// ==========================================
// TAGS E AUXILIARES
// ==========================================
const tags = [
  { group: 'Dados do Escritório', items: [
    { label: 'Nome do Escritório', tag: '{{ escritorio_nome }}' },
    { label: 'CNPJ/CPF Escritório', tag: '{{ escritorio_doc }}' },
  ]},
  { group: 'Dados do Cliente', items: [
    { label: 'Nome', tag: '{{ cliente_nome }}' },
    { label: 'Documento (CPF/CNPJ)', tag: '{{ cliente_doc }}' },
    { label: 'Endereço', tag: '{{ cliente_endereco }}' },
    { label: 'E-mail', tag: '{{ cliente_email }}' },
    { label: 'Profissão', tag: '{{ cliente_profissao }}' },
  ]},
  { group: 'Datas e Outros', items: [
    { label: 'Data Hoje', tag: '{{ data_hoje }}' },
    { label: 'Data Extenso', tag: '{{ data_extenso }}' },
    { label: 'IA Conteúdo', tag: '{{ conteudo_ia }}' },
  ]},
]

const copiedTag = ref('')
const copyToClipboard = async (tag) => {
  try {
    await navigator.clipboard.writeText(tag)
    copiedTag.value = tag
    setTimeout(() => copiedTag.value = '', 2000)
  } catch (err) {
    showToast('Erro ao copiar tag', 'error')
  }
}

const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (msg, type = 'success') => {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const getDownloadUrl = (path) => {
    if (!path) return '#'
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    let cleanPath = path
    // Suporte a arquivos legados sem o prefixo armazenamento/
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('static/')) {
        cleanPath = `armazenamento/${cleanPath}`
    }
    return `${baseUrl}/static/${cleanPath}`
}

const filteredItems = computed(() => {
  const items = currentTab.value === 'modelos' ? modelos.value : documentosInternos.value
  if (!searchQuery.value) return items
  const query = searchQuery.value.toLowerCase()
  return items.filter(m => m.nome.toLowerCase().includes(query))
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const irParaRedator = () => {
    router.push('/redator?context=escritorio')
}

const irParaAssinaturas = (id) => {
    router.push(`/documentos/${id}/assinaturas`)
}

const getStatusClass = (status) => {
    if (status === 'Concluido') return 'bg-emerald-100 text-emerald-700'
    if (status === 'Parcial' || status === 'Pendente') return 'bg-amber-100 text-amber-700'
    return 'bg-slate-100 text-slate-600'
}

const getFileExtension = (path) => {
    if (!path) return 'FILE'
    const parts = path.split('.')
    return parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

const getExtensionColor = (ext) => {
    const colors = {
        'PDF': 'bg-red-50 text-red-600 border-red-100',
        'DOCX': 'bg-blue-50 text-blue-600 border-blue-100',
        'DOC': 'bg-blue-50 text-blue-600 border-blue-100',
        'XLSX': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'XLS': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'CSV': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'TXT': 'bg-slate-50 text-slate-600 border-slate-100',
        'PNG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPEG': 'bg-purple-50 text-purple-600 border-purple-100',
        'ZIP': 'bg-amber-50 text-amber-600 border-amber-100',
        'RAR': 'bg-amber-50 text-amber-600 border-amber-100'
    }
    return colors[ext] || 'bg-slate-50 text-slate-500 border-slate-100'
}

onMounted(() => {
  if (currentTab.value === 'modelos') loadModelos()
  else loadDocumentosInternos()
  carregarDadosBase()
})
</script>

<template>
  <div class="h-screen flex bg-slate-50 font-sans overflow-hidden">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" :sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <!-- HEADER -->
      <header class="bg-white border-b border-slate-200 px-8 py-5 flex flex-col gap-4 z-10">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-500 hover:text-slate-900 focus:outline-none">
                <FileText class="h-6 w-6" />
            </button>
            <div>
                <h1 class="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                    <Building2 class="w-6 h-6 text-primary-600" /> Docs do Escritório
                </h1>
                <p class="text-sm text-slate-500 font-medium">Gestão centralizada de modelos e documentos internos</p>
            </div>
            </div>
            
            <div class="flex gap-3">
                <button @click="irParaRedator" class="hidden sm:flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-xl text-sm font-bold hover:bg-indigo-100 transition-colors">
                    <Wand2 class="w-4 h-4" /> Redator Inteligente
                </button>
                <button @click="triggerUpload" :disabled="isUploading" class="flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-bold shadow-sm hover:shadow-md hover:bg-primary-700 transition-all disabled:opacity-50">
                    <Plus class="w-4 h-4" /> {{ currentTab === 'modelos' ? 'Novo Modelo' : 'Upload Documento' }}
                </button>
            </div>
        </div>

        <!-- TABS -->
        <div class="flex gap-8 border-b border-slate-100 -mb-5 pt-2">
            <button @click="currentTab = 'modelos'; loadModelos()" 
                    :class="[currentTab === 'modelos' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-400 hover:text-slate-600', 'pb-4 border-b-2 font-bold text-sm transition-all']">
                Modelos de Automação
            </button>
            <button @click="currentTab = 'internos'; loadDocumentosInternos()" 
                    :class="[currentTab === 'internos' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-400 hover:text-slate-600', 'pb-4 border-b-2 font-bold text-sm transition-all']">
                Documentos Internos
            </button>
        </div>
      </header>

      <!-- CONTENT -->
      <div class="flex-1 flex overflow-hidden">
        <main class="flex-1 overflow-y-auto p-8">
          <div class="max-w-5xl mx-auto space-y-6">
            
            <!-- Hidden Inputs -->
            <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" />
            <input type="file" ref="replaceInput" class="hidden" @change="handleReplaceUpload" />

            <!-- Busca -->
            <div class="relative max-w-md">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input v-model="searchQuery" type="text" :placeholder="currentTab === 'modelos' ? 'Pesquisar modelos...' : 'Pesquisar documentos...'" 
                       class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 transition-shadow text-sm font-medium" />
            </div>

            <!-- Grid -->
            <div v-if="loading" class="flex flex-col items-center justify-center py-20">
                <RefreshCw class="h-8 w-8 text-primary-500 animate-spin mb-4" />
                <p class="text-slate-500 font-medium">Carregando...</p>
            </div>

            <div v-else-if="filteredItems.length === 0" class="text-center bg-white rounded-2xl border border-slate-200 border-dashed p-16">
                <FileText class="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 class="text-xl font-bold text-slate-900 mb-2">Nada por aqui ainda</h3>
                <p class="text-slate-500 mb-8 max-w-sm mx-auto">Comece enviando arquivos para organizar os documentos do seu escritório.</p>
                <button @click="triggerUpload" class="px-6 py-2.5 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-colors">
                    {{ currentTab === 'modelos' ? 'Enviar Primeiro Modelo' : 'Fazer Primeiro Upload' }}
                </button>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div v-for="item in filteredItems" :key="item.id" 
                     class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-primary-200 transition-all group flex flex-col overflow-hidden">
                    
                    <div class="p-5 flex items-start gap-4">
                        <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 border font-black text-[10px] tracking-tighter"
                             :class="getExtensionColor(getFileExtension(item.arquivo_path))">
                            {{ getFileExtension(item.arquivo_path) }}
                        </div>
                        <div class="min-w-0 flex-1">
                            <div class="flex items-center gap-2 mb-0.5">
                                <h3 class="text-slate-900 font-bold truncate text-base" :title="item.nome">{{ item.nome }}</h3>
                                <span v-if="item.signatarios?.length > 0" 
                                      :class="['text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider', getStatusClass(item.status_assinatura)]">
                                    {{ item.status_assinatura }}
                                </span>
                            </div>
                            <p class="text-xs text-slate-400 font-medium">Enviado em {{ formatDate(item.data_criacao) }}</p>
                        </div>
                    </div>

                    <div class="mt-auto px-5 py-4 border-t border-slate-50 bg-slate-50/30 flex items-center justify-between">
                        <div class="flex gap-1.5">
                            <a :href="getDownloadUrl(item.arquivo_path)" target="_blank" download class="p-2 text-slate-400 hover:text-primary-600 hover:bg-white rounded-lg transition-all border border-transparent hover:border-slate-100 shadow-none hover:shadow-sm" title="Download Original">
                                <FileDown class="w-4 h-4" />
                            </a>
                            <a v-if="item.status_assinatura === 'Concluido' && item.arquivo_assinado_path" 
                               :href="getDownloadUrl(item.arquivo_assinado_path)" target="_blank" download class="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all border border-transparent hover:border-emerald-100 shadow-none hover:shadow-sm" title="Download Doc Assinado">
                                <CheckCircle2 class="w-4 h-4" />
                            </a>
                            <button v-if="currentTab === 'internos'" @click="irParaAssinaturas(item.id)" class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-lg transition-all border border-transparent hover:border-slate-100 shadow-none hover:shadow-sm" title="Gerenciar Assinaturas">
                                <PenTool class="w-4 h-4" />
                            </button>
                            <button v-if="item.status_assinatura !== 'Parcial' && item.status_assinatura !== 'Concluido'" 
                                    @click="triggerReplace(item.id)" 
                                    class="p-2 text-slate-400 hover:text-amber-500 hover:bg-white rounded-lg transition-all border border-transparent hover:border-slate-100 shadow-none hover:shadow-sm" 
                                    title="Substituir Arquivo">
                                <RefreshCw class="w-4 h-4" />
                            </button>
                        </div>
                        <button @click="deleteItem(item.id)" class="p-2 text-slate-400 hover:text-red-500 hover:bg-white rounded-lg transition-all border border-transparent hover:border-red-50 shadow-none hover:shadow-sm" title="Excluir">
                            <Trash2 class="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
          </div>
        </main>

        <!-- Sidebar TAGS -->
        <aside v-if="currentTab === 'modelos'" class="w-80 border-l border-slate-200 bg-white flex flex-col flex-shrink-0 hidden xl:flex">
          <div class="px-6 py-6 border-b border-slate-100 bg-slate-50/30">
            <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
              <Tag class="w-4 h-4 text-primary-500" /> Tags de Automação
            </h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed font-medium">
              Cole estas tags no seu documento Word. O Redator Inteligente as preencherá automaticamente.
            </p>
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-8">
            <div v-for="grupo in tags" :key="grupo.group" class="space-y-4">
              <h3 class="text-[10px] font-black text-slate-300 uppercase tracking-widest px-2">
                {{ grupo.group }}
              </h3>
              <div class="space-y-1">
                <button v-for="item in grupo.items" :key="item.tag" @click="copyToClipboard(item.tag)"
                        class="w-full flex flex-col items-start px-3 py-2.5 rounded-xl text-left hover:bg-primary-50 group transition-all">
                  <div class="w-full flex items-center justify-between">
                    <span class="text-sm font-bold text-slate-700 group-hover:text-primary-700">{{ item.label }}</span>
                    <CheckCircle2 v-if="copiedTag === item.tag" class="w-3.5 h-3.5 text-emerald-500" />
                    <Copy v-else class="w-3.5 h-3.5 text-slate-300 group-hover:text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <code :class="['text-[10px] mt-1.5 px-2 py-0.5 rounded font-mono', 
                                 copiedTag === item.tag ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500 group-hover:bg-primary-100 group-hover:text-primary-600']">
                    {{ item.tag }}
                  </code>
                </button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- TOAST -->
    <Transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0" enter-to-class="translate-y-0 opacity-100" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="toast.show" class="fixed bottom-8 right-8 z-50 rounded-2xl shadow-2xl p-4 flex items-center gap-3 min-w-[300px]"
           :class="toast.type === 'error' ? 'bg-red-50 border border-red-100 text-red-800' : 'bg-slate-900 text-white'">
        <CheckCircle2 v-if="toast.type !== 'error'" class="h-5 w-5 text-emerald-400" />
        <p class="text-sm font-bold">{{ toast.message }}</p>
      </div>
    </Transition>
  </div>
</template>
