<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  MoreVertical, 
  ExternalLink,
  Gavel,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'

const router = useRouter()
const movimentacoes = ref([])
const loading = ref(true)

const carregarMovimentacoes = async () => {
    try {
        loading.value = true
        const res = await apiFetch('/api/dashboard/ultimas-movimentacoes?limit=5')
        if (res.ok) {
            const data = await res.json()
            movimentacoes.value = data.items || []
        }
    } catch (e) {
        console.error("Erro ao carregar movimentações", e)
    } finally {
        loading.value = false
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
    
    return data.toLocaleDateString('pt-BR')
}

onMounted(() => {
    carregarMovimentacoes()
})
</script>

<template>
  <div class="card p-0 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
    <div class="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-white/50 backdrop-blur-sm">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-primary-50 text-primary-600 rounded-lg">
           <Clock class="w-5 h-5" />
        </div>
        <div>
           <h2 class="text-base font-black text-slate-900 leading-tight">Últimas Movimentações</h2>
           <p class="text-xs text-slate-500 font-medium">Sincronizado via DataJud / PROJUDI</p>
        </div>
      </div>
      <button @click="router.push('/movimentacoes')" class="text-sm font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1 group">
        Ver todos <ExternalLink class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-100">
        <thead class="bg-slate-50/50">
          <tr>
            <th scope="col" class="py-3 px-6 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Processo</th>
            <th scope="col" class="px-6 py-3 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Cliente / Tribunal</th>
            <th scope="col" class="px-6 py-3 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Status / Movimentação</th>
            <th scope="col" class="px-6 py-3 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Data</th>
            <th scope="col" class="relative py-3 px-6"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          <template v-if="loading">
            <tr v-for="i in 5" :key="i" class="animate-pulse">
              <td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-32"></div></td>
              <td class="px-6 py-4"><div class="h-8 bg-slate-50 rounded w-40"></div></td>
              <td class="px-6 py-4"><div class="h-6 bg-slate-100 rounded w-28"></div></td>
              <td class="px-6 py-4"><div class="h-4 bg-slate-50 rounded w-20"></div></td>
              <td class="px-6 py-4"></td>
            </tr>
          </template>
          <template v-else-if="movimentacoes.length > 0">
            <tr v-for="mov in movimentacoes" :key="mov.id" class="hover:bg-slate-50/80 transition-colors group">
              <td class="py-4 px-6">
                <router-link :to="`/processos/${mov.processo.id}`" class="text-xs font-black text-slate-900 hover:text-primary-600 transition-colors">
                  {{ mov.processo.numero_processo || 'N/A' }}
                </router-link>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="text-sm font-bold text-slate-700">{{ mov.processo.cliente?.nome || '—' }}</span>
                  <span class="text-[10px] font-black text-primary-500 uppercase tracking-tighter">TJGO | PROJUDI</span>
                </div>
              </td>
              <td class="px-6 py-4 text-sm">
                <div class="flex items-center gap-2">
                  <span :class="[getStatusBadge(mov.nome_movimento), 'inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-black uppercase tracking-wider ring-1 ring-inset']">
                    {{ mov.nome_movimento }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-xs font-bold text-slate-500">
                {{ formatarData(mov.data_hora) }}
              </td>
              <td class="py-4 px-6 text-right">
                <button @click="router.push(`/processos/${mov.processo.id}`)" class="text-slate-300 group-hover:text-primary-500 transition-colors">
                  <MoreVertical class="w-5 h-5" />
                </button>
              </td>
            </tr>
          </template>
          <tr v-else>
            <td colspan="5" class="py-12 text-center text-slate-400 font-medium italic">
              Nenhuma movimentação identificada.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
