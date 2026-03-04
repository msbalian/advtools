<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import {
  Users,
  Search,
  Menu,
  ChevronDown,
  AlertCircle,
  CheckCircle2,
  X,
  UserCheck,
  UserX,
  Trash2,
  ShieldCheck,
  Building2,
  Mail,
  MoreVertical
} from 'lucide-vue-next'

const router = useRouter()
const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const escritorio = ref(null)
const currentUser = ref(null)
const usuarios = ref([])
const isLoading = ref(true)
const searchQuery = ref('')

const carregarEscritorio = async () => {
    try {
        const res = await apiFetch('/api/escritorio')
        if (res.ok) escritorio.value = await res.json()
    } catch (e) {
        console.error("Erro ao carregar escritório", e)
    }
}

const carregarUsuarioIdentificado = async () => {
    try {
        const res = await apiFetch('/api/me')
        if (res.ok) {
            currentUser.value = await res.json()
            if (!currentUser.value.is_admin) {
                router.push('/dashboard')
            }
        }
    } catch (e) {
        console.error("Erro ao carregar usuario", e)
    }
}

const carregarTodosUsuarios = async () => {
    isLoading.value = true
    try {
        const res = await apiFetch('/api/admin/usuarios')
        if (res.ok) {
            usuarios.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar usuários globais", e)
    } finally {
        isLoading.value = false
    }
}

const aprovarUsuario = async (userId) => {
    try {
        const res = await apiFetch(`/api/admin/usuarios/${userId}/aprovar`, { method: 'POST' })
        if (res.ok) {
            showMessage("Usuário aprovado com sucesso!")
            carregarTodosUsuarios()
        }
    } catch (e) {
        showMessage("Erro ao aprovar usuário", "error")
    }
}

const bloquearUsuario = async (userId) => {
    try {
        const res = await apiFetch(`/api/admin/usuarios/${userId}/bloquear`, { method: 'POST' })
        if (res.ok) {
            showMessage("Usuário bloqueado.")
            carregarTodosUsuarios()
        }
    } catch (e) {
        showMessage("Erro ao bloquear usuário", "error")
    }
}

const excluirUsuario = async (userId) => {
    if (!confirm("Tem certeza que deseja excluir permanentemente este usuário?")) return
    try {
        const res = await apiFetch(`/api/admin/usuarios/${userId}`, { method: 'DELETE' })
        if (res.status === 204) {
            showMessage("Usuário removido do sistema.")
            carregarTodosUsuarios()
        }
    } catch (e) {
        showMessage("Erro ao excluir usuário", "error")
    }
}

const filteredUsers = computed(() => {
    if (!searchQuery.value) return usuarios.value
    const q = searchQuery.value.toLowerCase()
    return usuarios.value.filter(u => 
        u.nome.toLowerCase().includes(q) || 
        u.email.toLowerCase().includes(q) ||
        (u.escritorio && u.escritorio.nome.toLowerCase().includes(q))
    )
})

const notification = ref({ show: false, message: '', type: 'success' })
const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

onMounted(() => {
    carregarEscritorio()
    carregarUsuarioIdentificado()
    carregarTodosUsuarios()
})

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10">
        <div class="flex items-center gap-4">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 text-slate-500">
            <Menu class="w-6 h-6" />
          </button>
          <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
            <ShieldCheck class="w-5 h-5 text-primary-600" />
            Painel Administrativo Global
          </h2>
        </div>

        <div class="flex items-center gap-4">
          <div class="relative group hidden sm:block">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input v-model="searchQuery" type="text" placeholder="Buscar usuários ou escritórios..." 
                   class="pl-10 pr-4 py-1.5 bg-slate-100 border-transparent focus:bg-white focus:ring-2 focus:ring-primary-500 rounded-full text-sm w-64 transition-all" />
          </div>
          
          <div class="relative">
            <button @click="showProfileMenu = !showProfileMenu" class="flex items-center gap-2 p-1 rounded-full hover:bg-slate-100 transition-colors">
               <div class="h-8 w-8 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-xs">
                 {{ currentUser?.nome?.charAt(0).toUpperCase() }}
               </div>
            </button>
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl ring-1 ring-black/5 divide-y divide-slate-100 z-50 animate-fade-in-up">
               <div class="px-4 py-3">
                 <p class="text-sm font-bold text-slate-900 truncate">{{ currentUser?.nome }}</p>
                 <p class="text-xs text-slate-500 truncate">Super Admin</p>
               </div>
               <div class="py-1">
                 <button @click="handleLogout" class="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                    Sair
                 </button>
               </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto p-6">
        <div class="max-w-7xl mx-auto">
          <div class="mb-8">
            <h1 class="text-2xl font-black text-slate-900">Gestão de Usuários</h1>
            <p class="text-slate-500">Aprovação e controle de acesso para todos os escritórios da plataforma.</p>
          </div>

          <!-- Users Table Card -->
          <div class="card p-0 overflow-hidden shadow-sm border-slate-200">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead class="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Usuário</th>
                    <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Escritório</th>
                    <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Perfil</th>
                    <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Status</th>
                    <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase text-right">Ações</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-if="isLoading">
                    <td colspan="5" class="px-6 py-12 text-center text-slate-400">
                      <div class="flex flex-col items-center gap-2">
                        <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                        <span>Carregando base de usuários...</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else-if="filteredUsers.length === 0" class="bg-white">
                    <td colspan="5" class="px-6 py-12 text-center text-slate-400">
                      Nenhum usuário encontrado.
                    </td>
                  </tr>
                  <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-slate-50/50 transition-colors bg-white">
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-3">
                        <div :class="[user.is_admin ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-600', 'h-10 w-10 rounded-full flex items-center justify-center font-bold relative']">
                          {{ user.nome.charAt(0).toUpperCase() }}
                          <div v-if="user.is_admin" class="absolute -top-1 -right-1 bg-white rounded-full p-0.5 shadow-sm">
                            <ShieldCheck class="w-3.5 h-3.5 text-indigo-600" />
                          </div>
                        </div>
                        <div>
                          <div class="text-sm font-bold text-slate-900">{{ user.nome }}</div>
                          <div class="text-xs text-slate-500 flex items-center gap-1">
                            <Mail class="w-3 h-3" /> {{ user.email }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2 text-sm text-slate-600">
                        <Building2 class="w-4 h-4 text-slate-400" />
                        {{ user.escritorio?.nome || 'N/A' }}
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <span :class="[user.perfil === 'Admin' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-600', 'px-2.5 py-1 rounded-md text-xs font-bold']">
                        {{ user.perfil }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2">
                        <div :class="[user.ativo ? 'bg-emerald-500' : 'bg-amber-500', 'h-2 w-2 rounded-full animate-pulse']"></div>
                        <span :class="[user.ativo ? 'text-emerald-700' : 'text-amber-700', 'text-xs font-bold']">
                          {{ user.ativo ? 'Ativo' : 'Pendente' }}
                        </span>
                      </div>
                    </td>
                    <td class="px-6 py-4 text-right">
                      <div class="flex justify-end gap-2">
                        <button v-if="!user.ativo" @click="aprovarUsuario(user.id)" title="Aprovar Usuário" 
                                class="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all border border-transparent hover:border-emerald-100">
                          <UserCheck class="w-5 h-5" />
                        </button>
                        <button v-if="user.ativo && user.id !== currentUser?.id" @click="bloquearUsuario(user.id)" title="Bloquear Usuário"
                                class="p-2 text-amber-600 hover:bg-amber-50 rounded-lg transition-all border border-transparent hover:border-amber-100">
                          <UserX class="w-5 h-5" />
                        </button>
                        <button v-if="user.id !== currentUser?.id" @click="excluirUsuario(user.id)" title="Excluir Usuário"
                                class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all border border-transparent hover:border-red-100">
                          <Trash2 class="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Notification -->
    <div v-if="notification.show" 
         :class="['fixed bottom-6 right-6 z-50 px-6 py-3 rounded-2xl shadow-2xl text-white font-bold flex items-center gap-3 animate-fade-in-up', 
                  notification.type === 'error' ? 'bg-red-600' : 'bg-primary-600']">
      <component :is="notification.type === 'error' ? AlertCircle : CheckCircle2" class="w-5 h-5" />
      {{ notification.message }}
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}
</style>
