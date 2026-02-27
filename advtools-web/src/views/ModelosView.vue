<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  FileText, 
  UploadCloud, 
  Trash2, 
  RefreshCw, 
  Search,
  Tag,
  Copy,
  CheckCircle2,
  FileDown
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

// Estado
const modelos = ref([])
const loading = ref(true)
const searchQuery = ref('')
const sidebarOpen = ref(false)

// Estado Upload
const isUploading = ref(false)
const fileInput = ref(null)
const replaceInput = ref(null)
const replacingId = ref(null)

// Notificações
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (msg, type = 'success') => {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

// ==========================================
// LISTA DE TAGS DISPONÍVEIS
// ==========================================
const tags = [
  { group: 'Dados do Cliente', items: [
    { label: 'Nome', tag: '{{ cliente_nome }}' },
    { label: 'Documento (CPF/CNPJ)', tag: '{{ cliente_doc }}' },
    { label: 'Endereço', tag: '{{ cliente_endereco }}' },
    { label: 'Bairro', tag: '{{ cliente_bairro }}' },
    { label: 'Cidade', tag: '{{ cliente_cidade }}' },
    { label: 'Estado', tag: '{{ cliente_uf }}' },
    { label: 'CEP', tag: '{{ cliente_cep }}' },
    { label: 'E-mail', tag: '{{ cliente_email }}' },
    { label: 'Nacionalidade', tag: '{{ cliente_nacionalidade }}' },
    { label: 'Estado Civil', tag: '{{ cliente_estado_civil }}' },
    { label: 'Profissão', tag: '{{ cliente_profissao }}' },
    { label: 'RG', tag: '{{ cliente_rg }}' },
    { label: 'Data Nascimento', tag: '{{ cliente_data_nascimento }}' },
  ]},
  { group: 'Dados do Serviço/Processo', items: [
    { label: 'Tipo', tag: '{{ servico_tipo }}' },
    { label: 'Descrição/Objeto', tag: '{{ descricao }}' },
    { label: 'Valor Total', tag: '{{ valor_total }}' },
    { label: 'Forma de Pagamento', tag: '{{ forma_pagamento }}' },
    { label: 'Detalhes Pagamento', tag: '{{ detalhes_pagamento }}' },
    { label: 'Qtd. Parcelas', tag: '{{ qtd_parcelas }}' },
  ]},
  { group: 'Datas', items: [
    { label: 'Data Hoje', tag: '{{ data_hoje }}' },
    { label: 'Ano Atual', tag: '{{ ano_atual }}' },
    { label: 'Data Extenso', tag: '{{ data_extenso }}' },
  ]},
  { group: 'Inteligência Artificial', items: [
    { label: 'Conteúdo IA', tag: '{{ conteudo_ia }}' },
    { label: 'Cláusulas Extras', tag: '{{ clausulas_extras }}' },
  ]}
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

// ==========================================
// API CALLS
// ==========================================
const loadModelos = async () => {
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
  if (!file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)
  // Remover a extensão para o nome de exibição
  formData.append('nome', file.name.replace('.docx', ''))

  isUploading.value = true
  try {
    const res = await apiFetch('/api/modelos', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Erro ao enviar modelo')
    }
    showToast('Modelo enviado com sucesso')
    loadModelos()
  } catch (err) {
    showToast(err.message || 'Erro ao enviar modelo', 'error')
  } finally {
    isUploading.value = false
    event.target.value = '' // reset
  }
}

const handleReplaceUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)

  isUploading.value = true
  try {
    const res = await apiFetch(`/api/modelos/${replacingId.value}`, {
      method: 'PUT',
      body: formData
    })
    if (!res.ok) {
        throw new Error('Erro ao substituir arquivo')
    }
    showToast('Arquivo substituído com sucesso')
    loadModelos()
  } catch (err) {
    showToast('Erro ao substituir arquivo', 'error')
  } finally {
    isUploading.value = false
    replacingId.value = null
    event.target.value = '' // reset
  }
}

const deleteModelo = async (id) => {
  if (!confirm('Tem certeza que deseja excluir este modelo permanentemente?')) return
  
  try {
    const res = await apiFetch(`/api/modelos/${id}`, { method: 'DELETE' })
    if(!res.ok) throw new Error('Erro')
    showToast('Modelo excluído com sucesso')
    loadModelos()
  } catch (err) {
    showToast('Erro ao excluir modelo', 'error')
  }
}

const getDownloadUrl = (path) => {
  return `http://localhost:8000/static/${path}`
}

onMounted(() => {
  // Simular usuário logado e escritório atual (Pegar da store ou context futuramente se não via API)
  loadModelos()
})

