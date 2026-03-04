<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import { Menu as MenuIcon } from 'lucide-vue-next'
import {
  ArrowLeft,
  Building2,
  Users,
  Upload,
  UserPlus,
  Trash2,
  Pencil,
  AlertCircle,
  CheckCircle2,
  X,
  Cloud,
  Settings2,
  ShieldCheck,
  Search
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeTab = ref(route.query.tab || 'escritorio') // 'escritorio', 'equipe' ou 'global'

watch(() => route.query.tab, (newTab) => {
    if (newTab) activeTab.value = newTab
})
const isLoading = ref(true)

// =======================
// ESTADO: ESCRITÓRIO
// =======================
const escritorio = ref({ 
    nome: '', 
    documento: '', 
    logo_path: ''
})
const isSavingEscritorio = ref(false)
const logoFile = ref(null)
const logoPreview = ref(null)

// =======================
// ESTADO: EQUIPE
// =======================
const usuarios = ref([])
const usuariosGlobais = ref([])
const searchGlobal = ref('')
const isSavingUsuario = ref(false)
const showUsuarioModal = ref(false)
const isEditingUsuario = ref(false)
const currentUser = ref(null)

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

const formUsuario = ref({
    nome: '',
    email: '',
    senha: '',
    tipo: 'Humano',
    perfil: 'Colaborador',
    cpf: '',
    ativo: true,
    is_admin: false
})

onMounted(async () => {
  await loadCurrentUser()
  await loadDadosEscritorio()
  await loadEquipe()
  if (currentUser.value?.is_admin) {
    await loadUsuariosGlobais()
  }
  isLoading.value = false
})

const loadCurrentUser = async () => {
    try {
        const res = await apiFetch('/api/me')
        if (res.ok) currentUser.value = await res.json()
    } catch (e) {
        console.error("Erro ao carregar usuário atual", e)
    }
}

const loadDadosEscritorio = async () => {
    try {
        const res = await apiFetch('/api/escritorio')
        if (!res.ok) throw new Error("Falha ao carregar escritório")
        escritorio.value = await res.json()
        if (escritorio.value.logo_path) {
            logoPreview.value = `http://localhost:8000/static/${escritorio.value.logo_path}`
        }
    } catch (e) {
        console.error(e)
    }
}

const loadEquipe = async () => {
    try {
        const res = await apiFetch('/api/usuarios')
        if (!res.ok) throw new Error("Falha ao carregar equipe")
        usuarios.value = await res.json()
    } catch (e) {
        console.error(e)
    }
}

const loadUsuariosGlobais = async () => {
    try {
        const res = await apiFetch('/api/admin/usuarios')
        if (res.ok) usuariosGlobais.value = await res.json()
    } catch (e) {
        console.error("Erro ao carregar gestão global", e)
    }
}

// =======================
// AÇÕES: ESCRITÓRIO
// =======================
const handleLogoUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
        logoFile.value = file
        logoPreview.value = URL.createObjectURL(file)
    }
}

const saveEscritorio = async () => {
    isSavingEscritorio.value = true
    try {
        const formData = new FormData()
        formData.append('nome', escritorio.value.nome)
        if (escritorio.value.documento) formData.append('documento', escritorio.value.documento)
        if (escritorio.value.gemini_api_key) formData.append('gemini_api_key', escritorio.value.gemini_api_key)
        
        if (logoFile.value) formData.append('logo', logoFile.value)

        const res = await apiFetch('/api/escritorio', {
            method: 'PUT',
            body: formData,
            // Header Content-Type deve ser omitido para o navegador colocar o boundary do form-data automático
        })
        
        // Remove content-type do headers no utils/api.ts quando for formData?
        // Sim, precisaremos atualizar utils/api.ts para não forçar application/json se body for FormData
        
        if (!res.ok) throw new Error("Erro ao atualizar escritório")
        showMessage("Escritório atualizado com sucesso!", "success")
        await loadDadosEscritorio()
    } catch (e) {
        showMessage("Erro: " + e.message, "error")
    } finally {
        isSavingEscritorio.value = false
    }
}

