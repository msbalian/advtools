<script setup>
import { ref, watch, reactive } from 'vue'
import { Plus } from 'lucide-vue-next'
import { vMaska } from 'maska/vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
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

const form = ref({ ...props.modelValue })

watch(() => props.modelValue, (newVal) => {
  form.value = { ...newVal }
}, { deep: true })

const updateField = (field, value) => {
  form.value[field] = value
  emit('update:modelValue', form.value)
}

const handleSubmit = () => {
  emit('submit', form.value)
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-8 animate-fade-in-up">
    
    <!-- Seção: Dados Pessoais -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-5">Dados Cadastrais</h3>
        
        <div class="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-6">
          <div class="sm:col-span-4">
            <label class="block text-sm font-medium leading-6 text-slate-900">Nome Completo / Razão Social *</label>
            <div class="mt-2">
              <input type="text" :value="form.nome" @input="updateField('nome', $event.target.value)" required class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">CPF / CNPJ</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="['###.###.###-##', '##.###.###/####-##']" :value="form.documento" @input="updateField('documento', $event.target.value)" placeholder="000.000.000-00" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Email</label>
            <div class="mt-2">
              <input type="email" :value="form.email" @input="updateField('email', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Telefone / WhatsApp</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="['(##) ####-####', '(##) #####-####']" :value="form.telefone" @input="updateField('telefone', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>
          
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">RG</label>
            <div class="mt-2">
              <input type="text" :value="form.rg" @input="updateField('rg', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Data Nasc. / Fundação</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="##/##/####" :value="form.data_nascimento" @input="updateField('data_nascimento', $event.target.value)" placeholder="DD/MM/AAAA" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Estado Civil</label>
            <div class="mt-2">
              <select :value="form.estado_civil" @change="updateField('estado_civil', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
                <option value="">Selecione...</option>
                <option value="Solteiro(a)">Solteiro(a)</option>
                <option value="Casado(a)">Casado(a)</option>
                <option value="Divorciado(a)">Divorciado(a)</option>
                <option value="Viúvo(a)">Viúvo(a)</option>
                <option value="União Estável">União Estável</option>
              </select>
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Nacionalidade</label>
            <div class="mt-2">
              <input type="text" :value="form.nacionalidade" @input="updateField('nacionalidade', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-6">
            <label class="block text-sm font-medium leading-6 text-slate-900">Profissão</label>
            <div class="mt-2">
              <input type="text" :value="form.profissao" @input="updateField('profissao', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Seção: Endereço -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-5">Endereço</h3>
        
        <div class="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-6">
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">CEP</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="#####-###" :value="form.cep" @input="updateField('cep', $event.target.value)" placeholder="00000-000" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-4">
            <label class="block text-sm font-medium leading-6 text-slate-900">Endereço (Rua, Nº, Compl.)</label>
            <div class="mt-2">
              <input type="text" :value="form.endereco" @input="updateField('endereco', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Bairro</label>
            <div class="mt-2">
              <input type="text" :value="form.bairro" @input="updateField('bairro', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Cidade</label>
            <div class="mt-2">
              <input type="text" :value="form.cidade" @input="updateField('cidade', $event.target.value)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-1">
            <label class="block text-sm font-medium leading-6 text-slate-900">UF</label>
            <div class="mt-2">
              <input type="text" :value="form.uf" @input="updateField('uf', $event.target.value)" maxlength="2" placeholder="SP" class="block w-full rounded-md border-0 px-3 py-2 leading-6 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm uppercase transition-shadow">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ações -->
    <div class="flex items-center justify-end gap-x-4">
      <button type="button" @click="$emit('cancel')" class="text-sm font-semibold leading-6 text-slate-900 hover:text-slate-600 transition-colors">Cancelar</button>
      <button type="submit" :disabled="isSubmitting" class="btn-primary flex items-center gap-2 shadow-primary-500/30 disabled:opacity-50">
        <span v-if="isSubmitting">Salvando...</span>
        <span v-else class="flex items-center gap-2">
           <Plus class="w-4 h-4" v-if="!isEditing" />
           {{ isEditing ? 'Salvar Alterações' : 'Cadastrar Cliente' }}
        </span>
      </button>
    </div>
  </form>
</template>
