<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import { vMaska } from 'maska/vue'
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
  Plus,
  FolderOpen,
  Scale,
  CreditCard,
  ArrowUpCircle,
  ArrowDownCircle,
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
// ESTADO: CONFIGURAÇÕES EXTRAS
// =======================
const pastasTrabalho = ref([])
const tiposServico = ref([])
const categoriasFinanceiras = ref([])
const newPastaNome = ref('')
const newTipoNome = ref('')
const newCategoriaNome = ref('')
const newCategoriaTipo = ref('Receita')

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
  await loadConfiguracoesExtras()
  if (currentUser.value?.is_admin) {
    await loadUsuariosGlobais()
  }
  isLoading.value = false
})

const loadConfiguracoesExtras = async () => {
    try {
        const [resPastas, resTipos] = await Promise.all([
            apiFetch('/api/configuracoes/pastas-trabalho'),
            apiFetch('/api/configuracoes/tipos-servico')
        ])
        if (resPastas.ok) pastasTrabalho.value = await resPastas.json()
        if (resTipos.ok) tiposServico.value = await resTipos.json()
        
        const resCats = await apiFetch('/api/financeiro/categorias')
        if (resCats.ok) categoriasFinanceiras.value = await resCats.json()
    } catch (e) {
        console.error("Erro ao carregar configurações extras", e)
    }
}

const addPastaTrabalho = async () => {
    console.log("Clicou adicionar pasta. Valor:", newPastaNome.value);
    if (!newPastaNome.value) {
        console.warn("Input de pasta vazio. Retornando early.");
        showMessage("Por favor, digite o nome da pasta.", "error");
        return;
    }
    try {
        console.log("Fazendo fetch de pasta...");        const res = await apiFetch('/api/configuracoes/pastas-trabalho', {
            method: 'POST',
            body: JSON.stringify({ nome: newPastaNome.value })
        })
        if (res.ok) {
            newPastaNome.value = ''
            await loadConfiguracoesExtras()
            showMessage("Pasta de trabalho adicionada!")
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao adicionar pasta", "error")
        }
    } catch (e) { showMessage("Erro de conexão", "error") }
}

const deletePastaTrabalho = (id) => {
    confirmAction("Deseja excluir esta pasta de trabalho?", async () => {
        try {
            const res = await apiFetch(`/api/configuracoes/pastas-trabalho/${id}`, { method: 'DELETE' })
            if (res.ok) {
                await loadConfiguracoesExtras()
                showMessage("Pasta excluída!")
            }
        } catch (e) { showMessage("Erro ao excluir", "error") }
    })
}

const addTipoServico = async () => {
    console.log("Clicou adicionar serviço. Valor:", newTipoNome.value);
    if (!newTipoNome.value) {
        console.warn("Input de tipo de serviço vazio. Retornando early.");
        showMessage("Por favor, digite o nome do tipo de serviço.", "error");
        return;
    }
    try {
        console.log("Fazendo fetch de tipo de serviço...");        const res = await apiFetch('/api/configuracoes/tipos-servico', {
            method: 'POST',
            body: JSON.stringify({ nome: newTipoNome.value })
        })
        if (res.ok) {
            newTipoNome.value = ''
            await loadConfiguracoesExtras()
            showMessage("Tipo de serviço adicionado!")
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao adicionar tipo", "error")
        }
    } catch (e) { showMessage("Erro de conexão", "error") }
}

const deleteTipoServico = (id) => {
    confirmAction("Deseja excluir este tipo de serviço?", async () => {
        try {
            const res = await apiFetch(`/api/configuracoes/tipos-servico/${id}`, { method: 'DELETE' })
            if (res.ok) {
                await loadConfiguracoesExtras()
                showMessage("Tipo excluído!")
            }
        } catch (e) { showMessage("Erro ao excluir", "error") }
    })
}

const addCategoriaFinanceira = async () => {
    if (!newCategoriaNome.value) {
        showMessage("Por favor, digite o nome da categoria.", "error");
        return;
    }
    try {
        const res = await apiFetch('/api/financeiro/categorias', {
            method: 'POST',
            body: JSON.stringify({ nome: newCategoriaNome.value, tipo: newCategoriaTipo.value })
        })
        if (res.ok) {
            newCategoriaNome.value = ''
            await loadConfiguracoesExtras()
            showMessage("Categoria financeira adicionada!")
        }
    } catch (e) { showMessage("Erro de conexão", "error") }
}

