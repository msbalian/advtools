<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Check, ChevronDown, Search } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: ''
  },
  options: {
    type: Array,
    required: true,
    default: () => [] // [{id: 1, nome: 'João', documento: '...'}, ...]
  },
  placeholder: {
    type: String,
    default: 'Selecione um cliente...'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const comboboxRef = ref(null)

const selectedOption = computed(() => {
  return props.options.find(opt => opt.id === props.modelValue) || null
})

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(opt => {
    return (
      (opt.nome && opt.nome.toLowerCase().includes(query)) ||
      (opt.documento && opt.documento.includes(query))
    )
  })
})

const toggleOpen = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
    setTimeout(() => {
      const searchInput = comboboxRef.value?.querySelector('input[type="text"]')
      if (searchInput) searchInput.focus()
    }, 50)
  }
}

const selectOption = (opt) => {
  emit('update:modelValue', opt.id)
  emit('change', opt)
  isOpen.value = false
}

// Fechar ao clicar fora
const handleClickOutside = (event) => {
  if (comboboxRef.value && !comboboxRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div class="relative" ref="comboboxRef">
    <!-- Trigger Button -->
    <button
      type="button"
      @click="toggleOpen"
      class="relative w-full cursor-pointer rounded-md bg-white py-2 pl-3 pr-10 text-left text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm sm:leading-6 transition-all"
      :class="{'ring-2 ring-primary-600': isOpen}"
    >
      <span class="block truncate">
        <template v-if="selectedOption">
          <span class="font-medium">{{ selectedOption.nome }}</span>
          <span class="text-slate-500 ml-2 text-xs" v-if="selectedOption.documento">({{ selectedOption.documento }})</span>
        </template>
        <template v-else>
          <span class="text-slate-400">{{ placeholder }}</span>
        </template>
      </span>
      <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
        <ChevronDown class="h-4 w-4 text-slate-400" aria-hidden="true" />
      </span>
    </button>

    <!-- Dropdown Panel -->
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isOpen" class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
        
        <!-- Search Input -->
        <div class="sticky top-0 z-20 bg-white px-3 pb-2 pt-2 border-b border-slate-100">
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2">
              <Search class="h-4 w-4 text-slate-400" />
            </div>
            <input
              type="text"
              v-model="searchQuery"
              class="block w-full rounded-md border-0 py-1.5 pl-8 pr-3 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 bg-slate-50"
              placeholder="Buscar por nome ou documento..."
              @click.stop
            />
          </div>
        </div>

        <!-- Options List -->
        <ul class="pt-1">
          <li v-if="filteredOptions.length === 0" class="relative cursor-default select-none py-4 px-4 text-slate-500 text-center">
            Nenhum cliente encontrado.
          </li>
          
          <li
            v-for="opt in filteredOptions"
            :key="opt.id"
            @click="selectOption(opt)"
            class="relative cursor-pointer select-none py-2 pl-3 pr-9 hover:bg-slate-50 transition-colors"
            :class="[opt.id === modelValue ? 'bg-primary-50 text-primary-900' : 'text-slate-900']"
          >
            <div class="flex items-center">
              <span class="block truncate" :class="[opt.id === modelValue ? 'font-semibold' : 'font-normal']">
                {{ opt.nome }}
              </span>
              <span class="ml-2 truncate text-slate-500 text-xs" v-if="opt.documento">
                {{ opt.documento }}
              </span>
            </div>

            <span v-if="opt.id === modelValue" class="absolute inset-y-0 right-0 flex items-center pr-4 text-primary-600">
              <Check class="h-4 w-4" aria-hidden="true" />
            </span>
          </li>
        </ul>

      </div>
    </transition>
  </div>
</template>
