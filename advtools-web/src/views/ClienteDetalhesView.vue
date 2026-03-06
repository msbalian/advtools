<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import { Menu as MenuIcon } from 'lucide-vue-next'
import {
  ArrowLeft,
  User,
  MapPin,
  Briefcase,
  Phone,
  Mail,
  Calendar,
  Pencil,
  Plus,
  BadgeDollarSign,
  FileText,
  X,
  LogOut,
  Settings,
  ChevronDown,
  AlertCircle,
  CheckCircle2,
  Users,
  Scale,
  Trash2,
  Download,
  UploadCloud,
  Wand2,
  Folder,
  FolderPlus,
  ChevronRight,
  Sparkles,
  RefreshCw,
  Loader2
} from 'lucide-vue-next'
import ClienteForm from '../components/ClienteForm.vue'
import ServicoForm from '../components/ServicoForm.vue'
import ParteEnvolvidaForm from '../components/ParteEnvolvidaForm.vue'
import FileExplorer from '../components/FileExplorer.vue'

const route = useRoute()
const router = useRouter()

const notification = ref({ show: false, message: '', type: 'success' })
const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'primary' })
const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'primary') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const cliente = ref(null)
const servicos = ref([])
const processos = ref([])
const partes = ref([])
const isLoading = ref(true)
const showProfileMenu = ref(false)
const currentUser = ref(null)
const sortBy = ref('nome') // 'nome' ou 'data'

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

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

const sidebarOpen = ref(false)

const loadDetalhes = async () => {
  isLoading.value = true
  try {
    // Fetch Cliente
    const resCliente = await apiFetch(`/api/clientes/${route.params.id}`)
    if (!resCliente.ok) throw new Error('Cliente não encontrado')
    cliente.value = await resCliente.json()

    // Fetch Serviços do Cliente
    const resServicos = await apiFetch(`/api/clientes/${route.params.id}/servicos`)
    if (resServicos.ok) {
        servicos.value = await resServicos.json()
    }

    // Fetch Processos
    const resProcessos = await apiFetch(`/api/processos/cliente/${route.params.id}`)
    if (resProcessos.ok) {
        processos.value = await resProcessos.json()
    }

    // Fetch Partes Envolvidas
    const resPartes = await apiFetch(`/api/clientes/${route.params.id}/partes`)
    if (resPartes.ok) {
        partes.value = await resPartes.json()
    }

  } catch (error) {
    if (error.message.includes('Sessão expirada')) return;
    console.error(error)
    showMessage("Erro ao carregar os dados do cliente.", "error")
    router.push('/clientes')
  } finally {
    isLoading.value = false
  }
}

// Lógica de Edição de Cliente (Modal)
const showEditClientModal = ref(false)
const isSavingClient = ref(false)
const formDataClient = ref({})

const openEditClient = () => {
    formDataClient.value = { ...cliente.value }
    showEditClientModal.value = true
}

