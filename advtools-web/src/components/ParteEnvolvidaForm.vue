<script setup>
import { ref, watch } from 'vue'
import { Plus, Users } from 'lucide-vue-next'
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
  <form @submit.prevent="handleSubmit" class="space-y-6 animate-fade-in-up text-left">
    
    <!-- Seção: Dados Principais e Papel -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-5 flex items-center gap-2">
            <Users class="w-5 h-5 text-primary-600" /> Identificação da Parte
        </h3>
        
        <div class="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-6">
          <div class="sm:col-span-4">
            <label class="block text-sm font-medium leading-6 text-slate-900">Nome Completo *</label>
            <div class="mt-2">
              <input type="text" v-model="form.nome" @input="emit('update:modelValue', form)" required class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Papel / Função *</label>
            <div class="mt-2">
              <input type="text" v-model="form.papel" @input="emit('update:modelValue', form)" required placeholder="Ex: Autor, Réu, Herdeiro" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">CPF / CNPJ</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="['###.###.###-##', '##.###.###/####-##']" v-model="form.documento" @input="emit('update:modelValue', form)" placeholder="000.000.000-00" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Email</label>
            <div class="mt-2">
              <input type="email" v-model="form.email" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Telefone</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="['(##) ####-####', '(##) #####-####']" v-model="form.telefone" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">RG</label>
            <div class="mt-2">
              <input type="text" v-model="form.rg" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Data de Nascimento</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="##/##/####" v-model="form.data_nascimento" @input="emit('update:modelValue', form)" placeholder="DD/MM/AAAA" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Estado Civil</label>
            <div class="mt-2">
              <select v-model="form.estado_civil" @change="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
                <option value="">Selecione...</option>
                <option value="Solteiro(a)">Solteiro(a)</option>
                <option value="Casado(a)">Casado(a)</option>
                <option value="Divorciado(a)">Divorciado(a)</option>
                <option value="Viúvo(a)">Viúvo(a)</option>
                <option value="União Estável">União Estável</option>
              </select>
            </div>
          </div>
          
          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Nacionalidade</label>
            <div class="mt-2">
              <input type="text" v-model="form.nacionalidade" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>

          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Profissão</label>
            <div class="mt-2">
              <input type="text" v-model="form.profissao" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Seção: Endereço -->
    <div class="bg-white shadow-sm ring-1 ring-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-5">Localização</h3>
        
        <div class="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-6">
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">CEP</label>
            <div class="mt-2">
              <input type="text" v-maska data-maska="#####-###" v-model="form.cep" @input="emit('update:modelValue', form)" placeholder="00000-000" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-4">
            <label class="block text-sm font-medium leading-6 text-slate-900">Endereço Completo</label>
            <div class="mt-2">
              <input type="text" v-model="form.endereco" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium leading-6 text-slate-900">Bairro</label>
            <div class="mt-2">
              <input type="text" v-model="form.bairro" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-3">
            <label class="block text-sm font-medium leading-6 text-slate-900">Cidade</label>
            <div class="mt-2">
              <input type="text" v-model="form.cidade" @input="emit('update:modelValue', form)" class="block w-full rounded-md border-0 px-3 py-2 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 transition-shadow">
            </div>
          </div>

          <div class="sm:col-span-1">
            <label class="block text-sm font-medium leading-6 text-slate-900">UF</label>
            <div class="mt-2">
              <input type="text" v-model="form.uf" @input="emit('update:modelValue', form)" maxlength="2" placeholder="SP" class="block w-full rounded-md border-0 px-3 py-2 leading-6 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm uppercase transition-shadow">
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
           {{ isEditing ? 'Salvar Alterações' : 'Adicionar Parte' }}
        </span>
      </button>
    </div>
  </form>
</template>