// =======================
// AÇÕES: EQUIPE
// =======================
const openNewUsuario = () => {
    isEditingUsuario.value = false
    formUsuario.value = { 
        nome: '', 
        email: '', 
        senha: '', 
        tipo: 'Humano', 
        perfil: 'Colaborador', 
        cpf: '', 
        ativo: true, 
        is_admin: false,
        escritorio_id: currentUser.value?.escritorio_id
    }
    showUsuarioModal.value = true
}

const openEditUsuario = (user) => {
    isEditingUsuario.value = true
    formUsuario.value = { ...user, senha: '', escritorio_id: user.escritorio_id || currentUser.value?.escritorio_id } // Limpa a senha pra não enviar de volta se não alterar
    showUsuarioModal.value = true
}

const saveUsuario = async () => {
    isSavingUsuario.value = true
    try {
        let url = '/api/usuarios'
        let method = 'POST'
        
        if (isEditingUsuario.value) {
            url = `/api/usuarios/${formUsuario.value.id}`
            method = 'PUT'
        }

        const res = await apiFetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formUsuario.value)
        })

        if (!res.ok) {
            const data = await res.json()
            let errMsg = "Erro ao salvar usuário"
            if (data.detail) {
               if (typeof data.detail === 'string') errMsg = data.detail
               else if (Array.isArray(data.detail)) errMsg = data.detail.map(d => d.msg).join(', ')
            }
            throw new Error(errMsg)
        }
        
        showUsuarioModal.value = false
        showMessage(isEditingUsuario.value ? "Membro atualizado com sucesso!" : "Membro adicionado com sucesso!", "success")
        await loadEquipe()
    } catch (e) {
        showMessage("Erro: " + e.message, "error")
    } finally {
        isSavingUsuario.value = false
    }
}

const deleteUsuario = (id) => {
    confirmAction("Tem certeza que deseja remover este membro da equipe?", async () => {
        try {
            const res = await apiFetch(`/api/usuarios/${id}`, { method: 'DELETE' })
            if (!res.ok) throw new Error("Erro ao remover usuário")
            showMessage("Membro removido com sucesso!", "success")
            await loadEquipe()
        } catch (e) {
            showMessage("Erro: " + e.message, "error")
        }
    })
}

const toggleStatus = async (user) => {
    try {
        const res = await apiFetch(`/api/usuarios/${user.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ativo: !user.ativo })
        })
        if (res.ok) {
            user.ativo = !user.ativo
            showMessage(`Status alterado para ${user.ativo ? 'Ativo' : 'Inativo'}.`, "success")
        }
    } catch (e) {
        showMessage("Erro ao alterar status.", "error")
    }
}

const isAdmin = () => {
    return currentUser.value && (currentUser.value.is_admin || currentUser.value.perfil === 'Admin')
}

const filteredGlobalUsers = computed(() => {
    if (!searchGlobal.value) return usuariosGlobais.value
    const s = searchGlobal.value.toLowerCase()
    return usuariosGlobais.value.filter(u => 
        u.nome.toLowerCase().includes(s) || 
        u.email.toLowerCase().includes(s) || 
        u.escritorio?.nome?.toLowerCase().includes(s)
    )
})

const handleAprovarGlobal = async (userId) => {
    try {
        const res = await apiFetch(`/api/admin/usuarios/${userId}/aprovar`, { method: 'POST' })
        if (res.ok) {
            showMessage("Usuário aprovado/ativado com sucesso!")
            await loadUsuariosGlobais()
        }
    } catch (e) { showMessage("Erro ao aprovar usuário", "error") }
}

const handleBloquearGlobal = async (userId) => {
    try {
        const res = await apiFetch(`/api/admin/usuarios/${userId}/bloquear`, { method: 'POST' })
        if (res.ok) {
            showMessage("Usuário bloqueado com sucesso!")
            await loadUsuariosGlobais()
        }
    } catch (e) { showMessage("Erro ao bloquear usuário", "error") }
}

const handleExcluirGlobal = async (userId) => {
    confirmAction("Deseja realmente EXCLUIR este usuário permanentemente?", async () => {
        try {
            const res = await apiFetch(`/api/admin/usuarios/${userId}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Usuário excluído com sucesso!")
                await loadUsuariosGlobais()
            }
        } catch (e) { showMessage("Erro ao excluir usuário", "error") }
    })
}