const saveCliente = async (dados) => {
    isSavingClient.value = true
    try {
        const response = await apiFetch(`/api/clientes/${route.params.id}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao atualizar')
        
        await loadDetalhes()
        showEditClientModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar: " + e.message, "error")
    } finally {
        isSavingClient.value = false
    }
}

// Lógica de Criação/Edição de Serviço Contextualizado
const showNewServiceModal = ref(false)
const isSavingService = ref(false)
const isEditingService = ref(false)
const formDataService = ref({})

const escritorio = ref(null)

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

const getEmptyService = () => ({
  cliente_id: Number(route.params.id), 
  descricao: '', 
  data_contrato: '', 
  valor_total: 0, 
  qtd_parcelas: 1, 
  condicoes_pagamento: '', 
  porcentagem_exito: ''
})

const openNewService = () => {
    isEditingService.value = false
    formDataService.value = getEmptyService()
    showNewServiceModal.value = true
}

const openEditService = (servico) => {
    isEditingService.value = true
    formDataService.value = { ...servico }
    showNewServiceModal.value = true
}

const saveServico = async (dados) => {
    isSavingService.value = true
    try {
        let url = `/api/servicos`
        let method = 'POST'
        
        if (isEditingService.value) {
            url = `/api/servicos/${dados.id}`
            method = 'PUT'
        }

        const response = await apiFetch(url, {
            method: method,
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao salvar serviço')
        
        showMessage(isEditingService.value ? 'Serviço atualizado com sucesso!' : 'Serviço adicionado com sucesso!', 'success')
        await loadDetalhes() // Recarrega para mostrar o novo serviço
        showNewServiceModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar serviço: " + e.message, "error")
    } finally {
        isSavingService.value = false
    }
}

// Lógica de Partes Envolvidas
const showParteModal = ref(false)
const isSavingParte = ref(false)
const isEditingParte = ref(false)
const formDataParte = ref({})

const getEmptyParte = () => ({
    cliente_id: Number(route.params.id),
    nome: '',
    papel: '',
    documento: '',
    email: '',
    telefone: '',
    rg: '',
    data_nascimento: '',
    nacionalidade: '',
    estado_civil: '',
    profissao: '',
    cep: '',
    endereco: '',
    bairro: '',
    cidade: '',
    uf: ''
})

const openNewParte = () => {
    isEditingParte.value = false
    formDataParte.value = getEmptyParte()
    showParteModal.value = true
}

const openEditParte = (parte) => {
    isEditingParte.value = true
    formDataParte.value = { ...parte }
    showParteModal.value = true
}

const saveParte = async (dados) => {
    isSavingParte.value = true
    try {
        let url = `/api/partes`
        let method = 'POST'
        
        if (isEditingParte.value) {
            url = `/api/partes/${dados.id}`
            method = 'PUT'
        }

        const response = await apiFetch(url, {
            method: method,
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao salvar parte envolvida')
        
        showMessage(isEditingParte.value ? 'Parte atualizada com sucesso!' : 'Parte adicionada com sucesso!', 'success')
        await loadDetalhes()
        showParteModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar parte: " + e.message, "error")
    } finally {
        isSavingParte.value = false
    }
}

const deleteParte = async (id) => {
    confirmAction("Tem certeza que deseja remover esta parte envolvida? Esta ação não pode ser desfeita.", async () => {
        try {
            const res = await apiFetch(`/api/partes/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Parte removida com sucesso!")
                await loadDetalhes()
            } else {
                throw new Error("Erro ao excluir")
            }
        } catch (e) {
            showMessage("Erro ao excluir parte envolvida", "error")
        }
    })
}

// Lógica de Documentos e Pastas removida: Gerenciada agora pelo componente FileExplorer

