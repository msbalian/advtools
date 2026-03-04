<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import { 
    Menu as MenuIcon, 
    User, 
    Settings, 
    LogOut, 
    ChevronDown, 
    Wand2, 
    Search,
    FileText,
    Sparkles,
    Check,
    AlertCircle,
    CheckCircle2,
    Building2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const notification = ref({ show: false, message: '', type: 'success' })
const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const showProfileMenu = ref(false)
const currentUser = ref(null)
const escritorio = ref(null)
const sidebarOpen = ref(false)

const loadBasicData = async () => {
    try {
        const [resUser, resEsc] = await Promise.all([
            apiFetch('/api/me'),
            apiFetch('/api/escritorio')
        ])
        if (resUser.ok) currentUser.value = await resUser.json()
        if (resEsc.ok) escritorio.value = await resEsc.json()
    } catch (e) {
        console.error("Erro básico", e)
    }
}

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

// ========================
// REDATOR STATE
// ========================
const formData = ref({
    cliente_id: '',
    modelo_id: '',
    titulo_documento: '',
    usar_ia: false,
    instrucoes_ia: ''
})

const isGenerating = ref(false)

// Dados do Autocomplete de Cliente
const clienteQuery = ref('')
const clientesEncontrados = ref([])
const clienteSelecionado = ref(null)
const isLoadingClientes = ref(false)
const showClienteDropdown = ref(false)

// Busca debounced para clientes
let searchTimeout = null
watch(clienteQuery, (newVal) => {
    if (clienteSelecionado.value && clienteSelecionado.value.nome === newVal) return
    
    showClienteDropdown.value = true
    if (!newVal || newVal.length < 2) {
        clientesEncontrados.value = []
        return
    }

    clearTimeout(searchTimeout)
    isLoadingClientes.value = true
    searchTimeout = setTimeout(async () => {
        try {
            // Em uma API real seria /api/clientes?busca=...
            // Por enquanto vamos puxar todos e filtrar no frontend para simplicidade
            const res = await apiFetch(`/api/clientes`)
            if (res.ok) {
                const all = await res.json()
                const queryLower = newVal.toLowerCase()
                clientesEncontrados.value = all.filter(c => 
                    c.nome.toLowerCase().includes(queryLower) || 
                    (c.documento && c.documento.includes(queryLower))
                )
            }
        } catch (e) {
            console.error(e)
        } finally {
            isLoadingClientes.value = false
        }
    }, 400)
})

const selecionarCliente = (cliente) => {
    clienteSelecionado.value = cliente
    clienteQuery.value = cliente.nome
    formData.value.cliente_id = cliente.id // Note: cliente.id will be null for Office
    showClienteDropdown.value = false
}

// Opção especial para o próprio escritório
const opcaoEscritorio = computed(() => {
    if (!escritorio.value) return null
    return {
        id: null,
        nome: "O Próprio Escritório",
        documento: escritorio.value.documento || "Documento Interno",
        isOffice: true
    }
})

// Se veio parametro na rota (da Dashboard do Cliente)
const prefillCliente = async (clienteId) => {
    try {
        const res = await apiFetch(`/api/clientes/${clienteId}`)
        if (res.ok) {
            const cliente = await res.json()
            selecionarCliente(cliente)
        }
    } catch (e) {
        console.error("Erro ao preencher cliente", e)
    }
}

// Busca de Modelos
const modelos = ref([])
const loadModelos = async () => {
    try {
        const res = await apiFetch('/api/modelos')
        if (res.ok) {
            modelos.value = await res.json()
        }
    } catch (e) {
        console.error(e)
    }
}

// Ao selecionar modelo, preencher título sugestão
watch(() => formData.value.modelo_id, (newVal) => {
    if (newVal) {
        const mod = modelos.value.find(m => m.id === newVal)
        if (mod && clienteSelecionado.value && !formData.value.titulo_documento) {
            formData.value.titulo_documento = `${mod.nome.replace('.docx', '')} - ${clienteSelecionado.value.nome}`
        }
    }
})

// Gerar Documento
const handleGenerate = async () => {
    if (formData.value.cliente_id === undefined || !formData.value.modelo_id || !formData.value.titulo_documento) {
        // Agora cliente_id pode ser null, mas não indefinido
    }

    if (!formData.value.modelo_id || !formData.value.titulo_documento) {
        showMessage("Preencha modelo e título.", "error")
        return
    }

    isGenerating.value = true
    try {
        const payload = { ...formData.value }
        // Se cliente_id for nulo, o backend entende como escritório
        
        const response = await apiFetch('/api/redator/gerar', {
            method: 'POST',
            body: JSON.stringify(payload)
        })

        if (!response.ok) {
            let errorMsg = 'Erro ao gerar documento'
            try {
                const err = await response.json()
                errorMsg = err.detail || errorMsg
            } catch (jsonErr) {
                errorMsg = `Erro do Servidor (${response.status})`
            }
            throw new Error(errorMsg)
        }

        showMessage("Documento gerado com sucesso!")
        
        // Redireciona para o local apropriado
        setTimeout(() => {
            if (payload.cliente_id) {
                router.push(`/clientes/${payload.cliente_id}`)
            } else {
                router.push('/modelos') // Volta para Docs do Escritório (aba internos carregará por lá)
            }
        }, 1500)
        
    } catch (e) {
        showMessage(e.message, "error")
    } finally {
        isGenerating.value = false
    }
}

// Initialization
onMounted(async () => {
    await loadBasicData()
    await loadModelos()

    if (route.query.cliente) {
        await prefillCliente(route.query.cliente)
    } else if (route.query.context === 'escritorio') {
        // Seleciona o escritório por padrão se vier da área interna
        if (opcaoEscritorio.value) {
            selecionarCliente(opcaoEscritorio.value)
        }
    }
})

</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Top Header -->
        <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-10 sticky top-0">
            <div class="flex items-center gap-4">
                <button @click="sidebarOpen = true" class="md:hidden p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-500 focus:outline-none">
                    <MenuIcon class="w-6 h-6" />
                </button>
                <h1 class="text-xl font-bold border-b-2 border-transparent text-slate-800 flex items-center gap-2">
                    <Wand2 class="w-5 h-5 text-purple-600" /> Redator Inteligente
                </h1>
            </div>

            <!-- Profile Dropdown -->
            <div class="relative ml-2">
            <button @click="showProfileMenu = !showProfileMenu" @blur="setTimeout(() => showProfileMenu = false, 200)" class="flex items-center gap-2 p-1.5 rounded-full hover:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700">
                <span class="text-xs font-bold">{{ currentUser ? currentUser.nome.charAt(0).toUpperCase() : 'U' }}</span>
                </div>
                <span class="hidden md:block text-sm font-medium text-slate-700">{{ currentUser ? currentUser.nome : 'Carregando...' }}</span>
                <ChevronDown class="hidden md:block w-4 h-4 text-slate-400" />
            </button>
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 focus:outline-none z-50 animate-fade-in-up">
                <div class="py-1">
                <button @click="handleLogout" class="group flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                    <LogOut class="mr-3 h-4 w-4 text-red-500 group-hover:text-red-600" /> Sair
                </button>
                </div>
            </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto w-full">
            
            <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden mt-4">
                <div class="bg-gradient-to-r from-purple-700 to-indigo-600 px-6 py-8 text-center">
                    <Wand2 class="w-12 h-12 text-purple-200 mx-auto mb-3" />
                    <h2 class="text-2xl font-bold text-white mb-2">Geração de Documentos</h2>
                    <p class="text-purple-100 max-w-lg mx-auto text-sm">Crie procurações, contratos e petições automaticamente usando seus modelos pré-cadastrados e os dados do cliente.</p>
                </div>
                
                <div class="p-6 sm:p-8 space-y-8">
                    
                    <!-- Passo 1: O Cliente -->
                    <div class="space-y-4">
                        <div class="flex items-center gap-2 border-b border-slate-100 pb-2">
                            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-700 font-bold text-xs">1</span>
                            <h3 class="font-semibold text-slate-900 text-lg">Para quem é o documento? *</h3>
                        </div>
                        
                        <div class="relative">
                            <label class="block text-sm font-medium leading-6 text-slate-900 mb-1">Buscar Cliente</label>
                            <div class="relative">
                                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                    <Search class="h-4 w-4 text-slate-400" aria-hidden="true" />
                                </div>
                                <input 
                                    type="text" 
                                    v-model="clienteQuery" 
                                    @focus="showClienteDropdown = true"
                                    class="block w-full rounded-xl border-0 py-2.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6 transition-all" 
                                    placeholder="Digite o nome, CPF ou CNPJ..." 
                                />
                                <div v-if="isLoadingClientes" class="absolute inset-y-0 right-0 flex items-center pr-3">
                                    <div class="animate-spin h-4 w-4 border-2 border-slate-400 border-t-transparent rounded-full"></div>
                                </div>
                            </div>
                            
                            <!-- Dropdown de Resultados -->
                            <div v-if="showClienteDropdown" class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-xl bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 sm:text-sm shadow-2xl">
                                <ul>
                                    <!-- Opção Escritório sempre disponível ou filtrada -->
                                    <li v-if="opcaoEscritorio && (!clienteQuery || opcaoEscritorio.nome.toLowerCase().includes(clienteQuery.toLowerCase()))" 
                                        @click="selecionarCliente(opcaoEscritorio)" 
                                        class="relative cursor-pointer select-none py-2.5 pl-3 pr-9 border-b border-slate-50 hover:bg-purple-50 text-slate-900 group">
                                        <div class="flex items-center">
                                            <Building2 class="w-4 h-4 text-purple-600 mr-2" />
                                            <span class="ml-1 truncate font-bold text-purple-700">{{ opcaoEscritorio.nome }}</span>
                                            <span class="ml-2 truncate text-xs text-slate-400">(Documento Interno)</span>
                                        </div>
                                    </li>

                                    <li v-for="c in clientesEncontrados" :key="c.id" @click="selecionarCliente(c)" class="relative cursor-pointer select-none py-2 pl-3 pr-9 hover:bg-purple-50 text-slate-900 group">
                                        <div class="flex items-center">
                                            <span :class="['ml-3 truncate font-medium group-hover:text-purple-700']">{{ c.nome }}</span>
                                            <span class="ml-2 truncate text-xs text-slate-500">{{ c.documento }}</span>
                                        </div>
                                        <span v-if="clienteSelecionado && clienteSelecionado.id === c.id && !clienteSelecionado.isOffice" class="absolute inset-y-0 right-0 flex items-center pr-4 text-purple-600">
                                            <Check class="h-4 w-4" />
                                        </span>
                                    </li>
                                </ul>
                                <div v-if="(!clientesEncontrados || clientesEncontrados.length === 0) && !isLoadingClientes && (!opcaoEscritorio || !opcaoEscritorio.nome.toLowerCase().includes(clienteQuery.toLowerCase()))" class="py-2 pl-6 pr-4 text-sm text-slate-500">Nenhum resultado encontrado.</div>
                            </div>
                        </div>
                    </div>

                    <!-- Passo 2: O Modelo e Configurações -->
                    <div class="space-y-4">
                        <div class="flex items-center gap-2 border-b border-slate-100 pb-2">
                            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-700 font-bold text-xs">2</span>
                            <h3 class="font-semibold text-slate-900 text-lg">Modelo e Título *</h3>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium leading-6 text-slate-900 mb-1">Selecione o Modelo Base</label>
                                <select v-model="formData.modelo_id" class="block w-full rounded-xl border-0 py-2.5 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6">
                                    <option value="" disabled>Escolha um modelo de documento...</option>
                                    <template v-if="modelos">
                                        <option v-for="m in modelos" :key="m.id" :value="m.id">{{ m.nome }}</option>
                                    </template>
                                </select>
                                <p v-if="!modelos || modelos.length === 0" class="mt-1 text-xs text-rose-500">Nenhum modelo cadastrado. Envie um modelo primeiro na área de Documentos.</p>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium leading-6 text-slate-900 mb-1">Título do Documento Gerado</label>
                                <input v-model="formData.titulo_documento" type="text" placeholder="Ex: Procuração Ad Judicia - João" class="block w-full rounded-xl border-0 py-2.5 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6" />
                            </div>
                        </div>
                    </div>

                    <!-- Passo 3: Inteligência Artificial -->
                    <div class="space-y-4">
                        <div class="flex items-center gap-2 border-b border-slate-100 pb-2">
                            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-700 font-bold text-xs">3</span>
                            <h3 class="font-semibold text-slate-900 text-lg">Inteligência Artificial (Opcional)</h3>
                        </div>
                        
                        <div class="bg-indigo-50/50 rounded-xl p-5 border border-indigo-100">
                            <div class="flex items-start">
                                <div class="flex h-6 items-center">
                                    <input 
                                        id="usar_ia" 
                                        type="checkbox" 
                                        v-model="formData.usar_ia"
                                        class="h-4 w-4 rounded border-slate-300 text-purple-600 focus:ring-purple-600"
                                    />
                                </div>
                                <div class="ml-3 text-sm leading-6">
                                    <label for="usar_ia" class="font-medium text-slate-900 flex items-center gap-1">
                                        Usar IA para redigir cláusulas personalizadas
                                    </label>
                                    <p class="text-slate-500">A IA usará o seu modelo como base e aplicará as instruções abaixo, preenchendo os dados do cliente automaticamente.</p>
                                </div>
                            </div>
                            
                            <div v-if="formData.usar_ia" class="mt-4 pl-7 animate-fade-in-up">
                                <label class="block text-sm font-medium leading-6 text-slate-900 mb-1">O que a IA deve fazer? (Instruções)</label>
                                <textarea v-model="formData.instrucoes_ia" rows="3" placeholder="Ex: Adicione uma cláusula de confidencialidade com multa de 10 salários mínimos e foro em São Paulo." class="block w-full rounded-xl border-0 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- Submit -->
                    <div class="pt-4 border-t border-slate-100 flex justify-end">
                        <button 
                            @click="handleGenerate" 
                            :disabled="isGenerating || formData.cliente_id === '' || !formData.modelo_id || !formData.titulo_documento" 
                            class="inline-flex justify-center items-center gap-2 rounded-xl bg-purple-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <div v-if="isGenerating" class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                            <Sparkles v-else class="h-5 w-5" />
                            {{ isGenerating ? 'Gerando Documento...' : 'Redigir Documento' }}
                        </button>
                    </div>

                </div>
            </div>
            
        </main>
    </div>

    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed bottom-4 right-4 z-50 animate-fade-in-up">
      <div :class="[ 'rounded-xl p-4 shadow-xl border', notification.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200' ]">
        <div class="flex items-center gap-3">
          <CheckCircle2 v-if="notification.type === 'success'" class="w-5 h-5 text-green-600" />
          <AlertCircle v-else class="w-5 h-5 text-red-600" />
          <p :class="[ 'text-sm font-medium', notification.type === 'error' ? 'text-red-800' : 'text-green-800' ]">
            {{ notification.message }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