const sidebarOpen = ref(false)
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar Centralizado -->
    <Sidebar :escritorio="escritorio" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-10 sticky top-0">
        <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-500 focus:outline-none">
                <MenuIcon class="w-6 h-6" />
            </button>
            <button @click="$router.push('/dashboard')" class="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors text-sm font-medium">
                <ArrowLeft class="w-4 h-4" /> Voltar para o Dashboard
            </button>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto w-full">
        
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-slate-900">Configurações do Sistema</h1>
            <p class="text-sm text-slate-500 mt-1">Gerencie os dados do seu escritório e o acesso da sua equipe.</p>
        </div>

        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="text-slate-500">Carregando configurações...</div>
        </div>

        <div v-else class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
            <!-- Tabs -->
            <div class="border-b border-slate-200">
                <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                    <button 
                        @click="activeTab = 'escritorio'"
                        :class="[activeTab === 'escritorio' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium flex items-center gap-2']"
                    >
                        <Building2 class="w-4 h-4" /> Meu Escritório
                    </button>
                    <button 
                        @click="activeTab = 'equipe'"
                        :class="[activeTab === 'equipe' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium flex items-center gap-2']"
                    >
                        <Users class="w-4 h-4" /> Gestão da Equipe
                    </button>
                    <button 
                        v-if="currentUser?.is_admin"
                        @click="activeTab = 'global'"
                        :class="[activeTab === 'global' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium flex items-center gap-2']"
                    >
                        <ShieldCheck class="w-4 h-4" /> Gestão Global (Root)
                    </button>
                </nav>
            </div>

            <!-- Tab Content: Escritório -->
            <div v-if="activeTab === 'escritorio'" class="p-6">
                <form @submit.prevent="saveEscritorio" class="space-y-8 max-w-2xl">
                    <div class="space-y-6 sm:space-y-5">
                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:border-b sm:border-slate-200 sm:py-5">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">Logomarca do Escritório</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <div class="flex items-center gap-x-6">
                                    <div class="h-24 w-24 rounded-lg bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200 bg-contain bg-center bg-no-repeat" :style="logoPreview ? `background-image: url('${logoPreview}')` : ''">
                                        <Building2 v-if="!logoPreview" class="h-10 w-10 text-slate-300" aria-hidden="true" />
                                    </div>
                                    <button v-if="isAdmin()" type="button" @click="$refs.logoInput.click()" class="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 flex items-center gap-2">
                                        <Upload class="w-4 h-4" /> Alterar logo
                                    </button>
                                    <input type="file" ref="logoInput" class="hidden" accept="image/*" @change="handleLogoUpload" />
                                </div>
                                <p class="text-xs leading-5 text-slate-500 mt-2">JPG, GIF ou PNG. Máximo 2MB.</p>
                            </div>
                        </div>

                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:pt-5">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">Nome do Escritório</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <input v-model="escritorio.nome" type="text" required :disabled="!isAdmin()" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 disabled:bg-slate-50 disabled:text-slate-500" />
                            </div>
                        </div>

                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:pt-5">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">CNPJ / CPF do Titular</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <input v-model="escritorio.documento" type="text" :disabled="!isAdmin()" class="block w-full max-w-md rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 disabled:bg-slate-50 disabled:text-slate-500" />
                            </div>
                        </div>

                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:pt-5 sm:border-t sm:border-slate-100">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">Gemini API Key (IA)</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <input v-model="escritorio.gemini_api_key" type="text" :disabled="!isAdmin()" placeholder="AIza..." class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 disabled:bg-slate-50 disabled:text-slate-500" />
                                <p class="mt-2 text-xs text-slate-500">
                                    Necessária para usar o Redator com IA. 
                                    <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-primary-600 hover:text-primary-500 font-medium">Obtenha sua chave aqui.</a>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div v-if="isAdmin()" class="pt-5 border-t border-slate-200 flex justify-end">
                        <button type="submit" :disabled="isSavingEscritorio" class="btn-primary">
                            {{ isSavingEscritorio ? 'Salvando...' : 'Salvar Alterações' }}
                        </button>
                    </div>
                </form>
            </div>

            <!-- Tab Content: Equipe -->
            <div v-if="activeTab === 'equipe'" class="p-6">
                
                <div class="sm:flex sm:items-center sm:justify-between mb-6">
                    <div>
                        <h2 class="text-base font-semibold leading-6 text-slate-900">Membros da Equipe</h2>
                        <p class="mt-1 text-sm text-slate-500">Lista completa com os acessos de parceiros e colaboradores do escritório.</p>
                    </div>
                    <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
                        <button v-if="isAdmin()" @click="openNewUsuario" type="button" class="btn-primary flex items-center gap-2">
                            <UserPlus class="w-4 h-4" /> Adicionar Membro
                        </button>
                    </div>
                </div>

                <!-- Lista de Usuários -->
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-300">
                        <thead class="bg-slate-50">
                            <tr>
                                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-3">Nome / Email</th>
                                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Nível / Perfil</th>
                                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Status</th>
                                <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-3 text-right">
                                    <span class="sr-only">Ações</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-slate-200">
                            <tr v-for="user in usuarios" :key="user.id">
                                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-3">
                                    <div class="font-medium text-slate-900">
                                        {{ user.nome }}
                                        <span v-if="user.is_admin" class="ml-2 inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-700/10">Admin</span>
                                    </div>
                                    <div class="text-slate-500">{{ user.email }}</div>
                                    <div v-if="user.cpf" class="text-xs text-slate-400">CPF: {{ user.cpf }}</div>
                                </td>
                                <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                                    <div class="text-slate-900">{{ user.perfil }}</div>
                                    <div>{{ user.tipo }}</div>
                                </td>
                                <td class="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                                    <button v-if="isAdmin() && currentUser.id !== user.id" @click="toggleStatus(user)" :class="[user.ativo ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' : 'bg-red-50 text-red-700 ring-red-600/10', 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset hover:opacity-80 transition-opacity']">
                                        {{ user.ativo ? 'Ativo' : 'Bloqueado' }}
                                    </button>
                                    <span v-else :class="[user.ativo ? 'text-emerald-700' : 'text-red-700']" class="text-sm font-medium">
                                        {{ user.ativo ? 'Ativo' : 'Bloqueado' }}
                                    </span>
                                </td>
                                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-3 flex justify-end gap-2">
                                    <button v-if="isAdmin() || currentUser.id === user.id" @click="openEditUsuario(user)" class="text-primary-600 hover:text-primary-900 px-2">
                                        <Pencil class="w-4 h-4" />
                                    </button>
                                    <button v-if="isAdmin() && currentUser.id !== user.id" @click="deleteUsuario(user.id)" class="text-red-500 hover:text-red-700 px-2">
                                        <Trash2 class="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab Content: Gestão Global -->
            <div v-if="activeTab === 'global'" class="p-6">
                <div class="sm:flex sm:items-center sm:justify-between mb-6">
                    <div>
                        <h2 class="text-base font-semibold leading-6 text-slate-900">Administração Global do Sistema</h2>
                        <p class="mt-1 text-sm text-slate-500">Gestão de usuários e aprovações de todos os escritórios cadastrados.</p>
                    </div>
                </div>

                <div class="relative mb-6">
                    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <Search class="h-4 w-4 text-slate-400" />
                    </div>
                    <input v-model="searchGlobal" type="text" placeholder="Filtrar por nome, email ou escritório..." class="block w-full max-w-md rounded-lg border-0 py-2 pl-10 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-primary-600 sm:text-sm" />
                </div>

                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-300">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-3">Usuário / Escritório</th>
                                <th class="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Status</th>
                                <th class="relative py-3.5 pl-3 pr-4 sm:pr-3 text-right">Ações</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-slate-200">
                            <tr v-for="u in filteredGlobalUsers" :key="u.id">
                                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-3">
                                    <div class="font-bold text-slate-900 text-base">{{ u.nome }}</div>
                                    <div class="text-slate-500">{{ u.email }}</div>
                                    <div class="mt-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                                        {{ u.escritorio?.nome || 'N/A' }}
                                    </div>
                                </td>
                                <td class="whitespace-nowrap px-3 py-4 text-sm">
                                    <span :class="[u.ativo ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' : 'bg-amber-50 text-amber-700 ring-amber-600/20', 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset']">
                                        {{ u.ativo ? 'Ativo' : 'Pendente/Bloqueado' }}
                                    </span>
                                </td>
                                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-3">
                                    <div class="flex justify-end gap-2">
                                        <button v-if="!u.ativo" @click="handleAprovarGlobal(u.id)" class="text-emerald-600 hover:text-emerald-900">Aprovar</button>
                                        <button v-if="u.ativo && u.id !== currentUser?.id" @click="handleBloquearGlobal(u.id)" class="text-amber-600 hover:text-amber-900">Bloquear</button>
                                        <button v-if="u.id !== currentUser?.id" @click="handleExcluirGlobal(u.id)" class="text-red-600 hover:text-red-900">Excluir</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <!-- Modal Novo/Edição Usuário -->
    <div v-if="showUsuarioModal" class="relative z-50 pointer-events-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"></div>
        <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <div class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
                    
                    <form @submit.prevent="saveUsuario">
                        <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4 border-b border-slate-100">
                            <h3 class="text-lg font-semibold leading-6 text-slate-900 mb-6" id="modal-title">{{ isEditingUsuario ? 'Editar Membro da Equipe' : 'Adicionar Membro à Equipe' }}</h3>
                            
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">Nome Completo</label>
                                    <input v-model="formUsuario.nome" type="text" required class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">E-mail (Login)</label>
                                    <input v-model="formUsuario.email" type="email" required class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">CPF</label>
                                    <input v-model="formUsuario.cpf" type="text" v-maska data-maska="###.###.###-##" placeholder="000.000.000-00" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">
                                        Senha de Acesso 
                                        <span v-if="isEditingUsuario" class="text-slate-400 font-normal ml-1">(Deixe em branco para manter a atual)</span>
                                    </label>
                                    <input v-model="formUsuario.senha" type="password" :required="!isEditingUsuario" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                </div>

                                <div v-if="isAdmin() && currentUser.id !== formUsuario.id" class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Perfil (Área)</label>
                                        <select v-model="formUsuario.perfil" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                            <option value="Advogado">Advogado</option>
                                            <option value="Comercial">Comercial</option>
                                            <option value="Administrativo">Administrativo</option>
                                            <option value="Colaborador">Colaborador Geral</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Permissão Admin?</label>
                                        <select v-model="formUsuario.is_admin" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                            <option :value="false">Acesso Padrão</option>
                                            <option :value="true">Administrador</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                                        <select v-model="formUsuario.ativo" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                            <option :value="true">Ativo</option>
                                            <option :value="false">Bloqueado</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Tipo de Membro</label>
                                        <select v-model="formUsuario.tipo" class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                                            <option value="Humano">Humano</option>
                                            <option value="IA">Inteligência Artificial (IA)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-slate-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                            <button type="submit" :disabled="isSavingUsuario" class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 sm:ml-3 sm:w-auto">
                                {{ isSavingUsuario ? 'Salvando...' : 'Salvar Usuário' }}
                            </button>
                            <button @click="showUsuarioModal = false" type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 sm:mt-0 sm:w-auto">
                                Cancelar
                            </button>
                        </div>
                    </form>

                </div>
            </div>
        </div>
    </div>

    </div>
  </div>
</template>