onMounted(async () => {
  carregarEscritorio()
  carregarUsuario()
  await loadDetalhes()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar Centralizado -->
    <Sidebar :escritorio="escritorio" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Top Header -->
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-10 sticky top-0">
        <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-500 focus:outline-none">
                <MenuIcon class="w-6 h-6" />
            </button>
            <button @click="$router.push('/clientes')" class="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors text-sm font-medium">
                <ArrowLeft class="w-4 h-4" /> Voltar para Clientes
            </button>
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
          
          <!-- Dropdown Menu -->
          <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 focus:outline-none z-50 animate-fade-in-up" role="menu">
            <div class="px-4 py-3">
              <p class="text-sm text-slate-900 truncate">{{ currentUser ? currentUser.nome : 'Carregando...' }}</p>
              <p class="text-xs font-medium text-slate-500 truncate">{{ currentUser ? currentUser.email : '' }}</p>
            </div>
            <div class="py-1" role="none">
              <a href="#" class="group flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors" role="menuitem">
                <User class="mr-3 h-4 w-4 text-slate-400 group-hover:text-primary-500" aria-hidden="true" />
                Meu Perfil
              </a>
              <router-link to="/configuracoes" class="group flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors" role="menuitem">
                <Settings class="mr-3 h-4 w-4 text-slate-400 group-hover:text-primary-500" aria-hidden="true" />
                Configurações
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
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
        
        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="text-slate-500">Carregando painel do cliente...</div>
        </div>

        <div v-else-if="cliente" class="space-y-6 animate-fade-in-up">
            <!-- Controles de Ordenação (Global para Documentos/Pastas abaixo) -->
             <!-- Deslocado para perto da seção de documentos se preferir, mas aqui fica central -->
            
            <!-- Dashboard Cover & Header -->
            <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden relative">
                <div class="h-24 bg-gradient-to-r from-primary-600 to-indigo-600"></div>
                <div class="px-6 py-5 sm:flex sm:items-end sm:justify-between relative">
                    <div class="sm:flex sm:space-x-5">
                        <div class="relative -mt-16 flex h-24 w-24 items-center justify-center rounded-2xl bg-white ring-4 ring-white shadow-md overflow-hidden">
                            <User class="h-12 w-12 text-slate-300" />
                        </div>
                        <div class="mt-4 sm:mt-0 sm:pt-1">
                            <p class="text-xs font-medium text-primary-600 uppercase tracking-widest">Painel do Cliente</p>
                            <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">{{ cliente.nome }}</h1>
                            <p class="text-sm font-medium text-slate-500 mt-1">Cadastrado em {{ new Date(cliente.data_cadastro).toLocaleDateString('pt-BR') }}</p>
                        </div>
                    </div>
                    <div class="mt-5 flex justify-stretch space-x-3 sm:mt-0 sm:justify-end">
                        <button @click="openEditClient" type="button" class="btn-secondary inline-flex items-center justify-center gap-2">
                            <Pencil class="h-4 w-4" aria-hidden="true" />
                            Editar Cliente
                        </button>
                        <button @click="openNewService" type="button" class="btn-primary inline-flex items-center justify-center gap-2">
                            <Plus class="h-4 w-4" aria-hidden="true" />
                            Novo Serviço
                        </button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Coluna Esquerda: Dados Rápidos -->
                <div class="space-y-6 md:col-span-1">
                    
                    <!-- Card Contato -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 p-5">
                        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-4">Informações de Contato</h3>
                        <dl class="space-y-4">
                            <div class="flex items-start gap-3">
                                <Phone class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">Telefone / WhatsApp</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.telefone || 'Não informado' }}</dd>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <Mail class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">E-mail</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.email || 'Não informado' }}</dd>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <MapPin class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">Endereço</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">
                                        {{ cliente.endereco ? `${cliente.endereco}, ${cliente.bairro || ''}. ${cliente.cidade || ''}/${cliente.uf || ''}` : 'Não informado' }}
                                    </dd>
                                </div>
                            </div>
                        </dl>
                    </div>

                    <!-- Card Documentação -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 p-5">
                        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-4">Documentação Pessoal</h3>
                        <dl class="grid grid-cols-2 gap-y-4 gap-x-2">
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">CPF / CNPJ</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.documento || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">RG</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.rg || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">Nascimento</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ formatDate(cliente.data_nascimento) || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">Estado Civil</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.estado_civil || '-' }}</dd>
                            </div>
                            <div class="col-span-2">
                                <dt class="text-xs font-medium text-slate-500">Profissão</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.profissao || '-' }}</dd>
                            </div>
                        </dl>
                    </div>

                </div>

                <!-- Coluna Direita: Serviços, Processos, Histórico -->
                <div class="space-y-6 md:col-span-2">
                    
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <BadgeDollarSign class="w-5 h-5 text-primary-600" /> Serviços Ativos
                            </h3>
                            <button @click="openNewService" class="text-xs font-medium text-primary-600 hover:text-primary-800 bg-primary-50 px-2 py-1 rounded-md transition-colors">
                                + Novo
                            </button>
                        </div>
                        <ul role="list" class="divide-y divide-slate-100">
                            <li v-if="servicos.length === 0" class="px-5 py-8 text-center text-sm text-slate-500">
                                Este cliente não possui nenhum serviço cadastrado.
                            </li>
                            <li v-for="servico in servicos" :key="servico.id" @click="openEditService(servico)" class="px-5 py-4 hover:bg-slate-50 transition-colors cursor-pointer group">
                                <div class="flex items-center justify-between">
                                    <div class="flex flex-col group-hover:pl-1 transition-all">
                                        <span class="text-sm font-semibold text-primary-600 group-hover:text-primary-800">{{ servico.descricao }}</span>
                                        <span class="text-xs text-slate-500 flex items-center mt-1">
                                            <Calendar class="w-3 h-3 mr-1 inline-block" /> 
                                            Registrado em: {{ new Date(servico.data_contratacao).toLocaleDateString() }} 
                                            | Honorários: R$ {{ servico.valor_total.toFixed(2) }}
                                        </span>
                                    </div>
                                    <div class="flex items-center">
                                       <span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Ativo</span>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Card Processos Judiciais -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <Scale class="w-5 h-5 text-primary-600" /> Processos Judiciais
                            </h3>
                            <div class="flex gap-2">
                                <button @click="router.push('/processos')" class="text-xs font-medium text-primary-600 hover:text-primary-800 bg-primary-50 px-2 py-1 rounded-md transition-colors">
                                    Ver Todos
                                </button>
                                <button @click="router.push(`/processos/novo?cliente_id=${cliente.id}`)" class="text-xs font-medium text-white bg-primary-600 hover:bg-primary-700 px-2 py-1 rounded-md transition-colors">
                                    + Novo
                                </button>
                            </div>
                        </div>
                        <ul role="list" class="divide-y divide-slate-100">
                            <li v-if="processos.length === 0" class="px-5 py-8 text-center text-sm text-slate-500">
                                Nenhum processo judicial vinculado a este cliente.
                            </li>
                            <li v-for="proc in processos" :key="proc.id" @click="router.push('/processos/' + proc.id)" class="px-5 py-4 hover:bg-slate-50 transition-colors cursor-pointer group">
                                <div class="flex items-center justify-between">
                                    <div class="flex flex-col group-hover:pl-1 transition-all">
                                        <div class="flex items-center gap-2">
                                            <span class="text-sm font-semibold text-slate-900 group-hover:text-primary-700">{{ proc.titulo }}</span>
                                            <span class="text-[9px] bg-emerald-100 text-emerald-700 font-black px-1.5 py-0.5 rounded uppercase">{{ proc.status }}</span>
                                        </div>
                                        <span class="text-xs text-primary-600 font-bold mt-1">
                                            {{ proc.numero_processo }}
                                        </span>
                                    </div>
                                    <ChevronRight class="w-4 h-4 text-slate-400" />
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Card Partes Envolvidas -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <Users class="w-5 h-5 text-indigo-600" /> Partes Envolvidas
                            </h3>
                            <button @click="openNewParte" class="text-xs font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2 py-1 rounded-md transition-colors">
                                + Adicionar
                            </button>
                        </div>
                        <div class="overflow-x-auto">
                            <table v-if="partes.length > 0" class="min-w-full divide-y divide-slate-100">
                                <thead class="bg-slate-50/30">
                                    <tr>
                                        <th scope="col" class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Nome / Papel</th>
                                        <th scope="col" class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Documento</th>
                                        <th scope="col" class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Ações</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    <tr v-for="parte in partes" :key="parte.id" class="hover:bg-slate-50 transition-colors group">
                                        <td class="px-5 py-4 whitespace-nowrap">
                                            <div class="flex flex-col">
                                                <span class="text-sm font-semibold text-slate-900">{{ parte.nome }}</span>
                                                <span class="text-xs text-indigo-600 font-medium">{{ parte.papel }}</span>
                                            </div>
                                        </td>
                                        <td class="px-5 py-4 whitespace-nowrap text-sm text-slate-500">
                                            {{ parte.documento || '-' }}
                                        </td>
                                        <td class="px-5 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div class="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button @click="openEditParte(parte)" class="p-1.5 text-slate-400 hover:text-primary-600 transition-colors">
                                                    <Pencil class="w-4 h-4" />
                                                </button>
                                                <button @click="deleteParte(parte.id)" class="p-1.5 text-slate-400 hover:text-red-600 transition-colors">
                                                    <Trash2 class="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div v-else class="px-5 py-8 text-center text-sm text-slate-500">
                                Nenhuma parte envolvida cadastrada para este cliente.
                            </div>
                        </div>
                    </div>

                    <!-- Card Documentos & Assinaturas (Componentizado) -->
                    <FileExplorer 
                        contextType="cliente" 
                        :contextId="cliente.id" 
                        title="Documentos e Assinaturas"
                    />

                </div>
            </div>

        </div>

    </main>
    </div>

    <!-- Modal Editar Cliente -->
    <div v-if="showEditClientModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showEditClientModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2"><User class="w-5 h-5 text-primary-600" /> Editar Cliente</h3>
            <button @click="showEditClientModal = false" class="text-slate-400 hover:text-slate-500 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ClienteForm v-model="formDataClient" :is-submitting="isSavingClient" :is-editing="true" @submit="saveCliente" @cancel="showEditClientModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Serviço (Contextual) -->
    <div v-if="showNewServiceModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showNewServiceModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-primary-50">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <BadgeDollarSign class="w-5 h-5 text-primary-600" /> 
                {{ isEditingService ? 'Formulário de Serviço' : 'Novo Serviço Privado' }}: <span class="text-primary-700">{{ cliente?.nome }}</span>
            </h3>
            <button @click="showNewServiceModal = false" class="text-slate-500 hover:text-slate-900 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ServicoForm v-model="formDataService" :clientes="[cliente]" :is-submitting="isSavingService" :is-editing="isEditingService" @submit="saveServico" @cancel="showNewServiceModal = false" />
          </div>
        </div>
      </div>
    </div>
    <!-- Modal Parte Envolvida -->
    <div v-if="showParteModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showParteModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-indigo-50">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <Users class="w-5 h-5 text-indigo-600" /> 
                {{ isEditingParte ? 'Editar Parte Envolvida' : 'Nova Parte Envolvida' }}
            </h3>
            <button @click="showParteModal = false" class="text-slate-500 hover:text-slate-900 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ParteEnvolvidaForm v-model="formDataParte" :is-submitting="isSavingParte" :is-editing="isEditingParte" @submit="saveParte" @cancel="showParteModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[999] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up">
        <div class="text-center">
          <div :class="['mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4', confirmDialog.type === 'purple' ? 'bg-purple-100' : 'bg-red-100']">
            <Sparkles v-if="confirmDialog.type === 'purple'" class="h-6 w-6 text-purple-600" />
            <Trash2 v-else class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
          <p class="text-sm text-slate-500 mb-6">{{ confirmDialog.message }}</p>
          <div class="flex gap-3 justify-center">
            <button @click="confirmDialog.show = false" class="btn-secondary px-5 py-2">Cancelar</button>
            <button @click="executeConfirm" :class="['px-5 py-2 rounded-lg font-bold text-white transition-all', confirmDialog.type === 'purple' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-red-600 hover:bg-red-700']">
                Confirmar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Nova Pasta -->
    <div v-if="showNewFolderModal" class="fixed inset-0 z-[60] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showNewFolderModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="relative inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md w-full">
          <div class="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
             <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2"><FolderPlus class="w-5 h-5 text-sky-600" /> Nova Pasta</h3>
             <button @click="showNewFolderModal = false" class="text-slate-400 hover:text-slate-500 transition-colors"><X class="w-5 h-5" /></button>
          </div>
          <div class="p-6">
             <div class="space-y-4">
                 <div>
                     <label class="block text-sm font-medium text-slate-700 mb-1">Nome da Pasta</label>
                     <input v-model="formDataFolder.nome" type="text" class="block w-full rounded-xl border-0 py-2.5 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-sky-600 sm:text-sm sm:leading-6" placeholder="ex: Procurações" @keyup.enter="handleCreateFolder" />
                 </div>
             </div>
          </div>
          <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
             <button @click="showNewFolderModal = false" type="button" class="btn-secondary">Cancelar</button>
             <button @click="handleCreateFolder" :disabled="isSavingFolder" type="button" class="btn-primary">
                 {{ isSavingFolder ? 'Salvando...' : 'Criar Pasta' }}
             </button>
          </div>
        </div>
      </div>
    </div>

  </div>
    <!-- Modal de Progresso da Organização -->
    <div v-if="progressModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
            <div class="p-8 text-center">
                <div class="mb-6 relative flex justify-center">
                    <div class="absolute inset-0 bg-primary-100 rounded-full animate-ping opacity-20"></div>
                    <div class="relative bg-primary-50 p-5 rounded-full ring-8 ring-primary-50/50">
                        <Sparkles v-if="jobProgress.status !== 'completed'" class="w-10 h-10 text-primary-600 animate-pulse" />
                        <CheckCircle2 v-else class="w-10 h-10 text-emerald-600" />
                    </div>
                </div>
                
                <h3 class="text-xl font-black text-slate-900 mb-2">Organizador Inteligente</h3>
                <p class="text-slate-500 text-sm font-medium mb-8 leading-relaxed">
                    {{ jobProgress.message }}
                </p>

                <!-- Barra de Progresso -->
                <div class="relative pt-1">
                    <div class="flex mb-2 items-center justify-between">
                        <div>
                            <span class="text-xs font-black inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-50">
                                {{ jobProgress.status === 'completed' ? 'Finalizado' : 'Em andamento' }}
                            </span>
                        </div>
                        <div class="text-right">
                            <span class="text-xs font-black inline-block text-primary-600">
                                {{ jobProgress.progress }}%
                            </span>
                        </div>
                    </div>
                    <div class="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-slate-100">
                        <div :style="{ width: jobProgress.progress + '%' }" 
                             class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-primary-500 to-indigo-600 transition-all duration-500">
                        </div>
                    </div>
                </div>
                
                <div v-if="jobProgress.status === 'running' || jobProgress.status === 'pending'" class="mt-4 flex items-center justify-center gap-2 text-xs font-bold text-slate-400">
                    <Loader2 class="w-4 h-4 animate-spin" />
                    A IA está processando seus documentos...
                </div>
                
                <button v-if="jobProgress.status === 'completed' || jobProgress.status === 'failed'"
                        @click="progressModalOpen = false" 
                        class="mt-6 w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors shadow-lg">
                    Fechar
                </button>
            </div>
        </div>
    </div>
</template>
