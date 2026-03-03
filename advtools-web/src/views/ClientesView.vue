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
  CheckCircle2,
  Phone,
  ArrowRight,
  Filter
} from 'lucide-vue-next'
import ClienteForm from '../components/ClienteForm.vue'
import GlobalClientSearch from '../components/GlobalClientSearch.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const router = useRouter()

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const clientes = ref([])
const isLoading = ref(true)
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


const loadClientes = async () => {
  isLoading.value = true
  try {
    const response = await apiFetch('/api/clientes')
    if (!response.ok) throw new Error('Falha ao buscar clientes')
    clientes.value = await response.json()
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const showAddModal = ref(false)
const isSaving = ref(false)

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

onMounted(() => {
  carregarEscritorio()
  carregarUsuario()
  loadClientes()
})
const isEditing = ref(false)

const getEmptyCliente = () => ({
  nome: '', documento: '', telefone: '', email: '', 
  cep: '', endereco: '', bairro: '', cidade: '', uf: '',
  rg: '', data_nascimento: '', nacionalidade: '', 
  estado_civil: '', profissao: ''
})

const currentCliente = ref(getEmptyCliente())

const openCreateModal = () => {
  isEditing.value = false
  currentCliente.value = getEmptyCliente()
  showAddModal.value = true
}

const openEditModal = (cliente) => {
  isEditing.value = true
  currentCliente.value = { ...cliente }
  showAddModal.value = true
}

const deleteCliente = (id) => {
  confirmAction('Tem certeza que deseja excluir permanentemente este cliente e todos os dados vinculados?', async () => {
    try {
      const response = await apiFetch(`/api/clientes/${id}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Falha ao excluir')
      showMessage('Cliente excluído com sucesso!', 'success')
      await loadClientes()
    } catch (error) {
      if (error.message.includes('Sessão expirada')) return;
      console.error('Erro:', error)
      showMessage('Erro ao excluir cliente.', 'error')
    }
  })
}

const saveCliente = async (formData) => {
  isSaving.value = true
  try {
    let url = '/api/clientes'
    let method = 'POST'
    
    if (isEditing.value) {
      url = `/api/clientes/${formData.id}`
      method = 'PUT'
    }

    const response = await apiFetch(url, {
      method: method,
      body: JSON.stringify(formData)
    })
    
    if (!response.ok) throw new Error('Falha ao salvar')
    
    showMessage(isEditing.value ? 'Cliente atualizado com sucesso!' : 'Cliente salvo com sucesso!', 'success')
    await loadClientes()
    showAddModal.value = false
  } catch (error) {
    console.error('Erro:', error)
    showMessage('Erro ao salvar cliente: ' + error.message, 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadClientes()
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
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      
      <!-- Top Header -->
      <header class="relative h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-30">
        <div class="flex items-center flex-1 gap-4">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 text-slate-500 hover:text-slate-700">
            <Menu class="w-6 h-6" />
          </button>
          
          <div class="max-w-md w-full hidden sm:block">
            <GlobalClientSearch :auto-focus="route.query.focus === 'true'" placeholder="Buscar clientes..." />
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
            <h1 class="text-2xl font-bold text-slate-900">Gestão de Clientes</h1>
            <p class="mt-1 text-sm text-slate-500">Cadastre, edite e acompanhe os clientes do escritório.</p>
          </div>
          <div class="mt-4 sm:mt-0">
            <button @click="openCreateModal" class="btn-primary flex items-center gap-2 shadow-primary-500/30">
               <Plus class="w-4 h-4" /> Novo Cliente
            </button>
          </div>
        </div>

        <!-- Table -->
        <div class="card p-0 animate-fade-in-up" style="animation-delay: 0.1s;">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200">
              <thead class="bg-slate-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Nome do Cliente</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Documento</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Contato</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Cidade/UF</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Ações</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-if="isLoading">
                  <td colspan="5" class="py-8 text-center text-sm text-slate-500">
                    Carregando clientes...
                  </td>
                </tr>
                <tr v-else-if="clientes.length === 0">
                  <td colspan="5" class="py-8 text-center text-sm text-slate-500">
                    Nenhum cliente cadastrado no momento. Clique em "Novo Cliente" para começar.
                  </td>
                </tr>
                <tr v-for="c in clientes" :key="c.id" class="hover:bg-slate-50 transition-colors">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium">
                     <router-link :to="'/clientes/' + c.id" class="text-primary-600 hover:text-primary-800 hover:underline flex items-center transition-colors">
                        {{ c.nome }}
                     </router-link>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                     {{ c.documento || '-' }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                    <div v-if="c.email">{{ c.email }}</div>
                    <div v-if="c.telefone">{{ c.telefone }}</div>
                    <span v-if="!c.email && !c.telefone">-</span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                     <span v-if="c.cidade">{{ c.cidade }}<span v-if="c.uf"> - {{ c.uf }}</span></span>
                     <span v-else>-</span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm font-medium">
                    <div class="flex items-center justify-end gap-2">
                       <button @click="openEditModal(c)" class="text-slate-400 hover:text-primary-600 transition-colors" title="Editar">
                         <Pencil class="w-4 h-4" />
                       </button>
                       <button @click="deleteCliente(c.id)" class="text-slate-400 hover:text-red-600 transition-colors" title="Excluir">
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
              <Users class="w-5 h-5 text-primary-600" /> 
              {{ isEditing ? 'Editar Cliente' : 'Novo Cliente' }}
            </h3>
            <button @click="showAddModal = false" class="text-slate-400 hover:text-slate-500 transition-colors rounded-full p-1 hover:bg-slate-100">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="px-6 py-6 max-h-[75vh] overflow-y-auto">
             <ClienteForm 
                v-model="currentCliente" 
                :is-submitting="isSaving"
                :is-editing="isEditing"
                @submit="saveCliente"
                @cancel="showAddModal = false" 
             />
          </div>

        </div>
      </div>
    </div>
    
  </div>
</template>
