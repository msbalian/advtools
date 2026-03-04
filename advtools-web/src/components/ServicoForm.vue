<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { Plus, Trash2, RefreshCw } from 'lucide-vue-next'
import { vMaska } from 'maska/vue'
import ClientCombobox from './ClientCombobox.vue'
import { apiFetch } from '../utils/api'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  clientes: {
    type: Array,
    default: () => []
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const form = ref({ 
  tipo_servico_id: null,
  ...props.modelValue 
})

const localClientes = ref([...props.clientes])
const tiposServico = ref([])

const carregarOpcoes = async () => {
    try {
        const promises = [apiFetch('/api/configuracoes/tipos-servico')]
        
        // Se não vierem clientes via props, buscar (importante para busca inteligente funcionar)
        if (props.clientes.length === 0) {
            promises.push(apiFetch('/api/clientes'))
        }
        
        const [resTipos, resClie] = await Promise.all(promises)
        
        if (resTipos.ok) tiposServico.value = await resTipos.json()
        if (resClie && resClie.ok) localClientes.value = await resClie.json()
    } catch (e) {
        console.error("Erro ao carregar opções do serviço", e)
    }
}

onMounted(carregarOpcoes)

// Estrutura para a Tabela Dinâmica de Pagamentos
const pagamentos = ref([])

watch(() => props.modelValue, (newVal) => {
  form.value = { ...form.value, ...newVal }
  // Se já houver pagamentos em JSON, decodificar, senão, criar linha vazia inicial
  if (form.value.condicoes_pagamento) {
    try {
      pagamentos.value = JSON.parse(form.value.condicoes_pagamento)
    } catch {
       pagamentos.value = [{ tipo: 'Pix', valor: null, data: '', obs: '' }]
    }
  } else if (!props.isEditing) {
    pagamentos.value = [{ tipo: 'Pix', valor: null, data: '', obs: '' }]
  }
}, { deep: true, immediate: true })

const updateField = (field, value) => {
  form.value[field] = value
  emit('update:modelValue', form.value)
}

// Lógica de Pagamentos
const addPagamento = () => {
  pagamentos.value.push({ tipo: 'Pix', valor: null, data: '', obs: '' })
}

const removePagamento = (index) => {
  pagamentos.value.splice(index, 1)
  if (pagamentos.value.length === 0) {
     addPagamento() // Sempre deixa no mínimo 1 linha
  }
}

const valorTotalPagamentos = computed(() => {
  return pagamentos.value.reduce((acc, curr) => acc + (parseFloat(curr.valor) || 0), 0)
})

const handleSubmit = () => {
  // Sincroniza a tabela dinâmica antes de enviar
  form.value.condicoes_pagamento = JSON.stringify(pagamentos.value)
  form.value.valor_total = valorTotalPagamentos.value
  form.value.qtd_parcelas = pagamentos.value.length
  
  emit('submit', form.value)
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-8 animate-fade-in-up">
    
    <!-- Seção: Dados Principais -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-5">Serviço / Contrato</h3>
        
        <div class="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-6">
          
          <div class="sm:col-span-6">
             <label class="block text-sm font-medium leading-6 text-slate-900 mb-2">Cliente Vinculado *</label>
             <ClientCombobox 
               v-model="form.cliente_id" 
               :options="localClientes" 
               @change="updateField('cliente_id', $event.id)"
             />
          </div>

          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Tipo de Serviço *</label>
            <div class="mt-2">
              <select v-model="form.tipo_servico_id" required class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow appearance-none">
                <option :value="null">Selecione o tipo...</option>
                <option v-for="tipo in tiposServico" :key="tipo.id" :value="tipo.id">{{ tipo.nome }}</option>
              </select>
              <p v-if="tiposServico.length === 0" class="mt-1 text-[10px] text-slate-400 italic">Cadastre os tipos nas configurações.</p>
            </div>
          </div>

          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Porcentagem no Êxito (%)</label>
            <div class="mt-2">
              <input type="text" :value="form.porcentagem_exito" @input="updateField('porcentagem_exito', $event.target.value)" placeholder="Ex: 30%" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-6">
            <label class="block text-sm font-medium leading-6 text-slate-900">Descrição Comercial / Notas Internas *</label>
            <div class="mt-2">
              <textarea :value="form.descricao" @input="updateField('descricao', $event.target.value)" required rows="3" placeholder="Detalhes do contrato, escopo do trabalho..." class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow"></textarea>
            </div>
          </div>
          
          <div class="sm:col-span-3">
             <label class="block text-sm font-medium leading-6 text-slate-900">Data de Celebração</label>
             <div class="mt-2">
               <input type="text" v-maska data-maska="##/##/####" :value="form.data_contrato" @input="updateField('data_contrato', $event.target.value)" placeholder="DD/MM/AAAA" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
             </div>
          </div>

          <div class="sm:col-span-3">
             <label class="block text-sm font-medium leading-6 text-slate-900">Forma Principal (Resumo)</label>
             <div class="mt-2">
               <strong class="text-sm font-medium block h-full flex items-center">{{ pagamentos.length }} Parcela(s)</strong>
             </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Seção: Financeiro Dinâmico -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3 mb-5">
           <h3 class="text-base font-semibold leading-6 text-slate-900">Condições de Pagamento</h3>
           <div class="text-sm font-bold text-success-600 bg-success-50 px-3 py-1 rounded-md">
              Total: R$ {{ valorTotalPagamentos.toFixed(2) }}
           </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
             <thead class="bg-slate-50">
               <tr>
                 <th scope="col" class="py-2 pl-4 pr-3 text-left text-xs font-semibold text-slate-500 w-1/5">Tipo</th>
                 <th scope="col" class="px-3 py-2 text-left text-xs font-semibold text-slate-500 w-1/5">Valor (R$)</th>
                 <th scope="col" class="px-3 py-2 text-left text-xs font-semibold text-slate-500 w-1/5">Data Venc.</th>
                 <th scope="col" class="px-3 py-2 text-left text-xs font-semibold text-slate-500">Observação</th>
                 <th scope="col" class="relative py-2 pl-3 pr-4 w-10"><span class="sr-only">Ações</span></th>
               </tr>
             </thead>
             <tbody class="divide-y divide-slate-200 bg-white">
               <tr v-for="(pag, index) in pagamentos" :key="index">
                 <td class="whitespace-nowrap py-2 pl-4 pr-3 text-sm">
                   <select v-model="pag.tipo" class="block w-full rounded-md border-0 px-2 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-xs">
                     <option value="Pix">Pix</option>
                     <option value="Boleto">Boleto</option>
                     <option value="Cartão">Cartão</option>
                     <option value="Dinheiro">Dinheiro</option>
                     <option value="Outros">Outros</option>
                   </select>
                 </td>
                 <td class="whitespace-nowrap px-3 py-2 text-sm">
                   <!-- type="number" natively blocks letters, giving a simple mask to currency -->
                   <input type="number" step="0.01" v-model="pag.valor" required placeholder="0.00" class="block w-full rounded-md border-0 px-2 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-xs">
                 </td>
                 <td class="whitespace-nowrap px-3 py-2 text-sm">
                   <input type="text" v-maska data-maska="##/##/####" v-model="pag.data" placeholder="DD/MM/AAAA" class="block w-full rounded-md border-0 px-2 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-xs">
                 </td>
                 <td class="whitespace-nowrap px-3 py-2 text-sm">
                   <input type="text" v-model="pag.obs" placeholder="Ex: Parcela 1/3" class="block w-full rounded-md border-0 px-2 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-xs">
                 </td>
                 <td class="relative whitespace-nowrap py-2 pl-3 pr-4 text-right text-sm font-medium">
                   <button type="button" @click="removePagamento(index)" class="text-slate-400 hover:text-red-600 transition-colors" title="Remover Parcela">
                     <Trash2 class="w-4 h-4" />
                   </button>
                 </td>
               </tr>
             </tbody>
          </table>
        </div>
        
        <div class="mt-4">
           <button type="button" @click="addPagamento" class="btn-secondary text-xs flex items-center gap-1">
              <Plus class="w-3 h-3" /> Adicionar Parcela
           </button>
        </div>
      </div>
    </div>

    <!-- Ações -->
    <div class="flex items-center justify-end gap-x-4">
      <button type="button" @click="$emit('cancel')" class="text-sm font-semibold leading-6 text-slate-900 hover:text-slate-600 transition-colors">Cancelar</button>
      <button type="submit" :disabled="isSubmitting || !form.cliente_id" class="btn-primary flex items-center gap-2 shadow-primary-500/30 disabled:opacity-50">
        <span v-if="isSubmitting">Salvando...</span>
        <span v-else class="flex items-center gap-2">
           <Plus class="w-4 h-4" v-if="!isEditing" />
           {{ isEditing ? 'Salvar Alterações' : 'Salvar Serviço' }}
        </span>
      </button>
    </div>
  </form>
</template>