const deleteCategoriaFinanceira = (id) => {
    confirmAction("Deseja excluir esta categoria financeira?", async () => {
        try {
            const res = await apiFetch(`/api/financeiro/categorias/${id}`, { method: 'DELETE' })
            if (res.ok) {
                await loadConfiguracoesExtras()
                showMessage("Categoria excluída!")
            }
        } catch (e) { showMessage("Erro ao excluir", "error") }
    })
}

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
            const baseUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/static/${escritorio.value.logo_path}`
            const timestamp = escritorio.value.data_atualizacao ? new Date(escritorio.value.data_atualizacao).getTime() : Date.now()
            logoPreview.value = `${baseUrl}?t=${timestamp}`
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

const tabItems = computed(() => {
    const items = [
        { id: 'escritorio', label: 'Meu Escritório', icon: Building2 },
        { id: 'equipe', label: 'Gestão da Equipe', icon: Users },
        { id: 'pastas', label: 'Pastas de Trabalho', icon: FolderOpen },
        { id: 'servicos', label: 'Tipos de Serviço', icon: Scale },
        { id: 'financeiro', label: 'Financeiro', icon: CreditCard },
    ]
    if (currentUser.value?.is_admin) {
        items.push({ id: 'global', label: 'Gestão Global', icon: ShieldCheck })
    }
    return items
})

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
    <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
        
        <div class="mb-10">
            <h1 class="text-4xl font-bold text-slate-900 mb-2">Configurações do Sistema</h1>
            <p class="text-slate-500 text-base mt-1">Gerencie os dados do seu escritório e o acesso da sua equipe com segurança e clareza.</p>
        </div>

        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="flex flex-col items-center gap-4">
                <div class="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
                <div class="text-slate-500 font-medium">Carregando configurações...</div>
            </div>
        </div>

        <div v-else class="flex flex-col lg:flex-row gap-8 items-start">
            <!-- Sidebar Interna de Navegação -->
            <aside class="w-full lg:w-72 flex-shrink-0 bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden lg:sticky lg:top-24">
                <div class="p-4 bg-slate-50 border-b border-slate-100 lg:hidden">
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Navegação</span>
                </div>
                <nav class="flex flex-col p-2 space-y-1">
                    <button 
                        v-for="item in tabItems" 
                        :key="item.id"
                        @click="activeTab = item.id"
                        :class="[
                            activeTab === item.id 
                                ? 'bg-primary-50 text-primary-700 shadow-sm ring-1 ring-primary-100' 
                                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900', 
                            'group flex items-center gap-4 px-6 py-4 rounded-2xl text-sm font-bold transition-all duration-200 cursor-pointer'
                        ]"
                    >
                        <component :is="item.icon" class="w-5 h-5 flex-shrink-0" :class="activeTab === item.id ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-600'" />
                        {{ item.label }}
                    </button>
                </nav>
            </aside>

            <!-- Área de Conteúdo Pro Max -->
            <div class="flex-1 w-full bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden min-h-[600px]">

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
                                <input v-model="escritorio.nome" type="text" required :disabled="!isAdmin()" class="input-field" />
                            </div>
                        </div>

                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:pt-5">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">CNPJ / CPF do Titular</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <input v-model="escritorio.documento" type="text" v-maska data-maska="['###.###.###-##', '##.###.###/####-##']" :disabled="!isAdmin()" class="input-field max-w-md" />
                            </div>
                        </div>

                        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:pt-5 sm:border-t sm:border-slate-100">
                            <label class="block text-sm font-medium leading-6 text-slate-900 sm:pt-1.5">Gemini API Key (IA)</label>
                            <div class="mt-2 sm:col-span-2 sm:mt-0">
                                <input v-model="escritorio.gemini_api_key" type="text" :disabled="!isAdmin()" placeholder="AIza..." class="input-field" />
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

            <!-- Tab Content: Pastas de Trabalho -->
            <div v-if="activeTab === 'pastas'" class="p-6">
                <div class="mb-6">
                    <h2 class="text-base font-semibold text-slate-900">Pastas de Trabalho / Áreas</h2>
                    <p class="text-sm text-slate-500">Defina as áreas de atuação do escritório para categorizar seus processos.</p>
                </div>

                <div class="flex gap-4 mb-8">
                    <input v-model="newPastaNome" type="text" placeholder="Ex: Direito Médico, Direito Civil..." class="input-field max-w-sm" />
                    <button @click="addPastaTrabalho" class="btn-primary flex items-center gap-2">
                        <Plus class="w-4 h-4" /> Adicionar
                    </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div v-for="item in pastasTrabalho" :key="item.id" class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between group">
                        <span class="font-bold text-slate-700">{{ item.nome }}</span>
                        <button @click="deletePastaTrabalho(item.id)" class="p-1.5 text-slate-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100">
                            <Trash2 class="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Tipos de Serviço -->
            <div v-if="activeTab === 'servicos'" class="p-6">
                <div class="mb-6">
                    <h2 class="text-base font-semibold text-slate-900">Tipos de Serviço</h2>
                    <p class="text-sm text-slate-500">Defina os tipos de serviços/contratos que o escritório realiza.</p>
                </div>

                <div class="flex gap-4 mb-8">
                    <input v-model="newTipoNome" type="text" placeholder="Ex: Ação Cível, Revisão de Contrato..." class="input-field max-w-sm" />
                    <button @click="addTipoServico" class="btn-primary flex items-center gap-2">
                        <Plus class="w-4 h-4" /> Adicionar
                    </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div v-for="item in tiposServico" :key="item.id" class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between group">
                        <span class="font-bold text-slate-700">{{ item.nome }}</span>
                        <button @click="deleteTipoServico(item.id)" class="p-1.5 text-slate-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100">
                            <Trash2 class="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Financeiro (Categorias) -->
            <div v-if="activeTab === 'financeiro'" class="p-6">
                <div class="mb-6">
                    <h2 class="text-base font-semibold text-slate-900">Categorias Financeiras</h2>
                    <p class="text-sm text-slate-500">Gerencie as categorias de receitas e despesas do seu escritório.</p>
                </div>

                <div class="flex flex-wrap gap-4 mb-8 items-end">
                    <div class="flex-1 min-w-[200px]">
                        <label class="block text-xs font-semibold text-slate-500 mb-1">NOME DA CATEGORIA</label>
                        <input v-model="newCategoriaNome" type="text" placeholder="Ex: Honorários, Aluguel..." class="input-field" />
                    </div>
                    <div class="w-32">
                        <label class="block text-xs font-semibold text-slate-500 mb-1">TIPO</label>
                        <select v-model="newCategoriaTipo" class="input-field">
                            <option value="Receita">Receita</option>
                            <option value="Despesa">Despesa</option>
                        </select>
                    </div>
                    <button @click="addCategoriaFinanceira" class="btn-primary flex items-center gap-2">
                        <Plus class="w-4 h-4" /> Adicionar
                    </button>
                </div>

                <div class="space-y-6">
                    <!-- Receitas -->
                    <div>
                        <h3 class="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <ArrowUpCircle class="w-4 h-4" /> Receitas
                        </h3>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div v-for="cat in categoriasFinanceiras.filter(c => c.tipo === 'Receita')" :key="cat.id" class="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100 flex items-center justify-between group">
                                <span class="font-bold text-emerald-800">{{ cat.nome }}</span>
                                <button @click="deleteCategoriaFinanceira(cat.id)" class="p-1.5 text-emerald-300 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </div>
                            <div v-if="!categoriasFinanceiras.some(c => c.tipo === 'Receita')" class="col-span-full py-4 text-center text-slate-400 text-sm border-2 border-dashed border-slate-100 rounded-xl">
                                Nenhuma categoria de receita cadastrada.
                            </div>
                        </div>
                    </div>

                    <!-- Despesas -->
                    <div>
                        <h3 class="text-xs font-bold text-red-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <ArrowDownCircle class="w-4 h-4" /> Despesas
                        </h3>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div v-for="cat in categoriasFinanceiras.filter(c => c.tipo === 'Despesa')" :key="cat.id" class="p-4 bg-red-50/50 rounded-xl border border-red-100 flex items-center justify-between group">
                                <span class="font-bold text-red-800">{{ cat.nome }}</span>
                                <button @click="deleteCategoriaFinanceira(cat.id)" class="p-1.5 text-red-300 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </div>
                            <div v-if="!categoriasFinanceiras.some(c => c.tipo === 'Despesa')" class="col-span-full py-4 text-center text-slate-400 text-sm border-2 border-dashed border-slate-100 rounded-xl">
                                Nenhuma categoria de despesa cadastrada.
                            </div>
                        </div>
                    </div>
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
            </div> <!-- Fim da Aba Global -->
        </div> <!-- Fim da Área de Conteúdo -->
    </div> <!-- Fim do Container Flex (v-else) -->
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
                                    <input v-model="formUsuario.nome" type="text" required class="input-field">
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">E-mail (Login)</label>
                                    <input v-model="formUsuario.email" type="email" required class="input-field">
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">CPF</label>
                                    <input v-model="formUsuario.cpf" type="text" v-maska data-maska="###.###.###-##" placeholder="000.000.000-00" class="input-field">
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">
                                        Senha de Acesso 
                                        <span v-if="isEditingUsuario" class="text-slate-400 font-normal ml-1">(Deixe em branco para manter a atual)</span>
                                    </label>
                                    <input v-model="formUsuario.senha" type="password" :required="!isEditingUsuario" class="input-field">
                                </div>

                                <div v-if="isAdmin() && currentUser.id !== formUsuario.id" class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Perfil (Área)</label>
                                        <select v-model="formUsuario.perfil" class="input-field">
                                            <option value="Advogado">Advogado</option>
                                            <option value="Comercial">Comercial</option>
                                            <option value="Administrativo">Administrativo</option>
                                            <option value="Colaborador">Colaborador Geral</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Permissão Admin?</label>
                                        <select v-model="formUsuario.is_admin" class="input-field">
                                            <option :value="false">Acesso Padrão</option>
                                            <option :value="true">Administrador</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                                        <select v-model="formUsuario.ativo" class="input-field">
                                            <option :value="true">Ativo</option>
                                            <option :value="false">Bloqueado</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-slate-700 mb-1">Tipo de Membro</label>
                                        <select v-model="formUsuario.tipo" class="input-field">
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


    <!-- Notificações -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="notification.show" class="fixed bottom-4 right-4 z-[100] w-full max-w-sm overflow-hidden rounded-xl bg-white shadow-2xl ring-1 ring-black ring-opacity-5 border-l-4" :class="notification.type === 'success' ? 'border-emerald-500' : 'border-red-500'">
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <CheckCircle2 v-if="notification.type === 'success'" class="h-6 w-6 text-emerald-500" />
              <AlertCircle v-else class="h-6 w-6 text-red-500" />
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-bold text-slate-900">{{ notification.message }}</p>
            </div>
            <div class="ml-4 flex flex-shrink-0">
              <button @click="notification.show = false" class="inline-flex rounded-md bg-white text-slate-400 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500">
                <X class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Confirmação -->
    <div v-if="confirmDialog.show" class="relative z-[100]" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"></div>
        <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <div class="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6">
                    <div>
                        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
                            <AlertCircle class="h-6 w-6 text-amber-600" aria-hidden="true" />
                        </div>
                        <div class="mt-3 text-center sm:mt-5">
                            <h3 class="text-base font-semibold leading-6 text-slate-900" id="modal-title">Confirmação</h3>
                            <div class="mt-2 text-sm text-slate-500">
                                {{ confirmDialog.message }}
                            </div>
                        </div>
                    </div>
                    <div class="mt-5 sm:mt-6 flex gap-3">
                        <button type="button" @click="confirmDialog.show = false" class="inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 sm:text-sm">Cancelar</button>
                        <button type="button" @click="executeConfirm" class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:text-sm">Confirmar</button>
                    </div>
                </div>
            </div>
    </div>
    </div>
    </div>
  </div>
</template>
