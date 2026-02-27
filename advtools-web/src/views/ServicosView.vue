<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
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
  Plus,
  Pencil,
  Trash2,
  X,
  User,
  LogOut,
  ChevronDown,
  AlertCircle,
  CheckCircle2
} from 'lucide-vue-next'
import ServicoForm from '../components/ServicoForm.vue'

const router = useRouter()

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const servicos = ref([])
const clientes = ref([])
const isLoading = ref(true)
const escritorio = ref(null)
const currentUser = ref(null)

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


const loadData = async () => {
  carregarUsuario()
  isLoading.value = true
  try {
    const [resServicos, resClientes] = await Promise.all([
      apiFetch('/api/servicos'),
      apiFetch('/api/clientes')
    ])
    
    if (!resServicos.ok || !resClientes.ok) {
      throw new Error('Falha ao buscar dados')
    }
    
    servicos.value = await resServicos.json()
    clientes.value = await resClientes.json()
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const getClienteNome = (id) => {
  const c = clientes.value.find(c => c.id === id)
  return c ? c.nome : `Cliente #${id}`
}

const showAddModal = ref(false)
const isSaving = ref(false)
const isEditing = ref(false)

const notification = ref({ show: false, message: '', type: 'success' })
const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmDialog = ref({ show: false, message: '', onConfirm: null })
const confirmAction = (message, onConfirm) => {
    confirmDialog.value = { show: true, message, onConfirm }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const getEmptyServico = () => ({
  cliente_id: '',
  descricao: '',
  valor_total: 0,
  condicoes_pagamento: '',
  forma_pagamento: '',
  qtd_parcelas: 0,
  detalhes_pagamento: '',
  porcentagem_exito: '',
  data_contrato: '',
  status: 'Ativo'
})

const currentServico = ref(getEmptyServico())

const openCreateModal = () => {
  isEditing.value = false
  currentServico.value = getEmptyServico()
  showAddModal.value = true
}

const openEditModal = (servico) => {
  isEditing.value = true
  currentServico.value = { ...servico }
  showAddModal.value = true
}

const deleteServico = (id) => {
  confirmAction('Tem certeza que deseja excluir permanentemente este serviço?', async () => {
    try {
      const response = await apiFetch(`/api/servicos/${id}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Falha ao excluir')
      showMessage('Serviço excluído com sucesso!', 'success')
      await loadData()
    } catch (error) {
      if (error.message.includes('Sessão expirada')) return;
      console.error('Erro:', error)
      showMessage('Erro ao excluir serviço.', 'error')
    }
  })
}

const saveServico = async (formData) => {
  isSaving.value = true
  try {
    let url = '/api/servicos'
    let method = 'POST'
    
    // API endpoint validation if missing PUT - you can assume its building now if not there
    if (isEditing.value) {
      url = `/api/servicos/${formData.id}`
      method = 'PUT' 
    }

    const response = await apiFetch(url, {
      method: method,
      body: JSON.stringify(formData)
    })
    
    if (!response.ok) throw new Error('Falha ao salvar')
    
    showMessage(isEditing.value ? 'Serviço atualizado com sucesso!' : 'Serviço salvo com sucesso!', 'success')
    await loadData()
    showAddModal.value = false
  } catch (error) {
    console.error('Erro:', error)
    showMessage('Erro ao salvar serviço: ' + error.message, 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex relative">
    
    <!-- Global Notification Toast -->
    <div v-if="notification.show" 
         :class="['fixed top-4 right-4 z-[100] px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center gap-3 transition-all animate-fade-in-down', 
                  notification.type === 'error' ? 'bg-red-600' : 'bg-emerald-600']">
        <component :is="notification.type === 'error' ? AlertCircle : CheckCircle2" class="w-5 h-5 flex-shrink-0" />
        <span class="max-w-[300px] break-words">{{ notification.message }}</span>
        <button @click="notification.show = false" class="ml-2 mt-0.5 hover:opacity-75 focus:outline-none flex-shrink-0 self-start">
            <X class="w-4 h-4" />
        </button>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="relative z-[100]" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"></div>
        <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <div class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-xl transition-all sm:my-8 w-full max-w-md animate-fade-in-up">
                    <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                        <div class="sm:flex sm:items-start">
                            <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                                <AlertCircle class="h-6 w-6 text-red-600" aria-hidden="true" />
                            </div>
                            <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                                <h3 class="text-base font-semibold leading-6 text-slate-900" id="modal-title">Confirmar Ação</h3>
                                <div class="mt-2">
                                    <p class="text-sm text-slate-500">{{ confirmDialog.message }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-slate-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-3">
                        <button @click="executeConfirm" type="button" class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:w-auto">Confirmar</button>
                        <button @click="confirmDialog.show = false" type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 sm:mt-0 sm:w-auto">Cancelar</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Sidebar Centralizado -->
    <Sidebar :escritorio="escritorio" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      
      <!-- Top Header -->
      <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-10">
        <div class="flex items-center flex-1 gap-4">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 text-slate-500 hover:text-slate-700">
            <Menu class="w-6 h-6" />
          </button>
          
          <div class="max-w-md w-full hidden sm:block">
            <div class="relative">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <Search class="h-5 w-5 text-slate-400" aria-hidden="true" />
              </div>
              <input type="text" class="block w-full rounded-full border-0 py-1.5 pl-10 pr-3 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 bg-slate-50" placeholder="Buscar serviços e contratos..." />
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
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
        </div>
      </header>

      <!-- Main Scrollable Area -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in-up">
          <div>
            <h1 class="text-2xl font-bold text-slate-900">Serviços e Honorários</h1>
            <p class="mt-1 text-sm text-slate-500">Gestão de serviços prestados e contratos vinculados aos clientes.</p>
          </div>
          <div class="mt-4 sm:mt-0">
            <button @click="openCreateModal" class="btn-primary flex items-center gap-2 shadow-primary-500/30">
               <Plus class="w-4 h-4" /> Novo Serviço
            </button>
          </div>
        </div>

        <!-- Table -->
        <div class="card p-0 animate-fade-in-up" style="animation-delay: 0.1s;">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200">
              <thead class="bg-slate-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Descrição / Contrato</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Cliente Vinculado</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Valor (R$)</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Ações</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-if="isLoading">
                  <td colspan="5" class="py-8 text-center text-sm text-slate-500">
                    Carregando serviços...
                  </td>
                </tr>
                <tr v-else-if="servicos.length === 0">
                  <td colspan="5" class="py-8 text-center text-sm text-slate-500">
                    Nenhum serviço registrado. Clique em "Novo Serviço" para adicionar.
                  </td>
                </tr>
                <tr v-for="s in servicos" :key="s.id" class="hover:bg-slate-50 transition-colors">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium text-slate-900">
                     {{ s.descricao || `Serviço #${s.id}` }}
                     <div class="text-xs text-slate-500">{{ s.forma_pagamento }}</div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm font-medium text-slate-900">
                     {{ getClienteNome(s.cliente_id) }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-700">
                     <span v-if="s.valor_total">R$ {{ s.valor_total.toFixed(2) }}</span>
                     <span v-else class="text-slate-400">-</span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                    <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset bg-emerald-50 text-emerald-700 ring-emerald-600/20">
                      {{ s.status }}
                    </span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm font-medium">
                    <div class="flex items-center justify-end gap-2">
                       <button @click="openEditModal(s)" class="text-slate-400 hover:text-primary-600 transition-colors" title="Editar">
                         <Pencil class="w-4 h-4" />
                       </button>
                       <button @click="deleteServico(s.id)" class="text-slate-400 hover:text-red-600 transition-colors" title="Excluir">
                         <Trash2 class="w-4 h-4" />
                       </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
    
    <!-- View Modal Wrapper (Fullscreen on mobile, large centered on desktop) -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showAddModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Panel -->
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full overflow-hidden border border-slate-200">
          
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <BadgeDollarSign class="w-5 h-5 text-primary-600" /> 
              {{ isEditing ? 'Editar Serviço / Contrato' : 'Novo Serviço / Contrato' }}
            </h3>
            <button @click="showAddModal = false" class="text-slate-400 hover:text-slate-500 transition-colors rounded-full p-1 hover:bg-slate-100">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="px-6 py-6 max-h-[75vh] overflow-y-auto">
             <ServicoForm 
                v-model="currentServico" 
                :clientes="clientes"
                :is-submitting="isSaving"
                :is-editing="isEditing"
                @submit="saveServico"
                @cancel="showAddModal = false" 
             />
          </div>

        </div>
      </div>
    </div>
    
  </div>
</template>