const filteredModelos = computed(() => {
  if (!searchQuery.value) return modelos.value
  const query = searchQuery.value.toLowerCase()
  return modelos.value.filter(m => m.nome.toLowerCase().includes(query))
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>

<template>
  <div class="h-screen flex bg-slate-50 font-sans overflow-hidden">
    <!-- Sidebar Component -->
    <Sidebar :sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <!-- HEADER -->
      <header class="bg-white border-b border-slate-200 px-8 py-5 flex items-center justify-between z-10 sticky top-0">
        <div class="flex items-center gap-4">
          <button @click="sidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-500 hover:text-slate-900 focus:outline-none">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div>
            <h1 class="text-2xl font-black text-slate-900 tracking-tight">Modelos de Docs</h1>
            <p class="text-sm text-slate-500 font-medium">Gerencie templates .docx e tags para automação</p>
          </div>
        </div>
      </header>

      <!-- MAIN CONTENT -->
      <div class="flex-1 flex overflow-hidden">
        
        <!-- Lista de Modelos (Esquerda) -->
        <main class="flex-1 overflow-y-auto p-8">
          
          <div class="max-w-4xl mx-auto space-y-6">
            <!-- Barra de Ferramentas -->
            <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
              <div class="relative w-full sm:w-96">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input v-model="searchQuery" 
                       type="text" 
                       placeholder="Pesquisar modelos..." 
                       class="w-full pl-10 pr-4 py-2 bg-slate-50 border-0 rounded-xl focus:ring-2 focus:ring-primary-500 transition-shadow text-sm font-medium" />
              </div>

              <div class="flex gap-3 w-full sm:w-auto">
                <input type="file" ref="fileInput" accept=".docx" class="hidden" @change="handleFileUpload" />
                <button @click="triggerUpload" :disabled="isUploading"
                        class="w-full sm:w-auto px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-bold rounded-xl shadow-sm hover:shadow-md transition-all flex items-center justify-center disabled:opacity-50">
                  <UploadCloud class="w-4 h-4 mr-2" />
                  {{ isUploading ? 'Enviando...' : 'Novo Modelo (.docx)' }}
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col flex-1 items-center justify-center p-12">
              <RefreshCw class="h-8 w-8 text-primary-500 animate-spin mb-4" />
              <p class="text-slate-500 font-medium">Carregando modelos...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="filteredModelos.length === 0" class="text-center bg-white rounded-2xl border border-slate-200 border-dashed p-12">
              <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText class="h-8 w-8 text-slate-400" />
              </div>
              <h3 class="text-lg font-bold text-slate-900 mb-2">Nenhum modelo encontrado</h3>
              <p class="text-slate-500 mb-6 max-w-sm mx-auto">Faça o upload do seu primeiro arquivo padrão em .docx para utilizá-lo na geração de contratos e relatórios.</p>
              <button @click="triggerUpload" class="px-4 py-2 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 transition-colors">
                Enviar Primeiro Modelo
              </button>
            </div>

            <!-- Grid de Modelos -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              
              <!-- Input oculto para substituir -->
              <input type="file" ref="replaceInput" accept=".docx" class="hidden" @change="handleReplaceUpload" />
              
              <div v-for="modelo in filteredModelos" :key="modelo.id" 
                   class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-primary-200 transition-all group flex flex-col">
                
                <div class="p-5 flex items-start gap-4">
                  <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileText class="w-6 h-6" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <h3 class="text-slate-900 font-bold truncate text-base" :title="modelo.nome">{{ modelo.nome }}</h3>
                    <p class="text-xs text-slate-500 mt-1">Carregado em: {{ formatDate(modelo.data_criacao) }}</p>
                  </div>
                </div>

                <div class="mt-auto px-5 pb-5 pt-3 border-t border-slate-50 flex items-center justify-between bg-slate-50/50 rounded-b-2xl">
                  <div class="flex gap-2">
                    <a :href="getDownloadUrl(modelo.arquivo_path)" target="_blank" download
                       class="p-2 text-slate-400 hover:text-primary-600 hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200 shadow-sm hover:shadow" 
                       title="Baixar Modelo">
                      <FileDown class="w-4 h-4" />
                    </a>
                    <button @click="triggerReplace(modelo.id)" 
                            class="p-2 text-slate-400 hover:text-amber-500 hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200 shadow-sm hover:shadow" 
                            title="Substituir Arquivo">
                      <RefreshCw class="w-4 h-4" />
                    </button>
                  </div>
                  <button @click="deleteModelo(modelo.id)" 
                          class="p-2 text-slate-400 hover:text-red-500 hover:bg-white rounded-lg transition-colors border border-transparent hover:border-red-100 shadow-sm hover:shadow" 
                          title="Excluir Modelo">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

          </div>
        </main>

        <!-- Sidebar de TAGS (Direita) -->
        <aside class="w-80 border-l border-slate-200 bg-white flex flex-col flex-shrink-0 hidden xl:flex">
          <div class="px-6 py-5 border-b border-slate-200 bg-slate-50/50">
            <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
              <Tag class="w-4 h-4 text-primary-500" />
              Tags Disponíveis
            </h2>
            <p class="text-xs text-slate-500 mt-1 leading-relaxed">
              Clique numa tag para copiar. Cole nos seus documentos Word e o sistema preencherá os dados automaticamente.
            </p>
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-6">
            <div v-for="grupo in tags" :key="grupo.group" class="space-y-3">
              <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest pl-2">
                {{ grupo.group }}
              </h3>
              
              <div class="space-y-1">
                <button v-for="item in grupo.items" :key="item.tag"
                        @click="copyToClipboard(item.tag)"
                        class="w-full flex flex-col items-start px-3 py-2 rounded-xl text-left hover:bg-primary-50 group transition-colors focus:outline-none">
                  <div class="w-full flex items-center justify-between">
                    <span class="text-sm font-semibold text-slate-700 group-hover:text-primary-700">{{ item.label }}</span>
                    <Copy v-if="copiedTag !== item.tag" class="w-3.5 h-3.5 text-slate-300 group-hover:text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CheckCircle2 v-else class="w-3.5 h-3.5 text-emerald-500" />
                  </div>
                  <code :class="['text-xs mt-1 px-1.5 py-0.5 rounded font-mono transition-colors', 
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

    <!-- Toast Component Refinado -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="toast.show" 
           class="fixed bottom-6 right-6 z-50 rounded-xl max-w-sm w-full shadow-2xl p-4 flex items-center gap-3"
           :class="toast.type === 'error' ? 'bg-red-50 border border-red-100 text-red-800' : 'bg-slate-900 text-white'">
        <CheckCircle2 v-if="toast.type !== 'error'" class="h-5 w-5 text-emerald-400" />
        <p class="text-sm font-medium">{{ toast.message }}</p>
      </div>
    </Transition>

  </div>
</template>
