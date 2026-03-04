<script setup>
import { ref, onMounted, watch } from 'vue'
import { apiFetch } from '../utils/api'
import ClientCombobox from './ClientCombobox.vue'
import { 
  X, 
  Save, 
  Gavel, 
  Scale, 
  FileText, 
  User, 
  AlertCircle,
  Calendar,
  ShieldAlert,
  TrendingUp,
  MapPin,
  RefreshCw,
  FolderOpen
} from 'lucide-vue-next'

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    },
    isEditing: {
        type: Boolean,
        default: false
    },
    isSubmitting: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const form = ref({
    titulo: '',
    numero_processo: '',
    tribunal: '',
    grau: 'G1',
    polo: 'Autor',
    cliente_id: null,
    servico_id: null,
    status: 'Ativo',
    prioridade: 'Normal',
    descricao: '',
    valor_causa: null,
    pasta_trabalho_id: null,
    fase_processual: '',
    ...props.modelValue
})

const clientes = ref([])
const pastasTrabalho = ref([])
const servicos = ref([])

watch(() => form.value.cliente_id, async (newVal) => {
    if (newVal) {
        try {
            const res = await apiFetch(`/api/clientes/${newVal}/servicos`)
            if (res.ok) {
                servicos.value = await res.json()
            } else {
                servicos.value = []
            }
        } catch (e) {
            console.error("Erro ao carregar serviços", e)
            servicos.value = []
        }
    } else {
        servicos.value = []
        form.value.servico_id = null
    }
}, { immediate: true })

const carregarOpcoes = async () => {
    try {
        const [resClie, resPastas] = await Promise.all([
            apiFetch('/api/clientes'),
            apiFetch('/api/configuracoes/pastas-trabalho')
        ])
        if (resClie.ok) clientes.value = await resClie.json()
        if (resPastas.ok) pastasTrabalho.value = await resPastas.json()
    } catch (e) {
        console.error("Erro ao carregar opções", e)
    }
}

onMounted(carregarOpcoes)

watch(() => props.modelValue, (newVal) => {
    form.value = { ...form.value, ...newVal }
}, { deep: true })

const handleSubmit = () => {
    emit('submit', form.value)
}

const errors = ref({})

const validate = () => {
    errors.value = {}
    if (!form.value.titulo) errors.value.titulo = 'Título é obrigatório'
    return Object.keys(errors.value).length === 0
}

const onFormSubmit = () => {
    if (validate()) {
        handleSubmit()
    }
}
</script>

