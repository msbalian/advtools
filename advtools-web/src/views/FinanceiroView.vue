<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  Plus, 
  Search, 
  Filter, 
  ArrowUpCircle, 
  ArrowDownCircle, 
  TrendingUp, 
  Calendar,
  MoreVertical,
  CheckCircle2,
  Clock,
  AlertCircle,
  X,
  CreditCard,
  DollarSign,
  Download
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

const loading = ref(true)
const escritorio = ref(null)
const currentUser = ref(null)
const sidebarOpen = ref(false)
const categorias = ref([])

const fluxoCaixa = ref({
    total_receitas: 0,
    total_despesas: 0,
    saldo: 0,
    transacoes: []
})

const mesAtual = ref(new Date().getMonth() + 1)
const anoAtual = ref(new Date().getFullYear())
const filterSearch = ref('')
const filtroAtivo = ref(null) // null, 'atrasados', 'recebidos', 'pagos', 'a_receber', 'a_pagar'

// Controle de UI
const notification = ref({ show: false, message: '', type: 'success' })
const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação' })
const activeMenu = ref(null) // ID da transação com menu aberto

const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmAction = (message, onConfirm, title = 'Confirmar Ação', onCancel = null, confirmText = 'Confirmar', cancelText = 'Cancelar') => {
    confirmDialog.value = { show: true, message, onConfirm, title, onCancel, confirmText, cancelText }
}

const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const executeCancel = async () => {
    if (confirmDialog.value.onCancel) {
        await confirmDialog.value.onCancel()
    }
    confirmDialog.value.show = false
}

const carregarDados = async () => {
    loading.value = true
    try {
        const [resFluxo, resEsc, resMe] = await Promise.all([
            apiFetch(`/api/financeiro/fluxo?mes=${mesAtual.value}&ano=${anoAtual.value}`),
            apiFetch('/api/escritorio'),
            apiFetch('/api/me')
        ])
        
        if (resFluxo.ok) fluxoCaixa.value = await resFluxo.json()
        if (resEsc.ok) escritorio.value = await resEsc.json()
        if (resMe.ok) currentUser.value = await resMe.json()

        const resCats = await apiFetch('/api/financeiro/categorias')
        if (resCats.ok) categorias.value = await resCats.json()
    } catch (e) {
        console.error("Erro ao carregar dados financeiros", e)
    } finally {
        loading.value = false
    }
}

const transacoesFiltradas = computed(() => {
    let list = fluxoCaixa.value.transacoes
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0)
    
    // Filtros Rápidos
    if (filtroAtivo.value === 'atrasados') {
        list = list.filter(t => t.tipo === 'Receita' && t.status === 'Pendente' && new Date(t.data_vencimento) < hoje)
    } else if (filtroAtivo.value === 'recebidos') {
        list = list.filter(t => t.tipo === 'Receita' && t.status === 'Pago')
    } else if (filtroAtivo.value === 'pagos') {
        list = list.filter(t => t.tipo === 'Despesa' && t.status === 'Pago')
    } else if (filtroAtivo.value === 'a_receber') {
        list = list.filter(t => t.tipo === 'Receita' && t.status === 'Pendente')
    } else if (filtroAtivo.value === 'a_pagar') {
        list = list.filter(t => t.tipo === 'Despesa' && t.status === 'Pendente')
    }

    if (!filterSearch.value) return list
    
    const search = filterSearch.value.toLowerCase()
    return list.filter(t => 
        t.descricao.toLowerCase().includes(search) || 
        (t.cliente?.nome.toLowerCase().includes(search))
    )
})

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' })
}

// Modal para nova transação
const showModal = ref(false)
const isEditing = ref(false)
const form = ref({
    tipo: 'Receita',
    categoria: 'Honorários',
    valor: 0,
    descricao: '',
    status: 'Pendente',
    data_vencimento: new Date().toISOString().split('T')[0],
    cliente_id: null,
    repetir: false,
    data_fim_recorrencia: null
})

const abrirNovaTransacao = () => {
    isEditing.value = false
    form.value = {
        tipo: 'Receita',
        categoria: 'Honorários',
        valor: 0,
        descricao: '',
        status: 'Pendente',
        data_vencimento: new Date().toISOString().split('T')[0],
        cliente_id: null,
        repetir: false,
        data_fim_recorrencia: null
    }
    showModal.value = true
}

const editarTransacao = (t) => {
    isEditing.value = true
    // Converte a data do banco para o padrão yyyy-MM-dd do input date
    const data_venc = t.data_vencimento ? t.data_vencimento.split('T')[0] : ''
    
    form.value = {
        id: t.id,
        tipo: t.tipo,
        categoria: t.categoria,
        valor: t.valor,
        descricao: t.descricao,
        status: t.status,
        data_vencimento: data_venc,
        cliente_id: t.cliente_id,
        recorrencia_id: t.recorrencia_id,
        update_series: false
    }
    activeMenu.value = null
    showModal.value = true
}

