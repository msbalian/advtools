<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import { 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  Calendar as CalendarIcon,
  Filter,
  Search,
  CheckCircle2,
  AlertCircle,
  Menu,
  MoreVertical,
  Briefcase,
  User as UserIcon,
  Check
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import TarefaFormModal from '../components/TarefaFormModal.vue'
import TarefaBadge from '../components/TarefaBadge.vue'

dayjs.locale('pt-br')

const router = useRouter()

// State
const sidebarOpen = ref(false)
const escritorio = ref(null)
const currentUser = ref(null)
const loading = ref(true)
const tarefas = ref([])
const usuarios = ref([])
const clientes = ref([])

// Calendar State
const currentMonth = ref(dayjs())
const viewMode = ref('month') // 'month', 'week', 'day'

// Computed range for fetching tasks
const visibleRange = computed(() => {
    let start, end
    if (viewMode.value === 'month') {
        start = currentMonth.value.startOf('month').startOf('week')
        end = currentMonth.value.endOf('month').endOf('week')
    } else if (viewMode.value === 'week') {
        start = currentMonth.value.startOf('week')
        end = currentMonth.value.endOf('week')
    } else {
        start = currentMonth.value.startOf('day')
        end = currentMonth.value.endOf('day')
    }
    return { start, end }
})

// Modal State
const showTarefaModal = ref(false)
const isEditingTarefa = ref(false)
const isSubmittingTarefa = ref(false)
const selectedTarefa = ref(null)

// Notification State
const notification = ref({ show: false, message: '', type: 'success' })

const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const carregarDadosIniciais = async () => {
    loading.value = true
    try {
        const [resEsc, resUser, resUsuarios, resClientes] = await Promise.all([
            apiFetch('/api/escritorio'),
            apiFetch('/api/me'),
            apiFetch('/api/usuarios'),
            apiFetch('/api/clientes')
        ])
        
        if (resEsc.ok) escritorio.value = await resEsc.json()
        if (resUser.ok) currentUser.value = await resUser.json()
        if (resUsuarios.ok) usuarios.value = await resUsuarios.json()
        if (resClientes.ok) clientes.value = await resClientes.json()
        
        await carregarTarefas()
    } catch (e) {
        console.error("Erro ao carregar dados iniciais", e)
    } finally {
        loading.value = false
    }
}

const carregarTarefas = async () => {
    const { start, end } = visibleRange.value
    // Usamos o início e fim do dia sem o 'Z' para evitar confusão de timezone no backend naive
    const dataInicio = start.startOf('day').format('YYYY-MM-DDTHH:mm:ss')
    const dataFim = end.endOf('day').format('YYYY-MM-DDTHH:mm:ss')
    
    const url = `/api/tarefas?data_inicio=${dataInicio}&data_fim=${dataFim}`
    
    try {
        const res = await apiFetch(url)
        if (res.ok) {
            const data = await res.json()
            tarefas.value = data
            console.log(`[Agenda] Carregadas ${data.length} tarefas. Range: ${dataInicio} até ${dataFim}`)
        } else {
            const err = await res.text()
            console.error(`[Agenda] Erro API: ${res.status}`, err)
        }
    } catch (e) {
        console.error("[Agenda] Erro de conexão ao carregar tarefas", e)
    }
}

// Calendar Logic
const daysInCalendar = computed(() => {
    // Garantimos que trabalhamos com o início do dia para evitar problemas de comparação
    if (viewMode.value === 'month') {
        const start = currentMonth.value.startOf('month').startOf('week')
        const end = currentMonth.value.endOf('month').endOf('week')
        const days = []
        let current = start.startOf('day')
        while (current.isBefore(end) || current.isSame(end, 'day')) {
            days.push(current)
            current = current.add(1, 'day')
        }
        return days
    } else if (viewMode.value === 'week') {
        const start = currentMonth.value.startOf('week').startOf('day')
        const days = []
        for (let i = 0; i < 7; i++) {
            days.push(start.add(i, 'day'))
        }
        return days
    } else {
        return [currentMonth.value.startOf('day')]
    }
})

const nextPeriod = () => {
    if (viewMode.value === 'month') currentMonth.value = currentMonth.value.add(1, 'month')
    else if (viewMode.value === 'week') currentMonth.value = currentMonth.value.add(1, 'week')
    else currentMonth.value = currentMonth.value.add(1, 'day')
}

const prevPeriod = () => {
    if (viewMode.value === 'month') currentMonth.value = currentMonth.value.subtract(1, 'month')
    else if (viewMode.value === 'week') currentMonth.value = currentMonth.value.subtract(1, 'week')
    else currentMonth.value = currentMonth.value.subtract(1, 'day')
}

const goToToday = () => {
    currentMonth.value = dayjs()
}

const getTarefasDay = (day) => {
    if (!tarefas.value) return []
    const dayStr = day.format('YYYY-MM-DD')
    return tarefas.value.filter(t => {
        if (!t.data_vencimento) return false
        return dayjs(t.data_vencimento).format('YYYY-MM-DD') === dayStr
    })
}

const selectDay = (day) => {
    isEditingTarefa.value = false
    selectedTarefa.value = {
        titulo: '',
        descricao: '',
        status: 'Pendente',
        prioridade: 'Normal',
        data_vencimento: day.hour(9).minute(0).toISOString(),
        cliente_id: null,
        processo_id: null,
        responsavel_id: currentUser.value?.id || null
    }
    showTarefaModal.value = true
}

const editarTarefa = (tarefa) => {
    isEditingTarefa.value = true
    selectedTarefa.value = { ...tarefa }
    showTarefaModal.value = true
}

const handleTarefaSubmit = async (dados) => {
    isSubmittingTarefa.value = true
    try {
        const method = isEditingTarefa.value ? 'PATCH' : 'POST'
        const url = isEditingTarefa.value ? `/api/tarefas/${dados.id}` : '/api/tarefas'
        
        const res = await apiFetch(url, {
            method,
            body: JSON.stringify(dados)
        })

        if (res.ok) {
            showMessage(isEditingTarefa.value ? "Tarefa atualizada!" : "Tarefa criada!", "success")
            showTarefaModal.value = false
            await carregarTarefas()
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao salvar tarefa", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão.", "error")
    } finally {
        isSubmittingTarefa.value = false
    }
}

const toggleTarefaStatus = async (tarefa) => {
    const newStatus = tarefa.status === 'Concluída' ? 'Pendente' : 'Concluída'
    try {
        const res = await apiFetch(`/api/tarefas/${tarefa.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        })
        if (res.ok) {
            tarefa.status = newStatus
            showMessage(newStatus === 'Concluída' ? "Tarefa concluída! 🎉" : "Tarefa reaberta.")
            await carregarTarefas()
        }
    } catch (e) {
        showMessage("Erro ao atualizar status", "error")
    }
}

watch(currentMonth, carregarTarefas)
watch(viewMode, carregarTarefas)

onMounted(carregarDadosIniciais)

const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <!-- Header -->
      <header class="bg-white border-b border-slate-200 px-4 sm:px-8 py-5 flex flex-col gap-4 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 text-slate-500">
               <Menu class="w-6 h-6" />
            </button>
            <div>
              <h1 class="text-2xl font-bold text-slate-900 flex items-center gap-3">
                <CalendarIcon class="w-7 h-7 text-primary-600" />
                Agenda Jurídica
              </h1>
              <p class="text-slate-500 text-sm">Visualize seus prazos e compromissos</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <div class="bg-slate-100 p-1 rounded-xl flex items-center">
              <button @click="viewMode = 'month'" :class="['px-4 py-1.5 text-xs font-bold rounded-lg transition-all', viewMode === 'month' ? 'bg-white shadow text-primary-600' : 'text-slate-500 hover:text-slate-700']">Mês</button>
              <button @click="viewMode = 'week'" :class="['px-4 py-1.5 text-xs font-bold rounded-lg transition-all', viewMode === 'week' ? 'bg-white shadow text-primary-600' : 'text-slate-500 hover:text-slate-700']">Semana</button>
              <button @click="viewMode = 'day'" :class="['px-4 py-1.5 text-xs font-bold rounded-lg transition-all', viewMode === 'day' ? 'bg-white shadow text-primary-600' : 'text-slate-500 hover:text-slate-700']">Dia</button>
            </div>
            <button @click="selectDay(viewMode === 'day' ? currentMonth : dayjs())" class="btn-primary flex items-center gap-2">
                <Plus class="w-5 h-5" /> Novo Compromisso
            </button>
          </div>
        </div>

        <!-- Calendar Controls -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
                <h2 class="text-xl font-bold text-slate-800 capitalize">
                  {{ viewMode === 'day' ? currentMonth.format('DD [de] MMMM [de] YYYY') : currentMonth.format('MMMM [de] YYYY') }}
                </h2>
                <div class="flex items-center bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                    <button @click="prevPeriod" class="p-2 hover:bg-slate-50 text-slate-500 border-r border-slate-200"><ChevronLeft class="w-5 h-5" /></button>
                    <button @click="goToToday" class="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50">Hoje</button>
                    <button @click="nextPeriod" class="p-2 hover:bg-slate-50 text-slate-500 border-l border-slate-200"><ChevronRight class="w-5 h-5" /></button>
                </div>
            </div>
            
            <div class="flex items-center gap-2">
                <div class="flex items-center gap-4 text-xs font-medium text-slate-500 mr-4">
                    <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Concluída</div>
                    <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-primary-500"></span> Normal</div>
                    <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span> Importante</div>
                </div>
            </div>
        </div>
      </header>

      <!-- Calendar Content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50">
        <div v-if="loading && tarefas.length === 0" class="flex flex-col items-center justify-center py-20">
          <div class="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin mb-4"></div>
          <p class="text-slate-500 font-medium">Sincronizando compromissos...</p>
        </div>

        <div v-else class="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden flex flex-col h-full min-h-[600px]">
          <!-- Weekday Headers (Only for Month and Week) -->
          <div v-if="viewMode !== 'day'" class="grid grid-cols-7 border-b border-slate-200 bg-slate-50/50">
            <div v-for="day in weekDays" :key="day" class="py-3 text-center text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ day }}</div>
          </div>

          <!-- Month/Week Grid -->
          <div v-if="viewMode !== 'day'" class="grid grid-cols-7 flex-1">
            <div v-for="day in daysInCalendar" :key="day.format('YYYY-MM-DD')" 
                 :class="['min-h-[120px] p-2 border-r border-b border-slate-100 hover:bg-slate-50/50 transition-colors flex flex-col gap-1 cursor-pointer', 
                 day.isSame(dayjs(), 'day') ? 'bg-primary-50/20' : '',
                 (viewMode === 'month' && day.month() !== currentMonth.month()) ? 'opacity-40 bg-slate-50/30' : 'bg-white']"
                 @click="selectDay(day)">
              
              <div class="flex items-center justify-between mb-1">
                <span :class="['text-sm font-bold w-7 h-7 flex items-center justify-center rounded-lg', 
                       day.isSame(dayjs(), 'day') ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/30' : 'text-slate-600']">
                  {{ day.date() }}
                </span>
                <span v-if="getTarefasDay(day).length > 0" class="text-[9px] font-black text-slate-300 bg-slate-100 px-1.5 py-0.5 rounded-md">
                   {{ getTarefasDay(day).length }}
                </span>
              </div>

              <!-- Task List in Cell -->
              <div class="flex flex-col gap-1 overflow-y-auto max-h-[140px] pr-1">
                <div v-for="tarefa in getTarefasDay(day).slice(0, 5)" :key="tarefa.id" 
                     @click.stop="editarTarefa(tarefa)"
                     :class="['group px-2 py-1.5 rounded-lg border text-[11px] font-bold transition-all truncate flex items-center gap-2', 
                     tarefa.status === 'Concluída' ? 'bg-emerald-50 border-emerald-100 text-emerald-700 opacity-60' : 
                     (tarefa.prioridade === 'Alta' || tarefa.prioridade === 'Urgente' ? 'bg-red-50 border-red-100 text-red-700 shadow-sm shadow-red-500/10' : 'bg-white border-slate-200 text-slate-700 hover:border-primary-300')]"
                     :title="tarefa.titulo">
                  
                  <div v-if="tarefa.status === 'Concluída'" class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></div>
                  <div v-else :class="['w-1.5 h-1.5 rounded-full shrink-0', 
                       (tarefa.prioridade === 'Alta' || tarefa.prioridade === 'Urgente') ? 'bg-red-500' : 'bg-primary-500']"></div>
                  
                  <span :class="['truncate', tarefa.status === 'Concluída' ? 'line-through' : '']">{{ tarefa.titulo }}</span>
                </div>
                <div v-if="getTarefasDay(day).length > 5" class="text-[10px] text-center font-bold text-slate-400 py-1">
                  + {{ getTarefasDay(day).length - 5 }} mais...
                </div>
              </div>
            </div>
          </div>

          <!-- Day View Layout -->
          <div v-else class="flex flex-col flex-1 overflow-y-auto">
            <div class="p-8 border-b border-slate-100 bg-slate-50/30">
              <div class="flex items-center gap-6">
                 <div class="text-center">
                    <span class="block text-sm font-black text-primary-600 uppercase tracking-widest mb-1">{{ currentMonth.format('ddd') }}</span>
                    <span class="text-5xl font-black text-slate-900 leading-none">{{ currentMonth.format('DD') }}</span>
                 </div>
                 <div class="h-16 w-px bg-slate-200"></div>
                 <div>
                    <h3 class="text-xl font-bold text-slate-900 capitalize">{{ currentMonth.format('MMMM [de] YYYY') }}</h3>
                    <p class="text-slate-500 font-medium">{{ getTarefasDay(currentMonth).length }} tarefas agendadas para hoje</p>
                 </div>
              </div>
            </div>

            <div class="p-8 space-y-4">
              <div v-if="getTarefasDay(currentMonth).length === 0" class="flex flex-col items-center justify-center py-20 text-center">
                <div class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6">
                   <CalendarIcon class="w-10 h-10 text-slate-300" />
                </div>
                <h4 class="text-lg font-bold text-slate-800">Nenhuma tarefa para este dia</h4>
                <p class="text-slate-500 max-w-xs mx-auto mt-2">Aproveite para organizar seu fluxo de trabalho ou clique em + Novo Compromisso.</p>
              </div>

              <div v-for="tarefa in getTarefasDay(currentMonth)" :key="tarefa.id"
                   @click="editarTarefa(tarefa)"
                   class="group bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-xl hover:border-primary-200 transition-all cursor-pointer flex items-center justify-between">
                <div class="flex items-center gap-6">
                  <div :class="['w-16 h-16 rounded-xl flex flex-col items-center justify-center shrink-0 border transition-colors', 
                       tarefa.status === 'Concluída' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 
                       (tarefa.prioridade === 'Alta' || tarefa.prioridade === 'Urgente' ? 'bg-red-50 border-red-100 text-red-600' : 'bg-primary-50 border-primary-100 text-primary-600')]">
                    <span class="text-xs font-black uppercase tracking-tighter">{{ dayjs(tarefa.data_vencimento).format('HH:mm') }}</span>
                    <Check v-if="tarefa.status === 'Concluída'" class="w-5 h-5 mt-1" />
                    <AlertCircle v-else :class="['w-5 h-5 mt-1', tarefa.prioridade === 'Normal' ? 'text-primary-400' : '']" />
                  </div>
                  
                  <div>
                    <h4 :class="['text-lg font-bold text-slate-900 group-hover:text-primary-700 transition-colors', tarefa.status === 'Concluída' ? 'line-through text-slate-400' : '']">
                      {{ tarefa.titulo }}
                    </h4>
                    <div class="flex items-center gap-4 mt-2">
                       <TarefaBadge :status="tarefa.status" />
                       <TarefaBadge :prioridade="tarefa.prioridade" />
                       <div v-if="tarefa.cliente" class="flex items-center gap-1.5 text-xs text-slate-500 font-bold">
                          <UserIcon class="w-3.5 h-3.5" /> {{ tarefa.cliente.nome }}
                       </div>
                       <div v-if="tarefa.processo" class="flex items-center gap-1.5 text-xs text-slate-500 font-bold">
                          <Briefcase class="w-3.5 h-3.5" /> {{ tarefa.processo.numero_processo }}
                       </div>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                   <button @click.stop="toggleTarefaStatus(tarefa)" 
                           :class="['p-3 rounded-xl border transition-all', tarefa.status === 'Concluída' ? 'bg-slate-100 text-slate-400 border-slate-200' : 'bg-emerald-50 text-emerald-600 border-emerald-200 hover:bg-emerald-600 hover:text-white']">
                     <Check class="w-5 h-5" />
                   </button>
                   <button class="p-3 bg-slate-50 text-slate-400 border border-slate-200 rounded-xl hover:bg-slate-200 hover:text-slate-600 transition-all">
                     <MoreVertical class="w-5 h-5" />
                   </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Notification Toast -->
      <div v-if="notification.show" 
           :class="[notification.type === 'success' ? 'bg-emerald-600' : 'bg-red-600']"
           class="fixed top-8 right-8 z-[1001] px-6 py-3 rounded-2xl text-white font-bold shadow-2xl flex items-center gap-3 animate-fade-in-down">
        <CheckCircle2 v-if="notification.type === 'success'" class="w-5 h-5" />
        <AlertCircle v-else class="w-5 h-5" />
        {{ notification.message }}
      </div>

      <!-- Modal -->
      <TarefaFormModal
        :show="showTarefaModal"
        :tarefa="selectedTarefa"
        :isEditing="isEditingTarefa"
        :isSubmitting="isSubmittingTarefa"
        @close="showTarefaModal = false"
        @submit="handleTarefaSubmit"
      />
    </div>
  </div>
</template>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/20 active:scale-95 text-sm;
}

.animate-fade-in-down { animation: fade-in-down 0.4s ease-out-back; }

@keyframes fade-in-down {
  0% { opacity: 0; transform: translateY(-20px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* Custom scrollbar for calendar cells */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