<template>
  <form @submit.prevent="onFormSubmit" class="space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      
      <!-- Seção: Identificação Principal -->
      <div class="space-y-6 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <h4 class="text-sm font-black text-slate-900 flex items-center gap-2 mb-4">
          <Gavel class="w-4 h-4 text-primary-600" /> Identificação do Processo
        </h4>
        
        <div class="space-y-4">
          <div>
            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Título Interno *</label>
            <input v-model="form.titulo" 
                   type="text" 
                   placeholder="Ex: Ação Indenizatória - João vs Seguradora"
                   :class="[errors.titulo ? 'border-red-300 ring-red-50' : 'border-slate-100 focus:border-primary-500']"
                   class="w-full px-4 py-3 bg-slate-50 border-2 rounded-2xl font-bold text-slate-900 transition-all outline-none" />
            <p v-if="errors.titulo" class="mt-1 text-xs text-red-500 font-bold ml-1">{{ errors.titulo }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Número (CNJ)</label>
               <input v-model="form.numero_processo" 
                      type="text" 
                      placeholder="0000000-00.0000.0.00.0000"
                      class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none" />
            </div>
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Tribunal</label>
               <input v-model="form.tribunal" 
                      type="text" 
                      placeholder="Ex: TJSP, TRF3"
                      class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Grau</label>
               <select v-model="form.grau" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none">
                 <option value="G1">1º Grau</option>
                 <option value="G2">2º Grau</option>
                 <option value="TST">TST / Superior</option>
                 <option value="STF">STF</option>
               </select>
            </div>
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Polo Assistido</label>
               <select v-model="form.polo" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none">
                 <option value="Autor">Autor / Ativo</option>
                 <option value="Réu">Réu / Passivo</option>
                 <option value="Terceiro">Terceiro</option>
               </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Seção: Cliente e Classificação -->
      <div class="space-y-6 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <h4 class="text-sm font-black text-slate-900 flex items-center gap-2 mb-4">
          <User class="w-4 h-4 text-indigo-600" /> Vínculo e Classificação
        </h4>

        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div>
                <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Cliente Vinculado</label>
                <ClientCombobox v-model="form.cliente_id" :options="clientes" />
             </div>
             <div>
                <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Serviço Vinculado (Opcional)</label>
                <select v-model="form.servico_id" :disabled="!form.cliente_id" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none disabled:opacity-50">
                  <option :value="null">Nenhum serviço associado</option>
                  <option v-for="servico in servicos" :key="servico.id" :value="servico.id">{{ servico.descricao }}</option>
                </select>
             </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Status</label>
               <select v-model="form.status" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none">
                 <option value="Ativo">Ativo</option>
                 <option value="Suspenso">Suspenso</option>
                 <option value="Arquivado">Arquivado</option>
                 <option value="Encerrado">Encerrado</option>
               </select>
            </div>
            <div>
               <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Prioridade</label>
               <select v-model="form.prioridade" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none">
                 <option value="Normal">Normal</option>
                 <option value="Alta">Alta</option>
                 <option value="Urgente">Urgente</option>
               </select>
            </div>
          </div>

          <div>
            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Pasta de Trabalho (Área)</label>
            <select v-model="form.pasta_trabalho_id" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none appearance-none">
              <option :value="null">Selecione uma pasta...</option>
              <option v-for="pasta in pastasTrabalho" :key="pasta.id" :value="pasta.id">{{ pasta.nome }}</option>
            </select>
            <p v-if="pastasTrabalho.length === 0" class="mt-1 text-[9px] text-slate-400 italic">Nenhuma pasta cadastrada nas configurações.</p>
          </div>
        </div>
      </div>

      <!-- Seção: Detalhes Adicionais (Full Width) -->
      <div class="md:col-span-2 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <h4 class="text-sm font-black text-slate-900 flex items-center gap-2 mb-4">
          <FileText class="w-4 h-4 text-emerald-600" /> Observações e Complementos
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
           <div>
              <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Descrição / Notas do Caso</label>
              <textarea v-model="form.descricao" 
                        rows="4"
                        placeholder="Descreva detalhes importantes, estratégias ou histórico resumido do caso..."
                        class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none resize-none"></textarea>
           </div>
           <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                   <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Valor da Causa (R$)</label>
                   <input v-model="form.valor_causa" 
                          type="number" step="0.01"
                          placeholder="0,00"
                          class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none" />
                </div>
                <div>
                   <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-1.5 block">Fase Processual</label>
                   <input v-model="form.fase_processual" 
                          type="text" 
                          placeholder="Ex: Inicial, Instrutória, Sentença"
                          class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-2xl font-bold text-slate-900 focus:border-primary-500 transition-all outline-none" />
                </div>
              </div>
              <div class="p-4 bg-primary-50/50 rounded-2xl border border-primary-100 flex gap-3">
                 <AlertCircle class="w-5 h-5 text-primary-500 flex-shrink-0" />
                 <p class="text-[11px] text-primary-700 font-medium leading-relaxed">
                   Os campos de <span class="font-bold">Tribunal</span> e <span class="font-bold">Número CNJ</span> são fundamentais caso você decida habilitar o monitoramento automático via DataJud futuramente.
                 </p>
              </div>
           </div>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-end gap-4 pt-4">
      <button type="button" 
              @click="emit('cancel')"
              class="px-8 py-3 bg-white text-slate-500 font-black rounded-2xl border-2 border-slate-100 hover:bg-slate-50 transition-all active:scale-95">
        Cancelar
      </button>
      <button type="submit" 
              :disabled="isSubmitting"
              class="px-8 py-3 bg-gradient-to-r from-primary-600 to-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-primary-500/20 hover:shadow-primary-500/40 hover:-translate-y-0.5 transition-all flex items-center gap-2 disabled:opacity-50 disabled:translate-y-0">
        <Save v-if="!isSubmitting" class="w-5 h-5" />
        <RefreshCw v-else class="w-5 h-5 animate-spin" />
        {{ isEditing ? 'Salvar Alterações' : 'Cadastrar Processo' }}
      </button>
    </div>
  </form>
</template>

<style scoped>
/* Custom transitions or tweaks if needed */
</style>