const salvarTransacao = async () => {
    // Se estiver editando e for recorrente, pergunta se quer atualizar a série
    if (isEditing.value && form.value.recorrencia_id) {
        confirmAction(
            "Este lançamento faz parte de uma recorrência. Deseja atualizar apenas este lançamento ou todas as parcelas futuras pendentes?",
            async () => {
                form.value.update_series = true
                await executarSalvar()
            },
            "Atualizar Recorrência",
            async () => {
                form.value.update_series = false
                await executarSalvar()
            },
            "Toda a Série",
            "Apenas Este"
        )
    } else {
        await executarSalvar()
    }
}

const executarSalvar = async () => {
    try {
        const method = isEditing.value ? 'PUT' : 'POST'
        const url = isEditing.value ? `/api/financeiro/transacoes/${form.value.id}` : '/api/financeiro/transacoes'
        
        const res = await apiFetch(url, {
            method,
            body: JSON.stringify(form.value)
        })
        if (res.ok) {
            showMessage(isEditing.value ? "Transação atualizada!" : "Transação criada!")
            showModal.value = false
            carregarDados()
        } else {
            showMessage("Erro ao salvar transação", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão", "error")
    }
}

const excluirTransacao = (t) => {
    activeMenu.value = null
    
    if (t.recorrencia_id) {
        confirmAction(
            "Este lançamento faz parte de uma recorrência. Deseja excluir apenas este lançamento ou todas as parcelas futuras pendentes?",
            async () => {
                await executarExclusao(t.id, true)
            },
            "Excluir Recorrência",
            async () => {
                await executarExclusao(t.id, false)
            },
            "Toda a Série",
            "Apenas Este"
        )
    } else {
        confirmAction(
            "Tem certeza que deseja excluir este lançamento? Esta ação não pode ser desfeita.",
            async () => {
                await executarExclusao(t.id, false)
            },
            "Excluir Lançamento"
        )
    }
}

const executarExclusao = async (id, deleteSeries) => {
    try {
        const res = await apiFetch(`/api/financeiro/transacoes/${id}?delete_series=${deleteSeries}`, { method: 'DELETE' })
        if (res.ok) {
            showMessage("Transação excluída com sucesso!")
            carregarDados()
        }
    } catch (e) {
        showMessage("Erro ao excluir", "error")
    }
}

const baixarRelatorio = () => {
    window.print()
}

onMounted(carregarDados)
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex" @click="activeMenu = null">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <main class="flex-1 flex flex-col p-4 sm:p-6 lg:p-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Financeiro</h1>
          <p class="mt-1 text-sm text-slate-500">Gestão de fluxo de caixa e transações do escritório.</p>
        </div>
        <div class="mt-4 sm:mt-0 flex gap-3">
          <button @click="baixarRelatorio" class="btn-secondary flex items-center gap-2">
            <Download class="w-4 h-4" /> Exportar
          </button>
          <button @click="abrirNovaTransacao" class="btn-primary flex items-center gap-2 shadow-primary-500/30">
            <Plus class="w-4 h-4" /> Novo Lançamento
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="card p-6 border-l-4 border-emerald-500">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-medium text-slate-500 uppercase">Receitas (Mês)</span>
            <ArrowUpCircle class="w-6 h-6 text-emerald-500" />
          </div>
          <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(fluxoCaixa.total_receitas) }}</p>
        </div>

        <div class="card p-6 border-l-4 border-red-500">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-medium text-slate-500 uppercase">Despesas (Mês)</span>
            <ArrowDownCircle class="w-6 h-6 text-red-500" />
          </div>
          <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(fluxoCaixa.total_despesas) }}</p>
        </div>

        <div class="card p-6 border-l-4 border-amber-500 bg-amber-50/20">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-medium text-slate-600 uppercase">Inadimplência</span>
            <AlertCircle class="w-6 h-6 text-amber-500" />
          </div>
          <p class="text-2xl font-bold text-amber-700">{{ formatCurrency(fluxoCaixa.total_atrasado) }}</p>
        </div>

        <div class="card p-6 border-l-4 border-primary-500">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-medium text-slate-500 uppercase">Saldo Operacional</span>
            <TrendingUp class="w-6 h-6 text-primary-500" />
          </div>
          <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(fluxoCaixa.saldo) }}</p>
        </div>
      </div>

      <!-- Filters & Monthly Selector -->
      <div class="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex items-center justify-between flex-wrap gap-4">
          <div class="flex items-center gap-4">
              <select v-model="mesAtual" @change="carregarDados" class="input py-1.5 w-40">
                  <option :value="1">Janeiro</option>
                  <option :value="2">Fevereiro</option>
                  <option :value="3">Março</option>
                  <option :value="4">Abril</option>
                  <option :value="5">Maio</option>
                  <option :value="6">Junho</option>
                  <option :value="7">Julho</option>
                  <option :value="8">Agosto</option>
                  <option :value="9">Setembro</option>
                  <option :value="10">Outubro</option>
                  <option :value="11">Novembro</option>
                  <option :value="12">Dezembro</option>
              </select>
              <select v-model="anoAtual" @change="carregarDados" class="input py-1.5 w-24">
                  <option :value="2024">2024</option>
                  <option :value="2025">2025</option>
                  <option :value="2026">2026</option>
              </select>
          </div>
          <div class="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar flex-1 lg:flex-none">
              <button 
                @click="filtroAtivo = null"
                :class="[filtroAtivo === null ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all"
              >
                Todos
              </button>
              <button 
                @click="filtroAtivo = 'atrasados'"
                :class="[filtroAtivo === 'atrasados' ? 'bg-red-600 text-white border-red-600 shadow-md shadow-red-200' : 'bg-white text-red-600 border-red-100 hover:border-red-200']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all flex items-center gap-1.5"
              >
                <Clock class="w-3.5 h-3.5" /> Atrasados
              </button>
              <button 
                @click="filtroAtivo = 'recebidos'"
                :class="[filtroAtivo === 'recebidos' ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-200' : 'bg-white text-emerald-600 border-emerald-100 hover:border-emerald-200']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all"
              >
                Recebidos
              </button>
              <button 
                @click="filtroAtivo = 'pagos'"
                :class="[filtroAtivo === 'pagos' ? 'bg-slate-600 text-white border-slate-600' : 'bg-white text-slate-600 border-slate-100 hover:border-slate-200']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all"
              >
                Pagos
              </button>
              <button 
                @click="filtroAtivo = 'a_receber'"
                :class="[filtroAtivo === 'a_receber' ? 'bg-amber-500 text-white border-amber-500 shadow-md shadow-amber-100' : 'bg-white text-amber-600 border-amber-100 hover:border-amber-200']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all"
              >
                A Receber
              </button>
              <button 
                @click="filtroAtivo = 'a_pagar'"
                :class="[filtroAtivo === 'a_pagar' ? 'bg-orange-500 text-white border-orange-500 shadow-md shadow-orange-100' : 'bg-white text-orange-600 border-orange-100 hover:border-orange-200']"
                class="whitespace-nowrap px-4 py-1.5 rounded-full border text-xs font-bold transition-all"
              >
                A Pagar
              </button>
          </div>
          <div class="flex items-center gap-3">
              <div class="relative">
                  <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input type="text" v-model="filterSearch" placeholder="Buscar descrição..." class="input pl-9 py-1.5 w-60 text-sm" />
              </div>
          </div>
      </div>

      <!-- Transactions Table -->
      <div class="card p-0 overflow-visible min-h-[400px]">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Data</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Descrição</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Categoria</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Status</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Valor</th>
              <th scope="col" class="relative px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 bg-white">
            <tr v-for="t in transacoesFiltradas" :key="t.id" @click="editarTransacao(t)" class="hover:bg-slate-50 transition-colors cursor-pointer group">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                {{ formatDate(t.data_vencimento) }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-slate-900 group-hover:text-primary-600 transition-colors">{{ t.descricao }}</div>
                <div class="text-xs text-slate-400" v-if="t.cliente">{{ t.cliente.nome }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800">
                  {{ t.categoria }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  t.status === 'Pago' ? 'bg-emerald-50 text-emerald-700' :
                  t.status === 'Atrasado' ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700',
                  'inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ring-1 ring-inset ring-current'
                ]">
                  {{ t.status }}
                </span>
              </td>
              <td :class="['px-6 py-4 whitespace-nowrap text-sm text-right font-bold', t.tipo === 'Receita' ? 'text-emerald-600' : 'text-red-600']">
                {{ t.tipo === 'Receita' ? '+' : '-' }} {{ formatCurrency(t.valor) }}
              </td>
              <td class="px-6 py-4 text-right" @click.stop>
                <div class="relative inline-block text-left">
                  <button @click.stop="activeMenu = activeMenu === t.id ? null : t.id" class="p-1 rounded-lg hover:bg-slate-100 transition-colors">
                    <MoreVertical class="w-5 h-5 text-slate-400" />
                  </button>
                  
                  <div v-if="activeMenu === t.id" class="absolute right-0 z-50 mt-2 w-36 rounded-xl bg-white shadow-2xl ring-1 ring-black/5 p-1">
                    <button @click="editarTransacao(t)" class="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-lg">
                      <Clock class="w-4 h-4 text-slate-400" /> Editar
                    </button>
                    <button @click="excluirTransacao(t)" class="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg font-bold">
                      <X class="w-4 h-4" /> Excluir
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="transacoesFiltradas.length === 0">
                <td colspan="6" class="px-6 py-12 text-center text-slate-400">
                    Nenhuma transação encontrada para este período.
                </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Toast Notification -->
      <div v-if="notification.show" 
           :class="[notification.type === 'success' ? 'bg-emerald-600' : 'bg-red-600']"
           class="fixed bottom-8 right-8 z-[2000] px-6 py-3 rounded-2xl text-white font-bold shadow-2xl flex items-center gap-3 animate-fade-in-up">
        <CheckCircle2 v-if="notification.type === 'success'" class="w-5 h-5" />
        <AlertCircle v-else class="w-5 h-5" />
        {{ notification.message }}
      </div>

      <!-- Confirm Dialog -->
      <div v-if="confirmDialog.show" class="fixed inset-0 z-[2001] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
        <div class="bg-white rounded-3xl shadow-2xl p-8 max-w-sm w-full border border-slate-100 flex flex-col items-center text-center animate-fade-in-up">
          <div class="h-16 w-16 bg-red-50 rounded-full flex items-center justify-center mb-4">
            <AlertCircle class="w-8 h-8 text-red-600" />
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
          <p class="text-slate-500 mb-8">{{ confirmDialog.message }}</p>
          <div class="flex gap-4 w-full">
            <button @click="executeCancel" class="flex-1 px-4 py-3 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-colors">{{ confirmDialog.cancelText || 'Cancelar' }}</button>
            <button @click="executeConfirm" class="flex-1 px-4 py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition-colors shadow-lg shadow-red-500/30">{{ confirmDialog.confirmText || 'Confirmar' }}</button>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal Nova Transação -->
    <div v-if="showModal" class="fixed inset-0 z-[100] overflow-y-auto">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" @click="showModal = false"></div>

        <div class="relative transform border border-slate-200 overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
          <div class="px-6 py-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-slate-900">{{ isEditing ? 'Editar Lançamento' : 'Novo Lançamento' }}</h3>
              <button @click="showModal = false" class="text-slate-400 hover:text-slate-600 transition-colors">
                <X class="w-6 h-6" />
              </button>
            </div>

            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Tipo</label>
                  <select v-model="form.tipo" class="input w-full">
                    <option value="Receita">Receita (Entrada)</option>
                    <option value="Despesa">Despesa (Saída)</option>
                  </select>
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Valor</label>
                    <div class="relative">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">R$</span>
                        <input type="number" step="0.01" v-model="form.valor" class="input w-full pl-9" />
                    </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Descrição</label>
                <input type="text" v-model="form.descricao" placeholder="Ex: Honorários Processo X" class="input w-full" />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Categoria</label>
                  <select v-model="form.categoria" class="input w-full">
                    <option v-for="cat in categorias.filter(c => c.tipo === form.tipo)" :key="cat.id">
                        {{ cat.nome }}
                    </option>
                    <option v-if="categorias.filter(c => c.tipo === form.tipo).length === 0">Outros</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Vencimento</label>
                  <input type="date" v-model="form.data_vencimento" class="input w-full" />
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Status</label>
                <select v-model="form.status" class="input w-full">
                  <option value="Pendente">Pendente</option>
                  <option value="Pago">Pago / Recebido</option>
                  <option value="Cancelado">Cancelado</option>
                </select>
              </div>

              <div v-if="!isEditing" class="pt-2">
                  <label class="flex items-center gap-2 cursor-pointer group">
                      <input type="checkbox" v-model="form.repetir" class="w-4 h-4 rounded text-primary-600 border-slate-300 focus:ring-primary-500" />
                      <span class="text-sm font-semibold text-slate-700 group-hover:text-primary-600 transition-colors">Repetir mensalmente</span>
                  </label>
                  
                  <div v-if="form.repetir" class="mt-3 animate-fade-in">
                      <label class="block text-sm font-semibold text-slate-700 mb-1">Repetir até</label>
                      <input type="date" v-model="form.data_fim_recorrencia" class="input w-full" />
                      <p class="mt-1 text-xs text-slate-400">Serão gerados lançamentos mensais até esta data.</p>
                  </div>
              </div>
            </div>
          </div>

          <div class="bg-slate-50 px-6 py-4 flex justify-end gap-3">
            <button @click="showModal = false" class="px-4 py-2 text-sm font-bold text-slate-600 hover:text-slate-800 transition-colors">Cancelar</button>
            <button @click="salvarTransacao" class="btn-primary shadow-primary-500/20">{{ isEditing ? 'Salvar Alterações' : 'Criar Lançamento' }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
