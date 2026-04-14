<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  MoreVertical, 
  Clock,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Search,
  Filter
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'

const router = useRouter()
const sidebarOpen = ref(false)

const movimentacoes = ref([])
const loading = ref(true)

// Paginação
const currentPage = ref(1)
const itemsPerPage = 20
const totalItems = ref(0)
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage))

const carregarMovimentacoes = async () => {
    try {
        loading.value = true
        const skip = (currentPage.value - 1) * itemsPerPage
        const res = await apiFetch(`/api/dashboard/ultimas-movimentacoes?skip=${skip}&limit=${itemsPerPage}`)
        
        if (res.ok) {
            const data = await res.json()
            movimentacoes.value = data.items
            totalItems.value = data.total
        }
    } catch (e) {
        console.error("Erro ao carregar movimentações", e)
    } finally {
        loading.value = false
    }
}

const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++
        carregarMovimentacoes()
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--
        carregarMovimentacoes()
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

const firstPage = () => {
    if (currentPage.value > 1) {
        currentPage.value = 1
        carregarMovimentacoes()
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

const lastPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value = totalPages.value
        carregarMovimentacoes()
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

const getStatusBadge = (texto) => {
    const t = texto.toLowerCase()
    if (t.includes('prazo') || t.includes('espera')) return 'bg-amber-50 text-amber-700 ring-amber-600/20'
    if (t.includes('juntada') || t.includes('protocolo')) return 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
    if (t.includes('concluso') || t.includes('decisão') || t.includes('despacho')) return 'bg-primary-50 text-primary-700 ring-primary-600/20'
    if (t.includes('audiência')) return 'bg-purple-50 text-purple-700 ring-purple-600/20'
    if (t.includes('sentença')) return 'bg-rose-50 text-rose-700 ring-rose-600/20'
    return 'bg-slate-50 text-slate-600 ring-slate-500/10'
}

const formatarData = (dateStr) => {
    if (!dateStr) return '-'
    const data = new Date(dateStr)
    const hoje = new Date()
    const ontem = new Date()
    ontem.setDate(hoje.getDate() - 1)

    const isMesmoDia = (d1, d2) => 
        d1.getDate() === d2.getDate() && 
        d1.getMonth() === d2.getMonth() && 
        d1.getFullYear() === d2.getFullYear()

    const hora = data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    
    if (isMesmoDia(data, hoje)) return `Hoje, ${hora}`
    if (isMesmoDia(data, ontem)) return `Ontem, ${hora}`
    
    // Se for deste ano, simplifica a data para Dia/Mês
    if (data.getFullYear() === hoje.getFullYear()) {
        return `${data.getDate().toString().padStart(2, '0')}/${(data.getMonth() + 1).toString().padStart(2, '0')}, ${hora}`
    }
    
    return `${data.toLocaleDateString('pt-BR')}, ${hora}`
}

onMounted(() => {
    carregarMovimentacoes()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    
    <!-- Sidebar -->
    <Sidebar v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden relative">

        <!-- Header -->
        <div class="bg-white border-b border-slate-200 px-6 py-6 sticky top-0 z-20 shadow-sm">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 class="text-2xl font-black text-slate-900 flex items-center gap-2">
                        <Clock class="w-7 h-7 text-primary-600" /> Central de Atualizações
                    </h1>
                    <p class="mt-1 text-sm text-slate-500 font-medium">Histórico completo de todas as movimentações dos processos.</p>
                </div>
            </div>
        </div>

        <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            <div class="card p-0 shadow-sm animate-fade-in-up">
                
                <!-- Table -->
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-100">
                        <thead class="bg-slate-50">
                        <tr>
                            <th scope="col" class="py-3.5 px-6 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest">Data / Hora</th>
                            <th scope="col" class="px-6 py-3.5 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest">Processo</th>
                            <th scope="col" class="px-6 py-3.5 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest">Cliente</th>
                            <th scope="col" class="px-6 py-3.5 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest">Movimentação</th>
                            <th scope="col" class="relative py-3.5 px-6"></th>
                        </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 bg-white">
                        <template v-if="loading">
                            <tr v-for="i in 10" :key="i" class="animate-pulse">
                                <td class="px-6 py-4 w-32"><div class="h-4 bg-slate-100 rounded w-24"></div></td>
                                <td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-32"></div></td>
                                <td class="px-6 py-4"><div class="h-4 bg-slate-50 rounded w-40"></div></td>
                                <td class="px-6 py-4 w-1/3"><div class="h-6 bg-slate-100 rounded-full w-full"></div></td>
                                <td class="px-6 py-4"></td>
                            </tr>
                        </template>
                        <template v-else-if="movimentacoes.length > 0">
                            <tr v-for="mov in movimentacoes" :key="mov.id" class="hover:bg-slate-50/80 transition-colors group">
                                <td class="px-6 py-5 text-sm font-bold text-slate-500 whitespace-nowrap">
                                    {{ formatarData(mov.data_hora) }}
                                </td>
                                <td class="px-6 py-5">
                                    <router-link :to="`/processos/${mov.processo.id}`" class="text-sm font-black text-slate-900 hover:text-primary-600 transition-colors">
                                        {{ mov.processo.numero_processo || 'N/A' }}
                                    </router-link>
                                    <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase">
                                        {{ mov.processo.titulo || 'Sem Título' }}
                                    </div>
                                </td>
                                <td class="px-6 py-5 text-sm font-semibold text-slate-700">
                                    {{ mov.processo.cliente?.nome || '—' }}
                                </td>
                                <td class="px-6 py-5 min-w-[250px]">
                                    <span :class="[getStatusBadge(mov.nome_movimento), 'inline-flex items-center rounded-full px-3 py-1 text-xs font-black uppercase tracking-wider ring-1 ring-inset']">
                                        {{ mov.nome_movimento }}
                                    </span>
                                </td>
                                <td class="px-6 py-5 text-right whitespace-nowrap">
                                    <button @click="router.push(`/processos/${mov.processo.id}`)" class="text-slate-300 hover:text-primary-600 hover:bg-primary-50 p-2 rounded-full transition-colors" title="Abrir Processo">
                                        <ExternalLink class="w-5 h-5" />
                                    </button>
                                </td>
                            </tr>
                        </template>
                        <tr v-else>
                            <td colspan="5" class="py-16 text-center text-slate-400 font-medium text-lg">
                                Nenhuma movimentação recente localizada.
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Paginação Padrão -->
                <div class="px-6 py-4 flex items-center justify-between border-t border-slate-100 bg-white rounded-b-2xl">
                    <div class="text-sm text-slate-500 hidden sm:block font-medium">
                        Mostrando <span class="font-bold text-slate-700">{{ ((currentPage - 1) * itemsPerPage) + 1 }}</span> 
                        até <span class="font-bold text-slate-700">{{ Math.min(currentPage * itemsPerPage, totalItems) }}</span> 
                        de <span class="font-bold text-slate-700">{{ totalItems }}</span> movimentações
                    </div>
                    
                    <div class="flex flex-1 sm:justify-end justify-between items-center gap-2">
                        <button 
                            @click="firstPage" 
                            :disabled="currentPage === 1"
                            class="relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-bold text-slate-900 ring-1 ring-inset ring-slate-200 hover:bg-slate-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Primeira
                        </button>

                        <button 
                            @click="prevPage" 
                            :disabled="currentPage === 1"
                            class="relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-bold text-slate-900 ring-1 ring-inset ring-slate-200 hover:bg-slate-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronLeft class="h-4 w-4 mr-1" />
                            Anterior
                        </button>
                        
                        <div class="text-sm font-bold text-slate-700 bg-slate-50 px-3 py-2 rounded-lg ring-1 ring-inset ring-slate-200">
                             {{ currentPage }} / {{ totalPages }}
                        </div>
                        
                        <button 
                            @click="nextPage" 
                            :disabled="currentPage === totalPages || totalPages === 0"
                            class="relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-bold text-slate-900 ring-1 ring-inset ring-slate-200 hover:bg-slate-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Próxima
                            <ChevronRight class="h-4 w-4 ml-1" />
                        </button>

                        <button 
                            @click="lastPage" 
                            :disabled="currentPage === totalPages || totalPages === 0"
                            class="relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-bold text-slate-900 ring-1 ring-inset ring-slate-200 hover:bg-slate-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Última
                        </button>
                    </div>
                </div>

            </div>
        </main>
    </div>
  </div>
</template>
